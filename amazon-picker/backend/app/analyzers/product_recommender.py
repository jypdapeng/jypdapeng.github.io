"""选品方向推荐器。"""

from typing import Any

PRODUCT_PLAYBOOK: list[dict[str, Any]] = [
    {
        "themes": ["滑落/不稳定", "太软/塌陷", "尺寸不合适"],
        "direction": "防滑加宽腿抬高枕",
        "direction_en": "anti-slip wide leg elevation pillow",
        "blue_ocean_score": 5,
        "reason": "需求大但竞争红海，需做防滑/加宽/可调高度微创新。",
        "actions": ["加宽 20%", "底部硅胶防滑", "侧挡防滑落", "打 PCL/ACL 长尾词"],
        "supply_keywords": ["腿抬高枕 OEM", "leg elevation pillow memory foam"],
        "price_band": "$29.99-$49.99",
    },
    {
        "themes": ["高度/角度不够"],
        "direction": "膝下伸直垫 / Terminal Knee Extension Bolster",
        "direction_en": "knee extension bolster post surgery",
        "blue_ocean_score": 8,
        "reason": "比大楔形枕更细分，评论少，符合术后伸直需求。",
        "actions": ["强调 0° extension", "硬质 EVA 材质", "体积小降 FBA 费"],
        "supply_keywords": ["膝下垫 康复", "foam bolster knee extension"],
        "price_band": "$19.99-$29.99",
    },
    {
        "themes": ["洗澡/防水困难"],
        "direction": "术后淋浴防水套 / 淋浴凳",
        "direction_en": "knee surgery shower cover stool",
        "blue_ocean_score": 7,
        "reason": "术后洗澡是高频恐惧点，硅胶加长款有微切口。",
        "actions": ["加长 27-30 寸", "易穿脱设计", "术后场景图文"],
        "supply_keywords": ["淋浴防水套 加长", "shower stool corner"],
        "price_band": "$24.99-$39.99",
    },
    {
        "themes": ["拐杖双手占用"],
        "direction": "拐杖/助行器配件套装",
        "direction_en": "walker crutch cup phone holder",
        "blue_ocean_score": 8,
        "reason": "轻小件、无模具、术后刚需，竞争低于康复大类。",
        "actions": ["杯架+手机夹+小袋 bundle", "适配多管径", "术后礼包组合"],
        "supply_keywords": ["拐杖杯架", "walker accessory bag"],
        "price_band": "$14.99-$24.99",
    },
    {
        "themes": ["冰敷持效短"],
        "direction": "加长绑带冰敷包",
        "direction_en": "xl knee ice pack wrap",
        "blue_ocean_score": 4,
        "reason": "需求真实但 REVIX 等头部强，仅建议做凝胶量/绑带加长。",
        "actions": ["更长绑带", "双面温感", "术后礼包搭配"],
        "supply_keywords": ["冰敷护膝 凝胶", "reusable gel ice pack knee"],
        "price_band": "$24.99-$34.99",
    },
    {
        "themes": ["康复依从性差"],
        "direction": "康复提醒卡片 / 跟练指南（轻量数字或纸质）",
        "direction_en": "post surgery rehab checklist",
        "blue_ocean_score": 6,
        "reason": "硬件计数器开发重，可先做康复清单+二维码内容。",
        "actions": ["术后 4 周打卡表", "踝泵/直腿抬高/股四头", "配 App 或 PDF"],
        "supply_keywords": ["康复计划卡片", "post surgery recovery journal"],
        "price_band": "$9.99-$19.99",
    },
    {
        "themes": ["够不到/弯腰难"],
        "direction": "加长拾物器",
        "direction_en": "reacher grabber after surgery",
        "blue_ocean_score": 7,
        "reason": "术后常被忽略但刚需，可打术后长尾场景。",
        "actions": ["32 寸加长", "磁吸爪头", "术后 recovery 文案"],
        "supply_keywords": ["拾物器 加长", "reacher grabber tool"],
        "price_band": "$12.99-$19.99",
    },
    {
        "themes": ["安装/使用复杂", "质量/耐用性差"],
        "direction": "易用型康复辅具（加固版）",
        "direction_en": "easy use recovery aid durable",
        "blue_ocean_score": 6,
        "reason": "通过加固材质、免安装设计切差评痛点。",
        "actions": ["免工具安装", "加厚材质", "图文说明优化"],
        "supply_keywords": ["康复辅助 加固", "easy install shower chair"],
        "price_band": "$19.99-$35.99",
    },
]


def recommend_products(pain_points: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """
    根据痛点推荐选品方向。

    @param pain_points 痛点列表
    @param limit 返回数量
    @return 选品建议
    """
    if not pain_points:
        return [_default_suggestion()]

    theme_scores: dict[str, int] = {}
    for point in pain_points:
        weight = {"高": 3, "中": 2, "低": 1}.get(point.get("severity", "低"), 1)
        theme_scores[point["theme_zh"]] = theme_scores.get(point["theme_zh"], 0) + point["count"] * weight

    ranked: list[dict[str, Any]] = []
    for playbook in PRODUCT_PLAYBOOK:
        score = sum(theme_scores.get(theme, 0) for theme in playbook["themes"])
        if score <= 0:
            continue
        ranked.append(
            {
                **playbook,
                "match_score": score,
                "matched_themes": [t for t in playbook["themes"] if t in theme_scores],
                "verdict": _verdict(playbook["blue_ocean_score"]),
            }
        )

    ranked.sort(key=lambda item: (item["match_score"], item["blue_ocean_score"]), reverse=True)
    if not ranked:
        return [_default_suggestion()]
    return ranked[:limit]


def _verdict(blue_ocean_score: int) -> str:
    """生成入场建议。"""
    if blue_ocean_score >= 8:
        return "建议优先验证"
    if blue_ocean_score >= 6:
        return "可做，需差异化"
    return "谨慎，竞争偏红"


def _default_suggestion() -> dict[str, Any]:
    """默认推荐项。"""
    return {
        "direction": "膝下伸直垫 + 拐杖配件",
        "direction_en": "knee extension bolster + walker accessories",
        "blue_ocean_score": 8,
        "reason": "术后康复轻小件切口中，蓝海评分较高。",
        "actions": ["先监控 3 个 ASIN 差评", "1688 找现货", "小批量 200 件测款"],
        "supply_keywords": ["膝下垫 康复", "拐杖杯架"],
        "price_band": "$19.99-$29.99",
        "match_score": 0,
        "matched_themes": [],
        "verdict": "建议优先验证",
    }
