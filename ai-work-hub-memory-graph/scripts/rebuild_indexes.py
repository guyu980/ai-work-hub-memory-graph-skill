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
    first_paragraph,
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
            state.get("related_projects")
            or section_entities(sections.get("相似项目", ""))
        )
        counterexamples = list(
            state.get("counterexamples")
            or section_entities(sections.get("反例项目", ""))
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
            "evidence_ledger_path": value_from_fields(fields, "证据账本"),
            "source_hash": value_from_fields(fields, "同步哈希"),
            "related_projects": related,
            "counterexamples": counterexamples,
            "updated_at": str(
                state.get("updated_at")
                or value_from_fields(fields, "最近更新")
            ),
            "summary": str(
                state.get("summary")
                or first_paragraph(sections.get("一句话", ""))
            ),
        }
        projects.append(record)

        for target, relation_type in [
            *((item, "comparable_to") for item in related),
            *((item, "counterexample_of") for item in counterexamples),
        ]:
            canonical = alias_to_name.get(target)
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
    for path in sorted((memory_root / "06_事件卡片").glob("*.md")):
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
                "primary_sector": value_from_fields(fields, "主赛道"),
                "tags": split_csv(fields.get("标签")),
                "event_type": value_from_fields(fields, "事件类型"),
                "impact": value_from_fields(fields, "影响等级"),
                "source_refs": split_csv(fields.get("来源")),
                "source_path": path.relative_to(memory_root).as_posix(),
                "related_projects": section_entities(
                    sections.get("影响哪些项目/赛道", "")
                ),
                "summary": first_paragraph(sections.get("为什么重要", "")),
            }
        )
    return records


def person_records(memory_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((memory_root / "08_人物卡片").glob("*.md")):
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
                    default="partial"
                    if any("pending" in item for item in source_tiers)
                    else "verified",
                ),
                "current_org_role": value_from_fields(fields, "当前机构/角色"),
                "related_projects": split_csv(fields.get("相关项目")),
                "primary_sectors": split_csv(fields.get("相关赛道")),
                "tags": split_csv(fields.get("标签")),
                "source_tiers": source_tiers,
                "source_path": path.relative_to(memory_root).as_posix(),
                "updated_at": value_from_fields(fields, "最近更新"),
                "summary": first_paragraph(sections.get("一句话", "")),
            }
        )
    return records


def thesis_records(memory_root: Path) -> list[dict[str, Any]]:
    path = memory_root / "05_观点账本" / "观点账本.md"
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^##\s+", text)[1:]
    records: list[dict[str, Any]] = []
    for chunk in chunks:
        lines = chunk.splitlines()
        title = lines[0].strip()
        fields: dict[str, str] = {}
        for line in lines[1:]:
            match = re.match(r"^-\s+([^:：]+)[:：]\s*(.*)$", line)
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        thesis = fields.get("观点", "").strip()
        if not thesis:
            continue
        records.append(
            {
                "schema_version": 2,
                "type": "thesis",
                "thesis_id": stable_id("thesis", title),
                "title": title,
                "thesis": thesis,
                "status": fields.get("状态", ""),
                "confidence": fields.get("置信度", ""),
                "supporting_evidence": fields.get("支持证据", ""),
                "counterevidence": fields.get("反向证据", ""),
                "related_projects": split_csv(fields.get("相关项目")),
                "related_events": split_csv(fields.get("相关事件")),
                "falsifier": fields.get("什么信号会推翻", ""),
                "updated_at": fields.get("最近更新", ""),
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
                "updated_at": first_paragraph(
                    parsed["sections"].get("最近更新", "")
                ),
                "summary": first_paragraph(
                    parsed["sections"].get("我们自己的价格纪律", "")
                ),
            }
        )
    return records


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

    projects, relations = project_records(workspace_root, memory_root)
    outputs = {
        "项目索引.jsonl": projects,
        "关系索引.jsonl": relations,
        "事件索引.jsonl": event_records(memory_root),
        "人物索引.jsonl": person_records(memory_root),
        "观点索引.jsonl": thesis_records(memory_root),
        "估值索引.jsonl": valuation_records(memory_root),
    }
    for name, records in outputs.items():
        path = memory_root / "00_索引" / name
        if not args.dry_run:
            write_jsonl_atomic(path, records)
        print(
            f"{'would write' if args.dry_run else 'wrote'} "
            f"{len(records):>3} records -> {path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
