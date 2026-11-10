# Modular Spec — Wire stripper (`wire_stripper`)

## 元信息
| 项 | 值 |
|---|---|
| slug | `wire_stripper` |
| registry key | `Electrical_Wiring_Wire_stripper` |
| template path | `agent/templates/Electrical_Wiring_Wire_stripper.py` (KEY-named file, stem-named funcs) |
| test path (optional) | `tests/agent/test_wire_stripper_template.py` (skipped while batch-authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（③ mechanism_family 深分支 → 每族一个 2–4 part 的两臂+pivot 拓扑；custom-branch build，非 assemble() 链） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in category `wire_stripper` (2 origins + 5 fork variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读结论：本小类的 5★ 分两大**机构族 / ③ 主体形态家族**，part tree + joint 拓扑不同：

- **A 族（手动多档钳）**：`rec_a-…a2129614`（origin A）。tool 在 XY 平面（+X=鼻，Y=开合，Z=厚），pivot 在原点，两臂用 visual `Origin(rpy=±DELTA)` 反转成开口 rest pose。part = `fixed_arm`(root) + `moving_arm` + `lock_latch`；joint = `pivot_squeeze` REVOLUTE(+Z) + `latch_pivot` REVOLUTE。几何全部 CadQuery：jaw/notch 布尔切（`_poly_solid`/`_circle_solid`/`_cut_edge_circles`），grip = catmull-rom spline + fillet，半搭 lap pivot + captured pin。
- **B 族（自动自调）**：`rec_an-…e60caa10`（origin B）。tool 长轴 X（头 +X，手柄 -X），两片交叉钢板绕 chrome 中心钮转。part = `gripping_jaw_arm`(root) + `stripping_jaw_arm` + `wire_stop_slider`；joint = `arm_pivot` REVOLUTE(+Z) + `wire_stop_slide` PRISMATIC(+X)。几何 = `ExtrudeGeometry`/`BoxGeometry`/`Cylinder` + `tube_from_spline_points` 弹簧。
- Fork 证据：`fixed_hole_gauge`(A 骨架，jaw 换成钻孔 AWG 量规板+压板)、`crimp_die_station`(A，jaw 加压接模站)、`gauge_n6`(A，N=6 升序 notch)、`pistol_grip`(B，手柄换 pistol/palm)、`auto_clamp_jaw`(B，加真实第二夹持 REVOLUTE mimic DOF)。

## 核心身份

手持剥线钳：两根手柄臂绕一个 REVOLUTE pivot 挤压 + 一个剥线 jaw 头。必须读成 **STRIPPER**（有升序 gauge notch/孔），不是通用 pliers。三大机构族（不同 joint 拓扑）是主轴。默认成熟域 = ~180–230 mm 手动/自动电工剥线钳。

**不该混入**：通用 pliers/lineman（无 gauge station，纯夹/剪）→ 见 §11；scissors/剪刀（两刃对剪，非剥线）；热剥/旋转剥线等 exotic（gate，非主流）。

## 槽位 + 候选模块表

### Slot A：mechanism_family（③ 主体形态家族 / Primary Form Family，主轴，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `manual_notch_plier` | forked_anchor | origin A `rec_a-…a2129614` | build L354-483 / jaw L202-217 / joints L457-481 | Planar Boundary Form（平面 blade 轮廓 + 布尔 notch/齿） | eligible | `fixed_arm`+`moving_arm`+`lock_latch`；2×REVOLUTE；CadQuery 布尔 jaw，成对 notch 半圆切 + 鼻锯齿 cutter，coil spring，thumb latch |
| `fixed_hole_gauge` | forked_anchor | `rec_wire_stripper_var_fixed_hole_gauge` | gauge plate L128-215 / AWG L67-75 | Planar Boundary Form（单块量规板 + 钻孔阵列） | eligible | A 骨架（同 part tree/2×REVOLUTE），jaw 头换成固定钻孔 AWG 量规板 + 平压板（无成对刃切） |
| `auto_selfadjust` | forked_anchor | origin B `rec_an-…e60caa10` | build L173-352 / plate L117-138 / joints L330-350 | Volumetric Envelope Form（交叉冲压钢板体量 + 滑块挡） | eligible | `gripping_jaw_arm`+`stripping_jaw_arm`+`wire_stop_slider`；1×REVOLUTE + 1×PRISMATIC（+可选 clamp DOF）；Extrude/Box/Cylinder jaw pads + brass 张力螺丝 + 红塑料长度挡滑块 |

三族 = 三个可识别主体形态原型（成对刃钳 / 钻孔量规板 / 自动交叉板），满足形态主导类 ≥3 ③ 原型。

### Slot B：handle_form（③/⑤ 手柄形态，family-gated）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `straight_plier` | forked_anchor | origin A | grip L166-266 | eligible（仅 A 族：manual/gauge） | 直钳手柄，yellow spline grip + black overmold + collar |
| `angled_offset` | forked_anchor | origin B | grip L141-149,239-260 | eligible（仅 auto 族） | 交叉板下略偏斜 red rubber grip + black inlay + tip cap（HANDLE_ANGLE=0.2405） |
| `pistol_grip` | forked_anchor + repaired adaptation | `rec_wire_stripper_var_pistol_grip`；对照母资产连续钢柄与现实自调剥线钳的人体工学双柄 | L46,240-314 | eligible（仅 auto 族） | 外张式弧度双柄（PISTOL_GRIP_ANGLE=0.34）+ 连续连接颈 + 同色 palm-swell + 小型尾帽；修正源 fork 中旋转符号反向、软胶柄与钢柄脱节的问题 |

| `offset_kick_plier` | **extrapolated**（无独立源 record） | 电工钳常见外折手柄；见 SourceMap §外推候选 | `_a_kick` L~440 | eligible（仅 A 族） | 手柄根 x=-46 起加外折 ramp，钢柄轮廓、黄黑分界线与外形同步折，机构（spring/latch 锚点）不变 |
| `inline_slim` | **extrapolated**（无独立源 record） | 紧凑型自动剥线钳 | `_B_HANDLE_SPINES` | eligible（仅 auto 族） | 头后扇开后近乎平行的细长双柄，柄更长更薄 |

handle_form 跨 sweep 实现 5 个 distinct（straight/offset_kick 来自 A 族 seed，angled/pistol/inline 来自 auto 族 seed）。

**2026-08-01 结构修正**：auto 族的钢柄与包胶改为共用 `_B_HANDLE_SPINES` 脊线（plate 边线 = 脊线 ± half_width，
grip slab 逐段落在同一脊线上）。此前包胶用独立 rake 常量摆放，相对钢柄中线外偏 8.3mm、角度差 0.5°–5.4°，
每条手柄读成"裸钢板 + 悬空胶柄"。脊线首段为头后"扇开"段——真实交叉杆剥线钳确有此形态，
同时它替代原来的外偏为两条包胶提供净空（作者测试 `GRIP_ROOT_CLEARANCE` 守住）。

### Slot C：jaw_feature（③ jaw 头细节，family-gated）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `notch_cutter` | forked_anchor | origin A | jaw L202-217 / NOTCH L65 / CRIMP L67 | eligible（manual 族） | 升序 V/圆 notch 布尔切 + 鼻锯齿 cutter + pivot 侧 crimp 扇贝 |
| `notch_crimp_die` | forked_anchor | `rec_wire_stripper_var_crimp_die_station` | crimp block L220-252 / L68 | eligible（manual 族） | 同 notch_cutter 再加一个独立凹形 crimp-die 站（成对凹模块 proud pad） |
| `gauge_hole_plate` | forked_anchor | `rec_wire_stripper_var_fixed_hole_gauge` | L128-215,67-75 | eligible（gauge 族） | 钻孔 AWG 量规板（升序孔径）+ 平压板；无成对刃切 |
| `clamp_screw` | forked_anchor | origin B | jaw L195-283 | eligible（auto 族） | 夹持 jaw + 剥线 jaw 块 + 钢齿垫 + brass 张力调节螺丝 |

| `notch_bolt_shear` | **extrapolated**（无独立源 record） | Klein/Ideal 类螺栓剪断 station | `_a_build_shear_rail` / `BOLT_SHEAR_SPECS` | eligible（manual 族） | pivot 侧 3 个升序螺纹剪孔 + 凸起 shear rail；notch 站外移到 x0=28 让位 |
| `gauge_slot_plate` | **extrapolated**（无独立源 record） | 开口槽式量规板 | `_a_cut_gauge_stations(slotted=True)` | eligible（gauge 族） | 量规孔从工作边开喉口（keyhole 槽），导线可侧向放入而非穿孔 |
| `clamp_vgroove_die` | **extrapolated**（无独立源 record） | 可换模盒式自调剥线钳 | `_b_die_pad_mesh(square=True)` | eligible（auto 族） | 模口由 V 形改方肩阶梯，模盒凸出 2.5mm 并由 2 颗盖头螺钉固定 |

jaw_feature 跨 sweep 实现 7 个 distinct。

**2026-08-01 结构修正**：auto 族 jaw 此前是两个光板 `BoxGeometry` + 平垫，没有任何剥线口，
整机渲染读不出 STRIPPER 身份。现在 jaw pad 的对合边带 N 档升序模口（真实去料，作者测试比对
`die_removed_volume`/`die_expected_volume`）。gauge 孔半径由 0.34–1.28mm（裸铜导体尺寸，
在 200mm 工具上是不可见针孔）改为 0.85–2.55mm（过绝缘线径）。

### Slot D：auto_clamp_dof（② 关节类型轴，仅 auto 族，family-gated，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `abstracted` | forked_anchor | origin B | body L186-237（jaw 为 body 内 visual，无独立 DOF） | eligible（auto 族） | “自调”抽象化：夹持 jaw 是 body 上的 visual，只有 1 REVOLUTE + 1 PRISMATIC |
| `real_clamp_joint` | forked_anchor | `rec_wire_stripper_var_auto_clamp_jaw` | gripping_jaw part L250-283 / clamp_pinch L378-395 / CLAMP_ANGLE L45 | eligible（auto 族） | 加真实第二夹持 DOF：`gripping_jaw` 成独立 part，`clamp_pinch` REVOLUTE(mimic arm_pivot) |

### Slot E：gauge_station_N（① multiplicity 轴，manual/gauge 族，family-gated，登记进 slot_choices）

见 §8。manual：N notch ∈ {3,4,5,6,7,8}；gauge：N hole ∈ {3,4,5,6,7}；保持升序半径不变量。

## 槽位图（slot graph）

pattern: `mixed`（deep ③ family branch；每族两臂 + pivot 的 2–4 part 拓扑，非跨 slot mating 链）

```
mechanism_family = manual_notch_plier / fixed_hole_gauge  (A 骨架)
    fixed_arm(root) --[pivot_squeeze REVOLUTE, axis +Z, origin(0,0,0) 半搭 boss/captured pin, 0..Q_CLOSE]--> moving_arm
    moving_arm     --[latch_pivot REVOLUTE, axis -Z, origin 在 moving 手柄面, 0..0.45]--> lock_latch
    jaw_feature ∈ {notch_cutter, notch_crimp_die}(manual) / {gauge_hole_plate}(gauge)
    handle_form = straight_plier ; gauge_station_N = N notch/hole (升序)

mechanism_family = auto_selfadjust  (B 骨架)
    gripping_jaw_arm(root) --[arm_pivot REVOLUTE, axis +Z, origin(0,0,0) chrome 中心钮, 0..SQUEEZE_MAX]--> stripping_jaw_arm
    gripping_jaw_arm       --[wire_stop_slide PRISMATIC, axis +X, origin 在 rail, 0..SLIDE_MAX]--> wire_stop_slider
    (real_clamp_joint) gripping_jaw_arm --[clamp_pinch REVOLUTE mimic arm_pivot, axis -Z, origin 在 riser]--> gripping_jaw
    jaw_feature = clamp_screw ; handle_form ∈ {angled_offset, pistol_grip} ; auto_clamp_dof ∈ {abstracted, real_clamp_joint}
```

- 接口点位：pivot = 原点半搭 boss + captured pin（omit MatingContract，grandfathered 的 captured-pin 几何，靠 flat 0.015 articulation-origin baseline + element-scoped allow_overlap）。latch/clamp/slider 各锚在真实父面（moving 手柄面 / riser / rail）。
- 互斥/gating：straight↔A 族，angled/pistol↔auto 族；jaw_feature 与 family 绑定；auto_clamp_dof 仅 auto；gauge_station_N 仅 A 族。见 §9 compatibility matrix。

## 每槽位 Module Emits / Interfaces

### Slot A / manual_notch_plier（A 骨架）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_arm`(root), `moving_arm`, `lock_latch` | A / L367-461 |
| internal joints | `pivot_squeeze` REVOLUTE axis(0,0,1) 0..Q_CLOSE；`latch_pivot` REVOLUTE axis(0,0,-1) 0..0.45 | A / L457-481 |
| root anchor | 原点半搭 boss disc(R=12mm)+captured pin；两臂 lap 在原点对称 | A / L219-237,284-291 |
| latch anchor | origin 在 moving 手柄面（rot2 的 (-31,5.5)），latch body seats on shank | A / L469-481 |

### Slot A / fixed_hole_gauge（A 骨架，jaw 换钻孔板）
| emits | 描述 | 来源 |
|---|---|---|
| parts / joints | 同 A 骨架（fixed_arm+moving_arm+lock_latch，2×REVOLUTE） | gauge fork / L367-468 |
| jaw | fixed_arm 头 = 钻孔 AWG 量规板（升序）；moving 头 = 平压板 | gauge fork / L190-215 |

### Slot A / auto_selfadjust（B 骨架）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gripping_jaw_arm`(root), `stripping_jaw_arm`, `wire_stop_slider`, (opt)`gripping_jaw` | B / L186-352 ; auto_clamp L256 |
| internal joints | `arm_pivot` REVOLUTE axis(0,0,1) 0..SQUEEZE_MAX；`wire_stop_slide` PRISMATIC axis(1,0,0) 0..SLIDE_MAX；(opt)`clamp_pinch` REVOLUTE axis(0,0,-1) mimic arm_pivot | B / L330-350 ; auto_clamp L378-395 |
| root anchor | 原点 chrome 中心钮（shaft+两 cap）；lever plate 交叉过 pivot | B / L211-233 |
| slider anchor | rail(在 body) origin(0.030,0.0105,0)；captured sliding fit | B / L214-216,342-350 |

不动细节（brass 张力螺丝、chrome rivet、grip inlay/tip、鼻齿、crimp 扇贝、pivot plate）均写成父 part 的 `parent.visual(...)`，不作独立 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| mechanism_family | enum | {manual_notch_plier, fixed_hole_gauge, auto_selfadjust} | manual_notch_plier | choice | weighted rng（见 §9） | Slot A |
| handle_form | enum | {straight_plier, angled_offset, pistol_grip} | straight_plier | conditional | A 族→straight；auto→{angled,pistol} | Slot B |
| jaw_feature | enum | {notch_cutter, notch_crimp_die, gauge_hole_plate, clamp_screw} | notch_cutter | conditional | 由 family 决定合法集 | Slot C |
| auto_clamp_dof | enum | {abstracted, real_clamp_joint} | abstracted | conditional | 仅 auto 族 | Slot D |
| gauge_count | int | manual {3,4,5,6,7,8} / gauge {3,4,5,6,7} | 4 | conditional | 仅 A 族；升序半径不变量 | Slot E / A L65 |
| palette_style | enum | {yellow_black, red_black, gunmetal, blue_black, safety_orange} | yellow_black | choice | rng.choice；解析成 mats 全套 | §8.5⑥ |
| open_angle_scale | float | [0.90, 1.10] | 1.0 | independent | manual DELTA=0.19·s clamp[0.16,0.215]；auto SQUEEZE=0.10·s clamp[0.09,0.11] | A L48 / B L43 |
| overall_scale | float | [0.92, 1.08] | 1.0 | conditional | A 族：均匀 mm 缩放（MM·s，所有坐标等比→clearance 不变）；auto 族固定 1.0 | A L43 |
| (—) | constraint | — | — | inequality | manual/gauge：Q_CLOSE=2·DELTA−0.02 保持“闭合差一线”；spring 线圈长 ∝ DELTA 以随开口缩放 | A L49,299-324 |
| (—) | constraint | — | — | equation | auto real_clamp：clamp mimic multiplier = CLAMP_ANGLE/SQUEEZE_MAX（随 SQUEEZE 变） | auto_clamp L390-394 |

连续尺寸采样契约：先采 independent（open_angle_scale）→ 派生（Q_CLOSE、spring 长、clamp multiplier）→ conditional（overall_scale 按 family 解析：auto 强制 1.0）。所有 clamp/派生在 `resolve_config` 完成。

## 7.5 编译预算 / compile budget
自报预算：**≤18s/seed**。依据：A 族是重 CadQuery 布尔雕刻（jaw 多 notch 切 + blade/nose face + 半搭 lap union + grip spline+fillet + latch），属库内“重布尔雕刻”档但 origin 记录本身可编译，实测应在 12-18s；auto 族轻（Box/Extrude/Cylinder + 1 tube），~5-8s。分档 tessellation：CadQuery `tolerance=0.00015, angular_tolerance=0.25`（沿用 origin，未加细）；spring/pin 圆柱 radial_segments ≤40；N 个 notch/hole 复用同一 `_circle_solid` helper（loop，不复制块）。sweep `--compile-timeout 120`（3× 预算，watchdog）。若超预算先粗化 tessellation 再迭代。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：gauge_station_N**，2026-08-01 起覆盖全部三族（manual notch {3..8}、
gauge hole {3..7}、auto stripping die {3..6}）。auto 族此前无 gauge station、N 记 0，是把
"自动剥线钳没有分档"当成了事实——实物是有升序模口的，属源资产简化，现已补回。

- `count_param` = `gauge_count`；`N_range`（产品域）：manual notch {3..8}，gauge hole {3..7}（源 origin A=4，gauge fork=7，gauge_n6 fork=6）。sampling domain（权重档）：小 N 高频、大 N 稀有 —— manual weights[3,4,5,6,7,8]=[3,5,4,3,1,1]；gauge weights[3,4,5,6,7]=[3,4,4,2,1]。
- copied object：manual = 成对半圆 notch 布尔切（`_cut_edge_circles` 双刃 loop）；gauge = 钻孔（`_circle_solid` loop）。naming：notch/hole 由 `NOTCH_SPECS`/`AWG_HOLE_SPECS` 生成（升序半径），`gauge_n{N}` 编进 slot_choices。placement：沿 y=0 刃线（manual）/板中宽（gauge）等 x 间距升序半径。joint policy：无（布尔切，不加 part/joint）。gating：升序半径不变量（`resolve` 断言 r[i]<r[i+1]）；N 由 family 决定域。
- 其它循环子件（非 multiplicity 轴，固定/派生数）：鼻齿 ×8、latch rib ×3、auto shank 齿 ×5、slider skirt ×2、crimp 扇贝 —— 均用 `for i in range(n)` + 共享 helper，**不复制块**（source origin B `head_rivet_0/1` 复制粘贴 → 模板改 loop）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | A 骨架（fixed_arm+moving_arm+lock_latch，2 REVOLUTE）vs B 骨架（gripping_jaw_arm+stripping_jaw_arm+wire_stop_slider，REVOLUTE+PRISMATIC）；forked_anchor（origin A / origin B） |
| └ multiplicity | 同构件 ×N | 有 | gauge_station_N（见 §8）：manual notch {3-8}，gauge hole {3-7}，权重小 N 高频 |
| ② 关节类型 | 图不变换 type/轴 | 有 | auto_clamp_dof：abstracted（无第二 DOF）vs real_clamp_joint（+`clamp_pinch` REVOLUTE mimic）；forked_anchor `auto_clamp_jaw`。B 族 REVOLUTE+PRISMATIC vs A 族 2×REVOLUTE 也是 ② 差异。声明的每种都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | mechanism_family 3 原型：manual_notch_plier(Planar Boundary)/fixed_hole_gauge(Planar Boundary，钻孔板)/auto_selfadjust(Volumetric Envelope，交叉板 + 连接 pivot/jaw/arm 的外侧冲压 cheek)；全 forked_anchor；登记进 slot_choices |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | jaw_feature 细节（notch_cutter 鼻锯齿+crimp 扇贝 / notch_crimp_die 加凹模站 / gauge 钻孔阵 / clamp brass 螺丝）+ shank 齿/rivet/grip inlay。record_only；均写成宿主 part visual，随 ③⑤ 共形（notch 由刃线 y=0 派生，随 N/scale 变） |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | open_angle_scale[0.90,1.10]、overall_scale[0.92,1.08]（A 族均匀）。运动包络：`pivot_squeeze`/`arm_pivot` REVOLUTE +Z [0, Q_CLOSE≈0.36 / SQUEEZE≈0.10]（闭合方向 = jaw 合拢）；`latch_pivot` REVOLUTE [0,0.45]；`wire_stop_slide` PRISMATIC +X [0,0.008]；`clamp_pinch` REVOLUTE mimic [0,0.04]。motion_test_plan：每族 targeted `ctx.pose(...)` 覆盖 rest-open + squeezed-closed（jaw 合而不撞），slider extended，latch flipped，clamp swung；captured pin/spring/latch/slider seat 用 element-scoped `allow_overlap`；compiler harness_motion_qc 跑 sampled poses（无 broad exemption） |
| ⑥ 涂装 | 只改材质/颜色 | 有 | palette_style ≥5：yellow_black(源A)/red_black(源B)/gunmetal(源图声明)/blue_black(电工蓝，外推)/safety_orange(外推)。材质大类覆盖 metal(steel/chrome/brass)+plastic/rubber(grip/slider)+painted(overmold) ≥ ceil(0.5×5)=3。每 `.visual(material=mats[...])` 由 palette_style 派生 |

收尾自检：batch 0-9 seed 里三族拉得开、五种配色都出现、notch/hole/crimp 贴刃线不悬空、squeeze 全程 jaw 合而不穿模、latch/slider/clamp 各自可动。

## 拓扑多样性审计

总组合数（离散）：
- manual：handle(2) × jaw{notch_cutter,notch_crimp_die,notch_bolt_shear}(3) × N{3..8}(6) = 36
- gauge：handle(2) × jaw{gauge_hole_plate,gauge_slot_plate}(2) × N{3..7}(5) = 20
- auto：handle{angled,pistol,inline}(3) × jaw{clamp_screw,clamp_vgroove_die}(2) × dof(2) × N{3..6}(4) = 48
- **core_domain = 22**（非 N 结构槽位笛卡尔积：manual 6 + gauge 4 + auto 12）
- **raw_domain = 104**（含 N）。3000-seed 实测 distinct core = 22、distinct raw = 104，全部可达。
- palette(5) 与连续 scale 按口径不计入 core/raw。

**覆盖说明（legacy 限制）**：本模板无 `TEMPLATE_DOMAIN`，sweep 的 `candidate_coverage` 与
`diversity` 均为 not_applicable，legacy corner 的 `max_corner_seeds=12` 只能补 12 个组合
（报告：reachable 96 / realized_by_base 30 / unrealized 66 / uncovered_tokens 55）。
因此 2026-08-01 另做了一次穷尽验证：按 slot tuple 取 104 个代表 seed 全量 `gen-seeds`
（full compile + motion QC），结果记在下方审核记录。


seed_domain_policy：procedural_first（`config_from_seed` 全 rng 加权采样，seed=0 不特殊）。
Procedural Sampling / Sweep Plan：先采 mechanism_family（weights[4,2,3]）→ 按 family 解析合法 handle/jaw/dof/N → 采 palette_style + 连续 scale。compatibility gating 在 `config_from_seed`+`resolve_config` 双重强制（非法组合 coerce 到合法）。少量 regression override：无。random sweep 0-35（初判）→ corner；viewer 目检 batch 0-9。
Controlled local parameterization：open_angle_scale（两族）、overall_scale（A 族均匀 mm 缩放）、gauge_count（N multiplicity）。全在 `resolve_config` clamp/派生，不破坏 pivot/captured-pin/mating/multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | family-first weighted，再 family-gated 子槽 + palette + scale | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | straight↔A / angled·pistol↔auto；jaw↔family；dof 仅 auto；N 仅 A；非法 coerce | 无 floating/collision/axis/max-N/optional-child 失败 |
| controlled local variation | open_angle_scale, overall_scale(A 均匀), gauge_count clamp | 比例变而不破 pivot/captured pin/spring reach/jaw close |
| regression overrides | none | — |
| random sweep | 0-35 初判，0-999 成熟审计 | contract failures；axis_realization / |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| mechanism_family | 3 | yes | yes | ③ 主体形态家族 |
| handle_form | 3 | yes | yes | family-gated |
| jaw_feature | 4 | yes | yes | family-gated |
| auto_clamp_dof | 2 | yes | no | ② 轴，仅 auto，源池仅 2 |
| gauge_station_N | 6/5 | yes | yes | multiplicity（覆盖不计 distinct） |

## Validator

- slot_choices_for_seed returns implemented module names（family + handle + jaw [+ dof / gauge_n{N}]）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility gating prevents illegal combos（straight↔A、angled/pistol↔auto、jaw↔family、dof/N family-gated）
- open_angle_scale / overall_scale clamped，captured-pin/mating/multiplicity 不破
- gauge_count 升序半径不变量（resolve 断言）
- 关键 joint type/axis/range：pivot REVOLUTE +Z 0..Q_CLOSE/SQUEEZE；latch REVOLUTE；wire_stop_slide PRISMATIC +X；clamp_pinch REVOLUTE mimic
- 复制子件（notch/hole/齿/rivet/skirt）走 loop + 共享 helper + name_{i}
- palette_style 驱动全部 material；≥5 配色

## Reject cases

- 把 jaw/grip 降级成裸 Box/Cylinder（违 Rule 3；A 必须 CadQuery 布尔，B 必须 Extrude/spline grip）
- straight grip 配 auto 骨架 / angled·pistol 配 A 骨架（非法组合未 coerce）
- gauge notch/hole 非升序半径（丢 stripper 身份不变量）
- notch/hole 悬空（未由刃线/板面派生，随 N/scale 脱离）
- captured pin / spring / latch / slider seat 未声明 element-scoped allow_overlap → closed/sampled pose 穿模误报
- open_angle 过大 → 闭合时 jaw 撞穿 或 spring 够不到 moving 手柄；过小 → jaw 不分离
- latch/clamp/slider origin 离几何 >15mm（未锚在真实父面）
- palette_style 只在 variant pool 变、swept 输出单色（未逐 visual 驱动）
- auto 族包胶手柄用独立 rake/offset 常量摆放，与 `_B_HANDLE_SPINES` 钢柄脱节（2026-08-01 回归项）
- auto 族 jaw 退化成无模口的光板（丢 STRIPPER 身份不变量）
- 头部两片半板中间留全长通缝（应只在 jaw 窗口开口）
- 量规孔/模口小到整机渲染不可见（N 轴名义存在、视觉上不可分辨）

## 与相邻类别的边界

- 不该混入 **Other/pliers（通用钳）**：pliers 无 gauge station（升序 notch/孔）；wire_stripper 必须能量规剥线。共享两臂+rivet 骨架但 jaw 语义不同。
- 不该混入 **Stationary/Scissors（剪刀）**：剪刀两刃对剪切断，wire_stripper jaw 是 strip/clamp 不剪断导线本体。
- 不该混入 **热剥/旋转剥线 exotic 形态**：非类目主流（源图排除项，gate）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | mechanically re-certified 2026-08-01 |
| reviewer notes | 形态主导，③ mechanism_family 3 族深分支（joint 拓扑不同）；custom-branch build 复用 pliers 模板 idiom（captured-pin allow_overlap + slot_choices_for_config + model.meta）。GATE P4 以 sweep verdict=pass 为准。 |
| 2026-08-01 verdict | random-16 16/16 · random-36 36/36 · corner 12/12 · joint_motion_coverage pass · completion_status `legacy_compatible` |
| 2026-08-01 穷尽验证 | 104 个 raw 组合代表 seed 全量 gen-seeds（full compile + motion QC） |

## 模板实现备注

- 共享 helper：A 族 `_poly_solid/_circle_solid/_cut_edge_circles/_mirror/_rot2/_grip_pair/_build_spring/_build_latch`（port origin A）；auto 族 `_plate_mesh/_grip_slab/_spring_mesh`（port origin B）。
- captured-pin：pivot（两族）omit MatingContract，element-scoped `allow_overlap`(pin↔lap / 交叉板 hub)；spring↔handle、latch↔shank、slider↔rail、clamp↔riser 各 element-scoped allow_overlap（port 自各 source run_tests）。
- notch/crimp 布尔去除体积存 `model.meta`（uncut−cut）供 run_tests 断言“真实去料”（不用模块 global）。
- 统一 part 名：root=`fixed_arm`（auto 的 body 也叫 fixed_arm），moving=`moving_arm`（auto 的 lever），auto 另有 `wire_stop_slider`(+`gripping_jaw`)，A 另有 `lock_latch` —— run_tests 按 family 分支。
