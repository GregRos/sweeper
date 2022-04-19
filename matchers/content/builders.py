from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Pattern

from .matchers import RegexpExtMatcher, ContentMatcher


class ContentMatchBuilder:
    _type: str
    _matchers: List[RegexpExtMatcher]

    def __init__(self, type):
        self._type = type
        self._matchers = []

    def add_exts(self, *exts: str):
        self._matchers.append(RegexpExtMatcher(self._type, "|".join((f".{x}" for x in exts))))
        return self

    def add_pattern(self, pattern: str | Pattern):
        self._matchers.append(RegexpExtMatcher(self._type, pattern))
        return self

    def next_group(self, type: str):
        self._type = type
        return self

    def finish(self):
        return ContentMatcher(self._matchers)


def make_content_matcher(type: str):
    return ContentMatchBuilder(type)
