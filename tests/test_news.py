from unittest.mock import patch, MagicMock

from news import get_news


def _make_feed(titles: list[str]) -> MagicMock:
    feed = MagicMock()
    feed.entries = [MagicMock(title=t, link=f"https://example.com/{t}") for t in titles]
    return feed


def test_get_news_returns_three_per_category():
    feeds = [
        _make_feed(["国内1", "国内2", "国内3", "国内4"]),
        _make_feed(["経済1", "経済2", "経済3", "経済4"]),
        _make_feed(["国際1", "国際2", "国際3", "国際4"]),
        _make_feed(["AI1", "AI2", "AI3", "AI4"]),
        _make_feed(["セキュリティ1", "セキュリティ2", "セキュリティ3", "セキュリティ4"]),
        _make_feed(["Zenn1", "Zenn2", "Zenn3", "Zenn4"]),
    ]

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    assert result["国内"] == [
        ("国内1", "https://example.com/国内1"),
        ("国内2", "https://example.com/国内2"),
        ("国内3", "https://example.com/国内3"),
    ]
    for category in ["経済", "国際", "AI", "セキュリティ", "Zenn"]:
        assert len(result[category]) == 3


def test_get_news_truncates_to_three():
    feeds = [_make_feed([f"記事{i}" for i in range(10)])] * 6

    with patch("news.feedparser.parse", side_effect=feeds):
        result = get_news()

    for items in result.values():
        assert len(items) == 3


def test_get_news_fallback_on_error():
    with patch("news.feedparser.parse", side_effect=Exception("feed error")):
        result = get_news()

    assert set(result.keys()) == {"国内", "経済", "国際", "AI", "セキュリティ", "Zenn"}
    for items in result.values():
        assert items == []
