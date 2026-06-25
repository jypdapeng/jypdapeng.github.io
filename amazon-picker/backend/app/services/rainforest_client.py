"""Rainforest API 客户端（Amazon 真实数据来源）。"""

from typing import Any

import httpx

from app.config import settings


class RainforestApiError(Exception):
    """Rainforest API 调用异常。"""


class RainforestClient:
    """封装 Rainforest API 的搜索与评论请求。"""

    BASE_URL = "https://api.rainforestapi.com/request"

    def __init__(self, api_key: str | None = None) -> None:
        """
        初始化客户端。

        @param api_key API 密钥，默认读取配置
        """
        self.api_key = api_key or settings.rainforest_api_key

    def ensure_configured(self) -> None:
        """校验 API Key 是否已配置。"""
        if not self.api_key:
            raise RainforestApiError(
                "未配置 RAINFOREST_API_KEY。请在 backend/.env 填入真实 API Key 后才能获取 Amazon 数据。"
            )

    async def search_products(self, search_term: str, limit: int = 3) -> list[dict[str, Any]]:
        """
        按关键词搜索 Amazon 商品。

        @param search_term 搜索词
        @param limit 返回数量
        @return 商品列表
        """
        self.ensure_configured()
        payload = await self._request(
            {
                "type": "search",
                "amazon_domain": "amazon.com",
                "search_term": search_term,
                "page": 1,
            }
        )
        results: list[dict[str, Any]] = []
        for item in payload.get("search_results", [])[:limit]:
            asin = item.get("asin")
            if not asin:
                continue
            results.append(
                {
                    "asin": asin,
                    "title": (item.get("title") or "")[:200],
                    "price": item.get("price", {}).get("value"),
                    "rating": item.get("rating"),
                    "ratings_total": item.get("ratings_total"),
                }
            )
        return results

    async def fetch_critical_reviews(self, asin: str, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取指定 ASIN 的差评（1-3 星）。

        @param asin 商品 ASIN
        @param limit 最大条数
        @return 评论列表
        """
        self.ensure_configured()
        payload = await self._request(
            {
                "type": "reviews",
                "amazon_domain": "amazon.com",
                "asin": asin,
                "review_stars": "all_critical",
                "sort_by": "recent",
                "page": 1,
            }
        )
        reviews: list[dict[str, Any]] = []
        for item in payload.get("reviews", [])[:limit]:
            body = (item.get("body") or "").strip()
            if len(body) < 15:
                continue
            reviews.append(
                {
                    "source": "amazon_rainforest",
                    "source_id": str(item.get("id", "")),
                    "asin": asin,
                    "title": (item.get("title") or "")[:200],
                    "content": body[:2000],
                    "rating": item.get("rating"),
                    "date": item.get("date", {}).get("raw", ""),
                }
            )
        return reviews

    async def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        发送 Rainforest API 请求。

        @param params 查询参数
        @return 响应 JSON
        """
        query = {"api_key": self.api_key, **params}
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(self.BASE_URL, params=query)
            response.raise_for_status()
            payload = response.json()

        request_info = payload.get("request_info", {})
        if not request_info.get("success", False):
            message = request_info.get("message", "Rainforest API 请求失败")
            raise RainforestApiError(message)
        return payload
