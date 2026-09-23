"""
AIニュース要約システム メイン実行スクリプト
RSS収集 -> Gemini要約 -> public/data/news.json 書き出し
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fetcher import get_latest_ai_news
from summarizer import summarize_articles_with_gemini
from config import GEMINI_MODEL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 出力先パス
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DATA_FILE = BASE_DIR / "public" / "data" / "news.json"

def run_pipeline():
    logger.info("=== Starting AI News Daily Digest Pipeline ===")
    
    # 1. RSSフィード収集
    articles = get_latest_ai_news()
    if not articles:
        logger.warning("No articles fetched from RSS feeds.")
        return

    # 2. Gemini API で一括要約
    summaries = summarize_articles_with_gemini(articles)
    
    # 日本時間 (JST: UTC+9) の現在時刻を取得
    jst_tz = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst_tz)
    date_str = now_jst.strftime("%Y年%m月%d日")
    time_str = now_jst.strftime("%H:%M")
    
    current_digest = {
        "date": date_str,
        "time": time_str,
        "iso_timestamp": now_jst.isoformat(),
        "articles_count": len(summaries),
        "articles": summaries
    }

    # 3. 過去ログ（過去7日分）のアーカイブ処理
    archives = []
    if OUTPUT_DATA_FILE.exists():
        try:
            with open(OUTPUT_DATA_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                
            # 既存の最新分をアーカイブに追加（同日の重複を避ける）
            old_current = existing_data.get("current")
            if old_current and old_current.get("date") != date_str:
                archives.append(old_current)
                
            existing_archives = existing_data.get("archives", [])
            for arch in existing_archives:
                if arch.get("date") != date_str and arch.get("date") not in [a.get("date") for a in archives]:
                    archives.append(arch)
                    
            # 直近7日分に限定
            archives = archives[:7]
        except Exception as e:
            logger.warning(f"Could not load existing news.json archives: {e}")

    final_output = {
        "meta": {
            "title": "Daily AI News Digest",
            "model_used": GEMINI_MODEL,
            "last_updated_jst": f"{date_str} {time_str}",
            "generated_at": now_jst.isoformat()
        },
        "current": current_digest,
        "archives": archives
    }

    # 4. JSONファイルに書き出し
    OUTPUT_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Successfully saved digest to {OUTPUT_DATA_FILE}")
    logger.info("=== Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_pipeline()
