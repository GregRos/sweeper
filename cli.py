import argparse
from pathlib import Path
from typing import Literal, Optional

from common import Torrent
from scripts.fail import SweeperError, invalid_input, get_input_dir
from scripts.sweep_torrent import SweepAction


class BaseArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class InfoArgs(BaseArgs):
    command: Literal["info"]
    torrent: Torrent


class SweepArgs(BaseArgs):
    command: Literal["sweep"]
    action: SweepAction
    torrent: Torrent
    force_group: Optional[Path]
    force_target: Optional[Path]


def parse_args():
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
        "--force_group",
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
    raw_args = root_parser.parse_args()
    if raw_args.command == "info":
        return InfoArgs(
            command="info",
            torrent=Torrent(raw_args.torrent)
        )
    else:
        return SweepArgs(
            command="sweep",
            torrent=Torrent(raw_args.torrent),
            action=raw_args.action,
            force_target=raw_args.force_target and Path(raw_args.force_target),
            force_group=raw_args.force_group
        )
