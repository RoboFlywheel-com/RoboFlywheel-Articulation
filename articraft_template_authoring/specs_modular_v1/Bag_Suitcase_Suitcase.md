# Bag_Suitcase / Suitcase — Modular Spec

> 来源小类：`picture/Bag_Suitcase/Suitcase/001.png`（articraft_data 上游复古硬箱小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Bag_Suitcase__Suitcase.md`。
> **本类别 = 复古皮硬箱式手提行李箱（vintage hard-sided travel suitcase）**：矩形单体箱壳（body）+ 后铰翻盖（lid）+ 前部闭合机构 + 提把 + 护角/包边加固 + 可选盖型 + 可选内部打包托盘。**与同大类 `bag_suitcase_box`（板条木箱 / chest）是不同小类**：本类是皮硬壳、有提把和前闭合扣件、盖永远后铰 REVOLUTE 翻起。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（1 parent + 6 fork 槽位变体）已在本仓库 `data/records/`。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一全文核对）。引用以 part / joint / helper **名字**为准；行号仅作定位。
>
> **代码核查要点（与 source map 不一致处，以代码为准）**：
> - source map 的 multiplicity「band_count / cap_count（护角固定 8；包边条 [2,6]）」与代码**不符**。edgeband 实测是**固定 12 条边的包边**（`edges` 列表恒 12 项，`n = len(edges)`，`for i in range(n)`，见 edgeband L108-144），corner_caps 是**固定 8 个护角**（4 body + 4 lid，双重 `for sx/sy` 各 4，见 parent L73-92 + L195-210）。两者都是 **module 内部固定数量的局部循环**，**不是模板级可变 N 复制轴**，数量不进 slot_choice、不加权采样。→ 本模板**无 multiplicity 轴**（见 §8）。
> - latch / buckle / zipper 是**互斥的前闭合机构**（同一根 closure slot 三选一），不是「latch + buckle + zipper 并存」。

## 元信息
| 项 | 值 |
|---|---|
| slug | `suitcase` |
| template path | `agent/templates/Bag_Suitcase_Suitcase.py` |
| test path (optional) | `tests/agent/test_suitcase_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: closure_mechanism + handle_system + reinforcement + lid_profile + internal_structure，各自挂到共同 `suitcase_body` 根；主活动轴 = 后铰 lid_hinge REVOLUTE，恒在；无 multiplicity）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent `cb7b4d8c` + 6 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only，category_slug=bag_suitcase）|
| read_count | 7（**全部读完整 `model.py` + run_tests**，不抽样；含每个样本 build helpers、part 树、articulation、allow_overlap 段）|
| read_scope | this explicit 5★ list（parent + buckle + zipper + folding_handle + edgeband + dome_trunk + lift_tray）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳 |

阅读要点（用于槽位分解）：
- **parent（基线）**：`suitcase_body`（root，皮硬壳 `_add_box_shell` floor+4 wall + 8 护角 `_add_corner_caps` + 竖向 trim 带 + 前面提把 rope grip + 前面 latch 铰座 bosses）；`suitcase_lid`（child，后铰平盖 + 4 lid 护角 + trim 带），单 `lid_hinge` REVOLUTE（axis=(-1,0,0)，origin=(0,D/2,HB)）后铰翻盖；两 `latch_left/right` part（REVOLUTE axis=(+1,0,0)，挂在 body 前面，q=0 直立闭合，翻下释放）。W=0.46/D=0.34/HB=0.085/HL=0.075/T=0.012。
- **closure 轴（Slot A）**：buckle（两条皮带扣，`strap_tongue_{i}` ×2 REVOLUTE axis=-X 扣舌翻转，+ body 侧 lower strap/buckle frame/lid 侧 upper strap visual，**无 latch**）/ zipper（沿周三段拉链 tape+teeth，`zipper_slider` 单 PRISMATIC axis=+X 沿前面滑，**唯一 PRISMATIC 主拓扑**，**无 latch**）相对 latches（2×REVOLUTE）是真正的 joint 拓扑变化。三者互斥（同一前闭合位置）。
- **handle 轴（Slot B）**：folding_handle（`folding_handle` 独立 part，`handle_fold` REVOLUTE axis=-X 折叠收倒，parent=**lid**，含 pivot 摆臂 + 木 grip + pivot rod + lid 上 mount 托座）相对 fixed_top_grab（rope grip 圆柱 + 两 loop，**无 joint，parent visual**）是 part 数 / joint 拓扑变化。
- **reinforcement 轴（Slot C）**：edge_banding（`_add_edge_banding` 沿 12 条边包黄铜箍条，body 12 + lid 12，**固定 12 循环**）相对 corner_caps（8 金属护角块，**固定 8 循环**）是表面加固 visual 族变化；二者都无独立 joint（Rule 1 inline 到 body/lid visual）。
- **lid_profile 轴（Slot D）**：dome_trunk（cadquery barrel-vault 圆顶 `_build_dome_shell` + 两侧 `_build_dome_endwall` 封口 + 黄铜环带 + 皮带，lid 用 mesh 而非 box 平盖）相对 flat（平盖 box 壳）是 lid mesh / primitive 拓扑变化（cadquery mesh vs Box）。
- **internal_structure 轴（Slot E）**：lift_tray（`packing_tray` 独立 part，`tray_hinge` REVOLUTE axis=-X 内部打包托盘掀起露下层腔，parent=body，tray 尺寸已 clear 8 护角内面、低侧壁、parent body trim 带已移除避免穿托盘）相对 open（无内部件，直接箱腔）是 part 数 / joint 拓扑变化。

## 核心身份

