"""风向分析与产品痛点聚合服务。"""

from typing import Any

from app.analyzers.pain_point_extractor import extract_pain_points
from app.collectors.amazon_collector import AmazonCollector
from app.collectors.amazon_suggest_collector import AmazonSuggestCollector
from app.collectors.google_trends_collector import GoogleTrendsCollector
from app.services.asin_discoverer import AsinDiscoverer


async def build_trend_insights() -> dict[str, Any]:
    """
    构建风向洞察：Google + Amazon 热度 → ASIN → 痛点。

    @return 风向报告
    """
    google_collector = GoogleTrendsCollector()
    amazon_collector = AmazonSuggestCollector()

    google_trends, google_stats = await google_collector.collect()
    amazon_trends, amazon_stats = await amazon_collector.collect()
    merged_keywords = _merge_trend_keywords(google_trends, amazon_trends)

    discoverer = AsinDiscoverer()
    products = await discoverer.discover(merged_keywords, limit=8)

    asin_list = [p["asin"] for p in products]
    reviews = await _fetch_reviews_for_asins(asin_list)
    products_with_pain = _attach_pain_points(products, reviews)

    return {
        "trend_keywords": merged_keywords[:15],
        "trend_products": products_with_pain,
        "source_stats": {
            "google": google_stats,
            "amazon_suggest": amazon_stats,
        },
    }


def _merge_trend_keywords(
    google_trends: list[dict[str, Any]], amazon_trends: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    合并 Google 与 Amazon 风向词并加权评分。

    @param google_trends Google 关键词
    @param amazon_trends Amazon 关键词
    @return 合并后的关键词
    """
    bucket: dict[str, dict[str, Any]] = {}

    for item in google_trends:
        key = item["keyword"].lower().strip()
        bucket[key] = {
            "keyword": item["keyword"],
            "google_score": item.get("score", 0),
            "amazon_score": 0,
            "score": int(item.get("score", 0) * 0.4),
            "sources": ["google"],
        }

    for item in amazon_trends:
        key = item["keyword"].lower().strip()
        if key not in bucket:
            bucket[key] = {
                "keyword": item["keyword"],
                "google_score": 0,
                "amazon_score": item.get("score", 0),
                "score": int(item.get("score", 0) * 0.6),
                "sources": ["amazon"],
            }
        else:
            bucket[key]["amazon_score"] = item.get("score", 0)
            bucket[key]["score"] = int(
                bucket[key].get("google_score", 0) * 0.4 + item.get("score", 0) * 0.6
            )
            if "amazon" not in bucket[key]["sources"]:
                bucket[key]["sources"].append("amazon")

    merged = sorted(bucket.values(), key=lambda x: x["score"], reverse=True)
    return merged


async def _fetch_reviews_for_asins(asins: list[str]) -> list[dict[str, Any]]:
    """
    拉取指定 ASIN 的差评样本。

    @param asins ASIN 列表
    @return 评论列表
    """
    if not asins:
        return []
    collector = AmazonCollector()
    reviews, _ = await collector.collect_for_asins(asins)
    return reviews


def _attach_pain_points(
    products: list[dict[str, Any]], reviews: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    为每个产品附加痛点分析。

    @param products 产品列表
    @param reviews 评论列表
    @return 带痛点的产品列表
    """
    enriched: list[dict[str, Any]] = []
    for product in products:
        asin = product["asin"]
        asin_reviews = [r for r in reviews if r.get("asin") == asin]
        pain_points = extract_pain_points(asin_reviews, top_n=5)
        complaints = [r.get("content", "")[:180] for r in asin_reviews[:3] if r.get("content")]
        enriched.append(
            {
                **product,
                "review_count": len(asin_reviews),
                "pain_points": pain_points,
                "sample_complaints": complaints,
            }
        )
    return enriched
