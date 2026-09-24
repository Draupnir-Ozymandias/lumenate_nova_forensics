# Roadmap and milestones

Milestones are evidence gates, not calendar promises. Work may overlap, but a milestone closes only when its exit criteria are met.

## N0 — Acquisition and APK reconnaissance

**Status:** closed 2026-09-22.

Completed evidence includes the three split APK hashes, package/build inventory,
the five-DEX 7.0.0 baseline and six-DEX 7.2.1 build, R8 detection,
native-library inventory, initial JNI symbols, process-specific runtime logs,
BLE connection observations, custom characteristic UUIDs, and the current Nova
hardware/firmware revisions.

Closeout produced reviewed permission, SDK, endpoint, asset, database, content,
native-library, tool, acquisition, privacy, and Git-history inventories. The
historical ARM APKiD invocation is indeterminate and is not presented as a clean
scan; verified extraction and Ghidra analysis supersede it for the N0 inventory.
No tracked raw evidence or credential-shaped text required remediation.

**Exit gate:** met. A reviewer can reproduce the baseline from local specimens
using hashes and documented methods without needing raw evidence in Git.

## N1 — Strobe and BLE control-path reconstruction

**Status:** bounded end-to-end report published; native scheduling details remain.

Trace the semantic bridge from session models to native timing and BLE writes.

Targets:

- declaration and call sites of `StrobeManager.doStrobe`;
- names, types, and origins of all array arguments;
- `onStrobeValuesChanged` and headset callback receivers;
- all references to the three custom UUIDs;
- writable characteristic, packet builder, and write queue;
- start, intensity, pause, resume, stop, connect, and disconnect paths.

**Exit gate:** a reviewed call graph maps session input → JNI/native state → packet construction → GATT write, with unknown edges identified.

## N2 — BLE protocol and device state machine

**Status:** core session-control path, characteristic audit, and firmware 1.0.4
forced-disconnect watchdog behavior documented; isolated loss and reconnect
behavior remain.

Capture one-variable-at-a-time experiments and infer framing semantics.

Targets:

- service/characteristic property table (complete for the reviewed GATT map;
  `0x001f` is explicitly bounded as current-app-unused with unknown semantics);
- command framing, byte order, counters, checksums, acknowledgements, and notifications;
- connection lifecycle and recovery behavior;
- distinction between streamed timing, buffered blocks, and state/status traffic;
- reproducible capture procedures for each user action.

**Exit gate:** a command dictionary and state machine reproduce observed start/control/stop exchanges across at least three captures.

## N3 — Session, segment, and synchronization reconstruction

**Status:** closed for the bounded Vitality `0.2.0` export.

Join app session data, native timing state, BLE traffic, and audio timing.

Targets:

- session/segment definitions and transition rules;
- intensity, color, frequency, on/off time, and duty-cycle timelines;
- audio/light synchronization anchors and drift estimates;
- confidence-scored interpretations and alternative hypotheses;
- first `lumenate-protocol-export` example.

**Exit gate:** one complete session timeline is internally consistent and validates against the project JSON schema.

## N4 — Native engine and firmware boundary

**Status:** bounded native/firmware responsibility report complete; device-side
buffering and boot/update validation policy remain unresolved.

Use Ghidra and focused runtime instrumentation only after N1 establishes semantics.

Targets:

- map `StrobeController` fields and callback arguments;
- determine interpolation, scheduling, and synchronization behavior;
- identify what executes on phone versus mask firmware;
- characterize update/firmware interfaces without bypassing access controls;
- document timing and platform constraints.

**Exit gate:** responsibility for generation, scheduling, buffering, and emission is assigned to app/native/transport/firmware layers with evidence and limitations.

## N5 — Physical validation

**Status:** provisional camera validation and one bounded BLE/audio/video common
clock are complete; calibrated photon-level measurement remains open.

Compare reconstructed intent with emitted light.

Targets:

- calibrated photodiode/ADC or oscilloscope setup;
- optical frequency, duty cycle, intensity, transition, and color measurements;
- synchronized audio, BLE, app, and optical clocks (bounded camera/audio bridge
  complete; calibrated photon timing remains open);
- error distributions across repetitions and selected operating conditions;
- explicit safety procedure for photosensitive exposure.

**Exit gate:** at least one session has a declared → commanded → emitted comparison with quantified timing and measurement uncertainty.

## N6 — AVE integration and release

**Status:** `0.2.0` producer/consumer release complete; later changes require a
new semantic version.

Publish validated device evidence without merging repositories.

Targets:

- pin AVE evidence schema `1.0.0`;
- validate every export in both producer and consumer repositories;
- implement a small AVE device-protocol importer;
- add golden fixtures and schema-drift contract tests;
- version release notes, provenance, and limitations.

**Exit gate:** AVE imports a Lumenate export, preserves evidence IDs/provenance, and rejects incompatible schema versions.

## Parallel program view

| Stream | Near term | Middle | Integration |
|---|---|---|---|
| AVE | Corpus Evidence Index; Golden Ratio pilot | Comparison, clustering, scoring | Validate/import device evidence |
| Lumenate | N0 closeout; N1 control path | N2–N5 reconstruction and validation | Publish versioned protocol evidence |
