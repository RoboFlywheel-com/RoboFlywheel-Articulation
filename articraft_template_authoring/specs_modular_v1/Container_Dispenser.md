# container_dispenser (pump / press-top soap·lotion·sanitizer dispenser bottle) — Modular Spec

> 来源小类：`picture/Container/Dispenser`（articraft_data 上游 Container/Dispenser fork-variant pool）。
> 参考图：clear hand-wash / lotion dispenser bottle — 透明圆瓶身 + 前贴标签 + 螺纹波纹 collar + 外露按压泵头 + 长水平 swivel spout + 瓶内可见直 dip tube（**无瓶盖/dust cap**）。
> 引用 `model.py:Lx-Ly` 来自各样本 `articraft_data` 当前 `data/records/<id>/revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`bottle`/`bottle_shell` / `collar`/`collar_shell` / `pump_head`/`pump_head_shell` / `spout`/`spout_shell` / `dip_tube` / `lock_ring`/`lock_ring_shell` / `pump_press` / `spout_swivel` / `lock_ring_twist` / `bottle_to_collar` / `pump_to_dip_tube` 等），行号仅作定位。
> **建模注记**：8 个 5★ 样本全部是同一份参数化 `build_object_model()` 的 fork（各自一个 `VARIANT` 常量切换 body mesh / pump 分支 / collar mesh / dip_tube path）。part tree 在 `VARIANT` 间是**稳定的固定 named slots**（bottle → collar → pump_head → {spout, dip_tube}），变化轴是 4 个独立功能层 mesh / 机构。因此采用 `parallel_children` 模板，4 轴笛卡尔积撑开拓扑多样性。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_dispenser` |
| template path | `agent/templates/Container_Dispenser.py` |
| test path (optional) | `tests/agent/test_container_dispenser_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + pump_head + neck_collar + dip_tube；collar / pump_head / dip_tube 挂到 root `bottle` 共同 parent，按压泵头链 collar→pump→spout/dip_tube，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent `rec_container_dispenser_v01` + 7 qwen fork 变体）|
| read_count | 8（全部全文读 model.py：parent 完整链 + 各 fork 的独有 `VARIANT` 分支 mesh / joint / tests）|
| read_scope | all 5-star samples in this category（无抽样；源映射列出的 8 个记录全部存在且评分 5★）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

阅读要点（fork 结构）：
- parent `rec_container_dispenser_v01`（`VARIANT="parent"`）= 基线全链：`bottle`(`bottle_shell` revolve 圆瓶 + `front_label` + `liquid_fill`) → `collar`(`collar_shell` 28-rib lathe，`bottle_to_collar` FIXED) → `pump_head`(`pump_head_shell` lathe + disk，`pump_press` PRISMATIC +Z lower=-PRESS_TRAVEL) → `spout`(`spout_shell` tube，`spout_swivel` REVOLUTE +Z ±π) + `dip_tube`(`pump_to_dip_tube` FIXED，直 spline 入瓶)。这套 part/joint 名在所有 fork 间稳定。
- body fork：`square_body`(`VARIANT="chunky_rect_body"` → `_chunky_rect_bottle_mesh` 方块 loft)、`oval_body`(`VARIANT="flattened_oval_flask"` → `_flask_bottle_mesh` 扁椭圆 flask)、parent 内置的 `_square_bottle_mesh`/`_oval_bottle_mesh`（同一 round body 的 footprint 变体）。
- pump fork：`long_spout_lotion_pump`(`VARIANT="long_spout_lotion_pump"` → 高 plunger stem + 椭圆 press button + 长弯 spout)、`detached_pump_insert`(`VARIANT="service_lift"` → 泵 stem 加 seal/guide 环 + `pump_press` lift 行程 lower=-0.012 upper=+0.015 半抽出可服务)、`twist_lock_pump`(`VARIANT="lock_twist_collar"` → `_lock_ring_mesh` cam-slot 锁环 + pump stem 上 engagement pins + `lock_ring_twist` REVOLUTE +Z 0..π/2)。
- collar fork：`ribbed_collar`(`VARIANT="oversized_industrial_collar"` → `_oversized_collar_mesh` 两层工业 stepped collar：下层螺纹 ribs + 上层 flutes + knurl band + lip)。
- dip_tube fork：`curved_dip_tube`(`VARIANT="s_curved_tube"` → S 形 5-point spline，pale-blue tube material)。

冗余/分流说明：
- 8 个 fork 只在 4 个功能层各动一处（body mesh / pump 机构 / collar mesh / dip_tube path），其余链完全相同 → 自然映射成 4 个正交 slot。
- material / 颜色（clear_plastic / pale_soap / white_label / warm_white / soft_grey / milky_tube / pale_blue_tube）是 palette，不计 slot_choice（见 §7 `palette_style`）。
- parent 文件里残留 `long_trigger_foam_head`(trigger lever 泡沫枪) 和 `detached_dip_tube_pump` 两个 `VARIANT` 分支，但**没有对应 5★ 记录**（源映射未列、record 不存在），按 hard rule **不采纳为 candidate**（不写进 slot 表）；其 `_trigger_mesh` 还是未定义符号。仅采纳有真实 5★ 记录支撑的 module。

## 核心身份

按压式 / 压泵式分装瓶（pump dispenser bottle）：一只直立中空透明（或半透明）瓶身，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。瓶身由 CadQuery `LatheGeometry`(圆 revolve) 或 `_loft_sections`(方块 / 椭圆 loft) 发射为带肩收 neck 的 shell，前面贴一块 `front_label`，瓶内可见 `liquid_fill` 体与一根 `dip_tube`。瓶口螺纹颈上旋一只 ribbed `collar`（FIXED visual），collar 之上是**外露的按压泵头**（**主活动语义**）：`pump_head` 经 `pump_press` PRISMATIC +Z 下压回弹（标称行程 ~18mm），泵头侧出一只 `spout`，经 `spout_swivel` REVOLUTE +Z 水平回转（±π）；某些变体泵头另有机构（高 plunger 长 spout / 半抽出 service lift / twist-lock 锁环）。dip_tube FIXED 挂泵头，直插或 S 形穿过透明瓶身。默认成熟域：单瓶单泵单 spout（无嵌套 / 无 multiplicity / **无瓶盖闭合件**）。

不该混入：
- 独立泵头机构本体（standalone pump，无瓶身——是单独的 `container_pump` 小类）：dispenser 一定带完整瓶身 + dip_tube + label；container_pump 是泵机构特写/替换件。
- 大容量洗衣液瓶（laundry detergent bottle，常带提手 + 量杯盖 / flip cap + 倒料颈，宽肩大容量）：是 `container_laundry_detergent_bottle`；dispenser 是小台面分装瓶，核心是按压泵 + swivel spout，**没有量杯 / 提手 / 倒料盖**。
- 细颈高瓶 / 滴管瓶 / 喷雾瓶：dispenser 的身份是**按压泵 + 水平 swivel spout**，不是 dropper、trigger-spray gun 或 screw cap bottle。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 root `bottle` 的 mesh 属性（一次 `_bottle_mesh(body_form)` 发射 `bottle_shell` + `front_label` + `liquid_fill`），不是独立串联 slot。`neck_collar` 发射 `collar`（FIXED 挂 bottle）。`pump_head` 发射按压泵链（挂 collar / lock_ring）。`dip_tube` 是 pump 的 FIXED child mesh path。四轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_form（瓶身形态 / 足迹——root `bottle` 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_clear_bottle（基线）| rec_container_dispenser_v01 | `_round_bottle_mesh` L57-87（`bottle_shell` revolve + body ribs + neck threads）| eligible if compatible | 圆软肩透明分装瓶（revolve LatheGeometry，body 波纹 ribs + neck thread torus），收肩居中 neck |
| square_rounded_body | rec_container_dispenser_var_square_body_qwen | `_chunky_rect_bottle_mesh` L154-197（`_rounded_rect_points` 圆角方截面 `_loft_sections` + box `liquid_fill`）| eligible if compatible | 矮胖圆角方块瓶：宽平方面板 + 宽肩 + 圆角竖棱，box 形 liquid_fill，更短身形 |
| oval_flask_body | rec_container_dispenser_var_oval_body_qwen | `_flask_bottle_mesh` L184-212（`_flask_ellipse` 多段 ellipse loft，腰部收）+ `_elliptical_liquid_mesh` L383-405 | eligible if compatible | 高扁椭圆 flask：宽:深 ≥3:1 透镜状正面，slim 侧面，圆 neck 接 collar，椭圆 liquid_fill |
| narrow_oval_footprint | rec_container_dispenser_v01 | `_oval_bottle_mesh` L137-150（`VARIANT="tapered_oval_body"` 分支，前后扁椭圆 loft）| eligible if compatible | 前后扁椭圆瓶（width > depth·1.35），broad 正面 + 浅侧深，比 oval_flask 矮 |
| square_prism_footprint | rec_container_dispenser_v01 | `_square_bottle_mesh` L130-134（`VARIANT="square_prism_body"` 分支，宽:深≈1 圆角方 loft）| eligible if compatible | 等宽深方棱柱瓶（broad flat footprint，dx≈dy），圆角方截面 base→shoulder→neck loft |

硬约束记录：body_form 5 candidate（达 3-6 目标）。全部 revolve / loft 中空开口瓶身，共享 neck 收肩 + `front_label` + `liquid_fill` helper，只换 footprint（圆 / 圆角方 / 扁椭圆 / 方棱柱）/ 高宽比 / loft 截面族。narrow_oval_footprint 与 square_prism_footprint 取自 parent 内置的 `tapered_oval_body`/`square_prism_body` 分支（parent 文件实现，5★ parent 记录覆盖）。

### Slot B：pump_head（**主开合机构槽**——按压泵头动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| press_swivel_pump（基线）| rec_container_dispenser_v01 | `_pump_head_mesh` L207-230（lathe stem+shoulder+disk）+ `pump_press` PRISMATIC +Z L296（lower=-PRESS_TRAVEL upper=0）+ `spout_swivel` REVOLUTE +Z L307（±π）| eligible if compatible | 外露按压泵 + 水平 swivel spout：`pump_press` 下压 18mm 回弹（PRISMATIC +Z）+ `spout` 经 `spout_swivel` REVOLUTE +Z 回转。1 PRISMATIC + 1 REVOLUTE，spout 独立 child |
| long_spout_lotion_pump | rec_container_dispenser_var_tall_plunger_long_spout_qwen | `_pump_head_mesh` L207-262（高 plunger stem + 椭圆 press button merge）+ `_spout_mesh` L295-318（长 4-point 弯 spout + 下喷 nozzle）+ `pump_press` PRISMATIC L375 + `spout_swivel` REVOLUTE | eligible if compatible | 高 plunger lotion 泵：更高 stem + 椭圆按压盘，长弯水平 spout 远伸出瓶身（reach 0.055-0.10），仍 PRISMATIC press + REVOLUTE swivel |
| service_lift_pump | rec_container_dispenser_var_detached_pump_insert_qwen | `_pump_head_mesh` L208-233（stem 加 seal/guide 环 seal_r=0.0155 contacts collar bore）+ `pump_press` PRISMATIC +Z L331-333（lower=-0.012 upper=+0.015 可半抽出）| eligible if compatible | 可服务/半抽出泵插件：泵 stem 带 seal 导向环卡 collar 内壁，`pump_press` 行程含**正向上抬**（部分拔出可见 stem），仍 spout swivel |
| twist_lock_pump | rec_container_dispenser_var_twist_lock_pump_qwen | `_lock_ring_mesh` L195-248（cam-slot 锁环 + grip tabs + indicator ridges）+ pump stem engagement pins L282-291 + `lock_ring_twist` REVOLUTE +Z L344（0..π/2）+ `pump_press` PRISMATIC | eligible if compatible | twist-lock 泵头：collar 上多一只 `lock_ring`（REVOLUTE +Z 转 ¼ 圈锁/解），pump stem 上 engagement pins 入 cam slots；2 活动件（lock_ring twist + pump press）+ spout swivel = 3 joint |

硬约束记录：pump_head 4 candidate（达 3-6 目标）。含 PRISMATIC（press，所有候选）+ REVOLUTE +Z（spout swivel）+ REVOLUTE +Z（twist_lock 多一只 lock_ring）三类 joint 拓扑 + 不同 part count（twist_lock 多 `lock_ring` part + parent_for_head 改挂 lock_ring）。每个 candidate **≥1 non-fixed 主机构**（pump_press PRISMATIC 必有）。所有候选共享 `spout` REVOLUTE swivel（基线机构）。**未采纳** `long_trigger_foam_head`（trigger 泡沫枪，无 5★ 记录 + `_trigger_mesh` 未定义）。

### Slot C：neck_collar（颈部螺纹 collar / 工业 collar——FIXED visual 挂 bottle）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| standard_ribbed_collar（基线）| rec_container_dispenser_v01 | `_collar_mesh` L183-191（lathe 环 + 28 竖 rib CylinderGeometry）+ `bottle_to_collar` FIXED L275 | eligible if compatible | 普通波纹螺纹 collar：单层 lathe 环 + 28 根竖 rib（旋紧把手感），FIXED 挂 bottle neck，泵 stem 穿 collar bore |
| oversized_industrial_collar | rec_container_dispenser_var_ribbed_collar_qwen | `_oversized_collar_mesh` L184-247（两层 stepped lathe：下层 10 torus 螺纹 ribs + 上层 28 vertical flutes + 40-bump knurl band + top lip）| eligible if compatible | 加大两层工业 collar：宽下裙 + 窄上层，下层 horizontal 螺纹 ribs、上层深竖 flutes + 滚花 knurl 带 + 顶 lip，机械感更强、视觉更宽 |

硬约束记录：neck_collar 2 candidate（**降到下限 2，理由**：源映射 Dispenser 小类只造了这 2 个真实 collar 结构族——普通竖 rib vs 两层工业 stepped collar，均为 FIXED visual。Slot C 不折入 pump_head 是因为 collar 是 `bottle` 的 FIXED child（不同 parent / 不同 mesh helper / 独立 part），与 pump 机构正交；主拓扑多样性由 body_form(5) × pump_head(4) = 20 提供，collar 作为第三轴叠加，不需要凑 3+）。两候选都用同名 `collar` part + `collar_shell` visual + `bottle_to_collar` FIXED，只换 mesh helper。

### Slot D：dip_tube（瓶内吸液管路径 / 可见度——pump 的 FIXED child mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| straight_dip_tube（基线）| rec_container_dispenser_v01 | `_dip_tube_mesh` L246-250（3-point 近直 spline z_top→0.115→0.020，milky tube）+ `pump_to_dip_tube` FIXED L301 | eligible if compatible | 近直吸液管：3-point spline 从泵 stem 底竖直降到瓶底，milky 半透明，透过透明瓶身可见，FIXED 挂 pump |
| s_curved_dip_tube | rec_container_dispenser_var_curved_dip_tube_qwen | `_dip_tube_mesh` L247-258（5-point S 形 spline，左右摆 x±0.024，pale_blue tube material）| eligible if compatible | S 形扫掠吸液管：5-point spline 左右蜿蜒下降（非竖直），pale-blue tube，瓶内蛇形可见，FIXED 挂 pump |

硬约束记录：dip_tube 2 candidate（**降到下限 2，理由**：Dispenser 真实 dip_tube 结构词汇就这 2 族——直管 vs S 形弯管，均为 pump 的 FIXED child mesh（无独立 joint）。Slot D 不折入 pump_head 是因为它是 `dip_tube` 独立 part（`pump_to_dip_tube` FIXED）且 mesh path 是真实可见结构差异（直 vs S 形，透过透明瓶身可见）。主拓扑多样性已由 A×B=20 撑开，D 作正交第四轴）。两候选都用同名 `dip_tube` part + `pump_to_dip_tube` FIXED，只换 spline path + tube 材质。

## 槽位图（slot graph）

pattern: parallel_children（root `bottle`；collar / pump 链挂 bottle；dip_tube 挂 pump；无 multiplicity）

```
bottle(body_form)  [ROOT, 坐地 z=0, 透明 bottle_shell + front_label + liquid_fill]
   │
   ├── collar(neck_collar) --[bottle_to_collar: FIXED @ neck]--> collar   [FIXED visual on neck threads]
   │
   ├── (twist_lock_pump 时) collar --[lock_ring_twist: REVOLUTE +Z @ collar top]--> lock_ring
   │
   ├── pump_head(pump_head) --[pump_press: PRISMATIC +Z @ collar bore]--> pump_head
   │        parent_for_head = collar（基线）或 lock_ring（twist_lock）
   │        │
   │        ├── spout --[spout_swivel: REVOLUTE +Z @ pump side socket]--> spout
   │        │
   │        └── dip_tube(dip_tube) --[pump_to_dip_tube: FIXED @ pump stem bottom]--> dip_tube  [入瓶]
