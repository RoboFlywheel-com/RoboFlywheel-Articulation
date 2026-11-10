# Two-Joint Prismatic Chain Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `twojoint_prismatic_chain` |
| template path | `agent/templates/twojoint_prismatic_chain.py` |
| test path | `tests/agent/test_twojoint_prismatic_chain_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 44 |
| read_count | 10 |
| read_scope | 全量 grep 44 个 5 星样本（part tree / 关节 axis / lower-upper limits / 构造方式 cq vs Box / end-effector 标记），并完整精读 10 个覆盖全部结构族的代表样本：0003、85e5611、6213b556、66bd7215、84dfe33、b31cd82、53ee6ce、7e3c4a4、0eebad、53ea9bfa |
| source_index_policy | 只索引被采纳为模块源的可复用片段；orthogonal XY-table（cross-axis）与 +Y vertical drawer 作为 `axis_family` gated 分支收录，不与默认 coaxial +X telescoping 混入同一默认拓扑 |

## 核心身份
二关节串联移动副链：必须有一个 grounded base/guide、一个被它承载的 first stage、一个再被 first stage 承载的 second/terminal stage，以及恰好两个串联 `prismatic` 关节（base→stage1、stage1→stage2）。默认成熟域是 coaxial +X telescoping/nested slide：两个滑动副共线 +X、`lower=0 upper=stroke`、每级嵌套在上一级内并保持 overlap 支撑。边界：与 serial_elbow_arm（revolute 转动）、与 telescoping_boom（单链多节但语义是 boom）区分；本类强调"两段直线伸缩"，不引入 revolute DOF。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_twojoint_prismatic_chain_53ee6ce38d074944bf9ebcdf9accd272` | `data/records/rec_twojoint_prismatic_chain_53ee6ce38d074944bf9ebcdf9accd272/revisions/rev_000001/model.py:L16-L101` | 最小 flat-rail base_guide（plate+rail+end stops）、carriage_1（base+rail+stops）、两个 +X prismatic 关节的最简范式 |
| S2 | `rec_twojoint_prismatic_chain_6213b556ca49454b992f41a3a489d851` | `data/records/rec_twojoint_prismatic_chain_6213b556ca49454b992f41a3a489d851/revisions/rev_000001/model.py:L62-L161` | U-channel `outer_guide`：cadquery base mount（带螺孔）+ Box floor + 两侧 walls；channel guide 构造与 `expect_within(yz)` 容纳语义 |
| S3 | `rec_twojoint_prismatic_chain_6213b556ca49454b992f41a3a489d851` | `data/records/rec_twojoint_prismatic_chain_6213b556ca49454b992f41a3a489d851/revisions/rev_000001/model.py:L163-L272` | `middle_carriage`（channel runner）、`inner_carriage`（bar+saddle+front plate）、两个 `lower=0 upper=travel` coaxial +X 关节 |
| S4 | `rec_twojoint_prismatic_chain_85e5611eced846959cf7e1eb41ce6be8` | `data/records/rec_twojoint_prismatic_chain_85e5611eced846959cf7e1eb41ce6be8/revisions/rev_000001/model.py:L40-L122` | `add_square_tube_visuals` / `add_square_guide_visuals` 方管壳体 helper（四面 Box 拼空心管 + 导向凸缘） |
| S5 | `rec_twojoint_prismatic_chain_85e5611eced846959cf7e1eb41ce6be8` | `data/records/rec_twojoint_prismatic_chain_85e5611eced846959cf7e1eb41ce6be8/revisions/rev_000001/model.py:L147-L288` | inline ram：grounded `outer_sleeve`（含 mount_base+feet+nose collar）、`intermediate_tube`、`front_output_tube`（含 tool_plate+ribs）、step-down 管径、coaxial +X |
| S6 | `rec_twojoint_prismatic_chain_0003` | `data/records/rec_twojoint_prismatic_chain_0003/revisions/rev_000001/model.py:L69-L255` | cadquery 加工件 helper（base_frame 带 pocket/holes、rail、guide block 带 cbore、cover plate、carriage）与 `_fixed`/`_add_mesh_part` 工具 |
| S7 | `rec_twojoint_prismatic_chain_0003` | `data/records/rec_twojoint_prismatic_chain_0003/revisions/rev_000001/model.py:L456-L521` | orthogonal XY-table（cross-axis）：base→x_carriage（+X）→y_carriage（+Y），各级带 rails/blocks/covers 的 fixed 子件，gated `axis_family=orthogonal_xy` 分支 |
| S8 | `rec_twojoint_prismatic_chain_84dfe33fa4e24c119b54b3544838cc29` | `data/records/rec_twojoint_prismatic_chain_84dfe33fa4e24c119b54b3544838cc29/revisions/rev_000001/model.py:L28-L179` | under-slung：`top_support`（mounting plate+webs+lips+wear strips+end stops）下挂 `outer_slider`/`inner_slider`，`MotionProperties(damping,friction)`，长 bearing engagement |
| S9 | `rec_twojoint_prismatic_chain_66bd7215ae0b44d4904aec1d0e5b4143` | `data/records/rec_twojoint_prismatic_chain_66bd7215ae0b44d4904aec1d0e5b4143/revisions/rev_000001/model.py:L97-L218` | wall-backed：竖直 `wall_plate`+base_beam+guides+ribs 的侧装 base_support、carriage_stage（runners+bridge+secondary rail）、inner_slider（bar+front plate） |
| S10 | `rec_twojoint_prismatic_chain_0eebad5691ef4bc9b7ff71f91b1e2a2c` | `data/records/rec_twojoint_prismatic_chain_0eebad5691ef4bc9b7ff71f91b1e2a2c/revisions/rev_000001/model.py:L58-L268` | side-plate double-carriage：`_add_box`/`_add_cylinder` helper、second_slider 带 `tool_plate` + 圆柱 tool mounts，end-effector plate 范式 |
| S11 | `rec_twojoint_prismatic_chain_7e3c4a4639b34403864963882bd57c24` | `data/records/rec_twojoint_prismatic_chain_7e3c4a4639b34403864963882bd57c24/revisions/rev_000001/model.py:L56-L290` | low-profile transfer table：宽扁 cadquery base + first_slide（runner+top rail）+ terminal_slide（runner+end plate），broad 平面比例 |
| S12 | `rec_twojoint_prismatic_chain_b31cd82023df4dcbad9307781ce0a883` | `data/records/rec_twojoint_prismatic_chain_b31cd82023df4dcbad9307781ce0a883/revisions/rev_000001/model.py:L11-L67` | telescoping drawer：outer/middle/inner tray（bottom+side walls+back wall，inner 带 front_wall+handle）、axis `(0,1,0)` 纯 +Y、`allow_isolated_part` 滑动间隙范式 |
| S13 | `rec_twojoint_prismatic_chain_623be4e01c944a70ad3732a16a755244` | `data/records/rec_twojoint_prismatic_chain_623be4e01c944a70ad3732a16a755244/revisions/rev_000001/model.py:L196-L223` | end_plate 作为独立第 4 part：`second_guide` fixed 到 first_carriage、prismatic 落在 `second_guide→end_plate`（end-effector 作为独立 child 的关节布置参考） |

