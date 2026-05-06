import feedparser

_FEEDS = {
    "名古屋情報通":     "https://jouhou.nagoya/feed",
    "久屋大通パーク":   "https://www.hisayaodoripark.com/feed",
}
_ITEMS_PER_SOURCE = 3


def get_nagoya_news() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for source, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            result[source] = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_SOURCE]]
        except Exception:
            result[source] = []
    return result
