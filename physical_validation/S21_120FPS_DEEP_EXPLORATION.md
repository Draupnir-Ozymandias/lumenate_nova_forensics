# Deep Exploration: simultaneous S21 optical and A35 BLE capture

## Acquisition

On 2026-09-21, the operator recorded a full Deep Exploration session with the
Galaxy S21 Ultra at FHD 120 fps while the Galaxy A35 ran the Lumenate app and
captured a Bluetooth HCI snoop log. The original video is retained locally at
`dynamic/lumenate_nova/optical/2026-09-21_deep-exploration/original/20260921_123356.mp4`
(SHA-256 `0b526b3bc7f97b804080906461f629257b885f77d8f967c4ca2f0facb0c074a4`,
128,211,849 bytes). It is HEVC 1920×1080, approximately 120 fps, 41,723
frames, duration 347.704711 s, with AAC 48 kHz stereo audio.

The user reported indirect daylight in the office and no visually apparent
left/right alternation. Camera exposure metadata were not independently
verified. The mask remained stationary; the S21 was moved for USB transfer.

The A35 bugreport and extracted HCI log are retained locally under
`dynamic/lumenate_nova/runs/2026-09-21_deep-exploration-dual/`, with hashes in
that directory's `SHA256SUMS`. Raw evidence is ignored by Git.

## BLE timing

After the pre-run marker, the active-state packet occurred at epoch
1789994038.895466. The first nonzero timing write occurred 37.6086 s later,
consistent with the declared 37.7 s dark introduction. The last nonzero
timing write was at epoch 1789994352.485755, and the inactive-state packet
was at 1789994376.022118. Active to inactive was 337.126652 s, consistent
with a natural full run. App metadata identified the session as Deep
Exploration.

There were 2,916 timing writes on handle 0x0034, of which 2,915 were nonzero.
Every timing write used the 12-byte compact form; none used the 40-byte
left/right extended form. This is packet-level evidence of matched rather
than independent left/right timing commands for this run.

## Four-emitter optical analysis

Four separate 50×50-pixel emitter-core regions were analyzed at x coordinates
705, 810, 910, and 1015, y=470. A nearby 50×50 background region at x=1170,
y=470 stayed at mean luma about 16 (maximum 16.02). The emitter dark baseline
was also about 16, while illuminated core-region maxima were 230–236. Thus
the indirect daylight did not prevent clear on/off classification in this
recording. Per-frame signalstat traces are retained in the local `analysis/`
directory, with hashes in its parent `SHA256SUMS`.

At mean luma greater than 30, the four regions yielded 2,879, 2,879, 2,879,
and 2,878 rising edges. All four first illuminated at video time 39.484811 s
and last illuminated at 314.895156 s. Exactly 55 of 41,723 frames (0.132%)
had any disagreement among the four binary states, and every disagreement
was isolated to a single frame. In 2,855 edge events, all four rising edges
fell on the exact same frame. All but one emitter-edge event matched across
emitters within ±1 frame. Pairwise luma correlations ranged from 0.998859
to 0.999981; zero-frame lag gave maximal binary agreement compared with ±1
or ±2 frames. Thresholds from 20 to 100 yielded 2,875–2,880 rising edges
per emitter. Video frame spacing was about 8.33 ms and monotonic.

This supports synchronous output of all four emitters for Deep Exploration
at 120 fps resolution. The experiment cannot rule out a phase difference
shorter than one frame, narrow pulses falling between exposures, or a
different pattern in another session. It also cannot prove that the visual
experience lacks spatial depth: perceived spatial effects and independent
left/right strobe timing are distinct claims.

## John Lennon mix follow-up

In the acquired app version 7.2.1, all nine John Lennon *Mind Games Meditation*
mix definitions provide one strobe-sequence string and leave the separate
right-hand sequence argument null. The runtime path uses the left sequence
for both sides when no right sequence is supplied. This predicts compact,
matched left/right timing for those built-in definitions, despite marketing
language about spatial light sequences. It does not substitute for a live
capture if the app can replace definitions remotely or the firmware adds
behavior not evident from commands. A short live Mind Games capture spanning
the first light onset would be a focused falsification test; another long
S21 recording is not presently needed to establish the app-side prediction.
