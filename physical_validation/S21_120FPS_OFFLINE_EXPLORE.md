# Nova offline Explore: S21 optical scout

## Acquisition

On 2026-09-21, the connected A35 app showed **Explore** already selected as
the Nova's stored offline sequence; no preset change was made. The app's live
mask connection was then disconnected without forgetting the device. The
operator started the mask-resident Explore preset using its buttons and
recorded the stationary mask with the Galaxy S21 Ultra. The mask reported
firmware version 1.0.4 before disconnection. No A35 app session or BLE timing
stream was intended for this run.

The original video is preserved locally at
`dynamic/lumenate_nova/optical/2026-09-21_offline-explore/original/20260921_134920.mp4`
(SHA-256 `6314bc1142e08766dcc9ff6b134394e6811dad81843e899db9e9f721df407f6d`).
It is 83,268,978 bytes, HEVC 1920×1080 at approximately 120 fps, 30,294
frames, duration 252.459478 s, with AAC audio. The recording covers the
first 64.54 s before detected illumination and about 185.02 s of illuminated
output. The preset is nominally ten minutes, so the later portion was not
captured.

## Four-emitter measurement

Four 50×50-pixel emitter-core regions were placed at x coordinates 505, 615,
725, and 835, y=500. A 50×50 nearby background region at x=1100, y=500
stayed at mean luma 16.0 throughout. The emitter dark baseline was about 16,
while illuminated region maxima were 232.6–236.3. Thus the room illumination
did not compromise on/off classification. Per-frame luma traces are retained
locally under `dynamic/lumenate_nova/optical/2026-09-21_offline-explore/analysis/`.

At mean luma greater than 30, the four regions produced 1,584, 1,586, 1,586,
and 1,584 detected rising edges. All four first illuminated at video time
64.544089 s and last illuminated at 249.567700 s. Of the rising-edge frames,
1,563 were identical across all four emitters. Only 35 of 30,294 frames
(0.116%) had any disagreement in binary LED state, and every disagreement
lasted exactly one frame. Pairwise luma correlations ranged from 0.997801
to 0.999953. Thresholds from 20 through 100 yielded 1,562–1,588 edges per
emitter, with no sustained binary-state disagreement. Frame spacing was
approximately 8.33 ms.

The captured portion of the firmware-resident offline Explore preset is
therefore synchronous across all four emitters at the camera's temporal
resolution. This distinct execution path agrees with the app-track captures,
but does not prove the entire ten-minute preset, the other offline presets,
or all future firmware/content is synchronous. Subframe offsets and pulses
falling between exposures remain unmeasured without a faster calibrated
sensor. Region-average luma is not a calibrated per-emitter intensity or
duty-cycle measurement.