一只**复古皮硬箱式手提行李箱**（vintage hard-sided travel suitcase）：一个矩形单体硬壳箱体（`suitcase_body`，皮革面 + 金属护角或黄铜包边），上接一只**后铰翻盖**（`suitcase_lid`，恒 `lid_hinge` REVOLUTE，axis=-X，origin 在后顶边铰线，q=0 盖合在 body rim 留 ~1.5mm seam gap，正 q 抬前缘上翻）。前部有**一个互斥的闭合机构**（金属搭扣 latch 双翻片 / 皮带扣 buckle 双扣舌 / 沿周拉链 zipper 滑头）——这是身份核心之一。前面有**提把**（固定木 grip 绳把 / 折叠提把），箱体可用**护角或黄铜包边**加固，盖可为**平盖或圆顶 trunk 盖**，内部可有**掀起式打包托盘**。默认成熟域：W≈0.46 / D≈0.34 / 闭合高 H≈0.16 m 的单体硬箱，恒有后铰 lid_hinge（REVOLUTE）+ 至少一个前闭合机构关节（latch REVOLUTE / buckle tongue REVOLUTE / zipper slider PRISMATIC）。

不该混入：
- **板条木箱 / 储物 chest（同大类 `bag_suitcase_box`）**——板条侧壁 + 多种 lid_closure（下翻 / 双叶 / 滑顶 / 立门 / 拱顶），无提把语义、无前皮带扣 / 拉链闭合、不是皮硬壳后铰翻盖单一形态；本类的盖恒后铰 REVOLUTE 翻起，前部恒有提把 + 闭合扣件。
- **软包行李袋 / Luggage bag（同大类 Bag_Suitcase / Luggage）**——软体包 + 拉杆 + 万向轮 + 拉链主体，主运动是伸缩拉杆 + 滚轮；本类是静置硬壳、无 telescoping 拉杆 + 轮轴。
- **珠宝盒 / 藏宝箱（treasure chest）**——虽同为后铰翻盖小盒，但藏宝箱是拱顶木箱 + 锁扣的储物身份、无手提行李语义（提把 + 旅行护角 + 皮带 / 拉链闭合）；本类身份在于「可手提的旅行硬箱」。

## 槽位 + 候选模块表

> **建模注记**：5 个 slot 不是串联链——`closure_mechanism` / `handle_system` / `reinforcement` / `lid_profile` / `internal_structure` 都把自己的 part/visual 挂到**共同的 `suitcase_body` 根**（或其 `suitcase_lid` child）（parallel_children）。**恒在的主活动轴是 `lid_hinge`（REVOLUTE，后铰翻盖）**，它不是 slot——所有 module 都共享同一根后铰 lid。各 slot 各自贡献 0–N 个独立子件（closure 的 latch/tongue/slider、handle 的 fold、internal 的 tray）或纯 visual（handle rope、reinforcement caps/bands、lid_profile dome mesh）。slot 之间通过共享 `suitcase_body` / `suitcase_lid` 的 mating face（前面 / 顶 rim / 棱边 / 内腔）装配。

### Slot A：closure_mechanism（前闭合机构 —— **互斥三选一**，决定前闭合子件的 part 树与 joint 拓扑；后铰 lid_hinge 恒在不变）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| latches（基线） | parent `cb7b4d8c` | L232-260（latch parts + 2×REVOLUTE）+ L138-151（body latch bosses）| eligible if compatible | 两 `latch_left/right` part，各 REVOLUTE axis=(+1,0,0)、origin=(±LATCH_X, 前面 latch_y, HB-0.018)，q=0 直立扣合跨 seam、正 q 翻下释放（lower=0/upper=1.4）；body 前面 `latch_boss_{side}` 铰座 |
| buckle_straps | rec_suitcase_var_buckle | L326-358（`strap_tongue_{i}` ×2 + 2×REVOLUTE）+ `_add_buckle_frame` L108-152 + body straps/bosses/frame L199-233 + lid upper straps L300-313 | eligible if compatible | 两 `strap_tongue_{i}` part，各 REVOLUTE axis=(-1,0,0)、origin=(±STRAP_X, BUCKLE_CY, HB)，扣舌绕 buckle center bar 翻转释放（lower=0/upper=1.4）；body 侧 lower_strap + buckle frame（top/bottom/left/right/center bar）+ mount bosses，lid 侧 upper_strap 跨 seam；**无 latch** |
| zipper_perimeter | rec_suitcase_var_zipper | L342-398（`zipper_slider` part + PRISMATIC）+ `_add_zipper_track` L105-180 + body/lid track L228-245/L312-329 + allow_overlap L492-505 | eligible if compatible | 单 `zipper_slider` part，PRISMATIC axis=(1,0,0)、origin=(-ZIP_TRAVEL/2, -(D/2), HB)，沿前面滑（lower=0/upper=ZIP_TRAVEL≈0.36）；body+lid 各三段 `zip_tape_{i}`/`zip_teeth_{i}`（front/left/right）沿 seam 上下分布；slider body 含 channel/bail/pull_tab/end_stop；teeth↔slider element-scoped allow_overlap；**唯一 PRISMATIC 主拓扑**，**无 latch** |

### Slot B：handle_system（提把 —— 挂到 body 前面 或 lid 顶面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_top_grab（基线） | parent `cb7b4d8c` | L121-136（handle_grip cylinder + 两 handle_loop）| eligible if compatible | 前面木 `handle_grip` 圆柱（radius=0.012,len=0.16，水平 rpy）+ 两 `handle_loop_{l/r}` 皮 loop；**无 joint，parent visual** |
| folding_handle | rec_suitcase_var_folding_handle | L248-282（`folding_handle` part + `handle_fold` REVOLUTE）+ `_add_handle_arm` L107-114 + lid pivot mounts L225-234 + allow_overlap L333-347 | eligible if compatible | `folding_handle` 独立 part（两 `handle_arm_{i}` 摆臂 + `handle_pivot_rod` 轴 + 木 `handle_grip`），`handle_fold` REVOLUTE axis=(-1,0,0)、parent=**lid**、origin=(0,-D/2,HL+HANDLE_PIVOT_Z)，q=0 平贴 lid 顶 / 正 q 立起提（lower=0/upper=1.3）；lid 顶 `handle_pivot_mount_{i}` ×2 托座；pivot rod↔mount captured-pin allow_overlap |