```

接口点位与 joint 语义：
- **collar 接口**：`bottle_to_collar` FIXED，collar 坐 bottle neck threads 处（origin 落 neck rim 区，collar bore 套 neck）。collar 是 bottle 的 FIXED visual child（无独立活动）。
- **pump press 接口**：`pump_press` PRISMATIC，axis +Z，origin 在 collar bore 顶（pump stem 穿过 collar），`parent_for_head` = collar（基线）或 lock_ring（twist_lock）；rest q=0 泵头坐下，负 q 下压 ~PRESS_TRAVEL(0.018)；service_lift 候选 q 含正向上抬（lower=-0.012 upper=+0.015，部分拔出）。
- **spout swivel 接口**：`spout_swivel` REVOLUTE，axis +Z，origin 在 pump 侧出 socket，limits ±π，spout 水平回转（viewer 目检活动语义）。spout 是 pump 的 child，随 pump 一起按压。
- **lock_ring 接口（仅 twist_lock_pump）**：`lock_ring_twist` REVOLUTE，axis +Z，origin 在 collar 顶环中心，limits 0..π/2（¼ 圈锁/解）；pump stem engagement pins 入 lock_ring cam slots（captured-fit）。此时 pump 的 `parent_for_head` 改挂 lock_ring。
- **dip_tube 接口**：`pump_to_dip_tube` FIXED，origin 在 pump stem 底，dip_tube spline 入瓶身腔（穿过 bottle_shell 内壁，allow_overlap）。
- **mating policy**：collar 套 neck、pump stem 穿 collar bore、dip_tube 穿瓶身、spout 插 pump socket、lock_ring 套 collar、pump pins 入 cam slot 均为 captured / 友配过盈（部件壁故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap`（见各 parent run_tests 的 `ctx.allow_overlap`：collar↔bottle、pump↔collar、dip_tube↔bottle、dip_tube↔pump、spout↔pump、lock_ring↔collar、pump↔lock_ring）守 overlap。
- **rest pose**：pump_press q=0 坐下；spout_swivel q=0 朝 +X；lock_ring_twist q=0 解锁位；collar / dip_tube 固定。pump 下压 / spout 回转 / lock_ring 旋锁 / service_lift 抬出为 viewer 目检活动语义。
- **互斥 / 可选**：pump_head 各候选互斥（一次只一种泵）；`lock_ring` part 仅 twist_lock_pump 候选发射；collar / dip_tube 候选互斥（各 slot 一选）。**无 closure/cap slot**（源图无瓶盖；加 cap 违反 parent 资产，见 §Reject + 排除项）。

