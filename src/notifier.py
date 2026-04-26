import os

import requests


def send(embeds: list[dict], content: str = "") -> None:
    url = os.environ["DISCORD_WEBHOOK_URL"]
    payload: dict = {"embeds": embeds}
    if content:
        payload["content"] = content
    requests.post(url, json=payload, timeout=10).raise_for_status()
