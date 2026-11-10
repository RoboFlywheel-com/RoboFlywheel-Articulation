# fire_extinguisher (portable cylindrical fire extinguisher) — Modular Spec

> 来源小类：`picture/Urban Environment/Fire Extinguisher`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Urban_Environment__Fire_Extinguisher.md`。
> **"fire extinguisher" 在此 = 直立便携式钢瓶灭火器（portable stored-pressure / CO2 cylinder）**，不是 Fire Hydrant（消防栓，固定地桩 + 横向喷口 + 顶帽螺母）、不是 fire bucket（bucket1 消防沙桶，开口敞桶无阀头）。
> 结构家族 = 钢瓶 body（root，base ring + cylinder + banding + dome shoulder + brass valve neck + valve head）+ 顶部 operating head 主机构（squeeze lever / hand-wheel / push trigger）+ 侧挂 discharge（hose+nozzle / co2 horn / hoseless nozzle）+ gauge/valve neck（固定）+ 可选 mounting（none / wall bracket / floor stand）。共享运动学：**operating head 的致动件是唯一非 fixed 主关节（defining joint）**，squeeze lever 绕后 cross-pin 横 Y REVOLUTE（基线身份）。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 个 parent + 8 个 fork 槽位变体）位于 articraft_data 上游仓库 `data/records/<id>/revisions/rev_000001/model.py`，均 converged。行号按各样本上游 `model.py` 实际行号计；引用以 part / element `name=` / joint 名为准（`body`/`operating_lever`/`hand_wheel`/`trigger`/`floor_stand`、`bottle`/`shoulder_dome`/`valve_neck`/`valve_head`/`label_band`/`gauge_dial`/`carry_handle`/`lever_pin`/`discharge_hose`/`discharge_nozzle`/`discharge_horn`/`bracket_back_plate`/`cradle_strap`/`base_plate`/`retainer_ring`、`body_to_lever`/`body_to_wheel`/`body_to_trigger`/`stand_to_body` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `fire_extinguisher` |
| template path | `agent/templates/Urban_Environment_Fire_Extinguisher.py` |
| test path (optional) | `tests/agent/test_fire_extinguisher_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `body`；operating-head 致动件 / discharge / mounting 等挂到 body；唯一可重复元素为 lug 对 + wheel spokes + trigger grip-ribs，**非小类级 multiplicity 轴**，见 §8）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 槽位变体；均 converged，compile success、含 REVOLUTE/PRISMATIC 非 fixed 主关节、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build 段、part 树、articulation、run_tests 的 allow_overlap/expect_*/check 段）|
| read_scope | all 5-star samples in this category（parent + 8 variants 即全部 retained 5 星样本）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **9 个样本共享同一身份骨架**：1 个 root `body` part（base ring + bottle cylinder + 双 banding ring + shoulder dome + brass valve neck + valve head + label band + 固定 gauge 三件 stem/case/dial + safety pin + pull ring + 固定 carry handle）+ 1 个顶部主机构致动 part（lever / wheel / trigger）。`gauge_dial` / `valve_neck` / `valve_head` / `carry_handle` / `label_band` 恒为 body visual，恒存在 —— 这是类别身份（run_tests 普遍含 `gauge_on_front`、`label_mid_body`、`base_at_ground`、`upright_bottle` 检查）。
- **operating head 是唯一变 joint 拓扑的 slot**（强多样性来源）：
  - **squeeze_lever**（parent / co2_tall_thin / squat_wide / co2_horn / hoseless_nozzle / wall_bracket / floor_stand 全部用）：`operating_lever` part，REVOLUTE 绕后 cross-pin（`pin_x≈-0.012`，`pin_z` 近 lug 顶），**横 Y 轴**，`lower=0,upper=0.5`，squeeze 把前缘下压；body 侧有 `lever_lug_left/right`（for-loop 对）+ `lever_pin` + 后挂 carry handle。
  - **wheel_valve**：`hand_wheel` part，REVOLUTE 绕**竖直 Z 轴**，多圈 `upper=4π`（screw-down），spoked 轮（hub + torus rim + `for i in range(n_spokes)` 5 根 spoke）坐于 `valve_stem` 顶；无 lug/pin，safety pin 改穿 valve head。
  - **top_pull_trigger**：`trigger` part，**PRISMATIC 沿 -Z**（`axis=(0,0,-1)`，`upper=0.012`），按钮 cap + stem 滑入 `trigger_guide` boss bore；grip-ribs `for i in range(6)`；safety pin 穿 guide boss。
