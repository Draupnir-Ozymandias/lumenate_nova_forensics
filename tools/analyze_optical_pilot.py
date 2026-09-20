#!/usr/bin/env python3
"""Analyze four fixed LED regions from the S21 120 fps optical pilot."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "dynamic/lumenate_nova/optical/2026-09-20_s21-pilot/analysis"


def read_series(path: Path) -> tuple[list[float], list[float], list[int]]:
    times: list[float] = []
    averages: list[float] = []
    maxima: list[int] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            times.append(float(row[0]))
            averages.append(float(row[1]))
            maxima.append(int(row[2]))
    return times, averages, maxima


def correlation(left: list[float], right: list[float]) -> float:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return numerator / denominator


def rising_edges(states: list[bool]) -> list[int]:
    return [index for index in range(1, len(states)) if states[index] and not states[index - 1]]


def analyze(directory: Path, threshold: float = 30.0) -> dict[str, Any]:
    series = [read_series(directory / f"062014-led{index}.csv") for index in range(1, 5)]
    times = series[0][0]
    if any(item[0] != times for item in series[1:]):
        raise ValueError("LED region timestamps do not match")
    averages = [item[1] for item in series]
    maxima = [item[2] for item in series]
    states = [[value > threshold for value in values] for values in averages]
    frame_deltas = [right - left for left, right in zip(times, times[1:])]
    first_on_indices = [next(index for index, state in enumerate(values) if state) for values in states]
    last_on_indices = [len(values) - 1 - next(index for index, state in enumerate(reversed(values)) if state) for values in states]
    mismatch_indices = [
        index
        for index, values in enumerate(zip(*states))
        if len(set(values)) != 1
    ]
    correlations = {
        f"led{left + 1}_led{right + 1}": correlation(averages[left], averages[right])
        for left in range(4)
        for right in range(left + 1, 4)
    }

    # Map first observed illumination to the declaration's 1.5-second onset.
    origin = statistics.median(times[index] for index in first_on_indices) - 1.5
    constant_start = origin + 37.0
    constant_end = origin + 56.0
    constant_indices = [
        index for index, time in enumerate(times) if constant_start <= time < constant_end
    ]
    constant_rates: list[float] = []
    constant_duties: list[float] = []
    for led_states in states:
        window_states = [led_states[index] for index in constant_indices]
        edges = rising_edges(window_states)
        edge_times = [times[constant_indices[index]] for index in edges]
        time_mean = statistics.fmean(edge_times)
        index_mean = (len(edge_times) - 1) / 2
        numerator = sum(
            (time - time_mean) * (index - index_mean)
            for index, time in enumerate(edge_times)
        )
        denominator = sum((time - time_mean) ** 2 for time in edge_times)
        constant_rates.append(numerator / denominator)
        constant_duties.append(sum(window_states) / len(window_states))

    return {
        "frame_count": len(times),
        "duration_seconds": times[-1] - times[0],
        "frame_interval_ms": {
            "median": statistics.median(frame_deltas) * 1000,
            "maximum": max(frame_deltas) * 1000,
        },
        "threshold_yavg": threshold,
        "first_on_seconds": [times[index] for index in first_on_indices],
        "last_on_seconds": [times[index] for index in last_on_indices],
        "maximum_y": [max(values) for values in maxima],
        "pairwise_yavg_correlations": correlations,
        "binary_state_mismatch_frames": len(mismatch_indices),
        "binary_state_mismatch_fraction": len(mismatch_indices) / len(times),
        "constant_segment_video_range_seconds": [constant_start, constant_end],
        "constant_segment_frequency_hz": constant_rates,
        "constant_segment_frame_duty_fraction": constant_duties,
        "limitations": [
            "Frame-duty fraction is exposure-integrated and is not a direct physical duty-cycle measurement.",
            "The first detected illuminated frame bounds onset only to one camera-frame interval.",
            "Rolling-shutter scan timing is not calibrated.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--threshold", type=float, default=30.0)
    args = parser.parse_args()
    print(json.dumps(analyze(args.directory, args.threshold), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
