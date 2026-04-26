import feedparser

_FEEDS = {
    "政治":       "https://www3.nhk.or.jp/rss/news/cat04.xml",
    "経済":       "https://www3.nhk.or.jp/rss/news/cat05.xml",
    "国際":       "https://www3.nhk.or.jp/rss/news/cat06.xml",
    "AI":         "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "セキュリティ": "https://rss.itmedia.co.jp/rss/2.0/security.xml",
    "Zenn":       "https://zenn.dev/feed",
}

_ITEMS_PER_CATEGORY = 1


def get_news() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for category, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            result[category] = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_CATEGORY]]
        except Exception:
            result[category] = []
    return result
