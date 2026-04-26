from unittest.mock import patch, MagicMock

from news import get_news


def _make_feed(titles: list[str]) -> MagicMock:
    feed = MagicMock()
    feed.entries = [MagicMock(title=t, link=f"https://example.com/{t}") for t in titles]
    return feed


def test_get_news_returns_one_per_category():
    feeds = [
        _make_feed(["政治1", "政治2"]),
        _make_feed(["経済1", "経済2"]),
        _make_feed(["国際1", "国際2"]),
        _make_feed(["AI1", "AI2"]),
        _make_feed(["セキュリティ1", "セキュリティ2"]),
        _make_feed(["Zenn1", "Zenn2"]),
    ]

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    assert result["政治"] == [("政治1", "https://example.com/政治1")]
    assert result["経済"] == [("経済1", "https://example.com/経済1")]
    assert result["国際"] == [("国際1", "https://example.com/国際1")]
    assert result["AI"] == [("AI1", "https://example.com/AI1")]
    assert result["セキュリティ"] == [("セキュリティ1", "https://example.com/セキュリティ1")]
    assert result["Zenn"] == [("Zenn1", "https://example.com/Zenn1")]


def test_get_news_truncates_to_one():
    feeds = [_make_feed([f"記事{i}" for i in range(10)])] * 6

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    for items in result.values():
        assert len(items) == 1


def test_get_news_fallback_on_error():
    with patch("news.feedparser.parse", side_effect=Exception("feed error")):
        result = get_news()

    assert set(result.keys()) == {"政治", "経済", "国際", "AI", "セキュリティ", "Zenn"}
    for items in result.values():
        assert items == []
