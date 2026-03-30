"""
主应用程序 - Flask Web应用
亚马逊卖家智能辅助系统
"""
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
from datetime import datetime, timedelta
import os

# 导入所有模块
from config import Config
from modules.product_research import ProductResearch
from modules.operations import OperationsManager
from modules.inventory import InventoryManager
from modules.advertising import AdvertisingOptimizer
from modules.ranking import RankingAnalyzer
from modules.competitor import CompetitorAnalyzer
from modules.listing import ListingOptimizer

app = Flask(__name__)
app.config.from_object(Config)

# 初始化所有模块
product_research = ProductResearch(Config)
operations = OperationsManager(Config)
inventory = InventoryManager(Config)
advertising = AdvertisingOptimizer(Config)
ranking = RankingAnalyzer(Config)
competitor = CompetitorAnalyzer(Config)
listing = ListingOptimizer(Config)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

# ============ 选品分析相关路由 ============

@app.route('/product-research')
def product_research_page():
    """选品分析页面"""
    return render_template('product_research.html')

@app.route('/api/product-research/calculate-profit', methods=['POST'])
def calculate_profit():
    """计算产品利润"""
    try:
        data = request.json
        result = product_research.calculate_profit(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/product-research/analyze-market', methods=['POST'])
def analyze_market():
    """分析市场机会"""
    try:
        data = request.json
        result = product_research.analyze_market_opportunity(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/product-research/score-product', methods=['POST'])
def score_product():
    """产品综合评分"""
    try:
        data = request.json
        product_data = data.get('product_data', {})
        market_data = data.get('market_data', {})
        result = product_research.score_product(product_data, market_data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 运营管理相关路由 ============

@app.route('/operations')
def operations_page():
    """运营管理页面"""
    return render_template('operations.html')

@app.route('/api/operations/analyze-sales', methods=['POST'])
def analyze_sales():
    """分析销售数据"""
    try:
        data = request.json
        sales_df = pd.DataFrame(data.get('sales_data', []))
        result = operations.analyze_sales_data(sales_df)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/operations/calculate-kpis', methods=['POST'])
def calculate_kpis():
    """计算KPIs"""
    try:
        data = request.json
        result = operations.calculate_kpis(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/operations/forecast-sales', methods=['POST'])
def forecast_sales():
    """销售预测"""
    try:
        data = request.json
        sales_df = pd.DataFrame(data.get('sales_data', []))
        days = data.get('days', 30)
        result = operations.forecast_sales(sales_df, days)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 库存管理相关路由 ============

@app.route('/inventory')
def inventory_page():
    """库存管理页面"""
    return render_template('inventory.html')

@app.route('/api/inventory/analyze', methods=['POST'])
def analyze_inventory():
    """分析库存"""
    try:
        data = request.json
        result = inventory.analyze_inventory(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/inventory/reorder-quantity', methods=['POST'])
def calculate_reorder():
    """计算补货量"""
    try:
        data = request.json
        result = inventory.calculate_reorder_quantity(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/inventory/turnover-rate', methods=['POST'])
def calculate_turnover():
    """计算周转率"""
    try:
        data = request.json
        result = inventory.calculate_turnover_rate(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 广告优化相关路由 ============

@app.route('/advertising')
def advertising_page():
    """广告优化页面"""
    return render_template('advertising.html')

@app.route('/api/advertising/analyze-campaign', methods=['POST'])
def analyze_campaign():
    """分析广告活动"""
    try:
        data = request.json
        result = advertising.analyze_campaign_performance(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/advertising/analyze-keywords', methods=['POST'])
def analyze_keywords():
    """分析关键词"""
    try:
        data = request.json
        keywords_data = data.get('keywords', [])
        result = advertising.analyze_keywords(keywords_data)
        result_dict = result.to_dict('records') if not result.empty else []
        return jsonify({'success': True, 'data': result_dict})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/advertising/optimize-budget', methods=['POST'])
def optimize_budget():
    """优化预算分配"""
    try:
        data = request.json
        campaigns = data.get('campaigns', [])
        result = advertising.optimize_budget_allocation(campaigns)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 排名分析相关路由 ============

@app.route('/ranking')
def ranking_page():
    """排名分析页面"""
    return render_template('ranking.html')

@app.route('/api/ranking/analyze', methods=['POST'])
def analyze_ranking():
    """分析排名表现"""
    try:
        data = request.json
        ranking_df = pd.DataFrame(data.get('ranking_data', []))
        tracked = ranking.track_keyword_rankings(ranking_df.to_dict('records'))
        result = ranking.analyze_ranking_performance(tracked)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ranking/visibility-score', methods=['POST'])
def calculate_visibility():
    """计算可见度分数"""
    try:
        data = request.json
        result = ranking.calculate_visibility_score(data.get('ranking_data', []))
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 竞品分析相关路由 ============

@app.route('/competitor')
def competitor_page():
    """竞品分析页面"""
    return render_template('competitor.html')

@app.route('/api/competitor/analyze-pricing', methods=['POST'])
def analyze_pricing():
    """分析竞品定价"""
    try:
        data = request.json
        result = competitor.analyze_competitor_pricing(data.get('pricing_data', []))
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/competitor/analyze-reviews', methods=['POST'])
def analyze_reviews():
    """分析竞品评论"""
    try:
        data = request.json
        result = competitor.analyze_competitor_reviews(data.get('reviews_data', []))
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/competitor/compare-products', methods=['POST'])
def compare_products():
    """产品对比"""
    try:
        data = request.json
        my_product = data.get('my_product', {})
        competitors = data.get('competitors', [])
        result = competitor.compare_products(my_product, competitors)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ Listing优化相关路由 ============

@app.route('/listing')
def listing_page():
    """Listing优化页面"""
    return render_template('listing.html')

@app.route('/api/listing/analyze-title', methods=['POST'])
def analyze_title():
    """分析标题"""
    try:
        data = request.json
        title = data.get('title', '')
        result = listing.analyze_title(title)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/listing/analyze-bullets', methods=['POST'])
def analyze_bullets():
    """分析要点"""
    try:
        data = request.json
        bullet_points = data.get('bullet_points', [])
        result = listing.analyze_bullet_points(bullet_points)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/listing/seo-report', methods=['POST'])
def seo_report():
    """生成SEO报告"""
    try:
        data = request.json
        title = data.get('title', '')
        bullet_points = data.get('bullet_points', [])
        description = data.get('description', '')
        keywords = data.get('keywords', [])
        result = listing.generate_seo_report(title, bullet_points, description, keywords)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ 工具函数 ============

@app.template_filter('format_currency')
def format_currency(value):
    """格式化货币"""
    return f"${value:,.2f}"

@app.template_filter('format_percent')
def format_percent(value):
    """格式化百分比"""
    return f"{value:.1f}%"

if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs(Config.EXPORT_PATH, exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)
