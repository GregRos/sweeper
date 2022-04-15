from cli import ProgramArgs
from common import Torrent
from config import file_matcher, title_matcher
from extract import Extractor

# VIDEO
# -
from fail import fail_with
from run_info import print_info


def run_sweep(args: ProgramArgs):
    torrent = Torrent(args.torrent_root)
    orig_torrent = torrent
    content_info = file_matcher.match(torrent)
    extractor = Extractor(args.working_dir)
    best_match = content_info[0]
    if best_match.type == "archive" and best_match.ratio > 0.8:
        torrent = extractor.extract(torrent)
        content_info = file_matcher.match(torrent)

    title_info = title_matcher.match(torrent)

    best_content = content_info[0]
    best_title = title_info[0]
    if best_content.type == "text":
        print_info()
        fail_with(torrent, "Torrent had 'text' content")
    if best_title.type == "video":
        if not best_content.is_mostly("video"):
            fail_with(torrent, "ASD")


