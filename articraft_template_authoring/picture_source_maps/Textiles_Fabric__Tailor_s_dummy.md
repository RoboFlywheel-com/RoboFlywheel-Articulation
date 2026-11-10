# Source Map — Textiles_Fabric / Tailor's dummy

slug `tailor_s_dummy` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_textiles_fabric__tailor_s_dummy__001_png_a7609e18748744f6b079369ec52ca3d1` — picture/Textiles_Fabric/Tailor's dummy/001.png
- `rec_textiles_fabric__tailor_s_dummy__002_png_c24bfb1920194ad1bd07f609db5bf0e6` — picture/Textiles_Fabric/Tailor's dummy/002.png

## Variants generated this batch (4 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_tailor_s_dummy_var_arms_articulated` | arms_articulated | PASS | 7 | 1 |
| `rec_tailor_s_dummy_var_base_round` | base_round | PASS | 6 | 1 |
| `rec_tailor_s_dummy_var_dials_n6` | dials_n6 | PASS | 9 | 1 |
| `rec_tailor_s_dummy_var_dials_n9` | dials_n9 | PASS | 12 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Textiles_Fabric / Tailor's dummy

slug `tailor_s_dummy` · pattern **mixed** (single fabric torso shell on a vertical adjustable
stand root; parallel articulated hardware children: height pole, clamp/finial knobs, sizing dials,
optional posable arms; sizing-dial multiplicity).

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Tailor's dummy
  core_identity: A headless, legless fabric-covered torso/dress form (shoulders-to-waist/hip) mounted on an adjustable vertical stand for fitting garments.
  must_keep:
    - fabric-covered volumetric torso shell (bust/waist/shoulder envelope), no head, no legs
    - vertical support pole/column rising from a floor base
    - prismatic telescoping height adjustment of the torso on the pole
    - at least one real non-fixed joint (height slide and/or clamp/dial knobs)
  must_not_become:
    - full retail mannequin (with head, arms-and-legs, standing figure)
    - clothing rack / garment rail / coat tree / valet stand
    - garment steamer or ironing board
  image_evidence:
    - "001: warm-grey neoprene adjustable dress form, armless, black recessed vertical seams, rows of chrome/brass sizing thumbwheels down front, chrome telescoping pole on a thin 3-leg tripod with spider feet"
    - "002: cream canvas pinnable torso with jointed dark-wood posable artist arms and hands folded, short cloth neck + wood finial, black telescoping pole on 5-spoke caster star base, side notions tray + wire gauge loop"
  parent_evidence:
    - "001 model.py: _make_torso_mesh superellipse loft (_TORSO_SECTIONS); base part with 4x tripod_leg_/foot_cap_ loop, outer_sleeve, height_collar; height_pole PRISMATIC base_to_height_pole; collar_knob + neck_knob CONTINUOUS; front_dial_z=3 sizing dials each CONTINUOUS torso_to_front_dial_i via _torso_surface placement"
    - "002 model.py: _dress_form_torso_geometry loft; lower_stand with 5x _star_base_leg/caster loop, telescoping outer_sleeve/inner_pole PRISMATIC stand_height; clamp_knob REVOLUTE; top_finial REVOLUTE; static _wood_arm/_wood_hand mesh visuals with shoulder/elbow/wrist balls (NOT jointed); side_tray, wire_gauge_loop accessories"
