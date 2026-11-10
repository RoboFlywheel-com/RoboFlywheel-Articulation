# Modular Spec — studio_spotlight_on_yoke

## 元信息
| 项 | 值 |
|---|---|
| slug | `studio_spotlight_on_yoke` |
| template path | `agent/templates/studio_spotlight_on_yoke.py` |
| test path (optional) | `tests/agent/test_studio_spotlight_on_yoke_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：主链是 `root_support --pan(Z)--> pan_yoke --tilt(horizontal)--> spotlight_head` 的串联两关节链；root_support 内部可含 module-local PRISMATIC（telescoping mast）或 REVOLUTE（tripod 腿展开）；auxiliary_mechanism 作为 **parallel optional child** 挂在 spotlight_head（barndoor / front filter / gel frame / rear lens cover / service hatch / rear handle / focus knob）或 pan_yoke（tilt lock knobs）上。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 46 |
| read_count | 46 |
| read_scope | all 5-star samples in this category（`model.py` 全量精读 + `prompt.txt` / `record.json` / `revision.json` / category metadata；46 个分 4 批 Explore 并行通读，未抽样） |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构族分布（46 个样本）：

| 轴 | 观察到的真实结构变体 | 样本计数 |
|---|---|---|
| root support | floor_pedestal_base / low_floor_disk_base / tripod_post / wheeled_dolly / telescoping_floor_stand / telescoping_tripod_stand | 21 / 5 / 5 / 4 / 5 / 6 |
| pan joint | REVOLUTE[-π,π] / CONTINUOUS / REVOLUTE[-2.2,2.2] / FIXED（仅 tilt 单 DOF 极少数） | 大致各半，FIXED 仅 3-4 例 |
| tilt joint | REVOLUTE，水平 axis 多为 (0,-1,0)，部分 (1,0,0) / (0,1,0)；range≈[-0.95,1.40] | 全部 |
| yoke shape | two_arm_box_yoke / mesh_trunnion_yoke / swept_arm_yoke / side_pivot_yoke | 28 / 9 / 3 / 6 |
| spotlight head | primitive_box_cylinder_can / lathe_shell_can / cadquery_shell_can / fresnel_lens_can | 14 / 17 / 9 / 6 |
| auxiliary | none / tilt_lock_knobs / focus_or_mode_knob / barndoor_four_leaf / front_filter_or_gel_frame / service_hatch_or_lens_cover / foldable_carry_handle | 17 / 6 / 6 / 5 / 5 / 4 / 3 |
| multiplicity | tripod_legs ∈ {3} / caster_wheels ∈ {3,4} / barndoor_leaves ∈ {4} / accessory_clips ∈ {2} | — |

## 核心身份

`studio_spotlight_on_yoke` 的不变身份：**一个可定向的影视/舞台/工作室聚光灯 —— 一个静态接地或可移动的 root_support（floor pedestal / low disk / tripod / wheeled dolly，可含 telescoping prismatic mast）顶部承载一个绕竖直 Z 轴方位旋转（pan/swivel）的 yoke stage（two-arm U yoke / mesh trunnion yoke / 单 side pivot yoke），yoke 抱住一只 barrel/can 形 spotlight head，head 绕水平 trunnion 轴俯仰（tilt/aim）；head 必须有朝光束方向的 translucent front lens + bezel + rear cap 的灯具 identity。**

最小合法体 = root + pan(Z) + tilt(horizontal) + 带 front lens/bezel 的圆柱/lathe/cadquery can；两级运动（pan + tilt）缺一不可（极少 FIXED pan 工业变体不进入采样）。

默认成熟域：影视/舞台/摄影棚/广播/photo session 的固定或便携 spotlight（fresnel head / PAR can / 工业 can / 户外 weatherproof can），spotlight 可装 barndoor / gel frame / front filter / lens cover / rear service hatch / focus knob / tilt lock knobs / 折叠 carry handle 等附件。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：root_support（固定/移动根，决定接地平面、pan 轴位置、mast/telescope/leg 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| floor_pedestal_base | rec_studio_spotlight_on_yoke_0001 | L49-L96 | eligible if compatible | 矩形/重力 box 底盘 + 中央立柱（短 post 或 tall pole），顶 pan bearing seat；最常见 |
| low_floor_disk_base | rec_studio_spotlight_on_yoke_0005 | L97-L148 | eligible if compatible | 低矮圆柱/圆盘底（floor base，0.15-0.22 半径），yoke 直接坐落 pan bearing 上，常 CONTINUOUS pan |
| tripod_post_base | rec_studio_spotlight_on_yoke_1761967de3ef43ad8d0ac952de205378 | L53-L165 | eligible if compatible | crown hub + 3 折叠 leg (spline/tube) + 中心 mast pole；leg hinge REVOLUTE，mast 固定或加 PRISMATIC |
| wheeled_dolly_base | rec_studio_spotlight_on_yoke_aa36438f54c446b0b15452bf78f1ef12 | L134-L189 | eligible if compatible | 4 caster wheels + box 底盘 + 短中心 post；wheel CONTINUOUS spin |
| telescoping_floor_stand | rec_studio_spotlight_on_yoke_b9ab25fbcdaa40229d411825763757bd | L100-L135 | eligible if compatible | 底座 sleeve + 内伸 prismatic post（高度可调），PRISMATIC sleeve→column 0..0.32 |
| telescoping_tripod_stand | rec_studio_spotlight_on_yoke_afb8b91e473b4db28cb0a8fd8dbfb469 | L133-L157 | eligible if compatible | 3 折叠 leg + 中心 column PRISMATIC（camera/photo 三脚架），column_slide 0..0.45 |

注：square_base（rec_…_11075c2c L32-L55）作为 floor_pedestal_base 的 module-local 截面变体记录，不单列 candidate。foldable_mast（rec_…_36d06ee L130-L154）极罕见（1/46），作为 telescoping_floor_stand 的 module-local 替代行为暂不进入主采样（reviewer 可启用）。

### Slot B：pan_yoke（pan 转台 + tilt 支撑，U 型或单 arm trunnion）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| two_arm_box_yoke | rec_studio_spotlight_on_yoke_0001 | L98-L142 | eligible if compatible | turntable disk + 两 Box arm + cylinder trunnion bearing；纯 primitive，最常见 |
| mesh_trunnion_yoke | rec_studio_spotlight_on_yoke_a7d172f7cf79434685dcca702d4364db | L46-L59 | eligible if compatible | 单 `TrunnionYokeGeometry` mesh 一体 yoke（lathe/cadquery 衍生），整块装在 pan post 顶 |
| swept_arm_yoke | rec_studio_spotlight_on_yoke_0003 | L219-L277 | eligible if compatible | turntable + `sweep_profile_along_spline` 弯曲 yoke arms（圆角矩形截面），带 trunnion bosses |
| side_pivot_yoke | rec_studio_spotlight_on_yoke_6ba32e9f51ee462582286df6b19cf3ab | L134-L208 | eligible if compatible | 单 side arm（offset C-bracket）抱 head 一侧，tilt pivot 偏置，常配 lock knobs（rec_d3ef30 / rec_d7dcae 同形） |

### Slot C：spotlight_head（barrel/can 灯头：lens + bezel + rear cap + trunnion，绕水平轴 tilt）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| primitive_box_cylinder_can | rec_studio_spotlight_on_yoke_0001 | L144-L222 | eligible if compatible | 纯 Box + Cylinder 灯壳 + 前 lens(半透明 Cylinder) + bezel ring + rear cap + 2 trunnion stubs |
| lathe_shell_can | rec_studio_spotlight_on_yoke_0002 | L284-L372 | eligible if compatible | `LatheGeometry.from_shell_profiles` 中空灯壳 + lens + bezel + rear cap + cooling fins，复杂 profile 灯具感强 |
| cadquery_shell_can | rec_studio_spotlight_on_yoke_06058b5ff50d45db8b83e7ff183ff9ce | L246-L300 | eligible if compatible | `mesh_from_cadquery` 灯壳（圆筒/锥体差集），lens + bezel；环境需 cadquery |
| fresnel_lens_can | rec_studio_spotlight_on_yoke_193640fbb692448ab2c13cf08ae04fad | L136-L270 | eligible if compatible | LatheGeometry 壳 + `BezelGeometry` 前 bezel + 多 `TorusGeometry` fresnel 同心环 lens（菲涅尔聚光灯 identity），rec_6eef18/8550 同型 |

注：primitive 选择与 head shape 选择耦合 —— cadquery 仅在 cadquery 可 import 时启用；不可降级成 Box only（lens/bezel 必须保留）。

### Slot D：auxiliary_mechanism（可选 0/1 个副自由度或装饰附件，默认 none）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none | — | — | eligible if compatible | 仅 pan + tilt 两关节，无第三 DOF |
| tilt_lock_knobs | rec_studio_spotlight_on_yoke_a7d172f7cf79434685dcca702d4364db | L104-L151 | eligible if compatible | 一对 lobed KnobGeometry 锁紧旋钮挂 yoke 两侧 trunnion，CONTINUOUS spin（同型 rec_6ba32 / rec_78d9f7 / rec_193640 / rec_6d63 / rec_36d06e） |
| focus_or_mode_knob | rec_studio_spotlight_on_yoke_eef41631f0d34697a9316ac0b700be93 | L312-L341 | eligible if compatible | 单 CONTINUOUS lobed knob 挂 can 后端或侧面（focus knob / mode dial / rear knob）；rec_06058 L246-L300 mode_dial / rec_aa36438 L470-L481 rear_knob 同型 |
| barndoor_four_leaf | rec_studio_spotlight_on_yoke_aa36438f54c446b0b15452bf78f1ef12 | L353-L437 | eligible if compatible | can 前 FIXED 4-leaf barndoor frame + 4 REVOLUTE 叶（top/bottom/left/right），每叶 axis 在 leaf 根边（rec_6eef18 / rec_8550 / rec_d3ef30 / rec_eef416 同型） |
| front_filter_or_gel_frame | rec_studio_spotlight_on_yoke_d1205dce2bf343bab3d9758393ccfcee | L229-L275 | eligible if compatible | can 前 REVOLUTE 翻盖 filter holder（hinge 在 can 前缘）；或 PRISMATIC 抽插 gel frame（rec_afb8b9 L271-L332 / rec_d7dcae L324-L363 gel_slide PRISMATIC 0..0.28） |
| service_hatch_or_lens_cover | rec_studio_spotlight_on_yoke_78d9f7c8b02d4aa48ed97c4ef453400a | L111-L267 | eligible if compatible | can 后端 REVOLUTE service hatch（gasket + quarter_turn_latch） / can 前 REVOLUTE flip lens cover（rec_85881 cover_hinge） / can 后/旁 REVOLUTE service flap（rec_987798 L166-L225） |
| foldable_carry_handle | rec_studio_spotlight_on_yoke_f20d5deae1534c4894cc84479eef4363 | L415-L454 | eligible if compatible | can 顶 REVOLUTE 折叠 carry handle（pivot eyes + tube grip + axle），rec_35f03b L307-L383 head_to_handle 同型 |

硬约束确认：A=6、B=4、C=4、D=7（含 none）candidate；均有真实 5 星 `model.py:Lx-Ly` 来源；candidate 间为 part tree / joint 拓扑 / primitive / 接口差异，非颜色/尺寸/材质差异。

## 槽位图（slot graph）

pattern: mixed

```
[Slot A root_support]（floor / low_disk / tripod / wheeled / telescoping_floor / telescoping_tripod）
   │
   ├─(tripod_post / telescoping_tripod 内部) leg_hinge_0..2 REVOLUTE crown→leg axis=(0,±1,0) range≈[-0.45, 1.05]    (module-local multiplicity)
   ├─(telescoping_floor / telescoping_tripod 内部) mast_slide PRISMATIC sleeve→column axis=(0,0,1) range≈[0, 0.45]    (module-local)
   ├─(wheeled_dolly 内部) wheel_spin_0..N CONTINUOUS base→caster axis=(0,0,1)                                          (module-local multiplicity)
   │
   ├─[pan_yaw; REVOLUTE[-π,π] 或 CONTINUOUS 或 REVOLUTE[-2.8,2.8]; axis=(0,0,1); turntable<->fixed bearing 接触面]
   │      ▼
   │   [Slot B pan_yoke]（two_arm_box / mesh_trunnion / swept_arm / side_pivot）
   │      │
   │      └─[tilt_aim; REVOLUTE; 水平 axis (0,-1,0) 主，少量 (1,0,0)/(0,1,0); yoke trunnion bearing<->head trunnion shaft; range≈[-0.95, 1.40]]
   │             ▼
   │          [Slot C spotlight_head]（primitive_box_cylinder / lathe_shell / cadquery_shell / fresnel_lens）
   │             │
   │             ├─[Slot D barndoor_four_leaf; FIXED frame + 4× REVOLUTE leaf; axis 在 leaf 根边; range≈[-0.61, 1.22]]    (optional)
   │             ├─[Slot D front_filter_or_gel_frame; REVOLUTE 翻盖 0..1.35 或 PRISMATIC 抽插 0..0.28]                     (optional)
   │             ├─[Slot D service_hatch_or_lens_cover; REVOLUTE 0..1.45]                                                 (optional)
   │             ├─[Slot D focus_or_mode_knob; CONTINUOUS axis=(0,±1,0)/(0,0,±1) 挂 can 后/侧]                           (optional)
   │             └─[Slot D foldable_carry_handle; REVOLUTE axis=(0,1,0) range≈[-1.0, 0.25] 挂 can 顶]                     (optional)
   │
   └─[Slot D tilt_lock_knobs; 2× CONTINUOUS axis=tilt_line 挂 pan_yoke trunnion 外侧]                                       (optional)
