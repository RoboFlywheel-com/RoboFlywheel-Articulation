# Chair / Folding chair — Modular Spec

> 来源小类：`picture/Chair/Folding chair`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Chair__Folding_Chair_Chair.md`。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自 1 个 parent + 20 个 fork 变体（`chair_folding_chair_gpt55_20260611` 批次，openai / gpt-5.5 / med，全 rc=0、全有 URDF、全 converged），**目前仍在 `articraft_data` 仓库，尚未同步进本仓库 `data/records/`**。进入 TEMPLATE_AFTER_REVIEW 阅读 / 实现前，需先把被采纳的 record 目录 + 物化缓存同步进本仓库 `data/records/` 并批量 `rating=5`（FORK_VARIANTS §7）。下方所有行号按 **当前 articraft_data 仓库** 的 `revisions/rev_000001/model.py` 计；同步后须按本仓库重新落地的 `model.py` rebase 行号。

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_chair` |
| template path | `agent/templates/Chair_Folding_chair.py` |
| test path (optional) | `tests/agent/test_folding_chair_template.py`（不写，sweep 为唯一验收） |
| stage | `SPEC_ONLY` |
| status | `spec_only` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots：fold 主机构 + seat_back_panel + frame_style + accessory，挂到共同 scissor 骨架；无 multiplicity） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 21（1 parent + 20 fork 变体，全部 converged，workbench-only，batch rating=5）|
| read_count | 13（parent `cc9b62cf` 全文；fold 槽 v02/v07/v10/v20 的机构段与装配段；accessory 槽 v08/v13/v16/v19 的 part+joint 段；frame 槽 v12/v18 的 helper+root 段；seat 槽 v17 cane/arched helper 段 + v01/v03/v09/v11 的 `_*_mesh` helper 段）|
| read_scope | 提供模块来源的样本全部读；纯比例/姿态重复格子样本（v04 beach / v05 vinyl 厚垫 / v06 director / v14 child / v15 heavy-duty）按 source map 判定为冗余（headline 轴为连续 scale，非新拓扑），未单独全文读 |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表 |

冗余说明：
- v04（beach 低斜）/ v06（tall director 高）/ v14（child 小）/ v15（heavy-duty 宽）/ v16-headline（narrow 窄）的"headline 差异"都是**连续比例/姿态**（座高 / 座宽 / 靠背角 / 整体缩放），不是新拓扑模块 → 折入 §7 连续尺寸参数，**不进 slot 候选**（source map "连续尺寸参数"节 + FORK_VARIANTS §2）。
- v05（padded_vinyl 厚垫）与 parent `_pad_mesh` 同 helper（仅厚度差），是 seat 槽 `padded_pad` 的尺寸变体，不另列 candidate。

## 核心身份

可坐人后能折叠收平的单椅（sit-on folding chair）。核心机构是**剪刀折叠（scissor fold）单 DOF**：`rear_leg_frame`（root）后腿向前上抬，过侧向交叉销（scissor pivot）继续上升成靠背立柱、并携带座板后铰杆与靠背；`front_leg_frame`（child）前腿向后上抬，过同一交叉销上升成座前杆；两者以一个 **REVOLUTE（+Y 轴）`fold_pivot`** 在交叉销处铰接。座板 `seat_pan`（child of rear）后缘铰在后铰杆、前缘搭在 front 的座前杆上，其 `seat_hinge` 用 **Mimic 跟随 `fold_pivot`**（multiplier≈0.49）使前缘始终贴前杆——展开时座板水平在坐高（~0.45 m），折叠时座板抬竖、四足沿地面收拢、整椅打平。默认成熟域：单椅、单（或少量）折叠 DOF。活动语义是"绕侧向交叉销折平 + 座板联动翻竖 + 可选附件铰"。

所有变体共享固定骨架 helper `_leg_tube` / `_cross_tube`（管腿 + 交叉撑 + 落地足印），这是模板固定脊柱；座/背板按变体各换一个 `_*_mesh` helper（最干净的可换模块）。

不该混入：见 §11。

## 槽位 + 候选模块表

