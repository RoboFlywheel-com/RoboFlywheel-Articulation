# Scissors — Modular Spec

> 来源小类：`picture/Stationary/Scissors`（articraft_data 上游小类样本池；对象身份为 a pair of scissors / shears，两片刀刃绕中央螺钉枢轴相对开合）。slug 取规范拼写 `scissors`。
> 上游 source map：建议回填 `picture_expansion/template_source_maps/Stationary__Scissors.md`（当前尚未建立；本 spec 已逐一内联全部 record_id + module 来源，source map 缺失不影响来源完整性）。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 个 parent + 8 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 9 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（FORK_VARIANTS §7：收敛即入池——9 个样本均 compile rc=0、均含 ≥1 非 fixed joint（中央 REVOLUTE pivot）、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_blade_solid` / `_handle_solid` / `_hub_solid` / `_pinking_edge_points` / `_finger_brace_solid` / `_spring_shape` / `_canted_blade` / `blade_a` / `blade_b` / `pivot` / `spring_flex` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `scissors` |
| template path | `agent/templates/Stationary_Scissors.py` |
| test path (optional) | `tests/agent/test_scissors_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| __modular__ | `True` |
| pattern | `mixed`（2-bar pivot 链：root `blade_a` + child `blade_b` 绕中央螺钉 REVOLUTE；叠加 blade_profile / handle_loops 并联可替换层、可选 spring_assist 第二关节、以及每半刀片数 `blades_per_half` 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 单轴 fork 变体；均 converged，compile rc=0、均有中央 REVOLUTE pivot、workbench-only）|
| read_count | 9（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（小类只有这 9 个，无抽样）|
| source_index_policy | only adopted module sources are indexed below（9 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_build-a-realistic-articulated-3d-model-of-a-pair_20260609_154019_842277_6adf5ca9`）：两片镜像 steel blade 绕中央 pivot 交叉，每半接一只 red 塑料 finger-loop handle，中央 steel hub + 可见 disc cap。pivot 为 REVOLUTE 绕 +Z（出平面），`lower=-2*HALF_CANT`（全闭）`upper=28°`（全开）。**全批基线**：提供 `_blade_solid`（锥形直刃 polyline）、`_handle_solid`（neck + 圆角矩形 loop ring）、`_hub_solid`（带孔 boss）、`_half_shape`/`_handle_shape`（mirror + cant）、pivot 装配、riveted-lap allow_overlap。
- **S1 spring_loaded**（`rec_scissors_var_spring_loaded`）：在两 handle 之间桥一片 leaf spring，新增第二个 REVOLUTE `spring_flex`（绕 +X，range 0..12°），spring 用 `sweep_profile_along_spline` 建曲带，两 handle 各加 anchor/contact boss。**spring_assist 槽位来源**（第二真实活动关节）。
- **S2 offset_loops**（`rec_scissors_var_offset_loops`）：两 handle loop 改非对称——half A 小圆 thumb loop（`_thumb_loop_solid`，OD 0.030），half B 大椭圆 finger loop（`_finger_loop_solid`）。**handle_loops 槽位来源（asymmetric）**。
- **S3 long_shears**（`rec_scissors_var_long_shears`）：`BLADE_LENGTH` 约翻倍成长裁缝剪，taper/tip/pivot/handle 不变。**blade_length_scale 连续轴来源**（受控局部 scale，非拓扑）。
- **S4 blunt_tips**（`rec_scissors_var_blunt_tips`）：刀尖由尖点改圆钝安全头（filleted 半圆端），刃口仍沿中线相会。**blade_profile / blunt_safety module 来源**。
- **S5 twin_blades**（`rec_scissors_var_twin_blades`）：每半把单刃改成 `HERB_BLADES_PER_HALF=4` 片平行薄刃堆叠（`_blade_z_positions` 交错 Z 槽，`for i in range(n)` 发射 `blade_{i}`），两组在 pivot 交叉 interleave。**blades_per_half 多重性轴来源 + 循环发射范式**。
- **S6 finger_brace**（`rec_scissors_var_finger_brace`）：在大 finger loop 外缘加一只 molded 弯钩 finger-brace tang（`_finger_brace_solid`，同 handle 层 union，非独立 fixed part）。**handle_loops / finger_brace module 来源**。
- **S7 pinking_edge**（`rec_scissors_var_pinking_edge`）：刃口直边改三角 zigzag pinking 锯齿（`_pinking_edge_points`，PITCH 3 mm，两刃半 pitch 错位 mesh）。**blade_profile / pinking_sawtooth module 来源**。
- **S8 curved_blades**（`rec_scissors_var_curved_blades`）：直刃改强弯钩刃（圆弧扫掠 `HOOK_RADIUS=0.13`，刃尖偏向一侧），两刃镜像仍交叉 shear。**blade_profile / curved_hooked module 来源**。

冗余说明：S0/S1/S2/S3/S4/S6/S7/S8 的核心机构（中央 REVOLUTE pivot、两 steel hub riveted lap、blade_a root / blade_b child）完全同构；每个 fork 只改 1 根结构轴（刃形 / 刃数 / handle / spring / 长度），diff 干净。这正是 fork 池"单轴控制变量"的设计。

## 核心身份

一把剪刀 / 剪（a pair of scissors / shears）：两片镜像 steel 刀刃，**绕单一中央螺钉枢轴交叉**，每片继续延伸成一只塑料 finger-loop handle；两半绕枢轴**相对转动**（REVOLUTE，轴 = 出平面 +Z）以张开 / 闭合。**主用户机构 = 两刀刃绕中央螺钉的相对开合**（`pivot` 关节，blade_a 为 root，blade_b 为 child）。中央有 steel hub boss + 可见 disc cap（riveted lap，两 hub 共轴 nest）。

物体平躺 XY 平面（从 +Z 俯视）：+Y → 刀尖方向，−Y → finger loop 方向，+Z → 出平面（枢轴方向）。pivot 在世界原点 (0,0,0)。每半在 pivot 居原点的局部 frame 内 author，再绕 Z cant `HALF_CANT≈11°` 使两刃在原点上方交叉、handle 在下方张开（open 姿态）。

默认成熟域：真实小尺度（pivot→tip ≈ 0.09 m，整体 ≈ 0.18 m 长），刀刃可为直 / 弯钩 / 钝头 / pinking 锯齿，handle loop 可对称 / 非对称 thumb-finger / 带 finger-brace，可选 leaf spring 自张，每半 1–5 片平行刀刃（herb 多刃）。活动语义恒为"两半绕中央 +Z pivot 相对转动"，叠加可选的 spring_flex 第二 REVOLUTE。中央 disc cap / hub 恒为固定装饰（inline 成 blade_a visual，不做独立 FIXED part）。

不该混入：钳子 / pliers / 夹钳（颚口夹合而非刀刃 shear，无 finger loop）、单刃 utility knife / 美工刀（无第二刃、无 pivot、无 loop）、修枝大剪 / loppers 与园艺 anvil 剪（长杆双手，出手持文具语义但若仅尺度放大且仍单 pivot 双 loop 可由 blade_length_scale 覆盖——本类不扩到双手长杆）、订书机 / hole punch（压合机构 + 不出刃）。Stationary 大类内也区别于 Pen / Clip / Folder / Calculator 等无双刃 pivot 的文具。

## 槽位 + 候选模块表

> **建模注记（重要）**：scissors 是 **2-bar pivot 链**——`blade_a`（root，承 steel 刃 + hub + cap + 自己那只 handle visual）与 `blade_b`（child，承自己的 steel 刃 + handle），二者绕中央螺钉 REVOLUTE `pivot`（轴 +Z，origin 在真实螺钉几何 (0,0,0)）。blade_profile 与 handle_loops 是 **blade_a/blade_b 上成对镜像应用的可替换几何层**（两半同形，仅 mirror）；spring_assist 是挂 blade_a 的**可选第二活动子件**；blades_per_half 是**每半 steel 刃的多重性轴**。disc cap / hub 恒为 blade_a 的 inline visual。下面 3 个离散 slot + 1 个 multiplicity 轴。

### Slot A：blade_profile（刀刃轮廓 + 刃尖/刃口形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_pointed（基线） | S0 parent / S3 long_shears | `_blade_solid` L57-87（锥形 polyline，尖点在中线）| eligible if compatible | 近直锥形刃，6 点 polyline，刃尖收成中线尖点 |
| curved_hooked | S8 curved_blades | `_blade_solid` L68-138（圆弧扫掠 `HOOK_RADIUS`，刃尖偏向一侧）| eligible if compatible | 沿圆弧扫掠的钩刃，cutting/spine 两侧 32 点采样，刃尖强烈侧偏（>15 mm lateral）|
| blunt_safety | S4 blunt_tips | `_blade_solid` L63-101（圆钝半圆端，刃口仍达中线）| eligible if compatible | 同直刃锥形但刃尖换 filleted 半圆钝头（保留 ≥BLADE_TIP_WIDTH 宽度的圆端，不收尖）|
| pinking_sawtooth | S7 pinking_edge | `_pinking_edge_points` L65-101 + `_blade_solid` L103-145（刃口三角锯齿）| eligible if compatible | 刃口 +X 侧带规则三角 zigzag pinking 齿（PITCH 3 mm），近尖处淡出，两刃半 pitch 错位 mesh |

> 4 candidate（达 3-6 目标）。每个刃形改变刃的 polyline/扫掠轮廓与 run_tests 几何断言，结构差异成立（curved 多侧偏、pinking 多齿子特征、blunt 改端帽），非纯尺寸。

### Slot B：handle_loops（finger-loop 手柄安排）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| symmetric_loops（基线） | S0 parent | `_handle_solid` L90-134（neck + 圆角矩形 loop ring，两半等大镜像）| eligible if compatible | 两 handle loop 等大对称（rect ring，outer−inner cut），两半镜像 |
| offset_thumb_finger | S2 offset_loops | `_thumb_loop_solid` L123-150 + `_finger_loop_solid` L152-183 | eligible if compatible | 非对称：half A 小圆 thumb loop（OD 0.030 圆环），half B 大椭圆 finger loop，两 loop 明显不等 |
| finger_brace_tang | S6 finger_brace | `_handle_solid` L99-144 + `_finger_brace_solid` L146-193（外缘弯钩 tang union 进 handle 层）| eligible if compatible | 在 finger loop 外缘 union 一只 molded 弯钩 finger-brace tang（同 handle 层，非独立 part），该半提供 loop+brace 两握点 |

> 3 candidate（达目标下限）。三者改 handle 层的 part-internal 几何（对称等大 / 非对称双 loop / 多 brace 子特征），结构差异成立。

### Slot C：spring_assist（可选自张 leaf spring；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | S0 parent（多数样本）| （无 spring part；无第二关节）| eligible if compatible | 无 spring（baseline 缺省，仅中央 pivot 一个活动关节）|
| leaf_spring | S1 spring_loaded | `_spring_shape` L214-255（spline 扫掠曲带）+ anchor/contact boss L199-211 + 第二 REVOLUTE `spring_flex` L373-386 | eligible if compatible | 两 handle 间桥一片 leaf spring（独立 part），新增 REVOLUTE `spring_flex` 绕 +X（range 0..12°）自张，handle 各加 anchor/contact boss |

> 降级理由（含 none 共 2 candidate）：optional 机构槽，候选为 {缺省, 1 个真实 spring 机构}。`none` 是 parent 基线的合法取值，非"未实现占位"。leaf_spring 相对 none **新增 1 个 part + 1 个 REVOLUTE joint**，拓扑改变。

## 槽位图（slot graph）

```
pattern: mixed（2-bar pivot 链 + 并联可替换刃/柄层 + 可选 spring + 每半刃数多重性）

        blade_a (root)  ──[REVOLUTE pivot, axis +Z, origin (0,0,0) 真实螺钉]──>  blade_b (child)
          │  承载: steel 刃[N](blade_profile)·hub·disc cap(inline)·handle(handle_loops)        │ 承载: steel 刃[N]·handle(镜像)
          │                                                                                      │
   ┌──────┴───────┐                                                                       (随 blade_a 选择镜像)
   │              │
 blade_profile  blades_per_half[N]            spring_assist (Slot C, optional)
 (Slot A)       (multiplicity 1..5)            │
   │            for i in range(N):             leaf_spring: 独立 part，
 刃 polyline/   blade_{i} 交错 Z 堆叠           REVOLUTE spring_flex 绕 +X
 扫掠 (两半镜像) (两半 interleave)               @ handle 内面 anchor (range 0..12°)

 handle_loops (Slot B)：blade_a/blade_b 上的 handle visual（neck+loop，两半镜像或非对称）
 disc cap + hub：blade_a 的 inline visual（FIXED 语义，不建 part）
