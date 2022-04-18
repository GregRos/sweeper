from __future__ import annotations

import sys
import traceback
from logging import getLogger

import config
from cli import parse_args, InfoArgs, SweepArgs
from extract import Extractor
from filebot import FilebotExecutor
from scripts.fail import SweeperError, get_path_env
from scripts.run_info import run_info
from scripts.sweep_torrent import Sweeper
from util import LibraryRoots

logger = getLogger("sweeper")


def run(args: SweepArgs | InfoArgs):
    if args.command == "info":
        run_info(args.torrent)
    else:
        filebot_runner = FilebotExecutor(
            exe=get_path_env("SWEEPER_FILEBOT", is_dir=False, check_exe=True)
        )

        extractor = Extractor(
            working_dir=get_path_env("SWEEPER_WORKING_DIR", is_dir=True, can_create=True)
        )

        library = LibraryRoots(
            get_path_env("SWEEPER_LIBRARY", is_dir=True, can_create=True),
            [
                "movies",
                "audio",
                "shows",
                "programs",
                "games",
                "ebooks"
            ]
        )
        Sweeper(
            action=args.action,
            filebot=filebot_runner,
            library=library,
            torrent=args.torrent,
            extractor=extractor,
            force_type=args.force_type,
            force_target=args.force_target,
            title_matcher=config.title_matcher,
            content_matcher=config.content_matcher,
            conflict=args.conflict,
            force_filebot_type=args.force_filebot_subtype
        ).run_sweep()


if __name__ == '__main__':
    try:
        run(parse_args())
    except Exception as err:
        logger.fatal(
            "Failed!",
            exc_info=err
        )
        exit(2)
