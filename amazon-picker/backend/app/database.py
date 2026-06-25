"""SQLite 数据库访问层。"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from app.config import settings


def _connect() -> sqlite3.Connection:
    """创建数据库连接。"""
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库连接上下文管理器。"""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """初始化数据表结构。"""
    settings.database_path
    from pathlib import Path

    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT,
                asin TEXT,
                title TEXT,
                content TEXT NOT NULL,
                rating INTEGER,
                collected_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL UNIQUE,
                pain_points_json TEXT NOT NULL,
                keywords_json TEXT NOT NULL,
                products_json TEXT NOT NULL,
                summary TEXT,
                source_stats_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS watch_asins (
                asin TEXT PRIMARY KEY,
                label TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        _migrate_reports_table(conn)


def _migrate_reports_table(conn: sqlite3.Connection) -> None:
    """为日报表增加风向字段（兼容旧库）。"""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(daily_reports)").fetchall()}
    if "trends_json" not in columns:
        conn.execute("ALTER TABLE daily_reports ADD COLUMN trends_json TEXT DEFAULT '{}'")
    if "trend_products_json" not in columns:
        conn.execute("ALTER TABLE daily_reports ADD COLUMN trend_products_json TEXT DEFAULT '[]'")


def save_raw_reviews(reviews: list[dict[str, Any]]) -> int:
    """
    批量保存原始评论/文本。

    @param reviews 评论列表
    @return 写入条数
    """
    if not reviews:
        return 0
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        conn.executemany(
            """
            INSERT INTO raw_reviews (source, source_id, asin, title, content, rating, collected_at)
            VALUES (:source, :source_id, :asin, :title, :content, :rating, :collected_at)
            """,
            [{**item, "collected_at": now} for item in reviews],
        )
    return len(reviews)


def save_daily_report(report: dict[str, Any]) -> None:
    """
    保存或更新每日报告。

    @param report 报告字典
    """
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO daily_reports (
                report_date, pain_points_json, keywords_json, products_json,
                summary, source_stats_json, trends_json, trend_products_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(report_date) DO UPDATE SET
                pain_points_json = excluded.pain_points_json,
                keywords_json = excluded.keywords_json,
                products_json = excluded.products_json,
                summary = excluded.summary,
                source_stats_json = excluded.source_stats_json,
                trends_json = excluded.trends_json,
                trend_products_json = excluded.trend_products_json,
                created_at = excluded.created_at
            """,
            (
                report["report_date"],
                json.dumps(report["pain_points"], ensure_ascii=False),
                json.dumps(report["keywords"], ensure_ascii=False),
                json.dumps(report["products"], ensure_ascii=False),
                report.get("summary", ""),
                json.dumps(report.get("source_stats", {}), ensure_ascii=False),
                json.dumps(report.get("trend_keywords", []), ensure_ascii=False),
                json.dumps(report.get("trend_products", []), ensure_ascii=False),
                datetime.utcnow().isoformat(),
            ),
        )


def get_report_by_date(report_date: str) -> dict[str, Any] | None:
    """
    按日期获取报告。

    @param report_date 日期 YYYY-MM-DD
    @return 报告或 None
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM daily_reports WHERE report_date = ?", (report_date,)
        ).fetchone()
    if not row:
        return None
    return _row_to_report(row)


def get_latest_report() -> dict[str, Any] | None:
    """
    获取最新日报。

    @return 最新报告或 None
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM daily_reports ORDER BY report_date DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    return _row_to_report(row)


def list_reports(limit: int = 30) -> list[dict[str, Any]]:
    """
    列出历史报告。

    @param limit 条数上限
    @return 报告列表
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_reports ORDER BY report_date DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_report(row) for row in rows]


def get_recent_raw_reviews(hours: int = 48) -> list[dict[str, Any]]:
    """
    获取最近采集的原始文本。

    @param hours 时间窗口（小时）
    @return 评论列表
    """
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM raw_reviews
            WHERE datetime(collected_at) >= datetime('now', ?)
            ORDER BY collected_at DESC
            """,
            (f"-{hours} hours",),
        ).fetchall()
    return [dict(row) for row in rows]


def list_watch_asins() -> list[dict[str, str]]:
    """获取监控 ASIN 列表。"""
    with get_db() as conn:
        rows = conn.execute("SELECT asin, label FROM watch_asins ORDER BY created_at").fetchall()
    return [dict(row) for row in rows]


def add_watch_asin(asin: str, label: str = "") -> None:
    """添加监控 ASIN。"""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO watch_asins (asin, label, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(asin) DO UPDATE SET label = excluded.label
            """,
            (asin.upper(), label, datetime.utcnow().isoformat()),
        )


def _row_to_report(row: sqlite3.Row) -> dict[str, Any]:
    """将数据库行转为报告字典。"""
    keys = row.keys()
    trends_raw = row["trends_json"] if "trends_json" in keys else "[]"
    products_raw = row["trend_products_json"] if "trend_products_json" in keys else "[]"
    return {
        "report_date": row["report_date"],
        "pain_points": json.loads(row["pain_points_json"]),
        "keywords": json.loads(row["keywords_json"]),
        "products": json.loads(row["products_json"]),
        "summary": row["summary"],
        "source_stats": json.loads(row["source_stats_json"]),
        "trend_keywords": json.loads(trends_raw) if trends_raw else [],
        "trend_products": json.loads(products_raw) if products_raw else [],
        "created_at": row["created_at"],
    }