> **建模注记（重要）**：4 个 slot **不是串联链**，而是挂在共同 scissor 骨架（rear/front 双腿架 + seat_pan）上的 `parallel_children`：
> - **fold_mechanism** 决定 root/child 腿架的折叠拓扑（基线 3 关节剪刀，或加第 2 个 fold 子件 → 4-5 关节）——它定义骨架本身。
> - **seat_back_panel** 只换 `seat_pan` 与 backrest 的 `_*_mesh` visual helper（**不改 part tree / joint**，纯 visual 模块）。
> - **frame_style** 换骨架管材原语（圆管 tube ↔ 扁条 Box flat-bar）+ 材质/铰板。
> - **accessory** 可选地新增 1 个独立活动子件（写字板 / 翻竖靠背 / 提手挖孔 / 翻下脚踏）。
> 它们的笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：fold_mechanism（主机构槽——椅子的折叠骨架与折叠动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| scissor_cross_brace（基线） | rec_..._cc9b62cf (parent) | root L118-185 / front L187-236 / `fold_pivot`+`seat_hinge` L238-284 | eligible if compatible | 单交叉剪刀：rear(root) + front(child) 双腿架，1 `fold_pivot` REVOLUTE(+Y) + 1 `seat_hinge` REVOLUTE(+Y, mimic) = **3 非 fixed 关节**；下层 rear/front cross_brace |
| reinforced_double_cross_brace | rec_..._4a3e7936 (v10) | `rear_upper_cross_brace` L176-189 / `front_upper_cross_brace` L255-268 | eligible if compatible | 在 rear/front 平面各加第 2 道高位横撑（front 撑随腿动），加大灰橡胶脚帽；关节数仍 3，骨架更刚 |
| triangular_folding_frame | rec_..._a5de1983 (v07) | `rear_triangle_brace_*` L128-139 / `front_triangle_brace_*` L218-231 | eligible if compatible | 每侧加对角压杆把脚直连座前杆/铰杆 → 三角折叠侧架（stool 高常配，但三角拓扑独立于高度）；关节数 3 |
| rear_legs_fold_under | rec_..._fcc91b91 (v02) | `rear_under_frame` part L319-368 / `rear_leg_fold` REVOLUTE L370-378 / hinge_tab L170-182 | eligible if compatible | 新增内置后支撑腿子件 `rear_under_frame`，自带 `rear_leg_fold` REVOLUTE(+Y) 向架下翻折 = **4 非 fixed 关节**；销眼 captured-pin |
| collapsing_side_hinge_links | rec_..._dad421cd (v20) | `side_links` part L364-395 / `side_link_hinge` REVOLUTE+mimic L396-405 | eligible if compatible | 新增侧铰链 U 形连杆子件 `side_links`，`side_link_hinge` REVOLUTE(-Y, mimic 跟 fold) 把座拉成扁束 = **4 非 fixed 关节**（fold+seat+side_link）|

### Slot B：seat_back_panel（座/背板填充——每候选一个 `_*_mesh` helper；纯 visual，挂在 `seat_pan` + backrest）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| padded_pad（基线） | rec_..._cc9b62cf (parent) | `_pad_mesh` L101-107 | eligible if compatible | 圆角矩形垫 + 柔顶 pad（ExtrudeGeometry body+top merge）；vinyl 厚垫即同 helper 尺寸变体 |
| molded_plastic | rec_..._fcc91b91 (v02) | `_pad_mesh`(molded) L102-116 + 底肋 `seat_rib_*` L290-298 | eligible if compatible | 模塑壳 shell+dish+lip 三层 merge + 底面加强肋 Box（真实模塑特征，非换色）|
| fabric_sling | rec_..._5571b31a (v01) | `_sling_mesh` L102-110 | eligible if compatible | 薄缝纫吊布 body + 浅冠 inset merge |
| canvas | rec_..._17cd26af (v12) | `_canvas_mesh` L101-109 | eligible if compatible | 薄帆布 body + 凸缝边 hem merge |
| perforated_plastic | rec_..._74b2022d (v09) | `_perforated_plastic_panel` L100-111 | eligible if compatible | `PerforatedPanelGeometry`：真实通孔阵列 + 实心边框（结构 primitive，非 Extrude）|
| wood_slat | rec_..._8c1cac12 (v03) | `_slat_y_positions` L111-116 + 座/背 slat 循环 L194-204 / L274-285 | eligible if compatible | N 根木条沿 Y 循环发射（座 + 背各一组），非整片板 → part-local 复制件 |
| polycarbonate_translucent | rec_..._364067f0 (v11) | `_panel_mesh` L101-117 | eligible if compatible | 单连接半透插板（ExtrudeGeometry 整片）|
| woven_cane | rec_..._0b7e3fd9 (v17) | `_cane_panel_mesh` L111-143 + `_arched_back_rail` L154-165 | eligible if compatible | 编藤面（底板 + 双向凸条 merge + 厚边框）+ 弓形拱背杆（额外 visual）|
| fabric_bucket | rec_..._dad421cd (v20) | `_fabric_bucket_mesh` L114-157 / `_fabric_back_mesh` L160-201 | eligible if compatible | 下沉吊兜（`MeshGeometry` 程序网格，边缘抬升、中心下垂）+ 杯形背布 |

