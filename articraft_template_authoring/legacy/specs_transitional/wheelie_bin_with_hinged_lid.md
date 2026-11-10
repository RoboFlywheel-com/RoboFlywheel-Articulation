# Wheelie Bin With Hinged Lid Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wheelie_bin_with_hinged_lid` |
| template path | `agent/templates/wheelie_bin_with_hinged_lid.py` |
| test path | `tests/agent/test_wheelie_bin_with_hinged_lid_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 28 |
| read_count | 7 |
| read_scope | 28 个 5 星全部用 grep 抽取了 part 列表 / 关节(name,type,parent,child,axis,limit) / shell-wheel 构造方式 / bbox 量级；其中 7 个(0002, e9ff29, e438ce, cbb9f5, 94165, 72bbed, 27973, b14d66 中选读 7 个跨结构全谱)按行精读以采纳可复用源码块 |
| source_index_policy | 仅索引被采纳的可复用片段；side-layout(lid 沿 +X、轴 ±Y)与 rear-up-layout(lid 沿 +Y、轴 ±X)视为同一 `lid_layout` 连续/离散开关而非两套模板；lock_tab 二级闩锁 DOF 视为 gated 可选件，不并入默认 1-lid-2-wheel 主干 |

## 核心身份
带铰链盖的轮式垃圾桶(wheelie bin)：必须包含一个开口向上的中空 bin body、一片覆盖开口的 full-width lid(单 REVOLUTE 后缘铰链)、以及一对绕后轴滚动的 wheels(各一个 CONTINUOUS joint)。盖一定从后缘上翻、轮一定沿同一水平宽度轴转。它不是无盖储物箱(必须有铰链盖)，也不是手推车/拖车(轮只滚动不转向、桶体本身落地不靠轮支撑姿态)，更不是带抽屉/对开门的柜体(开口靠单片上翻盖闭合)。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_wheelie_bin_with_hinged_lid_0002` | `data/records/rec_wheelie_bin_with_hinged_lid_0002/revisions/rev_000001/model.py:L25-L86` | `_axis_rpy` / `_add_cylinder_visual` / `_add_bolt_head` / `_add_wheel_lugs` 这类圆柱朝向 + 螺栓 + 轮缘螺纹 helper |
| S2 | `rec_wheelie_bin_with_hinged_lid_0002` | `data/records/rec_wheelie_bin_with_hinged_lid_0002/revisions/rev_000001/model.py:L112-L276` | prim-box 桶身(floor + 四壁 + 四 rim + 加强 ribs + axle pods/clamps + hinge saddles)与 inertial |
| S3 | `rec_wheelie_bin_with_hinged_lid_0002` | `data/records/rec_wheelie_bin_with_hinged_lid_0002/revisions/rev_000001/model.py:L278-L375` | 独立 FIXED `axle` part(shaft+spindle+collar+mount tab)与独立 FIXED `hinge_pin` part(rod+end cap) |
| S4 | `rec_wheelie_bin_with_hinged_lid_0002` | `data/records/rec_wheelie_bin_with_hinged_lid_0002/revisions/rev_000001/model.py:L560-L603` | `body_to_axle`/`body_to_hinge_pin` FIXED + `body_to_lid` REVOLUTE + `axle_to_*_wheel` CONTINUOUS 关节写法 |
| S5 | `rec_wheelie_bin_with_hinged_lid_e9ff29d8c8fa4ee6bffd7525ff3080a8` | `data/records/rec_wheelie_bin_with_hinged_lid_e9ff29d8c8fa4ee6bffd7525ff3080a8/revisions/rev_000001/model.py:L27-L94` | `LatheGeometry` 轮胎断面 profile + `_add_wheel_visuals`(shell/hub/cap/inner boss/index) |
| S6 | `rec_wheelie_bin_with_hinged_lid_e9ff29d8c8fa4ee6bffd7525ff3080a8` | `data/records/rec_wheelie_bin_with_hinged_lid_e9ff29d8c8fa4ee6bffd7525ff3080a8/revisions/rev_000001/model.py:L113-L274` | 微倾斜壁 prim-box 桶身 + 后 hinge bridge/connector + 前后/侧 axle saddle&bracket |
| S7 | `rec_wheelie_bin_with_hinged_lid_e438ce6ad9a745d08fc37aea0bcb2a50` | `data/records/rec_wheelie_bin_with_hinged_lid_e438ce6ad9a745d08fc37aea0bcb2a50/revisions/rev_000001/model.py:L25-L122` | `MeshGeometry` rounded-rect 双 loop 桥接中空桶壳(`_build_bin_shell_mesh`)+ Lathe 轮胎 |
| S8 | `rec_wheelie_bin_with_hinged_lid_e438ce6ad9a745d08fc37aea0bcb2a50` | `data/records/rec_wheelie_bin_with_hinged_lid_e438ce6ad9a745d08fc37aea0bcb2a50/revisions/rev_000001/model.py:L407-L438` | wheels-direct-to-body 的 `body_to_lid`(REVOLUTE) + `body_to_left/right_wheel`(CONTINUOUS)写法 |
| S9 | `rec_wheelie_bin_with_hinged_lid_cbb9f5bd1d044f56a9cb96f25f75d256` | `data/records/rec_wheelie_bin_with_hinged_lid_cbb9f5bd1d044f56a9cb96f25f75d256/revisions/rev_000001/model.py:L89-L114` | 参数化 `TireGeometry`/`WheelGeometry`(carcass/tread/groove/rim/hub/spokes/bore)轮胎+轮辋 |
| S10 | `rec_wheelie_bin_with_hinged_lid_cbb9f5bd1d044f56a9cb96f25f75d256` | `data/records/rec_wheelie_bin_with_hinged_lid_cbb9f5bd1d044f56a9cb96f25f75d256/revisions/rev_000001/model.py:L208-L295` | 多份 wheel 循环(`for ...: model.part(f"wheel_{suffix}")`)+ 独立 `lock_tab` 二级 REVOLUTE 闩锁件 |
| S11 | `rec_wheelie_bin_with_hinged_lid_72bbed106fa3404192b6be926d6ad5e8` | `data/records/rec_wheelie_bin_with_hinged_lid_72bbed106fa3404192b6be926d6ad5e8/revisions/rev_000001/model.py:L50-L78` | cadquery `loft`+`shell`+`fillet` 锥形中空桶壳与 fillet 倒角 full-width lid panel |
| S12 | `rec_wheelie_bin_with_hinged_lid_27973dc094e245dcaf418ffa13f92ff6` | `data/records/rec_wheelie_bin_with_hinged_lid_27973dc094e245dcaf418ffa13f92ff6/revisions/rev_000001/model.py:L71-L203` | 多 section lofted-mesh 桶身 + `ExtrudeGeometry.from_z0` rounded-rect lid + 桶内嵌 hinge_pin/knuckle/leaf |
| S13 | `rec_wheelie_bin_with_hinged_lid_b14d66b669284a948a29097abda2724f` | `data/records/rec_wheelie_bin_with_hinged_lid_b14d66b669284a948a29097abda2724f/revisions/rev_000001/model.py:L53-L104` | 三角函数派生 side/front tilt 倾斜壁 + `_add_bolted_plate` 螺栓适配板 helper |