## 每槽位 Module Emits / Interfaces

### Slot A / bottle（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottle`（visual: `bottle_shell` 透明 shell + `front_label` + `liquid_fill`）| v01 `_round_bottle_mesh` L57-87 / square `_chunky_rect_bottle_mesh` L154-197 / oval `_flask_bottle_mesh` L184-212 |
| internal joints | 无（root 瓶身本身无活动件）| — |
| upstream interface | 坐地 z=0（root）| — |
| downstream interface | neck threads 区（collar FIXED + pump_press parent 接口）| v01 NECK_TOP/COLLAR_Z0 L29-32 |

### Slot C / collar（neck_collar，FIXED 挂 bottle）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `collar`(visual `collar_shell`)| v01 `_collar_mesh` L183-191 / oversized `_oversized_collar_mesh` L184-247 |
| internal joints | `bottle_to_collar` FIXED（无活动）| v01 L275 |
| upstream interface | 套 bottle neck threads | v01 L275 |
| downstream interface | collar bore（pump_press 穿过的接口）| v01 collar bore |

### Slot B / pump_head（每候选发射对应按压泵链）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_head`(`pump_head_shell`) + `spout`(`spout_shell`)[ + twist_lock 多 `lock_ring`(`lock_ring_shell`)] | v01 L285-307 / twist L341-345 |
| internal joints | `pump_press` PRISMATIC +Z（所有候选）+ `spout_swivel` REVOLUTE +Z（所有候选）[ + `lock_ring_twist` REVOLUTE +Z（twist_lock）] | v01 L296/L307 / twist L344 |
| upstream interface | pump stem 穿 collar bore（parent=collar 或 lock_ring）| v01 L296 |
| downstream interface | pump stem 底（dip_tube FIXED）+ pump 侧 socket（spout）| v01 L301/L307 |