### Slot C：frame_style（管材/边框样式——换骨架原语与材质，结构不改 part tree）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tubular_steel（基线） | rec_..._cc9b62cf (parent) | `_leg_tube`/`_cross_tube` L84-98 | eligible if compatible | 圆钢管 `tube_from_spline_points` 腿/撑（默认原语）|
| aluminum_tube | rec_..._5571b31a (v01) | `_leg_tube` 同源 + aluminum 材质 L84-98 | eligible if compatible | 同圆管原语、轻量铝材质 + 细管半径；与 tubular 同拓扑、不同 palette/scale → **last-resort 列入仅为材质族区分** |
| wood_side_frame | rec_..._17cd26af (v12) | `_leg_tube` + dark_wood 材质 L84-98,128-160 | eligible if compatible | 圆截面木侧框（同 tube 原语、木材质 + 销钉视觉）|
| flat_bar_angular | rec_..._93e9880f (v18) | `_flat_bar_between`/`_flat_bar_path`/`_cross_flat_bar` L105-142 + `*_pivot_hub_*` L186/271 | eligible if compatible | **扁条 Box 原语**（非 tube）沿折线发射的角形侧框 + 圆 pivot hub；与 tube 原语正交的几何族 |

> 硬约束记录：frame_style 真正结构互异的只有 `tubular`(圆管) 与 `flat_bar_angular`(扁条 Box) 两族；`aluminum_tube` / `wood_side_frame` 与 tubular 同原语、仅换材质/半径，机械上属 palette。列为 4 candidate 是为对齐 source map 的样本格子（aluminum/wood 在上游各占一格、各有独立 5 星样本），但 **§9 拓扑去重时按"原语族" 折算**：frame_style 提供 **2 个真实拓扑等价类**（tube vs flat_bar）。多样性主由 fold × seat 提供，见 §9。

### Slot D：accessory（附加机构——各自带一个独立活动 joint 或 visual 特征；含 `plain` 空选项）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain（基线） | rec_..._cc9b62cf (parent) | — | eligible if compatible | 无附件，关节数由 fold 槽决定 |
| pivoting_tablet_arm | rec_..._659ae563 (v08) | `tablet_arm` part L347-364 / `tablet_pivot` REVOLUTE(+Z) L365-373 / `_tablet_steel_mesh` L110-133 | eligible if compatible | 新增写字板臂子件，绕侧柱 REVOLUTE(**+Z 轴**，水平旋开) +1 关节；焊接钢套+臂+板 |
| reclining_backrest_2nd_hinge | rec_..._929d0eb3 (v13) | `backrest` 独立 part L215-274 / `back_recline` REVOLUTE(-Y) L276-284 | eligible if compatible | 把靠背拆成独立 `backrest` part，`back_recline` REVOLUTE(-Y) 第 2 锁定铰 +1 关节 + lock_pin 视觉 |
| carry_handle_cutout | rec_..._1d9acfc6 (v16) | `_handle_backrest_mesh`（`BezelGeometry` 挖孔）L113-126 | eligible if compatible | 靠背开通手提孔（`BezelGeometry` opening slot）；**无新关节**（visual 特征类附件，靠 bezel 几何区分）|
| flip_down_footrest | rec_..._150f16e4 (v19) | `footrest_bar` part L330-345 / `footrest_flip` REVOLUTE(-Y, mimic) L346-360 / `_footrest_loop` L118-132 | eligible if compatible | 新增前腿联动翻下脚踏子件，`footrest_flip` REVOLUTE(-Y, mimic 跟 fold) +1 关节；U 形环+rubber tread |

