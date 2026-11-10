# wine_rack — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wine_rack` |
| template path | `agent/templates/wine_rack.py` |
| stage | `SPEC_APPROVED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed`（rack_frame → mount is a chain; bottles are a multiplicity axis on the rack; orientation is a swept rack-level branch parameter） |

## 5 星样本阅读摘要

11 个 5★ 记录已同步至 `data/records/`（全部 rating=5）：

- **origin_design** = `rec_wine_rack__wine_rack__001_png_3489ff2270b645d89354800da6b888f0` — compact_angled_wine_rack: 单个 `rack_frame` 部件 + 4 个 `bottle_i` 部件；4 个 `rack_to_bottle_i` PRISMATIC 关节，`axis=(0,0,-1)`, upper≈0.055；每层含 shelf/notch/rear stop/pair 三角肋，含 tube 型 `neck_cradle_i` 环；bottle 由 body + shoulder(loft) + narrow_neck + foil_cap + label_band + base_heel 组成。
- **rack_topology** 三支 `honeycomb`（两片打了 4 个六角孔的 cheek 板）/ `diagonal_x_grid`（每层两根交叉 slat + 前横档承 notch）/ `vertical_tower`（两根直立立柱 + 顶盖 + 底 apron，SHELF_ANGLE 保留 28° 但 topology 强调 upright）。
- **bottle_count** 三支 `3/6/9`：均沿用 origin 的斜梯，SHELF_CENTERS 由 `-0.040 + i*0.030, 0.120 + i*0.125` 生成，架子/rail 长度由端点导出。
- **mount** 两支 `wall_mounted`（YZ back plate 取代下 wedge、无 base plate）/ `countertop`（origin 之等价 — 保留底板 + wedge，被视作短家用桌面版）。
- **expansion** `rotating_carousel`：多出一个 `base_pedestal` 部件（bearing hub） + `rack_carousel_pivot` REVOLUTE 竖轴关节 `[-π, π]`，rack 无平底板而下 wedge 直接坐在 pedestal hub 顶。
- **orientation** `upright_presentation`：SHELF_ANGLE 降至 5°，SHELF_CENTERS 竖直堆 4 层（`z ≈ 0.16, 0.52, 0.88, 1.24`），rack_frame 加了 plinth。

共同 invariant：架子始终是 **一根 wood_frame 单 part** + N 个 bottle part，bottle 与 rack 之间是 PRISMATIC 沿架子外法向的滑出关节；bottle 视觉 6 件；每 bottle 一个 `neck_cradle_i` tube 视觉在 rack 上作 U 形抱扣。materials 一致：`warm_walnut_wood / dark_end_grain / brushed_steel / natural_cork` + 3 玻璃 + 4 label + 4 foil 十四种。

## 核心身份

- **core_identity**：一件把多支酒瓶物理保持在多层瓶槽内的家具尺度支架；至少一层 shelf/slot + 每瓶的 neck retention（notch/cradle/pillar 之一） + 与地面/墙面/桌面的稳固基座；每支瓶子可以沿槽外滑（PRISMATIC）或整体旋转（REVOLUTE）。
- **must_keep**：`rack_frame` 单体、多支独立 `bottle_i` 部件（≥3 支）、每瓶 PRISMATIC 抽出关节、瓶颈 U 型 cradle 视觉、稳定基座接地/接墙/接台面 – 与图片可辨识为 wine rack。
- **must_not_become**：
  - **wine cabinet**（有立柜、门、抽屉的封闭家具）→ 我们无 door/hinge，无封闭腔体。
  - **plain shelf**（无 bottle retention、无每瓶自己的 cradle/notch）→ 我们必须存在每 bottle 一个 `neck_cradle_i` 且每架层有 notch/cradle-groove。
  - **bar cart**（带轮台车、放整个 tray 的家具）→ 我们无轮子、无 tray-serving surface。
  - **bottle crate**（一次成型堆叠木箱）→ 我们必须有 leaning/upright/carousel 的架状显式 skeleton。
