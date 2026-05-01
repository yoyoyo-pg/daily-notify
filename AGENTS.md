# AGENTS.md

## プロジェクト概要

毎朝6時(JST)に天気・Googleカレンダー・ニュースをDiscordへ通知し、毎晩21時(JST)に振り返りリマインダーを送るPythonスクリプト。GitHub Actionsで定期実行する。

## リポジトリ構成

```
daily-notify/
├── .github/workflows/
│   ├── morning-notify.yml  # 朝通知（毎朝6時 JST = UTC 21:00）
│   ├── evening-notify.yml  # 夜通知（毎晩21時 JST = UTC 12:00）
│   ├── events-notify.yml   # イベント通知（月・木 6時 JST）
│   └── test.yml            # PRテスト（pytest）
├── src/
│   ├── reminkun/           # ショーンK（朝・夜通知）
│   │   ├── main.py
│   │   ├── main_evening.py
│   │   ├── weather.py
│   │   ├── gcalendar.py
│   │   ├── news.py
│   │   ├── journal.py
│   │   └── notifier.py
│   └── eventkun/           # 厚切りジェイソン（イベント通知）
│       ├── eventkun_main.py
│       └── events.py
├── tests/
├── docs/
├── scripts/
│   └── get_token.py        # Google OAuth token 取得ユーティリティ
├── pytest.ini
├── requirements.txt
└── .env.example
```

## 技術スタック

- **言語**: Python 3.11+
- **天気**: wttr.in JSON API（APIキー不要）
- **カレンダー**: google-api-python-client（OAuth2 refresh token 認証）
- **ニュース**: feedparser + 日本語RSSフィード
- **通知**: Discord Webhook（requests）
- **ジャーナル**: Notion API（notion-client）
- **CI/CD**: GitHub Actions

## コマンド

```bash
pip install -r requirements.txt
python src/reminkun/main.py
pytest tests/
```

## 制約

- 認証情報をコードにハードコードしない（必ず環境変数から読む）
- 既存のモジュール構成を理由なく変えない
- 新しい外部APIを勝手に追加しない
- Google Calendar認証は非対話型のみ（refresh token方式）
- テストは外部APIをモックして書く（実APIは叩かない）