```

接口点位与跨 slot joint：

- **A→B（pan_yaw，恒存在；FIXED 极罕见仅 reviewer-gated）**：REVOLUTE[-π,π] / CONTINUOUS / REVOLUTE[-2.8,2.8]，axis=(0,0,1)。接口=B 的 turntable/pan_disk 底面与 A 顶部 bearing seat/pan_post cap 轴向贴合（`expect_gap` max_gap≈0.0015）；origin 落 A 顶 bearing 面中心。`pan_joint_type` 由采样决定（CONTINUOUS 多见于低 disk/wheeled/telescoping；REVOLUTE 多见于 floor pedestal）。
- **B→C（tilt_aim，恒存在）**：REVOLUTE，水平 axis（默认 (0,-1,0)，部分 (1,0,0)/(0,1,0)）。接口=B 的 yoke arm trunnion bearing 与 C 的 head trunnion shaft/pin captured 关系（element-scoped `allow_overlap`，captured-pin 习语；`expect_gap` max_penetration≈0.004）；origin 落两 trunnion 连线（U yoke）或单 trunnion offset 中心（side_pivot）。range 由 `tilt_lower/tilt_upper` 派生。
- **A 内部 leg_hinge**：仅 root ∈ {tripod_post_base, telescoping_tripod_stand}；3 条 leg 等角 120°，REVOLUTE 展开（轴垂直于 leg 径向），module-local multiplicity。
- **A 内部 mast_slide**：仅 root ∈ {telescoping_floor_stand, telescoping_tripod_stand}；PRISMATIC 沿 Z，origin 在 sleeve 顶；range 0..0.45。
- **A 内部 wheel_spin**：仅 root = wheeled_dolly_base；3 或 4 caster 等角围绕底盘，CONTINUOUS 绕局部 Z 自转，module-local multiplicity。
- **C→D barndoor_four_leaf**：先 FIXED barndoor_frame 到 can 前缘，再 4 个 REVOLUTE leaf hinge 落 frame 各边；4 叶 axis 分别为 (0,±1,0) 或 (0,0,±1) 形成 top/bottom/left/right 对称。
- **C→D front_filter_or_gel_frame**：REVOLUTE 翻盖 → hinge 在 can 前缘上沿；PRISMATIC 抽插 → guide rails 沿 ±Y。
- **C→D service_hatch_or_lens_cover**：REVOLUTE hinge 落 can 后端/侧/前缘；closed pose 贴合 can 表面，不遮挡 lens identity。
- **C→D focus_or_mode_knob**：CONTINUOUS knob shaft 落 can 后端中心或侧面。
- **C→D foldable_carry_handle**：REVOLUTE pivot pair 落 can 顶 hinge eye；fold pose 时贴 can 顶。
- **B→D tilt_lock_knobs**：2 个 CONTINUOUS knob 挂 pan_yoke 外侧 trunnion 螺栓位置（与 tilt 轴共线），仅 pan_yoke ∈ {two_arm_box, mesh_trunnion, side_pivot}（swept_arm 拓扑不预留外侧 boss）。

互斥/可选/派生：

- `tripod_post_base` 和 `telescoping_tripod_stand` 必须含 3 leg_hinge；其余 root 不出 leg_hinge。
- `wheeled_dolly_base` 必须含 3-4 wheel_spin（caster）；其余 root 不出 wheel_spin。
- `telescoping_floor_stand` / `telescoping_tripod_stand` 必须含 mast_slide PRISMATIC；其余 root 不出 mast_slide。
- `tilt_lock_knobs` ⇒ pan_yoke ∈ {two_arm_box, mesh_trunnion, side_pivot}（swept_arm 拓扑无 boss）。
- `barndoor_four_leaf` ⇒ spotlight_head ∈ {lathe_shell_can, fresnel_lens_can, primitive_box_cylinder_can}（cadquery_shell_can 也允许，但要确保前 bezel 平面可承 barndoor frame）。
- `fresnel_lens_can` ⇒ aux ∈ {none, barndoor_four_leaf, focus_or_mode_knob, foldable_carry_handle}（fresnel lens 表面不挂 front_filter / lens_cover）。
- `cadquery_shell_can` ⇒ 仅在 cadquery 可 import 时启用；否则 fallback 到 lathe_shell_can。
- `side_pivot_yoke` ⇒ aux ∈ {none, tilt_lock_knobs, focus_or_mode_knob, foldable_carry_handle}（side_pivot 不预留 barndoor frame 对称，但样本中确有 side_pivot+barndoor 组合 rec_d3ef30，允许但权重低）。
- `wheeled_dolly_base` ⇒ pan_joint ∈ {CONTINUOUS, REVOLUTE[-π,π]}（不限位）；wheeled 平台多自由旋转。
- pan FIXED 极罕见（仅 rec_6d632 / rec_8fe98 / rec_97861e / rec_4efbe4 / rec_a7d172 / rec_bbaef / rec_fa8e36，多为 weatherproof/calibration 工业变体），暂不进入采样，reviewer-gated。

## 每槽位 Module Emits / Interfaces

### Slot A / module floor_pedestal_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_box / base_plate（Box）+ center_post / upright_tube（Cyl, 0.32-1.34m）+ 顶 pan_seat | rec_…_0001 / L49-L96；rec_…_fa8e36 L42-L58 |
| upstream interface | root（无 parent；接地平面 z=0） | 同上 |
| downstream interface | post 顶 bearing seat（半径 0.04-0.10，水平面）供 pan_yoke turntable 座；pan origin 落此面中心 | rec_…_0001 / L98-L103；rec_…_fa8e36 L188-L201 |

### Slot A / module low_floor_disk_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor_base（Cyl, 0.15-0.22 半径，0.04-0.08 高）+ 可选短中柱 | rec_…_0005 / L97-L148；rec_…_d8ff32 L29-L60 |
| downstream interface | disk 顶面供 yoke turntable 直接坐落；常 CONTINUOUS pan | rec_…_0005 / L260-L268 |

### Slot A / module tripod_post_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | crown_hub（Cyl/cadquery）+ 3 leg（tube_from_spline_points / wire）+ 3 rubber_foot + center_mast（Cyl）+ 顶 pan_seat | rec_…_1761967d / L53-L165；rec_…_aac63ac L109-L153 |
| internal joints | leg_hinge_0/1/2 REVOLUTE crown→leg axis=(0,±1,0)（等角 120°）range≈[0, 1.05]（或 [-0.45, 0.65]） | rec_…_1761967d / L226-L256；rec_…_06058b L172-L182 |
| internal multiplicity | tripod_legs N=3（spec 默认固定，不暴露） | 全 tripod 样本 |
| downstream interface | mast 顶 pan_seat 供 pan_yoke turntable | rec_…_1761967d / L296-L303 |

### Slot A / module wheeled_dolly_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_box / fork_bridges + 4 caster_yoke + 4 caster_wheel（TireGeometry）+ 短 center_post | rec_…_aa36438 / L134-L189；rec_…_f20d5d L88-L176 |
| internal joints | wheel_spin_0..3 CONTINUOUS base→wheel axis=(0,0,1)；caster yoke 可固定或可旋（本谱仅 spin 自转） | rec_…_aa36438 / L210-L221；rec_…_eef416 L196-L228 |
| internal multiplicity | caster_wheels N=3 或 4，采样域 {3,4}；module-local | rec_…_f20d5d（3）/ rec_…_aa36438（4） |
| downstream interface | center_post 顶 bearing 供 pan_yoke turntable | rec_…_aa36438 / L246-L259 |

### Slot A / module telescoping_floor_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_box + sleeve_shell（Cyl，外管）+ inner_post（Cyl，内伸）+ guide_shoes（小 Box ×2）+ pan_spigot 顶座 | rec_…_b9ab25 / L100-L135；rec_…_d59260 L68-L155 |
| internal joints | mast_slide PRISMATIC sleeve→inner_post axis=(0,0,1) range≈[0, 0.32-0.45] | rec_…_b9ab25 / L226-L234；rec_…_d59260 L210-L223 |
| downstream interface | inner_post 顶 pan_spigot 供 pan_yoke | rec_…_b9ab25 / L235-L243 |

### Slot A / module telescoping_tripod_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | crown_hub + 3 leg + 中心 sleeve + 中心 column（PRISMATIC，0.45-0.60m）+ 顶 pan_seat | rec_…_afb8b9 / L133-L157；rec_…_d7dcae L121-L203；rec_…_35f03b L27-L262；rec_…_62e4a6 L116-L215；rec_…_06058b L90-L205 |
| internal joints | leg_hinge_0/1/2 REVOLUTE（同 tripod_post_base）+ column_slide PRISMATIC sleeve→column axis=(0,0,1) range≈[0, 0.45] | rec_…_afb8b9 / L297-L305；rec_…_d7dcae L205-L218 |
| internal multiplicity | tripod_legs N=3 | rec_…_afb8b9 / rec_…_d7dcae |
| downstream interface | column 顶 pan_seat 供 pan_yoke | rec_…_afb8b9 / L306-L314 |

### Slot B / module two_arm_box_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | turntable disk（Cyl）+ lower_bridge（Box）+ 2 arm（Box，左右对称）+ 2 trunnion_bearing（Cyl/boss） | rec_…_0001 / L98-L142；rec_…_b3bc02 L70-L141 |
| upstream interface | turntable 底（pan child；轴向贴合 pan bearing） | rec_…_0001 / L257-L268 |
| downstream interface | 2 trunnion bearing（左右对称，连线为 tilt 轴）供 head trunnion 捕获；origin 落两 bearing 中点 | rec_…_0001 / L269-L283；rec_…_b3bc02 L244-L257 |

### Slot B / module mesh_trunnion_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | pan_disk + 单 `TrunnionYokeGeometry` mesh（一体 U 框，含两 trunnion bearing 内孔） | rec_…_a7d172 / L46-L59；rec_…_4efbe4 L139-L223；rec_…_b9ab25 L137-L156 |
| internal helpers | `TrunnionYokeGeometry(...)` 网格化（含 trunnion 孔） | 同上 |
| downstream interface | mesh 两侧内 trunnion 孔轴线即 tilt 轴 | rec_…_a7d172 / L121-L131 |

### Slot B / module swept_arm_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | turntable + lower_bridge + 2 `sweep_profile_along_spline` 弯曲 arm（rounded_rect 截面）+ 2 trunnion boss | rec_…_0003 / L219-L277；rec_…_6d632 L52-L162（cadquery 同构变体） |
| internal helpers | `sweep_profile_along_spline(rounded_rect_profile, spline)` | rec_…_0003 / L222-L240 |
| downstream interface | 2 trunnion boss（沿 arm 端）连线即 tilt 轴 | rec_…_0003 / L274-L283 |

### Slot B / module side_pivot_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | pan_disk + 单 offset side arm（C-bracket，TrunnionYokeGeometry 或 Box）+ 单 trunnion pivot | rec_…_6ba32 / L134-L208；rec_…_d3ef30 L142-L164；rec_…_d7dcae L220-L249；rec_…_6d632 L105-L162 |
| downstream interface | 单 trunnion pivot（offset 单侧）供 head 一侧捕获；tilt 轴穿过此 pivot 与 head 后端 | rec_…_6ba32 / L195-L208 |

### Slot C / module primitive_box_cylinder_can
| emits | 描述 | 来源 |
|---|---|---|
| parts | can_body（Cyl/Box，0.10-0.32m 长，0.03-0.18m 半径）+ front_lens（半透明 Cyl alpha≈0.45）+ bezel ring（Cyl/Torus）+ rear_cap（Cyl/Box）+ 2 trunnion stub（Cyl，左右对称） | rec_…_0001 / L144-L222；rec_…_b3bc02 L143-L228；rec_…_5bcc96 L151-L173 |
| upstream interface | 2 trunnion stub（径向外伸），插入 yoke trunnion bearing（captured pin） | rec_…_0001 / L210-L222；rec_…_b3bc02 L201-L211 |

### Slot C / module lathe_shell_can
| emits | 描述 | 来源 |
|---|---|---|
| parts | `LatheGeometry.from_shell_profiles(...)` 中空灯壳 + front lens + bezel + rear cap + 可选 cooling fins（Torus 环或 module-local 复制） | rec_…_0002 / L284-L372；rec_…_0005 L244-L339；rec_…_11075 L88-L147；rec_…_8550 L273-L337；rec_…_b3bc02 L143-L228 |
| upstream interface | 2 trunnion stub（捕获 yoke bearing） | rec_…_0002 / L356-L372 |

### Slot C / module cadquery_shell_can
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mesh_from_cadquery(Workplane...)` 灯壳（圆筒/圆锥/差集）+ lens + bezel + rear cap + 2 trunnion stub | rec_…_06058 / L246-L300；rec_…_d8ff32 L168-L214；rec_…_85881 L212-L228；rec_…_36d06e L181-L216 |
| upstream interface | 2 trunnion stub 捕获 yoke bearing；shape gated by cadquery import | rec_…_d8ff32 / L207-L214 |