```

接口点位（每条连接）：
- **blade_a → blade_b（pivot）**：mating = 中央螺钉轴线（`origin=(0,0,0)`，两 steel hub 共轴 riveted lap），joint = REVOLUTE，axis `(0,0,1)`，range `[-2*HALF_CANT, +28°]`。MatingContract = **省略（grandfathered）**：两 hub boss 沿一根销轴 nest，是 captured-pin 过盈几何，配 broad `allow_overlap(blade_a, blade_b)`。origin (0,0,0) 落在 hub/cap 真实几何上（≤0.015 m）。
- **blade_a → spring（spring_flex）**：mating = handle A 内面 anchor boss（`origin=(0, SPRING_ANCHOR_Y, anchor_z_on_a)`，落在 anchor boss 真实几何），joint = REVOLUTE，axis `(1,0,0)`，range `[0, 12°]`；spring 自由端接触 handle B 内面。
- **每半 steel 刃 blade_{i}**：non-articulated visuals（同一 part 内堆叠），各刃在 Z 上 `HERB_STACK_PITCH` 等距交错；A 取偶 slot、B 取奇 slot，interleave。
- **handle / cap / hub**：blade_a/blade_b 的 inline visuals（FIXED 语义），handle 在 Z 上 stack（A 在 −Z，B 在 +Z，共享 z=0 面不互穿）。
- **互斥/可选/派生**：Slot C optional；blade_profile/handle_loops 在两半上**镜像派生**（half B = half A mirror("YZ")，handle 可整组非对称）；blades_per_half 的 N 决定每半刃数与交错堆叠 Z 跨度。

## 每槽位 Module Emits / Interfaces

### Slot A / module straight_pointed
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `blade_steel`（blade_a/blade_b 上锥形直刃 polyline，extrude）| S0 / `_blade_solid` L57-87 |
| internal joints | 无（刃是 part visual）| — |
| downstream interface | 刃尖在 +Y 中线收尖；刃根 hub 在 pivot | S0 / L57-87 |

### Slot A / module curved_hooked
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `blade_steel`（圆弧扫掠钩刃，刃尖侧偏）| S8 / `_blade_solid` L68-138 |
| downstream interface | 刃尖偏向 +X（half A）/ −X（half B 镜像），仍在 pivot 上方交叉 | S8 / L68-138 |

### Slot A / module blunt_safety
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `blade_steel`（锥形刃 + filleted 半圆钝端帽）| S4 / `_blade_solid` L63-101 |
| downstream interface | 刃尖为圆钝端（width ≥ BLADE_TIP_WIDTH），刃口仍达中线 | S4 / L63-101 |

### Slot A / module pinking_sawtooth
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `blade_steel`（刃口三角 zigzag pinking 齿，近尖淡出）| S7 / `_pinking_edge_points` L65-101 + `_blade_solid` L103-145 |
| downstream interface | 刃口 +X 侧锯齿，两刃半 pitch 错位 mesh | S7 / L65-145 |

### Slot B / module symmetric_loops
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `handle_loop`（blade_a/blade_b 上 neck + 等大圆角矩形 loop ring，镜像）| S0 / `_handle_solid` L90-134 |
| upstream interface | handle neck 接 pivot hub 下方（−Y），Z stack 不互穿 | S0 / L90-134 |

### Slot B / module offset_thumb_finger
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `thumb_loop`（half A 小圆环）/ `finger_loop`（half B 大椭圆环）| S2 / `_thumb_loop_solid` L123-150、`_finger_loop_solid` L152-183 |
| upstream interface | 同 neck 接 pivot 下方；两 loop 明显不等大 | S2 / L123-183 |

### Slot B / module finger_brace_tang
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `handle_loop` + `finger_brace`（finger loop 外缘 union 弯钩 tang，同层）| S6 / `_handle_solid` L99-144、`_finger_brace_solid` L146-193 |
| upstream interface | brace 自 loop 外 rim 起、union 进 handle 实体（非独立 part）| S6 / L146-193 |

### Slot C / module leaf_spring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spring`（leaf spring 曲带，spline 扫掠）；blade_a/blade_b 加 anchor/contact boss visual | S1 / `_spring_shape` L214-255、boss L199-211 |
| internal joints | `spring_flex` REVOLUTE，axis (1,0,0)，range [0,12°] | S1 / L373-386 |
| upstream interface | handle A 内面 anchor boss（joint origin 落 boss 真实几何）；自由端接 handle B 内面 | S1 / L302-335 |