### Slot D / dip_tube（pump 的 FIXED child mesh）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dip_tube`(visual `dip_tube`)| v01 `_dip_tube_mesh` L246-250 / s_curved L247-258 |
| internal joints | `pump_to_dip_tube` FIXED（无活动）| v01 L301 |
| upstream interface | 挂 pump stem 底 | v01 L301 |
| downstream interface | spline 入瓶身腔（透过 bottle_shell 可见）| v01 L246-250 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | round_clear_bottle / square_rounded_body / oval_flask_body / narrow_oval_footprint / square_prism_footprint | round_clear_bottle | choice | deterministic procedural sampler 选 | module table |
| pump_head | enum | press_swivel_pump / long_spout_lotion_pump / service_lift_pump / twist_lock_pump | press_swivel_pump | choice | sampler 选 | module table |
| neck_collar | enum | standard_ribbed_collar / oversized_industrial_collar | standard_ribbed_collar | choice | sampler 选 | module table |
| dip_tube | enum | straight_dip_tube / s_curved_dip_tube | straight_dip_tube | choice | sampler 选 | module table |
| palette_style | enum | clear_soap / amber_lotion / frosted_white / blue_teal / ceramic_cream / matte_black / soft_touch_sage / pearlescent_blush / chrome_pump_clear / sanitizer_aqua_gel | clear_soap | palette | palette only，**不计入 slot_choice**；per-seed `rng.choice`；每 colorway 自带 finish 维度 | palette（见下，10 配色）|
| body_height_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放 BODY_H → SHOULDER_TOP / NECK_TOP / COLLAR_Z / PUMP_Z 链上移，clamp | resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 BODY_R / 半宽（不动 NECK_R，保 collar 配合），clamp | resolve clamp |
| collar_radius_scale | float | [0.92, 1.12] | 1.0 | independent | 缩放 collar 外径（oversized 更宽），clamp；不动 collar bore（pump 穿） | resolve clamp |
| pump_travel_scale | float | [0.85, 1.12] | 1.0 | independent | 缩放 `pump_press` 行程（PRESS_TRAVEL）+ service_lift 上抬量，clamp | resolve clamp |
| spout_reach_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 spout 水平伸出（long_spout 上限收紧防过长），clamp | resolve clamp |
| neck_z = f(body_height_scale) | float | derived | — | equation | `NECK_TOP/COLLAR_Z0/COLLAR_Z1/PUMP_Z0/PUMP_Z1 = base·body_height_scale`，整链同比上移（不独立采样）| resolve |
| (—) | constraint | — | — | inequality | collar bore / pump stem 配合：`collar_bore_R ≥ pump_stem_R + clearance` 且 collar 套 NECK_R 不破；违反按比例回缩 collar_radius / body_radius scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | dip_tube 触底：`dip_tube z_min < 0.030`（始终插入瓶身近底），body_height_scale 缩放时同比派生 z_top 保持触底；违反回缩 | 接口 / 类别身份 |

