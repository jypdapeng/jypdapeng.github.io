"""根据热门关键词自动发现竞品 ASIN。"""

from typing import Any

import httpx

from app.config import settings
from app.data.keyword_asin_map import lookup_asins


class AsinDiscoverer:
    """关键词 → ASIN 发现服务。"""

    async def discover(self, trend_keywords: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
        """
        根据风向关键词发现 ASIN。

        @param trend_keywords 风向关键词列表
        @param limit 返回产品数上限
        @return 产品列表（含 ASIN）
        """
        discovered: list[dict[str, Any]] = []
        seen_asins: set[str] = set()

        for trend in trend_keywords:
            keyword = trend["keyword"]
            asin_items = await self._resolve_asins(keyword)
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
                        "discovery_method": item.get("method", "map"),
                    }
                )
                if len(discovered) >= limit:
                    return discovered
        return discovered

    async def _resolve_asins(self, keyword: str) -> list[dict[str, Any]]:
        """
        解析单个关键词对应的 ASIN。

        @param keyword 关键词
        @return ASIN 列表
        """
        if settings.rainforest_api_key:
            api_items = await self._search_rainforest(keyword)
            if api_items:
                return api_items

        mapped = lookup_asins(keyword)
        if mapped:
            return [{**item, "method": "keyword_map"} for item in mapped]

        return []

    async def _search_rainforest(self, keyword: str) -> list[dict[str, Any]]:
        """
        通过 Rainforest API 搜索 ASIN。

        @param keyword 关键词
        @return ASIN 列表
        """
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            try:
                response = await client.get(
                    "https://api.rainforestapi.com/request",
                    params={
                        "api_key": settings.rainforest_api_key,
                        "type": "search",
                        "amazon_domain": "amazon.com",
                        "search_term": keyword,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                results: list[dict[str, Any]] = []
                for item in payload.get("search_results", [])[:3]:
                    asin = item.get("asin")
                    if not asin:
                        continue
                    results.append(
                        {
                            "asin": asin,
                            "title": item.get("title", "")[:120],
                            "method": "rainforest_search",
                        }
                    )
                return results
            except Exception:  # noqa: BLE001
                return []
