---
name: pr-ready
description: |
  PR 作成前チェックリストを自動実行する。
  トリガー: "PR作成前チェック", "PRの準備", "/pr-ready"
  使用場面: 実装が完了し PR を作成する直前
---

# pr-ready

workflow.md のチェックリストを順番に実行し、PR 作成可否を判定する。

## 実行手順

1. **rebase 確認**
   ```bash
   git fetch origin main
   git log --oneline origin/main..HEAD
   ```
   main との差分を確認し、必要なら rebase を促す。

2. **テスト実行**
   ```bash
   python -m pytest tests/ --ignore=tests/test_calendar.py -q --tb=short
   ```
   失敗があれば PR 作成を止めて修正を促す。

3. **変更ファイル確認**
   ```bash
   git diff origin/main..HEAD --name-only
   ```
   ロジック変更があるファイルに対応するテストが存在するか確認する。

4. **ドキュメント整合性チェック**
   変更内容に応じて以下を確認する:
   - CLAUDE.md のディレクトリ構造・コマンド表が実装と一致しているか
   - README.md の説明が実装と一致しているか
   - AGENTS.md のリポジトリ構成が実装と一致しているか

5. **環境変数チェック**
   新しい環境変数を追加した場合、.env.example と docs/architecture.md の環境変数テーブルを更新したか確認する。

6. **結果報告**
   すべて OK なら「PR 作成準備完了」と報告し、問題があれば箇条書きで列挙する。
