# telescoping_pointer — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `telescoping_pointer` |
| template path | `agent/templates/telescoping_pointer.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (multiplicity of prismatic stages + parallel-child optional clip) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star `rec_0611_telescoping_pointer_*` samples + the picturex origin |
| source_index_policy | only adopted module sources are indexed below |

Sources (all `revisions/rev_000001/model.py`, star=5):

- S1 `rec_picturex_0611__telescoping_pointer__001__png_19b2b645f11a4975a5020b55d4b232f9` — 3-stage baseline (L61-L272)
- S2 `rec_0611_telescoping_pointer_var_stage_count_2` — 2-stage (L61-L233)
- S3 `rec_0611_telescoping_pointer_var_stage_count_4` — 4-stage (L15-L335)
- S4 `rec_0611_telescoping_pointer_var_stage_count_5` — 5-stage looped assembly (L60-L343)
- S5 `rec_0611_telescoping_pointer_var_tip_form_ball` — sphere-tip (L122-L131)
- S6 `rec_0611_telescoping_pointer_var_tip_form_hand_silhouette` — flat hand silhouette tip (L122-L222)
- S7 `rec_0611_telescoping_pointer_var_body_form_pen_style` — slim pen barrel + pocket clip (L61-L153)
- S8 `rec_0611_telescoping_pointer_var_lock_twist_collars` — twist collars at each junction (L61-L78, L188-L224)
- S9 `rec_0611_telescoping_pointer_var_secondary_hinged_pocket_clip` — REVOLUTE pocket-clip child of grip (L133-L332)

## 核心身份

一根真实世界的伸缩式教学/激光指示棒：一根 foam / 塑料 grip 手柄，向 +Z 方向逐段套接 2–5 段可 collapse 的金属 tube stage，
最内 stage 顶端固定一个 tip（sphere / rounded stem / flat hand silhouette）。每段之间都有 PRISMATIC 关节，
从 grip 起，共同 +Z 轴、`upper=0.0, lower=-travel_i`（负向 collapse）。可选装饰性 hinged pocket clip（REVOLUTE, `+Z` 侧
挂在 grip 上）。不应混入 laser_pointer（无 telescoping）/ pointer_stick（单杆无 telescoping）/ walking_cane / retractable
antenna（跨类别）。

## 槽位 + 候选模块表

### Slot A：body_form
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| foam_grip_body | forked_anchor | S1 rec_picturex_0611_...001 | S1 L61-L79 (grip), L149-L181 (grip visuals) | eligible if compatible | 粗 0.0108m foam handle + 球端 + entry_ring + rubber stage_0_guide bushing；GRIP_TOP=0.190 |
| pen_style_body | forked_anchor | S7 rec_0611_..._var_body_form_pen_style | S7 L63-L79 (barrel + socket), L178-L215 (grip visuals incl. pocket clip) | eligible if compatible | 细 0.0048m glossy plastic barrel + 深 socket + 静态 spring-steel pocket_clip visual；GRIP_TOP=0.135 |

② `pen_style_body` 内嵌一个静态 clip visual（不动），不加 joint —— 若要动态 clip 请走 Slot D `hinged_pocket_clip`。

### Slot B：stage_count（multiplicity）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| stages_n_2 | forked_anchor | S2 var_stage_count_2 | S2 L82-L106, L119-L233 | eligible | grip → stage_0 → stage_1(inner+tip)；1+2 parts，2 prismatic |
| stages_n_3 | forked_anchor | S1 origin baseline | S1 L82-L131, L149-L272 | eligible | grip → stage_0 → stage_1 → stage_2(inner+tip)；1+3 parts，3 prismatic |
| stages_n_4 | forked_anchor | S3 var_stage_count_4 | S3 L122-L169, L186-L335 | eligible | 1+4 parts，4 prismatic；共享 `_intermediate_stage_shape` helper |
| stages_n_5 | forked_anchor | S4 var_stage_count_5 | S4 L79-L146, L202-L343 | eligible | 1+5 parts，5 prismatic；`_STAGE_TABLE` + `_GUIDE_TABLE` 循环生成 |

Multiplicity axis：`stage_count ∈ {2,3,4,5}`。每个 candidate 对应一个具体 N；共享 helper 且每段
tube outer/inner_r 与 travel 按 stage index 单调收窄（详见 §7）。

### Slot C：tip_form
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rounded_stem_tip | forked_anchor | S1 `_tip_shape` | S1 L122-L131 | eligible | 短 stem + 顶端 sphere；warm_tip 材质 |
| ball_tip | forked_anchor | S5 `_ball_tip_shape` | S5 L122-L131 | eligible | 更粗的球（r=0.004）+ 短颈；warm_tip |
| hand_silhouette_tip | forked_anchor | S6 `_hand_silhouette_shape` | S6 L122-L222 | eligible | 薄板 palm + 4 finger + thumb + mounting collar；warm_tip |
| flat_disc_tip | world_knowledge_extrapolation (③) | anchors: S1 tip + reviewer；form_subtype=Planar Boundary Form | template helper `_disc_tip_shape` | eligible if compatible | 与 S1 同 part tree（顶端 visual），换成扁平圆盘形态 |

③ Primary Form Family：`rounded_stem_tip` = Volumetric Envelope Form (rounded probe)，`ball_tip` = Volumetric
Envelope Form (isolated sphere)，`hand_silhouette_tip` = Planar Boundary Form (thin plate silhouette)，
`flat_disc_tip` = Planar Boundary Form (disc)。共 4 个可识别形态原型，登记进 `slot_choices`。

### Slot D：secondary（optional child of grip）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | forked_anchor | S1 origin baseline (no clip) | S1 L149-L181 | eligible | grip 无 clip child part；只保留 4 个 grip visuals |
| hinged_pocket_clip | forked_anchor | S9 pocket_clip revolute | S9 L133-L332 | eligible | grip 上新增 clip_mount visual + `pocket_clip` part + REVOLUTE `grip_to_clip` (axis=-Y, 0..0.55 rad) |

### Slot E：lock（visual/decoration）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rubber_bushings | forked_anchor | S1 origin | S1 L173-L212 | eligible | dark_rubber 圆环 stage_i_guide 藏在 parent inside；无外露 collar |
| twist_collars | forked_anchor | S8 var_lock_twist_collars | S8 L61-L78, L188-L224 | eligible | 每个 junction 加一个 matte-black 外露 twist_collar visual（带中间宽 band + 上下 lip） |

## 槽位图（slot graph）

pattern: mixed

```
[Slot A body_form] (root=grip)
  --PRISMATIC(+Z, socket contact) → [Slot B stages_n_k]  stage_0
    --PRISMATIC(+Z, guide bushing) → stage_1
      ... k-1 times ...
        → stage_{k-1}  --host visual→ [Slot C tip_form]
  --REVOLUTE(-Y, side hinge) → [Slot D secondary hinged_pocket_clip]  (optional)
  --visual overlay→ [Slot E lock twist_collars or rubber_bushings]  (装饰共形嵌入)
