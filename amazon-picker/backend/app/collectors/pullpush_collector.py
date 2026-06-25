"""PullPush API 采集真实 Reddit 评论。"""

from typing import Any

import httpx

from app.collectors.base import BaseCollector
from app.config import settings


class PullPushRedditCollector(BaseCollector):
    """通过 PullPush 接口获取 Reddit 真实帖子与评论。"""

    name = "reddit_pullpush"
    BASE_URL = "https://api.pullpush.io/reddit/search/comment/"

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集 Reddit 评论文本。

        @return (文本列表, 统计)
        """
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"subreddits": [], "errors": [], "mode": "pullpush"}
        subreddits = [s.strip() for s in settings.reddit_subreddits.split(",") if s.strip()]

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            for subreddit in subreddits:
                try:
                    response = await client.get(
                        self.BASE_URL,
                        params={
                            "subreddit": subreddit,
                            "size": 15,
                            "sort": "desc",
                            "sort_type": "created_utc",
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()
                    count = 0
                    for item in payload.get("data", []):
                        body = (item.get("body") or "").strip()
                        if len(body) < 40:
                            continue
                        reviews.append(
                            {
                                "source": "reddit_pullpush",
                                "source_id": item.get("id", ""),
                                "asin": "",
                                "title": f"r/{subreddit} comment",
                                "content": body[:2000],
                                "rating": None,
                            }
                        )
                        count += 1
                    stats["subreddits"].append({"name": subreddit, "count": count})
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"r/{subreddit}: {exc}")

        return reviews, stats
