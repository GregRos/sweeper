import json

from .torrent import Torrent


def print_cmd(args: list[str]):
    line = json.dumps([str(arg).replace("\\", "/") for arg in args])
    return line
