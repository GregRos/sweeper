from __future__ import annotations

import re
from pathlib import Path

total_downloaded_regexp=re.compile("total_downloadedi(?P<size>\d*)e")

class Torrent:
    name: str
    root: Path
    total_downloaded: int | None
    def __init__(self, folder: str):
        self.root = Path(folder)
        self.name = self.root.name
        rt_file = next(self.root.glob("*.rtorrent"), None)
        if rt_file:
            txt = rt_file.open("r", encoding="ascii").read()
            self.total_downloaded = total_downloaded_regexp.match(txt).group("size")
        self.name = folder

