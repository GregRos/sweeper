from __future__ import annotations

from logging import getLogger
from pathlib import Path
from subprocess import Popen, PIPE
from threading import Thread
from typing import Literal, TypeAlias, IO, Callable

from common import print_cmd
from common.fail import SweeperError

FilebotAction: TypeAlias = Literal["move", "hardlink", "duplicate", "symlink", "copy", "test"]
FilebotConflict: TypeAlias = Literal["skip", "override", "auto", "index", "fail"]
FilebotSubtype: TypeAlias = Literal["movie", "show", "anime"]
logger = getLogger("sweeper")


def read_all(p: Popen, timeout: int):
    def read(stream: IO, action: Callable[[str], None]):
        for line in stream:
            action(line)

    r_stdout = Thread(
        target=lambda: read(
            p.stdout,
            lambda s: logger.info(f"[FILEBOT-{p.pid}] {s.strip()}")
        )
    )
    r_stderr = Thread(
        target=lambda: read(
            p.stderr,
            lambda s: logger.warning(f"[FILEBOT-{p.pid}] ERR :: {s.strip()}")
        )
    )
    r_stdout.start()
    r_stderr.start()
    p.wait(timeout)
    if p.returncode > 0:
        raise SweeperError("FILEBOT_FAILED", f"Process {p.pid} exited with {p.returncode}")



class FilebotExecutor:
    def __init__(self, exe: str):
        self.exe = exe

    def _execute(self, args: list[str], timeout: int):
        args = [
            self.exe,
            *args
        ]
        logger.info(f"EXECUTING {print_cmd(args)}")
        p = Popen(
            args,
            stdout=PIPE,
            stderr=PIPE,
            shell=False,
            encoding="utf-8"
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
            "en",
            "--output",
            "srt",
            "--encoding",
            "utf-8"
        ], 60
        )

    def _get_force_for_type(self, type: FilebotSubtype = None):
        if type is None:
            return []
        if type == "show":
            return ["ut_label=series"]
        elif type == "movie":
            return ["ut_label=movie"]
        elif type == "anime":
            return ["ut_label=anime"]
        else:
            raise SweeperError("BAD_FILEBOT_TYPE", f"Unknown filebot type '{type}'.")

    def rename(
            self,
            root: Path,
            action: FilebotAction,
            conflict: FilebotConflict,
            force_type: FilebotSubtype,
            formats: dict[str, str],
            subs: bool
    ):
        """
        Processes the torrent using filebot.
        :param root: The torrent root
        :param action: The action to perform
        :param conflict: What to do if there is a conflict
        :param force_type: Forces the media type
        :param formats: A dictionary of formats, with {"series": "...", "movies": "...", "anime": "..."}
        :param subs: Whether to get subs
        :return:
        """
        format_bindings = [f"{k}Format={v}" for k, v in formats.items()]
        self._execute([
            "-script",
            "fn:amc",
            root.absolute(),
            "-non-strict",
            *(["-get-subtitles"] if subs else []),
            "--action",
            action,
            "--conflict",
            conflict,
            "-no-history",
            # Useless path needed by amc
            "--output",
            Path(__file__).parent,
            "--def",
            "music=n",
            *self._get_force_for_type(force_type),
            *format_bindings
        ], 60 * 60)
