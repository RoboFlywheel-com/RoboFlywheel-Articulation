# caster_trolley — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `caster_trolley` |
| template path | `agent/templates/Urban_Environment_Caster_Trolley.py` |
| test path (optional) | `tests/agent/test_caster_trolley_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children load_surface + handle on a wheeled chassis, plus multiplicity over casters and shelf tiers) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 4 (4 original 5★ parents; supermarket wire-basket seed moved OUT to `Caster Trolley2`) + 9 converged forked variants in id list |
| read_count | 13 model.py read in full or scanned for part/joint topology (4 parents read in full; 9 vars scanned for structure axis) |
| read_scope | all in-scope 5-star samples in this category (excl. the moved-out supermarket seed) + all converged forked variants on the source map |
| source_index_policy | only adopted module sources are indexed below |

Reading summary: every member is a horizontal load surface on a wheeled chassis riding on **N casters in the standard 2-fixed / 2-swivel layout** (2 swivel casters at one end steer, the rest rigid track straight), pushed by a tubular handle. The **defining, repeated motion** is the swivel-end pair's kingpin swivel (CONTINUOUS-Z) plus a CONTINUOUS wheel roll about a transverse Y axle on **every** caster (rigid casters roll but do not swivel). The two flat-platform parents (001/002) emit the swivel as REVOLUTE-Z (001) or CONTINUOUS-Z (002); the cage/tray parents (003/004) use CONTINUOUS-Z swivel + CONTINUOUS-Y roll. **The roll joint is always CONTINUOUS-Y and is the load-bearing identity motion.** The load surface differs structurally: single deck slab (001/002), stacked shallow trays on corner legs (004), multi-tier wire-mesh shelf stack on a tall tube frame (003), plus a warehouse **straight-walled rectangular wire bin** on a tubular chassis (converged variant deck_to_basket). The handle/upright differs structurally: tall inverted-U at one end + cross rails (001/002), continuous end-frame tube that bows over into a handle at BOTH ends (004), full-height wire-mesh cage uprights (003). Forked variants confirm the swap paths are clean: caster count is `len(positions)`-driven (six/three vars), shelf tiers are `len(SHELF_HEIGHTS)`-driven (shelves_three), a folding handle adds a REVOLUTE-Y hinge at the deck top (fixed_to_folding_handle), and a double handle / open-post / deck↔tray↔bin conversions reuse shared helpers. No left/right hand-written dual disease; all isomorphic children are loop-emitted. (The tapered supermarket shopping-basket seed 005 is now out of scope — see boundary section.)

## 核心身份

**Caster trolley** = a wheeled warehouse / service / utility cart: a horizontal load surface (flat deck OR stacked trays OR wire-mesh shelf stack OR straight-walled utility wire bin) carried on a wheeled chassis that rides on **N casters in the standard 2-fixed / 2-swivel layout**, and pushed via a tubular handle / upright. The **defining articulation** is **2 swivel casters (CONTINUOUS-Z kingpin + CONTINUOUS-Y roll) at one end + the rest rigid (FIXED mount, CONTINUOUS-Y roll only)** — the standard 2-fixed/2-swivel cart config: the swivel pair (at the max-x end) steers, the rigid pair tracks straight, and **for N>4 only the end pair swivels** (middle + far-end casters rigid). **Every** caster **rolls CONTINUOUSLY about a transverse axle** — this roll is the category-identity motion and must be present on every caster of every seed. Optional secondary articulation: a folding/hinged push handle (REVOLUTE-Y). Mature domain: warehouse stock carts, platform trucks, roll cages, two-tier service/bus carts, warehouse wire-bin/basket trolleys. Default proportions ~0.8–0.95 m long, 0.45–0.62 m wide, casters at the four corners with deck riding ~0.15–0.18 m above the floor.

**Neighbor boundary — supermarket shopping trolley excluded (nearest neighbor):** the chrome **tapered wire-basket supermarket shopping trolley** (fold-down child seat, low chrome push-bar, nesting splayed underframe) has been split into its own 小类 `Caster Trolley2` and is **OUT of scope here**. Its supermarket-only features (tapered nesting basket, child-seat flap, low basket push-bar, chrome colorway) are the nearest neighbor to exclude; a straight-walled warehouse wire bin is in scope, the tapered nesting supermarket basket is not.

Not in identity: a non-wheeled stand/shelf, a single drawn wagon body, a tipping/dumping bucket, a hand-truck with only 2 fixed wheels, a powered/AGV vehicle, a **tapered supermarket shopping basket / child-seat cart** (→ `Caster Trolley2`).

## 槽位 + 候选模块表

### Slot A：load_surface（主机构槽 — 承载面拓扑，root part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_platform_deck` | rec_flat-platform-utility-cart-with-a-tall-tubular-p_…0233d588 | L137-L155 | eligible if compatible | 单 root `deck`：sheet/wood slab + rolled-edge lip(s)；no internal joints；casters + handle attach directly. (Wood-plank variant: stock-cart parent …974df157 L80-L116.) |
| `stacked_open_trays` | rec_two-tier-galvanized-steel-service-cart-with-rais_…7e448273 | L83-L134 | eligible if compatible | `lower_tray` root + `upper_tray` (FIXED `lower_to_upper`)；shared `_tray_visuals` pan-floor+4-lip helper；corner legs span gap. Fork echo: deck→two_tray (rec_caster_trolley_var_deck_to_two_tray L150-L255). |
| `wire_mesh_shelf_stack` | rec_tall-wire-mesh-shelf-roll-cage-trolley-with-a-bl_…ef2c8c79 | L98-L172, L221-L250 | eligible if compatible | tall tube `frame` root (corner posts + top/bottom loops + base plate) + `for si,h in enumerate(SHELF_HEIGHTS)` shelf pans (FIXED `frame_to_shelf_{si}`). Drives the tier-count multiplicity axis. |
| `utility_wire_bin` | rec_caster_trolley_var_deck_to_basket | L74-L93, L126-L210, L255-L347 | eligible if compatible | **straight-walled RECTANGULAR** wire-mesh warehouse load bin/cage on a tubular `chassis` root: rectangular tube frame rails (L255-L297) + inline wire-mesh floor + 4 straight vertical walls + top rim rail (L299-L347), lattice built by grid for-loops (`_build_floor_mesh`/`_build_wall_mesh`/`_build_rim_mesh` L126-L210, dims L74-L93). **NOT a tapered supermarket basket** — walls are vertical, footprint constant with Z. No splayed underframe, no nesting taper. |

### Slot B：handle_upright（推手 / 立柱机构槽，attaches to load_surface root）

**3 base candidates**, each carrying variant sub-axes (single↔double handle; fixed↔folding hinge REVOLUTE-Y; cage↔open_post). NO low_basket_handle (that low chrome push-bar came only from the moved-out supermarket seed).

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `tall_inverted_U_one_end` | rec_flat-platform-utility-cart-with-a-tall-tubular-p_…0233d588 | L158-L200 | eligible if compatible | one tall inverted-U `push_handle` (loop + 2 ladder cross rails) at +X end via FIXED `deck_to_push_handle`; optional short `end_guard` at −X end. Mesh-backstop echo: stock-cart parent …974df157 L122-L169. Sub-axes: **single↔double** (rec_..._single_to_double_handle L125-L210 adds a 2nd tall handle via `_add_push_handle`); **fixed↔folding** (rec_..._fixed_to_folding_handle L204-L262 puts the +X handle on a REVOLUTE-Y hinge, axis≈(0,−1,0), origin at deck-top surface, lower=0 upper=1.50, hinge brackets/tabs/barrels/pin captured). |
| `handle_both_ends` | rec_two-tier-galvanized-steel-service-cart-with-rais_…7e448273 | L136-L166 | eligible if compatible | per end (`for sx in (1,-1)`) a single continuous tube run `end_frame_{tag}` that rises from corner legs and bows over into a handle, FIXED `lower_to_end_frame_{tag}`. Two-tall-handle echo on a deck: rec_caster_trolley_var_single_to_double_handle L125-L210 (`_add_push_handle` helper, `handle_{idx}`). |
| `full_cage_uprights` | rec_tall-wire-mesh-shelf-roll-cage-trolley-with-a-bl_…ef2c8c79 | L99-L130, L174-L219 | eligible if compatible | the shelf `frame` posts ARE the upright; full-height wire-mesh side/back panels (FIXED `frame_to_{name}`) close the cage, front open. Sub-axis **cage↔open_post** degrade: rec_caster_trolley_var_cage_to_open_post_handle L101-L149 (4 posts + single rear inverted-U handle, no mesh). |

