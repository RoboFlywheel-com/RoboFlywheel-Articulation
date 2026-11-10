# 0611 / Air_blower — template source map (P0 draft)
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: mixed (parallel_children drive-train on P2 + multiplicity accordion/blades)

parents:
- P1 = rec_picturex_0611__air_blower__001__png__airflex_batch_20260710_465e99de07bf49979cb7897a9fe752d3 — picture/0611/Air_blower/001.png — manual fireplace/hand squeeze BELLOWS (two hinged teardrop wooden boards, 4-fold leather accordion, brass nozzle, one-way intake flap, wrist strap). Free anchor.
- P2 = rec_picturex_0611__air_blower__002__png__airflex_batch_20260710_e56fe5260dbc45e6b323504cd56865d6 — picture/0611/Air_blower/002.png — manual HAND-CRANK CENTRIFUGAL blower (volute drum housing, crank -> shaft -> 18-blade squirrel-cage fan wheel, adjustable aluminum outlet tube, rear grille, molded top grip, trigger). Free anchor.

canonical_baselines: none (both parents compile OK; used directly as anchors)
underfilled_reason: n/a (13 candidate anchors converged, within 12–18 "normal" budget)

## subcategory_contract
core_identity: a hand-held or bench air-moving device that draws ambient air at an intake and expels a directed stream through a nozzle/outlet, driven by a human-powered or motor-powered impeller/compression element.
must_keep:
  - function: intake -> pressurize (impeller or compression chamber) -> directed air exit at a nozzle/outlet
  - structure: a body/chamber, a moving air-mover (fan wheel OR squeeze bellows), an outlet, and an intake
  - articulation: at least one real non-fixed joint driving the air-mover (REVOLUTE squeeze, CONTINUOUS crank/rotor, or PRISMATIC stroke)
must_not_become: [vacuum cleaner, hair dryer, spray/paint gun, air compressor tank, desk/pedestal fan, respirator, drone/PC fan]
image_evidence:
  - 001.png: wooden pear-shaped bellows, black leather bag with brass tacks, tapered brass nozzle, leather wrist strap, fire below (fireplace use)
  - 002.png: black plastic volute drum, side crank handle with free grip, brushed-aluminum telescoping outlet tube, molded carry grip
parent_evidence:
  - P1: parts lower_board/upper_board/intake_flap/bellows_fold_1..4; joints board_pivot(REVOLUTE)+<fold>_compression(mimic)+intake_hinge; helpers _board_shape/_bellows_fold/_nozzle_shell/_wrist_loop
  - P2: parts housing/nozzle/crank/drive_shaft/fan_rotor/crank_grip/trigger; joints housing_to_crank(CONTINUOUS)+housing_to_shaft/housing_to_rotor(mimic)+housing_to_nozzle+crank_to_grip+housing_to_trigger; BlowerWheelGeometry(18 blades), KnobGeometry grip; helpers _cylinder_y/_cylinder_x/_tapered_tube_x/_rear_grille

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| body_form | teardrop hinged boards (accordion) | ③ | origin_anchor | P1 lower_board/upper_board + folds | board_pivot | anchored |
| body_form | volute centrifugal drum | ③ | origin_anchor | P2 housing main_body | housing_to_rotor | anchored |
| body_form | in-line axial barrel | ③ | forked_anchor | rec_air_blower_var_axial_inline_barrel (from P2) | housing/main_body, outlet_socket | converged |
| body_form | horizontal canister/tank | ③ | forked_anchor | rec_air_blower_var_canister_tank (from P2) | housing/main_body | converged |
| body_form | spherical turbine pod | ③ | forked_anchor | rec_air_blower_var_spherical_turbine_pod (from P2) | housing/main_body | converged |
| body_form | single squeeze rubber bulb | ③ | forked_anchor | rec_air_blower_var_rubber_bulb (from P1) | bulb body + nozzle_shell + intake_flap | converged |
| motion_mechanism/impeller | manual squeeze (revolute) | ② | origin_anchor | P1 board_pivot | board_pivot | anchored |
| motion_mechanism/impeller | crank -> continuous centrifugal wheel | ② | origin_anchor | P2 crank/fan_rotor | housing_to_crank/housing_to_rotor | anchored |
| motion_mechanism/impeller | axial propeller impeller | ② | forked_anchor | rec_air_blower_var_axial_impeller (from P2) | fan_rotor/fan_wheel, housing_to_rotor | converged |
| motion_mechanism/impeller | prismatic foot-pump stroke | ② | forked_anchor | rec_air_blower_var_foot_pump_prismatic (from P1) | upper_board, board_pivot->prismatic | converged |
| outlet/nozzle | tapered brass nozzle (inserted) | ③ | origin_anchor | P1 nozzle_shell/nozzle_rim | fixed on lower_board | anchored |
| outlet/nozzle | adjustable straight aluminum tube | ③ | origin_anchor | P2 nozzle/metal_tube | housing_to_nozzle | anchored |
| outlet/nozzle | flexible corrugated duct | ③ | forked_anchor | rec_air_blower_var_flex_duct_outlet (from P2) | nozzle/metal_tube, housing_to_nozzle | converged |
| intake | one-way leather flap valve | ③ | origin_anchor | P1 intake_flap/intake_hinge | intake_hinge | anchored |
| intake | spoked rear grille | ③ | origin_anchor | P2 intake_grille (_rear_grille) | fixed on housing | anchored |
| intake | foam/mesh filter cap | ③ | forked_anchor | rec_air_blower_var_filter_intake (from P2) | housing/intake_grille | converged |
| handle/grip | wooden board handle + wrist strap | ③ | origin_anchor | P1 handle end + wrist_strap | fixed on boards | anchored |
| handle/grip | molded horizontal top grip | ③ | origin_anchor | P2 housing handle | fixed on housing | anchored |
| handle/grip | pistol grip (downward) | ③ | forked_anchor | rec_air_blower_var_pistol_grip (from P2) | housing handle, housing_to_trigger | converged |
| multiplicity(fan blades) | N=8 | N | forked_anchor | rec_air_blower_var_fan_blades_8 (from P2) | fan_rotor BlowerWheelGeometry | converged |
| multiplicity(fan blades) | N=32 | N | forked_anchor | rec_air_blower_var_fan_blades_32 (from P2) | fan_rotor BlowerWheelGeometry | converged |
| multiplicity(bellows folds) | N=2 | N | forked_anchor | rec_air_blower_var_bellows_folds_2 (from P1) | BELLOWS_FOLDS / <fold>_compression | converged |
| multiplicity(bellows folds) | N=6 | N | forked_anchor | rec_air_blower_var_bellows_folds_6 (from P1) | BELLOWS_FOLDS / <fold>_compression | converged |

