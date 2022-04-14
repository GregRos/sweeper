from __future__ import annotations

from pathlib import Path


class Torrent:
    name: str
    root: Path
    total_downloaded: int | None
    def __init__(self, folder: str):
        self.root = Path(folder)
        self.name = self.root.name

