# pictureX/0611/Cabinet_with_doors_and_drawers — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Cabinet_with_doors_and_drawers` |
| template path | `agent/templates/pictureX_0611_Cabinet_with_doors_and_drawers.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Cabinet_with_doors_and_drawers_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children door+drawer on one carcass root + drawer multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in this category (4 origins + 8 variant forks) |
| source_index_policy | only adopted module sources are indexed below |

Sources (paths under `data/records/<id>/revisions/rev_000001/model.py`):
- S1 = `rec_picturex_...__004__...` (gray-oak sideboard; side-by-side door|drawers; block legs; 3-drawer loop). pure Box.
- S2 = `rec_picturex_...__003__...` (slate cabinet; 2 doors over 1 drawer; apron+feet plinth). cadquery mesh.
- S3 = `rec_picturex_...__001__...` (walnut secretary; 2 doors over 4 drawers; tapered legs). Box + cadquery legs.
- S4 = `rec_picturex_...__002__...` (jeweler cabinet; 3 glazed doors over 20 drawers; marble plinth). pure Box.
- S5 = `rec_cabinet_..._var_body_bowfront` (bow/curved front fork ← S1). cadquery arc extrudes.
- S6 = `rec_cabinet_..._var_body_tapered` (tapered/canted body fork ← S2). cadquery trapezoid extrudes.
- S7 = `rec_cabinet_..._var_door_sliding` (sliding prismatic door fork ← S1). pure Box + track rails.
- S8 = `rec_cabinet_..._var_support_metal_legs` (splayed metal legs fork ← S1). Box + Cylinder legs.
- S9 = `rec_cabinet_..._var_drawers_n2` (N=2 drawer fork ← S1).
- S10 = `rec_cabinet_..._var_layout_drawers_over_door` (vertical flip fork ← S2).
- S11 = `rec_cabinet_..._var_layout_flanking_doors` (door|central-bank|door fork ← S1).
- S12 = `rec_cabinet_..._var_probe_curved_double_door` (bow front + double door compatibility probe).

## 核心身份

A freestanding cabinet / sideboard whose **defining trait is the CO-EXISTENCE of at least one
openable door AND at least one pull-out drawer on a single connected load-bearing carcass** with a
grounded base. Doors swing (REVOLUTE) or slide (PRISMATIC); drawers always slide out on the front
axis (PRISMATIC). Every seed keeps both mechanisms.

Must NOT drift into:
- a doors-only wardrobe / display cabinet (no drawers), or
- a drawers-only chest of drawers / dresser (no door).

Both are adjacent 0611 subcategories; either would erase the co-existence identity.

## 槽位 + 候选模块表

### Slot A：body_form（③ Primary Form Family — the required form slot）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `rectilinear` | origin_anchor | S1/S2/S3/S4 all straight prisms | S1:L227-L356; S3:L94-L163 | Planar Boundary Form | eligible | axis-aligned Box carcass shell (2 sides + top + bottom + back), flat fronts |
| `bowfront` | forked_anchor | S5 curved carcass + fronts | S5:L65-L135 (bow helpers), L330-L345 (bowed sides), L206-L214 (bowed front) | Macro Surface Construction | eligible | front panels + top/bottom caps become real `threePointArc` extruded curved **meshes** (bow bulge ~25mm); backs stay flat |
| `tapered` | forked_anchor | S6 canted side walls | S6:L59-L79 (`_trapezoid_xz`), L82-L122 (tapered sides/back) | Volumetric Envelope Form | eligible | side walls are real trapezoidal extruded **meshes** (wider base, TAPER_PER_SIDE≈20mm); fronts rectangular within tapered opening |

### Slot B：door_module（② door leaf construction）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `slab` | origin_anchor | S1 `door` slab; S3 recessed slab | S1:L358-L422; S2:L73-L94 | eligible | flush slab door_panel + integrated edge pull; hardware folded into door part |
| `paneled` | origin_anchor | S3 two recessed panels; S3 pulls | S2:L73-L110, L176-L205 | eligible | slab + applied perimeter trim rails + recessed inner-panel look + drop pull |
| `glazed` | origin_anchor | S4 `_add_glazed_door` | S4:L135-L226 | eligible if door_leaf_count≥1 | frame stiles/rails + translucent `glass` pane + crossed lattice bars + brass pull |

### Slot C：door_mechanism（② joint type on the door leaf）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged` | origin_anchor | all origins; REVOLUTE | S1:L424-L440; S3:L253-L272; S4:L216-L225 | eligible | REVOLUTE about vertical z at outer leaf edge; axis (0,0,-1) left / (0,0,1) right; upper ∈ [1.4,1.92] |
| `sliding` | forked_anchor | S7 door on PRISMATIC track | S7:L323-L344 (tracks), L431-L447 (PRISMATIC axis (1,0,0)) | eligible if door_leaf_count==1 and door_zone wide | single leaf covers ~0.6 of opening, slides +x on top/bottom track rails; travel ≈0.4·zone_width |

