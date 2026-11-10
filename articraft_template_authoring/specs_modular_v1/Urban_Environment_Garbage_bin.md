# garbage_bin — modular template spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `garbage_bin` |
| template path | `agent/templates/Urban_Environment_Garbage_bin.py` |
| test path (optional) | `tests/agent/test_garbage_bin_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern` 说明：body 是 root chassis；lid_closure（主机构）+ mobility（轮/脚）+ lift_interface 都作为 parallel children / inline body visual 挂在 body 上。multiplicity 轴（lid slats、ribs、casters、lift-bar brackets）在各自 module 内 loop 复制。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 parent + 8 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点（全部 9 个样本逐文件读过）：

- **共享 chassis 骨架**：所有 9 个样本共用同一组 helper —— `_tapered_body()`（外撇锥形 4 壁 + floor，hollow，z∈[FOOT_H, WALL_TOP_Z]）、`_ribs()`（per-wall for-i loop，竖向 corrugation，long 壁 `RIB_COUNT_SIDE`、end 壁 `RIB_COUNT_END`）、`_rim()`（4 根 rim bar 框口）、`_feet_and_pockets()`（四角脚 + 前 forklift pockets + 两侧 trunnion pockets，全 inline body visual）。坐标约定一致：+Z up，feet 坐 z=0，truck 从 +X 进，lid 后铰在 -X 顶缘，centerline y=0 左右对称。
- **主机构永远是 REVOLUTE lid hinge**：8/9 用 `body_to_lid`（axis=(0,-1,0)，hinge_x=-BODY_D_TOP/2-LID_OVER，hinge_z=WALL_TOP_Z+0.004，upper≈105°，positive q 把前缘抬起向后翻）。slot_top 例外：固定甲板 + 内摆投递 flap（`body_to_flap` axis=(0,1,0)，hinge@槽后缘，upper≈85° 向内下摆）。
- **lid 必须是一片连接盖，不浮空板条**：slat 类 lid 都在 slat loop 之外加一层 `skin` / `_lid_skin_geometry`（thin base plate）把所有 slat 连成一片。
- **真实关节只有两类**：lid hinge=REVOLUTE，wheel roll=CONTINUOUS（axis along Y，origin@axle center，z=wheel_R）。feet / pockets / trunnions / lift-bar / fork-plate 全部 inline body visual，无 FIXED 装饰关节。
- **结构变化轴只有 4 个 + multiplicity**：lid_closure（part tree / joint 拓扑差异最大）、body_profile（taper vs straight）、mobility（fixed feet vs caster CONTINUOUS，增删 wheel 子件）、lift_interface（短 trunnion pocket vs 整条连续 lift bar）。其余（绿/锈/galvanized 配色、2yard/4yard 尺寸、rib 密度）只是参数 / 材质，不立 slot。

## 核心身份

garbage_bin = **商用前装式钢制垃圾箱（commercial front-load steel dumpster / bin）**。物理含义：一个落地的、由垃圾车举升倾倒的大型钢制废物容器。默认成熟域：

- **体形**：tapered 或直立的矩形钢箱体，四壁压有竖向 corrugation ribs，卷边顶 rim，内部 hollow（开口投递）。约 2–4 cubic yard 量级（宽≈1.8 m，深≈1.0–1.2 m，高≈1.2 m），feet 坐 z=0。
- **主功能 / 主机构**：顶部钢盖的 **REVOLUTE 后铰翻盖** 是 defining joint —— 后顶缘横轴（axis≈Y），前缘抬起向后翻开投递。这是该类目身份的唯一主运动轴。
- **卡车举升接口**：前 forklift pockets + 两侧 trunnion pockets（或整条 lift bar），是“被车举起倾倒”的语义标记，区别于家用桶。
- **落地 / 移动**：四角固定钢脚，或换装 swivel caster（CONTINUOUS 滚轮）实现可推行。

**不该混入的相邻类别**：

- **Large_Trashcan（wheelie bin / 家用带轮翻盖桶）**：两轮 + 顶铰 pedal/手翻盖的圆/方塑料桶，靠后两轮 + 倾倒推行，**无 forklift/trunnion 举升接口、无 corrugated 钢壳、无前装外撇 taper**。garbage_bin 必须保留 truck-lift 接口 + 钢制 dumpster 体量，不可退化成家用桶。
- **Trashcan1 / Trashcan2（街道小废物桶 / pole-mount can）**：圆筒或开口篮筐式街头垃圾桶，体量小、常带摆动小翻门或开顶，无落地举升接口、无后铰全宽钢盖。garbage_bin 不可缩成街头小桶或镂空篮筐。

边界判据：必须同时满足 (a) 钢制矩形 corrugated dumpster 体量；(b) REVOLUTE 后铰钢盖主机构；(c) 至少一种 truck-lift 接口（fork pockets / trunnion / lift bar）。任一缺失即出类目。

## 槽位 + 候选模块表

### Slot A：lid_closure（主机构槽 —— 箱口封闭/开启动作；joint 拓扑差异最大）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rear_hinged_slat_lid`（baseline/parent） | rec_green-steel-commercial-front-load-dumpster-with-_20260608_164732_054691_3ec067a0 | `_lid_mesh` L233-L259; part+joint `body_to_lid` REVOLUTE L287-L314 | eligible if compatible | 单片全宽后铰板条翻盖：slat loop（`LID_SLATS`）+ thin base `skin`（L247-L249）连成一片 + 前缘 lift handle；REVOLUTE axis=(0,-1,0) @ 后顶缘，upper 105° |
| `lid_slat_count`（slat-multiplicity 形态） | rec_garbage_bin_var_lid_slat_count | helpers `_slat_geometry` L234-L243 / `_lid_skin_geometry` L246-L250 / `_handle_geometry` L253-L257; slat loop + skin L298-L323; joint L335-L348 | eligible if compatible | 同 rear_hinged 拓扑，但 slat 数由单参数 `LID_SLAT_COUNT` 驱动（疏/密），shared `_slat_geometry` helper + 单 `_lid_skin_geometry` skin 保持一片盖。承载 lid_slats multiplicity 轴的 reference 实现 |
| `twin_split_lids` | rec_garbage_bin_var_twin_split_lids | `_half_lid_mesh` L237-L280; for-i-in-range(2) parts `lid_i` + 镜像 joints `body_to_lid_i` REVOLUTE L318-L349 | eligible if compatible | 中线对开双半盖：2 个独立 part，各自后铰独立翻起（一边开另一边可关）；y_off=±full_width/4；每半各有 slat loop + skin。lid_count=2 多重度 |
| `domed_flat_lid` | rec_garbage_bin_var_domed_flat_lid | `_dome_lid_mesh`（cosine dome surface）L237-L375; part+joint L402-L429 | eligible if compatible | 圆拱实心钢罩盖：cos·cos dome 曲面 (nx×ny grid) + thin shell plate + 前缘 handle，整体后铰翻起；REVOLUTE axis=(0,-1,0) upper 105° |
| `slot_top_lid` | rec_garbage_bin_var_slot_top_lid | `_deck_mesh`（固定甲板+槽口）L242-L305; `_make_flap_slat` L308-L310 / `_flap_frame_mesh` L313-...; flap part+slat loop L371-L391; joint `body_to_flap` REVOLUTE L399-L411 | eligible if compatible | 固定投递甲板（4 panel 围槽口 + slot lip）+ 后铰**内摆** spring-flap 投递口：flap axis=(0,1,0) @ 槽后缘，positive q 把前缘**向内下摆**入箱（upper 85°）。joint 命名 `body_to_flap`（注意 ≠ `body_to_lid`） |

degrade 说明：无单候选 slot —— A 有 5 个结构不同候选。

### Slot B：body_profile（体形 / footprint 家族）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `sloped_front_load_tapered`（baseline/parent） | rec_green-steel-commercial-front-load-dumpster-with-_20260608_164732_054691_3ec067a0 | `_tapered_body` L70-L117; `_ribs` L120-L189 | eligible if compatible | 外撇锥形前装箱体：BODY_D_TOP(1.18) > BODY_D_BOT(1.00)，顶比底在 X 上更宽；trapezoidal 4 壁 + floor，taper-aware ribs（end 壁 rib 法线随 taper 倾斜） |
| `rectangular_upright` | rec_garbage_bin_var_rectangular_body | `_straight_body` L70-L113; `_ribs`（straight 版）L116-...; rim/feet/lid 同 baseline | eligible if compatible | 四壁竖直，口=底 footprint（BODY_D 单值）；ribs 竖直无 taper 倾斜。结构差异在 wall geometry（vertical vs trapezoidal）+ rib 法线 |

degrade 说明：B 只有 2 候选。理由：在 commercial dumpster 真实形态内，body 的**结构性**变化只有“外撇前装锥形 vs 直立矩形”两类；圆筒 / 篮筐式壁面会出类目（见排除项），尺寸（2yard/4yard）只是缩放参数不立 candidate。2 候选满足 slot 最低门槛（≥2），且与 §2.3 “来源不足可降到 2 并说明理由”一致。

### Slot C：mobility（落地 / 移动机构；wheel 为真 CONTINUOUS roll joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `fixed_corner_feet`（baseline/parent） | rec_green-steel-commercial-front-load-dumpster-with-_20260608_164732_054691_3ec067a0 | `_feet_and_pockets` 四角脚 loop L208-L218（feet 部分） | eligible if compatible | 四角固定钢脚（FOOT_SIZE×FOOT_SIZE×FOOT_H），feet 坐 z=0，无轮；inline body visual，无关节 |
| `four_caster_mobile` | rec_garbage_bin_var_four_caster_mobile | `_caster_fork_mesh` L243-L279; fork inline-visual loop L355-L361; wheel parts + `body_to_wheel_i` CONTINUOUS ×4 L370-L392 | eligible if compatible | 四角 swivel caster：fork+mounting plate 为 inline body visual，每角一个 `wheel_i` 子 part（Cylinder，rpy 旋成轴 along Y）+ CONTINUOUS roll joint @ axle center (z=WHEEL_R)，各自滚动 |
| `two_caster_tilt` | rec_garbage_bin_var_two_caster_tilt | `_feet_and_pockets`（仅后两脚）L224-L250; `_caster_fork_mesh(sign_y)` L274-...; `_caster_wheel_mesh` L353-...; 前两轮 part + `body_to_wheel_i` CONTINUOUS ×2 L448-L483 | eligible if compatible | 前两角 caster 轮（CONTINUOUS ×2，CASTER_X/CASTER_Y 在 body 外侧）+ 后两角固定脚的倾倒推行式；front-only feet 被移除并替换为轮 |

degrade 说明：C 有 3 候选（feet / 4-caster / 2-caster），结构差异在 wheel 子件数（0/4/2）与 feet 保留情况。

### Slot D：lift_interface（卡车举升接口）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `fork_pockets_plus_side_trunnions`（baseline/parent） | rec_green-steel-commercial-front-load-dumpster-with-_20260608_164732_054691_3ec067a0 | `_feet_and_pockets` forklift pocket loop L220-L223 + side trunnion loop L225-L229 | eligible if compatible | 前 2 个 forklift pockets（横管）+ 两侧各 1 短 trunnion pocket；全 inline body visual |
| `continuous_trunnion_lift_bar` | rec_garbage_bin_var_trunnion_lift_bar | `_lift_bar_assembly(side_sign)` L236-L300（bar = CylinderGeometry 沿 X + per-frac cradle bracket loop） | eligible if compatible | 两侧各一整条水平 lift bar（圆 rod 沿 X）+ 沿 bar 规律分布的焊接 cradle 托架（mounting plate + 2 ear + cradle strap），替换短 trunnion pocket。bracket count = `len(BRACKET_PAIR_FRACS)` multiplicity |

degrade 说明：D 有 2 候选。理由：truck-lift 接口的真实结构家族就是“离散短 trunnion pocket vs 整条连续 lift bar”两类；前 forklift pockets 在两者中都保留（公共 inline visual）。2 候选满足最低门槛。side-load/rear-load packer 机构、底部排液阀属未来回补轴（见排除项），本批不立。

## 槽位图（slot graph）

pattern: `parallel_children`（+ module-local `multiplicity`）

```
                         body (ROOT chassis)
                         = Slot B body_profile (_tapered_body / _straight_body)
                           + _ribs + _rim (inline visuals)
                           + Slot C mobility feet/fork-plate inline visuals
                           + Slot D lift_interface inline visuals (pockets / lift bar)
        ┌────────────────────────┼───────────────────────────┐
        │                        │                           │
 [A lid_closure]          [C mobility wheels]          [D no separate child]
 lid / lid_i / flap        wheel_i (0/2/4)             (inline body visual only)
        │                        │
  REVOLUTE body_to_lid     CONTINUOUS body_to_wheel_i
  (or body_to_flap;         axis=(0,1,0) @ axle center
   twin = 2× body_to_lid_i) z=WHEEL_R
  axis≈(0,-1,0) @ rear-top
  hinge (slot_top: (0,1,0))
```

接口点位与 joint policy：

- **body 是唯一 root**。坐标系：+Z up，feet z=0，front=+X，rear=-X，centerline y=0。`WALL_TOP_Z = FOOT_H + BODY_H` 是顶缘平面。
- **A→body（lid hinge，主机构）**：mating = body 后顶缘 (-X edge @ WALL_TOP_Z)。hinge origin `(-BODY_D_TOP/2 - LID_OVER, [0 或 ±full_width/4], WALL_TOP_Z+0.004)`，axis=(0,-1,0)，REVOLUTE，lower=0 closed（盖平躺、与 rim 接触 → element-scoped `allow_overlap(body, lid)` + `expect_overlap` xy footprint），upper≈radians(105)。
  - `twin_split_lids`：2 条镜像 hinge `body_to_lid_0/1`，y_off=±full_width/4，各自独立。
  - `slot_top_lid`：先放固定 deck（inline visual on body），flap hinge `body_to_flap` @ 槽后缘 `(-SLOT_D/2, 0, WALL_TOP_Z+DECK_T)`，axis=(0,1,0)，**内摆** upper≈radians(85)。
