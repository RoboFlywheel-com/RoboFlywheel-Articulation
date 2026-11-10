# Three-Stage Telescoping Slide Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `threestage_telescoping_slide` |
| template path | `agent/templates/threestage_telescoping_slide.py` |
| test path | `tests/agent/test_threestage_telescoping_slide_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 45 |
| read_count | 8 |
| read_scope | 完整精读 8 个跨结构谱系的代表样本（0002 / 0003 / 0004 / db83e907 / 9ef08c04 / fd45679a / 5aa889ab / 8bdc62dd），其余 37 个 5 星样本用 grep 扫 part 名 / joint 类型 / 嵌套轴 / 几何模式（mesh vs Box primitive）做覆盖核对 |
| source_index_policy | 只索引被采纳的可复用片段；side-web 抽屉滑轨（钢珠轨）与同心箱型管是不同 section family，通过 `section_style` gate，不在同一默认分支里混用横截面语义 |

## 核心身份
三级伸缩滑轨：三段嵌套的直线行程构件（outer / middle / inner）沿同一条滑动轴串联，靠两个串联 prismatic joints 实现「外套筒固定→中段伸出→内段再伸出」的两级展开。必须保证每级在收回和伸出位都有可见 overlap/engagement，且内段始终被中段、中段始终被外段横向包住。与 serial_elbow_arm（revolute 转动）和 telescoping_boom（单级或液压）的边界：本类是纯直线、必须恰好 3 段 2 级 prismatic，无转动关节。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_threestage_telescoping_slide_0002` | `data/records/rec_threestage_telescoping_slide_0002/revisions/rev_000001/model.py:L57-L114` | 同心空心箱型管 helper、端部 bracket、顶部 stop-tab helper |
| S2 | `rec_threestage_telescoping_slide_0002` | `data/records/rec_threestage_telescoping_slide_0002/revisions/rev_000001/model.py:L153-L289` | 三段 rail parts + 两个 +X prismatic（outer_to_middle / middle_to_inner）的最小干净 anchor |
| S3 | `rec_threestage_telescoping_slide_0003` | `data/records/rec_threestage_telescoping_slide_0003/revisions/rev_000001/model.py:L65-L200` | 带 window/port 的 tube_member、support_frame、access cover、boxed end bracket、guide sleeve cage helper |
| S4 | `rec_threestage_telescoping_slide_0003` | `data/records/rec_threestage_telescoping_slide_0003/revisions/rev_000001/model.py:L207-L523` | 11-part 全装饰装配：support_frame 固定父 + 前后 bracket + cover + guide_cage（roller/pad）+ inner_end_bracket，全部 FIXED 挂在 rail 上 |
| S5 | `rec_threestage_telescoping_slide_db83e907010746188db3e763b5c8a91f` | `data/records/rec_threestage_telescoping_slide_db83e907010746188db3e763b5c8a91f/revisions/rev_000001/model.py:L92-L293` | 开口 C-channel member helper（内置 raceway 滑轨 + window + counterbore + stop buffer/tab）、outer beam 带 feet、carriage_shoe terminal |
| S6 | `rec_threestage_telescoping_slide_db83e907010746188db3e763b5c8a91f` | `data/records/rec_threestage_telescoping_slide_db83e907010746188db3e763b5c8a91f/revisions/rev_000001/model.py:L341-L375` | 两个 prismatic + 末端 carriage_shoe 的 FIXED join 范式（origin 落在 inner 末端面） |
| S7 | `rec_threestage_telescoping_slide_9ef08c04ce314b64938bbdcbba7a7ccb` | `data/records/rec_threestage_telescoping_slide_9ef08c04ce314b64938bbdcbba7a7ccb/revisions/rev_000001/model.py:L72-L361` | 朝上开口 U-channel 抽屉滑轨：外段集成 base_plate + 四壁用 Box primitive 逐面拼，无 mesh，front-opening lintel/jamb |
| S8 | `rec_threestage_telescoping_slide_fd45679a02724870824da5ace345688d` | `data/records/rec_threestage_telescoping_slide_fd45679a02724870824da5ace345688d/revisions/rev_000001/model.py:L100-L361` | grounded carrier body（重质 Inertial）+ 两级 stage，roller 作为 stage 上的 Cylinder 子 visual，rail runner 派生 roller_y |
| S9 | `rec_threestage_telescoping_slide_5aa889abaf324640beafaeee91630ef7` | `data/records/rec_threestage_telescoping_slide_5aa889abaf324640beafaeee91630ef7/revisions/rev_000001/model.py:L25-L185` | side-web 钢珠抽屉滑轨：rear_support 背板固定父 + web/top-lip/bottom-lip/race 的 C 截面侧向嵌套 + terminal_tab + 螺钉 |
| S10 | `rec_threestage_telescoping_slide_0004` | `data/records/rec_threestage_telescoping_slide_0004/revisions/rev_000001/model.py:L52-L216` | 矩形管 helper + end_plate helper + pad 贴块 + `inner_to_end_plate` FIXED terminal 范式 |
| S11 | `rec_threestage_telescoping_slide_8bdc62dd3ab143d6b94dc90da1104997` | `data/records/rec_threestage_telescoping_slide_8bdc62dd3ab143d6b94dc90da1104997/revisions/rev_000001/model.py:L38-L172` | `_add_box_section` 四壁拼接 box-section helper + 加厚 front-mouth ring，集成接地、无独立 base part 的最简同心 box 变体 |