### Slot D：door↔drawer layout（① skeleton / zone partition）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `door_over_drawers` | origin_anchor | S2/S3/S4 doors above drawer bank | S2:L253-L282; S4:L301-L410 | eligible | z-split: upper band = full-width door zone, lower band = full-width drawer stack |
| `drawers_over_door` | forked_anchor | S10 vertical flip | S10:L258-L287 (drawer joint z=0.840 top, doors lower) | eligible | z-split flipped: drawers on top, doors below |
| `side_by_side` | origin_anchor | S1 door beside drawer column | S1:L44-L56 (x zones), L271-L281 (center_divider) | eligible | x-split at a vertical `center_divider`: left zone = single door (full height), right zone = drawer column |
| `flanking_doors` | forked_anchor | S11 door\|bank\|door | S11:L365-L387 (two dividers), L489-L573 (outer-hinged doors + central bank) | eligible if door_mechanism==hinged | two symmetric x-splits: outer-hinged door on each flank, central drawer bank between |

### Slot E：drawer_count N（multiplicity — see §8）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `1..6 drawers` | origin_anchor | S2 N=1; S9 N=2; S1 N=3; S3 N=4; S4 large bank | S1:L442-L465; S9:L49,L444-L467; S3:L255-L323 | eligible | loop-emits `drawer_i` + one PRISMATIC `drawer_slide_i` each; stable indexed names |

### Slot F：support_base（① base substructure — emitted as carcass visuals, not FIXED parts）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `block_legs` | origin_anchor | S1 four square legs | S1:L346-L356 | eligible | 4 square-section Box legs at corners |
| `tapered_legs` | origin_anchor | S3 turned tapered legs | S3:L26-L35 (`_tapered_leg` loft), L325-L347 | eligible | 4 cadquery-loft tapered round legs (single mesh reused) |
| `plinth` | origin_anchor | S4 marble plinth | S4:L263-L282 | eligible | solid stepped box plinth under carcass |
| `apron_feet` | origin_anchor | S2 apron + rear feet | S2:L48-L62 | eligible | front apron rail + 4 corner feet boxes |
| `metal_legs` | forked_anchor | S8 splayed steel legs | S8:L346-L378 (splay 0.21rad Cylinders) | eligible | 4 splayed steel Cylinder legs (rpy-tilted) |

### Slot G：palette_style（⑥ material / finish — sampled per seed）

| module_name | source_type | evidence | 结构特征 |
|---|---|---|---|
| `oak` | record_only | S1 limed/gray oak | wood/metal palette |
| `walnut` | record_only | S3/S4 walnut veneers | dark wood + brass |
| `painted` | record_only | S2 slate paint | opaque painted + brass |
| `industrial` | record_only | common palette | grey metal + accent |
| `slate` | record_only(+world_knowledge_extrapolation) | S2 slate blue-gray | painted blue-gray + aged brass |
| `jeweler` | record_only(+world_knowledge_extrapolation) | S4 green glass + marble | dark walnut + green glass + stone |

### handle / surface decoration（④ record_only — NOT a slot）
Integrated edge pull (S1:L165-L171), long wood pull (S3:L228-L234), brass drop pull / knob
(S2:L89-L94, S2:L228-L251), veneer grain streaks (S1:L73-L113, S3:L219-L226). All host-conformal
visuals folded into the owning door/drawer part; never a separate part or joint.

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
                     body (root: shell panels + support_base visuals + front frame)
                        |  (all doors + drawers are PARALLEL CHILDREN of body)
   +--------------------+-----------------------------+
   |                    |                             |
 door_i             drawer_i (× N)               (support_base = body visuals only)
 REVOLUTE z-axis     PRISMATIC (0,-1,0)
 or PRISMATIC x      travel ≤ box_depth
 (hinged/sliding)
