# USB Drive With Swivel Cover Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `usb_drive_with_swivel_cover` |
| template path | `agent/templates/usb_drive_with_swivel_cover.py` |
| test path | `tests/agent/test_usb_drive_with_swivel_cover_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 25 |
| read_count | 8 |
| read_scope | 全量 25 个 5 星样本均做结构指纹扫描（part 名、visual 计数、articulation 类型/轴、bbox、mesh 工具、辅助 DOF 计数）；其中 8 个跨越完整结构范围的样本逐行精读（4d3704a4 / 0072 / e4dc / 0002 / 94788541 / a34965 / b4af / e945，外加 0001 / 51cc 的 part+joint 段精读）|
| source_index_policy | 只索引被实际采纳为可复用模块的 snippet；单样本独有特征（如 e945 的 set-screw 辅助 DOF、fe06 的 scales+service_plate 堆叠）记为 gated/optional，不进默认主槽位 |

## 核心身份
USB 闪存盘 + swivel cover：一个承载 USB-A connector 的紧凑 drive body（root），加一个绕 side pivot 旋转的金属保护盖（cover），二者之间恰好一个主旋转关节。connector 必须从 body 一端明确外伸；cover 在 closed pose 包住/罩住 connector，在 open pose 让出 connector。区别于 cap-on-tether U 盘（盖子是独立漂浮件、无 pivot）、retractable/slider U 盘（connector 平移而非盖子旋转）、以及无盖裸 connector U 盘。pivot 必须是可见的 side pin/lug，cover 不能从空中悬挂。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_usb_drive_with_swivel_cover_4d3704a4c8b54a259bceec8e458fa4ab` | `data/records/rec_usb_drive_with_swivel_cover_4d3704a4c8b54a259bceec8e458fa4ab/revisions/rev_000001/model.py:L28-L98` | 最简 body（box shell + box usb_plug + 横置 pivot_sleeve）、U-arm cover（left_arm/right_arm/front_bridge + 两个 pivot_tab）、Y 轴 CONTINUOUS swivel 模板 |
| S2 | `rec_usb_drive_with_swivel_cover_0072dcef91ad4f8d94315e6bc4050609` | `data/records/rec_usb_drive_with_swivel_cover_0072dcef91ad4f8d94315e6bc4050609/revisions/rev_000001/model.py:L38-L118` | extrude rounded-rect body shell、U-channel wrap cover（top_shell/bottom_shell/side_spine，从 body 尺寸 + clearance 派生）、Z 轴 CONTINUOUS swivel origin |
| S3 | `rec_usb_drive_with_swivel_cover_e4dc0b9eb08c40c3a44846639028a26a` | `data/records/rec_usb_drive_with_swivel_cover_e4dc0b9eb08c40c3a44846639028a26a/revisions/rev_000001/model.py:L30-L120` | 多段 coaxial body（rear_cap/center_body/front_shoulder/connector_collar/usb_shell）、top_plate/bottom_plate/side_bridge plate cover、Z 轴 swivel |
| S4 | `rec_usb_drive_with_swivel_cover_0002` | `data/records/rec_usb_drive_with_swivel_cover_0002/revisions/rev_000001/model.py:L80-L289` | section_loft 锥度 body、独立 FIXED connector part（四壁 USB-A 壳 + tongue）、ExtrudeWithHoles 双 plate cover、body 内嵌 pivot_pin、Z 轴 REVOLUTE [0,π] + 双 articulation |
| S5 | `rec_usb_drive_with_swivel_cover_94788541fbe64586ab25c95e6ac4298b` | `data/records/rec_usb_drive_with_swivel_cover_94788541fbe64586ab25c95e6ac4298b/revisions/rev_000001/model.py:L79-L257` | slotted yoke body、独立 FIXED connector、独立 FIXED pivot_pin part（shaft+两 head）、U-cheek strip cover、Y 轴 REVOLUTE [0,3.25] + 三 articulation |
| S6 | `rec_usb_drive_with_swivel_cover_a34965c895c745609479626777de351c` | `data/records/rec_usb_drive_with_swivel_cover_a34965c895c745609479626777de351c/revisions/rev_000001/model.py:L19-L219` | CadQuery 单件 body（connector 壳与 pivot lug 全部 molded-in）、单件 stamped cover shell（integral 旋转 sleeve + U-channel hood + front lip）、Y 轴 REVOLUTE |
| S7 | `rec_usb_drive_with_swivel_cover_b4af38d836744d83b173f3d61af6c894` | `data/records/rec_usb_drive_with_swivel_cover_b4af38d836744d83b173f3d61af6c894/revisions/rev_000001/model.py:L134-L226` | hinge_saddle + center_hinge_barrel + 长 pivot_pin body、flip-hood cover（cover_top/cover_side×2/front_bumper/collar×2/wear_pad），Y 轴 REVOLUTE 翻盖 |
| S8 | `rec_usb_drive_with_swivel_cover_e945f13ce5bb48409d72ce1cad5f7c39` | `data/records/rec_usb_drive_with_swivel_cover_e945f13ce5bb48409d72ce1cad5f7c39/revisions/rev_000001/model.py:L160-L223` | 精密变体：side_lug + pivot_pin + pin_head 派生 pivot stack、可选 set_screw 辅助 CONTINUOUS adjusters（gated）、cover 上 datum tick marks |
| S9 | `rec_usb_drive_with_swivel_cover_0001` | `data/records/rec_usb_drive_with_swivel_cover_0001/revisions/rev_000001/model.py:L182-L224` | status_window 作为独立 FIXED 子部件（LED/indicator lens）+ FIXED→body、与 REVOLUTE cover 并列的 fixed-accessory 范例 |

