#!/usr/bin/env python3
"""Initialize a non-project knowledge source in an AI Work Hub workspace."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re


KINDS = {
    "expert-interview": ("专家访谈", "expert_interview"),
    "thematic-material": ("主题资料", "thematic_material"),
}


LIBRARY_README = """# 知识来源

本目录保存不专属于单一项目、但未来仍可复用的专家访谈和主题材料。

## 边界

- 围绕单一公司的材料进入 `项目/<项目名>/`，不要在这里复制一份。
- 正式、系统性的主题研究进入 `行业研究/<主题>/`。
- 专家访谈、会议记录、课程、播客、机构材料等可复用来源进入本目录。
- 原始资料只保存一次；项目、行业研究和 Memory Graph 通过链接引用。
- 每个来源只维护一份 `核心整理.md`，不为每条观点新建事件卡片或证据卡片。

## 分析流程

1. Memory Graph Skill 判断材料归属并完成轻量分析。
2. 将原文或原文件放入 `原始资料/`，解析结果放入 `解析文本/`。
3. 在 `核心整理.md` 中区分事实、来源观点和待核实事项。
4. 只把可复用的认知增量写回既有项目、赛道、技术、估值或高信号人物对象。
5. 需要外部检索或系统验证时，调用 Deep Research Skill；涉及单一项目判断时，调用 Diligence Skill。

这里是私有工作区内容，不属于公开 Skill 仓库。
"""


CORE_TEMPLATE = """# 知识来源｜{name}｜{topic}

- 类型: {kind_key}
- 日期: {source_date}
- 来源主体: {name}
- 主题: {topic}
- 来源链接:
- 相关赛道:
- 相关技术主题:
- 相关项目:
- 原始资料: `原始资料/`
- 解析文本: `解析文本/`
- 最近更新: {source_date}

## 一句话

## 来源与背景

## 主要内容

<!-- 专家访谈按问题与回答整理；其他材料按原文结构整理。 -->

## 技术与商业机制

<!-- 解释观点为何成立、约束在哪里，不只摘录结论。 -->

## 核心 Takeaways

<!-- 保留 3-7 条真正影响后续判断的结论。 -->

## 事实、观点与待核实

### 已核验事实

### 来源观点

### 待核实

## 转写风险与口径校正

## 与既有 Memory 的连接

<!-- 列出检索到的项目、赛道、技术、估值、事件、人物或既有来源，以及本材料是强化、修正还是反驳。 -->

## 对既有认知的影响

<!-- 写清强化、修正或推翻了什么；没有变化时也可明确写“无”。 -->

## 对投资判断的启发

## 最强反方与证伪信号

## 后续问题

## Memory Graph 写回

<!-- 只列实际更新或建议更新的既有对象；没有高价值增量时写“无”。 -->
"""


TEMPLATE_PLACEHOLDER = """# 知识来源｜来源主体｜主题

- 类型: expert_interview / thematic_material
- 日期: YYYY-MM-DD
- 来源主体:
- 主题:
- 来源链接:
- 相关赛道:
- 相关技术主题:
- 相关项目:
- 原始资料: `原始资料/`
- 解析文本: `解析文本/`
- 最近更新: YYYY-MM-DD

## 一句话
## 来源与背景
## 主要内容
## 技术与商业机制
## 核心 Takeaways
## 事实、观点与待核实
### 已核验事实
### 来源观点
### 待核实
## 转写风险与口径校正
## 与既有 Memory 的连接
## 对既有认知的影响
## 对投资判断的启发
## 最强反方与证伪信号
## 后续问题
## Memory Graph 写回
"""


def display_value(value: str, field: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f]", " ", value.strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        raise ValueError(f"{field} must contain a usable value")
    return cleaned


def safe_component(value: str, field: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", "-", display_value(value, field))
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .-")
    if not cleaned or cleaned in {".", ".."}:
        raise ValueError(f"{field} must contain a usable name")
    return cleaned


def valid_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def write_if_missing(path: Path, content: str) -> str:
    if path.exists():
        return "exists"
    path.write_text(content, encoding="utf-8")
    return "created"


def initialize_library(knowledge_root: Path) -> list[str]:
    events: list[str] = []
    for relative in ("专家访谈", "主题资料", "templates"):
        path = knowledge_root / relative
        path.mkdir(parents=True, exist_ok=True)
        events.append(f"dir     {path}")

    readme = knowledge_root / "README.md"
    template = knowledge_root / "templates" / "核心整理模板.md"
    events.append(f"{write_if_missing(readme, LIBRARY_README):7} {readme}")
    events.append(
        f"{write_if_missing(template, TEMPLATE_PLACEHOLDER):7} {template}"
    )
    return events


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize the AI Work Hub non-project knowledge-source layer."
    )
    parser.add_argument(
        "--workspace-root",
        default=str(Path.home() / "Documents" / "AI Work Hub"),
        help="AI Work Hub workspace root. Default: ~/Documents/AI Work Hub",
    )
    parser.add_argument(
        "--knowledge-root",
        default=None,
        help="Override knowledge-source root. Default: <workspace-root>/知识来源",
    )
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Create only the library root, categories, README, and template.",
    )
    parser.add_argument("--kind", choices=sorted(KINDS))
    parser.add_argument("--date", type=valid_date, default=date.today().isoformat())
    parser.add_argument("--name", help="Expert, institution, publication, or source name.")
    parser.add_argument("--topic", help="Short reusable topic name.")
    parser.add_argument(
        "--with-workspace",
        action="store_true",
        help="Also create an optional 工作区/ for temporary analysis artifacts.",
    )
    args = parser.parse_args()

    if not args.init_only:
        missing = [
            flag
            for flag, value in (
                ("--kind", args.kind),
                ("--name", args.name),
                ("--topic", args.topic),
            )
            if not value
        ]
        if missing:
            parser.error(f"required unless --init-only: {', '.join(missing)}")

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    knowledge_root = (
        Path(args.knowledge_root).expanduser().resolve()
        if args.knowledge_root
        else workspace_root / "知识来源"
    )
    knowledge_root.mkdir(parents=True, exist_ok=True)

    events = initialize_library(knowledge_root)
    if args.init_only:
        print(f"Knowledge-source library initialized at: {knowledge_root}")
        for event in events:
            print(event)
        return 0

    category, kind_key = KINDS[args.kind]
    name = display_value(args.name, "name")
    topic = display_value(args.topic, "topic")
    path_name = safe_component(name, "name")
    path_topic = safe_component(topic, "topic")
    source_date = args.date
    source_root = (
        knowledge_root
        / category
        / source_date[:4]
        / f"{source_date}_{path_name}_{path_topic}"
    )

    for relative in ("原始资料", "解析文本"):
        path = source_root / relative
        path.mkdir(parents=True, exist_ok=True)
        events.append(f"dir     {path}")
    if args.with_workspace:
        path = source_root / "工作区"
        path.mkdir(parents=True, exist_ok=True)
        events.append(f"dir     {path}")

    core_note = source_root / f"{source_date}_核心整理.md"
    content = CORE_TEMPLATE.format(
        name=name,
        topic=topic,
        kind_key=kind_key,
        source_date=source_date,
    )
    events.append(f"{write_if_missing(core_note, content):7} {core_note}")

    print(f"Knowledge source initialized at: {source_root}")
    for event in events:
        print(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
