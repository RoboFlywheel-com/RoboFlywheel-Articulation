# Folding ruler — SourceMap

export_category: pictureX_0611_Folding_ruler

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

SOURCES = 1. The single source is a two-blade folding *angle* ruler: two flat
graduated aluminium blades joined at a common through-rivet hub with a graduated
angle dial, each blade an independent revolute pivot about the axle (out-of-plane
Z axis). The Display category reframes this as a **carpenter's folding rule — a
chain of rigid segments joined by pivot hinges**. The rebuild therefore keeps the
source's characteristic building block (a flat, thin, two-colour graduated slat
with a rounded pivot lug and a through-rivet pivot hole) and generalises the
two-blade hub into a serial chain of N segments joined by N-1 out-of-plane revolute
hinges. N (segment count) is the honest multiplicity axis: the source's 2 is the
minimum (a single-fold rule / bevel), and world knowledge of carpenter's folding
rules gives the larger counts.

sync_records:
  - rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad

## Source record

- record: `rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad`
- revision: `rev_000001`
- source_classification: "two-blade folding angle ruler" (`model.py:L99-L104`)

## Slots and candidates

Four orthogonal, freely composable structural slots plus one multiplicity axis.
All four leave the pivot axis (out-of-plane Z through the pivot lug centre)
unchanged, so every candidate combination assembles by local geometry only — no
host-topology change — which is why they are independent slots rather than one
merged family. `core_domain = 2 x 2 x 3 x 3 = 36`; `raw_domain = 36 x 5 = 180`.

### Slot `hinge_style` — pivot hardware at every joint

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| hinge_style | angle_dial | graduated through-rivet dial hub | rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad/rev_000001 | model.py:L124-L187, model.py:L227-L251 | accepted (source-faithful) | frosted dial face disc (`dial_face` r=0.0215), torus reading rim (`dial_rim`), 24 radial graduation ticks (`dial_tick_i`), through axle + rivet cap; the child blade lug is captured under the dial and pivots as an angle reader |
| hinge_style | flush_rivet | plain riveted folding-rule pivot | rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad/rev_000001 | model.py:L150-L167 | accepted (world-knowledge extrapolation) | strips the dial to the source's own axle + rivet cap + rear washer + recess; the classic carpenter's zig-zag rule joint. Same axle, hole, and lug capture as the source, minus the angle-reading disc |

`hinge_style` changes real part geometry at each joint (a graduated reading boss —
disc + torus + 24 ticks — versus a flush rivet head), material-insensitively.

### Slot `end_profile` — segment end / pivot-lug shape

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| end_profile | round_lug | rounded circular pivot lug | rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad/rev_000001 | model.py:L29-L45 | accepted (source-faithful) | `_blade_shape` unions a flat rectangular body with a round pivot lug (`PIVOT_LUG_RADIUS=0.013`) and cuts a `PIVOT_HOLE_RADIUS=0.0033` axle hole |
| end_profile | square_paddle | squared brass-tip paddle end | rec_picturex_0611__folding_ruler__001__png_4fff479c986c41c196c2458f36c551ad/rev_000001 | model.py:L29-L45 | accepted (world-knowledge extrapolation) | traditional boxwood folding rules use a filleted rectangular paddle end instead of a round lug; same centred pivot hole and pivot axis, different silhouette/mesh |

`end_profile` changes the segment-end mesh topology (circular lug vs filleted
rectangular paddle) at every segment end while keeping the pivot hole and Z axis.

### Slot `blade_section` — slat cross-section family

