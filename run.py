from __future__ import annotations

from logging import getLogger

import config
from cli import parse_args, InfoArgs, SweepArgs
from common import print_cmd
from extract import Extractor
from filebot import FilebotExecutor
from common.fail import get_path_env, SweeperError
from scripts.info import run_info
from scripts.sweeper import Sweeper
from util import LibraryRoots

logger = getLogger("sweeper")


def run(args: SweepArgs | InfoArgs):
    logger.info(f"INVOKED {print_cmd(sys.argv)}")
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
            force_dest=args.force_dest,
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
            f"EXCEPTION {' '.join(err.args)}",
            exc_info=err
        )


