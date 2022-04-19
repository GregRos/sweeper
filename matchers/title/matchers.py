from __future__ import annotations

import re
from collections import defaultdict
from math import prod
from typing import List

from common.torrent import Torrent


class RegexpMatcher:
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

    def one_of(self, *types: str):
        return self.type in types

    def is_greater(self, min: float, type: str = None):
        if self.chance < min:
            return False
        return type is None or self.type == type


class TitleMatcher:
    def __init__(self, matchers: List[RegexpMatcher]):
        self._matchers = matchers

    def match(self, torrent: Torrent) -> List[TitleMatch]:
        all_events = defaultdict(list)
        all_matched_by_type = defaultdict(set)
        for m in self._matchers:
            result = m.apply(torrent)
            if result:
                all_matched_by_type[m.type].add(m.meta_name)
                all_events[m.type].append(result)

        # The following calculation is wrong because it assumes detections are independent
        # events, but they're really not. Also the calculation in step 2 is just misguided.
        all_positive_events = {
            key: 1 - prod([
                1 - x for x in all
            ]) for key, all in all_events.items()
        }

        # This is based on real math but isn't right.
        chance_none = prod([1 - P for k, P in all_positive_events.items()])
        final_chance_by_group = [
            TitleMatch(t, chance_none / (1 - P), list(all_matched_by_type[t])) for t, P in
            all_positive_events.items()
        ]
        unknown_chance = TitleMatch("Unknown", chance_none, [])

        if len(final_chance_by_group) > 0:
            # We return a match list in descending order
            chances_by_max = sorted(final_chance_by_group, key=lambda x: x.chance, reverse=True)

            # This is a heuristic correction to bad math that seems to work in practice:
            chance_some = 1 - chance_none
            scale_factor = chance_some / chances_by_max[0].chance
            for c in final_chance_by_group:
                c.chance *= scale_factor
            # This is helpful for later.
            final_chance_by_group.append(unknown_chance)
            return chances_by_max
        else:
            return [unknown_chance]
