from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable, List, Pattern

from common.torrent import Torrent


class RegexpExtMatcher:
    def __init__(self, t: str, regexp: str | Pattern[str]):
        self._type = t
        if type(regexp) is str:
            self._pattern = re.compile(regexp, re.I)
        else:
            self._pattern = regexp

    def get_type(self):
        return self._type

    def test(self, file: Path) -> bool:
        return bool(self._pattern.fullmatch(file.suffix))  # type: ignore


class ContentMatch:
    def __init__(self, type: str, ratio: float, total: int, exts: set[str]):
        self.ratio = ratio
        self.type = type
        self.total = total
        self.exts = exts

    def one_of(self, *options: str):
        return self.type in options

    def is_greater(self, min: float, type: str | None = None):
        if self.ratio < min:
            return False
        return type is None or self.type == type


class ContentMatcherResult(List[ContentMatch]):
    def __new__(cls, *args: Any, **kwargs: Any):
        return list.__new__(cls)

    def __init__(self, seq: Iterable[ContentMatch] = ()):
        super().__init__(seq)

    def get_type(self, type: str):
        return next(
            (x for x in self if x.type == type), ContentMatch(type, 0, 0, set())
        )


no_match = "Unknown"


class ContentMatcher:
    _matchers: list[RegexpExtMatcher]

    def __init__(self, extensions: List[RegexpExtMatcher]):
        self._matchers = extensions

    def _classify_file(self, file: Path):
        return next(
            (matcher.get_type() for matcher in self._matchers if matcher.test(file)),
            "Unknown",
        )

    def match(self, torrent: Torrent) -> ContentMatcherResult:
        total_size = 0
        content_matches: dict[str, ContentMatch] = {}
        for file in torrent.get_all():
            if file.is_dir():
                continue
            file_type = self._classify_file(file)
            size = file.stat().st_size
            if file_type not in content_matches:
                content_matches[file_type] = ContentMatch(
                    type=file_type, ratio=0, total=0, exts=set()
                )

            existing = content_matches[file_type]
            existing.total += size
            if file.suffix:
                existing.exts.add(file.suffix.lower())
            total_size += size

        for _, match in content_matches.items():
            match.ratio = match.total / total_size

        ratio_list = sorted(
            list(content_matches.values()), key=lambda x: x.ratio, reverse=True
        )

        return ContentMatcherResult(ratio_list)
