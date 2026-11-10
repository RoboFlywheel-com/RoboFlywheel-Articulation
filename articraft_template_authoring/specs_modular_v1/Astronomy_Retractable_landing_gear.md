# Modular Spec -- Astronomy / Retractable landing gear

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Retractable_landing_gear` |
| template path | `agent/templates/Astronomy_Retractable_landing_gear.py` |
| test path (optional) | `tests/agent/test_Astronomy_Retractable_landing_gear_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (serial root leg chain + parallel-children wheel-carrier + parallel-children brace + wheel multiplicity) |
| function stem | `astronomy_retractable_landing_gear` (exports `build_astronomy_retractable_landing_gear`, `config_from_seed`, `run_astronomy_retractable_landing_gear_tests`) |

`pattern = mixed`: the root `leg` module emits the serial retracting spine
`mount_plate --REVOLUTE(X)--> strut --PRISMATIC(Z)--> piston` (retraction hinge +
oleo shock, both ALWAYS present). The `wheel_carrier` slot then parents its own
joint(s) directly to the `piston` (parallel-children, no auto chain joint), and
the `brace` slot parents to the `mount_plate`/`strut`. One multiplicity axis
(`wheel_count`) rides on the fork carriers.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`);
line numbers cite `revisions/rev_000001/model.py`:

- `rec_astronomy__retractable_landing_gear__001_png_1a64faf20658463c8dbf85b29d826635`
  -- ORIGIN 母本. plate L69-94, strut (round oleo) L97-137, piston L140-158,
  twin-plate steerable fork L161-192, pneumatic wheel L194-246, joints
  `mount_to_strut` REVOLUTE(X,0..1.22) / `strut_to_piston` PRISMATIC(Z,0..0.075) /
  `piston_to_fork` REVOLUTE(Z,+-0.65) / `fork_to_wheel` CONTINUOUS(X) L248-283.
- `rec_landing_gear_var_blade_leg` -- ③ strut form: round oleo tubing ->
  flat rectangular fabricated blade cross-section (Box replaces Cylinder for
  trunnion/sleeve/gland/collar). Strut L96-141; blade assert L378-407.
- `rec_landing_gear_var_single_side_leg` -- ① carrier skeleton: twin-plate yoke
  -> single-sided cantilever fork + stub axle. Fork L160-185.
- `rec_landing_gear_var_bogie_truck` -- ① carrier skeleton: fork -> fore-aft
  `bogie_beam` on a REVOLUTE(X,+-0.18) rocker carrying 2 axles + 2 wheels
  (CONTINUOUS X); steering removed. piston lug L154-158, beam L160-234, joints
  L280-303.
- `rec_landing_gear_var_dual_wheel` -- ① wheel multiplicity: 1 -> 2 coaxial
  wheels on a widened axle (fork arms +-0.225, axle_pin L0.42, wheels X-offset
  +-0.1075). meshes L53-95, wheels L238-260, joints L290-300.
- `rec_landing_gear_var_solid_wheel` -- ③ wheel aperture form: pneumatic
  TireGeometry+WheelGeometry -> one-piece solid molded disc + plain hub-face
  caps. Solid disc L181-215 (source uses cadquery; re-authored here as a
  LatheGeometry revolved solid disc -- still a mesh, Rule 3 preserved).
- `rec_landing_gear_var_fixed_caster` -- ② joint type: `piston_to_fork`
  REVOLUTE -> FIXED (rigid non-steering main-gear leg). L268-272.
- `rec_landing_gear_var_free_caster` -- ② joint type: `piston_to_fork`
  REVOLUTE -> CONTINUOUS (free-swiveling caster, full turn). L268-273.
- `rec_landing_gear_var_drag_brace` -- ① companion skeleton: adds a 2-segment
  folding drag/side-stay brace (`drag_brace_upper` + `drag_brace_lower`) on
  REVOLUTE knee joints Mimic-tied to `mount_to_strut` so it folds with
  retraction. lugs L96-109,L153-165; parts L276-327; joints+Mimic L364-387;
  allowances L475-569.
- `rec_landing_gear_var_trailing_link` -- ① carrier skeleton: fork -> levered
  `trailing_arm` on a transverse REVOLUTE(X,-0.08..0.20) pin at the piston base,
  carrying the wheel axle AFT (+Y) of the strut centerline. piston pivot L155-167,
  arm L170-231, joints L318-336.

## 核心身份

A single **retractable aircraft landing-gear leg**: an aircraft-side `mount_plate`
that folds up on a **retraction hinge** (`mount_to_strut` REVOLUTE about the
lateral X pivot), a long **oleo-pneumatic shock strut** (`strut` sleeve +
telescoping `piston` on a PRISMATIC shock stroke), and a **wheel carrier**
(steerable/fixed/caster fork, single-sided cantilever, fore-aft bogie truck, or
levered trailing arm) that grounds the aircraft on one or more **rolling wheels**
(CONTINUOUS spin). Optional folding **drag/side-stay brace** locks the leg
down and folds with it. At least two real non-fixed joints are always present
(the retraction hinge + the oleo shock + at least one rolling wheel).

Default mature domain: a single nose- or main-gear leg, ~1.0-1.1 m deployed leg
length, 1-2 wheels of ~0.30 m radius.

Not to be confused with the neighbouring picture subclass **Lunar rover /
Mars rover** (a whole vehicle chassis carrying a suspension per corner) -- this
object is ONE isolated gear leg, not a rover; there is no chassis body, only the
aircraft mount plate.

## 槽位 + 候选模块表

### Slot A：leg (root · ③ Primary Form Family + always-on retraction/oleo joints)

The retracting spine. Same part tree + joint semantics across candidates:
`mount_plate` (plate skin + 2 hinge lugs + lug bores) + `strut` (trunnion +
outer shock sleeve + gland/collar + scissor torque links) + `piston` (chrome
piston + lower oleo head). Joints `mount_to_strut` REVOLUTE(X,0..retract_upper)
and `strut_to_piston` PRISMATIC(Z,0..oleo_stroke) are always emitted. Only the
strut member cross-section prototype changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `round_oleo` | forked_anchor (origin) | `rec_...1a64faf2` | L97-L158 | eligible | round telescoping oleo tubes: `Cylinder` trunnion/sleeve/gland/collar. **Volumetric Envelope Form** |
| `blade_leg` | forked_anchor | `rec_landing_gear_var_blade_leg` | L96-L141 | eligible | flat fabricated slab leg: `Box` trunnion (X-long) + `Box` sleeve (Y>X) + rectangular gland/collar flanges. **Volumetric Envelope Form** |

只有 2 candidate 的理由：整个 5 星池对 strut 主体形态只提供 round-oleo /
blade 两种可识别原型（其余变体都保持 round-oleo 主体、只改 carrier/wheel/joint）。
这是 mechanism-dominated 类别（主多样性在 Slot B ①②，见 §8.5），非 form-dominated，
故 ③ leg slot 降到 2 并登记进 `slot_choices`（符合 SPEC_TEMPLATE §4 "样本不足时
≥2 并说明理由"）。

### Slot B：wheel_carrier (parallel child on piston · ① skeleton + ② steer-joint type + `wheel_count`)

The dominant diversity axis. Each carrier adds its own terminal fitting visual
to the `piston` at the mount line (origin honesty), parents its first joint
directly to `piston`, and emits its wheel(s) via the shared `_emit_wheel`
helper. Captured pivots (steering bearing in socket, bogie/trailing pin in lug,
axle pin through hub) are grandfathered raw joints + element-scoped
`allow_overlap` (Rule 2 captured-pivot exception, exactly as every source).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `steer_fork` | forked_anchor (origin) | `rec_...1a64faf2` | L161-L192, L266-L283 | eligible | twin-plate yoke fork (crown + steering socket + 2 arms + axle bosses + axle pin); `piston_to_fork` **REVOLUTE** axis Z, +-steer_range. `wheel_count` {1,2}. |
| `fixed_fork` | forked_anchor | `rec_landing_gear_var_fixed_caster` | L268-L272 | eligible | same fork part tree; `piston_to_fork` **FIXED** (rigid non-steering main gear). `wheel_count` {1,2}. |
| `free_caster` | forked_anchor | `rec_landing_gear_var_free_caster` | L268-L273 | eligible | same fork part tree; `piston_to_fork` **CONTINUOUS** axis Z (free full-turn swivel, no limits). `wheel_count` {1,2}. |
| `single_side_fork` | forked_anchor | `rec_landing_gear_var_single_side_leg` | L160-L185 | eligible | ① single-sided cantilever fork (crown block + one `cantilever_leg` box + `stub_axle_boss`); REVOLUTE steer. `wheel_count` gated to 1 (stub axle). |
| `bogie_truck` | forked_anchor | `rec_landing_gear_var_bogie_truck` | L154-L234, L280-L303 | eligible | ① `bogie_beam` part on `piston_to_bogie` **REVOLUTE** axis X (+-0.18 fore-aft rocker); beam carries 2 transverse axles + `bogie_to_wheel_{0,1}` **CONTINUOUS** X. No steering. `wheel_count` fixed 2. |
| `trailing_link` | forked_anchor | `rec_landing_gear_var_trailing_link` | L155-L231, L318-L336 | eligible | ① levered `trailing_arm` on `piston_to_trailing_arm` **REVOLUTE** axis X (-0.08..0.20) at the piston base; arm carries the axle AFT (+Y) / down (-Z) of the strut centerline. `wheel_count` fixed 1. |

### Slot C：brace (parallel child on plate/strut · ① companion skeleton)

Optional folding drag/side-stay brace.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `no_side_stay` | forked_anchor (origin baseline) | `rec_...1a64faf2` | L97-L137 (strut, no brace) | eligible | no folding brace; a short static `side_stay_gusset` fused onto the strut as a non-moving `strut.visual` (Rule 1). |
| `folding_drag_brace` | forked_anchor | `rec_landing_gear_var_drag_brace` | L276-L387 | eligible | ① 2-segment `drag_brace_upper` + `drag_brace_lower` linkage; `plate_to_drag_upper` + `drag_knee` **REVOLUTE** Mimic-tied to `mount_to_strut` (folds with retraction). |

只有 2 candidate 的理由：5 星池只提供 "无 brace"（origin 及多数变体）与 "folding
drag brace"（drag_brace 变体）两种结构，是真实的 ① 存在/缺失骨架差异；登记进
`slot_choices`（SPEC_TEMPLATE §4 "样本不足时 ≥2 并说明理由"）。

硬约束满足：Slot B = 6 结构不同 candidate（远超 3）；Slot A / C 各 2（样本池上限，
已说明）。每个 candidate 有 `forked_anchor` + `model.py:Lx-Ly`；无
`world_knowledge_extrapolation` candidate（solid_wheel 是 ③ 轮形，属 `wheel_style`
参数而非新增 skeleton，几何锚定在 solid_wheel 源，只把 cadquery 布尔换成同为 mesh
的 LatheGeometry 旋转实体盘，保持同 part tree / mesh 家族 / interface，Rule 3 内）。

## 槽位图（slot graph）

pattern: `mixed` (serial root chain + parallel children + multiplicity)

```
leg (root)  mount_plate --REVOLUTE(X,retract)--> strut --PRISMATIC(Z,oleo)--> piston
   |
   +--[piston base fitting · captured pivot]--> wheel_carrier
   |        steer_fork/fixed_fork/free_caster/single_side_fork : piston --(REVOLUTE Z steer | FIXED | CONTINUOUS Z)--> fork --CONTINUOUS(X)--> wheel x{1,2}
   |        bogie_truck   : piston --REVOLUTE(X,+-0.18)--> bogie_beam --CONTINUOUS(X)--> wheel_{0,1}
   |        trailing_link : piston --REVOLUTE(X,-0.08..0.20)--> trailing_arm --CONTINUOUS(X)--> wheel
   |
   +--[plate drag lug + strut shoulder lug · pinned]--> brace
            no_side_stay        : (static gusset visual on strut; no joint)
            folding_drag_brace  : plate --REVOLUTE(X,Mimic)--> drag_brace_upper --REVOLUTE(X,Mimic knee)--> drag_brace_lower (pinned to strut lug)
```

- **slot 顺序 / parent**：`leg` 是 root（唯一被复用 parent 链）。`wheel_carrier`
  把首个 joint `parent=piston`；`brace` 把 `parent=mount_plate` / knee-child
  parent=drag_brace_upper，lower 端 pin 到 strut。两者只声明 `downstream`
  （re-export leg 的 piston 面），不声明 `upstream` -> assembler 不发自动 chain
  joint，各模块自己发原始 joint（parallel-children，同 Tipping_Barrow）。
- **接口点位**：carrier -> piston 底端 fitting，参考 z ~ -0.565（fork）/ -0.555
  （bogie）/ -0.572（trailing），各 carrier 自己往 `piston` 加 fitting visual 使
  joint 原点落在真实几何上（origin honesty）。brace -> plate 底 `drag_lug`
  (0,-0.14,0.02) + strut `drag_strut_lug` (0,-0.12,-0.18)。
- **跨 slot joint type/axis/range**：retraction REVOLUTE(X,0..retract_upper<=1.25)；
  oleo PRISMATIC(Z,0..oleo_stroke<=0.09)；steer REVOLUTE(Z,+-steer_range) /
  FIXED / CONTINUOUS(Z)；bogie rocker REVOLUTE(X,+-0.18)；trailing REVOLUTE(X,
  -0.08..0.20)；wheel spin CONTINUOUS(X)；drag brace REVOLUTE(X) Mimic。
- **互斥/派生**：`bogie_truck` -> wheel_count=2（每轴一轮）；`trailing_link` /
  `single_side_fork` -> wheel_count=1。leg 形态与 carrier/brace 正交（strut 主体
  换 box 不改挂点），自由组合。

## 每槽位 Module Emits / Interfaces

### Slot A / module round_oleo | blade_leg
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mount_plate` (root), `strut`, `piston` | origin L69,L98,L140 |
| visuals | plate: `plate_skin`+`hinge_lug_{0,1}`+`lug_bore_{0,1}`; strut: `trunnion_tube`/`trunnion_web`/`outer_shock_sleeve`/`upper_gland_nut`/`lower_sleeve_collar`/`torque_link_{0,1}`/`{upper,lower}_torque_pivot` (Cylinder or Box per form); piston: `chrome_piston`+`lower_oleo_head` | origin L70-158; blade L99-141 |
| internal joints | `mount_to_strut` REVOLUTE(X,0..retract_upper); `strut_to_piston` PRISMATIC(Z,0..oleo_stroke) | origin L248-265 |
| upstream interface | none (root) | — |
| downstream interface | `piston` part, `chrome_piston` visual, face `negative_z`, anchor at piston base (informational; children wire manually) | — |

