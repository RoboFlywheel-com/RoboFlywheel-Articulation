# Modular Spec - Industrial / Electric Saw

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Electric_Saw` |
| template path | `agent/templates/Industrial_Electric_Saw.py` |
| test path (optional) | `tests/agent/test_Industrial_Electric_Saw_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root body chassis + 3 parallel-children slots + 1 multiplicity axis) |
| function stem | `industrial_electric_saw` (exports `build_industrial_electric_saw`, `config_from_seed`, `run_industrial_electric_saw_tests`) |

`pattern = mixed`: a single pre-built root `body` (teal motor housing chassis) carries three
parallel-children slots (the moving cutter, the on/off control, and the workpiece mount), each of
which manually parents its own articulations to `body` (no serial chain joint). One multiplicity
axis rides on top: `tooth_count` (teeth on the circular saw blade). Every candidate creates at
least one non-FIXED joint, so a static-only model is never produced.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`). Each was
read in full; the origin was read line-by-line and every variant diffed against it to isolate its
structural axis:

- `rec_a-cordless-electric-circular-saw-with-a-teal-mot_20260708_091340_730591_88da991f` - ORIGIN 母本 (teal housing + toothed circular blade CONTINUOUS spin + retractable lower guard REVOLUTE + squeeze trigger REVOLUTE + safety lock PRISMATIC + flat handheld shoe).
- `rec_electric_saw_var_teeth_count_coarse` - multiplicity: blade `BLADE_TOOTH_COUNT=24` (coarse rip).
- `rec_electric_saw_var_teeth_count_fine` - multiplicity: blade tooth count 48 -> 60 (fine crosscut).
- `rec_electric_saw_var_cutoff_wheel` - ③ aperture form: toothed steel disc -> smooth toothless abrasive cut-off wheel (thicker disc, `_smooth_disc_profile`).
- `rec_electric_saw_var_chainsaw_bar` - ① skeleton: circular blade -> guide bar + traveling chain (36 cutter links + rail) on a CONTINUOUS chain drive; no lower guard.
- `rec_electric_saw_var_reciprocating_blade` - ①/② change: circular blade -> straight toothed reciprocating blade on a PRISMATIC stroke; no lower guard; small front foot shoe.
- `rec_electric_saw_var_paddle_switch` - ② joint type: squeeze trigger REVOLUTE -> sliding paddle switch PRISMATIC (axis Z).
- `rec_electric_saw_var_bevel_pivot` - ① skeleton (mount): fused flat shoe -> separate `shoe` part on a REVOLUTE bevel-tilt pivot (axis X).
- `rec_electric_saw_var_miter_arm` - READ, NOT ADOPTED: a stationary grounded `base` (plate + turntable + fence + hinge pillars) that would become the ROOT with the head on a pivoting arm. Under the shared body-as-root, blade-down canonical frame it requires reparent-inverting the hinge; a prototype did so but the grounded base + fence unavoidably penetrated the compact handheld housing (hinge barrel inside the top handle, fence into the lower guard). The compact body has no clean attachment point for a full ground base. Documented per source_index_policy; not made a distinct module.
- `rec_electric_saw_var_table_mount` - READ, NOT ADOPTED: fully re-oriented (blade points UP through a table, motor below), incompatible with the shared body-down canonical frame; its PRISMATIC rip-fence concept is structurally covered by other PRISMATIC joints (recip stroke, paddle). Documented per source_index_policy; not made a distinct module.

Both stationary-mount samples (miter_arm, table_mount) are read but NOT adopted for the same root cause: a grounded stationary base/table is geometrically incompatible with the compact handheld motor body reused as the single root. The mount slot ships 2 structurally distinct candidates (handheld_shoe / bevel_shoe); flagged for reviewer.

## 核心身份

A **handheld / bench electric power saw**: a compact teal motor `body` (housing shell + cross-motor
barrel + gearbox nose + rear cordless battery brick + rubber-overmolded top handle arch + front
grip knob) that drives one **cutting element** through a category-defining non-fixed joint - a
spinning toothed circular blade, a smooth abrasive cut-off wheel, a traveling chainsaw bar+chain,
or a straight reciprocating blade - controlled by an on/off **switch** (squeeze trigger or sliding
paddle, plus a safety lock-off button), and meeting the workpiece through a **mount** (a flat
stamped base shoe, a bevel-tilting shoe, or a stationary chop/miter base with a drop-cut hinge).
Default mature domain: ~0.33-0.42 m class one-hand/two-hand tool, 140 mm blade / 260 mm bar.

Not to be confused with the neighbouring subclasses **Industrial / Electric Saw vs. Drill press
table** (a fixed column drilling station, no rotating disc cutter) or a bare bench **grinder** (a
pedestal-mounted double wheel with no motor housing / trigger / shoe). The identity anchor is the
teal handheld motor body + trigger + a moving cutting element.

## 槽位 + 候选模块表

The root `body` chassis is pre-built (constant across all 10 samples - same teal housing) and is
NOT a diversity slot; the three diversity slots below all parent their joints directly to `body`
(parallel children, no auto chain joint). Each slot module may also add its own host visuals onto
`body` (Rule 4 conformal decoration: guards, brackets, guide bar) plus its own moving part(s).

### Slot A：cutting_element (parallel child of body · ③ Primary Form Family + ① skeleton + ② joint + multiplicity `tooth_count`)

The identity feature and the form-dominated ③ slot. Each candidate emits the defining non-fixed
cutter joint (parent=body). Disc candidates additionally emit the shared `upper_guard` host visual
+ `arbor_boss` + a retractable `lower_guard` REVOLUTE part.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `circular_blade` | forked_anchor (origin) | `rec_a-cordless-...88da991f` | L60-68, L108-149, L286-360 | eligible | toothed steel disc (`_blade_teeth_profile`, N teeth) CONTINUOUS `blade_spin` (axis Y) + `lower_guard` REVOLUTE retract; upper_guard host visual. `tooth_count` multiplicity. **Planar Boundary Form** (toothed disc silhouette) |
| `abrasive_wheel` | forked_anchor | `rec_electric_saw_var_cutoff_wheel` | L64-70, L83, L286-297 | eligible | smooth toothless abrasive disc (`_smooth_disc_profile`, thicker 0.003), CONTINUOUS `blade_spin` + `lower_guard`; upper_guard host visual. **Planar Boundary Form** (smooth disc silhouette; no teeth) |
| `chain_bar` | forked_anchor | `rec_electric_saw_var_chainsaw_bar` | L35-175, L217-271, L346-380 | eligible | ① skeleton: elongated `guide_bar` host visual + drive/nose sprockets, and a `chain` part = N cutter-link boxes on a bar-perimeter path + rail band, on a CONTINUOUS `chain_drive` (axis Y). No lower guard. **Macro Surface Construction** (bar+chain loop) |
| `reciprocating_blade` | forked_anchor | `rec_electric_saw_var_reciprocating_blade` | L37-100, L149-190, L264-299 | eligible | ①+② change: straight toothed `blade` (`_reciprocating_blade_profile`) + `blade_shank`, on a PRISMATIC `blade_stroke` (axis X, +/-stroke/2); `blade_clamp` host visual. No lower guard. **Planar Boundary Form** (straight blade silhouette) |

### Slot B：control (parallel child of body · ② joint type)

The on/off control + safety lock, present in every sample. Emits the primary switch part + joint
and the always-present `safety_lock` PRISMATIC button part + joint. Two structurally distinct
switch topologies exist in the pool (② joint-type axis).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `squeeze_trigger` | forked_anchor (origin) | `rec_a-cordless-...88da991f` | L239-251, L362-406 | eligible | `trigger` (boss + blade) on REVOLUTE `trigger_squeeze` (axis Y, 0..0.40) + `trigger_ear_*` host visuals; `safety_lock` cap on PRISMATIC `safety_lock_press` (axis -Y, 0..0.005). |
| `paddle_switch` | forked_anchor | `rec_electric_saw_var_paddle_switch` | L239-258, L362-399 | eligible | ② joint type: `paddle_slider` (+ grip ridge) on PRISMATIC `trigger_slide` (axis Z, 0..0.035) + `paddle_track`/`paddle_detent_*` host visuals; same `safety_lock` PRISMATIC button. |

### Slot C：mount (parallel child of body · ① skeleton, gated by cutter spine)

How the saw meets the workpiece. Disc saws (circular / abrasive) admit both mounts; the
handheld bare tools (chain / recip) are gated to `handheld_shoe` (a chainsaw / recip saw has no
base plate - handheld_shoe emits a spine-appropriate minimal foot). Degraded to 2 candidates: the
only other mount samples (miter_arm, table_mount) reparent/reorient the root and cannot host a
grounded base under the compact body-as-root frame (see reading summary); flagged for reviewer.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `handheld_shoe` | forked_anchor (origin + recip) | `rec_a-cordless-...88da991f` L158-203; `rec_electric_saw_var_reciprocating_blade` L166-190 | eligible (all spines) | spine-adaptive host visuals on `body`, NO new joint: disc -> full flat stamped shoe (rails + bridges + turned-up nose + depth/bevel brackets); recip -> small front foot (side plates + top plate); chain -> slim front hand-guard bar. Handheld tool. |
| `bevel_shoe` | forked_anchor | `rec_electric_saw_var_bevel_pivot` | L255-310 | eligible (disc only) | ① skeleton: full flat shoe as a separate `shoe` part on a REVOLUTE `bevel_pivot` (axis X at the front bevel bracket, 0..bevel_range, clearance-solved); depth/bevel brackets host visuals on body. The bevel shoe sits lower than the fused handheld shoe for roll clearance. |

硬约束满足：cutting_element=4, control=2, mount=2 candidates; every candidate has a
`forked_anchor` source + `model.py:Lx-Ly`. TWO justified degrades to 2: (a) control - the confirmed
pool contains exactly two switch topologies (REVOLUTE squeeze / PRISMATIC paddle); a 3rd would
require an unsourced ② joint type, forbidden. (b) mount - the only other mount samples
(miter_arm, table_mount) reparent/reorient the single root and cannot host a grounded base under
the compact body-as-root frame. No `world_knowledge_extrapolation` candidates.
The form-dominated ③ axis is registered in `slot_choices` via the `cutting_element` slot (>=3
recognisable form prototypes: toothed disc / smooth disc / straight blade / bar+chain loop).

## 槽位图（slot graph）

pattern: `mixed` (pre-built root + parallel children + 1 multiplicity)

```
body (root chassis; teal housing, pre-built, constant)
   |-[arbor (0.095,-0.078,0.070) · blade_spin CONTINUOUS(Y) | chain_drive CONTINUOUS(Y) | blade_stroke PRISMATIC(X); + lower_guard REVOLUTE(Y) for discs]-> cutting_element
   |-[handle strut · trigger_squeeze REVOLUTE(Y) | trigger_slide PRISMATIC(Z); + safety_lock_press PRISMATIC(-Y)]-> control
   `-[front bevel bracket (0.100,-0.020,0.020) · none (handheld) | bevel_pivot REVOLUTE(X)]-> mount
```

