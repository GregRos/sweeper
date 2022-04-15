import sys
from typing import NoReturn

from common import Torrent

class SweeperError(Exception):
    def __init__(self, target: Torrent, content_info, title_info):
        self.title_info = title_info
        self.content_info = content_info
        self.target = target
        super().__init__("Sweeper ")



def fail_with(torrent: Torrent, reason: str) -> NoReturn:
    print(f"Failed to process {torrent.name}. Reason: {reason}.", file=sys.stderr)
    exit(1)
