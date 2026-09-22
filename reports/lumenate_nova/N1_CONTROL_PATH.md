# N1 Nova strobe and BLE control path

## Finding

The Android 7.2.1 control path is now traceable from a selected session's
declarative strobe program through the native timing engine to recurring BLE
writes. The app does not upload the entire observed program to Nova. During an
active session it receives calculated left/right strobe values from native code,
serializes the current values, and streams changed timing packets to the mask.

The bounded chain has L4 transport confirmation. Native scheduling internals and
the device's final timer/LED implementation remain below the established
boundary.

## Reviewed control chain

1. The session catalog associates each selected duration with an audio asset and
   a separate compact strobe-program string. The Vitality 5-minute declaration,
   for example, parses into 34 contiguous segments from program time zero through
   300 seconds.
2. `LumenateSessionService` starts and controls `StrobeManager`, whose native
   methods include `doStrobe`, `syncMe`, pause, resume, and stop. Media-position
   discontinuities pass the integer ExoPlayer position directly to
   `syncMe(positionMs)`.
3. The native engine calls `NativeStrobeManagerCallback.onStrobeValuesChanged`
   with eight doubles. The service's retained `StrobeParams` labels them as left
   and right frequency, duty, constant-on value, and phase shift.
4. `LumenateSessionService.onStrobeValuesChanged` rejects values when the session
   is inactive or pausing, converts the callback values to the float parameter
   object, and forwards active values to the Nova controller.
5. The Nova writer validates finite values and suppresses unchanged parameter
   objects. For matched sides it builds three 32-bit integers; when both sides
   are active and materially differ it can build ten integers.
6. The integers are serialized little-endian and written to the timing
   characteristic. Captures show 12-byte Write Commands during active sessions,
   normally at roughly 10–11 updates per second as interpolated values change.
7. The mask receives session-state commands separately. Active/start or resume
   uses `0a`; pause/stop uses `00`. Pause suppresses timing writes until resume,
   while stop terminates the stream.

## Compact timing packet

The observed 12-byte form is three little-endian 32-bit integers:

| Offset | Meaning | Conversion |
|---:|---|---|
| 0 | left period | `round((1 / frequency_hz) * 1,000,000)` µs |
| 4 | left on-time | `round(duty_cycle * period_us)` µs |
| 8 | left constant-on | `round(constant_on * 1,000,000)` |

This mapping is established by the current-version serializer and independently
confirmed by decoding controlled and complete-session HCI captures. Across the
natural five-minute Vitality run, the decoded stream covered all 32 declared
active segments with mean absolute errors of 0.000903 Hz and 0.000049 duty
relative to the declaration.

The unobserved extended form contains ten little-endian integers derived from
left/right periods, on-times, constant-on values, and phase-related values. Its
code path establishes independent-side protocol capability, but no reviewed
built-in capture exercised it.

## State and synchronization behavior

| Action | Native/app behavior | Observed BLE behavior |
|---|---|---|
| Start | Start media/session and native strobe computation | `0a` state write followed by timing stream after any declared dark introduction |
| Pause | Pause path suppresses callback forwarding | `00`, zero timing packet, then no timing writes |
| Resume | Resume native computation against current session/media position | `0a`, then timing stream resumes |
| Seek/nonzero start | Pass media position to `syncMe(positionMs)` | Subsequent timing values reflect the synchronized program position |
| Stop | Stop native strobe computation and session | Zero timing packet and `00` state write(s) |

Start and resume share the same observed state value, as do pause and stop.
Their semantic distinction comes from surrounding service state and whether the
timing stream later resumes; it is not encoded by a unique one-byte opcode.

## Responsibility boundary

| Layer | Established responsibility |
|---|---|
| Session declaration | Segment bounds and frequency/duty expressions |
| Media/service layer | Playback lifecycle, media-position synchronization, pause/resume/stop gating |
| Native engine | Time-varying evaluation and callback production |
| BLE serializer | Deduplication, compact/extended selection, numeric conversion, little-endian framing |
| BLE transport | Recurring current-value delivery and separate active-state control |
| Nova firmware | Applying timing commands, local brightness gain, emitter drive, and offline presets |

The captures support streamed current parameters rather than a complete program
upload. They do not reveal the firmware scheduler's buffering depth, precise
command-to-photon latency, PWM implementation, or recovery behavior after a
missed write.

## Evidence and provenance

| Reviewed derivative | SHA-256 | Role |
|---|---|---|
| `LumenateSessionService.smali` | `9f722e6fb8bf190f900c46e17da15525790c0146215e79377e75ba7c2ef2ce41` | Lifecycle, native callback, synchronization |
| `services/d.smali` | `0e17fc1d20e4abf0fab4c002224de5703adec99374ad268d04b4ce444c2057fb` | Eight named strobe parameters |
| `common/v0.1.smali` | `8633d7777595ed608a7a09205236b22702449fd5317527995250213c46592742` | Compact/extended serializer and BLE write path |
| `StrobeManager.smali` | `473dfa8f4a84884101ba3c59f632ad7548521e2c0ff5d75b7553fabe5dd1e1e3` | Native entry points |
| `NativeStrobeManagerCallback.smali` | `92eff6f3f174c67718d948332ec5c66dcffeb45a3a86441832b6c7ec09eb8346` | Eight-double callback boundary |
| Controlled start/pause/resume/stop HCI | `1004fc22f71a95b54bddd7d8c25ebb98014fbae7354005c561ce1cadf46d1f82` | Runtime state transitions |
| Brightness-sequence HCI | `8006055e6a55e911e8ea80de255c758b343e5046395fc4dcb7df1da84a8fa0ce` | Timing decode and local-button separation |
| Vitality repeatability HCI | `a3a2073a2dbd1fe4d3bec2993f62b97d14e8f196f9089732bef915a59bbfbfbc` | Determinism and declaration agreement |

Static derivatives are from the acquired Android 7.2.1 package. The controlled
September 17 captures used Android 7.0.0; the relevant Vitality declaration and
`StrobeManager` were later verified byte-for-byte identical in 7.2.1, and the
complete September 19 run used 7.2.1 directly.

## Confidence and limits

- **Level:** L4 transport confirmation.
- **Score:** 0.98 for the bounded Vitality chain.
- **Method:** current-version static data flow, controlled lifecycle captures,
  cross-run repeatability, and full-duration declaration-to-packet residuals.
- **Alternative retained:** firmware may smooth, buffer, or otherwise transform
  received values before emission.
- **Not established:** native timer implementation, exact write scheduling rule,
  extended-form field behavior in a live run, packet-loss response, calibrated
  duty/intensity, and packet-to-photon latency.

