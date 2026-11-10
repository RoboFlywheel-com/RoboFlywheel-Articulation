# water_dispenser — Modular Spec

> 来源小类：`picture/Other/Water dispenser`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Water_dispenser.md`。
> **"Water dispenser" 在此 = 出水/饮料分配机（beverage / water dispensing tower、瓶装冷水机、饮料桶）**：一个接地的主体（drip-tray 台面塔 / 落地柜 / 瓶装冷水柜 / 圆筒饮料桶）正面挂 1..N 个出水阀（faucet / push-lever / push-button / twist-spigot / paddle），下方有 drip tray，部分形态顶部有倒装大水瓶。**不是**净水器滤芯、不是水龙头单体、不是 dehumidifier 水桶。
>
> **同步状态**：本 spec 引用的 **10 个 5 星样本**（4 个 parent 母资产 + 6 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5，均为 `revisions/rev_000001/model.py`。行号按各样本本仓库实际行号计（逐一核对）。引用以 part / joint / helper **名字**为准（`drip_tray` / `tower_column` / `faucet` / `tap_handle` / `faucet_lever` / `push_button` / `spigot_knob_{i}` / `hot_paddle` / `cold_paddle` / `urn` / `pedestal_cabinet` / `water_bottle` / `for i in range(NUM_FAUCETS)` 等），行号仅作定位。
>
> **排除/缺失（见 §排除项）**：source map 提到的 `faucet-count-2` / `faucet-count-6` fork 与 dual (`003.png`) record **在本仓库 `data/records/` 中不存在**（仅 4 母资产 N∈{1,3,4} + 6 槽位 fork 落地）。faucet_count 多重性轴本身**仍是真来源**——P4(`3f3a9da3`) 已是干净的 `for i in range(4)` 龙头复制循环，twist_spigot / cylindrical_urn / drip_tray / inverted_top_bottle 变体内部都已写 `for i in range(NUM_FAUCETS)` 复制骨架——但 N=2/6 没有专属样本，故 N_range 保守取 **[1,4]**（产品域），sweep 偏小加权，详见 §8。

## 元信息
| 项 | 值 |
|---|---|
| slug | `water_dispenser` |
| template path | `agent/templates/Other_Water_dispenser.py` |
| test path (optional) | `tests/agent/test_water_dispenser_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: tap_type(主机构) + body_form + base_reservoir 各自挂到接地 body（parallel children）+ **faucet_count 多重性轴** N 次复制 faucet/tap_handle）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（4 parent 母资产 + 6 fork 槽位变体；均 rating=5、compile=success、workbench-only、≥1 非 fixed joint）|
| read_count | 10（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、复制循环与 run_tests/allow_overlap）|
| read_scope | all 5-star samples named in the source map for this category（map 命名的 ID 全部读完；map 提及但磁盘缺失的 faucet-count-2/6 与 dual 记入 §排除项）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 10/10 全部被采纳，无未采用样本；磁盘上其它 `rec_variant-base-support-*` / `rec_variant-body-form-{boxy,bullnose,wedge}-*` 记录**未被 source map 命名**，已核为非本 spec 来源，排除 |

阅读要点（用于槽位分解）：
- **4 个 parent 母资产**覆盖 3 种主体形态 + faucet_count N∈{1,3,4}：
  - **P1 single（`b6696ffc`，492L）**：`drip_tray`(root, 矩形穿孔托盘) ─FIXED→ `tower_column`(立柱) ─FIXED→ `faucet` ─REVOLUTE(`faucet_lever`, axis Y, L300-312)→ `tap_handle`（单龙头基线）。
  - **P3 triple（`acfaa2cf`，380L）**：`drip_tray`(root) ─FIXED→ `beverage_column`(flared 立柱)；3 个 faucet **扇形**(`FAUCETS` 列, ±40° yaw) 各带 `{side}_tap_handle` REVOLUTE(`{side}_tap_pivot`, axis X@yawed frame, L237-248)。注意 P3 用站位列而非纯 `range(N)`。
  - **P4 four_tap（`3f3a9da3`，422L）**：`drip_tray`(root) ─FIXED→ `pedestal_column` ─FIXED→ `header_box`(T 型横梁)；**`for i, fx in enumerate(FAUCET_XS)`(L227-254)** 干净复制 `faucet_{i}` + `tap_handle_{i}_pivot` REVOLUTE(axis X) —— **这是 faucet_count 多重性复制逻辑的权威源**（共享 mesh 对象 + 沿 X 等距 + 各自独立 REVOLUTE）。
  - **P_cooler（`6fffaa2f`，526L）**：`cabinet`(root, 瓶装冷水柜，前 alcove 凹腔) + `hot_paddle`/`cold_paddle`(REVOLUTE `*_paddle_hinge`, axis Y, 由 alcove 顶悬下, L239-251) + `drip_tray`(**PRISMATIC** `drip_tray_lift` axis +Z 提起, L299-307) + `bottle`(倒装大水瓶 FIXED `cabinet_to_bottle`, L316-322)。**这是 paddle 主机构 + bottled_cooler_cabinet 主体 + PRISMATIC 提起 drip-tray + 倒装瓶 4 个来源的同源样本**。
- **tap_type 轴**（Slot A）真正改 faucet 子件 part/joint 拓扑：
  - push_lever（基线，REVOLUTE 翻拨）/ push_button（**PRISMATIC -Z** 按钮，`push_button` part + `faucet_button`, L323-333）/ twist_spigot（**REVOLUTE about +X 旋塞**，`spigot_knob_{i}` + `faucet_spigot_{i}`, L298-323）/ paddle（**REVOLUTE about Y 悬挂拨片**，`*_paddle`）→ 4 种出水阀活动拓扑。