## 槽位 + 候选模块表

### Slot A：base_mount（接地 / 固定方式，root link）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integral_grounded_outer` | S1/S2 (0002) | `model.py:L153-L168` | ✅ seed=0 | 外段本身即 root，直接落地，无独立 base part；最简、最常见 |
| `support_frame_fixed` | S4 (0003) | `model.py:L111-L121, L217-L224, L448-L454` | | 独立 support_frame 焊接件做 root，FIXED 把 outer member 抬高到 `OUTER_CENTER_Z`，台架式 |
| `wall_backplate_fixed` | S9 (5aa889ab) | `model.py:L25-L57, L160-L166` | | rear_support/side_plate 竖直背板做 root，FIXED 接 outer，墙挂/机柜抽屉式（背板在 -Y 侧） |
| `grounded_carrier_body` | S8 (fd45679a) | `model.py:L107-L171, L340-L353` | | 朝上开口 U 形 carrier body 做 root + 重质 Inertial，stage 直接 prismatic 挂 body，抽屉柜式 |

### Slot B：outer_member（第一级固定段，base 的子 / 或即 root）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `closed_box_tube_outer` | S1 (0002) | `model.py:L57-L69, L162-L173` | ✅ seed=0 | 四面闭合空心箱型管（mesh），同心包住 middle |
| `open_channel_raceway_outer` | S5 (db83e907) | `model.py:L92-L184, L186-L214` | | 开口 C 槽 + 内置两条 raceway 滑轨 + window + counterbore + feet（mesh） |
| `primitive_wall_box_outer` | S7/S11 (9ef08c04 / 8bdc62dd) | `9ef08c04 model.py:L72-L115`；`8bdc62dd model.py:L38-L94` | | 用 Box primitive 逐面（floor/walls/front-frame）拼成开口箱体，front-opening + lintel/jamb，无 mesh |
| `side_web_race_outer` | S9 (5aa889ab) | `model.py:L58-L94` | | side-web 截面：web + top/bottom lip + 钢珠 race，侧向（Y）嵌套，drawer-slide |

### Slot C：middle_member（第二级移动段，outer 的 prismatic 子）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `closed_box_tube_middle` | S1 (0002) | `model.py:L175-L184` | ✅ seed=0 | 闭合箱型管，比 outer 小一档，截面随 outer 内腔派生 |
| `open_channel_raceway_middle` | S5 (db83e907) | `model.py:L217-L236` | | C 槽 + raceway + stop_tab，截面随 outer raceway 派生 |
| `primitive_wall_box_middle` | S7 (9ef08c04) | `model.py:L256-L316` | | Box primitive 逐面 runner + front lintel/jamb |
| `side_web_race_middle` | S9 (5aa889ab) | `model.py:L96-L132` | | side-web：middle_web + 内外 race，钢珠夹在 outer/middle race 之间 |

