# Hamster Wheel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `hamster_wheel` |
| template path | `agent/templates/hamster_wheel.py` |
| test path (optional) | `tests/agent/test_hamster_wheel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | 2 origin parents + 8 verified-PASS variant forks provided for this subcategory |
| samples_adopted_as_module_sources | 6 (2 origins + 4 structural forks); the 4 multiplicity forks confirm N-range and are cited under §8 |
| source_index_policy | only adopted module sources are indexed below; multiplicity forks cited under Multiplicity |

- adopted as module sources: `rec_pet_animal_related__hamster_wheel__001_png_0b33af11f7df4e8e9dd52cc774223f12` (A), `rec_pet_animal_related__hamster_wheel__002_png_cd4d4b4b20814cf8b1aa9f9068edbd6b` (B), `rec_hamster_wheel_var_body_open_ring`, `rec_hamster_wheel_var_body_mesh`, `rec_hamster_wheel_var_skeleton_saucer`, `rec_hamster_wheel_var_mount_clamp`.
- multiplicity forks (cited in §8, not separate structural candidates): `rec_hamster_wheel_var_tread_n16`, `rec_hamster_wheel_var_tread_n48`, `rec_hamster_wheel_var_spoke_n3`, `rec_hamster_wheel_var_spoke_n8` — all are origin A re-emitted with a different `n_tread` / `n_spoke` loop count.

## 核心身份

A hamster exercise wheel: a single continuous running wheel (drum / open-rung ring / wire-mesh band / tilted saucer disc) that spins freely on a fixed axle carried by a low stand or cage mount. Exactly one primary revolute spin joint (`stand_to_wheel`). The wheel is always supported by an axle held in a bearing on the stand — never floating. Running surface + hub + rim + rear panel belong to the spinning `wheel` part; base/posts/wire/clamp + axle/bearing/caps belong to the grounded `stand` part.

不该混入的相邻类别：Ferris wheel / water wheel / paddle wheel (ride or fluid machine, multi-arm gondolas/paddles), fan / turbine / gear / pulley / spinning top (no stand-carried running drum), bird-cage panel, plate/bowl/dish (kitchenware, no spin joint), fully-enclosed exercise ball (rolls on the floor, no stand + axle).

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| A | `rec_pet_animal_related__hamster_wheel__001_png_0b33af11f7df4e8e9dd52cc774223f12` | `data/records/rec_pet_animal_related__hamster_wheel__001_png_0b33af11f7df4e8e9dd52cc774223f12/revisions/rev_000001/model.py:L116-L269` | solid_drum body (annular drum_wall + torus rims + rear_disk + hub + spokes + treads), acrylic_block stand, revolute Y spin, tread/spoke multiplicity helpers |
| B | `rec_pet_animal_related__hamster_wheel__002_png_cd4d4b4b20814cf8b1aa9f9068edbd6b/revisions/rev_000001/model.py:L95-L233` | `.../model.py:L95-L233` | bent-wire spline stand (base_loop + side yokes + axle/bearing/cap), thick rim lips, revolute spin |
| OR | `rec_hamster_wheel_var_body_open_ring` | `.../model.py:L192-L272` | open_rung_ring body (rims + full rear_disk + hub + spokes + N running rungs at rim radius, no drum_wall) |
| ME | `rec_hamster_wheel_var_body_mesh` | `.../model.py:L193-L281` | wire_mesh_band body (N axial mesh_bar + M circumferential mesh_hoop grid) |
| SA | `rec_hamster_wheel_var_skeleton_saucer` | `.../model.py:L61-L235` | tilted_saucer disc on inclined axle (① skeleton), converging-yoke inclined stand, thrust-bearing caps |
| CL | `rec_hamster_wheel_var_mount_clamp` | `.../model.py:L110-L216` | cage-clamp cantilever bracket (clamp plate + jaws + mount_arm) carrying a cantilevered axle |

## 槽位 + 候选模块表

Two structural layers vary independently and share a single mating interface (the fixed axle at `axle_height`, along the spin axis, captured in the wheel hub bore): the grounded **mount** (stand) and the spinning **wheel body** (③ Primary Form Family). Both parent/child of the one `stand_to_wheel` revolute joint.

### Slot A：mount / support（① skeleton — support topology）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `acrylic_block` | forked_anchor | A | L132-L190 | eligible if compatible | solid rounded base_plate (extruded profile) + 2 flanking support_post + bearing_crossbar + rear_foot_rail + bearing_block; horizontal Y axle |
| `bent_wire` | forked_anchor | B | L111-L169 | eligible if compatible | closed spline `base_loop` on floor + 2 curved `side_support` yokes converging on the rear bearing; horizontal Y axle |
| `cage_clamp` | forked_anchor | CL | L110-L216 | eligible if compatible | vertical clamp_plate + upper/lower hook jaws gripping a cage bar + cantilever mount_arm carrying a cantilevered axle; horizontal Y axle |

### Slot B：wheel_body（③ Primary Form Family / macro running-surface construction）

| module_name | source_type | form_subtype | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `solid_drum` | forked_anchor | Macro Surface Construction | A | L192-L259 | eligible if compatible | closed annular drum_wall shell + torus front/rear rims + rear_disk + hub sleeve + N radial spokes + N axial grip treads |
| `open_rung_ring` | forked_anchor | Macro Surface Construction | OR | L192-L260 | eligible if compatible | open sides: torus rims + full rear_disk + hub + N spokes + N discrete running rungs at rim radius (no drum_wall) |
| `wire_mesh_band` | forked_anchor | Macro Surface Construction | ME | L193-L258 | eligible if compatible | crossing-wire running band: N axial mesh_bar × M circumferential mesh_hoop + rims + rear_disk + hub + N spokes |
| `tilted_saucer` | forked_anchor | Volumetric Envelope Form | SA | L68-L217 | eligible only with `bent_wire` (see gating) | shallow dished disc (annular disc + hub boss + peripheral lip) whose normal lies along an inclined spin axle; no drum wall / rungs / mesh |

硬约束满足：Slot A = 3 candidates (≥3); Slot B = 4 candidates (≥3, form-dominated ③ slot registered into `slot_choices`). Each candidate cites a distinct real 5-star source with clear part tree, correct joint semantics (single revolute spin), category-faithful primitives (mesh drums / torus rims / spline tubes / cadquery disc), and a compatible axle interface. No size/color/decoration-only candidates.

## 槽位图（slot graph）

pattern: `mixed` (single grounded `stand` root → one revolute-spun `wheel` child; the `wheel` carries loop-emitted multiplicity families: running-surface treads/rungs/mesh_bars and hub spokes).

```text
[Slot A mount → part `stand`]
   ── fixed axle assembly (axle_shaft + bearing + front cap) at (0,0,axle_height), oriented along spin axis ──
        │  interface: axle passes through the wheel hub bore (captured pin, coaxial)
        ▼
   stand_to_wheel  REVOLUTE, axis = spin_axis, origin (0,0,axle_height), range ±π…±2π
        ▼
[Slot B wheel_body → part `wheel`]  (hub bore coaxial on axle; running surface + rims + rear_disk + hub + spokes + treads)
```

- 接口点位：the axle at `(0,0,axle_height)` along `spin_axis`; the wheel hub bore is coaxial on it. This is a **captured-pin** interface (pin-through-sleeve) — no `MatingContract` (grandfathered), verified instead by element-scoped `allow_overlap(stand.axle_shaft, wheel.hub)` + `expect_within`/`expect_overlap` coaxiality asserts.
- 跨 slot joint：single `stand_to_wheel` REVOLUTE. `spin_axis = (0,1,0)` for drum-family bodies (horizontal Y); `spin_axis = (cos t, 0, sin t)` (t≈35°) for `tilted_saucer` (inclined X–Z).
- 互斥 / gating：`tilted_saucer` re-orients the axle to an incline and requires converging rear supports; the `acrylic_block` flanking posts and the `cage_clamp` rear cantilever are built in the horizontal-Y convention and geometrically collide a tilted disc, so `tilted_saucer` is gated to the `bent_wire` mount (which builds the source-proven inclined converging-yoke stand). All drum-family bodies pair with all 3 mounts.

## 每槽位 Module Emits / Interfaces

### Slot A / module `acrylic_block`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand` visuals: `base_plate` (extruded rounded-rect), `support_post_0/1`, `bearing_crossbar`, `rear_foot_rail`, `bearing_block`, + shared axle assembly | A / model.py:L132-L190 |
| internal joints | none (single connected part) | A |
| downstream interface | horizontal Y axle at (0,0,H): `axle_shaft` (r≈0.005), `front_axle_cap` (front −Y), `bearing_block` (rear +Y); wheel hub bore coaxial | A / model.py:L167-L190 |

### Slot A / module `bent_wire`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand` visuals: `base_loop` (closed spline tube), `side_support_0/1` (curved yoke tubes), + shared axle assembly | B / model.py:L111-L169 |
| downstream interface | same horizontal Y axle assembly meeting the yoke tips at the rear bearing | B / model.py:L152-L169 |

### Slot A / module `cage_clamp`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand` visuals: `clamp_plate`, `clamp_jaw_upper`(+hook lip), `clamp_jaw_lower`(+grip lip), `mount_arm`(+brace), + shared axle assembly | CL / model.py:L110-L216 |
| downstream interface | cantilevered horizontal Y axle carried by `mount_arm`; wheel hub bore coaxial | CL / model.py:L190-L216 |

### Slot B / module `solid_drum`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel` visuals: `drum_wall` (annular mesh), `front_rim`/`rear_rim` (torus), `rear_disk` (annular), `wheel_hub` (annular sleeve), `spoke_{i}`×N, `tread_{i}`×N | A / model.py:L192-L259 |
| internal joints | none (all FIXED visuals on the wheel part) | A |
| upstream interface | hub bore coaxial on the axle at part-local origin; contains (0,0,0) | A / model.py:L227-L233 |

### Slot B / module `open_rung_ring`
| emits | `wheel`: `front_rim`/`rear_rim` (torus), full `rear_disk` (hub→rim), `wheel_hub`, `spoke_{i}`×N, `rung_{i}`×N at rim radius; no drum_wall | OR / model.py:L192-L260 |

### Slot B / module `wire_mesh_band`
| emits | `wheel`: `mesh_bar_{i}`×N (axial) + `mesh_hoop_{j}`×M (torus), rims, `rear_disk`, `wheel_hub`, `spoke_{i}`×N | ME / model.py:L193-L258 |

### Slot B / module `tilted_saucer`
| emits | `wheel`: `running_disc` (cadquery: annular disc + hub boss + peripheral lip), inclined spin axis; thrust-bearing caps overlap hub faces | SA / model.py:L68-L217 |

