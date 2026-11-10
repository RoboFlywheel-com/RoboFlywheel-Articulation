# trap_door — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `trap_door` |
| template path | `agent/templates/Door_Trap_door.py` |
| test path (optional) | `tests/agent/test_trap_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children chassis: fixed support + leaf; leaf carries a multiplicity fill axis; hinge slot is single-revolute vs per-copy-revolute bifold) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 (1 parent + 10 converged single-axis fork variants) |
| read_count | 11 |
| read_scope | all 5-star samples in this category (every model.py at `data/records/<id>/revisions/rev_000001/model.py`) |
| source_index_policy | only adopted module sources are indexed below |

**共同骨架 (every sample shares it).** Every trap door is a 3-tier stack rooted on the ground: `well_shaft` (hollow concrete `LatheGeometry.from_shell_profiles`, base at z=0, open bore) → support coaming (`mesh_collar` flush square diamond-mesh plate in 10 samples, OR `curb_frame` raised square kerb in 1 sample) **FIXED** to the shaft top → a movable leaf hinged at the **rear rim** on a real collar-side lug+pin mount, with the leaf carrying a coaxial knuckle barrel. The hinge axis is **horizontal** (world ±X at q=0) so the closed leaf lies FLAT (this is the defining trap-door pose, vs an upright wall door). The leaf is wider than the throat so its rim seats on the throat ring lip; q sweeps 0→~2.0 rad lifting the front edge up past vertical. Dimensions are near-identical across samples: `SHAFT_OUTER_R=0.40`, `SHAFT_HEIGHT=0.52`, `COLLAR_HALF=0.40`, `COLLAR_THK=0.05`, `COLLAR_THROAT_R≈0.325`, `LID_R=0.36` / square `LEAF_SIZE=0.70`.

**真正的拓扑变化轴 (what actually differs).** (A) leaf surface/fill — solid cast disc (LatheGeometry stepped profile), square steel checker-plate (BoxGeometry + diamond tread grid + folded lips), square planked deck (N edge-to-edge `plank_{i}` boards + 2 `batten_{j}`), open rectangular grate (border frame + N see-through `slat_{i}` bars). (B) hinge mechanism — single rear-hinged flap (1 revolute) vs double bi-fold (2 half-leaves `leaf_{i}`, each its OWN revolute on opposite-sign axis). (C) leaf footprint — round disc / square plate / rectangular oblong. (D) top grip/pull — recessed cross-wheel relief (no joint) / flush ring-pull torus / rope loop through 2 eyelets / folding bar handle (a SECOND nested revolute). (Support sub-axis) flush mesh collar vs raised rect kerb curb. Color/material and pure dimensional scaling are NON-structural (template params, not slots).

## 核心身份

A **trap door** is a horizontal access hatch set into a floor/deck/ground plane: a movable leaf that lies FLAT when closed (its hinge axis is horizontal) and swings UP to expose a vertical shaft/well below. The default mature domain is a ground-level utility/cellar/manhole hatch ~0.7–0.85 m across, ~0.5 m deep, sitting on a fixed coaming (a flush square mesh collar or a raised kerb curb) that caps a hollow round well shaft. The leaf is always wider than the throat opening so it seats on a ring lip; the hinge is a real mechanical mount (collar/curb-side lug plates + pin, leaf-side coaxial knuckle barrel). At least one non-fixed joint always exists — the hatch must open.

Identity-bearing features: the FLAT closed pose with a horizontal hinge; the round throat opening through a hollow shaft (visible when open); the rim/throat-lip seating; the diamond-mesh or kerb coaming. Surface/fill, hinge mechanism, footprint and grip vary independently over a shared support skeleton.

Should NOT mix in: an upright **Door** (vertical leaf, vertical hinge axis, threshold on the floor — a trap door's hinge is horizontal and the leaf lies flat); a **Box/chest lid** (lid hinged on a deep closed container, not a floor hatch over a shaft well); a **window/skylight** (glazed pane in a roof slope, no concrete well shaft / mesh collar). See the boundary section.

## 槽位 + 候选模块表

### Slot A：leaf surface / fill

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| solid_cast_slab (baseline) | rec_door_trapdoor (parent) | `_build_lid_body_mesh` L101-L141 (stepped LatheGeometry disc + rim-bolt loop `for i in range(N_BOLTS)` L134-L139); `_build_lid_relief_mesh` L144-L178 | eligible if compatible | solid cast-iron disc; stepped recessed top panel; carries a separate top-grip visual; rim-bolt ring (N_BOLTS=12) |
| checker_plate_steel | rec_trapdoor_var_checkerplate | `_build_hatch_plate_mesh` L94-L157 (flat `BoxGeometry` plate L104-L106 + folded edge lips L108-L130 + centering boss L132-L136 + diamond tread `nx*ny` grid L141-L155) | eligible if compatible | solid square steel plate; raised diamond-tread bar grid on top; folded edge lips on 3 sides (rear is hinge edge) |
| planked_deck | rec_trapdoor_var_plank4 (also _plank6, _plank9) | `_board` L87-L90; plank loop `for i in range(N_PLANKS)` L265-L272; batten loop `for j in range(N_BATTENS)` L276-L285 | eligible if compatible | square timber leaf filled by N edge-to-edge `plank_{i}` boards (shared `_board` helper, regular pitch) banded by 2 cross `batten_{j}` |
| barred_grate | rec_trapdoor_var_grate | `_slat_bar_geometry` L96-L102; `_build_grate_frame_mesh` L105-L135 (4-bar border frame); slat loop `for i in range(N_SLATS)` L328-L336 | eligible if compatible | open rectangular border frame with N see-through parallel `slat_{i}` bars at SLAT_PITCH; you can see into the shaft through the gaps |

Top-grip skins (ring-pull / rope-loop / fold-handle) are NOT separate Slot A candidates — they are the SAME solid_cast_slab body with a different Slot D grip; see Slot D.

### Slot B：hinge mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_revolute_flap (baseline) | rec_door_trapdoor (parent) | `_build_hinge_mount_mesh` L284-L309 (collar lug plates L296-L299 + pin L303-L307); knuckle visual + `collar_to_lid` REVOLUTE L427-L438 (axis=(-1,0,0)) | eligible if compatible | ONE rear-hinged leaf on a single revolute; collar carries one lug+pin set; leaf carries a coaxial knuckle barrel |
| double_bifold | rec_trapdoor_var_biparting | `_build_leaf_body_cq` L127-L155 (CadQuery half-disc, `_half_cutter` L108-L124); `_semicircle_profile` L162-L178; doubled hinge mount `for y_sign in (-1,1)` L369-L400; leaf loop + per-leaf REVOLUTE `for cfg in LEAF_CONFIGS` L462-L536 (`collar_to_leaf_{i}` axis=(y_sign,0,0)) | eligible if compatible | TWO semicircular half-leaves `leaf_{i}` meeting at the center seam; EACH leaf gets its OWN `collar_to_leaf_{i}` REVOLUTE on opposite-sign axis; the only candidate whose copy loop emits a real joint per copy |

Slot B has 2 candidates (min allowed). Pool reason: the converged set on disk only realizes single-flap and bi-fold; lift-out prismatic was deferred (see exclusions). 2 is sufficient because B multiplies with A×C×D×N to clear the gate by a wide margin.

### Slot C：leaf footprint shape

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_hatch (baseline) | rec_door_trapdoor (parent) | `LID_R=0.36` L62; lid disc LatheGeometry profile L113-L121; lid mesh placed at `Origin(xyz=(0,-LID_R,0))` L376 over circular throat | eligible if compatible | round disc leaf over the circular throat; rear rim at the hinge line |
| square_hatch | rec_trapdoor_var_checkerplate (also _plank4/6/9) | checkerplate: `HATCH_SIDE=0.70` L61, plate `BoxGeometry((HATCH_SIDE,HATCH_SIDE,..))` L104-L106, placed `Origin(xyz=(0,-HATCH_HALF,-HINGE_DROP))` L325; plank: `LEAF_SIZE=0.70` L60 | eligible if compatible | square steel/timber leaf over the round throat; square footprint seats on a wider lip |
| rectangular_hatch | rec_trapdoor_var_grate | `GRATE_W=0.66` L61, `GRATE_D=0.70` L62; frame side/cross bars L116-L133; `HINGE_Y=0.36` rear line L84 | eligible if compatible | rectangular/oblong leaf (GRATE_W×GRATE_D) over a rectangular clear span |

### Slot D：grip / pull

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cross_wheel_relief / none (baseline) | rec_door_trapdoor (parent) | `_build_lid_relief_mesh` L144-L178 (hub L157-L159 + 4 spokes `for i in range(N_SPOKES)` L165-L170 + framing torus L173-L176); inlined visual `lid_relief` L381-L386, no joint | eligible if compatible | recessed cross-wheel relief casting (hub + 4 spokes + ring); pure visual, NO movable pull |
| recessed_ring_pull | rec_trapdoor_var_ringpull | `_build_ring_pull_mesh` L146-L163 (torus seated in pocket); pocket added to lid profile L119-L121; visual `ring_pull` L366-L371, no joint | eligible if compatible | flush recessed ring-pull torus seated in a shallow round pocket; inlined visual, no joint |
| rope_loop_pull | rec_trapdoor_var_ropeloop | `_build_rope_loop_mesh` L148-L174 (`tube_from_spline_points` arch); `_build_eyelet_mesh` L177-L183; eyelet loop `for i in range(N_EYELETS)` L394-L402 | eligible if compatible | hemp rope arch + 2 `eyelet_{i}` grommets; inlined visuals, no joint |
| folding_bar_handle | rec_trapdoor_var_foldhandle | `_build_pocket_mesh` L160-L170; `_lug_geometry` L173-L176; `_build_handle_mesh` L191-L209; handle-lug loop `for i in range(N_HANDLE_LUGS)` L426-L435; `lift_handle` part + `lid_to_handle` REVOLUTE L509-L519 | eligible if compatible | recessed pocket + flat bar on its OWN nested `lid_to_handle` revolute (a SECOND joint, child of the lid); 2 `handle_lug_{i}` mounts |

### Support / coaming sub-axis (fixed)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_mesh_collar (baseline) | rec_door_trapdoor (parent) (+ most variants) | `_build_collar_mesh` L181-L281 (square 4-bar frame L190-L198 + diamond-mesh diagonal bars L200-L257 + throat ring L261-L276); `shaft_to_collar` FIXED L406-L412 | eligible if compatible | flush square diamond-mesh collar plate over the round throat; FIXED to shaft top |
| raised_rect_kerb_curb | rec_trapdoor_var_raisedcurb | `_curb_wall_section` L168-L189; `_build_curb_mesh` L192-L234 (base plate L199-L201 + 4 walls `for i in range(N_CURB_WALLS)` L211-L213 + throat ring L217-L232); `shaft_to_curb` FIXED L350-L356; hinge mount on curb top L237-L265 | eligible if compatible | raised square kerb coaming (4 upstanding walls + base + throat ring); lid hinges off the rear wall top; FIXED to shaft top |

## 槽位图（slot graph）

pattern: `mixed` — a fixed support chassis with a parallel movable leaf; the leaf has an internal multiplicity fill axis (planks/slats); the hinge slot is either one revolute or two per-copy revolutes; the grip slot may add a nested revolute.

```
well_shaft (ROOT, on ground z=0)
   |
   +--[FIXED  origin=(0,0,SHAFT_HEIGHT)]--> support_coaming  (Support sub-axis: flush_mesh_collar | raised_rect_kerb_curb)
                                                |  carries collar-side hinge mount (lug plates + pin) on the rear band/wall
                                                |
        single_revolute_flap:                   +--[REVOLUTE  origin=(0,HINGE_Y,HINGE_Z) axis=(-1,0,0) range 0..~2.0]--> leaf
                                                |        leaf = Slot A fill (solid_cast_slab|checker_plate_steel|planked_deck|barred_grate)
                                                |               + Slot C footprint (round|square|rectangular)
                                                |               + Slot D grip (cross_wheel_relief|ring_pull|rope_loop|fold_handle)
                                                |        leaf carries a coaxial knuckle barrel at the part origin (on the hinge axis)
                                                |        if Slot D = folding_bar_handle:
                                                |             leaf --[REVOLUTE  origin=(0,HANDLE_HINGE_Y,HANDLE_HINGE_Z) axis=(-1,0,0) range 0..~1.75]--> lift_handle
                                                |
        double_bifold (mutually exclusive       +--[REVOLUTE  origin=(0,+LID_R,HINGE_Z) axis=(-1,0,0)]--> leaf_0  (rear half-disc)
        with single_revolute_flap):             +--[REVOLUTE  origin=(0,-LID_R,HINGE_Z) axis=(+1,0,0)]--> leaf_1  (front half-disc)
                                                         each half-leaf carries its own coaxial knuckle barrel