- **slot 顺序 / parent**：`body` is the pre-built root, the only reused parent. `cutting_element`,
  `control`, `mount` all set `parent=body` on their own joints (parallel children). Each declares
  ONLY a `downstream` interface (re-export body) and NO `upstream`, so the assembler emits no
  automatic chain joint (same idiom as Tipping_Barrow).
- **接口点位**：cutting_element -> arbor boss `(0.095,-0.078,0.070)` (disc/recip) or sprocket
  `(0.155,-0.055,0.068)` (chain); control -> handle front strut `(0.075,0,0.150)` + lock strut
  `(0.055,0.014,0.190)`; mount -> front bevel bracket `(0.100,-0.020,0.030)` (bevel) or rear hinge
  boss `(-0.02,0,0.205)` (miter).
- **跨 slot joint type/axis/range**：blade_spin/chain_drive CONTINUOUS(Y); blade_stroke
  PRISMATIC(X, +/-0.014); lower_guard REVOLUTE(Y, 0..1.8); trigger_squeeze REVOLUTE(Y, 0..0.40);
  trigger_slide PRISMATIC(Z, 0..0.035); safety_lock_press PRISMATIC(-Y, 0..0.005); bevel_pivot
  REVOLUTE(X, 0..bevel_range, clearance-solved).
- **互斥/派生**：`chain_bar` / `reciprocating_blade` force `mount=handheld_shoe` (bare handheld
  tools); disc cutters (circular/abrasive) may take any mount. `tooth_count` only for
  `circular_blade` (toothed); other cutters n/a.

## 每槽位 Module Emits / Interfaces

### Slot A / module circular_blade | abrasive_wheel | chain_bar | reciprocating_blade
| emits | 描述 | 来源 |
|---|---|---|
| host visuals (on body) | disc: `upper_guard`+`upper_guard_web`+`arbor_boss`+`gearbox_nose`+`lower_guard_pivot_boss`; chain: `gearbox_nose`+`clutch_cover`+`guide_bar`+`drive_sprocket`+`nose_sprocket`+`chain_catcher`+`oil_tank`; recip: `gearbox_nose`+`blade_clamp`+`clamp_collar` | origin L108-156,254-259; chain L217-271; recip L149-162 |
| parts | disc: `blade`+`lower_guard`; chain: `chain`; recip: `blade` | origin L286,328; chain L346; recip L264 |
| internal joints | `blade_spin` CONTINUOUS(Y) / `chain_drive` CONTINUOUS(Y) / `blade_stroke` PRISMATIC(X); disc also `lower_guard_retract` REVOLUTE(Y) | origin L317,351; chain L371; recip L286 |
| upstream interface | **none declared** (parallel-children; joints parent directly to `body`) | - |
| downstream interface | re-export body downstream (passthrough) | - |

