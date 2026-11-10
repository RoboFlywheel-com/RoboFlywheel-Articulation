# Bag_Suitcase / Treasure chest — Modular Spec

> 来源小类：`picture/Bag_Suitcase/Treasure chest/001.png`（articraft_data 上游中世纪木+铁箍宝箱小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Bag_Suitcase__Treasure_chest.md`。
> **"Treasure chest" 在此 = 圆顶/曲面盖 + 板条木箱体 + 铁箍带的中世纪宝箱**（curved/domed-lid banded wooden chest），**不是**平板旅行箱（Suitcase）、也不是矩形平盖储物箱（Box）。盖必须能保住曲面身份（domed 用 lathe/`_half_disk_profile` 圆弧、gabled 用三角脊），不能降级成纯 Box 平盖。
>
> **同步状态**：本 spec 引用的 5 个 5 星样本（1 个 parent + 4 个 fork 槽位变体）已同步进本仓库 `data/records/`（`category_slug=bag_suitcase`）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对全文）。引用以 part / joint / helper **名字**为准（`_half_disk_profile` / `_barrel_band` / `_gabled_profile` / `_gabled_panel` / `_corner_bracket_mesh` / `_u_bar` / `chest_body` / `chest_lid` / `lock_hasp` / `padlock_body` / `padlock_shackle` / `lid_hinge` / `hasp_hinge` / `shackle_hinge`），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `treasure_chest` |
| template path | `agent/templates/Bag_Suitcase_Treasure_chest.py` |
| test path (optional) | `tests/agent/test_treasure_chest_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: lid_profile + lock_mechanism + banding，**外加** `band_count` 箍带多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5（1 parent `…_6febc2df` + 4 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only、单轴 diff、绑定门禁通过）|
| read_count | 5（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category（按显式给定的 4 个 var + 1 parent 清单，不用 category 查询）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 5/5 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **parent（基线）** `…_6febc2df`：`chest_body`（root，floor + 4 wall + 4 `corner_post_{i}` + 2 `body_band` + `lock_keeper`）+ `chest_lid`（domed barrel：`_barrel_band` lathe 圆顶 `lid_dome` + 5 条 `lid_strap_{i}` + `hasp_mount`）+ `lock_hasp`。**2 个 REVOLUTE**：`lid_hinge`（body→lid，axis=(-1,0,0)，origin=(0,R,HB)）+ `hasp_hinge`（lid→hasp，axis=(1,0,0)）。`_half_disk_profile` L25-30 是圆顶身份的核心 lathe profile，必须保留。
- **lid_profile 轴**（Slot A）：flat_plank（`rec_chest_var_flatlid`，`lid_plank_{i}` 平板 + 平 `lid_strap_{i}` + `rivet_{i}`，**无 lathe，纯 Box**）/ gabled_peaked（`rec_chest_var_gabled`，`_gabled_panel` 三角脊 `lid_panel` + `ridge_cap` + `_gabled_strap` 斜坡铁带，**双坡尖顶 mesh**）相对 domed_barrel（`_barrel_band` 圆弧）是真正的 lid 几何/part 树变化（盖 part 不同 visual 组、helper 不同），但**共享同一 `lid_hinge` REVOLUTE 拓扑**（axis=(-1,0,0)，origin=(0,D/2,HB)，后缝铰）。
- **lock_mechanism 轴**（Slot B）：front_hasp（parent + flat + gabled 共用，`lock_keeper` body visual + `lock_hasp` 独立 part **REVOLUTE** `hasp_hinge` axis=(1,0,0) 挂在 **lid** 上抬起释放）/ padlock_loop（`rec_chest_var_padlock`，`_u_bar` 做 `staple_loop` body visual + `padlock_body` 独立 part **FIXED** 挂 body + `padlock_shackle` 独立 part **REVOLUTE** `shackle_hinge` axis=(0,0,1) 立轴摆出锁梁）→ 锁机构是 part 数 / joint 拓扑 / 接口父级的真实变化（hasp 挂 lid、shackle 挂 padlock_body）。
- **banding 轴**（Slot C）：iron_straps（parent，箱体 4 `corner_post_{i}` 直角铁柱 + 2 `body_band` + lid 上 5 `lid_strap_{i}` 横箍带 for-loop）/ corner_brackets（`rec_chest_var_corners`，`_corner_bracket_mesh` L 形角铁 mesh 包 8 角的 for-loop，每角 3 plate + 3 rivet）→ 箍带/包边是 body visual 的发射结构（for-loop 复制对象 + helper）变化；两者都是 **non-moving parent visual**（Rule 1）。
- **band_count 轴**（Slot D 多重性）：parent 的 `lid_strap_{i}` for-loop（5 条横箍带，x 位置列表 L92）与 corner_brackets 的 8 角 for-loop（L165-172）都是同构子件 N 次复制。横箍带数（domed/gabled/flat 盖上的 `lid_strap_{i}`）是真正可变的模板级复制轴（N=2..6 真实存在的箱箍密度），**箍带是 non-moving visual**（Rule 1）。

## 核心身份

一只**中世纪木箱宝箱（medieval banded treasure chest）**：一只矩形板条木箱体（`chest_body`，floor + 4 板条 wall，角部铁件加固），由**一个曲面/坡面盖（lid_profile）**后缝铰链封口——盖是本类别身份核心：**domed barrel 圆顶（lathe `_half_disk_profile` 半圆弧拱）**、**gabled 双坡尖顶（三角脊 prism）**或 flat_plank 平板。箱体外缠**铁箍带/角铁包边（banding）**——横向铁箍带 `lid_strap_{i}`（绕盖弧）+ 角柱/角铁包 8 角。前缘有**锁机构（lock_mechanism）**：可抬起的前翻铁搭扣 `lock_hasp`（REVOLUTE 挂 lid）或穿过 staple loop 的挂锁 + 立轴摆出锁梁 `padlock_shackle`（REVOLUTE 挂 padlock_body）。活动语义 = **盖的后缝翻起开合**（`lid_hinge` REVOLUTE axis=(-1,0,0)）+ **锁机构的释放动作**（搭扣抬起 / 锁梁摆出）。默认成熟域：边长 ~0.3–0.6 m 的单体木箱，至少 2 个非 fixed joint（盖 + 锁），盖呈曲面/坡面（非平顶）。