### Slot C：caster_count / tier_count（MULTIPLICITY 槽，两根独立轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | N / copy logic |
|---|---|---|---|---|
| `casters_four` (baseline) | all 5 parents | …0233d588 L208-L321 (`add_caster` + 4 corner calls) | eligible | 4 corner casters; each `deck_to_caster_yoke_{i}` swivel-Z + `caster_spin_{i}` CONTINUOUS-Y roll. |
| `casters_N=len(positions)` | rec_caster_trolley_var_casters_six | L65-L80 (CASTER_POSITIONS), L222-L329 (`add_caster`), L332 (`for i,(cx,cy) in enumerate(CASTER_POSITIONS)`) | eligible | 6 casters (front/mid/rear pairs); count = `len(CASTER_POSITIONS)`. |
| `casters_N=3 tricycle` | rec_caster_trolley_var_casters_three | L65-L80 (CASTER_MOUNT_POSITIONS), L215-L329, L331 loop | eligible | 3 casters (pair at handle end + 1 central rear); count = `len(positions)`. |
| `tiers_N=len(SHELF_HEIGHTS)` | rec_caster_trolley_var_shelves_three (vs parent 003 4-tier) | parent …ef2c8c79 L72,L229-L250; var L72 (3-tuple), L254 | eligible (only with `wire_mesh_shelf_stack` / open-post) | shelf tiers = `len(SHELF_HEIGHTS)`; each `frame_to_shelf_{si}` FIXED. |

## 槽位图（slot graph）

pattern: mixed (parallel_children on a wheeled root + 2 multiplicity axes)

```
load_surface (Slot A, ROOT part)
   │
   ├──[FIXED, on root top/back face]────────────► handle_upright (Slot B)
   │        (folding_handle: REVOLUTE-Y hinge at root top surface, axis≈(0,-1,0), lower=0,upper=1.5)
   │
   ├──[FIXED, internal: lower_to_upper / frame_to_shelf_{si}]──► (load_surface internal tiers; utility_wire_bin = inline mesh, no internal joint)
   │
   └──[per caster i = 0..N-1, mount at corner/position list, on root underside]
            caster_yoke_i ──[max-x end pair: swivel-Z CONTINUOUS axis (0,0,1); all others: FIXED mount]──► (from root)
               └── caster_wheel_i ──[caster_spin_i CONTINUOUS, axis (0,1,0)]──► roll  ★ DEFINING MOTION (every caster)
```

接口点位 / policy:

- **Slot A → Slot B**: handle/upright mounts to the load_surface root. For deck/tray/bin: FIXED on the root top or +X back edge (`deck_to_push_handle` …0233d588 L176-L178; `lower_to_end_frame_{tag}` …7e448273 L164-L165; `chassis_to_push_handle` deck_to_basket L372-L374 for the wire bin). For the **fixed↔folding sub-axis** of `tall_inverted_U_one_end`: REVOLUTE-Y hinge, **origin on the root top surface at the +X end**, axis ≈ (0,−1,0), range [0.0, 1.50] (var fixed_to_folding_handle L254-L262). `full_cage_uprights` is not a separate child — the frame posts ARE the root, so Slot B folds into Slot A (see compatibility matrix).
- **Slot A internal tiers**: `stacked_open_trays` FIXED `lower_to_upper`; `wire_mesh_shelf_stack` FIXED `frame_to_shelf_{si}`; `utility_wire_bin` has **no internal joint** — its wire-mesh floor/walls/rim are inline visuals on the tubular chassis root (deck_to_basket L299-L347). `flat_platform_deck` has no internal joint.
- **Slot A → casters**: each caster mounts on the root underside at a position-list entry. The (up to) 2 casters at the **max-x end** have a swivel yoke mount `<root>_to_caster_yoke_{i}` = CONTINUOUS about Z (kingpin); **every other caster's** `<root>_to_caster_yoke_{i}` is **FIXED** (rigid, tracks straight). Roll joint `caster_spin_{i}` (axis Y) is CONTINUOUS on **every** caster. Wheel bottom touches z≈0; root rides ~0.15–0.18 m above the floor.
- Mutually exclusive / derived: `wire_mesh_shelf_stack` and the open-post degrade of `full_cage_uprights` are the only Slot-A modules that expose the **tier_count** axis; deck/tray/bin force tier_count = 0/fixed. `full_cage_uprights` requires Slot A = `wire_mesh_shelf_stack` (or open-post shelf frame).

## 每槽位 Module Emits / Interfaces

### Slot A / module flat_platform_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `deck` (root): slab + rolled-edge lip(s) (or 6 wood planks + steel chassis) | S2 / L137-L155 ; S1 / L80-L116 |
| internal joints | none | — |
| upstream interface | root part; no parent | S2 / L137 |
| downstream interface | top face (handle FIXED), back +X edge, underside corners (caster mounts at CASTER_X/Y) | S2 / L62-L65, L318-L321 |

### Slot A / module stacked_open_trays
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_tray` (root) + `upper_tray`; shared `_tray_visuals` (pan_floor + 4 lips) | S4 / L83-L134 |
| internal joints | `lower_to_upper` FIXED | S4 / L134 |
| upstream interface | `lower_tray` root | S4 / L120-L121 |
| downstream interface | corner-leg posts at POST_X/Y (handle rises from legs); caster mounts under lower pan (`caster_top_z`=leg_base_z) | S4 / L63-L66, L169 |

### Slot A / module wire_mesh_shelf_stack
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root: 4 posts + top/bottom loops + base plate + pads + mid rails) + `shelf_{si}` ×N + optional `box_{bi}` cargo | S3 / L99-L172, L229-L272 |
| internal joints | `frame_to_shelf_{si}` FIXED ×N (tier multiplicity); `shelf_{si}_to_box_{bi}` FIXED cargo | S3 / L247-L250, L268-L272 |
| upstream interface | `frame` root | S3 / L99 |
| downstream interface | post tops (cage panels / open-post handle); caster mounts at CASTER_X/Y on base (CASTER_TOP_Z) | S3 / L66-L68, L274 |

### Slot A / module utility_wire_bin
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (root: rectangular tubular frame rails + cross members, L255-L297) with inline wire-mesh **straight-walled rectangular bin** — floor + 4 vertical walls + top rim rail (L299-L347); dims L74-L93 | Sbin / L74-L93, L255-L347 |
| internal joints | none (bin walls/floor/rim are inline visuals on the chassis root) | — |
| upstream interface | `chassis` root | Sbin / L255-L256 |
| downstream interface | top rim / +X end (handle FIXED `chassis_to_push_handle` L372-L374); chassis underside corners carry casters at CASTER_X/Y (L403-L408) | Sbin / L57-L60, L372-L374, L403-L408 |

### Slot B / module tall_inverted_U_one_end
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_handle` (inverted-U loop + 2 ladder cross rails); optional `end_guard` (shorter U + 1 rail) | S2 / L158-L200 |
| internal joints | none (visual-only loop) | — |
| upstream interface | FIXED `deck_to_push_handle` at root top +X end; `deck_to_end_guard` at −X end | S2 / L176-L178, L198-L200 |
| downstream interface | tall grip ~0.93 m above deck top | S2 / L70 |

### Slot B / module handle_both_ends
| emits | 描述 | 来源 |
|---|---|---|
| parts | `end_frame_{tag}` ×2 (one continuous tube run/end: up legs → bow over → down) | S4 / L141-L166 |
| internal joints | none | — |
| upstream interface | FIXED `lower_to_end_frame_{tag}` ×2 (loop over `sx in (1,-1)`) | S4 / L164-L165 |
| downstream interface | handle grips above top tray at BOTH short ends | S4 / L68 |

### Slot B / module full_cage_uprights
| emits | 描述 | 来源 |
|---|---|---|
| parts | back + 2 side `*_mesh` PerforatedPanelGeometry panels (front open); posts belong to Slot-A frame | S3 / L174-L219 |
| internal joints | `frame_to_{name}` FIXED ×3 panels | S3 / L197-L200 |
| upstream interface | FIXED to frame posts; **requires Slot A = wire_mesh_shelf_stack** | S3 / L178-L201 |
| downstream interface | open front loading face; top push frame loop | S3 / L112-L120 |

