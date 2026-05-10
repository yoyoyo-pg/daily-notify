from unittest.mock import patch, Mock

from eventkun_main import build_embed
from nagoya_news import get_nagoya_news


_EMPTY_NEWS = {"名古屋情報通": [], "久屋大通パーク": []}
_SAMPLE_NEWS = {
    "名古屋情報通": [("新店オープン", "https://jouhou.nagoya/1"), ("イベント情報", "https://jouhou.nagoya/2")],
    "久屋大通パーク": [("マルシェ開催", "https://hisayaodoripark.com/1")],
}


def _make_news_feed(entries: list[dict]) -> Mock:
    feed = Mock()
    feed.entries = [Mock(title=e["title"], link=e["link"], summary=e.get("summary", "")) for e in entries]
    return feed


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


def test_get_nagoya_news_returns_both_sources():
    """日付なし記事はそのまま返す（名古屋情報通のような一般ニュース想定）。"""
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


def test_get_nagoya_news_returns_empty_on_failure():
    """フィード取得失敗時は空リストを返す。"""
    with patch("nagoya_news.feedparser.parse", side_effect=Exception("error")):
        result = get_nagoya_news()

    assert result["名古屋情報通"] == []
    assert result["久屋大通パーク"] == []