- image_evidence：`picture/0611/Wine_rack/001.png`
- parent_evidence：`rec_wine_rack__wine_rack__001_png_3489ff2270b645d89354800da6b888f0`

## 槽位 + 候选模块表

三个 slot（rack_frame、mount、orientation） + 一个 multiplicity 轴（bottle_count）；每个 slot 至少 2 个候选，rack_frame 4 个覆盖 ①/③。

### Slot A：`rack_frame`（轴 ①/③ — 支架 skeleton / Primary Form Family）

| candidate | ③ Form Family | source record | key parts/joints/helpers |
|---|---|---|---|
| `angled_ladder` (default) | Planar Boundary（斜梯） | `rec_wine_rack__wine_rack__001...` L60-168, `_build_wood_frame` | base plate + lower_wedge + 2 rails(-72°) + N shelves + notch + rear stop + N pairs triangular ribs |
| `honeycomb_cheeks` | Macro Surface Construction（穿孔面片） | `rec_0611_wine_rack_var_rack_topology_honeycomb` L60-187 | base plate + wedge + 2 cheek plates × N hex windows + shelves + short ledges |
| `vertical_tower` | Volumetric Envelope（立塔） | `rec_0611_wine_rack_var_rack_topology_vertical_tower` L60-175 | base plate + 2 upright posts + apron + top cap + horizontal shelves + ribs |
| `diagonal_x_grid` | Planar Boundary（X 交叉板） | `rec_0611_wine_rack_var_rack_topology_diagonal_x_grid` L60-230 | base plate + wedge + 2 inclined rails + N shelves each = (2 crossed slats + front bar w/ notch) + rear stop + ribs |

### Slot B：`mount`（轴 ①/② — 接地/接墙 + 是否 REVOLUTE 底轴）

| candidate | source record | key parts/joints/helpers |
|---|---|---|
| `floor_stand` (default) | origin — flat base plate + lower wedge | 单 rack_frame，无额外 part，纯家具坐地 |
| `countertop_plinth` | `rec_0611_wine_rack_var_mount_countertop` — 短平台 | 同 floor_stand（visual 差异：无 wedge，短 plinth） |
| `wall_mount_plate` | `rec_0611_wine_rack_var_mount_wall_mounted` L60-90 | rack_frame 后置 YZ 板 (0.228×0.580×0.018) 代替 base plate；无独立 part |
| `turntable_pedestal` | `rec_0611_wine_rack_var_expansion_rotating_carousel` L60-186 | 独立 `base_pedestal` part（foot disc + hub loft），REVOLUTE `rack_carousel_pivot` axis=(0,0,1) [-π, π] |

### Slot C：`orientation`（轴 ③ — 瓶身姿态）

| candidate | source record | key parts/joints/helpers |
|---|---|---|
| `angled_lay_down` (default) | origin — SHELF_ANGLE=28°, SHELF_CENTERS 斜升 | rack_frame + N shelves 倾斜 |
| `upright_presentation` | `rec_0611_wine_rack_var_orientation_upright_presentation` L60-80 | SHELF_ANGLE=5°, SHELF_CENTERS 竖直堆 (z≈0.16..1.24) + 短 plinth |

### Multiplicity 轴：`bottle_count` (N ∈ [3, 9])

| N | source record | 说明 |
|---|---|---|
| 3 | `rec_0611_wine_rack_var_bottle_count_3` | 最小 sample |
| 4 | origin — 4 层 | origin 的原生 N |
| 6 | `rec_0611_wine_rack_var_bottle_count_6` | 中值 |
| 9 | `rec_0611_wine_rack_var_bottle_count_9` | 长尾（用 pitch 参数 SHELF_PITCH_X=0.030, SHELF_PITCH_Z=0.125） |

其余 N ∈ [3, 9] 由 pitch 参数插值。

## 槽位图（slot graph）

```
                        [rack_frame]  ── carrier (root or hangs off mount) ──
                             │
                             ├── multiplicity: bottle_count (N)
                             │       └── N × PRISMATIC(rack → bottle_i) : 沿架子外法向 axis=(0,0,-1)
                             │
                             └── slot: orientation  (branch parameter — 改变 SHELF_ANGLE / SHELF_CENTERS)

                        [mount]
                             ├── floor_stand / countertop_plinth / wall_mount_plate : 无新 part, 直接烧进 rack_frame mesh
                             └── turntable_pedestal : 独立 base_pedestal part; REVOLUTE(base_pedestal → rack_frame) axis=(0,0,1)
```

`orientation` 是一个 rack-level 分支参数（改变 shelf 姿态 + 排布），本身不新增 part、也不新增关节，故实现上放进 `rack_frame` 内部；spec 里保留为独立 slot 是为了 §8.5 ③ 轴显式声明。

## 每槽位 Module Emits / Interfaces

### Slot A / module `angled_ladder`
- parts emitted：`rack_frame`（一个 wood_frame 视觉 + N cradle tube 视觉）
- internal articulations：0
- interfaces：`downstream`（top face 用于 bottle 挂接；bottle 视为 multiplicity children）
- source：origin `_build_wood_frame` L60-168。

### Slot A / module `honeycomb_cheeks`
- parts emitted：`rack_frame`（同名）
- internal articulations：0
- source：`rec_0611_..._honeycomb` `_build_wood_frame` L60-187；hex_window = 六边形 polyline extrude 后 cut。

### Slot A / module `vertical_tower`
- parts emitted：`rack_frame`
- 顶盖 + 底 apron + 双立柱 + 水平 shelf；不使用 wedge。
- source：`rec_0611_..._vertical_tower` L60-175。

### Slot A / module `diagonal_x_grid`
- parts emitted：`rack_frame`
- 每层 = 两根 X 交叉 slat + 前横档带 notch；仍用倾斜 rail 承 shelf。
- source：`rec_0611_..._diagonal_x_grid` L60-230。

### Slot B / module `floor_stand`
- 无独立 part；只是让 rack_frame 底部包含 `Box(0.340,0.240,0.025)` 平板 + wedge。
- internal articulations：0；rack_frame 是 root。

### Slot B / module `countertop_plinth`
- 无独立 part；rack_frame 底部换成 `Box(0.260,0.240,0.028)` + 短 plinth；无 wedge。
- source：`rec_0611_..._mount_countertop`。

### Slot B / module `wall_mount_plate`
- 无独立 part；rack_frame 后端加 YZ 板 `Box(0.018,0.228,0.580) @ x=-0.155, z=0.34`。
- source：`rec_0611_..._mount_wall_mounted` L60-90。

### Slot B / module `turntable_pedestal`
- 新增 `base_pedestal` part（foot disc + inset ring + hub）；rack_frame 不长平底板。
- articulation: `rack_carousel_pivot` REVOLUTE，parent=base_pedestal，child=rack_frame，origin=(0,0,0.055)，axis=(0,0,1)，limits=[-π, π]。
- MatingContract: parent face = pedestal `weighted_turntable_foot` top（+Z），child face = rack_frame `wood_frame` 底（-Z）。因是 pin-through-hub 结构（hub 陷入 wedge 内），采用 grandfathered 无 MatingContract 形式 + `allow_overlap(pedestal, rack, elem_a="weighted_turntable_foot", elem_b="wood_frame", reason="hub embedded in rack wedge")`.
- source：`rec_0611_..._expansion_rotating_carousel` L163-309。

### Slot C / module `angled_lay_down`
- 改变 `SHELF_ANGLE=math.radians(28°)`, `SHELF_CENTERS` = pitch 斜升。
- 不新增 part、不新增 joint。

### Slot C / module `upright_presentation`
- 改变 `SHELF_ANGLE=math.radians(5°)`, `SHELF_CENTERS` = pitch 竖直（z=0.16, 0.52, 0.88, 1.24）+ 底部短 plinth。
- 不新增 part、不新增 joint。
- source：`rec_0611_..._orientation_upright_presentation` L22-80。

