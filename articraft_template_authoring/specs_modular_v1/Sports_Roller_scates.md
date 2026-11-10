# Modular Spec — `roller_skates` (Sports / Roller scates)

## 元信息
| 项 | 值 |
|---|---|
| slug | `roller_skates` |
| template path | `agent/templates/Sports_Roller_scates.py` |
| test path (optional) | `tests/agent/test_roller_skates_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children boot↔chassis on the sole + multiplicity over wheels) |

`pattern` 说明：每个 skate 是一个 boot (parent root) 之下挂三个并列 module 子树：chassis/wheels（multiplicity 轴在此），ankle cuff（revolute），closure（boot 表面 + cuff 表面的 strap/lace 装饰，随各自宿主 part 走）。整对 skate = 一份 `_add_skate` 构造，右 skate 以 `side=-1` 镜像并 FIXED-mount 到左 boot。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (parent + 7 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

读过的 8 份（全部 `revisions/rev_000001/model.py`）：
- S0 parent `rec_a-pair-of-inline-roller-skates-with-hard-boots-a_…26f6e0cf` (661 行；inline_4 + hard_shell + laces)
- S1 `rec_roller_skates_var_inline3` (717 行；N=3, `WHEELS_PER_SKATE` 参数化的 inline 框架)
- S2 `rec_roller_skates_var_inline5` (701 行；N=5, `WHEEL_COUNT`+`WHEEL_SPACING` 参数化)
- S3 `rec_roller_skates_var_quad` (758 行；2×2 双 truck 底盘)
- S4 `rec_roller_skates_var_softboot` (686 行；soft 高帮鞋)
- S5 `rec_roller_skates_var_lowcut` (731 行；低帮速滑鞋 + 短 cuff band)
- S6 `rec_roller_skates_var_buckle` (775 行；ratchet 卡扣带 + power strap)
- S7 `rec_roller_skates_var_velcro` (754 行；魔术贴宽带)

## 核心身份

一双（pair）轮滑鞋：刚性/软质靴体 + 踝部铰接 cuff + 一组在地面共面滚动的轮子，挂在一个底盘（单列 inline 长 rail 或 quad 双横 truck）下。每只 skate 局部坐标系 +X 趾尖、+Y 横向、+Z 向上、地面 z=0。右 skate 是左 skate 同一构造的横向镜像（`side` 乘子，绝不负缩放网格），FIXED-mount 到左 boot 之下。

核心活动语义：(1) 每个轮子绕横向 +Y 轴一个 **CONTINUOUS** spin joint，自由独立旋转、原地自转；(2) 每只靴一个 **REVOLUTE** 踝 cuff_flex joint（绕 +Y，前倾为正，限位约 [-0.18, +0.50] rad）。靴面/cuff 面的鞋带、卡扣带、魔术贴带是各自宿主 part 上的 visual，不是独立 part（除 power/instep strap 仍贴在 boot/cuff 上随之运动）。

默认成熟域：真实轮滑鞋的 inline 3–5 轮单列、或 quad 2×2 四轮两横轴；硬壳/软帮/低帮三种靴型；鞋带/卡扣/魔术贴三种闭合。

## 槽位 + 候选模块表

### Slot A：chassis_arrangement（底盘 + 轮子 multiplicity，主 multiplicity 轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| inline_N | S1 rec_roller_skates_var_inline3 | L48-L71（dims: WHEELS_PER_SKATE/AXLE_XS 派生）, L210-L233（rail mesh）, L378-L421（frame+wheel 装配循环）| eligible if compatible | 单列双 rail rockered frame；`AXLE_XS` 从 N 在固定 wheelbase 上等距派生；rail bottom 在每个 axle station 拱起 boss、station 间为 arch；N 个轮单文件 in-line；rail 长度/boss 站随 N 重算 |
| inline_N (N=4 baseline) | S0 parent …26f6e0cf | L48-L77（dims, AXLE_XS 为 4 元 tuple）, L199-L222（rail mesh）, L367-L411（frame+wheel）| eligible if compatible | 同上 single-file twin-rail，N=4 的 baseline；parent 直接以 AXLE_XS tuple 迭代（模板须改成读单个 N 再派生 stations）|
| inline_N (N=5 packing) | S2 rec_roller_skates_var_inline5 | L48-L58（WHEEL_COUNT/WHEEL_SPACING/AXLE_XS 派生 + RAIL_HALF_SPAN 从 N 派生）| eligible if compatible | N=5 的 packing 证据：更小 `WHEEL_RADIUS=0.034`、`WHEEL_SPACING=0.072` 固定 → rail 半跨 = `_wheelframe_half+0.024`，证明 N↑ 须缩轮径或加 wheelbase 防 tire-tire 重叠 |
| quad_2x2 | S3 rec_roller_skates_var_quad | L55-L101（truck dims/corners）, L221-L268（baseplate+hanger mesh）, L414-L472（双 truck frame + 4 corner 轮循环）| eligible if compatible | 两块短横 truck plate（front/rear baseplate + hanger crossbar+arms+kingpin）取代单列 rail；4 轮在 2×2 corner 阵列（front/rear × lateral/medial），固定 4 轮 |

> inline_3/4/5 是同一单列 frame 上纯 N（multiplicity）样本；quad_2x2 是独立 arrangement（不同底盘拓扑 + 不同 placement law），但仍由同一 for-i 循环（over corner 位置）发射。模板把 wheel_count + arrangement 当作**一个** slot，N 驱动 inline 分支，arrangement enum 在 {inline, quad} 间切换。

### Slot B：boot_form

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| hard_shell | S0 parent …26f6e0cf | L104-L196（shell/heel/toe/sole/shaft/liner side-loft + extrude）, L340-L347（boot visuals）| eligible if compatible | 刚性 molded superellipse side-loft 外壳（exponents 2.5, segments 64）+ 高挺 hollow ankle shaft（L164-L173）+ liner_collar；硬壳 + 红 heel_panel + dark toe_bumper |
| soft_boot | S4 rec_roller_skates_var_softboot | L112-L196（soft upper exp=2.0 + quilt_panel + toe_cap + padded collar + liner）, L356-L362（boot visuals）| eligible if compatible | 软高帮：rounder side-loft（exponents 2.0, smooth_passes 2）、quilt_panel 绗缝叠层、padded_collar 厚壁环、更深 lace throat、更厚 padded tongue；无刚性 shaft |
| low_cut | S5 rec_roller_skates_var_lowcut | L73-L83（SHELL_TOP_Z/短 cuff band dims）, L114-L255（cut-down shell + 短 cuff_band/cuff_lip mesh）, L345-L351（boot visuals）| eligible if compatible | 低帮 molded shell 削到踝骨高度（`SHELL_TOP_Z=0.148`），无 tall shaft；cuff 退化为短 ~32mm 的 flexing band（L229-L253），tongue 缩短并从 cuff band 口穿出 |

### Slot C：closure

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| laces | S0 parent …26f6e0cf | L296-L312（`_lace_centers`）, L349-L365（eyelet_stay_lateral/medial + lace_0..4 rungs）, L417-L428（cuff strap+strap_buckle）| eligible if compatible | tongue + 两侧红 eyelet stays + 5 根横跨 tongue 的 lace rung（CONTINUOUS 装饰圆柱）+ cuff 上单条 strap+steel buckle |
| buckle_ratchet | S6 rec_roller_skates_var_buckle | L300-L304（INSTEP_STRAP_COUNT/dims）, L307-L323（`_instep_strap_positions(n)`）, L326-L394（`_add_strap_and_buckle` 共享 helper：strap+ladder ribs+cam buckle+lever+anchor）, L430-L433（instep loop ×N）, L498-L510（cuff power_strap）| eligible if compatible | molded ladder 带 ×N 卡在 cam buckle 中跨 instep + 宽 ratcheting power strap 压 cuff；instep 带与 power strap 共享同一 helper |
| velcro_strap | S7 rec_roller_skates_var_velcro | L82-L93（INSTEP_STRAP_COUNT/dims/FRACTIONS）, L319-L336（`_instep_strap_centers(n)`）, L338-L355（`_build_flat_strap_mesh` 共享 flat-band helper）, L390-L408（instep loop ×N + patches）, L459-L474（cuff velcro 宽带 + patch）| eligible if compatible | 宽平 hook-and-loop 织带 ×N 跨 instep（每带末端 hook patch）+ 更宽 velcro 带绕 cuff 前面 |

每 slot ≥3 candidates，无需 degrade-to-2。

## 槽位图（slot graph）

pattern: mixed（boot 为 root；chassis/cuff/closure 并列挂在 boot 子树上；chassis 内对 wheels 做 multiplicity）

```
left_boot (root part)
  │
  ├─[FIXED, origin=Origin()] ──────────────► frame  (Slot A chassis)
  │        interface: frame deck_plate 顶面坐贴 boot sole 底面 (DECK_PLATE_Z1≈SOLE_BOTTOM_Z+0.3mm seat)
  │        └─[CONTINUOUS ×N, axis=+Y, origin=(station_x, wheel_y, AXLE_Z)] ─► wheel_i  (Slot A 复制件)
  │                 interface: axle boss/hanger crossbar 处 contact；wheels 共面 z=0
  │
  ├─[REVOLUTE, axis=+Y, origin=CUFF_PIVOT, limits≈[-0.18,+0.50]] ──────────► cuff  (Slot B 派生几何 / Slot C cuff 带)
  │        interface: cuff hollow collar 同心套在 boot shaft 外、pivot_rivet 嵌入 shaft 壁；正 q 前倾过趾
  │
  └─ boot 表面 closure visuals (Slot C: tongue/eyelet/lace 或 instep strap×M)  ← 直接挂 boot，无独立 joint

