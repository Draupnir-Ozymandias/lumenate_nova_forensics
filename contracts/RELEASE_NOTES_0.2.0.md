# Lumenate protocol export 0.2.0 release notes

**Release date:** 2026-09-22

**Status:** Released and frozen

## Scope

Contract `0.2.0` is the first released Lumenate Nova producer contract used by
AVE's strict device-protocol consumer. It replaces prose conventions from
`0.1.0` with explicit audio identity, clock, transition, execution-layer,
overlap, and uncertainty structures.

The release does not alter the pinned AVE evidence-object contract, which
remains version `1.0.0`.

## Frozen schema

| Artifact | SHA-256 |
|---|---|
| `lumenate-protocol-export-0.2.0.schema.json` | `e6b6bf3fdf9d29a7a63d1f5f059584277d1296224aff227724e9620438ed265a` |
| `ave-evidence-object-1.0.0.schema.json` | `7edee601724e13ceb2308482a9f1135acbdb850360de149f1ac009374f26ce18` |

The unversioned `lumenate-protocol-export.schema.json` is byte-for-byte
identical to the frozen `0.2.0` schema at release. Tests pin the versioned
schema's digest and fail if the unversioned current schema drifts from it while
`0.2.0` remains current.

## Principal changes from 0.1.0

- verified, unavailable, or unknown audio-asset identity;
- named clocks with explicit type, origin, unit, resolution, and evidence;
- separate light and audio timeline origins;
- synchronization anchors relating two clocks with uncertainty and method;
- pulse waveform/gating shape;
- typed steps, ramps, interpolation, pauses, resumptions, and discontinuities;
- execution-layer attribution for segments, transitions, and commands;
- explicit overlap declarations; and
- nullable unknowns instead of inferred placeholder values.

## Released empirical fixtures

| Export | SHA-256 |
|---|---|
| `deep-exploration-optical-empirical-0.2.0.json` | `297a5b86b0afbec37cf79016453d60a705be36a4abbc633c4e1439ad4f202d1a` |
| `offline-explore-optical-empirical-0.2.0.json` | `860f098a424435e6901f45444cde2f0a5045dff1983dd9ddda987252a589db3a` |
| `spirit-optical-empirical-0.2.0.json` | `ca5802bef4640555f236a9e4dd45bfb06f88287c9d17744a4e269b67adf36cdf` |
| `vitality-5min-empirical-0.2.0.json` | `1515c82efc5fca9d3399e902d48dc6a54c1fbbb8925ff298f6c836ec8f235655` |

Vitality is the complete-session reconstruction. The other three are bounded
optical capture exports and deliberately preserve unavailable audio identity,
missing anchors, and partial coverage rather than inventing values.

## Producer/consumer verification

At release:

- all four empirical exports validate against the Lumenate producer schema;
- Lumenate's complete test suite passes;
- AVE vendors the exact released schema and byte-identical empirical fixtures;
- all AVE importer/contract tests pass, including malformed-reference,
  timeline, overlap, version, and evidence-schema rejection cases; and
- AVE's complete test suite passes.

## Compatibility and change policy

AVE accepts protocol `0.2.0` only with AVE evidence schema `1.0.0`. Released
`0.1.0` artifacts remain preserved for historical validation but are not
accepted by the current AVE importer.

The frozen `0.2.0` schema must not be edited. Documentation clarifications and
new valid fixtures may be added without changing it. Any validation or semantic
change requires a deliberately versioned successor under the repository's
semantic-versioning policy.
