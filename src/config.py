"""
AIニュース要約システム 設定ファイル
ニュースソース(RSS)の追加・削除や、要約モデルの設定をここで行えます。
"""

import os

# Gemini API設定
# モデル名: 無料枠で高速・高精度な gemini-2.5-flash または gemini-1.5-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# 1回に要約・配信する最大記事数
MAX_ARTICLES_TO_SUMMARIZE = 12

# 収集対象期間（過去何時間以内の記事を取得するか）
MAX_ARTICLE_AGE_HOURS = 36

# ニュースソース (RSSフィード) 一覧
# 'enabled': True/False で個別にオン/オフを切り替えられます。
# 新しいサイトを追加したい場合は、ここに辞書を追加するだけでOKです！
RSS_FEEDS = [
    # --- 国内ニュース (日本語) ---
    {
        "name": "Googleニュース (生成AI・人工知能)",
        "url": "https://news.google.com/rss/search?q=%E7%94%9F%E6%88%90AI%20OR%20%22%E4%BA%BA%E5%87%9B%E7%9F%A5%E8%83%BD%22&hl=ja&gl=JP&ceid=JP:ja",
        "category": "国内ビジネス・速報",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "ITmedia AI+",
        "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
        "category": "国内ビジネス・活用",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "GIGAZINE (AI・テクノロジー)",
        "url": "https://gigazine.net/news/rss_2.0/",
        "category": "国内速報・ツール",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "はてなブックマーク (AI人気エントリー)",
        "url": "https://b.hatena.ne.jp/q/AI?sort=popular&users=5&mode=rss",
        "category": "国内トレンド・オピニオン",
        "language": "ja",
        "enabled": True,
    },

    # --- 海外公式・テックメディア (英語 -> Geminiが日本語要約) ---
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "category": "海外公式発表",
        "language": "en",
        "enabled": True,
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "海外スタートアップ・最新モデル",
        "language": "en",
        "enabled": True,
    },
    {
        "name": "The Verge (AI)",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "海外テック・製品",
        "language": "en",
        "enabled": True,
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "海外深掘り・研究",
        "language": "en",
        "enabled": False, # 必要に応じて True に
    },
]
