# Metronome Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `metronome` |
| template path | `agent/templates/metronome.py` |
| test path (optional) | `tests/agent/test_metronome_template.py` — 可选回归网，默认被 pytest 排除；验收以 compile-sweep 为准 |
| stage | `APPROVED` |
| status | `APPROVED` |
| __modular__ | `True` |
| pattern | `mixed`（身份链 housing→pendulum→sliding_weight 的串联移动副 + winding_key/可选 door/lid/legs 并列 children + 可选 stabilizer-leg multiplicity） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 23 |
| read_count | 8 |
| read_scope | 23 个 5 星全部用 grep 抽取了 `model.part(...)` 列表、每个 `model.articulation` 的 (name,type,parent,child,axis,motion_limits)、所用几何 primitive(LatheGeometry / MeshGeometry / ExtrudeGeometry / section_loft / cadquery / Box+Cylinder+Sphere)、bbox 量级；其中 8 个(0307c136, 2b18c190, 1136c31b, 448b77a5, c8917520, 7af0c6f9, 0d660052, cd4513ba) 按行精读以采纳可复用源码块，覆盖全部结构家族(squat-pyramid / floor-cabinet / box、cadquery-loft / lathe-collar / mesh-panel、door / lid / base / stand / legs / dual-weight / escapement) |
| samples_adopted_as_module_sources | 8 |
| samples_read_but_not_adopted | 15（grep 扫描确认结构落在已采纳家族内，未单独索引源码） |

全部 23 个 5 星样本（每个均确认含 housing/body + pendulum(REVOLUTE) + sliding weight(PRISMATIC) + winding key(CONTINUOUS) 四元身份）：

- `rec_metronome_0307c136631e4c3985c7ca01132b9498` — **adopted S1**：cadquery loft 方锥壳 + tempo-window + 圆柱滑动 weight collar，4 part 经典骨架
- `rec_metronome_2b18c190d98b490db338a754b5d518c1` — **adopted S2**：tall floor `cabinet`(开口前门框 + 内部 bearing pedestal) + 1.5m 长 rod + LatheGeometry，4 part
- `rec_metronome_1136c31bf4ac4edba8787e67c28a84fd` — **adopted S3**：MeshGeometry 方锥壳 + `mechanism`(FIXED 内部擒纵) + `front_door`(REVOLUTE 下翻) + cheek-clamp weight，6 part 最全 gated
- `rec_metronome_448b77a5f25242a1841130ccfe8c971f` — **adopted S4**：primitive box 壳 + `dial_face`(FIXED) + 顶 `lid`(REVOLUTE 上翻) + key 挂 lid(CONTINUOUS)，6 part
- `rec_metronome_c8917520bd114977a46b060942212ee6` — **adopted S5**：section_loft 方锥壳 + LatheGeometry shell-collar 的 `coarse_weight`+`fine_weight` 双滑块(2 PRISMATIC)，5 part
- `rec_metronome_7af0c6f94b6b49979b3ff9b13d356329` — **adopted S6**：section_loft 壳 + 一对 fold-out `*_stabilizer_leg`(2 REVOLUTE) + superellipse extrude weight，6 part
- `rec_metronome_0d660052566e46b38c71c1b8bc5472ad` — **adopted S7**：独立 `base` part(FIXED `base_to_housing`) + MeshGeometry tapered 壳 + tube weight，5 part
- `rec_metronome_cd4513ba91c14bce998655f65dec12d6` — **adopted S8**：Loft 壳 + glass `front_panel`(REVOLUTE) + 独立 `escapement_gear`(FIXED) + Loft 几何，6 part
- `rec_metronome_0a0008f3f10c46a297b50b0f9e4cc336` — read，cadquery 4-part(housing/pendulum/weight/winding_key)，落在 S1 cadquery 家族
- `rec_metronome_31c18f362a074af1be5b897a0141589e` — read，MeshGeometry 壳 + `for leg_index ...: rear_leg_{i}`(REVOLUTE multiplicity 2)，落在 S6 leg 家族
- `rec_metronome_4ab9dfa5b09747ce8513dc89cce915ef` — read，mesh+cadquery 4-part，落在 S1/S3 家族
- `rec_metronome_4d43405a38c54bfb954c3063081a49ca` — read，LatheGeometry `frame` 4-part，落在 S2 lathe 家族
- `rec_metronome_66607e13eefd416d9f8ed897a637f0a4` — read，cadquery 4-part，落在 S1 家族
- `rec_metronome_8fe709dba54e4435a3fc8ba0dc03ce56` — read，Lathe+Extrude 4-part，落在 S2 家族
- `rec_metronome_a5b4066b8d19425082c78f327b63f094` — read，Lathe 壳 + `clip_arm`(第二 REVOLUTE)，gated clip 件归入 Slot 6 cover/extras 家族变体（见说明）
- `rec_metronome_b31fa9775a064d5c888a4a600bdf75e7` — read，Lathe 壳 + 顶 `lid`(REVOLUTE)，落在 S4 lid 家族
- `rec_metronome_c0525071926946bd956e34cd3ff432b5` — read，ExtrudeGeometry `body` 4-part，落在 S3 mesh 家族
- `rec_metronome_c48c7edd47ad48169b3b861c31d88b18` — read，cadquery `frame` 4-part，落在 S1 家族
- `rec_metronome_dc4b2346ef504872ba24b4e0df84a56b` — read，mesh 4-part，落在 S3 家族
- `rec_metronome_dcecf1c712a24793a9fa1db9c57c4324` — read，primitive 4-part，落在 S4 box 家族
- `rec_metronome_dff9afffab354a8da469c2c09eb19d66` — read，primitive 壳 + `stand`(REVOLUTE 后撑架)，gated stand 件归入 Slot 6（见说明）
- `rec_metronome_e59c60108b7d4741a1e0318e981a2907` — read，cadquery 壳 + `crown_knob`(CONTINUOUS)，落在 S1 家族
- `rec_metronome_e7e6f42c2dd64fd18ac8646da87e2603` — read，mesh+cadquery `apex_pivot` 4-part，落在 S1/S3 家族

