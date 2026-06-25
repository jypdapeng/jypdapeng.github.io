# Amazon 选品痛点洞察（仅真实数据）

所有数据均来自真实 API 或你手动粘贴的亚马逊差评，**不使用任何内置样本或假数据**。

## 无需 Rainforest API Key 也能用

| 功能 | 来源 | 是否需要 Key |
|------|------|-------------|
| 搜索热词 | Google 联想 + Amazon 补全 | 否 |
| Reddit 术后吐槽 | PullPush API | 否 |
| **Amazon 差评** | **页面手动粘贴导入** | **否** |
| 竞品 ASIN | 监控列表（你添加的 ASIN） | 否 |
| Amazon 自动采集 | Rainforest API（可选） | 是 |

### 推荐工作流（零成本）

1. 用「搜索风向」看 Google/Amazon 真实热词
2. 在亚马逊网页找到竞品，复制 1-3 星差评
3. 在网站「导入 Amazon 差评」粘贴，系统自动分析痛点
4. 添加监控 ASIN，下次采集自动汇总

### 可选：Rainforest 自动采集

若不想手动复制差评，可注册 https://www.rainforestapi.com/ 获取免费试用 Key（约 100 次请求），填入 `.env` 即可自动拉取差评和搜索 ASIN。

## 快速启动

```bash
cd amazon-picker/backend
cp .env.example .env
# Rainforest Key 可选，不填也能用手动导入 + Reddit + 风向

cd ..
chmod +x run.sh
./run.sh
```

浏览器访问：`http://localhost:8080`

## API

| 接口 | 说明 |
|------|------|
| `GET /api/data-sources/status` | 检查数据源状态 |
| `GET /api/report/latest` | 最新日报 |
| `POST /api/collect/run` | 手动全量采集 |
| `POST /api/reviews/import` | 导入手动复制的 Amazon 差评 |
| `POST /api/trends/refresh` | 刷新搜索风向 |
| `POST /api/analyze/text` | 即时分析粘贴文本（不保存） |

## 手动导入差评示例

```json
POST /api/reviews/import
{
  "asin": "B07Y3PZHD9",
  "text": "The pillow is too narrow and my leg keeps sliding off.\nNot firm enough, sinks after 10 minutes."
}
```