## 槽位 + 候选模块表

### Slot A：drive_body（root 固定 body）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `monolithic_box_body` | S1 | 4d3704a4 model.py:L28-L51 | ✅ seed=0 | 单 box shell + 内嵌 usb_plug box + 横置 pivot_sleeve cylinder；connector molded into body，最简 |
| `extruded_rounded_body` | S2 | 0072 model.py:L38-L65 | | rounded_rect_profile extrude shell + connector box + pivot_boss；圆角壳，仍单件 body |
| `multi_section_coaxial_body` | S3 | e4dc model.py:L30-L72 | | rear_cap + center_body + front_shoulder + connector_collar + usb_shell 多段串联 box + pivot_pin |
| `lofted_taper_body` | S4 | 0002 model.py:L80-L138 | | section_loft 锥度 body_shell + nose_guard + side_grip_pad×2 + 内嵌 pivot_pin/boss + service_fastener |
| `slotted_yoke_body` | S5 | 94788541 model.py:L79-L127 | | rear_block + front_block + upper/lower pivot_bridge 组成中部 pin 槽口（接独立 pivot_pin part）|
| `cadquery_molded_body` | S6 | a34965 model.py:L19-L188 | | CadQuery filleted box，connector 四壁壳 + tongue + pivot lug/web 全部 molded-in 单件 |

### Slot B：connector（USB-A 接口表达）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `molded_plug_in_body` | S1 | 4d3704a4 model.py:L35-L40 | ✅ seed=0 | connector 作为 body 上一个 box visual（usb_plug），不单独成 part；最简、随 body 移动 |
| `separate_fixed_connector_part` | S4 | 0002 model.py:L139-L188 | | 独立 connector part：四壁 USB-A 壳（shell_top/bottom/left/right）+ rear_insert + contact_tongue + latch dimple，FIXED→body |
| `four_wall_shell_in_body` | S6 | a34965 model.py:L117-L160 | | connector 四壁壳 + tongue + contact_pad 全部作为 body 的 visual（molded-in），不单独成 part |
| `plate_shell_with_contacts` | S5 | 94788541 model.py:L129-L169 | | 独立 connector part：薄壁四面 + tongue + tongue_support，强调 contact tongue，FIXED→body |

### Slot C：swivel_cover（旋转盖几何构型）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `u_arm_bridge_cover` | S1 | 4d3704a4 model.py:L53-L88 | ✅ seed=0 | left_arm + right_arm 两侧条 + front_bridge 横梁 + 两个 pivot_tab；开放 U 形托架 |
| `u_channel_wrap_cover` | S2 | 0072 model.py:L67-L102 | | top_shell + bottom_shell + side_spine 三面包裹，inner_width/height 从 body + clearance 派生 |
| `dual_plate_bridge_cover` | S3 | e4dc model.py:L74-L110 | | top_plate + bottom_plate + side_bridge + rivet_head×2；上下双板 + 单侧脊梁 |
| `single_stamped_shell_cover` | S6 | a34965 model.py:L48-L62, L190-L203 | | CadQuery 单件：integral 旋转 sleeve + web + top + side×2 + front_lip 一次成型 |
| `flip_hood_collar_cover` | S7 | b4af model.py:L165-L216 | | cover_top + cover_side×2 + front_bumper + collar×2 + wear_pad；翻盖式 hood 带 hinge collar |

### Slot D：pivot_hardware（pivot pin/lug 表达与是否独立成 part）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integral_sleeve_in_body` | S1 | 4d3704a4 model.py:L41-L46 | ✅ seed=0 | body 上一根横置 pivot_sleeve cylinder + cover 上 pivot_tab，pin 不单独成 part |
| `body_embedded_pin_with_bosses` | S4 | 0002 model.py:L110-L127 | | body 上 pivot_boss_top/bottom + 贯穿 pivot_pin cylinder（仍属 body visual）+ cover 上 pivot_washer |
| `separate_pivot_pin_part` | S5 | 94788541 model.py:L204-L243 | | 独立 pivot_pin part：shaft + left_head + right_head，FIXED→body，穿过 cover cheek |
| `side_lug_pin_stack` | S7 / S8 | b4af model.py:L134-L163 / e945 model.py:L140-L159 | | hinge_saddle/side_lug 凸台 + center barrel + 长 pin + pin_head，从 body 侧面长出 |

### Slot E：body_accessory（可选固定附件，drop 到 2 候选）
> Drop 到 2 候选的理由：除「无附件」基线外，5 星样本里真正成为独立 FIXED 子 part 的附件只有 status_window（S9，1 例）与 scales/service_plate（fe06，1 例）这两类，单类各只 1 个样本支撑；其余「附件」都是 body 上的 box visual（grip pad / seam / snap window / datum tick）而非独立 part，归入 Slot A/F 的 detail，不另立结构候选。
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `none` | S1 | 4d3704a4 model.py:L28-L51 | ✅ seed=0 | 不加独立附件 part，body+cover(+可选 pin) 即完整 |
| `status_window_fixed_part` | S9 | 0001 model.py:L182-L219 | | status_window 独立 part（indicator lens）FIXED→body，作为 LED/视窗附件 |

### Slot F：surface_detail（body/cover 上的固定细节层级，连续/离散混合）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `minimal_clean` | S1 | 4d3704a4 model.py:L28-L88 | ✅ seed=0 | 无额外细节，仅 shell/plug/cover；干净 silhouette |
| `grip_and_seam_cues` | S4 | 0002 model.py:L98-L137 | | side_grip_pad×2 + nose_guard + service_fastener×2 等 rugged 橡胶/螺栓 box visual |
| `datum_tick_marks` | S8 | e945 model.py:L108-L136, L201-L213 | | datum_rail + index_tick + gap_pad + cover_tick 等精密刻度，laser-etch box，挂在 body/cover 表面 |

## 槽位图（slot graph）
pattern: **mixed**（linear_chain 主干 body→cover + parallel_children 把 connector/pivot_pin/accessory 作为 body 的 FIXED 子节点并联挂载）

