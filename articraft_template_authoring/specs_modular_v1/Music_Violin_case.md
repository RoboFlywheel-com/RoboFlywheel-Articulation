# Violin Case Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `violin_case` |
| template path | `agent/templates/Music_Violin_case.py` |
| test path (optional) | `tests/agent/test_violin_case_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：根 `bottom_shell`（violin/dart/oblong 轮廓的料斗 tub，红色 plush 凹槽）为静态 ROOT；`lid`（匹配的浅壳）经 `bottom_to_lid` REVOLUTE 沿后（+Y）长边铰链 0..180° 折平（linear_chain shell↔lid 核心）。其上挂三组**平行子件**：Slot B closure（拥有真正的开合 latch/zipper/buckle 子机构与 multiplicity）、Slot C carry（可选 grab/strap 硬件）、Slot D interior（可选 cradle/clip/pocket 内衬）。Slot B=hinge 分支带 `latch_count` **multiplicity** 轴（N∈{2,3,4} 沿前 -Y 边复制 flip latch）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | all 5-star samples in this category：1 parent + 12 variant 的 `model.py` 全文已读 |
| samples_adopted_as_module_sources | 13 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

13 个 5★ 样本（1 parent + 12 fork variant，全部 compile=success、workbench-only、≥1 非 fixed joint、明确读作 violin 提琴硬盒）逐条阅读摘要：

- **S1 `rec_hardshell-violin-case-with-a-hinged-clamshell-li_...7727811a`**（全批 fork 母资产）— 基线。`bottom_shell`(ROOT) = violin 轮廓 tub（`_violin_half_points` L54-84 拼 scroll→upper bout→C-bout 腰→lower bout→tail 样条；`_bottom_shell_solid` L117-127 outer extrude 后 inset 样条 cut 出凹槽；`_red_interior_solid` L130-146 = 红 plush 地板垫 + 抬起壁唇）。`lid`(L212-225) = 匹配浅壳 + 红衬，`bottom_to_lid`(L231-240) REVOLUTE axis=-X、origin=(0,HINGE_Y,HINGE_Z)、0..180° 折平到 +Y 侧（open-book 姿态）。前 -Y 边 2 个 `latch_i` flip 杆（L242-278，`bottom_to_latch_i` REVOLUTE axis +X、0..80°）= multiplicity N=2 基线。后 +Y 边 2 个 hinge knuckle 内联 visual（L195-201）。这是 4 个 slot 的基线源 + lid 核心 + latch multiplicity 源。
- **S2 `rec_violin_case_var_outline_dart`** — Slot A `rounded_dart_taper`。改 footprint helper：`_dart_half_points`(L59-92) 在 +X tail 端宽圆、向 -X neck 端收成窄圆点（无 C-bout 腰），`_dart_outline_wire`(L106-122) 同样样条机制；shell/recess/lid 全部 keying 到 dart 轮廓。part 树与 S1 同名（bottom_shell/lid + 红衬 + hinge knuckle）。run_tests 加 dart shape 断言（L315-327，neck 半宽 < lower-bout 半宽×0.5）。
- **S3 `rec_violin_case_var_outline_rectangular`** — Slot A `rectangular_oblong`。footprint helper 换成 `_rounded_rect_solid(length,width,height,corner_r)`(L55-70，`CORNER_R=0.025` 竖边 fillet)，`_bottom_shell_solid`(L73-82) rect tub + rect 凹槽，hinge knuckle 坐在**固定 `HALF_W`**（L153-158，不再用 `_half_width_at_x` 插值），latch 在固定 (-0.15,0.15)（L203）。run_tests 断言 oblong 长宽比（L260-267）。**构建方法不同**（rect fillet vs 样条；固定半宽 vs 插值半宽）。
- **S4 `rec_violin_case_var_closure_zipper`** — Slot B `zipper_perimeter`。**删除 metal flip latch**，改软式拉链：3 边 rim 上 `zipper_track` tube（`tube_from_spline_points`，L253-265），前 -Y 边 `zipper_tooth_{i}`×8 + `zipper_stopper_{i}`×2 内联 visual（L267-286），`zipper_pull` 独立 part（L326-335）经 `bottom_to_zipper_pull` **PRISMATIC** axis +X 沿前缝平移（L340-350，±0.18m）；lid 改 `padded_nylon` 软盖（`_lid_padding_solid` L159-163）但仍 `bottom_to_lid` REVOLUTE 折平。run_tests 显式断言 `latch_0/latch_1` part 不存在（L404-415）。joint 拓扑 = lid REVOLUTE + 1× PRISMATIC。
- **S5 `rec_violin_case_var_closure_buckle_straps`** — Slot B `buckle_straps`。**删 latch**，改 2 条皮带→金属扣链：`strap_i`(L326-330) `lid_to_strap_i` REVOLUTE axis -X 0..60°（铰在 LID 前缘），`buckle_i`(L353-357) `strap_to_buckle_i` REVOLUTE axis -X 0..40°（铰在 strap 自由端），bottom 前墙 `catch_plate_i` 内联 visual（L270-282）承接扣。`_strap_band_solid`(L182-188)/`_buckle_frame_solid`(L191-221 带 prong bar + open window)。run_tests `expect_contact` strap↔lid（L513-518）。joint 拓扑 = lid REVOLUTE + 2×(strap REVOLUTE + buckle REVOLUTE) = 链式 2-link。
- **S6 `rec_violin_case_var_carry_top_handle`** — Slot C `single_top_handle`。bottom 前墙 2 个 `handle_mount_foot_{i}`+`handle_mount_ear_{i}` 内联 visual（L319-337），`carry_handle` 独立 part（curved grab bar 经 `_handle_bar_points` L183-201 + `tube_from_spline_points`，2 pivot stub），`bottom_to_handle` REVOLUTE axis -X 0..100°（L372-385，从贴墙 q=0 摆出 -Y/+Z）。joint 拓扑 = +1 REVOLUTE。
- **S7 `rec_violin_case_var_carry_dual_side_handles`** — Slot C `dual_side_handles`。两长边各 1 把：`_handle_bar_mesh(side)`(L188-215) 跟随 violin 壁 contour 的 9-pt 样条（`_half_width_at_x` 偏置）+ `_handle_assembly`(L225-240) 合并 2 pivot stub；`handle_{i}` part（L374-385）+ `bottom_to_handle_{i}` REVOLUTE axis=±X 0..90°（L390-403），mount foot boss 内联（L362-371）。`for i in range(2)` 固定循环。joint 拓扑 = +2 REVOLUTE（±Y 对称）。
- **S8 `rec_violin_case_var_carry_shoulder_strap_loops`** — Slot C `d_ring_strap_loops`。后 +Y 墙两端（neck/lower-bout，`DRING_X_POSITIONS=(-0.24,0.24)`）各 1 个 D 形吊环：`dring_mount_plate_{i}`+`dring_pivot_bar_{i}` 内联（L343-360），`d_ring_{i}` part（`_d_ring_mesh` L206-217 D 形 tube）+ `bottom_to_d_ring_{i}` REVOLUTE axis +X 0..170°（L379-392，绕 pivot bar 外摆）。`for i in range(2)`。joint 拓扑 = +2 REVOLUTE（+Y 后墙）。
- **S9 `rec_violin_case_var_interior_neck_cradle`** — Slot D `neck_cradle`。在 bottom 凹腔 neck 端（cx=-0.30）加静态 `neck_cradle` visual（`_neck_cradle_solid` L149-204：loft 锥块 + Y 向半圆 saddle 槽 cut + top 边 fillet），**无 joint**。run_tests `expect_within`（L408-415）保证含在 footprint 内、坐落地板。joint 拓扑 = 不变（纯静态 visual）。
- **S10 `rec_violin_case_var_interior_bow_clips`** — Slot D `bow_spinner_clips`。**lid 内**装 2 个 spinner 夹捕一根存放的弓：lid 内联 `clip_mount_{i}` post（L275-285）、`bow_stick`/`bow_frog`/`bow_cradle_pad_{i}`（L288-315），`bow_clip_{i}` part（`_bow_clip_arm_solid` L185-198 hub+paddle+hook）+ `lid_to_bow_clip_{i}` **REVOLUTE axis +Z** 0..90°（L335-348，绕 post 旋开释放）。run_tests `expect_contact` clip↔mount、`expect_overlap` clip↔bow（L543-557）。joint 拓扑 = +2 REVOLUTE（**父为 lid**，绕 Z）。
- **S11 `rec_violin_case_var_interior_accessory_pocket`** — Slot D `accessory_pocket`。bottom 凹腔 lower-bout 端（POCKET_X_CENTER=0.24）加 `pocket_box`（空心开顶盒 `_pocket_box_solid` L184-199）+ `pocket_pad` + `pocket_hinge_barrel` 内联（L335-352），`pocket_lid` part（`_pocket_lid_solid` L213-222 平板）+ `bottom_to_pocket_lid` **REVOLUTE axis (0,-1,0)** 0..120°（L367-378，掀盖）。run_tests `expect_gap` lid↔box（L503-510）。joint 拓扑 = +1 REVOLUTE（父为 bottom，绕 -Y）。
- **S12 `rec_violin_case_var_latch_count_3`** — Multiplicity N=3。仅改 `latch_positions=(0.02,0.16,0.30)`（L249），前 -Y 边均布 3 个 `latch_i` 同构副本（lever+hook+pin + `bottom_to_latch_i` REVOLUTE 0..80°，L250-279）。其余拓扑同 S1。
- **S13 `rec_violin_case_var_latch_count_4`** — Multiplicity N=4。`latch_positions=(-0.20,-0.05,0.10,0.25)`（L249）从 upper-bout 跨到 lower-bout 均布 4 个 latch（L250-279），run_tests 改 `range(4)` 循环断言（L294-368）。N=4 是产品域上界样本。

跨样本观察：13 样本共享 `bottom_shell` violin/dart/oblong tub + 红 plush 凹槽 + `lid` 浅壳红衬 + `bottom_to_lid` REVOLUTE 0..180° 折平的 open-book 核心、`_violin_half_points/_half_width_at_x/_violin_outline_wire` helper 家族、captured-pin `allow_overlap` 契约（lid 鼻盖、latch pin、handle stub、d-ring pivot、bow clip post、pocket barrel）。差异严格落在四轴：**(A) shell 轮廓**、**(B) closure 机构（含 multiplicity）**、**(C) carry 硬件**、**(D) interior 内衬**。配色高度一致（tweed 棕外壳 0.20/0.17/0.13 + 红 plush 0.62/0.07/0.08 + chrome 金属 0.78/0.79/0.82），为 §7 `palette_style` 提供基线 + 可派生 colorway。

## 核心身份

提琴硬盒（violin case）：一个躺放的细长 clamshell 硬壳乐器盒（~0.80 m 长 × ~0.26 m 宽 × ~0.13 m 高），`bottom_shell` 料斗内有一个**模制红色 plush 凹槽**承托提琴形状，`lid` 沿后长边铰链 **0..180° 折平**成 open-book 姿态（两侧红衬朝上，如参考照片）。世界系约定：+X = 长轴（neck→lower bout），+Y = 宽轴（跨 bouts），+Z = 上；盒底地板近 z=0，rim/密封面在 z=`SHELL_H`；后铰链线在 y=+HALF_W、前闭合硬件在 y=-HALF_W。

成熟域：经典 violin 轮廓（scroll/neck 端 → upper bout → C-bout 腰 → lower bout → tail）硬盒，或其 dart/oblong footprint 变体；含 clamshell lid（必折平 180°）、红 plush 提琴凹槽、可选闭合机构（金属 flip latch / 软拉链 / 皮带扣）、可选提手硬件、可选内衬（neck cradle / bow 夹 / 配件袋）。身份强约束：

- **必须**有 `bottom_shell` ROOT tub + 模制红 plush 凹槽（细长、长 ≫ 宽）。
- **必须**有 `lid` + `bottom_to_lid` REVOLUTE 沿后 +Y 长边、0..180° 折平（open-book）。
- **必须**前 -Y 边有某种闭合机构（latch / zipper / buckle 之一）。
- shell 轮廓、闭合机构、提手、内衬可变（Slot A/B/C/D），但 clamshell 折平身份 + 红 plush 提琴凹槽不可缺。

边界（不该混入，详见 §11）：guitar/cello case（更大、不同 body 轮廓 + 头部颈槽）、generic instrument/road flight case（带 caster/rack rail/butterfly 锁、无乐器形 plush 模）、hard tool case（Pelican 式防水箱、pick-pluck 泡棉、泄压阀、挂锁 hasp）。

## 槽位 + 候选模块表

### Slot A：shell_footprint（主 footprint 槽——bottom/lid 外轮廓 + 红 plush 凹槽形状；下游 recess inset / liner 缩放 / hinge knuckle 落座全部 keying 同一 outline helper）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `violin_contour`（基线） | S1 `rec_hardshell-violin-case-...7727811a` | `model.py:L54-L84`(`_violin_half_points`)、`L87-L95`(`_half_width_at_x`)、`L98-L114`(`_violin_outline_wire`)、`L117-L127`(`_bottom_shell_solid`)、`L130-L146`(`_red_interior_solid`)、`L149-L171`(`_lid_solid`/`_lid_liner_solid`)、`L195-L201`(hinge knuckle 插值落座) | eligible if compatible | 真 violin 样条 silhouette（scroll→upper bout→C-bout 腰→lower bout→tail）；recess 由内缩样条 cut；hinge knuckle 坐在 `_half_width_at_x(hx)` 的插值 rim。 |
| `rounded_dart_taper` | S2 `rec_violin_case_var_outline_dart` | `model.py:L59-L92`(`_dart_half_points`)、`L95-L103`(`_half_width_at_x`)、`L106-L122`(`_dart_outline_wire`)、`L125-L135`(`_bottom_shell_solid`)、`L138-L154`(`_red_interior_solid`)、`L157-L179`(lid)、断言 `L315-L327` | eligible if compatible | 圆 dart/泪滴 footprint：+X tail 端宽圆、-X neck 端收窄圆点、**无 C-bout 腰**；同样条机制不同控制点，hinge knuckle 仍走插值半宽。part 树同名。 |
| `rectangular_oblong` | S3 `rec_violin_case_var_outline_rectangular` | `model.py:L49`(`CORNER_R`)、`L55-L70`(`_rounded_rect_solid`)、`L73-L82`(`_bottom_shell_solid`)、`L85-L104`(`_red_interior_solid`)、`L107-L129`(lid)、`L153-L158`(固定 `HALF_W` 落座)、断言 `L260-L267` | eligible if compatible | 圆角矩形 oblong tub + rect 凹槽（`fillet(CORNER_R)`）；**构建法不同**（rect+fillet vs 样条），hinge knuckle 坐**固定 `HALF_W`**（不插值），latch 在固定 (-0.15,0.15)。 |

> Slot A 三候选差异充分：`violin_contour` vs `rounded_dart_taper` 是样条控制点 + 腰部存在与否（C-bout）；`rectangular_oblong` 是**整套不同的 solid 构建器**（`_rounded_rect_solid` fillet vs `_*_outline_wire` 样条）且 hinge/latch 落座逻辑从「插值半宽」改为「固定半宽」。三者不只是尺寸/颜色差异。**注意**：A 三模块 part/joint 树同名（bottom_shell+lid+红衬+hinge knuckle），所以 A 改的是 footprint 几何与落座逻辑，**不单独新增 part/joint 拓扑等价类**（topology 多样性由 B/C/D + latch_count 驱动，A 提供视觉/识别多样性，见 §9）。

### Slot B：closure_mechanism（主机构槽——拥有真正的开合子机构 + multiplicity；决定前 -Y 边 part 树 + joint 拓扑。lid↔body REVOLUTE 核心由所有候选共享，见 §槽位图）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `hinge_plus_flip_latches`（基线） | S1 `rec_hardshell-...7727811a` | `model.py:L242-L278`(latch loop：lever+hook+pin part + `bottom_to_latch_i` REVOLUTE axis +X 0..80°)、`L248`(`latch_positions`) | eligible if compatible | 前 -Y 边 2..4 个金属 flip latch（lever plate + hook lip + pivot pin），各 REVOLUTE 翻出。**承载 `latch_count` multiplicity 轴**（§8）。joint 拓扑 = lid REVOLUTE + N× latch REVOLUTE。 |
| `zipper_perimeter` | S4 `rec_violin_case_var_closure_zipper` | `model.py:L50-L57`(zipper 常量)、`L159-L163`(`_lid_padding_solid`)、`L168-L191`(`_zipper_track_path_3d`)、`L196-L227`(`_front_edge_point`/tooth/stopper/pull geom)、`L253-L286`(track+teeth+stopper 内联)、`L326-L350`(`zipper_pull` part + `bottom_to_zipper_pull` PRISMATIC axis +X) | eligible if compatible | **删 latch**；3 边 rim 软拉链 cord + teeth/stopper 内联 visual + `zipper_pull` 沿前缝 PRISMATIC（±0.18m）；lid 改 `padded_nylon` 软盖。run_tests 断言无 latch part。joint 拓扑 = lid REVOLUTE + 1× PRISMATIC。 |
| `buckle_straps` | S5 `rec_violin_case_var_closure_buckle_straps` | `model.py:L52-L68`(strap/buckle 常量)、`L182-L221`(`_strap_band_solid`/`_buckle_frame_solid`)、`L229-L235`(`_strap_hinge_y_lid`)、`L270-L282`(catch plate 内联)、`L321-L376`(strap/buckle loop：`lid_to_strap_i` REVOLUTE 0..60° + `strap_to_buckle_i` REVOLUTE 0..40°) | eligible if compatible | **删 latch**；2 条皮带→金属扣 2-link 链铰在 LID 前缘，绕前 rim 搭到 bottom `catch_plate` 上。joint 拓扑 = lid REVOLUTE + 2×(strap REVOLUTE + buckle REVOLUTE)。 |

> Slot B 三候选跨 **N×REVOLUTE flip latch（hinge）/ 1×PRISMATIC slider（zipper）/ 2×2-link REVOLUTE 链（buckle）** 三种 joint 拓扑，是本模板拓扑多样性的主驱动槽；且只有 `hinge_plus_flip_latches` 携带 `latch_count` multiplicity（zipper/buckle 用自身固定 native count，见 §8/§9 兼容矩阵）。

### Slot C：carry_hardware（可选 grab/strap 硬件，bolt 到 bottom_shell 墙；含 baseline none）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none`（基线） | S1 `rec_hardshell-...7727811a` | （无 carry part；parent 默认无提手） | eligible if compatible | 无提手/吊环硬件；degrade baseline（不是所有提琴盒都带外部提手，"裸盒" 是真实成熟态）。 |
| `single_top_handle` | S6 `rec_violin_case_var_carry_top_handle` | `model.py:L54-L60`(handle 常量)、`L183-L201`(`_handle_bar_points`)、`L319-L337`(mount foot/ear 内联)、`L340-L385`(`carry_handle` part + `bottom_to_handle` REVOLUTE axis -X 0..100°) | eligible if compatible | 单把弯 grab bar，2 mount foot/ear 内联，pivot 在前墙中段，REVOLUTE 从贴墙摆出可抓。joint = +1 REVOLUTE。 |
| `dual_side_handles` | S7 `rec_violin_case_var_carry_dual_side_handles` | `model.py:L57-L65`(常量)、`L188-L240`(`_handle_bar_mesh`/`_handle_endpoint_y_local`/`_handle_assembly`)、`L355-L403`(handle loop：mount boss + `handle_{i}` + `bottom_to_handle_{i}` REVOLUTE axis ±X 0..90°) | eligible if compatible | 两长边各 1 把跟随壁 contour 的 grab bar（`for i in range(2)`），pivot stub 落 mount boss，±Y 对称外摆。joint = +2 REVOLUTE。 |
| `d_ring_strap_loops` | S8 `rec_violin_case_var_carry_shoulder_strap_loops` | `model.py:L54-L64`(常量)、`L187-L222`(`_d_ring_tube_points`/`_d_ring_mesh`/`_mount_plate_geometry`)、`L338-L392`(D-ring loop：mount plate+pivot bar + `d_ring_{i}` + `bottom_to_d_ring_{i}` REVOLUTE axis +X 0..170°) | eligible if compatible | 后 +Y 墙两端（neck/lower-bout）2 个肩带 D 形吊环，绕 pivot bar 外摆。joint = +2 REVOLUTE（后墙）。 |

> Slot C 四候选跨 **0 / 1×REVOLUTE / 2×REVOLUTE（侧墙）/ 2×REVOLUTE（后墙，不同 part 名+轴+父落座面）** 四种 carry 拓扑。`none` 为合理 degrade baseline（≥2 候选门槛满足，无需折叠）。

### Slot D：interior_fitting（凹腔内衬，决定内部 part 是否活动 + joint 类型/父）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `plain_plush_recess`（基线） | S1 `rec_hardshell-...7727811a` | `model.py:L130-L146`(`_red_interior_solid`：地板垫 + 抬起壁唇) | eligible if compatible | 仅模制红 plush 提琴凹腔（地板 pad + 壁 lip），无附加内衬。所有候选都含此红衬基底（A 决定其轮廓）。 |
| `neck_cradle` | S9 `rec_violin_case_var_interior_neck_cradle` | `model.py:L149-L204`(`_neck_cradle_solid`)、`L252-L256`(`neck_cradle` 静态 visual)、断言 `L408-L415` | eligible if compatible | neck 端（cx=-0.30）静态悬挂 cradle 块（loft 锥块 + Y 向 saddle 半圆槽 + fillet），**无 joint**（静态 visual）。 |
| `bow_spinner_clips` | S10 `rec_violin_case_var_interior_bow_clips` | `model.py:L53-L62`(常量)、`L185-L198`(`_bow_clip_arm_solid`)、`L275-L315`(post/bow_stick/frog/pad 内联)、`L318-L348`(`bow_clip_{i}` + `lid_to_bow_clip_{i}` REVOLUTE axis +Z 0..90°) | eligible if compatible（gated，见 §9） | **lid 内**装 2 个 spinner 夹捕存放的弓 stick；`lid_to_bow_clip_i` REVOLUTE 绕 +Z 旋开。**父为 lid**，假设 violin-contour 刚性 lid 腔。joint = +2 REVOLUTE（lid 上，绕 Z）。 |
| `accessory_pocket` | S11 `rec_violin_case_var_interior_accessory_pocket` | `model.py:L53-L61`(常量)、`L184-L222`(`_pocket_box_solid`/`_pocket_pad_solid`/`_pocket_lid_solid`)、`L335-L352`(box/pad/barrel 内联)、`L355-L378`(`pocket_lid` + `bottom_to_pocket_lid` REVOLUTE axis -Y 0..120°) | eligible if compatible | lower-bout 端（POCKET_X=0.24）带盖配件盒：`pocket_box` 开顶盒 + `pocket_lid` 掀盖 REVOLUTE 绕 -Y。joint = +1 REVOLUTE（bottom 上，绕 -Y）。 |

> Slot D 四候选跨 **无 joint（plain）/ 静态 visual（neck_cradle）/ 2×REVOLUTE 父=lid 绕 Z（bow_clips）/ 1×REVOLUTE 父=bottom 绕 -Y（pocket）** 四种内衬拓扑。`bow_spinner_clips` 因 lid 挂载 + 假设刚性 violin-contour lid 腔，有 §9 兼容门控。

## 槽位图（slot graph）

pattern = `mixed`（linear_chain shell↔lid 核心 + parallel children closure/carry/interior + latch multiplicity）

```
[bottom_shell]  (ROOT：violin/dart/oblong tub + 红 plush 凹槽；rim 面 z=SHELL_H；后 +Y 边 hinge knuckle 内联)
   |
   |== [lid]  --REVOLUTE bottom_to_lid (axis -X, origin (0, +HALF_W·w, SHELL_H·h), 0..180°)-->
   |        (匹配浅壳 + 红衬；折平到 +Y 侧 open-book；所有 Slot B 候选共享此核心)
   |
   |-- [Slot B closure 子机构]：
   |     · hinge_plus_flip_latches: bottom_shell --REVOLUTE bottom_to_latch_{i} (axis +X, origin (lx, -hw(lx)+0.002, SHELL_H-0.020), 0..80°)--> latch_{i}   [×N latch_count]
   |     · zipper_perimeter:        bottom_shell --PRISMATIC bottom_to_zipper_pull (axis +X, origin (0, -hw(0), SHELL_H+0.004), ±0.18)--> zipper_pull
   |     · buckle_straps:           lid --REVOLUTE lid_to_strap_{i} (axis -X, 0..60°)--> strap_{i} --REVOLUTE strap_to_buckle_{i} (axis -X, 0..40°)--> buckle_{i}   [×2]
   |
   |-- [Slot C carry 子件]（除 none，均挂 bottom_shell）：
   |     · single_top_handle:  bottom_shell --REVOLUTE bottom_to_handle (axis -X, origin (HANDLE_X, -hw(HANDLE_X), HANDLE_Z), 0..100°)--> carry_handle
   |     · dual_side_handles:  bottom_shell --REVOLUTE bottom_to_handle_{i} (axis ±X, origin (0, ±(hw(0)+standoff), HANDLE_Z), 0..90°)--> handle_{i}   [×2]
   |     · d_ring_strap_loops: bottom_shell --REVOLUTE bottom_to_d_ring_{i} (axis +X, origin (dx, +hw(dx)+MOUNT_T, DRING_PIVOT_Z), 0..170°)--> d_ring_{i}   [×2]
   |
   +-- [Slot D interior 子件]：
         · plain_plush_recess: （无 joint；红衬基底 visual 在 bottom_shell）
         · neck_cradle:        （无 joint；静态 cradle visual 在 bottom_shell neck 端）
         · bow_spinner_clips:  lid --REVOLUTE lid_to_bow_clip_{i} (axis +Z, origin (cx, BOW_CLIP_Y, BOW_CLIP_Z), 0..90°)--> bow_clip_{i}   [×2，父=lid]
         · accessory_pocket:   bottom_shell --REVOLUTE bottom_to_pocket_lid (axis -Y, origin (POCKET_HINGE_X, 0, POCKET_HINGE_Z), 0..120°)--> pocket_lid
```

