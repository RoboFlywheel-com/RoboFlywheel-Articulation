# pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal — SourceMap

source_map_schema: 1
export_category: pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal
picture_category: 0611
picture_subcategory: hand_operated_metal_brake_for_bending_sheet_metal
category_scope: A hand-operated sheet-metal bending brake — one grounded bed with a bending edge, a clamp beam hinged above it that holds the sheet down, a bending leaf hinged at that edge that folds the sheet up, and the hand levers and adjusters that work them. Press brakes with hydraulic rams, box-and-pan folders sold as complete benches and slip rolls are outside this host.

sync_records:
  - rec_picturex0611_metal_brake_var_bench_top
  - rec_picturex0611_metal_brake_var_bend_stop
  - rec_picturex0611_metal_brake_var_center_lever
  - rec_picturex0611_metal_brake_var_five_fingers
  - rec_picturex0611_metal_brake_var_floor_stand
  - rec_picturex0611_metal_brake_var_screw_down_clamp
  - rec_picturex0611_metal_brake_var_segmented_clamp
  - rec_picturex0611_metal_brake_var_segmented_leaf
  - rec_picturex_0611__hand_operated_metal_brake_for_bending_sheet_metal__001__png_7e96ce87aa024cdbb5f0c1be8c9b999d

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex0611_metal_brake_var_bench_top/rev_000001 | reviewed | used | Mounts the whole brake on a bench-top pad with bolt-down lugs instead of the bare bed. Distinct frame family. |
| rec_picturex0611_metal_brake_var_bend_stop/rev_000001 | reviewed | used | Adds a `bend_stop_fence` carriage on a real PRISMATIC slide behind the bed that sets the fold depth. Distinct accessory. |
| rec_picturex0611_metal_brake_var_center_lever/rev_000001 | reviewed | used | Adds a long centre lever on its own REVOLUTE at mid span, worked instead of the end handles. Distinct accessory. |
| rec_picturex0611_metal_brake_var_five_fingers/rev_000001 | reviewed | used | Breaks the clamp face into separate removable fingers bolted to the beam. Distinct clamp family. |
| rec_picturex0611_metal_brake_var_floor_stand/rev_000001 | reviewed | used | Stands the bed on a welded floor frame with splayed legs instead of a bench pad. Distinct frame family. |
| rec_picturex0611_metal_brake_var_screw_down_clamp/rev_000001 | reviewed | used | Replaces the cam handles with screw-down clamps on their own PRISMATIC travel. Distinct clamp family. |
| rec_picturex0611_metal_brake_var_segmented_clamp/rev_000001 | reviewed | used | Splits the clamp bar into bolted segments across the width with visible joints. Distinct clamp family. |
| rec_picturex0611_metal_brake_var_segmented_leaf/rev_000001 | reviewed | used | Splits the bending leaf into stiffened segments with ribs between them. Distinct leaf family. |
| rec_picturex_0611__hand_operated_metal_brake_for_bending_sheet_metal__001__png_7e96ce87aa024cdbb5f0c1be8c9b999d/rev_000001 | reviewed | used | Origin anchor: a plain bed with a one-piece clamp bar, a plain bending leaf and two cam handles with screw adjusters. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| frame_form | plain_bed | grounded frame | rec_picturex_0611__hand_operated_metal_brake_for_bending_sheet_metal__001__png_7e96ce87aa024cdbb5f0c1be8c9b999d/rev_000001 | model.py:L138-L184 | structure | A bare bed casting with the bending edge and the hinge ears, sitting straight on the table. |
| frame_form | bench_top | grounded frame | rec_picturex0611_metal_brake_var_bench_top/rev_000001 | model.py:L137-L214 | structure | The same bed on a bench-top pad with bolt-down lugs at each corner. |
| frame_form | floor_stand | grounded frame | rec_picturex0611_metal_brake_var_floor_stand/rev_000001 | model.py:L155-L226 | structure | A welded floor frame with splayed legs and a tie rail standing the bed at working height. |
| clamp_form | plain_clamp_bar | clamp beam face | rec_picturex_0611__hand_operated_metal_brake_for_bending_sheet_metal__001__png_7e96ce87aa024cdbb5f0c1be8c9b999d/rev_000001 | model.py:L185-L241 | structure+motion | One continuous clamp bar with a plain nose that lands on the bed across the whole width. |
| clamp_form | segmented_clamp | clamp beam face | rec_picturex0611_metal_brake_var_segmented_clamp/rev_000001 | model.py:L185-L262 | structure | The clamp bar is split into bolted segments with visible joints across the width. |
| clamp_form | finger_clamp | clamp beam face | rec_picturex0611_metal_brake_var_five_fingers/rev_000001 | model.py:L203-L268 | structure | Separate removable fingers are bolted to the beam so box corners can be folded. |
| clamp_form | screw_down_clamp | clamp beam face | rec_picturex0611_metal_brake_var_screw_down_clamp/rev_000001 | model.py:L296-L362 | structure+motion | Screw-down clamps on their own PRISMATIC travel replace the cam handles. |
| leaf_form | plain_leaf | bending leaf | rec_picturex_0611__hand_operated_metal_brake_for_bending_sheet_metal__001__png_7e96ce87aa024cdbb5f0c1be8c9b999d/rev_000001 | model.py:L242-L304 | structure+motion | A plain one-piece bending leaf hinged on the bed edge with a full-width lift bar. |
| leaf_form | segmented_leaf | bending leaf | rec_picturex0611_metal_brake_var_segmented_leaf/rev_000001 | model.py:L247-L333 | structure | The leaf is split into stiffened segments with ribs standing between them. |
| accessory | bend_stop_fence | accessory | rec_picturex0611_metal_brake_var_bend_stop/rev_000001 | model.py:L403-L468 | structure+motion | A `bend_stop_fence` carriage on a real PRISMATIC slide behind the bed that sets the fold depth. |
| accessory | center_lever | accessory | rec_picturex0611_metal_brake_var_center_lever/rev_000001 | model.py:L153-L212 | structure+motion | A long centre lever on its own REVOLUTE at mid span, worked instead of the end handles. |

## Multiplicity and N derivation

- `clamp_station_count = 2 | 3 | 4`, applied to `clamp_form`.
  - `observed_N`: two hand stations in 001 and most forks, five clamp fingers in
    `var_five_fingers`.
  - `derived_N_range = 2..4`: every clamp candidate repeats one complete station across the
    width — a handle and its adjuster, a bar segment, a finger, or a screw clamp — so the loop
    is index-general; the bound comes from keeping a real gap between adjacent stations at the
    narrowest brake and from the per-build pose budget.
  - validation: each station is placed from the same derived width, and the station pitch, the
    handle sweep and the adjuster travel are re-derived with the count.
- `leaf_rib_count = 3 | 5 | 7`, applied to `leaf_form`.
  - `observed_N`: full-width stiffening on the plain leaf and explicit segment ribs in
    `var_segmented_leaf`.
  - `derived_N_range = 3..7`: the rib loop is index-general across the leaf width; the bound
    comes from keeping a real gap between adjacent ribs at the narrowest brake.
  - validation: each rib is placed from the same derived leaf width and its width is re-derived
    from the rib pitch.

## Coverage note

All nine active records in the `0611 / hand_operated_metal_brake_for_bending_sheet_metal`
workbench pool are reviewed and all nine contribute a structural candidate; 001 backs the plain
frame, the plain clamp bar and the plain leaf. The bed, the bending edge, the two hinge lines
and the painted colourway are shared host geometry.

`core_domain = 3 (frame_form) x 4 (clamp_form) x 2 (leaf_form) x 2 (accessory) = 48`;
`raw_domain = 48 x 3 (clamp_station_count) x 3 (leaf_rib_count) = 432`.