不该混入：
- **Suitcase（行李箱 / 旅行箱）**——壳体 + 拉链 + 万向轮 + 伸缩拉杆的扁平旅行携行件；本类是**静置单体木箱、无拉链/轮/拉杆**，盖是曲面/坡面非扁平对开壳。
- **Bag_Suitcase/Box（矩形平盖储物箱，`bag_suitcase_box`）**——同大类的姊妹小类，但其身份是**矩形单体箱 + 平顶盖（hinged_flat_top）+ 多机构 lid_closure（drop panel / 滑盖 / 立门 / 抽屉）**；treasure_chest 的身份在于**曲面/坡面盖 + 铁箍带 + 中世纪宝箱形态**——若盖降级成纯矩形平顶 + 无箍带，即退化为 Box 而出类。两者刻意分 slug：Box 主多样性在 lid_closure 机构族，treasure_chest 主多样性在 lid_profile 曲面族 + banding 铁件族 + band_count。
- **chest_freezer_with_hinged_lid（家电制冷柜）**——含压缩机/温控语义的家电壳体；本类是无源储物木箱。
- **首饰盒 / 药盒翻盖小盒**——缺铁箍带 + 曲面盖 + 中世纪宝箱身份。

## 槽位 + 候选模块表

> **建模注记**：3 个 named slot 都把自己的 part/visual 挂到**共同的 `chest_body` 根**（`mixed`：lid_profile 决定唯一活动主轴 `lid_hinge` 的盖 part，lock_mechanism 与 banding 各贡献 0–N 个独立子件 / body visual），外加 `band_count` 在盖上 N 次复制横箍带 visual。`lid_profile` 决定盖的 part 树 / mesh helper（但主 joint 拓扑 `lid_hinge` REVOLUTE 不变），`lock_mechanism` 决定第二/三 joint 的 part 数 / type / 父级（hasp REVOLUTE 挂 lid vs shackle REVOLUTE 挂 padlock_body + padlock FIXED 挂 body）。slot 之间通过共享 `chest_body` 的 mating face（顶后缝 rim / 前面 / 角部 / 弧面）装配。

### Slot A：lid_profile（盖型 —— 主结构轴；盖 part 树 / mesh helper 变化，`lid_hinge` REVOLUTE 保持）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| domed_barrel（基线）| parent `…_6febc2df` | helper `_half_disk_profile` L25-30 + `_barrel_band` L33-40；`lid_dome` + 5 `lid_strap_{i}` L88-95；`hasp_mount` L97-99；`lid_hinge` REVOLUTE L101-110 | eligible if compatible | **lathe 圆顶**：`_half_disk_profile` 半圆弧（segs=26）经 `ExtrudeGeometry.from_z0(cap=True)` + rotate_z/rotate_y 拉成半圆筒 `lid_dome`（`mesh_from_geometry`），峰高 ≈ HB+R；`lid_hinge` REVOLUTE axis=(-1,0,0) origin=(0,R,HB) 后缝铰，upper≈1.9 |
| flat_plank | `rec_chest_var_flatlid` | `_plank_x` L32-34；`lid_plank_{i}` planks L96-101；平 `lid_strap_{i}` L104-109；`rivet_{i}` L112-121；`hasp_mount` L124-126；`lid_hinge` REVOLUTE L129-139 | eligible if compatible | **平板盖（纯 Box，无 lathe）**：4 块 front-to-back `lid_plank_{i}` 平板 + 3 条平 `lid_strap_{i}` + 12 `rivet_{i}` 交点；盖顶 z ≈ HB+T_LID（非穹顶）；同一 `lid_hinge` REVOLUTE axis=(-1,0,0) origin=(0,D/2,HB)。**降级保护**：run_tests `lid is a flat plank profile (not domed)` 断言盖顶 < HB+T_LID+slack |
| gabled_peaked | `rec_chest_var_gabled` | helper `_gabled_profile` L26-40 + `_gabled_panel` L43-51 + `_gabled_strap` L54-66；`lid_panel` L117-118；5 斜坡 `lid_strap_{i}` L121-125；`ridge_cap` L128-130；`lid_front_skirt` L133-135；`hasp_mount` L138-140；`lid_hinge` REVOLUTE L142-151 | eligible if compatible | **双坡尖顶 mesh**：三角 `_gabled_profile`（rear/front edge + ridge peak）经 extrude → `lid_panel` 三棱柱（`mesh_from_geometry`），脊高 GABLE_PEAK=0.10；`ridge_cap` 铁脊 + 5 斜坡 `lid_strap_{i}`（`_gabled_strap` 略 proud）+ `lid_front_skirt`；同一 `lid_hinge` REVOLUTE axis=(-1,0,0) |

> 三候选共享 `lid_hinge` REVOLUTE 拓扑（轴/origin 相同），但盖 part 的 visual 组与 mesh helper 不同（lathe 圆弧 / 三角脊 / 纯板）→ part 树差异成立为独立 candidate。domed/gabled 的 lathe/mesh 不可降级成 flat Box（见 reject cases）。

### Slot B：lock_mechanism（锁扣 —— 第二/三 joint 拓扑轴；part 数 / type / 父级变化）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| front_hasp（基线）| parent `…_6febc2df`（+ flat / gabled 同款）| `lock_keeper` body visual L83-85；`lock_hasp` part（`hasp_arm`+`hasp_eye`）L113-117；`hasp_hinge` REVOLUTE L118-126 | eligible if compatible | **前翻搭扣**：body 前面 `lock_keeper` staple visual + `lock_hasp` 独立 part（`hasp_arm` + `hasp_eye`），**1×REVOLUTE** `hasp_hinge` **parent=lid**（axis=(1,0,0)，origin 在 lid 前缘 `hasp_mount`），q=0 搭扣悬下扣 keeper / 抬起释放 upper≈1.4。**latch parent=lid**（依赖 lid_profile 发出 `hasp_mount`）|
| padlock_loop | `rec_chest_var_padlock` | helper `_u_bar` L47-64；`staple_loop`+`staple_plate` body visual L108-124；`padlock_body` part L156-176 + `body_to_padlock` FIXED L179-185；`padlock_shackle` part L193-231 + `shackle_hinge` REVOLUTE L236-244 | eligible if compatible | **挂锁 + 锁梁**：body 前面 `_u_bar` `staple_loop`（mesh）+ `staple_plate` visual；`padlock_body` 独立 part（cadquery 倒角 `padlock_case` brass + `keyhole_plate`）**FIXED** 挂 body（`body_to_padlock`）；`padlock_shackle` 独立 part（`shackle_bow` U 梁 + 2 `shackle_leg_*`）**REVOLUTE** `shackle_hinge` **parent=padlock_body**（axis=(0,0,1) 立轴），q=0 锁梁穿 staple / 摆出 upper≈2.4。**2 个新 part + 1 FIXED + 1 REVOLUTE，锁机构挂 body（不挂 lid）** |

> 两候选锁机构不同 joint 拓扑：front_hasp = 1 REVOLUTE 挂 **lid**；padlock_loop = 1 FIXED + 1 REVOLUTE 挂 **body/padlock_body**。这是真正的 part 数 / joint type / 父级差异。Slot B 仅 2 candidate（样本池 4 var 只覆盖这 2 个锁机构）；**降级说明**：宝箱锁机构真实词汇表小（搭扣 / 挂锁是中世纪宝箱仅有的两类锁），2 candidate 已覆盖样本池全部锁拓扑，无第三类样本可采；满足 ≥2 下限且有明确理由，非 1-candidate 退化槽。

### Slot C：banding（箍带 / 包边 —— 箱体加固 visual 结构轴；non-moving，Rule 1）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| iron_straps（基线）| parent `…_6febc2df` | body 4 `corner_post_{i}` L64-74 + 2 `body_band_{l/r}` L77-80；lid 5 `lid_strap_{i}` for-loop L92-95 | eligible if compatible | **直角铁柱 + 横箍带**：4 根 `corner_post_{i}` 方角铁柱（垂直边）+ 2 条 `body_band` 竖向铁带（长面，带 rivet）+ 盖上 `lid_strap_{i}` 横箍带 for-loop（`_barrel_band`/`_gabled_strap`/平 Box，随 lid_profile）；全 non-moving body/lid visual |
| corner_brackets | `rec_chest_var_corners` | helper `_corner_bracket_mesh` L47-130；8 角 for-loop L155-172 | eligible if compatible | **角铁包边**：`_corner_bracket_mesh` L 形角铁（每角 3 plate Z/Y/X-face + 3 rivet bump，合并为单连通 mesh）包 8 个箱角的 for-loop（`_corners` 列表）；替方角铁柱；top4 角铁与 lid_dome 在 z=HB 平面 sandwich（element-scoped allow_overlap）；non-moving body visual |

> Slot C 2 candidate（样本池 4 var 只覆盖直柱箍带 / L 角铁两类包边）；**降级说明**：箱体包边真实形态在样本池内只有这两族（方角柱 + 横箍带 / L 形角铁），无第三类样本；满足 ≥2 下限，非退化槽。`lid_strap_{i}` 横箍带数由 band_count（Slot D）控制。

硬约束记录：Slot A=3、Slot B=2（有降级说明）、Slot C=2（有降级说明）、Slot D=band_count 多重性轴（采样域 [2,6]）；全部来自被采纳五星样本，无 1-candidate 槽。

## 槽位图（slot graph）

pattern: `mixed`（固定 named slots: lid_profile + lock_mechanism + banding 各自挂到共同 `chest_body`（parallel children），外加 `band_count` 在 `chest_lid` 上 N 次复制横箍带 visual）

```
chest_body (root, 坐地; floor + 4 板条 wall + lock_keeper/staple 接口面)
  │
  ├── [lid_profile slot]  (互斥三选一; 决定盖 part 树/mesh, 共享 lid_hinge 拓扑)
  │     ├─ domed_barrel : chest_lid(lid_dome lathe 圆弧) ──[lid_hinge: REVOLUTE axis=-X, origin=(0, D/2, HB) 后缝]
  │     ├─ flat_plank   : chest_lid(lid_plank_{i} 平板)  ──[lid_hinge: REVOLUTE axis=-X, origin=(0, D/2, HB) 后缝]
  │     └─ gabled_peaked: chest_lid(lid_panel 三角脊)    ──[lid_hinge: REVOLUTE axis=-X, origin=(0, D/2, HB) 后缝]
  │
  ├── [lock_mechanism slot]  (互斥二选一)
  │     ├─ front_hasp   : lock_hasp ──[hasp_hinge: REVOLUTE axis=+X, parent=chest_LID, origin=lid 前缘 hasp_mount]
  │     │                  (+ lock_keeper = body visual)
  │     └─ padlock_loop : padlock_body ──[body_to_padlock: FIXED, parent=chest_body]
  │                        padlock_shackle ──[shackle_hinge: REVOLUTE axis=+Z, parent=padlock_BODY]
  │                        (+ staple_loop/staple_plate = body visual)
  │
  ├── [banding slot]  (互斥二选一; non-moving body/lid visual)
  │     ├─ iron_straps    : corner_post_{i}(×4) + body_band(×2) + lid_strap_{i}(×N) = body/lid visual
  │     └─ corner_brackets: corner_bracket_{i}(×8 L 形角铁 mesh) + lid_strap_{i}(×N) = body/lid visual
  │
  └── [band_count multiplicity 轴]  lid_strap_{i}  i∈range(N), N∈[2,6]
        发射位置：盖弧/坡/面上沿 X 等距并排（绝对式: x = -W/2 + margin + i·spacing）；
        几何随 lid_profile（domed→_barrel_band 弧带 / gabled→_gabled_strap 坡带 / flat→平 Box 带）
```