### Slot C / module fresnel_lens_can
| emits | 描述 | 来源 |
|---|---|---|
| parts | LatheGeometry 壳 + `BezelGeometry` 前 bezel + 3-4 `TorusGeometry` 同心 fresnel 环（半透明）+ rear cap + 2 trunnion stub | rec_…_193640 / L136-L270；rec_…_6eef18 L273-L373；rec_…_8550 L273-L337；rec_…_afb8b9 L197-L269（fresnel_lens L204-L215） |
| internal multiplicity | fresnel_ring N=3 或 4，module-local 固定 | rec_…_193640 / rec_…_6eef18 |

### Slot D / module tilt_lock_knobs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2 `KnobGeometry` lobed 旋钮 + 2 friction washer/ring（Torus）挂 pan_yoke 两侧 trunnion 外端 | rec_…_a7d172 / L104-L120；rec_…_6ba32 L213-L283；rec_…_193640 / clamp knobs；rec_…_78d9f7 L150-L180 |
| internal joints | knob_spin_0/1 CONTINUOUS pan_yoke→knob axis 与 tilt 轴共线 | rec_…_a7d172 / L132-L151；rec_…_193640 / clamp_spin_0/1 |
| internal multiplicity | knob N=2 固定，不暴露 | 全部 |

### Slot D / module focus_or_mode_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | 1 `KnobGeometry` lobed/cylindrical knob（focus / mode dial / rear knob）挂 can 后端或侧 | rec_…_eef416 / L312-L341；rec_…_06058 / L246-L300（mode_dial）；rec_…_aa36438 L439-L469；rec_…_62e4a6 L260-L296（mode_dial_cap）；rec_…_6eef18 L273-L373（focus_knob） |
| internal joints | knob_spin CONTINUOUS can→knob axis 横向（多为 ±X/±Y） | rec_…_eef416 / L333-L341；rec_…_aa36438 L470-L481 |

