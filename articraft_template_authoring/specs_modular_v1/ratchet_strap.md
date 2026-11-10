# ratchet_strap — Modular Spec (0611)

## 元信息
| 项 | 值 |
|---|---|
| slug | `ratchet_strap` |
| template path | `agent/templates/ratchet_strap.py` |
| test path (optional) | `tests/agent/test_ratchet_strap_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern` 说明：全部机构件（spool / handle / pawl / release / webbing）都挂到共同的 `frame`
chassis（parallel children），不是串行链。frame 由 ③ 主体形态家族 slot 生成并作为 root。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star retained samples in 0611/ratchet_strap (2 origins + 9 forked variants; the excluded/deleted old-origin `001` lineage is not counted) |
| source_index_policy | only adopted module sources are indexed below |

阅读的 11 条：2 origins（`rec_use-the-attached-image-as-the-primary-and-author_20260711_160740_098181_6a70af39` = 001 stamped twin-cheek；`rec_picturex_0611__ratchet_strap__002__png_8a06b96fc10447be86c17bcba7c52ec4` = 002 U-frame）+ 3 frame_form forks + 5 end_fitting forks（含 gated snap_hook）+ 1 release fork（pull_tab）+ 1 webbing_topology fork（endless_loop）。

**共同机构脊柱（两 origin 都有）**：`frame`（stamped/U-frame chassis）承载一个 captured
**winding spool**（REVOLUTE，axis Y，带 ratchet 齿轮）、一个 coaxial **handle**（REVOLUTE，axis Y）、
一个 **pawl/release** 机构、一条 **webbing** 载荷路径（FIXED 于 frame）。001 额外有独立 `drive_pawl`
（REVOLUTE）、`webbing_roll`（REVOLUTE）、成对金属 J-hook（frame 端 + free-strap 端）、frame 挂载
的 thumb release；002 是更精简的 U-frame，handle 挂载的 finger-paddle release、无 hook 的 loose
feed-through webbing、无 roll。所有 pivot 都是 captured-pin（穿过 cheek 板 / bore），origin 用
element-scoped `allow_overlap` + `expect_contact` 表达，不用 MatingContract（几何非两轴对齐面）。

## 核心身份

cargo tie-down 捆绑带：由**带手柄的棘轮**张紧的织带（webbing），核心为一个 captured 的**卷绕
spool/mandrel + ratchet 齿轮 + pawl/release** 机构，加上 webbing 载荷路径和端部 fitting（金属钩 /
软环 / E-track / 或无钩 feed-through 尾）。默认成熟域 = 手持货运棘轮张紧器（0.15–0.35 m 手柄级）。

不该混入：cam-buckle / over-center buckle strap（无棘轮齿+pawl，纯凸轮夹）、seat belt（缩回卷簧、无手柄棘轮）、
tow strap（纯钩+织带无张紧机构）、hand-winch / 齿轮绞盘（曲柄+齿轮箱，另一类机构）。

## 槽位 + 候选模块表

### Slot A：ratchet_body（③ Primary Form Family + 核心机构 root）

生成 root `frame` + captured `spool`（REVOLUTE Y，ratchet 齿）+ coaxial `handle`（REVOLUTE Y）+
`drive_pawl`（REVOLUTE Y）。4 个恒定 part、3 个 captured-pin revolute（grandfathered）。候选间差异 =
frame/handle 的**可识别几何形态原型**（Planar Boundary / Volumetric Envelope），part tree / joint
graph / interface 不变（Rule 3）。

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `stamped_twin_cheek` | forked_anchor | `rec_use-...-160740_098181_6a70af39` (001) | `_frame_shape` L63-71, `_side_plate` L27-60, `_toothed_spindle` L74-89, pawl L263-290 | Planar Boundary Form | eligible if compatible | 冲压穿孔 cheek 板（2 lightening windows/侧）+ 18 齿双 ratchet wheel + rubber-grip 手柄 + 独立 drive_pawl |
| `u_frame` | forked_anchor | `rec_picturex_...002...8a06b96f` (002) | `_frame_shape` L82-99, `_spool_drum_shape` L137-142, `_ratchet_wheel` L58-79, `_handle_shape` L102-120 | Volumetric Envelope Form | eligible if compatible | 放样 U 侧型 chassis + 开槽 mandrel + 16 齿 saw-tooth wheel×2 + raised long-handle；pawl 采用 001 派生小 pawl |
| `compact_mini` | forked_anchor | `rec_0611_ratchet_strap_var_frame_form_compact_mini_ratchet` (from 001) | `_side_plate`/`_frame_shape` (缩短版) | Planar Boundary Form | eligible if compatible | 缩短 stamped cheek family，保留 captured pivots；短机身轻载 |
| `long_handle_heavy_duty` | forked_anchor | `rec_0611_ratchet_strap_var_frame_form_long_handle_heavy_duty_ratc` (from 001) | `_heavy_handle_arm` / `_heavy_rubber_grip` / `_frame_shape` | Volumetric Envelope Form | eligible if compatible | 加强/加长 frame + 长橡胶手柄臂（高杠杆） |
| `wide_body_cargo` | forked_anchor | `rec_0611_ratchet_strap_var_frame_form_wide_body_cargo_ratchet` (from 002) | `frame_shell` / `_frame_shape`（加宽 bearing span） | Volumetric Envelope Form | eligible if compatible | 加宽 U-frame bearing 跨距（宽织带货运） |

### Slot B：actuation_release（② 关节类型 / mechanism）

生成 `release` part + 一个 bounded REVOLUTE（axis Y）。区别在**pivot 挂载位置 + 关节 parent**：
frame-mounted thumb vs handle-mounted paddle vs handle-mounted pull-tab。这是 ② 轴（同一"释放 pawl"
功能，边的 parent/位置/几何不同）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `frame_thumb` | origin_anchor | `rec_use-...6a70af39` (001) | `release_lever` L292-319 | eligible if compatible | frame-mounted thumb bar + thumb pad + release pin；`release_pivot` REVOLUTE on frame |
| `handle_paddle` | origin_anchor | `rec_picturex_...8a06b96f` (002) | `_release_shape` L123-134, `handle_to_release` L337-346 | eligible if compatible | handle-mounted finger paddle（pin+arms+box）；REVOLUTE on **handle** |
| `pull_tab` | forked_anchor | `rec_0611_ratchet_strap_var_release_pull_tab_release` (from 002) | `_release_shape` / `release_mechanism` / `handle_to_release` | eligible if compatible | handle-mounted 中央 pull-tab；bounded REVOLUTE on handle |

### Slot C：webbing_fitting（① 骨架图：webbing topology + 端部 fitting，合并槽）

