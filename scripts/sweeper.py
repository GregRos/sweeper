from __future__ import annotations

import logging
from os import link
from pathlib import Path
from shutil import copytree, move
from typing import Literal, TypeAlias, Any

from common import Torrent
from extract import Extractor
from filebot import FilebotExecutor, FilebotAction, FilebotSubtype
from matchers import TitleMatcher, ContentMatcher
from common.fail import not_enough_info, detector_mismatch, \
    file_exists, raise_bad_input
from scripts.info import to_content_table, to_title_table
from util import get_dir_for_torrent

logger = logging.getLogger("sweeper")
Conflict: TypeAlias = Literal["override", "index", "fail"]

SweepAction: TypeAlias = Literal["copy", "hard", "move"]
soft_threshold = 0.8
hard_threshold = 0.9
certain_threshold = 0.93


def get_filebot_action(action: SweepAction) -> FilebotAction:
    if action == "copy":
        return "copy"
    if action == "hard":
        return "duplicate"
    if action == "move":
        return "move"
    raise Exception("Not here")


filebot_format = '{ ~plex ** " [tmdbid-$id]" % " - [$vf, $vc, $bitrate, $ac]" }'


class Sweeper:
    _torrent: Torrent
    _action: SweepAction
    _library: Any
    _title_matcher: TitleMatcher
    _content_matcher: ContentMatcher
    _filebot: FilebotExecutor
    _extractor: Extractor
    _dest: Path
    _type: str | None
    _filebot_type: FilebotSubtype
    _conflict: Conflict
    _no_subs: bool
    def __init__(
            self,
            torrent: Torrent,
            action: SweepAction,
            library: Any,
            title_matcher: TitleMatcher,
            content_matcher: ContentMatcher,
            filebot: FilebotExecutor,
            extractor: Extractor,
            force_dest: Path = None,
            force_type: str = None,
            force_filebot_type: FilebotSubtype = None,
            conflict: Conflict = "fail",
            no_subs: bool = False
    ):

        self._type = force_type
        self._dest = force_dest
        self._filebot_type = force_filebot_type
        self._extractor = extractor
        self._filebot = filebot
        self._content_matcher = content_matcher
        self._title_matcher = title_matcher
        self._library = library
        self._action = action
        self._torrent = torrent
        self._conflict = conflict
        self._no_subs=  no_subs

    def _assume_type(self, type: str, based_on: str):
        """
        Assumes the type of the media is {type}. This overwrites force_type and emits a log.
        """
        self._type = type
        log_code = "Assumption"
        logger.info(
            f"ASSUMING torrent is of type '{type}' ({based_on})",
            extra={
                "type": log_code
            }
        )

    def _sweep_filebot(self):
        """
        Sweeps by running filebot.
        """
        logger.info(f"CHOSE_METHOD :: filebot ({self._action})")
        try:
            if not self._no_subs:
                self._filebot.down_subs(
                    root=self._torrent.root
                )
        except Exception as err:
            logger.error("Failed to get subs.", exc_info=err)

        self._filebot.rename(
            root=self._torrent.root,
            conflict=self._conflict,
            action=get_filebot_action(self._action),
            force_type=self._filebot_type,
            formats={
                "movie": self._library.movies.absolute().joinpath(filebot_format),
                "series": self._library.shows.absolute().joinpath(filebot_format),
                "anime": self._library.anime.absolute().joinpath(filebot_format)
            }
        )

    def _get_target(self, start: Path):
        next_target = start.joinpath(self._torrent.name)
        if self._conflict == "fail":
            return file_exists(next_target, None)
        elif self._conflict == "index":
            final_target, index = get_dir_for_torrent(self._dest, self._torrent.name)
            file_exists(next_target, f"Adding free suffix '.{index}'.")
            return final_target
        else:
            file_exists(next_target, "Will overwrite.")
            return next_target

    def _sweep_files(self):
        logger.info(f"CHOSE_METHOD :: manual ({self._action})")
        sweep_type: SweepAction
        if self._torrent.is_temp:
            logger.info(f"FORCING move (torrent is temp, after extract)")
            self._action = "move"
        final_target = self._dest.joinpath(self._torrent.name)
        if final_target.exists():
            if self._conflict == "fail":
                file_exists(final_target, None)
            elif self._conflict == "index":
                next_target, index = get_dir_for_torrent(self._dest, self._torrent.name)
                file_exists(final_target, f"Adding free suffix {index}.")
                final_target = next_target
            else:
                file_exists(final_target, "Will overwrite.")

        if self._action == "move":
            move(self._torrent.root, final_target)
        elif self._action == "copy":
            copytree(self._torrent.root, final_target)
        elif self._action == "hard":
            copytree(self._torrent.root, final_target, copy_function=link)
        else:
            raise Exception(f"Unknown action {self._action}")

        logger.info("SWEEPING succeeded.")

    def _get_target_by_group(self):
        if self._type == "program":
            return self._library.programs
        elif self._type == "game":
            return self._library.games
        elif self._type == "audio":
            return self._library.audio
        elif self._type == "text":
            return self._library.ebooks
        elif self._type == "video":
            return None
        elif self._type == "image":
            raise NotImplementedError()

    def run_sweep(self):
        content_info = self._content_matcher.match(self._torrent)
        logger.info(f"SWEEPING {self._torrent.name}")
        content = content_info[0]
        if content.one_of("archive"):
            logger.info(f"Archive extensions found: {', '.join(content.exts)}")
            self._torrent = self._extractor.extract(self._torrent)
            content_info = self._content_matcher.match(self._torrent)
        title_info = self._title_matcher.match(self._torrent)
        logger.info(to_content_table(content_info))
        logger.info(to_title_table(title_info))
        content = content_info[0]
        title = title_info[0]

        if self._type:
            logger.info(f"FORCED type '{self._type}'")
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

        self._dest = self._dest or self._get_target_by_group()
        if self._type == "video":
            self._sweep_filebot()
        else:
            self._sweep_files()