### blades_per_half multiplicity / module blade_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `blade_{i}`（每半 N 片平行薄刃，Z 交错堆叠）× N，刃形由 Slot A 派生 | S5 / `_canted_blade` + 循环 L210-221/256-266 |
| internal joints | 无（同 part 内 visuals；整半绕 pivot 一起转）| S5 |
| upstream interface | 各刃 Z slot `(i-(2N-1)/2)*PITCH`，A 偶 / B 奇 interleave；hub 跨全 stack | S5 / `_blade_z_positions` L71-83、`_herb_hub_solid` L127-144 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| blade_profile | enum | {straight_pointed, curved_hooked, blunt_safety, pinking_sawtooth} | straight_pointed | choice | deterministic procedural sampler 选择 | Slot A 表 |
| handle_loops | enum | {symmetric_loops, offset_thumb_finger, finger_brace_tang} | symmetric_loops | choice | sampler 选择 | Slot B 表 |
| spring_assist | enum | {none, leaf_spring} | none | choice | sampler 选择；optional | Slot C 表 |
| blades_per_half | int | [1, 5] | 1 | independent | 加权采样（1 单刃高频，>1 herb 多刃稀有）后 clamp | §8 / S5 `HERB_BLADES_PER_HALF` |
| material_style | enum | {steel_red, steel_green, steel_black, gold_ivory} | steel_red | choice | sampler 选择（palette）| S0/S5 配色 |
| blade_length_scale | float | [0.85, 2.05] | 1.0 | independent | 缩放 `BLADE_LENGTH`（pivot→tip）；上界覆盖 long_shears（约翻倍），clamp 保真实小尺度 | S3 long_shears / S0 L30 |
| loop_size_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 finger-loop 尺寸；clamp 保 loop 在 handle reach 内 | S0 L39-41 |
| handle_reach_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 `HANDLE_LENGTH`（pivot→loop 端）| S0 L35 |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放 pivot `upper`（张开角）；clamp 到 [12°, 40°] 真实开度 | S0 L256 |
| spring_flex_scale | float | [0.80, 1.20] | 1.0 | conditional | 仅 leaf_spring 存在时缩放 spring_flex range；clamp 到 [6°, 18°] | S1 L384 |
| (—) | constraint | — | — | inequality | 中央 pivot origin 必须落在 hub/cap 真实几何 (0,0,0)±0.015 m；blade_length_scale 放大刃时 hub/cap 尺寸不随之缩放，origin 仍贴 hub | 接口 / captured-pin |
| (—) | constraint | — | — | inequality | blades_per_half=N 时整 stack Z 跨度 `(2N-1)*PITCH` 须 < hub 高度容许；handle Z offset = hub 半高 + handle 半厚，避免刃/handle 互穿（由 `_HANDLE_Z_OFFSET` 派生）| S5 L52-57 |

