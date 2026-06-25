"""Amazon 搜索联想词采集器。"""

from typing import Any

import httpx

from app.collectors.base import BaseCollector
from app.config import settings


class AmazonSuggestCollector(BaseCollector):
    """通过 Amazon Autocomplete API 获取买家真实搜索词。"""

    name = "amazon_suggest"

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集 Amazon 联想词风向。

        @return (关键词列表, 统计)
        """
        seeds = [s.strip() for s in settings.trend_seed_keywords.split(",") if s.strip()]
        trends: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"seeds": len(seeds), "errors": []}

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            for seed in seeds:
                try:
                    suggestions = await self._fetch_suggestions(client, seed)
                    for idx, phrase in enumerate(suggestions[:10]):
                        score = max(10, 100 - idx * 8)
                        trends.append(
                            {
                                "keyword": phrase,
                                "source": "amazon_suggest",
                                "seed": seed,
                                "score": score,
                                "rank": idx + 1,
                            }
                        )
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"amazon:{seed}: {exc}")

        merged = self._merge_keywords(trends)
        stats["total_keywords"] = len(merged)
        return merged, stats

    async def _fetch_suggestions(self, client: httpx.AsyncClient, prefix: str) -> list[str]:
        """
        调用 Amazon 自动补全接口。

        @param client HTTP 客户端
        @param prefix 前缀词
        @return 联想词
        """
        response = await client.get(
            "https://completion.amazon.com/api/2017/suggestions",
            params={
                "alias": "aps",
                "mid": settings.amazon_marketplace_id,
                "prefix": prefix,
            },
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        payload = response.json()
        suggestions = payload.get("suggestions", [])
        return [item.get("value", "") for item in suggestions if item.get("value")]

    def _merge_keywords(self, trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """关键词去重合并。"""
        bucket: dict[str, dict[str, Any]] = {}
        for item in trends:
            key = item["keyword"].lower().strip()
            if key not in bucket or item["score"] > bucket[key]["score"]:
                bucket[key] = item
        return sorted(bucket.values(), key=lambda x: x["score"], reverse=True)[:20]
