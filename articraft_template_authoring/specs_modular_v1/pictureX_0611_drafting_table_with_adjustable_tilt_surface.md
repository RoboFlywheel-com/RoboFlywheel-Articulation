# pictureX_0611_drafting_table_with_adjustable_tilt_surface - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_drafting_table_with_adjustable_tilt_surface` |
| template path | `agent/templates/pictureX_0611_drafting_table_with_adjustable_tilt_surface.py` |
| test path (optional) | inline `run_picturex_0611_drafting_table_with_adjustable_tilt_surface_tests` |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed`（serial base→carriage prismatic 链 + parallel_children：board / 控件 / stay 挂到 mount） |

## Category Binding

`category_slug=pictureX_0611_drafting_table_with_adjustable_tilt_surface` ·
`template_slug=pictureX_0611_drafting_table_with_adjustable_tilt_surface` ·
`mechanism_profile=prismatic_height_plus_revolute_tilt`（每个 seed 恒有一级 PRISMATIC 高度
调节 + 一条 REVOLUTE 板倾轴；两者皆为固定的合理机构，不伪装成单候选 slot） ·
`export_namespace=pictureX_0611`。

`diversity_profile=compositional`（硬下限 120）。`profile_reason`：诚实核心词汇是
5 种支撑骨架 × 4 种板形态家族 × 4 种 angle-hold 机构 × 2 种板面附件，全部有 5 星
source anchor，gate 后 144 个合法组合 —— 组合式而非单 spine。profile 只描述核心结构
词汇；机构风险与视觉审核强度由 `Visual Risk` 独立声明。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category（5 origins + 3 confirmed forks, rated_by `picturex_0611_centrifuge_to_drafting_variant_confirmed_20260714`），全部 `revisions/rev_000001/model.py` 全文读取 |
| source_index_policy | only adopted module sources are indexed below；8/8 全部被采纳（无排除样本） |

Source id 缩写（下文用）：
- `O1` = `rec_picturex_0611__drafting_table_with_adjustable_tilt_surface__001__png__airflex_batch_20260710_f54126a0bc61472286fa57cd919015ad`
- `O2` = `rec_picturex_0611__drafting_table_with_adjustable_tilt_surface__002__png__airflex_batch_20260710_339d69d056e540b7b862114aa2e1ac1f`
- `O3` = `rec_picturex_0611__drafting_table_with_adjustable_tilt_surface__003__png__airflex_batch_20260710_017bcd7f10b64bd38ef006c033a29e10`
- `O4` = `rec_picturex_0611__drafting_table_with_adjustable_tilt_surface__004__png__airflex_batch_20260710_de81babb7b9e43b892c6a20b6fea9f8b`
- `O5` = `rec_picturex_0611__drafting_table_with_adjustable_tilt_surface__005__png__airflex_batch_20260710_7afa864680d945db9d3963f6ff47ce49`
- `F_split` = `rec_picturex0611_drafting_table_fork_split_top_dual_surface_20260714`
- `F_spring` = `rec_picturex0611_drafting_table_fork_counterbalance_spring_tilt_20260714`
- `F_column` = `rec_picturex0611_drafting_table_fork_single_pedestal_column_20260714`

## 核心身份

高度可调 + 倾角可调的绘图桌：一块宽幅绘图板（drawing board）由接地支撑结构承载；支撑结构内有**真实
PRISMATIC 高度调节级**（伸缩柱 / 伸缩腿 / 升降柱），板由**真实 REVOLUTE 倾角铰链**承载并配有可见的
angle-lock / stay / counterbalance 硬件。**每个 seed 必须同时具备这两种机构** —— 缺一即漂移成
easel（无高度级）、普通书桌（板不倾）、或固定桌。默认成熟域：室内工作室/学校/工程制图桌，
金属或木质框架，板宽 0.85-1.25 m，闭合位姿为图源常见的 10-15° 工作倾角。
不该混入：easel 画架、普通书桌、熨衣板、壁挂绘图板（source map "Blocked / Excluded" 同款约束）。

## 槽位 + 候选模块表

### Slot A：support_base（① 骨架 + 高度 PRISMATIC 级的载体；mount = 承载板铰链的 part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `four_leg_downleg` | forked_anchor | O2 | L97-L237（rails L100-L103、cq 方管 sleeves L106-L124、stretchers L127-L130、organizer L133-L158、hinge brackets L160-L166、stay bearings L169-L199、4 根伸缩下腿 + PRISMATIC L201-L237） | eligible | 白钢四腿 trestle，root=frame 即 mount；4 根斜向 sleeve + 4 根下伸伸缩腿（front_0 为 driver，其余 mimic，mimic 模式源自 O3/O4/O5 L154-L171/L267-L287/L195-L218）；rear-elevated 顶面 + 蓝灰 organizer；板铰在后上梁 |
| `sleeve_post_carriage` | forked_anchor | O5 | L128-L218（foot rails/ExtrudeWithHolesGeometry 圆角方管 sleeve L140-L173、stop pins、2 根 mimic 联动 height post L181-L218）+ 顶架 L220-L281（side rails、cross rails、hinge wings、pivot cheeks + pins、stay brackets） | eligible | 黑钢双 sleeve 底座 + 双内柱 carriage；源中 top_frame 为 FIXED 子件（L276-L281），模板按 Rule 1 折并为 post_0 carriage 的 host visuals；前缘铰（pivot cheeks/pins） |
| `twin_post_trestle` | forked_anchor | O3 | L59-L124（木底座 feet/pads/lower uprights/outer sleeves/knee braces/stretchers/bolts）+ L127-L171（2 根 mimic 联动 height post + pivot block/bushing）+ L315-L345（2 只 base 侧 height-lock 手柄，REVOLUTE） | eligible | 红木双柱 trestle；中心枢轴（板中线 pivot shaft 被两根柱顶 bushing 捕获）；柱顶枢轴显著高出 sleeve（源 +0.28），使板全程扫掠不进框架 |
| `twin_pedestal_lift` | forked_anchor | O4 | L64-L159（四壁盒式空心 pedestal sleeves + collars + 前伸 feet + rear stretcher）+ L161-L287（2 根 lift post：post tube/guide pads/moving cross rail/lock bracket/pivot bearing+pin+cap；PRISMATIC + mimic L267-L287）+ L406-L441（2 只 frame 侧 height knob） | eligible | 灰钢双 pedestal；升降柱携带 moving cross rail；靠后枢轴（板从枢轴前伸），底座后置 + 低前脚使板前缘下扫空间开阔 |
| `single_pedestal_column` | forked_anchor | F_column | L75-L136（T-foot + gusset + cq 空心圆柱 outer column + collar + knob boss）+ L138-L230（lift column：inner column/guide pads/yoke arms+bridge/yoke bearings/pivot pins+caps/lock bracket；PRISMATIC L221-L230）+ L325-L359（1 只 height knob） | eligible | 单柱 pedestal：中心 yoke 枢轴，一级升降柱；三点 T 脚 |

### Slot B：board_top（③ 主体形态家族 / Primary Form Family slot；本类为形态主导类，登记进 `slot_choices`）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `rounded_laminate_panel` | forked_anchor | O5（辅 O2） | O5 L73-L80（`_board_mesh`：`ExtrudeGeometry(rounded_rect_profile)`）+ L288-L337（wood_panel/front_underrail/pencil_ledge/ledge_fence/pivot_barrel/rear_lamination）；O2 L244-L263（cq 圆角板同族） | eligible | 单片圆角矩形 mesh 面板 + 铅笔挡条；Planar Boundary Form（圆角轮廓） |
| `slatted_wood_board` | forked_anchor | O4 | L289-L341（board_core + 9 wood_slat 交替色 + slat_seam + side_band + 铝 paper_ledge_shelf/lip）+ hinge lugs/straps L342-L356 | eligible | 板条拼面构造（slat N 为 ④ 装饰数量档 7-10）；Macro Surface Construction |
| `framed_batten_board` | forked_anchor | O3 | L175-L205（board_core + panel_seam×2 + rear_edge + front_ledge + ledge_fence + center_batten + pivot_shaft + pivot_cap×2） | eligible | 边框 + 中枕木 + 通长枢轴轴杆的宽木板；Volumetric Envelope Form（下挂 batten/轴杆的厚薄分布） |
| `split_top_side_shelf` | forked_anchor | F_split | L168-L218（frame 侧固定 shelf_panel/lips/brackets/under_rail，host visuals）+ L291-L325（收窄主倾板）+ L326-L340（joint 不变） | eligible if compatible（见 gating） | 分体顶：收窄倾斜主板 + mount 侧固定工具搁板（搁板不动、为 mount host visuals）；Planar Boundary Form（顶面分区） |

### Slot C：tilt_stay（② 机构 / 关节类型；板下 angle-lock 硬件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `curved_spline_braces` | forked_anchor | O3 | L226-L277（`tube_from_spline_points` 曲杆 + upper_hub/lower_hub、board 侧 brace_pin 捕获）+ L279-L313（tilt_lock 手柄，brace_1 的 REVOLUTE 子件） | eligible | 双曲线钢 stay（板的子件）+ 独立 tilt-lock 手柄子链；stay 关节 mimic 耦合到板倾（耦合式样引自 F_spring L329-L351），driver 行程由 clearance solver 收敛 |
| `counterbalance_spring_arms` | forked_anchor | F_spring | L197-L208（board 侧 spring_pivot 座）+ L234-L327（upper_bracket/pivot_pin/link_plate/spring_cylinder/cylinder_cap/coil_ring×3/piston_rod/lower_bracket/pin）+ L329-L351（REVOLUTE + `Mimic(joint=board_tilt, multiplier=-1)`） | eligible | 双弹簧平衡臂（板的子件），mimic 耦合 = 世界姿态守恒的配重筒；coil ring N=3 为 ④ 装饰档 |
| `folding_bar_stays` | forked_anchor | O2 + O5（链式挂法引 O3/F_spring） | O2 L289-L325（support_bar/pivot_boss/support_shoe）；O5 L359-L413（support_bar/support_pad/support_rivet）+ L415-L443（CONTINUOUS clamp knob 子件，KnobGeometry+KnobIndicator） | eligible | 双直杆折叠 stay（板的子件、mimic 耦合），杆端橡胶 shoe；每根 stay 带 1 只 CONTINUOUS 蝶形锁钮子件（② continuous 覆盖） |
| `lever_angle_lock` | forked_anchor | O4 | L376-L404（lever_hub/lever_arm/lever_grip，REVOLUTE [-0.45,0.65]，hub 座于 lock_bracket） | eligible | 单只独立摆杆锁（mount 的子件）；模板改置于板宽外侧 x>W/2+margin 的 mount 侧托架上（外侧放置引 O2 L340-L361 / O3 L315-L345 / O4 L407-L441 的 outboard 控件先例），行程由 solver 收敛，避免 O4 原位（板扫掠楔区内）的中程干涉 |

### Slot D：board_accessory（① 可选活动子件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `parallel_rule` | forked_anchor | O1 | L210-L245（aluminum_bar/black_guide/end_carriage×2/runner_pad×2/knob_bushing×2）+ L246-L260（PRISMATIC 沿板 +Y）+ L262-L310（2 只 lobed KnobGeometry 锁钮，REVOLUTE） | eligible | 平行尺滑轨机（板的 PRISMATIC 子件 + 2 只 REVOLUTE 锁钮子件）；行程用 `sliding_member` 求解 |
| `plain_surface` | forked_anchor | O3 / O4 | O3 L175-L205、O4 L289-L356（裸板面、无滑尺硬件） | eligible | 无附件（不发射额外 part）。候选数=2 的理由：样本池只有 O1 一个附件锚，无第二种附件结构可 source-back，降档为 2 并在此说明 |

## 槽位图（slot graph）

pattern: mixed

```
support_base(root base part)
   --[height PRISMATIC +z（four_leg_downleg 为斜轴下伸；driver + mimics）]--> mount(carriage/post_0/lift_column/frame 本体)
