# Modular Spec — Retail_Shop Fixtures / Clothing rack

## 元信息
| 项 | 值 |
|---|---|
| slug | `clothing_rack` |
| template path | `agent/templates/clothing_rack.py` |
| test path (optional) | `tests/agent/test_clothing_rack_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (base_frame root → PRISMATIC telescoping upper_frame carrying the hanging rail(s) with a loop of REVOLUTE-swinging hangers; 4 CONTINUOUS caster wheels as parallel children of base_frame; optional horizontal-extension rail as a PRISMATIC child of upper_frame) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 origins + 8 forks) |
| source_index_policy | only adopted module sources are indexed below |

Read in full: `rec_retail_shop_fixtures__clothing_rack__001…` (A, double-rail gold rolling rack),
`rec_retail_shop_fixtures__clothing_rack__002…` (B, single-rail black rolling rack),
and forks `…var_feetbase`, `…var_fold`, `…var_n_hangers`, `…var_railextend`, `…var_round`,
`…var_skeleton_arch`, `…var_topshelf`, `…var_twotier`.

## 核心身份

A free-standing garment rack: one or more elevated horizontal hanging rails held up by two
uprights that telescope (PRISMATIC height adjust) out of a floor-standing base, garments
hung on wire hangers that hook over the rail(s) and swing (REVOLUTE). The base is either a
wheeled rolling caster base (4 CONTINUOUS wheels) or a stationary leveling-feet base. Optional
storage lives as a lower shoe/storage shelf of round rods on the base or an overhead slatted
wire shelf above the rail. Must keep: ≥1 elevated horizontal hanging span carried by uprights
on a floor base, garment/hanger capacity, ≥1 real non-fixed joint (telescoping prismatic +
hanger swing revolute + caster spin continuous). Must NOT become: coat/hat tree or valet stand
(vertical pegs, no horizontal span), shelving unit / wardrobe cabinet (solid panels dominate),
clothes-horse / accordion airer, curtain rod / wall track, mannequin bust, umbrella stand, or a
carousel turntable.

## 槽位 + 候选模块表

### Slot A：rail_topology （① 骨架 + ③ 主体形态家族 hero slot）

主承力主多样性的槽位。所有候选装配在同一 two-upright telescoping spine 上（共享 lower_sleeve
mating face @ x=±x_post），只改变上部 rail 结构 / 形态 / 附加水平机构。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_straight_rail` | forked_anchor | rec_…clothing_rack__002 (B) | model.py:L269-L333 | eligible if compatible | 1 条直 top_hanging_rail on 2 upright posts + rail_tee spheres；单 REVOLUTE hanger loop；part tree = upper_frame + N×hanger |
| `double_parallel_rail` | forked_anchor | rec_…clothing_rack__001 (A) | model.py:L164-L232, L333-L376 | eligible if compatible | 2 条平行直 rail (front + rear, Δy) on same upper_frame，各自 REVOLUTE hanger loop；part tree gains a second rail-set (① skeleton delta) |
| `arched_inverted_u_rail` | forked_anchor | rec_…clothing_rack_var_skeleton_arch | model.py:L269-L338 | eligible if compatible | 单条连续拱形 mesh 管 (tube_from_spline_points，Volumetric Envelope Form) 从两 sleeve 升起并在顶部拉平成 crown；no straight posts；③ 形态原型切换 |
| `two_tier_stacked_rail` | forked_anchor | rec_…clothing_rack_var_twotier | model.py:L290-L348 | eligible if compatible | top rail + 第二条 lower_hanging_rail (Δz) on same posts，各自 REVOLUTE hanger loop；① skeleton delta (双悬挂层) |
| `extendable_straight_rail` | forked_anchor | rec_…clothing_rack_var_railextend | model.py:L301-L405 | eligible if compatible | top rail 拆成 rail_outer 空心套管 + captured rail_inner 滑管 + `rail_extend` 水平 PRISMATIC；part+joint delta（② 机构：水平伸缩）；outer 段 + inner 段各挂 hanger |

form_subtype 标注：`single_straight_rail`/`double_parallel_rail`/`two_tier_stacked_rail`/
`extendable_straight_rail` = **Planar Boundary Form / Volumetric Envelope Form (直管骨架)**；
`arched_inverted_u_rail` = **Volumetric Envelope Form (连续弯管扫掠包络)** — 可识别的 ③ 原型切换。

### Slot B：support_base （① 骨架）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rolling_caster_base` | forked_anchor | rec_…clothing_rack__002 (B) + __001 (A) | model.py:L186-L267 | eligible if compatible | 矩形管 base + welded corner spheres + low_rear_brace + 4× caster fork/stem hardware，4 个 `wheel_{i}` CONTINUOUS 转轮（captured cross-pin 过 hub）；提供 lower_sleeve_{i} 接口 |
| `static_feet_base` | forked_anchor | rec_…clothing_rack_var_feetbase | model.py:L153-L226 | eligible if compatible | H 形 foot_rail + foot_crossbar + 4 rubber foot glides + foot_stem，无 caster / 无 CONTINUOUS 关节；同样提供 lower_sleeve_{i} 接口 |

（2 candidates — 源池仅两种 base family；两 origin 都用 caster，唯一 non-caster 结构是 feetbase fork。
round/fold 的 spider / scissor base 属另一 motion spine，见 §9 blocked。符合"降到 2 需说明"。）

### Slot C：storage_shelf （① 骨架）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `no_shelf` | forked_anchor | rec_…clothing_rack__002 (B) | model.py:L269-L333 | eligible if compatible | 无附加储物层；rail + hangers 主导 |
| `lower_storage_shelf` | forked_anchor | rec_…clothing_rack__001 (A) | model.py:L191-L205 | eligible if compatible | base_frame 上 2 层 shelf_rod loops (2 tiers × N_rods) + side rails，FIXED slats（不动 → base visuals） |
| `overhead_top_shelf` | forked_anchor | rec_…clothing_rack_var_topshelf | model.py:L303-L351 | eligible if compatible | upper_post 延长，其上一整块 CadQuery wire-mesh 顶架 (side rails + N cross rods)，FIXED（不动 → upper_frame visual） |

### Multiplicity：hanger_count （① 的子项，见 §8）

主 rail hanger 数量 N（加权采样，小 N 偏多）。secondary rail（double 的第二 rail、two_tier 的
lower rail）派生同/近 N；extendable 的 outer/inner 段各派生子计数。

## 槽位图（slot graph）

pattern: mixed

```
base_frame (root, Slot B)
  ├─[PRISMATIC axis=(0,0,1)  height_slide  origin z=1.04  limits 0..0.14]─▶ upper_frame (Slot A)
  │     ├─[REVOLUTE axis=(1,0,0)  *_swing  origin on rail centerline  ±0.35]─▶ hanger_{i} (×N)
  │     └─[PRISMATIC axis=(1,0,0) rail_extend origin on rail  0..0.25]─▶ rail_inner  (extendable only)
  │             └─[REVOLUTE  inner_hanger_{i}_swing  ±0.35]─▶ inner_hanger_{i}
  └─[CONTINUOUS axis=(0,1,0)  wheel_spin_{i}  origin at caster axle]─▶ wheel_{i} (×4, caster base only)

storage_shelf (Slot C): lower_storage_shelf → FIXED visuals on base_frame;
                        overhead_top_shelf → FIXED visual on upper_frame; no_shelf → none.
```

接口点位：
- base_frame ↔ upper_frame：telescoping mating = upper `sliding_bushing_{i}` / `upper_post_{i}`
  captured inside base `lower_sleeve_{i}` (open annular tube @ x=±x_post, z 0.10..1.04); joint frame
  is prismatic gauge (exempt from origin-on-geometry). Both bases expose identical sleeves.
- upper_frame ↔ hanger：hook_loop wraps the rail tube (intentional overlap); revolute origin on the
  rail centerline (axis colinear with rail = symmetry line → origin-honesty passes).
- upper_frame ↔ rail_inner (extendable)：rail_inner captured inside rail_outer sleeve along X
  (allow_overlap outer/inner); prismatic axis = rail X.
- base_frame ↔ wheel：caster_cross_pin captured through wheel hub_disc (allow_overlap + expect_contact).

互斥/gating：见 §9 compatibility matrix。round_hoop / folding_scissor = disjoint motion spines,
deferred (§9 blocked).

## 每槽位 Module Emits / Interfaces

### Slot A / module single_straight_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_frame (posts + rail_tees + top_hanging_rail + hanger_stops + side hooks + N hangers) | B / model.py:L269-L333 |
| internal joints | N × `top_hanger_{i}_swing` REVOLUTE axis (1,0,0) ±0.35 | B / model.py:L159-L167 |
| upstream interface | sliding_bushing_{i}/upper_post_{i} into base lower_sleeve_{i} (prismatic) | B / model.py:L273-L282 |
| downstream interface | rail centerline @ rail_z for hanger swings | B / model.py:L290-L302 |

### Slot A / module double_parallel_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_frame with front_rail + rear_rail (Δy) + rail_tees; two hanger loops | A / model.py:L164-L232 |
| internal joints | 2×N `front_hanger_{i}_swing` / `rear_hanger_{i}_swing` REVOLUTE ±0.35 | A / model.py:L221-L232, L357-L368 |
| upstream / downstream | as single, two rail centerlines | A / model.py:L164-L187 |

### Slot A / module arched_inverted_u_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_frame with continuous arch mesh tube (spline) + sliding_bushing_{i} + crown hangers | arch / model.py:L269-L338 |
| internal joints | N `top_hanger_{i}_swing` REVOLUTE ±0.35 on crown | arch / model.py:L327-L338 |
| upstream / downstream | arch legs telescope into sleeves; hangers on level crown segment | arch / model.py:L277-L309 |

### Slot A / module two_tier_stacked_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_frame top rail + lower_hanging_rail (Δz) + rail_tees; two hanger loops | twotier / model.py:L290-L348 |
| internal joints | N `top_hanger_{i}_swing` + N `lower_hanger_{i}_swing` REVOLUTE ±0.35 | twotier / model.py:L321-L332 |
| upstream / downstream | posts into sleeves; two rail centerlines Δz apart | twotier / model.py:L310-L320 |

### Slot A / module extendable_straight_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_frame rail_outer sleeve + bushing + posts; rail_inner sliding tube + caps; outer & inner hangers | railextend / model.py:L301-L395 |
| internal joints | `rail_extend` PRISMATIC axis (1,0,0) 0..0.25 + outer/inner `*_swing` REVOLUTE ±0.35 | railextend / model.py:L340-L405 |
| upstream / downstream | posts into sleeves; rail_inner captured in rail_outer along X | railextend / model.py:L304-L360 |

### Slot B / module rolling_caster_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_frame (rect tubes + corners + brace + caster hardware + sleeves) + 4× wheel_{i} | B / model.py:L186-L267 |
| internal joints | 4 × `wheel_spin_{i}` CONTINUOUS axis (0,1,0) | B / model.py:L345-L356 |
| downstream interface | lower_sleeve_{i} @ x=±x_post receive upper posts (prismatic) | B / model.py:L225-L231 |

### Slot B / module static_feet_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_frame (H foot rails + crossbar + foot glides + stems + sleeves), no wheels | feetbase / model.py:L153-L226 |
| internal joints | none (base is static; non-fixed joints come from height_slide + hangers) | feetbase |
| downstream interface | lower_sleeve_{i} @ x=±x_post receive upper posts (prismatic) | feetbase / model.py:L208-L214 |

### Slot C / module lower_storage_shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2-tier `shelf_rod_{tier}_{j}` FIXED cylinders + side rails on base_frame (visuals, non-articulating) | A / model.py:L191-L205 |
| internal joints | none (Rule 1: non-articulating → parent visuals) | A |

### Slot C / module overhead_top_shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | extended upper_post + one welded wire-mesh shelf (side rails + N cross rods) FIXED visual on upper_frame | topshelf / model.py:L303-L351 |
| internal joints | none (Rule 1) | topshelf |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| rail_topology | enum | single_straight / double_parallel / arched_inverted_u / two_tier_stacked / extendable_straight | — | choice | deterministic procedural sampler + gating | Slot A |
| support_base | enum | rolling_caster / static_feet | — | choice | sampler | Slot B |
| storage_shelf | enum | no_shelf / lower_storage_shelf / overhead_top_shelf | — | choice | sampler + gating | Slot C |
| hanger_count | int | [4, 10] | 7 | independent | 加权采样（小 N 偏多）后 clamp | B(7)/A(6,5)/n_hangers(11) |
| material_style | enum | black_steel / brushed_gold / chrome / matte_white | black_steel | independent | palette 选择 | A(gold)/B(black) + ④⑥ 外推 |
| width_scale | float | [0.88, 1.12] | 1.0 | independent | clamp；缩放 rail 长度 / post 间距 / base 宽 | A/B (~1.5–1.65 m) |
| rail_r_scale | float | [0.9, 1.15] | 1.0 | independent | clamp；缩放主 rail/tube 半径 | A/B tube radii |
| (—) | constraint | — | — | conditional | `arched_inverted_u` ⇒ storage_shelf ∈ {no_shelf, lower_storage_shelf}（arch 无 straight post 承 overhead）；`extendable_straight`/`two_tier`/`double_parallel` 允许 overhead；见 §9 | 接口 / clearance |
| (—) | constraint | — | — | inequality | hanger even x-spacing `step = span/(N-1) > body_thin(≈0.03)`，N≤10 恒满足；越界则 clamp N | 接口 |

## 7.5 编译预算 / compile budget
自报 **≤ 18 s/seed**（sweep hang-guard `--compile-timeout 60`）。依据：几何以 cylinders/boxes/spheres
为主，重 mesh 只有 hanger hook+body spline、lower_sleeve/clamp_collar (CadQuery)、caster tire、arch
spline、extendable rail sleeves、overhead wire-mesh；**同构 hanger 复用同一个 hook Mesh + body Mesh**
（N 只加 part/joint，不加 tessellation）。分档 tessellation：spline radial ≤18、CadQuery angular_tol 0.08–0.10。

## Multiplicity / Copy Logic

**hanger_count（1 根 multiplicity 轴）**
- `count_param` = `hanger_count`；`N_range` = 产品域 [3,14]，测试/sweep 域 [4,10]（偏小高频）。
- sampling domain：加权采样，小 N（5–7）高频、大 N（9–10）稀有；各自 clamp；sweep 上限 10（编译预算）。
- copied object = 一个 hanger assembly（hook_loop + vertical_neck + hanger_body），沿 rail 均匀 x 间距，
  每个一条 `*_swing` REVOLUTE (±0.35)，indexed `{prefix}_hanger_{i}`；hook/body 复用共享 Mesh。
- placement/joint policy：even x-spacing in [-span, span]；secondary rail（double rear / two_tier lower）
  派生 `max(3, N-1)`；extendable：outer 段 `max(2, N-3)` + inner 段固定 3。
- source/gating：B `top_hanger_{0..6}` (7)、A (6/5)、n_hangers fork (11)；无非法组合（rail 越长 N 越大安全）。

其余复制件（非 N 轴）：casters 固定 4（base-family change 是 ① slot 非 N 轴）；storage shelf rods 为 shelf
细节（lower 2×N_rods=5、overhead N_rods）随 shelf module 内部循环，非主 N 轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | rail_topology：single(1 rail) / double(2 rail sets) / two_tier(2 stacked) / extendable(+rail_inner part +PRISMATIC) / arched(连续拱管无 posts)；support_base：caster(+4 wheel parts +CONTINUOUS) vs feet(无 wheel)；storage_shelf：无 / lower(base rods) / overhead(upper mesh)。全部 forked_anchor（§4） |
| └ multiplicity | 同构件 ×N | 有 | hanger_count N∈[4,10]（§8），加权小 N 偏多 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | PRISMATIC height_slide (z, 0..0.14, A/B) + REVOLUTE hanger swing (x, ±0.35, A/B) + CONTINUOUS wheel spin (y, caster base, A/B) + PRISMATIC rail_extend (x, 0..0.25, railextend fork)。四类关节都在 sweep 里出现（axis_realization 覆盖 caster vs feet + extendable vs 非） |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别几何原型 | 有 | 直管骨架 (single/double/two_tier/extendable, Volumetric Envelope Form — 直圆管) vs 连续弯管拱 (arched_inverted_u, Volumetric Envelope Form — swept 弯管包络)。arched 登记进 rail_topology slot_choices，source-backed (skeleton_arch fork)。form_subtype 见 §4 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有(record_only) | rail_tee spheres / welded corner spheres / rail 端 caps / red_plastic ball-cap side hooks (B) / adjust_collar + clamp_knob/screw (A) / spring_button / hanger_stops。全部宿主 part visual，随 rail_z/post 位置派生贴合宿主；非独立 part、非 joint。no dedicated ④ variant（无 padding） |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/行程 | 有 | width_scale [0.88,1.12]、rail_r_scale [0.9,1.15]；关节运动包络：height_slide z [0(闭合),0.14]、rail_extend x [0,0.25]、hanger swing x [-0.35,+0.35]、wheel continuous。motion_test_plan 见下 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 材质大类 metal（powder-coated steel / brushed brass / chrome / matte-white painted）+ pale-wood/silver hangers + dark-rubber tires + red caps；配色 4 档（black_steel/brushed_gold/chrome/matte_white）。材质大类=metal 主导（品类内在），painted/brushed/chrome 覆盖 ≥ ceil(0.5×4)=2 |

