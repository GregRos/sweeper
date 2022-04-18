import argparse
import json
import sys
from logging import getLogger
from pathlib import Path
from typing import Literal, Optional

from common import Torrent, print_cmd
from filebot import FilebotSubtype
from scripts.fail import get_input_dir
from scripts.sweep_torrent import SweepAction


class BaseArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class InfoArgs(BaseArgs):
    command: Literal["info"]
    torrent: Torrent


class SweepArgs(BaseArgs):
    command: Literal["sweep"]
    conflict: Literal["indexs", "fail", "overwrite"]
    action: SweepAction
    torrent: Torrent
    force_type: Optional[Path]
    force_target: Optional[Path]
    force_filebot_subtype: FilebotSubtype


logger = getLogger("sweeper")

def parse_force_type(force_type: str):
    if force_type:
        split = force_type.split("/")
        if len(split) > 1:
            return split
        else:
            return [force_type, None]
    else:
        return [None, None]

def parse_args():
    logger.info(f"INVOKED {print_cmd(sys.argv)}")

    root_parser = argparse.ArgumentParser(
        description='Torrent sorting script. Can delegate for FileBot'
    )

    actions = root_parser.add_subparsers(title='actions', required=True, dest='command')
    info = actions.add_parser("info", help="classify torrent type")
    info.add_argument(
        "torrent",
        help="path to the torrent's folder",
        type=lambda s: get_input_dir("torrent", s)
    )
    sweep = actions.add_parser("sweep", help="sort torrent")
    sweep.add_argument(
        "torrent",
        help="root folder containing the torrent",
        type=lambda s: get_input_dir("torrent", s)
    )
    sweep.add_argument(
        "--conflict",
        help="What to do in case dest already exists.",
        type=str,
        choices=[
            "index",
            "fail",
            "overwrite"
        ]
    )
    sweep.add_argument(
        "--force_type",
        help="Turn off auto-detect and sweep as a specific content type.",
        required=False,
        default=None,
        choices=[
            "video",
            "video/show",
            "video/movie",
            "audio",
            "text",
            "program",
            "game"
        ]
    )

    sweep.add_argument(
        "--force_target",
        help="Force sweep location",
        required=False,
        default=None,
        type=lambda s: get_input_dir("force_target", s)
    )
    sweep.add_argument("--action", help="sorting action", default="copy", choices=[
        "move",
        "copy",
        "hard"
    ]
                       )
    parsed_args = root_parser.parse_args()
    if parsed_args.command == "info":
        return InfoArgs(
            command="info",
            torrent=Torrent(parsed_args.torrent)
        )
    else:
        force_type, force_subtype = parse_force_type(parsed_args.force_type)

        return SweepArgs(
            command="sweep",
            torrent=Torrent(parsed_args.torrent),
            action=parsed_args.action,
            force_target=parsed_args.force_target,
            force_type=force_type,
            conflict=parsed_args.conflict,
            force_filebot_subtype=force_subtype
        )
