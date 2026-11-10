# Modular Spec — telescoping_fishing_rod

## 元信息
| 项 | 值 |
|---|---|
| slug | `telescoping_fishing_rod` |
| template path | `agent/templates/telescoping_fishing_rod.py` |
| test path (optional) | `tests/agent/test_telescoping_fishing_rod_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear telescoping prismatic chain + parallel reel rotary children off a common handle) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 (2 origin anchors + 10 forked variants) |
| read_count | 12 |
| read_scope | all 5-star samples in this category (both origins fully; every fork diffed against its parent) |
| source_index_policy | only adopted module sources are indexed below |

Reading summary (what is invariant vs. what varies):
- **Invariant skeleton.** Every sample is a rear grounded **handle/grip carrying a reel seat**, a **fixed outer blank tube**, then a **serial chain of concentric telescoping section tubes** each joined to its parent by a **PRISMATIC joint along the rod axis** (`MotionLimits(lower=0, upper>0.05)`), plus a **reel** whose body is a fixed load path off the handle with **rotary moving children** (spool REVOLUTE, crank REVOLUTE, bail/thumb REVOLUTE). Line **guides** ride the top of the blank + each section.
- **Hero geometry.** Tube sections are hollow open-bore **`LatheGeometry.from_shell_profiles`** (001) / cadquery annular tubes (002) — NOT solid cylinders. Guides are **`TorusGeometry`** rings (001) or bent **`tube_from_spline_points`** wire (002). Reel stems/cranks/bails are spline tubes; reel bodies are `CapsuleGeometry`/`LatheGeometry`/`Sphere`. These primitive families must be preserved (Rule 3).
- **Nesting is captured/declared.** Both origins `allow_overlap` the concentric nested tubes (parent shell ↔ child shell / rear bushing) and the reel captures (spool-in-rotor, crank-in-boss, bail-on-pivot) — telescoping tubes and reel pivots are captured geometry (grandfathered, no MatingContract).
- **What varies across forks:** reel TYPE (spinning capsule / baitcasting bridge-frame / spincast closed dome), reel SEAT (fixed hood / sliding rings / screw-lock hood), guide TOPOLOGY (torus wire eye / bent wire / roller-tip sheave), and telescoping SECTION COUNT (3/5/7/9).

## 核心身份
A telescoping fishing rod: a hand rod whose blank is a stack of concentric tapered tubes that slide (PRISMATIC) out of one another to extend and back in to collapse for carry, carrying line guides along the top of the blank, a rear grip + reel seat, and a mounted fishing reel (spinning / baitcasting / spincast) with a spinning spool, a turning crank handle, and (spinning/baitcasting) a bail or thumb bar. Default mature domain = a compact/assembled rod with the reel mounted below the axis and guides above.

不该混入：a fixed (non-telescoping) one-piece fishing pole — this category REQUIRES ≥3 prismatic telescoping stages. A telescoping pointer / antenna / selfie stick — those have no reel, no line guides, no fishing grip.

## 槽位 + 候选模块表

### Slot A：reel_type  (③ Primary Form Family + ② joint mix + ① part count)
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| spinning_reel | forked_anchor | origin 001 `rec_picturex_..._001...` | L281-411, L346-433, L553-585 | eligible if compatible | Volumetric Envelope Form: capsule/graphite body hung below axis; rotor nose; spool (REVOLUTE +X) + crank (REVOLUTE) + bail wire (REVOLUTE) — 3 moving parts |
| baitcasting_reel | forked_anchor | `rec_0611_telescoping_fishing_rod_var_reel_type_baitcasting_reel` | L160-281 | eligible if compatible | Macro Surface Construction: low-profile bridge frame w/ round side plates + levelwind rail; transverse exposed spool (REVOLUTE +Y) + crank w/ drag star (REVOLUTE +Y) + thumb bar (REVOLUTE +Y) — 3 moving parts |
| spincast_reel | forked_anchor | `rec_0611_telescoping_fishing_rod_var_reel_type_spincast_reel` | L282-311 | eligible if compatible | Volumetric Envelope Form: closed-face lathed dome shell + cover cap enclosing spool (REVOLUTE +X) + crank (REVOLUTE +Y); NO bail (closed face) — 2 moving parts |

### Slot B：reel_seat  (② mechanism / ④ host-conformal decoration)
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_hood_seat | forked_anchor | origin 001 / 002 | 001 L217-234 / 002 L185-196 | eligible if compatible | continuous barrel + fixed & front locking hoods + locking nut; non-moving handle visuals |
| sliding_ring_seat | forked_anchor | `rec_0611_..._reel_seat_sliding_ring_seat` | L185-200 | eligible if compatible | slim exposed core + two close-fitting anodized sliding retaining rings + trim ring |
| screw_lock_seat | forked_anchor | `rec_0611_..._reel_seat_screw_lock_seat` | L185-215 | eligible if compatible | continuous barrel + slotted fixed/sliding hoods + fine thread crests + knurled locking nut |

### Slot C：guide_topology  (④ surface hardware / ① guide construction)
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wire_ring_guides | forked_anchor | origin 001 | L62-99, L154-162 | eligible if compatible | `TorusGeometry` ring + tapered box foot brazed to blank top; 1 per section |
| bent_wire_guides | forked_anchor | origin 002 | L74-150 | eligible if compatible | single continuous bent `tube_from_spline_points` wire eye + seat foot; 1 per section |
| roller_tip_guides | forked_anchor | `rec_0611_..._guide_topology_roller_tip_guide` | L62-160 | eligible if compatible | plain wire eyes on mid sections + a grooved roller sheave (cylinder+torus) on a transverse axle w/ yoke at the tip |

Every candidate is structurally distinct (different part/primitive/joint content), each grounded in a real `model.py:Lx-Ly`. No single-candidate slot. Slot A is the registered ③ Primary Form Family slot (≥3 recognizable reel form prototypes across the three form_subtypes).

## 槽位图（slot graph）

pattern: mixed

```
handle(root, grounded; grip + reel_seat[Slot B] + fixed outer blank + reel_body[Slot A form])
  |
  +--[FIXED implied — outer blank is folded into handle visuals]
  |
  +--[PRISMATIC +X @ blank front, MotionLimits(0..travel_1)]--> section_1
  |         (rear bushing rides parent bore; concentric captured overlap declared)
  |            +--[PRISMATIC +X]--> section_2 --[PRISMATIC +X]--> ... --> section_N   (N = stage_count)
  |               each section carries a guide[Slot C]; last section carries tip cap + tip guide
  |
  +--[REVOLUTE @ reel]--> spool         (captured in reel rotor/dome)
  +--[REVOLUTE @ reel]--> crank         (captured in reel side boss)
  +--[REVOLUTE @ reel]--> bail/thumb    (spinning & baitcasting only; spincast omits — closed face)
