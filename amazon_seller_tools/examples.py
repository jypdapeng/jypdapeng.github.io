"""
示例代码 - 演示如何使用各个模块
"""

# ==================== 1. 选品分析示例 ====================

def example_product_research():
    """选品分析示例"""
    from modules.product_research import ProductResearch
    from config import Config
    
    print("\n" + "="*60)
    print("示例1：选品分析")
    print("="*60)
    
    pr = ProductResearch(Config)
    
    # 计算利润
    print("\n【利润计算】")
    product_data = {
        'selling_price': 29.99,
        'cost': 10.0,
        'amazon_fee_percentage': 15,
        'fba_fee': 4.5,
        'shipping_cost': 2.0,
        'other_costs': 1.0
    }
    
    profit_result = pr.calculate_profit(product_data)
    print(f"售价: ${profit_result['selling_price']}")
    print(f"总成本: ${profit_result['total_costs']}")
    print(f"净利润: ${profit_result['profit']}")
    print(f"利润率: {profit_result['profit_margin']}%")
    print(f"ROI: {profit_result['roi']}%")
    
    # 产品综合评分
    print("\n【产品综合评分】")
    market_data = {
        'monthly_sales': 5000,
        'avg_price': 28.0,
        'avg_rating': 4.2,
        'review_count': 500,
        'top_sellers_count': 10,
        'search_volume': 50000
    }
    
    score_result = pr.score_product(product_data, market_data)
    print(f"综合得分: {score_result['total_score']}")
    print(f"评级: {score_result['grade']}")
    print(f"市场建议: {score_result['market_analysis']['recommendation']}")


# ==================== 2. 运营管理示例 ====================

def example_operations():
    """运营管理示例"""
    from modules.operations import OperationsManager
    from config import Config
    import pandas as pd
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print("示例2：运营管理")
    print("="*60)
    
    ops = OperationsManager(Config)
    
    # 生成模拟销售数据
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    sales_df = pd.DataFrame({
        'date': dates,
        'sales': [1000 + i*50 + (i%7)*100 for i in range(30)],
        'units': [30 + i*2 + (i%5)*5 for i in range(30)],
        'orders': [25 + i + (i%3)*3 for i in range(30)]
    })
    
    # 分析销售数据
    print("\n【销售数据分析】")
    sales_analysis = ops.analyze_sales_data(sales_df)
    print(f"总销售额: ${sales_analysis['summary']['total_sales']:,.2f}")
    print(f"总销量: {sales_analysis['summary']['total_units']:,} 件")
    print(f"总订单数: {sales_analysis['summary']['total_orders']:,}")
    print(f"日均销售额: ${sales_analysis['daily_averages']['sales']:.2f}")
    print(f"7天增长率: {sales_analysis['trend']['growth_rate_7d']:.2f}%")
    
    # 计算KPIs
    print("\n【KPI指标】")
    kpi_data = {
        'sales': sales_analysis['summary']['total_sales'],
        'ad_spend': 5000,
        'units_sold': sales_analysis['summary']['total_units'],
        'sessions': 10000,
        'orders': sales_analysis['summary']['total_orders'],
        'returns': 50,
        'total_costs': 20000
    }
    
    kpis = ops.calculate_kpis(kpi_data)
    print(f"ACoS: {kpis['acos']:.2f}%")
    print(f"转化率: {kpis['conversion_rate']:.2f}%")
    print(f"退货率: {kpis['return_rate']:.2f}%")
    print(f"利润率: {kpis['profit_margin']:.2f}%")
    print(f"绩效评级: {kpis['performance_grade']}")


# ==================== 3. 库存管理示例 ====================

def example_inventory():
    """库存管理示例"""
    from modules.inventory import InventoryManager
    from config import Config
    
    print("\n" + "="*60)
    print("示例3：库存管理")
    print("="*60)
    
    im = InventoryManager(Config)
    
    # 分析库存状态
    print("\n【库存状态分析】")
    inventory_data = {
        'current_stock': 100,
        'daily_sales_avg': 5,
        'lead_time_days': 30
    }
    
    inventory_analysis = im.analyze_inventory(inventory_data)
    print(f"当前库存: {inventory_analysis['current_stock']} 件")
    print(f"可用天数: {inventory_analysis['days_of_stock']:.1f} 天")
    print(f"库存状态: {inventory_analysis['status_text']}")
    print(f"建议补货点: {inventory_analysis['reorder_point']:.0f} 件")
    print(f"是否需要补货: {'是' if inventory_analysis['need_reorder'] else '否'}")
    
    # 计算补货量
    print("\n【补货量计算】")
    reorder_data = {
        'annual_demand': 1825,  # 5件/天 * 365天
        'ordering_cost': 50,
        'holding_cost_rate': 0.2,
        'unit_cost': 10,
        'daily_sales_avg': 5,
        'lead_time_days': 30,
        'current_stock': 100
    }
    
    reorder_calc = im.calculate_reorder_quantity(reorder_data)
    print(f"经济订货量(EOQ): {reorder_calc['eoq']:.0f} 件")
    print(f"建议订货量: {reorder_calc['suggested_order_quantity']:.0f} 件")
    print(f"订货后库存可用天数: {reorder_calc['days_after_reorder']:.1f} 天")
    print(f"订货总成本: ${reorder_calc['total_order_cost']:.2f}")


