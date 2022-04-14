from __future__ import annotations

import re
from abc import abstractmethod, ABC
from collections import defaultdict
from itertools import groupby
from math import prod
from typing import Protocol, List, Iterable

from types.torrent import Torrent


class Matcher(Protocol):
    type: str
    meta_name: str
    @abstractmethod
    def apply(self, other: Torrent) -> int | None: pass

class RegexpMatcher(Matcher):
    def __init__(self, type: str, pattern: str, chance: float, meta_name: str):
        self.type = type
        self._pattern = re.compile(pattern, re.I)
        self._chance = chance
        self.meta_name = meta_name

    def apply(self, other: Torrent) -> int | None:
        return self._chance if self._pattern.match(other.name) else 0

class Chance:
    def __init__(self, type: str, chance: float):
        self.type = type
        self.chance = chance

class TitleMatchResult:
    def __init__(self, chances: List[Chance], matcher_names: List[str]):
        self.matcher_names = matcher_names
        self.chances = chances


class TitleMatcher:
    def __init__(self, *matchers: Matcher):
        self._matchers = matchers

    def match(self, torrent: Torrent):
        all_events = defaultdict(list)
        matched = set()
        for m in self._matchers:
            result = m.apply(torrent)
            if result:
                matched.add(m.meta_name)
                all_events[m.type].append(result)

        all_positive_events = {
            key : 1 - prod([
                1 - x for x in all
            ]) for key, all in all_events.items()
        }

        # chance no match type is right
        chance_none = prod([1 - P for k, P in all_positive_events])

        # Divide out the (1 - P) factor and multiply by the P factor:
        final_chance_by_group = [
            Chance(t, chance_none * P / (1 - P)) for t, P in all_positive_events.items()
        ]

        # Return list of chances in descending order
        chances_by_max = sorted(final_chance_by_group, key=lambda x: x.chance, reverse=True)
        return TitleMatchResult(
            chances_by_max,
            list(matched)
        )
