# wrench_set — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wrench_set` |
| template path | `agent/templates/wrench_set.py` |
| test path (optional) | `tests/agent/test_wrench_set_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 2 |
| read_count | 2 |
| read_scope | all 5-star origins in category 0611/Wrench_set |
| source_index_policy | only adopted module sources are indexed below |

Sources: `rec_0611__wrench_set__001_png_867fcfc363504a5081e23c143d60d7fd` (paired
compact hex-key holders, 2×8 L-shaped hex keys, per-key PRISMATIC extraction),
`rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa` (single blue
molded holder, 8 combination wrenches in a graduated fan, per-wrench PRISMATIC
extraction along fanned axes).

## 核心身份

一套（**set**, N≥3）功能等价的手持扳手/hex-key/socket 类工具，被一个**共享
holder / rack / organizer / pouch / tray / rail** 统一收纳，每支工具可独立从收纳
体上取出（PRISMATIC 抽出为主，少量 REVOLUTE 翻折）。类别核心 = "多个工具 + 收纳
体 + 每支工具独立活动关节"三件套。工具本体呈现真实扳手/hex-key/socket 的几何原型
（长杆末端环眼/开口/六角/棘轮头），holder 呈现真实模塑塑料/发泡/皮革/金属轨的
面型 + 每工具一个 socket/slot/pocket。

不该混入:
- 单支扳手（Handtools_Wrench 的领域: 一个工具 + 可能一个可调节颚 REVOLUTE，
  不是 set）。
- 通用工具箱 / 工具车 / rolling toolbox（Handtools_Tool_cart, rolling_toolbox_
  with_telescoping_handle 的领域: 抽屉、handle、多层收纳、混合工具，不是纯扳手
  set）。
- 单支螺丝刀 / 多头驱动器 / 扭矩扳手（属于 Powertools_drill / Stationary_Pen 类
  或 handtool 单件）。
- 静态装饰墙挂无独立关节工具（不是本类别可接受的 set 骨架）。

## 槽位 + 候选模块表

### Slot A：`holder_form`（③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `paired_wedge_holder` | forked_anchor | rec_0611__wrench_set__001 | L104-L203 (`_holder_shell_shape`, `_add_holder`) | eligible if compatible | 两块 XZ 楔形塑料板通过中央 pair_clip FIXED 连接；共 2×N 或 N 个 socket 沿 X 排布；工具沿 +Z 竖直抽出；`form_subtype = Volumetric Envelope Form`（楔形体量） |
| `fan_organizer` | forked_anchor | rec_0611__wrench_set__002 | L33-L97, L161-L200 (`_holder_shape`, holder assembly) | eligible if compatible | 单块高矮墓碑轮廓的模塑板，顶部一个 handle 洞、中部宽 socket 梁、下方 fan 出 N 支工具；工具沿各自小角度 fan 方向 -Z 抽出；`form_subtype = Planar Boundary Form`（大平面 XZ 剪影） |
| `flat_rack_holder` | world_knowledge_extrapolation | anchors: 001 socket vocabulary + 002 slot fan + reviewer | in template (`_flat_rack_shape`) | eligible if compatible | 长条水平托盘 + N 个直立 socket 立柱，工具沿 +Z 直抽；`form_subtype = Macro Surface Construction`（薄板 + N 立柱构成宏观表面） |

Slot A 三个候选覆盖 Planar Boundary Form / Volumetric Envelope Form / Macro
Surface Construction 三大 ③ 原型；两个 forked_anchor + 一个受 (a) 现有源背书
socket 词汇 + (b) 同 part tree（holder + N tools）+ (c) 同 primitive 家族
（cadquery mesh + Box + Cylinder） + (d) 只改 planar/envelope/macro-surface 骨架
的 world_knowledge_extrapolation。三者共享同一 upstream interface（承地面 / 底部
FIXED），同一 downstream interface（每工具 socket_i 由 holder 传出）。

### Slot B：`tool_family`（③ 工具原型 + ② 关节语义）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hex_key_family` | forked_anchor | rec_0611__wrench_set__001 | L53-L102, L206-L291 (`_key_geometries`, `_add_key_set`) | eligible if compatible | 每工具 = 长直柄 + 弯头 + 短臂（L 形）三段扫掠或近似（回退 Box 拟合柄 + 短臂 Box + Sphere ball tip），PRISMATIC 沿 +Z 抽出；`form_subtype = Volumetric Envelope Form`（L 形三段体） |
| `combination_wrench_family` | forked_anchor | rec_0611__wrench_set__002 | L100-L158, L204-L256 (`_wrench_shape`) | eligible if compatible | 每工具 = 环眼 + 锥柄 + 开口 U 形颚（Ring + Shaft + Jaw 复合 mesh），PRISMATIC 沿各自 fan 方向 -Z 抽出；`form_subtype = Planar Boundary Form`（薄扁片，主要在 XZ 剪影） |
| `socket_family` | world_knowledge_extrapolation | anchors: 001 hex socket bore + 002 chrome ring + reviewer | in template (`_socket_shape`) | eligible if compatible | 每工具 = 短金属圆筒 socket（Cylinder + 六角内孔 hint via decoration），PRISMATIC 沿 +Z 抽出；同 holder + N 个 PRISMATIC 拓扑；`form_subtype = Volumetric Envelope Form`（短圆柱） |

Slot B 三个候选完全共享 slot 拓扑（holder + N 独立 PRISMATIC 子部件），只换单支工
具的 ③ Primary Form Family。socket_family 世界扩展受 001 六角孔词汇 + 002 抛光铬
金属家族背书。

### Slot C：`access_motion`（② 关节 + ⑤ 运动包络）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `straight_prismatic` | forked_anchor | rec_0611__wrench_set__001 | L273-L291 (per-key PRISMATIC axis=(0,0,1)) | eligible if compatible | 每工具沿 holder Z 轴笔直抽出，upper=0.045-0.05；共 N 个 PRISMATIC |
| `fanned_prismatic` | forked_anchor | rec_0611__wrench_set__002 | L234-L256 (per-wrench PRISMATIC rpy=(0,fan,0), axis=(0,0,-1)) | eligible if compatible | 每工具沿 holder Z 轴带小 fan 角 (±10°) 抽出，upper=EXTRACTION_TRAVEL；共 N 个 PRISMATIC |
| `tilting_rack` | world_knowledge_extrapolation | anchors: 002 fan axis + reviewer | in template (per-tool rpy tilt + shared axis) | eligible if compatible | 整支 holder 以固定倾斜角安装，工具沿 holder-local +Z 抽出（世界看像斜向抽），共 N 个 PRISMATIC；只影响 holder 安装 rpy + 每支工具的 rpy，同 part tree、同 N PRISMATIC 拓扑 |

Slot C 三种全部保持 "每工具 1 个 PRISMATIC" 的 ② 关节骨架（②本身不变），只改运动
轴 rpy 与 holder 姿态。fanned_prismatic 与 straight_prismatic 是骨架级别的 ⑤ 运动
包络差异；tilting_rack 是同一 ② 类别下的 rpy 世界差异。

### Multiplicity Slot：`tool_count`

见 §8。多重性轴 = 工具数量 N ∈ [3, 12]；两个原始锚点分别给出 2×8 (holder=001) 和
8 (holder=002) 样本。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
holder_form (Slot A, chassis)
  └── holder ── FIXED anchoring on ground (root or FIXED on optional base)
       ├── tool_0 ── PRISMATIC per Slot C axis + Slot B geometry
       ├── tool_1 ── PRISMATIC per Slot C axis + Slot B geometry
       ├── ...
       └── tool_{N-1} ── PRISMATIC per Slot C axis + Slot B geometry
```

- Slot A 定义 chassis = `holder` part（root），提供 N 个 socket 面（`socket_i`
  visual, 面法向 = tool 抽出方向）作为 downstream interfaces。
- Slot B 定义单支工具的 part 内 visual 群（steel / body mesh + optional Sphere
  tip + optional Cylinder ring）。同一 slot 内 N 支工具复用同一 mesh helper（性
  能约束）；每支单独 `model.part(f"tool_{i}")` 以支持独立 PRISMATIC。
- Slot C 决定每个 `tool_i_slide` 关节的 origin.rpy + axis + motion_limits.upper。
- 每个 tool socket 是 captured geometry（工具轴穿过 holder 的 socket 圆柱孔或
  slot slit），因此每个 PRISMATIC 关节 **omit MatingContract**（grandfathered，
  Rule 2 例外允许 pin-through-sleeve 情形），并搭配 element-scoped `allow_overlap`
  + `allow_isolated_part`（工具重力座在 socket 内为松配合视为独立部件）。
- Slot A `paired_wedge_holder` 内部保留 001 源的 `holder_pair_mount` FIXED（两半
  holder shell 硬连），不作为独立 slot；`fan_organizer` / `flat_rack_holder` 是
  单块 holder，无 FIXED。

## 每槽位 Module Emits / Interfaces

### Slot A / `paired_wedge_holder`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `holder`（yellow half + red half fused into 1 part via 2 mesh visuals + pair_clip visual） | S1 / model.py:L104-L203 |
| internal joints | 无（两 half 融合为同一 part 的多 visual，遵循 Rule 1） | derived |
| downstream interface | N 个 `socket_{i}` visual + socket_top_z(i) 提供每工具起点 | S1 / L273-L291 |

### Slot A / `fan_organizer`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `holder`（molded blue plate 单 mesh + raised_top_panel + N 个 slot_shadow visual） | S2 / model.py:L33-L97, L176-L210 |
| internal joints | 无 | derived |
| downstream interface | N 个 socket 中心 (x, y, SLOT_Z) + fan_angle_i | S2 / L204-L256 |

### Slot A / `flat_rack_holder`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `holder`（薄 Box base + N 个 Cylinder socket 立柱作为 host visual） | derived from S1 socket vocabulary + S2 plate |
| internal joints | 无 | derived |
| downstream interface | N 个 socket 顶面 (x, 0, base_top_z + post_h) | derived |

### Slot B / `hex_key_family`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tool_{i}`（i=0..N-1）；每 part = shank Box + short_arm Box + optional Sphere ball_tip | S1 / L53-L102, L235-L272 |
| internal joints | 无 | S1 |
| upstream interface | 每工具顶面（-Z 方向）via socket_top_z | S1 |

### Slot B / `combination_wrench_family`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tool_{i}`；每 part = `wrench_body` mesh_from_cadquery（ring+shaft+jaw） | S2 / L100-L158 |
| internal joints | 无 | S2 |
| upstream interface | ring 端顶部（+Z 方向） | S2 |

### Slot B / `socket_family`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tool_{i}`；每 part = Cylinder body + Cylinder bore mesh + optional decoration ring | derived |
| internal joints | 无 | derived |
| upstream interface | Cylinder 顶面 | derived |

### Slot C / `straight_prismatic`（对每支工具）
- 关节：`tool_{i}_slide` = PRISMATIC，axis=(0,0,1)，rpy=(0,0,0)，upper=0.045。
- 语义：源自 001 每 hex key 从 holder Z 轴抽出。

### Slot C / `fanned_prismatic`
- 关节：`tool_{i}_slide` = PRISMATIC，rpy=(0, radians(fan_i), 0)，axis=(0,0,-1)，
  upper=EXTRACTION_TRAVEL (0.024)。
- 语义：源自 002 每 wrench 沿 fanned axis 抽出。

### Slot C / `tilting_rack`
- 关节：`tool_{i}_slide` = PRISMATIC，rpy=(0, ±rack_tilt, 0)，axis=(0,0,1)，
  upper=0.04。整个 holder 由 root 承地面（可选 base_tilt 使得整支 rack 斜置）。

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `holder_form` | enum | `paired_wedge_holder` / `fan_organizer` / `flat_rack_holder` | `paired_wedge_holder` | choice | procedural sample | Slot A |
| `tool_family` | enum | `hex_key_family` / `combination_wrench_family` / `socket_family` | `hex_key_family` | choice | procedural sample | Slot B |
| `access_motion` | enum | `straight_prismatic` / `fanned_prismatic` / `tilting_rack` | `straight_prismatic` | choice | procedural sample; `fanned_prismatic` 只在 `holder_form==fan_organizer` 时保留 fan_angles；其他 holder 下 fanned 退化为 straight | Slot C |
| `tool_count` | int | [3, 12] weighted | 8 | independent (weighted) | 权重: `(3,4,5,6,7,8,9,10,11,12)` = `(0.06,0.10,0.13,0.16,0.14,0.14,0.10,0.08,0.05,0.04)` | §8 |
| `palette_style` | enum | 5 candidates (see below) | `chrome_yellow_plastic` | choice | procedural sample | ⑥ |
| `holder_width_scale` | float | [0.85, 1.20] | 1.0 | independent | 采样后 clamp | S1/S2 |
| `holder_height_scale` | float | [0.85, 1.15] | 1.0 | independent | | |
| `tool_length_scale` | float | [0.90, 1.15] | 1.0 | independent | | |
| `extraction_travel_scale` | float | [0.85, 1.20] | 1.0 | independent | | |
| `holder_tilt_deg` | float | [0, 12] | 0 | conditional | 仅 `tilting_rack` 时用（非 tilting_rack 强制 0） | derived |
| (—) | constraint | — | — | inequality | `N * socket_pitch(holder_width_scale) ≤ holder_max_width`；超出时按比例缩 pitch | 布局 |
| (—) | constraint | — | — | inequality | `tool_travel ≤ 0.60 * tool_shank_length` 防脱轨 | 抽出 |