## 槽位 + 候选模块表

### Slot 1：body_shell（桶身）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `prim_box_walls` | S2 (0002) | `model.py:L112-L276` | ✅ seed=0 | floor + 四面 box 壁 + 四条 rim box + 侧/前加强 rib + 后 axle pod，全部 Box 拼接，最稳健 |
| `mesh_rrect_loft_shell` | S7 (e438ce) | `model.py:L25-L122` | | `MeshGeometry` 上下两 rounded-rect loop 桥接成单片中空壳，molded HDPE 观感，外加 rim rail |
| `cadquery_loft_shell` | S11 (72bbed) | `model.py:L50-L78` | | cadquery `rect→loft→faces(">Z").shell(-t)` 锥形中空桶 + `edges("|Z").fillet`，再 union 重 rim |
| `tilted_box_walls` | S13 (b14d66) | `model.py:L53-L104,L194-L244` | | 用 `atan`/`sin` 派生 side/front tilt，四壁带外扩锥度的 Box，上小下大梯形桶 |

### Slot 2：lid（盖板）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `box_panel_skirt` | S2 (0002) | `model.py:L376-L448` | ✅ seed=0 | Box 顶板 + 左右/前 skirt box + center/front stiffener + grip ridge + 铰链 plate/knuckle |
| `extrude_rrect_panel` | S12 (27973) | `model.py:L162-L203` | | `ExtrudeGeometry.from_z0(rounded_rect_profile,...)` 圆角盖板 + 前 grip lip + 顶 ribs + 铰链 knuckle/leaf |
| `cadquery_fillet_panel` | S11 (72bbed) | `model.py:L65-L78,L146-L170` | | cadquery `box.edges("|Z").fillet` 单片盖板，local origin 落在铰链线，配 front lip + 铰链 tongue/knuckle |

