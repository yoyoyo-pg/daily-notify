import re
from datetime import datetime, timezone, timedelta

import feedparser

_FEEDS = {
    "名古屋情報通":     "https://jouhou.nagoya/feed",
    "久屋大通パーク":   "https://www.hisayaodoripark.com/feed",
}
_ITEMS_PER_SOURCE = 3
_MAX_AGE_DAYS = 60  # RSS掲載日がこれより古いエントリは除外
_JST = timezone(timedelta(hours=9))
_DATE_PATTERN = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")


def _latest_date(text: str) -> datetime | None:
    """テキスト中の日本語日付を抽出し、最も遅い日付を返す。"""
    dates = []
    for year, month, day in _DATE_PATTERN.findall(text):
        try:
            dates.append(datetime(int(year), int(month), int(day), tzinfo=_JST))
        except ValueError:
            pass
    return max(dates) if dates else None


def _is_upcoming(entry) -> bool:
    """過去イベントを除外する。日付が見つからない場合は表示する。"""
    today = datetime.now(_JST).replace(hour=0, minute=0, second=0, microsecond=0)
    text = f"{entry.title} {getattr(entry, 'summary', '')}"
    latest = _latest_date(text)
    return latest is None or latest >= today


def _published_dt(entry) -> datetime:
    """RSSのpublished_parsedをdatetimeに変換する。不明な場合は古い日時を返す。"""
    t = getattr(entry, "published_parsed", None)
    if t is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    return datetime(*t[:6], tzinfo=timezone.utc)


def _is_recent(entry) -> bool:
    """RSS掲載日が_MAX_AGE_DAYS以内のエントリのみ通す。日付不明は除外しない。"""
    t = getattr(entry, "published_parsed", None)
    if t is None:
        return True
    published = datetime(*t[:6], tzinfo=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(days=_MAX_AGE_DAYS)
    return published >= cutoff


def get_nagoya_news() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for source, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = sorted(feed.entries, key=_published_dt, reverse=True)
            items = [
                (e.title, e.link)
                for e in entries
                if _is_upcoming(e) and _is_recent(e)
            ]
            result[source] = items[:_ITEMS_PER_SOURCE]
        except Exception:
            result[source] = []
    return result
