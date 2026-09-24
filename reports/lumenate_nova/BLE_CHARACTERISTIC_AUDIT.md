# Nova BLE characteristic audit

## Result

The offline audit resolves three of the four previously unassigned Nova
characteristics. The fourth is now bounded as firmware-exposed but unused by
the acquired Android app and silent in every reviewed capture; its semantics
remain unknown rather than being inferred from adjacency.

| Handle | Characteristic | Properties | Audited role | Confidence |
|---:|---|---|---|---|
| `0x001d` | `3e25a3bf-bfe1-4c71-97c5-5bdb73fac89e` | Write Without Response | Welcome-LED command; current app payload `01 00` | L2 static, 0.98 |
| `0x001f` | `2b35ef1f-11a6-4089-8cd5-843c5d0c9c55` | Read, Write Without Response, Notify | Firmware-exposed, current-app-unused characteristic; exact role unresolved | L1 presence, 1.00; semantics unknown |
| `0x002e` | `2a84aaff-6738-4629-894c-346357b89a0c` | Read, Write Without Response, Notify | Offline-session selection and selected-state value | L4, 0.99 |
| `0x0031` | `51bfc219-feab-4227-8b93-8af8cc5306d4` | Read | Nova offline-session header | L4, 0.99 |

Handles describe the reviewed firmware 1.0.4 GATT layout and are not protocol
identifiers. UUIDs are the durable identifiers.

## Method

The audit cross-correlated:

- all ten standalone HCI files acquired from 2026-09-17 through 2026-09-21;
- the current and rotated HCI logs embedded in the 2026-09-22 firmware-check
  bugreport;
- GATT discovery records and characteristic properties;
- direct ATT reads, writes, notifications, and CCCD changes;
- Android 7.2.1 UUID constants, callers, serializers, and response parsers; and
- the operator-observed Explore selection in the app.

Several Android snoop files contain cumulative earlier traffic. Repeated packet
prefixes were treated as the same historical observations, not independent
replications. Device addresses and the mask serial number are excluded.

## `0x001d`: Welcome LEDs command

Android 7.2.1 binds service `47bbfb1e-670e-4f81-bfb3-78daffc9a783` and
characteristic `3e25a3bf-bfe1-4c71-97c5-5bdb73fac89e` to the app's generic
headset-command writer. Its only implemented command enum is explicitly named
`WelcomeLEDs` / “Welcome LEDs Command” and has command byte `01`.

The writer builds two bytes: command byte followed by an optional argument. The
only current implementation supplies no argument, which serializes as `01 00`.
Call sites occur in Nova introduction/session UI paths. The characteristic's
GATT property is Write Without Response, consistent with this serializer.

No reviewed HCI file contains a direct value write to `0x001d`. The role and
payload are therefore high-confidence static findings, not a dynamically
confirmed device response. No acknowledgement behavior is claimed.

## `0x001f`: firmware-exposed, current-app-unused

Characteristic `2b35ef1f-11a6-4089-8cd5-843c5d0c9c55` is adjacent to the
Welcome-LED command in the same custom service and advertises Read, Write
Without Response, and Notify. A CCCD is present at `0x0020`.

The UUID is absent from the acquired 7.0.0 and 7.2.1 app constants and code
references. Across all reviewed captures there is no direct read, write, or
notification on `0x001f`, and the app never writes its CCCD. This rules out use
by the reviewed app flows but does not identify the firmware feature.

It may be a response/status peer, manufacturing interface, reserved extension,
or feature used by another client. Those are alternatives, not findings. The
correct durable label is **firmware-exposed, current-app-unused; semantic role
unresolved**.

## `0x002e`: offline-session selection and state

Android 7.2.1 names the method argument `offlineSessionType`, converts it to one
byte, and writes it to service `3e8ec328-a4b8-4273-a380-47d219f64e9b`,
characteristic `2a84aaff-6738-4629-894c-346357b89a0c`. The enum mapping is:

