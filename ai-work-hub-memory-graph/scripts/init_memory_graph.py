#!/usr/bin/env python3
"""Initialize a private AI Work Hub Memory Graph directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_graph_lib import DEFAULT_CONFIG, write_json_atomic
from object_templates import (PROJECT_TEMPLATE, PERSON_TEMPLATE, EVENT_TEMPLATE,
                              SECTOR_TEMPLATE, TECH_TEMPLATE, VALUATION_TEMPLATE, REVIEW_TEMPLATE)


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
- 项目卡片是持续判断的压缩投影；正式判断由项目文件维护。事件卡片只保留具有独立、持久价值的重大事件。
- 日报/周报全文继续保存在 `自动化归档/`，这里只按价值更新相关项目、赛道、技术、估值、人物或重大事件，不设机械数量上限。
- 本目录可能包含敏感投资判断，不应上传到 public GitHub。
- 项目目录是完整事实层，项目状态 JSON 是机器可读真相，项目卡片是压缩视图，JSONL 索引均为可重建缓存。
- 与项目直接相关的新闻进入项目卡片 `外部动态`，可以说明可能影响，但不得静默改写正式投资判断。
- 清晰的可复用变化直接更新对应文件；只有重要但没有安全归宿的信号才进入单一 `待复核.md`。
- 不单独维护观点账本；可复用观点进入最直接的赛道、技术、估值、项目或工作流规则。
- 同类对象使用 templates 中相同的结构，省略空段落；内容截至日期不等于排版或迁移日期。
- 跨对象使用普通 Markdown 链接说明联系；项目的当前价格建议只在项目内维护，其他对象链接过去。
- 共享写入使用 write_graph.py 检查读取时的哈希并加锁；同步字段成功不代表正文已更新，写后仍须回读。
- 使用 Obsidian 时打开整个工作区，以保留项目、知识来源、研究和图谱之间的相对链接。
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
        "赛道地图模板.md": SECTOR_TEMPLATE,
        "估值锚点模板.md": VALUATION_TEMPLATE,
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
