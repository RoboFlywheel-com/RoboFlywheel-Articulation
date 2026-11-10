# Modular Spec — parabolic_dish_on_azimuth_elevation_mount

## 元信息
| 项 | 值 |
|---|---|
| slug | `parabolic_dish_on_azimuth_elevation_mount` |
| template path | `agent/templates/parabolic_dish_on_azimuth_elevation_mount.py` |
| test path (optional) | `tests/agent/test_parabolic_dish_on_azimuth_elevation_mount_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：主体是 `root_support --azimuth(Z)--> azimuth_stage --elevation(horizontal)--> reflector_assembly` 的串联两关节链；可选的 auxiliary_mechanism 作为 **parallel optional child** 挂在 reflector（rear cover / instrument hatch）或 root/azimuth（transport leg / side crank）上；feed 支撑与 rear rib 是 reflector 内部的 module-local multiplicity。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 38 |
| read_count | 38 |
| read_scope | all 5-star samples in this category（`model.py` 全量精读 + `prompt` 标识；6 个 anchor 主代理直读，其余 32 个并行通读，未抽样） |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构族分布（38 个样本）：

| 轴 | 观察到的真实结构变体 | 代表样本 |
|---|---|---|
| root support | pedestal_column / heavy_slab_base / roof_mount / tripod / wall_mast / mobile_skid / lattice_tower(observatory) | 7c7f54, a10cd, 3915, f7afff, a59149, 7ba40, 77d410 |
| azimuth stage | dual_yoke_turntable / compact_fork_collar / mast_clamp_fork / tripod_head / instrument_yoke | d8ba65, 11d0, a59149, f7afff, 7f851 |
| azimuth joint | CONTINUOUS 或 REVOLUTE[-π,π]，axis (0,0,1) | 二者各约半数 |
| elevation joint | REVOLUTE，水平 axis（多数 (0,-1,0)，部分 (1,0,0)/(0,1,0)），range≈[-0.45,1.57] | 全部 |
| reflector shell primitive | LatheGeometry.from_shell_profiles / 自定义 MeshGeometry 抛物面 / mesh_from_cadquery | 7c7f54, 0d48, 18ef |
| feed support | single_boom(1) / dual_strut(2) / tripod_feed(3) / quad_strut(4,quadrupod) / horn_only(0) | a59149, 0112, a10cd, 7c7f54, 1135 |
| back frame | simple_spine / ribbed / truss / instrument_box / covered | 11d0, 0112, d8ba65, 49566, a10cd |
| auxiliary | none / instrument_hatch / rear_cover / side_crank·lock_knob / transport_leg(fold-down) | 多数 none；49566, a10cd, 121f, 424fe |

## 核心身份

`parabolic_dish_on_azimuth_elevation_mount` 的不变身份：**一个可跟踪方向的抛物面天线 —— 一个固定 root（pedestal/slab/roof/tripod/wall-mast/skid）支撑一个绕竖直 Z 轴调方位角的 azimuth stage（turntable + yoke/fork），再经一个水平轴 REVOLUTE elevation hinge 支撑凹面 parabolic reflector assembly；reflector 必须有凹面反射面 + rim + feed horn/boom（焦点馈源）+ rear back-frame 的天线 identity。** 最小合法体 = root + azimuth(Z) + elevation(horizontal) + 带 feed/back-frame 的凹面 dish；两级运动（方位 + 俯仰）缺一不可。

默认成熟域：地面/屋顶/墙面/三脚架/车载固定式卫星通信与雷达/射电天线（VSAT、卫通、跟踪雷达、射电望远镜、车载/便携天线）。auxiliary（rear cover / instrument hatch / side crank / lock knob / transport leg）是可选辅助，不替代主两关节。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：root_support（固定根，决定接地/安装平面与方位轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pedestal_column | rec_…_7c7f540f3bc54fa29b7d54bb85b26ce1 | L122-L140 | eligible if compatible | ground_pad + 圆柱 column + 顶部 bearing ring，地面立柱 |
| heavy_slab_base | rec_…_a10cd68df45446dea72f5ab62d12b71f | L91-L114 | eligible if compatible | ballast_block slab + upper_plinth + fixed azimuth bearing，重载基座 |
| roof_mount | rec_…_aedd5aed8708470a8566356d353c2520 | L104-L133 | eligible if compatible | flashing 屋顶板 + 低 bearing ring，低矮屋顶安装 |
| tripod_base | rec_…_f7afffc3fbc14af38b62a74b9a4bb6d4 | L104-L159 | eligible if compatible | 中心 hub + 3 leg(wire/spline) + spreader + 顶 plate，便携三脚架 |
| wall_mast_mount | rec_…_a591490345ea40fe9c2ee315910e1855 | L92-L134 | eligible if compatible | wall_plate + upper/lower arm + brace + mast_socket + pipe mast，墙挂管柱 |
| mobile_skid_base | rec_…_7ba40683e2a848c0991bb9294e60f9e8 | L118-L171 | eligible if compatible | 双 skid + crossbar + center_spine + leg_hinge_bridge，车载/便携底盘（带 transport leg 铰座） |

注：observatory lattice_tower（rec_…_77d410b1 L104-L197：foundation slab + 4 tower legs + bearing ring）是 heavy_slab_base 的放大 truss 变体，初版作为 heavy_slab_base 的 module-local scale 变体记录，不单列 candidate（见模板实现备注）。

### Slot B：azimuth_stage（方位转台 + elevation 支撑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| dual_yoke_turntable | rec_…_d8ba65c1b7a74a15b9b6c5b2342312ee | L188-L235 | eligible if compatible | turntable disk + 两 yoke 臂 + pivot pad + rear gusset，左右 yoke cheek 抱 elevation bearing |
| compact_fork_collar | rec_…_11d08956138d4c589cb527b07caeb7b0 | L142-L172 | eligible if compatible | 旋转 collar + left/right 短 fork arm，低矮紧凑叉 |
| mast_clamp_fork | rec_…_a591490345ea40fe9c2ee315910e1855 | L136-L177 | eligible if compatible | mast 上环形 clamp collar(lathe tube) + web + cheek + capture plate，抱管旋转头 |
| tripod_head | rec_…_f7afffc3fbc14af38b62a74b9a4bb6d4 | L161-L220 | eligible if compatible | 紧凑 turntable head + dual yoke arm + trunnion，便携头 |
| instrument_yoke | rec_…_7f8512f01f3c4faf96101c5b596b1cf0 | L111-L182 | eligible if compatible | turntable + center_mast + shoulder block + sweep-profile 弯臂 + 两 bearing |

### Slot C：reflector_feed_assembly（凹面反射体 + feed 支撑 + back frame，elevation 子件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_boom_spine | rec_…_a591490345ea40fe9c2ee315910e1855 | L179-L244（shell L46-L69，feed_arm L76-L90） | eligible if compatible | lathe/mesh 凹壳 + rim + 单 feed boom(tube) + 简单 rear hub/spine + feed horn |
| dual_strut_ribbed | rec_…_0112ba3226e1487192d3e73272a2db3d | L364-L434（shell L60-L89，feed boom+braces L154-L195，ribs L137-L150） | eligible if compatible | 凹壳 + 2 feed strut/brace + rear ring + N 条 rear rib(tube) |
| tripod_feed_ribbed | rec_…_a10cd68df45446dea72f5ab62d12b71f | L171-L310（shell L63-L72，3 feed strut L286-L293，rear frame L202-L237） | eligible if compatible | 凹壳 + 3 feed strut(120°) + ribbed/torus rear ring + rear frame skeleton |
| quad_strut_truss | rec_…_7c7f540f3bc54fa29b7d54bb85b26ce1 | L184-L237（lathe L185-L194，truss L54-L73，quad feed L76-L109） | eligible if compatible | 凹壳 + 4-strut quadrupod feed + rear truss(nodes+tube) + rim torus |
| horn_only_minimal | rec_…_113598a9eab74e75807c3aaae00aa262 | L159-L198（mesh shell L21-L65） | eligible if compatible | 凹壳 + rim + rear spine/hub，仅 feed horn 无 boom（survey/简化天线） |

reflector shell primitive 三族（module-local variant，gated by sampling，禁止降级成 Box/Cylinder）：

| primitive 族 | 来源 | 采用判据 |
|---|---|---|
| `lathe_shell_profiles` | rec_…_7c7f540f L185-L194；rec_…_a10cd L63-L72；rec_…_0004 L120-L133 | 默认；LatheGeometry.from_shell_profiles 内外壳廓 |
| `custom_parabolic_mesh` | rec_…_0d4863f7 L32-L90；rec_…_7c38db97 L26-L74；rec_…_77d410b1 L22-L74 | 手工 MeshGeometry 抛物面(径向×角向 segment) |
| `cadquery_shell` | rec_…_18eff859 L17-L41；rec_…_ff95ab24 `_dish_shell`；rec_…_b46d320f `_dish_shell_geometry` | cadquery 球面/抛物面差集；仅环境可 import cadquery 时启用 |

### Slot D：auxiliary_mechanism（可选副自由度/辅助件，默认 none）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none | — | — | eligible if compatible | 仅 azimuth + elevation 两关节 |
| instrument_hatch | rec_…_49566120c578436cb5061a6f0e715707 | box L368-L384 + hatch L385-L411 + joints L435-L446 | eligible if compatible | dish 后 FIXED instrument_box + 其上 REVOLUTE 翻盖 hatch |
| rear_cover | rec_…_a10cd68df45446dea72f5ab62d12b71f | cover L312-L347 + REVOLUTE L372-L385 | eligible if compatible | dish rear frame 上 REVOLUTE 翻盖电子舱盖（hinge knuckle + leaf + pull） |
| side_crank_or_lock_knob | rec_…_121fa18bce2642609c5eec64bac0fc07 | crank + CONTINUOUS L422-L430 | eligible if compatible | azimuth/elevation head 侧 CONTINUOUS 手摇曲柄/锁紧旋钮（lock_knob 变体 rec_…_f1a5c78b L311） |
| transport_leg | rec_…_7ba40683e2a848c0991bb9294e60f9e8 | leg L293-L319 + REVOLUTE L339-L347 | eligible if compatible | mobile_skid 底盘上 REVOLUTE 折叠 transport leg（hinge barrel + leg tube + foot pad） |

硬约束确认：A=6、B=5、C=5、D=5（含 none）candidate；均有真实 5 星 `model.py:Lx-Ly` 来源；candidate 间为 part tree / joint 拓扑 / primitive / 接口差异，非颜色/尺寸/材质差异。

## 槽位图（slot graph）

pattern: mixed

```
[Slot A root_support] (fixed root; 接地/屋顶/墙面/三脚架/底盘平面)
   │
   ├─[azimuth_yaw; CONTINUOUS 或 REVOLUTE[-π,π]; axis=(0,0,1); turntable<->fixed bearing ring 接触面]
   │      ▼
   │   [Slot B azimuth_stage]
   │      │
   │      └─[elevation_tilt; REVOLUTE; 水平 axis (0,-1,0)/(±1,0,0); yoke/fork bearing<->dish trunnion; range≈[-0.45,1.57]]
   │             ▼
   │          [Slot C reflector_feed_assembly]
   │             │
   │             ├─(feed struts ×N, FIXED 到 dish rim/hub；module-local multiplicity)
   │             ├─(rear ribs ×M, parent visual / 内部 helper)
   │             ├─[Slot D rear_cover; REVOLUTE; cover hinge<->dish rear frame]   (optional)
   │             └─[Slot D instrument_hatch; FIXED box + REVOLUTE hatch]          (optional)
   │
   ├─[Slot D side_crank/lock_knob; CONTINUOUS; horizontal; 挂 azimuth/elevation head]  (optional)
   └─[Slot D transport_leg; REVOLUTE fold; leg hinge<->skid hinge bridge]              (optional, root=mobile_skid)
