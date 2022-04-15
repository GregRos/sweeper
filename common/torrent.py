from __future__ import annotations

from os import PathLike
from pathlib import Path


class Torrent:
    is_temp: bool
    name: str
    root: Path
    total_downloaded: int | None
    def __init__(self, folder: str | PathLike[str], is_temp = False):
        self.is_temp = is_temp
        self.root = Path(folder)
        self.name = self.root.name