连续 scale 默认独立采样 → conditional（spring_flex_scale 仅 spring 存在时解析）→ inequality 把 pivot origin 钉在 hub、把多刃 stack Z 跨度投影回 hub 容许。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

scissors 含 **1 根 multiplicity 轴**（每半平行刀刃数），单独声明：

- `count_param`: **`blades_per_half`**（每个 scissor 半上平行薄刃的片数）
- `N_range`: `[1, 5]`（产品域；1=普通单刃剪、2-5=herb / 多刃香草剪）。已覆盖样本：S0=1（单刃）；S5=4（herb 4 刃）。
- sampling domain（权重档）：单刃高频（1 最常见），多刃（2-5）稀有长尾——多数剪刀是单刃，herb 多刃是少数品类。
- copied object: 单片 steel 刃 visual `blade_{i}`（刃形由 Slot A 派生）；几何由共享 helper `_blade_mesh`（按 blade_profile 分支 + Z slot 平移 + mirror/cant）生成。N=1 时退化为单刃 `blade_0`（仍用同一循环路径，N-invariant 命名）。
- naming: `blade_{i}` / `for i in range(n)`（S5 已用此结构，直接作 module 源码）；hub 跨全 stack。
- placement: 交错堆叠——刃 Z center `(slot-(2N-1)/2)*PITCH`，half A 取偶 slot、half B 取奇 slot，使两组 interleave；hub 高度随 N 扩展，handle Z offset 随之外移。
- joint policy: 单刃不引入额外关节（所有刃同属一个 blade part，绕 pivot 整体转）；唯一活动关节仍是中央 `pivot`（+ 可选 spring_flex）。多刃只是 part-internal visual 多重性，不增 joint。
- source/gating: 循环范式 S5 L210-221/256-266；N>1 时强制 blade_profile 退化为 `straight_pointed`（薄 herb 刃只见直刃；curved/pinking/blunt 与多刃堆叠组合上游无样本，gating 排除以免穿模/无源造型）。