palette_style 颜色定义（target 8-10，取 **10**；锚定 5★ 源 material + 真实 soap/lotion/sanitizer dispenser 常见配色；rgba 以源材质为基准微调）。每 colorway = bottle_shell + pump_head + collar/accent + dip_tube + **finish**（显式材质表面维度）。`finish` 维度取值：`clear_gloss` / `frosted_translucent` / `opaque_matte` / `ceramic_glaze` / `soft_touch_matte` / `amber_translucent` / `metallic_chrome_pump` / `pearlescent`：

| palette_style | bottle_shell | liquid_fill | pump_head | collar / accent | dip_tube | finish | 来源 / 说明 |
|---|---|---|---|---|---|---|---|
| clear_soap（基线）| clear_plastic (0.78,0.88,0.92,0.34) | pale_soap (0.78,0.90,0.84,0.62) | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey (0.70,0.72,0.72,1.0) | milky_tube (0.88,0.92,0.92,0.78) | clear_gloss | v01 原配色（透明皂液瓶）L256-262 |
| amber_lotion | amber 半透明 (0.80,0.62,0.34,0.40) | honey lotion (0.86,0.66,0.40,0.70) | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey | milky_tube | amber_translucent | 琥珀色润肤泵瓶（源 clear_plastic→amber 同 alpha 区）|
| frosted_white | frosted (0.92,0.93,0.94,0.55) | pale_soap (0.78,0.90,0.84,0.62) | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey | milky_tube | frosted_translucent | 磨砂白分装瓶（半透明乳白）|
| blue_teal | blue clear (0.55,0.72,0.90,0.40) | teal liquid (0.45,0.78,0.80,0.66) | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey | pale_blue_tube (0.55,0.72,0.90,0.85) | clear_gloss | s_curved 源用 pale_blue_tube L275；蓝/teal 消毒液瓶 |
| ceramic_cream | opaque cream (0.95,0.92,0.85,1.0) | （不可见，opaque） | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey | milky_tube | ceramic_glaze | 陶瓷奶油色不透明皂液瓶（釉面光泽，label 仍贴）|
| matte_black | matte black (0.18,0.18,0.20,1.0) | （不可见） | dark grey pump (0.30,0.30,0.32,1.0) | dark grey pump / soft_grey | dark tube (0.22,0.22,0.24,1.0) | opaque_matte | 哑黑高端泵瓶（不透明哑光）|
| soft_touch_sage | opaque sage (0.66,0.72,0.62,1.0) | （不可见，opaque） | soft sage pump (0.60,0.66,0.56,1.0) | warm_white / soft_grey | milky_tube | soft_touch_matte | 软触哑光鼠尾草绿润肤泵瓶（橡胶软触表面，不透明）|
| pearlescent_blush | pearl blush 半透明 (0.95,0.84,0.86,0.58) | rose lotion (0.92,0.74,0.76,0.70) | pearl warm_white (0.96,0.94,0.93,1.0) | pearl warm_white / soft_grey | milky_tube | pearlescent | 珠光腮红粉润肤泵瓶（珠光半透明，label 仍贴）|
| chrome_pump_clear | clear_plastic (0.78,0.88,0.92,0.34) | pale_soap (0.78,0.90,0.84,0.62) | chrome pump (0.82,0.84,0.86,1.0) | chrome accent (0.82,0.84,0.86,1.0) / soft_grey | milky_tube | metallic_chrome_pump | 透明瓶身 + 抛光铬金属泵头/collar（金属泵，瓶身仍透明）|
| sanitizer_aqua_gel | aqua clear (0.62,0.86,0.88,0.36) | aqua gel (0.55,0.84,0.86,0.60) | warm_white (0.94,0.93,0.90,1.0) | warm_white / soft_grey | pale_blue_tube (0.55,0.72,0.90,0.85) | clear_gloss | 透明青绿凝胶消毒液泵瓶（clear gel sanitizer）|

