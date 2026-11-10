# storage_cart_with_drawers_on_wheels — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `storage_cart_with_drawers_on_wheels` |
| template path | `agent/templates/storage_cart_with_drawers_on_wheels.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 (source map ★: 6 origin anchors + 6 slot-fork variants) |
| read_count | 3 variant model.py fully inspected (`caster_braked_swivel`, `drawer_count_3`, `drawer_layout_twin_bank`) + source map inventory of remaining 9 |
| read_scope | picture-derived origin models 001-006 + 12 fork variants under `rec_0611_storage_cart_with_drawers_on_w_var_*` |
| source_index_policy | only adopted module sources indexed below |

Structure family distribution (from source map + reads):

| family | evidence | notes |
|---|---|---|
| open tubular cart frame + tray + drawers + 4 casters | var `frame_open_tubular_cart` (from 006) | 4 casters (2 swivel + 2 fixed / all swivel), single bank drawers |
| rounded tower cabinet + drawers + 4 casters | var `frame_rounded_tower` (from 001) | fully enclosed cabinet on casters, single drawer bank |
| twin-bank medical cart + top handle + 4 braked casters | var `drawer_layout_twin_bank` (from 002) | two parallel drawer banks side-by-side |
| retractable / brake caster + drawer stack | var `caster_retractable_caster`, `caster_braked_swivel` | swivel + brake pattern (revolute swivel + continuous roll + optional brake lever) |

## 核心身份

A grounded, wheeled **storage cart** whose primary use is stowing small items in
one or more banks of **pull-out drawers**, standing on **four caster wheels**
(swivel or fixed). Must retain:

- a raised carcass / frame supporting ≥1 drawer bank (typically 0.60–0.95 m tall);
- ≥1 PRISMATIC drawer (multiplicity axis);
- 4 wheels on the floor, each with at least one non-FIXED joint (CONTINUOUS
  roll about a horizontal axle; swivel casters add a REVOLUTE/CONTINUOUS +Z);
- freestanding on the wheels (no upstream mount).

不该混入：
- office desk / office table (has raised worktop, no casters, drawers are same
  role but the identity is a table with legs) — see `office_table_with_doors_or_drawers`.
- rolling toolbox with telescoping handle (2 wheel + drag box, not a cart);
- shelving unit (no casters, no drawers, only open shelves).
- shopping cart / trolley (open basket, no drawers).
- warehouse platform cart (bare deck, no drawer bank).

## 槽位 + 候选模块表

### Slot A：`frame_form` (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `open_tubular_cart` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_frame_open_tubular_cart` (from 006) | source map §origin_design storage_cart_006, adapted L60-L200 | Volumetric Envelope Form | eligible | 四角立柱 + 顶部收纳盘（open tray）+ 底部驮托抽屉栈；侧面开放 |
| `rounded_tower` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_frame_rounded_tower` (from 001) | source map §origin_design storage_cart_001, `_rotated_xy` L58-L120 | Volumetric Envelope Form | eligible | 圆角封闭柜体（rounded rectangular envelope），四壁 + 顶盖 |
| `rectangular_cabinet` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_drawer_count_3` (from 002) & `_drawer_count_8` (from 003) | drawer_count_3 model.py L166-L226 (_build_cabinet_shell / cabinet visuals) | Volumetric Envelope Form | eligible | 直角矩形柜体 (baseline)，四壁 + 底 + 顶盖 |
| `slim_service_stand` | world_knowledge_extrapolation | reviewer-authored variation of `rectangular_cabinet` (narrow tall frame) — same part tree/primitive/interface, only Volumetric Envelope Form changes (Planar & Envelope narrower + taller) | n/a (form_subtype variant of rectangular_cabinet) | Volumetric Envelope Form | eligible | 更窄更高的矩形柜体（相同 primitive、相同 interface）；单 bank 抽屉 |