接口点位与 joint 语义：
- **lid_profile → chest_body**（互斥三选一）：盖均沿**顶后缝 rim** 铰，`lid_hinge` REVOLUTE axis=(-1,0,0)，origin=(0, D/2, HB)（落在后缝铰线 = body 顶后边）；rest pose q=0 盖合在 body rim（0–6 mm gap，`expect_gap` 守座入 + `expect_overlap` xy ≥0.20 覆盖开口）。盖前缘携带 `hasp_mount`（供 front_hasp 接入）。domed/gabled 盖 mesh 用 lathe/三角 helper，不降级 Box。
- **lock_mechanism**（互斥二选一）：
  - front_hasp：`hasp_hinge` REVOLUTE **parent=chest_lid**（不是 body！axis=(1,0,0)，origin 在 lid 前缘 `hasp_mount` 下方），q=0 搭扣悬下扣 `lock_keeper`（body visual）/ 抬起 upper≈1.4 释放。**依赖 lid_profile 发出 `hasp_mount`**（三盖均发）。
  - padlock_loop：`body_to_padlock` FIXED parent=chest_body（挂锁体悬于 `staple_loop` 下）；`shackle_hinge` REVOLUTE **parent=padlock_body**（axis=(0,0,1) 立轴，origin 在 padlock 顶左腿），q=0 锁梁穿 `staple_loop` / 摆出 upper≈2.4 释放。锁机构全挂 body（与 lid 解耦）。
- **banding → chest_body / chest_lid**（互斥二选一，non-moving visual，Rule 1）：iron_straps = 4 `corner_post_{i}` 直柱 + 2 `body_band`（body visual）；corner_brackets = 8 `corner_bracket_{i}` L 角铁 mesh（body visual，top4 与 lid_dome z=HB sandwich）。两者都加盖上 `lid_strap_{i}` 横箍带（band_count 控制数量）。
- **band_count 接口**：`lid_strap_{i}` 为**非移动 visual**（Rule 1，inline 到 `chest_lid` 的 visual，无独立 joint）；沿 X 绝对式等距并排，几何随 lid_profile 切换 helper（`_barrel_band` 弧带 / `_gabled_strap` 坡带 / 平 Box 带）。
- **mating policy**：所有活动接口是 captured 几何——hasp 销挂 `hasp_mount` plate、shackle 腿插 padlock_body（`shackle_leg_*`）、shackle 穿 `staple_loop` loop、top 角铁与 lid_dome z=HB sandwich —— 非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（来源样本 run_tests 已逐条声明：flatlid L178-197 hasp↔mount/keeper、gabled L256-273 hasp↔keeper/mount、padlock L326-340 shackle↔staple/padlock、corners L269-279 top 角铁↔lid_dome）。
- **rest pose**：盖 q=0 闭合座 rim、hasp q=0 悬下扣 keeper、shackle q=0 穿 staple、横箍带坐盖面。
- **互斥 / 可选 / 派生**：lid_profile 三候选互斥；lock_mechanism 二候选互斥；banding 二候选互斥；front_hasp 依赖 lid 发出 `hasp_mount`（三盖均发 → 始终兼容）。详见 §10 兼容矩阵。

## 每槽位 Module Emits / Interfaces

### Slot A / lid_profile — domed_barrel（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chest_lid`（visual: `lid_dome` lathe 半圆筒 + `lid_strap_{i}`×N 弧箍带 + `hasp_mount`）| parent `_barrel_band` L33-40 / L88-99 |
| internal joints | `lid_hinge` REVOLUTE，axis=(-1,0,0)，origin=(0, D/2, HB)，range [0, 1.9] | parent L101-110 |
| upstream interface | 顶后缝 rim（消费 `chest_body` 顶后边 `wall_back` 顶面）| parent L101-110 |
| downstream interface | lid 前缘 `hasp_mount`（携带 front_hasp 的 `hasp_hinge`）| parent L97-99 |

### Slot A / lid_profile — flat_plank
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chest_lid`（visual: `lid_plank_{i}`×4 平板 + 平 `lid_strap_{i}`×N + `rivet_{i}` + `hasp_mount`）| flatlid L96-126 |
| internal joints | `lid_hinge` REVOLUTE，axis=(-1,0,0)，origin=(0, D/2, HB)，range [0, 1.9] | flatlid L129-139 |
| upstream interface | 顶后缝 rim | flatlid L129-139 |
| downstream interface | lid 前缘 `hasp_mount` | flatlid L124-126 |

### Slot A / lid_profile — gabled_peaked
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chest_lid`（visual: `lid_panel` 三角脊 mesh + 坡 `lid_strap_{i}`×N + `ridge_cap` + `lid_front_skirt` + `hasp_mount`）| gabled `_gabled_panel` L43-51 / L117-140 |
| internal joints | `lid_hinge` REVOLUTE，axis=(-1,0,0)，origin=(0, D/2, HB)，range [0, 1.9] | gabled L142-151 |
| upstream interface | 顶后缝 rim | gabled L142-151 |
| downstream interface | lid 前缘/skirt `hasp_mount` | gabled L138-140 |

### Slot B / lock_mechanism — front_hasp（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lock_hasp`（visual: `hasp_arm` + `hasp_eye`）；body 上 `lock_keeper` visual | parent L83-85, L113-117 |
| internal joints | `hasp_hinge` REVOLUTE，axis=(1,0,0)，**parent=chest_lid**，origin=lid 前缘 hasp_mount，range [0, 1.4] | parent L118-126 |
| upstream interface | `hasp_arm` 顶嵌入 lid 的 `hasp_mount` plate（captured，allow_overlap）| flatlid L178-183 |
| downstream interface | `hasp_eye` 扣 body `lock_keeper`（captured，allow_overlap）| flatlid L188-197 |

### Slot B / lock_mechanism — padlock_loop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `padlock_body`（`padlock_case` cadquery + `keyhole_plate`）+ `padlock_shackle`（`shackle_bow` + `shackle_leg_fixed/free`）；body 上 `staple_loop`+`staple_plate` visual | padlock L108-124, L156-231 |
| internal joints | `body_to_padlock` FIXED（parent=chest_body）+ `shackle_hinge` REVOLUTE，axis=(0,0,1)，**parent=padlock_body**，range [0, 2.4] | padlock L179-185, L236-244 |
| upstream interface | `padlock_body` 悬于 body `staple_loop` 下（FIXED）；`shackle_bow` 穿 `staple_loop` loop（captured，allow_overlap）| padlock L326-330 |
| downstream interface | `shackle_leg_fixed/free` 插入 `padlock_case`（captured，allow_overlap + expect_within）| padlock L331-349 |

