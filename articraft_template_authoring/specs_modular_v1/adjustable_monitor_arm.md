# Modular Spec — Adjustable monitor arm

## 元信息
| 项 | 值 |
|---|---|
| slug | `adjustable_monitor_arm` |
| template path | `agent/templates/adjustable_monitor_arm.py` |
| test path (optional) | `tests/agent/test_adjustable_monitor_arm_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear_chain support→riser→arm→head + multiplicity N arms on a shared pole) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 origins + 8 verified forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

A desk/wall-anchored articulated arm that carries a VESA monitor mount through several
real adjustment joints. Physical含义: an office monitor arm — an anchoring interface
(desk clamp / grommet stud / weighted base / wall plate) rises to a pole or pivot, one
or more revolute arm segments fold and swivel, and the terminal is a VESA plate or a
captured monitor head that tilts and rotates. 默认成熟域: single glossy/silver
gas-spring arm, but the vocabulary also covers multi-monitor poles and a sliding
height collar. 不该混入: laptop/tablet stands, keyboard trays, desk lamps, microphone
booms, camera tripods, static (non-articulated) TV wall brackets.

## 槽位 + 候选模块表

### Slot A：support_base（锚固接口，root part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| c_clamp | forked_anchor | rec_..._002 (origin B) | 002 L57-L117 | eligible if compatible | top saddle + splayed feet + clamp spine/jaw + screw/pad/thumb-bar + vertical pole + thrust collar; poled root |
| grommet_mount | forked_anchor | rec_..._var_base_grommet | grommet L87-L142 | eligible if compatible | top washer plate + pole socket + threaded stud + backing flange washer + hex lock nut + pole + collar; through-desk poled root |
| freestanding_base | forked_anchor | rec_..._var_base_freestanding | freestanding L82-L115 | eligible if compatible | broad oval base plate (Mesh ellipse) + tapered pole hub (Mesh loft) + 4 rubber feet + pole + collar; poled volumetric base |
| wall_mount | forked_anchor | rec_..._var_base_wall | wall L58-L114 | eligible if compatible | thin vertical wall panel + 4 lag-screw heads + bracket flange + rounded stub boss + vertical swivel pivot pin + collar; POLE-LESS, planar root, swivel axis offset in +x |

### Slot B：arm_skeleton（① 骨架 / 段数）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_segment | forked_anchor | rec_..._var_skeleton_single_seg | single L121-L180 | eligible if compatible | one cast `arm` shell swivel-sleeve→wrist clevis; joints base_swivel + wrist_tilt (NO elbow); 2 arm parts (arm, wrist_head) |
| two_segment | forked_anchor | rec_..._002 (origin B) | 002 L121-L233 | eligible if compatible | lower_arm + upper_arm with elbow clevis/eye; joints base_swivel + elbow_pitch + wrist_tilt; 3 arm parts |
| three_segment | forked_anchor | rec_..._var_skeleton_three_seg | three L167-L319 | eligible if compatible | lower_arm + mid_arm + upper_arm; adds mid_fold revolute; joints base_swivel + elbow_pitch + mid_fold + wrist_tilt; 4 arm parts |

### Slot C：head_terminal（③ 主体形态家族）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| stamped_vesa_plate | forked_anchor | rec_..._002 (origin B) | 002 L259-L288 | eligible if compatible | Planar Boundary Form — thin stamped backplate + 4 corner ears + center boss + 4 fastener heads; bare VESA plate |
| captured_monitor_head | forked_anchor | rec_..._001 (origin A) | 001 L399-L472 | eligible if compatible | Volumetric Envelope Form — rotation boss + vesa plate + screw/standoff grid + full monitor_body volume + screen inset + 4 bezels + rear ribs |

### Slot D：riser（② 关节类型 — 是否有 prismatic 升降）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_riser | forked_anchor | rec_..._002 (origin B) | 002 L290-L298 | eligible if compatible | no extra part; base_swivel REVOLUTE mounts arm root directly on the pole/pivot |
| prismatic_riser | forked_anchor | rec_..._var_joint_pole_prismatic | prismatic L123-L146,L327-L346 | eligible if compatible (poled single-arm only) | adds a `height_slider` collar (tube collar + swivel platform + lever pivot + clamp lever) riding PRISMATIC on the pole; base_swivel then mounts on the slider platform |

硬约束满足：support_base 4、arm_skeleton 3、head_terminal 2、riser 2 candidate；每个 slot ≥2
结构上不同的 candidate，皆有 forked_anchor + model.py 来源。无 world_knowledge_extrapolation
candidate（全部 source-backed）。尺寸/涂装差异不计为 candidate。

## 槽位图（slot graph）

pattern: mixed（linear_chain 主干 + multiplicity 分叉）

```
support_base --[REVOLUTE base_swivel, axis z, @ pole-top / stub-tip]--> arm_skeleton(root) --[...arm joints...]--> wrist_head --[REVOLUTE vesa_rotation, axis x]--> head_terminal
                    |
                    └─(riser=prismatic_riser)─> height_slider --[PRISMATIC height_slide, axis z]--> (slider platform) --[REVOLUTE base_swivel]--> arm_skeleton(root)