## 槽位图（slot graph）

pattern: `parallel_children`（固定 named slots 挂共同 scissor 骨架；无 multiplicity）

```
                         scissor 骨架（由 fold_mechanism 槽定义）
rear_leg_frame (ROOT, frame_style 原语)
   ├──[fold_pivot: REVOLUTE +Y @ scissor pivot]──> front_leg_frame (frame_style 原语)
   ├──[seat_hinge: REVOLUTE +Y @ rear hinge bar, MIMIC(fold_pivot, ~0.49)]──> seat_pan
   │        └── seat visual = seat_back_panel 槽的 `_*_mesh`
   ├── backrest visual = seat_back_panel 槽的 `_*_mesh`（贴 root 上立柱）
   │
   ├── fold_mechanism 二级子件（按所选 module 之一，可空）：
   │     ├─ rear_legs_fold_under:  rear_under_frame  ──[rear_leg_fold: REVOLUTE +Y]──> (child of rear)
   │     └─ collapsing_side_hinge_links: side_links ──[side_link_hinge: REVOLUTE −Y, MIMIC(fold)]──> (child of rear)
   │
   └── accessory 子件（按所选 module，可空 = plain）：
         ├─ pivoting_tablet_arm:  tablet_arm  ──[tablet_pivot: REVOLUTE +Z]──> (child of rear)
         ├─ reclining_backrest:   backrest    ──[back_recline: REVOLUTE −Y]──> (child of rear)  (靠背改挂此 part)
         ├─ flip_down_footrest:   footrest_bar──[footrest_flip: REVOLUTE −Y, MIMIC(fold)]──> (child of front)
         └─ carry_handle_cutout:  无新 part/joint，仅改 backrest 的 bezel 几何
```

接口点位与 joint 语义：
- **scissor pivot（核心接口）**：rear 与 front 在世界 `PIVOT=(0, z_pivot)` 处交叉共销 → `fold_pivot` REVOLUTE，axis=+Y，origin 锚在交叉销几何上；正 q 把前足后上摆使两腿平面平行、整椅打平。front 视觉相对 pivot 系 author（`local = world − pivot`），q=0 复现展开位。
- **seat 后铰接口**：`seat_pan` 后缘铰在 root 的 `seat_hinge_bar`（世界 `SEAT_HINGE`）→ `seat_hinge` REVOLUTE,axis=+Y,**`Mimic(fold_pivot, multiplier≈0.49)`**；前缘搭在 front 的 `seat_front_rail` 上（captured-rest，靠 mimic 保持贴合）。
- **fold 二级子件接口**：`rear_under_frame` / `side_links` 各以 REVOLUTE 挂在 root 的铰杆/侧销上；mimic 型（side_link）跟 `fold_pivot` 联动，独立型（rear_leg_fold）自由折。
- **accessory 接口**：tablet 绕侧柱竖轴(+Z)；recline 把靠背独立成 part 绕 −Y；footrest 绕 front 前杆 −Y 且 mimic 跟 fold；handle_cutout 只改 backrest bezel、不加 joint。
- **mating policy**：scissor 交叉、座缘搭杆、销眼捕获均为 captured/crossing 几何，非两轴面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin 落在铰杆/销几何上 + element-scoped `allow_overlap`（rear↔front 交叉、front↔seat 搭杆、seat↔hinge_bar 捕获、fold 子件销眼）守 overlap。
- **rest pose**：所有 fold/seat/accessory 联动关节 = 展开值（q=0）→ 椅子站立可坐位；座板水平在坐高、四足贴地、靠背竖立。

## 每槽位 Module Emits / Interfaces

