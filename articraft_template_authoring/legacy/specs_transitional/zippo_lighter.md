# Zippo Lighter Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `zippo_lighter` |
| template path | `agent/templates/zippo_lighter.py` |
| test path | `tests/agent/test_zippo_lighter_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 21 |
| read_count | 9 |
| read_scope | 9 个样本完整逐行精读（覆盖 3/4/5 part、FIXED/PRISMATIC/无 insert、cadquery shell / 纯 primitive / KnobGeometry 三种构造、Y 轴与 Z 轴 hinge、有无 cam mimic 的全部结构区间）；其余 12 个 5 星样本用 grep 抽取 part 名 / joint 类型与 parent-child / 构造手段（cadquery vs mesh_from_geometry vs primitive）/ 是否有 Mimic，已纳入下方拓扑分布统计 |
| source_index_policy | 仅索引被采纳为候选模块来源的可复用片段；非默认的 PRISMATIC-insert 与 cam-lever 作为 gated/optional 分支处理，不强行混进最小默认拓扑 |

## 核心身份
Zippo 式翻盖防风打火机：必须包含一个落地的 lower case（含中空 fuel cavity）、一个靠后边铰链翻起的 flip-top lid（REVOLUTE）、一个 chimney/insert（带 wind guard 与 wick），以及一个 CONTINUOUS 旋转的 spark/striker wheel（拇指轮）。核心 DOF 是 lid 翻盖 + spark wheel 旋转两个。它不是普通带盖盒子（必须有打火轮与防风烟囱），也不是 butane 气体打火机（无气阀/无压电按钮、燃料靠 wick 而非喷嘴）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_zippo_lighter_bea7f175043c4792a9c0a6ae7026aae3` | `data/records/rec_zippo_lighter_bea7f175043c4792a9c0a6ae7026aae3/revisions/rev_000001/model.py:L56-L147` | cadquery shell helpers：`_lower_shell_shape` 中空壳 + `_cap_shape` 翻盖 + `_insert_shape` 烟囱打孔 + `_wheel_shape` 开槽轮 |
| S2 | `rec_zippo_lighter_bea7f175043c4792a9c0a6ae7026aae3` | `data/records/rec_zippo_lighter_bea7f175043c4792a9c0a6ae7026aae3/revisions/rev_000001/model.py:L149-L208` | 3-part fused 拓扑：body(壳+insert+wick) / cap / wheel，FIXED 隐式融合 + REVOLUTE(Y) + CONTINUOUS(Y) |
| S3 | `rec_zippo_lighter_0215496335c84a629660993cbecc92e0` | `data/records/rec_zippo_lighter_0215496335c84a629660993cbecc92e0/revisions/rev_000001/model.py:L113-L185` | `_shell_box` 通用开口壳 helper + 独立 chimney insert shape + 多边形轮 shape（4-part） |
| S4 | `rec_zippo_lighter_0215496335c84a629660993cbecc92e0` | `data/records/rec_zippo_lighter_0215496335c84a629660993cbecc92e0/revisions/rev_000001/model.py:L223-L252` | FIXED chimney insert + CONTINUOUS wheel(parent=chimney) + REVOLUTE lid 的 4-part 关节写法 |
| S5 | `rec_zippo_lighter_a9599c7af31e48b895173f4700f83569` | `data/records/rec_zippo_lighter_a9599c7af31e48b895173f4700f83569/revisions/rev_000001/model.py:L71-L137` | 纯 primitive：body 由 5 个 Box 壁 + 4 个 corner Cylinder + hinge pad/knuckle 组成（无 cadquery） |
| S6 | `rec_zippo_lighter_a9599c7af31e48b895173f4700f83569` | `data/records/rec_zippo_lighter_a9599c7af31e48b895173f4700f83569/revisions/rev_000001/model.py:L296-L350` | cam lever part（hub+arm+toe）+ REVOLUTE cam 关节 + `Mimic(joint="lid_hinge")` |
| S7 | `rec_zippo_lighter_351666d755e346a297fba8c95a854988` | `data/records/rec_zippo_lighter_351666d755e346a297fba8c95a854988/revisions/rev_000001/model.py:L150-L235` | PRISMATIC sliding insert（`shell_to_insert` 竖直滑出）+ insert 上的 striker fork/axle boss |
| S8 | `rec_zippo_lighter_351666d755e346a297fba8c95a854988` | `data/records/rec_zippo_lighter_351666d755e346a297fba8c95a854988/revisions/rev_000001/model.py:L237-L266` | `KnobGeometry(grip=KnobGrip(style="knurled"))` + `mesh_from_geometry` 滚花拇指轮 + CONTINUOUS 关节 |
| S9 | `rec_zippo_lighter_240fee4992484c1cb3d1e603a0bbfff9` | `data/records/rec_zippo_lighter_240fee4992484c1cb3d1e603a0bbfff9/revisions/rev_000001/model.py:L157-L181` | cadquery toothed spark wheel（18 颗 tooth 环绕 + 轴），齿轮式打火轮 mesh |
| S10 | `rec_zippo_lighter_16d841b23f4045779d5807f11670f771` | `data/records/rec_zippo_lighter_16d841b23f4045779d5807f11670f771/revisions/rev_000001/model.py:L343-L377` | Z 轴 hinge 变体（`case_to_lid` axis=(0,0,1)）+ FIXED insert + cam mimic 的关节写法 |
| S11 | `rec_zippo_lighter_edb393d5826644a691e90359063351ef` | `data/records/rec_zippo_lighter_edb393d5826644a691e90359063351ef/revisions/rev_000001/model.py:L485-L533` | cam lever parent=insert 的变体 + `Mimic(joint="lid_hinge", multiplier=0.45)` 联动 |
| S12 | `rec_zippo_lighter_62f6a981187245d8ba9b93aee5f70b4f` | `data/records/rec_zippo_lighter_62f6a981187245d8ba9b93aee5f70b4f/revisions/rev_000001/model.py:L199-L228` | 3-part fused：case(壳+insert+chimney 全融合) / cap / wheel(parent=case)，最简默认拓扑 |

