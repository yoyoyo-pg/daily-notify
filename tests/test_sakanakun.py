from unittest.mock import patch, Mock

from sakanakun_main import build_embed, get_articles


def _make_feed(entries: list[dict]) -> Mock:
    mock = Mock()
    mock.entries = [Mock(title=e["title"], link=e["link"]) for e in entries]
    return mock


def _make_entries(n: int, prefix: str = "記事") -> list[dict]:
    return [{"title": f"{prefix}{i}", "link": f"https://example.com/{i}"} for i in range(n)]


def test_get_articles_returns_both_sources():
    feeds = [_make_feed(_make_entries(3, "Zenn")), _make_feed(_make_entries(3, "Qiita"))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert "Zenn" in result
    assert "Qiita" in result
    assert len(result["Zenn"]) == 2
    assert len(result["Qiita"]) == 2


def test_get_articles_limits_to_2_per_source():
    feeds = [_make_feed(_make_entries(5)), _make_feed(_make_entries(5))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert len(result["Zenn"]) == 2
    assert len(result["Qiita"]) == 2


def test_get_articles_returns_empty_on_failure():
    with patch("sakanakun_main.feedparser.parse", side_effect=Exception("connection error")):
        result = get_articles()

    assert result["Zenn"] == []
    assert result["Qiita"] == []


def test_get_articles_partial_failure():
    feeds = [Exception("zenn down"), _make_feed(_make_entries(3, "Qiita"))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert result["Zenn"] == []
    assert len(result["Qiita"]) == 2


def test_build_embed_with_articles():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1"), ("Zenn記事2", "https://zenn.dev/2")],
        "Qiita": [("Qiita記事1", "https://qiita.com/1"), ("Qiita記事2", "https://qiita.com/2")],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert embed["title"] == "🐟 ギョギョ！今日の技術トレンドだよ〜！"
    assert "4件" in embed["description"]
    assert len(embed["fields"]) == 4
    assert embed["fields"][0]["name"] == "[Zenn] Zenn記事1"
    assert embed["fields"][2]["name"] == "[Qiita] Qiita記事1"


def test_build_embed_no_articles_shows_fallback():
    with patch("sakanakun_main.get_articles", return_value={"Zenn": [], "Qiita": []}):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed


def test_build_embed_partial_source():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1")],
        "Qiita": [],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert len(embed["fields"]) == 1
    assert "1件" in embed["description"]
