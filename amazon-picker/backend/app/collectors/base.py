"""数据采集器基类。"""

from abc import ABC, abstractmethod
from typing import Any


class BaseCollector(ABC):
    """采集器抽象基类。"""

    name: str = "base"

    @abstractmethod
    async def collect(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        执行采集。

        @return (评论列表, 采集统计)
        """
