# Modular Spec -- Industrial / Ore crusher (jaw)

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Ore_crusher_jaw` |
| template path | `agent/templates/Industrial_Ore_crusher_jaw.py` |
| test path (optional) | `tests/agent/test_Industrial_Ore_crusher_jaw_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root frame + parallel-children drive + parallel-children crush mechanism + 3 multiplicity axes) |
| function stem | `industrial_ore_crusher_jaw` (exports `build_industrial_ore_crusher_jaw`, `config_from_seed`, `run_industrial_ore_crusher_jaw_tests`) |

`pattern = mixed`: a single root `frame` part carries two parallel-children
slots -- the `drive` (eccentric shaft + flywheel + belt pulleys) and the
`crush` mechanism (swing jaw + back linkage) -- each of which manually parents
its own articulations to the frame (no serial chain joint). Three multiplicity
axes ride on top: `cross_member_count` (base cross members), `flywheel_spoke_count`
(spoked flywheel), and `jaw_rib_count` (corrugation teeth on both jaw plates).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_gray-steel-single-toggle-jaw-crusher-with-an-ora_...bcb3073f` -- ORIGIN 母本 (welded steel frame, tilted fixed jaw plate FIXED, swing pitman-jaw on REVOLUTE hung from eccentric shaft, spoked flywheel on CONTINUOUS shaft, single rear toggle plate REVOLUTE mimic, side motor + belt pulley CONTINUOUS mimic).
- `rec_ore_crusher_var_base_crossmember_count` -- multiplicity: base `CROSS_MEMBER_COUNT` 2 -> 4 (evenly spaced transverse members).
- `rec_ore_crusher_var_cast_monobloc_frame` -- ③ frame form: 4 welded flat plates -> single cast monobloc housing (thick volumetric walls, integral bearing bosses).
- `rec_ore_crusher_var_dodge_pivot` -- ① skeleton: swing jaw pivot moves top-hung (Blake) -> bottom pivot (Dodge), driven at the top by the eccentric; adds a `jaw_pivot_mount` frame boss.
- `rec_ore_crusher_var_double_toggle` -- ① skeleton: single-toggle -> Blake double-toggle; adds a separate `pitman` member riding the eccentric + two toggle plates (front to jaw, rear to frame) + top `pivot_bosses`.
- `rec_ore_crusher_var_fixed_jaw_setting_ram` -- ② joint: fixed jaw plate FIXED -> PRISMATIC wear/setting adjustment along the front-wall normal + hydraulic `adjustment_wedge` carriage.
- `rec_ore_crusher_var_flywheel_spoke_count` -- multiplicity: `FLYWHEEL_SPOKE_COUNT` 6 -> 8.
- `rec_ore_crusher_var_hydraulic_toggle` -- ② joint: rear toggle plate REVOLUTE mimic -> PRISMATIC hydraulic tramp-relief cylinder (axis +X in jaw frame).
- `rec_ore_crusher_var_jaw_rib_count` -- multiplicity / ④: corrugation `RIB_COUNT` 9 -> 5 (coarse teeth) shared by both crushing plates.
- `rec_ore_crusher_var_solid_disc_flywheel` -- ③ form: spoked flywheel -> solid cast disc (full web + rim ring + hub boss, no spokes).

## 核心身份

A **single-eccentric jaw rock crusher (welded/cast steel machine on a ground
base)**: a heavy grounded `frame` (welded flat side plates + front/rear walls,
or a cast monobloc housing) that holds, between a tilted **fixed jaw plate** and
a swinging **movable jaw plate**, a wedge-shaped crushing chamber. An
**eccentric shaft** spinning a heavy **flywheel** (and a V-belt drive pulley fed
by a side motor pulley) drives the swing jaw through a short crushing stroke; a
**toggle back-linkage** (mechanical toggle plate, hydraulic cylinder, or a
double-toggle pitman pair) closes the kinematic loop from the swing jaw to the
frame seat. Both jaw plates carry orange corrugation teeth. At least two real
non-fixed joints are always present (the CONTINUOUS eccentric-shaft spin and the
REVOLUTE crushing stroke). Default mature domain: a ~2 m lab/pilot single-toggle
jaw crusher, feed at the top, discharge gap at the bottom.

Not to be confused with the neighbouring picture subclass **Industrial / Ore
crusher (other types)** (a cone/gyratory or roll crusher -- a spinning mantle or
counter-rotating rolls, no swinging jaw + toggle + flywheel eccentric spine),
nor with a generic **welded steel workbench / press frame** (no crushing jaws,
no eccentric flywheel drive).

## 槽位 + 候选模块表

### Slot A：frame (root · ③ Primary Form Family + multiplicity `cross_member_count` + ② `fixed_jaw_mode`)

The grounded root machine body. Same functional part tree across candidates:
one grounded `frame` part carrying base rails + N cross members + side walls +
tilted front wall + rear wall + toggle seat + rod bracket + bearing housings +
motor pedestal + motor. Both candidates expose the identical inner mounting
envelope (`SIDE_INNER` half-width, `SHAFT_X/SHAFT_Z` bearing point, front-wall
plane) so the drive and crush slots are frame-form independent. The fixed jaw
plate is emitted here: `welded` mode = a frame `visual` (non-moving, Rule 1);
`adjustable` mode = a separate PRISMATIC `fixed_jaw_plate` part on a wear-setting
ram (source: fixed_jaw_setting_ram).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `welded_plate_frame` | forked_anchor (origin) | `rec_gray-steel-...bcb3073f` | L106-L189, L355-L405 | eligible | two ExtrudeGeometry flat side plates + Box front/rear walls + base rails + cross members + bearing housings + motor. **Macro Surface Construction** (welded flat-plate assembly) |
| `cast_monobloc_frame` | forked_anchor | `rec_ore_crusher_var_cast_monobloc_frame` | L54-L206, L424 | eligible | single thick-walled cast housing (extruded volumetric side walls `CAST_WALL`=0.10 + integral bottom/front/rear walls + raised bearing bosses) replacing the four flat plates. Adapted to `ExtrudeGeometry` thick walls (no cadquery, compile-budget). **Volumetric Envelope Form** (cast monobloc) |

### Slot B：drive (parallel child on frame · ③ flywheel form + ② CONTINUOUS + multiplicity `flywheel_spoke_count`)

The eccentric-shaft spin drive. Same part tree across candidates: one
`eccentric_shaft` part (CONTINUOUS about +Y at the bearing point) carrying the
shaft journal + eccentric boss + flywheel + V-belt drive pulley, plus a
`motor_pulley` part (CONTINUOUS mimic, belt-plane aligned with the drive pulley).
Only the flywheel's ③ form prototype changes. All shaft visuals are rotationally
compact about the spin axis (outboard flywheel/pulley) so continuous rotation
never sweeps into the frame.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `spoked_flywheel` | forked_anchor (origin) | `rec_gray-steel-...bcb3073f` L281-L298; `rec_ore_crusher_var_flywheel_spoke_count` L79, L293-L296 | L281-L310, L456-L486 | eligible | LatheGeometry rim ring + N radial `BoxGeometry` spokes + central hub cylinder. flywheel_spoke_count multiplicity. **Macro Surface Construction** (open spoked wheel) |
| `solid_disc_flywheel` | forked_anchor | `rec_ore_crusher_var_solid_disc_flywheel` | L282-L304 | eligible | full CylinderGeometry web disc + LatheGeometry rim ring + hub boss + chamfer rings; no spokes. No spoke_count. **Volumetric Envelope Form** (solid cast disc) |

### Slot C：crush (parallel child on frame · ① skeleton + ② joint + multiplicity `jaw_rib_count`)

The identity mechanism. Same functional role across candidates: a `swing_jaw`
part (REVOLUTE crushing stroke, carrying the orange movable jaw plate + tension
rod), plus a back-linkage that closes the loop to the frame. Candidates change
the kinematic skeleton (pivot location, extra pitman member) and the back-link
joint type. The eccentric-shaft spin (Slot B) and the crushing stroke are the
two always-present non-fixed joints; the back-linkage parts follow the stroke as
REVOLUTE/PRISMATIC mimics so there is exactly one crushing DOF plus one spin DOF.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_toggle` | forked_anchor (origin) | `rec_gray-steel-...bcb3073f` | L205-L248, L423-L504 | eligible | Blake single-toggle, top-hung pitman-jaw: `swing_jaw` REVOLUTE about the eccentric-shaft axis (`pitman_hub` wraps the boss); one rear `toggle_plate` REVOLUTE mimic(-1) into the frame toggle seat. |
| `dodge_pivot` | forked_anchor | `rec_ore_crusher_var_dodge_pivot` | L65-L72, L182-L191, L260-L316, L519-L556 | eligible | ① skeleton: Dodge-type bottom pivot -- `swing_jaw` REVOLUTE about a fixed hinge at the chamber base (adds `jaw_pivot_mount` frame boss), driven at the top by the eccentric; one rear `toggle_plate` REVOLUTE mimic(-1). |
| `double_toggle` | forked_anchor | `rec_ore_crusher_var_double_toggle` | L58-L94, L174-L181, L319-L386, L478-L576 | eligible | ① skeleton: Blake double-toggle -- `swing_jaw` REVOLUTE about a top pivot (adds `pivot_bosses`), a separate `pitman` member riding the eccentric (REVOLUTE mimic), `front_toggle` REVOLUTE mimic(-0.5) jaw->pitman and `rear_toggle` REVOLUTE mimic(+0.5) frame->pitman. |
| `hydraulic_toggle` | forked_anchor | `rec_ore_crusher_var_hydraulic_toggle` | L292-L368, L524-L540 | eligible | ② joint: single-toggle jaw, but the back link is a PRISMATIC hydraulic tramp-relief `hydraulic_cylinder` (barrel + rod + gland + mounting eyes + hose ports) mimicking the jaw stroke along the seat axis. |

硬约束满足：Slot A=2, B=2, C=4 结构不同 candidate。Slot A/B 降到 2 的理由：
5 星样本池内 frame 只出现两种主体形态（welded flat-plate 与 cast monobloc），
flywheel 只出现两种（spoked 与 solid disc），无第三种 source anchor；不臆造未被
资产支撑的 candidate（Rule 3 / VISUAL_DIVERSITY_MODEL §6：③ 上游需 fork anchor）。
主多样性由 Slot C（4 candidate，① 骨架 + ② 关节）承载，符合"机构主导类"定位。
每个 candidate 均有 forked_anchor + `model.py:Lx-Ly`；无 world_knowledge_extrapolation
candidate。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel children + multiplicity)

```
frame (root; welded_plate_frame / cast_monobloc_frame; + N cross members; + fixed jaw welded|adjustable)
   |
   +-[bearing point (SHAFT_X,0,SHAFT_Z) · shaft CONTINUOUS(Y); belt-plane motor pulley CONTINUOUS(Y) mimic]-> drive  (eccentric shaft + flywheel + pulleys)
   |
   +-[chamber · swing_jaw REVOLUTE(Y); back link REVOLUTE(Y)|PRISMATIC mimic; captured eccentric-boss bearing]-> crush  (swing jaw + toggle linkage [+ pitman])
```

