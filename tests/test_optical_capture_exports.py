from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.build_optical_capture_exports import CAPTURES, build_document
from tools.validate_protocol_export import validate_document


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("capture_key", sorted(CAPTURES))
def test_optical_capture_export_builds_and_validates(capture_key: str) -> None:
    document = build_document(capture_key)
    validate_document(document)
    assert document["schema_version"] == "0.2.0"
    assert document["segments"][0]["execution_layer"] == "physical_measurement"
    assert document["audio_asset"]["identity_status"] == "unavailable"
    assert any(clock["kind"] == "optical_measurement" for clock in document["clocks"])
    assert any(
        evidence["evidence_type"] == "four_emitter_optical_synchrony"
        for evidence in document["ave_evidence"]
    )


@pytest.mark.parametrize("capture_key", sorted(CAPTURES))
def test_checked_in_optical_capture_export_validates(capture_key: str) -> None:
    export = ROOT / "reports/lumenate_nova/exports" / CAPTURES[capture_key]["filename"]
    validate_document(json.loads(export.read_text(encoding="utf-8")))


def test_only_offline_capture_claims_observed_firmware_version() -> None:
    assert build_document("offline-explore")["device"]["firmware_version"] == "1.0.4"
    assert build_document("deep-exploration")["device"]["firmware_version"] is None
    assert build_document("spirit")["device"]["firmware_version"] is None
