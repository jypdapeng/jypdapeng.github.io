"""
排名分析模块 - Ranking Analysis Module
功能：关键词排名追踪、排名变化趋势、竞争分析、排名优化建议
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class RankingAnalyzer:
    """排名分析工具"""
    
    def __init__(self, config):
        self.config = config
    
    def track_keyword_rankings(self, ranking_data: List[Dict]) -> pd.DataFrame:
        """
        追踪关键词排名
        
        每条记录应包含：
        - keyword: 关键词
        - date: 日期
        - rank: 排名
        - page: 页码
        - search_volume: 搜索量（可选）
        """
        df = pd.DataFrame(ranking_data)
        
        if df.empty:
            return df
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date'])
        
        # 按关键词和日期排序
        df = df.sort_values(['keyword', 'date'])
        
        # 计算排名变化
        df['rank_change'] = df.groupby('keyword')['rank'].diff()
        
        # 计算移动平均排名
        df['rank_ma7'] = df.groupby('keyword')['rank'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # 排名趋势
        def get_trend(changes):
            if pd.isna(changes):
                return 'stable'
            elif changes < -2:
                return 'improving'  # 排名数字变小是改善
            elif changes > 2:
                return 'declining'
            else:
                return 'stable'
        
        df['trend'] = df['rank_change'].apply(get_trend)
        
        return df
    
    def analyze_ranking_performance(self, ranking_df: pd.DataFrame) -> Dict:
        """
        分析排名表现
        
        提供整体排名分析
        """
        if ranking_df.empty:
            return {'error': '没有排名数据'}
        
        # 获取最新排名
        latest_rankings = ranking_df.sort_values('date').groupby('keyword').last()
        
        # 统计各页面分布
        page_1_count = len(latest_rankings[latest_rankings['page'] == 1])
        page_2_3_count = len(latest_rankings[latest_rankings['page'].isin([2, 3])])
        beyond_page_3 = len(latest_rankings[latest_rankings['page'] > 3])
        
        # 统计趋势
        improving = len(latest_rankings[latest_rankings['trend'] == 'improving'])
        declining = len(latest_rankings[latest_rankings['trend'] == 'declining'])
        stable = len(latest_rankings[latest_rankings['trend'] == 'stable'])
        
        # 平均排名
        avg_rank = latest_rankings['rank'].mean()
        median_rank = latest_rankings['rank'].median()
        
        # 最佳和最差关键词
        best_keyword = latest_rankings.nsmallest(1, 'rank')
        worst_keyword = latest_rankings.nlargest(1, 'rank')
        
        # 计算排名得分（0-100）
        rank_score = self._calculate_ranking_score(
            page_1_count, 
            len(latest_rankings),
            avg_rank
        )
        
        return {
            'summary': {
                'total_keywords': len(latest_rankings),
                'avg_rank': round(avg_rank, 1),
                'median_rank': round(median_rank, 1),
                'rank_score': round(rank_score, 1)
            },
            'page_distribution': {
                'page_1': page_1_count,
                'page_2_3': page_2_3_count,
                'beyond_page_3': beyond_page_3,
                'page_1_percentage': round(page_1_count / len(latest_rankings) * 100, 1)
            },
            'trend_analysis': {
                'improving': improving,
                'declining': declining,
                'stable': stable,
                'improving_percentage': round(improving / len(latest_rankings) * 100, 1)
            },
            'best_keyword': {
                'keyword': best_keyword.index[0] if not best_keyword.empty else 'N/A',
                'rank': int(best_keyword['rank'].values[0]) if not best_keyword.empty else 0
            },
            'worst_keyword': {
                'keyword': worst_keyword.index[0] if not worst_keyword.empty else 'N/A',
                'rank': int(worst_keyword['rank'].values[0]) if not worst_keyword.empty else 0
            },
            'recommendations': self._get_ranking_recommendations(
                page_1_count, len(latest_rankings), improving, declining
            )
        }
    
    def _calculate_ranking_score(self, page_1_count: int, 
                                 total_keywords: int, 
                                 avg_rank: float) -> float:
        """计算排名得分"""
        # 第一页关键词占比得分（60分）
        page_1_score = (page_1_count / total_keywords) * 60 if total_keywords > 0 else 0
        
        # 平均排名得分（40分）
        # 排名1-10: 40分，11-20: 30分，21-30: 20分，30+: 10分
        if avg_rank <= 10:
            avg_rank_score = 40
        elif avg_rank <= 20:
            avg_rank_score = 30
        elif avg_rank <= 30:
            avg_rank_score = 20
        else:
            avg_rank_score = max(0, 40 - (avg_rank - 10) * 0.5)
        
        return page_1_score + avg_rank_score
    
    def _get_ranking_recommendations(self, page_1: int, total: int,
                                    improving: int, declining: int) -> List[str]:
        """获取排名优化建议"""
        recommendations = []
        
        page_1_pct = (page_1 / total * 100) if total > 0 else 0
        
        if page_1_pct < 30:
            recommendations.append("🎯 第一页关键词占比较低，需要加强SEO优化和广告投放")
        
        if declining > improving:
            recommendations.append("⚠️ 下降趋势明显，检查竞品动态和调整优化策略")
        
        if page_1_pct > 50:
            recommendations.append("✅ 第一页排名表现良好，继续保持并扩展更多关键词")
        
        if improving > total * 0.3:
            recommendations.append("📈 多数关键词排名上升，当前策略有效")
        
        recommendations.append("💡 定期监控排名变化，及时调整广告和内容策略")
        
        return recommendations
    
    def identify_ranking_opportunities(self, ranking_df: pd.DataFrame,
                                      target_page: int = 1) -> pd.DataFrame:
        """
        识别排名提升机会
        
        找出接近目标页面的关键词
        """
        if ranking_df.empty:
            return pd.DataFrame()
        
        # 获取最新排名
        latest = ranking_df.sort_values('date').groupby('keyword').last().reset_index()
        
        # 筛选接近目标页面的关键词
        if target_page == 1:
            # 排名在11-30之间，有机会冲击第一页
            opportunities = latest[
                (latest['rank'] > 10) & 
                (latest['rank'] <= 30)
            ].copy()
        else:
            target_rank_min = (target_page - 1) * 48 + 1
            target_rank_max = target_page * 48
            opportunities = latest[
                (latest['rank'] > target_rank_max) & 
                (latest['rank'] <= target_rank_max + 48)
            ].copy()
        
        if opportunities.empty:
            return pd.DataFrame()
        
        # 计算提升潜力分数
        opportunities['opportunity_score'] = opportunities.apply(
            lambda row: self._calculate_opportunity_score(
                row['rank'], 
                row.get('search_volume', 0),
                row.get('trend', 'stable')
            ),
            axis=1
        )
        
        # 添加建议
        opportunities['suggestion'] = opportunities.apply(
            lambda row: self._get_opportunity_suggestion(row['rank'], row['trend']),
            axis=1
        )
        
        # 排序
        opportunities = opportunities.sort_values('opportunity_score', ascending=False)
        
        return opportunities[['keyword', 'rank', 'page', 'trend', 
                             'opportunity_score', 'suggestion']]
    
    def _calculate_opportunity_score(self, rank: int, 
                                    search_volume: int,
                                    trend: str) -> float:
        """计算机会分数"""
        # 基础分数：排名越靠前分数越高
        if rank <= 15:
            rank_score = 50
        elif rank <= 20:
            rank_score = 40
        elif rank <= 30:
            rank_score = 30
        else:
            rank_score = 20
        
        # 搜索量分数
        if search_volume > 10000:
            volume_score = 30
        elif search_volume > 5000:
            volume_score = 20
        elif search_volume > 1000:
            volume_score = 10
        else:
            volume_score = 5
        
        # 趋势分数
        if trend == 'improving':
            trend_score = 20
        elif trend == 'stable':
            trend_score = 10
        else:
            trend_score = 0
        
        return rank_score + volume_score + trend_score
    
    def _get_opportunity_suggestion(self, rank: int, trend: str) -> str:
        """获取机会建议"""
        if rank <= 15 and trend == 'improving':
            return '💎 高优先级：已接近第一页且趋势向上，加大广告投入'
        elif rank <= 15:
            return '🎯 中优先级：接近第一页，优化Listing和适度增加广告'
        elif rank <= 20 and trend == 'improving':
            return '📈 中优先级：排名上升中，持续优化'
        elif rank <= 30:
            return '💡 低优先级：需要系统性优化Listing和广告策略'
        else:
            return '⏳ 观察：排名较低，先优化其他更有潜力的关键词'
    
    def compare_with_competitors(self, my_rankings: List[Dict],
                                competitor_rankings: List[Dict]) -> pd.DataFrame:
        """
        与竞品排名对比
        
        my_rankings和competitor_rankings格式：
        - keyword: 关键词
        - rank: 排名
        - product_name: 产品名称（竞品需要）
        """
        my_df = pd.DataFrame(my_rankings)
        comp_df = pd.DataFrame(competitor_rankings)
        
        if my_df.empty or comp_df.empty:
            return pd.DataFrame()
        
        # 合并数据
        my_df = my_df.rename(columns={'rank': 'my_rank'})
        
        # 按关键词聚合竞品最佳排名
        comp_best = comp_df.groupby('keyword').agg({
            'rank': 'min',
            'product_name': 'first'
        }).reset_index()
        comp_best = comp_best.rename(columns={
            'rank': 'competitor_best_rank',
            'product_name': 'top_competitor'
        })
        
        # 合并
        comparison = pd.merge(my_df, comp_best, on='keyword', how='outer')
        
        # 计算排名差距
        comparison['rank_gap'] = comparison['my_rank'] - comparison['competitor_best_rank']
        
        # 竞争态势
        def get_competitive_status(row):
            if pd.isna(row['my_rank']):
                return '未排名'
            elif pd.isna(row['competitor_best_rank']):
                return '领先'
            elif row['rank_gap'] < -5:
                return '大幅领先'
            elif row['rank_gap'] < 0:
                return '领先'
            elif row['rank_gap'] == 0:
                return '持平'
            elif row['rank_gap'] <= 5:
                return '落后'
            else:
                return '大幅落后'
        
        comparison['status'] = comparison.apply(get_competitive_status, axis=1)
        
        # 优先级
        def get_priority(row):
            if row['status'] in ['大幅落后', '落后']:
                if pd.notna(row['my_rank']) and row['my_rank'] > 20:
                    return '高'
                else:
                    return '中'
            elif row['status'] == '未排名':
                return '高'
            else:
                return '低'
        
        comparison['priority'] = comparison.apply(get_priority, axis=1)
        
        # 排序
        comparison = comparison.sort_values('rank_gap', ascending=False)
        
        return comparison[['keyword', 'my_rank', 'competitor_best_rank', 
                          'rank_gap', 'status', 'top_competitor', 'priority']]
    
    def calculate_visibility_score(self, ranking_data: List[Dict]) -> Dict:
        """
        计算可见度分数
        
        基于关键词排名和搜索量计算整体可见度
        """
        df = pd.DataFrame(ranking_data)
        
        if df.empty:
            return {'error': '没有数据'}
        
        total_visibility = 0
        total_search_volume = 0
        
        for _, row in df.iterrows():
            rank = row.get('rank', 100)
            search_volume = row.get('search_volume', 0)
            
            # 根据排名计算可见度权重
            # 第1名: 100%, 第2名: 85%, 第3名: 70%...
            if rank == 1:
                visibility_weight = 1.0
            elif rank <= 3:
                visibility_weight = 0.85 - (rank - 2) * 0.15
            elif rank <= 10:
                visibility_weight = 0.70 - (rank - 3) * 0.07
            elif rank <= 20:
                visibility_weight = 0.21 - (rank - 10) * 0.015
            else:
                visibility_weight = max(0, 0.05 - (rank - 20) * 0.001)
            
            # 加权可见度
            weighted_visibility = search_volume * visibility_weight
            total_visibility += weighted_visibility
            total_search_volume += search_volume
        
        # 计算可见度分数（0-100）
        if total_search_volume > 0:
            visibility_score = (total_visibility / total_search_volume) * 100
        else:
            visibility_score = 0
        
        # 评级
        if visibility_score >= 60:
            rating = '优秀'
        elif visibility_score >= 40:
            rating = '良好'
        elif visibility_score >= 25:
            rating = '一般'
        elif visibility_score >= 10:
            rating = '偏低'
        else:
            rating = '很低'
        
        return {
            'visibility_score': round(visibility_score, 2),
            'rating': rating,
            'total_search_volume': int(total_search_volume),
            'weighted_visibility': round(total_visibility, 2),
            'recommendations': self._get_visibility_recommendations(visibility_score)
        }
    
    def _get_visibility_recommendations(self, score: float) -> List[str]:
        """获取可见度优化建议"""
        recommendations = []
        
        if score < 25:
            recommendations.append("🚨 可见度很低，需要大幅提升关键词排名")
            recommendations.append("📊 优先优化高搜索量关键词的排名")
            recommendations.append("💰 增加广告预算提升曝光")
        elif score < 40:
            recommendations.append("⚠️ 可见度偏低，继续优化主要关键词排名")
            recommendations.append("🎯 聚焦前20名关键词，争取进入前10")
        elif score < 60:
            recommendations.append("📈 可见度良好，继续提升核心关键词排名")
            recommendations.append("🔍 扩展长尾关键词覆盖")
        else:
            recommendations.append("✅ 可见度优秀！保持当前优化策略")
            recommendations.append("🌟 考虑扩展到更多相关关键词")
        
        return recommendations
