import os
from unittest.mock import patch, MagicMock

import pytest

os.environ.setdefault("NOTION_API_KEY", "test_notion_key")
os.environ.setdefault("NOTION_PARENT_PAGE_ID", "test_parent_id")

from journal import create_journal_page

_TITLE = "ジャーナル 2026/04/26(日)"
_NOTION_URL = "https://notion.so/test-page-abcdef"


def _mock_notion(url: str = _NOTION_URL) -> MagicMock:
    m = MagicMock()
    m.pages.create.return_value = {"url": url}
    return m


def test_create_journal_page_returns_url():
    with patch("journal.Client", return_value=_mock_notion()):
        url = create_journal_page(_TITLE)
    assert url == _NOTION_URL


def test_create_journal_page_sets_title():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    kwargs = mock.pages.create.call_args[1]
    assert kwargs["properties"]["title"][0]["text"]["content"] == _TITLE


def test_create_journal_page_has_todo_blocks():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    children = mock.pages.create.call_args[1]["children"]
    todo_blocks = [b for b in children if b["type"] == "to_do"]
    assert len(todo_blocks) == 6
    assert all(not b["to_do"]["checked"] for b in todo_blocks)


def test_create_journal_page_has_sections():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    children = mock.pages.create.call_args[1]["children"]
    headings = [
        b["heading_2"]["rich_text"][0]["text"]["content"]
        for b in children if b["type"] == "heading_2"
    ]
    assert "やること" in headings
    assert "やれたこと" in headings
    assert "メモ" in headings


def test_create_journal_page_sets_parent_id():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    kwargs = mock.pages.create.call_args[1]
    assert kwargs["parent"]["page_id"] == "test_parent_id"