- **C→body（wheel roll）**：mating = body 底角下方。每个 `wheel_i` 是独立子 part，CONTINUOUS joint origin @ axle center `(cx, cy, WHEEL_R)`，axis=(0,1,0)。fork/mounting-plate 是 inline body visual（不动）。`fixed_corner_feet` 无 wheel 子件（纯 inline feet）。
- **D**：无独立子 part —— 全部 inline body visual（pockets / trunnions / lift bar + cradle brackets 直接 merge 进 body mesh）。互斥：A 的 slot_top 与其它 lid 互斥（要么全宽盖要么 deck+flap）；C 的 feet/4-caster/2-caster 三选一；D 的 pocket/lift-bar 二选一。
- **派生关系**：mobility 选 caster 时 body 底面到地的净空由 `WHEEL_R + fork drop` 决定（feet 版由 FOOT_H 决定）——见参数表 inequality。

## 每槽位 Module Emits / Interfaces

### Slot A / module rear_hinged_slat_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（visual `lid_slats`：slat loop + base skin + front handle） | parent / model.py:L287-L289, L233-L259 |
| internal joints | 无（slat 是单 part 内 visual loop，不是关节） | parent / model.py:L250-L254 |
| upstream interface | body 后顶缘 hinge anchor `(-BODY_D_TOP/2-LID_OVER, 0, WALL_TOP_Z+0.004)` | parent / model.py:L299-L300 |
| downstream interface | `body_to_lid` REVOLUTE axis=(0,-1,0) lower=0 upper=105° | parent / model.py:L301-L314 |

### Slot A / module lid_slat_count
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（visual `lid_skin` + slats `slat_i`(i=0..N-1) + `lid_handle`） | rec_garbage_bin_var_lid_slat_count / model.py:L288-L323 |
| internal joints | 无（slat loop 内 visual） | rec_garbage_bin_var_lid_slat_count / model.py:L307-L315 |
| upstream interface | hinge anchor 同 baseline | rec_garbage_bin_var_lid_slat_count / model.py:L333-L334 |
| downstream interface | `body_to_lid` REVOLUTE axis=(0,-1,0) upper=105° | rec_garbage_bin_var_lid_slat_count / model.py:L335-L348 |

