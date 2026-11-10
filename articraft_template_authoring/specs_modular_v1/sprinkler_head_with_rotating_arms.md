# Sprinkler Head With Rotating Arms Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `sprinkler_head_with_rotating_arms` |
| template path | `agent/templates/sprinkler_head_with_rotating_arms.py` |
| test path (optional) | `tests/agent/test_sprinkler_head_with_rotating_arms_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (3 picture origin anchors + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

- adopted as module sources:
  - `rec_picturex_0611__sprinkler_head_with_rotating_arms__001__png_7ff2244508c64596895614e834e21aae` (perforated_disk_hub, straight radial arms, silver+orange nozzles)
  - `rec_picturex_0611__sprinkler_head_with_rotating_arms__002__png_70341112add34cc997a9ecd7802603c4` (threaded brass pillar, curved reaction arms, amber-grip nozzles)
  - `rec_picturex_0611__sprinkler_head_with_rotating_arms__003__png_c3c083e861614cb0a0f31263560e13d9` (wheeled green cast base, three-arm brass rotor, adjustable nozzle jets)
  - `rec_0611_sprinkler_head_with_rotating_a_var_arm_count_2` (N=2 straight radial arm variant, silver nozzles)
  - `rec_0611_sprinkler_head_with_rotating_a_var_arm_count_4` (N=4 brass curved arm variant)
  - `rec_0611_sprinkler_head_with_rotating_a_var_arm_form_curved_s` (③ curved-S reaction arm on wheeled base)
  - `rec_0611_sprinkler_head_with_rotating_a_var_arm_form_straight_radial` (③ straight radial arm baseline)
  - `rec_0611_sprinkler_head_with_rotating_a_var_base_ground_spike` (① ground-spike base with perforated hub head)
  - `rec_0611_sprinkler_head_with_rotating_a_var_base_tripod` (① three-legged tripod cast base)
  - `rec_0611_sprinkler_head_with_rotating_a_var_nozzle_count_2_per_arm` (multiplicity N=2 nozzles per arm)
  - `rec_0611_sprinkler_head_with_rotating_a_var_nozzle_motion_pivoting_jet` (② each nozzle is a separate REVOLUTE child)

## 核心身份

Sprinkler head with rotating arms = 由地面/水管进给的实用花园洒水器：静态 base（多孔盘 / 三脚架 / 地钉 / 带轮托架 / 螺纹立柱）承载一个绕竖直轴 REVOLUTE 或 CONTINUOUS 旋转的 rotor，rotor 上以 120°、90° 或 180° 等角向外伸出 N 根喷水臂（直辐管、弯曲反作用 S 管、直向 straight radial），每根臂末端带一个（或两个）朝上/朝外的喷嘴。核心运动至少包括 rotor 绕竖直中央轴的自由旋转；ground truth 场景中喷嘴可再绕臂轴独立 REVOLUTE 调向。这一竖直中央旋转 + 径向 N 臂拓扑就是本类别的定义特征。

边界：
- 不是 `ceiling_fan` / `box_fan` / 桌面风扇：本类是与地面/水管相连的洒水器，喷嘴向上/向外，非空气动力叶片。
- 不是 `traditional_windmill` / `wind_turbine`：那些是水平轴风叶塔身机；本类是竖直中央轴 + 短径向水臂。
- 不是 `overshot_waterwheel` / `turntable`：无水槽/无平台功能。
- 不是纯静态景观喷嘴（sprinkler head 必须至少有一个 rotor 关节）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_picturex_0611__sprinkler_head_with_rotating_arms__001__png_7ff2244508c64596895614e834e21aae` | `data/records/rec_picturex_0611__sprinkler_head_with_rotating_arms__001__png_7ff2244508c64596895614e834e21aae/revisions/rev_000001/model.py:L46-L343` | perforated_disk base with side hose connector; hub_shell + radial arm_tube + silver nozzle w/ orange insert; REVOLUTE base_to_rotor + per-nozzle REVOLUTE |
| S2 | `rec_picturex_0611__sprinkler_head_with_rotating_arms__002__png_70341112add34cc997a9ecd7802603c4` | `data/records/rec_picturex_0611__sprinkler_head_with_rotating_arms__002__png_70341112add34cc997a9ecd7802603c4/revisions/rev_000001/model.py:L56-L343` | threaded brass pillar connector + curved-S reaction arms via `tube_from_spline_points`; KnobGeometry hub; per-nozzle REVOLUTE |
| S3 | `rec_picturex_0611__sprinkler_head_with_rotating_arms__003__png_c3c083e861614cb0a0f31263560e13d9` | `data/records/rec_picturex_0611__sprinkler_head_with_rotating_arms__003__png_c3c083e861614cb0a0f31263560e13d9/revisions/rev_000001/model.py:L69-L456` | green cast_metal wheeled base + tripod-adjacent gusset geometry; adjustment_ring; rotor with tube-arm + inline nozzles |
| S4 | `rec_0611_sprinkler_head_with_rotating_a_var_arm_count_2` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_arm_count_2/revisions/rev_000001/model.py` | N=2 arm multiplicity evidence |
| S5 | `rec_0611_sprinkler_head_with_rotating_a_var_arm_count_4` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_arm_count_4/revisions/rev_000001/model.py` | N=4 arm multiplicity evidence |
| S6 | `rec_0611_sprinkler_head_with_rotating_a_var_arm_form_curved_s` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_arm_form_curved_s/revisions/rev_000001/model.py` | ③ curved_s arm form on wheeled base |
| S7 | `rec_0611_sprinkler_head_with_rotating_a_var_arm_form_straight_radial` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_arm_form_straight_radial/revisions/rev_000001/model.py` | ③ straight_radial arm form baseline |
| S8 | `rec_0611_sprinkler_head_with_rotating_a_var_base_ground_spike` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_base_ground_spike/revisions/rev_000001/model.py` | ① ground_spike base skeleton |
| S9 | `rec_0611_sprinkler_head_with_rotating_a_var_base_tripod` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_base_tripod/revisions/rev_000001/model.py` | ① tripod cast base |
| S10 | `rec_0611_sprinkler_head_with_rotating_a_var_nozzle_count_2_per_arm` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_nozzle_count_2_per_arm/revisions/rev_000001/model.py` | multiplicity nozzles_per_arm=2 |
| S11 | `rec_0611_sprinkler_head_with_rotating_a_var_nozzle_motion_pivoting_jet` | `data/records/rec_0611_sprinkler_head_with_rotating_a_var_nozzle_motion_pivoting_jet/revisions/rev_000001/model.py` | ② nozzle_pivot REVOLUTE separate-part nozzles |

## 槽位 + 候选模块表

### Slot A：base_form (① base skeleton family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `perforated_disk_base` | forked_anchor | S1 | L46-L115, L232-L274 | eligible if compatible | thick perforated disk plate + lower threaded connector + side hose port; hub bearing shaft at plate center; ⑤ perforation pattern via visuals; NON-rotating base part; single grounded body |
| `threaded_pillar_base` | forked_anchor | S2 | L79-L149 | eligible if compatible | tall threaded brass column; ribbed ridges as visuals; bearing cap on top hosts rotor bearing skirt; single grounded connector part |
| `wheeled_cart_base` | forked_anchor | S3 | L69-L127, L275-L343 | eligible if compatible | green cast_metal three-lobed plate with two side wheels; ribbed hose connector at back; central pedestal & bearing post; two CONTINUOUS wheel children |
| `tripod_base` | forked_anchor | S9 | L46-L112 (var_base_tripod) | eligible if compatible | three-legged cast pedestal; short bearing post at apex; single grounded body |
| `ground_spike_base` | forked_anchor | S8 | L60-L120 (var_base_ground_spike) | eligible if compatible | tapered ground spike + slim collar carrying bearing post; minimal footprint; single grounded body |

### Slot B：arm_form (③ Primary Form Family — arm envelope)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 | form_subtype |
|---|---|---|---|---|---|---|
| `straight_radial_tube` | forked_anchor | S1 / S7 | L167-L196, L282-L289 | eligible if compatible | straight cylindrical arm tube + optional stub spindle; 直向径向管；同 part tree (arms live on rotor visuals + separate nozzle children) | Volumetric Envelope Form |
| `curved_s_reaction` | forked_anchor | S2 / S6 | L215-L263 | eligible if compatible | 3D swept spline (S/reaction curve) via `tube_from_spline_points`; upturned tangential outlet; same rotor part + separate nozzle children | Macro Surface Construction |
| `tapered_upsweep` | forked_anchor | S3 | L394-L433 | eligible if compatible | mild upsweeping tapered tube (source polyline via `tube_from_spline_points`) + inline brass nozzle sockets; same rotor visual carrier | Volumetric Envelope Form |

### Slot C：nozzle_style (② moving-joint variant + ④ decoration)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_inline_nozzles` | forked_anchor | S3 | L227-L251 | eligible if compatible | 喷嘴几何作为 rotor 部件 visuals（无独立 nozzle 部件），rotor 单 REVOLUTE 关节；简单静止喷口 |
| `revolute_pivot_nozzles` | forked_anchor | S1 / S2 / S11 | S1 L303-L343; S2 L291-L341 | eligible if compatible | 每根臂一个独立 `nozzle_i` part + REVOLUTE joint (axis 沿臂径向 x)；每 nozzle 可小角度俯仰调向 |

### Slot D：arm_count (multiplicity axis)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `arms_2` | forked_anchor | S4 | full model.py | eligible if compatible | N=2 arms at 0°/180° |
| `arms_3` | forked_anchor | S1 / S2 / S3 | S1 L19 `ARM_ANGLES_DEG`; S2 L23 `ARM_COUNT=3` | eligible if compatible | N=3 arms at 120° |
| `arms_4` | forked_anchor | S5 | full model.py | eligible if compatible | N=4 arms at 90° |

### Slot E：nozzles_per_arm (multiplicity axis)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `noz_1` | forked_anchor | S1 / S2 / S3 | primary anchors | eligible if compatible | 每根臂末端 1 个喷嘴（origin default） |
| `noz_2` | forked_anchor | S10 | full model.py | eligible if compatible | 每根臂 2 个喷嘴（root + tip 两点） |

## 槽位图（slot graph）

pattern: `mixed` (parallel_children + multiplicity)

```text
[Slot A base_form (base part)]
  -- REVOLUTE base_to_rotor, axis (0,0,1), origin at central bearing -->
[synthesized rotor part driven by Slot B arm_form]
  -- for i in range(Slot D arm_count):
       arm i visuals attached to rotor at angle 2*pi*i/N
       -- for j in range(Slot E nozzles_per_arm):
            (Slot C = fixed_inline_nozzles) inline nozzle visuals on rotor
            (Slot C = revolute_pivot_nozzles) REVOLUTE arm_to_nozzle_{i}_{j}, axis (1,0,0) rotated by angle,
                child = nozzle_{i}_{j} part

(if Slot A = wheeled_cart_base) CONTINUOUS wheel_spin_L, wheel_spin_R about (1,0,0) attach two wheel children to base.
```

Interface contracts:
- `base ↔ rotor`: REVOLUTE joint. Parent visual = base's declared `bearing_post` / `bearing_shaft` / `bearing_cap` (each Slot A candidate publishes one); child visual = rotor's `hub_shell` / `bearing_skirt`. MatingContract mates the top face of the base bearing post (positive_z) to the bottom face of the rotor hub (negative_z). `allow_overlap` on shaft ↔ hub bore (captured shaft geometry).
- `rotor ↔ nozzle_i_j`: REVOLUTE axis along the arm's radial direction. Parent visual = arm socket (mesh cylinder at arm end); child visual = nozzle body cylinder that inserts into the socket. MatingContract references the socket face and nozzle ferrule face; captured-pin `allow_overlap` on ferrule ↔ arm tip.
- `base ↔ wheel_i` (wheeled_cart_base only): CONTINUOUS about (1,0,0); MatingContract references axle side face and wheel hub inner face.

## 每槽位 Module Emits / Interfaces

### Slot A / module `perforated_disk_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (single) | S1 / L46-L274 |
| internal joints | none (all base features are single-part visuals) | S1 |
| upstream interface | ground `-z` bottom face (world origin) | S1 |
| downstream interface | central `bearing_shaft` +z top face for `base_to_rotor` REVOLUTE | S1 L266-L274 |

