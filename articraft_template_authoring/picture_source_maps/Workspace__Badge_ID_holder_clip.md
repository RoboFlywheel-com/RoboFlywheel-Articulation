# Source Map — Workspace / Badge_ID holder clip

slug `badge_id_holder_clip` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d` — picture/Workspace/Badge_ID holder clip/002.png
- `rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735` — picture/Workspace/Badge_ID holder clip/001.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_badge_id_holder_clip_var_bulldog` | bulldog | PASS | 2 | 0 |
| `rec_badge_id_holder_clip_var_card_frame` | card_frame | PASS | 2 | 0 |
| `rec_badge_id_holder_clip_var_magnetic_clamp` | magnetic_clamp | PASS | 2 | 0 |
| `rec_badge_id_holder_clip_var_ring_loop` | ring_loop | PASS | 2 | 0 |
| `rec_badge_id_holder_clip_var_teeth_n10` | teeth_n10 | PASS | 2 | 0 |
| `rec_badge_id_holder_clip_var_teeth_n3` | teeth_n3 | PASS | 2 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / Badge_ID holder clip

slug: `badge_id_holder_clip` · richness band: **simple** · pattern: **mixed** (linear clip_body root; revolute spring jaw + continuous swivel badge connector; jaw-serration multiplicity)

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Badge_ID holder clip
  core_identity: a small worn device that attaches an ID/name badge to a person's clothing — a clothing-grip mechanism at one end and a badge-holding connector at the other, usually joined by a swivel.
  must_keep:
    - a clothing/fabric attachment mechanism (spring pinch clip, magnetic sandwich, or reel body)
    - a badge/ID connector (clear strap, card frame, or ring) that holds or receives the badge
    - a real non-fixed joint (jaw revolute and/or connector swivel continuous)
  must_not_become:
    - plain alligator/electrical/cable clip with no badge connector
    - lanyard or its hardware (bare hook, carabiner, split keyring as the whole object)
    - binder/bulldog paper clip, chip-bag clip, or picture frame
    - fridge magnet / jewelry clasp
  image_evidence:
    - 001 & 002: stamped chrome spring pinch-jaw (alligator) clip with serrated mouth and folded side cheeks
    - clear/frosted vinyl strap tab behind the clip with a punched oblong slot + round grommet hole
    - round snap button (swivel) joining the clear strap to the metal clip; strap can rotate flat/vertical
    - 002 left clip shown open (jaw pivoted up) — visible spring hinge
  parent_evidence:
    - 002: parts clip_body / spring_jaw / badge_connector; body_to_jaw REVOLUTE (axis y, torsion_spring+hinge_pin), body_to_connector CONTINUOUS (axis z, swivel_boss+swivel_button_ring); _tooth_bar(count,...) helper -> lower_jaw_teeth(6), upper_front_teeth(5); perforated_clear_strap with slot + grid rect_holes
    - 001: parts clip_base / jaw / swivel_tab; clip_base_to_jaw REVOLUTE, clip_base_to_swivel_tab CONTINUOUS; hand-written teeth (lower_tooth_0..4, upper_tooth_0..4); _slotted_clear_strap; annular snap button