### Slot C / banding — iron_straps（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`corner_post_{i}`×4 + `body_band_{l/r}`×2（body visual）+ `lid_strap_{i}`×N（lid visual）| parent L64-80, L92-95 |
| internal joints | 无（Rule 1，non-moving）| — |
| upstream interface | 挂 `chest_body` 四垂直边 + 长面（body visual）；盖弧/坡/面（lid visual）| parent L64-80 |

### Slot C / banding — corner_brackets
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`corner_bracket_{i}`×8（L 形角铁 mesh，body visual）+ `lid_strap_{i}`×N（lid visual）| corners `_corner_bracket_mesh` L47-130 / L155-172 |
| internal joints | 无（Rule 1，non-moving）| — |
| upstream interface | 挂 `chest_body` 8 角（top4 与 lid_dome z=HB sandwich，allow_overlap）| corners L155-172, L269-279 |

### band_count multiplicity（横箍带复制；non-moving visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`lid_strap_{i}`（domed 风 `_barrel_band` 弧带 / gabled 风 `_gabled_strap` 坡带 / flat 风平 Box 带）作 `chest_lid` 的 visual | parent L92-95 / gabled L121-125 / flatlid L104-109 |
| joints | 无（Rule 1，箍带非移动件 inline）| — |
| placement | `for i in range(N)`，沿 X 绝对式等距并排（parent x 列表 L92 / flatlid `STRAP_Y_FRACS`→改 X 等距 / gabled L121）| parent L92 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| lid_profile | enum | domed_barrel / flat_plank / gabled_peaked | — | choice | deterministic sampler 选；决定盖 part 树 + mesh helper（共享 lid_hinge）| module table |
| lock_mechanism | enum | front_hasp / padlock_loop | — | choice | sampler 选；主锁机构（互斥，joint 拓扑/父级不同）| module table |
| banding | enum | iron_straps / corner_brackets | — | choice | sampler 选；箱体包边 visual（互斥，non-moving）| module table |
| band_count (N) | int | 声明域 [2,6]；sweep 采样域 [2,6]（偏小加权：3–4 高频、5–6 长尾）| 5（parent 名义）| conditional→slot_choice | 编入 slot_choice 为 `("band_count", f"n{N}")`（拓扑维度）；N 与 lid 宽 W 联动（见不等式）| parent L92 |
| palette_style | enum | aged_oak_iron / dark_walnut_blackiron / weathered_pine_iron / mahogany_brass / ebony_brass | aged_oak_iron | palette | palette only，**不计入 slot_choice**；见 §PALETTE_STYLES | 各样本 material |
| box_w / box_d | float | W∈[0.34,0.60]、D∈[0.24,0.38] | W=0.46, D=0.30 | independent | 在范围内独立采样后 clamp | parent L18-19 |
| box_h HB | float | [0.14,0.24] | 0.18 | independent | 独立采样 clamp（domed/gabled 盖峰高随 D/GABLE_PEAK 派生不计入 HB）| parent L20 |
| barrel_radius R | float | derived | D/2 | equation | `R = D/2`（domed 盖弧半径 = 半深，保盖跨满深）| parent L22 |
| gable_peak | float | derived | 0.10 | equation | `= clamp(0.06, 0.5·D)`（gabled 脊高，仅 gabled_peaked 有效）| gabled L23 |
| wall_thickness T | float | derived | 0.018 | equation | `= clamp(0.014, 0.020)` 随 box scale | 各样本 L17-21 |
| lid_open_scale | float | [0.85, 1.05] | 1.0 | independent | 缩放 `lid_hinge` upper（基线 1.9，clamp ≤ π·0.62）| 各样本 motion_limits |
| lock_open_scale | float | [0.85, 1.05] | 1.0 | independent | 缩放 hasp(1.4)/shackle(2.4) upper，clamp | 各样本 motion_limits |
| strap_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放横箍带并排间距 | parent L92 |
| (—) | constraint | — | — | inequality | 横箍带不超盖宽：`N·strap_w + (N-1)·gap ≤ W − 2·margin`；违反时按比例缩 strap_w / spacing 或 clamp N 上限 | parent L92 |
| (—) | constraint | — | — | conditional | gable_peak 仅 lid_profile=gabled_peaked 解析；R 仅 domed_barrel 用作弧半径；flat_plank 盖顶 z 派生 = HB+T_LID（不抬穹顶）| lid_profile |

连续尺寸采样契约：先采 named slot（lid_profile / lock_mechanism / banding）+ N（解析 conditional：gable_peak 仅 gabled、strap_spacing 仅 N≥2）→ 采 independent 主尺度（box_w/d/h、lid_open_scale、lock_open_scale）→ 派生 R/gable_peak/T（equation）→ 用 inequality 把横箍带排布投影回盖宽可行域（违反则缩 strap_w/spacing 或 clamp N）。所有 scale 在 `resolve_config` clamp/派生，**绝不改 slot enum 选择、joint type 或盖曲面身份**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（盖上横向铁箍带数）：

- **count_param**：`band_count`（模板内变量 N / BAND_COUNT；`chest_lid` 上 `lid_strap_{i}` 横箍带条数）。
- **N_range**：声明产品域 **[2, 6]**（中世纪宝箱盖上的横箍带数现实区间——2 条最简到 6 条密箍；source map 建议 [2,6]）。`config_from_seed` 的 sweep 采样域 **[2, 6]**（偏小加权：N=3/4 高频、N=5/6 长尾）。parent 名义 N=5。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,4,5,6), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [2,6]，并按盖宽不等式收窄上限。
- **copied object**：单条横箍带——`lid_strap_{i}`，几何随 lid_profile 共享 helper（domed→`_barrel_band(R+0.004, x0, strap_w)` 弧带 / gabled→`_gabled_strap(D, peak, strap_w, x0)` 坡带 / flat→`Box((W, strap_w, strap_t))` 平带）；N 个 visual 复用同一 helper。
- **naming**：`lid_strap_{i}`，`for i in range(N)`（parent L92-95 / gabled L122-125 / flatlid L104-109 已用此结构，可直接作 copy-logic 源）。
- **placement**：沿 X **绝对式**等距并排——以盖中心对称分布（`x_i = -W/2 + margin + i·(W − 2·margin)/(N−1)`，端带贴边缘）。绝对式（每个 i 的 x 由 N 与盖宽解析，不累加漂移）是 N-不变前提。
- **joint policy**：横箍带是**非移动件**（Rule 1）→ inline 为 `chest_lid` 的 visual，**不发射独立 joint**；活动关节由 lid_hinge / lock_mechanism 提供。箍带随 lid 一起翻起（FIXED 于 lid，Rule 1）。
- **source/gating**：copy-logic 源取 parent L92-95（domed 弧带 N=5）+ gabled L121-125（坡带 N=5）+ flatlid L104-109（平带 N=3）的 `for i in range(N)` / 位置列表循环；N 与 lid_profile 正交（任意盖均可配任意 N），但受盖宽不等式约束上限。
- **说明**：corner_brackets 的 8 角 for-loop（corners L165-172）是 banding module **内部固定数量**的局部循环（8 个固定箱角），**不是模板级 N-复制轴**（角数不进 slot_choice，不加权采样）；padlock 的 2 shackle_leg、parent 的 4 corner_post / 2 body_band 同此判定。唯一模板级多重性轴是 `band_count`。