- **body_form 轴**（Slot B）改主体 mesh/part 树：rectangular_box（基线 tray+column / pedestal+header T 型）/ bottled_cooler_cabinet（`cabinet` 实柜 + alcove 凹腔，P_cooler）/ cylindrical_urn（`base`+`urn` lathe 圆筒饮料桶，`b7793c5c`，faucets 绕壁径向扇出）。
- **base_reservoir 轴**（Slot C）改接地/承托/补水机构：countertop（基线，drip_tray 即 root）/ floor_standing_pedestal（`pedestal_cabinet` 落地柜 root，tray/column 叠上，`9a1aa34a`）/ removable_drip_tray（drip_tray **PRISMATIC** 抽拉，countertop -Y `tray_slide` `7e820f42` / 或 P_cooler +Z lift）/ inverted_top_bottle（顶置倒装 `water_bottle` FIXED，`870bb3bc` / P_cooler）。
- **faucet_count 轴**（多重性）：N∈{1(P1),3(P3),4(P4)} 母资产覆盖；fork 变体内部均已 `for i in range(NUM_FAUCETS)` 复制就绪（twist_spigot/cylindrical_urn/drip_tray/inverted_top_bottle）。复制对象 = 单 faucet(+tap_type 子件) + tap_handle，沿主体正面等距，各自独立活动关节。**N=2/6 无专属样本**（见 §排除项）→ N_range 保守 [1,4]。

## 核心身份

一台**接地的出水/饮料分配机（water dispenser）**：一个稳定的主体（`body_form`：drip-tray 顶上的不锈钢立柱 / T 型横梁塔，或瓶装冷水柜，或圆筒饮料桶），正面/周向布 **1..N 个出水阀**（`faucet`），每个出水阀由用户操作的活动机构出水（`tap_type`：拨杆 REVOLUTE / 按钮 PRISMATIC / 旋塞 REVOLUTE绕流轴 / 悬挂拨片 REVOLUTE）。主体下方有 **drip tray**（穿孔接水盘，可固定或抽拉），部分形态在顶部有**倒装大水瓶**（FIXED 水箱）。接地方式由 `base_reservoir` 决定（台面 countertop / 落地柜 pedestal）。默认成熟域：body_form × tap_type × base_reservoir × 龙头数 N∈[1,4] 的台面到落地饮料/水分配机。

活动语义 = **每个出水阀的开关动作**（拨杆向前翻 REVOLUTE / 按钮压入 PRISMATIC / 旋塞绕流轴转 REVOLUTE / 拨片后推 REVOLUTE）+ 可选 **抽拉 drip-tray**（PRISMATIC）。倒装水瓶为 FIXED 非活动件（reservoir 身份件）。

不该混入：
- **单体水龙头 / faucet（厨卫龙头）**——本类是整机（主体 + 多阀 + 接水盘 + 可选水箱），不是装在台盆上的单个龙头；`rec_faucet_with_side_handle_*` 是不同类别。
- **除湿机水桶 / dehumidifier（`rec_dehumidifier_with_pullout_water_bucket_*`）**——抽拉水桶是收集冷凝水的，无出水阀/无饮用出水身份。
- **水车 / waterwheel（`rec_*shot_waterwheel_*`）**——纯旋转水力机械，与饮料分配无关。
- **净水器 / 滤水壶 / 咖啡机**——本类身份在于"主体 + 1..N 出水阀 + 接水盘"，缺这套即出类。

## 槽位 + 候选模块表

> **建模注记**：`tap_type`（Slot A）与 `base_reservoir`（Slot C）是真正改 part 树 / joint 拓扑的轴（出水阀活动机构 / 接地与补水机构）。`body_form`（Slot B）主要改主体 mesh + part 数（实柜 vs 立柱+横梁 vs 圆筒），并决定 faucet 的挂载父件与布列方式（正面排 vs 周向扇）。`faucet_count`（多重性轴）按 §8 编入 slot_choice。所有出水阀均**直接挂主体**（parallel children），无跨 slot 串联运动 spine → assembler 用显式 slot dispatch，不用自动链。

### Slot A：tap_type（出水阀——**主机构槽**，决定每个龙头的活动 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| push_lever（基线） | rec_model-…single…_b6696ffc / …triple…_acfaa2cf / …four-tap…_3f3a9da3（4 parent 中 3 个）| P1 `faucet`+`tap_handle`+`faucet_lever` REVOLUTE L245-312 / P4 `for i` `faucet_{i}`/`tap_handle_{i}_pivot` REVOLUTE L221-254 | eligible if compatible | `tap_handle` child，拨杆 **REVOLUTE** 绕水平横轴（P1 axis=(0,1,0)；P3/P4 axis=(1,0,0)@yawed），lower=0 直立闭 / upper≈0.6-0.7（~35-40°）向前翻；collar 捕获 faucet bonnet boss |
| push_button | rec_variant-tap-type-push-button-replace-the-push-le_…_1a8f4bb6 | `button_bezel` 固定 L259-283 + `push_button` part(`button_stem`+`button_cap`) L285-318 + `faucet_button` **PRISMATIC** axis=(0,0,-1) L323-333 | eligible if compatible | `push_button` child，**PRISMATIC** 向下压入 bonnet bore（lower=0 / upper≈0.010），`button_stem` 捕获在 `faucet_bonnet` 内（retained insertion）；bezel 为固定 trim visual |
| twist_spigot | rec_variant-tap-type-twist-spigot-replace-the-push-l_…_ffb293c3 | `_spigot_stem_geometry`/`_spigot_knob_geometry`(KnobGeometry) L265-296 + `for i in range(N_FAUCETS)` `spigot_knob_{i}` + `faucet_spigot_{i}` **REVOLUTE** axis=(1,0,0) L298-323 | eligible if compatible | `spigot_knob_{i}` child，绕**流轴 +X** **REVOLUTE** 旋塞（quarter-turn，lower=0 / upper≈SPIGOT_TRAVEL）；stem collar 捕获 bonnet；已写 faucet 复制循环 |
| paddle | rec_model-a-countertop-bottled-water-cooler-the-base_…_6fffaa2f | `hot_paddle`/`cold_paddle`(`hinge_barrel`+`paddle_plate`) L223-251 + `{tag}_paddle_hinge` **REVOLUTE** axis=(0,1,0) L239-251 | eligible if compatible | 悬挂式拨片 child，由 alcove 顶悬下，**REVOLUTE** 绕 Y（lower=0 / upper≈0.52，~30° 后推 -X 出水）；`hinge_barrel` 捕获 `{tag}_tap_body`；paddle 形态原生于 bottled_cooler_cabinet |

