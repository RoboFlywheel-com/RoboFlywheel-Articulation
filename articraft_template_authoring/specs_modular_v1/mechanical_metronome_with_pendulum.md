# mechanical_metronome_with_pendulum — Modular Spec

> 承接 sibling slug `metronome` 的成熟规范, 覆盖 0611 图片扩展流水线定义的
> "带摆杆的机械节拍器" 小类. 与 `metronome` 相比, 本 slug 的差异只在:
> (a) palette 家族扩到 5 档 (walnut / mahogany / black+gold / cream+brass /
> modern-white) 覆盖 picture/0611 参考照 001.png 中出现的木壳+黄铜风格,
> (b) case_form 主体形态族显式登记 (pyramid / rectangular / arched /
> floor-cabinet), (c) 保留 hinged_door(front_closure) / dual_weights(tempo_module) /
> folding_side_key(winding) / swing_carry_handle(handle) / leveling_foot(base)
> 五条 source-map planned candidate.
>
> 骨架、joint 恒定身份 (REVOLUTE 摆 + PRISMATIC 滑块 + CONTINUOUS 上弦) 与
> `metronome` 完全一致.

## 元信息
| 项 | 值 |
|---|---|
| slug | `mechanical_metronome_with_pendulum` |
| template path | `agent/templates/mechanical_metronome_with_pendulum.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (housing→pendulum→sliding_weight 移动副链 + winding_key/optional door/mechanism/base/legs/handle 并列 children + leg multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 23 (sibling slug `metronome` 池) + 1 origin `mechanical_metronome_001` |
| read_count | 8 精读 + 1 origin |
| read_scope | 采纳 sibling slug 已 approved 的 8 个 5-star 源码块 (见下方 Adopted Source Index), 并附加 0611 origin_anchor `rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e44f59a0309e028d26892` |
| source_index_policy | 只索引采纳的可复用片段, sibling `metronome` 的家族 (squat-pyramid / tapered-mesh / box / floor-cabinet / cadquery-bore / lathe-collar / cheek-clamp / superellipse / door / mechanism / base / legs / dual-weight / cabinet-rod / long-cabinet-rod) 与 origin_anchor 观察一致 |

## 核心身份

机械节拍器 (mechanical metronome with pendulum): 一个落地的 case (常为方锥/梯形/方盒/落地柜), case 顶部前缘附近有一根**摆杆 pendulum rod** 经 **REVOLUTE** 绕水平轴 (多为前后向 `±Y`) 左右摆动; 摆杆上套一个**配速滑块 sliding tempo weight** 经 **PRISMATIC** 沿杆长方向 (`±Z`) 上下滑动以改变摆频; case 侧/后/顶面板上还有一个**上弦钥匙 winding key** 经 **CONTINUOUS** 绕自身轴旋转. 这三 DOF (REVOLUTE 摆 + PRISMATIC 滑块 + CONTINUOUS 上弦) 是全部 5 星与 origin_anchor 共有的恒定身份骨架.

不该混入:

- **数字/电子节拍器**: 无摆杆、无 tempo weight、无 CONTINUOUS 上弦, 只是按钮 + 显示.
- **落地摆钟 pendulum clock**: bob 固定, 靠 gear 走时, 无沿杆可滑 tempo weight; 本类必有 PRISMATIC.
- **单铰链盖盒**: 主体是 fixed half + 单 REVOLUTE 盖; 本类 door/lid 只是 `case_extras` gated 附件.
- **天平/指针仪表**: 无沿臂可滑配速块, 无上弦 CONTINUOUS.
- **纯装饰道具**: 无关节.

## Adopted Source Index

复用 sibling `metronome` spec 的 8 个 adopted 源码块 (S1..S15), 详细的 model.py 行范围与用途见 `articraft_template_authoring/specs_modular_v1/metronome.md` §"采用源码索引" (adopted source index). 本 spec 完全继承这些源码块的采纳结论 —— origin_anchor `picture/0611/mechanical_metronome_with_pendulum/001.png` 已在图像识别核对中确认属于 sibling 的 `squat_pyramid_shell` × `rod_with_top_cap` × `cadquery_bore_collar` × `winged_side_key` 主家族 (与 S1/S2 完全一致), 不引入新的结构族.

Origin_anchor: `rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e44f59a0309e028d26892` (picture/0611/mechanical_metronome_with_pendulum/001.png).

## 槽位 + 候选模块表

### Slot 1: case (Primary Form Family, ③) — housing / case, root part

节拍器接地外壳, 承载摆轴 pivot、上弦 key boss、tempo scale. **形态主导 slot**, 四个可识别 primary-form 原型.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| `squat_pyramid_shell` | forked_anchor | S1 rec_metronome_0307c136…; origin_anchor 图像匹配 | L29-L98, L115-L188 | eligible if compatible | Volumetric Envelope Form (方锥 loft) | cadquery `rect→loft→cut` 方锥/楔形中空壳 + 前 tempo-window 大圆角切口 + top-slot 摆杆出口; 经典 Maelzel 造型 |
| `tapered_mesh_shell` | forked_anchor | S5 rec_metronome_1136c31b…; S14 rec_metronome_0d660052… | 1136…:L57-L320 / 0d66…:L28-L175 | eligible if compatible | Macro Surface Construction (MeshGeometry 四面 quad panel) | MeshGeometry 四 `_panel_from_quad` 上小下大梯形壳 + 前门框 stile/lintel + tempo scale strip |
| `box_case` | forked_anchor | S8 rec_metronome_448b77a5… | L40-L139 | eligible if compatible | Planar Boundary Form (直墙 primitive box) | primitive Box 拼方盒壳 (plinth + floor + 四壁 + front sill/header); 现代直方形 |
| `floor_cabinet` | forked_anchor | S3 rec_metronome_2b18c190… | L44-L156 | eligible if compatible | Volumetric Envelope Form (高柱柜式) | 落地柜式高壳 (plinth + floor + 四壁 + roof + 前 opening 框); 配长摆杆, 落地钟量级 |

### Slot 2: pendulum — REVOLUTE child

绕 case 顶部前缘水平轴摆动的摆杆, 必为单 REVOLUTE. 结构必带 pivot barrel/boss + rod + 顶/底 tip.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rod_with_top_cap` | forked_anchor | S2 rec_metronome_0307c136… | L190-L214 | eligible if compatible | rod_shaft Cylinder + pivot_boss Sphere + pivot_pin + 顶 top_cap; 杆顶露出壳外 |
| `rod_with_bob_tip` | forked_anchor | S7 rec_metronome_1136c31b… | L443-L472 | eligible if compatible | rod Cylinder + pivot_sleeve + 底 lower_counterweight + tempo_pointer; 欧式机芯倒挂 |
| `long_cabinet_rod` | forked_anchor | S4 rec_metronome_2b18c190… | L158-L188 | eligible if compatible | pivot_hub Cylinder + 横 arm + rod_collar + 极长 rod + sphere rod_tip; 落地柜专用 |
| `slim_rod_with_lower_bob` | forked_anchor | S6 rec_metronome_7af0c6f9… | L132-L161 | eligible if compatible | pivot_barrel + 极细方 rod + lower_bob + lower_tip; 便携小型摆 |

### Slot 3: sliding_weight (tempo_module) — PRISMATIC child

套在摆杆上沿杆滑动调速的 tempo weight, 恒为 PRISMATIC. Source map row `tempo_module = bell-beat slider` 与该 slot 一一对应 (滑块沿杆 = bell-beat slider 位置).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `cadquery_bore_collar` | forked_anchor | S1 rec_metronome_0307c136… | L84-L98, L216-L233 | eligible if compatible | cadquery 圆柱 + clearance bore + index line + friction pad (press-fit allow_overlap) |
| `cheek_clamp_weight` | forked_anchor | S7 rec_metronome_1136c31b… | L488-L538 | eligible if compatible | left/right cheek + front/back bridge + wedge; 双侧抱住方 rod |
| `lathe_shell_collar` | forked_anchor | S10 rec_metronome_c8917520… | L36-L45, L142-L162 | eligible if compatible | LatheGeometry 中空环 collar (coaxial 套 rod), 可单件或双件 (见 Slot 5) |
| `extrude_ring_weight` | forked_anchor | S12 rec_metronome_7af0c6f9… | L163-L184 | eligible if compatible | superellipse 外轮廓 + 内孔 + 侧 grip; 套圆 rod |

### Slot 4: winding_key — CONTINUOUS child

case 侧/后/顶面板上绕自身轴连续旋转的上弦件, 恒为 CONTINUOUS. Source map row `winding = folding side key` 对应本 slot 的 `winged_side_key` / `stem_handle_key` 侧向变体.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `winged_side_key` | forked_anchor | S2 rec_metronome_0307c136…; origin_anchor 图像匹配 | L235-L254 | eligible if compatible | key_collar + 双 wing Box + 端 lobe; 侧面板 `(±1,0,0)` 蝶形 |
| `crossbar_rear_key` | forked_anchor | S7 rec_metronome_1136c31b… | L554-L592 | eligible if compatible | key_shaft + hub + stem + crossbar; 后面板 `(0,-1,0)` |
| `stem_handle_key` | forked_anchor | S4 rec_metronome_2b18c190… | L204-L240 | eligible if compatible | escutcheon + 长 stem + 横 bar + 双端 grip ball; 侧面板长杆手柄 (folding-side-key 变体) |
| `top_face_knob` | forked_anchor | S9 rec_metronome_448b77a5… | L237-L278 | eligible if compatible | key_shaft + hub + arm + grip_knob; 顶/盖面 `(0,0,-1)` 小旋钮 |

### Slot 5: weight_dof — multiplicity gate on tempo_module

sliding weight 是 1 件还是 coarse+fine 2 件 (各自独立 PRISMATIC). 决定 PRISMATIC 关节数与 part 数. Source map row `tempo_module = dual weights` 与本 slot `coarse_plus_fine` 一一对应.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_weight` | forked_anchor | S1 rec_metronome_0307c136… | L216-L273 | eligible if compatible | 1 个 sliding_weight + 1 个 `weight_slide` PRISMATIC (默认主干) |
| `coarse_plus_fine` | forked_anchor | S10+S11 rec_metronome_c8917520… | L142-L162, L204-L232 | eligible if compatible | coarse_weight + fine_weight 双 collar part, `pendulum_to_coarse_weight` + `pendulum_to_fine_weight` 两 PRISMATIC (区间不重叠) |
| `weight_plus_index` | forked_anchor | S7 rec_metronome_1136c31b… | L488-L538 | eligible if compatible | 仍是 1 PRISMATIC + weight 含 index/pointer 细节 (单-DOF 骨架的细节变体) |

### Slot 6: case_extras — gated 附件 (front_closure / handle / base / mechanism)

挂在 case 上的可选件, 一次采样一个: 内部机芯 (FIXED) / 前门或顶盖 (REVOLUTE) / 独立 base (FIXED) / 折叠脚 (REVOLUTE × N=1..2). Source map planned candidates `front_closure = hinged cover`、`handle = swing carry handle`、`base = leveling foot` 全部落到本 slot (见下表 candidate 说明).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_no_extra` | forked_anchor | S1 rec_metronome_0307c136…; origin_anchor 图像匹配 | L115-L188 | eligible if compatible | 仅 case 自带 pivot cheek/bridge visual; 无附加 part/joint (默认主干, 4 part) |
| `hinged_door` | forked_anchor | S6/S9/S15 rec_metronome_1136c31b… / 448b77a5… / cd4513ba… | 1136…:L396-L441 / 448b…:L177-L235 / cd45…:L118-L159 | eligible if compatible | 一个 `front_door` 经 REVOLUTE 挂 case; 覆盖 source map `front_closure = hinged cover` 语义 |
| `internal_mechanism` | forked_anchor | S6/S15 rec_metronome_1136c31b… / cd4513ba… | 1136…:L322-L394 / cd45…:L161-L195 | eligible if compatible | `mechanism` part (spring barrel/gears/escapement/anchor), FIXED, 无附加 DOF |
| `separate_base` | forked_anchor | S14 rec_metronome_0d660052… | L77-L183 | eligible if compatible | 独立 `base` part (plinth + cap), FIXED 承托 case; 覆盖 source map `base = leveling foot` (调平底座) |
| `fold_out_legs` | forked_anchor | S12/S13 rec_metronome_7af0c6f9… / 31c18f36… | 7af0…:L186-L316 / 31c1…:L232-L260 | eligible if compatible | N 个 `stabilizer_leg_{i}` REVOLUTE 外摆 (N=1..2); 兼作 source map `handle = swing carry handle` 拓扑同族 (皆为 case + 单 part + 单 REVOLUTE, 只是位置/轴向不同) |

说明:

- Source map planned candidate `handle = swing carry handle` 与 `fold_out_legs` 同属 "case + 单 part + 单 REVOLUTE" 拓扑, 结构上无独立骨架差异, 归入 `fold_out_legs` axis 变体避免每槽候选膨胀. 若 reviewer 要求拆细可升为独立候选 `carry_handle`.
- Source map planned candidate `handle` 与 `base` 的独立性需 forked variant records; 当前 (P3) 未生成额外 forked_anchor 就先用 sibling `metronome` 的 record-only 复用. 待 P4 sweep 通过后 P5 造 record 时如出现 identity issue 可回补 forked_anchor.

## 槽位图 (slot graph)

```
pattern = mixed
恒定身份链: case (Slot 1) → pendulum (Slot 2, REVOLUTE ±Y) → sliding_weight (Slot 3, PRISMATIC ±Z)
并列 children: case → winding_key (Slot 4, CONTINUOUS)
gated (Slot 6):
  [separate_base FIXED, root=base] --FIXED--> case
                                                |
              +----------------+-----------------+-----------------+
              | REVOLUTE       | CONTINUOUS      | FIXED (gated)   | REVOLUTE ×N (gated)
              v (±Y)           v (key axis)      v                 v (±Z)
        pendulum          winding_key       [mechanism]     [stabilizer_leg_{i}]
              |                                              (fold_out_legs, N=1..2)
              | PRISMATIC (±Z, 沿杆)                          + gated REVOLUTE (hinged_door)
              v
       sliding_weight ── [+第二 PRISMATIC → fine_weight, 仅 weight_dof=coarse_plus_fine]
```

- 每条跨-slot 连接的 mating face / pivot / axis 见 `metronome.md` slot graph.
- Slot 6 gates 互斥 (一次一个): plain / hinged_door / internal_mechanism / separate_base / fold_out_legs.
- Slot 4 winding_key 默认 parent=case; `top_face_knob` + `hinged_door` (顶盖) 组合时会挂在 case (不挂 lid) 以保持接口简单.

## 每槽位 Module Emits / Interfaces

### Slot 1 / case
| emits | 描述 | 来源 |
|---|---|---|
| parts | `case` (root): floor + 壳 tier/wall + pivot cheek + tempo scale + key boss | S1/S3/S5/S8/S14 |
| internal joints | 无 | — |
| upstream interface | (root, 无) | — |
| downstream interface | pivot 面 (顶前缘, `y=0, z=pivot_z`) → pendulum; key boss 面 → winding_key; 底面 → base 或 legs | slot graph |

### Slot 2 / pendulum
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pendulum`: pivot_boss + rod + tip/cap/counterweight | S2/S4/S7/S6 |
| internal joints | 无 | — |
| upstream interface | pivot_boss (Cylinder 沿 Y), part 原点 = pivot 中心 | S2 |
| downstream interface | rod 沿 +Z 到 z=L, 作为 sliding_weight 的 rail | S1/S7 |

### Slot 3 / sliding_weight
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_weight`: bore/cheek/collar/ring + index/grip | S1/S7/S10/S12 |
| internal joints | 无 | — |
| upstream interface | bore/cheek 沿 rod 轴 (part 原点在 rod 轴) | S1 |
| downstream interface | 无 (终端 slot) | — |

### Slot 4 / winding_key
| emits | 描述 | 来源 |
|---|---|---|
| parts | `winding_key`: collar/hub + stem + wing/bar/handle + grip | S2/S4/S7/S9 |
| internal joints | 无 | — |
| upstream interface | collar (Cylinder 轴 = joint axis), part 原点 = 转轴上 | S2 |
| downstream interface | 无 (终端) | — |

### Slot 5 / weight_dof (multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `coarse_weight` + `fine_weight` (仅 `coarse_plus_fine`) | S10 |
| internal joints | 无 | — |
| upstream interface | 两 collar 各自沿 rod 轴 | S11 |
| downstream interface | 无 | — |

### Slot 6 / case_extras (gated)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_door` (hinged_door) / `mechanism` (internal_mechanism) / `base` (separate_base) / `stabilizer_leg_{i}` (fold_out_legs, N=1..2) | S6/S9/S14/S12/S13 |
| internal joints | door: REVOLUTE `(±1,0,0)`; mechanism: FIXED; base: FIXED; legs: REVOLUTE `(0,0,±1)` | slot table |
| upstream interface | door/legs hinge barrel ↔ case 前底/后底缘; mechanism ↔ case cavity; base cap ↔ case floor | S6/S12/S14 |
| downstream interface | 无 | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `housing_style` | enum | 4 candidates | `squat_pyramid_shell` | choice | procedural sampling | source map row `case_form` |
| `pendulum_style` | enum | 4 candidates | `rod_with_top_cap` | conditional | `long_cabinet_rod` 仅在 `housing_style == floor_cabinet` 时可选 | slot table |
| `weight_style` | enum | 4 candidates | `cadquery_bore_collar` | choice | procedural sampling | slot table |
| `key_style` | enum | 4 candidates | `winged_side_key` | choice | procedural sampling | slot table |
| `weight_dof` | enum | 3 candidates | `single_weight` | choice | procedural sampling | slot table |
| `case_extras` | enum | 5 candidates | `plain_no_extra` | choice | procedural sampling | source map rows `front_closure` / `base` / `handle` |
| `palette_style` | enum | 5 candidates: `maple_brass` / `mahogany_brass` / `ebony_brass` / `cream_brass` / `modern_white` | `maple_brass` | choice | procedural sampling; 覆盖 ⑥ 材质/涂装 | source map ④/⑥ observed + world knowledge |
| `case_width` | float | `[0.080, 0.140]` 便携, `[0.22, 0.30]` `floor_cabinet` | 0.115 | conditional | 上界随 `housing_style` 分档 | S1/S3/S8 |
| `case_depth` | float | `[0.060, 0.110]` 便携, `[0.20, 0.27]` `floor_cabinet` | 0.090 | conditional | 同上 | S1/S3/S8 |
| `case_height` | float | `[0.150, 0.260]` 便携, `[0.85, 1.10]` `floor_cabinet` | 0.205 | conditional | 上界随 `housing_style` | S1/S3/S8 |
| `pendulum_swing` | float | `[0.12, 0.65]` rad | 0.45 | independent | 对称摆角上限, `[-s, +s]` | 全 23 5-star 实测 |
| `door_open_upper` | float | `[0.95, 1.50]` rad | 1.20 | independent | 仅 `hinged_door` | S6/S9 |
| `leg_count` | int | `[1, 2]` | 2 | independent | 仅 `fold_out_legs`; leg multiplicity | S12/S13 |
| `rod_length` | float | derived | derived | equation | `= case_height * 0.78` | S2/S4 |
| `weight_travel` | float | derived | derived | equation | `= rod_length * 0.35` (便携) / `= rod_length * 0.45` (cabinet) | S2/S3 |
| `rod_radius` | float | derived | derived | equation | `0.005` (便携) / `0.008` (cabinet) | S2/S4 |
| `pivot_z` | float | derived | derived | equation | `= case_height * 0.18` | S1 |

`equation` / `inequality` / `conditional` 全部在 `resolve_config` 内求解, 不留给 builder.

### 7.5 编译预算 / compile budget

自报 <20s/seed. 依据: sibling `metronome.py` 实测 0.07–0.09s/seed (纯 primitive Box/Cylinder/Sphere, 无 cadquery/lathe/loft heavy 布尔; 每 seed part 数 4–7, visual 数 30–80). 分档 tessellation: 小半径特征 (rod, key collar) 用 SDK 默认 <=32 段, 主体壳全为 Box (无曲面高精度需求). 无重复 N 子件的 Mesh (即使 fold_out_legs N=1..2 也不复用 Mesh, 因是独立 part). 超出预算时先降 Cylinder length_segments, 再讨论迭代.

## Multiplicity / Copy Logic

- `count_param`: `leg_count`
- N samples: `fold_out_legs` (仅本 case_extras 分支)
- suggested `N_range`: `[1, 2]`; 权重档: 均匀采样 (S13 观察).
- copied object / naming / placement / joint policy:
  - copied object: `stabilizer_leg_{i}` (index 0..N-1), 共享 helper `_build_leg(side, index)`
  - naming: `stabilizer_leg_{i}` (稳定命名)
  - placement: 底后角对称 (index 0 → left `-x`, index 1 → right `+x`)
  - joint policy: 每条独立 REVOLUTE `leg_hinge_{i}`, axis `(0,0,±1)` 外摆, `[0, 1.10]` rad
- source / gating: 仅当 `case_extras == fold_out_legs` 时激活, 其他分支 `leg_count` 保持不采样.

其他 slot (housing/pendulum/weight/key/extras) 无模板级复制数量逻辑.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot 5 `single_weight` vs `coarse_plus_fine` 引入 +1 PRISMATIC; Slot 6 `hinged_door` +1 REVOLUTE, `internal_mechanism` +1 FIXED, `separate_base` +1 FIXED, `fold_out_legs` +1..2 REVOLUTE; part 数 4→7 (≥9 拓扑骨架, 见 metronome.md 拓扑多样性审计); 全部 forked_anchor |
| └ multiplicity | 同构件 ×N | 有 | `leg_count ∈ [1,2]`, 见 §"Multiplicity / Copy Logic" |
| ② 关节类型 | 图不变, 某条边换 type/轴 | 有 | 恒定身份: REVOLUTE (pendulum) + PRISMATIC (weight) + CONTINUOUS (key); Slot 6 gated 新增: REVOLUTE (door/legs) / FIXED (mechanism/base); axis 变体 (winding_key: ±X / -Y / -Z, door: ±X, legs: ±Z); forked_anchor |
| ③ 主体形态家族 / Primary Form Family | 图 & 关节不变, 换核心 part 可识别几何形态原型 | 有 | Slot 1 `case`: `squat_pyramid_shell` (Volumetric Envelope, 方锥 loft) / `tapered_mesh_shell` (Macro Surface, 四 quad panel) / `box_case` (Planar Boundary, 直方) / `floor_cabinet` (Volumetric Envelope, 高柱); 4 candidates, 全 forked_anchor. 覆盖 pyramid / rectangular / arched (tapered) / floor-cabinet 四类观察形态 |
| ④ 表面装饰 | 原型不变, 叠加表面细节 / 改装饰数 | 有 | `record_only` + `world_knowledge_extrapolation`: 每壳的 tempo_scale plate + ticks (S1) / crown lower/upper (S5) / apex_cap (S1) / plinth (S1) / front_sill / front_header; 由宿主 case 表面派生 (Rule 4). 无独立 module. |
| ⑤ 尺寸/行程 | 离散全不变, 只连续改尺寸/比例/行程 | 有 | 关键比例: `case_width [0.080, 0.30]`, `case_depth [0.060, 0.27]`, `case_height [0.150, 1.10]` (`housing_style` 分档), `pendulum_swing [0.12, 0.65]`, `door_open_upper [0.95, 1.50]`. **每个非-continuous 关节的运动包络与 motion_test_plan**: (1) `pendulum_pivot` REVOLUTE 轴 `(0,1,0)`, `[-swing, +swing]`, 覆盖 `{lower, upper, mid}` + 组合 collision + targeted `ctx.pose({pendulum_pivot: swing})` 验位移; (2) `weight_slide` PRISMATIC 轴 `(0,0,1)`, `[0, weight_travel]`, 覆盖 `{0, upper, mid}` + targeted; (3) `housing_to_front_door` REVOLUTE `(±1,0,0)`, `[0, door_open_upper]`, 覆盖 `{0, upper}` + targeted; (4) `leg_hinge_{i}` REVOLUTE `(0,0,±1)`, `[0, 1.10]`, 覆盖 `{0, upper}` + targeted. 关节全程不穿模; 通过 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)` |
| ⑥ 涂装 | 几何全不变, 只改材质/颜色 | 有 | `palette_style` 5 candidates: `maple_brass` (浅木 + 黄铜) / `mahogany_brass` (深红木 + 黄铜) / `ebony_brass` (黑檀 + 亮金) / `cream_brass` (奶白 + 黄铜) / `modern_white` (纯白 + 银灰). 材质大类: painted (2), wood (2), metal accents (5). 覆盖 ≥ ceil(0.5×5)=3 材质大类. 五档共同 palette key: case / case_dark / metal / rod / bob / accent / glass / dark. |

**收尾自检**: `template batch mechanical_metronome_with_pendulum --seeds 0-9` 目检时: (a) 5 档 palette 都出现且视觉可分, (b) 4 档 case_form 都出现且拉得开 (pyramid / tapered / box / cabinet 一眼可辨), (c) pendulum 摆到 ±swing、weight 滑到 upper 都不穿模, (d) door/legs 开启无穿模.

## 采样与覆盖审计

总组合数 (未加相容约束) = 4 × 4 × 4 × 4 × 3 × 5 × 5 (palette) = **9600**. 加相容约束 (long_cabinet_rod 仅 floor_cabinet) 后仍 >>300.

seed_domain_policy: `procedural_first`.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` 对所有 seed (含 `seed=0`) 用 deterministic procedural sampling: `random.Random(seed)` 先选 `housing_style`, 若 `floor_cabinet` 则 pendulum 强制 `long_cabinet_rod` 且尺寸走 cabinet 分档 (compat gate), 其它槽独立 `rng.choice`. 连续 scale 全部 `rng.uniform` 在分档范围内, `resolve_config` 内 clamp + 派生. Regression overrides: 无 (默认全 procedural). Random sweep: `sweep-pipeline` 跑 0-15 (fast) + 16-35 (final) + corner. Topology target: 1000-seed 覆盖 report-only, 预计 realized 组合 >100.

Controlled local parameterization: `case_width` / `case_depth` / `case_height` / `pendulum_swing` / `door_open_upper` (independent), `rod_length` / `weight_travel` / `rod_radius` / `pivot_z` (equation-derived), `case_*` (conditional on `housing_style`). 全部在 `resolve_config` 中 clamp, 不会破坏 interface / clearance / joint origin.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural first; compat gate: `long_cabinet_rod ↔ floor_cabinet` | `slot_choices_for_seed` matches build |
| compatibility matrix | 一次一个 Slot 6 分支; `long_cabinet_rod` 强制 cabinet; 其他槽自由组合 | no floating, no collision, key axis 与 boss 匹配 |
| controlled local variation | 4 独立 scale + 4 derived | 比例变化不破 interface / clearance / motion |
| regression overrides | 无 | — |
| random sweep | `sweep-pipeline` 0-35 + corner | axis_realization; palette + case_form 可分 |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| Slot 1 housing_style | 4 | yes | yes | ③ 主体形态 slot, 4 form_subtype |
| Slot 2 pendulum_style | 4 | yes | yes | conditional gate: `long_cabinet_rod` |
| Slot 3 weight_style | 4 | yes | yes | |
| Slot 4 key_style | 4 | yes | yes | |
| Slot 5 weight_dof | 3 | yes | yes | 单-DOF 骨架 2 candidate + 双-DOF 1 candidate |
| Slot 6 case_extras | 5 | yes | yes | + leg multiplicity N=1..2 |
| Slot 7 palette_style | 5 | yes | yes | ⑥ 涂装 |

