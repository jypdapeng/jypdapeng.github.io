"""Amazon 差评采集器（仅 Rainforest API 真实数据）。"""

from typing import Any

from app.collectors.base import BaseCollector
from app.config import settings
from app.database import list_watch_asins
from app.services.rainforest_client import RainforestApiError, RainforestClient


class AmazonCollector(BaseCollector):
    """通过 Rainforest API 采集真实 Amazon 差评。"""

    name = "amazon_rainforest"

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
        """按 ASIN 列表调用 Rainforest API。"""
        client = RainforestClient()
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"asins": [], "errors": [], "mode": "rainforest"}

        if not asins:
            stats["errors"].append("没有可采集的 ASIN，请先配置 DEFAULT_ASINS 或添加监控 ASIN")
            return reviews, stats

        try:
            client.ensure_configured()
        except RainforestApiError as exc:
            stats["errors"].append(str(exc))
            return reviews, stats

        for asin in asins:
            try:
                items = await client.fetch_critical_reviews(asin)
                reviews.extend(items)
                stats["asins"].append({"asin": asin, "count": len(items)})
            except RainforestApiError as exc:
                stats["errors"].append(f"{asin}: {exc}")
            except Exception as exc:  # noqa: BLE001
                stats["errors"].append(f"{asin}: {exc}")

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