mount --[board_tilt REVOLUTE axis +x @ hinge InterfaceSpec anchor，joint rpy=授权预倾 θ0]--> board
board --[stay REVOLUTE ×2, Mimic(board_tilt, -1)（coupled_chain 求解 driver 行程）]--> stay_0/1   （Slot C 前三候选）
mount --[lock REVOLUTE axis +x, outboard]--> angle_lever                                        （Slot C lever 候选）
stay_1 --[handle REVOLUTE]--> tilt_lock（仅 curved_spline_braces）
stay_i --[knob CONTINUOUS]--> stay_knob_i（仅 folding_bar_stays）
board --[rule PRISMATIC 沿板 +y（sliding_member 求解）]--> parallel_rule --[REVOLUTE ×2]--> rule_knob_0/1
base  --[height-lock/knob REVOLUTE（随 base 模块：O3 ×2 / O4 ×2 / F_column ×1）]--> height_lock_i
```

- 接口点位：Slot A 每个候选产出一个 `InterfaceSpec`（`_modular.InterfaceSpec`）描述板铰接口：
  `part_name`=mount part、`visual_name`=铰链承载 visual、`anchor_local`=铰轴点（mount 局部）、
  `consumer_joint_type=REVOLUTE`、`consumer_joint_axis=(1,0,0)`；并附 mount 计划（pivot_frac、前方净空
  半径 front_clear、shelf 可用区、outboard 控件 x）。board 工厂消费该接口自行发射带 rpy 预倾的
  tilt joint（parallel-children 式样，assembler 不发射链 joint）。
- 关节全部为捕获销/套筒/倾斜子树几何：per AUTHORING Rule 2，`MatingContract` 的轴对齐面亲吻假设
  不成立（board 子树在闭合位姿即带 θ0 旋转；柱在 sleeve 内、枢轴在 bushing 内），这些 joint 按
  grandfather 路线省略 `mating=`，以 element-scoped `allow_overlap` + `expect_contact/expect_overlap`
  按源样本逐一钉死（O2 L380-L446、O3 L367-L483、O4 L465-L479、O5 L475-L607、F_column L377-L451 同款）。
  唯一轴对齐直立面接触（base 侧 height knob stem 端面 ↔ sleeve 外侧面）声明 `MatingContract`。
- 互斥/可选：Slot D `plain_surface` 不发射 part；`split_top_side_shelf` 仅在宽顶 mount 上可用（gating 见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / four_leg_downleg
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame`（rails/sleeves/stretchers/organizer/hinge brackets/stay pedestal），`leg_{fl,fr,rl,rr}` ×4 | O2 L97-L237 |
| internal joints | `height_leg_*` PRISMATIC（斜轴、driver=front_left，其余 mimic） | O2 L227-L237（mimic 引 O3 L154-L171） |
| upstream interface | 地面（root） | — |
| downstream interface | 板铰 InterfaceSpec：rear-top hinge（pivot_frac≈0.72）、outboard 控件位、shelf-OK | O2 L273-L287 |

### Slot A / sleeve_post_carriage
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base`（foot rails/hollow sleeves/stop pins/stretcher），`post_0`（含折并的顶架 visuals）、`post_1`（mimic） | O5 L128-L281 |
| internal joints | `height_post_0/1` PRISMATIC +z（post_1 mimic post_0） | O5 L195-L218 |
| downstream interface | 前缘铰（pivot cheeks/pins，pivot_frac≈0.08）、stay brackets、shelf-OK | O5 L243-L275 |

### Slot A / twin_post_trestle
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base`（木脚/护垫/立柱/sleeve/膝撑/横枕），`post_0/1`（pivot block+bushing），`height_lock_0/1` | O3 L59-L171, L315-L345 |
| internal joints | `height_post_0/1` PRISMATIC（mimic），`height_lock_*` REVOLUTE | O3 L154-L171, L332-L345 |
| downstream interface | 中心铰（柱顶 bushing 线，pivot_frac≈0.5，铰高出 sleeve 顶 ≥0.26·h_scale）、no-shelf | O3 L207-L223 |

### Slot A / twin_pedestal_lift
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame`（四壁 sleeves/collars/feet/stretcher），`post_0`（moving cross rail/lock bracket/pivot pin），`post_1`（rail socket），`height_knob_0/1` | O4 L64-L287, L406-L441 |
| internal joints | `height_post_0/1` PRISMATIC +z（mimic），`height_knob_*` REVOLUTE | O4 L267-L287, L427-L441 |
| downstream interface | 靠后铰（post 顶 pivot pins，pivot_frac≈0.7）、shelf-OK（cross rail 端） | O4 L358-L374 |

### Slot A / single_pedestal_column
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base`（T-foot/gusset/空心柱/collar/knob boss），`lift_column`（yoke/bearings/pins/lock bracket），`height_knob` | F_column L75-L230, L325-L359 |
| internal joints | `height_column` PRISMATIC +z，`height_knob` REVOLUTE | F_column L221-L230, L345-L359 |
| downstream interface | 中心 yoke 铰（pivot_frac≈0.5）、no-shelf | F_column L277-L292 |