### Slot A / module twin_split_lids
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_0`、`lid_1`（各 `lid_i_slats`：half-width slat loop + skin + handle） | rec_garbage_bin_var_twin_split_lids / model.py:L322-L327 |
| internal joints | 无（每半 part 内 visual loop） | rec_garbage_bin_var_twin_split_lids / model.py:L269-L273 |
| upstream interface | 2× hinge anchor，y_off=±full_width/4 @ 后顶缘 | rec_garbage_bin_var_twin_split_lids / model.py:L313-L344 |
| downstream interface | `body_to_lid_0/1` REVOLUTE axis=(0,-1,0) 各自 upper=105°，独立开合 | rec_garbage_bin_var_twin_split_lids / model.py:L339-L349 |

### Slot A / module domed_flat_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（visual `lid_dome`：cos·cos dome surface + shell plate + handle） | rec_garbage_bin_var_domed_flat_lid / model.py:L402-L404 |
| internal joints | 无 | — |
| upstream interface | hinge anchor 同 baseline | rec_garbage_bin_var_domed_flat_lid / model.py:L414-L415 |
| downstream interface | `body_to_lid` REVOLUTE axis=(0,-1,0) upper=105° | rec_garbage_bin_var_domed_flat_lid / model.py:L416-L429 |

### Slot A / module slot_top_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | body 上 inline `deck`(visual `_deck_mesh`)；child `flap`（visual `flap_frame` + slat loop `flap_slat_i`） | rec_garbage_bin_var_slot_top_lid / model.py:L352-L391 |
| internal joints | 无（flap slat loop 内 visual） | rec_garbage_bin_var_slot_top_lid / model.py:L378-L386 |
| upstream interface | deck 固定在 WALL_TOP_Z；flap hinge @ 槽后缘 `(-SLOT_D/2, 0, WALL_TOP_Z+DECK_T)` | rec_garbage_bin_var_slot_top_lid / model.py:L397-L398 |
| downstream interface | `body_to_flap` REVOLUTE axis=(0,1,0) 内摆 lower=0 upper=85° | rec_garbage_bin_var_slot_top_lid / model.py:L399-L411 |

### Slot B / module sloped_front_load_tapered
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root visuals `body_shell`(taper) + `body_ribs`(taper-aware) + `top_rim` | parent / model.py:L70-L189, L271-L277 |
| internal joints | 无 | — |
| upstream interface | root（无 parent）；feet z=0；提供顶缘 WALL_TOP_Z 给 A | parent / model.py:L66-L67 |
| downstream interface | 后顶缘 hinge plane + 底角 mobility anchor + 壁面 lift_interface mount | parent / model.py:L208-L229 |

### Slot B / module rectangular_upright
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root visuals `body_shell`(vertical) + `body_ribs`(straight) + `top_rim` | rec_garbage_bin_var_rectangular_body / model.py:L70-L113, L116-... |
| internal joints | 无 | — |
| upstream interface | root；feet z=0；BODY_D 单值（口=底） | rec_garbage_bin_var_rectangular_body / model.py:L78-L79 |
| downstream interface | 同 tapered 的 hinge/mobility/lift anchor（接口面平移，无 taper 倾斜） | rec_garbage_bin_var_rectangular_body / model.py:L197-... |

### Slot C / module fixed_corner_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline body visual：四角脚 box loop（无独立 part） | parent / model.py:L213-L218 |
| internal joints | 无 | — |
| upstream interface | 挂 body 底四角，z∈[0, FOOT_H] | parent / model.py:L216-L218 |
| downstream interface | 无（地面接触由 feet 底面 z=0 提供） | parent / model.py:L213-L218 |

### Slot C / module four_caster_mobile
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline `caster_fork_i`×4（fork+plate visual）+ child parts `wheel_i`×4（Cylinder tire） | rec_garbage_bin_var_four_caster_mobile / model.py:L355-L382 |
| internal joints | `body_to_wheel_i` CONTINUOUS ×4 | rec_garbage_bin_var_four_caster_mobile / model.py:L384-L392 |
| upstream interface | fork plate mounting face @ body 底角 z=FOOT_H | rec_garbage_bin_var_four_caster_mobile / model.py:L356-L361 |
| downstream interface | 4× CONTINUOUS axis=(0,1,0) origin @ axle `(cx,cy,WHEEL_R)` | rec_garbage_bin_var_four_caster_mobile / model.py:L384-L392 |

### Slot C / module two_caster_tilt
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline `caster_fork_i`×2（前角）+ 后两脚 inline feet + child `wheel_i`×2 | rec_garbage_bin_var_two_caster_tilt / model.py:L234-L238, L452-L464 |
| internal joints | `body_to_wheel_i` CONTINUOUS ×2（前角） | rec_garbage_bin_var_two_caster_tilt / model.py:L474-L483 |
| upstream interface | 前两角 caster plate @ CASTER_X/CASTER_Y（body 外侧）；后两角 fixed feet z∈[0,FOOT_H] | rec_garbage_bin_var_two_caster_tilt / model.py:L234-L243 |
| downstream interface | 2× CONTINUOUS axis=(0,1,0) origin `(CASTER_X, ±CASTER_Y, WHEEL_R)` | rec_garbage_bin_var_two_caster_tilt / model.py:L474-L483 |

### Slot D / module fork_pockets_plus_side_trunnions
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline body visual：前 2 forklift pocket loop + 两侧 2 trunnion pocket loop | parent / model.py:L220-L229 |
| internal joints | 无 | — |
| upstream interface | forklift pocket @ 前壁底 z≈FOOT_H+0.06；trunnion @ 侧壁 z≈FOOT_H+BODY_H*0.62 | parent / model.py:L221-L228 |
| downstream interface | 无（truck-arm 接触面，纯 visual） | parent / model.py:L225-L229 |

### Slot D / module continuous_trunnion_lift_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline body visual：两侧各一条 lift bar（Cylinder 沿 X）+ per-frac cradle bracket loop | rec_garbage_bin_var_trunnion_lift_bar / model.py:L236-L300 |
| internal joints | 无 | — |
| upstream interface | bar @ 侧壁外 standoff，z=FOOT_H+BODY_H*BAR_HEIGHT_RATIO；bracket mounting plate 贴壁 | rec_garbage_bin_var_trunnion_lift_bar / model.py:L254-L277 |
| downstream interface | 无（truck-arm lift bar 接触面，纯 visual） | rec_garbage_bin_var_trunnion_lift_bar / model.py:L257-L298 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `lid_closure` | enum | rear_hinged_slat_lid / lid_slat_count / twin_split_lids / domed_flat_lid / slot_top_lid | rear_hinged_slat_lid | choice | deterministic procedural sampler（compatibility-gated） | Slot A table |
| `body_profile` | enum | sloped_front_load_tapered / rectangular_upright | sloped_front_load_tapered | choice | sampler | Slot B table |
| `mobility` | enum | fixed_corner_feet / four_caster_mobile / two_caster_tilt | fixed_corner_feet | choice | sampler | Slot C table |
| `lift_interface` | enum | fork_pockets_plus_side_trunnions / continuous_trunnion_lift_bar | fork_pockets_plus_side_trunnions | choice | sampler | Slot D table |
| `palette_style` | enum | weathered_green / municipal_blue / rust_brown / galvanized_steel / hazard_red / charcoal_black | weathered_green | choice | 仅改 material rgba，不改拓扑 | parent L265-L268; twin L286-L290 |
| `lid_slat_count` | int | [4, 16] | 11 | independent(conditional) | 仅 slat-lid 类（rear/lid_slat_count/twin）有效；twin 用 half；domed/slot_top 无此轴 | rec_garbage_bin_var_lid_slat_count L293; parent L60 |
| `lid_count` | int | {1, 2} | 1 | conditional | 2 仅当 lid_closure=twin_split_lids；其余=1 | rec_garbage_bin_var_twin_split_lids L318 |
| `caster_count` | int | {0, 2, 4} | 0 | conditional | =0 feet / =4 four_caster / =2 two_caster，由 mobility enum 决定 | four L370; two L448 |
| `lift_bracket_count` | int | [2, 4] | 2 | conditional | 仅 lift_interface=continuous_trunnion_lift_bar 时有效（`BRACKET_PAIR_FRACS` 长度） | rec_garbage_bin_var_trunnion_lift_bar L268 |
| `rib_count_side` | int | [6, 12] | 9 | independent | long 壁 corrugation 数（纹理轴，不计样本数） | parent L56 |
| `rib_count_end` | int | [3, 7] | 5 | independent | end 壁 corrugation 数 | parent L57 |
| `body_width_scale` | float | [0.85, 1.20] | 1.0 | independent | BODY_W 缩放，clamp | parent L45 |
| `body_height_scale` | float | [0.85, 1.25] | 1.0 | independent | BODY_H 缩放，clamp | parent L48 |
| `body_depth_scale` | float | [0.85, 1.20] | 1.0 | independent | BODY_D_BOT 缩放 | parent L46 |
| `taper_ratio` | float | derived | — | equation | `BODY_D_TOP = BODY_D_BOT * (1.10..1.22)`（tapered）；rectangular 时 =1.0 | parent L46-L47 |
| `lid_open_upper` | float | [rad(90), rad(110)] | rad(105) | independent | slat/dome lid hinge 行程上限；slot_top flap 用 [rad(75),rad(90)] | parent L312 |
| (—) | constraint | — | — | inequality | `lid_closure=slot_top_lid` 互斥所有全宽盖（A 内单选，已由 enum 保证） | 接口 |
| (—) | constraint | — | — | inequality | caster 净空：`WHEEL_R(+fork drop) ≥ 0` 且 body 底面不穿地；feet 版 feet 底 z=0；mobility 与 body_height_scale 独立但 wheel origin z=WHEEL_R 固定 | mobility 接口 |
| (—) | constraint | — | — | inequality | 闭盖 seating：lid closed AABB top-z 接触 body rim（`abs(lid_min_z - body_top_z) < 0.05`），违反则回缩 LID_OVER/hinge_z | parent L364-L368 |

连续尺寸采样契约：先采 independent 主尺度（body_*_scale、rib_count_*、lid_open_upper），再按 equation 派生 taper（BODY_D_TOP），再用 inequality 投影闭盖 seating + caster 净空，conditional 轴（lid_slat_count/lid_count/caster_count/lift_bracket_count）在采样前按上游 enum 解析。

## Multiplicity / Copy Logic

本类有 **4 根独立 multiplicity 轴**（按轴单独声明；下游模板对每根各做一次加权采样、各自 clamp、sweep 各自设上限）。

### 轴 1：lid_slats（主轴）
- `count_param`: `lid_slat_count`
- `N_range`: [4, 16]（产品域；parent=11；few≈5、many≈14 由 rec_garbage_bin_var_lid_slat_count 覆盖）
- sampling domain: 中段（8–12）高频，端点（4–5 / 14–16）稀有
- copied object: lid slat 条（`slat_i` / `lid_i_slats` 内）
- naming: `slat_i` / half-lid 内 `lid_{j}_slats`
- placement: 沿 Y 均匀 pitch `(width - LID_GAP) / N`，每条 BoxGeometry，**外加一层 `_lid_skin_geometry` skin 把所有 slat 连成一片**（绝不浮空）
- joint policy: 无关节（part 内 visual loop）
- source/gating: 仅 lid_closure∈{rear_hinged_slat_lid, lid_slat_count, twin_split_lids} 有效；domed/slot_top 不暴露此轴（twin 用 half-width 子集 n_half）

### 轴 2：lid_count
- `count_param`: `lid_count`
- `N_range`: {1, 2}
- sampling domain: 1 高频，2（twin）较稀
- copied object: 整片半盖 part + 镜像 hinge
- naming: `lid_i` + `body_to_lid_i`
- placement: y_off=±full_width/4，镜像 across y=0
- joint policy: 每片各 1 REVOLUTE，独立开合
- source/gating: 2 仅当 lid_closure=twin_split_lids（conditional）

### 轴 3：caster_count
- `count_param`: `caster_count`
- `N_range`: {0, 2, 4}
- sampling domain: 由 mobility enum 决定（0=feet / 2=two_caster / 4=four_caster）
- copied object: `wheel_i` 子 part + `caster_fork_i` inline visual
- naming: `wheel_i` + `body_to_wheel_i`；`caster_fork_i`
- placement: 4 = 四角；2 = 前两角（CASTER_X/CASTER_Y 外侧）+ 后两固定脚
- joint policy: 每轮 1 CONTINUOUS axis=(0,1,0) origin @ axle (z=WHEEL_R)
- source/gating: conditional on mobility enum

### 轴 4：lift_bracket_count
- `count_param`: `lift_bracket_count`
- `N_range`: [2, 4]（`BRACKET_PAIR_FRACS` 长度，每侧）
- sampling domain: 2 高频，3–4 稀有
- copied object: cradle bracket（mounting plate + 2 ear + cradle strap）沿 lift bar
- naming: inline body visual（per-frac merge），无独立 part 名
- placement: 沿 bar 长度按 frac 规律分布，每侧镜像
- joint policy: 无关节（inline body visual）
- source/gating: 仅 lift_interface=continuous_trunnion_lift_bar 有效

次级 texture count（不计样本数）：`rib_count_side` [6,12]、`rib_count_end` [3,7]，per-wall loop，inline body visual，无关节。

## 拓扑多样性审计

总组合数（结构槽）：A(5) × B(2) × C(3) × D(2) = **60** legal slot 组合（slot_top 与全宽盖在 A 内已是互斥单选，不额外相乘）。
加上 multiplicity distinct-N：lid_slats {4..16} + lid_count {1,2} + caster_count {0,2,4} + lift_bracket_count {2..4} 进一步放大 distinct topology equivalence classes 远超 60。

理由：单是 4 结构槽 product = 60 ≥ 10 已独立满足硬门；twin(lid_count=2)、caster_count、slat_count、lift_bracket_count 各自改变 part/joint count → slot choice tuple distinct equivalence class，叠加后 1000-seed slot choice tuple distinct 预计 按 ≥300 report-only 口径观察。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic procedural sampling 依次加权选 lid_closure → body_profile → mobility → lift_interface，再解析 conditional multiplicity（lid_slat_count / lid_count / caster_count / lift_bracket_count），最后采连续 scale（body_*_scale、rib_count_*、lid_open_upper）并经 `resolve_config` clamp/derive/project。compatibility matrix 排除：slot_top + 全宽盖共存（A 内单选保证）；twin 的 lid_count=2 与非-twin 共存；caster_count 与 mobility enum 不一致。无大型 curated/modulo 主表；最多少量 regression overrides（见下）。random sweep：seeds 0-49 初轮，0-999 成熟审计。Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；60 结构组合 × multiplicity 轴，低于 300 时记录类别离散空间或采样权重原因；不设门。

Controlled local parameterization：`body_width_scale` [0.85,1.20]、`body_height_scale` [0.85,1.25]、`body_depth_scale` [0.85,1.20]（independent，clamp）；`taper_ratio`（equation：BODY_D_TOP=BODY_D_BOT×k，rectangular 时 k=1）；`lid_open_upper`（independent，slat/dome [90°,110°]、flap [75°,90°]）；`rib_count_side/end`（independent int）。这些只改安全比例 / 行程 / 纹理密度，不破坏 hinge anchor（始终 -BODY_D_TOP/2-LID_OVER @ WALL_TOP_Z）、wheel axle 净空（z=WHEEL_R）、闭盖 seating（inequality 投影）或 truck-lift 接口语义。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权选 4 enum slot + 解析 4 conditional N + 采连续 scale | slot_choices_for_seed matches build choices |
| compatibility matrix | A 内单选（slot_top 互斥全宽盖）；lid_count=2↔twin；caster_count↔mobility；lift_bracket_count↔lift bar | no floating slats, lid-rim seating overlap, hinge axis/range, wheel axle ground clearance, closed pose |
| controlled local variation | body_*_scale + rib counts + lid_open_upper，clamp/derive/project | proportions vary，hinge/axle/接口 / category identity 不破 |
| regression overrides | none（初版无；若 sweep 暴露特定失败 seed 再加并注明） | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A lid_closure | 5 | yes | yes | 主机构槽 |
| B body_profile | 2 | yes | no | 真实结构家族仅 taper/straight 两类（degrade 已说明） |
| C mobility | 3 | yes | yes | feet/4-caster/2-caster |
| D lift_interface | 2 | yes | no | pocket/lift-bar 两类（degrade 已说明） |

## Validator

- slot_choices_for_seed returns implemented module names（4 slot enum）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（slot_top↔全宽盖、lid_count↔twin、caster_count↔mobility、lift_bracket_count↔lift bar）
- optional regression overrides are sparse and justified（初版 none）
- final templates do not endlessly cycle a small curated table
- controlled local scale params clamped；不破 hinge anchor / wheel axle / 闭盖 seating / 接口 / identity
- cross-part scale deps（taper equation、caster 净空 inequality、闭盖 seating inequality）resolved in `resolve_config`
- critical InterfaceSpec/MatingContract exist：lid hinge @ 后顶缘、wheel axle @ (cx,cy,WHEEL_R)、lift_interface mount 面
- key joints have expected type/axis/range：body_to_lid REVOLUTE axis≈(0,-1,0) upper≈105°（slot_top flap axis=(0,1,0) upper≈85°）；body_to_wheel_i CONTINUOUS axis=(0,1,0)
- copied objects follow naming/placement policy：`slat_i`/`lid_i`/`wheel_i`/`caster_fork_i`/per-frac bracket；slat 永远有 skin 连成一片

## Reject cases

- lid 不是 REVOLUTE 后铰（缺主机构）或 hinge 不在后顶缘 → 出类目。
- slat 板条浮空（缺 base skin / 缺 `_lid_skin_geometry`）→ 散件，reject。
- 闭盖未坐在 rim 上（lid_min_z 与 body_top_z 偏离 >0.05，或盖悬空 / 穿入箱内）。
- mobility=caster 但 wheel 不是 CONTINUOUS roll 子 part，或 axle 不沿 Y / wheel 穿地（origin z≠WHEEL_R）。
- 缺失全部 truck-lift 接口（无 fork pocket / trunnion / lift bar）→ 退化成家用桶，出类目。
- body 退化成圆筒 / 镂空篮筐 / 街头小桶体量（违反 commercial dumpster 体形与体量）。
- twin_split_lids 两半 hinge 不在 centerline 两侧（lid_0 应 y<0、lid_1 应 y>0）或不独立开合。
- slot_top flap 向**外/上**翻（应内摆入箱，axis=(0,1,0) positive q 把前缘下摆）。
- multiplicity 失配：caster_count 与 mobility enum 不一致，或 lid_count=2 但 lid_closure≠twin。

## 与相邻类别的边界

- 不该混入：**Large_Trashcan（wheelie bin）** —— 该类是两轮塑料家用翻盖桶，靠后两轮倾倒推行、顶铰 pedal/手翻小盖，无 forklift/trunnion 举升接口、无 corrugated 钢壳、无前装外撇 taper、体量小。garbage_bin 必须保留 truck-lift 接口 + 钢制 dumpster 体量；caster 选项也只是工业 swivel caster，不是 wheelie 两轮。
- 不该混入：**Trashcan1 / Trashcan2（街道小废物桶）** —— 圆筒 / 开口篮筐式街头垃圾桶，体量小、常带小摆门或开顶 / pole-mount，无落地举升接口、无后铰全宽钢盖、无 corrugation 钢壳。garbage_bin 不可缩成街头小桶或镂空篮筐。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_tapered_body` / `_straight_body`（Slot B 二选一）、`_ribs`（taper-aware vs straight 两版）、`_rim`、`_feet_and_pockets`（feet+pockets+trunnion 公共骨架）。slat lid 三模块共享 `_slat_geometry` + `_lid_skin_geometry` + `_handle_geometry`（来自 lid_slat_count 的干净 helper 拆分）。caster 两模块共享 `_caster_fork_mesh` + wheel-part 工厂。
- InterfaceSpec/MatingContract 重点：lid hinge anchor（`-BODY_D_TOP/2-LID_OVER, *, WALL_TOP_Z+0.004`）必须随 body_*_scale 重算；wheel axle origin z=WHEEL_R 固定；闭盖 seating 是 element-scoped `allow_overlap(body, lid)` + `expect_overlap` xy footprint（twin 用 min_overlap≈0.35，single≈0.8）。
- captured-pin / overlap：lid 坐 rim、slat 与 skin 小 embed、rib RIB_EMBED、caster fork embed —— 均需 element-scoped allow_overlap。
- 暂不进入 seed domain 的组合：无（4 槽全部互相兼容；唯一互斥已由 A 内单选 + conditional N gating 表达）。未来回补轴（side/rear-load packer、底部排液阀）本批不立。
