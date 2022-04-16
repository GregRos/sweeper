from cli import ProgramArgs
from common import Torrent
from config import file_matcher, title_matcher, program_root, audio_root, ebook_root, image_root, game_root, show_root, movie_root
from extract import Extractor

# VIDEO
# -
from fail import fail_with, SweeperError
from run_info import print_info


def exec_action(torrent: Torrent, action: str, new_root: str)
    action = "move" if torrent.is_temp else action
    if action == "hard":
        torrent.hard(new_root)
    elif action == "copy":
        torrent.copy(new_root)
    elif action == "move":
        torrent.move(new_root)
    else:
        raise SweeperError(f"Unknown action {action}")


def run_sweep(args: ProgramArgs):
    torrent = Torrent(args.torrent_root)
    orig_torrent = torrent
    content_info = file_matcher.match(torrent)
    extractor = Extractor(args.working_dir)
    if content_info[0].is_mostly("archive"):
        torrent = extractor.extract(torrent)
        content_info = file_matcher.match(torrent)

    title_info = title_matcher.match(torrent)

    best_content = content_info[0]
    best_title = title_info[0]
    if best_content.is_mostly("text"):
        exec_action(torrent, args.action, text_root)

    if best_content.is_mostly("audio", 0.7):

    if best_title.type == "video":
        if not best_content.is_mostly("video"):
            fail_with(torrent, "ASD")
