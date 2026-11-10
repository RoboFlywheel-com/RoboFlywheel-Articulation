# container_locker (steel storage locker / cabinet bank) — Modular Spec

> 来源小类：`picture/Container/Locker`（articraft_data 上游 Container/Locker fork-variant pool）。
> 源 source map：`articraft_data/picture_expansion/template_source_maps/Container__Locker.md`。
> 1 母资产 + 10 个 converged fork 变体，全部读 `model.py`（见 §5 摘要）。引用 `model.py:Lx-Ly`
> 来自各样本 `arti-template/data/records/<id>/revisions/rev_000001/model.py`，以 part/joint/helper
> **名字** 为准（`carcass` / `door_{idx}` / `hinge_{idx}` / `slide_{idx}` / `shutter_{idx}` /
> `door_vent_{idx}` / `door_mesh_{idx}` / `door_slot_{idx}_{i}` / `lockbtn_{idx}_{n}` /
> `btnjoint_{idx}_{n}` / `hasp_{idx}` / `dial_{idx}` / `dialjoint_{idx}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_locker` |
| template path | `agent/templates/Container_Locker.py` |
| test path (optional) | `tests/agent/test_container_locker_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: closure_mechanism(主机构) + door_surface + latch_mechanism；外加 `bank_count` 一根 multiplicity 轴——同一行并排 locker bay × N）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 10 converged fork 变体 = 11 |
| read_count | 11（全部读 `model.py` 全文 / 关键机构段）|
| read_scope | combinatorial fork pool：parent 全读 + 每个变体读其差异层（closure 机构 / door-face / latch / multiplicity 循环）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表与 §14 |

逐样本要点（采纳归属）：
- **P1**（`rec_a-bank-of-two-metal-storage-lockers-with-hinged-_..._d0776185`）：两并排金属储物柜。共享 `carcass`（plinth/divider/per-bay back·side_l·side_r·top·bottom·shelf）；每 bay 一扇 `door_{idx}` REVOLUTE 侧铰门（`hinge_{idx}` 绕左竖边 +Z 轴外摆 0..100°）；门面 `door_vent_{idx}` VentGrilleGeometry 百叶 + `door_plate_{idx}` PerforatedPanel 号牌；门底 `lockpad_{idx}` 上 10 颗 `lockbtn_{idx}_{n}` PRISMATIC 按键（`btnjoint_{idx}_{n}` -Y 内压 1.5mm，双层 `for r/c in range` 循环）。**采纳为 closure=hinged_single_door 基线 + door_surface=louver_vents 基线 + latch=keypad_buttons 基线 + carcass 共享件 + bank_count 基线 N=2**。§4 可读性问题：bay 复制用 `for idx in (0, 1):` 手写元组（非 `range(n)`），bank_count_4 变体已修。
- **double_leaf_doors**：`_build_leaf` 把每 bay 拆为左右两窄扇 `door_{idx}_0`/`door_{idx}_1`，各自 `hinge_{idx}_{leaf}` REVOLUTE 绕外缘对开（左扇 axis +Z、右扇 axis -Z，从中线对开）；键盘只在左扇。**采纳为 closure=double_leaf_doors**。
- **sliding_door**：`_build_track_rails` 给每 bay 加上下 `track_top_{idx}`/`track_bottom_{idx}` 轨；门 `door_{idx}` 经 `slide_{idx}` PRISMATIC 沿 bank 宽 X 横移（bay0 -X、bay1 +X）clear bay opening。**采纳为 closure=sliding_door**。
- **roll_down_shutter**：`_build_slat_cq` CadQuery 波纹截面 slat；`shutter_{idx}` 部件在 `for i in range(N_SLATS)` 循环里发射 ~27 片 `slat_{idx}_{i}` + `curtain_strip_{idx}` 背带 + `handle_{idx}`；`slide_{idx}` PRISMATIC +Z 升入 `head_box_{idx}`，两侧 `guide_l/r_{idx}` 导轨。键盘移到 carcass 前面板（门不再承载）。**采纳为 closure=roll_down_shutter**。
- **perforated_mesh_panel**：门面换为整面满高 `door_mesh_{idx}` PerforatedPanelGeometry 冲孔板（覆盖 0.78W×0.74H），底部留号牌+键盘。**采纳为 door_surface=perforated_mesh_panel**。
- **horizontal_slot_vents**：`_door_slot_geometry` 助手发射 8 道细横缝 `door_slot_{idx}_{i}`（`for i in range(slot_count)` 等距列），上半门面。**采纳为 door_surface=horizontal_slot_vents**。
- **solid_smooth_door**：无孔实心门，门面 4 条 `rib_top/bot/left/right_{idx}` 加强肋边框（proud visual，parent visual 不动）。**采纳为 door_surface=solid_smooth_door**。
- **padlock_hasp**：门面 `hasp_bracket_{idx}` 托板 + `hasp_{idx}` REVOLUTE 铰式搭扣臂（绕 +X 翻起 0..90° 脱开/扣下），carcass 上 `staple_plate/leg_l/leg_r/bar_{idx}` 钉环 + `padlock_body_{idx}`/`shackle_leg_l/r_{idx}`/crown 黄铜挂锁（固定 visual 挂钉环）。**采纳为 latch=padlock_hasp**。
- **rotary_combo_dial**：门面 `dial_recess_{idx}` 凹座 + `dial_{idx}` KnobGeometry 滚花密码盘，`dialjoint_{idx}` REVOLUTE 绕面法向 +Y 自旋 0..2π。**采纳为 latch=rotary_combo_dial**。
- **bank_count_3** / **bank_count_4**：把 P1 的 bay 复制层改为 `_bay_center_x(i)=(i-(N_BAYS-1)/2)·LOCKER_W` + `for i in range(N_BAYS)` 单循环链，`range(N_BAYS-1)` 条 divider；其余 slot 不动。**采纳为 multiplicity bank_count 的 copied-object + range 循环契约**（N=3 / N=4 样本）。

冗余/分流说明：door_surface / latch 变体只在 parent 基础上替换门面或锁机构层，carcass / closure / multiplicity 不动；只换该层结构的差异被归入对应 slot 候选，纯尺寸/颜色差异不另列 candidate。

## 核心身份

钢制储物柜 / 更衣柜 / 储物柜阵列（steel storage locker bank）：一排并排直立的金属柜体，整 bank 居中于 x=0、坐地 z=0、门面朝前 +Y、沿 bank 宽度 +X 等距排列。每个 bay（~0.30W × 0.45D × 0.90H）由薄钢板 `carcass`（root：plinth 底座 + bay 间 divider + 每 bay back/side/top/bottom 板 + 内部 shelf）围成一个开口储物格，前方一扇门按某种机构开合（**主活动语义**）：

- **hinged_single_door**：单扇侧铰门，`hinge_{idx}` REVOLUTE 绕左竖边 +Z 外摆 0..100°。
- **double_leaf_doors**：每 bay 两窄扇，从中线各自 REVOLUTE 绕外缘对开（左 +Z / 右 -Z）。
- **sliding_door**：门 `slide_{idx}` PRISMATIC 沿 bank 宽 X 横移上下轨。
- **roll_down_shutter**：波纹卷帘 `shutter_{idx}` PRISMATIC +Z 逐片升入头箱，沿两侧导轨。

门面通风/表面结构可为：顶部小百叶（louver_vents）/ 整面冲孔板（perforated_mesh_panel）/ 多道细横缝（horizontal_slot_vents）/ 无孔实心带加强肋（solid_smooth_door）。锁/闩机构可为：循环按键键盘（keypad_buttons，PRISMATIC 内压）/ 铰式搭扣+挂锁（padlock_hasp，REVOLUTE 翻臂）/ 旋转密码盘（rotary_combo_dial，REVOLUTE 面法向自旋）。

默认成熟域：同一行 2..8 个并排 bay，每 bay 一扇门 + 一套锁机构，门面同款；金属漆面色板 10 套配色 × 显式 finish 表面工艺维度（off-white / battleship-grey / locker-blue / forest-green / tan-beige / gloss-red-enamel / brushed-stainless / galvanized-zinc / two-tone-grey-blue / weathered-scuffed，finish ∈ matte_powdercoat / gloss_enamel / brushed_metal / galvanized / two_tone_powdercoat / weathered_matte / wood_laminate；见 §「配色板 / Palette」，锚定 5★ RGBA，palette-only 不计 slot_choice）。每个门机构 **≥1 non-fixed joint**（满足真实 articulation），按键/搭扣/密码盘也有各自活动件。

不该混入：桌面纸/木收纳盒（`container_box`，小尺度无门机构）、ISO 米级钢运输集装箱（`container_shipping_container`，corner casting + 双开货柜门 + 波纹墙，单体非并排 bay 阵列、无键盘锁/百叶门）、敞口无门储物格架（无非-fixed joint，接近货架物）。

## 槽位 + 候选模块表

> **建模注记**：`carcass` 是 root 共享件（plinth/divider/per-bay 板/shelf），由 multiplicity 轴 `bank_count` 在 `for i in range(N)` 里逐 bay 发射。`closure_mechanism` / `door_surface` / `latch_mechanism` 三个 named slot 各自挂到每个 bay 的门或 carcass 前面（per-bay 复制时同一组合应用到所有 bay）。三个 slot 笛卡尔积 × bank_count 的 N 构成拓扑多样性（见 §9）。

### Slot A：closure_mechanism（**主开合机构槽**——锁门开合范式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·joint·helper 名 / 结构特征 |
|---|---|---|---|---|
| hinged_single_door（基线）| rec_a-bank-of-two-metal-...-d0776185（P1）| `_build_locker` L62-264；`door_{idx}` 面板 L121-130；`hinge_{idx}` REVOLUTE axis=(0,0,1) origin=左竖边 rim L208-222 | eligible if compatible | 单扇侧铰门绕左竖边 +Z 外摆 0..100°；门为 carcass 子，1 REVOLUTE/ bay |
| double_leaf_doors | rec_container_locker_var_double_leaf_doors | `_build_leaf` L65-250；左扇 axis=(0,0,1) L84 / 右扇 axis=(0,0,-1) L89；`hinge_{idx}_{leaf}` REVOLUTE L238-248 | eligible if compatible | 一 bay 两窄扇 `door_{idx}_0`/`door_{idx}_1`，各铰外缘从中线对开；2 REVOLUTE/ bay，键盘只在左扇 |
| sliding_door | rec_container_locker_var_sliding_door | `_build_track_rails` L80-102；`door_{idx}` L164-246；`slide_{idx}` PRISMATIC axis=(±1,0,0) origin=bay center L250-260 | eligible if compatible | 上下 `track_top/bottom_{idx}` 轨横移滑门；bay0 -X、bay1 +X 各自 clear opening；1 PRISMATIC/ bay |
| roll_down_shutter | rec_container_locker_var_roll_down_shutter | `_build_slat_cq` L84-106；`slat_{idx}_{i}` 循环 L195-202；`curtain_strip_{idx}` L208-213；`slide_{idx}` PRISMATIC axis=(0,0,1) L234-245；`guide_l/r_{idx}`+`head_box_{idx}` L156-172 | eligible if compatible | 波纹卷帘 `shutter_{idx}` 逐片（~27 `slat_{idx}_{i}`）升入头箱，沿两侧导轨；1 PRISMATIC +Z/ bay，键盘移到 carcass 前面板 |

硬约束记录：closure_mechanism 4 candidate（达 3-6 目标）。跨 REVOLUTE(铰门 +Z / 双开 ±Z) 与 PRISMATIC(横移 X / 卷帘升降 +Z) 两种 joint 拓扑 + 不同 part/joint count（hinged=1 door part、double=2 leaf part、sliding=1 door + carcass 轨、shutter=1 多-slat 循环 part + 头箱/导轨）。每 candidate ≥1 non-fixed joint。

### Slot B：door_surface（门面通风/表面结构——挂到门 part 或 carcass 前面的 visual 层）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·visual 名 / 结构特征 |
|---|---|---|---|---|
| louver_vents（基线）| rec_a-bank-of-two-metal-...-d0776185（P1）| `door_vent_{idx}` VentGrilleGeometry L132-159 + `door_plate_{idx}` L162-177 | eligible if compatible | 门面顶部小百叶格栅（VentGrilleSlats flat/down）+ 下方号牌；固定 visual 挂门 |
| perforated_mesh_panel | rec_container_locker_var_perforated_mesh_panel | `door_mesh_{idx}` PerforatedPanelGeometry(0.78W×0.74H) L133-164 + `door_plate_{idx}` L166-183 | eligible if compatible | 整面满高冲孔板覆盖门面，底留号牌+键盘区；固定 visual 挂门 |
| horizontal_slot_vents | rec_container_locker_var_horizontal_slot_vents | `_door_slot_geometry` L58-64；`door_slot_{idx}_{i}` `for i in range(8)` 等距列 L147-159 | eligible if compatible | 上半门面 8 道细横缝等距列（循环 Box 凹槽）；固定 visual 挂门 |
| solid_smooth_door | rec_container_locker_var_solid_smooth_door | `rib_top/bot/left/right_{idx}` 加强肋边框 L135-172 | eligible if compatible | 无孔实心门 + 四条 proud 加强肋边框（parent visual，无通风开口）；固定 visual 挂门 |

硬约束记录：door_surface 4 candidate（达 3-6 目标）。全为固定 visual（无独立 joint），改门面 mesh helper 与开孔形态（VentGrille / PerforatedPanel / 横缝循环 / 实心肋框）——真实门面结构家族差异，非纯装饰换色。注：shutter 门面由卷帘 slat 自身定义，door_surface 在 roll_down_shutter 下退化（见 §9 compatibility）。

### Slot C：latch_mechanism（锁/闩机构——各 bay 一套活动件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·joint 名 / 结构特征 |
|---|---|---|---|---|
| keypad_buttons（基线）| rec_a-bank-of-two-metal-...-d0776185（P1）| `lockpad_{idx}` L179-189；`lockbtn_{idx}_{n}` part + `btnjoint_{idx}_{n}` PRISMATIC axis=(0,-1,0) 双层 `for r/c in range` L224-264 | eligible if compatible | 门底 10 颗循环按键键盘，各 PRISMATIC -Y 内压 1.5mm；10 活动件/ bay（数量轴在内层循环固定 5×2）|
| padlock_hasp | rec_container_locker_var_padlock_hasp | `hasp_bracket_{idx}` L220-228；`hasp_{idx}` REVOLUTE axis=(1,0,0) L259-299；carcass `staple_plate/leg_l/leg_r/bar_{idx}` L301-342 + `padlock_body_{idx}`/`shackle_*_{idx}` L344-383 | eligible if compatible | 门面铰式搭扣臂绕 +X 翻起 0..90°（盖过 carcass 钉环），黄铜挂锁固定 visual 挂钉环；1 REVOLUTE/ bay + 固定锁体 |
| rotary_combo_dial | rec_container_locker_var_rotary_combo_dial | `dial_recess_{idx}` 凹座 L194-204；`dial_{idx}` KnobGeometry(knurled) L238-273；`dialjoint_{idx}` REVOLUTE axis=(0,1,0) 面法向 L278-292 | eligible if compatible | 门面凹座内旋转密码盘绕 +Y 自旋 0..2π；1 REVOLUTE/ bay |

硬约束记录：latch_mechanism 3 candidate（达下限 3）。含 PRISMATIC(keypad -Y) / REVOLUTE(hasp +X 翻臂) / REVOLUTE(dial +Y 面法向自旋) 三种 joint 拓扑 + 不同 part count（keypad 10 按键、hasp 1 臂+固定锁、dial 1 盘）。每 candidate ≥1 non-fixed joint。样本只支持这三族；主多样性由 closure_mechanism × bank_count 提供（见 §9）。

## 槽位图（slot graph）

pattern: mixed（`carcass` 为 root；门机构 / 门面 / 锁机构挂到每 bay；`bank_count` 一根 multiplicity 轴沿 +X 复制 bay）

```
carcass [ROOT, 坐地 z=0, 整 bank 居中 x=0]
  │  plinth(全宽) + dividers(range(N-1)) + 每 bay back/side_l/side_r/top/bottom/shelf
  │
  └── for i in range(bank_count):  bay_i @ cx=(i-(N-1)/2)·LOCKER_W   ← multiplicity 轴
        │
        ├── closure_mechanism (per-bay 门 part, 挂 carcass):
        │     hinged_single_door:
        │       carcass --[hinge_{i}: REVOLUTE +Z @ 左竖边 rim, z=H/2]--> door_{i}
        │     double_leaf_doors:
        │       carcass --[hinge_{i}_0: REVOLUTE +Z @ 左缘]--> door_{i}_0
        │       carcass --[hinge_{i}_1: REVOLUTE -Z @ 右缘]--> door_{i}_1
        │     sliding_door:
        │       carcass(+track_top/bottom_{i}) --[slide_{i}: PRISMATIC ±X @ bay center]--> door_{i}
        │     roll_down_shutter:
        │       carcass(+guide_l/r_{i}+head_box_{i}) --[slide_{i}: PRISMATIC +Z @ opening bottom]--> shutter_{i}(N_SLATS 循环)
        │
        ├── door_surface (固定 visual, 挂门 part [hinged/double/sliding] 或卷帘自带 [shutter]):
        │     louver_vents door_vent_{i} / perforated door_mesh_{i} / slots door_slot_{i}_{j} / solid rib_*_{i}
        │
        └── latch_mechanism (per-bay 活动件):
              keypad_buttons:
                door_{i} --[btnjoint_{i}_{n}: PRISMATIC -Y]--> lockbtn_{i}_{n}  (×10, 内层 for r/c)
              padlock_hasp:
                door_{i} --[hasp_{i}: REVOLUTE +X @ bracket]--> hasp_{i};  staple+padlock 固定 visual 挂 carcass
              rotary_combo_dial:
                door_{i} --[dialjoint_{i}: REVOLUTE +Y 面法向 @ dial center]--> dial_{i}
