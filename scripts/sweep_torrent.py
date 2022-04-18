import logging
import pprint
import sys
from os import link
from pathlib import Path
from shutil import copytree, move
from typing import Literal, TypeAlias

from common import Torrent
from extract import Extractor
from filebot import FilebotExecutor, FilebotAction
from scripts.fail import SweeperError, not_enough_info, invalid_input, detector_mismatch
from matchers import TitleMatcher, ContentMatcher
from scripts.run_info import to_content_table, to_title_table
from util import uproot_path, LibraryRoots

logger = logging.getLogger("sweeper")

SweepAction: TypeAlias = Literal["copy", "hard", "move"]

base_threshold = 0.55
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


class Sweeper:
    torrent: Torrent
    action: SweepAction
    library: LibraryRoots
    title_matcher: TitleMatcher
    content_matcher: ContentMatcher
    filebot: FilebotExecutor
    extractor: Extractor
    force_target: Path
    force_group: str | None

    def __init__(
            self,
            torrent: Torrent,
            action: SweepAction,
            library: LibraryRoots,
            title_matcher: TitleMatcher,
            content_matcher: ContentMatcher,
            filebot: FilebotExecutor,
            extractor: Extractor,
            force_target: Path = None,
            force_group: str = None):

        self.force_group = force_group
        self.force_target = force_target
        self.extractor = extractor
        self.filebot = filebot
        self.content_matcher = content_matcher
        self.title_matcher = title_matcher
        self.library = library
        self.action = action
        self.torrent = torrent

    def assume_torrent(self, type: str):
        self.force_group = type
        log_code = "Assumption"
        logger.info(
            f"Assuming torrent is of type '{type}'",
            extra={
                "type": log_code
            }
        )

    def sweep_filebot(self):
        self.filebot.rename(
            root=self.torrent.root,
            format=self.get_filebot_format(),
            conflict="skip",
            action=get_filebot_action(self.action)
        )

    def get_filebot_format(self):
        if self.force_target:
            media_root = self.force_target.absolute()
        else:
            media_root = f'[episode ? "{self.library.shows.absolute()}" : "{self.library.movies.absolute()}"] '
        media_path = '[ ~plex.derive[" [tmdb-$id}"][" [$vf, $vc, $ac]"] ]'
        full_path = f"{media_root}/{media_path}".replace("[", "{").replace("]", "}")
        return full_path

    def sweep_files(self):
        logger.info("Chose to sweep as files.")
        sweep_type: SweepAction
        if self.torrent.is_temp:
            logger.info(f"Torrent is temporary dir (prob after extract), so forcing move.")
            self.action = "move"
        logger.info(f"Sweeping with action {self.action}")
        if self.action == "move":
            move(self.torrent.root, self.force_target)
        elif self.action == "copy":
            copytree(self.torrent.root, self.force_target, dirs_exist_ok=True)
        elif self.action == "hard":
            copytree(self.torrent.root, self.force_target, copy_function=link, dirs_exist_ok=True)
        else:
            raise Exception(f"Unknown action {self.action}")

    def run_sweep(self):
        content_info = self.content_matcher.match(self.torrent)
        logger.info("Sweeping « %s »", self.torrent.name)
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

        if self.force_group:
            logger.info(f"force_group received. Forcing {self.force_group}")
        else:
            if not content.is_greater(soft_threshold):
                # This is an error because it shouldn't happen, as it means this is a weird mixed torrent
                # If the torrent has unknown extensions, it would be marked as Unknown.
                not_enough_info(f"Too low content ratio {content.ratio}.", error=True)
            elif content.type == "unsortable":
                invalid_input(f"Torrent content detected as 'unsortable'.")
            elif content.type == "image":
                invalid_input(f"Torrent content detected as 'image', which isn't supported.")
            elif content.type == "Unknown":
                not_enough_info(f"Content matched as Unknown.", error=False)
                if not title.is_greater(certain_threshold):
                    not_enough_info(f"Content is unknown, Title is below threshold.", error=True)
                self.assume_torrent(title.type)
                self.force_group = title.type
            elif content.type == "program":
                self.assume_torrent("program")
                if not title.is_greater(soft_threshold):
                    not_enough_info(f"Title Detector is at {title.chance}, which is low. Assuming default.",
                                    error=False)
                    self.assume_torrent(title.type)
                elif title.type not in ["game", "program"]:
                    detector_mismatch(f"Title Detector detects {title.type}, which is not valid for 'program'. Assuming default.",
                                      error=False)
                    self.assume_torrent("game")
                else:
                    self.assume_torrent(title.type)
            else:
                if content.type != title.type:
                    detector_mismatch(f"Title detector detected {title.type}, which is not valid.",
                                      error=False)
                # This includes: audio, video, text
                self.assume_torrent(content.type)

        if self.force_target:
            pass
        elif self.force_group == "program":
            self.force_target = self.library.programs
        elif self.force_group == "game":
            self.force_target = self.library.games
        elif self.force_group == "audio":
            self.force_target = self.library.audio
        elif self.force_group == "text":
            self.force_target = self.library.ebooks
        elif self.force_group == "image":
            raise NotImplementedError()

        if self.force_group == "video":
            self.sweep_filebot()
        else:
            self.force_target = self.force_target.joinpath(self.torrent.name)
            self.sweep_files()