## 核心身份补充：拓扑分布统计（21 个 5 星全样本）
- part 数：3-part = 3 个（62f6/b657/bea7）；4-part = 8 个；5-part = 10 个。
- insert 装配：FIXED insert = 11 个；PRISMATIC sliding insert = 7 个；无独立 insert（融合进 body）= 3 个。
- cam lever（第 4 个 REVOLUTE，带 Mimic）：出现 9 个；不出现 12 个。cam parent=lid 居多，parent=insert 2 个（edb3/c06c），parent=case 1 个（304570）。
- lid hinge 轴：±Y（后边铰链）≈18 个；Z 轴 2 个（16d8/976c）；spark wheel 始终 CONTINUOUS。
- 构造手段：cadquery `mesh_from_cadquery` shell 居多；纯 primitive Box 壁 = 3 个（a959/dc8d 及 edb3 的壳体）；`KnobGeometry`/`mesh_from_geometry` 滚花轮 = 5 个（351666/842b/b657/dc8d/08b8）。

## 槽位 + 候选模块表

### Slot A：body_case（下壳 / fuel case，root，落地固定）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| cadquery_shell_cup | `rec_..._bea7f175` | L56-L147（`_lower_shell_shape`）| **yes** | cadquery box `.shell` 中空壳 + 圆角，单 mesh visual，铰链 knuckle 融合进同一 part |
| primitive_wall_box | `rec_..._a9599c7a` | L71-L137 | | 5 个 Box 壁 + 4 个 corner Cylinder + hinge pad/knuckle，全 primitive 无 cadquery |
| open_shell_box_helper | `rec_..._0215496335` | L113-L130（`_shell_box`/`_build_case_shape`）| | 通用 `_shell_box(open_top=True)` + lug/barrel hinge boss，可参数化壁厚与圆角 |

### Slot B：insert_module（chimney/fuel insert + 装配关节）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| fixed_chimney_insert | `rec_..._0215496335` | L155-L178 + L237-L243 | **yes** | 独立 chimney/insert part（fuel can + wind guard + 打孔 + wick），FIXED 到 case，wheel parent=insert |
| prismatic_sliding_insert | `rec_..._351666d7` | L150-L235 | | insert 经 PRISMATIC `shell_to_insert`（axis=Z）可竖直滑出壳体，含 striker fork/axle boss |
| fused_no_insert | `rec_..._62f6a981` | L123-L158 + L199-L209 | | 无独立 insert part：insert+chimney mesh 融合进 body part，wheel 直接 parent=case |

