# Amazon 选品痛点洞察

每日采集用户差评与社区吐槽，自动提取痛点、扩展关键词、给出选品方向建议。

## 功能

- 每日自动采集（UTC 08:00，可配置）
- **Google 搜索联想 + Amazon 买家搜索词 → 自动更新风向**
- **按热度自动匹配竞品 ASIN，并分析每个 ASIN 的差评痛点**
- Amazon 差评监控（支持 Rainforest API）
- Reddit 社区文本采集
- 痛点主题提取（滑落、太软、洗澡难、拐杖双手占用等）
- 关键词扩展与选品方向推荐
- 手动粘贴差评即时分析
- 自定义监控 ASIN

## 快速启动

```bash
cd amazon-picker
chmod +x run.sh
./run.sh
```

浏览器打开：`http://localhost:8080`

## 配置真实 Amazon 差评

1. 复制 `backend/.env.example` 为 `backend/.env`
2. 填入 `RAINFOREST_API_KEY`（[Rainforest API](https://www.rainforestapi.com/)）
3. 重启服务

## API

| 接口 | 说明 |
|------|------|
| `GET /api/report/latest` | 最新日报 |
| `POST /api/collect/run` | 手动采集 |
| `POST /api/analyze/text` | 分析粘贴文本 |
| `POST /api/watch-asins` | 添加监控 ASIN |

## 说明

- Amazon 直连抓取在部分服务器会被拦截，此时会使用内置种子样本 + 你粘贴的差评。
- 配置 Rainforest API 后可获取真实 1-3 星差评，建议生产环境使用。
