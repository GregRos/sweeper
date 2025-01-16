from __future__ import annotations

import logging

import re
from os import PathLike
from pathlib import Path
from typing import List

import patoolib  # type: ignore

from common import Torrent
from util import get_dir_for_torrent

archive_head_pattern = re.compile(
    "|".join(
        [
            f"\\.{x}$"
            for x in [
                "rar",
                "7z",
                "zip",
                "tar",
                "gz",
                "bz2",
                "z01",
                r"zip\.001",
                r"7z\.001",
                "cbr",
                "cb7",
                "cbt",
            ]
        ]
    ),
    re.I,
)

archive_tail_pattern = re.compile(r"\.(z\d+|\d+|r\d+)$", re.I)

multipart_rar = re.compile(r"\.part(\d+)")
logger = logging.getLogger("sweeper")


def get_rar_part(file: Path) -> int | None:
    if file.suffix == ".rar" and len(file.suffixes) > 1:
        try_part = multipart_rar.fullmatch(file.stem)
        if not try_part:
            return None
        return int(try_part.group(1))
    return None


def extract_single(target_dir: Path, archive: Path):
    logger.info("Extracting as single archive")
    patoolib.extract_archive(
        archive=str(archive), outdir=str(target_dir), interactive=False
    )


def extract_all_files(target_dir: Path, archives: List[Path]):
    logger.info("Extracting as multiple archives")
    for archive in archives:
        outdir = target_dir / archive.stem
        patoolib.extract_archive(
            archive=str(archive),
            outdir=str(outdir),
            interactive=False,
        )


class Extractor:
    working_dir: Path

    def __init__(self, working_dir: Path | PathLike[str] | str):
        self.working_dir = Path(working_dir)

    def extract(self, torrent: Torrent):
        target_dir, _ = get_dir_for_torrent(self.working_dir, torrent.name)
        target_dir.mkdir(exist_ok=True)
        heads: list[Path] = []
        for file in torrent.get_all():
            retargeted_path = target_dir.joinpath(file)
            if file.is_dir():
                retargeted_path.mkdir(exist_ok=True)
            elif archive_head_pattern.search(file.name):
                rar_part = get_rar_part(file)
                if rar_part and rar_part > 1:
                    continue
                heads.append(file)
            elif archive_tail_pattern.search(file.name):
                # pass on tails
                pass
            elif (x := get_rar_part(file)) is not None and x > 1:
                heads.append(file)

        if not heads:
            raise Exception("Dir didn't contain an archive.")

        target_dir.mkdir(exist_ok=True)

        if len(heads) == 1:
            extract_single(target_dir, heads[0])
        else:
            extract_all_files(target_dir, heads)

        return Torrent(target_dir, is_temp=True)
