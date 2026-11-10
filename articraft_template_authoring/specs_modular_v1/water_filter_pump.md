# water_filter_pump — modular spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `water_filter_pump` |
| template path | `agent/templates/water_filter_pump.py` |
| test path (optional) | `tests/agent/test_water_filter_pump_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root chassis `pump_body` + parallel-children actuator / ports / base + multiplicity ribs·webs·legs) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 15 |
| read_count | 15 |
| read_scope | all 5-star / anchor / fork / probe records in the id list |
| source_index_policy | only adopted module sources are indexed below |

Records read (all under `data/records/<id>/revisions/rev_000001/model.py`):
- **origin1** `rec_a-handheld-...72ff3145` — twin fused barrels (pump Cylinder + shorter filter Cylinder), PRISMATIC T-bar paddle piston, REVOLUTE twist filter-cap carrying the outlet, 5 molded grip ribs, intake hose + foam pre-filter, output hose + blue clip.
- **origin2** `rec_...1c2f03adc4a5434c99f27df29d239b97` — single fat cylinder + top manifold + Lathe plunger_sleeve, PRISMATIC T-handle plunger, black rubber grip panel + 5 finger-scallop reliefs, TWO PRISMATIC detachable hose ports (outlet/intake) + two FIXED sample cups.
- **origin3** `rec_...4b72f2e9740148e2b07ac2a2dfaa6a66` — parallel filter cartridge + offset pump sleeve joined by 2 molded bridge webs, single PRISMATIC plunger, ribbed Knob caps, side outlet barb + curved clear hose + end fitting, front recess/label panel.
- **var_lever_pump** (fork of origin3) — plunger driven by a REVOLUTE lever arm on a `pivot_post`.
- **var_rotary_crank** (fork of origin2) — CONTINUOUS crank on a `crank_hub_boss`.
- **var_squeeze_bulb** (fork of origin2) — Lathe ovoid elastomer bulb, short-travel PRISMATIC squeeze + static check-valve nubs.
- **var_tripod_stand** (fork of origin3) — folding tripod: `tripod_hub` + 3 REVOLUTE legs (`base_to_leg_i`), shared leg helper (pivot_eye + strut + rubber foot).
- **var_inline_coaxial** (fork of origin3) — pump barrel stacked coaxially over the filter cartridge (single column, transition ring, top collar).
- **var_bottle_top** (fork of origin2) — free base replaced by a Lathe threaded bottle collar + a Lathe clear bottle hanging below.
- **var_ring_pull_handle** (fork of origin1) — TorusGeometry closed D-ring pull handle in place of the paddle.
- **var_inline_prefilter** (fork of origin1) — a cadquery inline sediment canister spliced mid-run on the intake hose.
- **var_grip_ribs_dense / var_grip_ribs_sparse** (forks of origin1) — rib multiplicity N=10 / N=3.
- **var_bridge_webs_multi** (fork of origin3) — bridge-web multiplicity N=4.
- **probe_lever_twin_barrel** — REVOLUTE lever mounted on the twin-barrel body (② lever × ③ twin-barrel clearance probe; converged).

## 核心身份

A **handheld, hand-powered water filter pump**: a filter body/cartridge that source water is forced through by a **reciprocating / driven hand actuator with a real non-fixed joint** (piston plunger, pivoting lever, rotary crank, or squeeze bulb), plus dirty-water intake and clean-water outlet interfaces (barbs / hoses / detachable ports). Default mature domain = olive/dark-olive molded plastic backpacking micro-filter pumps ~0.15–0.32 m tall.

Must NOT drift into (see §11): gravity/squeeze straw filters with no pump actuator (LifeStraw/Sawyer squeeze), electric/USB pumps, generic tire/bike hand pumps, lab filtration rigs, or a plain water bottle.

## 槽位 + 候选模块表

Assembly is **parallel-children**: `body_form` builds the root `pump_body` and publishes mount metadata; `pump_actuation`, `hose_ports`, `support_base` each read `ctx.upstream_interface.part_name` (= `pump_body`), emit their own parts + joints parented to the body, declare **no `upstream` interface** (so the assembler emits no auto chain joint), and re-export the body interface as `downstream`. This lets every joint be authored with the correct type / mating / grandfather exactly as the source records do.

### Slot A：body_form  (③ Primary Form Family — root)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `twin_barrel` | origin_anchor | origin1 | L94-L121, L182-L197 | Volumetric Envelope Form | eligible | pump Cylinder (r≈0.021,h≈0.150) fused to shorter filter Cylinder (r≈0.018,h≈0.112) at +X; base pads + top collar; **grip-rib multiplicity**; mount = top collar of pump barrel |
| `single_cylinder` | origin_anchor | origin2 | L156-L228 | Volumetric Envelope Form | eligible | one fat Cylinder (r≈0.045,h≈0.185) + bottom/top caps + manifold disk + Lathe `plunger_sleeve` + black grip panel mesh + **finger-scallop multiplicity**; mount = top manifold |
| `parallel_sleeve` | origin_anchor | origin3 | L45-L118 | Macro Surface Construction | eligible | filter cartridge Cylinder (r≈0.030,h≈0.235) + offset pump-sleeve Cylinder (r≈0.0145) joined by **bridge-web multiplicity** (Box); ribbed Knob caps + front recess panel; mount = top of pump sleeve |
| `inline_coaxial` | forked_anchor | var_inline_coaxial | L44-L109 | Volumetric Envelope Form | eligible | single vertical column: filter Cylinder → ribbed transition ring (Knob) → coaxial pump barrel Cylinder → top collar (Knob); mount = top collar on the shared axis |
| `bottle_top` | forked_anchor | var_bottle_top | L86-L149, L194-L268 | Volumetric Envelope Form | eligible | single_cylinder body but base = Lathe threaded collar (`_pump_base_geom`) + a Lathe clear `bottle` shell folded in as a body visual below; mount = top manifold |

Degrade note: none — 5 structurally distinct ③ forms, all source-backed.

### Slot B：pump_actuation  (② joint / mechanism type)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `piston_paddle` | origin_anchor | origin1 | L241-L264 | eligible | PRISMATIC rod + T-bar paddle (cadquery→Box crossbar) captured in barrel; long stroke ≈0.075–0.085 |
| `piston_thandle` | origin_anchor | origin2/origin3 | o2 L231-L265 / o3 L158-L194 | eligible | PRISMATIC rod + capsule/cylinder cross T-handle grip; long stroke |
| `lever_pump` | forked_anchor | var_lever_pump | L159-L223 | eligible if `body_form≠parallel_sleeve` else via probe | REVOLUTE lever arm on a `pivot_post` (added to body), arm swings −X away from filter; rod hangs into sleeve. probe_lever_twin_barrel validates lever×twin |
| `rotary_crank` | forked_anchor | var_rotary_crank | L193-L256 | eligible | CONTINUOUS crank hub on `crank_hub_boss` (added to body) + offset crank arm + perpendicular grip knob |
| `squeeze_bulb` | forked_anchor | var_squeeze_bulb | L194-L270 | eligible | short-travel PRISMATIC Lathe ovoid elastomer bulb on a `bulb_neck` (added to body) + static check-valve nubs; travel ≈0.012 |

`ring_pull` grip is folded into `piston_paddle`/`piston_thandle` as a `handle_grip_form` palette/geometry option (see §8 handle grip), per source var_ring_pull_handle (TorusGeometry L136-143).

### Slot C：hose_ports  (③/② interface layer)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_hoses` | origin_anchor | origin1 | L199-L238, L278-L316 | eligible | intake barb + spline `tube` hose → foam pre-filter tip; outlet barb + hose → clip; all `pump_body` visuals, no new part |
| `detachable_ports` | origin_anchor | origin2 | L310-L413 | eligible | TWO real PRISMATIC port parts (`outlet_port`, `intake_port`): barb + collar (seats on body socket → MatingContract) + tube hose + end fitting; slide out along ±X |
| `single_outlet` | origin_anchor | origin3 | L121-L156 | eligible | single side outlet barb + curved `tube` hose + grey end fitting; `pump_body` visuals only |
| `fixed_hoses_prefilter` | forked_anchor | var_inline_prefilter | L93-L113, L166-L197 | eligible | `fixed_hoses` + an inline sediment canister (cadquery, ① added intake element) spliced mid-run on the intake hose; body visuals |

