from __future__ import annotations

import re
from os import mkdir, PathLike
from pathlib import Path
from typing import List

import patoolib

from common import Torrent
from util import is_dir_empty, get_dir_for_torrent

archive_exts = [
    "rar", "7z", "zip", "tar", "gz", "bz2", "cbr", "cb7", "cbt", "z01", "zip.001", "7z.001"
]

multipart_rar = re.compile("\.part(\d+)")

def get_rar_part(file: Path) -> int | None:
    if file.suffix == ".rar" and len(file.suffixes) > 1:
        try_part = multipart_rar.fullmatch(file.stem)
        if not try_part:
            return None
        return int(try_part.group(1))
    return None

class Extractor:
    working_dir: Path

    def __init__(self, working_dir: Path | PathLike[str] | str):
        self.working_dir = Path(working_dir)

    def extract_single(self, target_dir: Path, archive: Path):
        patoolib.extract_archive(archive=archive, outdir=target_dir, interactive=False)

    def extract_all_files(self, target_dir: Path, archives: List[Path]):
        for archive in archives:
            outdir = target_dir / archive.stem
            try_part = get_rar_part(archive)
            if try_part is not None:
                if try_part != 1:
                    continue
                outdir = outdir.with_suffix("")
            outdir.mkdir(exist_ok=True)
            patoolib.extract_archive(
                archive=archive,
                outdir=outdir,
                interactive=False
            )

    def extract(self, torrent: Torrent):
        target_dir = get_dir_for_torrent(self.working_dir, torrent.name)
        all_archives = [
            file for ext in archive_exts for file in torrent.root.glob(f"**/*.{ext}")
        ]
        if not all_archives:
            raise Exception("No archives found")

        target_dir.mkdir(exist_ok=True)

        if len(all_archives) == 1:
            self.extract_single(target_dir, all_archives[0])
        else:
            self.extract_all_files(target_dir, all_archives)

        return Torrent(target_dir, is_temp=True)