- **body_shape**（改 root 几何比例 + banding/label 高度，**非纯 scale**：L/D 比 + 结构特征带不同 run_tests check）：standard（parent，`body_r=0.056`，`shoulder_z=0.330`）/ co2_tall_thin（`body_r=0.040`，`shoulder_z=0.520`，`tall_slender_body` 检查 h>w·4）/ squat_wide（`body_r=0.100`，`shoulder_z=0.175`，`squat_wide_body`+`wide_diameter`+宽 base ring 检查）。
- **discharge**（侧挂出料件形态 + 是否为独立 swept tube）：hose+nozzle（parent，细黑软管 spline + 小 lathe nozzle）/ co2_horn（rigid swept `discharge_tube` r=0.009 + 宽锥 lathe `discharge_horn` horn_large_r=0.062）/ hoseless_nozzle（无 hose，短 lathe `discharge_nozzle` 直出 valve head 前 -Y）。
- **mounting**（承托/安装结构，改 root 拓扑）：none（parent，仅 base ring 立地）/ wall_bracket（inline 到 body 的 `bracket_back_plate` Box + 300° `cradle_strap` swept strap，红钣金壁挂）/ floor_stand（**独立 `floor_stand` part 作 ROOT**：`base_plate` Box + 2 根 `post_i` + 全环 `retainer_ring` torus + 2 gusset；body 经 `stand_to_body` FIXED 坐于 plate 顶 z=plate_thickness）。
- **palette**：全样本统一 red bottle / brass valve / steel pin / black rubber / white label / green gauge_face；floor_stand 另有 `stand_paint` 黑漆。→ 抽象出 4-6 套 colorway（见 §7 palette_style：classic_red / co2_black / chrome_steel / yellow_industrial / brass_vintage）。

## 核心身份

一只直立**便携式钢瓶灭火器**：一个 root `body`（钢瓶轴 +Z，base ring 立于 z=0），自下而上为 recessed base ring → 红色钢瓶 cylinder（带两道 rolled banding ring + 中段 white `label_band`）→ 红色 dome shoulder → 黄铜 `valve_neck` → `valve_head` 阀块；阀块顶部承载**一个 operating head 主机构致动件**（侧 squeeze `operating_lever` REVOLUTE 横 Y / 顶 spoked `hand_wheel` REVOLUTE 立 Z / 顶 push `trigger` PRISMATIC 立 Z）；阀块前方 (-Y) 恒有圆形 `gauge_dial` 压力表（stem+case+dial 三件）；阀块旁有 safety pin + `pull_ring` + 固定后挂 `carry_handle`；body 侧面挂一组 discharge（软管+nozzle / CO2 horn / hoseless nozzle）。活动语义恒为：**operating-head 致动件是唯一主关节（defining joint）**；身份基线为 squeeze lever 绕后 cross-pin 横 Y REVOLUTE 下压。默认成熟域：body_shape × operating_head × discharge × mounting 笛卡尔积的单瓶手提灭火器。

不该混入：
- **Fire Hydrant（消防栓）**——固定地桩 + 顶帽六角螺母 + 侧向 2-3 个出水口法兰 + 链帽，**无可提瓶身、无 pressure gauge、无 squeeze lever / pull ring 身份**；若 root 为埋地短粗桩 + 横向喷口而非可提钢瓶即出类。
- **fire bucket（bucket1 消防沙桶）**——敞口锥/圆桶 + 提梁，**无 valve head / gauge / discharge / lever 机构**；若为开口空桶即出类。
- **gas cylinder / propane tank（纯储气瓶）**——虽同为直立钢瓶，但**缺 squeeze lever + gauge + discharge hose 这套灭火器致动身份**；若仅瓶 + 顶阀手轮而无 carry handle + gauge + discharge 即降为储气瓶，拒绝（注：wheel_valve 变体仍保留 carry handle + gauge + discharge，故仍读作灭火器）。

## 槽位 + 候选模块表

> **建模注记**：fire_extinguisher 是 **root `body`（dispatch body_shape 几何 + 固定 gauge/valve/carry/label）+ parallel children**：operating-head 致动件（lever/wheel/trigger，唯一主关节）+ inline 的 discharge visuals + inline/独立的 mounting。四个 slot 中 **Slot A（body_shape）改 root 钢瓶 lathe profile 比例 + banding/label 高度 + base ring 宽度 + 一组 body 形态 check**；**Slot B（operating_head）改主关节 part / type / axis / range + body 侧承载（lug+pin / valve_stem / trigger_guide）+ safety pin 穿点**；**Slot C（discharge）改侧挂出料 visual 形态**；**Slot D（mounting）改 root 拓扑（none=单 body root / wall_bracket=body inline 钣金 / floor_stand=独立 floor_stand root + body FIXED）**。Slot B 与 Slot D 的兼容矩阵见 §9（floor_stand 改 root parent，与所有 head 兼容但需 head 锚点统一在 body-local frame）。

