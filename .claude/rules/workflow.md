# 開発ワークフロー

## ブランチ・PR

- 作業は必ず新規ブランチ（`claude/<作業内容>`）を切って行う（main への直接コミット禁止）
- PR を作成すると `test.yml` が自動で走り pytest が実行される
- GitHub MCP ツール（`mcp__github__*`）を使う（`gh` CLI は使用不可）
- 既存ブランチで作業を続ける前に PR の状態を確認する（マージ済みなら新ブランチを切る）

## コンフリクト防止ルール

ブランチが長生きすると main との乖離が大きくなりコンフリクトが起きやすい。以下を必ず守る。

1. **PR 作成直前に必ず rebase する**
   ```bash
   git fetch origin main
   git rebase origin/main
   # push --force-with-lease はユーザーに確認を取ってから実行する
   # （settings.json の deny リストに git push --force* があるため）
   ```
2. **1ブランチ = 1タスク**。複数機能を同じブランチに詰め込まない。
3. **ブランチ寿命は原則 1 セッション以内**。跨ぐ場合は冒頭で `git fetch origin main && git log --oneline origin/main..HEAD` でズレを確認する。
4. **docs 系ファイル（README.md・CLAUDE.md・AGENTS.md・ideas.md）は特に競合しやすい**。実装ブランチでは必要最小限の docs 更新に留め、main への追従を早める。

## PR作成前チェックリスト

```
[ ] git fetch origin main && git rebase origin/main 済み（コンフリクト防止）
[ ] pytest tests/ がすべて通る
[ ] ロジックを変えた場合、対応するテストも同時に更新した
[ ] CLAUDE.md のディレクトリ構造が実装と合っている
[ ] README.md の説明が実装と合っている
[ ] AGENTS.md のリポジトリ構成が実装と合っている
[ ] ボット追加・変更の場合、docs/ideas.md の稼働中メンバー表と実装優先度表を更新した
[ ] 環境変数を追加・変更した場合、.env.example と architecture.md の環境変数テーブルも更新した
```

## マルチエージェント方針

新しいファイル作成・複数ファイルにまたがる実装では役割を分けて進める。

| 役割 | subagent_type | 担当 |
|------|---------------|------|
| 調査役 | Explore | コードベース読み取り・外部情報収集のみ。コードは書かない |
| 実装役 | general-purpose + `isolation: worktree` | 調査結果を受けて実装・テスト作成 |
| レビュー役 | Explore | テスト漏れ・制約違反・セキュリティの検証。修正はしない |
| 整理役 | general-purpose | PR作成・ドキュメント更新 |

**使う条件**（いずれかに該当）: 新ファイル作成、複数ファイル変更、外部情報の調査が必要

**使わない条件**（すべて該当）: 既存ファイル1〜2件の軽微な修正 かつ ロジック変更なし