> **2-candidate 说明**：handle_system 仅 2 个 candidate（fixed_top_grab + folding_handle）。本批 5★ 源池中无第三种提把结构（无侧提把 / 无伸缩拉杆——伸缩拉杆属相邻 Luggage bag 类，见边界）。符合 SPEC_TEMPLATE §4「样本池不足时可降到 2，但必须说明理由」：源池只覆盖固定 grab vs 折叠 handle 两种真实结构，不为凑数发明第三种。两者 joint 拓扑明确不同（无 joint parent visual vs REVOLUTE child），构成合法 2-candidate slot。

### Slot C：reinforcement（边角 / 棱边加固 —— 挂到 body+lid 表面，Rule 1 inline，无独立 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| corner_caps（基线） | parent `cb7b4d8c` | `_add_corner_caps` L73-92 + body caps L109-111 + lid caps L195-210 | eligible if compatible | 8 个金属护角块（body 4 个双重 `for sx/sy`，lid 4 个 enumerate 列表），固定 cap=0.045 方块；**固定 8 数量**，无独立 joint（body/lid visual）|
| edge_banding | rec_suitcase_var_edgeband | `_add_edge_banding` L91-144（`_add_edge_band` L81-88）+ body banding L165-172 + lid banding L256-263 | eligible if compatible | 沿 12 条棱边包黄铜箍条（4 X 向 + 4 Y 向 + 4 Z 向竖角，`edges` 列表恒 12 项 `for i in range(n)`），半嵌入墙面读作包角；body 12 + lid 12，**固定 12 数量**，无独立 joint |

> **2-candidate 说明**：reinforcement 仅 2 个 candidate（护角 vs 包边），源池无第三种加固结构。两者 visual 族结构明确不同（8 离散方角块 vs 12 连续棱条，不同 helper / 数量 / 棱 vs 角）。同上符合降级理由。
> **重要：固定数量非 multiplicity**。corner_caps 恒 8、edge_banding 恒 12——这两个数量在 source code 里是 module 内部**固定**循环（不暴露参数、不加权采样、不变），**不是模板级可变 N 复制轴**。source map 的「band_count [2,6] / cap_count 8」描述与代码不符，以代码为准（见 §8）。

### Slot D：lid_profile（盖型 —— 决定 lid 的 mesh / primitive，恒后铰 lid_hinge 不变）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat（基线） | parent `cb7b4d8c` | lid L153-218（shell_panel + 4 wall + 4 corner + trim）| eligible if compatible | 平盖：Box 顶板 + 4 Box 墙 + 4 护角 + trim 带；lid 闭合时四墙下缘贴 body rim（SEAM_GAP）；primitive = Box |
| dome_trunk | rec_suitcase_var_dome_trunk | dome lid L214-285 + `_build_dome_shell` L101-120 + `_build_dome_endwall` L123-139 + `_dome_surface_z` L142-153 | eligible if compatible | 圆顶 steamer-trunk 盖：cadquery barrel-vault `dome_shell`（mesh，DOME_H=0.08 拱顶）+ 两侧 `dome_end_{i}` 实心封口（封住 vault 左右月牙缺口，lid 全覆盖 body）+ 黄铜 `dome_band_{i}` 环带 + `lid_strap_{i}` 皮带；primitive = `mesh_from_cadquery`（**不降级成 Box**）；闭合时 dome rim seat 在 body 前 rim 上方 |

> **2-candidate 说明**：lid_profile 仅 2 个 candidate（平盖 vs 圆顶）；源池只覆盖这两种 lid mesh。结构差异明确（Box vs cadquery barrel-vault mesh + 端封 + 环带，dome 峰高于 body top）。符合降级理由。

### Slot E：internal_structure（内部结构 —— 挂到 body 内腔）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| open（基线） | parent `cb7b4d8c` | —（无内部件）| eligible if compatible | 无内部机构，直接箱腔；body trim 带保留 |
| lift_tray | rec_suitcase_var_lift_tray | `packing_tray` part L276-333（tray_floor + 3 wall + lift_tab + `tray_hinge` REVOLUTE）+ clearance 常量 L29-39 + body 带移除注记 L130-133 | eligible if compatible | `packing_tray` 独立 part（`tray_floor` linen 板 + 前/左/右 3 低侧壁 + `tray_lift_tab` 皮拉手），`tray_hinge` REVOLUTE axis=(-1,0,0)、parent=body、origin=(0, D/2-T-0.003, TRAY_Z=0.047)、掀起露下层腔（lower=0/upper=1.3）；tray 尺寸 clear 8 护角内面（TRAY_W~0.370，TRAY_CLEAR=0.004）；**parent body 两条 trim 带移除**（否则横跨 open 腔悬于托盘上方读作穿模）|

> **2-candidate 说明**：internal_structure 仅 2 个 candidate（空腔 vs 掀起托盘），源池无第三种内部机构。两者 joint 拓扑明确不同（无 part vs REVOLUTE tray child）。符合降级理由。

硬约束记录：Slot A=3 candidate（含 PRISMATIC zipper + 2 REVOLUTE）；Slot B/C/D/E 各 2 candidate（均有书面降级理由：源池真实结构上限就是 2，不发明）。无 1-candidate 槽。全部来自被采纳 7 个 5★ 样本。

## 槽位图（slot graph）

pattern: `parallel_children`（共同 root = `suitcase_body`；恒在主轴 = `lid_hinge` REVOLUTE 后铰翻盖）