生成 `webbing` part（FIXED 于 frame）+ 端部 fitting 几何（钩/软环/E-track）+（two_piece 时）独立
`webbing_roll` part（REVOLUTE）+（snap_hook 时）fitting-local `snap_gate_*` part（REVOLUTE ×N）。
webbing_topology（two_piece / feed_through / endless）与 end_fitting（钩类型）在物理上耦合（钩是 webbing
route 的终端），故合并为一个 slot，用完整合法组合作为 candidate——彻底消除跨槽非法组合（endless_loop+钩、
feed_through+钩）。① 骨架覆盖充分（8 个结构不同 webbing+fitting）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `two_piece_wire_j` | origin_anchor | `rec_use-...6a70af39` (001) | `_routed_strap_shape` L140-161, `_hook_shape` L108-122, `_webbing_roll` L92-105, roll joint L373-382 | eligible if compatible | 独立 orange roll（REVOLUTE）+ routed free-strap + 成对 wire J-hook（frame 端+free 端）+ blue 测量条 |
| `two_piece_flat_j` | forked_anchor | `rec_0611_ratchet_strap_var_end_fitting_flat_j_hook` (001) | `_hook_shape`（扁平冲压 slot 版） | eligible if compatible | 同 two_piece，钩换扁平冲压 J-hook（宽槽轮廓） |
| `two_piece_s_hook` | forked_anchor | `rec_0611_ratchet_strap_var_end_fitting_s_hook` (001) | `_hook_shape`（S 型双弯 + webbing eye） | eligible if compatible | 同 two_piece，钩换 S-hook |
| `two_piece_snap_hook` | forked_anchor | `rec_0611_ratchet_strap_var_end_fitting_snap_hook` (001) | `_snap_hook_body` + `_snap_hook_gate`, `snap_gate_0..1` + `snap_gate_pivot_0..1` | eligible if compatible | 同 two_piece，钩换 gated snap hook；**每钩带 fitting-local `snap_gate` part（REVOLUTE，fitting-local revolute policy）** |
| `two_piece_e_track` | forked_anchor | `rec_0611_ratchet_strap_var_end_fitting_e_track_fitting` (001) | `_etrack_end_fitting` | eligible if compatible | trailer E-track tongue/slot fitting 代替 J-hook |
| `two_piece_soft_loop` | forked_anchor | `rec_0611_ratchet_strap_var_end_fitting_soft_loop` (001) | `_soft_loop_shape` + `_add_soft_loop` + reinforcement stitches | eligible if compatible | 缝制软环 eye 代替金属钩（sourced 柔性结构，不降级为 Box 占位） |
| `feed_through_tail` | origin_anchor | `rec_picturex_...8a06b96f` (002) | `feed_webbing`/`tail_webbing` L245-315 | eligible if compatible | 单条 loose feed-through 织带尾（无钩、无 roll），穿过开槽 mandrel |
| `endless_loop` | forked_anchor | `rec_0611_ratchet_strap_var_webbing_topology_endless_loop` (002) | `_endless_webbing_shape`, `frame_to_webbing` | eligible if compatible | 无钩闭合环织带（bundling），单一连续 loop |

硬约束自查：Slot A 5 candidate（≥3，含 ≥3 ③ 主体形态原型：stamped 平面边界 / U-frame 体量包络 / compact /
long-handle / wide-body）；Slot B 3 candidate（②）；Slot C 8 candidate（①）。均 forked/origin anchor 支撑，
无凭空 skeleton。候选间为结构差异（part tree / joint parent / fitting 拓扑），非只换尺寸/涂装。

## 槽位图（slot graph）

```
pattern: parallel_children

           ratchet_body (root: frame)
            ├─[spindle_rotation REVOLUTE axis Y, captured pin on cheek bores]→ spool
            ├─[handle_pivot     REVOLUTE axis Y, coaxial captured pin]        → handle
            ├─[pawl_pivot       REVOLUTE axis Y, captured pin]                → drive_pawl
            ├─ actuation_release slot:
            │     frame_thumb  : [release_pivot REVOLUTE axis Y] frame  → release
            │     handle_paddle: [handle_to_release REVOLUTE axis Y] handle → release   (parent = handle)
            │     pull_tab     : [handle_to_release REVOLUTE axis Y] handle → release   (parent = handle)
            └─ webbing_fitting slot:
                  [webbing_mount FIXED] frame → webbing (+ fittings fused as visuals)
                  two_piece_*: [webbing_roll_rotation REVOLUTE axis Y] frame → webbing_roll
                  two_piece_snap_hook: [snap_gate_pivot_i REVOLUTE] webbing → snap_gate_i  (i=0..1, fitting-local)
```

接口点位：
- spool/handle/pawl/release 的 pivot 为 captured-pin（穿 cheek 板 / bore），**omit MatingContract**（Rule 2
  captured-pin 例外，grandfathered），由 element-scoped `allow_overlap` + `expect_contact` 守住。
- 各件 pivot 轴均 = object Y 轴（(0,1,0)）；handle 与 spool 共轴（同 origin xyz）。
- webbing FIXED 于 frame（origin()），用 `expect_overlap`（webbing 穿过 frame 宽度/spool 槽）表达 route。
- webbing_roll pivot 在 frame 上方 tangent 位置（REVOLUTE Y）。
- snap gate pivot 为 fitting-local REVOLUTE（uniform fitting-local revolute policy）。

互斥/派生：webbing_roll part 仅 `two_piece_*` candidate 存在；`snap_gate_*` part 仅 `two_piece_snap_hook`
存在；release 的 parent（frame vs handle）由 Slot B module 决定。

## 每槽位 Module Emits / Interfaces

### Slot A / ratchet_body（所有 candidate 同结构，仅形态原型/尺寸变）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(root), `spool`, `handle`, `drive_pawl` | 001 L179-290 / 002 L167-243 |
| internal joints | `spindle_rotation` REVOLUTE Y (captured), `handle_pivot` REVOLUTE Y (coaxial captured), `pawl_pivot` REVOLUTE Y (captured) | 001 L206-290 / 002 L317-336 |
| upstream interface | none（root） | — |
| downstream interface | `frame` mount face（供 release/webbing 读取 `frame` part 名并 parent） | — |

### Slot B / actuation_release
| emits | 描述 | 来源 |
|---|---|---|
| parts | `release` | 001 L292-319 / 002 L238-243 |
| internal joints | `release_pivot`(frame_thumb, on frame) 或 `handle_to_release`(paddle/pull_tab, on handle) REVOLUTE Y, captured | 001 L311-319 / 002 L337-346 |
| upstream interface | reads `frame`（+ `handle` for handle-mounted）part by canonical name | — |
| downstream interface | none | — |

### Slot C / webbing_fitting
| emits | 描述 | 来源 |
|---|---|---|
| parts | `webbing`(+ fitting visuals); `webbing_roll`(two_piece_*); `snap_gate_0..1`(snap_hook) | 001 L321-382 / 002 L245-353 |
| internal joints | `webbing_mount` FIXED; `webbing_roll_rotation` REVOLUTE Y(two_piece_*); `snap_gate_pivot_i` REVOLUTE(snap_hook, fitting-local, mating declared) | 001 L355-382 |
| upstream interface | reads `frame` part by canonical name（FIXED mount） | — |
| downstream interface | none | — |

