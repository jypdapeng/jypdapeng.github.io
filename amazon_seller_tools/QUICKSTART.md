# 快速开始指南

## 🚀 5分钟快速上手

### 第一步：启动系统

```bash
# 进入项目目录
cd /workspace/amazon_seller_tools

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动应用
python app.py
```

您会看到：
```
 * Running on http://0.0.0.0:5000
```

### 第二步：访问系统

打开浏览器访问：`http://localhost:5000`

### 第三步：尝试选品分析

1. 点击顶部导航栏的 **"选品分析"**
2. 在利润计算器中输入示例数据：
   - 售价: `29.99`
   - 产品成本: `10.00`
   - 亚马逊佣金: `15`
   - FBA费用: `4.50`
3. 点击 **"计算利润"**
4. 查看结果！

---

## 🎓 使用Python直接调用模块

如果您更喜欢用Python代码而不是Web界面：

### 示例1：计算产品利润

```python
from modules.product_research import ProductResearch
from config import Config

# 初始化
pr = ProductResearch(Config)

# 产品数据
product_data = {
    'selling_price': 29.99,
    'cost': 10.0,
    'amazon_fee_percentage': 15,
    'fba_fee': 4.5,
    'shipping_cost': 2.0,
    'other_costs': 1.0
}

# 计算利润
result = pr.calculate_profit(product_data)

print(f"净利润: ${result['profit']}")
print(f"利润率: {result['profit_margin']}%")
print(f"ROI: {result['roi']}%")
print(f"是否有利可图: {result['is_profitable']}")
```

### 示例2：产品综合评分

```python
from modules.product_research import ProductResearch
from config import Config

pr = ProductResearch(Config)

# 产品数据
product_data = {
    'selling_price': 35.0,
    'cost': 12.0,
    'amazon_fee_percentage': 15,
    'fba_fee': 5.0
}

# 市场数据
market_data = {
    'monthly_sales': 3000,
    'avg_price': 32.0,
    'avg_rating': 4.2,
    'review_count': 500,
    'top_sellers_count': 15,
    'search_volume': 50000
}

# 综合评分
result = pr.score_product(product_data, market_data)

print(f"\n{'='*50}")
print(f"产品综合评分: {result['total_score']}")
print(f"评级: {result['grade']}")
print(f"{'='*50}\n")

print("各项得分:")
print(f"  利润得分: {result['scores']['profit_score']}")
print(f"  ROI得分: {result['scores']['roi_score']}")
print(f"  市场吸引力: {result['scores']['market_score']}")
print(f"  竞争优势: {result['scores']['competition_score']}")

print(f"\n市场建议: {result['market_analysis']['recommendation']}")
print(f"\n最终建议:\n{result['recommendation']}")
```

### 示例3：分析库存

```python
from modules.inventory import InventoryManager
from config import Config

im = InventoryManager(Config)

# 库存数据
inventory_data = {
    'current_stock': 100,
    'daily_sales_avg': 5,
    'lead_time_days': 30
}

# 分析库存
result = im.analyze_inventory(inventory_data)

print(f"当前库存: {result['current_stock']} 件")
print(f"可用天数: {result['days_of_stock']} 天")
print(f"库存状态: {result['status_text']}")
print(f"紧急程度: {result['urgency']}")
print(f"是否需要补货: {'是' if result['need_reorder'] else '否'}")
print(f"建议补货点: {result['reorder_point']} 件")
```

### 示例4：优化广告

```python
from modules.advertising import AdvertisingOptimizer
from config import Config

ad = AdvertisingOptimizer(Config)

# 广告活动数据
campaign_data = {
    'impressions': 50000,
    'clicks': 500,
    'spend': 250,
    'sales': 625,
    'orders': 25
}

# 分析活动
result = ad.analyze_campaign_performance(campaign_data)

print(f"\n广告活动分析")
print(f"{'='*50}")
print(f"CTR: {result['metrics']['ctr']}%")
print(f"CPC: ${result['metrics']['cpc']}")
print(f"ACoS: {result['metrics']['acos']}%")
print(f"CVR: {result['metrics']['cvr']}%")
print(f"ROAS: {result['metrics']['roas']}")
print(f"\n综合评级: {result['performance']['overall_rating']}")
print(f"{'='*50}\n")

print("优化建议:")
for i, rec in enumerate(result['recommendations'], 1):
    print(f"{i}. {rec}")
```

### 示例5：Listing优化

