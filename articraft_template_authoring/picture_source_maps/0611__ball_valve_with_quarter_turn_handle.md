# 0611 / ball_valve_with_quarter_turn_handle — template source map
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: linear_chain (body -> single revolute -> rotor), with multiplicity on flanged bolt circle
parents: rec_picturex_0611__ball_valve_with_quarter_turn_handle__001__png__airflex_batch_20260710_c15cac650e7c4e2d897ff29893db3af2 (picture/0611/ball_valve_with_quarter_turn_handle/001.png)
canonical_baselines: (none yet)
budget_note: 12 normal candidate anchors + 2 probe-only records; within simple/normal budget.

subcategory_contract:
  category: 0611
  subcategory: ball_valve_with_quarter_turn_handle
  core_identity: a quarter-turn ball valve — a bored spherical ball inside a flow body, sealed by seats, rotated ~90 deg by a stem and a manual lever
  must_keep: [flow body with inlet/outlet ports, internal ported ball + PTFE seats, stem through a packing gland, single ~90 deg lever revolute (body_to_rotor)]
  must_not_become: [gate valve (rising stem, multi-turn handwheel), globe valve, plug/tapered-cock valve, faucet/bibcock tap]
  image_evidence: [two-piece stainless hex body, female-female threaded ports, blue vinyl straight lever parallel to pipe axis, packing gland nut and stop plate under the handle]
  parent_evidence: [parts valve_body + valve_rotor; joint body_to_rotor REVOLUTE axis z lower 0 upper pi/2; ball with straight through-bore; seat_left/seat_right PTFE; gland_nut + stem_packing; handle_lever + grip + handle_hub + stop_tab + retaining_nut; helpers _cylinder_x/_annulus_x/_hex_x/_annulus_z/_hex_z/_thread_rings_x]

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| body_form / port_config | 2-way inline (parent) | ③ | origin_anchor | 001.png, parent valve_body | valve_body, ball straight-bore | converged |
| body_form / port_config | 3-way L-port | ①/③ | forked_anchor | var_3way_lport | third port, L-bore ball | converged |
| body_form / port_config | 3-way T-port | ③ (ball internal_structure) | forked_anchor | var_3way_tport | third port, T-bore ball | converged |
| body_form / port_config | angle (90 deg elbow) body | ① | forked_anchor | var_angle_body | bent valve_body, angle ball bore | converged |
| connection_ends | threaded NPT female-female (parent) | ① | origin_anchor | parent _thread_rings_x, port lips | left/right_threads, port_lip | converged |
| connection_ends | flanged raised-face | ① | forked_anchor | var_flanged_ends | flange discs, flange_bolt_hole_i | converged |
| connection_ends | compression / ferrule | ① | forked_anchor | var_compression_ends | ferrule ring, hex nut | converged |
| connection_ends | hose barb | ① | forked_anchor | var_hose_barb_ends | stepped barb spigots | converged |
| connection_ends | sweat / solder cup | ① | forked_anchor | var_solder_ends | plain solder socket | converged |
| handle_or_grip | straight lever (parent) | ③ | origin_anchor | 001.png, parent handle_lever+grip | handle_lever, grip | converged |
| handle_or_grip | tee-bar handle | ③ | forked_anchor | var_tee_handle | crossbar on handle_hub | converged |
| handle_or_grip | oval loop (butterfly) lever | ③ | forked_anchor | var_oval_lever | oval loop plate | converged |
| handle_or_grip | lockable lever + lockout ears | ③ | forked_anchor | var_lockable_lever | lug on lever + stop_plate ears | converged |
| stem_bonnet / mounting | integral packing gland (parent) | ① | origin_anchor | parent gland_nut, stem_packing | gland_nut, stem_packing | converged |
| stem_bonnet / mounting | ISO 5211 actuator pad | ① | forked_anchor | var_iso5211_pad | mounting pad, iso_bolt_hole_i, drive stub | converged |
| stem_bonnet / mounting | extended stem/bonnet column | ① | forked_anchor | var_stem_extension | standoff column, raised rotor | converged |

## Multiplicity / Copy Logic
- count_param: flange_bolt_hole_count (flanged-body variant)
- N samples: 4 (flanged anchor default), 8 (var_flange_boltholes)
- suggested N_range: 4 / 6 / 8 / 12
- copied object / naming / placement / joint policy: copied_object = flange_bolt_hole; naming = flange_bolt_hole_i; placement = even radial spacing on a fixed bolt circle; joint_policy = fixed cuts in valve_body, no new joints
- note: gated on var_flanged_ends converging (parent threaded body has no bolt circle)

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | 2-way inline (parent) vs 3-way L-port vs 3-way T-port vs angle body; end-connection interface threaded/flanged/compression/barb/solder; stem/bonnet integral vs ISO pad vs extended column |
| ② joint / mechanism type | source-backed | single 90 deg REVOLUTE ball (body_to_rotor) is the fixed identity mechanism across all ordinary variants; gear-operated worm+handwheel input tested only as compatibility_probe |
| ③ primary form family | source-backed | operator family: straight lever / tee-bar / oval loop / lockable lever; ball-bore family: straight / L / T |
| ④ surface decoration | record_only / world_knowledge_extrapolation | molded "BALL VALVE" text and directional arrows on lever, size/pressure stamps on body, lockout/tag lug — host-conformal only, no dedicated variant |
| ⑤ proportion / size / travel | record_only | nominal size DN15..DN50; lever length ~1 hand-span; stem/bonnet height (esp. extended-stem); travel fixed at 0..pi/2 |
| ⑥ material / palette / finish | record_only | body: polished/brushed stainless, brass/bronze (sweat), cast-iron gray (flanged), PVC; grip: blue (parent) / red / yellow / black vinyl |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| gear operator + handwheel | rec_ball_valve_with_quarter_turn_handle_var_gear_operated | ② mechanism + ⑥ | multi-turn handwheel input vs 90 deg ball output; gate-valve silhouette drift | converged |
| flange bolt-hole N | rec_ball_valve_with_quarter_turn_handle_var_flange_boltholes | N multiplicity gated on flanged anchor | bolt count copy logic only after flanged forked_anchor exists | converged |

## Blocked / Excluded
- round handwheel operator (direct, no lever): blocked — a multi-turn round wheel reads as a gate valve and breaks the quarter-turn identity; only allowed via the gear_operated probe.
- separate articulated padlock part on lockable lever: blocked — lockout is a fixed lug/ear feature, not a second joint.
- full actuator body on ISO 5211 pad: blocked — out of subcategory; only the mounting interface is modeled.
- material-only forks (brass / PVC / red-grip): excluded from candidate count — ⑥ record_only, may ride along on structural forks.

## GATE P1 Verification (machine)
- normal variants forked & accepted: 12 (all exit 0)
- compatibility probe-only variants: 2 (`rec_ball_valve_with_quarter_turn_handle_var_gear_operated`, `rec_ball_valve_with_quarter_turn_handle_var_flange_boltholes`)
- total synced source records after confirmation: 15 (1 origin + 12 normal variants + 2 probe-only variants)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=ball_valve_with_quarter_turn_handle, parent_record_id set (verified in data/index/subcat/0611__ball_valve_with_quarter_turn_handle.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
