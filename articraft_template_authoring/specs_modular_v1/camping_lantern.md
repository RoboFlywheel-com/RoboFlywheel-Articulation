# Camping Lantern — modular spec (specs_modular_v1/camping_lantern.md)

## 元信息
| 项 | 值 |
|---|---|
| slug | `camping_lantern` |
| template path | `agent/templates/camping_lantern.py` |
| test path (optional) | `tests/agent/test_camping_lantern_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (base→body linear seat/slide chain + parallel-children grip + leg / cage-bar multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | all 5-star ids in `spec5star/camping_lantern.txt` (2 origin anchors + 14 forked variants) |
| source_index_policy | only adopted module sources indexed below |

Two structural families across the pool:

- **Canister family** (origin `9f7633a6`): parts `lower_base` (ribbed canister) → `upper_lantern`
  (clear chamber + LED board + stepped cap) → `wire_handle` (fold-up bail). Joints
  `base_to_lantern_slide` PRISMATIC (telescope) or `base_to_lantern_seat` FIXED (forks),
  `lantern_to_handle_hinge` REVOLUTE. Body forks: orb globe (Sphere), flat puck disc, slim tube.
  Base forks: ground stake, magnetic disc. Motion fork: accordion bellows (PRISMATIC).
- **Cage/tripod family** (origin `c2bd28cb`): one big `lantern_body` (warm diffuser + wire-cage lattice +
  vented base + top vent cap + control block) with parallel children `carry_bail` REVOLUTE and
  `leg_0..2` REVOLUTE ×3. Body forks: barn/hurricane lathe globe, rectangular cadquery box + flat panels.
  Multiplicity forks: 4 legs (quadpod), 12 cage bars. Grip fork: single J top-hook. Motion forks:
  twist base cap (REVOLUTE z), hinged guard door (REVOLUTE z).

The template unifies both as: one grounded `lower_base` part (the ① skeleton, incl. fold-out legs) →
one `upper_lantern` light-chamber part (the ③ Primary Form Family, seated/telescoped on the base) →
one swinging `carry_handle` grip part (the ② handle). Cage bars are inline body visuals; legs are FIXED-hub
REVOLUTE children of the base.

## 核心身份

A **portable, self-contained battery/LED area lantern** for a campsite: a diffusing/glowing light body
(clear chamber, wire-cage + diffuser, globe, panel box, disc, or tube), a way to carry/hang or stand it
(canister base, tripod legs, ground stake, magnetic disc), and at least one real non-fixed joint
(fold-up bail/hook/loop, fold-out legs, or telescoping collapse). Default mature domain: compact hand-carry
lanterns ~0.10–0.17 m body height, satin-black / olive-steel / brass / frosted colorways with a warm LED core.

Must NOT drift into: handheld flashlight/torch (end-emitting, no area diffuser + hang/stand); fixed
pendant/ceiling fixture or table lamp (not portable); live-wick oil lamp / gas-mantle burner / tiki torch /
chemical glow-stick (`Light/Latern` neighbor); non-lighting cylinder (thermos, speaker, bottle).

## 槽位 + 候选模块表

### Slot A：base （① 骨架 / 支撑 + base-motion ②）

Root, grounded. Owns the ① support skeleton and the base↔body attachment joint (② prismatic-vs-fixed).
Emits `body_seat_rim` (top face the light body seats on) + base geometry; `tripod` additionally emits N
fold-out leg parts (REVOLUTE, the leg multiplicity axis).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `canister_telescope` | origin_anchor | rec `9f7633a6` | model.py:L67-L120, L291-L299 | eligible if compatible | ribbed lathe canister shell + grip ribs + foot lugs; body attaches via PRISMATIC telescope slide (axis z) |
| `canister_seat` | forked_anchor | rec `..._var_orb_globe_body` / `..._panel_puck_body` | orb model.py:L73-L126, L303-L309 | eligible if compatible | same ribbed canister; body attaches via FIXED seat (no telescope) |
| `ground_stake` | forked_anchor | rec `..._var_ground_stake_base` | model.py:L73-L101, L270-L276 | eligible if compatible | long pointed lathe spike + cylindrical hub + seating flange; FIXED seat |
| `magnetic_disc` | forked_anchor | rec `..._var_magnetic_clip_base` | model.py:L73-L142, L382-L388 | eligible if compatible | thin magnetic puck disc + contact ring + anti-slip pad; FIXED seat (moving clip omitted to bound joint count) |
| `tripod` | origin_anchor | rec `c2bd28cb` | model.py:L244-L294, L312-L336 | eligible if compatible | short vented hub + N fold-out wire legs (REVOLUTE per leg); FIXED seat. **legs = multiplicity axis** |

### Slot B：body （③ 主体形态家族 / Primary Form Family）

Seated/telescoped onto Slot A's `body_seat_rim`. Builds in a seat-relative frame (z=0 = seat plane, extends
+z). Emits `body_seat` (bottom seat face), the light chamber/diffuser, a warm LED core assembly bridged to
collar+cap (no island), a top cap, and grip-mount hardware at the resolved `body_top_z`.

| module_name | source_type | form_subtype | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|---|
| `cylinder_chamber` | origin_anchor | Volumetric Envelope Form | rec `9f7633a6` | model.py:L122-L257 | clear LatheGeometry cylindrical tube chamber + 4 clear posts + LED board/lens dots + stepped cap |
| `cage_diffuser` | origin_anchor | Macro Surface Construction | rec `c2bd28cb` | model.py:L84-L123, L223-L273 | warm Cylinder diffuser + `_lantern_cage_mesh` guard lattice (**cage-bar multiplicity**) + vented base + top vent cap + control block |
| `barn_globe` | forked_anchor | Volumetric Envelope Form | rec `..._var_barn_globe_body` | model.py:L28-L48, L124-L153 | bulged barn/hurricane LatheGeometry glass globe + vented base + peaked cap |
| `orb_globe` | forked_anchor | Volumetric Envelope Form | rec `..._var_orb_globe_body` | model.py:L170-L233 | frosted `Sphere` orb diffuser captured between collar and stepped cap |
| `box_panel` | forked_anchor | Planar Boundary Form | rec `..._var_box_fixture_body` | model.py:L44-L210 | cadquery rectangular housing frame + 4 flat translucent panels + squared base/cap |
| `puck_disc` | forked_anchor | Planar Boundary Form | rec `..._var_panel_puck_body` | model.py:L126-L236 | short wide diffuser disc + downward COB panel + puck shell + low cap |
| `slim_tube` | forked_anchor | Volumetric Envelope Form | rec `..._var_stick_tube_body` | model.py:L128-L279 | tall thin LatheGeometry tube column (H:D ≈ 5:1) + carrier spine + LED strip + slim cap |

### Slot C：grip （② handle / 提挂）

Parallel child of `upper_lantern` (reads the resolved body top/side mount point). One REVOLUTE captured-pin
pivot (grandfathered, element-scoped `allow_overlap`). Body-side bosses/axle are inline `upper_lantern` visuals.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fold_bail` | origin_anchor | rec `9f7633a6` / `c2bd28cb` | 9f model.py:L259-L310 | eligible if compatible | fold-up U-shaped wire bail over top cap; REVOLUTE axis x |
| `top_hook` | forked_anchor | rec `..._var_fixed_top_hook` | model.py:L185-L314 | eligible if compatible | single J-hook that pivots up from cap-center pivot boss; REVOLUTE axis y |
| `side_loop` | forked_anchor | rec `..._var_side_carry_loop` | model.py:L257-L328 | eligible if compatible | side-pivoting carry loop on the body +Y sidewall + rubber grip sleeve; REVOLUTE axis x |

硬约束满足：Slot A 5 候选（≥3），Slot B 7 候选（≥3，③ 形态主导），Slot C 3 候选（≥3）。每个候选结构不同
（part tree / primitive family / interface / joint 或可识别 ③ 原型不同），均有真实 `model.py:Lx-Ly` 来源。

## 槽位图（slot graph）

pattern: `mixed`

```
lower_base (root, grounded)
  --[base_to_lantern  (FIXED seat | PRISMATIC slide axis z) + MatingContract
        parent body_seat_rim(+z) ↔ child body_seat(−z)]-->  upper_lantern
        --[lantern_to_grip (REVOLUTE, captured-pin, grandfathered) ]-->  carry_handle
  --[base_to_leg_i (REVOLUTE axis ≈ −y, ×N)  (only when base=tripod) ]-->  leg_i
```

- Slot order: base (root) → body (seat/slide chain child) → grip (parallel child of body).
- Interfaces: base exposes `body_seat_rim` top face at world z=`base_top_z`; body builds `body_seat` at
  part z=0 (negative_z face) so the two coincide at the joint origin `(0,0,base_top_z)`.
- Cross-slot joint types: base→body FIXED (all except `canister_telescope`) or PRISMATIC z (telescope);
  body→grip REVOLUTE (captured-pin, no MatingContract); base→leg REVOLUTE (captured-pin) when tripod.
