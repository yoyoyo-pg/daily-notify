from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from weather import get_weather
from gcalendar import get_today_events
from news import get_news
from notifier import send

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

_COLOR_WEATHER = 0x5DADE2
_COLOR_CALENDAR = 0x2ECC71
_COLOR_NEWS = 0xE67E22


def build_embeds() -> list[dict]:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"
    embeds = []

    try:
        w = get_weather()
        weather_embed = {
            "author": {"name": f"☀️ おはようございます！{date_str}"},
            "title": f"🌤 名古屋の天気：{w['desc']}",
            "url": w["url"],
            "color": _COLOR_WEATHER,
            "fields": [
                {"name": "🌡 気温", "value": f"{w['temp']}°C（最高 {w['temp_max']}°C / 最低 {w['temp_min']}°C）", "inline": True},
                {"name": "☔ 降水確率", "value": f"{w['precip_prob']}%", "inline": True},
            ],
        }
    except Exception:
        weather_embed = {
            "author": {"name": f"☀️ おはようございます！{date_str}"},
            "title": "🌤 天気情報を取得できませんでした",
            "color": _COLOR_WEATHER,
        }
    embeds.append(weather_embed)

    try:
        events = get_today_events()
        description = "\n".join(f"・{e['time']} {e['summary']}" for e in events) if events else "予定はありません"
        calendar_embed = {
            "title": "📅 今日の予定",
            "description": description,
            "color": _COLOR_CALENDAR,
        }
    except Exception:
        calendar_embed = {
            "title": "📅 今日の予定",
            "description": "予定を取得できませんでした",
            "color": _COLOR_CALENDAR,
        }
    embeds.append(calendar_embed)

    try:
        news = get_news()
        fields = [
            {"name": f"【{category}】", "value": f"[{title}]({link})", "inline": False}
            for category, items in news.items()
            for title, link in items
        ]
        news_embed = {
            "title": "📰 今日のニュース",
            "color": _COLOR_NEWS,
            "fields": fields,
        }
    except Exception:
        news_embed = {
            "title": "📰 今日のニュース",
            "description": "ニュースを取得できませんでした",
            "color": _COLOR_NEWS,
        }
    embeds.append(news_embed)

    return embeds


if __name__ == "__main__":
    send(build_embeds())
