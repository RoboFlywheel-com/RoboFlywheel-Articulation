# Modular Spec - Industrial / Drill press table

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Drill_press_table` |
| template path | `agent/templates/Industrial_Drill_press_table.py` |
| test path (optional) | `tests/agent/test_Industrial_Drill_press_table_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root mount spine + chained worktop child + parallel lock-lever child + optional fold-leaf grandchild + 3 multiplicity axes) |
| function stem | `industrial_drill_press_table` (exports `build_industrial_drill_press_table`, `config_from_seed`, `run_industrial_drill_press_table_tests`) |

`pattern = mixed`: a `column` root (invariant cast base + upright tube) carries a
`carriage` that rides the column on a PRISMATIC **height slide**; the carriage
carries a `table` worktop on a REVOLUTE/swivel **tilt** joint and a `lock_lever`
on the clamp joint. The mount spine (column+carriage) is Slot A (root); the
worktop is Slot B (chained to the carriage); the lock lever is Slot C (parallel
child of the carriage). An optional fold-out `leaf` hangs off the table. Three
multiplicity axes ride on the worktop: `slot_count`, `fence_count`, `track_count`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 10 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 11 were read in full (origin full read; each variant diffed against origin + targeted reads of the differing part/joint/helper) |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`).
Every one shares the identical spine `column -> [height_slide PRISMATIC Z] ->
carriage -> [table_tilt REVOLUTE X] -> table` + `carriage -> [lever_pivot
REVOLUTE X] -> lock_lever`:

- `rec_industrial__drill_press_table__002_png_...bf057f97` - ORIGIN 母本 (rounded-rect
  plywood+laminate composite worktop, forked-yoke trunnion carriage, REVOLUTE-X
  tilt, cam lock lever). model.py:1-448.
- `rec_drill_press_var_cast_iron_slab` - ③ worktop form: composite plate -> single
  solid cast-iron slab with milled T-slot channels + trunnion lugs.
- `rec_drill_press_var_round_table` - ③ worktop form: rectangular -> round disc with
  four radial T-slots + concentric dog-hole rings.
- `rec_drill_press_var_side_tilt` - ② joint axis: `table_tilt` REVOLUTE axis X -> Y
  (side tilt).
- `rec_drill_press_var_column_swing` - ② joint axis: table motion REVOLUTE axis Z
  (`table_swing`, swivel about the vertical) with wide range.
- `rec_drill_press_var_screw_clamp` - ② joint type: `lever_pivot` REVOLUTE cam ->
  PRISMATIC screw clamp (T-handle, axis -Y, 0..0.012 m).
- `rec_drill_press_var_single_pivot` - ③/① mount form: symmetric forked yoke ->
  single-sided cantilever pivot bracket + stub trunnion.
- `rec_drill_press_var_flip_leaf` - ① skeleton: adds a `leaf` part + `leaf_hinge`
  REVOLUTE (parent=table) that folds up about the front edge.
- `rec_drill_press_var_slot_count` - multiplicity: worktop clamping T-slots 2->4
  evenly-spaced parallel slots.
- `rec_drill_press_var_fence_segments` - multiplicity: fence faces 2->3 segments.
- `rec_drill_press_var_track_count` - multiplicity: 3 parallel aluminium T-track
  rails inlaid across the worktop surface (+ per-rail screws).

## 核心身份

An **adjustable auxiliary drill-press table / worktable** for a benchtop drill
press: a cast **base + vertical column** (the ground reference), a **carriage /
collar** that clamps around the column and slides up/down (height adjust
PRISMATIC), and a **work surface / table** mounted on the carriage through a
**tilt (or swivel) bearing** so the work can be angled, plus a **clamp lever /
knob** that locks the height/tilt. The worktop is drilled with dog holes and
clamping T-slots and usually carries a two-piece **fence** and/or inlaid T-track
rails. At least two real non-fixed joints are always present (height slide +
table tilt); a lock lever (cam or screw) is a third. Default mature domain: a
~0.4-0.6 m benchtop auxiliary table on a ~0.9 m column.

Not to be confused with the neighbouring picture subclasses **Industrial /
Drill press (whole machine)** (which would add the motor head, spindle, quill
and belt housing - here only the *table sub-assembly* is modelled, the column is
a plain upright), **Industrial / Machinist workbench** (a free-standing 4-leg
bench, no column/carriage/tilt), or **Industrial / Rotary table** (a horizontal
indexing table with no column height slide).

## 槽位 + 候选模块表

### Slot A: mount (root . ③/① mount form + PRISMATIC height slide)

The ground spine. Emits the `column` root part (invariant cast base plate +
upright tube + base flange + flange bolts) and the `carriage` part (split clamp
collar jaws + saddle + trunnion support + clamp screw) chained to the column by
the `height_slide` PRISMATIC joint (axis Z). Only the **trunnion support form**
varies; both candidates expose the same trunnion mount datum
(`trunnion_x=0, trunnion_y=TABLE_Y+0.055, trunnion_z`) so Slot B is mount-form
independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `forked_yoke` | forked_anchor (origin) | `rec_industrial__drill_press_table__002...` | L99-L178, L262-L270 | eligible | symmetric forked yoke: two `yoke_arm_{0,1}` cheeks + `yoke_rail_{0,1}` straddle the trunnion shaft; split 5-jaw collar. **Macro Surface Construction** (twin-cheek fork). |
| `single_bracket` | forked_anchor | `rec_drill_press_var_single_pivot` | L99-L120 (`_carriage_casting`), part build L64-L95 | eligible | single-sided cantilever `pivot_bracket` + `bracket_rail` + `stub_trunnion` replacing the twin fork; same collar + saddle. **Macro Surface Construction** (single cantilever). |

### Slot B: worktop (chained to carriage . ③ Primary Form Family + ② motion + ① leaf + multiplicity)

The category ID slot. Emits the `table` part (worktop body + `tilt_trunnion`
shaft + fence assembly), the carriage->table **motion** joint, and optionally a
fold-out `leaf`. Same part-tree envelope across candidates (one worktop body
visual/mesh + `tilt_trunnion` cylinder + fence faces + cap + rails + screws);
only the worktop's core geometric prototype changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `rect_laminate` | forked_anchor (origin) | `rec_industrial__drill_press_table__002...` | L30-L82, L179-L240 | eligible | rounded-rectangular plywood `worktop_substrate` + `worktop_laminate` composite (2 cadquery plates) with round dog holes + straight clamping slots. **Planar Boundary Form** (rectangular boundary). |
| `cast_slab` | forked_anchor | `rec_drill_press_var_cast_iron_slab` | L24-L133 (`_cast_iron_table_slab`), L223-L240 | eligible | single solid cast-iron `worktop_slab` (one cadquery body) with milled T-slot channels (top opening + undercut) + trunnion lugs. **Volumetric Envelope Form** (solid slab). |
| `round_disc` | forked_anchor | `rec_drill_press_var_round_table` | L22, L41-L131 (`_drill_table_plate` disc), part L202-L232 | eligible | round `worktop_disc` (substrate+laminate discs) with radial T-slots at even angles + concentric dog-hole rings. **Planar Boundary Form** (circular boundary). |

### Slot C: locking (parallel child of carriage . ② joint type)

The clamp lock. Emits the `lock_lever` part + the clamp joint parented to the
carriage clamp ear.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `cam_lever` | forked_anchor (origin) | `rec_industrial__drill_press_table__002...` | L242-L260, L280-L288 | eligible | `lever_hub` + `lever_stem` + `lever_knob` sphere on a REVOLUTE cam pivot (axis X, +-1.2 rad). |
| `screw_knob` | forked_anchor | `rec_drill_press_var_screw_clamp` | L236-L262, L285-L293 | eligible | `screw_shaft` + `screw_tip` + `t_handle_bar` + 2 `t_handle_grip` spheres on a PRISMATIC screw clamp (axis -Y, 0..0.012 m). |

硬约束满足: Slot A=2, Slot B=3, Slot C=2 candidate; 每个 candidate 有
`forked_anchor` + `model.py:Lx-Ly`; 无 `world_knowledge_extrapolation`(全部 source-backed)。
Slot A/C 只 2 candidate: 源池对 mount-form 只给了 fork/single 两种真实结构,
对 clamp 只给了 cam/screw 两种真实结构 - 降到 2 有理由(sample-limited),不是 re-skin。

## 槽位图 (slot graph)

pattern: `mixed` (root spine + chained child + parallel child + optional grandchild + multiplicity)

```
column (root; invariant cast base + upright tube)
   |
   +--[height_slide PRISMATIC axis Z; captured clamp collar around column tube]--> carriage (Slot A: forked_yoke | single_bracket)
          |
          +--[table motion REVOLUTE axis X|Y|Z at the trunnion mount; captured trunnion in fork/bracket]--> table (Slot B worktop: rect_laminate | cast_slab | round_disc)
          |       |
          |       +--[leaf_hinge REVOLUTE axis X at front edge] (optional)--> leaf   (Slot B sub-axis: no_leaf | flip_leaf)
          |
          +--[lever_pivot REVOLUTE axis X (cam) | lever_screw PRISMATIC axis -Y (screw)]--> lock_lever (Slot C: cam_lever | screw_knob)
