from unittest.mock import patch, Mock

from sakanakun_main import build_embed, get_zenn_articles


def _make_feed(entries: list[dict]) -> Mock:
    mock = Mock()
    mock.entries = [Mock(title=e["title"], link=e["link"]) for e in entries]
    return mock


def test_get_zenn_articles_returns_list():
    entries = [
        {"title": "Pythonの新機能ギョ", "link": "https://zenn.dev/articles/1"},
        {"title": "TypeScript入門ギョ", "link": "https://zenn.dev/articles/2"},
        {"title": "RustでWebAssembly", "link": "https://zenn.dev/articles/3"},
    ]
    with patch("sakanakun_main.feedparser.parse", return_value=_make_feed(entries)):
        result = get_zenn_articles()

    assert len(result) == 3
    assert result[0] == ("Pythonの新機能ギョ", "https://zenn.dev/articles/1")


def test_get_zenn_articles_limits_to_3():
    entries = [{"title": f"記事{i}", "link": f"https://zenn.dev/articles/{i}"} for i in range(5)]
    with patch("sakanakun_main.feedparser.parse", return_value=_make_feed(entries)):
        result = get_zenn_articles()

    assert len(result) == 3


def test_get_zenn_articles_returns_empty_on_failure():
    with patch("sakanakun_main.feedparser.parse", side_effect=Exception("connection error")):
        result = get_zenn_articles()

    assert result == []


def test_build_embed_with_articles():
    articles = [
        ("Pythonの新機能", "https://zenn.dev/articles/1"),
        ("TypeScript入門", "https://zenn.dev/articles/2"),
    ]
    with patch("sakanakun_main.get_zenn_articles", return_value=articles):
        embed = build_embed()

    assert embed["title"] == "🐟 ギョギョ！今日の技術トレンドだよ〜！"
    assert "fields" in embed
    assert embed["fields"][0]["name"] == "・Pythonの新機能"
    assert embed["fields"][0]["value"] == "https://zenn.dev/articles/1"
    assert "2件" in embed["description"]


def test_build_embed_no_articles_shows_fallback():
    with patch("sakanakun_main.get_zenn_articles", return_value=[]):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed
