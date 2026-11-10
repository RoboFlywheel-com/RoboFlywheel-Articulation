# Modular Spec — junction_box (Electrical_Wiring / Junction box)

## 元信息
| 项 | 值 |
|---|---|
| slug | `junction_box` |
| registry key | `Electrical_Wiring_Junction_box` |
| template path | `agent/templates/Electrical_Wiring_Junction_box.py` |
| function stem | `junction_box` (`build_junction_box` / `run_junction_box_tests`) |
| test path (optional) | `tests/agent/test_junction_box_template.py` (skipped while authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (single root `enclosure`; `cover` parallel child via 1 joint; glands + interior are inline visuals) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (3 origins + 4 slot-fork variants) |
| source_index_policy | only adopted module sources are indexed below |

3 origins share ONE abstract spine `enclosure(fixed root) → [cover hinge/lift] cover`, N cable glands
on the side walls, an interior terminal strip. All three COPY-PASTED their `_add_gland` calls; the
`2way` fork proved the loop-over-`gland_specs` form (adopted as the multiplicity idiom). Housing color
(clear PC / black / gray) is an ⑥ palette axis, NOT a structural slot.

| id | record | 建成形态 |
|---|---|---|
| S1 | `rec_use-...-518a36b7` | black IP68, N=6 glands on 4 walls, hinged cover, terminal_strip as a separate FIXED part, mount ears |
| S2 | `rec_use-...-058eea1f` | gray opaque, N=4 glands (2 left + 2 right) w/ conduits, hinged service cover, terminals INLINE on enclosure |
| S3 | `rec_use-...-d3744a0e` | clear polycarbonate, N=3 glands, **`KnobGeometry` ribbed gland nut (highest fidelity)**, hinged cover, mount ears |
| F-2way | `rec_junction_box_var_2way` | N=2, `_add_gland` replaced by a single `for spec in gland_specs` loop |
| F-screw | `rec_junction_box_var_screw_lid` | 4-corner-screw lift-off cover = **PRISMATIC +Z** lift (hinge removed) |
| F-empty | `rec_junction_box_var_empty_passthrough` | interior stripped to a bare gasketed pass-through (ground lug only, no terminals) |
| F-round | `rec_junction_box_var_round_box` | **round/cylindrical body** = `LatheGeometry` wall + circular lid + radial glands |

## 核心身份

A waterproof electrical junction box (IP68 enclosure): a sealed molded housing that joins/branches
insulated conductors. A grounded `enclosure` (root, FIXED to world) holds a removable `cover` (hinged
flip = REVOLUTE, or 4-screw lift-off = PRISMATIC); N threaded cable glands protrude from the side
walls; the interior is either a populated terminal strip (base + white insulators + brass bus + brass
ground lug) or an empty gasketed pass-through. Default mature form: rectangular gray/black/clear box,
gasket lip, mounting ears, 3–6 glands.

不该混入：a **distribution board / breaker panel** (has a DIN-rail breaker field + door-latch — a
different, denser interior); a **bare conduit fitting / coupling** (a threaded pipe union with no
enclosed terminal cavity and no lid). Junction box = enclosed cavity + lid + gasket + glands.

## 槽位 + 候选模块表

### Slot A：footprint_envelope（③ Primary Form Family，登记进 `slot_choices`）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rectangular` | forked_anchor | S3 (`d3744a0e`) / S2 / S1 | S3 L89-102, S2 L160-173 | eligible if compatible | `form_subtype=Volumetric Envelope Form`. Extruded-rectangular prism: 4 `Box` walls + `Box` floor + rounded-corner cylinders; glands on ±Y long walls; box cover panel. |
| `round` | forked_anchor | F-round (`var_round_box`) | L101-124 (wall/floor/gasket), L47-63 (radial gland) | eligible if compatible | `form_subtype=Macro Surface Construction`. Surface-of-revolution: hollow `LatheGeometry` cylindrical wall + `Cylinder` floor + annular `LatheGeometry` gasket ring; glands enter radially; circular `Cylinder` lid. |

Degrade-to-2 reason: the observed **and** real-world primary-form space for IP junction boxes is
bimodal — an extruded-polygon prism (rectangular; square is a ⑤ L≈W proportion, not a new form) vs a
surface-of-revolution cylinder (round conduit box). No third source-backed or world-plausible primary
form exists without drifting toward a neighbor category. Both candidates keep the same part tree
(`enclosure` + `cover`), same interface (top mouth → cover), same joint semantics; only the wall
primitive family and gland-placement math change (§6).

### Slot B：lid_mechanism（② 关节类型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_flip` | forked_anchor | S3 / S2 / S1 / F-round | S3 L152-188, F-round L234-307 | eligible if compatible | Rear-edge REVOLUTE about −X. Cover = panel + rim + labels + `cover_hinge_leaf` + 2 pins captured in 2 base barrels; opens upward `[0, ~1.2]`. |
| `screw_liftoff` | forked_anchor | F-screw (`var_screw_lid`) | L190-247 | eligible if compatible | 4-corner-screw removable cover = PRISMATIC +Z lift `[0, ~0.08]`. Cover = panel + corner screw heads/recesses + rib frame; no hinge hardware; seats on the gasket rim. |

Degrade-to-2 reason: exactly two lid mechanisms exist across the pool (revolute flip cover;
prismatic screwed lift-off cover). Both are source-backed; no third mechanism (e.g. slide/bayonet)
appears for junction boxes in the sources or the mature domain.

### Slot C：interior_fitout

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `terminal_strip` | forked_anchor | S3 / S2 / S1 | S3 L123-131 | eligible if compatible | Populated: `terminal_base` slab + brass bus bar + K white insulator/brass-cup terminal screws (looped) + brass `ground_lug`. All inline visuals on `enclosure` (Rule 1, non-moving). |
| `empty_passthrough` | forked_anchor | F-empty (`var_empty_passthrough`) | L144-163 | eligible if compatible | Bare gasketed cavity: terminal rows/bus removed, only the brass `ground_lug` remains on the floor. A minimalist pull/pass-through box. |

Degrade-to-2 reason: interior fit-out is binary in the pool — populated terminal strip vs bare
pass-through. A third interior (e.g. DIN-rail) is a distribution-board neighbor and is excluded by the
identity boundary.

### Multiplicity 轴：gland_count N（见 §8）

## 槽位图（slot graph）

pattern: `mixed`

```
enclosure (root, FIXED to world; footprint_envelope ∈ {rectangular, round})
  ├─[inline visuals]  N cable glands on side walls  (multiplicity axis, one shared _emit_gland helper)
  ├─[inline visuals]  interior_fitout ∈ {terminal_strip, empty_passthrough}  (Rule 1, no joint)
  ├─[inline visuals]  gasket lip + screw bosses + mount ears + labels + (if hinged) base hinge leaf/barrels
  └─[1 joint]────────► cover
        hinged_flip   : REVOLUTE, axis −X, origin (0, HINGE_Y, HINGE_Z) on rear hinge line, range [0, lid_open]
        screw_liftoff : PRISMATIC, axis +Z, origin (0, 0, mouth_top),                       range [0, lift_travel]
```

- The only cross-part connection is `enclosure → cover`. `cover` is a parallel child of the root
  `enclosure` (mixed pattern à la `Accessories_Cushion.py`); no `assemble()` chain is used.
- Interface point: the **top mouth** of the enclosure (rim/gasket plane at `z = mouth_top`).
  - hinged: mating = captured hinge pin ↔ base barrel (grandfathered, `allow_overlap` element-scoped);
    cover pins sit ON the pivot axis so they never translate → connectivity + no mid-travel 穿模.
  - screw_liftoff: mating = cover panel bottom resting on the gasket top (contact for connectivity),
    prismatic origin is gauge-free (proximity check exempt for prismatic).
- Glands / interior / gasket / ears are inline visuals on `enclosure` (non-moving → Rule 1), so they
  are all on one part and carry no isolated-part / mating obligations.

## 每槽位 Module Emits / Interfaces

### Slot A / footprint_envelope
| emits | 描述 | 来源 |
|---|---|---|
| parts | `enclosure` root part (walls + floor + rounded corners OR lathe wall + disc floor) | S3 L89-96 / F-round L101-113 |
| internal joints | none (root) | — |
| inline visuals | gasket lip, screw bosses, mount ears, rating/warning labels | S3 L99-113 / F-round L116-147 |
| downstream interface | top mouth plane `z=mouth_top`, footprint half-extents → cover + gland placement | S3 L152 / F-round L234-241 |

### Slot B / lid_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover` (box panel or circular disc) | S3 L152-160 / F-screw L191-235 |
| internal joints | `cover_hinge` REVOLUTE −X **or** `cover_lift` PRISMATIC +Z | S3 L180-188 / F-screw L238-247 |
| inline visuals (hinged) | base: `base_hinge_leaf` + 2 `base_hinge_barrel`; cover: `cover_hinge_leaf` + 2 `cover_hinge_pin` | S3 L148-150, L163-165 |
| inline visuals (screw) | 4 corner screw heads + recesses + rib frame on cover top | F-screw L202-235 |
| upstream interface | mouth plane; joint origin on rear hinge line (hinged) or mouth center (prismatic) | S3 L185 / F-screw L243 |

### Slot C / interior_fitout
| emits | 描述 | 来源 |
|---|---|---|
| inline visuals (terminal_strip) | `terminal_base` + brass bus + K looped terminal screws + `ground_lug` | S3 L123-131 |
| inline visuals (empty_passthrough) | `ground_lug` only (bare cavity) | F-empty L155-159 |
| joints | none (Rule 1: non-moving interior is a parent visual, never a FIXED-joint part) | — |

### Multiplicity / gland
| emits | 描述 | 来源 |
|---|---|---|
| inline visuals | N glands via ONE `for spec in gland_specs` loop, shared `_emit_gland` + shared `KnobGeometry` ribbed-nut mesh | F-2way L116-131 (loop), S3 L45-56 (gland stack) |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `footprint_envelope` | enum | rectangular / round | — | choice | procedural sampler | Slot A |
| `lid_mechanism` | enum | hinged_flip / screw_liftoff | — | choice | procedural sampler | Slot B |
| `interior_fitout` | enum | terminal_strip / empty_passthrough | — | choice | procedural sampler | Slot C |
| `gland_count` N | int | product {2,3,4,6}; template [2,8] weighted | — | multiplicity | weighted small-N draw (§8), clamp [2,8] | F-2way / sources |
| `palette_style` | enum | clear_polycarbonate / black_abs / light_gray_abs / diecast_aluminum / safety_blue_painted | clear_polycarbonate | choice | `rng.choice(PALETTE_STYLES)` | S1/S2/S3 colors + world |
| `len_scale` (rect L) | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp | ⑤ |
| `width_scale` (rect W) | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp | ⑤ |
| `radius_scale` (round R) | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp | ⑤ |
| `height_scale` (H) | float | [0.80, 1.25] | 1.0 | independent | uniform, clamp | ⑤ |
| `lid_open_scale` | float | [0.85, 1.10] | 1.0 | independent | uniform, clamp; only used by hinged | S3 L188 |
| `lift_travel_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; only used by screw | F-screw L245 |
| `terminal_count` K | int | [3, 8] | 6 | conditional | terminal screws; only when interior=terminal_strip; K loop | S3 L126-128 |
| (—) | constraint | — | — | inequality | **rect**: `L_eff ≥ ceil(N/2)·gland_pitch + 2·end_margin` → bump L; **round**: `R_eff ≥ N·gland_pitch/(2π) + wall` → bump R (glands never overlap along a wall / around the ring) | §7 gland clearance |
| (—) | constraint | — | — | inequality | `H ≥ gland_diameter + 2·wall_margin` → clamp H up so a wall-centered gland fits vertically | gland fit |

连续尺寸采样契约：先采所有 `independent` scale → 无 `equation` 从属 → 用上面两条 `inequality` 把
`L_eff`/`R_eff`/`H` 投影到可行域（按 N 抬升下界）→ `terminal_count` 的 `conditional` 仅在
interior=terminal_strip 时解析。所有约束在 `resolve_config` 内求解。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤ 15s/seed**（依据：本类别是 Box/Cylinder 主体 + 单个共享 `KnobGeometry` ribbed-nut mesh
复用 N 次 + round 时 1 根 48 段 `LatheGeometry` 壁 + 1 圈 gasket ring；无逐 gland mesh、无 CadQuery
布尔、无 wire spline tube（作为易碎 greeble 主动删除）——远低于重雕刻类 30-60s）。分档 tessellation：
`KnobGrip(count=32)`（沿用 S3）、`LatheGeometry(segments=48)`、terminal socket 用 `Cylinder`（隐式≤32
段）。N 个 gland 复用同一个 `ribbed_nut` mesh 对象。sweep `--compile-timeout 120`（≈3× 预算，watchdog）。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：gland_count N。**

- `count_param` = `gland_count`；`N_range`（产品域）= 观测 {2,3,4,6}，模板全程 `[2,8]`（可外推 >6）。
  sampling domain（权重档，小 N 高频）：`weights = {2:0.28, 3:0.24, 4:0.22, 5:0.12, 6:0.10, 7:0.02, 8:0.02}`。
- copied object：一个 cable gland（threaded cylindrical stack：clear_thread + 4 thread rings +
  `KnobGeometry` ribbed nut + collar + domed end + dark cable bore），沿用 S3 L45-56 的保真几何。
- naming：`gland_{i}_*`（`for i, spec in enumerate(gland_specs)`）。
- placement：`_gland_layout(r)` 生成 `gland_specs`（每条 = wall_point + 外法向方位角 θ）。
  - rectangular：N 分到 front(−Y,θ=−π/2) / rear(+Y,θ=+π/2) 两长壁，`ceil(N/2)`/`floor(N/2)`，
    壁内沿 X 均布；`_emit_gland` 沿 θ 外法向堆叠，最内 cylinder 反向嵌入壁 → 连通。
  - round：N 个方位角 `θ_i = −π/2 + i·2π/N` 绕圆均布，径向进入曲壁（沿用 F-round L47-63 的 rpy=(0,π/2,θ)）。
- joint policy：无关节（inline visuals，Rule 1）。
- source/gating：三源均 copy-paste `_add_gland`，F-2way 收敛为 `gland_specs` loop —— 模板**必须**只保留这一根循环。
- 其它 loop 化的同构件：terminal screws（K，S3 L126-128）、corner screw bosses（4）、mount ears（4）、
  gland 内 thread rings（4）、screw-lid corner screws（4/round 6）——全部 `for` 循环，禁止复制粘贴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有（轻） | 固定 2 part（`enclosure` + `cover`），1 个跨 part joint。骨架本身单一；结构多样性由 ②/③/interior/multiplicity 承载。part-count 不变是本类别的真实形态（junction box 就是"盒+盖"）。source-backed（全源同骨架）。 |
| └ multiplicity | 同构件 ×N | 有 | gland N，见 §8：产品 {2,3,4,6}，模板 [2,8] 权重档（小 N 高频）。forked_anchor F-2way loop。 |
| ② 关节类型 | 某条边换 type/轴 | 有 | `cover_hinge` REVOLUTE −X（S3/S2/S1/F-round）↔ `cover_lift` PRISMATIC +Z（F-screw）。两种都 forked_anchor，都在 sweep 出现（slot B 采样）。 |
| ③ 主体形态家族 | 换核心 part 的可识别几何形态原型 | 有 | 登记 slot A：`rectangular`(Volumetric Envelope Form, extruded prism, forked_anchor S1/S2/S3) / `round`(Macro Surface Construction, LatheGeometry surface-of-revolution, forked_anchor F-round)。2 值 + 理由（见 Slot A：观测+现实 IP-box 主体形态空间即双峰）。 |
| ④ 表面装饰 | 叠加表面细节 / 改装饰数 | 有 | 宿主派生：gasket lip（随 footprint：rect=4 Box / round=annular lathe ring）、rating/warning label（贴壁面，随 ③⑤ 定位）、gland thread rings（4）、cover rib frame。`record_only`（S3 L99-113,L173-178）。派生顺序 ③→⑤→④：label/gasket 由最终 footprint 的壁面/半径派生。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | len/width/radius/height scale ∈ 见 §7；关节运动包络——**hinged**：REVOLUTE −X，向上开，`[0, lid_open≈1.0–1.2]`；**screw**：PRISMATIC +Z，向上抬离，`[0, lift_travel≈0.06–0.09]`。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（cover 唯一动件，捕获 hinge pin 用 element-scoped `allow_overlap`）+ targeted `ctx.pose`：hinged 证开盖顶升高、screw 证抬离 z 升高、两者证闭合跨越 mouth。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | `palette_style` ×5：clear_polycarbonate(glass/translucent α0.40) / black_abs(plastic) / light_gray_abs(plastic) / diecast_aluminum(metal) / safety_blue_painted(painted)。材质大类 = {glass, plastic, metal, painted} = 4 ≥ ceil(0.5×5)=3。gasket 恒黄、terminal 恒白+brass、screw 恒 metal（真实硬件配色）。 |

收尾自检：0-9 seed batch 里必须肉眼见到 rect 与 round 两种主体、hinge 与 screw 两种盖、terminal 与
empty 两种内部、gland 数变化、且 shell 颜色（clear/黑/灰/金属/蓝）明显不同。

## 拓扑多样性审计

总组合数：footprint(2) × lid(2) × interior(2) × N档(7: 2..8) = **56** 离散拓扑（未计 palette×5 与连续 scale）。

理由：3 个离散 slot 各 2 candidate，全部无条件可达（无 gating 互斥）；N 有 7 档。1000-seed slot choice tuple distinct（footprint×lid×interior×N档）上限 56，远超 slot-key≥2 要求；低于 300 因类别真实离散空间有限（盒盖类），由连续 scale + palette 补足视觉多样性。report-only，不设门。

seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`：`rng.choice` 各 slot，
`rng.choices` 加权抽 N，`rng.choice(PALETTE_STYLES)`，`rng.uniform` 各连续 scale。`resolve_config` clamp
scale、按 N 抬升 L_eff/R_eff/H 下界、conditional 解析 K。无 regression override（seed 0 不特殊）。
compatibility：全 2×2×2 组合合法（rect/round × hinge/screw × terminal/empty 均物理可造）；无互斥 gate。
viewer 目检：0-35 sweep + 0-9 batch。

Controlled local parameterization：`len_scale`/`width_scale`/`radius_scale`/`height_scale`（主体比例）、
`lid_open_scale`（hinge 行程）、`lift_travel_scale`（prismatic 行程）、`terminal_count` K。全部在
`resolve_config` clamp/派生，受 gland-clearance inequality、gland 垂直 fit、cover mouth 覆盖约束，
不破坏单一 cover 关节 / mouth 接口 / N 复制。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→N→palette→scales；`rng.choice`/`rng.choices`/`rng.uniform` | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | 全组合合法，无互斥；N 与 L/R 用 inequality 抬升下界 | 无 floating / collision / axis / max-N / bulky 失败 |
| controlled local variation | 上列 scale + K，clamp/inequality/conditional | 比例变化不破坏接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 首过，0-999 成熟审计 | contract 失败；axis_realization / report |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| footprint_envelope | 2 | yes | no | ③ 形态双峰，见 Slot A degrade 理由 |
| lid_mechanism | 2 | yes | no | ② 仅 revolute/prismatic 两源 |
| interior_fitout | 2 | yes | no | 内部二元（populated/empty） |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名 + `("gland_count", f"n{N}")`
- `config_from_seed` 对所有 seed（含 0）用 deterministic procedural sampling
- compatibility 全合法，无非法组合需 gate
- 无 regression override
- 连续 scale 在 `resolve_config` clamp；gland-clearance / gland-fit inequality、K conditional 在 resolve 求解，不留到 builder
- 关键 interface：cover 单关节；hinged=captured pin+barrel（grandfathered mating）、screw=panel-on-gasket 接触
- 关键关节 type/axis/range：hinged REVOLUTE −X `[0, lid_open]`、screw PRISMATIC +Z `[0, lift_travel]`
- copied objects（gland/terminal/boss/ear/ring）遵循 `name_{i}` + 共享 helper，绝不复制粘贴 N 块
- gland 用一根 `gland_specs` loop（不复制粘贴 `_add_gland`）
- `KnobGeometry` ribbed nut 保真（不降级为裸 Cylinder）；round 用 `LatheGeometry`（不降级为 Box）

## Reject cases

- gland 用复制粘贴的 `_add_gland_0..N` 而非单一 `gland_specs` 循环
- 把 terminal strip / gland / gasket 做成 FIXED-joint 独立 part（违反 Rule 1）
- cover 关节缺失或成 0-joint（"固定盖"）
- round 把 `LatheGeometry` 壁降级为 `Cylinder`/`Box`，或 gland 把 `KnobGeometry` 降级为裸柱
- 闭合 cover 悬空（与壳无接触路径）或穿入壳体 / gasket
- hinged cover 开合中途 cover_hinge_leaf 撞后壁（mid-travel 穿模）
- N 增大时 gland 沿壁互相穿模（未按 N 抬升 L_eff/R_eff）
- 内部 terminal/ground_lug 浮在 floor 之上（未嵌入 → island）
- palette 全程单色（未把 shell 材质接到 `palette_style`）
- 生成 wire spline tube 却成 disconnected island（本模板主动不生成 wire）

## 与相邻类别的边界

- 不该混入：**Distribution board / breaker panel / consumer unit**（有 DIN-rail 断路器阵列 + 门锁面板，
  内部密度与门机构不同；junction box 内部只是 terminal strip 或空腔）。
- 不该混入：**Conduit fitting / cable coupling / gland-only union**（纯螺纹管接头，无封闭 terminal 腔、
  无盖、无 gasket lip；junction box 必须是"封闭腔 + 盖 + gasket + glands"）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | spec authored from 3 origins + 4 forks; maps onto the Accessories_Cushion mixed pattern (enclosure≈base, cover≈lid mechanism, interior, gland≈pan multiplicity). |

## 模板实现备注（可选）

- 共享 helper：`_emit_gland`（gland stack）、`_emit_terminal_strip`、`_enclosure_walls`（rect/round 分支）、
  `_emit_hinged_cover` / `_emit_screw_cover`。
- captured-pin overlap：`allow_overlap(cover, enclosure, elem_a="cover_hinge_pin_{i}", elem_b="base_hinge_barrel_{i}")`。
  cover 端 pin 在 pivot 轴上（local (x,0,0)），旋转不平移 → 全程连通且不新增 mid-travel 穿模。
- barrel 沿 X 交错（base 2 段外侧、cover pin 内侧）以贴合真实铰链读感；连通靠 pin-in-barrel overlap，非靠 barrel-barrel 接触。
- 参考模板：`agent/templates/Accessories_Cushion.py`（同构 mixed：footprint/lid-mechanism/interior/multiplicity）。