### Slot B / module squeeze_trigger | paddle_switch
| emits | 描述 | 来源 |
|---|---|---|
| host visuals (on body) | squeeze: `trigger_ear_left/right`; paddle: `paddle_track`+`paddle_detent_top/bottom` | origin L239-251; paddle L239-258 |
| parts | `trigger` (squeeze boss+blade / paddle slider+ridge) + `safety_lock` | origin L363,389; paddle L363 |
| internal joints | `trigger_squeeze` REVOLUTE(Y) / `trigger_slide` PRISMATIC(Z); `safety_lock_press` PRISMATIC(-Y) | origin L377,397; paddle L389 |
| upstream interface | **none declared** | - |
| downstream interface | re-export body passthrough | - |

### Slot C / module handheld_shoe | bevel_shoe
| emits | 描述 | 来源 |
|---|---|---|
| host visuals (on body) | handheld: shoe rails/bridges/nose (or recip foot / chain guard) + depth/bevel brackets; bevel: depth/bevel brackets | origin L158-203; bevel L~255 |
| parts | handheld: none; bevel: `shoe` | bevel L~260 |
| internal joints | handheld: none; bevel: `bevel_pivot` REVOLUTE(X) | bevel L~300 |
| upstream interface | **none declared** | - |
| downstream interface | re-export body passthrough | - |

