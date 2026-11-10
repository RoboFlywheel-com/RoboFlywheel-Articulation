# door_other — Modular Spec

> **⚠️ HETEROGENEITY FLAG — READ FIRST (template author).** Door/Other is a
> deliberate **catch-all "other single door" bucket**. The two 5★ parents are
> two genuinely DIFFERENT objects, not minor variants of one door:
>   - **rec_door_dutch** — a wood-casing Dutch (stable) door whose leaf is split
>     HORIZONTALLY into an independently-swinging upper + lower leaf (TWO vertical
>     revolute joints on the same jamb).
>   - **rec_door_other_arched** — a stone-surround rustic plank door: ONE solid
>     leaf on ONE vertical revolute, plus a hanging iron ring-pull on a SECOND,
>     horizontal revolute.
>
> They differ in split mechanism, head profile, leaf infill, and hardware **all
> at once**, and the on-disk pool splits into TWO structurally-disjoint shells:
>   - **Dutch shell** (wood casing): `door_frame`(`hinge_jamb`/`latch_jamb`/`head_jamb`/`threshold`/`casing_*`) + `upper_leaf` + `lower_leaf`.
>   - **Arched shell** (stone surround): `stone_frame`(`stone_arch`/`jamb_pintles`) + `door` + `ring_pull`.
>
> **Organizing decision (per the source map):** the **split-mechanism slot
> (Slot A)** is the PRIMARY structural axis and carries the most distinctive
> articulation. Head-profile (Slot B) and leaf-infill/hardware (Slot C) are
> ORTHOGONAL slots. BUT the two shells share almost no code, so **Slot A is the
> shell selector**: choosing a Slot A module also selects the frame context
> (wood casing vs stone surround) and gates which Slot B / Slot C modules are
> legal. See the **compatibility matrix** (§9) — several cross-shell cells are
> blocked by design and MUST be gated, not forced. The first template should ship
> the two parent corners + the converged variant fills; cross-shell unification
> (e.g. a single-leaf-in-Dutch-casing, or Dutch×plank) is explicitly NOT in
> scope for v1.