```

Interfaces / connection points:
- **body ↔ door_i**: hinge/slide origin on the front plane `y=-D/2` at the leaf's outer edge (hinged)
  or track origin (sliding). MatingContract pins the door_panel back face (positive_y) to a body
  `front_frame_*` stile front face (negative_y), contact along −y.
- **body ↔ drawer_i**: prismatic origin at `(drawer_center_x, -D/2, drawer_center_z)`, axis (0,-1,0).
  MatingContract pins drawer `front` back face (positive_y) to a body front rail (negative_y).
- **support_base**: pure carcass visuals contacting/embedding the carcass bottom panel (no joint).
- **layout** decides the x/z zones (which region is doors vs drawers) and the divider visuals.

Cross-slot joint policy: doors REVOLUTE about vertical z (stay in their z-band, never sweep into a
drawer z-band) or PRISMATIC +x (sliding). Drawers PRISMATIC −y. No FIXED joints anywhere (base is
folded into the body per AUTHORING Rule 1).

## 每槽位 Module Emits / Interfaces

### Slot A / body_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | none of its own — writes visuals into root `body` | S1:L227-L356 |
| internal joints | none | — |
| downstream interface | front plane `y=-D/2`, opening zones (from layout), front frame stiles/rails | S1:L319-L344 |

### Slot B/C / door_module × door_mechanism (per leaf)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_i` (slab/paneled/glazed visuals + folded pull + hinge/guide hardware) | S1:L358-L422; S4:L135-L226 |
| internal joints | one REVOLUTE `door_hinge_i` (hinged) or PRISMATIC `door_slide_i` (sliding) | S1:L424-L440; S7:L431-L447 |
| upstream interface | door_panel back face positive_y at `y=-D/2` (MatingContract to body front frame) | S1:L365-L371 |

### Slot E / drawer_module (per drawer, loop-emitted)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_i` (front + open-top box side/bottom/back + folded pull + inner slide) | S1:L116-L197 |
| internal joints | one PRISMATIC `drawer_slide_i`, axis (0,-1,0), lower=0 upper=travel | S1:L442-L465 |
| upstream interface | drawer `front` back face positive_y at `y=-D/2` (MatingContract to body front rail) | S1:L118-L124 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | rectilinear / bowfront / tapered | rectilinear | choice | procedural sampler | Slot A |
| door_module | enum | slab / paneled / glazed | slab | choice | procedural sampler | Slot B |
| door_mechanism | enum | hinged / sliding | hinged | conditional | sliding only if door_leaf_count==1 & zone wide | Slot C |
| layout | enum | door_over_drawers / drawers_over_door / side_by_side / flanking_doors | door_over_drawers | choice | procedural sampler | Slot D |
| drawer_count | int | 1..6 (weighted small; corner→8) | 3 | independent | clamp[1,8] | Slot E / §8 |
| support_base | enum | block_legs / tapered_legs / plinth / apron_feet / metal_legs | block_legs | choice | procedural sampler | Slot F |
| palette_style | enum | oak/walnut/painted/industrial/slate/jeweler | oak | choice | procedural sampler | Slot G |
| width | float | [0.55, 1.15] | 1.04 | independent | clamp | S1:L21; S3:L78 |
| depth | float | [0.34, 0.50] | 0.46 | independent | clamp | S1:L22 |
| carcass_height | float | [0.55, 1.60] | 0.72 | independent | clamp | S1/S3/S4 scale range |
| base_height | float | [0.04, 0.16] | 0.07 | independent | clamp | S1:L23 |
| door_swing | float | [1.4, 1.92] | 1.75 | independent | clamp | S1:L438; S3:L260 |
| drawer_travel | float | derived | 0.24 | equation | `= min(sampled[0.18,0.27], 0.72·box_depth)` | S1:L55; S4:L124 |
| door_leaf_count | int | derived | — | conditional | side_by_side→1; flanking→2(one/flank); else module→{slab 1/2, paneled 2, glazed 2/3} | S1/S3/S4 |
| (—) | constraint | — | — | inequality | `drawer_zone_height/N ≥ 0.06` else reduce N; `door_zone_width ≥ leaf·count` | interface/clearance |

连续采样契约：先采 independent（width/depth/heights/swing）→ 派生 drawer_travel（equation）→
用 inequality 投影（N vs zone height，door leaves vs zone width）→ conditional 解析
door_mechanism / door_leaf_count。全部在 `resolve_config` 完成。

## 7.5 编译预算 / compile budget
自报预算 **≤18s/seed**（依据：`rectilinear` 全 Box ≈3-5s；`bowfront`/`tapered` 每 seed 仅少量小
`threePointArc`/trapezoid 挤出 mesh，无重布尔并集 ≈8-15s；`tapered_legs` 复用一个 loft mesh）。
分档 tessellation：cadquery 挤出 tolerance≈0.0015（英雄弧面），角公差 0.2；N 个抽屉复用同构
helper。`--compile-timeout 120` 仅作 watchdog（约 6×预算）。

