from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.build_vitality_empirical_export import MODEL, RUN, build_document
from tools.validate_protocol_export import validate_document

ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_vitality_export_validates() -> None:
    export = ROOT / "reports/lumenate_nova/exports/vitality-5min-empirical-0.2.0.json"
    validate_document(json.loads(export.read_text(encoding="utf-8")))


@pytest.mark.skipif(
    not MODEL.exists() or not RUN.exists(),
    reason="local forensic evidence is intentionally excluded from Git",
)
def test_vitality_empirical_export_builds_and_validates() -> None:
    document = build_document()

    validate_document(document)
    assert document["schema_version"] == "0.2.0"
    assert document["session"]["duration_ms"] == 300_000
    assert len(document["segments"]) == 34
    assert document["segments"][0]["pulse"] is None
    assert document["segments"][-1]["pulse"] is None
    assert document["confidence"]["level"] == "L4"
    assert any(clock["kind"] == "media_position" for clock in document["clocks"])
    assert any(clock["kind"] == "optical_measurement" for clock in document["clocks"])
    assert any(anchor["uncertainty_ms"] == 20 for anchor in document["sync_anchors"])
    optical = next(
        evidence
        for evidence in document["ave_evidence"]
        if evidence["evidence_type"] == "four_emitter_optical_synchrony"
    )
    assert optical["provenance"]["input_sha256"] == (
        "d332a84e2e363d56d0ddd2a248a4393169c3431ca60ee7c45b5aaf68c3a881fd"
    )
