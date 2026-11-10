# Single Revolute Hinge Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `single_revolute_hinge` |
| template path | `agent/templates/single_revolute_hinge.py` |
| test path | `tests/agent/test_single_revolute_hinge_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 55 |
| read_count | 14 |
| read_scope | 14 个 5 星样本完整/重点精读，覆盖全部 prompt 家族（leaf-leaf、strap、knuckle-stack、clevis/fork、trunnion-tab、bracket-cover、pedestal/block、object cabinet/gate）；其余 41 个用 grep（part 数 / visual 数 / axis 向量 / 是否独立 pin part / cadquery vs primitive / KNUCKLE_COUNT / motion_limits）扫描确认轴覆盖 |
| source_index_policy | 只索引被采纳的可复用片段；object-mounted hinge（cabinet/gate，宿主 carcass+door）与 hardware hinge（两个 hinge half）共享同一 `body_to_door` 单 revolute 骨架，但用 `host_family` 区分，不把宿主 carcass 几何塞进 hardware 默认分支 |

## 核心身份
单自由度铰链：恰好一个 grounded/fixed half 加一个 moving half，二者只由**一个** revolute joint 相连，轴穿过共同的 knuckle/barrel/journal 销线，moving half 绕销线摆动约 0–π。与 serial_elbow_arm（两个串联 revolute）、与 louvered_shutter（多叶共轴 multiplicity）、与 prismatic/滑动类（移动副）划清边界：本类永远 exactly one revolute、exactly two 运动体（独立 pin 可作为第三个 fixed part）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_single_revolute_hinge_a3053de9d063498e8c5154dd589362e0` | `data/records/rec_single_revolute_hinge_a3053de9d063498e8c5154dd589362e0/revisions/rev_000001/model.py:L20-L105` | primitive Box+Cylinder 交错 knuckle leaf-pair：`_knuckle_length`/`_knuckle_centers`/`_add_leaf_visuals` helper、左右 leaf 与 `(0,0,1)` revolute |
| S2 | `rec_single_revolute_hinge_d6f0182b00fa47568edfd64f65ed616e` | `data/records/rec_single_revolute_hinge_d6f0182b00fa47568edfd64f65ed616e/revisions/rev_000001/model.py:L16-L233` | cadquery hollow-tube knuckle leaf-pair：`_tube_z`/`_leaf_plate`/`_grounded_knuckles`/`_carried_knuckles`/`_pin_core_and_caps`/washers/counterbore，grounded+carried 两 part |
| S3 | `rec_single_revolute_hinge_d4bb37b28179466396216af38e3a323f` | `data/records/rec_single_revolute_hinge_d4bb37b28179466396216af38e3a323f/revisions/rev_000001/model.py:L21-L160` | bracket+gusset 支座承载顶/底两 knuckle，moving leaf 只带单 `moving_knuckle`，`_make_side_gusset` 与 lug helper |
| S4 | `rec_single_revolute_hinge_01de33e852e744a8a80ca92868c063cd` | `data/records/rec_single_revolute_hinge_01de33e852e744a8a80ca92868c063cd/revisions/rev_000001/model.py:L19-L140` | clevis 两 cheek 捕获单 moving plate：`ClevisBracketGeometry` SDK helper、`_hinge_barrel`、pin caps、`(1,0,0)` 销轴 |
| S5 | `rec_single_revolute_hinge_0e1fe00c532a44cdb34cd2bb93d33fd2` | `data/records/rec_single_revolute_hinge_0e1fe00c532a44cdb34cd2bb93d33fd2/revisions/rev_000001/model.py:L20-L215` | fork-and-tab：`_circle_profile`/`_tab_profile`/`_extrude_yz_profile_along_x` 把 YZ 轮廓沿 X 销轴挤出，双 cheek + rear bridge + through-pin |
| S6 | `rec_single_revolute_hinge_2ffbf43a26474507a8c1c531850b90f6` | `data/records/rec_single_revolute_hinge_2ffbf43a26474507a8c1c531850b90f6/revisions/rev_000001/model.py:L22-L140` | trunnion-tab：grounded support cheek 带短 journal+retaining head，moving tab 只是带 eye 的 blade，`(0,-1,0)` 销轴 |
| S7 | `rec_single_revolute_hinge_0be604c5e1064ff7bbf5bd2e81b06b8c` | `data/records/rec_single_revolute_hinge_0be604c5e1064ff7bbf5bd2e81b06b8c/revisions/rev_000001/model.py:L22-L158` | pedestal/foot 落地块承载 fixed knuckle + 整根 hinge pin，moving door_plate 带 hollow `moving_knuckle`，`Inertial.from_geometry` |
| S8 | `rec_single_revolute_hinge_1704bfa0c9ca4ddab81ec04749f0b9ea` | `data/records/rec_single_revolute_hinge_1704bfa0c9ca4ddab81ec04749f0b9ea/revisions/rev_000001/model.py:L23-L144` | boxed-cover bracket：thin 安装片 + 上下两 end-knuckle + through-pin，moving cover 带 panel+flange+中间 hollow knuckle，`(0,-1,0)` |
| S9 | `rec_single_revolute_hinge_b5434123bf5b4928bab1160c34ea453e` | `data/records/rec_single_revolute_hinge_b5434123bf5b4928bab1160c34ea453e/revisions/rev_000001/model.py:L19-L218` | 独立 pin part 形态：3 part（left_leaf/right_leaf/`hinge_pin`），`_pin_shape`+`FIXED` pin、3+2 web/knuckle 交错、`(0,1,0)` |
| S10 | `rec_single_revolute_hinge_f024d2a10e03485caf0815f548fad29d` | `data/records/rec_single_revolute_hinge_f024d2a10e03485caf0815f548fad29d/revisions/rev_000001/model.py:L18-L187` | 三段 knuckle-stack（grounded 上下两段 + carried 中段）+ 独立 `_pin_shape` FIXED part，`_knuckle_segment` 半空间裁剪 |
| S11 | `rec_single_revolute_hinge_c2ca41d0df374d298b4e0e89f07cb611` | `data/records/rec_single_revolute_hinge_c2ca41d0df374d298b4e0e89f07cb611/revisions/rev_000001/model.py:L62-L186` | 5-knuckle broad equipment-door：`_segment_center`/`_leaf_hinge_body(side,(0,2,4))/(1,3)` 参数化交错 + barrel collar/spacer 细节，独立 barrel part |
| S12 | `rec_single_revolute_hinge_0001` | `data/records/rec_single_revolute_hinge_0001/revisions/rev_000001/model.py:L22-L188` | object-mounted family：cabinet carcass body + door panel + pull handle，`body_to_door` `(0,0,1)`，`AssetContext`+cadquery shell+`Inertial` |
| S13 | `rec_single_revolute_hinge_0002` | `data/records/rec_single_revolute_hinge_0002/revisions/rev_000001/model.py:L100-L189` | object-mounted family：garden gate frame+post（含 pintle/strap/keeper hardware）+ braced gate leaf，单 hinge 轴 `(0,0,1)` |
| S14 | `rec_single_revolute_hinge_ab94a17090224fbdbcfd00e1a0bd0646` | `data/records/rec_single_revolute_hinge_ab94a17090224fbdbcfd00e1a0bd0646/revisions/rev_000001/model.py:L60-L188` | block-and-leaf：grounded block support（带 barrel relief + 内嵌 pin/knuckle）+ rectangular moving leaf plate，确认 bracket-block 家族 |

## 槽位 + 候选模块表

### Slot A：fixed_half（grounded/固定半，root part）
铰链的接地/固定侧，承载销线一侧的 knuckle/cheek/journal，并提供安装到墙/门框/设备的几何。是 root part。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `leaf_with_knuckles` | S1 / S2 / S11 | a3053de…:L56-L88 / d6f0182b…:L128-L155 / c2ca41d…:L75-L135 | ✓ | 矩形 leaf plate + 与对侧交错的若干 knuckle 段（primitive 或 cadquery hollow tube），最经典 hinge half |
| `bracket_support` | S3 / S8 / S14 | d4bb37b…:L46-L117 / 1704bfa…:L52-L107 / ab94a17…:L65-L116 | — | L 形/带 gusset 的支座或安装片，承载顶+底两 knuckle 或 barrel relief，单侧承力 |
| `clevis_fork` | S4 / S5 | 01de33…:L75-L98（ClevisBracketGeometry）/ 0e1fe…:L107-L160 | — | 双 cheek 叉形支座，cheek 间留 gap 捕获对侧单 tab/plate，含 through-pin + caps |
| `trunnion_cheek` | S6 | 2ffbf43a…:L43-L123 | — | 单 cheek + 短 journal/trunnion 凸台 + retaining head，悬臂支撑对侧 eye（仅 1 源，见说明） |
| `host_carcass` | S12 / S13 | 0001…:L46-L112 / 0002…:L113-L153 | — | object-mounted：宿主柜体/门框（cabinet body、gate post+pintle hardware），gated `host_family=object` |