```

Interface points:
- **shaft → coaming**: FIXED support; coaming base plane mates onto the shaft-top plane (z=SHAFT_HEIGHT). Invariant: coaming min-z == shaft max-z (no float).
- **coaming → leaf (hinge)**: REVOLUTE. Pivot = a horizontal pin line at the REAR rim, on the collar-side lug+pin mount; the leaf-side knuckle barrel is COAXIAL with the joint axis (sits exactly at the leaf part origin so it never orbits off the pin). Axis world ±X; range lower=0 (flat/closed), upper≈2.0 (open past vertical). HINGE_Z is tuned so the closed leaf bottom embeds ~2 mm into the throat-ring lip seat.
- **leaf → lift_handle (only when Slot D=folding_bar_handle)**: nested REVOLUTE, child of the leaf; pivot at the rear of the lid pocket on lid-side `handle_lug_{i}`; axis world -X; range 0..~1.75.
- **center seam (double_bifold only)**: the two half-leaves meet at the y=0 diameter; opposite-sign axes so they swing apart outward; collar carries TWO lug+pin sets.

Mutual exclusion / derivation:
- Slot B {single_revolute_flap, double_bifold} are mutually exclusive (one leaf+1 joint vs two half-leaves+2 joints).
- double_bifold is realized on disk ONLY with round footprint + solid_cast_slab fill + cross_wheel relief; it is NOT compatible with planked_deck/barred_grate fills or the folding_bar_handle (the half-disc CadQuery body has no plank/slat builder and no pocket). Gated by the compatibility matrix.
- raised_rect_kerb_curb is realized on disk only with single_revolute_flap + round + solid_cast_slab + cross_wheel; treated as compatible with any single-flap leaf in principle but sampled conservatively (see matrix).
- folding_bar_handle is only compatible with a solid (non-see-through) leaf face that has room for a pocket: solid_cast_slab and checker_plate_steel; NOT barred_grate (no solid face) and NOT double_bifold.

## 每槽位 Module Emits / Interfaces

### Slot A / module solid_cast_slab
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` part: `lid_disc` (stepped LatheGeometry disc + rim-bolt loop), grip visual per Slot D, coaxial `lid_knuckle` | parent / L101-L141, L373-L402 |
| internal joints | none internal to fill (the only fill candidate adding a joint is via Slot D folding_bar_handle) | parent / — |
| upstream interface | leaf part origin sits ON the hinge axis (rear rim); disc mesh offset forward by `Origin(xyz=(0,-LID_R,0))` so disc center sits over the throat | parent / L376, L427-L438 |
| downstream interface | `lid_knuckle` barrel coaxial with the revolute axis (rpy pitch π/2 → barrel along X) | parent / L391-L402 |

