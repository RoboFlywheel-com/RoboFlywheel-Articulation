# scifi_gate — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `scifi_gate` |
| template path | `agent/templates/Door_Scifi_Gate.py` |
| test path (optional) | `tests/agent/test_scifi_gate_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children frame surround + per-mechanism multiplicity loop) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (2 parents + 9 converged variants); each record's `model.py` was read in full (AST + region map), plus `record.json` rating verified =5 |
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

阅读结论（结构变化轴）：

- **两个 parent 共享同一根机构** — bi-parting 2-stage lateral telescope，4 个手写命名 leaf（`door_0`/`door_1`/`door_0_outer`/`door_1_outer`），1 个 PRISMATIC driver `door_0_slide` + 3 个 mimic（同级 ×1.0、两 outer ×0.5）。它们只在 **seam motif**（hex=cosine 波浪 vs zigzag=尖齿燕尾）和 **surround**（hex 扁平 slab vs lintel+sill+side-housing）上分叉。
- **9 个 variant 沿 4 根真实结构轴扇出**：opening_mechanism（机构）、multiplicity N（移动段数）、leaf/seam/surface motif（叶面 motif）、frame surround（框）。
- **机构是支配性的结构轴，且每个候选有不同 joint 拓扑**：lateral telescope（±X PRISMATIC, mimic 链）、single-leaf pocket（+X PRISMATIC, 1 driver + 1 mimic 0.5×）、vertical lift（±Z PRISMATIC, 独立 staggered 或 even-pitch, 无 mimic）、iris revolute（about-rim REVOLUTE, driver + mimic 1.0×）、iris radial slide（径向 PRISMATIC, 外圈槽派生约束，无中心 hub，driver + mimic 1.0×）。
- **multiplicity 是循环复制轴，但每个机构有自己的 count**：`N_SLABS`（vertical lift）、`N_PETALS`（iris swing）、`N_LEAVES`（iris radial slide）；lateral telescope / pocket 用固定 leaf 集（2 per side / 1），不是 swept count。iris N ≠ slab N ≠ telescope N，**不是单一共享正交 N**。
- **loop-emission 现状**：parents + pocket + piston_greeble + round_bulkhead 的 leaf 是手写命名（`for` 仅用于装饰/fixed-mount）；blastslabs4/6、iris6/8、leaves4/8 已经从一个共享几何 helper 用 `for i in range(N)` 循环发射 `slab_{i}`/`petal_{i}`/`leaf_{i}`。multiplicity 模板必须 drive off 这些 loop variant，而非 parents。
- **颜色/材质从不作为结构变化**；fixed greeble（piston/beacon/keypad/clamp/jamb strip）是被 exercise 的 fixed-furniture 层，**不计入结构轴**。

## 核心身份

Scifi gate 是一扇墙体安装的科幻 blast / airlock / security 门：一个固定结构 surround（框）围出一个**真正的贯通开口**（无背墙），由一套**带动力的开门机构**清空门洞。门站在 z=0 上。核心运动语义 = 至少一个真实非 fixed joint 把移动段从「closed（封住门洞）」驱动到「open（让出贯通开口）」。

四个独立结构层：

1. **opening_mechanism**（主机构）— 门洞如何被清空：bi-parting 横向伸缩、单叶口袋滑移、竖直升降、虹膜旋转、虹膜径向滑移。每个候选有不同 joint 拓扑。
2. **multiplicity N** — 移动段数（slab/petal/leaf），按机构本地化。
3. **leaf/seam/surface motif** — 移动叶的面处理 + 中缝 motif（cosine 波缝 / 尖齿燕尾缝 / 横向百叶条 / 径向楔瓣 / 平装甲板）。
4. **frame surround** — 固定框风格（六边斜面 slab / 楣-槛-侧舱 / 圆形舱壁环）。

边界（不该混入）：

- 不混入普通 **room/building door**（铰链平板木门 + 把手）：scifi gate 强调动力机构、装甲面、危险条、贯通门洞，没有把手转把。
- 不混入 **elevator door** 单功能：虽然横向伸缩相近，但 scifi gate 包含 iris/lift/bulkhead 等多机构家族 + 装甲科幻 surround，且必须保持贯通门洞（无电梯井背墙）。
- 不混入 **vault/safe door**（厚旋钮 + boltwork）：scifi gate 是建筑级门洞 surround，不是嵌入柜体的圆盘门。
- fixed greeble（piston ram / warning beacon / keypad / clamp / jamb glow strip）是装饰层，不是机构。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_door_scifi_hex` | `data/records/rec_door_scifi_hex/revisions/rev_000001/model.py:L284-L468` | parent：hex_beveled_slab surround + biparting telescope + hazard_cosine_seam + jamb/clamp 家具 |
| S2 | `rec_door_scifi_zigzag` | `data/records/rec_door_scifi_zigzag/revisions/rev_000001/model.py:L211-L539` | parent：lintel_sill_side_housing surround + biparting telescope + zigzag_dovetail_seam + keypad/hazard 家具 |
| S3 | `rec_scifi_gate_var_blastslabs4` | `data/records/rec_scifi_gate_var_blastslabs4/revisions/rev_000001/model.py:L167-L423` | vertical_lift N=4 overhead louver（独立 staggered +Z PRISMATIC）+ horizontal_louver_slab motif |
| S4 | `rec_scifi_gate_var_blastslabs6` | `data/records/rec_scifi_gate_var_blastslabs6/revisions/rev_000001/model.py:L238-L501` | vertical_lift N=6 bi-parting（lower 3 −Z / upper 3 +Z, even-pitch, uniform travel）+ louver motif |
| S5 | `rec_scifi_gate_var_iris6` | `data/records/rec_scifi_gate_var_iris6/revisions/rev_000001/model.py:L291-L449` | iris_revolute_swing N=6（about-rim REVOLUTE driver + 5 mimic ×1.0）+ radial_petal_wedge motif |
| S6 | `rec_scifi_gate_var_iris8` | `data/records/rec_scifi_gate_var_iris8/revisions/rev_000001/model.py:L269-L365` | iris_revolute_swing N=8（+Y REVOLUTE driver + 7 mimic ×1.0）+ radial_petal_wedge（curved blade） |
| S7 | `rec_scifi_gate_var_leaves4` | `data/records/rec_scifi_gate_var_leaves4/revisions/rev_000001/model.py:L247-L397` | iris_radial_slide N=4（per-config 独立径向 PRISMATIC，无 mimic）+ flat_armor_plate wedge motif |
| S8 | `rec_scifi_gate_var_leaves8` | `data/records/rec_scifi_gate_var_leaves8/revisions/rev_000001/model.py:L281-L460` | iris_radial_slide N=8（径向 PRISMATIC driver + 7 mimic ×1.0）+ radial_petal_wedge；source hazard arc / 中央 hub 不采纳到实现 |
| S9 | `rec_scifi_gate_var_pocket` | `data/records/rec_scifi_gate_var_pocket/revisions/rev_000001/model.py:L172-L506` | single_leaf_sliding_pocket（+X PRISMATIC driver + 1 mimic ×0.5）+ flat_armor_plate motif + 加大右舱 |
| S10 | `rec_scifi_gate_var_piston_greeble` | `data/records/rec_scifi_gate_var_piston_greeble/revisions/rev_000001/model.py:L398-L552` | biparting telescope + hazard_cosine_seam + piston/beacon 家具（fixed-furniture 层证据） |
| S11 | `rec_scifi_gate_var_round_bulkhead` | `data/records/rec_scifi_gate_var_round_bulkhead/revisions/rev_000001/model.py:L206-L606` | circular_bulkhead_ring surround（`_make_bulkhead_ring`）+ biparting telescope + zigzag_dovetail_seam |

