# Lessons Learned

実装を通じて得た教訓。次の作業前に確認し、作業後に追記する。
**何をしたか** ではなく **なぜそうしたか・次回どうすべきか** を書く。

---

## 2026-04-30 ボット名変更・テスト自動化・ドキュメント整合性

### テスト失敗の早期検知

- `.claude/settings.json` の PostToolUse hook で `.py` 編集直後に `pytest` を自動実行するようにした
- 「PR前に気づく」ではなく「編集直後に気づく」が理想。hook はその最速の手段
- ローカル環境の `cryptography` パッケージ破損で `test_calendar.py` がコレクション時にクラッシュするため `--ignore=tests/test_calendar.py` を付けた。CI では全テストが走るので問題ない

### ブランチ切り替え時に settings.json が戻る

- `.claude/settings.json` は git 管理下にあるため、ブランチ切り替えで内容が変わる
- hook を追加したブランチが main にマージされる前に別ブランチに切り替えると hook が消える。マージ後は全ブランチで使える

### ボット名変更はコードとテストとドキュメントの3点セット

- embed のタイトル・説明文を変えたら、それをアサートしているテストも必ず同時に変える
- README・CLAUDE.md・docs/ の記述が「以前の名前のまま」になりやすい。grep で一括確認してから commit する

### コンフリクトの原因は「同じファイルを異なるブランチで編集したこと」

- PR #34（docs 修正）と PR #35（ショーンK化）が `tests/test_evening.py` を両方変更していたためコンフリクト発生
- rebase 後は force push が必要。`settings.json` の deny リストに `git push --force*` があると弾かれるので、リベース作業前にユーザーに確認を取る


- `settings.local.json` はコミット非推奨の仕様。プロジェクト共通の permissions は `settings.json` に書く
- `gh pr list` はデフォルトでオープンPRのみ。`--state all` を付けないとマージ済みブランチに気づけない
- マージ済みブランチへの追加コミットはPRに反映されない。作業前に `gh pr view` で状態確認が必須
- 「新ファイル作成 + 複数ファイル変更」はマルチエージェントで進める基準に該当する
- 実装後は README.md・CLAUDE.md のリポジトリ構成・説明を必ずセットで更新する

---

## 2026-05-01 ディレクトリ構成見直し・厚切りジェイソン別チャンネル対応・動作確認

### ディレクトリ構成の見直しは PYTHONPATH への影響を必ず確認する

- `src/` 直下にあったファイルを `src/reminkun/` に移動し、`eventkun/` を `src/eventkun/` に移動した
- モジュールが別ディレクトリをまたぐ場合（eventkun が reminkun の `notifier.py` を使う等）、PYTHONPATH に複数パスを通す必要がある
- GitHub Actions の workflow と `pytest.ini` の `pythonpath` 設定も一緒に更新しないと CI が壊れる。移動後は必ず両方確認する

### ローカルでの eventkun 実行には PYTHONPATH の手動設定が必要

- `python src/eventkun/main.py` をそのまま実行すると `notifier` が見つからずエラーになる
- `PYTHONPATH="...src/reminkun;...src/eventkun" python src/eventkun/main.py` のように絶対パスで設定する必要がある（Windows では `;` 区切り）
- GitHub Actions 側は `PYTHONPATH: src/reminkun` が設定済みなので本番は問題ない。ローカルでの動作確認時に忘れやすいので注意

### 別 Webhook URL へのフォールバックパターン

- 厚切りジェイソン専用の `DISCORD_WEBHOOK_URL_EVENTS` が未設定の場合は `DISCORD_WEBHOOK_URL` にフォールバックする設計にした
- `notifier.send()` に `webhook_url` 引数を追加し、呼び出し側（eventkun/main.py）で解決することで notifier 側をシンプルに保てた
- 新しい Webhook URL 変数を追加したときは `.env.example`・`CLAUDE.md` の環境変数テーブル・workflow の `env:` ブロックの3点セットを必ず更新する