```
                    suitcase_body  (root, 皮硬壳; 由 reinforcement 决定表面加固 visual)
                          │
                          ├──[lid_hinge: REVOLUTE axis=-X, origin=(0,D/2,HB)]──> suitcase_lid (child, 恒在)
                          │        （lid mesh 由 lid_profile 决定: flat Box / dome cadquery mesh）
                          │
   ┌──────────────┬───────┴────────────┬───────────────────────┐
   │ closure (A)  │ handle (B)         │ internal (E)          │  reinforcement(C)=body+lid 表面 visual
   ▼              ▼                     ▼
 latch/tongue    rope(纯visual)/        packing_tray
 (REVOLUTE) 或    folding_handle        (REVOLUTE，掀起)
 zipper slider   (REVOLUTE, parent=lid) 或 open(无件)
 (PRISMATIC)
 （挂 body 前面/  （rope 挂 body 前面;     （挂 body 内腔）
  slider 挂 body; folding 挂 lid 顶）
  buckle 跨 body+lid）
```

接口点位与 joint 语义：
- **lid_hinge（恒在主轴）→ suitcase_body**：后顶边铰线 origin=(0, D/2, HB)，axis=(-1,0,0)，rest pose=closed（q=0 盖合 body rim，flat 留 SEAM_GAP≈1.5mm / dome rim seat 上方留 ≤8mm gap）。**所有 slot 共享同一 lid_hinge**，不被 slot 替换。
- **closure_mechanism → body（前面）/ lid**（互斥三选一）：
  - latches：两 latch part REVOLUTE axis=(+1,0,0)，origin=(±LATCH_X, latch_y, HB-0.018)，parent=body，跨 seam 扣 lid。
  - buckle_straps：两 strap_tongue part REVOLUTE axis=(-1,0,0)，origin=(±STRAP_X, BUCKLE_CY, HB)，parent=body；body 侧 buckle frame + lower strap，lid 侧 upper strap 跨 seam（**lid visual 依赖 flat lid 前墙面**——dome 无平前墙，见 §兼容矩阵）。
  - zipper_perimeter：单 slider PRISMATIC axis=(1,0,0)，origin=(-ZIP_TRAVEL/2, -(D/2), HB)，parent=body；zip track 沿 body+lid seam 三段（**依赖 flat lid 的平直 seam 边**——dome 的 seam 形状不同，见 §兼容矩阵）；teeth↔slider element-scoped allow_overlap。
- **handle_system → body / lid**：fixed_top_grab=body 前面 rope 纯 visual（无 joint）；folding_handle=lid 顶 mount 托座 + `handle_fold` REVOLUTE axis=(-1,0,0)、parent=**lid**、origin=(0,-D/2,HL+PIVOT_Z)，pivot rod↔mount captured-pin allow_overlap（**folding mount 锚在 flat lid 顶面 z=HL**——dome 顶为曲面，见 §兼容矩阵）。
- **reinforcement → body+lid 表面**：corner_caps（8 块 Rule1 inline body/lid visual）/ edge_banding（12 条 Rule1 inline body/lid visual）；均无独立 joint。
- **internal_structure → body 内腔**：open=无件；lift_tray=`packing_tray` REVOLUTE axis=(-1,0,0)、parent=body、origin=(0, D/2-T-0.003, TRAY_Z)，tray clear 8 护角内面（**lift_tray 与 corner_caps 的 clearance 已显式 size，与 edge_banding 需复核内面**，见 §兼容矩阵）。
- **mating policy**：captured-pin（folding pivot rod↔mount、latch/tongue 铰座、zipper teeth↔slider）省略 MatingContract（grandfather），由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（来源样本已逐条声明：folding L333-347、zipper L492-505）。
- **互斥 / 派生**：closure 三候选互斥；lid_profile=dome 派生闭合 seam / lid 顶曲面形态，影响 zipper / buckle / folding 的接口（见 §10 compatibility matrix）。

## 每槽位 Module Emits / Interfaces

### lid_hinge（恒在主轴，非 slot；以 parent 为准）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `suitcase_lid`（child；mesh 由 lid_profile slot 决定）| parent L153-218 |
| internal joints | `lid_hinge` REVOLUTE，axis=(-1,0,0)，origin=(0,D/2,HB)，range [0,2.0] | parent L220-230 |
| upstream interface | 后顶边铰线（消费 body `wall_back` 顶 rim）| parent L225 |
| downstream interface | lid 前缘 → 携带 closure（latch 扣 / buckle upper strap / zipper lid track）| parent L153-218 |

### Slot A / closure_mechanism — latches（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch_left` / `latch_right`（latch_plate + latch_catch）；body 上 `latch_boss_{side}` 铰座 visual | parent L232-260 / L138-151 |
| internal joints | `latch_{side}_hinge` REVOLUTE ×2，axis=(1,0,0)，origin=(±LATCH_X, latch_y, HB-0.018)，range [0,1.4] | parent L250-260 |
| upstream interface | body 前面 latch_boss（face contact 铰线）| parent L138-151 |
| downstream interface | 无（终端扣件，扣 lid 前缘）| — |

### Slot A / closure_mechanism — buckle_straps
| emits | 描述 | 来源 |
|---|---|---|
| parts | `strap_tongue_{i}` ×2（tongue_strip + tongue_tip）；body 上 lower_strap/buckle frame(top/bottom/left/right/center bar)/mount boss；lid 上 upper_strap_{i} | buckle L326-358 / L199-233 / L300-313 |
| internal joints | `strap_tongue_{i}_hinge` REVOLUTE ×2，axis=(-1,0,0)，origin=(±STRAP_X, BUCKLE_CY, HB)，range [0,1.4] | buckle L348-358 |
| upstream interface | body 前面 buckle frame center bar（扣舌绕之翻转）| buckle L108-152 |
| downstream interface | lid 前墙面 upper_strap 跨 seam（依赖 flat lid 前墙）| buckle L300-313 |