```

- **slot 顺序 / parent**: `mount` (Slot A) is the root - it emits `column` (root
  part) and `carriage`. `worktop` (Slot B) reads `carriage` via
  `ctx.upstream_interface.part_name` and parents its motion joint to it (chained
  child). `locking` (Slot C) is a parallel child of the carriage. Slot B/C each
  declare only `downstream` (re-export the carriage face) -> no auto chain joint;
  each module emits its own raw joint (same idiom as
  `Urban_Environment_Tipping_Barrow`).
- **接口点位**: column tube axis (0,0,z) - collar bore captures it (height
  slide). Carriage trunnion mount `(0, trunnion_y, trunnion_z)` - `tilt_trunnion`
  shaft captured by the fork cheeks / single bracket (table motion). Carriage
  clamp ear `(0.077, +-0.028, 0)` - lever hub/screw shaft.
- **跨 slot joint type/axis/range**: height_slide PRISMATIC Z [0, slide_travel];
  table motion REVOLUTE X|Y (+-tilt_range<=0.55) or Z (+-swing_range<=1.4);
  lever_pivot REVOLUTE X (+-1.2) or lever_screw PRISMATIC -Y [0, 0.012];
  leaf_hinge REVOLUTE X [0, pi/2].
- **互斥/派生**: motion axis, mount form, worktop form, clamp type are mutually
  orthogonal (all reference the shared trunnion / column / ear datums). `leaf`
  is available on any worktop. `slot_count`/`fence_count`/`track_count` ride the
  worktop. `round_disc` uses radial slots (its own slot layout), so `slot_count`
  for it maps to radial-slot count; `track_count` gated to 0 on `round_disc`
  (parallel rails do not fit a round disc - see Multiplicity).

## 每槽位 Module Emits / Interfaces

### Slot A / module forked_yoke | single_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `column` (root), `carriage` | origin L140, L162 |
| visuals (column) | `base_plate` (cadquery slotted plate) + `column_tube` (Cylinder) + `base_flange` (Cylinder) + 4 `flange_bolt_*` | origin L141-L160 |
| visuals (carriage) | 5-jaw split collar (`collar_rear`,`collar_side_{0,1}`,`clamp_ear_{0,1}`) + `saddle_block` + trunnion support (fork: `yoke_rail_{0,1}`,`yoke_arm_{0,1}`; single: `bracket_rail`,`pivot_bracket`,`stub_trunnion`) + `clamp_screw` | origin L163-L178; single_pivot L64-L95 |
| internal joints | `height_slide` PRISMATIC(Z, parent=column, child=carriage, [0,slide_travel]) | origin L262-L270 |
| downstream interface | `carriage` re-export (worktop + locking parent to it) | - |

### Slot B / module rect_laminate | cast_slab | round_disc
| emits | 描述 | 来源 |
|---|---|---|
| parts | `table` (+ optional `leaf`) | origin L179; flip_leaf L286 |
| visuals | worktop body (rect: `worktop_substrate`+`worktop_laminate`; cast: `worktop_slab`; round: `worktop_disc_substrate`+`worktop_disc_laminate`) + `tilt_trunnion` (Cylinder X) + fence (`fence_face_{i}` x fence_count, `fence_wood_cap`, `fence_top_track`, `fence_lower_rail`, `fence_screw_{i}`) + optional `t_track_{i}` x track_count (+ screws) + optional leaf visuals (`leaf_substrate`,`leaf_laminate`,`leaf_knuckle_{i}`,`leaf_hinge_pin`,table-side `table_hinge_knuckle_{i}`) | origin L179-L240; cast L223-L240; round L202-L232; fence_segments L133-L140,L226-L228; track_count L141-L163,L263-L265; flip_leaf L250-L318 |
| internal joints | table motion `table_tilt` REVOLUTE(X|Y) or `table_swing` REVOLUTE(Z), parent=carriage child=table, origin at trunnion mount; optional `leaf_hinge` REVOLUTE(X, parent=table child=leaf, [0,pi/2]) | origin L271-L279; side_tilt L271-L279; column_swing L278-L289; flip_leaf L348-L358 |
| upstream interface | **none declared** (chained child; parents motion joint directly to `carriage`) | - |
| downstream interface | re-export carriage downstream (passthrough) | - |

### Slot C / module cam_lever | screw_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lock_lever` | origin L242 |
| visuals | cam: `lever_hub`+`lever_stem`+`lever_knob`(Sphere); screw: `screw_shaft`+`screw_tip`+`t_handle_bar`+2 `t_handle_grip`(Sphere) | origin L242-L260; screw_clamp L236-L262 |
| internal joints | `lever_pivot` REVOLUTE(X, +-1.2) or `lever_screw` PRISMATIC(-Y, [0,0.012]), parent=carriage child=lock_lever, origin at clamp ear | origin L280-L288; screw_clamp L285-L293 |
| upstream interface | **none declared** (parallel child; parents joint directly to `carriage`) | - |
| downstream interface | re-export carriage downstream (passthrough) | - |

