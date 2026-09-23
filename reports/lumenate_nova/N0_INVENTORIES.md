# N0 sanitized inventories — Android 7.2.1

## Scope

This is the reviewed, publishable inventory for package
`com.lumenate.lumenateaa`, version `7.2.1` (`versionCode 400`). It was produced
from the SHA-256-identified split APK acquisition dated 2026-09-19. It records
names, roles, counts, versions, and hashes needed for reproducibility while
excluding device identifiers, user data, API keys, access tokens, signed object
URLs, and raw evidence.

Static presence establishes bundled capability or configuration. It does not,
by itself, prove that a permission, SDK, endpoint, or asset was exercised in a
captured run.

## Package and component surface

| Property | Value |
|---|---|
| Package | `com.lumenate.lumenateaa` |
| Version | `7.2.1` (`400`) |
| Minimum / target / compile SDK | 24 / 36 / 36 |
| Debuggable | false |
| Installed splits | base, ARM64 v8a, xxhdpi |
| DEX files | 6 |
| Base-APK ZIP entries | 1,550 |
| Manifest components | 118 activities, 13 services, 8 receivers, 5 providers |

The first-party `LumenateSessionService` is an exported foreground service with
media-playback and connected-device roles. `AudioDownloadService` is a
non-exported data-sync foreground service. The remaining component surface
includes Firebase messaging, reminders, analytics, billing, authentication,
media, and customer-support SDK integrations.

## Declared permissions

Duplicates in the merged manifest are shown once.

