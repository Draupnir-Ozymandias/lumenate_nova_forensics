from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
from referencing import Registry, Resource

from tools.validate_protocol_export import semantic_errors, validate_document


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
AVE_SCHEMA_SHA256 = "7edee601724e13ceb2308482a9f1135acbdb850360de149f1ac009374f26ce18"
PROTOCOL_0_2_0_SCHEMA_SHA256 = "e6b6bf3fdf9d29a7a63d1f5f059584277d1296224aff227724e9620438ed265a"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_pinned_ave_schema_has_not_drifted() -> None:
    schema_path = CONTRACTS / "ave-evidence-object-1.0.0.schema.json"
    digest = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    assert digest == AVE_SCHEMA_SHA256
    assert load_json(schema_path)["properties"]["schema_version"]["const"] == "1.0.0"


def test_released_schema_is_0_2_0_and_frozen() -> None:
    current_path = CONTRACTS / "lumenate-protocol-export.schema.json"
    released_path = CONTRACTS / "lumenate-protocol-export-0.2.0.schema.json"
    assert current_path.read_bytes() == released_path.read_bytes()
    assert hashlib.sha256(released_path.read_bytes()).hexdigest() == PROTOCOL_0_2_0_SCHEMA_SHA256

    schema = load_json(released_path)
    jsonschema.validators.Draft202012Validator.check_schema(schema)
    assert schema["properties"]["schema_version"]["const"] == "0.2.0"
    assert schema["properties"]["ave_evidence_schema_version"]["const"] == "1.0.0"


def test_minimal_export_validates() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    validate_document(fixture)


def test_aligned_export_validates_complete_released_shape() -> None:
    fixture = load_json(CONTRACTS / "examples" / "aligned-export.json")
    validate_document(fixture)


def test_released_0_1_0_fixture_remains_valid() -> None:
    protocol_schema = load_json(CONTRACTS / "lumenate-protocol-export-0.1.0.schema.json")
    ave_schema = load_json(CONTRACTS / "ave-evidence-object-1.0.0.schema.json")
    fixture = load_json(CONTRACTS / "examples" / "minimal-export-0.1.0.json")

    resolved_ave_uri = (
        "https://example.invalid/lumenate-nova/contracts/"
        "ave-evidence-object-1.0.0.schema.json"
    )
    registry = Registry().with_resource(
        resolved_ave_uri,
        Resource.from_contents(ave_schema),
    )
    validator = jsonschema.validators.Draft202012Validator(protocol_schema, registry=registry)
    validator.validate(fixture)


def test_segment_ranges_are_ordered() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    assert all(segment["end_ms"] >= segment["start_ms"] for segment in fixture["segments"])


def test_verified_audio_requires_identity_fields() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    fixture["audio_asset"]["identity_status"] = "verified"

    with pytest.raises(jsonschema.ValidationError):
        validate_document(fixture)


def test_semantic_validation_rejects_dangling_references() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    fixture["segments"][0]["command_ids"] = ["missing-command"]

    assert "unknown command" in "\n".join(semantic_errors(fixture))


def test_semantic_validation_requires_explicit_overlaps() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    second = deepcopy(fixture["segments"][0])
    second["segment_id"] = "segment-002"
    second["start_ms"] = 500
    fixture["segments"].append(second)

    assert "must be declared by both segments" in "\n".join(semantic_errors(fixture))


def test_semantic_validation_rejects_unknown_clocks() -> None:
    fixture = load_json(CONTRACTS / "examples" / "minimal-export.json")
    fixture["session"]["light_timeline_origin"]["clock_id"] = "missing-clock"

    assert "unknown clock" in "\n".join(semantic_errors(fixture))


def test_verified_audio_must_match_provenance_hash() -> None:
    fixture = load_json(CONTRACTS / "examples" / "aligned-export.json")
    fixture["audio_asset"]["sha256"] = "c" * 64

    assert "must match a provenance source hash" in "\n".join(semantic_errors(fixture))