### Slot A / module checker_plate_steel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hatch_leaf` part: `hatch_plate` (flat box + folded lips + diamond tread grid + centering boss), coaxial `hatch_knuckle` | checkerplate / L94-L157, L322-L342 |
| internal joints | none | checkerplate / — |
| upstream interface | plate mesh offset `Origin(xyz=(0,-HATCH_HALF,-HINGE_DROP))`; rear edge lands on the hinge line; HINGE_DROP sinks the plate top below the pin so the knuckle embeds for connectivity | checkerplate / L325, L83-L86 |
| downstream interface | `hatch_knuckle` coaxial barrel; `collar_to_hatch_leaf` REVOLUTE axis=(-1,0,0) | checkerplate / L337-L342, L354-L365 |

### Slot A / module planked_deck (multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` part: N `plank_{i}` board visuals (shared `_board`, regular pitch), 2 `batten_{j}`, coaxial `lid_knuckle` | plank4 / L265-L298 |
| internal joints | none (planks inlined as leaf visuals, single hinge) | plank4 / — |
| upstream interface | leaf part frame on the hinge line; planks extend forward (-Y), top at z=0 | plank4 / L261-L272 |
| downstream interface | `lid_knuckle` coaxial; `collar_to_lid` REVOLUTE axis=(-1,0,0) | plank4 / L289-L298, L313-L321 |

