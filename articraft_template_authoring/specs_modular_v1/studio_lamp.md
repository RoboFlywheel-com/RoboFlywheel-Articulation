# Modular Spec — studio_lamp

## 元信息
| 项 | 值 |
|---|---|
| slug | `studio_lamp` |
| template path | `agent/templates/studio_lamp.py` |
| test path (optional) | `tests/agent/test_studio_lamp_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：主脊椎 `support --prismatic(Z)--> stage_i (repeat multiplicity)--> upper_stage --FIXED--> yoke --REVOLUTE(x/y)--> lamp_head`。head_family 是并列的 ③ 主体形态族替换（不改主脊椎）。head_module（barn_doors / focus_barrel）作为 head 上的可选 REVOLUTE/PRISMATIC 子件。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star samples in this category (3 picturex origin + 11 forked variants under `data/records/rec_0611_studio_lamp_*` and `rec_picturex_0611__studio_lamp__*`) |
| source_index_policy | only adopted module sources are indexed below |

全 14 个 5 星样本均已读取 `model.py` 全文。3 个 picturex origin 提供三条 spine 变体（tripod+2-stage 伸缩+softbox；tripod+1-stage+boom+softbox；tripod+1-stage+spotlight-lathe），11 个 forked variant 分别扩了 head_family（round_reflector / led_panel / fresnel）、head_module（barn_doors / focus_barrel）、support（counterweighted_boom_base / rolling_base）、mast_count（1 / 3）、yoke（dual_axis_yoke）、folding（collapsible_tripod）。

## 核心身份

`studio_lamp` = 真实世界的**摄影/影视工作室灯**：一个可折叠地面 support（三脚架 / 滚轮底座 / 配重底座），一根可上下延伸的伸缩 mast column，顶端 yoke 抱住一个 lamp_head（softbox / round reflector / LED panel / fresnel / spotlight can），head 绕水平 trunnion 轴俯仰。head 必须有可辨识的 diffuser/lens 面朝正 +y 出光方向。

**不该混入**：路灯 street_lamp（无 diffuser 灯罩细节，杆件更粗），desk lamp / articulated_task_lamp（无三脚架，为 clamp/base+multi-link 关节链），theater spotlight_on_yoke（低支架简化 pedestal），camera_tripod（无 lamp_head）。

## 槽位 + 候选模块表

### Slot A：support（① 骨架 / ②）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tripod_stand` | forked_anchor | `rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96` | L141-L245 | eligible if compatible | root `base` 部件：hub + hollow_outer_tube + 3×REVOLUTE hinged legs (`leg_i` 各挂 leg_tube spline + rubber_foot + support_brace) + lobed lower_clamp_knob（CONTINUOUS around Z）。 |
| `rolling_base` | forked_anchor | `rec_0611_studio_lamp_var_support_rolling_base` | L178-L275 | eligible if compatible | root `base`：中心 hub + 3 条星形 spider arm + 3×`caster_wheel_i` CONTINUOUS 轮 + column hollow tube。腿被换为轮子（CONTINUOUS wheels 替代 REVOLUTE legs）。 |
| `counterweighted_boom_base` | forked_anchor | `rec_0611_studio_lamp_var_support_counterweighted_boom` | L162-L228 | eligible if compatible | root `base`：加宽 tripod hub（更粗更矮 counterbalance 底座）+ rear counterweight disk (Cylinder mass) 作为 base visual + 3 REVOLUTE legs（angle range 更小，配重脚型态）。 |