活动件语义：blade_spin/chain_drive 旋转刀具；blade_stroke 往复推拉直刃；lower_guard 收回护罩露刃；
trigger/paddle 触发开关；safety_lock 内压锁止；bevel_pivot 斜切倾斜底板。
不动细节（guards / brackets / guide bar / sprockets / fence / handle）写成宿主 body visual，非独立
part（Rule 1）。captured pivot / clamp / socket 用 element-scoped allow_overlap（Rule 2 例外）。
旋转关节原点落在 body 真实 boss 几何（origin honesty）；prismatic 原点为 gauge freedom 免检。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `cutting_element` | enum | circular_blade / abrasive_wheel / chain_bar / reciprocating_blade | circular_blade | choice | procedural sampler | Slot A |
| `control` | enum | squeeze_trigger / paddle_switch | squeeze_trigger | choice | procedural sampler | Slot B |
| `mount` | enum | handheld_shoe / bevel_shoe | handheld_shoe | conditional | disc -> handheld_shoe/bevel_shoe; chain/recip -> handheld_shoe (gate) | Slot C |
| `tooth_count` | int | {24,48,60} (obs: 24 coarse, 48 origin, 60 fine) | 48 | conditional | only for `circular_blade`; else n/a | teeth24 L40, teeth60 L289 |
| `body_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; overall tool scale (housing/blade/handle co-scale) | origin L38-45 |
| `blade_radius` | float | derived | - | equation | `= 0.076 · body_scale` | origin L38 |
| `bevel_range` | float | [0.45, 0.80] | 0.75 | conditional | bevel_shoe tilt upper (rad), further clamped by clearance solver (margin 0.002); else n/a | bevel L~305 |
| `chain_links` | int | derived | 36 | equation | `= round(bar_perimeter / link_pitch)`; not sampled | chain L52 |
| (—) | constraint | — | — | inequality | disc cutters clear the shoe slot; bevel joint range clamped by `clamp_joint_limits(keepout=["body"])` so the moving shoe never sweeps into the housing | origin L556-565 / clearance |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 18 s** (hang-guard `--compile-timeout 60`). Geometry is dominated by
a few extruded side-silhouette meshes (housing rounded-rect, disc teeth profile, guide-bar profile,
top-handle loop) plus N small chain-link boxes reusing ONE shared `Box` mesh. Tessellation tiers:
disc teeth profile <=60 tooth pairs (hero silhouette), guide-bar nose arc 17 seg, handle loop
default, tube splines (vent stub) <=8 samples/seg. All chain links share one `_chain_link_mesh()`;
both guards reuse their profile. No boolean sculpting. Expect 4-10 s/seed; drop tooth/arc seg first
if over.

## Multiplicity / Copy Logic

**一根 multiplicity 轴**（加权采样、编入 `slot_choices`、clamp、sweep 设上限）：

### 轴 1 - `tooth_count`（圆锯片齿数）
- `count_param`: `tooth_count`; `N_range` product `{24,48,60}`, test `{24,48,60}`; sampling domain
  加权：`{24: 0.3, 48: 0.4, 60: 0.3}`.
- copied object: the tooth pairs of the circular `blade_disc` profile (`_blade_teeth_profile(inner,
  outer, tooth_count)`), 2 polygon vertices per tooth. Not separate parts - a single extruded disc
  whose silhouette vertex count scales with N.
- naming: single `blade_disc` visual; N controls its profile resolution only. placement: revolved
  about the arbor. joint policy: one CONTINUOUS `blade_spin` regardless of N.
- source/gating: origin (48) L289, teeth_count_coarse (24) L40, teeth_count_fine (60) L289. Only
  `circular_blade`; `abrasive_wheel` (smooth), `chain_bar`, `reciprocating_blade` -> axis `n/a`.
- 数量变化不改主体形态/机制（仍是旋转圆盘）。

Chain-link count (`chain_links`) is DERIVED from bar perimeter / link pitch (not a sampled
multiplicity axis) to keep the compile budget and chain geometry stable; documented as equation.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | cutting_element 骨架：circular/abrasive disc（blade + lower_guard，2 动 part）/ chain_bar（chain 单动 part，无 lower_guard）/ reciprocating（straight blade 单动 part，PRISMATIC）；mount 骨架：handheld（0 新关节）/ bevel（+shoe REVOLUTE bevel_pivot）。全部 forked_anchor。 |
| └ multiplicity | 同构件 xN | 有 | 见 §8：tooth_count {24,48,60}（origin/teeth24/teeth60）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | control switch REVOLUTE（squeeze, origin）<-> PRISMATIC（paddle, paddle_switch）；cutter drive CONTINUOUS（disc/chain）<-> PRISMATIC（recip stroke）；mount REVOLUTE bevel(X) / REVOLUTE miter(Y)。全部 forked_anchor；每种在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 的 cutting_element slot**：toothed circular disc（origin, Planar Boundary Form）/ smooth abrasive disc（cutoff_wheel, Planar Boundary Form）/ straight toothed blade（reciprocating, Planar Boundary Form）/ guide-bar + chain loop（chainsaw, Macro Surface Construction）。>=3 可识别形态原型。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `brand_plate` 红色标牌、`battery_terminal_shroud`、`vent_stub` 线缆节、chain `oil_tank`/`chain_catcher`、fence/turntable 刻线、paddle 齿脊 detents - 均为宿主 body/base part visual，随 ③/⑤ 派生位置。source_type=record_only（origin/chain/miter/paddle）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：body_scale[0.90,1.15]（blade_radius/housing/handle co-scale）。关节运动包络（每个非-continuous joint）：lower_guard REVOLUTE Y，回收方向 +q，[闭合 0, 可行 1.8]；blade_stroke PRISMATIC X，[-0.014,+0.014]；trigger_squeeze REVOLUTE Y [0,0.40]；trigger_slide PRISMATIC Z [0,0.035]；safety_lock PRISMATIC -Y [0,0.005]；bevel_pivot REVOLUTE X [0, bevel_range<=0.80, clearance-solved]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；targeted `ctx.pose` - blade spin 转 0.8、lower_guard 收回 1.6、chain 转 1.2、recip stroke、trigger 触发、paddle 滑动、bevel 倾斜。continuous drive 采 {0,±90°,180°}。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/plastic/metal；配色 >=5 colorway：`teal_classic`（母本）、`safety_yellow`、`industrial_red`、`graphite_black`、`cobalt_blue`、`bare_metal`。材质大类覆盖 >= ceil(0.5x6)=3（painted housing + metal blade/shoe + plastic handle）。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 disc/smooth-disc/straight-blade/chain-bar 四种刀具、
squeeze/paddle 两种开关、handheld/bevel 两种底座、材质配色多样、所有关节全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- 按 spine 分：disc（circular×tooth3 + abrasive×1 = 4 cutter variants）× control 2 × mount 2 = 16；
  chain 1 × control 2 × mount 1 = 2；recip 1 × control 2 × mount 1 = 2。合计 **20**。

理由：28 < 富类别建议 300，因为真实结构词汇在此收敛——所有样本共享同一「teal 电机 body + 单刀具
关节 + 开关 + 底座」cell；离散槽只有三根 + 一根小 multiplicity，且 chain/recip 无底座变体，两个 stationary-mount 样本未采纳。不硬凑
组合空间（质量红线：不反推上游变体数量）。report-only，不设 gate。

理由：...

seed_domain_policy：`procedural_first`.

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次抽
cutting_element、control、mount，再按 compatibility gate 抽 tooth_count（circular 时）、palette、
连续 scale（body_scale/bevel_range/miter_range）。seed 0 pinned 到 origin 母本组合（circular_blade
×48 + squeeze_trigger + handheld_shoe, teal_classic）作为 documented regression anchor（sparse
override，其余 seed 全 procedural）。random sweep `0-15`（fast）-> `0-35`（final）-> corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 20（见上），低于 300 的
原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`body_scale`（blade_radius/housing/handle 由其 equation co-derive）、
`bevel_range`（conditional）、`miter_range`（conditional，另经 clearance solver clamp）。全部在
`resolve_config` clamp / 派生；不破坏 body 挂点接口、joint 原点、multiplicity。连续尺寸契约：先采
independent（body_scale）-> equation 派生 blade_radius -> conditional 解析 bevel_range/miter_range/
tooth_count。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 cutting->control->mount，均匀 choice；tooth_count 加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | chain/recip -> mount=handheld_shoe（gate）；tooth_count 仅 circular；disc×{handheld,bevel} 自由 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 3 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| cutting_element | 4 | yes | yes | circular/abrasive/chain/recip |
| control | 2 | yes | no | squeeze/paddle（pool 只有两种开关拓扑，justified degrade） |
| mount | 2 | yes | no | handheld/bevel（justified degrade：其余 mount 样本 miter/table 需 reparent/reorient root，本 body-as-root 框架无法承载接地底座） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ tooth_count axis)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (chain/recip -> handheld_shoe; tooth_count only circular) in `resolve_config`
- controlled local scales clamped; cannot break body mount points, joint origin honesty, or multiplicity
- cross-part scale dependencies (blade_radius) derived in `resolve_config`
- captured pivot / clamp / guard overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: blade_spin/chain_drive CONTINUOUS(Y); blade_stroke PRISMATIC(X); trigger REVOLUTE(Y) or PRISMATIC(Z); safety_lock PRISMATIC; bevel_pivot REVOLUTE(X)
- copied blade teeth follow `_blade_teeth_profile` naming + count policy
- `run_industrial_electric_saw_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Disc/guard steered pose collides with the housing at joint min/max -> shrink range or move mount; guard overlaps are element-scoped only.
- Bevel shoe tilted past range clips the protruding blade or housing -> clamp `bevel_range` (clearance solver), element-scoped allow_overlap on bracket<->shoe only.
- chain links float off the bar (path offset wrong) or bury into the guide bar -> keep `CHAIN_RADIAL_OFFSET`, element-scoped allow_overlap chain<->guide_bar only.
- Downgrading `_blade_teeth_profile` / `_reciprocating_blade_profile` / guide-bar `ExtrudeGeometry` / top-handle `ExtrudeWithHolesGeometry` to crude Box/Cylinder (Rule 3 violation).
- Emitting a static-only tool (no non-fixed joint) - every cutter candidate carries a CONTINUOUS/PRISMATIC drive.
- Body chassis + trigger present but no moving cutter, or a table-saw blade-up reorientation mixing frames.