### Slot B / module steer_fork | fixed_fork | free_caster | single_side_fork | bogie_truck | trailing_link
| emits | 描述 | 来源 |
|---|---|---|
| parts | fork carriers: `fork` + `wheel`/`wheel_{0,1}`; bogie: `bogie_beam` + `wheel_{0,1}`; trailing: `trailing_arm` + `wheel` | origin L161,L194; bogie L160,L235; trailing L170 |
| piston fitting visual | fork: `caster_bearing_stack`; bogie: `bogie_pivot_lug`; trailing: `pivot_lug`+`pivot_pin` (added to `piston`) | origin L153-158; bogie L154-158; trailing L155-167 |
| carrier visuals | fork: `fork_crown`+`steering_socket`+`fork_arm_{0,1}`+`*_axle_boss`+`axle_pin` (single-side: `cantilever_leg`+`stub_axle_boss`); bogie: `beam_body`+`pivot_pin`+`axle_{0,1}`+`axle_cap_{0,1}`; trailing: `pivot_bushing`+`pivot_web`+`arm_member_{0,1}`+`arm_cross_brace`+`axle_boss_{0,1}`+`axle_pin`; wheel: pneumatic tire+sidewall+hub+bore OR solid disc+hub caps | origin L162-246; single L162-185; bogie L163-234; trailing L184-231 |
| internal joints | `piston_to_fork` REVOLUTE(Z)/FIXED/CONTINUOUS(Z); `piston_to_bogie` REVOLUTE(X,+-0.18); `piston_to_trailing_arm` REVOLUTE(X,-0.08..0.20); `fork_to_wheel[_i]`/`bogie_to_wheel_i`/`trailing_arm_to_wheel` CONTINUOUS(X) | origin L266-283; bogie L280-303; trailing L318-336 |
| upstream interface | none declared (parallel-children; joints parent directly to `piston`) | — |
| downstream interface | re-export leg downstream (passthrough) | — |

