# N0 closeout and acquisition manifest

## Gate decision

**N0 is closed as of 2026-09-22.** A reviewer can identify the current
acquisition by hash, understand the collection and verification methods,
reproduce static checks from local specimens, and review sanitized inventories
without placing raw evidence or credentials in Git.

This closeout does not claim source-code completeness, dynamic coverage of every
SDK/endpoint, possession of Nova firmware, or calibrated physical validation.
Those are later-milestone boundaries.

## Current acquisition

| Field | Value |
|---|---|
| Acquisition date | 2026-09-19 |
| Package | `com.lumenate.lumenateaa` |
| Version | `7.2.1` (`versionCode 400`) |
| Minimum / target / compile SDK | 24 / 36 / 36 |
| Installed splits | base, ARM64 v8a, xxhdpi |
| Collection | read-only `adb shell pm path`, `dumpsys package`, and `adb pull` |
| Signer certificate SHA-256 | `ee0cdc8327859eae3c13600034c74a87ab26e72dc6b91279b9952ef250d5bac8` |
| Signature result | APK Signature Schemes v2/v3 verified; base Google Play source stamp verified |
| ZIP result | all three APKs passed integrity checks |

### Specimen hashes

| Local-only component | SHA-256 |
|---|---|
| `original/base.apk` | `40a2cf2bff296006f2bdb0fbde1136f9e67608cbcce0dc54c8f34ba535fd8b7d` |
| `original/split_config.arm64_v8a.apk` | `cf143f85dc9cd2d4191586ab072fd541d376ea791705b8d35493bdb3b75cc03a` |
| `original/split_config.xxhdpi.apk` | `bb1713652a6d6fb886c216d127f69c3977cff9e6aa449411f39d739967473a2e` |

### High-value derivative hashes

| Derivative | SHA-256 |
|---|---|
| Vitality five-minute declaration, newline terminated | `2b6c46189fba81d0aa6e2db2663d869a61ced9d3674983275e53000b9ee5d7fd` |
| `StrobeManager.smali` | `473dfa8f4a84884101ba3c59f632ad7548521e2c0ff5d75b7553fabe5dd1e1e3` |
| Session model derivative | `43a20771a98c9a14dace448779b252f4507325e2724f651d0e2a598662f5f85b` |
| Session service derivative `i` | `346943aaf06a58d3142cdeb497593d21bbf8060c3b3cbbc7e48514e2f9ad25a0` |
| Session service derivative `t` | `8b08bf129b17d461de13d6e73d1305baab4886181851333640769c1e1a69965a` |

The 7.2.1 Vitality declaration and `StrobeManager.smali` are byte-identical to
their reviewed 7.0.0 counterparts. Apktool warned about unresolved drawable
resources because the density split was not merged into the base decode; the
relevant bytecode decoded normally.

## Tool and run inventory

| Tool | Recorded version / identity | Material result | Exit-status record |
|---|---|---|---|
| Android platform tools / ADB | acquisition host installation; exact historical version not captured | located installed splits, collected package metadata, pulled all three APKs | successful artifacts and acquisition notes; numeric status not preserved |
| APK signature verifier | Android build-tools installation; exact historical version not captured | v2/v3, signer certificate, and source-stamp verification | success recorded in acquisition notes; numeric status not preserved |
| ZIP integrity tool | host installation; exact historical version not captured | all APKs readable and intact | success recorded; numeric status not preserved |
| Apktool | `3.0.2` | base decode completed; density-resource warnings bounded above | successful decode with warnings |
| `apkanalyzer` | `/opt/homebrew/bin/apkanalyzer`; tool does not expose a conventional version verb | package 7.2.1/400, SDK 24/36, non-debuggable, six DEX | current rerun successful |
| JADX | `1.5.6` | earlier broad pass produced useful methods with 162 method errors; later detailed save exhausted heap at 99% | incomplete by design; no completeness claim |
| APKiD | `3.1.0` in historical output | 7.0.0 base: R8 and anti-VM/debug indicators across five DEX | base output present; ARM status indeterminate, see below |
| Ghidra | `12.1.2` | successful headless AArch64 analysis of the 7.2.1 strobe library | successful analysis derivatives; documented in N4 |
| TShark | `4.6.7` | HCI/BLE filtering and packet inventories | successful reviewed derivatives |
| FFmpeg | `8.1.2` | video/audio probing and optical-analysis preparation | successful reviewed derivatives |
| Java | OpenJDK `26.0.1` | supports current Java analysis tooling | current version capture successful |
| Python | `3.14.6` host default | utility runtime | present; the default interpreter does not contain project test dependencies |

Where the original command's numeric exit status was not contemporaneously
captured, this table says so. Artifact presence is not rewritten as a fictional
status code. Later reviewed reports and hashes preserve the material outcomes.

## ARM APKiD disposition

The historical `apkid-arm64.txt` contains only the APKiD 3.1.0 header. It does
not retain a target confirmation or exit status, so it cannot support either a
clean result or a completed scan. The historical invocation is therefore
classified **indeterminate**, not “no finding.”

This does not leave the ARM payload unidentified. The ARM split passed ZIP and
signature verification; all five native libraries were independently extracted
and hashed; and `libstrobecontroller-lib.so` was successfully loaded as a
stripped AArch64 ELF and analyzed with Ghidra 12.1.2. N4's native conclusions
rest on that analysis plus smali and HCI corroboration, not on APKiD. Reinstalling
APKiD solely to recreate a generic packer scan would not change the evidentiary
boundary and is not an N0 gate requirement.

## Repository and secret audit

The closeout audit performed two separate checks:

1. `git rev-list --objects --all` was filtered for raw-evidence directories and
   APK/AAB/APKS/XAPK/DEX/SO/PCAP/PCAPNG/HCI/archive/database/log/media
   extensions. It returned no matching historical Git objects.
2. tracked text was searched for credential-shaped API keys, bearer values,
   signed-URL signatures, private-key markers, and private-key assignments. It
   returned no matches.

The repository ignore policy covers `specimens/`, `dynamic/`, `static/`,
captures, downloads, raw mobile binaries, packet captures, databases, logs,
media, environment files, keys, and secrets. Local ignored APK derivatives do
contain proprietary material and signed Firebase media URLs; publication
inventories intentionally reduce those to sanitized host/role entries.

This is a path/extension and credential-pattern audit, not a proof that every
historical byte is non-sensitive. Its result is sufficient for this repository's
documented publication model because only reviewed text, schemas, code, hashes,
and measurement derivatives have been tracked.

## N0 gap disposition

| Former gap | Disposition |
|---|---|
| Permissions, SDKs, endpoints, assets, databases | Closed by `N0_INVENTORIES.md` |
| Content-library version | No independent identifier exists in reviewed material; pinned to app 7.2.1/400 and derivative hashes |
| Writable characteristic and packet construction | Closed in N1/N2, including compact 12-byte and extended 40-byte serializers |
| Raw-evidence secret/PII review and Git-history remediation | Audit clean; no history rewrite required |
| Acquisition manifest and tool outcomes | Closed here, with missing historical numeric statuses explicitly disclosed |
| ARM APKiD ambiguity | Historical run classified indeterminate; ARM identity/inventory independently superseded by verified extraction and Ghidra analysis |

## Reproduction boundary

A reviewer with lawful access to local specimens can verify APK hashes, ZIP
integrity, signatures, manifest/DEX/native inventories, derivative hashes, and
the documented static paths. Raw specimens are intentionally not distributed
through Git. The sanitized public trail continues in N1–N4, physical-validation
reports, protocol exports, and the released AVE `0.2.0` contract fixtures.
