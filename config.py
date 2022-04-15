from content import make_file_matcher, match_exts
from title.builders import match_title_refined, match_title, make_title_matcher

title_matcher = make_title_matcher(
    # RELEASE TYPES
    match_title(
        "game",
        "video"
    ).add_words("GameMovieReleaseType", 90, [
        "Remastered",
        "Proper",
        "beta",
        "alpha",
        "Preload",
        "Repack",
        r"multi\d*",
    ]),

    match_title(
        "game",
        "program"
    ).add_words("Modification", 60, [
        "Crack",
        "Activator",
        "Activated",
        "Keygen",
        "Cracked",
        "Unlocked",
        "Patch",
        "Update"
    ]).add_words("VersionPattern", 50, [
        # It's low because the last pattern will match the previous one,
        # So actually it's very high sensitivity
        r"v\d+\.\d+",
        r"v\d+\.\d+\.\d+",
        r"v\d+\.\d+\.\d+\.\d+"
    ]).add_words("IsoFile", 50, [
        "ISO"
    ]),

    match_title_refined({
        "game": 1,
        "program": 2
    }).add_words("PcPlatform", 90, [
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
    ]).add_words("ProgramKeyword", 50, [
        "Pro",
        "Professional",
        "Retail",
        "RTM",
        r"SP\d",
        "OEM"
    ]),

    match_title(
        "game"
    ).add_words("GamePlatform", 90, [
        "PS[43]",
        "3?DS",
        r"X\s?BOX",
        r"PC\s?DVD",
        r"Steam[\-. ]?rip"
        "BATTLENET",
        "GOG",
        "WII",
    ]).add_words("GameGroup", 80, [
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
    ]).add_words("GameKeyword", 60, [
        "DLC",
        "Simulator"
    ]),

    match_title(
        "video"
    ).add_words("VideoQuality", 80, [
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
        "BluRay"
    ]).add_words("MovieAudioQuality", 30, [
        "5.1",
        "7.1",
        "DTS",
        "DDP",
        "ATMOS",
        r"\dch"
    ]).add_words("VideoEncoding", 80, [
        "HEVC",
        "XVID",
        r"[XH][\-.]?26[3456]",
        "MP4",
        "MKV"
    ]).add_words("VideoSource", 80, [
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
    ]).add_words("VideoGroup", 80, [
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
    ]).add_words("SeasonPattern", 40, [
        r"s[01234]\d"
    ]).add_words("EpisodePattern", 40, [
        r"s[01234]\de\d\d"
    ]).add_words("VideoKeyword", 50, [
        "Episode",
        "Season",
        "Movie",
        "Series"
    ]),

    match_title(
        "video",
        "audio"
    ).add_words("AudioEncoding", 80, [
        "AC3",
        "AAC",
        "AAC2",
        "MP3",
        "FLAC"
    ]),

    match_title(
        "audio"
    ).add_words("AudioKeyword", 60, [
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
    ]).add_words("AudioQuality", 90, [
        r"(320|64|128|256|224|32)\s?kbps",
        r"(24|16)\s?bit",
        r"44.1khz",
        "44khz",
        "44000hz"
    ]),

    match_title(
        "ebook"
    ).add_words("EbookFormat", 93, [
        "EPIB",
        "MOBI",
        "PDF",
    ]),
)

file_matcher = make_file_matcher(
    match_exts(
        "video"
    ).add_exts("mkv", "avi", "flv", "mp4", "mpg", "mov", "vob", "wmv", "mkv", "webm", "mpeg", "ogv", "m4v", "h264", "srt", "ssa"),

    match_exts(
        "audio"
    ).add_exts("mid", "midi", "mp3", "wav", "wma", "aac", "flac", "mka", "m4a", "m4b", "ac3"),

    match_exts(
        "program"
    ).add_exts("exe", "dll", "msi", "apk", "ahk", "jar", "cmd", "bin", "iso", "cue", "js", "dmg", "rom", "mdf", "img"),

    match_exts(
        "ebook"
    ).add_exts("epub", "mobi", "pdf", "cbc"),

    match_exts(
        "text"
    ).add_exts("txt", "nfo", "docx", "markdown", "md", "markd", "mmd", "odf", "doc", "xsl", "xslx", "xml", "json", "yaml", "yml", "rtf", "html", "chm"),

    match_exts(
        "image"
    ).add_exts("jpg", "jpeg", "gif", "png", "tiff", "bmp", "svg", "ico")

)
