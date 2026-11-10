# Source Map — Workspace / ring-blinder

slug `ring_blinder` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__3_ring_binder__001_png_ebac2626578245f29ad4f0eb22ba639f` — picture/Workspace/ring-blinder/001.png
- `rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b` — picture/Workspace/ring-blinder/002.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_ring_blinder_var_closure_strap` | closure_strap | PASS | 5 | 1 |
| `rec_ring_blinder_var_handle_spine` | handle_spine | PASS | 5 | 0 |
| `rec_ring_blinder_var_mount_back_cover` | mount_back_cover | PASS | 4 | 0 |
| `rec_ring_blinder_var_n2` | n2 | PASS | 4 | 0 |
| `rec_ring_blinder_var_ring_dring` | ring_dring | PASS | 4 | 0 |
| `rec_ring_blinder_var_ring_slant` | ring_slant | PASS | 4 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / ring-blinder (3-ring binder)

SLUG: `ring_blinder` · CATEGORY: `Workspace` · SUBCATEGORY: `ring-blinder`
Real object identity (per parent model.py + reference images): an office/school **ring binder** — two hinged cover boards + a center spine carrying a metal ring mechanism that clamps punched sheets. Folder name says "ring-blinder" but the object is a 3-ring binder.

Pattern: **mixed** (single `spine` root; hinged front/back covers as revolute children; a spine-fixed ring mechanism `ring_bar` carrying a shared-rod moving-half assembly `ring_halves` + a linked `lever_tabs`; per-ring multiplicity along the spine).

Richness band: **simple** (target low end). A ring binder has genuinely thin structural vocabulary: two flat cover boards + spine are fixed, and variety lives almost entirely in ring shape, ring count, mechanism side-count, and mount. Coverage-first, no padding — see `underfilled_reason`.

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: ring-blinder
  core_identity: a ring binder — two hinged cover boards on a center spine, with a metal multi-ring mechanism that opens to load/hold punched sheets
  must_keep:
    - two cover boards hinged to a spine (revolute covers)
    - a metal ring mechanism with 2+ ring stations that open and close
    - at least one real non-fixed ring-opening joint
  must_not_become:
    - lever-arch file (single big lever + 2 upright rings on a spring plate)
    - 2-pocket folder / document wallet / portfolio (no rings)
    - planner / 6-ring personal organizer (leather, disc/organizer identity)
    - clipboard / report cover / spiral (coil) notebook
  image_evidence:
    - 001.png: black vinyl binder, hinged covers, spine label sleeve ("1in, 175 sheets"), open binder shows round metal rings on a spine plate with end lever tabs
    - 002.png: white binder, clear overlay pockets on covers, three large round rings on a spine plate with two end lever/booster tabs, one binder standing / one open flat
  parent_evidence:
    - parent B (002): spine + front_cover + back_cover (revolute), ring_bar (FIXED, holds fixed_ring_half_i), ring_halves (single shared moving_hinge_rod REVOLUTE carrying moving_ring_half_i), lever_tabs (linked cam strip, REVOLUTE), paper_stack with reinforced_hole_i; RING_Y = 3 stations; ring_tube() helper builds ring paths from point lists
    - parent A (001): spine + back_cover + front_cover (revolute), ring_plate (FIXED), TWO split ring arms ring_arm_0/1 each own REVOLUTE (both sides open), two independent levers lever_0/1; ring_y = 4 stations; _ring_bank_geometry()/_tube() helpers