**palette_style 候选（≥5）：**
- `chrome_yellow_plastic` — chrome tool + yellow plastic holder (source 001 yellow half)
- `chrome_red_plastic` — chrome tool + red plastic holder (source 001 red half)
- `chrome_blue_plastic` — polished chrome + molded blue plastic (source 002)
- `black_oxide_softgrip` — black oxide tool + dark gray soft-grip rubber holder
- `industrial_red_steel` — bare steel tool + industrial red powder-coat holder

### 7.5 编译预算
每 seed 目标 8-20s。理由：holder = 1 个 mesh_from_cadquery，tool ×N 共享同一 mesh
helper（helper 结果按 (tool_family, size_rank) LRU 缓存），Sphere/Cylinder/Box
primitives 主导；无重布尔雕刻。tessellation：small features ≤32 段，主 mesh ≤64
段。超预算先降精度。

## Multiplicity / Copy Logic

- `count_param`: `tool_count`
- `N_range`: [3, 12]（本小类的实产品域：hex-key set 常见 8-10；combination
  wrench 常见 3-15；socket 常见 6-24；限制上限 12 以控制 compile 时间）
- sampling domain (weighted, small-N-heavy):
  `weights = (0.06, 0.10, 0.13, 0.16, 0.14, 0.14, 0.10, 0.08, 0.05, 0.04)`
  for `N = 3..12`；测试小 N 高频，长尾稀有。
- copied object: 单支 `tool_{i}` part（内部 visuals 复用 shared mesh helper 结果）
- naming: `tool_0, tool_1, ..., tool_{N-1}`
- placement: 沿 holder-local X 均匀分布（socket_pitch = width/(N or width/1
  fallback)），Y 固定，Z = socket_top_z
- joint policy: 每工具单独 PRISMATIC，同 axis / rpy 规则由 Slot C 决定，upper
  由 `extraction_travel_scale` 缩放并 clamp

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 说明 |
|---|---|---|---|
| ① 骨架图 | 加/减 part 或边 | 有 | 骨架恒等 = `holder`（1 part）+ N × `tool_i`（N parts）+ N PRISMATIC 边；multiplicity 变 N（②的部分数量） |
| └ multiplicity | 同构 ×N | 有 | 见 §8：N∈[3,12] weighted 小 N 高频 |
| ② 关节类型 | 换 type/轴 | 有 | 全部 PRISMATIC；axis / rpy 分 straight_prismatic (axis=(0,0,1)) / fanned_prismatic (axis=(0,0,-1) + per-tool rpy fan) / tilting_rack (axis=(0,0,1) + shared rack tilt rpy)；三种在 sweep 中必现 |
| ③ 主体形态家族 | 换核心 part 形态原型 | 有 | Slot A 3 个 form_subtype：Volumetric Envelope Form (paired_wedge_holder), Planar Boundary Form (fan_organizer), Macro Surface Construction (flat_rack_holder)；Slot B 3 个 form_subtype：Volumetric Envelope Form (hex_key), Planar Boundary Form (combination_wrench), Volumetric Envelope Form/short cylinder (socket)。作为形态主导类的主 slot |
| ④ 表面装饰 | 叠加宿主表面细节 | 有（record_only 主导） | holder 上：size_tick_i / raised_top_panel / slot_shadow_i / rail 均由 holder mesh 派生宿主 z-face 逐 tool 生成；tool 上：ball_tip / bevelled ring end；覆盖 host-conformal 要求 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | scales: holder_width [0.85,1.20], holder_height [0.85,1.15], tool_length [0.90,1.15], extraction_travel [0.85,1.20]；关节包络：每 PRISMATIC upper ∈ [0.03, 0.06]；tilting_rack tilt ∈ [0, 12]°；motion_test_plan: 跑 sampled collision + 每关节 targeted `ctx.pose(0)` and `ctx.pose(upper)` on tool_0 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette_style；材质大类覆盖 metal (chrome / black_oxide / bare steel) + plastic (molded plastic 3 色) + rubber (soft-grip)，覆盖 ≥ ceil(0.5 × 5) = 3 |

## 采样与覆盖审计

