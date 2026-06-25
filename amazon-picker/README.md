# Amazon 选品痛点洞察（仅真实数据）

所有数据均来自真实 API，**不使用任何内置样本或假数据回退**。

## 真实数据来源

| 数据 | 来源 | 是否需要 Key |
|------|------|-------------|
| 搜索热词 | Google 搜索联想 API | 否 |
| 买家搜索词 | Amazon 自动补全 API | 否 |
| Google 热点 | Google Trends RSS | 否 |
| Reddit 吐槽 | PullPush API | 否 |
| **Amazon 差评** | **Rainforest API** | **是（必填）** |
| **ASIN 自动发现** | **Rainforest Search API** | **是（必填）** |

## 快速启动

### 1. 获取 Rainforest API Key

1. 打开 https://www.rainforestapi.com/
2. 注册账号并获取 API Key（有免费试用额度）

### 2. 配置环境变量

```bash
cd amazon-picker/backend
cp .env.example .env
# 编辑 .env，填入：
# RAINFOREST_API_KEY=你的真实密钥
```

### 3. 启动

```bash
cd amazon-picker
chmod +x run.sh
./run.sh
```

浏览器访问：`http://localhost:8080`

## API

| 接口 | 说明 |
|------|------|
| `GET /api/data-sources/status` | 检查真实数据源是否就绪 |
| `GET /api/report/latest` | 最新日报 |
| `POST /api/collect/run` | 手动全量采集 |
| `POST /api/trends/refresh` | 刷新搜索风向 + ASIN + 痛点 |
| `POST /api/analyze/text` | 分析你粘贴的真实差评 |

## 说明

- 未配置 `RAINFOREST_API_KEY` 时：Google/Amazon 风向和 Reddit 仍可用，但 **Amazon 差评和 ASIN 为空**。
- 配置 Key 后点击「立即采集」即可获取真实差评与竞品 ASIN。