**motion_test_plan (⑤ 关节)：**
- height_slide PRISMATIC z [0,0.14]：targeted `ctx.pose({height_slide:0.14})` — upper_frame world-z bbox 抬升 >0.10 且 upper_post 仍插在 sleeve 内（保留插入）。
- hanger swing REVOLUTE x ±0.35：targeted `ctx.pose({swing_0:0.35})` — hanger body 相对 rail 有可见 Y 位移；hook 仍绕 rail。
- rail_extend PRISMATIC x [0,0.25]（extendable only）：targeted `ctx.pose({rail_extend:0.25})` — rail_inner 沿 +X 伸出且两端仍 captured 在 outer 内。
- wheel_spin CONTINUOUS：captured cross-pin 过 hub，allow_overlap（每 pose 生效）。
- 全程不穿模由 harness_motion_qc（默认 on，sampled {0,lower,upper,mid} 每关节）覆盖 + 上述 targeted poses；无需 sampled-pose exemption。所有 intentional overlap（caster pin/hub、hook/rail、post/sleeve、inner/outer）在 run_tests 以 element-scoped `allow_overlap` 声明，每 pose 生效。

## 采样与覆盖审计

总组合数（离散，忽略 N 与连续 scale）：rail_topology(5) × support_base(2) × storage_shelf(3, 受 gating) = 约
5×2×3 − (arched×overhead 非法 = 2 combos) = **28 合法离散组合**；乘 hanger N (≈6 档) + 连续 scale → 远超 300。

理由：clothing rack 结构词汇为中等；主多样性来自离散 rail_topology(5) + base(2) + shelf(3) + N，
连续 scale 只做 controlled local variation，不撑多样性。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次：加权抽
rail_topology → 抽 support_base → 抽 storage_shelf（按 rail_topology 过 gating，非法则降级到 no_shelf）→
加权抽 hanger_count（小 N 偏多）→ 抽 material_style → 均匀抽 width_scale/rail_r_scale。`resolve_config`
里 clamp 所有 scale、解析 conditional shelf gating、派生 secondary/inner hanger 计数。seed=0 不特殊。
无 regression override。random sweep seeds 0-35 初评；viewer 目检 seed 0/1/2（本任务不跑 batch）。
Topology target：report-only；28 离散 combo × N × scale，1000-seed tuple 覆盖用于成熟度观察（富类别 >300 达标）。
Controlled local parameterization：width_scale [0.88,1.12]（缩放 rail 长度 / post 间距 / base 宽，independent+clamp）、
rail_r_scale [0.9,1.15]（主 rail/tube 半径，independent+clamp）。两者都不改 lower_sleeve 接口内径/位置、
不改 height_slide/rail_extend 行程、不改 hanger 间距合法性（N≤10 恒满足 spacing 不等式），故不破坏
InterfaceSpec / MatingContract / multiplicity。跨部件依赖（post 间距 x_post 同时决定 base sleeve 位置 +
upper post 位置）由单一 `x_post = 0.72 * width_scale` 派生，single-source（Contract 3c）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 rail→base→shelf→N→style→scales；weighted N；shelf gating | slot_choices_for_seed matches build choices |
| compatibility matrix | 合法：任意 rail × 任意 base × (no_shelf 全通)；lower_storage_shelf × 任意 rail；overhead_top_shelf × {single,double,two_tier,extendable}（arched 非法→降级 no_shelf）| no floating / collision / axis / bulky module failures |
| controlled local variation | width_scale / rail_r_scale，clamp；派生 x_post、rail_len；不破坏接口/clearance/joint origin/identity | proportions vary，接口不破 |
| regression overrides | none | — |
| random sweep | seeds 0-35 初评，0-999 成熟度 | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| rail_topology | 5 | yes | yes | hero ①③ slot |
| support_base | 2 | yes | no | 源池仅 2 base family（caster/feet）；round/fold spider/scissor 属另一 spine（blocked） |
| storage_shelf | 3 | yes | yes | 受 arched×overhead gating |