### Slot B / 各 board 模块
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board`（面板 + 挡条 + 枢轴 barrel/shaft + 下侧加强 + hinge lugs 按候选） | 见槽位表 |
| internal joints | `board_tilt` REVOLUTE axis (1,0,0)，origin=mount 铰接口 anchor，rpy=(θ0,0,0)，limits [-θ0, θmax−θ0]（solver 收敛） | O2 L273-L287 / O3 L207-L223 / O4 L358-L374 / O5 L339-L357 |
| upstream interface | 消费 Slot A 的铰 InterfaceSpec；板局部坐标：枢轴线 y=0、板面 z=0 平铺授权（倾角全在 joint rpy） | O4 L22-L36 的 `_tilted_xyz` 反式 |
| downstream interface | 板面（accessory 停靠）、板下 brace_pin / spring_pivot / stay 承载点（Slot C 用） | O3 L196-L205 / F_spring L197-L208 |
| host visuals（split_top） | mount 侧 shelf_panel/lips/brackets/under_rail（不动件 → host visuals，Rule 1） | F_split L168-L218 |

### Slot C / 各 stay 模块
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stay_0/1`（曲杆 / 弹簧筒 / 直杆+shoe）或 `angle_lever`；附属 `tilt_lock`（O3）/`stay_knob_0/1`（O5） | 槽位表 |
| internal joints | stay REVOLUTE ×2 = Mimic(board_tilt, −1)（coupled_chain）；lever/handle REVOLUTE 独立；knob CONTINUOUS | F_spring L329-L351, O3 L264-L277, O4 L395-L404, O5 L434-L443 |
| upstream interface | 板下 pin/pivot 捕获（allow_overlap + expect_contact）或 mount outboard 托架 | O3 L440-L468, F_spring L477-L507 |