活动件语义: height_slide 升降工作台; table motion 倾斜/回转工作面; lever 夹紧锁定
(cam 转 / screw 拧); leaf_hinge 折起延伸板。不动细节 (dog holes / T-slots / fence
faces / cap / rails / screws / flange bolts) 全部写成宿主 part visual 或直接切进
worktop mesh (cadquery cut),非独立 FIXED part (Rule 1)。captured trunnion (fork/
bracket) 与 captured clamp collar (column) 用 element-scoped `allow_overlap` (Rule 2
例外),motion/slide/lever 原点落在真实 trunnion / column / ear 几何 (origin honesty)。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount_style` | enum | forked_yoke / single_bracket | forked_yoke | choice | procedural sampler | Slot A |
| `worktop_form` | enum | rect_laminate / cast_slab / round_disc | rect_laminate | choice | procedural sampler | Slot B |
| `table_motion` | enum | tilt_front / tilt_side / swing_column | tilt_front | choice | procedural sampler | side_tilt/column_swing |
| `clamp_style` | enum | cam_lever / screw_knob | cam_lever | choice | procedural sampler | Slot C |
| `leaf_style` | enum | no_leaf / flip_leaf | no_leaf | choice | procedural sampler | flip_leaf |
| `slot_count` | int | {2,3,4} (obs: origin 2 side pairs, slot_count 4) | 3 | independent | weighted; radial count for round_disc | origin L76-L78, slot_count L75-L79 |
| `fence_count` | int | {2,3} (obs: origin 2, fence_segments 3) | 2 | independent | weighted | origin L209, fence_segments FENCE_N=3 |
| `track_count` | int | {0,2,3} (obs: origin 0, track_count 3) | 0 | conditional | gated to 0 on round_disc | origin (none), track_count TRACK_COUNT=3 |
| `table_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; worktop footprint (len/depth or radius) | origin L21-L22 |
| `column_h_scale` | float | [0.90, 1.20] | 1.0 | independent | uniform, clamp; column tube length | origin L143 |
| `slide_travel` | float | derived | - | equation | `= 0.5 * column_tube_len - 0.13` (clamp [0.10,0.30]); slide never runs the carriage off the tube | origin L269 |
| `tilt_range` | float | [0.30, 0.55] | 0.45 | conditional | tilt_front/side REVOLUTE +- range (rad); n/a for swing | origin L278 |
| `swing_range` | float | [0.90, 1.40] | 1.20 | conditional | swing_column REVOLUTE +- range (rad); n/a for tilt | column_swing L288 |

