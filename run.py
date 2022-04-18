from __future__ import annotations

import sys
import traceback
from logging import getLogger

import config
from cli import parse_args, InfoArgs, SweepArgs
from scripts.fail import SweeperError
from scripts.run_info import run_info
from scripts.sweep_torrent import Sweeper

logger = getLogger("sweeper")


def run(args: SweepArgs | InfoArgs):
    if args.command == "info":
        run_info(args.torrent)
    else:
        Sweeper(
            action=args.action,
            filebot=config.filebot_runner,
            library=config.library,
            torrent=args.torrent,
            extractor=config.extractor,
            force_group=args.force_group,
            force_target=args.force_target,
            title_matcher=config.title_matcher,
            content_matcher=config.content_matcher
        ).run_sweep()


if __name__ == '__main__':
    try:
        run(parse_args())
    except SweeperError as err:
        logger.fatal(
            "Exception!",
            exc_info=err
        )
        exit(2)
