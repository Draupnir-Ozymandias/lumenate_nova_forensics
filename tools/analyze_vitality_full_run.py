#!/usr/bin/env python3
"""Compare a full Vitality BLE timing capture with the declared schedule."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics
import struct
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_vitality_empirical_export import extract_vitality_program
from tools.strobe_program import Segment, parse_program, value_at


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WRITES = (
    ROOT
    / "dynamic/lumenate_nova/runs/2026-09-19_vitality-full-5min/app-writes.tsv"
)


def _segment_at(segments: list[Segment], time_s: float) -> tuple[int, Segment]:
    for index, segment in enumerate(segments, 1):
        if segment.start_s <= time_s < segment.end_s:
            return index, segment
    raise ValueError(f"time {time_s} is outside the declared program")


def analyze(path: Path) -> dict[str, Any]:
    segments = parse_program(extract_vitality_program())
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="|"))

    active_rows = [
        row for row in rows if row["btatt.handle"] == "0x0039" and row["btatt.value"] == "0a"
    ]
    if len(active_rows) != 1:
        raise ValueError(f"expected one active-state write, found {len(active_rows)}")
    active_epoch = float(active_rows[0]["frame.time_epoch"])

    timing_rows = [row for row in rows if row["btatt.handle"] == "0x0034"]
    nonzero_rows = [row for row in timing_rows if int(row["btatt.value"], 16) != 0]
    if not nonzero_rows:
        raise ValueError("no nonzero timing writes")
    first_epoch = float(nonzero_rows[0]["frame.time_epoch"])
    last_epoch = float(nonzero_rows[-1]["frame.time_epoch"])
    final_zero = next(
        row
        for row in timing_rows
        if float(row["frame.time_epoch"]) > last_epoch and int(row["btatt.value"], 16) == 0
    )
    final_zero_epoch = float(final_zero["frame.time_epoch"])

    # The first nonzero write corresponds to the declaration's 1.5 s onset.
    frequency_errors: list[float] = []
    duty_errors: list[float] = []
    observed_segments: set[int] = set()
    for row in nonzero_rows:
        elapsed_from_first = float(row["frame.time_epoch"]) - first_epoch
        program_time = 1.5 + elapsed_from_first
        index, segment = _segment_at(segments, program_time)
        if segment.frequency.is_off or segment.duty.is_off:
            raise ValueError(f"nonzero write mapped to off segment {index}")
        fraction = (program_time - segment.start_s) / (segment.end_s - segment.start_s)
        expected_frequency = value_at(segment.frequency, fraction)
        expected_duty = value_at(segment.duty, fraction)
        period_us, on_time_us, constant_on_ppm = struct.unpack(
            "<III", bytes.fromhex(row["btatt.value"])
        )
        if constant_on_ppm != 0:
            raise ValueError(f"unexpected constant-on field in frame {row['frame.number']}")
        observed_frequency = 1_000_000.0 / period_us
        observed_duty = on_time_us / period_us
        assert expected_frequency is not None and expected_duty is not None
        frequency_errors.append(observed_frequency - expected_frequency)
        duty_errors.append(observed_duty - expected_duty)
        observed_segments.add(index)

    declared_active = {
        index for index, segment in enumerate(segments, 1) if not segment.frequency.is_off
    }
    inactive_rows = [
        row for row in rows if row["btatt.handle"] == "0x0039" and row["btatt.value"] == "00"
    ]
    first_inactive_epoch = float(inactive_rows[0]["frame.time_epoch"])
    return {
        "source": str(path.relative_to(ROOT)),
        "active_epoch": active_epoch,
        "first_nonzero_after_active_ms": round((first_epoch - active_epoch) * 1000, 3),
        "nonzero_timing_write_count": len(nonzero_rows),
        "last_nonzero_after_active_ms": round((last_epoch - active_epoch) * 1000, 3),
        "final_zero_after_active_ms": round((final_zero_epoch - active_epoch) * 1000, 3),
        "first_inactive_after_active_ms": round((first_inactive_epoch - active_epoch) * 1000, 3),
        "active_segment_count": len(declared_active),
        "observed_active_segment_count": len(observed_segments),
        "missing_active_segment_ids": sorted(declared_active - observed_segments),
        "frequency_error_hz": {
            "mean_absolute": statistics.fmean(abs(value) for value in frequency_errors),
            "maximum_absolute": max(abs(value) for value in frequency_errors),
        },
        "duty_cycle_error": {
            "mean_absolute": statistics.fmean(abs(value) for value in duty_errors),
            "maximum_absolute": max(abs(value) for value in duty_errors),
        },
        "alignment_method": "Map first nonzero BLE timing write to declared program time 1.500 s.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("writes", nargs="?", type=Path, default=DEFAULT_WRITES)
    args = parser.parse_args()
    print(json.dumps(analyze(args.writes), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