### Slot D / module barndoor_four_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | barndoor_frame（FIXED 到 can 前缘）+ 4 leaf（Box，top/bottom/left/right） | rec_…_aa36438 / L353-L437；rec_…_6eef18 L273-L373；rec_…_8550 L273-L337；rec_…_eef416 L343-L369；rec_…_d3ef30 L279-L438 |
| internal joints | frame FIXED；leaf hinge top REVOLUTE axis=(0,1,0) range≈[-1.22, 0.61]；bottom (0,1,0) [-0.61, 1.22]；side_0 (0,0,1) [-0.61, 1.22]；side_1 (0,0,1) [-1.22, 0.61] | rec_…_aa36438 / L371-L437；rec_…_6eef18 / leaf joints |
| internal multiplicity | leaf N=4 固定 | 全部 5 例 |

### Slot D / module front_filter_or_gel_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | 翻盖变体：filter_holder Box + 2 hinge knuckle + glass pane；抽插变体：gel_frame + 4 guide rail（PRISMATIC 槽） | rec_…_d1205 / L229-L275（filter_hinge REVOLUTE）；rec_…_afb8b9 L271-L332（gel_slide PRISMATIC）；rec_…_d7dcae L324-L363；rec_…_d8ff32 L216-L261 |
| internal joints | filter_hinge REVOLUTE can→filter_holder axis=(0,1,0) range≈[0, 1.35]；或 gel_slide PRISMATIC can→gel_frame axis=(0,1,0) range≈[0, 0.28] | rec_…_d1205 / L266-L274；rec_…_afb8b9 / L324-L332 |

### Slot D / module service_hatch_or_lens_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | 翻盖板（Box / cadquery cover）+ 2 hinge knuckle + 可选 latch + 可选 gasket | rec_…_78d9f7 / L111-L267（rear_hatch + gasket + quarter_turn_latch）；rec_…_85881 L212-L228（cover_hinge）；rec_…_987798 L166-L225（service_flap） |
| internal joints | hatch/cover hinge REVOLUTE can→cover axis 沿 hinge 边 range≈[0, 1.45-1.83] | rec_…_78d9f7 / L210-L267；rec_…_85881 / cover_hinge |

