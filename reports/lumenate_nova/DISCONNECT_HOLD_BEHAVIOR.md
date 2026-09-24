# Nova live-stream disconnect and hold behavior

## Result

A controlled 2026-09-24 Vitality run shows that Nova firmware briefly retains
the last received timing command after the BLE link is lost, then stops emitted
light without receiving the normal app-level zero-timing or inactive-state
writes. At 120 fps, all four emitters produced three further synchronized
10.5 Hz rising edges after the mapped HCI disconnect. The final illuminated
frame occurred approximately 229 ms after disconnect, and no emitter
illuminated during the remaining 28.6 seconds of video.

This resolves the principal live-stream watchdog question for firmware 1.0.4:
loss of the app link does not leave the last command running indefinitely. It
also does not stop on the exact disconnect instant. The observed behavior is a
short device-side hold followed by a firmware-side safe stop.

## Controlled procedure

The Galaxy A35 ran Lumenate 7.2.1 and streamed the five-minute Vitality session
to a Nova reporting firmware 1.0.4. The mask was stationary, unworn, and framed
by a Galaxy S21 Ultra recording 1920x1080 HEVC at approximately 120 fps with
48 kHz stereo audio. At media position 45.017 seconds, an ADB-controlled Android
Bluetooth disable interrupted the link. The S21 continued recording for more
than 28 seconds after optical cessation.

The final successful run followed two ordinary non-disconnect controls produced
while the automation was being corrected. The first watcher expired before
playback began. The second parsed MediaSession's buffered position rather than
its playback position. Neither issued a Bluetooth-disable command; both videos
are retained locally and explicitly labeled as controls. Before the final run,
the corrected parser and Android disable/re-enable path were independently
tested while playback was stopped.

## Source identity

| Local-only source | SHA-256 |
| --- | --- |
| Final S21 video, 81.378056 s | `6ac885d0b40ad879347b0bc6526f6165af48b475397a05ab3b87755e707f4dba` |
| A35 HCI snoop | `8b70f60c6b25946b1922f71d9555558544b4526f3704bfa0cbef3ddfebfaa526` |
| Final-run BLE writes | `7a8afed355552fcbf73b42e90876ff9143b72b5c47d784738237960abde0b2c9` |
| A35 dumpstate | `29770db474b477e75398f6ec023c97d317bc1f9677cdff06bf46d5f116526cb9` |
| A35 bugreport ZIP | `a217eec25b13b7c707efecf8acef79953eb3d1445dbc73f5aa8656ec522210c8` |
| Timeout control video | `2acbe85e2266da32dcdaa4e9da1bd9cef0a94e080c42f42f60955b0df1c3a49c` |
| Parser control video | `88084e7c5889b07445f66ad83e5c7f7d6d6ffa5f064c650df1e2075d83d974be` |

Phone-side and workstation hashes matched for all three S21 files.

## Transport boundary

The successful trace contains one active-state write and 334 nonzero timing
writes. No zero-timing write and no inactive-state `00` write preceded link
loss. The last timing payload was:

`06 74 01 00 68 4a 00 00 00 00 00 00`

Decoded little-endian, it requests a 95,238 microsecond period, 19,048
microsecond on-time, zero constant-on field, approximately 10.5 Hz, and 20%
duty. It arrived 8.572807 seconds before the HCI Disconnection Complete event.
Nova was therefore already holding a constant command between updates when the
link was interrupted.

Android disabled Bluetooth at media position 45.017 seconds. The HCI disconnect
event carried reason `0x16` (local host termination). Lumenate changed its
MediaSession to `PAUSED` at position 45.541--45.553 seconds, approximately
94 ms after the HCI disconnect on the A35 wall clock, and remained paused for
the entire 35-second automated observation tail.

## Common-clock mapping

The S21 soundtrack was aligned to the verified Vitality audio asset using the
same band-limited normalized cross-correlation method as the preceding common-
clock run. Decoded reference time zero maps to S21 video time 6.961875 seconds.
Because the verified M4A stream starts at media position 44 ms, media position
zero maps to video time 6.917875 seconds.

The MediaSession entered `PLAYING` at 10:01:18.021 EDT; the BLE active-state
write followed at 10:01:18.072023. Mapping the HCI disconnect at
10:02:03.684159 through that wall-clock relation places it at video time
approximately 52.581 seconds. A conservative 20 ms uncertainty is retained for
the audio/video and Android/HCI association.

Samsung's btsnoop timestamps encode local wall time such that Tshark renders
them four hours behind the EDT Android log. Analysis uses elapsed HCI time and
the observed 14,400-second offset, not the rendered epoch as portable UTC.

## Optical boundary

Four fixed 60x60-pixel emitter-core regions were classified at mean luma greater
than 30. Results were unchanged at thresholds from 20 through 80. Every emitter
produced 423 rising edges, and the final twelve edge times were identical across
all four regions at camera resolution.

The final three post-disconnect rising edges occurred at video times 52.610311,
52.701978, and 52.793644 seconds. The final illuminated frame was 52.810311;
the next frame at 52.818644 was dark. All 3,427 later frames were dark, with a
maximum region-average luma of 16.0 after video time 53 seconds.

Relative to the mapped disconnect, the last rising edge was about 213 ms later
and the last illuminated frame about 229 ms later. The next 10.5 Hz rise would
have been expected around 52.889 seconds but was not observed. This supports a
camera-observed hold of roughly three cycles and cessation within approximately
0.3 seconds. That upper bound is not photon-calibrated: a 120 fps camera with a
1/500-second exposure can miss a narrow pulse between frames.

Pairwise full-video luma correlations ranged from 0.998539 to 0.999982. No
left/right or cluster-specific divergence accompanied disconnect.

## State-machine consequence

The normal app pause/stop path explicitly sends zero timing and inactive state.
The forced-disconnect path did neither. Nevertheless, physical output ceased
after a short hold. The state machine therefore gains a distinct link-loss
transition:

```text
active streaming
  -> link lost (no zero or inactive write)
  -> retain final timing for roughly three observed cycles
  -> firmware-side light-off watchdog state
```

This conclusion is bounded to the reviewed Nova hardware and firmware 1.0.4,
the compact matched-side timing path, and the tested 10.5 Hz / 20% command.
Packet-loss without full link loss, other frequencies, independent-side
commands, reconnect behavior during an active session, and electrical shutdown
timing remain separate questions.