source_index_policy：只索引被采纳的可复用片段；squat-pyramid / floor-cabinet / box 三种壳视为同一 `housing_style` 离散开关而非三套模板；door / lid / glass-panel / stand / clip / dual-weight / escapement / 独立 base 一律视为 gated 可选件，不并入默认 4-part 主干(housing + pendulum + sliding_weight + winding_key)。

## 核心身份
机械节拍器(metronome)：一个落地的 housing/case(常为方锥/楔形壳，也有落地柜式或方盒式)，case 顶部前缘附近有一根**摆杆(pendulum rod)**经**单个 REVOLUTE** 绕水平轴(多为前后向 `±Y`)左右摆动；摆杆上套一个**配速滑块/bob(sliding tempo weight)**经**单个 PRISMATIC** 沿杆长方向(`±Z`)上下滑动以改变摆频；case 侧/后面板上还有一个**上弦钥匙/旋钮(winding key)**经 **CONTINUOUS** 绕自身轴旋转。这三件(摆 REVOLUTE + 滑块 PRISMATIC + 上弦 CONTINUOUS)是 23 个 5 星全部具备的恒定身份骨架。它不是单纯的摆钟/落地钟(metronome 摆杆短、靠可滑动 bob 调速、case 矮)，不是天平/指针仪表(无可滑配速块)，不是单铰链盖盒(可选的盖/门是附件而非主体)。

边界：
- 不包括没有可滑动 tempo weight 的纯单摆/钟摆（必须有沿杆 PRISMATIC 的 bob）。
- 不混入把摆做成 CONTINUOUS 连续旋转（摆必须是有限摆角的 REVOLUTE）。
- 不混入 coupled/mimic 机构（单摆 + 单滑块，绝不发明摆与滑块联动、或多摆共轴）。
- 可选的 door/lid/stand/legs/clip/dual-weight 只是 gated 附件，不得篡夺 metronome 四元身份。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_metronome_0307c136631e4c3985c7ca01132b9498` | `data/records/rec_metronome_0307c136631e4c3985c7ca01132b9498/revisions/rev_000001/model.py:L29-L98` | `_housing_shell`(cadquery `rect→loft→cut` 方锥壳 + tempo-window + top-slot)与 `_sliding_weight`(cadquery 圆柱 + clearance bore collar) helper |
| S2 | `rec_metronome_0307c136631e4c3985c7ca01132b9498` | `data/records/rec_metronome_0307c136631e4c3985c7ca01132b9498/revisions/rev_000001/model.py:L190-L282` | 经典 4-part 骨架：pendulum(rod_shaft+pivot_boss+pivot_pin+top_cap)、weight、key(collar+wings)，及 `pendulum_pivot`(REVOLUTE `(0,1,0)`)+`weight_slide`(PRISMATIC `(0,0,1)`)+`key_axle`(CONTINUOUS `(1,0,0)`) 关节写法 |
| S3 | `rec_metronome_2b18c190d98b490db338a754b5d518c1` | `data/records/rec_metronome_2b18c190d98b490db338a754b5d518c1/revisions/rev_000001/model.py:L44-L156` | 落地柜式 `cabinet`(plinth + floor + 四壁 box + roof + 前 opening 框 jamb/lintel/apron + 内部 left/right `bearing_pedestal` + side key_bushing)，开口前面板带摆杆露出 |
| S4 | `rec_metronome_2b18c190d98b490db338a754b5d518c1` | `data/records/rec_metronome_2b18c190d98b490db338a754b5d518c1/revisions/rev_000001/model.py:L158-L240` | 长 rod 摆(pivot_hub + arm + rod_collar + 1.5m pendulum_rod + sphere rod_tip) + box/cyl weight clamp + 长杆 key，落地钟量级 |
| S5 | `rec_metronome_1136c31bf4ac4edba8787e67c28a84fd` | `data/records/rec_metronome_1136c31bf4ac4edba8787e67c28a84fd/revisions/rev_000001/model.py:L57-L320` | `_panel_from_quad`/`_solid_from_loops` MeshGeometry 方锥壳 + 前门框 stile/lintel + cheek/pivot shaft + tempo scale strip |
| S6 | `rec_metronome_1136c31bf4ac4edba8787e67c28a84fd` | `data/records/rec_metronome_1136c31bf4ac4edba8787e67c28a84fd/revisions/rev_000001/model.py:L322-L441` | 独立 `mechanism` part(spring barrel/gears/escapement/anchor，FIXED `housing_to_mechanism`) + `front_door`(door_panel mesh + knob，REVOLUTE `(1,0,0)` 下翻) |
| S7 | `rec_metronome_1136c31bf4ac4edba8787e67c28a84fd` | `data/records/rec_metronome_1136c31bf4ac4edba8787e67c28a84fd/revisions/rev_000001/model.py:L443-L592` | cheek-clamp `slider_weight`(left/right cheek + front/back bridge + wedge body 抱住 rod) + rear `winding_key`(CONTINUOUS `(0,-1,0)`)，PRISMATIC `(0,0,-1)` |
| S8 | `rec_metronome_448b77a5f25242a1841130ccfe8c971f` | `data/records/rec_metronome_448b77a5f25242a1841130ccfe8c971f/revisions/rev_000001/model.py:L40-L139` | primitive Box 方盒壳 `body`(plinth + floor + 四壁 + front sill/header + 内 pendulum journal/pivot support + 顶后缘 hinge barrel) |
| S9 | `rec_metronome_448b77a5f25242a1841130ccfe8c971f` | `data/records/rec_metronome_448b77a5f25242a1841130ccfe8c971f/revisions/rev_000001/model.py:L141-L278` | `dial_face`(FIXED tempo board + standoff) + 顶 `lid`(panel+skirt+hinge barrel，REVOLUTE `(1,0,0)` 上翻) + key 挂 lid(CONTINUOUS `(0,0,-1)`) |
| S10 | `rec_metronome_c8917520bd114977a46b060942212ee6` | `data/records/rec_metronome_c8917520bd114977a46b060942212ee6/revisions/rev_000001/model.py:L25-L162` | `section_loft` 方锥 `body_shell` + `_collar_mesh`(LatheGeometry shell-profile 中空 collar) + 独立 `coarse_weight`/`fine_weight` 两 collar part |
| S11 | `rec_metronome_c8917520bd114977a46b060942212ee6` | `data/records/rec_metronome_c8917520bd114977a46b060942212ee6/revisions/rev_000001/model.py:L204-L245` | 双滑块 `pendulum_to_coarse_weight`+`pendulum_to_fine_weight`(两 PRISMATIC `(0,0,1)`，独立 lower/upper) 写法 |
| S12 | `rec_metronome_7af0c6f94b6b49979b3ff9b13d356329` | `data/records/rec_metronome_7af0c6f94b6b49979b3ff9b13d356329/revisions/rev_000001/model.py:L186-L316` | 一对 fold-out `*_stabilizer_leg`(hinge_barrel + leg_arm + rubber foot_pad，REVOLUTE `(0,0,±1)` 绕底角外摆) + superellipse `ExtrudeWithHolesGeometry` slider ring |
| S13 | `rec_metronome_31c18f362a074af1be5b897a0141589e` | `data/records/rec_metronome_31c18f362a074af1be5b897a0141589e/revisions/rev_000001/model.py:L232-L260` | leg multiplicity：`for leg_index,(x,direction,axis) in enumerate(...): model.part(f"rear_leg_{leg_index}")` + 同循环体内 `leg_hinge_{i}` REVOLUTE，证明 leg 可做 N 件 |
| S14 | `rec_metronome_0d660052566e46b38c71c1b8bc5472ad` | `data/records/rec_metronome_0d660052566e46b38c71c1b8bc5472ad/revisions/rev_000001/model.py:L77-L183` | 独立 `base` part(plinth + cap) + `_build_tapered_housing_shell` MeshGeometry tapered 壳 `housing`，`base_to_housing` FIXED |
| S15 | `rec_metronome_cd4513ba91c14bce998655f65dec12d6` | `data/records/rec_metronome_cd4513ba91c14bce998655f65dec12d6/revisions/rev_000001/model.py:L118-L195` | glass `front_panel`(hinge_barrel + 四 rail 框 + door_glass，REVOLUTE `(-1,0,0)`) + 独立 `escapement_gear`(gear_wheel + 16 tooth loop + bracket，FIXED) |

## 槽位 + 候选模块表

### Slot 1：housing（外壳 / case，root part）
节拍器的接地外壳，承载摆轴 pivot cheek、上弦 key boss、tempo scale。是 root part。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `squat_pyramid_shell` | S1 (0307c136) | `model.py:L29-L98,L115-L188` | eligible if compatible | cadquery `rect→loft→cut` 方锥/楔形中空壳 + 前 tempo-window 大圆角切口 + top-slot 摆杆出口，最经典节拍器外形 |
| `tapered_mesh_shell` | S5 (1136c31b) / S14 (0d66) | `1136…:L57-L320` / `0d66…:L28-L175` | eligible if compatible | MeshGeometry 四 `_panel_from_quad` / `_build_tapered_housing_shell` 上小下大梯形壳 + 前门框 stile/lintel + tempo scale strip |
| `box_case` | S8 (448b77a5) | `model.py:L40-L139` | eligible if compatible | primitive Box 拼方盒壳(plinth + floor + 四壁 + front sill/header)，内置 pendulum journal/pivot support，最轻量 |
| `floor_cabinet` | S3 (2b18c190) | `model.py:L44-L156` | eligible if compatible | 落地柜式高壳(plinth + floor + 四壁 + roof + 前 opening 框 + 内部 left/right bearing pedestal + side bushing)，配长摆杆，落地钟量级 |

### Slot 2：pendulum（摆杆，REVOLUTE child）
绕 housing 顶部前缘水平轴摆动的摆杆，必为单 REVOLUTE。结构必带 pivot barrel/boss + rod + 顶/底 tip。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rod_with_top_cap` | S2 (0307c136) | `model.py:L190-L214` | eligible if compatible | rod_shaft Cylinder + pivot_boss Sphere + 横向 pivot_pin + 顶 top_cap，杆顶露出壳外，bob 在杆上半段 |
| `rod_with_bob_tip` | S7 (1136c31b) | `model.py:L443-L472` | eligible if compatible | rod Cylinder + pivot_sleeve + 底 lower_counterweight + tempo_pointer，下端配重式(欧式机芯倒挂) |
| `long_cabinet_rod` | S4 (2b18c190) | `model.py:L158-L188` | eligible if compatible | pivot_hub Cylinder + 横 arm + rod_collar + 极长 rod(~1.5m) + sphere rod_tip，落地柜专用长摆 |
| `slim_rod_with_lower_bob` | S6 (7af0c6f9) | `model.py:L132-L161` | eligible if compatible | pivot_barrel + 极细方 rod + lower_bob + lower_tip Cylinder，便携小型摆 |

### Slot 3：sliding_weight（配速滑块 / bob，PRISMATIC child，强制第二 DOF）
套在摆杆上沿杆滑动调速的 tempo weight，恒为 PRISMATIC，是 23/23 全部具备的真实第二自由度。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cadquery_bore_collar` | S1 (0307c136) | `model.py:L84-L98,L216-L233` | eligible if compatible | cadquery 圆柱 + 真实 clearance bore 套在 rod 上 + index line + friction pad(声明 allow_overlap 压在 rod 上) |
| `cheek_clamp_weight` | S7 (1136c31b) | `model.py:L488-L538` | eligible if compatible | left/right cheek + front/back bridge + wedge body，从两侧抱住方 rod(适配方截面摆杆) |
| `lathe_shell_collar` | S10 (c8917520) | `model.py:L36-L45,L142-L162` | eligible if compatible | `_collar_mesh` LatheGeometry 中空环 collar(coaxial 套 rod)，可单件或 coarse+fine 双件(见 Slot 5 dual gate) |
| `extrude_ring_weight` | S12 (7af0c6f9) | `model.py:L163-L184` | eligible if compatible | `ExtrudeWithHolesGeometry` superellipse 外轮廓 + 内孔环 + 侧 grip，套圆 rod |

### Slot 4：winding_key（上弦钥匙 / 旋钮，CONTINUOUS child）
case 侧/后/顶面板上绕自身轴连续旋转的上弦件，恒为 CONTINUOUS。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `winged_side_key` | S2 (0307c136) | `model.py:L235-L254` | eligible if compatible | key_collar + 两 key_wing Box + 端 lobe，侧面板 `(±1,0,0)` 轴蝶形上弦钥匙 |
| `crossbar_rear_key` | S7 (1136c31b) | `model.py:L554-L592` | eligible if compatible | key_shaft + hub + stem + crossbar，后面板 `(0,-1,0)` 轴，靠 rear_key_boss seat |
| `stem_handle_key` | S4 (2b18c190) | `model.py:L204-L240` | eligible if compatible | escutcheon + 长 stem + boss + 横 bar + 两端 grip ball，侧面板长杆手柄式 |
| `top_face_knob` | S9 (448b77a5) | `model.py:L237-L278` | eligible if compatible | key_shaft + hub + arm + grip_knob，顶/盖面 `(0,0,-1)` 轴小旋钮(挂 lid 时随 Slot 6 而定) |

### Slot 5：weight_dof（滑块自由度个数 / multiplicity）
sliding weight 是 1 件还是 coarse+fine 2 件(各自独立 PRISMATIC)。决定 PRISMATIC 关节数与 part 数。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_weight` | S1 (0307c136) | `model.py:L216-L273` | eligible if compatible | 1 个 sliding_weight + 1 个 `weight_slide` PRISMATIC，默认主干 |
| `coarse_plus_fine` | S10+S11 (c8917520) | `model.py:L142-L162,L204-L232` | eligible if compatible | coarse_weight + fine_weight 两 collar part，`pendulum_to_coarse_weight`+`pendulum_to_fine_weight` 两 PRISMATIC，区间不重叠 |
| `weight_plus_index` | S7 (1136c31b) | `model.py:L488-L538` | eligible if compatible | 仍是 1 PRISMATIC 滑块，但 weight 含 index/pointer 细节随 tempo scale 读数(单 DOF，与 single_weight 同骨架的细节变体) |

说明：Slot 5 实质是「PRISMATIC 个数 ∈ {1,2}」的 multiplicity 开关。`weight_plus_index` 与 `single_weight` 都是单 PRISMATIC，仅 weight 细节不同；保留它是为了让 其他 procedural samples仍有一个单 DOF 候选承载 index/pointer 细节家族。`coarse_plus_fine` 是唯一引入第二 PRISMATIC 的候选——这是结构上明确不同的拓扑骨架(part +1、PRISMATIC joint +1)。三候选中 2 个共享单-DOF 骨架，故此槽有效结构骨架 = 2(单滑块 / 双滑块)，已注明。