- **slot 顺序 / parent**：`frame` 是 root，唯一被复用的 parent。`drive` 与 `crush`
  都直接把各自 joint 的 `parent=frame`（`shaft`->frame CONTINUOUS，`motor_pulley`->frame
  CONTINUOUS mimic，`swing_jaw`->frame REVOLUTE，back-link->frame/swing_jaw mimic，
  double `pitman`->frame REVOLUTE mimic）。两者均只声明 `downstream`（re-export frame），
  不声明 `upstream`，因此 assembler 不发射自动 chain joint（各模块发原始 joint，与 5 星源一致）。
- **build 顺序**：frame -> drive -> crush（drive 先建 `eccentric_shaft` 以便 crush 的
  hub/boss overlap 声明有对象；crush 的 pivot-mount 硬件按需 append 为 frame visual，
  保持 frame 形态正交）。
- **接口点位**：drive -> frame 轴承点 `(SHAFT_X, ±SIDE_PLATE_Y, SHAFT_Z)`（captured
  bearing）+ 侧电机皮带面 `MOTOR_PULLEY_POS`；crush -> 摆动颚枢轴（single=shaft 轴心；
  dodge=底部 `BOTTOM_PIVOT`；double=顶部 `PIVOT`），toggle seat 在 frame 后座 / pitman 座。