```

## Slots & Candidates
| slot | candidate | axis | source_type | evidence |
|---|---|---|---|---|
| ring_form | round / O-ring | ③ | origin_anchor | A & B (curved ring_tube paths) |
| ring_form | D-ring (straight back post) | ③ | forked_anchor | fork `ring_dring` |
| ring_form | slant-D ring (tilted back) | ③ | forked_anchor | fork `ring_slant` |
| ring_mechanism | single moving side (one revolute) | ② | origin_anchor | B (`ring_bar_to_ring_halves`) |
| ring_mechanism | split dual side (both open, two revolutes) | ② | origin_anchor | A (`plate_to_ring_arm_0/1`) |
| mechanism_mount | spine-mounted | ① | origin_anchor | A & B (`spine_to_ring_bar`) |
| mechanism_mount | back-cover-mounted | ① | forked_anchor | fork `mount_back_cover` |
| ring_count (N) | 2 rings | N | forked_anchor | fork `n2` |
| ring_count (N) | 3 rings | N | origin_anchor | B (RING_Y) |
| ring_count (N) | 4 rings | N | origin_anchor | A (ring_y) |
| lever_actuator | linked cam strip (one part) | ② | origin_anchor | B (`lever_tabs`) |
| lever_actuator | two independent levers | ② | origin_anchor | A (`lever_0/1`) |
| handle_or_grip | none | — | origin_anchor | A & B |
| handle_or_grip | folding spine carry handle | ① | forked_anchor | fork `handle_spine` |
| closure | none | — | origin_anchor | A & B |
| closure | fold-over strap-and-catch | ② | forked_anchor | fork `closure_strap` |

Every supported slot reaches ≥2 structurally distinct candidates (ring_form 3, ring_mechanism 2, mechanism_mount 2, ring_count 3, lever_actuator 2, handle 2, closure 2). Cover-board body form has no second family (always flat rounded panels) — recorded, not forked.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed | mechanism mount spine (A,B) vs back-cover (`mount_back_cover`); handle branch none vs folding spine handle (`handle_spine`) |
| ② joint / mechanism | source-backed | single-moving revolute (B) vs split dual-arm revolutes (A); linked lever bar (B) vs two independent levers (A); added fold-over closure revolute (`closure_strap`); all covers revolute |
| ③ primary form family | source-backed | ring cross-section family: round (A,B) / D-ring (`ring_dring`) / slant-D (`ring_slant`). Cover-board family fixed (planar boards) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | spine label sleeve + insert (A); clear overlay view pockets (B); brand decals; "holds N sheets" callout — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only | spine width ~0.5–3 in (capacity); ring Ø ~0.5–3 in; cover H ~0.30–0.31 m; ring open throw ~0.55–0.62 rad; lever ±5° |
| ⑥ material / palette / finish | record_only | black textured vinyl (A) / white plastic (B) / poly / colored board; satin-nickel vs dark metal rings; may ride along as companion only |

①②③ and N are source-backed (origin_anchor or converged forked_anchor). ④⑤⑥ are record_only/companion — never standalone, never counted toward budget.

## Multiplicity / Copy Logic
- **count_param**: number of ring stations = `len(RING_Y)` (B) / `len(ring_y)` (A).
- **N samples**: 2 (`n2`, fork), 3 (B, origin), 4 (A, origin) → 3 representative samples.
- **suggested N_range**: [2, 4] for true ring binders (6/7-ring drifts to personal-organizer neighbor — excluded).
- **copied object**: one ring "station" = {`fixed_ring_half_i`, `moving_ring_half_i`, `fixed_saddle_i`, `moving_saddle_i`, `rivet_i`} on the mechanism + `reinforced_hole_i` on the paper stack.
- **naming**: stable `*_{i}` index suffix per station.
- **placement**: evenly spaced along spine Y, symmetric about center (RING_Y tuple).
- **joint policy**: all moving halves share the ONE `moving_hinge_rod` / `ring_bar_to_ring_halves` revolute — no per-ring joints; paper holes FIXED. Loop-emitted (parent B already loops over RING_Y), so N-forks change only the station tuple.

## Budget Decision
- Candidate anchors (origins + forks) = **8**: 2 origins + 6 forks. Lands at the low end of the simple band (8–12).
- `underfilled_reason`: a ring binder is intrinsically simple — cover boards + spine are a single fixed body family, mechanism ② and count N are already dual/triple-anchored by the two origins, and ③ ring-form + ① mount/handle + ② closure exhaust the honest structural vocabulary. Rather than pad with ④/⑤/⑥ or out-of-category forms (lever-arch, organizer, zip portfolio), we stop at 8.

## Variant Cards
```yaml
- variant_id: rec_ring_blinder_var_ring_dring
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: heavy-capacity D-ring binder, why_same_subcategory: two hinged covers + spine + multi-ring open/close mechanism kept}
  primary_axis: {slot: ring_form, diversity_axis: ③, target_candidate: D-ring straight-back}
  structural_delta:
    change: [reshape ring_tube point lists so fixed half is a straight vertical back post and moving half is a top arc meeting it]
    keep_parts: [spine, front_cover, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack, fixed_hinge_rod, moving_hinge_rod]
    joint_policy: preserve the single ring_bar_to_ring_halves revolute + lever revolute
    interface_policy: moving arc tip meets fixed post tip at closed pose
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [metal palette], forbidden: [ring count, mount, mechanism side count]}
  acceptance_focus: [D outline reads flat-backed, rings still open on the shared revolute]

- variant_id: rec_ring_blinder_var_ring_slant
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: slant-D presentation binder, why_same_subcategory: rings/covers/spine mechanism kept}
  primary_axis: {slot: ring_form, diversity_axis: ③, target_candidate: slant-D angled-back}
  structural_delta:
    change: [tilt the straight back leg forward and use an angled arc for the leaning slant-D profile]
    keep_parts: [spine, front_cover, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack]
    joint_policy: preserve ring_bar_to_ring_halves revolute + lever revolute
    interface_policy: halves meet cleanly at closed pose
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [metal palette], forbidden: [ring count, mount, mechanism side count]}
  acceptance_focus: [leaning profile distinct from round and upright-D]

