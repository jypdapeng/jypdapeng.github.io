"""
分类爬取清单（入口目录）

说明：
- 很多权威站点没有公开 API，或对自动化访问有严格限制；请务必遵守 ToS/robots，优先使用开放数据/镜像/已授权接口。
- 这里提供的是“数据源目录与抓取入口”的工程骨架，便于在 Cursor 中继续实现每个 source 的采集器。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    category: str  # 1 法典/法律法规 2 司法解释/规范性文件 3 案例/裁判文书 4 地方法规 5 实务问答/手册 6 程序性知识
    name: str
    entry: str  # 入口（URL/说明字符串）。不要在代码里硬写账号/密钥
    notes: str = ""


SOURCES: list[Source] = [
    # 1) 法律渊源（母法/行政法规/规章等）
    Source(
        category="1-法典/法律法规",
        name="国家法律法规数据库（权威）",
        entry="https://flk.npc.gov.cn/",
        notes="全国人大法工委；优先用其公开检索入口/下载能力，注意访问频率与许可。",
    ),
    Source(
        category="1-法典/法律法规",
        name="国务院政策文件库（行政法规/规范性文件）",
        entry="http://www.gov.cn/zhengce/",
        notes="国务院网站政策栏目，适合补齐行政法规/国务院文件。",
    ),

    # 2) 司法解释 / 部门规章 / 规范性文件
    Source(
        category="2-司法解释/规范性文件",
        name="最高人民法院（司法解释/指导性文件）",
        entry="https://www.court.gov.cn/",
        notes="可按‘司法解释’栏目与检索抓取；建议做栏目级抓取 + 详情页抽取。",
    ),
    Source(
        category="2-司法解释/规范性文件",
        name="最高人民检察院（规范性文件/典型案例解读）",
        entry="https://www.spp.gov.cn/",
        notes="可补齐检察系统发布的指导性/典型案例与解读。",
    ),
    Source(
        category="2-司法解释/规范性文件",
        name="人社部（劳动领域部门规章/规章解释）",
        entry="https://www.mohrss.gov.cn/",
        notes="工伤、劳动合同、仲裁等部门规章/政策口径的重要来源。",
    ),

    # 3) 指导性案例与判例（核心）
    Source(
        category="3-案例/裁判文书",
        name="最高人民法院指导性案例（入口/汇编）",
        entry="https://www.court.gov.cn/fabu-gengduo-77.html",
        notes="建议以‘指导性案例/典型案例’发布页为入口，提取裁判要旨、裁判理由、要点。",
    ),
    Source(
        category="3-案例/裁判文书",
        name="人民法院案例库（如可访问）",
        entry="https://rmfyalk.court.gov.cn/",
        notes="若站点/接口受限，优先使用公开数据集或机构授权的接口。",
    ),
    Source(
        category="3-案例/裁判文书",
        name="中国裁判文书网（强限制，谨慎）",
        entry="https://wenshu.court.gov.cn/",
        notes="反爬严格且合规风险高；建议改用开源镜像/公开数据集/授权渠道。",
    ),

    # 4) 地方性法规（各地执行口径差异）
    Source(
        category="4-地方性法规",
        name="地方人大/政府法制办网站（按省市扩展）",
        entry="（示例）上海市人大/政府官网法规库",
        notes="建议先选 3-5 个重点地区（如沪/粤/京/浙）做样板，再扩展到全国。",
    ),

    # 5) 实务问答（Q&A）与手册（贴近人话）
    Source(
        category="5-实务问答/手册",
        name="法律援助中心/司法局 Q&A（按地区扩展）",
        entry="（示例）各地司法局网站的‘常见问题/办事指南/在线问答’",
        notes="这类内容在 Dify 知识库里可设置更高权重（或单独数据集）。",
    ),
    Source(
        category="5-实务问答/手册",
        name="法院/仲裁委 办事指南与文书模板",
        entry="（示例）劳动仲裁申请指南/证据清单/仲裁文书模板",
        notes="适合沉淀‘证据清单/时效/流程’等强可执行内容。",
    ),

    # 6) 程序性知识（如何操作）
    Source(
        category="6-程序性知识",
        name="诉讼服务/立案指南（法院/12368/诉服中心）",
        entry="https://www.court.gov.cn/fuwu/",
        notes="补齐‘去哪起诉/怎么立案/诉讼费/流程节点’等操作性知识。",
    ),
]


def grouped() -> dict[str, list[Source]]:
    out: dict[str, list[Source]] = {}
    for s in SOURCES:
        out.setdefault(s.category, []).append(s)
    return out