```

接口点位与 joint 语义：
- **closure 接口**：hinged/double 的 `hinge_*` origin 落在该 bay 门左/右竖边 rim `(cx∓DOOR_W/2, DOOR_FRONT_Y, H/2)`，axis ±Z REVOLUTE（q=0 闭合、正 q 外摆 ≤100°）；sliding 的 `slide_{i}` origin 在 bay center 门面 Y、mid-height，axis ±X PRISMATIC（q=0 盖住开口、正 q 横移 clear）；shutter 的 `slide_{i}` origin 在开口底中心 `(cx, CARCASS_FRONT_Y, OPENING_BOTTOM_Z)`，axis +Z PRISMATIC（q=0 闭合落下、正 q 升起入头箱）。门 part 与 carcass 前面有意小重叠（seated reveal）→ element-scoped `allow_overlap(door↔carcass)`；shutter slat 与 guide/head_box 有意重叠 → `allow_overlap(shutter↔carcass)`。
- **door_surface 接口**：固定 visual 挂门 front face（hinged/double/sliding 门 part 的 +Y 面）；roll_down_shutter 下门面由卷帘 slat 自身定义，door_surface 退化为 no-op（见 compatibility）。无独立 joint。
- **latch 接口**：keypad `btnjoint_{i}_{n}` origin 在门底 `lockpad_{i}` 面 `(bx, DOOR_TH/2+δ, bz)`，axis -Y PRISMATIC 内压；按键 base 嵌入锁板 → `allow_overlap(lockbtn↔door)`；hasp `hasp_{i}` origin 在门面 `hasp_bracket_{i}` `(DOOR_W-setback, DOOR_TH/2+δ, 0)`，axis +X REVOLUTE 翻臂（q=0 扣下盖过钉环、正 q 翻起脱开），padlock 锁体固定 visual 挂 carcass 钉环（`allow_overlap(padlock↔staple/crossbar)`）；dial `dialjoint_{i}` origin 在 `dial_recess_{i}` 中心门面，axis +Y(面法向) REVOLUTE 自旋 0..2π。
- **multiplicity 接口**：`bank_count` 沿 +X 等距复制整 bay（carcass 板件 + 门机构 + 门面 + 锁机构），`_bay_center_x(i)=(i-(N-1)/2)·LOCKER_W`；相邻 bay 共享 `divider`（range(N-1) 条），整 bank 居中 x=0，plinth 全宽。每 bay 独立 closure/latch joint，统一策略。
- **rest pose**：所有门 q=0 闭合（hinge 落座 / slide 盖住 / shutter 落下）；keypad 按键 q=0 不压；hasp q=0 扣下盖钉环；dial q=0；门面 visual / padlock 锁体固定。门外摆 / 横移 / 升降、按键内压、搭扣翻起、密码盘自旋为 viewer 目检的活动语义。
- **mating policy**：门罩/搭扣/卷帘的 seated 重叠为 captured / 友配（有意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 rim / hinge bracket / opening / dial 凹座）+ element-scoped `allow_overlap`（见各样本 run_tests 的 `ctx.allow_overlap`）。
- **互斥 / 可选**：closure_mechanism 各候选互斥（一 bay 一种门机构）；latch_mechanism 各候选互斥；door_surface 在 roll_down_shutter 下退化为 no-op（卷帘自带门面）。

## 每槽位 Module Emits / Interfaces

### root / carcass（共享件，由 bank_count 复制）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass`（root，visual: plinth + dividers(range(N-1)) + per-bay back/side_l/side_r/top/bottom/shelf）| P1 L75-115 / build L276-310；bank_count_4 `range(N_BAYS-1)` dividers L273-290 |
| internal joints | 无（root 本身无活动件）| — |
| upstream interface | 坐地 z=0、整 bank 居中 x=0（root）| P1 `_locker_center_x` L57-59 / bank_count `_bay_center_x` L58-60 |
| downstream interface | 每 bay 门 rim / opening（closure joint 的 parent 接口）+ 锁机构 mount 面 | P1 hinge origin L208-213 |

