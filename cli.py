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
    command: Literal["info"]
    torrent: Torrent


class SweepArgs(BaseArgs):
    command: Literal["sweep"]
    conflict: Literal["indexs", "fail", "override"]
    action: SweepAction
    torrent: Torrent
    force_type: Optional[Path]
    force_dest: Optional[Path]
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


def format_usage():
    options_block = {
        "--action=copy": "Copy media files.",
        "--action=move": "Move media files.",
        "--action=hard": "Hardlink media files.",
        "--force_dest=<path>": "Force the destination dir. No auto-select.",
        "--force_type=<type>": """
Force media type: text, audio, program, game, video, video/{movie,show,anime}
            """.strip(),
        "--conflict=overwrite": "If dest exists, overwrite.",
        "--conflict=index": "If dest exists, create new dir with postfix, e.g. /data/movies/your_movie.5",
        "--conflict=fail": "If dest exists, fail."
    }
    formatted = "\n".join([
        f"{k.ljust(30).rjust(34)}{v}" for k, v in options_block.items()
    ])
    return f"""
Sorts torrents and renames media to work with streaming servers.

Supports: games, movies, shows, anime, ebooks, programs 
Usage:
    sweeper info <torrent_path>
    sweeper sweep <torrent_path> [options]
    sweeper --help | -h | help

Options:
{formatted}
    """.lstrip()


class CustomizedArgumentParser(argparse.ArgumentParser):
    help_override: str

    def format_help(self):
        return self.help_override


def parse_args():
    root_parser = CustomizedArgumentParser(
        add_help=True
    )
    root_parser.help_override = format_usage()

    actions = root_parser.add_subparsers(title='actions', required=True, dest='command')
    actions.add_parser("help")
    info = actions.add_parser("info")
    info.add_argument(
        "torrent",
        type=lambda s: get_input_dir("torrent", s)
    )
    sweep = actions.add_parser("sweep", help="sort torrent")
    sweep.add_argument(
        "torrent",
        type=lambda s: get_input_dir("torrent", s)
    )
    sweep.add_argument(
        "--conflict",
        type=str,
        choices=[
            "index",
            "fail",
            "override"
        ],
        default="fail"
    )
    sweep.add_argument(
        "--force_type",
        default=None,
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
        "--force_dest",
        default=None,
        type=lambda s: get_input_dir("force_dest", s)
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
    if parsed_args.command == "help":
        root_parser.print_help()
        exit(0)
    elif parsed_args.command == "info":
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
            force_dest=parsed_args.force_dest,
            force_type=force_type,
            conflict=parsed_args.conflict,
            force_filebot_subtype=force_subtype
        )
