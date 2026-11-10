# pictureX_0611_Butter_maker — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Butter_maker
picture_category: 0611
picture_subcategory: Butter_maker
category_scope: A hand or motor driven butter churn: one closed vessel, a lid carrying a support frame, a vertical dasher shaft reaching into the vessel, and the dasher blades on it. The vessel, lid, frame, shaft and dasher are always present; what varies is the vessel body, how the shaft is driven, the dasher blade family and how the churn is mounted. A plain storage jar with no dasher, and a stand mixer with an open bowl, are out of scope.

sync_records:
  - rec_butter_maker_var_bench_clamp
  - rec_butter_maker_var_box_churn
  - rec_butter_maker_var_ceramic_crock
  - rec_butter_maker_var_clamp_lid
  - rec_butter_maker_var_cross_dasher
  - rec_butter_maker_var_direct_vertical_crank
  - rec_butter_maker_var_electric
  - rec_butter_maker_var_floor_stand
  - rec_butter_maker_var_footed_stand
  - rec_butter_maker_var_gear_teeth_n
  - rec_butter_maker_var_helical_dasher
  - rec_butter_maker_var_hinged_lid
  - rec_butter_maker_var_paddle_holes_n
  - rec_butter_maker_var_paddle_n2
  - rec_butter_maker_var_paddle_n4
  - rec_butter_maker_var_plunger_dash
  - rec_butter_maker_var_plunger_dasher
  - rec_butter_maker_var_rocker
  - rec_butter_maker_var_squat_tub
  - rec_butter_maker_var_stoneware_crock
  - rec_butter_maker_var_top_crank
  - rec_butter_maker_var_whisk_cage
  - rec_butter_maker_var_wood_barrel
  - rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_butter_maker_var_bench_clamp/rev_000001 | reviewed | reference_only | Adds a bench clamp frame and thumbscrew, but this outboard assembly is excluded from the template so mounting never supplies a decorative articulation. |