## 槽位 + 候选模块表

### Slot A：opening_mechanism（主机构 — 门洞如何被清空；支配性结构轴，每候选不同 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `biparting_lateral_telescope` | S1 `rec_door_scifi_hex` | L391-L466 | eligible if compatible | 4 手写 leaf（door_0/1 + _outer），driver `door_0_slide` PRISMATIC ±X（L428-L436）+ 3 mimic（L437-L466，同级 ×1.0、outer ×0.5）；captured leaf 嵌入侧舱 |
| `biparting_lateral_telescope` (alt seam/surround) | S2 `rec_door_scifi_zigzag` | L410-L537 | eligible if compatible | 同拓扑，axis +X driver（L499-L507）+ 3 mimic（L508-L537）；验证 motif/surround 互换不改机构 |
| `single_leaf_sliding_pocket` | S9 `rec_scifi_gate_var_pocket` | L394-L506 | eligible if compatible | 1 整宽 leaf（door_0）+ rear stage（door_0_outer）；driver `door_0_slide` PRISMATIC +X（L488-L496）+ 1 mimic ×0.5（L497-L506）；滑入加大右舱 |
| `vertical_lift` | S3 `rec_scifi_gate_var_blastslabs4` / S4 `rec_scifi_gate_var_blastslabs6` | S3:L370-L423 / S4:L454-L501 | eligible if compatible | `slab_{i}` 循环发射；S3=独立 staggered +Z PRISMATIC（无 mimic，axis(0,0,1) L416，per-slab upper L417）；S4=lower 3 −Z / upper 3 +Z（axis 选择 L467-L471，uniform travel L480） |
| `iris_revolute_swing` | S5 `rec_scifi_gate_var_iris6` / S6 `rec_scifi_gate_var_iris8` | S5:L390-L449 / S6:L329-L365 | eligible if compatible | `petal_{i}` 循环发射；REVOLUTE about-rim（S5 axis(0,0,-1)+rpy tangent L429-L438 / S6 axis(0,1,0) +Y L355-L363）；driver petal_0 + N−1 mimic ×1.0；360/N 角度布置 |
| `iris_radial_slide` | S7 `rec_scifi_gate_var_leaves4` / S8 `rec_scifi_gate_var_leaves8` | S7:L348-L397 / S8:L398-L460 | eligible if compatible | `leaf_{i}` 循环发射，径向 PRISMATIC 向外滑；实现删除 S8 中央 hub/三叶架，改为每叶外圈 `radial_pocket_{i}` + `radial_joint_pad_{i}` 派生约束；S8=axis(cosθ,0,sinθ) driver + mimic ×1.0 |

> Slot A 有 6 个候选行（5 个结构不同的机构 + 1 个 biparting alt-source 用于验证 motif/surround 与机构正交）。最小机构去重 = 5（telescope / pocket / lift / iris-revolute / iris-radial）≥ 3 ✓。

### Slot B：multiplicity N（移动段数 — 按机构本地化，详见第 8 节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_leaf` (N=1) | S9 `rec_scifi_gate_var_pocket` | L394-L396 | eligible if compatible | door_0 + door_0_outer（rear stage）；唯一全宽滑叶，2 级伸缩 |
| `pair_per_side` (N=2) | S1/S2/S10/S11 | S1:L391-L394 / S2:L410-L413 | eligible if compatible | door_0/door_1 + _outer 对；每侧 inner+outer 伸缩对 |
| `four_segment` (N=4) | S3 `rec_scifi_gate_var_blastslabs4` / S7 `rec_scifi_gate_var_leaves4` | S3:L370-L387 / S7:L348-L353 | eligible if compatible | slab_0..slab_3 / leaf_0..leaf_3（`N_SLABS=4` S3:L77 / `N_LEAVES=4` S7:L77） |
| `six_segment` (N=6) | S4 `rec_scifi_gate_var_blastslabs6` / S5 `rec_scifi_gate_var_iris6` | S4:L454-L456 / S5:L402-L405 | eligible if compatible | slab_0..slab_5 / petal_0..petal_5（`N_SLABS=6` S4:L73 / `N_PETALS=6` S5:L83，60°） |
| `eight_segment` (N=8) | S6 `rec_scifi_gate_var_iris8` / S8 `rec_scifi_gate_var_leaves8` | S6:L337-L343 / S8:L420-L437 | eligible if compatible | petal_0..petal_7 / leaf_0..leaf_7（`N_PETALS=8` S6:L85 / `N_LEAVES=8` S8:L67，45°） |

> distinct N = {1,2,4,6,8} = 5 ≥ 2-3 required ✓。N 不是单一正交轴：合法 N 域随 Slot A 机构 conditional（见第 7/8 节兼容矩阵）。

### Slot C：leaf / seam / surface motif（移动叶的面处理 + 中缝 motif）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `hazard_cosine_seam` | S1 `rec_door_scifi_hex` / S10 `rec_scifi_gate_var_piston_greeble` | S1:L183-L281（seam L183-L199, leaf mesh L211-L221, hazard decal L224-L281）/ S10:L297-L395 | eligible if compatible | 黄黑斜向 chevron 贴片 + 平滑 cosine 中缝（`_seam_points` 1.5 波 S1:L197） |
| `zigzag_dovetail_seam` | S2 `rec_door_scifi_zigzag` / S11 `rec_scifi_gate_var_round_bulkhead` | S2:L126-L170（seam L126-L136, panel L139-L154, accent L157-L170）/ S11:L132-L167 | eligible if compatible | 尖齿燕尾 tooth-into-notch 中缝（5 角节点 S2:L130-L136）；实现中删除会扫入滑槽的凸起 `leaf_seam_accent` |
| `horizontal_louver_slab` | S3 `rec_scifi_gate_var_blastslabs4` / S4 `rec_scifi_gate_var_blastslabs6` | S3:L382-L387（accent_line）/ S4:L158-L232（`_add_slab_visuals`: panel/edge_strip/center_rib/meeting_accent） | eligible if compatible | 扁平 gunmetal 横条 + 黄安全条（4）或 edge strip + 中肋 + meeting accent（6） |
| `radial_petal_wedge` | S5 `rec_scifi_gate_var_iris6` / S6 `rec_scifi_gate_var_iris8` / S8 `rec_scifi_gate_var_leaves8` | S5:L215-L284（plate/spine/knuckle/rib）/ S6:L157-L205（curved blade/boss/ridge）/ S8:L172-L258（wedge/stripe/rib） | eligible if compatible | 三角/弧形/扇楔装甲瓣 + 加强 spine/ridge/rib；leaves8 加 hazard-yellow 弧带（S8:L205-L237） |
| `flat_armor_plate` | S9 `rec_scifi_gate_var_pocket` / S7 `rec_scifi_gate_var_leaves4` | S9:L152-L166 + L404-L470（leaf_panel/edge_accent/groove/kick）/ S7:L188-L241（`_leaf_wedge_mesh`: plate/groove-slot/outer-rib） | eligible if compatible | 平倒角装甲板；实现中删除会扫入滑槽的 pocket `edge_accent` / `kick_plate` 凸起条，径向叶也不再发 hazard arc 凸条 |

### Slot D：frame / surround style（固定框风格）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `hex_beveled_slab` | S1 / S5 / S6 / S7 / S8 / S10 | S1:`_frame_mesh` L121-L136 + tracks L304-L313 + trim/bolt L359-L388 | eligible if compatible | 扁平矩形 slab + 倒角六边贯通口（`_frame_mesh`）+ 暗导轨 + 倒角 trim + 螺栓 |
| `lintel_sill_side_housing` | S2 / S3 / S4 / S9 | S2:lintel L231-L236 + sill L245-L250 + guide L255-L267 + housing L283-L330 + keypad L333-L374 + hazard L376-L407 | eligible if compatible | 楣梁 + 地槛 + 侧舱回缩袋 + 墙 keypad + 基角危险 chevron（pocket 加大右舱；blastslabs 深化槛/楣袋） |
| `circular_bulkhead_ring` | S11 `rec_scifi_gate_var_round_bulkhead` | `_make_bulkhead_ring` L206-L270 + bolt-circle L306-L331 + header_trim L333-L342 | eligible if compatible | 圆形装甲气闸环 + 矩形门洞 bore + rim lip + 内门挡框 + 周边螺栓圈（20 颗，`for i in range(20)` L306） |

> Slot D = 3 个结构不同的候选 ≥ 3 ✓。

### （非结构）Slot E：fixed root furniture / greebles — 被 exercise，不计入结构轴
| 候选 | 5_star_source | model.py:Lx-Ly | 状态 |
|---|---|---|---|
| `jamb_strips + clamp_blocks` | S1 `rec_door_scifi_hex` | L314-L357（clamp/lamp/light_strip） | parent baseline |
| `keypad + hazard_chevrons` | S2 `rec_door_scifi_zigzag` | L333-L407（keypad/key grid/hazard） | parent baseline |
| `piston_rams + warning_beacons` | S10 `rec_scifi_gate_var_piston_greeble` | L429-L443（piston_0/1 L429-L435, beacon_0/1 L437-L443） | converged（替换 strips+clamps） |

> Slot E 是 piston_greeble 移动的那一层；**不计入 GATE P1，不进入主拓扑组合数**。模板把它实现为 surround-bound parent visual（无 per-greeble FIXED joint），由 palette/surround 选择隐式带出，不作为独立采样轴。

## 槽位图（slot graph）

pattern: `mixed`（surround 是固定 parent；机构的移动段 parallel 挂到 surround；某些机构内部用 multiplicity 循环复制段）

```text
[Slot D frame_surround]  (固定 root part "frame"，站在 z=0，含 Slot E 家具作为 parent visual)
        │  门洞 = 真正贯通开口（hex bore / rect bore / circular bore）
        │  upstream interface = surround 的 doorway 面 + guide rail/track + side wall pocket / lintel-sill pocket / rim pivot ring / outer radial pocket
        │
        ├── (机构 A1 biparting_lateral_telescope)
        │      door_0 --[PRISMATIC ±X, driver door_0_slide]--> 侧舱
        │      door_1 / door_0_outer / door_1_outer --[PRISMATIC mimic ×1.0 / ×0.5]
        │
        ├── (机构 A2 single_leaf_sliding_pocket)  [互斥]
        │      door_0 --[PRISMATIC +X driver]--> 加大右舱
        │      door_0_outer --[PRISMATIC mimic ×0.5]
        │
        ├── (机构 A3 vertical_lift)  [互斥, multiplicity N_SLABS]
        │      slab_{i} for i in range(N) --[PRISMATIC ±Z, 独立 staggered 或 even-pitch]--> 楣/槛袋
        │
        ├── (机构 A4 iris_revolute_swing)  [互斥, multiplicity N_PETALS, 需圆口]
        │      petal_{i} for i in range(N) --[REVOLUTE about-rim, driver petal_0 + mimic ×1.0]--> 环
        │
        └── (机构 A5 iris_radial_slide)  [互斥, multiplicity N_LEAVES, 需圆口]
               leaf_{i} for i in range(N) --[PRISMATIC 径向, mimic ×1.0]--> 外圈径向槽
```

跨 slot 连接接口点位：

- **surround → 机构**：surround 提供 doorway 面 + 导向（lateral=top/bottom guide bar + 左右墙体收纳槽；lift=楣/槛袋 + 侧 channel；iris-revolute=rim pivot ring；iris-radial=外圈径向槽 + 外圈 joint pad；pocket=加大侧舱）。机构的所有移动段以 surround 的固定 part `frame` 为 parent。
- **机构内部 joint**：lateral/pocket = ±X PRISMATIC；lift = ±Z PRISMATIC；iris-revolute = about-rim REVOLUTE（axis 在 artic frame 为 ±Z 经 rpy tangent，或显式 +Y）；iris-radial = 径向 PRISMATIC（per-index axis）。
- **mimic 策略**（按机构）：lateral = 1 driver + 3 mimic（同级 ×1.0、两 outer ×0.5）；pocket = 1 driver + 1 mimic ×0.5；lift = N 个独立 joint（无 mimic）；iris-revolute = driver petal_0 + (N−1) mimic ×1.0；iris-radial = driver leaf_0 + (N−1) mimic ×1.0（leaves4 例外：per-config 独立无 mimic）。
- **互斥/可选**：Slot A 的 5 个机构互斥（一次只有一个）。Slot E 家具可选，由 surround 隐式带出。Slot B 的 N 仅对 lift/iris-revolute/iris-radial 暴露；lateral/pocket 用固定 leaf 集。
- **派生关系**：圆口 iris-revolute 可配 `circular_bulkhead_ring` 或 hex-slab 圆 aperture；iris-radial 因外圈槽和径向 sweep 必须配 `circular_bulkhead_ring`；矩形机构（lateral/lift/pocket）配 hex_beveled_slab 或 lintel_sill_side_housing（兼容矩阵见第 9 节）。

## 每槽位 Module Emits / Interfaces

### Slot D / module `hex_beveled_slab`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定 `frame` part：frame_slab（`_frame_mesh` 倒角六边 bore）+ top_recess + top_track/bottom_track + chamfer_trim_* + bolt_* | S1/model.py:L121-L161, L296-L388 |
| internal joints | 无（家具是 frame sub-visual，无 FIXED joint —— hex 家族风格） | S1/model.py:L296-L388 |
| upstream interface | root，站 z=0；doorway = 倒角六边 bore（OPEN_W=1.18, OPEN_H=1.74 S1:L63-L64） | S1/model.py:L104-L136 |
| downstream interface | top/bottom guide bar 作为 lateral leaf 滑轨；矩形/圆 aperture 供机构挂载 | S1/model.py:L139-L146 |

### Slot D / module `lintel_sill_side_housing`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定 `frame`（lintel_header/header_trim/sill/top_guide/bottom_guide）+ 独立 part：left_housing/right_housing（cowl_front/cowl_plate/rear_rail/pocket_end_wall + rivet）+ keypad（box/screen/3×3 key/status_lamp）+ haz_left/haz_right | S2/model.py:L228-L407 |
| internal joints | 5 个 FIXED joint（frame→housing×2, frame→keypad, frame→hazard×2） | S2/model.py:L484-L496 |
| upstream interface | root，站 z=0；doorway = 矩形 bore（OPENING_W=1.62, OPENING_H=2.05 S2:L64-L65）；侧舱 = leaf 回缩袋 | S2/model.py:L72, L283-L330 |
| downstream interface | top_guide/bottom_guide 滑轨 + 侧舱袋（pocket 加大右舱 S9:L73）+ 楣/槛深袋（lift S4:L258/L280） | S2/model.py:L255-L267 |

### Slot D / module `circular_bulkhead_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定 `frame`：bulkhead_ring（`_make_bulkhead_ring` 旋转盘 + 矩形 bore + rim lip + 内门挡框 + deck cut）+ ring_bolt_{i}（20 颗 bolt-circle）+ header_trim 弧 + top/bottom_guide + housing + keypad + hazard | S11/model.py:L206-L480 |
| internal joints | 5 个 FIXED joint（同 lintel 家族） | S11/model.py:L553-L565 |
| upstream interface | root，站 z=0；圆形装甲环 + 矩形 doorway bore；rim 可作 iris pivot ring | S11/model.py:L206-L270 |
| downstream interface | 矩形 bore 供 telescope；圆 rim 供 iris-revolute pivot 与 iris-radial 外圈径向槽 | S11/model.py:L211-L258 |

### Slot A / module `biparting_lateral_telescope`
| emits | 描述 | 来源 |
|---|---|---|
| parts | door_0/door_1（inner，front plane）+ door_0_outer/door_1_outer（outer，rear plane）；面 = Slot C motif | S1/model.py:L391-L425 |
| internal joints | driver `door_0_slide` PRISMATIC axis(±1,0,0) upper=TRAVEL_A + door_1_slide mimic ×1.0 + 两 outer mimic ×0.5 upper=TRAVEL_B | S1/model.py:L428-L466 |
| upstream interface | parent=frame；leaf 在 top/bottom guide bar 间被 capture | S1/model.py:L139-L146, L428 |
| downstream interface | open pose leaf nest 进固定 frame 的左右 `*_wall_pocket_recess`，避免门叶收进墙体时穿模 | S1/model.py:L428-L466 |

### Slot A / module `single_leaf_sliding_pocket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | door_0（整宽 inner leaf）+ door_0_outer（rear stage） | S9/model.py:L394-L470 |
| internal joints | driver `door_0_slide` PRISMATIC axis(1,0,0) upper=TRAVEL_A=1.10 + door_0_outer_slide mimic ×0.5 upper=TRAVEL_B | S9/model.py:L488-L506 |
| upstream interface | parent=frame；加大右舱（RIGHT_HOUSING_W=1.15 S9:L73） | S9/model.py:L258-L313 |
| downstream interface | open pose 整叶嵌入加大右侧 `right_wall_pocket_recess`（2 级伸缩），槽口 lip 外移避开 closed leaf | S9/model.py:L488-L506 |

### Slot A / module `vertical_lift`
| emits | 描述 | 来源 |
|---|---|---|
| parts | slab_{i} for i in range(N_SLABS)（一个共享 Box / `_add_slab_visuals` helper） | S3:L133-L134, L370-L387 / S4:L158-L232, L454-L465 |
| internal joints | slab_{i}_slide PRISMATIC；S3=独立 staggered axis(0,0,1) per-slab upper（底叶行程最大 `_slab_travel(i)`）；S4=lower i<N//2 axis(0,0,-1) / upper axis(0,0,1)，uniform SLAB_TRAVEL=OPENING_H/2 | S3:L404-L423 / S4:L454-L486 |
| upstream interface | parent=frame；slab 在左右 vertical channel 间被 capture | S3:L239-L245 / S4:L302-L312 |
| downstream interface | open pose slab nest 进楣/槛深袋（lintel 家族） | S3:L122-L130 / S4:L87-L92 |