### Slot A / closure_mechanism — zipper_perimeter
| emits | 描述 | 来源 |
|---|---|---|
| parts | `zipper_slider`（slider_body + channel + bail + pull_tab + end_stop）；body+lid 各 `zip_tape_{i}`/`zip_teeth_{i}` ×3 段 | zipper L342-398 / L228-245 / L312-329 |
| internal joints | `zipper_slide` PRISMATIC，axis=(1,0,0)，origin=(-ZIP_TRAVEL/2,-(D/2),HB)，range [0, ZIP_TRAVEL≈0.36] | zipper L390-398 |
| upstream interface | body 前面 seam 线 zip track（slider 座于 tape）| zipper L228-245 |
| downstream interface | lid seam 边 zip track（依赖 flat lid 平直 seam）；teeth↔slider captured allow_overlap | zipper L312-329, L492-505 |

### Slot B / handle_system — folding_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `folding_handle`（handle_arm_{i}×2 + handle_pivot_rod + handle_grip）；lid 上 handle_pivot_mount_{i}×2 | folding L248-270 / L225-234 |
| internal joints | `handle_fold` REVOLUTE，axis=(-1,0,0)，parent=lid，origin=(0,-D/2,HL+HANDLE_PIVOT_Z)，range [0,1.3] | folding L272-282 |
| upstream interface | lid 顶 handle_pivot_mount（captured-pin，pivot rod↔mount）| folding L225-234, L333-347 |
| downstream interface | 无（终端把手）| — |

### Slot E / internal_structure — lift_tray
| emits | 描述 | 来源 |
|---|---|---|
| parts | `packing_tray`（tray_floor + tray_wall_0/1/2 + tray_lift_tab）| lift_tray L276-319 |
| internal joints | `tray_hinge` REVOLUTE，axis=(-1,0,0)，parent=body，origin=(0, D/2-T-0.003, TRAY_Z=0.047)，range [0,1.3] | lift_tray L321-333 |
| upstream interface | body 内后壁铰线 + 内腔（tray 尺寸 clear 8 护角内面 CORNER_INNER_X）| lift_tray L29-39 |
| downstream interface | 无（露下层腔）| — |

### reinforcement / lid_profile（纯 visual / mesh，无独立 part / joint）
| emits | 描述 | 来源 |
|---|---|---|
| corner_caps | 8 个 `body_corner_{i}`/`lid_corner_{i}` Box，Rule1 inline body/lid visual | parent L73-92 |
| edge_banding | body 12 + lid 12 `*_band_{i}` Box（12 棱），Rule1 inline | edgeband L91-144 |
| dome_trunk | lid `dome_shell` + `dome_end_{i}`×2 + `dome_band_{i}`×2 cadquery mesh + 皮带，替换 flat lid Box 壳 | dome L214-285 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure_mechanism | enum | latches / buckle_straps / zipper_perimeter | — | choice | deterministic sampler；编入 slot_choice（joint-type 区分：REVOLUTE×2 / REVOLUTE×2 / PRISMATIC）| module table |
| handle_system | enum | fixed_top_grab / folding_handle | — | conditional | sampler 选；dome_trunk 时降级 fixed_top_grab（见 §10）| module table |
| reinforcement | enum | corner_caps / edge_banding | — | conditional | sampler 选；与 lift_tray 内腔 clearance 复核（见 §10）| module table |
| lid_profile | enum | flat / dome_trunk | — | choice | sampler 选；dome 对 closure/handle 派生 gating（见 §10）| module table |
| internal_structure | enum | open / lift_tray | — | conditional | sampler 选；lift_tray 需 reinforcement clearance（见 §10）| module table |
| palette_style | enum | vintage_leather_brass / oxblood_chrome / tan_steamer / black_travel / olive_canvas_brass | vintage_leather_brass | palette | palette only，**不计入 slot_choice**；见 §palette | 各样本材质 |
| box_w / box_d / box_h_scale | float | W∈[0.40,0.54]、D∈[0.28,0.40]、HB∈[0.070,0.105] | 0.46/0.34/0.085 | independent | 在范围内独立采样后 clamp（保硬箱比例）| 各样本 L17-19 |
| lid_h (HL) | float | derived | 0.075 | equation | `= clamp(0.060, 0.095)`，flat 随 box_h；dome 用 DOME_H 派生 | 各样本 L20 |
| dome_h_scale | float | [0.85,1.15] | 1.0（DOME_H=0.08）| conditional | 仅 lid_profile=dome_trunk 有效；缩放拱顶高，clamp（≤ D/2 以保 barrel-vault 合法）| dome L24, L29 |
| lid_open_scale | float | [0.85,1.05] | 1.0 | independent | clamp lid_hinge `upper`（基线 2.0）；各 closure/handle/tray REVOLUTE upper 按各自 1.4/1.3 clamp | 各样本 |
| zip_travel_scale | float | [0.85,1.05] | 1.0 | conditional | 仅 closure=zipper 有效；缩放 PRISMATIC upper（≤ 沿前面可用行程 W-0.10）| zipper L40 |
| (—) | constraint | — | — | conditional | dome_trunk × {zipper, buckle, folding_handle} 接口派生（见 §10 gating：dome 时这三者降级 / 重锚）| lid_profile |
| (—) | constraint | — | — | inequality | lift_tray TRAY_W ≤ 2·(reinforcement 内面 − TRAY_CLEAR)：corner_caps 内面=CORNER_INNER_X≈0.189；edge_banding 内面=W/2−T（更靠外，需缩 tray 复核）→ 违反则缩 TRAY_W | lift_tray L29-33 |

连续尺寸采样契约：先采 named slot（解析 conditional：dome_h_scale 仅 dome、zip_travel_scale 仅 zipper、lift_tray clearance 随 reinforcement、handle 降级随 lid_profile）→ 采 independent 主尺度（box_w/d/h、lid_open_scale）→ 派生 HL（equation）→ 用 inequality 把 tray 宽投影回内腔可行域。所有 scale 在 `resolve_config` clamp/派生，绝不改 slot enum 选择或 joint type。

