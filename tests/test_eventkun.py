import time
from unittest.mock import patch, Mock

from eventkun_main import build_embed
from nagoya_news import get_nagoya_news

_EMPTY_NEWS = {"名古屋情報通": [], "久屋大通パーク": []}
_SAMPLE_NEWS = {
    "名古屋情報通": [("新店オープン", "https://jouhou.nagoya/1"), ("イベント情報", "https://jouhou.nagoya/2")],
    "久屋大通パーク": [("マルシェ開催", "https://hisayaodoripark.com/1")],
}

# published_parsed は feedparser が返す time.struct_time 形式
_RECENT = time.strptime("2026-05-01", "%Y-%m-%d")   # 今日に近い日付
_OLD    = time.strptime("2020-01-01", "%Y-%m-%d")   # 60日超の古い日付


def _make_entry(title: str, link: str, summary: str = "", published_parsed=None) -> Mock:
    return Mock(title=title, link=link, summary=summary, published_parsed=published_parsed)


def _make_news_feed(entries: list[dict]) -> Mock:
    feed = Mock()
    feed.entries = [
        _make_entry(
            title=e["title"],
            link=e["link"],
            summary=e.get("summary", ""),
            published_parsed=e.get("published_parsed", None),
        )
        for e in entries
    ]
    return feed


# ── build_embed ────────────────────────────────────────────────

def test_build_embed_with_news():
    """ニュースがあるとき、fieldsを持つembedを返す。"""
    with patch("eventkun_main.get_nagoya_news", return_value=_SAMPLE_NEWS):
        embed = build_embed()

    assert embed["title"] == "🎤 今週の名古屋情報 WHY NOT KNOW!?"
    assert "fields" in embed
    field_names = [f["name"] for f in embed["fields"]]
    assert "名古屋情報通" in field_names
    assert "久屋大通パーク" in field_names


def test_build_embed_no_news_shows_fallback():
    """ニュースが0件のとき、descriptionのフォールバックを返す。"""
    with patch("eventkun_main.get_nagoya_news", return_value=_EMPTY_NEWS):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed


# ── get_nagoya_news ────────────────────────────────────────────

def test_get_nagoya_news_returns_both_sources():
    """published_parsed なし記事（日付不明）はそのまま返す。"""
    entries = [{"title": f"記事{i}", "link": f"https://example.com/{i}"} for i in range(4)]
    feeds = [_make_news_feed(entries), _make_news_feed(entries[:2])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    assert len(result["名古屋情報通"]) == 3
    assert len(result["久屋大通パーク"]) == 2


def test_get_nagoya_news_filters_past_events():
    """過去の日付を含むタイトルの記事は除外される。"""
    entries = [
        {"title": "2020年1月1日（水）のイベント", "link": "https://example.com/past"},
        {"title": "日付なし記事", "link": "https://example.com/no-date"},
        {"title": "2099年12月31日（火）の未来イベント", "link": "https://example.com/future"},
    ]
    feeds = [_make_news_feed(entries), _make_news_feed([])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    titles = [t for t, _ in result["名古屋情報通"]]
    assert "2020年1月1日（水）のイベント" not in titles
    assert "日付なし記事" in titles
    assert "2099年12月31日（火）の未来イベント" in titles


def test_get_nagoya_news_uses_latest_date_in_range():
    """期間イベントは終了日で判定する（終了日が未来なら表示）。"""
    entries = [
        {"title": "2020年4月1日〜2099年12月31日のロングイベント", "link": "https://example.com/long"},
    ]
    feeds = [_make_news_feed(entries), _make_news_feed([])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    assert len(result["名古屋情報通"]) == 1


def test_get_nagoya_news_filters_old_rss_entries():
    """RSS掲載日が60日超の記事は除外される。"""
    entries = [
        {"title": "古い記事", "link": "https://example.com/old", "published_parsed": _OLD},
        {"title": "新しい記事", "link": "https://example.com/new", "published_parsed": _RECENT},
    ]
    feeds = [_make_news_feed(entries), _make_news_feed([])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    titles = [t for t, _ in result["名古屋情報通"]]
    assert "古い記事" not in titles
    assert "新しい記事" in titles


def test_get_nagoya_news_no_published_date_not_filtered():
    """published_parsed が None の記事は古さフィルタを通過する。"""
    entries = [
        {"title": "日付不明記事", "link": "https://example.com/unknown", "published_parsed": None},
    ]
    feeds = [_make_news_feed(entries), _make_news_feed([])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    assert len(result["名古屋情報通"]) == 1


def test_get_nagoya_news_sorted_by_published_newest_first():
    """RSS掲載日が新しい順に並ぶ。"""
    entries = [
        {"title": "古い記事", "link": "https://example.com/old", "published_parsed": _OLD},
        {"title": "新しい記事", "link": "https://example.com/new", "published_parsed": _RECENT},
    ]
    feeds = [_make_news_feed(entries), _make_news_feed([])]
    with patch("nagoya_news.feedparser.parse", side_effect=feeds):
        result = get_nagoya_news()

    # 古い記事は60日フィルタで除外されるため、新しい記事のみ
    assert result["名古屋情報通"][0][0] == "新しい記事"


def test_get_nagoya_news_returns_empty_on_failure():
    """フィード取得失敗時は空リストを返す。"""
    with patch("nagoya_news.feedparser.parse", side_effect=Exception("error")):
        result = get_nagoya_news()

    assert result["名古屋情報通"] == []
    assert result["久屋大通パーク"] == []
