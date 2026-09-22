# Lumenate Nova Forensics

An independent, evidence-first workstream for reconstructing how the Lumenate Android application controls the Nova light mask.

This project owns APK analysis, Bluetooth Low Energy (BLE) traffic, device commands, native timing behavior, session reconstruction, firmware constraints, and physical validation. It does not become part of the AVE codebase. Integration occurs through versioned JSON exports that AVE validates and imports.

## Current position

The baseline and current app versions (`7.0.0` and `7.2.1`) have been acquired,
and the investigation now includes empirical BLE and optical capture. It has
established:

- a native Android Kotlin/Java application using Jetpack Compose;
- five DEX files compiled/obfuscated with R8;
- a native strobe engine in `libstrobecontroller-lib.so`;
- JNI entry points linking `StrobeManager` to frequency and on/off timing state;
- a low-latency Nova BLE connection and three custom notification characteristics;
- complete-session Vitality declaration and BLE reconstruction under contract
  candidate `0.2.0`;
- physical four-emitter synchrony measurements for Vitality, Deep Exploration,
  Spirit, and the offline Explore preset; and
- an active server-mediated MCUmgr/SMP firmware-update path in Android 7.2.1.

See [PROJECT.md](PROJECT.md) for the operating model, [ROADMAP.md](ROADMAP.md) for milestones, and [reports/lumenate_nova/N0_RECONNAISSANCE.md](reports/lumenate_nova/N0_RECONNAISSANCE.md) for the evidence baseline.

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

1. Preserve and release the candidate `0.2.0` producer/consumer contract fixtures.
2. Acquire a firmware package through the ordinary update-check workflow without
   initiating installation, then hash and inspect its manifest and payloads.
3. Add verified audio/light anchors for additional sessions before cross-modal
   comparisons are generalized.
4. Reserve a controlled OTA capture for a separately approved experiment with
   uninterrupted power and recovery contingencies.

## AVE boundary

AVE owns signal analysis, evidence indexing, comparisons, clustering, scoring, and multimodal interpretation. This project exports device facts and reconstructions; AVE consumes them. Repositories should remain independently versioned and should use contract tests to detect schema drift.
