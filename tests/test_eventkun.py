from unittest.mock import patch, Mock

from events import get_events
from eventkun_main import build_embed


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


def test_build_embed_with_events():
    """イベントがあるとき、fieldsを持つembedを返す。"""
    events = [
        {"title": "名古屋勉強会", "date": "05/02(土)", "place": "名古屋市中区", "url": "https://connpass.com/event/1/"}
    ]
    with patch("eventkun_main.get_events", return_value=events):
        embed = build_embed()

    assert embed["title"] == "🎤 今週の名古屋・愛知イベント（Connpass） WHY NOT GO!?"
    assert "fields" in embed
    assert embed["fields"][0]["name"] == "・05/02(土) 名古屋勉強会"
    assert embed["fields"][0]["value"] == "[名古屋市中区](https://connpass.com/event/1/)"


def test_build_embed_no_events_shows_fallback():
    """イベントが0件のとき、descriptionのフォールバックを返す。"""
    with patch("eventkun_main.get_events", return_value=[]):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed
