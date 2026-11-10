# Folders (expanding file organizer / folder) — SourceMap

export_category: pictureX_0611_folders

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

This is a picture-derived category with a **single source** (`SOURCES = 1`). The one source
asset is an *expandable hanging-file organizer* shown in its compressed accordion pose:
two stiff end boards enclose N thin file-pocket dividers, every neighbouring divider is
joined by a short **uniform prismatic accordion gap** so the whole stack expands along its
length, and fabric V-fold gussets plus a top hanging-rail crossbar/tabs give the folder its
recognizable silhouette.

sync_records:
  - rec_picturex_0611__folders__001__png__airflex_batch_20260710_44a51551668f45fbacaa1b09d219161b

## Source anchor (record / revision / spans)

record: `rec_picturex_0611__folders__001__png__airflex_batch_20260710_44a51551668f45fbacaa1b09d219161b`
revision: `rev_000001`

| Source element | model.py span | Role |
|---|---|---|
| image-scaled constants (depth, end/pocket height, pitch, gap travel, count=16) | model.py:L18-L30 | proportions + observed N |
| `_add_vertical_leaf` (one thin yawed fabric leaf between two XY endpoints) | model.py:L42-L55 | crease/fold segment generator |
| `_add_gussets` (paired near/far V-folds with an outward crease) | model.py:L58-L91 | per-gap connective fold |
| `_add_side_attachment` (stitched retaining tape reaching back over the previous leaf) | model.py:L94-L114 | neighbour retention / support contact |
| `_add_end_panel` board | model.py:L117-L124 | rigid end cover panel |
| `_add_end_panel` woven top binding + near/far vertical edge bindings | model.py:L125-L140 | cover edge reinforcement |
| `_add_pocket_stage` separator panel | model.py:L143-L150 | interior file leaf body |
| `_add_pocket_stage` ivory crossbar + projecting near/far hanging-rail tabs | model.py:L152-L171 | leaf top hardware / suspension interface |
| `build_object_model` assembly (materials, fixed end, N pocket loop, moving end) | model.py:L182-L267 | chained accordion assembly, terminates open-topped |
| prismatic accordion joints (axis +X, lower=0, upper=gap_travel, mimic first gap) | model.py:L217-L236, L249-L265 | uniform expansion mechanism |
| author tests (uniform prismatic travel, divider spacing, retained contact, expansion) | model.py:L270-L456 | motion / contact invariants |

## Decomposition

The source object is **not** one monolithic "folder family". Reading `model.py` in full, it is a
shared accordion host plus four separable sub-assemblies, each authored by its own helper and each
changing the part tree, the joint graph or an assembly interface:

* the leaf's **top hardware** (`_add_pocket_stage`, L152-L171) vs the cover's **edge binding**
  profile (`_add_end_panel`, L125-L140) — two different top treatments already present in the source;
* the **per-gap connective fold** (`_add_gussets` / `_add_vertical_leaf`, L42-L91), a crease chain
  whose crease count and crease outset are explicit parameters of the generator;
* the **rigid end cover** construction (`_add_end_panel`, L117-L140) = panel + an edge-reinforcement set;
* the **closure** at the moving end — the source has none (L240-L267 ends in a bare board), which is
  itself one member of the folder/wallet closure family.

Shared, source-anchored host preserved by every combination:

> two rigid end covers + N thin interior leaves chained head-to-tail on a uniform prismatic
> accordion, with a per-gap connective fold and a retention tape keeping neighbours in support
> contact (`_add_side_attachment`, L94-L114).

Candidates marked **extrapolated** are controlled world-knowledge extrapolation inside a *form
family* driven by a shared profile taken from the source, with every dependent value re-derived
(crease outset, tab pitch, frame recess, hinge stand-off). No candidate is surface decoration only,
and none replaces a characteristic source structure with a box/cylinder placeholder.

## Accepted candidates (four independent slots)