## 拓扑多样性审计

总组合数（离散槽）：blade_profile(4) × handle_loops(3) × spring_assist(2) = **24**
叠加 multiplicity：blades_per_half(5 值，但 N>1 时 profile 锁 straight) → N=1 时 24 组合 + N∈{2,3,4,5} 各 3(handle)×2(spring)=6 组合 = 24 + 4×6 = **48 distinct 拓扑等价类**（不同刃数 → 不同 visual/part 计数 = 不同拓扑）。

理由：仅 N=1 的 24 个离散槽组合即 >10；叠多刃轴后 ~48，distinct 拓扑充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——先加权选 blade_profile / handle_loops / spring_assist（profile 偏 straight、handle 偏 symmetric、spring 偏 none）、再加权采 blades_per_half（单刃偏多）、采连续 scale，经 `resolve_config` 解析 conditional（spring_flex_scale）与 inequality（pivot origin 钉 hub、多刃 stack Z 跨度、N>1⇒profile 退 straight）。`seed=0` 不特殊。无需 regression overrides（若 sweep 暴露特定 seed 失败，再稀疏加显式 override 并注明）。
Topology target：1000-seed slot choice tuple distinct 目标 ≈48 上界（本类离散组合受样本词汇表限；若实测低，多因多刃组合稀有，可调宽 blades_per_half 权重）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：初版即含 `blade_length_scale` / `loop_size_scale` / `handle_reach_scale` / `open_angle_scale` / `spring_flex_scale`（§7），全部 clamp/conditional，受 captured-pin origin、hub stack 容许、真实开度约束，不改变拓扑、pivot REVOLUTE 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：blade_profile→handle_loops→spring_assist→blades_per_half→scales；加权（profile 偏 straight、handle 偏 symmetric、spring 偏 none、单刃偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | N>1⇒blade_profile 锁 straight_pointed；spring_flex_scale 仅 leaf_spring 时生效；pivot origin 恒钉 (0,0,0) hub 几何；两半刃 interleave 不同 Z slot | 无穿模/悬空，pivot origin 贴 hub，两刃交叉、开合分离刃尖、spring 真实活动 |
| controlled local variation | blade_length / loop_size / handle_reach / open_angle / spring_flex scale + clamp | 比例变化不破坏 captured-pin origin、hub stack、loop 闭环、joint range、类别身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 captured-pin overlap / origin 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A blade_profile | 4 | yes | yes | straight/curved/blunt/pinking 四真实刃形 |
| B handle_loops | 3 | yes | yes | symmetric / offset thumb-finger / finger-brace |
| C spring_assist | 2 | yes | no | optional：{none, leaf_spring}（第二真实关节）|
| (mult) blades_per_half | [1-5] | — | — | 多重性轴，单刃/herb 多刃，提供拓扑乘子 |

