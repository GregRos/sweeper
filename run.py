from __future__ import annotations

from cli import parse_args
from run_info import print_info, run_info
from run_sweep import run_sweep

if __name__ == '__main__':
    args = parse_args()
    args.torrent_root = " ".join(args.torrent_root)
    if args.command == "info":
        run_info(args)
    else:
        run_sweep(args)