说明：`trunnion_cheek` 仅 1 个 5 星直接源（2ffbf43a），保留为候选是因为它与 `bracket_support`/`clevis_fork` 在拓扑上明确不同（单 cheek 悬臂 journal vs 双 cheek/双 knuckle）。若 gate 收紧到“每槽 ≥2 源”，可将其折叠进 `bracket_support` 的一个 `cheek_count=1` 子样式。anchor 选 `leaf_with_knuckles`（占 5 星多数）。

### Slot B：moving_half（运动半，child part）
绕销线摆动的活动侧，结构必须与 Slot A 的 hinge-line 互补（leaf↔leaf、fork↔tab、bracket↔cover、host↔door）。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `opposing_leaf` | S1 / S2 / S11 | a3053de…:L56-L88 / d6f0182b…:L157-L184 / c2ca41d…:L175-L185 | ✓ | 与 fixed leaf 镜像的 leaf plate + 互补 knuckle 段（如 fixed (0,2,4) → moving (1,3)） |
| `single_tab_blade` | S5 / S6 | 0e1fe…:L181-L205 / 2ffbf43a…:L80-L130 | — | 单一 tab/blade，根部带 eye/barrel，整片插入 fork gap 或套在 trunnion 上 |
| `cover_panel` | S3 / S8 / S14 | d4bb37b…:L119-L143 / 1704bfa…:L109-L132 / ab94a17…:L117-L188 | — | 较大的 cover/door 面板 + 根部 hollow knuckle/root block，bracket-cover 形态 |
| `host_door` | S12 / S13 | 0001…:L114-L121 / 0002…:L155-L189 | — | object-mounted door/gate leaf（cabinet door+handle、braced gate frame），gated `host_family=object` |

### Slot C：hinge_line（销线机构 / pin 处理，multiplicity 元素）
销线上的 knuckle 互锁方式与 pin 表达；决定 part 数（是否独立 pin part）与 knuckle 段数。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `interleaved_knuckles_pin_in_leaf` | S1 / S2 | a3053de…:L69-L103 / d6f0182b…:L141-L294 | ✓ | 交错 knuckle，pin 表达为 fixed half 内部的 `pin_core`/cylinder（visual），仅 2 part |
| `separate_pin_part` | S9 / S10 | b5434123…:L190-L216 / f024d2a…:L122-L186 | — | pin 是独立 part，用 `ArticulationType.FIXED` 固定到 fixed half，3 part，pin 贯穿全 stack |
| `barrel_with_collars` | S11 | c2ca41d…:L137-L173 | — | 独立 barrel part = pin + 段间 spacer collar + 两端 head，5-knuckle 重型门铰（见说明） |
| `single_journal_or_bore` | S4 / S6 | 01de33…:L93-L108 / 2ffbf43a…:L113-L123 | — | 无交错 stack：clevis 单 through-bore + caps，或 trunnion 单 journal stub，moving 侧单 eye 套入 |

