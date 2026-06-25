"""Amazon 评论采集器（支持 Rainforest API 与种子回退）。"""

import re
from typing import Any

import httpx

from app.collectors.base import BaseCollector
from app.config import settings
from app.database import list_watch_asins
from app.seed_data import SEED_REVIEWS


class AmazonCollector(BaseCollector):
    """采集 Amazon 差评或回退到种子数据。"""

    name = "amazon"

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集 Amazon 评论。

        @return (评论列表, 统计信息)
        """
        asins = self._resolve_asins()
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"asins": [], "errors": [], "mode": "direct"}

        if settings.rainforest_api_key:
            stats["mode"] = "rainforest"
            reviews, api_stats = await self._collect_via_rainforest(asins)
            stats.update(api_stats)
        else:
            reviews, direct_stats = await self._collect_direct(asins)
            stats.update(direct_stats)

        if not reviews:
            seed_subset = [r for r in SEED_REVIEWS if r["source"] == "amazon_seed"]
            reviews.extend(seed_subset)
            stats["fallback_seed"] = len(seed_subset)
            stats["errors"].append("Amazon 直连被拦截，已使用内置种子差评样本")

        return reviews, stats

    def _resolve_asins(self) -> list[str]:
        """合并默认与监控 ASIN。"""
        watched = [item["asin"] for item in list_watch_asins()]
        defaults = [a.strip() for a in settings.default_asins.split(",") if a.strip()]
        merged: list[str] = []
        for asin in watched + defaults:
            if asin not in merged:
                merged.append(asin.upper())
        return merged

    async def _collect_direct(self, asins: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """尝试直接抓取评论页。"""
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"asins": [], "errors": []}

        async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
            for asin in asins:
                url = (
                    f"https://www.amazon.com/product-reviews/{asin}"
                    "?filterByStar=critical&reviewerType=all_reviews&pageNumber=1"
                )
                try:
                    response = await client.get(
                        url,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36"
                            ),
                            "Accept-Language": "en-US,en;q=0.9",
                        },
                    )
                    if response.status_code != 200 or len(response.text) < 5000:
                        stats["errors"].append(f"{asin}: 页面抓取失败或被拦截")
                        continue

                    parsed = self._parse_review_html(response.text, asin)
                    reviews.extend(parsed)
                    stats["asins"].append({"asin": asin, "count": len(parsed)})
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"{asin}: {exc}")

        return reviews, stats

    async def _collect_via_rainforest(
        self, asins: list[str]
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """通过 Rainforest API 获取评论。"""
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"asins": [], "errors": []}

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            for asin in asins:
                try:
                    response = await client.get(
                        "https://api.rainforestapi.com/request",
                        params={
                            "api_key": settings.rainforest_api_key,
                            "type": "reviews",
                            "amazon_domain": "amazon.com",
                            "asin": asin,
                            "review_stars": "1,2,3",
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()
                    items = payload.get("reviews", [])
                    count = 0
                    for item in items[:20]:
                        body = item.get("body", "")
                        if len(body) < 20:
                            continue
                        reviews.append(
                            {
                                "source": "amazon",
                                "source_id": item.get("id", ""),
                                "asin": asin,
                                "title": item.get("title", "")[:200],
                                "content": body[:2000],
                                "rating": item.get("rating"),
                            }
                        )
                        count += 1
                    stats["asins"].append({"asin": asin, "count": count})
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"{asin}: {exc}")

        return reviews, stats

    def _parse_review_html(self, html: str, asin: str) -> list[dict[str, Any]]:
        """
        从评论页 HTML 提取差评文本。

        @param html 页面 HTML
        @param asin 商品 ASIN
        @return 评论列表
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        reviews: list[dict[str, Any]] = []

        for block in soup.select('[data-hook="review"]'):
            title_el = block.select_one('[data-hook="review-title"]')
            body_el = block.select_one('[data-hook="review-body"]')
            rating_el = block.select_one('[data-hook="review-star-rating"]')
            if not body_el:
                continue
            title = title_el.get_text(" ", strip=True) if title_el else ""
            content = body_el.get_text(" ", strip=True)
            rating = None
            if rating_el:
                match = re.search(r"(\d)", rating_el.get_text())
                if match:
                    rating = int(match.group(1))
            reviews.append(
                {
                    "source": "amazon",
                    "source_id": "",
                    "asin": asin,
                    "title": title[:200],
                    "content": content[:2000],
                    "rating": rating,
                }
            )
        return reviews