right_boot ──[FIXED, origin=RIGHT_SKATE_OFFSET, yaw=RIGHT_SKATE_YAW] mounted under left_boot
            (整只右 skate 子树以 side=-1 镜像重建)
```

跨 slot 连接说明：
- **boot → frame**：FIXED，接口为 sole 底面 ↔ deck_plate 顶面（坐贴 0.3mm seat）。inline 分支 deck_plate = 长 box；quad 分支 deck_plate = 短桥 box + 两 truck baseplate/hanger。
- **frame → wheel_i**：CONTINUOUS，axis=(0,1,0)，origin 在 axle boss/hanger 接触点 `(station_x, wheel_y, AXLE_Z)`，AXLE_Z=WHEEL_RADIUS 使轮触地。inline：wheel_y=0；quad：wheel_y=±side·WHEEL_Y_OFFSET。
- **boot → cuff**：REVOLUTE，axis=+Y，origin=CUFF_PIVOT（踝枢轴），limits 在合法窗口内。Slot B 决定 cuff 几何高度（hard/soft 高 collar vs low_cut 短 band）与 pivot Z。
- **closure**：laces/velcro/buckle 的 instep 带挂 boot（随 boot），cuff strap/power strap 挂 cuff（随 cuff_flex 运动）。无新增 joint（带为宿主 part 的 visual）。
- **left → right**：FIXED，右子树整体镜像 + 偏移 + 轻 yaw（toe-in）。两 skate 之间无接触（`allow_isolated_part` + `expect_origin_distance` 0.10–0.20）。

## 每槽位 Module Emits / Interfaces

### Slot A / module inline_N
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{prefix}_frame`（deck_plate + rail_lateral + rail_medial visuals），`{prefix}_wheel_{i}` ×N（tire+hub+axle visuals）| S1 / L378-L421 |
| internal joints | `{prefix}_frame_mount` FIXED(boot→frame)；`{prefix}_wheel_{i}_spin` CONTINUOUS axis+Y ×N | S1 / L380-L421 |
| upstream interface | frame FIXED 到 boot，deck_plate 顶面坐贴 boot sole | S1 / L379-L399 |
| downstream interface | 每轮 spin joint origin=(AXLE_XS[i],0,AXLE_Z)；axle 横穿两 rail（captured-pin allow_overlap）| S1 / L413-L421, S0 / L495-L502 |