### Slot B sub-axis / fixed↔folding hinge (SECONDARY articulation on tall_inverted_U_one_end)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_handle` (U-loop in local frame, origin at hinge) + hinge brackets/tabs/barrels/pin captured visuals on deck | S6 / L204-L250 |
| internal joints | **`deck_to_push_handle` REVOLUTE**, axis≈(0,−1,0), origin at deck top +X end, lower=0.0 upper=1.50 | S6 / L254-L262 |
| upstream interface | hinge pivot on root top surface at +X end (deck/tray/bin only — needs a flat top to hinge) | S6 / L254-L262 |
| downstream interface | folds from upright (q=0) toward flat (q≈π/2) | S6 / L251-L262 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `load_surface_choice` | enum | flat_platform_deck / stacked_open_trays / wire_mesh_shelf_stack / utility_wire_bin | — | choice | deterministic procedural sampler | Slot A table |
| `handle_choice` | enum | tall_inverted_U_one_end / handle_both_ends / full_cage_uprights | — | choice | gated by `load_surface_choice` (see compat matrix) | Slot B table |
| `handle_double` | bool | single / double | single | sub-axis | only on tall_inverted_U_one_end (deck/tray/bin) | var single_to_double_handle L125-L210 |
| `handle_folding` | bool | fixed / folding (REVOLUTE-Y) | fixed | sub-axis | only on tall_inverted_U_one_end, deck/tray/bin flat top | var fixed_to_folding_handle L204-L262 |
| `cage_style` | enum | cage / open_post | cage | sub-axis | only on full_cage_uprights (shelf frame) | var cage_to_open_post_handle L101-L149 |
| `caster_count` | int | [3, 8] | 4 | independent | weighted draw (small-N偏多); count = `len(positions)` | S-six L65-L80 / S-three L65-L80 |
| `tier_count` | int | [2, 6] | 4 | conditional | active only if load_surface ∈ {wire_mesh_shelf_stack, open-post}; else fixed by module | S3 L72 / S-shelves L72 |
| `palette_style` | enum | warehouse_steel / galvanized / black_rollcage / industrial_blue_wood | warehouse_steel | choice | 4 realistic colorways (≥3; see palette block) | 4 in-scope parents + bin var materials |
| `deck_len_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp; scales root长 (X) | S2 L48 |
| `deck_wid_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp; scales root宽 (Y) | S2 L49 |
| `handle_height_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp; tall handle grip height | S2 L70 |
| `wheel_radius_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp; caster wheel radius | S2 L53 |
| `deck_bottom_z` | float | derived | — | equation | `= 2·wheel_radius + clearance`；root rides above wheels | S2 L57 |
| `caster_inset` | float | derived | — | equation | `= f(deck_len,deck_wid)`；casters inset from edges, kept inside footprint | S2 L62-L65 |
| (—) | constraint | — | — | inequality | caster positions ⊂ root footprint (each within ±deck_len/2, ±deck_wid/2 minus inset); violated → retract inset | 接口 / footprint |
| (—) | constraint | — | — | inequality | shelf clear height between tiers ≥ box_min；tier spacing = (TOP_Z−BASE_Z)/(tier_count) ≥ min_gap, else reduce tier_count | S3 L72 / clearance |
| (—) | constraint | — | — | inequality | folding_handle swept arc clears deck top + cargo (lower=0,upper≤1.50) | S6 L261 |

**palette_style 候选 (4 realistic colorways from in-scope sources; ≥3 satisfied)**:
- `warehouse_steel`: deck_gray (0.62,0.63,0.65) + frame_gray (0.70,0.71,0.73) + steel/rim_silver + dark rubber — from S2 (also the wire-bin var: frame_gray/wire_zinc/rim_silver).
- `galvanized`: galv (0.66,0.67,0.69) + galv_leg (0.60,0.61,0.63) + rim_silver (0.78) — from S4.
- `black_rollcage`: frame_black (0.13,0.13,0.15) + wire_mesh (0.30,0.31,0.33) + shelf_steel (0.45) + dark rubber — from S3.
- `industrial_blue_wood`: deck_wood (0.55,0.45,0.32) + chassis_steel (0.30,0.32,0.36) + handle_steel blue (0.28,0.36,0.52) + caster_red hub (0.62,0.14,0.13) — from S1.

## Multiplicity / Copy Logic

本 spec 有 **2 根独立 multiplicity 轴**（不互相穷举；下游各做一次加权采样）。

### 轴 1：caster ring（primary）
- `count_param`: `caster_count`
- `N_range`: [3, 8]（产品全程；测试样本覆盖 {3,4,6}）
- sampling domain: 加权 — 4 最高频（标准 4-corner），3/6 中频，5/7/8 稀有尾部。
- copied object: 每个 caster = `caster_yoke_{i}` (swivel plate + kingpin + offset bracket + fork legs/crown + axle) + `caster_wheel_{i}` (WheelGeometry rim + TireGeometry tire)。
- naming: `caster_yoke_{i}` / `caster_wheel_{i}`, joints `<root>_to_caster_yoke_{i}` + `caster_spin_{i}`, i=0..N-1。
- placement: positions = corner/列表 driven by `len(positions)`. N=4→4 corners; N=6→front/mid/rear pairs (mid at x≈0); N=3→pair at handle end + 1 central rear. Positions ⊂ footprint.
- joint policy: **standard 2-fixed / 2-swivel** — the (up to) 2 casters at the max-x end swivel: `<root>_to_caster_yoke_{i}` axis (0,0,1) CONTINUOUS (kingpin). Every other caster's `<root>_to_caster_yoke_{i}` is **FIXED** (rigid, no kingpin). For N>4 only the single max-x end pair swivels. Roll `caster_spin_{i}` axis (0,1,0) CONTINUOUS on **every** caster. **每个 caster 必须有 roll joint；只有 max-x 端的 2 个 caster 才 swivel，其余 rigid。**
- source/gating: S-six L65-L80,L332; S-three L65-L80,L331。

