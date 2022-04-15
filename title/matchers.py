from __future__ import annotations

import re
from abc import abstractmethod, ABC
from collections import defaultdict
from itertools import groupby
from math import prod
from typing import Protocol, List, Iterable

from common.torrent import Torrent


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
        result = self._chance if self._pattern.search(other.name) else 0
        return result

class Chance:
    def __init__(self, type: str, chance: float, meta_names: List[str]):
        self.type = type
        self.chance = chance
        self.meta_names = meta_names


class TitleMatchResult:
    def __init__(self, chances: List[Chance], matcher_names: List[str]):
        self.matcher_names = matcher_names
        self.chances = chances


class TitleMatcher:
    def __init__(self, *matchers: Matcher):
        self._matchers = matchers

    def match(self, torrent: Torrent) -> List[Chance]:
        all_events = defaultdict(list)
        all_matched_by_type = defaultdict(list)
        for m in self._matchers:
            result = m.apply(torrent)
            if result:
                all_matched_by_type[m.type].append(m.meta_name)
                all_events[m.type].append(result)

        all_positive_events = {
            key : 1 - prod([
                1 - x for x in all
            ]) for key, all in all_events.items()
        }

        # Divide out the (1 - P) factor and multiply by the P factor:
        final_chance_by_group = [
            Chance(t, P, all_matched_by_type[t]) for t, P in all_positive_events.items()
        ]

        # Return list of chances in descending order
        chances_by_max = sorted(final_chance_by_group, key=lambda x: x.chance, reverse=True)

        return chances_by_max