### Slot B：body_form（主体形态——决定主壳 mesh + faucet 挂载父件 + 布列方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular_box（基线，立柱+塔/横梁） | rec_model-…single…_b6696ffc / …triple…_acfaa2cf / …four-tap…_3f3a9da3 | P1 `drip_tray`+`tower_column` L130-251 / P3 `beverage_column` flared L66-144 / P4 `pedestal_column`+`header_box` T 型 L145-219 | eligible if compatible | drip-tray 上立柱（圆柱/flared），可加 T 型 `header_box` 横梁；faucet 挂柱壁/横梁正面，沿 X 排或扇形布；root 为 drip_tray（或由 base_reservoir 改 root） |
| bottled_cooler_cabinet | rec_model-a-countertop-bottled-water-cooler-the-base_…_6fffaa2f | `cabinet`(`_cabinet_shell` cut alcove)+控制面板+侧 vent+collar L100-198 | eligible if compatible | 实心柜体 `cabinet`(root)，前 alcove 凹腔容纳 paddle/spout，顶部 collar 受倒装瓶；faucet(paddle) 由 alcove 顶悬下；自带 led 面板/vent grille visual |
| cylindrical_urn | rec_variant-body-form-cylindrical-urn-reshape-the-re_…_b7793c5c | `_base_geometry`/`_urn_shell_geometry`(lathe) L70-101 + `base`(root)+`urn`(FIXED) L230-293 + `for i in range(FAUCET_COUNT)` 周向 faucet L296-373 | eligible if compatible | 圆筒饮料桶：lathe `base` 平台(root) + lathe `urn` 桶身(FIXED) + 顶盖/knob visual；faucet 绕桶壁径向扇出（mount 在 `URN_R_AT_FAUCET`，rpy 带 yaw），各带 REVOLUTE lever |

### Slot C：base_reservoir（接地 / 承托 / 补水机构——改 root 与可选活动件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| countertop（基线） | rec_model-…single…_b6696ffc / …triple…_acfaa2cf / …four-tap…_3f3a9da3 | P1 `drip_tray` root L140-208 / P4 `drip_tray` root+穿孔 grate L155-204 | eligible if compatible | drip_tray 即 root，坐台面 z=0；穿孔接水盘 FIXED 承托 column；无额外活动件（空机构基线）|
| floor_standing_pedestal | rec_variant-base-floor-standing-pedestal-mount-the-b_…_9a1aa34a | `pedestal_cabinet`(toe_kick+shell+top_plate+door) root L90-159 + `pedestal_to_tray` FIXED L199-205 | eligible if compatible | 落地柜 `pedestal_cabinet`(root, toe-kick 接地 z=0)，drip_tray + column **叠装其上**（FIXED 链）；改 root 与总高，不新增活动件 |
| removable_drip_tray | rec_variant-base-removable-drip-tray-add-a-removable_…_7e820f42 / rec_model-…cooler…_6fffaa2f | countertop 抽拉：`drip_tray` + `tray_slide` **PRISMATIC** axis=(0,-1,0) L295-324 / cooler 提起：`drip_tray_lift` **PRISMATIC** axis=(0,0,1) L299-307 | eligible if compatible | drip_tray 改为**活动 PRISMATIC** 抽拉/提起件（-Y 抽出 或 +Z 提起，lower=0 / upper≈TRAY_SLIDE）；与 tap_type 活动件并存 |
| inverted_top_bottle（reservoir 件） | rec_variant-reservoir-inverted-top-bottle-add-an-inv_…_870bb3bc / rec_model-…cooler…_6fffaa2f | `water_bottle` part + `tower_to_bottle` FIXED L438-452 / cooler `bottle`+`cabinet_to_bottle` FIXED + collar L310-322 | eligible if compatible | 顶置**倒装大水瓶** `water_bottle`(lathe 倒装瓶) **FIXED** 坐入主体顶 collar/socket（非活动，reservoir 身份件）；与任意 tap_type 并存 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: tap_type + body_form + base_reservoir 挂到接地 body（parallel children）；外加 faucet_count 在主体正面/周向 N 次复制 faucet+tap_type 子件+tap_handle）

```
ROOT body  (由 base_reservoir 决定 root: countertop→drip_tray 为 root;
            floor_pedestal→pedestal_cabinet 为 root, tray/column 叠上 FIXED)
  │   (body_form 决定主壳 mesh + faucet 挂载父件 P:
  │     rectangular_box → tower_column / header_box (P=column/header)
  │     bottled_cooler_cabinet → cabinet 实柜 alcove (P=cabinet)
  │     cylindrical_urn → base+urn lathe 桶 (P=urn 周向))
  │
  ├── [base_reservoir slot]  (改 root + 可选活动件)
  │     ├─ countertop          : (drip_tray = root, 无额外 joint)
  │     ├─ floor_standing_pedestal : pedestal_cabinet=root ──[pedestal_to_tray: FIXED]
  │     ├─ removable_drip_tray : drip_tray ──[tray_slide/drip_tray_lift: PRISMATIC -Y 或 +Z]
  │     └─ inverted_top_bottle : water_bottle ──[tower_to_bottle/cabinet_to_bottle: FIXED, 坐顶 collar]
  │
  └── [faucet_count multiplicity 轴]  i∈range(N)  faucet_{i} (+tap_type 子件) + tap_handle_{i}
        每个 faucet_{i} ──[body_to_faucet_{i}: FIXED, mount 在 P 正面/周向]
          └── [tap_type slot]  (互斥四选一, 每个 faucet 各一份活动机构)
                ├─ push_lever   : tap_handle_{i} ──[faucet_lever_{i}: REVOLUTE axis Y 或 X@yaw, origin=bonnet boss]
                ├─ push_button  : push_button_{i} ─[faucet_button_{i}: PRISMATIC -Z, origin=bezel top]
                ├─ twist_spigot : spigot_knob_{i} ─[faucet_spigot_{i}: REVOLUTE axis +X(流轴), origin=bonnet top]
                └─ paddle       : paddle_{i} ──────[paddle_hinge_{i}: REVOLUTE axis Y, origin=alcove 顶 tap_body]
```

