# Lumenate Nova evidence status — 2026-09-22

## Purpose and scope

This report consolidates the publishable evidence state after the Android
7.2.1 acquisition, controlled BLE runs, Galaxy S21 optical captures, released
`0.2.0` handoff, and non-invasive firmware check. It is an evidence inventory,
not a product-safety, clinical-efficacy, or subjective-experience assessment.

Raw APKs, audio, videos, bugreports, HCI logs, identifiers, credentials, and
generated download URLs remain local and ignored by Git. Tracked artifacts
contain only hashes, reviewed measurements, sanitized interpretations, and
bounded limitations.

## Findings at a glance

| Finding | Strongest support | Confidence boundary |
|---|---|---|
| Vitality has a contiguous 300 s declaration with 34 segments, including 32 active segments spanning 7.0–13.5 Hz. | Runtime-version declaration plus a natural five-minute BLE run covering every active segment. | L4 transport confirmation, score 0.98. |
| The verified Vitality audio and light program share an app/native media-position association. | SHA-256-identified audio, `syncMe(positionMs)` control flow, and two runtime BLE/media clock pairs. | Association uncertainty is 20 ms at runtime and excludes firmware-to-photon latency. |
| Vitality physically emits closely matching four-emitter flashes and approximately the reconstructed frequency. | Two full 120 fps recordings plus a pilot; the 10.5 Hz segment repeatedly measured about 10.464 Hz. | Direct optical corroboration, but not one simultaneous packet-to-photon clock chain; overall session remains L4. |
| Captured Vitality, Deep Exploration, Spirit, and offline Explore intervals showed no sustained emitter divergence. | Four-region optical measurements and compact matched-timing BLE writes where simultaneous HCI was available. | Phase offsets below about 8.33 ms and unobserved content remain possible. |
| Android 7.2.1 supports distinct left/right programs, while all 128 inspected built-in duration constructions default the right program to null. | Current-version smali audit, compact/extended packet builder, BLE captures, and optical measurements. | Capability is established; shipped use of independent timing was not observed. |
| Nova reports model `nrf52833`, hardware revision `1.0`, and firmware `1.0.4`. | Direct GATT Device Information reads on 2026-09-22; firmware also displayed in the app UI on 2026-09-21. | Current-device fact only; it does not retroactively identify firmware in earlier captures. |
| Android 7.2.1 contains an active server-mediated MCUmgr/SMP firmware-update path. | Current-version smali, package parser, and standard SMP UUIDs observed in GATT discovery. | No update package or OTA transfer was offered or captured. |

## Evidence chain by session

| Session or path | Declaration/app | BLE transport | Audio identity/anchor | Physical measurement | Published export |
|---|---|---|---|---|---|
| Vitality, 5 min | Complete 34-segment 7.2.1 declaration | Complete natural run; 2,962 nonzero timing writes | Verified asset; three anchors | Two full S21 runs plus pilot | `vitality-5min-empirical-0.2.0.json` |
| Deep Exploration | App session identity | 2,916 compact writes; no extended writes | Not exported | Full 347.705 s S21 capture | `deep-exploration-optical-empirical-0.2.0.json` |
| Mind Games Meditation: Spirit | Current catalog definition inspected | 888 compact writes across log rotation | Not exported | Partial 146.197 s S21 capture | `spirit-optical-empirical-0.2.0.json` |
| Offline Explore | Firmware-resident preset selected by one-byte app command | No live app timing stream intended | Unavailable | Partial 252.459 s S21 capture | `offline-explore-optical-empirical-0.2.0.json` |
| Firmware check | Automatic settings-screen check reconstructed | Device Information reads; no SMP transaction | Not applicable | Not applicable | Narrative report only |

The three non-Vitality optical exports are deliberately partial empirical
captures. They do not pretend to reconstruct complete program declarations or
invent missing audio identities and synchronization anchors.

## Published AVE evidence objects

| Evidence ID | Type | Scope | Score |
|---|---|---|---:|
| `ave_83759cb2d0776a88` | deterministic strobe-program reconstruction | Vitality declaration | 0.99 |
| `ave_c7cf4b7e3b1e7b45` | full-duration BLE confirmation | Vitality transport | 0.995 |
| `ave_b602920cf5622739` | BLE timing repeatability | Vitality controlled repeats | 0.99 |
| `ave_e93d512211639e46` | media/light clock association | Vitality app/native and runtime clocks | 0.95 |
| `ave_d2750e72d53836a8` | verified session audio | Vitality audio | 1.00 |
| `ave_0ec37c9346327df3` | four-emitter optical synchrony | Vitality full S21 replication | 0.98 |
| `ave_cff3179ab694b1b9` | broadband pulse pattern | Vitality audio analysis | 1.00 |
| `ave_02cf954dc2395f0e` | four-emitter optical synchrony | Deep Exploration | 0.98 |
| `ave_0b824fbe08d57035` | compact BLE timing stream | Deep Exploration | 0.98 |
| `ave_7b3fb4c011ddfea5` | four-emitter optical synchrony | Spirit | 0.98 |
| `ave_3fa537e4ca2d874e` | compact BLE timing stream | Spirit | 0.98 |
| `ave_4f1d0e5ac6ea353e` | four-emitter optical synchrony | Offline Explore | 0.98 |

Evidence-object scores express confidence in the bounded measurement or
association stated by that object. They are not probabilities of a health,
safety, entrainment, or efficacy claim.

## Released 0.2.0 handoff status

The producer contract now explicitly represents audio identity, named clocks,
separate light/audio origins, uncertain clock anchors, pulse shape, transitions,
execution layers, overlaps, and unknown values. Four empirical exports validate
against the released schema. AVE's consumer imports the same fixtures, retains
their evidence relationships, and rejects incompatible contract versions.

This satisfies the released producer/consumer handoff. The versioned schema is
immutable; any validation or semantic change requires a new contract version.

## Milestone assessment

| Gate | Current assessment | Remaining evidence needed |
|---|---|---|
| N0 acquisition/reconnaissance | Substantially complete | Sanitized permission/SDK/endpoint/asset/database inventories and final acquisition manifest. |
| N1 control path | Bounded report complete | Close remaining unknown native scheduling edges and test the extended live path if suitable content appears. |
| N2 BLE/state machine | Core session path documented | Resolve remaining custom-characteristic roles and characterize loss, recovery, and disconnect causes. |
| N3 session/synchronization | Closed for the bounded Vitality export | A photon-level clock anchor is still required for precise device latency, not for the existing importer. |
| N4 native/firmware boundary | Partially complete | Native scheduling responsibility and device-side firmware validation policy remain unresolved. |
| N5 physical validation | Provisional camera-based confirmation | A photodiode/ADC or oscilloscope is needed for calibrated duty, intensity, subframe phase, and packet-to-photon timing. |
| N6 AVE integration | `0.2.0` released | Additional fixtures may be added without changing the frozen schema. |

## Material limitations

- The 120 fps camera resolves approximately 8.33 ms frames, not continuous
  optical time. Rolling shutter and finite exposure can move threshold crossings
  or miss narrow pulses.
- Region-average luma is not calibrated radiometry and cannot establish absolute
  intensity, color, or physical duty cycle.
- No captured session supplies one common, calibrated BLE/audio/optical clock.
- No observed built-in content used the extended independent-side command, but
  the software capability exists and future or remote content may differ.
- The firmware check response body was unavailable. Absence of an update action
  cannot distinguish a normal `updateAvailable = false` response from a silently
  handled backend failure.
- Engineering timing evidence does not establish neurological entrainment,
  therapeutic benefit, safety, or subjective outcome.

## Remaining reports and evidence work

The highest-value documentary work is now:

1. an N0 closeout manifest covering the remaining sanitized inventories;
2. an N4 native/firmware-boundary report focused on scheduling, buffering, and
   device-side validation responsibilities;
3. a deliberately versioned successor only if new evidence requires a contract
   change.

The N1 control path and N2 BLE/state-machine reports are now published as
`N1_CONTROL_PATH.md` and `N2_BLE_PROTOCOL_STATE_MACHINE.md`.

Further random track scouting is lower-value unless a new app, content catalog,
or firmware version exposes an independent-side program. A future firmware
package should be preserved only if the ordinary app workflow offers one; OTA
installation remains a separate experiment requiring explicit approval and
recovery planning.