```

## Slots and Candidates
Real functional layers for a dress form:

- **support_or_base (① skeleton)**: `tripod_radial`(001) / `star_caster_rolling`(002) / `round_cast_disc`(fork@001)
- **arms / appendage topology (① skeleton + ② joint)**: `armless`(001) / `static_wood_arms`(002) / `articulated_posable_arms`(fork@002, shoulder+elbow revolute)
- **adjustment mechanism (② joint)**: `sizing_dial_adjustable`(001, front_dial continuous thumbwheels) / `fixed_pinnable_form`(002, no dials)
- **height mechanism (② joint)**: `telescoping_prismatic + clamp knob`(001,002) — shared, single anchor
- **top_finial / neck (② joint)**: `neck_knob`(001) / `wood_finial`(002) — recorded, not a standalone fork target
- **multiplicity (N sizing dials)**: N{3(001), 6(fork@001), 9(fork@001)} distributed around torso

Each supported slot reaches ≥2 structurally distinct source-backed candidates.

### Slot coverage
| slot | candidates | source |
|---|---|---|
| support_or_base ① | tripod_radial / star_caster / round_cast_disc | 001 / 002 / fork |
| arms ①② | armless / static_wood_arms / articulated_posable_arms | 001 / 002 / fork |
| adjustment ② | sizing_dial_adjustable / fixed_pinnable | 001 / 002 |
| height ② | telescoping_prismatic (+clamp) | 001,002 |
| dial multiplicity N | N3 / N6 / N9 | 001 / fork / fork |

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked) | base: tripod(001) / star-caster(002) / round-disc(fork); arm topology: armless(001) / arms-present(002,fork) |
| ② joint / mechanism | source-backed (origin + forked) | prismatic telescoping height(001,002); continuous sizing dials(001); revolute clamp knob & neck finial(001,002); NEW articulated shoulder+elbow revolute arms(fork@002) |
| ③ primary form family | source-backed (record_only) | volumetric fabric torso superellipse envelope — both origins share the same body family; no distinct ③ candidate honest here (see underfilled note) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | recessed vertical seams, waist band, shoulder/front seam tapes, sizing-dial faces/screw slots; extrapolate pin-marking guide lines, brand label — host-conformal only, no dedicated variant |
| ⑤ proportion / size / travel | record_only | height travel ~0.22–0.25 m prismatic; torso bust Ø ~0.35–0.44; female bust-waist vs straighter male/child proportion; ride-along only |
| ⑥ material / palette / finish | record_only | warm-grey neoprene(001) / cream canvas(002); chrome vs satin-black pole; brass vs chrome dials; worn-wood arms; ride-along only |

## Multiplicity / Copy Logic
- **count_param**: number of front/side sizing dials (origin `front_dial_z` tuple length = 3).
- **copied object**: `front_dial_{idx}` part (dial_stem + dial_face + screw_slot) with continuous joint `torso_to_front_dial_{idx}`.
- **N samples**: 3 (origin 001), 6 (fork), 9 (fork).
- **suggested N_range**: [3, 12] (real adjustable forms carry ~8–12 sizing wheels around bust/waist/hip).
- **naming**: `front_dial_{idx}` / joint `torso_to_front_dial_{idx}` (stable indexed).
- **placement_rule**: dials seated on the torso surface via `_torso_surface(theta, z)`; distribute across bust/waist/hip z-bands and left/right of center-front as N grows.
- **joint_policy**: each dial keeps its own CONTINUOUS thumbwheel joint; multiplicity fork changes only count/placement, no body/base/category change.

## Budget Decision
- Richness band: **simple (8–12)** — this is a low-complexity object with a shared torso form family and a small honest structural vocabulary.
- Candidate anchors (origins + forks): **12** — base×3, arms×3, adjustment×2, height×1, dial-N samples×3 (N3/N6/N9). Coverage-first, no padding.
- Fork jobs emitted: **4** (round-disc base, articulated arms, dials N6, dials N9).
- `underfilled_reason`: Axis ③ (primary form family) has no second honest structural candidate — both origins are the same volumetric fabric-torso envelope, and alternative "body families" (male/child/hip-length) are proportion ⑤, not ③; recorded as ⑤ record_only rather than forked to avoid padding. No compatibility probes needed (all forks combine cleanly with the shared pole/torso interface).

## Variant Cards
```yaml
- variant_id: rec_tailor_s_dummy_var_base_round
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__tailor_s_dummy__001_png_a7609e18748744f6b079369ec52ca3d1
  positioning: {product_archetype: weighted round cast-iron / domed disc dress-form base, why_same_subcategory: same fabric torso + telescoping pole; only the floor base topology changes}
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: round_cast_disc_base}
  structural_delta:
    change: [replace 4x radial tripod_leg_/foot_cap_ loop with a single solid domed round cast disc base + short pedestal collar under the pole]
    keep_parts: [torso, torso_shell, height_pole, inner_pole, outer_sleeve, base_to_height_pole, front_dial_0..2, collar_knob]
    joint_policy: preserve height prismatic + dial/clamp joints; no new base joint
    interface_policy: pole seats vertically at disc center; disc rests flat on floor
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [cast-metal palette, disc diameter], forbidden: [adding arms, changing dial count, casters]}
  acceptance_focus: [pole centered on disc, disc on floor, height prismatic still raises torso]

