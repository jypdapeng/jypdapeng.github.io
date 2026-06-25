"""数据源配置与可用性检查。"""

from app.config import settings
from app.database import count_manual_reviews_by_asin


def get_data_source_status() -> dict:
    """
    返回各真实数据源的配置与可用状态。

    @return 数据源状态字典
    """
    amazon_api_ready = bool(settings.rainforest_api_key)
    manual_stats = count_manual_reviews_by_asin()
    manual_count = sum(item["count"] for item in manual_stats)
    core_ready = True

    if amazon_api_ready:
        amazon_message = "Rainforest API 已配置，可自动拉取差评与搜索 ASIN"
        amazon_mode = "rainforest"
    elif manual_count > 0:
        amazon_message = f"已用手动导入 {manual_count} 条真实 Amazon 差评（无需 API Key）"
        amazon_mode = "manual"
    else:
        amazon_message = (
            "Amazon 自动采集未启用。可在页面手动粘贴差评，或注册 Rainforest 免费试用（约 100 次）"
        )
        amazon_mode = "manual_pending"

    return {
        "data_mode": "real_only",
        "sources": {
            "google_suggest": {"enabled": True, "label": "Google 搜索联想", "real": True},
            "amazon_suggest": {"enabled": True, "label": "Amazon 自动补全", "real": True},
            "google_trends_rss": {"enabled": True, "label": "Google Trends RSS", "real": True},
            "reddit_pullpush": {"enabled": True, "label": "Reddit PullPush API", "real": True},
            "amazon_manual": {
                "enabled": manual_count > 0,
                "label": "手动导入 Amazon 差评",
                "real": True,
                "count": manual_count,
            },
            "amazon_rainforest": {
                "enabled": amazon_api_ready,
                "label": "Amazon 自动采集 (Rainforest API，可选)",
                "real": amazon_api_ready,
                "required_env": "RAINFOREST_API_KEY",
                "optional": True,
            },
        },
        "ready": core_ready,
        "amazon_mode": amazon_mode,
        "manual_review_count": manual_count,
        "message": amazon_message,
    }