```python
from modules.listing import ListingOptimizer
from config import Config

lo = ListingOptimizer(Config)

# 分析标题
title = "Bluetooth Headphones Wireless Earbuds"
result = lo.analyze_title(title)

print(f"\n标题分析")
print(f"{'='*50}")
print(f"标题: {result['title']}")
print(f"长度: {result['length']} 字符")
print(f"得分: {result['score']}")
print(f"评级: {result['grade']}")
print(f"{'='*50}\n")

print("优化建议:")
for i, suggestion in enumerate(result['suggestions'], 1):
    print(f"{i}. {suggestion}")
```

---

## 📊 使用测试数据

项目包含了示例数据，您可以直接使用：

```python
# 创建示例数据
import pandas as pd
from datetime import datetime, timedelta

# 生成30天销售数据
dates = [datetime.now() - timedelta(days=i) for i in range(30)]
sales_data = {
    'date': dates,
    'sales': [1000 + i*50 for i in range(30)],
    'units': [30 + i*2 for i in range(30)],
    'orders': [25 + i for i in range(30)]
}

df = pd.DataFrame(sales_data)

# 使用运营管理模块分析
from modules.operations import OperationsManager
from config import Config

ops = OperationsManager(Config)
result = ops.analyze_sales_data(df)

print("销售数据分析:")
print(f"总销售额: ${result['summary']['total_sales']}")
print(f"总销量: {result['summary']['total_units']} 件")
print(f"总订单数: {result['summary']['total_orders']}")
print(f"平均客单价: ${result['summary']['avg_order_value']}")
```

---

## 🔧 自定义配置

编辑 `config.py` 文件来调整默认参数：

```python
# 选品分析配置
PRODUCT_RESEARCH = {
    'min_profit_margin': 30,  # 最小利润率 (%)
    'min_monthly_sales': 300,  # 最小月销量
    'max_competition_score': 70,  # 最大竞争分数
}

# 库存管理配置
INVENTORY = {
    'low_stock_days': 30,  # 低库存预警天数
    'safety_stock_days': 7,  # 安全库存天数
}

# 广告配置
ADVERTISING = {
    'target_acos': 25,  # 目标ACoS (%)
    'max_cpc': 2.0,  # 最大CPC ($)
}
```

---

## 💡 提示和技巧

### 技巧1：批量分析产品

```python
from modules.product_research import ProductResearch
from config import Config
import pandas as pd

pr = ProductResearch(Config)

# 准备多个产品数据
products = [
    {
        'name': '产品A',
        'product_data': {'selling_price': 29.99, 'cost': 10, 'amazon_fee_percentage': 15, 'fba_fee': 4.5},
        'market_data': {'monthly_sales': 5000, 'avg_price': 28, 'avg_rating': 4.2, 'review_count': 500, 'top_sellers_count': 10, 'search_volume': 50000}
    },
    {
        'name': '产品B',
        'product_data': {'selling_price': 49.99, 'cost': 20, 'amazon_fee_percentage': 15, 'fba_fee': 6.0},
        'market_data': {'monthly_sales': 3000, 'avg_price': 45, 'avg_rating': 4.0, 'review_count': 300, 'top_sellers_count': 15, 'search_volume': 30000}
    }
]

# 批量对比
result_df = pr.compare_products(products)
print(result_df.to_string())
```

### 技巧2：导出Excel报告

```python
from modules.operations import OperationsManager
from config import Config
import pandas as pd

ops = OperationsManager(Config)

# 准备数据
data = {
    '销售数据': sales_df,
    'KPI指标': kpi_df,
    # ... 更多数据
}

# 导出Excel
filepath = ops.export_to_excel(data, '月度运营报告.xlsx')
print(f"报告已保存到: {filepath}")
```

### 技巧3：API集成

如果您想在自己的应用中集成这些功能：

```python
import requests

# 调用API
response = requests.post('http://localhost:5000/api/product-research/calculate-profit', 
    json={
        'selling_price': 29.99,
        'cost': 10.0,
        'amazon_fee_percentage': 15,
        'fba_fee': 4.5
    }
)

result = response.json()
if result['success']:
    print(result['data'])
```

---

## ❗ 常见错误解决

### 错误1：模块导入失败

```bash
ModuleNotFoundError: No module named 'flask'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

### 错误2：端口被占用

```bash
OSError: [Errno 48] Address already in use
```

**解决方案：**
修改 `app.py` 中的端口：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为5001或其他端口
```

### 错误3：中文显示乱码

**解决方案：**
确保您的终端支持UTF-8编码，或在代码中添加：
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

---

## 🎯 下一步

现在您已经掌握了基础使用，可以：

1. 📖 阅读完整的 [README.md](README.md) 了解所有功能
2. 🔍 探索各个模块的详细功能
3. 🛠️ 根据您的需求定制和扩展
4. 📊 导入您的真实数据进行分析
5. 🚀 在生产环境中部署使用

---

**祝您使用愉快！** 🎉
