# N2 Nova BLE protocol and state-machine report

## Result

Controlled HCI captures establish the Nova session-control service, compact
timing packet, active-state values, brightness-button notifications, and the
observable start/pause/resume/stop state machine. The report distinguishes UUIDs
from connection-specific ATT handles: UUIDs identify protocol attributes, while
the listed handles are convenient references for the reviewed firmware's GATT
layout and must not be assumed stable across versions.

## Reviewed GATT map

| Service | Characteristic | Reviewed handle | Observed role |
|---|---|---:|---|
| Battery `180f` | Battery Level `2a19` | `0x0012` | Periodic device-to-app battery notification |
| Custom `47bbfb1e-670e-4f81-bfb3-78daffc9a783` | `964fbffe-6940-4371-8d48-fe43b07ed00b` | `0x001a` | Physical brightness-button notification |
| Custom `47bbfb1e-670e-4f81-bfb3-78daffc9a783` | `3e25a3bf-bfe1-4c71-97c5-5bdb73fac89e` | `0x001d` | Present; semantic role not assigned |
| Custom `47bbfb1e-670e-4f81-bfb3-78daffc9a783` | `2b35ef1f-11a6-4089-8cd5-843c5d0c9c55` | `0x001f` | Present; semantic role not assigned |
| Custom `3e8ec328-a4b8-4273-a380-47d219f64e9b` | `2a84aaff-6738-4629-894c-346357b89a0c` | `0x002e` | App subscribes; exact payload semantics unresolved |
| Custom `3e8ec328-a4b8-4273-a380-47d219f64e9b` | `51bfc219-feab-4227-8b93-8af8cc5306d4` | `0x0031` | Present; semantic role not assigned |
| Session control `b568de7c-b6c6-42cb-8303-fcc9cb25007c` | `f2c51a4e-2a46-4bef-b18f-cb00c716cfa6` | `0x0034` | App-to-mask timing stream, Write Without Response |
| Session control `b568de7c-b6c6-42cb-8303-fcc9cb25007c` | `12345678-9abc-4def-8012-3456789abcde` | `0x0036` | Notification subscription follows active playback state |
| Session control `b568de7c-b6c6-42cb-8303-fcc9cb25007c` | `abcdef01-2345-6789-abcd-ef0123456789` | `0x0039` | App-to-mask active/inactive state |
| Zephyr SMP `8d53dc1d-1db7-4cd3-868b-8a527460aa84` | `da2e7828-fbce-4e01-ae9e-261174997c48` | `0x003c` | Firmware update transport; discovered but unused in reviewed sessions |

Standard GAP, GATT, Device Information, and Battery attributes are omitted except
where they support a finding. Current device-information values are documented
in `NOVA_FIRMWARE_UPDATE_PATH.md`; the serial number and Bluetooth addresses are
not published.

## Command dictionary

| Direction | Attribute | Payload | Evidence-backed interpretation |
|---|---|---|---|
| App → mask | Timing (`0x0034`) | 12 bytes, three little-endian integers | Matched-side period µs, on-time µs, and constant-on scaled by 1,000,000 |
| App → mask | Timing (`0x0034`) | 40 bytes, ten little-endian integers | Independent-side-capable timing form; statically implemented but not observed in reviewed content |
| App → mask | State (`0x0039`) | `0a` | Active streaming state associated with start and resume |
| App → mask | State (`0x0039`) | `00` | Inactive state associated with pause and stop |
| App → mask | Timing (`0x0034`) | twelve zero bytes | Light-off/terminal timing value at pause or stop |
| Mask → app | Brightness (`0x001a`) | `0101` | Physical brightness-decrease interaction |
| Mask → app | Brightness (`0x001a`) | `0102` | Physical brightness-increase interaction |
| Mask → app | Battery (`0x0012`) | one-byte level | Periodic battery level |

Duplicate brightness notifications occurred within subsecond clusters in one
capture, so notification count is not universally treated as physical press
count. A later paced sequence produced exactly four decrease, four increase,
and four decrease notifications in the reported order.

## Observable state machine

```text
disconnected
  → GATT connected
  → services discovered / subscriptions configured
  → ready
  → active (`0a`; recurring timing writes)
       ↔ paused (`00`; zero timing; stream suppressed)
  → stopped (`00`; zero timing; no later resume)
  → disconnected
```

The state byte alone does not distinguish start from resume or pause from stop.
Those states are reconstructed from event order, app lifecycle, subscription
changes, and whether timing delivery subsequently resumes.

The controlled sequence supplies the clearest transition evidence:

| Boundary | Observation |
|---|---|
| Start | `0a` at 13:03:25.129; timing begins 49 ms later |
| Pause | `00` at 13:04:01.239; zero timing follows 3.8 ms later; no timing during pause |
| Resume | `0a` at 13:04:15.550; timing resumes 4 ms later |
| Stop | zero timing at 13:04:33.127; two `00` writes follow |

## Streaming and repeatability

The app streams current timing values instead of provisioning the complete
session program in one transaction:

- Bittersweet repeated 600 paired nonzero packets over 53 seconds. Every field
  matched within one microsecond; mean timing displacement was 2.646 ms.
- Vitality repeated 447 paired packets. Every field matched within one
  microsecond; mean timing displacement was 0.924 ms.
- The full Vitality run emitted 2,962 nonzero writes and covered all 32 declared
  active segments.
- Deep Exploration emitted 2,915 nonzero compact writes during a natural run.
- The captured Stillness and Spirit intervals likewise used only the compact
  form.

These runs establish deterministic, track-relative timing streams. They do not
prove how many values Nova buffers or whether firmware interpolates between
updates.

## Brightness separation

Physical brightness-button events travel mask-to-app on a notification channel;
they do not alter the three timing fields or cause an app-to-mask brightness
echo. Programmed frequency and duty continue evolving between button events.
The evidence therefore supports a mask-local brightness gain that is separate
from the streamed strobe envelope. Exact gain steps, persistence, and electrical
drive levels are not measured.

## Connection and error behavior

The reviewed connection negotiated a large ATT MTU and initially requested a
7.5 ms interval. Several captures ended with Android reporting GATT status 8.
No fatal app exception or native crash accompanied those events. Status 8 is
retained as an observed disconnection outcome, not assigned a device-specific
root cause.

## Confidence and limitations

- **L4, 0.99:** compact timing layout and active/inactive values, supported by
  static serialization plus multiple controlled HCI captures.
- **L3–L4, 0.98:** brightness payload meanings and local-control separation,
  supported by paced physical-button sequences and absence of echo writes.
- **L2, 0.95:** extended independent-side form, established in current-version
  code but not observed in a live capture.
- **Unresolved:** two custom-characteristic roles, notification payloads other
  than brightness/battery, firmware buffering/interpolation, retransmission or
  loss behavior, exact disconnect causes, and any firmware-version-dependent
  GATT-layout change.

Raw HCI logs and device identifiers remain local. Source hashes and detailed
per-run timelines are preserved in the controlled-run `ANALYSIS.md` files and
the tracked Vitality, Stillness, Spirit, left/right, and physical-validation
reports.