### Slot C：lid（flip-top 翻盖，REVOLUTE）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| cadquery_shell_lid_yhinge | `rec_..._bea7f175` | L119-L135 + L187-L195 | **yes** | cadquery 开口壳 cap + 圆角 + 后边 knuckle，REVOLUTE 绕 ±Y（后边铰链）|
| primitive_wall_lid_yhinge | `rec_..._a9599c7a` | L222-L288 + L332-L340 | | 翻盖由 5 个 Box 壁 + corner Cylinder + hinge pad 组成（纯 primitive），REVOLUTE ±Y |
| z_hinge_lid | `rec_..._16d841b2` | L74-L93 + L343-L358 | | 翻盖绕 Z 轴侧翻（`case_to_lid` axis=(0,0,1)），盒形壳 + 侧 hinge barrel |

### Slot D：spark_wheel（拇指打火轮，CONTINUOUS）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| grooved_cylinder_wheel | `rec_..._bea7f175` | L138-L146（`_wheel_shape`）| **yes** | cadquery 圆柱 + 轴，绕 Y 切多道 groove 形成滚花纹，单 mesh |
| knurled_knob_wheel | `rec_..._351666d7` | L237-L257 | | `KnobGeometry(grip=KnobGrip(style="knurled", count=28))` + `mesh_from_geometry` 滚花轮 + 短轴 |
| toothed_spark_wheel | `rec_..._240fee49` | L157-L181 | | cadquery 圆盘 + 18 颗 tooth 环绕 + 轴，齿轮式打火轮 |
| band_cylinder_wheel | `rec_..._16d841b2` | L309-L321 | | 双 Cylinder（外 band + 暗色 core）+ 轴，最简 primitive 轮 |

### Slot E：cam_lever（可选第 4 DOF，REVOLUTE + Mimic）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| none | （12 个 5 星无 cam，如 `rec_..._62f6a981` / `rec_..._bea7f175`）| n/a | **yes** | 不添加 cam lever，只有 lid + wheel 两个 DOF（最常见的最小拓扑）|
| cam_on_lid | `rec_..._a9599c7a` | L296-L350 | | cam lever part（hub+arm+toe）parent=lid，REVOLUTE，`Mimic(joint="lid_hinge")` 随翻盖联动 |
| cam_on_insert | `rec_..._edb393d5` | L485-L533 | | cam lever parent=insert，REVOLUTE，`Mimic(joint="lid_hinge", multiplier=0.45)` |

## 槽位图（slot graph）
pattern = **mixed**（chain 主干 + parallel children + 一个 optional 多重性 slot）

```
                        [A] body_case  (root, grounded)
                         |
        +----------------+------------------+------------------+
        | (REVOLUTE lid_hinge)              | (FIXED 或 PRISMATIC, 见 B)
        v                                   v
     [C] lid                            [B] insert_module
        |                                   |
        | (Slot E = cam_on_lid:             | (CONTINUOUS wheel_spin)
        |  REVOLUTE+Mimic)                  v
        v                               [D] spark_wheel
   [E] cam_lever                            ^
   (parent=lid)                             | (Slot E = cam_on_insert:
                                            |  REVOLUTE+Mimic, parent=insert)
                                       [E] cam_lever

特例 B=fused_no_insert：无 [B] 节点，wheel(D) 直接 parent=A，E 仅能取 none 或 cam_on_lid。
```

