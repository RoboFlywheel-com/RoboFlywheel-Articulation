# Pen — Modular Spec

> 来源小类：`picture/Stationary/Pen`（articraft_data 上游小类样本池；对象身份为 handheld marker/highlighter pen，slug = `pen`）。
> 上游 source map：建议回填 `picture_expansion/template_source_maps/Stationary__Pen.md`（当前尚未建立；本 spec 已逐一内联全部 record_id + module 来源，source map 缺失不影响来源完整性）。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 个 parent + 9 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 10 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（FORK_VARIANTS §7：收敛即入池——10 个样本均 compile rc=0、均含 ≥1 非 fixed joint、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_build_barrel` / `_build_nib` / `_build_cap` / `_build_carrier_body` / `_build_flip_cap` / `_build_clip` / `_build_grip_rib` / `barrel_to_cap` / `barrel_to_carrier` / `body_to_collar` / `body_to_nib` / `cap_to_clip` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pen` |
| template path | `agent/templates/Stationary_Pen.py` |
| test path (optional) | `tests/agent/test_pen_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| __modular__ | `True` |
| pattern | `mixed`（固定 root barrel + parallel/serial children 槽位：actuation 主机构 + tip_form + pocket_clip，**外加** grip 的 ribbed-band 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 parent + 9 单轴 fork 变体；均 converged，compile rc=0、均有 ≥1 非 fixed joint、workbench-only）|
| read_count | 10（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（fork 池 1 parent + 9 fork，无抽样）|
| source_index_policy | only adopted module sources are indexed below（10 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_build-...-pen-_20260609_200037_041760_bd7a9b72`）：STABILO BOSS 矩形 barrel highlighter，lime 圆角矩形 body + 前 collar，黑色 chisel 楔形 nib（barrel visual），分离黑 cap 沿 +X **PRISMATIC pull-off**，flat pocket clip（cap 上 visual）。**全批基线**：barrel/collar/cap/nib/felt 几何 + 拉帽机构。
- **S1 bullet_tip**（`rec_pen_var_bullet_tip`）：把 chisel 楔形 nib 换成 **revolved bullet cone**（cylinder base + cone loft + sphere cap）。**tip_form 槽位来源**。
- **S2 twin_tip**（`rec_pen_var_twin_tip`）：双头 marker，两端各 chisel nib + 各自 pull-off cap，`for i in range(2)` 发射两 cap，镜像 ±X，各自 PRISMATIC。**actuation 多重性来源（twin pull-off）**。
- **S3 twist_extend**（`rec_pen_var_twist_extend`）：去掉分离 cap，分前 body + 旋转后 collar（REVOLUTE 绕 +X），nib carrier 沿 +X PRISMATIC 推出（双 joint：collar 旋 + nib 滑）。**actuation 槽位来源（twist-extend）**。
- **S4 click_retract**（`rec_pen_var_click_retract`）：去 cap，nib carrier 沿 +X **PRISMATIC** 缩入/伸出 barrel bore，rear click 按钮（barrel visual）。**actuation 槽位来源（click-retract）**。
- **S5 twist_cap**（`rec_pen_var_twist_cap`）：cap 改螺纹旋帽，**REVOLUTE 绕 +X** 拧开（threaded boss + 内螺纹 relief）。**actuation 槽位来源（twist-cap）**。
- **S6 round_barrel**（`rec_pen_var_round_barrel`）：barrel/collar/cap 全改 **圆柱 lathe**（`circle`+`extrude` revolve），slim round marker。**barrel_profile 槽位来源**。
- **S7 flip_cap**（`rec_pen_var_flip_cap`）：tethered hinged flip cap，**REVOLUTE 横轴（−Y）** 在 collar 侧 hinge knuckle 翻开。**actuation 槽位来源（flip-cap）**。
- **S8 sprung_clip**（`rec_pen_var_sprung_clip`）：flat clip 换成 **独立 spring-loaded clip part**，REVOLUTE 横轴（+Y）hinged 在 cap top，cap 仍 pull-off PRISMATIC（barrel→cap→clip 串链）。**pocket_clip 槽位来源（sprung）**。
- **S9 grip_section**（`rec_pen_var_grip_section`）：collar 后加 rubber **grip 凸肋带**，`for i in range(GRIP_RIB_COUNT)` 等距发射相同 rib visual。**grip 多重性轴来源**。

