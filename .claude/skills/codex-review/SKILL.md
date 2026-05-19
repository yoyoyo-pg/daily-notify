---
name: codex-review
description: |
  現在のブランチの差分を Codex にレビューさせる。
  トリガー: "codexにレビューさせて", "codexでレビュー", "/codex-review"
  使用場面: 実装完了後、PR作成前にCodexの視点でコードレビューを受けたいとき
---

# codex-review

現在のブランチ（origin/main との差分）を Codex にレビューさせる。

## 実行手順

1. **変更ファイル一覧を取得**
   ```bash
   git diff origin/main..HEAD --name-only
   git diff origin/main..HEAD --stat
   ```

2. **Codex にレビューを依頼**

   以下のプロンプトで `codex exec` を実行する。`<変更ファイル一覧>` には前のステップで取得したファイル名を埋め込む。

   ```bash
   codex exec --full-auto --sandbox read-only --cd <プロジェクトのフルパス> "$(cat <<'EOF'
   以下のファイルが origin/main から変更されています。
   <変更ファイル一覧>

   git diff origin/main で差分を確認し、以下の観点でレビューしてください：
   1. バグや論理的な誤り
   2. 意図しない副作用・見落とし
   3. 改善できる点

   問題なければ「LGTM」と一言だけ返してください。回答は要点を箇条書きで簡潔にまとめてください。確認や質問は不要です。具体的な指摘まで自主的に出力してください。
   EOF
   )"
   ```

3. **結果をユーザーに報告**
   - Codex の出力をそのまま伝える
   - 問題が指摘された場合は修正を促す
   - LGTM なら PR 作成に進む
