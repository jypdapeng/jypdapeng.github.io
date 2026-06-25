"""根据热门关键词通过 Rainforest 搜索发现真实 ASIN。"""

from typing import Any

from app.services.rainforest_client import RainforestApiError, RainforestClient


class AsinDiscoverer:
    """关键词 → 真实 ASIN 发现服务。"""

    async def discover(self, trend_keywords: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
        """
        根据风向关键词发现 ASIN。

        @param trend_keywords 风向关键词列表
        @param limit 返回产品数上限
        @return 产品列表（含 ASIN）
        """
        client = RainforestClient()
        discovered: list[dict[str, Any]] = []
        seen_asins: set[str] = set()

        try:
            client.ensure_configured()
        except RainforestApiError:
            return []

        for trend in trend_keywords:
            keyword = trend["keyword"]
            try:
                asin_items = await client.search_products(keyword, limit=3)
            except RainforestApiError:
                continue

            for item in asin_items:
                asin = item["asin"]
                if asin in seen_asins:
                    continue
                seen_asins.add(asin)
                discovered.append(
                    {
                        "keyword": keyword,
                        "trend_score": trend.get("score", 0),
                        "trend_sources": trend.get("sources", [trend.get("source", "")]),
                        "asin": asin,
                        "title": item.get("title", ""),
                        "price": item.get("price"),
                        "rating": item.get("rating"),
                        "ratings_total": item.get("ratings_total"),
                        "discovery_method": "rainforest_search",
                    }
                )
                if len(discovered) >= limit:
                    return discovered
        return discovered
