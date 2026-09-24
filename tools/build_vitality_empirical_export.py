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
E_OPTICAL = stable_id("ave", "vitality-5m-s21-optical-2026-09-20-1-500")
E_BRIDGE = stable_id("ave", "vitality-5m-audio-ble-optical-bridge-2026-09-24")
E_DISCONNECT = stable_id("ave", "nova-vitality-disconnect-watchdog-2026-09-24")
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
        evidence_object(
            E_OPTICAL,
            "measurement",
            "four_emitter_optical_synchrony",
            "A full-session 120 fps S21 recording physically measured synchronized output across all four Nova emitters.",
            ["light-emitter-1", "light-emitter-2", "light-emitter-3", "light-emitter-4"],
            {"start": 0, "end": 306.244822},
            [
                {"name": "video_frame_rate", "value": 120, "unit": "frames/second"},
                {"name": "frame_count", "value": 36732, "unit": "count"},
                {"name": "emitter_1_rising_edges", "value": 3123, "unit": "count"},
                {"name": "emitter_2_rising_edges", "value": 3123, "unit": "count"},
                {"name": "emitter_3_rising_edges", "value": 3122, "unit": "count"},
                {"name": "emitter_4_rising_edges", "value": 3123, "unit": "count"},
                {"name": "same_frame_four_emitter_rising_edges", "value": 3091, "unit": "count"},
                {"name": "binary_disagreement_frames", "value": 52, "unit": "count"},
                {"name": "binary_disagreement_fraction", "value": 0.00142, "unit": "ratio"},
                {"name": "constant_segment_frequency", "value": 10.4644, "unit": "Hz"},
            ],
            {
                "camera": "Samsung Galaxy S21 Ultra 5G",
                "resolution": "1920x1080",
                "operator_reported_iso": 50,
                "operator_reported_shutter_seconds": 0.002,
                "classification": "50x50 core-region mean luma > 30",
            },
            0.98,
            "Threshold-robust per-frame luma analysis of four spatially separate emitter cores.",
            {
                "source_id": "vitality-s21-120fps-1-500",
                "input_sha256": "d332a84e2e363d56d0ddd2a248a4393169c3431ca60ee7c45b5aaf68c3a881fd",
            },
            [
                "The 8.33 ms video frame interval cannot exclude subframe phase offsets.",
                "A 1/500-second exposure can miss narrow pulses between frames.",
                "The recording is not a calibrated intensity or duty-cycle measurement.",
                "The exposure settings are operator-recalled rather than independently embedded in the file.",
            ],
            [E_DECLARATION, E_BLE],
        ),
        evidence_object(
            E_BRIDGE,
            "association",
            "audio_ble_optical_clock_bridge",
            "One simultaneous run maps the verified Vitality audio, BLE command stream, and four-emitter S21 video onto a bounded common timeline.",
            ["audio", "light-control", "light-emitter-1", "light-emitter-2", "light-emitter-3", "light-emitter-4"],
            {"start": 0, "end": 98.276073},
            [
                {"name": "video_frame_count", "value": 14223, "unit": "count"},
                {"name": "nonzero_timing_write_count", "value": 772, "unit": "count"},
                {"name": "captured_active_segment_count", "value": 11, "unit": "count"},
                {"name": "emitter_rising_edges_each", "value": 963, "unit": "count"},
                {"name": "same_frame_four_emitter_rising_edges", "value": 960, "unit": "count"},
                {"name": "binary_disagreement_frames", "value": 13, "unit": "count"},
                {"name": "minimum_pairwise_luma_correlation", "value": 0.997984, "unit": "correlation"},
                {"name": "maximum_pairwise_luma_correlation", "value": 0.99987, "unit": "correlation"},
                {"name": "audio_video_anchor_uncertainty", "value": 20, "unit": "ms"},
                {"name": "measured_7_5_hz_region", "value": 7.4818, "unit": "Hz"},
                {"name": "measured_10_5_hz_region", "value": 10.4638, "unit": "Hz"},
            ],
            {
                "runtime_app_version": "7.2.1",
                "firmware_version": "1.0.4",
                "camera": "Samsung Galaxy S21 Ultra 5G",
                "video": "1920x1080 at approximately 120 fps",
                "classification": "60x60 emitter-core mean luma > 30",
                "audio_alignment": "Band-limited normalized cross-correlation against the SHA-256-identified Vitality asset",
            },
            0.99,
            "Cross-correlate the S21 soundtrack to the verified asset, pair Android MediaSession and HCI wall-clock events, and measure four fixed emitter regions on the same S21 media timeline.",
            {
                "source_ids": [
                    "vitality-correlated-s21-video",
                    "vitality-correlated-btsnoop",
                    "vitality-correlated-app-writes",
                    "vitality-correlated-dumpstate",
                    "vitality-5min-audio",
                ]
            },
            [
                "The 20 ms audio/video anchor uncertainty includes observed local-correlation spread but not calibrated acoustic propagation or Android output latency.",
                "The 8.33 ms video frame interval and 1/500-second exposure can miss narrow pulses and cannot resolve subframe emitter phase.",
                "The first camera-detected pulse is not a calibrated packet-to-photon latency measurement.",
            ],
            [E_AUDIO, E_SYNC, E_BLE, E_OPTICAL],
        ),
        evidence_object(
            E_DISCONNECT,
            "measurement",
            "forced_disconnect_watchdog_behavior",
            "Nova firmware 1.0.4 retained the final 10.5 Hz command for roughly three observed cycles after forced BLE loss, then stopped all four emitters without an app zero or inactive write.",
            ["light-control", "light-emitter-1", "light-emitter-2", "light-emitter-3", "light-emitter-4"],
            {"start": 0, "end": 45.612136},
            [
                {"name": "nonzero_timing_write_count", "value": 334, "unit": "count"},
                {"name": "last_command_period", "value": 95238, "unit": "microseconds"},
                {"name": "last_command_on_time", "value": 19048, "unit": "microseconds"},
                {"name": "last_command_age_at_disconnect", "value": 8572.807, "unit": "ms"},
                {"name": "post_disconnect_rising_edges_each", "value": 3, "unit": "count"},
                {"name": "last_rising_edge_after_disconnect", "value": 212.61, "unit": "ms"},
                {"name": "last_illuminated_frame_after_disconnect", "value": 229.277, "unit": "ms"},
                {"name": "dark_frames_after_last_illumination", "value": 3427, "unit": "count"},
                {"name": "minimum_pairwise_luma_correlation", "value": 0.998539, "unit": "correlation"},
                {"name": "maximum_pairwise_luma_correlation", "value": 0.999982, "unit": "correlation"},
            ],
            {
                "runtime_app_version": "7.2.1",
                "firmware_version": "1.0.4",
                "disconnect_reason": "HCI 0x16, local host termination",
                "normal_zero_or_inactive_write_observed": False,
                "last_command": "approximately 10.5 Hz at 20% duty",
                "camera": "Samsung Galaxy S21 Ultra 5G, approximately 120 fps",
            },
            0.98,
            "Map the HCI disconnect to the verified-audio S21 timeline, then threshold four fixed emitter regions across the disconnect boundary.",
            {
                "source_ids": [
                    "vitality-disconnect-s21-video",
                    "vitality-disconnect-btsnoop",
                    "vitality-disconnect-app-writes",
                    "vitality-disconnect-dumpstate",
                ]
            },
            [
                "The approximately 0.3-second cessation bound is camera-observed, not a calibrated photon-level watchdog timeout.",
                "Finite 1/500-second exposures at 120 fps can miss narrow pulses between frames.",
                "The result is bounded to firmware 1.0.4, the compact matched-side path, and the tested 10.5 Hz / 20% command.",
            ],
            [E_BRIDGE, E_BLE, E_OPTICAL],
        ),
        pulse,
    ]


