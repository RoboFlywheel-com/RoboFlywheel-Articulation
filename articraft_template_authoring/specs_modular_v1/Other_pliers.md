# pliers — Modular Spec

> 来源小类：`picture/Other/pliers`（articraft_data 上游小类样本池；对象身份为 a pair of pliers——两片锻钢半钳绕中央铆钉枢轴交叉，颚口夹合、手柄张合）。slug 取规范拼写 `pliers`。
> 上游 source map：`picture_expansion/template_source_maps/Other__Other_pliers.md`。
> **同步状态**：本 spec 引用的 8 个 5★ 样本（2 母资产 + 6 单轴 fork 变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 计。引用以 part/joint/helper **名字** 为准（`_jaw_solid` / `_hub_solid` / `_hub_slotted_solid` / `_shank_solid` / `_grip_solid` / `_inlay_solid` / `_bow_arm` / `_bow_ring` / `_toggle_link_solid` / `_groove_step_solid` / `_groove_solid` / `_tongue_solid` / `_carrier_link_solid` / `plier_half_0` / `plier_half_1` / `pivot_carriage` / `pivot_carrier` / `toggle_link` / `pivot` / `slot_slide` / `groove_select` / `jaw_pivot` / `toggle` 等），行号仅作定位。
> **source map 偏差更正（重要）**：(1) source map 称 P2 为 "2 REVOLUTE"，实读 P2 (`lineman`) 只有**单一中央 `pivot` REVOLUTE**（rivet 为 half_0 的固定 visual，不是关节）；本 spec 的 "2 关节" 只出现在 locking_vise_grip（+toggle REVOLUTE）与两个 slip 机构（PRISMATIC+REVOLUTE）。(2) source map 的 `groove_count` 多重性轴列出 `rec_variant-groove-count-3-...` / `rec_variant-groove-count-7-...` 两个 N 样本，但这两个 record **在本仓库 records-root 中不存在**（见 §排除/缺源）——groove multiplicity 的唯一真实源是 slip_joint 的 `GROOVE_COUNT=2` 与 tongue_and_groove 的 `GROOVE_COUNT=5` 两个 parent + 二者各自的 `for i in range(GROOVE_COUNT)` 循环范式。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pliers` |
| template path | `agent/templates/Other_pliers.py` |
| test path (optional) | `tests/agent/test_pliers_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（核心机构 = 两半钳绕中央铆钉 REVOLUTE 开合的 2-bar 链；pivot_mechanism 槽可把链插入一个滑动 carrier（PRISMATIC + REVOLUTE 3-part 链）；jaw_function / handle_form 是两半上成对镜像应用的可替换几何层；jaw_function=locking_vise_grip 追加可选 toggle 第二 REVOLUTE 子件；groove_count 是 slip 机构下的同构 detent/groove 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 parent 母资产 + 6 单轴 fork 变体；均 converged、compile=success、workbench-only、≥1 非 fixed joint、均为真实双臂中央枢轴钳）|
| read_count | 8（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（小类只有这 8 个，无抽样；source map 另列的 groove-count-3 / groove-count-7 两 record 在 records-root 不存在，无法读，见 §排除）|
| source_index_policy | only adopted module sources are indexed below（8 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **P1 flush_cut_snips**（`rec_model-a-pair-of-compact-flush-cut-wire-snips-ele_..._e0ef2013` ← picture/Other/pliers/001.png）：紧凑平口断线钳。两片镜像 steel 半（`lower_cutter_half` root / `upper_cutter_half` child），各 = 锥形剪刃 (`_half_blade`) + pivot boss (`_half_boss`) + neck tang + 浸塑直柄 (`_soft_prism` GRIP_PTS) + peach inlay。单一 `rivet_pivot` REVOLUTE 绕 +Z（出平面），lower=0（rest=open splay）upper=CLOSE_TRAVEL(~25°) 闭刃。rivet 为 lower 的固定 visual。**Slot A 基线 flush_cutter + Slot B 基线 straight_dipped + Slot C 基线 fixed_rivet 来源（紧凑型）**。
- **P2 lineman_pliers**（`rec_model-heavy-duty-combination-lineman-pliers-abou_..._2d2cf55e` ← picture/Other/pliers/002.png；**fork 主母资产**）：重型综合电工钳。两片半 (`plier_half_0` root / `plier_half_1` child)，各 = 方头综合咬颚（`_jaw_solid`：squared nose + 横纹 serration + pipe-grip recess + wire-cutter notch）+ 锻造圆 hub (`_hub_solid`) + steel tang (`_shank_solid`) + 黑橡胶 over-mold 柄 (`_grip_solid` ellipse loft) + red inlay (`_inlay_solid`)。两半在 pivot 处 half-lap（`_lap_cut`：half_0 下层 / half_1 上层互错）。单一 `pivot` REVOLUTE 绕 -Z，lower=0(closed)…upper=30°(open)。一体 rivet（seam+boss+shaft+head）固定于 half_0，captured 穿过 half_1 lap（`allow_overlap` rivet_shaft↔hub1）。**Slot A 基线 combination_grip + Slot B 基线 straight_dipped + Slot C 基线 fixed_rivet 来源（重型，全批 fork 基底）**。
- **V1 needle_nose**（`rec_variant-jaw-function-needle-nose-..._7b198890`，fork P2）：把综合方颚换成**长尖嘴**——`_jaw_solid` 改为沿 `NEEDLE_STATIONS`（8 站 (x, hw, hh)，base 0.013→tip 0.0008，长 0.075）的 `makeLoft` 渐细矩形截面（`_jaw_section_wire`），加 14 道横纹 serration + base wire-cutter notch。hub/shank/grip/rivet/pivot 全同 P2。**Slot A：needle_nose 来源**。
- **V2 locking_vise_grip**（`rec_variant-jaw-function-locking-vise-grip-..._1903a019`，fork P2）：**锁定 vise-grip**——`_jaw_solid` 改弯曲 C 形夹颚（inner/outer 弧 polyline + 交叉网纹 serration + 夹槽 recess）；**新增第 3 part `toggle_link`**（`_toggle_link_solid` 扁钢杆 + toggle_pin）挂 half_0，含**第二 REVOLUTE `toggle`** 绕 +Z（lower=-0.05…upper=TOGGLE_RANGE=25°，over-center 锁死）；并加 half_0 把端 `adjustment_screw` 固定 visual（`_adjustment_screw_solid`）。主 `pivot` REVOLUTE 同 P2。**Slot A：locking_vise_grip 来源（+可选 toggle 第二关节）**。
- **V3 looped_bow**（`rec_variant-handle-form-looped-bow-..._dbc49fe3`，fork P1）：把 P1 两片直柄换成**闭环指圈柄**——`_bow_arm`（neck polyline prism）+ `_bow_ring`（`TorusGeometry`，major 0.013 / tube 0.003 finger ring）替代 `_soft_prism` grip。blade/boss/tang/rivet/单 pivot 全同 P1。**Slot B：looped_bow 来源（scissor-style finger loop）**。
- **V4 cushioned_ergonomic**（`rec_variant-handle-form-cushioned-ergonomic-..._11ae9efe`，fork P2）：把 P2 over-mold 柄换成**厚软人体工学柄**——`_grip_solid` 用加厚 `GRIP_SECTIONS`（half-height>0.014、宽>0.010）+ 指槽 ridge 凹槽 loft，run_tests 断言厚>28mm/宽>20mm。jaw/hub/shank/rivet/单 pivot 全同 P2。**Slot B：cushioned_ergonomic 来源**。
- **V5 slip_joint**（`rec_variant-pivot-mechanism-slip-joint-..._9df407d7`，fork P2）：**滑销式 slip-joint pivot**——half_0 的 hub 换成开椭圆槽 hub (`_hub_slotted_solid` = `_hub_solid` cut `_slot_cut_solid` 胶囊槽，SLOT_LENGTH 0.020)；**新增第 3 part `pivot_carriage`**（rivet seam/boss/shaft/head 全移到 carriage）。**链改为 half_0 →[PRISMATIC `slot_slide` 轴 +X，行程 ±SLOT_TRAVEL/2]→ carriage →[REVOLUTE `pivot` 轴 -Z 0…30°]→ half_1**。half_0 上经 `for i in range(GROOVE_COUNT)`（默认 2）+ 共享 `_groove_solid(i)` 发射 `groove_{i}` detent 固定 visual。**Slot C：slip_joint 来源（PRISMATIC+REVOLUTE 3-part 链）+ groove_count 多重性范式源（GROOVE_COUNT=2）**。
- **V6 tongue_and_groove**（`rec_variant-pivot-mechanism-tongue-and-groove-..._90e7c88e`，fork P2）：**channel-lock 调宽 tongue-and-groove**——lower_half shank 上经 `for i in range(GROOVE_COUNT)`（默认 5）+ 共享 `_groove_step_solid()` 发射 `groove_{i}` 凹槽轨（沿 -X 等距 GROOVE_SPACING）；**新增第 3 part `pivot_carrier`**（`_tongue_solid` 舌 + `_carrier_link_solid` 连杆 + `_button_solid` 橙按钮）。**链改为 lower →[PRISMATIC `groove_select` 轴 +X，行程 PRISMATIC_TRAVEL=GROOVE_SPACING·(N-1)]→ carrier →[REVOLUTE `jaw_pivot` 轴 -Z 0…30°]→ upper**。**Slot C：tongue_and_groove 来源（channel-lock 调宽 PRISMATIC+REVOLUTE 3-part 链）+ groove_count 多重性主源（GROOVE_COUNT=5 + 等距 placement + 行程随 N 派生）**。

