# Modular Spec — Aquarium

## 元信息
| 项 | 值 |
|---|---|
| slug | `aquarium` |
| template path | `agent/templates/aquarium.py` |
| test path (optional) | `tests/agent/test_aquarium_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (single `tank_frame` root; parallel children `substrate` / `filter` / lid; nested chain `hood → feed_flap`; plant-cluster multiplicity on `substrate`) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

Read: `..._001_...` (rect HOB hood/flap), `..._002_...` (rounded internal hood/flap plants),
`rec_aquarium_var_bowfront`, `rec_aquarium_var_cylinder`, `rec_aquarium_var_hexagon`,
`rec_aquarium_var_filter_canister`, `rec_aquarium_var_lid_bifold`, `rec_aquarium_var_lid_sliding`,
`rec_aquarium_var_plants_n2`, `rec_aquarium_var_plants_n7`. All 10 adopted.

## 核心身份

A transparent water-holding glass/acrylic tank for keeping aquatic life: a hollow glass basin
built from separately-held panes/walls (reads water-tight, not a solid block), a black plastic
rim frame + base trim, a top lid/hood (hinged, sliding, or split — usually with a feed opening),
in-tank/rim/floor filtration hardware, a gravel substrate bed, and rooted aquascape (plants +
rockwork). At least one real non-fixed joint (lid or feed flap) is always present.
Not to be confused with: an open round **fish bowl** (no frame/lid/equipment), a dry
**terrarium/vivarium**, an **aquarium stand/cabinet** (furniture), a **display case**, or a
plain **water tank / vase**.

## 槽位 + 候选模块表

### Slot A：body_form  (③ Primary Form Family — headline diversity axis, registered in `slot_choices`)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 (form_subtype) |
|---|---|---|---|---|---|
| `rect` | forked_anchor | `..._001_...` | L76-L183 | eligible if compatible | 4 flat glass Box panes + Box bottom, 4 straight base rails + 4 top rim rails + 4 corner posts. **Planar Boundary Form** (rectangular section). |
| `rounded` | forked_anchor | `..._002_...` | L70-L156 | eligible if compatible | Single hollow rounded-rect cadquery shell wall (fillet vertical edges) + bottom plate; soft-corner basin. **Volumetric Envelope Form** (rounded prism envelope). |
| `bowfront` | forked_anchor | `rec_aquarium_var_bowfront` | L60-L213 | eligible if compatible | rear/2 side flat panes + **cadquery convex bowed front panel** + curved front base/top rail. **Macro Surface Construction** (convex front). |
| `cylinder` | forked_anchor | `rec_aquarium_var_cylinder` | L45-L212 | eligible if compatible | annular cadquery glass wall + round bottom disc + base/top rings + radial ribs. **Volumetric Envelope Form** (circular column). |
| `hexagon` | forked_anchor | `rec_aquarium_var_hexagon` | L76-L221 | eligible if compatible | 6 glass wall Box panes (shared loop helper) + hex bottom plate + 6 base/6 top rails + 6 posts. **Planar Boundary Form** (hexagonal section). |

### Slot B：lid  (② joint / mechanism)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_hood` | forked_anchor | `..._001_...`, `..._002_...` | L258-L340 / L235-L321 | eligible if compatible | molded hood shell (shape follows body_form: rect box / round disc / hex prism) on a rear **REVOLUTE** (axis −X) + a nested **REVOLUTE** `feed_flap` covering a feed aperture (`hood → feed_flap`). |
| `sliding_cover` | forked_anchor | `rec_aquarium_var_lid_sliding` | L244-L300 | eligible if compatible (rect family) | flat glass canopy panel riding top-rim guide lips on a **PRISMATIC** joint (axis +Y); no feed flap. |
| `bifold_canopy` | forked_anchor | `rec_aquarium_var_lid_bifold` | L266-L328 | eligible if compatible (rect family) | two independent rear-hinged glass leaves (`lid_leaf_front` + `lid_leaf_rear`), each its own **REVOLUTE** (axis −X); front leaf on a center cross-brace, rear leaf on rear rim. |

### Slot C：filtration  (① skeleton / topology)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hob` | forked_anchor | `..._001_...` | L216-L256 | eligible if compatible (flat rear rim) | hang-on-back: rear-external housing Box + rim_hanger over the rear rail + intake tube down inside + strainer + outlet elbow. |
| `internal` | forked_anchor | `..._002_...`, `rec_aquarium_var_cylinder` | L172-L183 / L246-L292 | eligible if compatible | submerged housing Box clipped to the inside rear wall + down intake tube + strainer. |
| `canister` | forked_anchor | `rec_aquarium_var_filter_canister` | L329-L428 | eligible if compatible | floor-standing sealed canister Cylinder + lid + rigid plumbing (riser/arch over the rear rim/down-tube/strainer + spray bar). |

### Slot D：aquascape (multiplicity — plant clusters on `substrate`)

Not a structural slot; a per-seed multiplicity **N** copied on the `substrate` part. See §8.
Static rooted decoration (FIXED, no articulation) → emitted as `substrate` visuals (Rule 1).

硬约束满足：body_form 5 候选（③ 主体形态家族 slot，登记进 `slot_choices`）；lid 3、filtration 3；
每个 candidate 结构不同且有 `forked_anchor` 5-star 来源。support/base（rim frame + base trim）是每个
body_form module 自带的 module-local fixed structure（单候选，按 §4 折入 body_form，不单列 slot）。

## 槽位图（slot graph）

pattern: mixed

```
tank_frame (root, = Slot A body_form)
  ├─[FIXED, contact @ gravel/bottom_glass plane]──────────► substrate (Slot D plant multiplicity host)
  ├─[FIXED, contact @ rear-rail / inner-wall / rim-arch]──► filter (Slot C)
  └─ lid (Slot B):
        hinged_hood   : tank_frame ─[REVOLUTE −X @ rear hinge line]─► hood ─[REVOLUTE −X @ feed hinge]─► feed_flap
        sliding_cover : tank_frame ─[PRISMATIC +Y @ top-rim guide rails]─► hood
        bifold_canopy : tank_frame ─[REVOLUTE −X @ center brace]─► lid_leaf_front
                        tank_frame ─[REVOLUTE −X @ rear rim]────────► lid_leaf_rear
```

- 接口点位：所有 lid 铰接经 **hinge barrel 嵌入 tank 的 hinge_mount ledge**（captured-pin，~2 mm 嵌入，同时给
  几何接触保证连通）。sliding 经 **top-rim guide lip 承托**。substrate 经 **gravel_bed 落在 bottom_glass 上**。
  filter 经 **rear-rail hanger / inner-wall clip / over-rim arch** 接触。
- 跨 slot joint：lid 主铰 REVOLUTE 轴 −X 行程 [0, ~1.15 rad]（hinged/bifold）；sliding PRISMATIC 轴 +Y 行程
  [0, travel]；feed_flap REVOLUTE 轴 −X [0, ~1.3 rad]。substrate/filter 为 FIXED。
- 互斥/派生：lid 形态由 body_form 派生（rect→rect hood，round→disc hood，hex→hex hood）。
  `sliding_cover` / `bifold_canopy` 仅 rect-family（rect/rounded/bowfront）；cylinder/hexagon 强制 `hinged_hood`。
  `hob` 需平直后缘 → 不用于 cylinder。见 §9 compatibility matrix。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form (每个 module)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tank_frame` (root): glass panes/wall + `bottom_glass` + base frame + top rim (含命名 `top_front_rail`) + corner posts/ribs + 2 `hinge_mount` ledges on rear rim | S_form / 各 body_form 源 |
| internal joints | none (single part) | — |
| downstream interface | rear hinge line (hinge_y, hinge_z) + top rim footprint (给 lid)；rear-rail top / inner-wall / rim-arch 接触面（给 filter）；bottom_glass 顶面（给 substrate） | 各源 hood/filter/substrate 装配处 |

### Slot B / lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hood`(+`feed_flap`) / `hood` / `lid_leaf_front`+`lid_leaf_rear` | lid 源 |
| internal joints | hinged: `hood_to_feed_flap` REVOLUTE −X | `..._001/002_...` |
| upstream interface | hinge barrel 嵌入 tank `hinge_mount`（captured pin）/ guide-lip 承托 | lid 源 |

### Slot C / filter
| emits | 描述 | 来源 |
|---|---|---|
| parts | `filter` (single part, all hardware as visuals) | filter 源 |
| upstream interface | FIXED @ rear-rail hanger / inner-wall clip / over-rim arch 接触点 | filter 源 |

### Slot D / substrate + aquascape
| emits | 描述 | 来源 |
|---|---|---|
| parts | `substrate`: `gravel_bed` + gravel ridges + 2 rocks + N×(`plant_stem_{i}` + `plant_leaf_{i}_0/1`) | `..._002_...` plant loop |
| upstream interface | FIXED @ gravel_bed/bottom_glass 接触面 | 各源 substrate |

活动件均有 articulation 语义；plants/rocks/gravel/ribs/status buttons/led 为宿主 part visual（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | rect / rounded / bowfront / cylinder / hexagon | rect | choice | deterministic sampler | Slot A |
| lid | enum | hinged_hood / sliding_cover / bifold_canopy | hinged_hood | conditional | 合法集依 body_form（见 §9） | Slot B |
| filter | enum | hob / internal / canister | hob | conditional | 合法集依 body_form（cylinder 无 hob） | Slot C |
| plant_count | int | [2, 8]（测试 2/4/7 锚点，产品全程；小 N 高频、大 N 稀有） | 4 | independent | 加权采样后 clamp | §8 |
| palette_style | enum | 4 presets（glass tint / gravel / frame / led / plant） | classic_warm | choice | deterministic sampler | ⑥ |
| glass_h | float | [0.26, 0.40] | 0.34 | independent | clamp | 各源 GLASS_H |
| foot_w | float | [0.44, 0.60] | 0.52 | independent | clamp（rect-family 用） | 001/002 |
| foot_d | float | [0.28, 0.36] | 0.32 | independent | clamp（rect-family 用） | 001/002 |
| radius | float | [0.17, 0.24] | 0.20 | independent | clamp（cylinder R / hexagon 外接半径用） | cylinder/hex 源 |
| hood_open_scale | float | [0.85, 1.05] | 1.0 | independent | clamp（缩放铰行程上界） | 各源 |
| flap_open_scale | float | [0.85, 1.05] | 1.0 | independent | clamp | 001/002 |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | independent | clamp（× base travel） | sliding 源 |
| (—) | constraint | — | — | inequality | plant 根部半径 `< open footprint − margin`（不穿侧壁）；stem 顶 `< TOP_Z`（不穿 rim）；lid hinge upper 由 open_scale clamp 到不后穿 filter | 接口/clearance |

