from unittest.mock import patch, MagicMock

from news import get_news


def _make_feed(titles: list[str]) -> MagicMock:
    feed = MagicMock()
    feed.entries = [MagicMock(title=t, link=f"https://example.com/{t}") for t in titles]
    return feed


def test_get_news_returns_two_per_category():
    feeds = [
        _make_feed(["政治1", "政治2", "政治3"]),
        _make_feed(["経済1", "経済2"]),
        _make_feed(["技術1", "技術2"]),
        _make_feed(["AI1", "AI2"]),
    ]

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    assert result["政治"] == [("政治1", "https://example.com/政治1"), ("政治2", "https://example.com/政治2")]
    assert result["経済"] == [("経済1", "https://example.com/経済1"), ("経済2", "https://example.com/経済2")]
    assert result["技術"] == [("技術1", "https://example.com/技術1"), ("技術2", "https://example.com/技術2")]
    assert result["AI"] == [("AI1", "https://example.com/AI1"), ("AI2", "https://example.com/AI2")]


def test_get_news_truncates_to_two():
    feeds = [_make_feed([f"記事{i}" for i in range(10)])] * 4

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    for items in result.values():
        assert len(items) == 2


def test_get_news_fallback_on_error():
    with patch("news.feedparser.parse", side_effect=Exception("feed error")):
        result = get_news()

    assert set(result.keys()) == {"政治", "経済", "技術", "AI"}
    for items in result.values():
        assert items == []