冗余说明：8 个样本核心机构（两片镜像锻钢半绕中央铆钉相对开合、颚口闭合/手柄张开、hub half-lap、captured rivet shaft）完全同构；每个 fork 只改 1 根结构轴（颚形 / 柄形 / 枢轴机构），diff 干净。P1 是紧凑剪刃型、P2 是重型综合型，二者占 jaw_function 槽两个基线。

## 核心身份

一把钳子 / 一对手钳（a pair of pliers）：两片镜像**锻钢半钳**，**绕单一中央铆钉枢轴交叉**，铆钉前方是成对**颚口**（jaws，相对夹合 / 切断 / 咬持），后方延伸成两条**手柄**（handles，相对张合驱动颚口）。**主用户机构 = 两半绕中央铆钉的相对开合**（REVOLUTE，轴 = 出平面 Z），合颚 = 闭、张柄 = 开。两 hub 在枢轴处 half-lap 互错叠合，一根 rivet shaft captured 穿过两 lap（captured-pin 过盈，配 broad `allow_overlap`）。

物体平躺 XY 平面（Z = 厚度/枢轴方向）：颚尖指 +X，手柄向 -X 张开于 ±Y；铆钉枢轴在世界原点 (0,0,0)。half_0（jaw 在 +Y）为 root，half_1（mirror，jaw 在 -Y）为 moving child。每半在 pivot 居原点的局部 frame 内 author（`s=±1` 镜像），颚口内面落 `y = s·JAW_FACE`。

默认成熟域：真实手工具小尺度（P1 紧凑型整长 ~0.13 m、P2 重型整长 ~0.20 m）。颚形可为平口剪刃 / 综合方头咬剪 / 长尖嘴 / 弯曲锁定夹颚；手柄可为浸塑直柄 / 闭环指圈 / 厚软人体工学；枢轴可为固定铆钉（1 REVOLUTE）/ slip-joint 滑销（PRISMATIC+REVOLUTE，移位扩容）/ channel-lock tongue-and-groove（PRISMATIC+REVOLUTE，沿 N 槽调宽）。活动语义恒含"两半绕中央 Z pivot 相对开合"；slip 机构再叠一个 PRISMATIC 调位轴；locking 颚再叠一个 toggle REVOLUTE。rivet seam/boss/head 恒为固定装饰（inline 成 half_0 或 carriage 的 visual，不做独立 FIXED 装饰 part；carriage/carrier 是真实滑动 part，非装饰）。

不该混入：**剪刀 / scissors**（见 §与相邻类别的边界——两薄刃 shear + finger-loop，与本类颚口夹合 / 锻钢咬颚是不同结构家族，且本仓库已有独立 `scissors` 模板）、单刃刀具、订书机 / 打孔器（压合冲孔、不出双臂枢轴）、扳手 / spanner（无枢轴开合的固定开口）、镊子 / tweezers（无中央铆钉枢轴，弹性夹臂）。

## 槽位 + 候选模块表