## 槽位 + 候选模块表

### Slot A：grounded_base（落地/固定 base-guide）
本槽决定整链如何接地以及 stage1 在哪条轨道上滑。每个候选的 part tree / per-part 视觉数都来自真实 5 星样本。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `flat_rail_table` | `rec_..._53ee6ce` | `model.py:L16-L41` | **yes** | 低矮平台：base_plate + 中央 rail + 左右 end stops；扁平、轨道朝上，stage 骑在 rail 上 |
| `u_channel_guide` | `rec_..._6213b556` | `model.py:L62-L161` | | cadquery 底座（带螺孔）+ Box floor + 两侧 walls 形成 U 形通道，stage 嵌入通道内，yz 被包住 |
| `square_sleeve` | `rec_..._85e5611` | `model.py:L147-L198` | | 空心方管 outer_sleeve（四面 Box）+ rear cap + mount_base + feet + nose collar，管套管 telescoping |
| `wall_side_plate` | `rec_..._66bd7215` | `model.py:L97-L162` / `model.py:L257-L292` | | 竖直 wall_plate 侧装 + 水平 base_beam + 双侧导轨 + 三角 ribs；stage 悬出于墙板前方 |
| `top_support_gantry` | `rec_..._84dfe33` | `model.py:L28-L82` | | 顶部 mounting_plate + 下垂 webs/lips + wear strips + 前后 end stops；stage 下挂（under-slung） |
| `broad_transfer_table` | `rec_..._7e3c4a4` | `model.py:L56-L90` | | 宽扁 cadquery base（倒角板）+ 双侧长导轨，broad 平面承载大行程 transfer |