| Slot | Candidate | Component type | Source type | Exact model.py:Lx-Ly | Accept reason | Key parts/joints/visuals |
|---|---|---|---|---|---|---|
| leaf_top | hanging_rail_crossbar | file_leaf_top_hardware | **source anchor** | model.py:L143-L171 | ivory crossbar seated into the leaf top plus two tabs projecting past the depth edges — an outboard suspension interface | `top_crossbar`, `near/far_rail_tab` |
| leaf_top | staggered_index_tab | file_leaf_top_hardware | extrapolated (shared profile: "bound top edge band + one locator projecting above the leaf top", L152-L171) | model.py:L152-L171 | replaces the continuous rail with a bound edge and one raised index tab whose depth slot cycles by leaf index; different visual set and per-leaf variation | `bound_top_edge`, `index_tab` |
| leaf_top | reinforced_bound_edge | file_leaf_top_hardware | **source structure, transposed host** | model.py:L125-L140 | the end panel's top binding + two vertical edge bindings applied to the leaf: bound perimeter, no projecting hardware, no suspension interface | `bound_top_edge`, `leaf_near/far_binding` |
| gusset_style | v_fold_bellows | per_gap_connective_fold | **source anchor** | model.py:L42-L91 | the source V-fold: 2 yawed leaves per side meeting at an outward crease (4 segments per gap) | `gusset_style__v_fold_bellows__gap_i_{near,far}_leaf_{0,1}` |
| gusset_style | pleated_multifold | per_gap_connective_fold | extrapolated (same crease generator, k=3 creases; outset re-derived 0.35*span) | model.py:L42-L91 | 8 segments per gap, different fold topology inside the same compressed band | `..._pleat_{0..3}` |
| gusset_style | floor_web_gusset | per_gap_connective_fold | extrapolated (same straight-leaf generator with zero creases + a boxed bottom) | model.py:L42-L55 | 3 segments per gap and a new horizontal element spanning the depth: a boxed-bottom bay instead of an open bellows | `..._{near,far}_web`, `..._floor_web` |
| cover_build | bound_board | rigid_end_cover | **source anchor** | model.py:L117-L140 | flat board + woven top binding + two vertical edge bindings | `cover_panel`, `cover_top_binding`, `cover_near/far_binding` |
| cover_build | framed_board | rigid_end_cover | extrapolated (shared profile: "panel of thickness t over depth x height + an edge-reinforcement set") | model.py:L117-L140 | reinforcement closes into a four-rail perimeter frame and the panel recesses to 0.6 t; different part tree and silhouette | `cover_recessed_panel`, `cover_near/far_stile`, `cover_top/bottom_rail` |
| cover_build | wrap_lip_shell | rigid_end_cover | extrapolated (same profile, reinforcement returned as an outward L-section rim) | model.py:L117-L140 | rim wraps over the cover's outward face on all four edges; return direction derived per cover so it never intrudes into the accordion interior | `cover_panel`, `cover_top/bottom_lip`, `cover_near/far_lip` |
| closure | open_top | moving_end_closure | **source anchor** | model.py:L182-L267 (moving end L240-L267) | the source terminates in a bare moving board: zero closure parts, accordion is the only DOF | — |
| closure | fold_over_flap | moving_end_closure | extrapolated (folder/wallet closure family on the source moving-end host) | model.py:L240-L265 | adds one part and one revolute DOF about +Y (0..135 deg) on a knuckle boss growing out of the cover's outer face | part `closure__fold_over_flap__flap`, joint `..._flap_hinge` |
| closure | turn_button_clasp | moving_end_closure | extrapolated (same host, different mechanism) | model.py:L240-L265 | adds one part and one revolute DOF about the accordion axis +X (0..150 deg), sweeping in the depth/height plane: different joint axis, interface frame and part tree | part `closure__turn_button_clasp__clasp`, joint `..._clasp_pivot` |

`core_domain = 3 x 3 x 3 x 3 = 81`; `raw_domain = 81 x 4 = 324` with `divider_count`.

Every combination is required to build — `TemplateDomain` has no compatibility gate. The accordion
host absorbs the differences: the gusset band is derived from the neighbouring parts' thicknesses
and trim envelope, the retention tape reach from `gap_travel_m`, the closure stand-off from the
cover thickness, so cross-slot pairs such as *wrap_lip_shell + fold_over_flap* or
*floor_web_gusset + hanging_rail_crossbar* need no exclusion (both are named corners).

Rejected decomposition: the previous single `folder_family` slot (core 3) is rejected — it fused
four independent sub-assemblies of the source into one enumeration and hid real structural
diversity. Loose-leaf sheets each on their own turning hinge remain rejected as the interior
mechanism: N independently rotating pages fan into each other and the covers, and the source's
interior DOF is the uniform prismatic accordion, which every candidate keeps.

## Multiplicity and N derivation

- `divider_count = 6 | 9 | 12 | 16`, applied to `leaf_top`.
  - `observed_N = 16` (source `POCKET_COUNT`, model.py:L26).
  - `derived_N_range = 6..16`: real expanding organizers / wallets span roughly six to sixteen
    interior leaves; smaller counts are the same mechanism with fewer gaps. `16` keeps the source
    anchor as the upper bound.
  - validation: each N adds exactly one interior `file_leaf` part, one accordion gap joint, one
    fold set and one retention tape pair (the first gap is the prismatic driver; the rest mimic it
    with multiplier `i+1`, matching model.py:L216-L236,L263). The accordion origins, gusset bands,
    tape reach and moving-cover placement are re-derived for every N.

## Independent parameters (honest, not core/raw)

- `depth_m` (0.22–0.34 m; source DEPTH 0.310) — folder depth; derives leaf depth, fold anchor lines,
  crossbar length, tape inset and cover footprint.
- `leaf_height_m` (0.18–0.30 m; source POCKET_HEIGHT≈0.220 / END_HEIGHT 0.245) — interior leaf
  height; derives cover height, tab/rail height, fold band height and closure hinge height.
- `compressed_pitch_m` (0.014–0.024 m; source COMPRESSED_PITCH 0.018) — compressed gap spacing;
  derives accordion joint origins, the gusset band and neighbour clearance.
- `gap_travel_m` (0.006–0.012 m; source GAP_TRAVEL 0.009) — per-gap prismatic travel; is the
  shared accordion joint `upper` limit and derives the retention tape reach and expansion envelope.

## Category identity and motion

- Exactly two `end_board` parts (a fixed root cover and a moving end cover) and N `file_leaf`
  interior parts are required for every combination; the source baseline is two covers + 16 leaves.
- Every accordion gap is prismatic along +X with `lower = 0` (compressed) and
  `upper = gap_travel`; the first gap is the driver and every following gap mimics it with
  multiplier `i+1`, so the stack expands uniformly (source mechanism preserved). No motion is
  clamped; the motion gate exercises the driver at both limits.
- Neighbour support contact is carried by the shared retention tapes, 3 mm thin along the depth
  axis so the deep along-axis reach they need never reads as a collision on all three axes.
- The connective fold lives strictly inside the compressed gap (1.5 mm clear of the previous part's
  trim envelope, 0.5 mm embedded in its own panel), so it is connected to its own part and cannot
  interpenetrate a neighbour at any pose.
- `fold_over_flap` and `turn_button_clasp` each add exactly one revolute DOF built from an
  `AxisInterface` pair via `mate_axes` + `register_interface_mate`; both hinge in the moving cover's
  outer half-space on a 3.5 mm thin knuckle boss (captured contact, no `allow_overlap`).
