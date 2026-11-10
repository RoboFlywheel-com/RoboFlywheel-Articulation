# universal_joint — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `universal_joint` |
| template path | `agent/templates/universal_joint.py` |
| test path (optional) | `tests/agent/test_universal_joint_template.py` (not written; sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern=mixed`: the primary slot `joint_topology` selects one of **two disjoint
part-joint skeletons** (single cross = parallel children off a spider root;
double-cardan = a `middle → spider → end` chain replicated left/right). The other
slots (`yoke_form`, `middle_member`, `shaft_connection`) are topology-family-gated
modifiers of the selected skeleton.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subcategory (2 origins + 8 forked anchors) |
| source_index_policy | only adopted module sources are indexed below |

Reading summary (verified against each `model.py`):

- **S1 `rec_build-a-reference-accurate-compact-steel-double-_…f7e21841`** (001.png,
  `compact_double_cardan`). Root `middle_section` (double-yoke forging + 2 pressed
  bearing cups per side) → two `*_spider` parts (forged cross core + 4 stepped
  journals each) → two `*_section` end sleeve-yokes (open forged cheeks + hollow
  sleeve + 2 cups each). **FOUR** REVOLUTE journal joints (`left/right_primary` about
  Y at the middle stations, `left/right_secondary` about Z at the end yokes),
  bounded ±16° with a baked rest pitch/yaw. Journals are captured in cups
  (element-scoped `allow_overlap` + `expect_overlap`/`expect_within`/`expect_contact`).
  Cadquery meshes: `_bearing_cup_shape` L31-54, `_spider_core_shape` L57-62,
  `_journal_shape` L65-77, `_end_section_shape` L80-127, `_middle_section_shape`
  L130-177, `_add_spider_visuals` L180-200, joints L344-395.
- **S2 `rec_picturex_0611__universal_joint__002…884db283`** (002.png,
  `universal_joint_002`). Root `spider` (spherical `forged_hub` + `journal_x` +
  `journal_y`) with **TWO** shaft yokes `shaft_yoke_a` (−X sleeve, Y bearings) and
  `shaft_yoke_b` (+Z sleeve, X bearings) as parallel children. **TWO** REVOLUTE
  joints `spider_to_yoke_a` (axis Y) / `spider_to_yoke_b` (axis X), both origin at
  spider center, ±0.55 rad, orthogonal. Each yoke carries `shaft_yoke`, `cap_pos/neg`
  (needle-bearing cups), `retaining_ring_pos/neg`, `cap_dimple_pos/neg`, `bore_liner`,
  `mouth_edge`. Helpers `_cylinder/_annulus/_fuse/_bearing_cap` L18-75,
  `_yoke_a_shape` L78-103, `_yoke_b_shape` L106-131, joints L408-437.
- **S3 pin_and_block** (`rec_0611_universal_joint_var_joint_topology_pin_and_block_joint`
  from S2): identical spider+2-yoke skeleton and joints; the spider center becomes a
  chamfered machined `pivot_block` (box+chamfer) instead of the spherical hub
  (`hub_shape` L179-185).
- **S4 sc_forged_open** (`…var_yoke_form_forged_open_yoke` from S2): yoke head becomes
  a lofted slender tapered cheek pair with the shaft necked well back; longer
  journals. `_yoke_a_shape` L78-115 (loft), `_yoke_b_shape` L118-153.
- **S5 sc_enclosed_block** (`…var_yoke_form_enclosed_block_yoke` from S2): yoke head is
  a closed rectangular block with a cross-window + coaxial bearing bores.
  `_yoke_a_shape` L78-111, `_yoke_b_shape` L114-145.
- **S6 splined_shaft** (`…var_connection_splined_shaft` from S2): the hollow sleeve
  shaft is replaced by a solid 12-tooth external spline root; open-arm head kept.
  `_splined_shaft_x` L58-74, `_splined_shaft_z` L77-93, `_yoke_a_shape` L116-140.
- **S7 dc_enclosed_block** (`…var_end_enclosed_block_yoke` from S1): end section is a
  heavy monobloc block yoke fused to the sleeve. `_end_section_shape` L80-142.
- **S8 dc_flange** (`…var_end_flange_yoke` from S1): end section swaps the hollow
  sleeve for a 4-bolt companion flange behind the forged cheeks.
  `_end_section_shape` L80-…(flange L88-113).
- **S9 centering_ball** (`…var_middle_centering_ball` from S1): middle forging adds a
  spherical `centering_socket` + polished `centering_ball` + `centering_ball_stub`
  (all visuals on `middle_section`, not parts). `_middle_section_shape` L130-181,
  `_centering_socket_shape` L184-196, `_centering_ball_shape` L199-201,
  `_centering_ball_stub_shape` L204-216, build L294-333.
- **S10 intermediate_shaft** (`…var_middle_intermediate_shaft` from S1): middle is a
  turned round shaft with two independent forked yokes at each end.
  `_middle_section_shape` L130-192.

## 核心身份

A **shaft-coupling universal joint** transmitting rotation across an angled axis via
a **cross/spider (Hooke joint)** or a **centered/uncentered double-cardan**, with
**real non-fixed revolute journal joints** between the spider(s) and the end yokes.
Defining features that must survive every slot combo: orthogonal spider journals
captured in yoke bearing cups; the revolute journals remain articulable
(yoke stays captured while articulated); visible shaft-connection interfaces
(sleeve bore / spline / flange). Default mature domain: compact machined/forged
steel joint, ~0.15–0.22 m across the shafts.

Must NOT become (neighbor boundary): a **rigid flange coupling** (no articulation —
we always keep live revolute journals), a **constant-velocity Rzeppa ball joint**
housing (ours is a cross/spider or cardan, not a caged-ball CV race), or a **plain
clevis/pin linkage** (a single pin hinge with no orthogonal second axis and no shaft
coupling role).

## 槽位 + 候选模块表

### Slot A：joint_topology  （③ Primary Form Family — 登记进 slot_choices）

Selects the whole skeleton family. `single_cross` / `pin_and_block` share the
spider+2-yoke parallel-children skeleton (2 journals, 2 revolute joints); they differ
in the ③ recognizable center prototype. `double_cardan` is a distinct chain skeleton
(middle + 2 spiders + 2 ends, 4 revolute joints).

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `single_cross` | origin_anchor | S2 | L165-210, L408-437 | Volumetric Envelope Form | eligible | spider root, spherical forged hub + journal_x/journal_y, 2 yokes, 2 REVOLUTE (Y,X) |
| `pin_and_block` | forked_anchor | S3 | L179-185 | Volumetric Envelope Form | eligible | same skeleton; chamfered machined `pivot_block` center replaces sphere |
| `double_cardan` | origin_anchor | S1 | L203-397 | Macro Surface Construction | eligible | middle_section + left/right spider + left/right end section; 4 REVOLUTE (Y×2, Z×2) |

### Slot B：yoke_form  （② + ③, topology-family-gated）

Candidate set is chosen from the topology family (compatibility gate — never
cross-composed across families).

Single-cross family (`single_cross` / `pin_and_block`):

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `sc_sleeve_open` | origin_anchor | S2 | L78-131 | hollow sleeve shaft + open box-arm fork + bearing bosses (default) |
| `sc_forged_open` | forked_anchor | S4 | L78-153 | lofted slender tapered cheeks, shaft necked back, longer journals |
| `sc_enclosed_block` | forked_anchor | S5 | L78-145 | closed rectangular block head with cross-window + coaxial bearing bores |

Double-cardan family (`double_cardan`):

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `dc_sleeve_open` | origin_anchor | S1 | L80-127 | open forged cheeks fused to hollow round sleeve (default) |
| `dc_enclosed_block` | forked_anchor | S7 | L80-142 | monobloc rectangular block yoke fused to the sleeve |
| `dc_flange` | forked_anchor | S8 | L80-130 | forged cheeks on a 4-bolt companion flange (no sleeve) |

### Slot C：middle_member  （① skeleton detail — GATED: double_cardan only）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `solid_hub` | origin_anchor | S1 | L130-177 | rounded double-yoke forging bridged by a solid central hub (default) |
| `centering_ball` | forked_anchor | S9 | L130-216 | saddles + spherical socket/ball/stub visuals (centered double-cardan) |
| `intermediate_shaft` | forked_anchor | S10 | L130-192 | turned round shaft with two independent forked end yokes (uncentered) |

Gate: `middle_member` is **only sampled when `joint_topology == double_cardan`**; a
single cross has no middle member. For single-cross seeds the value is `n/a`.

### Slot D：shaft_connection  （② interface — GATED: single-cross family only）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `plain_bore` | origin_anchor | S2 | L78-131 | hollow sleeve with keyed/plain bore + bore_liner + mouth_edge (default) |
| `splined_shaft` | forked_anchor | S6 | L58-140 | solid 12-tooth external splined shaft root replacing the sleeve bore |

Gate: `shaft_connection` is **only sampled for single-cross family**
(`single_cross` / `pin_and_block`). For `double_cardan` the driveline interface is
expressed by `yoke_form` (sleeve vs flange), so `shaft_connection = n/a`.

Hard-constraint notes: every slot has ≥2 structurally distinct candidates
(joint_topology 3, yoke_form 3 per family, middle_member 3, shaft_connection 2). No
single-candidate slots.

## 槽位图（slot graph）

pattern: mixed (topology-selected skeleton)

```
joint_topology = single_cross | pin_and_block:
    spider(root)  --[REVOLUTE axis Y, origin(0,0,0), ±0.55]-->  shaft_yoke_a
    spider(root)  --[REVOLUTE axis X, origin(0,0,0), ±0.55]-->  shaft_yoke_b
    (yoke_form shapes the yoke head; shaft_connection shapes the shaft behind it)

joint_topology = double_cardan:
    middle_section(root) --[REVOLUTE axis Y, origin(±0.025,0,0), ±16°]--> {left,right}_spider
    {left,right}_spider  --[REVOLUTE axis Z, origin(0,0,0),   ±16°]--> {left,right}_section
    (middle_member shapes middle_section; yoke_form shapes each end section)
```

Interface points:
- Single-cross: both revolute joints share the spider-center pivot (0,0,0); the
  spider's Y-journals seat in `shaft_yoke_a`'s `cap_pos/neg` cups (Y axis), the
  X-journals seat in `shaft_yoke_b`'s cups (X axis). Journal↔cup is a **captured
  trunnion** (no axis-aligned face pair) → joints omit `MatingContract` (grandfathered
  per AUTHORING §A Rule 2); capture is asserted via element-scoped `allow_overlap` +
  `expect_overlap`/`expect_within`/`expect_contact`.
- Double-cardan: each spider's Y-journals seat in the `middle_section` side cups
  (`{side}_cap_pos_y/neg_y`); its Z-journals seat in the end section caps
  (`{side}_cap_pos_z/neg_z`). Same captured-trunnion policy.

Mutual exclusion / optional / derived:
- The two families are mutually exclusive skeletons chosen by `joint_topology`.
- `middle_member` exists only in the double_cardan skeleton; `shaft_connection` only
  in the single-cross skeleton (both gated in `config_from_seed`/`slot_choices_for_seed`).
- Journal count is FIXED at 4 per spider (two orthogonal pairs) by cross geometry —
  NOT a diversity axis.

## 每槽位 Module Emits / Interfaces

### Slot A / single_cross (& pin_and_block)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spider` (forged_hub|pivot_block, journal_x, journal_y), `shaft_yoke_a`, `shaft_yoke_b` | S2 L165-406 / S3 L179-185 |
| internal joints | `spider_to_yoke_a` REVOLUTE axis (0,1,0) ±0.55; `spider_to_yoke_b` REVOLUTE axis (1,0,0) ±0.55; both origin (0,0,0) | S2 L408-437 |
| upstream interface | spider center pivot = part origin (root) | S2 |
| downstream interface | captured trunnion: journal_x/journal_y in yoke `cap_pos/neg` (no MatingContract) | S2 L563-619 |

### Slot A / double_cardan
| emits | 描述 | 来源 |
|---|---|---|
| parts | `middle_section` (+ side cups), `left_spider`, `right_spider`, `left_section`, `right_section` | S1 L243-342 |
| internal joints | `{left,right}_primary` REVOLUTE (0,1,0) ±16° origin (±0.025,0,0); `{left,right}_secondary` REVOLUTE (0,0,1) ±16° origin (0,0,0) | S1 L344-395 |
| upstream interface | middle_section stations (±0.025,0,0) side cups (root) | S1 |
| downstream interface | captured trunnions: spider Y-journals in middle cups, Z-journals in end caps | S1 L520-599 |

### Slot B / yoke_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | modifies `shaft_yoke_*` (single) or `*_section` (double) mesh only; no new parts | S4/S5/S7/S8 |
| internal joints | none (shapes the child body of an existing revolute) | — |
| interfaces | preserves bearing-boss/cup seat so journals stay captured across forms | S5 L100-106 / S7 L124-134 |

### Slot C / middle_member (double_cardan only)
| emits | 描述 | 来源 |
|---|---|---|
| parts | modifies `middle_section` mesh; centering_ball adds socket/ball/stub **visuals** (Rule 1: not parts) | S9 L294-333 |
| internal joints | none (centering ball is a fused decoration set, not an articulation) | S9 |
| interfaces | keeps the two Y-journal cup stations at ±0.025 | S1/S9/S10 |

### Slot D / shaft_connection (single-cross only)
| emits | 描述 | 来源 |
|---|---|---|
| parts | modifies `shaft_yoke_*` shaft body (sleeve bore vs spline root); decorations follow | S6 L58-140 |
| internal joints | none | — |
| interfaces | keeps bearing bore + yoke head unchanged | S6 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| joint_topology | enum | single_cross / pin_and_block / double_cardan | single_cross | choice | procedural sampler | Slot A |
| yoke_form | enum | (sc) sc_sleeve_open/sc_forged_open/sc_enclosed_block · (dc) dc_sleeve_open/dc_enclosed_block/dc_flange | sc_sleeve_open | conditional | candidate set = f(joint_topology family) | Slot B |
| middle_member | enum | solid_hub / centering_ball / intermediate_shaft / n·a | solid_hub | conditional | sampled iff joint_topology==double_cardan | Slot C |
| shaft_connection | enum | plain_bore / splined_shaft / n·a | plain_bore | conditional | sampled iff single-cross family | Slot D |
| palette_style | enum | machined_bright / satin_forged / zinc_plated / blackened_oxide / raw_forged | machined_bright | choice | rng.choice(PALETTE_STYLES) | S1/S2 materials |
| sc_journal_reach_scale | float | [0.90, 1.15] | 1.0 | independent | scales single-cross journal length & cup offset together | S2 L173-180 |
| sc_articulation_limit | float | [0.42, 0.58] rad | 0.55 | independent | symmetric revolute travel (single-cross) | S2 L415-436 |
| dc_articulation_limit | float | [0.18, 0.30] rad | 0.279 | independent | symmetric revolute travel (double-cardan) | S1 L344-349 |
| dc_joint_half_spacing | float | [0.023, 0.028] m | 0.025 | independent | half-distance between the two cardan stations | S1 L18 |
| (—) | constraint | — | — | inequality | journal reach must keep cup capture ≥6mm overlap; if a form/limit combo would break capture, clamp limit down (not reach up) | S2 L583-591 |

All `conditional` gating + clamps resolved in `resolve_config` (never deferred to the
builder). `sc_journal_reach_scale` co-scales the journal length and the cup seat
offset via one helper so capture depth is preserved (single-source geometric
quantity).

### 7.5 编译预算 / compile budget（必填）

**Budget: ≤20 s/seed** (typical target 8-14 s). Basis: each seed builds ~5-9 distinct
cadquery boolean meshes (2 yoke/end bodies + spider core + 1-2 journals + reused cup +
small decorations); the equivalent single 5★ records materialize well under this. The
pressed cup mesh is built **once and reused** across all cup instances (8× in
double-cardan, 4× in single-cross); the journal mesh is built once per spider style and
reused for all 4 journals. Tessellation follows the sources (tolerance 0.00016-0.00035,
angular 0.06-0.08 → ≤~64 facets on small radii). `_safe_fillet` guarded with try/except
so a fillet miss never hangs. `--compile-timeout 120` is a 6× watchdog, not a budget.

## Multiplicity / Copy Logic

- 无模板级复制数量逻辑（no `*_count` axis）。The spider journal count is **fixed at 4**
  by cross geometry (two orthogonal journal pairs) and is not exposed or swept. The
  double-cardan replicates a left/right `spider`+`end_section` pair — this is a fixed
  count of 2 dictated by the double-cardan topology, not a sampled multiplicity. No
  loop-copied template-level parts/joints beyond these fixed named slots.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | Two skeletons via `joint_topology`: single-cross (3 parts / 2 revolute) vs double-cardan (5 parts / 4 revolute). middle_member `intermediate_shaft` vs `solid_hub`/`centering_ball` changes the middle body construction. Source-backed S1/S2/S3/S9/S10. |
| └ multiplicity | 同构件 ×N | 无 | Journal count fixed=4 by cross geometry; L/R cardan pair fixed=2 by topology (see §8). |
| ② 关节类型 | 换 type/轴 | 有 | All journal joints REVOLUTE; single-cross axes (0,1,0)+(1,0,0), double-cardan axes (0,1,0)×2 + (0,0,1)×2. Every declared revolute appears in sweep. Source S1/S2. |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | `joint_topology` is the ③ slot (≥3 prototypes): single_cross spherical hub (Volumetric Envelope), pin_and_block chamfered block (Volumetric Envelope), double_cardan chain (Macro Surface Construction). Plus yoke_form prototypes (sleeve-open / forged-open loft / enclosed block; flange) as recognizable head forms. Source-backed S2/S3/S1/S4/S5/S7/S8. |
| ④ 表面装饰 | 叠加表面细节 | 有 | Host-conformal, non-articulating visuals fused/attached to the moving parent: retaining_ring_pos/neg, cap_dimple_pos/neg, bore_liner, mouth_edge, forging seams, and the centering ball/socket/stub set. `record_only`. Rings/dimples derived from the cup seat radius/position so they track ⑤ scale (Rule 4). |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | sc_journal_reach_scale [0.90,1.15], joint spacing [0.023,0.028], sc limit [0.42,0.58] rad, dc limit [0.18,0.30] rad. Motion envelope per revolute below. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 realistic steel colorways (metal 大类): machined_bright, satin_forged, zinc_plated, blackened_oxide, raw_forged. All-metal category ⇒ metal 大类 覆盖 100% ≥ ceil(0.5×5). Source S1/S2 materials + realistic companions. |

Motion envelopes / `motion_test_plan` (⑤ Rule 5):
- single-cross `spider_to_yoke_a` axis Y, `spider_to_yoke_b` axis X, each
  `[-limit, +limit]` (limit ∈ [0.42,0.58]); targeted `ctx.pose({joint:0.30})` asserts
  the yoke swings and stays captured (journal-cup overlap ≥8mm), mirroring S2 L621-663.
- double-cardan 4 revolutes `[-limit,+limit]` (limit ∈ [0.18,0.30]); targeted compound
  pose on the left group asserts sleeve displacement, mirroring S1 L638-652.
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)` with
  element-scoped `allow_overlap` on every captured journal↔cup pair (intended overlap);
  all other pairs must clear at every sampled pose.

## 采样与覆盖审计

总组合数：
- single-cross family: joint_topology(2: single_cross,pin_and_block) × yoke_form(3) ×
  shaft_connection(2) = 12
- double-cardan family: joint_topology(1) × yoke_form(3) × middle_member(3) = 9
- × palette_style(5) = (12+9)×5 = **105** discrete slot/palette combos, before continuous
  scales. Ample for a 0-35 sweep and >300 not expected (bounded by a 10-source anchor pool);
  documented per the low-combo allowance.

理由：two source families with topology-gated modifiers; combining across families is
explicitly illegal (compatibility gate), so the legal space is the sum of the two family
products, not their cross-product.

seed_domain_policy：procedural_first. `config_from_seed(seed)` (including seed 0) samples
`joint_topology`, then the family-appropriate `yoke_form`, then the gated
`middle_member`/`shaft_connection`, then `palette_style` and continuous scales, all from
`random.Random(seed)`. No curated/modulo table. No regression overrides at v1.

Topology target: report-only; the 105-combo legal space is covered well below 300 due to
the 10-anchor source ceiling and the family gate — documented, not a gate.

Controlled local parameterization: `sc_journal_reach_scale`, `sc_articulation_limit`,
`dc_articulation_limit`, `dc_joint_half_spacing` (ranges in §7). All clamped in
`resolve_config`; `sc_journal_reach_scale` co-derives the cup seat offset so capture depth
is preserved; limits clamp down (never reach up) if a form would break capture.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | topology → family yoke_form → gated middle_member/shaft_connection → palette → scales | slot_choices_for_seed matches build choices |
| compatibility matrix | middle_member⇔double_cardan only; shaft_connection⇔single-cross only; yoke_form set matched to family | no illegal cross-family form; no floating cup; journals stay captured |
| controlled local variation | 4 continuous scales, clamped/derived | proportions vary without breaking capture, joint origin, identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass (+corner), 0-999 maturity audit | contract failures; axis_realization; captured-journal viewer check |

Compatibility matrix (encodes the two gates):

| joint_topology | yoke_form candidates | middle_member | shaft_connection |
|---|---|---|---|
| single_cross | sc_sleeve_open / sc_forged_open / sc_enclosed_block | n/a (gated off) | plain_bore / splined_shaft |
| pin_and_block | sc_sleeve_open / sc_forged_open / sc_enclosed_block | n/a (gated off) | plain_bore / splined_shaft |
| double_cardan | dc_sleeve_open / dc_enclosed_block / dc_flange | solid_hub / centering_ball / intermediate_shaft | n/a (gated off) |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| joint_topology | 3 | yes | yes | ③ primary form family |
| yoke_form (per family) | 3 | yes | yes | family-gated |
| middle_member | 3 | yes | yes | double_cardan only |
| shaft_connection | 2 | yes | no | single-cross only; 2 structurally distinct sources |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed` returns implemented module names for every applicable slot and
  matches the build's actual picks.