- 链主干：A → C（lid_hinge, REVOLUTE）。
- 并联子节点：A → B（insert，FIXED 或 PRISMATIC）；B → D（spark_wheel，CONTINUOUS）。
- optional slot E（cam_lever）：取 none / cam_on_lid（parent=C）/ cam_on_insert（parent=B）。
- B=fused_no_insert 时 D 改 parent=A，E 不能取 cam_on_insert（无 insert 可挂）。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `case` / `body` / `lower_shell` | 下壳：中空 fuel cavity + 后边 hinge knuckle/pad，root 落地 | `case_w`, `case_d`, `case_h`, `wall`, `corner_r`, `case_style` | S1 / S3 / S5 / S12 |
| `insert` / `chimney` | 烟囱/燃料 insert：fuel can + wind guard（打孔）+ wick + striker fork | `insert_w`, `insert_d`, `chimney_h`, `vent_hole_rows`, `insert_mount` | S3 / S4 / S7 / S12 |
| `lid` / `cap` | 翻盖：中空 cap 壳 + 后边/侧边 hinge knuckle | `lid_h`, `lid_wall`, `hinge_axis`, `lid_style` | S1 / S5 / S10 |
| `spark_wheel` / `striker_wheel` | 拇指打火轮：滚花/齿/带纹圆柱 + 轴 | `wheel_r`, `wheel_len`, `wheel_style`, `axle_r` | S2 / S8 / S9 |
| `cam_lever` | 可选：随翻盖联动的 cam/凸轮杆（hub+arm+toe），optional | `has_cam`, `cam_parent`, `cam_mimic_mult`, `cam_mimic_offset` | S6 / S11 |
| `wick`（visual） | wick 棉芯，作为 insert/body 的 `visual`，非独立 part | `wick_r`, `wick_len` | S2 / S3 / S7 |
| `hinge_knuckle`（visual） | 铰链 knuckle/barrel/leaf，作为 case/lid 的 `visual` 融合 | `hinge_r`, `knuckle_len`, `knuckle_count` | S1 / S5 / S10 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `lid_hinge` | revolute | A.case | C.lid | `(0,±1,0)`（默认）或 `(0,0,1)`（z_hinge_lid）| `[0, ~1.95]` rad（≈112°）| 翻盖绕后边/侧边铰链翻起，唯一主翻盖 DOF | S2 / S5 / S10 |
| `insert_mount` | fixed | A.case | B.insert | n/a | n/a | fixed_chimney_insert / fused 时 insert 固定到 case | S4 / S12 |
| `insert_slide` | prismatic | A.case | B.insert | `(0,0,1)` | `[0, ~0.026]` m | prismatic_sliding_insert 时 insert 竖直滑出壳体 | S7 |
| `wheel_spin` | continuous | B.insert（或 A.case，fused 时）| D.spark_wheel | `(±1,0,0)` 或 `(0,±1,0)` | n/a（连续）| 拇指打火轮连续旋转，轴与 hinge 轴正交于轮宽方向 | S2 / S4 / S8 |
| `cam_pivot` | revolute（+ Mimic）| C.lid 或 B.insert | E.cam_lever | 与 lid_hinge 同向 | `[-0.5, 1.05]` rad | optional：cam 随 `lid_hinge` 联动（`Mimic`），仅 has_cam 时存在 | S6 / S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `case_style` | enum | `cadquery_shell` / `primitive_walls` / `open_shell_helper` | `cadquery_shell` | 决定下壳构造手段（mesh vs box 壁）| S1 / S3 / S5 |
| `insert_mount` | enum | `fixed` / `prismatic` / `fused_none` | `fixed` | 决定 insert 装配关节与 wheel parent | S4 / S7 / S12 |
| `lid_style` | enum | `cadquery_shell_yhinge` / `primitive_walls_yhinge` / `z_hinge` | `cadquery_shell_yhinge` | 决定翻盖构造与 hinge 轴 | S2 / S5 / S10 |
| `wheel_style` | enum | `grooved_cylinder` / `knurled_knob` / `toothed` / `band_cylinder` | `grooved_cylinder` | 决定打火轮 mesh 手段（保留 KnobGeometry/cadquery，不降级）| S2 / S8 / S9 / S10 |
| `has_cam` | bool | `true` / `false` | `false` | 是否添加第 4 DOF cam lever | S6 / S11 |
| `cam_parent` | enum | `lid` / `insert` | `lid` | has_cam 时 cam 挂在 lid 或 insert；insert 需 insert_mount≠fused_none | S6 / S11 |
| `case_w` | float | `0.030-0.040` m | `0.038` | 下壳宽（口袋尺度）| S1 / S3 / S5 |
| `case_d` | float | `0.010-0.015` m | `0.013` | 下壳厚 | S1 / S5 |
| `case_h` | float | `0.038-0.043` m | `0.040` | 下壳高 | S1 / S3 |
| `lid_h` | float | `0.015-0.019` m | `0.017` | 翻盖高（≈ case_h 的 0.4-0.45）| S2 / S5 |
| `wall` | float | `0.0006-0.0012` m | `0.0009` | 壳壁厚 | S1 / S5 |
| `hinge_axis` | enum | `+Y` / `-Y` / `+Z` | `-Y` | 翻盖铰链轴向；z_hinge_lid 强制 Z | S2 / S10 |
| `lid_open_upper` | float | `1.75-1.95` rad | `1.95` | 翻盖开启上限角 | S2 / S5 |
| `wheel_r` | float | `0.0030-0.0040` m | `0.0035` | 打火轮半径 | S2 / S8 |
| `vent_hole_rows` | int | `2-4` | `3` | wind guard 打孔行数（fused/primitive 可为 0）| S3 / S7 |

