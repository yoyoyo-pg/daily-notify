import os

import requests


def send(embeds: list[dict], content: str = "", webhook_url: str | None = None) -> None:
    url = webhook_url if webhook_url is not None else os.environ["DISCORD_WEBHOOK_URL"]
    payload: dict = {"embeds": embeds}
    if content:
        payload["content"] = content
    requests.post(url, json=payload, timeout=10).raise_for_status()