### Slot B：head_family（③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| `softbox_rect` | forked_anchor | `rec_picturex_0611__studio_lamp__001__png_...` | L338-L425 | eligible if compatible | `lamp_head` 内含 cadquery loft softbox shell + front_diffuser Box + rear_housing Cylinder + trunnion_shaft + pivot_block；outgoing 光轴 +Y。form_subtype = Volumetric Envelope Form (锥形柔光箱 loft envelope)。 |
| `round_reflector` | forked_anchor | `rec_0611_studio_lamp_var_head_family_round_reflector` | L138-L360 | eligible if compatible | `lamp_head` 换为 parabolic loft dish + 前 rim + 后 necked can；仍然 trunnion + pivot_block；+Y 出光。form_subtype = Volumetric Envelope Form (parabolic 抛物 loft envelope)。 |
| `led_panel` | forked_anchor | `rec_0611_studio_lamp_var_head_family_led_panel` | L34-L45,L321-L400 | eligible if compatible | `lamp_head` 换为 rounded-rect flat panel（Box body + LED grid front + rear yoke bridge）；trunnion 仍在。form_subtype = Planar Boundary Form（矩形圆角平面 boundary）。 |
| `fresnel_can` | forked_anchor | `rec_0611_studio_lamp_var_head_family_fresnel` | L91-L146,L362-L440 | eligible if compatible | `lamp_head` 换为 cylindrical fresnel can（LatheGeometry cylindrical shell + fresnel lens front + rear vent）。form_subtype = Volumetric Envelope Form（圆柱 revolution envelope）。 |
| `spotlight_can` | forked_anchor | `rec_picturex_0611__studio_lamp__003__png_...` | L65-L88,L330-L406 | eligible if compatible | `lamp_head` 用 LatheGeometry `_lamp_shell` 造 satin_aluminum 复杂 revolution can；含 pivot_boss + rear vent bands + carry_handle。form_subtype = Macro Surface Construction（cast can 有 vent band 与 handle 立面）。 |

### Slot C：head_module（可选 ② 附加机构）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | world_knowledge_extrapolation | anchors: `rec_picturex_0611__studio_lamp__001/003` （head 无附加机构） | n/a | eligible if compatible | head 上不加任何机构，直接 pass-through。 |
| `focus_barrel` | forked_anchor | `rec_0611_studio_lamp_var_head_module_focus_barrel` | L34-L60,L433-L490 | eligible if focus_barrel 与 fresnel_can/spotlight_can/softbox_rect 兼容 | 在 head 前面加一个 PRISMATIC ring：`focus_barrel` child 沿 head +Y 轴前后 slide，形成 focus 调节。 |
| `barn_doors_4` | forked_anchor | `rec_0611_studio_lamp_var_head_module_4_barn_doors` | L28-L31,L488-L560 | eligible if head_family in {softbox_rect, led_panel, round_reflector} | 在 head 前挂 4 片 REVOLUTE barn door panels（left/right/top/bottom），围绕 diffuser rim。multiplicity=4 固定。 |

## 槽位图（slot graph）

pattern: `mixed`

```
support (root) --PRISMATIC(z, stage_1)--> stage_1
  --PRISMATIC(z, stage_2 if mast_count>=2)--> stage_2
    --PRISMATIC(z, stage_3 if mast_count==3)--> stage_3
      --FIXED--> yoke
        --REVOLUTE(x, head_tilt)--> lamp_head [head_family]
          --{FIXED / REVOLUTE(×4) / PRISMATIC(y)}--> head_module [head_module]
```

- 主脊椎串联 revolute/prismatic 链，`yoke` 是固定过渡件。
- 每一段 telescoping stage 用 PRISMATIC，共享 hollow_tube 接口（外 outer_tube 面包内 inner_tube 面）；multiplicity 参数 `mast_count ∈ {1,2,3}` 决定 stage 数量。
- `head_family` 决定 lamp_head 的形态、mass、diffuser 位置；接口 = trunnion_shaft cylinder 穿过 yoke bearing bores。
- `head_module` 是 head 的可选并列子件（parallel child），共享 head 前面 diffuser rim / lens plane 作为 mating plane。
- `support` 决定 root 部件的地面接触（3×hinged legs / 3×casters / heavy counterweight），与 stage_1 通过 PRISMATIC 内外套接口相连。

## 每槽位 Module Emits / Interfaces

### Slot A / support

| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`（root），tripod: 3× `leg_i`；rolling: 3× `caster_wheel_i`；counterweighted: 3× `leg_i` + 内含 counterweight visual on base | S1/S2/S3 (parents), S_boom_base, S_rolling_base |
| internal joints | tripod: `base_to_leg_i` (REVOLUTE y-tangent, range [-0.72, 0.05])；rolling: `base_to_caster_i` (CONTINUOUS around wheel axis)；counterweighted: `base_to_leg_i` (REVOLUTE 类似 tripod 但腿较短) | 同上 |
| downstream interface | `base` 顶部 hollow outer_tube 顶端 +Z 面（供 stage_1 inner_tube 沿 z prismatic 插入） | 同上 |

### Slot B (multiplicity) / mast_stages

| emits | 描述 | 来源 |
|---|---|---|
| parts | `mast_stage_i` for i in [0, mast_count-1]；每段 hollow inner tube + top clamp collar visual | S1 L246-L295 / S2 L174-L242 / var_mast_count_1 / var_mast_count_3 |
| internal joints | `stage_{i}_prismatic`：parent=前一 stage (或 base if i=0)，PRISMATIC axis=(0,0,1)，range=(-0.20, 0.15) | 同上 |
| upstream interface | `stage_0`：`base` outer_tube 面沿 +Z 插入；后续 `stage_i` 相同接口（`stage_{i-1}` outer_tube top） | 同上 |
| downstream interface | `stage_{mast_count-1}` outer_tube top +Z 面作为 yoke 座（FIXED） | 同上 |

### Slot ExtraYoke / yoke（固定过渡件，非 slot 但每次必生成）

| emits | 描述 | 来源 |
|---|---|---|
| parts | `yoke` | S1 L297-L336 / S3 L258-L312 |
| internal joints | 无 | — |
| upstream interface | `yoke.receiver_sleeve` bottom -Z 面，FIXED 到 topmost stage top | 同上 |
| downstream interface | `yoke.tilt_boss`/`bearing_pos` 提供左右 trunnion bore（供 head 沿 x/y 轴 REVOLUTE） | 同上 |

### Slot D / head_family

| emits | 描述 | 来源 |
|---|---|---|
| parts | `lamp_head`；每 family 内含 diffuser/lens visual + trunnion_shaft + rear_housing | S1_softbox, S_round_reflector, S_led_panel, S_fresnel, S3_spotlight |
| internal joints | 无（head 是叶节点，若 head_module=none） | — |
| upstream interface | trunnion_shaft cylinder（穿过 yoke 双 bearing），REVOLUTE axis x，range (-0.55, 0.65) | 同上 |
| downstream interface | 前面 diffuser/lens rim 面作为 head_module 挂载面（+Y 方向） | 同上 |

### Slot E / head_module

| emits | 描述 | 来源 |
|---|---|---|
| parts | `focus_barrel`（PRISMATIC）或 4× `barn_door_i`（REVOLUTE）或无 | S_focus_barrel, S_4_barn_doors |
| internal joints | focus_barrel: `head_to_focus_barrel` PRISMATIC (0,1,0) range (0, 0.05)；barn_doors: 4× `head_to_barn_door_i` REVOLUTE，绕 barn door 铰边，range (0, 1.4) | 同上 |
| upstream interface | head 前面 diffuser rim 面 | 同上 |
| downstream interface | 无（leaf） | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support` | enum | tripod / rolling_base / counterweighted_boom_base | tripod | choice | procedural sampler | Slot A |
| `head_family` | enum | softbox_rect / round_reflector / led_panel / fresnel_can / spotlight_can | softbox_rect | choice | procedural sampler | Slot B |
| `head_module` | enum | none / focus_barrel / barn_doors_4 | none | conditional | barn_doors_4 仅在 head_family in {softbox_rect, led_panel, round_reflector}；focus_barrel 与全部 family 兼容 | Slot E |
| `mast_count` | int | {1, 2, 3} | 2 | independent (weighted) | weights (0.30, 0.45, 0.25) | Multiplicity |
| `palette_style` | enum | studio_black / silver_industrial / warm_brass / cinema_grey / arctic_white | studio_black | choice | procedural sampler；全部 material 均来源于 palette | §8.5 ⑥ |
| `column_length_scale` | float | [0.85, 1.15] | 1.0 | independent | 缩放 stage tube 长度 | S1/S2/S3 |
| `mast_travel_scale` | float | [0.80, 1.15] | 1.0 | independent | 缩放每段 PRISMATIC 行程；clamp `travel ≤ 0.30 * tube_length` | 接口 clearance |
| `head_scale` | float | [0.85, 1.20] | 1.0 | independent | 头部整体缩放 | Slot B |
| `leg_spread_scale` | float | [0.90, 1.10] | 1.0 | independent | tripod leg 展开半径 | S1 |
| (—) | constraint | — | — | inequality | `sum(stage_length_i) + yoke_h + head_h/2` ≤ `2.4 m`（保持真实工作室灯尺度） | 接口 |
| (—) | constraint | — | — | inequality | `mast_travel <= 0.9 * inner_tube_length`（保插入深度）| 接口 |

**采样契约**：（1）先采 `support`、`head_family`、`head_module`（`resolve_config` 应用 conditional gate 降级 barn_doors_4 → none 如果 head_family=fresnel_can/spotlight_can）；（2）采 `mast_count` 加权；（3）采所有 scale independent；（4）resolve inequalities → clamp `mast_travel` 与总高。

### 7.5 编译预算 / compile budget

**每 seed ≤ 20 s**（依据：softbox 与 round_reflector 有 cadquery loft cut；spotlight_can 与 fresnel_can 用 LatheGeometry；参考 cushion.py cadquery loft 15-18 s / seed，articulated_task_lamp 5-10 s / seed）。分档 tessellation：
- 小半径 hollow_tube extrude → `.circle(...).extrude` 保持默认 tolerance 0.001。
- LatheGeometry 主 shell `segments=48`（正常）到 `segments=72`（英雄面 spotlight_can, softbox_rect）。
- 复用 mesh：`mast_stage_i` 复用同一 hollow_tube mesh 缓存（模板级 dict 缓存），barn_doors 用共享 Box。
- 超出 20s：先降 lathe segments 到 32，再降 loft workplane 数。

## Multiplicity / Copy Logic

**唯一 multiplicity 轴：`mast_count` ∈ {1, 2, 3}**

- `count_param`: `mast_count`
- `N_range`: `[1, 3]`（真实工作室灯极少超过 3 段伸缩）
- sampling domain: `weights (0.30, 0.45, 0.25)` — 2 段最常见（tripod + boom family），1 段紧凑 spotlight（origin 003 型），3 段最长伸缩（extended booms）。
- copied object: `mast_stage_i` — 每段完全同构（inner_tube visual + top clamp_collar visual + optional knob CONTINUOUS child on the parent stage）。
- naming: `mast_stage_0`, `mast_stage_1`, `mast_stage_2`
- placement: 沿 +z 轴累积堆叠，`stage_i` 的 rest pose 顶端为 `stage_{i+1}` 的 prismatic joint origin。
- joint policy: 每段独立 `stage_{i}_prismatic`（PRISMATIC axis (0,0,1)，range `(-0.20, 0.15) * mast_travel_scale`）。
- source/gating: 见 S_var_mast_count_1（N=1 无 boom）与 S_var_mast_count_3（N=3 telescoping stages）。

**次要 multiplicity（写死不进入 slot_choices）：**
- tripod / counterweighted_boom_base 的 legs 固定为 3（真实工作室灯永远 3 腿；不参数化）。
- rolling_base 的 casters 固定为 3（源 var_support_rolling_base 用 3 caster；不参数化）。
- barn_doors_4 固定 4 片（源固定）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 3 support (tripod 3-leg / rolling 3-caster / counterweighted 3-leg + counterweight visual) + 3 mast_count（1/2/3 段 stage） × head_module presence（none/focus_barrel/barn_doors_4）。全部 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | mast_count ∈ {1,2,3} weights (0.30, 0.45, 0.25)。见 §8。 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE (leg hinge, head tilt, barn doors, knob) / PRISMATIC (mast_stage, focus_barrel) / CONTINUOUS (caster wheels, clamp knobs) / FIXED (yoke→stage_top)。每种在 sweep 都出现。全部 forked_anchor。 |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | 有 | 5 head_family candidates：softbox_rect (Volumetric Envelope, loft 锥形软箱) / round_reflector (Volumetric Envelope, parabolic loft dish) / led_panel (Planar Boundary Form, rounded-rect flat panel) / fresnel_can (Volumetric Envelope, 圆柱 revolution can) / spotlight_can (Macro Surface Construction, cast can with vent bands + carry handle)。登记进 `slot_choices` 作为 head_family key。全部 forked_anchor。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | fresnel_can 前面 concentric fresnel rings（host-conformal，由 lens face 派生），spotlight_can 侧面 vent bands（由 head_shell 半径派生），LED panel 前面 grid dots（由 diffuser rectangle 派生）。全部 `record_only`。装饰派生顺序 ③→⑤→④。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | column_length_scale [0.85, 1.15]、mast_travel_scale [0.80, 1.15]、head_scale [0.85, 1.20]、leg_spread_scale [0.90, 1.10]。运动包络：`head_tilt` REVOLUTE axis=(1,0,0) 或 (0,1,0) 依 head_family，range [-0.55, 0.65]；`stage_i_prismatic` PRISMATIC axis=(0,0,1) range [-0.20, 0.15]；`base_to_leg_i` REVOLUTE range [-0.72, 0.05]；`caster_wheel_i` CONTINUOUS 无限制；`head_to_focus_barrel` PRISMATIC axis=(0,1,0) range [0, 0.05]；`head_to_barn_door_i` REVOLUTE range [0, 1.4]。**motion_test_plan**：`run_studio_lamp_tests` 调 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` + 每关节 targeted `ctx.pose` 验证方向（tilt 抬 diffuser，leg 折 foot 上抬，stage 抬 head 高度）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette_style：`studio_black` (powder_black + dark_metal + fabric_black + diffuser_white)，`silver_industrial` (satin_aluminum + polished_metal + vent_dark)，`warm_brass` (brass + walnut + amber)，`cinema_grey` (grey_matt + graphite + soft_white)，`arctic_white` (arctic_white + light_grey + cool_white)。材质大类覆盖 metal / painted / fabric / plastic。 |

## 采样与覆盖审计

总组合数：3 (support) × 5 (head_family) × 3 (head_module) × 3 (mast_count) × 5 (palette) = **675**（在 gating 后合法组合约 3 × 5 × 2.4 × 3 × 5 ≈ 540）。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)` 独立采样每个 enum + weighted `mast_count` + independent scales；`resolve_config` 应用 conditional gates（barn_doors_4 仅在 planar head；总高 clamp）。sweep 0-35 覆盖 36 seed（应命中至少 30+ 独立 tuple），corner stage 由 pipeline 自动生成 per-field 极值组合。palette_style 每 seed 用 rng.choice → 材质大类覆盖 ≥ 3。

