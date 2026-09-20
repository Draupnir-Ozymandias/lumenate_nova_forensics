# Galaxy S21 Ultra Vitality full-run optical captures

## Acquisition

The original five-minute Vitality recording was acquired on 2026-09-20 with a
Galaxy S21 Ultra 5G (`SM-G998U`) and preserved at:

`dynamic/lumenate_nova/optical/2026-09-20_vitality-full/original/20260920_065325.mp4`

| Property | Value |
| --- | --- |
| SHA-256 | `03f26ad6c59aece0be740b85c68b2014b07bde6ab1dac203a1b1b6c7b2bbce53` |
| Size | 155,503,164 bytes |
| Duration | 312.370056 s |
| Video | HEVC, 1920x1080, approximately 120 fps |
| Frames | 37,483 |
| Audio | AAC, 48 kHz, stereo |

The operator reports ISO 50 and a 1/2000-second shutter. The earlier report of
ISO 30 was a transcription error. The file does not embed independently
verified exposure settings, so these are operator-recalled acquisition
parameters.

The mask remained stationary. The S21 camera was repositioned between captures
because it had to be moved to the Mac for each USB transfer. Consequently, ROI
coordinates differ by recording and do not indicate movement of the device
under test.

## Provisional analysis

Four fixed 60x60-pixel regions were placed over the spatially separated
emitters. An illuminated frame was provisionally classified at mean luma
greater than 30; the dark baseline was approximately 16. Depending on emitter,
the brightest mean luma was 134.9 to 179.7, so illuminated frames were clearly
separated from the baseline without saturation in the region average.

The four regions produced 3,084, 3,085, 3,085, and 3,086 detected rising edges.
Pairwise luma correlations ranged from 0.99957 to 0.99998. Only 54 of 37,483
frames (0.144%) disagreed in binary state across emitters, and 3,068 rising
edges occurred on the exact same frame in all four regions. This full recording
therefore independently supports synchronous operation of all four emitters
for Vitality at the camera's temporal resolution. It does not establish that
every Lumenate track uses synchronous left/right output.

The declared frequency trajectory integrates to approximately 3,160.2 cycles
over the five-minute program; fractional phase makes this an expectation, not
an exact integer event count. The camera detected about 3,085 rising edges,
approximately 97.6% of that expectation. In the declared constant 10.5 Hz
segment from session seconds 37 through 56, the camera detected 199 rising
edges and measured approximately 10.467 Hz. This agrees with and replicates the
pilot recording's approximately 10.464 Hz optical result.

Long apparent inter-flash gaps concentrate in low-duty portions of the
declaration, particularly near session seconds 294 through 297 as duty
approaches 0.01. This distribution is consistent with temporal undersampling:
at 120 fps, a 1/2000-second exposure observes only about 0.5 ms of each 8.33 ms
frame interval. A narrow pulse can occur entirely between exposures. The
recording is therefore strong evidence for frequency and four-emitter
synchrony, but it is not a complete census of physical pulses and must not be
used to estimate duty cycle directly.

## Replication rationale

The short-exposure recording was retained and a complementary full run was
acquired in controlled darkness at FHD 120, ISO 50, and a 1/500-second shutter.
The longer exposure was expected to reduce missed narrow pulses while retaining
enough separation for emitter synchrony analysis. Because a 1/500-second
exposure still leaves unsampled time between frames, any direct duty-cycle
claim remains out of scope without a photodiode or calibrated continuous
sensor.

Rain and dark skies provided a sufficiently dark environment for the repeat;
the environmental change is retained as operator context rather than treated
as an instrumented illumination measurement.

## ISO 50, 1/500-second replication

Rain and dark skies restored a suitably dark environment, and the operator
completed the recommended replication at the corrected ISO 50 setting and a
1/500-second shutter. The original is preserved at:

`dynamic/lumenate_nova/optical/2026-09-20_vitality-full-1-500/original/20260920_071733.mp4`

| Property | Value |
| --- | --- |
| SHA-256 | `d332a84e2e363d56d0ddd2a248a4393169c3431ca60ee7c45b5aaf68c3a881fd` |
| Size | 106,006,004 bytes |
| Duration | 306.244822 s |
| Video | HEVC, 1920x1080, approximately 120 fps |
| Frames | 36,732 |
| Audio | AAC, 48 kHz, stereo |

Four narrower 50x50-pixel core regions were used because the longer exposure
increased optical bloom. The cores remained spatially separable. At mean luma
greater than 30, the regions produced 3,123, 3,123, 3,122, and 3,123 rising
edges. Counts remained within ten events per emitter as the threshold was swept
from 20 through 100, demonstrating that the result is not sensitive to a
single threshold choice.

The 1/500-second capture recovered approximately 38 more rising edges than the
1/2000-second capture. The longest apparent inter-flash gap decreased from
0.667 seconds in the short-exposure capture to 0.375 seconds in the replicate;
two regions had a maximum of only 0.283 seconds. Some low-duty events can still
fall between 120 fps exposures, but the predicted improvement in pulse-event
completeness is observed.

The constant 10.5 Hz segment contained 198 in-window rising edges and measured
10.4644 Hz on all four regions. This agrees with the 1/2000 full run and the
earlier pilot. The repeated approximately 0.34% frequency shortfall is therefore
unlikely to be a threshold or shutter artifact.

Pairwise full-recording luma correlations ranged from 0.99860 to 0.99998. Only
52 of 36,732 frames (0.142%) disagreed in thresholded state across emitters,
and 3,091 rising edges occurred on the exact same frame in all four regions.
The replicate independently confirms synchronous four-emitter operation for
Vitality while leaving other tracks, including any possible left/right-specific
programs, untested.
