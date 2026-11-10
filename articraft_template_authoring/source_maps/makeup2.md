# makeup2 — SourceMap

export_category: makeup2

Authoritative records live under `data/records`. `makeup2` is a **hard-shell hinged makeup
compact / eyeshadow palette**: a moulded outer case whose rim carries a rear-hinged mirror lid
that opens to roughly 100°, an N-well pressed-cosmetic pan grid held by one or more carriers
inside the case, and optional front closure hardware.

The pool is two origin records plus nine `_var_` forks. Reading all eleven, the differences
separate cleanly:

* **primary form** — the outer silhouette of case *and* lid changes together
  (rounded-rect / round / four-lobe clover) → one `case_form` slot;
* **carrier topology** — how many cosmetic carriers exist, how they are supported and about
  which axis they move (one swing-up tray / two stacked swing-up tiers / two swivel fan-out
  leaves) → one `tray_topology` slot, because joint count *and* joint axis change;
* **closure hardware** — friction hinge only / spring push-latch (extra prismatic joint) /
  over-centre toggle latch (extra revolute joint) → one `closure` slot;
* **well geometry** — circular pan + domed pressed powder (001 family) vs rounded-rectangular
  inset pan (002 family) → one `well_profile` slot;
* **well count** — 2 / 4 / 6 / 8 → multiplicity `well_count`, *not* a slot (see below).

Frame convention for the rebuild: +X is case width, **+Y is the rear (hinge) side**, −Y is the
front (thumb/latch side), +Z is up, and the case bottom sits at z=0. Both origins already put
the hinge at +Y with the lid panel folding toward −Y; the rebuild keeps that and standardises
`q=0` = fully closed for every joint (the origins encoded `q=0` as the open photo pose with
negative lower limits; that is a datum choice, not a structural difference).

sync_records:
  - rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a
  - rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb
  - rec_0611_makeup2_var_case_form_clover
  - rec_0611_makeup2_var_case_form_round
  - rec_0611_makeup2_var_closure_over_center_latch
  - rec_0611_makeup2_var_closure_push_latch
  - rec_0611_makeup2_var_powder_layout_2_well
  - rec_0611_makeup2_var_powder_layout_6_well
  - rec_0611_makeup2_var_powder_layout_8_well
  - rec_0611_makeup2_var_tray_topology_double_stacked_carrier
  - rec_0611_makeup2_var_tray_topology_fan_out_carrier