```

Interfaces:
- handle→section_1 and section_i→section_{i+1}: concentric bore/rear-bushing slide interface; PRISMATIC axis = rod axis (+X); range `[0, travel_i]`; nested overlap declared element-scoped allow_overlap (captured concentric tubes, no MatingContract).
- handle→spool/crank/bail: reel rotor / side boss / pivot bar captured pivots; REVOLUTE; captured overlap declared element-scoped (no MatingContract).
- Slot B (reel_seat) and reel_body (Slot A) geometry are non-moving handle visuals (Rule 1), sitting on the reel-seat region of the grip.
- Guides (Slot C) are non-moving visuals folded into the blank / each section (Rule 1), derived from that tube's local top surface radius (Rule 4).

## 每槽位 Module Emits / Interfaces

### handle (fixed skeleton, all forks)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle` (rear grip, butt cap, reel seat[Slot B], foregrip, outer blank tube, guide 0, reel body[Slot A]) | 001 L192-345 / 002 L176-216 |
| internal joints | none (single root part) | — |
| upstream interface | root / grounded | 001 L192 |
| downstream interface | blank front face (x=blank_front, +X) → section_1 prismatic; reel rotor/boss/pivot faces → reel revolutes | 001 L502-585 |

### section_i (×N, multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `section_i` (hollow tapered lathe tube shell + trim collar/ferrule + rear bushing + guide[Slot C]; last adds tip cap) | 001 L102-163 / 002 L229-263 |
| internal joints | PRISMATIC parent→section_i, axis +X, `MotionLimits(0..travel_i)` | 001 L509-552 / 002 L266-280 |
| upstream interface | rear bushing rides parent bore (captured overlap) | 002 L253-263 |
| downstream interface | own bore front → next section prismatic | 001 L525-548 |

