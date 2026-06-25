"""数据源配置与可用性检查。"""

from app.config import settings


def get_data_source_status() -> dict:
    """
    返回各真实数据源的配置与可用状态。

    @return 数据源状态字典
    """
    amazon_ready = bool(settings.rainforest_api_key)
    return {
        "data_mode": "real_only",
        "sources": {
            "google_suggest": {"enabled": True, "label": "Google 搜索联想", "real": True},
            "amazon_suggest": {"enabled": True, "label": "Amazon 自动补全", "real": True},
            "google_trends_rss": {"enabled": True, "label": "Google Trends RSS", "real": True},
            "reddit_pullpush": {"enabled": True, "label": "Reddit PullPush API", "real": True},
            "amazon_rainforest": {
                "enabled": amazon_ready,
                "label": "Amazon 差评与搜索 (Rainforest API)",
                "real": amazon_ready,
                "required_env": "RAINFOREST_API_KEY",
            },
        },
        "ready": amazon_ready,
        "message": (
            "全部真实数据源已就绪"
            if amazon_ready
            else "请在 backend/.env 配置 RAINFOREST_API_KEY 以获取真实 Amazon 差评与 ASIN"
        ),
    }