## Validator

- slot_choices_for_seed returns implemented module names（blade_profile / handle_loops / spring_assist + blades_per_half count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：N>1⇒straight blade；spring_flex 仅 leaf_spring；pivot origin 恒在 hub 几何
- optional regression overrides 初版为空（如加须稀疏 + 注明）
- controlled local scale params 全部 clamp，且不破坏 captured-pin origin / hub stack / loop 闭环 / joint range / 类别身份
- critical captured-pin overlap：两 steel hub riveted lap（broad allow_overlap blade_a/blade_b，grandfathered，MatingContract 省略）；spring anchor/contact 与 handle 内面接触
- key joints：中央 `pivot` REVOLUTE axis (0,0,1) range [-2*HALF_CANT, upper]；可选 `spring_flex` REVOLUTE axis (1,0,0)
- 开合测试：opening the pivot 使两刃尖分离（blade_b 尖 x 偏移随开度增大）；closing 使刃尖相聚
- copied objects 遵循 `blade_{i}` 命名 + 交错 Z placement + 整半同 pivot
- disc cap / hub 恒为 blade_a inline visual（不建 FIXED 装饰 part）

## Reject cases

- 把中央 pivot 做成 FIXED 或省略（剪刀必须有两半相对开合的 REVOLUTE）。
- pivot origin 不在中央螺钉几何上（漂浮于空、>0.015 m 离 hub/cap），或没有两 hub 共轴的 riveted lap allow_overlap → captured-pin overlap 被判失败。
- 两刃不交叉（两 steel 半在同侧、blade_a/blade_b 刃尖 X 不异号），或开合不分离刃尖（pivot pose 变化刃尖不动）。
- disc cap / hub 做成独立 FIXED part（违反"不动装饰 inline blade visual"）。
- 多刃用手写 2-3 片代替 `for i in range(N)` 循环 + 共享 helper（多重性退化）；或 N>1 时两半刃不 interleave / 不同 Z slot。
- 刀刃用 boxy 占位代替真实锥形/扫掠/锯齿轮廓（curved 须圆弧扫掠、pinking 须真实齿、blunt 须圆端）。
- handle finger loop 未做成真实闭环 ring（实心块），或 offset/brace 与 base loop 脱开成孤岛。
- spring_assist=leaf_spring 但 spring 是 FIXED 或无第二关节（变体要求 ≥2 活动关节）。
- 连续 scale 把刀刃放到非真实尺度（如 blade_length_scale 越界使整剪 >0.4 m），或 open_angle 超出真实开度。
- config_from_seed 采到非法组合（如 N>1 + pinking_sawtooth，上游无源）。

