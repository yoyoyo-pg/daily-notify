import os

from dotenv import load_dotenv

load_dotenv()

from notifier import send
from nagoya_news import get_nagoya_news

_COLOR = 0xE91E63  # ピンク


def build_embed() -> dict:
    news = get_nagoya_news()

    fields = [
        {
            "name": source,
            "value": "\n".join(f"・[{title}]({url})" for title, url in items),
            "inline": False,
        }
        for source, items in news.items()
        if items
    ]

    if not fields:
        return {
            "title": "🎤 今週の名古屋情報",
            "description": "なんで情報がないの!? WHY JAPANESE PEOPLE!?",
            "color": _COLOR,
        }
    return {
        "title": "🎤 今週の名古屋情報 WHY NOT KNOW!?",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_EVENTS") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