### Slot A / scissor_cross_brace（基线骨架）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_leg_frame`（visuals: rear_upright_l/r、rear_foot_l/r、back_rail_top、seat_hinge_bar、rear_cross_brace、backrest_*）、`front_leg_frame`（front_leg_l/r、front_foot_l/r、seat_front_rail、front_cross_brace）、`seat_pan`（seat visual）| cc9b62cf L118-265 |
| internal joints | `fold_pivot` REVOLUTE +Y（rear→front，limits 0..1.28）；`seat_hinge` REVOLUTE +Y mimic(fold,0.49)（rear→seat）| cc9b62cf L238-284 |
| upstream interface | root = 世界系；四足贴地 z≈0 | cc9b62cf L118-145 |
| downstream interface | scissor pivot（front 接口）、seat_hinge_bar（seat 后接口）、seat_front_rail（seat 前搭杆）| cc9b62cf L246/278/214 |

### Slot A / rear_legs_fold_under（+1 关节）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 增 `rear_under_frame`（rear_under_leg_*、rear_under_foot_*、rear_under_hinge、rear_under_brace）+ root 上 `rear_hinge_tab_*` | fcc91b91 L319-368, L170-182 |
| internal joints | 增 `rear_leg_fold` REVOLUTE +Y（rear→rear_under，lower −1.45..0）| fcc91b91 L370-378 |
| downstream interface | 销眼 captured（hinge_tab 抱 rear_under_hinge，element-scoped allow_overlap + expect_overlap）| fcc91b91 L420-443 |

### Slot A / collapsing_side_hinge_links（+1 mimic 关节）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 增 `side_links`（side_link_l/r、side_hinge_boss_l/r、link_front_crossbar）| dad421cd L364-395 |
| internal joints | 增 `side_link_hinge` REVOLUTE −Y mimic(fold,0.55)（rear→side_links，0..0.75）| dad421cd L396-405 |

### Slot B / seat_back_panel（任一 module，仅 visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part；替换 `seat_pan` 的 seat visual + root 的 backrest visual 为所选 `_*_mesh`（wood_slat 为座/背各一组 part-local slat 循环；fabric_bucket 用 `MeshGeometry`）| 各 seat 槽 helper（见 Slot B 表）|
| internal joints | 无（座/背均为所属 part 的 visual）| — |
| interface | 贴合 seat_pan local 原点（搭前杆/抱铰杆）、贴 backrest 立柱锚点 | parent L260-265, L172-185 |

### Slot C / frame_style（换原语）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 不新增 part；rear/front 的 leg/brace visual 从 `_leg_tube`(tube) 换为 `_flat_bar_path`(Box) 等 + pivot_hub 视觉 | v18 L105-142, L167-271 |
| internal joints | 无（仅换骨架原语/材质，scissor 关节不变）| — |

### Slot D / accessory（任一，含 plain）
| emits | 描述 | 来源 |
|---|---|---|
| parts | tablet→`tablet_arm`；recline→独立 `backrest`；footrest→`footrest_bar`；handle→无新 part（改 backrest bezel）；plain→无 | v08 L347 / v13 L215 / v19 L330 / v16 L113 |
| internal joints | tablet `tablet_pivot` +Z；recline `back_recline` −Y；footrest `footrest_flip` −Y mimic(fold)；handle/plain 无 | v08 L365 / v13 L276 / v19 L346 |
| interface | 各挂 root（tablet/recline）或 front（footrest）的固定锚；mimic 型跟 fold | 同上 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| fold_mechanism | enum | scissor_cross_brace / reinforced_double_cross_brace / triangular_folding_frame / rear_legs_fold_under / collapsing_side_hinge_links | — | choice | 由 deterministic procedural sampler 选；编入 slot_choice | Slot A 表 |
| seat_back_panel | enum | padded_pad / molded_plastic / fabric_sling / canvas / perforated_plastic / wood_slat / polycarbonate_translucent / woven_cane / fabric_bucket | — | choice | 由 sampler 选；编入 slot_choice | Slot B 表 |
| frame_style | enum | tubular_steel / aluminum_tube / wood_side_frame / flat_bar_angular | — | choice | 由 sampler 选；编入 slot_choice（去重按原语族，见 §9）| Slot C 表 |
| accessory | enum | plain / pivoting_tablet_arm / reclining_backrest_2nd_hinge / carry_handle_cutout / flip_down_footrest | — | choice | 由 sampler 选；编入 slot_choice | Slot D 表 |
| material_style | enum | steel_gray / black_powder / aluminum / wood / matte_red / green / ripstop_blue | — | choice | palette only，**不计入 slot_choice** | palette |
| seat_height_scale | float | [0.70, 1.05] | 1.0 | independent | 缩放 PIVOT_Z / SEAT_HINGE_Z / SEAT_FRONT_Z / 足距（stool↔标准椅，覆盖 v07 stool / v04 beach）；四足贴地与 mimic 系数随之派生 | resolve clamp / v07 L53-82 |
| seat_width_scale | float | [0.80, 1.25] | 1.0 | independent | 缩放 HALF_W / SEAT_W / BACK_W（narrow↔heavy-duty，覆盖 v16 narrow / v15 heavy-duty / v14 child）| resolve clamp |
| back_height_scale | float | [0.55, 1.15] | 1.0 | independent | 缩放 BACK_TOP_Z / 靠背高（small stool back ↔ tall director，覆盖 v06 / v07）| resolve clamp |
| back_recline_angle | float | [0.0, 0.35] rad | 0.0 | conditional | 仅 accessory=reclining 时有效，clamp 到 RECLINE_UPPER；否则忽略 | v13 RECLINE_UPPER |
| seat_fold_mult | float | derived | 0.49 | equation | `= f(座前杆轨迹/座高)`，由 SEAT_FRONT 与 PIVOT 几何派生，不独立采样（保持座前缘贴前杆）| parent L78-82 |
| (—) | constraint | — | — | inequality | 折叠位四足收拢 footprint < 展开 footprint − ε 且 < 阈值；rest 位座板水平在坐高、四足贴地、靠背竖立——违反时按 seat_height/back_height 比例回缩或拒绝重采 | 接口 / clearance |

