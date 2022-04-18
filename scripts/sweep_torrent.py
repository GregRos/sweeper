import logging
from os import link
from pathlib import Path
from shutil import copytree, move
from typing import Literal, TypeAlias, Any

from common import Torrent
from extract import Extractor
from filebot import FilebotExecutor, FilebotAction, FilebotSubtype
from matchers import TitleMatcher, ContentMatcher
from scripts.fail import not_enough_info, detector_mismatch, \
    file_exists, raise_bad_input
from scripts.run_info import to_content_table, to_title_table
from util import get_dir_for_torrent

logger = logging.getLogger("sweeper")
Conflict: TypeAlias = Literal["overwrite", "index", "fail"]

SweepAction: TypeAlias = Literal["copy", "hard", "move"]
soft_threshold = 0.8
hard_threshold = 0.9
certain_threshold = 0.93


def get_filebot_action(action: SweepAction) -> FilebotAction:
    if action == "copy":
        return "duplicate"
    if action == "hard":
        return "hardlink"
    if action == "copy":
        return "duplicate"
    raise Exception("Not here")

filebot_format = '{ ~plex.derive{" {tmdb-$id}"}{" {$vf, $vc, $ac}"} }'


class Sweeper:
    torrent: Torrent
    action: SweepAction
    library: Any
    title_matcher: TitleMatcher
    content_matcher: ContentMatcher
    filebot: FilebotExecutor
    extractor: Extractor
    force_target: Path
    force_type: str | None
    force_filebot_type: FilebotSubtype
    conflict: Conflict

    def __init__(
            self,
            torrent: Torrent,
            action: SweepAction,
            library: Any,
            title_matcher: TitleMatcher,
            content_matcher: ContentMatcher,
            filebot: FilebotExecutor,
            extractor: Extractor,
            force_target: Path = None,
            force_type: str = None,
            force_filebot_type: FilebotSubtype = None,
            conflict: Conflict = "fail"
    ):

        self.force_type = force_type
        self.force_target = force_target
        self.force_filebot_type = force_filebot_type
        self.extractor = extractor
        self.filebot = filebot
        self.content_matcher = content_matcher
        self.title_matcher = title_matcher
        self.library = library
        self.action = action
        self.torrent = torrent
        self.conflict = conflict

    def _assume_type(self, type: str, based_on: str):
        self.force_type = type
        log_code = "Assumption"
        logger.info(
            f"ASSUMING torrent is of type '{type}' ({based_on})",
            extra={
                "type": log_code
            }
        )

    def _sweep_filebot(self):
        logger.info(f"CHOSE_METHOD :: filebot ({self.action})")
        self.filebot.rename(
            root=self.torrent.root,
            format=self._get_filebot_format(),
            conflict=self.conflict,
            action=get_filebot_action(self.action),
            force_type=self.force_filebot_type,
            formats={
                "movie": self.library.movies.absolute().joinpath(filebot_format),
                "series": self.library.shows.absolute().joinpath(filebot_format),
                "anime": self.library.shows.absolute().joinpath(filebot_format)
            }
        )

    def _get_filebot_format(self):
        if self.force_target:
            media_root = self.force_target.absolute()
        else:
            media_root = f'[episode ? "{self.library.shows.absolute()}" : "{self.library.movies.absolute()}"]'

        media_root = media_root
        media_name = '[ ~plex.derive[" [tmdb-$id}"][" [$vf, $vc, $ac]"] ]'
        full_path = f"{media_root}/{media_name}".replace("[", "{").replace("]", "}")
        return full_path

    def _get_target(self, start: Path):
        next_target = start.joinpath(self.torrent.name)
        if self.conflict == "fail":
            return file_exists(next_target, None)
        elif self.conflict == "index":
            final_target, index = get_dir_for_torrent(self.force_target, self.torrent.name)
            file_exists(next_target, f"Adding free suffix '.{index}'.")
            return final_target
        else:
            file_exists(next_target, "Will overwrite.")
            return next_target

    def _sweep_files(self):
        logger.info(f"CHOSE_METHOD :: manual ({self.action})")
        sweep_type: SweepAction
        if self.torrent.is_temp:
            logger.info(f"FORCING move (torrent is temp, after extract)")
            self.action = "move"
        final_target = self.force_target.joinpath(self.torrent.name)
        if final_target.exists():
            if self.conflict == "fail":
                file_exists(final_target, None)
            elif self.conflict == "index":
                next_target, index = get_dir_for_torrent(self.force_target, self.torrent.name)
                file_exists(final_target, f"Adding free suffix {index}.")
                final_target = next_target
            else:
                file_exists(final_target, "Will overwrite.")

        if self.action == "move":
            move(self.torrent.root, final_target)
        elif self.action == "copy":
            copytree(self.torrent.root, final_target)
        elif self.action == "hard":
            copytree(self.torrent.root, final_target, copy_function=link)
        else:
            raise Exception(f"Unknown action {self.action}")

        logger.info("SWEEPING succeeded.")

    def _get_target_by_group(self):
        if self.force_type == "program":
            return self.library.programs
        elif self.force_type == "game":
            return self.library.games
        elif self.force_type == "audio":
            return self.library.audio
        elif self.force_type == "text":
            return self.library.ebooks
        elif self.force_type == "video":
            return None
        elif self.force_type == "image":
            raise NotImplementedError()

    def run_sweep(self):
        content_info = self.content_matcher.match(self.torrent)
        logger.info(f"SWEEPING {self.torrent.name}")
        content = content_info[0]
        if content.one_of("archive"):
            logger.info(f"Archive extensions found: {', '.join(content.exts)}")
            self.torrent = self.extractor.extract(self.torrent)
            content_info = self.content_matcher.match(self.torrent)
        title_info = self.title_matcher.match(self.torrent)
        logger.info(to_content_table(content_info))
        logger.info(to_title_table(title_info))
        content = content_info[0]
        title = title_info[0]

        if self.force_type:
            logger.info(f"FORCED type '{self.force_type}'")
        else:
            if not content.is_greater(soft_threshold):
                # This is an error because it shouldn't happen, as it means this is a weird mixed torrent
                # If the torrent has unknown extensions, it would be marked as Unknown.
                raise_bad_input(f"Too low content ratio {content.ratio}.")
            elif content.type == "unsortable":
                raise_bad_input(f"Torrent content detected as 'unsortable'.")
            elif content.type == "image":
                raise_bad_input(f"Torrent content detected as 'image', which isn't supported.")
            elif content.type == "Unknown":
                not_enough_info(f"Content matched as Unknown.", error=False)
                if not title.is_greater(certain_threshold):
                    not_enough_info(f"Content is unknown, Title is below threshold.", error=True)
                self._assume_type(title.type, "Title")
            elif content.type == "program":
                self._assume_type("program", "Content")
                if not title.is_greater(soft_threshold):
                    not_enough_info(
                        f"Title Detector is at {title.chance}, which is low. Assuming default.",
                        error=False
                    )
                    self._assume_type("game", "Default")
                elif title.type not in ["game", "program"]:
                    detector_mismatch(
                        f"Title Detector detects {title.type}, which is not valid for 'program'. Assuming default.",
                        error=False
                    )
                    self._assume_type("game", "Default")
                else:
                    self._assume_type(title.type, "Title")
            else:
                if content.type != title.type:
                    detector_mismatch(
                        f"Title detector detected {title.type}, which is not valid.",
                        error=False
                    )
                # This includes: audio, video, text
                self._assume_type(content.type, "Content")

        self.force_target = self.force_target or self._get_target_by_group()
        if self.force_type == "video":
            self._sweep_filebot()
        else:
            self._sweep_files()