活动件语义：spool 卷绕、handle 张紧、pawl 棘爪、release 释放、webbing_roll 放线、snap_gate 开合——
每个都有 bounded REVOLUTE + targeted `ctx.pose(...)` 覆盖。不动细节（齿、grip 肋、woven picks、tick、
stitches、hook shank）都写成宿主 part visual（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `ratchet_body` | enum | stamped_twin_cheek/u_frame/compact_mini/long_handle_heavy_duty/wide_body_cargo | — | choice | procedural sampler | Slot A |
| `release_style` | enum | frame_thumb/handle_paddle/pull_tab | — | choice | procedural sampler | Slot B |
| `webbing_fitting` | enum | two_piece_wire_j/flat_j/s_hook/snap_hook/e_track/soft_loop/feed_through_tail/endless_loop | — | choice | procedural sampler | Slot C |
| `palette_style` | enum | orange_zinc/blue_galvanized/black_polyester/green_zinc/red_black/hi_vis_yellow (6) | orange_zinc | choice | procedural sampler | 5★ colorways |
| `frame_len_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp | 001/002 frame dims |
| `frame_width_scale` | float | [0.85, 1.25] | 1.0 | independent | clamp；wide_body 偏大 | 002 wide-body |
| `handle_len_scale` | float | [0.80, 1.35] | 1.0 | independent | clamp；long_handle 偏大 | 001/002 handle |
| `spool_radius_scale` | float | [0.9, 1.15] | 1.0 | independent | clamp | spindle dims |
| `webbing_width` | float | derived | 0.042 (001) | equation | `= f(ratchet_body)`；U-frame 家族用 0.025，stamped 用 0.042；bearing span 派生 | frame bearing span |
| `handle_open` (行程) | float | [闭合, 上界] | — | conditional | 见 §8.5 ⑤ 运动包络；上界随 body clamp | 001/002 handle limits |
| (—) | constraint | — | — | inequality | webbing_width ≤ frame_inner_span − 2·wall；违反则回缩 webbing_width | frame 宽度 |
| (—) | constraint | — | — | inequality | spool_radius·scale ≤ frame_cheek_gap/2；违反回缩 spool_radius_scale | cheek 捕获间隙 |

连续尺寸采样契约：先采 independent scale → 派生 `webbing_width`（随 body 家族）→ inequality 把
webbing_width / spool_radius 投影回可行域 → conditional 解析 handle_open 上界。全部在 `resolve_config` 求解。

## 参数 §7.5 编译预算 / compile budget（必填）

**每-seed 预算 = 18s**（依据：本类别为重布尔雕刻类——stamped 穿孔 cheek、toothed spindle、J/S/snap
hook、webbing roll 都是 cadquery boolean union/cut；库内该档 15–30s。用分档 tessellation +
成对 fitting 复用同一 `Mesh` 把它压到 ~12–18s）。sweep `--compile-timeout 120`（≈6–8× hang-guard）。
分档：小半径特征（hook 曲率、齿、pin、band）≤32 段；frame/handle hero cq 用 tolerance ≈ 0.0004；
成对 hook / 双 ratchet wheel / 两 snap_gate 复用同一 mesh 对象，只换 origin。超预算先降精度（减 roll
层数、减 woven pick 数、粗化 tolerance）再迭代。

## Multiplicity / Copy Logic

- 无 product-level multiplicity 轴：ratchet 齿数、grip 肋、woven picks、stitches、成对 fitting 细节
  都是 implementation copy logic，不暴露为 `*_count` 模板 slot。
- 成对同构件（frame 两端 hook、两 ratchet wheel、snap_hook 两 gate）用 `name_{i}` 命名 + 共享 helper +
  复用同一 `Mesh`；均匀角/线性摆放；gate 用统一 fitting-local REVOLUTE policy。
- 唯一"随 module 出现/消失"的 part（webbing_roll、snap_gate_i）属 ① 骨架差异（在 Slot C candidate 内），
  不是 multiplicity。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | Slot C 8 个结构不同 webbing+fitting（two_piece 带独立 REVOLUTE `webbing_roll`；snap_hook 带 fitting-local REVOLUTE `snap_gate`×2；feed_through/endless 无 roll 无钩）+ Slot A 恒定 4-part 机构脊柱。全部 forked/origin anchor 支撑。 |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：无 product-level 复制轴；成对 fitting/齿/picks 为 implementation copy。 |
| ② 关节类型 | 边换 type/轴 | 有 | 全部主 pivot = REVOLUTE axis Y（bounded）；webbing_mount = FIXED；snap_gate = fitting-local REVOLUTE。②的多样性在 **release 边的 parent/位置**：frame-mounted thumb（frame→release）vs handle-mounted paddle/pull_tab（handle→release）。source-backed（001/002/pull_tab fork）。声明的每种在 sweep 出现（axis_realization 核对）。 |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | Slot A 5 candidate：stamped_twin_cheek(Planar Boundary)、u_frame(Volumetric Envelope)、compact_mini(Planar Boundary)、long_handle_heavy_duty(Volumetric Envelope)、wide_body_cargo(Volumetric Envelope)。forked_anchor，登记进 `slot_choices`。 |
| ④ 表面装饰 | 叠加表面细节 | 有 | stamped cheek lightening windows、grip 肋、blue 测量条+tick、woven picks/edge yarns、soft-loop reinforcement stitches、woven roll edge bands。record_only / host-conformal；由宿主 part 表面派生（Rule 4）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | frame_len/width、handle_len、spool_radius scale（见 §7）；运动包络：handle_pivot REVOLUTE Y 开启方向抬起手柄 `[0, open_upper]`；spindle_rotation `[-0.45,1.10]`；pawl_pivot `[-0.10,0.26]`；release `[闭合, ~0.32]`；webbing_roll `[-0.8,0.8]`；snap_gate `[0, ~0.9]`。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（max_pose_samples 依关节数）+ 每机构一条 targeted `ctx.pose(...)`（handle 开合、spool 转、pawl 摆、release 抬、roll 转、snap_gate 开）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 colorway（orange_zinc / blue_galvanized / black_polyester / green_zinc / red_black / hi_vis_yellow）；材质大类含 metal(zinc/galv steel)、rubber(grip)、painted/polyester(webbing)——覆盖 ≥ ceil(0.5×6)=3。来自 5★ 真实 colorway（001 orange+zinc+black+blue；002 blue+galv+charcoal；+ 常见 black/green/red/yellow 织带）。 |

收尾自检：batch 0-9 需肉眼看到——5 种 frame 形态拉开、release 三种挂载位置不同、8 种 webbing+fitting 结构不同、
金属/橡胶/织带三材质大类都出现、装饰贴合宿主面、handle/spool/pawl/release/roll/gate 全程开合不穿模。

## 采样与覆盖审计

总组合数：A(5) × B(3) × C(8) = 120 slot 组合（× 6 palette = 720 视觉组合）。
理由：120 结构组合 < 300，属于 report-only 观察指标，不作 gate；真实组合空间受 anchor（2 origin + 9 fork）
与 fitting 耦合（合并 Slot C 已剔除非法组合）限制，120 是诚实的合法结构组合上限。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)` 对 A/B/C/palette
各做 `rng.choice`，再采连续 scale；seed=0 不特殊（也走采样）。无 curated/modulo 主表。