### 轴 2：shelf tier ring（secondary, conditional）
- `count_param`: `tier_count`
- `N_range`: [2, 6]（样本覆盖 {3,4}）
- sampling domain: 加权 — 3/4 高频，2/5/6 稀有。
- copied object: `shelf_{si}` (pan + rear lip); optional `box_{bi}` cargo.
- naming: `shelf_{si}`, joint `frame_to_shelf_{si}` FIXED, si=0..tier-1; heights = `SHELF_HEIGHTS` list driven by `len`。
- placement: stacked at increasing Z between BASE_Z and TOP_Z, even-ish spacing; each seats on mid rails.
- joint policy: all FIXED `frame_to_shelf_{si}`.
- source/gating: **仅当 `load_surface_choice` ∈ {wire_mesh_shelf_stack, open-post degrade}**；deck/tray/bin 时 tier_count 由 module 内部固定 (deck=0 internal tiers, tray=2 fixed, utility_wire_bin=1 single bin)。S3 L229-L250; S-shelves L72,L254。

## §8.5 视觉多样性 6 轴考察
| axis | present? | spec decision |
|---|---|---|
| ① Part-tree / skeleton | yes | Slot A/B choices change the load_surface + handle part tree (deck slab vs tray stack vs shelf frame vs chassis+bin; one-end U vs both-ends vs full cage), all within caster-trolley identity; caster/tier N复制 |
| ② Joint topology | yes | every seed = N× (swivel-Z + roll-Y CONTINUOUS) caster pairs; internal FIXED tiers (lower_to_upper / frame_to_shelf_{si}); optional REVOLUTE-Y folding-handle hinge sub-axis |
| ③ Primary Form Family | yes | **4 load_surface 形态原型**：flat_platform_deck（平板 slab）/ stacked_open_trays（浅盘叠层）/ wire_mesh_shelf_stack（高网架多层）/ utility_wire_bin（直壁矩形网笼料箱）。**排除**：锥形嵌套超市购物篮（→ Caster Trolley2） |
| ④ Surface detail | yes | rolled-edge lips, ladder cross-rails, wire-mesh panels, straight-wall lattice, rim rails, end guards, caster yokes/forks |
| ⑤ Multiplicity | yes | caster count N∈[3,8]（样本 {3,4,6}）; shelf tier count N∈[2,6]（样本 {3,4}）; wire-lattice grid density |
| ⑥ Material / palette | yes | warehouse_steel / galvanized / black_rollcage / industrial_blue_wood（4 realistic colorways；chrome_supermarket 随 005 移出） |

## 拓扑多样性审计

标称组合数（HARD GATE）：Slot A(4) × Slot B(3) × Slot C distinct-N(3) = **36 ≥ 10** ✓。
- Slot A(4)：flat_platform_deck / stacked_open_trays / wire_mesh_shelf_stack / utility_wire_bin。
- Slot B(3 base)：tall_inverted_U_one_end / handle_both_ends / full_cage_uprights（+ 子轴 single↔double、fixed↔folding、cage↔open_post）。
- Slot C distinct-N(3)：casters N∈{4,6,3}；tiers N∈{4,3}（复用同一 multiplicity 轴）。
- per-A 合法收窄：deck → {one_end, both_ends}；tray → {one_end, both_ends}；utility_wire_bin → {one_end, both_ends}；shelf → {full_cage (cage↔open_post)}。Σ A×B base legal = 2+2+2+1 = 7；再乘 caster distinct-N(3)=21、叠加 fixed↔folding / single↔double 子轴与 palette → distinct topology ≫ 10。

理由：即便单 Slot A(4) × Slot B(3) = 12 ≥10 独立通过；Slot A(4) × distinct caster-N(3) = 12 ≥10 亦独立通过；标称 4×3×3 = 36。所有候选均由现存 4 母资产 + 9 变体（无 supermarket seed）真源支撑。

seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic RNG(seed) → (1) 抽 `load_surface_choice`；(2) 按 compat matrix 抽 `handle_choice`；(3) caster_count 加权抽 + 解析 position list；(4) 若 shelf 系，tier_count 加权抽并生成 SHELF_HEIGHTS，否则 tier 由 module 固定；(5) 抽 palette_style；(6) 抽 independent scales (deck_len/wid, handle_height, wheel_radius) → 派生 deck_bottom_z / caster_inset → inequality 投影 (footprint, tier clearance, fold arc)。`slot_choices_for_seed` 返回与 build 一致的 module 名 + N。无主体 modulo 表。
Topology target：1000-seed distinct 富类别建议 ≥300（report-only）；本类别凭 A×B base legal(7) × caster-N(3) × tier-N(2, partial) × 子轴(double/folding/open_post) × palette(4) 自然 按 ≥300 report-only 口径观察。
regression overrides：none（首版）；若发现 folding+tray 折臂穿模等坏组合，仅按 seed 记录降级，不作主 domain。
Controlled local parameterization：deck_len_scale, deck_wid_scale, handle_height_scale, wheel_radius_scale (all independent, clamped [0.85,1.2])；deck_bottom_z 与 caster_inset 为 equation 派生；footprint / tier-clearance / fold-arc 为 inequality。这些 scale 不改 slot/joint 拓扑，不破坏 InterfaceSpec / 多重性。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→caster_N→tier_N→palette→scales; weighted; gates per matrix | slot_choices_for_seed matches build choices |
| compatibility matrix | full_cage_uprights ⇒ A=wire_mesh_shelf_stack; tier_count active only for shelf系; utility_wire_bin compatible with one_end/both_ends (+folding sub-axis), NOT full_cage; folding sub-axis only on deck/tray/bin (flat top) | no floating caster, no front-panel-on-non-cage, no orphan shelf joint, fold-arc clearance |
| controlled local variation | 4 independent scales clamped [0.85,1.2]; deck_bottom_z & caster_inset derived | proportions vary; casters stay in footprint & on floor; handle reachable |
| regression overrides | none | — |
| random sweep | seeds 0-49 initial; 0-999 maturity | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A load_surface | 4 | yes | yes | deck/trays/shelf_stack/utility_wire_bin |
| B handle_upright | 3 | yes | yes | base 3 (+ sub-axes double/folding/open_post); per-A legal subset ≥1 |
| C caster multiplicity | N∈[3,8] | yes | yes | distinct-N axis |
| C tier multiplicity | N∈[2,6] (conditional) | yes | yes | shelf系 only |

## Validator

- slot_choices_for_seed returns implemented module names + (caster_count, tier_count)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix prevents illegal combos (full_cage without shelf frame; tier_count on non-shelf; full_cage on utility_wire_bin; folding sub-axis on shelf/cage)
- controlled local scales clamped; deck_bottom_z / caster_inset / footprint / tier-clearance / fold-arc resolved in resolve_config, not builder
- critical interfaces exist: each caster mount on root underside within footprint; handle FIXED/REVOLUTE on root top
- key joints: every caster has swivel axis (0,0,1) + roll `caster_spin_{i}` CONTINUOUS axis (0,1,0); folding_handle REVOLUTE axis≈(0,−1,0) origin at root top, lower=0 upper≤1.5
- copied objects follow naming/placement: `caster_yoke_{i}`/`caster_wheel_{i}` i=0..N-1; `shelf_{si}` si=0..tier-1; all N wheels touch z≈0
- captured-pin overlaps element-scoped: axle↔rim per caster; shelf pan↔frame rails; kingpin↔mount pad; folding hinge brackets↔tube
- final template does not cycle a curated table as main seed domain

## Reject cases

- 任一 caster 缺 roll (`caster_spin_{i}`) 或 roll 轴非 (0,1,0) → 失去类别 identity motion。
- caster 数硬编码为 4（未用 `len(positions)`），caster_count 轴失效。
- 某 caster wheel 不触地 (z 偏离 0 > 0.012) 或位置落在 footprint 外（悬空/穿模）。
- `full_cage_uprights` 与非 shelf-frame load_surface 组合（front 面板挂在 deck/tray/bin 上 → 漂浮）。
- tier_count 暴露在 deck/tray/bin（孤立 `frame_to_shelf` joint，无 frame post）。
- folding hinge (fixed↔folding 子轴) origin 不在 root 顶面、或轴非横向 Y、或 upper>1.5 折臂穿过 deck/cargo。
- **tapered supermarket shopping basket / fold-down child-seat flap / low chrome push-bar / nesting splayed underframe / chrome_supermarket palette → 属 `Caster Trolley2`，本模板 reject**（straight-walled 仓储 wire bin OK，锥形嵌套超市篮 NOT）。
- handle 与 load surface 不接触（push_handle 漂浮在 root 之上无 mating face）。
- root 直接坐地（deck_bottom_z 未 ≈ 2·wheel_radius + clearance）。

