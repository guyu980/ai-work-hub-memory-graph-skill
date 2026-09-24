#!/usr/bin/env python3
"""Sync a compact project projection without inventing or changing its judgment."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from memory_graph_lib import (file_hash, graph_lock, parse_markdown, project_card_name,
                              replace_card_header, resolve_workspace_path,
                              state_to_card_fields, write_json_atomic, write_text_atomic)
from rebuild_indexes import rebuild


COMPACT_FIELDS = ("Schema Version", "项目 ID", "创建日期", "最近更新", "主赛道",
                  "标签", "别名", "项目状态", "当前投资判断", "状态文件", "同步哈希")


def initial_card_text(state: dict[str, Any]) -> str:
    return f"# 项目卡片｜{state['name']}\n\n## 一句话\n\n{state.get('summary', '')}\n"


def compact_header(state: dict[str, Any], text: str, state_path: str) -> str:
    fields = state_to_card_fields({**state, "state_path": state_path})
    return replace_card_header(text, [(key, fields[key]) for key in COMPACT_FIELDS if key in fields])


def sync(workspace: Path, memory: Path, state_path: Path, skip_rebuild: bool = False) -> Path:
    workspace, memory, state_path = workspace.resolve(), memory.resolve(), state_path.resolve()
    with graph_lock(memory):
        state = json.loads(state_path.read_text(encoding="utf-8"))
        name = str(state["name"])
        if "/" in name or "\\" in name:
            raise ValueError("project name cannot contain path separators; use aliases")
        cards = [p for p in (memory / "01_项目卡片").glob("*.md")
                 if project_card_name(parse_markdown(p)) == name]
        if len(cards) > 1:
            raise ValueError(f"expected one card for {name}, found {len(cards)}")
        created = str(state.get("created_at") or datetime.now().date().isoformat())
        card = cards[0] if cards else memory / "01_项目卡片" / f"{created}_{name}.md"
        if not cards and card.exists():
            raise ValueError(f"unrecognized card already exists: {card}")
        text = card.read_text(encoding="utf-8") if cards else initial_card_text(state)
        sources = [resolve_workspace_path(workspace, str(ref)) for ref in
                   [state.get("running_judgment_path", ""), *state.get("source_refs", [])]]
        state["source_hash"] = file_hash(p for p in sources if p)
        state["last_synced_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        write_json_atomic(state_path, state)
        write_text_atomic(card, compact_header(state, text, state_path.relative_to(workspace).as_posix()))
        write_json_atomic(memory / ".system" / "last-sync.json", {
            "schema_version": 2, "action": "sync_project", "project": name,
            "state_path": state_path.relative_to(workspace).as_posix(),
            "card_path": card.relative_to(memory).as_posix(), "completed_at": state["last_synced_at"],
        })
        if not skip_rebuild:
            rebuild(workspace, memory)
        return card


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--skip-rebuild", action="store_true")
    args = parser.parse_args()
    workspace = Path(args.workspace_root).expanduser().resolve()
    memory = Path(args.memory_root).expanduser().resolve() if args.memory_root else workspace / "Memory Graph"
    card = sync(workspace, memory, Path(args.state).expanduser().resolve(), args.skip_rebuild)
    print(f"Synced: {card}")
    print("Header sync does not establish that the analytical prose is current; read back the changed sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
