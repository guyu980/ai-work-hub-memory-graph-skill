#!/usr/bin/env python3
"""Shared helpers for AI Work Hub Memory Graph v2 tooling."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "primary_sectors": [
        "AI基础设施与开发者工具",
        "AI原生应用与工作流",
        "具身智能与机器人",
        "AI硬件与边缘智能",
        "半导体与硬件基础设施",
        "基础模型与前沿技术",
        "观察与非核心机会",
    ],
    "project_statuses": ["active", "archived"],
    "intake_modes": ["live", "historical_review"],
    "historical_outcomes": [
        "not_applicable",
        "invested",
        "pass",
        "unknown",
    ],
    "review_statuses": [
        "not_applicable",
        "pending",
        "in_progress",
        "reviewed",
        "refresh_due",
    ],
    "process_stages": [
        "screening",
        "diligence",
        "ic",
        "closing",
        "monitoring",
        "archived",
    ],
    "investment_decisions": [
        "invest",
        "continue",
        "pause",
        "pass",
        "observe",
        "invested",
    ],
    "recommended_plays": [
        "lead",
        "co_lead",
        "follow",
        "small_option",
        "none",
        "tbd",
    ],
    "position_sizes": ["standard", "small", "symbolic", "tbd"],
    "price_views": [
        "cheap",
        "reasonable",
        "expensive",
        "unacceptable",
        "unknown",
    ],
    "confidence_levels": ["low", "medium", "high"],
    "evidence_tiers": [
        "contract_or_original",
        "customer_confirmed",
        "public_verified",
        "company_claim",
        "inference",
        "legacy_migrated",
    ],
    "evidence_statuses": [
        "confirmed",
        "partial",
        "unverified",
        "disputed",
        "stale",
        "superseded",
    ],
    "decision_impacts": ["high", "medium", "low"],
    "evidence_temporal_scopes": [
        "decision_time",
        "post_outcome",
        "current",
        "unknown",
    ],
    "relation_types": [
        "comparable_to",
        "counterexample_of",
        "linked_person",
        "affected_by",
        "uses_valuation_anchor",
    ],
}


HEADER_LABELS = {
    "schema_version": "Schema Version",
    "project_id": "项目 ID",
    "created_at": "创建日期",
    "updated_at": "最近更新",
    "last_synced_at": "最近同步",
    "primary_sector": "主赛道",
    "tags": "标签",
    "aliases": "别名",
    "intake_mode": "资料模式",
    "historical_outcome": "历史结果",
    "review_status": "复盘状态",
    "historical_decision_date": "历史决策日期",
    "review_as_of": "复盘基准日",
    "project_status": "项目状态",
    "process_stage": "流程阶段",
    "investment_decision": "投资判断",
    "recommended_play": "建议打法",
    "position_size": "仓位",
    "price_view": "价格判断",
    "confidence": "判断置信度",
    "judgment_display": "当前投资判断",
    "stage": "融资阶段",
    "valuation": "估值摘要",
    "state_path": "状态文件",
    "evidence_ledger_path": "证据账本",
    "source_refs": "资料来源",
    "source_hash": "同步哈希",
    "evidence_backfill_status": "证据回填状态",
}


def load_config(memory_root: Path) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config_path = memory_root / "config" / "schema-v2.json"
    if config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        config.update(loaded)
    return config


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        records.append(value)
    return records


def write_jsonl_atomic(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        for record in records
    ]
    content = "\n".join(lines)
    if content:
        content += "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = re.sub(r"[\s_/]+", "-", normalized)
    normalized = re.sub(r"[^\w\-\u3400-\u9fff.]+", "", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-.")
    return normalized or "unnamed"


def split_csv(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    stripped = value.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [
        item.strip()
        for item in re.split(r"[,，;；]", stripped)
        if item.strip()
    ]


def parse_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = ""
    fields: dict[str, str] = {}
    sections: dict[str, str] = {}
    current_section: str | None = None
    section_lines: list[str] = []

    for line in lines:
        if not title and line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current_section is not None:
                sections[current_section] = "\n".join(section_lines).strip()
            current_section = line[3:].strip()
            section_lines = []
            continue
        if current_section is None:
            match = re.match(r"^-\s+([^:：]+)[:：]\s*(.*)$", line)
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        else:
            section_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(section_lines).strip()

    return {
        "title": title,
        "fields": fields,
        "sections": sections,
        "text": text,
    }


def first_paragraph(text: str) -> str:
    paragraphs = [
        re.sub(r"\s+", " ", part).strip()
        for part in re.split(r"\n\s*\n", text.strip())
        if part.strip()
    ]
    return paragraphs[0] if paragraphs else ""


def section_entities(text: str) -> list[str]:
    entities: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        value = re.split(r"[:：]", value, maxsplit=1)[0].strip()
        if value and value not in entities:
            entities.append(value)
    return entities


def file_hash(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    found = False
    for path in sorted(set(paths), key=lambda item: str(item)):
        if not path.exists() or not path.is_file():
            continue
        found = True
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16] if found else ""


def resolve_workspace_path(workspace_root: Path, value: str) -> Path | None:
    stripped = value.strip()
    if not stripped:
        return None
    candidate = Path(stripped).expanduser()
    if candidate.is_absolute():
        return candidate
    return workspace_root / candidate


def find_project_dir(
    workspace_root: Path,
    name: str,
    aliases: list[str],
    overrides: dict[str, str] | None = None,
) -> Path | None:
    overrides = overrides or {}
    override = overrides.get(name)
    if override:
        candidate = resolve_workspace_path(workspace_root, override)
        if candidate and candidate.is_dir():
            return candidate

    candidates = [name, *aliases]
    roots = [workspace_root / "项目", workspace_root / "项目" / "归档"]
    for root in roots:
        for candidate_name in candidates:
            candidate = root / candidate_name
            if candidate.is_dir():
                return candidate

    normalized_names = {slugify(item) for item in candidates if item}
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.is_dir() and slugify(child.name) in normalized_names:
                return child
    return None


def infer_state(
    legacy_status: str,
    judgment_display: str,
) -> dict[str, str]:
    combined = f"{legacy_status} {judgment_display}".lower()

    project_status = "archived" if any(
        token in combined for token in ["archived", "归档", "passed"]
    ) else "active"

    if project_status == "archived":
        process_stage = "archived"
    elif any(token in combined for token in ["watch", "已投", "invested"]):
        process_stage = "monitoring"
    elif "ic" in combined:
        process_stage = "ic"
    else:
        process_stage = "diligence"

    if any(token in combined for token in ["不投", "pass"]):
        investment_decision = "pass"
    elif "暂缓" in combined:
        investment_decision = "pause"
    elif any(token in combined for token in ["已投", "invested"]):
        investment_decision = "invested"
    elif (
        "建议投" in judgment_display
        or re.search(r"(^|[；;，,\s])投([；;，,\s]|$)", judgment_display)
    ):
        investment_decision = "invest"
    elif any(token in combined for token in ["继续推进", "条件推进"]):
        investment_decision = "continue"
    else:
        investment_decision = "observe"

    if any(token in combined for token in ["小额 option", "小额option", "symbolic"]):
        recommended_play = "small_option"
        position_size = "small"
    elif "共同领投" in combined:
        recommended_play = "co_lead"
        position_size = "standard"
    elif "领投" in combined and "不领投" not in combined:
        recommended_play = "lead"
        position_size = "standard"
    elif "跟投" in combined:
        recommended_play = "follow"
        position_size = (
            "small"
            if any(token in combined for token in ["小仓位", "小额"])
            else "tbd"
        )
    elif investment_decision in {"pass", "pause", "observe", "invested"}:
        recommended_play = "none"
        position_size = "tbd"
    else:
        recommended_play = "tbd"
        position_size = "tbd"

    if any(token in combined for token in ["明显过贵", "现价不投", "不追"]):
        price_view = "unacceptable"
    elif any(token in combined for token in ["偏贵", "价格贵"]):
        price_view = "expensive"
    elif any(token in combined for token in ["合理", "可接受", "以内可投"]):
        price_view = "reasonable"
    elif "便宜" in combined:
        price_view = "cheap"
    else:
        price_view = "unknown"

    return {
        "project_status": project_status,
        "process_stage": process_stage,
        "investment_decision": investment_decision,
        "recommended_play": recommended_play,
        "position_size": position_size,
        "price_view": price_view,
        "confidence": "medium",
    }


def state_to_card_fields(state: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for key, label in HEADER_LABELS.items():
        value = state.get(key)
        if value is None:
            continue
        if isinstance(value, list):
            values[label] = json.dumps(value, ensure_ascii=False)
        else:
            values[label] = str(value)
    return values


def replace_card_header(
    text: str,
    ordered_fields: list[tuple[str, str]],
) -> str:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("project card must start with a level-one title")

    first_section = next(
        (index for index, line in enumerate(lines) if line.startswith("## ")),
        len(lines),
    )
    body = lines[first_section:]
    header_lines = [lines[0], ""]
    header_lines.extend(
        f"- {label}: {value}"
        for label, value in ordered_fields
        if str(value).strip()
    )
    return "\n".join([*header_lines, "", *body]).rstrip() + "\n"


def project_card_name(parsed: dict[str, Any]) -> str:
    title = parsed.get("title", "")
    if "｜" in title:
        return title.split("｜", 1)[1].strip()
    return title.replace("项目卡片", "").strip(" |｜")


def value_from_fields(
    fields: dict[str, str],
    *labels: str,
    default: str = "",
) -> str:
    for label in labels:
        value = fields.get(label)
        if value is not None and value != "":
            return value
    return default