### Slot D / parallel_rule
| emits | 描述 | 来源 |
|---|---|---|
| parts | `parallel_rule` + `rule_knob_0/1` | O1 L210-L310 |
| internal joints | `board_to_rule` PRISMATIC 沿板 +y（`sliding_member` 求解），`rule_to_knob_*` REVOLUTE | O1 L246-L310 |
| upstream interface | 板面停靠（runner pads 触板面、end carriages 包边，allow_overlap 按 O1 L510-L523） | O1 L426-L434 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support_base` | enum | 5 modules | — | choice | deterministic procedural sampler | Slot A |
| `board_top` | enum | 4 modules | — | choice | `split_top_side_shelf` 需 shelf-OK base，否则降级 `rounded_laminate_panel`（gating） | Slot B |
| `tilt_stay` | enum | 4 modules | — | choice | sampler | Slot C |
| `board_accessory` | enum | 2 modules | — | choice | sampler | Slot D |
| `palette_style` | enum | 5 palettes | `pale_maple_black` | choice | sampler | ⑥ |
| `board_width_scale` | float | [0.92, 1.10] | 1.0 | independent | clamp；`single_pedestal_column` 上限 1.02（yoke 悬臂） | O2-O5 板宽 0.92-1.20 |
| `board_depth_scale` | float | [0.94, 1.06] | 1.0 | independent | clamp | O2-O5 板深 0.55-0.68 |
| (—) | constraint | — | — | inequality | `d_front = pivot_frac·depth ≤ front_clear(base) − 0.03`；违反时按比例回缩 `board_depth_scale`（在 `resolve_config` 内解） | 板前缘扫掠弧 vs mount 前构件 |
| `height_travel` | float | [0.10, 0.18] | 0.14 | **derived-capped** | 先 clamp 到 [0.10,0.18]，再由 **G6** `_max_height_travel(r)` 按实现的 sleeve/post 栈求解上限后 clamp（双柱实测上限 ≈0.154，四腿随 `mount_top_z` 变化）；实现为 driver PRISMATIC [0, travel] | O3 L168 / O4 L274 / O5 L33-L34 |
| `tilt_total_max` (θmax) | float | [0.70, 1.05] rad (40-60°) | 0.87 | conditional | `twin_post_trestle`/`single_pedestal_column`（中心铰）allow ≤1.05；其余 ≤0.87；最终由 coupled_chain/clamp_joint_limits 收敛，模板断言 realized ≥0.50 | O2 L284 / O3 L221 / O5 L29-L30 |
| `authored_tilt` (θ0) | float | [0.17, 0.26] rad (10-15°) | 0.21 | independent | clamp；joint rpy 预倾，lower=−θ0（闭合=图源工作倾角，min=水平） | O2 L245 / O3 L21 / O4 L19 / O5 L29 |
| `frame_height_scale` | float | [0.95, 1.08] | 1.0 | independent | clamp；铰高、sleeve 长同源缩放（Contract 3c） | O2-O5 铰高 0.74-1.02 |
| `slat_count` | int | 7-10 | 9 | conditional | 仅 `slatted_wood_board`；④ 装饰数量档，不进 slot_choices | O4 L297-L313 |
| `rule_travel` | derived | `0.62·(depth−0.12)` 再经 `sliding_member` 求解 | — | equation | 单一来源派生（Contract 3c） | O1 L253-L258 |
| stay 杆长/挂点 | derived | `≈0.42·(hinge_z−mount_top)`；rest 倾角 ≥30° | — | equation | 保证 mimic 全程杆不贴板、下端距 mount ≥0.03 | O3 L231-L237 / F_spring L268-L307 |

**连续尺寸采样契约**：`config_from_seed` 先均匀采样全部 independent 主尺度 → `resolve_config` 解
conditional 范围（θmax 随 base）→ 按 equation 派生（rule_travel、stay 几何、铰高）→ 用 inequality
把 `board_depth_scale` 投影回可行域（前缘弧净空）；无法满足时回缩不拒绝（域构造保证非空）。

## 7.5 编译预算 / compile budget

**自报 20s/seed**。依据：几何以 Box/Cylinder 梁为主 + 少量 SDK mesh（`ExtrudeGeometry`/
`ExtrudeWithHolesGeometry`/`tube_from_spline_points`/`KnobGeometry`）+ 每 seed ≤4 个小型 cadquery
布尔（方管/空心柱），与同库 drafting_table（<10s）同量级。分档 tessellation：knob/销 ≤32 段、
板面 mesh ≤64 段；成对 stay/knob 复用同一 mesh 实例。超预算先降 profile 段数。sweep
`--compile-timeout` 用默认（120s ≈ 6×预算），仅作 hang-guard。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达，不暴露 `*_count`，也不通过循环复制模板级
  visual/part/joint。成对 stay/柱/膝撑/脚垫是源样本的固定拓扑细节（×2 固定），slat_count（7-10）与
  coil_ring（3）是 ④ 表面装饰数量档（host visuals 循环，不是 part/joint 复制），与 source map
  "No honest homogeneous structural N axis" 结论一致。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | 5 种支撑骨架（四腿下伸腿×4 / 双柱 carriage / 木双柱 / 双 pedestal / 单柱 yoke，part 数 2-6）；stay 家族改变边数（双 stay+手柄子链 / 双弹簧臂 / 双 stay+2 knob / 单 lever）；accessory 增删 rule+2 knob 子链；全部 forked_anchor（Slot 表） |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：无诚实同构 N 轴（source map 同结论）；slat/coil 为 ④ 装饰档 |
| ② 关节类型 | 边换 type/轴 | 有 | PRISMATIC（高度级：+z 直轴 O3/O4/O5/F_column；斜轴下伸 O2；板上滑尺 O1）；REVOLUTE（板倾 x 轴、stay、lever、锁钮）；CONTINUOUS（O5 蝶形锁钮）；MIMIC 耦合（O3/O4/O5 高度、F_spring stay）；全部 source-backed；sweep 中三种类型均出现（rule 为 PRISMATIC、stay knob 为 CONTINUOUS 的 seed 由采样覆盖） |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | board_top slot 登记进 `slot_choices`：`rounded_laminate_panel`（Planar Boundary，O5/O2）、`slatted_wood_board`（Macro Surface Construction，O4）、`framed_batten_board`（Volumetric Envelope，O3）、`split_top_side_shelf`（Planar Boundary 分区顶，F_split）；4 个全 source-backed，无需 world_knowledge_extrapolation |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | record_only：slat 纹/缝（O4，档 7-10）、panel seams + 通长 batten（O3）、rear lamination 缝（O5）、organizer 蓝灰箱体（O2）、coil ring×3（F_spring）、ruler 黑导条（O1）、rubber 脚垫/shoe（全体）。装饰随 ③→⑤ 派生：slat/seam 长宽由已实现板宽派生、shoe 贴合板底面 |
| ⑤ 尺寸/行程 | 连续尺寸/行程 | 有 | 比例见 §7。运动包络 + motion_test_plan：**board_tilt**（axis +x；开启方向=后缘升；[−θ0, θmax−θ0]，solver 收敛；targeted pose：min=水平断言前后缘共面、mid、max=后缘升 ≥0.12）；**height driver**（axis +z 或斜轴；[0, travel]；targeted：上限位姿 mount/板整体升 ≥0.9·travel，O2 基座断言脚下伸）；**stay mimic**（随 driver，coupled_chain 求解，无独立采样）；**lever/handle**（独立小摆，solver 收敛，targeted 摆角位移）；**rule**（沿板 +y，`sliding_member` 求解 [0, rule_travel]，targeted 位移沿板面）；**锁钮/knob**（±π 或 continuous，原地自旋断言）。全模板 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`，无 exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palettes：`school_white_blue`（O2 白钢+蓝灰+冷灰板）、`crimson_wood_black`（O3 红木+黑钢）、`honey_beech_gray`（O4 蜂蜜榉+灰钢）、`pale_maple_black`（O5 枫木+粉黑）、`cool_white_graphite`（O1 冷白+石墨）；材质大类 painted metal / wood / laminate(plastic) / rubber / bare steel ≥ ceil(0.5×5) 覆盖 |