接口点位与 joint 语义：
- **faucet 挂载接口**：`faucet_{i}` 以 FIXED 挂主体父件 P（由 body_form 定）；mount 点为正面/周向 boss（rectangular_box: 沿 X `FAUCET_XS` 等距或扇形 `FAUCETS` 站位；cylindrical_urn: 周向 `URN_R_AT_FAUCET` + yaw；bottled_cooler: alcove 顶 `TAP_X`）。shank 嵌入主壳（captured overlap）。
- **tap_type 接口（互斥，每 faucet 一份）**：
  - push_lever：`tap_handle_{i}` collar 捕获 faucet `bonnet`；REVOLUTE，origin 落在 bonnet boss（P1=(BONNET_X,0,PIVOT_Z)；P4=(0,VALVE_Y,PIVOT_Z)）。
  - push_button：`button_stem` 滑入 `faucet_bonnet` bore；PRISMATIC -Z，origin=(BONNET_X,0,bezel_top)。
  - twist_spigot：`spigot_stem` collar 捕获 bonnet；REVOLUTE +X，origin=(SPIGOT_X,0,SPIGOT_KNOB_Z)。
  - paddle：`hinge_barrel` 捕获 `tap_body`；REVOLUTE +Y，origin=alcove 顶 tap 轴(PADDLE_PIVOT)。
- **base_reservoir 接口**：
  - countertop：drip_tray 为 root（无 joint）。
  - floor_standing_pedestal：`pedestal_cabinet` root，`pedestal_to_tray` FIXED（tray 坐柜顶），column/faucet 顺链叠上。
  - removable_drip_tray：drip_tray PRISMATIC（-Y 抽出 `tray_slide` 或 +Z 提起 `drip_tray_lift`），origin=tray seat。
  - inverted_top_bottle：`water_bottle` FIXED 坐主体顶 collar/socket（`BOTTLE_SEAT_Z`），neck 嵌 collar bore（captured overlap）。
- **mating policy**：所有 hinge=pin-in-barrel / collar-on-boss captured-pin、button=stem-in-bore captured-slide、slide tray=rail/seat、bottle=neck-in-collar captured → **几何非两轴对接面 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests allow_overlap 段）。
- **rest pose**：所有出水阀 q=0 闭合（lever 直立 / button 弹出 / spigot 关 / paddle 直挂）；removable tray q=0 坐位；倒装瓶静止。
- **互斥 / 可选 / 派生**：tap_type 四候选互斥（一台机所有龙头同一阀型）；base_reservoir 四候选——countertop/floor_pedestal 互斥改 root；removable_drip_tray 与 inverted_top_bottle 是可叠加的可选活动/水箱件（见 §9 兼容矩阵，按 body_form gate paddle/urn 等组合）。

## 每槽位 Module Emits / Interfaces

### Slot A / tap_type — push_lever（以 P4 复制风格为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `faucet_{i}`(faucet_body+bonnet/pivot_boss+spout, FIXED 挂 P) + `tap_handle_{i}`(lever_collar+grip) | P4 L221-254 / P1 L211-298 |
| internal joints | `faucet_lever_{i}`(P1)/`tap_handle_{i}_pivot`(P4) REVOLUTE axis Y(P1)/X(P3/P4@yaw)，lower=0 / upper≈0.6-0.7 | P1 L300-312 / P4 L242-254 |
| upstream interface | `lever_collar` 捕获 faucet `bonnet`/`pivot_boss`（captured-pin）；faucet shank 嵌主壳 | P4 L278-299 |

### Slot A / tap_type — push_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定 `button_bezel`(faucet visual) + `push_button_{i}`(button_stem+button_cap) | 1a8f4bb6 L259-318 |
| internal joints | `faucet_button_{i}` PRISMATIC axis=(0,0,-1)，lower=0 / upper≈0.010 | 1a8f4bb6 L323-333 |
| upstream interface | `button_stem` 滑入 `faucet_bonnet` bore（retained captured-slide）| 1a8f4bb6 L354-361, L526-534 |

### Slot A / tap_type — twist_spigot
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spigot_knob_{i}`(spigot_stem+KnobGeometry knob) | ffb293c3 L298-309 |
| internal joints | `faucet_spigot_{i}` REVOLUTE axis=(1,0,0)（流轴），lower=0 / upper≈SPIGOT_TRAVEL | ffb293c3 L310-321 |
| upstream interface | `spigot_stem` collar 捕获 faucet bonnet（captured-pin）| ffb293c3 L265-280 |

### Slot A / tap_type — paddle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `paddle_{i}`(hinge_barrel+paddle_plate)；主壳上加 `{tag}_tap_body`/`tap_ring`/`tap_spout` visual | 6fffaa2f L202-238 |
| internal joints | `paddle_hinge_{i}` REVOLUTE axis=(0,1,0)，lower=0 / upper≈0.52（~30°）| 6fffaa2f L239-251 |
| upstream interface | `hinge_barrel` 捕获 alcove 顶 `tap_body`（captured-pin），paddle 悬下 | 6fffaa2f L340-353 |

### Slot B / body_form — rectangular_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drip_tray`(穿孔托盘) + `tower_column`/`beverage_column`(+ 可选 `header_box` T 横梁)；全为 named visual | P1 L130-208 / P4 L155-219 |
| internal joints | `tray_to_tower`/`tray_to_column`/`column_to_header` FIXED（主体内部刚性叠装）| P1 L202-208 / P4 L198-219 |
| downstream interface | column 壁/header 正面 mount boss 列（供 faucet_count 复制挂载）| P4 L227-237 |

### Slot B / body_form — bottled_cooler_cabinet
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`(root, shell cut alcove + control_panel + side_vent_grille + bottle_collar)，全 named visual | 6fffaa2f L100-198 |
| internal joints | 无（cabinet 是 root；paddle/tray/bottle 由 Slot A/C 发出）| — |
| downstream interface | alcove 顶 tap mount + 顶 collar（供 paddle 与倒装瓶接入）| 6fffaa2f L200-221 |

### Slot B / body_form — cylindrical_urn
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`(lathe 平台 root) + `urn`(lathe 桶身 + band + lid + knob，FIXED) | b7793c5c L230-293 |
| internal joints | `base_to_urn` FIXED | b7793c5c L287-293 |
| downstream interface | 桶壁周向 mount(`URN_R_AT_FAUCET` + yaw)（供 faucet 周向复制）| b7793c5c L296-334 |

### Slot C / base_reservoir — countertop
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无额外 part（drip_tray = body_form 的 root）| P1 L140-160 |
| internal joints | 无 | — |
| upstream interface | 坐台面 z=0 | P1 run_tests grounding |