### Slot 3：wheel_pair（一对轮）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `param_tire_wheel` | S9 (cbb9f5) | `model.py:L89-L114` | ✅ seed=0 | 参数化 `TireGeometry`(carcass/tread/groove/sidewall/shoulder) + `WheelGeometry`(rim/hub/spokes/bore)，最真实 |
| `lathe_profile_wheel` | S5 (e9ff29) | `model.py:L27-L94` | | `LatheGeometry` 轮胎断面 profile 旋转成型 + Cylinder hub/cap/inner-boss + 索引块 |
| `primitive_cyl_wheel` | S1 (0002) | `model.py:L474-L558` | | tire/hub_disc/hub_cap/inner_boss 全用 Cylinder 叠 + `_add_wheel_lugs` 螺纹环，最轻量 |

### Slot 4：wheel_axle_topology（轮-轴拓扑）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `wheels_on_body` | S8 (e438ce) | `model.py:L407-L438` | ✅ seed=0 | 轴是 body 的 visual(`rear_axle_tube`+bracket+collar)，两轮各自 `body_to_*_wheel` CONTINUOUS 直挂 body |
| `fixed_axle_part` | S3+S4 (0002) | `model.py:L278-L375,L584-L603` | | 独立 FIXED `axle` part(shaft+spindle+collar) `body_to_axle`，两轮 `axle_to_*_wheel` 挂在 axle 上 |
| `loop_wheels_on_body` | S10 (cbb9f5) | `model.py:L208-L222` | | `for y,suffix in (...): model.part(f"wheel_{suffix}")` 循环建轮 + 单循环体内 CONTINUOUS 直挂 body |

### Slot 5：hinge_interface（铰链界面）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `baked_knuckle_plus_pin` | S12 (27973) | `model.py:L141-L160,L191-L203` | ✅ seed=0 | body 与 lid 上各嵌 knuckle Cylinder + leaf box，hinge pin 作为 body 内细 Cylinder visual 穿过 knuckle |
| `separate_hinge_pin_part` | S3+S4 (0002) | `model.py:L342-L375,L567-L573` | | 独立 FIXED `hinge_pin` part(全宽 rod + 端盖)，`body_to_hinge_pin` FIXED，lid knuckle 抱住它 |
| `cheek_bracket_frame` | S6 (e9ff29) | `model.py:L245-L274` | | 后 hinge bridge box + 左右 hinge connector/cheek 框住 lid hinge leaf，无独立销，knuckle 嵌 lid |