> **建模注记（重要）**：pliers 的链拓扑由 **Slot C (pivot_mechanism)** 决定，是本类拓扑变化的主轴：
> - `fixed_rivet`：**2-part 链** half_0 →[REVOLUTE pivot]→ half_1，rivet 为 half_0 inline visual。
> - `slip_joint` / `tongue_and_groove`：**3-part 链** half_0 →[PRISMATIC]→ carriage/carrier →[REVOLUTE]→ half_1，新增 1 个真实滑动 part + 1 个 PRISMATIC 关节 + groove 多重性。
>
> **Slot A (jaw_function)** 与 **Slot B (handle_form)** 是两半上**成对镜像应用的可替换几何层**（两半同形仅 `s=±1` mirror），改 part-internal visual 几何（`_jaw_solid` / grip helper），通常不改 part/joint 计数——**例外**：`jaw_function=locking_vise_grip` 追加 1 个 `toggle_link` part + 1 个 toggle REVOLUTE（Slot A 内可选第二活动子件）。
> 下面 3 个离散 slot + 1 个 conditional multiplicity 轴。

### Slot A：jaw_function（钳头颚口功能；**主机构槽之一**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_cutter（基线，紧凑）| P1 | `_half_blade` L184-188 + `JAW_PTS` L63-73 + `_bevel_wedge` L161-175 | eligible if compatible | 锥形剪刃 polyline，刃口沿中线收 land，bevel 楔切出 flush 刃；紧凑剪断型，配 single rivet |
| combination_grip（基线，重型）| P2 | `_jaw_solid` L126-179 | eligible if compatible | 方头综合咬剪颚：squared nose + 7 道横纹 serration + 圆 pipe-grip recess + scallop 齿 + wire-cutter V-notch；最通用基底 |
| needle_nose | V1 | `_jaw_solid` L153-178 + `NEEDLE_STATIONS` L130-139 + `_jaw_section_wire` L142-150 | eligible if compatible | 长尖嘴：8 站矩形截面 `makeLoft` 渐细（base 0.013→tip 0.0008，长 0.075）+ 14 道横纹 + base notch；长>>宽 taper |
| locking_vise_grip | V2 | `_jaw_solid` L146-226（弯 C 颚）+ `_toggle_link_solid` L265-313 + `_adjustment_screw_solid` L316-352 + toggle 关节 L483-496 | eligible if compatible | 弯曲 C 形夹颚 + 交叉网纹 + 夹槽；**追加第 3 part `toggle_link` + 第二 REVOLUTE `toggle` 绕 +Z（over-center 锁死）+ 把端 adjustment_screw 固定 visual** |

> 4 candidate（达 3-6 目标）。每个颚形改 `_jaw_solid` 的 polyline/loft 轮廓 + run_tests 几何断言（needle taper 比、locking C 弧 + toggle 关节存在），结构差异成立；locking_vise_grip 另改 part/joint 计数（+toggle）。

### Slot B：handle_form（手柄形态；两半镜像几何层）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_dipped（基线）| P1 / P2 | P2 `_grip_solid` L201-207 + `_inlay_solid` L210-216 + `GRIP_SECTIONS` L57-66；P1 `_soft_prism` L139-153 + `GRIP_PTS` L88-101 | eligible if compatible | 直浸塑/over-mold 柄：ellipse loft（重型）或 soft spline prism（紧凑），flared 拇指护 + bulbous 端，配 red/peach inlay 条 |
| looped_bow | V3 | `_bow_arm` L203-212 + `_bow_ring` L215-225 + `BOW_RING_R/BOW_TUBE_R` L56-57 | eligible if compatible | 闭环指圈柄（scissor-style）：neck arm prism + `TorusGeometry` finger ring（major 0.013 / tube 0.003）替代实心 grip；两半各一闭环 ring |
| cushioned_ergonomic | V4 | `_grip_solid` L214-247 + 加厚 `GRIP_SECTIONS` L59-80 + `_grip_h` L105-107 | eligible if compatible | 厚软人体工学柄：加厚截面（半高>0.014 / 半宽>0.010）+ 指槽 ridge 凹槽 loft；run_tests 断言厚>28mm / 宽>20mm |

> 3 candidate（达目标下限）。三者改手柄层 part-internal 几何（实心直柄 / 闭环指圈 ring / 加厚带指槽），结构差异成立（looped_bow 引入 torus 闭环、cushioned 改截面族），非纯尺寸/颜色。

### Slot C：pivot_mechanism（枢轴机构；**主机构槽之二，决定链拓扑**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_rivet（基线）| P1 / P2 | P2 `_hub_solid` L182-185 + rivet visual L266-295 + `pivot` REVOLUTE L300-308；P1 `_half_boss` L191-200 + `_rivet` L203-214 + `rivet_pivot` L306-314 | eligible if compatible | 固定铆钉：两 hub half-lap，rivet 为 half_0 inline visual，**单一 REVOLUTE 开合**；2-part 链，无 groove |
| slip_joint | V5 | `_hub_slotted_solid` L234-239 + `_slot_cut_solid` L213-231 + `pivot_carriage` 部件 L397-434 + `slot_slide` PRISMATIC L441-454 + `pivot` REVOLUTE L459-472 + `_groove_solid`/`_groove_x` L254-285 | eligible if compatible | 滑销 slip-joint：half_0 开椭圆槽 hub，**第 3 part `pivot_carriage`（rivet 组件）经 PRISMATIC `slot_slide`（轴 +X，±SLOT_TRAVEL/2）滑动 + REVOLUTE `pivot` 开合**；half_0 上 `for i in range(GROOVE_COUNT=2)` detent 多重性 |
| tongue_and_groove | V6 | `_groove_step_solid` L250-256 + `_tongue_solid` L258-261 + `_carrier_link_solid` L280-287 + `_button_solid` L263-277 + `pivot_carrier` 部件 L340-359 + `groove_select` PRISMATIC L395-406 + `jaw_pivot` REVOLUTE L410-421 | eligible if compatible | channel-lock 调宽：lower shank 上 `for i in range(GROOVE_COUNT=5)` 等距凹槽轨，**第 3 part `pivot_carrier`（tongue+link+button）经 PRISMATIC `groove_select`（轴 +X，行程 = GROOVE_SPACING·(N-1)）沿槽索引 + REVOLUTE `jaw_pivot` 开合**；groove_count 主多重性源 |

> 3 candidate（达目标下限）。三者改链拓扑：fixed_rivet=2-part/1-joint；slip_joint / tongue_and_groove 各 +1 滑动 part + 1 PRISMATIC，结构差异显著（非尺寸）。

## 槽位图（slot graph）

