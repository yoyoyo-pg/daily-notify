import os

import feedparser
from dotenv import load_dotenv

load_dotenv()

from notifier import send

_ZENN_FEED = "https://zenn.dev/feed"
_ITEMS = 3
_COLOR = 0x00BCD4  # 水色


def get_zenn_articles() -> list[tuple[str, str]]:
    try:
        feed = feedparser.parse(_ZENN_FEED)
        return [(e.title, e.link) for e in feed.entries[:_ITEMS]]
    except Exception:
        return []


def build_embed() -> dict:
    articles = get_zenn_articles()
    if not articles:
        return {
            "title": "🐟 ギョギョ！今日の技術ニュースだよ〜！",
            "description": "ギョ…今日はZennの記事が取れなかったギョ…！🐡",
            "color": _COLOR,
        }
    fields = [
        {"name": f"・{title}", "value": url, "inline": False}
        for title, url in articles
    ]
    return {
        "title": "🐟 ギョギョ！今日の技術トレンドだよ〜！",
        "description": f"【Zennより{len(articles)}件ギョ！】",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_SAKANAKUN") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