Topology target：1000-seed slot choice tuple 覆盖用于成熟度观察；不设 gate。真实合法子集 ≈ 540。

若使用 regression overrides：暂无；后续如 sweep 找出稳定坏 seed 再补。

Controlled local parameterization：`column_length_scale`、`mast_travel_scale`、`head_scale`、`leg_spread_scale` 独立采样后 clamp；`resolve_config` 内解 inequality（总高、travel/tube ratio）。所有 scale 在 `[0.85, 1.20]` 保守范围。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rng.choice per slot + weighted mast_count + independent scales | slot_choices_for_seed matches build choices |
| compatibility matrix | barn_doors_4 → 仅 planar head_family；rolling_base 与 counterweighted_boom_base 互斥（因都占用 base slot） | 无 sweep floating caster、无 counterweight 悬空 |
| controlled local variation | 4 scale param，clamp range 保守，总高 inequality clamp | proportions vary without breaking interfaces |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass + corner stage | axis_realization 每 slot value 出现 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support | 3 | yes | yes | tripod / rolling / counterweighted |
| head_family | 5 | yes | yes | ③ 主形态族 |
| head_module | 3 | yes | yes | none / focus_barrel / barn_doors_4 |
| mast_count | 3 | yes | yes | multiplicity |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed` returns implemented module names for `support`, `head_family`, `head_module`, `mast_count`, `palette_style`
- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` 不特殊
- barn_doors_4 只在 head_family in planar/loft family；否则 resolve_config 降级为 none
- rolling_base 与 counterweighted_boom_base 不同时被选（同一 support slot）
- 总高 = sum(stage tube lengths * column_length_scale) + yoke + head_height/2 ≤ 2.4m
- 每 stage `mast_travel` ≤ 0.90 * `inner_tube_length` (保插入)
- critical InterfaceSpec / MatingContract points：yoke→stage FIXED (mating declared)；leg hinge REVOLUTE grandfathered (captured pin) with allow_overlap element-scoped；head_tilt REVOLUTE grandfathered (trunnion in yoke) with allow_overlap；barn_door hinge REVOLUTE with MatingContract to rim
- head_tilt REVOLUTE range 满足 `[-0.55, 0.65]` × `head_scale`
- multiplicity `mast_count` 采样后一致：`slot_choices_for_seed` 报 `("mast_count", f"n{k}")`

## Reject cases

- 三角腿悬空（root_part unconnected / foot below floor）
- Telescoping stage 完全脱出（`mast_travel` > tube_length）
- Head 前面 diffuser 与后面 rear_housing 交换位置（+Y 出光方向错）
- barn_doors_4 打开时穿透 head 前面
- rolling_base 的轮子中心不在地面（axis 不通过轮轴）
- 总高超出 2.4m 或低于 0.5m
- palette_style 材质缺失（palette dict 少 key）
- fresnel_can 与 spotlight_can 上加 barn_doors（结构不合，会穿模）

## 与相邻类别的边界