```
pattern: mixed（2-bar pivot 链；pivot_mechanism 可把链改成 3-part 滑动链 + groove 多重性；
                jaw/handle 为两半镜像几何层；locking 颚追加 toggle 子件）

  ── Slot C = fixed_rivet（2-part 链）──
    plier_half_0 (root) ──[REVOLUTE pivot, axis Z, origin (0,0,0) 真实铆钉]──> plier_half_1 (child)
      承载: jaw[Slot A]·hub(half-lap)·shank·grip[Slot B]·rivet(inline)        承载: jaw[A 镜像]·hub·shank·grip[B 镜像]

  ── Slot C = slip_joint / tongue_and_groove（3-part 链）──
    plier_half_0/lower (root) ──[PRISMATIC slot_slide/groove_select, axis +X]──> pivot_carriage/pivot_carrier
      承载: jaw[A]·slotted_hub 或 groove track[N]·shank·grip[B]                      （rivet 组件 或 tongue+link+button）
                                                                                          │
                                                                  [REVOLUTE pivot/jaw_pivot, axis Z, 0..30°]
                                                                                          ↓
                                                                          plier_half_1/upper (moving child)
                                                                            承载: jaw[A 镜像]·hub·shank·grip[B 镜像]

  ── Slot A = locking_vise_grip 追加（任一 Slot C 之上）──
    plier_half_0 ──[REVOLUTE toggle, axis +Z, origin (TOGGLE_PIVOT_X, yc, 0)]──> toggle_link (over-center 锁)

  groove_count[N]（multiplicity，仅 Slot C∈{slip_joint, tongue_and_groove}）：
    for i in range(N): groove_{i} 沿 shank 等距固定 visual（共享 helper），PRISMATIC 行程随 N 派生
  rivet seam/boss/head：fixed_rivet 时 half_0 inline visual / slip 机构时 carriage inline visual（FIXED 语义，非独立装饰 part）
```

接口点位（每条连接）：
- **half_0 → half_1（fixed_rivet，pivot）**：mating = 中央铆钉轴线（`origin=(0,0,0)`，两 hub half-lap 共轴），joint = REVOLUTE，axis `(0,0,±1)`，range `[0, OPEN_LIMIT≈30°]`（紧凑 P1 用 [0, CLOSE_TRAVEL]，语义同：rest splay→闭合）。MatingContract **省略（grandfathered）**：rivet shaft captured 穿 half_1 lap，配 broad `allow_overlap(half_0, half_1)`（P2 L384-391 已声明 reason）。origin 落 hub/rivet 真实几何 (≤0.002 m)。
- **half_0 → carriage/carrier（slip_joint/tongue_and_groove，PRISMATIC）**：mating = slotted hub 槽 / groove 轨（`origin` 落 SLOT 中心或 GROOVE_X_START 真实几何），joint = PRISMATIC，axis `(1,0,0)`，range = slip:`[-SLOT_TRAVEL/2, +SLOT_TRAVEL/2]` / channel-lock:`[0, GROOVE_SPACING·(N-1)]`。carriage rivet shaft captured 穿 half_1（broad allow_overlap）。
- **carriage/carrier → half_1（slip 机构，REVOLUTE）**：joint = REVOLUTE，axis `(0,0,-1)`，range `[0, OPEN_LIMIT]`；origin (0,0,0) 落 carriage rivet 几何。
- **half_0 → toggle_link（locking_vise_grip，REVOLUTE toggle）**：mating = 把内 toggle pin（`origin=(TOGGLE_PIVOT_X, yc, 0)` 落 toggle_pin 真实几何），joint = REVOLUTE，axis `(0,0,1)`，range `[-0.05, TOGGLE_RANGE≈25°]`（over-center 锁）。
- **groove_{i}**：non-articulated 固定 visuals（half_0/lower shank 上同 part 内），各 groove 沿 -X 等距 `GROOVE_X_START + i·GROOVE_SPACING`（channel-lock）或 slot 两侧 detent（slip）；共享 helper 发射。
- **rivet seam/boss/head、adjustment_screw、jaw serration / recess / notch**：half_0 或 carriage 的 inline visuals（FIXED 语义，不建独立装饰 part）。
- **互斥/可选/派生**：Slot C 决定 2-part vs 3-part 链（互斥）；groove_count multiplicity 仅在 Slot C∈{slip_joint, tongue_and_groove} 时存在（conditional，fixed_rivet 下 N 无意义）；toggle 子件仅 jaw_function=locking_vise_grip 时存在；Slot A/B 在两半上**镜像派生**（half_1 = half_0 `s=-1` mirror）。

## 每槽位 Module Emits / Interfaces

### Slot A / module flush_cutter
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_blade`（锥形剪刃 polyline，bevel 楔切出 flush 刃，刃口沿中线 land）| P1 / `_half_blade` L184-188、`_bevel_wedge` L161-175 |
| internal joints | 无（刃是 part visual）| — |
| downstream interface | 刃口在中线相会（闭合接触），刃根 hub 在 pivot | P1 / L63-73 |

### Slot A / module combination_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw`（方头综合咬颚 + serration + pipe-grip recess + wire-cutter notch）| P2 / `_jaw_solid` L126-179 |
| downstream interface | 颚内面 `y=s·JAW_FACE` 闭合近触；颚根 hub half-lap 在 pivot | P2 / L126-179 |

### Slot A / module needle_nose
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw`（长尖嘴 lofted 渐细 + 横纹 serration + base notch）| V1 / `_jaw_solid` L153-178、`NEEDLE_STATIONS` L130-139 |
| downstream interface | 长>>宽 taper，tip 收至 0.0008，内面闭合近触 | V1 / L130-178 |

### Slot A / module locking_vise_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `toggle_link`（over-center 扁钢杆 + toggle_pin）；half_0 加 `adjustment_screw` 固定 visual | V2 / `_toggle_link_solid` L265-313、`_adjustment_screw_solid` L316-352 |
| visuals | `jaw`（弯曲 C 形夹颚 + 交叉网纹 + 夹槽 recess）| V2 / `_jaw_solid` L146-226 |
| internal joints | `toggle` REVOLUTE，axis (0,0,1)，range [-0.05, TOGGLE_RANGE≈25°]（half_0→toggle_link）| V2 / L483-496 |
| upstream interface | toggle pin 落把内真实几何 (TOGGLE_PIVOT_X, yc, 0) | V2 / L88-91、L483-488 |

### Slot B / module straight_dipped
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip`（直浸塑/over-mold 柄 loft）+ `grip_inlay`（外/顶面 red/peach 条）| P2 `_grip_solid` L201-207、`_inlay_solid` L210-216；P1 `_soft_prism` L139-153 |
| upstream interface | grip 接 shank/tang 末端，向 -X 张开 | P2 / L57-66 |

