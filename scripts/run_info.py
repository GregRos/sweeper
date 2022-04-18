from typing import List

from common import Torrent
from config import title_matcher, content_matcher
from matchers import ContentMatch, TitleMatch
from util import format_filesize, format_float, Tablizer

tablizer = Tablizer()


def to_content_table(info: List[ContentMatch]):
    table_rows = [
        [x.type, format_float(x.ratio), format_filesize(x.total), ", ".join(x.exts)] for x in info
    ]
    return f"""
CONTENT_INFO
{
    tablizer.format_table(table_rows)
    }    
    """.strip()


def to_title_table(info: List[TitleMatch]):
    table_rows = [
        [
            x.type, format_float(x.chance), ", ".join(x.meta_names)
        ] for x in info
    ]
    return f"""
TITLE_INFO
{
    tablizer.format_table(table_rows)
    }    
    """.strip()


def run_info(torrent: Torrent):
    content_info = content_matcher.match(torrent)
    title_info = title_matcher.match(torrent)
    print(f"Info « {torrent.name} »")
    print(to_title_table(title_info))
    print(to_content_table(content_info))
