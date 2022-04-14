from abc import abstractmethod
from subprocess import Popen
from typing import Literal, TypeAlias, Protocol, List

from types import Torrent

Action: TypeAlias = Literal["move", "hardlink", "duplicate", "symlink"]
Conflict: TypeAlias = Literal["skip", "override", "auto", "index", "fail"]

class FilebotAction(Protocol):
    @abstractmethod
    def get_args(self) -> List[str]: pass

class GetSubs(FilebotAction):
    _torrent: Torrent

    def __init__(self, torrent: Torrent):
        self._torrent = torrent

    def get_args(self):
        return [
            "-get-subtitles",
            "-r",
            self._torrent.root.absolute(),
            "-non-strict",
            "--lang",
            "en"
            "--output"
            "srt",
            "--encoding",
            "utf-8"
        ]


class Rename(FilebotAction):
    torrent: Torrent
    action: Action
    format: str
    conflict: Conflict
    file_filter: str
    output: str
    def __init__(self, torrent: Torrent, action: Action, format: str, conflict: Conflict, file_filter: str, output: str):
        self.output = output
        self.file_filter = file_filter
        self.conflict = conflict
        self.format = format
        self.action = action
        self.torrent = torrent

    def get_args(self):
        return [
            "-rename",
            "-r",
            self.torrent.root.absolute(),
            "-non-strict",
            "--format",
            self.format,
            "--conflict",
            self.conflict,
            "--file-filter",
            self.file_filter,
            "--output",
            self.output
        ]

class FilebotExecutor:
    def __init__(self, exe: str):
        self.exe = exe

    def run(self, cmd: FilebotAction):
        Popen([
            self.exe,
            *cmd.get_args()
        ])
