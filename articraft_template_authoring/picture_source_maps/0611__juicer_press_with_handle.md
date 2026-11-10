# 0611 / juicer_press_with_handle - template source map

pattern: tabletop manual juicer press with frame, strainer/cup, pressing head, and force-transmission handle
parents: 1 origin record from `picture/0611/juicer_press_with_handle`
canonical_baselines: none
underfilled_reason: refill 20260713 added C-frame, rack-pinion, and bench-clamp anchors; still short of the normal 8-anchor budget by 3 source-backed anchors (toggle/pivoting-cone/dual-post retries did not converge)

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| press_frame | original lever juicer press | ①/② | origin_anchor | `rec_picturex_0611__juicer_press_with_handle__001__png_4f95d74d2d3847cd8bdb9c4751cc97b7` | frame, cup/strainer, ram/head, handle linkage | origin |
| force_mechanism | vertical screw press with handwheel | ② | forked_anchor | `rec_juicer_press_with_handle_var_screw_press` | handwheel, threaded screw/ram, nut housing, press head; 4 non-fixed joints | PASS |
| press_frame | C-frame long-lever citrus press | ① | blocked/retry_needed | `rec_juicer_press_with_handle_var_c_frame_lever` planned from origin 001 | C-frame, long lever, ram, cup | not started in retry batch |

## Multiplicity / Copy Logic

- count_param: handwheel spokes/knobs, feet, strainer perforations.
- N samples: screw handwheel spokes/knobs in passed fork; original press parts from source image.
- suggested N_range: spokes 3-6; feet 3-4; strainer holes 12-32.
- copied object / naming / placement / joint policy: spokes and perforations should be host visuals emitted by loops; ram/screw uses prismatic/continuous joints according to mechanism.

| press_frame | C-frame long-lever citrus press | ① | forked_anchor | `rec_juicer_press_with_handle_var_c_frame_lever_refill` | C-shaped frame, cup/strainer, descending ram, long lever; 5 non-fixed joints | PASS |
| force_mechanism | rack-and-pinion handled press | ② | forked_anchor | `rec_juicer_press_with_handle_var_rack_pinion_refill` | side handle, pinion housing, rack ram, strainer cup; 4 non-fixed joints | PASS |
| support_or_base | bench-clamp mounted press | ① | forked_anchor | `rec_juicer_press_with_handle_var_bench_clamp_press_refill` | clamp base, upright frame, lever handle, cup/strainer; 6 non-fixed joints | PASS |
| force_mechanism | over-center toggle linkage press | ② / N | blocked/retry_needed | `rec_juicer_press_with_handle_var_toggle_linkage_refill` | paired toggle links, sliding ram, long handle | provider timeout/no persisted record |
| press_head | hinged citrus cone press | ③ | blocked/retry_needed | `rec_juicer_press_with_handle_var_pivoting_cone_refill` | conical reamer cup, hinged upper press dome | interrupted before persisted record |
| press_frame | dual-post screw press | ① / N | blocked/retry_needed | `rec_juicer_press_with_handle_var_dual_post_screw_refill` | two guide posts, top crosshead, screw/ram, T-handle | interrupted before persisted record |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | partial source-backed | original frame plus screw-press fork; C-frame still retry_needed |
| ② joint / mechanism type | source-backed | lever/ram origin, screw/handwheel fork, press head travel |
| ③ primary form family | source-backed | manual tabletop citrus/fruit press with cup/strainer |
| ④ surface decoration | record_only | strainer holes, knobs, frame fillets, host-conformal only |
| ⑤ proportion / size / travel | record_only | ram travel and frame height inherited from origin/fork |
| ⑥ material / palette / finish | record_only | cast metal frame, stainless strainer, rubber feet |

## Compatibility Probes

None yet.

## Blocked / Excluded

- `rec_juicer_press_with_handle_var_c_frame_lever`: planned but not started after interrupted first batch; retry if more topology coverage is needed.
- Blender, electric juicer, citrus reamer without press frame: excluded as category drift.
