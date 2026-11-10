# pictureX_0611_Ice_crream_machine — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Ice_crream_machine
picture_category: 0611
picture_subcategory: Ice_crream_machine
category_scope: Batch ice-cream freezers: an insulated freezing vessel holding a rotating dasher that scrapes the wall, an access lid or end cap over that vessel, and a hand crank or motor pod driving the dasher; blenders, food processors, drink dispensers and soft-serve dispensing cabinets are not candidates.

sync_records:
  - rec_ice_crream_machine_var_bucket_churn_refill
  - rec_ice_crream_machine_var_countertop_compressor
  - rec_ice_crream_machine_var_dasher_paddles_n4_gt10
  - rec_ice_crream_machine_var_horizontal_batch_freezer_gt10
  - rec_ice_crream_machine_var_twin_bowl_refill
  - rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80
  - rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c
  - rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469
  - rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80/rev_000001 | reviewed | reference_only | The coopered bucket origin; its geometry is carried forward part for part by the reviewed bucket-churn refill, which supersedes it. |
| rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c/rev_000001 | reviewed | used | Countertop origin: its low bearing web - a bored ring on a single flat bridge across the mouth - is a third, much shallower way to carry the drive than a bridge yoke or a cast arch. |
| rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469/rev_000001 | reviewed | used | Upright tub origin: a revolved tapered pail with a sealed floor, and a low cast arch frame whose two shoulders meet a central bored bearing sleeve. |
| rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0/rev_000001 | reviewed | used | Horizontal origin: the hinged lid over the housing is the only access mechanism in the pool that swings instead of lifting. |
| rec_ice_crream_machine_var_countertop_compressor/rev_000001 | reviewed | used | Compact appliance family: a rounded rectangular base with a bowl recess and seating collar, a rear motor pod with vent slots and drive shaft, and a lift-off lid. |
| rec_ice_crream_machine_var_bucket_churn_refill/rev_000001 | reviewed | used | Coopered bucket family: a frustum bucket shell with stave seams and bands, a shaft dasher with full-width bars, and a hand crank with a free grip. |
| rec_ice_crream_machine_var_horizontal_batch_freezer_gt10/rev_000001 | reviewed | used | Horizontal barrel family: a hollow barrel with reinforcing bands and a rear bearing mount, plus a radial scraper dasher. |
| rec_ice_crream_machine_var_dasher_paddles_n4_gt10/rev_000001 | reviewed | used | The indexed paddle dasher: a hub collar carrying n_paddles blades at evenly rotated yaws and staggered heights. |
| rec_ice_crream_machine_var_twin_bowl_refill/rev_000001 | reviewed | reference_only | Confirms that bowl modules can be loop-emitted on a shared base, but adds no vessel, dasher, lid or drive form the other reviewed sources do not already provide. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| vessel_body | countertop_bowl | appliance base with a seated bowl | rec_ice_crream_machine_var_countertop_compressor/rev_000001 | model.py:L49-L110 | structure | A rounded rectangular body is cut with a bowl recess and fused with a raised seating collar, integrated feet and a control-panel recess. |
| vessel_body | coopered_bucket | staved wooden churn bucket | rec_ice_crream_machine_var_bucket_churn_refill/rev_000001 | model.py:L108-L196 | structure | A frustum shell carries 24 indexed stave seams, lighter strips and steel bands around a real inner cavity. |
| vessel_body | upright_tub | revolved tapered freezer pail | rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469/rev_000001 | model.py:L60-L74 | structure | A revolved section gives a genuinely hollow tapered pail with a sealed floor and a rolled top edge. |
| dasher_form | paddle_blades | hub with indexed paddles | rec_ice_crream_machine_var_dasher_paddles_n4_gt10/rev_000001 | model.py:L371-L399 | structure | A hub collar carries n_paddles flat blades at evenly rotated yaws and staggered heights on the shaft. |
| dasher_form | scraper_bars | full-width scraper bars | rec_ice_crream_machine_var_bucket_churn_refill/rev_000001 | model.py:L380-L406 | structure | A shaft with a thrust collar carries full-diameter bars alternating in yaw down the canister. |
| dasher_form | radial_plates | axial scraper plates | rec_ice_crream_machine_var_horizontal_batch_freezer_gt10/rev_000001 | model.py:L201-L258 | structure | A bearing-collared shaft carries long plates standing radially off the shaft with a real clearance to the wall. |
| drive_mount | arch_frame | cast arch with a bearing sleeve | rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469/rev_000001 | model.py:L92-L129 | structure | Two cast shoulder plates rise from the rim to a gearbox block with a tall hollow bearing sleeve bored for the dasher shaft. |
| access_form | lift_off_lid | lift-off lid with skirt | rec_ice_crream_machine_var_countertop_compressor/rev_000001 | model.py:L176-L191 | structure+motion | A disc with a seating skirt and a centre hub bore lifts straight off the vessel rim. |
| access_form | hinged_cap | hinged access cap | rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0/rev_000001 | model.py:L140-L164 | structure+motion | A cap swings on a real hinge line at the edge of the housing instead of lifting away. |
| drive_mount | bridge_yoke | bored bridge yoke on two posts | rec_ice_crream_machine_var_bucket_churn_refill/rev_000001 | model.py:L229-L258 | structure | A bored bridge plate spans the vessel on two side supports with clamp tabs gripping the rim. |
| drive_mount | bearing_web | low bored bearing web | rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c/rev_000001 | model.py:L108-L123 | structure | A single flat bridge across the mouth carries a small bored ring on the axis, with no posts or shoulders. |
| drive_form | hand_crank | crank arm with free grip | rec_ice_crream_machine_var_bucket_churn_refill/rev_000001 | model.py:L407-L457 | structure+motion | A drive shaft carries an offset crank arm and a grip that spins on its own axis. |
| drive_form | motor_pod | motor pod with vent slots | rec_ice_crream_machine_var_countertop_compressor/rev_000001 | model.py:L111-L148 | structure | A rounded pod is cut with four vent slots and fused with a downward drive shaft and coupling collar instead of a hand crank. |

## Component evidence

- The dasher shaft, its bearing and the vessel cavity are identity-fixed host structure across
  every reviewed source (for example `rec_ice_crream_machine_var_countertop_compressor/rev_000001`
  `model.py:L149-L175` for the bowl shell and its drive socket), so they are not a slot.
- Blade multiplicity comes from `rec_ice_crream_machine_var_dasher_paddles_n4_gt10/rev_000001`
  `model.py:L387-L399`, which derives blade yaw and height from a paddle count rather than
  hard-coding them; the bucket churn's three-bar dasher is the other reviewed count.
