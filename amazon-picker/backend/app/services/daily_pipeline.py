"""每日采集编排服务。"""

from datetime import date
from typing import Any

from app.analyzers.keyword_expander import expand_keywords
from app.analyzers.pain_point_extractor import extract_pain_points
from app.analyzers.product_recommender import recommend_products
from app.collectors.amazon_collector import AmazonCollector
from app.collectors.reddit_collector import RedditCollector
from app.database import save_daily_report, save_raw_reviews
from app.seed_data import SEED_REVIEWS


async def run_daily_collection(use_seed_on_empty: bool = True) -> dict[str, Any]:
    """
    执行每日采集并生成报告。

    @param use_seed_on_empty 无数据时是否注入种子
    @return 日报内容
    """
    collectors = [AmazonCollector(), RedditCollector()]
    all_reviews: list[dict[str, Any]] = []
    source_stats: dict[str, Any] = {}

    for collector in collectors:
        reviews, stats = await collector.collect()
        all_reviews.extend(reviews)
        source_stats[collector.name] = stats

    if use_seed_on_empty and len(all_reviews) < 5:
        reddit_seed = [r for r in SEED_REVIEWS if r["source"] in {"reddit_seed", "community_seed"}]
        all_reviews.extend(reddit_seed)
        source_stats["seed"] = {"count": len(reddit_seed), "reason": "社区种子补充"}

    save_raw_reviews(all_reviews)

    pain_points = extract_pain_points(all_reviews)
    keywords = expand_keywords(pain_points)
    products = recommend_products(pain_points)

    report = {
        "report_date": date.today().isoformat(),
        "pain_points": pain_points,
        "keywords": keywords,
        "products": products,
        "summary": _build_summary(pain_points, products, len(all_reviews)),
        "source_stats": source_stats,
    }
    save_daily_report(report)
    return report


def _build_summary(pain_points: list[dict], products: list[dict], review_count: int) -> str:
    """生成日报摘要。"""
    if not pain_points:
        return f"今日采集 {review_count} 条文本，暂未识别显著痛点。"
    top = pain_points[0]
    best = products[0] if products else None
    product_hint = f"建议关注：{best['direction']}" if best else "建议继续扩展监控词"
    return (
        f"今日采集 {review_count} 条用户反馈，最高频痛点为「{top['theme_zh']}」"
        f"（{top['count']} 次）。{product_hint}。"
    )