### Multiplicity（bottle）
- 每 bottle 一个独立 part `bottle_i`：6 个 Cylinder / loft 视觉（glass_body, tapered_shoulder, narrow_neck, foil_cap, label_band, base_heel）+ index-0 加 `cork_tip`。
- 每 bottle 一个 PRISMATIC 关节 `rack_to_bottle_i`，parent=rack_frame，child=bottle_i，axis=(0,0,-1)（在 rack 局部帧），upper 在 `[0.04, 0.07]` 之间，lower=0。
- MatingContract：captured-pin/neck-in-cradle 类型 — 采用 `allow_overlap(bottle_i, rack_frame, elem_a="foil_cap", elem_b="neck_cradle_i", reason="metal U-cradle locally compresses around foil")` + 无 MatingContract。

## 参数范围汇总

| 参数 | 类型 | 范围/取值 | 说明 |
|---|---|---|---|
| `rack_frame` | enum | angled_ladder / honeycomb_cheeks / vertical_tower / diagonal_x_grid | Slot A |
| `mount` | enum | floor_stand / countertop_plinth / wall_mount_plate / turntable_pedestal | Slot B |
| `orientation` | enum | angled_lay_down / upright_presentation | Slot C |
| `bottle_count` | int | 3..9 (采样：3, 4, 5, 6, 7, 9；三分位偏 4-6) | Multiplicity |
| `palette_style` | enum | warm_walnut_wood / dark_end_grain / black_metal_frame / industrial_matte_grey / painted_cream | ⑥ palette（≥4，此处 5 种） |
| `shelf_length_scale` | float | 0.90..1.15 | ⑤ |
| `shelf_width_scale` | float | 0.90..1.10 | ⑤ |
| `shelf_pitch_scale` | float | 0.90..1.12 | ⑤，控制 SHELF_PITCH_Z |
| `slide_upper_scale` | float | 0.85..1.10 | ⑤，控制 PRISMATIC upper（clamp 到 [0.04, 0.07]） |
| `carousel_yaw_scale` | float | 0.80..1.00 | ⑤，控制 REVOLUTE 上/下限（clamp 到 [±π*0.85, ±π]） |

### 7.5 编译预算 / compile budget（必填）

- 目标 ≤ 20 秒/seed（sweep-pipeline `--compile-timeout 120` 三倍 watchdog）。
- 措施：
  - `_build_wood_frame` 全部用 cadquery boolean，最后一次 `.clean()`；六角/X-slat/hex_window 均用 polyline extrude；每 rack 仅一个 `mesh_from_cadquery` 调用。
  - bottle 全部原生 primitive（Cylinder），`_build_shoulder` loft 只算一次（`shoulder_mesh` shared）。
  - neck cradle 使用 `tube_from_spline_points` `radial_segments=12, samples_per_segment=8`。
  - N=9 时同样只做一次 rack mesh，仅循环 9 次 shelf boolean（origin 已验证 N=9 sample 通过 5★）。

### 8. Multiplicity / Copy Logic

- **count_param**: `bottle_count`（int，range [3,9]）
- **copied object**: `bottle_i` — 独立 part，identical 6 visuals + 1 PRISMATIC 关节
- **placement**: rack 的 SHELF_CENTERS 由 `SHELF_PITCH_X, SHELF_PITCH_Z` 与 anchor 生成：`(cx_0 + i*pitch_x, cz_0 + i*pitch_z)`，N=9 参考 `rec_..._bottle_count_9`
- **naming**: `bottle_{i}`, `rack_to_bottle_{i}`, `neck_cradle_{i}` (rack 的 visual name)
- **joint policy**：所有 PRISMATIC 关节 axis 相同（rack-local -z），limits identical after 一次全局 clamp

### 8.5 视觉多样性 6 轴考察

| 轴 | 是否声明 | 实现 |
|---|---|---|
| **① skeleton / topology** | ✅ | Slot A 4 candidates（angled_ladder / honeycomb / tower / x_grid）+ Slot B turntable_pedestal 新增 REVOLUTE 结构 |
| **② joint / mechanism** | ✅ | 基础 PRISMATIC(bottle) 恒存在；turntable_pedestal 引入 REVOLUTE `rack_carousel_pivot` |
| **③ Primary Form Family** | ✅ | Slot A 覆盖 Planar Boundary（angled_ladder, x_grid）/ Macro Surface Construction（honeycomb）/ Volumetric Envelope（tower）+ Slot C（angled vs upright） |
| **④ 表面装饰** | ✅ | 每 bottle 有 label_band + foil_cap（host-conformal，长度/半径从 body 派生）；无 rack 层贴花（rack 是裸木） |
| **⑤ proportion / size / travel** | ✅ | shelf_length_scale / width_scale / pitch_scale / slide_upper_scale / carousel_yaw_scale；REVOLUTE 限位覆盖 ±150°..180°；PRISMATIC upper 0.04..0.07 |
| **⑥ material / palette / finish** | ✅ | 5 种 `palette_style`：warm_walnut_wood, dark_end_grain, black_metal_frame, industrial_matte_grey, painted_cream；每 palette 有 rack 色、cradle 金属、瓶体玻璃、标签、酒帽 5 组配色 |

