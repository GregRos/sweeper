from __future__ import annotations

from typing import List

from .matchers import RegexpMatcher, TitleMatcher


class TitleGroupBuilder:
    _matchers: List[RegexpMatcher]
    _weights: dict[str, float]

    def __init__(self):
        self._matchers = []

    def next_group(self, weights: dict[str, float] | list[str] = None):
        if isinstance(weights, List):
            self._weights = {k: 1 / len(weights) for k in weights}
        elif isinstance(weights, dict):
            total_weights = sum((x for k, x in weights.items()))
            self._weights = {k: v / total_weights for k, v in weights.items()}
        return self

    def add_subgroup(self, subgroup_name: str, percent: int, words: List[str]):
        all = [
            RegexpMatcher(type, rf"\b{word}\b", weight * percent / 100, subgroup_name)
            for word in words
            for type, weight
            in self._weights.items()
        ]
        self._matchers.extend(all)
        return self

    def finish(self):
        return TitleMatcher(self._matchers)


def make_title_matcher(weights: dict[str, float] | list[str]):
    return TitleGroupBuilder().next_group(weights)
