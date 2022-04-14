from content.builders import make_content_matcher, for_media

file_matcher = make_content_matcher(
    for_media(
        "video"
    ).add_extensions(
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
        # sub formats are also here
        "srt",
        "ssa"
    ),

    for_media(
        "audio"
    ).add_extensions(
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
    ),

    for_media(
        "program"
    ).add_extensions(
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
        "img"
    ),

    for_media(
        "ebook"
    ).add_extensions(
        "epub",
        "mobi",
        "pdf",
        "cbc"
    ),

    for_media(
        "text"
    ).add_extensions(
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
    ),

    for_media(
        "image"
    ).add_extensions(
        "jpg",
        "jpeg",
        "gif",
        "png",
        "tiff",
        "bmp",
        "svg",
        "ico"
    )

)