### Slot A：body_shape（root 钢瓶形态 / 比例 —— 结构形态差异，非纯 scale）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| standard_cylinder（基线） | rec_red-portable-fire-extinguisher-a-cylindrical-ste_20260608_170539_994452_8766eb99（parent）| base_ring L62-78 / bottle(+banding) L80-95 / dome L97-114 / neck L116-132 / label L134-148 | eligible if compatible | `body_r=0.056`，`shoulder_z=0.330`，`dome_top_z=0.400`，`neck_top_z=0.440`；banding `bz∈(0.060,0.300)`，label `0.110-0.278`；run_tests `upright_bottle` h>w·1.6 |
| co2_tall_thin | rec_fire_extinguisher_var_co2_tall_thin | dims L50-54 / bottle L80-95 / dome L97-114 / label L134-148 / `tall_slender_body`+`thin_cylinder_diameter` test L349-365 | eligible if compatible | 高瘦高压 CO2 型：`body_r=0.040`，`shoulder_z=0.520`，`neck_top_z=0.620`；banding `(0.080,0.470)`，label `0.150-0.410`；test 要求 cyl_h>cyl_w·4 且 cyl_w<0.110 |
| squat_wide | rec_fire_extinguisher_var_squat_wide | dims L51-55 / 宽 base_ring L63-79 / bottle L81-95 / dome L97-114 / label L134-150 / `squat_wide_body`+`wide_diameter`+`short_cylinder` test L344-393 | eligible if compatible | 矮胖宽瓶：`body_r=0.100`，`shoulder_z=0.175`，`dome_top_z=0.248`；宽 base ring（body_r-0.012），label `0.068-0.160` 宽环；test 要求 w>0.16 且 h<w·1.8 |

### Slot B：operating_head（主机构槽 —— 阀门致动；唯一非 fixed defining joint；joint 拓扑多样）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| squeeze_lever（基线，REVOLUTE 横 Y） | parent（同上 id）| body 侧 lug+pin L191-211 / carry handle L173-189 / `operating_lever` part L301-323 / `body_to_lever` REVOLUTE L324-333 / squeeze test L371-404 | eligible if compatible | `operating_lever` part；body 侧 `lever_lug_{left,right}`（`for s,tag` 对）+ `lever_pin`（steel cross-pin）；REVOLUTE `axis=(0,1,0)` `lower=0,upper=0.5`；joint origin `(pin_x≈-0.012,0,pin_z)`；前缘 squeeze 下压；`allow_overlap(operating_lever,lever_pin)` captured-hinge；safety pin 穿 lug |
| wheel_valve（REVOLUTE 立 Z，多圈） | rec_fire_extinguisher_var_wheel_valve | `valve_stem` L172-180 / `hand_wheel` part(hub+rim+spokes) L290-351 / `body_to_wheel` REVOLUTE L353-363 / wheel test L417-470 | eligible if compatible | `hand_wheel` part = `hub` Cylinder + `rim` torus + `for i in range(n_spokes=5)` `spoke_{i}`；坐于 brass `valve_stem` 顶；REVOLUTE `axis=(0,0,1)` `upper=4π`（screw-down 多圈）；joint origin `(0,0,joint_z)` 立轴；test `wheel_is_round`(dx>dz·2)+`wheel_multi_turn_range`+`expect_within(rim,bottle,xy)`；无 lug/pin，safety pin 穿 valve head；**无 carry-lever，仍含 carry_handle + gauge + discharge** |
| top_pull_trigger（PRISMATIC 立 Z） | rec_fire_extinguisher_var_top_pull_trigger | `trigger_guide` boss L173-192 / `trigger` part(cap+stem+ribs) L301-358 / `body_to_trigger` PRISMATIC L360-370 / trigger test L408-464 | eligible if compatible | `trigger` part = domed `trigger_cap` lathe + `trigger_stem` Cylinder + `for i in range(6)` `grip_rib_{i}`；body 侧 `trigger_guide` brass boss（bore）；PRISMATIC `axis=(0,0,-1)` `lower=0,upper=0.012` push-down；joint origin guide boss 顶；`allow_overlap(trigger_stem,trigger_guide)` captured-shaft + `expect_within(trigger_stem,trigger_guide,xy)`；safety pin 穿 guide boss |

### Slot C：discharge（侧挂出料件 —— body inline visuals）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| hose_nozzle（基线） | parent（同上 id）| `discharge_hose` spline tube L271-286 / `discharge_nozzle` lathe L287-296 | eligible if compatible | 细黑 `discharge_hose`（`tube_from_spline_points` 5 控制点 r=0.006 从 valve head 弯下贴瓶）+ 小 lathe `discharge_nozzle`（rpy=(0,π,0) 末端朝外）|
| co2_horn | rec_fire_extinguisher_var_co2_horn | `discharge_tube` rigid swept L274-288 / `discharge_horn` 宽锥 lathe L289-318 | eligible if compatible | rigid `discharge_tube`（r=0.009 swept tube）+ 宽锥 `discharge_horn`（lathe `horn_small_r=0.018`→`horn_large_r=0.062`，`horn_len=0.180`，rpy=(0,π,0) 大口朝下外）—— CO2 单元身份 |
| hoseless_nozzle | rec_fire_extinguisher_var_hoseless_nozzle | `discharge_nozzle` 固定短喇叭 L271-293 | eligible if compatible | 无 hose；单件短 flared `discharge_nozzle`（8 点 lathe，mounting flange→throat→flare bell，`origin=(0,-0.022,nozzle_z)` rpy=(π/2,0,0) 直出 valve head 前 -Y）—— 紧凑车/厨用型 |

### Slot D：mounting（承托 / 安装 —— root 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | parent（同上 id）| body root（无额外 mounting part）；base ring L62-78 立地 | eligible if compatible | 仅 base ring 立 z=0，body 即 root，无安装件；`base_at_ground` abs(min z)<0.004 |
| wall_bracket | rec_fire_extinguisher_var_wall_bracket | `bracket_back_plate` Box L310-315 / `cradle_strap` 300° swept L317-340 | eligible if compatible | inline 到 body：红钣金 `bracket_back_plate`（`Box`，背靠瓶 -X 面）+ `cradle_strap`（`for i in range(n_arc=28)` 沿 150°→-150° 约 300° 抱箍 swept strap）；body 仍为 root，base 仍可立地 |
| floor_stand | rec_fire_extinguisher_var_floor_stand | `floor_stand` ROOT part(base_plate+posts+ring+gussets) L74-124 / `stand_to_body` FIXED L370-376 / stand test L425-459 | eligible if compatible | **独立 `floor_stand` part 作 ROOT**：黑漆 `base_plate` Box（plate_size=0.200）+ `for i in range(2)` `post_{i}` 立柱 + 全环 `retainer_ring` torus（ring_major_r=0.068）+ `for i in range(2)` `gusset_{i}`；body 经 `stand_to_body` FIXED 坐于 `(0,0,plate_thickness)`；test `stand_at_ground`+`stand_plate_wide`(w>0.15)+`body_above_plate`+ ring 环绕 bottle |

> 无单 candidate 槽位。所有 4 slot 各 3 candidate。

## 槽位图（slot graph）

pattern: `parallel_children`（root = body 或 floor_stand；其余挂 body）

```
[Slot D mounting]
  none        : ROOT = body (base ring @ z=0)
  wall_bracket: ROOT = body ; bracket_back_plate + cradle_strap inline 到 body (-X 背板 + 300° 抱箍)
  floor_stand : ROOT = floor_stand (base_plate @ z=0) --[stand_to_body FIXED @ (0,0,plate_thickness)]--> body

[Slot A body_shape] 决定 body lathe profile (body_r / shoulder_z / dome_top_z / neck_top_z / banding / label / base_ring 宽)
  body
   ├─ (固定 visuals) base_ring · bottle(+banding) · shoulder_dome · valve_neck · valve_head · label_band
   │                 · gauge_stem/gauge_case/gauge_dial(-Y front) · carry_handle(-X 后挂) · safety_pin · pull_ring
   │
   ├─[Slot B operating_head 主关节 —— 锚点随 head 变]
   │    squeeze_lever : body 侧 lever_lug_{l,r}+lever_pin @ (pin_x,0,pin_z)
   │                    --[body_to_lever REVOLUTE axis=(0,1,0) [0,0.5]]--> operating_lever
   │    wheel_valve   : body 侧 valve_stem @ valve head 顶
   │                    --[body_to_wheel REVOLUTE axis=(0,0,1) [0,4π]]--> hand_wheel(hub+rim+spokes)
   │    top_pull_trigger: body 侧 trigger_guide boss @ valve head 顶
   │                    --[body_to_trigger PRISMATIC axis=(0,0,-1) [0,0.012]]--> trigger(cap+stem+ribs)
   │
   └─[Slot C discharge 侧挂 inline visual]
        hose_nozzle / co2_horn / hoseless_nozzle  (body visual, -Y/+X 侧出 valve head)
```

