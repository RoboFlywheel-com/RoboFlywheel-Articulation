# Healthcare / Prosthetic limb — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_Prosthetic_limb` |
| template path | `agent/templates/Healthcare_Prosthetic_limb.py` |
| test path (optional) | `tests/agent/test_Healthcare_Prosthetic_limb_template.py` (skipped while authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 (2 parents + 4 forked variants) |
| read_count | 6 |
| read_scope | all sources in `Healthcare__Prosthetic_limb.md` source map |
| source_index_policy | only adopted module sources are indexed below |

Sources (all under `data/records/<id>/revisions/rev_000001/model.py`):
- **S1** `rec_a-below-knee-trans-tibial-prosthetic-leg-a-conto_...1fb23a2c` — carbon/beige trans-tibial: mesh socket shell + carbon wraps + pyramid adapter + skeletal cadquery pylon + carbon J-blade; ankle REVOLUTE.
- **S2** `rec_a-modern-below-knee-prosthetic-leg-with-a-blue-s_...a594c50c` — clinical-blue: monolithic leg + articulated rubber-soled foot (toe pod + treads + red energy coil) + bail handle; ankle REVOLUTE.
- **S3** `rec_prosthetic_var_above_knee` — inserts polycentric `knee_joint` block (socket→knee REVOLUTE, knee→pylon FIXED) → trans-femoral.
- **S4** `rec_prosthetic_var_sach_foot` — solid SACH foot (`section_loft` shoe-last body) on the S1 spine.
- **S5** `rec_prosthetic_var_foam_cover` — lifelike cadquery cosmesis foam sleeve over the pylon.
- **S6** `rec_prosthetic_var_shock_pylon` — telescoping shock/damper pylon (adapter→shock_pylon PRISMATIC, visible helical coil).

## 核心身份

A **below-knee (trans-tibial) prosthetic LEG**, optionally **above-knee (trans-femoral)** when a knee joint is inserted. Physically it is a serial chain **socket → [knee] → pylon/shank → ankle → foot** authored upright in meters (~0.50–0.62 m tall). The proximal socket is a sculpted open cup that cradles the residual limb; below it a metal coupler/adapter or a polycentric knee ties the socket to a shank (exposed skeletal tube, telescoping shock strut, or lifelike foam-covered shank); the shank terminates in an ankle revolute carrying a terminal foot (carbon running blade, articulated jointed-look foot, or solid SACH foot).

Not to be confused with: a **prosthetic arm/hand/hook** (structurally distinct terminal device — EXCLUDED; would break the "leg" reading), a **robotic/humanoid leg** (`robotic_leg` — powered multi-DOF actuator chain, not a socket-mounted assistive device), or an **orthotic brace/exoskeleton** (straps onto an intact limb rather than replacing one).

## 槽位 + 候选模块表

### Slot A：foot / terminal device （③ Primary Form Family — form-dominated slot）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `running_blade` | forked_anchor | S1 | L300-L332 (`_running_blade_geometry`), L467-L484 (blade part) | eligible if compatible | carbon C/J ribbon blade (`_add_ribbon` mesh) + heel leaf + ankle_pin + blade_neck. `form_subtype = Macro Surface Construction` (swept ribbon spring). |
| `sach_foot` | forked_anchor | S4 | L250-L305 (`_sach_foot_body_geometry`), L440-L451 (part) | eligible if compatible | solid `section_loft` shoe-last D-section foam foot + ankle_pin. `form_subtype = Volumetric Envelope Form`. |
| `articulated_foot` | forked_anchor | S2 | L196-L236 (`_sole_shape`/`_foot_upper_shape`), L392-L457 (foot part) | eligible if compatible | cadquery rockered rubber sole + open blue frame + toe pod + tread bars + red energy coil (`tube_from_spline_points`) + ankle hub/pin. `form_subtype = Volumetric Envelope Form` (built-up shoe). |

Three source-backed candidates, each a distinct recognizable foot form family → registered as the ③ Primary-Form-Family slot in §8.5.

### Slot B：knee （below-knee vs above-knee）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `below_knee_none` | forked_anchor | S1 / S2 | S1 L381-L410 (adapter), L486-L499 (FIXED chain) | eligible if compatible | no knee part; socket couples to pylon through a pyramid metal adapter (FIXED). Trans-tibial. |
| `above_knee_polycentric` | forked_anchor | S3 | L207-L302 (`_knee_block_cadquery`), L460-L477 (part), L555-L570 (joints) | eligible if compatible | cadquery polycentric knee block + axle + tube clamp; socket→knee REVOLUTE (y, flexion), knee→pylon FIXED. Trans-femoral. |

Degrade-to-2 justified: knee presence is a binary anatomical level (trans-tibial vs trans-femoral); the source pool offers exactly these two structural states. Both are genuine part-tree/joint-count differences (adds a `knee` part + a REVOLUTE), not a re-skin.

### Slot C：pylon / shank

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `exposed_tube_pylon` | forked_anchor | S1 | L226-L244 (`_pylon_frame_cadquery`), L412-L465 (part) | eligible if compatible | skeletal cadquery shin frame with through lightening windows + blue inserts + round shin tube + fork/yoke bridge. Bare-metal shank. |
| `shock_pylon` | forked_anchor | S6 | L226-L304 (`_spring_coil_geometry`), L475-L537 (part), L565-L573 (PRISMATIC) | eligible if compatible | telescoping damper: damper cap/body/ring FIXED above, `shock_pylon` inner (visible helical coil + piston + bump-stop + fork) PRISMATIC (z) below. Adds a part + a PRISMATIC joint. |
| `foam_cosmesis_cover` | forked_anchor | S5 | L68-L107 (`_cosmesis_cover_shape`) | eligible if compatible | exposed skeletal shank PLUS a lofted cadquery foam cosmesis sleeve (④/③ Macro Surface: lifelike calf reading over the shank). Cover is a host part.visual, not a joint. |

## 槽位图（slot graph）

pattern: linear_chain

```
socket ──[Slot B]──> shank_top ──[Slot C body]──> ankle ──[Slot A]──> foot
  (root)   below_knee_none: socket ─FIXED(z, distal_plate↔adapter top_flange)→ pylon
           above_knee:      socket ─REVOLUTE(y, socket_to_knee)→ knee ─FIXED(z)→ pylon
  Slot C:  exposed / foam:  pylon is one part; ankle parent = pylon
           shock:           pylon(housing) ─PRISMATIC(z, adapter_to_shock)→ shock_pylon; ankle parent = shock_pylon
  Slot A:  ankle_parent ─REVOLUTE(y, ankle_pitch, [-0.30,0.35])→ foot (pin-through-fork, grandfathered)
```

- 接口点位：socket **distal cap face** (part-local z=0) is the proximal mount; every downstream part is authored in its own local frame with frame origin at its top mount face, so chain joint origins sit ON the mating hardware.
- 跨 slot joint：`socket_to_knee` REVOLUTE axis (0,1,0) range [0,knee_upper]; `knee_to_pylon`/`socket_to_pylon` FIXED at the coupler face; `adapter_to_shock_pylon` PRISMATIC axis (0,0,1) [0,0.020]; `ankle_pitch` REVOLUTE axis (0,-1,0) [-0.30,0.35].
- 互斥/可选：`knee` part exists only for `above_knee_polycentric`; `shock_pylon` inner part exists only for `shock_pylon`; the pyramid adapter coupler exists only for `below_knee_none` (above-knee's knee tube-clamp is the coupler).

## 每槽位 Module Emits / Interfaces

### socket (root, always)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `socket` | S1 L345-L379 |
| visuals | socket_shell (mesh), liner_edge (mesh), distal_plate (Cyl), carbon wrap bands ×3 (host-derived ④) | S1 L345-L379 |
| downstream interface | distal cap face at local z≈0 (child mounts here) | S1 |

### Slot B / `above_knee_polycentric`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knee` | S3 L460-L477 |
| internal joints | none | — |
| upstream interface | socket distal → `socket_to_knee` REVOLUTE (y) | S3 L555-L563 |
| downstream interface | knee tube-clamp bottom → `knee_to_pylon` FIXED | S3 L564-L570 |

### Slot C / `exposed_tube_pylon` (also base of `foam_cosmesis_cover`)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pylon` | S1 L412-L465 |
| visuals | (adapter coupler if below-knee) + top_collar + skeletal_shin_frame (cadquery) + blue inserts + round_shin_tube + fork_bridge + fork_plate_0/1 (+cosmesis_cover for foam) | S1, S5 |
| upstream interface | pylon top mount face → FIXED from socket/knee | S1 |
| downstream interface | fork plates at ankle z → `ankle_pitch` REVOLUTE | S1 L500-L508 |

### Slot C / `shock_pylon`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pylon` (damper housing) + `shock_pylon` (telescoping inner) | S6 L441-L537 |
| internal joints | `adapter_to_shock_pylon` PRISMATIC axis (0,0,1) [0,0.020] | S6 L565-L573 |
| downstream interface | shock_pylon fork plates → `ankle_pitch` REVOLUTE | S6 L574-L583 |

### Slot A / foot modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | `foot` | S1/S4/S2 |
| visuals | foot body (blade ribbon / sach loft / built-up shoe) + ankle_pin (all feet) | S1 L467-L484, S4 L440-L451, S2 L392-L457 |
| upstream interface | ankle_pin at foot-local origin (pin-through pylon fork) → `ankle_pitch` REVOLUTE | S1 L500-L508 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `foot_module` | enum | running_blade / sach_foot / articulated_foot | — | choice | procedural sampler | Slot A |
| `knee_module` | enum | below_knee_none / above_knee_polycentric | — | choice | procedural sampler | Slot B |
| `pylon_module` | enum | exposed_tube_pylon / shock_pylon / foam_cosmesis_cover | — | choice | procedural sampler | Slot C |
| `palette_style` | enum | carbon_titanium / clinical_blue / carbon_red / skin_cosmesis / titanium_brushed / foam_liner_tan | carbon_titanium | choice | procedural sampler | ⑥ |
| `shank_length_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform then clamp; scales skeletal frame height + insert spacing, shifts ankle_z | S1 L226-L244 |
| `foot_scale` | float | [0.92, 1.10] | 1.0 | independent | uniform then clamp; scales foot forward/overall extent | S1/S4/S2 |
| `knee_upper` | float | [1.15, 1.55] | 1.4 | independent | knee flexion upper bound (rad); solved-safe by sampled poses | S3 L562 |
| `ankle_range` | float | fixed [-0.30, 0.35] | — | constant | anatomical ankle pitch envelope | S1 L507 |
| `shock_travel` | float | fixed [0.0, 0.020] | — | constant | telescoping damper stroke | S6 L572 |
| (—) | constraint | — | — | inequality | `ankle_z = shank_top_z - 0.147*shank_length_scale`; fork/round_tube derived from ankle_z (single-sourced) so shank never gaps | interfaces |

连续尺寸采样契约：sample independents (`shank_length_scale`, `foot_scale`, `knee_upper`) → derive `ankle_z`, coupler/fork positions by equation from `shank_top_z` and `shank_length_scale` → clamp in `resolve_config`.

## 7.5 编译预算 / compile budget
自报 **≤40 s/seed**（依据：库内 cadquery 布尔雕刻/放样类 30-60s；本类每 seed 仅构建 1 个 pylon 变体 + 1 个 foot；socket/carbon wraps/blade/adapter 为纯 `MeshGeometry`（快），只有 skeletal 骨架 cadquery 3×`cutThruAll` 与 cosmesis loft/cut 为布尔重活，foam 变体叠加两者）。分档 tessellation：socket 壳 72×10、carbon wrap 72 段、spring coil 24×8、cadquery `tolerance≈0.0008`。N 相同子件复用同一 helper。sweep `--compile-timeout 120`（≈3×）。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots (socket / [knee] / pylon(/shock) / foot) 表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。这是单链命名槽装配（source map 明确 `count_param: none`）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值 / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part | 有 | part-joint 图随 slot 变：{socket,pylon,foot}（3 part/2 joint）; +knee (above); +shock_pylon (shock)。最长链 socket→knee→pylon→shock_pylon→foot。全部 forked_anchor (S1/S2/S3/S6)。 |
| └ multiplicity | 同构件 ×N | 无 | 单链命名槽，无 N 复制（见 §8）。 |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE ankle_pitch (y, S1); REVOLUTE socket_to_knee (y, S3); PRISMATIC adapter_to_shock (z, S6); FIXED couplers。声明的每种在 sweep 均出现（knee/shock 各自 slot）。 |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | **Slot A foot 登记为 ③ slot**：running_blade (Macro Surface swept ribbon) / sach_foot (Volumetric Envelope loft) / articulated_foot (Volumetric Envelope built-up shoe)；均 forked_anchor，登记进 `slot_choices`。pylon 亦有形态差 (skeletal vs damper vs foam-covered)。 |
| ④ 表面装饰 | 叠加表面细节 | 有 | 碳纤维 wrap 饰带 ×3（`_socket_wrap_band_geometry` 由 socket 逐-theta 曲面派生，共形嵌入，record_only S1）; blue/red 插条; cosmesis foam sleeve (S5, host-derived loft)。装饰为宿主 part.visual，非 joint。 |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | `shank_length_scale`[0.90,1.12], `foot_scale`[0.92,1.10]; 关节包络：ankle_pitch (y, [-0.30,0.35]); socket_to_knee (y, [0,knee_upper≈1.4]); adapter_to_shock (z, [0,0.020])。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（qc 默认档）+ targeted `ctx.pose` 每机构一条（ankle 摆动/knee 屈曲后移/shock 上压）。全程不穿模；captured pin/telescope 用 element-scoped allow_overlap。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | `palette_style` ×6：carbon_titanium / clinical_blue / carbon_red / skin_cosmesis / titanium_brushed / foam_liner_tan。材质大类 painted(socket)/metal/foam-rubber/carbon ≥ ceil(0.5×6)=3。每 `.visual(material=...)` 由 palette 驱动。 |

## 拓扑多样性审计

总组合数：A(3 foot) × B(2 knee) × C(3 pylon) = 18 discrete topologies（× palette 6 × 连续 scale → 数千 seed 唯一）。


seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)` 对每 slot `rng.choice` + 连续 scale `rng.uniform`；seed=0 不特殊（普通 procedural draw）。无 curated/modulo 主表。

Procedural Sampling / Sweep Plan：每 seed 独立抽 foot/knee/pylon/palette + scales；无非法组合（所有 18 组合几何可造；above_knee×shock 用短 coupler 亦装配）。compatibility gating：coupler(adapter) 仅 below-knee 出现，shock 内部 part 仅 shock 出现——由 module 内条件生成，不产生悬空。random sweep seeds 0-35（初版）；viewer 目检 0-9 覆盖每 foot / knee level / pylon。

Topology target：1000-seed 下 discrete topology 上限 18（类别本征离散度）；palette+scale 使 seed 唯一度 按 ≥300 report-only 口径观察。18 <300 属类别兼容约束（单链命名槽，非 multiplicity 类）——已说明。

Controlled local parameterization：`shank_length_scale`, `foot_scale`, `knee_upper`——均在 `resolve_config` clamp；`ankle_z` 等接口量由 `shank_top_z`/scale 单源派生（Contract 3c），不破坏 InterfaceSpec/fork 对齐。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order foot/knee/pylon/palette + uniform scales; rng=Random(seed) | slot_choices_for_seed == build choices |
| compatibility matrix | all 18 legal; adapter↔below-knee, shock-inner↔shock gated in-module | no floating / collision / axis / closed-pose failures |
| controlled local variation | shank/foot scales, knee_upper; clamped + derived ankle_z | proportions vary, fork/ankle stay mated |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial, 0-999 maturity | axis_realization per slot |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A foot | 3 | yes | yes | ③ primary form family |
| B knee | 2 | yes | no | binary anatomical level, degrade-to-2 justified |
| C pylon | 3 | yes | yes | |

## Validator

- `slot_choices_for_seed` returns implemented module names (foot/knee/pylon/palette)
- `config_from_seed` uses deterministic procedural sampling for all seeds incl. 0
- compatibility gating prevents floating adapter / orphaned shock part
- key joints: ankle_pitch REVOLUTE y; socket_to_knee REVOLUTE y (above); adapter_to_shock PRISMATIC z (shock)
- controlled scales clamped; ankle_z single-sourced from shank_top_z
- every non-FIXED child part has a support path (pin-through-fork contact / captured overlap); FIXED coupler origins on welded interface
- sampled-pose collision clean + one targeted pose per mechanism (Rule 5)

## Reject cases
- Prosthetic ARM/hand/hook terminal device (breaks the leg reading) — excluded.
- Downgrading mesh socket shell / blade ribbon / sach loft / cadquery pylon to Box/Cylinder placeholders (Rule 3).
- Carbon wrap band at constant radius standing proud of the tapered socket (Rule 4) — must derive from `_socket_surface_point`.
- Floating pyramid adapter or shock inner part with no support path.
- Ankle/knee joint穿模 mid-travel (Rule 5) or shank gapping off the fork when `shank_length_scale` changes.
- Monochrome batch (palette not driving every visual).

## 与相邻类别的边界
- 不该混入：prosthetic arm/hand（结构迥异的 terminal device，会破坏每个 seed 的 "leg" 读法）。
- 不该混入：`robotic_leg`（powered humanoid 多 DOF 执行链，非 socket 假肢）。
- 不该混入：orthosis/exoskeleton（绑在完好肢体上，非替换缺失肢体）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Two source families (carbon S1/S3/S4/S6 upright-negative-z chain; clinical S2/S5) unified onto the S1 socket→pylon→ankle spine; S2 foot + S5 cosmesis + S6 shock adapted as slot candidates. |
