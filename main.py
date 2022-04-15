from __future__ import annotations

import os
from fractions import Fraction
from os.path import relpath
from pathlib import Path

import util
from common import Torrent
from cli import get_cli
from match_files import file_matcher
from match_title import title_matcher

def pretty_float(x: float):
    return round(x, 4)

def print_title_info(torrent: Torrent):
    result = title_matcher.match(torrent)
    by_confidence = "\n".join([
        f"{i + 1}) {chance.type} | {pretty_float(chance.chance)} | {' + '.join(chance.meta_names)} " for i, chance in enumerate(result)
    ])
    print("TITLE INFO")
    print(by_confidence)

def print_file_info(torrent: Torrent):
    result = file_matcher.match(torrent)
    by_confidence = "\n".join([
        f"{i + 1}) {content.type} | {pretty_float(content.ratio)} ({util.sizeof_fmt(content.total)})" for i, content in enumerate(result)
    ])
    print("FILE INFO")
    print(by_confidence)

def get_sibling_path(a: Path, b: os.PathLike[str] | str):
    b = Path(b)
    cur = b
    shared_root = None
    while cur.root != cur.parent:
        if a.is_relative_to(cur):
            shared_root = cur
            break
        cur = cur.parent

    if not shared_root:
        return None

    rel_a = shared_root.relative_to(b)
    rel_b = a.relative_to(shared_root)
    x = 1

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
        print(f"TORRENT {relpath(torrent.root, os.getcwd())}")
        print_info(torrent, args.type)
    elif args.command == "sort":
        raise Exception("Not implemented yet!")
    else:
        raise Exception(f"Unknown command {args.command}")


