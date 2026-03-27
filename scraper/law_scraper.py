#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载法律法规网页（HTML），用 BeautifulSoup 提取正文并保存为以标题命名的 .txt。

两种用法：
1) 站内搜索模式：根据 search_url_template 抓取结果页并解析链接
2) URL 列表模式：直接读取 url_file 中的链接并下载
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup


UA_POOL = [
    # 保持温和即可；如目标站点有限制，可自行替换
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


BAD_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "canvas",
    "form",
    "button",
    "input",
    "select",
    "option",
    "textarea",
    "nav",
    "footer",
    "header",
    "aside",
}

# 通过 class/id 粗略剔除导航、广告、侧栏、分享、评论等
BAD_ATTR_RE = re.compile(
    r"(?:^|[-_ ])("
    r"nav|menu|breadcrumb|crumb|header|footer|sidebar|aside|"
    r"ad|ads|advert|advertise|banner|popup|modal|"
    r"share|social|comment|comments|"
    r"related|recommend|tool|toolbar"
    r")(?:$|[-_ ])",
    re.IGNORECASE,
)

WS_RE = re.compile(r"[ \t\r\f\v]+")
MANY_BLANK_LINES_RE = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class ScrapeConfig:
    base_url: str
    keywords: list[str]
    output_dir: str
    output_format: str = "txt"  # txt | md（适配 Dify 知识库导入）

    # 搜索模式
    search_url_template: Optional[str] = None  # 需包含 {kw}，可选 {page}
    max_pages: int = 20
    result_link_selector: str = "a"

    # 解析模式
    content_selector: Optional[str] = None
    title_selector: Optional[str] = None

    # 下载行为
    concurrency: int = 6
    delay_min: float = 0.2
    delay_max: float = 0.8
    timeout: float = 20.0
    same_domain_only: bool = True
    respect_robots: bool = False

    # 输入：URL 文件（优先于搜索模式）
    url_file: Optional[str] = None


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = WS_RE.sub(" ", text)
    # 保留换行，压缩多余空行
    text = "\n".join(line.strip() for line in text.splitlines())
    text = MANY_BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def _sanitize_filename(name: str, max_len: int = 120) -> str:
    name = _normalize_text(name)
    name = name.replace("/", " ").replace("\\", " ")
    name = re.sub(r'[:*?"<>|]', " ", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if not name:
        name = "untitled"
    if len(name) > max_len:
        name = name[:max_len].rstrip(" .")
    return name


def _unique_path(dir_path: str, base_name: str, ext: str = ".txt") -> str:
    base_name = _sanitize_filename(base_name)
    candidate = os.path.join(dir_path, f"{base_name}{ext}")
    if not os.path.exists(candidate):
        return candidate
    for i in range(2, 10_000):
        candidate = os.path.join(dir_path, f"{base_name}-{i}{ext}")
        if not os.path.exists(candidate):
            return candidate
    # 极端情况：用哈希兜底
    h = hashlib.sha1(base_name.encode("utf-8")).hexdigest()[:10]
    return os.path.join(dir_path, f"{base_name}-{h}{ext}")


def _pick_user_agent() -> str:
    return random.choice(UA_POOL)


def _build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": _pick_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
            "Connection": "keep-alive",
        }
    )
    return s


def _sleep_polite(cfg: ScrapeConfig) -> None:
    if cfg.delay_max <= 0:
        return
    time.sleep(random.uniform(max(0.0, cfg.delay_min), max(cfg.delay_min, cfg.delay_max)))


def _is_same_domain(base_url: str, url: str) -> bool:
    try:
        return urllib.parse.urlparse(base_url).netloc == urllib.parse.urlparse(url).netloc
    except Exception:
        return False


def _read_urls_from_file(path: str) -> list[str]:
    urls: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def _robots_allowed(rp: urllib.robotparser.RobotFileParser, url: str, ua: str) -> bool:
    try:
        return rp.can_fetch(ua, url)
    except Exception:
        return True


def _init_robot_parser(cfg: ScrapeConfig) -> Optional[urllib.robotparser.RobotFileParser]:
    if not cfg.respect_robots:
        return None
    base = urllib.parse.urlparse(cfg.base_url)
    robots_url = f"{base.scheme}://{base.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # 读不到就不阻断（但仍建议遵守站点规则）
        return None
    return rp


def _fetch_html(session: requests.Session, url: str, cfg: ScrapeConfig) -> str:
    resp = session.get(url, timeout=cfg.timeout)
    resp.raise_for_status()
    # requests 会基于 headers/内容猜测编码
    resp.encoding = resp.encoding or resp.apparent_encoding or "utf-8"
    return resp.text