冗余说明：S0/S1/S2/S4/S5/S7/S8/S9 的 barrel 均为圆角矩形（同一 `rounded_rect` 基线，提供共享壳 + 拉帽 helper）；只有 S6 提供 round 形态。每个 fork 各自只改 1 根结构轴，diff 干净，每个轴恰好 1 个收敛候选——actuation 轴例外，独得 5 个不同机构候选（pull-off / click / twist-extend / twist-cap / flip）。

## 核心身份

手持记号笔 / 荧光笔（handheld marker / highlighter pen）：一只细长杆状壳体（barrel，长 ~0.14 m，长轴沿 +X，横截面在 Y-Z 面），前端是写字 tip（chisel 楔形或 bullet 锥形 nib + 暴露的 ink-soaked felt 尖），笔身上有 pocket clip（夹口袋），**主用户机构 = tip 的开合/伸缩**：分离 pull-off cap 沿 +X PRISMATIC 拔出、click 笔 nib carrier 沿 +X PRISMATIC 推出、twist 笔后段 REVOLUTE 旋出 nib、twist/screw cap REVOLUTE 拧开、或 flip cap 横轴 REVOLUTE 翻开。barrel 为圆角矩形或圆柱细杆，可选 rubber grip 肋带、可选 sprung pivot clip。

默认成熟域：一只细长 barrel（矩形或圆柱），前端 chisel 或 bullet nib，五选一的 tip-actuation 机构（pull-off cap / click-retract / twist-extend / twist-cap / flip-cap），可选 grip 肋带（N 根等距相同 rib），clip 为 fixed-flat / sprung-pivot / none。活动语义恒为"露出/收回写字 tip"，叠加可选的 sprung clip REVOLUTE。felt tip + click button + fixed clip + grip rib 恒为固定装饰（inline barrel visual，不做独立 FIXED part）。

不该混入：铅笔 pencil（木杆 + 石墨，无 cap/纤维 tip、无 felt，常六棱）、自动铅笔 mechanical pencil（细芯推进、橡皮帽，机构身份不同）、记号笔以外的 stylus / 触控笔（无 ink tip）、马克笔套装 / 笔筒（多件容器，出"单只笔"语义）。Stationary 大类内区别于 Clip / Folder / Calculator 等无细长写字杆身份的文具。

## 槽位 + 候选模块表

> **建模注记（重要）**：pen 是 **root barrel 杆身 + 一组 parallel/serial children**——actuation 机构（cap / carrier / collar，挂 barrel 的真实端面/座面）、tip（chisel/bullet，作 barrel 或 carrier 的 visual）、pocket_clip（fixed=barrel/cap visual，sprung=独立 part 挂 cap）；felt/click button/grip rib 恒为 visual。actuation 是核心轴：pull-off/click/twist-extend 用 **PRISMATIC** 直滑，twist-cap/flip-cap 用 **REVOLUTE**（绕 +X 拧 或 横轴翻）。pen 尺度极小（barrel ~0.14 m，tip ~0.02 m），joint origin 必须精确落在真实硬件接触面（座面/铰链/bore 口），≤0.015 m baseline。

### Slot A：barrel_profile（杆身 + cap 横截面族，成对）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_rect（基线） | rec_..._bd7a9b72（S0；多数 fork 同形） | `_rounded_rect_prism` L71-80 + `_build_barrel` L83-93 + `_build_cap` L128-171 | eligible if compatible | 圆角矩形 prism（`rect`+`extrude`+`fillet("|X")`），矩形 collar，矩形中空 cap |
| round_cylindrical | rec_..._round_barrel（S6） | `_cylinder` L68-74 + `_build_barrel` L77-84 + `_build_cap`（圆 bore）L125-160 | eligible if compatible | 圆柱 prism（`circle`+`extrude` revolve），圆 collar，圆中空 cap（slim round marker）|

> 降级理由（2 candidate）：本小类 fork 池 barrel 截面只有 parent 矩形 + S6 圆柱两个真实收敛形态；现实记号笔截面词汇表本身窄（矩形 highlighter / 圆 marker 为主）。审核如需扩容应回 fork 池补造（如六棱/三角 grip 杆），不在模板侧虚构。

