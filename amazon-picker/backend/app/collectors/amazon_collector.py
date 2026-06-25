"""Amazon 差评采集器（Rainforest API 或手动导入真实差评）。"""

from typing import Any

from app.collectors.base import BaseCollector
from app.config import settings
from app.database import list_watch_asins
from app.services.manual_review_service import load_manual_reviews
from app.services.rainforest_client import RainforestApiError, RainforestClient


class AmazonCollector(BaseCollector):
    """采集 Amazon 差评：优先 Rainforest API，否则使用用户手动导入的真实差评。"""

    name = "amazon"

    async def collect_for_asins(self, asins: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集指定 ASIN 列表的差评。

        @param asins ASIN 列表
        @return (评论列表, 统计信息)
        """
        return await self._collect_asins(asins)

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集监控 ASIN 的差评。

        @return (评论列表, 统计信息)
        """
        asins = self._resolve_asins()
        return await self._collect_asins(asins)

    async def _collect_asins(self, asins: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """按 ASIN 列表采集差评。"""
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {
            "asins": [],
            "errors": [],
            "mode": "manual",
            "rainforest_count": 0,
            "manual_count": 0,
        }

        if not asins:
            stats["errors"].append("没有可采集的 ASIN，请先添加监控 ASIN 或配置 DEFAULT_ASINS")

        client = RainforestClient()
        if settings.rainforest_api_key:
            stats["mode"] = "rainforest+manual"
            for asin in asins:
                try:
                    items = await client.fetch_critical_reviews(asin)
                    reviews.extend(items)
                    stats["rainforest_count"] += len(items)
                    stats["asins"].append({"asin": asin, "count": len(items), "source": "rainforest"})
                except RainforestApiError as exc:
                    stats["errors"].append(f"{asin}: {exc}")
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"{asin}: {exc}")

        manual_reviews = load_manual_reviews(asins if asins else None)
        reviews.extend(manual_reviews)
        stats["manual_count"] = len(manual_reviews)

        manual_by_asin: dict[str, int] = {}
        for item in manual_reviews:
            asin = item.get("asin", "")
            manual_by_asin[asin] = manual_by_asin.get(asin, 0) + 1

        for asin, count in manual_by_asin.items():
            existing = next((entry for entry in stats["asins"] if entry["asin"] == asin), None)
            if existing:
                existing["count"] += count
                existing["source"] = "rainforest+manual"
            else:
                stats["asins"].append({"asin": asin, "count": count, "source": "manual"})

        if not settings.rainforest_api_key and not manual_reviews:
            stats["errors"].append(
                "未配置 Rainforest API，且暂无手动导入差评。请在页面粘贴亚马逊 1-3 星差评，或注册免费试用 Key。"
            )

        return reviews, stats

    def _resolve_asins(self) -> list[str]:
        """合并默认与监控 ASIN。"""
        watched = [item["asin"] for item in list_watch_asins()]
        defaults = [a.strip() for a in settings.default_asins.split(",") if a.strip()]
        merged: list[str] = []
        for asin in watched + defaults:
            upper = asin.upper()
            if upper not in merged:
                merged.append(upper)
        return merged
