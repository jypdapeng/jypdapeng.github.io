"""根据热门关键词发现 ASIN（Rainforest 或监控列表）。"""

from typing import Any

from app.config import settings
from app.database import list_watch_asins
from app.services.rainforest_client import RainforestApiError, RainforestClient


class AsinDiscoverer:
    """关键词 → ASIN 发现服务。"""

    async def discover(self, trend_keywords: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
        """
        根据风向关键词发现 ASIN。

        @param trend_keywords 风向关键词列表
        @param limit 返回产品数上限
        @return 产品列表（含 ASIN）
        """
        if settings.rainforest_api_key:
            products = await self._discover_via_rainforest(trend_keywords, limit)
            if products:
                return products
        return self._discover_from_watchlist(trend_keywords, limit)

    async def _discover_via_rainforest(
        self, trend_keywords: list[dict[str, Any]], limit: int
    ) -> list[dict[str, Any]]:
        """
        通过 Rainforest Search API 发现 ASIN。

        @param trend_keywords 风向关键词
        @param limit 数量上限
        @return 产品列表
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

    def _discover_from_watchlist(
        self, trend_keywords: list[dict[str, Any]], limit: int
    ) -> list[dict[str, Any]]:
        """
        无 Rainforest 时，使用监控 ASIN 列表匹配风向词。

        @param trend_keywords 风向关键词
        @param limit 数量上限
        @return 产品列表
        """
        watch_items = list_watch_asins()
        defaults = [
            {"asin": asin.strip().upper(), "label": ""}
            for asin in settings.default_asins.split(",")
            if asin.strip()
        ]
        merged: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in watch_items + defaults:
            asin = item["asin"].upper()
            if asin in seen:
                continue
            seen.add(asin)
            merged.append({"asin": asin, "label": item.get("label", "")})

        if not merged:
            return []

        top_keyword = trend_keywords[0]["keyword"] if trend_keywords else "监控竞品"
        top_score = trend_keywords[0].get("score", 0) if trend_keywords else 0
        top_sources = trend_keywords[0].get("sources", []) if trend_keywords else []

        discovered: list[dict[str, Any]] = []
        for item in merged[:limit]:
            keyword = self._match_keyword(item, trend_keywords) or top_keyword
            trend = next((t for t in trend_keywords if t["keyword"] == keyword), None)
            discovered.append(
                {
                    "keyword": keyword,
                    "trend_score": trend.get("score", top_score) if trend else top_score,
                    "trend_sources": trend.get("sources", top_sources) if trend else top_sources,
                    "asin": item["asin"],
                    "title": item.get("label") or f"监控竞品 {item['asin']}",
                    "price": None,
                    "rating": None,
                    "ratings_total": None,
                    "discovery_method": "watchlist",
                }
            )
        return discovered

    def _match_keyword(self, item: dict[str, str], trend_keywords: list[dict[str, Any]]) -> str | None:
        """
        根据 ASIN 备注匹配最相关的风向词。

        @param item 监控 ASIN
        @param trend_keywords 风向关键词
        @return 匹配到的关键词或 None
        """
        label = (item.get("label") or "").lower()
        if not label:
            return None
        for trend in trend_keywords:
            keyword = trend["keyword"].lower()
            if keyword in label or any(token in label for token in keyword.split() if len(token) > 3):
                return trend["keyword"]
        return None
