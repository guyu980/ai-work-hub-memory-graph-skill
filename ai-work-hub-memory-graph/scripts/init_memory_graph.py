#!/usr/bin/env python3
"""Initialize a private AI Work Hub Memory Graph directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_graph_lib import DEFAULT_CONFIG, write_json_atomic


SECTORS = [
    "AI基础设施与开发者工具",
    "AI原生应用与工作流",
    "具身智能与机器人",
    "AI硬件与边缘智能",
    "半导体与硬件基础设施",
    "基础模型与前沿技术",
    "观察与非核心机会",
]

VALUATION_SECTORS = [
    sector for sector in SECTORS if sector != "观察与非核心机会"
]

DIRS = [
    "00_索引",
    "01_项目卡片",
    "02_赛道地图",
    "03_技术主题",
    "04_估值锚点",
    "05_事件卡片",
    "06_人物卡片",
    ".system",
    "config",
    "templates",
]

INDEX_FILES = [
    "项目索引.jsonl",
    "关系索引.jsonl",
    "赛道索引.jsonl",
    "技术主题索引.jsonl",
    "估值索引.jsonl",
    "事件索引.jsonl",
    "人物索引.jsonl",
]


README = """# AI Work Hub Memory Graph

本目录是本地私有的跨项目投资认知库，用于连接项目尽调、非项目知识来源、日报/周报、GitHub radar、技术主题和估值锚点。

原则：

- 这里保存的是可复用的投资认知，不替代 `项目/` 下的完整尽调材料。
- `知识来源/` 保存可复用的非项目访谈和主题材料；这里仅接收其重要认知增量，不复制原文。
- 项目卡片用于连续判断；事件卡片只保留具有独立、持久价值的重大事件。
- 日报/周报全文继续保存在 `自动化归档/`，这里只按价值更新相关项目、赛道、技术、估值、人物或重大事件，不设机械数量上限。
- 本目录可能包含敏感投资判断，不应上传到 public GitHub。
- 项目目录是完整事实层，项目状态 JSON 是机器可读真相，项目卡片是压缩视图，JSONL 索引均为可重建缓存。
- 与项目直接相关的新闻进入项目卡片 `外部动态`，可以说明可能影响，但不得静默改写正式投资判断。
- 清晰的可复用变化直接更新对应文件；只有重要但没有安全归宿的信号才进入单一 `待复核.md`。
- 不单独维护观点账本；可复用观点进入最直接的赛道、技术、估值、项目或工作流规则。
"""

PROJECT_TEMPLATE = """# 项目卡片｜项目名

- Schema Version: 2
- 项目 ID: project:项目名
- 创建日期:
- 最近更新:
- 最近同步:
- 主赛道:
- 标签:
- 别名: []
- 资料模式: live
- 历史结果: not_applicable
- 复盘状态: not_applicable
- 历史决策日期:
- 复盘基准日:
- 项目状态: active
- 流程阶段: screening
- 投资判断: observe
- 建议打法: tbd
- 仓位: tbd
- 价格判断: unknown
- 判断置信度: low
- 当前投资判断:
- 融资阶段:
- 估值摘要:
- 状态文件:
- 资料来源:
- 同步哈希:

## 一句话

## 公司与产品

## 技术路线

## 客户与商业化

## 团队技术背景

## 估值与融资

## 已验证事实

## 公司/来源自述

## 仍需确认

## 外部动态

## 相似项目

## 反例项目

## 相关赛道/技术主题

## 对投资判断的启发

## 下次触发更新的信号
"""

PERSON_TEMPLATE = """# 人物卡片｜姓名或待核验称呼

- 创建日期:
- 最近更新:
- 当前机构/角色:
- 相关项目:
- 相关赛道:
- 标签:
- 信息口径:
- 当前判断:

## 一句话

## 身份消歧

## 学术与技术背景

## 论文 / 专利 / GitHub / 开源

## 创业与产业履历

## 跨项目关系

## 对投资判断的启发

