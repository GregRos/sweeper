from title.builders import for_media_refine, for_media, make_title_matcher

title_matcher = make_title_matcher(
    # RELEASE TYPES
    for_media(
        "game",
        "video"
    ).add_words("GAME_MOVIE_RELEASE_TYPES", 60, [
        "Remastered",
        "Proper",
        "beta",
        "alpha",
        "Preload",
        "Repack",
        r"multi\d",
    ]),

    for_media(
        "game",
        "program"
    ).add_words("CRACK_PATCH", 70, [
        "Crack",
        "Activator",
        "Activated",
        "Keygen",
        "Cracked",
        "Unlocked",
        "Patch",
        "Update"
    ]).add_words("VERSION_PATTERN", 50, [
        # It's low because the last pattern will match the previous one,
        # So actually it's very high sensitivity
        r"v\d+\.\d+",
        r"v\d+\.\d+\.\d+",
        r"v\d+\.\d+\.\d+\.\d+"
    ]).add_words("ISO_FORMAT", 50, [
        "ISO"
    ]),

    for_media_refine({
        "game": 0.3,
        "program": 1
    }).add_words("PC_PLATFORMS", 90, [
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
    ]).add_words("SOFTWARE_KEYWORDS", 50, [
        "Pro",
        "Professional",
        "Retail",
        "RTM",
        r"SP\d",
        "OEM"
    ]),

    for_media(
        "game"
    ).add_words("CONSOLE_PLATFORMS", 90, [
        "PS[43]",
        "3?DS",
        r"X\s?BOX",
        r"PC\s?DVD",
        "BATTLENET",
        "GOG",
        "WII",
        r"Steam[\-. ]?rip"
    ]).add_words("GAME_RELEASE_GROUPS", 80, [
        "FLT",
        "SKIDROW",
        "CODEX",
        "TiNYiSO",
        "KAOS",
        "READNFO",
        "GameWorks",
        "SteamWorks",
        "RG",
    ]).add_words("GAME_KEYWORDS", 60, [
        "DLC"
    ]),

    for_media(
        "video"
    ).add_words("VIDEO_QUALITY", 80, [
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
    ]).add_words("VIDEO_AUDIO_QUALITY", 30, [
        "5.1",
        "7.1",
        "DTS",
        "DDP",
        "ATMOS",
        r"\dch"
    ]).add_words("VIDEO_ENCODINGS", 80, [
        "HEVC",
        "XVID",
        r"[XH][\-.]?26[3456]",
        "MP4",
        "MKV"
    ]).add_words("VIDEO_SOURCES", 80, [
        "WEB-DL",
        "WEBDL",
        "WEB",
        "WEBRip",
        "HDrip",
        "BRRip",
        "DVDRip",
        "HDTV",
        "HDTVRip",
        "AMZN"
    ]).add_words("VIDEO_RELEASE_GROUPS", 80, [
        "ettv",
        "YTS",
        "YIFY",
        "eztv",
        "MeGusta",
        "TGx",
        "EVO"
    ]).add_words("SEASON_PATTERN", 60, [
        r"s[01234]\d"
    ]).add_words("EPISODE_PATTERN", 60, [
        r"s[01234]\de\d\d"
    ]).add_words("VIDEO_KEYWORDS", 50, [
        "Episode",
        "Season",
        "Movie",
        "Series"
    ]),

    for_media(
        "video",
        "audio"
    ).add_words("AUDIO_ENCODINGS", 80, [
        "AC3",
        "AAC",
        "MP3",
        "FLAC"
    ]),

    for_media(
        "audio"
    ).add_words("AUDIO_KEYWORDS", 60, [
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
    ]).add_words("AUDIO_QUALITY", 90, [
        "(320|64|128|256|224|32)\s?kbps",
        r"(24|16)\s?bit",
        r"44.1khz",
        "44khz",
        "44000hz"
    ]),

    for_media(
        "ebook"
    ).add_words("EBOOK_FORMATS", 93, [
        "EPIB",
        "MOBI",
        "PDF",
    ]),
)
