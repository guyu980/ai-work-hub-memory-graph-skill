#!/usr/bin/env python3
"""Sync one project state to its Memory Graph card."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from memory_graph_lib import (
    file_hash,
    parse_markdown,
    project_card_name,
    replace_card_header,
    state_to_card_fields,
    resolve_workspace_path,
    write_json_atomic,
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def workspace_path(workspace_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else workspace_root / path


def append_review_note(
    memory_root: Path,
    project_name: str,
    delta: dict[str, Any],
    timestamp: str,
) -> Path | None:
    proposals: dict[str, list[Any]] = {}
    for kind in (
        "sector_updates",
        "technical_theme_updates",
        "valuation_updates",
        "event_triggers",
        "person_updates",
    ):
        values = delta.get(kind, [])
        if values:
            proposals[kind] = values
    if not proposals:
        return None
    path = memory_root / "待复核.md"
    if path.exists():
        existing = path.read_text(encoding="utf-8").rstrip()
    else:
        existing = "# 待复核\n\n## 待处理"
    payload = json.dumps(proposals, ensure_ascii=False, indent=2)
    section = (
        f"\n\n### {timestamp} | {project_name}\n\n"
        "仅在没有安全目标文件时保留；确认后更新对应知识文件并删除本条。\n\n"
        f"```json\n{payload}\n```\n"
    )
    path.write_text(existing + section, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--graph-delta")
    parser.add_argument("--skip-rebuild", action="store_true")
    args = parser.parse_args()
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else workspace_root / "Memory Graph"
    )
    state_path = Path(args.state).expanduser().resolve()
    state = load_json(state_path)
    project_name = str(state["name"])
    cards = []
    for card_path in (memory_root / "01_项目卡片").glob("*.md"):
        if project_card_name(parse_markdown(card_path)) == project_name:
            cards.append(card_path)
    if len(cards) != 1:
        raise ValueError(
            f"expected exactly one card for {project_name}, found {len(cards)}"
        )
    card_path = cards[0]
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    running = workspace_path(
        workspace_root,
        str(state.get("running_judgment_path", "")),
    )
    source_files = [running] if running else []
    evidence = workspace_path(
        workspace_root,
        str(state.get("evidence_ledger_path", "")),
    )
    if evidence:
        source_files.append(evidence)
    for source_ref in state.get("source_refs", []):
        source_path = resolve_workspace_path(workspace_root, str(source_ref))
        if source_path and source_path.exists():
            source_files.append(source_path)
    state["source_hash"] = file_hash(source_files)
    state["last_synced_at"] = now
    write_json_atomic(state_path, state)

    parsed = parse_markdown(card_path)
    card_state = dict(state)
    card_state["state_path"] = state_path.relative_to(workspace_root).as_posix()
    ordered = state_to_card_fields(card_state)
    field_order = [
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
    ]
    card_path.write_text(
        replace_card_header(
            parsed["text"],
            [(label, ordered[label]) for label in field_order if label in ordered],
        ),
        encoding="utf-8",
    )

    review_note = None
    if args.graph_delta:
        review_note = append_review_note(
            memory_root,
            project_name,
            load_json(Path(args.graph_delta).expanduser().resolve()),
            now,
        )
    system_root = memory_root / ".system"
    system_root.mkdir(parents=True, exist_ok=True)
    log_path = system_root / "last-sync.json"
    write_json_atomic(
        log_path,
        {
            "schema_version": 2,
            "action": "sync_project",
            "project": project_name,
            "state_path": state_path.relative_to(workspace_root).as_posix(),
            "card_path": card_path.relative_to(memory_root).as_posix(),
            "review_note_path": (
                review_note.relative_to(memory_root).as_posix()
                if review_note
                else ""
            ),
            "completed_at": now,
        },
    )
    if not args.skip_rebuild:
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("rebuild_indexes.py")),
                "--workspace-root",
                str(workspace_root),
                "--memory-root",
                str(memory_root),
            ],
            check=True,
        )
    print(f"Synced {project_name}")
    if review_note:
        print(f"Appended unresolved graph delta to: {review_note}")
    print(f"Latest sync metadata: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
