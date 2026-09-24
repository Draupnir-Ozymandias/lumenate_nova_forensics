# Audio-correlated Vitality BLE/video clock bridge

## Acquisition

On 2026-09-24, one controlled Vitality run was captured simultaneously with:

- a Galaxy A35 (`SM-A356U`) running Lumenate 7.2.1 and recording an unfiltered
  Android Bluetooth HCI snoop;
- Nova firmware 1.0.4 connected over encrypted BLE; and
- a Galaxy S21 Ultra 5G recording the stationary, unworn mask in Pro Video mode
  at 1920x1080 and approximately 120 fps with 48 kHz stereo AAC audio.

The operator selected the five-minute Vitality duration, allowed approximately
98 seconds of playback, stopped the session in the app, and did not use the
mask brightness buttons. The operator-reported camera settings were ISO 50 and
1/500-second shutter. Those exposure values are recollection, not embedded
camera metadata.

The local-only source hashes are:

| Source | Size | SHA-256 |
| --- | ---: | --- |
| S21 video | 48,845,467 bytes | `024e8cbfdbfeef3a3ff53235e5490753ad0579c0f36253dedf2e3dcd6d0bee11` |
| A35 HCI snoop | 248,266 bytes | `f4699c289fb9d42bb6418af1d3affcceb727643959f9d4fc6821a758f5ea3ea3` |
| Extracted app writes | 778 rows including header | `603237f02eeb14e8855a127226b464f111b58c40e809fec0af5d7406e778337d` |
| A35 dumpstate | 76,320,580 bytes | `16abe2346c58d0245e463c2275fec5b4bb1ade2600e9b17ce24bdf32102f2475` |

The phone-side and workstation hashes of the S21 video matched. The video is
118.529444 seconds long and contains 14,223 frames.

## BLE and media boundary

The Android MediaSession entered `PLAYING` at position zero at
09:23:38.353--09:23:38.354 EDT. The BLE active-state write followed at
09:23:38.356861, a 3.861 ms displacement on the same A35 wall-clock record.
The HCI trace then contained 772 nonzero timing writes, covering the first 11
complete active declaration segments, followed by a final zero and inactive
state at 98.276073 seconds on the BLE run clock. The MediaSession stopped at
position 98.015 seconds.

Tshark renders Samsung's local-time btsnoop timestamp four hours behind the
Android log on this EDT capture. Adding the observed 14,400-second timezone
offset makes the packet and log timestamps agree. Exported synchronization uses
elapsed run time rather than treating that encoded value as a portable UTC
timestamp.

## Audio/video alignment

The S21 soundtrack and the SHA-256-identified Vitality asset were decoded to
mono 8 kHz PCM, band-limited to 100--3500 Hz, and aligned with normalized
cross-correlation. Decoded reference time zero maps to S21 video time
8.047750 seconds. The verified M4A audio stream begins at media position 44 ms,
so media position zero extrapolates to video time 8.003750 seconds.

A 20-second local correlation at decoded-reference time 75 seconds maps to
video time 83.047625 seconds. Additional 10--20 second local windows stayed
within approximately 22 ms peak-to-peak despite room acoustics and repetitive
music structure. The export therefore assigns 20 ms uncertainty to each
audio/video anchor; this does not include calibrated acoustic propagation or
Android speaker-output latency.

The resulting common chain is:

`A35 HCI elapsed time -> A35 media position -> verified Vitality audio -> S21 audio/video time -> S21 optical frames`

This is the first capture in the project to place the packet stream and physical
emitter observations from the same run on one bounded timeline.

## Optical measurement

Four fixed 60x60-pixel emitter-core regions were classified at mean luma greater
than 30. Each emitter produced 963 rising edges. Of those, 960 occurred on the
same frame across all four emitters. Only 13 of 14,223 frames (0.0914%) differed
in binary state among the four regions. Pairwise full-video luma correlations
ranged from 0.997984 to 0.999870.

The constant-frequency regions reproduced prior captures:

| Declared command region | Measured emitter frequency |
| --- | ---: |
| 7.5 Hz, program seconds 26--35 | 7.481800 Hz |
| 10.5 Hz, program seconds 37--56 | 10.463793--10.463809 Hz |
| 10.5 Hz, program seconds 58--78 | 10.466483 Hz |

The first frame above threshold occurred at video time 9.958711 seconds. The
first nonzero BLE timing write maps to approximately 9.521788 seconds through
the common clock. Their roughly 437 ms separation must not be interpreted as
device latency: the program begins with one-percent duty, and a 1/500-second
exposure at 120 fps can miss many narrow pulses before a frame samples one.

## Conclusion and boundary

The run establishes a bounded common BLE/audio/video clock and independently
replicates the commanded-frequency and four-emitter-synchrony findings. It
raises the clock-chain association to strong L4 evidence but not L5 physical
timing. The camera cannot measure calibrated intensity, true duty cycle,
electrical latency, or phase below approximately one 8.33 ms frame, and finite
exposure can miss narrow pulses entirely. A photodiode or equivalent sensor is
still required for packet-to-photon latency and subframe phase claims.

Raw video, audio, bugreport, HCI packets, and device identifiers remain local
and ignored by Git. The sanitized measurements and hashes are incorporated into
the Vitality `0.2.0` empirical export.