### Slot 6：case_extras（外壳附件 / 可选 gated DOF）
挂在 housing 上的可选件：内部机芯/擒纵(FIXED)、前门或顶盖(REVOLUTE)、独立 base(FIXED)、后撑 stand(REVOLUTE)、fold-out stabilizer legs(REVOLUTE × N)、clip 臂(REVOLUTE)。决定附加 part/joint。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `plain_no_extra` | S1 (0307c136) | `model.py:L115-L188` | eligible if compatible | 仅 housing 自带 pivot cheek/bridge/bushing visual，无附加 part、无附加 DOF（默认主干，4 part） |
| `hinged_door` | S6 (1136c31b) / S9 (448b77a5) / S15 (cd45) | `1136…:L396-L441` / `448b…:L177-L235` / `cd45…:L118-L159,L301-L313` | eligible if compatible | 一个 `front_door`/`lid`/`front_panel` part 经第二 REVOLUTE 挂 housing(前缘下翻 `(±1,0,0)` 或顶后缘上翻 `(±1,0,0)`)，gated 二级 DOF |
| `internal_mechanism` | S6 (1136c31b) / S15 (cd45) | `1136…:L322-L394` / `cd45…:L161-L195,L315-L321` | eligible if compatible | 一个 `mechanism`/`escapement_gear` part(spring barrel/gears/escapement/anchor，FIXED `housing_to_*`)，机芯细节件，无附加 DOF |
| `separate_base` | S14 (0d66) | `model.py:L77-L183` | eligible if compatible | 独立 `base` part(plinth + cap) 经 FIXED `base_to_housing` 承托 housing，root 改为 base，case 抬高 |
| `fold_out_legs` | S12 (7af0c6f9) / S13 (31c1) | `7af0…:L186-L316` / `31c1…:L232-L260` | eligible if compatible | N 个 `*_stabilizer_leg`/`rear_leg_{i}`(hinge_barrel + leg_arm + foot_pad) 经 REVOLUTE `(0,0,±1)` 绕底角外摆，multiplicity 1..2 件，gated 折叠脚 DOF |

说明：`fold_out_legs` 同时是 gated 附件与 leg multiplicity(N=1..2，S13 用 `for leg_index` 循环)。`hinged_door` 合并了 front-door(下翻)、lid(上翻)、glass front_panel 三种同骨架(单 part + 单 REVOLUTE)子样式，axis 与 hinge 位置随子样式定。`a5b4` 的 `clip_arm`(housing 上第二 REVOLUTE `(-1,0,0)` 摆臂) 与 `dff9` 的 `stand`(housing 后第二 REVOLUTE `(1,0,0)` 撑架)结构上同属「housing + 单 part + 第二 REVOLUTE」，归入 `hinged_door` 候选的 axis/位置变体(rear-stand / side-clip)，不单列以避免每槽候选膨胀；若 reviewer 要求拆细可升为独立候选 `rear_stand` / `clip_arm`。常见 reference example 可选 `plain_no_extra`(占 5 星多数：23 个中 13 个是纯 4-part 主干)。

## 槽位图（slot graph）
```
pattern = mixed
（身份串联链 housing→pendulum→sliding_weight 是移动副链；winding_key 与可选 door/lid/legs/base 是 housing 的并列 children；legs 是 multiplicity）

   [Slot6 separate_base: 可选独立 base] --FIXED-->
                                                   housing (Slot1, root 或 base 的 child)
                                                     |
            +----------------+------------------------+------------------------+----------------------+
            | REVOLUTE       | CONTINUOUS              | FIXED (gated)          | REVOLUTE (gated)     | REVOLUTE ×N (gated)
            v (pivot, ±Y)    v (key, ±X/±Y/±Z)         v                        v (±X)                 v (±Z)
   pendulum (Slot2)    winding_key (Slot4)     [mechanism/escapement]   [front_door/lid/panel]   [stabilizer_leg_{i}]
            |                                   (Slot6 internal_mechanism)  (Slot6 hinged_door)    (Slot6 fold_out_legs, N=1..2)
            | PRISMATIC (±Z, 沿杆)
            v
   sliding_weight (Slot3) ── [+第二 PRISMATIC 沿杆 → fine_weight，仅 Slot5=coarse_plus_fine]
```
- 恒定身份骨架：`housing -> pendulum`(REVOLUTE) -> `sliding_weight`(PRISMATIC) + `housing -> winding_key`(CONTINUOUS)。
- Slot5=`coarse_plus_fine` 时 sliding_weight 拆成 coarse+fine 两 part，引入第二 PRISMATIC（仍 parent=pendulum）。
- Slot6 决定是否新增 base(FIXED)/door(REVOLUTE)/mechanism(FIXED)/legs(REVOLUTE×N) 件；`plain_no_extra` 时无附加件。
- Slot4 winding_key 默认 parent=housing；仅 Slot6=`hinged_door` 且 key 落在盖上时 parent=lid(随 S9)。

## 部件（Parts）

### Slot1 housing
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `housing` / `body` / `cabinet` / `frame` | ~8-16 | 方锥/梯形/方盒/落地柜外壳 + base plinth + 内 pivot cheek/journal/pedestal + tempo scale + key boss | S1/S3/S5/S8/S14 |

### Slot2 pendulum
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `pendulum` | ~4-5 | pivot barrel/boss/hub + rod(Cylinder 或方 Box) + 顶 top_cap 或底 counterweight/tip + 横 pivot_pin | S2/S4/S7/S6 |

### Slot3 sliding_weight
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `sliding_weight` / `weight` / `tempo_weight` / `slider_weight` | ~2-5 | 带 bore/cheek 的配速 bob，套在 rod 上 + index line/grip | S1/S7/S10/S12 |

### Slot4 winding_key
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `winding_key` / `key` / `winding_knob` / `crown_knob` | ~3-6 | collar/hub + stem + wings/crossbar/handle + grip lobe，绕自身轴连续旋转 | S2/S4/S7/S9 |

### Slot5 weight_dof（multiplicity 1..2）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `coarse_weight` / `fine_weight` | ~1-2 each | `coarse_plus_fine` 时的两 LatheGeometry shell-collar，各自独立 PRISMATIC、区间不重叠 | S10/S11 |

### Slot6 case_extras（gated）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `front_door` / `lid` / `front_panel` | ~3-6 | 可选门/盖/玻璃面板，第二 REVOLUTE 开合 | S6/S9/S15 |
| `mechanism` / `escapement_gear` | ~9-30 | 可选内部机芯/擒纵齿，FIXED 到 housing | S6/S15 |
| `base` | ~2 | 可选独立底座，FIXED 承托 housing | S14 |
| `stabilizer_leg_{i}` / `rear_leg_{i}` | ~3 each | 可选 fold-out 脚 ×N(1..2)，REVOLUTE 外摆 | S12/S13 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `pendulum_pivot` / `housing_to_pendulum` | revolute | Slot1 housing | Slot2 pendulum | `(0,±1,0)`(主) / `(±1,0,0)` | `[-0.55,0.55]` 典型对称摆 | 主关节：摆杆绕顶前缘水平轴左右摆 | S2/S4/S7 |
| `weight_slide` / `pendulum_to_*weight` | prismatic | Slot2 pendulum | Slot3 sliding_weight | `(0,0,±1)`(沿杆) | `[0,0.04~0.13]` 或 `[-0.6,0.1]`(长杆) | 第二主关节：bob 沿杆上下滑调速 | S2/S7/S11 |
| `key_axle` / `housing_to_winding_key` | continuous | Slot1 housing(或 lid) | Slot4 winding_key | `(±1,0,0)` / `(0,±1,0)` / `(0,0,±1)` | unlimited | 第三主关节：上弦钥匙绕自身轴连续转 | S2/S7/S9 |
| `pendulum_to_fine_weight` | prismatic (gated) | Slot2 pendulum | Slot5 fine_weight | `(0,0,1)` | `[-0.015,0.015]` | 仅 Slot5=`coarse_plus_fine`：第二滑块独立微调 | S11 |
| `housing_to_front_door` / `lid_hinge` | revolute (gated) | Slot1 housing | Slot6 door/lid/panel | `(±1,0,0)` | `[0,1.0~1.35]` | 仅 Slot6=`hinged_door`：门/盖开合二级 DOF | S6/S9/S15 |
| `housing_to_mechanism` / `body_to_gear` | fixed (gated) | Slot1 housing | Slot6 mechanism/gear | n/a | n/a | 仅 Slot6=`internal_mechanism`：机芯钉死在壳内 | S6/S15 |
| `base_to_housing` | fixed (gated) | Slot6 base | Slot1 housing | n/a | n/a | 仅 Slot6=`separate_base`：独立底座承托壳 | S14 |
| `leg_hinge_{i}` / `body_to_*_stabilizer` | revolute (gated) | Slot1 housing | Slot6 stabilizer_leg_{i} | `(0,0,±1)` | `[0,0.76~1.10]` | 仅 Slot6=`fold_out_legs`：fold-out 脚外摆，N=1..2 | S12/S13 |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `housing_style` | enum | `squat_pyramid_shell` / `tapered_mesh_shell` / `box_case` / `floor_cabinet` | `squat_pyramid_shell` | drives Slot1 壳构造与量级(`floor_cabinet` 配长摆) | S1/S5/S8/S3 |
| `pendulum_style` | enum | `rod_with_top_cap` / `rod_with_bob_tip` / `long_cabinet_rod` / `slim_rod_with_lower_bob` | `rod_with_top_cap` | drives Slot2；`long_cabinet_rod` 仅配 `floor_cabinet` | S2/S7/S4/S6 |
| `weight_style` | enum | `cadquery_bore_collar` / `cheek_clamp_weight` / `lathe_shell_collar` / `extrude_ring_weight` | `cadquery_bore_collar` | drives Slot3；`cheek_clamp_weight` 配方截面 rod | S1/S7/S10/S12 |
| `key_style` | enum | `winged_side_key` / `crossbar_rear_key` / `stem_handle_key` / `top_face_knob` | `winged_side_key` | drives Slot4 与 key 安装面/轴向 | S2/S7/S4/S9 |
| `weight_dof` | enum | `single_weight` / `coarse_plus_fine` / `weight_plus_index` | `single_weight` | drives Slot5：PRISMATIC 个数 1 或 2 | S1/S10/S7 |
| `case_extras` | enum | `plain_no_extra` / `hinged_door` / `internal_mechanism` / `separate_base` / `fold_out_legs` | `plain_no_extra` | drives Slot6：附加 part/joint 类型 | S1/S6/S6/S14/S12 |
| `pendulum_axis` | enum | `pos_y=(0,1,0)` / `neg_y=(0,-1,0)` / `x=(1,0,0)` | `pos_y` | revolute.axis；21/23 用 `±Y`（19 用 `+Y`，2 用 `−Y`），2 用 `+X` | S2/S6/S10 |
| `key_axis` | enum | `x=(±1,0,0)` / `y=(0,±1,0)` / `z=(0,0,±1)` | `x` | continuous.axis；随 key 安装面 | S2/S7/S9 |
| `pendulum_swing` | float | `0.12 - 0.65` rad（实测全距；典型 0.3–0.45）| sampled | revolute `[-s, +s]` 对称摆角上限 | 全 23 个实测 / S1/S3/S6 |
| `case_height` | float | `0.15 - 0.24`(便携) / `0.9 - 1.05`(`floor_cabinet`) | sampled | 壳高，pivot_z ≈ case_top | S1/S3/S8 |
| `rod_length` | float | `0.18 - 0.30`(便携) / `1.3 - 1.5`(`floor_cabinet`) | sampled | 摆杆长，weight_travel < rod_length | S2/S4/S7 |
| `weight_travel` | float | `0.04 - 0.13`(便携) / `0.5 - 0.7`(长杆) | sampled | PRISMATIC `upper`，沿杆行程 | S1/S3/S7 |
| `weight_bore_radius` | float | `0.0035 - 0.006` | sampled | `> rod_radius` 留 press/clearance | S1/S10 |
| `leg_count` | int | `randint(1, 2)` | 2 | 仅 `fold_out_legs`；S13 用循环建 N 件 | S12/S13 |
| `door_open_upper` | float | `1.0 - 1.35` rad | sampled | 仅 `hinged_door` | S6/S9 |
| `key_velocity` | float | `5.0 - 10.0` | sampled | CONTINUOUS velocity(无角限) | S2/S3 |

