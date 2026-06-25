"""每日采集编排服务（仅真实数据源）。"""

from datetime import date
from typing import Any

from app.analyzers.keyword_expander import expand_keywords
from app.analyzers.pain_point_extractor import extract_pain_points
from app.analyzers.product_recommender import recommend_products
from app.collectors.amazon_collector import AmazonCollector
from app.collectors.pullpush_collector import PullPushRedditCollector
from app.database import save_daily_report, save_raw_reviews
from app.services.trend_service import build_trend_insights


async def run_daily_collection() -> dict[str, Any]:
    """
    执行每日采集并生成报告（不使用任何种子/样本回退）。

    @return 日报内容
    """
    collectors = [AmazonCollector(), PullPushRedditCollector()]
    all_reviews: list[dict[str, Any]] = []
    source_stats: dict[str, Any] = {"data_mode": "real_only"}

    for collector in collectors:
        reviews, stats = await collector.collect()
        all_reviews.extend(reviews)
        source_stats[collector.name] = stats

    save_raw_reviews(all_reviews)

    pain_points = extract_pain_points(all_reviews)
    keywords = expand_keywords(pain_points)
    products = recommend_products(pain_points)

    trend_insights = await build_trend_insights()
    source_stats["trends"] = trend_insights.get("source_stats", {})

    report = {
        "report_date": date.today().isoformat(),
        "pain_points": pain_points,
        "keywords": keywords,
        "products": products,
        "trend_keywords": trend_insights.get("trend_keywords", []),
        "trend_products": trend_insights.get("trend_products", []),
        "summary": _build_summary(
            pain_points, products, len(all_reviews), trend_insights.get("trend_keywords", [])
        ),
        "source_stats": source_stats,
        "data_mode": "real_only",
    }
    save_daily_report(report)
    return report


def _build_summary(
    pain_points: list[dict],
    products: list[dict],
    review_count: int,
    trend_keywords: list[dict] | None = None,
) -> str:
    """生成日报摘要。"""
    if not pain_points and not trend_keywords:
        return f"今日采集 {review_count} 条真实反馈；若 Amazon 数据为空，请检查 RAINFOREST_API_KEY。"
    top = pain_points[0] if pain_points else None
    best = products[0] if products else None
    product_hint = f"建议关注：{best['direction']}" if best else ""
    trend_hint = ""
    if trend_keywords:
        trend_hint = f"当前最热搜索词：「{trend_keywords[0]['keyword']}」。"
    if top:
        return (
            f"今日采集 {review_count} 条真实用户反馈，最高频痛点「{top['theme_zh']}」"
            f"（{top['count']} 次）。{trend_hint}{product_hint}"
        )
    return f"今日已更新真实搜索风向。{trend_hint}{product_hint}"