## 元信息
| 项 | 值 |
|---|---|
| slug | `door_other` |
| template path | `agent/templates/Door_Other.py` |
| test path (optional) | `tests/agent/test_door_other_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel named slots: split_mechanism + head_profile + infill, on a revolute spine) × multiplicity (plank / lite / slat count) |

`mixed`：核心是一个 split-mechanism revolute spine（Slot A）选定外壳 (frame) + 叶片
拓扑，head_profile (Slot B) 与 infill/hardware (Slot C) 作为正交 module 填充同一叶片；
叠加 plank / lite / slat 的 multiplicity 复制轴。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 parents + 8 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读结论（结构变化轴）：

- **Split-mechanism is the true topology axis (Slot A).** Three distinct joint
  topologies appear: (1) Dutch = TWO independent vertical revolutes (upper + lower
  leaf on the same jamb); (2) single solid leaf = ONE jamb-edge vertical revolute
  (+ an optional ring-pull horizontal revolute); (3) center-pivot = ONE vertical
  revolute through the leaf CENTERLINE with bidirectional swing and top/bottom
  socket bearings. These differ in joint count, root coordinate, and bearing
  interface — the strongest structural signal in the category.
- **Two disjoint shells.** Dutch shell uses a rectangular wood casing/jamb root
  with a HINGE_LAP overlap policy; arched/pivot shell uses a CadQuery stone-arch
  root with captured-pin (pintle) / pivot-socket bearing policy. Slot A selects
  the shell.
- **Head profile (Slot B) is a clean orthogonal axis** built almost entirely from
  one parametrized helper `_arched_profile_face(width, spring, top|rise)`: flat
  square (Dutch), full semicircle (radius=W/2), broad barn segmental (rise 0.20 on
  a 1.20 m leaf), shallow segmental (rise 0.12), and flat-top-rect-in-arched-
  surround (leaf flat, arch lives only in the stone tympanum above).
- **Infill/hardware (Slot C) varies the leaf face + latch hardware** independently
  of head profile: glazed-lite-over-raised-panel + knob, solid-raised-panel-both-
  leaves + lever, louvered-slat-vent + knob, vertical-plank-strap + ring-pull,
  porthole-glazed-round-light + ring-pull.
- **Multiplicity** appears as plank count (best-sampled, 4 distinct N), lite count
  (2×2 grid, hand-written, single sample), and louver slat count (loop-emitted,
  single sample).
- Pure size / color / material / decoration-density differences are NOT treated as
  slots or candidates (e.g. roundtop's LEAF_W=1.20 vs 0.90 is a continuous
  proportion param, not a slot; only its barn-arch profile is the Slot B candidate).

## 核心身份

Door/Other 是 **"其它单扇门"** 的异质收集类：单扇（或单扇水平对开）独立门，带真实
开合活动件，立在地面上（几何从 z=0 向上）。物理含义是一道可开合的门：一个固定 frame
（木门套或石拱洞口）作为 root，一个或两个叶片在 revolute hinge 上摆动；可选的把手 /
拉环 hardware。坐标约定（两壳一致）：**X = 门宽**（hinge 边在小 X，latch 边在大 X；
center-pivot 例外，以叶片中线为 x=0），**Y = 厚度**（房间 / 正面在 +Y），
**Z = 高度**（地面 z=0，门高 ~2.0 m）。主开合轴是 **竖直 (Z) revolute**；Dutch 有
两个不同高度的竖直 revolute，arched 有一个 + 一个水平 (door-local X) 的 ring-pull
revolute，center-pivot 有一个穿叶片中线的双向竖直 revolute。

默认成熟域：墙挂 / 立地的单扇住宅 / 谷仓 / 教堂式门，0.85–1.30 m 宽、~1.7–2.0 m 高。
**不该混入相邻类别见 §11。**

## 槽位 + 候选模块表

> **Slot A is the SHELL/spine selector.** Picking a Slot A module fixes the frame
> root (wood casing vs stone surround), the leaf-local coordinate origin (hinge
> edge vs centerline), the bearing interface (HINGE_LAP vs pintle vs pivot-socket),
> and which Slot B / Slot C modules are reachable (see compatibility matrix §9).

### Slot A：leaf split mechanism (PRIMARY axis — the Dutch identity)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `dutch_two_leaf_horizontal_split` (baseline / PRIMARY) | rec_door_dutch (parent) | frame root L245-L312; upper_leaf L317-L342; lower_leaf L345-L354; hinge loop L364-L381; **two revolutes** `frame_to_upper`/`frame_to_lower` L402-L420 | eligible if compatible | Wood-casing shell. Leaf split at a mid-rail (SPLIT_Z=1.06) into `upper_leaf` + `lower_leaf`, EACH on its own vertical Z revolute on the SAME hinge jamb at different heights; leaves open INDEPENDENTLY → **joint count j=2**. Bearing policy = HINGE_LAP jamb laps leaf edge (allow_overlap). |
| `single_solid_leaf` | rec_door_other_arched (parent) | stone root L361-L385; door part L386-L407; **leaf revolute** `frame_to_door` L424-L434; ring-pull revolute L442-L452 | eligible if compatible | Stone-surround shell. ONE continuous full-height `door` leaf on ONE vertical Z revolute at the jamb reveal (`X_HINGE`); door hangs on fixed `jamb_pintles` (captured strap-barrel/pintle bearing). Optional second horizontal (door-local X) revolute for the `ring_pull` → **joint count j=1 or 2** depending on Slot C hardware. |
| `center_pivot` | rec_door_other_var_centerpivot | `_arched_profile_centered` L99-L112; `build_pivot_spine_mesh` L165-L237; `build_pivot_socket_bottom_mesh` L351-L371; `build_pivot_socket_top_mesh` L374-L396; **center pivot revolute** `frame_to_door` L465-L477 | eligible if compatible | Stone-surround shell. Leaf authored CENTERED (x=0 at centerline); rotates about its OWN vertical centerline (X_PIVOT) on a single bidirectional revolute (lower=-90°, upper=+90°). Top + bottom iron pivot sockets on the stone head/threshold capture the `pivot_spine` pins → **joint count j=1 (+ optional ring-pull)**. Distinct bearing topology (socket cups, not jamb laps / pintles). |

### Slot B：head / top profile

> Slot B is largely one parametrized helper (`_arched_profile_face`). The flat
> head is the Dutch-shell baseline; the four curved/tympanum heads belong to the
> stone-surround shells.

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_square_head` (baseline) | rec_door_dutch (parent) | `head_jamb` + `casing_head` (Box) L261-L269, L307-L312 | eligible if compatible | Flat square top; rectangular wood casing head over the opening. No arch. (Dutch shell only.) |
| `full_semicircular_arch` | rec_door_other_arched (parent) | `_arched_profile_face(width, spring, top)` L86-L102 (radius=W/2 ⇒ true semicircle); `stone_arch` keystone L304-L308 | eligible if compatible | Tall church-style FULL semicircle springing at LEAF_SPRING=1.55, apex = spring + W/2 (= 2.00 m). Concentric stone opening + keystone. (Stone shell.) |
| `broad_barn_segmental_arch` | rec_door_other_var_roundtop | `_arched_profile_face(width, spring, rise)` L95-L111; dims LEAF_W=1.20 / ARCH_RISE=0.20 L45-L48 | eligible if compatible | **Broad shallow barn-door curved head** (rise 0.20 on a wide 1.20 m leaf). **NOTE: slug says "roundtop" but it is NOT a semicircle — classify by structural feature (segmental, low rise).** (Stone shell.) |
| `shallow_segmental_arch` | rec_door_other_var_segmental | `_arched_profile_face` L91-L108; LEAF_RISE=0.12 L42; concentric-arch rise calc L56-L59 | eligible if compatible | Gently cambered low-rise (0.12) segmental top; opening rise derived from a true concentric arc center so leaf/stone arcs stay parallel. (Stone shell.) |
| `flat_top_rect_in_arched_surround` | rec_door_other_var_porthole | flat-top leaf slab L125-L133; tympanum opening `OPEN_SPRING=LEAF_TOP+GAP` L60-L64; semicircular stone arch above L350-L365 | eligible if compatible | RECTANGULAR flat-top leaf (LEAF_TOP=2.00, no leaf arch) inside a STONE tympanum arch; the arch lives ONLY in the stone surround above the flat door. (Stone shell.) |

### Slot C：leaf infill / latch hardware

