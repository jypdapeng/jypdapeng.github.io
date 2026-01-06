## Dify 知识库的 Markdown 规范（建议）

目标：让“法条 + 解释 + 适用（案例/问答/手册/流程）”在检索与引用时**更稳定**。

### 统一文档结构

每个源文档建议输出为单独 `.md` 文件，结构如下：

1) YAML front-matter（元数据）
2) `# 标题`
3) `来源：URL`
4) 正文（按段落/小标题组织）

### 建议的元数据字段（front-matter）

- `title`: 标题
- `doc_type`: `law|judicial_interpretation|department_rule|local_regulation|case|qa|manual|procedure`
- `jurisdiction`: `national|beijing|shanghai|guangdong|...`
- `source_url`: 来源 URL
- `source_name`: 来源站点/出版物
- `issued_at`: 发布日期（如可解析）
- `effective_at`: 施行日期（如可解析）
- `updated_at`: 更新日期（如可解析）
- `crawled_at_utc`: 抓取时间
- `keywords`: 关键词数组（如 `["劳动法","工伤","解除劳动合同"]`）

### 分段建议（面向“可回答性”）

同一文档内，把信息切成可检索的块：

- 法条：按“章/节/条”拆分
- 司法解释：按“条款/要点/适用范围/例外”拆分
- 判决书/案例：**只保留高信号段落**（诉求、争点、法院认为、裁判结果）
- Q&A：严格保持问答对格式（`Q:` / `A:` 或二级标题）
- 办案手册/流程：用清单（证据、步骤、材料、时限、费用）