## 与相邻类别的边界

- 不该混入：**Industrial / Drill press table**（固定立柱钻床工作台，无旋转圆盘刀具/扳机/护罩）。
- 不该混入：**Industrial / bench grinder**（座式双砂轮，无电机手柄壳/扳机/底板）。
- 不该混入：**table saw / miter saw 的接地整机改造**（table_mount blade 朝上穿桌面、miter_arm 接地底座+落切臂；二者的接地/倒装世界系与本模板 body-down 单根框架冲突，见未采纳说明）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | (1) control slot degraded to 2 candidates (pool has exactly two switch topologies REVOLUTE squeeze / PRISMATIC paddle; a 3rd ② type would be unsourced). (2) mount slot degraded to 2 candidates (handheld_shoe / bevel_shoe): the two stationary-mount samples `miter_arm` and `table_mount` are read but NOT adopted - both reparent/reorient the single root and a grounded base/table geometrically penetrates the compact handheld body-as-root (a reparent-inverted miter prototype failed the sweep on base-into-housing/lower-guard 穿模). Both degrades are honest source-pool limits, not threshold dilution. Flagged for human reconciliation. |

## 模板实现备注（可选）

- body 是 pre-built root chassis（在 `build_` 里先造），三 slot 全 parallel-children（只声明 downstream 再导出 body，无 upstream -> 无自动 chain joint），同 Tipping_Barrow 惯用。
- 共享几何 helper：`_side_extrusion`（XZ 侧影 Y 挤出）、`_side_loop`（带孔挤出，top_handle）、`_blade_teeth_profile` / `_smooth_disc_profile` / `_reciprocating_blade_profile` / `_guide_bar_profile` / `_chain_path_points`，全部改自样本，保留 primitive 家族（Rule 3）。
- captured pivot/guard/clamp overlaps -> element-scoped `allow_overlap`；圆锯的 guard/blade 大量 intentional-fit overlap 需按 origin L426-551 全量移植。
- bevel_pivot / arm_hinge 用 `clamp_joint_limits(keepout=["body"], allowed_pairs=...)` solve 安全行程，替代手调角度。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | circular_blade + squeeze_trigger + handheld_shoe + body chassis | `rec_a-cordless-...88da991f` (origin 母本) | L60-634 | body 通用壳, 圆锯片 part + CONTINUOUS spin + lower_guard REVOLUTE, squeeze trigger REVOLUTE + safety_lock PRISMATIC, 平底 shoe, 全部 allow_overlap + test 语义 |
| S2 | A mult | tooth_count=24 | `rec_electric_saw_var_teeth_count_coarse` | L40, L291 | tooth_count 下界 |
| S3 | A mult | tooth_count=60 | `rec_electric_saw_var_teeth_count_fine` | L289 | tooth_count 上界 |
| S4 | A ③ | abrasive_wheel | `rec_electric_saw_var_cutoff_wheel` | L64-70, L83, L286-297 | 光滑砂轮盘（Planar Boundary Form, 无齿） |
| S5 | A ① | chain_bar | `rec_electric_saw_var_chainsaw_bar` | L35-175, L217-271, L346-380 | 导板 + 链条 CONTINUOUS drive |
| S6 | A ①② | reciprocating_blade | `rec_electric_saw_var_reciprocating_blade` | L37-100, L149-190, L264-299 | 直刃往复 PRISMATIC stroke |
| S7 | B ② | paddle_switch | `rec_electric_saw_var_paddle_switch` | L239-258, L362-399 | 滑动拨板开关 PRISMATIC |
| S8 | C ① | bevel_shoe | `rec_electric_saw_var_bevel_pivot` | L255-310 | 斜切倾斜底板 REVOLUTE(X) |
| (n/a) | - | NOT ADOPTED | `rec_electric_saw_var_miter_arm` / `rec_electric_saw_var_table_mount` | - | 接地底座/倒装桌面与 body-as-root 框架冲突（见 reading summary + reviewer notes） |
