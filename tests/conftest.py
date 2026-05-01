import os
from unittest.mock import patch, Mock

import pytest

os.environ.setdefault("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test/token")
os.environ.setdefault("DISCORD_WEBHOOK_URL_EVENTS", "https://discord.com/api/webhooks/test/events-token")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test_token")


@pytest.fixture(autouse=True)
def block_discord():
    """全テストでDiscord Webhookへの実HTTPリクエストをブロックする。"""
    with patch("notifier.requests.post", return_value=Mock()):
        yield
