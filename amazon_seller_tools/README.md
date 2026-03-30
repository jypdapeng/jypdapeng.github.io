# 🛒 亚马逊卖家智能辅助系统

> 一站式解决选品、运营、库存、广告、排名、竞品、Listing优化的所有需求

## 📋 目录

- [系统简介](#系统简介)
- [功能模块](#功能模块)
- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [使用教程](#使用教程)
- [API文档](#api文档)
- [常见问题](#常见问题)

---

## 🎯 系统简介

**亚马逊卖家智能辅助系统**是一个专为亚马逊中国卖家设计的综合性运营工具，整合了7大核心功能模块，帮助卖家进行数据驱动的决策，提升运营效率和盈利能力。

### 核心优势

✅ **数据驱动** - 基于实际数据进行科学分析  
✅ **智能建议** - 自动生成优化建议和行动方案  
✅ **一体化解决方案** - 覆盖从选品到优化的全流程  
✅ **简单易用** - 友好的Web界面，无需编程知识  
✅ **开源免费** - 完全开源，可自由定制和扩展  

---

## 🔧 功能模块

### 1. 📊 选品分析

帮助您找到最有利可图的产品机会。

**主要功能：**
- **利润计算器** - 精确计算产品利润、利润率和ROI
- **市场机会分析** - 评估市场规模、竞争强度和进入难度
- **产品综合评分** - 整合多维度数据给出选品建议
- **批量产品对比** - 快速比较多个产品的潜力

**使用场景：**
- 新产品开发前的市场调研
- 评估现有产品的盈利能力
- 对比多个产品选择最佳机会

---

### 2. 📈 运营管理

全面掌控店铺运营状况。

**主要功能：**
- **销售数据分析** - 分析销售趋势、最佳/最差销售日
- **KPI计算** - 自动计算ACoS、转化率、ROI等关键指标
- **销售预测** - 基于历史数据预测未来销售
- **绩效报告** - 生成详细的运营报告

**使用场景：**
- 每日/每周/每月销售复盘
- 设定和追踪运营目标
- 向团队或投资人展示业绩

---

### 3. 📦 库存管理

避免断货和库存积压。

**主要功能：**
- **库存状态分析** - 实时评估库存健康度
- **补货量计算** - 使用EOQ模型计算最优补货量
- **周转率分析** - 评估库存周转效率
- **滞销库存识别** - 及时发现需要清仓的产品
- **补货计划生成** - 批量生成补货建议

**使用场景：**
- 制定补货计划
- 优化库存结构
- 降低库存成本

---

### 4. 💰 广告优化

提升广告投放效率和ROI。

**主要功能：**
- **广告活动分析** - 评估广告活动表现
- **关键词分析** - 找出高效和低效关键词
- **预算优化** - 智能分配广告预算
- **否定关键词建议** - 自动识别应该屏蔽的搜索词
- **最优出价计算** - 计算每个关键词的最佳出价

**使用场景：**
- 优化PPC广告投放
- 降低ACoS提高利润
- 扩大广告规模

---

### 5. 🔍 排名分析

追踪和提升关键词排名。

**主要功能：**
- **关键词排名追踪** - 监控关键词排名变化
- **排名趋势分析** - 识别上升和下降趋势
- **可见度评分** - 计算产品整体可见度
- **提升机会识别** - 找出最有潜力的优化机会
- **竞品排名对比** - 与竞品排名进行对比

**使用场景：**
- 监控SEO效果
- 优化产品排名策略
- 竞品排名分析

---

### 6. 🎯 竞品分析

了解竞争对手，制定竞争策略。

**主要功能：**
- **竞品定价分析** - 分析市场定价策略
- **评论分析** - 从竞品评论中提取洞察
- **市场份额计算** - 了解各竞品的市场占有率
- **产品对比** - 全方位对比您的产品和竞品
- **价格变化监控** - 追踪竞品价格变化

**使用场景：**
- 制定定价策略
- 发现产品改进方向
- 监控竞争态势

---

### 7. ✍️ Listing优化

提升产品页面的转化率。

**主要功能：**
- **标题分析** - 评估标题质量并提供优化建议
- **要点分析** - 评估5个Bullet Points的有效性
- **描述分析** - 分析产品描述的完整性
- **关键词密度** - 检查关键词使用情况
- **SEO综合报告** - 生成完整的SEO优化报告

**使用场景：**
- 新品上架前的Listing优化
- 提升现有产品的转化率
- A/B测试不同Listing版本

---

## 💻 安装指南

### 系统要求

- Python 3.8+
- 2GB+ RAM
- 100MB 磁盘空间

### 安装步骤

#### 1. 克隆或下载项目

```bash
cd /workspace/amazon_seller_tools
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量（可选）

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置您的API密钥（如果需要）：

```
# 亚马逊SP-API配置（可选）
AMAZON_ACCESS_KEY=your_access_key_here
AMAZON_SECRET_KEY=your_secret_key_here

# OpenAI API配置（用于智能Listing优化）
OPENAI_API_KEY=your_openai_api_key_here

# 应用密钥
SECRET_KEY=your_secret_key_here
```

#### 4. 运行应用

```bash
python app.py
```

#### 5. 访问系统

打开浏览器访问：`http://localhost:5000`

---

## 🚀 快速开始

### 示例1：计算产品利润

1. 访问 **选品分析** 页面
2. 在 **利润计算器** 中输入：
   - 售价：$29.99
   - 产品成本：$10.00
   - 亚马逊佣金：15%
   - FBA费用：$4.50
3. 点击 **计算利润**
4. 查看详细的利润分析结果

### 示例2：分析产品评分

1. 在 **选品分析** 页面向下滚动到 **产品综合评分**
2. 输入产品数据（售价、成本等）
3. 输入市场数据（月销量、评分、竞品数等）
4. 点击 **分析产品**
5. 获得0-100分的综合评分和详细建议

---

## 📖 使用教程

### 教程1：新品选品完整流程

**场景：** 您想在亚马逊上销售蓝牙耳机，需要评估这个产品的可行性。

#### 第一步：收集基础数据

从亚马逊、Jungle Scout、Helium 10等工具收集以下数据：

- 产品成本：$12
- 预计售价：$35
- FBA费用：$5
- 月销量（市场平均）：3000件
- 市场平均价格：$32
- 平均评分：4.2
- 平均评论数：500
- 主要竞品数量：15个

#### 第二步：计算利润

1. 访问 **选品分析** 页面
2. 使用利润计算器：
   - 售价：$35
   - 成本：$12
   - 佣金：15%
   - FBA：$5
3. 结果显示：
   - 净利润：$12.75
   - 利润率：36.4%
   - ROI：106%
   - ✅ 有利可图

#### 第三步：综合评分

使用产品综合评分功能，输入所有数据，获得：

- 综合得分：**72分**
- 评级：**A (良好)**
- 市场吸引力：68分
- 竞争强度：55分
- 建议：**推荐 - 市场机会良好**

#### 第四步：决策

根据分析结果：
- ✅ 利润率>30%，符合目标
- ✅ 市场规模足够大
- ⚠️ 竞争中等，需要差异化
- **决定：** 进入市场，重点做产品差异化

---

### 教程2：优化现有产品的Listing

**场景：** 您的产品转化率偏低，想优化Listing提升转化。

#### 第一步：分析当前Listing

访问 **Listing优化** 页面（功能开发中，可通过API使用）：

```python
from modules.listing import ListingOptimizer
from config import Config

optimizer = ListingOptimizer(Config)

# 分析标题
title = "Bluetooth Headphones Wireless Earbuds"
title_analysis = optimizer.analyze_title(title)
print(f"标题得分: {title_analysis['score']}")
print(f"建议: {title_analysis['suggestions']}")
```

#### 第二步：优化标题

根据建议优化标题：

**原标题：**
```
Bluetooth Headphones Wireless Earbuds
```

**优化后：**
```
Premium Bluetooth 5.0 Wireless Earbuds - Noise Cancelling Headphones with Charging Case, IPX7 Waterproof Sports Earphones for Running Gym Workout
```

改进点：
- ✅ 添加了品牌定位（Premium）
- ✅ 包含技术规格（Bluetooth 5.0）
- ✅ 突出关键特性（Noise Cancelling, IPX7）
- ✅ 说明使用场景（Sports, Running, Gym）
- ✅ 长度达到150+字符

#### 第三步：优化Bullet Points

使用分析功能检查每个要点：

```python
bullets = [
    "Advanced Bluetooth 5.0 technology for stable connection",
    "Premium sound quality with deep bass",
    "IPX7 waterproof rating, perfect for sports",
    "30-hour battery life with charging case",
    "One-touch control and voice assistant support"
]

bullet_analysis = optimizer.analyze_bullet_points(bullets)
```

#### 第四步：跟踪改进效果

优化后监控关键指标：
- 转化率变化
- 关键词排名变化
- 单位会话量

---

### 教程3：优化广告活动

**场景：** 您的广告ACoS过高（40%），需要优化。

#### 第一步：分析广告活动

使用 **广告优化** 模块：

```python
from modules.advertising import AdvertisingOptimizer
from config import Config

ad_optimizer = AdvertisingOptimizer(Config)

campaign_data = {
    'impressions': 50000,
    'clicks': 500,
    'spend': 250,
    'sales': 625,
    'orders': 25
}

analysis = ad_optimizer.analyze_campaign_performance(campaign_data)
```

结果显示：
- ACoS: 40% ⚠️ 过高
- CTR: 1.0% ✅ 良好
- CVR: 5% ⚠️ 偏低
- 建议：暂停低效关键词，优化产品页面

#### 第二步：分析关键词

导出广告报告，分析每个关键词：

```python
keywords_data = [
    {'keyword': 'bluetooth headphones', 'impressions': 20000, 'clicks': 200, 
     'spend': 100, 'sales': 400, 'orders': 16},
    {'keyword': 'wireless earbuds', 'impressions': 15000, 'clicks': 150,
     'spend': 75, 'sales': 225, 'orders': 9},
    # ... 更多关键词
]

keyword_analysis = ad_optimizer.analyze_keywords(keywords_data)
```

发现：
- ✅ "bluetooth headphones" - ACoS 25%，表现优秀，提高出价
- ⚠️ "wireless earbuds" - ACoS 33%，中等，保持
- ❌ "cheap earbuds" - ACoS 60%，暂停

#### 第三步：优化预算分配

重新分配预算：

```python
campaigns = [
    {'campaign_name': 'Auto Campaign', 'current_budget': 50, 'sales': 200, 'acos': 35, 'roas': 2.86},
    {'campaign_name': 'Manual Exact', 'current_budget': 100, 'sales': 400, 'acos': 25, 'roas': 4.0},
    # ...
]

budget_optimization = ad_optimizer.optimize_budget_allocation(campaigns)
```

建议：
- Manual Exact: $100 → $130 (+30%) ✅ 高效活动
- Auto Campaign: $50 → $35 (-30%) ⚠️ 效率偏低

#### 第四步：执行和监控

1. 暂停低效关键词
2. 提高高效关键词出价
3. 调整预算分配
4. 7天后复盘效果

预期结果：
- ACoS从40%降至28%
- 总销售额保持或增长
- ROAS从2.5提升至3.5

---

## 📡 API文档

### 选品分析API

#### 计算利润

```http
POST /api/product-research/calculate-profit
Content-Type: application/json

{
  "selling_price": 29.99,
  "cost": 10.0,
  "amazon_fee_percentage": 15,
  "fba_fee": 4.5,
  "shipping_cost": 0,
  "other_costs": 0
}
```

响应：

```json
{
  "success": true,
  "data": {
    "selling_price": 29.99,
    "total_costs": 17.24,
    "profit": 12.75,
    "profit_margin": 42.51,
    "roi": 127.5,
    "is_profitable": true
  }
}
```

#### 产品综合评分

```http
POST /api/product-research/score-product
Content-Type: application/json

{
  "product_data": {
    "selling_price": 29.99,
    "cost": 10.0,
    "amazon_fee_percentage": 15,
    "fba_fee": 4.5
  },
  "market_data": {
    "monthly_sales": 5000,
    "avg_price": 28.0,
    "avg_rating": 4.2,
    "review_count": 500,
    "top_sellers_count": 10,
    "search_volume": 50000
  }
}
```

### 更多API端点

详细的API文档请参考：
- `/api/operations/*` - 运营管理
- `/api/inventory/*` - 库存管理
- `/api/advertising/*` - 广告优化
- `/api/ranking/*` - 排名分析
- `/api/competitor/*` - 竞品分析
- `/api/listing/*` - Listing优化

---

## ❓ 常见问题

### Q1: 系统是否需要连接亚马逊API？

**A:** 不需要。系统可以手动输入数据使用。如果您想自动获取数据，可以配置亚马逊SP-API（可选）。

### Q2: 数据从哪里获取？

**A:** 您可以从以下来源获取数据：
- 亚马逊卖家中心
- 第三方工具（Jungle Scout、Helium 10等）
- 手动市场调研
- 历史销售数据导出

### Q3: 系统支持哪些亚马逊站点？

**A:** 系统的分析逻辑适用于所有亚马逊站点，但您需要根据不同站点调整：
- 货币单位
- FBA费用标准
- 佣金比例

### Q4: 如何导出分析结果？

**A:** 目前支持：
- 截图保存结果
- 通过API获取JSON数据
- 使用Excel导出功能（部分模块）

### Q5: 系统是否收费？

**A:** 完全免费开源！您可以自由使用、修改和分发。

### Q6: 如何获取技术支持？

**A:** 您可以：
- 查看本文档
- 查看代码注释
- 在GitHub提Issue
- 参与社区讨论

### Q7: 可以定制开发吗？

**A:** 当然可以！系统采用模块化设计，易于扩展。您可以：
- 添加新的分析模块
- 集成其他API
- 定制UI界面
- 添加自动化功能

---

## 🔒 数据安全

- ✅ 所有数据存储在本地
- ✅ 不向第三方发送您的业务数据
- ✅ 支持自托管部署
- ✅ 开源代码，透明可审计

---

## 🛠️ 技术栈

- **后端:** Flask (Python)
- **数据分析:** Pandas, NumPy
- **可视化:** Matplotlib, Seaborn
- **前端:** HTML5, CSS3, JavaScript
- **数据库:** SQLite (可选)

---

## 📈 未来计划

- [ ] 完善所有模块的Web界面
- [ ] 添加数据可视化图表
- [ ] 集成亚马逊SP-API自动获取数据
- [ ] 添加AI智能建议（基于GPT）
- [ ] 支持多用户和团队协作
- [ ] 移动端适配
- [ ] 数据导出Excel/PDF

---

## 🤝 贡献

欢迎贡献代码、提出建议或报告问题！

---

## 📄 许可证

MIT License - 可自由使用、修改和分发

---

## 📞 联系方式

- 项目地址: `/workspace/amazon_seller_tools`
- 文档: `README.md`

---

**祝您在亚马逊业务中取得成功！** 🎉