所有 equation/conditional 在 `resolve_config` 内求解; builder 不失败。

### 7.5 编译预算 / compile budget (必填)

**Per-seed compile budget: <= 25 s** (hang-guard `--compile-timeout 75`). Geometry
is dominated by cadquery boolean cuts on ONE worktop body per seed: rect (fillet
+ <=7 dog-hole cuts + <=4 slot cuts), cast slab (fillet + chamfer + 2*3 T-slot
box cuts + centre hole + 4 dog holes + 2 lug unions), round disc (centre hole +
4 radial-slot cutters (3 unions each) + 8 dog holes). The base plate is a small
filleted cadquery plate with 2-4 slot cuts. All other parts are SDK
`Box`/`Cylinder`/`Sphere` primitives (cheap). Cadquery cut counts are capped by
`slot_count<=4` and dog-hole rings; no lathe/loft. Expect 6-16 s/seed; if over,
drop dog-hole/slot counts and base-plate cuts first (`AUTHORING.md` §C).

## Multiplicity / Copy Logic

**三根独立 multiplicity 轴** (各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限):

### 轴 1 - `slot_count` (工作台夹紧 T 槽数)
- `count_param`: `slot_count`; `N_range` product `[2,4]`, test `[2,4]`; sampling
  domain 加权 `{2:0.4, 3:0.3, 4:0.3}`。