### Slot B / module looped_bow
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `bow_arm`（neck arm prism）+ `bow_ring`（TorusGeometry finger ring，闭环）| V3 / `_bow_arm` L203-212、`_bow_ring` L215-225 |
| upstream interface | arm 接 neck tang 末端，ring 中心 (BOW_RING_CX, s·BOW_RING_CY)；两半各一闭环 | V3 / L56-66、L218-225 |

### Slot B / module cushioned_ergonomic
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip`（加厚带指槽 ridge 的人体工学 loft）+ `grip_inlay` | V4 / `_grip_solid` L214-247 |
| upstream interface | grip 接 shank 末端；厚>28mm / 宽>20mm | V4 / L59-80 |

### Slot C / module fixed_rivet
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `hub`（half-lap）+ rivet seam/boss/shaft/head（half_0 inline）| P2 `_hub_solid` L182-185、rivet L266-295；P1 `_half_boss` L191-200、`_rivet` L203-214 |
| internal joints | `pivot`/`rivet_pivot` REVOLUTE，axis (0,0,±1)，range [0, OPEN_LIMIT]（half_0→half_1）| P2 / L300-308；P1 / L306-314 |
| upstream/downstream interface | rivet shaft captured 穿 half_1 hub lap（broad allow_overlap）；origin (0,0,0) | P2 / L384-391 |

### Slot C / module slip_joint
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pivot_carriage`（rivet seam/boss/shaft/head 组件，滑动 part）| V5 / L397-434 |
| visuals | half_0 `hub`（开椭圆槽，`_hub_slotted_solid`）；`groove_{i}`×N detent（共享 `_groove_solid`）| V5 / `_hub_slotted_solid` L234-239、`_slot_cut_solid` L213-231、groove L254-285/388-393 |
| internal joints | `slot_slide` PRISMATIC，axis (1,0,0)，range [-SLOT_TRAVEL/2, +SLOT_TRAVEL/2]（half_0→carriage）；`pivot` REVOLUTE，axis (0,0,-1)，range [0, OPEN_LIMIT]（carriage→half_1）| V5 / L441-472 |
| upstream interface | rivet shaft captured 穿 slot + half_1 lap（broad allow_overlap）| V5 / L399-405 |