## Component slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Diversity axis | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| case_form | rounded_rect | primary-form shell pair | rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a/rev_000001 | model.py:L37-L68, model.py:L133-L156 | accepted | ① primary form | `_rounded_prism` filleted prism drives both `base_shell` (recessed well, two cut hinge reliefs) and `lid_frame` (rim + back plate + mirror opening + two barrel reliefs + hinge neck); rim land seats the lid |
| case_form | round | primary-form shell pair | rec_0611_makeup2_var_case_form_round/rev_000001 | model.py:L45-L75, model.py:L139-L171 | accepted | ① primary form | circular/oval extrude replaces the filleted prism for `base_shell` and for the `lid_frame` rim + back plate; disc shifted toward the well so the rear perimeter still carries the unchanged hinge interfaces; footprint test asserts X≈Y extents |
| case_form | clover | primary-form shell pair | rec_0611_makeup2_var_case_form_clover/rev_000001 | model.py:L54-L103, model.py:L168-L205 | accepted | ① primary form | `_clover_body` unions four offset lobe cylinders into a four-lobe prism used for `base_shell` and for the clover rim + back plate; an extended `hinge_neck` bridges the lobed body to the hinge barrel so the lid stays one connected solid |
| tray_topology | single_tray | swing-up cosmetic carrier | rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a/rev_000001 | model.py:L84-L100, model.py:L255-L300, model.py:L329-L345 | accepted | ② joint topology | one `powder_tray` part: filleted plate with a real cut powder recess + two cut barrel reliefs, `tray_barrel` between two fixed `tray_knuckle_*` on the case, one revolute X hinge `base_to_powder_tray` over a lower base compartment |
| tray_topology | double_stacked_carrier | two stacked cosmetic tiers | rec_0611_makeup2_var_tray_topology_double_stacked_carrier/rev_000001 | model.py:L38-L82, model.py:L178-L221 | accepted | ② joint topology | two-tier shell: bottom plate + lower rim + intermediate shelf + upper rim + external tier groove; two pan tiers at distinct Z; hinge hardware and lid hinge lifted to the taller upper rim height |
| tray_topology | fan_out_carrier | swivel fan-out leaves | rec_0611_makeup2_var_tray_topology_fan_out_carrier/rev_000001 | model.py:L39-L84, model.py:L91-L110 | accepted | ② joint topology | lateral carrier flanges that extend the seating footprint past the tray body, with the lid widened to seat on them; a fan-out carrier that swings laterally rather than lifting |
| closure | hinge_only | friction compact hinge | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb/rev_000001 | model.py:L53-L61, model.py:L202-L225 | accepted | ② joint topology | front thumbnail relief cut into the rim is the only closure feature; a single friction revolute `lid_hinge` with two fixed `base_knuckle_*` and a captured `hinge_pin` retains the lid |
| closure | push_latch | spring push-latch | rec_0611_makeup2_var_closure_push_latch/rev_000001 | model.py:L95-L152, model.py:L228-L318 | accepted | ② joint topology | `latch_catch` tab fused to the lid front, `_latch_housing` boss inside the base front rim, `_latch_hook` on the lid inner front edge and a separate `latch_button` part on a **prismatic** `latch_press` joint along Y |
| closure | over_center_latch | over-centre toggle latch | rec_0611_makeup2_var_closure_over_center_latch/rev_000001 | model.py:L95-L120, model.py:L134-L159, model.py:L259-L286 | accepted | ② joint topology | cam-follower housing fused into the lid hinge edge, semi-cylindrical knuckle reliefs cut for rotation clearance, `_lid_barrel_shape` barrel with a radial cam detent bump, and a snap-through detent hinge with raised effort |
| well_profile | round_pan | circular cosmetic well | rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a/rev_000001 | model.py:L103-L130, model.py:L228-L253 | accepted | ③ component geometry | `_build_tray_pan` circular aluminium pan inside a circular cut recess, `_build_tray_powder` pressed-powder disc plus a shallower top break, and the same circular pan/powder pair in the lower base compartment |
| well_profile | rounded_rect_pan | rounded-rectangular cosmetic well | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb/rev_000001 | model.py:L64-L65, model.py:L150-L163 | accepted | ③ component geometry | `_pan_shape` filleted rounded-rect pan instanced at four inset grid stations inside the moulded tray, one distinct cosmetic shade per pan; distinct part-tree (no circular pan, no domed top break) |

## Multiplicity evidence (`well_count`, not a slot)

| N (well_count) | Record/revision | Exact model.py:Lx-Ly | Observed wells | What actually changed |
|---|---|---|---|---|
| 2 | rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a/rev_000001 | model.py:L88-L100, model.py:L228-L253 | 1 tray well + 1 base well = 2 | baseline: one large circular well per level |
| 4 | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb/rev_000001 | model.py:L150-L163 | 4 | one pan mesh instanced at a 2x2 grid of origins |
| 4 | rec_0611_makeup2_var_powder_layout_2_well/rev_000001 | model.py:L36-L57, model.py:L254-L281, model.py:L305-L343 | 2 tray + 2 base = 4 | the single well per level splits into two; pan radius, powder radius and X offsets are *derived from the count* |
| 6 | rec_0611_makeup2_var_powder_layout_6_well/rev_000001 | model.py:L64-L66, model.py:L159-L176 | 6 | same pan helper, narrowed by the count, instanced over a 3x2 grid |
| 8 / 16 | rec_0611_makeup2_var_powder_layout_8_well/rev_000001 | model.py:L36-L58, model.py:L111-L135, model.py:L137-L146 | 8 tray + 8 base = 16 | `_well_grid` rows x cols helper; well radius, X/Y pitch **and the recess footprint** all derive from the count |

`well_count` is a multiplicity, not a component slot. Across all five records the only thing
that changes with the count is *how many* pans exist and the derived pitch / radius / recess
footprint that follows from packing that many wells into the same carrier: the part tree, the
joint set, the pan construction and the carrier geometry family are identical. Promoting it to
a slot would inflate `core_domain` with duplicate geometry. What *is* genuinely different is
the pan cross-section itself — circular with a domed pressed-powder break (001 family) versus a
filleted rounded-rectangular inset pan (002 family) — so that, and only that, becomes the
`well_profile` slot. Declared values `2 | 4 | 6 | 8`; observed per-record totals are 2, 4, 4, 6
and 16, so the declared range brackets the observed cluster with a modest upper bound that
still packs credibly into the smallest sampled case.

Spacing: wells are split as evenly as possible across the active carriers
(`ceil(N/carrier_count)` on the first carrier), then laid out on a per-carrier
`cols x rows` grid for the lifting carriers and on a constant-radius arc for the fan-out
leaves. Host capacity: `pan_radius_m` derives from the smaller grid pitch times
`well_diameter_ratio`, so the grid always fits the carrier footprint that the case cavity
allows.

