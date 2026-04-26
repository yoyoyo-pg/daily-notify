from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from weather import get_weather
# from gcalendar import get_today_events  # TODO: Google Calendar 連携（未実装）
from news import get_news
from notifier import send

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def build_message() -> str:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"

    lines = [f"☀️ おはようございます！{date_str}", ""]

    try:
        w = get_weather()
        lines += [
            f"🌤 今日の名古屋の天気: {w['desc']}",
            f"　　気温: {w['temp']}°C（最高 {w['temp_max']}°C / 最低 {w['temp_min']}°C）",
            f"　　降水確率: {w['precip_prob']}%",
            f"　　{w['url']}",
        ]
    except Exception:
        lines.append("🌤 天気情報を取得できませんでした")

    lines.append("")

    # TODO: Google Calendar 連携（未実装）
    # lines.append("📅 今日の予定")
    # try:
    #     events = get_today_events()
    #     if events:
    #         lines += [f"　・{e['time']} {e['summary']}" for e in events]
    #     else:
    #         lines.append("　予定はありません")
    # except Exception:
    #     lines.append("　予定を取得できませんでした")

    lines.append("")

    lines.append("📰 今日のニュース")
    try:
        news = get_news()
        for category, items in news.items():
            for title, link in items:
                lines.append(f"　【{category}】{title}\n　{link}")
    except Exception:
        lines.append("　ニュースを取得できませんでした")

    return "\n".join(lines)


if __name__ == "__main__":
    send(build_message())
