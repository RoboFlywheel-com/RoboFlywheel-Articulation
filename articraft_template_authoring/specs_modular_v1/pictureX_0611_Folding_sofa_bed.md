# pictureX/0611/Folding_sofa_bed Modular Spec

## Scope

Source-replay modular template for `pictureX/0611/Folding_sofa_bed`. The identity boundary is a convertible sofa-bed with upholstered back/seat or mattress panels, base frame, support legs, and supported folding or sliding conversion articulation. It must not drift into a fixed sofa, ordinary bed, or side table.

## Sources

- `rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c`

## Slots And Coverage

- `source_record`: the approved 5-star workbench source.
- `source_index`: deterministic source index, currently `0`.

The template binds to the exact requested `Folding_sofa_bed` image-conditioned source. Nearby sibling folders such as `Folding_sofa_bed1` are not mixed into this template unless separately approved.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_Folding_sofa_bed`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