def build_document() -> dict[str, Any]:
    parsed = parse_program(extract_vitality_program())
    document = {
        "schema_version": "0.2.0",
        "ave_evidence_schema_version": "1.0.0",
        "export_id": stable_id("ln", f"vitality-5m-{AUDIO_SHA256}-v7.2.1-candidate-0.2.0"),
        "created_at": "2026-09-24T14:12:53Z",
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
            {
                "clock_id": "optical-video-ms",
                "kind": "optical_measurement",
                "monotonic": True,
                "unit": "ms",
                "origin": "Start of the S21 120 fps Vitality replication video.",
                "resolution_ms": 8.333333,
                "evidence_ids": [E_OPTICAL],
            },
            {
                "clock_id": "ble-correlated-capture-ms",
                "kind": "ble_capture",
                "monotonic": True,
                "unit": "ms",
                "origin": "2026-09-24 correlated-run active-state write at HCI epoch 1790241818.356861; Android's local-time btsnoop encoding is treated only as a within-run clock.",
                "resolution_ms": 0.001,
                "evidence_ids": [E_BRIDGE],
            },
            {
                "clock_id": "correlated-optical-video-ms",
                "kind": "optical_measurement",
                "monotonic": True,
                "unit": "ms",
                "origin": "Start of the simultaneous 2026-09-24 S21 Vitality video.",
                "resolution_ms": 8.333333,
                "evidence_ids": [E_BRIDGE],
            },
            {
                "clock_id": "ble-disconnect-capture-ms",
                "kind": "ble_capture",
                "monotonic": True,
                "unit": "ms",
                "origin": "2026-09-24 disconnect-run active-state write at HCI epoch 1790244078.072023; elapsed time is authoritative within the run.",
                "resolution_ms": 0.001,
                "evidence_ids": [E_DISCONNECT],
            },
            {
                "clock_id": "disconnect-optical-video-ms",
                "kind": "optical_measurement",
                "monotonic": True,
                "unit": "ms",
                "origin": "Start of the successful 2026-09-24 S21 disconnect video.",
                "resolution_ms": 8.333333,
                "evidence_ids": [E_DISCONNECT],
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
            {
                "anchor_id": "correlated-run-ble-active-to-media",
                "from_clock_id": "ble-correlated-capture-ms",
                "from_time_ms": 0,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 3.861,
                "uncertainty_ms": 5,
                "method": "The HCI active-state write at 09:23:38.356861 was paired to the Android MediaSession PLAYING position-zero event at 09:23:38.353 in the same bugreport.",
                "evidence_ids": [E_BRIDGE],
            },
            {
                "anchor_id": "correlated-video-to-audio-early",
                "from_clock_id": "correlated-optical-video-ms",
                "from_time_ms": 8047.75,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 44,
                "uncertainty_ms": 20,
                "method": "Normalized cross-correlation maps decoded-reference time zero to S21 video time 8.047750 s; the verified audio stream begins at media position 44 ms.",
                "evidence_ids": [E_BRIDGE, E_AUDIO],
            },
            {
                "anchor_id": "correlated-video-to-audio-late",
                "from_clock_id": "correlated-optical-video-ms",
                "from_time_ms": 83047.625,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 75044,
                "uncertainty_ms": 20,
                "method": "A late 20-second local cross-correlation maps decoded-reference time 75 s to S21 video time 83.047625 s.",
                "evidence_ids": [E_BRIDGE, E_AUDIO],
            },
            {
                "anchor_id": "disconnect-video-to-audio",
                "from_clock_id": "disconnect-optical-video-ms",
                "from_time_ms": 6961.875,
                "to_clock_id": "audio-media-position-ms",
                "to_time_ms": 44,
                "uncertainty_ms": 20,
                "method": "Normalized cross-correlation maps decoded-reference time zero to disconnect-video time 6.961875 s; the verified audio stream begins at media position 44 ms.",
                "evidence_ids": [E_DISCONNECT, E_AUDIO],
            },
            {
                "anchor_id": "disconnect-ble-active-to-video",
                "from_clock_id": "ble-disconnect-capture-ms",
                "from_time_ms": 0,
                "to_clock_id": "disconnect-optical-video-ms",
                "to_time_ms": 6968.898,
                "uncertainty_ms": 20,
                "method": "Pair the HCI active write at 10:01:18.072023 with the MediaSession position-zero event at 10:01:18.021, then map media position zero to S21 video time 6.917875 s.",
                "evidence_ids": [E_DISCONNECT],
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
                {"source_id": "vitality-s21-120fps-1-500", "sha256": "d332a84e2e363d56d0ddd2a248a4393169c3431ca60ee7c45b5aaf68c3a881fd"},
                {"source_id": "vitality-correlated-s21-video", "sha256": "024e8cbfdbfeef3a3ff53235e5490753ad0579c0f36253dedf2e3dcd6d0bee11"},
                {"source_id": "vitality-correlated-btsnoop", "sha256": "f4699c289fb9d42bb6418af1d3affcceb727643959f9d4fc6821a758f5ea3ea3"},
                {"source_id": "vitality-correlated-app-writes", "sha256": "603237f02eeb14e8855a127226b464f111b58c40e809fec0af5d7406e778337d"},
                {"source_id": "vitality-correlated-dumpstate", "sha256": "16abe2346c58d0245e463c2275fec5b4bb1ade2600e9b17ce24bdf32102f2475"},
                {"source_id": "vitality-disconnect-s21-video", "sha256": "6ac885d0b40ad879347b0bc6526f6165af48b475397a05ab3b87755e707f4dba"},
                {"source_id": "vitality-disconnect-btsnoop", "sha256": "8b70f60c6b25946b1922f71d9555558544b4526f3704bfa0cbef3ddfebfaa526"},
                {"source_id": "vitality-disconnect-app-writes", "sha256": "7a8afed355552fcbf73b42e90876ff9143b72b5c47d784738237960abde0b2c9"},
                {"source_id": "vitality-disconnect-dumpstate", "sha256": "29770db474b477e75398f6ec023c97d317bc1f9677cdff06bf46d5f116526cb9"},
            ],
            "acquisition_notes": [
                "Two unfiltered Android Bluetooth HCI snoop runs were captured without physical brightness-button input.",
                "A third uninterrupted five-minute run completed naturally and covered all 32 declared active segments.",
                "The runtime package and decompiled declaration are both Lumenate 7.2.1 (400).",
                "The 7.2.1 Vitality declaration and StrobeManager are byte-for-byte identical to their acquired 7.0.0 counterparts.",
                "A complementary full-session S21 recording physically measured the four emitter cores at approximately 120 fps.",
                "A 2026-09-24 simultaneous A35 HCI plus S21 video/audio run established a bounded BLE/audio/video common clock over the first 98 seconds of Vitality.",
                "A separate controlled 2026-09-24 run measured firmware 1.0.4 light-off behavior after forced BLE loss without normal zero/inactive writes.",
                "Signed media URLs, Bluetooth addresses, phone identifiers, and audio bytes are intentionally excluded.",
            ],
        },
        "confidence": {
            "level": "L4",
            "score": 0.98,
            "method": "The full runtime-version declaration is confirmed across all 32 active segments in a natural five-minute BLE capture; full-session S21 recordings confirm frequency and four-emitter synchrony, a simultaneous run binds BLE/audio/video clocks, and a controlled forced-disconnect run bounds firmware 1.0.4 safe-stop behavior.",
        },
        "limitations": [
            "No photodiode measurement was made; S21 video physically verifies frequency and frame-scale synchrony but cannot resolve subframe phase or provide calibrated duty cycle or intensity.",
            "Brightness-button level, LED intensity calibration, color, and firmware version are unknown.",
            "The simultaneous audio/video anchors carry 20 ms uncertainty; camera sampling and unknown firmware-to-photon latency still prevent a calibrated packet-to-photon claim.",
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
