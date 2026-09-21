# Spirit Mind Games Meditation BLE scout

On 2026-09-21, the operator ran the John Lennon *Mind Games Meditation*
**Spirit** mix on the Galaxy A35 with Bluetooth HCI snooping enabled. The
bugreport's Android media metadata identifies the track as `Spirit` with a
declared duration of 372,819 ms. The session was stopped early after about
128.2 s, so this result covers only the first active portion of the mix.

The original bugreport and both pieces of the rotated HCI log are preserved
locally, outside Git, under
`dynamic/lumenate_nova/runs/2026-09-21_spirit-dual/`. Their hashes are in the
local `SHA256SUMS` file. The HCI log rotated during this run; analyzing only
`btsnoop_hci.log` would omit the first 57.3 s of timing writes.

| Event | HCI epoch | Capture part |
| --- | ---: | --- |
| Active-state write (`0a`, handle `0x0039`) | 1789996086.841267 | `.last` |
| First nonzero timing write | 1789996128.746709 | `.last` |
| Last nonzero timing write | 1789996214.925020 | current |
| Zero timing write | 1789996214.999773 | current |
| First inactive-state write (`00`) | 1789996214.943803 | current |

The first light command followed activation by 41.905442 s, matching the
built-in Spirit definition's approximately 42 s dark introduction. The
active-to-first-inactive interval was 128.102536 s. There were 603 timing
writes in `.last` and 285 in the current log, for **888 total** (887 nonzero
and one zero). Every one was 12 bytes; no 40-byte independent left/right
timing command appeared in the captured interval.

This is direct BLE evidence that the first approximately 86 s of Spirit's
illuminated portion uses the compact matched-timing path. It agrees with the
installed app's single-sequence Spirit definition. It does not establish
what a later, uncaptured portion of the mix does. The companion S21 video
was acquired and independently showed four-emitter synchrony in the same
interval; see `physical_validation/S21_120FPS_SPIRIT.md`.
