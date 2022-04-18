from pathlib import Path
from typing import List, Any

from scripts.fail import SweeperError, raise_bad_input, raise_bad_env


def format_filesize(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def is_dir_empty(dir: Path):
    if not dir.exists() and dir.is_dir():
        raise Exception("Not a dir or doesn't exist")
    return not any(dir.iterdir())


def get_dir_for_torrent(root: Path, name: str):
    cur = root / name
    index = 1
    while cur.exists():
        if is_dir_empty(cur):
            return cur
        cur = root / f"{name}.{index}"

    return cur


class Tablizer:
    def __init__(self, column="|", row_num=True, spacing=1):
        self.spacing = spacing
        self.row_num = row_num
        self.column = column

    def format_table(self, rows: List[List[str]]):
        padding = self.spacing * " "
        for row_index, row in enumerate(rows):
            if self.row_num:
                row.insert(0, str(row_index + 1))
            for col_ix, col in enumerate(row):
                row[col_ix] = f"{padding}{col}{padding}"

        col_sizes = []

        for row in rows:
            for col_ix, col in enumerate(row):
                if len(col_sizes) <= col_ix:
                    col_sizes.append(0)
                col_sizes[col_ix] = max(col_sizes[col_ix], len(str(col)))

        rows_str = []
        for row in rows:
            rows_str.append(self.column.join([
                col.ljust(col_sizes[col_ix]) for col_ix, col in enumerate(row)
            ]))

        return "\n".join(rows_str)


def format_float(x: float):
    return "{:.2f}".format(x)


def uproot_path(target: Path, old_root: Path, new_root: Path):
    rel = target.relative_to(old_root)
    return new_root.joinpath(rel)


class LibraryRoots(object):
    def __init__(self, root: Path, names: list[str]):
        for name in names:
            p = root.joinpath(name)
            if not p.exists():
                p.mkdir()
            if p.is_file():
                raise_bad_env(f"Library path {p} is a file")
            self.__setattr__(name, root.joinpath(name))

