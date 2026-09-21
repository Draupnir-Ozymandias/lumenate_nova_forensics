# Nova left/right capability versus shipped Android content

## Finding

The acquired Android app version 7.2.1 contains protocol and parser support
for separate left/right light timing, but its inspected built-in session
catalog does not supply a separate right-hand light sequence. This is
consistent with the observed compact 12-byte BLE commands and synchronous
four-emitter optical output in Vitality, Deep Exploration, and the captured
portion of the John Lennon *Mind Games Meditation* Spirit mix.

This supports a **capability-without-observed-content** interpretation. It
does not establish whether Lumenate intends a future release, whether any
server-delivered content uses the feature, or whether device-stored offline
sequences take a different path.

## Static audit

The local acquisition is under
`dynamic/lumenate_nova/acquisitions/2026-09-19_v7.2.1/apktool/`.

- `smali_classes4/com/lumenate/lumenate/model/a.smali` has 128 synthetic
  `Leb/Q0` session-duration constructor calls. At all 128 call sites, the
  default-argument mask is `0x10`.
- In `smali_classes4/eb/Q0.smali`, the synthetic constructor tests mask bit
  `0x10` and replaces the right-hand sequence argument with null when set.
  Thus all 128 inspected built-in session-duration constructions default the
  right-hand program to null, regardless of the register's prior value.
- In `smali_classes4/ib/c.smali`, the parser detects an absent/empty
  right-hand string and reuses its parsed left-hand sequence for the right
  side. The BLE command builder has a compact 12-byte path for matched
  timing and an extended 40-byte path for divergent side parameters. This
  establishes software support, not use by the inspected catalog.
- The earlier decompiled catalog contains 139 `C16172P0` constructions,
  each with an explicit null right-hand sequence. This is corroborative only;
  the 7.2.1 smali mask audit above is the current-version result.

## Dynamic evidence and limits

The full Deep Exploration capture used 2,916 compact 12-byte timing writes
and no extended 40-byte write. The Spirit scout used 888 compact timing
writes and no extended write during its first approximately 128 s. The S21
videos independently showed synchronous four-emitter flashes at about 8.33
ms resolution in their recorded intervals. See
`physical_validation/S21_120FPS_DEEP_EXPLORATION.md`,
`reports/lumenate_nova/SPIRIT_BLE_SCOUT.md`, and
`physical_validation/S21_120FPS_SPIRIT.md`.

No capture can exclude unobserved later or remote content. A 120 fps camera
cannot exclude subframe offsets. The catalog audit does not cover Nova's
device-stored offline sequence implementation or future app/firmware versions.

## Interpretation and next experiment

Lumenate's [Nova product page](https://lumenate.co/lumenate-nova/) describes
four independently controlled LEDs, while its
[support article](https://support.lumenate.co/en/articles/13431643-how-does-the-nova-experience-differ-from-the-phone)
frames spatial sequencing as a possibility enabled by the hardware. Neither
statement establishes that a currently selectable built-in track drives
independent left/right flashes. The current evidence therefore makes random
track-by-track camera scouting low-yield.

The next distinct path is the device-stored offline sequences. Lumenate
[documents](https://support.lumenate.co/en/articles/13512963-how-do-i-access-nova-free-core-light-sequences)
Relaxed, Explore, and Sleep as selectable sequences that run on Nova without
an app connection. In the acquired 7.2.1 app,
`smali_classes4/com/lumenate/lumenate/common/v0.1.smali` encodes the selected
offline session type as **one byte** and writes it to a dedicated BLE
characteristic. The earlier decompiled enum maps Relaxed=0, Explore=1,
Sleep=2, and Not Set=255. The app therefore selects a mask-resident preset;
it does not provision a timed light-program string on this path.

The mask firmware's preset timing is not revealed by that one-byte write.
A short, targeted S21 optical scout of offline **Explore** is justified.
Capture should begin before starting the preset and cover at least its first
illuminated minute. If that also
shows synchrony, further random track scouting is unlikely to be useful;
the next step is firmware analysis, a new app/firmware/content version, or
a direct technical clarification from Lumenate.

On 2026-09-21, the connected A35 app displayed **Explore already selected**
for the operator's Nova (firmware 1.0.4). No preset change was necessary.
The app's live connection was then disconnected, without forgetting the
device, to prepare a clean firmware-only optical scout. The subsequent S21
recording covers about 185 seconds of illuminated offline Explore output and
shows all four emitters synchronized to the camera's 8.33 ms resolution.
See `physical_validation/S21_120FPS_OFFLINE_EXPLORE.md` for the measurement
and limits.