接口点位与策略：
- **mounting→body**：none/wall_bracket 时 body 自身是 root（base ring 立 z=0，`base_at_ground` 不变量）；floor_stand 时 floor_stand 是 root，body 经 FIXED 抬高 `plate_thickness`（`body_above_plate` min z>0.003，floor_stand `base_at_ground`）。wall_bracket 的 back_plate 前面贴瓶 `-（body_r+0.001)`、strap_r=`body_r+0.004` 抱箍 —— **抱箍/背板的 X/半径必须随 Slot A 的 body_r 重解析**（见 §9 conditional）。
- **operating_head→body**：所有 head 的 joint origin 锚于 valve head 顶（z 近 `neck_top_z`），**随 Slot A 的 neck_top_z 派生**；squeeze 用后 cross-pin（横 Y），wheel/trigger 用立轴顶（Z）。head 是唯一主关节；none/lever 时 body 是关节 parent，floor_stand 时 body 仍是 head parent（head 不直接挂 floor_stand）。
- **discharge→body**：侧挂 inline visual，控制点起于 valve head（z 近 head_z），末端贴瓶身（半径随 body_r），**随 Slot A body_r/shoulder_z 派生终点**。
- **互斥/可选**：4 slot 全独立可组合（无互斥）；floor_stand 与任意 head 兼容（FIXED 不影响 head 关节，但 head 锚点须以 body-local 解析，FIXED 仅平移 root）。

## 每槽位 Module Emits / Interfaces

### Slot A / module standard_cylinder | co2_tall_thin | squat_wide
| emits | 描述 | 来源 |
|---|---|---|
| parts | （改 body root visuals）`base_ring`·`bottle`(+banding)·`shoulder_dome`·`valve_neck`·`valve_head`·`label_band` | parent L62-171 |
| internal joints | 无（全 body visual）| — |
| upstream interface | body root 或经 mounting FIXED 抬高；base ring 底面 = 接地/坐板面 | parent L62-78 |
| downstream interface | valve head 顶面 z≈`neck_top_z`（head 锚点）；瓶身半径 body_r（discharge/strap 锚）；label 中段高度 | parent L116-148 |

### Slot B / module squeeze_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `operating_lever`（swept lever）；body 侧 `lever_lug_{l,r}`+`lever_pin`+`carry_handle` 为 body visual | parent L173-211,301-320 |
| internal joints | `body_to_lever` REVOLUTE axis=(0,1,0) lower=0 upper=0.5 effort=12 | parent L324-333 |
| upstream interface | joint origin `(pin_x,0,pin_z)` 锚于 valve head 后上方 | parent L329 |
| downstream interface | `allow_overlap(operating_lever,lever_pin)` captured hinge；`expect_contact(lever,body)` | parent L387,401 |

### Slot B / module wheel_valve
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hand_wheel`（hub+rim torus+`spoke_{i}`×5）；body 侧 `valve_stem` | wheel_valve L172-180,305-351 |
| internal joints | `body_to_wheel` REVOLUTE axis=(0,0,1) lower=0 upper=4π effort=8 | wheel_valve L353-363 |
| upstream interface | joint origin `(0,0,joint_z=head顶+stem_h)` 立轴 | wheel_valve L303,358 |
| downstream interface | `expect_contact(wheel,body)` on stem；`expect_within(rim,bottle,xy)` | wheel_valve L458,463 |

### Slot B / module top_pull_trigger
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trigger`（`trigger_cap`+`trigger_stem`+`grip_rib_{i}`×6）；body 侧 `trigger_guide` boss | top_pull_trigger L173-192,301-358 |
| internal joints | `body_to_trigger` PRISMATIC axis=(0,0,-1) lower=0 upper=0.012 effort=15 | top_pull_trigger L360-370 |
| upstream interface | joint origin guide boss 顶 `(0,0,trigger_top_z)` | top_pull_trigger L366 |
| downstream interface | `allow_overlap(trigger_stem,trigger_guide)`+`expect_within(trigger_stem,trigger_guide,xy)`+`expect_contact` | top_pull_trigger L445-464 |