```

## Slot / Candidate Grid
| slot | candidate | axis | source_type | evidence/record | status |
|---|---|---|---|---|---|
| attachment_mechanism | spring pinch-jaw alligator clip | ① / ② revolute | origin_anchor | 001, 002 | covered |
| attachment_mechanism | bulldog / twin-lever folded clip | ③ clip form | forked_anchor | var_bulldog | emit |
| attachment_mechanism | magnetic two-plate sandwich clamp | ② prismatic | forked_anchor | var_magnetic_clamp | emit |
| attachment_mechanism | retractable reel body | ② | forked_anchor | var_reelbody (**already forked — not re-emitted**) | covered |
| badge_connector | clear perforated vinyl strap (planar) | ③ planar | origin_anchor | 001, 002 | covered |
| badge_connector | rigid open card-holder frame/pocket (volumetric) | ③ | forked_anchor | var_card_frame | emit |
| badge_connector | swivel split-ring / D-ring loop | ③ | forked_anchor | var_ring_loop | emit |
| swivel_joint | snap-button continuous swivel | ② continuous | origin_anchor | 001, 002 | covered |
| jaw_serrations (N) | ~5–6 teeth baseline | N | origin_anchor | 001(5), 002(5&6) | covered |
| jaw_serrations (N) | coarse 3 teeth | N | forked_anchor | var_teeth_n3 | emit |
| jaw_serrations (N) | fine 10 teeth | N | forked_anchor | var_teeth_n10 | emit |

Each supported slot reaches ≥2 structurally distinct candidates: attachment_mechanism (4), badge_connector (3), jaw_serrations N (3 samples). swivel_joint has one real candidate (origin) — a no-swivel/fixed variant would only remove a joint and is recorded, not forked.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed | clip_body+jaw+connector chain (origins); magnetic front_plate+prismatic magnet_backer+connector (fork); reel body (fork, covered) |
| ② joint / mechanism | source-backed | revolute spring jaw + continuous swivel (origins); prismatic magnetic clamp (fork); reel retract (fork, covered) |
| ③ primary form family | source-backed | clip body: alligator jaw (origin) vs bulldog leaves (fork); connector: planar strap (origin) vs volumetric card frame (fork) vs ring loop (fork) |
| ④ surface decoration | record_only | strap perforation grid (grid_holes), badge slot, grommet holes, tooth serrations as host visuals — no dedicated variant |
| ⑤ proportion / size / travel | record_only / companion | jaw open ±0.45 rad, swivel continuous; card window portrait vs landscape (~86×54 mm); ride-along only |
| ⑥ material / palette | record_only / companion | polished/brushed chrome, nickel, brass ring, black magnet, clear/frosted vinyl — ride-along only |

## Multiplicity / Copy Logic
- count_param: `count` argument of `_tooth_bar(count, pitch, tooth_width, bar_width, height)` (002); origins hand/loop-emit ~5–6.
- N samples (source-backed after fork): baseline 5–6 (origin) · 3 (var_teeth_n3) · 10 (var_teeth_n10).
- suggested N_range: [3, 12].
- copied object: single rectangular serration tooth on a back strip; naming: loop-indexed within `lower_jaw_teeth`/`upper_front_teeth` bars; placement: even pitch across `bar_width`; joint policy: FIXED decoration fused to its jaw plate (moves with the jaw's revolute).
- Note: 001 hand-writes teeth; forks are taken from 002 which uses the loop-based `_tooth_bar` helper (template-clean).

## Budget Decision
- Candidate anchors (origins + forks, ④⑤⑥/probes not counted): pinch-jaw clip, bulldog clip, magnetic clamp, reel(covered), clear strap, card frame, ring loop, swivel snap, teeth N baseline, teeth N=3, teeth N=10 = **11** → simple band (8–12). Coverage-first, no padding.
- Fork jobs emitted: **6** (reelbody already covered, not re-emitted; origins need no fork).

## Blocked / Excluded
- pin-back / safety-pin only attachment: would drop the clip identity and drift toward a pin/brooch — blocked.
- lobster/J-hook lanyard clasp as the whole object: drifts to lanyard hardware — blocked.
- belt slide clip: structurally the same spring pinch clip, no new vocabulary — excluded (padding).
- no-swivel (fixed connector) variant: only removes a joint, no new candidate — recorded, not forked.

## Variant Cards
```yaml
- variant_id: rec_badge_id_holder_clip_var_magnetic_clamp
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: magnetic name-badge holder, why_same_subcategory: still holds an ID badge on the wearer via the swivel connector}
  primary_axis: {slot: attachment_mechanism, diversity_axis: ②, target_candidate: prismatic magnetic sandwich clamp}
  structural_delta:
    change: [remove spring_jaw+hinge_pin+torsion_spring+body_to_jaw revolute, add front_plate + magnet_backer part with prismatic clamp joint along +z]
    keep_parts: [clip_body, badge_connector, perforated_clear_strap, swivel_boss, swivel_button_ring, body_to_connector]
    joint_policy: replace revolute pinch hinge with one prismatic magnetic clamp; keep continuous swivel
    interface_policy: magnet_backer closes a fabric gap onto front_plate; swivel button seated on boss unchanged
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [nickel/black magnet finish], forbidden: [fridge magnet, jewelry clasp, keeping a spring jaw]}
  acceptance_focus: [prismatic clamp closes onto front_plate, swivel still rotates 90°, no spring jaw remains]
- variant_id: rec_badge_id_holder_clip_var_card_frame
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: rigid ID card-holder clip, why_same_subcategory: card frame is the badge connector swiveling on the same clip}
  primary_axis: {slot: badge_connector, diversity_axis: ③, target_candidate: rigid open card-holder pocket frame}
  structural_delta:
    change: [replace perforated_clear_strap with back_panel + raised rim border + open card_window + top card_slot]
    keep_parts: [clip_body, spring_jaw, hinge_pin, torsion_spring, swivel_boss, swivel_button_ring, body_to_jaw, body_to_connector]
    joint_policy: preserve both joints; no mechanism change
    interface_policy: frame's clip end keeps button ring seated on boss (continuous swivel)
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [portrait vs landscape card window], forbidden: [picture frame, wallet, lanyard, changing clip/jaw]}
  acceptance_focus: [open card window with retaining rim, swivels on boss, clip mechanism intact]
