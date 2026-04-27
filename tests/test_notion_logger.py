import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("NOTION_API_KEY", "test_key")
os.environ.setdefault("NOTION_DATABASE_ID", "test_db_id")

from notion_logger import log_daily_page

_WEATHER = {
    "desc": "晴れ",
    "temp": "22",
    "temp_max": "28",
    "temp_min": "18",
    "precip_prob": 10,
    "url": "https://wttr.in/Nagoya",
}
_EVENTS = [
    {"time": "10:00", "summary": "チームミーティング"},
    {"time": "14:00", "summary": "1on1"},
]
_NEWS = {
    "政治": [("ニュース1", "https://example.com/1")],
    "経済": [("ニュース2", "https://example.com/2")],
}


def test_log_daily_page_calls_notion_api():
    mock_client = MagicMock()

    with patch("notion_logger.Client", return_value=mock_client):
        log_daily_page(_WEATHER, _EVENTS, _NEWS)

    mock_client.pages.create.assert_called_once()


def test_log_daily_page_title_contains_date():
    mock_client = MagicMock()

    with patch("notion_logger.Client", return_value=mock_client):
        log_daily_page(_WEATHER, _EVENTS, _NEWS)

    call_kwargs = mock_client.pages.create.call_args.kwargs
    title = call_kwargs["properties"]["title"]["title"][0]["text"]["content"]
    assert "朝の記録" in title


def test_log_daily_page_no_weather():
    mock_client = MagicMock()

    with patch("notion_logger.Client", return_value=mock_client):
        log_daily_page(None, [], {})

    mock_client.pages.create.assert_called_once()


def test_log_daily_page_no_events_shows_placeholder():
    mock_client = MagicMock()

    with patch("notion_logger.Client", return_value=mock_client):
        log_daily_page(_WEATHER, [], _NEWS)

    call_kwargs = mock_client.pages.create.call_args.kwargs
    children = call_kwargs["children"]
    texts = [
        block.get("bulleted_list_item", {}).get("rich_text", [{}])[0]
             .get("text", {}).get("content", "")
        for block in children
        if block.get("type") == "bulleted_list_item"
    ]
    assert "予定はありません" in texts