### Slot 6：lid_extras（盖附件 / 可选 DOF）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `front_grip_lip` | S2 (0002) | `model.py:L395-L418` | ✅ seed=0 | 仅前缘 grip ridge / stiffener，FIXED 在 lid 上，无附加 DOF（默认） |
| `none_plain` | S11 (72bbed) | `model.py:L146-L170` | | 光板盖 + 少量 rib，无 grip lip、无附加件，最简 |
| `lock_tab_latch` | S10 (cbb9f5) | `model.py:L269-L295` | | 独立 `lock_tab` part(pivot barrel + plate + pull tab) 经第二个 REVOLUTE 挂 body 前缘，gated 二级 DOF |

## 槽位图（slot graph）
```
pattern = mixed
（线性身份链 body→lid + 并列双轮 children + 可选 gated 件）

                       body (Slot1: body_shell)
                         |
        +----------------+----------------------+--------------------+
        | REVOLUTE                               | CONTINUOUS x2      | FIXED (gated)
        v (rear hinge, axis ±X 或 ±Y)            v (axis = width)    v
   lid (Slot2)                          wheel_L / wheel_R (Slot3)   [axle part]
        |                                  ^  (Slot4 决定 parent:    (仅 fixed_axle_part)
        | FIXED                            |   body 或 axle part)
        v                                  |
  [Slot5 hinge_interface 件:               +--- Slot4: wheels_on_body / fixed_axle_part / loop_wheels_on_body
   baked pin | 独立 hinge_pin(FIXED) | cheek bracket]
        |
        | (Slot6)
        v
  front_grip_lip / none / [lock_tab → 第二 REVOLUTE 挂 body]
```
- 身份链恒为 `body -> lid`(REVOLUTE)。
- 双轮恒为并列 children，parent 视 Slot4 为 `body` 或独立 `axle`。
- Slot4=`fixed_axle_part` 时额外引入一个 FIXED `axle` 件；Slot5=`separate_hinge_pin_part` 时额外引入一个 FIXED `hinge_pin` 件；Slot6=`lock_tab_latch` 时额外引入一个 REVOLUTE `lock_tab` 件。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `body` / `bin_body` / `bin` | 开口向上中空桶身，含底、壁、上 rim、加强 ribs、后轴硬件、铰链 saddle/knuckle；落地 root | `body_style`, `bin_top_width`, `bin_top_depth`, `bin_height`, `wall_thickness`, `taper` | S2 / S6 / S7 / S11 / S12 / S13 |
| `lid` | full-width 盖板，含 skirt/lip、ribs/stiffener、铰链 knuckle/leaf；覆盖开口 | `lid_style`, `lid_thickness`, `lid_overhang`, `rib_count` | S2 / S11 / S12 |
| `left_wheel` / `right_wheel` / `wheel_{i}` | 一对滚轮(tire + rim/hub)，绕后轴水平宽度轴滚动 | `wheel_style`, `wheel_radius`, `wheel_width`, `wheel_track` | S1 / S5 / S9 / S10 |
| `axle` / `rear_axle` | 可选独立后轴件(shaft + spindle + collar + mount tab)，FIXED 到 body | `axle_topology`, `axle_radius`, `axle_z` | S3 |
| `hinge_pin` | 可选独立全宽铰链销(rod + 端盖)，FIXED 到 body，被 lid knuckle 抱住 | `hinge_interface`, `pin_radius` | S3 |
| `lock_tab` | 可选前缘闩锁件(pivot barrel + plate + pull tab)，第二个 REVOLUTE | `has_lock_tab`, `latch_range` | S10 |
| `axle_brackets` / `hinge_saddles` / `ribs` / `bolts` / `grip_lip` | FIXED 装饰/承力硬件，挂在 body/lid 上，从尺寸派生 | `detail_level` | S2 / S6 / S12 / S13 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `body_to_lid` / `lid_hinge` | revolute | body | lid | `(±1,0,0)` 或 `(0,±1,0)` | `[0.0, 1.35~2.2]` rad | 主关节：盖绕后缘水平轴上翻；轴随 `lid_layout` 选向 | S4 / S8 / S12 |
| `body_to_left_wheel` / `axle_to_left_wheel` | continuous | body 或 axle (Slot4) | left_wheel | `(±1,0,0)` 或 `(0,±1,0)`(与 lid 轴族一致) | unlimited | 左轮滚动，轴 = 桶宽方向 | S4 / S8 |
| `body_to_right_wheel` / `axle_to_right_wheel` | continuous | body 或 axle (Slot4) | right_wheel | 同左轮 | unlimited | 右轮滚动，与左轮共轴 | S4 / S8 |
| `body_to_axle` | fixed | body | axle | n/a | n/a | 仅 Slot4=`fixed_axle_part`：独立轴件固定到桶 | S4 |
| `body_to_hinge_pin` | fixed | body | hinge_pin | n/a | n/a | 仅 Slot5=`separate_hinge_pin_part`：全宽销固定到桶 | S4 |
| `body_to_lock_tab` | revolute (gated) | body | lock_tab | `(0,±1,0)` | `[-0.35, 1.3]` rad | 仅 Slot6=`lock_tab_latch`：前缘闩锁二级 DOF | S10 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `body_style` | enum | `prim_box_walls` / `mesh_rrect_loft_shell` / `cadquery_loft_shell` / `tilted_box_walls` | `prim_box_walls` | drives Slot1 桶壳构造 | S2 / S7 / S11 / S13 |
| `lid_style` | enum | `box_panel_skirt` / `extrude_rrect_panel` / `cadquery_fillet_panel` | `box_panel_skirt` | drives Slot2 盖板构造 | S2 / S12 / S11 |
| `wheel_style` | enum | `param_tire_wheel` / `lathe_profile_wheel` / `primitive_cyl_wheel` | `param_tire_wheel` | drives Slot3 轮构造 | S9 / S5 / S1 |
| `axle_topology` | enum | `wheels_on_body` / `fixed_axle_part` / `loop_wheels_on_body` | `wheels_on_body` | drives Slot4：是否独立 axle 件、轮 parent | S8 / S3 / S10 |
| `hinge_interface` | enum | `baked_knuckle_plus_pin` / `separate_hinge_pin_part` / `cheek_bracket_frame` | `baked_knuckle_plus_pin` | drives Slot5：是否独立 hinge_pin 件 | S12 / S3 / S6 |
| `lid_extras` | enum | `front_grip_lip` / `none_plain` / `lock_tab_latch` | `front_grip_lip` | drives Slot6；`lock_tab_latch` 引入第二 REVOLUTE | S2 / S11 / S10 |
| `lid_layout` | enum | `rear_up_x`(轴 ±X、盖沿 +Y) / `side_y`(轴 ±Y、盖沿 +X) | `rear_up_x` | 决定 lid/wheel 共同轴族方向 | S2 / S12 |
| `bin_top_width` | float | `0.55-0.66` | sampled | 桶上口宽(X)，wheel_track 由此派生 | S2 / S6 / S11 |
| `bin_top_depth` | float | `0.66-0.78` | sampled | 桶上口深(Y) | S2 / S11 / S12 |
| `bin_height` | float | `0.80-0.92` | sampled | 桶壁高，hinge_z ≈ floor_z + bin_height | S2 / S6 / S13 |
| `taper` | float | `0.0-0.16` | sampled | 上口比下口外扩量(loft/tilt 用) | S11 / S13 |
| `wheel_radius` | float | `0.085-0.160` | sampled | 轮半径，axle_z ≈ wheel_radius | S5 / S9 / S12 |
| `wheel_track` | float | derived | derived | `~bin_top_width + 2*wheel_width`，两轮对称分布 | S2 / S12 |
| `lid_hinge_upper` | float | `1.35-2.2` rad | sampled | 盖开角上限 | 全样本 |