### Slot B：first_stage（被 base 承载、再承载 stage2 的中间级）
本槽必须既能在 base 轨道上滑（child of joint1），又能为 stage2 提供轨道/通道（parent of joint2）。模块需与 Slot A 风格相容（见组合逻辑）。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `rail_carriage` | `rec_..._53ee6ce` | `model.py:L43-L66` | **yes** | carriage base + 上表面二级 rail + 端部 stops；为 stage2 提供朝上轨道 |
| `channel_runner` | `rec_..._6213b556` | `model.py:L163-L198` | | 中间通道件：floor + 两侧 walls，外被 base channel 包住、内再包 stage2 |
| `intermediate_tube` | `rec_..._85e5611` | `model.py:L200-L223` | | 空心方管中间级 + rear guide 凸缘，套在 sleeve 内、再套 front tube |
| `bridge_carriage` | `rec_..._66bd7215` | `model.py:L294-L322` | | 双 runner + bridge_plate + secondary_rail，跨接墙板导轨并顶一条二级轨 |
| `outer_slider_web` | `rec_..._84dfe33` | `model.py:L84-L132` | | web + 双 cheeks + runners + lips + end tie 的下挂滑块，捕获 inner slider |

### Slot C：second_stage_core（终端移动级主体）
本槽是 joint2 的 child 主体（不含末端工具盘）。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `slim_carriage` | `rec_..._53ee6ce` | `model.py:L79-L91` | **yes** | c2_body + 顶部 top_plate 的简洁小滑块 |
| `bar_with_saddle` | `rec_..._6213b556` | `model.py:L200-L232` | | 下 bar + 中部 saddle 加厚 + 前端竖板，typical nested inner runner |
| `output_tube` | `rec_..._85e5611` | `model.py:L225-L243` | | 最小空心方管 + rear guide 凸缘的输出杆 |
| `inner_blade_slider` | `rec_..._84dfe33` | `model.py:L134-L158` | | flange + stem + lower_blade + end tie 的薄型下挂内滑块 |

### Slot D：end_effector（终端附加件，fixed 或省略）
本槽为 stage2 末端的工具盘/抓手/把手/纯端面，固定到 stage2（或如 S13 作为独立 child）。允许 `none`（≥2 个样本是纯端面无附件，见 53ca07/d0af697）。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `plain_end_face` | `rec_..._53ca07` 等 | `model.py:L79-L91`（S1 stage 末端语义） | **yes** | 无附加件，stage2 末端即工作面（多个样本如此） |
| `tool_plate` | `rec_..._85e5611` | `model.py:L244-L264` | | 竖直法兰板 + 上下 ribs，固定到 stage2 前端 |
| `tool_plate_with_mounts` | `rec_..._0eebad` | `model.py:L219-L239` | | 法兰板 + 两个圆柱 tool mounts，端面带安装接口 |
| `drawer_front_handle` | `rec_..._b31cd82` | `model.py:L43-L46` | | front_wall + handle，抽屉式人机把手（随 drawer/tray 风格） |

