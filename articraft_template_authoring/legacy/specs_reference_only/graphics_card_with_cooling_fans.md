# Graphics Card With Cooling Fans Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `graphics_card_with_cooling_fans` |
| template path | `agent/templates/graphics_card_with_cooling_fans.py` |
| test path | `tests/agent/test_graphics_card_with_cooling_fans_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
带散热风扇的显卡必须有长条 PCB / backplate、PCIe 金手指、I/O bracket、散热器 / heatpipes / fins、外部 shroud，以及 1-3 个轴流冷却风扇；每个风扇 rotor 必须围绕垂直于板面的轴连续旋转。类别识别不应退化成“矩形板加圆盘”，必须包含 GPU card 的接口边、挡板、shroud fan wells、fan frames 和板上散热细节。

采纳策略：本类别主 topology 稳定，不需要优先拆分；但 5 星样本中的 compact dual fan、long triple fan、asymmetric tail fan、fold-out support brace 只能作为兼容 variant。模板先建立 PCB/shroud/fan-center 约束图，再把 adopted fan rotor、bezel、I/O bracket、brace 代码适配到对应 helper，不能让 fan_count、fan radius、shroud profile 独立随机。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc` | `data/records/rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc/revisions/rev_000001/model.py:L38-L80` | PCB, backplate, heatsink fin stack, heatpipes and board proportions |
| S2 | `rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc` | `data/records/rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc/revisions/rev_000001/model.py:L81-L167` | shroud rails, fan bezels, stators, spokes, accent ribs and screw details |
| S3 | `rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc` | `data/records/rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc/revisions/rev_000001/model.py:L169-L277` | PCIe contacts, power socket, I/O bracket, three independent fan rotors and continuous joints |
| S4 | `rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc` | `data/records/rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc/revisions/rev_000001/model.py:L282-L376` | tests for GPU proportions, fan shaft alignment, bushing and rotor-inside-bezel checks |
| S5 | `rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f` | `data/records/rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f/revisions/rev_000001/model.py:L27-L195` | circle profile helper, compact dual-fan PCB, shroud, fan bosses, hinge block, fan rotor geometry and continuous fan joints |
| S6 | `rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f` | `data/records/rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f/revisions/rev_000001/model.py:L197-L336` | support brace geometry, brace hinge and fan / brace validator checks |
| S7 | `rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225` | `data/records/rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225/revisions/rev_000001/model.py:L26-L195` | card constants, fan shroud cadquery helper, root body, shroud, I/O bracket and hinge hardware |
| S8 | `rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225` | `data/records/rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225/revisions/rev_000001/model.py:L198-L398` | fan rotor helper, prop leg helper, triple fans, prop-leg hinge and tests |
| S9 | `rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e` | `data/records/rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e/revisions/rev_000001/model.py:L25-L168` | card / rotor constants, circle / annulus / support frame and fan rotor geometry |
| S10 | `rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e` | `data/records/rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e/revisions/rev_000001/model.py:L171-L420` | shroud fascia with two large fans plus smaller tail flow-through fan and card body / fan frames |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `pcb` / `main_board` | 必需；长条 printed circuit board，带边缘、mount holes、PCIe 接触区 | `card_length`, `card_height`, `pcb_thickness`, `pcb_color`, `board_profile` | S1 / `model.py:L38-L80`; S3 / `model.py:L169-L232`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195`; S9 / `model.py:L25-L168` |
| `backplate` / `stiffener` | optional but common；背板、加固板、装饰肋 | `backplate_enabled`, `backplate_style` | S1 / `model.py:L38-L80`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195` |
| `heatsink` / `fin_stack` | 必需 visual；散热片阵列、fin stack、base plate | `fin_count`, `fin_pitch`, `heatsink_depth`, `fin_style` | S1 / `model.py:L38-L80`; S7 / `model.py:L65-L195`; S9 / `model.py:L25-L168` |
| `heatpipe_i` | optional；铜 heatpipe，穿过 fin stack 或 shroud 下方 | `heatpipe_count`, `heatpipe_style`, `heatpipe_radius` | S1 / `model.py:L38-L80`; S3 / `model.py:L169-L232` |
| `cooler_shroud` / `fan_fascia` | 必需；包住风扇与散热器的外壳、导风罩、斜切外框 | `shroud_profile`, `shroud_height`, `shroud_overhang`, `fan_layout` | S2 / `model.py:L81-L167`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195`; S10 / `model.py:L171-L420` |
| `fan_frame_i` / `fan_bezel_i` | 必需；每个风扇的圆环、支撑 spoke、stator、screw bosses | `fan_count`, `fan_radius`, `bezel_style`, `spoke_count` | S2 / `model.py:L81-L167`; S5 / `model.py:L47-L160`; S7 / `model.py:L26-L195`; S9 / `model.py:L40-L168`; S10 / `model.py:L171-L420` |
| `fan_rotor_i` | 必需；独立可旋转 rotor，包含 hub、blades、rim 或 blade tips | `fan_count`, `blade_count`, `blade_profile`, `hub_radius` | S3 / `model.py:L234-L277`; S5 / `model.py:L162-L195`; S8 / `model.py:L198-L398`; S9 / `model.py:L40-L168`; S10 / `model.py:L171-L420` |
| `io_bracket` | 必需；显卡端部金属挡板，带通风孔和视频接口 | `io_bracket_style`, `port_count`, `vent_slot_count` | S3 / `model.py:L169-L232`; S7 / `model.py:L65-L195` |
| `pcie_fingers` | 必需；底部金手指接触片 | `pcie_contact_count`, `pcie_edge_length` | S3 / `model.py:L169-L232`; S7 / `model.py:L65-L195` |
| `power_connector` | optional；顶部 / 侧边电源插座 | `power_connector_style`, `power_pin_count` | S3 / `model.py:L169-L232`; S7 / `model.py:L65-L195` |
| `support_brace` / `prop_leg` | optional；折叠支撑脚、抗 sag brace 或小支架 | `support_brace_enabled`, `brace_style`, `brace_length` | S6 / `model.py:L197-L336`; S8 / `model.py:L223-L398` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `fan_spin_i` | continuous | `(0, 0, 1)` or board-normal axis | fan center at shroud / rotor hub | unbounded | 每个 cooling fan rotor 围绕垂直 PCB / shroud 面的轴连续旋转 | S3 / `model.py:L234-L277`; S4 / `model.py:L282-L376`; S5 / `model.py:L162-L195`; S8 / `model.py:L269-L398`; S9 / `model.py:L40-L168`; S10 / `model.py:L171-L420` |
| `support_brace_hinge` | revolute | `(1, 0, 0)` or card-length hinge axis | hinge block on card edge or shroud side | `[0, 1.4]` typical | 可选防 sag 支撑脚从显卡边缘翻出 | S6 / `model.py:L197-L336`; S8 / `model.py:L223-L398` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `card_length` | float | `0.18-0.36` | `0.28` | primary envelope for PCB, shroud, fan centers and PCIe edge | S1 / `model.py:L38-L80`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195`; S9 / `model.py:L25-L168` |
| `card_height` | float | `0.08-0.17` | `0.12` | fan radius and shroud height must fit within card height | S1 / `model.py:L38-L80`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195` |
| `cooler_thickness` | float | `0.025-0.075` | `0.045` | shroud / fan / heatsink z stack derived from PCB top plane | S1 / `model.py:L38-L80`; S2 / `model.py:L81-L167`; S10 / `model.py:L171-L420` |
| `board_profile` | enum | `rectangular_full_length` / `compact_dual_fan` / `long_triple_fan` / `angular_cutout` | `long_triple_fan` | controls PCB outline and shroud overhang | S1 / `model.py:L38-L80`; S5 / `model.py:L47-L160`; S7 / `model.py:L65-L195`; S10 / `model.py:L171-L420` |
| `cooler_family` | enum | `single_short_card` / `compact_dual_fan` / `long_triple_fan` / `dual_large_tail_small` | `long_triple_fan` | compatibility profile for board length, fan count, fan layout, shroud profile and brace availability | S1 / `model.py:L38-L277`; S5 / `model.py:L47-L336`; S7 / `model.py:L26-L398`; S10 / `model.py:L171-L420` |
| `fan_count` | int | `1 / 2 / 3` | `3` | fan centers distributed along card length; card length clamps legal count | S3 / `model.py:L234-L277`; S5 / `model.py:L162-L195`; S8 / `model.py:L269-L398`; S10 / `model.py:L171-L420` |
| `fan_layout` | enum | `single_center` / `dual_equal` / `triple_equal` / `dual_large_tail_small` | `triple_equal` | determines centers, radius variants and shroud windows | S2 / `model.py:L81-L167`; S5 / `model.py:L47-L195`; S8 / `model.py:L269-L398`; S10 / `model.py:L171-L420` |
| `fan_radius` | float | `0.028-0.065` | `0.046` | `<= min(card_height, fan_pitch) / 2 - clearance` | S2 / `model.py:L81-L167`; S5 / `model.py:L162-L195`; S8 / `model.py:L198-L398`; S9 / `model.py:L40-L168` |
| `blade_count` | int | `5-11` | `9` | blade angular spacing from rotor hub; all fans share or style overrides | S3 / `model.py:L234-L277`; S5 / `model.py:L162-L195`; S9 / `model.py:L40-L168` |
| `blade_profile` | enum | `straight_radial` / `swept_curved` / `thin_turbine` | `swept_curved` | controls rotor mesh and visual identity | S3 / `model.py:L234-L277`; S5 / `model.py:L162-L195`; S9 / `model.py:L40-L168` |
| `shroud_profile` | enum | `rectangular_rail` / `angular_gaming` / `open_ring_frame` / `compact_rounded` | `angular_gaming` | drives fascia outline, ribs and bezel shape | S2 / `model.py:L81-L167`; S5 / `model.py:L47-L160`; S7 / `model.py:L26-L195`; S10 / `model.py:L171-L420` |
| `bezel_style` | enum | `simple_ring` / `spoked_ring` / `recessed_well` / `open_frame` | `spoked_ring` | fan frame geometry around rotor | S2 / `model.py:L81-L167`; S5 / `model.py:L47-L160`; S9 / `model.py:L40-L168`; S10 / `model.py:L171-L420` |
| `fin_count` | int | `8-32` | `18` | fin pitch from heatsink length and fan layout | S1 / `model.py:L38-L80`; S7 / `model.py:L65-L195` |
| `heatpipe_count` | int | `0-6` | `3` | visual copper pipes under shroud | S1 / `model.py:L38-L80`; S3 / `model.py:L169-L232` |
| `io_bracket_style` | enum | `single_slot` / `dual_slot_vented` / `short_low_profile` | `dual_slot_vented` | determines bracket height and vent holes | S3 / `model.py:L169-L232`; S7 / `model.py:L65-L195` |
| `support_brace_enabled` | bool | `true` / `false` | `false` | if true, add brace part and hinge joint | S6 / `model.py:L197-L336`; S8 / `model.py:L223-L398` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| PCB / card outline | full-length rectangle / compact dual fan / angular cutouts | no | yes | `board_profile` | 显卡轮廓和 shroud overhang 是类别身份细节 |
| cooler shroud | rectangular rail / angular gaming fascia / open ring frame / compact rounded | no | yes | `shroud_profile` | 外壳形态不能靠尺寸表达 |
| fan layout | single / dual / triple / asymmetric tail fan | no | yes | `fan_count`, `fan_layout` | fan count and centers directly affect joints |
| fan frame / bezel | simple ring / spoked ring / recessed well / open frame | no | yes | `bezel_style` | rotor 必须坐进对应 frame，结构差异明显 |
| fan rotor / blades | straight / swept curved / turbine-like blades | no | yes | `blade_profile`, `blade_count` | blade shape 是冷却风扇视觉核心 |
| heatsink / heatpipe | dense fins / sparse fins / visible heatpipes / hidden sink | no | yes | `fin_count`, `heatpipe_count`, `fin_style` | count 可连续 / 整数，但 pipe presence 是结构差异 |
| I/O bracket | vented dual slot / compact low profile / plain bracket | no | yes | `io_bracket_style` | 显卡可识别接口端 |
| support brace | none / fold-out brace / prop leg | no | yes | `support_brace_enabled`, `brace_style` | 若出现则是独立 hinge topology |
| PCIe fingers | length/contact-count variation only | yes | no | `pcie_contact_count`, `pcie_edge_length` | 同一语义下主要是数量与长度变化 |

## 组合逻辑（Composition Logic）
1. 先生成 PCB envelope，定义坐标：card length 沿 X，card height 沿 Y，board normal 沿 Z；后续 fan axis 默认沿 Z。
2. 从 PCB 派生 I/O bracket 在一端、PCIe fingers 在底边、power connector 在顶部或侧边；这些接口位置不可独立随机。
3. 在 PCB 顶面堆叠 heatsink base、fin stack、heatpipes，再由 shroud profile 覆盖其上，shroud 厚度由 `cooler_thickness` 派生。
4. 根据 `fan_count` 和 `fan_layout` 计算 fan center positions；`fan_radius` 由 card height、fan pitch、shroud margin、neighbor clearance 夹紧。
5. 对每个 fan center 生成 bezel / ring / screw bosses，再生成 `fan_rotor_i`；rotor radius 必须小于 inner bezel radius，hub center 必须等于 joint origin。
6. `fan_spin_i` joint origin 从 fan center 与 shroud top plane 派生，axis 与 board normal 一致；board 倾斜时使用 local board normal 转换。
7. blade count 和 blade profile 只改变 rotor visual，不改变 fan joint semantics。
8. support brace 若启用，hinge block 必须位于 card side / shroud side，brace closed pose 贴近 card edge，open pose 支撑到 ground / desk plane 或规定角度。
9. screws、LED strips、logos、labels、vent perforations 默认作为 parent visual；不要为静态小件创建大量无意义 part。
10. `resolve_config` 必须执行 cooler compatibility matrix：`single_short_card` 使用 `fan_count=1` + `single_center` + short PCB；`compact_dual_fan` 使用 `fan_count=2` + `dual_equal` + compact/rounded shroud；`long_triple_fan` 使用 `fan_count=3` + `triple_equal` + card_length 上半区；`dual_large_tail_small` 使用 2 个大 fan 加 1 个小 tail fan，tail radius 单独由剩余长度派生。
11. support brace 是 optional helper，不得因为采纳了 brace 样本就强制所有 cooler family 生成；brace 只在 card length、edge clearance 和 ground-contact story 合法时启用。

## 已有模板写法参考
continuous_rotor / radial_array / revolute_hinge / latch_lock / guide_shoe

## 约束
- 必须包含 PCB、shroud、至少一个 fan rotor continuous joint、PCIe fingers 和 I/O bracket。
- `fan_count` 必须等于 fan rotor part 和 `fan_spin_i` joint 数量。
- fan rotor 必须位于 fan bezel / shroud window 内，不能穿过 ring 或漂浮在外。
- fan axis 必须垂直于 PCB 面；不能沿 card length 或 card height 错转。
- `fan_radius` 必须由可用 card height 和 center spacing 派生，避免三风扇互相重叠。
- PCIe fingers 必须沿底边，I/O bracket 必须在端部；两者不能随机放在 shroud 顶面。
- support brace 若出现，必须有 hinge block 和合理 range，不能只是漂浮杆。
- `cooler_family`, `board_profile`, `fan_count`, `fan_layout`, `fan_radius` 必须互相合法；短卡不能采样三等分大风扇。
- adopted fan / brace 源码必须映射到对应 helper；不能把 support brace、asymmetric tail fan 和 compact dual shroud 随机混成不兼容结构。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | PCB/backplate + shroud + PCIe fingers + I/O bracket + fan rotor(s) present |
| fan joint count | `len(fan_spin_joints) == fan_count == len(fan_rotor_parts)` |
| cooler compatibility | `cooler_family`, `fan_layout`, `fan_count`, `fan_radius`, `card_length` satisfy legal matrix |
| fan axis | each fan joint axis equals board normal within tolerance |
| rotor seating | rotor radius < inner bezel radius and rotor center equals fan joint origin |
| fan spacing | adjacent fan disks and card edges satisfy configured clearance |
| card interfaces | PCIe contacts on bottom edge, I/O bracket on card end, power connector optional top/side |
| heatsink stack | heatsink / fins lie between PCB and shroud, not outside card envelope |
| support brace | if enabled, brace hinge origin sits on card/shroud edge and range opens away from PCB |
| part diversity | `board_profile`, `fan_layout`, `shroud_profile`, `bezel_style`, `blade_profile`, `io_bracket_style` drive geometry |
| no floating | fans、brackets、heatpipes、brace、connectors all attach to PCB/shroud stack |

## Reject cases
- 只有矩形板和圆盘，没有 PCIe fingers、I/O bracket 或 shroud。
- fans 是静态贴图 / visual，没有 continuous joint。
- fan axis 沿 X/Y 方向，旋转语义像轮子而非轴流风扇。
- fan rotor 超出 bezel，或三风扇互相穿模。
- PCIe 金手指放在错误边，显卡身份丢失。
- heatpipes / fins 漂浮在 shroud 外，散热结构不可信。
- support brace 漂浮或 hinge 不在 card edge。
- `fan_count` 参数与实际 fan / joint 数不一致。
- 短 PCB 上强行放三颗同半径风扇，或 asymmetric tail fan 没有单独半径 / center derivation。
- 因为某个 5 星样本有 support brace，就在所有显卡变体上都生成不接地的支撑杆。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review. 未进入模板实现阶段。 |
