from typing import List

from common import Torrent
from matchers import ContentMatch
from matchers.content import ContentMatcher
from matchers.title import TitleMatch, TitleMatcher


class TorrentContext:
    def __init__(self, torrent: Torrent, content_matches: List[ContentMatch], title_matches: List[TitleMatch]):
        self.title_matches = title_matches
        self.content_matches = content_matches
        self.torrent = torrent

class TorrentMatchers:
    def __init__(self, title_matcher: TitleMatcher, content_matcher: ContentMatcher):
        self.content_matcher = content_matcher
        self.title_matcher = title_matcher

    def match(self, torrent: Torrent):
        return TorrentContext(
            torrent,
            content_matches=self.content_matcher.match(torrent),
            title_matches=self.title_matcher.match(torrent)
        )
