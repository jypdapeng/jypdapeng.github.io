"""FastAPI 应用入口。"""

import logging
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.analyzers.keyword_expander import expand_keywords
from app.analyzers.pain_point_extractor import analyze_free_text
from app.analyzers.product_recommender import recommend_products
from app.config import FRONTEND_DIR, settings
from app.database import (
    add_watch_asin,
    count_manual_reviews_by_asin,
    get_latest_report,
    get_report_by_date,
    init_db,
    list_reports,
    list_watch_asins,
)
from app.services.manual_review_service import import_manual_reviews
from app.scheduler import start_scheduler
from app.services.daily_pipeline import run_daily_collection
from app.services.data_source_status import get_data_source_status
from app.services.trend_service import build_trend_insights

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyzeTextRequest(BaseModel):
    """文本分析请求体。"""

    text: str = Field(..., min_length=20, description="粘贴的差评或社区吐槽")


class WatchAsinRequest(BaseModel):
    """监控 ASIN 请求体。"""

    asin: str = Field(..., min_length=10, max_length=10)
    label: str = ""


class ImportReviewsRequest(BaseModel):
    """手动导入差评请求体。"""

    asin: str = Field(..., min_length=10, max_length=10)
    text: str = Field(..., min_length=20, description="从亚马逊页面复制的 1-3 星差评")
    rating: int | None = Field(default=None, ge=1, le=3)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期：初始化数据库与调度器。"""
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    init_db()
    start_scheduler()

    latest = get_latest_report()
    if not latest:
        logger.info("Generating initial real-data report...")
        await run_daily_collection()

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    """健康检查。"""
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/data-sources/status")
async def data_sources_status() -> dict:
    """返回真实数据源配置状态。"""
    return get_data_source_status()


@app.get("/api/report/latest")
async def report_latest() -> dict:
    """获取最新日报。"""
    report = get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="暂无日报，请先执行采集")
    return report


@app.get("/api/report/today")
async def report_today() -> dict:
    """获取今日日报。"""
    report = get_report_by_date(date.today().isoformat())
    if not report:
        report = get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="暂无日报")
    return report


@app.get("/api/reports")
async def reports(limit: int = 30) -> dict:
    """历史日报列表。"""
    return {"items": list_reports(limit=limit)}


@app.post("/api/collect/run")
async def collect_run() -> dict:
    """手动触发采集。"""
    report = await run_daily_collection()
    return {"message": "采集完成", "report": report}


@app.get("/api/trends/latest")
async def trends_latest() -> dict:
    """获取最新风向洞察（关键词 + ASIN + 痛点）。"""
    report = get_latest_report()
    if not report:
        insights = await build_trend_insights()
        return insights
    return {
        "trend_keywords": report.get("trend_keywords", []),
        "trend_products": report.get("trend_products", []),
        "report_date": report.get("report_date"),
        "source_stats": report.get("source_stats", {}).get("trends", {}),
    }


@app.post("/api/trends/refresh")
async def trends_refresh() -> dict:
    """立即刷新 Google/Amazon 风向并返回。"""
    insights = await build_trend_insights()
    return {"message": "风向已刷新", **insights}


@app.post("/api/analyze/text")
async def analyze_text(payload: AnalyzeTextRequest) -> dict:
    """
    分析用户粘贴的差评/吐槽文本。

    @param payload 请求体
    @return 痛点、关键词、选品建议
    """
    pain_points = analyze_free_text(payload.text)
    keywords = expand_keywords(pain_points)
    products = recommend_products(pain_points)
    return {
        "pain_points": pain_points,
        "keywords": keywords,
        "products": products,
    }


@app.get("/api/watch-asins")
async def watch_asins() -> dict:
    """监控 ASIN 列表。"""
    return {"items": list_watch_asins()}


@app.post("/api/watch-asins")
async def add_asin(payload: WatchAsinRequest) -> dict:
    """添加监控 ASIN。"""
    asin = payload.asin.upper()
    if not asin.isalnum():
        raise HTTPException(status_code=400, detail="ASIN 格式无效")
    add_watch_asin(asin, payload.label)
    return {"message": "已添加", "asin": asin}


@app.post("/api/reviews/import")
async def import_reviews(payload: ImportReviewsRequest) -> dict:
    """
    导入手动复制的真实 Amazon 差评。

    @param payload 请求体
    @return 导入结果
    """
    asin = payload.asin.upper()
    if not asin.isalnum():
        raise HTTPException(status_code=400, detail="ASIN 格式无效")
    add_watch_asin(asin, "")
    result = import_manual_reviews(asin, payload.text, payload.rating)
    if result["imported"] == 0:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/api/reviews/manual")
async def manual_reviews() -> dict:
    """获取已导入手动差评的 ASIN 统计。"""
    return {"items": count_manual_reviews_by_asin()}


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

    @app.get("/")
    async def index() -> FileResponse:
        """前端首页。"""
        return FileResponse(FRONTEND_DIR / "index.html")