### Slot A / module `iris_revolute_swing`
| emits | 描述 | 来源 |
|---|---|---|
| parts | petal_{i} for i in range(N_PETALS)（共享 `_petal_mesh`/`_petal_cq`）+ frame 上的 pivot bracket-hub / iris_ring | S5:L170-L284, L402-L405 / S6:L157-L262, L337-L343 |
| internal joints | petal_0 driver REVOLUTE（S5 axis(0,0,-1)+rpy tangent / S6 axis(0,1,0) +Y），lower=0 upper=IRIS_OPEN_ANGLE（~60-63°）+ (N−1) mimic ×1.0 | S5:L409-L449 / S6:L347-L365 |
| upstream interface | parent=frame；petal 铰挂在 360/N 角度的 rim pivot 上 | S5:L390-L420 / S6:L348-L350 |
| downstream interface | open pose petal 绕 rim 旋开露出圆 aperture（需圆口 surround 或 hex 上的圆 aperture） | S5:L417-L427 / S6:L355-L363 |

### Slot A / module `iris_radial_slide`
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf_{i} for i in range(N_LEAVES)（共享 `_leaf_wedge_mesh`）+ frame 外圈 `radial_pocket_{i}` / `radial_joint_pad_{i}`；删除 S8 中央 hub / 三叶架 | S7:L188-L241, L348-L363 / S8:L172-L278, L398-L437 |
| internal joints | leaf_{i}_slide 径向 PRISMATIC；S7=per-config 独立 axis +X/+Z/−X/−Z（无 mimic，per-leaf travel `LEAF_CONFIGS` L95-L104）；S8=axis(cosθ,0,sinθ) θ=i·45° driver leaf_0 + 7 mimic ×1.0 upper=LEAF_TRAVEL=0.36 | S7:L384-L397 / S8:L441-L460 |
| upstream interface | parent=frame；leaf 的外圈 guide shoe 坐在 `radial_joint_pad_{i}`，长槽 `radial_pocket_{i}` 退到叶片后方，θ=i·360/N | S7:L95-L104 / S8:L398-L416 |
| downstream interface | open pose leaf 径向向外缩入圆形 bulkhead 外圈槽，closed pose 叶尖在中心闭合但不依赖中心固定架 | S7:L384-L397 / S8:L441-L460 |

### Slot C / motif modules（挂在移动段上的面/缝 visual）
| emits | 描述 | 来源 |
|---|---|---|
| hazard_cosine_seam | leaf 装甲面 + cosine 中缝 + 黄黑斜 chevron 贴片（parent visual，无 joint） | S1:L183-L281 |
| zigzag_dovetail_seam | leaf 面 + 尖齿燕尾缝；实现删除滑动路径中的凸起 leaf_seam_accent / groove/kick_plate | S2:L139-L170, L420-L481 |
| horizontal_louver_slab | slab panel + edge strip + center rib + meeting accent + 黄安全条 | S3:L382-L387 / S4:L158-L232 |
| radial_petal_wedge | 三角/弧/扇瓣 + spine/ridge/rib（+ leaves8 hazard 弧带） | S5:L215-L284 / S6:L157-L205 / S8:L172-L258 |
| flat_armor_plate | 平倒角板；pocket 前缘黄条/kick_plate 与 radial hazard arc 作为滑动路径凸起不采纳，径向叶保留楔板主体 + 外圈滑座 | S9:L152-L166, L404-L470 / S7:L188-L241 |

> 所有 motif 是移动段的 parent visual（无 per-decoration FIXED joint）；同理 surround 家具（hazard chevron / bolt circle / keypad grid / rivet / clamp）是 surround 的 parent visual。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `opening_mechanism` | enum | `biparting_lateral_telescope` / `single_leaf_sliding_pocket` / `vertical_lift` / `iris_revolute_swing` / `iris_radial_slide` | `biparting_lateral_telescope` | choice | 由 deterministic procedural sampler 选择 | Slot A table |
| `seam_motif` | enum | `hazard_cosine_seam` / `zigzag_dovetail_seam` / `horizontal_louver_slab` / `radial_petal_wedge` / `flat_armor_plate` | `hazard_cosine_seam` | conditional | 合法集随机构变化（见第 9 节兼容矩阵） | Slot C table |
| `frame_surround` | enum | `hex_beveled_slab` / `lintel_sill_side_housing` / `circular_bulkhead_ring` | `hex_beveled_slab` | conditional | iris-revolute 可用 bulkhead/hex 圆口；iris-radial 强制 circular_bulkhead_ring；矩形机构隐含矩形 surround | Slot D table |
| `palette_style` | enum | `gunmetal_hazard_yellow` / `dark_armor_cyan_glow` / `riveted_steel_amber` / `olive_mil_hazard` / `airlock_white_cyan` | `gunmetal_hazard_yellow` | choice | top-dressing 自由选择，不改拓扑（>=4-5 colorway） | S1-S11 materials |
| `slab_count` | int | `[3, 8]`（仅 vertical_lift） | 4 | conditional | 仅当 `opening_mechanism==vertical_lift` 暴露；加权小 N 偏多 | S3:L77, S4:L73 |
| `petal_count` | int | `[5, 10]`（仅 iris_revolute_swing） | 6 | conditional | 仅当 `iris_revolute_swing`；360/N 角度，N≥5 防瓣过宽自碰 | S5:L83, S6:L85 |
| `leaf_count` | int | `[3, 8]`（仅 iris_radial_slide） | 4 | conditional | 仅当 `iris_radial_slide`；径向 360/N，3/4/5 叶明确支持中心闭合 | S7:L77, S8:L67 |
| `leaves_per_side` | int | `[1, 2]`（仅 lateral telescope / pocket） | 2 | conditional | telescope=2、pocket=1；不是 swept 大 N | S1:L391, S9:L395 |
| `opening_width_scale` | float | `[0.85, 1.15]` | 1.0 | independent | 在范围内独立采样后 clamp（基线 OPENING_W≈1.18-1.62） | S1:L63 / S2:L64 |
| `opening_height_scale` | float | `[0.90, 1.12]` | 1.0 | independent | 独立采样后 clamp（基线 OPENING_H≈1.74-2.05） | S1:L64 / S2:L65 |
| `surround_depth_scale` | float | `[0.9, 1.2]` | 1.0 | independent | 框深 FRAME_D/FRAME_DEPTH 独立缩放 | S1:L59 / S2:L68 |
| `slide_travel_scale` | float | derived | 1.0 | equation | `TRAVEL_A = f(opening_width_scale·half_opening)`；lateral/pocket 行程随开口宽派生，outer = ×0.5 | S1:L100-L101 / S9:L81-L82 |
| `lift_travel` | float | derived | — | equation | `slab/lift upper = g(opening_height_scale·OPENING_H, N)`（staggered 底叶最大 / even uniform=H/2） | S3:L128-L130 / S4:L87 |
| `iris_open_angle` | float | `[0.95, 1.20] rad` | 1.05 | conditional | iris-revolute 摆角，上限随 petal_count clamp（N 大角小防互撞） | S5:L87 / S6:L91 |
| `iris_radius_scale` | float | `[0.9, 1.15]` | 1.0 | conditional | iris aperture 半径缩放（IRIS_R≈0.50-0.55），需 ≤ surround bore 内切圆 | S5:L84 / S8:L71 |
| (—) | constraint | — | — | inequality | `(leaf_outer_r + bore_clearance) ≤ 0.5·min(OPEN_W,OPEN_H)·opening_*_scale − rim_lip`；违反则回缩 iris_radius_scale / leaf_outer_r | 圆口内切约束 + 滑动 clearance |
| (—) | constraint | — | — | inequality | `Σ leaf/slab span（closed pose）≥ opening`（无缝隙封口）且 `open pose 段全部 ≤ pocket/lintel 容量`；违反则回缩 travel 或拒绝 | closed/open pose clearance |
| (—) | constraint | — | — | inequality | `petal_count·petal_angular_width ≤ 360° − N·gap`（iris 闭合无重叠穿模）；违反则降 N 或缩瓣 | S6:L68-L70 |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette。未实现拓扑不入 enum。