- variant_id: rec_ring_blinder_var_mount_back_cover
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: back-mounted flat-lay office binder, why_same_subcategory: same covers/spine/rings; only the mechanism root moves}
  primary_axis: {slot: mechanism_mount, diversity_axis: ①, target_candidate: back-cover-mounted}
  structural_delta:
    change: [replace spine_to_ring_bar FIXED with back_cover_to_ring_bar FIXED; reposition metal_plate onto inner back-cover face]
    keep_parts: [spine, front_cover, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack]
    joint_policy: preserve moving + lever revolutes; re-root the mechanism FIXED joint only
    interface_policy: plate seated on inner back cover near spine edge
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [ring shape, ring count, mechanism side count]}
  acceptance_focus: [rings rise from back cover, no floating plate]

- variant_id: rec_ring_blinder_var_n2
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: European 2-ring binder, why_same_subcategory: covers/spine/mechanism kept, only station count changes}
  primary_axis: {slot: ring_count, diversity_axis: N, target_candidate: 2 rings}
  structural_delta:
    change: [set RING_Y to 2 evenly spaced stations; all per-ring loops regenerate]
    keep_parts: [spine, front_cover, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack, moving_hinge_rod]
    joint_policy: preserve the single shared ring_bar_to_ring_halves revolute (no per-ring joints)
    interface_policy: saddles/rivets/halves/holes all track RING_Y
  multiplicity: {applies: true, target_n: 2, copied_object: ring station (halves+saddles+rivet+paper hole), placement_rule: symmetric spacing along Y}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [ring shape, mount, mechanism topology]}
  acceptance_focus: [2 aligned stations, loop-emitted, rings open together]

- variant_id: rec_ring_blinder_var_handle_spine
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: heavy-duty binder with folding spine carry handle, why_same_subcategory: covers/spine/rings intact; handle is an added grip}
  primary_axis: {slot: handle_or_grip, diversity_axis: ①, target_candidate: folding spine handle}
  structural_delta:
    change: [add spine_handle part with two mount lugs on outer spine + spine_to_handle REVOLUTE (Y axis) to fold flat / swing out]
    keep_parts: [spine, spine_board, front_cover, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack]
    joint_policy: add exactly one handle revolute; preserve all ring/cover joints
    interface_policy: lugs seated on spine board, fully supported
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [plastic palette], forbidden: [ring shape, ring count, mechanism change]}
  acceptance_focus: [handle folds on revolute, not floating]

- variant_id: rec_ring_blinder_var_closure_strap
  source_type: forked_anchor
  parent_record_id: rec_workspace__3_ring_binder__002_png_f0e9ff769b6a4ee09bffd6c68a3fd03b
  positioning: {product_archetype: school poly binder with fold-over strap closure, why_same_subcategory: covers/spine/rings intact; strap is an added closure}
  primary_axis: {slot: closure, diversity_axis: ②, target_candidate: fold-over strap-and-catch}
  structural_delta:
    change: [add closure_strap part rooted on front-cover free edge + front_cover_to_closure_strap REVOLUTE folding across the opening face]
    keep_parts: [spine, front_cover, front_board, back_cover, ring_bar, ring_halves, lever_tabs, paper_stack]
    joint_policy: add exactly one closure revolute; preserve all ring/cover joints
    interface_policy: strap hinge lug on front board edge, reaches toward back cover
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [contrasting elastic color], forbidden: [ring shape, ring count, mechanism change]}
  acceptance_focus: [strap folds over closed binder on revolute, supported]
```

## Blocked / Excluded
- **N=6/7 rings** — drifts to 6-ring personal organizer / planner neighbor; excluded to keep binder identity (N_range capped at [2,4]).
- **lever-arch mechanism** — distinct subcategory (single big lever, spring-loaded 2-ring); listed in must_not_become, not forked.
- **zip-around / zippered portfolio closure** — neighbor (portfolio/wallet); the simple strap closure is used instead.
- **third distinct ② ring mechanism** — the two origins already anchor single-moving and split-dual; any further mechanism would drift to lever-arch. Not forked.
- **cover-board body-form family** — always flat rounded panels; no structurally distinct second family; recorded (⑤/⑥) not forked.

## Fork jobs
6 fork jobs emitted (all forked from the cleaner loop-based origin B). Manifest: `/tmp/jobs/ring_blinder.jobs.txt`. Origins A & B need no fork (they anchor round ring, N=3/4, single vs split mechanism, spine mount, linked vs dual lever).