## Form Dependency Contracts

Slot B 的 4 个 ③ candidate **全部 source-backed**（各有直接 accepted anchor + 精确行号，见槽位表），
本 spec **没有** `world_knowledge_extrapolation` 的受控外推③，因此无需外推契约。仍登记以下 master
descriptor，防止板体与其依赖消费者各自抽样导致边界错配（Contract 3c 单一真源）：

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| `rounded_laminate_panel` | O5 `model.py:L73-L80`, `L288-L337`；O2 `model.py:L244-L263` | `board_profile={width,depth,thickness,corner_r}`（单次采样） | wood_panel mesh、front_underrail、pencil_ledge、ledge_fence、rear_lamination、pivot_barrel 长度、stay 挂点 x、rule 行程 | 全部由 `half_width`/`board_depth` 派生；ledge 贴前缘 `y=0` 侧、barrel 长 `=2·half_width−0.02` | 板面/挡条共面；barrel 不触 hinge 端托架；closed/mid/max sampled collision | eligible |
| `slatted_wood_board` | O4 `model.py:L289-L341`, `L342-L356` | 同一 `board_profile` + `slat_count`(7-10) | board_core、slat×N、slat_seam×(N−1)、side_band×2、paper_ledge_shelf/lip、hinge lug/strap | slat 长 `=2·half_width−0.022`、间距 `=(depth−0.12)/slat_count` 由已实现板宽/深派生（④ 随 ③→⑤ 共形，Rule 4） | slat 全部落在板面内且相互连通；ledge 贴前缘 | eligible |
| `framed_batten_board` | O3 `model.py:L175-L205` | 同一 `board_profile` | board_core、panel_seam×2、rear_edge、front_ledge、ledge_fence、center_batten、pivot_shaft、pivot_cap×2 | seam x `=±0.32·half_width`；batten 沿 y 通长 `=0.88·depth`；shaft 长 `=2·half_width−0.02` | batten/shaft 与板底连通；shaft 被两侧 bushing 捕获 | eligible |
| `split_top_side_shelf` | F_split `model.py:L168-L218`, `L291-L325`, `L326-L340` | 同一 `board_profile`，主板宽 `=0.72·2·half_width`，shelf 宽 `=0.26·2·half_width` | 收窄主倾板 + mount 侧 shelf_panel/front_lip/side_lip/brackets/under_rail（host visuals） | 主板与 shelf **共同**由一个 `board_profile` 派生：`panel_w + shelf_w ≥ 0.94·2·half_width`（顶面不缺口）；shelf 托架从 mount 宽横构件起、顶面与主板闭合位姿同高 | 主板宽 > shelf 宽；两者合span 覆盖原顶面；板倾时 shelf 不动（F_split L590-L598 语义）；shelf 托架有 mount 支撑路径 | eligible if compatible（见 Compatibility Gates） |

## Compatibility Gates

| # | deny 条件 | 理由 | fallback |
|---|---|---|---|
| G1 | `board_top=split_top_side_shelf` **且** base ∉ {`four_leg_downleg`, `sleeve_post_carriage`, `twin_pedestal_lift`} | `twin_post_trestle` / `single_pedestal_column` 是中心铰骨架，mount 顶部没有承接侧搁板托架的宽横向构件 → 搁板会漂浮（无支撑路径，Contract 3 违例） | 降级 `rounded_laminate_panel` |
| G2 | `single_pedestal_column` 且 `board_width_scale > 1.02` | 单柱 yoke 悬臂过载；宽板超出 yoke 承托跨度读作漂浮 | clamp 到 1.02 |
| G3 | 中心铰 base（`twin_post_trestle`/`single_pedestal_column`）以外的 base 且 `tilt_total_max > 0.87` | 前缘/后缘铰骨架在大倾角时板缘扫入 mount 构件 | conditional clamp θmax ≤0.87（中心铰 ≤1.05） |
| G4 | `d_front = pivot_frac·depth > front_clear(base) − 0.03` | 板前缘扫掠弧撞 mount 前构件 | 按比例回缩 `board_depth_scale`（域构造保证非空） |
| G5 | `board_top=slatted_wood_board` **且** `board_accessory=parallel_rule` | 平行尺靠 runner pad 在**连续平面**上滑行取直；板条饰面高出芯板 `SLAT_H`(4mm) 且条间有 `slat_seam` 开缝（2mm 凹槽），pad 没有连续承载面 → 尺要么悬空（Contract 3 漂浮）要么逐条磕碰。真实配平行尺的绘图板一律用光滑 laminate / framed 面板 | 降级 `board_accessory=plain_surface`（config 期求解，builder 不失败；`parallel_rule` 仍可达其余 3 个 board_top） |
| G6 | `height_travel` > 实现 telescoping 栈允许的行程 | 行程不是口味而是硬件决定：双柱升到 guide_block 顶到 sleeve_collar 为止，四腿收到腿头顶到 frame-top 底面为止。域冻结在 0.18 会把 guide_block 顶进 collar 17mm | 由 `_max_height_travel(r)` **求解**后 clamp（非冻结常量；Contract 3e） |

