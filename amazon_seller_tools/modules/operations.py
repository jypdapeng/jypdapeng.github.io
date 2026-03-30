"""
运营管理模块 - Operations Management Module
功能：销售分析、绩效追踪、报表生成、趋势预测
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
import seaborn as sns

class OperationsManager:
    """运营管理工具"""
    
    def __init__(self, config):
        self.config = config
        # 设置中文字体（避免中文乱码）
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def analyze_sales_data(self, sales_df: pd.DataFrame) -> Dict:
        """
        分析销售数据
        
        DataFrame应包含列：
        - date: 日期
        - sales: 销售额
        - units: 销量
        - orders: 订单数
        """
        if sales_df.empty:
            return {'error': '没有销售数据'}
        
        # 确保日期列是datetime类型
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        sales_df = sales_df.sort_values('date')
        
        # 基础统计
        total_sales = sales_df['sales'].sum()
        total_units = sales_df['units'].sum()
        total_orders = sales_df['orders'].sum()
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        avg_units_per_order = total_units / total_orders if total_orders > 0 else 0
        
        # 时间范围
        date_range = (sales_df['date'].max() - sales_df['date'].min()).days + 1
        
        # 日均数据
        daily_avg_sales = total_sales / date_range if date_range > 0 else 0
        daily_avg_units = total_units / date_range if date_range > 0 else 0
        daily_avg_orders = total_orders / date_range if date_range > 0 else 0
        
        # 趋势分析（最近7天 vs 之前7天）
        if len(sales_df) >= 14:
            recent_7_days = sales_df.tail(7)['sales'].sum()
            previous_7_days = sales_df.iloc[-14:-7]['sales'].sum()
            growth_rate = ((recent_7_days - previous_7_days) / previous_7_days * 100) if previous_7_days > 0 else 0
        else:
            growth_rate = 0
        
        # 最佳和最差销售日
        best_day = sales_df.loc[sales_df['sales'].idxmax()]
        worst_day = sales_df.loc[sales_df['sales'].idxmin()]
        
        return {
            'summary': {
                'total_sales': round(total_sales, 2),
                'total_units': int(total_units),
                'total_orders': int(total_orders),
                'avg_order_value': round(avg_order_value, 2),
                'avg_units_per_order': round(avg_units_per_order, 2)
            },
            'daily_averages': {
                'sales': round(daily_avg_sales, 2),
                'units': round(daily_avg_units, 2),
                'orders': round(daily_avg_orders, 2)
            },
            'trend': {
                'growth_rate_7d': round(growth_rate, 2),
                'trend_direction': 'upward' if growth_rate > 0 else 'downward' if growth_rate < 0 else 'stable'
            },
            'best_day': {
                'date': best_day['date'].strftime('%Y-%m-%d'),
                'sales': round(best_day['sales'], 2),
                'units': int(best_day['units'])
            },
            'worst_day': {
                'date': worst_day['date'].strftime('%Y-%m-%d'),
                'sales': round(worst_day['sales'], 2),
                'units': int(worst_day['units'])
            },
            'date_range': {
                'start': sales_df['date'].min().strftime('%Y-%m-%d'),
                'end': sales_df['date'].max().strftime('%Y-%m-%d'),
                'days': date_range
            }
        }
    
    def calculate_kpis(self, data: Dict) -> Dict:
        """
        计算关键绩效指标 (KPIs)
        
        参数：
        - sales: 销售额
        - ad_spend: 广告支出
        - units_sold: 销量
        - sessions: 访问量
        - orders: 订单数
        - returns: 退货数
        - total_costs: 总成本
        """
        sales = data.get('sales', 0)
        ad_spend = data.get('ad_spend', 0)
        units_sold = data.get('units_sold', 0)
        sessions = data.get('sessions', 0)
        orders = data.get('orders', 0)
        returns = data.get('returns', 0)
        total_costs = data.get('total_costs', 0)
        
        # ACoS (广告成本销售比)
        acos = (ad_spend / sales * 100) if sales > 0 else 0
        
        # TACoS (总广告成本销售比)
        tacos = (ad_spend / sales * 100) if sales > 0 else 0
        
        # 转化率
        conversion_rate = (orders / sessions * 100) if sessions > 0 else 0
        
        # 退货率
        return_rate = (returns / units_sold * 100) if units_sold > 0 else 0
        
        # ROI (投资回报率)
        roi = ((sales - total_costs) / total_costs * 100) if total_costs > 0 else 0
        
        # ROAS (广告支出回报率)
        roas = (sales / ad_spend) if ad_spend > 0 else 0
        
        # 利润
        profit = sales - total_costs
        profit_margin = (profit / sales * 100) if sales > 0 else 0
        
        # 绩效评级
        performance_grade = self._calculate_performance_grade(
            acos, conversion_rate, return_rate, profit_margin
        )
        
        return {
            'acos': round(acos, 2),
            'tacos': round(tacos, 2),
            'conversion_rate': round(conversion_rate, 2),
            'return_rate': round(return_rate, 2),
            'roi': round(roi, 2),
            'roas': round(roas, 2),
            'profit': round(profit, 2),
            'profit_margin': round(profit_margin, 2),
            'performance_grade': performance_grade,
            'recommendations': self._get_kpi_recommendations(acos, conversion_rate, return_rate, profit_margin)
        }
    
    def _calculate_performance_grade(self, acos: float, conversion: float,
                                     return_rate: float, profit_margin: float) -> str:
        """计算绩效评级"""
        score = 0
        
        # ACoS评分（越低越好，目标<30%）
        if acos < 20:
            score += 30
        elif acos < 30:
            score += 20
        elif acos < 40:
            score += 10
        
        # 转化率评分（越高越好，目标>10%）
        if conversion > 15:
            score += 30
        elif conversion > 10:
            score += 20
        elif conversion > 5:
            score += 10
        
        # 退货率评分（越低越好，目标<5%）
        if return_rate < 3:
            score += 20
        elif return_rate < 5:
            score += 15
        elif return_rate < 10:
            score += 5
        
        # 利润率评分（越高越好，目标>30%）
        if profit_margin > 40:
            score += 20
        elif profit_margin > 30:
            score += 15
        elif profit_margin > 20:
            score += 10
        
        if score >= 80:
            return 'A+ (卓越)'
        elif score >= 70:
            return 'A (优秀)'
        elif score >= 60:
            return 'B (良好)'
        elif score >= 50:
            return 'C (中等)'
        else:
            return 'D (需改进)'
    
    def _get_kpi_recommendations(self, acos: float, conversion: float,
                                return_rate: float, profit_margin: float) -> List[str]:
        """获取KPI改进建议"""
        recommendations = []
        
        if acos > 30:
            recommendations.append("🎯 ACoS偏高，建议优化广告投放策略，降低广告成本")
        
        if conversion < 10:
            recommendations.append("📈 转化率较低，建议优化产品页面、图片和描述")
        
        if return_rate > 5:
            recommendations.append("⚠️ 退货率偏高，检查产品质量和描述准确性")
        
        if profit_margin < 30:
            recommendations.append("💰 利润率较低，考虑优化成本结构或提高售价")
        
        if conversion > 15 and acos < 25:
            recommendations.append("✅ 表现优秀！继续保持当前策略")
        
        return recommendations
    
    def forecast_sales(self, sales_df: pd.DataFrame, days: int = 30) -> Dict:
        """
        销售预测（简单移动平均）
        
        参数：
        - sales_df: 历史销售数据
        - days: 预测天数
        """
        if len(sales_df) < 7:
            return {'error': '数据不足，至少需要7天历史数据'}
        
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        sales_df = sales_df.sort_values('date')
        
        # 使用最近30天的平均值进行预测
        recent_data = sales_df.tail(min(30, len(sales_df)))
        avg_daily_sales = recent_data['sales'].mean()
        avg_daily_units = recent_data['units'].mean()
        
        # 计算趋势（简单线性）
        if len(recent_data) > 1:
            x = np.arange(len(recent_data))
            y = recent_data['sales'].values
            z = np.polyfit(x, y, 1)
            trend = z[0]  # 斜率
        else:
            trend = 0
        
        # 预测
        last_date = sales_df['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        forecast_sales = [avg_daily_sales + trend * i for i in range(days)]
        forecast_units = [avg_daily_units * (1 + trend / avg_daily_sales) ** i for i in range(days)]
        
        total_forecast_sales = sum(forecast_sales)
        total_forecast_units = sum(forecast_units)
        
        return {
            'forecast_period': days,
            'total_forecast_sales': round(total_forecast_sales, 2),
            'total_forecast_units': round(total_forecast_units, 0),
            'avg_daily_forecast_sales': round(avg_daily_sales, 2),
            'avg_daily_forecast_units': round(avg_daily_units, 2),
            'trend': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'daily_forecast': [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'sales': round(sales, 2),
                    'units': round(units, 0)
                }
                for date, sales, units in zip(forecast_dates, forecast_sales, forecast_units)
            ][:10]  # 只返回前10天详情
        }
    
    def generate_performance_report(self, sales_df: pd.DataFrame, kpi_data: Dict) -> str:
        """
        生成绩效报告
        """
        sales_analysis = self.analyze_sales_data(sales_df)
        kpis = self.calculate_kpis(kpi_data)
        forecast = self.forecast_sales(sales_df)
        
        report = f"""