## PALETTE_STYLES（colorway，per-seed 采样，不计入 slot_choice）

> 跟随 `Accessories_Cushion.md` PALETTE_STYLES 模式：palette_style 是一只**命名材质集**（per-seed `rng.choice`），只换 `model.material(...)` 的 rgba，不改任何 part 树 / joint / mesh。下列 5 套均**来自 5 星样本实际观测到的材质**（parent/flat/gabled 用 wood + wood_dark + wood_light + iron_band；padlock 额外引入 iron_dark + brass_lock）：木色（深/中/浅木 stain）× 金属箍件（iron-black / blackened-iron / brass-bronze）的现实组合。

| palette_style | wood（主板）| wood_dark（floor/暗板）| wood_light（亮板）| band/hardware（箍带/角铁/锁）| 锁体/亮件 | 观测来源 |
|---|---|---|---|---|---|---|
| aged_oak_iron（基线）| `chest_wood` (0.42,0.30,0.20) | `chest_wood_dark` (0.30,0.21,0.14) | `chest_wood_light` (0.48,0.35,0.23) | `iron_band` (0.20,0.21,0.24) iron-black | — | parent / flat / gabled / corners |
| dark_walnut_blackiron | walnut (0.26,0.17,0.11) | (0.18,0.12,0.08) | (0.34,0.24,0.16) | `iron_dark` (0.16,0.17,0.20) blackened | — | padlock `iron_dark` + 深木变体 |
| weathered_pine_iron | weathered pine (0.55,0.45,0.34) | (0.42,0.34,0.25) | (0.62,0.52,0.40) | `iron_band` (0.20,0.21,0.24) iron-black | — | parent wood/light 提亮（风化松木）|
| mahogany_brass | mahogany (0.36,0.18,0.13) | (0.26,0.13,0.09) | (0.44,0.24,0.18) | iron-black (0.20,0.21,0.24) | `brass_lock` (0.60,0.50,0.22) 黄铜锁/铆钉 | padlock `brass_lock` + 红木 |
| ebony_brass | ebony (0.16,0.13,0.11) | (0.10,0.08,0.07) | (0.24,0.20,0.17) | `iron_dark` (0.16,0.17,0.20) blackened | `brass_lock` (0.60,0.50,0.22) bronze 箍/锁 | padlock iron_dark + brass，黑檀 |

palette_style 在 `config_from_seed` 用 `rng.choice` 选；`resolve_config` 把名字映射到 material rgba 集；**不计入 `slot_choices_for_seed`**（非拓扑维度）。padlock_loop 必带 brass/iron_dark 可用项（brass_lock 用作 `padlock_case`）；front_hasp 用对应 band rgba 作搭扣。

## 拓扑多样性审计

总组合数（不含 palette、不含连续 scale）：
lid_profile(3) × lock_mechanism(2) × banding(2) × band_count 采样数(5，即 {2,3,4,5,6}) = **60**。
不含 band_count 的命名 slot 笛卡尔积 = lid_profile(3) × lock_mechanism(2) × banding(2) = **12 ≥ 10** ✓（与 source map 预审一致）。

仅 lid_profile(3) × lock_mechanism(2) = **6**；叠 banding(2) → 12 ≥ 10 已稳过；叠 band_count(5) → 60 充裕。

