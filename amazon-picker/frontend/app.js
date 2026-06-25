/**
 * 前端交互逻辑：加载日报、触发采集、文本分析。
 */

const reportDate = document.getElementById("reportDate");
const summaryText = document.getElementById("summaryText");
const sourceStats = document.getElementById("sourceStats");
const painPointsEl = document.getElementById("painPoints");
const keywordsEl = document.getElementById("keywords");
const productsEl = document.getElementById("products");
const statusText = document.getElementById("statusText");
const asinList = document.getElementById("asinList");
const manualResult = document.getElementById("manualResult");
const trendKeywordsEl = document.getElementById("trendKeywords");
const trendProductsEl = document.getElementById("trendProducts");

document.getElementById("refreshBtn").addEventListener("click", runCollect);
document.getElementById("refreshTrendsBtn").addEventListener("click", refreshTrends);
document.getElementById("analyzeBtn").addEventListener("click", analyzeText);
document.getElementById("addAsinBtn").addEventListener("click", addAsin);

init();

/**
 * 初始化页面数据。
 */
async function init() {
  await Promise.all([loadReport(), loadAsins()]);
}

/**
 * 加载最新日报。
 */
async function loadReport() {
  setStatus("加载日报中...");
  try {
    const response = await fetch("/api/report/latest");
    if (!response.ok) {
      throw new Error("暂无日报");
    }
    const report = await response.json();
    renderReport(report);
    setStatus("日报已更新");
  } catch (error) {
    summaryText.textContent = "暂无日报，请点击「立即采集」。";
    setStatus(error.message);
  }
}

/**
 * 触发后端采集。
 */
async function runCollect() {
  setStatus("采集中，请稍候...");
  const response = await fetch("/api/collect/run", { method: "POST" });
  const payload = await response.json();
  renderReport(payload.report);
  setStatus("采集完成");
}

/**
 * 渲染日报内容。
 * @param {object} report 日报对象
 */
function renderReport(report) {
  reportDate.textContent = report.report_date;
  summaryText.textContent = report.summary || "暂无摘要";
  sourceStats.innerHTML = Object.entries(report.source_stats || {})
    .map(([name, stat]) => `<span class="chip">${name}: ${formatStat(stat)}</span>`)
    .join("");

  painPointsEl.innerHTML = (report.pain_points || [])
    .map(
      (item) => `
      <div class="list-item">
        <h3>${item.theme_zh}</h3>
        <div class="meta">
          <span class="tag ${severityClass(item.severity)}">${item.severity}频</span>
          <span class="tag">${item.category}</span>
          <span class="tag">提及 ${item.count} 次</span>
        </div>
        <div class="examples">${(item.examples || []).map((e) => `• ${escapeHtml(e)}`).join("<br/>")}</div>
      </div>`
    )
    .join("");

  keywordsEl.innerHTML = (report.keywords || [])
    .map(
      (item) => `
      <div class="list-item">
        <h3>${escapeHtml(item.keyword)}</h3>
        <div class="meta">
          <span class="tag">来源: ${item.source_theme}</span>
          <span class="tag">优先级: ${item.priority}</span>
        </div>
      </div>`
    )
    .join("");

  productsEl.innerHTML = (report.products || [])
    .map(
      (item) => `
      <div class="product-card">
        <div class="score">${item.blue_ocean_score}/10</div>
        <h3>${escapeHtml(item.direction)}</h3>
        <p>${escapeHtml(item.reason)}</p>
        <div class="meta">
          <span class="tag">${item.verdict}</span>
          <span class="tag">${item.price_band}</span>
        </div>
        <div class="examples">1688: ${(item.supply_keywords || []).join(" / ")}</div>
      </div>`
    )
    .join("");

  renderTrends(report);
}

/**
 * 渲染搜索风向与 ASIN 痛点。
 * @param {object} report 日报对象
 */
