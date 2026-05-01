import os

from dotenv import load_dotenv

load_dotenv()

from notifier import send
from events import get_events

_COLOR = 0xE91E63  # ピンク


def build_embed() -> dict:
    events = get_events()
    if not events:
        return {
            "title": "🎤 今週の名古屋・愛知イベント（Connpass）",
            "description": "なんでイベントがないの!? WHY JAPANESE PEOPLE!?",
            "color": _COLOR,
        }
    fields = [
        {
            "name": f"・{event['date']} {event['title']}",
            "value": f"[{event['place']}]({event['url']})",
            "inline": False,
        }
        for event in events
    ]
    return {
        "title": "🎤 今週の名古屋・愛知イベント（Connpass） WHY NOT GO!?",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_EVENTS") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