- copied object: rect/cast -> parallel clamping T-slots cut across the worktop at
  uniform X spacing (`slot_spacing = width / (N+1)`); round_disc -> `N` (clamped
  to 4) radial T-slots at even angular spacing `360/N deg`.
- naming: cut features inside the worktop mesh (not separate parts). placement:
  uniform. joint policy: none (cut geometry). source: origin L76-L78 (2 pairs),
  slot_count L75-L79 (4 parallel), round L62-L92 (radial).
- 数量变化不改主体形态 (还是同一 worktop_form) 或机制。

### 轴 2 - `fence_count` (围栏面段数)
- `count_param`: `fence_count`; `N_range` `[2,3]`, test `{2,3}`; sampling domain
  加权 `{2:0.6, 3:0.4}`。
- copied object: `fence_face_{i}` aluminium box segments spread along X on the
  worktop rear, sharing one `fence_wood_cap` + `fence_top_track` +
  `fence_lower_rail`, with one `fence_screw_{i}` per segment gap.
- naming: `fence_face_{i}` / `fence_screw_{i}`. placement: uniform along X.
  joint policy: none (host visuals). source: origin L209 (2), fence_segments
  `_add_fence_face` + `FENCE_N=3`.

### 轴 3 - `track_count` (工作面 T 型轨道条数)
- `count_param`: `track_count`; `N_range` `[0,3]`, test `{0,2,3}`; sampling
  domain 加权 `{0:0.5, 2:0.2, 3:0.3}`。