接口点位与装配说明（`hw(x)` = 该 footprint 在世界 x 处的半宽：violin/dart 走 `_half_width_at_x` 插值、oblong 走固定 `HALF_W`）：

- **bottom_shell → lid（核心 hinge）**：joint origin 在后 rim 边 `(0, +HALF_W·width_scale, SHELL_H·height_scale)`，axis=-X；lid solid 在 lid-local frame 平移 `(0,-HINGE_Y,0)` 使铰链边落到 local 原点，q=0 时 lid 正盖 bottom rim、q=180° 折平到 +Y 侧。captured：lid 鼻盖 bottom rim（`allow_overlap` lid_exterior↔bottom_exterior）；后 rim hinge knuckle 为 bottom 内联 visual。
- **Slot B closure 接口**：
  - hinge latch：pivot 在前 -Y 墙 `(lx, -hw(lx)+0.002, SHELL_H-0.020)`，axis +X；`allow_overlap` latch↔bottom（pin/lever 座入前墙）+ latch↔lid（hook lip 扣 lid 前缘）。
  - zipper pull：坐前缘 track `(0, -hw(0), SHELL_H+0.004)`，PRISMATIC +X；`allow_overlap` pull↔track + pull↔bottom；`expect_overlap` pull↔track（XY，保持骑在 track 上）；teeth/stopper/track 为 bottom 内联 visual。
  - buckle：strap 铰在 **lid** 前缘 `(sx, _strap_hinge_y_lid(sx), STRAP_HINGE_Z_LID)`，buckle 铰在 strap 自由端 `(0,0,-STRAP_L)`；catch_plate 为 bottom 前墙内联 visual；`allow_overlap` strap↔bottom/lid、buckle↔bottom/strap；`expect_contact` strap↔lid。
- **Slot C carry 接口**：mount foot/ear/plate/boss/pivot-bar 为 bottom 内联 visual；handle/d_ring part 经 captured-pin `allow_overlap` 座入 mount 硬件（pivot stub↔ear/boss、d_ring↔mount plate）。single/dual 在前/侧墙、d_ring 在后 +Y 墙。
- **Slot D interior 接口**：plain/neck_cradle 纯静态（`expect_within` 保证含在 footprint）；bow_clips 的 post/bow/pad 为 **lid** 内联 visual，clip part captured 在 post（`expect_contact` clip↔mount、`expect_overlap` clip↔bow）；pocket 的 box/pad/barrel 为 bottom 内联 visual，pocket_lid captured 在 barrel（`expect_gap` lid↔box top）。
- **互斥 / 派生关系**：Slot B 三模块互斥（决定 latch/zipper/buckle 哪一族存在 + 是否启用 latch_count 轴）。`HINGE_Y`/`hw()`/所有 joint origin 的 Y 必须**由 Slot A 派生**（violin/dart 插值半宽 vs oblong 固定 HALF_W），latch/handle/d_ring 落座 Y 随之派生（接口一致性）。`bow_spinner_clips` 假设刚性 violin-contour lid 腔，受 §9 门控（不配 zipper 软盖 / 不配 oblong）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `violin_contour`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottom_shell`(bottom_exterior + red_interior + hinge_barrel_{0,1} 内联) / `lid`(lid_exterior + lid_liner) | S1 / model.py:L181-L225 |
| internal joints | 无（shell/lid 内部为 visual 组；hinge knuckle 为内联 visual） | S1 / model.py:L195-L201 |
| upstream interface | ROOT；rim 面 z=SHELL_H；红衬轮廓由 `_violin_outline_wire` 决定 | S1 / model.py:L117-L146 |
| downstream interface | 后 rim `(0,+HALF_W,SHELL_H)` 供 lid 铰链；前墙 `-hw(x)` 供 closure；侧/后墙供 carry；凹腔地板 z=WALL 供 interior | S1 / model.py:L195-L206 |

### Slot A / module `rounded_dart_taper`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同名 `bottom_shell`/`lid`（dart 轮廓） | S2 / model.py:L189-L233 |
| internal joints | 无 | — |
| upstream interface | ROOT；红衬/recess keying `_dart_outline_wire`；hinge knuckle 仍走插值半宽 | S2 / model.py:L125-L154, L203-L207 |
| downstream interface | 同 `violin_contour`，但前/后墙半宽走 dart 插值（neck 端窄、tail 端宽圆） | S2 / model.py:L95-L103 |

### Slot A / module `rectangular_oblong`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同名 `bottom_shell`/`lid`（rounded-rect 轮廓） | S3 / model.py:L140-L182 |
| internal joints | 无 | — |
| upstream interface | ROOT；`_rounded_rect_solid` + `CORNER_R` fillet；hinge knuckle 坐**固定 `HALF_W`** | S3 / model.py:L55-L104, L153-L158 |
| downstream interface | 前墙固定 `-HALF_W`（不插值）；latch 固定 (-0.15,0.15)；其余接口同名 | S3 / model.py:L203-L228 |

### Slot B / module `hinge_plus_flip_latches`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch_{i}`（lever plate + hook lip + pivot pin，i=0..N-1） | S1 / model.py:L252-L263 |
| internal joints | `bottom_to_latch_{i}`（REVOLUTE axis +X，0..80°） | S1 / model.py:L269-L278 |
| upstream interface | pivot 座前 -Y 墙 `(lx,-hw(lx)+0.002,SHELL_H-0.020)`；pin/lever 座入墙（allow_overlap latch↔bottom） | S1 / model.py:L274, L369-L375 |
| downstream interface | hook lip 扣 lid 前缘（allow_overlap latch↔lid）；**承载 latch_count multiplicity** | S1 / model.py:L376-L379 |