Procedural Sampling / Sweep Plan：deterministic `rng.choice` 选三 slot + palette + 连续 scale；合并 Slot C
消除跨槽非法组合，故无需 compatibility gate（唯一"gate"是 release parent 由 module 自选 frame/handle）。
无 regression override。random sweep：初版 0-35，成熟度审计可 0-999（report-only）。
Topology target：120 结构组合 < 300，report-only；已说明 anchor/耦合上限，不反推上游变体数。

Controlled local parameterization：`frame_len_scale`/`frame_width_scale`/`handle_len_scale`/`spool_radius_scale`
（§7 范围 + clamp）；`webbing_width` equation 派生自 body 家族；两条 inequality（webbing_width ≤ frame 内跨、
spool_radius ≤ cheek 半间隙）在 `resolve_config` 投影回缩；handle_open conditional 依 body clamp。均不破坏
captured-pin interface / clearance / joint origin / 类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A/B/C + palette 各 `rng.choice`；连续 scale uniform+clamp | slot_choices_for_seed == build 选择 |
| compatibility matrix | 合并 Slot C → 无非法跨槽组合；release parent 由 module 自选 | no floating/collision/axis/closed-pose 风险；snap_gate/roll 仅在对应 module 出现 |
| controlled local variation | frame/handle/spool scale + webbing_width 派生，clamp/inequality | 比例变化不破坏 captured pivot / webbing route / hook 附着 |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial；0-999 maturity（report-only） | contract failures；axis_realization；viewer |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| ratchet_body (③) | 5 | yes | yes | ≥3 ③ 主体形态原型 |
| actuation_release (②) | 3 | yes | yes | frame/handle 挂载差异 |
| webbing_fitting (①) | 8 | yes | yes | 含 gated snap_hook + endless loop |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（三 slot + palette）。
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic procedural sampling。
- 合并 Slot C 消除非法组合；无 curated/modulo 主表；无 regression override。
- 连续 scale 全部 clamp；`webbing_width`(equation) 与两 inequality 在 `resolve_config` 求解，不留到 builder 失败。
- captured-pin pivot（spindle/handle/pawl/release）omit MatingContract 且 grandfathered，用 element-scoped
  `allow_overlap`+`expect_contact`；FIXED webbing_mount 与 snap_gate（可两面接触时）声明 MatingContract。
- 关键 joint 类型/轴正确：主 pivot REVOLUTE axis Y；webbing_mount FIXED；snap_gate fitting-local REVOLUTE。
- 成对 copied fitting 遵循 `name_{i}` 命名 + 共享 helper/mesh。
- 每非-FIXED 关节有 targeted `ctx.pose(...)` + `fail_if_parts_overlap_in_sampled_poses`。

## Reject cases

- frame cheek 缩放后 captured spool/pawl pin 脱离 bore（floating/isolated）→ inequality 未回缩。
- webbing_width 超过 frame 内跨 → route 穿出 frame 或悬空。
- handle 与 spool 非共轴 / release 轴错 → pose 检查失败。
- snap_gate 开合中与 hook body 穿模 → 范围过宽（收窄 fitting-local range）。
- 把 J/S/snap hook 曲面 cq 降级为 Box、或 soft_loop 降级为简单方框（违反 Rule 3，柔性结构须 sourced）。
- two_piece 的 webbing_roll 与 free_strap 非 tangent（悬空 gap）。
- palette 每 seed 不变（未从 PALETTE_STYLES 采样）。
- fitting 装饰（tick/stitch/band）用常数半径贴在缩放/收锥面外（违反 Rule 4）。

