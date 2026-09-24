#!/usr/bin/env python3
"""Apply a reviewed Markdown batch with optimistic checks and a short shared lock."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from memory_graph_lib import content_hash, graph_lock, parse_markdown, write_text_atomic
from rebuild_indexes import rebuild


FOLDERS = {"01_项目卡片", "02_赛道地图", "03_技术主题", "04_估值锚点", "05_事件卡片", "06_人物卡片"}


def target_path(memory: Path, relative: str) -> Path:
    path = (memory / relative).resolve()
    if (not path.is_relative_to(memory.resolve()) or len(Path(relative).parts) != 2
            or Path(relative).parts[0] not in FOLDERS or path.suffix != ".md"):
        raise ValueError(f"not a graph Markdown object: {relative}")
    return path


def apply_batch(workspace: Path, memory: Path, changes: list[dict], dry_run: bool = False) -> int:
    workspace, memory = workspace.resolve(), memory.resolve()
    # Research stays parallel; only the read-check-write-index phase is locked.
    with graph_lock(memory):
        prepared = {}
        for change in changes:
            path = target_path(memory, change["path"])
            if path in prepared:
                raise ValueError(f"duplicate target: {path}")
            if "expected_sha256" not in change:
                raise ValueError("expected_sha256 is required; null means a new object")
            if content_hash(path) != change["expected_sha256"]:
                raise ValueError(f"conflict: reread and merge {path}; nothing was written")
            content = Path(change["content_file"]).read_text(encoding="utf-8")
            if not content.startswith("# ") or not content.strip():
                raise ValueError(f"invalid Markdown object: {path}")
            if path.parent.name == "01_项目卡片":
                fields = parse_markdown(Path(change["content_file"]))["fields"]
                state_ref = fields.get("状态文件", "")
                state_path = (workspace / state_ref).resolve()
                if not state_ref or not state_path.is_relative_to(workspace) or not state_path.is_file():
                    raise ValueError(f"project card needs a valid local state: {path}")
                state = json.loads(state_path.read_text(encoding="utf-8"))
                for key, label in (("project_id", "项目 ID"), ("project_status", "项目状态"),
                                   ("judgment_display", "当前投资判断"), ("updated_at", "最近更新")):
                    if str(state.get(key, "")) != fields.get(label, ""):
                        raise ValueError(f"project header conflicts with formal state: {path}: {label}")
            prepared[path] = (path.read_text(encoding="utf-8") if path.exists() else None, content)
        changed = {p: pair for p, pair in prepared.items() if pair[0] != pair[1]}
        if dry_run or not changed:
            return len(changed)
        try:
            for path, (_, content) in changed.items():
                write_text_atomic(path, content)
            rebuild(workspace, memory)
        except Exception:
            for path, (before, _) in changed.items():
                if before is None:
                    path.unlink(missing_ok=True)
                else:
                    write_text_atomic(path, before)
            rebuild(workspace, memory)
            raise
        return len(changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--snapshot", nargs="+", metavar="RELATIVE_PATH")
    group.add_argument("--plan", help="JSON with changes: path, expected_sha256, content_file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    workspace = Path(args.workspace_root).expanduser().resolve()
    memory = Path(args.memory_root).expanduser().resolve() if args.memory_root else workspace / "Memory Graph"
    if args.snapshot:
        with graph_lock(memory):
            print(json.dumps([{"path": p, "expected_sha256": content_hash(target_path(memory, p))}
                              for p in args.snapshot], ensure_ascii=False, indent=2))
    else:
        changes = json.loads(Path(args.plan).read_text(encoding="utf-8"))["changes"]
        count = apply_batch(workspace, memory, changes, args.dry_run)
        print(f"{'Would update' if args.dry_run else 'Updated'} {count} graph objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