| Purpose | Permissions and qualifications |
|---|---|
| Nova / Bluetooth | `BLUETOOTH` (`maxSdkVersion=30`), `BLUETOOTH_ADMIN`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN` (`neverForLocation`) |
| Legacy BLE discovery | `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION` |
| Phone-light and audio input | `CAMERA`, `RECORD_AUDIO` |
| Long-running work | `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_CONNECTED_DEVICE`, `FOREGROUND_SERVICE_DATA_SYNC`, `FOREGROUND_SERVICE_MEDIA_PLAYBACK`, `WAKE_LOCK`, `POST_NOTIFICATIONS` |
| Network | `INTERNET`, `ACCESS_NETWORK_STATE` |
| Legacy storage | `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE` (`maxSdkVersion=28`) |
| Commerce and attribution | `com.android.vending.BILLING`, Play install-referrer, Google advertising ID, AdServices attribution and advertising ID |
| Google messaging/services | C2DM receive, Google services configuration read |
| App-internal receiver guard | signature-level `DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` defined and used by the app |

The manifest also requires camera-flash hardware and makes microphone hardware
optional. Declaration is not evidence of runtime grant or use. Camera access is
consistent with the phone-torch fallback; Bluetooth permissions are consistent
with Nova control; network/storage/foreground permissions are consistent with
streaming, downloads, telemetry, and durable playback.

## SDK and library inventory

Versions below are taken from bundled library property files.

| Family | Bundled versions |
|---|---|
| Google Play Billing / core | Billing `8.3.0`; core-common `2.0.4` |
| Firebase | Analytics `22.0.0`; Auth `23.0.0`; Auth interop `20.0.0`; database collection `18.0.1`; encoders `17.0.0`; encoders-proto `16.0.0`; IID `21.1.0`; IID interop `17.1.0`; measurement connector `20.0.1` |
| Identity / integrity | Google ID `1.1.0`; Play Integrity `1.4.0`; reCAPTCHA `18.4.0`; FIDO `20.1.0` |
| Google Play services | Ads identifier `18.0.1`; Auth `20.7.0`; Auth API phone `18.0.2`; Auth base `18.0.4`; Auth blockstore `16.4.0`; base/basement `18.9.0`; cloud messaging `17.4.0`; location `21.3.0`; stats `17.0.2`; tasks `18.4.0` |
| Measurement / protocol | Play measurement modules `22.0.0`; protolite well-known types `18.0.0` |
| Store review | Review and Review KTX `2.0.1` |

Class namespaces and manifest components also establish the presence of Braze,
Intercom, RevenueCat, Mixpanel, Adjust, Spotify, Firebase Functions/Storage/
Remote Config/Messaging/App Check, Android Media3/ExoPlayer, and OkHttp. Exact
versions for those families were not exposed by the reviewed property files and
are therefore not guessed.

## Sanitized endpoint inventory

Path, query, token, and object-name details are intentionally omitted.

| Role | Host or pattern | Static support and boundary |
|---|---|---|
| Lumenate cloud data | `lumenate-app.firebaseio.com` | Firebase configuration; runtime use not established by presence alone |
| Lumenate media storage | `lumenate-app.appspot.com`, `firebasestorage.googleapis.com`, `storage.googleapis.com` | Configuration and catalog media references; signed query values omitted |
| Callable backend | `%PROJECT%-%REGION%.cloudfunctions.net` | Firebase Functions client pattern; actual calls require runtime corroboration |
| RevenueCat-configured API | `api-production.8-lives-cat.io` | Bundled SDK configuration |
| Lumenate links | `go.lumenate.link`, `lumenate.page.link`, `lumenateapp.onelink.me` | Regulatory, deep-link, and referral roles |
| Spotify | `api.spotify.com` | Create-your-own-session integration |
| JW Platform | `content.jwplatform.com` | Media/content integration |
| Mixpanel EU | `api-eu.mixpanel.com` | Manifest-configured events, people, groups, and decide endpoints |
| Other bundled services | Braze, Intercom, RevenueCat, Adjust, and Google/Firebase service hosts | Library endpoints are inventoried by family; generic documentation/test URLs are excluded |

This is an endpoint surface, not a network-traffic ledger. Incidental URLs from
licenses, schemas, documentation, and library test strings were excluded.

## Assets, resources, content, and databases

The base APK contains six asset payloads:

- two Braze HTML bridge JavaScript files;
- baseline ART profile and profile-metadata files;
- one Font Awesome font;
- `lennon_sample_animation.json`.

The decoded base contains Android resource families for values/localizations,
drawables, layouts, colors, animation, fonts, menus, raw resources, and XML.
Density-specific resources are supplied by the xxhdpi split; therefore counts
from an unmerged Apktool decode are not a canonical visual-asset count.

No `.db`, `.sqlite`, or `.sqlite3` payload is bundled in the acquired splits.
The file named `firebase-database-collection.properties` is SDK metadata, not a
database. Runtime-created stores and user data were outside this static APK
inventory.

The 7.2.1 catalog audit found 128 built-in session-duration constructions. All
128 default the independent right-hand program to null; the parser then reuses
the left program. The catalog is bundled into app bytecode and has no separate,
reviewed content-version identifier. Its reproducible version is therefore the
app build plus the relevant derivative hashes, not a fabricated library number.
Server-delivered, account-gated, or future content may differ.

## ARM64 native libraries

| Library | Bytes | SHA-256 | Evident role |
|---|---:|---|---|
| `libandroidx.graphics.path.so` | 10,096 | `41e9a793c43a0f4fddb19e33f346bace464f30f888ba7b9eaf96294ea115bfb6` | AndroidX graphics support |
| `libdatastore_shared_counter.so` | 7,784 | `178f89a2c6c9234ddf980dd4cd1f3616186a46b2b932aafa6707abd04c5fd76a` | DataStore shared counter |
| `libsigner.so` | 1,304,840 | `8be033d3423258ac6975c17813eae0ee41c9c743f90ab40e40fa9c1c58eef371` | Bundled signing/security implementation; detailed semantics not assigned |
| `libspotifycyos-lib.so` | 12,040 | `a237f729a91ee31e16f02f9e52b312853db4040c326f4739fefcc748f807a6f9` | Spotify create-your-own-session JNI |
| `libstrobecontroller-lib.so` | 15,864 | `0580e57f9ebda51fa89851c3a40c18bda59e4eae5f9da18615fa01fb421a6b3e` | Session clock, interpolation, and strobe-cycle scheduling |

The last library's bounded behavior is documented in
`N4_NATIVE_FIRMWARE_BOUNDARY.md`. Static library naming does not imply that
Nova firmware itself was acquired.

## Privacy and publication boundary

Raw APKs and generated decode trees remain under ignored `dynamic/` storage.
They contain proprietary program material and signed media references. The
tracked repository publishes only sanitized domains, hashes, counts, versions,
behavioral findings, and reviewed derivatives. Bluetooth addresses, device
serial number, account state, raw HCI/video/audio, and URL credentials are not
included.