### Slot C / base_reservoir — floor_standing_pedestal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedestal_cabinet`(toe_kick + shell + top_plate + door_panel + handle，新 root) | 9a1aa34a L90-159 |
| internal joints | `pedestal_to_tray` FIXED（drip_tray 坐柜顶；其余主体顺链叠上）| 9a1aa34a L199-205 |
| upstream interface | toe_kick 接地 z=0；drip_tray/column 叠装柜顶 | 9a1aa34a L198-237 |

### Slot C / base_reservoir — removable_drip_tray
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drip_tray`(改活动件，rim+floor+perforated_plate) | 7e820f42 L295-312 |
| internal joints | `tray_slide` PRISMATIC axis=(0,-1,0)（抽出）/ `drip_tray_lift` PRISMATIC axis=(0,0,1)（提起），lower=0 / upper≈TRAY_SLIDE | 7e820f42 L315-324 / 6fffaa2f L299-307 |
| upstream interface | tray seat（countertop 前沿或 cooler alcove 底）| 7e820f42 L315-321 |

### Slot C / base_reservoir — inverted_top_bottle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `water_bottle`/`bottle`(lathe 倒装瓶 shell) | 870bb3bc L438-443 / 6fffaa2f L310-315 |
| internal joints | `tower_to_bottle`/`cabinet_to_bottle` FIXED（坐顶 collar/socket，非活动）| 870bb3bc L445-452 / 6fffaa2f L316-322 |
| upstream interface | bottle neck 嵌主体顶 collar bore（captured overlap）| 6fffaa2f L354-360 |

### faucet_count multiplicity（faucet+tap_type 子件+tap_handle 复制）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `faucet_{i}`(+对应 tap_type 子件 `tap_handle_{i}`/`push_button_{i}`/`spigot_knob_{i}`/`paddle_{i}`)；共享 mesh 对象 N 复用 | P4 `for i, fx in enumerate(FAUCET_XS)` L221-254（权威源）|
| joints | 每个 faucet 一个 FIXED 挂载 + 一个独立 tap_type 活动关节（REVOLUTE/PRISMATIC）| P4 L231-254 |
| placement | `for i in range(N)`，沿主体正面 X **绝对式**等距（rectangular_box: `FAUCET_XS`）/ 周向等角（cylindrical_urn: yaw fan）/ alcove 内对称（bottled_cooler: ±TAP_Y）| P4 L227 / b7793c5c L296 / 6fffaa2f L202-251 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| tap_type | enum | push_lever / push_button / twist_spigot / paddle | push_lever | choice | sampler 选；主机构（互斥，全机同型）；paddle 由 body_form gate（见 §9）| module table |
| body_form | enum | rectangular_box / bottled_cooler_cabinet / cylindrical_urn | rectangular_box | choice | sampler 选；决定主壳 mesh + faucet 挂载父件 + 布列方式 | module table |
| base_reservoir | enum | countertop / floor_standing_pedestal / removable_drip_tray / inverted_top_bottle | countertop | choice | sampler 选；countertop/floor_pedestal 改 root（互斥）；removable_tray/top_bottle 为可叠加可选件（见 §9）| module table |
| faucet_count (N) | int | 声明产品域 [1,4]；sweep 采样域 [1,4]（偏小加权：1/2 高频、3 常见、4 长尾）| 1 | conditional→slot_choice | 编入 slot_choice 为 `("faucet_count", f"n{N}")`（拓扑维度）；N 与 body_form 联动（见下不等式 + §8）| P4 / P3 / P1 |
| palette_style | enum | brushed_steel / matte_black_chrome / white_cooler / copper_urn / pastel_dispenser | brushed_steel | palette | palette only，**不计入 slot_choice**；按 seed 采样（见下 colorway）| 各样本材质 |
| body_height_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放主体高（column/cabinet/urn 高 → faucet 挂载 Z），clamp | resolve clamp |
| body_footprint_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放主体/托盘 XY 主尺寸（保比例），clamp | resolve clamp |
| faucet_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放正面/周向龙头间距 | resolve clamp |
| tap_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放出水阀活动 `motion_limits.upper`（REVOLUTE ≤π·0.45 / button ≤0.015），clamp | resolve clamp |
| tray_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 removable_drip_tray 有效；缩放 PRISMATIC upper（≤ 抽出/提起暴露所需） | resolve clamp |
| (—) | constraint | — | — | inequality | 龙头排布不超主体正面/周长：`N·faucet_w + (N-1)·gap ≤ front_span − 2·margin`（urn 用周长 `2πR`）；违反时按比例缩 gap 或拒绝重采（cylindrical_urn 桶细，N 上限更小）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 每个 spout 出水位落在 drip_tray footprint 内（`expect_within` spout↔tray）| 接口 / clearance |
| (—) | constraint | — | — | conditional | tap_type=paddle 要求 body_form=bottled_cooler_cabinet（paddle 悬挂于 alcove 顶，非立柱/桶壁原生）；否则 gate 回退 push_lever（见 §9）| 接口 |
| (—) | constraint | — | — | conditional | base_reservoir=inverted_top_bottle 要求主体顶有 collar/socket（rectangular_box / bottled_cooler 有；cylindrical_urn 顶为 lid → gate 关闭或改 collar mesh）| 接口 |

**palette_style colorway（≥3，目标 4-6，按 seed 采样；palette only 不计 slot_choice）**：
| palette_style | 主体 | 出水阀/五金 | 配色来源 |
|---|---|---|---|
| brushed_steel（标称） | brushed/polished steel 立柱+托盘 | chrome faucet + gloss_black grip | P1/P3/P4 brushed_steel+chrome+gloss_black |
| matte_black_chrome | dark_matte 立柱/柜 | polished chrome 阀 + gloss_black | P1 dark_matte + chrome / ffb293c3 polished_steel |
| white_cooler | body_white 柜 + body_gray 件 | chrome 阀 + hot_red/cold_blue 指示 | 6fffaa2f body_white/body_gray/hot_red/cold_blue |
| copper_urn | dark_matte/铜 urn + chrome band | chrome 阀 + gloss_black grip | b7793c5c dark_matte+chrome band |
| pastel_dispenser | 浅色柜体 | chrome 阀 + 彩色按钮/拨片 | 合成（柔和饮料机配色）|

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 tap_type / body_form / base_reservoir / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（出水龙头数）：

- **count_param**：`faucet_count`（模板内变量 N / NUM_FAUCETS；主体正面/周向并排出水阀数）。
- **N_range**：声明产品域 **[1, 4]**。**保守取 [1,4] 而非 source map 建议的 [1,8]**：母资产仅 N∈{1(P1),3(P3),4(P4)} 有样本，source map 称 N=2/6 由 fork 补——但**这两个 faucet-count fork record 与 dual(003.png) 在本仓库 `data/records/` 中不存在**（见 §排除项），故无 N=2/5/6/7/8 的专属几何验证样本，N>4 与 N=2 仅靠 `for i in range(N)` 复制骨架插值，保守封顶 N=4（P4 已实证 4 龙头）。reviewer 可决定是否放宽到 [1,6]。`config_from_seed` 的 sweep 采样域 **[1, 4]**（偏小加权：N=1/2 高频、N=3 常见、N=4 稀疏）。N=1 即 P1/单龙头退化（不进循环或 range(1)）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((1,2,3,4), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,4]，并按 body_form 二次 clamp（cylindrical_urn 桶周长小 → N≤3）。
- **copied object**：单只出水阀单元——`faucet_{i}`(faucet_body+bonnet+spout) + 对应 tap_type 活动子件(`tap_handle_{i}` / `push_button_{i}` / `spigot_knob_{i}` / `paddle_{i}`)，共享 mesh 对象发射（P4 已 `faucet_mesh`/`collar_mesh`/`grip_mesh` 模板复用，N 个 visual 复用同一几何）。
- **naming**：`faucet_{i}` / `tap_handle_{i}`（+ `faucet_lever_{i}` / `body_to_faucet_{i}`），`for i in range(N)`（P4 L227 `for i, fx in enumerate(FAUCET_XS)` + twist_spigot L298 / cylindrical_urn L296 / drip_tray L249 / inverted_top_bottle L457 均已用此结构，可直接作 copy-logic 源）。
- **placement**：**绝对式**等距——rectangular_box: 沿主体正面 X 以中心对称(`FAUCET_XS = (-1.5,-0.5,0.5,1.5)·pitch`)；cylindrical_urn: 绕桶壁等角扇出(`angle = (i-(N-1)/2)·fan`)；bottled_cooler: alcove 内对称(±TAP_Y)。绝对式（每 i 的位姿由 N 与中心解析，不累加漂移）是 N-不变前提。
- **joint policy**：每个 faucet 一个 FIXED 挂载 + 一个**独立**tap_type 活动关节（REVOLUTE 或 PRISMATIC）；各龙头独立操作（P3/P4 run_tests 已验证 independent articulation）。
- **source/gating**：copy-logic 权威源 P4 `for i, fx in enumerate(FAUCET_XS)` L221-254（N=4 共享 mesh + 沿 X 等距 + 独立 REVOLUTE）；N=3 取 P3 扇形；**N=1 取 P1 单 faucet**（等价 range(1)）。N 与 body_form 兼容由 §9 矩阵 gate（cylindrical_urn 限 N≤3；bottled_cooler paddle 通常 N=2 hot/cold）。

## 拓扑多样性审计

总组合数（在 body_form/paddle gate 约束下，非自由笛卡尔积）：
- tap_type(4) × body_form(3) × base_reservoir(4) × faucet_count(4) 的**自由上界** = 192；
- 实际合法组合（gate 后约）：rectangular_box × {push_lever,push_button,twist_spigot}(3) × base(4) × N(4) = 48；bottled_cooler_cabinet × {push_lever,push_button,twist_spigot,paddle}(4) × base(4) × N(1-2) ≈ 24；cylindrical_urn × {push_lever,push_button,twist_spigot}(3) × base(4) × N(≤3) ≈ 27 → **合计约 ≈ 99 个合法拓扑组合**（未计 palette 与连续 scale）。

仅 tap_type(joint 拓扑：REVOLUTE-Y lever / PRISMATIC-Z button / REVOLUTE-X spigot / REVOLUTE-Y paddle) × base_reservoir(空 / FIXED 改 root / PRISMATIC tray / FIXED 倒瓶) = 真正的 joint-topology 差异层，单这两轴即 ≥10 distinct。

理由：tap_type 提供 4 种出水阀 joint 拓扑（lever REVOLUTE / button PRISMATIC / spigot REVOLUTE@流轴 / paddle REVOLUTE@悬挂）× base_reservoir 提供 4 种接地/活动拓扑（含 PRISMATIC 抽拉 tray）× body_form(3) × N(4) → 合法组合 ≈99 ≫ 10。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("faucet_count", f"n{N}")`，对齐 cushion/shopping_bucket/candy_vending_machine），否则单龙头与多龙头 slot_choice 同形，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` body_form → 按兼容矩阵从合法集采 tap_type（paddle 仅 bottled_cooler）→ 采 base_reservoir（按 body_form/顶 collar 合法化 inverted_top_bottle）→ `rng.choices` 加权 N∈[1,4]（按 body_form clamp 上界）→ uniform 各连续 scale。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 body_height_scale / body_footprint_scale / faucet_spacing_scale（conditional@N≥2）/ tap_travel_scale / tray_travel_scale（conditional@removable_drip_tray）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：faucet_spacing 仅 N≥2、tray_travel 仅 removable_drip_tray、N 上界随 body_form）→ 采 independent body_height/footprint/tap_travel scale → 派生（faucet 挂载 Z 随 body_height）→ 用两条 clearance inequality（龙头不超正面/周长、spout 落在 tray 内）投影/回缩。跨部件依赖（龙头排布 vs 正面跨度、spout vs tray footprint）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 bonnet/collar origin、captured-pin/slide 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` body_form → 兼容矩阵采 tap_type → 采 base_reservoir → `rng.choices` 加权 N∈[1,4]（body_form clamp）→ uniform scale | slot_choices_for_seed 含 `("faucet_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **paddle × body_form**：paddle 悬挂于 alcove 顶 → 仅 bottled_cooler_cabinet 合法；rectangular_box / cylindrical_urn + paddle → gate 回退 push_lever。 (2) **inverted_top_bottle × body_form**：需主体顶 collar/socket → rectangular_box / bottled_cooler 合法；cylindrical_urn 顶为 lid → gate 关闭 top_bottle（或改 urn 顶 collar mesh）。 (3) **N × body_form**：cylindrical_urn 桶周长小 → N≤3；bottled_cooler paddle 形态 N 多为 2(hot/cold)，封顶 N≤2；rectangular_box N≤4。 (4) **removable_drip_tray 方向 × base root**：countertop/rectangular_box→ -Y 抽出(`tray_slide`)；bottled_cooler→ +Z 提起(`drip_tray_lift`)；floor_pedestal 与 removable tray 共存（tray 在柜顶可抽）。 (5) tap_type 全机同型（不混阀）。 | no floating / paddle 悬空 / top_bottle 无 collar 穿模 / 龙头超正面 / spout 不落 tray / 行程不足 |
| controlled local variation | 5 个 clamped scale（body_height、body_footprint、faucet_spacing@N≥2、tap_travel、tray_travel@removable），每 build 统一；faucet_spacing/tray_travel 为 conditional | 比例变化不破坏 bonnet/collar origin、captured 接口、spout 落 tray、坐地、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐阀型/逐 base QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A tap_type | 4 | yes | yes | REVOLUTE-Y lever / PRISMATIC-Z button / REVOLUTE-X spigot / REVOLUTE-Y paddle（互斥主机构）|
| B body_form | 3 | yes | yes | 立柱塔 / 实柜 alcove / lathe 圆筒 |
| C base_reservoir | 4 | yes | yes | countertop / floor pedestal / PRISMATIC removable tray / FIXED 倒瓶 |
| faucet_count (N) | 4（采样域 {1,2,3,4}，1/2 高频 / 4 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("faucet_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,4]
- `resolve_config` 把 faucet_count clamp 到 [1,4] 并按 body_form 二次 clamp（urn≤3、cooler-paddle≤2）；各 scale clamp 到声明范围；faucet_spacing/tray_travel 为 conditional 随 N / base_reservoir 解析；两条 clearance inequality 在 resolve 内投影/回缩
- compatibility matrix / gating 阻止非法组合（paddle 仅 bottled_cooler；inverted_top_bottle 需顶 collar；urn N≤3；tap_type 全机同型）
- 连续 scale clamp 后不破坏 bonnet/collar origin / captured-pin/slide 接口 / spout 落 tray / 坐地 / N 复制
- 关键 joint：push_lever `faucet_lever_{i}` REVOLUTE axis≈Y(P1)/X(P3/P4)；push_button `faucet_button_{i}` PRISMATIC axis≈(0,0,-1)；twist_spigot `faucet_spigot_{i}` REVOLUTE axis≈(1,0,0)；paddle `paddle_hinge_{i}` REVOLUTE axis≈(0,1,0)；removable tray `tray_slide`/`drip_tray_lift` PRISMATIC axis≈(0,-1,0)/(0,0,1)；inverted bottle FIXED
- captured-pin / slide / collar：element-scoped `allow_overlap`（`lever_collar`↔`bonnet`/`pivot_boss`；`button_stem`↔`faucet_bonnet`；`spigot_stem`↔bonnet；`hinge_barrel`↔`tap_body`；faucet shank↔主壳；bottle neck↔collar），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `faucet_{i}`/`tap_handle_{i}` 命名 + 绝对式等距/等角 placement + 各龙头独立活动关节
- grandfather：所有 hinge/slide/collar/bottle captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 单龙头与多龙头 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- 在 rectangular_box / cylindrical_urn 上发射 paddle（悬挂拨片无 alcove 顶承载）→ 悬空；必须 gate paddle 仅 bottled_cooler_cabinet。
- inverted_top_bottle 装在无顶 collar/socket 的主体（如 urn lid 顶）→ 瓶悬空/穿模；gate 需顶 collar。
- cylindrical_urn 上塞 N=4 龙头 → 桶周长不够，龙头互撞；urn 限 N≤3，违反 §7 周长不等式则回缩。
- 出水阀做成静态 visual 而无活动关节（lever 不翻 / button 不压 / spigot 不转 / paddle 不推）→ 失活动语义。
- faucet shank/collar/stem origin 放在主壳中心或任意点而非真实 bonnet boss / collar → `fail_if_articulation_origin_far_from_geometry`(0.015) FAIL。
- 给 captured-pin / captured-slide / bottle-neck 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- faucet_spacing 过大致龙头超出主体正面/托盘 → §7 第一条不等式 FAIL；按比例缩 gap。
- spout 出水位不落 drip_tray footprint → §7 第二条不等式 FAIL（所有样本 `expect_within` spout↔tray）。
- 一台机内混用多种 tap_type（如 1 lever + 1 button）→ 不符样本（全机同阀型）；tap_type 全机统一。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"单体水龙头 / 除湿机水桶 / 净水器滤芯"语义混入 → 出类，本类是"主体 + 1..N 出水阀 + 接水盘 + 可选倒瓶"整机。

## 与相邻类别的边界

- 不该混入：**单体水龙头 / faucet（厨卫龙头，`rec_faucet_with_side_handle_*`）**——装在台盆上的单个龙头，无主体/无多阀/无接水盘整机身份；本类是整机分配器。
- 不该混入：**除湿机 / dehumidifier（`rec_dehumidifier_with_pullout_water_bucket_*`）**——抽拉水桶收集冷凝水，无饮用出水阀；虽同有 PRISMATIC 抽屉，但无出水身份。
- 不该混入：**水车 / waterwheel（overshot/undershot）**——水力旋转机械，与饮料分配无关。
- 不该混入：**净水器 / 滤水壶 / 咖啡机 / 自动售卖机**——本类聚焦"主体 + 1..N 机械出水阀 + 接水盘 + 可选倒装水箱"，无屏幕/制冷/滤芯/螺旋货道。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **N_range 取 [1,4] 保守**（faucet-count-2/6 fork 与 dual record 磁盘缺失，见 §排除项）还是放宽到 source map 的 [1,8]/[1,6]——放宽到 [1,6] 可令 topology distinct 越过 100；(2) tap_type 全机同型 vs 允许混阀（样本均同型 → 取同型）；(3) paddle 仅 bottled_cooler_cabinet 的 gate、inverted_top_bottle 需顶 collar 的 gate、urn N≤3 的 gate 是否接受；(4) base_reservoir 中 removable_drip_tray 与 inverted_top_bottle 作为"可叠加可选件" vs countertop/floor_pedestal 作为"互斥 root"的混合 slot 语义是否清晰；(5) body_form 建模为主壳 mesh + faucet 父件维度（rectangular_box 同时覆盖 P1 立柱与 P4 T 横梁两种 sub-mesh）是否需拆为独立 slot）|

## 模板实现备注（可选）
- 共享 helper：`_tray_basin_geometry`/`_build_tray_*`（drip-tray mesh）、`_spout_geometry`（下弯 spout，P1/P3/cylindrical_urn 通用）、`_faucet_body_geometry`/`_faucet_bonnet_geometry`（faucet）、`_handle_grip_geometry`/`_handle_ferrule_geometry`（lever grip）、`KnobGeometry`(twist_spigot knob)、`_cabinet_shell`(bottled_cooler alcove)、`_urn_shell_geometry`/`_base_geometry`(cylindrical_urn lathe)、`_bottle_geometry`/`_inverted_bottle_geometry`(倒装瓶 lathe)。faucet/tap_handle mesh 在 N 复制中复用同一对象（P4 范式）。
- captured 接口 allow_overlap：`run_water_dispenser_tests` 里逐机构补 element-scoped `allow_overlap`（lever_collar↔bonnet / button_stem↔bonnet / spigot_stem↔bonnet / hinge_barrel↔tap_body / faucet shank↔主壳 / bottle neck↔collar），照搬各样本 run_tests 段（P1 L325-340、P4 L271-299、1a8f4bb6 L346-361、ffb293c3 allow_overlap 段、6fffaa2f L340-360、b7793c5c 段）。
- conditional 范围解析顺序：先采 body_form → tap_type(paddle gate) → base_reservoir(top_bottle collar gate) → N（body_form clamp 上界）→ 解析 faucet_spacing(仅 N≥2)/tray_travel(仅 removable)/faucet 父件(body_form 决定挂哪) → 采 body_height/footprint/tap_travel independent scale → 派生 faucet 挂载 Z → 投影两条 clearance inequality。
- N=1 退化：直接用 P1 单 faucet（不进 range 循环），等价 range(1)；N≥2 走 P4 `for i in range(N)` 共享 mesh 复制。
- root 切换：base_reservoir=countertop → drip_tray 为 root；floor_standing_pedestal → pedestal_cabinet 为 root（drip_tray/column 顺链 FIXED 叠上，照 9a1aa34a `pedestal_to_tray`）；bottled_cooler_cabinet body_form 自带 cabinet root。
- 参考模板：`agent/templates/candy_vending_machine.py`（同为 mixed parallel_children chassis + multiplicity：接地 body + 多机构挂 body + selector/faucet 复制 + chassis-profile gating + captured-pin allow_overlap 骨架，本类可同构改编）；`agent/templates/Accessories_Cushion.py`（`("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 兼容矩阵 gating 范式）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（parent 基线）| push_lever + rectangular_box + countertop（N=1）| rec_model-…single…_b6696ffc | `_tray_basin`/`_spout` + `drip_tray`+`tower_column`+`faucet`+`faucet_lever` REVOLUTE L56-312 / allow_overlap L325-340 | 单龙头 push_lever 基线 + 立柱主体 + countertop + spout helper + captured-pin 范式 |
| S2 | A/B/C + N | push_lever + rectangular_box + countertop（N=3 扇形）| rec_model-…triple…_acfaa2cf | `FAUCETS` 扇形站位 + `{side}_tap_pivot` REVOLUTE L46-248 | N=3 扇形龙头 copy（flared column）|
| S3 | A/B/C + N（权威复制源）| push_lever + rectangular_box(T) + countertop（N=4）| rec_model-…four-tap…_3f3a9da3 | `for i, fx in enumerate(FAUCET_XS)` 共享 mesh `faucet_{i}`+`tap_handle_{i}_pivot` REVOLUTE L221-254 | **faucet_count 多重性权威源**（共享 mesh + 沿 X 等距 + 独立 REVOLUTE）+ T 型 header_box |
| S4 | A/B/C（同源四件）| paddle + bottled_cooler_cabinet + removable(+Z lift) + inverted_top_bottle | rec_model-…cooler…_6fffaa2f | `cabinet`+alcove+collar L100-198 / `*_paddle`+`*_paddle_hinge` REVOLUTE Y L223-251 / `drip_tray_lift` PRISMATIC +Z L299-307 / `bottle`+`cabinet_to_bottle` FIXED L310-322 | paddle 主机构 + 瓶装冷水柜主体 + PRISMATIC 提起 tray + 倒装瓶 4 来源同源样本 |
| S5 | A | push_button | rec_variant-tap-type-push-button-…_1a8f4bb6 | `push_button`(stem+cap)+`faucet_button` PRISMATIC -Z L259-333 / allow_overlap L346-361 | 按钮阀（PRISMATIC 压入 + stem 捕获 bonnet）|
| S6 | A | twist_spigot | rec_variant-tap-type-twist-spigot-…_ffb293c3 | `spigot_knob_{i}`(stem+KnobGeometry)+`faucet_spigot_{i}` REVOLUTE +X L265-323 | 旋塞阀（绕流轴 REVOLUTE）+ faucet 复制循环 |
| S7 | B | cylindrical_urn | rec_variant-body-form-cylindrical-urn-…_b7793c5c | `base`+`urn` lathe L70-293 + `for i in range(FAUCET_COUNT)` 周向 faucet L296-373 | 圆筒饮料桶主体（周向龙头扇出）|
| S8 | C | floor_standing_pedestal | rec_variant-base-floor-standing-pedestal-…_9a1aa34a | `pedestal_cabinet`(toe_kick+shell+door) root + `pedestal_to_tray` FIXED L90-205 | 落地柜 root（tray/column 叠上）|
| S9 | C | removable_drip_tray（抽出式）| rec_variant-base-removable-drip-tray-…_7e820f42 | `drip_tray`+`tray_slide` PRISMATIC -Y L295-324 + `for i in range(NUM_FAUCETS)` L249-361 | 抽拉 drip-tray（countertop -Y 抽出）|
| S10 | C | inverted_top_bottle（reservoir）| rec_variant-reservoir-inverted-top-bottle-…_870bb3bc | `water_bottle`+`tower_to_bottle` FIXED L438-452 + `for i in range(NUM_FAUCETS)` L457 | 顶置倒装水瓶 FIXED 水箱 |