- variant_id: rec_tailor_s_dummy_var_arms_articulated
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__tailor_s_dummy__002_png_c24bfb1920194ad1bd07f609db5bf0e6
  positioning: {product_archetype: posable artist-mannequin dress form with jointed wooden arms, why_same_subcategory: fabric torso on stand remains the identity; arms become truly articulated instead of static}
  primary_axis: {slot: arms, diversity_axis: ②, target_candidate: articulated_shoulder_elbow_revolute_arms}
  structural_delta:
    change: [split each static wood arm into upper_arm + forearm(+hand) links joined by revolute shoulder and elbow joints mounted at the torso shoulder balls]
    keep_parts: [upper_stage, torso_shell, lower_stand, star base spokes/casters, stand_height, shoulder_ball_0/1]
    joint_policy: add exactly the shoulder + elbow revolute mechanism per arm; keep height prismatic and existing knobs
    interface_policy: shoulder pivot at shoulder_ball; elbow pivot at elbow_ball; wrist/hand fixed to forearm
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: mirrored left/right}
  companion_variations: {allowed_④⑤⑥: [wood finish tone], forbidden: [changing base type, adding sizing dials, changing torso family]}
  acceptance_focus: [arms swing at shoulder/elbow within human limits, hands stay attached, no float]

- variant_id: rec_tailor_s_dummy_var_dials_n6
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__tailor_s_dummy__001_png_a7609e18748744f6b079369ec52ca3d1
  positioning: {product_archetype: adjustable dress form with 6 sizing thumbwheels (bust/waist/hip, front + sides), why_same_subcategory: identical form, denser sizing-dial copy set}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 6_sizing_dials}
  structural_delta:
    change: [extend front_dial loop from 3 to 6 dials distributed across bust/waist/hip z-bands and left/right of center-front via _torso_surface(theta,z)]
    keep_parts: [torso, torso_shell, base tripod, height_pole, front_dial part template, torso_to_front_dial_ joint template]
    joint_policy: each dial keeps its own CONTINUOUS thumbwheel joint
    interface_policy: dial stems seat on torso surface points
  multiplicity: {applies: true, target_n: 6, copied_object: front_dial_{idx}, placement_rule: front + symmetric side seats across 3 z-bands}
  companion_variations: {allowed_④⑤⑥: [dial-face metal], forbidden: [base/arm/height change, torso family change]}
  acceptance_focus: [6 indexed dials loop-emitted, each articulated, seated on shell]

- variant_id: rec_tailor_s_dummy_var_dials_n9
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__tailor_s_dummy__001_png_a7609e18748744f6b079369ec52ca3d1
  positioning: {product_archetype: fully adjustable dress form with 9 sizing thumbwheels around torso, why_same_subcategory: same form, upper multiplicity sample}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 9_sizing_dials}
  structural_delta:
    change: [extend front_dial loop to 9 dials across bust/waist/hip and front/side seats via _torso_surface(theta,z)]
    keep_parts: [torso, torso_shell, base tripod, height_pole, front_dial part template, torso_to_front_dial_ joint template]
    joint_policy: each dial keeps its own CONTINUOUS thumbwheel joint
    interface_policy: dial stems seat on torso surface points
  multiplicity: {applies: true, target_n: 9, copied_object: front_dial_{idx}, placement_rule: 3 z-bands x front/left/right seats}
  companion_variations: {allowed_④⑤⑥: [dial-face metal], forbidden: [base/arm/height change, torso family change]}
  acceptance_focus: [9 indexed dials loop-emitted, each articulated, no collision]
```

## Blocked / Excluded
- ③ alternate torso body-family (male/child/hip-length skirt form): proportion ⑤, not a distinct ③ structural family — record_only, not forked (avoids padding; drives `underfilled_reason`).
- Expandable/hinged torso panels (real adjustable-form internal cam): shell is a single loft mesh; genuine panel articulation is high-risk and not source-backed — blocked.
- Compatibility probes: none needed; all forks share the pole/torso mating interface with no risky combination.