multiplicity(N arms): the arm_skeleton→wrist_head→head_terminal subchain is copied N times, each copy
gets its OWN base_swivel REVOLUTE on the shared support_base pole at a distinct height z_i and yaw φ_i.
```

跨 slot 连接点位：
- support_base → arm root: contact = the swivel sleeve/bearing wraps the pole/pivot pin (cylindrical
  captured pivot). Joint = REVOLUTE `base_swivel` axis z; origin on the pole top (poled) or stub tip (wall).
- riser insertion: support_base → height_slider is PRISMATIC `height_slide` axis z (collar bore wraps
  pole, captured); height_slider → arm root is the same REVOLUTE base_swivel on the slider platform.
- arm internal joints: elbow_pitch (y), mid_fold (y), wrist_tilt (y) — all clevis-pin captured pivots.
- wrist_head → head_terminal: REVOLUTE `vesa_rotation` axis x; the rotation bearing seats into the head backplate.
- 互斥 / gating: wall_mount ⇒ riser fixed, N=1（无 pole）; N≥2 ⇒ riser fixed + head=stamped_vesa_plate;
  prismatic_riser ⇒ N=1; captured_monitor_head ⇒ N=1.

## 每槽位 Module Emits / Interfaces

### Slot A / module c_clamp（and grommet / freestanding / wall share the interface）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `support_base` (single root part) | 002 L57 / freestanding L82 / grommet L87 / wall L58 |
| internal joints | none (all base geometry fused into one part per Rule 1) | — |
| upstream interface | root (grounded); exposes `swivel_origin` xyz + `has_pole` + pole radius/top-z | 002 L107-L117 |
| downstream interface | pole-top (poled) or stub-tip (wall) captured-pivot face for base_swivel | 002 L290-L298 / wall L287-L296 |

### Slot D / module prismatic_riser
| emits | 描述 | 来源 |
|---|---|---|
| parts | `height_slider` (collar + platform + lever) | prismatic L123-L146 |
| internal joints | `height_slide` PRISMATIC axis z (parent=support_base) | prismatic L327-L336 |
| upstream interface | collar bore wraps pole (captured) | prismatic L125 |
| downstream interface | swivel platform top → base_swivel origin | prismatic L129-L134,L338-L345 |

### Slot B / module two_segment（representative）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_arm`, `upper_arm`, `wrist_head` (prefixed `arm{i}_` when N>1) | 002 L121-L285 |
| internal joints | `elbow_pitch` REVOLUTE y @ (0.400,0,0) rpy -0.42; `wrist_tilt` REVOLUTE y @ (0.420,0,0) | 002 L297-L316 |
| upstream interface | `base_swivel_sleeve` tube at part origin wraps pole; base_swivel REVOLUTE z | 002 L121-L126,L290 |
| downstream interface | `rotation_bearing` on wrist_head @ (0.103,0,0); vesa_rotation origin (0.126,0,0) | 002 L247-L254,L317 |

### Slot C / module stamped_vesa_plate / captured_monitor_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `vesa_plate` (plate) or `vesa_mount` (monitor head) — prefixed when N>1 | 002 L259 / 001 L399 |
| internal joints | none (all head detail fused per Rule 1) | — |
| upstream interface | backplate at part origin; rotation bearing seats into it (captured) | 002 L260 / 001 L400 |
| downstream interface | none (terminal) | — |

活动件皆有 articulation 语义；不动细节（cable clips、bolt/screw heads、bezels、ribs、feet、
fasteners、lever）均写成宿主 part 的 `parent.visual(...)`，不作独立 FIXED part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| support_base | enum | c_clamp / grommet_mount / freestanding_base / wall_mount | c_clamp | choice | deterministic sampler | Slot A |
| arm_skeleton | enum | single_segment / two_segment / three_segment | two_segment | choice | deterministic sampler | Slot B |
| head_terminal | enum | stamped_vesa_plate / captured_monitor_head | stamped_vesa_plate | choice | deterministic sampler | Slot C |
| riser | enum | fixed_riser / prismatic_riser | fixed_riser | choice | deterministic sampler | Slot D |
| n_arms | int | 1 / 2 / 3 | 1 | choice(weighted) | small-N-heavy; §8 | multiplicity |
| pole_height | float | [0.42, 0.62] | 0.500 | independent | pole length; clamp | 002 L107 |
| arm_reach_scale | float | [0.86, 1.16] | 1.0 | independent | scales arm shell lengths + elbow/wrist offsets uniformly | 002 L127-L233 |
| head_size_scale | float | [0.90, 1.14] | 1.0 | independent | scales head plate / monitor body | 002 L259 / 001 L431 |
| (—) | constraint | — | — | conditional | wall_mount ⇒ riser=fixed_riser, n_arms=1 (no pole) | wall L58 |
| (—) | constraint | — | — | conditional | n_arms≥2 ⇒ riser=fixed_riser, head=stamped_vesa_plate (inter-arm clearance) | n2 L364-L387 |
| (—) | constraint | — | — | conditional | prismatic_riser ⇒ n_arms=1; captured_monitor_head ⇒ n_arms=1 | prismatic / 001 |
| (—) | constraint | — | — | inequality | per-arm base_swivel limit = ±(π/n_arms − 0.20) for n_arms≥2 → disjoint azimuth sectors (no inter-arm collision); N=1 keeps ±π | n2 L369-L371 |
| (—) | constraint | — | — | conditional | vesa_rotation limit = ±π for plate, ±0.85 for monitor_head (large head clearance) | 001 L515 |
| (—) | constraint | — | — | equation | effective_pole_len = pole_height + (n_arms−1)·arm_stagger(0.16) | n2 L342 |

采样契约：先采 independent（pole_height, arm_reach_scale, head_size_scale）→ 解析 conditional
（gating by base/N/head）→ 由 equation 派生 pole 长度与 arm 高度 → 由 inequality 收缩 swivel 上下限。
全部在 `resolve_config` 内求解。

### 7.5 编译预算 / compile budget
自报预算：**≤25 s/seed**（依据：arm shells / swivel sleeves / hinge eyes 用 cadquery `mesh_from_cadquery`
放样+布尔，库内实测重放样类 15-30s；N 个相同 arm 复用同一批共享 Mesh，故 N=2/3 不线性增长）。
分档 tessellation：cadquery tolerance 0.0008 / angular 0.08（沿用源）。所有 N 根 arm 共享同一组
预生成 Mesh 资产（sleeve / shells / eyes / neck），只生成一次。sweep `--compile-timeout 75`（≈3×）。

## Multiplicity / Copy Logic

有复制数量逻辑，1 根独立轴：

- `count_param`: `n_arms`
- `N_range`: 产品域 [1, 3]（source 覆盖 N=1 origins、N=2 fork、N=3 fork；suggested product [1,4]，模板
  实现并 sweep [1,3]）；sampling domain 权重档：N=1 高频（≈0.70）、N=2（≈0.20）、N=3 稀有（≈0.10）。
- copied object: the full arm subchain `arm_skeleton(root..wrist_head) + head_terminal` with its
  per-arm revolute sub-graph (base_swivel + elbow/mid_fold/wrist_tilt + vesa_rotation).
- naming: loop-indexed, stable prefix `arm{idx}_` for every part / visual / joint when N>1; empty
  prefix when N==1 (matches single-arm sources).
- placement: radial fan on the shared pole — arm i at yaw φ_i = i·(2π/N) and height z_i =
  top_arm_z − i·arm_stagger(0.16); loop-emitted via one shared helper, one shared Mesh set.
- joint policy: each copied arm gets its OWN base_swivel REVOLUTE on the shared pole; pole/base stays a
  single shared root. base_swivel range sector-limited to ±(π/N − 0.20) for N≥2 so sectors are disjoint.
- source / gating: N≥2 only on poled bases (c_clamp / grommet / freestanding), fixed_riser,
  stamped_vesa_plate head.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | arm_skeleton {single(2 parts, no elbow) / two(3 parts, elbow) / three(4 parts, +mid_fold)} + N-arm branch {1/2/3 copies on shared pole}; all forked_anchor (single/three/n2/n3 forks + origin B two_segment) |
| └ multiplicity | 同构件 ×N | 有 | n_arms ∈ [1,3]，权重 0.70/0.20/0.10，见 §8 |
| ② 关节类型 | 图不变换 type/轴 | 有 | REVOLUTE base_swivel(z) / elbow_pitch(y) / mid_fold(y) / wrist_tilt(y) / vesa_rotation(x)；PRISMATIC height_slide(z) via prismatic_riser。source-backed（origins + prismatic fork）；每种类型都在 sweep 出现（riser slot 保证 prismatic 被采） |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | head_terminal: stamped_vesa_plate = **Planar Boundary Form**（薄冲压板）vs captured_monitor_head = **Volumetric Envelope Form**（整块显示器体量+屏幕+bezel）; 另 support_base 形态族: C-clamp(骨架) / grommet(轴对称washer/nut) / freestanding(体量oval座) / wall(planar板)。source-backed origins+forks，登记进 slot_choices |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | cable clips、elbow/wrist bolt heads、VESA 75/100 fastener grid、corner ears、center boss、rubber feet、lag-screw heads、monitor bezels/rear ribs、clamp thumb-bar/knob。均为宿主 part flat 面上的 `parent.visual`，随 arm_reach_scale / head_size_scale 由宿主尺寸派生放置（③→⑤→④），不悬空 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | pole_height [0.42,0.62]、arm_reach_scale [0.86,1.16]、head_size_scale [0.90,1.14]。运动包络（每个非-continuous 关节）：base_swivel axis z, [−π,π]（N=1）/ ±(π/N−0.20)（N≥2）; elbow_pitch axis y [−0.75,0.85]; mid_fold axis y [−0.70,0.80]; wrist_tilt axis y [−0.85,0.85]; vesa_rotation axis x [−π,π] plate / [−0.85,0.85] monitor; height_slide axis z [−0.18,0.12]. motion_test_plan: 跑 `fail_if_parts_overlap_in_sampled_poses`（max_pose_samples 32, ignore_fixed）+ targeted `ctx.pose` 覆盖 swivel 摆臂 / elbow 抬降 / wrist 俯仰 / vesa 翻滚 / prismatic 升降。captured pin/sleeve overlaps 用 element-scoped `allow_overlap`。 |
| ⑥ 涂装 | 只改材质/颜色 | 有(record_only) | 材质大类：metal(brushed_silver pole/steel), painted(satin/glossy black, warm_gray powdercoat), dark_hardware, glass(monitor screen_glass on monitor head)。配色沿用源 5 材质；不作独立 candidate。 |

**收尾自检**：0-9 seed 渲染需肉眼见到：4 种 base 形态、1/2/3 段臂、单/多臂、plate vs 显示器头、
prismatic 升降臂；装饰贴合宿主；各关节全程不穿模。

## 采样与覆盖审计

总组合数（离散）：support_base 4 × arm_skeleton 3 × head_terminal 2 × riser 2 × n_arms 3 = 144，
经 compatibility gating（wall/N/monitor/prismatic 互斥）后合法组合约 ~70；连续 scale 另贡献覆盖。

seed_domain_policy：procedural_first（seed 0 不特殊；全 seed 走 `random.Random(seed)` 加权采样）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 4 个 slot
enum（support/skeleton/head/riser 均匀）+ n_arms（加权 0.70/0.20/0.10）+ 3 个连续 scale（均匀）。
`resolve_config` 解析 gating（见 §7 conditional/inequality），clamp 所有连续量，派生 pole 长度与 swivel
上下限。`slot_choices_for_seed` 导出 (support_base, arm_skeleton, head_terminal, riser, n_arms) 五元组。
无 curated/modulo 主表，无 regression override（初版）。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察，report-only；本类合法离散组合 ~70，
连续 scale 提升实际去重数，>=300 可达但不作 gate。