| Value | Selection |
|---:|---|
| `00` | Relaxed |
| `01` | Explore |
| `02` | Sleep |
| `ff` | Not set |

The connection setup reads this characteristic and enables notifications on its
CCCD at `0x002f`. The 2026-09-22 firmware-check traffic contains two direct
reads returning `01`; the rotated log contains an earlier read with the same
value. This independently agrees with the app UI showing Explore selected.

No selection-change write was captured because Explore was already selected
and the operator correctly left it unchanged. Thus the selected-state read is
L4-confirmed; the four-value write mapping is L2 static with a directly observed
read for value `01`.

## `0x0031`: Nova offline-session header

Android reads `51bfc219-feab-4227-8b93-8af8cc5306d4` during Nova setup and
passes the response to a class whose retained name is
`NovaOfflineSessionHeader`. Its parser requires at least 16 bytes and reads four
little-endian 32-bit unsigned values named:

1. `magic`;
2. `version`;
3. `sessionCount`; and
4. `activeSessionIndex`.

The current-mask response begins:

```text
4e 4c 46 4f | 01 00 00 00 | 00 00 00 00 | 01 00 00 00
magic       | version = 1 | count = 0    | active index = 1
```

The same prefix appeared in three reviewed reads spanning the current and
rotated firmware-check logs. The long response continues with zero-filled data
and required an ATT Read Blob continuation; Android's reviewed parser uses only
the first 16 bytes. The remaining capacity must not be labeled as session data
without a nonzero specimen or firmware implementation.

The active index `1` is consistent with the separately read offline type
`Explore = 1`. The zero `sessionCount` coexists with app-defined Relaxed,
Explore, and Sleep choices; it should not be interpreted as “no presets” without
firmware documentation.

## Evidence hashes

| Artifact | SHA-256 | Role |
|---|---|---|
| Android 7.2.1 `L1.smali` | `d1ca189bd70ea0464fb51038bce13fdfb83f0f738cf6a00e0f3b305a4c23f14c` | UUID bindings and public operations |
| Android 7.2.1 `v0.1.smali` | `8633d7777595ed608a7a09205236b22702449fd5317527995250213c46592742` | reads, writes, payload construction, response dispatch |
| Welcome command enum | `f3352c281115b956b74260dc760fc943fbd8f040e3ef3ce29a2b8635ec484fa4` | command `01` and retained name |
| Offline-header model | `f81a713a701de393430dad7e37d6dc3fdebc84ea2266af5e45813dd7d7673b69` | retained field names |
| Offline-header parser | `40a4156b8e52a4290144636d25858671bc44373aa92a74401dc0d3c0a5f0e44f` | 16-byte little-endian decode |
| Offline-session enum | `0c6726ff1b25e842f0348919318aae4019bce175bfd46d3eef99262d7e0d433a` | Relaxed/Explore/Sleep/Not Set mapping |
| Firmware-check HCI, current | `d63253f0308cb5db5725b6c5e40a164162ae87b67494a4f841c05a87126e9729` | repeated `0x002e` and `0x0031` reads |
| Firmware-check HCI, rotated | `2f8d5db219ae79ac8dd9ea1456e8e8af1650d5acc192e65dbc62fc5378d19aad` | earlier matching reads |

The two HCI files remain embedded in the ignored, local-only bugreport whose
published container hash is documented in `NOVA_FIRMWARE_UPDATE_PATH.md`.

## Consequences for the next experiments

The characteristic dictionary is sufficiently resolved for the next capture.
`0x002e` and `0x0031` are configuration/setup traffic and should not be confused
with live timing or acknowledgement packets. `0x001d` is unrelated to the
steady app-session stream. `0x001f` should simply be monitored for unexpected
activity during later experiments; no targeted write is justified.

The next high-value collection is therefore the audio-correlated A35 HCI plus
S21 video/audio run, followed by the separately controlled disconnect/hold
experiment.
