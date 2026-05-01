import os
from unittest.mock import patch, Mock

import pytest

os.environ.setdefault("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test/token")

from notifier import send

_WEBHOOK_URL = "https://discord.com/api/webhooks/test/token"
_EMBEDS = [{"title": "テスト", "color": 0x5DADE2}]


def test_send_posts_embeds_only():
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        send(_EMBEDS)

    mock_post.assert_called_once_with(
        _WEBHOOK_URL,
        json={"embeds": _EMBEDS},
        timeout=10,
    )


def test_send_posts_content_with_embeds():
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        send(_EMBEDS, content="おはようございます！")

    mock_post.assert_called_once_with(
        _WEBHOOK_URL,
        json={"embeds": _EMBEDS, "content": "おはようございます！"},
        timeout=10,
    )


def test_send_calls_raise_for_status():
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp):
        send(_EMBEDS)

    mock_resp.raise_for_status.assert_called_once()


def test_send_raises_on_http_error():
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = Exception("403 Forbidden")

    with patch("notifier.requests.post", return_value=mock_resp):
        with pytest.raises(Exception, match="403"):
            send(_EMBEDS)


def test_send_uses_explicit_webhook_url():
    custom_url = "https://discord.com/api/webhooks/custom/token"
    mock_resp = Mock()

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        send(_EMBEDS, webhook_url=custom_url)

    mock_post.assert_called_once_with(
        custom_url,
        json={"embeds": _EMBEDS},
        timeout=10,
    )