- **跨 slot joint type/axis/range**：shaft CONTINUOUS(Y)；swing_jaw REVOLUTE(±Y, [0, JAW_STROKE])；
  toggle REVOLUTE(Y) mimic / hydraulic PRISMATIC(jaw +X) mimic / double front+rear REVOLUTE(Y) mimic；
  motor_pulley CONTINUOUS(Y) mimic；fixed jaw PRISMATIC(front-wall normal, [0, FIXED_PLATE_TRAVEL]) 仅 adjustable。
- **互斥/派生**：`solid_disc_flywheel` 无 `flywheel_spoke_count`（写 n/a）；
  `fixed_jaw_mode` 与 frame 形态、crush 机构完全正交；jaw_rib_count 由 frame（fixed plate）
  与 crush（movable plate）共享（single-sourced in ResolvedConfig）。

## 每槽位 Module Emits / Interfaces

### Slot A / module welded_plate_frame | cast_monobloc_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (single root part); + `fixed_jaw_plate` (only when `fixed_jaw_mode=adjustable`) | origin L355, L408 |
| visuals | `base_rails` + `cross_member_{i}` (N) + (`flywheel_side_plate`+`drive_side_plate`+`front_wall`+`rear_wall`  |  `cast_housing`) + `toggle_seat` + `rod_bracket` + `bearing_housings` + `motor_pedestal` + `motor_assembly` + (`fixed_plate_welded` \| `adjustment_wedge`) | origin L356-L405; crossmember var L364-L379; cast var L424 |
| internal joints | none for welded; `frame_to_fixed_jaw_plate` PRISMATIC(front-wall normal) only when adjustable | ram var L479-L486 |
| downstream interface | `frame` part, `base_rails` visual, face `positive_z`, anchor `(0,0,0.12)` (informational; children wire manually) | -- |

### Slot B / module spoked_flywheel | solid_disc_flywheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `eccentric_shaft`, `motor_pulley` | origin L457, L507 |
| visuals | `shaft` + `eccentric_boss` + (`flywheel` spoked/disc) + `drive_pulley`; `pulley_body` | origin L458-L477, L508-L512 |
| internal joints | `frame_to_eccentric_shaft` CONTINUOUS(Y); `frame_to_motor_pulley` CONTINUOUS(Y) mimic(BELT_RATIO x shaft) | origin L478-L486, L513-L522 |
| upstream interface | **none declared** (parallel-children; parents joints directly to `frame`) | -- |
| downstream interface | re-export frame downstream (passthrough) | -- |

### Slot C / module single_toggle | dodge_pivot | double_toggle | hydraulic_toggle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `swing_jaw` + back-link part(s): `toggle_plate` (single/dodge) \| `hydraulic_cylinder` (hydraulic) \| `pitman`+`front_toggle_plate`+`rear_toggle_plate` (double) | origin L423, L489; double L530,L543,L561; hydraulic L490 |
| visuals | `pitman_body`+`pitman_hub`+`movable_plate_corrugated`(N ribs)+`tension_rod_spring`; toggle/hydraulic/pitman bodies; (+ frame `jaw_pivot_mount`/`pivot_bosses` appended for dodge/double) | origin L424-L443; dodge L182-L191; double L174-L181,L321-L352 |
| internal joints | `frame_to_swing_jaw` REVOLUTE(Y,[0,JAW_STROKE]); back link REVOLUTE(Y)/PRISMATIC mimic of swing jaw; double: `frame_to_pitman` REVOLUTE mimic + `swing_jaw_to_front_toggle` + `frame_to_rear_toggle` REVOLUTE mimic | origin L444-L504; double L491-L576; hydraulic L524-L540 |
| upstream interface | **none declared** (parallel-children; parents joints directly to `frame`) | -- |
| downstream interface | re-export frame downstream (passthrough) | -- |