## Multiplicity / Copy Logic

- 无模板级复制数量逻辑：核心结构由固定 named slots 和 gated module-local fixed copies 表达，不暴露全局 `*_count` 作为主拓扑采样轴。
- 若某个 module source 内部包含固定成对、环形阵列或若干重复 visual/part，模板实现应把它保留为 module-local construction，并使用稳定命名；不得把未审核的可变复制数量加入 seed domain。
- 未来若要把固定重复结构升级为可变 multiplicity，必须补充来源、N_range、placement、joint policy、regression seeds 和 reviewer 审核记录。

## 拓扑多样性审计
- 每槽候选数：Slot1=4，Slot2=4，Slot3=4，Slot4=4，Slot5=3，Slot6=5。
- total_combinations（未加相容约束）= 4 × 4 × 4 × 4 × 3 × 5 = **3840**。
- 加合理相容约束(`long_cabinet_rod` 配 `floor_cabinet`、`cheek_clamp_weight` 配方截面 rod)后仍有数百种合法组合。

| 结构骨架（part/joint 拓扑，按 Slot5 × Slot6 计） | part 数 | 主要 joint |
|---|---|---|
| 单滑块 + plain（默认主干） | 4 | REVO + PRIS + CONT |
| 双滑块(coarse+fine) + plain | 5 | REVO + 2×PRIS + CONT |
| 单滑块 + hinged_door | 5 | 2×REVO + PRIS + CONT |
| 单滑块 + internal_mechanism | 5 | REVO + PRIS + CONT + FIXED |
| 单滑块 + separate_base | 5 | FIXED + REVO + PRIS + CONT |
| 单滑块 + fold_out_legs(N=1) | 5 | 2×REVO + PRIS + CONT |
| 单滑块 + fold_out_legs(N=2) | 6 | 3×REVO + PRIS + CONT |
| 双滑块 + hinged_door | 6 | 2×REVO + 2×PRIS + CONT |
| 双滑块 + fold_out_legs(N=2) | 7 | 3×REVO + 2×PRIS + CONT |

→ ≥9 个明确不同的 part/joint 拓扑骨架(part 数 4→7、REVOLUTE 1→3、PRISMATIC 1→2、含/不含 FIXED)，远超阈值 5；叠加 4×4×4×4 个构造槽后离散组合达 3840。

| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---|---|---|
| Slot1 housing | 4 | yes | |
| Slot2 pendulum | 4 | yes | |
| Slot3 sliding_weight | 4 | yes | |
| Slot4 winding_key | 4 | yes | |
| Slot5 weight_dof | 3 | yes | 但有效结构骨架仅 2(单/双滑块)，3 个候选中 2 个共享单-DOF 骨架，已注明 |
| Slot6 case_extras | 5 | yes | |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
- identity：存在 housing/body(root 或 base 的 child) + 恰好 1 个 pendulum + ≥1 个 sliding_weight + 1 个 winding_key。
- primary joint：恰好 1 个 `pendulum_pivot` REVOLUTE + ≥1 个 `weight_slide` PRISMATIC(parent=pendulum) + 1 个 `key` CONTINUOUS；默认 case_extras=plain 时无其他 joint。
- pendulum axis & range：pendulum REVOLUTE 轴为水平(`±Y` 主，`±X` 允许)，对称摆角 `lower≈-s, upper≈+s`，`0.1<=s<=0.7`（覆盖实测 23 个 0.12–0.65 全距，勿写死成更窄的 [0.2,0.6]——会误拒 4/23 个真 5 星）；非 CONTINUOUS、非竖直 `±Z`。
- weight prismatic：沿杆 `(0,0,±1)`，weight 套在 rod 上(`expect_within`/`expect_overlap` 与 rod coaxial)，行程 < rod_length；扫 lower→upper 时 weight 沿杆移动且保持 coaxial。
- weight rides rod：滑块 bore/cheek 与 rod 接触(`allow_overlap` press-fit friction pad / cheek clamp)，不漂浮、不脱离 rod。
- key continuous：CONTINUOUS 且 `motion_limits.lower is None and upper is None`，绕自身轴；扫 π/2 时 grip 实际转位。
- dual weight(gated)：`coarse_plus_fine` 时两 PRISMATIC 区间不重叠，coarse 动时 fine 不被拖动(独立)。
- door(gated)：`hinged_door` 时门/盖闭合覆盖开口(`expect_overlap`)、开到 upper 时显著位移且不穿模。
- legs(gated)：`fold_out_legs` 时每脚 REVOLUTE 外摆，foot_pad 落地支撑姿态。
- base(gated)：`separate_base` 时 FIXED `base_to_housing`、root 落地、housing 不漂浮。
- swing coherence：扫 pendulum 到 ±upper 时 sliding_weight 随杆侧移(`weight_pos[lateral]` 变化)，证明摆+滑块语义连贯。
- no floating：pendulum/weight/key/door/mechanism/base/legs 全部 attached 或 FIXED；无悬空装饰件。