### Slot A / module barred_grate (multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grate` part: `grate_frame` (4-bar border), N `slat_{i}` bar visuals (shared `_slat_bar_geometry`, SLAT_PITCH), coaxial `grate_knuckle` | grate / L105-L135, L315-L349 |
| internal joints | none (slats inlined, single hinge) | grate / — |
| upstream interface | grate frame authored with rear edge at y=0 (the hinge line), so visual origin is (0,0,0); slats at regular pitch | grate / L315-L336 |
| downstream interface | `grate_knuckle` coaxial; `collar_to_grate` REVOLUTE axis=(-1,0,0) | grate / L340-L349, L361-L372 |

### Slot B / module single_revolute_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | collar-side `hinge_mount` visual = 2 lug plates + pin on the rear band | parent / L284-L309 |
| internal joints | one `collar_to_<leaf>` REVOLUTE axis world -X, range 0..~2.0 | parent / L427-L438 |
| upstream interface | lug plates stand on the rear collar frame band (y∈[0.345,COLLAR_HALF]); `HINGE_LUG_TOP > HINGE_Z + HINGE_PIN_R` so the pin is captured | parent / L296-L299, L86-L91 |
| downstream interface | pin along world X at (0,HINGE_Y,HINGE_Z); the leaf knuckle rides on it | parent / L303-L307 |

### Slot B / module double_bifold
| emits | 描述 | 来源 |
|---|---|---|
| parts | doubled `hinge_mount` (2 lug+pin sets, one per leaf); `leaf_0`/`leaf_1` half-disc bodies (CadQuery `_build_leaf_body_cq`) + half-relief + half-bolts + seat + knuckle | biparting / L369-L400, L462-L513 |
| internal joints | TWO REVOLUTEs `collar_to_leaf_0` axis=(-1,0,0) and `collar_to_leaf_1` axis=(+1,0,0); each emitted inside the leaf copy loop | biparting / L526-L536 |
| upstream interface | rear set at y=+LID_R, front set at y=-LID_R; each leaf part origin on its own hinge axis; disc offset (0, y_sign·LID_R, 0) | biparting / L465-L473 |
| downstream interface | each leaf carries its own coaxial knuckle barrel; the two half-leaves meet at the y=0 seam | biparting / L506-L513 |

