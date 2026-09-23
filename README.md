# 🌅 AI Morning Digest (AIニュース要約 PWA)

毎朝更新される最新のAIニュースを30秒で把握できる、通勤中・隙間時間専用のAI要約PWA（Progressive Web Apps）アプリです。
**サーバー代・API代・アプリ代すべて完全無料（0円）** で運用できます。

---

## ✨ 特徴

- 💸 **完全無料**: GitHub Actions (月2,000分無料枠) + Gemini 2.5 Flash (無料枠) + GitHub Pages (無料ホスティング)
- 📲 **iPhone アプリ化 (PWA)**: Safariから「ホーム画面に追加」するだけで、ネイティブアプリ感覚（全画面表示）で起動可能
- ⚡ **通勤最適化**: 3行の箇条書き要約、重要度判定（★3）、カテゴリ分類、既読チェック機能を搭載
- 📶 **オフライン対応**: 地下鉄などの電波が届かない場所でも、直近取得したニュースをサクサク読める
- ⚙️ **簡単カスタマイズ**: 好きなニュースサイトのRSSを `src/config.py` に追加・削除可能

---

## 🚀 5分でできるセットアップ手順

### 1. Gemini API キーを取得する（無料・クレジットカード不要）
1. [Google AI Studio](https://aistudio.google.com/) にアクセスし、Googleアカウントでログインします。
2. 「Get API key」をクリックし、**Create API key** を押してキーをコピーします。

---

### 2. GitHub リポジトリを作成してコードをアップロードする
1. GitHub で新しいリポジトリ（Public または Private）を作成します（例: `ai-news-pwa`）。
2. お手元のPCのターミナル（またはPowerShell）で、本プロジェクトフォルダ内で以下を実行します：

```bash
git init
git add .
git commit -m "feat: initial commit of AI Morning Digest"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git push -u origin main
```

---

### 3. GitHub に API キーを登録する (Secrets)
1. GitHubのリポジトリページを開き、**「Settings」** タブをクリックします。
2. 左メニューの **「Secrets and variables」** > **「Actions」** を選択します。
3. **「New repository secret」** をクリックします。
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: 手順1でコピーした Gemini API キーを貼り付け
4. **「Add secret」** をクリックします。

---

### 4. GitHub Pages を有効化する
1. リポジトリの **「Settings」** > **「Pages」** を開きます。
2. **Build and deployment** の **Source** を **「GitHub Actions」** に変更します。

---

### 5. 動作テスト（手動実行）
1. リポジトリ上部の **「Actions」** タブをクリックします。
2. 左側の **「Daily AI News Update & Deploy」** を選択し、右側の **「Run workflow」** ボタンを押します。
3. 1〜2分で処理が完了し、GitHub PagesのURL（`https://あなたのユーザー名.github.io/リポジトリ名/`）が発行されます！

> [!NOTE]
> これ以降は、**毎朝日本時間の朝7:00 (UTC 22:00)** に自動で最新ニュースが収集・要約され、Webページが更新されます。

---

## 📱 iPhone でホーム画面に追加する方法

1. iPhone の **Safari** で公開された GitHub Pages の URL を開きます。
2. 画面下部の中央にある **共有ボタン（四角から矢印が上に出ているアイコン）** をタップします。
3. メニューを少しスクロールして **「ホーム画面に追加」** をタップします。
4. ホーム画面に専用アプリアイコンが追加されます。タップすると**アドレスバーの出ない全画面アプリ**として起動します！

---

## 🛠️ ニュースサイトのカスタマイズ方法

`src/config.py` を開くだけで、巡回するニュースサイトを自由に追加・無効化できます。

```python
RSS_FEEDS = [
    {
        "name": "追加したいサイト名",
        "url": "https://example.com/feed.xml",
        "category": "最新モデル・研究",
        "language": "ja", # または "en" (英語記事はGeminiが自動で日本語要約)
        "enabled": True,  # False にすると一時的にスキップ
    },
    # ...
]
```

---

## 📁 ディレクトリ構造

```
ai-news-pwa/
├── .github/workflows/
│   └── daily_update.yml       # 毎朝定時実行＆GitHub Pages自動デプロイ
├── src/
│   ├── config.py              # RSSフィード一覧・Gemini設定
│   ├── fetcher.py             # RSSニュース収集 & 重複排除
│   ├── summarizer.py          # Gemini API による要約
│   └── main.py                # 全体実行スクリプト
├── public/                    # PWA Webフロントエンド
│   ├── index.html             # レスポンシブUI
│   ├── style.css              # iOS風モダンデザイン
│   ├── app.js                 # クライアント処理（既読・検索・オフライン）
│   ├── manifest.json          # PWA設定
│   ├── sw.js                  # Service Worker（オフラインキャッシュ）
│   ├── icons/                 # アプリアイコン
│   └── data/
│       └── news.json          # 毎朝更新されるニュースJSON
├── requirements.txt           # Pythonライブラリ
└── README.md                  # 本説明書
```