function renderTrends(report) {
  const keywords = report.trend_keywords || [];
  const products = report.trend_products || [];

  trendKeywordsEl.innerHTML = keywords.length
    ? keywords
        .map(
          (item) => `
      <div class="list-item">
        <h3>${escapeHtml(item.keyword)}</h3>
        <div class="meta">
          <span class="tag high">热度 ${item.score}</span>
          <span class="tag">Google ${item.google_score || 0}</span>
          <span class="tag">Amazon ${item.amazon_score || 0}</span>
          <span class="tag">${(item.sources || []).join(" + ")}</span>
        </div>
      </div>`
        )
        .join("")
    : "<p class='note'>暂无风向数据，点击「刷新风向」获取。</p>";

  trendProductsEl.innerHTML = products.length
    ? products
        .map((item) => {
          const pains = (item.pain_points || [])
            .map((p) => `<span class="chip">${escapeHtml(p.theme_zh)} (${p.count})</span>`)
            .join("");
          const complaints = (item.sample_complaints || [])
            .map((c) => `• ${escapeHtml(c)}`)
            .join("<br/>");
          return `
      <div class="product-card">
        <div class="trend-score">${item.trend_score}</div>
        <div class="asin-link">${item.asin}</div>
        <h3>${escapeHtml(item.title || item.keyword)}</h3>
        <p>来源词：${escapeHtml(item.keyword)}</p>
        <div class="meta">${pains || "<span class='tag'>暂无痛点样本</span>"}</div>
        <div class="examples">${complaints}</div>
      </div>`;
        })
        .join("")
    : "<p class='note'>暂未匹配到 ASIN，可在 backend/.env 配置 RAINFOREST_API_KEY 提升命中率。</p>";
}

/**
 * 单独刷新风向数据。
 */
async function refreshTrends() {
  setStatus("刷新风向中...");
  const response = await fetch("/api/trends/refresh", { method: "POST" });
  const payload = await response.json();
  renderTrends(payload);
  setStatus("风向已刷新");
}

/**
 * 分析用户粘贴文本。
 */
async function analyzeText() {
  const text = document.getElementById("analyzeInput").value.trim();
  if (text.length < 20) {
    manualResult.innerHTML = "<p class='note'>请至少输入 20 个字符。</p>";
    return;
  }
  setStatus("分析文本中...");
  const response = await fetch("/api/analyze/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const result = await response.json();
  manualResult.innerHTML = `
    <h3>识别痛点 ${result.pain_points.length} 个</h3>
    ${result.pain_points
      .map((p) => `<div class="chip">${p.theme_zh} (${p.count})</div>`)
      .join("")}
    <h3 style="margin-top:12px">建议关键词</h3>
    ${result.keywords
      .slice(0, 8)
      .map((k) => `<div class="chip">${escapeHtml(k.keyword)}</div>`)
      .join("")}
    <h3 style="margin-top:12px">选品方向</h3>
    ${result.products
      .slice(0, 3)
      .map((p) => `<div class="list-item"><strong>${escapeHtml(p.direction)}</strong><br/>${escapeHtml(p.verdict)}</div>`)
      .join("")}
  `;
  setStatus("文本分析完成");
}

/**
 * 加载监控 ASIN。
 */
async function loadAsins() {
  const response = await fetch("/api/watch-asins");
  const payload = await response.json();
  asinList.innerHTML = (payload.items || [])
    .map((item) => `<span class="chip">${item.asin}${item.label ? ` · ${escapeHtml(item.label)}` : ""}</span>`)
    .join("");
}

/**
 * 添加监控 ASIN。
 */
async function addAsin() {
  const asin = document.getElementById("asinInput").value.trim().toUpperCase();
  const label = document.getElementById("asinLabel").value.trim();
  if (asin.length !== 10) {
    setStatus("ASIN 需为 10 位");
    return;
  }
  await fetch("/api/watch-asins", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ asin, label }),
  });
  document.getElementById("asinInput").value = "";
  document.getElementById("asinLabel").value = "";
  await loadAsins();
  setStatus(`已添加 ASIN ${asin}`);
}

/**
 * 格式化采集统计。
 * @param {object|string|number} stat 统计对象
 * @return {string}
 */
function formatStat(stat) {
  if (typeof stat === "number") {
    return String(stat);
  }
  if (stat && typeof stat === "object") {
    if (stat.count !== undefined) {
      return String(stat.count);
    }
    if (Array.isArray(stat.asins)) {
      return `${stat.asins.length} ASIN`;
    }
    if (Array.isArray(stat.subreddits)) {
      return `${stat.subreddits.reduce((sum, s) => sum + (s.count || 0), 0)} 帖`;
    }
  }
  return "ok";
}

/**
 * 严重度样式。
 * @param {string} severity 严重度
 * @return {string}
 */
function severityClass(severity) {
  if (severity === "高") {
    return "high";
  }
  if (severity === "中") {
    return "mid";
  }
  return "";
}

/**
 * HTML 转义。
 * @param {string} value 原字符串
 * @return {string}
 */
function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

/**
 * 更新状态栏。
 * @param {string} text 状态文本
 */
function setStatus(text) {
  statusText.textContent = text;
}