| rec_butter_maker_var_box_churn/rev_000001 | reviewed | used | Rectangular staved box body with a square lid; a different vessel plan, not a scaled cylinder. |
| rec_butter_maker_var_ceramic_crock/rev_000001 | reviewed | used | Bellied opaque crock profile with a rolled rim instead of the straight glass jar. |
| rec_butter_maker_var_clamp_lid/rev_000001 | reviewed | reference_only | Same machine as the origin plus two toggle clamp arms on the lid; closure hardware only, folded into the shared lid host. |
| rec_butter_maker_var_cross_dasher/rev_000001 | reviewed | used | Two perforated boards crossed at 90 degrees; a distinct dasher blade family. |
| rec_butter_maker_var_direct_vertical_crank/rev_000001 | reviewed | used | The bevel pair is deleted and the crank sits straight on the vertical shaft; three fewer parts and a different drive topology. |
| rec_butter_maker_var_electric/rev_000001 | reviewed | used | A motor housing on the lid replaces the whole hand drive; the shaft is driven with no crank at all. |
| rec_butter_maker_var_floor_stand/rev_000001 | reviewed | used | The frame becomes a floor-standing cradle and the vessel hangs from it, so the frame is the root instead of the vessel. |
| rec_butter_maker_var_footed_stand/rev_000001 | reviewed | reference_only | A short footed base under the same countertop machine; a proportion change on the floor-stand idea, so it would duplicate that candidate. |
| rec_butter_maker_var_gear_teeth_n/rev_000001 | reviewed | reference_only | Only the bevel tooth count changes; decorative count on the same gear, not a structural candidate. |
| rec_butter_maker_var_helical_dasher/rev_000001 | reviewed | used | The blade is a swept helical ribbon rather than a flat board; a distinct dasher family. |
| rec_butter_maker_var_hinged_lid/rev_000001 | reviewed | reference_only | Adds a lid hinge to the shared lid host; closure hardware only. |
| rec_butter_maker_var_paddle_holes_n/rev_000001 | reviewed | reference_only | Only the perforation count in the blade changes; decorative count. |
| rec_butter_maker_var_paddle_n2/rev_000001 | reviewed | reference_only | Two blades on one shaft through an indexed loop; multiplicity evidence, recorded under Multiplicity. |
| rec_butter_maker_var_paddle_n4/rev_000001 | reviewed | reference_only | Four blades on one shaft through the same loop; multiplicity evidence. |
| rec_butter_maker_var_plunger_dash/rev_000001 | reviewed | rejected_duplicate | Same up-and-down plunger construction as rec_butter_maker_var_plunger_dasher with a slightly different grip joint parent. |
| rec_butter_maker_var_plunger_dasher/rev_000001 | reviewed | used | No crank at all: the shaft is a prismatic plunger worked by a top grip; a distinct drive family. |
| rec_butter_maker_var_rocker/rev_000001 | reviewed | reference_only | A rocking lever version of the direct vertical crank; same part tree with a narrower joint range. |
| rec_butter_maker_var_squat_tub/rev_000001 | reviewed | reference_only | A wider shallower version of the crock profile; a proportion change already covered by the ceramic crock candidate and the vessel parameters. |
| rec_butter_maker_var_stoneware_crock/rev_000001 | reviewed | rejected_duplicate | Same construction as rec_butter_maker_var_ceramic_crock with a different glaze colour only. |
| rec_butter_maker_var_top_crank/rev_000001 | reviewed | reference_only | The direct vertical crank moved to the frame top bar; same part tree and axis. |
| rec_butter_maker_var_whisk_cage/rev_000001 | reviewed | used | A wire whisk cage of swept loops instead of a solid blade; a distinct dasher family. |
| rec_butter_maker_var_wood_barrel/rev_000001 | reviewed | used | Staved wooden barrel with real hoop bands; a distinct vessel body. |
| rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274/rev_000001 | reviewed | used | Origin record for 001.png. Supplies the always-present lid, frame and shaft host and four baseline candidates: the glass mason jar, the bevel-gear side crank, the flat perforated blade and the countertop mount. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| vessel_form | glass_mason_jar | straight-walled glass jar with a threaded neck | rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274/rev_000001 | model.py:L26-L46, model.py:L273-L279 | structure | `_jar_shell` builds a genuinely hollow straight glass body with a rolled thread neck. |
| vessel_form | ceramic_crock | bellied opaque crock with a rolled rim | rec_butter_maker_var_ceramic_crock/rev_000001 | model.py:L26-L53, model.py:L283-L311 | structure | The revolved profile is waisted and bellied instead of straight, and the rim is rolled over. |
| vessel_form | wood_barrel | staved wooden barrel with hoop bands | rec_butter_maker_var_wood_barrel/rev_000001 | model.py:L36-L73, model.py:L301-L313 | structure | `_barrel_shell`/`_hoop_band` emit individual staves and real steel hoops, not a smooth revolve. |
| vessel_form | box_churn | rectangular staved box body | rec_butter_maker_var_box_churn/rev_000001 | model.py:L33-L189, model.py:L390-L397 | structure | `_box_churn_body`/`_square_lid_shell` give a square plan whose lid, frame footprint and dasher clearance all change with it. |
| drive_form | bevel_gear_crank | side crank driving the shaft through a bevel pair | rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274/rev_000001 | model.py:L138-L179, model.py:L342-L417 | structure+motion | `_bevel_gear` builds two real toothed wheels on perpendicular axes with `drive_shaft`, `drive_gear` and `vertical_gear` between crank and dasher. |
| drive_form | direct_vertical_crank | crank straight on the vertical shaft | rec_butter_maker_var_direct_vertical_crank/rev_000001 | model.py:L138-L160, model.py:L276-L303 | structure+motion | The bevel pair and drive shaft are gone; the crank turns the dasher axis directly, so three parts disappear from the tree. |
| drive_form | plunger_dasher | up-and-down plunger worked by a top grip | rec_butter_maker_var_plunger_dasher/rev_000001 | model.py:L126-L160, model.py:L238-L290 | structure+motion | The shaft joint is prismatic instead of continuous and there is no crank anywhere in the tree. |
| drive_form | electric_motor | motor housing on the lid driving the shaft | rec_butter_maker_var_electric/rev_000001 | model.py:L130-L237, model.py:L328-L352 | structure+motion | `_motor_housing` stands a real motor with a vent and switch on the lid and drives the shaft with no hand crank. |
| dasher_form | perforated_blade | one flat perforated board | rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274/rev_000001 | model.py:L151-L164, model.py:L432-L455 | structure | `_paddle` cuts a real hole grid through a flat board, matching the blade in 001.png. |
| dasher_form | cross_dasher | two perforated boards crossed at 90 degrees | rec_butter_maker_var_cross_dasher/rev_000001 | model.py:L151-L178, model.py:L446-L470 | structure | `_perforated_board`/`_paddle` union two boards on perpendicular planes, doubling the swept blade area. |
| dasher_form | helical_dasher | swept helical ribbon | rec_butter_maker_var_helical_dasher/rev_000001 | model.py:L151-L187, model.py:L455-L480 | structure | The blade is swept along a helix so its section rotates with height instead of staying planar. |
| dasher_form | whisk_cage | wire whisk cage of swept loops | rec_butter_maker_var_whisk_cage/rev_000001 | model.py:L156-L175, model.py:L444-L470 | structure | `_whisk_loop_points` sweeps real wire loops into an open cage, a wire structure rather than a solid blade. |
| mount_form | countertop | the vessel stands on its own base | rec_picturex_0611__butter_maker__001__png__airflex_batch_20260710_1e7bf8c7df754c2ea25bac719b39e274/rev_000001 | model.py:L76-L133, model.py:L316-L341 | structure | The vessel is the grounded root and the frame is carried by the lid; no extra mount part exists. |
| mount_form | floor_stand | floor-standing cradle carrying the vessel | rec_butter_maker_var_floor_stand/rev_000001 | model.py:L90-L245, model.py:L398-L413 | structure | The frame becomes the grounded root and the vessel hangs from it, inverting the parent chain. |

## Rejected and reference notes

- Closure hardware (hinged lid, toggle clamp arms) and decorative counts (gear teeth, blade perforations)
  change only a small solid on the shared lid or blade and are derived detail, not candidates.
- The outboard bench clamp and its thumbscrew joint are intentionally excluded. Every accepted
  mount leaves articulation to the category-defining dasher drive inside the churn.
- Rocker and top-crank are the direct vertical crank with a different joint range or bar position.
- Footed stand and squat tub are proportion changes already reachable through the vessel and mount
  parameters, so they would duplicate the floor-stand and crock candidates.

## Multiplicity

- `paddle_count = 1 | 2 | 3 | 4`, applied to `dasher_form`.
  N=2 evidence `rec_butter_maker_var_paddle_n2/rev_000001` model.py:L442-L500;
  N=4 evidence `rec_butter_maker_var_paddle_n4/rev_000001` model.py:L428-L486.
  Blades are indexed around the shaft at an even angular pitch; blade width, hub length and the
  clearance to the vessel wall derive from the vessel bore and from N.
