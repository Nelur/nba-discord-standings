# 🏀 NBA順位 Discord自動投稿Bot

更新

指定したNBAチームの順位を毎日Discordに自動投稿するBot。

## 投稿イメージ

```
🏀 NBA順位 (2024/12/31)

【Eastern】
 1位 ☘️ セルツ (25勝10敗) 直近: 8-2
 4位 🗽 ニックス (22勝13敗) 直近: 5-5
10位 🔥 ヒート (15勝18敗) 直近: 4-6

【Western】
 1位 ⚡ サンダー (26勝9敗) 直近: 9-1
 3位 💜 レイカーズ (21勝14敗) 直近: 6-4
 7位 🌉 ウォリアーズ (18勝17敗) 直近: 3-7
```

## 特徴

- ✅ **完全無料** - GitHub Actions + Discord Webhookで運用
- ✅ **毎日自動投稿** - 日本時間13:00に自動実行
- ✅ **簡単カスタマイズ** - `config.json`でチーム変更可能
- ✅ **サーバー不要** - GitHub Actionsで完結

---

# 🚀 セットアップ手順

## Step 1: GitHubリポジトリを作成

1. [GitHub](https://github.com) にログイン

2. 右上の「+」→「New repository」をクリック

3. 以下の設定で作成：
   - **Repository name**: `nba-discord-standings`（好きな名前でOK）
   - **Public** を選択（⚠️ 無料で使うにはPublic必須）
   - 「Create repository」をクリック

---

## Step 2: Discord Webhook URLを取得

1. Discordで投稿先のチャンネルを開く

2. チャンネル名の横の ⚙️（設定）をクリック

3. 左メニューから「連携サービス」→「ウェブフック」

4. 「新しいウェブフック」をクリック

5. 名前を設定（例: `NBA順位Bot`）

6. 「ウェブフックURLをコピー」をクリック
   - このURLは後で使うので、メモ帳などに保存しておく
   - ⚠️ **このURLは絶対に公開しない！**

---

## Step 3: GitHub SecretsにWebhook URLを登録

1. GitHubの作成したリポジトリページを開く

2. 「Settings」タブをクリック

3. 左メニューの「Secrets and variables」→「Actions」をクリック

4. 「New repository secret」をクリック

5. 以下を入力：
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: Step 2でコピーしたWebhook URL

6. 「Add secret」をクリック

---

## Step 4: コードをアップロード

### 方法A: GitHubのWeb画面から（初心者向け）

1. リポジトリページで「Add file」→「Upload files」

2. このフォルダ内の全ファイルをドラッグ＆ドロップ：
   - `main.py`
   - `config.json`
   - `requirements.txt`
   - `.gitignore`
   - `.github/workflows/post-standings.yml`

3. 「Commit changes」をクリック

### 方法B: Git コマンドから

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/nba-discord-standings.git
cd nba-discord-standings

# ファイルをコピー（ダウンロードしたファイルをこのフォルダに入れる）

# コミット＆プッシュ
git add .
git commit -m "Initial commit"
git push origin main
```

---

## Step 5: 追いかけたいチームを設定

`config.json` を編集して、追いかけたいチームを設定：

```json
{
  "teams": [
    {"id": "BOS", "name": "セルツ", "emoji": "☘️"},
    {"id": "LAL", "name": "レイカーズ", "emoji": "💜"},
    {"id": "GSW", "name": "ウォリアーズ", "emoji": "🌉"}
  ]
}
```

### チームIDの一覧

| Eastern | | Western | |
|---------|---|---------|---|
| ATL - ホークス 🦅 | BOS - セルツ ☘️ | DAL - マブス 🐴 | DEN - ナゲッツ ⛏️ |
| BKN - ネッツ 🕸️ | CHA - ホーネッツ 🐝 | GSW - ウォリアーズ 🌉 | HOU - ロケッツ 🚀 |
| CHI - ブルズ 🐂 | CLE - キャブス ⚔️ | LAC - クリッパーズ ⛵ | LAL - レイカーズ 💜 |
| DET - ピストンズ 🔧 | IND - ペイサーズ 🏎️ | MEM - グリズリーズ 🐻 | MIN - ウルブズ 🐺 |
| MIA - ヒート 🔥 | MIL - バックス 🦌 | NOP - ペリカンズ 🦢 | OKC - サンダー ⚡ |
| NYK - ニックス 🗽 | ORL - マジック ✨ | PHX - サンズ ☀️ | POR - ブレイザーズ 🌲 |
| PHI - シクサーズ 🔔 | TOR - ラプターズ 🦖 | SAC - キングス 👑 | SAS - スパーズ 🤠 |
| WAS - ウィザーズ 🧙 | | UTA - ジャズ 🎷 | |

---

## Step 6: 動作テスト

1. GitHubリポジトリの「Actions」タブを開く

2. 左メニューから「Post NBA Standings to Discord」を選択

3. 「Run workflow」→「Run workflow」をクリック

4. 実行が完了するまで待つ（約1分）

5. Discordチャンネルに投稿されていれば成功！🎉

---

## 🔧 カスタマイズ

### 投稿時間を変更

`.github/workflows/post-standings.yml` の cron を編集：

```yaml
schedule:
  - cron: '0 4 * * *'  # UTC 4:00 = JST 13:00
```

| 日本時間 | UTC | cron |
|----------|-----|------|
| 9:00 | 0:00 | `0 0 * * *` |
| 12:00 | 3:00 | `0 3 * * *` |
| 13:00 | 4:00 | `0 4 * * *` |
| 18:00 | 9:00 | `0 9 * * *` |
| 21:00 | 12:00 | `0 12 * * *` |

### チーム名・絵文字を変更

`config.json` で自由にカスタマイズ可能：

```json
{"id": "LAL", "name": "レイカーズ", "emoji": "💛"}
```

---

## ❓ トラブルシューティング

### Discordに投稿されない

1. **Secrets確認**: `DISCORD_WEBHOOK_URL` が正しく設定されているか
2. **Actions確認**: GitHubの「Actions」タブでエラーログを確認
3. **Webhook確認**: Discord側でWebhookが有効か確認

### チームが見つからないエラー

- `config.json` のチームIDが正しいか確認（上のチームID一覧を参照）

### 「This scheduled workflow is disabled」と表示される

- リポジトリに60日間アクティビティがないと自動で無効化される
- 「Enable workflow」をクリックして再有効化

---

## 📄 ライセンス

MIT License - 自由に使ってください！