## Validator

- slot_choices_for_seed 返回 implemented module names.
- config_from_seed 对所有 seed 使用 deterministic procedural sampling.
- compat gate: `long_cabinet_rod` 仅 `housing_style == floor_cabinet`.
- regression overrides 稀疏 (当前为 0).
- controlled local scale params 在 `resolve_config` 中 clamp; 派生尺寸 (`rod_length` / `weight_travel` / `rod_radius` / `pivot_z`) 单-source.
- 恒定身份 joint 存在: 1 REVOLUTE pendulum_pivot + 1 或 2 PRISMATIC weight_slide + 1 CONTINUOUS key_axle.
- Slot 6 gated joint 存在: hinged_door → +1 REVOLUTE housing_to_front_door; internal_mechanism → +1 FIXED; separate_base → +1 FIXED; fold_out_legs → +N REVOLUTE `leg_hinge_{i}`.
- copied objects `stabilizer_leg_{i}` 遵循 naming & placement policy.
- 每个 movable child (pendulum / sliding_weight / winding_key / front_door / stabilizer_leg) 声明 `ctx.allow_overlap` for captured-pin / press-fit / hinge saddle 情形 (element-scoped when 可能).
- Rule 5: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)` + 每 mechanism 一个 targeted `ctx.pose({joint: value})` (待 template 实现).

## Reject cases

- 缺少 sliding tempo weight 或它不是 PRISMATIC (退化成纯单摆).
- 摆杆做成 CONTINUOUS 或 PRISMATIC 或 FIXED (失去 REVOLUTE 摆).
- winding key 做成 REVOLUTE 有角限 (退成拨杆).
- sliding_weight 不套在 rod 上 (脱离 rod / 与 rod 不 coaxial).
- `coarse_plus_fine` 两滑块共 PRISMATIC 或区间重叠导致穿模.
- `separate_base` 声明独立 base 却让 case 漂浮; `fold_out_legs` 脚不落地.
- `hinged_door` 门做成 PRISMATIC 滑盖或闭合不覆盖开口.
- mechanism/base/legs 悬空 (非 FIXED/REVOLUTE attached).
- 硬塞电子/数字节拍器、纯落地摆钟、天平仪表.

## 与相邻类别的边界

- vs `pendulum_clock` / `floor_clock`: 无沿杆可滑 tempo weight; 本类必有 PRISMATIC.
- vs `metronome_digital` (若存在): 有 CONTINUOUS 上弦 + REVOLUTE 摆; 数字类只有按钮.
- vs `single_revolute_hinge` / `tackle_box_with_simple_hinged_lid`: 主体是 fixed + 单 REVOLUTE 盖; 本类铰链 door 只是 gated 附件.
- vs `balance_scale` / `analog_meter`: 无沿臂可滑配速块 + 无 CONTINUOUS 上弦.
- vs `coaxial_rotary_stack`: 主体为连续旋转; 本类 CONTINUOUS 仅 winding_key 小件.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 继承 sibling slug `metronome` 的成熟规范; 差异仅在 palette 从 4→5 与 case_form 家族显式登记; sweep 验收在 P4 阶段用 `sweep-pipeline mechanical_metronome_with_pendulum` |
