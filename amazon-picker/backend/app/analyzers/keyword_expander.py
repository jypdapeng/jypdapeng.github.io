"""关键词扩展器。"""

from typing import Any

THEME_KEYWORD_MAP: dict[str, list[str]] = {
    "滑落/不稳定": [
        "non slip leg pillow",
        "anti slide wedge pillow",
        "leg elevation pillow stays in place",
        "knee surgery pillow anti fall",
    ],
    "太软/塌陷": [
        "firm leg elevation pillow",
        "high density foam wedge",
        "post surgery leg support firm",
    ],
    "太硬/硌痛": [
        "soft top firm base leg pillow",
        "knee recess leg wedge",
        "comfort leg elevation after surgery",
    ],
    "尺寸不合适": [
        "wide leg elevation pillow",
        "extra large leg wedge",
        "single leg elevation pillow",
    ],
    "高度/角度不够": [
        "adjustable height leg pillow",
        "knee extension bolster",
        "terminal knee extension wedge",
        "0 degree knee extension pillow",
    ],
    "洗澡/防水困难": [
        "knee surgery shower cover",
        "waterproof leg cast cover shower",
        "post surgery shower stool",
    ],
    "拐杖双手占用": [
        "crutch cup holder",
        "walker phone holder",
        "hands free crutch bag",
        "walker accessory tray",
    ],
    "冰敷持效短": [
        "long lasting knee ice pack",
        "xl knee ice wrap",
        "ice pack knee after surgery",
    ],
    "康复依从性差": [
        "ankle pump exercise",
        "post surgery exercise reminder",
        "knee surgery rehab exercises",
    ],
    "够不到/弯腰难": [
        "reacher grabber tool long",
        "pick up tool after surgery",
        "extended grabber for elderly",
    ],
    "安装/使用复杂": [
        "easy on shower cast cover",
        "one hand crutch accessories",
    ],
    "质量/耐用性差": [
        "heavy duty shower stool",
        "durable knee ice pack",
    ],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "术后康复": [
        "ACL recovery essentials",
        "PCL surgery recovery",
        "knee replacement recovery aids",
        "post op knee supplies",
    ],
    "通用": [
        "problem solving amazon finds",
        "ergonomic home helper",
    ],
}


def expand_keywords(pain_points: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    """
    根据痛点扩展亚马逊搜索关键词。

    @param pain_points 痛点列表
    @param limit 关键词数量上限
    @return 关键词建议
    """
    keywords: list[dict[str, Any]] = []
    seen: set[str] = set()

    for point in pain_points:
        theme = point["theme_zh"]
        for phrase in THEME_KEYWORD_MAP.get(theme, []):
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            keywords.append(
                {
                    "keyword": phrase,
                    "source_theme": theme,
                    "category": point.get("category", "通用"),
                    "priority": _priority(point),
                }
            )

        for phrase in CATEGORY_KEYWORDS.get(point.get("category", ""), []):
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            keywords.append(
                {
                    "keyword": phrase,
                    "source_theme": theme,
                    "category": point.get("category", "通用"),
                    "priority": "中",
                }
            )

        if len(keywords) >= limit:
            break

    priority_order = {"高": 0, "中": 1, "低": 2}
    keywords.sort(key=lambda item: priority_order.get(item["priority"], 9))
    return keywords[:limit]


def _priority(point: dict[str, Any]) -> str:
    """根据痛点严重度映射关键词优先级。"""
    severity = point.get("severity", "低")
    if severity == "高":
        return "高"
    if severity == "中":
        return "中"
    return "低"