### Slot D / module folding_bar_handle (nested joint)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_pocket` recess visual; 2 `handle_lug_{i}` + `handle_hinge_pin` on the lid; separate `lift_handle` part with `handle_bar` | foldhandle / L160-L209, L417-L476 |
| internal joints | `lid_to_handle` REVOLUTE (child of lid) axis=(-1,0,0) range 0..~1.75 | foldhandle / L509-L519 |
| upstream interface | handle hinge at rear of pocket; lid-side lugs support the pin; handle barrel coaxial with the handle axis | foldhandle / L179-L188, L426-L449 |
| downstream interface | `handle_bar` lies flush in pocket at q=0, lifts at q>0 | foldhandle / L191-L209 |

### Support / module flush_mesh_collar (fixed)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mesh_collar` part: `collar_frame` (square 4-bar frame + diamond mesh + throat ring), `hinge_mount` | parent / L181-L281, L354-L367 |
| internal joints | none (fixed support) | parent / — |
| upstream interface | `shaft_to_collar` FIXED at origin (0,0,SHAFT_HEIGHT); base at z=0 of part frame mates shaft top | parent / L406-L412 |
| downstream interface | throat ring gives the leaf a seat; rear band carries the hinge mount | parent / L261-L276 |

### Support / module raised_rect_kerb_curb (fixed)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `curb_frame` part: `curb_body` (base plate + 4 `_curb_wall_section` walls + throat ring), `hinge_mount` on rear wall top | raisedcurb / L168-L234, L308-L320 |
| internal joints | none (fixed support) | raisedcurb / — |
| upstream interface | `shaft_to_curb` FIXED at (0,0,SHAFT_HEIGHT) | raisedcurb / L350-L356 |
| downstream interface | lid seats on the curb WALL TOPS (CURB_TOP_Z); hinge axis raised to curb top; `HINGE_Y=CURB_INNER` | raisedcurb / L84-L85, L237-L265 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| leaf_fill | enum | {solid_cast_slab, checker_plate_steel, planked_deck, barred_grate} | — | choice | deterministic procedural sampler | Slot A table |
| hinge_mechanism | enum | {single_revolute_flap, double_bifold} | — | choice | gated by leaf_fill/footprint (see matrix) | Slot B table |
| footprint | enum | {round, square, rectangular} | — | choice | gated by leaf_fill (see matrix) | Slot C table |
| grip | enum | {cross_wheel_relief, ring_pull, rope_loop, fold_handle} | — | choice | gated by leaf_fill/hinge (see matrix) | Slot D table |
| support_coaming | enum | {flush_mesh_collar, raised_rect_kerb_curb} | — | choice | sampler; curb gated to single-flap (see matrix) | Support table |
| palette_style | enum | {cast_iron, checker_plate_steel, weathered_planks, gunmetal_grate, painted_kerb_curb} (>=4 active per build, footprint/fill-aware) | cast_iron | choice | sampler picks a colorway compatible with leaf_fill | all samples' Material blocks |
| plank_count | int | product `[4, 12]`; test `[4, 9]` | 6 | conditional | only when leaf_fill=planked_deck; weighted small-N | plank4/6/9 / N_PLANKS L62 |
| grate_slat_count | int | product `[6, 20]`; test `[6, 14]` | 12 | conditional | only when leaf_fill=barred_grate; weighted small-N | grate / N_SLATS=12 L68 |
| leaf_radius_scale | float | [0.92, 1.10] | 1.0 | independent | scales LID_R / LEAF_SIZE / GRATE_W·GRATE_D about the throat; clamp | parent LID_R L62, grate L61-L62 |
| shaft_height_scale | float | [0.85, 1.20] | 1.0 | independent | scales SHAFT_HEIGHT (and FIXED support origin Z) | parent SHAFT_HEIGHT L55 |
| throat_radius | float | derived | — | equation | `= SHAFT_INNER_R + 0.01` (unchanged formula) | parent L60 |
| hinge_open_upper | float | [1.7, 2.2] | 2.0 | independent | revolute upper limit; lower fixed at 0.0 (flat closed) | parent MotionLimits L437 |
| curb_wall_height_scale | float | [0.8, 1.3] | 1.0 | conditional | only when support_coaming=raised_rect_kerb_curb; scales CURB_WALL_H; HINGE_Z re-derived | raisedcurb CURB_WALL_H L59 |
| (—) | constraint | — | — | inequality | leaf half-extent ≥ throat_r + 0.02 (leaf seats on the lip, never hangs over the opening); if violated, grow leaf or shrink throat then resample | parent L491-L493 |
| (—) | constraint | — | — | inequality | `HINGE_LUG_TOP > HINGE_Z + HINGE_PIN_R` (pin captured by lugs) — holds after any HINGE_Z re-derivation | parent L87, L487 |
| (—) | constraint | — | — | inequality | grate open ratio > 0.5 ⇒ `grate_slat_count` upper bound from INNER_D / (SLAT_W) so gaps stay see-through; clamp count | grate L421-L427 |
| (—) | constraint | — | — | inequality | fold_handle pocket length+lug clearance ≤ leaf front extent (handle bar fits in pocket) | foldhandle L623-L628 |