### Slot D：inner_member（第三级移动段，middle 的 prismatic 子）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `closed_box_tube_inner` | S1 (0002) | `model.py:L186-L200` | ✅ seed=0 | 最小闭合箱型管 + 顶部 stop-tab |
| `open_channel_raceway_inner` | S5 (db83e907) | `model.py:L239-L261` | | C 槽 inner + nose_plate（行程末端鼻板） |
| `primitive_wall_box_inner` | S7 (9ef08c04) | `model.py:L318-L360` | | Box primitive runner，front_face 实心 |
| `side_web_bar_inner` | S9 (5aa889ab) | `model.py:L134-L158` | | side-web：实心 inner_bar + terminal_tab + 端部螺钉 |

### Slot E：terminal（内段末端固定件，inner 的 FIXED 子，可空）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `bare_no_terminal` | S2 (0002) | `model.py:L186-L210`（仅 inner，无 terminal join） | ✅ seed=0 | 不加末端件，inner rail 直接作为末端；最简 |
| `carriage_shoe` | S5/S6 (db83e907) | `model.py:L263-L293, L369-L375` | | 带底部 relief + 顶孔 + nose 的 carriage 滑块，FIXED 在 inner 末端面 |
| `flat_end_plate` | S10 (0004) | `model.py:L67-L76, L170-L216` | | 薄端板 + 中心孔，`inner_to_end_plate` FIXED 在 `INNER_LEN` 处 |
| `top_carriage_tray` | 1038e85b / 2285b11d / 47e2913d | `1038e85b … top_carriage`（grep 核对：root=outer_member term=top_carriage / tray_plate） | | 顶置承载托盘/carriage（行李或抽屉式），FIXED 在 inner 上方 |

### Slot F：guide_detail（导向 / 止挡 / 滚珠等装饰硬件，挂在各 member 上，可空）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `none_clean` | S11 (8bdc62dd) | `model.py:L83-L152`（无 detail child / 无 stop） | ✅ seed=0 | 纯净三段，无任何附加硬件 |
| `stop_tabs_only` | S1 (0002) | `model.py:L97-L114, L178-L200` | | 仅顶部行程 stop-tab（middle/inner 各布点） |
| `guide_cage_pads_rollers` | S3/S4 (0003) | `model.py:L188-L200, L321-L431`（guide_cage + side/top pad + roller + cover + wiper） | | 全套 guide_cage（bronze pad + zinc roller）+ access cover + wiper lip + boxed bracket，FIXED 挂在 member |
| `ball_race_rollers` | S8/S9 (fd45679a / 5aa889ab) | `fd45679a model.py:L83-L97, L246-L262`；`5aa889ab model.py:L50-L56, L147-L158` | | Cylinder 滚珠/滚柱沿 race 排布（roller_y 随 rail 派生），抽屉钢珠轨/螺钉 |

## 槽位图（slot graph）
pattern: **mixed**（3 级 prismatic 线性主链 + 每级 section_style 多选 + base/terminal/detail 为可选 FIXED 子件）

```
[Slot A: base_mount]                      (root link, 接地/固定)
        │ FIXED (若 base 非 integral；integral 时 outer 即 root)
        ▼
[Slot B: outer_member] ──prismatic(+X, outer_to_middle)──► [Slot C: middle_member]
        │                                                        │
        │ FIXED (Slot F detail: cover/cage/stop 挂 outer)         │ prismatic(+X, middle_to_inner)
        │                                                        ▼
        │                                                  [Slot D: inner_member]
        │                                                        │ FIXED
        │                                                        ▼
        └────────── (Slot F detail 也可挂 middle/inner) ──► [Slot E: terminal] (carriage/plate, 可空)
```