### Slot B：tip_form（写字 nib 几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| chisel_wedge（基线） | rec_..._bd7a9b72（S0） | `_build_nib`（holder+wedge loft）L96-111 + `_build_felt_tip` L114-125 | eligible if compatible | 直 holder + 楔形 loft 收到薄 chisel 边（`rect→rect` loft），扁平宽刃 felt |
| bullet_cone | rec_..._bullet_tip（S1） | `_build_nib`（base+cone+sphere）L97-122 + `_build_felt_tip` L126-138 | eligible if compatible | 圆柱 base + 锥 loft + 球冠尖（revolved bullet），中心线圆 felt fiber |

> 降级理由（2 candidate）：fork 池 tip 只有 chisel（parent + 多数 fork 继承）与 bullet（S1）两个真实形态。审核如需扩容回 fork 池补造（如 brush tip / fine-liner needle）。

### Slot C：actuation（tip 开合/伸缩主机构；互斥）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pull_off_cap（基线） | rec_..._bd7a9b72（S0） | `_build_cap` L128-171 + PRISMATIC `barrel_to_cap` L224-234 | eligible if compatible | 分离中空 cap，**PRISMATIC 绕 +X** 拔出（q=0 seated 盖 nib，q=upper 拔离）；nib 是 barrel visual |
| twin_pull_off_cap | rec_..._twin_tip（S2） | `for i in range(2)` cap L224-263 + 两 PRISMATIC `barrel_to_cap_{i}` L242-258 | eligible if compatible | 双头双 cap，`for i in range(2)` 发射，镜像 ±X，各自 PRISMATIC 向外拔（**多重性=2 个相同 cap**）；两端各 nib visual |
| click_retract | rec_..._click_retract（S4） | `_build_carrier_body` L151-159 + PRISMATIC `barrel_to_carrier` L248-258 | eligible if compatible | 无 cap；nib carrier **PRISMATIC 绕 +X** 缩入/伸出 barrel bore（q=0 缩回藏 nose，q=upper 伸出写字），rear click 按钮 barrel visual |
| twist_extend | rec_..._twist_extend（S3） | 旋 collar REVOLUTE `body_to_collar` L351-363 + nib PRISMATIC `body_to_nib` L366-378 + knurl ribs loop L325-331 | eligible if compatible | 无 cap；后 collar **REVOLUTE 绕 +X**（knurl band）+ nib carrier PRISMATIC 推出（双 joint，helical relief 语义）|
| twist_cap | rec_..._twist_cap（S5） | `_build_cap`（threaded）+ REVOLUTE `barrel_to_cap` L296-305 | eligible if compatible | 分离螺纹 cap，**REVOLUTE 绕 +X** 拧开（threaded boss + 内螺纹 relief，q=0 seated 盖 nib，q=upper 拧离 ~2.5 圈）|
| flip_cap | rec_..._flip_cap（S7） | `_build_flip_cap` + REVOLUTE 横轴 `barrel_to_cap` L261-272 | eligible if compatible | tethered hinged cap，**REVOLUTE 横轴（−Y）** 在 collar 侧 hinge knuckle 翻开（q=0 闭合盖 nib，q=upper 翻起露 nib，铰链不脱离）|

> 这是模板主多样性轴：5 种结构不同的机构（PRISMATIC×3 含 twin、REVOLUTE×3 不同轴/座），part tree 与 joint 拓扑各异。互斥：同一支笔只能选一种 tip-actuation。

### Slot D：pocket_clip（夹身机构；optional/variant）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_flat（基线） | rec_..._bd7a9b72（S0） | clip+boss visual in `_build_cap` L147-170（cap 上）/ `_build_pocket_clip` L162-183（barrel 上，click 形态）| eligible if compatible | 不动 flat 夹片，**inline visual**（cap 有 cap 时挂 cap，否则挂 barrel；无活动）|
| sprung_pivot | rec_..._sprung_clip（S8） | `_build_clip` + REVOLUTE 横轴 `cap_to_clip` L298-309 | eligible if compatible | 独立 spring clip part，**REVOLUTE 横轴（+Y）** hinged 在 cap top（q=0 贴合，q=upper 抬起 free tail）；仅 cap 类 actuation 可用 |
| none | rec_..._click_retract（S4，无 clip 也合法的 click 形态变体）| （无 clip visual/part）| eligible if compatible | 无夹片（极简笔；baseline 合法取值，非占位）|

> 降级理由（含 none 共 3 candidate，达 ≥3 目标）：sprung 是真实活动机构，fixed/none 是合法静态/缺省。sprung 依赖 cap 存在（盖类 actuation），gating 见 §9。

## 槽位图（slot graph）

```
pattern: mixed（root barrel + parallel/serial children + grip multiplicity）

                         barrel (root, barrel_profile ∈ {rounded_rect, round_cylindrical})
                          │   坐标：杆身沿 +X，前端 +X、后端 −X；横截面 Y-Z；front collar 端面 = 各 child 锚点
        ┌─────────────────┼──────────────────┬──────────────────┬───────────────────┐
        │                 │                  │                  │                   │
   tip(Slot B)       actuation(Slot C)   pocket_clip(Slot D)  grip_ribs[N]        felt/click button
   chisel/bullet     互斥五选一            fixed/sprung/none   (multiplicity)      (恒 visual)
        │                 │                  │                  │                   │
   barrel visual     cap/carrier/collar  fixed: inline       grip_rib_{i}:        inline visual
   (pull-off/twist/  child 挂 barrel      visual @ cap/barrel  FIXED 语义 等距      @ tip / rear
    flip 类)；或      端面/座面/bore       sprung: REVOLUTE     band（不建 part）
   carrier visual    PRISMATIC 或          +Y @ cap top
   (click/twist-     REVOLUTE             (serial: barrel→cap→clip)
    extend 类)
```

接口点位（每条 barrel→child 连接）：
- **barrel → cap（pull_off / twin / twist_cap / flip）**：mating = front collar 座面。pull-off/twin：`origin=(BARREL_LEN−CAP_SEAT_OVERLAP, 0, 0)`，PRISMATIC axis `(±1,0,0)`，range `[0, full_clear]`；twist_cap：`origin=(BARREL_LEN+COLLAR_LEN,0,0)`，REVOLUTE axis `(1,0,0)`，range `[0, ~2.5 圈]`；flip：`origin=(BARREL_LEN, 0, COLLAR_H/2)` hinge knuckle，REVOLUTE axis `(0,−1,0)`，range `[0, 2.4]`。MatingContract = cap mouth 套 collar（capture fit，element-scoped allow_overlap）。
- **barrel → carrier（click / twist_extend）**：mating = barrel bore 口。`origin=(RETRACTED_X,0,0)`，PRISMATIC axis `(1,0,0)`，range `[0, EXTENSION]`；twist_extend 另加 collar REVOLUTE `origin=(0,0,0)` axis `(1,0,0)`。carrier stem 嵌 bore（nested fit，allow_overlap）。
- **cap → clip（sprung_pivot）**：mating = cap top hinge line（`origin=(CAP_LEN−ε, 0, CAP_OUTER_H/2+ε)` cap-local），REVOLUTE axis `(0,1,0)`，range `[0, 0.55]`。串链 barrel→cap→clip。
- **互斥/可选/派生**：Slot C 五选一互斥；Slot D sprung 仅当 actuation 产生独立 cap part（pull_off/twin/twist_cap/flip）时可用，click/twist_extend 无 cap ⇒ clip 退化为 barrel-fixed 或 none；tip primitive 由 Slot A 派生横截面（round⇒圆 holder/bullet，rect⇒矩形 holder/chisel 兼容）。

## 每槽位 Module Emits / Interfaces

### Slot A / module rounded_rect
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel`（root，`barrel_body` visual：圆角矩形 prism + collar union）| S0 / `_build_barrel` L83-93 |
| internal joints | 无（root）| — |
| downstream interface | front collar 座面 + bore 口（供 actuation 锚定）；cap top（供 sprung clip）| S0 / L83-93 |

### Slot A / module round_cylindrical
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel`（圆柱 prism + 圆 collar union，revolved）| S6 / `_build_barrel` L77-84 |
| downstream interface | 同上但圆截面 collar 座 + 圆 bore | S6 / L77-84 |

### Slot B / module chisel_wedge
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`nib` + `felt_tip` 作 barrel/carrier visual（楔形 loft + 扁刃 felt）| S0 / `_build_nib` L96-111 |
| upstream interface | 贴 collar 前端面 / carrier 前端 | S0 / L96-125 |

### Slot B / module bullet_cone
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`nib`（base+cone+sphere）+ 圆 `felt_tip` visual | S1 / `_build_nib` L97-122 |
| upstream interface | 同 chisel，中心线圆锥 | S1 / L97-138 |

### Slot C / module pull_off_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap`（中空壳）| S0 / `_build_cap` L128-171 |
| internal joints | `barrel_to_cap` PRISMATIC axis (1,0,0) range [0,full_clear] | S0 / L224-234 |
| upstream interface | front collar 座面（cap mouth 套入，capture fit）| S0 / L219-229 |