## Reject cases（必须能识别并拒绝）
- 缺少 sliding tempo weight 或它不是 PRISMATIC(做成 FIXED 装饰、或根本没有 bob)——退化成纯单摆，出界。
- 摆杆不是 REVOLUTE(被做成 CONTINUOUS 连续旋转 / PRISMATIC 上下抽 / FIXED)，或摆角竖直轴 `±Z`(变成转盘)。
- winding key 不是 CONTINUOUS(被加角限做成 REVOLUTE 拨杆)，或缺失。
- 发明摆与滑块的 coupled/mimic 联动，或做成多摆共轴(本类是单摆 + 单滑块；coarse+fine 只是两独立 PRISMATIC，非联动)。
- sliding_weight 不套在 rod 上(漂在杆外 / 与 rod 不 coaxial / 脱离杆悬空)。
- `coarse_plus_fine` 声称两滑块却共用一个 PRISMATIC、或两区间重叠导致碰撞穿模。
- `separate_base` 声称独立 base 却把 housing 直接落地(base 漂浮)，或 `fold_out_legs` 脚不与底角接触/不落地支撑。
- `hinged_door` 门闭合却不覆盖开口、或门/盖做成 PRISMATIC 滑盖、或开门时与壳体非预期穿模。
- mechanism/escapement/dial_face/base/legs 等附件悬空，不 FIXED/attached 到 housing。
- 把落地摆钟(无滑动 bob)、天平/指针仪表、单铰链盖盒硬塞进本模板。

## 与相邻类别的边界
- vs `pendulum_clock` / `floor_clock`(落地摆钟)：钟摆靠固定 bob 自然摆、不靠可滑 tempo weight 调频；本类摆杆短、必有沿杆 PRISMATIC 的配速块。`floor_cabinet` 样式量级接近落地钟但仍保留可滑 bob。
- vs `single_revolute_hinge` / `tackle_box_with_simple_hinged_lid`(单铰链盖盒)：那些主体就是 fixed half + 单 REVOLUTE 盖；本类铰链 door/lid 只是 gated 附件，主体是摆+滑块+上弦三元身份。
- vs `balance_scale` / `analog_meter`(天平 / 指针仪表)：那些指针/横梁绕轴摆但无沿臂可滑配速块、无上弦 CONTINUOUS；本类三 DOF 俱全。
- vs `coaxial_rotary_stack` / `screwin_light_bulb`(连续旋转/螺旋)：那些是连续旋转主体；本类主体是有限摆角 REVOLUTE + 沿杆 PRISMATIC，CONTINUOUS 仅限上弦小件。
- vs `desk_with_drawer` / `sliding_window`(纯移动副)：那些主 DOF 是 PRISMATIC 抽拉；本类 PRISMATIC 仅是套在摆杆上的配速块，主身份是摆动 REVOLUTE。

## 模板实现备注（可选）
- 共享 helper：`_housing_shell`(cadquery loft，S1) / `_build_tapered_housing_shell`(MeshGeometry，S14) / `section_loft`(S10/S12) / primitive box(S8) 四套壳工厂按 `housing_style` 分发；`_sliding_weight`(cadquery bore，S1) / `_collar_mesh`(LatheGeometry，S10) / cheek-clamp(S7) / superellipse(S12) 四套 bob 工厂按 `weight_style` 分发。
- `pendulum_to_sliding_weight` PRISMATIC 不创建独立锚定 surface(weight 直接套 rod)，需 `ctx.allow_overlap(pendulum, weight, friction_pad/cheek, rod, reason="...")` 声明 press-fit/clamp 重叠(S2 L298-L304 模式)；保持 weight bore/cheek 与 rod coaxial。
- gated 件(door/mechanism/base/legs) 经 FIXED/REVOLUTE 创建独立 child part 时必须带 `MatingContract`(Rule 2)：door 的 hinge_barrel ↔ housing 的 hinge saddle、leg 的 hinge_barrel ↔ housing 底角、base 的 cap ↔ housing 底面。
- `floor_cabinet`(S3) 是开口前面板壳，摆杆从前 opening 露出；与便携 `squat_pyramid_shell` 共享同一 pendulum/weight/key 装配，仅尺寸量级与壳工厂不同——不要做成两套模板。
- leg multiplicity(S13 `for leg_index`) 与 fold-out REVOLUTE 在同一循环体内 emit part + joint；`leg_count` 控制 1..2 件，axis 左右镜像 `(0,0,±1)`。
- `coarse_plus_fine`(S11) 两 PRISMATIC 同 parent=pendulum、不同 origin z、区间不重叠，author_run_tests 需断言互不拖动(S11 L333-L381 模式)。