理由：`slot_choices_for_seed` 返回 `(lid_profile, lock_mechanism, banding, ("band_count", f"n{N}"))` 四元组；12 个命名 slot 组合已 ≥10，叠 N 后 60 个合法 distinct 远超 10。lock_mechanism 的 front_hasp（hasp REVOLUTE 挂 lid）与 padlock_loop（FIXED + shackle REVOLUTE 挂 padlock_body）是不同 joint 拓扑等价类（part 数 / type / 父级不同），不会被 distinct 折叠。**N 必须编入 slot_choice tuple**（对齐 cushion/shopping_bucket/fence_cascade），否则不同箍带数在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（lid_profile / lock_mechanism / banding，三槽正交，无非法组合），再 `rng.choices` 加权 N∈[2,6]，再解析 conditional（gable_peak 仅 gabled、strap_spacing 仅 N≥2），再 uniform 各连续 scale，最后 `rng.choice` palette_style。compatibility matrix 主要守 N 与盖宽（盖宽不足时 clamp N 上限）与 domed/gabled mesh 不降级（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：关键 scale = box_w / box_d / box_h（independent，clamp）、barrel_radius R（equation = D/2）、gable_peak（equation，conditional@gabled）、wall_thickness T（equation）、lid_open_scale / lock_open_scale（independent，每主 joint clamp）、strap_spacing_scale（conditional@N≥2）。全部 `resolve_config` clamp/派生，按 §7 约束类型声明依赖；遵循采样契约（named slot + N + conditional → independent → equation → inequality 投影）。这些 scale 不破坏 lid_hinge origin（后缝铰线）、hasp/shackle captured 接口、band_count 复制逻辑或类别曲面身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（正交无 gate）→ `rng.choices` 加权 N∈[2,6] → 解析 conditional（gable_peak/strap_spacing）→ uniform scale → `rng.choice` palette | slot_choices_for_seed 含 `("band_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **band_count × 盖宽**：横箍带排布超盖宽时 clamp N 上限 / 缩 strap_w（盖窄时 N≤4）。 (2) **domed/gabled mesh 不降级**：domed 必走 `_barrel_band` lathe、gabled 必走 `_gabled_panel` 三角，禁退化纯 Box（run_tests profile 断言）。 (3) **front_hasp 依赖 hasp_mount**：三盖均发 `hasp_mount` → 始终兼容（无需 gate）。 (4) lid_profile / lock_mechanism / banding 三槽正交（任意盖配任意锁配任意包边均合法）。 (5) **padlock_loop palette**：必含 brass/iron_dark 可用项作 `padlock_case`/hardware。 | 无 floating lock、盖不降级、横箍带不超盖、N 不越界、palette 缺色 |
| controlled local variation | box_w/d/h + R/gable_peak/T（equation 派生）+ lid_open/lock_open/strap_spacing scale，全 clamp/派生 | 比例变化不破坏 lid 后缝铰 origin、hasp/shackle captured、盖曲面峰高、横箍带等距、坐 rim、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 captured allow_overlap + closed-pose seat + 盖曲面 profile |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| lid_profile | 3 | yes | yes | domed lathe / gabled 三角 / flat 平板（共享 lid_hinge，盖 part 树不同）|
| lock_mechanism | 2 | yes | no | front_hasp(REVOLUTE 挂 lid) / padlock_loop(FIXED + REVOLUTE 挂 padlock)；样本池仅这 2 类锁拓扑（降级说明见 Slot B）|
| banding | 2 | yes | no | iron_straps(角柱) / corner_brackets(L 角铁)；样本池仅这 2 类包边（降级说明见 Slot C）|
| band_count (N) | 5（采样域 {2,3,4,5,6}，3–4 高频 / 5–6 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名四元组 `(lid_profile, lock_mechanism, banding, ("band_count", f"n{N}"))`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊），N 采样域 ⊆ [2,6]
- `resolve_config` 把 band_count clamp 到 [2,6] 并按盖宽不等式收窄上限；各 scale clamp 到声明范围；gable_peak（conditional@gabled）/ strap_spacing（conditional@N≥2）随 slot/N 解析；R=D/2、T 派生在 resolve 内
- compatibility matrix / gating 阻止非法组合（横箍带超盖宽 clamp N；domed/gabled mesh 不降级；padlock palette 必含 brass/iron_dark）
- 连续 scale clamp 后不破坏 lid_hinge 后缝 origin / hasp/shackle captured 接口 / 盖曲面峰高 / 横箍带等距 / 坐 rim / 类别身份
- cross-part scale 依赖（R=D/2、gable_peak conditional、横箍带排布 inequality、T equation）在 `resolve_config` 解析，不留到 builder
- 关键 joint：`lid_hinge` REVOLUTE axis≈(-1,0,0)（abs(axis[0])>0.99）origin 在后缝（z≈HB）；front_hasp `hasp_hinge` REVOLUTE axis≈(1,0,0) **parent=chest_lid**；padlock_loop `body_to_padlock` FIXED + `shackle_hinge` REVOLUTE axis≈(0,0,1) **parent=padlock_body**
- 曲面身份：domed_barrel run_tests 断言 `lid_dome` 峰 > HB+R·0.7；gabled_peaked 断言 ridge > 前缘 + 0.04（双坡）；flat_plank 断言盖顶 < HB+T_LID+slack（**反向守不穹顶**）
- captured 接口：element-scoped `allow_overlap`（hasp_arm↔hasp_mount、hasp_arm/eye↔lock_keeper、shackle_bow↔staple_loop、shackle_leg_*↔padlock_case、top corner_bracket↔lid_dome），照搬各样本 run_tests 段
- copied object 遵循 `lid_strap_{i}` 命名 + 绝对式沿 X 等距 placement + Rule 1（无独立 joint，随 lid FIXED）
- grandfather：所有 hasp/shackle/staple/sandwich captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- palette_style 只换 material rgba，不进 slot_choice，不改 part 树

## Reject cases

- 把 domed_barrel / gabled_peaked 盖降级成纯矩形 Box 平顶 → 丢失宝箱曲面身份、退化为 Box 小类；必须保留 `_barrel_band` lathe / `_gabled_panel` 三角 mesh（run_tests profile 断言守护）。
- 把 N（band_count）当普通 int 参数、不进 slot_choice → 不同箍带数 slot_choice 同形，损失一整根拓扑维度（违反 §8/§9 硬要求）。
- 把 corner_brackets 的 8 角 for-loop / padlock 的 2 shackle_leg / parent 的 4 corner_post 当成模板级 multiplicity 轴并加权采样 → 误造 count 参数（这些是 module 内部固定数量，违反 §8 单体判定）。
- 让 front_hasp 的 `hasp_hinge` parent 设成 body 而非 **lid** → 搭扣不随盖翻起、铰线错位、closed-pose 错；hasp 必须挂 chest_lid。
- 让 padlock_loop 的 `shackle_hinge` parent 设成 body 而非 **padlock_body**，或漏 `body_to_padlock` FIXED → 锁体浮空 / 锁梁铰线脱离锁体 FAIL。
- 横箍带 strap_spacing/N 过大致箍带超出盖宽 → §7 不等式 FAIL；须按比例缩 strap_w/spacing 或 clamp N 上限。
- 给 captured 接口（hasp↔mount/keeper、shackle↔staple/padlock、top 角铁↔dome）补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + element-scoped allow_overlap（照搬来源样本 run_tests）。
- 盖 / 搭扣 / 锁梁 rest pose 设成张开角而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合）。
- 把连续尺寸（box_w/h）/ gable_peak / palette_style 当新 candidate 塞进 slot → 不是结构差异，违反 §2.4。
- 把 padlock_loop 配非 brass/iron_dark palette 致 `padlock_case` 颜色缺失 → palette gating 须保证挂锁体有黄铜/暗铁可用项。

## 与相邻类别的边界

- 不该混入：**Suitcase（行李箱 / 旅行箱）**——壳体 + 拉链 + 万向轮 + 伸缩拉杆的扁平携行件；本类是静置单体木箱、曲面/坡面盖、无拉链/轮/拉杆。
- 不该混入：**Bag_Suitcase/Box（`bag_suitcase_box`，矩形平盖储物箱）**——同大类姊妹小类，身份是矩形 + 平顶盖 + 多 lid_closure 机构族（drop panel / 滑盖 / 立门）；treasure_chest 身份在曲面/坡面盖 + 铁箍带 + 中世纪宝箱形态；盖降级矩形平顶 + 无箍带即退化为 Box 出类。两者刻意分 slug。
- 不该混入：**chest_freezer_with_hinged_lid（家电制冷柜）**——含压缩机/温控的家电壳体；本类是无源储物木箱。
- 不该混入：**首饰盒 / 药盒翻盖小盒**——缺铁箍带 + 曲面盖 + 中世纪宝箱身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) Slot B/C 各 2 candidate 的降级说明（样本池仅 4 var，锁/包边真实词汇表小）是否接受；(2) band_count 编入 slot_choice 为 `("band_count", f"n{N}")` 且横箍带 Rule 1 inline 无独立 joint；(3) front_hasp parent=lid 与 padlock shackle parent=padlock_body 的父级接口；(4) Topology target 60<300 的说明是否接受（本小类真实结构上限）；(5) palette_style 5 套（aged_oak_iron / dark_walnut_blackiron / weathered_pine_iron / mahogany_brass / ebony_brass）是否覆盖足够木色/金属现实组合；(6) domed/gabled mesh 不降级 Box 的 run_tests profile 断言守护）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_half_disk_profile`/`_barrel_band`（domed 盖 + domed 风横箍带，parent L25-40）、`_gabled_profile`/`_gabled_panel`/`_gabled_strap`（gabled 盖 + 坡箍带，gabled L26-66）、`_plank_x`（flat 盖板，flatlid L32-34）、`_corner_bracket_mesh`（corner_brackets 包边，corners L47-130）、`_u_bar`（staple_loop + shackle_bow，padlock L47-64）。横箍带 helper 随 lid_profile 切换，N 复制复用同一 helper。
- captured 接口 allow_overlap：`run_treasure_chest_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段：front_hasp（flatlid L178-197 / gabled L256-273：hasp_arm↔hasp_mount + hasp_arm/eye↔lock_keeper）、padlock_loop（padlock L326-340：shackle_bow↔staple_loop + shackle_leg_fixed/free↔padlock_case，+ expect_within L343-349）、corner_brackets（corners L269-279：top4 corner_bracket_{i}↔lid_dome z=HB sandwich）。
- joint 父级关键：front_hasp `hasp_hinge` **parent=chest_lid**（随盖翻起）；padlock_loop `shackle_hinge` **parent=padlock_body**（不挂 body）+ `body_to_padlock` FIXED parent=chest_body。实现时严守，勿混父级。
- 曲面身份守护：domed/gabled 盖必走 lathe/三角 mesh helper（不降级 Box）；保留各样本 run_tests 的 profile 断言（domed 峰 > HB+R·0.7 / gabled ridge > 前缘 + 0.04 / flat 盖顶 < HB+T_LID+slack 反向守）。
- band_count N=2..6：用 `for i in range(N)` 绝对式沿 X 等距发射 `lid_strap_{i}`（端带贴盖缘）；几何随 lid_profile（弧/坡/平带）；箍带 FIXED 于 lid（Rule 1，随盖翻起）。
- 不调 `fail_if_parts_overlap_in_sampled_poses`（多 module 多姿态积大）；保留自动 baseline 的 `fail_if_parts_overlap_in_current_pose`（closed rest pose 干净）。
- 参考实现模板（review 通过后选读）：`agent/templates/Accessories_Cushion.py`（同为 mixed：固定 named slots + multiplicity 轴 `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh helper 复用 + 兼容矩阵 + captured allow_overlap 骨架 + PALETTE_STYLES）；`agent/templates/Bag_Suitcase_Box.py`（同大类 box-shell + hinged-lid + hasp latch 骨架，body chassis + lid REVOLUTE + captured-pin 范式可同构改编）；`agent/templates/single_revolute_hinge` 类（hinge line / closed pose / captured-pin overlap）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A / B / C（parent 基线）| domed_barrel + front_hasp + iron_straps | rec_medieval-treasure-chest-…`_6febc2df` | `_half_disk_profile` L25-30 / `_barrel_band` L33-40 / body L50-85 / `lid_dome`+5 `lid_strap_{i}` L88-95 / `lid_hinge` REVOLUTE L101-110 / `lock_hasp`+`hasp_hinge` L113-126 | root chassis + domed lathe 圆顶 + front_hasp + iron_straps 箍带 + band_count copy 源 |
| S1 | A | flat_plank | rec_chest_var_flatlid | `_plank_x` L32-34 / `lid_plank_{i}` L96-101 / 平 `lid_strap_{i}` L104-109 / `rivet_{i}` L112-121 / `lid_hinge` L129-139 / allow_overlap L178-197 | 平板盖（纯 Box）+ 平横箍带 copy 源 + hasp captured allow_overlap 范式 |
| S2 | A | gabled_peaked | rec_chest_var_gabled | `_gabled_profile` L26-40 / `_gabled_panel` L43-51 / `_gabled_strap` L54-66 / `lid_panel` L117-118 / `ridge_cap` L128-130 / 坡 `lid_strap_{i}` L121-125 / `lid_hinge` L142-151 / allow_overlap L256-273 | 双坡尖顶 mesh + 坡横箍带 copy 源 + gabled profile 断言 |
| S3 | B | padlock_loop | rec_chest_var_padlock | `_u_bar` L47-64 / `staple_loop`+`staple_plate` L108-124 / `padlock_body`(cadquery) L156-176 + `body_to_padlock` FIXED L179-185 / `padlock_shackle` L193-231 + `shackle_hinge` REVOLUTE +Z L236-244 / allow_overlap L326-349 | 挂锁体（FIXED）+ 锁梁（REVOLUTE 立轴）+ staple captured + brass palette 源 |
| S4 | C | corner_brackets | rec_chest_var_corners | `_corner_bracket_mesh` L47-130 / 8 角 for-loop `corner_bracket_{i}` L155-172 / top4↔dome allow_overlap L269-279 | L 形角铁包 8 角 mesh + sandwich captured 范式 |