连续尺寸采样契约：先采 independent（opening_width_scale / opening_height_scale / surround_depth_scale / iris_radius_scale 上游解析后）→ 按 equation 派生 slide_travel/lift_travel → 用 inequality 把 iris 半径、closed/open pose span、iris 角宽投影/回缩到可行域，无法满足则拒绝重采 → conditional 范围（count 域、iris 角/半径上限）在采样前按 opening_mechanism 解析。

## Multiplicity / Copy Logic

本类别有**多根 multiplicity 轴**，但**每根轴按机构互斥本地化**（不是单一共享正交 N）。一次采样只激活当前 `opening_mechanism` 对应的那根轴；其余轴不暴露。

### 轴 1：`slab_count`（仅 vertical_lift）
- count_param: `N_SLABS`（S3:L77=4, S4:L73=6）
- N_range（产品域）: `[3, 8]`；测试偏小，产品全程
- sampling domain（权重档）: 小 N（3-5）高频，6-8 稀有
- copied object: 横向 slab 装甲条（共享 `_SLAB_BODY` Box S3:L133-L134 / `_add_slab_visuals` S4:L158-L232）
- naming: `slab_{i}`；joint `slab_{i}_slide`
- placement: 垂直均匀堆叠（even-pitch SLAB_PITCH=OPENING_H/N S3:L81 / S4:L75）
- joint policy: N 个独立 PRISMATIC ±Z（无 mimic）；overhead 模式全 +Z staggered（底叶 upper 最大 `_slab_travel(i)` S3:L128-L130）；bi-parting 模式 lower i<N//2 → −Z、upper → +Z，uniform travel=OPENING_H/2（S4:L467-L480）
- source/gating: drive off S3/S4 的 `for i in range(N_SLABS)` 循环（S3:L371 / S4:L455），**不要 fork parent 手写 leaf**

### 轴 2：`petal_count`（仅 iris_revolute_swing）
- count_param: `N_PETALS`（S5:L83=6, S6:L85=8）
- N_range（产品域）: `[5, 10]`（圆口证据：360/N，N<5 瓣过宽闭合自碰）
- sampling domain: 6-8 高频，5/9/10 稀有
- copied object: 装甲瓣（共享 `_petal_mesh` S5:L215-L284 / `_petal_cq_at` S6:L208-L215）+ pivot bracket-hub
- naming: `petal_{i}`；joint `petal_{i}_joint`（S5）/ `petal_{i}_hinge`（S6）
- placement: 规则 360/N 角度环绕 rim（θ=i·2π/N S5:L410 / S6:L348）
- joint policy: petal_0 driver REVOLUTE + (N−1) mimic ×1.0；axis = about-rim（S5 axis(0,0,-1)+rpy tangent / S6 axis(0,1,0) +Y）；lower=0 upper=IRIS_OPEN_ANGLE（clamp 随 N）
- source/gating: drive off S5/S6 的 `for i in range(N_PETALS)`（S5:L390-L449 / S6:L337-L365）

### 轴 3：`leaf_count`（仅 iris_radial_slide）
- count_param: `N_LEAVES`（S7:L77=4, S8:L67=8）
- N_range（产品域）: `[3, 8]`
- sampling domain: 4-6 高频，3/7/8 稀有
- copied object: 径向楔/扇瓣（共享 `_leaf_wedge_mesh` S7:L188-L241 / S8:L172-L202）+ 外圈 radial pocket / joint pad；删除 S8 中央 hub / hazard arc 凸条
- naming: `leaf_{i}`；joint `leaf_{i}_slide`
- placement: 径向轴 θ=i·360/N 向外滑（S7 per-config LEAF_CONFIGS L95-L104 / S8 axis(cosθ,0,sinθ) L442-L443）
- joint policy: 径向 PRISMATIC；leaf_0 driver + (N−1) mimic ×1.0 upper=LEAF_TRAVEL（3/4/5/… 共用同一派生约束）
- source/gating: drive off S7/S8 的 `for i in range(N_LEAVES)`（S7:L348-L397 / S8:L420-L460）

### 轴 4：`leaves_per_side`（lateral telescope / pocket — 固定集，非 swept）
- count_param: 固定（telescope=2 per side、pocket=1）
- N_range: `[1, 2]`（不暴露大 N）
- copied object: 手写命名 leaf（door_0/door_1/_outer），不循环复制
- naming: `door_0`/`door_1`/`door_0_outer`/`door_1_outer`（telescope）；`door_0`/`door_0_outer`（pocket）
- placement: 每侧 inner+outer 伸缩对（telescope）/ 单全宽叶（pocket）
- joint policy: 1 driver + 3 mimic（同级 ×1.0、outer ×0.5）（telescope）/ 1 driver + 1 mimic ×0.5（pocket）
- source/gating: S1/S2/S9/S10/S11；**保持手写命名 leaf，不强行 loop 化**（拓扑等价类不变）

