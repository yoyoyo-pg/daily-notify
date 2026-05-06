import os

import feedparser
from dotenv import load_dotenv

load_dotenv()

from notifier import send

_FEEDS = {
    "Zenn":  "https://zenn.dev/feed",
    "Qiita": "https://qiita.com/popular-items/feed.atom",
}
_ITEMS_PER_SOURCE = 2
_COLOR = 0x00BCD4  # 水色


def get_articles() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for source, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            result[source] = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_SOURCE]]
        except Exception:
            result[source] = []
    return result


def build_embed() -> dict:
    articles = get_articles()
    fields = []
    for source, items in articles.items():
        if items:
            value = "\n".join(f"・[{title}]({url})" for title, url in items)
            fields.append({"name": source, "value": value, "inline": False})

    if not fields:
        return {
            "title": "🐟 ギョギョ！今日の技術ニュースだよ〜！",
            "description": "ギョ…今日は記事が取れなかったギョ…！🐡",
            "color": _COLOR,
        }
    return {
        "title": "🐟 ギョギョ！今日の技術トレンドだよ〜！",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_SAKANAKUN") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
