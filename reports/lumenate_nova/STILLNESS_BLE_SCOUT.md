# Stillness BLE left/right scout

## Scope

On 2026-09-21, the operator started a five-minute **Stillness** session on the
Galaxy A35 with Bluetooth HCI snooping enabled, then stopped it after about
148.6 seconds. The app's Android media metadata identified the playing title
as `Stillness`. No optical recording was made for this scout.

The original bugreport and extracted HCI log are preserved locally, outside
Git, under `dynamic/lumenate_nova/runs/2026-09-21_stillness-ble-scout/`.

| Local source | SHA-256 |
| --- | --- |
| `bugreport.zip` | `7617b9ae1ba89861be793e8ee4aade87f9c7d46004dc99f6c9bcb028e71baa12` |
| `btsnoop_hci.log` | `a275ad022f7f755bb4376344833632fdf4de7b20a3d8810484963ee26b50b6da` |

## Capture boundary and result

The HCI archive also includes an earlier, separate playback interval. Only the
later interval, after the `LUMENATE_FORENSICS` pre-run Android log marker at
11:59:15 EDT, is attributed to this scout. HCI display timestamps have the
previously observed four-hour offset from Android local wall time.

- Active-state write: HCI frame 13636, epoch 1789992752.064819, value `0a`.
- First nonzero timing write: frame 13951, epoch 1789992764.514279.
- Last nonzero timing write: frame 19161, epoch 1789992900.580887.
- Inactive-state writes: frames 19167 and 19188, values `00`.
- Session interval from active to first inactive write: 148.624 seconds.
- Timing writes on handle `0x0034`: 1,485, comprising 1,484 nonzero writes and
  one zero write after stop. **All 1,485 payloads were 12 bytes.**

The first approximately 148.6 seconds of Stillness therefore used the compact
synchronized timing command. No 40-byte left/right command was observed in
this interval. This does **not** rule out different commands later in Stillness
or in another session.

## Why 40 bytes matters

Static app code supports both the compact three-integer (12-byte) command and
an extended ten-integer (40-byte) command. The extended form can carry separate
left/right timing and phase-related values when both sides are active and
their parameters diverge. The existence of that branch makes left/right
optical disparity a testable hypothesis; it does not establish that Stillness
or any particular available track exercises the branch.

An efficient next scout is a different session family, preferably one the
operator remembers as having left/right behavior. Once a 40-byte BLE interval
is found, optical recording can target that exact program interval.