### Slot C / module no_side_stay | folding_drag_brace
| emits | 描述 | 来源 |
|---|---|---|
| parts | none / `drag_brace_upper` + `drag_brace_lower` | drag L276,L305 |
| visuals | no_side_stay: `side_stay_gusset` (static, on `strut`); drag: lugs `drag_lug`/`drag_lug_bore` (plate), `drag_strut_lug`/`_bore` (strut), bars+bosses | drag L96-109,L153-165,L276-327 |
| internal joints | none / `plate_to_drag_upper` REVOLUTE(X) Mimic + `drag_knee` REVOLUTE(X) Mimic | drag L364-387 |
| upstream interface | none declared (parallel-children) | — |
| downstream interface | re-export leg downstream (passthrough) | — |

活动件语义：retraction 折叠整条 leg；oleo 压缩缓冲；steer 转向机轮；bogie rocker
前后摇；trailing 杠杆压缩；wheel 滚动；drag brace 随 retraction 折叠。不动细节
（torque links / gusset / lug bores / axle caps）写成宿主 part visual，非独立 part
（Rule 1）。captured pivots 用 element-scoped allow_overlap（Rule 2 例外），joint
原点落在真实 fitting 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `leg_form` | enum | round_oleo / blade_leg | round_oleo | choice | procedural sampler | Slot A |
| `carrier_module` | enum | steer_fork / fixed_fork / free_caster / single_side_fork / bogie_truck / trailing_link | steer_fork | choice | procedural sampler | Slot B |
| `brace_module` | enum | no_side_stay / folding_drag_brace | no_side_stay | choice | procedural sampler | Slot C |
| `wheel_style` | enum | pneumatic / solid | pneumatic | choice | procedural sampler | solid_wheel L181-215 |
| `wheel_count` | int | {1,2} (obs: 1 origin, 2 dual_wheel) | 1 | conditional | fork carriers {1,2}; bogie=2; single_side/trailing=1 | origin L194, dual L238-260 |
| `wheel_radius_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; scales tire/disc radius (leaf part) | origin L195 |
| `retract_upper` | float | [1.05, 1.25] | 1.22 | independent | retraction REVOLUTE upper (rad) | origin L255 |
| `oleo_stroke` | float | [0.06, 0.09] | 0.075 | independent | shock PRISMATIC upper (m) | origin L264 |
| `steer_range` | float | [0.45, 0.75] | 0.65 | conditional | steer_fork/single_side REVOLUTE +-range; else n/a | origin L273 |
| (—) | constraint | — | — | inequality | `wheel_count==2` iff carrier in {steer_fork,fixed_fork,free_caster}; ==1 for single_side/trailing; ==2 for bogie | dual L238-260 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 20 s** (hang-guard `--compile-timeout 60`).
Heavy geometry is the wheel: `TireGeometry` + `WheelGeometry` meshes; both are
built ONCE per seed and the SAME mesh object is reused for all wheels
(1-2 wheels). The solid disc is one `LatheGeometry` (32 seg) revolved profile.
Blade leg is `Box`es (cheap). Tube helpers use plain `Cylinder`. No boolean
sculpting (source cadquery solid disc re-authored as a lathe). Expect 4-10 s/seed;
if over, drop tire tread `count` / lathe segments first.

## Multiplicity / Copy Logic

**一根 multiplicity 轴**：

### 轴 1 — `wheel_count`（fork carrier 上的同轴轮数）
- `count_param`: `wheel_count`; `N_range` product `{1,2}`, test `{1,2}`;
  sampling domain 加权（fork carriers only）`{1: 0.6, 2: 0.4}`（小 N 偏多）。
- copied object: `wheel_{i}` 整个轮子装配（tire+sidewall+hub+bore 或 solid
  disc+caps）+ 各自 `fork_to_wheel_{i}` CONTINUOUS(X)。轮子沿 spin 轴 X 偏移
  `+-(tire_width+gap)/2`；fork 臂加宽到 +-0.225、axle_pin 加长以跨双轮。
- naming: `wheel` (N=1) / `wheel_{0,1}` (N=2) / (bogie) `wheel_{0,1}`.
  placement: 同轴 X 偏移。joint policy: 每轮独立 CONTINUOUS(X) spin。
- source/gating: origin (N=1) L194-246, dual_wheel (N=2) L238-260。
  `single_side_fork` / `trailing_link` 强制 1；`bogie_truck` 强制 2（每轴一轮，
  fore-aft 分布，非同轴）。
- 数量变化不改 carrier 机制（steer 仍 steer，fixed 仍 fixed）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | carrier skeleton candidates：twin-plate fork（origin）／single-sided cantilever fork（single_side_leg）／fore-aft bogie beam +2 轴（bogie_truck，加 rocker part+joint）／levered trailing arm（trailing_link，加 arm part + X 轴 pivot）；brace：无（origin）／2 段折叠 drag brace（drag_brace，加 2 part+2 joint）。全部 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`wheel_count` {1,2}（origin/dual_wheel）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | `piston_to_fork` REVOLUTE(Z,steer)（origin）↔ FIXED（fixed_caster）↔ CONTINUOUS(Z)（free_caster）；bogie rocker REVOLUTE(X)（bogie）；trailing pivot REVOLUTE(X)（trailing_link）。全部 forked_anchor；每种类型都在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | (A) strut 主体 — round oleo tube（origin, Volumetric Envelope）/ flat fabricated blade（blade_leg, Volumetric Envelope），登记进 `slot_choices`。(B) wheel 孔径 — pneumatic 充气胎（origin, Volumetric Envelope）/ solid molded disc（solid_wheel, Volumetric Envelope），登记为 `wheel_style`。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `torque_link`/`torque_pivot` 剪式连杆、`lug_bore`/`axle_bore_shadow` 深色套筒、`outer_sidewall_ring` 胎侧环、`axle_cap` 轴端法兰、hub bolt pattern（WheelHub `bolt_pattern` count=6）、`side_stay_gusset` — 均为宿主 part visual，随 ③（strut box/round）/⑤（wheel_radius_scale）派生尺寸。source_type=record_only（origin/blade/bogie）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：wheel_radius_scale[0.85,1.15]。关节运动包络（每个非-continuous joint）：retraction REVOLUTE axis X，单向开 [0, retract_upper<=1.25]；oleo PRISMATIC axis Z，[0, oleo_stroke<=0.09] m；steer REVOLUTE axis Z，双向 [-steer_range, +steer_range]（<=+-0.75）；bogie rocker REVOLUTE axis X，[-0.18, 0.18]；trailing REVOLUTE axis X，[-0.08, 0.20]；drag brace REVOLUTE Mimic。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`；targeted `ctx.pose` — retraction 折叠机轮上移、oleo 压缩抬 carrier、steer 转 fork、bogie rocker 摇 beam、trailing pivot 抬轮。continuous wheel spin 采 {0,+-90,180}。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal/rubber；配色 >=6 colorway：`nose_gear_white`、`bare_aluminum`、`military_gray`、`navy_gloss`、`matte_black`、`hydraulic_gold`。材质大类覆盖 >= ceil(0.5x3)=2。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 round/blade 两种 strut、pneumatic/solid 两种
wheel、fork/single-side/bogie/trailing 四类 carrier、steer/fixed/caster 三种关节、
单/双轮、drag brace 折叠，材质配色多样，全部关节全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- leg 2 × brace 2 × wheel_style 2 ×
  carrier(fork×3 form × wheel_count 2 = 6, + single_side 1 + bogie 1 + trailing 1 = 9)
  = **2 × 2 × 2 × 9 = 72**。