> Slot C varies the leaf face + latch hardware. The first two are Dutch-only
> (need two leaves); the last three are stone-shell.

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `glazed_lite_over_raised_panel + knob` (baseline) | rec_door_dutch (parent) | `_window_frame_leaf_cq` (2×2 muntin grid) L138-L200; `_raised_panel_leaf_cq` L93-L135; window_glass L337-L342; knob `door_knob` L386-L395 + FIXED `lower_to_knob` L426-L432 | eligible if compatible | Frosted 2×2 lite (hollow opening + thin glass pane behind hand-written v_bar/h_bar muntins) on the UPPER leaf, moulded raised panel on the LOWER leaf, brushed-steel latch knob (FIXED). **Dutch-only (two leaves).** |
| `solid_raised_panel_both_leaves + lever` | rec_door_other_var_levered_panel | `_raised_panel_leaf_cq` L92-L134 (used for BOTH leaves L307-L329); `_lever_handle_mesh` L164-L224; FIXED `lower_to_handle` L400-L406 | eligible if compatible | Both leaves are solid raised-panel wood (no glazing); horizontal lever handle on a rectangular backplate (FIXED), room side. **Dutch-only (two leaves).** |
| `louvered_slat_vent + knob` | rec_door_other_var_louvered | `_louver_frame_leaf_cq` (bare opening) L140-L169; slat loop `slat_{i}` L306-L316 (N_SLATS=13 L80); raised-panel lower L319-L328; knob L360-L369 | eligible if compatible | UPPER leaf is a tilted-slat louver vent (loop-emitted `slat_{i}`, FIXED into leaf), LOWER raised panel, latch knob. **Dutch-only (two leaves).** |
| `vertical_plank_strap + ring_pull` | rec_door_other_arched (parent) | `build_door_leaf_mesh` plank groove loop L105-L155; `build_strap_hinge_mesh` L158-L211; `build_iron_hardware_mesh` (studs+boss) L214-L258; `build_ring_pull_mesh` L261-L274; **ring revolute** `door_to_ring_pull` L442-L452 | eligible if compatible | Board-and-batten vertical planks, forged iron strap hinges + dome studs (fused leaf visuals), hanging iron `ring_pull` on its own horizontal revolute. **Stone-shell.** Loop-emitted individual `plank_{i}` source = rec_door_other_var_plankcount L402-L407. |
| `porthole_glazed_round_light + ring_pull` | rec_door_other_var_porthole | circular cut leaf L140-L146; `build_porthole_glass_mesh` L183-L191; `build_muntin_ring_mesh` (continuous annular through-ring) L194-L212; ring revolute L512-L522 | eligible if compatible | Circular through-cut porthole light with a continuous iron muntin ring + transparent glass pane cut into the plank leaf; hanging ring-pull. **Stone-shell** (paired with `flat_top_rect_in_arched_surround` head). |

> Every slot has ≥3 candidates (A=3, B=5, C=5). No degraded single-candidate slot.

## 槽位图（slot graph）

pattern: `mixed` — split-mechanism revolute spine selects shell/leaf-topology;
head_profile + infill are parallel children of the chosen leaf; multiplicity
replicates planks / lites / slats rigidly into a leaf.

```
                         [Slot A: split mechanism = shell/spine selector]
                                          |
        +---------------------------------+----------------------------------+
        |                                 |                                  |
  dutch_two_leaf                   single_solid_leaf                    center_pivot
  (wood casing root)               (stone surround root)               (stone surround root)
        |                                 |                                  |
   door_frame ──[Z revolute @hinge_jamb, q∈[0,1.7]]──> upper_leaf            |
   (HINGE_LAP)──[Z revolute @hinge_jamb, q∈[0,1.7]]──> lower_leaf            |
                                          |                                  |
                          stone_frame ──[Z revolute @X_HINGE,                |
                          (jamb_pintles  q∈[0,110°]]──> door (one leaf)      |
                          captured pin)              |                       |
                                          door ──[X revolute @boss]──> ring_pull (optional, Slot C)
                                                                              |
                          stone_frame ──[Z revolute @X_PIVOT (centerline),
                          (pivot_sockets q∈[-90°,+90°]]──> door (centered leaf)
                          top+bottom cups)            |
                                                door ──[X revolute @boss]──> ring_pull (optional)

  [Slot B head profile]  applied to the leaf top edge + frame opening (parallel child of leaf):
        flat_square (Dutch) | full_semicircle | broad_barn_segmental | shallow_segmental | flat_top_rect_in_arched_surround
  [Slot C infill]        applied to the leaf face + latch hardware (parallel child of leaf):
        glazed_lite+knob | solid_panel+lever | louvered+knob   ← Dutch-shell only (two leaves)
        plank_strap+ring | porthole+ring                       ← stone-shell only
  [Multiplicity]         plank_count → plank_{i}/seam_{i} (rigid into leaf, no joint)
                         lite_count  → pane_{i}/muntin_{i} (rigid, FIXED glazing)
                         slat_count  → slat_{i}            (rigid, FIXED into leaf)
```

Interface points / joint policy:

- **dutch_two_leaf**: two parallel vertical-Z revolutes, parent=`door_frame`,
  children=`upper_leaf`/`lower_leaf`; origins at the hinge edge lifted to
  UPPER_BOTTOM / LOWER_BOTTOM; range [0, 1.7 rad]. Closed-pose interface: each leaf
  hinge edge LAPS the `hinge_jamb` (intended overlap, allow_overlap) and the two
  leaves meet at the split with only SPLIT_GAP (`leaves_meet_at_split`).
- **single_solid_leaf**: one vertical-Z revolute parent=`stone_frame`,
  child=`door`, origin at `X_HINGE`, axis -Z, range [0, 110°]. Support interface:
  rolled strap barrels (on door) captured on fixed `jamb_pintles` pins (on frame) —
  metal-on-metal capture overlap (allow_overlap + expect_contact).
- **center_pivot**: one vertical-Z revolute parent=`stone_frame`, child=`door`,
  origin at `X_PIVOT` (opening center), axis +Z, range [-90°, +90°] (bidirectional).
  Support interface: `pivot_spine` pins seat in top/bottom `pivot_sockets` cups
  (allow_overlap + expect_contact); leaf-in-cut-opening tessellation overlap also
  allow_overlapped with containment proof.
- **ring_pull (Slot C optional child)**: horizontal door-local-X revolute,
  parent=`door`, child=`ring_pull`, origin at the mounting boss
  (`RING_CX, RING_PIVOT_Y, RING_PIVOT_Z`), range [0, 90°]; ring threads through the
  boss (allow_overlap + expect_contact).
- **latch hardware (knob / lever)**: FIXED joint, parent=lower leaf (Dutch) /
  door (single), seated flush on the +Y face (allow_overlap).

Mutually exclusive / optional / gated:

- Slot A modules are mutually exclusive (one shell per build) and gate Slots B & C.
- Slot B picks are one-at-a-time per build.
- Slot C picks are one-at-a-time per build.
- `ring_pull` is an OPTIONAL moving child present only with stone-shell Slot C
  (plank_strap / porthole); absent with Dutch Slot C → joint count varies.

## 每槽位 Module Emits / Interfaces