### Slot B：`caster` (②机构候选，wheel_type multiplicity handler)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `swivel_caster` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_caster_braked_swivel` (from 004) | model.py L192-L260 (_add_caster_fork_visuals + swivel articulation), L416-L450 | eligible | 4 只旋转 caster: fork REVOLUTE +Z (swivel) + wheel CONTINUOUS +X (roll) |
| `fixed_caster` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_caster_retractable_caster` (from 003) | source map §origin_design storage_cart_003 `_build_caster_fork` | eligible | 4 只固定 caster: bracket FIXED + wheel CONTINUOUS +X only |
| `mixed_swivel_fixed` | forked_anchor | (from 004 variant + 003 variant combined) — front 2 swivel, rear 2 fixed; both real anchors provide the joint semantics | model.py refs L192-L260 (var_caster_braked_swivel) + `_build_caster_fork` (drawer_count_3) | eligible | 前 2 swivel + 后 2 fixed (常见工业货柜配置) |
| `braked_swivel_caster` | forked_anchor | `rec_0611_storage_cart_with_drawers_on_w_var_caster_braked_swivel` (from 004) | model.py L262-L312 `_add_brake_lever_visuals` + L451-L472 brake_engage joint | eligible | swivel + roll 之外每只加一根 REVOLUTE 制动杆 |

### Slot C：`drawer_count` (multiplicity, N per bank)

| module_name | source_type | source evidence | model.py:Lx-Ly | eligibility | 结构特征 |
|---|---|---|---|---|---|
| `2_drawers`, `3_drawers`, `4_drawers`, `5_drawers`, `6_drawers`, `8_drawers` | forked_anchor | `_var_drawer_count_3` (3), `_var_drawer_count_8` (8), `_var_drawer_count_12` (12) | model.py L370-L410 (drawer stack loop) | eligible | N 个同构 PRISMATIC drawer 沿 body -Y (front) 滑出 |

- N per bank ∈ [2, 8] (bounded by compile budget; 12-drawer source used only as
  design evidence, template caps N at 8 to keep sweep-pipeline seed budget
  ≤120 s and to avoid excessive AABB comparisons).
- If `drawer_layout=twin_bank`, drawer_count applies **per bank**, total = 2×N;
  in `single_bank` the total is N.

### Slot D：`drawer_layout` (①)

| module_name | source_type | source evidence | model.py:Lx-Ly | eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_bank` | forked_anchor | `_var_drawer_layout_single_bank` (from 005) | source map §origin fifteen_drawer_rolling_cart | eligible | 单列抽屉栈，居中 |
| `twin_bank` | forked_anchor | `_var_drawer_layout_twin_bank` (from 002) | drawer_layout_twin_bank model.py L166-L250 | eligible if drawer_count≤5 | 两列平行栈（左右），共享 body |

### Slot E：`palette_style` (⑥ material/palette; ≥4 candidates)

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `medical_white` | forked_anchor | `_var_drawer_layout_twin_bank` (from 002) | eligible | 白 + 铝 + 蓝抽屉标签（record_only recolor） |
| `industrial_gray` | forked_anchor | `_var_frame_open_tubular_cart` (from 006) & `_var_drawer_count_3` (from 002) | eligible | 灰体 + 黑 caster + 红把手 |
| `warm_oak_utility` | world_knowledge_extrapolation | palette recolor of `rectangular_cabinet` (record_only) | eligible | 木质柜体 + 黑金属 caster |
| `safety_yellow` | world_knowledge_extrapolation | record_only palette swap | eligible | 亮黄 body + 黑 caster + 黑抽屉；工业车间 |
| `stainless_steel` | forked_anchor | `_var_frame_rounded_tower` (from 001) | eligible | 光亮不锈钢 + 黑 caster |

## 槽位图（slot graph）

pattern = `mixed` (parallel-children + multiplicity + optional brake lever child)

