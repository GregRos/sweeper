import argparse
import sys
from logging import getLogger
from pathlib import Path
from typing import Literal, Optional, IO

from common import Torrent, print_cmd
from filebot import FilebotSubtype
from common.fail import get_input_dir
from scripts.sweeper import SweepAction


class BaseArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class InfoArgs(BaseArgs):
    torrent: Torrent


class SubsArgs(BaseArgs):
    torrent: Torrent


class SweepArgs(BaseArgs):
    conflict: Literal["index", "fail", "override"]
    action: SweepAction
    torrent: Torrent
    force_type: Optional[Path]
    force_dest: Optional[Path]
    force_filebot_subtype: FilebotSubtype
    no_subs: bool


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


def format_usage():
    options_block = {
        "--action=copy": "Copy media files. (default)",
        "--action=move": "Move media files.",
        "--action=hard": "Hardlink media files.",
        "--force_dest=<path>": "Force the destination dir.",
        "--force_type=<type>": """
Force media type: text, audio, program, game, video, video/{movie,show,anime}
            """.strip(),
        "--conflict=fail": "If dest exists, fail. (default)",
        "--conflict=override": "If dest exists, overwrite.",
        "--conflict=index": "If dest exists, use dest.$N",
        "--conflict=skip": "If dest exists, skip.",
        "--no-subs": "Don't download subs."
    }
    formatted = "\n".join([
        f"{k.ljust(30).rjust(34)}{v}" for k, v in options_block.items()
    ])
    return f"""
Sorts torrents and renames media to work with streaming servers. Assumes
the path it receives is the root of a torrent download.

Supports:
    games, movies, shows, anime, ebooks, programs 

Normally you'd want to run this as part of an automatic process.

Usage:
    sweeper info <torrent_root>
    sweeper sweep <torrent_root> [options]
    sweeper getsubs <torrent_root>
    sweeper --help | -h

Options:
{formatted}
    """.lstrip()


class CustomizedArgumentParser(argparse.ArgumentParser):
    def format_help(self):
        return format_usage()


def parse_args():
    root_parser = CustomizedArgumentParser(
        add_help=True
    )

    actions = root_parser.add_subparsers(
        title='actions',
        required=True,
        dest='command',
        parser_class=CustomizedArgumentParser
    )
    info = actions.add_parser("info")
    info.add_argument(
        "torrent",
        nargs="+"
    )
    getsubs = actions.add_parser("getsubs", help="gets subs")
    getsubs.add_argument("torrent", nargs="+")
    sweep = actions.add_parser("sweep", help="sort torrent")
    sweep.add_argument(
        "torrent",
        nargs="+"
    )
    sweep.add_argument(
        "--conflict",
        type=str,
        choices=[
            "index",
            "fail",
            "override",
            "skip"
        ],
        default="fail"
    )
    sweep.add_argument(
        "--force-type",
        default=None,
        dest="force_type",
        choices=[
            "video",
            "video/show",
            "video/movie",
            "video/anime",
            "audio",
            "text",
            "program",
            "game"
        ]
    )

    sweep.add_argument(
        "--no-subs",
        default=False,
        dest="no_subs",
        action='store_true'
    )

    sweep.add_argument(
        "--force-dest",
        default=None,
        dest="force_dest",
        type=lambda s: get_input_dir("force-dest", s)
    )
    sweep.add_argument(
        "--action",
        default="copy",
        choices=[
            "move",
            "copy",
            "hard"
        ]
    )
    parsed_args = root_parser.parse_args()
    parsed_args.torrent = get_input_dir('torrent', parsed_args.torrent)

    if parsed_args.command == "info":
        return InfoArgs(
            command="info",
            torrent=Torrent(parsed_args.torrent)
        )
    elif parsed_args.command == "sweep":
        force_type, force_subtype = parse_force_type(parsed_args.force_type)
        return SweepArgs(
            command="sweep",
            torrent=Torrent(parsed_args.torrent),
            action=parsed_args.action,
            force_dest=parsed_args.force_dest,
            force_type=force_type,
            conflict=parsed_args.conflict,
            force_filebot_subtype=force_subtype,
            no_subs=parsed_args.no_subs
        )
    elif parsed_args.command == "getsubs":
        return SubsArgs(
            torrent=Torrent(parsed_args.torrent)

        )
    else:
        raise Exception(f"Unknown command {parsed_args.command}")
