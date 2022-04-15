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

class TitleMatch:
    def __init__(self, type: str, chance: float, meta_names: List[str]):
        self.type = type
        self.chance = chance
        self.meta_names = meta_names

    def at_least(self, v: float):
        return self.chance >= v

class TitleMatchResult:
    def __init__(self, chances: List[TitleMatch], matcher_names: List[str]):
        self.matcher_names = matcher_names
        self.chances = chances


class TitleMatcher:
    def __init__(self, *matchers: Matcher):
        self._matchers = matchers

    def match(self, torrent: Torrent) -> List[TitleMatch]:
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


        # chance no match type is right
        chance_none = prod([1 - P for k, P in all_positive_events.items()])

        # Divide out the (1 - P) factor:
        final_chance_by_group = [
            TitleMatch(t, chance_none / (1 - P), all_matched_by_type[t]) for t, P in all_positive_events.items()
        ]
        # The values we got for the Ps are messed up and a result of bad math.
        # They're not actually probabilities.

        # Add a chance for the unknown
        unknown_chance = TitleMatch("Unknown", chance_none, [])
        final_chance_by_group.append(unknown_chance)

        # Return list of chances in descending order
        chances_by_max = sorted(final_chance_by_group, key=lambda x: x.chance, reverse=True)

        # This is a heuristic correction that seems to work well
        chance_some = 1 - chance_none
        scale_factor = chance_some / chances_by_max[0].chance if len(chances_by_max) > 0 else 0
        for c in final_chance_by_group:
            c.chance *= scale_factor
        return chances_by_max