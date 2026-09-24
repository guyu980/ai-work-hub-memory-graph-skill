#!/usr/bin/env python3
"""Rebuild all generated Memory Graph JSONL indexes from Markdown and state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from memory_graph_lib import (
    content_date,
    first_paragraph,
    graph_lock,
    markdown_links,
    parse_markdown,
    project_card_name,
    resolve_workspace_path,
    section_entities,
    split_csv,
    value_from_fields,
    write_jsonl_atomic,
)


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}:{digest}"


def latest_date(text: str) -> str:
    values = re.findall(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)", text)
    return max(values) if values else ""


def compact_text(text: str, limit: int = 700) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def compact_entities(text: str) -> list[str]:
    entities = section_entities(text)
    if entities:
        return entities
    compact = compact_text(text)
    return [compact] if compact else []


def load_state(workspace_root: Path, fields: dict[str, str]) -> dict[str, Any]:
    path = resolve_workspace_path(
        workspace_root,
        value_from_fields(fields, "状态文件"),
    )
    if path and path.exists():
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    return {}


def project_records(
    workspace_root: Path,
    memory_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    projects: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    card_payloads: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    alias_to_name: dict[str, str] = {}

    for path in sorted((memory_root / "01_项目卡片").glob("*.md")):
        parsed = parse_markdown(path)
        fields = parsed["fields"]
        state = load_state(workspace_root, fields)
        name = str(state.get("name") or project_card_name(parsed))
        aliases = state.get("aliases") or split_csv(fields.get("别名"))
        alias_to_name[name] = name
        for alias in aliases:
            alias_to_name[str(alias)] = name
        card_payloads.append((path, parsed, state))

    for path, parsed, state in card_payloads:
        fields = parsed["fields"]
        sections = parsed["sections"]
        name = str(state.get("name") or project_card_name(parsed))
        aliases = list(state.get("aliases") or split_csv(fields.get("别名")))
        related = list(
            state.get("related_projects", section_entities(sections.get("相似项目", "")))
        )
        counterexamples = list(
            state.get("counterexamples", section_entities(sections.get("反例项目", "")))
        )
        record = {
            "schema_version": 2,
            "type": "project",
            "project_id": str(
                state.get("project_id")
                or value_from_fields(fields, "项目 ID", default=f"project:{name}")
            ),
            "name": name,
            "aliases": aliases,
            "primary_sector": str(
                state.get("primary_sector")
                or value_from_fields(fields, "主赛道")
            ),
            "tags": list(state.get("tags") or split_csv(fields.get("标签"))),
            "intake_mode": str(
                state.get("intake_mode")
                or value_from_fields(fields, "资料模式", default="live")
            ),
            "historical_outcome": str(
                state.get("historical_outcome")
                or value_from_fields(
                    fields,
                    "历史结果",
                    default="not_applicable",
                )
            ),
            "review_status": str(
                state.get("review_status")
                or value_from_fields(
                    fields,
                    "复盘状态",
                    default="not_applicable",
                )
            ),
            "historical_decision_date": str(
                state.get("historical_decision_date")
                or value_from_fields(fields, "历史决策日期")
            ),
            "review_as_of": str(
                state.get("review_as_of")
                or value_from_fields(fields, "复盘基准日")
            ),
            "project_status": str(
                state.get("project_status")
                or value_from_fields(fields, "项目状态")
            ),
            "process_stage": str(
                state.get("process_stage")
                or value_from_fields(fields, "流程阶段")
            ),
            "investment_decision": str(
                state.get("investment_decision")
                or value_from_fields(fields, "投资判断")
            ),
            "recommended_play": str(
                state.get("recommended_play")
                or value_from_fields(fields, "建议打法")
            ),
            "position_size": str(
                state.get("position_size")
                or value_from_fields(fields, "仓位")
            ),
            "price_view": str(
                state.get("price_view")
                or value_from_fields(fields, "价格判断")
            ),
            "confidence": str(
                state.get("confidence")
                or value_from_fields(fields, "判断置信度")
            ),
            "judgment_display": str(
                state.get("judgment_display")
                or value_from_fields(fields, "当前投资判断")
            ),
            "stage": str(
                state.get("stage")
                or value_from_fields(fields, "融资阶段")
            ),
            "valuation": str(
                state.get("valuation")
                or value_from_fields(fields, "估值摘要")
            ),
            "source_path": path.relative_to(memory_root).as_posix(),
            "state_path": value_from_fields(fields, "状态文件"),
            "source_hash": value_from_fields(fields, "同步哈希"),
            "related_projects": related,
            "counterexamples": counterexamples,
            "updated_at": str(
                state.get("updated_at")
                or value_from_fields(fields, "最近更新")
            ),
            "summary": str(
                first_paragraph(sections.get("一句话", "") or sections.get("定位与业务", ""))
                or state.get("summary", "")
            ),
        }
        projects.append(record)

        for target, relation_type in [
            *((item, "relates_to") for item in related),
            *((item, "counterexample_of") for item in counterexamples),
        ]:
            canonical = alias_to_name.get(target)
            if not canonical:
                # General failure patterns are prose, not invented company nodes.
                continue
            target_kind = "project" if canonical else "external_entity"
            target_value = canonical or target
            relation_key = f"{name}|{relation_type}|{target_kind}|{target_value}"
            relations.append(
                {
                    "schema_version": 2,
                    "type": "relationship",
                    "relation_id": stable_id("relation", relation_key),
                    "from_kind": "project",
                    "from_id": record["project_id"],
                    "from_name": name,
                    "relation_type": relation_type,
                    "to_kind": target_kind,
                    "to_id": (
                        f"project:{target_value}"
                        if target_kind == "project"
                        else stable_id("external", target_value)
                    ),
                    "to_name": target_value,
                    "source_path": record["source_path"],
                    "updated_at": record["updated_at"],
                }
            )

    return projects, relations


def event_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "05_事件卡片").glob("*.md")):
        parsed = parse_markdown(path)
        fields = parsed["fields"]
        sections = parsed["sections"]
        title = parsed["title"].split("｜", 1)[-1].strip()
        records.append(
            {
                "schema_version": 2,
                "type": "event",
                "event_id": stable_id("event", title),
                "title": title,
                "date": value_from_fields(fields, "日期"),
                "updated_at": content_date(parsed),
                "primary_sector": value_from_fields(fields, "主赛道"),
                "tags": split_csv(fields.get("标签")),
                "event_type": value_from_fields(fields, "事件类型"),
                "impact": value_from_fields(fields, "影响等级"),
                "source_refs": [href for _, href in markdown_links(sections.get("来源", ""))]
                or split_csv(fields.get("来源")),
                "source_path": path.relative_to(memory_root).as_posix(),
                "related_projects": section_entities(
                    sections.get("关联对象", "") or sections.get("影响哪些项目/赛道", "")
                ),
                "summary": first_paragraph(sections.get("当前影响", "") or sections.get("为什么重要", "")),
            }
        )
    return records


def person_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "06_人物卡片").glob("*.md")):
        parsed = parse_markdown(path)
        fields = parsed["fields"]
        sections = parsed["sections"]
        name = parsed["title"].split("｜", 1)[-1].strip()
        source_tiers = split_csv(fields.get("信息口径"))
        records.append(
            {
                "schema_version": 2,
                "type": "person",
                "person_id": stable_id("person", name),
                "name": name,
                "aliases": split_csv(fields.get("别名")),
                "identity_status": value_from_fields(
                    fields,
                    "身份状态",
                    default="partial",
                ),
                "current_org_role": value_from_fields(fields, "当前机构/角色"),
                "related_projects": split_csv(fields.get("相关项目")),
                "primary_sectors": split_csv(fields.get("相关赛道")),
                "tags": split_csv(fields.get("标签")),
                "source_tiers": source_tiers,
                "source_path": path.relative_to(memory_root).as_posix(),
                "updated_at": content_date(parsed),
                "summary": first_paragraph(sections.get("一句话", "")),
            }
        )
    return records


def sector_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "02_赛道地图").glob("*.md")):
        parsed = parse_markdown(path)
        sections = parsed["sections"]
        name = parsed["title"].split("｜", 1)[-1].strip()
        records.append(
            {
                "schema_version": 2,
                "type": "sector",
                "sector_id": stable_id("sector", name),
                "title": name,
                "primary_sector": name,
                "tags": split_csv(parsed["fields"].get("标签")),
                "aliases": split_csv(parsed["fields"].get("别名")),
                "summary": compact_text(sections.get("当前判断", "")),
                "strong_signals": compact_entities(
                    sections.get("强信号", "")
                ),
                "related_projects": section_entities(
                    sections.get("项目入口", "") or sections.get("已看项目", "")
                ),
                "counterexamples": section_entities(
                    sections.get("代表性反例", "")
                ),
                "updated_at": content_date(parsed),
                "source_path": path.relative_to(memory_root).as_posix(),
            }
        )
    return records


def technical_theme_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "03_技术主题").glob("*.md")):
        parsed = parse_markdown(path)
        sections = parsed["sections"]
        title = parsed["title"].split("｜", 1)[-1].strip()
        records.append(
            {
                "schema_version": 2,
                "type": "technical_theme",
                "theme_id": stable_id("technical-theme", title),
                "title": title,
                "tags": split_csv(parsed["fields"].get("标签")),
                "aliases": split_csv(parsed["fields"].get("别名")),
                "summary": compact_text(sections.get("当前理解", "")),
                "key_variables": compact_text(
                    sections.get("技术路线与关键变量", "")
                ),
                "validation_signals": compact_entities(
                    sections.get("可验证信号", "")
                ),
                "related_projects": section_entities(
                    sections.get("关联项目与研究", "") or sections.get("相关项目", "")
                ),
                "updated_at": content_date(parsed),
                "source_path": path.relative_to(memory_root).as_posix(),
            }
        )
    return records


def valuation_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "04_估值锚点").glob("*.md")):
        parsed = parse_markdown(path)
        sector = parsed["title"].split("｜", 1)[-1].strip()
        records.append(
            {
                "schema_version": 2,
                "type": "valuation_anchor",
                "valuation_id": stable_id("valuation", sector),
                "sector": sector,
                "source_path": path.relative_to(memory_root).as_posix(),
                "updated_at": content_date(parsed),
                "summary": compact_text(
                    parsed["sections"].get("适用边界", "")
                    or parsed["sections"].get("我们自己的价格纪律", "")
                ),
            }
        )
    return records


def record_id(record: dict[str, Any]) -> str:
    return next((str(value) for key, value in record.items() if key.endswith("_id")), "")


def linked_relations(workspace: Path, memory_root: Path,
                     outputs: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    records = [r for name, values in outputs.items() if name != "关系索引.jsonl" for r in values]
    by_path = {(memory_root / r["source_path"]).resolve(): r for r in records}
    sectors = {r.get("title"): r for r in records if r["type"] == "sector"}
    result = []
    for record in records:
        source = memory_root / record["source_path"]
        text = source.read_text(encoding="utf-8")
        targets = []
        for line in text.splitlines():
            for _, href in markdown_links(line):
                if "://" in href or href.startswith("#"):
                    continue
                path = (source.parent / href.split("#", 1)[0]).resolve()
                target = by_path.get(path)
                if not target and path.is_relative_to(workspace / "知识来源") and path.name.endswith("核心整理.md") and path.is_file():
                    target = {"type": "knowledge_source", "source_id": stable_id("source", path.relative_to(workspace).as_posix()),
                              "title": parse_markdown(path)["title"], "source_path": path.relative_to(workspace).as_posix()}
                if target:
                    targets.append((target, compact_text(line, 360)))
        if record.get("primary_sector") in sectors and record["type"] != "sector":
            targets.append((sectors[record["primary_sector"]], "主赛道"))
        for target, context in targets:
            if record_id(record) == record_id(target):
                continue
            relation = {"sector": "belongs_to", "person": "linked_person", "event": "affected_by",
                        "valuation_anchor": "uses_valuation_anchor", "knowledge_source": "draws_from"}.get(target["type"], "relates_to")
            key = f"{record_id(record)}|{relation}|{record_id(target)}"
            result.append({"schema_version": 2, "type": "relationship", "relation_id": stable_id("relation", key),
                           "from_kind": record["type"], "from_id": record_id(record),
                           "from_name": record.get("name", record.get("title", record.get("sector", ""))),
                           "relation_type": relation, "to_kind": target["type"], "to_id": record_id(target),
                           "to_name": target.get("name", target.get("title", target.get("sector", ""))),
                           "source_path": record["source_path"], "target_path": target["source_path"],
                           "context": context, "updated_at": record.get("updated_at", "")})
    return result


def build_outputs(workspace_root: Path, memory_root: Path) -> dict[str, list[dict[str, Any]]]:
    workspace_root, memory_root = workspace_root.resolve(), memory_root.resolve()
    projects, relations = project_records(workspace_root, memory_root)
    outputs = {
        "项目索引.jsonl": projects,
        "关系索引.jsonl": relations,
        "赛道索引.jsonl": sector_records(memory_root),
        "技术主题索引.jsonl": technical_theme_records(memory_root),
        "估值索引.jsonl": valuation_records(memory_root),
        "事件索引.jsonl": event_records(memory_root),
        "人物索引.jsonl": person_records(memory_root),
    }
    relations.extend(linked_relations(workspace_root, memory_root, outputs))
    outputs["关系索引.jsonl"] = list({r["relation_id"]: r for r in relations}.values())
    return outputs


def rebuild(workspace_root: Path, memory_root: Path, dry_run: bool = False) -> dict[str, int]:
    with graph_lock(memory_root):
        outputs = build_outputs(workspace_root, memory_root)
        for name, records in outputs.items():
            if not dry_run:
                write_jsonl_atomic(memory_root / "00_索引" / name, records)
        return {name: len(records) for name, records in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else workspace_root / "Memory Graph"
    )

    for name, count in rebuild(workspace_root, memory_root, args.dry_run).items():
        path = memory_root / "00_索引" / name
        print(
            f"{'would write' if args.dry_run else 'wrote'} "
            f"{count:>3} records -> {path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