## 与相邻类别的边界

- 不该混入：cam_buckle_strap / over-center buckle（无棘轮齿+pawl，纯凸轮夹紧，机构不同）。
- 不该混入：seat_belt / retractor（缩回卷簧、无手柄棘轮张紧）。
- 不该混入：tow_strap（纯钩+织带、无张紧机构）。
- 不该混入：hand_winch / geared winch（曲柄+齿轮箱，另一 bundled 机构，source map Blocked 已排除）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | parallel_children，root=frame；captured-pin pivot grandfathered；合并 webbing+fitting 消除非法组合；③ 主体形态家族 slot=ratchet_body（5 candidate）。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | stamped_twin_cheek | rec_use-...6a70af39 (001) | L27-290 | frame+spool+handle+pawl part tree + captured pivots |
| S2 | A | u_frame | rec_picturex_...8a06b96f (002) | L58-243 | 放样 U-frame + 开槽 mandrel + saw-tooth wheel |
| S3 | A | compact_mini | rec_..._frame_form_compact_mini_ratchet | frame/side_plate 缩短 | Planar Boundary 缩短 cheek |
| S4 | A | long_handle_heavy_duty | rec_..._frame_form_long_handle_heavy_duty_ratc | heavy handle/frame | Volumetric Envelope 长手柄 |
| S5 | A | wide_body_cargo | rec_..._frame_form_wide_body_cargo_ratchet | frame_shell 加宽 | Volumetric Envelope 宽机身 |
| S6 | B | frame_thumb | rec_...6a70af39 (001) | L292-319 | frame-mounted thumb release |
| S7 | B | handle_paddle | rec_...8a06b96f (002) | L123-134,337-346 | handle-mounted paddle release |
| S8 | B | pull_tab | rec_..._release_pull_tab_release | release_mechanism | handle-mounted pull tab |
| S9 | C | two_piece_wire_j | rec_...6a70af39 (001) | L92-161,321-382 | roll+routed strap+wire J hook |
| S10 | C | two_piece_flat_j | rec_..._end_fitting_flat_j_hook | _hook_shape flat | flat J hook |
| S11 | C | two_piece_s_hook | rec_..._end_fitting_s_hook | _hook_shape S | S hook |
| S12 | C | two_piece_snap_hook | rec_..._end_fitting_snap_hook | _snap_hook_body/_snap_hook_gate | gated snap hook + gate joints |
| S13 | C | two_piece_e_track | rec_..._end_fitting_e_track_fitting | _etrack_end_fitting | E-track tongue/slot |
| S14 | C | two_piece_soft_loop | rec_..._end_fitting_soft_loop | _soft_loop_shape/_add_soft_loop | sewn soft loop eye |
| S15 | C | feed_through_tail | rec_...8a06b96f (002) | L245-315 | loose feed-through webbing tail |
| S16 | C | endless_loop | rec_..._webbing_topology_endless_loop | _endless_webbing_shape | closed loop webbing |

## 模板实现备注（可选）

- 全部 frame_form candidate 用**统一 canonical part 名**（`frame`/`spool`/`handle`/`drive_pawl`），
  使 release/webbing module 可按名 `model.get_part("frame"/"handle")` parent（parallel pattern）。
- captured-pin overlap 用 element-scoped `allow_overlap`（frame↔spool、frame↔handle、frame↔pawl、
  frame/handle↔release、frame↔webbing、webbing↔roll、webbing↔spool）——照抄两 origin run_tests。
- snap_gate 若几何可两轴对齐面则声明 MatingContract；否则 fitting-local captured-pin grandfather。
- 成对 hook / 两 ratchet wheel / 两 snap_gate 复用同一 `mesh_from_cadquery` 结果对象（省编译）。
- u_frame / wide_body 家族的 pawl 采用 001 派生的小 drive_pawl（保持恒定 4-part 脊柱）。
</content>
</invoke>
