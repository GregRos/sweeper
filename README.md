# Sweeper

A python script for sorting media like games, programs, movies, shows, etc. Uses filebot to sort and rename videos.

```
Sorts torrents and renames media to work with streaming servers. Assumes
the path it receives is the root of a torrent download.

Supports:
    games, movies, shows, anime, ebooks, programs

Normally you'd want to run this as part of an automatic process.

Usage:
    sweeper info <torrent_root>
    sweeper sweep <torrent_root> [options]
    sweeper --help | -h | help

Options:
    --action=copy                 Copy media files. (default)
    --action=move                 Move media files.
    --action=hard                 Hardlink media files.
    --force_dest=<path>           Force the destination dir.
    --force_type=<type>           Force media type: text, audio, program, game, video, video/{movie,show,anime}
    --conflict=fail               If dest exists, fail. (default)
    --conflict=overwrite          If dest exists, overwrite.
    --conflict=index              If dest exists, use dest.$N


```