说明：`barrel_with_collars` 仅 1 个直接 5 星源（c2ca41d），但与 `separate_pin_part`（光 pin）/`interleaved_knuckles_pin_in_leaf`（pin 嵌 leaf）拓扑不同（pin + collar + head 组合体）。保留以覆盖重型门铰细节；如收紧可并入 `separate_pin_part` 的 `pin_detail=collared` 子样式。Slot C 与 Slot A/B 必须相容（约束见拓扑审计）。

## 槽位图（slot graph）
pattern: **mixed**（parallel_children + multiplicity）

```
                      [Slot C: hinge_line]  ← 销线机构（可选独立 pin part）
                              │ 共享销线 origin/axis
                              │
         (revolute, exactly 1)│
[Slot A: fixed_half] ─────────●───────── [Slot B: moving_half]
   (root / grounded)      pin axis          (child, swings 0..~π)
   ↑ 接地 / mount             X | Y | Z
```

- Slot A 与 Slot B 是 revolute 的 parent/child，结构互补（parallel_children）。
- Slot C 是叠加在销线上的 multiplicity 元素：要么 pin 内嵌于 Slot A（2 part），要么作为独立 fixed part（3 part）。
- pin 轴是派生 enum（见参数），不单列槽位。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `fixed_half` (`grounded_leaf`/`bracket`/`fixed_support`/`support_cheek`/`pedestal`/`cabinet_body`) | 接地/固定半，root，承载销线一侧 knuckle/cheek/journal + 安装几何 | `fixed_style`, `leaf_width`, `leaf_height`, `plate_thickness`, `mount_hole_count` | S1/S2/S3/S4/S5/S6/S7/S8/S11/S12/S13/S14 |
| `moving_half` (`carried_leaf`/`moving_leaf`/`moving_plate`/`tab`/`cover`/`door`) | 运动半，child，绕销线摆动 | `moving_style`, `moving_len`, `moving_width` | S1/S2/S3/S5/S6/S8/S11/S12/S13/S14 |
| `hinge_pin` (optional) | 独立销轴 part（含 head/collar），`FIXED` 到 fixed_half | `pin_radius`, `pin_is_separate_part`, `pin_detail` | S9/S10/S11 |
| `knuckle_segments` | fixed/moving 各自的 barrel/knuckle 段（part 内 visual，非独立 part） | `knuckle_count`, `knuckle_outer_radius`, `knuckle_gap`, `pin_bore_radius` | S1/S2/S11 |
| `hinge_hardware_detail` (optional) | pin head/cap、spacer collar、bronze washer、counterbore ring、gusset、handle 等 fixed 细节 | `detail_level`, `has_washers`, `has_gusset` | S2/S3/S4/S11/S12 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `hinge_revolute` | revolute | Slot A `fixed_half` | Slot B `moving_half` | `(0,0,1)` / `(0,-1,0)` / `(0,1,0)` / `(1,0,0)` | `[0.0, ~1.35..1.85]` 典型（重型对开 `[-3.0, 0.0]`） | 唯一主关节，轴穿过共同销线 origin | S1/S4/S6/S7/S8/S9/S11/S12/S13 |
| `pin_fixed` | fixed | Slot A `fixed_half` | Slot C `hinge_pin` | n/a | n/a | 仅 `pin_is_separate_part=True` 时存在，把独立 pin 钉死在 fixed half | S9/S10 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `host_family` | enum | `hardware` / `object` | `hardware` | `object` gate 启用 carcass+door（S12/S13），否则两 hinge half | S1/S12/S13 |
| `fixed_style` | enum | `leaf_with_knuckles` / `bracket_support` / `clevis_fork` / `trunnion_cheek` / `host_carcass` | `leaf_with_knuckles` | 决定 Slot A 拓扑及与 Slot B/C 的相容集 | S1/S3/S4/S6/S12 |
| `moving_style` | enum | `opposing_leaf` / `single_tab_blade` / `cover_panel` / `host_door` | `opposing_leaf` | 必须与 `fixed_style` 互补 | S1/S5/S8/S12 |
| `hinge_line_style` | enum | `interleaved_knuckles_pin_in_leaf` / `separate_pin_part` / `barrel_with_collars` / `single_journal_or_bore` | `interleaved_knuckles_pin_in_leaf` | 决定是否有独立 pin part 与 `pin_fixed` joint | S1/S9/S11/S4 |
| `pin_axis` | enum | `z=(0,0,1)` / `neg_y=(0,-1,0)` / `pos_y=(0,1,0)` / `x=(1,0,0)` | `z` | revolute.axis；与销线方向一致 | S1/S4/S6/S9 |
| `knuckle_count` | int | `randint(2, 7)`（总段数，闭区间随机采样） | sampled（leaf 偏 5、stack 偏 3、bracket 偏 2，但允许全区间） | 互补拆分：`fixed_segments = ceil(N/2)`、`moving_segments = floor(N/2)`，沿销轴交错咬合（fixed 占偶数位、moving 占奇数位） | S1/S11/cbf8cbf3(=7) |
| `leaf_height` (`hinge_height`) | float | `0.09 - 0.235` | sampled | knuckle stack 总长由此减端余量派生 | S1/S2/S9/S11 |
| `leaf_width` | float | `0.036 - 0.105` | sampled | plate 横向尺寸 | S1/S2/S11 |
| `plate_thickness` | float | `0.0018 - 0.012` | sampled | leaf/plate 厚度 | S8/S11/S3 |
| `knuckle_outer_radius` | float | `0.0042 - 0.018` | sampled | `> pin_bore_radius > pin_radius` | S8/S1/S2 |
| `pin_radius` | float | `0.00235 - 0.008` | derived | `< pin_bore_radius` 留间隙 | S8/S2/S9 |
| `hinge_lower` | float | `-3.0` 或 `0.0` | `0.0` | 对开重型可负向 | S9 |
| `hinge_upper` | float | `1.35 - 1.85`（重型 `0.0`） | `1.8` | moving half 摆角 | S2/S7/S8 |
| `pin_is_separate_part` | bool | `true` / `false` | `false` | `true` ⇔ `hinge_line_style∈{separate_pin_part, barrel_with_collars}` | S9/S10/S11 |
| `detail_level` | enum | `plain` / `standard` / `rich` | `standard` | head/collar/washer/counterbore/gusset 数量 | S2/S11/S4 |

