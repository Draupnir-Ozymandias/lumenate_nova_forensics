# Highest-value next steps without a photodiode

## Recommendation

Stop broad track scouting. The existing-evidence characteristic audit was
completed on 2026-09-23. The best return now is to improve cross-clock alignment
with the S21's audio channel and then probe Nova's app-stream timeout safely.
Neither substitutes for calibrated N5 optical measurement, but each resolves a
specific open architecture question.

| Rank | Experiment | Expected information gain | Effort / risk |
|---:|---|---|---|
| Done | Resolve remaining custom BLE characteristic roles from existing HCI and smali | Closed three roles and bounded `0x001f` as current-app-unused | Completed 2026-09-23 |
| Done | Build an audio-correlated packet-to-video clock bridge | Established one bounded BLE/audio/video timeline over 98 seconds of Vitality | Completed 2026-09-24 |
| Done | Measure stream interruption and hold behavior | Bounded firmware 1.0.4 link-loss hold to roughly three observed 10.5 Hz cycles | Completed 2026-09-24 |
| 4 | Add version/content drift detection | Makes future independent-side content, protocol, or firmware changes obvious | Low recurring effort / none |
| 5 | Seek first-party technical clarification | Could answer independent-channel availability and update policy directly | Low / uncertain response |

## 1. Custom-characteristic dictionary — completed

The 2026-09-23 audit assigned `0x001d` to the Welcome LEDs command, `0x002e`
to offline-session selection/state, and `0x0031` to the offline-session header.
It bounded `0x001f` as firmware-exposed but unused by Android 7.2.1 and silent
in all reviewed captures. See `BLE_CHARACTERISTIC_AUDIT.md` and the durable
`protocol_reconstruction/lumenate_nova/service-map.json`.

## 2. Audio as the common clock bridge — completed

The S21 records video and audio on one media timeline. For an app session whose
exact audio asset is lawfully acquired through the app's ordinary offline
download, cross-correlate the S21 soundtrack with that hashed reference asset.
Relate the reference-audio position to the app/native media-position anchors and
the simultaneous A35 HCI timeline. This provides a common BLE/audio/video clock
without asserting photon precision.

Best procedure for one short run:

1. keep the mask stationary, unworn, and framed into four fixed emitter regions;
2. start S21 1080p/120 fps video before starting the app session;
3. record A35 HCI for the same run, with unrelated Bluetooth devices absent;
4. use a downloaded, hash-identified session asset and retain the S21 audio;
5. align reference audio to recorded audio by correlation, then map BLE timing
   through the app/media anchors; and
6. report camera-frame quantization, exposure/rolling-shutter limits, audio
   resampling uncertainty, HCI clock uncertainty, and the combined bound.

The 2026-09-24 run completed this step. It captured 772 nonzero BLE timing
writes, a 118.529-second S21 audio/video recording, and 14,223 optical frames.
Cross-correlation against the verified Vitality asset established two
audio/video anchors with 20 ms uncertainty. All four emitter regions produced
963 rising edges, 960 of which occurred on the same frame. See
`physical_validation/AUDIO_CORRELATED_VITALITY_2026-09-24.md`.

The result tests commanded frequency and observed frame timing on one common
clock. It still cannot measure absolute optical intensity, true pulse width,
subframe left/right phase, or calibrated electrical/packet-to-photon latency.

## 3. Nova live-stream hold/watchdog behavior — completed

Use a short, steady app-driven segment at a clearly identifiable frequency.
While the S21 records, interrupt the A35–Nova link in a controlled, reversible
way—prefer an app disconnect or phone Bluetooth-off action, not RF interference
or power interruption. Measure whether emission stops immediately, holds the
last period/on-time command, fades, or changes to a safe state, and for how long.
Repeat once for confirmation.

The 2026-09-24 controlled run completed this step. Bluetooth was disabled at
Vitality media position 45.017 seconds while Nova held a 10.5 Hz / 20% command.
No normal zero-timing or inactive-state write was sent. All four emitters
produced three additional synchronized rising edges, with the last illuminated
frame approximately 229 ms after the mapped HCI disconnect, and then remained
dark. Lumenate paused automatically after link loss. See
`DISCONNECT_HOLD_BEHAVIOR.md`.

## 4. Monitor changes instead of sampling more current tracks

For each future app acquisition, automatically diff:

- package/version, signer, splits, DEX and native-library hashes;
- the 128-session constructor audit and any non-null right-hand programs;
- compact versus extended BLE serializer code;
- custom UUIDs and firmware-update paths;
- content titles/durations and referenced media identities; and
- hardware/firmware revision shown by the ordinary app workflow.

Trigger a targeted HCI+S21 capture only when a diff exposes a new right-hand
program, extended 40-byte command use, new offline preset, changed native
library, or new firmware. This is much higher yield than visually trying tracks
from the unchanged 7.2.1 catalog.

## 5. Ask the questions only the vendor can cheaply answer

A concise, non-adversarial inquiry can ask whether firmware 1.0.4 currently
ships any four-emitter spatial sequence, whether the John Lennon mixes use
independent channels on Nova, whether spatial sequences are server-delivered,
and whether firmware checks expose release notes or a current-version endpoint.
Any answer remains a vendor statement until corroborated, but it can determine
whether more capture work is warranted.

## Defer for now

- additional random track videos from the unchanged catalog;
- longer repetitions of already synchronous Vitality, Deep Exploration,
  Spirit, or offline Explore;
- camera-based claims about absolute brightness, color, duty cycle, or phase
  below 8.33 ms;
- OTA installation or induced update failure without a recovery plan; and
- protocol injection merely to force the 40-byte path, unless separately scoped
  with device-safety limits.

The next low-risk engineering task is version/content drift detection. A
photodiode/ADC later remains the correct tool for calibrated packet-to-photon
latency, pulse shape, duty cycle, and independent-emitter phase.