## Multiplicity / Copy Logic

- 单轴：`drawer_count` N。
- `count_param`: length of the per-column drawer-center list / loop bound (`for i in range(N)`), as
  in S1:L51-L54, S9:L49, S3:L167. product 域 N ∈ [1,8]；测试偏小 [1,6]，corner 触及 8.
- sampling domain（权重档）：小 N 高频（N∈{2,3,4} 常见），N=1 与 N∈{5,6,7,8} 稀有尾部。
- copied object: a `drawer_i` part = drawer `front` + open-top box (`box_side_0/1`, `box_bottom`,
  `box_back`) + folded `pull` + `inner_slide_0/1`, plus exactly one PRISMATIC `drawer_slide_i`
  joint (S1:L116-L197, L442-L465).
- naming: stable indexed `drawer_i` / `drawer_slide_i` (S1/S3/S9).
- placement: evenly spaced single vertical column in the drawer zone; axis (0,-1,0).
- joint policy: exactly one PRISMATIC per drawer, lower=0, travel=min(sampled, 0.72·box_depth); box
  stays engaged behind the front frame at full extension.
- gating: N clamped so each drawer front height ≥ 0.06m (reduce N if the zone is short). Large
  jeweler 2-column banks (S4 N=20) are represented as a single tall column up to N=8 (simplified;
  see Blocked).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | layout {door_over_drawers, drawers_over_door, side_by_side, flanking_doors} (S1/S2/S10/S11) + drawer multiplicity N (§8) + support_base {block/tapered/plinth/apron_feet/metal} (S1/S2/S3/S4/S8) |
| └ multiplicity | 同构件 ×N | 有 | drawer_count N∈[1,8]，小 N 高频；见 §8 |
| ② 关节类型 | 换 type/轴 | 有 | door REVOLUTE (all origins) vs PRISMATIC sliding door (S7); drawer PRISMATIC (all). 每种在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | body_form: `rectilinear`(Planar Boundary, S1), `bowfront`(Macro Surface, real arc meshes S5), `tapered`(Volumetric Envelope, real trapezoid meshes S6). 登记进 slot_choices |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | integrated/wood/brass pulls, veneer grain streaks, recessed door panels, glazed lattice — host-conformal visuals folded into owning part (S1:L73-113; S3:L219-226; S4:L170-179). 派生顺序 ③→⑤→④ |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | width[0.55,1.15], carcass_height[0.55,1.60], depth[0.34,0.50] (S1/S3/S4). 运动包络见下 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 palettes (oak/walnut/painted/industrial/slate/jeweler); 材质大类 painted-wood + metal + glass(glazed) ≥ ceil(0.5×6)=3 |

Motion envelope / motion_test_plan (⑤ non-continuous joints):
- `door_hinge_i` REVOLUTE, axis (0,0,∓1), opens outward toward −y; range [0, door_swing≤1.92].
- `door_slide_i` PRISMATIC, axis (1,0,0), range [0, slide_travel]; door stays within body width.
- `drawer_slide_i` PRISMATIC, axis (0,-1,0), range [0, drawer_travel]; box retains front-frame engagement.
- motion_test_plan: run `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`
  (drop to 32 when N≥5). Targeted `ctx.pose`: (a) a door opens outward (panel min-y decreases);
  (b) drawer_0 extends outward (part y decreases) and stays within body x/z. Doors rotate about
  vertical z so they never enter a drawer z-band; no sampled-pose exemption needed.

## 采样与覆盖审计

总组合数（离散，忽略连续 scale）：body_form 3 × door_module 3 × door_mechanism ~1.5(gated) ×
layout 4 × support_base 5 × palette 6 × N(1..8) ≈ 3·3·4·5·6·8 ≈ 8640（gating 前上界）。

理由：形态主导多样性由 body_form(③) + layout(①) + support_base(①) + N(multiplicity) 承载；
door_module/mechanism 提供 ② 变化；palette 提供 ⑥。远超 300 topology target。