### Slot D：support_base  (① skeleton / N)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_base` | origin_anchor | origin1/2/3 | o3 L51-L56 | eligible | a molded base pad / foot ring folded into `pump_body` as a visual; no new part/joint |
| `tripod_stand` | forked_anchor | var_tripod_stand | L23-L46, L184-L233 | eligible | `tripod_hub` on body + N REVOLUTE folding legs (`base_to_leg_i`), each = pivot_eye + strut + rubber foot; **leg multiplicity** N=3–4 |

Degrade note: support_base has 2 candidates (documented degrade). The 5★ pool contains exactly two structurally-distinct base treatments — a molded static base pad (all three origins) vs. the folding hinged tripod (var_tripod_stand). No third structurally-distinct base exists in-pool, so 2 candidates is the honest count; both are source-backed and one adds a real REVOLUTE multiplicity subtree.

## 槽位图（slot graph）

pattern: mixed / parallel_children off a root chassis

```
body_form(pump_body, root)
   ├─[PRISMATIC z | REVOLUTE y | CONTINUOUS z, mount=wfp_mount]──> pump_actuation (actuator part)
   ├─[PRISMATIC ±x on body sockets (detachable) | none (fixed/embedded hoses)]──> hose_ports
   └─[REVOLUTE tangential ×N (tripod) | none (flat)]──> support_base
```

- **body_form** publishes `model.meta["wfp"]`: `mount_xy`, `mount_top_z`, `barrel_inner_r`, `barrel_bottom_z`, `barrel_visual` (name for rod allow_overlap), `outlet_socket`, `intake_socket`, `base_center_xy`, `base_bottom_z`, `neighbor_keepout` (x-range the actuator must avoid).
- **pump_actuation** reads `mount_*`/`barrel_*`; for lever/crank/bulb it first adds its pivot hardware (`pivot_post`/`crank_hub_boss`/`bulb_neck`) as a `pump_body` visual at the mount so the REVOLUTE/CONTINUOUS/short-PRISMATIC origin sits on real geometry; then emits its child part + joint. Joint uses **no MatingContract** (captured-shaft / pin-through-sleeve, grandfathered) except the bulb base-collar contact.
- **hose_ports** reads `outlet_socket`/`intake_socket`; detachable ports emit PRISMATIC joints WITH a `MatingContract` (collar `positive/negative_x` ↔ body socket).
- **support_base** reads `base_center_xy`/`base_bottom_z`; tripod emits N REVOLUTE leg joints (grandfathered captured-pin pivots).
- No slot-to-slot serial mating; every child parents to `pump_body`.

## 每槽位 Module Emits / Interfaces

### Slot A / body_form (all candidates)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_body` (root) | o1/o2/o3 |
| internal joints | none | — |
| upstream interface | none (root) | — |
| downstream interface | `pump_body` self-face (re-exported to B/C/D; never auto-jointed) | assembler contract |
| meta | `wfp` mount/socket/base dict | this spec |

### Slot B / pump_actuation
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_handle` (paddle/thandle/lever/bulb) or `crank_handle` | o1 L241 / o2 L231 / lever L167 / crank L225 / bulb L234 |
| body visuals added | pivot hardware for lever/crank/bulb | lever L159 / crank L193 / bulb L194 |
| internal joints | `body_to_actuator`: PRISMATIC z (piston/coaxial) · REVOLUTE y (lever) · CONTINUOUS z (crank) · short PRISMATIC −z (bulb) | o1 L256 / lever L213 / crank L248 / bulb L261 |
| upstream interface | none (parallel child; parents to `pump_body`) | parallel pattern |
| downstream interface | re-export `pump_body` | — |

### Slot C / hose_ports
| emits | 描述 | 来源 |
|---|---|---|
| parts | 0 (fixed/single/prefilter) or `outlet_port`+`intake_port` (detachable) | o1/o3 / o2 L310 |
| body visuals added | barbs, tube hoses, tips, fittings, canister | o1/o3/prefilter |
| internal joints | detachable: `body_to_outlet_port`/`body_to_intake_port` PRISMATIC ±x, WITH MatingContract | o2 L396-L413 |
| downstream interface | re-export `pump_body` | — |

### Slot D / support_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | 0 (flat) or `leg_0..N-1` (tripod) | tripod L218 |
| body visuals added | base pad / foot ring / `tripod_hub` + `leg_boss_i` | o3 L51 / tripod L192-L215 |
| internal joints | tripod: `base_to_leg_i` REVOLUTE tangential (grandfathered captured-pin) | tripod L223-L233 |
| downstream interface | re-export `pump_body` | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | twin_barrel / single_cylinder / parallel_sleeve / inline_coaxial / bottle_top | twin_barrel | choice | procedural `rng.choice` | §4 A |
| `pump_actuation` | enum | piston_paddle / piston_thandle / lever_pump / rotary_crank / squeeze_bulb | piston_paddle | choice | procedural; lever/crank/bulb on parallel_sleeve→re-roll to piston_thandle (offset-sleeve clearance) | §4 B |
| `hose_ports` | enum | fixed_hoses / detachable_ports / single_outlet / fixed_hoses_prefilter | fixed_hoses | choice | procedural | §4 C |
| `support_base` | enum | flat_base / tripod_stand | flat_base | choice | procedural | §4 D |
| `handle_grip_form` | enum | tbar / thandle / ring_pull | tbar | conditional | only when actuation∈{piston_paddle,piston_thandle}; ring_pull=Torus | var_ring_pull |
| `palette_style` | enum | olive_classic / dark_olive / desert_tan / graphite_grey / blue_accent | olive_classic | choice | `rng.choice(PALETTE_STYLES)` → `mats` | ⑥ across sources |
| `body_height_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform then clamp | ⑤ o1/o2/o3 |
| `body_radius_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform then clamp | ⑤ |
| `stroke_scale` | float | [0.85, 1.15] | 1.0 | equation | `stroke = base_stroke·stroke_scale`, `base_stroke` from form; bulb uses short travel | o1 STROKE=0.085 |
| `rod_len` | float | derived | — | equation | `= mount_top_z − barrel_bottom_z + stroke + retain` | o1 L52-57 |
| `rib_count` | int | [3, 12] | 5 | conditional | only twin_barrel (else scallops/webs); small-N weighted | o1 / dense10 / sparse3 |
| `web_count` | int | [2, 5] | 2 | conditional | only parallel_sleeve | o3 (2) / webs_multi (4) |
| `scallop_count` | int | [3, 6] | 5 | conditional | only single_cylinder/bottle_top | o2 (5) |
| `leg_count` | int | [3, 4] | 3 | conditional | only tripod_stand | tripod (3) |
| (—) | constraint | — | — | inequality | actuator envelope must clear `neighbor_keepout` (lever/crank arm points away from filter cyl); clamp swing/arm-len | probe |
| (—) | constraint | — | — | inequality | `rod_radius ≤ barrel_inner_r − 0.002`; rod retained ≥0.02 in barrel at full extension | o1 L421-453 |

All `equation`/`inequality`/`conditional` resolved in `resolve_config` / at build from published body meta; nothing left to fail in the builder.

### 7.5 编译预算 / compile budget（必填）
**Target ≤ 18 s / seed.** Rationale: body barrels are `Cylinder` primitives (no boolean); sculpted meshes are bounded — `KnobGeometry` caps/collars, `LatheGeometry` plunger sleeve / squeeze bulb / bottle shell, and `tube_from_spline_points` hoses. Tessellation caps: small features (barbs, ribs, feet, collars) `radial_segments ≤ 24`; hero Lathe/Knob faces `segments ≤ 56`; hoses `samples_per_segment ≤ 16`, `radial_segments ≤ 16`; the inline canister and the paddle crossbar are the only cadquery unions (small, ≤2 booleans). N repeated legs/ribs/webs reuse one shared helper/`Mesh`. Sweep watchdog `--compile-timeout 120` (≈3×). If any seed >20 s, drop hose/Lathe segment counts before iterating.

## Multiplicity / Copy Logic

Four independent multiplicity axes, each per-body-form / per-base and each编进 `slot_choices`:

- **grip ribs** (twin_barrel): `count_param=rib_count`; N_range **[3,12]**, samples 3 (sparse) / 5 (origin1) / 10 (dense); weighted small-N (3–6 common, 7–12 rare); copied_object=`body_rib_{i}`; placement = even angular spacing over the rear grip arc (≈210°–290°); joint_policy = static body visuals (no joints). source: origin1 L182-197 + forks.
- **bridge webs** (parallel_sleeve): `count_param=web_count`; N_range **[2,5]**, samples 2 (origin3) / 4 (webs_multi); copied_object=`bridge_web_{i}`; placement = even Z-stack between the two columns; joint_policy = static body visuals. source: origin3 L98-109 + webs_multi.
- **finger scallops** (single_cylinder/bottle_top): `count_param=scallop_count`; N_range **[3,6]**, sample 5 (origin2); copied_object=`scallop_{i}`; placement = even Z on the black grip panel; joint_policy = static body visuals. source: origin2 L221-228.
- **tripod legs** (tripod_stand): `count_param=leg_count`; N_range **[3,4]**, sample 3; copied_object=`leg_{i}`; placement = radial `2πi/N`; joint_policy = one REVOLUTE fold joint per leg (captured-pin, element-scoped allow_overlap). source: var_tripod_stand L199-233.

Each axis samples independently, weighted small-N, clamps to its range, and is capped in the sweep. A non-selected form/base contributes N=0 for its axis.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | actuator subtree (1 part, joint varies §②); tripod base subtree N=3–4 hinged legs (var_tripod_stand); detachable-port subtree 2 PRISMATIC parts (origin2); inline pre-filter adds an intake element (var_inline_prefilter). All forked_anchor/source-backed. |
| └ multiplicity | 同构件 ×N | 有 | 见 §8 — 4 axes: ribs[3,12], webs[2,5], scallops[3,6], legs[3,4]. |
| ② 关节类型 | 图不变，换 type/轴 | 有 | PRISMATIC piston z (o1/o2/o3), REVOLUTE lever y (var_lever), CONTINUOUS crank z (var_crank), short PRISMATIC −z squeeze (var_bulb), PRISMATIC ±x detachable ports (o2), REVOLUTE tangential tripod legs (var_tripod). Every declared type appears in the sweep. source-backed. |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | 5 candidates §4A: twin_barrel / single_cylinder / parallel_sleeve / inline_coaxial (Volumetric Envelope) + parallel_sleeve (Macro Surface Construction). Registered in `slot_choices`. source-backed. |
| ④ 表面装饰 | 叠加表面细节 / 改装饰数 | 有 | molded grip ribs, black rubber grip panel + finger scallops, ribbed/fluted Knob cap knurl, front recess/label panel, molded bridge webs. `record_only`; all host-conformal (ribs at `barrel_r+t/2−embed`, panel hugs cyl radius, scallops on the panel face). Derive order ③→⑤→④. |
| ⑤ 尺寸/行程 | 只改尺寸/比例/行程 | 有 | body H≈0.15–0.32 m (`body_height_scale`[0.85,1.20]), radius scale[0.90,1.12], pump stroke 0.075–0.085·`stroke_scale`; bulb travel≈0.012; tripod fold [0,0.55]; port detach [0,0.030]; twist-cap (twin) [0,0.75]. **运动包络**: piston/coaxial PRISMATIC +z `[0, stroke]` (rod stays inserted ≥0.02); lever REVOLUTE +y `[0, ~0.9]` arm swings up/away from filter; crank CONTINUOUS full turn; bulb PRISMATIC −z `[0,0.012]`; ports PRISMATIC ±x `[0,0.030]`; legs REVOLUTE `[0,0.55]` splay outward. `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose(...)` per mechanism (rod rises & retained; lever grip lifts & clears filter; crank knob sweeps xy; bulb compresses down; port detaches outward; leg_0 splays +x). |
| ⑥ 涂装 | 只改材质/颜色 | 有 | plastic + rubber + clear-hose + metal-rod + grey-fitting. `palette_style` ≥5: olive_classic, dark_olive, desert_tan, graphite_grey, blue_accent — material大类 covered ≥ ceil(0.5×5)=3 (plastic/rubber/metal/glass-hose). record_only across the 5★ palettes. |

收尾自检: 0-9 seed batch must show the 5 body forms spread, all 4 actuator joint types, decoration hugging the body, no closed/mid-travel 穿模, and palette varying (not olive-monochrome every seed).

## 采样与覆盖审计

总组合数 (离散): body_form 5 × pump_actuation 5 (−1 gated pair) × hose_ports 4 × support_base 2 = **~200** base slot combos, ×4 multiplicity axes (ribs 10 / webs 4 / scallops 4 / legs 2 effective) → topology tuple space well over **300**. report-only.

理由: 形态主导 + 机构主导双轴富类别；ribs/webs/legs 提供覆盖而非 distinctness 灌水。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses `random.Random(seed)` for ALL seeds incl. 0 — samples each slot via `rng.choice`, then multiplicity counts (weighted small-N), then continuous scales, then `palette_style`. Compatibility gates: `lever_pump`/`rotary_crank`/`squeeze_bulb` on `parallel_sleeve` re-roll to `piston_thandle` (the short offset pump sleeve gives a top-mounted swing/sweep/seat no clearance beside the tall filter cartridge; lever×twin is validated by probe_lever_twin_barrel and allowed since twin's filter is short and below the actuator). `detachable_ports` only on forms with side sockets (`single_cylinder`/`bottle_top`), else `fixed_hoses`. `handle_grip_form` only applies to piston actuators. No curated/modulo main table; no regression overrides at v1.
Topology target：≥300 unique slot-choice tuples over 1000 seeds (report-only).
Controlled local parameterization：`body_height_scale`, `body_radius_scale`, `stroke_scale` (independent, clamped in `resolve_config`); `rod_len` derived from published body meta; multiplicity counts clamped to their ranges. None break the parallel-children joints (each parents to the body; scales move the published mount/socket/base meta together, so children follow by construction).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→C→D, weighted small-N multiplicity, lever/parallel gate | `slot_choices_for_seed` matches build choices |
| compatibility matrix | {lever,crank,bulb}∉parallel_sleeve (→piston_thandle); detachable_ports only single/bottle; handle_grip only on piston; all others free | no floating, no closed/mid overlap, joint axis/range, actuator clears neighbor keepout |
| controlled local variation | 3 clamped scales + derived rod_len | proportions vary; interfaces/clearance/joint-origin/identity intact |
| regression overrides | none | — |
| random sweep | seeds 0-15 fast, 0-35 final, corner stage; 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 5 | yes | yes | |
| pump_actuation | 5 | yes | yes | |
| hose_ports | 4 | yes | yes | |
| support_base | 2 | yes | no | documented degrade (only 2 structurally-distinct base treatments in-pool) |

## Validator

- `slot_choices_for_seed` returns implemented module names (incl. multiplicity band tokens)
- `config_from_seed` uses deterministic procedural sampling for all seeds incl. 0
- compatibility gate prevents lever_pump×parallel_sleeve
- no regression overrides
- controlled scales clamped in `resolve_config`; `rod_len` derived from body meta, never a sweep-tuned constant
- detachable ports declare MatingContract (collar↔socket); tripod/actuator captured pivots use element-scoped `allow_overlap`
- actuator joint type/axis/range match the chosen module; `fail_if_parts_overlap_in_sampled_poses` + targeted poses run
- copied objects (`body_rib_i`/`bridge_web_i`/`scallop_i`/`leg_i`) follow naming + placement policy

## Reject cases

- No non-fixed pump actuator (becomes a gravity/straw filter) → identity fail.
- Rod/plunger not retained in the barrel at full extension, or rod radius ≥ barrel bore → sampled-pose / within fail.
- Lever or crank arm swinging into the neighboring filter cylinder (穿模) → mid-travel overlap fail; clamp swing / point arm away.
- Free-floating cups / hose ends with no contact path to the body → isolated-part / island fail (cups dropped; hose ends terminate in a contacting fitting).
- Decoration (ribs/panel/scallops) built at constant radius standing proud of a scaled body → Rule 4 fail.
- Tripod leg joint origin off the hub hardware, or legs interpenetrating when folded → origin / overlap fail.
- Monochrome every seed (palette_style not driving materials) → §8.5 ⑥ fail.

## 与相邻类别的边界

- 不该混入：gravity / squeeze straw filter (LifeStraw/Sawyer) — drops the core pump actuator; a neighbor subcategory.
- 不该混入：electric / USB inline pump — not hand-powered.
- 不该混入：generic hand tire / bike pump, car jack, lab vacuum-filtration rig, plain water bottle — no filter cartridge + intake/outlet identity.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored from 15 records; 4 slots (body 5 / actuation 5 / ports 4 / base 2), parallel-children off `pump_body`, 4 multiplicity axes. |

## 模板实现备注（可选）
- Shared helpers: `_knob_cap`, `_lathe_sleeve`, `_hose`, one rib/web/scallop/leg emitter each.
- Body publishes `model.meta["wfp"]`; B/C/D read it — the single source of mount/socket/base geometry (Contract 3c).
- Captured-pin overlaps element-scoped: rod↔barrel, pivot_boss↔post, crank_hub↔boss, bulb_collar↔neck, leg pivot_eye↔leg_boss/hub.
- lever×parallel_sleeve excluded from seed domain; lever×twin allowed (probe-backed) with clamped swing.
