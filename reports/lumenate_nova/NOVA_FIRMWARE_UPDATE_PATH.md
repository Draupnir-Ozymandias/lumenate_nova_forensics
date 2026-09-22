# Nova firmware update path (Android 7.2.1)

**Status:** Static reconstruction complete; no update was requested or installed  
**App:** Lumenate 7.2.1 (`versionCode` 400)  
**Base APK SHA-256:** `40a2cf2bff296006f2bdb0fbde1136f9e67608cbcce0dc54c8f34ba535fd8b7d`

## Result

The current Android app contains an active Nova firmware-update implementation,
not a placeholder. It uses a server-mediated discovery and download flow followed
by a Zephyr/MCU Manager (MCUmgr) BLE transfer. Firmware updating is separate from
the Nova session-control characteristics used in the light-timing captures.

The reconstructed path is:

1. Read the connected Nova's hardware and firmware versions.
2. Call Firebase callable function `checkForHeadsetFirmwareUpdate` with those two
   values. The response contains `updateAvailable` and optional release notes.
3. On an explicit update request, call
   `generateHeadsetFirmwareUpdateURL`, again with hardware and firmware versions.
4. Parse a returned `url`, download it with an HTTP GET into memory, and expose
   download progress.
5. Parse the response as a ZIP containing `manifest.json` plus `.bin` and/or
   `.suit` payloads.
6. Convert manifest entries into MCUmgr image descriptors and transfer them over
   the standard SMP BLE service and characteristic.
7. Report success, failure, and restart/reconnection states to the UI.

## Network control plane

The 7.2.1 smali invokes two named Firebase callable functions:

- `checkForHeadsetFirmwareUpdate`
- `generateHeadsetFirmwareUpdateURL`

Both calls send `hardwareVersion` and `firmwareVersion`. The update-check response
expects `updateAvailable` and `notes`; the URL response expects `url`. This means
the APK does not embed a fixed firmware URL or firmware image. Compatibility and
artifact selection are delegated to the backend.

The app's downloader uses a GET request, 10-second connect and read timeouts, and
requires HTTP status 200. It reads the entire response into memory. Static code
does not reveal a current firmware URL, because the URL is generated at runtime.

## Package format

`HeadsetZipUpdatePackage` accepts a ZIP with:

- `manifest.json`, decoded with lower-case underscore field names;
- `.bin` images; and
- `.suit` envelopes.

Each manifest file entry can carry `type`, `file`, `size`, `image_index`, `slot`,
and `partition`. The parser maps entries into MCUmgr images and has special slot
selection behavior for type `mcuboot`. It rejects directory ZIP entries and uses
canonical-path checks to reject traversal outside the conceptual extraction root.

The reviewed app-side parser does not visibly compare a manifest digest or the
declared `size` with downloaded bytes. That observation does **not** establish
that arbitrary firmware is accepted: MCUmgr, MCUboot, and/or SUIT validation on
the device may enforce integrity and authenticity. Device-side acceptance remains
unmeasured.

## BLE transport

The OTA transport uses Zephyr SMP/MCUmgr UUIDs:

| Role | UUID |
|---|---|
| SMP service | `8d53dc1d-1db7-4cd3-868b-8a527460aa84` |
| SMP characteristic | `da2e7828-fbce-4e01-ae9e-261174997c48` |

The characteristic must support write-without-response and notification. The
upgrade manager is configured with a 20-second erase timeout and retry/window
parameters of four. The app selects `CONFIRM_ONLY` for its post-upload image mode;
the exact boot/test/confirm consequences should be verified from a real update
capture rather than inferred from the enum name alone.

## Evidence

Current-version reviewed derivatives:

| Artifact | SHA-256 | Relevant evidence |
|---|---|---|
| `common/a2$a.smali` | `1c0c19ea17c14bae88d6dc72204781e6ee9fa9673621130e9f63bd655bc88cfe` | callable-function names, request fields, response handling |
| `common/a2.1.smali` | `5b9d765312704141420bd0083c05991b13cfe4c40e7b3b73f31aed7cad7b4285` | download and MCUmgr installation path |
| `HeadsetZipUpdatePackage.smali` | `15f1fae27a4c2c72602d6eb24b15c886b9a69539dc53a4e62feae6f995fcffcb` | ZIP manifest and payload parser |
| `Oc/a.smali` | `df71fcf6f2047d82d7e56c1226ffdebcda1612afc1a6dd10dc81033f3e39ca08` | SMP service and characteristic UUIDs |

The readable 7.0.0 JADX output was used only to recover names and control-flow
meaning. Every material claim above was cross-checked against the acquired 7.2.1
smali listed in the table.

## Safe acquisition plan

A firmware package should be acquired through the ordinary app workflow, without
initiating the BLE install:

1. Connect Nova and open its settings page while recording a Bluetooth HCI snoop
   log and an app/network capture that the device permits.
2. Record the hardware version, current firmware version, and update-check result.
3. If an update is offered, capture the generated download request and preserve
   the response bytes and headers before the installer sends SMP packets.
4. Hash the untouched ZIP, inspect `manifest.json`, hash each payload, and record
   file sizes and types.
5. Stop before transfer unless a separate, explicit update experiment is planned
   with uninterrupted power and recovery contingencies.

At present firmware `1.0.4` was observed in the app UI during the offline Explore
capture, but it was not established whether a newer package is available. No
firmware package, generated URL, or OTA packet trace has yet been acquired.

## Confidence and limitations

- **High confidence:** backend function names and request fields; ZIP payload
  types; MCUmgr transport; SMP UUIDs; app-visible state machine.
- **Medium confidence:** precise semantics of the selected MCUmgr confirmation
  mode without observing a full update.
- **Unknown:** current latest firmware, package signatures/digests, bootloader
  policy, rollback behavior, recovery path, and whether the backend will offer an
  update for the observed hardware/firmware pair.

This reconstruction does not justify bypassing the vendor workflow, modifying a
firmware image, or asserting that the device accepts unsigned code.