## palette_style（colorway，follow Accessories_Cushion.md PALETTE_STYLES 模式）

每 seed 采样一个 palette_style（**palette only，不计入 slot_choice、不算拓扑维度**），决定命名材质 RGBA 组。从 7 个 5★ 样本观察到的真实材质族抽取（5 套，target 4-6）：

| palette_style | body / leather | trim / strap | corner / band 加固 | handle wood | hardware metal | 观察来源 |
|---|---|---|---|---|---|---|
| vintage_leather_brass（默认）| 复古棕皮 (0.32,0.15,0.10) | 深棕 (0.18,0.09,0.06) | 棕护角 (0.22,0.11,0.07) / 黄铜带 (0.68,0.60,0.36) | 木 (0.55,0.27,0.07) | 灰金属 (0.58,0.58,0.62) | parent / edgeband banding (0.68,0.60,0.36) |
| oxblood_chrome | 暗红棕皮 (0.30,0.12,0.10) | 深酒红 (0.20,0.08,0.07) | 铬护角 (0.55,0.56,0.60) | 深木 (0.45,0.22,0.06) | 亮铬 (0.72,0.72,0.76) | parent metal_latch (0.58,0.58,0.62) 提亮 |
| tan_steamer | 浅褐皮 (0.55,0.40,0.24) | 棕带 (0.34,0.22,0.12) | 黄铜环带 (0.72,0.58,0.22) | 浅木 (0.62,0.40,0.18) | 黄铜扣 (0.72,0.58,0.22) | dome_trunk brass_band (0.72,0.58,0.22) + buckle metal_buckle (0.60,0.56,0.45) |
| black_travel | 黑硬壳 (0.10,0.10,0.12) | 炭灰带 (0.16,0.16,0.18) | 铬护角 (0.62,0.62,0.66) | 黑 grip (0.14,0.14,0.16) | 亮铬 (0.74,0.74,0.78) | zipper zipper_tape (0.10,0.07,0.05) 黑系 |
| olive_canvas_brass | 橄榄帆布 (0.36,0.34,0.22) | 棕革带 (0.28,0.18,0.10) | 黄铜带 (0.68,0.60,0.36) | 木 (0.55,0.27,0.07) | 旧黄铜 (0.60,0.56,0.45) | edgeband brass + buckle metal_buckle (0.60,0.56,0.45) |

> palette 实现：模板内 `PALETTE_STYLES` dict（同 Accessories_Cushion.md），`config_from_seed` 用 `rng.choice` 选一套，factory 用命名材质（不在 factory 裸 RGB 随机）。zipper teeth / buckle frame / brass band 等 hardware 用对应 palette 的 metal / brass 色。

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots（closure_mechanism / handle_system / reinforcement / lid_profile / internal_structure + 恒在 lid_hinge）表达，suitcase 是单体，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。
- 说明：以下都是 **module 内部固定数量的局部循环，不是模板级 N-复制轴**（数量不进 slot_choice、不加权采样、不变）：
  - corner_caps 恒 **8**（4 body + 4 lid，parent L73-92 双重 for + L195-210 enumerate）。
  - edge_banding 恒 **12**（每个 box 12 棱，edgeband L108-144 `edges` 列表恒 12 项 `for i in range(n)`）。
  - latches 恒 **2**（parent L236）、buckle strap_tongue 恒 **2**（buckle L327）、dome_band 恒 **2**、handle pivot mount 恒 **2**。
- **与 source map 的分歧（以代码为准）**：source map line 42-46 写「count_param: band_count / cap_count；包边条 [2,6]」。实测代码 edge_banding 是**固定 12 棱包边**（不是 2-6 条可变），corner_caps 是**固定 8**——二者均无可变 N 参数、无加权采样。故**本模板无 multiplicity 轴**，符合 SPEC_TEMPLATE §8「无复制数量逻辑」。（与同大类 `bag_suitcase_box` 的同类判定一致：固定数量局部循环 ≠ 模板级 multiplicity。）

## 拓扑多样性审计

总组合数（不含 palette、不含连续 scale）：
closure_mechanism(3) × handle_system(2) × reinforcement(2) × lid_profile(2) × internal_structure(2) = **48**（gating 后仍 ≫ 10，见兼容矩阵）。


