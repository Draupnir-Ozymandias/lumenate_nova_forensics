# Integration contracts

`lumenate-protocol-export.schema.json` is the candidate `0.2.0` producer contract for reconstructed Nova sessions. It pins `ave_evidence_schema_version` to `1.0.0`, matching the current AVE evidence contract. The released `0.1.0` schema and fixture remain available under versioned filenames.

## Candidate 0.2.0 additions

The candidate makes the AVE handoff relationships explicit:

- `audio_asset` records verified identity metadata or explicitly marks it unavailable/unknown;
- `clocks` defines every time source, while the session defines separate light and audio zero points;
- synchronization anchors relate two named clocks and include uncertainty, method, and evidence;
- pulse objects preserve waveform/gating shape;
- transitions distinguish steps, ramps, interpolation, pauses, resumptions, and discontinuities;
- segments, transitions, and commands identify their execution layer; and
- nullable values remain unknown rather than being populated with assumptions.

Segments are ordered by `start_ms`. Any real overlap must be listed by both segments in `overlap_with_segment_ids`; undeclared overlap is invalid.

## Validation

Install the development dependencies and validate an export with:

```bash
python tools/validate_protocol_export.py path/to/export.json
```

The validator performs Draft 2020-12 schema validation plus cross-field checks for unique IDs, references, temporal bounds, segment ordering, and overlap declarations.

`examples/minimal-export.json` demonstrates explicit unknowns. `examples/aligned-export.json` exercises verified audio identity, two clocks, an anchor, a command, pulse shapes, and a transition. Both are sanitized synthetic fixtures, not empirical evidence.

## Migrating from 0.1.0

Add the required `audio_asset`, `clocks`, and `transitions` collections. Add named light/audio origins to `session`; add `execution_layer` and `overlap_with_segment_ids` to every segment; add shape fields to non-null pulse objects; add clock and execution-layer fields to commands; and rewrite anchors as explicit `from_clock_id`/`to_clock_id` relationships. Unknown values should be `null`, `unknown`, and/or explained in `limitations` as appropriate.

Release policy:

1. Validate exports in this repository before publication.
2. Keep a golden, sanitized fixture for each supported contract version. The unversioned fixture follows the current candidate.
3. Validate the same fixture in AVE importer tests.
4. Reject unsupported major versions and unexpected AVE schema versions.
5. Change schemas deliberately under semantic versioning; never edit a released contract silently.

The bundled schema describes the boundary, not raw evidence storage. Commands may omit `payload_hex` when publishing the literal payload would be inappropriate; interpretations must still cite reviewed evidence IDs.
