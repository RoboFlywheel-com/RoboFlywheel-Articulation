# pictureX/0611/Floor-standing_drafting_table Modular Spec

## Scope

Source-replay modular template for `pictureX/0611/Floor-standing_drafting_table`. The synced image-bound source depicts a floor-standing drafting/easel table form with a hinged panel/frame, splayed support, and travel-limiting spreader. It must not drift into a fixed table, desk, or wall-mounted board.

## Sources

- `rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92`

## Slots And Coverage

- `source_record`: the approved 5-star workbench source.
- `source_index`: deterministic source index, currently `0`.

The existing authored `drafting_table.py` remains available for the broader generic drafting-table category. This template intentionally binds to the exact `pictureX/0611/Floor-standing_drafting_table` source.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_Floor_standing_drafting_table`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
