# CLAUDE.md

## プロジェクト概要

毎朝7時(JST)に天気・Googleカレンダー・ニュースをDiscordへ通知するPythonスクリプト。GitHub Actionsで定期実行する。

## リポジトリ構成

```
morning-notify/
├── .github/workflows/morning-notify.yml   # スケジュール実行定義
├── src/
│   ├── main.py          # エントリーポイント。各モジュールを呼び出して通知を組み立てる
│   ├── weather.py       # wttr.in APIで名古屋の天気を取得
│   ├── calendar.py      # Google Calendar APIで当日の予定を取得
│   ├── news.py          # RSSフィードから日本語ニュースを取得
│   └── notifier.py      # Discordへ通知を送信
├── tests/
├── requirements.txt
└── .env.example
```

## アーキテクチャ

```
GitHub Actions (cron: 0 21 * * * UTC = 毎朝6時 JST)
└── src/main.py
    ├── weather.py     → wttr.in JSON API で名古屋の天気取得（APIキー不要）
    ├── calendar.py    → Google Calendar API（OAuth2 refresh token 認証）
    ├── news.py        → feedparser で日本語RSSを取得（政治・経済・技術・AI・セキュリティ 各2件）
    └── notifier.py    → Discord Webhook で通知送信
```

## コマンド

```bash
pip install -r requirements.txt        # 依存インストール
python src/main.py                     # ローカル実行（.envに環境変数を設定した上で）
pytest tests/                          # テスト実行
pytest tests/test_weather.py           # 単一テスト実行
```

## 環境変数

ローカルでは `.env`、GitHub Actions では Secrets で管理する。

| 変数名 | 用途 |
|--------|------|
| `GOOGLE_CLIENT_ID` | Google OAuth クライアントID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth クライアントシークレット |
| `GOOGLE_REFRESH_TOKEN` | Google Calendar アクセス用リフレッシュトークン |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |

## 開発ルール

- 作業は必ず新規ブランチを切って行う（masterへの直接コミットは禁止）
- ブランチ名は `claude/<作業内容>` の形式にする
- 実装が完了したらmasterへのプルリクエストを作成する

## 制約

**やってはいけないこと**
- 認証情報をコードにハードコードしない（必ず環境変数から読む）
- 既存のモジュール構成（weather / calendar / news / notifier）を理由なく変えない
- 新しい外部APIを勝手に追加しない
- Google Calendar認証に対話的OAuthフローを使わない（非対話型のrefresh token方式のみ）

**テスト方針**
- 外部API（wttr.in、Google Calendar、Discord Webhook）はモックを使う
- 実APIを叩くテストは書かない

## 設計上の注意

- wttr.in は `?format=j1` のJSON形式で取得する（`lang=ja` オプションで日本語）
- GitHub Actions の cron はUTCで指定するため `0 22 * * *`（JST 7:00 = UTC 22:00 前日）
- ニュースRSSは取得できない場合のフォールバックを設けること
