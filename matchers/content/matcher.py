from pathlib import Path


class FileMatcher:
    def __init__(self, type: str, ext: str):
        self.ext = ext
        self._type = type

    def get_type(self, file: Path):
        return self._type

    def test(self, file: Path):
        return file.suffix[:1].lower() == self.ext