理由：`slot_choices_for_seed` 返回 `(closure_mechanism, handle_system, reinforcement, lid_profile, internal_structure)` 五元组；48 个理论组合，gating 后（dome 收窄 closure/handle、edge_banding×lift_tray 复核）仍远超 10 个 distinct。zipper 的 PRISMATIC 主 joint 与 latch/buckle 的 REVOLUTE 是不同拓扑等价类，不被 distinct 折叠。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 顺序 = 先 `rng.choice` lid_profile → 据 lid_profile gating 决定 closure / handle 合法子集（dome 收窄，见兼容矩阵）→ `rng.choice` closure / handle / reinforcement → `rng.choice` internal_structure（据 reinforcement clearance gating）→ 解析 conditional scale（dome_h@dome / zip_travel@zipper）→ 采 independent 主尺度 → 派生 HL → inequality 投影 tray 宽。compatibility matrix 排除 / 降级非法组合。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：关键 scale = box_w/box_d/box_h（independent，保硬箱比例）、HL（equation 派生）、dome_h_scale（conditional@dome）、lid_open_scale（independent，每 REVOLUTE clamp）、zip_travel_scale（conditional@zipper，≤ 前面可用行程）、tray 宽（inequality 投影内腔）。全部 `resolve_config` clamp/派生，不破坏 lid_hinge / closure 铰座 / folding pivot / tray captured 接口或类别身份。按 §7 约束类型声明依赖；遵循采样契约（conditional→independent→equation→inequality）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | lid_profile 先选 → gating closure/handle（dome 收窄）→ 选 closure/handle/reinforcement → gating internal（reinforcement clearance）→ 解析 conditional scale → 采主尺度 → 派生 HL → 投影 tray 宽 | slot_choices_for_seed 五元组与 build 一致、含 PRISMATIC(zipper) 维度 |
| compatibility matrix | (1) **dome_trunk × zipper_perimeter**：zip track 沿 flat lid 平直 seam 边授权，dome lid 的 seam 形状不同 → gate（dome 时 closure∈{latches, buckle_straps}，或 zipper 仅配 flat）。 (2) **dome_trunk × buckle_straps**：buckle upper strap 授权在 flat lid 前墙面，dome 无平前墙 → gate（dome 时 buckle 降级 latches，或仅 flat 配 buckle）。 (3) **dome_trunk × folding_handle**：folding pivot mount 锚在 flat lid 顶面 z=HL，dome 顶为曲面 → gate（dome 时 handle 降级 fixed_top_grab，或 folding 仅配 flat）。**→ 实务上：dome_trunk 时安全子集 = closure=latches + handle=fixed_top_grab**。 (4) **edge_banding × lift_tray**：edge_banding 内面=W/2−T 比 corner_caps 的 CORNER_INNER_X 更靠外，tray clearance 需按 banding 内面复核（inequality 缩 TRAY_W）；corner_caps×lift_tray 已显式 size 安全。 (5) handle/closure/reinforcement 在 flat lid 下正交（互不干涉）。 | 无 floating closure、无 dome 上挂 flat-only 接口、无 tray 撞加固内面、无 zipper seam 错位 |
| controlled local variation | box_w/d/h + HL + dome_h@dome + lid_open + zip_travel@zipper + tray 宽，全 clamp/派生 | 比例变化不破坏 lid seat gap、closure 对位、folding pivot、tray captured、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 module captured-pin allow_overlap + closed-pose seat |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| closure_mechanism | 3 | yes | yes | 含 2 REVOLUTE + 1 PRISMATIC（zipper），joint-type 多样 |
| handle_system | 2 | yes | no | 源池上限 2（grab/folding），书面降级 |
| reinforcement | 2 | yes | no | 源池上限 2（8 护角 / 12 包边），书面降级 |
| lid_profile | 2 | yes | no | 源池上限 2（flat Box / dome cadquery mesh），书面降级 |
| internal_structure | 2 | yes | no | 源池上限 2（open / lift_tray REVOLUTE），书面降级 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名的五元组 `(closure_mechanism, handle_system, reinforcement, lid_profile, internal_structure)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` clamp box_w/d/h、派生 HL、解析 conditional（dome_h@dome / zip_travel@zipper / tray clearance@reinforcement / handle 降级@dome）、投影 tray 宽到内腔、clamp 各 open scale
- compatibility matrix / gating 阻止非法 dome×{zipper,buckle,folding} 接口与 edge_banding×lift_tray clearance 越界
- controlled local scale clamp 后不破坏 lid seat gap、closure 对位、folding pivot、tray captured 接口、joint origin、类别身份
- cross-part scale 依赖（dome conditional、tray inequality、HL equation）在 `resolve_config` 解析，不留到 builder
- 关键 joint type/axis/range：恒在 `lid_hinge` REVOLUTE axis≈(-1,0,0)（abs(axis[0])>0.99）；closure 主 joint（latch/tongue REVOLUTE axis≈±X / zipper_slide PRISMATIC axis≈(1,0,0)）；handle_fold REVOLUTE axis≈(-1,0,0) parent=lid（仅 folding）；tray_hinge REVOLUTE axis≈(-1,0,0)（仅 lift_tray）
- captured-pin / captured-slide：element-scoped `allow_overlap`（folding pivot rod↔mount 照搬 folding L333-347；zipper teeth↔slider 照搬 zipper L492-505）
- copied / 固定循环：corner_caps 恒 8、edge_banding 恒 12、latch/tongue 恒 2——固定数量，非 multiplicity，无 `*_count` 参数
- closed pose：lid q=0 seat 在 body rim（flat ≤6mm / dome ≤8mm gap）覆盖开口；closure q=0 扣合；folding q=0 平贴 lid 顶；tray q=0 坐内腔

## Reject cases

- 把 corner_caps 的 8 或 edge_banding 的 12 当成模板级 multiplicity 轴并加权采样 N → 误造 count 参数（代码是固定循环），违反 §8 单体判定。
- dome_trunk 配 zipper_perimeter / buckle_straps / folding_handle 却不 gating / 不重锚 → zip track 沿 dome seam 错位、buckle upper strap 浮在曲面外、folding mount 嵌入曲面 FAIL；须按兼容矩阵 gate 或降级到 dome 安全子集。
- edge_banding 配 lift_tray 不复核 tray 内面 clearance → tray 撞包边内沿穿模；须按 banding 内面缩 TRAY_W。
- lift_tray 不移除 parent body 的两条 trim 带 → 带横跨 open 腔悬于托盘上方读作穿模（见 lift_tray L130-133 注记）。
- closure=zipper / buckle 时仍发 latch 子件 → 三者互斥，重复闭合硬件 / 浮空 FAIL；closure 必三选一。
- lid rest pose 默认设成开启角而非 closed → closed-pose seat 检查 FAIL、不符合行李箱身份。
- 给 captured-pin（folding pivot、zipper teeth↔slider）补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。
- 把 dome cadquery barrel-vault mesh 降级成粗糙 Box 平盖 → 丢失 lid_profile 身份（MATURE_METHOD §4.4 primitive 不降级）。
- 把连续尺寸（box_w/h）或 palette_style 当新 candidate 塞进 slot → 不是结构差异，违反 §2.4。

## 与相邻类别的边界