### reel moving parts (Slot A)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spool`, `crank`, `bail` (bail omitted for spincast) | 001 L346-433 |
| internal joints | REVOLUTE handle→spool / handle→crank / handle→bail | 001 L553-585 / 002 L371-419 |
| upstream interface | captured pivots (rotor bar / side boss / pivot bar) | 001 L708-738 |
| downstream interface | none (leaf parts) | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| reel_type | enum | spinning_reel / baitcasting_reel / spincast_reel | spinning_reel | choice | procedural sampler | Slot A |
| reel_seat | enum | fixed_hood_seat / sliding_ring_seat / screw_lock_seat | fixed_hood_seat | choice | procedural sampler | Slot B |
| guide_topology | enum | wire_ring_guides / bent_wire_guides / roller_tip_guides | wire_ring_guides | choice | procedural sampler | Slot C |
| stage_count | int (multiplicity) | [3, 8] product; test biased small | 4 | conditional | # telescoping section parts; per-section radii derived | 001/002 + 3/5/7/9 forks |
| palette_style | enum | 6 colorways (see §8.5 ⑥) | carbon_graphite | choice | procedural sampler | 001/002/spincast materials |
| rod_len_scale | float | [0.88, 1.15] | 1.0 | independent | uniform, clamp; scales all section lengths + travels | 001 L435-494 |
| taper_shrink | float | [0.76, 0.84] | 0.80 | independent | per-stage outer-radius multiplicative shrink | 001 radii L435-494 |
| travel_scale | float | [0.85, 1.15] | 1.0 | independent | scales prismatic upper limits | 001 L509-552 |
| reel_scale | float | [0.90, 1.12] | 1.0 | independent | scales reel body + moving parts | 001 L307-433 |
| (—) | constraint | — | — | inequality | `outer_radius_{i+1} = taper_shrink·outer_radius_i` and `bore_i = 0.82·outer_radius_i` ⇒ child outer < parent bore; wall floored at 0.0005; retained insertion ≥ 0.03·L guarantees overlap at full extension | interface / clearance |

连续尺寸采样契约：先采 independent 主尺度（rod_len_scale, taper_shrink, travel_scale, reel_scale）→ 派生每级半径/长度/行程 → 用 inequality 保证 child outer < parent bore 且 retained-insertion 恒 >0（回缩 travel 上限）。stage_count 的 conditional 半径链在 resolve_config 内解析（尾段半径 floored）。

### 7.5 编译预算 / compile budget
Self-reported budget: **≤15 s/seed** (typical ~8-12 s). Cost drivers: (1+N) lathe tube shells (`from_shell_profiles`, segments=36) + N guides (torus radial=14/tubular=28 or spline wire) + 1 reel (capsule/lathe/spline). Tessellation buckets: tube segments ≤36; guide torus ≤28 tubular; reel capsule ≤24 segments; reuse a single shell helper for every section. N capped at 8 (product) keeps the tube count bounded. Sweep `--compile-timeout 120` (watchdog ≈ 8×budget). If any seed >15 s, drop tube `segments` first.

## Multiplicity / Copy Logic
本类别有 **1 根 multiplicity 轴：`stage_count`**（telescoping 段数）。

- `count_param` = `stage_count`; `N_range` 产品域 `[3, 8]`（源样本 3/5/7/9 支持；≥9 尾段半径亚毫米、易穿模，故产品上限 8；测试偏小 3-6）。sampling domain 权重档：小 N 高频（3-5），大 N 稀有（6-8）。
- copied object：`section_i` 隐构 tube（shared `_tube_section` helper）；naming `section_{i}`；placement：沿 +X 串行嵌套，joint origin 在上一段 bore front；joint policy：每段一个 PRISMATIC(+X) 关节，range 派生自该段长度与保留插入量；source/gating：N≥3 强制（telescoping 身份）。
- 其余结构由固定 named parts（handle + reel 三活动件）表达，不做模板级循环复制。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | telescoping 段数 N（multiplicity，见 §8）改变 prismatic 关节数；reel_type 改变 reel 活动件数（spincast 无 bail = 少一个 REVOLUTE）。forked_anchor: 3/5/7/9 forks + spincast fork |
| └ multiplicity | 同构件 ×N | 有 | `stage_count` N∈[3,8]，权重小 N 高频；见 §8 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | telescoping = PRISMATIC(+X)；reel = REVOLUTE(spool +X 或 +Y、crank +Y、bail +X/+Y)。spinning spool +X vs baitcasting spool +Y = 轴变。全部 source-backed；每种都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 可识别形态原型 | 有 | **Slot A reel_type = ③ 主体形态家族 slot（登记进 slot_choices）**：spinning_reel=Volumetric Envelope Form（capsule 体）; baitcasting_reel=Macro Surface Construction（桥架侧板+levelwind）; spincast_reel=Volumetric Envelope Form（闭面穹顶壳）。3 个可识别原型，全 forked_anchor |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | Slot C guide_topology（torus 环 / 弯线眼 / 滚轮尖）+ Slot B reel_seat（固定罩/滑环/螺纹锁）。装饰几何由宿主 tube/grip 表面逐-tube 半径派生（guide foot 坐落 blank_radius(z) 顶面）、随 ③/⑤ 共形。record_only + forked_anchor |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | rod_len_scale[0.88,1.15]、taper_shrink[0.76,0.84]、travel_scale[0.85,1.15]、reel_scale[0.90,1.12]（见 §7）。运动包络：每 telescoping 关节 PRISMATIC +X `[0, travel_i]`（开启方向 = 向 rod tip 延伸，全程保留插入 ≥0.03·L 不脱出/不穿模）；spool/crank REVOLUTE 整程、bail REVOLUTE `[-0.18, 1.35]`。motion_test_plan：跑 sampled collision（cap 32）；targeted `ctx.pose`：全段 prismatic→upper 验证 tip 前移且仍插入、spool 转动 aabb 变、crank knob 位移、bail 包络变 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal(steel/anodized)+plastic/foam(EVA grip)+carbon(blank)+painted(reel enamel)。配色 6：carbon_graphite(001)、black_gold(002)、spincast_red(fork)、cobalt_blue、olive_bronze、ice_silver。材质大类覆盖 ≥ ceil(0.5×6)=3 ✓ |