- copied object: `t_track_{i}` aluminium rail boxes inlaid flush on the worktop
  top at uniform Y spacing (in front of the fence), each with 4
  `t_track_{i}_screw_{j}`.
- naming: `t_track_{i}` / `t_track_{i}_screw_{j}`. placement: uniform Y.
  joint policy: none (host visuals). source: track_count `_add_t_track` +
  `TRACK_COUNT=3`, `_t_track_y_positions`. gating: 0 on `round_disc` (parallel
  rails do not fit a round worktop).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构骨架 candidate: mount fork twin-cheek (origin, forked_anchor) vs single cantilever bracket (single_pivot, forked_anchor); optional fold-out `leaf` part + `leaf_hinge` edge (flip_leaf, forked_anchor, part/joint count 4->5). 全部 source-backed。 |
| └ multiplicity | 同构件 xN | 有 | 见 §8: slot_count {2,3,4} (origin/slot_count), fence_count {2,3} (origin/fence_segments), track_count {0,2,3} (origin/track_count)。 |
| ② 关节类型 | 图不变,边换 type/轴 | 有 | table motion REVOLUTE X (origin) / REVOLUTE Y (side_tilt) / REVOLUTE Z (column_swing); clamp REVOLUTE (origin cam) / PRISMATIC (screw_clamp). 全部 forked_anchor; 每种 type/轴都在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变,换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 的 worktop slot**: rectangular composite plate (origin, Planar Boundary Form) / solid cast-iron slab (cast_iron_slab, Volumetric Envelope Form) / round disc (round_table, Planar Boundary Form)。附 mount-form: twin fork / single bracket (Macro Surface Construction, 登记为 mount slot)。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | dog holes + clamping T-slots cut into the worktop (随 ③ worktop_form + ⑤ table_scale 逐-seed 由宿主板面派生位置/半径), fence faces + wood cap + tracks + screw heads, inlaid T-track rails, flange bolts。source_type=record_only (origin/cast/round/fence_segments/track_count)。派生顺序 ③ worktop 面 -> ⑤ 缩放 -> ④ 切孔/贴条。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale: table_scale[0.85,1.15]、column_h_scale[0.90,1.20]。关节运动包络: height_slide PRISMATIC axis Z [0, slide_travel<=0.30]; table motion REVOLUTE axis X|Y 开启双向 [闭合0, +-tilt_range<=0.55] 或 axis Z [闭合0, +-swing_range<=1.4]; lever REVOLUTE X [+-1.2] 或 PRISMATIC -Y [0,0.012]; leaf_hinge REVOLUTE X [0, pi/2]。`motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`; targeted `ctx.pose` - height_slide 抬升 table、motion 倾斜/回转 worktop、lever 转/移、leaf 折起。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal (cast/steel/aluminium) + painted; 配色 >=5 colorway: `shop_cast` (黑铸 + 木纹 + 浅层压 + 铝), `granite_gray`, `machinist_green`, `safety_red`, `raw_steel`, `walnut_bench`。材质大类覆盖 >= ceil(0.5x6)=3。 |

**收尾自检**: 0-9 seed 渲染须肉眼见到 rect/cast/round 三种 worktop、X/Y/Z 三种 motion、
fork/single 两种 mount、cam/screw 两种 clamp、有无 leaf、slot/fence/track 数量档、
材质配色多样、slide/tilt/swing/lever/leaf 全程不穿模。

## 采样与覆盖审计

总组合数 (distinct slot-choice tuple 上界):
- mount 2 x worktop 3 x motion 3 x clamp 2 x leaf 2 = 72 离散骨架;
  x slot_count 3 x fence_count 2 x track_count(avg ~2.3 reachable, round gates to 1)
  ~= 72 x 3 x 2 x 2.3 ~= **~990**。

理由: >300 富类别建议达标 (离散结构词汇宽: 3 form x 3 motion x 2 mount x 2 clamp
x 2 leaf + 3 multiplicity)。report-only,不设 gate,不反推上游变体数量。