```

- Slot A→B 接口：grip 顶部 socket (`entry_ring` 内壁 z=0.188)，mating face 是 grip 的 `stage_0_guide`
  visual（内径 0.00435m）与 stage_0 的 `outer_tube` 视觉（外径 0.00445m）。共 axis (+Z)。
- Slot B 内部 stage_i→stage_{i+1}：parent 的 `stage_{i+1}_guide` 内壁 vs child 的 shaft outer_tube。共 axis (+Z)。
- Slot B→Slot C：`tip_shape` 挂在最内 stage 的 host part 上作为 visual（不新建 part）。
- Slot A→Slot D：clip_mount visual 装在 grip 侧面 (x=+0.0113, z≈0.160)，pocket_clip part 通过 REVOLUTE 绕 -Y 轴摆动。
- Slot E：lock 装饰纯 visual 层，不新增 part / joint；`twist_collars` 是新增到 grip 与每段 parent stage 的 matte_lock
  visual，`rubber_bushings` 是保留源码的 dark_rubber `stage_i_guide` 环。

## 每槽位 Module Emits / Interfaces

### Slot A / module foam_grip_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grip` (root) | S1 model.py:L149 |
| internal joints | none | — |
| upstream interface | root, no parent | — |
| downstream interface | grip 顶部 socket，anchor_local≈(0,0,0.190)，face_side=+Z，`stage_0_guide` visual 内径 0.00435m | S1 L173-L181 |

### Slot A / module pen_style_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grip` (root, 细 barrel + pocket_clip static visual) | S7 L178-L215 |
| internal joints | none | — |
| upstream interface | root | — |
| downstream interface | anchor_local≈(0,0,0.135)，face_side=+Z，`stage_0_guide` 内径 0.00350m | S7 L202-L210 |