### Slot D / module foldable_carry_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2 pivot eye + handle bar（tube_from_spline_points / Box）+ axle | rec_…_f20d5d / L415-L454；rec_…_35f03b / L307-L383（head_to_handle） |
| internal joints | handle_fold REVOLUTE can→handle axis=(0,1,0) range≈[-1.0, 0.25] | rec_…_f20d5d / L446-L454；rec_…_35f03b / L378-L383 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| root_choice (A) | enum | floor_pedestal_base / low_floor_disk_base / tripod_post_base / wheeled_dolly_base / telescoping_floor_stand / telescoping_tripod_stand | sampled | deterministic procedural sampler | Slot A table |
| yoke_choice (B) | enum | two_arm_box_yoke / mesh_trunnion_yoke / swept_arm_yoke / side_pivot_yoke | sampled | 受 root_choice gating（无强约束，权重微调） | Slot B table |
| head_choice (C) | enum | primitive_box_cylinder_can / lathe_shell_can / cadquery_shell_can / fresnel_lens_can | sampled | gated（cadquery 可用性、fresnel↔aux 互斥） | Slot C table |
| aux_choice (D) | enum | none / tilt_lock_knobs / focus_or_mode_knob / barndoor_four_leaf / front_filter_or_gel_frame / service_hatch_or_lens_cover / foldable_carry_handle | sampled | 受 head/yoke gating | Slot D table |
| pan_joint_type | enum | revolute_limited / continuous / wide_revolute(-2.8..2.8) | sampled | wheeled/low_disk 偏 continuous；floor pedestal 偏 limited | 全样本 |
| tilt_axis | enum | (0,-1,0) / (1,0,0) / (0,1,0) | (0,-1,0) | 由 yoke trunnion 朝向派生 | 全样本 |
| tripod_leg_count | int (module-local multiplicity) | {3} | 3 | 仅 root ∈ tripod_*；spec 内固定 | rec_…_1761967d / rec_…_afb8b9 |
| caster_wheel_count | int (module-local multiplicity) | {3, 4} | 4 | 仅 root = wheeled_dolly_base | rec_…_f20d5d（3）/ rec_…_aa36438（4） |
| barndoor_leaf_count | int (module-local) | {4} | 4 | 仅 aux = barndoor_four_leaf；spec 内固定 | 全 5 例 barndoor 样本 |
| fresnel_ring_count | int (module-local) | {3, 4} | 3 | 仅 head = fresnel_lens_can | rec_…_193640（3）/ rec_…_6eef18（4） |
| tilt_lower | float | [-0.95, -0.20] | -0.45 | tilt 下限 | 全样本 |
| tilt_upper | float | [0.65, 1.40] | 1.05 | tilt 上限（上仰更大） | 全样本 |
| pan_height | float | [0.18, 1.45] | 0.55 | root 顶 pan_seat 距地高度（含 mast slack） | 全样本 |
| post_radius | float | [0.018, 0.090] | 0.038 | 中柱/mast 半径 | 全样本 |
| yoke_span | float | [0.10, 0.42] | 0.20 | 两 yoke arm 中心距 = head 宽度，tilt 轴长度 | 全 U-yoke 样本 |
| pan_stage_height | float | [0.05, 0.32] | 0.14 | turntable 顶到 trunnion 的高度 | 全样本 |
| head_length | float | [0.08, 0.42] | 0.22 | can 长度 | 全样本 |
| head_radius | float | [0.030, 0.18] | 0.085 | can 半径 | 全样本 |
| lens_radius | float | [0.026, 0.16] | 0.075 | 前 lens 半径（略小于 bezel） | 全样本 |
| lens_alpha | float | [0.32, 0.70] | 0.45 | lens 半透明度 | 全样本 |
| mast_slide_range | float | [0.16, 0.45] | 0.32 | telescoping mast PRISMATIC 行程 | rec_…_b9ab25 / rec_…_afb8b9 |
| support_width_scale | float | [0.9, 1.15] | 1.0 | root/base 平面安全缩放 | resolve_config clamp |
| leg_spread_scale | float | [0.9, 1.18] | 1.0 | tripod 腿外张/wheeled fork 张开度 | resolve_config clamp |
| arm_thickness_scale | float | [0.9, 1.15] | 1.0 | yoke arm 截面厚度安全缩放 | resolve_config clamp |
| head_aim_scale | float | [0.9, 1.10] | 1.0 | head 沿 aim 方向 length/lens 微调（clamp 避免穿 yoke arms） | resolve_config clamp |
| bezel_radius_scale | float | [0.95, 1.10] | 1.0 | bezel 半径相对 lens 安全 envelope | resolve_config clamp |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette 与 module-local variant；未实现拓扑（foldable_mast / 工业 FIXED-pan / square_base 单独 slot）不进 enum。

## Multiplicity / Copy Logic

本类别含若干 module-local 复制逻辑：

**(1) tripod_leg_count（root 内部 multiplicity）**
- count_param：`tripod_leg_count`
- N_range：{3}（5 星样本中 3 腿固定，少见 4 腿亦视为 4 腿 stand 但本类别样本均为 3）
- sampling domain：固定 3；仅当 root ∈ {tripod_post_base, telescoping_tripod_stand} 启用
- copied object：leg（tube_from_spline_points / wire_from_points / cadquery sleeve）+ rubber_foot
- naming：`leg_0..2`，`leg_hinge_0..2`，`rubber_foot_0..2`
- placement：crown_hub 周围等角 120° 绕 Z 轴
- joint policy：每条 leg 一个 REVOLUTE leg_hinge（crown→leg），axis 垂直 leg 径向（多为 (0,±1,0)）；range≈[0, 1.05] 或 [-0.45, 0.65]
- source/gating：rec_…_1761967d L226-L256；rec_…_afb8b9 / rec_…_35f03b / rec_…_06058b L172-L182

**(2) caster_wheel_count（root 内部 multiplicity）**
- count_param：`caster_wheel_count`
- N_range：{3, 4}
- sampling domain：仅当 root = wheeled_dolly_base；rec_…_aa36438（4）/ rec_…_f20d5d（3）
- copied object：caster_yoke（Box）+ wheel（TireGeometry）
- naming：`caster_yoke_i`，`wheel_i`，`wheel_spin_i`
- placement：底盘四角（N=4）或等角 120°（N=3）
- joint policy：每轮 CONTINUOUS wheel_spin（base→wheel）axis=(0,0,1)（仅自转，不旋向转向）
- source/gating：rec_…_aa36438 L210-L221；rec_…_f20d5d L88-L176

**(3) barndoor_leaf_count（aux 内部 multiplicity）**
- count_param：`barndoor_leaf_count`
- N_range：{4}（5 星样本全 4 叶 top/bottom/left/right；spec 固定）
- sampling domain：仅当 aux = barndoor_four_leaf
- copied object：leaf（Box 薄片）
- naming：`leaf_top`/`leaf_bottom`/`leaf_side_0`/`leaf_side_1`
- placement：barndoor_frame 4 边缘对称
- joint policy：每叶 REVOLUTE，axis 沿叶根边；top/bottom (0,1,0)，side (0,0,1)；range 各 [-1.22, 0.61] 或 [-0.61, 1.22] 对称
- source/gating：rec_…_aa36438 L371-L437；rec_…_6eef18 / rec_…_8550 / rec_…_eef416 / rec_…_d3ef30

**(4) fresnel_ring_count（head 内部 multiplicity）**
- count_param：`fresnel_ring_count`
- N_range：{3, 4}
- sampling domain：仅当 head = fresnel_lens_can
- copied object：fresnel_ring（TorusGeometry 半透明）
- naming：`fresnel_ring_i`
- placement：lens 中心同心，半径等差递减（外向内）
- joint policy：parent visual，无 joint
- source/gating：rec_…_193640 L136-L270；rec_…_6eef18 L273-L373

