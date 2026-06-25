"""Google 搜索热度采集器（联想词 + Trends RSS）。"""

import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from app.collectors.base import BaseCollector
from app.config import settings

PRODUCT_INTENT_WORDS = {
    "pillow",
    "cover",
    "holder",
    "kit",
    "must",
    "haves",
    "equipment",
    "shower",
    "ice",
    "crutch",
    "walker",
    "reacher",
    "grabber",
    "stool",
    "bolster",
    "elevation",
    "recovery",
    "brace",
    "support",
    "wrap",
    "pack",
}

SKIP_WORDS = {
    "time",
    "timeline",
    "tips",
    "exercises",
    "video",
    "reddit",
    "cost",
    "insurance",
}


class GoogleTrendsCollector(BaseCollector):
    """通过 Google 联想词与 Trends RSS 获取搜索风向。"""

    name = "google_trends"

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集 Google 搜索风向。

        @return (风向关键词列表, 统计)
        """
        seeds = [s.strip() for s in settings.trend_seed_keywords.split(",") if s.strip()]
        trends: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"seeds": len(seeds), "errors": []}

        async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
            for seed in seeds:
                try:
                    suggestions = await self._fetch_google_suggest(client, seed)
                    for idx, phrase in enumerate(suggestions[:10]):
                        if not self._is_product_intent(phrase):
                            continue
                        score = max(10, 100 - idx * 9)
                        trends.append(
                            {
                                "keyword": phrase,
                                "source": "google_suggest",
                                "seed": seed,
                                "score": score,
                                "rank": idx + 1,
                            }
                        )
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"google:{seed}: {exc}")

            try:
                rss_trends = await self._fetch_trends_rss(client, seeds)
                trends.extend(rss_trends)
                stats["rss_matched"] = len(rss_trends)
            except Exception as exc:  # noqa: BLE001
                stats["errors"].append(f"rss: {exc}")

        merged = self._merge_scores(trends)
        stats["total_keywords"] = len(merged)
        return merged, stats

    async def _fetch_google_suggest(self, client: httpx.AsyncClient, query: str) -> list[str]:
        """
        获取 Google 搜索联想词。

        @param client HTTP 客户端
        @param query 种子词
        @return 联想词列表
        """
        response = await client.get(
            "https://suggestqueries.google.com/complete/search",
            params={"client": "firefox", "hl": "en", "q": query},
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        payload = response.json()
        if len(payload) < 2:
            return []
        return [str(item) for item in payload[1] if isinstance(item, str)]

    async def _fetch_trends_rss(
        self, client: httpx.AsyncClient, seeds: list[str]
    ) -> list[dict[str, Any]]:
        """
        从 Google Trends RSS 中筛选与种子词相关的趋势。

        @param client HTTP 客户端
        @param seeds 种子词列表
        @return 趋势关键词
        """
        response = await client.get(
            f"https://trends.google.com/trending/rss?geo={settings.google_trends_geo}",
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        seed_tokens = {token for seed in seeds for token in seed.lower().split()}

        results: list[dict[str, Any]] = []
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip().lower()
            traffic = item.findtext("{https://trends.google.com/trending/rss}approx_traffic") or ""
            if not title:
                continue
            if not any(token in title for token in seed_tokens):
                continue
            if not self._is_product_intent(title):
                continue
            traffic_score = self._parse_traffic(traffic)
            results.append(
                {
                    "keyword": title,
                    "source": "google_trends_rss",
                    "seed": "rss",
                    "score": traffic_score,
                    "rank": 1,
                    "traffic": traffic,
                }
            )
        return results

    def _is_product_intent(self, phrase: str) -> bool:
        """判断是否为产品相关搜索意图。"""
        lower = phrase.lower()
        if any(skip in lower for skip in SKIP_WORDS):
            return False
        return any(word in lower for word in PRODUCT_INTENT_WORDS)

    def _parse_traffic(self, traffic: str) -> int:
        """解析 Trends RSS 流量文本。"""
        match = re.search(r"(\d+)", traffic.replace(",", ""))
        if not match:
            return 40
        value = int(match.group(1))
        if value >= 100000:
            return 95
        if value >= 10000:
            return 85
        if value >= 1000:
            return 70
        return 50

    def _merge_scores(self, trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """合并同源关键词并累计热度分。"""
        bucket: dict[str, dict[str, Any]] = {}
        for item in trends:
            key = item["keyword"].lower().strip()
            if key not in bucket:
                bucket[key] = {**item, "sources": [item["source"]], "score": item["score"]}
                continue
            bucket[key]["score"] = min(100, bucket[key]["score"] + int(item["score"] * 0.35))
            if item["source"] not in bucket[key]["sources"]:
                bucket[key]["sources"].append(item["source"])

        merged = sorted(bucket.values(), key=lambda x: x["score"], reverse=True)
        return merged[:20]