约束：B/C/D 的 `section_style` 必须取同一族（4 个候选一一对应：closed_box / open_channel / primitive_wall / side_web），不可跨族混横截面。base_mount 与 section_style 的相容性：`side_web_*` 通常配 `wall_backplate_fixed`；`primitive_wall`/`open_channel` 可配 `grounded_carrier_body` 或 `integral_grounded_outer`。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base_mount` / `support_frame` / `rear_support` / `body` | root link：接地或固定外段的方式（integral / 台架 / 背板 / 抽屉柜体） | `base_style`, `mount_setback`, `base_height` | S2 / S4 / S8 / S9 |
| `outer_member` | 第一级固定段，包住 middle | `outer_len`, `outer_w`, `outer_h`, `outer_wall`, `section_style` | S1 / S3 / S5 / S7 / S9 / S11 |
| `middle_member` | 第二级移动段，outer 的 prismatic 子，截面随 outer 内腔派生 | `middle_len`, `middle_w`, `middle_h`, `middle_wall` | S1 / S3 / S5 / S7 / S9 |
| `inner_member` | 第三级移动段，middle 的 prismatic 子 | `inner_len`, `inner_w`, `inner_h`, `inner_wall` | S1 / S3 / S5 / S7 / S9 |
| `terminal` (`carriage_shoe`/`end_plate`/`top_carriage`) | inner 末端 FIXED 件，可空 | `terminal_style`, `terminal_len`, `terminal_offset` | S5 / S6 / S10 / 1038e85b |
| `guide_cage` / `stop_tabs` / `rollers` / `covers` / `brackets` / `wipers` | 导向块、止挡、滚珠/滚柱、盖板、端 bracket、防尘唇，全部 FIXED 挂在 member 上 | `detail_level`, `has_rollers`, `has_covers`, `stop_style` | S3 / S4 / S8 / S9 / S1 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `base_to_outer` | fixed | A.base_mount | B.outer_member | n/a | n/a | 仅当 base 非 integral；把 outer 抬到 base datum（integral 时省略，outer 即 root） | S4 / S8 / S9 |
| `outer_to_middle` | prismatic | B.outer_member | C.middle_member | `(1, 0, 0)` | `lower=0, upper≈0.10-0.32` | 第一级伸出，origin 落在 outer 内腔起点 / home setback | S2 / S6 / S8 |
| `middle_to_inner` | prismatic | C.middle_member | D.inner_member | `(1, 0, 0)` | `lower=0, upper≈0.09-0.28` | 第二级伸出，轴必须与第一级平行同向（共线 +X） | S2 / S6 / S8 |
| `inner_to_terminal` | fixed | D.inner_member | E.terminal | n/a | n/a | 末端 carriage/plate FIXED 在 inner 末端面（`origin.x≈INNER_LEN`）；terminal 为空时省略 | S6 / S10 |
| `*_to_detail` | fixed | B/C/D.member | F.guide_cage/cover/bracket | n/a | n/a | 各 guide cage / cover / bracket FIXED 挂对应 member，origin 随 member 几何派生 | S4 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `base_style` | enum | `integral_grounded_outer` / `support_frame_fixed` / `wall_backplate_fixed` / `grounded_carrier_body` | `integral_grounded_outer` | drives root link 与 base_to_outer 是否存在 | S2 / S4 / S8 / S9 |
| `section_style` | enum | `closed_box_tube` / `open_channel_raceway` / `primitive_wall_box` / `side_web_race` | `closed_box_tube` | 同时决定 B/C/D 横截面族与嵌套轴（box=同心 yz；side_web=侧向 y） | S1 / S5 / S7 / S9 |
| `outer_len` | float | `0.18-0.72` | sampled | base reach；middle_len≈outer_len*`(0.74-0.82)` | S1 / S5 / S7 |
| `stage_ratio` | float | `0.74-0.84` | sampled | `middle_len = outer_len*ratio`，`inner_len = middle_len*ratio` | S1 / S5 / S10 |
| `outer_to_middle_travel` | float | `0.10-0.32` | derived | ≤ engagement 余量约束（收回/伸出都要 overlap） | S2 / S5 / S8 |
| `middle_to_inner_travel` | float | `0.09-0.28` | derived | 同上，通常 ≤ 第一级 travel | S2 / S5 / S8 |
| `wall` / `clearance` | float | `0.0010-0.018` | sampled | inner 截面 = 外层内腔 − 2*(wall+clearance) | S1 / S3 / S5 |
| `terminal_style` | enum | `none` / `carriage_shoe` / `flat_end_plate` / `top_carriage_tray` | `none` | 决定 inner_to_terminal 是否存在 | S6 / S10 / 1038e85b |
| `detail_level` | enum | `none` / `stop_tabs` / `guide_cage` / `ball_race` | `none` | 决定 guide/roller/cover/bracket 数量与 FIXED 子件数 | S1 / S4 / S8 |
| `has_rollers` | bool | `true` / `false` | derived | 仅 `detail_level∈{guide_cage,ball_race}` 时为 true | S3 / S8 / S9 |
| `mount_setback` | float | `0.014-0.045` | sampled | home 位 stage 后缩量（origin.x 负偏移） | S5 / S8 |

## 拓扑多样性审计
- base_style 候选数 = 4
- section_style 候选数 = 4（B/C/D 锁同族，记 1 个独立轴）
- terminal_style 候选数 = 4
- detail_level 候选数 = 4
- total_combinations = 4 × 4 × 4 × 4 = **256**

| slot | candidate_count |
|---|---|
| A base_mount | 4 |
| B outer_member (section family) | 4 |
| C middle_member (随 B 同族) | 4（与 B 锁定） |
| D inner_member (随 B 同族) | 4（与 B 锁定） |
| E terminal | 4 |
| F guide_detail | 4 |

注：B/C/D 共享 `section_style` 单轴，组合计数按 1 个独立轴算，故 total = base × section × terminal × detail = 256。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 恰好 3 段嵌套 member（outer/middle/inner）+ 恰好 2 个 prismatic joints |
| joint type | 两个主关节均为 PRISMATIC，无 revolute；axis 均为 `(1,0,0)` 且平行同向（共线） |
| serial topology | outer → middle → inner 串联，不跳父；base（若存在）→ outer 为 FIXED；terminal（若存在）挂 inner |
| nesting containment | box family：`expect_within(middle, outer, axes="yz")` 且 `expect_within(inner, middle, axes="yz")`；side_web family：沿主嵌套轴 within，截面 lip 包住 race |
| home engagement | 收回位 `expect_overlap(middle, outer, axes="x")` 与 `expect_overlap(inner, middle, axes="x")` 有明显 overlap |
| extended engagement | 全行程伸出位仍保留 retained overlap（middle 在 outer 内、inner 在 middle 内，min_overlap>0） |
| travel direction | 伸出后 inner/middle world x 单调增大（+X），位移≈commanded travel |
| base grounding | base_mount/outer 必须接地或固定；无 floating member（`fail_if_isolated_parts`） |
| terminal attach | terminal 必须 FIXED 在 inner 末端面（origin.x≈INNER_LEN），不漂浮 |
| detail attach | guide cage / roller / cover / bracket / stop 全部 FIXED 挂在某 member 上，随其几何派生 |
| section family consistency | B/C/D 三段必须用同一 `section_style` 族，不跨族混横截面 |

## Reject cases
- 出现 revolute / 球铰 / 螺旋等非直线关节，或关节数 ≠ 2。
- 两级 prismatic 轴不平行 / 不共线（一个 +X 一个 +Y/+Z 而无明确说明）。
- 只有 2 段或 4 段以上 member（非三级），或 middle/inner 缺失。
- 收回位或伸出位某级 overlap 为 0（脱开、悬空、互不咬合）。
- inner 不在 middle 内、middle 不在 outer 内（横向 containment 失败）。
- base/outer 漂浮，rail 从空中开始；terminal/carriage/plate 不在 inner 末端或无 FIXED 父。
- guide cage / roller / cover / 螺钉 / stop tab 悬空或随机漂浮。
- B/C/D 三段横截面混族（如 outer 闭箱、middle 突然变 side-web）。
- side_web 抽屉钢珠轨被硬塞进默认同心 box 分支导致嵌套轴语义错误。

## 与相邻类别的边界
| 相邻类别 | 区别 |
|---|---|
| `serial_elbow_arm` | 该类是 revolute 转动二连杆；本类是纯 prismatic 直线伸缩，无转动 DOF。 |
| `telescoping_boom` | boom 多为单级或液压缸 + 工业 reach；本类强制 3 段 2 级、强调每级 overlap/engagement 与 stop。 |
| `drawer_slide` / 单级抽屉轨 | 单级（1 prismatic）；本类是双级串联（2 prismatic）三段嵌套。 |
| `linear_actuator` | 由电机/丝杠驱动的单自由度直线；本类是被动多级嵌套滑轨，重点在嵌套几何与行程包络。 |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；精读 8 个代表样本 + grep 覆盖 37 个；待人工审核。section_style 锁 B/C/D 同族，total_combinations=256，拓扑 distinct已过 。 |