连续尺寸采样契约：(1) sample `leaf_radius_scale`, `shaft_height_scale`, `hinge_open_upper` independently; (2) derive `throat_radius` and re-derive `HINGE_Z` (and curb top / lug top) by equation; (3) project leaf/throat/grate-count inequalities and clamp; resample on infeasible; (4) resolve conditional ranges (plank/grate count, curb_wall_height_scale) per the chosen enums BEFORE the continuous draw. All solved in `resolve_config`, never deferred to the builder.

## Multiplicity / Copy Logic

Two independent multiplicity axes (mutually exclusive by leaf_fill), plus structurally-fixed copy loops that are NOT template knobs.

**Axis 1 — plank_count (only when leaf_fill=planked_deck)**
- `count_param`: `plank_count` (source `N_PLANKS`).
- `N_range`: product `[4, 12]`; test `[4, 9]` (the on-disk samples are 4/6/9).
- sampling domain: weighted small-N (4–6 most common; 7–9 medium; 10–12 rare tail).
- copied object: `plank_{i}` edge-to-edge timber boards via shared `_board` helper (plank4 L87-L90, loop L265-L272); plus a fixed 2× `batten_{j}` band loop (L276-L285) — battens are fixed at 2, not a knob.
- naming: `plank_0..plank_{N-1}` (+ `batten_0`, `batten_1`).
- placement: regular pitch `PLANK_W + PLANK_GAP`, planks span full leaf width in X, top at z=0 (plank4 L266).
- joint policy: planks are inlined leaf visuals — NO per-plank joint; the leaf has the single `collar_to_lid` revolute only.
- source/gating: only when footprint=square; PLANK_W re-derived from LEAF_SIZE/N so boards stay edge-to-edge.

**Axis 2 — grate_slat_count (only when leaf_fill=barred_grate)**
- `count_param`: `grate_slat_count` (source `N_SLATS`).
- `N_range`: product `[6, 20]`; test `[6, 14]` (on-disk sample is 12).
- sampling domain: weighted small-N (6–10 common; 11–14 medium; 15–20 rare tail).
- copied object: `slat_{i}` parallel see-through bars via shared `_slat_bar_geometry` (grate L96-L102, loop L328-L336).
- naming: `slat_0..slat_{N-1}`.
- placement: regular `SLAT_PITCH = INNER_D / (N_SLATS+1)`, slat top flush with frame top (grate L74, L329-L333).
- joint policy: slats inlined — NO per-slat joint; single `collar_to_grate` revolute.
- source/gating: only when footprint=rectangular; SLAT_PITCH re-derived; count upper-clamped to keep open-ratio > 0.5.

**Structurally-fixed copy loops (NOT exposed as template knobs):**
- `N_LEAVES=2` bi-fold half-leaves — the ONLY loop that emits a real joint per copy (`collar_to_leaf_{i}`, biparting L462-L536). Fixed at 2 (a bi-fold is by definition two leaves); selecting hinge_mechanism=double_bifold sets it.
- `N_BOLTS=12` rim-bolt loop (parent L134-L139), `N_SPOKES=4` cross-wheel spokes (parent L165-L170), `N_EYELETS=2` rope eyelets (ropeloop L394-L402), `N_HANDLE_LUGS=2` fold-handle lugs (foldhandle L426-L435), `N_CURB_WALLS=4` curb walls (raisedcurb L211-L213): decorative/mechanical fixed counts inlined into a single parent visual or grip; not template-level multiplicity knobs.

## 拓扑多样性审计

总组合数（受 compatibility matrix 约束后的合法离散组合）：

- solid_cast_slab × round × {single_revolute_flap, double_bifold} × {cross_wheel, ring_pull, rope_loop, fold_handle} × {flush_collar, kerb_curb}
  - single_revolute_flap × round × 4 grips × 2 supports = 8
  - double_bifold × round × cross_wheel only × flush_collar only = 1
- checker_plate_steel × square × single_revolute_flap × {cross_wheel, fold_handle} × {flush_collar, kerb_curb} = 1×1×1×2×2 = 4
- planked_deck × square × single_revolute_flap × {cross_wheel} × {flush_collar, kerb_curb} × plank_count∈[4,12] (9 distinct N) = 2 supports × 9 N = 18
- barred_grate × rectangular × single_revolute_flap × {none} × {flush_collar, kerb_curb} × grate_slat_count∈[6,20] (15 distinct N) = 2 supports × 15 N = 30

Discrete-topology distinct count (collapsing continuous scales, counting N buckets):
≈ 8 + 1 + 4 + 18 + 30 = **61 distinct topology classes** ≫ 10.