### Slot B / module `zipper_perimeter`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `zipper_pull`(pull_body)；内联：`zipper_track`/`zipper_tooth_{0..7}`/`zipper_stopper_{0,1}`；lid 改 `lid_padding` 软盖 | S4 / model.py:L253-L286, L294-L335 |
| internal joints | `bottom_to_zipper_pull`（PRISMATIC axis +X，±0.18） | S4 / model.py:L340-L350 |
| upstream interface | pull 坐前缘 track `(0,-hw(0),SHELL_H+0.004)`；track/teeth/stopper 内联 bottom visual | S4 / model.py:L253-L286 |
| downstream interface | `expect_overlap` pull↔track（XY 骑轨）；`expect_overlap` lid↔pull（闭盖覆盖 pull）；断言无 latch part | S4 / model.py:L404-L515 |

### Slot B / module `buckle_straps`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `strap_{i}`(strap_band_{i}) + `buckle_{i}`(buckle_frame_{i})，i=0,1；内联 bottom `catch_plate_{i}` | S5 / model.py:L270-L282, L326-L357 |
| internal joints | `lid_to_strap_{i}`（REVOLUTE axis -X 0..60°）+ `strap_to_buckle_{i}`（REVOLUTE axis -X 0..40°） | S5 / model.py:L340-L376 |
| upstream interface | strap 铰在 **lid** 前缘 `(sx,_strap_hinge_y_lid(sx),STRAP_HINGE_Z_LID)`（随 lid 开合） | S5 / model.py:L229-L235, L340-L350 |
| downstream interface | strap 搭 bottom 前墙 catch_plate；buckle 铰 strap 自由端；`expect_contact` strap↔lid | S5 / model.py:L491-L518 |

### Slot C / module `none`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无 carry part | S1 |
| internal joints | 无 | — |
| upstream / downstream interface | 无（degrade baseline） | — |

### Slot C / module `single_top_handle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carry_handle`(handle_bar + pivot_stub_{0,1})；内联 `handle_mount_foot_{i}`/`handle_mount_ear_{i}` | S6 / model.py:L319-L368 |
| internal joints | `bottom_to_handle`（REVOLUTE axis -X 0..100°） | S6 / model.py:L372-L385 |
| upstream interface | pivot 前墙 `(HANDLE_X,-hw(HANDLE_X),HANDLE_Z)`；stub 座 mount ear（allow_overlap handle↔bottom） | S6 / model.py:L511-L517 |
| downstream interface | 无（终端活动件） | — |

### Slot C / module `dual_side_handles`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`(handle_bar_{i} + 2 stub)，i=0,1；内联 `handle_mount_{i}_{j}` boss | S7 / model.py:L362-L385 |
| internal joints | `bottom_to_handle_{i}`（REVOLUTE axis ±X 0..90°，±Y 对称） | S7 / model.py:L390-L403 |
| upstream interface | pivot 两侧墙 `(0,±(hw(0)+standoff),HANDLE_Z)`；stub 座 boss（allow_overlap handle↔bottom） | S7 / model.py:L578-L584 |
| downstream interface | 无 | — |

### Slot C / module `d_ring_strap_loops`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `d_ring_{i}`(dring_ring_{i})，i=0,1；内联 `dring_mount_plate_{i}`/`dring_pivot_bar_{i}` | S8 / model.py:L343-L374 |
| internal joints | `bottom_to_d_ring_{i}`（REVOLUTE axis +X 0..170°） | S8 / model.py:L379-L392 |
| upstream interface | pivot 后 +Y 墙 `(dx,+hw(dx)+MOUNT_T,DRING_PIVOT_Z)`；ring 座 mount plate（allow_overlap dring↔bottom） | S8 / model.py:L528-L531 |
| downstream interface | 无 | — |

### Slot D / module `plain_plush_recess`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`red_interior` 为 bottom 内联 visual（A 决定轮廓） | S1 / model.py:L130-L146 |
| internal joints | 无 | — |
| upstream / downstream interface | 凹腔基底；所有其他 D 模块叠加于此红衬之上 | S1 / model.py:L188-L192 |

### Slot D / module `neck_cradle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`neck_cradle` 为 bottom 静态内联 visual（neck 端 saddle 块） | S9 / model.py:L252-L256 |
| internal joints | 无（静态） | — |
| upstream interface | 坐凹腔地板 z=WALL、neck 端 cx=-0.30；`expect_within` 含在 footprint | S9 / model.py:L408-L415 |
| downstream interface | 无 | — |

### Slot D / module `bow_spinner_clips`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bow_clip_{i}`(clip_arm_{i})，i=0,1；**lid** 内联 `clip_mount_{i}`/`bow_stick`/`bow_frog`/`bow_cradle_pad_{i}` | S10 / model.py:L275-L331 |
| internal joints | `lid_to_bow_clip_{i}`（REVOLUTE axis +Z 0..90°，**父=lid**） | S10 / model.py:L335-L348 |
| upstream interface | clip hub 座 lid 内 mount post（`expect_contact` clip↔mount）；假设刚性 violin-contour lid 腔 | S10 / model.py:L526-L548 |
| downstream interface | clip arm 捕 bow_stick（`expect_overlap` clip↔bow）；`expect_within` clip 含在 lid footprint | S10 / model.py:L518-L557 |

### Slot D / module `accessory_pocket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pocket_lid`(pocket_lid_panel)；**bottom** 内联 `pocket_box`/`pocket_pad`/`pocket_hinge_barrel` | S11 / model.py:L335-L365 |
| internal joints | `bottom_to_pocket_lid`（REVOLUTE axis -Y 0..120°，父=bottom） | S11 / model.py:L367-L378 |
| upstream interface | box 坐凹腔 lower-bout 端 POCKET_X=0.24；lid captured 在 barrel（allow_overlap） | S11 / model.py:L513-L517 |
| downstream interface | `expect_gap` pocket_lid↔box top（盖搭盒口） | S11 / model.py:L503-L510 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `shell_footprint` | enum | `violin_contour` / `rounded_dart_taper` / `rectangular_oblong` | `violin_contour` | choice | deterministic procedural sampler 选择；决定 outline helper + 半宽落座逻辑（插值 vs 固定） | Slot A 表 |
| `closure_mechanism` | enum | `hinge_plus_flip_latches` / `zipper_perimeter` / `buckle_straps` | `hinge_plus_flip_latches` | choice | sampler 选择；决定前 -Y 闭合 joint 拓扑 + 是否启用 `latch_count` | Slot B 表 |
| `carry_hardware` | enum | `none` / `single_top_handle` / `dual_side_handles` / `d_ring_strap_loops` | `none` | choice | sampler 选择；决定 carry joint 拓扑（0/1/2 REVOLUTE） | Slot C 表 |
| `interior_fitting` | enum | `plain_plush_recess` / `neck_cradle` / `bow_spinner_clips` / `accessory_pocket` | `plain_plush_recess` | choice | sampler 选择（`bow_spinner_clips` 受 §9 门控） | Slot D 表 |
| `latch_count` | int | {2, 3, 4} | 2 | conditional | **仅当 `closure_mechanism=hinge_plus_flip_latches`** 时为可变 multiplicity 轴；否则 N/A（见 §8） | S1/S12/S13 latch loop |
| `palette_style` | enum | `brown_tweed_red` / `black_shell_red_plush` / `brown_tan_plush` / `navy_grey` / `green_tweed_gold` / `carbon_black` | `brown_tweed_red` | choice | 每 seed 采样 colorway；仅改 material rgba，不改拓扑/尺寸/接口 | S1 mats L177-L179 + 跨样本配色观察 |
| `case_length_scale` | float | [0.90, 1.12] | 1.0 | independent | 长轴 `CASE_LEN` + outline `scale_x` 缩放；clamp | S1 `CASE_LEN` L43；outline scale_x L81 |
| `case_width_scale` | float | [0.90, 1.12] | 1.0 | independent | 宽轴 `HALF_W` + outline `scale_w` 缩放；clamp | S1 `HALF_W` L44；outline scale_w L82 |
| `shell_height_scale` | float | [0.85, 1.15] | 1.0 | independent | `SHELL_H` tub 高缩放；clamp | S1 `SHELL_H` L45 |
| `lid_depth_scale` | float | [0.85, 1.20] | 1.0 | independent | `LID_H` lid 壳深缩放；clamp | S1 `LID_H` L46 |
| `hinge_y` | float | derived | — | equation | `= HALF_W·case_width_scale`（oblong）或 `_half_width_at_x(0)` 缩放后值（violin/dart）；不独立采样 | S1 `HINGE_Y` L50 |
| `hinge_z` | float | derived | — | equation | `= SHELL_H·shell_height_scale`；lid 铰链 origin Z | S1 `HINGE_Z` L51 |
| `front_wall_y(x)` | float | derived | — | equation | `= -hw(x)`（A 决定 hw=插值 or 固定 HALF_W·width_scale）；latch/zipper/buckle/handle 落座 Y 全部派生于此 | §槽位图接口 |
| (—) | constraint | — | — | inequality | **细长身份**：`CASE_LEN·case_length_scale > 2·HALF_W·case_width_scale + 0.20`。违反时按比例回缩 `case_width_scale`。 | run_tests "case longer than wide" 全样本 |
| (—) | constraint | — | — | inequality | **凹槽不反转**：`RECESS_INSET + pad < HALF_W·case_width_scale`（红衬内缩轮廓 scale_w>0）。违反时回缩 `RECESS_INSET` 或抬高 `case_width_scale` 下限。 | S1 `_red_interior_solid` L133-135 |
| (—) | constraint | — | — | inequality | **内衬含在 footprint**：neck_cradle 半宽 / pocket(POCKET_WID, POCKET_LEN) / bow_len(0.72) 须含在缩放后 footprint − margin 0.005。违反时回缩内衬尺寸或拒绝。 | S9 L408-L415；S11；S10 `expect_within` |
| (—) | constraint | — | — | inequality | **latch 均布不出界**：N 个 `latch_positions` 均匀分布于 `[-CASE_LEN·len_scale/2+margin, +CASE_LEN·len_scale/2-margin]` 的前下 bout 段，相邻间距 ≥ 0.035（latch 宽 0.030 + 间隙）。N=4 时须仍满足。违反时收窄分布或降 N。 | S1/S12/S13 latch_positions |
| (—) | constraint | — | — | inequality | **carry × closure 共墙间隙（C=dual_side_handles × B≠none）**：-Y 侧 handle（x≈0 腰部）须与前墙 closure 硬件（latch/zipper teeth/buckle，x∈下 bout）X 向间隙 ≥ 0.02。违反时把 handle 保持腰部或缩 span。 | S7 HANDLE_CENTER_X=0；S5 STRAP_X 0.14/0.24 |

