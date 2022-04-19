# Sweeper

A python script for sorting media like games, programs, movies, shows, etc. Uses filebot to sort and rename videos.

```
Sorts torrents and renames media to work with streaming servers.

Usage:
    sweeper info <torrent_path>
    sweeper sweep <torrent_path> [options]
    sweeper --help | -h

Options:
    --action=copy                 Copy media files.
    --action=move                 Move media files.
    --action=hard                 Hardlink media files.
    --force_dest=<path>           Force the destination dir. No auto-select.
    --force_type=<type>           Force media type: text, audio, program, game, video, video/{movie,show,anime}
    --conflict=overwrite          If dest exists, overwrite.
    --conflict=index              If dest exists, create new dir with postfix, e.g. /data/movies/your_movie.5
    --conflict=fail               If dest exists, fail.

```