## 拓扑多样性审计
- per-slot candidate_count：

| slot | candidate_count |
|---|---|
| Slot A `fixed_half` | 5 |
| Slot B `moving_half` | 4 |
| Slot C `hinge_line` | 4 |

- total_combinations（笛卡尔积，未加相容约束）= 5 × 4 × 4 = **80**。
- pin_axis（4）× knuckle_count（总段数 2–7 随机采样，互补拆分给 fixed/moving）作为参数进一步扩展每个拓扑的可见变体，但不计入“拓扑”计数（属 scale/枚举层）。

相容矩阵（合法配对，防止非法笛卡尔积）：
| fixed_style | 合法 moving_style | 合法 hinge_line_style |
|---|---|---|
| `leaf_with_knuckles` | `opposing_leaf` | `interleaved_knuckles_pin_in_leaf` / `separate_pin_part` / `barrel_with_collars` |
| `bracket_support` | `cover_panel` / `opposing_leaf` | `interleaved_knuckles_pin_in_leaf` / `separate_pin_part` |
| `clevis_fork` | `single_tab_blade` | `single_journal_or_bore` / `separate_pin_part` |
| `trunnion_cheek` | `single_tab_blade` | `single_journal_or_bore` |
| `host_carcass` | `host_door` | `interleaved_knuckles_pin_in_leaf` / `single_journal_or_bore` |

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 恰好一个 `fixed_half` + 一个 `moving_half`，由 exactly one REVOLUTE 相连 |
| revolute count | `len([a for a in articulations if a.type==REVOLUTE]) == 1` |
| part count | 2 part（pin 内嵌）或 3 part（独立 pin，含 1 个 FIXED `pin_fixed`）；object family ≤3 |
| axis sanity | `axis ∈ {(0,0,1),(0,-1,0),(0,1,0),(1,0,0)}`，且与销线几何方向一致 |
| motion range | `lower==0.0 且 1.2<=upper<=2.0`，或重型对开 `lower<=-2.8 且 -0.05<=upper<=0.05` |
| hinge-line origin | revolute.origin 落在共同销线中心，且贴近 fixed/moving knuckle 几何（fail_if_articulation_origin_far_from_geometry tol≈0.02） |
| knuckle interlock | fixed 与 moving 的 knuckle 段沿销轴交错/共享 footprint（`expect_overlap axes=销轴`），或 fork/trunnion 单点捕获（`expect_within`） |
| pin captured | pin（内嵌或独立）coaxial 穿过 moving 侧 bore（`expect_within`/`allow_overlap` press-fit） |
| compatibility | `fixed_style`/`moving_style`/`hinge_line_style` 满足相容矩阵；`pin_is_separate_part` 与 style 一致 |
| grounding & swing | fixed_half 接地/可固定；扫 0→upper 时 moving_half 摆出且 `fail_if_parts_overlap` 在 lower/upper 通过 |
| no floating | leaf/knuckle/pin/cover/door/hardware 全部 attached 或 FIXED，无悬空装饰 |

