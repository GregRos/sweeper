from abc import ABC, abstractmethod
from typing import List

from matchers.content.matchers import ContentMatcher
from matchers.content import ExtensionClassifier


class Builder(ABC):
    @abstractmethod
    def get(self) -> List[ExtensionClassifier]: pass

class MediaTypeBuilder(Builder):
    _extensions: List[str] = []
    def __init__(self, type: str):
        self.type = type
        self._extensions = []

    def add_exts(self, *exts: str):
        self._extensions.extend(exts)
        return self

    def get(self):
        return [
            ExtensionClassifier(self.type, ext) for ext in self._extensions
        ]

def match_exts(type: str):
    return MediaTypeBuilder(type)

def make_file_matcher(*builders: Builder):
    return ContentMatcher([
        ext for builder in builders for ext in builder.get()
    ])