> palette_style 仅改材质 rgba + finish 表面语义，**不改任何 mesh / joint / part tree**。`finish` 是 palette 内的显式材质表面维度（gloss / frosted / matte / glaze / soft-touch / amber / metallic / pearlescent），不引入新 part / slot，仅决定材质表观 + 透明/不透明分支。
> 透明 / 半透明类（clear_soap=clear_gloss / amber_lotion=amber_translucent / frosted_white=frosted_translucent / blue_teal=clear_gloss / pearlescent_blush=pearlescent / chrome_pump_clear=metallic_chrome_pump 的透明瓶身 / sanitizer_aqua_gel=clear_gloss）保 `bottle_shell.rgba[3] < 0.5`（满足基线测试 "transparent bottle material"），liquid_fill 可见。
> 不透明类（ceramic_cream=ceramic_glaze / matte_black=opaque_matte / soft_touch_sage=soft_touch_matte）需在 resolve 标记 `opaque_body=True`，模板对应**放宽/跳过透明断言并跳过 liquid_fill 可见性**（不透明瓶看不到液体，避免穿模目检误判）。
> `metallic_chrome_pump`（chrome_pump_clear）仅泵头 / collar accent 为金属铬（rgba ~0.82-0.86，高反光语义），瓶身仍透明 → 走透明分支；金属表观由 finish 标记，不改 alpha<0.5 的瓶身断言。

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_z` 为 equation（collar / pump / spout 挂高随 body 高同比上移，保按压链 origin 配合）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / pump_head / neck_collar / dip_tube 的拓扑。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + pump_head + neck_collar + dip_tube）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单瓶单泵单 spout 单 dip_tube。源映射 `count_param: 无`、`N_range: 无`、`copied object: 无` 一致确认本小类无 multiplicity 轴。

## 拓扑多样性审计

总组合数：body_form(5) × pump_head(4) × neck_collar(2) × dip_tube(2) = **80**。

仅 body_form × pump_head = **20 ≥ 10** 已可过门控；叠 neck_collar × dip_tube ×4 后充裕（80）。

理由：本类拓扑多样性来源充裕——body_form(5) × pump_head(4) 的笛卡尔积即 20 distinct，远超 10。pump_head 引入不同 joint 拓扑 + part count：press_swivel（PRISMATIC press + REVOLUTE swivel）/ long_spout（同机构 + 长弯 spout mesh）/ service_lift（PRISMATIC 含正向上抬 + seal 环）/ twist_lock（多一只 `lock_ring` part + `lock_ring_twist` REVOLUTE +Z = 3 joint），是真实结构差异（part count 与 joint 数随泵候选变）。body_form 在圆 / 圆角方 / 扁椭圆 / 方棱柱间换 mesh 发射方式（revolve vs loft）。neck_collar 在单层 rib vs 两层工业 collar 间换 `collar_shell`。dip_tube 在直 vs S 形 spline 间换 path。四轴编入 slot_choices。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 四个 named slot（笛卡尔积近全合法，少量 gating 见下），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除/适配非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 80（80 组合的采样空间足够；受真实词汇表约束的轴是 neck_collar(2)/dip_tube(2)，但 body_form(5) × pump_head(4) 已撑开 20）。低于 300 的原因：本小类真实结构词汇就是 5 body × 4 pump × 2 collar × 2 tube = 80，是该类目（小台面按压分装瓶，无 multiplicity、无 cap slot）的合理上限，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 6 个 scale（body_height / body_radius / collar_radius / pump_travel / spout_reach + neck_z equation）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_z` 为 equation（collar / pump / spout 挂高随 body 高同比上移）。collar bore / pump stem 配合不等式 + dip_tube 触底不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 pump_press / spout_swivel / lock_ring_twist joint origin（collar bore / pump socket / collar top）、collar 套 neck 配合、dip_tube 触底或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 四 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含四轴且与 build 一致 |
| compatibility matrix | (1) `twist_lock_pump` 需要 collar 顶能承 lock_ring → 与任意 collar 兼容（lock_ring 套 collar 顶外径，oversized collar 更宽时 lock_ring 半径在 resolve 按 collar 顶径派生，不 gate 掉）。(2) `service_lift_pump` seal 环径需 ≤ collar bore + 过盈带 → 与任意 collar / body 兼容（seal_r 在 resolve 按 collar bore 派生）。(3) 不透明 palette（ceramic_cream / matte_black / soft_touch_sage）跳过透明断言 + 跳过 liquid_fill 可见性（避免不透明瓶内液体穿模目检误判）；其余 7 透明/半透明 palette（含 chrome_pump_clear 的透明瓶身 + 金属泵头）走透明分支。(4) 各 pump_head 互斥；collar / dip_tube 各 slot 一选。(5) **无 cap/closure 组合**（不发射瓶盖）。无硬 gate-out（80 组合全合法，仅 resolve 派生尺寸适配 + palette 透明度分支）| 无 floating / collision / pump 穿瓶 / dip_tube 离瓶 / joint 轴或 origin 错位 / 不透明瓶误判穿模 |
| controlled local variation | 6 个 clamped scale，每 build 统一；neck_z equation 驱动 collar/pump/spout 挂高 | 比例变化不破坏 pump/spout/lock joint origin / collar 套 neck 配合 / dip_tube 触底 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | pump 下压 / spout 回转 / lock 旋 / dip_tube 触底 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 5 | yes | yes | round / 圆角方 / 扁椭圆 flask / narrow oval / 方棱柱 |
| pump_head | 4 | yes | yes | press_swivel(PRIS+REV) / long_spout(同+长 spout) / service_lift(PRIS 含上抬+seal) / twist_lock(多 lock_ring REV +Z = 3 joint) |
| neck_collar | 2 | yes | no | 单层 rib collar + 两层工业 stepped collar（源仅 2 真实族，已记降级理由）|
| dip_tube | 2 | yes | no | 直管 + S 形弯管（源仅 2 真实族，已记降级理由）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, pump_head, neck_collar, dip_tube) 四轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；neck_z equation 驱动 collar/pump/spout 挂高；collar bore↔pump stem 配合不等式 + dip_tube 触底不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：80 组合全合法（无硬 gate-out）；lock_ring 半径 / service_lift seal_r 按 collar 在 resolve 派生；不透明 palette 跳过透明 + liquid 可见性断言
- 连续 scale clamp 后不破坏 pump/spout/lock joint origin / collar 套 neck 配合 / dip_tube 触底 / 坐地 / 类别身份
- 关键 joint：`pump_press` PRISMATIC +Z (abs(axis[2])>0.99) 所有候选；`spout_swivel` REVOLUTE +Z 所有候选；twist_lock `lock_ring_twist` REVOLUTE +Z (0..π/2)；`bottle_to_collar` / `pump_to_dip_tube` FIXED
- captured-fit：element-scoped `allow_overlap`（collar↔bottle、pump↔collar、dip_tube↔bottle、dip_tube↔pump、spout↔pump、lock_ring↔collar、pump↔lock_ring），复刻各 5★ run_tests 的 allow_overlap
- grandfather：所有 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- 透明瓶身：透明/半透明 palette（7 个，含 chrome_pump_clear 的透明瓶身 + 金属泵头）满足 `bottle_shell.rgba[3] < 0.5`；不透明 palette（3 个：ceramic_cream / matte_black / soft_touch_sage）显式标记并放宽该断言。finish 维度（clear_gloss / frosted_translucent / opaque_matte / ceramic_glaze / soft_touch_matte / amber_translucent / metallic_chrome_pump / pearlescent）只决定材质表观 + 透明分支，不引入 part / slot
- **无 cap/closure part**：模板不发射瓶盖 / dust cover（参考资产是 uncapped 泵瓶）

