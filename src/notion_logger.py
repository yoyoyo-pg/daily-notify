import os
from datetime import datetime, timezone, timedelta

from notion_client import Client

_JST = timezone(timedelta(hours=9))


def log_daily_page(weather: dict | None, events: list[dict], news: dict) -> None:
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    database_id = os.environ["NOTION_DATABASE_ID"]

    now = datetime.now(_JST)
    title = now.strftime("%Y/%m/%d") + " 朝の記録"

    children = []

    # 天気
    if weather:
        children.append(_heading("🌤 天気"))
        children.append(_bullet(
            f"{weather['desc']}　{weather['temp']}°C（最高 {weather['temp_max']}°C / 最低 {weather['temp_min']}°C）　降水確率 {weather['precip_prob']}%"
        ))
    else:
        children.append(_heading("🌤 天気"))
        children.append(_bullet("取得できませんでした"))

    # 予定
    children.append(_heading("📅 今日の予定"))
    if events:
        for e in events:
            children.append(_bullet(f"{e['time']}　{e['summary']}"))
    else:
        children.append(_bullet("予定はありません"))

    # ニュース
    children.append(_heading("📰 ニュース"))
    for category, items in news.items():
        for title_text, link in items:
            children.append(_bullet(f"【{category}】{title_text}", url=link))

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "title": {"title": [{"text": {"content": title}}]},
        },
        children=children,
    )


def _heading(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _bullet(text: str, url: str | None = None) -> dict:
    rich_text = {"type": "text", "text": {"content": text}}
    if url:
        rich_text["text"]["link"] = {"url": url}
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [rich_text]},
    }
