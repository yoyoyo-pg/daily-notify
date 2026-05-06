from unittest.mock import patch, Mock

from events import get_events
from eventkun_main import build_embed
from nagoya_news import get_nagoya_news


def _make_response(events: list[dict]) -> Mock:
    """Connpass APIレスポンスのMockを生成する。"""
    mock = Mock()
    mock.raise_for_status = Mock()
    mock.json.return_value = {"events": events}
    return mock


def _make_event(
    title: str = "テストイベント",
    started_at: str = "2026-05-02T10:00:00+09:00",
    place: str = "名古屋市中区",
    event_url: str = "https://connpass.com/event/123/",
) -> dict:
    return {
        "title": title,
        "started_at": started_at,
        "place": place,
        "event_url": event_url,
    }


def test_get_events_returns_correct_format():
    """正常なAPIレスポンスを受け取ったとき、正しい形式のリストを返す。"""
    api_events = [
        _make_event(
            title="名古屋Python勉強会",
            started_at="2026-05-02T10:00:00+09:00",
            place="名古屋市中区",
            event_url="https://connpass.com/event/123/",
        )
    ]
    with patch("events.requests.get", return_value=_make_response(api_events)):
        result = get_events()

    assert len(result) == 1
    assert result[0]["title"] == "名古屋Python勉強会"
    assert result[0]["date"] == "05/02(土)"
    assert result[0]["place"] == "名古屋市中区"
    assert result[0]["url"] == "https://connpass.com/event/123/"


def test_get_events_empty_place_becomes_online():
    """placeが空文字のとき、"オンライン"になる。"""
    api_events = [_make_event(place="")]
    with patch("events.requests.get", return_value=_make_response(api_events)):
        result = get_events()

    assert result[0]["place"] == "オンライン"


def test_get_events_none_place_becomes_online():
    """placeがNoneのとき、"オンライン"になる。"""
    api_events = [_make_event(place=None)]
    with patch("events.requests.get", return_value=_make_response(api_events)):
        result = get_events()

    assert result[0]["place"] == "オンライン"


def test_get_events_returns_empty_list_on_failure():
    """API呼び出しに失敗したとき、空リストを返す。"""
    with patch("events.requests.get", side_effect=Exception("connection error")):
        result = get_events()

    assert result == []


def test_get_events_http_error_returns_empty_list():
    """HTTPエラーが発生したとき、空リストを返す。"""
    mock = Mock()
    mock.raise_for_status.side_effect = Exception("404 Not Found")
    with patch("events.requests.get", return_value=mock):
        result = get_events()

    assert result == []


def test_get_events_date_format_weekdays():
    """started_atの日付フォーマット変換が各曜日で正しい。"""
    # 2026-05-04 は月曜日
    api_events = [_make_event(started_at="2026-05-04T09:00:00+09:00")]
    with patch("events.requests.get", return_value=_make_response(api_events)):
        result = get_events()

    assert result[0]["date"] == "05/04(月)"


def test_get_events_multiple_events():
    """複数イベントが正しく返る。"""
    api_events = [
        _make_event(title=f"イベント{i}", started_at=f"2026-05-0{i+1}T10:00:00+09:00", place=f"場所{i}")
        for i in range(3)
    ]
    with patch("events.requests.get", return_value=_make_response(api_events)):
        result = get_events()

    assert len(result) == 3
    assert result[0]["title"] == "イベント0"
    assert result[1]["title"] == "イベント1"
    assert result[2]["title"] == "イベント2"


def test_get_events_empty_response():
    """イベントが0件のAPIレスポンスでは空リストを返す。"""
    with patch("events.requests.get", return_value=_make_response([])):
        result = get_events()

    assert result == []


_EMPTY_NEWS = {"名古屋情報通": [], "久屋大通パーク": []}
_SAMPLE_NEWS = {
    "名古屋情報通": [("新店オープン", "https://jouhou.nagoya/1"), ("イベント情報", "https://jouhou.nagoya/2")],
    "久屋大通パーク": [("マルシェ開催", "https://hisayaodoripark.com/1")],
}


def test_build_embed_with_events():
    """イベントがあるとき、Connpassイベントのfieldsを持つembedを返す。"""
    events = [
        {"title": "名古屋勉強会", "date": "05/02(土)", "place": "名古屋市中区", "url": "https://connpass.com/event/1/"}
    ]
    with patch("eventkun_main.get_events", return_value=events), \
         patch("eventkun_main.get_nagoya_news", return_value=_EMPTY_NEWS):
        embed = build_embed()

    assert embed["title"] == "🎤 今週の名古屋・愛知イベント（Connpass） WHY NOT GO!?"
    assert "fields" in embed
    assert embed["fields"][0]["name"] == "・05/02(土) 名古屋勉強会"
    assert embed["fields"][0]["value"] == "[名古屋市中区](https://connpass.com/event/1/)"


def test_build_embed_no_events_shows_fallback():
    """イベントもニュースも0件のとき、descriptionのフォールバックを返す。"""
    with patch("eventkun_main.get_events", return_value=[]), \
         patch("eventkun_main.get_nagoya_news", return_value=_EMPTY_NEWS):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed


def test_build_embed_includes_news_fields():
    """ニュースがあるとき、イベントfieldsの後にニュースfieldsが追加される。"""
    events = [
        {"title": "名古屋勉強会", "date": "05/02(土)", "place": "名古屋市中区", "url": "https://connpass.com/event/1/"}
    ]
    with patch("eventkun_main.get_events", return_value=events), \
         patch("eventkun_main.get_nagoya_news", return_value=_SAMPLE_NEWS):
        embed = build_embed()

    field_names = [f["name"] for f in embed["fields"]]
    assert "・05/02(土) 名古屋勉強会" in field_names
    assert "名古屋情報通" in field_names
    assert "久屋大通パーク" in field_names


def test_build_embed_news_only_when_no_events():
    """Connpassイベントがなくてもニュースがあれば表示する。"""
    with patch("eventkun_main.get_events", return_value=[]), \
         patch("eventkun_main.get_nagoya_news", return_value=_SAMPLE_NEWS):
        embed = build_embed()

    assert "fields" in embed
    assert "description" not in embed
    field_names = [f["name"] for f in embed["fields"]]
    assert "名古屋情報通" in field_names


def _make_news_feed(entries: list[dict]) -> Mock:
    feed = Mock()
    feed.entries = [Mock(title=e["title"], link=e["link"], summary=e.get("summary", "")) for e in entries]
    return feed


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