## 与相邻类别的边界

- **最近邻，必须排除 — `Caster Trolley2`（超市购物手推车）**：chrome tapered wire-basket **supermarket shopping trolley**（锥形嵌套购物篮 + 折叠童座 flap + 篮口低 chrome push-bar + splayed 嵌套 underframe + chrome colorway）已于 2026-07-02 拆分为独立 小类 `Caster Trolley2`，不再属本模板。本类只收 **仓储 / 服务 / 备料 utility cart**：straight-walled 矩形 wire bin OK，锥形嵌套超市篮 / 童座 / 低 chrome 横杆 NOT。出现这些超市专有特征 → 判 `Caster Trolley2`。
- 不该混入 **Draft_Wagon（役用拖车 / 大车）**：wagon 是被牵引的单体车厢（牵引杆 + 固定/转向前轴的大轮），不是被人推、靠 4+ 颗 swivel caster 行进的服务车；caster_trolley 的 identity motion 是 per-caster swivel+roll，wagon 是整车牵引转向。若出现牵引杆/辕、车厢式深斗或 2 大固定轮，应判 wagon。
- 不该混入 **Tipping_Barrow（翻斗 / 手推独轮/翻倒车）**：barrow 的 identity 是 **可翻倒/倾卸的斗体**（REVOLUTE 倾翻 bin）+ 1-2 轮 + 双握把支腿，载面是封闭可倾斗而非平台/货架/篮；caster_trolley 载面不可倾倒、且必须 ≥3 swivel casters。若出现倾翻铰接的斗体或独轮+支脚静止支撑，应判 barrow。

## 模板实现备注（可选）

- 共享 helper: `add_caster(idx,cx,cy)` (yoke+wheel, 复用于全部 Slot A); `_tray_visuals` (tray pan+lips); `_tube`/`_u_frame_mesh`/`_cross_rail_mesh` (handle); `_add_push_handle` (双 handle); `_shelf_geometry` (shelf pan+lip).
- caster swivel 类型：统一采用 **CONTINUOUS-Z**（004/003/005 风格）作模板默认，避免 001 的 REVOLUTE-Z/CONTINUOUS-Z 不一致；validator 接受任一但 build 统一。
- element-scoped allow_overlap 清单：axle↔rim（每 caster）、shelf_pan↔frame rails、swivel_plate/kingpin↔mount pad/base_plate、folding hinge bracket/tab/barrel↔handle tube base、end_frame run↔tray pan_floor。
- 暂不进入 seed domain 的组合：utility_wire_bin + full_cage（bin 非 shelf frame，无 frame post）、deck + full_cage、tray + full_cage（无 frame post）。utility_wire_bin 有平面 rim/顶，folding 子轴 OK。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | flat_platform_deck (wood) / mesh backstop | rec_industrial-platform-stock-cart-…974df157 | L80-L116, L122-L169, L177-L283 | 木甲板 deck + mesh handle + caster 双关节范式 |
| S2 | A/B/C | flat_platform_deck / tall_inverted_U_one_end / casters_four | rec_flat-platform-utility-cart-…0233d588 | L137-L200, L208-L321 | deck slab+lip, one-end handle+guard, add_caster 4-corner |
| S3 | A/B/C | wire_mesh_shelf_stack / full_cage_uprights / tiers | rec_tall-wire-mesh-shelf-roll-cage-…ef2c8c79 | L98-L272, L274-L376 | frame+shelves(tier 轴)+mesh panels+casters |
| S4 | A/B | stacked_open_trays / handle_both_ends | rec_two-tier-galvanized-…7e448273 | L83-L166, L168-L271 | 双 tray+corner-leg handle 两端 |
| Sbin | A | utility_wire_bin | rec_caster_trolley_var_deck_to_basket | L74-L93, L126-L210, L255-L347 | 直壁矩形 wire-mesh 仓储料箱（tubular chassis + inline floor/walls/rim lattice for-loop）——非超市锥形篮 |
| S6 | B(sub) | fixed↔folding hinge | rec_caster_trolley_var_fixed_to_folding_handle | L204-L262 | REVOLUTE-Y 折叠 handle hinge（tall_inverted_U 子轴） |

（已删：S5 = rec_chrome-wire-basket-…58ed850d 锥形超市 basket / seat flap / low bar — 随 005 移出至 `Caster Trolley2`。）
