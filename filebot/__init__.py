from __future__ import annotations

from logging import getLogger
from pathlib import Path
from subprocess import Popen, PIPE
from threading import Thread
from typing import Literal, TypeAlias, IO, Callable

from common import print_cmd
from common.fail import SweeperError

FilebotAction: TypeAlias = Literal[
    "move", "hardlink", "duplicate", "symlink", "copy", "test"
]
FilebotConflict: TypeAlias = Literal["skip", "override", "auto", "index", "fail"]
FilebotSubtype: TypeAlias = Literal["movie", "show", "anime"]
logger = getLogger("sweeper")


def read_all(p: Popen[str], timeout: int):
    def read(stream: IO[str] | None, action: Callable[[str], None]):
        if stream is None:
            return
        for line in stream:
            action(line)

    r_stdout = Thread(
        target=lambda: read(
            p.stdout, lambda s: logger.info(f"[FILEBOT-{p.pid}] {s.strip()}")
        )
    )
    r_stderr = Thread(
        target=lambda: read(
            p.stderr, lambda s: logger.warning(f"[FILEBOT-{p.pid}] ERR :: {s.strip()}")
        )
    )
    r_stdout.start()
    r_stderr.start()
    p.wait(timeout)
    if p.returncode > 0:
        raise SweeperError(
            "FILEBOT_FAILED", f"Process {p.pid} exited with {p.returncode}"
        )


class FilebotExecutor:
    def __init__(self, exe: str | Path):
        self.exe = exe

    def _execute(self, args: list[str | Path], timeout: int):
        args = [self.exe, *args]
        logger.info(f"EXECUTING {print_cmd(args)}")
        p = Popen(args, stdout=PIPE, stderr=PIPE, shell=False, encoding="utf-8")
        logger.info(f"Spawned process at {p.pid}.")
        read_all(p, timeout)

    def down_subs(self, root: Path):
        self._execute(
            [
                "-get-subtitles",
                "-r",
                root.absolute(),
                "-non-strict",
                "--lang",
                "en",
                "--output",
                "srt",
                "--encoding",
                "utf-8",
            ],
            60,
        )

    def _get_force_for_type(self, type: FilebotSubtype | None = None) -> list[str]:
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

    def _get_force_title(self, title: str | None) -> list[str]:
        if title is None:
            return []
        return [f"ut_title={title}"]

    def rename(
        self,
        root: Path,
        action: FilebotAction,
        conflict: FilebotConflict,
        force_type: FilebotSubtype | None,
        formats: dict[str, str],
        interactive: bool,
        force_title: str | None,
        subs: bool,
        multi_media: bool,
    ):
        """
        Processes the torrent using filebot.
        :param multi_media: True if the input has multiple shows/movies etc
        :param interactive: Forces interactive mode (?)
        :param force_title: Forces title
        :param root: The torrent root
        :param action: The action to perform
        :param conflict: What to do if there is a conflict
        :param force_type: Forces the media type
        :param formats: A dictionary of formats, with {"series": "...", "movies": "...", "anime": "..."}
        :param subs: Whether to get subs
        :return:
        """
        format_bindings = [f"{k}Format={v}" for k, v in formats.items()]
        self._execute(
            [
                "-script",
                "fn:amc",
                root.absolute(),
                "-non-strict",
                *(["-get-subtitles"] if subs else []),
                *(["--mode", "interactive"] if interactive else []),
                "--action",
                action,
                "--conflict",
                conflict,
                "--log",
                "all",
                # Useless path needed by amc
                "--output",
                Path(__file__).parent,
                "--def",
                "music=n",
                "artwork=y",
                *self._get_force_for_type(force_type),
                *self._get_force_title(force_title),
                *format_bindings,
            ],
            60 * 60,
        )
