from pathlib import Path
from typing import List


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class Tablizer:
    def __init__(self, column = "|", row_num = True, spacing = 1):
        self.spacing = spacing
        self.row_num = row_num
        self.column = column

    def table(self, rows: List[List[str]]):
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