## Multiplicity / Copy Logic
- Fan blades (P2):
  - count_param: BlowerWheelGeometry blade-count (4th positional arg, origin = 18)
  - N samples: 8 (converged), 18 (origin_anchor), 32 (converged)
  - suggested N_range: 6–40
  - copied object: single swept fan blade; naming: internal to BlowerWheelGeometry mesh; placement: radial even spacing about rotor axis; joint policy: single housing_to_rotor CONTINUOUS mimic (blades rigid within fan_rotor)
- Bellows folds (P1):
  - count_param: number of BELLOWS_FOLDS entries (origin = 4)
  - N samples: 2 (converged), 4 (origin_anchor), 6 (converged)
  - suggested N_range: 2–8
  - copied object: bellows_fold part (fold_shell via _bellows_fold); naming: bellows_fold_<i>; placement: stacked/telescoping along +Z between boards; joint policy: each fold gets its own <fold>_compression REVOLUTE mimic of board_pivot with monotonically increasing angle_ratio
- Other homogeneous parts (record_only, not forked): P2 cover_screw_0..3 (N=4), grille spokes (N=6), KnobGrip ribs (N=14); P1 perimeter_tack_* (N=12 per board), grain_line_* — cosmetic, exposed as copy loops but not candidate anchors.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | Two topologies present across parents: single-root drive-train w/ parallel children (P2 housing -> nozzle/crank/shaft/rotor/grip/trigger) vs hinged-boards + mimic accordion chain (P1). Forks preserve their parent topology (no ① standalone fork converged; body-form ③ forks reuse existing topology). |
| ② joint / mechanism type | source-backed | REVOLUTE squeeze (P1), CONTINUOUS crank/rotor (P2), plus converged axial-propeller impeller and revolute->PRISMATIC foot-pump. |
| ③ primary form family | source-backed | body_form (boards / volute drum / axial barrel / canister / spherical pod / rubber bulb), outlet (brass nozzle / straight tube / flex duct), intake (flap / grille / filter cap), handle (board / top grip / pistol grip). |
| ④ surface decoration | record_only / world_knowledge_extrapolation | brass tacks + oiled wood grain (P1); molded ribs, front_seam, cover screws, foot pads (P2). May ride as companion (finger ridges on pistol grip, mesh perforations) — no standalone fork. |
| ⑤ proportion / size / travel | record_only | P1 ~0.70 m board, ~5° squeeze; P2 ~0.146 m drum, nozzle ±0.35 rad twist, trigger 0–0.26 rad. Companion-only (canister length, foot-pump stroke). |
| ⑥ material / palette / finish | record_only | P1 oiled walnut / black leather / aged brass; P2 black plastic / brushed aluminum / gunmetal / dark rubber. Companion-only (safety-orange shell, rubber bulb). |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| (none converged) | | | | |

## Blocked / Excluded
- backpack / engine blower: would bundle body_form ③ + support/harness ③ + mechanism ② (worn engine unit) — excluded to keep single-axis purity; revisit as support-only fork if needed.
- pedestal/stand-mounted blower: support/base form is borderline ⑤ proportion; excluded to avoid a weak ⑤-driven anchor.
- axial-impeller + inline-barrel together: kept as two separate single-axis forks (② impeller vs ③ body); combined pairing would be a bundled-axis change (only allowed as a compatibility_probe, not converged here).

## GATE P1 Verification (machine)
- normal variants forked & accepted: 13 (all exit 0)
- compatibility probe-only variants: 0
- total synced source records after confirmation: 15 (2 origins + 13 normal variants)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=Air_blower, parent_record_id set (verified in data/index/subcat/0611__Air_blower.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