> 装饰（hazard 贴片、rivet/bolt 行、keypad 网格、ring bolt 圈、edge/meeting accent）一律 inline 为 parent visual，**无 per-decoration FIXED joint**。凡是会进入滑动扫掠路径的凸起条（leaf_seam_accent、pocket edge_accent/kick_plate、radial hazard arc、早期 sill 立柱式 drive boss）删除或改为 flush guide socket。

## 拓扑多样性审计

总组合数（按机构本地化 N 求和，而非笛卡尔积所有 N）：

```text
biparting_lateral_telescope : motif{cosine,zigzag,louver?no,wedge?no,flat} × surround{hex,lintel,bulkhead} × leaves_per_side{2}
  → 兼容 motif≈3（cosine/zigzag/flat）× surround 3 × 1 = 9
single_leaf_sliding_pocket  : motif{flat,cosine,zigzag} × surround{lintel(加大舱),hex} × N{1}
  → ≈3 × 2 × 1 = 6
vertical_lift               : motif{louver,flat} × surround{hex,lintel} × slab_count{3..8}=6
  → 2 × 2 × 6 = 24
iris_revolute_swing         : motif{wedge} × surround{bulkhead,hex(圆 aperture)} × petal_count{5..10}=6
  → 1 × 2 × 6 = 12
iris_radial_slide           : motif{wedge,flat} × surround{bulkhead only} × leaf_count{3..8}=6
  → 2 × 1 × 6 = 12
合计 ≈ 9 + 6 + 24 + 12 + 12 = 63 distinct topology classes（保守，未含 palette × continuous scale）
```

理由：机构本身就提供 5 个不同 joint 拓扑（±X PRISMATIC mimic 链 / +X PRISMATIC 单 mimic / ±Z PRISMATIC 独立 / about-rim REVOLUTE / 径向 PRISMATIC），叠加 multiplicity N 改变重复段拓扑、motif 改变 part 子结构、surround 改变固定 part 数与 FIXED joint 数。仅 mechanism × distinct-N 一项就有 5+6+6+1+1 远超 10。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对普通 seed 做 deterministic procedural sampling，`seed=0` 不特殊。采样顺序：(1) 选 `opening_mechanism`（加权：lateral/iris/lift 主流，pocket 稍少）；(2) 按 conditional 解析合法 `frame_surround` 与 `seam_motif` 集合（兼容矩阵 gating，iris-radial 强制 circular_bulkhead_ring）；(3) 仅对当前机构暴露的 count 轴做加权 N 采样（小 N 偏多、尾部稀有）、clamp、编进 `slot_choices`；(4) 采 independent 连续 scale → 派生 equation 行程 → 投影/回缩 inequality（iris 半径 + bore_clearance 内切、closed/open pose span、iris 角宽）；(5) 自由选 `palette_style`。每根 N 轴各自 clamp、sweep 各设上限（lift/leaf 8、petal 10）。Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）（机构×N×motif×surround 组合空间≈63 类 + 连续 scale/palette 变体足以达到）。

Controlled local parameterization：初版包含 opening_width_scale / opening_height_scale / surround_depth_scale（independent）、slide_travel_scale / lift_travel（equation 派生）、iris_open_angle / iris_radius_scale（conditional，随 N/surround clamp）。所有 scale 在 `resolve_config` clamp/派生/投影，受 doorway 内切、closed/open pose clearance、guide rail capture、joint range 和类别 identity 约束，不破坏 InterfaceSpec / MatingContract / multiplicity。

Regression overrides：默认无。若 sweep 发现稳定失败组合或 reviewer 指定回归样本，可添加少量显式 regression seed 并写明 seed/组合/原因；不得用 curated/modulo 表作为主 seed domain。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mechanism 加权 → conditional 解析 surround/motif → per-mechanism N 加权 → continuous scale 派生/投影 → palette | slot_choices_for_seed matches build choices |
| compatibility matrix | iris-revolute ⇒ 圆 aperture（bulkhead 或 hex 上的圆口）+ wedge motif；iris-radial ⇒ circular_bulkhead_ring + wedge/flat motif + 外圈径向槽；lateral/lift/pocket ⇒ 矩形 surround（hex/lintel）+ cosine/zigzag/louver/flat；louver 仅 lift；cosine/zigzag 仅 lateral/pocket/bulkhead-telescope；pocket ⇒ 加大右舱 | 无 floating / collision / 错轴 / closed-pose 穿模 / 超 max-N / bulky-module / optional-child 失败 |
| controlled local variation | opening_*_scale / surround_depth_scale clamp；iris_radius_scale 内切回缩；travel equation 派生 | 比例变化不破坏 doorway 内切、closed/open clearance、guide capture、joint origin、类别 identity |
| regression overrides | none（除非 sweep 后发现稳定失败组合） | previously failed / reviewer-selected cases only |
| random sweep | seeds 0-49 初轮（cumulative 0 / 0-4 / 0-19 / 0-49），0-999 成熟审计 | 与 MatingContract / joint / support / collision 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A opening_mechanism | 5（去重机构）/ 6（含 alt-source 行） | yes | yes | 5 个不同 joint 拓扑 |
| B multiplicity N | 5 distinct（1/2/4/6/8） | yes | yes | 按机构本地化，非单一正交轴 |
| C seam_motif | 5 | yes | yes | 部分随机构 conditional |
| D frame_surround | 3 | yes | yes | iris 隐含圆口 |

## Validator
- `slot_choices_for_seed` 返回已实现 module names（mechanism / surround / motif / per-mechanism N）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling（seed=0 不特殊）
- compatibility matrix / gating 阻止非法组合（iris+矩形小口 / louver+非 lift / cosine+iris / 超 max-N / 圆口被矩形机构封不住）
- optional regression overrides 稀疏且有理由
- 最终模板不无限轮换小型 curated 表作为主 seed domain
- 受控局部 scale（opening_*_scale / surround_depth_scale / iris_radius_scale / travel）clamp，不破坏 interface / clearance / joint origin / multiplicity
- 跨部件 scale 依赖（equation/inequality/conditional）在 `resolve_config` 求解，不留到 builder 失败
- 关键 InterfaceSpec / MatingContract：每个移动段有可见 surround 支撑路径（guide rail / wall pocket / rim pivot / 外圈径向槽），captured leaf 的过盈 overlap 需 element-scoped allow_overlap；滑动路径上的装饰凸条不得用 allow_overlap 掩盖
- 关键 joint type/axis/range：lateral/pocket ±X PRISMATIC、lift ±Z PRISMATIC、iris-revolute about-rim REVOLUTE、iris-radial 径向 PRISMATIC；driver/mimic 关系符合机构策略
- 复制对象遵循命名（slab_{i}/petal_{i}/leaf_{i}/door_*）与 placement（均匀堆叠 / 360-N 角度 / 径向 / 伸缩对）
- closed pose 真正封住门洞（无缝隙），open pose 露出真正贯通开口（无背墙、各段全收进容腔）