连续尺寸采样契约：先独立采 glass_h/foot_w/foot_d/radius/*_scale（均匀）→ 无 equation 从属 → 用上述
inequality 在 `resolve_config` 内 clamp（plant 半径、stem 高、hinge 行程）→ conditional 的 lid/filter 合法集
在采样前按 body_form 解析。

## 编译预算 / compile budget
自报 **≤ 20s/seed**（rect/hexagon 近乎纯 primitive；rounded/bowfront/cylinder 各 1–2 个 cadquery 布尔，
hood 视形态另 1 个）。分档 tessellation：cadquery 默认 tol；N 个 plant 复用同一 helper 几何。超预算先降
cadquery 精度。sweep `--compile-timeout 120`（≈6× 预算 watchdog）。

## Multiplicity / Copy Logic

- `count_param`: `plant_count`（rooted plant clusters）。
- `copied_object`: 1 plant cluster = 1 stem `Cylinder` (`plant_stem_{i}`) + 2 leaf `Box` (`plant_leaf_{i}_0/1`)。
- `N_range`: 产品域 **[2, 8]**；sampling domain 加权（`{2:.10, 3:.22, 4:.26, 5:.18, 6:.12, 7:.08, 8:.04}` — 小 N 高频、大 N 稀有）；测试锚点 N=2/4/7 对应三个 plant fork。
- `naming`: 稳定索引 `plant_stem_{i}` / `plant_leaf_{i}_{j}`；shared helper `_emit_plant`。
- `placement`: 沿 open footprint 前 ~240° 弧确定性分布，根部嵌入 `gravel_bed`，半径 clamp 到 footprint−margin
  （不穿侧壁玻璃），避开后部 filter 区；stem 高随 glass_h clamp（不穿 rim）。
- `joint policy`: FIXED（静态 rooted 装饰，visuals on `substrate`，无 articulation）。
- 次级 multiplicity（record_only，不单独 sweep）：hexagon 6 面板 loop（骑在 ③ hexagon 上）、cylinder 4 ribs、
  status buttons、gravel ridges。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | filtration 子装配拓扑：HOB(001) / internal(002,cylinder) / canister+plumbing(fork)；lid part 数：单 hood+flap / 单 sliding / 双 leaf。均 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | plant_count N∈[2,8]，见 §8（N=2/4/7 fork 锚点 + 权重档）。 |
| ② 关节类型 | 图不变，某边换 type/轴 | 有 | 主 lid 铰：REVOLUTE −X（hinged/bifold）vs PRISMATIC +Y（sliding）；nested feed_flap REVOLUTE −X；bifold = 两独立 REVOLUTE。均 source-backed，且 sweep 内 REVOLUTE+PRISMATIC 都出现。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | 5 候选（登记进 `slot_choices`）：rect(Planar Boundary) / rounded(Volumetric Envelope) / bowfront(Macro Surface) / cylinder(Volumetric Envelope) / hexagon(Planar Boundary)。全 forked_anchor。 |
| ④ 表面装饰 | 原型不变，叠表面细节 | 有(record_only) | led 灯条 / control_panel + 3 status_button / gravel ridges / rockwork / 叶形；宿主派生（贴在 hood 顶面、gravel 顶面），随 ③⑤ 共形。不伪装成 part/joint。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | glass_h[0.26,0.40]、foot_w[0.44,0.60]、foot_d[0.28,0.36]、radius[0.17,0.24]（见 §7）。运动包络：hood REVOLUTE −X [0, 1.15·open_scale]（前缘 +Z 抬升，不后穿 filter）；feed_flap REVOLUTE −X [0, 1.3·flap_scale]（+Z 抬升）；sliding PRISMATIC +Y [0, travel]（水平后移，不变高）；bifold 两 leaf REVOLUTE −X [0,1.15]（各自 +Z）。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses` + 每机构 targeted `ctx.pose(...)`（hood/flap/leaf 抬升、sliding 水平位移、独立性）；无需 qc_sample_values（默认 {0,lower,upper,mid} 足够）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 glass / plastic / painted-metal（frame）/ ceramic-rock；4 palette preset（glass 蓝/清、gravel 暖/蓝/黑、led 暖/aqua、plant 绿/品红）。材质大类覆盖 ≥ ceil(0.5×4)=2。 |

收尾自检：body_form 5 形态在 0-9 seed 拉得开；材质大类都出现；plants/led/rocks 贴合宿主面；lid 全程不穿模。

## 采样与覆盖审计

总组合数（含兼容 gating）：
- rect/rounded/bowfront：lid 3 × filter 3 = 9  → ×3 = 27
- cylinder：lid 1 × filter 2 = 2
- hexagon：lid 1 × filter 3 = 3
离散组合 = 27 + 2 + 3 = **32**；× plant_count 7 档 ≈ **224** slot-choice tuple 空间（report-only 成熟度观察）。

理由：body_form 与 lid 强耦合（lid 形态派生自 tank 顶开口），故对 cylinder/hexagon 只保留 source-backed 的
hinged 形态；对 cylinder 去掉需平直后缘的 hob。这些 gating 直接对应真实 5-star 装配，不是为凑数。

seed_domain_policy：procedural_first（`seed=0` 不特殊，与其它 seed 同走加权 deterministic sampler）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 body_form（均匀 5）→
按 body_form 解析 lid/filter 合法集再采 → plant_count 加权 → palette → 连续尺度；`resolve_config` clamp/投影
inequality。`slot_choices_for_seed` 返回 `(body_form, lid, filter, ("plant_count", f"n{N}"))`。无 regression override。
Topology target：224 tuple 空间偏小，因 body_form↔lid 兼容约束与 source-anchor 上限（真实只有这些装配）；report-only。
Controlled local parameterization：glass_h / foot_w / foot_d / radius / hood_open_scale / flap_open_scale /
slide_travel_scale，全部 `resolve_config` 内 clamp，且 plant 半径与 stem 高按 footprint / TOP_Z 派生 clamp，
不破坏 hinge 接口、清隙、支撑或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form 均匀 → lid/filter 条件合法集 → plant_count 加权 → palette → 连续尺度 | slot_choices_for_seed == build choices |
| compatibility matrix | sliding/bifold 仅 rect-family；hob 不用于 cylinder；lid 形态派生自 body_form；plant 半径/高 clamp | 无 floating / collision / 轴错 / max-mult / bulky / 可选 child 失败 |
| controlled local variation | 上列连续尺度，clamp+派生 | 比例变化不破接口/清隙/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初测；0-999 成熟度 | contract failures；axis_realization；viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 5 | yes | yes | ③ 主体形态家族 slot |
| lid | 3 | yes | yes | cylinder/hexagon 条件退化到 1（hinged），全局仍 3 |
| filter | 3 | yes | yes | cylinder 退化到 2（internal/canister） |
| aquascape (mult) | N∈[2,8] | yes | yes | 3 fork 锚点 N=2/4/7 |

## Validator
- slot_choices_for_seed returns implemented module names。
- config_from_seed 全 seed（含 0）走 deterministic procedural sampling。
- compatibility gating 阻止非法组合（sliding/bifold on cylinder/hex；hob on cylinder）。
- 无 regression override。
- controlled local scales 全 clamp，不破接口/清隙/joint origin/multiplicity。
- 关键接口：lid hinge barrel ↔ tank hinge_mount 接触；substrate gravel ↔ bottom_glass 接触；filter ↔ tank 接触。
- 关键关节 type/轴/行程：hood/leaf REVOLUTE −X；sliding PRISMATIC +Y；feed_flap REVOLUTE −X。
- copied plants 遵守命名/placement。

## Reject cases
- 实心不透明块体（不读作 hollow glass basin）。
- lid 或 feed flap 缺失全部非-FIXED 关节（变静态盒）。
- plant 穿侧壁玻璃 / stem 穿出 rim / plant 悬空不入 gravel。
- 开 hood 后穿 filter 或后墙（穿模）。
- cylinder/hexagon 上错配矩形 sliding/bifold 或方 hood。
- filter 悬空不接触 tank（canister 无 over-rim 接触）。
- 变成 fish bowl（去掉 frame/lid/filter）或 furniture stand。

## 与相邻类别的边界
- 不该混入：Fish_bowl（开口圆碗、无框/无盖/无设备）。
- 不该混入：Aquarium_stand/Cabinet（高柜家具底座；support 只保留集成 rim/base trim）。
- 不该混入：Terrarium/Vivarium（干养爬宠，无水基缸语义）。
- 不该混入：Display_case / Water_tank / Vase。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pass (sweep-pipeline verdict=pass, seeds 0-35 + corner clean, pass_rate=1.0, 41 distinct slot tuples) |
| reviewer notes | body_form↔lid 兼容 gating 与真实 5-star 装配一致；hinge 用 captured-pin barrel 嵌入 mount（grandfathered，无 MatingContract）。 |

## 模板实现备注（可选）
- 共享 helper：`_emit_plant`、`_emit_hinge_mounts`、`_lid_rear_edge`、rounded/hex/bowfront/round cadquery helpers。
- **Rear-clearance strip（关键几何约定）**：所有闭合 lid 的后缘停在 `_lid_rear_edge(g)=inner_rear_y-LID_REAR_GAP`
  之前，露出一条后置 filter strip（真实缸盖亦有后置滤材/线缆开口）。滤材硬件（HOB/内置 clip、canister over-rim
  plumbing）均落在此 strip 内或其后的 rim 上，故 lid 全程（含开合运动包络）不穿滤材。sliding travel 上界 clamp 到开盖时
  面板后缘不越过 strip；bifold 后叶铰移到该后缘（非后 rim）。
- **Hinged hood**：铰轴抬高到 `rim_top+0.034`，使 full-width hinge barrel（底 ~rim_top+0.026）越过 rim 高度的滤材
  hook/saddle（顶 ~rim_top+0.017）；barrel 经两 `hood_mount` ledge 嵌入 ~1.5mm（captured-pin 接触，<5mm）。hood 壳后中开
  一条 center slot（x±0.045）令居中滤材立管（intake/down-tube/arch）在任意开盖角都从槽中穿过、不被摆动的壳体扫到；壳侧翼经
  `hinge_arm` 连到 barrel。feed_flap 面板略小于 aperture，开合时穿孔而过不刮壳沿。
- **Rounded body**：用 4 片平板玻璃 pane + 圆柱角柱（rounded corner columns）实现，而非单一 hollow-shell mesh
  （后者按实心 mesh 参与碰撞、会把整个内部 substrate 判为 overlap）；cylinder/hex 的 ring/pane 构造本身即真空腔，OK。
- 无 water_volume 实心块（避免与独立 substrate/filter/plant part 的跨 part 穿模；源 001 亦无 water block）。
</content>
</invoke>
