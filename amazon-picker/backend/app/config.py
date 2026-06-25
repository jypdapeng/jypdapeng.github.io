"""应用配置模块。"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR.parent / "frontend"


class Settings(BaseSettings):
    """全局配置项。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Amazon 选品痛点洞察"
    database_path: str = str(DATA_DIR / "picker.db")
    daily_collect_hour: int = 8
    daily_collect_minute: int = 0
    request_timeout: float = 20.0
    user_agent: str = (
        "Mozilla/5.0 (compatible; AmazonPickerInsight/1.0; +https://github.com/picker)"
    )
    reddit_subreddits: str = "ACL,kneesurgery,AmazonFinds,BuyItForLife,FulfillmentByAmazon"
    default_asins: str = "B07Y3PZHD9,B0GVDCX8T2,B0DQDCBF7X,B089YBVBV3"
    rainforest_api_key: str = ""


settings = Settings()
