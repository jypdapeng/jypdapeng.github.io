"""手动导入 Amazon 差评服务（无需 Rainforest API）。"""

import hashlib
import re
from typing import Any

from app.database import get_reviews_by_asins, save_raw_reviews


def parse_review_lines(text: str) -> list[str]:
    """
    将粘贴文本拆分为单条评论。

    @param text 用户粘贴的多行文本
    @return 评论内容列表
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    reviews: list[str] = []
    buffer: list[str] = []

    for line in lines:
        if re.match(r"^\d+\s*(star|星)", line, re.IGNORECASE):
            if buffer:
                reviews.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line)

    if buffer:
        reviews.append(" ".join(buffer))

    if not reviews and text.strip():
        line_items = [line.strip() for line in text.splitlines() if len(line.strip()) >= 15]
        reviews = line_items if line_items else [text.strip()]

    return [item for item in reviews if len(item) >= 15]


def import_manual_reviews(asin: str, text: str, rating: int | None = None) -> dict[str, Any]:
    """
    导入用户从亚马逊页面复制的真实差评。

    @param asin 商品 ASIN
    @param text 粘贴的评论文本
    @param rating 可选评分（1-3 星）
    @return 导入结果
    """
    normalized_asin = asin.upper().strip()
    parsed = parse_review_lines(text)
    if not parsed:
        return {"imported": 0, "asin": normalized_asin, "message": "未识别到有效评论，每条至少 15 个字符"}

    records: list[dict[str, Any]] = []
    for index, content in enumerate(parsed):
        digest = hashlib.md5(f"{normalized_asin}:{content[:120]}".encode()).hexdigest()[:12]
        records.append(
            {
                "source": "amazon_manual",
                "source_id": f"manual-{digest}",
                "asin": normalized_asin,
                "title": "",
                "content": content[:2000],
                "rating": rating,
            }
        )

    saved = save_raw_reviews(records)
    return {
        "imported": saved,
        "asin": normalized_asin,
        "message": f"已导入 {saved} 条真实差评",
    }


def load_manual_reviews(asins: list[str] | None = None) -> list[dict[str, Any]]:
    """
    读取已导入的手动差评。

    @param asins 可选 ASIN 过滤
    @return 评论列表
    """
    return get_reviews_by_asins(asins, sources=["amazon_manual"])