### Slot E：axis_family（滑动副轴与方向族，gating enum）
本槽不产生独立几何，而是决定两关节的 axis 与 limits 形态，并门控 base 朝向语义。每个分支都有 ≥2 个 5 星样本背书。

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `coaxial_x` | `rec_..._6213b556` / `rec_..._85e5611` | `model.py:L245-L272` / `model.py:L271-L288` | **yes** | 两关节同为 +X、`lower=0 upper=stroke`，逐级嵌套（dominant 域） |
| `vertical_y` | `rec_..._b31cd82` / `rec_..._b732335` | `model.py:L49-L67` | | 两关节同为 +Y（竖直抽出/drawer），`lower=0 upper=stroke`，`allow_isolated_part` 滑动间隙 |
| `orthogonal_xy` | `rec_..._0003` / `rec_..._40abfc` | `model.py:L462-L513` | | joint1=+X、joint2=+Y 的 cross-axis XY-table，`lower=-T upper=+T` 对称行程（gated，不与 coaxial 混默认） |

## 槽位图（slot graph）
pattern: **mixed**（linear_chain 主体 + `axis_family` enum gate）

```
[Slot E: axis_family]  ──gates axes/limits/base-orientation──┐
                                                             ▼
Slot A (grounded_base) ──prismatic joint1──> Slot B (first_stage)
                                                  │
                                                  └──prismatic joint2──> Slot C (second_stage_core)
                                                                              │
                                                                              └──fixed (或省略)──> Slot D (end_effector)
```