### Slot C / module hose_nozzle | co2_horn | hoseless_nozzle
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual：`discharge_hose`+`discharge_nozzle` / `discharge_tube`+`discharge_horn` / `discharge_nozzle` | parent L271-296 / co2_horn L274-318 / hoseless L271-293 |
| internal joints | 无（全 body visual，固定侧挂）| — |
| upstream interface | 控制点起于 valve head（z≈head_z）| parent L272-273 |
| downstream interface | 末端贴瓶身（半径随 body_r）/ horn 大口朝下 / hoseless 直出 -Y | parent L278 / co2_horn L312 / hoseless L290 |

### Slot D / module none | wall_bracket | floor_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | （none 无）/ body inline `bracket_back_plate`+`cradle_strap` / 独立 `floor_stand`(base_plate+`post_{i}`+`retainer_ring`+`gusset_{i}`) | wall_bracket L310-340 / floor_stand L74-124 |
| internal joints | none/wall_bracket 无；floor_stand `stand_to_body` FIXED | floor_stand L370-376 |
| upstream interface | none/wall：body=root 立地；floor：floor_stand=root 立地 | floor_stand L77-82 |
| downstream interface | wall：back_plate 贴 -X 面、strap_r=body_r+0.004 抱箍；floor：body FIXED 坐 `(0,0,plate_thickness)` | wall_bracket L308,319 / floor_stand L375 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_shape | enum | standard_cylinder / co2_tall_thin / squat_wide | — | choice | deterministic procedural sampler | Slot A 表 |
| operating_head | enum | squeeze_lever / wheel_valve / top_pull_trigger | — | choice | deterministic procedural sampler | Slot B 表 |
| discharge | enum | hose_nozzle / co2_horn / hoseless_nozzle | — | choice | deterministic procedural sampler | Slot C 表 |
| mounting | enum | none / wall_bracket / floor_stand | — | choice | deterministic procedural sampler | Slot D 表 |
| palette_style | enum | classic_red / co2_black / chrome_steel / yellow_industrial / brass_vintage | classic_red | choice | 5 套 colorway（≥3 目标 4-6）；仅改 material rgba 不改拓扑 | 全样本 material L43-48 + floor_stand stand_paint L55 |
| body_r | float | [0.040, 0.100] | 0.056 | independent | 在范围内独立采样后 clamp；映射 Slot A choice 的标称值 | parent L51 / co2 L51 / squat L52 |
| body_aspect (shoulder_z/body_r) | float | derived | — | equation | `shoulder_z = aspect·body_r`，aspect∈[1.75,13.0] 由 Slot A choice 决定；dome_top_z=shoulder_z+0.070·k，neck_top_z=dome_top_z+0.040 | parent L52-54 / co2 L52-54 / squat L53-55 |
| banding_z / label_z | float | derived | — | equation | banding/label 高度 = shoulder_z 的固定比例（如 label∈[0.33,0.85]·shoulder_z）| parent L83,135 |
| head_anchor_z | float | derived | — | equation | `= neck_top_z`（+ stem_h for wheel）；head joint origin 随 Slot A 派生 | parent L155 / wheel L303 |
| discharge_end_r | float | derived | — | equation | discharge 末端贴瓶半径 `= body_r + ε`；随 Slot A body_r 派生 | parent L278 |
| wheel_upper | float | conditional | wheel: 4π；其它 head: n/a | conditional | 仅 wheel_valve 有 multi-turn range；lever upper=0.5，trigger upper=0.012 | wheel L361 / parent L332 / trigger L369 |
| n_spokes (wheel) | int | conditional | 5 | conditional | 仅 wheel_valve 有；module-local（非小类 multiplicity 轴），范围 [4,8] clamp | wheel L300 |
| wall_strap_r / wall_plate_x | float | conditional | wall: body_r+0.004 / -(body_r+0.001) | conditional | 仅 wall_bracket 有；随 Slot A body_r 重解析抱箍/背板 | wall_bracket L308,319 |
| stand_ring_major_r | float | conditional | floor: max(body_r+0.012, 0.068) | conditional | 仅 floor_stand 有；ring 内径须 ≥ body_r + 间隙 | floor_stand L67 |
| (—) | constraint | — | — | inequality | mounting=wall_bracket → strap_r > body_r（不穿模）；mounting=floor_stand → ring_major_r > body_r+0.008（瓶进环）；违反按比例外扩 ring/strap | wall L319 / floor L67 |
| (—) | constraint | — | — | inequality | head joint origin z ≥ neck_top_z 且 ≤ neck_top_z+0.040（致动件坐于阀块顶，不悬空/不沉入 dome）；违反按 neck_top_z 回缩 | parent L329 / wheel L358 / trigger L366 |

