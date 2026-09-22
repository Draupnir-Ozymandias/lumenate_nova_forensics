#!/usr/bin/env python3
"""Build sanitized 0.2.0 exports for Nova optical/BLE capture windows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.validate_protocol_export import validate_document


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports/lumenate_nova/exports"


def stable_id(prefix: str, label: str) -> str:
    return f"{prefix}_{hashlib.sha256(label.encode()).hexdigest()[:16]}"


CAPTURES: dict[str, dict[str, Any]] = {
    "deep-exploration": {
        "filename": "deep-exploration-optical-empirical-0.2.0.json",
        "session_id": "deep-exploration-5min-capture",
        "title": "Deep Exploration",
        "duration_ms": 347705,
        "firmware_version": None,
        "first_on_ms": 39485,
        "last_on_ms": 314895,
        "frame_count": 41723,
        "edge_counts": [2879, 2879, 2879, 2878],
        "same_frame_edges": 2855,
        "disagreement_frames": 55,
        "disagreement_fraction": 0.0013182,
        "correlation_min": 0.998859,
        "correlation_max": 0.999981,
        "video_duration_seconds": 347.704711,
        "video_sha256": "0b526b3bc7f97b804080906461f629257b885f77d8f967c4ca2f0facb0c074a4",
        "ble": {
            "btsnoop_sha256": "ab9d8842bb9c0f03e464d6fe77b3c87718778cb23cd1666d103ee8dbb68476f7",
            "bugreport_sha256": "d5727be869bee77f5cdccb9d095b99ad53c9ec7d7bd18d6c6c854a6d069b345b",
            "timing_writes": 2916,
            "nonzero_timing_writes": 2915,
            "compact_writes": 2916,
            "extended_writes": 0,
            "active_duration_seconds": 337.126652,
            "first_timing_delay_seconds": 37.6086,
        },
        "notes": [
            "The operator reported indirect daylight and no visually apparent asynchronous flashing.",
            "The app identified the session as Deep Exploration.",
        ],
    },
    "spirit": {
        "filename": "spirit-optical-empirical-0.2.0.json",
        "session_id": "mind-games-spirit-partial-capture",
        "title": "Mind Games Meditation: Spirit",
        "duration_ms": 146197,
        "firmware_version": None,
        "first_on_ms": 53427,
        "last_on_ms": 138822,
        "frame_count": 17543,
        "edge_counts": [850, 850, 850, 850],
        "same_frame_edges": 843,
        "disagreement_frames": 20,
        "disagreement_fraction": 0.00114,
        "correlation_min": 0.997637,
        "correlation_max": 0.999956,
        "video_duration_seconds": 146.197156,
        "video_sha256": "2d527d610ac4aee0bf798ccc709bb2c89ca2e837086fa9c2a278f0853594031d",
        "ble": {
            "btsnoop_sha256": "c74d0b404ef3422212e325098d2cd9825cb3bb05d71bea30828faa53bb372cad",
            "btsnoop_rotated_sha256": "7cb8f0396dda7f0a8e045f04d33602f31e5a8d66cb408b983ee6a0d24a6dca98",
            "bugreport_sha256": "f1feba8bcecca37e4147a6d065bda571795c229eb33520c424124e14210bfed8",
            "timing_writes": 888,
            "nonzero_timing_writes": 887,
            "compact_writes": 888,
            "extended_writes": 0,
            "active_duration_seconds": 128.102536,
            "first_timing_delay_seconds": 41.905442,
        },
        "notes": [
            "The app identified the session as Spirit with a declared duration of 372.819 seconds.",
            "Only the first approximately 85.4 seconds of illuminated physical output were recorded.",
            "The operator did not visually observe asynchronous flashing.",
        ],
    },
    "offline-explore": {
        "filename": "offline-explore-optical-empirical-0.2.0.json",
        "session_id": "offline-explore-partial-capture",
        "title": "Offline Explore",
        "duration_ms": 252459,
        "firmware_version": "1.0.4",
        "first_on_ms": 64544,
        "last_on_ms": 249568,
        "frame_count": 30294,
        "edge_counts": [1584, 1586, 1586, 1584],
        "same_frame_edges": 1563,
        "disagreement_frames": 35,
        "disagreement_fraction": 0.00116,
        "correlation_min": 0.997801,
        "correlation_max": 0.999953,
        "video_duration_seconds": 252.459478,
        "video_sha256": "6314bc1142e08766dcc9ff6b134394e6811dad81843e899db9e9f721df407f6d",
        "ble": None,
        "notes": [
            "The A35 displayed Explore as the already-selected mask-resident preset before the run.",
            "The live app connection was disconnected before the operator started the preset with mask buttons.",
            "The nominal ten-minute preset was stopped after approximately 185 seconds of illuminated output.",
        ],
    },
}


def evidence_object(
    evidence_id: str,
    evidence_type: str,
    summary: str,
    channels: list[str],
    time_range: dict[str, float],
    measurements: list[dict[str, Any]],
    context: dict[str, Any],
    provenance: dict[str, Any],
    limitations: list[str],
    supporting: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "evidence_level": "measurement",
        "evidence_type": evidence_type,
        "source_module": "lumenate_nova.optical_capture_export",
        "summary": summary,
        "scope": {"channels": channels, "time_range_seconds": time_range},
        "measurements": measurements,
        "context": context,
        "confidence": {
            "score": 0.98,
            "method": "Threshold-robust per-frame luma analysis of four spatially separate emitter cores.",
        },
        "provenance": provenance,
        "supporting_evidence_ids": supporting or [],
        "limitations": limitations,
    }


def build_document(key: str) -> dict[str, Any]:
    capture = CAPTURES[key]
    optical_id = stable_id("ave", f"{key}-s21-optical-2026-09-21")
    ble_id = stable_id("ave", f"{key}-ble-2026-09-21") if capture["ble"] else None
    evidence_ids = [optical_id]
    source_hashes = [
        {"source_id": f"{key}-s21-video", "sha256": capture["video_sha256"]}
    ]
    ave_evidence = [
        evidence_object(
            optical_id,
            "four_emitter_optical_synchrony",
            f"A 120 fps S21 recording measured synchronized output across all four Nova emitters during the captured {capture['title']} interval.",
            ["light-emitter-1", "light-emitter-2", "light-emitter-3", "light-emitter-4"],
            {"start": 0, "end": capture["video_duration_seconds"]},
            [
                {"name": "video_frame_rate", "value": 120, "unit": "frames/second"},
                {"name": "frame_count", "value": capture["frame_count"], "unit": "count"},
                *[
                    {"name": f"emitter_{index}_rising_edges", "value": count, "unit": "count"}
                    for index, count in enumerate(capture["edge_counts"], 1)
                ],
                {"name": "same_frame_four_emitter_rising_edges", "value": capture["same_frame_edges"], "unit": "count"},
                {"name": "binary_disagreement_frames", "value": capture["disagreement_frames"], "unit": "count"},
                {"name": "binary_disagreement_fraction", "value": capture["disagreement_fraction"], "unit": "ratio"},
                {"name": "minimum_pairwise_luma_correlation", "value": capture["correlation_min"], "unit": "correlation"},
                {"name": "maximum_pairwise_luma_correlation", "value": capture["correlation_max"], "unit": "correlation"},
            ],
            {
                "camera": "Samsung Galaxy S21 Ultra 5G",
                "resolution": "1920x1080",
                "classification": "50x50 core-region mean luma threshold sweep",
                "first_on_video_ms": capture["first_on_ms"],
                "last_on_video_ms": capture["last_on_ms"],
            },
            {"source_id": f"{key}-s21-video", "input_sha256": capture["video_sha256"]},
            [
                "The approximately 8.33 ms frame interval cannot exclude subframe phase offsets.",
                "Camera exposures can miss narrow pulses between frames.",
                "The recording is not a calibrated intensity or duty-cycle measurement.",
                "The export describes only the recorded window, not unrecorded portions of the session.",
            ],
            [ble_id] if ble_id else [],
        )
    ]
    clocks = [
        {
            "clock_id": "optical-video-ms",
            "kind": "optical_measurement",
            "monotonic": True,
            "unit": "ms",
            "origin": "Start of the S21 recording.",
            "resolution_ms": 8.333333,
            "evidence_ids": [optical_id],
        }
    ]

    if capture["ble"]:
        ble = capture["ble"]
        evidence_ids.append(ble_id)
        source_hashes.extend(
            [
                {"source_id": f"{key}-btsnoop", "sha256": ble["btsnoop_sha256"]},
                {"source_id": f"{key}-bugreport", "sha256": ble["bugreport_sha256"]},
            ]
        )
        if "btsnoop_rotated_sha256" in ble:
            source_hashes.append(
                {"source_id": f"{key}-btsnoop-rotated", "sha256": ble["btsnoop_rotated_sha256"]}
            )
        clocks.append(
            {
                "clock_id": "ble-capture-ms",
                "kind": "ble_capture",
                "monotonic": True,
                "unit": "ms",
                "origin": "Observed active-state write in the Android Bluetooth HCI capture.",
                "resolution_ms": 0.001,
                "evidence_ids": [ble_id],
            }
        )
        ave_evidence.append(
            evidence_object(
                ble_id,
                "compact_ble_timing_stream",
                f"The captured {capture['title']} interval used only compact matched-timing BLE writes.",
                ["light-control"],
                {"start": 0, "end": ble["active_duration_seconds"]},
                [
                    {"name": "timing_write_count", "value": ble["timing_writes"], "unit": "count"},
                    {"name": "nonzero_timing_write_count", "value": ble["nonzero_timing_writes"], "unit": "count"},
                    {"name": "compact_12_byte_write_count", "value": ble["compact_writes"], "unit": "count"},
                    {"name": "extended_40_byte_write_count", "value": ble["extended_writes"], "unit": "count"},
                    {"name": "first_timing_write_delay", "value": ble["first_timing_delay_seconds"], "unit": "seconds"},
                ],
                {"runtime_app_version": "7.2.1", "timing_handle": "0x0034"},
                {"source_id": f"{key}-btsnoop", "input_sha256": ble["btsnoop_sha256"]},
                [
                    "BLE arrival timestamps are not optical-emission timestamps.",
                    "The capture does not establish behavior outside its recorded interval.",
                ],
            )
        )

    document = {
        "schema_version": "0.2.0",
        "ave_evidence_schema_version": "1.0.0",
        "export_id": stable_id("ln", f"{key}-empirical-capture-v0.2.0"),
        "created_at": "2026-09-22T21:19:53Z",
        "device": {
            "product": "Lumenate Nova",
            "app_package": "com.lumenate.lumenateaa",
            "app_version": "7.2.1",
            "app_version_code": 400,
            "firmware_version": capture["firmware_version"],
        },
        "session": {
            "session_id": capture["session_id"],
            "title": capture["title"],
            "duration_ms": capture["duration_ms"],
            "light_timeline_origin": {
                "clock_id": "optical-video-ms",
                "time_ms": 0,
                "definition": "Start of the physical measurement recording; not necessarily session-program zero.",
                "evidence_ids": [optical_id],
            },
            "audio_timeline_origin": None,
        },
        "audio_asset": {
            "identity_status": "unavailable",
            "source_id": None,
            "role": None,
            "sha256": None,
            "duration_ms": None,
            "sample_rate_hz": None,
            "limitations": ["No verified audio asset is included in this partial physical-capture export."],
        },
        "clocks": clocks,
        "segments": [
            {
                "segment_id": f"{key}-measured-light-window",
                "start_ms": capture["first_on_ms"],
                "end_ms": capture["last_on_ms"],
                "execution_layer": "physical_measurement",
                "intensity": None,
                "color_rgb": None,
                "pulse": {
                    "frequency_hz": None,
                    "duty_cycle": None,
                    "on_ms": None,
                    "off_ms": None,
                    "shape": "unknown",
                    "shape_detail": "Variable flashing was detected; this summary segment does not assert a constant waveform.",
                },
                "overlap_with_segment_ids": [],
                "command_ids": [],
                "evidence_ids": evidence_ids,
            }
        ],
        "transitions": [],
        "commands": [],
        "sync_anchors": [],
        "provenance": {
            "source_hashes": source_hashes,
            "acquisition_notes": capture["notes"]
            + ["Raw video, Bluetooth logs, bugreports, identifiers, and copyrighted audio remain local-only."],
        },
        "confidence": {
            "level": "L4",
            "score": 0.98,
            "method": "Direct four-region optical measurement, with simultaneous BLE confirmation where available.",
        },
        "limitations": [
            "This is a partial empirical capture export, not a complete program reconstruction.",
            "No verified audio identity or cross-modal synchronization anchor is available.",
            "The camera cannot exclude phase differences shorter than one approximately 8.33 ms frame.",
            "No calibrated optical intensity or physical duty-cycle measurement was made.",
        ],
        "ave_evidence": ave_evidence,
    }
    validate_document(document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="*", choices=sorted(CAPTURES), default=sorted(CAPTURES))
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for key in args.captures:
        output = args.output_dir / CAPTURES[key]["filename"]
        output.write_text(json.dumps(build_document(key), indent=2) + "\n", encoding="utf-8")
        print(f"wrote valid 0.2.0 export: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
