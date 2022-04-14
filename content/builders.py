from abc import ABC, abstractmethod
from typing import Iterable, List

from content.matchers import MediaExtension, ContentClassifier

class Builder(ABC):
    @abstractmethod
    def get(self) -> List[MediaExtension]: pass

class MediaTypeBuilder(Builder):
    _extensions: List[str] = []
    def __init__(self, type: str):
        self.type = type
        self._extensions = []

    def add_extensions(self, *exts: str):
        self._extensions.extend(exts)
        return self

    def get(self):
        return [
            MediaExtension(self.type, ext) for ext in self._extensions
        ]

def for_media(type: str):
    return MediaTypeBuilder(type)

def make_content_matcher(*builders: Builder):
    return ContentClassifier([
        ext for builder in builders for ext in builder.get()
    ])

