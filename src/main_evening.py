from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from notifier import send

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]
_COLOR_JOURNAL = 0x9B59B6


def build_embed() -> tuple[str, dict]:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"
    content = f"🌙 おつかれさまです！{date_str}の振り返りをしましょう。"
    embed = {
        "title": "📓 振り返りの時間です",
        "description": "今日のやること・やれたことを記録しましょう。",
        "color": _COLOR_JOURNAL,
    }
    return content, embed


if __name__ == "__main__":
    content, embed = build_embed()
    send([embed], content=content)