Controlled form-family extrapolation. The **shared profile descriptor** is
`(section_rise_m, section_drop_m, section_flat_x0_m, section_feature_width_m)`,
resolved once in `resolve_config` and used by *every* dependent: the blade mesh
(`_segment_shape`), the stacked level pitch
(`level_pitch = thickness + section_rise + section_drop + style_gap`), hence the
hub seat height `child_lug_top_z_m` and the hub axle length, and the graduation
land (`band_center_x_m` / `band_width_m` derive from `section_flat_x0_m`, and the
mid-span window `_section_span` keeps every raised feature outside the pivot-hub
keepout `DIAL_FACE_R + 0.005`). It is therefore not surface decoration: the same
descriptor moves the joint hardware in Z and the scale in X.

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| blade_section | flat_slat | flat rectangular slat, rise = drop = 0 | rec_...4fff479c/rev_000001 | model.py:L22-L36 (`BLADE_THICKNESS=0.0018`, `body … .rect(BLADE_WIDTH, BLADE_LENGTH).extrude(BLADE_THICKNESS)`) | accepted (source-faithful) | the source blade is a plain flat slat of uniform 1.8 mm section; this candidate reproduces it exactly and keeps `level_pitch` at its previous value |
| blade_section | ridged_spine | T-section: raised centre spine between the pivot bosses | rec_...4fff479c/rev_000001 | model.py:L29-L45 + L83-L94 | accepted (controlled form-family extrapolation) | shares the source slat body and pivot lug; the spine occupies the ungraduated centre seam that the source keeps free for its sparser inner scale (`inner_tick_i`, `model.py:L83-L94`), so the spine and the graduated `+X` edge cannot collide. Stiffened folding rules use exactly this T-rib |
| blade_section | edge_rail | rail section: ungraduated `-X` back edge thickened above and below | rec_...4fff479c/rev_000001 | model.py:L29-L36 + L60-L81 | accepted (controlled form-family extrapolation) | the source graduates only the outer `+X` edge (`x = side * (BLADE_WIDTH - tick_length/2)`, `model.py:L75`), leaving the opposite edge blank; a bevel/rolled-edge steel rule thickens exactly that blank edge. It is the only candidate with a non-zero `section_drop_m`, so it is the one that re-derives the stack pitch downward as well as upward |

### Slot `tip_treatment` — the two free chain ends

The chain has exactly two free ends (segment 0's near pivot end and segment N-1's
far end); every other end is a live pivot. `tip_treatment` changes their mesh
silhouette and feeds `tip_rise_m`/`tip_drop_m`/`tip_extent_m` into the same
section descriptor, so the stack pitch re-derives with the tip as well.

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| tip_treatment | plain_tip | bare slat end | rec_...4fff479c/rev_000001 | model.py:L29-L45 | accepted (source-faithful) | the source blade's far end is the bare extruded slat end — no tip hardware at all |
| tip_treatment | brass_shoe | wrapped metal end shoe, proud on both faces | rec_...4fff479c/rev_000001 | model.py:L121, L150-L167 | accepted (controlled form-family extrapolation) | the source already carries a discrete steel hardware family (`rivet_steel`, `rear_washer`, `rivet_cap`) that sits proud of the slat faces; the end shoe reuses that language at the free end, as on boxwood rules with brass end plates. Adds `tip_rise/tip_drop = 0.6 mm`, which re-derives `level_pitch` |
| tip_treatment | hook_tang | in-plane L hook off the graduated edge | rec_...4fff479c/rev_000001 | model.py:L29-L45, L75 | accepted (controlled form-family extrapolation) | the tang runs off the graduated `+X` edge that the source establishes as the measuring datum (`model.py:L75`), so the hook registers the zero of the same scale. Purely in-plane (rise = drop = 0), so it never enters a neighbouring segment's Z level |

### Multiplicity `segment_count` (N)

- values: `2 | 4 | 6 | 8 | 10`, item_slot = `end_profile` (the repeated unit is the
  graduated segment).