Controlled local parameterization：`arm_reach_scale`（缩放臂 shell 长度 + elbow/wrist 关节偏移，保持
接口不破）、`pole_height`（pole 长度 + swivel 高度派生）、`head_size_scale`（头部尺寸）。全部在
`resolve_config` clamp/派生；跨部件依赖（pole 长度↔N、swivel 高度↔pole、swivel 范围↔N、rotation 范围↔head）
以 equation/inequality/conditional 显式声明，不当独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot enums uniform + n_arms weighted + 3 continuous scales; gating in resolve_config | slot_choices_for_seed matches build choices |
| compatibility matrix | wall⇒fixed+N1; N≥2⇒fixed+plate; prismatic⇒N1; monitor⇒N1; else legal | no floating, no inter-arm collision, no pole-less prismatic |
| controlled local variation | arm_reach_scale / pole_height / head_size_scale, clamped | proportions vary without breaking captured pivots, clearance, joint origins, identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass; 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 4 | yes | yes | |
| arm_skeleton | 3 | yes | yes | |
| head_terminal | 2 | yes | no | Planar vs Volumetric form family — 结构不同 |
| riser | 2 | yes | no | revolute-only vs +prismatic |

## Validator
- slot_choices_for_seed returns implemented module names for all 5 axes incl. n_arms
- config_from_seed uses deterministic procedural sampling for all ordinary seeds incl. seed 0
- compatibility gating in resolve_config prevents illegal combos (pole-less prismatic, multi-arm monitor)
- no regression overrides
- controlled scales are clamped; cross-part relations (pole len, swivel z, swivel range, rot range) derived in resolve_config
- captured-pivot joints (base_swivel sleeve, elbow/mid/wrist pins, vesa boss, prismatic collar) grandfathered from mating-gap; element-scoped allow_overlap declared
- key joints have expected type/axis (base_swivel z, elbow/mid/wrist y, vesa_rotation x, height_slide z prismatic)
- copied arms follow arm{idx}_ naming + radial fan placement + disjoint swivel sectors

## Reject cases
- wall_mount that removes all articulation (→ static bracket): forbidden, keep full arm motion
- laptop tray / tablet clamp / keyboard tray terminal in head slot: category drift, blocked
- inter-arm collision on multi-arm pole: prevented by disjoint swivel sectors + head=plate
- prismatic riser on a pole-less base (wall): illegal, gated to poled single-arm
- captured_monitor_head with ±π rotation sweeping into the arm: rotation clamped to ±0.85 for monitor
- decoration built at constant size on a scaled shell (detached): derive placement from resolved shell dims
- floating base/head or unsupported islands: every visual rests/embeds on a supported neighbor

## 与相邻类别的边界
- 不该混入：laptop stand / tablet holder / keyboard tray（不是 VESA monitor 承载；缺 desk-anchor+arm 语义）
- 不该混入：desk lamp / microphone boom（终端非 VESA monitor，关节语义不同）
- 不该混入：static TV wall bracket（无关节，违反 must_keep articulation）
- 不该混入：camera tripod / shelf bracket（非桌面 VESA arm）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 初版；multi-arm 采用 disjoint swivel-sector 保证不穿模；prismatic/monitor 仅单臂 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | c_clamp | rec_..._002 | 002 L57-L117 | clamp root + pole |
| S2 | A | grommet_mount | rec_..._var_base_grommet | grommet L87-L142 | through-desk root |
| S3 | A | freestanding_base | rec_..._var_base_freestanding | freestanding L82-L115 | weighted volumetric base |
| S4 | A | wall_mount | rec_..._var_base_wall | wall L58-L114 | planar wall plate + stub pivot |
| S5 | B | single_segment | rec_..._var_skeleton_single_seg | single L121-L180 | one-piece arm, no elbow |
| S6 | B | two_segment | rec_..._002 | 002 L121-L233 | lower+upper+elbow |
| S7 | B | three_segment | rec_..._var_skeleton_three_seg | three L167-L319 | +mid_arm/mid_fold |
| S8 | C | stamped_vesa_plate | rec_..._002 | 002 L259-L288 | planar VESA plate |
| S9 | C | captured_monitor_head | rec_..._001 | 001 L399-L472 | volumetric monitor head |
| S10 | D | prismatic_riser | rec_..._var_joint_pole_prismatic | prismatic L123-L146 | pole height slider (PRISMATIC) |
```
</content>
</invoke>
