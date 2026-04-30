from main_evening import build_embed


def test_build_embed_content_has_date():
    content, _ = build_embed()
    assert "リフレクション" in content
    assert "/" in content  # 日付が含まれる


def test_build_embed_has_required_fields():
    _, embed = build_embed()
    assert embed["title"] == "📓 デイリー・リフレクション"
    assert embed["description"] == "本日のアクション・アイテムとアチーブメントをレコーディングしましょう。"
    assert "color" in embed
