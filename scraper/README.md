## 目标

批量下载法律相关页面（HTML），用 **BeautifulSoup** 提取正文（尽量忽略导航栏/广告/侧边栏），并自动保存为“以标题命名”的 `.txt` 或 `.md` 文件（**推荐 md 以便导入 Dify 知识库**）。

如果你要做“智能法律顾问”，仅抓《民法典》《劳动法》远远不够。建议按 4 个维度构建库：

- **法律渊源**：母法 + 司法解释 + 部门规章 + 地方条例
- **案例/裁判**：指导性案例/公报案例/典型案例/（合规渠道的）裁判文书数据
- **实务问答与手册**：Q&A、办案指南、证据清单（对“人话”命中率最高）
- **程序性知识**：怎么做（起诉/仲裁/材料/费用/时限）

仓库内提供了入口目录骨架：`scraper/sources_catalog.py` 与建议的 Markdown 规范：`scraper/normalize_to_dify_md.md`。

> 说明：不同站点的正文 DOM 结构差异很大。脚本提供 `content_selector`/`title_selector` 进行精准抽取；不配置时会用“最长文本容器”做兜底，但建议按目标站点配置。

## 安装

在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scraper/requirements.txt
```

## 用法一：URL 列表模式（最稳）

1) 把目标页面链接整理到一个文件（每行一个 URL）：

- 参考：`scraper/urls_example.txt`

2) 运行：

```bash
python scraper/law_scraper.py \
  --base-url "https://example.com/" \
  --url-file "scraper/urls_example.txt" \
  --output-format md \
  --output-dir "./out"
```

## 用法二：站内搜索模式（批量抓取“搜索结果页”里的链接）

你需要提供目标站点的“搜索结果页 URL 模板”，并告诉脚本如何在结果页里选取结果链接。

```bash
python scraper/law_scraper.py \
  --base-url "https://example.com/" \
  --search-url-template "https://example.com/search?q={kw}&page={page}" \
  --result-link-selector "a.search-result-title" \
  --max-pages 50 \
  --keywords 劳动法 民法典 \
  --content-selector "article" \
  --title-selector "h1" \
  --output-format md \
  --output-dir "./out"
```

### 关键词

默认关键词就是：

- 劳动法
- 民法典

你也可以通过 `--keywords` 覆盖。

## 输出格式

每个页面生成一个 `.txt` 或 `.md`，文件名来源于标题（自动清理非法字符并避免重名）。

### txt

`.txt` 文件内容：

1) 第一行：标题
2) 第二行：原始 URL
3) 空一行后：正文文本

### md（推荐给 Dify）

`.md` 文件包含：

- YAML front-matter：`title/source_url/crawled_at_utc`
- `# 标题`
- `来源：URL`
- 正文段落

## 抽取正文的关键参数（强烈建议配置）

- `--title-selector`
  - 示例：`h1` / `.article-title` / `#title`
- `--content-selector`
  - 示例：`article` / `#content` / `.article-content`

不配置时脚本会自动：

- 删除 `nav/header/footer/aside/script/style/iframe` 等噪音标签
- 删除 `class/id` 疑似包含 `nav/menu/breadcrumb/ad/banner/sidebar/share/comment...` 的节点
- 在常见容器（`article/main/#content/.content/...`）中选择“文本最长”的节点作为正文

## 合规与礼貌抓取

- 默认会加入随机 UA 且在请求间加入短暂停顿（`delay_min/delay_max`）
- 如需遵守 `robots.txt`，加上：

```bash
python scraper/law_scraper.py ... --respect-robots
```

## 使用 JSON 配置文件（可选）

参考 `scraper/config_example.json`：

```bash
python scraper/law_scraper.py --config scraper/config_example.json
```

