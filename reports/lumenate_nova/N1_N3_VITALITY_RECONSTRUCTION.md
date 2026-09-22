# Vitality 5-minute reconstruction and audio alignment

## Result

The Vitality 5-minute session is represented by the first empirical candidate
`0.2.0` export in
`reports/lumenate_nova/exports/vitality-5min-empirical-0.2.0.json`.
It contains a contiguous 300-second light declaration, a cryptographically
identified audio asset, representative observed BLE commands, three explicit
clock anchors, seven AVE-compatible evidence objects, and bounded limitations.

The full schedule now has L4 BLE transport confirmation with score 0.98. An
uninterrupted natural five-minute run covered every declared active segment. It
remains L4 overall because the later optical recordings were separate runs and
did not connect individual BLE packets to emitted photons on one shared clock.
Those recordings nevertheless provide direct physical corroboration of the
reconstructed frequency and four-emitter synchrony at approximately 8.33 ms
video resolution.

## Deterministic light schedule

The decompiled Lumenate 7.2.1 model declares 34 contiguous segments from zero
through 300 seconds:

- off from 0 to 1.5 seconds;
- 32 active segments from 1.5 to 298 seconds;
- off from 298 to 300 seconds.

The active schedule ranges from 7.0 to 13.5 Hz. It contains 31 segments with
linear frequency and/or duty interpolation and one constant segment: 10.5 Hz
at 0.20 duty from 37 to 56 seconds. The export preserves interpolated endpoints
in transition parameters rather than collapsing ramps to scalar values.

Two independently started 7.2.1 runs confirm the captured prefix. Of 447
sequence-paired timing packets, 394 were byte-for-byte identical; all remaining
timing fields differed by at most one microsecond. Mean packet displacement was
0.924 ms and maximum displacement was 4.732 ms. No physical brightness-button
notification was observed in either run.

A third run on 2026-09-19 completed naturally. It contained 2,962 nonzero
timing writes, covered all 32 declared active segments, entered the declared
off interval at the end, and emitted the inactive-state command at 299.492
seconds on the BLE capture clock. Mapping the first nonzero write to declared
program time 1.500 seconds produced these full-run residuals:

| Comparison | Mean absolute error | Maximum absolute error |
| --- | ---: | ---: |
| Frequency | 0.000903 Hz | 0.021239 Hz |
| Duty cycle | 0.000049 | 0.000553 |

## Audio identity and structure

The exact cached 5-minute asset is AAC-LC stereo at 48 kHz. Its SHA-256 is
`b24513faf9f3e920d9addf725563bd236fa3b33f6c1fa91949bcf6011eda7c41`.
The container duration is 299.690667 seconds, 309.333 ms shorter than the
declared light program, and its audio stream starts at 44 ms.

AVE decoded 299.646667 seconds and classified both channels as irregular
transients, with zero onset regularity and different aggregate rates (8.540421
Hz left, 9.632731 Hz right). All 28 time windows had the same irregular-
transient classification and AVE found no classification transition. This does
not support treating the music as a regular hard-gated pulse train mirroring
the 7.0–13.5 Hz light schedule. The classification does not establish intent,
efficacy, or physiological response.

## Audio/light clock association

Static control flow provides the strongest definition of the intended clock
relationship. On playback-position discontinuity, the service passes the new
integer ExoPlayer media position directly to native
`StrobeManager.syncMe(positionMs)`. Starting at a nonzero media position follows
the same synchronization path before `doStrobe` runs. The export therefore
anchors program zero to media-position zero with 1 ms argument-resolution
uncertainty. That anchor applies at the app/native execution layers and does
not claim BLE-arrival or photon-level simultaneity.

The uninterrupted full run adds two bounded observations:

| BLE clock from active write | Media position | Difference | Assigned uncertainty |
| ---: | ---: | ---: | ---: |
| 1,460.828 ms | 1,322 ms | 138.828 ms | 20 ms |
| 297,964.395 ms | 297,830 ms | 134.395 ms | 20 ms |

The first row pairs the first nonzero timing write with a MediaSession log about
five milliseconds away in wall-clock time. The second pairs the final zero
timing write with a MediaSession log about one millisecond away. The BLE/media
offset changes by only 4.433 ms across almost the entire session, but Android
emits MediaSession state asynchronously. It is therefore evidence for clock
association, not a precise device-to-photon latency measurement.

## Physical optical corroboration

Two full-session Galaxy S21 Ultra recordings independently sampled Vitality at
approximately 120 fps. The ISO 50, 1/500-second replication produced 3,123,
3,123, 3,122, and 3,123 rising edges across the four emitter regions; 3,091
rising-edge frames were identical across all four. Only 52 of 36,732 frames
(0.142%) disagreed in binary state, with pairwise luma correlations from 0.99860
to 0.99998. The declared constant 10.5 Hz segment measured 10.4644 Hz on all
four regions, agreeing with the separate 1/2000-second full run and the pilot.

This is direct physical evidence of matched four-emitter timing and a close
frequency correspondence. It is not a calibrated intensity or duty-cycle
measurement: the rolling-shutter camera samples only part of each frame period,
can miss narrow pulses, and cannot exclude offsets shorter than one frame. The
optical run was not simultaneous with the complete BLE run, so the cumulative
chain remains L4 under the project's evidence-level rules. See
`physical_validation/S21_120FPS_VITALITY_FULL.md` for acquisition hashes,
threshold checks, and limitations.

## Version verification and limitations

The runtime phone package was acquired on 2026-09-19 and verified as Lumenate
7.2.1 (`versionCode` 400). Its five-minute Vitality declaration is byte-for-byte
identical to the declaration from the earlier 7.0.0 (`versionCode` 380) APK.
`StrobeManager.smali` is also byte-for-byte identical, and the same media-
position `syncMe` and `doStrobe` control paths remain present. The earlier
cross-version boundary is therefore resolved: the full reconstruction now
comes directly from the same app version used for the dynamic capture.

The base APK SHA-256 is
`40a2cf2bff296006f2bdb0fbde1136f9e67608cbcce0dc54c8f34ba535fd8b7d`.
All three installed splits passed archive-integrity and APK-signature
verification and share the same signing-certificate SHA-256 digest,
`ee0cdc8327859eae3c13600034c74a87ab26e72dc6b91279b9952ef250d5bac8`.

The same Nova later reported hardware revision `1.0` and firmware `1.0.4`
directly over the standard GATT Device Information Service on 2026-09-22; the
app UI had also displayed firmware `1.0.4` on 2026-09-21. That does not
retroactively prove the firmware version present during the earlier Vitality
captures, so the session export correctly leaves `device.firmware_version`
null. Brightness calibration, LED color, physical intensity, and
firmware-to-photon latency remain unknown. The tracked export excludes the
signed media URL, Bluetooth addresses, phone identifiers, device serial, and
copyrighted audio bytes.

## Reproduction

From the repository root:

```sh
.venv/bin/python tools/build_vitality_empirical_export.py
.venv/bin/python tools/validate_protocol_export.py \
  reports/lumenate_nova/exports/vitality-5min-empirical-0.2.0.json
PYTHONPATH=. .venv/bin/pytest -q
```
