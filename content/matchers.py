from collections import defaultdict
from pathlib import Path
from typing import List

from types.torrent import Torrent

class MediaExtension:
    def __init__(self, type: str, ext: str):
        self.ext = ext
        self.type = type

    def test(self, file: Path):
        return file.suffix.lower() == self.ext

class ContentRatio:
    def __init__(self, content: str, ratio: float, total: int):
        self.ratio = ratio
        self.type = content
        self.total = total

class ContentClassifier:
    def __init__(self, extensions: List[MediaExtension]):
        self.extensions = {ext: ext.type for ext in extensions}

    def _classify_file(self, file: Path):
        return self.extensions.get(file.suffix, "?")

    def match(self, torrent: Torrent) -> List[ContentRatio]:
        total_size = 0
        file_size_by_group = defaultdict(lambda x: 0)
        for item in torrent.root.glob("**/*"):
            if item.is_dir():
                continue
            file_type = self._classify_file(item)
            size = item.stat().st_size
            file_size_by_group[file_type] += size
            total_size += size

        ratio_list = sorted([
            ContentRatio(k, v / total_size, v) for k, v in file_size_by_group.items()
        ], key=lambda x: x.ratio, reverse=True)
        return ratio_list
