#!/usr/bin/env python3
"""Validate the core contract of a context-package/v1 JSON file."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any


PACKAGE_TYPES = {
    "new_context", "state_update", "workflow_output", "resource_update",
    "strategy_input", "graph_delta", "outcome"
}
VISIBILITY = {"organization", "organization_core", "project_team", "restricted"}
ACTOR_TYPES = {"human", "agent", "automation"}
OBJECT_TYPES = {
    "project", "event", "report", "thesis", "person",
    "decision_snapshot", "capital_resource", "human_capital", "workflow"
}
CONTEXT_TYPES = {
    "project", "event", "report", "thesis", "person",
    "decision_snapshot", "resource", "workflow_output"
}
RELATION_TYPES = {
    "comparable_to", "counterexample_of", "supports_thesis",
    "contradicts_thesis", "linked_person", "affected_by",
    "uses_valuation_anchor"
}
BACKENDS = {"local", "feishu", "web", "other"}
KINDS = {"file", "folder", "document", "base_record", "url"}
COLLECTIONS = {
    "sources", "structured_context", "workflow_outputs",
    "actions_outcomes", "governance"
}


def check_datetime(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a date-time string")
        return
    if "T" not in value:
        errors.append(f"{label} must include a date and time")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must use ISO 8601 date-time format")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")


def check_locator(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    if value.get("backend") not in BACKENDS:
        errors.append(f"{label}.backend is invalid")
    if value.get("kind") not in KINDS:
        errors.append(f"{label}.kind is invalid")
    uri = str(value.get("uri") or "").strip()
    if not uri:
        errors.append(f"{label}.uri is required")
    elif value.get("backend") == "local":
        parts = Path(uri.replace("\\", "/")).parts
        if (
            Path(uri).is_absolute()
            or PureWindowsPath(uri).is_absolute()
            or uri.startswith(("~/", "~\\"))
            or ".." in parts
        ):
            errors.append(
                f"{label}.uri must be workspace-relative for local locators"
            )


def check_context_record(
    value: Any,
    label: str,
    errors: list[str],
) -> str:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return ""
    required = {
        "schema_version", "context_id", "context_type", "title",
        "summary", "primary_sector", "tags", "relations", "source_refs",
        "object_root", "current_artifact", "status", "visibility", "version"
    }
    for key in sorted(required - set(value)):
        errors.append(f"{label}.{key} is required")
    if value.get("schema_version") != "context-record/v1":
        errors.append(f"{label}.schema_version must be context-record/v1")
    context_id = str(value.get("context_id") or "").strip()
    if not context_id:
        errors.append(f"{label}.context_id is required")
    if value.get("context_type") not in CONTEXT_TYPES:
        errors.append(f"{label}.context_type is invalid")
    if not str(value.get("title") or "").strip():
        errors.append(f"{label}.title is required")
    if not isinstance(value.get("summary"), str):
        errors.append(f"{label}.summary must be a string")
    if not isinstance(value.get("primary_sector"), str):
        errors.append(f"{label}.primary_sector must be a string")
    tags = value.get("tags")
    if not isinstance(tags, list) or not all(
        isinstance(tag, str) for tag in tags
    ):
        errors.append(f"{label}.tags must be an array of strings")
    if not str(value.get("status") or "").strip():
        errors.append(f"{label}.status is required")
    if not str(value.get("version") or "").strip():
        errors.append(f"{label}.version is required")
    if value.get("visibility") not in VISIBILITY:
        errors.append(f"{label}.visibility is invalid")
    check_locator(value.get("object_root"), f"{label}.object_root", errors)
    check_locator(
        value.get("current_artifact"),
        f"{label}.current_artifact",
        errors,
    )
    source_refs = value.get("source_refs")
    if not isinstance(source_refs, list):
        errors.append(f"{label}.source_refs must be an array")
    else:
        if not source_refs:
            errors.append(
                f"{label}.source_refs must contain at least one locator"
            )
        for index, locator_value in enumerate(source_refs):
            check_locator(
                locator_value,
                f"{label}.source_refs[{index}]",
                errors,
            )
    relations = value.get("relations")
    if not isinstance(relations, list):
        errors.append(f"{label}.relations must be an array")
    else:
        for index, relation in enumerate(relations):
            relation_label = f"{label}.relations[{index}]"
            if not isinstance(relation, dict):
                errors.append(f"{relation_label} must be an object")
                continue
            if relation.get("relation_type") not in RELATION_TYPES:
                errors.append(f"{relation_label}.relation_type is invalid")
            if not str(relation.get("target") or "").strip():
                errors.append(f"{relation_label}.target is required")
    return context_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    args = parser.parse_args()
    path = Path(args.package).expanduser().resolve()
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: {exc}")
        return 1

    errors: list[str] = []
    if not isinstance(package, dict):
        print("FAILED with 1 error(s)")
        print("- package must be an object")
        return 1
    required = {
        "schema_version", "package_id", "package_type", "created_at",
        "created_by", "visibility", "object", "trigger", "source_refs"
    }
    for key in sorted(required - set(package)):
        errors.append(f"missing required field: {key}")
    if package.get("schema_version") != "context-package/v1":
        errors.append("schema_version must be context-package/v1")
    if not str(package.get("package_id") or "").strip():
        errors.append("package_id is required")
    if package.get("package_type") not in PACKAGE_TYPES:
        errors.append("package_type is invalid")
    if package.get("visibility") not in VISIBILITY:
        errors.append("visibility is invalid")
    check_datetime(package.get("created_at"), "created_at", errors)

    actor = package.get("created_by")
    if not isinstance(actor, dict):
        errors.append("created_by must be an object")
    else:
        if actor.get("actor_type") not in ACTOR_TYPES:
            errors.append("created_by.actor_type is invalid")
        if not str(actor.get("actor_id") or "").strip():
            errors.append("created_by.actor_id is required")
    obj = package.get("object")
    if not isinstance(obj, dict):
        errors.append("object must be an object")
    else:
        for key in ("object_id", "object_type", "title"):
            if not str(obj.get(key) or "").strip():
                errors.append(f"object.{key} is required")
        if obj.get("object_type") not in OBJECT_TYPES:
            errors.append("object.object_type is invalid")
        if obj.get("object_root") is not None:
            check_locator(obj["object_root"], "object.object_root", errors)
    trigger = package.get("trigger")
    if not isinstance(trigger, dict):
        errors.append("trigger must be an object")
    else:
        if not str(trigger.get("trigger_type") or "").strip():
            errors.append("trigger.trigger_type is required")
        if not str(trigger.get("summary") or "").strip():
            errors.append("trigger.summary is required")
        if trigger.get("occurred_at") is not None:
            check_datetime(trigger["occurred_at"], "trigger.occurred_at", errors)

    source_refs = package.get("source_refs")
    if not isinstance(source_refs, list):
        errors.append("source_refs must be an array")
    else:
        if not source_refs:
            errors.append("source_refs must contain at least one locator")
        for index, value in enumerate(source_refs):
            check_locator(value, f"source_refs[{index}]", errors)

    seen: set[str] = set()
    artifacts = package.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("artifacts must be an array")
        artifacts = []
    for index, value in enumerate(artifacts):
        label = f"artifacts[{index}]"
        if not isinstance(value, dict):
            errors.append(f"{label} must be an object")
            continue
        artifact_id = str(value.get("artifact_id") or "")
        if not artifact_id or artifact_id in seen:
            errors.append(f"{label}.artifact_id is missing or duplicated")
        seen.add(artifact_id)
        if value.get("collection") not in COLLECTIONS:
            errors.append(f"{label}.collection is invalid")
        if not str(value.get("title") or "").strip():
            errors.append(f"{label}.title is required")
        check_locator(value.get("locator"), f"{label}.locator", errors)
        if value.get("source_locator") is not None:
            check_locator(
                value["source_locator"],
                f"{label}.source_locator",
                errors,
            )

    workflow_outputs = package.get("workflow_outputs", [])
    if not isinstance(workflow_outputs, list):
        errors.append("workflow_outputs must be an array")
    else:
        for index, value in enumerate(workflow_outputs):
            label = f"workflow_outputs[{index}]"
            if not isinstance(value, dict):
                errors.append(f"{label} must be an object")
                continue
            for key in ("workflow_id", "workflow_version", "summary"):
                if not str(value.get(key) or "").strip():
                    errors.append(f"{label}.{key} is required")
            artifact_refs = value.get("artifact_refs", [])
            if not isinstance(artifact_refs, list):
                errors.append(f"{label}.artifact_refs must be an array")
            else:
                for artifact_id in artifact_refs:
                    if artifact_id not in seen:
                        errors.append(
                            f"{label}.artifact_refs contains unknown artifact "
                            f"{artifact_id!r}"
                        )

    graph_delta = package.get("graph_delta")
    if graph_delta is not None:
        if not isinstance(graph_delta, dict):
            errors.append("graph_delta must be an object")
        else:
            if graph_delta.get("schema_version") != "context-registry-delta/v1":
                errors.append(
                    "graph_delta.schema_version must be "
                    "context-registry-delta/v1"
                )
            records = graph_delta.get("records")
            if not isinstance(records, list):
                errors.append("graph_delta.records must be an array")
            else:
                context_ids: set[str] = set()
                for index, value in enumerate(records):
                    context_id = check_context_record(
                        value, f"graph_delta.records[{index}]", errors
                    )
                    if context_id in context_ids:
                        errors.append(
                            f"graph_delta.records[{index}].context_id is duplicated"
                        )
                    if context_id:
                        context_ids.add(context_id)

    if package.get("writeback") is not None and not isinstance(
        package["writeback"], dict
    ):
        errors.append("writeback must be an object")

    if errors:
        print(f"FAILED with {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"OK: {package['package_id']}; {len(artifacts)} artifact(s); "
        f"object={package['object']['object_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
