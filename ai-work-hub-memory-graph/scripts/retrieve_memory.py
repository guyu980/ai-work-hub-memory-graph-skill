#!/usr/bin/env python3
"""Retrieve bounded source-backed matches without adding a second knowledge store."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from memory_graph_lib import read_jsonl, write_json_atomic


GROUPS = {
    "projects": ("项目索引.jsonl", "01_项目卡片", "project"),
    "sectors": ("赛道索引.jsonl", "02_赛道地图", "sector"),
    "technical_themes": ("技术主题索引.jsonl", "03_技术主题", "technical_theme"),
    "valuation_anchors": ("估值索引.jsonl", "04_估值锚点", "valuation_anchor"),
    "events": ("事件索引.jsonl", "05_事件卡片", "event"),
    "people": ("人物索引.jsonl", "06_人物卡片", "person"),
}
SKIP_DIRS = {"工作区", "原始资料", "解析文本", "node_modules", "templates"}


def tokens(value: str) -> set[str]:
    latin = re.findall(r"[a-z0-9_.+-]{2,}", value.lower())
    chinese = re.findall(r"[\u3400-\u9fff]{2,}", value)
    grams = [part for phrase in chinese for part in (
        [phrase] + [phrase[i:i + 2] for i in range(len(phrase) - 1)]
    )]
    return set(latin + grams)


def score(record: dict[str, Any], query_tokens: set[str]) -> int:
    weights = {
        "name": 10, "title": 10, "aliases": 8, "tags": 5,
        "primary_sector": 5, "sector": 5, "summary": 3,
        "key_variables": 3, "validation_signals": 3, "strong_signals": 3,
        "related_projects": 4, "counterexamples": 4,
    }
    return sum(
        len(query_tokens & tokens(json.dumps(record.get(field, ""), ensure_ascii=False))) * weight
        for field, weight in weights.items()
    )


def source_text(root: Path, relative: str) -> str:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def excerpt(body: str, query_tokens: set[str]) -> tuple[int, str]:
    lines = body.splitlines()
    if not lines:
        return 0, ""
    index = max(range(len(lines)), key=lambda i: len(tokens(lines[i]) & query_tokens))
    line = lines[index]
    # Center long source lines on a matching term rather than losing a late match.
    matches = [m.start() for term in query_tokens
               for m in re.finditer(re.escape(term), line, re.IGNORECASE)]
    start = max(0, min(matches, default=0) - 100)
    return index + 1, line[start:start + 480]


def select(records: list[dict[str, Any]], query_tokens: set[str], limit: int) -> list[dict[str, Any]]:
    ranked = []
    for record in records:
        body = record.get("_body", "")
        overlap = query_tokens & tokens(body)
        value = score(record, query_tokens) + 2 * len(overlap)
        if not value:
            continue
        result = {key: item for key, item in record.items() if not key.startswith("_")}
        if overlap:
            result["match_line"], result["match_excerpt"] = excerpt(body, query_tokens)
        ranked.append({"retrieval_score": value, **result})
    ranked.sort(key=lambda item: str(item.get("source_path", "")))
    ranked.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    ranked.sort(key=lambda item: item["retrieval_score"], reverse=True)
    return ranked[:limit]


def graph_records(memory_root: Path) -> dict[str, list[dict[str, Any]]]:
    groups = {}
    for group, (index_name, folder, kind) in GROUPS.items():
        records = read_jsonl(memory_root / "00_索引" / index_name)
        by_path = {record.get("source_path", ""): dict(record) for record in records}
        for path in sorted((memory_root / folder).glob("*.md")):
            relative = path.relative_to(memory_root).as_posix()
            by_path.setdefault(relative, {"type": kind, "title": path.stem, "source_path": relative})
        for relative, record in by_path.items():
            record["source_scope"] = "memory_root"
            record["_body"] = source_text(memory_root, relative)
        groups[group] = list(by_path.values())
    return groups


def workspace_notes(workspace: Path, patterns: list[str], kind: str) -> list[dict[str, Any]]:
    records = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(workspace.glob(pattern)):
            relative = path.relative_to(workspace)
            if path in seen or SKIP_DIRS.intersection(relative.parts):
                continue
            seen.add(path)
            body = source_text(workspace, relative.as_posix())
            if not body:
                continue
            title = next((line.lstrip("# ").strip() for line in body.splitlines()
                          if line.startswith("# ")), path.stem)
            records.append({
                "type": kind, "title": title, "source_path": relative.as_posix(),
                "source_scope": "workspace_root", "_body": body,
            })
    return records


def one_hop(groups: dict[str, list[dict[str, Any]]], selected: dict[str, Any],
            relations: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    lookup = {}
    selected_ids = set()
    for group, records in groups.items():
        chosen_paths = {item["source_path"] for item in selected[group]}
        for record in records:
            for key, value in record.items():
                if key.endswith("_id") and isinstance(value, str):
                    lookup[value] = record
                    if record.get("source_path") in chosen_paths:
                        selected_ids.add(value)
    neighbors = []
    seen = set()
    # Exactly one hop from direct matches; neighbor discoveries never expand the seeds.
    for relation in relations:
        left, right = relation.get("from_id"), relation.get("to_id")
        if left in selected_ids:
            seed, target = left, right
        elif right in selected_ids:
            seed, target = right, left
        else:
            continue
        if target in selected_ids or target in seen or target not in lookup:
            continue
        seen.add(target)
        record = {key: value for key, value in lookup[target].items() if not key.startswith("_")}
        neighbors.append({
            "via_id": seed, "relation_type": relation.get("relation_type"),
            "relation_source_path": relation.get("source_path"), "record": record,
        })
        if len(neighbors) >= limit:
            break
    return neighbors


def retrieve(workspace: Path, memory_root: Path, query: str, limit: int) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be positive")
    query_tokens = tokens(query)
    groups = graph_records(memory_root)
    selected = {group: select(records, query_tokens, limit) for group, records in groups.items()}
    selected["knowledge_sources"] = select(workspace_notes(
        workspace, ["知识来源/**/*核心整理.md"], "knowledge_source"), query_tokens, limit)
    selected["research_reports"] = select(workspace_notes(
        workspace, [
            "行业研究/*/输出文档/**/*.md",
            "项目/*/输出文档/03_研究与分析/**/*.md",
            "项目/归档/*/输出文档/03_研究与分析/**/*.md",
        ], "research_report"), query_tokens, limit)
    selected["related"] = one_hop(groups, selected, read_jsonl(
        memory_root / "00_索引" / "关系索引.jsonl"), limit)
    return {"schema_version": 2, "query": query, **selected}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    workspace = Path(args.workspace_root).expanduser().resolve()
    memory_root = Path(args.memory_root).expanduser().resolve() if args.memory_root else workspace / "Memory Graph"
    result = retrieve(workspace, memory_root, args.query, args.limit)
    if args.output:
        output = Path(args.output).expanduser()
        write_json_atomic(output, result)
        print(f"Wrote retrieval result: {output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