### Slot A / module `threaded_pillar_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (single) | S2 |
| internal joints | none | S2 |
| downstream interface | `bearing_cap` +z top face for `base_to_rotor` REVOLUTE | S2 L143-L149 |

### Slot A / module `wheeled_cart_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`, `wheel_L`, `wheel_R` | S3 |
| internal joints | `wheel_spin_L`, `wheel_spin_R` (CONTINUOUS, axis (1,0,0)) | S3 L344-L352 |
| downstream interface | `bearing_post` top +z face for `base_to_rotor` REVOLUTE | S3 L285-L297 |

### Slot A / module `tripod_base` and `ground_spike_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (single) | S9 / S8 |
| internal joints | none | S9 / S8 |
| downstream interface | short central `bearing_post` +z top face for `base_to_rotor` REVOLUTE | S9 / S8 |

### Slot B / module `straight_radial_tube` (arm_form; runs inside rotor)
| emits | 描述 | 来源 |
|---|---|---|
| visuals on `rotor` | `arm_tube_{i}` straight cylinder (radial +x rotated by angle) + `arm_socket_{i}` short outer stub | S1 L167-L196 |
| internal joints | none (arms are rotor visuals) | S1 |
| downstream interface (per arm) | outer arm-tip face (radial direction) supplies mount point for nozzle child | S1 L303-L343 |

### Slot B / module `curved_s_reaction`
| emits | 描述 | 来源 |
|---|---|---|
| visuals on `rotor` | `arm_tube_{i}` spline `tube_from_spline_points` mesh (3D S curve upturning at tip) + `nozzle_socket_{i}` short cylinder | S2 L215-L263 |
| downstream interface (per arm) | endpoint direction unit-vector determines nozzle mount frame; per-arm direction supplied to Slot C | S2 |

### Slot B / module `tapered_upsweep`
| emits | 描述 | 来源 |
|---|---|---|
| visuals on `rotor` | `arm_tube_{i}` mild-sweep polyline `tube_from_spline_points`, upward tilt; `arm_socket_{i}` shoulder cylinder | S3 L394-L433 |
| downstream interface (per arm) | endpoint direction; nozzle sockets sit inline outboard | S3 |

### Slot C / module `fixed_inline_nozzles`
| emits | 描述 | 来源 |
|---|---|---|
| visuals on `rotor` | `nozzle_body_{i}_{j}`, `nozzle_cap_{i}_{j}`, `outlet_hole_{i}_{j}` (Cylinder visuals inline in the arm-tip direction) | S3 L233-L251 |
| internal joints | none | S3 |

### Slot C / module `revolute_pivot_nozzles`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nozzle_{i}_{j}` (one per arm-slot × nozzles_per_arm) | S1, S2, S11 |
| internal joints | `arm_to_nozzle_{i}_{j}` REVOLUTE, axis = arm radial unit vector (or (1,0,0) rotated by arm angle), origin at arm-tip mount, limits ≈ [-0.48, +0.48] rad (source S1) | S1 L330-L343 |

### Slot D / arm_count multiplicity
Rotor part is single (`rotor`); arm visuals + optional nozzle children are looped over `range(N)` where N ∈ {2, 3, 4}. All arms share one geometry helper; placement angle = `2π · i / N`; joint policy uniform.

### Slot E / nozzles_per_arm multiplicity
For `noz_1`: one nozzle at arm end. For `noz_2`: root nozzle at ~1/3 arm length and tip nozzle at outer end (S10). Same geometry helper; uniform joint policy per Slot C rules.

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_form` | enum | `perforated_disk_base` / `threaded_pillar_base` / `wheeled_cart_base` / `tripod_base` / `ground_spike_base` | `perforated_disk_base` | choice | procedural sampling | S1-S3, S8, S9 |
| `arm_form` | enum | `straight_radial_tube` / `curved_s_reaction` / `tapered_upsweep` | `straight_radial_tube` | choice | procedural sampling | S1-S3, S6, S7 |
| `nozzle_style` | enum | `fixed_inline_nozzles` / `revolute_pivot_nozzles` | `revolute_pivot_nozzles` | choice | procedural sampling; `revolute_pivot_nozzles` weighted higher because Rule 5 requires a non-FIXED joint beyond `base_to_rotor` when possible; both are legal | S1, S3, S11 |
| `arm_count` | int enum | `2 / 3 / 4` | `3` | choice | procedural sampling, weights (3, 6, 3) so N=3 dominates but 2/4 appear | S1, S2, S3, S4, S5 |
| `nozzles_per_arm` | int enum | `1 / 2` | `1` | choice | procedural sampling, weights (3, 1); N=2 requires `arm_length_scale ≥ 0.95` (inequality) | S10 |
| `palette_style` | enum | `gunmetal_silver_orange` / `warm_brass_amber` / `green_cast_brass` / `black_plastic_orange` / `bronze_polished` | `gunmetal_silver_orange` | choice | procedural sampling, uniform | S1, S2, S3 palette |
| `base_size_scale` | float | `[0.85, 1.15]` | 1.0 | independent | uniform sample, clamp | S1-S3 |
| `arm_length_scale` | float | `[0.85, 1.15]` | 1.0 | independent | uniform sample, clamp | S1-S3 |
| `hub_radius_scale` | float | `[0.90, 1.10]` | 1.0 | independent | uniform sample, clamp | S1-S3 |
| `nozzle_pivot_range_scale` | float | `[0.7, 1.1]` | 1.0 | independent | uniform sample, clamp; scales revolute nozzle limits ±0.48·s rad | S1 L340-L343 |
| (—) | constraint | — | — | inequality | `arm_count * 2 * (hub_r + arm_tip_pad) ≤ arm_reach_perimeter_slack` — arms at reach must clear neighbors; realized by ensuring `(2π/N)·arm_end_r > 2·arm_tip_half_width + 0.008` | closed-pose clearance |
| (—) | constraint | — | — | inequality | `nozzles_per_arm == 2 → arm_length_scale ≥ 0.95` (short arms cannot host two nozzles cleanly) | S10 |
| (—) | constraint | — | — | conditional | when `nozzle_style = fixed_inline_nozzles`, `nozzle_pivot_range_scale` is ignored (no revolute nozzles) | Slot C |

**连续尺寸采样契约** (`config_from_seed` → `resolve_config`):
1. 采样所有 `independent` 主尺度（uniform）;
2. 无 `equation` 从属尺度（本类别 arm 与 hub 保持独立结构自由度）;
3. 应用 `inequality` 检查：`arm_count=4` 且 `hub_radius_scale > 1.05` 时按比例回缩 `hub_radius_scale`；`nozzles_per_arm=2` 且 `arm_length_scale<0.95` 时把 `nozzles_per_arm` 降到 1；
4. 应用 `conditional`: `fixed_inline_nozzles` 忽略 `nozzle_pivot_range_scale`。

### 7.5 编译预算 / compile budget（必填）

自报预算：**每-seed ≤ 20s**（目标 8-15s 平均）。依据：源码使用 `tube_from_spline_points`（S2/S3）与 `mesh_from_cadquery`（S1/S3）；模板通过 `arm_form=straight_radial_tube` 保持 Cylinder 主导，仅 curved / tapered arm 分支进入 spline mesh。分档 tessellation：
- 小半径特征（nozzle body, bearing shaft, index rib）≤ 24 段。
- 主体英雄面（arm spline tubes，hub knob mesh）`radial_segments=16`，`samples_per_segment=10`。
- N 根臂共享同一个 `arm_mesh`（每种 arm_form 只烘一次，用 rpy 旋转放置）。
- N 个喷嘴共享同一个 `nozzle_body_mesh`。

超出预算先降 `radial_segments` / `samples_per_segment` 再迭代（`AUTHORING.md` §C）。

## Multiplicity / Copy Logic

- **arm_count 轴**：本小类核心 N 轴。
  - `count_param`: `arm_count`
  - `N_range`: {2, 3, 4}（源锚点覆盖 2/3/4；不外推更大 N）
  - sampling domain：`rng.choices((2,3,4), weights=(3,6,3), k=1)`（N=3 主流）
  - copied object：per-arm `arm_tube_{i}` 视觉 + arm_socket + 可选 nozzle 子件
  - naming：`arm_tube_{i}`、`arm_socket_{i}`、`nozzle_{i}_{j}` / `arm_to_nozzle_{i}_{j}`
  - placement：radial phase = `2π · i / N`
  - joint policy: 均匀 REVOLUTE（Slot C = revolute_pivot_nozzles）或全部无关节（fixed_inline_nozzles）；`allow_overlap` 声明每根臂末端 socket ↔ nozzle ferrule 的 captured-pin overlap（有 pivot 时）
  - source/gating：≤ arms_4 + arm 之间不允许自相撞（inequality 约束）
- **nozzles_per_arm 轴**：次要 N 轴。
  - `count_param`: `nozzles_per_arm`
  - `N_range`: {1, 2}（S10 支撑 2）
  - sampling domain: `rng.choices((1,2), weights=(3,1), k=1)`；`arm_length_scale<0.95` 时强制降到 1
  - copied object：per-nozzle `nozzle_{i}_{j}` 视觉/子件
  - naming：`nozzle_{i}_{j}`, `arm_to_nozzle_{i}_{j}`
  - placement：`t ∈ {0.65, 1.00}` 沿 arm 方向；j=0 靠近 arm 中段，j=1 在尖端
  - joint policy: same as Slot C
  - source/gating：≤ nozzles_per_arm=2，且必须 arm 足够长

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot A `base_form` × Slot C `nozzle_style` 决定图：无 pivot 时图 = base+rotor + optional 2 轮；有 pivot 时图额外增加 N×M 个 nozzle 节点 + N×M 条 REVOLUTE 边。所有 candidate `source_type=forked_anchor` (S1-S3, S8, S9, S11) |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`arm_count ∈ {2,3,4}`（默认 3），`nozzles_per_arm ∈ {1,2}`（默认 1） |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | `base_to_rotor` REVOLUTE (0,0,1) 恒定；`arm_to_nozzle_i_j` REVOLUTE 或不存在（Slot C 二选一）；wheeled_cart_base 时 `wheel_spin_L/R` CONTINUOUS (1,0,0)。全部 `forked_anchor` S1/S2/S3/S11 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色） | 有 | Slot B `arm_form` 就是 ③ 主体形态家族 slot，三候选：`straight_radial_tube` (Volumetric Envelope Form — 圆柱直管母线)、`curved_s_reaction` (Macro Surface Construction — 3D spline S 曲线扫掠改变类别内读法)、`tapered_upsweep` (Volumetric Envelope Form — 上翘 loft 母线)。所有 candidate `source_type=forked_anchor` (S1, S2, S3, S6, S7)。已登记为 slot |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Slot A 内部 host-conformal 细节：`perforated_disk_base` 上的孔阵列 + 六道径向 rib slot（S1 L60-L92）作为 base visual；`threaded_pillar_base` 上五道 thread_ridge Torus + 两道 gasket（S2 L96-L120）；`green_cast` 上的 gusset visual（S3 L116-L125）；`wheeled_cart_base` 的 tire groove。`record_only` 记录 + host-derived visual。装饰 counts (perforation ≥ 40, ridges ∈ {3,4,5}, gussets = 3)。派生顺序 ③ → ⑤ → ④（Rule 4） |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | scales: `base_size_scale [0.85,1.15]`, `arm_length_scale [0.85,1.15]`, `hub_radius_scale [0.90,1.10]`, `nozzle_pivot_range_scale [0.7,1.1]`. 运动包络：（a）`base_to_rotor` REVOLUTE axis (0,0,1) 开启方向绕竖直中心正/负，`[-π, +π]`；对应 `motion_test_plan`: sampled collision + targeted `ctx.pose({base_to_rotor: 1.0})` 验证 rotor 摆过 ≥60 mm。（b）`arm_to_nozzle_i_j` REVOLUTE axis 沿 arm 径向 (1,0,0) rpy 旋转 arm_angle，`[-0.48·s, +0.48·s]`；`motion_test_plan`: sampled collision + per-nozzle targeted `ctx.pose({arm_to_nozzle_0_0: 0.35})` 验证喷嘴 AABB 移动 ≥2 mm。（c）wheeled_cart_base `wheel_spin_L/R` CONTINUOUS axis (1,0,0)，`qc_samples` 使用默认 `{0, ±90°, 180°}`；不作 targeted pose，靠 sampled collision 通过。全程不得穿模。 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `palette_style` ∈ 5 档：`gunmetal_silver_orange` (S1: gunmetal/graphite/silver/safety_orange 金属+塑料), `warm_brass_amber` (S2: warm_brass/polished_brass/amber_grip/rubber), `green_cast_brass` (S3: green_cast_metal/brass/black_polymer), `black_plastic_orange` (源自 S1 palette 变体：dark_plastic/safety_orange), `bronze_polished` (aged bronze + silver). 材质大类覆盖：metal (5/5), plastic (2/5), rubber/painted (2/5) — ≥ ceil(0.5·5)=3 覆盖满足。全部 `record_only` |

**收尾自检**：本表每个"有"里列的取值必须在 `template batch` 的 0-9 seed 渲染里肉眼可见地出现。

## 采样与覆盖审计

总组合数：Slot A (5) × Slot B (3) × Slot C (2) × arm_count (3) × nozzles_per_arm (2) × palette_style (5) = **900** slot-choice tuples；加上 4 个连续 scale 后 seed 域接近无界。

seed_domain_policy：`procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 序贯采样 base_form / arm_form / nozzle_style / arm_count / nozzles_per_arm / palette_style（离散 enum + weighted N），然后 uniform 采样四个 scale；`resolve_config` 应用 §7 inequality / conditional 后返回 ResolvedConfig。`seed=0` 与其他 seed 一样通过 rng 采样（不作 anchor）。Regression overrides：默认无。
Topology target：900 离散组合中 sweep 0-35 只能命中一部分；1000-seed 探针预计 >=200 distinct tuple（受 nozzles_per_arm=2 稀有权重与 base_form 权重影响；weighted）。report-only。
Controlled local parameterization：`base_size_scale` / `arm_length_scale` / `hub_radius_scale` / `nozzle_pivot_range_scale` 独立采样后 clamp；不派生。跨部件依赖（`arm_count=4 & hub_radius_scale>1.05`）通过 inequality 回缩，不允许当独立自由变量各自采样。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 序贯 `rng.choice` on enums + `rng.choices` weighted on N + `rng.uniform` on scales; then `resolve_config` clamping | slot_choices_for_seed matches build choices |
| compatibility matrix | `nozzles_per_arm=2 → arm_length_scale ≥ 0.95` (fallback to N=1); `arm_count=4 & hub_radius_scale>1.05 → hub_radius_scale=1.05`; `nozzle_style=fixed_inline_nozzles → nozzle_pivot_range_scale ignored` | no floating nozzle, no arm-arm collision, no closed-pose failure |
| controlled local variation | 4 continuous scales listed above | proportions vary without breaking bearing engagement, arm reach, joint origin, category identity |
| regression overrides | none | reserved for reviewer-selected regression seeds |
| random sweep | seeds 0-15 (fast), 0-35 (final), corner seeds appended | axis_realization coverage of all 5 base_form × 3 arm_form × 2 nozzle_style × 3 arm_count × 2 nozzles_per_arm × 5 palette_style entries |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_form | 5 | yes | yes | ① 源锚点富足 |
| arm_form | 3 | yes | yes | ③ 形态家族 slot |
| nozzle_style | 2 | yes | no | ② 关节类型二值（本类别源锚点二选一） |
| arm_count | 3 | yes | yes | multiplicity N |
| nozzles_per_arm | 2 | yes | no | multiplicity N |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- slot_choices_for_seed returns implemented module names 且与 build 一致
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal module combinations（nozzles_per_arm=2 short-arm 强制降到 1；hub 半径与 arm_count 4 互斥回缩）
- optional regression overrides are sparse and justified（当前无）
- `run_tests` 里必须断言:
  - `base_to_rotor` 存在且 `ArticulationType.REVOLUTE`，`axis == (0,0,1)`，motion_limits ≈ [-π, +π]
  - `arm_count` 值与实际 `arm_tube_i` 视觉数量一致（Rotor part visuals）
  - `nozzles_per_arm` 与每根臂上的 nozzle 视觉/子件数量一致
  - 每根 arm 的 REVOLUTE nozzle joint（若 Slot C = revolute_pivot_nozzles）都存在，axis 为 arm radial 方向
  - `fail_if_isolated_parts()`、`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`、`fail_if_joint_mating_has_gap()` 全部执行
  - targeted `ctx.pose({base_to_rotor: 1.0})` 验证 rotor 摆过 ≥ 40mm 位移
  - 若有 revolute pivot nozzle，`ctx.pose({arm_to_nozzle_0_0: 0.35})` 验证喷嘴 AABB 变化 ≥ 2mm
  - captured-shaft `ctx.allow_overlap` 声明必须 element-scoped（bearing_shaft ↔ hub_shell / bearing_post ↔ hub_shell / arm_tube ↔ nozzle_ferrule）
  - closed-pose overlap 通过

## Reject cases

- rotor 不绕竖直轴旋转，或缺少 `base_to_rotor` REVOLUTE 关节
- arms 数量与 `arm_count` 不一致
- 单色（palette_style 未映射到 mats）或所有 visuals 用同一 material
- arm 相互碰撞（closed pose 或 sampled pose）
- Slot A = wheeled_cart_base 但缺少 wheel CONTINUOUS 关节
- Nozzle 悬浮或 nozzle 与 arm 之间无 MatingContract 支撑
- FIXED 关节用于装饰细节（违反 Rule 1）
- 把类别退化成风扇 / 风车 / 静态景观喷嘴

## 与相邻类别的边界

- 不该混入 `ceiling_fan` / `box_fan`：这些是空气动力叶片、轴水平/竖直方向不同，且无水连接语义。
- 不该混入 `traditional_windmill` / `wind_turbine`：塔身 + 水平轴风叶，不是竖直中央轴 + 径向水臂。
- 不该混入 `turntable`：无喷嘴/无水路语义，纯平台旋转。
- 不该混入 `overshot_waterwheel`：驱动方式（水槽）与形态完全不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；11 个 5-star 全读；三 origin anchors + 8 forked variants |

## 模板实现备注（可选）

- 所有 arm 共享一个 `_arm_visual(arm_form, ...)` helper，返回该 arm_form 的 `Mesh`（`tube_from_spline_points` 或 `Cylinder` 转 mesh），并用 `Origin(rpy=(0,0,angle))` 放置 N 份。
- 所有 nozzle 共享一个 `_nozzle_body_mesh(...)` helper（Cylinder 派生 + inline outlet + optional index_rib），由 palette 决定 material 名。
- palette 通过 `mats = {"body": model.material(...), "arm": ..., "nozzle_shell": ..., "insert": ..., "hose": ...}` 每 palette_style 一份；所有 `.visual(..., material=mats[key])`。
- captured-pin：`bearing_shaft` ↔ `hub_shell` element-scoped allow_overlap；`arm_socket_i` ↔ `nozzle_i_j.ferrule` element-scoped allow_overlap（当 revolute_pivot_nozzles）。
- 目前 not 使用 `_modular.assemble`：拓扑用条件分支直连（类似 traditional_windmill），因跨 slot 关节 (`base_to_rotor`) 需要 base 和 rotor part 都持有真实 bearing 视觉；`__modular__=True` 仅供 report。
