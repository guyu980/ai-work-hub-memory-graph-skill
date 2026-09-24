#!/usr/bin/env python3
"""Retrieve bounded source-backed matches without adding a second knowledge store."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from memory_graph_lib import content_date, graph_lock, parse_markdown, read_jsonl, write_json_atomic
from rebuild_indexes import stable_id


GROUPS = {
    "projects": ("项目索引.jsonl", "01_项目卡片", "project"),
    "sectors": ("赛道索引.jsonl", "02_赛道地图", "sector"),
    "technical_themes": ("技术主题索引.jsonl", "03_技术主题", "technical_theme"),
    "valuation_anchors": ("估值索引.jsonl", "04_估值锚点", "valuation_anchor"),
    "events": ("事件索引.jsonl", "05_事件卡片", "event"),
    "people": ("人物索引.jsonl", "06_人物卡片", "person"),
}
SKIP_DIRS = {"工作区", "原始资料", "解析文本", "node_modules", "templates"}
STOP_WORDS = {"ai", "公司", "项目", "技术", "产品", "模型", "行业", "相关", "分析", "研究", "判断", "我们", "这个", "如何", "什么", "创始人", "创始", "始人", "团队", "估值"}


def tokens(value: str) -> set[str]:
    latin = re.findall(r"[a-z0-9_.+-]{2,}", value.lower())
    chinese = [p for p in re.findall(r"[\u3400-\u9fff]{2,}", value) if p not in STOP_WORDS]
    grams = [part for phrase in chinese for part in (
        [phrase] + [phrase[i:i + 2] for i in range(len(phrase) - 1)]
    )]
    return set(latin + grams) - STOP_WORDS


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


def select(records: list[dict[str, Any]], query_tokens: set[str], limit: int,
           weights: dict[str, float] | None = None) -> list[dict[str, Any]]:
    ranked = []
    for record in records:
        body = record.get("_body", "")
        overlap = query_tokens & tokens(body)
        identity = tokens(" ".join(str(record.get(k, "")) for k in ("name", "title", "aliases")))
        matched = overlap | (query_tokens & identity)
        if not matched or (len(query_tokens) > 3 and len(matched) < 2 and not (query_tokens & identity)):
            continue
        value = score(record, query_tokens) + sum((weights or {}).get(t, 1) * 2 for t in matched)
        value *= 0.5 + len(matched) / max(len(query_tokens), 1)
        entity_terms = set(record.get("_entity_terms", []))
        if entity_terms:
            identity_text = " ".join(str(record.get(k, "")) for k in ("name", "title", "aliases")).lower()
            if any(term in identity_text for term in entity_terms):
                value += 80 if record.get("type") in {"project", "project_judgment"} else 20
            elif not any(term in body.lower() for term in entity_terms):
                value *= 0.35
        result = {key: item for key, item in record.items() if not key.startswith("_")}
        if overlap:
            result["match_line"], result["match_excerpt"] = excerpt(body, query_tokens)
            if record.get("type") == "radar_candidate":
                result.pop("match_line", None)
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
            path = (memory_root / relative).resolve()
            if path.is_relative_to(memory_root.resolve()) and path.is_file():
                parsed = parse_markdown(path)
                record["updated_at"] = content_date(parsed)
                current = next((parsed["sections"][s] for s in ("一句话", "当前判断", "当前理解", "适用边界", "当前影响")
                                if parsed["sections"].get(s)), "")
                if current:
                    record["summary"] = current[:700]
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
                "updated_at": content_date(parse_markdown(path)),
            })
            if kind == "knowledge_source":
                records[-1]["source_id"] = stable_id("source", relative.as_posix())
    return records


def one_hop(groups: dict[str, list[dict[str, Any]]], selected: dict[str, Any],
            relations: list[dict[str, Any]], limit: int, query_tokens: set[str] | None = None) -> list[dict[str, Any]]:
    lookup = {}
    selected_ids = set()
    direct_ids = set()
    seed_scores = {}
    cutoff = max((item.get("retrieval_score", 0) for g in GROUPS for item in selected.get(g, [])), default=0) * 0.6
    for group, records in groups.items():
        all_chosen_paths = {item["source_path"] for item in selected[group]}
        chosen_paths = {item["source_path"]: item.get("retrieval_score", 0) for item in selected[group]
                        if item.get("retrieval_score", 0) >= cutoff}
        for record in records:
            for key, value in record.items():
                if key.endswith("_id") and isinstance(value, str):
                    lookup[value] = record
                    if record.get("source_path") in all_chosen_paths:
                        direct_ids.add(value)
                    if record.get("source_path") in chosen_paths:
                        selected_ids.add(value)
                        seed_scores[value] = chosen_paths[record["source_path"]]
    neighbors = []
    # Exactly one hop from direct matches; neighbor discoveries never expand the seeds.
    for relation in relations:
        left, right = relation.get("from_id"), relation.get("to_id")
        if left in selected_ids:
            seed, target = left, right
        elif right in selected_ids:
            seed, target = right, left
        else:
            continue
        if target in direct_ids or target not in lookup:
            continue
        record = {key: value for key, value in lookup[target].items() if not key.startswith("_")}
        relevance = score(record, query_tokens or set())
        if lookup[seed].get("type") in {"sector", "valuation_anchor"} and relevance < 15:
            continue
        neighbors.append({
            "via_id": seed, "relation_type": relation.get("relation_type"),
            "relation_source_path": relation.get("source_path"), "record": record,
            "context": relation.get("context", ""),
            "relevance": relevance + seed_scores.get(seed, 0) * 0.1,
        })
    neighbors.sort(key=lambda item: (-item["relevance"], item["record"].get("source_path", "")))
    unique = {}
    for item in neighbors:
        unique.setdefault(item["record"].get("source_path"), item)
    return list(unique.values())[:limit]


def radar_candidates(workspace: Path) -> list[dict[str, Any]]:
    records = {}
    for path in sorted(workspace.glob("自动化归档/**/*projects.json"), reverse=True):
        if SKIP_DIRS.intersection(path.relative_to(workspace).parts):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        projects = payload.get("projects", []) if isinstance(payload, dict) else payload
        for item in projects:
            if not isinstance(item, dict):
                continue
            name = str(item.get("repo") or item.get("repository") or item.get("name") or "")
            if not name or name in records:
                continue
            records[name] = {"type": "radar_candidate", "title": name, "entry_key": name,
                             "source_path": path.relative_to(workspace).as_posix(), "source_scope": "workspace_root",
                             "_body": json.dumps(item, ensure_ascii=False, indent=2),
                             "updated_at": str(payload.get("generated_at", ""))[:10] if isinstance(payload, dict) else ""}
    return list(records.values())


def retrieve(workspace: Path, memory_root: Path, query: str, limit: int) -> dict[str, Any]:
    workspace, memory_root = workspace.resolve(), memory_root.resolve()
    if limit < 1:
        raise ValueError("limit must be positive")
    query_tokens = tokens(query)
    if not query_tokens:
        return {"schema_version": 2, "query": query, **{g: [] for g in GROUPS},
                "knowledge_sources": [], "research_reports": [], "project_judgments": [], "radar_candidates": [], "related": []}
    groups = graph_records(memory_root)
    groups["knowledge_sources"] = workspace_notes(
        workspace, ["知识来源/**/*核心整理.md"], "knowledge_source")
    groups["research_reports"] = workspace_notes(
        workspace, [
            "行业研究/*/输出文档/**/*.md",
            "项目/*/输出文档/03_研究与分析/**/*.md",
            "项目/归档/*/输出文档/03_研究与分析/**/*.md",
        ], "research_report")
    groups["project_judgments"] = workspace_notes(workspace, [
        "项目/*/输出文档/*项目判断与todo.md", "项目/归档/*/输出文档/*项目判断与todo.md",
        "基金/输出文档/**/*.md", "基金/*/输出文档/**/*.md"], "project_judgment")
    groups["radar_candidates"] = radar_candidates(workspace)
    phrases = [p.lower() for p in re.findall(r"[a-zA-Z0-9_.+-]{2,}|[\u3400-\u9fff]{2,}", query) if p.lower() not in STOP_WORDS]
    entity_terms = {term for term in phrases for r in groups["projects"]
                    for name in [r.get("name", ""), *r.get("aliases", [])]
                    if str(name).lower().startswith(term)}
    for records in groups.values():
        for record in records:
            record["_entity_terms"] = list(entity_terms)
    corpus = [tokens(r.get("_body", "")) for records in groups.values() for r in records]
    weights = {t: math.log(1 + len(corpus) / (1 + sum(t in d for d in corpus))) for t in query_tokens}
    selected = {group: select(records, query_tokens, limit, weights) for group, records in groups.items()}
    ranked = sorted([(item["retrieval_score"], group, i) for group, records in selected.items()
                     for i, item in enumerate(records)], reverse=True)[:limit]
    keep = {(group, i) for _, group, i in ranked}
    selected = {group: [r for i, r in enumerate(records) if (group, i) in keep] for group, records in selected.items()}
    selected["related"] = one_hop(groups, selected, read_jsonl(
        memory_root / "00_索引" / "关系索引.jsonl"), min(limit, 5), query_tokens)
    return {"schema_version": 2, "query": query, "limit_scope": "total_direct_matches", **selected}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=8, help="Total direct matches across all kinds")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    workspace = Path(args.workspace_root).expanduser().resolve()
    memory_root = Path(args.memory_root).expanduser().resolve() if args.memory_root else workspace / "Memory Graph"
    with graph_lock(memory_root):
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