### Slot A / module quad_2x2
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{prefix}_frame`（短 deck_plate + front/rear baseplate + front/rear hanger）；`{prefix}_wheel_{i}` ×4 | S3 / L414-L472 |
| internal joints | frame_mount FIXED；`{prefix}_wheel_{i}_spin` CONTINUOUS axis+Y ×4 在 2×2 corner | S3 / L463-L472 |
| upstream interface | 两 truck baseplate 顶面坐贴 boot sole（短桥 deck_plate 连接两 truck 区）| S3 / L423-L447 |
| downstream interface | wheel origin=(TRUCK_{F/R}_X, ±side·WHEEL_Y_OFFSET, AXLE_Z)；axle 捕获在 hanger crossbar | S3 / L449-L472, L555-L564 |

### Slot B / module hard_shell
| emits | 描述 | 来源 |
|---|---|---|
| parts | boot visuals：shell / sole / shaft（hollow tall）/ liner_collar / heel_panel / toe_bumper（皆为 boot part 的 visual，不独立）| S0 / L104-L196, L340-L347 |
| internal joints | 无（boot 内部全为 visual）| — |
| upstream interface | boot 是 skate 子树 root；右 boot 由 left 经 FIXED 镜像 mount | S0 / L330-L338 |
| downstream interface | shaft 外壁供 cuff collar 同心套接 + pivot_rivet 嵌入；sole 底面供 frame 坐贴；tongue 供 closure | S0 / L341-L347 |

### Slot B / module soft_boot
| emits | 描述 | 来源 |
|---|---|---|
| parts | soft_upper / sole / padded_collar / liner / quilt_panel / toe_cap / padded tongue | S4 / L112-L209, L356-L362 |
| internal joints | 无 | — |
| upstream interface | boot root；右镜像 mount | S4 / L330-L353 |
| downstream interface | padded_collar 外壁供 soft cuff wrap 套接；更高 CUFF_PIVOT(z=0.240) | S4 / L76-L78, L430-L431 |

### Slot B / module low_cut
| emits | 描述 | 来源 |
|---|---|---|
| parts | 削低 shell / sole / liner / heel_panel / toe_bumper / 短 tongue | S5 / L114-L251, L345-L351 |
| internal joints | 无 | — |
| upstream interface | boot root；右镜像 mount | S5 / L320-L344 |
| downstream interface | 低 CUFF_PIVOT(z=0.135) + 短 cuff_band/cuff_lip；tongue 从 cuff band 口穿出（allow_overlap）| S5 / L80-L83, L420-L445 |

### Slot C / module laces
| emits | 描述 | 来源 |
|---|---|---|
| parts | boot visuals：tongue / eyelet_stay_lateral / eyelet_stay_medial / lace_0..4；cuff visuals：strap / strap_buckle | S0 / L347-L365, L417-L428 |
| internal joints | 无（lace rung 为装饰圆柱 visual）| — |
| upstream interface | 挂 boot tongue 上表面（`_lace_centers` 沿 tongue 法向 offset）+ cuff 前面 | S0 / L296-L312 |
| downstream interface | 无下游 | — |

### Slot C / module buckle_ratchet
| emits | 描述 | 来源 |
|---|---|---|
| parts | boot：`instep_strap_{i}` ×M（strap+ladder ribs+cam buckle+lever+anchor）；cuff：`power_strap` + power_strap_buckle | S6 / L326-L394, L430-L433, L498-L510 |
| internal joints | 无（带为宿主 part visual）；cuff power strap 随 cuff_flex 运动 | S6 / L757-L768 |
| upstream interface | instep 带挂 boot instep（`_instep_strap_positions(n)`）；power strap 挂 cuff | S6 / L307-L323 |
| downstream interface | 无 | — |

### Slot C / module velcro_strap
| emits | 描述 | 来源 |
|---|---|---|
| parts | boot：`velcro_strap_{i}`(+hook patch) ×M；cuff：`cuff_strap`(+patch) | S7 / L338-L408, L459-L474 |
| internal joints | 无；cuff strap 随 cuff_flex 运动 | S7 / L739-L741 |
| upstream interface | instep 带挂 boot（`_instep_strap_centers(n)`，FRACTIONS 切片）；cuff 带挂 cuff 前面 | S7 / L319-L336 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| chassis_arrangement | enum | `{inline, quad}` | inline | choice | procedural sampler；inline 权重高（真实主流），quad 较少 | Slot A table |
| boot_form | enum | `{hard_shell, soft_boot, low_cut}` | hard_shell | choice | sampler 选择 | Slot B table |
| closure | enum | `{laces, buckle_ratchet, velcro_strap}` | laces | choice | sampler 选择 | Slot C table |
| wheel_count (N) | int | inline: `[3,5]`；quad: 固定 4 | 4 | conditional | 仅 inline 分支采样；quad 强制 N=4 | S1 L48-L58, S3 L60-L65 |
| instep_strap_count (M) | int | `[2,3]`（仅 buckle/velcro）| 3 | conditional | 仅当 closure∈{buckle,velcro}；laces 不暴露 M | S6 L300, S7 L83 |
| palette_style | enum | 见下 4–6 colorway | classic_gray_red | choice | 每 seed 采一个；驱动 boot/frame/tire/accent 材质组 | S0/S4/S5/S6/S7 材质块 |
| wheelbase_scale | float | [0.92, 1.08] | 1.0 | independent | inline rail 总跨缩放；clamp 后派生 station | S0 L51-L55, S1 L53-L58 |
| wheel_radius_scale | float | derived | 1.0 | equation/inequality | `= f(N, wheelbase)`：N↑ 须缩径；见下不等式；AXLE_Z=WHEEL_RADIUS 随之变 | S2 L49-L54 |
| shell_height_scale | float | [0.95, 1.06] | 1.0 | independent | 靴/shaft 高度缩放；不改 sole 接口 Z | S0 L62-L74 |
| cuff_pivot_z | float | derived | — | equation | `= f(boot_form)`：hard≈0.215 / soft≈0.240 / low≈0.135 | S0 L70, S4 L76, S5 L80 |
| rail_half_span | float | derived | — | equation | `= _wheelframe_half + 0.024`（inline）；保证 boss 站在 rail 内 | S2 L58 |
| (—) | constraint | — | — | inequality | **tire 不互碰**：`2·WHEEL_RADIUS ≤ station_spacing − clearance`，其中 `station_spacing = wheelbase/(N-1)`；违反则缩 wheel_radius_scale 或回缩 N 上界（inline_5 packing 风险，源 S2/排除项）| S2 L48-L58, 排除项 |
| (—) | constraint | — | — | inequality | **轮共面触地**：所有 wheel spin origin z = AXLE_Z = WHEEL_RADIUS，min-z spread ≤ 1.5mm，|min-z| ≤ 4mm | S0 L548-L560 |
| (—) | constraint | — | — | inequality | **cuff_flex 限位**：`-0.6 ≤ lower < 0 < upper ≤ 0.8` rad | S0 L562-L574 |
| (—) | constraint | — | — | inequality | **轮在 rail 间**：inline wheel_y=0 且 tire 横宽 < rail 内距（quad 例外，轮在 truck 外侧）| S0 L595-L601 |

约束求解全部落在 `resolve_config`：先采 independent（wheelbase/shell_height），按 equation 派生（wheel_radius、cuff_pivot_z、rail_half_span、station），再用 tire-不互碰/共面不等式投影回缩（缩 wheel_radius 或拒绝重采），最后按 conditional 解析 N（依 arrangement）与 M（依 closure）。

**palette_style colorways（≥3，目标 4–6，取自 5★ 实际材质集）**：
1. `classic_gray_red` — 灰硬壳 + 红 heel/accent + 白 frame + 半透 urethane 轮（S0 parent 配色）
2. `graphite_speed` — 石墨深灰低帮壳 + 红 accent + 银 frame + 深 toe cap（S5 lowcut）
3. `soft_black_blue` — 黑软织面 + 蓝 accent + 铝 frame + 白绗缝/白鞋带（S4 softboot）
4. `mono_black_buckle` — 黑 strap + 深 buckle 硬件 + 灰壳 + 白 frame（S6 buckle）
5. `velcro_dark_gray` — 深灰魔术贴织带 + hook patch + 灰壳 + 白 frame（S7 velcro）
6. `urethane_neutral` — 浅中性靴 + 钢色硬件 + 半透 urethane 轮强调（通用，跨样本钢/urethane 材质）

## Multiplicity / Copy Logic

**有复制数量逻辑，1 根主轴（wheels）+ 1 根条件副轴（instep straps）。**

### 轴 1：wheel_count（per-skate 轮 multiplicity）
- `count_param`：`wheel_count`（单个整数；模板须从 N 派生 axle stations，**不**沿用 parent 直接迭代 AXLE_XS tuple 的写法）。
- `N_range`：inline 分支产品域 `[3,5]`（真实 inline 轮滑 3–5 轮；<3 或 >5 离开类别）；quad 分支固定 N=4（2 truck × 2）。测试偏小：inline 用 {3,4}，5 稀采（packing 风险）。
- sampling domain（权重）：inline N∈{3:中, 4:高（主流）, 5:低（packing 风险）}；arrangement∈{inline:高, quad:较低}。
- copied object：一个 wheel = TireGeometry tire + WheelGeometry hub + steel axle Cylinder（三 visual 一组）。
- naming：`{prefix}_wheel_{i}`，i=0 为最前；prefix∈{left,right}。
- placement：inline → 沿 frame X 在固定/缩放 wheelbase 上等距 axle stations（`_wheelframe_half - i·spacing`）；quad → 4 truck-corner（front/rear × lateral/medial），wheel_y=±side·offset。
- joint policy：每轮一个 CONTINUOUS spin joint，axis=(0,1,0)，origin=(station_x, wheel_y, AXLE_Z)，统一 `MotionLimits(effort=4, velocity=60)`；每轮独立自转。
- source/gating：arrangement=quad 时 N 强制 4 且布局切到 TRUCK_CORNERS；arrangement=inline 时 N∈[3,5] 且 tire-不互碰不等式可回缩 N 上界。

### 轴 2：instep_strap_count（条件副轴）
- `count_param`：`instep_strap_count`（M）。
- `N_range`：`[2,3]`，仅当 closure∈{buckle_ratchet, velcro_strap}。
- sampling domain：{3:高（实物常见）, 2:中}。
- copied object：buckle → strap+ladder ribs+cam buckle+lever+anchor（`_add_strap_and_buckle` helper）；velcro → flat band+hook patch（`_build_flat_strap_mesh` helper）。
- naming：`instep_strap_{i}`（+ `_buckle_{i}`/`_patch`）。
- placement：沿 tilted tongue 等距（`_instep_strap_positions(n)` / `_instep_strap_centers(n)` 切 FRACTIONS）。
- joint policy：无 joint（带为 boot part visual，随 boot）。cuff power/velcro 带挂 cuff，随 cuff_flex。
- gating：closure=laces 时本轴不存在（laces 用固定 5 lace rung + eyelet stays，不暴露 M）。

## 拓扑多样性审计

总组合数（拓扑）：
- arrangement/N：inline N∈{3,4,5}=3 + quad(N=4)=1 → 4 个底盘拓扑样本
- boot_form：3
- closure：3（laces 不含 M；buckle/velcro 各含 M∈{2,3} → closure×M 拓扑 = 1 + 2 + 2 = 5）
- 顶层拓扑组合 ≈ 4(chassis) × 3(boot) × 5(closure×M) = **60** distinct 拓扑（未计连续 scale）。

理由：仅 chassis 4 × boot 3 × closure 3 = 36，已远超 10；叠加 N 与 M 的复制差异（part/joint count 改变拓扑哈希）后 ≈60，1000-seed sweep 的 slot choice tuple distinct 预计 按 ≥300 report-only 口径观察（连续 scale 不计入拓扑哈希，但 N、M、arrangement、boot/closure module 切换都改变 part/joint 结构）。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic 加权采样依次选 arrangement→N(条件)→boot_form→closure→M(条件)→palette_style，再采连续 scale；compatibility matrix 见下表 gating 拦非法组合；少量 regression override 仅用于已知失败 seed。random sweep：seeds 0–49 初轮、0–999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类有 60 顶层拓扑 + N/M 变体，预计达到建议线；不设门。

Controlled local parameterization（初版模板应含的关键连续 scale）：
- `wheelbase_scale` [0.92,1.08] independent — inline rail 总跨；派生 station 间距。
- `wheel_radius_scale` equation/inequality — `=f(N,wheelbase)`，N↑ 缩径；受 tire-不互碰不等式回缩；改 AXLE_Z 保持触地。
- `shell_height_scale` [0.95,1.06] independent — 靴/shaft 高；不改 sole↔frame 接口 Z。
- `cuff_pivot_z` equation — `=f(boot_form)`（hard/soft/low 三档）。
- `rail_half_span` equation — `=_wheelframe_half+0.024`，保证最外 boss 在 rail 内。
- 所有派生与不等式在 `resolve_config` 求解；不破坏 spin joint origin、cuff pivot、共面触地、tire 间隙、rail-内约束。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序：arrangement→N(cond)→boot→closure→M(cond)→palette→scales；加权（inline/N=4 偏多，quad/N=5 稀）| slot_choices_for_seed matches build choices |
| compatibility matrix | quad↔{soft_boot,low_cut} 标记 untested（见下，初版 gate off 或谨慎放行）；quad 强制 N=4；laces 不含 M；inline_5 受 packing 不等式回缩 | no floating（右 skate isolated 已声明）、collision（tire-tire/穿模）、axis(+Y spin/+Y cuff)、max multiplicity(N≤5, M≤3)、bulky module、optional child |
| controlled local variation | wheelbase/shell_height/wheel_radius scale + clamp/derive | 比例变化不破接口、clearance、joint origin、共面触地、类别 identity |
| regression overrides | none（如出现 inline_5 packing 或 quad×软靴 失败再加 + 理由）| previously failed / reviewer-selected only |
| random sweep | seeds 0–49 初轮，0–999 成熟审计 | contract failures |

兼容矩阵（排除/gating，取自源 map 排除项）：
- **quad_2x2 × {soft_boot, low_cut}**：未测底盘↔靴 mount 组合；quad truck 装在平 sole 下，low_cut/soft 的 sole footprint 可能不同 → 初版 gate off（或仅在 viewer 审核后放行），不进默认 seed domain。
- **inline N=5 packing**：缩轮径以在 wheelbase 内塞 5 轮有 tire-tire 重叠风险；tire-不互碰不等式触发时缩 wheel_radius 或回缩 N 上界（或加长 rail）。
- **segment 退化**：boot side-loft / boolean 在 segments=64 在某些 soft/low 重建上退化（"Profile area must be non-zero"）；soft_boot/low_cut 的壳重建用 segments ≤ 56。
- **closure=laces × M**：laces 不暴露 M（固定 5 lace + eyelet）；M 仅对 buckle/velcro 合法。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A chassis_arrangement | 4 (inline_3/4/5 + quad) | yes | yes | inline 为 N 复制；quad 为独立拓扑 |
| B boot_form | 3 | yes | yes | hard/soft/low |
| C closure | 3 | yes | yes | laces/buckle/velcro |

## Validator
- slot_choices_for_seed 返回已实现 module 名（inline/quad、hard/soft/low、laces/buckle/velcro）
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling
- compatibility matrix / gating 阻止非法组合（quad×软/低 gate off、laces 无 M、inline_5 packing 回缩）
- regression overrides 稀少且有理由（初版 none）
- 不无限轮换小型 curated 表作主 seed domain
- 局部连续 scale 全部 clamp / 派生，不破坏接口、clearance、spin/cuff joint origin、共面触地、N/M 复制
- 跨部件 scale 依赖（wheel_radius=f(N,wheelbase)、cuff_pivot_z=f(boot_form)、rail_half_span 派生、tire 间隙不等式）在 `resolve_config` 求解，不留到 builder 失败
- 关键 InterfaceSpec/MatingContract 点存在：sole↔deck_plate 坐贴、shaft↔cuff collar 同心、axle 捕获、tongue↔closure
- 关键 joint 类型/轴/范围：wheel_spin = CONTINUOUS axis≈(0,1,0)；cuff_flex = REVOLUTE axis≈(0,1,0) 限位 [-0.18,+0.50] 落在 [-0.6,0)∪(0,0.8]
- 复制件遵守命名/布局：`{prefix}_wheel_{i}`、inline 等距 station / quad 4 corner；`instep_strap_{i}` 沿 tongue 等距

## Reject cases
1. wheels 不共面触地（min-z spread > 1.5mm 或 |min-z| > 4mm）——AXLE_Z≠WHEEL_RADIUS 或 N 缩放未同步轮径。
2. inline 高 N 下相邻 tire 互碰（`2R > station_spacing − clearance`）——未触发 packing 回缩。
3. wheel_spin 不是 CONTINUOUS 或轴非 +Y（被误设 REVOLUTE/限位，或轴写成 X/Z）。
4. cuff_flex 不是 REVOLUTE 或限位越界（lower≥0 / upper>0.8 / lower<-0.6），正 q 不前倾过趾。
5. quad 误用 N≠4 或 wheel_y=0（4 轮挤成单列，丢 2×2 横向分离）。
6. closure=laces 仍暴露 M，或 buckle/velcro 的 instep 带未沿 tongue 等距（穿过 shell 或悬空）。
7. boot shaft 与 cuff collar 非同心/无径向 clearance（cuff 实心穿模 shaft，或 collar 漂离），或 pivot_rivet 未嵌入 shaft 壁。
8. soft_boot/low_cut 壳在 segments=64 重建报 "Profile area must be non-zero"（未降到 ≤56），或 frame 未坐贴 sole（deck_plate 与 sole 脱离/穿透）。

## 与相邻类别的边界
- 不该混入：**Ice skates（冰刀鞋）**——冰刀是固定单刃刀片、无滚动轮、无 spin joint；本类核心是绕 +Y 自转的轮 multiplicity。
- 不该混入：**Skateboard / longboard**——滑板是一块板 + 双 quad truck 但**无靴体、无踝 cuff、无闭合系统**；本类必须有 boot + cuff_flex。
- 不该混入：**Roller skis / 单纯轮组**——缺少 boot_form 与 closure slot 即非轮滑鞋。
- 不该混入：**Shoes / sneakers（普通鞋）**——普通鞋无底盘/轮/spin joint，且 cuff 不铰接。

## 模板实现备注（可选）
- closure 的 instep strap helper 跨 buckle/velcro 形态不同（cam-buckle vs flat band），各自保留 module-local helper，暂不强行抽公共 helper。
- multiplicity 两轴（wheel N、instep M）的加权采样 helper 待第二个多轴 multiplicity 模板出现再抽，不提前抽象。
- captured-pin allow_overlap 须按 element scope 声明：inline = (rail_lateral/medial ↔ axle)；quad = ({front/rear}_hanger ↔ axle)；cuff = (shaft ↔ pivot_rivet_lateral/medial) 与 (shaft ↔ collar 同心环)。
- 右 skate 整子树用 `allow_isolated_part`（boot/frame/cuff/all wheels），并 `expect_origin_distance` 两 boot y 距 0.10–0.20。
- low_cut：tongue 从短 cuff band 口穿出须声明 element-scoped allow_overlap（tongue ↔ cuff_band）。
- quad×{soft_boot,low_cut} 初版不进 seed domain（compatibility gate），待人工审核底盘↔软/低 sole mount 后再放行。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C | inline_4 + hard_shell + laces | rec_a-pair-of-inline-…26f6e0cf | L104-L196 / L296-L428 | baseline boot 壳 + 鞋带闭合 + 4 轮 inline frame + cuff/spin joint |
| S1 | A | inline_N | rec_roller_skates_var_inline3 | L48-L71, L378-L421 | N 参数化（WHEELS_PER_SKATE → AXLE_XS 派生）|
| S2 | A | inline_N(packing) | rec_roller_skates_var_inline5 | L48-L58 | N=5 packing：WHEEL_SPACING/缩径/rail 半跨派生 |
| S3 | A | quad_2x2 | rec_roller_skates_var_quad | L55-L101, L221-L268, L414-L472 | 双 truck 底盘 + 2×2 corner 轮循环 |
| S4 | B | soft_boot | rec_roller_skates_var_softboot | L112-L209, L238-L259, L356-L362 | 软高帮 upper + padded collar + 高 cuff pivot |
| S5 | B | low_cut | rec_roller_skates_var_lowcut | L73-L83, L114-L251 | 低帮壳 + 短 cuff band + 低 pivot |
| S6 | C | buckle_ratchet | rec_roller_skates_var_buckle | L300-L394, L430-L433, L498-L510 | instep ratchet 带 ×M + cuff power strap helper |
| S7 | C | velcro_strap | rec_roller_skates_var_velcro | L82-L93, L319-L408, L459-L474 | flat velcro 带 ×M + cuff velcro 带 helper |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待审：(1) quad×{soft_boot,low_cut} 是否在初版即放行还是 gate off；(2) instep_strap_count N_range 是否扩到 [2,4]；(3) inline N=5 是否允许通过加长 wheelbase（而非仅缩径）满足 packing。SPEC_ONLY，未写模板代码。|