seed_domain_policy: `procedural_first`。

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 mount_style、worktop_form、table_motion、clamp_style、leaf_style、palette,
再抽 slot_count/fence_count/track_count (加权),再抽连续 scale (table_scale/
column_h_scale/tilt_range/swing_range)。seed 0 pinned 到 origin 母本组合
(forked_yoke + rect_laminate + tilt_front + cam_lever + no_leaf, shop_cast) 作
documented regression anchor (sparse override; 其余 seed 全 procedural)。random
sweep `0-15` (fast) -> `0-35` (final) -> corner。

Topology target: 1000-seed slot-choice tuple 覆盖用于成熟度观察; 真实上界 ~990
(见上)。report-only。

Controlled local parameterization: `table_scale` (worktop footprint; fence /
slot / trunnion 派生于此)、`column_h_scale` (tube length; slide_travel equation 派生)、
`tilt_range` / `swing_range` (conditional 运动幅度)。全部在 `resolve_config` clamp /
派生; 不破坏 captured-collar / captured-trunnion 接口、joint 原点、multiplicity。
连续尺寸契约: 先采 independent (table_scale/column_h_scale/tilt_range/swing_range)
-> equation 派生 slide_travel -> conditional 解析 tilt_range/swing_range/track_count。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 mount->worktop->motion->clamp->leaf->mult->scale,加权 choice | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | swing_column uses swing_range (tilt_range n/a); round_disc gates track_count=0 and maps slot_count to radial slots; all form/mount/clamp/leaf orthogonal | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 4 clamp 连续 scale + 1 derived | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本 (documented anchor); 无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| mount | 2 | yes | no | fork/single (sample-limited: source pool gives 2 real mount forms) |
| worktop | 3 | yes | yes | rect/cast/round |
| locking | 2 | yes | no | cam/screw (sample-limited: source pool gives 2 real clamp types) |
| table_motion (sub) | 3 | yes | yes | tilt_front/tilt_side/swing_column |
| leaf (sub) | 2 | yes | no | no_leaf/flip_leaf |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ table_motion/leaf/slot_count/fence_count/track_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (swing->swing_range; round_disc->track_count=0 + radial slots) in `resolve_config`
- controlled local scales clamped; cannot break captured-collar / captured-trunnion interfaces, motion/slide/lever origin honesty, or multiplicity
- cross-part scale dependencies (slide_travel from column length) derived in `resolve_config`
- captured clamp-collar (column) + captured trunnion (fork/bracket) overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: height_slide PRISMATIC(Z); table motion REVOLUTE(X|Y|Z); lever REVOLUTE(X) or PRISMATIC(-Y); leaf_hinge REVOLUTE(X)
- copied `fence_face_{i}` / `t_track_{i}` / worktop slot cuts follow naming + placement policy
- `run_industrial_drill_press_table_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism (slide/motion/lever/leaf)

## Reject cases

- Carriage collar clears the column with a gap and floats (isolated part) -> collar bore snug on the column tube with element-scoped `allow_overlap` (captured sliding clamp), never a broad part overlap.
- Table motion steered pose drives the worktop or trunnion into the carriage/column at min/max -> shrink `tilt_range`/`swing_range` or keep the pivot at the trunnion mount; declare only the captured-trunnion overlap.
- Height slide runs the carriage off the top/bottom of the column tube -> `slide_travel` derived from tube length (clamped), so the collar always stays on the tube.
- Fold leaf folded to 90 deg collides with the fence or drives through the worktop -> hinge axis sign folds the leaf UP and away from the fence; cap at pi/2; allow only the captured hinge-knuckle/pin overlap.
- Worktop form swap leaves dog holes / T-slots / fence floating off the new plate (constant positions on a round disc or scaled slab) -> derive cut/fence/track positions from the realized worktop footprint + `table_scale` (Rule 4).
- track_count>0 parallel rails on a `round_disc` overhang the circular boundary -> gate track_count=0 on round_disc.
- Downgrading the cadquery cut worktop / cast slab / round disc to a plain uncut Box (Rule 3 violation) - keep the milled slots/holes.

## 与相邻类别的边界

- 不该混入: **Industrial / Drill press (whole machine)** (完整钻床带电机头、主轴、
  quill、皮带罩; 本类只建工作台 sub-assembly, 立柱是素直柱)。
- 不该混入: **Industrial / Machinist workbench** (独立四脚工作台, 无立柱/滑座/倾斜)。
- 不该混入: **Industrial / Rotary index table** (水平分度台, 无立柱升降滑座)。
- 不该混入: 一个只有台面无立柱升降与倾斜关节的固定桌 (缺类别定义的 height slide +
  table tilt 双关节身份特征)。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全部 11 样本 source-backed 采纳; mount(2)/locking(2) 因源池只给两种真实结构降到 2-candidate, 已说明非 re-skin; swing_column 实现为 REVOLUTE Z 绕 trunnion 挂点 (类别 ② 轴变), 源锚 column_swing 的 Z revolute table 运动, 未逐字复制其绕立柱中心的原点 - 更安全且忠实 ② 轴意图, 待人工目检确认回转读感。 |

## 模板实现备注 (可选)

- worktop footprint / trunnion mount / column datums single-sourced in
  `ResolvedConfig` (Contract 3c); mount/worktop/locking 挂点全部从中派生, 四轴正交。
- captured clamp-collar (column tube) + captured trunnion (fork cheeks / single
  bracket) -> 原始 joint (no MatingContract, grandfathered) + element-scoped
  `allow_overlap`, 与全部 5 星源一致 (Rule 2 例外)。
- 每个 worktop_form 用一次 cadquery 布尔; base plate 用一个小 cadquery 布尔; 其余全
  SDK primitive - 保编译预算。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`: mount root 声明
  downstream (carriage); worktop/locking 只声明 downstream (re-export carriage)
  -> 无自动 chain joint, 各模块发原始 joint 到 carriage/column (parallel-children,
  同 Tipping_Barrow 惯用)。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | forked_yoke + rect_laminate + tilt_front + cam_lever | `rec_industrial__drill_press_table__002...` (origin 母本) | L1-L448 | 全部 part tree + 3 关节 + rect worktop cadquery + fork mount + cam lever + test 语义 |