不动细节（rim grip ribs, molded striations, rear petal vents, brand ring）写成宿主 part visual，不作为独立 part。活动件只有一个 `wheel`（一条 revolute 边）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount` | enum | `acrylic_block` / `bent_wire` / `cage_clamp` | `acrylic_block` | choice | procedural sampler; forced to `bent_wire` when `body_form==tilted_saucer` | Slot A table |
| `body_form` | enum | `solid_drum` / `open_rung_ring` / `wire_mesh_band` / `tilted_saucer` | `solid_drum` | choice | procedural sampler | Slot B table |
| `n_tread` | int | [12, 56] (drum/ring running rungs; = mesh_bar count for mesh) | 32 | independent | weighted small-N sample; clamp; ignored by saucer | A L248; §8 |
| `n_spoke` | int | [3, 12] (hub spokes) | 5 | independent | weighted small-N sample; clamp; ignored by saucer | A L235; §8 |
| `wheel_radius` | float | [0.090, 0.140] (drum family); saucer fixed 0.145 | 0.112 | independent | clamp | A L23 / SA |
| `wheel_depth` | float | [0.055, 0.110] | 0.082 | independent | clamp; drives axle span & rear-support y | A L24 |
| `axle_height` | float | [0.140, 0.200] | 0.160 | inequality | `axle_height ≥ wheel_radius + 0.030` (wheel clears base); reproject | A L25 |
| `spin_range` | float | [π, 2π] | π | independent | revolute lower=−range, upper=+range | A L268 / B L229 |
| `palette_theme` | enum | 5 themes (blue/green/pink/amber/purple translucent + metal/steel/white) | `blue_clear` | choice | procedural sampler | A/B materials |
| `spin_axis` | derived | `(0,1,0)` or `(cos t,0,sin t)` | `(0,1,0)` | equation | `= (cos t,0,sin t)` iff `body_form==tilted_saucer`, else `(0,1,0)` | SA L61-L64 |

连续尺寸采样契约：先独立采 `wheel_radius`/`wheel_depth`/`spin_range`；派生 `spin_axis`；用不等式把 `axle_height` 投影到 `≥ wheel_radius+0.030`。所有约束在 `resolve_config` 求解。

### 7.5 编译预算 / compile budget
自报预算：**每 seed ≤ 30s**（多数 drum-family seed 用 mesh/torus/cylinder，实测参考 5-15s；`tilted_saucer` + `cage_clamp` 用少量 cadquery 布尔，30-45s 档的下缘）。分档 tessellation：drum_wall/rear_disk annular mesh 96-128 段（英雄环面），torus 16×128，hub 72 段，treads/spokes/mesh_bars 复用同一 `Cylinder`（无 per-copy Mesh）。cadquery disc tolerance 0.0008 / angular 0.05。sweep `--compile-timeout 90`（≈3×预算 watchdog）。

## Multiplicity / Copy Logic

两根独立复制轴，都挂在 `wheel` 上，均为 FIXED visuals（不是独立 part），共享同一 helper：

**轴 1 — 运行面 rungs/treads/mesh_bars（`count_param = n_tread`）**
- `N_range`：产品域 [12, 56]；sweep 上限 56。sampling domain：加权小 N 高频、大 N 稀有（源 samples {16, 32(A), 48}）。
- copied object：`tread_{i}`（solid_drum，drum 内半径处轴向 grip 圆柱）/ `rung_{i}`（open_rung_ring，rim 半径处）/ `mesh_bar_{i}`（wire_mesh_band，轴向丝）。naming `f"{stem}_{i}"`，even angular spacing `2π i/N`，FIXED to `wheel`。
- gating：solid_drum / open_rung_ring / wire_mesh_band 适用；`tilted_saucer` 不适用（disc 无运行 rung）。
- source：A helper `add_y_cylinder` in `for i in range(32)`；forks n16/n48 证明 N-range。

**轴 2 — hub spokes（`count_param = n_spoke`）**
- `N_range`：产品域 [3, 12]；sweep 上限 12。sampling domain：加权小 N（源 samples {3, 5(A), 8}）。
- copied object：`spoke_{i}`（hub→rim 径向圆柱），even spacing `18°+i·(360/N)`，FIXED to `wheel`。
- gating：drum / ring / mesh 适用；`tilted_saucer` 不适用。
- source：A helper `add_radial_cylinder` in `for i in range(5)`；forks n3/n8。

**record_only（不 sweep，避免 padding）**：B 的 `rim_rib_{i}`(18) 和 rear petal-vent(5) 已在原始资产 loop-emitted，作为 host-conformal 表面装饰，不额外 fork（单一 running-rung + spoke 族已充分暴露 copy logic）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 单 revolute spin `stand_to_wheel` 恒定；support topology 变化：acrylic-block（A）/ bent-wire（B）/ cage-clamp cantilever（CL）；`tilted_saucer`（SA）把 spin 边的轴从水平 Y 改为 inclined X–Z。全部 forked_anchor/source-backed |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`n_tread` [12,56]、`n_spoke` [3,12]，各自加权小 N；forks 证明 N |
| ② 关节类型 | 换 type/轴 | 有（源限定） | 单 REVOLUTE spin，轴 = (0,1,0)（drum family）或 (cos t,0,sin t)（saucer）。continuous-vs-revolute 平凡，不 fork（两 origin 均自由旋转）；声明的两种轴都会在 sweep 出现（saucer 触发 inclined 轴） |
| ③ 主体形态家族 | 换核心 part 的几何形态原型 | 有（主多样性轴，登记进 `slot_choices`） | `solid_drum`（Macro Surface Construction，A）/ `open_rung_ring`（Macro Surface Construction，OR）/ `wire_mesh_band`（Macro Surface Construction，ME）/ `tilted_saucer`（Volumetric Envelope Form，SA）。全部 forked_anchor，同 part tree（wheel + hub + rim/backbone）、同 primitive 家族、同 axle interface，只改运行面宏观构成 |
| ④ 表面装饰 | 叠加表面细节 | 有（record_only） | rim grip ribs / molded rim striations（B）/ rear petal vents（B）/ printed brand ring；host-conformal，写成 `wheel` visual 派生自 rim/rear 面，无专门 variant；装饰数随 ③⑤ 共形，不悬空 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | `wheel_radius` [0.090,0.140]、`wheel_depth` [0.055,0.110]、`axle_height` [0.140,0.200]（见 §7）。运动包络：`stand_to_wheel` REVOLUTE，轴 spin_axis，[−spin_range, +spin_range]，spin_range∈[π,2π]。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses`（wheel 关于 axis 轴对称 → 旋转不改包络，closed 通过即全程通过）+ targeted `ctx.pose({spin: mid})` 断言 tread/rung/disc 绕轴位移且 wheel 原点保持在 axle。无需 `qc_samples`；captured-pin/thrust-bearing overlap 用 element-scoped `allow_overlap`，非 sampled-pose exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：translucent plastic（glass-like，A 蓝/B 绿）、solid/rim plastic、metal（wire stand / axle）。配色 5 themes（blue/green/pink/amber/purple）+ white/steel 金属件；材质大类 3 ≥ ceil(0.5×5)=3 |

收尾自检：`template batch` 0-9 seed 必须肉眼看到 4 种 body form 拉得开、3 种 stand topology、材质大类都出现、rim 装饰贴合、spin 全程不穿模。

## 采样与覆盖审计

总组合数：drum-family = mount(3) × body(3) × n_tread(≈8 有效档) × n_spoke(≈6) ≈ 432；saucer = mount(1,gated) × body(1) = 1 结构组合 × palette。加 palette(5) 后离散空间充分 > 300。

理由：形态主导 + 双 multiplicity 轴提供主多样性；连续 scale 仅作局部变形，不承载多样性。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对所有普通 seed（含 seed 0）用 `random.Random(seed)` deterministic 采样，seed 0 不特殊、不 anchor。采样顺序：先 body_form → 据此 gate mount → 采 n_tread/n_spoke/dims/palette → resolve 投影 axle_height。

Procedural Sampling / Sweep Plan：sampler 先选 body_form；若 `tilted_saucer` 则 mount 强制 `bent_wire`（compatibility gate），否则 mount 自由三选一。n_tread/n_spoke 各自加权小 N 采样、各自 clamp、各自编进 `slot_choices`（tread 报 band sparse/medium/dense，spoke 报 raw N；saucer 报 `na`）。compatibility matrix 只有一条硬 gate（saucer→bent_wire），其余全兼容（同一水平 Y axle interface）。

