#!/bin/bash
# セッション開始時に git 状態と教訓をコンテキストに注入する

# ── 毎セッション実行: リモート同期 & ブランチ自動クリーンアップ ──────────
git fetch --prune -q 2>/dev/null
CURRENT=$(git branch --show-current 2>/dev/null)
if [ "$CURRENT" = "main" ]; then
  git pull -q 2>/dev/null
elif [ -n "$CURRENT" ]; then
  git fetch origin main:main -q 2>/dev/null
fi

GONE=$(git branch -vv 2>/dev/null | grep ': gone]' | awk '{print $1}')
if [ -n "$GONE" ]; then
  echo "### ブランチ自動クリーンアップ"
  echo "$GONE" | xargs git branch -d 2>/dev/null
  echo "削除しました: $GONE"
  echo ""
fi

# ── 1日1回のみ: 詳細な状態表示 ────────────────────────────────────────────
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

echo "### 過去の教訓（docs/lessons.md）"
cat docs/lessons.md 2>/dev/null || echo "(まだ教訓はありません)"
