#!/usr/bin/env python3
"""Build a deterministic, compact retrieval pack for a diligence question."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from memory_graph_lib import read_jsonl, write_json_atomic


def tokens(value: str) -> set[str]:
    latin = re.findall(r"[a-z0-9_.+-]{2,}", value.lower())
    chinese = re.findall(r"[\u3400-\u9fff]{2,}", value)
    grams: list[str] = []
    for phrase in chinese:
        grams.append(phrase)
        grams.extend(phrase[index : index + 2] for index in range(len(phrase) - 1))
    return set([*latin, *grams])


def score(record: dict[str, Any], query_tokens: set[str]) -> int:
    weights = {
        "name": 10,
        "title": 10,
        "aliases": 8,
        "tags": 5,
        "primary_sector": 5,
        "sector": 5,
        "summary": 3,
        "thesis": 3,
        "related_projects": 4,
        "counterexamples": 4,
    }
    total = 0
    for field, weight in weights.items():
        value = record.get(field, "")
        rendered = json.dumps(value, ensure_ascii=False)
        overlap = query_tokens & tokens(rendered)
        total += len(overlap) * weight
    return total


def select(
    records: list[dict[str, Any]],
    query_tokens: set[str],
    limit: int,
) -> list[dict[str, Any]]:
    ranked = [
        (score(record, query_tokens), record)
        for record in records
    ]
    ranked.sort(
        key=lambda item: str(
            item[1].get("name") or item[1].get("title") or ""
        )
    )
    ranked.sort(
        key=lambda item: str(item[1].get("updated_at", "")),
        reverse=True,
    )
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        {"retrieval_score": value, **record}
        for value, record in ranked[:limit]
        if value > 0
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output")
    args = parser.parse_args()
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else workspace_root / "Memory Graph"
    )
    query_tokens = tokens(args.query)
    index_dir = memory_root / "00_索引"
    pack = {
        "schema_version": 2,
        "query": args.query,
        "projects": select(
            read_jsonl(index_dir / "项目索引.jsonl"),
            query_tokens,
            args.limit,
        ),
        "theses": select(
            read_jsonl(index_dir / "观点索引.jsonl"),
            query_tokens,
            args.limit,
        ),
        "events": select(
            read_jsonl(index_dir / "事件索引.jsonl"),
            query_tokens,
            min(args.limit, 3),
        ),
        "people": select(
            read_jsonl(index_dir / "人物索引.jsonl"),
            query_tokens,
            min(args.limit, 3),
        ),
        "valuation_anchors": select(
            read_jsonl(index_dir / "估值索引.jsonl"),
            query_tokens,
            2,
        ),
    }
    if args.output:
        output = Path(args.output).expanduser()
        write_json_atomic(output, pack)
        print(f"Wrote context pack: {output}")
    else:
        print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
