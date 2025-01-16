import json
from pathlib import Path
from typing import Iterable

from .torrent import Torrent


def print_cmd(args: Iterable[str | Path]):
    line = json.dumps([str(arg).replace("\\", "/") for arg in args])
    return line
