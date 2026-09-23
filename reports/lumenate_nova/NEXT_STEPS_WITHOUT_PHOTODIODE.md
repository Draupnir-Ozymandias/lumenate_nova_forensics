# Highest-value next steps without a photodiode

## Recommendation

Stop broad track scouting. The best return now is a short program that extracts
new information from existing artifacts, improves cross-clock alignment with
the S21's audio channel, and probes Nova's app-stream timeout safely. None of
these substitutes for calibrated N5 optical measurement, but each resolves a
specific open architecture question.

| Rank | Experiment | Expected information gain | Effort / risk |
|---:|---|---|---|
| 1 | Resolve remaining custom BLE characteristic roles from existing HCI and smali | Closes N2 command/state gaps without another capture | Low / none to hardware |
| 2 | Build an audio-correlated packet-to-video clock bridge | Converts existing or one short S21+A35 capture into a bounded common timeline | Medium / low |
| 3 | Measure stream interruption and hold behavior | Directly bounds Nova's app-session buffering/watchdog behavior | Medium / controlled hardware experiment |
| 4 | Add version/content drift detection | Makes future independent-side content, protocol, or firmware changes obvious | Low recurring effort / none |
| 5 | Seek first-party technical clarification | Could answer independent-channel availability and update policy directly | Low / uncertain response |

## 1. Finish the custom-characteristic dictionary first

Re-index existing captures against all reads, writes, notifications, connection
events, button presses, battery observations, offline-preset selection, and
firmware checks. Then trace the remaining UUID references in current-version
smali. The deliverable should assign or bound the roles still labeled by handles
or suffixes, especially `0x1d`, `0x1f`, `0x2e`, and `0x31`, with negative
evidence where a characteristic remained silent.

Why this is first: it consumes no device time, avoids optical uncertainty, and
improves every later transport experiment. It should precede collection of more
sessions because otherwise new captures merely reproduce already understood
compact timing writes.

## 2. Use audio as the common clock bridge

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

This can test whether commanded transitions and observed frame transitions are
consistent to roughly a video-frame scale. It cannot measure absolute optical
intensity, true pulse width, subframe left/right phase, or electrical latency.

## 3. Bound Nova's live-stream hold/watchdog behavior

Use a short, steady app-driven segment at a clearly identifiable frequency.
While the S21 records, interrupt the A35–Nova link in a controlled, reversible
way—prefer an app disconnect or phone Bluetooth-off action, not RF interference
or power interruption. Measure whether emission stops immediately, holds the
last period/on-time command, fades, or changes to a safe state, and for how long.
Repeat once for confirmation.

This directly addresses N4's largest firmware-boundary unknown: how much command
state Nova retains and what it does when a cycle-cadence stream disappears. Keep
the mask unworn and pointed away from people; abort on heating, unexpected
behavior, or failure to reconnect. This experiment does not require an OTA,
firmware modification, or protocol injection.

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

The recommended immediate sequence is: existing-evidence characteristic audit,
then one audio-correlated S21+A35 run, then one controlled disconnect run. A
photodiode/ADC later remains the correct tool for calibrated packet-to-photon
latency, pulse shape, duty cycle, and independent-emitter phase.