# ==================== 4. 广告优化示例 ====================

def example_advertising():
    """广告优化示例"""
    from modules.advertising import AdvertisingOptimizer
    from config import Config
    
    print("\n" + "="*60)
    print("示例4：广告优化")
    print("="*60)
    
    ad = AdvertisingOptimizer(Config)
    
    # 分析广告活动
    print("\n【广告活动分析】")
    campaign_data = {
        'impressions': 50000,
        'clicks': 500,
        'spend': 250,
        'sales': 625,
        'orders': 25
    }
    
    campaign_analysis = ad.analyze_campaign_performance(campaign_data)
    print(f"展示量: {campaign_analysis['impressions']:,}")
    print(f"点击量: {campaign_analysis['clicks']:,}")
    print(f"CTR: {campaign_analysis['metrics']['ctr']:.2f}%")
    print(f"CPC: ${campaign_analysis['metrics']['cpc']:.2f}")
    print(f"ACoS: {campaign_analysis['metrics']['acos']:.2f}%")
    print(f"CVR: {campaign_analysis['metrics']['cvr']:.2f}%")
    print(f"ROAS: {campaign_analysis['metrics']['roas']:.2f}")
    print(f"综合评级: {campaign_analysis['performance']['overall_rating']}")
    
    # 关键词分析
    print("\n【关键词分析】")
    keywords_data = [
        {'keyword': 'bluetooth headphones', 'impressions': 20000, 'clicks': 200, 
         'spend': 100, 'sales': 400, 'orders': 16},
        {'keyword': 'wireless earbuds', 'impressions': 15000, 'clicks': 150,
         'spend': 75, 'sales': 225, 'orders': 9},
        {'keyword': 'cheap headphones', 'impressions': 10000, 'clicks': 100,
         'spend': 50, 'sales': 50, 'orders': 2}
    ]
    
    keyword_df = ad.analyze_keywords(keywords_data)
    print(keyword_df.to_string(index=False))


# ==================== 5. 排名分析示例 ====================

def example_ranking():
    """排名分析示例"""
    from modules.ranking import RankingAnalyzer
    from config import Config
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print("示例5：排名分析")
    print("="*60)
    
    ra = RankingAnalyzer(Config)
    
    # 生成模拟排名数据
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    ranking_data = []
    
    keywords = ['bluetooth headphones', 'wireless earbuds', 'noise cancelling headphones']
    for keyword in keywords:
        for i, date in enumerate(dates):
            ranking_data.append({
                'keyword': keyword,
                'date': date,
                'rank': 15 + (i % 10) - 5 if keyword == 'bluetooth headphones' else 25 + (i % 8),
                'page': 1,
                'search_volume': 50000 if keyword == 'bluetooth headphones' else 30000
            })
    
    # 追踪排名
    tracked_df = ra.track_keyword_rankings(ranking_data)
    
    # 分析排名表现
    print("\n【排名表现分析】")
    ranking_analysis = ra.analyze_ranking_performance(tracked_df)
    print(f"总关键词数: {ranking_analysis['summary']['total_keywords']}")
    print(f"平均排名: {ranking_analysis['summary']['avg_rank']:.1f}")
    print(f"第一页关键词: {ranking_analysis['page_distribution']['page_1']}")
    print(f"第一页占比: {ranking_analysis['page_distribution']['page_1_percentage']:.1f}%")
    print(f"排名上升: {ranking_analysis['trend_analysis']['improving']}")
    print(f"排名下降: {ranking_analysis['trend_analysis']['declining']}")
    print(f"排名稳定: {ranking_analysis['trend_analysis']['stable']}")


# ==================== 6. 竞品分析示例 ====================

