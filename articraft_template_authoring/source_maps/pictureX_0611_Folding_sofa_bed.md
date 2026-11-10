# Folding sofa bed — SourceMap

export_category: pictureX_0611_Folding_sofa_bed
slug: pictureX_0611_Folding_sofa_bed

Authoritative record lives under `<ARTI_SKILL_ROOT>/arti-template/data/records`.
SOURCES=1: a single wide gray tufted click-clack sofa bed with a fold-out foot mattress
and fold-down deck legs. There are no variant records, so slots/candidates/N/params are
abstracted from the one source by controlled world-knowledge extrapolation per
`VISUAL_DIVERSITY_MODEL.md`. The fold-out conversion mechanism (reclining backrest + a
foot mattress panel that folds out at the front + fold-down deck legs that support the
extended foot) is the fixed category identity and is preserved in every candidate; only
peripheral, genuinely-variable components (base support legs, arm bolsters, deck-leg
style) form structural slots.

sync_records:
  - rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c

## Source mechanism (preserved identity)

| Entity | Source `model.py:Lx-Ly` | Role | Motion |
|---|---|---|---|
| frame (root) | model.py:L180-L251 | upholstered base + hinge-bearing frame | fixed root |
| seat_deck | model.py:L255-L290 | center seat / middle bed panel | source hinged; rebuilt as fixed middle bed deck |
| pullout_carriage | model.py:L293-L324 | guided front support frame | source prismatic; folded into fixed frame support in rebuild |
| front_mattress_panel | model.py:L329-L369 | folding foot mattress | REVOLUTE fold-out about +x, source range 0..pi |
| backrest | model.py:L372-L400 | reclining rear mattress panel | REVOLUTE recline about +x, source range -0.18..1.40 |
| armrest_0/1 | model.py:L405-L431 | upholstered side bolsters | source pivoting; rebuilt as fixed arms |
| support_leg_0..3 | model.py:L434-L454 | splayed base support legs | source tiny-range revolute splay; rebuilt as fixed supports |
| deck_leg_0/1 | model.py:L459-L481 | fold-down foot-extension supports | REVOLUTE fold-down about +x, source range 0..pi/2, pivot pinned to front panel |
| linkage_0/1 | model.py:L485-L499 | exposed side conversion hardware | source decorative revolute; folded into fixed frame hardware |

Rebuild rationale: the source used several tiny-range or decorative revolute joints
(base-leg splay ±0.14, side linkages ±0.55, arm counter-fold, seat lift, 0.12 m carriage
travel). These are not the category's identifying articulation and the source only ever
validated the single simultaneous conversion pose; independently swept they add collision
risk with no identity value. The rebuild keeps the three identifying articulations
(backrest recline, foot-panel fold-out, fold-down deck legs) and their real supports, and
makes the seat/arms/base-legs/rear support rigid, so every swept pose is genuinely clear
without motion clamping or whole-part overlap allowances.

## Accepted structural slots (controlled extrapolation from the single source)

| Slot | Candidate | Status | Record/Revision | Exact model.py:Lx-Ly | Diversity axis | Key parts/joints/helpers |
|---|---|---|---|---|---|---|
| base_leg | splayed_chrome | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L122-L134 | geometry | source round chrome tube + ball foot, splayed |
| base_leg | tapered_walnut | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L434-L454 | geometry | square tapered solid wood leg (world-knowledge variant) |
| base_leg | hairpin_steel | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L434-L454 | part_tree | thin bent double-rod hairpin leg (world-knowledge variant) |
| arm_style | bolster_arm | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L405-L419 | geometry | source cylindrical pillow bolster arm |
| arm_style | roll_arm | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L405-L419 | geometry | rounded rolled upholstered arm (world-knowledge variant) |
| arm_style | track_arm | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L405-L419 | geometry | low flat square track arm (world-knowledge variant) |
| deck_support | single_post | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L122-L134 | geometry | source one tube leg + ball foot per station |
| deck_support | splayed_strut | accepted | rec_picturex_0611__folding_sofa_bed__001__png_rerun_48f5fc4582674cabbb6693a08e92001c/rev_000001 | model.py:L459-L481 | part_tree | twin splayed struts + crossbar foot per station (world-knowledge variant) |

Each `base_leg` candidate builds 4 rigid corner legs; each `arm_style` candidate builds 2
rigid arms; each `deck_support` candidate builds the fold-down deck-leg station geometry
used for every deck leg. All three slots keep the core mechanism and every support real.

## Multiplicity

- `deck_leg_count = 2 | 3 | 4`, applied to `deck_support`. It adds N fold-down deck-leg
  stations spaced across the foot panel, each an independent REVOLUTE (+x) joint child of
  the foot panel with its own pivot receiver bracket. Source shows 2; wider beds use 3–4.
  Min/max N prove structural growth; each station has a real captured pivot and a floor-
  reaching foot in the deployed bed pose.

## Parameters and derivations

- `width_m` (1.70–2.10 m): overall sofa/bed width; derives frame, seat, backrest, foot,
  arm span, and support-leg x positions.
- `seat_depth_m` (0.55–0.68 m): seat/middle-panel depth; derives frame depth, foot-panel
  length, backrest length and the rear support-leg y position.
- `bed_height_m` (0.38–0.44 m): deployed bed-surface height; derives seat top, hinge
  heights, and deck-leg length (leg length = bed_height so the deployed foot reaches the
  floor).
- Foot-panel folded rest clears the seat and upright backrest; deck-leg spacing derives
  from foot-panel length and deck_leg_count.
- Palette (upholstery/wood/metal colors) and tufting counts do not contribute to core/raw.

## Category identity and motion

- Exactly one `sofa_frame` root, one fixed `seat_deck`, one `backrest`, one `foot_panel`,
  N `deck_leg`, four `support_leg`, two `armrest`.
- `frame_to_backrest`, `frame_to_foot_panel`, and each `foot_panel_to_deck_leg_i` are
  REVOLUTE about (1,0,0), built from `mate_axes` + `register_interface_mate`.
- Neutral (all revolute at lower) = folded sofa: backrest upright, foot panel folded over
  the seat, deck legs stowed. Foot panel upper = deployed forward at bed height; deck legs
  upper = deployed downward to the floor; backrest upper = reclined flat rearward onto the
  fixed rear support legs. Deployed bed = all three panels coplanar at bed height.
- Each deck-leg pivot is genuinely captured in a per-element receiver bracket on the foot
  panel; declared per-element (elem_a pivot boss / elem_b receiver), never whole-part.

## Rejected decompositions

- Independent conversion-mechanism families are rejected: with one source they would be the
  same mechanism reskinned (fabricated structure), so the mechanism is a fixed shared core.
- No motion clamping, no whole-part overlap allowance, no source-replay import: the source
  thin shell relied on all three and is discarded.
