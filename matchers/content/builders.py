from abc import ABC, abstractmethod
from typing import List

from matchers.content.matcher import FileMatcher
from matchers.content.matchers import ContentMatcher


class ContentMatchBuilder:
    _type: str
    _matchers: List[FileMatcher]
    def __init__(self, type):
        self._type = type
        self._matchers = []

    def add_exts(self, *exts: str):
        self._matchers.extend([
            FileMatcher(self._type, ext) for ext in exts
        ])

    def next_group(self, type: str):
        self._type = type

    def get(self):
        return self._matchers

def content_matcher(type: str):
    return ContentMatchBuilder(type)