### Slot C / module twin_pull_off_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap_0` / `cap_1`（`for i in range(2)`，镜像）| S2 / L224-238 |
| internal joints | `barrel_to_cap_{i}` PRISMATIC axis (±1,0,0) × 2 | S2 / L242-258 |
| upstream interface | 两端 collar 座面 | S2 / L240-245 |

### Slot C / module click_retract
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nib_carrier`（carrier 圆柱 + nib + felt）| S4 / `_build_carrier_body` L151-159 |
| internal joints | `barrel_to_carrier` PRISMATIC axis (1,0,0) range [0,EXTENSION] | S4 / L248-258 |
| upstream interface | barrel bore 口（nested fit）；rear click button = barrel visual | S4 / L186-193 |

### Slot C / module twist_extend
| emits | 描述 | 来源 |
|---|---|---|
| parts | `twist_collar`（knurl band + ribs loop）、`nib_carrier`（stem+nib+felt）| S3 / collar L311-331、carrier L333-345 |
| internal joints | `body_to_collar` REVOLUTE (1,0,0) [0,TWIST_UPPER] + `body_to_nib` PRISMATIC (1,0,0) [0,NIB_TRAVEL] | S3 / L351-378 |
| upstream interface | 后段 seam 面（collar 旋）+ bore（nib 滑）| S3 / L348-378 |

### Slot C / module twist_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap`（螺纹中空壳）| S5 / `_build_cap`(threaded) |
| internal joints | `barrel_to_cap` REVOLUTE (1,0,0) [0,~2.5 圈] | S5 / L296-305 |
| upstream interface | collar 螺纹 boss 座（cap 内螺纹啮合）| S5 / L290-302 |

### Slot C / module flip_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap`（hinge knuckle 中空壳）| S7 / `_build_flip_cap` |
| internal joints | `barrel_to_cap` REVOLUTE (0,−1,0) [0,2.4] | S7 / L261-272 |
| upstream interface | collar 侧 hinge knuckle（横轴铰链，tethered）| S7 / L259-267 |

### Slot D / module fixed_flat
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`pocket_clip` 作 cap（或 barrel）visual | S0 / clip in `_build_cap` L147-170 |
| upstream interface | cap top / barrel top（inline，无活动）| S0 / L147-170 |

