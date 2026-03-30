"""
库存管理模块 - Inventory Management Module
功能：库存预警、周转率分析、补货建议、安全库存计算
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class InventoryManager:
    """库存管理工具"""
    
    def __init__(self, config):
        self.config = config
        self.low_stock_days = config.INVENTORY['low_stock_days']
        self.reorder_point_factor = config.INVENTORY['reorder_point_factor']
        self.safety_stock_days = config.INVENTORY['safety_stock_days']
    
    def analyze_inventory(self, inventory_data: Dict) -> Dict:
        """
        分析库存状态
        
        参数：
        - current_stock: 当前库存量
        - daily_sales_avg: 日均销量
        - lead_time_days: 补货周期（天）
        - safety_stock: 安全库存（可选）
        """
        current_stock = inventory_data.get('current_stock', 0)
        daily_sales_avg = inventory_data.get('daily_sales_avg', 0)
        lead_time_days = inventory_data.get('lead_time_days', 30)
        safety_stock = inventory_data.get('safety_stock')
        
        # 计算安全库存（如果未提供）
        if safety_stock is None:
            safety_stock = daily_sales_avg * self.safety_stock_days
        
        # 计算补货点
        reorder_point = (daily_sales_avg * lead_time_days * self.reorder_point_factor) + safety_stock
        
        # 计算可用天数
        days_of_stock = (current_stock / daily_sales_avg) if daily_sales_avg > 0 else float('inf')
        
        # 库存状态判断
        if days_of_stock <= 7:
            status = 'critical'
            status_text = '严重缺货'
            urgency = 'high'
        elif days_of_stock <= self.low_stock_days:
            status = 'low'
            status_text = '库存偏低'
            urgency = 'medium'
        elif days_of_stock <= 60:
            status = 'normal'
            status_text = '库存正常'
            urgency = 'low'
        else:
            status = 'excess'
            status_text = '库存过剩'
            urgency = 'low'
        
        # 是否需要补货
        need_reorder = current_stock <= reorder_point
        
        return {
            'current_stock': int(current_stock),
            'days_of_stock': round(days_of_stock, 1),
            'status': status,
            'status_text': status_text,
            'urgency': urgency,
            'reorder_point': round(reorder_point, 0),
            'safety_stock': round(safety_stock, 0),
            'need_reorder': need_reorder,
            'daily_sales_avg': round(daily_sales_avg, 2),
            'lead_time_days': lead_time_days
        }
    
    def calculate_reorder_quantity(self, inventory_data: Dict) -> Dict:
        """
        计算建议补货数量
        
        使用经济订货量(EOQ)模型
        """
        annual_demand = inventory_data.get('annual_demand', 0)
        ordering_cost = inventory_data.get('ordering_cost', 50)  # 每次订货成本
        holding_cost_rate = inventory_data.get('holding_cost_rate', 0.2)  # 持有成本率
        unit_cost = inventory_data.get('unit_cost', 10)
        daily_sales_avg = inventory_data.get('daily_sales_avg', 0)
        lead_time_days = inventory_data.get('lead_time_days', 30)
        current_stock = inventory_data.get('current_stock', 0)
        
        # 如果没有年需求，根据日均销量计算
        if annual_demand == 0:
            annual_demand = daily_sales_avg * 365
        
        # 计算持有成本
        holding_cost = unit_cost * holding_cost_rate
        
        # 经济订货量 (EOQ)
        if holding_cost > 0:
            eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        else:
            eoq = daily_sales_avg * 90  # 默认3个月的量
        
        # 安全库存
        safety_stock = daily_sales_avg * self.safety_stock_days
        
        # 补货点
        reorder_point = (daily_sales_avg * lead_time_days) + safety_stock
        
        # 建议订货量
        if current_stock < reorder_point:
            suggested_order = max(eoq, reorder_point - current_stock + (daily_sales_avg * lead_time_days))
        else:
            suggested_order = 0
        
        # 计算补货后库存可用天数
        stock_after_reorder = current_stock + suggested_order
        days_after_reorder = (stock_after_reorder / daily_sales_avg) if daily_sales_avg > 0 else 0
        
        # 计算订货成本
        total_order_cost = (suggested_order * unit_cost) + ordering_cost
        
        return {
            'eoq': round(eoq, 0),
            'suggested_order_quantity': round(suggested_order, 0),
            'reorder_point': round(reorder_point, 0),
            'safety_stock': round(safety_stock, 0),
            'stock_after_reorder': round(stock_after_reorder, 0),
            'days_after_reorder': round(days_after_reorder, 1),
            'total_order_cost': round(total_order_cost, 2),
            'should_order_now': current_stock < reorder_point,
            'ordering_cost': ordering_cost,
            'holding_cost_per_unit': round(holding_cost, 2)
        }
    
    def calculate_turnover_rate(self, sales_data: Dict) -> Dict:
        """
        计算库存周转率
        
        参数：
        - cost_of_goods_sold: 销售成本
        - avg_inventory: 平均库存价值
        - period_days: 统计周期（天）
        """
        cogs = sales_data.get('cost_of_goods_sold', 0)
        avg_inventory = sales_data.get('avg_inventory', 0)
        period_days = sales_data.get('period_days', 365)
        
        # 库存周转率
        if avg_inventory > 0:
            turnover_rate = cogs / avg_inventory
        else:
            turnover_rate = 0
        
        # 库存周转天数
        if turnover_rate > 0:
            days_in_inventory = period_days / turnover_rate
        else:
            days_in_inventory = 0
        
        # 评估周转率
        if turnover_rate >= 12:  # 一年12次以上
            rating = '优秀'
            comment = '库存周转非常快，资金利用率高'
        elif turnover_rate >= 6:  # 一年6-12次
            rating = '良好'
            comment = '库存周转较快，运营健康'
        elif turnover_rate >= 4:  # 一年4-6次
            rating = '一般'
            comment = '库存周转正常，有优化空间'
        elif turnover_rate >= 2:  # 一年2-4次
            rating = '偏低'
            comment = '库存周转较慢，需要优化'
        else:
            rating = '差'
            comment = '库存周转很慢，存在积压风险'
        
        return {
            'turnover_rate': round(turnover_rate, 2),
            'days_in_inventory': round(days_in_inventory, 1),
            'rating': rating,
            'comment': comment,
            'cost_of_goods_sold': round(cogs, 2),
            'avg_inventory_value': round(avg_inventory, 2)
        }
    
    def generate_restock_plan(self, products: List[Dict]) -> pd.DataFrame:
        """
        生成批量补货计划
        
        每个产品应包含：
        - product_name: 产品名称
        - current_stock: 当前库存
        - daily_sales_avg: 日均销量
        - lead_time_days: 补货周期
        - unit_cost: 单位成本
        """
        restock_plan = []
        
        for product in products:
            # 分析库存
            inventory_analysis = self.analyze_inventory(product)
            
            # 计算补货量
            reorder_calc = self.calculate_reorder_quantity(product)
            
            # 只添加需要补货的产品
            if reorder_calc['should_order_now']:
                restock_plan.append({
                    'product_name': product.get('product_name', 'Unknown'),
                    'current_stock': inventory_analysis['current_stock'],
                    'days_of_stock': inventory_analysis['days_of_stock'],
                    'status': inventory_analysis['status_text'],
                    'urgency': inventory_analysis['urgency'],
                    'suggested_order': reorder_calc['suggested_order_quantity'],
                    'order_cost': reorder_calc['total_order_cost'],
                    'days_after_reorder': reorder_calc['days_after_reorder'],
                    'daily_sales': inventory_analysis['daily_sales_avg']
                })
        
        # 转换为DataFrame并排序
        if restock_plan:
            df = pd.DataFrame(restock_plan)
            # 按紧急程度和可用天数排序
            urgency_order = {'high': 1, 'medium': 2, 'low': 3}
            df['urgency_score'] = df['urgency'].map(urgency_order)
            df = df.sort_values(['urgency_score', 'days_of_stock'])
            df = df.drop('urgency_score', axis=1)
            return df
        else:
            return pd.DataFrame()
    
    def forecast_inventory_needs(self, forecast_sales: float, 
                                 current_stock: int,
                                 daily_sales_avg: float,
                                 lead_time_days: int,
                                 forecast_days: int = 30) -> Dict:
        """
        预测未来库存需求
        
        参数：
        - forecast_sales: 预测销售额
        - current_stock: 当前库存
        - daily_sales_avg: 日均销量
        - lead_time_days: 补货周期
        - forecast_days: 预测天数
        """
        # 预测期间总需求
        forecast_demand = daily_sales_avg * forecast_days
        
        # 安全库存
        safety_stock = daily_sales_avg * self.safety_stock_days
        
        # 计算预测期末的库存
        ending_stock = current_stock - forecast_demand
        
        # 需要补货的数量
        if ending_stock < safety_stock:
            needed_quantity = (safety_stock - ending_stock) + (daily_sales_avg * lead_time_days)
        else:
            needed_quantity = 0
        
        # 补货时间点
        days_until_reorder = (current_stock - safety_stock) / daily_sales_avg if daily_sales_avg > 0 else 0
        days_until_stockout = current_stock / daily_sales_avg if daily_sales_avg > 0 else 0
        
        return {
            'forecast_days': forecast_days,
            'forecast_demand': round(forecast_demand, 0),
            'current_stock': current_stock,
            'ending_stock': round(ending_stock, 0),
            'safety_stock': round(safety_stock, 0),
            'needed_quantity': round(needed_quantity, 0),
            'days_until_reorder': round(max(0, days_until_reorder), 1),
            'days_until_stockout': round(max(0, days_until_stockout), 1),
            'stockout_risk': 'high' if days_until_stockout < 14 else 'medium' if days_until_stockout < 30 else 'low',
            'recommendation': self._get_inventory_recommendation(days_until_stockout, needed_quantity)
        }
    
    def _get_inventory_recommendation(self, days_until_stockout: float, 
                                     needed_quantity: float) -> str:
        """获取库存建议"""
        if days_until_stockout < 7:
            return f"🚨 紧急！预计{days_until_stockout:.0f}天内断货，立即补货{needed_quantity:.0f}件"
        elif days_until_stockout < 14:
            return f"⚠️ 警告！预计{days_until_stockout:.0f}天内断货，建议尽快补货{needed_quantity:.0f}件"
        elif days_until_stockout < 30:
            return f"💡 提醒：预计{days_until_stockout:.0f}天内需要补货{needed_quantity:.0f}件"
        else:
            return f"✅ 库存充足，预计{days_until_stockout:.0f}天内无需补货"
    
    def analyze_slow_moving_inventory(self, inventory_df: pd.DataFrame,
                                      days_threshold: int = 90) -> pd.DataFrame:
        """
        分析滞销库存
        
        DataFrame应包含：
        - product_name: 产品名称
        - current_stock: 当前库存
        - daily_sales_avg: 日均销量
        - unit_cost: 单位成本
        - days_in_stock: 库存天数
        """
        if inventory_df.empty:
            return pd.DataFrame()
        
        # 计算库存可用天数
        inventory_df['days_of_supply'] = inventory_df['current_stock'] / inventory_df['daily_sales_avg']
        
        # 计算库存价值
        inventory_df['inventory_value'] = inventory_df['current_stock'] * inventory_df['unit_cost']
        
        # 筛选滞销产品
        slow_moving = inventory_df[inventory_df['days_of_supply'] > days_threshold].copy()
        
        # 添加建议
        def get_action(days):
            if days > 180:
                return '清仓处理'
            elif days > 120:
                return '大幅促销'
            else:
                return '适度促销'
        
        if not slow_moving.empty:
            slow_moving['recommended_action'] = slow_moving['days_of_supply'].apply(get_action)
            slow_moving = slow_moving.sort_values('days_of_supply', ascending=False)
        
        return slow_moving[['product_name', 'current_stock', 'days_of_supply', 
                           'inventory_value', 'recommended_action']]