- 不该混入：**板条木箱 / 储物 chest（`bag_suitcase_box`，同大类不同小类）**——板条侧壁 + 多种 lid_closure（下翻 / 双叶 / 滑顶 / 立门）、无手提 + 前皮带 / 拉链闭合；本类是皮硬壳后铰翻盖 + 提把 + 前闭合扣件单一形态。
- 不该混入：**软包行李袋 / Luggage bag（Bag_Suitcase / Luggage）**——软体 + 伸缩拉杆 + 万向轮主运动；本类是静置硬壳，无 telescoping 拉杆 + 轮轴。
- 不该混入：**藏宝箱 / 珠宝盒（treasure chest / jewelry box）**——拱顶木箱 + 锁扣储物身份、无手提旅行语义；本类身份在「可手提旅行硬箱」（提把 + 旅行护角 + 皮带 / 拉链闭合）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) closure_mechanism 三候选互斥（latch/buckle/zipper 同一前闭合位置）+ zipper PRISMATIC 编入 slot_choice 为独立拓扑等价类；(2) handle/reinforcement/lid_profile/internal 各 2-candidate 的源池上限降级理由是否接受；(3) **本模板无 multiplicity 轴**（corner_caps 固定 8、edge_banding 固定 12 是 module 内部固定循环，与 source map 的「band_count [2,6]」分歧，以代码为准）；(4) dome_trunk × {zipper, buckle, folding_handle} 的兼容 gating / 降级（dome 安全子集 = latches + fixed_top_grab）；(5) edge_banding × lift_tray 的 clearance 复核策略；(6) Topology target 48<300 的说明是否接受（本小类真实结构上限）；(7) palette_style 5 套是否覆盖期望 colorway）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_add_box_shell`（body+flat lid 公用骨架，7 样本全等）、`_add_corner_caps`（corner_caps reinforcement）、`_add_edge_banding`/`_add_edge_band`（edge_banding reinforcement）、`_add_buckle_frame`（buckle closure）、`_add_zipper_track`（zipper closure）、`_add_handle_arm`（folding handle）、`_build_dome_shell`/`_build_dome_endwall`/`_dome_surface_z`（dome lid_profile，cadquery，仅 dome 用）。
- captured-pin allow_overlap 来源样本已逐条声明：folding L333-347（pivot rod↔mount + arm↔mount）、zipper L492-505（teeth↔slider body，body+lid 各一）。latch/tongue 由 origin 检查守（无显式 allow_overlap）。实现时按 module 复制对应 element-scoped allow_overlap。
- folding_handle 的 parent = `suitcase_lid`（不是 body）：folding mount + handle_fold 必须在 lid module 发出 lid part 后才挂；dome lid 时降级 fixed_top_grab（曲面无平 mount 面）。
- lift_tray 的 corner-clearance 常量（L29-39）按 reinforcement 派生：corner_caps→CORNER_INNER_X≈0.189；edge_banding→W/2−T≈0.218（更靠外，tray 需更窄或复核）。tray 还需移除 parent body trim 带（lift_tray L130-133）。
- lid_hinge 恒在、不被任何 slot 替换——所有 module 共享同一后铰 lid（区别于 bag_suitcase_box 的 lid_closure 是可替换 slot）。
- 不调 `fail_if_parts_overlap_in_sampled_poses`（多 module 多姿态积大）；保留自动 baseline 的 `fail_if_parts_overlap_in_current_pose`（closed rest pose 干净）。
- 参考实现模板（review 通过后选读，按 MATURE_METHOD §2 选 slot graph / 运动拓扑相近者）：`cushion.py`（同方法：固定 named slots + parallel children + palette_style + captured-pin allow_overlap + 兼容矩阵 gating + cadquery mesh 不降级，本类可同构改编）、`bag_suitcase_box.py`（同大类箱体 + 后铰 lid + interior REVOLUTE/PRISMATIC 机构 + captured-pin grandfather）、`single_revolute_hinge` / `wheelie_bin_with_hinged_lid`（hinge line / closed pose / captured-pin overlap）、`twojoint_prismatic_chain` / `threestage_telescoping_slide`（zipper slider PRISMATIC rail/socket 接口）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | base | body 骨架 + lid_hinge + flat lid + corner_caps + latches + rope handle 基线 | rec_..._cb7b4d8c (parent) | L33-92 helpers / L104-260 build | root chassis + 恒在 lid_hinge + latches closure + fixed_top_grab handle + corner_caps reinforcement + flat lid_profile + open internal |
| S1 | A | buckle_straps | rec_suitcase_var_buckle | `_add_buckle_frame` L108-152 / body L199-233 / lid L300-313 / tongue+REVOLUTE L326-358 | 双皮带扣闭合（2×REVOLUTE 扣舌）|
| S2 | A | zipper_perimeter | rec_suitcase_var_zipper | `_add_zipper_track` L105-180 / body+lid track L228-245,L312-329 / slider+PRISMATIC L342-398 / allow_overlap L492-505 | 沿周拉链闭合（PRISMATIC slider，唯一 PRISMATIC 主拓扑）|
| S3 | B | folding_handle | rec_suitcase_var_folding_handle | `_add_handle_arm` L107-114 / mounts L225-234 / part+REVOLUTE L248-282 / allow_overlap L333-347 | 折叠提把（REVOLUTE，parent=lid，captured-pin）|
| S4 | C | edge_banding | rec_suitcase_var_edgeband | `_add_edge_banding`/`_add_edge_band` L81-144 / body L165-172 / lid L256-263 | 12 棱黄铜包边（固定 12 循环，非 multiplicity）|
| S5 | D | dome_trunk | rec_suitcase_var_dome_trunk | `_build_dome_shell` L101-120 / `_build_dome_endwall` L123-139 / `_dome_surface_z` L142-153 / dome lid L214-285 | 圆顶 steamer-trunk 盖（cadquery barrel-vault mesh + 端封 + 环带）|
| S6 | E | lift_tray | rec_suitcase_var_lift_tray | clearance L29-39 / `packing_tray`+`tray_hinge` L276-333 / body 带移除 L130-133 | 掀起式打包托盘（REVOLUTE，parent=body，clear 护角内面）|
