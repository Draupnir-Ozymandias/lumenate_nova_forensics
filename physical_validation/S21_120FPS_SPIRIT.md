# Spirit Mind Games Meditation: S21 optical cross-check

## Acquisition and scope

The operator recorded the John Lennon *Mind Games Meditation* **Spirit** mix
on 2026-09-21 with the Galaxy S21 Ultra (`SM-G998U`) while the A35 captured
Bluetooth HCI traffic. The original video is preserved locally at
`dynamic/lumenate_nova/optical/2026-09-21_spirit/original/20260921_130755.mp4`
(SHA-256 `2d527d610ac4aee0bf798ccc709bb2c89ca2e837086fa9c2a278f0853594031d`).
It is 48,948,551 bytes, HEVC 1920×1080 at approximately 120 fps, 17,543
frames, duration 146.197156 s, with AAC audio. The operator did not visually
observe asynchronous flashes.

The S21 video starts before the A35 session. The recorded light-output window
is approximately video time 53.427–138.822 s, so this video tests only about
85.4 s of the mix's illuminated portion, not the full 372.819 s track.

## Optical measurement

Four distinct 50×50-pixel emitter-core regions were analyzed at x coordinates
760, 860, 960, and 1060, y=500. A nearby background region at x=1200,
y=500 remained at mean luma 16.005 (maximum 16.289). Each emitter region
had a dark baseline near 16 and an illuminated maximum of 231.8–236.3.
Thus, despite the reported indirect daylight, the pulses are well separated
from background in this capture. Per-frame luma traces are preserved locally
under `dynamic/lumenate_nova/optical/2026-09-21_spirit/analysis/`.

At mean luma greater than 50, all four emitter regions yielded exactly 850
rising edges. Of these, 843 rose on the same video frame in all four regions
(99.18%). All four first illuminated at 53.427 s and last illuminated at
138.821878 s. Only 20 of 17,543 frames (0.114%) differed among the four
thresholded states; every disagreement was an isolated single frame. Pairwise
full-video luma correlations ranged from 0.997637 to 0.999956. Thresholds
from 20 through 100 yielded 848–854 edges per emitter and no sustained
disagreement. Frame spacing remained approximately 8.33 ms.

The physical output is therefore synchronous across all four emitters to the
camera's approximately 8.33 ms temporal resolution for the recorded Spirit
interval. Subframe phase differences, pulses missed between exposures, and
later portions of the full mix remain untested. Mean-luma analysis also does
not make a calibrated claim about relative emitter brightness or duty cycle.

## BLE cross-check

The simultaneous A35 log identifies the session as Spirit. Across the HCI
log rotation, its 888 timing writes (887 nonzero) were all 12-byte compact
commands, with no 40-byte independent left/right command. The first nonzero
write followed activation by 41.905442 s, consistent with the declared 42 s
dark introduction. See `reports/lumenate_nova/SPIRIT_BLE_SCOUT.md` for the
packet boundary and hashes. The BLE and optical observations agree for the
overlapping captured interval; neither establishes that all Nova content is
synchronous.
