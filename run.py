from __future__ import annotations

import sys
from logging import getLogger

import config
from cli import parse_args, InfoArgs, SweepArgs, SubsArgs
from common import print_cmd
from extract import Extractor
from filebot import FilebotExecutor
from common.fail import get_path_env
from scripts.info import run_info
from scripts.sweeper import Sweeper
from util import LibraryRoots

logger = getLogger("sweeper")


def run(args: SweepArgs | InfoArgs | SubsArgs):
    if type(args) is InfoArgs:
        run_info(args.torrent)
    elif type(args) is SubsArgs:
        filebot_runner = FilebotExecutor(
            exe=get_path_env("SWEEPER_FILEBOT", is_dir=False, check_exe=True)
        )
        filebot_runner.down_subs(args.torrent.root)
        pass
    elif type(args) is SweepArgs:
        filebot_runner = FilebotExecutor(
            exe=get_path_env("SWEEPER_FILEBOT", is_dir=False, check_exe=True)
        )

        extractor = Extractor(
            working_dir=get_path_env(
                "SWEEPER_WORKING_DIR", is_dir=True, can_create=True
            )
        )

        library = LibraryRoots(
            get_path_env("SWEEPER_LIBRARY", is_dir=True, can_create=True),
            ["movies", "audio", "shows", "programs", "games", "ebooks", "anime"],
        )
        Sweeper(
            action=args.action,
            filebot=filebot_runner,
            library=library,
            torrent=args.torrent,
            extractor=extractor,
            force_type=args.force_type,
            force_dest=args.force_dest,
            interactive=args.interactive,
            title_matcher=config.title_matcher,
            content_matcher=config.content_matcher,
            conflict=args.conflict,
            force_filebot_type=args.force_filebot_subtype,
            no_subs=args.no_subs,
            force_title=args.force_title,
        ).run_sweep()


if __name__ == "__main__":
    logger.info(f"INVOKED {print_cmd(sys.argv)}")
    try:
        run(parse_args())
    except Exception as err:
        logger.fatal(f"EXCEPTION {' '.join(err.args)}", exc_info=err)