```
[body]  (grounded root; frame / carcass visuals + optional top tray/handle visuals)
  ├── PRISMATIC (0,-1,0) drawer_{bank}_{i}   (i ∈ [0,drawer_count-1]; bank ∈ single_bank|left|right)
  └── (per-caster subtree; ×4)
        caster_swivel_j         (REVOLUTE (0,0,1)  OR CONTINUOUS (0,0,1); FIXED for fixed_caster / rear-of-mixed)
          └── caster_wheel_j    (CONTINUOUS (1,0,0) roll)
        (braked_swivel_caster only) brake_lever_j (REVOLUTE (1,0,0), parent=fork)
```

- Drawer joint origin: front face of the corresponding pedestal at drawer Z.
- Caster swivel joint origin: at body floor bottom, at each corner inset from
  `(±cart_w/2 − inset_x, ±cart_d/2 − inset_y, floor_z)`; wheel axle sits below.
- Wheel roll axis: (1, 0, 0); swivel axis: (0, 0, 1).
- Brake lever pivots about (1, 0, 0) on the fork's outer boss.

## 每槽位 Module Emits / Interfaces

### Slot A / frame_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visuals only (frame walls, floor, top cap); no separate parts | source map storage_cart_001..006 |
| internal joints | none | — |
| upstream interface | (grounded root, no upstream) | — |
| downstream interface | drawer bank front face(s), 4 caster mount points | — |

### Slot B / caster (all variants)
| emits | 描述 | 来源 |
|---|---|---|
| parts | 4 × `caster_fork_j` (or `caster_bracket_j`), 4 × `caster_wheel_j`, optional 4 × `brake_lever_j` | model.py L336-L472 (var_caster_braked_swivel) |
| internal joints | body→fork (REVOLUTE +Z or FIXED); fork→wheel (CONTINUOUS +X); optional fork→brake (REVOLUTE +X) | ibid |
| upstream interface | 4 corner mount plates on body floor bottom | ibid |
| downstream interface | wheel contact plane at z=0 | ibid |

### Slot C+D / drawer_count × drawer_layout
| emits | 描述 | 来源 |
|---|---|---|
| parts | N (or 2N) × `drawer_{i}` parts (front panel + box) | var drawer_count models |
| internal joints | body→drawer PRISMATIC (0,-1,0) | ibid |
| upstream interface | pedestal front opening plane | ibid |
| downstream interface | drawer extends outward toward -Y | ibid |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | open_tubular_cart / rounded_tower / rectangular_cabinet / slim_service_stand | rectangular_cabinet | choice | procedural sampler | Slot A |
| `caster` | enum | swivel_caster / fixed_caster / mixed_swivel_fixed / braked_swivel_caster | swivel_caster | choice | sampler | Slot B |
| `drawer_count` | int | [2, 8] | 4 | independent | uniform, clamp; per-bank | Slot C |
| `drawer_layout` | enum | single_bank / twin_bank | single_bank | choice | sampler; if twin_bank, drawer_count clamped ≤5 | Slot D |
| `palette_style` | enum | medical_white / industrial_gray / warm_oak_utility / safety_yellow / stainless_steel | industrial_gray | choice | sampler | Slot E |
| `cart_width` | float | [0.44, 0.78] | 0.56 | independent | m | source_maps 001-006 |
| `cart_depth` | float | [0.36, 0.60] | 0.44 | independent | m | ibid |
| `cart_height` | float | [0.60, 0.95] | 0.78 | independent | m; carcass Z above floor | ibid |
| `drawer_travel` | float | [0.20, 0.34] | 0.28 | inequality | ≤ 0.85 × drawer_box_depth | var_drawer_count_3 L390 |
| `swivel_range` | float | radians, [1.20, 2.60] (upper) | π | independent | REVOLUTE swivel upper bound; unused for CONTINUOUS variant | var_caster_braked_swivel L420-L432 |
| `brake_angle` | float | radians, [0.40, 0.70] | 0.55 | independent | brake_lever upper limit (only for braked_swivel_caster) | var_caster_braked_swivel L455-L470 |
| (—) | constraint | — | — | inequality | wheel_radius + fork_drop < caster_gap; drawers must fit within cart_height − top_cap − plinth | mating |
| (—) | constraint | — | — | inequality | 4 casters must fit under cart footprint with wheel_w/2 clearance from edges | mating |