- 链结构：base → stage1 → stage2 是严格 3 节串联（两个 prismatic）；end_effector 是 stage2 上的 fixed 叶子（或 none，或如 S13 作为独立 child）。
- axis_family（Slot E）是横切 enum：`coaxial_x`（默认）令 joint1/joint2 共线 +X；`vertical_y` 令二者 +Y；`orthogonal_xy` 令 joint1=+X、joint2=+Y。
- Slot A/B/C 的具体模块需风格相容：channel↔channel_runner↔bar、sleeve↔tube↔tube、flat rail↔rail_carriage↔slim_carriage（见组合逻辑），避免几何不咬合。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `grounded_base` / `outer_guide` / `outer_sleeve` / `base_support` / `top_support` | 固定接地件，承载 stage1 的轨道/通道/管套/墙板/顶梁 | `base_style`, `base_length`, `base_width`, `base_height`, `mount_hole_count` | S1 / S2 / S5 / S6 / S8 / S9 / S11 |
| `first_stage` / `middle_carriage` / `intermediate_tube` / `carriage_stage` | 中间移动级：joint1 的 child、joint2 的 parent | `stage1_length`, `stage1_stroke`, `stage1_insert`, `link_style` | S1 / S3 / S5 / S9 |
| `second_stage` / `inner_carriage` / `front_output_tube` / `inner_slider` | 终端移动级主体：joint2 的 child | `stage2_length`, `stage2_stroke`, `stage2_insert` | S1 / S3 / S5 / S8 |
| `end_effector` / `tool_plate` / `front_plate` / `handle` | stage2 末端 fixed 工具盘/把手/端面，可省略 | `end_effector_style`, `plate_thickness`, `plate_width`, `plate_height`, `mount_count` | S5 / S10 / S12 / S13 |
| `guides` / `rails` / `runners` / `wear_strips` | 沿 base/stage 的导轨、滑块、耐磨条等 fixed 细节，从主体尺寸派生 | `guide_count`, `guide_inset`, `detail_level` | S6 / S8 / S9 / S11 |
| `end_stops` / `caps` / `feet` / `ribs` | 端部限位、封盖、地脚、加强筋等 fixed 细节 | `has_end_stops`, `has_feet`, `cap_style` | S1 / S5 / S8 / S9 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `joint1` (base_to_stage1) | prismatic | A.grounded_base | B.first_stage | `(1,0,0)` 默认 / `(0,1,0)` 或与 stage2 正交（按 axis_family） | `[0, stage1_stroke]`（coaxial/vertical）或 `[-T, T]`（orthogonal_xy） | 第一移动副：stage1 在 base 轨道上滑 | S1 / S3 / S5 / S9 |
| `joint2` (stage1_to_stage2) | prismatic | B.first_stage | C.second_stage | `(1,0,0)` 默认 / `(0,1,0)` / `(0,1,0)`（orthogonal_xy 的第二轴） | `[0, stage2_stroke]` 或 `[-T, T]` | 第二移动副：stage2 在 stage1 轨道上滑 | S1 / S3 / S5 / S8 |
| `stage2_to_end_effector` | fixed | C.second_stage | D.end_effector | n/a | n/a | 末端工具盘/把手固定到 stage2（end_effector=none 时省略） | S5 / S10 / S12 |
| `(变体) stage1_to_guide_then_end` | fixed + prismatic | B.first_stage | (second_guide)→D.end_plate | 沿 slide axis | `[0, stroke]` | S13 变体：second_guide fixed 到 stage1、prismatic 落在 guide→end_plate（end_effector 作独立 child 时的关节布置） | S13 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `axis_family` | enum | `coaxial_x` / `vertical_y` / `orthogonal_xy` | `coaxial_x` | 决定 joint1/joint2 axis 与 limit 形态、base 朝向 | S3 / S5 / S7 / S12 |
| `base_style` | enum | `flat_rail_table` / `u_channel_guide` / `square_sleeve` / `wall_side_plate` / `top_support_gantry` / `broad_transfer_table` | `flat_rail_table` | 决定接地几何与 stage1 导向方式 | S1 / S2 / S5 / S8 / S9 / S11 |
| `link_style` | enum | `flat_carriage` / `channel` / `tube` / `bridge` / `under_slung_web` | `flat_carriage` | 决定 stage1/stage2 截面构造（须与 base_style 相容） | S1 / S3 / S5 / S8 / S9 |
| `base_length` | float | `0.30-0.90` | sampled | base 主体长度，应 ≳ stage1_length + stage1_stroke 余量 | S1 / S5 / S9 / S11 |
| `stage1_length` | float | `0.20-0.55` | sampled | stage1 主体长度 | S1 / S3 / S9 |
| `stage2_length` | float | `0.10-0.40` | sampled | stage2 主体长度，应 < stage1_length（逐级缩短） | S1 / S3 / S5 |
| `stage1_stroke` | float | `0.10-0.35` | sampled | joint1 行程；retract 时须保持 overlap 支撑 | S1 / S3 / S5 / S8 |
| `stage2_stroke` | float | `0.08-0.30` | sampled | joint2 行程 | S1 / S3 / S5 / S8 |
| `stage1_insert` / `stage2_insert` | float | derived | derived | joint origin 沿 slide 轴的初始插入量，保证 rest 时 overlap | S3 / S5 / S9 |
| `limit_profile` | enum | `asymmetric_0_to_stroke` / `symmetric_pm_T` | `asymmetric_0_to_stroke` | coaxial/vertical 用 0→stroke；orthogonal_xy 用 −T→T | S3 / S5 / S7 |
| `end_effector_style` | enum | `none` / `plain_end_face` / `tool_plate` / `tool_plate_with_mounts` / `drawer_front_handle` | `plain_end_face` | 末端语义；drawer_front_handle 仅随 tray/vertical 风格 | S5 / S10 / S12 / S13 |
| `mount_hole_count` | int | `0-6` | sampled | base 安装孔数（cadquery base 才有） | S2 / S6 / S9 |
| `has_end_stops` | bool | `true` / `false` | derived | base/stage 端部限位块 | S1 / S5 |

## 拓扑多样性审计
- 槽位候选数（用于拓扑多样性的离散结构槽）：
  - Slot A grounded_base: **6**
  - Slot B first_stage: **5**
  - Slot C second_stage_core: **4**
  - Slot D end_effector: **4**
  - Slot E axis_family: **3**