- variant_id: rec_badge_id_holder_clip_var_ring_loop
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: swivel-ring badge clip, why_same_subcategory: ring is the badge/lanyard connector on the same swivel clip}
  primary_axis: {slot: badge_connector, diversity_axis: ③, target_candidate: split-ring / D-ring loop}
  structural_delta:
    change: [replace perforated_clear_strap with torus ring_loop on a short neck_shank]
    keep_parts: [clip_body, spring_jaw, hinge_pin, torsion_spring, swivel_boss, swivel_button_ring, body_to_jaw, body_to_connector]
    joint_policy: preserve both joints; ring rotates on boss via continuous swivel
    interface_policy: neck_shank seats button ring on boss
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [chrome/brass ring], forbidden: [keychain, carabiner, curtain ring, changing clip/jaw]}
  acceptance_focus: [ring loop swivels on boss, remains a badge clip not a keyring]
- variant_id: rec_badge_id_holder_clip_var_bulldog
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: bulldog-clip badge holder, why_same_subcategory: same spring pinch clip + swivel strap, bulldog silhouette}
  primary_axis: {slot: attachment_mechanism (clip body), diversity_axis: ③, target_candidate: bulldog twin-lever folded clamp}
  structural_delta:
    change: [reshape jaw plates into short wide bulldog leaves + two upturned finger_lever tabs]
    keep_parts: [clip_body, spring_jaw, hinge_pin, torsion_spring, lower_jaw_teeth, upper_front_teeth, badge_connector, perforated_clear_strap, swivel_boss, body_to_jaw, body_to_connector]
    joint_policy: preserve revolute pinch hinge + continuous swivel
    interface_policy: serrated flat mouth; swivel_boss still carries strap
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [mouth width proportion], forbidden: [paper binder clip, chip-bag clip, hair clip, changing connector/mechanism/tooth-count]}
  acceptance_focus: [bulldog silhouette with finger levers, pinch hinge opens, strap swivels]
- variant_id: rec_badge_id_holder_clip_var_teeth_n3
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: coarse-tooth alligator badge clip, why_same_subcategory: same clip, fewer serrations}
  primary_axis: {slot: jaw_serrations, diversity_axis: N, target_candidate: N=3}
  structural_delta:
    change: [set _tooth_bar count=3 for lower_jaw_teeth and upper_front_teeth, rescale pitch]
    keep_parts: [clip_body, spring_jaw, badge_connector, _tooth_bar, body_to_jaw, body_to_connector]
    joint_policy: no joint change
    interface_policy: teeth fused to jaw plates (FIXED)
  multiplicity: {applies: true, target_n: 3, copied_object: single serration tooth, placement_rule: even pitch across bar_width}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any body/mechanism/connector change, hand-written teeth]}
  acceptance_focus: [3 loop-emitted teeth per jaw, spacing regular, nothing else changed]
- variant_id: rec_badge_id_holder_clip_var_teeth_n10
  source_type: forked_anchor
  parent_record_id: rec_workspace__badge_id_holder_clip__002_...
  positioning: {product_archetype: fine-tooth alligator badge clip, why_same_subcategory: same clip, many serrations}
  primary_axis: {slot: jaw_serrations, diversity_axis: N, target_candidate: N=10}
  structural_delta:
    change: [set _tooth_bar count=10 for lower_jaw_teeth and upper_front_teeth, rescale pitch]
    keep_parts: [clip_body, spring_jaw, badge_connector, _tooth_bar, body_to_jaw, body_to_connector]
    joint_policy: no joint change
    interface_policy: teeth fused to jaw plates (FIXED)
  multiplicity: {applies: true, target_n: 10, copied_object: single serration tooth, placement_rule: even pitch across bar_width}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any body/mechanism/connector change, hand-written teeth]}
  acceptance_focus: [10 loop-emitted teeth per jaw, spacing regular, nothing else changed]
```

## Already-covered forked_anchor (do NOT re-emit)
- `rec_badge_id_holder_clip_var_reelbody` — retractable reel body, ② mechanism (attachment_mechanism slot). Counted as a candidate anchor; no job emitted.
