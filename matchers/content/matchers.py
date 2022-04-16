from collections import defaultdict
from pathlib import Path
from typing import List, Iterable

from common.torrent import Torrent
from .matcher import FileMatcher


class ContentMatch:
    def __init__(self, type: str, ratio: float, total: int, exts: List[str]):
        self.ratio = ratio
        self.type = type
        self.total = total
        self.exts = exts

    def is_mostly(self, what: str, at = 0.5):
        return self.type == what and self.ratio >= at

class ContentMatcher:
    extensions: dict[str, FileMatcher]
    def __init__(self, extensions: List[FileMatcher]):
        self.extensions = defaultdict(lambda : ExtensionMatcher("Unknown", "???"))
        for x in extensions:
            self.extensions[x.ext] = x

    def _classify_file(self, file: Path):
        return self.extensions[file.suffix[1:]].get_type(file)

    def match(self, torrent: Torrent) -> List[ContentMatch]:
        total_size = 0
        content_matches: dict[str, ContentMatch] = {}
        for file in torrent.root.glob("**/*"):
            if file.is_dir():
                continue
            file_type = self._classify_file(file)
            size = file.stat().st_size
            if file_type not in content_matches:
                content_matches[file_type] = ContentMatch(
                    type=file_type,
                    ratio=0,
                    total=0,
                    exts=[]
                )

            existing = content_matches[file_type]
            existing.total += size
            existing.exts.append(file.suffix)
            total_size += size

        for k, match in content_matches.items():
            match.ratio = match.total / total_size

        ratio_list = sorted(
            list(content_matches.values())
        , key=lambda x: x.ratio, reverse=True)

        return ratio_list