Topology target：slot-choice tuple 覆盖 report-only；模块拓扑多样性 gate 实测 PASS。corner-stage 512-seed 探针实测 reachable distinct slot tuple ≈ 251（(mount×body×tread-band×spoke) 组合，saucer 因 gate 只走 bent_wire），低于富类别 300 建议线的原因是本类结构本就精简（单 wheel + 单 stand + 单 spin joint，simple richness band），已由真实源锚点上限与 saucer→bent_wire 兼容约束决定，非上游变体数量不足。该指标不作为 gate。

Regression overrides：none（初版）。

Controlled local parameterization：`wheel_radius` / `wheel_depth` / `axle_height` / `spin_range`（§7 范围与 clamp/inequality）。它们只做局部变形，不破坏 axle interface（hub bore 恒 coaxial）、clearance（axle_height≥radius+0.030）、joint origin（恒 (0,0,axle_height)）、multiplicity（N 独立 clamp）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form→gate mount→N/dims/palette，weighted small-N | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | 唯一硬 gate：`tilted_saucer`→`bent_wire`（inclined disc 与 flanking/cantilever 水平支撑互斥）；其余全兼容 | 无 floating / collision / axis / max-N 失败 |
| controlled local variation | 4 个连续 scale，resolve 内 clamp/inequality | 比例变化不破坏 interface / clearance / joint origin / identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 首验；0-999 成熟度 | contract failures；axis_realization；viewer 目检 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| mount | 3 | yes | yes | |
| body_form | 4 | yes | yes | ③ Primary Form Family slot（登记进 slot_choices） |

## Validator
- `slot_choices_for_seed` 返回 implemented module names（mount / body_form / n_tread band / n_spoke）。
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic procedural sampling。
- compatibility gate（saucer→bent_wire）在 `resolve_config` 求解，不留到 builder 失败。
- 恰有一个 REVOLUTE `stand_to_wheel`；drum-family 轴 (0,1,0)，saucer 轴 (cos t,0,sin t)；origin (0,0,axle_height)。
- wheel 关于 axle 轴对称，spin 全程不穿模（sampled poses）；captured-pin (axle↔hub) + thrust-bearing (cap↔disc) 用 element-scoped allow_overlap。
- wheel 站在 base 之上（front_rim/disc 底 > base 顶）。
- tread/rung/mesh_bar/spoke 按 naming/even-spacing/FIXED-to-wheel 复制。
- 连续 scale 在 resolve clamp/投影，不在 builder 失败。

## Reject cases
- 无 spin joint，或多于一个 primary spin joint。
- wheel 悬空（axle 不穿 hub，或 wheel 不被 bearing 支撑）。
- flanking-post / cantilever 水平 stand 配 tilted disc（穿模）——被 gate 排除。
- 运行面/spoke 做成独立 FIXED part 而非 wheel visual（floating decoration）。
- drum/mesh 运行面与 rim/rear_disk 之间留缝形成 disconnected island。
- 把 rim ribs / petal vents / brand ring 当独立 part 或独立 sweep 轴（padding）。
- 退化为 Ferris/water wheel、fan/turbine/gear、plate/bowl 或 enclosed ball。

## 与相邻类别的边界
- 不该混入：Ferris wheel / water wheel / overshot_waterwheel（ride/fluid machine，multi-arm gondola/paddle；hamster wheel 是单一 running drum + stand）。
- 不该混入：ceiling_fan / wind_turbine / gear_assemblies（blades/teeth 做功；hamster wheel 运行面是连续 drum/ring/mesh，被动自由旋转）。
- 不该混入：plate / bowl / turntable platter（无 stand-carried 水平/倾斜 axle 与 running-surface identity）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；directly implemented as `agent/templates/hamster_wheel.py`；driven to sweep verdict |