### Slot B / module stages_n_k (k∈{2,3,4,5})
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stage_0` … `stage_{k-1}`，共 k parts | S4 L262-L299 (looped) |
| internal joints | `grip_to_stage_0` + `stage_i_to_stage_{i+1}` (i=0..k-2)，全部 PRISMATIC(+Z)，`upper=0, lower=-travel_i`；每段 guide bushing on parent | S4 L322-L343 |
| upstream interface | `stage_0` outer_tube 视觉外径 ≈ 0.00445m，anchor_local=(0,0,0)，face_side=-Z | S1 L149 |
| downstream interface | `stage_{k-1}` 顶部 holder_nose / neck，face_side=+Z，供 tip 挂载；world 位置 grip_top + Σ joint_z_offsets | S1/S3 innermost |

### Slot C / module rounded_stem_tip / ball_tip / hand_silhouette_tip / flat_disc_tip
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part；tip 作为最内 stage 的 visual `tip` 挂上 | S1/S5/S6 |
| internal joints | none | — |
| upstream interface | anchor 在 innermost stage 顶部 holder，face_side=+Z | S1 L226 |
| downstream interface | none (tip 自由端) | — |

### Slot D / module hinged_pocket_clip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pocket_clip` part（clip_arm 视觉：hinge barrel + arm + bend + retaining ball） | S9 L307-L316 |
| internal joints | none 内部 | — |
| upstream interface | 挂在 grip 侧面：anchor_local=(clip_hinge_offset,0,clip_hinge_z) | S9 L318-L332 |
| chain joint | `grip_to_clip` REVOLUTE axis=(0,-1,0)，`lower=0.0, upper=0.55` rad | S9 L318-L332 |

### Slot E / module rubber_bushings / twist_collars
| emits | visual overlays 到 grip + 各 parent stage；无 part / joint | S1 / S8 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | `foam_grip_body` / `pen_style_body` | `foam_grip_body` | choice | seeded RNG | Slot A |
| stage_count | int | 2 / 3 / 4 / 5 | 3 | choice | weighted (3 最常见, 2/4 次之, 5 稀有) | Slot B / §8 |
| tip_form | enum | `rounded_stem_tip` / `ball_tip` / `hand_silhouette_tip` / `flat_disc_tip` | `rounded_stem_tip` | choice | seeded RNG | Slot C |
| secondary | enum | `none` / `hinged_pocket_clip` | `none` | choice | seeded RNG，pen_style 更偏 clip | Slot D |
| lock | enum | `rubber_bushings` / `twist_collars` | `rubber_bushings` | choice | seeded RNG | Slot E |
| palette_style | enum | 5 realistic 皇色 (见下) | `office_black` | choice | seeded RNG | ⑥ |
| grip_length_scale | float | [0.90, 1.10] | 1.0 | independent | clamp | 来自 S1 GRIP_TOP=0.190 |
| stage_ratio | float | [0.72, 0.82] | 0.78 | independent | 每段 shaft/collar 半径缩比 | S1/S3/S4 |
| travel_scale | float | [0.85, 1.15] | 1.0 | independent | 每段 travel = base * travel_scale | S1 STAGE_TRAVELS |
| clip_open_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 secondary=`hinged_pocket_clip` 时生效 | S9 |
| (—) | constraint | — | — | inequality | 相邻 stage: `stage_{i+1}.outer_r < stage_i.inner_r - clearance`，违反回缩 `stage_ratio` | S4 nested engineering |
| (—) | constraint | — | — | inequality | `travel_i ≤ shaft_len_i - min_retention` (保证 collapsed 仍互相 engage) | S1 collapse test |

**Palette (⑥, ≥3 candidates)**：

| palette_style | 描述 |
|---|---|
| `office_black` | S1 baseline: black_foam grip + polished_steel/bright_steel tubes + warm_tip |
| `chrome_business` | S7 pen-style: glossy_barrel + polished_chrome/bright_chrome + brass_tip |
| `matte_industrial` | matte-black foam + gunmetal steel + dark_tip |
| `retail_bronze` | tan foam + bronze/copper tubes + brass tip |
| `student_bright` | red plastic grip + polished_steel + warm_tip |

### 7.5 编译预算 / compile budget

自报 15-25 s / seed（cadquery mesh：grip + 2-5 nested tubes + tip；lock/twist_collar 若命中再加 3-6 boolean）。
分档 tessellation：所有 tube.circle ≤ 32 seg（默认 cq mesh tolerance 0.00015-0.00035，实测 15-25 s）；hand_silhouette
tip 走 Box primitives 不走 boolean。相同结构 stage 共享 `Mesh` cache 通过 `mesh_from_cadquery(name=...)`。超支先降 tolerance。

## Multiplicity / Copy Logic

- `count_param`：`stage_count`
- `N_range`：`{2, 3, 4, 5}` (由 5 星样本枚举确认；产品域上限 6 可达但无 5 星支持)。
- sampling domain：weighted RNG (3 频率最高 40%，2 与 4 各 25%，5 频率 10%)。
- copied object：`stage_i` part（`_intermediate_stage_shape` 共享 helper）
- naming：`f"stage_{i}"`（i=0..N-1），joint `f"stage_{i}_to_stage_{i+1}"`，i=0 时 parent 为 `grip`（joint 名 `grip_to_stage_0`）。
- placement：串行沿 +Z，每段起 z 依 parent 局部 joint_z_offset（≈parent_top - 0.005）。
- joint policy：全部 PRISMATIC，axis=(0,0,1)，`upper=0.0, lower=-travel_i`；travel 随 stage index 递减；
  每对 (parent, child) 均声明 `MatingContract`（`stage_i_guide` face → child `tube` face，`positive_z / negative_z`）。
- sweep 覆盖：N=2/3/4/5 每种 ≥1 次；`slot_choices` 记录 `stage_count` value。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 3 种骨架：（a）无 clip 的 N-stage 链（Slot A + B），（b）加 hinged_pocket_clip → grip 多一 REVOLUTE 子（Slot D=hinged）；均 forked_anchor（S1/S9）|
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`stage_count ∈ {2,3,4,5}`，weighted (3≥2/4>5) |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 主链全 PRISMATIC(+Z)；secondary=hinged_pocket_clip 加 REVOLUTE(-Y)；forked_anchor S9 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot C 4 candidate：Volumetric Envelope Form (`rounded_stem_tip`, `ball_tip`) + Planar Boundary Form (`hand_silhouette_tip`, `flat_disc_tip`)；登记进 `slot_choices`，`form_subtype` 已标注 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | Slot E：`rubber_bushings`（S1）/ `twist_collars`（S8，matte-black collar + wider band + lip rings）；`twist_collar` 视觉半径按 parent stage outer_r 派生（host-conformal, 派生顺序 ③→⑤→④）|
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | grip_length_scale [0.90,1.10], stage_ratio [0.72,0.82], travel_scale [0.85,1.15]；每段 PRISMATIC 关节：axis=(0,0,1)，方向 `[-travel_i, 0]`，全程互相 engage；`motion_test_plan`：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` + targeted `ctx.pose({all joints: -travel})` 验证 collapsed pose 仍有 z-overlap；secondary clip 若存在：`ctx.pose({grip_to_clip: upper})` 验证 clip 向 +X 外摆 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 5 palette_style（`office_black` / `chrome_business` / `matte_industrial` / `retail_bronze` / `student_bright`）；材质大类 painted plastic + metal + rubber ≥3 |

## 采样与覆盖审计

总组合数：body_form(2) × stage_count(4) × tip_form(4) × secondary(2) × lock(2) × palette_style(5) = 640
（无兼容 gate 屏蔽；实际 seed 域内会通过 weighted 采样偏中间 stage_count 与 rounded_stem_tip）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 独立均匀（或加权）采样每个 slot；`resolve_config` clamp
连续 scale，按 `inequality` 检查 stage 半径 nesting 并按比例回缩 `stage_ratio`，若仍非法则回退到 stage_ratio=0.78；`slot_choices_for_seed`
以 tuple 返回 `("body_form", ...), ("stage_count", ...), ("tip_form", ...), ("secondary", ...), ("lock", ...), ("palette_style", ...)`。
无 regression overrides；seed=0 走标准 RNG。sweep 覆盖 0-35，corner stage 附加。

Topology target：≥300 unique slot-tuple 是可达（640 组合），但由 weighted 分布 1000 seed 预期 ~ 400-500 unique。

Controlled local parameterization：`grip_length_scale`, `stage_ratio`, `travel_scale`, `clip_open_scale` 全走独立 independent + clamp；
`stage_ratio` 通过 inequality 保 nesting；派生的 `travel_i = base_travel_i * travel_scale` 走 equation。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 6 slots 独立采样；stage_count 加权 (3>2,4>5) | slot_choices_for_seed matches build choices |
| compatibility matrix | 无强互斥；pen_style_body 与 hinged_pocket_clip 双重 clip 时 pen barrel 的静态 clip 让给 dynamic clip（生成时静态 clip 不出）| no double clip, no overlap |
| controlled local variation | grip_length_scale, stage_ratio, travel_scale, clip_open_scale 全 clamp | proportions vary without breaking nesting / collapse |
| regression overrides | none | — |
| random sweep | seeds 0-35 fast/final; corner stage appended | axis_realization 每 slot value_count ≥1 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 2 | yes | no | 5 星池仅 2 结构不同 body |
| stage_count | 4 | yes | yes | multiplicity |
| tip_form | 4 | yes | yes | 3 forked + 1 wke |
| secondary | 2 | yes | no | 结构上是 optional child part |
| lock | 2 | yes | no | ④ 装饰层 |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名。
- `config_from_seed` 对所有 seed 用 deterministic RNG 采样。
- compatibility matrix：pen_style_body 若同时命中 hinged_pocket_clip → 只保留 dynamic clip visual，不双重挂。
- controlled local scale：`stage_ratio` clamp [0.72,0.82]，若 nesting 违反 inequality 回缩到 0.78；`travel_scale` clamp [0.85,1.15]。
- InterfaceSpec：grip.stage_0_guide 内径 → stage_0.outer_tube 外径；每段 parent.stage_{i+1}_guide → child.tube_{i+1}。
- Key joints：`grip_to_stage_0` + `stage_i_to_stage_{i+1}` PRISMATIC(+Z) `upper=0, lower<0`；若 secondary=hinged_pocket_clip
  额外 `grip_to_clip` REVOLUTE(-Y) `lower=0, upper>0.3`。
- copied objects follow `stage_i` naming + regular +Z placement.

## Reject cases

- stage_{i+1} outer_r >= stage_i inner_r（无 nesting，直接穿模）
- travel_i > shaft_len_i - min_retention（collapsed 时 stage 脱离 parent socket）
- tip 挂到非最内 stage（run away tip）
- 双重 clip（pen_style_body 静态 clip + hinged_pocket_clip 同时出现）
- PRISMATIC axis 非 (+Z) 或 upper > 0（违反 collapse 语义）
- twist_collar 半径小于 parent stage outer_r（外露 collar 沉进 body 消失）
- palette 只作用于部分 material，导致 mixed palette 出现
- clip 挂在最内 stage（应挂 grip）

## 与相邻类别的边界

- 不该混入：`laser_pointer`（无 telescoping，是一段固定 pen）
- 不该混入：`walking_cane`（同样 telescoping 但底部 tip 是防滑橡胶大脚，且长度差一个 order）
- 不该混入：`retractable_antenna`（虽同为 telescoping tube，但顶端无 tip，且用于收音机而非指示）
- 不该混入：`ball_pen`（点端 tip 是笔尖，非指示 sphere/hand，且无 telescoping）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | segment-2 first authoring |

## 模板实现备注（可选）

- 所有 stage 共享 `_intermediate_stage_shape` helper（S3 / S4 已抽），i=0 用 `_stage_0_shape`（更粗，带 collar_base + collar_taper），最内 stage 用 `_innermost_stage_shape`（带 holder_nose 供 tip 挂）。
- `twist_collar` 视觉尺寸由 parent stage outer_r 派生：`collar_outer_r = 1.15 * parent_outer_r`, `collar_inner_r = child_outer_r - clearance`。
- captured-pin overlap：`grip.stage_0_guide` 与 `stage_0.outer_tube` 之间 element-scoped `allow_overlap`；同样每段 `stage_i.stage_{i+1}_guide` ↔ `stage_{i+1}.tube_{i+1}`；secondary `pocket_clip` 与 grip 侧 clip_mount 元素之间同样 element-scoped allow_overlap。
- `MatingContract`：每个非-FIXED joint declare parent_face_geometry=parent的 `stage_i_guide` visual (positive_z) + child_face_geometry= child 的 `tube_i` visual (negative_z)，contact_tol=0.002；REVOLUTE `grip_to_clip` 走 grip 的 `clip_mount` visual +X face + `pocket_clip` 的 barrel visual -X face。
- Rule 5 motion tests：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` + targeted `ctx.pose({all prismatic joints: -travel_i})` 验证 collapsed 且 stage_{i+1} 顶端仍在 stage_i 内；若 hinged_pocket_clip 存在再加 `ctx.pose({grip_to_clip: upper})` 验证 clip x-swing。
