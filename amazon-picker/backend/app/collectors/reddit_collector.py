"""Reddit 社区文本采集器。"""

from typing import Any

import httpx

from app.collectors.base import BaseCollector
from app.config import settings


class RedditCollector(BaseCollector):
    """从 Reddit JSON 接口采集帖子与评论。"""

    name = "reddit"

    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        采集 Reddit 帖子标题与正文。

        @return (文本列表, 统计信息)
        """
        reviews: list[dict[str, Any]] = []
        stats: dict[str, Any] = {"subreddits": [], "errors": []}
        subreddits = [s.strip() for s in settings.reddit_subreddits.split(",") if s.strip()]

        async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=15"
                try:
                    response = await client.get(
                        url,
                        headers={
                            "User-Agent": settings.user_agent,
                            "Accept": "application/json",
                        },
                    )
                    if response.status_code != 200 or "application/json" not in response.headers.get(
                        "content-type", ""
                    ):
                        stats["errors"].append(f"r/{subreddit}: HTTP {response.status_code}")
                        continue

                    payload = response.json()
                    children = payload.get("data", {}).get("children", [])
                    count = 0
                    for child in children:
                        data = child.get("data", {})
                        title = data.get("title", "")
                        body = data.get("selftext", "")
                        content = f"{title}. {body}".strip()
                        if len(content) < 30:
                            continue
                        reviews.append(
                            {
                                "source": "reddit",
                                "source_id": data.get("id", ""),
                                "asin": "",
                                "title": title[:200],
                                "content": content[:2000],
                                "rating": None,
                            }
                        )
                        count += 1
                    stats["subreddits"].append({"name": subreddit, "count": count})
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"r/{subreddit}: {exc}")

        return reviews, stats
