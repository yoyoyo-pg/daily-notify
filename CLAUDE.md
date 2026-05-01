# daily-notify

毎朝6時(JST)に天気・カレンダー・ニュースをDiscordへ通知し、毎晩21時(JST)に振り返りリマインダーを送るPythonスクリプト。GitHub Actionsで定期実行する。

## 技術スタック
- Python 3.11
- Discord Webhook（requests）、Google Calendar API（OAuth2 refresh token）、Notion API、wttr.in JSON API、Connpass API

## コマンド
| コマンド | 用途 |
|---------|------|
| `pip install -r requirements.txt` | 依存インストール |
| `python src/reminkun/main.py` | 朝通知ローカル実行 |
| `python src/eventkun/eventkun_main.py` | イベント通知ローカル実行 |
| `pytest tests/` | テスト実行 |

## ディレクトリ構造
| パス | 役割 |
|-----|------|
| `src/reminkun/` | ショーンK（朝・夜通知） |
| `src/eventkun/` | 厚切りジェイソン（イベント通知） |
| `tests/` | pytest テスト（pytest.ini で src/ 以下が PATH に追加済み） |
| `.github/workflows/` | GitHub Actions（morning/evening/events/test） |
| `.claude/rules/` | 詳細ルール（コンテキスト注入） |
| `docs/` | 教訓・アイデア |
| `scripts/` | ユーティリティ（get_token.py: OAuth token 取得） |

## 行動原則
- 3ステップ以上のタスクは必ずPlanモードで開始する
- 動作を証明できるまでタスクを完了とマークしない（pytest 実行を省略しない）
- コードを読まずに書かない。必ず既存コードを確認してから変更する
- 作業は必ず新規ブランチで行う（main への直接コミット禁止、ブランチ名: `claude/<作業内容>`）
- 実装完了後は README.md と CLAUDE.md を必ず更新する
- コンテキストが逼迫したら正直に伝え、セッション分割を提案する
