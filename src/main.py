from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from weather import get_weather
# from gcalendar import get_today_events  # TODO: Google Calendar 連携（未実装）
from news import get_news
from notifier import send
from notion_logger import log_daily_page

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def build_message(weather: dict | None, events: list[dict], news: dict) -> str:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"

    lines = [f"☀️ おはようございます！{date_str}", ""]

    if weather:
        lines += [
            f"🌤 今日の名古屋の天気: {weather['desc']}",
            f"　　気温: {weather['temp']}°C（最高 {weather['temp_max']}°C / 最低 {weather['temp_min']}°C）",
            f"　　降水確率: {weather['precip_prob']}%",
            f"　　{weather['url']}",
        ]
    else:
        lines.append("🌤 天気情報を取得できませんでした")

    lines.append("")

    lines.append("📅 今日の予定")
    if events:
        lines += [f"　・{e['time']} {e['summary']}" for e in events]
    else:
        lines.append("　予定はありません")

    lines.append("")

    lines.append("📰 今日のニュース")
    if news:
        for category, items in news.items():
            for title, link in items:
                lines.append(f"　【{category}】{title}\n　{link}")
    else:
        lines.append("　ニュースを取得できませんでした")

    return "\n".join(lines)


if __name__ == "__main__":
    weather = None
    try:
        weather = get_weather()
    except Exception:
        pass

    events: list[dict] = []
    # TODO: Google Calendar 連携（未実装）
    # try:
    #     events = get_today_events()
    # except Exception:
    #     pass

    news: dict = {}
    try:
        news = get_news()
    except Exception:
        pass

    send(build_message(weather, events, news))

    try:
        log_daily_page(weather, events, news)
    except Exception:
        pass