连续 scale 在 `resolve_config` 中 clamp，每 build 解析一次、全椅统一应用。scale 只动安全比例 / 坐高 / 宽度 / 靠背高（即 source map "连续尺寸参数"节列出的 stool/child/heavy-duty/beach/tall/narrow 差异），绝不改变 fold/seat/frame/accessory 槽的拓扑或 scissor 接口语义。

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots（单椅：rear/front 双腿架 + seat_pan + 可选 fold 子件 + 可选 accessory 子件）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 来产生数量轴。
- 说明：wood_slat 内部的座/背木条是 **module-local 固定 N（座~5 / 背~5）的细节复制**（v03 `_slat_y_positions(5,...)`），属该 seat module 内部装饰，不暴露为模板级 multiplicity 轴、不进 slot_choice。

## 拓扑多样性审计

总组合数（按真实拓扑等价类，frame 去重为 2 原语族）：
**fold(5) × seat(9) × frame(2 原语族) × accessory(5) = 450**。
仅 fold × seat = 5 × 9 = **45 ≥ 10** ✓（即使忽略 frame/accessory 也充裕过门）。
按 source map 原始格子计（frame=4 含材质族）= 5 × 9 × 4 × 5 = 900。

理由：fold 槽含 j=3（scissor / reinforced / triangular）与 j=4（rear_legs_fold_under / collapsing_side_hinge_links）两种关节拓扑；accessory 槽再叠加 j+1（tablet/recline/footrest）或 j+0（handle/plain）。distinct topology 由 (fold 关节拓扑 × seat part-tree 差异[wood_slat 多 part-local 件 / 其余整片] × accessory 关节拓扑) 共同撑起，远超 10。**slot_choices_for_seed 必须返回 (fold, seat, frame, accessory) 四元组**，由其把 distinct 撑到数百。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四槽 module（笛卡尔积基本正交，compatibility gate 见下），再 uniform 各连续 scale。compatibility matrix 排除少数易坏组合（见下表）。random sweep seeds 0-49 初轮、0-999 成熟审计；viewer 目检覆盖每个 fold module × 代表 seat/accessory。

Topology target：1000-seed slot choice tuple distinct 预计 ≈ 数百（fold 5 × seat 9 × frame 2 × accessory 5 = 450 真实拓扑；按 ≥300 report-only 口径观察）。受真实结构词汇表约束，这是样本支持的全部真实形态。