### Slot A / module `dutch_two_leaf_horizontal_split`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_frame` (root: hinge_jamb/latch_jamb/head_jamb/threshold/casing_leg_hinge/casing_leg_latch/casing_head), `upper_leaf`, `lower_leaf` | rec_door_dutch L245-L312, L317, L345 |
| internal joints | `frame_to_upper` (REVOLUTE, axis +Z, range [0,1.7]); `frame_to_lower` (REVOLUTE, axis +Z, range [0,1.7]); visible barrel hinges are fused visuals (not jointed) | rec_door_dutch L402-L420; hinge loop L364-L381 |
| upstream interface | root part stands on ground (z=0); HINGE_LAP jamb laps each leaf hinge edge | rec_door_dutch L247, L453 |
| downstream interface | each leaf +Y face hosts Slot C infill + FIXED latch; leaf top edge hosts Slot B (flat only) | rec_door_dutch L317-L354 |

### Slot A / module `single_solid_leaf`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stone_frame` (root: `stone_arch` + fixed `jamb_pintles`), `door` (one leaf), optional `ring_pull` | rec_door_other_arched L371-L415 |
| internal joints | `frame_to_door` (REVOLUTE, axis -Z, range [0,110°]); optional `door_to_ring_pull` (REVOLUTE, axis +X, range [0,90°]) | rec_door_other_arched L424-L452 |
| upstream interface | stone block on ground; strap barrels captured on `jamb_pintles` pins (bearing) | rec_door_other_arched L322-L353, L513-L519 |
| downstream interface | leaf face hosts Slot C plank/porthole; leaf top edge + stone opening host Slot B arch profile | rec_door_other_arched L386-L407 |

### Slot A / module `center_pivot`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stone_frame` (root: `stone_arch` + `pivot_sockets` top/bottom cups), `door` (centered leaf with fused `pivot_spine`), optional `ring_pull` | rec_door_other_var_centerpivot L413-L457 |
| internal joints | `frame_to_door` (REVOLUTE, axis +Z, range [-90°,+90°] bidirectional); optional `door_to_ring_pull` (REVOLUTE, axis +X) | rec_door_other_var_centerpivot L465-L492 |
| upstream interface | threshold extends below z=0 to host the bottom socket; pivot_spine pins seat in top/bottom socket cups | rec_door_other_var_centerpivot L351-L396, L578-L584 |
| downstream interface | centered leaf face (x=0 at centerline) hosts Slot C plank; leaf top edge + opening host Slot B arch | rec_door_other_var_centerpivot L115-L162 |

### Slot B / modules (head profiles)
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf top-edge profile + frame opening profile (modifies leaf mesh + stone/casing head; no new part) | rec_door_other_arched `_arched_profile_face` L86-L102 |
| internal joints | none (static profile) | — |
| upstream interface | consumes leaf width + spring height from Slot A; for tympanum, springs the stone arch ABOVE the flat leaf top | rec_door_other_var_porthole L60-L64 |
| downstream interface | the curved/flat top edge that Slot C plank/lite tops follow (`_arch_height` per-plank top) | rec_door_other_var_plankcount L110-L144 |

### Slot C / module `glazed_lite_over_raised_panel + knob`
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper leaf = window frame (stiles/rails + 2×2 muntins) + `window_glass` pane; lower leaf = raised panel; `door_knob` part | rec_door_dutch L138-L200, L337-L342, L386-L395 |
| internal joints | `lower_to_knob` (FIXED) | rec_door_dutch L426-L432 |
| upstream interface | mounts onto both Dutch leaves; transparent glass material (alpha<0.6) | rec_door_dutch L240, L499-L509 |
| downstream interface | latch knob protrudes +Y near latch edge | rec_door_dutch L423-L425 |

### Slot C / module `solid_raised_panel_both_leaves + lever`
| emits | 描述 | 来源 |
|---|---|---|
| parts | both leaves = `_raised_panel_leaf_cq`; `lever_handle` part (backplate + lever shaft + tip) | rec_door_other_var_levered_panel L307-L329, L164-L224 |
| internal joints | `lower_to_handle` (FIXED) | rec_door_other_var_levered_panel L400-L406 |
| upstream interface | no glass material; both leaves solid | rec_door_other_var_levered_panel L474-L489 |
| downstream interface | horizontal lever (dy > 1.5·dx) protruding +Y near latch edge | rec_door_other_var_levered_panel L491-L517 |

### Slot C / module `louvered_slat_vent + knob`
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper leaf = `_louver_frame_leaf_cq` bare opening + N `slat_{i}` (loop); lower = raised panel; `door_knob` | rec_door_other_var_louvered L140-L169, L306-L316, L319-L328 |
| internal joints | `lower_to_knob` (FIXED); slats are FIXED into the leaf (no per-slat joint) | rec_door_other_var_louvered L400-L406, L306-L316 |
| upstream interface | mounts on Dutch upper leaf opening | rec_door_other_var_louvered L283-L292 |
| downstream interface | tilted slats span the opening at even vertical pitch (i+0.5)/N | rec_door_other_var_louvered L306-L316 |

### Slot C / module `vertical_plank_strap + ring_pull`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_planks` (or `plank_{i}` loop) + battens + `strap_hinges` + `iron_studs` (fused leaf visuals); `ring_pull` part | rec_door_other_arched L386-L407; rec_door_other_var_plankcount L402-L413 |
| internal joints | `door_to_ring_pull` (REVOLUTE, axis +X, range [0,90°]) | rec_door_other_arched L442-L452 |
| upstream interface | strap barrels captured on jamb pintles (Slot A bearing) | rec_door_other_arched L394-L401, L513-L519 |
| downstream interface | hanging ring lifts +Y; mounting boss on iron_studs | rec_door_other_arched L549-L557 |