## Multiplicity / Copy Logic

- **无小类级复制数量逻辑**：核心多样性来自 4 个固定 named slot（body_shape × operating_head × discharge × mounting）的笛卡尔积，**不暴露小类级 `*_count` 轴**，不通过模板级循环复制 part/joint。
- 以下为 **module-local 固定/受限 for-loop**（非可暴露的小类 multiplicity 轴，已是源码内联循环）：
  - `lever_lug_{left,right}`：squeeze_lever 内 `for s,tag in ((1,"left"),(-1,"right"))` **固定 2 件 lug 对**（parent L197-204）。
  - `spoke_{i}`：wheel_valve 内 `for i in range(n_spokes)`，`n_spokes` 默认 5，作 module-local conditional 参数 clamp 至 [4,8]（wheel L333-347）；**不进 slot_choices 拓扑等价类**。
  - `grip_rib_{i}`：top_pull_trigger 内 `for i in range(6)` **固定 6 件装饰 rib**（trigger L341-354）。
  - `post_{i}`/`gusset_{i}`：floor_stand 内 `for i in range(2)` **固定 2 件柱/角板**（floor L87-96,111-120）；`cradle_strap` 内 `for i in range(n_arc=28)` 是 swept-spline 采样段（非部件复制）。
- 这些 module-local 计数固定或窄 clamp，不破坏 InterfaceSpec，不作小类多样性主轴。

## 拓扑多样性审计

总组合数：A × B × C × D = 3 × 3 × 3 × 3 = **81**（×5 palette_style 装饰层不计入拓扑）。

去重后 **distinct topology**（part 树 / joint type+axis / root parent 差异）估计：
- operating_head 给 3 类 distinct joint 拓扑（REVOLUTE-Y / REVOLUTE-Z-multiturn / PRISMATIC-Z）。
- mounting 给 3 类 distinct root 拓扑（body-root / body-root+inline 钣金 part-count / floor_stand-root+FIXED）。
- discharge 给 3 类 distinct discharge part-count/形态。
- body_shape 给 3 类比例族（part 树同构但 run_tests check 类不同，作温和拓扑等价区分）。
- 仅 operating_head(3) × mounting(3) 即 9 个**强 distinct**（joint+root），再 × discharge(3) part-count 区分 → 远超 27 distinct。