Controlled local parameterization：见 §7 的 seat_height_scale / seat_width_scale / back_height_scale（independent）+ back_recline_angle（conditional on accessory）+ seat_fold_mult（equation，派生不独立采）。全部 `resolve_config` clamp / 派生，每 build 统一应用，遵循连续尺寸采样契约（先采 independent → 派生 seat_fold_mult equation → 投影 footprint/rest inequality → 解析 recline conditional）；不破坏 scissor pivot 接口、seat mimic 贴合、四足贴地或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` fold/seat/frame/accessory（四元组进 slot_choice），再 uniform 各 scale | slot_choices_for_seed 含四槽且与 build 一致 |
| compatibility matrix | (1) accessory=reclining 时靠背改挂独立 `backrest` part，seat_back_panel 仍可任选 visual（recline 与 seat 正交，但 seat helper 须能贴可动 backrest）；(2) accessory=tablet/footrest 与任意 fold 兼容（独立锚），但与 collapsing_side_hinge_links 同时存在时 sweep 关节数达 5，须确认 origin/overlap 不冲突；(3) frame=flat_bar_angular 与 fabric_bucket/wood_slat 兼容（扁条框照样托 visual）；(4) 无互斥硬 gate，排除项 fallback：若某组合 footprint/origin QC 失败，降级 accessory→plain 重试 | 无 floating / collision / 轴错 / 折叠自碰 / 关节数超 5 |
| controlled local variation | seat_height/seat_width/back_height（independent clamp）+ back_recline_angle（conditional）+ seat_fold_mult（equation 派生）| 比例变化不破坏 scissor 接口 / seat mimic 贴合 / 四足贴地 / 类别身份 |
| regression overrides | none（首版用纯 procedural；若 sweep 暴露特定坏 seed 再按审核补，记录原因）| previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 module origin/overlap/fold QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| fold_mechanism | 5 | yes | yes | 含 j=3 / j=4 两种关节拓扑 |
| seat_back_panel | 9 | yes | yes | 纯 visual 模块，最干净可换 |
| frame_style | 4（拓扑去重 2） | yes | yes（原始）/ 边界（去重）| 真实原语族 2（tube/flat_bar）；aluminum/wood 属 tube 材质族 |
| accessory | 5 | yes | yes | 含 plain；含 j+1（tablet/recline/footrest）与 j+0（handle/plain）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `(fold_mechanism, seat_back_panel, frame_style, accessory)` 四元组
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` clamp 各连续 scale 到声明范围；派生 seat_fold_mult；解析 back_recline_angle conditional
- compatibility matrix / gating 阻止非法组合（recline 与 seat visual 协同、多 fold/accessory 关节数 ≤5、flat_bar 托各 seat visual）
- 连续 scale clamp 后不破坏 scissor pivot 接口 / seat mimic 贴合 / 四足贴地 / 折平动作
- 跨部件 scale 依赖（seat_fold_mult equation、footprint/rest inequality、recline conditional）在 `resolve_config` 求解，不留到 builder 失败
- 关键 joint：`fold_pivot` REVOLUTE +Y；`seat_hinge` REVOLUTE +Y 且 mimic=`fold_pivot`；fold/accessory 子件关节按所选 module 的 type/axis（rear_leg_fold +Y、side_link_hinge −Y mimic、tablet_pivot +Z、back_recline −Y、footrest_flip −Y mimic）
- captured/crossing 接口逐 element-scoped `allow_overlap`（rear↔front 交叉、front↔seat 搭杆、seat↔hinge_bar 捕获、fold 子件销眼）
- rest pose（所有联动 q=0）：座板水平在坐高、四足贴地、靠背竖立，current-pose overlap 仅声明的捕获/交叉处
- folded pose（fold=upper）：四足 footprint 收拢、座板抬竖、整椅打平

## Reject cases