## 与相邻类别的边界

- 不该混入：钳子 / pliers（颚口夹合而非刀刃 shear，无 finger loop，pivot 处是 box joint 不是双刃交叉）。
- 不该混入：单刃 utility knife / box cutter（单刃、无 pivot、无第二半、无 finger loop）。
- 不该混入：园艺 anvil 剪 / loppers / 大型修枝剪（长杆双手操作；本类限手持单 pivot 双 loop，长度仅由 blade_length_scale 在真实小尺度内变化）。
- 不该混入：订书机 / 打孔器（压合或冲孔机构，不出刃，无双刃 shear pivot）。
- Stationary 大类内：区别于 Pen / Clip / Folder / Calculator 等无双刃中央 pivot 的文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 自动批量授权（spec + 模板一并产出，不停审）。模板已实现 `agent/templates/Stationary_Scissors.py`（注册于 `cli/template.py` TEMPLATE_REGISTRY）。`uv run articraft template sweep-pipeline scissors` 分阶段全 pass_rate.95，verdict=pass， distinct。降级说明：spring_assist 为 optional 2-candidate 槽（{none, leaf_spring}），blade_profile/handle_loops 已达。剩余：viewer 目检（人工）。|

## 模板实现备注（可选）

- 共享 helper：`_blade_mesh`（按 blade_profile 分 straight/curved/blunt/pinking 四路；统一接受 Z slot offset + side 供多刃堆叠与 mirror）、`_handle_mesh`（按 handle_loops 分 symmetric/offset/brace；side-aware）、`_hub_mesh`（按 blades_per_half 决定 hub 高度跨全 stack）、`_blade_z_slots`（按 N 生成交错 Z 槽）、`_spring_mesh`（spline 扫掠 leaf spring）。
- 关键 captured-pin overlap：两 steel hub riveted lap 需 **broad** `allow_overlap(blade_a, blade_b, reason=...)`（pivot 处两 hub/cap/多刃 stack 沿一根销轴 nest，element-scoped 难穷举各刃对，按 AUTHORING.md §B 对 captured pin 用 broad allow_overlap）；spring anchor/contact boss 与 handle 内面接触（spring part 与 blade_a/blade_b 的 allow_overlap）。
- pivot 与 spring_flex joint 均 **省略 MatingContract**（captured-pin / 接触面 grandfathered）；origin 落真实 hub/anchor 几何（≤0.015 m）。
- 派生与门控集中在 `resolve_config`：N>1⇒straight profile、spring_flex_scale conditional、blade_length/loop/reach/open_angle clamp、hub stack Z 跨度。
- 开合测试：pose pivot 到 upper 使 blade_b 刃尖 |x| 增大（分离）、到 lower 使刃尖相聚（参考 S0 run_tests L340-382）。
- 模板实现前已深读近邻：`shopping_bucket.py`（直接 build + 并联 children + multiplicity + captured-pin bail）、`calculator.py`（function-set 结构基线）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/mult/pivot | straight_pointed / symmetric_loops / 基线 | rec_..._6adf5ca9 | `_blade_solid` L57-87、`_handle_solid` L90-134、`_hub_solid` L137-151、pivot L244-257、riveted-lap allow_overlap L396-402 | 直刃 + 对称 loop + 中央 REVOLUTE pivot + hub/cap 基线 |
| S1 | C | leaf_spring | rec_scissors_var_spring_loaded | `_spring_shape` L214-255、boss L199-211、`spring_flex` REVOLUTE L373-386 | 可选 spring part + 第二活动关节 |
| S2 | B | offset_thumb_finger | rec_scissors_var_offset_loops | `_thumb_loop_solid` L123-150、`_finger_loop_solid` L152-183 | 非对称 thumb/finger loop |
| S3 | (scale) | blade_length_scale | rec_scissors_var_long_shears | `BLADE_LENGTH` 放大 | long shears 连续长度轴 |
| S4 | A | blunt_safety | rec_scissors_var_blunt_tips | `_blade_solid` 圆钝端 L63-101 | 钝头安全刃 |
| S5 | mult | blades_per_half | rec_scissors_var_twin_blades | `_blade_z_positions` L71-83、`_herb_hub_solid` L127-144、循环 L210-221/256-266 | 每半多刃 multiplicity + 循环范式 |
| S6 | B | finger_brace_tang | rec_scissors_var_finger_brace | `_finger_brace_solid` L146-193 | finger loop 外缘 brace tang |
| S7 | A | pinking_sawtooth | rec_scissors_var_pinking_edge | `_pinking_edge_points` L65-101、`_blade_solid` L103-145 | pinking 锯齿刃口 |
| S8 | A | curved_hooked | rec_scissors_var_curved_blades | `_blade_solid` 圆弧扫掠 L68-138 | 强弯钩刃 |
