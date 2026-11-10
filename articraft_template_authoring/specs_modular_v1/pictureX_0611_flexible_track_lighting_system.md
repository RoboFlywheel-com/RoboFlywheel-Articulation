# pictureX/0611/flexible_track_lighting_system Modular Spec

## Scope

Source-replay modular template for `pictureX/0611/flexible_track_lighting_system`. The identity boundary is an adjustable track-lighting assembly with a rail or flexible track, multiple lamp heads or carriers, visible mounts, and supported pan/tilt/slide articulation. It must not become a generic ceiling lamp or static strip light.

## Sources

- `rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd`
- `rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc`

## Slots And Coverage

- `source_record`: one of the approved 5-star workbench sources.
- `source_index`: deterministic index selected from the source pool by seed.

The template uses the shared `picturex_0611_source_replay` harness to retain the source assembly and motion semantics. Diversity comes from switching between the two reference-derived lighting assemblies.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_flexible_track_lighting_system`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
