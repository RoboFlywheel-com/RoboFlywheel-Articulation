# Modular Spec — Art Drawing Models / Articulated mannequin / Poseable figure mannequin

## 元信息
| 项 | 值 |
|---|---|
| slug | `Art_Drawing_Models_Articulated_mannequin_Poseable_figure_mannequin` |
| template path | `agent/templates/Art_Drawing_Models_Articulated_mannequin_Poseable_figure_mannequin.py` |
| test path (optional) | `tests/agent/test_Art_Drawing_Models_Articulated_mannequin_Poseable_figure_mannequin_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root `base`/stand + parallel-children `torso` body + parallel-children `arms` + 1 caster multiplicity axis) |
| function stem | `art_drawing_models_articulated_mannequin_poseable_figure_mannequin` (exports `build_art_drawing_models_articulated_mannequin_poseable_figure_mannequin`, `config_from_seed`, `run_art_drawing_models_articulated_mannequin_poseable_figure_mannequin_tests`) |

`pattern = mixed`: a root `base` (wheeled stand) carries the figure. The `torso`
body slot FIXES the kinematic-root torso onto the base and emits, as parallel
children of the (upper/lower) torso, the head + 2 leg chains; the `arms` slot
emits the 2 arm chains as parallel children of the upper torso. One multiplicity
axis (`caster_count`) rides on the base. Every appendage joint is parented
manually (parallel-children idiom, no assembler chain joint) exactly as the
5-star sources author it.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full (origin full, 9 diffed against origin) |

Samples (all `collections=["workbench"]`, `rating=5`):

- `rec_use-the-attached-reference-image-003-png-as-the-_20260706_043717_205274_0c6efacc` — ORIGIN 母本 (matte-black sculpted mannequin: loft superellipse torso, tapered lathe limbs, ovoid head, 12 REVOLUTE joints, square glass base + 4 casters + rear lean-rod).
- `rec_mannequin_var_barrel_torso` — ③ body form (torso): 3 loft regions -> single `torso_barrel` LatheGeometry egg body.
- `rec_mannequin_var_wooden_blocky` — ③ body form (whole figure): organic loft/lathe -> classic turned-wood LatheGeometry blocks (`turned_barrel`/`turned_cylinder`/`turned_limb`), wood palette.
- `rec_mannequin_var_caster_count` — multiplicity: 4 corner casters on square plate -> N radial casters on circular plate (`NUM_CASTERS`).
- `rec_mannequin_var_center_pole_mount` — ① stand: rear lean-rod+saddle -> central vertical `central_pole` rising into the pelvis (pole-through-hip mount).
- `rec_mannequin_var_telescoping_stand` — ①/② stand: lean-rod -> `outer_sleeve` (on base) + separate `height_rod` part on a PRISMATIC `sleeve_to_rod` (axis Z, 0..0.30).
- `rec_mannequin_var_segmented_hands` — ① skeleton (hands): mitten paddle -> `palm` + 4 `finger_i` parts + `thumb` part, each on a REVOLUTE knuckle.
- `rec_mannequin_var_swivel_neck` — ② joint type: `neck_joint` REVOLUTE(Y,+-0.8) -> CONTINUOUS(Z) free swivel.
- `rec_mannequin_var_twist_wrists` — ② joint type: `{side}_wrist` REVOLUTE(X,+-1.0) -> CONTINUOUS(Z) free pronation.
- `rec_mannequin_var_waist_joint` — ① skeleton (torso spine): single `torso` -> `pelvis` (FIXED to base) + `chest` on a REVOLUTE `waist_joint` (axis Y, -0.5..0.8); arms/head parent to chest, legs to pelvis.

## 核心身份

A **poseable artist drawing mannequin / manikin**: a stylized featureless human
figure (rounded ovoid head, sculpted or turned-wood torso, tapered limbs) whose
every major joint is a visible ball-and-socket articulation — neck, both
shoulders/elbows/wrists, both hips/knees/ankles — so the figure can be posed.
The figure is a kinematic tree rooted at the `torso`, which is rigidly mounted on
a small tabletop **stand** (a wheeled glass base plate with casters, plus a rear
lean-rod / central mounting pole / telescoping height column). At least a dozen
non-fixed joints are always present (limb REVOLUTEs); optional extras add finger
knuckles, a waist bend, a free-swivel neck, twist wrists, and a prismatic stand.
Default mature domain: a ~1.6 m-tall (model-scale) full figure on a rolling base.

Not to be confused with the neighbouring picture subclasses **action figure /
poseable toy with sculpted costume detail** (this manikin is featureless matte
black or plain turned wood, no face/clothing/accessories) or a **static tailor's
dress form / bust** (no limbs, single upright body on a pole — the manikin has a
full articulated limb tree). It is not a **robot/android** (organic tapered
proportions + ball joints, not mechanical hardware).

## 槽位 + 候选模块表

### Slot A：stand (root · ① support skeleton + ② prismatic + ③ base-plate form + multiplicity `caster_count`)

The root `base` part: a rolling glass plate + N caster visuals + a rear support
structure. The support sub-form is the slot candidate. All expose the same
`figure_mount` datum (top of base at world z ~= 0.07) where the torso FIXES on.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `lean_rod` | forked_anchor (origin) | `rec_use-...0c6efacc` | L77-L110 | eligible | glass `base_plate` Box + N caster cylinders + rear `lean_rod` Cylinder + `lean_saddle` Box (static decoration; torso FIXED to base). |
| `center_pole` | forked_anchor | `rec_mannequin_var_center_pole_mount` | L99-L112 | eligible | central vertical `central_pole` Cylinder from plate center up into the pelvis cavity (pole-through-hip); no rear rod. Torso FIXED to base. |
| `telescoping_stand` | forked_anchor | `rec_mannequin_var_telescoping_stand` | L99-L129 | eligible | ① adds a part + ② PRISMATIC: `outer_sleeve` Cylinder on base + separate `height_rod` part (`inner_rod_member` + `lean_saddle`) on PRISMATIC `sleeve_to_rod` (axis Z, 0..0.30). |

### Slot B：body (parallel-children on base · ③ Primary Form Family + ① waist articulation + ② neck joint)

The figure body: (lower)torso + (upper)torso + head + neck + 2 leg chains. The
③ mesh idiom is the registered form slot. The torso is FIXED to the base (a
composed sub-assembly: the stand and the figure are distinct fabricated bodies
joined rigidly; the torso is the kinematic root of every limb — Rule 1 legit
FIXED). Arms/head/neck parent to the UPPER torso; legs to the LOWER torso.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `sculpted_organic` | forked_anchor (origin) | `rec_use-...0c6efacc` | L116-L168, L206-L379 | eligible | LoftGeometry superellipse torso (pelvis/waist/chest rings) + tapered LatheGeometry limbs + lofted foot wedge, matte body. **Macro Surface Construction** (blended anatomical lofts). |
| `barrel_torso` | forked_anchor | `rec_mannequin_var_barrel_torso` | L118-L134 | eligible | torso is ONE `torso_barrel` LatheGeometry egg/barrel (single revolve, pelvis->shoulder); limbs stay the tapered-lathe organic idiom. **Volumetric Envelope Form** (single revolved envelope). |
| `turned_wood` | forked_anchor | `rec_mannequin_var_wooden_blocky` | L29-L77, L129-L168, L217-L348 | eligible | classic turned-wood: `turned_barrel` pelvis+chest blocks + `turned_cylinder` waist/neck + `turned_limb` limb cylinders + turned ovoid hands/feet; every segment a Z-revolved lathe. **Volumetric Envelope Form** (lathe-turned solids of revolution). |

`waist` (① within Slot B) and `neck` (② within Slot B) are branches, registered
report-only in `slot_choices`:
- `waist`: `rigid` (single torso part, FIXED to base; origin) vs `jointed`
  (lower `pelvis` FIXED to base + upper `chest` on REVOLUTE `waist_joint` axis Y;
  `rec_mannequin_var_waist_joint` L114-L193). Gated OFF for `barrel_torso` (a
  single revolved egg has no region seam to split; only `sculpted_organic` /
  `turned_wood` split cleanly at the waist ring — documented compatibility gate).
- `neck`: `pitch` (REVOLUTE axis Y, +-neck_range; origin L196-L204) vs `swivel`
  (CONTINUOUS axis Z; `rec_mannequin_var_swivel_neck` L196-L206).

### Slot C：arms (parallel-children on upper torso · ① hand skeleton + ② wrist joint)

Two mirror arm chains (upper_arm -> forearm -> hand), each shoulder/elbow REVOLUTE.
The candidate is the hand skeleton.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `mitten_hands` | forked_anchor (origin) | `rec_use-...0c6efacc` | L265-L291 | eligible | one `hand` part per arm carrying a single `hand_paddle` (loft mitten / turned ovoid) + `wrist_ball`; wrist joint only. |
| `segmented_hands` | forked_anchor | `rec_mannequin_var_segmented_hands` | L64-L76, L285-L362 | eligible | ① each `hand` carries a `palm` block + 4 `{side}_finger_i` parts (REVOLUTE `{side}_knuckle_i`, axis X) + a `{side}_thumb` part (REVOLUTE `{side}_thumb_knuckle`); 10 extra moving parts total. |

`wrist` (② within Slot C) branch, registered report-only: `pitch` (REVOLUTE axis
X, +-wrist_range; origin L283-L291) vs `twist` (CONTINUOUS axis Z;
`rec_mannequin_var_twist_wrists` L285-L290).

硬约束满足：Slot A=3 candidates, Slot B=3 candidates (③ 形态主导, 登记进
`slot_choices`), Slot C=2 candidates（降到 2 的理由：5 星池只有 mitten 与
segmented 两种结构不同的 hand skeleton；无第三种，flagged）。每个 candidate 有
`forked_anchor` + `model.py:Lx-Ly`；无 `world_knowledge_extrapolation` candidate。
legs 全样本恒为 3-link REVOLUTE chain（无结构变体）→ 不设 slot，固定嵌在 body
builder（避免 1-candidate slot）。

## 槽位图（slot graph）

pattern: `mixed` (root base + parallel children + 1 multiplicity)

```
base (root; Slot A stand: lean_rod / center_pole / telescoping_stand; + N casters)
  |  [figure_mount: torso FIXED onto base top, world z ~= 0.07]
  +-- torso / pelvis+chest (Slot B body: sculpted_organic / barrel_torso / turned_wood)
  |        |-- [waist REVOLUTE(Y) if jointed]--> chest
  |        |-- [neck REVOLUTE(Y) | CONTINUOUS(Z)]--> head
  |        +-- [hip REVOLUTE(Y)]--> thigh --[knee REVOLUTE(Y)]--> shin --[ankle REVOLUTE(Y)]--> foot   (x2 legs, on LOWER torso)
  +-- (Slot C arms, parallel children on UPPER torso)
           +-- [shoulder REVOLUTE(Y)]--> upper_arm --[elbow REVOLUTE(Y)]--> forearm --[wrist REVOLUTE(X)|CONTINUOUS(Z)]--> hand
                    +-- [knuckle REVOLUTE(X)]--> finger_i (x4) ; [thumb_knuckle REVOLUTE(Y)]--> thumb   (segmented_hands only)
