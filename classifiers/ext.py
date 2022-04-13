from pathlib import Path
from typing import List

from classifiers.types import Torrent


class ExtGroup:
    def __init__(self, type: str, exts: List[str]):
        self.type = type
        self.exts = exts

class CrawlFiles:
    def __init__(self, *groups: ExtGroup):
        self.groups = groups

    def _calc_size(self, path: Path):
        return

    def _classify_file(self, file: Path):
        for group in self.groups:
            ext = file.suffix
            if ext in group.exts:
                return group.type

    def classify(self, torrent: Torrent) -> None | str:
        file_size_by_group = {group.type: 0 for group in self.groups}
        for item in torrent.root.glob("**/*"):
            if item.is_dir():
                continue
            file_type = self._classify_file(item)
            file_size_by_group[file_type] += item.stat().st_size
        total_sigze