## 风险与待确认

## 来源
"""

EVENT_TEMPLATE = """# 事件卡片｜事件短名

- 日期:
- 来源:
- 主赛道:
- 标签:
- 事件类型:
- 影响等级:

## 事件

## 为什么重要

## 影响哪些项目/赛道

## 估值或技术含义

## 后续跟踪
"""

SECTOR_TEMPLATE = """# 赛道地图｜{sector}

## 当前判断

## 子方向

## 强信号

## 弱信号 / 伪命题

## 已看项目

## 代表性反例

## 估值锚点

## 最近改变判断的事件

## 下一步想找的机会
"""

TECH_TEMPLATE = """# 技术主题｜主题名

## 当前理解

## 技术路线与关键变量

## 商业化映射

## 可验证信号

## 常见风险

## 相关项目

## 相关事件

## 会改变判断的新信号
"""

VALUATION_TEMPLATE = """# 估值锚点｜{sector}

## 使用口径

## 上市公司可比

## 一级市场可比

### 公司 / 材料 / 公开口径

### 深度交易核验（仅在必要时）

## 商业模式分层

### SaaS / ARR

### API / usage-based

### 硬件收入

### 项目制 / SI-like

### 模型或技术授权

## 我们自己的价格纪律

## 最近更新
"""

REVIEW_TEMPLATE = """# 待复核

只记录重要但暂时没有安全归宿的信号。普通新闻直接进入相关项目卡片的
`外部动态`，清晰的跨项目认知直接更新对应赛道、技术、估值、人物或重大事件文件。

## 待处理
"""


def write_if_missing(path: Path, content: str) -> str:
    if path.exists():
        return "exists"
    path.write_text(content, encoding="utf-8")
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace-root",
        default=str(Path.home() / "Documents" / "AI Work Hub"),
        help="AI Work Hub workspace root. Default: ~/Documents/AI Work Hub",
    )
    parser.add_argument(
        "--memory-root",
        default=None,
        help="Override Memory Graph root. Default: <workspace-root>/Memory Graph",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else workspace_root / "Memory Graph"
    )
    memory_root.mkdir(parents=True, exist_ok=True)

    events: list[str] = []

    for directory in DIRS:
        path = memory_root / directory
        path.mkdir(parents=True, exist_ok=True)
        events.append(f"dir    {path}")

    events.append(f"{write_if_missing(memory_root / 'README.md', README):7} {memory_root / 'README.md'}")

    for name in INDEX_FILES:
        path = memory_root / "00_索引" / name
        events.append(f"{write_if_missing(path, ''):7} {path}")

    templates = {
        "项目卡片模板.md": PROJECT_TEMPLATE,
        "人物卡片模板.md": PERSON_TEMPLATE,
        "事件卡片模板.md": EVENT_TEMPLATE,
        "技术主题模板.md": TECH_TEMPLATE,
    }
    for filename, content in templates.items():
        path = memory_root / "templates" / filename
        events.append(f"{write_if_missing(path, content):7} {path}")

    for sector in SECTORS:
        path = memory_root / "02_赛道地图" / f"{sector}.md"
        events.append(f"{write_if_missing(path, SECTOR_TEMPLATE.format(sector=sector)):7} {path}")

    for sector in VALUATION_SECTORS:
        path = memory_root / "04_估值锚点" / f"{sector}.md"
        events.append(f"{write_if_missing(path, VALUATION_TEMPLATE.format(sector=sector)):7} {path}")

    review_path = memory_root / "待复核.md"
    events.append(f"{write_if_missing(review_path, REVIEW_TEMPLATE):7} {review_path}")

    config_path = memory_root / "config" / "schema-v2.json"
    if config_path.exists():
        events.append(f"exists  {config_path}")
    else:
        write_json_atomic(config_path, DEFAULT_CONFIG)
        events.append(f"created {config_path}")

    print(f"Memory Graph initialized at: {memory_root}")
    for event in events:
        print(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