- 把 stool / child / heavy-duty / beach / tall / narrow 的尺寸差异当新 Slot 候选 → 不是结构差异，应折入 §7 连续 scale（source map 明令）。
- seat_hinge 不用 mimic、或 mult 不随座高/前杆几何派生 → 座前缘折叠时脱离前杆（座板悬空），fold QC 失败。
- 给 scissor 交叉销 / 座缘搭杆补 MatingContract 硬对接 → captured/crossing 几何对不上，mating-gap 失败；应 grandfather + allow_overlap。
- fold=rear_legs_fold_under / collapsing_side_hinge_links 漏写 captured-pin element-scoped allow_overlap → 销眼重叠触发 current-pose overlap FAIL。
- accessory=reclining 仍把靠背画在 root（不拆独立 part）→ 第 2 铰无可动 child，recline 关节空转。
- accessory=tablet 的 `tablet_pivot` 写成 ±Y（应 +Z 竖轴水平旋开）→ 写字板转向错误、可能扫穿座/腿。
- 同时叠 collapsing_side_hinge_links + footrest + recline 致关节数 >5 且 origin/overlap 冲突未 gate → sweep origin/overlap FAIL；compatibility matrix 须限关节数 ≤5 或降级 accessory。
- 折叠 rest pose 默认设成已折角而非展开可坐位 → 站立 QC（座高/四足贴地）失败。
- wood_slat 把木条做成模板级 multiplicity 轴并进 slot_choice → 它是 module-local 固定 N 装饰，不是数量轴。

## 与相邻类别的边界

- 不该混入：`folding_arm_chain` / `multisegment_foldout_arm`（这些是**机器人折叠臂**——多段串联 link、reach/抓取语义，不是坐人椅；折叠椅是绕单交叉销折平的 sit-on 家具，拓扑是 scissor 双腿架 + 座板 mimic，不是 N 段臂链）。
- 不该混入：固定（不可折）餐椅 / 办公椅（无 `fold_pivot` 折平机构、违反折叠身份与 ≥1 非 fixed joint 的折叠语义）。
- 不该混入：折叠桌 / 折叠床（无座板 + 靠背 + 坐高语义；座面承坐人而非置物/卧）。
- 不该混入：折叠屏风 / 折叠门（无座/背、非自立坐具，是多扇竖板链）。
- 不该混入：高脚凳 / stool（无靠背的 stool 是另一类；本类 stool-height 变体仍带小靠背 + 折叠机构，属 folding chair 的连续 scale 端，不外溢成无靠背 stool）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) frame_style 拓扑去重为 tube/flat_bar 2 族、aluminum/wood 作材质族的处理；(2) fold × accessory 同时叠加致关节数 ≤5 的 compatibility gate；(3) reclining_backrest 把靠背拆独立 part 与 seat_back_panel visual 协同；(4) seat_height/width/back_height 连续 scale 覆盖 stool/child/heavy-duty/beach/tall/narrow 的取舍）|

## 模板实现备注（可选）

- 共享 helper：`_leg_tube` / `_cross_tube` 为全 module 固定骨架原语；frame_style=flat_bar_angular 时改用 `_flat_bar_between`/`_flat_bar_path`/`_cross_flat_bar`（Box）+ pivot_hub 视觉。
- seat_back_panel 是最干净的可换模块：每个 module 即一个 `_*_mesh` helper，同时供 `seat_pan` seat visual 与 root backrest visual；wood_slat / fabric_bucket / woven_cane 例外（slat 为 part-local 循环、bucket/cane 用 `MeshGeometry`/多 merge）。
- captured-pin / crossing overlap：`run_folding_chair_tests` 须按所选 fold/accessory module 条件性发 element-scoped `allow_overlap`（rear↔front 交叉常驻；rear_legs_fold_under 的 hinge_tab↔rear_under_hinge、collapsing_side_hinge_links 的 side 销、seat↔seat_hinge_bar 捕获、seat↔front 搭杆）。
- seat mimic：`seat_hinge` 必须 `Mimic(fold_pivot, multiplier=seat_fold_mult)`，seat_fold_mult 由座前杆轨迹/座高几何派生（resolve_config 内），保证座前缘全程贴前杆。
- accessory=reclining 时靠背从 root visual 移到独立 `backrest` part（挂 `back_recline` REVOLUTE −Y），seat_back_panel 的 backrest `_*_mesh` 随之挂到该可动 part。
- 关节数上限：fold 子件（+1）+ accessory 子件（+1）叠加时总非 fixed 关节可达 5；compatibility matrix 须保证 ≤5 且各 origin 落几何、各 captured overlap 已声明。
- 参考模板（实现阶段从 MATURE_TEMPLATE_METHOD 选）：含 scissor/mimic 单 DOF 折叠 + parallel_children 固定槽 + 可选 moving child accessory 的模板优先（按运动拓扑选，不按类别名）。
