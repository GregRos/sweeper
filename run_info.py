from typing import List

from cli import ProgramArgs
from common import Torrent
from config import file_matcher, title_matcher
from matchers.content import ContentMatch
from matchers.title import TitleMatch
from util import format_float, format_filesize, Tablizer

tablizer = Tablizer()

def print_content_info(info: List[ContentMatch]):
    print("Content Info")
    table = tablizer.format_table([
        [x.type, format_float(x.ratio), format_filesize(x.total), ", ".join(x.exts)] for x in info
    ])
    print(table)


def print_title_info(info: List[TitleMatch]):
    print("Title Info")
    table = tablizer.format_table([
        [
            x.type, format_float(x.chance), ", ".join(x.meta_names)
        ] for x in info
    ])
    print(table)

def print_info(torrent: Torrent, content: List[ContentMatch], title:  List[TitleMatch]):
    print(f"Torrent {torrent.name}")
    print_title_info(title)
    print_content_info(content)

def run_info(args: ProgramArgs):
    torrent = Torrent(args.torrent_root)
    content_info = file_matcher.match(torrent)
    title_info = title_matcher.match(torrent)
    print_info(torrent, content_info, title_info)
