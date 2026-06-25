"""痛点提取分析器。"""

import re
from collections import Counter, defaultdict
from typing import Any

PAIN_PATTERNS: list[dict[str, Any]] = [
  {
    "theme_zh": "滑落/不稳定",
    "theme_en": "sliding unstable",
    "keywords": ["slide", "slip", "sliding", "move", "unstable", "falls off", "滑", "不稳"],
    "category": "术后康复",
  },
  {
    "theme_zh": "太软/塌陷",
    "theme_en": "too soft flatten",
    "keywords": ["too soft", "flatten", "sink", "collapse", "flimsy", "太软", "塌陷"],
    "category": "术后康复",
  },
  {
    "theme_zh": "太硬/硌痛",
    "theme_en": "too firm painful",
    "keywords": ["too firm", "too hard", "uncomfortable", "pressure", "hurts", "太硬", "硌"],
    "category": "术后康复",
  },
  {
    "theme_zh": "尺寸不合适",
    "theme_en": "size fit issue",
    "keywords": ["too narrow", "too small", "too short", "too wide", "not wide enough", "尺寸", "太小"],
    "category": "通用",
  },
  {
    "theme_zh": "高度/角度不够",
    "theme_en": "height angle issue",
    "keywords": ["not high enough", "height", "angle", "extension", "straight", "高度", "伸直"],
    "category": "术后康复",
  },
  {
    "theme_zh": "洗澡/防水困难",
    "theme_en": "shower waterproof",
    "keywords": ["shower", "water", "wet", "waterproof", "洗澡", "防水", "进水"],
    "category": "术后康复",
  },
  {
    "theme_zh": "拐杖双手占用",
    "theme_en": "crutch hands busy",
    "keywords": ["crutch", "crutches", "hands free", "carry", "both hands", "拐杖", "双手"],
    "category": "术后康复",
  },
  {
    "theme_zh": "冰敷持效短",
    "theme_en": "ice pack short cold",
    "keywords": ["not cold", "warm too fast", "ice pack", "cold enough", "冰", "不够凉"],
    "category": "术后康复",
  },
  {
    "theme_zh": "康复依从性差",
    "theme_en": "exercise compliance",
    "keywords": ["forget", "count", "exercise", "ankle pump", "physical therapy", "忘记", "计数", "踝泵"],
    "category": "术后康复",
  },
  {
    "theme_zh": "够不到/弯腰难",
    "theme_en": "reach bend difficulty",
    "keywords": ["reach", "floor", "grabber", "bend", "pick up", "够不到", "弯腰"],
    "category": "术后康复",
  },
  {
    "theme_zh": "安装/使用复杂",
    "theme_en": "hard to use",
    "keywords": ["hard to put on", "difficult", "confusing", "alone", "安装", "难用"],
    "category": "通用",
  },
  {
    "theme_zh": "质量/耐用性差",
    "theme_en": "poor durability",
    "keywords": ["broke", "tear", "cheap", "fall apart", "quality", "坏了", "质量"],
    "category": "通用",
  },
]


def extract_pain_points(reviews: list[dict[str, Any]], top_n: int = 8) -> list[dict[str, Any]]:
    """
    从评论文本中提取痛点主题。

    @param reviews 原始评论列表
    @param top_n 返回主题数量
    @return 痛点列表
    """
    theme_counter: Counter[str] = Counter()
    theme_examples: dict[str, list[str]] = defaultdict(list)
    theme_meta: dict[str, dict[str, str]] = {}

    for review in reviews:
        text = f"{review.get('title', '')} {review.get('content', '')}".lower()
        if len(text.strip()) < 10:
            continue
        for pattern in PAIN_PATTERNS:
            if any(keyword in text for keyword in pattern["keywords"]):
                theme = pattern["theme_zh"]
                theme_counter[theme] += 1
                theme_meta[theme] = {
                    "theme_en": pattern["theme_en"],
                    "category": pattern["category"],
                }
                if len(theme_examples[theme]) < 3:
                    snippet = review.get("content", "")[:160]
                    if snippet and snippet not in theme_examples[theme]:
                        theme_examples[theme].append(snippet)

    results: list[dict[str, Any]] = []
    for theme, count in theme_counter.most_common(top_n):
        meta = theme_meta.get(theme, {})
        results.append(
            {
                "theme_zh": theme,
                "theme_en": meta.get("theme_en", ""),
                "category": meta.get("category", "通用"),
                "count": count,
                "examples": theme_examples.get(theme, []),
                "severity": _severity_label(count, len(reviews)),
            }
        )
    return results


def analyze_free_text(text: str) -> list[dict[str, Any]]:
    """
    分析用户粘贴的任意文本。

    @param text 原始文本（可多段）
    @return 痛点列表
    """
    chunks = [chunk.strip() for chunk in re.split(r"[\n\r]+", text) if chunk.strip()]
    reviews = [{"title": "", "content": chunk} for chunk in chunks]
    return extract_pain_points(reviews, top_n=10)


def _severity_label(count: int, total: int) -> str:
    """根据频次生成严重度标签。"""
    if total == 0:
        return "低"
    ratio = count / total
    if ratio >= 0.25 or count >= 5:
        return "高"
    if ratio >= 0.12 or count >= 3:
        return "中"
    return "低"
