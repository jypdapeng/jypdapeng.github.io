"""
配置文件 - 亚马逊卖家辅助工具
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'amazon_seller.db')
    
    # 亚马逊API配置（如果使用SP-API）
    AMAZON_ACCESS_KEY = os.environ.get('AMAZON_ACCESS_KEY', '')
    AMAZON_SECRET_KEY = os.environ.get('AMAZON_SECRET_KEY', '')
    AMAZON_REGION = os.environ.get('AMAZON_REGION', 'us-east-1')
    AMAZON_MARKETPLACE_ID = os.environ.get('AMAZON_MARKETPLACE_ID', 'ATVPDKIKX0DER')
    
    # OpenAI配置（用于Listing优化）
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # 选品分析配置
    PRODUCT_RESEARCH = {
        'min_profit_margin': 30,  # 最小利润率（%）
        'min_monthly_sales': 300,  # 最小月销量
        'max_competition_score': 70,  # 最大竞争分数
        'min_review_rating': 3.5,  # 最小评分
    }
    
    # 库存管理配置
    INVENTORY = {
        'low_stock_days': 30,  # 低库存预警天数
        'reorder_point_factor': 1.5,  # 补货点系数
        'safety_stock_days': 7,  # 安全库存天数
    }
    
    # 广告配置
    ADVERTISING = {
        'target_acos': 25,  # 目标ACOS（%）
        'max_cpc': 2.0,  # 最大CPC（美元）
        'min_impressions': 1000,  # 最小展示量
    }
    
    # 数据导出配置
    EXPORT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'exports')