## Reject cases
- 门洞被背墙/实心板封死，open pose 不是真正贯通开口（变成柜门/电梯井而非 gate）。
- 移动段漂浮：leaf/petal/slab 无 surround guide rail / wall pocket / rim pivot / 外圈径向槽支撑路径；iris-radial 不允许靠中心 hub 假支撑。
- joint 轴错误：iris 用线性 ±X、lateral telescope 用 REVOLUTE、lift 不是 ±Z。
- iris 圆口与 surround 不匹配：圆 aperture 露出 surround 矩形 bore 的角，矩形机构封不住圆口，或 iris-radial 被采到 hex slab 导致径向叶/墙体槽扫掠穿模。
- closed pose 段间穿模或留缝（iris 瓣角宽超 360/N、telescope 缝不啮合、slab 不接触）。
- 滑动路径穿模：门叶上的凸起条、底部立柱、hazard arc、kick plate 等进入侧槽/底轨/径向槽扫掠体；应删除或改成 flush guide socket。
- multiplicity 退化：N 超机构上限（lift/leaf>8、petal>10）导致瓣过窄自碰，或 N<下限导致段过宽闭合互撞。
- 把 fixed greeble（piston/keypad/clamp/beacon）做成独立采样机构或带假 joint。
- 只换 palette/材质/尺寸当作新拓扑 candidate（颜色从不是结构轴）。
- mimic 链断裂：driver 缺失或 mimic multiplier 与机构策略不符（telescope outer 应 ×0.5、iris mimic 应 ×1.0）。

## 与相邻类别的边界
- 不该混入 **普通室内门/building door**：scifi gate 是动力机构 + 装甲面 + 危险条 + 贯通门洞，没有铰链平板木门 + 球形把手。
- 不该混入 **elevator door**：虽横向伸缩相近，但 scifi gate 涵盖 iris/lift/bulkhead 多机构 + 科幻装甲 surround，且必须保持贯通门洞（无电梯井背墙）。
- 不该混入 **vault/safe door**：那是嵌入柜体的厚旋钮圆盘门 + boltwork；scifi gate 是建筑级墙体门洞 surround。
- 不该混入 **iris diaphragm / camera shutter**：那是镜头级薄叶光圈；scifi gate 的 iris 是建筑门洞级装甲瓣 + 真实门洞 + surround。

## Multiplicity 轴汇总（recap，呼应第 8 节）
- 4 根 multiplicity 轴，按机构互斥本地化：`slab_count`[3,8]（lift）、`petal_count`[5,10]（iris-revolute）、`leaf_count`[3,8]（iris-radial）、`leaves_per_side`[1,2]（lateral/pocket，固定集非 swept）。
- 一次采样只激活当前机构对应轴；iris N ≠ slab N ≠ telescope N，不共享正交 N。
- 每根 swept 轴 drive off 已 loop-emit 的 variant（`for i in range(N)`），各自加权采样（小 N 偏多）、各自 clamp、sweep 各设上限。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；11/11 5★ 全读，每个 candidate 引用真实 model.py:Lx-Ly；4 slot（机构/N/motif/surround）+ 非结构 Slot E 家具；按机构本地化的多轴 multiplicity；兼容矩阵明确 iris-radial⇒circular_bulkhead_ring + 外圈槽，滑动路径凸起条删除；等待人工审核 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C/D/E | biparting_lateral_telescope + hazard_cosine_seam + hex_beveled_slab + jamb/clamp | rec_door_scifi_hex | L284-L468 | parent baseline（hex 家族） |
| S2 | A/C/D/E | biparting_lateral_telescope + zigzag_dovetail_seam + lintel_sill_side_housing + keypad/hazard | rec_door_scifi_zigzag | L211-L539 | parent baseline（lintel 家族，5 FIXED 家具 joint） |
| S3 | A/B/C/D | vertical_lift N=4 + horizontal_louver_slab + lintel | rec_scifi_gate_var_blastslabs4 | L167-L423 | slab_{i} 独立 staggered +Z 循环 |
| S4 | A/B/C/D | vertical_lift N=6 + louver + lintel | rec_scifi_gate_var_blastslabs6 | L238-L501 | slab_{i} bi-parting even-pitch 循环 |
| S5 | A/B/C/D | iris_revolute_swing N=6 + radial_petal_wedge + hex(圆 aperture) | rec_scifi_gate_var_iris6 | L291-L449 | petal_{i} REVOLUTE 循环 + mimic |
| S6 | A/B/C/D | iris_revolute_swing N=8 + radial_petal_wedge + hex | rec_scifi_gate_var_iris8 | L269-L365 | petal_{i} +Y REVOLUTE 循环 |
| S7 | A/B/C/D | iris_radial_slide N=4 + flat_armor_plate wedge（实现改配 bulkhead 外圈槽） | rec_scifi_gate_var_leaves4 | L247-L397 | leaf_{i} per-config 独立径向 PRISMATIC；采纳叶片/轴，不采纳 hex 组合 |
| S8 | A/B/C/D | iris_radial_slide N=8 + radial_petal_wedge（实现删除 hazard arc / 中央 hub，改配 bulkhead 外圈槽） | rec_scifi_gate_var_leaves8 | L281-L460 | leaf_{i} 径向 PRISMATIC + mimic 循环；采纳 leaf loop/mimic，不采纳中心架 |
| S9 | A/C/D | single_leaf_sliding_pocket + flat_armor_plate + lintel(加大右舱) | rec_scifi_gate_var_pocket | L172-L506 | 1 driver + 1 mimic ×0.5 |
| S10 | A/C/D/E | biparting_lateral_telescope + hazard_cosine_seam + hex + piston/beacon | rec_scifi_gate_var_piston_greeble | L398-L552 | fixed-furniture 层证据（piston/beacon） |
| S11 | A/C/D | biparting_lateral_telescope + zigzag_dovetail_seam + circular_bulkhead_ring | rec_scifi_gate_var_round_bulkhead | L206-L606 | `_make_bulkhead_ring` 圆口 surround |
