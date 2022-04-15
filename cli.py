import argparse
from typing import Protocol, cast


class ProgramArgs(Protocol):
    command: str
    working_dir: str
    action: str
    torrent_root: str
    info: bool


def parse_args() -> ProgramArgs:
    root_parser = argparse.ArgumentParser(description='Torrent sorting script. Can delegate for FileBot')

    actions = root_parser.add_subparsers(title='actions', required=True, dest='command')
    classify = actions.add_parser("info", help="classify torrent type")
    classify.add_argument("torrent_root", help="path to the torrent's folder", nargs="+")

    copy = actions.add_parser("sort", help="sort torrent")
    copy.add_argument("torrent_root", help="root folder containing the torrent", nargs="+")
    copy.add_argument("--working_dir", help="Working dir for extracting files", required=True)
    copy.add_argument("--info", help="print info", default=False)
    copy.add_argument("--action", help="sorting action", default="copy", choices=[
        "move",
        "copy",
        "hard"
    ])
    return cast(ProgramArgs, root_parser.parse_args())

