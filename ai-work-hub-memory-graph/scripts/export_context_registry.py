#!/usr/bin/env python3
"""Export a local Memory Graph as a portable Context Registry delta."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any
from urllib.parse import urlparse

from memory_graph_lib import read_jsonl, write_json_atomic


INDEXES = [
    ("项目索引.jsonl", "project"),
    ("事件索引.jsonl", "event"),
    ("人物索引.jsonl", "person"),
    ("观点索引.jsonl", "thesis"),
    ("估值索引.jsonl", "resource"),
]
LOCATOR_BACKENDS = {"local", "feishu", "web", "other"}
LOCATOR_KINDS = {"file", "folder", "document", "base_record", "url"}
LOCATOR_FIELDS = {
    "backend", "kind", "uri", "display_path", "content_hash",
    "last_verified_at"
}


def relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"portable local locator is outside workspace: {path}"
        ) from exc


def locator(
    path: Path,
    root: Path,
    kind: str | None = None,
) -> dict[str, str]:
    return {
        "backend": "local",
        "kind": kind or ("folder" if path.is_dir() else "file"),
        "uri": relative(path, root),
    }


def source_ref_locator(value: str, workspace_root: Path) -> dict[str, str]:
    if PureWindowsPath(value).is_absolute():
        raise ValueError(
            "Windows absolute source references are not portable"
        )
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        hostname = (parsed.hostname or "").lower()
        is_feishu = hostname.endswith((
            ".feishu.cn", ".larksuite.com", ".larkoffice.com"
        ))
        path_parts = {part for part in parsed.path.split("/") if part}
        kind = (
            "document"
            if is_feishu and path_parts.intersection({"doc", "docs", "docx"})
            else "url"
        )
        return {
            "backend": "feishu" if is_feishu else "web",
            "kind": kind,
            "uri": value,
        }
    if parsed.scheme:
        if parsed.scheme == "file":
            raise ValueError("file:// source references are not portable")
        return {"backend": "other", "kind": "url", "uri": value}
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = workspace_root / path
    return locator(path, workspace_root)


def normalize_locator(
    value: dict[str, Any],
    workspace_root: Path,
) -> dict[str, Any]:
    normalized = dict(value)
    unknown = set(normalized) - LOCATOR_FIELDS
    if unknown:
        raise ValueError(
            "locator has unsupported field(s): " + ", ".join(sorted(unknown))
        )
    if normalized.get("backend") not in LOCATOR_BACKENDS:
        raise ValueError("locator backend is invalid")
    if normalized.get("kind") not in LOCATOR_KINDS:
        raise ValueError("locator kind is invalid")
    if not str(normalized.get("uri") or "").strip():
        raise ValueError("locator uri is required")
    if normalized.get("backend") == "local":
        uri = str(normalized.get("uri") or "")
        if PureWindowsPath(uri).is_absolute():
            raise ValueError("Windows absolute local locators are not portable")
        path = Path(uri).expanduser()
        if path.is_absolute():
            normalized["uri"] = relative(path, workspace_root)
    return normalized


def first(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def stable_id(context_type: str, title: str, record: dict[str, Any]) -> str:
    explicit = first(
        record, "project_id", "event_id", "person_id", "thesis_id",
        "valuation_id", "context_id"
    )
    if explicit:
        return explicit
    digest = hashlib.sha256(
        f"{context_type}:{title}".encode("utf-8")
    ).hexdigest()[:16]
    return f"context:{context_type}:{digest}"


def record_artifact_path(
    record: dict[str, Any],
    workspace_root: Path,
    memory_root: Path,
) -> Path:
    source_path = first(record, "source_path")
    if source_path:
        path = Path(source_path).expanduser()
        return path if path.is_absolute() else memory_root / path
    state_path = first(record, "state_path")
    if state_path:
        path = Path(state_path).expanduser()
        return path if path.is_absolute() else workspace_root / path
    return memory_root


def record_object_root(
    record: dict[str, Any],
    context_type: str,
    workspace_root: Path,
    memory_root: Path,
) -> Path:
    if context_type != "project":
        return memory_root
    for key in ("state_path", "evidence_ledger_path"):
        value = first(record, key)
        if not value:
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = workspace_root / path
        for parent in path.parents:
            if parent.name in {"原始资料", "解析文本", "输出文档"}:
                return parent.parent
    return memory_root


def record_to_context(
    record: dict[str, Any],
    context_type: str,
    workspace_root: Path,
    memory_root: Path,
    visibility: str,
) -> dict[str, Any]:
    title = first(record, "name", "title", "person", "thesis", "sector")
    if not title:
        raise ValueError(f"{context_type} index record has no title")
    artifact_path = record_artifact_path(
        record, workspace_root, memory_root
    )
    object_root = record_object_root(
        record, context_type, workspace_root, memory_root
    )
    source_refs = record.get("source_refs") or []
    if not isinstance(source_refs, list):
        source_refs = [source_refs]
    normalized_refs: list[Any] = []
    for value in source_refs:
        if isinstance(value, dict):
            normalized_refs.append(normalize_locator(value, workspace_root))
        elif str(value).strip():
            normalized_refs.append(source_ref_locator(
                str(value).strip(), workspace_root
            ))
    if not normalized_refs and artifact_path != memory_root:
        normalized_refs.append(locator(artifact_path, workspace_root))

    relations = []
    for relation_type, field in (
        ("comparable_to", "related_projects"),
        ("counterexample_of", "counterexamples"),
    ):
        values = record.get(field) or []
        if not isinstance(values, list):
            values = [values]
        relations.extend(
            {"relation_type": relation_type, "target": str(value).strip()}
            for value in values if str(value).strip()
        )

    tags = record.get("tags") or []
    if not isinstance(tags, list):
        tags = [tags]
    context = {
        "schema_version": "context-record/v1",
        "context_id": stable_id(context_type, title, record),
        "context_type": context_type,
        "title": title,
        "summary": first(record, "summary", "judgment_display", "current_view"),
        "primary_sector": first(record, "primary_sector", "sector"),
        "tags": [str(tag) for tag in tags if str(tag).strip()],
        "relations": relations,
        "source_refs": normalized_refs,
        "object_root": locator(object_root, workspace_root, kind="folder"),
        "current_artifact": locator(artifact_path, workspace_root),
        "status": first(record, "status", "project_status") or "current",
        "visibility": visibility,
        "version": str(record.get("schema_version") or 2),
    }
    last_verified_at = first(
        record, "last_verified_at", "updated_at", "date"
    )
    if last_verified_at:
        context["last_verified_at"] = last_verified_at
    return context


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--memory-root")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--visibility",
        default="restricted",
        choices=["organization", "organization_core", "project_team", "restricted"],
    )
    parser.add_argument("--actor-id", default="codex")
    parser.add_argument("--runtime", default="codex")
    parser.add_argument("--runtime-version", default="current")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    memory_root = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root else workspace_root / "Memory Graph"
    )
    try:
        memory_root.relative_to(workspace_root)
    except ValueError:
        parser.error("--memory-root must be inside --workspace-root for export")
    index_root = memory_root / "00_索引"
    records: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    digest = hashlib.sha256()

    for filename, context_type in INDEXES:
        path = index_root / filename
        if not path.exists():
            continue
        digest.update(filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
        artifacts.append({
            "artifact_id": f"artifact:memory-graph:{path.stem}",
            "collection": "structured_context",
            "title": path.stem,
            "locator": locator(path, workspace_root),
        })
        for raw in read_jsonl(path):
            records.append(record_to_context(
                raw, context_type, workspace_root, memory_root, args.visibility
            ))

    digest.update(args.visibility.encode("utf-8"))
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    package = {
        "schema_version": "context-package/v1",
        "package_id": f"pkg-memory-graph-{digest.hexdigest()[:16]}",
        "package_type": "graph_delta",
        "created_at": now,
        "created_by": {
            "actor_type": "agent",
            "actor_id": args.actor_id,
            "runtime": args.runtime,
            "runtime_version": args.runtime_version,
        },
        "visibility": args.visibility,
        "object": {
            "object_id": "workflow:ai-work-hub-memory-graph",
            "object_type": "workflow",
            "title": "AI Work Hub Memory Graph",
            "object_root": locator(memory_root, workspace_root),
        },
        "trigger": {
            "trigger_type": "context_registry_export",
            "summary": "Export local Memory Graph records for adapter upsert",
            "occurred_at": now,
        },
        "source_refs": [locator(memory_root, workspace_root)],
        "artifacts": artifacts,
        "graph_delta": {
            "schema_version": "context-registry-delta/v1",
            "records": records,
        },
        "workflow_outputs": [{
            "workflow_id": "workflow:ai-work-hub-memory-graph",
            "workflow_version": "current-main",
            "summary": f"Exported {len(records)} Context Registry record(s)",
            "artifact_refs": [item["artifact_id"] for item in artifacts],
        }],
        "writeback": {
            "requested_operation": "upsert_context_registry_records"
        },
    }
    output = Path(args.output).expanduser().resolve()
    write_json_atomic(output, package)
    print(f"Wrote Context Registry package: {output}")
    print(f"Records: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