- `config_from_seed` uses deterministic procedural sampling for all seeds (incl. 0).
- gating prevents illegal combos: no middle_member on single-cross; no shaft_connection on
  double-cardan; no cross-family yoke_form.
- no regression overrides.
- controlled scales clamped/derived in `resolve_config`; capture depth preserved.
- captured-journal joints exist as REVOLUTE with expected axes; single-cross axes
  orthogonal; double-cardan 4 revolutes.
- element-scoped `allow_overlap` on every journal↔cup pair; all other pairs clear in
  sampled poses; at least one targeted `ctx.pose` per family proves articulation.
- copied cup/journal meshes reused (single Mesh) per naming/placement policy.

## Reject cases

- middle_member sampled onto a single-cross seed (illegal — gate must block).
- shaft_connection sampled onto a double-cardan seed (illegal — gate must block).
- cross-family yoke_form (e.g. `dc_flange` on a single cross) — illegal.
- journal escapes its cup at any articulation extreme (capture overlap < ~6mm) — clamp
  limit, do not widen reach.
- a bearing cup / retaining ring / centering ball floating off its host (must be a fused
  or contacting visual on the moving parent — Rule 1).
- the two single-cross yokes interpenetrate near the spider at combined extreme poses.
- primitives downgraded to plain Box/Cylinder where the source uses fused/lathe/loft forms
  (Rule 3).
- palette collapses to one colorway across seeds (⑥ not realized).

## 与相邻类别的边界

- 不该混入：**rigid flange coupling** — has no articulation; we always retain live revolute
  journal joints (a flange appears only as the driveline interface behind a real joint).
- 不该混入：**constant-velocity Rzeppa ball joint** — caged-ball CV race, not a cross/spider
  or cardan; our centering_ball is a small centering element inside a double-cardan, not a
  load-path ball cage.
- 不该混入：**plain clevis/pin linkage** — single pin, no orthogonal second axis, no shaft
  coupling; ours always has orthogonal journal pairs and shaft interfaces.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Two-family single-slug template; joint_topology gates the whole skeleton. Split into `universal_joint_double_cardan` only if the two spines cannot converge to verdict=pass together. |

## 模板实现备注（可选）

- Shared helpers: one `_pressed_cup_mesh()` reused for all cups; one journal mesh per
  spider style; `_cylinder/_annulus/_fuse/_bearing_cap` verbatim from S2.
- Captured-pin overlaps need element-scoped `allow_overlap` (journal_* ↔ cap_*), declared
  before `fail_if_parts_overlap_in_sampled_poses`.
- Single-cross yoke body is one composed function `_single_yoke_shape(head_form,
  shaft_form, …)` branching on yoke_form × shaft_connection — same primitive family, just
  different fused sub-shapes (Rule 3 compliant).
</content>
</invoke>