## 拓扑多样性审计
- 槽位与候选数：A=3，B=3，C=3，D=4，E=3。
- **total_combinations = 3 × 3 × 3 × 4 × 3 = 324**（未扣除约束）。
- 扣除硬约束后仍远超门控：B=fused_none 时 E 不能取 cam_on_insert（剔除 3×1×3×4×1=36 个非法组合），仍剩 ≈288 个合法组合。

### 每槽位 candidate_count
| slot | candidate_count |
|---|---|
| A body_case | 3 |
| B insert_module | 3 |
| C lid | 3 |
| D spark_wheel | 4 |
| E cam_lever | 3（含 none）|

## Validator
| 检查项 | 标准 |
|---|---|
| identity | case + lid + spark_wheel 至少存在；lid 经 REVOLUTE 翻起，spark_wheel 为 CONTINUOUS |
| primary DOF | 至少 `lid_hinge`(REVOLUTE) + `wheel_spin`(CONTINUOUS) 两个主关节 |
| insert presence | insert_mount∈{fixed,prismatic} 时存在独立 insert part；fused_none 时 insert 几何融入 body 且 wheel parent=case |
| wheel parent | wheel_spin.parent 为 insert（有 insert 时）或 case（fused 时），且 wheel 在 chimney/wind guard 之内或之侧 |
| hinge axis consistency | 默认 lid_hinge 绕 ±Y（后边）；z_hinge 分支绕 Z；wheel 轴与 hinge 轴正交，沿轮宽方向 |
| lid closure | 闭合 pose 下 lid 覆盖 case footprint（xy overlap），seam 间隙 < ~1.2mm 不穿模 |
| lid opening | 开启到上限角时 lid 顶部明显抬高（z 增大）且向后/侧让开 |
| cam coupling | has_cam 时 cam_pivot 为 REVOLUTE 且带 `Mimic(joint=lid_hinge)`；cam_parent=insert 要求 insert 存在 |
| scale sanity | 口袋尺度：case_w 0.030-0.040、case_d 0.010-0.015、case_h 0.038-0.043，闭合总高 0.055-0.061 |
| primitive fidelity | wheel_style 的 KnobGeometry/cadquery 滚花/齿不得降级为裸 Box/Cylinder 占位 |
| no floating | wick、hinge knuckle、vent 孔、cam 全部挂在已有 part 上或作为 visual 融合，无悬空装饰 |

## Reject cases
- 只有一个带盖盒子、没有 spark wheel 或 wheel 不是 CONTINUOUS。
- lid 不翻起（无 REVOLUTE）或翻盖铰链放在自由边而非后边/侧边。
- spark_wheel 漂浮、不在 chimney/wind guard 旁，或轴向与 hinge 轴平行导致语义错误。
- insert_mount=fused_none 却又额外建了独立 insert part 并要求 cam_on_insert（无处可挂）。
- 把 wheel_style 的 KnobGeometry/cadquery 滚花轮降级成光面 Cylinder 占位（违反 Rule 3）。
- cam lever 不带 Mimic、与 lid 翻盖脱钩，或 cam_parent=insert 但模型无 insert。
- 尺度失真（做成大于 5cm 宽的台式打火机或缩成几 mm）。
- wick / vent 孔 / hinge knuckle 做成独立 FIXED part + 微型 interface disk（违反 Rule 1/2）。

## 与相邻类别的边界
| 相邻类别 | 区别 |
|---|---|
| 普通 hinged box / 翻盖盒 | zippo 必须有 spark wheel（CONTINUOUS 拇指轮）+ chimney/wind guard + wick；普通翻盖盒只有 lid_hinge 一个 DOF |
| butane 气体打火机 | butane 用气阀 + 压电/滑轮按钮 + 喷嘴火焰，无 wick 棉芯与 flint wheel；zippo 是 wick + flint 摩擦点火 |
| screwcap_bottle / 螺纹瓶盖 | 瓶盖是旋拧（continuous/螺旋）密封，无翻盖铰链与打火轮 |
| 单纯 rotary knob / 滚花旋钮 | zippo 的 spark_wheel 虽用 KnobGeometry 但必须从属于打火机壳体并与 wick/insert 共存，不能是孤立旋钮 |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。重点确认：(1) Slot B 的 fused_no_insert 与 cam_on_insert 的互斥约束是否在实现里 gate 干净；(2) Slot D 四个 wheel 候选是否都保留原 primitive 等级（KnobGeometry / cadquery 齿轮不降级）；(3) z_hinge_lid 与默认 ±Y hinge 是否需要像 serial_elbow_arm 那样进一步拆成 gated family。 |
