"""
竞品分析模块 - Competitor Analysis Module
功能：价格监控、评论分析、市场份额、竞品对比
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter
import re

class CompetitorAnalyzer:
    """竞品分析工具"""
    
    def __init__(self, config):
        self.config = config
    
    def analyze_competitor_pricing(self, pricing_data: List[Dict]) -> Dict:
        """
        分析竞品定价
        
        每个竞品应包含：
        - product_name: 产品名称
        - price: 价格
        - sales_rank: 销量排名（可选）
        - rating: 评分（可选）
        - review_count: 评论数（可选）
        """
        df = pd.DataFrame(pricing_data)
        
        if df.empty:
            return {'error': '没有竞品数据'}
        
        # 价格统计
        avg_price = df['price'].mean()
        median_price = df['price'].median()
        min_price = df['price'].min()
        max_price = df['price'].max()
        std_price = df['price'].std()
        
        # 价格区间分布
        low_price_count = len(df[df['price'] < avg_price * 0.8])
        mid_price_count = len(df[(df['price'] >= avg_price * 0.8) & (df['price'] <= avg_price * 1.2)])
        high_price_count = len(df[df['price'] > avg_price * 1.2])
        
        # 找出性价比最高的竞品（如果有评分数据）
        if 'rating' in df.columns and 'review_count' in df.columns:
            df['value_score'] = (df['rating'] * np.log1p(df['review_count'])) / df['price']
            best_value = df.nlargest(3, 'value_score')[['product_name', 'price', 'rating', 'review_count']]
        else:
            best_value = None
        
        # 价格建议
        pricing_recommendation = self._get_pricing_recommendation(
            avg_price, median_price, min_price, max_price
        )
        
        return {
            'price_statistics': {
                'average': round(avg_price, 2),
                'median': round(median_price, 2),
                'min': round(min_price, 2),
                'max': round(max_price, 2),
                'std_dev': round(std_price, 2)
            },
            'price_distribution': {
                'low_price': low_price_count,
                'mid_price': mid_price_count,
                'high_price': high_price_count
            },
            'best_value_products': best_value.to_dict('records') if best_value is not None else [],
            'total_competitors': len(df),
            'pricing_recommendation': pricing_recommendation
        }
    
    def _get_pricing_recommendation(self, avg: float, median: float,
                                   min_price: float, max_price: float) -> Dict:
        """获取定价建议"""
        # 竞争性定价
        competitive_price = median * 0.95
        
        # 高端定价
        premium_price = avg * 1.15
        
        # 低价策略
        budget_price = median * 0.85
        
        recommendations = []
        
        if max_price / min_price > 2:
            recommendations.append("市场价格差异大，有不同定位的细分市场")
        
        recommendations.append(f"竞争性定价：${competitive_price:.2f}（略低于市场中位数）")
        recommendations.append(f"高端定价：${premium_price:.2f}（需要突出产品优势）")
        recommendations.append(f"低价策略：${budget_price:.2f}（适合快速获取市场份额）")
        
        return {
            'competitive_price': round(competitive_price, 2),
            'premium_price': round(premium_price, 2),
            'budget_price': round(budget_price, 2),
            'recommendations': recommendations
        }
    
    def monitor_price_changes(self, price_history: List[Dict]) -> pd.DataFrame:
        """
        监控竞品价格变化
        
        每条记录应包含：
        - product_name: 产品名称
        - date: 日期
        - price: 价格
        """
        df = pd.DataFrame(price_history)
        
        if df.empty:
            return df
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['product_name', 'date'])
        
        # 计算价格变化
        df['price_change'] = df.groupby('product_name')['price'].diff()
        df['price_change_pct'] = df.groupby('product_name')['price'].pct_change() * 100
        
        # 识别价格波动
        df['volatility'] = df.groupby('product_name')['price'].transform('std')
        
        # 最新价格和变化
        latest = df.sort_values('date').groupby('product_name').last()
        
        return latest[['price', 'price_change', 'price_change_pct', 'volatility']]
    
    def analyze_competitor_reviews(self, reviews_data: List[Dict]) -> Dict:
        """
        分析竞品评论
        
        每个竞品应包含：
        - product_name: 产品名称
        - rating: 评分
        - review_count: 评论数
        - positive_reviews: 正面评论数（可选）
        - negative_reviews: 负面评论数（可选）
        """
        df = pd.DataFrame(reviews_data)
        
        if df.empty:
            return {'error': '没有评论数据'}
        
        # 评分统计
        avg_rating = df['rating'].mean()
        median_rating = df['rating'].median()
        
        # 评论数统计
        total_reviews = df['review_count'].sum()
        avg_reviews = df['review_count'].mean()
        
        # 评分分布
        rating_4_5 = len(df[df['rating'] >= 4.0])
        rating_3_4 = len(df[(df['rating'] >= 3.0) & (df['rating'] < 4.0)])
        rating_below_3 = len(df[df['rating'] < 3.0])
        
        # 找出评论最多的竞品
        top_reviewed = df.nlargest(5, 'review_count')[['product_name', 'rating', 'review_count']]
        
        # 找出评分最高的竞品
        top_rated = df.nlargest(5, 'rating')[['product_name', 'rating', 'review_count']]
        
        # 市场机会分析
        opportunities = self._identify_review_opportunities(df)
        
        return {
            'rating_statistics': {
                'average_rating': round(avg_rating, 2),
                'median_rating': round(median_rating, 2),
                'total_reviews': int(total_reviews),
                'avg_reviews_per_product': round(avg_reviews, 0)
            },
            'rating_distribution': {
                'high_rating_4_5': rating_4_5,
                'mid_rating_3_4': rating_3_4,
                'low_rating_below_3': rating_below_3
            },
            'top_reviewed_products': top_reviewed.to_dict('records'),
            'top_rated_products': top_rated.to_dict('records'),
            'market_opportunities': opportunities
        }
    
    def _identify_review_opportunities(self, df: pd.DataFrame) -> List[str]:
        """识别基于评论的市场机会"""
        opportunities = []
        
        avg_rating = df['rating'].mean()
        avg_reviews = df['review_count'].mean()
        
        # 评分普遍不高
        if avg_rating < 4.0:
            opportunities.append(f"✅ 市场平均评分较低({avg_rating:.2f})，有机会通过高质量产品脱颖而出")
        
        # 评论数普遍不高
        if avg_reviews < 100:
            opportunities.append(f"💡 市场评论数较少，容易通过早期评论积累建立优势")
        
        # 有低评分产品
        low_rated = len(df[df['rating'] < 3.5])
        if low_rated > 0:
            opportunities.append(f"🎯 有{low_rated}个低评分竞品，可以针对其痛点改进产品")
        
        # 评论数差异大
        if df['review_count'].std() > df['review_count'].mean():
            opportunities.append("📊 市场评论数分布不均，头部产品优势明显但仍有机会")
        
        return opportunities
    
    def extract_review_insights(self, review_texts: List[str]) -> Dict:
        """
        从评论文本中提取洞察
        
        分析评论关键词和情感
        """
        if not review_texts:
            return {'error': '没有评论文本'}
        
        # 合并所有评论
        all_text = ' '.join(review_texts).lower()
        
        # 提取常见词汇（简单分词）
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        
        # 排除常见停用词
        stop_words = {'the', 'and', 'for', 'this', 'that', 'with', 'was', 'are', 
                      'but', 'not', 'have', 'from', 'they', 'been', 'were', 'had'}
        words = [w for w in words if w not in stop_words]
        
        # 统计词频
        word_freq = Counter(words)
        top_words = word_freq.most_common(20)
        
        # 识别正面和负面关键词
        positive_keywords = ['good', 'great', 'excellent', 'perfect', 'love', 'best', 
                            'quality', 'recommend', 'happy', 'satisfied', 'amazing']
        negative_keywords = ['bad', 'poor', 'terrible', 'worst', 'hate', 'disappointed',
                            'defective', 'broken', 'waste', 'awful', 'useless']
        
        positive_mentions = sum(all_text.count(word) for word in positive_keywords)
        negative_mentions = sum(all_text.count(word) for word in negative_keywords)
        
        # 产品特征提及
        features = {
            'quality': all_text.count('quality'),
            'price': all_text.count('price') + all_text.count('expensive') + all_text.count('cheap'),
            'durability': all_text.count('durable') + all_text.count('durability') + all_text.count('last'),
            'shipping': all_text.count('shipping') + all_text.count('delivery'),
            'packaging': all_text.count('packaging') + all_text.count('package'),
            'size': all_text.count('size') + all_text.count('fit'),
        }
        
        return {
            'top_keywords': [{'word': word, 'count': count} for word, count in top_words],
            'sentiment_indicators': {
                'positive_mentions': positive_mentions,
                'negative_mentions': negative_mentions,
                'sentiment_ratio': round(positive_mentions / max(negative_mentions, 1), 2)
            },
            'feature_mentions': features,
            'insights': self._get_review_insights(features, positive_mentions, negative_mentions)
        }
    
    def _get_review_insights(self, features: Dict, positive: int, negative: int) -> List[str]:
        """获取评论洞察"""
        insights = []
        
        # 情感分析
        if positive > negative * 2:
            insights.append("✅ 整体情感偏正面，客户满意度高")
        elif negative > positive:
            insights.append("⚠️ 负面评论较多，需要关注产品质量和客户体验")
        
        # 特征分析
        top_feature = max(features, key=features.get)
        if features[top_feature] > 0:
            insights.append(f"🔍 客户最关注：{top_feature}（提及{features[top_feature]}次）")
        
        if features['quality'] > sum(features.values()) * 0.3:
            insights.append("💎 质量是关键关注点，确保产品质量过硬")
        
        if features['price'] > sum(features.values()) * 0.2:
            insights.append("💰 价格敏感度高，需要权衡定价策略")
        
        return insights
    
    def calculate_market_share(self, competitors: List[Dict]) -> pd.DataFrame:
        """
        计算市场份额
        
        每个竞品应包含：
        - product_name: 产品名称
        - monthly_sales: 月销量
        - revenue: 月收入（可选）
        """
        df = pd.DataFrame(competitors)
        
        if df.empty:
            return df
        
        # 计算销量市场份额
        total_sales = df['monthly_sales'].sum()
        df['sales_market_share'] = (df['monthly_sales'] / total_sales * 100).round(2)
        
        # 如果有收入数据，计算收入市场份额
        if 'revenue' in df.columns:
            total_revenue = df['revenue'].sum()
            df['revenue_market_share'] = (df['revenue'] / total_revenue * 100).round(2)
        
        # 排序
        df = df.sort_values('monthly_sales', ascending=False)
        
        # 添加排名
        df['rank'] = range(1, len(df) + 1)
        
        return df
    
    def compare_products(self, my_product: Dict, competitors: List[Dict]) -> Dict:
        """
        产品对比分析
        
        产品应包含：
        - product_name: 产品名称
        - price: 价格
        - rating: 评分
        - review_count: 评论数
        - monthly_sales: 月销量（可选）
        - features: 产品特征列表（可选）
        """
        my_name = my_product.get('product_name', 'My Product')
        my_price = my_product.get('price', 0)
        my_rating = my_product.get('rating', 0)
        my_reviews = my_product.get('review_count', 0)
        my_sales = my_product.get('monthly_sales', 0)
        
        # 竞品平均值
        comp_df = pd.DataFrame(competitors)
        avg_comp_price = comp_df['price'].mean()
        avg_comp_rating = comp_df['rating'].mean()
        avg_comp_reviews = comp_df['review_count'].mean()
        avg_comp_sales = comp_df.get('monthly_sales', pd.Series([0])).mean()
        
        # 对比分析
        comparison = {
            'price': {
                'my_value': my_price,
                'competitor_avg': round(avg_comp_price, 2),
                'difference': round(my_price - avg_comp_price, 2),
                'difference_pct': round((my_price - avg_comp_price) / avg_comp_price * 100, 1),
                'position': 'higher' if my_price > avg_comp_price else 'lower' if my_price < avg_comp_price else 'equal'
            },
            'rating': {
                'my_value': my_rating,
                'competitor_avg': round(avg_comp_rating, 2),
                'difference': round(my_rating - avg_comp_rating, 2),
                'position': 'higher' if my_rating > avg_comp_rating else 'lower' if my_rating < avg_comp_rating else 'equal'
            },
            'review_count': {
                'my_value': my_reviews,
                'competitor_avg': round(avg_comp_reviews, 0),
                'difference': int(my_reviews - avg_comp_reviews),
                'position': 'higher' if my_reviews > avg_comp_reviews else 'lower' if my_reviews < avg_comp_reviews else 'equal'
            }
        }
        
        if my_sales > 0:
            comparison['monthly_sales'] = {
                'my_value': my_sales,
                'competitor_avg': round(avg_comp_sales, 0),
                'difference': int(my_sales - avg_comp_sales),
                'position': 'higher' if my_sales > avg_comp_sales else 'lower' if my_sales < avg_comp_sales else 'equal'
            }
        
        # 竞争力评分
        competitive_score = self._calculate_competitive_score(
            my_price, avg_comp_price, my_rating, avg_comp_rating,
            my_reviews, avg_comp_reviews
        )
        
        # 优劣势分析
        strengths, weaknesses = self._analyze_strengths_weaknesses(comparison)
        
        return {
            'comparison': comparison,
            'competitive_score': competitive_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': self._get_competitive_recommendations(comparison, strengths, weaknesses)
        }
    
    def _calculate_competitive_score(self, my_price: float, avg_price: float,
                                    my_rating: float, avg_rating: float,
                                    my_reviews: int, avg_reviews: int) -> Dict:
        """计算竞争力评分"""
        score = 0
        
        # 价格竞争力（30分）
        price_ratio = my_price / avg_price if avg_price > 0 else 1
        if price_ratio < 0.9:  # 价格更低
            price_score = 30
        elif price_ratio < 1.0:
            price_score = 25
        elif price_ratio < 1.1:
            price_score = 20
        else:
            price_score = 10
        
        # 评分竞争力（35分）
        if my_rating >= avg_rating + 0.3:
            rating_score = 35
        elif my_rating >= avg_rating:
            rating_score = 30
        elif my_rating >= avg_rating - 0.2:
            rating_score = 20
        else:
            rating_score = 10
        
        # 评论数竞争力（35分）
        review_ratio = my_reviews / avg_reviews if avg_reviews > 0 else 0
        if review_ratio >= 1.5:
            review_score = 35
        elif review_ratio >= 1.0:
            review_score = 30
        elif review_ratio >= 0.5:
            review_score = 20
        else:
            review_score = 10
        
        score = price_score + rating_score + review_score
        
        if score >= 80:
            grade = 'A+ (极具竞争力)'
        elif score >= 70:
            grade = 'A (竞争力强)'
        elif score >= 60:
            grade = 'B (有竞争力)'
        elif score >= 50:
            grade = 'C (竞争力一般)'
        else:
            grade = 'D (竞争力弱)'
        
        return {
            'total_score': score,
            'grade': grade,
            'breakdown': {
                'price_score': price_score,
                'rating_score': rating_score,
                'review_score': review_score
            }
        }
    
    def _analyze_strengths_weaknesses(self, comparison: Dict) -> Tuple[List[str], List[str]]:
        """分析优劣势"""
        strengths = []
        weaknesses = []
        
        # 价格
        if comparison['price']['position'] == 'lower':
            strengths.append(f"价格优势：比竞品平均价格低{abs(comparison['price']['difference_pct'])}%")
        elif comparison['price']['difference_pct'] > 20:
            weaknesses.append(f"价格劣势：比竞品平均价格高{comparison['price']['difference_pct']}%")
        
        # 评分
        if comparison['rating']['position'] == 'higher':
            strengths.append(f"评分优势：评分({comparison['rating']['my_value']})高于竞品平均")
        elif comparison['rating']['difference'] < -0.3:
            weaknesses.append(f"评分劣势：评分低于竞品平均{abs(comparison['rating']['difference'])}")
        
        # 评论数
        if comparison['review_count']['position'] == 'higher':
            strengths.append(f"评论优势：评论数({comparison['review_count']['my_value']})超过竞品平均")
        elif comparison['review_count']['difference'] < -50:
            weaknesses.append(f"评论劣势：评论数少于竞品平均，需要积累社会证明")
        
        return strengths, weaknesses
    
    def _get_competitive_recommendations(self, comparison: Dict,
                                        strengths: List[str],
                                        weaknesses: List[str]) -> List[str]:
        """获取竞争建议"""
        recommendations = []
        
        if len(strengths) >= 2:
            recommendations.append("✅ 产品竞争力强，可以加大推广力度")
        
        if comparison['price']['position'] == 'higher' and comparison['rating']['position'] == 'lower':
            recommendations.append("⚠️ 价格高但评分低，需要优化产品质量或降低价格")
        
        if comparison['review_count']['position'] == 'lower':
            recommendations.append("📝 评论数较少，通过促销和邮件营销增加评论")
        
        if comparison['rating']['position'] == 'lower':
            recommendations.append("⭐ 评分较低，分析负面评论并改进产品")
        
        if not recommendations:
            recommendations.append("💡 继续保持产品竞争力，持续监控竞品动态")
        
        return recommendations
