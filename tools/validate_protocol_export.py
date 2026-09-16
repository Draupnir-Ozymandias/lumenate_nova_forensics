#!/usr/bin/env python3
"""Validate a Lumenate protocol export against the current contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import jsonschema
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
SCHEMA_PATH = CONTRACTS / "lumenate-protocol-export.schema.json"
AVE_SCHEMA_PATH = CONTRACTS / "ave-evidence-object-1.0.0.schema.json"
AVE_SCHEMA_URI = (
    "https://example.invalid/lumenate-nova/contracts/"
    "ave-evidence-object-1.0.0.schema.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _check_references(
    errors: list[str],
    owner: str,
    values: Iterable[str],
    available: set[str],
    kind: str,
) -> None:
    for value in values:
        if value not in available:
            errors.append(f"{owner} references unknown {kind} {value!r}")


def semantic_errors(document: dict[str, Any]) -> list[str]:
    """Return cross-field errors not expressible in the JSON Schema."""
    errors: list[str] = []
    duration = document["session"]["duration_ms"]

    collections = {
        "clock": ("clocks", "clock_id"),
        "segment": ("segments", "segment_id"),
        "transition": ("transitions", "transition_id"),
        "command": ("commands", "command_id"),
        "anchor": ("sync_anchors", "anchor_id"),
        "evidence": ("ave_evidence", "evidence_id"),
        "source": ("provenance.source_hashes", "source_id"),
    }
    ids: dict[str, set[str]] = {}
    for kind, (collection, field) in collections.items():
        if collection == "provenance.source_hashes":
            items = document["provenance"]["source_hashes"]
        else:
            items = document[collection]
        values = [item[field] for item in items]
        duplicates = _duplicates(values)
        if duplicates:
            errors.append(f"duplicate {kind} IDs: {', '.join(sorted(duplicates))}")
        ids[kind] = set(values)

    for name in ("light_timeline_origin", "audio_timeline_origin"):
        origin = document["session"][name]
        if origin is not None:
            _check_references(errors, f"session.{name}", [origin["clock_id"]], ids["clock"], "clock")
            _check_references(errors, f"session.{name}", origin["evidence_ids"], ids["evidence"], "evidence")

    audio = document["audio_asset"]
    if audio["identity_status"] == "verified":
        source_hashes = {
            item["source_id"]: item["sha256"] for item in document["provenance"]["source_hashes"]
        }
        if source_hashes.get(audio["source_id"]) != audio["sha256"]:
            errors.append("verified audio identity must match a provenance source hash")

    previous_start = -1
    for segment in document["segments"]:
        owner = f"segment {segment['segment_id']!r}"
        start, end = segment["start_ms"], segment["end_ms"]
        if start < previous_start:
            errors.append(f"{owner} is not ordered by start_ms")
        previous_start = start
        if end < start:
            errors.append(f"{owner} ends before it starts")
        if end > duration:
            errors.append(f"{owner} exceeds session duration")
        _check_references(errors, owner, segment["command_ids"], ids["command"], "command")
        _check_references(errors, owner, segment["evidence_ids"], ids["evidence"], "evidence")
        _check_references(errors, owner, segment["overlap_with_segment_ids"], ids["segment"], "segment")
        if segment["segment_id"] in segment["overlap_with_segment_ids"]:
            errors.append(f"{owner} declares an overlap with itself")

    segment_list = document["segments"]
    for index, left in enumerate(segment_list):
        for right in segment_list[index + 1 :]:
            overlaps = left["start_ms"] < right["end_ms"] and right["start_ms"] < left["end_ms"]
            left_declares = right["segment_id"] in left["overlap_with_segment_ids"]
            right_declares = left["segment_id"] in right["overlap_with_segment_ids"]
            if overlaps and not (left_declares and right_declares):
                errors.append(
                    f"overlap between {left['segment_id']!r} and {right['segment_id']!r} "
                    "must be declared by both segments"
                )
            if not overlaps and (left_declares or right_declares):
                errors.append(
                    f"declared overlap between {left['segment_id']!r} and {right['segment_id']!r} does not occur"
                )

    for transition in document["transitions"]:
        owner = f"transition {transition['transition_id']!r}"
        start, end = transition["start_ms"], transition["end_ms"]
        if end < start:
            errors.append(f"{owner} ends before it starts")
        if end > duration:
            errors.append(f"{owner} exceeds session duration")
        for field in ("from_segment_id", "to_segment_id"):
            value = transition[field]
            if value is not None:
                _check_references(errors, owner, [value], ids["segment"], "segment")
        _check_references(errors, owner, transition["evidence_ids"], ids["evidence"], "evidence")

    for clock in document["clocks"]:
        _check_references(
            errors,
            f"clock {clock['clock_id']!r}",
            clock["evidence_ids"],
            ids["evidence"],
            "evidence",
        )

    for command in document["commands"]:
        owner = f"command {command['command_id']!r}"
        _check_references(errors, owner, [command["clock_id"]], ids["clock"], "clock")
        _check_references(errors, owner, command["evidence_ids"], ids["evidence"], "evidence")

    for anchor in document["sync_anchors"]:
        owner = f"anchor {anchor['anchor_id']!r}"
        clock_refs = [anchor["from_clock_id"], anchor["to_clock_id"]]
        _check_references(errors, owner, clock_refs, ids["clock"], "clock")
        if anchor["from_clock_id"] == anchor["to_clock_id"]:
            errors.append(f"{owner} must relate two different clocks")
        _check_references(errors, owner, anchor["evidence_ids"], ids["evidence"], "evidence")

    for evidence in document["ave_evidence"]:
        _check_references(
            errors,
            f"evidence {evidence['evidence_id']!r}",
            evidence["supporting_evidence_ids"],
            ids["evidence"],
            "evidence",
        )

    return errors


def validate_document(document: dict[str, Any]) -> None:
    protocol_schema = _load_json(SCHEMA_PATH)
    ave_schema = _load_json(AVE_SCHEMA_PATH)
    registry = Registry().with_resource(AVE_SCHEMA_URI, Resource.from_contents(ave_schema))
    validator = jsonschema.validators.Draft202012Validator(
        protocol_schema,
        registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )
    validator.validate(document)
    errors = semantic_errors(document)
    if errors:
        raise ValueError("Invalid protocol export:\n- " + "\n- ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="JSON export to validate")
    args = parser.parse_args()
    validate_document(_load_json(args.export))
    print(f"valid: {args.export}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
