# Source Map — Textiles_Fabric / Fabric scissors

slug `fabric_scissors` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_textiles_fabric__fabric_scissors__002_png_8904372f20114f569b6f2ac77b3522aa` — picture/Textiles_Fabric/Fabric scissors/002.png
- `rec_textiles_fabric__fabric_scissors__001_png_bf8f7c7d50324697b8f064266385ff8a` — picture/Textiles_Fabric/Fabric scissors/001.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_fabric_scissors_var_curved` | curved | PASS | 1 | 1 |
| `rec_fabric_scissors_var_duckbill` | duckbill | PASS | 1 | 0 |
| `rec_fabric_scissors_var_pinking_n15` | pinking_n15 | PASS | 1 | 0 |
| `rec_fabric_scissors_var_pinking_n9` | pinking_n9 | PASS | 1 | 0 |
| `rec_fabric_scissors_var_scalloping` | scalloping | PASS | 1 | 0 |
| `rec_fabric_scissors_var_serrated` | serrated | PASS | 1 | 0 |
| `rec_fabric_scissors_var_spring_snips` | spring_snips | PASS | 1 | 1 |
| `rec_fabric_scissors_var_symmetric_bow` | symmetric_bow | PASS | 1 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Textiles_Fabric / Fabric scissors

slug `fabric_scissors` · pattern **linear_chain** (one `pivot_screw` REVOLUTE joining two blade arms; no repeated homogeneous parts on the base object — multiplicity appears only on forked pinking-tooth rows). Richness band: **simple** (structural vocabulary is genuinely thin; coverage-first). Total candidate anchors = **10** (2 origins + 8 forked). Fork jobs emitted = **8**.

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Fabric scissors
  core_identity: two forged steel blades crossing at a single pivot screw, revolute open/close, honed cutting edges meeting at a shear line, finger handle(s) for a scissor grip
  must_keep:
    - two blades that mesh/cross at one pivot and shear along a cutting line
    - exactly one primary non-fixed joint (pivot_screw revolute) opening/closing the blades
    - hand-held tailoring scale (~0.15-0.32 m overall) with finger grip(s)
  must_not_become:
    - garden pruning shears / secateurs
    - kitchen or poultry shears
    - hair-cutting / thinning barber shears
    - tin snips or paper guillotine
    - electric / rotary fabric cutter (powered, no scissor pivot)
  image_evidence:
    - 001.png: heavy bent-handle tailor shears, black-coated blades, brass pivot screw, offset black plastic loops (small thumb loop + large finger loop with pinky rest)
    - 002.png: a family of dressmaker/tailor shears - long steel-bow tailor shears, bent-handle dressmaker shears with steel loops, small embroidery-style scissors; floral-etched blades + brand stamp
  parent_evidence:
    - both parents = fabric_tailor_shears, two blade parts + one pivot_screw REVOLUTE
    - offset asymmetric finger loops (large finger loop + small thumb loop), pointed honed straight blades, raised polished cutting bevel + spine facet, visible pivot screw head/shank/slot
```

## Origins (full reconciliation, 2/2 on-grid)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_..._002_png_8904372f...` | 002 | brushed-steel bent-handle dressmaker shears; parts `lower_arm`/`upper_arm`; polygon `_metal_plate`+`_blade_bevel`+`_grip`; `pivot_screw` revolute; asymmetric `large_finger_loop`/`small_thumb_loop` | edge=honed / body=pointed_straight / handle=offset_asymmetric |
| B `rec_..._001_png_bf8f7c7d...` | 001 | black-coated tailor shears, brass screw; parts `upper_shear`/`lower_shear`; `ExtrudeWithHolesGeometry` blade + `_ring_extrude_geometry`/`_oval_profile` loops; `pivot_screw` revolute | edge=honed / body=pointed_straight / handle=offset_asymmetric |

Both origins are the **same skeleton** (two-arm pivot + offset asymmetric loops + pointed honed blades); they differ only on ④ coating (brushed steel vs black), ⑥ screw material (steel vs brass), ⑤ proportion (dressmaker vs heavy tailor). They jointly anchor the `honed_edge / pointed_straight / offset_asymmetric` candidate — no fork needed for it.

## Slots & Candidate Grid
- **A blade_edge_geometry (③)**: honed_smooth (A,B origin) / pinking_zigzag (fork, +N) / scalloping_wave (fork) / micro_serrated (fork)
- **B blade_body_form (③)**: pointed_straight (A,B origin) / duckbill_paddle (fork) / curved_trimming (fork)
- **C handle_configuration (②/① handle topology)**: offset_asymmetric_bent (A,B origin) / symmetric_inline_bows (fork)
- **D skeleton/mechanism (①/②)**: two_arm_pivot_revolute (A,B origin, all pivot forks) / spring_squeeze_yoke (fork, ①+spring-return ②)

Every supported slot reaches >=2 structurally distinct candidates. No slot padded.

## Slot candidate coverage
### A blade_edge_geometry
| candidate | record | source_type | status |
|---|---|---|---|
| honed_smooth | A, B | origin_anchor | converged |
| pinking_zigzag | rec_fabric_scissors_var_pinking_n9 | forked_anchor | planned |
| scalloping_wave | rec_fabric_scissors_var_scalloping | forked_anchor | planned |
| micro_serrated | rec_fabric_scissors_var_serrated | forked_anchor | planned |
### B blade_body_form
| pointed_straight | A, B | origin_anchor | converged |
| duckbill_paddle (appliqué) | rec_fabric_scissors_var_duckbill | forked_anchor | planned |
| curved_trimming | rec_fabric_scissors_var_curved | forked_anchor | planned |
### C handle_configuration
| offset_asymmetric_bent | A, B | origin_anchor | converged |
| symmetric_inline_bows | rec_fabric_scissors_var_symmetric_bow | forked_anchor | planned |
### D skeleton/mechanism
| two_arm_pivot_revolute | A, B (+ all pivot forks) | origin_anchor | converged |
| spring_squeeze_yoke | rec_fabric_scissors_var_spring_snips | forked_anchor | planned |

## Multiplicity / Copy Logic
- **Base object has no repeated homogeneous parts** (a scissor has exactly two blades — no N-sweep on the base).
- Multiplicity appears only on the **pinking/scalloping/serrated edge forks**: the sawtooth/scallop teeth are repeated homogeneous features and must be **loop-emitted** (`_pinking_teeth(n)` etc.).
- count_param: `n_pinking_teeth`
- N samples: **9 (coarse)**, **15 (fine)** — `rec_fabric_scissors_var_pinking_n9`, `rec_fabric_scissors_var_pinking_n15`
- suggested N_range: [6, 18]
- copied object / naming / placement / joint policy: one triangular tooth `tooth_i`, evenly spaced along the ~0.20 m cutting edge, indexed `tooth_0..tooth_{n-1}`, mirrored on the opposing blade so the two rows mesh; each tooth FIXED to its blade (teeth do not add joints).

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | two_arm_pivot (origins) / spring_squeeze_yoke (spring_snips fork) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | single pivot_screw REVOLUTE (all); spring-return bias added on spring_snips; handle topology offset->inline on symmetric_bow |
| ③ primary form family | source-backed (forked_anchor) | edge: honed/pinking/scalloping/serrated; blade body: pointed/duckbill/curved |
| ④ surface decoration | record_only + world_knowledge_extrapolation | floral etch + brand stamp (002), coating pattern; host-conformal only, no standalone fork |
| ⑤ proportion / size / travel | record_only (may ride companion) | overall length embroidery ~0.09 / dressmaker ~0.20 / heavy tailor ~0.30; loop sizes; pivot travel ~ -0.3..0.6 rad |
| ⑥ material / palette / finish | record_only (may ride companion) | brushed steel / black-coated blades; steel vs brass pivot screw; black / colored plastic or steel bow handles; chrome / gold-plate finishes |

④/⑤/⑥ are recorded for template sampling only; none used as a standalone variant or to hit the budget.

## Budget decision
Simple band (8-12). 10 candidate anchors (2 origin + 8 forked), each fork one primary structural axis. Coverage-first; no padding. Object's honest structural vocabulary is edge-geometry-heavy plus a small number of blade-body / handle / skeleton candidates; that is fully covered, so no `underfilled_reason` needed (sits comfortably inside the simple band).

## Variant cards (one per fork)
```yaml
- variant_id: rec_fabric_scissors_var_pinking_n9
  source_type: forked_anchor
  parent_record_id: rec_..._002_png_8904372f...
  primary_axis: {slot: blade_edge_geometry, diversity_axis: ③(+N), target_candidate: pinking_zigzag N=9}
  structural_delta: {change: [cutting side of _metal_plate/_blade_bevel -> loop-emitted 9 meshing triangular teeth], keep_parts: [lower_arm, upper_arm, pivot_screw, large_finger_loop, small_thumb_loop], joint_policy: preserve pivot_screw revolute, interface_policy: opposing tooth rows interlock at shear line}
  multiplicity: {applies: true, target_n: 9, copied_object: tooth_i, placement_rule: even spacing along cutting edge}
- variant_id: rec_fabric_scissors_var_pinking_n15
  source_type: forked_anchor
  parent_record_id: rec_..._002_png_8904372f...
  primary_axis: {slot: blade_edge_geometry, diversity_axis: N, target_candidate: pinking N=15}
  structural_delta: {change: [same _pinking_teeth loop, fine count 15], keep_parts: [lower_arm, upper_arm, pivot_screw, large_finger_loop, small_thumb_loop], joint_policy: preserve, interface_policy: meshing rows}
  multiplicity: {applies: true, target_n: 15, copied_object: tooth_i, placement_rule: even spacing}
- variant_id: rec_fabric_scissors_var_scalloping
  source_type: forked_anchor
  parent_record_id: rec_..._002_png_8904372f...
  primary_axis: {slot: blade_edge_geometry, diversity_axis: ③, target_candidate: scalloping_wave}
  structural_delta: {change: [cutting side -> loop-emitted convex/concave arc scallops], keep_parts: [lower_arm, upper_arm, pivot_screw, loops], joint_policy: preserve}
- variant_id: rec_fabric_scissors_var_serrated
  source_type: forked_anchor
  parent_record_id: rec_..._002_png_8904372f...
  primary_axis: {slot: blade_edge_geometry, diversity_axis: ③, target_candidate: micro_serrated (lower edge only)}
  structural_delta: {change: [fine micro-serration teeth on lower_cutting_bevel only; straight-line cut], keep_parts: [lower_arm, upper_arm, pivot_screw, upper_cutting_bevel, loops], joint_policy: preserve}
- variant_id: rec_fabric_scissors_var_duckbill
  source_type: forked_anchor
  parent_record_id: rec_..._001_png_bf8f7c7d...
  primary_axis: {slot: blade_body_form, diversity_axis: ③, target_candidate: duckbill_paddle (appliqué)}
  structural_delta: {change: [lower_shear blade_plate -> broad flat paddle; upper stays pointed], keep_parts: [upper_shear, lower_shear, pivot_screw, handle_loop, screw_head], joint_policy: preserve, interface_policy: paddle rides flat under upper edge}
- variant_id: rec_fabric_scissors_var_curved
  source_type: forked_anchor
  parent_record_id: rec_..._001_png_bf8f7c7d...
  primary_axis: {slot: blade_body_form, diversity_axis: ③, target_candidate: curved_trimming}
  structural_delta: {change: [sweep both blade_plate profiles along shallow arc; tips curve up], keep_parts: [upper_shear, lower_shear, pivot_screw, handle_loop, edge_bevel], joint_policy: preserve}
- variant_id: rec_fabric_scissors_var_symmetric_bow
  source_type: forked_anchor
  parent_record_id: rec_..._001_png_bf8f7c7d...
  primary_axis: {slot: handle_configuration, diversity_axis: ②, target_candidate: symmetric_inline_bows}
  structural_delta: {change: [equal _oval_profile bows centered on blade axis; remove bent crank + pinky_lip; straighten tang], keep_parts: [upper_shear, lower_shear, pivot_screw, blade_plate, screw_head], joint_policy: preserve, interface_policy: bows collinear with cutting axis}
- variant_id: rec_fabric_scissors_var_spring_snips
  source_type: forked_anchor
  parent_record_id: rec_..._001_png_bf8f7c7d...
  primary_axis: {slot: skeleton/mechanism, diversity_axis: ①(+② spring), target_candidate: spring_squeeze_yoke}
  structural_delta: {change: [replace two loops with one U leaf-spring yoke bridging both arms; keep front blade cross on pivot_screw revolute; spring-biased open rest], keep_parts: [upper_shear, lower_shear, pivot_screw, blade_plate, screw_head], joint_policy: preserve pivot revolute, add spring bias; interface_policy: yoke joined to both arms, no floating parts}
```

## Blocked / Excluded
- **left-handed shears**: pure mirror geometry, not a structural template candidate — excluded.
- **electric / rotary fabric cutter**: powered, no scissor pivot — neighbor category, blocked.
- **base-object N-sweep**: a scissor has exactly two blades — no multiplicity on the base; N lives only on the pinking-tooth rows.
- **③ edge sub-splits beyond pinking/scalloping/serrated**: further tooth-profile tweaks would be ④/⑤ cosmetic — not forked.