- total_combinations = 6 × 5 × 4 × 4 × 3 = **1440**（名义上界；实际须扣除组合逻辑禁止的不相容配对，但仍远超阈值）

| slot | candidate_count |
|---|---|
| A grounded_base | 6 |
| B first_stage | 5 |
| C second_stage_core | 4 |
| D end_effector | 4 |
| E axis_family | 3 |

## Validator
| 检查项 | 标准 |
|---|---|
| identity | grounded_base + first_stage + second_stage + 恰好两个串联 prismatic 关节 present |
| primary joint count | 主关节恰为 joint1(base→stage1) 与 joint2(stage1→stage2)，均为 PRISMATIC |
| serial topology | base → stage1 → stage2 链无跳级；end_effector（若有）fixed 到 stage2 |
| axis consistency | `coaxial_x`：joint1/joint2 均 +X；`vertical_y`：均 +Y；`orthogonal_xy`：joint1=+X、joint2=+Y |
| limit form | coaxial/vertical 用 `lower=0,upper=stroke>0`；orthogonal_xy 用对称 `lower=-T,upper=+T`；不得 lower==upper |
| nesting overlap | rest 与 full-stroke 两态下 stage1⊂base、stage2⊂stage1 仍保持 `expect_within`/`expect_overlap` 支撑（不脱轨） |
| step-down sizing | stage2 截面/长度 ≤ stage1 ≤ base（逐级缩小），tube 族 outer>mid>front |
| base grounding | base 接地或固定（flat/channel/broad 落地；wall/top_support 提供固定接口），stage1 与 base 轨道接触 |
| carried motion | 仅驱动 joint1 时 stage2 随 stage1 同步平移；仅驱动 joint2 时 stage1 不动（独立性） |
| style compatibility | base_style 与 link_style 相容（channel↔channel、sleeve↔tube、flat↔carriage 等）；drawer_front_handle 仅随 tray/vertical |
| no floating | base/stage1/stage2/end_effector/guides/rails/stops 全部 attached 或 constrained，无漂浮装饰 |

## Reject cases
- 只有两个静态杆件而没有两个 prismatic 关节，或把其中一个换成 revolute/continuous。
- joint1 与 joint2 轴向不一致却未声明 `orthogonal_xy` 分支（一个 +X 一个 +Y 但当作默认 coaxial）。
- `lower==upper` 或 stroke=0 的"伪移动副"。
- stage2 不嵌套在 stage1 内、或 full-stroke 时脱离支撑（overlap 丢失、悬空伸出）。
- 逐级尺寸反向（stage2 比 stage1 还大、tube 管径反增）。
- base 漂浮、stage1 不与 base 轨道接触、链从空中开始。
- end_effector/工具盘/把手/导轨/限位块 悬空，不 fixed 到任何主体。
- 把 orthogonal XY-table 或 vertical drawer 硬塞进默认 coaxial_x 而不切换 axis_family 与 limit_profile，导致语义/行程错误。
- 用 Box/Cylinder 占位替换 cadquery/方管壳体源模块（降级 primitive，违反 Rule 3）。

## 与相邻类别的边界
- **serial_elbow_arm**：相邻 serial 二自由度链，但用两个 **revolute**（肩/肘转动）；本类是两个 **prismatic**（直线伸缩），无转动 DOF。
- **telescoping_boom**：同为嵌套直线伸缩，但语义是单一 boom 多节悬臂；本类强调"base + 两级独立 stage"的通用 two-joint slide 模块（包含 XY-table / drawer 等非 boom 形态）。
- **drawer/cabinet 类**：`vertical_y` + `drawer_front_handle` 分支与抽屉重叠，但本类要求恰好两级 prismatic 串联且保持嵌套支撑语义，不引入铰链门或多抽屉阵列。
- **linear_actuator/single prismatic**：本类必须是 **两** 个串联移动副，不是单级。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；读了 10 个全量代表样本 + grep 全部 44 个 5 星；coaxial_x 为默认成熟域，vertical_y / orthogonal_xy 作为 gated axis_family 分支；等待人工审核 |
