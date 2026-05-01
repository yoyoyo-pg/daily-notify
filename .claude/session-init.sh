#!/bin/bash
# セッション開始時に1度だけ git 状態と教訓をコンテキストに注入する
MARKER="${TEMP:-/tmp}/daily_notify_session_$(date +%Y%m%d)"

[ -f "$MARKER" ] && exit 0
touch "$MARKER"

echo "=== セッション開始チェック（自動実行）==="
echo ""
echo "### 現在のブランチ"
git branch --show-current 2>/dev/null
echo ""
echo "### 最近のコミット"
git log --oneline -5 2>/dev/null
echo ""
echo "### PR一覧（直近10件）"
gh pr list --state all --limit 10 2>/dev/null
echo ""
echo "### リモートと同期"
git fetch --prune -q 2>/dev/null
CURRENT=$(git branch --show-current 2>/dev/null)
if [ "$CURRENT" = "main" ]; then
  git pull -q 2>/dev/null && echo "main を pull しました"
else
  git fetch origin main:main -q 2>/dev/null && echo "ローカル main を更新しました（現在: $CURRENT）"
fi
echo ""
echo "### マージ済みローカルブランチのクリーンアップ"
GONE=$(git branch -vv 2>/dev/null | grep ': gone]' | awk '{print $1}')
if [ -n "$GONE" ]; then
  echo "$GONE" | xargs git branch -d 2>/dev/null && echo "削除しました: $GONE"
else
  echo "削除対象なし"
fi
echo ""
echo "### 過去の教訓（docs/lessons.md）"
cat docs/lessons.md 2>/dev/null