活动件语义：eccentric shaft 旋转飞轮/皮带；swing jaw 摆动破碎（开合料口）；back
linkage 随颚行程往复（mimic）。不动细节（walls / tiles / motor / fixed plate welded /
tension rod / cross members）写成宿主 part visual，非独立 part（Rule 1）。captured
eccentric-boss / bearing / toggle-seat 用 element-scoped allow_overlap（Rule 2 例外），
所有 joint 原点落在 frame/shaft 真实几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | welded_plate_frame / cast_monobloc_frame | welded_plate_frame | choice | procedural sampler | Slot A |
| `flywheel_form` | enum | spoked_flywheel / solid_disc_flywheel | spoked_flywheel | choice | procedural sampler | Slot B |
| `crush_linkage` | enum | single_toggle / dodge_pivot / double_toggle / hydraulic_toggle | single_toggle | choice | procedural sampler | Slot C |
| `fixed_jaw_mode` | enum | welded / adjustable | welded | choice | procedural sampler | ram var |
| `cross_member_count` | int | {2,3,4} (obs: 2 origin, 4 crossmember var) | 2 | independent | weighted `{2:.5,3:.2,4:.3}` | origin L125-126, var L119 |
| `flywheel_spoke_count` | int | {4,6,8} (obs: 6 origin, 8 var) | 6 | conditional | only for spoked flywheel; solid disc -> n/a; weighted `{6:.5,4:.2,8:.3}` | origin L291, var L79 |
| `jaw_rib_count` | int | {5,7,9} (obs: 9 origin, 5 var) | 9 | independent | shared by both plates; weighted `{9:.5,7:.2,5:.3}` | origin L196, var L71 |
| `jaw_stroke_scale` | float | [0.8, 1.4] | 1.0 | independent | uniform, clamp; scales JAW_STROKE (crushing swing range) | origin L59 |
| `flywheel_scale` | float | [0.9, 1.2] | 1.0 | independent | uniform, clamp; flywheel rim radius | origin L281-298 |
| `plate_gap_scale` | float | [0.9, 1.25] | 1.0 | independent | uniform, clamp; nominal closed discharge gap | origin L616 |
| (—) | constraint | — | — | inequality | `flywheel_spoke_count = n/a` when `flywheel_form=solid_disc_flywheel` | var |
| (—) | constraint | — | — | inequality | fixed-jaw ram: `FIXED_PLATE_TRAVEL <= closed_gap - 0.02` so an advanced plate never touches the movable plate | ram var L82 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 20 s** (hang-guard `--compile-timeout 60`).
Geometry is a handful of merged `MeshGeometry` parts: side-plate/cast-wall
`ExtrudeGeometry` (profile <=6 pts), flywheel `LatheGeometry` rim (<=56 seg) +
N box spokes, hollow pitman hub `LatheGeometry.from_shell_profiles` (<=48 seg),
tension-rod tori (<=24 tub seg), small motor/pulley cylinders (<=48 seg). No
boolean sculpting, no cadquery (cast frame built from thick extruded walls +
boxes). Tessellation tiers: hero lathe/extrude <=56 seg, small cylinders 20-48
seg, tori 24 seg. Expect 4-10 s/seed; downgrade seg counts first if over.

## Multiplicity / Copy Logic

**三根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 -- `cross_member_count`（底座横梁数）
- `count_param`: `cross_member_count`; `N_range` product `[2,4]`, test `[2,4]`;
  sampling domain 加权 `{2:.5,3:.2,4:.3}`（小 N 偏多）。
- copied object: `cross_member_{i}` box，evenly spaced along X between the base
  rails `t = i/(N-1)` over `[-0.88, 0.88]`。naming `cross_member_{i}`。
  joint policy: none (frame visuals, non-moving, Rule 1)。
- source/gating: origin (N=2) L125-126, crossmember var (N=4) L119-124,L364-379。
- 数量变化不改主体形态/机制。

### 轴 2 -- `flywheel_spoke_count`（飞轮辐条数）
- `count_param`: `flywheel_spoke_count`; `N_range` `[4,8]`, test `{4,6,8}`;
  sampling domain 加权 `{6:.5,4:.2,8:.3}`。
- copied object: `BoxGeometry` spoke merged into the `flywheel` visual at
  `angle=i*2pi/N`。naming: merged spokes (single flywheel visual)。
- source/gating: origin (N=6) L291-296, var (N=8) L79,L293-296。**仅 spoked**；
  `solid_disc_flywheel` 该轴写 `n/a`。
- 数量变化不改飞轮为 spoked 的读法。

