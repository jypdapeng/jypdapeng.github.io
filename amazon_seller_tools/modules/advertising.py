"""
广告优化模块 - Advertising Optimization Module
功能：广告分析、关键词建议、预算优化、ACOS优化
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class AdvertisingOptimizer:
    """广告优化工具"""
    
    def __init__(self, config):
        self.config = config
        self.target_acos = config.ADVERTISING['target_acos']
        self.max_cpc = config.ADVERTISING['max_cpc']
        self.min_impressions = config.ADVERTISING['min_impressions']
    
    def analyze_campaign_performance(self, campaign_data: Dict) -> Dict:
        """
        分析广告活动表现
        
        参数：
        - impressions: 展示量
        - clicks: 点击量
        - spend: 花费
        - sales: 销售额
        - orders: 订单数
        """
        impressions = campaign_data.get('impressions', 0)
        clicks = campaign_data.get('clicks', 0)
        spend = campaign_data.get('spend', 0)
        sales = campaign_data.get('sales', 0)
        orders = campaign_data.get('orders', 0)
        
        # CTR (点击率)
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        # CPC (每次点击成本)
        cpc = (spend / clicks) if clicks > 0 else 0
        
        # ACoS (广告成本销售比)
        acos = (spend / sales * 100) if sales > 0 else 0
        
        # CVR (转化率)
        cvr = (orders / clicks * 100) if clicks > 0 else 0
        
        # ROAS (广告投资回报率)
        roas = (sales / spend) if spend > 0 else 0
        
        # CPA (每次转化成本)
        cpa = (spend / orders) if orders > 0 else 0
        
        # 评估表现
        performance = self._evaluate_campaign_performance(ctr, acos, cvr, roas)
        
        return {
            'impressions': impressions,
            'clicks': clicks,
            'spend': round(spend, 2),
            'sales': round(sales, 2),
            'orders': orders,
            'metrics': {
                'ctr': round(ctr, 2),
                'cpc': round(cpc, 2),
                'acos': round(acos, 2),
                'cvr': round(cvr, 2),
                'roas': round(roas, 2),
                'cpa': round(cpa, 2)
            },
            'performance': performance,
            'recommendations': self._get_campaign_recommendations(ctr, cpc, acos, cvr)
        }
    
    def _evaluate_campaign_performance(self, ctr: float, acos: float,
                                      cvr: float, roas: float) -> Dict:
        """评估广告活动表现"""
        score = 0
        
        # CTR评分（目标>0.5%）
        if ctr > 1.0:
            score += 25
            ctr_rating = '优秀'
        elif ctr > 0.5:
            score += 20
            ctr_rating = '良好'
        elif ctr > 0.3:
            score += 10
            ctr_rating = '一般'
        else:
            ctr_rating = '偏低'
        
        # ACoS评分（目标<30%）
        if acos < 20:
            score += 30
            acos_rating = '优秀'
        elif acos < self.target_acos:
            score += 25
            acos_rating = '良好'
        elif acos < 40:
            score += 15
            acos_rating = '一般'
        else:
            acos_rating = '偏高'
        
        # CVR评分（目标>10%）
        if cvr > 15:
            score += 25
            cvr_rating = '优秀'
        elif cvr > 10:
            score += 20
            cvr_rating = '良好'
        elif cvr > 5:
            score += 10
            cvr_rating = '一般'
        else:
            cvr_rating = '偏低'
        
        # ROAS评分（目标>3）
        if roas > 5:
            score += 20
            roas_rating = '优秀'
        elif roas > 3:
            score += 15
            roas_rating = '良好'
        elif roas > 2:
            score += 10
            roas_rating = '一般'
        else:
            roas_rating = '偏低'
        
        # 总体评级
        if score >= 80:
            overall = 'A+ (卓越)'
        elif score >= 70:
            overall = 'A (优秀)'
        elif score >= 60:
            overall = 'B (良好)'
        elif score >= 50:
            overall = 'C (中等)'
        else:
            overall = 'D (需优化)'
        
        return {
            'overall_rating': overall,
            'score': score,
            'ratings': {
                'ctr': ctr_rating,
                'acos': acos_rating,
                'cvr': cvr_rating,
                'roas': roas_rating
            }
        }
    
    def _get_campaign_recommendations(self, ctr: float, cpc: float,
                                     acos: float, cvr: float) -> List[str]:
        """获取广告活动优化建议"""
        recommendations = []
        
        if ctr < 0.5:
            recommendations.append("📊 CTR偏低，建议优化广告标题和图片，提高吸引力")
        
        if cpc > self.max_cpc:
            recommendations.append(f"💰 CPC过高({cpc:.2f})，建议降低出价或优化关键词质量分")
        
        if acos > self.target_acos:
            recommendations.append(f"🎯 ACoS高于目标({acos:.1f}% > {self.target_acos}%)，建议暂停低效关键词")
        
        if cvr < 10:
            recommendations.append("🔄 转化率较低，检查产品页面、定价和评论")
        
        if ctr > 1.0 and cvr < 5:
            recommendations.append("⚠️ CTR高但CVR低，可能关键词不够精准或产品页面有问题")
        
        if acos < 20:
            recommendations.append("✅ 表现优秀！可以适度提高预算扩大投放")
        
        return recommendations
    
    def analyze_keywords(self, keywords_data: List[Dict]) -> pd.DataFrame:
        """
        分析关键词表现
        
        每个关键词应包含：
        - keyword: 关键词
        - impressions: 展示量
        - clicks: 点击量
        - spend: 花费
        - sales: 销售额
        - orders: 订单数
        """
        results = []
        
        for kw_data in keywords_data:
            keyword = kw_data.get('keyword', '')
            impressions = kw_data.get('impressions', 0)
            clicks = kw_data.get('clicks', 0)
            spend = kw_data.get('spend', 0)
            sales = kw_data.get('sales', 0)
            orders = kw_data.get('orders', 0)
            
            # 计算指标
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            acos = (spend / sales * 100) if sales > 0 else 0
            cvr = (orders / clicks * 100) if clicks > 0 else 0
            roas = (sales / spend) if spend > 0 else 0
            
            # 关键词策略建议
            action = self._get_keyword_action(impressions, ctr, acos, cvr, spend)
            
            results.append({
                'keyword': keyword,
                'impressions': impressions,
                'clicks': clicks,
                'ctr': round(ctr, 2),
                'cpc': round(cpc, 2),
                'spend': round(spend, 2),
                'sales': round(sales, 2),
                'acos': round(acos, 2),
                'cvr': round(cvr, 2),
                'roas': round(roas, 2),
                'orders': orders,
                'action': action
            })
        
        df = pd.DataFrame(results)
        if not df.empty:
            # 按花费排序
            df = df.sort_values('spend', ascending=False)
        
        return df
    
    def _get_keyword_action(self, impressions: int, ctr: float,
                           acos: float, cvr: float, spend: float) -> str:
        """获取关键词操作建议"""
        # 数据不足
        if impressions < self.min_impressions:
            return '继续观察'
        
        # 高效关键词
        if acos < self.target_acos and cvr > 10:
            return '✅ 提高出价'
        
        # 低效关键词
        if acos > self.target_acos * 2 or (cvr < 2 and spend > 10):
            return '❌ 暂停'
        
        # 待优化关键词
        if acos > self.target_acos and acos < self.target_acos * 2:
            return '⚠️ 降低出价'
        
        # 潜力关键词
        if ctr > 1.0 and cvr > 5:
            return '💡 优化'
        
        return '保持'
    
    def optimize_budget_allocation(self, campaigns: List[Dict]) -> Dict:
        """
        优化预算分配
        
        每个活动应包含：
        - campaign_name: 活动名称
        - current_budget: 当前预算
        - spend: 实际花费
        - sales: 销售额
        - acos: ACoS
        - roas: ROAS
        """
        total_budget = sum(c.get('current_budget', 0) for c in campaigns)
        total_sales = sum(c.get('sales', 0) for c in campaigns)
        
        # 计算每个活动的权重
        campaign_scores = []
        for campaign in campaigns:
            name = campaign.get('campaign_name', '')
            current_budget = campaign.get('current_budget', 0)
            sales = campaign.get('sales', 0)
            acos = campaign.get('acos', 100)
            roas = campaign.get('roas', 0)
            spend = campaign.get('spend', 0)
            
            # 计算表现分数
            # ROAS越高越好，ACoS越低越好
            roas_score = min(100, roas * 20)
            acos_score = max(0, 100 - acos * 2)
            sales_score = (sales / total_sales * 100) if total_sales > 0 else 0
            
            # 综合分数
            performance_score = (roas_score * 0.4 + acos_score * 0.4 + sales_score * 0.2)
            
            # 预算使用率
            budget_usage = (spend / current_budget * 100) if current_budget > 0 else 0
            
            campaign_scores.append({
                'campaign_name': name,
                'current_budget': current_budget,
                'performance_score': performance_score,
                'sales': sales,
                'acos': acos,
                'roas': roas,
                'budget_usage': budget_usage
            })
        
        # 按表现分数排序
        campaign_scores.sort(key=lambda x: x['performance_score'], reverse=True)
        
        # 重新分配预算
        recommendations = []
        for camp in campaign_scores:
            score = camp['performance_score']
            current = camp['current_budget']
            usage = camp['budget_usage']
            
            if score > 70 and usage > 80:
                # 高表现且预算快用完 - 增加预算
                suggested_change = current * 0.3
                action = '增加预算'
                new_budget = current + suggested_change
            elif score < 40:
                # 低表现 - 减少预算
                suggested_change = -current * 0.3
                action = '减少预算'
                new_budget = current + suggested_change
            elif score > 60 and usage < 50:
                # 好表现但预算未用完 - 适度增加
                suggested_change = current * 0.15
                action = '适度增加'
                new_budget = current + suggested_change
            else:
                # 保持不变
                suggested_change = 0
                action = '保持不变'
                new_budget = current
            
            recommendations.append({
                'campaign_name': camp['campaign_name'],
                'current_budget': round(current, 2),
                'suggested_budget': round(new_budget, 2),
                'change': round(suggested_change, 2),
                'change_percent': round((suggested_change / current * 100) if current > 0 else 0, 1),
                'action': action,
                'performance_score': round(score, 1),
                'reason': self._get_budget_reason(score, usage, camp['acos'])
            })
        
        return {
            'total_budget': round(total_budget, 2),
            'recommendations': recommendations
        }
    
    def _get_budget_reason(self, score: float, usage: float, acos: float) -> str:
        """获取预算调整原因"""
        if score > 70 and usage > 80:
            return f'高效活动(得分{score:.0f})且预算使用率高({usage:.0f}%)，应增加投入'
        elif score < 40:
            return f'表现不佳(得分{score:.0f})，ACoS为{acos:.1f}%，建议减少投入'
        elif acos < 20:
            return f'ACoS优秀({acos:.1f}%)，可以扩大规模'
        elif usage < 50:
            return f'预算使用率低({usage:.0f}%)，可能出价过低或关键词太少'
        else:
            return '表现稳定，保持当前策略'
    
    def suggest_negative_keywords(self, search_terms: List[Dict],
                                  min_spend: float = 5.0,
                                  max_acos: float = 50.0) -> List[Dict]:
        """
        建议否定关键词
        
        每个搜索词应包含：
        - search_term: 搜索词
        - impressions: 展示量
        - clicks: 点击量
        - spend: 花费
        - sales: 销售额
        - orders: 订单数
        """
        negative_suggestions = []
        
        for term_data in search_terms:
            search_term = term_data.get('search_term', '')
            clicks = term_data.get('clicks', 0)
            spend = term_data.get('spend', 0)
            sales = term_data.get('sales', 0)
            orders = term_data.get('orders', 0)
            
            # 计算ACoS
            acos = (spend / sales * 100) if sales > 0 else float('inf')
            
            # 判断是否应该加入否定关键词
            should_negate = False
            reason = ''
            
            # 有花费但没有转化
            if spend >= min_spend and orders == 0:
                should_negate = True
                reason = f'花费${spend:.2f}但无转化'
            
            # ACoS过高
            elif sales > 0 and acos > max_acos:
                should_negate = True
                reason = f'ACoS过高({acos:.1f}%)，不划算'
            
            # 点击多但无转化
            elif clicks >= 10 and orders == 0:
                should_negate = True
                reason = f'{clicks}次点击但无转化'
            
            if should_negate:
                # 判断否定类型（精确 vs 短语 vs 广泛）
                if len(search_term.split()) == 1:
                    match_type = 'exact'  # 单词用精确否定
                elif len(search_term.split()) <= 3:
                    match_type = 'phrase'  # 短语否定
                else:
                    match_type = 'broad'  # 广泛否定
                
                negative_suggestions.append({
                    'search_term': search_term,
                    'match_type': match_type,
                    'spend': round(spend, 2),
                    'clicks': clicks,
                    'orders': orders,
                    'acos': round(acos, 1) if sales > 0 else 'N/A',
                    'reason': reason,
                    'priority': 'high' if spend >= min_spend * 2 else 'medium'
                })
        
        # 按花费排序
        negative_suggestions.sort(key=lambda x: x['spend'], reverse=True)
        
        return negative_suggestions
    
    def calculate_optimal_bid(self, keyword_data: Dict) -> Dict:
        """
        计算最优出价
        
        参数：
        - current_bid: 当前出价
        - avg_position: 平均排名
        - cvr: 转化率
        - avg_order_value: 平均订单价值
        - target_acos: 目标ACoS
        - profit_margin: 利润率
        """
        current_bid = keyword_data.get('current_bid', 1.0)
        avg_position = keyword_data.get('avg_position', 50)
        cvr = keyword_data.get('cvr', 10) / 100  # 转换为小数
        avg_order_value = keyword_data.get('avg_order_value', 30)
        target_acos = keyword_data.get('target_acos', self.target_acos) / 100
        profit_margin = keyword_data.get('profit_margin', 30) / 100
        
        # 计算最大可承受CPC
        # Max CPC = (订单价值 × 转化率 × 目标ACoS)
        max_cpc = avg_order_value * cvr * target_acos
        
        # 计算盈亏平衡CPC
        break_even_cpc = avg_order_value * cvr * profit_margin
        
        # 根据当前排名调整建议出价
        if avg_position > 20:  # 排名靠后
            suggested_bid = min(max_cpc * 1.2, current_bid * 1.3)
            action = '提高出价以改善排名'
        elif avg_position < 5:  # 排名很好
            suggested_bid = max(max_cpc * 0.8, current_bid * 0.9)
            action = '可以适当降低出价以提高利润'
        else:  # 排名适中
            suggested_bid = max_cpc
            action = '维持在目标ACoS水平'
        
        # 确保不超过最大CPC限制
        suggested_bid = min(suggested_bid, self.max_cpc)
        
        return {
            'current_bid': round(current_bid, 2),
            'suggested_bid': round(suggested_bid, 2),
            'max_cpc': round(max_cpc, 2),
            'break_even_cpc': round(break_even_cpc, 2),
            'bid_change': round(suggested_bid - current_bid, 2),
            'bid_change_percent': round((suggested_bid - current_bid) / current_bid * 100, 1),
            'action': action,
            'avg_position': avg_position
        }