### Slot A / closure_mechanism（每候选发射对应活动门）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}`（+面板/号牌/handle）/ `door_{i}_0`+`door_{i}_1` / `door_{i}`+`track_*_{i}` / `shutter_{i}`(N_SLATS 循环)+`guide_*`/`head_box` | P1 L121-197 / double L65-250 / sliding L164-246 / shutter L109-281 |
| internal joints | `hinge_{i}` REVOLUTE +Z（hinged）/ `hinge_{i}_0`+`hinge_{i}_1` REVOLUTE ±Z（double）/ `slide_{i}` PRISMATIC ±X（sliding）/ `slide_{i}` PRISMATIC +Z（shutter）| P1 L208-222 / double L238-248 / sliding L250-260 / shutter L234-245 |
| downstream interface | 门 front face（承载 door_surface + latch）| P1 door panel L121-130 |

### Slot B / door_surface（固定 visual 挂门）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`door_vent_{i}` / `door_mesh_{i}` / `door_slot_{i}_{j}` / `rib_*_{i}` 为门 part 的固定 visual）| P1 L132-177 / mesh L133-164 / slots L147-159 / solid L135-172 |
| internal joints | 无 | — |

### Slot C / latch_mechanism（每候选发射活动锁件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lockbtn_{i}_{n}`(×10) / `hasp_{i}`(+staple/padlock 固定 visual 挂 carcass) / `dial_{i}`(+`dial_recess_{i}` 凹座 visual) | P1 L237-247 / hasp L260-383 / dial L238-273 |
| internal joints | `btnjoint_{i}_{n}` PRISMATIC -Y（keypad ×10）/ `hasp_{i}` REVOLUTE +X（hasp）/ `dialjoint_{i}` REVOLUTE +Y 面法向（dial）| P1 L251-263 / hasp L287-299 / dial L278-292 |
| upstream interface | 锁板/搭扣托板/凹座挂门 front face；padlock 锁体挂 carcass 钉环 | P1 lockpad L179-189 / hasp bracket+staple L220-342 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure_mechanism | enum | hinged_single_door / double_leaf_doors / sliding_door / roll_down_shutter | hinged_single_door | choice | deterministic procedural sampler 选 | Slot A 表 |
| door_surface | enum | louver_vents / perforated_mesh_panel / horizontal_slot_vents / solid_smooth_door | louver_vents | choice | sampler 选；roll_down_shutter 下退化 no-op | Slot B 表 |
| latch_mechanism | enum | keypad_buttons / padlock_hasp / rotary_combo_dial | keypad_buttons | choice | sampler 选 | Slot C 表 |
| bank_count | int (multiplicity) | [2, 8] | 2 | choice | 加权采样（小 N 偏多），见 §8 | source map Multiplicity / bank_count_3·4 |
| palette_style | enum | locker_offwhite / battleship_grey / locker_blue / forest_green / tan_beige / gloss_red_enamel / brushed_stainless / galvanized_zinc / two_tone_grey_blue / weathered_scuffed（**10 配色 × finish 维度**，见 §「配色板 / Palette」）| locker_offwhite | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)` | 各样本 material（见 §「配色板 / Palette」，锚定 5★ RGBA）|
| bank_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 LOCKER_H → hinge/slide/shutter origin z 同步，clamp | P1 LOCKER_H L37 |
| bay_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 LOCKER_W → DOOR_W / bay 间距 / slide 行程同步派生，clamp | P1 LOCKER_W L35 |
| door_width_scale | float | derived | 1.0 | equation | `DOOR_W = LOCKER_W·bay_width_scale - 2·HINGE_GAP`，不独立采样 | P1 L44 |
| slide_travel_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 sliding/shutter 生效；`SLIDE_DIST = LOCKER_W·...`、`SHUTTER_TRAVEL = (N_SLATS-4)·pitch·...`，clamp 保 clear-opening | sliding L57 / shutter L63 |
| hinge_open_limit | float (rad) | [80°, 110°] | 100° | independent | 缩放 hinge/hasp upper limit，clamp ≤110° 防穿邻 bay | P1 L221 / hasp L297 |
| keypad_press_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 BTN_PRESS 行程，clamp | P1 BTN_PRESS L52 |
| (—) | constraint | — | — | inequality | 横移 clear-opening：`SLIDE_DIST ≥ LOCKER_W`（滑门必须完全让开 opening），违反按比例回缩 slide_travel | sliding clear test L398-416 |
| (—) | constraint | — | — | inequality | 卷帘行程：`SHUTTER_TRAVEL ≤ N_SLATS·pitch`（不超过帘高，避免脱轨），违反回缩 | shutter L63 |
| (—) | constraint | — | — | inequality | 铰门不撞邻 bay：`hinge_open_limit·DOOR_W` 投影 ≤ bay 间隙容差（多 bay 时门外摆不与邻门干涉，仅 closed-pose QC 必过；open-pose 允许大幅外摆为活动语义）| double_leaf opposite-edge test L416-426 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`door_width_scale` 为 equation（DOOR_W 跟随 LOCKER_W）。`slide_travel_scale` 为 conditional（仅 sliding/shutter closure 生效）。scale 只动安全比例 / clearance / 行程 / 角度，绝不改 closure/door_surface/latch 拓扑或 bank_count multiplicity。

## 配色板 / Palette（palette_style，10 配色 × finish 维度）

> **palette only**：`palette_style` 是颜色/材质换皮轴，**不计入 slot_choice**、不改任何 slot/candidate/multiplicity/joint/dimension/topology。每 seed 单次 `rng.choice(PALETTE_STYLES)` 选一套配色，整 bank 统一应用（所有 bay 同配色）。每套 = 四组件颜色（carcass 柜体 / door 门 / latch·handle 锁闩把手 / accent 通风·号牌·点缀）+ 一个 **finish 表面工艺维度**（新增显式列）。工业写实，非霓虹。锚定 5★ 样本 RGBA（`locker_white` 0.90/0.90/0.88、`locker_grey` 0.62/0.64/0.66、`vent_dark` 0.18/0.19/0.21、`button_dark` 0.12/0.12/0.14、`steel_dark` 0.42/0.44/0.48、`padlock_brass` 0.72/0.58/0.22、`shutter_silver` 0.78/0.80/0.82、`channel_grey` 0.48/0.50/0.52、`dial_gunmetal` 0.22/0.23/0.26），其余为写实推断色。

finish 维度（表面工艺）取值：`matte_powdercoat`（哑光粉末喷涂）/ `gloss_enamel`（亮光搪瓷漆）/ `brushed_metal`（拉丝金属）/ `galvanized`（热镀锌花纹）/ `two_tone_powdercoat`（双色粉喷）/ `weathered_matte`（做旧哑光带刮痕脏化）/ `wood_laminate`（木纹贴面）。

| # | palette_style | carcass 柜体 rgba | door 门 rgba | latch/handle 锁闩·把手 rgba | accent 通风·号牌·点缀 rgba | **finish 表面工艺** | 锚定 / 说明 |
|---|---|---|---|---|---|---|---|
| 1 | `locker_offwhite`（基线/默认）| (0.90, 0.90, 0.88, 1.0) | (0.90, 0.90, 0.88, 1.0) | (0.12, 0.12, 0.14, 1.0) | (0.18, 0.19, 0.21, 1.0) | `matte_powdercoat` | 锚 5★ `locker_white`/`button_dark`/`vent_dark`；经典米白哑光粉喷储物柜 |
| 2 | `battleship_grey` | (0.62, 0.64, 0.66, 1.0) | (0.56, 0.58, 0.60, 1.0) | (0.12, 0.12, 0.14, 1.0) | (0.18, 0.19, 0.21, 1.0) | `matte_powdercoat` | 锚 5★ `locker_grey`；战舰灰柜体+略深灰门，工厂/车间常见 |
| 3 | `locker_blue` | (0.78, 0.79, 0.80, 1.0) | (0.20, 0.34, 0.55, 1.0) | (0.14, 0.15, 0.17, 1.0) | (0.62, 0.64, 0.66, 1.0) | `matte_powdercoat` | 浅灰柜体+储物蓝门（学校/健身房储物柜），accent 取 `locker_grey` |
| 4 | `forest_green` | (0.80, 0.80, 0.78, 1.0) | (0.20, 0.34, 0.24, 1.0) | (0.14, 0.15, 0.16, 1.0) | (0.48, 0.50, 0.52, 1.0) | `matte_powdercoat` | 米灰柜体+森林绿门（工业/军用），accent 取 `channel_grey` |
| 5 | `tan_beige` | (0.82, 0.76, 0.64, 1.0) | (0.74, 0.67, 0.54, 1.0) | (0.30, 0.27, 0.22, 1.0) | (0.42, 0.44, 0.48, 1.0) | `matte_powdercoat` | 米黄/沙褐柜体+门（办公/政府机构），accent 取 `steel_dark` |
| 6 | `gloss_red_enamel` | (0.88, 0.88, 0.86, 1.0) | (0.62, 0.14, 0.13, 1.0) | (0.15, 0.15, 0.16, 1.0) | (0.20, 0.21, 0.23, 1.0) | `gloss_enamel` | 白柜体+亮光搪瓷红门（消防/急救/安全柜识别色），高光泽 |
| 7 | `brushed_stainless` | (0.70, 0.71, 0.73, 1.0) | (0.74, 0.75, 0.77, 1.0) | (0.42, 0.44, 0.48, 1.0) | (0.55, 0.57, 0.59, 1.0) | `brushed_metal` | 整体拉丝不锈钢（实验室/食品/医疗），锚 `shutter_silver`/`steel_dark`/`channel_grey` |
| 8 | `galvanized_zinc` | (0.66, 0.68, 0.70, 1.0) | (0.72, 0.74, 0.75, 1.0) | (0.40, 0.41, 0.44, 1.0) | (0.50, 0.52, 0.54, 1.0) | `galvanized` | 热镀锌冷灰带锌花（户外/仓储），锚 `shutter_silver`/`channel_grey` |
| 9 | `two_tone_grey_blue` | (0.60, 0.62, 0.64, 1.0) | (0.26, 0.38, 0.52, 1.0) | (0.12, 0.12, 0.14, 1.0) | (0.84, 0.85, 0.86, 1.0) | `two_tone_powdercoat` | 双色粉喷：深灰柜体+钢蓝门+浅银号牌点缀（商业储物间）|
| 10 | `weathered_scuffed` | (0.58, 0.57, 0.54, 1.0) | (0.50, 0.49, 0.46, 1.0) | (0.16, 0.16, 0.17, 1.0) | (0.34, 0.30, 0.24, 1.0) | `weathered_matte` | 做旧刮痕：旧灰柜体/门 + 锈褐脏化 accent（陈旧车间/旧厂房），暗哑光带磨损 |

> finish 表面工艺为颜色/材质语义说明（粗糙度/金属度/光泽倾向），由模板在 `model.material(...)` 上以对应 rgba + 注释体现；**不引入新 part/joint/几何**。realistic 推断色（locker_blue/forest_green/tan_beige/gloss_red/brushed/galvanized/two_tone/weathered）均落在工业写实区间（无饱和霓虹），且每套都复用至少一处 5★ 锚定 RGBA 作 carcass 或 accent。finish 维度另含 `wood_laminate`（木纹贴面 carcass≈(0.55,0.40,0.26,1.0)、door≈(0.62,0.46,0.30,1.0)、latch≈(0.20,0.14,0.10,1.0)、accent≈(0.42,0.44,0.48,1.0)，finish=`wood_laminate`）作为第 7 种 finish 工艺示例——可作为 `wood_laminate` 配色挂接到 carcass，保持 palette-only（仅换 `model.material` 的 rgba + finish 注释，不增 part/joint/几何）。

## Multiplicity / Copy Logic

本小类有 **1 根 multiplicity 轴**：

- `count_param`：`bank_count`（同一行并排 locker bay 数）
- `N_range`：`[2, 8]`（产品域；样本覆盖 N∈{2(P1), 3, 4}，模板采样域大于样本覆盖正常）
- sampling domain（权重档）：小 N 高频、大 N 稀有。建议 `2:0.30, 3:0.25, 4:0.18, 5:0.12, 6:0.08, 7:0.04, 8:0.03`（归一化）；sweep 测试偏小（N≤4 多采），产品全程 [2,8] 都合法（结构按 `range(N)` 复制天然安全）。
- copied object：整个 bay = `carcass` 板件（back/side_l/side_r/top/bottom/shelf）+ 一套 closure_mechanism 门 + door_surface 门面 + latch_mechanism 锁机构。
- naming：`door_{i}` / `hinge_{i}`（或 `door_{i}_{leaf}` / `slide_{i}` / `shutter_{i}` 按 closure）；锁件 `lockbtn_{i}_{n}` / `hasp_{i}` / `dial_{i}`；carcass 板件 `back_{i}` 等；bay 间 `divider`（`range(N-1)` 条）。
- placement：沿 bank 宽 +X 等距排列，`_bay_center_x(i)=(i-(N-1)/2)·LOCKER_W`，整 bank 居中 x=0，plinth 全宽 `N·LOCKER_W`。
- joint policy：每 bay 一套独立 closure joint（REVOLUTE 或 PRISMATIC）+ 各自 latch joint（PRISMATIC/REVOLUTE）；同一 bank 内所有 bay 用同一 (closure, door_surface, latch) 组合（统一外观），不混搭。
- source/gating：母资产 §4 可读性契约——bay 复制必须用 `for i in range(bank_count)` 单循环链（非手写元组 `for idx in (0,1)`），dividers 用 `range(N-1)`，见 bank_count_3 / bank_count_4 样本。模板 sampler 内部仅做 1 次 bank_count 加权采样，编入 slot_choices。

## 拓扑多样性审计

总组合数：closure_mechanism(4) × door_surface(4) × latch_mechanism(3) × bank_count(N∈[2,8]=7) = 4 × 4 × 3 × 7 = **336**。
（door_surface 在 roll_down_shutter 下退化 → closure=shutter 时 door_surface 不增量；保守去重后 slot 组合 ≈ (3 closure × 4 surface + 1 shutter) × 3 latch = 13 × 3 = 39 distinct 门面×机构×锁，再 × 7 N = 273。无论按哪种口径都 ≫ 10。）

仅 closure(4) × latch(3) = **12 ≥ 10** 已可过门控；叠 door_surface 与 bank_count 后充裕。

理由：closure 跨 REVOLUTE(铰门 +Z / 双开 ±Z 2 leaf part) 与 PRISMATIC(横移 X / 卷帘升降 +Z N-slat 循环 part) 两类 joint 拓扑 + 不同 part/joint count；latch 跨 PRISMATIC(keypad 10 按键) / REVOLUTE(hasp 翻臂 +X) / REVOLUTE(dial 面法向 +Y) 三类；bank_count 改 part-tree 宽度（N bay × (carcass 板 + 门 + 锁) + (N-1) divider）是真实结构 multiplicity。door_surface 改门面 mesh 组（VentGrille / PerforatedPanel / 横缝循环 / 实心肋框）。这些都是 part tree / joint topology / chain count 的真实差异，非纯尺寸/颜色。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 依次 (1) `rng.choices` 加权采 `bank_count`（小 N 偏多），(2) `rng.choice` closure_mechanism，(3) door_surface（若 closure=roll_down_shutter 则强制 no-op / 占位 louver 等价），(4) latch_mechanism，(5) uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-4 → 0-19 → 0-49 分阶段；viewer 目检 seeds 0-9（覆盖各 closure × 小 N）。

Topology target：1000-seed slot choice tuple distinct 预计接近 39 slot-组合 × 多个 N 档 ≈ 100+（slot 组合 39 × bank_count 7 = 273 理论上限，加权后实采 distinct 受 closure×latch×N 主导）。受真实词汇表约束的轴是 latch(3)，但 closure(4) × door_surface(4) × N(7) 已撑开足够。低于 300 时原因：本小类真实结构词汇就是 4 closure × 4 surface × 3 latch × N，是该类目合理域，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §7 的连续 scale（bank_height_scale / bay_width_scale → door_width_scale equation / slide_travel_scale conditional / hinge_open_limit / keypad_press_scale）。全部 `resolve_config` clamp + 每 build 统一应用。clear-opening / 卷帘行程 / 不撞邻 bay 三条不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（门 rim / opening / bay center）、滑门 clear-opening、卷帘脱轨界、锁机构 mount 面或类别身份；也不改 bank_count multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权采 bank_count → `rng.choice` closure/door_surface/latch → uniform scale + palette | slot_choices_for_seed 含四轴(closure,door_surface,latch,bank_count)且与 build 一致 |
| compatibility matrix | (1) closure=roll_down_shutter → door_surface 退化 no-op（卷帘自带门面，不再叠门面 visual，避免双层穿模）；resolve 把 door_surface 归一为占位，不 gate 掉 N/latch。(2) latch=keypad 在 shutter 下挂到 carcass 前面板（非门，门是卷帘），其余 closure 挂门；resolve 按 closure 决定 latch parent。(3) latch=padlock_hasp / rotary_combo_dial 需门面有锁区——sliding/hinged/double 门均可；shutter 下 hasp/dial 挂 carcass 前面板（搭扣扣 carcass 钉环、dial 在前面板凹座）。(4) double_leaf 键盘只在左扇（沿用样本）。(5) 各 closure 互斥、各 latch 互斥。(6) bank_count 与任意 slot 正交（按 range(N) 复制同组合）。无硬 gate-out（组合全合法，只在 resolve 派生 parent / 占位 / 尺寸适配）| 无 floating / collision / 门穿邻 bay / 卷帘脱轨 / latch origin 错位 / 双层门面穿模 |
| controlled local variation | 6 个 clamped/derived scale，每 build 统一；door_width equation 跟随 bay_width；slide_travel conditional 仅滑门/卷帘 | 比例变化不破坏 closure joint origin / clear-opening / 坐地 / 类别身份 / bank_count |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-4 初轮 / 0-19 / 0-49 分阶段；0-999 成熟审计 | 门动作 / 坐地 / overlap / 多 bay clear QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| closure_mechanism | 4 | yes | yes | hinged(REV +Z) / double(REV ±Z, 2 leaf) / sliding(PRIS ±X) / shutter(PRIS +Z, N-slat) |
| door_surface | 4 | yes | yes | louver / perforated / horizontal slots / solid 肋框（shutter 下退化）|
| latch_mechanism | 3 | yes | yes | keypad(PRIS -Y ×10) / hasp(REV +X 翻臂) / dial(REV +Y 自旋)|
| bank_count (multiplicity) | N∈[2,8] | yes | yes | 加权采样，小 N 偏多；range(N) 复制契约 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (closure_mechanism, door_surface, latch_mechanism, bank_count) 四轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（bank_count 加权 + 三 slot rng.choice）
- `resolve_config` 各 scale clamp 到声明范围；door_width equation 跟随 bay_width；slide_travel conditional 仅 sliding/shutter；clear-opening / 卷帘行程 / 不撞邻 bay 三不等式在 resolve 投影/回缩
- compatibility matrix / gating：roll_down_shutter 下 door_surface 退化 no-op、latch parent 按 closure 决定（门 vs carcass 前面板）；其余组合全合法（无硬 gate-out）
- 连续 scale clamp 后不破坏 closure joint origin / clear-opening / 坐地 / 类别身份 / bank_count multiplicity
- 关键 joint：hinged `hinge_{i}` REVOLUTE +Z (abs(axis[2])>0.99)；double `hinge_{i}_0/1` REVOLUTE ±Z 对开；sliding `slide_{i}` PRISMATIC ±X (abs(axis[0])>0.99)；shutter `slide_{i}` PRISMATIC +Z；keypad `btnjoint_{i}_{n}` PRISMATIC -Y；hasp `hasp_{i}` REVOLUTE +X (abs(axis[0])>0.99)；dial `dialjoint_{i}` REVOLUTE +Y 面法向
- multiplicity：bay 复制用 `for i in range(bank_count)` 单循环、dividers `range(N-1)`、`_bay_center_x` 居中 x=0
- captured-fit：element-scoped `allow_overlap(door↔carcass)` 门 seated reveal；`allow_overlap(shutter↔carcass)` slat 入 guide/head_box；`allow_overlap(lockbtn↔door)` 按键嵌锁板；`allow_overlap(padlock↔staple)` 锁体挂钉环
- grandfather：门罩/搭扣/卷帘 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用单体桌面盒占位体当 locker，或丢掉 carcass 共享件 / bank 阵列 → 失类别身份；locker 必须有并排 bay carcass + 门机构。
- closure joint origin 放在 carcass 任意点而非门左竖边 rim / bay center / 开口底 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 滑门 `SLIDE_DIST < LOCKER_W` 不完全让开 opening，或卷帘 `SHUTTER_TRAVEL` 超帘高脱轨 → clear-opening / 行程不等式 FAIL。
- closure rest pose 设成张开 / 抬起而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- roll_down_shutter 下又叠一层 door_surface 门面 visual（双层穿模），或没把 latch parent 切到 carcass 前面板 → compatibility 违规、穿模/origin 漂移。
- bay 复制用手写元组 `for idx in (0,1)` 而非 `for i in range(bank_count)`，或 dividers 数 ≠ N-1 → multiplicity 契约 FAIL（§4 可读性）。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 门外摆 / 横移 / 升降时穿邻 bay 壁或 origin 漂移、按键不沿 -Y 内压、密码盘轴不沿面法向 → joint 轴/origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_box（桌面纸/木收纳盒）**——理由：box 是小尺度桌面单体，无门开合机构、无并排 bay 阵列、无键盘/挂锁；locker 是地面钢柜阵列 + 门机构 + 锁。
- 不该混入：**container_shipping_container（ISO 钢运输集装箱）**——理由：shipping_container 是米级单体货柜（corner casting + 波纹墙 + 双开货柜门 + 锁杆），无并排 locker bay、无键盘锁/百叶门/密码盘；locker 是室内储物柜阵列。
- 不该混入：**cabinet（通用橱柜）**——理由：cabinet 多为木质带抽屉/隔板的家具柜；locker 的身份是钢制储物柜阵列 + 通风门面 + 安防锁机构（keypad/padlock/dial）+ bank_count 多 bay 复制。借用 cabinet 的 door/compartment 词汇但不混入抽屉/木家具语义。
- 不该混入：**敞口无门储物格架（货架）**——理由：货架无非-fixed joint（纯固定隔板），locker 必须有 ≥1 门活动机构 + 锁。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。读全 11 样本（1 parent + 10 变体）。4 closure × 4 door_surface × 3 latch × bank_count N[2,8] = 336（保守去重 273）；closure×latch=12 已过 。closure 跨 REVOLUTE/PRISMATIC，latch 跨 PRISMATIC/REVOLUTE 两轴；bank_count 单 multiplicity 轴（range(N) 复制 + N-1 dividers，§4 可读性已在 bank_count_4 修）。roll_down_shutter 下 door_surface 退化 no-op + latch 切 carcass 前面板（compatibility gate）。palette_style 扩为 **10 套协调配色 × 显式 finish 表面工艺维度**（matte_powdercoat / gloss_enamel / brushed_metal / galvanized / two_tone_powdercoat / weathered_matte / wood_laminate），每套 = carcass/door/latch·handle/accent 四组件色 + finish；锚定 5★ RGBA（locker_white/locker_grey/vent_dark/button_dark/steel_dark/padlock_brass/shutter_silver/channel_grey/dial_gunmetal），其余写实推断（工业写实非霓虹）；palette-only，不计 slot_choice、不改任何 slot/candidate/multiplicity/joint/dimension/topology。待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_carcass_bay_panels(carcass, cx, i)`（back/side/top/bottom/shelf）+ `_bay_center_x(i, N)` + `_door_panel(...)` 全 module 公用；closure 各 module 一个 factory（`_make_hinged_door` / `_make_double_leaf` / `_make_sliding_door` / `_make_shutter`），door_surface 一个 `_apply_door_surface(door, surface, ...)`，latch 一个 `_apply_latch(parent, latch, ...)`。
- closure=roll_down_shutter：slat 用 `_build_slat_cq` CadQuery 波纹截面 + `for i in range(N_SLATS)` 循环发射到单 `shutter_{i}` part；door_surface 在此 closure 下短路为 no-op。
- latch parent 切换：`resolve_config` 按 closure 决定 latch 挂点——hinged/double/sliding 挂门 part；shutter 挂 carcass 前面板（参照 shutter 样本 keypad-on-carcass L247-281）。
- multiplicity：bay 复制必须 `for i in range(bank_count)` 单循环 + `range(bank_count-1)` dividers（参照 bank_count_4 L273-290）；sampler 内部 1 次加权 bank_count 采样。
- captured-fit overlap：`run_container_locker_tests` 里复制各样本的 `ctx.allow_overlap`（door↔carcass seated reveal、shutter↔carcass guide/head_box、lockbtn↔door 锁板、padlock↔staple 钉环）。
- 参考模板：`container_jar.py`（Config/ResolvedConfig + config_from_seed + resolve_config clamp + slot_choices + run_tests allow_overlap + element-scoped grandfather 骨架）；带 multiplicity 的模板（如 fence_cascade / 模块化 N 轴模板）参考 bank_count 加权采样 + range(N) 复制 + N-1 dividers。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root/A/B/C/mult | carcass + hinged_single_door + louver_vents + keypad_buttons + bank_count=2 | rec_a-bank-of-two-metal-...-d0776185（P1）| `_build_locker` L62-264 / `hinge_{idx}` L208-222 / `door_vent_{idx}` L132-159 / `btnjoint_{idx}_{n}` L251-263 / build loop L300-310 | carcass 共享件 + 铰门基线 + 百叶门面基线 + 键盘锁基线 + multiplicity 基线 |
| S2 | A | double_leaf_doors | rec_container_locker_var_double_leaf_doors | `_build_leaf` L65-250 / `hinge_{idx}_{leaf}` REVOLUTE ±Z L238-248（axis L84/89）| 一 bay 两窄扇对开 |
| S3 | A | sliding_door | rec_container_locker_var_sliding_door | `_build_track_rails` L80-102 / `slide_{idx}` PRISMATIC ±X L250-260 | 上下轨横移滑门 |
| S4 | A | roll_down_shutter | rec_container_locker_var_roll_down_shutter | `_build_slat_cq` L84-106 / `slat_{idx}_{i}` 循环 L195-202 / `slide_{idx}` PRISMATIC +Z L234-245 / guide+head_box L156-172 | 波纹卷帘升入头箱 |
| S5 | B | perforated_mesh_panel | rec_container_locker_var_perforated_mesh_panel | `door_mesh_{idx}` PerforatedPanelGeometry L133-164 | 整面满高冲孔板门面 |
| S6 | B | horizontal_slot_vents | rec_container_locker_var_horizontal_slot_vents | `_door_slot_geometry` L58-64 / `door_slot_{idx}_{i}` 循环 L147-159 | 多道细横缝等距列 |
| S7 | B | solid_smooth_door | rec_container_locker_var_solid_smooth_door | `rib_top/bot/left/right_{idx}` L135-172 | 无孔实心门 + 加强肋边框 |
| S8 | C | padlock_hasp | rec_container_locker_var_padlock_hasp | `hasp_{idx}` REVOLUTE +X L259-299 / staple L301-342 / `padlock_body_{idx}`+shackle L344-383 | 铰式搭扣 + 黄铜挂锁 |
| S9 | C | rotary_combo_dial | rec_container_locker_var_rotary_combo_dial | `dial_{idx}` KnobGeometry L238-273 / `dialjoint_{idx}` REVOLUTE +Y L278-292 | 凹座旋转密码盘 |
| S10 | mult | bank_count (N=3/4 range 循环) | rec_container_locker_var_bank_count_3 / _4 | `_bay_center_x(i)` L58-60 / `for i in range(N_BAYS)` 复制 / `range(N_BAYS-1)` dividers（bank_count_4 L273-290）| multiplicity range(N) 复制契约 + N-1 dividers |