总组合数：`3 × 3 × 3 × 10 (N buckets) × 5 (palette) = 1350` 名义组合（access_motion
在非 fan_organizer 下 fanned_prismatic 退化为 straight_prismatic，实际有效组合
≈ 3 × 3 × (2 + 1/3) × 10 × 5 ≈ 1050）。

seed_domain_policy: procedural_first。`config_from_seed(seed)`:
1. rng.choice each of holder_form, tool_family, access_motion, palette_style.
2. rng.choices tool_count with the weighted small-N-heavy tuple.
3. rng.uniform each independent scale ∈ its range.
4. `resolve_config` clamps scales, applies compatibility (access_motion×holder_form),
   and derives holder_tilt_deg.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rng-based enum + weighted N + clamped uniform scales | `slot_choices_for_seed` matches build; every (holder_form × tool_family × access_motion) triple realized in `axis_realization` |
| compatibility matrix | `fanned_prismatic` only fully realized on `fan_organizer`; on other holders fan is 0 (straight) | no floating tools, no fan orientation gap |
| controlled local variation | 4 scales (holder_width/height, tool_length, extraction_travel) + optional rack_tilt | proportions vary but socket pitch, joint origin, tool length stay coherent |
| regression overrides | none at initial spec; add only for confirmed corner seeds | — |
| random sweep | seeds 0-35 pipeline; batch preview 0-9 | axis_realization; visible palette variety, holder form variety |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| holder_form | 3 | yes | yes | ③ 主 slot |
| tool_family | 3 | yes | yes | ③ 副 slot |
| access_motion | 3 | yes | yes | ② + ⑤ |
| tool_count | 10 buckets | yes | yes | § multiplicity |

## Validator

- `slot_choices_for_seed` 返回 4 元组 `(holder_form, tool_family, access_motion,
  n{N})`，每项 ∈ 声明候选。
- `config_from_seed` 对全部 ordinary seeds 走 procedural 采样；`seed=0` 不特殊。
- Compatibility: `access_motion == fanned_prismatic` 且 `holder_form !=
  fan_organizer` 时，fan 内部退化为 0，slot_choices 仍报 fanned_prismatic（保
  留 axis 语义），axis 仍 (0,0,-1)。
- controlled local scales 全部 clamp 到声明范围；socket_pitch 由 holder_width 与
  N 联合派生并保证 tool 间隙 ≥ 0.006m。
- InterfaceSpec: N 个 tool_i 与 holder 之间的 PRISMATIC socket 关节属 captured
  geometry，omit MatingContract；element-scoped `allow_overlap` (holder socket
  visual vs tool body visual) + `allow_isolated_part` on each tool.
- 每个 tool_i_slide 是 PRISMATIC；`fail_if_parts_overlap_in_sampled_poses` 覆盖
  全部工具关节。
- Targeted `ctx.pose` on tool_0: rest vs upper 位移 > 0.6 × upper。

## Reject cases

- 只造单支扳手（等价于 Handtools_Wrench），无 set / holder。
- Holder 与 tool 之间用 FIXED 而非 PRISMATIC（丢失关键 identity 语义）。
- N < 3（不构成 set）或 N > 12（compile 超预算 + 视觉过挤）。
- Tool `.visual` 未由 palette 参数驱动的常量颜色（Rule 4 违反 + 违反 palette 契约）。
- 用 LatheGeometry 源被降级为 Box/Cylinder 而未保 mesh（Rule 3 违反）。
- 每工具漂浮无 socket 支撑（Contract 3 disconnected islands）。
- `access_motion=fanned_prismatic` 强套 `paired_wedge_holder` 导致 fanned 工具轴
  与 holder socket 面法向不共线 → 未处理 compat gating。

## 与相邻类别的边界

- 不该混入 `Handtools_Wrench`：单支扳手 + 单 REVOLUTE 可调节颚（本类必 N≥3 + N
  个 PRISMATIC）。
- 不该混入 `Handtools_Tool_cart` / `rolling_toolbox_with_telescoping_handle`：这
  些是抽屉 + handle 的 tool cart，含轮子 + 抽屉，不是 fixed holder。
- 不该混入 `Powertools_*`：power tool 有 motor 壳体 + trigger，不是被动扳手。
- 不该混入通用容器 (`Container_Box` 等) 或 `Kitchen_Knife_set`（厨房刀 + shears，
  刀刃形态不同，且要求 shears REVOLUTE pivot）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Initial spec author-generated 2026-07-12; ready for template implementation & sweep. |
