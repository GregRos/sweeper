import re
from pathlib import Path
from typing import List, Pattern

from common.torrent import Torrent


class RegexpExtMatcher:
    def __init__(self, type: str, regexp: str | Pattern):
        self._type = type
        self._pattern = re.compile(regexp, re.I)

    def get_type(self, file: Path):
        return self._type

    def test(self, file: Path):
        return self._pattern.fullmatch(file.suffix)


class ContentMatch:
    def __init__(self, type: str, ratio: float, total: int, exts: set[str]):
        self.ratio = ratio
        self.type = type
        self.total = total
        self.exts = exts

    def one_of(self, *options: str):
        return self.type in options

    def is_greater(self, min: float, type: str = None):
        if self.ratio < min:
            return False
        return type is None or self.type == type


no_match = "Unknown"


class ContentMatcher:
    _matchers: list[RegexpExtMatcher]

    def __init__(self, extensions: List[RegexpExtMatcher]):
        self._matchers = extensions

    def _classify_file(self, file: Path):
        return next(
            (matcher.get_type(file) for matcher in self._matchers if matcher.test(file)),
            "Unknown"
        )

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
                    exts=set()
                )

            existing = content_matches[file_type]
            existing.total += size
            if file.suffix:
                existing.exts.add(file.suffix.lower())
            total_size += size

        for k, match in content_matches.items():
            match.ratio = match.total / total_size

        ratio_list = sorted(
            list(content_matches.values())
            , key=lambda x: x.ratio, reverse=True
        )

        return ratio_list
