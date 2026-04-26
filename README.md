# morning-notify

毎朝7時に天気・Googleカレンダー・ニュースをまとめてDiscordに通知するPythonアプリ。

## 通知イメージ

```
☀️ おはようございます！4/26(日)

🌤 今日の天気: 名古屋 晴れ 22°C
　　降水確率: 10%

📅 今日の予定
　・10:00 チームミーティング
　・14:00 1on1

📰 今日のニュース
　【政治】〇〇〇〇
　【経済】〇〇〇〇
　【技術】〇〇〇〇
　【AI】　〇〇〇〇
```

## セットアップ

### 1. Python 3.11+ のインストール

**Windows**

[python.org](https://www.python.org/downloads/) からインストーラーをダウンロードして実行する。
インストール時に「Add Python to PATH」にチェックを入れること。

**Mac**

```bash
brew install python@3.11
```

**インストール確認**

```bash
python --version   # 3.11 以上であること
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example` を `.env` にコピーして値を入力する。

```bash
cp .env.example .env
```

### 4. Discord Webhook URL の取得

1. 通知を送りたい Discord サーバーのチャンネルを開く
2. チャンネル名を右クリック →「チャンネルの編集」
3. 「連携サービス」タブ →「ウェブフックを作成」
4. 名前を設定して「ウェブフックURLをコピー」
5. コピーしたURLを `.env` の `DISCORD_WEBHOOK_URL` に設定する

### 5. Google Calendar 認証

初回のみ対話的OAuthフローでリフレッシュトークンを取得する。

```bash
python scripts/get_token.py
```

取得した `refresh_token` を `.env` の `GOOGLE_REFRESH_TOKEN` に設定する。

### 6. ローカル実行

```bash
python src/main.py
```

## GitHub Actions でのデプロイ

以下のSecretsをリポジトリに設定する。

| Secret名 | 内容 |
|----------|------|
| `GOOGLE_CLIENT_ID` | Google Cloud Console で発行 |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console で発行 |
| `GOOGLE_REFRESH_TOKEN` | `scripts/get_token.py` で取得 |
| `DISCORD_WEBHOOK_URL` | Discord チャンネルの設定から発行 |

設定後は毎朝7時(JST)に自動実行される（GitHub Actions cron: `0 22 * * *` UTC）。

## AI コーディングツールのセットアップ

このリポジトリは Claude Code と Codex CLI での作業を想定している。Node.js 18+ が前提。

### Claude Code

Anthropic が提供するターミナル向け AI コーディングアシスタント。

```bash
npm install -g @anthropic-ai/claude-code
```

初回起動時に Claude.ai アカウント（無料）またはAPIキーでログインする。

```bash
claude   # プロジェクトディレクトリで起動
```

### Codex CLI

OpenAI が提供するターミナル向け AI エージェント。

```bash
npm install -g @openai/codex
```

初回起動時に OpenAI アカウントでログインする。ChatGPT Plus/Pro またはAPIクレジットが必要。

```bash
codex   # インタラクティブモードで起動
```

非インタラクティブなレビューやタスク実行には `codex exec` を使う。

```bash
codex exec --full-auto --sandbox read-only --cd . "このコードをレビューしてください"
```

## 今後の展望

### 近期（実装準備済み）

- **Google カレンダー連携**
  - `src/gcalendar.py` にスタブあり（OAuth2 refresh token 方式）
  - 当日の予定一覧をDiscord通知に追加する
  - `scripts/get_token.py` でリフレッシュトークンを取得できる

### 中期

- **Notion TODO 連携**
  - Notion API でデータベースからその日のTODOを取得
  - 「今日やること」をDiscord通知に追加する
  - タスクの完了状態も反映できると理想

- **朝のジャーナル管理**
  - 毎朝の通知をトリガーに、Notion へ日報ページを自動生成
  - 天気・予定・ニュースをジャーナルのテンプレートとして埋め込む
  - 夜の振り返り通知（Discord）も合わせて追加する

### 長期

- **通知のパーソナライズ**
  - ニュースカテゴリや件数を設定ファイルで変更できるようにする
  - 曜日や天気に応じて通知内容を変える（雨の日は傘リマインダーなど）

- **複数チャンネル対応**
  - Discord 以外に Slack や LINE Notify への送信にも対応する
