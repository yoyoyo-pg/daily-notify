from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from weather import get_weather
from gcalendar import get_today_events
from news import get_news
from journal import create_journal_page
from notifier import send

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

_COLOR_WEATHER = 0x5DADE2
_COLOR_CALENDAR = 0x2ECC71
_COLOR_NEWS = 0xE67E22
_COLOR_JOURNAL = 0x9B59B6


def build_embeds() -> tuple[str, list[dict]]:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"
    greeting = f"💼 グッドモーニング！{date_str}も最高のバリューを出していきましょう！"
    embeds = []

    try:
        w = get_weather()
        weather_embed = {
            "title": f"🌤 名古屋のウェザーコンディション：{w['desc']}",
            "url": w["url"],
            "color": _COLOR_WEATHER,
            "fields": [
                {"name": "🌡 テンペラチャー", "value": f"{w['temp']}°C（Max {w['temp_max']}°C / Min {w['temp_min']}°C）", "inline": True},
                {"name": "☔ プレシピテーション", "value": f"{w['precip_prob']}%", "inline": True},
            ],
        }
    except Exception:
        weather_embed = {
            "title": "🌤 ウェザー情報をフェッチできませんでした",
            "color": _COLOR_WEATHER,
        }
    embeds.append(weather_embed)

    try:
        events = get_today_events()
        description = "\n".join(f"・{e['time']} {e['summary']}" for e in events) if events else "本日はフリーなスケジュールです。ジャスト・ドゥ・イット！"
        calendar_embed = {
            "title": "📅 本日のスケジュール・アジェンダ",
            "description": description,
            "color": _COLOR_CALENDAR,
        }
    except Exception:
        calendar_embed = {
            "title": "📅 本日のスケジュール・アジェンダ",
            "description": "スケジュールをフェッチできませんでした",
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
            "title": "📰 本日のインサイトフルなニュース",
            "color": _COLOR_NEWS,
            "fields": fields,
        }
    except Exception:
        news_embed = {
            "title": "📰 本日のインサイトフルなニュース",
            "description": "ニュースをフェッチできませんでした",
            "color": _COLOR_NEWS,
        }
    embeds.append(news_embed)

    try:
        journal_title = f"ジャーナル {now.year}/{now.month:02d}/{now.day:02d}({_WEEKDAYS[now.weekday()]})"
        journal_url = create_journal_page(journal_title)
        embeds.append({
            "title": "📓 本日のジャーナル・セッション",
            "description": f"[Notionでオープン →]({journal_url})",
            "color": _COLOR_JOURNAL,
            "url": journal_url,
        })
    except Exception:
        pass

    return greeting, embeds


if __name__ == "__main__":
    greeting, embeds = build_embeds()
    send(embeds, content=greeting)
