import sys
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
from pathlib import Path

from extract import archive_exts
from extract.extractor import multipart_archive_pattern
from matchers import make_content_matcher
from matchers import make_title_matcher
from common.fail import get_path_env

title_matcher = make_title_matcher(
    ["game", "video"]
).add_subgroup(
    "GameMovieReleaseType",
    90, [
        "Remastered",
        "Proper",
        "beta",
        "alpha",
        "Preload",
        "Repack",
        r"multi\d*",
    ]
).next_group(
    ["game", "program"]
).add_subgroup(
    "Modification",
    60, [
        "Crack",
        "Activator",
        "Activated",
        "Keygen",
        "Cracked",
        "Unlocked",
        "Patch",
        "Update"
    ]
).add_subgroup(
    "VersionPattern",
    50, [
        # It's low because the last pattern will match the previous one,
        # So actually it's very high sensitivity
        r"v\d+\.\d+\w*",
        r"v\d+\.\d+\.\d+\w*",
        r"v\d+\.\d+\.\d+\.\d+\w*"
    ]
).add_subgroup(
    "IsoFile",
    50, [
        "ISO"
    ]
).next_group(
    {
        "game": 1,
        "program": 2
    }
).add_subgroup(
    "PcPlatform",
    90, [
        "x86",
        "x64",
        r"32\s?bit",
        r"64\s?bit",
        "windows",
        "linux",
        "ubuntu",
        "debian",
        "microsoft",
        r"OS\s?X",
        "Mac",
        "win32",
        "win64"
    ]
).add_subgroup(
    "ProgramKeyword",
    50, [
        "Pro",
        "Professional",
        "Retail",
        "RTM",
        r"SP\d",
        "OEM"
    ]
).next_group(
    ["game"]
).add_subgroup(
    "GamePlatform",
    90, [
        "PS[43]",
        "3?DS",
        r"X\s?BOX",
        r"PC\s?DVD",
        r"Steam[\-. ]?rip"
        "BATTLENET",
        "GOG",
        "WII",
    ]
).add_subgroup(
    "GameGroup", 80, [
        "FLT",
        "SKIDROW",
        "CODEX",
        "TiNYiSO",
        "KAOS",
        "READNFO",
        "GameWorks",
        "SteamWorks",
        "RELOADED",
        "PROPHET",
        "RG",
        "RAZOR1911",
        "HOODLUM",
        "PLAZA",
        "EMPRESS"
    ]
).add_subgroup(
    "GameKeyword", 60, [
        "DLC",
        "Simulator"
    ]
).next_group(
    ["video"]
).add_subgroup(
    "VideoQuality", 80, [
        "(1080|720|540|1440|2160|480)[pi]",
        "10bit",
        "HDR",
        "DolbyD",
        "HDR10",
        "UHD",
        "BDRemux",
        "TrueHD",
        "DDP5",
        "HMAX",
        r"Blu-?Ray",
        "Hi10"
    ]
).add_subgroup(
    "MovieAudioQuality", 30, [
        "5.1",
        "7.1",
        "DTS",
        "DDP",
        "ATMOS",
        r"\dch"
    ]
).add_subgroup(
    "VideoEncoding", 80, [
        "HEVC",
        "XVID",
        r"[XH][\-.]?26[3456]",
        "MP4",
        "MKV"
    ]
).add_subgroup(
    "VideoSource", 80, [
        "WEB-DL",
        "WEBDL",
        "WEB",
        "WEBRip",
        "HDrip",
        "BRRip",
        "DVDRip",
        "HDTV",
        "HDTVRip",
        "AMZN",
    ]
).add_subgroup(
    "VideoGroup",
    80, [
        "ettv",
        "YTS",
        "YIFY",
        "eztv",
        "MeGusta",
        "TGx",
        "EVO",
        "RARBG",
        "SPARKS",
        "GECKOS",
    ]
).add_subgroup(
    "SeasonPattern",
    40,
    [
        r"s[01234]\d"
    ]
).add_subgroup(
    "EpisodePattern",
    40, [
        r"s[01234]\de\d\d"
    ]
).add_subgroup(
    "VideoKeyword", 50, [
        "Episode",
        "Season",
        "Movie",
        "Series"
    ]
).next_group([
    "video",
    "audio"
]
).add_subgroup(
    "AudioEncoding", 80, [
        "AC3",
        "AAC",
        "AAC2",
        "MP3",
        "FLAC"
    ]
).next_group([
    "audio"
]
).add_subgroup(
    "AudioKeyword", 60, [
        r"\dCD",
        "single",
        "album",
        "discography",
        "music",
        "cbr",
        "vbr",
        "audible",
        "audiobook",
        "unabridged",
        "abridged"
    ]
).add_subgroup(
    "AudioQuality", 90, [
        r"(320|64|128|256|224|32)\s?kbps",
        r"(24|16)\s?bit",
        r"44.1khz",
        "44khz",
        "44000hz"
    ]
).next_group([
    "text"
]
).add_subgroup(
    "EbookFormat", 93, [
        "EPUB",
        "MOBI",
        "PDF",
    ]
).finish()

content_matcher = make_content_matcher(
    "video"
).add_exts(
    "ts",
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
    "h264",
    "srt",
    "ssa"
).next_group(
    "audio"
).add_exts(
    "mid",
    "midi",
    "mp3",
    "wav",
    "wma",
    "aac",
    "flac",
    "mka",
    "m4a",
    "m4b",
    "ac3"
).next_group(
    "program"
).add_exts(
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
    "js",
    "dmg",
    "rom",
    "mdf",
    "img",
    "cab",
    "mpq",
    "dat"
).next_group(
    "unsortable"
).add_exts(
    "txt",
    "nfo",
    "markdown",
    "md",
    "markd",
    "mmd",
    "xsl",
    "xslx",
    "xml",
    "json",
    "yaml",
    "yml",
    "rtf",
    "chm",
    "strings",
    "log",
    "url",
    "sfv",
    "tex",
    "css",

).next_group(
    "text"
).add_exts(
    "docx",
    "odt",
    "doc",
    "html",
    "djvu",
    "epub",
    "mobi",
    "pdf",
    "htm",
    "fb2",
    "azw",
    "azw3",
    "kf8",
    "kfx,"
    "prc",
    "xps",
    "oxps"
).next_group(
    "image"
).add_exts(
    "jpg",
    "jpeg",
    "gif",
    "png",
    "tiff",
    "bmp",
    "svg",
    "ico",
    "icns"
).next_group(
    "archive"
).add_exts(
    *archive_exts
).add_pattern(
    multipart_archive_pattern
).finish()

logger = getLogger("sweeper")
logger.addHandler(
    RotatingFileHandler(
        filename=get_path_env(
            "SWEEPER_LOGS",
            is_dir=True,
            can_create=True,
            default=Path(__file__).parent
        ).joinpath("sweeper.log"),
        # 10 MB in size
        maxBytes=10 ** 7,
        # Max 1 GB of logs
        backupCount=100,
        encoding="utf8"
    )
)

info_handler = StreamHandler(
    stream=sys.stdout
)
info_handler.addFilter(lambda x: x.levelno <= 30)
info_handler.setLevel(10)
err_handler = StreamHandler(
    stream=sys.stderr
)
err_handler.setLevel(40)

logger.addHandler(
    err_handler
)
logger.addHandler(
    info_handler
)
logger.setLevel(10)

for handler in logger.handlers:
    handler.setFormatter(
        Formatter(
            fmt="%(asctime)s %(levelname)s: %(message)s",
            datefmt="[%d]%H:%M:%S"
        )
    )
