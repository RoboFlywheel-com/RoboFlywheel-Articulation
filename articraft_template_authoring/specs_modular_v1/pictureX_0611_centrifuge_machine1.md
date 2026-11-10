# pictureX_0611_centrifuge_machine1 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_centrifuge_machine1` |
| template path | `agent/templates/pictureX_0611_centrifuge_machine1.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_centrifuge_machine1_template.py` (skipped while batch-authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (rotor tube-station multiplicity + parallel structural children for lid / body / base / controls, all parenting the housing root) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 (1 origin + 10 forked/probe anchors) |
| read_count | 11 |
| read_scope | all 5-star samples in this subcategory (origin fully read; 10 forks read via targeted structural extraction of joints / part trees / multiplicity constants / body geometry) |
| source_index_policy | only adopted module sources are indexed below |

Sources read (record id → adopted structure):
- `rec_picturex_0611__centrifuge_machine1__001__png__redo_...` (ORIGIN) — teardrop housing loft, recessed rotor well, 6-place fixed-angle rotor (radial stations), rear-hinged translucent cyan dome, front latch + push button, 4 embedded feet. **Gold reference for all shared geometry.**
- `rec_..._var_rotor_n12` / `rec_..._var_rotor_n24` — HOLDER_COUNT param replaces hard-coded 6; stations at `tau/N`.
- `rec_..._var_swing_bucket` — BUCKET_COUNT=4; rotor cross_arms + trunnions; per-bucket `bucket_hinge_i` REVOLUTE children of rotor while `rotor_spin` stays CONTINUOUS.
- `rec_..._var_lift_lid` — `lid_lift` PRISMATIC +z; guide sockets on lid.
- `rec_..._var_sliding_lid` — `lid_slide` PRISMATIC +y; side rails.
- `rec_..._var_clinical_box` — boxy filleted `rect().extrude().fillet()` cabinet shells + circular rotor-well cut.
- `rec_..._var_microfuge` — tall round `Cylinder` column body, small rotor well.
- `rec_..._var_plinth_base` — continuous static `plinth_base` skirt instead of 4 feet.
- `rec_..._var_probe_clinical_swing_bucket` — GATED PROBE: boxy well wall vs swing-bucket envelope + closed-lid crown clearance (converged).
- `rec_..._var_probe_sliding_lid_n24` — GATED PROBE: flat sliding cover clearance over a dense 24-cap ring (converged).

## 核心身份

台式实验室离心机 (benchtop laboratory centrifuge)：一个带盖的外壳 (lidded housing) 包住一个**电机驱动、持续旋转的转子** (motor-driven CONTINUOUS-spinning rotor)，转子在**倾斜插孔** (angled slots/stations) 中固定样品管；由一个**真实的非固定盖关节** (non-fixed lid joint) 打开进入。默认成熟域 = 285×325×450 mm 级台式单元，6–24 管固定角转子或 4–6 桶摆动转子，白/灰外壳 + 黑转子 + 半透明彩色安全盖 + 金属主轴。

必须保留 (must_keep)：lidded housing enclosure；spinning tube rotor as CONTINUOUS joint (`rotor_spin`)；angled tube slots/stations on the rotor；a real non-fixed lid joint over the rotor。

不该混入 (must_not_become)：food blender（无盖、刀片在杯底、无插管环）、spin dryer（大桶脱水、无倾斜管位）、turntable（唱盘 + 唱臂，无盖无插管）、salad spinner（手压绳驱动篮、非电机连续轴）、drone motor（裸露螺旋桨、无外壳无盖）。

## 槽位 + 候选模块表

### Slot A：rotor（转子 + 管位复制，① multiplicity + ② 摆桶机制）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_rotor` (N∈{6,12,24}) | origin_anchor / forked_anchor | origin `range(6)`; `var_rotor_n12`; `var_rotor_n24` | origin L335-L381; n24 L346-L387 | eligible if compatible | rotor part: spindle+central_hub+outer_ring+spindle_cap，加 N 个 loop-emitted 站簇 `radial_support_i`+`rotor_arm_i`+`tube_holder_i`+`tube_cap_i`（径向 `tau/N`）。转子唯一关节 = `rotor_spin` CONTINUOUS。 |
| `swing_bucket` (K∈{4,6}) | forked_anchor | `var_swing_bucket` (BUCKET_COUNT=4)；probe `var_probe_clinical_swing_bucket` | swing L344-L455; probe L442-L505 | eligible if compatible | rotor part 加 K 个 `cross_arm_i`+`trunnion_i` 视觉；再挂 K 个 `bucket_i` part，各由 `bucket_hinge_i` REVOLUTE（切向轴）挂到 rotor。`rotor_spin` 仍为 CONTINUOUS —— 真正的 ②+K 结构候选。 |

结构差异：fixed vs swing 改变 rotor 的 part 树（swing 新增 K 个 part + K 个 REVOLUTE 关节）；N/K 改变 multiplicity。

### Slot B：lid_mechanism（盖机制，② joint/mechanism）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_clamshell` | origin_anchor | origin `lid_hinge` REVOLUTE | origin L212-L294 | eligible if compatible | 后置横轴翻盖穹顶；`lid_hinge` REVOLUTE axis=x，closed→open ~105°；铰链 barrel/tab + housing hinge_mount。 |
| `lift_up` | forked_anchor | `var_lift_lid` `lid_lift` PRISMATIC z | lift L212-L301 | eligible if compatible | 竖直升降穹顶；`lid_lift` PRISMATIC +z，closed→上升 ~0.12 m；导向 socket + housing guide post。 |
| `sliding` | forked_anchor | `var_sliding_lid` `lid_slide` PRISMATIC y | slide L200-L290 | eligible if compatible | 水平滑盖；`lid_slide` PRISMATIC +y，closed→后滑 ~0.20 m；两侧滑轨 rail。 |

每个候选保持真实非固定盖关节；每个盖关节都带 MatingContract（closed pose 盖座面 ↔ housing 座面）。

### Slot C：body_form（③ Primary Form Family — 形态主导 slot，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| `rounded_teardrop_mini` | origin_anchor | origin `_lofted_outline(footprint)` | origin L90-L159 | Volumetric Envelope Form | cadquery 泪滴放样 lower_shell + upper_deck（curved），圆形转子井 cut。 |
| `boxy_clinical` | forked_anchor | `var_clinical_box` `rect().extrude().fillet()` | clinical L108-L169 | Planar Boundary Form | 圆角矩形立柜壳（filleted 竖边 = 真实曲面边），矩形投影轮廓。 |
| `tall_microfuge` | forked_anchor | `var_microfuge` round column | microfuge L100-L200 | Volumetric Envelope Form | 高窄圆柱塔（Cylinder，curved），小转子井。 |

三种可识别主体形态原型；同一 part tree（housing root）、同一 primitive 家族（cadquery loft/rect-extrude + Cylinder，均为真实曲面，非 Box 降级）、同一 rotor/lid 接口。**符合 §8.5 ③ 形态主导要求。**

### Slot D：support_base（③ support topology）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `elastomer_feet` | origin_anchor | origin `foot_0..3` loop | origin L161-L170 | eligible if compatible | 4 个嵌入橡胶脚（housing 视觉，非独立 part）。 |
| `plinth_skirt` | forked_anchor | `var_plinth_base` `plinth_base` | plinth L160-L175 | eligible if compatible | 连续裙座 skirt（housing 视觉）。 |

**单-degrade 说明：** support_base 仅 2 candidate。理由（源图 underfilled_reason）：整个小类只有 **1 个 origin**，结构覆盖靠 forked_anchor 扩展；支撑拓扑在源图里仅记录 feet（origin）+ plinth（1 个 fork），无第三个 source-backed 支撑候选。诚实上限，不用世界知识硬造第三支撑骨架（会违反 §4 硬约束）。2 candidate 均 source-backed，两者都是 housing 表面视觉（非独立 part），风险低。

### Slot palette_style（⑥ 涂装，非结构 slot，登记进 slot_choices 做覆盖）
`clinical_white` / `lab_gray` / `cyan_dome` / `amber_dome` / `graphite` — 5 组配色，每组 translucent 盖 tint + white/gray housing + black rotor + satin metal spindle + white caps。目标 4–6，材质大类覆盖 glass(半透盖) + plastic(壳/盖框) + metal(主轴/铰链)。

## 槽位图（slot graph）

pattern: mixed（multiplicity + parallel_children，全部 parent 到 housing root）

```
                         housing (root, built by Slot C body_form + Slot D support_base)
                          │
      ┌───────────────────┼───────────────────┬────────────────────┐
      │                   │                   │                    │
  [rotor_spin           [lid joint          [latch_pivot         [button_travel
   CONTINUOUS z]         REVOLUTE x /         REVOLUTE z]          PRISMATIC -z]
      │                  PRISMATIC z /         front_latch          control_button
   rotor (Slot A)        PRISMATIC y]          (record_only ④)      (record_only ④)
      │                   lid (Slot B)
   ┌──┴── (swing only)
   │
  bucket_i (×K)
   [bucket_hinge_i REVOLUTE, tangential axis]
```

接口点位：
- `rotor_spin`：housing `rotor_socket` 顶面 (positive_z) ↔ rotor `central_hub` 底面 (negative_z)，axis=(0,0,1)，CONTINUOUS，origin 在转子井 mount plane。**带 MatingContract。**
- lid joint（三选一）：closed pose 下 lid 座接面 ↔ housing 座面，**带 MatingContract**。REVOLUTE(hinged, axis x, [0, ~1.83]) / PRISMATIC(lift, axis +z, [0,~0.12]) / PRISMATIC(slide, axis +y, [0,~0.20])。
- `bucket_hinge_i`（仅 swing）：rotor `trunnion_i` ↔ bucket，切向 axis `(sin θ,-cos θ,0)`，REVOLUTE [0, ~80°]，captured-trunnion → 省略 mating（grandfathered）+ element-scoped allow_overlap。
- `latch_pivot` REVOLUTE z / `button_travel` PRISMATIC -z：captured pin/boss → 省略 mating（grandfathered）+ allow_overlap。

互斥/派生：swing_bucket ⊗ 任意 lid 合法（probe 已收敛 clinical×swing）；sliding lid ⊗ N=24 合法（probe 已收敛）。body_form 与 lid/rotor 正交。

## 每槽位 Module Emits / Interfaces

### Slot A / fixed_rotor
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rotor`（spindle+central_hub+outer_ring+spindle_cap + N×(radial_support_i, rotor_arm_i, tube_holder_i, tube_cap_i)） | origin L296-L381 |
| internal joints | 无（站簇为 rotor rigid 视觉） | origin |
| upstream interface | rotor `central_hub` negative_z ↔ housing `rotor_socket` positive_z，`rotor_spin` CONTINUOUS | origin L383-L396 |

### Slot A / swing_bucket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rotor`（+ K×(cross_arm_i, trunnion_i)）+ K×`bucket_i`（bucket_body+bucket_bottom+tube_cap） | swing L344-L455 |
| internal joints | `rotor_spin` CONTINUOUS + K×`bucket_hinge_i` REVOLUTE（rotor→bucket_i） | swing L375-L453 |
| interface | trunnion_i 捕获 bucket 铰（切向 axis），rotor_spin 同上 | swing L436-L453 |

### Slot B / hinged_clamshell | lift_up | sliding
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（transparent_panel loft + perimeter_rim + hinge_barrel/tab 或 guide_socket 或 runner） | origin L212-L282; lift L266-L289; slide |
| internal joints | `lid_hinge` REVOLUTE / `lid_lift` PRISMATIC z / `lid_slide` PRISMATIC y | origin L284; lift L291; slide L286 |
| upstream interface | closed pose：lid 座接面 ↔ housing 座面（MatingContract） | 各 lid 变体 |

### Slot C / body_form + Slot D / support_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（lower_shell + upper_deck(rotor well cut) + panel_seam + rotor_well_floor + rotor_socket + hinge_mount_i + latch_boss + control_bezel + feet/plinth） | origin L106-L211; clinical L108-L198; microfuge L100-L200; plinth L160-L175 |
| internal joints | 无（housing 是 root，唯一根 part） | — |
| downstream interface | rotor_socket / hinge_mount / lid-seat 面供上述子件挂接 | origin |

### 控制件（④ record_only，always present）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_latch`（latch_shaft+latch_handle+latch_tip）、`control_button`（button_body） | origin L398-L442 |
| joints | `latch_pivot` REVOLUTE z、`button_travel` PRISMATIC -z（captured，无 mating） | origin L417-L442 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `rotor_type` | enum | fixed_rotor / swing_bucket | fixed_rotor | choice | procedural sampler | Slot A |
| `tube_count` | int (mult) | fixed:{6,12,24}；swing:{4,6} | 6 | conditional | 域随 rotor_type：fixed∈{6,12,24}, swing∈{4,6} | swing L25 / n24 L21 |
| `lid_mechanism` | enum | hinged_clamshell / lift_up / sliding | hinged_clamshell | choice | procedural sampler | Slot B |
| `body_form` | enum | rounded_teardrop_mini / boxy_clinical / tall_microfuge | rounded_teardrop_mini | choice | procedural sampler | Slot C |
| `support_base` | enum | elastomer_feet / plinth_skirt | elastomer_feet | choice | procedural sampler | Slot D |
| `palette_style` | enum | clinical_white / lab_gray / cyan_dome / amber_dome / graphite | cyan_dome | choice | procedural sampler | ⑥ |
| `body_scale` | float | [0.90, 1.18] | 1.0 | independent | 均匀采样后 clamp；缩放 housing 外形 | origin dims |
| `rotor_scale` | float | derived | 1.0 | equation | `= clamp(0.94..1.06 · f(tube_count))`；N 大→station_radius/outer_ring 略增以容纳更多站 | n24 L346 |
| `lid_open` | float | hinged[1.4,1.83] / lift[0.09,0.13] / slide[0.16,0.22] | — | conditional | 行程范围随 lid_mechanism；clamp | origin L292/lift L299/slide |
| (—) | constraint | — | — | inequality | `station_ring_radius + holder_r ≤ rotor_well_radius − 0.002`（管环落在井内）；`closed_lid_crown_z ≥ tallest_cap_world_z + 0.020`（闭盖清顶）；违反→回缩 rotor_scale / 抬高 dome | origin L676-L703 |

连续尺度契约：先采 `body_scale`（independent）→ 派生 `rotor_scale`（equation，依 tube_count）→ 投影 inequality（管环 ⊂ 井、闭盖清顶）→ 解析 `lid_open`/`tube_count` conditional 范围。全部在 `resolve_config` 求解。

## 7.5 编译预算 / compile budget

**自报预算：≤ 20 s/seed。** 依据：本类别用 cadquery 放样壳/穹顶 + 布尔井 cut，但**分档 tessellation**（tolerance 0.0012–0.0015，主体 loft 3–5 profiles）实测每个 cadquery 面 0.1–0.4 s、整机 housing+lid 放样 < 1.5 s（origin 用 0.0005 精细精度才到 ~8.8 s，本模板刻意降精度）。Box/Cylinder body_form 更快。N 个相同管位复用 `Cylinder` primitive（非 mesh）。sweep watchdog `--compile-timeout 120`（~6× 预算，仅挂死保护）。

## Multiplicity / Copy Logic

**轴 1：tube_count（fixed_angle 管位）**
- `count_param`: `tube_count`（替换 origin 硬编码 `range(6)` 与 rotor.meta holder_count/holder_spacing_deg）。
- `N_range`: 产品域 {6,12,24}（bench-scale 固定角转子标准位数）；测试偏小（6 高频）。sampling domain 权重：6 高频、12 中、24 稀有。
- copied object: 每站簇 = `radial_support_i` + `rotor_arm_i` + `tube_holder_i` + `tube_cap_i`。
- naming: 稳定后缀 `_i`；placement: 径向 `angle = i·tau/N`、共享 `station_ring_radius`；joint policy: 站簇为 rotor rigid 视觉（**不新增关节**，`rotor_spin` 为 rotor 唯一关节）。
- source/gating: origin(6)/n12/n24。

**轴 2：bucket_count（swing_bucket 摆桶）**
- `count_param`: `tube_count`（swing 语义下即桶数 K）。
- `N_range`: {4,6}（bench-scale 摆桶转子）；4 高频。
- copied object: 每桶 = rotor 上 `cross_arm_i`+`trunnion_i` 视觉 + 独立 `bucket_i` part（bucket_body+bucket_bottom+tube_cap）+ `bucket_hinge_i` REVOLUTE。
- naming: `_i`；placement: 径向 `i·tau/K`、`BUCKET_TRUNNION_RADIUS`；joint policy: **每桶新增 1 个 REVOLUTE（rotor→bucket_i，切向轴），`rotor_spin` 仍 CONTINUOUS**。
- source/gating: `var_swing_bucket`(4) + probe。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | (a) fixed_rotor（rotor 无子 part）vs swing_bucket（rotor + K 个 bucket part + K REVOLUTE）；(b) support feet vs plinth。均 source-backed（origin / var_swing_bucket / var_plinth_base）。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：fixed N∈{6,12,24}、swing K∈{4,6}，权重小 N 高频。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | lid: REVOLUTE(hinged,x) / PRISMATIC(lift,+z) / PRISMATIC(slide,+y)；rotor: CONTINUOUS(z) 恒定 + swing 每桶 REVOLUTE(切向)；latch REVOLUTE(z) + button PRISMATIC(-z) 恒有。均 forked/origin source-backed；每种在 sweep 出现。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | rounded_teardrop_mini(Volumetric Envelope, origin loft) / boxy_clinical(Planar Boundary, var_clinical_box filleted rect) / tall_microfuge(Volumetric Envelope, var_microfuge round column)。登记进 slot_choices。source-backed。 |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | control_bezel、latch/button、panel_seam(模缝)、hinge boss —— host-conformal，写成 housing/ lid 视觉，随 ③⑤ 共形；无独立 variant（source map 记 record_only）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | body_scale[0.90,1.18]、rotor_scale(derived)、lid_open(conditional)。运动包络：lid_hinge axis=x 开向 +z [closed=0, open ~1.83]；lid_lift axis=+z [0,0.12]；lid_slide axis=+y [0,0.20]；rotor_spin continuous 整圈；bucket_hinge 切向 [0,80°]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（max_pose_samples 按关节数 32–64）+ targeted `ctx.pose`：盖 open(升/翻/滑到 upper 有位移) & closed(清顶 caps)、rotor 转 90°/180° 仍在盖内、swing bucket q=0 竖挂/q=upper 外摆。continuous 整圈不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette（clinical_white/lab_gray/cyan_dome/amber_dome/graphite）；材质大类 glass(半透盖)+plastic(壳/框)+metal(主轴/铰链) 全覆盖（≥ceil(0.5×5)=3）。 |

**收尾自检**：0-9 seed 渲染须肉眼见：三种 body form 拉得开、盖三机制开合可辨、6/12/24/swing 管数不同、配色变化、闭盖清顶不穿模。

## 采样与覆盖审计

总组合数（离散）：rotor_type×N/K (3 fixed N + 2 swing K = 5) × lid (3) × body_form (3) × support_base (2) × palette (5) = 5×3×3×2×5 = **450**（未计连续 scale）。>300，够成熟度观察。

理由：mixed 模板，主多样性来自离散 slot（rotor 结构+N、lid 机制、body form、base、palette），连续 scale 仅微调比例。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对每个 seed 用 `random.Random(seed)` 做加权离散采样 + 连续 scale 均匀采样；seed=0 不特殊（走同一 procedural 路径）。无 curated/modulo 主表。
Topology target：1000-seed slot tuple 覆盖 report-only；本类别真实离散空间 450，兼容约束少（probe 已收敛 clinical×swing、slide×n24），预期覆盖 > 300。
Procedural Sampling / Sweep Plan：加权 `random.choices`（小 N 高频）；compatibility gating 在 `resolve_config`（tube_count 域随 rotor_type、lid_open 域随 lid_mechanism、inequality 回缩 rotor_scale）。无 regression override。random sweep 0-35 初测、viewer 目检 0-9。
Controlled local parameterization：`body_scale`(independent,[0.90,1.18])、`rotor_scale`(equation,依 N)、`lid_open`(conditional,依 lid)。全部在 `resolve_config` clamp/派生/投影，不破坏 MatingContract / multiplicity / 接口。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted discrete slot choice + uniform scale；slot 顺序 body_form→support→rotor→lid→controls | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | tube_count 域 gate by rotor_type；lid_open gate by lid_mechanism；inequality 回缩 rotor_scale / 抬 dome | 无 floating / collision / 闭盖穿顶 / 管环越井 / bucket 越壁 |
| controlled local variation | body_scale / rotor_scale / lid_open clamp | 比例变化不破接口、clearance、joint origin、类别 identity |
| regression overrides | none | — |
| random sweep | 0-15 fast, 16-35 final, + corner | contract failures; axis_realization; viewer 目检 0-9 |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| rotor_type | 2 (fixed/swing) + N/K mult | yes | (mult 扩) | swing 是真 ②+K 结构候选 |
| lid_mechanism | 3 | yes | yes | REVOLUTE/PRISMATIC×2 |
| body_form | 3 | yes | yes | ③ 形态主导，三原型 |
| support_base | 2 | yes | no | 源图 underfilled（单 origin），诚实上限；均 source-backed housing 视觉 |
| palette | 5 | yes | yes | ⑥ |

拓扑审计（gated probes）：
- `boxy_clinical × swing_bucket`：桶摆动包络 vs 方壳井壁 + 闭盖 crown 清桶 —— 源 probe 已收敛；本模板保 rotor_well_radius 与 bucket envelope 一致、闭盖 dome crown 抬高。sweep 须覆盖此组合。
- `sliding_lid × N=24`：平滑盖清过密 24 顶帽环 + 滑程 vs 转子直径 —— 源 probe 已收敛；本模板 slide 盖 crown 覆盖 tallest cap，滑程不与壳穿模。sweep 须覆盖此组合。

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（rotor_type+N、lid、body_form、support、palette）。
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic procedural sampling。
- compatibility gating 阻止非法组合（tube_count 域、lid_open 域）。
- 无 regression override / 无 curated 主表。
- controlled scale 都 clamp，不破接口/clearance/joint origin/multiplicity。
- 跨部件 scale 依赖（rotor_scale equation、管环⊂井 / 闭盖清顶 inequality）在 `resolve_config` 解。
- 关键 MatingContract：`rotor_spin`(rotor_socket↔central_hub)、lid joint（座面）存在。
- 关键关节 type/axis/range：rotor_spin CONTINUOUS z；lid REVOLUTE x 或 PRISMATIC z/y；swing bucket_hinge_i REVOLUTE；latch REVOLUTE、button PRISMATIC。
- copied objects 遵循 `_i` 命名 + 径向 `tau/N` 放置。
- **专项**：rotor 关节为 CONTINUOUS 且 tube/bucket 数与 config 一致；闭盖 sampled pose 清最高 cap。

## Reject cases

- rotor 关节不是 CONTINUOUS（退化成 REVOLUTE/FIXED）→ reject。
- 无真实非固定盖关节（盖被 FIXED 或省略）→ reject。
- 管位数与 config.tube_count 不符，或管环越出转子井 → reject。
- 闭盖穿最高 tube_cap / spindle_cap（清顶 < 20 mm）→ reject。
- swing_bucket 未给每桶 REVOLUTE，或桶穿井壁/相邻桶 → reject。
- housing 用纯 Box 冒充圆润壳（rounded_teardrop/microfuge 降级为 Box 无曲面）→ reject（违 Rule 3）。
- 装饰件（bezel/seam/latch）做成独立 FIXED part 悬浮 → reject（违 Rule 1）。
- lid/rotor 子件无 MatingContract 且非 captured-pin 豁免 → reject（违 Rule 2）。

## 与相邻类别的边界

- 不该混入 food blender：离心机有盖 + 倾斜插管环 + 转子 recessed 在井内；blender 无盖、刀在杯底、无插管。
- 不该混入 spin dryer / salad spinner：离心机是电机 CONTINUOUS 主轴 + 倾斜管位；脱水机/沙拉甩干是大桶/手驱篮、无倾斜管位。
- 不该混入 turntable：离心机有盖罩住转子、无唱臂；turntable 有唱臂 + 开放唱盘、无盖无插管。
- 不该混入 drone motor：离心机有外壳 + 盖 + 插管；drone 是裸露螺旋桨、无壳无盖。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 单 origin 小类；结构覆盖靠 forked/probe anchors（source map underfilled_reason 已记录）。support_base 仅 2 candidate 为诚实上限。swing×clinical、slide×n24 为源已收敛的 gated probe，模板须在 sweep 覆盖。 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot C/A/B | housing+rotor+lid | ORIGIN redo_...51206fe6 | L59-L446 | 全部共享几何 gold reference |
| S2 | Slot A | fixed_rotor N | var_rotor_n12 / var_rotor_n24 | n24 L21,L346-L387 | HOLDER_COUNT param + 站簇 loop |
| S3 | Slot A | swing_bucket | var_swing_bucket | L25-L30,L344-L455 | 桶 part + bucket_hinge REVOLUTE + trunnion |
| S4 | Slot B | lift_up | var_lift_lid | L266-L301 | lid_lift PRISMATIC z + guide socket |
| S5 | Slot B | sliding | var_sliding_lid | L200-L290 | lid_slide PRISMATIC y + rails |
| S6 | Slot C | boxy_clinical | var_clinical_box | L108-L169 | filleted rect 壳 |
| S7 | Slot C | tall_microfuge | var_microfuge | L100-L200 | round column 塔 |
| S8 | Slot D | plinth_skirt | var_plinth_base | L160-L175 | 连续裙座 |
| S9 | probe | clinical×swing / slide×n24 | var_probe_* | — | gated 组合，sweep 覆盖 |
</content>
</invoke>
