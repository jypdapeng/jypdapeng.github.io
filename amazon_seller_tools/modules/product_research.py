"""
选品分析模块 - Product Research Module
功能：市场研究、利润计算、选品评分、竞争分析
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class ProductResearch:
    """选品分析工具"""
    
    def __init__(self, config):
        self.config = config
        self.min_profit_margin = config.PRODUCT_RESEARCH['min_profit_margin']
        self.min_monthly_sales = config.PRODUCT_RESEARCH['min_monthly_sales']
        
    def calculate_profit(self, product_data: Dict) -> Dict:
        """
        计算产品利润
        
        参数：
        - selling_price: 售价
        - cost: 成本
        - amazon_fee_percentage: 亚马逊佣金比例（默认15%）
        - fba_fee: FBA费用
        - shipping_cost: 运输成本
        - other_costs: 其他成本
        """
        selling_price = product_data.get('selling_price', 0)
        cost = product_data.get('cost', 0)
        amazon_fee_percentage = product_data.get('amazon_fee_percentage', 15)
        fba_fee = product_data.get('fba_fee', 0)
        shipping_cost = product_data.get('shipping_cost', 0)
        other_costs = product_data.get('other_costs', 0)
        
        # 计算各项费用
        amazon_fee = selling_price * (amazon_fee_percentage / 100)
        total_costs = cost + amazon_fee + fba_fee + shipping_cost + other_costs
        
        # 计算利润和利润率
        profit = selling_price - total_costs
        profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0
        roi = (profit / cost * 100) if cost > 0 else 0
        
        return {
            'selling_price': selling_price,
            'total_costs': round(total_costs, 2),
            'cost_breakdown': {
                'product_cost': cost,
                'amazon_fee': round(amazon_fee, 2),
                'fba_fee': fba_fee,
                'shipping_cost': shipping_cost,
                'other_costs': other_costs
            },
            'profit': round(profit, 2),
            'profit_margin': round(profit_margin, 2),
            'roi': round(roi, 2),
            'is_profitable': profit_margin >= self.min_profit_margin
        }
    
    def analyze_market_opportunity(self, market_data: Dict) -> Dict:
        """
        分析市场机会
        
        参数：
        - monthly_sales: 月销量
        - avg_price: 平均价格
        - review_count: 评论数量
        - avg_rating: 平均评分
        - top_sellers_count: 头部卖家数量
        - search_volume: 搜索量
        """
        monthly_sales = market_data.get('monthly_sales', 0)
        avg_price = market_data.get('avg_price', 0)
        review_count = market_data.get('review_count', 0)
        avg_rating = market_data.get('avg_rating', 0)
        top_sellers_count = market_data.get('top_sellers_count', 0)
        search_volume = market_data.get('search_volume', 0)
        
        # 计算市场规模
        market_size = monthly_sales * avg_price
        
        # 计算竞争强度（0-100分，分数越低竞争越小）
        competition_score = self._calculate_competition_score(
            review_count, top_sellers_count, monthly_sales
        )
        
        # 计算市场吸引力（0-100分，分数越高越好）
        attractiveness_score = self._calculate_attractiveness_score(
            monthly_sales, avg_price, avg_rating, search_volume
        )
        
        # 计算进入难度（0-100分）
        entry_difficulty = self._calculate_entry_difficulty(
            competition_score, avg_rating, review_count
        )
        
        return {
            'market_size': round(market_size, 2),
            'monthly_revenue_potential': round(market_size, 2),
            'competition_score': round(competition_score, 2),
            'attractiveness_score': round(attractiveness_score, 2),
            'entry_difficulty': round(entry_difficulty, 2),
            'recommendation': self._get_market_recommendation(
                competition_score, attractiveness_score, entry_difficulty
            ),
            'details': {
                'monthly_sales': monthly_sales,
                'avg_price': avg_price,
                'avg_rating': avg_rating,
                'review_count': review_count,
                'top_sellers': top_sellers_count
            }
        }
    
    def _calculate_competition_score(self, review_count: int, 
                                     top_sellers: int, sales: int) -> float:
        """计算竞争分数"""
        # 评论数越多，竞争越激烈
        review_score = min(100, (review_count / 1000) * 50)
        
        # 头部卖家越多，竞争越激烈
        seller_score = min(100, top_sellers * 10)
        
        # 销量越高，市场越成熟，竞争可能越激烈
        sales_score = min(100, (sales / 10000) * 30)
        
        return (review_score + seller_score + sales_score) / 3
    
    def _calculate_attractiveness_score(self, sales: int, price: float,
                                        rating: float, search_volume: int) -> float:
        """计算市场吸引力"""
        # 销量分数
        sales_score = min(100, (sales / 5000) * 40)
        
        # 价格分数（价格适中最好）
        if 15 <= price <= 50:
            price_score = 40
        elif 10 <= price <= 100:
            price_score = 25
        else:
            price_score = 10
        
        # 评分分数（评分不能太高，说明有改进空间）
        if 3.5 <= rating <= 4.2:
            rating_score = 30
        elif rating < 3.5:
            rating_score = 10
        else:
            rating_score = 20
        
        # 搜索量分数
        search_score = min(100, (search_volume / 10000) * 30)
        
        return sales_score + price_score + rating_score + (search_score * 0.3)
    
    def _calculate_entry_difficulty(self, competition: float,
                                    rating: float, reviews: int) -> float:
        """计算进入难度"""
        # 竞争分数占50%
        comp_factor = competition * 0.5
        
        # 评分因素：评分越高越难超越
        rating_factor = (rating / 5) * 25
        
        # 评论数因素：评论越多越难竞争
        review_factor = min(25, (reviews / 1000) * 25)
        
        return comp_factor + rating_factor + review_factor
    
    def _get_market_recommendation(self, competition: float,
                                   attractiveness: float,
                                   difficulty: float) -> str:
        """获取市场建议"""
        if attractiveness >= 70 and competition <= 40 and difficulty <= 50:
            return "强烈推荐 - 高吸引力、低竞争、易进入"
        elif attractiveness >= 60 and competition <= 60:
            return "推荐 - 市场机会良好"
        elif competition >= 70 or difficulty >= 70:
            return "谨慎 - 竞争激烈，需要强大的资源和策略"
        elif attractiveness <= 40:
            return "不推荐 - 市场吸引力不足"
        else:
            return "一般 - 需要详细评估后再决定"
    
    def score_product(self, product_data: Dict, market_data: Dict) -> Dict:
        """
        产品综合评分
        整合利润分析和市场分析，给出最终评分
        """
        profit_analysis = self.calculate_profit(product_data)
        market_analysis = self.analyze_market_opportunity(market_data)
        
        # 计算各维度得分（0-100）
        profit_score = min(100, profit_analysis['profit_margin'] * 2)
        roi_score = min(100, profit_analysis['roi'] / 2)
        market_score = market_analysis['attractiveness_score']
        competition_score = 100 - market_analysis['competition_score']
        
        # 加权总分
        total_score = (
            profit_score * 0.3 +
            roi_score * 0.2 +
            market_score * 0.3 +
            competition_score * 0.2
        )
        
        # 评级
        if total_score >= 80:
            grade = 'A+ (优秀)'
        elif total_score >= 70:
            grade = 'A (良好)'
        elif total_score >= 60:
            grade = 'B (中等)'
        elif total_score >= 50:
            grade = 'C (一般)'
        else:
            grade = 'D (不推荐)'
        
        return {
            'total_score': round(total_score, 2),
            'grade': grade,
            'scores': {
                'profit_score': round(profit_score, 2),
                'roi_score': round(roi_score, 2),
                'market_score': round(market_score, 2),
                'competition_score': round(competition_score, 2)
            },
            'profit_analysis': profit_analysis,
            'market_analysis': market_analysis,
            'recommendation': self._get_final_recommendation(total_score, profit_analysis, market_analysis)
        }
    
    def _get_final_recommendation(self, score: float, profit: Dict, market: Dict) -> str:
        """获取最终建议"""
        recommendations = []
        
        if score >= 70:
            recommendations.append("✅ 这是一个优质的选品机会！")
        
        if profit['profit_margin'] < 30:
            recommendations.append("⚠️ 利润率偏低，建议优化成本结构或提高售价")
        
        if market['competition_score'] > 70:
            recommendations.append("⚠️ 市场竞争激烈，需要强大的差异化策略")
        
        if market['entry_difficulty'] > 70:
            recommendations.append("⚠️ 进入门槛较高，需要充足的资金和资源")
        
        if profit['is_profitable'] and market['attractiveness_score'] > 60:
            recommendations.append("💡 建议：快速行动，抓住市场机会")
        
        return '\n'.join(recommendations) if recommendations else "需要更多数据进行评估"
    
    def compare_products(self, products: List[Dict]) -> pd.DataFrame:
        """
        批量比较多个产品
        返回对比表格
        """
        results = []
        
        for product in products:
            analysis = self.score_product(
                product.get('product_data', {}),
                product.get('market_data', {})
            )
            
            results.append({
                'product_name': product.get('name', 'Unknown'),
                'total_score': analysis['total_score'],
                'grade': analysis['grade'],
                'profit_margin': analysis['profit_analysis']['profit_margin'],
                'roi': analysis['profit_analysis']['roi'],
                'market_attractiveness': analysis['market_analysis']['attractiveness_score'],
                'competition': analysis['market_analysis']['competition_score'],
                'recommendation': analysis['market_analysis']['recommendation']
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('total_score', ascending=False)
        return df
