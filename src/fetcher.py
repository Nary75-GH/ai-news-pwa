"""
RSSフィード取得・正規化・フィルタリングモジュール
"""

import re
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from config import RSS_FEEDS, MAX_ARTICLE_AGE_HOURS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 全般テックサイト用AI関連キーワード判定
AI_KEYWORDS = [
    "ai", "人工知能", "生成ai", "llm", "gpt", "chatgpt", "openai", "claude", "anthropic",
    "gemini", "deepmind", "copilot", "機械学習", "ディープラーニング", "画像生成",
    "stable diffusion", "midjourney", "llama", "パラメータ", "推論", "エージェント"
]

def clean_html(raw_html: str) -> str:
    """HTMLタグを除去してプレーンテキストにする"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # 連続する空白・改行を整理
    text = re.sub(r'\s+', ' ', text)
    return text[:600] # 要約プロンプト用に適度な長さにカット

def parse_published_time(entry: Any) -> datetime:
    """エントリから公開日時を抽出し、UTC datetime オブジェクトとして返す"""
    now = datetime.now(timezone.utc)
    for field in ["published", "updated", "created"]:
        if field in entry and entry[field]:
            try:
                dt = date_parser.parse(entry[field])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
            
    return now

def is_ai_related(title: str, summary: str) -> bool:
    """記事がAIに関連しているかキーワード判定"""
    content = f"{title.lower()} {summary.lower()}"
    return any(kw in content for kw in AI_KEYWORDS)

def fetch_feed_entries(feed_conf: Dict[str, Any], cutoff_time: datetime) -> List[Dict[str, Any]]:
    """単一のRSSフィードを取得して整形"""
    url = feed_conf["url"]
    name = feed_conf["name"]
    category = feed_conf["category"]
    
    logger.info(f"Fetching RSS: {name} ({url})")
    articles = []
    
    try:
        # ユーザーエージェントを設定してリクエスト
        parsed = feedparser.parse(url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-News-Digest/1.0")
        
        for entry in parsed.entries:
            pub_date = parse_published_time(entry)
            
            # 収集対象期間外の記事はスキップ
            if pub_date < cutoff_time:
                continue
                
            title = clean_html(getattr(entry, "title", "")).strip()
            summary = clean_html(getattr(entry, "summary", getattr(entry, "description", ""))).strip()
            link = getattr(entry, "link", "").strip()
            
            if not title or not link:
                continue

            # 一般テック系サイトの場合はAI関連キーワードが含まれているか判定
            if "GIGAZINE" in name or "はてな" in name:
                if not is_ai_related(title, summary):
                    continue
                    
            articles.append({
                "source_name": name,
                "category": category,
                "title": title,
                "summary": summary,
                "link": link,
                "published_at": pub_date.isoformat(),
                "published_dt": pub_date
            })
            
    except Exception as e:
        logger.error(f"Error fetching feed {name}: {e}")
        
    return articles

def get_latest_ai_news() -> List[Dict[str, Any]]:
    """有効な全RSSフィードから最新ニュースを収集し、重複排除して返す"""
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(hours=MAX_ARTICLE_AGE_HOURS)
    
    all_articles: List[Dict[str, Any]] = []
    seen_links = set()
    seen_titles = set()
    
    for feed_conf in RSS_FEEDS:
        if not feed_conf.get("enabled", True):
            continue
            
        entries = fetch_feed_entries(feed_conf, cutoff_time)
        
        # サイトごとに最大5件までピックアップ（偏りを防ぐ）
        count = 0
        for item in entries:
            norm_title = re.sub(r'[\s\W_]+', '', item["title"].lower())
            if item["link"] in seen_links or norm_title in seen_titles:
                continue
                
            seen_links.add(item["link"])
            seen_titles.add(norm_title)
            all_articles.append(item)
            count += 1
            if count >= 5:
                break
                
    # 公開日時の新しい順にソート
    all_articles.sort(key=lambda x: x["published_dt"], reverse=True)
    
    logger.info(f"Total unique articles collected: {len(all_articles)}")
    return all_articles

if __name__ == "__main__":
    articles = get_latest_ai_news()
    print(f"Collected {len(articles)} articles.")
    for i, a in enumerate(articles[:5], 1):
        print(f"{i}. [{a['source_name']}] {a['title']} ({a['published_at']})")
