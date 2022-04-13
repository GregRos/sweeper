from typing import List


class ExtGroup:
    def __init__(self, type: str, exts: List[str]):
        self.type = type
        self.exts = exts


all = [
    ExtGroup(
        type="video",
        exts=[
            "mkv",
            "avi",
            "flv",
            "mp4",
            "mpg",
            "mov",
            "vob",
            "wmv",
            "mkv",
            "webm",
            "mpeg",
            "ogv",
            "m4v",
            "h264"
        ]
    ),
    ExtGroup(
        type="audio",
        exts=[
            "mid",
            "midi",
            "mp3",
            "wav",
            "wma",
            "aaac",
            "flac",
            "mka",
            "m4a",
            "m4b",
            "ac3"
        ]
    ),
    ExtGroup(
        type="software",
        exts=[
            "exe",
            "dll",
            "msi",
            "apk",
            "ahk",
            "jar",
            "cmd",
            "bin",
            "iso",
            "cue",
            "js"
        ]
    ),
    ExtGroup(
        type="ebook",
        exts=[
            "epub",
            "mobi",
            "pdf",
            "cbc"
        ]
    ),
    ExtGroup(
        type="text",
        exts=[
            "txt",
            "nfo",
            "docx",
            "markdown",
            "md",
            "markd",
            "mmd",
            "odf",
            "doc",
            "xsl",
            "xslx",
            "xml",
            "json",
            "yaml",
            "yml",
            "rtf",
            "html",
            "chm"
        ]
    )
]