```

接口点位与跨 slot joint：

- **A→B（azimuth_yaw，恒存在）**：CONTINUOUS 或 REVOLUTE[-π,π]，axis=(0,0,1)。接口=B 的 turntable/collar 底面与 A 的 fixed bearing ring/turntable 座 `expect_gap`(轴向贴合，max_gap≈0.0015)；origin 落 A 顶部 bearing 面中心。`azimuth_joint_type` 由采样决定（两类样本各半）。
- **B→C（elevation_tilt，恒存在）**：REVOLUTE，水平 axis（默认 (0,-1,0)，少量 (1,0,0)/(0,1,0)）。接口=B 的 yoke/fork cheek bearing 与 C 的 dish trunnion/axle，captured 关系（`expect_gap` max_penetration≈0.004，element-scoped allow_overlap）；origin 落两 cheek bearing 连线（elevation hinge line）。range reviewer-gated（见参数表）。
- **C 内部 feed**：feed boom/strut 从 dish rim/hub 指向焦点 feed horn；strut 数=feed_strut_count（multiplicity），FIXED 或 parent visual。
- **C→D rear_cover / instrument_hatch**：REVOLUTE，hinge 落 dish rear frame / instrument_box edge；cover/hatch 在 closed pose 贴合后框，不得遮挡前反射面。
- **A/B→D side_crank/lock_knob**：CONTINUOUS，水平轴，knob/crank 套在 azimuth neck 或 elevation trunnion 侧。
- **A→D transport_leg**：REVOLUTE 折叠，hinge 落 mobile_skid 的 leg_hinge_bridge；仅 root=mobile_skid_base。

互斥/可选/派生：

- `transport_leg` 仅当 root=mobile_skid_base。
- `tripod_head` 仅当 root=tripod_base；`mast_clamp_fork` 仅当 root ∈ {wall_mast_mount, pedestal_column(细管型)}。
- `roof_mount` ⇒ azimuth ∈ {compact_fork_collar, dual_yoke_turntable(低)}（低矮）。
- `rear_cover` / `instrument_hatch` ⇒ Slot C ∈ {dual_strut_ribbed, tripod_feed_ribbed, quad_strut_truss}（需有 rear frame 可挂）；horn_only_minimal/single_boom_spine 默认不挂 rear cover。
- `cadquery_shell` primitive 仅在 cadquery 可用时进入采样。

## 每槽位 Module Emits / Interfaces

### Slot A / module pedestal_column
| emits | 描述 | 来源 |
|---|---|---|
| parts | ground_pad(Cyl) + column(Cyl) + bearing_ring(Cyl)（fixed root 单 part） | rec_…_7c7f540f / L122-L140 |
| upstream interface | root（无 parent） | 同上 |
| downstream interface | 顶部 bearing_ring 上面供 azimuth turntable 座；azimuth origin 落此面中心 | rec_…_7c7f540f / L239-L252 |

### Slot A / module heavy_slab_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | ballast_block(Box) + upper_plinth(Box) + stationary azimuth bearing(Cyl) | rec_…_a10cd / L91-L114 |
| downstream interface | plinth 顶 bearing 面供 turntable | rec_…_a10cd / L349-L357 |

### Slot A / module roof_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | flashing 屋顶板 + 低 bearing ring + standoff | rec_…_aedd5aed / L104-L133 |
| downstream interface | 低 bearing ring 供 compact fork | rec_…_aedd5aed / L261 |

### Slot A / module tripod_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | center hub + 3 leg(wire/spline) + 3 brace + 3 foot + 顶 plate | rec_…_f7afffc3 / L104-L159 |
| internal helpers | leg/brace 用 wire_from_points / tube_from_spline_points | rec_…_f7afffc3 / L129-L154 |
| downstream interface | 顶 plate bearing 供 tripod_head | rec_…_f7afffc3 / L285 |

### Slot A / module wall_mast_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | wall_plate + upper/lower arm + brace + mast_socket + mast_pipe(Cyl) + cap | rec_…_a591490 / L92-L134 |
| downstream interface | mast_pipe 外柱面供 mast_clamp collar 抱箍 | rec_…_a591490 / L246-L254 |

### Slot A / module mobile_skid_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2 skid + 2 crossbar + center_spine + azimuth bearing + leg_hinge_bridge + hinge lugs | rec_…_7ba40683 / L118-L171 |
| downstream interface | center 上 azimuth bearing 供 pedestal/turntable；leg_hinge_bridge 供 transport_leg | rec_…_7ba40683 / L321-L347 |

### Slot B / module dual_yoke_turntable
| emits | 描述 | 来源 |
|---|---|---|
| parts | turntable disk + central hub + 两 yoke 臂 + pivot pad + rear gusset | rec_…_d8ba65 / L188-L235 |
| upstream interface | turntable 底座 azimuth bearing（CONTINUOUS/REVOLUTE Z child） | rec_…_d8ba65 / L310 |
| downstream interface | 两 yoke cheek bearing 抱 dish trunnion（elevation hinge line） | rec_…_d8ba65 / L324 |

### Slot B / module compact_fork_collar
| emits | 描述 | 来源 |
|---|---|---|
| parts | 旋转 collar + bearing drum + left/right 短 fork arm + pivot panel | rec_…_11d0 / L142-L172 |
| downstream interface | fork arm 端 bearing 供 dish_yoke trunnion | rec_…_11d0 / L238-L251 |

### Slot B / module mast_clamp_fork
| emits | 描述 | 来源 |
|---|---|---|
| parts | mast_collar(lathe tube) + pad + upper/lower web + inner cheek + capture plate | rec_…_a591490 / L136-L177 |
| upstream interface | collar 抱 mast_pipe（azimuth Z 绕 mast 轴） | rec_…_a591490 / L246-L254 |
| downstream interface | cheek/capture plate 抱 dish trunnion journal | rec_…_a591490 / L255-L268 |

### Slot B / module tripod_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | turntable head + dual yoke arm + trunnion seat | rec_…_f7afffc3 / L161-L220 |
| downstream interface | yoke arm trunnion shaft 供 dish | rec_…_f7afffc3 / L299 |

### Slot B / module instrument_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | turntable + center_mast + shoulder collar/block + sweep-profile 弯臂 + 两 bearing | rec_…_7f8512 / L111-L182 |
| internal helpers | 臂用 sweep_profile_along_spline(rounded_rect_profile) | rec_…_7f8512 / L143-L165 |
| downstream interface | 两臂端 bearing 供 dish trunnion | rec_…_7f8512 / L338-L351 |

### Slot C / module single_boom_spine
| emits | 描述 | 来源 |
|---|---|---|
| parts | trunnion journal/flange + rear hub + reflector_shell + rim(torus) + 单 feed_arm(tube) + feed_block + feed_horn | rec_…_a591490 / L179-L244 |
| upstream interface | trunnion journal/flange 入 yoke/fork cheek bearing（elevation child） | rec_…_a591490 / L180-L197 |
| internal | feed_arm tube_from_spline_points 指向焦点 | rec_…_a591490 / L76-L90 |

### Slot C / module dual_strut_ribbed
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell + rear ring/hub + N rear rib(tube) + feed boom + 2 feed brace + feed horn | rec_…_0112 / L364-L434 |
| internal | shell L60-L89；ribs L137-L150；feed boom+braces L154-L195 | rec_…_0112 |

### Slot C / module tripod_feed_ribbed
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell + rear frame skeleton + torus 加强环 + 3 feed strut(120°) + feed hub + horn | rec_…_a10cd / L171-L310 |
| internal | shell L63-L72；rear frame L202-L237；3 strut L286-L293 | rec_…_a10cd |
| downstream interface | rear frame 供 rear_cover/instrument_hatch hinge | rec_…_a10cd / L372-L385 |

### Slot C / module quad_strut_truss
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell + rear truss(nodes+tube) + rim torus + 4-strut quadrupod + receiver + horn | rec_…_7c7f540f / L184-L237 |
| internal helpers | `_tube_between` / `_build_truss_geometry` / `_build_feed_geometry` | rec_…_7c7f540f / L23-L109 |

### Slot C / module horn_only_minimal
| emits | 描述 | 来源 |
|---|---|---|
| parts | reflector_shell + rim + rear spine/hub + feed horn（无 boom） | rec_…_113598a9 / L159-L198 |
| internal | 自定义 MeshGeometry 凹壳 L21-L65 | rec_…_113598a9 |

### Slot D / module instrument_hatch
| emits | 描述 | 来源 |
|---|---|---|
| parts | instrument_box(FIXED 到 dish) + hatch(REVOLUTE) | rec_…_49566120 / L368-L411 |
| internal joints | box FIXED L435-L441；hatch REVOLUTE axis(0,0,-1) L442-L446 | rec_…_49566120 |

### Slot D / module rear_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | cover leaf + 3 hinge knuckle + pull | rec_…_a10cd / L312-L347 |
| internal joints | REVOLUTE axis(0,1,0) range[0,1.35] L372-L385 | rec_…_a10cd |

### Slot D / module side_crank_or_lock_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | crank/knob shaft + handle/grip | rec_…_121f / crank；rec_…_f1a5c78b / lock_knob |
| internal joints | CONTINUOUS horizontal L422-L430（121f）/ L311（f1a5c） | rec_…_121f / rec_…_f1a5c78b |

### Slot D / module transport_leg
| emits | 描述 | 来源 |
|---|---|---|
| parts | hinge barrel + leg tube(wire) + foot pad | rec_…_7ba40683 / L293-L319 |
| internal joints | REVOLUTE axis(0,1,0) range[0,1.35] L339-L347 | rec_…_7ba40683 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| root_choice (A) | enum | pedestal_column / heavy_slab_base / roof_mount / tripod_base / wall_mast_mount / mobile_skid_base | sampled | deterministic procedural sampler | Slot A table |
| azimuth_choice (B) | enum | dual_yoke_turntable / compact_fork_collar / mast_clamp_fork / tripod_head / instrument_yoke | sampled | 受 root_choice gating | Slot B table |
| reflector_choice (C) | enum | single_boom_spine / dual_strut_ribbed / tripod_feed_ribbed / quad_strut_truss / horn_only_minimal | sampled | feed_strut_count 派生 | Slot C table |
| shell_primitive | enum | lathe_shell_profiles / custom_parabolic_mesh / cadquery_shell | lathe_shell_profiles | gated（cadquery 可用性） | shell primitive 三族 |
| auxiliary_choice (D) | enum | none / instrument_hatch / rear_cover / side_crank_or_lock_knob / transport_leg | sampled | 受 root/reflector gating | Slot D table |
| azimuth_joint_type | enum | continuous / revolute_limited | sampled | 两类样本各半 | rec_…_0004 / rec_…_d8ba65 |
| elevation_axis | enum | (0,-1,0) / (1,0,0) / (0,1,0) | (0,-1,0) | 由 azimuth_stage cheek 朝向派生 | 全样本 |
| feed_strut_count | int (multiplicity) | 0/1/2/3/4 | 由 reflector_choice 派生 | horn_only=0,single=1,dual=2,tripod=3,quad=4 | Slot C table |
| rear_rib_count | int (multiplicity) | 4/6/8/16 | 6 | module-local，back-frame 密度 | rec_…_0112 L137-L150 / rec_…_77d410 L313-L318 |
| dish_radius | float | [0.30, 1.05] | 0.62 | yoke span / feed 焦距 / cheek clearance 派生 | rec_…_0112 / rec_…_7c7f54 |
| dish_depth | float | [0.10, 0.45] | 0.24 | 抛物面深度，焦点 offset 派生 | rec_…_5c50 / rec_…_77d410 |
| azimuth_height | float | [0.35, 1.45] | 0.78 | root→elevation hinge 高度 | rec_…_7c38db / rec_…_a10cd |
| elevation_range | float pair | lower∈[-0.45,0], upper∈[0.80,1.57] | [-0.20,1.20] | reviewer-gated；俯仰行程 | 全样本 |
| support_width_scale | float | [0.9, 1.15] | 1.0 | root/azimuth 平面安全缩放 | resolve_config clamp |
| leg_spread_scale | float | [0.9, 1.15] | 1.0 | tripod/skid 张开度 | resolve_config clamp |
| feed_boom_len_scale | float | [0.9, 1.12] | 1.0 | feed 焦距微调，clamp 使 horn 落焦点附近 | resolve_config clamp |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette 与 module-local variant；未实现拓扑不进 enum。

## Multiplicity / Copy Logic

本类别含若干 module-local 复制逻辑：

**(1) feed_strut_count（核心，由 Slot C 派生）**
- count_param：`feed_strut_count`
- N_range：{0,1,2,3,4}
- sampling domain：由 reflector_choice 派生 —— horn_only_minimal=0、single_boom_spine=1、dual_strut_ribbed=2、tripod_feed_ribbed=3、quad_strut_truss=4。
- copied object：feed strut（tube_from_spline_points / wire_from_points），从 rim/hub 收敛到焦点 feed horn
- naming：`feed_strut_0..N-1`
- placement：tripod/quad 等角(120°/90°)绕轴；dual 镜像；single 单 boom
- joint policy：feed 静态支撑（FIXED 或 parent visual），无独立 joint；horn 落焦点
- source/gating：rec_…_a10cd L286-L293（3）；rec_…_7c7f540f L76-L109（4）；rec_…_0112 L154-L195（2）

**(2) rear_rib_count（back-frame 密度）**
- count_param：`rear_rib_count`，N_range={4,6,8,16}，module-local
- copied object：rear rib(tube) / 加强 torus 环
- placement：绕 dish 背面等角辐射
- joint policy：parent visual，无 joint
- source/gating：rec_…_0112 L137-L150（8）；rec_…_77d410 L313-L318（16）；rec_…_c601 L181-L202（4）

**(3) back_ring_count（后框加强环）**
- count_param：`back_ring_count`，N_range={0,1,2,3}，module-local 采样
- copied object：concentric rear stiffener torus（TorusGeometry），dish 背面同心环，横跨 radial ribs 受支撑
- placement：dish 背平面（x-z），半径 R*0.28..R*0.52 等距分布
- joint policy：parent visual，无 joint
- source/gating：rec_…_7f8512f0 L202-L209（outer+inner 2 环）；rec_…_77d410b1 L302-L312（3 stiffener rings）

**(4) support_leg_count（三脚架/塔腿）**
- count_param：`support_leg_count`，N_range={3,4}，仅 root=tripod_base 采样（其余 root 固定）
- copied object：splayed leg + rubber foot + lower foot tie（等角）
- placement：等角 tau*i/n 绕中心柱张开
- joint policy：root 静态支撑，无 joint
- source/gating：rec_…_f7afffc3 / rec_…_3ebbc287（3 腿三脚架）；rec_…_77d410b1 L132-L143（4 tower legs，4 腿塔）

**(5) yoke_cheek_count / skid 数 — 固定，不采样**
- yoke cheek 固定 2，skid 固定 2；为 module-local fixed helper loop，不暴露 `*_count`。

**(4) auxiliary 数量**
- auxiliary 为 0 或 1 个（none / 单个 hatch·cover·crank·leg），非可变 N。

## 拓扑多样性审计

总组合数（合法化前）：A(6) × B(5) × C(5) × D(5) = 750；再 × azimuth_joint_type(2)。compatibility matrix 裁剪后估算：

- pedestal/heavy/roof × {dual_yoke,compact_fork,instrument_yoke} × C(5) × {none,hatch,cover,crank} ≈ 3×3×5×4 = 180
- tripod_base × {tripod_head,compact_fork} × C(5) × {none,crank} ≈ 2×5×2 = 20
- wall_mast × {mast_clamp_fork,compact_fork} × C(5) × {none,cover} ≈ 2×5×2 = 20
- mobile_skid × {compact_fork,dual_yoke} × C(5) × {none,transport_leg,crank} ≈ 2×5×3 = 30
- 合计合法组合 **≥ 230**，再叠加 azimuth_joint_type、feed_strut multiplicity、shell primitive 三族 → 远超门槛。

理由：仅 A×B×C 在合法子集内已远超 10 个 distinct 拓扑等价类（不同 root part tree / 不同 azimuth fork-vs-yoke / 不同 feed strut 数与 back-frame / 带或不带 aux 第三关节 transport_leg·hatch·cover·crank / continuous vs revolute azimuth）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed deterministic procedural sampling —— 先 rng 选 root_choice → 经 compatibility matrix 得 azimuth/aux 合法子集再选 → 选 reflector_choice（派生 feed_strut_count）→ 选 shell_primitive（gated）→ 采样 azimuth_joint_type / elevation_axis / range / 连续 scale / rear_rib_count。`seed=0` 不特殊。所有非法组合由 compatibility matrix + resolve_config clamp 拦截。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 root×azimuth×reflector 家族至少 1 例，重点：elevation hinge 落 cheek bearing 线、dish 不漂浮、feed horn 落焦点、aux closed pose 不遮挡反射面、transport_leg 折叠合理、azimuth continuous/revolute 语义。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别合法组合估计 ≥230，预期可达。
regression overrides：初版默认 none；若 sweep 暴露特定失败组合再以稀疏、显式 + 失败回归理由加入，不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入 `dish_radius [0.30,1.05]`、`dish_depth [0.10,0.45]`、`azimuth_height [0.35,1.45]`、`support_width_scale [0.9,1.15]`、`leg_spread_scale [0.9,1.15]`、`feed_boom_len_scale [0.9,1.12]`、`elevation_range`（reviewer-gated）。全部在 resolve_config clamp / 派生，受 elevation hinge line、cheek bearing 捕获、feed 焦点、接地面、azimuth bearing 贴合约束；不改变 slot/module 选择、feed_strut_count、aux 存在性等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | root→azimuth→reflector→aux 顺序选择 + 每步 compatibility gate；weighted（pedestal/heavy 家族权重高，wall/skid/tripod 低频但保留） | slot_choices_for_seed matches build choices |
| compatibility matrix | transport_leg↔mobile_skid、tripod_head↔tripod_base、mast_clamp↔wall_mast/pipe、roof↔低 azimuth、rear_cover/hatch↔有 rear frame 的 reflector、cadquery 可用性 | no floating（dish/aux 不漂浮）、collision（cheek vs dish、cover closed）、axis（azimuth Z、elevation horizontal）、max multiplicity（strut≤4、rib≤16）、bulky module、optional child（aux 缺省安全） |
| controlled local variation | dish_radius/depth/azimuth_height/support_width/leg_spread/feed_boom_len/elevation_range，全 clamp | 比例变化不破坏 hinge line、cheek bearing 捕获、feed 焦点、接地、joint origin、类别 identity |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/captured-pin/axis/range） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A root_support | 6 | yes | yes | |
| B azimuth_stage | 5 | yes | yes | |
| C reflector_feed_assembly | 5 | yes | yes | × shell primitive 三族 |
| D auxiliary_mechanism | 5 | yes | yes | 含 none |

兼容矩阵（合法 / 互斥 / fallback）：

- `transport_leg` ⇒ root=mobile_skid_base（否则无 leg_hinge_bridge）。其余 root 不出 transport_leg。
- `tripod_head` ⇒ root=tripod_base；`mast_clamp_fork` ⇒ root ∈ {wall_mast_mount, pedestal_column(管型)}。
- `roof_mount` ⇒ azimuth ∈ {compact_fork_collar, dual_yoke_turntable(低 profile)}；不配 instrument_yoke（过高）。
- `dual_yoke_turntable` / `compact_fork_collar` / `instrument_yoke` ⇒ root ∈ {pedestal_column, heavy_slab_base, mobile_skid_base, tripod_base(compact)}。
- `rear_cover` / `instrument_hatch` ⇒ reflector ∈ {dual_strut_ribbed, tripod_feed_ribbed, quad_strut_truss}（需 rear frame/box）；horn_only_minimal/single_boom_spine ⇒ aux ∈ {none, side_crank_or_lock_knob, transport_leg(若 skid)}。
- `side_crank_or_lock_knob` ⇒ 任意（挂 azimuth/elevation head）。
- `cadquery_shell` ⇒ 仅 cadquery 可 import；否则 fallback 到 lathe_shell_profiles。
- elevation_axis 必须水平且与 azimuth_stage cheek 朝向一致；azimuth 必须 Z。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D 四元组 + azimuth_joint_type + feed_strut_count 派生）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（transport_leg↔skid、tripod_head↔tripod、mast_clamp↔mast、roof↔低 azimuth、cover/hatch↔rear frame、cadquery 可用性）
- optional regression overrides are sparse and justified（初版 none）
- controlled local scale params (dish_radius/depth/azimuth_height/support_width/leg_spread/feed_boom_len/elevation_range) clamped；不破坏 elevation hinge line、cheek bearing 捕获、feed 焦点、接地面、joint origin、类别 multiplicity
- critical InterfaceSpec / MatingContract points exist：turntable<->fixed bearing ring（azimuth）、yoke/fork cheek bearing<->dish trunnion（elevation captured pin）、feed strut<->rim/horn、cover/hatch hinge<->rear frame
- key joints have expected type/axis/range：azimuth CONTINUOUS/REVOLUTE axis(0,0,1)；elevation REVOLUTE 水平 axis range≈[-0.45,1.57]；aux hatch/cover REVOLUTE、crank/knob CONTINUOUS、transport_leg REVOLUTE
- reflector geometry：凹面 parabolic shell + rim + feed horn/boom + rear frame；primitive 不得从 Lathe/mesh/cadquery 降级成 Box/Cylinder
- copied objects follow naming/placement policy（feed_strut_i 等角；rear_rib_i 辐射）
- elevation hinge origin 落 yoke/fork cheek bearing 连线（非 dish 任意中心）；feed horn 落抛物面焦点

## Reject cases

- 静态 dish 缺 azimuth 或 elevation 任一关节（退化成固定天线 / 单 DOF）。
- elevation 轴竖直 或 azimuth 轴水平（轴向错误）。
- dish 脱离 yoke/fork cheek，trunnion 未被 cheek bearing 捕获 → dish 漂浮。
- feed horn/boom 脱离 dish 或不指向焦点；feed strut 数与 reflector_choice 不一致。
- reflector 用 Box/Cylinder 拼凑代替凹面 shell（违反 primitive 保真）。
- rear_cover/instrument_hatch 装在前反射面或遮挡 dish identity（应在 rear frame/box）。
- transport_leg 出现在非 mobile_skid root（无铰座 → 漂浮）；tripod_head 配非 tripod root。
- 仅在 rest pose 验 elevation —— 改 elevation axis 符号/range 必须 pose 到 upper/lower 实测 cheek-trunnion 捕获与 dish AABB（[[project_sweep_only_rest_pose]]）。
- aux 第二/第三自由度几何不连贯（cover 铰不接触 rear frame、crank 悬空）却靠 sweep pass 蒙混 —— viewer 目检，不连贯就退回 none（[[feedback_gated_aux_geometry_coherence]]）。
- 把 feed/rib 的 mesh/lathe profile 沿轴摆放当居中导致几何多伸（[[feedback_mesh_profile_origin_pitfall]]）。

## 与相邻类别的边界

- 不该混入：pan-tilt 相机云台 —— 无凹面抛物反射体与 feed 馈源，末端是相机不是 dish。
- 不该混入：`astronomical_telescope_on_tripod` —— 末端是镜筒/光学管，非反射天线 feed；俯仰/方位虽类似但 identity 不同。
- 不该混入：平板/相控阵雷达（flat panel / phased array）—— reflector 必须凹面抛物，非平板。
- 不该混入：固定不动的装饰卫星天线 —— 必须有 azimuth + elevation 两级 articulation。
- 不该混入：`parabolic_dish` 之外的一般 `turntable` / `rotary_table` —— 必须有 dish 反射体 + feed + 俯仰，不仅是转台。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | A | pedestal_column | rec_…_7c7f540f3bc54fa29b7d54bb85b26ce1 | L122-L140 | 立柱 root + bearing 接口 |
| S-A2 | A | heavy_slab_base | rec_…_a10cd68df45446dea72f5ab62d12b71f | L91-L114 | 重载 slab + plinth |
| S-A3 | A | roof_mount | rec_…_aedd5aed8708470a8566356d353c2520 | L104-L133 | 屋顶板 + 低 bearing |
| S-A4 | A | tripod_base | rec_…_f7afffc3fbc14af38b62a74b9a4bb6d4 | L104-L159 | 三脚架 leg/brace(wire) |
| S-A5 | A | wall_mast_mount | rec_…_a591490345ea40fe9c2ee315910e1855 | L92-L134 | 墙挂 + pipe mast |
| S-A6 | A | mobile_skid_base | rec_…_7ba40683e2a848c0991bb9294e60f9e8 | L118-L171 | 车载 skid + leg 铰座 |
| S-B1 | B | dual_yoke_turntable | rec_…_d8ba65c1b7a74a15b9b6c5b2342312ee | L188-L235 | 双 yoke 转台 |
| S-B2 | B | compact_fork_collar | rec_…_11d08956138d4c589cb527b07caeb7b0 | L142-L172 | 紧凑 collar fork |
| S-B3 | B | mast_clamp_fork | rec_…_a591490345ea40fe9c2ee315910e1855 | L136-L177 | 抱管 clamp 头 |
| S-B4 | B | tripod_head | rec_…_f7afffc3fbc14af38b62a74b9a4bb6d4 | L161-L220 | 便携头 |
| S-B5 | B | instrument_yoke | rec_…_7f8512f01f3c4faf96101c5b596b1cf0 | L111-L182 | sweep-profile 弯臂 yoke |
| S-C1 | C | single_boom_spine | rec_…_a591490345ea40fe9c2ee315910e1855 | L179-L244 (shell L46-69, boom L76-90) | 单 boom 简单 spine |
| S-C2 | C | dual_strut_ribbed | rec_…_0112ba3226e1487192d3e73272a2db3d | L364-L434 (shell L60-89, feed L154-195) | 双 strut + ribbed |
| S-C3 | C | tripod_feed_ribbed | rec_…_a10cd68df45446dea72f5ab62d12b71f | L171-L310 (shell L63-72, 3 strut L286-293) | 3 strut + rear frame |
| S-C4 | C | quad_strut_truss | rec_…_7c7f540f3bc54fa29b7d54bb85b26ce1 | L184-L237 (lathe L185-194, truss L54-73, quad L76-109) | quadrupod + truss |
| S-C5 | C | horn_only_minimal | rec_…_113598a9eab74e75807c3aaae00aa262 | L159-L198 (mesh shell L21-65) | 仅 horn 无 boom |
| S-Csh1 | C | lathe_shell primitive | rec_…_0004 | L120-L133 | LatheGeometry.from_shell_profiles |
| S-Csh2 | C | custom mesh primitive | rec_…_0d4863f7 | L32-L90 | 手工 MeshGeometry 抛物面 |
| S-Csh3 | C | cadquery primitive | rec_…_18eff859d8854213a75f4d5e0743a692 | L17-L41 | mesh_from_cadquery 球面差集 |
| S-D1 | D | instrument_hatch | rec_…_49566120c578436cb5061a6f0e715707 | L368-L411 + L435-446 | FIXED box + REVOLUTE hatch |
| S-D2 | D | rear_cover | rec_…_a10cd68df45446dea72f5ab62d12b71f | L312-L347 + L372-385 | REVOLUTE 电子舱盖 |
| S-D3 | D | side_crank_or_lock_knob | rec_…_121fa18bce2642609c5eec64bac0fc07 | crank L422-L430 | CONTINUOUS 曲柄/旋钮 |
| S-D4 | D | transport_leg | rec_…_7ba40683e2a848c0991bb9294e60f9e8 | L293-L319 + L339-347 | REVOLUTE 折叠腿 |

## 模板实现备注（可选）

- 共享 helper：`_dish_shell_mesh`（lathe/mesh/cadquery 三 primitive 分支，禁降级）、`_feed_struts(n)`（等角复制 tube_from_spline_points）、`_rear_ribs(m)`、`_tube_between` / `_beam_between`（杆件）、`_yoke_cheek`（trunnion bearing 捕获）、tripod/skid leg(wire_from_points)。
- 重点 InterfaceSpec / MatingContract：azimuth turntable↔fixed bearing ring 轴向贴合（expect_gap≈0.0015）；yoke/fork cheek bearing↔dish trunnion 为 captured pin（element-scoped allow_overlap，参 rec_…_ff95 L241-243、rec_…_a591490 trunnion 捕获测试）；cover/hatch hinge barrel↔rear frame mount captured；feed strut↔rim/horn 接触。
- captured-pin overlap：trunnion-in-cheek、hinge barrel-in-knuckle、mast collar-around-pipe、crank shaft-in-bush 处需 element-scoped allow_overlap，仅对真实意图穿插声明。
- 暂不进入 seed domain（待实现后再开）：cadquery_shell 仅在环境可 import cadquery 时启用；observatory lattice_tower 作为 heavy_slab_base 的 large-scale 变体二期；多 feed/sub-reflector（如 77d410 subreflector_disk）作为 quad_strut_truss 的 module-local 细节，不单列。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （重写自 v1-era spec；全 38 个 5 星样本重读，新增 mobile_skid+transport_leg、feed_strut multiplicity、三 shell primitive 族；待人工审核） |