```

- **slot 顺序 / parent**：`base` 是 root。`body` 与 `arms` 只声明 `downstream`
  接口（re-export base）→ assembler 不发自动 chain joint；各模块用
  `model.get_part(...)` 手动 parent 各自 joint（parallel-children，同
  Tipping_Barrow 惯用）。
- **接口点位**：torso->base FIXED at `figure_mount` (base top). Limb joints
  socket into torso lofts (shoulder x=+-0.205 z=1.49; hip x=+-0.09 z=0.99; neck
  x=0 z=1.63) — captured ball-in-socket, joint origin on the torso ball/loft.
- **跨 slot joint type/axis/range**：base->torso FIXED; waist REVOLUTE(Y,
  -waist_range..+waist_range); neck REVOLUTE(Y,+-neck_range) or CONTINUOUS(Z);
  shoulder REVOLUTE(Y,+-shoulder_range); elbow REVOLUTE(Y,0..elbow_upper); wrist
  REVOLUTE(X,+-wrist_range) or CONTINUOUS(Z); hip/knee/ankle REVOLUTE(Y);
  knuckle/thumb REVOLUTE; telescoping PRISMATIC(Z,0..0.30).
- **互斥/派生**：`barrel_torso` forces `waist=rigid`. `telescoping_stand` is the
  only stand adding a moving part+prismatic. caster layout: N==4 -> square plate
  corners (origin), else circular plate radial ring (caster_count sample).

## 每槽位 Module Emits / Interfaces

### Slot A / module lean_rod | center_pole | telescoping_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (root); `telescoping_stand` also emits `height_rod` | origin L77; tele L106 |
| visuals | `base_plate` (Box square / Cylinder round) + `caster_yoke_i`/`caster_i` (N) + rear support (`lean_rod`+`lean_saddle` / `central_pole` / `outer_sleeve` + height_rod's `inner_rod_member`+`lean_saddle`) | origin L78-L110; center L99-L112; tele L99-L129 |
| internal joints | none / `sleeve_to_rod` PRISMATIC(Z,0..0.30) for telescoping | tele L121-L129 |
| downstream interface | re-export base `figure_mount` (informational; body wires FIXED manually) | — |

### Slot B / module sculpted_organic | barrel_torso | turned_wood
| emits | 描述 | 来源 |
|---|---|---|
| parts | `torso` (rigid) OR `pelvis`+`chest` (jointed); `head`; 2x `{side}_thigh`/`{side}_shin`/`{side}_foot` | origin L116,L179,L298-L350; waist L115-L142 |
| visuals | torso lofts/barrel/turned blocks + `deltoid_{l,r}` + `neck`; head ovoid + chin; per-leg hip/knee/ankle ball + tapered/turned seg + foot | origin L117-L168,L180-L195,L298-L370 |
| internal joints | `base_to_torso` FIXED; `waist_joint` REVOLUTE(Y) if jointed; `neck_joint` REVOLUTE(Y)/CONTINUOUS(Z); 2x `{side}_hip`/`{side}_knee`/`{side}_ankle` REVOLUTE(Y) | origin L169-L204,L314-L378; waist L169-L193 |
| upstream interface | **none declared** (parallel-children; FIXES torso to base manually) | — |
| downstream interface | re-export base (passthrough) | — |

### Slot C / module mitten_hands | segmented_hands
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2x `{side}_upper_arm`/`{side}_forearm`/`{side}_hand`; segmented adds 2x(`{side}_finger_0..3`+`{side}_thumb`) | origin L211-L265; seg L305-L362 |
| visuals | shoulder/elbow/wrist ball + tapered/turned seg; hand paddle (mitten) or palm+finger segs (segmented) | origin L213-L282; seg L285-L362 |
| internal joints | 2x `{side}_shoulder`/`{side}_elbow` REVOLUTE(Y) + `{side}_wrist` REVOLUTE(X)/CONTINUOUS(Z); segmented adds 4x `{side}_knuckle_i` + `{side}_thumb_knuckle` REVOLUTE | origin L227-L291; seg L305-L362 |
| upstream interface | **none declared** (parallel-children; parents shoulders to upper torso) | — |
| downstream interface | re-export base (passthrough) | — |

活动件语义：每个 ball joint 让肢体摆动/弯曲；waist bend 前俯；neck pitch/swivel；
wrist pitch/twist；finger/thumb 屈曲；telescoping 升降。不动细节（casters / plate /
lean_rod / deltoid caps / joint balls）写成宿主 part visual（Rule 1）。ball-in-socket
嵌入用 element-scoped allow_overlap（Rule 2 captured-pivot 例外，与全部 5 星源一致）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `stand_module` | enum | lean_rod / center_pole / telescoping_stand | lean_rod | choice | procedural sampler | Slot A |
| `body_form` | enum | sculpted_organic / barrel_torso / turned_wood | sculpted_organic | choice | procedural sampler | Slot B |
| `hand_module` | enum | mitten_hands / segmented_hands | mitten_hands | choice | procedural sampler | Slot C |
| `waist_jointed` | bool | {False, True} | False | conditional | forced False iff `body_form==barrel_torso` | waist L169-L193 |
| `neck_mode` | enum | pitch / swivel | pitch | choice | procedural sampler | swivel L196-L206 |
| `wrist_mode` | enum | pitch / twist | pitch | choice | procedural sampler | twist L285-L290 |
| `caster_count` | int | {3,4,5,6} (obs: 4 origin, 5 caster_count) | 4 | independent | weighted; N==4 square-corner else circular-radial | origin L84, caster L28,L108-L112 |
| `palette_style` | enum | 6 colorways | matte_black | choice | procedural sampler | origin L70-L72, wooden L86 |
| `arm_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform, clamp; upper/forearm seg length + elbow/wrist joint offsets co-derive | origin L219-L263 |
| `leg_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform, clamp; thigh/shin seg length + knee/ankle joint offsets co-derive | origin L306-L378 |
| `shoulder_range` | float | [2.2, 2.9] | 2.8 | independent | shoulder REVOLUTE +- range (rad) | origin L234-L236 |
| `elbow_upper` | float | [2.2, 2.7] | 2.6 | independent | elbow REVOLUTE upper (rad) | origin L262 |
| `hip_upper` | float | [1.5, 2.0] | 1.8 | independent | hip REVOLUTE upper (rad) | origin L321 |
| `knee_upper` | float | [1.9, 2.4] | 2.2 | independent | knee REVOLUTE upper (rad) | origin L347 |
| `waist_range` | float | [0.4, 0.8] | 0.6 | conditional | waist REVOLUTE +-; only if waist_jointed | waist L193 |
| `neck_range` | float | [0.6, 0.9] | 0.8 | conditional | neck REVOLUTE +-; only if neck_mode==pitch | origin L203 |
| `wrist_range` | float | [0.8, 1.2] | 1.0 | conditional | wrist REVOLUTE +-; only if wrist_mode==pitch | origin L290 |
| (—) | constraint | — | — | inequality | knee/elbow/hip ranges physically clear when a single joint is swept (relations solved by keeping the ball-in-socket allow_overlap element-scoped; adjacent limb sweep contacts declared, see Multiplicity) | origin run_tests |

所有 equation/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 20 s** (hang-guard `--compile-timeout 60`). Geometry
is many small LatheGeometry / LoftGeometry solids of revolution (torso lofts,
limb lathes, head ovoid, feet, turned-wood blocks) plus Spheres/Cylinders/Boxes;
no boolean sculpting. The origin record compiles clean at ~19 parts; the worst
case (`segmented_hands` + `waist_jointed` + `telescoping_stand`) is ~30 parts.
Tessellation tiers: lathe/loft profiles 20-28 segments (default), head/torso hero
lathes <=28, small joint balls default Sphere. Both mirror sides reuse identical
profile helpers; all N casters reuse two cylinder primitives. Expect 5-14 s/seed;
downgrade lathe `segments` first if over.

## Multiplicity / Copy Logic

**一根独立 multiplicity 轴**：

### 轴 1 — `caster_count`（滚轮数量）
- `count_param`: `caster_count`; `N_range` product `[3,6]`, test `{3,4,5,6}`;
  sampling domain 加权：`{4: 0.4, 3: 0.2, 5: 0.2, 6: 0.2}`（N=4 origin 母本偏多）。
- copied object: a `caster_yoke_i` cylinder + `caster_i` cylinder pair (base part
  visuals; static decoration, NOT parts — Rule 1). N==4 -> square plate at 4
  corners `(+-0.16,+-0.16)` (origin); else circular plate, casters on a radial
  ring `angle=2*pi*i/N` at radius 0.16 (caster_count sample).
- naming: `caster_yoke_{i}` / `caster_{i}`. placement: corners or radial ring.
  joint policy: none (fixed base visuals).
- source/gating: origin (N=4, square) L84-L98; caster_count (N=5, radial)
  L28,L99-L112.
- 数量变化不改主体形态/机制（figure identical）。

（腿数、臂数恒为 2，指数恒为 4+拇指——不暴露为可变 multiplicity 轴，样本无变体。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构骨架 candidate：waist rigid（origin, forked_anchor，单 torso）↔ waist jointed（waist_joint, forked_anchor，pelvis+chest+waist REVOLUTE 多一 part/edge）；hands mitten（origin）↔ segmented（segmented_hands, forked_anchor，+10 finger/thumb part + 10 knuckle REVOLUTE）；stand lean_rod（origin）↔ center_pole（center_pole_mount）↔ telescoping（telescoping_stand, forked_anchor，+height_rod part + PRISMATIC edge）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：caster_count {3,4,5,6}（origin N=4 / caster_count N=5）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | neck REVOLUTE(Y)（origin）↔ CONTINUOUS(Z)（swivel_neck）；wrist REVOLUTE(X)（origin）↔ CONTINUOUS(Z)（twist_wrists）；stand adds PRISMATIC(Z)（telescoping_stand）。全部 forked_anchor；每种类型都在 sweep 出现。 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices**（body_form slot，3 candidates）：sculpted_organic（origin，Macro Surface Construction — blended anatomical lofts）/ barrel_torso（barrel_torso，Volumetric Envelope Form — 单一 revolve egg）/ turned_wood（wooden_blocky，Volumetric Envelope Form — lathe-turned solids of revolution）。均 forked_anchor。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `deltoid_{l,r}` 肩帽 sphere、visible joint balls（shoulder/elbow/wrist/hip/knee/ankle/knuckle）、casters、`lean_saddle` — 均为宿主 part visual，随 ③（wood/organic material）/⑤（arm_scale/leg_scale/figure 尺寸）派生位置。source_type=record_only（origin/wooden/caster_count）。装饰数量档 = caster_count（见 §8）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：arm_scale/leg_scale [0.90,1.12]。关节运动包络（每个非-continuous joint）：shoulder REVOLUTE(Y) [闭合 0, +-shoulder_range<=2.9]；elbow REVOLUTE(Y) [0, elbow_upper<=2.7]；wrist REVOLUTE(X) [0, +-wrist_range<=1.2]；hip REVOLUTE(Y) [-0.6, hip_upper<=2.0]；knee REVOLUTE(Y) [0, knee_upper<=2.4]；ankle REVOLUTE(Y) [+-0.6]；neck REVOLUTE(Y) [+-neck_range<=0.9]；waist REVOLUTE(Y) [+-waist_range<=0.8]；knuckle/thumb REVOLUTE [0, ~1.4]；telescoping PRISMATIC(Z) [0, 0.30]。**`motion_test_plan` — sampled-pose exemption**（见下）+ targeted `ctx.pose(...)`：neck turn、shoulder fold、elbow bend、wrist twist、hip swing、knee bend、waist bend、finger curl、telescoping raise 各一。continuous(neck/wrist swivel) 采 {0,+-90,180}。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/plastic + wood(painted) + metal(stand steel) + glass(base)。配色 >=6 colorway：`matte_black`（原母本）、`artist_wood`（浅木）、`walnut_wood`（深木）、`porcelain_white`、`slate_gray`、`terracotta`。材质大类覆盖 >= ceil(0.5x6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 sculpted/barrel/turned-wood 三种 body、mitten
与 segmented 两种手、lean_rod/center_pole/telescoping 三种 stand、材质配色多样、
每个 targeted pose 语义正确、rest pose 无非预期穿模。

**sampled-pose exemption（Rule 5）**：本类别是**可摆姿人偶**，其关节被**设计成**
可摆到肢体互相/与躯干接触的姿态（手抬到下巴、双臂交叉抱胸、屈膝抱腿等——真实玩具
即如此）。对 12-24 个自由度做 blanket `fail_if_parts_overlap_in_sampled_poses` 会
把这些**合法摆姿接触**误报为穿模，与类别语义相悖。故模板 run_tests **不调**
blanket sampled-pose 门，改用：(a) element-scoped `allow_overlap` 声明全部
ball-in-socket 嵌入 + 相邻肢段在摆姿时的合法扫掠接触（compiler 默认 harness_motion_qc
会读取这些 allowance 并在每个采样姿态生效）；(b) 每个机构一条 targeted
`ctx.pose(...)` 断言预期位移/方向（rest pose 干净 + 语义可测）。关节行程保持源样本
真实值，不为过门而缩程。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- stand 3 x body_form 3 x waist(2, barrel 只 1) x neck 2 x hands 2 x wrist 2 x caster(4)
  ~= 3 x (3 form x ~1.7 waist avg) x 2 x 2 x 2 x 4 ~= **>= 490** distinct tuples。
  （report-only；不硬凑。）

理由：>300，结构词汇丰富（多根独立离散轴）。不反推上游变体数量。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 stand_module、body_form、hand_module、neck_mode、wrist_mode、waist_jointed
（barrel 时强制 rigid）、caster_count（加权）、palette_style、连续 scale + joint
ranges。seed 0 pinned 到 origin 母本组合（lean_rod + sculpted_organic + mitten +
rigid + neck pitch + wrist pitch + 4 casters + matte_black）作为 documented
regression anchor（sparse override，其余 seed 全 procedural）。random sweep
`0-15`（fast）->`0-35`（final）-> corner。

Topology target：真实上界 >= 490（见上），report-only。

Controlled local parameterization：`arm_scale`、`leg_scale`（各自 clamp，肢段长度
与其子关节偏移在同一 builder 内 co-derive，Contract 3e）；joint-range bands
（shoulder/elbow/hip/knee/waist/neck/wrist）在 `resolve_config` clamp。全部不破坏
ball-socket 接口、joint 原点、caster multiplicity。连续尺寸契约：先采 independent
scale/ranges -> conditional 解析（waist/neck/wrist range 依 mode/jointed）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 stand->body->hands，加权 caster；neck/wrist/waist 独立抽 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | barrel_torso -> waist rigid（gate）；telescoping 唯一 prismatic stand；caster N==4 方板角 else 圆板环 | 无 floating / 非预期 collision / 轴错误 / max-N |
| controlled local variation | arm_scale/leg_scale + 7 joint-range bands | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | >=2 | >=3 | 备注 |
|---|---:|---|---|---|
| stand | 3 | yes | yes | lean_rod/center_pole/telescoping |
| body_form | 3 | yes | yes | sculpted/barrel/turned_wood（③ 登记） |
| arms(hands) | 2 | yes | no | 池内仅 mitten/segmented 两种手骨架，无第三 |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ waist/neck/wrist/caster axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (barrel->rigid waist) in `resolve_config`
- controlled local scales/ranges clamped; cannot break ball-socket interfaces, joint origin honesty, or caster multiplicity
- conditional ranges (waist/neck/wrist) resolved in `resolve_config`, not left to fail in builder
- captured ball-in-socket + posing-sweep overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: base_to_torso FIXED; waist/neck/shoulder/elbow/hip/knee/ankle REVOLUTE(Y) (wrist REVOLUTE X); neck/wrist CONTINUOUS(Z) when swivel/twist; telescoping PRISMATIC(Z)
- copied `caster_i` follow naming + placement policy
- `run_..._tests` declares the sampled-pose exemption + >=1 targeted `ctx.pose` per mechanism (Rule 5)

## Reject cases

- Any limb segment resting deeply inside the torso at REST pose (q=0) that is not a real ball-in-socket seat -> fix the joint origin / seat, do not blanket-allow.
- Downgrading LoftGeometry / LatheGeometry sculpted body to crude Box/Cylinder placeholders (Rule 3 violation) — turned_wood must stay lathe, organic must stay loft/lathe.
- A non-moving caster / lean-rod / pole spawned as a FIXED-joint part instead of a base visual (Rule 1).
- barrel_torso split at a waist joint (no clean region seam) -> gate barrel to rigid.
- Head/hand/limb floating off its parent (island): every joint ball must seat into the parent's ball/loft (element-scoped allow_overlap) or contact it.
- telescoping height_rod colliding the base or torso through its full 0..0.30 travel -> keep saddle clear; declare only the sleeve<->rod captured-slide overlap.
- Widening a joint range past the source value to look more articulated (dilutes / breaks clearance).

## 与相邻类别的边界

- 不该混入：**action figure / poseable toy**（有面部/服装/配件细节；manikin 是无特征哑光或素木）。
- 不该混入：**tailor's dress form / bust**（无四肢，单一躯干立于杆上；manikin 是全关节肢体树）。
- 不该混入：**robot / android / humanoid mechanism**（机械硬件外形；manikin 是有机渐细比例 + 可见球关节）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot C (arms/hands) 只有 2 candidates（池内仅 mitten/segmented），已按硬约束说明降级理由。Rule 5 采用 sampled-pose exemption（可摆姿人偶语义），靠 element-scoped allow_overlap + targeted ctx.pose；待人工 viewer 目检确认摆姿全程无非预期穿模。 |

## 模板实现备注（可选）

- torso 上/下段由 `_upper_torso_part` / `_lower_torso_part` helper 单一来源（rigid 时同一 `torso` part；jointed 时 chest/pelvis），arms/head parent 到 upper，legs parent 到 lower（Contract 3c）。
- body_form 决定 mesh idiom + limb 构造 helper（loft/lathe organic vs 单 barrel lathe vs turned-wood lathe）；palette 独立控制颜色（decoupled，wood mesh 可配任意色）。
- ball-in-socket / posing-sweep overlap 全部 element-scoped `allow_overlap`（Rule 2 例外），与全部 5 星源一致。
- 两侧肢体共享 profile helper；N casters 共享 cylinder 原语 —— 保编译预算。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：base root 声明 downstream；body/arms 只声明 downstream（re-export base）-> 无自动 chain joint，各模块手动发 joint（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | lean_rod + sculpted_organic + mitten_hands | `rec_use-...0c6efacc` (origin 母本) | L64-L497 | base + 4 casters + lean_rod, loft/lathe organic body + 12 REVOLUTE limb tree, mitten hand, all test semantics |
| S2 | B ③ | barrel_torso | `rec_mannequin_var_barrel_torso` | L118-L134 | single revolved barrel torso (Volumetric Envelope) |
| S3 | B ③ | turned_wood | `rec_mannequin_var_wooden_blocky` | L29-L77,L129-L348 | turned-wood lathe idiom (turned_barrel/cylinder/limb) + wood palette |
| S4 | A mult | caster_count | `rec_mannequin_var_caster_count` | L24-L31,L99-L112 | N radial casters + circular plate |
| S5 | A ① | center_pole | `rec_mannequin_var_center_pole_mount` | L99-L112 | central pole-through-hip mount |
| S6 | A ①/② | telescoping_stand | `rec_mannequin_var_telescoping_stand` | L99-L129 | outer sleeve + height_rod part + PRISMATIC |
| S7 | C ① | segmented_hands | `rec_mannequin_var_segmented_hands` | L64-L76,L285-L362 | 4 fingers + thumb parts + REVOLUTE knuckles |
| S8 | B ② | swivel_neck | `rec_mannequin_var_swivel_neck` | L196-L206 | neck CONTINUOUS(Z) swivel |
| S9 | C ② | twist_wrists | `rec_mannequin_var_twist_wrists` | L285-L290 | wrist CONTINUOUS(Z) twist |
| S10 | B ① | waist_joint | `rec_mannequin_var_waist_joint` | L114-L193 | torso split pelvis+chest + REVOLUTE waist |
</content>
</invoke>