========================================
        亚马逊店铺绩效报告
========================================
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 销售概况
----------------------------------------
总销售额: ${sales_analysis['summary']['total_sales']:,.2f}
总销量: {sales_analysis['summary']['total_units']:,} 件
总订单数: {sales_analysis['summary']['total_orders']:,}
平均客单价: ${sales_analysis['summary']['avg_order_value']:.2f}
数据周期: {sales_analysis['date_range']['start']} 至 {sales_analysis['date_range']['end']}

📈 日均表现
----------------------------------------
日均销售额: ${sales_analysis['daily_averages']['sales']:.2f}
日均销量: {sales_analysis['daily_averages']['units']:.0f} 件
日均订单数: {sales_analysis['daily_averages']['orders']:.0f}

📉 趋势分析
----------------------------------------
7天增长率: {sales_analysis['trend']['growth_rate_7d']:.2f}%
趋势方向: {sales_analysis['trend']['trend_direction']}

🎯 关键指标 (KPIs)
----------------------------------------
ACoS: {kpis['acos']:.2f}%
转化率: {kpis['conversion_rate']:.2f}%
退货率: {kpis['return_rate']:.2f}%
利润率: {kpis['profit_margin']:.2f}%
ROI: {kpis['roi']:.2f}%
ROAS: {kpis['roas']:.2f}
绩效评级: {kpis['performance_grade']}

💡 改进建议
----------------------------------------
"""
        for i, rec in enumerate(kpis['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        if 'error' not in forecast:
            report += f"""
🔮 未来30天预测
----------------------------------------
预计总销售额: ${forecast['total_forecast_sales']:,.2f}
预计总销量: {forecast['total_forecast_units']:,.0f} 件
日均预期销售: ${forecast['avg_daily_forecast_sales']:.2f}
趋势: {forecast['trend']}
"""
        
        report += "\n========================================"
        
        return report
    
    def export_to_excel(self, data: Dict, filename: str) -> str:
        """
        导出数据到Excel
        """
        import os
        from config import Config
        
        export_path = Config.EXPORT_PATH
        os.makedirs(export_path, exist_ok=True)
        
        filepath = os.path.join(export_path, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                if isinstance(df, pd.DataFrame):
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return filepath
