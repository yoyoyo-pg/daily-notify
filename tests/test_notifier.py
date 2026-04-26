import os
from unittest.mock import patch, Mock

import pytest

os.environ.setdefault("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test/token")

from notifier import send

_WEBHOOK_URL = "https://discord.com/api/webhooks/test/token"


def test_send_posts_correct_payload():
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        send("テストメッセージ")

    mock_post.assert_called_once_with(
        _WEBHOOK_URL,
        json={"content": "テストメッセージ", "flags": 4},
        timeout=10,
    )


def test_send_calls_raise_for_status():
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp):
        send("メッセージ")

    mock_resp.raise_for_status.assert_called_once()


def test_send_raises_on_http_error():
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = Exception("403 Forbidden")

    with patch("notifier.requests.post", return_value=mock_resp):
        with pytest.raises(Exception, match="403"):
            send("メッセージ")