**(5) tilt_lock_knob_count（aux 内部 multiplicity）**
- count_param：固定 N=2，spec 不暴露
- copied object：lobed KnobGeometry + 可选 friction Torus
- naming：`tilt_lock_knob_0/1`，`tilt_lock_knob_spin_0/1`
- placement：pan_yoke 两侧 trunnion 外端，与 tilt 轴共线
- joint policy：每个 CONTINUOUS（pan_yoke→knob）axis 与 tilt 轴共线（左右镜像符号）

**(6) yoke_arm_count / trunnion_count — 固定，不采样**
- two_arm_box / mesh_trunnion / swept_arm 固定 2 arm；side_pivot 固定 1 arm；trunnion stub 与 yoke arm 数对齐；不暴露 `*_count`。

**(7) auxiliary 数量**
- auxiliary 为 0 或 1 个（none / 单个 aux module）；非可变 N。tilt_lock_knobs 内部固定 2，其余 aux 均为单实例。

## 拓扑多样性审计

总组合数（合法化前）：A(6) × B(4) × C(4) × D(7) = 672；再 × pan_joint_type(2) × tilt_axis(3) ≈ 4032 个 enum 组合。compatibility matrix 裁剪后估算合法组合：

- floor_pedestal/low_disk/wheeled × {two_arm,mesh,swept,side} × C(4) × D(7) ≈ 3×4×4×7 = 336；减去 fresnel↔front_filter/lens_cover 互斥（3×4×1×2=24）→ ≈ 312
- tripod_post / telescoping_tripod × {two_arm,mesh,swept,side} × C(4) × D(7) ≈ 2×4×4×7 = 224
- telescoping_floor × {two_arm,mesh,swept,side} × C(4) × D(7) ≈ 1×4×4×7 = 112
- 合计合法组合 **≥ 600**（保守），再叠加 pan_joint_type(2)、tilt_axis 选择、caster_count {3,4}、fresnel_ring_count {3,4}、mast_slide range 与 leg_hinge range 区段 → 远超门槛。

理由：仅 A×B×C×D 在合法子集内已远超 10 个 distinct 拓扑等价类（floor vs tripod vs wheeled vs telescoping 的 root part tree 差异极大；fresnel 头 + barndoor 是独立 part tree；wheeled+barndoor=dolly studio light；telescoping+gel_frame=theatre light；tripod+foldable_handle=portable；tilt_lock_knobs vs none 决定是否带 ±X CONTINUOUS knob 关节）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed deterministic procedural sampling —— rng 先选 root_choice → 经 compatibility matrix 得 yoke/head/aux 合法子集再依次选 → 派生 multiplicity（tripod_leg_count / caster_wheel_count / barndoor_leaf_count / fresnel_ring_count）→ 采样 pan_joint_type / tilt_axis / tilt_lower / tilt_upper / 连续 scale（dimensions）。`seed=0` 不特殊。所有非法组合由 compatibility matrix + `resolve_config` clamp 拦截。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 root×yoke×head×aux 家族至少 1 例。重点：

- pan 轴竖直、tilt 轴水平、tilt origin 落两 trunnion 连线（U-yoke）或单 trunnion offset（side_pivot）
- spotlight head 不漂浮，trunnion 被 yoke bearing 捕获
- barndoor leaves closed pose 不互相穿模，全开 pose 不超 frame envelope
- tripod 腿展开/收拢全 range 内 leg 不穿地、不穿中柱
- telescoping mast 全 PRISMATIC range 内 inner_post 不脱出 sleeve、不与 base 干涉
- wheeled dolly 4 caster 全 CONTINUOUS spin 不与底盘干涉
- fresnel rings 同心、半径单调、半透明 alpha 与 lens 一致
- foldable_carry_handle fold 后贴 can 顶不穿 lens
- aux closed pose 不遮挡 lens identity

Topology target：1000-seed slot choice tuple distinct 建议 ≥150；本类别合法组合 ≥600，预期可达。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
regression overrides：初版默认 none；若 sweep 暴露 root×aux 特定失败组合（如 wheeled_dolly+barndoor 的 frame 与底盘相撞，或 telescoping_tripod+gel_frame 的 gel slide 与 leg 干涉）再以稀疏、显式 + 失败回归理由加入，不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入 `pan_height [0.18,1.45]`、`post_radius [0.018,0.090]`、`yoke_span [0.10,0.42]`、`pan_stage_height [0.05,0.32]`、`head_length [0.08,0.42]`、`head_radius [0.030,0.18]`、`lens_radius [0.026,0.16]`、`lens_alpha [0.32,0.70]`、`mast_slide_range [0.16,0.45]`、`tilt_lower/tilt_upper`、`support_width_scale [0.9,1.15]`、`leg_spread_scale [0.9,1.18]`、`arm_thickness_scale [0.9,1.15]`、`head_aim_scale [0.9,1.10]`、`bezel_radius_scale [0.95,1.10]`。全部在 `resolve_config` clamp / 派生，受 trunnion line 长度、yoke bearing 捕获、bezel envelope、接地面、pan bearing 贴合、PRISMATIC 行程限位约束；不改变 slot/module 选择、tripod/caster/barndoor/fresnel multiplicity、aux 存在性等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | root→yoke→head→aux 顺序选择 + 每步 compatibility gate；weighted（floor pedestal 高、low disk/wheeled/telescoping 中、tripod_post/telescoping_tripod 低-中；fresnel/cadquery head 中频但保留） | slot_choices_for_seed matches build choices |
| compatibility matrix | tripod_leg↔tripod root；caster_wheel↔wheeled root；mast_slide↔telescoping root；tilt_lock_knobs↔U/mesh/side yoke（非 swept）；fresnel_lens↔aux ∈ {none, barndoor, focus_knob, foldable_handle}；cadquery 可用性；FIXED pan 不进采样 | no floating（head/aux 不漂浮）、collision（barndoor closed/open、tripod leg vs ground/mast、telescoping range、caster vs base）、axis（pan Z、tilt horizontal、leaf hinge 边轴）、max multiplicity（caster≤4、leaf=4、fresnel_ring≤4）、bulky module、optional child（aux 缺省安全）、closed pose（gel slide retracted、cover closed、handle folded） |
| controlled local variation | pan_height/post_radius/yoke_span/pan_stage_height/head_length/head_radius/lens_radius/lens_alpha/mast_slide_range/tilt_range/support_width/leg_spread/arm_thickness/head_aim/bezel_radius，全 clamp | 比例变化不破坏 trunnion 捕获、bezel envelope、tilt 轴穿两 trunnion、pan bearing 贴合、接地、PRISMATIC 行程、joint origin、类别 identity |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/captured-pin/axis/range/closed pose） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A root_support | 6 | yes | yes | floor / low_disk / tripod_post / wheeled_dolly / telescoping_floor / telescoping_tripod |
| B pan_yoke | 4 | yes | yes | two_arm_box / mesh_trunnion / swept_arm / side_pivot |
| C spotlight_head | 4 | yes | yes | primitive / lathe / cadquery / fresnel |
| D auxiliary_mechanism | 7 | yes | yes | 含 none |

兼容矩阵（合法 / 互斥 / fallback）：

