import argparse

def get_cli():
    root_parser = argparse.ArgumentParser(description='Torrent sorting script. Can delegate for FileBot')
    actions = root_parser.add_subparsers(title='actions', required=True, dest='command')
    classify = actions.add_parser("info", help="classify torrent type")
    classify.add_argument("--type", choices=[
        "all",
        "title",
        "content"
    ], default="all", type=str)
    classify.add_argument("torrent_root", help="path to the torrent's folder", nargs="+")

    copy = actions.add_parser("sort", help="sort torrent")
    copy.add_argument("torrent_root", help="root folder containing the torrent", nargs="+")
    copy.add_argument("--dry-run", help="see what happens")
    copy.add_argument("--dest", help="new content root", required=True)
    copy.add_argument("--action", help="sorting action", default="copy", choices=[
        "move",
        "copy",
        "hard"
    ])
    return root_parser

