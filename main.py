from __future__ import annotations

import os
from fractions import Fraction
from os.path import relpath
from pathlib import Path

import util
from common import Torrent
from cli import get_cli

from config import file_matcher, title_matcher

tablizer = util.Tablizer()
def pretty_float(x: float):
    return "{:.2f}".format(x)

def print_title_info(torrent: Torrent):
    result = title_matcher.match(torrent)
    info_table = [
        [x.type, pretty_float(x.chance), ", ".join(x.meta_names)] for x in result
    ]
    print("TITLE INFO")
    print(tablizer.table(info_table))

def print_file_info(torrent: Torrent):
    result = file_matcher.match(torrent)
    info_table = [
        [x.type, pretty_float(x.ratio), util.sizeof_fmt(x.total)] for x in result
    ]
    print("FILE INFO")
    print(tablizer.table(info_table))

def print_info(torrent: Torrent, type: str):
    if type == "title":
        print_title_info(torrent)
    elif type == "content":
        print_file_info(torrent)
    elif type == "all":
        print_info(torrent, "title")
        print_info(torrent, "content")
    else:
        raise Exception(f"Unknown info {type}")

if __name__ == '__main__':
    cli = get_cli()
    args = cli.parse_args()
    torrent = Torrent(" ".join(args.torrent_root))
    if args.command == "info":
        print(f"TORRENT {torrent.name}")
        print_info(torrent, args.type)
    elif args.command == "sort":
        raise Exception("Not implemented yet!")
    else:
        raise Exception(f"Unknown command {args.command}")