## 拓扑多样性审计
- 每槽候选数：Slot1=4，Slot2=3，Slot3=3，Slot4=3，Slot5=3，Slot6=3。
- total_combinations = 4 × 3 × 3 × 3 × 3 × 3 = **972**。

| slot | candidate_count |
|---|---|
| Slot1 body_shell | 4 |
| Slot2 lid | 3 |
| Slot3 wheel_pair | 3 |
| Slot4 wheel_axle_topology | 3 |
| Slot5 hinge_interface | 3 |
| Slot6 lid_extras | 3 |

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 存在 body + lid + 恰好 2 个 wheel；存在 1 个 `body->lid` REVOLUTE 与 2 个 wheel CONTINUOUS |
| primary joint count | 默认主关节 = 1 lid REVOLUTE + 2 wheel CONTINUOUS；仅 `lid_extras=lock_tab_latch` 才追加第二个 REVOLUTE |
| lid axis | lid 铰链轴为水平宽度方向(`±X` 或 `±Y`)，且与两轮轴同族；lower≈0，upper∈[1.35, 2.2] |
| wheel coaxial | 两轮 CONTINUOUS 共轴、轴向 = 桶宽方向、左右对称(track 由桶宽派生) |
| axle topology | `fixed_axle_part` 时存在 FIXED `body->axle` 且两轮 parent=axle；否则两轮 parent=body 且轴是 body visual |
| hinge interface | `separate_hinge_pin_part` 时存在 FIXED `body->hinge_pin`；lid knuckle 必须抱住销/cheek，hinge 轴与销同线 |
| lid coverage | 闭合位 lid 在 XY 投影覆盖桶开口(min_overlap≥0.3)，且盖底坐落在前 rim 上方(小 gap、无穿模) |
| lid opens up | 开到 upper 时 lid 前缘 AABB 顶 Z 显著抬升(>0.2m)且不与桶体非预期重叠 |
| body grounding | body 落地(floor 在 z≈0 附近)，轮触地支撑姿态，桶身不漂浮 |
| no floating | wheels/axle/hinge_pin/lock_tab/ribs/bolts/grip_lip 全部 attached 或 FIXED；无悬空件 |