理由：operating_head 独立给 3 个 joint-topology（含 PRISMATIC vs 两类 REVOLUTE 轴），mounting 独立给 3 个 root-topology，二者笛卡尔积已 9，叠加 discharge part-count 多样轻松 >10；1000-seed 估计 slot choice tuple distinct >27（按 §211 类别约束，灭火器身份固定故 distinct 上限受 81 组合 + module-local clamp 限制，<300 合理，已说明）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng`（seed 派生）对 4 个 slot 各做加权 choice（小类无 multiplicity 加权档，slot 近均匀；可对 standard_cylinder/squeeze_lever/hose_nozzle/none 基线略加权以稳产基线身份），随后采 `body_r` independent → 派生 shoulder_z/dome/neck/banding/label/head_anchor/discharge_end → conditional 解析 wheel_upper/n_spokes/wall_strap/stand_ring → inequality 投影（strap/ring 外扩、head 锚 clamp）。`slot_choices_for_seed(seed)` 返回稳定 `[(body_shape,m),(operating_head,m),(discharge,m),(mounting,m)]`（连续 scale 不入，除非改拓扑等价类）。compatibility matrix 全合法（4 slot 无互斥）。regression overrides：none（无已知失败回归）。random sweep：seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检覆盖每个 head×mounting 角点（9 角）+ co2_horn/hoseless。
Topology target：1000-seed slot choice tuple distinct 目标 >27（受类别 81 组合上限 + 身份约束，<300 已说明原因：灭火器为低拓扑维度类别，主轴 = 4 个有限 slot）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：关键连续 scale = `body_r`（[0.040,0.100] independent）、`body_aspect`（equation 派生 shoulder/dome/neck）、`label_z_frac`/`banding_z_frac`（equation）、`discharge_end_r`（equation= body_r+ε）、`wall_strap_r`/`stand_ring_major_r`（conditional+inequality 外扩）、`n_spokes`（conditional [4,8] clamp）。全部在 `resolve_config` clamp/派生/投影，遵循 independent→equation→inequality→conditional 契约，不破坏 head 锚点 / 抱箍间隙 / 接地不变量 / 类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 slot 加权 choice（基线略加权）+ body_r independent + 派生/conditional/inequality | slot_choices_for_seed matches build choices |
| compatibility matrix | 4 slot 全合法可组合（无互斥）；floor_stand=独立 root，head 锚点以 body-local 解析；wall/floor 间隙随 body_r conditional 外扩 | no floating, collision, axis, root parent, optional child failures |
| controlled local variation | body_r + aspect + label/banding frac + discharge_end_r + strap/ring + n_spokes，全 clamp/派生/投影 | proportions vary without breaking head anchor, clearance, ground contact, joint origin, identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_shape | 3 | yes | yes | 比例族 + 不同 body-check 类 |
| B operating_head | 3 | yes | yes | 3 distinct joint 拓扑（defining joint）|
| C discharge | 3 | yes | yes | 3 distinct discharge 形态/part-count |
| D mounting | 3 | yes | yes | 3 distinct root 拓扑 |

## Validator

- slot_choices_for_seed returns implemented module names（4 slot × 各 3 candidate）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combinations（4 slot 全合法；floor_stand root + head 锚点 body-local 解析）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params（body_r/aspect/label/discharge_end/strap/ring/n_spokes）clamped/derived in `resolve_config`，不破坏 head 锚点 / 抱箍间隙 / 接地 / 关节 origin
- cross-part scale dependencies（aspect/discharge_end/strap/ring inequality+conditional）resolved in `resolve_config`，not builder
- critical InterfaceSpec / MatingContract：head joint origin ∈ [neck_top_z, neck_top_z+0.040]；floor_stand FIXED 坐 plate 顶；wall back_plate 贴瓶 -X
- key joints：body_to_lever REVOLUTE axis≈(0,1,0) [0,0.5] / body_to_wheel REVOLUTE axis≈(0,0,1) [0,4π] / body_to_trigger PRISMATIC axis≈(0,0,-1) [0,0.012] / stand_to_body FIXED
- copied objects（lug pair / spokes / ribs / posts）follow naming and placement policy（module-local 固定或窄 clamp）
- gauge_dial 恒存在且在 -Y front；label_band 中段；base/stand 接地 z≈0

## Reject cases

- operating_head 致动件缺失或退化为 fixed（无 defining joint）→ 出类（必须有 1 个非 fixed 主关节）。
- gauge_dial 缺失或不在 -Y front，或 valve_neck/valve_head/carry_handle 缺失 → 失类别身份。
- squeeze_lever axis 非横 Y（如误配立轴）或 wheel/trigger 误配横轴 → joint 语义错。
- floor_stand 选中但 body 未 FIXED 坐于 plate（body 悬空或穿 plate / ring 内径 < body_r 穿模）→ reject。
- wall_bracket 抱箍 strap_r ≤ body_r（背板/抱箍穿瓶）或背板不贴 -X 面 → reject。
- body_r 超 [0.040,0.100] 或 aspect 失配致瓶非直立（standard/co2 应 h>w·1.6，squat 应 w>0.16）→ clamp 失败 reject。
- head joint origin 沉入 dome 或悬于阀块上方过高（越 [neck_top_z, neck_top_z+0.040]）→ reject。
- discharge 末端脱离瓶身（end_r 未随 body_r 派生，悬空）→ reject。
- base ring / floor plate 不接地（abs(min z) 越界）→ reject。

## 与相邻类别的边界

- 不该混入：**Fire Hydrant（消防栓）**——固定地桩 + 顶帽螺母 + 侧向出水法兰 + 链帽；无可提瓶身、无 gauge、无 squeeze lever / pull ring；root 为埋地桩而非可提钢瓶即出类。
- 不该混入：**fire bucket（bucket1 消防沙桶）**——敞口锥/圆桶 + 提梁，无 valve head / gauge / discharge / 致动机构；开口空桶即出类。
- 不该混入：**gas cylinder / propane tank（储气瓶）**——直立钢瓶 + 顶阀手轮但缺 carry handle + gauge + discharge 这套灭火器身份；仅瓶+手轮无三件套即降为储气瓶（wheel_valve 变体因保留三件套仍读作灭火器）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |
