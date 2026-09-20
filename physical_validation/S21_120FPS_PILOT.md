# Galaxy S21 Ultra 120 fps optical pilot

## Acquisition

Two original Pro Video recordings were acquired from a Galaxy S21 Ultra 5G
(`SM-G998U`) on 2026-09-20. Both are 1920x1080 HEVC video at approximately
120 fps with 48 kHz stereo AAC audio.

| Source file | Duration | Frames | Size | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `20260920_061633.mp4` | 84.294833 s | 10,115 | 79,056,332 bytes | `a59759b760436e89e36be7a101e02f7bcc44fa724b8b666329b601cde18bf351` |
| `20260920_062014.mp4` | 92.695144 s | 11,123 | 32,439,202 bytes | `cecc719a60bb9d1a6899d07fe679c086fd8a77b12110afd9852fb1ccbbc6ee6b` |

The files do not expose the operator's manual shutter/ISO settings in metadata.
The operator recalls that the preferred second recording used approximately
ISO 50 and a 1/500-second shutter. These values are acquisition recollection,
not file-embedded metadata.

The mask remained stationary throughout the optical work. The camera position
changed between recordings because the S21 had to be moved between the filming
position and its USB connection to the Mac; this accounts for changes in LED
image coordinates between captures.

## Suitability assessment

The first recording has substantial optical bloom: the four sources merge into
one bright bar in illuminated frames. It remains useful for aggregate flash
frequency but is poorly suited to individual-emitter timing.

The second recording is suitable for provisional physical validation. The four
emitters are spatially separable, the background is stable, and the recording
contains 11,123 frames with a median frame interval of 8.333 ms and maximum
interval of 8.345 ms. Four fixed 80x80-pixel regions were analyzed at equal
vertical position.

## Four-emitter synchrony

Each region produced 875 detected rising edges. Of these, 863 rising edges
occurred in the identical frame for all four emitters. The remaining 12 had a
maximum span of one frame (8.33 ms) across the four threshold crossings. No
edge differed by more than one frame.

Pairwise full-recording luma correlations ranged from 0.9938 to 0.9999. Only 28
of 11,123 frames (0.252%) had differing binary on/off classifications across
the regions. These mismatches occur at partial-exposure threshold boundaries.
The recording therefore supports synchronous four-emitter operation at camera
resolution; it does not support independently timed emitters or clusters.

## Frequency observation

The video audio was correlated against the acquired Vitality soundtrack. The
second recording's acoustic media onset is approximately 2.20 seconds into the
video and remains stable to within about 18 ms across local correlations. The
first detected illumination occurs at 3.5418 seconds, approximately 1.34
seconds after the acoustic onset, consistent with the previously observed
control/media offset at the declared 1.5-second light onset.

Across the long declared 10.5 Hz portion, all four regions measure approximately
10.464 Hz from their optical rising edges. The approximately 0.036 Hz shortfall
(0.34%) is common to all four emitters and is not explained by audio/video clock
drift in the recording. This is a provisional physical observation of a small
device-output clock deviation, subject to replication in the full recording.

## Duty-cycle limitation

Thresholded illuminated-frame fractions are around 0.23 during the nominal
0.20-duty constant segment. Camera exposure integrates light over each frame,
and rolling-shutter scan timing has not been calibrated. The pilot can therefore
confirm flash frequency and inter-emitter synchrony, but its frame-duty fraction
must not be presented as a direct physical duty-cycle measurement.

## Recommendation

Use ISO 50 and a 1/500-second shutter, the recalled configuration that produced
`20260920_062014.mp4`, for a full five-minute recording. Preserve the same
camera/mask geometry, keep audio enabled, begin at least five seconds before
playback, and continue at least five seconds after natural completion. The
first recording's configuration should not be used because bloom obscures
individual emitters.
