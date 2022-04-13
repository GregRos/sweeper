import re

from classifiers.title import Reducer, from_pattern, from_words

sorter = Reducer([
    from_pattern("(1080|720|1440|2196|480)[pi]", 80),
    # Codecs, sources, etc
    from_words(["HEVC", "WEB-DL", "XviD", "WEBRip", "HDrip",
                "BRRip", "DVDrip", "Movie", "YTS", "YIFY", "UNRATED"
             ], 85),
    # S01E02 format
    from_pattern(r"\bs[01234]\de\d\d\b", 90),
    from_pattern(r"\bs[0123]\d\b", 60),
    from_pattern(r"Season [1234]\d", 50),
    # Other keywords
    from_words(["BluRay", "XXX"], 50),
    # Gaming words
    from_words([
        "PS3",
        "BATTLENET",
        "XBOX",
        "PS4",
        "FLT",
        "SKIDROW",
        "GOG",
        "CODEX",
        "DLC",
        "Repack",
        "CPY",
        "PROPER",
        "Crack",
        "32\s?bit",
        "64\s?bit",
        "x64",
        "x86",
        "CPY",
        "RELOADED",
        "ISO"
        "Remastered",
        "Preload"
    ], -80),
    from_words([
        "EPUB",
        "PDF",
        "MOBI",
        "Kindle",
        "Audible",
        "Audiobook"
    ], -85),
    # These have the same percentage because the final one will effectively be all 3
    from_words(["v\d+\.\d+"], -20),
    from_words(["v\d+\.\d+\.\d+"], -30),
    from_words(["v\d+\.\d+\.\d+\.\d+"], -30),
    # audio
    from_pattern(r"\d{2,3}\s?kbps", -40),
])

sortables = [
    # Resolutions

]

unsortables = [

    # Books, audiobooks
]

keywords = [
    re.compile("\bPC(DVD)"),

]