理由：even ignoring multiplicity entirely, the slot product (Slot A 4 × Slot B {1 or 2 valid} × Slot D valid × Support 2) yields >15 distinct slot signatures; adding plank/slat N buckets pushes distinct topologies past 60. No slot is single-candidate; bi-fold adds a genuinely different joint topology (2 revolutes); fold_handle adds a nested revolute; multiplicity adds variable visual-part counts.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` seeds `ctx.rng`; sampler order = (1) leaf_fill weighted draw; (2) footprint forced/weighted by leaf_fill (cast→round, checker/plank→square, grate→rectangular; cast may also allow square? NO — keep cast→round for fidelity to the converged set); (3) hinge_mechanism (double_bifold ONLY eligible when leaf_fill=solid_cast_slab AND footprint=round, else single_revolute_flap); (4) grip weighted, gated (grate→none; fold_handle only on solid/checker single-flap; bifold→cross_wheel); (5) support_coaming weighted (kerb gated off bifold); (6) multiplicity N per-axis weighted small-N; (7) continuous scales per the sampling contract. `slot_choices_for_seed(seed)` returns the stable `(slot, module)` list (enums + N buckets that change topology; continuous scales excluded). Topology target: 1000-seed distinct ≥300 is NOT expected here (discrete classes cap ~61 + continuous-scale variety); this is justified — trap_door is a tightly-constrained category whose identity forbids arbitrary slot mixing, so slot choice tuple distinct is bounded by the legal compatibility matrix, not undersampling. Document ≈61 as the ceiling. Regression overrides: none planned at spec time; if a specific seed later fails, add it with a recorded reason — do NOT use a curated/modulo table as the main domain.（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization: `leaf_radius_scale` [0.92,1.10], `shaft_height_scale` [0.85,1.20], `hinge_open_upper` [1.7,2.2], `curb_wall_height_scale` [0.8,1.3] (conditional). All clamped/derived in `resolve_config`; throat_radius and HINGE_Z (and curb top, lug top) re-derived by equation; leaf-seat / pin-capture / grate-open-ratio / pocket-fit inequalities projected. These change only safe proportions and never break the FIXED support, the hinge InterfaceSpec, or the multiplicity helpers.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | leaf_fill → footprint (forced) → hinge → grip → support → N → scales; weighted small-N | slot_choices_for_seed matches build choices |
| compatibility matrix | bifold⇔(cast+round+cross_wheel+flush_collar) only; fold_handle⇔solid/checker single-flap; grate⇔no grip; kerb⇔single-flap; plank⇔square; slat⇔rectangular | no floating, no穿模, hinge axis/range, closed-flat pose, max multiplicity, grate open-ratio, fold-handle pocket fit |
| controlled local variation | 4 clamped scales (1 conditional) | proportions vary; leaf still seats on lip; pin captured; closed pose flat; shaft hollow |
| regression overrides | none (add only on a recorded failure/reviewer pick) | previously failed or reviewer-selected cases only |
| random sweep | seeds 0–49 initial; 0–999 maturity audit | MatingContract/closed-pose failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A leaf fill | 4 | yes | yes | |
| B hinge mechanism | 2 | yes | no | 2 is min; pool only realizes flap + bifold; lift-out deferred |
| C footprint | 3 | yes | yes | derived from leaf_fill |
| D grip / pull | 4 | yes | yes | one (fold_handle) adds a nested joint |
| Support coaming | 2 | yes | no | flush collar vs raised kerb |

## Validator

- slot_choices_for_seed returns implemented module names only
- config_from_seed uses deterministic procedural sampling for all ordinary seeds; seed=0 not special
- compatibility matrix prevents illegal combos (bifold+plank, fold_handle+grate, kerb+bifold, plank on round, etc.)
- regression overrides absent/sparse and justified; no curated/modulo main domain
- controlled local scales clamped/derived in `resolve_config`; cannot break support FIXED, hinge interface, clearance, joint origin, multiplicity
- cross-part scale dependencies (throat_radius equation; HINGE_Z/curb-top/lug-top re-derivation; leaf-seat / pin-capture / open-ratio / pocket-fit inequalities) resolved in `resolve_config`
- critical InterfaceSpec/MatingContract present: shaft→coaming FIXED contact (coaming min-z==shaft max-z); coaming→leaf REVOLUTE with leaf-side knuckle coaxial on collar-side pin; (bifold) two opposite-sign revolutes; (fold_handle) nested lid→handle revolute
- key joints: hinge axis ≈ world ±X (|axis.x|>0.9), horizontal; range lower=0 (flat closed), upper≈2.0; handle/leaf upper>0.5
- closed pose: leaf lies FLAT (z_span<0.12, x_span & y_span>0.5), seats on coaming (expect_contact), covers throat in plan
- open pose: leaf max-z rises >0.20 above closed; stands tall (z_span>0.45)
- shaft hollow (throat clears bore); nothing floats
- copied objects follow `plank_{i}`/`slat_{i}`/`leaf_{i}` naming, regular pitch, joint policy (no per-plank/slat joint; per-leaf joint only for bifold)

## Reject cases

- Vertical/upright leaf or vertical hinge axis (that is a wall Door, not a trap door) — hinge must be horizontal, closed leaf flat.
- Leaf narrower than the throat so it falls through / hangs over the opening (violates leaf-seat inequality).
- Hinge pin not captured by the lug plates (`HINGE_LUG_TOP ≤ HINGE_Z + HINGE_PIN_R`) → floating/unsupported joint.
- Coaming floating above or sunk into the shaft top (FIXED contact invariant broken).
- A trap door with NO non-fixed joint (everything fused) — the hatch must open.
- Illegal slot combo emitted (e.g. bifold with planked fill, fold_handle on a see-through grate, kerb curb on a bi-fold) — sampler bypassed the compatibility matrix.
- Grate with too many slats so gaps vanish (open ratio ≤ 0.5) — not see-through.
- Solid/throat geometry not hollow (shaft bore filled) — loses the "well below" identity.
- Closed bi-fold leaves overlapping/penetrating at the center seam, or swinging the wrong way (same-sign axes) instead of apart.

## 与相邻类别的边界

- 不该混入：**Door (upright wall door)** — vertical leaf, vertical hinge axis, threshold at the floor, no horizontal flat-closed pose and no shaft well below. Trap door's defining feature is the horizontal hinge / flat closed leaf over a hollow shaft.
- 不该混入：**Box / chest / container lid** — a lid hinged on a deep closed box with walls and a floor; a trap door's "container" is an open well shaft (hollow, bottomless within the model) capped by a flush collar or kerb, not an enclosed box.
- 不该混入：**Skylight / roof window** — glazed pane on a sloped roof; a trap door is opaque cast iron / steel / timber / grate on a square mesh collar over a round concrete well, not glazing on a roof slope.
- 不该混入：**Floor grate / drain cover (non-opening)** — a fixed grille with no hinge; a trap door always retains at least one real revolute (it opens).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D + Support | solid_cast_slab / single_revolute_flap / round / cross_wheel / flush_mesh_collar | rec_door_trapdoor (parent) | L101-L178 (lid+relief), L181-L309 (collar+hinge), L312-L329 (shaft), L406-L438 (joints) | full baseline skeleton + all baseline modules |
| S2 | D | recessed_ring_pull | rec_trapdoor_var_ringpull | L146-L163 ring pull; L119-L121 pocket profile; L366-L371 visual | ring-pull grip on solid cast disc |
| S3 | D | rope_loop_pull | rec_trapdoor_var_ropeloop | L148-L183 rope+eyelet; L394-L402 eyelet loop | rope-loop grip + 2 eyelets |
| S4 | D / nested joint | folding_bar_handle | rec_trapdoor_var_foldhandle | L160-L209 pocket/lug/handle; L426-L449 lugs+pin; L509-L519 lid_to_handle REVOLUTE | folding bar handle on a nested revolute |
| S5 | A / C | checker_plate_steel / square | rec_trapdoor_var_checkerplate | L94-L157 plate+tread+lips; L322-L342 leaf; L354-L365 hinge | square steel checker-plate leaf |
| S6 | A / C / N | planked_deck / square / plank_count | rec_trapdoor_var_plank4 (+_plank6 L63, _plank9 L65) | L87-L90 _board; L265-L298 plank+batten loops | N-plank timber deck multiplicity |
| S7 | A / C / N | barred_grate / rectangular / grate_slat_count | rec_trapdoor_var_grate | L96-L135 frame+slat helper; L315-L349 grate+slats | N-slat see-through grate multiplicity |
| S8 | B | double_bifold | rec_trapdoor_var_biparting | L108-L178 half-disc CadQuery; L369-L400 doubled mount; L462-L536 leaf loop + 2 REVOLUTE | bi-parting two-leaf hinge mechanism |
| S9 | Support | raised_rect_kerb_curb | rec_trapdoor_var_raisedcurb | L168-L234 curb body+walls; L237-L265 hinge on curb top; L350-L356 FIXED | raised kerb coaming support sub-axis |

## 模板实现备注（可选）

- All samples share `_build_collar_mesh` / `_build_hinge_mount_mesh` / `_build_shaft_mesh` verbatim — factor into shared helpers; the curb support swaps `_build_collar_mesh`→`_build_curb_mesh` and re-derives HINGE_Y/HINGE_Z to the wall top.
- The leaf-side knuckle MUST sit at the leaf part origin (on the joint axis) with rpy pitch π/2 so the barrel lies along X and never orbits off the pin — load-bearing for the "no floating joint" check.
- bi-fold uses CadQuery (`mesh_from_cadquery`, `import cadquery as cq`) for the half-disc body; the other fills use pure SDK geometry. Keep bi-fold isolated to its compatibility cell.
- allow_overlap is element/part-scoped in every sample (lid↔collar for knuckle/seat; lid↔lift_handle for the pocketed bar; per-leaf↔collar for bifold) — replicate the same scoped allow_overlaps in the composite template tests.
- Deferred (NOT in seed domain, real-world plausible but not on disk): lift-out prismatic lid, glazed skylight pane, square diamond-mesh leaf-fill. Add only via future gap forks if a wider pool is wanted; current pool is covered without them.