## Shared (non-slotted) category anchors

These are present in every record and are rebuilt as shared geometry, not slot candidates.

- **Moulded outer case** — a layered shell (outer wall + floor + rim land + inner cavity),
  never a solid block: 001 model.py:L45-L68; 002 model.py:L38-L61. Rebuilt as the single root
  part `compact_case` with role `compact_case`.
- **Rim seating land** — the flat annulus the closed lid rests on: 002 model.py:L41-L43 (outer
  rim minus inner cut) and the closed-pose seat assertion at 002 model.py:L312-L321. Rebuilt as
  a real `PlaneInterface` land whose width is derived so the lid rim ring always lands on it.
- **Rear hinge hardware** — two fixed side knuckles on the case plus one moving barrel on the
  lid, on one X axis: 001 model.py:L255-L266 and model.py:L308-L312; 002 model.py:L165-L179 and
  model.py:L195-L200.
- **Mirror lid** — rim + back plate + mirror opening + mirror plate + bezel: 001
  model.py:L133-L193; 002 model.py:L68-L106 and model.py:L181-L194. Rebuilt as the part
  `mirror_lid` with role `mirror_lid`.
- **~100° lid travel** — 001 model.py:L346-L362 (105°); 002 model.py:L202-L225 (1.745 rad).
  Rebuilt as one bounded revolute joint with `lower=0` (closed) and `upper=lid_open_rad`.
- **Front thumb relief** — the shallow opening notch in the front rim: 002 model.py:L53-L60;
  double-stacked fork model.py:L69-L76. Present for every `closure` candidate; only
  `hinge_only` parameterises it.
- **Pressed cosmetic fill inside a metal pan inside a cut recess** (three material layers, not
  a decal): 001 model.py:L88-L130; 002 model.py:L64-L65 + L150-L163.

## Parameters and derivations

Independent (unit in parentheses):

- `case_width_m` (m, 0.070–0.104) and `case_depth_ratio` (ratio, 0.82–1.00) → `case_depth_m`.
  Source footprints: 001 0.083x0.072 (ratio 0.867), 002 0.082x0.068 (0.829).
- `case_height_m` (m, 0.019–0.032). Sources: 001 0.017, 002 0.012 lower shell + rim, the
  double-stacked fork ~0.020 to carry two tiers.
- `wall_thickness_m` (m, 0.0018–0.0034) → rim land width, cavity footprint, floor thickness.
- `lid_open_rad` (rad, 1.66–2.00) → the lid revolute upper limit (1.745–1.833 rad observed).
- `clover_lobe_ratio` (ratio, 0.28–0.42), clover only → lobe radius and therefore lobe centre
  offsets, rear knuckle stations and cavity waist.
- `well_diameter_ratio` (ratio, 0.55–0.86) and `well_depth_m` (m, 0.0016–0.0030) → pan size and
  recess depth, hence carrier plate thickness.
- `carrier_lift_rad` (rad, 0.80–1.45) for the two lifting topologies → carrier revolute upper.
- `tier_gap_ratio` (ratio, 0.25–0.40), double-stacked only → how the free cavity height splits
  into the three inter-tier gaps, hence both tier seat heights.
- `fan_angle_rad` (rad, 0.55–1.20) and `leaf_sector_ratio` (ratio, 0.56–0.82), fan-out only →
  leaf swivel limit and leaf sector radius.
- `thumb_notch_ratio` (ratio, 0.16–0.34), hinge-only → width of the front thumb relief.
- `latch_travel_m` (m, 0.0014–0.0032), push-latch only → prismatic button stroke and therefore
  the guided pocket depth.
- `toggle_lever_rad` (rad, 0.55–1.10), over-centre only → toggle release swing.

Key derivations (full DAG in `designs/makeup2.json`):

- `case_depth_m = case_width_m * case_depth_ratio`; `rim_seat_width_m = wall_thickness_m +
  0.0022`; `floor_thickness_m = 0.0022 + 0.35*wall_thickness_m`; `cavity_width_m = case_width_m - 2*rim_seat_width_m` (same for depth).
- `hinge_knuckle_radius_m = clamp(0.20*case_height_m, 0.0026, 0.0048)`;
  `hinge_axis_y_m = case_depth_m/2 - hinge_knuckle_radius_m - 0.0005`;
  `hinge_axis_z_m = case_height_m + 0.45*hinge_knuckle_radius_m`.