### Slot D / module sprung_pivot
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip`（独立 spring 夹片）| S8 / `_build_clip` |
| internal joints | `cap_to_clip` REVOLUTE (0,1,0) [0,0.55] | S8 / L298-309 |
| upstream interface | cap top hinge line（contoured tail，仅 cap 类 actuation）| S8 / L292-304 |

### grip multiplicity / module grip_rib_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`grip_rib_{i}` 作 barrel visual × N（等距凸肋）| S9 循环 L224-234 |
| internal joints | 无（FIXED 语义凸肋，inline barrel visual）| S9 / L224-234 |
| upstream interface | collar 后 grip 带（barrel 表面，等距 pitch）| S9 / L222-234 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| barrel_profile | enum | {rounded_rect, round_cylindrical} | rounded_rect | choice | deterministic procedural sampler 选择 | Slot A 表 |
| tip_form | enum | {chisel_wedge, bullet_cone} | chisel_wedge | choice | sampler 选择 | Slot B 表 |
| actuation | enum | {pull_off_cap, twin_pull_off_cap, click_retract, twist_extend, twist_cap, flip_cap} | pull_off_cap | choice | sampler 选择（互斥）| Slot C 表 |
| pocket_clip | enum | {fixed_flat, sprung_pivot, none} | fixed_flat | conditional | sprung 仅当 actuation 产生独立 cap part 时合法，否则降级 fixed/none | Slot D 表 |
| has_cap（derived） | bool | derived | — | conditional | `= actuation in {pull_off,twin,twist_cap,flip}` | Slot C 派生 |
| n_grip_ribs | int | [0, 12] | 0 | independent | 加权采样（0 偏多）后 clamp；0=无 grip | §8 / S9 `GRIP_RIB_COUNT` |
| barrel_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BARREL_LEN，clamp 保细长（length≫宽）| S0 L32 |
| barrel_girth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放截面 W/H 或 R，clamp 保 tip/cap 仍能套合 | S0 L33-34 |
| cap_travel_scale | float | [0.95, 1.15] | 1.0 | conditional | 仅 cap 类缩放 full_clear；clamp 使拔出后仍露 nib | S0 L222 |
| nib_len_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 nib holder+wedge/cone 长，clamp 使 seated cap 仍盖住 | S0 L44-47 |
| grip_band_scale | float | [0.85, 1.10] | 1.0 | conditional | n_grip_ribs>0 时缩放 grip 带长度/pitch；clamp 使带落在 collar 后 barrel 段内 | S9 L223 |
| (—) | constraint | — | — | inequality | seated cap 内腔 ≥ nib 截面包络（`cap_bore ≥ nib_section + clear`）；违反则放大 cap 或回缩 nib | 接口 / capture fit |
| (—) | constraint | — | — | inequality | grip 带 X 包络 ≤ collar 后可用 barrel 段（`n·pitch·grip_band_scale ≤ usable_len`）；越界回缩 pitch | S9 footprint |

连续 scale 默认独立采样 → 派生 has_cap（按 actuation）→ inequality 把 cap-nib 套合与 grip 带包络投影回可行域 → conditional 范围（cap_travel/grip_band/pocket_clip 依赖上游）在采样前解析。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

grip 肋带是唯一模板级多重性来源（twin-tip 的双 cap 折入 actuation 的 `twin_pull_off_cap` module，固定 N=2，不单列）：

- `count_param`: **`n_grip_ribs`**（collar 后等距 rubber 凸肋数）
- `N_range`: `n_grip_ribs ∈ [0, 12]`（产品域；0=无 grip 光杆、6-10=典型 grip 带）。已覆盖样本：S9 = 8 根等距 rib（`for i in range(GRIP_RIB_COUNT)` 循环）
- sampling domain（权重档）：0（无 grip）高频，中等 N（6-10）次之，大 N（>10）稀有长尾
- copied object: 单只 rib visual `grip_rib_{i}`（barrel visual，非 part）；几何由共享 helper `_build_grip_rib` 复用（相同凸肋环）
- naming: `grip_rib_{i}`，`for i in range(n_grip_ribs)`（S9 已用此结构，直接作 module 源码）
- placement: collar 后 grip 带内等距 `rib_x = GRIP_ZONE_START + i·pitch`，pitch = grip 带长 / n
- joint policy: 无 joint（FIXED 语义不动凸肋，inline barrel visual——遵循"不动装饰不建 FIXED part"）
- source/gating: 循环范式 S9 L224-234；n=0 时跳过整段；grip 带须落在 collar 后 barrel 段内（§7 inequality）

> 注：`twin_pull_off_cap`（双 cap N=2）是 actuation 槽内固定多重性 module（`for i in range(2)`），不暴露为可变 count 轴——pen 不存在"任意 N 个 cap"的产品域，故按 module 而非 multiplicity 轴声明（与直升机叶数式可变轴不同）。

## 拓扑多样性审计

总组合数（离散槽）：barrel_profile(2) × tip_form(2) × actuation(6) × pocket_clip(≤3) = **最多 72**（受 gating：无 cap 的 click/twist_extend ⇒ pocket_clip∈{fixed,none}，sprung 仅 4 个 cap 类 actuation 可用，仍 >40 合法组合）。
叠加 multiplicity：n_grip_ribs(0..12, ~5 个高频档) × grip on/off → 进一步乘子。
→ 离散槽即 **40+ distinct 拓扑**（远超 ≥10 门槛），含 grip 轴上千。

理由：actuation 单轴即 6 个 distinct，乘 barrel_profile(2)×tip_form(2) 已 24，再叠 clip/grip 充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——先加权选 barrel_profile/tip_form/actuation，再按 actuation 派生 has_cap 并 gating pocket_clip（无 cap⇒sprung 降 fixed/none），加权采 n_grip_ribs（0 偏多），采连续 scale，经 `resolve_config` inequality 把 cap-nib 套合与 grip 带包络投影回可行域。`seed=0` 不特殊。无需 regression overrides（若 sweep 暴露特定 seed 失败再稀疏加显式 override 并注明）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）（actuation×profile×tip×clip×grip 乘积上界可达；若实测低于 300 多因 grip 档碰撞，可调宽 n_grip_ribs 权重）。
Controlled local parameterization：初版即含 `barrel_len_scale` / `barrel_girth_scale` / `cap_travel_scale` / `nib_len_scale` / `grip_band_scale`（§7），全部 clamp/派生，受 cap-nib 套合、grip 带包络、joint origin 约束，不改变拓扑、actuation 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：barrel_profile→tip_form→actuation→(派生 has_cap)→pocket_clip→n_grip_ribs→scales；加权（rect/chisel/pull-off 偏多，无 grip 偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | sprung_pivot 仅 cap 类 actuation；click/twist_extend⇒pocket_clip∈{fixed_on_barrel,none}；round⇒圆 holder/bullet；cap-nib 套合 clamp；grip 带落 collar 后段 | 无穿模/悬空 nib、cap 拔出露 nib、carrier 缩回不出 nose、clip 抬起、grip 等距贴身 |
| controlled local variation | barrel_len/girth/cap_travel/nib_len/grip_band scale + clamp | 比例变化不破坏 cap 套合、bore 嵌合、grip 包络、joint origin、类别身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 InterfaceSpec/MatingContract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A barrel_profile | 2 | yes | no | 矩形+圆柱两个真实形态；扩容须回 fork 池补造 |
| B tip_form | 2 | yes | no | chisel/bullet 两个真实形态 |
| C actuation | 6 | yes | yes | 主拓扑轴，5 机构 + twin 多重性 module |
| D pocket_clip | 3 | yes | yes | fixed/sprung/none，sprung 为活动 REVOLUTE |
| (mult) grip | n_grip_ribs[0-12] | — | — | 多重性轴，提供拓扑乘子 |

## Validator

- slot_choices_for_seed returns implemented module names（barrel_profile / tip_form / actuation / pocket_clip + n_grip_ribs）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：sprung_pivot 仅 cap 类 actuation；click/twist_extend 无 cap⇒clip∈{fixed_on_barrel,none}；round⇒圆 nib holder
- optional regression overrides 初版为空（如加须稀疏 + 注明）
- controlled local scale params 全部 clamp，且不破坏 cap-nib 套合 / bore 嵌合 / grip 包络 / joint origin / 类别身份
- cross-part scale 依赖（cap 内腔 vs nib 截面、grip 带 vs barrel 段）在 `resolve_config` 内 inequality/conditional 求解，不留到 builder 失败
- critical InterfaceSpec / MatingContract 存在：cap-collar 套合 capture、carrier-bore 嵌合、collar seam 接触、clip-cap hinge 铰链
- key joints：pull_off/twin/click/twist_extend(nib) PRISMATIC axis (±1,0,0)；twist_cap REVOLUTE +X；flip_cap REVOLUTE −Y；twist_extend(collar) REVOLUTE +X；sprung clip REVOLUTE +Y
- copied objects 遵循 `grip_rib_{i}` / `cap_{i}` 命名 + 等距/镜像 placement + 统一 joint policy
- felt tip / click button / fixed clip / grip rib 恒为 barrel/carrier visual（不建 FIXED 装饰 part）

## Reject cases

- 把 felt tip / click button / fixed clip / grip rib 做成 FIXED-joint 独立 part（违反"不动装饰内联 visual"）。
- nib 悬浮或穿出 barrel：未坐落在 collar 前端面 / carrier 前端的真实接触。
- seated cap 不盖住 nib（套合失败）或拔出后 cap 仍盖 nib（travel 不足）。
- click/twist_extend carrier 缩回时 nib 仍露出 nose（retract 失败），或伸出时未过 nose 口。
- round barrel 仍用矩形 cap / 矩形 nib holder（横截面未随 barrel_profile 派生）。
- sprung_pivot clip 配 click/twist_extend（无 cap 可挂）而未 gating 降级。
- flip_cap 翻开轴方向错误（绕 +X 而非横轴），或 twist_cap 用 PRISMATIC 冒充螺纹。
- 用连续 enum/尺寸冒充拓扑：只改 barrel 长/色不换 actuation/profile/tip/clip/grip 数就当新拓扑。
- grip 用手写命名的 2-3 根 rib 代替 `for i in range(N)` 循环（多重性退化）；或 grip 带溢出 barrel 段。
- config_from_seed 采样到未实现组合（如 sprung + click，或 round + 矩形 cap）。

## 与相邻类别的边界

- 不该混入：铅笔 pencil（木杆/石墨芯，无 cap/felt 纤维 tip，常六棱；pen 身份 = 写字 tip + 开合机构 + clip）。
- 不该混入：自动铅笔 mechanical pencil（细芯推进 + 橡皮帽，机构身份不同）。
- 不该混入：触控笔 stylus（无 ink/felt tip，无开合机构）。
- 不该混入：马克笔套装 / 笔筒 / 收纳盒（多件容器，出"单只笔"语义）。
- Stationary 大类内：区别于 Clip / Folder / Calculator / Scissors 等无细长写字杆身份的文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 模板与 spec 同批产出（批量授权，不停审）。模板已实现 `agent/templates/Stationary_Pen.py`（注册于 `cli/template.py` TEMPLATE_REGISTRY），`uv run articraft template sweep-pipeline pen` verdict=pass。降级点：barrel_profile / tip_form 各 2 candidate（单 parent fork 池形态词汇窄）；actuation 独得 6 candidate 抵消，diversity 充裕。待人工确认 ① A/B 槽 2 candidate 是否接受还是要求回 fork 池补造；② sprung_pivot 仅 cap 类的 gating 方案；③ n_grip_ribs N_range/权重档。|

## 模板实现备注（可选）

- 共享 helper：`_barrel_section`（按 barrel_profile 分矩形/圆 prism + collar）、`_build_nib`（按 tip_form 分 chisel loft / bullet cone）、`_build_cap`（按 barrel_profile 分矩形/圆中空壳）、`_build_grip_rib`（等距凸肋环）。
- InterfaceSpec/MatingContract 注意点：cap 类 actuation 的 cap mouth 套 collar 是 capture fit ⇒ element-scoped `allow_overlap(cap, barrel, ...)`；click/twist_extend 的 carrier stem 嵌 barrel bore ⇒ nested fit allow_overlap；sprung clip 串在 cap 上（barrel→cap→clip）。pen 尺度小，所有 joint origin 必须精确落真实硬件面（≤0.015 m baseline）。
- 派生与门控集中在 `resolve_config`：has_cap、pocket_clip gating（依赖 actuation）、cap-nib 套合投影、grip 带包络、round 派生圆 nib holder。
- 模板实现前先从近邻模板深读 root chassis + parallel/serial children + 多重性 visual 阵列（calculator 的 keypad multiplicity + parallel children、shopping_bucket 的 telescoping PRISMATIC + 翻盖 REVOLUTE + caddy 串链），按运动拓扑相近选。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/D | rounded_rect / chisel / pull_off_cap / fixed_flat | rec_..._bd7a9b72 | `_build_barrel` L83-93、`_build_nib` L96-111、`_build_cap` L128-171、PRISMATIC `barrel_to_cap` L224-234、clip L147-170 | 矩形壳 + chisel + 拉帽 + flat clip 基线 |
| S1 | B | bullet_cone | rec_pen_var_bullet_tip | `_build_nib`(base+cone+sphere) L97-122 | bullet 锥 tip |
| S2 | C | twin_pull_off_cap | rec_pen_var_twin_tip | `for i in range(2)` cap L224-263、两 PRISMATIC L242-258 | 双头双 cap 多重性 module |
| S3 | C | twist_extend | rec_pen_var_twist_extend | collar REVOLUTE L351-363 + nib PRISMATIC L366-378 + knurl ribs L325-331 | 旋出机构（双 joint）|
| S4 | C/D | click_retract / none-clip | rec_pen_var_click_retract | `_build_carrier_body` L151-159、PRISMATIC `barrel_to_carrier` L248-258、click button L186-193 | click 缩回 carrier + 无 cap 形态 |
| S5 | C | twist_cap | rec_pen_var_twist_cap | REVOLUTE `barrel_to_cap` L296-305、threaded boss | 螺纹旋帽 |
| S6 | A | round_cylindrical | rec_pen_var_round_barrel | `_cylinder` L68-74、圆 barrel/cap L77-160 | 圆柱杆身 + 圆 cap |
| S7 | C | flip_cap | rec_pen_var_flip_cap | REVOLUTE 横轴 `barrel_to_cap` L261-272、hinge knuckle | tethered 翻盖 |
| S8 | D | sprung_pivot | rec_pen_var_sprung_clip | REVOLUTE `cap_to_clip` L298-309、`_build_clip` | 独立弹簧夹 part |
| S9 | mult | grip_rib | rec_pen_var_grip_section | `for i in range(GRIP_RIB_COUNT)` L224-234、`_build_grip_rib` L93-105 | 等距 grip 凸肋多重性 |
</content>
</invoke>
