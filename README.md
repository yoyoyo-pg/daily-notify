# morning-notify

毎朝6時に天気・Googleカレンダー・ニュースをまとめてDiscordに通知するPythonアプリ。

## 通知イメージ

Discord の Embed（カード形式）で3枚のカードを送信する。

| カード | 色 | 内容 |
|--------|-----|------|
| 🌤 天気 | 青 | 天気概況・気温・降水確率。タイトルクリックで wttr.in へ |
| 📅 カレンダー | 緑 | 当日の予定一覧（予定なしの場合はその旨表示） |
| 📰 ニュース | オレンジ | カテゴリごとに記事タイトル（リンク付き）をフィールド表示 |
| 📓 ジャーナル | 紫 | Notionの当日ジャーナルページへのリンク（Notion連携時のみ表示） |

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

#### 5-1. Google Cloud Console でプロジェクトとOAuth認証情報を作成する

1. [Google Cloud Console](https://console.cloud.google.com/) を開き、新規プロジェクトを作成（または既存を選択）する
2. 「APIとサービス」→「ライブラリ」で **Google Calendar API** を有効化する
3. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuth クライアント ID」を選択する
4. アプリケーションの種類を「**デスクトップアプリ**」にして作成する
5. 発行された **クライアントID** と **クライアントシークレット** を控えておく

#### 5-2. OAuth 同意画面にテストユーザーを追加する

アプリが Google の審査を通過していない場合、テストユーザーとして登録されたアカウントのみ認証を通過できる。

1. 「APIとサービス」→「OAuth 同意画面」を開く
2. 「テストユーザー」セクションの「＋ユーザーを追加」をクリックする
3. 自分の Google アカウントのメールアドレスを追加して保存する

> この設定をしないと「アクセスをブロック: morning notify は Google の審査プロセスを完了していません」というエラーが表示される。

#### 5-3. リフレッシュトークンを取得する

```bash
python scripts/get_token.py
```

実行するとクライアントID・シークレットの入力を求められ、ブラウザが開いて Google アカウントへのアクセス許可を求める。

「このアプリは Google で確認されていません」という警告が出た場合は「詳細」→「（アプリ名）に移動」をクリックして続行する。

認証が完了するとターミナルに以下のように表示される。

```
GOOGLE_REFRESH_TOKEN=1//0xxxxxxxxxxxxxxxx...
```

この値を `.env` の `GOOGLE_REFRESH_TOKEN` に設定する。

### 6. Notion 連携（任意）

ジャーナル機能を使う場合のみ設定する。設定しない場合は他の通知は通常どおり動作する。

#### 6-1. Notion インテグレーションを作成する

1. [Notion Integrations](https://www.notion.so/my-integrations) を開き「新しいインテグレーション」を作成する
2. 名前を設定し（例: `morning-notify`）、対象ワークスペースを選択して「送信」
3. 表示された **インターナルインテグレーションシークレット**（`secret_...` で始まる文字列）を控える
4. これを `.env` の `NOTION_API_KEY` に設定する

#### 6-2. 親ページを作成してインテグレーションを接続する

1. Notion でジャーナルを置きたい親ページを開く（例: 「Morning Journal」というページ）
2. ページ右上の「…」メニュー →「接続」→ 作成したインテグレーションを選択する
3. ページのURLから ID を取得する（`notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` の32文字部分）
4. これを `.env` の `NOTION_PARENT_PAGE_ID` に設定する

毎朝の通知時に `ジャーナル YYYY/MM/DD(曜)` というページがこの親ページ配下に自動生成され、「やること」チェックリスト3枠と「メモ」欄が用意される。

### 7. ローカル実行

```bash
python src/main.py
```

## GitHub Actions でのデプロイ

以下のSecretsをリポジトリに設定する。

| Secret名 | 内容 |
|----------|------|
| `DISCORD_WEBHOOK_URL` | Discord チャンネルの設定から発行 |
| `GOOGLE_CLIENT_ID` | Google Cloud Console で発行（Google Calendar連携時） |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console で発行（Google Calendar連携時） |
| `GOOGLE_REFRESH_TOKEN` | `scripts/get_token.py` で取得（Google Calendar連携時） |
| `NOTION_API_KEY` | Notion インテグレーションシークレット（Notion連携時） |
| `NOTION_PARENT_PAGE_ID` | ジャーナルを作成する親ページのID（Notion連携時） |

設定後は毎朝6時(JST)に自動実行される（GitHub Actions cron: `0 21 * * *` UTC）。

mainへのPR作成時にはテストが自動実行され、`DISCORD_WEBHOOK_URL` に実際の通知が送信される。

## ニュースソース一覧

| カテゴリ | ソース | RSS URL |
|---------|--------|---------|
| 政治 | Yahoo!ニュース | `https://news.yahoo.co.jp/rss/topics/politics.xml` |
| 経済 | Yahoo!ニュース | `https://news.yahoo.co.jp/rss/topics/business.xml` |
| 国際 | Yahoo!ニュース | `https://news.yahoo.co.jp/rss/topics/world.xml` |
| AI | ITmedia AIPlus | `https://rss.itmedia.co.jp/rss/2.0/aiplus.xml` |
| セキュリティ | ITmedia Security | `https://rss.itmedia.co.jp/rss/2.0/security.xml` |
| Zenn | Zenn トレンド | `https://zenn.dev/feed` |

各カテゴリ1件ずつ取得。フィードが取得できない場合は空リストにフォールバックする。

## 開発ツールのセットアップ

このリポジトリは Claude Code・Codex CLI・GitHub CLI での作業を想定している。Node.js 18+ が前提。

### GitHub CLI

GitHub CLI（`gh`）を使うとターミナルから PR 作成などの GitHub 操作が行える。

**Windows（winget）**

```powershell
winget install --id GitHub.cli -e
```

インストール後は**新しいターミナルを開いて** PATH を反映させること。

**Mac**

```bash
brew install gh
```

**ログイン**

```bash
gh auth login
```

対話式で「GitHub.com」→「HTTPS」→「Login with a web browser」を選択するとブラウザ認証できる。

> PowerShell でパスが通っていない場合は `& "C:\Program Files\GitHub CLI\gh.exe" auth login` で直接実行できる。

### Claude Code

Anthropic が提供するターミナル向け AI コーディングアシスタント。Node.js 18+ が必要。

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

- **タスクの持ち越し機能**
  - 前日のジャーナルページで未チェックのタスクを翌朝の通知に表示する
  - Notion API で前日ページのチェックボックス状態を取得し、未完了分を Discord に一覧表示する

- **夜の振り返り通知**
  - 夜（例: 21時 JST）に当日ジャーナルの完了状況を Discord へ通知する
  - 未完了タスクを一覧表示し、翌日への持ち越しを意識させる