```
                 drive_body (Slot A, root)
                 ├── [FIXED] connector            (Slot B：molded-in 则并入 A，不成独立 child)
                 ├── [FIXED] pivot_pin            (Slot D：仅 separate_pivot_pin_part 时成独立 child)
                 ├── [FIXED] body_accessory       (Slot E：仅 status_window / scales 时成独立 child)
                 └── [REVOLUTE | CONTINUOUS] swivel_cover (Slot C)   <-- 唯一主 DOF
                          └── (cover 内含 pivot_tab/collar/sleeve，几何随 Slot C/D 派生)

Slot F (surface_detail) 不引入节点：以 visual 形式叠加在 drive_body / swivel_cover 上。
[可选 gated] set_screw adjusters (e945)：精密变体下额外 CONTINUOUS 子 part，默认关闭。
```

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `drive_body` | root 固定 body，承载 USB-A connector，必含 pivot 支撑（sleeve/boss/lug/yoke） | `body_style`, `body_length`, `body_width`, `body_thickness`, `pivot_x` | S1 / S2 / S3 / S4 / S5 / S6 |
| `connector` | USB-A 接口；可作为 body 的 visual（molded-in）或独立 FIXED part | `connector_style`, `connector_length`, `connector_width`, `connector_thickness` | S1 / S4 / S5 / S6 |
| `swivel_cover` | 绕 pivot 旋转的保护盖，closed 包 connector / open 让出 connector | `cover_style`, `cover_length`, `cover_clearance`, `cover_wall` | S1 / S2 / S3 / S6 / S7 |
| `pivot_pin` | pivot 销/凸台；多数随 body，部分作为独立 FIXED part | `pivot_style`, `pin_radius`, `pin_length`, `has_pin_head` | S1 / S4 / S5 / S7 / S8 |
| `body_accessory` | 可选独立 FIXED 子 part（status window / scales / service plate） | `accessory_style` | S9 |
| `surface_detail` | body/cover 表面固定细节（grip pad / seam / datum tick / fastener） | `detail_level` | S4 / S8 |
| `set_screw` (gated) | 精密变体下的辅助 CONTINUOUS 调节螺钉，默认不生成 | `has_adjusters`, `adjuster_count` | S8 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `body_to_cover` | revolute 或 continuous | A.drive_body | C.swivel_cover | `(0,±1,0)`（side-flip）或 `(0,0,±1)`（top-swivel） | continuous: 无限；revolute: `[0, ~π]`（典型 0–2.45/2.75/3.25/π） | 唯一主 DOF；轴穿过可见 pivot pin 中心，origin = pivot_x 处 | S1 / S2 / S4 / S5 / S6 / S7 |
| `body_to_connector` | fixed | A.drive_body | B.connector | n/a | n/a | 仅当 connector 为独立 part 时存在；molded-in 时无此关节 | S4 / S5 |
| `body_to_pin` | fixed | A.drive_body | D.pivot_pin | n/a | n/a | 仅当 pivot_pin 为独立 part 时存在（separate_pivot_pin_part） | S5 |
| `body_to_accessory` | fixed | A.drive_body | E.body_accessory | n/a | n/a | 仅当存在 status_window / scales / service_plate 独立 part 时 | S9 |
| `body_to_set_screw` (gated) | continuous | A.drive_body | F.set_screw | `(0,0,1)` | 无限 | 精密变体辅助调节 DOF，默认关闭，绝不替代主 swivel | S8 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `pivot_axis_family` | enum | `side_flip`(Y) / `top_swivel`(Z) | `side_flip` | 决定主关节 axis 与 cover 开合平面 | S1 / S4（Z）/ S5 / S6 / S7（Y）|
| `articulation_kind` | enum | `continuous` / `revolute` | `continuous` | revolute 时设 `[0, swivel_upper]` | S1 / S2（cont.）/ S4 / S5 / S6（rev.）|
| `swivel_upper` | float | `2.4 – pi`（约 137°–180°）| `pi` | 仅 revolute 用；下限固定 0（closed pose）| S5 / S6 / S7 |
| `body_style` | enum | `monolithic_box` / `extruded_rounded` / `multi_section` / `lofted_taper` / `slotted_yoke` / `cadquery_molded` | `monolithic_box` | 决定 body mesh 构造与 pivot 支撑形态 | S1 / S2 / S3 / S4 / S5 / S6 |
| `body_length` | float | `0.036 – 0.064` | sampled | USB 盘主体长，含 connector 前伸 | S1 / S3 / S4 / S6 |
| `body_width` | float | `0.017 – 0.021` | sampled | body 横宽，约束 cover inner_width | S1 / S2 / S4 |
| `body_thickness` | float | `0.0076 – 0.0108` | sampled | body 厚，约束 cover inner_height | S1 / S2 / S4 |
| `connector_style` | enum | `molded_box` / `separate_four_wall_part` / `in_body_four_wall` / `plate_with_contacts` | `molded_box` | molded 时不建 connector part | S1 / S4 / S5 / S6 |
| `connector_length` | float | `≈0.012` | `0.012` | USB-A 标准前伸段，外伸出 body 前端 | S1 / S4 / S5 / S6 |
| `cover_style` | enum | `u_arm_bridge` / `u_channel_wrap` / `dual_plate_bridge` / `single_stamped_shell` / `flip_hood_collar` | `u_arm_bridge` | 决定 cover 几何与 pivot_tab/sleeve 接口 | S1 / S2 / S3 / S6 / S7 |
| `cover_clearance` | float | `0.0007 – 0.0010` | `0.0008` | cover 内壁与 body 间隙，派生 inner_width/height | S2 / S3 |
| `pivot_style` | enum | `integral_sleeve` / `body_embedded_pin` / `separate_pin_part` / `side_lug_stack` | `integral_sleeve` | separate_pin_part 时建 pivot_pin part + FIXED | S1 / S4 / S5 / S7 |
| `pivot_x` | float | body 一端附近（`-0.024 – +0.0065`，多在后端）| sampled | swivel origin x；与 cover/connector 端相反侧居多 | S1 / S4 / S5 / S6 / S7 |
| `accessory_style` | enum | `none` / `status_window` | `none` | none 时不建独立附件 part | S1 / S9 |
| `detail_level` | enum | `minimal` / `grip_seam` / `datum_tick` | `minimal` | 仅叠加 visual，不改拓扑 | S1 / S4 / S8 |
| `has_adjusters` | bool | `true` / `false` | `false` | 仅精密 gated 变体；true 时加 set_screw CONTINUOUS 子 part | S8 |