### Slot C / module `porthole_glazed_round_light + ring_pull`
| emits | 描述 | 来源 |
|---|---|---|
| parts | plank leaf with circular through-cut + `porthole_glass` + continuous `muntin_rings`; `iron_studs`; `ring_pull` part | rec_door_other_var_porthole L140-L146, L183-L212, L466-L477 |
| internal joints | `door_to_ring_pull` (REVOLUTE, axis +X) | rec_door_other_var_porthole L512-L522 |
| upstream interface | porthole cut + seated muntin ring (allow_overlap seating into door_planks) | rec_door_other_var_porthole L571-L581 |
| downstream interface | round glazed light in the upper leaf; transparent glass alpha 0.35 | rec_door_other_var_porthole L467, L620-L625 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `split_mechanism` (Slot A) | enum | dutch_two_leaf / single_solid_leaf / center_pivot | — | choice | deterministic procedural sampler; selects shell + gates Slot B/C | Slot A table |
| `head_profile` (Slot B) | enum | flat_square / full_semicircle / broad_barn_segmental / shallow_segmental / flat_top_rect | — | conditional | legal set depends on `split_mechanism` (flat ⇔ Dutch; arches ⇔ stone shell) — see §9 | Slot B table |
| `leaf_infill` (Slot C) | enum | glazed_lite / solid_panel / louvered / plank_strap / porthole | — | conditional | legal set depends on `split_mechanism` (lite/panel/louver ⇔ Dutch two-leaf; plank/porthole ⇔ single/pivot) — see §9 | Slot C table |
| `palette_style` | enum | stone_oak_plank / painted_pine_panel / glazed_white_lite / charcoal_iron_barn / weathered_grey_plank / honey_oak_porthole | stone_oak_plank | palette | palette only，**不计入 slot_choice**；material RGBA 集合，按 shell 兼容（painted_pine/glazed_white = Dutch tones; stone_oak/charcoal/weathered/honey = stone-shell tones） | 各样本 materials（rec_door_dutch L235-L242；rec_door_other_arched L364-L368；rec_door_other_var_porthole L421-L425） |
| `plank_count` (Slot C plank/porthole) | int | [3, 12]，加权偏 4–8 | 6 | conditional | 仅 plank_strap/porthole 有效；pitch = LEAF_W/plank_count；rigid into leaf | rec_door_other_var_plankcount L105-L144 |
| `lite_count` (Slot C glazed) | int | [2, 9]（2×2..3×3 grid，加权 4） | 4 | conditional | 仅 glazed_lite 有效；row×col grid，FIXED glazing | rec_door_dutch L138-L200（hand-written → loop） |
| `louver_slat_count` (Slot C louvered) | int | [6, 18] | 13 | conditional | 仅 louvered 有效；even pitch (i+0.5)/N，FIXED into leaf | rec_door_other_var_louvered L306-L316 |
| `leaf_width_scale` | float | [0.90, 1.35] | 1.0 | independent | 缩放 LEAF_W；派生 opening / pitch / hinge-x；clamp | rec_door_other_var_roundtop LEAF_W=1.20 L45 |
| `leaf_height_scale` | float | [0.92, 1.10] | 1.0 | independent | 缩放 DOOR_H / LEAF_SPRING；派生 SPLIT_Z、apex；clamp | rec_door_dutch L42-L43；rec_door_other_arched L41-L42 |
| `arch_rise_scale` | float | derived | 1.0 | conditional | 仅 segmental heads (broad_barn/shallow)；rise ∈ [0.08, 0.28]·width-band，apex = spring + rise；半圆/flat 不用 | rec_door_other_var_roundtop ARCH_RISE=0.20 L47；rec_door_other_var_segmental LEAF_RISE=0.12 L42 |
| `leaf_thickness_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 LEAF_T / LEAF_THK；不破坏 hinge_y / barrel | rec_door_dutch L44；rec_door_other_arched L43 |
| (—) | constraint | — | — | inequality | opening profile ⊇ leaf profile + GAP everywhere（同心 arch：R_open = R_door + GAP）；违反则按比例回缩 spring/rise；保证 leaf 在洞口内、arc 不穿模 | rec_door_other_var_segmental L56-L59 |
| (—) | constraint | — | — | inequality | center_pivot：leaf half-width + swing 不得超出 X_PIVOT 两侧 reveal；threshold 下沉 ≥ socket depth；违反则回缩 LEAF_W | rec_door_other_var_centerpivot L66-L68, L315-L319 |
| (—) | constraint | — | — | inequality | Dutch：SPLIT_Z ∈ (LOWER_BOTTOM+0.3, DOOR_H-0.3)，两叶高均 > 0.3 m；违反则回缩 SPLIT_Z | rec_door_dutch L46-L57 |

连续尺寸采样契约：先采 independent（width/height/thickness scale）→ 派生 equation（apex、pitch、SPLIT_Z、opening 尺寸）→ 用 inequality 把 opening⊇leaf+GAP、pivot reveal、SPLIT_Z 投影回可行域，无法满足则拒绝重采 → conditional 范围（arch_rise / *_count）按所选 Slot A/B/C 解析。

## Multiplicity / Copy Logic

本类有 **3 根独立 multiplicity 轴**（按 Slot C 模块条件激活，互斥地各只在一种 infill 出现）：

### 轴 1：`plank_count`（PRIMARY，best-sampled）
- `count_param`: `plank_count`
- `N_range`: 产品域 [3, 12]；测试偏小（3–9 已有样本，sweep 上限设 12）
- sampling domain（权重档）: 4–8 高频（住宅 / 谷仓常见），3 与 9–12 稀有尾部
- copied object: 单块竖板 `plank_{i}`（loop-emitted，shared `_build_single_plank` + `_arch_height` 让每块板顶随 Slot B arch 轮廓走）；或 fused seam `seam_{i}`（`_plank_pitch` + `for i in range(seam_count)`）
- naming: `plank_{i}` (i=0..N-1) 或 `seam_{i}` (i=0..N-2)
- placement: uniform pitch = LEAF_W / plank_count，从 hinge 边（或 center_pivot 的 -LEAF_W/2）起
- joint policy: **rigid into leaf，无 per-plank joint**（随叶片 hinge 一起动）
- source/gating: rec_door_other_var_plankcount L105-L144, L402-L407（N=9 loop）; rec_door_other_var_plankcount_three L86-L88, L131-L145（N=3 seam）; 仅 `plank_strap` / `porthole` Slot C 激活
- 已覆盖 N: {3, 6, 8, 9} = **4 distinct N**

### 轴 2：`lite_count`（Dutch glazed leaf）
- `count_param`: `lite_count`（row×col grid，默认 2×2=4）
- `N_range`: [2, 9]（2×2..3×3），加权 4
- sampling domain: 4 高频，2 / 6 / 9 稀有
- copied object: `pane_{i}` glass + `muntin_{i}` bar（当前 hand-written 单 v_bar/h_bar，需转 `for-i-in-range` + shared helper）
- naming: `pane_{r}_{c}` / `muntin_v_{i}` / `muntin_h_{j}`
- placement: regular grid pitch over the window opening
- joint policy: uniform FIXED-into-leaf transparent glazing（随上叶 hinge 动）
- source/gating: rec_door_dutch L138-L200（单样本，hand-written → flag for loop 转换）; 仅 `glazed_lite` Slot C 激活
- 已覆盖 N: {4} — **单样本，标记需 loop 化**

### 轴 3：`louver_slat_count`（Dutch louvered leaf）
- `count_param`: `louver_slat_count`（默认 13）
- `N_range`: [6, 18]
- sampling domain: 10–14 高频，6 / 18 稀有
- copied object: `slat_{i}`（shared `Box` geometry，统一 tilt）
- naming: `slat_{i}` (i=0..N-1)
- placement: even vertical pitch `(i+0.5)/N` over the opening
- joint policy: uniform FIXED into the leaf（随上叶 hinge 动）
- source/gating: rec_door_other_var_louvered L306-L316（loop-emitted，clean copy logic）; 仅 `louvered` Slot C 激活
- 已覆盖 N: {13} — **单样本，但已是干净 loop**

下游模板：每根轴各做一次按小类加权采样、各自编进 `slot_choices`、各自 clamp、sweep
各自设上限（plank≤12、lite≤9、slat≤18）。三轴互斥激活（一个 build 只有一种 infill），
不会同时出现，因此不需要跨轴共享 helper（待第二个真·并发 multiplicity 出现再抽）。

## 拓扑多样性审计

总组合数（按兼容矩阵 §9 过滤后的合法 cell）：

- **Dutch shell**（split=dutch_two_leaf）：Slot B = {flat_square} ×
  Slot C = {glazed_lite, solid_panel, louvered} = 1 × 3 = **3 cells**
  （每个 cell 再乘 lite/slat N：glazed×lite(2..9 加权≈4 档) + louvered×slat(6..18 加权≈4 档) + solid_panel(无 N) → ~9 拓扑变体）
- **Stone single-leaf shell**（split=single_solid_leaf）：Slot B =
  {full_semicircle, broad_barn_segmental, shallow_segmental, flat_top_rect} ×
  Slot C = {plank_strap, porthole} 但 porthole ⇔ flat_top_rect 配对（见 §9），
  plank_strap ⇔ 任一 arch head → 3 (arch heads)×plank_strap + 1 (flat_top)×porthole
  = **4 cells** × plank N (4 distinct, 加权≈5 档) ≈ **~20 拓扑变体**
- **Center-pivot shell**（split=center_pivot）：Slot B =
  {full_semicircle, broad_barn_segmental, shallow_segmental} × Slot C = {plank_strap}
  = 3 × 1 = **3 cells** × plank N (4 distinct) ≈ **~12 拓扑变体**

合法 cell 合计 ≈ **10 cells**（3 + 4 + 3），叠加三条 multiplicity 轴后拓扑变体 **≈ 40+**。

理由：仅 split_mechanism(3) × 合法 head/infill ≈ 10 cells 即达 ≥10 distinct；joint
拓扑本身就横跨 j=2（Dutch 双叶）、j=1/2（单叶 ± ring-pull）、j=1/2（center-pivot ±
ring-pull）三种，加上 plank/lite/slat multiplicity 让 distinct 计数轻松破 10。即便最小
积（Dutch 3 cells + 单叶 4 cells + pivot 3 cells = 10）也刚好达标，加 N 后舒适越过。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：

1. 加权采 `split_mechanism`（dutch / single / pivot，三者均衡，single 略高因样本最多）。
2. 按 split 解析 Slot B 合法集（conditional）→ 加权采 head_profile。
3. 按 split 解析 Slot C 合法集（conditional）→ 加权采 leaf_infill；porthole 只在
   flat_top_rect head 下出现（配对 gate）。
4. 若 infill ∈ {plank/porthole/louvered/glazed} 则各自加权采对应 *_count（小 N 偏多）。
5. 采 independent 连续 scale（width/height/thickness）→ 派生 apex/pitch/SPLIT_Z/opening
   → inequality 投影（opening⊇leaf+GAP、pivot reveal、SPLIT_Z）→ 解析 conditional arch_rise。
6. 选 `palette_style`（按 shell 兼容子集）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。**本类受兼容约束 <300**：
合法 module cell 仅 ~10，distinct 拓扑（含 multiplicity N 分桶）目标 ~40–60，低于 300 的
原因是 catch-all 但两壳不可跨（Dutch×plank、single×glazed 等被设计性 block），且 head/
infill 强配对。这是类别 / 兼容约束导致的合理上限，已在兼容矩阵记录。

Controlled local parameterization：初版关键连续 scale = `leaf_width_scale`
[0.90,1.35]、`leaf_height_scale` [0.92,1.10]、`leaf_thickness_scale` [0.85,1.20]、
`arch_rise_scale`（conditional，segmental 专用，rise∈[0.08,0.28]）。全部在
`resolve_config` clamp / 派生；跨部件依赖（apex、opening、pitch、SPLIT_Z）按 §7 的
equation/inequality 显式声明并求解，不留到 builder 失败。这些 scale 只改安全比例 /
clearance，不改 InterfaceSpec（hinge 轴 / 位置）、MatingContract（pintle/socket 捕获、
HINGE_LAP）或 multiplicity 拓扑。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted: split → (gated) head → (gated) infill → *_count → scales → palette | slot_choices_for_seed matches build choices；non-gated combos never sampled |
| compatibility matrix | Dutch⇔{flat, glazed/panel/louver}; stone-single⇔{arch heads + plank, flat_top+porthole}; pivot⇔{arch heads + plank}; cross-shell cells BLOCKED | no floating leaf, no cross-shell infill, single-leaf never gets two-leaf glazed/louver, porthole only with flat_top head, ring-pull only on stone shells |
| controlled local variation | width/height/thickness/arch_rise scales clamped + derived | proportions vary; hinge axis/origin, pintle/socket capture, HINGE_LAP, opening⊇leaf+GAP, SPLIT_Z all preserved |
| regression overrides | none initially | only known-failed/reviewer cases later |
| random sweep | seeds 0-49 initial pass; 0-999 maturity audit |, contract failures, closed-pose seal, swing direction |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A split_mechanism | 3 | yes | yes | dutch_two_leaf / single_solid_leaf / center_pivot (all on-disk converged) |
| B head_profile | 5 | yes | yes | flat / full_semicircle / broad_barn_segmental / shallow_segmental / flat_top_rect |
| C leaf_infill | 5 | yes | yes | glazed_lite / solid_panel / louvered / plank_strap / porthole |

### 兼容矩阵（compatibility matrix — blocked cross-shell cells flagged）

> ✓ = legal & on-disk; (paired) = legal but head/infill强配对; ✗ = BLOCKED by design (gate, do not force).

| Slot A \ Slot C | glazed_lite | solid_panel | louvered | plank_strap | porthole |
|---|---|---|---|---|---|
| dutch_two_leaf | ✓ (parent) | ✓ (levered) | ✓ (louvered) | ✗ (no Dutch plank shell) | ✗ (no Dutch porthole shell) |
| single_solid_leaf | ✗ (needs 2 leaves) | ✗ (needs 2 leaves) | ✗ (needs 2 leaves) | ✓ (parent) | ✓ (porthole, paired w/ flat_top head) |
| center_pivot | ✗ (needs 2 leaves) | ✗ (needs 2 leaves) | ✗ (needs 2 leaves) | ✓ (pivot var) | ✗ (no on-disk pivot porthole; not sampled v1) |

| Slot A \ Slot B | flat_square | full_semicircle | broad_barn_segmental | shallow_segmental | flat_top_rect |
|---|---|---|---|---|---|
| dutch_two_leaf | ✓ (parent) | ✗ (Dutch shell flat-headed) | ✗ | ✗ | ✗ |
| single_solid_leaf | ✗ (stone shell arched) | ✓ (parent/plankcount) | ✓ (roundtop) | ✓ (segmental) | ✓ (porthole, paired w/ porthole infill) |
| center_pivot | ✗ | ✓ | ✓ | ✓ | ✗ (no on-disk pivot tympanum; not sampled v1) |

**Blocked-cell rationale for the template author:** the `✗` cells are NOT failed
forks — they require shell unification that this batch did NOT bank. Gate them out
in `resolve_config`; do not attempt to build a single-leaf-in-Dutch-casing or a
Dutch-with-planks. `flat_top_rect` head and `porthole` infill are a STRONG pair
(both only on rec_door_other_var_porthole) — sample them together.

## Validator

- `slot_choices_for_seed` returns implemented module names (split / head / infill + active *_count)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility matrix / gating prevents illegal cross-shell combos (no Dutch×plank, no single×two-leaf-infill, porthole only with flat_top head, ring-pull only on stone shells)
- optional regression overrides are sparse and justified (none in v1)
- final template does not endlessly cycle a small curated table as the main seed domain
- controlled local scales (width/height/thickness/arch_rise) clamped + derived in `resolve_config`; cannot break hinge axis/origin, pintle/socket capture, HINGE_LAP, opening⊇leaf+GAP, SPLIT_Z, or multiplicity
- cross-part scale dependencies (apex/pitch/SPLIT_Z/opening = equation/inequality) resolved in `resolve_config`, not in the builder
- critical InterfaceSpec / MatingContract points exist: HINGE_LAP (Dutch), strap-barrel↔pintle capture (single), pivot-spine↔socket capture (pivot), ring-pull-through-boss, FIXED knob/lever seating
- key joints have expected type/axis/range: Dutch two vertical-Z revolutes [0,1.7]; single one vertical-Z revolute [0,110°]; pivot one vertical-Z revolute [-90°,+90°]; ring-pull horizontal-X revolute [0,90°]
- copied objects follow naming/placement: `plank_{i}` uniform pitch, `slat_{i}` even pitch FIXED, `pane_{i}`/`muntin_{i}` grid FIXED
- closed pose: leaves seat against jamb / stay within opening; Dutch leaves meet at split with only SPLIT_GAP; no infill seals behind the leaf

## Reject cases

- Single-leaf or center-pivot shell built with a two-leaf-only infill (glazed_lite / solid_panel_both / louvered) — needs two leaves; must be gated.
- Dutch shell built with plank_strap or porthole infill, or with any arch head — cross-shell, not banked; must be gated.
- `porthole` infill sampled with a curved leaf head instead of `flat_top_rect` (porthole leaf is flat; arch is only in the stone tympanum).
- ring_pull present on a Dutch shell, or absent on a plank/porthole stone shell — joint count must follow shell.
- Opening profile not ⊇ leaf profile + GAP (leaf pokes through stone / casing, or arch arcs intersect) — inequality not resolved.
- center_pivot leaf half-width + swing exceeds the reveal, or threshold not sunk to host the bottom socket — leaf collides / pivot floats.
- Dutch SPLIT_Z pushed so a leaf height < ~0.3 m, or leaves overlap / gap at the split beyond SPLIT_GAP.
- Plank/lite/slat count copied without uniform pitch, or planks not following the Slot B arch top edge (flat-top planks under a semicircle head).
- Treating leaf width/height/color/material/decoration-density as a new slot or candidate (e.g. roundtop's 1.20 m width) instead of a continuous scale / palette.
- "Floating" leaf: hinge/pintle/socket capture overlap removed so the leaf has no real bearing support.

## 与相邻类别的边界

- 不该混入：**Door / Double or Sliding doors**（双扇对开、推拉、折叠、车库卷门）——本类是
  "单扇 / 单扇水平对开" 的杂项门；多扇并排对开 / 水平滑轨 / 折叠链属另类（不同 spine：
  滑轨 prismatic、折叠多铰链）。Dutch 的"两叶"是 **竖直水平分割** 的同一道门，不是并排双扇。
- 不该混入：**Cabinet / Furniture door**（柜门、橱门、家具上的小门）——本类是建筑级
  立地 / 墙挂整门（~2 m 高、有门套 / 石拱洞口、立在地面），不是挂在家具箱体上的小门板。
- 不该混入：**Window / Shutter**（窗、百叶窗扇）——louvered 候选是门叶上的通风格栅段，
  不是独立窗扇；整体仍是一道门。
- 不该混入：**Gate / Fence**（栅栏门、围墙大门）——本类是带 frame/洞口的住宅 / 教堂 /
  谷仓门，不是无实体洞口的栅栏 / 铁艺大门。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- **两壳几乎无共享代码**：Dutch 壳是 Box-based 木门套（HINGE_LAP），stone 壳是
  CadQuery `_arched_profile_face` + pintle/socket。实现时建议两个 shell builder
  (`_build_dutch_shell` / `_build_stone_shell`)，Slot A 选其一；不要强行统一。
- 共享 helper：`_arched_profile_face(width, spring, top|rise)`（Slot B 全部曲头，
  注意 segmental 用 rise、semicircle 用 top=spring+W/2）；`_plank_pitch` + `_build_single_plank`
  + `_arch_height`（plank multiplicity，板顶随 arch 走）；`_raised_panel_leaf_cq`
  （Dutch panel）；`_hinge_barrel_mesh`（Dutch 可见铰链）。
- **关键 allow_overlap（element-scoped，复制进合成测试）**：
  Dutch HINGE_LAP（upper/lower body ↔ hinge_jamb + 每个 barrel hinge ↔ hinge_jamb）；
  single 壳 strap_hinges↔jamb_pintles（captured pin）+ ring_pull↔iron_studs；
  pivot 壳 pivot_spine↔pivot_sockets + door_planks↔stone_arch（tessellation，带 containment 证明）+ pivot_spine↔stone_arch；
  porthole muntin_rings↔door_planks（seating）；knob/lever↔leaf（seating）。
- **flag for loop conversion**：Dutch lite 当前是 hand-written 单 v_bar/h_bar
  (rec_door_dutch L174-L184)；模板需转 row×col `for-i-in-range` + shared pane/muntin helper。
- **不进入 v1 seed domain**：center_pivot×porthole、center_pivot×flat_top tympanum、
  任何 cross-shell `✗` cell（见兼容矩阵）；如未来统一两壳可再开。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | dutch_two_leaf_horizontal_split | rec_door_dutch | L245-L420 | wood-casing shell root + two-leaf double revolute + HINGE_LAP |
| S2 | A | single_solid_leaf | rec_door_other_arched | L361-L452 | stone-surround shell root + one leaf revolute + pintle capture |
| S3 | A | center_pivot | rec_door_other_var_centerpivot | L99-L112, L165-L237, L351-L396, L465-L477 | centered leaf + pivot spine + top/bottom sockets + bidirectional revolute |
| S4 | B | full_semicircular_arch | rec_door_other_arched | L86-L102 | `_arched_profile_face` (radius=W/2) + keystone |
| S5 | B | broad_barn_segmental_arch | rec_door_other_var_roundtop | L45-L48, L95-L111 | segmental rise-param arch on wide leaf |
| S6 | B | shallow_segmental_arch | rec_door_other_var_segmental | L42, L56-L59, L91-L108 | shallow concentric segmental arc |
| S7 | B | flat_top_rect_in_arched_surround | rec_door_other_var_porthole | L60-L64, L125-L133, L350-L365 | flat leaf + stone tympanum arch above |
| S8 | C | glazed_lite_over_raised_panel + knob | rec_door_dutch | L138-L200, L93-L135, L337-L342, L386-L395, L426-L432 | window frame + 2×2 muntins + glass + knob |
| S9 | C | solid_raised_panel_both_leaves + lever | rec_door_other_var_levered_panel | L92-L134, L164-L224, L307-L329, L400-L406 | both-leaf raised panel + lever handle |
| S10 | C | louvered_slat_vent + knob | rec_door_other_var_louvered | L140-L169, L306-L316, L319-L328, L360-L369 | louver frame + slat loop + knob |
| S11 | C | vertical_plank_strap + ring_pull | rec_door_other_arched | L105-L155, L158-L258, L261-L274, L442-L452 | plank leaf + strap hinges + studs + ring-pull revolute |
| S12 | C / mult | vertical_plank loop-emitted | rec_door_other_var_plankcount | L105-L144, L402-L407 | `plank_{i}` loop + `_build_single_plank` + `_arch_height` |
| S13 | C / mult | plank seam loop | rec_door_other_var_plankcount_three | L86-L88, L131-L145 | fused `seam_{i}` via `_plank_pitch` (N=3 wide boards) |
| S14 | C | porthole_glazed_round_light + ring_pull | rec_door_other_var_porthole | L140-L146, L183-L212, L466-L477, L512-L522 | porthole cut + glass + continuous muntin ring + ring-pull |
