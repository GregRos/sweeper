import sys
from pathlib import Path
from subprocess import Popen
from typing import Literal, TypeAlias

FilebotAction: TypeAlias = Literal["move", "hardlink", "duplicate", "symlink"]
FilebotConflict: TypeAlias = Literal["skip", "override", "auto", "index", "fail"]


class FilebotExecutor:
    def __init__(self, exe: str):
        self.exe = exe

    def _execute(self, args: list[str]):
        p = Popen([
            self.exe,
            *args
        ], stdout=sys.stdout, stderr=sys.stderr, shell=False)
        return p

    def down_subs(self, root: Path):
        self._execute([
            "-get-subtitles",
            "-r",
            root.absolute(),
            "-non-strict",
            "--lang",
            "en"
            "--output"
            "srt",
            "--encoding",
            "utf-8"
        ]).wait(20)

    def rename(self, root: Path, action: FilebotAction, format: str, conflict: FilebotConflict):
        self._execute([
            "-rename",
            "-r",
            root.absolute(),
            "-non-strict",
            "--format",
            format,
            "--conflict",
            conflict,
            "--action",
            action
        ]).wait(60)
