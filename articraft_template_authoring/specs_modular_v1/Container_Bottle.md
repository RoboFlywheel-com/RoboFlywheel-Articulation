# container_bottle — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_bottle` |
| template path | `agent/templates/Container_Bottle.py` |
| test path (optional) | (inline `run_container_bottle_tests`) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (a single hollow lathe body root carries one of several closure subtrees + an optional fixed seal child) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | combinatorial fork pool (`rec_qwen_bottle_001_v01..v30`, `rec_qwen_bottle_002_v01..v30`) + 2 parents |
| read_count | parents (2 prompts) + variants v01,v02,v05,v09,v13,v17,v21,v25,v29 (full model.py for v01/v13/v17/v25; prompts for the rest) |
| read_scope | approved TEMPORARY fast path: the variants are combinatorial multi-axis diffs, so the slot/module vocabulary was extracted directly from the variant `model.py` + `prompt.txt`, not from a per-sample enumeration |
| source_index_policy | only adopted module sources are indexed below |

Source records (under `<ARTI_SKILL_ROOT>/articraft_data/data/records/`, each `revisions/rev_000001/model.py`):

| source_id | record | role |
|---|---|---|
| S1 | `rec_qwen_bottle_001_v01` | tall cylindrical body lathe + screw-cap (CONTINUOUS spin + PRISMATIC lift) + gasket ring + mouth rim |
| S13 | `rec_qwen_bottle_001_v13` | sports body + flip straw cap: fixed cap_base ring with hinge ears, flip lid on REVOLUTE hinge, fixed straw, gasket |
| S17 | `rec_qwen_bottle_001_v17` | ribbed water body (grip grooves) + lip ring + swing-top stopper on side-hinge REVOLUTE + fixed hinge collar |
| S25 | `rec_qwen_bottle_001_v25` | squeeze conical body + conical nozzle/pump cap: PRISMATIC press + REVOLUTE twist via massless carrier + gasket |
| P2 | `rec_qwen_bottle_002_v01` / parent "tapered shoulder + black screw cap" | square-shouldered tapered body + continuous screw cap |

## 核心身份

A `container_bottle` is a hand-held hollow liquid container: a watertight body
(base at z=0, axis +Z) that narrows through a shoulder into a comparatively
narrow neck, topped by a **closable, articulated top**. Identity invariants:

- A single hollow revolved (lathe) body — never a boxy placeholder — with a
  base, a barrel, a shoulder taper, and a narrower neck with a visible hollow
  mouth bore.
- The neck is clearly narrower than the barrel.
- At least one **non-fixed** joint that is the closure mechanism (screw spin,
  flip hinge, swing-top hinge, pump press, straw pivot).

Adjacent classes to keep out: wide-mouth `container_jar` (mouth ≈ body width,
screw lid only — a bottle has a distinct narrow neck); `screwcap_bottle` (that
template is screw-cap-only; this is the broader closure family); drinking
`cup`/`mug` (open, no closable top); `pump_dispenser` standalone.

## 槽位 + 候选模块表

### Slot A：body_form  (the hollow lathe body — varies footprint/taper/wall treatment)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `tall_cylindrical` | S1 | L71-L108 | eligible if compatible | straight tall barrel, smooth shoulder arc, narrow neck, shelled-open mouth |
| `square_shouldered` | P2 | (parent profile) L64-L97-analog | eligible if compatible | squat barrel + sharper square shoulder step to a short neck |
| `sports_grip` | S13 | L58-L85 | eligible if compatible | wider barrel with an ergonomic grip waist (indent in the profile) |
| `squeeze_conical` | S25 | L64-L97 | eligible if compatible | waisted soft-squeeze body, longer shoulder taper to a slim neck |
| `ribbed_water` | S17 | L59-L108 | eligible if compatible | barrel with N vertical grip grooves cut into the shell |
| `canteen_oval` | S1+S17 (lathe + flattened scale) | L71-L108 | eligible if compatible | shorter wider barrel, flattened-oval footprint via per-axis body scale |

### Slot B：closure  (the articulated top — each module has ≥1 non-fixed joint)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `screw_cap` | S1 | L124-L156 (cap), L218-L239 (joints) | eligible if compatible | ribbed cap on a massless carrier: CONTINUOUS spin + PRISMATIC lift about +Z |
| `flip_cap` | S13 | L88-L170 (base+lid), L292-L311 (hinge) | eligible if compatible | fixed cap_base ring w/ hinge ears + flip lid disc on REVOLUTE hinge (axis +X) |
| `swingtop_stopper` | S17 | L111-L211 (stopper+collar), L259-L272 (hinge) | eligible if compatible | fixed hinge collar w/ side pins + plug-disc-bail stopper on side REVOLUTE (axis +Y) |
| `pump_press` | S25 | L113-L180 (nozzle), L255-L280 (joints) | eligible if compatible | conical nozzle/pump head: PRISMATIC press (-Z) + REVOLUTE twist via carrier |
| `straw_spout` | S13 | L145-L200 (lid+straw), L292-L311 (hinge) | eligible if compatible | flip lid (REVOLUTE) over a fixed straw tube protruding from the mouth bore |

### Slot C：seal  (optional fixed sealing/lip detail on the neck rim)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | — (degenerate) | — | eligible if compatible | bare neck rim; closure seats directly on the bore |
| `gasket_ring` | S1 | L111-L121, L210-L216 | eligible if compatible | rubber washer ring FIXED on the neck rim below the closure |
| `mouth_lip` | S17 | L80-L86 (lip step-out) | eligible if compatible | rolled thicker lip ring fused at the neck top (parent visual on body) |

Each slot has ≥3 structurally-distinct candidates. No 1-candidate slot.

## 槽位图（slot graph）

pattern: `parallel_children`

```
                         body (root, hollow lathe shell)
                          |  neck rim datum @ neck_top_z (mouth bore)
   +----------------------+-----------------------+
   |                      |                       |
 seal (Slot C)        closure (Slot B)        (optional fixed straw, in straw_spout)
 FIXED @ neck rim     non-fixed mechanism      FIXED @ neck bore
```

- **Common parent / datum**: the bottle body root; the neck rim plane at
  `neck_top_z` (and the bore at `mouth_r`) is the shared mating datum for every
  Slot B/C module.
- **Slot C → body**: FIXED joint at the neck rim (`gasket_ring`), or fused
  parent visual (`mouth_lip`), or absent (`none`).
- **Slot B → body** (per module):
  - `screw_cap`: body →[CONTINUOUS +Z]→ carrier →[PRISMATIC +Z]→ cap.
  - `flip_cap` / `straw_spout`: body →[FIXED]→ cap_base ring; cap_base →[REVOLUTE +X]→ flip lid. `straw_spout` also body →[FIXED]→ straw.
  - `swingtop_stopper`: body carries a FIXED hinge collar visual; body →[REVOLUTE +Y]→ stopper at the side-pin height.
  - `pump_press`: body →[PRISMATIC −Z]→ carrier →[REVOLUTE +Z]→ nozzle head.
- **Exclusivity**: exactly one Slot B closure per bottle. Slot C is independent
  and optional. No multiplicity.

## 每槽位 Module Emits / Interfaces

### Slot A / body (all modules)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottle_body` root: hollow lathe shell (base→barrel→shoulder→neck), inertial cylinder | S1 L71-L108 |
| internal joints | none (single rigid body); ribbed/grooves are body visuals | S17 L94-L108 |
| downstream interface | neck rim plane @ `neck_top_z`, bore radius `mouth_r`, neck outer radius `neck_r` | S1 L37-L48 |

### Slot B / screw_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | massless `cap_carrier`, ribbed `cap` w/ off-axis marker | S1 L124-L206 |
| internal joints | `cap_spin` CONTINUOUS +Z; `cap_lift` PRISMATIC +Z [0, cap_h] | S1 L218-L239 |
| upstream interface | carrier mounted to body at neck rim; cap skirt wraps neck (allow_overlap) | S1 L317-L331 |

### Slot B / flip_cap & straw_spout
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed `cap_base` ring w/ hinge ears; `flip_lid` disc + hinge barrel; (straw_spout) fixed `straw` tube | S13 L88-L200 |
| internal joints | `cap_flip` REVOLUTE +X [0, ~2.2] | S13 L292-L311 |
| upstream interface | cap_base FIXED on neck; straw FIXED in bore; lid hinge at rear ear top | S13 L274-L311 |

### Slot B / swingtop_stopper
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed `hinge_collar` (body visual) w/ side pins; `stopper` (plug+disc+bail arms) | S17 L111-L211 |
| internal joints | `stopper_hinge` REVOLUTE +Y [0, ~1.9] at side-pin height | S17 L259-L272 |
| upstream interface | collar around neck; plug seats in bore at q=0 (allow_overlap) | S17 L309-L325 |

### Slot B / pump_press
| emits | 描述 | 来源 |
|---|---|---|
| parts | massless `cap_carrier`, conical `nozzle` head w/ off-axis tab | S25 L113-L242 |
| internal joints | `cap_slide` PRISMATIC −Z [0, travel]; `cap_rotate` REVOLUTE +Z [−lim, lim] | S25 L255-L280 |
| upstream interface | carrier mounted at neck rim; skirt wraps neck (allow_overlap) | S25 L344-L360 |

