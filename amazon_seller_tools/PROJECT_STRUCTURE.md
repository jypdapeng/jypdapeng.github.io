# 项目结构说明

## 📁 完整目录结构

```
amazon_seller_tools/
│
├── 📄 app.py                          # Flask主应用程序
├── 📄 config.py                       # 配置文件
├── 📄 requirements.txt                # Python依赖包
├── 📄 examples.py                     # 示例代码
├── 📄 README.md                       # 完整文档
├── 📄 QUICKSTART.md                   # 快速开始指南
├── 📄 .env.example                    # 环境变量模板
│
├── 📁 modules/                        # 核心功能模块
│   ├── __init__.py                    # 模块初始化
│   ├── product_research.py            # 选品分析模块
│   ├── operations.py                  # 运营管理模块
│   ├── inventory.py                   # 库存管理模块
│   ├── advertising.py                 # 广告优化模块
│   ├── ranking.py                     # 排名分析模块
│   ├── competitor.py                  # 竞品分析模块
│   └── listing.py                     # Listing优化模块
│
├── 📁 templates/                      # HTML模板
│   ├── index.html                     # 首页
│   ├── product_research.html          # 选品分析页面
│   ├── operations.html                # 运营管理页面
│   ├── inventory.html                 # 库存管理页面
│   ├── advertising.html               # 广告优化页面
│   ├── ranking.html                   # 排名分析页面
│   ├── competitor.html                # 竞品分析页面
│   └── listing.html                   # Listing优化页面
│
├── 📁 static/                         # 静态资源
│   ├── 📁 css/
│   │   └── style.css                  # 全局样式
│   ├── 📁 js/
│   │   └── main.js                    # 前端JavaScript
│   └── 📁 images/                     # 图片资源
│
├── 📁 data/                           # 数据存储
│   └── 📁 exports/                    # 导出文件
│
└── 📁 utils/                          # 工具函数（预留）
```

---

## 📦 核心模块详解

### 1. 📊 product_research.py - 选品分析模块

**类：** `ProductResearch`

**主要方法：**
- `calculate_profit(product_data)` - 计算产品利润
- `analyze_market_opportunity(market_data)` - 分析市场机会
- `score_product(product_data, market_data)` - 产品综合评分
- `compare_products(products)` - 批量产品对比

**功能特点：**
- ✅ 精确的利润计算（包含所有成本）
- ✅ 多维度市场分析
- ✅ 智能评分算法
- ✅ 竞争强度评估

---

### 2. 📈 operations.py - 运营管理模块

**类：** `OperationsManager`

**主要方法：**
- `analyze_sales_data(sales_df)` - 分析销售数据
- `calculate_kpis(data)` - 计算关键指标
- `forecast_sales(sales_df, days)` - 销售预测
- `generate_performance_report(sales_df, kpi_data)` - 生成绩效报告
- `export_to_excel(data, filename)` - 导出Excel

**功能特点：**
- ✅ 趋势分析（7日增长率）
- ✅ 多种KPI自动计算
- ✅ 简单移动平均预测
- ✅ 详细的绩效报告

---

### 3. 📦 inventory.py - 库存管理模块

**类：** `InventoryManager`

**主要方法：**
- `analyze_inventory(inventory_data)` - 分析库存状态
- `calculate_reorder_quantity(inventory_data)` - 计算补货量（EOQ模型）
- `calculate_turnover_rate(sales_data)` - 计算周转率
- `generate_restock_plan(products)` - 生成补货计划
- `forecast_inventory_needs(...)` - 预测库存需求
- `analyze_slow_moving_inventory(inventory_df)` - 分析滞销库存

**功能特点：**
- ✅ EOQ经济订货量模型
- ✅ 安全库存计算
- ✅ 库存周转率分析
- ✅ 多级别预警系统

---

### 4. 💰 advertising.py - 广告优化模块

**类：** `AdvertisingOptimizer`

**主要方法：**
- `analyze_campaign_performance(campaign_data)` - 分析广告活动
- `analyze_keywords(keywords_data)` - 关键词分析
- `optimize_budget_allocation(campaigns)` - 优化预算分配
- `suggest_negative_keywords(search_terms)` - 建议否定关键词
- `calculate_optimal_bid(keyword_data)` - 计算最优出价

**功能特点：**
- ✅ 完整的广告指标分析（CTR, CPC, ACoS, CVR, ROAS）
- ✅ 关键词自动分类（提高/降低/暂停）
- ✅ 智能预算分配算法
- ✅ 自动识别无效搜索词

---

### 5. 🔍 ranking.py - 排名分析模块

**类：** `RankingAnalyzer`

**主要方法：**
- `track_keyword_rankings(ranking_data)` - 追踪关键词排名
- `analyze_ranking_performance(ranking_df)` - 分析排名表现
- `identify_ranking_opportunities(ranking_df)` - 识别提升机会
- `compare_with_competitors(my_rankings, competitor_rankings)` - 竞品排名对比
- `calculate_visibility_score(ranking_data)` - 计算可见度分数

**功能特点：**
- ✅ 排名变化趋势追踪
- ✅ 7日移动平均
- ✅ 可见度加权计算
- ✅ 机会评分系统

---

### 6. 🎯 competitor.py - 竞品分析模块

**类：** `CompetitorAnalyzer`

**主要方法：**
- `analyze_competitor_pricing(pricing_data)` - 分析竞品定价
- `monitor_price_changes(price_history)` - 监控价格变化
- `analyze_competitor_reviews(reviews_data)` - 分析竞品评论
- `extract_review_insights(review_texts)` - 提取评论洞察
- `calculate_market_share(competitors)` - 计算市场份额
- `compare_products(my_product, competitors)` - 产品对比

**功能特点：**
- ✅ 定价策略分析（竞争性/高端/低价）
- ✅ 评论情感分析
- ✅ 市场机会识别
- ✅ 竞争力评分

---

### 7. ✍️ listing.py - Listing优化模块

**类：** `ListingOptimizer`

**主要方法：**
- `analyze_title(title)` - 分析产品标题
- `optimize_title(current_title, keywords, brand, features)` - 优化标题
- `analyze_bullet_points(bullet_points)` - 分析产品要点
- `analyze_description(description)` - 分析产品描述
- `calculate_keyword_density(text, keywords)` - 计算关键词密度
- `generate_seo_report(title, bullets, description, keywords)` - 生成SEO报告

**功能特点：**
- ✅ 标题质量评分（0-100）
- ✅ 要点完整性检查
- ✅ 关键词密度分析（1-3%最优）
- ✅ SEO综合评估

---

## 🌐 Web应用架构

### Flask后端 (app.py)

**路由结构：**

```
/ (首页)
├── /product-research (选品分析)
├── /operations (运营管理)
├── /inventory (库存管理)
├── /advertising (广告优化)
├── /ranking (排名分析)
├── /competitor (竞品分析)
└── /listing (Listing优化)

API端点:
├── /api/product-research/*
├── /api/operations/*
├── /api/inventory/*
├── /api/advertising/*
├── /api/ranking/*
├── /api/competitor/*
└── /api/listing/*
```

**技术栈：**
- **后端框架：** Flask 3.0
- **数据处理：** Pandas, NumPy
- **可视化：** Matplotlib, Seaborn
- **前端：** HTML5 + CSS3 + JavaScript (原生)

---

## ⚙️ 配置系统 (config.py)

### 环境变量

```python
# .env 文件
AMAZON_ACCESS_KEY=xxx          # 亚马逊API密钥（可选）
AMAZON_SECRET_KEY=xxx          # 亚马逊API密钥（可选）
OPENAI_API_KEY=xxx             # OpenAI密钥（可选）
SECRET_KEY=xxx                 # Flask密钥
```

### 默认配置

```python
PRODUCT_RESEARCH = {
    'min_profit_margin': 30,    # 最小利润率 30%
    'min_monthly_sales': 300,   # 最小月销量
    'max_competition_score': 70 # 最大竞争分数
}

INVENTORY = {
    'low_stock_days': 30,       # 库存预警 30天
    'reorder_point_factor': 1.5,# 补货点系数
    'safety_stock_days': 7      # 安全库存 7天
}

ADVERTISING = {
    'target_acos': 25,          # 目标ACoS 25%
    'max_cpc': 2.0,             # 最大CPC $2
    'min_impressions': 1000     # 最小展示量
}
```

---

## 🎨 前端设计

### 设计系统

**颜色方案：**
- 主色调：`#667eea` (紫蓝色)
- 次色调：`#764ba2` (紫色)
- 成功色：`#10b981` (绿色)
- 警告色：`#f59e0b` (橙色)
- 错误色：`#ef4444` (红色)

**布局系统：**
- 响应式网格布局
- 卡片式设计
- 移动端适配

**交互特性：**
- 表单验证
- 加载动画
- 结果动态展示
- 错误提示

---

## 📊 数据流程

### 典型工作流

```
1. 用户输入 → 2. 前端验证 → 3. API调用 → 4. 后端处理 → 5. 返回结果 → 6. 前端展示
```

### 数据格式

**输入格式：** JSON
```json
{
  "product_data": {...},
  "market_data": {...}
}
```

**输出格式：** JSON
```json
{
  "success": true,
  "data": {
    "score": 75,
    "grade": "A",
    "recommendations": [...]
  }
}
```

---

## 🔧 扩展指南

### 添加新模块

1. 在 `modules/` 下创建新的 `.py` 文件
2. 创建模块类
3. 在 `modules/__init__.py` 中导入
4. 在 `app.py` 中添加路由
5. 创建对应的HTML模板

### 添加新API

```python
@app.route('/api/your-module/your-function', methods=['POST'])
def your_function():
    try:
        data = request.json
        # 处理逻辑
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

### 自定义配置

编辑 `config.py`：

```python
class Config:
    # 添加您的配置
    YOUR_SETTING = 'value'
```

---

## 📈 性能优化建议

1. **数据缓存** - 使用Redis缓存频繁查询的数据
2. **异步处理** - 使用Celery处理耗时任务
3. **数据库优化** - 添加索引，优化查询
4. **CDN加速** - 静态资源使用CDN
5. **负载均衡** - 使用Nginx进行负载均衡

---

## 🔒 安全建议

1. **API密钥管理** - 使用环境变量，不要硬编码
2. **输入验证** - 严格验证用户输入
3. **SQL注入防护** - 使用参数化查询
4. **HTTPS** - 生产环境启用HTTPS
5. **访问控制** - 添加用户认证和权限管理

---

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 Python代码规范
- 函数和变量使用下划线命名
- 类使用驼峰命名
- 添加详细的文档字符串

### 注释规范

```python
def function_name(param1, param2):
    """
    函数简要说明
    
    参数：
    - param1: 参数1说明
    - param2: 参数2说明
    
    返回：
    返回值说明
    """
    pass
```

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 🧪 测试

### 运行示例

```bash
python examples.py
```

### 单元测试（待添加）

```bash
pytest tests/
```

---

## 📚 参考资源

- [Flask文档](https://flask.palletsprojects.com/)
- [Pandas文档](https://pandas.pydata.org/)
- [亚马逊SP-API](https://developer.amazonservices.com/)
- [EOQ模型](https://en.wikipedia.org/wiki/Economic_order_quantity)

---

## 📧 技术支持

如有问题，请：
1. 查看文档
2. 运行示例代码
3. 查看代码注释
4. 提交Issue

---

**最后更新：** 2024年1月  
**版本：** v1.0.0