- 不该混入：`articulated_task_lamp`（有 clamp/wall/desk mount + 2R arm，我们只有 tripod/rolling/counterweighted + 单 mast）
- 不该混入：`camera_tripod`（无 lamp_head，顶端是 camera_plate）
- 不该混入：`street_lamp`（地埋杆件，无三脚架，无 diffuser）
- 不该混入：`theater_spotlight`（低 pedestal base 非 telescoping）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Segment 2 auto-generated by claude-code. Spec continuous → template implementation. |

## 模板实现备注（可选）

- 共享 helper：`_hollow_tube(outer, inner, length)` cadquery 生成的 mesh 在 tripod/rolling/counterweighted 与 mast_stage 三处复用。
- `_lobed_knob(...)` REVOLUTE knob helper 复用 origin 001 pattern（用于 lower_clamp_knob CONTINUOUS 旋钮）。
- 每 stage `mast_stage_i` 的 `stage_i_prismatic` grandfathered（内外套管为 captured 关系），添加 element-scoped `allow_overlap(base/prev_stage, cur_stage, elem_a="outer_tube", elem_b="inner_tube")`。
- head_tilt REVOLUTE grandfathered（trunnion 穿过 yoke 双 bearing），添加 element-scoped `allow_overlap(yoke, head, elem_a="trunnion_shaft", elem_b="tilt_yoke")` 或 `bearing_pos`。
- barn_door 铰边接触 `MatingContract` 到 head 前面 diffuser rim（`positive_y` 面），`tangential_containment=False`（rim ring 面不好检测 tangential 容纳）。
- focus_barrel PRISMATIC 沿 +Y，`MatingContract` 到 head 前面 rim +Y 面（因为它平移）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A (tripod) + Slot D (softbox_rect) + trunk | rec_picturex_0611__studio_lamp__001 | L141-L245 (tripod + column) / L246-L295 (2-stage mast) / L297-L336 (yoke) / L338-L425 (softbox_rect head) | primary spine |
| S2 | Slot A (tripod hub for boom-family arms) | rec_picturex_0611__studio_lamp__002 | L87-L172 (tripod + hollow lower column) / L174-L242 (upper_pole + mast_extension) | tripod pattern for boom families |
| S3 | Slot A (tripod compact) + Slot D (spotlight_can) | rec_picturex_0611__studio_lamp__003 | L116-L255 (spider tripod) / L257-L327 (single-stage prismatic + yoke) / L330-L406 (spotlight_can head with LatheGeometry `_lamp_shell`) | spine + spotlight family |
| S_round | Slot D (round_reflector) | rec_0611_studio_lamp_var_head_family_round_reflector | L35-L83 (parabolic loft) / L338-L425 (round_reflector head + trunnion) | round reflector head |
| S_led | Slot D (led_panel) | rec_0611_studio_lamp_var_head_family_led_panel | L34-L45 (rect body helper) / L321-L400 (led panel head + trunnion + rear plate) | LED panel head |
| S_fresnel | Slot D (fresnel_can) | rec_0611_studio_lamp_var_head_family_fresnel | L91-L146 (fresnel lens LatheGeometry) / L362-L440 (fresnel can head + trunnion) | fresnel can head |
| S_focus_barrel | Slot E (focus_barrel) | rec_0611_studio_lamp_var_head_module_focus_barrel | L34-L60 (focus barrel ring helper) / L433-L490 (focus_barrel PRISMATIC child) | focus barrel |
| S_4_barn_doors | Slot E (barn_doors_4) | rec_0611_studio_lamp_var_head_module_4_barn_doors | L28-L31 (_barn_door_panel) / L488-L560 (4× REVOLUTE barn door children) | barn doors |
| S_rolling | Slot A (rolling_base) | rec_0611_studio_lamp_var_support_rolling_base | L64-L92 (rolling platform helper) / L178-L275 (base + 3× caster wheels CONTINUOUS) | rolling base |
| S_boom_base | Slot A (counterweighted_boom_base) | rec_0611_studio_lamp_var_support_counterweighted_boom | L34-L48 (counterweight disk) / L162-L228 (base + counterweight visual + short legs) | counterweighted base |
| S_mast_1 | Slot B mast_count=1 | rec_0611_studio_lamp_var_mast_count_1 | L90-L172 (mast helper) / L320-L327 (single-stage PRISMATIC) | mast_count=1 |
| S_mast_3 | Slot B mast_count=3 | rec_0611_studio_lamp_var_mast_count_3 | L75-L124 (`_mast_section_specs`) / L244-L295 (3 nested stages) | mast_count=3 |