### Slot C / module tongue_and_groove
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pivot_carrier`（`tongue` + `link` + `button` 组件，滑动 part）| V6 / L340-359 |
| visuals | lower shank `groove_{i}`×N 等距凹槽轨（共享 `_groove_step_solid`）| V6 / `_groove_step_solid` L250-256、循环 L330-337 |
| internal joints | `groove_select` PRISMATIC，axis (1,0,0)，range [0, GROOVE_SPACING·(N-1)]（lower→carrier）；`jaw_pivot` REVOLUTE，axis (0,0,-1)，range [0, OPEN_LIMIT]（carrier→upper）| V6 / L395-421 |
| upstream interface | tongue 索引进 groove 轨；carrier 经 button/link 穿 upper lap | V6 / L258-287、L342-359 |

### groove_count multiplicity / module groove_{i}（见 §Multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `groove_{i}`（沿 shank 等距 detent/凹槽）× N，共享 helper 发射 | V6 `_groove_step_solid` + 循环 L330-337；V5 `_groove_solid` + 循环 L388-393 |
| internal joints | 无（同 half_0/lower part 内固定 visual；PRISMATIC 行程随 N 派生）| V6 / L330-337、L400-405 |
| upstream interface | groove_0 在 GROOVE_X_START，间距 GROOVE_SPACING；行程 PRISMATIC_TRAVEL = GROOVE_SPACING·(N-1) | V6 / L43-46、L330-337 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_function | enum | {flush_cutter, combination_grip, needle_nose, locking_vise_grip} | combination_grip | choice | deterministic procedural sampler 选择 | Slot A 表 |
| handle_form | enum | {straight_dipped, looped_bow, cushioned_ergonomic} | straight_dipped | choice | sampler 选择 | Slot B 表 |
| pivot_mechanism | enum | {fixed_rivet, slip_joint, tongue_and_groove} | fixed_rivet | choice | sampler 选择；决定 2-part vs 3-part 链 | Slot C 表 |
| groove_count | int | [2, 7] | 5 | conditional | 仅 pivot_mechanism∈{slip_joint, tongue_and_groove} 有效；加权采样（小 N 偏多）后 clamp；fixed_rivet 下不暴露 | §Multiplicity / V5 `GROOVE_COUNT=2`、V6 `GROOVE_COUNT=5` 循环 |
| palette_style | enum | {steel_red_dipped, black_chrome, gunmetal_yellow, polished_blue, chrome_natural} | steel_red_dipped | palette | **palette only，不计入 slot_choice / 拓扑**；按 seed 采样 | P1/P2/各样本配色 |
| overall_len_scale | float | [0.85, 1.20] | 1.0 | independent | 整体等比缩放（颚长 + shank + grip + hub），clamp 保真实手工具尺度（P1~0.13→P2~0.20 区间）| P1/P2 整体尺寸 |
| jaw_len_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放颚长（NOSE_X / NEEDLE 链长），clamp 保闭合接触 | P2 `NOSE_X` L40、V1 `NEEDLE_STATIONS` |
| grip_girth_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 grip 截面族（半宽/半高），clamp 保不与对半 grip 在 rest 互穿 | P2 `GRIP_SECTIONS`、V4 加厚 |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放主 REVOLUTE `upper` 张开角；clamp 到 [15°, 40°] 真实开度 | P2 `OPEN_LIMIT` L41 |
| slide_travel_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 slip 机构有效；缩放 PRISMATIC 行程（≤ slot/groove 轨真实长度）| V5 `SLOT_TRAVEL` L57、V6 `PRISMATIC_TRAVEL` L46 |
| (—) | constraint | — | — | inequality | 中央 pivot/PRISMATIC origin 必须落 hub/rivet/slot 真实几何 (0,0,0)±0.002 m；scale 放大颚/柄时 hub/rivet/slot 尺寸不随之失配，origin 仍贴几何 | 接口 / captured-pin |
| (—) | constraint | — | — | inequality | groove_count=N 时槽轨总跨 `GROOVE_X_START + (N-1)·GROOVE_SPACING` 须落 lower shank 真实长度内（不出 shank 尾）；PRISMATIC 行程 = GROOVE_SPACING·(N-1) 同步派生 | V6 / L43-46 |
| (—) | constraint | — | — | conditional | groove_count / slide_travel_scale 仅 pivot_mechanism∈{slip_joint, tongue_and_groove} 解析；fixed_rivet 下惰性（不暴露、不影响拓扑）| §Multiplicity |

连续 scale 默认独立采样 → conditional（groove_count / slide_travel_scale 仅 slip 机构解析）→ inequality 把 pivot/PRISMATIC origin 钉真实几何、把槽轨跨度投影回 shank。全部在 `resolve_config` 内求解。**palette_style 只换 4 个 material rgba，绝不进 slot_choice / 不改拓扑。**

## Multiplicity / Copy Logic

pliers 含 **1 根 conditional multiplicity 轴**（slip 机构下的调宽槽 / detent 数），单独声明：

- `count_param`: **`groove_count`**（channel-lock / slip-joint 下颚柄沿 shank 的调宽槽 / detent 数）
- `N_range`: `[2, 7]`（产品域；已覆盖真实源：slip_joint `GROOVE_COUNT=2`、tongue_and_groove `GROOVE_COUNT=5`；source map 建议过的 [3,9] 上界保守收到 7，因 N=3/N=7 的独立 record 在 records-root **缺失**——见 §排除；本轴的真实源是两个 parent 的 `for i in range(GROOVE_COUNT)` **循环范式**本身，可参数化到 [2,7]，上界由"槽轨须落 shank 真实长度内"的 inequality 守门）。**fixed_rivet 下不暴露**（N 无几何意义）。
- sampling domain（权重档）：小 N 偏多（5 最常见 channel-lock 档位，3-4 次之，2 / 6-7 稀疏）；仅当 pivot_mechanism∈{slip_joint, tongue_and_groove} 时进入采样，否则跳过。
- copied object: 单只调宽槽 / detent visual `groove_{i}`——channel-lock 用共享 `_groove_step_solid()`（等距凹槽轨），slip_joint 用共享 `_groove_solid(i)`（slot 两侧 detent）；N 个 visual 复用同一 helper。
- naming: `groove_{i}` / `for i in range(n)`（V5/V6 已用此结构，直接作 module 源码）。
- placement: 沿 shank `-X` 等距——channel-lock `GROOVE_X_START + i·GROOVE_SPACING`；PRISMATIC 行程随 N 派生 = `GROOVE_SPACING·(N-1)`，slot/轨长随 N 扩展并受 shank 长度 inequality 守门。
- joint policy: groove 不引入额外关节（同 half_0/lower part 内固定 visual）；唯一与 N 相关的是 PRISMATIC 行程上限派生。两个真实活动关节仍是 PRISMATIC（slot_slide / groove_select）+ REVOLUTE（pivot / jaw_pivot）。
- source/gating: 循环范式 V6 L330-337 / V5 L388-393；N 仅在 slip 机构下采样（conditional gate）；上界 7 由 shank 长度 inequality 守门，不外推到无源造型。

## 拓扑多样性审计

总组合数（离散槽，先不含 groove multiplicity）：jaw_function(4) × handle_form(3) × pivot_mechanism(3) = **36**
叠加 conditional multiplicity：
- pivot_mechanism=fixed_rivet（1/3 的组合，无 groove 轴）：4×3×1 = **12** 拓扑等价类。
- pivot_mechanism∈{slip_joint, tongue_and_groove}（2 种）× groove_count∈[2,7]（6 个 N 值，不同 N → 不同 groove visual 计数 = 不同拓扑）：4(jaw) × 3(handle) × 2(slip 机构) × 6(N) = **144** 拓扑等价类。
合计 ≈ **156 distinct 拓扑等价类**（locking_vise_grip 再叠 toggle part/joint，已隐含在 jaw 维度，不重复计）。

理由：仅 fixed_rivet 分支的 12 个离散组合即 >10；叠 slip 机构 + groove_count 后 ~156，distinct 拓扑充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——先加权选 jaw_function / handle_form / pivot_mechanism（combination/straight/fixed 偏多），若 pivot_mechanism∈{slip_joint, tongue_and_groove} 再加权采 groove_count（小 N 偏多），采连续 scale，经 `resolve_config` 解析 conditional（groove_count / slide_travel_scale 仅 slip 机构）与 inequality（pivot/PRISMATIC origin 钉真实几何、槽轨跨 ≤ shank 长）。`seed=0` 不特殊。无需 regression overrides（若 sweep 暴露特定 seed 失败，再稀疏加显式 override 并注明）。
Topology target：1000-seed slot choice tuple distinct 目标 ≈156 上界（本类离散组合受样本词汇表 + groove N 域限）。若实测偏低，多因 fixed_rivet 分支无 N 乘子，可微调 slip 机构 / 大 N 权重。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：初版即含 `overall_len_scale` / `jaw_len_scale` / `grip_girth_scale` / `open_angle_scale` / `slide_travel_scale`（conditional@slip 机构）（§参数表），全部 clamp/conditional，受 captured-pin origin、shank 长、真实开度、grip 互穿约束，不改变拓扑、REVOLUTE/PRISMATIC 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：jaw_function→handle_form→pivot_mechanism→(groove_count if slip 机构)→scales→palette；加权（jaw 偏 combination、handle 偏 straight、pivot 偏 fixed_rivet、小 N 偏多）| slot_choices_for_seed 与 build choices 一致（含 `("groove_count", f"n{N}")` 仅 slip 机构）|
| compatibility matrix | (1) groove_count / slide_travel_scale **仅** pivot_mechanism∈{slip_joint, tongue_and_groove} 生效，fixed_rivet 下惰性。(2) pivot/PRISMATIC origin 恒钉 (0,0,0) hub/slot 真实几何；rivet shaft captured 配 broad allow_overlap。(3) 槽轨跨度随 N 受 shank 长 inequality 守门（N≤7）。(4) locking_vise_grip 的 toggle 子件正交于 Slot C（任一枢轴机构均可叠 toggle）；toggle pin 落把内真实几何。(5) jaw/handle 在两半镜像派生，闭合时两颚内面近触不互穿。| 无 floating / collision / captured-pin origin 漂移 / 槽轨出 shank / toggle 漂浮 / 颚不闭合 |
| controlled local variation | 5 个 clamped scale（overall_len / jaw_len / grip_girth / open_angle / slide_travel@slip），每 build 统一；slide_travel 为 conditional | 比例变化不破坏 captured-pin origin、shank/slot 接口、grip 间隙、joint range、类别身份 |
| regression overrides | none（首版纯 procedural）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 captured-pin overlap / PRISMATIC 行程 / 颚闭合失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A jaw_function | 4 | yes | yes | flush_cutter / combination_grip / needle_nose / locking_vise_grip（含 +toggle）|
| B handle_form | 3 | yes | yes | straight_dipped / looped_bow / cushioned_ergonomic |
| C pivot_mechanism | 3 | yes | yes | fixed_rivet(1 REVOLUTE) / slip_joint / tongue_and_groove（各 PRISMATIC+REVOLUTE 3-part 链）|
| (mult) groove_count | [2-7]，conditional@slip 机构 | — | — | 多重性轴，sliding 调宽档位，提供拓扑乘子（仅 slip 机构分支）|

## Validator

- slot_choices_for_seed returns implemented module names（jaw_function / handle_form / pivot_mechanism + groove_count count 仅 slip 机构）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：groove_count / slide_travel 仅 slip 机构解析；pivot/PRISMATIC origin 恒钉 hub/slot 几何；槽轨跨 ≤ shank 长；toggle 仅 locking_vise_grip
- optional regression overrides 初版为空（如加须稀疏 + 注明）
- controlled local scale params 全部 clamp，且不破坏 captured-pin origin / shank-slot 接口 / grip 间隙 / joint range / 类别身份
- cross-part scale dependencies（conditional / inequality）在 `resolve_config` 求解，不留到 builder 失败
- critical captured-pin overlap：rivet shaft captured 穿 half_1 lap（broad allow_overlap half_0/half_1 或 carriage/half_1，grandfathered，MatingContract 省略）
- key joints：主 `pivot`/`jaw_pivot` REVOLUTE axis (0,0,±1) range [0, OPEN_LIMIT≈30°]；slip 机构 `slot_slide`/`groove_select` PRISMATIC axis (1,0,0)；locking `toggle` REVOLUTE axis (0,0,1)
- 开合测试：opening 主 REVOLUTE 使两颚分离（moving jaw min_y 远离）、手柄张开（grip 外扩）；closing 使颚口相聚近触
- copied objects 遵循 `groove_{i}` 命名 + 沿 shank 等距 placement + PRISMATIC 行程随 N 派生
- rivet seam/boss/head、adjustment_screw 恒为 half_0/carriage inline visual（不建 FIXED 装饰 part；carriage/carrier 是真实滑动 part）
- palette_style 只换 material rgba，不进 slot_choice、不改拓扑

## Reject cases

- 把中央 pivot 做成 FIXED 或省略（钳子必须有两半相对开合的 REVOLUTE）。
- pivot/PRISMATIC origin 不落中央铆钉 / slot 真实几何（漂浮 >0.002 m），或缺两 hub half-lap + captured rivet shaft 的 broad allow_overlap → captured-pin overlap 判失败。
- 两颚不交叉于中线（闭合时两半颚 y 不异号 / 不近触），或开合不分离颚口（pivot pose 变化颚不动）。
- pivot_mechanism=slip_joint/tongue_and_groove 但缺 PRISMATIC 关节或缺独立 carriage/carrier 滑动 part（退化成 fixed_rivet）；或 fixed_rivet 仍暴露 groove_count / PRISMATIC（拓扑错配）。
- groove 用手写 2-3 个代替 `for i in range(N)` 循环 + 共享 helper（多重性退化）；或槽轨跨度出 shank 真实长度（N 越界无守门）。
- jaw_function=locking_vise_grip 但缺 toggle_link part 或缺第二 REVOLUTE `toggle`（locking 要求 over-center 第二活动子件）。
- handle_form=looped_bow 的 finger ring 未做成真实闭环 torus（实心块），或与 neck arm 脱开成孤岛。
- 颚口用 boxy 占位代替真实轮廓（needle 须 lofted 渐细 taper、combination 须 serration+recess+notch、locking 须弯 C 弧）。
- 连续 scale 把钳放到非真实尺度（如 overall_len_scale 越界使整钳 <0.10 或 >0.26 m），或 open_angle 超出真实开度 / PRISMATIC 行程超 slot 轨。
- config_from_seed 采到非法组合（如 fixed_rivet + groove_count>0，或 slip 机构 + 行程超轨）。
- 把 palette_style / 连续尺寸当新 candidate 塞进 slot（非结构差异）。

## 与相邻类别的边界

- 不该混入：**剪刀 / scissors**——两薄钢刃绕中央螺钉 shear + finger-loop 手柄，刃口相剪而非颚口夹合；本类是锻钢咬颚 + 铆钉枢轴 + 调宽机构（slip/channel-lock），且本仓库已有独立 `scissors` 模板，二者身份须区分（剪=切，钳=夹/咬；looped_bow 虽借 finger-ring 形，但仍是颚口钳头而非剪刃，不与 scissors 混）。
- 不该混入：**单刃刀具 / utility knife**（无第二半、无枢轴开合）。
- 不该混入：**扳手 / spanner / wrench**（固定开口无枢轴开合，或活络扳手是 PRISMATIC 调宽但无双臂剪式枢轴 + 无 finger 手柄张合）。
- 不该混入：**镊子 / tweezers**（无中央铆钉枢轴，弹性夹臂在尾部相连）。
- 不该混入：**订书机 / 打孔器**（压合 / 冲孔机构，不出双臂中央枢轴开合）。
- Other 大类内：区别于无中央铆钉双臂枢轴的其他手工具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工确认：(1) groove_count `N_range` 取保守 [2,7]（N=3/N=7 独立 record 缺失，唯一源是 slip `GROOVE_COUNT=2` / channel-lock `GROOVE_COUNT=5` 两 parent 的循环范式）还是按 source map 的 [3,9]；(2) groove_count 为 conditional@{slip_joint, tongue_and_groove}（fixed_rivet 下不暴露）是否符合多重性审计期望；(3) palette_style 5 档配色（steel_red_dipped / black_chrome / gunmetal_yellow / polished_blue / chrome_natural）取 4-6 目标，是否接受 5 档；(4) locking_vise_grip 的 toggle 第二 REVOLUTE 作为 Slot A 内可选子件（正交于 Slot C）建模是否接受；(5) 与 scissors 模板的身份边界（looped_bow finger-ring 借形但保持颚口钳头身份）是否清晰。模板尚未实现（SPEC_ONLY）。|

## 模板实现备注（可选）

- 共享 helper：`_jaw_mesh`（按 jaw_function 分 flush/combination/needle/locking 四路；统一接受 `s=±1` mirror 与 serration 子特征）、`_grip_mesh`（按 handle_form 分 straight/bow/cushioned；side-aware；bow 走 torus 路径）、`_hub_mesh`（按 pivot_mechanism 决定 plain / slotted）、`_groove_emit`（按 groove_count N + slip 机构类型生成 detent/凹槽轨循环）、`_toggle_mesh`（仅 locking_vise_grip）。
- 关键 captured-pin overlap：rivet shaft captured 穿 half_1 hub lap 需 **broad** `allow_overlap(half_0, half_1)`（fixed_rivet）或 `allow_overlap(pivot_carriage/pivot_carrier, half_1/upper)`（slip 机构）；两半 hub half-lap nest（参考 P2 L384-391 reason）。
- 主 `pivot` / `slot_slide` / `groove_select` / `toggle` joint 均 **省略 MatingContract**（captured-pin / 滑槽 grandfathered）；origin 落真实 hub/slot/pin 几何（≤0.002 m）。
- 派生与门控集中在 `resolve_config`：fixed_rivet⇒不暴露 groove_count/slide_travel；groove_count 仅 slip 机构、N∈[2,7]、PRISMATIC 行程 = GROOVE_SPACING·(N-1) 且槽轨 ≤ shank 长；overall/jaw/grip/open_angle clamp。
- 链拓扑由 pivot_mechanism 派生：fixed_rivet=2-part（half_0→half_1）；slip_joint / tongue_and_groove=3-part（half_0/lower→carriage/carrier→half_1/upper）。builder 须按所选机构选择 part/joint 装配路径。
- 开合测试：pose 主 REVOLUTE 到 upper 使 moving jaw min_y 远离 fixed jaw（分离）、手柄 max_y 外扩（张开）；slip 机构再 pose PRISMATIC 验证调位（参考 P2 run_tests L477-505 / V5 / V6）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P1 | A/B/C | flush_cutter / straight_dipped(紧凑) / fixed_rivet | rec_model-a-pair-of-compact-flush-cut-wire-snips-ele_..._e0ef2013 | `_half_blade` L184-188、`_soft_prism` L139-153、`_half_boss` L191-200、`_rivet` L203-214、`rivet_pivot` L306-314 | 紧凑剪刃 + 直浸塑柄 + 单 rivet REVOLUTE 基线 |
| P2 | A/B/C | combination_grip / straight_dipped(重型) / fixed_rivet | rec_model-heavy-duty-combination-lineman-pliers-abou_..._2d2cf55e | `_jaw_solid` L126-179、`_hub_solid` L182-185、`_shank_solid` L188-194、`_grip_solid` L201-207、`_inlay_solid` L210-216、rivet L266-295、`pivot` L300-308、allow_overlap L384-391 | 重型综合颚 + over-mold 柄 + 中央 REVOLUTE + captured rivet 基线（fork 主基底）|
| V1 | A | needle_nose | rec_variant-jaw-function-needle-nose-..._7b198890 | `_jaw_solid` L153-178、`NEEDLE_STATIONS` L130-139、`_jaw_section_wire` L142-150 | 长尖嘴 lofted 渐细颚 |
| V2 | A | locking_vise_grip | rec_variant-jaw-function-locking-vise-grip-..._1903a019 | `_jaw_solid` L146-226、`_toggle_link_solid` L265-313、`_adjustment_screw_solid` L316-352、`toggle` REVOLUTE L483-496 | 弯 C 锁定夹颚 + toggle 第二关节 + 调螺 |
| V3 | B | looped_bow | rec_variant-handle-form-looped-bow-..._dbc49fe3 | `_bow_arm` L203-212、`_bow_ring` L215-225（TorusGeometry）| 闭环指圈柄 |
| V4 | B | cushioned_ergonomic | rec_variant-handle-form-cushioned-ergonomic-..._11ae9efe | `_grip_solid` L214-247、加厚 `GRIP_SECTIONS` L59-80 | 厚软人体工学指槽柄 |
| V5 | C/mult | slip_joint / groove_count | rec_variant-pivot-mechanism-slip-joint-..._9df407d7 | `_hub_slotted_solid` L234-239、`_slot_cut_solid` L213-231、`pivot_carriage` L397-434、`slot_slide` PRISMATIC L441-454、`pivot` REVOLUTE L459-472、`_groove_solid`/`_groove_x` L254-285、循环 L388-393 | 滑销 3-part 链 + groove detent 多重性范式（N=2）|
| V6 | C/mult | tongue_and_groove / groove_count | rec_variant-pivot-mechanism-tongue-and-groove-..._90e7c88e | `_groove_step_solid` L250-256、`_tongue_solid` L258-261、`_carrier_link_solid` L280-287、`_button_solid` L263-277、`pivot_carrier` L340-359、`groove_select` PRISMATIC L395-406、`jaw_pivot` REVOLUTE L410-421、循环 L330-337 | channel-lock 调宽 3-part 链 + groove_count 主多重性源（N=5 + 等距 + 行程派生）|

## 排除 / 缺源说明

- **groove-count-3 / groove-count-7 record 缺失**：source map（§Multiplicity / 格子覆盖）列 `rec_variant-groove-count-3-...` 与 `rec_variant-groove-count-7-...` 作为 groove_count 的 N 样本，但二者**在本仓库 `data/records/` 中不存在**（`ls | grep groove-count` 仅命中 tongue_and_groove parent）。groove_count 多重性轴的真实来源因此收敛为 V5（`GROOVE_COUNT=2`）+ V6（`GROOVE_COUNT=5`）两 parent 自带的 `for i in range(GROOVE_COUNT)` 循环范式 + 共享 groove helper；N_range 据此保守取 [2,7]（覆盖两真实档 2/5，上界 7 由 shank 长 inequality 守门、不外推无源 N=9）。此为缺源收窄，非内容污染。
- **无内容污染排除**：8 个被采纳样本全部经全文读，均为真实"两片锻钢半钳绕中央铆钉枢轴交叉、颚口夹合 / 手柄张合"，无伪装成 pliers 的他类、无穿模 / joint 语义错误样本，无需排除任何已读样本。