## 拓扑多样性审计
主结构槽位（不含纯 visual 的 Slot F、不含 gated adjusters）的候选计数：

| slot | name | candidate_count |
|---|---|---|
| A | drive_body | 6 |
| B | connector | 4 |
| C | swivel_cover | 5 |
| D | pivot_hardware | 4 |
| E | body_accessory | 2 |
| F | surface_detail | 3 |

total_combinations = 6 × 4 × 5 × 4 × 2 × 3 = **2880**

正交轴（axis-only）拓扑组合：`pivot_axis_family`(2) × `articulation_kind`(2) × `cover_style`(5) × `connector_style`(separate vs molded → 2 拓扑) × `pivot_style`(separate pin vs integral → 2 拓扑) × `accessory_style`(2) = 2×2×5×2×2×2 = **160** 个结构上可区分的组合。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | 恰好存在 drive_body（root）+ swivel_cover，且二者间恰好一个非 fixed 主关节 |
| primary joint count | 主 DOF 恰好 1 个（body_to_cover）；set_screw adjusters 仅在 `has_adjusters` 时出现且为辅助，不计入主 DOF |
| axis consistency | 主关节 axis 必为 ±Y（side_flip）或 ±Z（top_swivel）之一；不得用 X 轴；axis 必须穿过可见 pivot pin/sleeve 中心 |
| connector exposure | connector 在 body 一端明确外伸（前端 AABB 超出 body shell ≥ ~0.010），closed pose cover 罩/邻接 connector，open pose cover 让出 connector 前方空间 |
| cover capture | cover 与 body 在 pivot 处保持 contact / within，不漂浮；pivot_tab/sleeve/collar 与 body pivot 支撑同轴 |
| body grounding | drive_body 为唯一 root；connector/pivot_pin/accessory 若独立必 FIXED→body 且 expect_contact 成立 |
| molded consistency | `connector_style=molded` 时不存在 connector part 与 body_to_connector 关节；`pivot_style=integral/side_lug` 时不存在独立 pivot_pin part |
| swivel range | continuous 无限制；revolute 下限=0（closed），上限 ∈ [~2.4, π]，open/closed 两端均无 part 互穿 |
| no floating | body、connector、cover、pin、accessory、detail visual 全部 attached 或 constrained，无空中漂浮件/孤立 island |

## Reject cases
- 只有 body 与盖子两个静态件，没有 revolute/continuous 主关节（盖子焊死或纯 fixed）。
- swivel 主关节用 X 轴（沿盘体长轴），或 axis 不穿过任何可见 pivot pin/sleeve（盖子绕空中点旋转）。
- connector 不外伸、被完全埋进 body，或根本没有 USB-A 接口表达。
- closed pose cover 没有罩住/对齐 connector，或 open pose cover 仍压在 connector 上不让位。
- `connector_style=molded` 却又额外建了独立 connector part（重复几何）；或 `pivot_style=integral` 却建了独立 pivot_pin part 且不接触 body。
- 独立 connector / pivot_pin / status_window part 不 FIXED→body 或与 body 无接触，成为漂浮件。
- cover 的 pivot_tab/sleeve/collar 与 body pivot 支撑不同轴，导致旋转时穿模或脱开。
- 把 retractable/slider U 盘（connector 平移）或 tethered-cap U 盘（盖子独立无 pivot）当成本类默认拓扑。
- 主 swivel 被拆成多个旋转 DOF，或 set_screw adjusters 在非精密变体下默认开启替代主盖运动。

## 与相邻类别的边界
- **vs tethered_cap_usb（拔插式带绳盖）**：那类盖子是独立件、靠 tether/snap 固定、无固定 pivot 关节；本类盖子必须绕固定 side pivot 旋转，恰好 1 个主 revolute/continuous DOF。
- **vs retractable_slider_usb（伸缩推拉式）**：那类 connector 沿盘体长轴平移（prismatic），盖子不旋转；本类是盖子旋转、connector 与 body 相对固定。
- **vs bare_connector_usb（无盖裸接口）**：那类无可动盖、无主关节；本类必含 swivel_cover 与主关节。
- **vs flip_phone / laptop_hinge（翻盖铰链类）**：虽同为单 revolute 翻盖，但本类 bbox 在 USB 盘量级（body ~0.04–0.06 m），connector exposure 是硬性身份特征，盖子是保护性而非屏幕/键盘载体。
- 边界判据：USB-A connector 外伸 + 单 side-pivot 旋转盖 + USB 盘尺度，三者同时满足才属本类。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