| S2 | B ③ | cast_slab | `rec_drill_press_var_cast_iron_slab` | L24-L133, L223-L240 | 实心铸铁 slab + T-slot 通道 + trunnion lugs |
| S3 | B ③ | round_disc | `rec_drill_press_var_round_table` | L22, L41-L131, L202-L232 | 圆盘工作面 + 径向 T-slot + 同心 dog hole |
| S4 | B ② | tilt_side | `rec_drill_press_var_side_tilt` | L271-L279 | 侧倾 REVOLUTE 轴 Y |
| S5 | B ② | swing_column | `rec_drill_press_var_column_swing` | L278-L289 | 回转 REVOLUTE 轴 Z |
| S6 | C ② | screw_knob | `rec_drill_press_var_screw_clamp` | L236-L262, L285-L293 | PRISMATIC 螺旋夹紧 T-handle |
| S7 | A ③/① | single_bracket | `rec_drill_press_var_single_pivot` | L64-L120 | 单侧悬臂 pivot bracket + stub trunnion |
| S8 | B ① | flip_leaf | `rec_drill_press_var_flip_leaf` | L30-L34, L250-L358 | 折叠延伸板 leaf part + REVOLUTE leaf_hinge |
| S9 | B mult | slot_count=4 | `rec_drill_press_var_slot_count` | L75-L79 | 平行夹紧 T-slot 数量上界 |
| S10 | B mult | fence_count=3 | `rec_drill_press_var_fence_segments` | L133-L140, L226-L228 | 围栏面段数 |
| S11 | B mult | track_count=3 | `rec_drill_press_var_track_count` | L29-L34, L133-L163, L263-L265 | 工作面 T-track 轨道条数 |
</content>
</invoke>