- `tripod_post_base` / `telescoping_tripod_stand` ⇒ 含 3 leg_hinge REVOLUTE（必须）；其他 root 禁止 leg_hinge。
- `wheeled_dolly_base` ⇒ 含 3-4 wheel_spin CONTINUOUS（必须）；其他 root 禁止 wheel_spin。
- `telescoping_floor_stand` / `telescoping_tripod_stand` ⇒ 含 mast_slide PRISMATIC（必须）；其他 root 禁止 mast_slide。
- `tilt_lock_knobs` ⇒ pan_yoke ∈ {two_arm_box, mesh_trunnion, side_pivot}（swept_arm 拓扑无外侧 boss）。
- `barndoor_four_leaf` ⇒ head ∈ {primitive_box_cylinder_can, lathe_shell_can, cadquery_shell_can, fresnel_lens_can}（任意；frame 落 can 前缘 bezel 外平面）。
- `front_filter_or_gel_frame` ⇒ head ∈ {primitive_box_cylinder_can, lathe_shell_can, cadquery_shell_can}（**fresnel_lens_can 禁止**：fresnel 面前不挂 filter/gel，会遮 identity）。
- `service_hatch_or_lens_cover` ⇒ head ∈ {primitive_box_cylinder_can, lathe_shell_can, cadquery_shell_can}（fresnel 禁止 lens_cover；rear hatch 始终允许，front cover 仅非 fresnel）。
- `cadquery_shell_can` ⇒ 仅 cadquery 可 import；否则 fallback 到 lathe_shell_can。
- `wheeled_dolly_base` ⇒ pan_joint_type ∈ {continuous, wide_revolute(-2.8..2.8), revolute_limited(-π..π)}（不可 FIXED）；其余 root 同。
- `low_floor_disk_base` ⇒ 更偏 CONTINUOUS pan（地板 disk 摄影常自由旋转）。
- pan FIXED 不进入采样（reviewer-gated 工业变体）。
- pan axis 必须 Z（0,0,1）；tilt axis 必须水平且与 yoke trunnion 朝向一致；leaf hinge axis 必须沿 leaf 根边。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D 四元组 + pan_joint_type + tilt_axis + 派生 multiplicity）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（tripod_leg↔tripod root、caster↔wheeled、mast_slide↔telescoping、tilt_lock_knobs↔非 swept yoke、fresnel↔front_filter/lens_cover 互斥、cadquery 可用性、FIXED pan 不入采样）
- optional regression overrides are sparse and justified（初版 none）
- controlled local scale params (pan_height/post_radius/yoke_span/pan_stage_height/head_length/head_radius/lens_radius/lens_alpha/mast_slide_range/tilt_range/support_width/leg_spread/arm_thickness/head_aim/bezel_radius) clamped；不破坏 trunnion 捕获、tilt 轴穿两 trunnion 连线、pan bearing 贴合、bezel envelope、接地面、PRISMATIC 行程、leaf hinge 闭合 envelope、类别 identity
- critical InterfaceSpec / MatingContract points exist：turntable↔pan bearing seat（pan_yaw 轴向贴合）、yoke trunnion bearing↔head trunnion stub（tilt captured pin，element-scoped allow_overlap）、barndoor frame↔can 前缘（FIXED）、leaf hinge↔frame 边、filter/gel hinge↔can 前缘、cover/hatch hinge↔can 边、knob shaft↔can 后/侧、handle pivot↔can 顶、leg_hinge↔crown_hub、mast_slide↔sleeve 内壁、wheel_spin↔caster yoke
- key joints have expected type/axis/range：pan REVOLUTE/CONTINUOUS axis=(0,0,1) range ∈ {[-π,π], CONTINUOUS, [-2.8,2.8]}；tilt REVOLUTE axis 水平 range≈[-0.95,1.40]；leg_hinge REVOLUTE axis=(0,±1,0) range≈[0,1.05]；mast_slide PRISMATIC axis=(0,0,1) range≈[0,0.45]；wheel_spin CONTINUOUS axis=(0,0,1)；leaf hinge REVOLUTE 各 axis 与 range；knob/handle 各 axis 与 range
- spotlight head geometry：head 必含 translucent front lens(alpha∈[0.32,0.70]) + bezel ring + rear cap + 2 trunnion stub（side_pivot 单 stub）；primitive 不得从 lathe/cadquery 降级成只剩 Box（lens/bezel/cap 必须保留）；fresnel head 必含 ≥3 同心 TorusGeometry 环
- copied objects follow naming/placement policy（leg_i 等角 120°；wheel_i 底盘四角或等角；leaf top/bottom/side 4 叶对称；fresnel_ring_i 同心半径递减；tilt_lock_knob_0/1 对称）
- tilt hinge origin 落 yoke 两 trunnion 连线（U-yoke）或单 trunnion offset（side_pivot），非 yoke 任意中心
- closed pose & range：barndoor closed 不互穿、不超 bezel envelope；filter/gel 收回时不穿 lens；service hatch 闭合贴 can；foldable handle fold 后贴 can 顶不穿 lens
- 改 tilt axis 符号或 range 时必须 pose 到 upper/lower 实测 AABB，不能只在 rest pose 验（参 [[project_sweep_only_rest_pose]]）

## Reject cases

- 静态 spotlight 缺 pan 或 tilt 任一关节（退化成固定灯具 / 单 DOF）。
- pan 轴水平 或 tilt 轴竖直（轴向错误）；leaf hinge 不沿 leaf 根边。
- head 脱离 yoke trunnion，trunnion stub 未被 yoke bearing 捕获 → head 漂浮（[[project_sweep_only_rest_pose]] 风险）。
- head 缺 translucent front lens / bezel / rear cap，退化成普通 Box/Cylinder（违反 identity；lens 必须 alpha<1）。
- fresnel_lens_can 配 front_filter_or_gel_frame / lens_cover（遮挡 fresnel 同心环 identity）。
- barndoor frame 浮在 can 前不接触 bezel envelope；leaf closed/open 与 frame 或相邻 leaf 穿模。
- tripod leg 在某 hinge 位置穿地或穿中柱；leg 展开 range 不一致。
- telescoping mast inner_post 在 PRISMATIC 上限脱出 sleeve 或下限穿底盘。
- wheeled caster wheel 穿底盘或与车体相撞；caster 数与采样 N 不一致。
- 把 head shell 的 lathe/cadquery profile 沿 aim 方向居中偏差（[[feedback_mesh_profile_origin_pitfall]]），导致 lens 偏出 bezel 或 trunnion 偏出 yoke。
- 仅 rest pose 验 tilt —— 改 tilt axis 符号必须 pose 到 upper/lower 实测 AABB（[[project_sweep_only_rest_pose]]）。
- aux 第二/第三自由度几何不连贯（focus_knob 浮空 / barndoor frame 不贴 bezel / handle pivot 不在 can 顶 hinge eye）却靠 sweep pass 蒙混（[[feedback_gated_aux_geometry_coherence]]）。
- 把 multiplicity 件（fresnel ring、cooling fin、tripod leg）当成 slot 拓扑差异 —— 这些是 module-local 复制（参 [[feedback_multiplicity_includes_jointless]]）。
- 包形外壳把 lens 完全藏起来（[[feedback_enclosed_mechanism_open_front]]），lens 必须可见。

## 与相邻类别的边界

