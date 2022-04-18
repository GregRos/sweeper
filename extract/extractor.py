from __future__ import annotations

import logging
import re
from os import PathLike
from pathlib import Path
from shutil import copy
from typing import List

import patoolib

from common import Torrent
from util import get_dir_for_torrent

archive_exts = [
    "rar", "7z", "zip", "tar", "gz", "bz2", "z01", "zip.001", "7z.001", "cbr", "cb7", "cbt",
]

multipart_rar = re.compile(r"\.part(\d+)")
logger = logging.getLogger("sweeper")
multipart_archive_pattern = re.compile(r"\.(z\d\d\d|\d\d\d)")


def get_rar_part(file: Path) -> int | None:
    if file.suffix == ".rar" and len(file.suffixes) > 1:
        try_part = multipart_rar.fullmatch(file.stem)
        if not try_part:
            return None
        return int(try_part.group(1))
    return None


def extract_single(target_dir: Path, archive: Path):
    logger.info("Extracting as single archive")
    patoolib.extract_archive(archive=archive, outdir=target_dir, interactive=False)


def extract_all_files(target_dir: Path, archives: List[Path]):
    logger.info("Extracting as multiple archives")
    for archive in archives:
        outdir = target_dir / archive.stem
        patoolib.extract_archive(
            archive=archive,
            outdir=outdir,
            interactive=False,

        )


class Extractor:
    working_dir: Path

    def __init__(self, working_dir: Path | PathLike[str] | str):
        self.working_dir = Path(working_dir)

    def extract(self, torrent: Torrent):
        target_dir = get_dir_for_torrent(self.working_dir, torrent.name)
        target_dir.mkdir(exist_ok=True)
        archives = []
        for file in torrent.root.glob("**/*", ):
            retargeted_path = target_dir.joinpath(file)
            if file.is_dir():
                retargeted_path.mkdir(exist_ok=True)
            elif file.suffix not in archive_exts:
                copy(file, retargeted_path)
            elif (x := get_rar_part(file)) is not None and x > 1:
                archives.append(file)

        if not archives:
            raise Exception("Dir didn't contain an archive.")

        target_dir.mkdir(exist_ok=True)

        if len(archives) == 1:
            extract_single(target_dir, archives[0])
        else:
            extract_all_files(target_dir, archives)

        return Torrent(target_dir, is_temp=True)
