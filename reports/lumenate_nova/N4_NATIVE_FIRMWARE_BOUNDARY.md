# N4 native engine and Nova firmware boundary

## Finding

The Android native engine, not Nova firmware, evaluates app-session segment
arrays against a monotonic session clock and interpolates the current left/right
strobe parameters. When Nova is connected, native code emits an eight-value Java
callback once per strobe cycle; Android serializes those values to the recurring
BLE timing stream. Nova firmware receives current period/on-time parameters and
owns their physical execution, local brightness gain, emitter drive, and
mask-resident offline presets.

This closes the principal scheduling boundary without claiming knowledge of the
firmware's internal timers, buffering depth, interpolation, or safety checks.

## Native specimen

| Property | Value |
|---|---|
| Library | `libstrobecontroller-lib.so` |
| APK | Lumenate 7.2.1 ARM64 split |
| SHA-256 | `0580e57f9ebda51fa89851c3a40c18bda59e4eae5f9da18615fa01fb421a6b3e` |
| Size | 15,864 bytes |
| Format | Stripped AArch64 ELF shared object |
| Build ID | `59577327869c6826636406d7cff661d286195b82` |
| Analysis | Ghidra 12.1.2, AARCH64 little-endian, default compiler model |

The binary exports JNI entry points for `doStrobe`, pause, resume, stop,
media-position synchronization, headset connection, and headset disconnection.
Readable globals and strings name pause/stop/synchronization state, current time,
session origin, previous cycle onset, and the eight-value callback.

## Clock and interpolation

`doStrobe` copies the Java arrays into native storage and uses
`clock_gettime(CLOCK_MONOTONIC)` at microsecond resolution. For the active
segment it computes a bounded linear fraction:

```text
fraction = clamp((current_time - segment_start) /
                 (segment_end - segment_start), 0, 1)
value = start + fraction * (end - start)
```

The pattern is applied to frequency, duty, constant-on, and phase-related
left/right arrays. Frequency and duty determine microsecond on/off intervals.
Zero-frequency intervals advance against the same monotonic timeline and still
allow a headset callback carrying the remaining interpolated values.

The engine terminates at the end of the final interval, switches the phone torch
off if applicable, and sends an all-zero headset callback.

## Cycle scheduling and transport

When no headset is connected, the native loop directly toggles Android's camera
torch and waits against the monotonic clock for calculated on and off intervals.
When Nova is connected, the same cycle loop substitutes
`triggerHeadsetCallback(...)` for the torch-on action. That callback invokes
`onStrobeValuesChanged(DDDDDDDD)` in `LumenateSessionService`.

The Android Nova writer then:

1. rejects non-finite values;
2. suppresses an unchanged parameter object;
3. selects the compact matched-side or extended independent-side form;
4. converts frequency/duty to integer period and on-time fields; and
5. sends a little-endian Write Without Response packet.

Observed packet rates track the programmed flash rate, normally about 7–13.5
writes per second in Vitality, rather than a fixed 10 Hz control timer. This is
consistent with one callback opportunity per native strobe cycle. Millisecond
scheduling displacement between repeated runs is transport/runtime jitter; the
serialized period and on-time fields agree within one microsecond.

## Seek, pause, and resume

`syncMe(mediaPositionMs)` sets the native origin to monotonic-now minus the media
position and marks synchronization active. The running loop then locates the
segment containing that reconstructed session time before resuming normal
evaluation.

Pause records the monotonic pause instant. Resume shifts the session origin by
the elapsed pause duration, preserving program position. A restart instead
resets the origin to the current monotonic time. Stop sets both stop and pause
state and clears synchronization state. These native mechanics agree with the
captured zero packet/stream suppression on pause and resumed timing afterward.

## Responsibility assignment

| Behavior | Assigned layer | Support |
|---|---|---|
| Session definitions and endpoint arrays | App/session catalog | Current-version smali and parsed Vitality declaration |
| Session clock, seek correction, pause compensation | Native Android engine | ARM64 decompilation and runtime lifecycle agreement |
| Linear interpolation of current parameters | Native Android engine | Decompiled arithmetic plus declaration-to-BLE residuals |
| Per-cycle callback cadence | Native Android engine | Decompiled cycle loop plus frequency-dependent packet rate |
| Compact/extended framing and deduplication | Android BLE layer | Current-version serializer and HCI captures |
| Pulse generation from received period/on-time | Nova firmware | Necessary device-side execution boundary; physical output observed |
| Physical brightness buttons/local gain | Nova firmware | Button notifications without app echo or timing-field change |
| Offline Explore program | Nova firmware | Runs disconnected after one-byte preset selection |
| LED electrical drive and emitter output | Nova hardware/firmware | Physical measurement boundary |
| OTA image validation and boot policy | Bootloader/firmware, unresolved | App transport reconstructed; no package or installation captured |

## Buffering conclusion

The phone does not upload the complete observed app-session program to Nova.
It streams current timing parameters at cycle cadence. Nova must retain enough
state to execute a received period/on-time command, and it may continue, smooth,
or guard that state if a later packet is delayed, but the available captures do
not measure how long. No application-layer acknowledgement accompanies each
Write Command.

The offline presets are a separate firmware-resident path and must not be used
to infer buffering behavior for app-driven sessions.

## Confidence and limitations

- **L4, 0.99:** phone/native interpolation and current-parameter streaming,
  supported by decompiled arithmetic, callback framing, repeatability, and
  complete-session BLE agreement.
- **L4 with physical corroboration, 0.98:** Nova executes closely matching
  frequency and synchronous four-emitter timing in the measured sessions.
- **Unresolved:** device timer implementation, buffer timeout, packet-loss
  behavior, subframe left/right phase, calibrated duty/intensity, electrical
  limits, bootloader signature policy, rollback, and recovery behavior.
- Ghidra output is a reviewed derivative of a stripped optimized binary; names
  preserved in exports and strings are stronger than automatically inferred
  local variable types. Conclusions are cross-checked against smali and HCI
  behavior rather than resting on decompiler output alone.

