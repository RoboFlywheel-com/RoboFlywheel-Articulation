# pictureX/0611/folders Modular Spec

## Scope

Source-replay modular template for `pictureX/0611/folders`. The identity boundary is a document folder or folder stack with covers, tab/flap/fastener details when present, page or divider geometry, and real hinge/lift articulation. It must not drift into a binder, box, or static paper stack.

## Sources

- `rec_picturex_0611__folders__001__png__airflex_batch_20260710_44a51551668f45fbacaa1b09d219161b`

## Slots And Coverage

- `source_record`: the approved 5-star workbench source.
- `source_index`: deterministic source index, currently `0`.

The existing `Stationary_Folder.py` template remains available for the broader stationary folder category. This pictureX template binds to the image-conditioned `folders` source.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_folders`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