def _strip_noise(soup: BeautifulSoup) -> None:
    # 删除明显的噪音标签
    for t in list(soup.find_all(BAD_TAGS)):
        t.decompose()

    # 删除疑似导航/广告等
    for tag in list(soup.find_all(True)):
        cid = " ".join(tag.get("class", [])) if tag.has_attr("class") else ""
        tid = tag.get("id", "") if tag.has_attr("id") else ""
        attr_blob = f"{cid} {tid}".strip()
        if attr_blob and BAD_ATTR_RE.search(attr_blob):
            tag.decompose()


def _select_title(soup: BeautifulSoup, title_selector: Optional[str]) -> str:
    if title_selector:
        node = soup.select_one(title_selector)
        if node and node.get_text(strip=True):
            return node.get_text(strip=True)
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)
    return "untitled"


def _candidate_content_nodes(soup: BeautifulSoup) -> list:
    # 常见正文容器优先
    selectors = [
        "article",
        "main",
        "#content",
        "#article",
        "#artical",  # 少量站点拼写
        ".content",
        ".article",
        ".article-content",
        ".post",
        ".post-content",
        ".entry-content",
        ".law-content",
        ".txt",
    ]
    nodes = []
    for sel in selectors:
        nodes.extend(soup.select(sel))
    if nodes:
        return nodes
    # 兜底：所有 div/section/article
    return list(soup.find_all(["article", "section", "div"]))


def _node_text_len(node) -> int:
    text = node.get_text("\n", strip=True)
    # 轻微抑制重复导航类文本（通常很短）
    return len(text)


def _select_content_node(soup: BeautifulSoup, content_selector: Optional[str]):
    if content_selector:
        node = soup.select_one(content_selector)
        if node:
            return node
    candidates = _candidate_content_nodes(soup)
    if not candidates:
        return soup.body or soup
    # 选取文本最长的节点作为正文
    return max(candidates, key=_node_text_len)


def extract_article_text(html: str, cfg: ScrapeConfig) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml") if _has_lxml() else BeautifulSoup(html, "html.parser")
    _strip_noise(soup)

    title = _select_title(soup, cfg.title_selector)
    content_node = _select_content_node(soup, cfg.content_selector)

    # 进一步剔除内容区域内的噪音
    for t in list(content_node.find_all(BAD_TAGS)):
        t.decompose()
    for tag in list(content_node.find_all(True)):
        cid = " ".join(tag.get("class", [])) if tag.has_attr("class") else ""
        tid = tag.get("id", "") if tag.has_attr("id") else ""
        attr_blob = f"{cid} {tid}".strip()
        if attr_blob and BAD_ATTR_RE.search(attr_blob):
            tag.decompose()

    text = content_node.get_text("\n", strip=False)
    text = _normalize_text(text)
    return title, text


def _has_lxml() -> bool:
    try:
        import lxml  # noqa: F401

        return True
    except Exception:
        return False


def _extract_links_from_search_page(
    html: str, search_page_url: str, cfg: ScrapeConfig
) -> list[str]:
    soup = BeautifulSoup(html, "lxml") if _has_lxml() else BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select(cfg.result_link_selector):
        if a.name != "a":
            continue
        href = a.get("href")
        if not href:
            continue
        abs_url = urllib.parse.urljoin(search_page_url, href)
        if cfg.same_domain_only and not _is_same_domain(cfg.base_url, abs_url):
            continue
        # 排除明显的非内容链接
        if abs_url.lower().startswith(("javascript:", "mailto:")):
            continue
        links.append(abs_url)
    # 去重保持顺序
    seen = set()
    out = []
    for u in links:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def collect_target_urls(session: requests.Session, cfg: ScrapeConfig) -> list[str]:
    if cfg.url_file:
        urls = _read_urls_from_file(cfg.url_file)
        if cfg.same_domain_only:
            urls = [u for u in urls if _is_same_domain(cfg.base_url, u)]
        # 去重
        seen = set()
        out = []
        for u in urls:
            if u in seen:
                continue
            seen.add(u)
            out.append(u)
        return out

    if not cfg.search_url_template or "{kw}" not in cfg.search_url_template:
        raise SystemExit(
            "未提供可用的 search_url_template（需包含 {kw}），或未提供 url_file。"
        )

    all_urls: list[str] = []
    seen: set[str] = set()

    for kw in cfg.keywords:
        empty_pages = 0
        for page in range(1, cfg.max_pages + 1):
            encoded_kw = urllib.parse.quote(kw)
            url = cfg.search_url_template.format(kw=encoded_kw, page=page)
            _sleep_polite(cfg)
            html = _fetch_html(session, url, cfg)
            links = _extract_links_from_search_page(html, url, cfg)
            new_links = [u for u in links if u not in seen]
            for u in new_links:
                seen.add(u)
                all_urls.append(u)
            if not new_links:
                empty_pages += 1
            else:
                empty_pages = 0
            # 连续几页没有新链接就提前停止（避免无穷翻页）
            if empty_pages >= 3:
                break

    return all_urls


