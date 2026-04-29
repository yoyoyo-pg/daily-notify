import os

from notion_client import Client


def _heading_2(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _to_do() -> dict:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": [], "checked": False},
    }


def _paragraph() -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def create_journal_page(title: str) -> str:
    """Notionに日次ジャーナルページを作成してURLを返す。"""
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    parent_id = os.environ["NOTION_PARENT_PAGE_ID"]

    response = notion.pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": [{"type": "text", "text": {"content": title}}],
        },
        children=[
            _heading_2("やること"),
            _to_do(),
            _to_do(),
            _to_do(),
            {"object": "block", "type": "divider", "divider": {}},
            _heading_2("やれたこと"),
            _to_do(),
            _to_do(),
            _to_do(),
            {"object": "block", "type": "divider", "divider": {}},
            _heading_2("メモ"),
            _paragraph(),
        ],
    )

    return response["url"]
