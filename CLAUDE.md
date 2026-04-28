# CLAUDE.md

## プロジェクト概要

毎朝6時(JST)に天気・Googleカレンダー・ニュースをDiscordへ通知するPythonスクリプト。GitHub Actionsで定期実行する。

## リポジトリ構成

```
morning-notify/
├── .github/workflows/
│   ├── morning-notify.yml  # スケジュール実行定義（毎朝6時 JST）
│   └── test.yml            # PRテスト（pytest + Discord通知テスト）
├── src/
│   ├── main.py             # エントリーポイント。各モジュールを呼び出して通知を組み立てる
│   ├── weather.py          # wttr.in APIで名古屋の天気を取得
│   ├── gcalendar.py        # Google Calendar APIで当日の予定を取得（要: GOOGLE_* 環境変数）
│   ├── news.py             # RSSフィードから日本語ニュースを取得（政治・経済・国際・AI・セキュリティ・Zenn）
│   ├── journal.py          # Notion APIで日次ジャーナルページを作成（要: NOTION_* 環境変数）
│   └── notifier.py         # Discord Webhookへ通知を送信
├── tests/
│   ├── conftest.py         # テスト共通設定（env stub、Discord Webhookブロック）
│   ├── test_weather.py
│   ├── test_news.py
│   ├── test_notifier.py
│   ├── test_calendar.py
│   └── test_journal.py
├── docs/
│   ├── ideas.md            # 開発アイデアメモ
│   └── ai-coding-experience.md  # AIコーディング体験記
├── pytest.ini              # pythonpath = src を設定済み
├── requirements.txt
└── .env.example
```

## アーキテクチャ

```
GitHub Actions (cron: 0 21 * * * UTC = 毎朝6時 JST)
└── src/main.py
    ├── weather.py     → wttr.in JSON API で名古屋の天気取得（APIキー不要）
    ├── gcalendar.py   → Google Calendar API（OAuth2 refresh token 認証）
    ├── news.py        → feedparser で日本語RSSを取得（各カテゴリ1件）
    ├── journal.py     → Notion API で日次ジャーナルページを作成（未設定時はスキップ）
    └── notifier.py    → Discord Webhook で通知送信
```

## コマンド

```bash
pip install -r requirements.txt        # 依存インストール
python src/main.py                     # ローカル実行（.envに環境変数を設定した上で）
pytest tests/                          # テスト実行（pytest.ini により src/ がパスに追加される）
pytest tests/test_weather.py           # 単一テスト実行
```

## 環境変数

ローカルでは `.env`、GitHub Actions では Secrets で管理する。

| 変数名 | 用途 | 未設定時の挙動 |
|--------|------|--------------|
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | エラー（必須） |
| `GOOGLE_CLIENT_ID` | Google OAuth クライアントID | カレンダー欄が「取得できませんでした」 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth クライアントシークレット | 同上 |
| `GOOGLE_REFRESH_TOKEN` | Google Calendar アクセス用リフレッシュトークン | 同上 |
| `NOTION_API_KEY` | Notion インテグレーショントークン | ジャーナル欄をスキップ |
| `NOTION_PARENT_PAGE_ID` | ジャーナルページを作成する親ページのID | 同上 |

## 開発ルール

- 作業は必ず新規ブランチを切って行う（mainへの直接コミットは禁止）
- ブランチ名は `claude/<作業内容>` の形式にする
- 実装が完了したらmainへのプルリクエストを作成する
- PRを作成すると `test.yml` が自動で走り、テスト通過 + Discord通知テストが行われる

## 制約

**やってはいけないこと**
- 認証情報をコードにハードコードしない（必ず環境変数から読む）
- 既存のモジュール構成（weather / gcalendar / news / journal / notifier）を理由なく変えない
- 新しい外部APIを勝手に追加しない
- Google Calendar認証に対話的OAuthフローを使わない（非対話型のrefresh token方式のみ）

**テスト方針**
- 外部API（wttr.in、Google Calendar、Discord Webhook）はモックを使う
- 実APIを叩くテストは書かない
- conftest.py で環境変数のデフォルト値をセットし、Discord Webhookへの実リクエストをブロックしている

## 設計上の注意

- wttr.in は `?format=j1` のJSON形式で取得する（`lang=ja` オプションで日本語）
- GitHub Actions の cron はUTCで指定するため `0 21 * * *`（JST 6:00 = UTC 21:00 前日）
- ニュースRSSは取得できない場合のフォールバックを設けること
- 各機能は `try/except Exception` でラップし、一部失敗しても通知全体が止まらないようにする