- observed: 2 (the source's two blades, `model.py:L189-L219`).
- derived: carpenter's folding rules are chains of ~6-inch segments, commonly 4, 6,
  8, or 10 segments to reach 0.6-2 m folded lengths; world-knowledge extrapolation.
- validation: N adds exactly N graduated segment parts and N-1 out-of-plane revolute
  hinges (one hub per joint). Each hinge is indexed independently; adjacent segments
  sit on distinct stacked Z levels (`level_pitch`), so they never intersect at any
  fold angle — checked at fully extended (all hinges 0) and fully folded (all hinges
  at the upper limit) via authored `risk_poses` and at N min/max via corners.

## Copy / joint policy for N

- Every segment is a copy of the same source-derived slat mesh (shared within a build
  for the active `end_profile` + dimensions); joints are not copied blindly — each
  interior segment hosts the outgoing hub on its far lug and is captured by the
  previous hub on its near lug. Segment 0's near lug and segment N-1's far lug are
  free ends.
- The chain is serial: segment_0 is the supported root; hinge_i parents segment_i to
  segment_{i+1}. Number of hinges = N - 1.

## Parameters and derivations

- `segment_length_m` (0.140-0.220 m) — pivot-to-pivot slat length; the source blade
  is 0.300 m (a long angle-ruler blade), so folding-rule segments derive a shorter
  honest range. Drives body length, scale span, and tick count.
- `segment_width_m` (0.026-0.040 m) — slat width; source `BLADE_WIDTH=0.034`.
  Derives lug radius, paddle width, and hub clearances.
- Fixed/derived from source: slat thickness (`BLADE_THICKNESS=0.0018`), lug radius
  (`min(0.013, width*0.42)`), pivot hole radius (0.0033), axle radius (0.0030),
  rivet cap (0.0058), dial face (0.0215), torus rim (0.0202/0.00125). `level_pitch`
  is derived per `hinge_style` so the stacked hub of a joint clears the two
  non-adjacent segment levels (larger for the taller dial hub).
- Cross-slot derivation:
  `level_pitch_m = thickness + section_rise_m + section_drop_m + style_gap_m`,
  where `section_rise_m = max(blade_section rise, tip rise)` and
  `section_drop_m = max(blade_section drop, tip drop)` and
  `style_gap_m = 0.0080 (angle_dial) | 0.0035 (flush_rivet)`. Every added
  cross-section or tip relief therefore widens the stacked gap between adjacent
  segment levels by the same amount, and `child_lug_top_z_m`, the hub axle length
  and the dial/cap seat all follow. `band_center_x_m` / `band_width_m` derive from
  `section_flat_x0_m` so the pale scale band always lands on flat metal between
  the section feature and the graduated `+X` edge.

## Category identity and motion

- Every build is a connected serial chain rooted at segment_0, with N graduated flat
  segments and N-1 out-of-plane (Z-axis) revolute hinges, each pivot captured by a
  through-rivet hub (dial or flush). This preserves the source's characteristic
  graduated two-colour slat and through-rivet folding pivot.
- Each hinge folds 0 (extended, colinear) to the upper limit (folded back over the
  parent). Rotation is about Z only, so segment Z levels are pose-invariant.

## Rejected decompositions

- A shared central hub with all segments as independent children (the literal source
  topology) is rejected for N>2: the Display category is an in-line folding chain,
  not a fan of blades about one axle. The source hub geometry is preserved instead as
  the per-joint `angle_dial` hinge candidate.
- Colour/material-only or uniform-scale-only variants are not candidates.
- Text/number glyphs are not modelled (the source uses geometric graduation ticks).
- **Graduation relief as a slot** (engraved vs printed-flat vs raised strip) was
  examined against `model.py:L60-L94` and rejected: the source's ticks and scale
  band are 0.10-0.14 mm proud boxes on the blade face, i.e. surface decoration
  inside a single part. Changing their relief alters no part tree, joint or
  interface, so it would be padding. The graduated *land* still participates in
  the `blade_section` descriptor (band placement derives from
  `section_flat_x0_m`), but it is not a slot of its own.
- **A joint-locking element** (wing screw / detent ring on the hub) was examined:
  the source has `rivet_cap` + `rivet_recess` (`model.py:L156-L167`) but no
  lock — the two blades swing freely over ±175°. A lock candidate would either be
  decoration on the cap or would have to clamp the travel, which is forbidden;
  rejected on both counts.
- **A third `end_profile`** (metal-capped or hooked pivot end) was rejected as an
  `end_profile` candidate because it is not a *pivot* end treatment — it belongs
  on the two free chain ends. It is modelled as the separate `tip_treatment` slot.