理由：72 < 富类别建议 300，因为这是单条 gear leg，真实结构词汇收敛在
「plate+strut+piston + 一个 carrier + 可选 brace」一个 cell，可动轴只有几根离散槽
+ 一根小 multiplicity。不硬凑组合空间（红线：不反推上游变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 leg_form、carrier_module、brace_module、wheel_style，再按 compatibility 抽
wheel_count（fork carriers 加权；bogie=2，single_side/trailing=1）、palette、连续
scale（wheel_radius_scale/retract_upper/oleo_stroke/steer_range）。seed 0 pinned
到 origin 母本组合（round_oleo + steer_fork×1 wheel + no_side_stay, pneumatic,
nose_gear_white）作为 documented regression anchor（sparse override，其余 seed 全
procedural）。random sweep `0-15`（fast）-> `0-35`（final）-> corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 72
（见上），低于 300 的原因为单-leg 结构词汇收敛，已记录。report-only。

Controlled local parameterization：`wheel_radius_scale`（leaf 轮半径）、
`retract_upper`/`oleo_stroke`/`steer_range`（关节行程）。全部在 `resolve_config`
clamp；不破坏 captured-pivot 接口、joint 原点、multiplicity。连续尺寸契约：先采
independent（wheel_radius_scale/retract_upper/oleo_stroke）-> conditional 解析
steer_range（仅转向 carrier）/ wheel_count（按 carrier）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 leg->carrier->brace->wheel_style，加权 choice；wheel_count 按 carrier 加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | bogie->wheel_count=2；single_side/trailing->1；steer_range 仅 REVOLUTE-steer carrier；leg×carrier×brace×wheel_style 正交自由组合 | 无 floating / collision / 轴错误 / max-N / 可选子件失败 |
| controlled local variation | 4 个 clamp 连续 scale | 比例/行程变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| leg | 2 | yes | no | round/blade（③ 池上限，已说明） |
| wheel_carrier | 6 | yes | yes | steer/fixed/free/single-side/bogie/trailing |
| brace | 2 | yes | no | none/drag（① 池上限，已说明） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ wheel_count / wheel_style axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented母本 override only)
- compatibility gating prevents illegal combos (bogie->2; single_side/trailing->1; steer_range only for revolute-steer carriers) in `resolve_config`
- controlled local scales clamped; cannot break captured-pivot interfaces, joint origin honesty, or multiplicity
- captured pivots are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: retraction REVOLUTE(X); oleo PRISMATIC(Z); steer REVOLUTE(Z)/FIXED/CONTINUOUS(Z); bogie/trailing REVOLUTE(X); wheel CONTINUOUS(X); drag brace REVOLUTE Mimic
- copied `wheel_{i}` follow naming + placement policy
- `run_astronomy_retractable_landing_gear_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Retracted gear (mount_to_strut at upper) collides with the mount plate -> clamp `retract_upper` <=1.25 so the folded wheel clears the plate.
- Steered fork+wheel (steer at +-range) sweeps into the strut/piston -> keep steer axis vertical Z through the wheel center; wheel stays below the piston (no clamp needed) OR shrink `steer_range`.
- bogie rocker at +-0.18 drives a wheel up into the piston -> keep the rocker range small (+-0.18) and the beam below the piston base.
- trailing_arm places the wheel FORWARD of the strut (wrong sign) -> arm must extend +Y (aft) so the axle sits behind the centerline; assert with `expect_gap`.
- drag brace bars self-intersect or hit the strut mid-retraction -> element-scoped allow_overlap on bar<->lug / bar<->strut-lug / knee only; never mask a bar<->sleeve body 穿模.
- Downgrading the pneumatic `TireGeometry`/`WheelGeometry` meshes or the solid-disc `LatheGeometry` to a crude `Cylinder` (Rule 3 violation).
- Dual coaxial wheels overlap each other (gap too small) -> offset each by `(tire_width+gap)/2` along the spin axis and widen the fork arms.

## 与相邻类别的边界

- 不该混入：**Astronomy / Lunar rover / Mars rover**（整车底盘每角一个悬挂；此对象只是单条起落架腿，无车身，仅飞机安装板）。
- 不该混入：**Industrial / Mine cart**（轨道货斗车轮组，无 oleo 减震腿、无收放铰链）。
- 不该混入：一个只会滚的孤立轮子（无 retraction 铰链、无 oleo strut、无 carrier 骨架身份特征）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全部 10 个 5 星样本均在 PATHFINDER 任务书确认池内；无 checklist 分歧。solid_wheel 源用 cadquery 布尔造实体盘，本模板改用同为 mesh 的 LatheGeometry 旋转实体盘（保编译预算 + Rule 3），待 reviewer 确认忠实度。 |

## 模板实现备注（可选）

- piston 底端 fitting 由 carrier module 各自往 `piston` part 加 visual（fork
  caster_bearing_stack / bogie lug / trailing pivot_lug+pin），使 carrier 首个
  joint 原点落在真实几何（origin honesty）；leg module 只造 chrome_piston +
  lower_oleo_head（carrier-agnostic）。
- captured pivot -> 原始 joint（no MatingContract, grandfathered）+ element-scoped
  `allow_overlap`（steering socket<->bearing、pivot bushing/web<->pin/lug、axle
  pin<->hub、dual-wheel hub<->axle），与全部 5 星源一致（Rule 2 例外）。
- 两轮共享一个 tire_mesh / hub_mesh；solid disc 共享一个 lathe mesh -- 保编译预算。
- drag brace 用 `Mimic(joint="mount_to_strut", ...)`；plate_to_drag_upper
  multiplier=0.90，drag_knee multiplier=-1.50（源值），随 retraction 折叠；
  若 sampled-pose 在 mid-retraction 穿模再补 element-scoped allow_overlap 或
  回缩 retract_upper。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：leg root 声明
  downstream；carrier/brace 只声明 downstream（re-export piston）-> 无自动 chain
  joint，各模块发原始 joint（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | round_oleo + steer_fork + no_side_stay + pneumatic wheel | `rec_...1a64faf2` (origin 母本) | L48-L433 | plate/strut/piston part tree + retraction/oleo joints, twin-plate fork + REVOLUTE steer, pneumatic wheel, 全部 test 语义 |
| S2 | A ③ | blade_leg | `rec_landing_gear_var_blade_leg` | L96-L141 | flat fabricated blade strut (Box cross-section) |
| S3 | B ① | single_side_fork | `rec_landing_gear_var_single_side_leg` | L160-L185 | single-sided cantilever fork + stub axle |
| S4 | B ① | bogie_truck | `rec_landing_gear_var_bogie_truck` | L154-L303 | fore-aft bogie beam rocker + 2 axles + 2 wheels |
| S5 | B mult | wheel_count=2 | `rec_landing_gear_var_dual_wheel` | L53-L95, L238-L300 | coaxial dual-wheel + widened fork/axle |
| S6 | wheel ③ | solid wheel | `rec_landing_gear_var_solid_wheel` | L181-L215 | solid molded disc wheel form (re-authored as LatheGeometry) |
| S7 | B ② | fixed_fork | `rec_landing_gear_var_fixed_caster` | L268-L272 | FIXED non-steering caster joint |
| S8 | B ② | free_caster | `rec_landing_gear_var_free_caster` | L268-L273 | CONTINUOUS free-swivel caster joint |
| S9 | C ① | folding_drag_brace | `rec_landing_gear_var_drag_brace` | L276-L569 | 2-segment folding drag brace + Mimic joints + allowances |
| S10 | B ① | trailing_link | `rec_landing_gear_var_trailing_link` | L155-L336 | levered trailing-arm suspension + transverse X pivot |