seed_domain_policy：procedural_first（seed 0 不特殊）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | per-seed `random.Random(seed)` weighted choices over all 7 slots + continuous scales; gating in `resolve_config` | slot_choices_for_seed == build choices |
| compatibility matrix | sliding⇒leaf==1 & wide zone else hinged; flanking⇒hinged & leaf==2; side_by_side⇒leaf==1; N reduced if drawer zone too short; glazed keeps ≥1 leaf | no floating, no closed-pose overlap, door swing within z-band, N max, rail engagement |
| controlled local variation | width/depth/carcass_height/base_height/door_swing continuous, clamped+derived travel | proportions vary without breaking mating/clearance/identity |
| regression overrides | none | — |
| random sweep | 0-35 initial pass, corner stage; 0-999 maturity audit | contract failures; axis_realization; viewer focus 0-9 |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | required ③ form slot |
| door_module | 3 | yes | yes | |
| door_mechanism | 2 | yes | no | gated (②) |
| layout | 4 | yes | yes | |
| support_base | 5 | yes | yes | body visuals |
| palette_style | 6 | yes | yes | |
| drawer_count | N (1-8) | yes | yes | multiplicity |

## Validator

- slot_choices_for_seed returns implemented module names for all 7 keys
- config_from_seed uses deterministic procedural sampling for all seeds incl. seed 0
- gating prevents illegal combos (sliding multi-leaf, flanking sliding, over-tall N)
- controlled scales clamped/derived in resolve_config; travel = f(box_depth)
- every door joint has REVOLUTE(z) or PRISMATIC(x); every drawer PRISMATIC (0,-1,0)
- every non-FIXED joint declares a MatingContract to real door/drawer + body front-frame visuals
- copied drawers follow `drawer_i` / `drawer_slide_i` naming & even placement
- no FIXED joints (base = body visuals)

## Reject cases
- doors-only or drawers-only output (loses co-existence identity)
- a door swinging into or overlapping a drawer's z-band / open drawer
- N so large a drawer front is < 0.06m tall (unreadable stack)
- bowfront/tapered downgraded to plain boxes (must be real curved/trapezoid meshes)
- decorative pull / leg emitted as a FIXED-joint part instead of a host visual
- drawer travel exceeding box depth (box leaves the carcass entirely)
- sliding door sliding past the carcass side silhouette

## 与相邻类别的边界
- 不该混入：wardrobe / display_cabinet（doors-only — 缺 drawer，违背 co-existence）
- 不该混入：chest_of_drawers / dresser（drawers-only — 缺 door）
- 不该混入：desk_with_drawer（书桌以工作台面为主体，抽屉附属，非门+抽屉共存柜体）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 12 5-star sources; ③ form slot = body_form (rectilinear/bowfront/tapered) with real curved/trapezoid meshes |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | layout/door/drawer/support | side_by_side, slab, N-loop, block_legs | rec_...004 | L116-L465 | drawer loop, hinge/slide semantics, center_divider, block legs |
| S2 | door/support/layout | paneled, apron_feet, door_over_drawers | rec_...003 | L32-L282 | recessed door, apron+feet, door-over-drawer joints |
| S3 | support/layout/drawer | tapered_legs, door_over_drawers, N=4 | rec_...001 | L26-L347 | tapered leg loft, 4-drawer loop |
| S4 | door/support/drawer | glazed, plinth, large bank | rec_...002 | L135-L410 | glazed lattice door, marble plinth |
| S5 | body_form | bowfront | rec_...var_body_bowfront | L65-L214 | real curved arc-extrude fronts |
| S6 | body_form | tapered | rec_...var_body_tapered | L59-L122 | real trapezoid-extrude sides |
| S7 | door_mechanism | sliding | rec_...var_door_sliding | L323-L447 | PRISMATIC door + track rails |
| S8 | support | metal_legs | rec_...var_support_metal_legs | L346-L378 | splayed cylinder legs |
| S9 | drawer | N=2 | rec_...var_drawers_n2 | L49,L444-L467 | N=2 multiplicity fork |
| S10 | layout | drawers_over_door | rec_...var_layout_drawers_over_door | L258-L287 | vertical flip |
| S11 | layout | flanking_doors | rec_...var_layout_flanking_doors | L365-L573 | two dividers + outer-hinged flanks |
| S12 | probe | bow+double-door | rec_...var_probe_curved_double_door | L53-L421 | curved-front × double-door compatibility |

## Blocked / Excluded
- corner/angled-footprint cabinet: excluded — no source geometry for angled footprint (unsourced ③).
- standalone handle/grip & standalone ⑤/⑥ variants: record_only companions, not slots.
- 2-column apothecary bank (S4 N=20): simplified to a single column up to N=8; full 2-column grid
  excluded to bound collision/compile risk (multiplicity already source-backed at 1/2/3/4).
- doors-only / drawers-only forks: forbidden (drift out of subcategory).