`palette_style` colorway 取值（rgba 仅作示意，下游模板落实；全部源自 S1 基线 tweed-棕/红-plush/chrome 及现实变体）：
- `brown_tweed_red`（= S1 基线）：shell tweed 棕 (0.20,0.17,0.13)、plush 红 (0.62,0.07,0.08)、latch chrome (0.78,0.79,0.82)。
- `black_shell_red_plush`：shell 黑 (0.06,0.06,0.07)、plush 红 (0.62,0.07,0.08)、chrome。
- `brown_tan_plush`：shell 棕皮 (0.30,0.18,0.10)、plush 驼黄 (0.74,0.62,0.42)、黄铜 (0.72,0.58,0.26)。
- `navy_grey`：shell 藏青 (0.10,0.13,0.22)、plush 灰 (0.45,0.46,0.50)、镍 (0.74,0.75,0.78)。
- `green_tweed_gold`：shell 军绿 tweed (0.16,0.22,0.13)、plush 金赭 (0.66,0.52,0.16)、黄铜。
- `carbon_black`：shell 碳纹 (0.10,0.10,0.12)、plush 黑 (0.10,0.08,0.08)、深枪灰 latch (0.30,0.31,0.34)。

## Multiplicity / Copy Logic

本模板有 **1 根 multiplicity 轴**：`latch_count`（前 -Y 边 flip latch 复制）。

- `count_param`：`latch_count`
- `N_range`：[2, 4]（本小类本轴产品域；测试偏小 N，产品全程 2..4。真实提琴硬盒鲜有 >4 latch，故上界封顶 4）。
- sampling domain（权重档）：N=2 高频（≈60%）、N=3 中频（≈30%）、N=4 稀有（≈10%）——小 N 偏多、尾部稀有；与 5★ 覆盖一致（parent=2 / var_3 / var_4）。
- copied object：`latch_i` part（lever plate + hook lip + pivot pin，per-i loop 建）+ 其 `bottom_to_latch_i` REVOLUTE joint。
- naming：`latch_{i}` / visual `latch_body_{i}` / joint `bottom_to_latch_{i}`，i=0..N-1。
- placement：沿前 -Y 下-bout rim 均布的 `latch_positions` X-list；pivot Y = `-hw(lx)+0.002`（坐在该 x 的前墙）；spread 从 N=2 的下-bout 对（0.10,0.30）随 N 增大扩到 N=4 的 upper→lower bout 跨度（-0.20,-0.05,0.10,0.25）。
- joint policy：每副本独立 REVOLUTE on bottom_shell，axis=(1,0,0)，0..80°，向外（-Y）翻；`allow_overlap` latch↔bottom（pin 座）+ latch↔lid（hook 扣）按副本复制。
- source/gating：**仅当 `closure_mechanism=hinge_plus_flip_latches` 时该轴启用**；`zipper_perimeter`（native count = 1 个 PRISMATIC pull + 固定 teeth 串）与 `buckle_straps`（native count = 固定 2 strap）**替换**了 flip latch，此时 `latch_count` N/A——sampler 在选定非 hinge closure 时不采样 `latch_count`（设为该 closure 的固定 native count，不复制 latch part）。见 §9 兼容矩阵。

## 拓扑多样性审计

总组合数：A × B × C × D = 3 × 3 × 4 × 4 = **144**（slot 组合）。计入 `latch_count` multiplicity（仅 B=hinge 时 N∈{2,3,4}）后，含 N 的拓扑组合 = `B=hinge`：3(N) × 4(C) × 4(D) = 48；`B=zipper`：1 × 4 × 4 = 16；`B=buckle`：1 × 4 × 4 = 16 → **80 个 joint-拓扑等价类**（A 为 footprint 几何轴，再 ×3 视觉变体）。