## Reject cases
- 两个静态半，没有 revolute joint，或有 ≥2 个 revolute（那是 elbow/multi-hinge，不是本类）。
- revolute origin/axis 不在共同销线上，moving half 绕错误中心摆动。
- knuckle 段不交错、不共享销轴 footprint（两 leaf 各自独立，pin 没穿过对侧 bore）。
- 独立 pin part 没有 `FIXED` 到 fixed half（pin 漂浮），或 pin 比 bore 还粗导致非 press-fit 穿模未声明。
- `fixed_style`/`moving_style` 不互补（如 clevis_fork 配 opposing_leaf 全 stack）。
- fixed half 不接地 / object carcass 漂浮，或 moving half 摆动 0→upper 时与 fixed half 实体穿模。
- motion range 不真实（upper<1.2 几乎不开，或 >2.0 过冲）且非重型对开特例。
- 把 cabinet/gate 整套 carcass 硬塞进 `host_family=hardware` 默认分支。
- pin head/collar/washer/counterbore/gusset/handle 等细节悬空或不挂在 leaf/bracket/pin 上。

## 与相邻类别的边界
- **serial_elbow_arm / cantilever_articulated_arm**：那些是两个串联 revolute（shoulder+elbow）+ 连杆链；本类 exactly one revolute、无 reach-derived link。
- **louvered_shutter_assembly / 多叶共轴**：多个叶片共轴是 multiplicity（N 个 child）；本类只有一个 moving half。
- **prismatic / telescoping / drawer 滑动类**：移动副（PRISMATIC）；本类是纯 revolute。
- **screwin_light_bulb / coaxial_rotary_stack**：连续旋转或螺旋；本类是有限 0..~π 摆角的开合铰链。
- **同类内 hardware vs object**：hardware = 单独的铰链五金（两 hinge half）；object = 宿主物件（cabinet/gate）通过单铰链开合，用 `host_family` gate，不混入默认。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；读 14/55 个 5 星 + grep 全量；mixed pattern（parallel_children fixed↔moving + multiplicity hinge_line/独立 pin）；trunnion_cheek 与 barrel_with_collars 各仅 1 直接源已注明折叠备选；待人工审核 |