### Slot C / gasket_ring & mouth_lip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gasket` washer ring (FIXED), or `mouth_lip` rolled-ring body visual | S1 L111-L121 / S17 L80-L86 |
| internal joints | `gasket_fixed` FIXED @ neck rim | S1 L210-L216 |
| upstream interface | seats on neck rim; closure compresses it (allow_overlap) | S1 L333-L340 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | 6 modules above | — | choice | deterministic procedural sampler | Slot A |
| closure | enum | 5 modules above | — | choice | deterministic procedural sampler | Slot B |
| seal | enum | none / gasket_ring / mouth_lip | — | choice | deterministic procedural sampler | Slot C |
| material_style | enum | clear_pet / amber / sports_smoke / juice_green | clear_pet | choice | palette only | S1/S13/S25 |
| body_radius | float | [0.026, 0.040] | 0.032 | independent | clamp | S1 L32 |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp; sets barrel/neck heights | S1 L36-L38 |
| neck_radius | float | derived | — | equation | `= body_radius * 0.40` (per-form factor) | S1 L37 |
| oval_scale | float | [0.72, 1.0] | 1.0 | conditional | only for `canteen_oval`: Y-axis body scale | S17 layout |
| groove_count | int | {6,8,10} | 8 | conditional | only for `ribbed_water` | S17 L54 |
| joint_limit_scale | float | [0.85, 1.10] | 1.0 | independent | clamp hinge upper limits | S13 L305-L311 |
| (—) | constraint | — | — | inequality | `neck_r < body_r * 0.7` (neck narrower than body) | identity |
| (—) | constraint | — | — | inequality | cap/skirt inner radius `> neck_r + clearance` | S1 L52 / S25 L52 |

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body / closure / seal）表达，不暴露
  `*_count`，也不通过循环复制模板级 visual/part/joint。Each bottle has exactly
  one body, one closure subtree, and at most one seal. (`groove_count` is an
  intra-mesh detail count of the `ribbed_water` body visual, not a structural
  copy of parts/joints.)

## 拓扑多样性审计

总组合数：body_form(6) × closure(5) × seal(3) = 90 distinct (slot, module) tuples
之外的拓扑等价类（body_form × closure 决定 part-tree/joint topology）= 30 distinct.

理由：closure alone yields 5 distinct joint topologies; body_form × closure = 30
distinct topology classes, far above 10. A 10-seed sweep readily samples ≥10.

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses `random.Random(seed)`
to draw body_form / closure / seal uniformly, plus controlled local scales.
`resolve_config` clamps scales and applies compatibility gating (neck-narrower
inequality, cap clearance inequality, conditional groove/oval params). `seed=0`
is not special. Random sweep seeds 0-49 for the initial pass, 0-999 for maturity.
Topology target: 1000-seed slot choice tuple distinct ≥30 (= body_form × closure), well（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
above the 100 guideline caveat (small combinatorial family — 30 is the ceiling
of structurally-distinct topology classes for this category, which is acceptable
and noted).

Controlled local parameterization: `body_radius` (independent), `body_height_scale`
(independent), `neck_radius = f(body_radius)` (equation), `oval_scale`
(conditional on canteen_oval), `joint_limit_scale` (independent). All clamped in
`resolve_config`; none change declared topology or break the neck-rim datum,
cap clearance, or hinge origins.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | uniform body_form/closure/seal + clamped scales | slot_choices_for_seed matches build choices |
| compatibility matrix | neck_r < 0.7·body_r; cap_inner_r > neck_r + clearance; groove_count/oval only on their forms | no floating, no neck-wider-than-body, cap clears neck |
| controlled local variation | body radius/height/oval/neck scales, joint limit scale, all clamped | proportions vary without breaking neck datum, clearance, hinge origins |
| regression overrides | none | — |
| random sweep | seeds 0-49 initial, 0-999 maturity | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 6 | yes | yes | |
| B closure | 5 | yes | yes | each ≥1 non-fixed joint |
| C seal | 3 | yes | yes | optional fixed/visual |

## Validator
- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combinations (neck width, cap clearance)
- no regression overrides
- controlled local scale params are clamped and cannot break interfaces, clearance, joint origin, or identity
- cross-part scale dependencies resolved in `resolve_config`
- each closure emits ≥1 non-fixed joint with the expected type/axis/range
- seal modules follow fixed-mount placement at the neck rim

## Reject cases
- neck not narrower than barrel (loses bottle identity → jar/cup)
- boxy placeholder body instead of a revolved hollow shell
- closure with no non-fixed joint (violates category contract)
- cap inner radius smaller than neck (cap cannot seat / collides)
- gasket/seal floating above or below the neck rim
- hinge axis not matching the visible mechanism (flip +X, swing-top +Y, screw/pump +Z)
- closure mounted below the shoulder instead of at the neck

## 与相邻类别的边界
- 不该混入：`container_jar`（宽口、口径≈瓶身、只有旋盖；瓶子必须有明显窄颈）
- 不该混入：`screwcap_bottle`（那个模板只做旋盖；本模板是更广的 closure 家族）
- 不该混入：`cup`/`mug`（开口、无可闭合顶盖）

## 模板实现备注（可选）
- 所有 body 用 cadquery revolve + `faces(">Z").shell(-WALL)` + `mesh_from_cadquery`
  (mirrors S1/S13/S17/S25 and the shopping_bucket reference).
- `screw_cap` and `pump_press` share the massless-carrier two-joint pattern.
- `flip_cap` and `straw_spout` share the cap_base ring + REVOLUTE hinge helper.
- captured-pin / seated-skirt overlaps need element-scoped `allow_overlap` in tests.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved (TEMPORARY fast path per task instructions: spec written first, then implement) |
| reviewer notes | combinatorial fork pool read directly from variant model.py; subset chosen (6×5×3) for clean implementability and diversity ≥10 |