### 轴 3 -- `jaw_rib_count`（颚板波纹齿数）
- `count_param`: `jaw_rib_count`; `N_range` `[5,9]`, test `{5,7,9}`; sampling
  domain 加权 `{9:.5,7:.2,5:.3}`（原生细齿偏多，粗齿稀有）。
- copied object: vertical corrugation rib `CylinderGeometry` merged into
  `fixed_plate_corrugated` (Slot A) and `movable_plate_corrugated` (Slot C),
  evenly spaced over the plate Y span。both plates share the same N (matched
  crushing set, single-sourced)。
- source/gating: origin (N=9) L196-200,L243-247, var (N=5) L71,L197,L246。
- ④ 表面装饰计数：不改颚板主体形态，只改齿密。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | crush slot：single-toggle 顶挂摆颚 + 单 toggle（origin）／Dodge 底枢摆颚（dodge_pivot，枢轴位移 + jaw_pivot_mount）／double-toggle（double_toggle，新增 `pitman` part + 前后两 toggle，part/joint 计数 +2）／hydraulic（hydraulic_cylinder 替换 toggle_plate）。全部 forked_anchor。 |
| └ multiplicity | 同构件 xN | 有 | 见 §8：cross_member_count {2,3,4}（origin/crossmember），flywheel_spoke_count {4,6,8}（origin/spoke_count），jaw_rib_count {5,7,9}（origin/jaw_rib）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | back link REVOLUTE(Y) toggle mimic（origin/dodge/double）<-> PRISMATIC hydraulic cylinder（hydraulic_toggle）；fixed jaw FIXED-fold（welded）<-> PRISMATIC 设定行程（fixed_jaw_setting_ram）；shaft/motor CONTINUOUS(Y)。全部 forked_anchor；每种类型都在 sweep 出现（REVOLUTE 摆颚+toggle、PRISMATIC hydraulic/ram、CONTINUOUS shaft）。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **两处登记进 slot_choices**：(A) frame -- welded flat-plate 组装（Macro Surface Construction）/ cast monobloc 体量壳（Volumetric Envelope Form）。(B) flywheel -- 开辐 spoked wheel（Macro Surface Construction）/ 实心 cast disc（Volumetric Envelope Form）。各 2 原型，源锚点上限=2（样本池仅两种，见硬约束理由）。 |
| ④ 表面装饰 | 原型不变叠加表面细节 / 改装饰数 | 有 | 颚板 corrugation ribs（jaw_rib_count {5,7,9}，随颚板 Y 面派生逐齿间距）、飞轮 spoke/hub、motor cooling fins、V-belt rim cheeks、coil-spring tori、hose-port fittings（hydraulic）-- 均为宿主 part visual，随 ③（板面）/⑤（缩放）派生。source_type=record_only（origin/jaw_rib/hydraulic）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：jaw_stroke_scale[0.8,1.4]、flywheel_scale[0.9,1.2]、plate_gap_scale[0.9,1.25]。关节运动包络：swing_jaw REVOLUTE axis Y，开启方向 = 摆颚离开 fixed plate（料口张开），[闭合 0, 可行上界 JAW_STROKE*jaw_stroke_scale <= 0.035]；fixed-jaw PRISMATIC axis=front-wall normal，[0, FIXED_PLATE_TRAVEL<=0.03]（仅 adjustable）；shaft/motor CONTINUOUS 整圈；back-link mimic 随 swing_jaw。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；targeted `ctx.pose` -- swing_jaw 行程使 movable plate 离开 fixed plate（料口张开 > 0.01），fixed-jaw ram 前进（+X），shaft 转 90 度不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal/painted；配色 >=6 colorway：`steel_orange`（灰 frame + 橙颚）、`blue_industrial`、`green_machine`、`red_oxide`、`cat_yellow`、`graphite_dark`。材质大类覆盖 >= ceil(0.5x6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 welded/cast 两种 frame、spoked/disc 两种飞轮、
single/dodge/double/hydraulic 四种机构、颚板齿密变化、配色多样、摆颚/皮带全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界，含 multiplicity 与 fixed_jaw_mode）：
- frame 2 x fixed_jaw_mode 2 x cross_member 3 = 12
- drive (spoked x spoke_count 3 = 3, + solid disc 1 = 4)
- crush 4 x jaw_rib 3 = 12
- => 12 x 4 x 12 = **576** distinct topology tuples。

理由：576 >= 富类别建议 300。真实结构词汇在此展开充分（frame 形态 x 固定颚模式 x
机构骨架 x 三根 multiplicity）。report-only，不设 gate，也不反推上游变体数量。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 frame_form、flywheel_form、crush_linkage、fixed_jaw_mode、palette，再按
compatibility 抽 cross_member_count / flywheel_spoke_count（spoked 时）/ jaw_rib_count、
连续 scale。seed 0 pinned 到 origin 母本组合（welded_plate_frame + spoked_flywheel x6 +
single_toggle + welded fixed jaw + 9 ribs + 2 cross members, steel_orange）作为
documented regression anchor（sparse override，其余 seed 全 procedural）。random sweep
`0-15`（fast）-> `0-35`（final）-> corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 576，>=300，
已记录。report-only。

Controlled local parameterization：`jaw_stroke_scale`、`flywheel_scale`、
`plate_gap_scale`。全部在 `resolve_config` clamp；不破坏 captured-bearing 接口、
joint 原点、multiplicity。连续尺寸契约：先采 independent（三个 scale）-> 无 equation 派生
-> conditional 解析 flywheel_spoke_count（依赖 flywheel_form）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 frame->drive->crush，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | solid_disc -> 无 spoke_count；fixed-jaw ram travel gated <= closed_gap-0.02；frame x drive x crush 正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 3 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | >=2 | >=3 | 备注 |
|---|---:|---|---|---|
| frame | 2 | yes | no | welded/cast；样本池仅两种主体形态（justified） |
| drive | 2 | yes | no | spoked/solid-disc；样本池仅两种飞轮形态（justified） |
| crush | 4 | yes | yes | single/dodge/double/hydraulic |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ cross/spoke/rib multiplicity + fixed_jaw_mode axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented母本 override only)
- compatibility gating prevents illegal combos (solid_disc -> no spoke_count; ram travel gated) in `resolve_config`
- controlled local scales clamped; cannot break captured-bearing interfaces, joint origin honesty, or multiplicity
- captured eccentric-boss / bearing / toggle-seat overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: shaft CONTINUOUS(Y); swing_jaw REVOLUTE(Y,[0,JAW_STROKE]); back link REVOLUTE(Y)/PRISMATIC mimic; motor_pulley CONTINUOUS(Y) mimic; fixed jaw PRISMATIC only when adjustable
- copied `cross_member_i` / spokes / ribs follow naming + placement policy
- `run_industrial_ore_crusher_jaw_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism (jaw stroke, fixed-jaw ram, shaft spin)

## Reject cases

- Swing-jaw stroke drives the movable plate into the fixed plate at the closed pose (discharge gap <= 0) -> keep a positive closed gap; stroke OPENS the gap.
- Fixed-jaw setting ram advances the plate through the movable plate at full travel -> gate `FIXED_PLATE_TRAVEL <= closed_gap - 0.02`.
- Continuous eccentric shaft carries an offset heavy member that sweeps a large torus into the frame -> shaft carries only rotationally compact/outboard visuals; the pitman/toggles follow the crushing stroke as mimics, NOT the full shaft rotation.
- Cross members / ribs / spokes float off the base or plate face (constant offset on a scaled body) -> derive spacing from the realized rail span / plate Y span (Rule 4).
- Cast monobloc frame downgraded to a crude Box, or spoked flywheel LatheGeometry rim downgraded to a plain cylinder (Rule 3 violation).
- Non-moving fixed jaw plate (welded mode) spawned as a FIXED-joint part instead of a frame visual (Rule 1 violation).
- Double-toggle pitman/toggles wired as independent joints instead of coupled mimics -> independent-joint linkage self-intersects; couple to the single crushing DOF.

## 与相邻类别的边界

- 不该混入：**Industrial / Ore crusher (cone / gyratory / roll)**（旋转 mantle 或对辊，无摆颚 + toggle + 飞轮偏心脊，机构骨架不同）。
- 不该混入：**Industrial / Hydraulic press**（竖直压头 + 柱/框，无破碎腔、无偏心飞轮驱动）。
- 不该混入：一个只做焊接钢架/工作台的对象（无颚板、无偏心飞轮、无 toggle 机构）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot A/B 各仅 2 candidate（样本池只出现两种 frame 形态、两种飞轮形态），已按硬约束说明理由；主多样性由 Slot C 4-candidate 机构轴承载。cast frame 以 thick ExtrudeGeometry 墙实现（非 cadquery），保编译预算，同为 Volumetric Envelope Form。 |

## 模板实现备注（可选）

- crushing DOF single-sourced：唯一独立破碎关节是 `frame_to_swing_jaw` REVOLUTE；
  所有 back linkage（toggle / hydraulic cylinder / double front+rear toggle + pitman）
  与 motor pulley 均为 `Mimic`（跟随 swing_jaw 或 shaft），保证 sampled-pose motion QC
  只需采 shaft(CONT) + swing_jaw(REV) + fixed-jaw(PRIS, adjustable) 三根独立轴。
- 偏心轴 CONTINUOUS 只挂 rotationally-compact/outboard visuals（flywheel/pulley/boss），
  整圈旋转零穿模；`eccentric_boss`↔`pitman_hub`/`swing_jaw` 用 element-scoped allow_overlap
  （captured bearing，Rule 2 例外）。
- jaw_rib_count / SIDE_INNER / SHAFT 位置 single-sourced in `ResolvedConfig`（Contract 3c），
  fixed plate（Slot A）与 movable plate（Slot C）共享齿数与腔体几何。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：frame root 声明
  downstream；drive/crush 只声明 downstream（re-export frame）-> 无自动 chain joint，
  各模块发原始 joint 到 frame（parallel-children，同 Tipping_Barrow 惯用）。
- dodge/double 的枢轴硬件（`jaw_pivot_mount` / `pivot_bosses`）由 crush 模块 append 为
  frame visual，保持 frame 形态正交。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | welded_plate_frame + spoked_flywheel + single_toggle | `rec_gray-steel-...bcb3073f` (origin 母本) | L44-L705 | frame part tree + walls, eccentric shaft + spoked flywheel + CONTINUOUS drive + belt mimic, single-toggle swing jaw + REVOLUTE stroke + toggle mimic, fixed jaw plate, 全部 test 语义 |
| S2 | A mult | cross_member_count=4 | `rec_ore_crusher_var_base_crossmember_count` | L119-124, L364-379 | 底座横梁 multiplicity 上界 + even-spacing 逻辑 |
| S3 | A ③ | cast_monobloc_frame | `rec_ore_crusher_var_cast_monobloc_frame` | L54-206, L424 | 铸造整体机身体量壳（thick walls + 轴承凸台），改 ExtrudeGeometry 实现 |
| S4 | C ① | dodge_pivot | `rec_ore_crusher_var_dodge_pivot` | L65-72,L182-191,L260-316,L519-556 | Dodge 底枢摆颚骨架 + jaw_pivot_mount |
| S5 | C ① | double_toggle | `rec_ore_crusher_var_double_toggle` | L58-94,L174-181,L319-386,L478-576 | Blake 双肘板机构：pitman + 前后 toggle + pivot_bosses |
| S6 | A ② | fixed_jaw_setting_ram | `rec_ore_crusher_var_fixed_jaw_setting_ram` | L82-84,L145-195,L479-486 | 固定颚 PRISMATIC 磨损/设定行程 + adjustment wedge |
| S7 | B mult | flywheel_spoke_count=8 | `rec_ore_crusher_var_flywheel_spoke_count` | L79,L293-296 | 飞轮辐条数 multiplicity |
| S8 | C ② | hydraulic_toggle | `rec_ore_crusher_var_hydraulic_toggle` | L292-368,L524-540 | PRISMATIC 液压 tramp-relief 缸替换 toggle plate |
| S9 | A/C mult | jaw_rib_count=5 | `rec_ore_crusher_var_jaw_rib_count` | L71,L197-200,L246-249 | 颚板波纹齿数（双板共享） |
| S10 | B ③ | solid_disc_flywheel | `rec_ore_crusher_var_solid_disc_flywheel` | L282-304 | 实心铸盘飞轮形态 |
</content>
</invoke>