## Reject cases
- 缺少铰链盖(只有开口桶 + 轮)，或盖不是 REVOLUTE(被做成 FIXED/PRISMATIC/滑盖)。
- 缺少轮，或轮用 REVOLUTE 限位/PRISMATIC 而非 CONTINUOUS 滚动。
- lid 铰链轴竖直(±Z)或与两轮轴不同族，导致盖侧开/轮转向。
- 两轮不共轴、不对称，或 track 与桶宽脱节(轮飞在桶外或埋进桶里无支撑)。
- `fixed_axle_part` 声称独立轴件却把两轮直接挂 body(或反之)，axle/wheel parent 关系自相矛盾。
- lid 闭合却不覆盖开口(悬在半空 / 投影不重叠 / 穿透桶底)。
- hinge_pin / lock_tab / axle / ribs / bolts 悬空，不与 body 或 lid 接触固定。
- 把对开门柜 / 抽屉 / 无盖储物箱 / 转向脚轮手推车硬塞进本模板。

## 与相邻类别的边界
- vs `open_storage_bin`(无盖储物箱)：本类必须有可动 REVOLUTE 铰链盖；无盖即出界。
- vs `cabinet_with_doors` / `drawer_unit`：本类开口靠单片后缘上翻盖闭合，而非对开门 / 抽出抽屉。
- vs `hand_cart` / `trolley`：本类轮只 CONTINUOUS 滚动、不转向，桶体自身落地承重；带转向脚轮 / 桶体悬于轮架上即出界。
- vs `pedal_bin`(脚踏垃圾桶)：本类开盖默认靠 lid 直接 REVOLUTE，不建脚踏-连杆-盖联动链；如需脚踏请单独 gate，不混入默认主干。
- vs `dumpster`(大型装卸料箱)：本类是 wheelie bin 量级(≈0.55–0.66 宽、0.8–0.95 高)，不是带 tipping/lift 接口的大型钢制料箱。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；28 个 5 星全 grep、7 个精读；身份恒为 body+lid(1 REVOLUTE)+2 wheel(2 CONTINUOUS)，无 no-wheel 变体；待人工 review |