## Reject cases

- 给瓶身补瓶盖 / dust cap / clear over-cap → 违反参考资产（uncapped 泵瓶）；源映射明确排除 closure slot。
- pump_press / spout_swivel / lock_ring_twist joint origin 放在瓶底 / 任意点而非 collar bore / pump socket / collar top 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 把 dispenser 做成独立泵机构（无瓶身 + 无 dip_tube + 无 label）→ 出 `container_pump` 语义；dispenser 必须带完整瓶身链。
- 给瓶子加量杯盖 / 提手 / 倒料颈 → 出 `container_laundry_detergent_bottle` 语义；dispenser 是小台面按压瓶。
- pump_head rest pose 设成下压 / spout rest 设成已转 90° 而非 q=0 坐下/朝 +X → current-pose 与 viewer 目检不符。
- 圆 body 用纯 Box 占位 / 方 body 用 revolve → 失 footprint 身份；圆 body 必须 revolve（LatheGeometry），方 / 椭圆 body 用 `_loft_sections`。
- dip_tube 不触瓶底 / 离开瓶身（z_min ≥ 0.030 或浮在瓶外）→ "dip tube descends below label" FAIL；body 缩放时未派生 z_top 保触底。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 采纳 `long_trigger_foam_head` / `detached_dip_tube_pump`（无 5★ 记录 + `_trigger_mesh` 未定义）作为 candidate → 违反 hard rule（candidate 必须有真实 5★ 来源）。
- 不透明 palette（ceramic_cream / matte_black / soft_touch_sage）仍跑透明断言或仍渲染瓶内 liquid → 误判穿模 / 透明 FAIL；需 resolve 标记 opaque 并放宽。

## 与相邻类别的边界

- 不该混入：**container_pump（独立泵头机构）**——理由：dispenser 必带完整瓶身 + dip_tube + front_label，按压泵 + swivel spout 装在瓶口；container_pump 是泵机构本体/替换件，无瓶身。
- 不该混入：**container_laundry_detergent_bottle（洗衣液瓶）**——理由：洗衣液瓶常带提手 + 量杯盖 / flip cap + 倒料颈、宽肩大容量；dispenser 是小台面分装瓶，核心是按压泵 + 水平 swivel spout，无量杯/提手/倒料盖。
- 不该混入：**细颈瓶 / 滴管瓶 / 喷雾瓶 / 带盖罐**——理由：dispenser 身份是外露按压泵 + swivel spout + dip_tube + 无瓶盖闭合件，不是 screw-cap bottle、dropper、trigger spray 或 lidded jar。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | palette-only revision：palette_style 由 6 → **10 coordinated colorway**（clear_soap / amber_lotion / frosted_white / blue_teal / ceramic_cream / matte_black / soft_touch_sage / pearlescent_blush / chrome_pump_clear / sanitizer_aqua_gel），每 colorway 含 bottle_shell + pump_head + collar/accent + dip_tube + 显式 **finish** 维度（clear_gloss / frosted_translucent / opaque_matte / ceramic_glaze / soft_touch_matte / amber_translucent / metallic_chrome_pump / pearlescent）。SPEC_ONLY：未动 slot / candidate / multiplicity / joint / dimension / topology；rgba 锚定 5★ 源材质（clear_plastic / pale_soap / warm_white / soft_grey / milky_tube / pale_blue_tube）+ 真实推断配色。透明/半透明 7 个保 alpha<0.5，不透明 3 个（ceramic_cream / matte_black / soft_touch_sage）标记 opaque_body。|

