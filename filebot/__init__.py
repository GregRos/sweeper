from logging import getLogger
from pathlib import Path
from subprocess import Popen, PIPE
from threading import Thread
from typing import Literal, TypeAlias, IO, Callable

from common import print_cmd

FilebotAction: TypeAlias = Literal["move", "hardlink", "duplicate", "symlink"]
FilebotConflict: TypeAlias = Literal["skip", "override", "auto", "index", "fail"]

logger = getLogger("sweeper")


def read_all(p: Popen, timeout: int):
    def read(stream: IO, action: Callable[[str], None]):
        for line in stream:
            action(line)

    r_stdout = Thread(
        target=lambda: read(
            p.stdout,
            lambda s: logger.info(f"[FILEBOT] OUT :: {s.strip()}")
        )
    )
    r_stderr = Thread(
        target=lambda: read(
            p.stderr,
            lambda s: logger.warning(f"[FILEBOT] ERR :: {s.strip()}")
        )
    )
    r_stdout.start()
    r_stderr.start()
    p.wait(timeout)
    if p.returncode > 0:
        logger.error(f"[FILEBOT] Return code {p.returncode}")
    else:
        logger.info(f"[FILEBOT] Finished successfuly.")


class FilebotExecutor:
    def __init__(self, exe: str):
        self.exe = exe

    def _execute(self, args: list[str], timeout: int):
        args = [
            self.exe,
            *args
        ]
        logger.info(f"EXECUTING: {print_cmd(args)}")
        p = Popen(
            args,
            stdout=PIPE,
            stderr=PIPE,
            shell=False,
            encoding="ansi"
        )
        logger.info(f"Spawned process at {p.pid}.")
        read_all(p, timeout)

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
        ], 20
        )

    def rename(self, root: Path, action: FilebotAction, format: str, conflict: FilebotConflict):
        self._execute([
            "-rename",
            "-r",
            root.absolute(),
            "-non-strict",
            "--format",
            format.replace("\\", "/"),
            "--conflict",
            conflict,
            "--action",
            action
        ], 60
        )
