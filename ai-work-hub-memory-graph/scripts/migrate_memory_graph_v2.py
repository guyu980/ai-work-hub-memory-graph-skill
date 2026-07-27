#!/usr/bin/env python3
"""Migrate an existing AI Work Hub Memory Graph to schema v2."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from memory_graph_lib import (
    DEFAULT_CONFIG,
    SCHEMA_VERSION,
    file_hash,
    find_project_dir,
    infer_state,
    parse_markdown,
    project_card_name,
    replace_card_header,
    resolve_workspace_path,
    split_csv,
    state_to_card_fields,
    value_from_fields,
    write_json_atomic,
)


def relative_to_workspace(path: Path, workspace_root: Path) -> str:
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return str(path)


def load_overrides(memory_root: Path) -> dict[str, str]:
    path = memory_root / "config" / "project-path-overrides.json"
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {str(key): str(item) for key, item in value.items()}


def load_state_overrides(memory_root: Path) -> dict[str, dict[str, Any]]:
    path = memory_root / "config" / "migration-state-overrides.json"
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    result: dict[str, dict[str, Any]] = {}
    for key, item in value.items():
        if not isinstance(item, dict):
            raise ValueError(f"{path}: override for {key!r} must be an object")
        result[str(key)] = item
    return result


def load_legacy_index(memory_root: Path) -> dict[str, dict[str, Any]]:
    path = memory_root / "00_索引" / "项目索引.jsonl"
    result: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return result
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict) or not value.get("name"):
            raise ValueError(f"{path}:{line_number}: invalid project record")
        result[str(value["name"])] = value
    return result


def locate_running_judgment(project_dir: Path, canonical_name: str) -> Path | None:
    output_dir = project_dir / "输出文档"
    if not output_dir.is_dir():
        return None
    preferred = [
        output_dir / f"{canonical_name}_项目判断与todo.md",
        output_dir / f"{project_dir.name}_项目判断与todo.md",
    ]
    for path in preferred:
        if path.exists():
            return path
    candidates = sorted(
        [
            *output_dir.glob("*项目判断*todo*.md"),
            *output_dir.glob("*项目推进底稿*.md"),
            *output_dir.glob("*判断更新*.md"),
        ],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def normalize_date(value: str, fallback: str) -> str:
    value = value.strip()
    if len(value) >= 10:
        return value[:10]
    return fallback


def migrate_card(
    card_path: Path,
    workspace_root: Path,
    memory_root: Path,
    legacy_record: dict[str, Any] | None,
    overrides: dict[str, str],
    state_overrides: dict[str, dict[str, Any]],
    dry_run: bool,
) -> tuple[dict[str, Any], str]:
    parsed = parse_markdown(card_path)
    fields = parsed["fields"]
    name = project_card_name(parsed)
    record = legacy_record or {}
    aliases = list(
        dict.fromkeys(
            [
                *split_csv(record.get("aliases", [])),
                *split_csv(value_from_fields(fields, "别名")),
            ]
        )
    )
    legacy_status = value_from_fields(
        fields,
        "项目状态",
        "当前状态",
        default=str(record.get("status", "")),
    )
    judgment_display = value_from_fields(
        fields,
        "当前投资判断",
        default=str(record.get("judgment", "观察")),
    )
    inferred = infer_state(legacy_status, judgment_display)
    structured_labels = {
        "project_status": "项目状态",
        "process_stage": "流程阶段",
        "investment_decision": "投资判断",
        "recommended_play": "建议打法",
        "position_size": "仓位",
        "price_view": "价格判断",
        "confidence": "判断置信度",
    }
    for key, label in structured_labels.items():
        if fields.get(label):
            inferred[key] = fields[label]
    project_id = value_from_fields(fields, "项目 ID", default=f"project:{name}")
    created_at = normalize_date(
        value_from_fields(fields, "创建日期"),
        card_path.name[:10] if card_path.name[:10].count("-") == 2 else str(date.today()),
    )
    updated_at = normalize_date(
        value_from_fields(
            fields,
            "最近更新",
            default=str(record.get("updated_at", "")),
        ),
        created_at,
    )
    primary_sector = value_from_fields(
        fields,
        "主赛道",
        default=str(record.get("primary_sector", "")),
    )
    tags = list(
        dict.fromkeys(
            [
                *split_csv(record.get("tags", [])),
                *split_csv(value_from_fields(fields, "标签")),
            ]
        )
    )
    project_dir = find_project_dir(workspace_root, name, aliases, overrides)
    running_judgment = (
        locate_running_judgment(project_dir, name) if project_dir else None
    )
    state_path = (
        project_dir / "输出文档" / f"{name}_项目状态.json"
        if project_dir
        else None
    )
    evidence_path = (
        project_dir / "解析文本" / "证据账本.jsonl"
        if project_dir
        else None
    )

    source_refs: list[str] = []
    if running_judgment:
        source_refs.append(relative_to_workspace(running_judgment, workspace_root))
    for item in split_csv(value_from_fields(fields, "资料来源")):
        if item not in source_refs:
            source_refs.append(item)

    source_files = [path for path in [running_judgment, evidence_path] if path]
    for source_ref in source_refs:
        source_path = resolve_workspace_path(workspace_root, source_ref)
        if source_path and source_path.exists():
            source_files.append(source_path)
    source_hash = file_hash(source_files)
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "type": "project_state",
        "project_id": project_id,
        "name": name,
        "aliases": aliases,
        "primary_sector": primary_sector,
        "tags": tags,
        "intake_mode": "live",
        "historical_outcome": "not_applicable",
        "review_status": "not_applicable",
        "historical_decision_date": "",
        "review_as_of": "",
        **inferred,
        "judgment_display": judgment_display,
        "stage": str(record.get("stage", "")),
        "valuation": str(record.get("valuation", "")),
        "summary": parsed["sections"].get("一句话", "").strip(),
        "blocking_gates": [],
        "watch_signals": [],
        "related_projects": list(record.get("related_projects", [])),
        "counterexamples": list(record.get("counterexamples", [])),
        "source_refs": source_refs,
        "running_judgment_path": (
            relative_to_workspace(running_judgment, workspace_root)
            if running_judgment
            else ""
        ),
        "card_path": relative_to_workspace(card_path, memory_root),
        "evidence_ledger_path": (
            relative_to_workspace(evidence_path, workspace_root)
            if evidence_path
            else ""
        ),
        "evidence_backfill_status": "pending",
        "source_hash": source_hash,
        "created_at": created_at,
        "updated_at": updated_at,
        "last_synced_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "migration_status": "migrated" if project_dir else "graph_only",
    }

    if state_path and not dry_run:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        if not evidence_path.exists():
            evidence_path.touch()
        if state_path.exists():
            existing = json.loads(state_path.read_text(encoding="utf-8"))
            for key in (
                "project_status",
                "intake_mode",
                "historical_outcome",
                "review_status",
                "historical_decision_date",
                "review_as_of",
                "process_stage",
                "investment_decision",
                "recommended_play",
                "position_size",
                "price_view",
                "confidence",
                "blocking_gates",
                "watch_signals",
                "evidence_backfill_status",
            ):
                if existing.get(key):
                    state[key] = existing[key]
        state.update(state_overrides.get(name, {}))
        write_json_atomic(state_path, state)
    else:
        state.update(state_overrides.get(name, {}))

    card_state = dict(state)
    card_state["state_path"] = (
        relative_to_workspace(state_path, workspace_root) if state_path else ""
    )
    ordered = state_to_card_fields(card_state)
    ordered_fields = [
        (label, ordered[label])
        for label in (
            "Schema Version",
            "项目 ID",
            "创建日期",
            "最近更新",
            "最近同步",
            "主赛道",
            "标签",
            "别名",
            "资料模式",
            "历史结果",
            "复盘状态",
            "历史决策日期",
            "复盘基准日",
            "项目状态",
            "流程阶段",
            "投资判断",
            "建议打法",
            "仓位",
            "价格判断",
            "判断置信度",
            "当前投资判断",
            "融资阶段",
            "估值摘要",
            "状态文件",
            "证据账本",
            "资料来源",
            "同步哈希",
            "证据回填状态",
        )
        if label in ordered
    ]
    migrated_text = replace_card_header(parsed["text"], ordered_fields)
    if not dry_run:
        card_path.write_text(migrated_text, encoding="utf-8")
    return state, "linked" if project_dir else "graph_only"


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
    (memory_root / "config").mkdir(parents=True, exist_ok=True)
    config_path = memory_root / "config" / "schema-v2.json"
    merged_config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        loaded_config = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(loaded_config, dict):
            raise ValueError(f"{config_path} must contain a JSON object")
        merged_config.update(loaded_config)
    if not args.dry_run:
        write_json_atomic(config_path, merged_config)

    legacy = load_legacy_index(memory_root)
    overrides = load_overrides(memory_root)
    state_overrides = load_state_overrides(memory_root)
    results: list[tuple[str, str]] = []
    for card_path in sorted((memory_root / "01_项目卡片").glob("*.md")):
        name = project_card_name(parse_markdown(card_path))
        state, status = migrate_card(
            card_path,
            workspace_root,
            memory_root,
            legacy.get(name),
            overrides,
            state_overrides,
            args.dry_run,
        )
        results.append((state["name"], status))

    print(
        f"{'Would migrate' if args.dry_run else 'Migrated'} "
        f"{len(results)} project cards to schema v2"
    )
    for name, status in results:
        print(f"- {name}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