`motion_test_plan`：
- PRISMATIC `rack_to_bottle_0`：在 `upper` 姿态下断言 bottle body 仍与 rack x-轴有 ≥0.12m 重叠（`expect_overlap(x, min=0.12)`）、y 方向仍完全落在 rack 内部（`expect_within(y)`）、`narrow_neck` 与 `neck_cradle_0` 仍 xz 重叠 ≥0.025。
- REVOLUTE `rack_carousel_pivot`（当选中 turntable_pedestal）：在 `upper=π*0.85` 姿态下断言 rack z 轴顶端相对静止 pedestal 中心的 xy 偏移接近 rack 的 xy 尺寸的一半（旋转生效）。
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)` 因 N 可达 9 关节。

## 采样与覆盖审计

- `config_from_seed(seed)`：deterministic `random.Random(seed)` 采样每个 slot + `bottle_count` 从 (3,4,5,6,7,9) 加权 (0.15, 0.28, 0.20, 0.20, 0.10, 0.07)、`palette_style` uniform、scales `uniform`。
- 兼容性 gating（`resolve_config`）：
  - `mount=turntable_pedestal` 与 `orientation=upright_presentation` — 二者独立可组合，无冲突（旋转塔亦真实存在）。
  - `mount=wall_mount_plate` 强制 `bottle_count ≤ 6`（墙上不挂 9 瓶，避免 rack 过高越出面板；且防止 sweep 里 bottle_count=9 + upright 出现 z>2m）。
  - `orientation=upright_presentation` 强制 `bottle_count ≤ 6`（每层 ~0.36m 竖直堆积，防止 z>2.2m 超尺）。
  - `mount=turntable_pedestal` 强制 `rack_frame ∈ {angled_ladder, honeycomb_cheeks, diagonal_x_grid}`（vertical_tower 在 pedestal 上会过高失稳，且原 sample 中无此组合）。
- 拓扑覆盖：36 seeds 至少覆盖 rack_frame 全部 4 candidate、mount 全部 4、orientation 两个、bottle_count 每个都出现 ≥1。
- `slot_choices_for_seed(seed)` 返回 `(("rack_frame", ...), ("mount", ...), ("orientation", ...), ("bottle_count", f"n{N}"))`。

## Validator

`run_wine_rack_tests(model, config)`:
1. rack_frame 部件存在且 visuals 中含 `wood_frame` + N 个 `neck_cradle_i`。
2. bottle 数量 = N；每 bottle 视觉包含 `glass_body`、`tapered_shoulder`、`narrow_neck`、`foil_cap`、`label_band`。
3. 存在 N 个 PRISMATIC `rack_to_bottle_i`，upper ∈ [0.04, 0.07]。
4. `expect_contact(bottle_i, rack, elem_a="foil_cap", elem_b=f"neck_cradle_{i}", tol=0.0005)`。
5. `expect_overlap(bottle_i, rack, elem_a="narrow_neck", elem_b=f"neck_cradle_{i}", axes="xz", min=0.025)` on `upper` pose。
6. 若 `mount=turntable_pedestal`：额外 base_pedestal 部件 + 1 REVOLUTE 关节；`ctx.pose({pivot: 2.5})` 断言 rack 顶端 xy 相对 rest 偏移显著。
7. `fail_if_parts_overlap_in_sampled_poses(32, ignore_fixed=True)`。
8. rack 世界高度：
   - `angled/floor+angled_lay_down` z_max ∈ [0.55, 1.20]
   - `vertical_tower / upright_presentation` z_max ≤ 2.20
9. materials 至少含 `warm_walnut_wood` (or palette 主色) + `brushed_steel` (cradle) + 3 玻璃系 + label + foil。

## Reject cases

- rack 视觉退化为一块无 shelf 的平板（`shelf_count < 3`）→ reject。
- bottle 部件退化为 Box 或缺 `narrow_neck` 视觉 → reject。
- 缺失 PRISMATIC `rack_to_bottle_i` → reject（不再是 wine rack）。
- rack 与 bottle 出现广义 `allow_overlap(part, part)`（非 element scoped）→ reject。
- `mount=turntable_pedestal` 但无 REVOLUTE → reject。
- rack 高度 > 2.3m 或 x/y > 0.60m → reject（超家具尺度）。

## 与相邻类别的边界

- **wine_cabinet**：有柜门/hinge/封闭腔体、内部含 shelf 但外壳封闭。本类**无 door**、rack 骨架可视。
- **plain shelf**：无 bottle-specific retention。本类必须每层有 `neck_cradle_i`（U 形抱扣或 notch）。
- **bar_cart**：有 caster 轮 + tray。本类无轮子。
- **bottle_crate**：无 skeleton（就是个箱子）。本类必须有 leaning/tower/x_grid/honeycomb 之一。

## 审核记录

- 2026-07-12：P3 subagent 手写（scaffold 未产 slot）。11 个 5★ record 全部检查（origin + 10 变体），slot 分解基于 rack_topology / mount / orientation / bottle_count 四轴；③ Primary Form Family 通过 rack_frame slot 4 candidate 覆盖；palette 提供 5 种。

## 模板实现备注

- 单文件：`agent/templates/wine_rack.py`。
- 导出：`WineRackConfig`, `ResolvedWineRackConfig`, `config_from_seed`, `resolve_config`, `build_wine_rack`, `build_seeded_wine_rack`, `slot_choices_for_seed`, `run_wine_rack_tests`, `__modular__ = True`。
- 复用 origin 的 `_oriented_box`, `_neck_cradle_path`, `_build_shoulder` 三个 helper；rack_frame 分支放进四个 `_build_frame_<candidate>` helper。

## Module Source Index

| slot / module | 5★ record | 关键行 |
|---|---|---|
| A/angled_ladder | rec_wine_rack__wine_rack__001... | L60-168, L211-378 |
| A/honeycomb_cheeks | rec_0611_..._honeycomb | L60-187 |
| A/vertical_tower | rec_0611_..._vertical_tower | L60-175 |
| A/diagonal_x_grid | rec_0611_..._diagonal_x_grid | L60-230 |
| B/floor_stand | rec_wine_rack__wine_rack__001... | L63-70 (base plate) |
| B/countertop_plinth | rec_0611_..._mount_countertop | L60-99 |
| B/wall_mount_plate | rec_0611_..._mount_wall_mounted | L60-90 |
| B/turntable_pedestal | rec_0611_..._expansion_rotating_carousel | L163-309 |
| C/angled_lay_down | rec_wine_rack__wine_rack__001... | L22-33 |
| C/upright_presentation | rec_0611_..._orientation_upright_presentation | L22-40, L61-100 |
| Multiplicity bottle_count=3 | rec_0611_..._bottle_count_3 | full |
| Multiplicity bottle_count=6 | rec_0611_..._bottle_count_6 | full |
| Multiplicity bottle_count=9 | rec_0611_..._bottle_count_9 | L22-70 |
