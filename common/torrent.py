from __future__ import annotations

import os
from os import PathLike
from pathlib import Path
from shutil import copy, copytree, move


class Torrent:
    is_temp: bool
    name: str
    root: Path
    total_downloaded: int | None

    def __init__(self, folder: str | PathLike[str], is_temp=False):
        self.is_temp = is_temp
        self.root = Path(folder)
        self.name = self.root.name

    def get_all(self):
        if self.root.is_file():
            return [self.root]
        else:
            return self.root.glob("**/*")

    def move(self, new_root: Path | PathLike[str] | str):
        new_location = new_root / self.root.name
        self.root.rename(new_location)

    def copy(self, new_root: Path | PathLike[str] | str):
        copytree(self.root, new_root, symlinks=True)

    def hard(self, new_root: Path | PathLike[str] | str):
        copytree(self.root, new_root, copy_function=os.link)
