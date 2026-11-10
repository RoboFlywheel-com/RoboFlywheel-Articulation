# pictureX/0611/Folding_ruler Modular Spec

## Scope

Source-replay modular template for `pictureX/0611/Folding_ruler`. The identity boundary is a folding measuring rule with narrow graduated blades, pivot rivets, overlapping segments, and supported revolute folding joints. It must not drift into scissors, calipers, or a single rigid ruler.

## Sources

- `rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad`

## Slots And Coverage

- `source_record`: the approved 5-star workbench source.
- `source_index`: deterministic source index, currently `0`.

The source-replay harness preserves the source blade count, hinge layout, and material/color interpretation while making the source choice explicit in sweep metadata.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_Folding_ruler`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
