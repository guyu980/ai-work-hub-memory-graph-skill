#!/usr/bin/env python3
"""Validate Memory Graph v2 structure, enums, indexes, and project links."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from memory_graph_lib import (
    file_hash,
    load_config,
    parse_markdown,
    project_card_name,
    read_jsonl,
    resolve_workspace_path,
    value_from_fields,
)


def add_error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def unique(records: list[dict[str, Any]], key: str, path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for record in records:
        value = str(record.get(key, ""))
        if not value:
            add_error(errors, path, f"missing {key}")
        elif value in seen:
            add_error(errors, path, f"duplicate {key}: {value}")
        seen.add(value)
    return errors


def validate_project_records(
    workspace_root: Path,
    memory_root: Path,
    records: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    enum_fields = {
        "intake_mode": "intake_modes",
        "historical_outcome": "historical_outcomes",
        "review_status": "review_statuses",
        "project_status": "project_statuses",
        "process_stage": "process_stages",
        "investment_decision": "investment_decisions",
        "recommended_play": "recommended_plays",
        "position_size": "position_sizes",
        "price_view": "price_views",
        "confidence": "confidence_levels",
    }
    errors.extend(unique(records, "project_id", memory_root / "00_索引/项目索引.jsonl"))
    errors.extend(unique(records, "name", memory_root / "00_索引/项目索引.jsonl"))
    for record in records:
        name = str(record.get("name", "<unknown>"))
        for field, config_key in enum_fields.items():
            if record.get(field) not in config[config_key]:
                add_error(
                    errors,
                    memory_root / "00_索引/项目索引.jsonl",
                    f"{name}: invalid {field}={record.get(field)!r}",
                )
        sector = record.get("primary_sector")
        if sector not in config["primary_sectors"]:
            add_error(
                errors,
                memory_root / "00_索引/项目索引.jsonl",
                f"{name}: unknown primary_sector={sector!r}",
            )
        if (
            record.get("intake_mode") == "historical_review"
            and record.get("historical_outcome") == "not_applicable"
        ):
            add_error(
                errors,
                memory_root / "00_索引/项目索引.jsonl",
                f"{name}: historical_review requires a historical_outcome",
            )
        if (
            record.get("intake_mode") == "historical_review"
            and record.get("review_status") == "not_applicable"
        ):
            add_error(
                errors,
                memory_root / "00_索引/项目索引.jsonl",
                f"{name}: historical_review requires a review_status",
            )
        if (
            record.get("intake_mode") == "live"
            and record.get("historical_outcome") != "not_applicable"
        ):
            add_error(
                errors,
                memory_root / "00_索引/项目索引.jsonl",
                f"{name}: live intake has historical_outcome",
            )
        card_path = memory_root / str(record.get("source_path", ""))
        if not card_path.exists():
            add_error(errors, card_path, f"{name}: project card missing")
            continue
        parsed = parse_markdown(card_path)
        if project_card_name(parsed) != name:
            add_error(errors, card_path, f"title does not match index name {name}")
        if value_from_fields(parsed["fields"], "Schema Version") != "2":
            add_error(errors, card_path, "missing Schema Version: 2")
        state_value = str(record.get("state_path", "")).strip()
        if state_value:
            state_path = resolve_workspace_path(workspace_root, state_value)
            if not state_path or not state_path.exists():
                add_error(errors, card_path, f"state file missing: {state_value}")
            else:
                try:
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    add_error(errors, state_path, f"invalid JSON: {exc}")
                else:
                    if state.get("project_id") != record.get("project_id"):
                        add_error(errors, state_path, "project_id differs from index")
                    for field in enum_fields:
                        if state.get(field) != record.get(field):
                            add_error(
                                errors,
                                state_path,
                                f"{field} differs from generated index",
                            )
                    for field in (
                        "judgment_display",
                        "source_hash",
                        "updated_at",
                    ):
                        if state.get(field) != record.get(field):
                            add_error(
                                errors,
                                state_path,
                                f"{field} differs from generated index",
                            )
                    source_files: list[Path] = []
                    for source_ref in [
                        state.get("running_judgment_path", ""),
                        state.get("evidence_ledger_path", ""),
                        *state.get("source_refs", []),
                    ]:
                        source_path = resolve_workspace_path(
                            workspace_root,
                            str(source_ref),
                        )
                        if source_path and source_path.exists():
                            source_files.append(source_path)
                    expected_hash = file_hash(source_files)
                    if state.get("source_hash") != expected_hash:
                        add_error(
                            errors,
                            state_path,
                            "source_hash is stale; run sync_project.py",
                        )
        evidence_value = str(record.get("evidence_ledger_path", "")).strip()
        if evidence_value:
            evidence_path = resolve_workspace_path(workspace_root, evidence_value)
            if not evidence_path or not evidence_path.exists():
                add_error(
                    errors,
                    card_path,
                    f"evidence ledger missing: {evidence_value}",
                )
            else:
                for item in read_jsonl(evidence_path):
                    if item.get("evidence_tier") not in config["evidence_tiers"]:
                        add_error(
                            errors,
                            evidence_path,
                            f"invalid evidence_tier={item.get('evidence_tier')!r}",
                        )
                    if item.get("status") not in config["evidence_statuses"]:
                        add_error(
                            errors,
                            evidence_path,
                            f"invalid status={item.get('status')!r}",
                        )
                    if item.get("decision_impact") not in config["decision_impacts"]:
                        add_error(
                            errors,
                            evidence_path,
                            "invalid decision_impact="
                            f"{item.get('decision_impact')!r}",
                        )
                    if (
                        item.get("temporal_scope")
                        not in config["evidence_temporal_scopes"]
                    ):
                        add_error(
                            errors,
                            evidence_path,
                            "invalid temporal_scope="
                            f"{item.get('temporal_scope')!r}",
                        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    args = parser.parse_args()
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else workspace_root / "Memory Graph"
    )
    config = load_config(memory_root)
    errors: list[str] = []
    warnings: list[str] = []

    index_names = [
        "项目索引.jsonl",
        "关系索引.jsonl",
        "赛道索引.jsonl",
        "技术主题索引.jsonl",
        "估值索引.jsonl",
        "事件索引.jsonl",
        "人物索引.jsonl",
    ]
    indexes: dict[str, list[dict[str, Any]]] = {}
    for name in index_names:
        path = memory_root / "00_索引" / name
        try:
            indexes[name] = read_jsonl(path)
        except ValueError as exc:
            errors.append(str(exc))

    projects = indexes.get("项目索引.jsonl", [])
    errors.extend(
        validate_project_records(workspace_root, memory_root, projects, config)
    )
    project_names = {str(item.get("name")) for item in projects}
    project_ids = {str(item.get("project_id")) for item in projects}

    relations = indexes.get("关系索引.jsonl", [])
    errors.extend(
        unique(relations, "relation_id", memory_root / "00_索引/关系索引.jsonl")
    )
    for relation in relations:
        if relation.get("relation_type") not in config["relation_types"]:
            add_error(
                errors,
                memory_root / "00_索引/关系索引.jsonl",
                f"invalid relation_type={relation.get('relation_type')!r}",
            )
        if relation.get("from_kind") == "project":
            if str(relation.get("from_id")) not in project_ids:
                add_error(
                    errors,
                    memory_root / "00_索引/关系索引.jsonl",
                    f"unknown source project {relation.get('from_name')!r}",
                )
        if relation.get("to_kind") == "project":
            if str(relation.get("to_name")) not in project_names:
                add_error(
                    errors,
                    memory_root / "00_索引/关系索引.jsonl",
                    f"unknown target project {relation.get('to_name')!r}",
                )

    for name, key in [
        ("赛道索引.jsonl", "sector_id"),
        ("技术主题索引.jsonl", "theme_id"),
        ("估值索引.jsonl", "valuation_id"),
        ("事件索引.jsonl", "event_id"),
        ("人物索引.jsonl", "person_id"),
    ]:
        errors.extend(unique(indexes.get(name, []), key, memory_root / "00_索引" / name))
        for record in indexes.get(name, []):
            source_path = memory_root / str(record.get("source_path", ""))
            if not source_path.is_file():
                add_error(errors, source_path, f"missing source for {key}")

    graph_only = [
        item["name"] for item in projects if not str(item.get("state_path", "")).strip()
    ]
    if graph_only:
        warnings.append(
            "graph-only projects without a project state file: "
            + ", ".join(graph_only)
        )

    print(
        "Validated: "
        f"{len(projects)} projects, "
        f"{len(relations)} relationships, "
        f"{len(indexes.get('赛道索引.jsonl', []))} sectors, "
        f"{len(indexes.get('技术主题索引.jsonl', []))} technical themes"
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print(f"FAILED with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: Memory Graph v2 is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
