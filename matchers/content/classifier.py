from pathlib import Path
from typing import Protocol


class FileTypeClassifier(Protocol):
    ext: str
    def get_type(self, file: Path) -> str: pass
