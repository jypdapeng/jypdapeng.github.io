"""关键词到竞品 ASIN 的映射表（用于搜索页被拦截时的回退）。"""

KEYWORD_ASIN_MAP: dict[str, list[dict[str, str]]] = {
    "knee surgery recovery pillow": [
        {"asin": "B0DQDCBF7X", "title": "KingPavonini Single Leg Elevation Pillow"},
        {"asin": "B0GVDCX8T2", "title": "Wellbrance Adjustable Leg Elevation Pillow"},
        {"asin": "B087TR1X4R", "title": "LightEase Leg Elevation Pillow"},
    ],
    "leg elevation pillow after surgery": [
        {"asin": "B0DQDD465D", "title": "KingPavonini Double Leg Pillow"},
        {"asin": "B0D4LJ1XLS", "title": "LightEase Adjustable Leg Pillow"},
        {"asin": "B0DQDCBF7X", "title": "KingPavonini Single Leg Pillow"},
    ],
    "knee surgery shower cover": [
        {"asin": "B07Y3PZHD9", "title": "KEEFITT Knee Shower Cover"},
        {"asin": "B07RMDRDMN", "title": "Meydoja Full Leg Shower Cover"},
        {"asin": "B07FKSGRZF", "title": "KEEFITT Knee Cast Cover"},
    ],
    "knee extension bolster": [
        {"asin": "B0G4G534LW", "title": "KneEXT Heel-Cup Foam Roll"},
        {"asin": "B07CQ5W8VJ", "title": "PureComfort Knee Extension Pillow"},
    ],
    "walker cup holder": [
        {"asin": "B07HFD1M6S", "title": "Walker Cup Holder Attachment"},
        {"asin": "B09MVP5Q8C", "title": "Crutch Drink Holder"},
        {"asin": "B0B7BP6C7L", "title": "Walker Basket Organizer"},
    ],
    "knee ice pack after surgery": [
        {"asin": "B089YBVBV3", "title": "REVIX Knee Ice Pack"},
        {"asin": "B0B41GD6CF", "title": "KingPavonini XXL Knee Ice Pack"},
    ],
    "reacher grabber tool": [
        {"asin": "B0006VDDW6", "title": "ArcMate E-Z Reacher"},
        {"asin": "B07WTXWC4R", "title": "Vive Suction Cup Reacher"},
    ],
    "shower stool after surgery": [
        {"asin": "B0BTGN5GSM", "title": "ENKEZI Shower Foot Rest"},
        {"asin": "B0FHKLS2FP", "title": "LIDTOP Adjustable Shower Stool"},
    ],
    "knee surgery recovery kit": [
        {"asin": "B07Y3PZHD9", "title": "KEEFITT Shower Cover"},
        {"asin": "B0DQDCBF7X", "title": "KingPavonini Leg Pillow"},
        {"asin": "B089YBVBV3", "title": "REVIX Ice Pack"},
    ],
    "knee surgery recovery must haves": [
        {"asin": "B0GVDCX8T2", "title": "Wellbrance Leg Pillow"},
        {"asin": "B07Y3PZHD9", "title": "KEEFITT Shower Cover"},
        {"asin": "B0G4G534LW", "title": "KneEXT Knee Bolster"},
    ],
    "leg lifter for after knee surgery": [
        {"asin": "B07CQ5W8VJ", "title": "PureComfort Leg Lifter"},
        {"asin": "B0DQDCBF7X", "title": "KingPavonini Leg Pillow"},
    ],
    "acl surgery recovery essentials": [
        {"asin": "B0DQDCBF7X", "title": "KingPavonini Leg Pillow"},
        {"asin": "B07Y3PZHD9", "title": "KEEFITT Shower Cover"},
    ],
}


def lookup_asins(keyword: str) -> list[dict[str, str]]:
    """
    根据关键词查找 ASIN 列表。

    @param keyword 搜索关键词
    @return ASIN 信息列表
    """
    normalized = keyword.lower().strip()
    if normalized in KEYWORD_ASIN_MAP:
        return KEYWORD_ASIN_MAP[normalized]

    matches: list[dict[str, str]] = []
    for key, items in KEYWORD_ASIN_MAP.items():
        if key in normalized or normalized in key:
            matches.extend(items)

    if matches:
        return _dedupe_asins(matches)

    tokens = set(normalized.split())
    for key, items in KEYWORD_ASIN_MAP.items():
        if len(tokens & set(key.split())) >= 2:
            matches.extend(items)

    return _dedupe_asins(matches)


def _dedupe_asins(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """ASIN 去重。"""
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in items:
        asin = item["asin"]
        if asin in seen:
            continue
        seen.add(asin)
        result.append(item)
    return result[:3]
