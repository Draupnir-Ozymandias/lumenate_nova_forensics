#!/usr/bin/env python3
"""Build the sanitized Vitality 5-minute empirical 0.2.0 export."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.strobe_program import Expression, Segment, parse_program
from tools.validate_protocol_export import validate_document


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "dynamic/lumenate_nova/runs/2026-09-17_vitality-track_1556"
ACQUISITION = ROOT / "dynamic/lumenate_nova/acquisitions/2026-09-19_v7.2.1"
MODEL = ACQUISITION / "apktool/smali_classes4/com/lumenate/lumenate/model/a.smali"
OUTPUT = ROOT / "reports/lumenate_nova/exports/vitality-5min-empirical-0.2.0.json"

AUDIO_SHA256 = "b24513faf9f3e920d9addf725563bd236fa3b33f6c1fa91949bcf6011eda7c41"
FIRST_PACKET_AFTER_ACTIVE_MS = 1449.590


def stable_id(prefix: str, label: str) -> str:
    return f"{prefix}_{hashlib.sha256(label.encode()).hexdigest()[:16]}"


E_DECLARATION = stable_id("ave", "vitality-5m-session-declaration-v7.2.1")
E_REPEAT = stable_id("ave", "vitality-5m-ble-repeatability-2026-09-17")
E_BLE = stable_id("ave", "vitality-5m-full-ble-confirmation-2026-09-19")
E_SYNC = stable_id("ave", "vitality-5m-media-ble-clock-association-run2")
E_AUDIO = stable_id("ave", f"vitality-5m-audio-{AUDIO_SHA256}")
E_AVEPULSE = "ave_cff3179ab694b1b9"


def extract_vitality_program() -> str:
    text = MODEL.read_text(encoding="utf-8")
    matches = set(
        re.findall(
            r'const-string v\d+, "(s\(0,1\.5,z,z\);[^"\n]+s\(298,300,z,z\))"',
            text,
        )
    )
    if len(matches) != 1:
        raise ValueError(f"expected one Vitality 5-minute program, found {len(matches)}")
    return next(iter(matches))


def expression_json(expression: Expression) -> dict[str, Any]:
    return {"start": expression.start, "end": expression.end, "mode": expression.kind}


def pulse_for(segment: Segment) -> dict[str, Any] | None:
    if segment.frequency.is_off and segment.duty.is_off:
        return None
    if segment.frequency.is_off or segment.duty.is_off:
        raise ValueError("partially off segment is not supported")
    frequency = segment.frequency.start if segment.frequency.is_constant else None
    duty = segment.duty.start if segment.duty.is_constant else None
    on_ms = None
    off_ms = None
    if frequency is not None and duty is not None:
        period_ms = 1000.0 / frequency
        on_ms = period_ms * duty
        off_ms = period_ms - on_ms
    interpolated = not (segment.frequency.is_constant and segment.duty.is_constant)
    detail = None
    if interpolated:
        detail = (
            "Linear parameter interpolation; frequency "
            f"{segment.frequency.start:g}->{segment.frequency.end:g} Hz and duty "
            f"{segment.duty.start:g}->{segment.duty.end:g}."
        )
    return {
        "frequency_hz": frequency,
        "duty_cycle": duty,
        "on_ms": on_ms,
        "off_ms": off_ms,
        "shape": "interpolated" if interpolated else "square",
        "shape_detail": detail,
    }


def make_segments(parsed: list[Segment]) -> list[dict[str, Any]]:
    result = []
    for index, segment in enumerate(parsed, 1):
        start_ms = round(segment.start_s * 1000)
        evidence_ids = [E_DECLARATION, E_BLE]
        result.append(
            {
                "segment_id": f"vitality-segment-{index:03d}",
                "start_ms": start_ms,
                "end_ms": round(segment.end_s * 1000),
                "execution_layer": "session_declaration",
                "intensity": None,
                "color_rgb": None,
                "pulse": pulse_for(segment),
                "overlap_with_segment_ids": [],
                "command_ids": [],
                "evidence_ids": evidence_ids,
            }
        )
    return result


def make_transitions(parsed: list[Segment]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index in range(1, len(parsed)):
        at_ms = round(parsed[index].start_s * 1000)
        evidence_ids = [E_DECLARATION, E_BLE]
        result.append(
            {
                "transition_id": f"vitality-boundary-{index:03d}",
                "type": "step",
                "start_ms": at_ms,
                "end_ms": at_ms,
                "from_segment_id": f"vitality-segment-{index:03d}",
                "to_segment_id": f"vitality-segment-{index + 1:03d}",
                "execution_layer": "session_declaration",
                "parameters": {"changed_fields": ["pulse.frequency_hz", "pulse.duty_cycle"]},
                "evidence_ids": evidence_ids,
            }
        )
    for index, segment in enumerate(parsed, 1):
        if segment.frequency.kind != "linear" and segment.duty.kind != "linear":
            continue
        parameters: dict[str, Any] = {}
        if segment.frequency.kind == "linear":
            parameters["frequency_hz"] = expression_json(segment.frequency)
        if segment.duty.kind == "linear":
            parameters["duty_cycle"] = expression_json(segment.duty)
        evidence_ids = [E_DECLARATION, E_BLE]
        result.append(
            {
                "transition_id": f"vitality-interpolation-{index:03d}",
                "type": "interpolation",
                "start_ms": round(segment.start_s * 1000),
                "end_ms": round(segment.end_s * 1000),
                "from_segment_id": f"vitality-segment-{index:03d}",
                "to_segment_id": f"vitality-segment-{index:03d}",
                "execution_layer": "session_declaration",
                "parameters": parameters,
                "evidence_ids": evidence_ids,
            }
        )
    return result


def representative_commands() -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = [
        {
            "command_id": "run2-active-state",
            "clock_id": "ble-run2-capture-ms",
            "time_ms": 0,
            "direction": "app_to_device",
            "execution_layer": "ble_transport",
            "service_uuid": None,
            "characteristic_uuid": "att-handle-0x0039",
            "payload_hex": "0a",
            "interpretation": "Observed active-state write.",
            "evidence_ids": [E_REPEAT],
        }
    ]
    with (RUN / "vitality-repeatability.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))[:12]
    for row in rows:
        period_us = int(row["period2_us"])
        on_time_us = int(row["on_time2_us"])
        elapsed_ms = FIRST_PACKET_AFTER_ACTIVE_MS + float(row["run2_elapsed_s"]) * 1000
        commands.append(
            {
                "command_id": f"run2-strobe-{int(row['index']):03d}",
                "clock_id": "ble-run2-capture-ms",
                "time_ms": round(elapsed_ms, 3),
                "direction": "app_to_device",
                "execution_layer": "ble_transport",
                "service_uuid": None,
                "characteristic_uuid": "att-handle-0x0034",
                "payload_hex": row["run2_payload"],
                "interpretation": (
                    f"Observed little-endian timing write: period={period_us} us, "
                    f"on-time={on_time_us} us, constant-on={row['constant2_ppm']} ppm."
                ),
                "evidence_ids": [E_REPEAT],
            }
        )
    commands.append(
        {
            "command_id": "run2-inactive-state",
            "clock_id": "ble-run2-capture-ms",
            "time_ms": 68403.949,
            "direction": "app_to_device",
            "execution_layer": "ble_transport",
            "service_uuid": None,
            "characteristic_uuid": "att-handle-0x0039",
            "payload_hex": "00",
            "interpretation": "Observed operator-triggered inactive-state write.",
            "evidence_ids": [E_REPEAT],
        }
    )
    return commands


def evidence_object(
    evidence_id: str,
    level: str,
    evidence_type: str,
    summary: str,
    channels: list[str],
    time_range: dict[str, float] | None,
    measurements: list[dict[str, Any]],
    context: dict[str, Any],
    score: float,
    method: str,
    provenance: dict[str, Any],
    limitations: list[str],
    supporting: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "evidence_level": level,
        "evidence_type": evidence_type,
        "source_module": "lumenate_nova.vitality_export",
        "summary": summary,
        "scope": {"channels": channels, "time_range_seconds": time_range},
        "measurements": measurements,
        "context": context,
        "confidence": {"score": score, "method": method},
        "provenance": provenance,
        "supporting_evidence_ids": supporting or [],
        "limitations": limitations,
    }


def make_evidence(segment_count: int) -> list[dict[str, Any]]:
    ave_evidence = json.loads((RUN / "ave-analysis/ave_evidence.json").read_text(encoding="utf-8"))
    pulse = next(item for item in ave_evidence["evidence"] if item["evidence_id"] == E_AVEPULSE)
    return [
        evidence_object(
            E_DECLARATION,
            "reconstruction",
            "deterministic_strobe_program",
            f"A contiguous 300-second Vitality declaration reconstructs {segment_count} light segments.",
            ["light"],
            {"start": 0, "end": 300},
            [
                {"name": "segment_count", "value": segment_count, "unit": "count"},
                {"name": "declared_duration", "value": 300, "unit": "seconds"},
                {"name": "minimum_frequency", "value": 7.0, "unit": "Hz"},
                {"name": "maximum_frequency", "value": 13.5, "unit": "Hz"},
            ],
            {"decompiled_app_version": "7.2.1", "program_language": "s(start,end,frequency,duty)"},
            0.99,
            "Exact parse of the acquired runtime-version declaration with full-duration BLE agreement.",
            {"source_id": "session-model-smali-v7.2.1"},
            ["Transport confirmation is not physical optical confirmation."],
        ),
        evidence_object(
            E_BLE,
            "measurement",
            "full_duration_ble_strobe_confirmation",
            "A natural five-minute run emitted timing writes across every declared active segment.",
            ["light-control"],
            {"start": 0, "end": 299.492362},
            [
                {"name": "nonzero_timing_write_count", "value": 2962, "unit": "count"},
                {"name": "observed_active_segment_count", "value": 32, "unit": "count"},
                {"name": "declared_active_segment_count", "value": 32, "unit": "count"},
                {"name": "mean_absolute_frequency_error", "value": 0.0009025113, "unit": "Hz"},
                {"name": "maximum_absolute_frequency_error", "value": 0.0212385384, "unit": "Hz"},
                {"name": "mean_absolute_duty_error", "value": 0.0000490948, "unit": "ratio"},
                {"name": "maximum_absolute_duty_error", "value": 0.0005526836, "unit": "ratio"},
            ],
            {"runtime_app_version": "7.2.1", "alignment": "first nonzero write maps to program time 1.500 s"},
            0.995,
            "Decode all 12-byte timing writes and compare them with the declared segment interpolation.",
            {"source_id": "vitality-full-run-app-writes", "hci_source_id": "vitality-full-run-btsnoop"},
            ["BLE arrival timestamps are not optical-emission timestamps."],
        ),
        evidence_object(
            E_REPEAT,
            "measurement",
            "ble_strobe_timing_repeatability",
            "Two controlled starts reproduced the Vitality timing stream through the shorter run.",
            ["light-control"],
            {"start": 1.44959, "end": 68.403949},
            [
                {"name": "paired_packet_count", "value": 447, "unit": "count"},
                {"name": "byte_exact_pair_count", "value": 394, "unit": "count"},
                {"name": "maximum_field_difference", "value": 1, "unit": "microseconds"},
                {"name": "mean_timing_displacement", "value": 0.924, "unit": "ms"},
                {"name": "maximum_timing_displacement", "value": 4.732, "unit": "ms"},
            ],
            {"runtime_app_version": "7.2.1", "button_notifications_observed": 0},
            0.99,
            "Index-paired packet comparison across two independently started runs.",
            {"source_id": "vitality-repeatability-tsv", "hci_source_id": "vitality-btsnoop"},
            ["BLE arrival timestamps are not optical-emission timestamps."],
        ),
        evidence_object(
            E_SYNC,
            "association",
            "media_position_to_strobe_clock_alignment",
            "Static syncMe control flow and runtime media-position observations associate the audio and light clocks.",
            ["audio", "light-control"],
            {"start": 0, "end": 299.350},
            [
                {"name": "first_full_run_ble_media_offset", "value": 138.828, "unit": "ms"},
                {"name": "late_full_run_ble_media_offset", "value": 134.395, "unit": "ms"},
                {"name": "full_run_offset_change", "value": -4.433, "unit": "ms"},
                {"name": "anchor_uncertainty", "value": 20, "unit": "ms"},
            ],
            {"sync_function": "StrobeManager.syncMe(mediaPositionMs)", "runtime_run": "2026-09-19-full"},
            0.95,
            "Control-flow association plus start and end Android media-position/HCI wall-clock pairs.",
            {"source_ids": ["session-service-position-callback-v7.2.1", "vitality-full-run-dumpstate", "vitality-full-run-btsnoop"]},
            [
                "MediaSession state is logged asynchronously and may be stale at emission time.",
                "The 20 ms runtime uncertainty does not include unknown firmware-to-photon latency.",
            ],
            [E_DECLARATION, E_BLE, E_REPEAT],
        ),
        evidence_object(
            E_AUDIO,
            "measurement",
            "verified_session_audio_asset",
            "The cached Vitality 5-minute M4A was acquired, decoded, and cryptographically identified.",
            ["left", "right"],
            {"start": 0, "end": 299.690667},
            [
                {"name": "container_duration", "value": 299.690667, "unit": "seconds"},
                {"name": "sample_rate", "value": 48000, "unit": "Hz"},
                {"name": "channel_count", "value": 2, "unit": "count"},
                {"name": "stream_start", "value": 0.044, "unit": "seconds"},
            ],
            {"codec": "AAC-LC", "container": "M4A"},
            1.0,
            "SHA-256 identity, ffprobe metadata, and full FFmpeg decode validation.",
            {"source_id": "vitality-5min-audio", "input_sha256": AUDIO_SHA256},
            ["The copyrighted audio bytes remain local-only and are not embedded in this export."],
        ),
        pulse,
    ]


def build_document() -> dict[str, Any]:
    parsed = parse_program(extract_vitality_program())
    document = {
        "schema_version": "0.2.0",
        "ave_evidence_schema_version": "1.0.0",
        "export_id": stable_id("ln", f"vitality-5m-{AUDIO_SHA256}-v7.2.1-candidate-0.2.0"),
        "created_at": "2026-09-19T18:40:29Z",
        "device": {
            "product": "Lumenate Nova",
            "app_package": "com.lumenate.lumenateaa",
            "app_version": "7.2.1",
            "app_version_code": 400,
            "firmware_version": None,
        },
        "session": {
            "session_id": "vitality-5min-high-intensity",
            "title": "Vitality",
            "duration_ms": 300000,
            "light_timeline_origin": {
                "clock_id": "session-program-ms",
                "time_ms": 0,
                "definition": "Zero of the bundled 300-second strobe declaration.",
                "evidence_ids": [E_DECLARATION],
            },
            "audio_timeline_origin": {
                "clock_id": "audio-media-position-ms",
                "time_ms": 0,
                "definition": "ExoPlayer media position zero for the verified Vitality asset.",
                "evidence_ids": [E_AUDIO, E_SYNC],
            },
        },
        "audio_asset": {
            "identity_status": "verified",
            "source_id": "vitality-5min-audio",
            "role": "session_audio",
            "sha256": AUDIO_SHA256,
            "duration_ms": 299690.667,
            "sample_rate_hz": 48000,
            "limitations": [
                "Container duration is 309.333 ms shorter than the declared light program.",
                "The audio stream begins 44 ms into the container timeline.",
            ],
        },
        "clocks": [
            {
                "clock_id": "session-program-ms",
                "kind": "monotonic",
                "monotonic": True,
                "unit": "ms",
                "origin": "Start of the parsed strobe declaration.",
                "resolution_ms": 1,
                "evidence_ids": [E_DECLARATION],
            },
            {
                "clock_id": "audio-media-position-ms",
                "kind": "media_position",
                "monotonic": True,
                "unit": "ms",
                "origin": "ExoPlayer media position zero.",
                "resolution_ms": 1,
                "evidence_ids": [E_AUDIO, E_SYNC],
            },
            {
                "clock_id": "ble-run2-capture-ms",
                "kind": "ble_capture",
                "monotonic": True,
                "unit": "ms",
                "origin": "Run 2 active-state write at HCI epoch 1789660168.039099.",
                "resolution_ms": 0.001,
                "evidence_ids": [E_REPEAT],
            },
            {
                "clock_id": "ble-full-run-capture-ms",
                "kind": "ble_capture",
                "monotonic": True,
                "unit": "ms",
                "origin": "Full-run active-state write at HCI epoch 1789832752.288698.",
                "resolution_ms": 0.001,
                "evidence_ids": [E_BLE],
            },
        ],
        "segments": make_segments(parsed),
        "transitions": make_transitions(parsed),
        "commands": representative_commands(),
        "sync_anchors": [
            {
                "anchor_id": "program-to-media-origin",
                "from_clock_id": "session-program-ms",
                "from_time_ms": 0,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 0,
                "uncertainty_ms": 1,
                "method": "The service passes integer ExoPlayer media position directly to native StrobeManager.syncMe; this anchor excludes BLE and optical latency.",
                "evidence_ids": [E_SYNC],
            },
            {
                "anchor_id": "full-run-first-light-write-to-media",
                "from_clock_id": "ble-full-run-capture-ms",
                "from_time_ms": 1460.828,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 1322,
                "uncertainty_ms": 20,
                "method": "First nonzero BLE timing write paired to the adjacent Android MediaSession position log (approximately 5 ms wall-clock separation).",
                "evidence_ids": [E_SYNC, E_BLE],
            },
            {
                "anchor_id": "full-run-final-light-zero-to-media",
                "from_clock_id": "ble-full-run-capture-ms",
                "from_time_ms": 297964.395,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 297830,
                "uncertainty_ms": 20,
                "method": "Final zero timing write paired to the adjacent Android MediaSession position log (approximately 1 ms wall-clock separation).",
                "evidence_ids": [E_SYNC, E_BLE],
            },
        ],
        "provenance": {
            "source_hashes": [
                {"source_id": "vitality-5min-audio", "sha256": AUDIO_SHA256},
                {"source_id": "base-apk-v7.2.1", "sha256": "40a2cf2bff296006f2bdb0fbde1136f9e67608cbcce0dc54c8f34ba535fd8b7d"},
                {"source_id": "session-model-smali-v7.2.1", "sha256": "43a20771a98c9a14dace448779b252f4507325e2724f651d0e2a598662f5f85b"},
                {"source_id": "session-service-position-callback-v7.2.1", "sha256": "346943aaf06a58d3142cdeb497593d21bbf8060c3b3cbbc7e48514e2f9ad25a0"},
                {"source_id": "session-service-start-v7.2.1", "sha256": "8b08bf129b17d461de13d6e73d1305baab4886181851333640769c1e1a69965a"},
                {"source_id": "strobe-manager-smali-v7.2.1", "sha256": "473dfa8f4a84884101ba3c59f632ad7548521e2c0ff5d75b7553fabe5dd1e1e3"},
                {"source_id": "vitality-btsnoop", "sha256": "a3a2073a2dbd1fe4d3bec2993f62b97d14e8f196f9089732bef915a59bbfbfbc"},
                {"source_id": "vitality-logcat", "sha256": "52f29edebe701e0bfa18269bf834c880ed247841a637ca1ce733775fef5495f3"},
                {"source_id": "vitality-repeatability-tsv", "sha256": "7061c4bec4dc383e8ff9f5cfd308b17a0f476a64e29e222d6fb9d116284457ad"},
                {"source_id": "vitality-full-run-btsnoop", "sha256": "0792646c160d944e295479f62905923746453c49174e89de8e873891dd585913"},
                {"source_id": "vitality-full-run-app-writes", "sha256": "7ce640a4ad51b162af4b8c5881b3851983cf390ee92e3ea0f04fbe9d97ba8288"},
                {"source_id": "vitality-full-run-dumpstate", "sha256": "d0a0f27f46f128d22218925e953748e442206eaaf377767be80d5876c4c55f83"},
                {"source_id": "ave-pulse-analysis", "sha256": "65d8b0036b8856291b4f6c2e102a20dcc463772ee988f2d7e531b569aab1da31"},
            ],
            "acquisition_notes": [
                "Two unfiltered Android Bluetooth HCI snoop runs were captured without physical brightness-button input.",
                "A third uninterrupted five-minute run completed naturally and covered all 32 declared active segments.",
                "The runtime package and decompiled declaration are both Lumenate 7.2.1 (400).",
                "The 7.2.1 Vitality declaration and StrobeManager are byte-for-byte identical to their acquired 7.0.0 counterparts.",
                "Signed media URLs, Bluetooth addresses, phone identifiers, and audio bytes are intentionally excluded.",
            ],
        },
        "confidence": {
            "level": "L4",
            "score": 0.98,
            "method": "The full runtime-version declaration is confirmed across all 32 active segments in a natural five-minute BLE capture; no optical measurement exists.",
        },
        "limitations": [
            "No photodiode measurement was made; firmware behavior and actual optical output remain unverified.",
            "Brightness-button level, LED intensity calibration, color, and firmware version are unknown.",
            "Runtime audio/light anchors carry 20 ms uncertainty and exclude unknown firmware-to-photon latency.",
            "AVE classified the soundtrack as irregular transients; this does not establish intent, efficacy, or physiological response.",
        ],
        "ave_evidence": make_evidence(len(parsed)),
    }
    validate_document(document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    document = build_document()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote valid 0.2.0 export: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
