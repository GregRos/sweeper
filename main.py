from fractions import Fraction

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
        f"{i + 1}) {chance.type} | {pretty_float(chance.chance)}" for i, chance in enumerate(result.chances)
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

def print_info(torrent: Torrent, type: str):
    match type:
        case "title":
            print_title_info(torrent)
        case "content":
            print_file_info(torrent)
        case "all":
            print_info(torrent, "title")
            print_info(torrent, "content")
        case _:
            raise Exception(f"Unknown info {type}")

if __name__ == '__main__':
    cli = get_cli()
    args = cli.parse_args()
    torrent = Torrent(" ".join(args.torrent_root))
    match args.command:
        case "info":
            print_info(torrent, args.type)
        case "sort":
            raise Exception("Not implemented yet!")