- `lid_depth_m = 2*(hinge_axis_y_m - lid_rear_gap_m)` so the closed lid is centred on the case
  and its rear edge never crosses the hinge axis; `lid_width_m = case_width_m *
  (lid_depth_m / case_depth_m)` keeps the lid a scaled copy of the chosen case profile, which
  is what makes the clover and round hosts seat correctly.
- `lid_rim_m = rim_seat_width_m - lid_edge_inset_m - 0.0006` guarantees the lid rim ring lands
  entirely inside the case rim land for every profile.
- `carrier_thickness_m = well_depth_m + 0.0012`; free cavity height
  `carrier_free_h_m = case_height_m - floor_thickness_m - 0.0010 - carrier_count*carrier_thickness_m`
  is what the topology candidates spend on seat heights / tier gaps / leaf pitch.
- `pan_pitch_m = min(usable_w/cols, usable_d/rows)`;
  `pan_radius_m = 0.5*well_diameter_ratio*pan_pitch_m`;
  `recess_radius_m = pan_radius_m + 0.0004`.
- Latch: `latch_pocket_depth_m = latch_travel_m + flange_thickness_m + 0.0006`, so the guided
  slot always contains the full stroke.

## Category identity and motion

- Exactly one root part `compact_case` (role `compact_case`), exactly one `mirror_lid`
  (role `mirror_lid`), `carrier_count` parts with role `well_carrier`
  (1 for `single_tray`, 2 for `double_stacked_carrier`, 2 for `fan_out_carrier`), and
  `closure_actuator_count` parts with role `closure_actuator`
  (0 / 1 / 1 for `hinge_only` / `push_latch` / `over_center_latch`).
- `compact_case -> mirror_lid` is one bounded revolute joint about the real barrel line,
  axis (-1,0,0), `lower=0` closed, `upper=lid_open_rad` ≈ 95°–115°.
- Every `well_carrier` is a direct revolute child of `compact_case`: about X on the rear barrel
  line for the lifting topologies, about Z on the stepped centre pin for the fan-out leaves.
- `push_latch` adds one prismatic joint along +Y (button pressed inward);
  `over_center_latch` adds one revolute joint about X on the front toggle pin.
- Every revolute joint is solved with `AxisInterface`/`mate_axes` on the real pin/barrel line
  and registered with `register_interface_mate`; the moving part's local origin lies on its own
  rotation axis.
- Planar seats (rim land, carrier ledges, leaf thrust shoulders) declare their real supporting
  footprint in `PlaneInterface.extent` and mate with `mate_planes`.
- No `ctx.allow_overlap`. The captured-pin fits the origins allowed by overlap are rebuilt as
  real geometry: side knuckles with a barrel that abuts them axially, a bored leaf hub riding a
  stepped support boss, a latch button captured by a flange inside a real through-pocket, and a
  lid hook that enters a real cut catch window.
- `model.meta["motion_interlocks"]` encodes the physical operating order (the lid must be open
  before a carrier can move, and the upper tier before the lower tier), which is the real
  mechanism, not a suppressed collision.

## Rejected decompositions

- **`powder_layout` as a component slot — rejected.** All four layout forks change only the
  well count and the pitch/radius/recess that derive from it (2-well fork model.py:L36-L57,
  8-well fork model.py:L137-L146). It is multiplicity `well_count`. Only the pan cross-section
  differs structurally between the two origin families, and that is the `well_profile` slot.
- **The mirror, bezel, hinge knuckles and rim land as slots — rejected.** They appear
  identically in every record; they are shared identity anchors. Slotting them would create
  candidates that differ only in surface detail.
- **`case_form` split into separate base-profile and lid-profile slots — rejected.** In both
  the round and clover forks the base shell and the lid frame change *together* (round fork
  model.py:L45-L75 + L139-L171; clover fork model.py:L81-L103 + L168-L205), because the lid
  must nest on the case rim land. A free base x lid profile product would produce
  non-seating combinations, i.e. it is one structural family, not two slots.
- **Carrying the forks' compatibility shortcuts — rejected.** The fan-out fork only widened the
  lid to sit on fixed flanges and the double-stacked fork only fused a second tier into the
  base shell, so neither actually articulated its carriers. The rebuild promotes both to real
  pivots with real clearance instead, because the observed axis/joint-count difference is what
  makes `tray_topology` a slot in the first place.
- **A separate `lid_style` slot (framed mirror vs full-bleed mirror) — rejected.** The two
  origins differ here only in bezel/mirror outline proportion inside the same rim + back-plate
  part tree; that is surface detail under the diversity rules.