def _save_txt(output_dir: str, title: str, url: str, text: str) -> str:
    _ensure_dir(output_dir)
    path = _unique_path(output_dir, title, ".txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(title.strip() + "\n")
        f.write(url.strip() + "\n\n")
        f.write(text.strip() + "\n")
    return path


def _escape_frontmatter_value(v: str) -> str:
    v = v.replace("\n", " ").strip()
    # YAML 简单安全转义：双引号包裹并转义双引号与反斜杠
    v = v.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{v}"'


def _text_to_markdown_paragraphs(text: str) -> str:
    """
    将抽取的纯文本适配为 Markdown 段落：
    - 保留已有的空行作为分段
    - 避免行内多余空白
    """
    text = _normalize_text(text)
    if not text:
        return ""
    # 已经压缩过多余空行，这里只保证段落之间一个空行
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n\n".join(parts)


def _save_md(output_dir: str, title: str, url: str, text: str) -> str:
    _ensure_dir(output_dir)
    path = _unique_path(output_dir, title, ".md")
    now = datetime.now(timezone.utc).isoformat()
    body = _text_to_markdown_paragraphs(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: {_escape_frontmatter_value(title)}\n")
        f.write(f"source_url: {_escape_frontmatter_value(url)}\n")
        f.write(f"crawled_at_utc: {_escape_frontmatter_value(now)}\n")
        f.write("---\n\n")
        f.write(f"# {title.strip()}\n\n")
        f.write(f"来源：{url.strip()}\n\n")
        f.write(body.strip() + "\n")
    return path


def _hash_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def download_one(session: requests.Session, url: str, cfg: ScrapeConfig, rp) -> tuple[str, str]:
    ua = session.headers.get("User-Agent", UA_POOL[0])
    if rp and not _robots_allowed(rp, url, ua):
        return "SKIP_ROBOTS", url

    _sleep_polite(cfg)
    html = _fetch_html(session, url, cfg)
    title, text = extract_article_text(html, cfg)

    # 如果正文过短，避免只保存到“导航残留”
    if len(text) < 80:
        # 仍保存，但给标题加后缀方便排查
        title = f"{title} (可能未命中正文容器)"

    if cfg.output_format.lower() == "md":
        saved_path = _save_md(cfg.output_dir, title, url, text)
    else:
        saved_path = _save_txt(cfg.output_dir, title, url, text)
    return saved_path, url


def _load_config_from_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _merge_cli_overrides(base: dict, overrides: dict) -> dict:
    out = dict(base)
    for k, v in overrides.items():
        if v is None:
            continue
        out[k] = v
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="批量下载法律法规 HTML，BeautifulSoup 提取正文并保存为 txt/md（md 适配 Dify 知识库导入）。"
    )
    p.add_argument("--config", help="JSON 配置文件路径（可选）")

    p.add_argument("--base-url", help="站点基准 URL（用于同域过滤/robots）")
    p.add_argument(
        "--keywords",
        nargs="*",
        default=None,
        help="关键词列表（默认：劳动法 民法典）",
    )
    p.add_argument("--output-dir", default=None, help="输出目录（默认：./out）")
    p.add_argument(
        "--output-format",
        default=None,
        choices=["txt", "md"],
        help="输出格式：txt 或 md（默认：txt；推荐 md 用于 Dify）",
    )

    p.add_argument(
        "--search-url-template",
        default=None,
        help="搜索结果页 URL 模板，需包含 {kw}，可包含 {page}",
    )
    p.add_argument("--max-pages", type=int, default=None, help="每个关键词最大翻页数")
    p.add_argument(
        "--result-link-selector",
        default=None,
        help="搜索结果页中，结果链接的 CSS selector（默认：a）",
    )

    p.add_argument(
        "--content-selector",
        default=None,
        help="正文容器 CSS selector（可选，强烈建议按目标站点配置）",
    )
    p.add_argument("--title-selector", default=None, help="标题 CSS selector（可选）")

    p.add_argument("--url-file", default=None, help="包含目标页面 URL 的文本文件（优先）")

    p.add_argument("--concurrency", type=int, default=None, help="并发下载线程数")
    p.add_argument("--delay-min", type=float, default=None, help="请求间隔最小秒数")
    p.add_argument("--delay-max", type=float, default=None, help="请求间隔最大秒数")
    p.add_argument("--timeout", type=float, default=None, help="请求超时秒数")
    p.add_argument(
        "--same-domain-only",
        action="store_true",
        help="只抓取同域链接（默认开启；若要关闭用 --no-same-domain-only）",
    )
    p.add_argument(
        "--no-same-domain-only",
        dest="same_domain_only",
        action="store_false",
        help="允许跨域链接",
    )
    p.set_defaults(same_domain_only=True)

    p.add_argument(
        "--respect-robots",
        action="store_true",
        help="启用 robots.txt 校验（默认关闭）",
    )
    return p.parse_args(argv)


def build_config(ns: argparse.Namespace) -> ScrapeConfig:
    base: dict = {}
    if ns.config:
        base = _load_config_from_json(ns.config)

    overrides = {
        "base_url": ns.base_url,
        "keywords": ns.keywords,
        "output_dir": ns.output_dir,
        "output_format": ns.output_format,
        "search_url_template": ns.search_url_template,
        "max_pages": ns.max_pages,
        "result_link_selector": ns.result_link_selector,
        "content_selector": ns.content_selector,
        "title_selector": ns.title_selector,
        "url_file": ns.url_file,
        "concurrency": ns.concurrency,
        "delay_min": ns.delay_min,
        "delay_max": ns.delay_max,
        "timeout": ns.timeout,
        "same_domain_only": ns.same_domain_only,
        "respect_robots": ns.respect_robots,
    }
    merged = _merge_cli_overrides(base, overrides)

    # 默认值
    if not merged.get("keywords"):
        merged["keywords"] = ["劳动法", "民法典"]
    if not merged.get("output_dir"):
        merged["output_dir"] = os.path.abspath("out")

    if not merged.get("base_url"):
        # 尽量从 search_url_template 推导
        tmpl = merged.get("search_url_template") or ""
        if tmpl:
            p = urllib.parse.urlparse(tmpl)
            if p.scheme and p.netloc:
                merged["base_url"] = f"{p.scheme}://{p.netloc}/"
    if not merged.get("base_url"):
        raise SystemExit("必须提供 --base-url 或在 config 中提供 base_url。")

    return ScrapeConfig(**merged)


def main(argv: list[str]) -> int:
    ns = parse_args(argv)
    cfg = build_config(ns)
    _ensure_dir(cfg.output_dir)

    session = _build_session()
    rp = _init_robot_parser(cfg)

    print(f"[INFO] base_url = {cfg.base_url}")
    print(f"[INFO] output_dir = {cfg.output_dir}")
    print(f"[INFO] keywords = {cfg.keywords}")

    # 1) 收集目标 URL
    try:
        urls = collect_target_urls(session, cfg)
    except Exception as e:
        print(f"[ERROR] 收集 URL 失败：{e}", file=sys.stderr)
        return 2

    if not urls:
        print("[WARN] 未收集到任何目标 URL。请检查 search_url_template / result_link_selector，或改用 --url-file。")
        return 0

    print(f"[INFO] 收集到 {len(urls)} 个候选 URL，开始下载/解析…")

    # 2) 并发下载
    ok = 0
    skipped = 0
    failed = 0
    seen_saved: set[str] = set()

    def _worker(u: str):
        # 每个 worker 使用独立 session，避免线程安全问题
        s = _build_session()
        return download_one(s, u, cfg, rp)

    with ThreadPoolExecutor(max_workers=max(1, cfg.concurrency)) as ex:
        futures = {ex.submit(_worker, u): u for u in urls}
        for fut in as_completed(futures):
            u = futures[fut]
            try:
                saved_path, src_url = fut.result()
                if saved_path == "SKIP_ROBOTS":
                    skipped += 1
                    print(f"[SKIP] robots 禁止：{src_url}")
                    continue
                # 防止重复保存（碰撞/重入）
                key = _hash_url(src_url)
                if key in seen_saved:
                    continue
                seen_saved.add(key)
                ok += 1
                print(f"[OK] {saved_path}")
            except Exception as e:
                failed += 1
                print(f"[FAIL] {u} -> {e}", file=sys.stderr)

    print(f"[DONE] 成功 {ok}，跳过 {skipped}，失败 {failed}。输出目录：{cfg.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
