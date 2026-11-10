# pictureX/0611/flaring_tool_with_cone_and_clamp Modular Spec

## Scope

Source-replay modular template for the `pictureX/0611/flaring_tool_with_cone_and_clamp` class. The identity boundary is a tube-flaring hand tool: clamp bar or yoke, cone/anvil, screw or press motion, visible handles, and supported tightening articulation. It must not drift into a generic vise, pliers, or pipe cutter.

## Sources

- `rec_picturex_0611__flaring_tool_with_cone_and_clamp__001__png__airflex_batch_20260710_52f7016c9eb84902806fb01f2892cffe`
- `rec_picturex_0611__flaring_tool_with_cone_and_clamp__002__png__airflex_batch_20260710_11b92ba5965f4a87b12afcd7024803e9`

## Slots And Coverage

- `source_record`: one of the approved 5-star workbench sources.
- `source_index`: deterministic index selected from the source pool by seed.

The template uses the shared `picturex_0611_source_replay` harness. It preserves the source part tree, joints, materials, and image-bound geometry, tightens motion limits for stable sweep QC, and records slot choices in metadata.

## Validation

Run `uv run articraft template sweep-pipeline pictureX_0611_flaring_tool_with_cone_and_clamp`. The template self-test requires parts, at least one articulation, at least one non-fixed joint, and source metadata.