## 模板实现备注（可选）

- 共享 helper：`_round_bottle_mesh`(revolve) + `_loft_sections`/`_rounded_rect_points`(方 / 椭圆 body) + `_flask_ellipse` + `_collar_mesh`/`_oversized_collar_mesh` + `_pump_head_mesh`(分支按 pump_head) + `_spout_mesh` + `_dip_tube_mesh` + `_lock_ring_mesh` + `_ring_mesh` 全 module 公用（直接改编 8 个 fork 的同名 helper）。
- pump 链：`pump_head` 经 `pump_press` PRISMATIC +Z 挂 `parent_for_head`（collar 基线 / lock_ring twist_lock）；`spout` REVOLUTE +Z 挂 pump；`dip_tube` FIXED 挂 pump stem 底。twist_lock 多一只 `lock_ring`（REVOLUTE +Z 0..π/2 挂 collar）+ pump stem engagement pins。
- captured-fit overlap：`run_container_dispenser_tests` 复刻 8 个 fork 的 `ctx.allow_overlap`（collar↔bottle、pump↔collar、dip_tube↔bottle、dip_tube↔pump、spout↔pump，twist_lock 加 lock_ring↔collar / pump↔lock_ring，loft body 加 pump↔bottle stem 穿肩）。
- neck_z equation：`resolve_config` 派生 `COLLAR_Z0/Z1/PUMP_Z0/Z1/NECK_TOP = base·body_height_scale`，collar bore↔pump stem 配合不等式 + dip_tube 触底不等式在 resolve 投影。
- palette_style：10 colorway（带显式 finish 维度：clear_gloss / frosted_translucent / opaque_matte / ceramic_glaze / soft_touch_matte / amber_translucent / metallic_chrome_pump / pearlescent）仅改材质 rgba + finish 表观；透明/半透明类保 alpha<0.5，不透明类（ceramic_cream/matte_black/soft_touch_sage）resolve 标记 `opaque_body=True`，模板放宽透明断言 + 跳过/隐藏 liquid_fill。chrome_pump_clear 金属泵头但瓶身仍透明。
- **不发射任何 cap/closure part**（参考资产是 uncapped 泵瓶）。
- 参考模板：`agent/templates/Container_Jar.py`（Config/ResolvedConfig dataclass + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` 报 topology family + `build_<stem>` + `run_<stem>_tests` 的 allow_overlap + element-scoped grandfather 骨架；jar 与 dispenser 同为 parallel_children + 透明 body + 顶部机构 + captured-fit overlap，运动拓扑最近）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | round_clear_bottle + press_swivel_pump + standard_ribbed_collar + straight_dip_tube | rec_container_dispenser_v01 | `_round_bottle_mesh` L57-87 / `_pump_head_mesh` L207-230 / `pump_press` L296 / `spout_swivel` L307 / `_collar_mesh` L183-191 / `_dip_tube_mesh` L246-250 / `bottle_to_collar` L275 / `pump_to_dip_tube` L301 | 全链基线：圆瓶 body + 按压泵 + swivel spout + 普通 collar + 直 dip_tube |
| S2 | A | square_rounded_body | rec_container_dispenser_var_square_body_qwen | `_chunky_rect_bottle_mesh` L154-197 / box `liquid_fill` L321-328 | 圆角方块瓶身 loft |
| S3 | A | oval_flask_body | rec_container_dispenser_var_oval_body_qwen | `_flask_bottle_mesh` L184-212 / `_elliptical_liquid_mesh` L383-405 | 高扁椭圆 flask 瓶身 + 椭圆 liquid |
| S4 | A | narrow_oval_footprint + square_prism_footprint | rec_container_dispenser_v01 | `_oval_bottle_mesh` L137-150 / `_square_bottle_mesh` L130-134 | parent 内置前后扁椭圆 + 方棱柱 footprint 变体 |
| S5 | B | long_spout_lotion_pump | rec_container_dispenser_var_tall_plunger_long_spout_qwen | `_pump_head_mesh` L207-262 / `_spout_mesh` L295-318 | 高 plunger 泵 + 椭圆按压盘 + 长弯水平 spout |
| S6 | B | service_lift_pump | rec_container_dispenser_var_detached_pump_insert_qwen | `_pump_head_mesh` L208-233（seal 环）/ `pump_press` L331-333（含上抬）| 可半抽出服务泵插件 + seal 导向环 |
| S7 | B | twist_lock_pump | rec_container_dispenser_var_twist_lock_pump_qwen | `_lock_ring_mesh` L195-248 / pump pins L282-291 / `lock_ring_twist` REVOLUTE +Z L344 | twist-lock 锁环（¼ 圈）+ pump engagement pins，3 joint |
| S8 | C | oversized_industrial_collar | rec_container_dispenser_var_ribbed_collar_qwen | `_oversized_collar_mesh` L184-247 | 两层工业 stepped collar（螺纹 ribs + flutes + knurl + lip）|
| S9 | D | s_curved_dip_tube | rec_container_dispenser_var_curved_dip_tube_qwen | `_dip_tube_mesh` L247-258（5-point S spline）+ pale_blue_tube L275 | S 形蛇行吸液管 |
