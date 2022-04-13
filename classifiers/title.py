from __future__ import annotations

import re
from abc import abstractmethod
from functools import reduce
from typing import List, Protocol

from classifiers.types import Torrent


class Matcher(Protocol):
    @abstractmethod
    def apply(self, other: Torrent) -> int | None: pass

class RegexpMatcher(Matcher):
    def __init__(self, pattern: str, percent: int):
        self.pattern = re.compile(pattern, re.I)
        self.percent = percent

    def apply(self, other: Torrent) -> int | None:
        return self.percent if self.pattern.match(other.name) else None

def from_words(words: List[str], percent: int) -> RegexpMatcher:
    pattern = "|".join(words)
    return RegexpMatcher(pattern, percent)

def from_pattern(path: str, percent: int) -> RegexpMatcher:
    return RegexpMatcher(path, percent)

class BaysianReducer:
    def __init__(self, possible_events: List[Matcher]):
        self._kws = possible_events


class Classifier:
    def __init__(self, pattern: str | List[str], score: int):
        if type(pattern) is str:
            self.pattern = re.compile(pattern, re.I)
        else:
            self.pattern = re.compile("|".join(pattern), re.I)
        self.percent = score

    def match(self, where: str):
        return self.pattern.match(where)


class Reducer:
    def __init__(self, kws: List[Classifier]):
        self._kws = kws

    def calculate(self, torrent_name: str):
        matching = [kw.percent for kw in self._kws if kw.match(torrent_name)]
        # positive events:
        # A = 1 - Prod(1 - M_i)

        # opposite of negative matches:
        # B = Prod(1 + M_i)

        # Then A * B

        is_positive = 1 - reduce(lambda a, b: a * b, [
            1 - m for m in matching if m > 0
        ], 1)
        is_not_negative = reduce(lambda a, b: a * b, [
            1 + m for m in matching if m < 0
        ])
        return is_positive * is_not_negative