收尾自检：`template batch` 0-9 seed 需肉眼见 reel 三形态拉得开、guide 三拓扑不同、材质大类都出现、guide 贴合 blank 顶面不悬空、telescoping 全程不穿模不脱出。

## 采样与覆盖审计

总组合数（拓扑元组）：reel_type(3) × reel_seat(3) × guide_topology(3) × stage_count(6: 3..8) = 162 topology tuples × palette(6) = 972 seed-distinct configs（连续 scale 另计）。

理由：162 拓扑元组 <300 富类别建议线，但受源锚点数上限约束（2 origins + 10 forks），已覆盖所有声明的离散结构；乘 6 palette 与 4 连续 scale 后 seed 空间充分。该指标 report-only。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 全程 deterministic 采样，seed=0 不特殊；无 curated/modulo 主表）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 enum(weighted) + stage_count(weighted small) + palette + 4 clamp scales | slot_choices_for_seed == build choices |
| compatibility matrix | 全 slot 正交可自由组合；无非法组合（reel/seat/guide/N 相互独立）；spincast 无 bail 由 reel_type 分支处理 | no floating / collision / axis / bulky-module failures |
| controlled local variation | rod_len_scale, taper_shrink, travel_scale, reel_scale（§7 clamp/derived） | 比例变化不破坏 bore<parent、retained insertion、joint origin、identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass；0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| reel_type | 3 | yes | yes | ③ Primary Form Family slot |
| reel_seat | 3 | yes | yes | |
| guide_topology | 3 | yes | yes | |
| stage_count (mult) | 6 (N 3..8) | yes | yes | multiplicity axis |

## Validator
- slot_choices_for_seed returns implemented module names (reel_type, reel_seat, guide_topology, stage_count)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds incl. seed 0
- per-section radii chain resolved in resolve_config (child outer < parent bore; wall & tip floored); retained insertion clamps travel upper so no stage un-nests
- critical captured overlaps declared element-scoped (concentric tubes, reel pivots); telescoping/reel joints omit MatingContract (grandfathered)
- key joints: N PRISMATIC(+X, lower=0, upper>0.05); reel REVOLUTE (spool/crank always, bail spinning+baitcasting)
- copied section objects follow `section_{i}` naming + serial +X nesting
- tube shells stay `LatheGeometry.from_shell_profiles`; guides stay Torus/spline; reel bodies stay capsule/lathe/sphere (no downgrade to Box/Cylinder)

## Reject cases
- A one-piece (non-telescoping) rod with <3 prismatic stages → not this category.
- Solid-cylinder "tubes" (downgraded lathe shell) → Rule 3 violation.
- A telescoping section that fully un-nests (retained insertion ≤0) at joint upper → collapse/detach pose.
- Guides built at a constant radius floating off the tapered blank top → Rule 4 violation.
- Reel body spawned as a FIXED tiny-disk part instead of folded handle visuals → Rule 1/2 violation.
- Missing reel spool/crank rotary joints, or bail present on spincast (closed face) → wrong reel semantics.
- Nested-tube or reel-pivot overlap left undeclared → closed/sampled-pose overlap failure.

## 与相邻类别的边界
- 不该混入：fixed one-piece fishing pole（无 telescoping prismatic 段，缺本类核心运动）。
- 不该混入：telescoping pointer / antenna / selfie stick（无 reel、无 line guides、无 fishing 手柄）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 2 origins + 10 forks; Slot A registered as ③ Primary Form Family slot; stage_count multiplicity N∈[3,8]. |

## 模板实现备注
- 单一 `_tube_section` helper（`LatheGeometry.from_shell_profiles`）供 outer blank + 全部 section 复用。
- 所有 telescoping + reel 关节为 captured 几何：omit MatingContract，改声明 element-scoped `allow_overlap`（concentric tube shells 逐对 + handle↔section_1 + reel rotor/boss/pivot 捕获）。
- guide/seat/reel_body 非活动 → 一律 handle/section parent visual（Rule 1）。
- 全局连续 scale 在 resolve_config 内 clamp/派生；尾段半径 & 壁厚 floored 以防亚毫米穿模。
</content>
</invoke>