- Mutually exclusive / derived: legs exist only for `tripod`; cage bars exist only for `cage_diffuser`;
  the grip mount point is derived from the chosen body module (single-sourced in `resolve_config`).

## 每槽位 Module Emits / Interfaces

### Slot A / base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_base` (+ `leg_0..N-1` for tripod) | 9f L67 / c2bd28cb L316 |
| internal joints | tripod: `base_to_leg_i` REVOLUTE axis (0,−1,0) rot z by angle, range [0,1.25] | c2bd28cb L328-L336 |
| downstream interface | `body_seat_rim` top ring, positive_z face at `base_top_z`; consumer joint FIXED or PRISMATIC(z) | 9f L291 / orb L303 |

### Slot B / body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_lantern` | 9f L122 / c2bd28cb L223 |
| internal joints | none (all body detail is inline visuals — Rule 1) | — |
| upstream interface | `body_seat` bottom seat ring, negative_z at part z=0 | 9f L134 / orb L134 |
| downstream interface | resolved `body_top_z` / `body_side` grip-mount datum (used by Slot C) + inline grip bosses | 9f L250 / side L257 |

### Slot C / grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carry_handle` (bail wire / J-hook / side loop) | 9f L259 / hook L300 / side L270 |
| internal joints | `lantern_to_grip` REVOLUTE (axis x for bail/side, y for hook); captured-pin, grandfathered | 9f L301 |
| upstream interface | REVOLUTE origin at body grip datum; body-side bosses/axle are `upper_lantern` inline visuals | 9f L250 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_style` | enum | canister_telescope / canister_seat / ground_stake / magnetic_disc / tripod | canister_seat | choice | procedural rng.choice; gated | Slot A |
| `body_style` | enum | cylinder_chamber / cage_diffuser / barn_globe / orb_globe / box_panel / puck_disc / slim_tube | cylinder_chamber | choice | procedural rng.choice; gated | Slot B |
| `grip_style` | enum | fold_bail / top_hook / side_loop | fold_bail | choice | procedural rng.choice; gated | Slot C |
| `palette_style` | enum | graphite_black / olive_steel / vintage_brass / frosted_white / sand_tan / anodized_orange | graphite_black | choice | procedural rng.choice | ⑥ across pool |
| `leg_count` | int | [3,4] | 3 | conditional | active only if base=tripod; clamp [3,4] | c2bd28cb / quadpod |
| `cage_bar_count` | int | [8,16] | 8 | conditional | active only if body=cage_diffuser; clamp [8,16] | c2bd28cb / n12 |
| `body_height_scale` | float | [0.88,1.15] | 1.0 | independent | uniform then clamp; scales chamber height | 9f ⑤ |
| `body_radius_scale` | float | [0.90,1.12] | 1.0 | independent | uniform then clamp; scales body radius | 9f ⑤ |
| `base_height_scale` | float | [0.85,1.15] | 1.0 | independent | uniform then clamp; scales base/hub height | 9f ⑤ |
| (—) | constraint | — | — | conditional | `base_style==canister_telescope ∧ body_style==box_panel` → base→canister_seat (square won't slide round bore) | 接口 |
| (—) | constraint | — | — | conditional | `grip_style==side_loop ∧ body_style==puck_disc` → grip→fold_bail (flat puck has no tall sidewall) | 接口 |
| (—) | constraint | — | — | equation | `body_top_z`, `body_seat_radius`, `body_side_y/z` = f(body_style, scales); single-sourced in resolve_config | Contract 3c |

连续尺寸采样契约：先采 independent scales (body/base) → 派生几何 datum (equation) → conditional gates
(base/grip 重定向、leg/cage counts) 在 resolve_config 内求解，不留到 builder。

### 7.5 编译预算 / compile budget（必填）

**≤ 12 s/seed** 目标（sweep `--compile-timeout 120` 仅作 watchdog）。依据：主体多为 LatheGeometry 旋转壳
（segments ≤ 72）+ 少量 Sphere/Cylinder/Box + 一个 `tube_from_spline` 提梁；最重的是 `cage_diffuser`
的角向 lattice（angular n = 72，7 个 z 段）与 `box_panel` 的一次 cadquery union（8 posts + rails，
tolerance 0.0004）。分档 tessellation：旋转壳 segments 64–72，small 特征 ≤ 24；N 根同构腿复用同一个
`Mesh`（`.copy()`）；cage 用单一 mesh。超预算先降 segments 再迭代。

## Multiplicity / Copy Logic

两根独立 multiplicity 轴，各自加权采样、各自编入 `slot_choices`、各自 clamp。

- **legs 轴**（axis 1，仅 base=tripod）
  - `count_param` = `leg_count`; `N_range` = [3,4]（物理稳定：三脚/四脚；>4 罕见，排除）；sampling domain:
    3 高频、4 较少。
  - copied object = fold-out wire leg (`tube_from_spline` mesh + `hinge_pin` Cylinder); naming `leg_i` /
    `leg_socket_i`; placement 径向等分 `TAU*i/N + π/6`; joint policy 每腿一个 `base_to_leg_i` REVOLUTE
    (同 axis (0,−1,0) rot z，同 range [0,1.25])；captured-pin，element-scoped `allow_overlap`。
    source/gating: rec `c2bd28cb` L313-L336 / quadpod fork。
- **cage bars 轴**（axis 2，仅 body=cage_diffuser）
  - `count_param` = `cage_bar_count`; `N_range` = [8,16]（源 8→12；<8 露光、>16 过密，排除）；sampling
    domain: 8/10/12 高频、14/16 稀有。
  - copied object = 一根竖直 guard-bar column（在单一 `_lantern_cage_mesh` 内按角向索引生成，非独立 part/joint）；
    placement 角向等分；joint policy 无关节（inline body visual，Rule 1）。source/gating: rec `c2bd28cb`
    `_lantern_cage_mesh` L84-L123 / n12 fork。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 支撑骨架 4 种 + 腿轴：canister（sitting，o1）、tripod（fold-out legs REVOLUTE ×N，o2）、ground_stake（forked）、magnetic_disc（forked）。均 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：legs [3,4]；cage bars [8,16]。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | PRISMATIC z（canister_telescope, o1）、FIXED seat（canister_seat/stake/disc/tripod, forks）、REVOLUTE x/y（bail o1/o2 · hook fork · side_loop fork · legs o2）。声明的 PRISMATIC/FIXED/REVOLUTE 都在 sweep 出现。twist-cap continuous / hinged-door 为 forked_anchor，但为 bound joint-count/compat 风险本版 defer（见 §13），已由 3 种核心 joint type 覆盖 ②。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别几何原型 | 有 | 7 candidate（登记进 slot_choices）：cylinder_chamber（Volumetric Envelope）、cage_diffuser（Macro Surface Construction）、barn_globe（Volumetric Envelope）、orb_globe（Volumetric Envelope）、box_panel（Planar Boundary）、puck_disc（Planar Boundary）、slim_tube（Volumetric Envelope）。source-backed origin+forked。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 (record_only + world_knowledge_extrapolation) | grip ribs / castellated foot lugs / cap tabs / brand stroke / LED lens dot arrays / control block（源）；host-conformal，随 ③⑤ 派生（vertical ribs 贴 canister 半径、cap tabs 贴 cap 半径）。派生顺序 ③→⑤→④。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | body_height_scale [0.88,1.15]、body_radius_scale [0.90,1.12]、base_height_scale [0.85,1.15]（§7）。关节运动包络：base_to_lantern PRISMATIC z [0, 0.070]（telescope 抬升，向上，闭合=0）；lantern_to_grip REVOLUTE：bail x [−1.45,0.20]、hook y [0,1.50]、side_loop x [0,1.40]；base_to_leg_i REVOLUTE ≈−y [0,1.25]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses` + 每机构 targeted `ctx.pose`（bail 折下、hook 前折、side_loop 外摆、telescope 抬升、legs 下折）；captured-pin 用 element-scoped allow_overlap，全程不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：painted/plastic（graphite_black, sand_tan）、metal（olive_steel, vintage_brass, anodized_orange）、frosted glass/plastic diffuser（frosted_white + 每 palette 的 translucent diffuser，alpha<0.5）。配色 6 档（≥3-6），材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：`template batch` 0-9 seed 须肉眼可见：7 种 ③ 形态拉开、6 palette 材质大类都出现、装饰贴合宿主面、
bail/hook/loop/legs/telescope 各自机构全程不穿模。

## 采样与覆盖审计

总组合数：base 5 × body 7 × grip 3 = 105 discrete；× legs(2) [仅 tripod] × cage_bars(≈5) [仅 cage] +
3 连续 scale → 有效离散拓扑 > 300。

理由：形态主导小类，③ 7 候选承载主多样性；① 4 骨架 + 2 multiplicity 轴 + ② 3 joint types 补足。

seed_domain_policy：procedural_first（seed 0 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采样
base_style / body_style / grip_style / palette_style / leg_count / cage_bar_count / 3 scales；
`resolve_config` 内执行 compatibility gating（canister_telescope+box_panel→canister_seat；
side_loop+puck_disc→fold_bail），派生 grip mount datum，clamp counts/scales。无 curated/modulo 主表；
无 regression override（如后续锁回归再加，注明 seed+理由）。random sweep 0-35 初判，0-999 成熟度目检。
Topology target：>300（富类别）。

Controlled local parameterization：body_height_scale / body_radius_scale / base_height_scale
（范围见 §7，resolve_config 内 clamp/derive），不破坏 seat MatingContract / grip datum / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 base→body→grip；weighted counts；compat gates in resolve_config | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | telescope+box→seat；side_loop+puck→bail；legs↔tripod；cage_bars↔cage_diffuser | 无 floating / collision / 非法 telescope / 空 multiplicity |
| controlled local variation | 3 连续 scale + clamp | 比例变化不破 interface / clearance / joint origin / 类别 identity |
| regression overrides | none | — |
| random sweep | 0-35 初判，0-999 成熟度 | contract failures；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base | 5 | yes | yes | |
| body | 7 | yes | yes | ③ 主体形态家族 |
| grip | 3 | yes | yes | |

## Validator

- slot_choices_for_seed returns implemented module names (base/body/grip + leg_n / cage_n tokens)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds incl. seed 0
- compatibility gating prevents telescope+box and side_loop+puck; legs/cage counts gated by slot
- no regression override cycling
- local scales clamped; cannot break seat MatingContract, grip datum, or multiplicity
- cross-part datums (grip mount, seat z) resolved in resolve_config, not builder
- base_to_lantern joint declares a MatingContract (`body_seat_rim`+z ↔ `body_seat`−z); grip/leg captured-pins grandfathered with element-scoped allow_overlap
- key joints have expected type/axis/range (see §8.5 ⑤)
- copied legs/bars follow naming + radial placement policy

## Reject cases

- body downgraded to Box/Cylinder where source uses LatheGeometry / Sphere / cadquery (Rule 3 violation)
- LED / diffuser core floating as an island inside `upper_lantern` (no collar↔cap bridge)
- telescope base with square box body (square won't slide the round bore)
- grip/leg joint with no captured-pin allowance AND no MatingContract → mating-gap or overlap fail
- fold-up bail/hook/loop/telescope/legs that clip the body mid-travel (sampled-pose overlap)
- monochrome output (palette_style not driving every `.visual` material)
- drift to flashlight / pendant fixture / live-wick oil lamp / thermos

## 与相邻类别的边界

- 不该混入：Light/Latern（live-wick 煤油/飓风灯，有火焰+wick knob；本类是电池/LED，无燃烧件）
- 不该混入：Technology/Flashlight（端射手电，无面漫射+提挂/站立）
- 不该混入：Facade/Lamp1 / ceiling_light_fixture（固定吊/顶灯，非便携营地装备）
- 不该混入：Container（thermos/bottle/speaker 圆柱，无发光漫射体）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 16 5-star sources (2 origin anchors + 14 forks); mixed base→body→grip + 2 multiplicity axes |

## 模板实现备注（可选）

- 共享 helper：`_ring_profile_mesh`（LatheGeometry.from_shell_profiles 壳）、`_lantern_cage_mesh`
  （cage-bar 轴）、`_bail/_hook/_loop` `tube_from_spline`、box_panel 用 cadquery。
- MatingContract 只在 base→body seat/slide 上；grip 与 legs 是 captured-pin → grandfather + element-scoped
  `allow_overlap`（bail_wire↔bail_ear / hook_wire↔hook_pivot_boss / leg hinge_pin↔leg_socket_i）。
- 单一来源 datum：body 相关 z/半径全部在 `resolve_config` 派生（`body_top_z` 等），body 与 grip 共用。
- 本版 defer：accordion bellows、twist base cap（CONTINUOUS/REVOLUTE z）、hinged guard door —— 为 bound
  joint-count/compat 风险；② 已由 PRISMATIC/FIXED/REVOLUTE 三类覆盖。若后续需要再各起 module 或 slug 拆分。
```