- 不该混入：塔式探照灯 —— 那是 pole/lattice/tripod 塔身 + 高位 pan_yoke + barrel head 的 **塔式** spotlight，root scale 远大（tower_height 2-5m）；本类别是 studio/photo scale（0.2-1.5m），root 是 floor/tripod/wheeled，不堆叠塔身。
- 不该混入：监控云台杆 —— 末端是相机 + 镜头模组，不是带 lens/bezel 的 spotlight barrel；本类别 head 必含半透明 lens identity。
- 不该混入：`parabolic_dish_on_azimuth_elevation_mount` —— 末端是凹面抛物反射体 + feed horn，不是 barrel can；运动链同形但身份件完全不同。
- 不该混入：`ceiling_light_fixture` / `screwin_light_bulb_with_socket` / `box_fan_with_control_knob` —— 无 pan + tilt 两级 articulation；缺 yoke 结构。
- 不该混入：`articulated_task_lamp` —— 是多关节臂 + 灯头链（serial chain），而本类别只有 pan + tilt 两关节，且 root 是静态 base 不是可弯曲手臂。
- 不该混入：`monitor_mount` / `desktop_monitor_with_tilt_swivel_stand` —— 末端是 panel/屏幕，不是带 lens 的 spotlight；俯仰/方位虽类似但 identity 不同。
- 不该混入：`stand_mixer` / `box_fan_with_control_knob` —— 是单 DOF 旋钮/风扇，无 yoke trunnion 抱头拓扑。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | A | floor_pedestal_base | rec_studio_spotlight_on_yoke_0001 | L49-L96 | 矩形重力 base + 中央立柱 root |
| S-A2 | A | low_floor_disk_base | rec_studio_spotlight_on_yoke_0005 | L97-L148 | 低矮 disk floor base + 直接 pan |
| S-A3 | A | tripod_post_base | rec_studio_spotlight_on_yoke_1761967de3ef43ad8d0ac952de205378 | L53-L165（含 leg 3× L226-256） | crown + 3 leg(spline) + 中心 mast |
| S-A4 | A | wheeled_dolly_base | rec_studio_spotlight_on_yoke_aa36438f54c446b0b15452bf78f1ef12 | L134-L189（含 wheel 4× L210-221） | dolly 4 caster |
| S-A5 | A | telescoping_floor_stand | rec_studio_spotlight_on_yoke_b9ab25fbcdaa40229d411825763757bd | L100-L135（含 PRISMATIC L226-234） | sleeve + inner_post PRISMATIC |
| S-A6 | A | telescoping_tripod_stand | rec_studio_spotlight_on_yoke_afb8b91e473b4db28cb0a8fd8dbfb469 | L133-L157（含 column_slide L297-305） | tripod + 中心 column PRISMATIC |
| S-B1 | B | two_arm_box_yoke | rec_studio_spotlight_on_yoke_0001 | L98-L142 | turntable + 2 Box arm + trunnion bearing |
| S-B2 | B | mesh_trunnion_yoke | rec_studio_spotlight_on_yoke_a7d172f7cf79434685dcca702d4364db | L46-L59 | TrunnionYokeGeometry 单 mesh |
| S-B3 | B | swept_arm_yoke | rec_studio_spotlight_on_yoke_0003 | L219-L277 | sweep_profile_along_spline 弯曲 arm |
| S-B4 | B | side_pivot_yoke | rec_studio_spotlight_on_yoke_6ba32e9f51ee462582286df6b19cf3ab | L134-L208 | 单 offset side arm + 单 trunnion |
| S-C1 | C | primitive_box_cylinder_can | rec_studio_spotlight_on_yoke_0001 | L144-L222 | Box + Cyl + 半透明 lens + bezel + rear cap |
| S-C2 | C | lathe_shell_can | rec_studio_spotlight_on_yoke_0002 | L284-L372 | LatheGeometry.from_shell_profiles 中空灯壳 |
| S-C3 | C | cadquery_shell_can | rec_studio_spotlight_on_yoke_06058b5ff50d45db8b83e7ff183ff9ce | L246-L300 | mesh_from_cadquery 灯壳 |
| S-C4 | C | fresnel_lens_can | rec_studio_spotlight_on_yoke_193640fbb692448ab2c13cf08ae04fad | L136-L270 | LatheGeometry 壳 + BezelGeometry + TorusGeometry 同心 fresnel 环 |
| S-D1 | D | tilt_lock_knobs | rec_studio_spotlight_on_yoke_a7d172f7cf79434685dcca702d4364db | L104-L151 | 2 KnobGeometry + CONTINUOUS |
| S-D2 | D | focus_or_mode_knob | rec_studio_spotlight_on_yoke_eef41631f0d34697a9316ac0b700be93 | L312-L341 | 单 KnobGeometry rear knob + CONTINUOUS |
| S-D3 | D | barndoor_four_leaf | rec_studio_spotlight_on_yoke_aa36438f54c446b0b15452bf78f1ef12 | L353-L437 | FIXED frame + 4 REVOLUTE leaf |
| S-D4 | D | front_filter_or_gel_frame | rec_studio_spotlight_on_yoke_d1205dce2bf343bab3d9758393ccfcee | L229-L275 | filter REVOLUTE 翻盖（rec_…_afb8b9 L271-332 / rec_…_d7dcae L324-363 PRISMATIC gel_slide 同型） |
| S-D5 | D | service_hatch_or_lens_cover | rec_studio_spotlight_on_yoke_78d9f7c8b02d4aa48ed97c4ef453400a | L111-L267 | REVOLUTE rear hatch + gasket + latch（rec_…_85881 cover_hinge / rec_…_987798 L166-225 同型） |
| S-D6 | D | foldable_carry_handle | rec_studio_spotlight_on_yoke_f20d5deae1534c4894cc84479eef4363 | L415-L454 | REVOLUTE pivot + tube grip（rec_…_35f03b L307-383 同型） |

## 模板实现备注（可选）

- 共享 helper：`_yoke_trunnion_bearing()`（U-yoke 双 bearing 或 mesh trunnion 单 bearing）、`_can_shell(primitive/lathe/cadquery/fresnel)` 四 primitive 分支不可降级、`_fresnel_rings(n)` 同心 Torus 复制、`_barndoor_leaves()` 4 叶对称、`_tripod_legs(n=3)` spline tube 等角、`_caster_wheels(n)` 等角或四角、`_tube_grip` 折叠 handle、`_lock_knob_pair` 镜像对称。
- 重点 InterfaceSpec / MatingContract：`pan_seat↔turntable` 轴向贴合（expect_gap≈0.0015）；`yoke trunnion bearing↔head trunnion stub` captured pin（element-scoped allow_overlap，参 rec_…_0001 L210-222、rec_…_b3bc02 L201-211）；`barndoor frame↔can 前缘` FIXED 贴 bezel 外平面；`leaf hinge↔frame edge` REVOLUTE 沿叶根边；`filter/gel hinge↔can 前缘 / 抽插槽`；`cover/hatch hinge↔can 边`；`knob shaft↔can 后/侧 boss`；`handle pivot↔can 顶 hinge eye`；`leg_hinge↔crown_hub` REVOLUTE captured；`mast_slide↔sleeve 内壁` PRISMATIC 限位；`wheel_spin↔caster yoke` CONTINUOUS 内孔。
- captured-pin overlap：trunnion-in-yoke-bearing、leg-pin-in-crown、knob-shaft-in-can-boss、handle-pin-in-eye、wheel-axle-in-caster、column-in-sleeve 处需 element-scoped allow_overlap，仅对真实意图穿插声明。
- 暂不进入 seed domain（待审核或后续启用）：foldable_mast (rec_…_36d06ee L130-154，1/46 极罕见)、FIXED pan 工业变体 (rec_…_6d632 / rec_…_8fe98 / rec_…_97861e / rec_…_4efbe4 / rec_…_a7d172 / rec_…_bbaef / rec_…_fa8e36，weatherproof/calibration)、square_base 截面变体 (rec_…_11075c2c 作为 floor_pedestal_base 内部截面 variant)；cadquery_shell_can 仅在 cadquery 可 import 时启用，否则 fallback 到 lathe_shell_can。
- 4-leg tripod 变体 (5 星样本中未出现) 暂不进入；caster_wheel_count {3,4} 双值覆盖 dolly 三轮/四轮设计。
- side_pivot_yoke + barndoor_four_leaf 仅 rec_d3ef30 1 例，作为低权重 candidate；如 sweep 暴露不对齐问题则收窄到 side_pivot 不配 barndoor。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全 46 个 5 星样本（rec_studio_spotlight_on_yoke_*）逐文件读取 model.py / revision.json / record.json / prompt / category metadata，分 4 批并行 Explore；候选模块 source 锚定每条 `model.py:Lx-Ly`。结构家族：6 root × 4 yoke × 4 head × 7 aux + 4 module-local multiplicity（tripod_leg/caster/barndoor_leaf/fresnel_ring）。等待人工审核。 |
