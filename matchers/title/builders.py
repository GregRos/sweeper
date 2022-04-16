from __future__ import annotations

from abc import ABC
from typing import List, Iterable, Any

from matchers.title.matchers import RegexpMatcher, TitleMatcher

class TitleGroupBuilder:
    _matchers: List[RegexpMatcher]
    _weights: dict[str, float]
    _group_name: str
    def __init__(self):
        self._matchers = []
        self._weights = weights

    def next_group(self, group_name: str, weights: dict[str, float] | list[str]):
        if isinstance(weights, List):
            self._weights = {k: 1 / len(weights) for k in weights}
        else:
            total_weights = sum((x for k, x in weights.items()))
            self._weights = {k: v / total_weights for k, v in weights.items()}
        self._group_name = group_name
        return self

    def add_words(self, percent: int, words: List[str]):
        all = [
            RegexpMatcher(type, rf"\b{word}\b", weight * percent / 100, self._group_name)
            for word in word_patterns
            for type, weight
            in self._weights.items()
        ]
        self._matchers.extend(all)
        return self

def title_matcher(group_name: str, weights: dict[str, float] | list[str]):
    return TitleGroupBuilder().next_group(group_name, weights)
