---
paths: tests/**/*.py
---

# テスト方針

- 外部API（wttr.in、Google Calendar、Discord Webhook、Connpass）はモックを使う
- 実APIを叩くテストは書かない
- conftest.py で環境変数のデフォルト値をセットし、Discord Webhook への実リクエストをブロックしている
- ロジックを変更したときは、対応するテストも必ず同時に更新する（テストが古い仕様のままになるのを防ぐ）
- ローカルでは `pytest tests/ --ignore=tests/test_calendar.py` を使う（cryptography パッケージ破損対策）
- CI（test.yml）では `pytest tests/` で全テストが走るため、CI で全テストが通ることを確認する
