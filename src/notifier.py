import os

import requests


def send(embeds: list[dict]) -> None:
    url = os.environ["DISCORD_WEBHOOK_URL"]
    requests.post(url, json={"embeds": embeds, "flags": 4}, timeout=10).raise_for_status()