理由：joint 拓扑由 B/C/D + latch_count 共同驱动——Slot B 跨 **N×REVOLUTE latch / 1×PRISMATIC / 2×2-link REVOLUTE 链** 三种闭合拓扑，Slot C 跨 **0 / 1 / 2 / 2(后墙)** 四种 carry 拓扑，Slot D 跨 **无 joint / 静态 visual / 2×REVOLUTE(lid,Z) / 1×REVOLUTE(bottom,-Y)** 四种内衬拓扑，latch_count 改 latch joint 数。即便 A（footprint 几何，part 树同名不单独算拓扑等价类）与 palette/连续 scale 不计入，单 B×C×D×N 即达 80 distinct，远超 10 门槛。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG 独立加权采样四个 slot enum（A 3 选 1、B 3 选 1、C 4 选 1、D 4 选 1，默认近均匀，可对经典 `violin_contour`/`hinge_plus_flip_latches`/`plain_plush_recess` 略加权），**若 B=hinge 再加权采样 `latch_count`∈{2,3,4}**（小 N 偏多），再采样 `palette_style` 与 4 个 `independent` 连续 scale，按 `equation` 派生 `hinge_y`/`hinge_z`/`front_wall_y(x)` 等接口坐标，最后用 §7 inequality（细长身份、凹槽不反转、内衬含 footprint、latch 均布、carry×closure 共墙间隙）投影/回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定 `[(shell_footprint,…),(closure_mechanism,…),(carry_hardware,…),(interior_fitting,…)]` + （若 hinge）`latch_count`；连续 scale 不进 slot_choices。compatibility matrix 见下表，gating 在 `resolve_config` 解析（不留到 builder 失败）。`seed=0` 不特殊。无需 regression overrides（13 个 5★ 源覆盖全部模块，各格一次收敛）；若 sweep 暴露特定坏组合（如 §9 门控外漏）再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别约束封顶在 80（B×C×D×N joint-拓扑等价类上限）。本类别 slot 池中等（A 3 + B 3 + C 4 + D 4 + latch N 3），80 distinct 已显著 ≥ 推荐线，但 <300 是**类别固有约束**（提琴盒结构词汇表有限）而非建模缺陷；多样性进一步由 A（3 footprint 几何）× `palette_style`（6 colorway）× 连续 scale 谱共同提供视觉/比例多样性。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization（初版模板应含的关键连续 scale）：`case_length_scale [0.90,1.12] independent`、`case_width_scale [0.90,1.12] independent`、`shell_height_scale [0.85,1.15] independent`、`lid_depth_scale [0.85,1.20] independent`；派生 `hinge_y`/`hinge_z`/`front_wall_y(x)`（equation，随 A 与 width/height scale）。遵循连续尺寸采样契约：先采 independent → 派生 equation → 用 §7 inequality（细长身份 / 凹槽不反转 / 内衬含 footprint / latch 均布 / carry×closure 共墙间隙）投影回缩。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（lid 铰链 origin、closure/carry/interior 落座 Y 随 A 派生）、MatingContract（lid 鼻盖 rim、latch pin/hook 座、handle stub 座 ear、d-ring 座 plate、bow clip 座 post、pocket lid 座 barrel）或 multiplicity（latch_count 仅 hinge）。**lid 开合上限固定 180°**（折平 open-book 是身份不变量，不暴露为 scale）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→(latch_count if hinge)→C→D，独立加权 enum + latch N + palette + 4 连续 scale；compatibility gate 在 resolve_config | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | 多数 A×B×C×D 组合默认合法。门控：**(1) `latch_count` 仅 B=hinge**（B=zipper/buckle 时不采样 latch_count，用 closure native count）；**(2) `bow_spinner_clips`（D）需 lid 刚性 violin-contour 腔**——排除 D=bow_clips × B=zipper（软 padded 盖）与 D=bow_clips × A=rectangular_oblong（lid 腔几何差异），命中时 D fallback 到 `plain_plush_recess`（或 `neck_cradle`）；**(3) carry×closure 共墙间隙**（C=dual_side_handles × B≠none）走 §7 inequality 保 X 间隙，不可行则 C fallback `none`。 | 无 floating / 无穿模 / lid 折平不自碰 / 内衬含 footprint / latch 均布不出界 / 红 plush 凹槽不反转 |
| controlled local variation | 4 个 independent scale + 派生 hinge/front-wall 坐标；全部 clamp + 5 条 inequality 回缩 | 比例随机但 lid 铰链 origin、closure/carry/interior 落座、内衬含 footprint、细长身份不破 |
| regression overrides | none（13 个 5★ 源覆盖全模块，各格一次收敛） | — |
| random sweep | seeds 0-49 初轮（contract）、0-999 成熟审计（lid 折平 + 内衬 clearance + latch 均布 + 凹槽不反转） |、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A shell_footprint | 3 | yes | yes | violin / dart / oblong |
| B closure_mechanism | 3 | yes | yes | hinge+latch（带 multiplicity）/ zipper / buckle |
| C carry_hardware | 4 | yes | yes | none / top / dual-side / d-ring |
| D interior_fitting | 4 | yes | yes | plain / neck-cradle / bow-clips / pocket |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{violin_contour, rounded_dart_taper, rectangular_oblong}、B∈{hinge_plus_flip_latches, zipper_perimeter, buckle_straps}、C∈{none, single_top_handle, dual_side_handles, d_ring_strap_loops}、D∈{plain_plush_recess, neck_cradle, bow_spinner_clips, accessory_pocket}；若 B=hinge 含 `latch_count`∈{2,3,4}）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + latch N + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：latch_count 仅 hinge；bow_spinner_clips 需刚性 violin-contour lid（否则 fallback plain/neck_cradle）；dual_side_handles×closure 共墙间隙 gate 或 fallback none。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（case_length / case_width / shell_height / lid_depth）在 `resolve_config` clamp/派生；5 条 inequality（细长身份、凹槽不反转、内衬含 footprint、latch 均布、carry×closure 共墙间隙）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：lid 鼻盖 bottom rim（`allow_overlap` lid_exterior↔bottom_exterior）；latch pin/hook 座 bottom/lid（B=hinge）；zipper pull 座 track（`expect_overlap` XY，B=zipper）；strap 座 lid + buckle 座 catch_plate（`expect_contact`，B=buckle）；handle stub 座 mount ear/boss（C=top/dual）；d_ring 座 mount plate（C=d_ring）；bow clip 座 lid post（`expect_contact`，D=bow_clips）；pocket lid 座 hinge barrel（D=pocket）。
- 关键 joint type/axis/range：`bottom_to_lid` REVOLUTE -X 0..180°（折平身份，全候选）；`bottom_to_latch_i` REVOLUTE +X 0..80°（B=hinge，×N）；`bottom_to_zipper_pull` PRISMATIC +X ±0.18（B=zipper）；`lid_to_strap_i` REVOLUTE -X 0..60° + `strap_to_buckle_i` REVOLUTE -X 0..40°（B=buckle）；`bottom_to_handle(_i)` REVOLUTE ±X 0..90/100°（C）；`bottom_to_d_ring_i` REVOLUTE +X 0..170°（C=d_ring）；`lid_to_bow_clip_i` REVOLUTE +Z 0..90°（D=bow_clips）；`bottom_to_pocket_lid` REVOLUTE -Y 0..120°（D=pocket）。
- copied object 命名/placement：`latch_{i}`/`latch_body_{i}`/`bottom_to_latch_{i}`（i=0..N-1，前 -Y rim 均布，pivot Y=`-hw(lx)+0.002`）。
- 身份不变量：bottom_shell 细长（长 ≫ 宽）+ 模制红 plush 凹槽；lid `bottom_to_lid` 0..180° 折平 open-book（lid 升起→折到 +Y 侧→平躺，lid top < SHELL_H+LID_H+0.03）；前 -Y 边有闭合机构之一。
- B=zipper：断言无 `latch_0/latch_1` part（closure 替换）；B=buckle：断言 strap/buckle 随 lid 开合上升。

## Reject cases

- lid 缺 `bottom_to_lid` REVOLUTE 或不折平（180° 时 lid 仍站立 / 不落到 +Y 侧）——丢失 clamshell open-book 身份。
- bottom_shell 无模制红 plush 凹槽，或凹槽轮廓不随 A footprint 派生（红衬反转/穿出壳壁）。
- closure/carry/interior 落座 Y 未随 Slot A 的 `hw(x)`（violin/dart 插值 vs oblong 固定 HALF_W）派生 → latch/zipper/buckle/handle 悬空于错误前墙或漂浮在壳外。
- `latch_count` 被施加到 B=zipper / B=buckle（latch 与替换 closure 并存）——前 -Y 边重复硬件穿模 / 双重闭合机构。
- `bow_spinner_clips` 配 B=zipper 软 padded 盖或 A=rectangular_oblong → lid 腔几何不符，clip post/bow 悬空或穿出软盖。
- lid 折平 / 缩放后内衬（neck_cradle / pocket / bow_stick）超出 footprint 或穿出壳壁（`expect_within` 失败）。
- 细长身份违反：缩放后 `CASE_LEN·len_scale ≤ 2·HALF_W·width_scale + 0.20`（读成方砖而非细长琴盒）。
- captured-pin overlap 缺 element-scoped `allow_overlap`（lid 鼻盖 / latch pin / handle stub / d-ring pivot / bow clip post / pocket barrel）→ 误判穿模 reject 或子件脱离落座面悬空。
- 把 guitar/cello case、generic instrument/road flight case、或 Pelican 防水工具箱的特征（caster / rack rail / 泄压阀 / pick-pluck 泡棉 / butterfly road 锁）混进来（错类别，见 §11）。

