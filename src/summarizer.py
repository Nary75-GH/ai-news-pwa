"""
Gemini API を利用した記事の一括要約モジュール
"""

import os
import json
import logging
from typing import List, Dict, Any

from config import GEMINI_MODEL, MAX_ARTICLES_TO_SUMMARIZE

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
あなたは毎朝、多忙なビジネスパーソンやエンジニア向けに最新のAIニュースをキュレーションするプロのエディターです。
与えられた最新記事リストを読み込み、通勤中や隙間時間にスマホで30秒〜1分で内容と重要性が把握できるように、わかりやすく魅力的な日本語で要約してください。
英語の記事も、自然で読みやすい日本語に翻訳して要約してください。
"""

SUMMARY_PROMPT_TEMPLATE = """
以下のAI関連ニュース記事リストを要約し、指定されたJSONフォーマットで出力してください。
特に重要なニュース（最大 {max_count} 件）を厳選して要約してください。

【出力するJSONスキーマ】
[
  {{
    "id": 1,
    "source_name": "配信元メディア名",
    "original_title": "元のタイトル",
    "japanese_title": "スマホで一目で内容がわかるキャッチーで端的な日本語タイトル",
    "link": "元記事URL",
    "published_at": "公開日時ISO文字列",
    "category": "最新モデル・研究 | プロダクト・ツール | ビジネス・提携 | 規制・社会動向 のいずれか",
    "importance": 1から3の整数 (3がトップニュース・最重要),
    "summary_points": [
      "何が起きたか・何が発表されたか（事実）",
      "何ができるようになったか・注目の技術・機能（詳細）",
      "なぜ重要なのか・今後の影響や活用メリット（インパクト）"
    ],
    "keywords": ["キーワード1", "キーワード2"],
    "read_time_seconds": 30
  }}
]

【入力記事リスト】
{articles_text}
"""

def summarize_articles_with_gemini(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gemini API を呼び出して記事リストを一括要約する"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. Generating mock summaries for testing.")
        return generate_mock_summaries(articles[:MAX_ARTICLES_TO_SUMMARIZE])
        
    target_articles = articles[:MAX_ARTICLES_TO_SUMMARIZE]
    if not target_articles:
        logger.info("No articles to summarize.")
        return []

    # 入力テキストの整形
    articles_input = []
    for i, a in enumerate(target_articles, 1):
        articles_input.append(
            f"[{i}] タイトル: {a['title']}\n"
            f"メディア: {a['source_name']}\n"
            f"リンク: {a['link']}\n"
            f"公開日: {a['published_at']}\n"
            f"概要: {a['summary']}\n"
        )
    articles_text = "\n".join(articles_input)

    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        max_count=MAX_ARTICLES_TO_SUMMARIZE,
        articles_text=articles_text
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        content = response.text.strip()
        summaries = json.loads(content)
        logger.info(f"Successfully generated {len(summaries)} summaries with Gemini ({GEMINI_MODEL}).")
        return summaries

    except ImportError:
        logger.warning("google-genai package not found, trying google.generativeai fallback...")
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                generation_config={"response_mime_type": "application/json", "temperature": 0.2}
            )
            res = model.generate_content(prompt)
            return json.loads(res.text.strip())
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            return generate_mock_summaries(target_articles)

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        # 万が一のエラー時はモック要約を返してサイト生成が途切れないようにする
        return generate_mock_summaries(target_articles)

def generate_mock_summaries(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """APIキーがない場合やエラー時のフォールバック用サマリー生成"""
    mock_list = []
    for i, a in enumerate(articles, 1):
        mock_list.append({
            "id": i,
            "source_name": a["source_name"],
            "original_title": a["title"],
            "japanese_title": a["title"],
            "link": a["link"],
            "published_at": a["published_at"],
            "category": a.get("category", "国内ビジネス・速報"),
            "importance": 2,
            "summary_points": [
                f"{a['title']} に関する最新情報です。",
                a["summary"][:120] + "..." if a["summary"] else "詳細は元記事をご確認ください。",
                "AI技術やビジネス活用における重要な動向として注目されています。"
            ],
            "keywords": ["AI", "速報"],
            "read_time_seconds": 30
        })
    return mock_list