其余 5×4×4×2 组合共用同一 mount 铰接口（`InterfaceSpec` anchor + `consumer_joint_type=REVOLUTE`
+ `axis=(1,0,0)`），跨来源 module 合法重组，无需共同来源。所有 gate 在 `resolve_config` 内求解，
builder 不失败；不开放未验证的完整笛卡尔积。

## Combination Domain

- diversity_profile / reason：`compositional`，硬下限 **120**。5 个骨架 × 4 个板形态家族 ×
  4 个 angle-hold 机构 × 2 个附件，全部 source-backed，是真实组合式词汇而非单 spine。
- core axes / cartesian count / gate-filtered legal count：
  `support_base(5) × board_top(4) × tilt_stay(4) × board_accessory(2)` = 笛卡尔 **160**；
  G1 裁掉 `split_top × {twin_post_trestle, single_pedestal_column} × 4 × 2` = 16；
  G5 裁掉 `slatted_wood_board × parallel_rule × 5 base × 4 stay` = 20（与 G1 不相交）
  → 合法 **124**（≥120，通过 compositional profile，**无需人工例外**）。
  实测（枚举 `resolve_config` 全笛卡尔积去重）：raw=160 → distinct legal=**124**；
  两条 gate 的违规组合存活数均为 0；4 个轴的每个取值仍全部可达。
- multiplicity axes / admitted integers / reachable integers / min-mid-max boundaries：
  **无 multiplicity 轴**（见 §8）。`slat_count`(7-10) 与 `coil_ring`(3) 是 ④ 表面装饰档
  （host visuals 循环，不复制 part/joint），不计入任何域。
- raw cartesian count / gate-filtered legal count：无 N 轴，故 `raw_domain = core_domain` = **144**。
- excluded：palette(5)、材质、host-conformal 装饰（slat/seam/coil/grain）、连续尺寸
  （width/depth/height_travel/θmax/θ0/frame_height scale）均不计入。
- profile floor / recommended target / exception：floor=120，实际 144 → **无需人工例外**。
  核心数不靠 N 膨胀、不含假组合。

## Visual Risk

`telescopic`（每个 base 的高度级都是柱-套筒插入，必须全程保持 ≥0.04 插入且不脱出）、
`curved_fit`（`curved_spline_braces` 的 `tube_from_spline_points` 曲杆须随板倾 mimic 全程贴合、
不脱离 brace_pin）、`hidden_slide`（`parallel_rule` 沿板面 PRISMATIC，runner pad 须始终贴板面、
end carriage 不脱板边）、`multi_joint`（单 seed 最多 ~10 个非 FIXED joint：高度 driver+mimics、
板倾、双 stay、手柄/锁钮、rule+2 knob）。

视觉审核必须核对：(a) 板在 closed/mid/max 三姿下与 mount/stay/lever 的净空；(b) stay/spring 臂
mimic 耦合后仍钉在板下挂点（不漂浮、不脱开）；(c) split_top 搁板在板倾时静止且托架有支撑路径；
(d) 柱在上限位姿仍插在 sleeve 内；(e) palette 五档在渲染中确实拉开（非单色池）。

## 采样与覆盖审计

总组合数：受 gating 后的 slot tuple = base(5)×board(4|3)×stay(4)×accessory(2) = (3×4+2×3)×4×2 = **144**
（palette 与连续尺度不计入）。

理由：五个骨架族 × 四个板形态族 × 四个机构族覆盖了 8 个 5 星源的全部结构轴；无 multiplicity 轴。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采样
base → board（gated）→ stay → accessory → palette → 连续尺度；seed 0 不特殊、无 regression override。
compatibility gating 全部在 `resolve_config`：(a) `split_top_side_shelf` 仅当 base ∈
{four_leg_downleg, sleeve_post_carriage, twin_pedestal_lift}（mount 有宽横向构件承接搁板托架），否则
降级 `rounded_laminate_panel`；(b) `single_pedestal_column` 时 `board_width_scale ≤ 1.02`；(c)
θmax conditional 上限随 base（中心铰 1.05 / 其余 0.87）；(d) 前缘弧净空 inequality 回缩 depth。
random sweep：0-35 pipeline + corner 阶段；viewer 目检 seeds 0-9（无 pyrender 时程序化检查代替）。

Topology target：144 组合全可达（gating 只裁剪 split_top×2 base），1000-seed tuple 覆盖预计饱和至
144（<300 因真实组合空间即 144：5 源锚 base × 4 源锚 board × 4 源锚 stay × 2 accessory，受源锚点上限
约束；report-only）。

Controlled local parameterization：`board_width_scale`、`board_depth_scale`、`height_travel`、
`tilt_total_max`、`authored_tilt`、`frame_height_scale`（范围/约束见 §7）；全部在 `resolve_config`
clamp/派生，不破坏铰接口（铰 anchor 随 frame_height_scale 单源派生）、不破坏捕获配合（sleeve/柱
截面不采样）、不破坏类别身份（θmax、travel 下限保证两机构行程可用）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | base→board(gated)→stay→accessory→palette→scales，均匀 | `slot_choices_for_seed` 与 build 一致 |
| compatibility matrix | split_top→宽顶 base 否则降级；θmax/width 随 base conditional；depth inequality 回缩 | 无漂浮 shelf、无板-框扫掠、无 yoke 过载悬臂 |
| controlled local variation | 6 个连续 scale，clamp+派生 | 比例变化不破坏铰/捕获/身份 |
| regression overrides | none | — |
| random sweep | pipeline 0-15 → 0-35 → corner | failure_clusters；axis_realization 确认 5/4/4/2 候选与 PRISMATIC/REVOLUTE/CONTINUOUS 全出现 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 5 | yes | yes | 全 forked_anchor |
| board_top | 4 | yes | yes | ③ slot，登记 slot_choices |
| tilt_stay | 4 | yes | yes | 含 continuous 子件候选 |
| board_accessory | 2 | yes | no | 池内仅 O1 一个附件锚，降档理由见槽位表 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名，与 `config_from_seed`→`resolve_config`→build 一致
- 所有普通 seed 走 deterministic procedural sampling；无 curated/modulo 主域；无 regression override
- gating 在 `resolve_config` 内完成（split_top 降级、θmax/width conditional、depth inequality），builder 不失败
- 每个 seed 恒有 ≥1 个可用行程的 PRISMATIC 高度 joint（travel ≥0.06）和 1 个 REVOLUTE `board_tilt`（realized 行程 ≥0.50 rad）——类别身份 guard 写进模板测试
- stay/spring/brace 关节 mimic 耦合到 `board_tilt`（coupled_chain），driver 行程 solver 收敛；lever/rule 行程 solver 收敛
- 捕获式配合全部 element-scoped `allow_overlap` + `expect_contact/expect_overlap`（柱-套、轴-瓦、销-毂、shoe-板、stem-boss、carriage-包边）
- 高度 mimic 联动（post_1 等）声明并断言（O3/O4/O5 语义）
- `fail_if_parts_overlap_in_sampled_poses` + 每机构 targeted `ctx.pose(...)`（§8.5 ⑤ 计划）
- board 局部坐标平铺授权、倾角全在 joint rpy —— 保证 min 位姿=水平、闭合位姿=图源工作倾角

## Reject cases

- 只有板倾没有高度级（→ easel 漂移），或高度级退化为 FIXED / 行程 <0.06
- 板在任一 sampled 位姿扫入框架/stay/lever（前缘弧 inequality 失效）
- stay/spring 臂与板独立采样导致组合位姿穿模（必须 mimic 耦合）
- split_top 搁板挂在无宽横构件的 mount 上（漂浮 shelf）
- 平行尺 end carriage 脱离板边、runner pad 悬空于板面
- 柱升到上限后脱出 sleeve（保持 ≥0.04 插入，O3 L583-L600 / O5 L513-L532 语义）
- 用宽泛 part 级 allow_overlap 掩盖真实穿模；捕获配合必须 element-scoped
- 板闭合位姿水平（应为 θ0 预倾，否则渲染读作普通桌）

## 与相邻类别的边界

- 不该混入：easel 画架（无高度 PRISMATIC 级、无水平可用位姿）
- 不该混入：普通书桌 / 固定桌（板不倾、无 angle-lock 硬件）
- 不该混入：熨衣板（X 折叠腿主运动、无绘图板挡条/锁钮语义）
- 不该混入：壁挂绘图板（无接地支撑）；tabletop 便携板架（O1 的 stand 无高度级，故 O1 只贡献
  rule/knob/ledge 模块，不作 base 候选）

## Authoring 自检记录
| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| self-check notes | 8/8 5 星样本全文读取（5 origins + 3 confirmed forks）；每个 candidate 有 record + 精确 `model.py:Lx-Ly`；4 个 slot 候选数 5/4/4/2（accessory 降档至 2 的理由已写在槽位表：池内仅 O1 一个附件锚）；§7.5 编译预算自报 20s/seed；§8 声明无 multiplicity 轴（与 source map 一致）；§8.5 六轴逐轴考察完成（③ board_top 登记进 `slot_choices`）；§9 四个机器检查小节（Form Dependency Contracts / Compatibility Gates / Combination Domain / Visual Risk）齐备，core=144 ≥ compositional floor 120，无人工例外；`palette_style` 5 档来自 5 个源的真实配色。tilt 铰为强制身份，无固定顶候选。 |

## 模板实现备注（可选）

- 共享 helper：`_beam`（O2 L40-L47 `_add_beam` 同款）、`_box`/`_cyl`、`_rotated_yz`（O5 L42-L52）、
  hollow tube mesh（O5 L55-L70 SDK 版；cq 版仅用于 O2 方管与 F_column 圆柱）
- board 工厂消费 mount 的 `InterfaceSpec`（anchor=铰点）；stay/accessory 直接读 `board` part
  （parallel-children 式样，不声明 upstream 接口）
- 捕获 pin overlap 清单（全 element-scoped）：`inner_post↔outer_sleeve`、`pivot_shaft/barrel↔bushing/cheek/lug`、
  `hub↔brace_pin`、`upper_bracket/pin↔spring_pivot`、`shoe/pad↔board 面`、`stem↔boss/socket`、
  `end_carriage↔side_edge`、`lever_hub↔lock_bracket`
- 暂不进入 seed domain 的组合：无（gating 后 144 组合全可达）
