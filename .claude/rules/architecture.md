---
paths: src/**/*.py
---

# アーキテクチャと設計制約

## モジュール構成

| モジュール | 役割 |
|-----------|------|
| `reminkun/main.py` | 朝通知エントリーポイント（weather/gcalendar/news/journal/notifier を呼び出す） |
| `reminkun/main_evening.py` | 夜通知エントリーポイント（21:00 JST） |
| `reminkun/weather.py` | wttr.in API（`?format=j1`、APIキー不要） |
| `reminkun/gcalendar.py` | Google Calendar API（OAuth2 refresh token 認証） |
| `reminkun/news.py` | feedparser で日本語RSS取得（政治・経済・国際・AI・セキュリティ・Zenn、各カテゴリ3件） |
| `reminkun/journal.py` | Notion API で日次ジャーナルページ作成 |
| `reminkun/notifier.py` | Discord Webhook 送信（eventkun も共用。`webhook_url` 引数で切り替え可） |
| `eventkun/eventkun_main.py` | イベント通知エントリーポイント（embed を組み立てて送信） |
| `eventkun/events.py` | Connpass API で愛知県の直近イベント取得 |

## 環境変数

| 変数名 | 未設定時の挙動 |
|--------|--------------|
| `DISCORD_WEBHOOK_URL` | エラー（必須） |
| `DISCORD_WEBHOOK_URL_EVENTS` | `DISCORD_WEBHOOK_URL` にフォールバック |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` | カレンダー欄が「取得できませんでした」 |
| `NOTION_API_KEY` / `NOTION_PARENT_PAGE_ID` | ジャーナル欄をスキップ |

## 設計制約（必ず守る）

- 認証情報をコードにハードコードしない（必ず環境変数から読む）
- Google Calendar認証は非対話型のみ（refresh token 方式。InstalledAppFlow は scripts/get_token.py 専用）
- 既存のモジュール構成（weather/gcalendar/news/journal/notifier）を理由なく変えない
- 新しい外部APIを勝手に追加しない
- 各機能は `try/except Exception` でラップし、一部失敗しても通知全体が止まらないようにする
- ニュースRSSは取得できない場合のフォールバックを設けること
- GitHub Actions の cron はUTC基準（JST 6:00 = UTC 21:00、JST 21:00 = UTC 12:00）