## 编译预算 / compile budget

- 目标 6–15 s / seed. 全部 Box primitives, 无 cadquery/mesh。 最大 N=8 抽屉 ×2 bank = 16 drawer parts + 4 casters + 4 wheels + optional 4 brake levers = ≤28 parts, ≤32 non-FIXED joints. Watchdog `--compile-timeout 120`.

## Multiplicity / Copy Logic

- axis 1: `drawer_count_count` per bank
  - `count_param`: `drawer_count` (per bank)
  - `N_range`: [2, 8] (product domain [2, 12] observed; template caps at 8)
  - sampling domain (weighted): 3–5 (high), 6–7 (mid), 2/8 (tail)
  - copied object: `drawer_{bank}_{i}` (bank ∈ {'', 'left_', 'right_'}); shared helper `_build_drawer`; even Z-pitch inside pedestal; joint policy: all PRISMATIC (0,-1,0), same travel
- axis 2: caster count = 4 (fixed, not procedurally varied — real-world storage
  carts overwhelmingly use 4 casters)

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `drawer_layout`: single_bank vs twin_bank (加一个 drawer bank + N drawers). `caster`: braked_swivel_caster 额外加 4 revolute brake_lever。全部 forked_anchor 支撑 |
| └ multiplicity | 同构件 ×N | 有 | drawer_count N∈[2,8] (per bank)；见 §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | swivel_caster (REVOLUTE +Z + CONTINUOUS +X) / fixed_caster (FIXED + CONTINUOUS) / mixed (front swivel + rear fixed) / braked (REVOLUTE 三重). 所有 forked_anchor |
| ③ 主体形态家族 | 图&关节不变，换主体几何形态原型 | 有 | frame_form 4 candidate: open_tubular_cart / rounded_tower / rectangular_cabinet / slim_service_stand (form_subtype = Volumetric Envelope Form)。前 3 forked_anchor，最后 1 world_knowledge_extrapolation |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 (record_only) | 抽屉把手 (pull) 由 drawer_front 表面派生；对角抽屉标签 palette-dependent；braked_swivel 加 brake lever 手柄细节 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | cart_width [0.44,0.78]/cart_depth [0.36,0.60]/cart_height [0.60,0.95]. drawer PRISMATIC: axis (0,-1,0), open direction -Y, [0, drawer_travel]; motion_test_plan = sampled collision (`fail_if_parts_overlap_in_sampled_poses`) + targeted `ctx.pose({j0:upper})` 验证 -Y 位移；caster wheel CONTINUOUS 走完整圈；swivel REVOLUTE [0, swivel_range] targeted 半圈检查 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette（medical_white/industrial_gray/warm_oak_utility/safety_yellow/stainless_steel）覆盖 metal/plastic/painted/wood 材质大类 (≥3) |

## 采样与覆盖审计

总组合数：frame_form(4) × caster(4) × drawer_layout(2) × drawer_count(7 values 2-8) × palette(5) = **1120** unique slot tuples

seed_domain_policy: procedural_first

Procedural Sampling / Sweep Plan:
- Deterministic per-seed `random.Random(seed)` picks each slot independently then
  clamps `drawer_count ≤ 5` if `drawer_layout == twin_bank` (compatibility gate,
  keeps runtime under compile budget).
- Random sweep: 0-15 smoke → 0-35 final → corner 100-135 as `sweep-pipeline`
  default. Topology target: ≥300 distinct tuples on 1000-seed audit; 1120 space
  should hit >250 distinct with weighted sampling.
- No regression overrides.
- Controlled local scale: `cart_width`, `cart_depth`, `cart_height`,
  `drawer_travel_scale`, `swivel_range`, `brake_angle` — all clamped in
  `resolve_config`, none change slot choice or interface.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent draws per slot; twin_bank ⇒ N clamp | slot_choices_for_seed matches build |
