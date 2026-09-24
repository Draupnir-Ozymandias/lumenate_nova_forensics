# Lumenate Nova Forensics

An independent, evidence-first workstream for reconstructing how the Lumenate Android application controls the Nova light mask.

This project owns APK analysis, Bluetooth Low Energy (BLE) traffic, device commands, native timing behavior, session reconstruction, firmware constraints, and physical validation. It does not become part of the AVE codebase. Integration occurs through versioned JSON exports that AVE validates and imports.

## Current position

The baseline and current app versions (`7.0.0` and `7.2.1`) have been acquired,
and the investigation now includes empirical BLE and optical capture. It has
established:

- a native Android Kotlin/Java application using Jetpack Compose;
- five DEX files in the 7.0.0 baseline and six in the current 7.2.1 build,
  compiled/obfuscated with R8;
- a native strobe engine in `libstrobecontroller-lib.so`;
- JNI entry points linking `StrobeManager` to frequency and on/off timing state;
- a low-latency Nova BLE connection and three custom notification characteristics;
- complete-session Vitality declaration and BLE reconstruction under released
  contract `0.2.0`;
- physical four-emitter synchrony measurements for Vitality, Deep Exploration,
  Spirit, and the offline Explore preset;
- a simultaneous Vitality BLE/audio/video clock bridge with bounded 20 ms
  audio/video anchors;
- a firmware 1.0.4 forced-disconnect watchdog measurement showing a short
  three-cycle hold followed by light-off; and
- an active server-mediated MCUmgr/SMP firmware-update path in Android 7.2.1.

See [PROJECT.md](PROJECT.md) for the operating model, [ROADMAP.md](ROADMAP.md) for milestones, [reports/lumenate_nova/N0_RECONNAISSANCE.md](reports/lumenate_nova/N0_RECONNAISSANCE.md) for the evidence baseline, and [reports/lumenate_nova/EVIDENCE_STATUS_2026-09-22.md](reports/lumenate_nova/EVIDENCE_STATUS_2026-09-22.md) for the consolidated current assessment.

The simultaneous clock-bridge result is documented in
[physical_validation/AUDIO_CORRELATED_VITALITY_2026-09-24.md](physical_validation/AUDIO_CORRELATED_VITALITY_2026-09-24.md).

## Repository map

```text
methodology/                   Scope, evidence levels, legal and safety rules
specimens/                     Local-only original APKs and acquisition metadata
static/                        Local-only generated static-analysis output
dynamic/                       Local-only raw logs and packet captures
protocol_reconstruction/      Reviewed protocol models and sanitized exports
physical_validation/          Measurement plans and reviewed optical results
contracts/                    Versioned Lumenate and AVE JSON contracts
reports/                       Sanitized milestone findings
tools/                         Reproducible acquisition/analysis utilities
```

Raw or proprietary evidence stays outside Git. Every publishable conclusion must point to a source hash, acquisition record, reviewed derivative, confidence level, and stated limitation.

## Immediate work

1. Monitor app/content/firmware changes and capture again only when a diff
   exposes a new program, extended command, native library, or firmware.
2. Repeat calibrated packet-to-photon work when a suitable optical sensor is
   available.

The N0 acquisition milestone is closed. See
`reports/lumenate_nova/N0_CLOSEOUT_MANIFEST.md`,
`reports/lumenate_nova/N0_INVENTORIES.md`, and
`reports/lumenate_nova/NEXT_STEPS_WITHOUT_PHOTODIODE.md`.

## AVE boundary

AVE owns signal analysis, evidence indexing, comparisons, clustering, scoring, and multimodal interpretation. This project exports device facts and reconstructions; AVE consumes them. Repositories should remain independently versioned and should use contract tests to detect schema drift.