def example_competitor():
    """竞品分析示例"""
    from modules.competitor import CompetitorAnalyzer
    from config import Config
    
    print("\n" + "="*60)
    print("示例6：竞品分析")
    print("="*60)
    
    ca = CompetitorAnalyzer(Config)
    
    # 分析竞品定价
    print("\n【竞品定价分析】")
    pricing_data = [
        {'product_name': '竞品A', 'price': 29.99, 'rating': 4.5, 'review_count': 1000},
        {'product_name': '竞品B', 'price': 34.99, 'rating': 4.3, 'review_count': 500},
        {'product_name': '竞品C', 'price': 24.99, 'rating': 4.0, 'review_count': 300},
        {'product_name': '竞品D', 'price': 39.99, 'rating': 4.7, 'review_count': 1500},
    ]
    
    pricing_analysis = ca.analyze_competitor_pricing(pricing_data)
    print(f"平均价格: ${pricing_analysis['price_statistics']['average']:.2f}")
    print(f"中位数价格: ${pricing_analysis['price_statistics']['median']:.2f}")
    print(f"价格范围: ${pricing_analysis['price_statistics']['min']:.2f} - ${pricing_analysis['price_statistics']['max']:.2f}")
    print(f"总竞品数: {pricing_analysis['total_competitors']}")
    
    # 产品对比
    print("\n【产品对比】")
    my_product = {
        'product_name': '我的产品',
        'price': 32.99,
        'rating': 4.4,
        'review_count': 200,
        'monthly_sales': 500
    }
    
    comparison = ca.compare_products(my_product, pricing_data)
    print(f"竞争力得分: {comparison['competitive_score']['total_score']}")
    print(f"竞争力评级: {comparison['competitive_score']['grade']}")
    print("\n优势:")
    for strength in comparison['strengths']:
        print(f"  ✓ {strength}")
    print("\n劣势:")
    for weakness in comparison['weaknesses']:
        print(f"  ✗ {weakness}")


# ==================== 7. Listing优化示例 ====================

def example_listing():
    """Listing优化示例"""
    from modules.listing import ListingOptimizer
    from config import Config
    
    print("\n" + "="*60)
    print("示例7：Listing优化")
    print("="*60)
    
    lo = ListingOptimizer(Config)
    
    # 分析标题
    print("\n【标题分析】")
    title = "Bluetooth Headphones Wireless Earbuds"
    title_analysis = lo.analyze_title(title)
    print(f"标题: {title_analysis['title']}")
    print(f"长度: {title_analysis['length']} 字符")
    print(f"字数: {title_analysis['word_count']}")
    print(f"得分: {title_analysis['score']}")
    print(f"评级: {title_analysis['grade']}")
    print("\n优化建议:")
    for i, suggestion in enumerate(title_analysis['suggestions'], 1):
        print(f"  {i}. {suggestion}")
    
    # 分析要点
    print("\n【要点分析】")
    bullet_points = [
        "Advanced Bluetooth 5.0 technology ensures stable wireless connection up to 33ft",
        "Premium sound quality with deep bass and crystal clear treble",
        "IPX7 waterproof rating makes it perfect for sports and outdoor activities",
        "Long battery life - 8 hours playtime on single charge, 30 hours with charging case",
        "One-touch control and voice assistant support for hands-free operation"
    ]
    
    bullet_analysis = lo.analyze_bullet_points(bullet_points)
    print(f"要点数量: {bullet_analysis['bullet_count']}")
    print(f"平均得分: {bullet_analysis['avg_score']:.1f}")
    print(f"评级: {bullet_analysis['grade']}")
    
    # 关键词密度
    print("\n【关键词密度】")
    full_text = title + " " + " ".join(bullet_points)
    keywords = ['bluetooth', 'wireless', 'headphones', 'waterproof', 'battery']
    
    density_analysis = lo.calculate_keyword_density(full_text, keywords)
    print(f"总字数: {density_analysis['total_words']}")
    for kw_stat in density_analysis['keyword_stats']:
        print(f"  {kw_stat['keyword']}: 出现{kw_stat['count']}次, 密度{kw_stat['density']:.2f}% ({kw_stat['status']})")


# ==================== 主函数 ====================

def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("亚马逊卖家智能辅助系统 - 示例代码")
    print("="*60)
    
    try:
        example_product_research()
        example_operations()
        example_inventory()
        example_advertising()
        example_ranking()
        example_competitor()
        example_listing()
        
        print("\n" + "="*60)
        print("所有示例运行完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