| compatibility matrix | twin_bank ⇒ N ≤ 5; fixed_caster ⇒ swivel joint absent | no floating, closed-pose clear, no oversampled N |
| controlled local variation | linear scales clamped per §7 | proportions vary without breaking interfaces |
| regression overrides | none | — |
| random sweep | seeds 0-35 smoke; 0-135 corner | axis_realization; viewer for slot coverage |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 4 | yes | yes | ③ Primary Form Family registered |
| caster | 4 | yes | yes | |
| drawer_layout | 2 | yes | no | 唯一二选一 layout（源池实证仅两种） |
| drawer_count | 7 (2..8) | yes | yes | multiplicity |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed` returns realized module choice for each slot
- `config_from_seed` uses deterministic procedural sampling
- resolve_config gates twin_bank drawer count and derives interface geometry
- every non-FIXED joint has correct type/axis/range
- N drawers exist per bank; joint prismatic +(-1) along Y with valid pull-out travel
- all 4 caster wheels roll around (1,0,0), swivel casters swivel about (0,0,1)
- braked_swivel_caster adds 4 REVOLUTE brake levers
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples≤64, ignore_fixed=True)`
- targeted `ctx.pose({drawer0: upper})` shows drawer moves toward -Y
- targeted `ctx.pose({wheel0: π/2})` shows wheel rotates (roll semantics)
- targeted `ctx.pose({swivel0: swivel_range})` shows fork yaws (swivel semantics)
- `fail_if_articulation_origin_far_from_geometry(tol=0.020)`

## Reject cases

- drawer travel exceeds pedestal depth (drawer exits carcass through the rear)
- wheel intersects floor (axle_z + wheel_radius > caster_gap floor)
- carcass floor sits below wheel bottom (visible float)
- fixed_caster + REVOLUTE swivel joint (mis-typed slot)
- twin_bank N>5 (compile budget blow-up)
- drawer boxes overlap in extended pose (drawer_travel too large)

## 与相邻类别的边界

- 不该混入：`office_table_with_doors_or_drawers` — 有 worktop、无 casters、静置。
- 不该混入：warehouse platform cart — 无 drawer, 只有 bare deck。
- 不该混入：shopping cart / trolley — 无 drawer, 上开口 basket。
- 不该混入：filing cabinet / drawer_cabinet_with_sliding_drawers — 无 wheels。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | first pass; 4 frame forms + 4 caster mechanisms + 2 layouts + N∈[2,8] + 5 palettes → 1120 tuples, well over ≥300 target. |

## 模板实现备注

- Frame + drawer builder shared across `frame_form` (only geometry constants
  differ — envelope shape from same primitive family: Box carcass). Slot A really
  varies wall proportions + rounded/open flags, staying inside "Volumetric
  Envelope Form" family (Rule 3 preserved).
- Shared `_build_drawer` helper; `_build_caster_stack` dispatches on caster kind.
- `braked_swivel_caster` uses `ctx.allow_overlap(fork, brake_lever, ...)`
  captured-pin allowance.
- Wheel and swivel joints don't declare `MatingContract` (captured-pin geometry;
  see AUTHORING.md Rule 2 grandfather clause).

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | frame | rectangular_cabinet | rec_...var_drawer_count_3 | L166-L226 | body walls / floor / top cap |
| S2 | caster | braked_swivel_caster | rec_...var_caster_braked_swivel | L192-L472 | fork REVOLUTE + wheel CONTINUOUS + brake REVOLUTE |
| S3 | drawer | (all) | rec_...var_drawer_count_3 / _8 / _12 | L370-L410 | N drawer stack PRISMATIC -Y |
| S4 | layout | twin_bank | rec_...var_drawer_layout_twin_bank | L166-L250 | two parallel drawer banks |
| S5 | frame | open_tubular_cart | rec_...var_frame_open_tubular_cart | source map §origin storage_cart_006 | open frame envelope |
| S6 | frame | rounded_tower | rec_...var_frame_rounded_tower | source map §origin storage_cart_001 | closed rounded envelope |