## 与相邻类别的边界

- 不该混入：`guitar_case` / `cello_case`（更大乐器盒：guitar 是单大下-bout + 腰 + headstock 颈槽、~1.0–1.1 m；cello 更巨；提琴盒 ~0.80 m 且 violin 双-bout + C-bout 腰 + scroll/neck 收窄 silhouette，scale 与 body 轮廓不同）。
- 不该混入：generic `instrument_case` / road/flight case（矩形 road 箱：corner caster、recessed butterfly 锁、rack rail、铝包角、无乐器形 plush 模；本类别即便用 `rectangular_oblong` footprint 仍保留模制红 plush 提琴凹槽 + clamshell 折平红衬 + 可选 neck cradle，这是身份核心）。
- 不该混入：hard tool case（Pelican 式防水箱：pick-n-pluck 泡棉、pressure-relief 泄压阀、可挂锁 hasp、堆叠肋；非乐器内衬，无 violin/dart/oblong 乐器 footprint + 红 plush 提琴凹腔身份）。
- 不该混入：briefcase / suitcase（行李箱：顶提手 + 组合锁 + 拉杆/万向轮；提琴盒以 clamshell 折平到 180° open-book + 乐器 plush 凹槽为定义，开合语义不同）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`bottom_shell` tub + `lid` 浅壳 + 红衬 + `bottom_to_lid` REVOLUTE 0..180° 折平核心 + `_*_half_points/_half_width_at_x/_*_outline_wire` outline helper 家族在全 13 源一致，可抽公共 helper（保留 `# adopted: <source>` 注释）。Slot A 三模块各有自己的 outline solid 构建器（`_violin_outline_wire`/`_dart_outline_wire` 样条 vs `_rounded_rect_solid` fillet），按 `shell_footprint` 分派；**hw(x) 半宽函数也随 A 切换**（violin/dart 插值 vs oblong 固定 HALF_W），下游所有落座 Y 必须从 resolved `hw()` 取值，不可硬编码。
- captured-pin overlap 须 element-scoped `allow_overlap`：lid_exterior↔bottom_exterior（全候选）；latch↔bottom + latch↔lid（B=hinge，按 N 复制）；zipper_pull↔track + zipper_pull↔bottom（B=zipper）；strap↔bottom/lid + buckle↔bottom/strap（B=buckle）；handle↔bottom（C=top/dual）；d_ring↔bottom（C=d_ring）；bow_clip↔lid post/bow（D=bow_clips）；pocket_lid↔barrel（D=pocket）。参考各源 run_tests 的 `allow_overlap`/`expect_*` 块。
- Slot B 互斥 gate：选定 `closure_mechanism` 后只发射对应子机构 part/joint；**`latch_count` 仅在 B=hinge 时进入 sampler 与 slot_choices**（zipper/buckle 用固定 native count，不复制 latch）。
- D=bow_spinner_clips 门控：`resolve_config` 校验 A∈{violin_contour, rounded_dart_taper} 且 B∈{hinge, buckle}（刚性 lid 腔）；否则该 seed 的 D fallback 到 `plain_plush_recess`（compatibility matrix fallback 路径，与源 map 排除项一致）。
- C=dual_side_handles × B≠none：`resolve_config` 校验 -Y 侧 handle（腰部 x≈0）与前墙 closure 硬件（latch/zipper teeth/buckle，x∈下 bout）X 向间隙 ≥0.02；不可行则 C fallback `none`。
- lid 开合上限固定 180°（折平 open-book 身份），不暴露为 scale；`shell_height_scale`/`lid_depth_scale` 改变 hinge origin Z 与 lid 厚但 q=180° 折平断言（lid_top < SHELL_H·h + LID_H·d + 0.03）须随缩放更新阈值。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / D + core | `violin_contour` / `hinge_plus_flip_latches` / `none` / `plain_plush_recess` | `rec_hardshell-violin-case-with-a-hinged-clamshell-li_20260605_161837_673361_7727811a` | `L54-L171`(outline+shell+lid helper)、`L181-L240`(bottom+lid+`bottom_to_lid`)、`L242-L278`(latch loop, multiplicity N=2)、`L195-L201`(hinge knuckle) | 四 slot 基线 + lid 折平核心 + latch multiplicity 源 |
| S2 | A | `rounded_dart_taper` | `rec_violin_case_var_outline_dart` | `L59-L122`(dart outline)、`L125-L179`(shell+lid)、`L315-L327`(dart 断言) | dart footprint（无 C-bout 腰，插值半宽） |
| S3 | A | `rectangular_oblong` | `rec_violin_case_var_outline_rectangular` | `L49`、`L55-L129`(`_rounded_rect_solid`+shell+lid)、`L153-L158`(固定 HALF_W)、`L260-L267` | oblong footprint（rect+fillet 构建法，固定半宽落座） |
| S4 | B | `zipper_perimeter` | `rec_violin_case_var_closure_zipper` | `L50-L57`、`L159-L227`(padding/track/tooth/pull helper)、`L253-L286`(内联)、`L326-L350`(`zipper_pull` PRISMATIC)、`L404-L515` | 软拉链 PRISMATIC slider，删 latch |
| S5 | B | `buckle_straps` | `rec_violin_case_var_closure_buckle_straps` | `L52-L68`、`L182-L235`(strap/buckle helper)、`L270-L282`(catch plate)、`L321-L376`(strap/buckle 2-link REVOLUTE 链) | 皮带→金属扣 2-link 链，删 latch |
| S6 | C | `single_top_handle` | `rec_violin_case_var_carry_top_handle` | `L54-L60`、`L183-L201`(`_handle_bar_points`)、`L319-L385`(mount+`carry_handle`+`bottom_to_handle` REVOLUTE) | 单顶提手 REVOLUTE |
| S7 | C | `dual_side_handles` | `rec_violin_case_var_carry_dual_side_handles` | `L57-L65`、`L188-L240`(`_handle_*` helper)、`L355-L403`(handle loop + `bottom_to_handle_{i}` REVOLUTE) | 双侧 contour 提手 ×2 REVOLUTE |
| S8 | C | `d_ring_strap_loops` | `rec_violin_case_var_carry_shoulder_strap_loops` | `L54-L64`、`L187-L222`(`_d_ring_*` helper)、`L338-L392`(D-ring loop + `bottom_to_d_ring_{i}` REVOLUTE) | 后墙肩带 D 形吊环 ×2 REVOLUTE |
| S9 | D | `neck_cradle` | `rec_violin_case_var_interior_neck_cradle` | `L149-L204`(`_neck_cradle_solid`)、`L252-L256`(静态 visual)、`L408-L415` | neck 端静态悬挂 cradle 块（无 joint） |
| S10 | D | `bow_spinner_clips` | `rec_violin_case_var_interior_bow_clips` | `L53-L62`、`L185-L198`(`_bow_clip_arm_solid`)、`L275-L315`(post/bow/pad 内联)、`L318-L348`(`bow_clip_{i}` + `lid_to_bow_clip_{i}` REVOLUTE +Z) | lid 内 spinner bow 夹 ×2 REVOLUTE（绕 Z，父=lid） |
| S11 | D | `accessory_pocket` | `rec_violin_case_var_interior_accessory_pocket` | `L53-L61`、`L184-L222`(pocket helper)、`L335-L378`(box/pad/barrel 内联 + `pocket_lid` + `bottom_to_pocket_lid` REVOLUTE -Y) | 带盖配件盒 1×REVOLUTE（绕 -Y，父=bottom） |
| S12 | B(mult) | `hinge_plus_flip_latches` N=3 | `rec_violin_case_var_latch_count_3` | `L249`(`latch_positions=(0.02,0.16,0.30)`)、`L250-L279`(latch loop) | latch_count multiplicity N=3 |
| S13 | B(mult) | `hinge_plus_flip_latches` N=4 | `rec_violin_case_var_latch_count_4` | `L249`(`latch_positions=(-0.20,-0.05,0.10,0.25)`)、`L250-L279`、`L294-L368`(range(4) 断言) | latch_count multiplicity N=4（产品域上界） |