## Validator
- slot_choices_for_seed returns implemented module names（rail_topology / support_base / storage_shelf / hanger_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility gating：arched_inverted_u + overhead_top_shelf 被降级为 no_shelf（resolve_config 内）
- controlled local scale params clamped，不破坏 sleeve 接口 / height_slide+rail_extend 行程 / hanger 间距 / identity
- cross-part scale deps（x_post 派生）在 resolve_config 求解
- critical MatingContract：post↔sleeve 插入、hook↔rail、caster pin↔hub、rail_inner↔rail_outer 都有 allow_overlap + expect_*
- key joints：height_slide PRISMATIC z (0..0.14)、hanger swing REVOLUTE x (±0.35)、wheel_spin CONTINUOUS y、rail_extend PRISMATIC x (0..0.25)
- copied hangers follow `{prefix}_hanger_{i}` naming + even x-spacing + shared Mesh reuse

## Reject cases
- rail 未由 uprights 抬离 base（塌成货架/矮台）
- 无任何 non-fixed 关节（纯静态）→ 至少 height_slide + hanger swing 必须存在
- hanger body 不悬于 rail 下方 / hook 不绕 rail（悬空 island）
- caster 轮不通过 captured cross-pin 支撑（floating wheel）
- arched crown 上强塞 overhead shelf 导致穿模（gating 必须降级）
- upper_post 在 max height 脱出 sleeve（telescoping 失去插入）
- 连续 scale 破坏 sleeve 内径/间距导致 post 卡不进 sleeve 或 hanger 相撞
- 用 solid panel 代替 rod/tube 使其读成 wardrobe cabinet

## 与相邻类别的边界
- 不该混入：coat/hat tree、valet stand（竖直挂钉、无水平悬挂跨距）
- 不该混入：shelving unit / bookcase / wardrobe cabinet（实心隔板/面板主导）
- 不该混入：clothes-horse / accordion drying airer、drying-rack ladder（折叠晾衣，无 telescoping 悬挂 rail）
- 不该混入：curtain rod / wall track、mannequin bust、umbrella stand、carousel turntable（round 只保留 ① 圆环拓扑但已 deferred，且严禁加 turntable 旋转关节）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | round_hoop_rounder & folding_scissor 作为 disjoint-motion-spine 备选架构 deferred（见下），以保单一 telescoping spine 的一致性与可过性；如需可另开 slug 或增分支。 |

## 模板实现备注（可选）
- 共享 helper：`_create_hanger`（复用共享 hook_mesh + body_mesh）、`_add_cyl_x/y/z`、`_hollow_z_tube`/`_hollow_x_tube`（CadQuery）、`_add_caster`、`_add_lower_sleeves`。
- captured-pin overlap 需 element-scoped allow_overlap：caster cross_pin↔hub_disc、post/bushing↔lower_sleeve、rail_inner↔rail_outer、hook_loop↔rail。
- 暂不进入 seed domain（blocked）：
  - `round_hoop_rounder_rail`（var_round）：central mast + 4-arm spider base + circular mesh hoop + 径向 hanger — 需要 spider base（与 rect/feet base 互斥）与 no_shelf，属**另一 motion spine**；deferred 以保单 spine 一致性（AUTHORING §C 允许按 disjoint spine 拆分/收窄）。非因失败而 drop。
  - `folding_scissor_frame`（var_fold）：X 交叉腿 + 中央 fold REVOLUTE + 两个 moving part + FIXED rail_mount — 与 telescoping spine 及两 base 互斥的**另一 motion spine**；deferred 同理。
```
