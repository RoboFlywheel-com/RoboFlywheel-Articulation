# pictureX_0611_Dressing_table — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Dressing_table
picture_category: 0611
picture_subcategory: Dressing_table
category_scope: A seated-height vanity: one carcass on legs or pedestals carrying a row or stack of pull-out drawers under a worktop, plus exactly one mirror assembly mounted on that worktop. A chest of drawers with no mirror, a wall mirror with no carcass, and a writing desk without a mirror are all out of scope.

sync_records:
  - rec_dressing_table_var_drawer_n2_20260714
  - rec_dressing_table_var_drawer_n6_20260714
  - rec_dressing_table_var_kidney_plan_body_20260714
  - rec_dressing_table_var_lift_top_mirror
  - rec_dressing_table_var_mirror_jewellery_door_20260714
  - rec_dressing_table_var_sliding_mirror_storage_20260714
  - rec_dressing_table_var_trunnion_oval_mirror_20260714
  - rec_picturex_0611__dressing_table__001__png__airflex_batch_20260710_86d8e96d7d714090a50b4c5f80dfc9be
  - rec_picturex_0611__dressing_table__002__png__airflex_batch_20260710_8b07b10648bb4d5aa2826cb22b419f51
  - rec_picturex_0611__dressing_table__003__png__airflex_batch_20260710_54143b3f1719456999f47774a46e2142
  - rec_picturex_0611__dressing_table__004__png__airflex_batch_20260710_73bfe825072f4eb68ea75bf81f4b955d
  - rec_picturex_0611__dressing_table__005__png__airflex_batch_20260710_29297dbcc1314ef697098b2bfffa492b
  - rec_picturex_0611__dressing_table__006__png__airflex_batch_20260710_d71fb551c7744b94a055079ecb4a236f

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_dressing_table_var_drawer_n2_20260714/rev_000001 | reviewed | reference_only | Same carcass, legs and mirror as the 002 baseline; its only contribution is multiplicity evidence for a two-drawer row, recorded under Multiplicity. |
| rec_dressing_table_var_drawer_n6_20260714/rev_000001 | reviewed | reference_only | Same carcass and mirror as the 002 baseline with the drawer loop at six; multiplicity evidence only. |
| rec_dressing_table_var_kidney_plan_body_20260714/rev_000001 | reviewed | used | Kidney-shaped worktop and apron on cabriole legs; a genuinely different plan and leg family. |
| rec_dressing_table_var_lift_top_mirror/rev_000001 | reviewed | used | Distinct mirror family: a hinged lid on the worktop carrying the mirror on a second hinge underneath it. |
| rec_dressing_table_var_mirror_jewellery_door_20260714/rev_000001 | reviewed | used | Distinct mirror family: the mirror is the face of a side-hinged jewellery cabinet door standing on the worktop. |
| rec_dressing_table_var_sliding_mirror_storage_20260714/rev_000001 | reviewed | used | Distinct mirror family: the mirror panel slides sideways on a rail instead of hinging. |
| rec_dressing_table_var_trunnion_oval_mirror_20260714/rev_000001 | reviewed | used | Distinct mirror family: an oval frame carried between two turned posts on trunnion pivots. |
| rec_picturex_0611__dressing_table__001__png__airflex_batch_20260710_86d8e96d7d714090a50b4c5f80dfc9be/rev_000001 | reviewed | reference_only | Fragmentary origin record for 001.png: it emits only the two drawer parts and mirror-frame helpers, with no carcass part to review. Used for drawer proportions only. |
| rec_picturex_0611__dressing_table__002__png__airflex_batch_20260710_8b07b10648bb4d5aa2826cb22b419f51/rev_000001 | reviewed | used | Origin record for 002.png. Supplies the rectangular rounded carcass on tapered legs, the knob drawer front and the plain swing mirror. |
| rec_picturex_0611__dressing_table__003__png__airflex_batch_20260710_54143b3f1719456999f47774a46e2142/rev_000001 | reviewed | used | Origin record for 003.png: solid D-profile side panels replace legs and carry the carcass to the floor. |
| rec_picturex_0611__dressing_table__004__png__airflex_batch_20260710_73bfe825072f4eb68ea75bf81f4b955d/rev_000001 | reviewed | used | Origin record for 004.png: long bar pulls across the drawer fronts instead of knobs. |
| rec_picturex_0611__dressing_table__005__png__airflex_batch_20260710_29297dbcc1314ef697098b2bfffa492b/rev_000001 | reviewed | used | Origin record for 005.png: twin full-height pedestals with a knee hole between them. |
| rec_picturex_0611__dressing_table__006__png__airflex_batch_20260710_d71fb551c7744b94a055079ecb4a236f/rev_000001 | reviewed | rejected_duplicate | Byte-for-byte the same construction as rec_dressing_table_var_trunnion_oval_mirror_20260714; reviewed and skipped so the oval mirror is not duplicated. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_form | rect_carcass_tapered_legs | rounded rectangular carcass on tapered legs | rec_picturex_0611__dressing_table__002__png__airflex_batch_20260710_8b07b10648bb4d5aa2826cb22b419f51/rev_000001 | model.py:L34-L78, model.py:L223-L314 | structure | `_carcass_shape` builds a rounded rectangular carcass and `_tapered_leg` four square tapered legs under it. |
| body_form | kidney_plan_cabriole | kidney-plan worktop and apron on cabriole legs | rec_dressing_table_var_kidney_plan_body_20260714/rev_000001 | model.py:L65-L131, model.py:L470-L524 | structure | `_kidney_slab`/`_kidney_apron_solid` produce a real waisted plan and `_cabriole_leg` a curved leg; neither the plan nor the leg is a scaled rectangle. |
| body_form | d_panel_carcass | solid D-profile side panels instead of legs | rec_picturex_0611__dressing_table__003__png__airflex_batch_20260710_54143b3f1719456999f47774a46e2142/rev_000001 | model.py:L28-L50, model.py:L131-L211 | structure | `_d_panel` extrudes a curved end panel that carries the carcass to the floor, so there is no leg at all. |
| body_form | pedestal_knee_hole | twin full-height pedestals with a knee hole | rec_picturex_0611__dressing_table__005__png__airflex_batch_20260710_29297dbcc1314ef697098b2bfffa492b/rev_000001 | model.py:L21-L31, model.py:L176-L324 | structure | The body splits into two pedestals with an open knee hole between them, so the drawer zone is two vertical stacks instead of one row. |
| drawer_front | knob_front | moulded front with a turned knob | rec_picturex_0611__dressing_table__002__png__airflex_batch_20260710_8b07b10648bb4d5aa2826cb22b419f51/rev_000001 | model.py:L79-L101, model.py:L116-L177 | structure | `_drawer_front` gives a lipped front and `_add_drawer` centres a turned knob on it. |
| drawer_front | bar_handle_front | flat front with a long bar pull | rec_picturex_0611__dressing_table__004__png__airflex_batch_20260710_73bfe825072f4eb68ea75bf81f4b955d/rev_000001 | model.py:L30-L55, model.py:L56-L308 | structure | `_add_bar_handle` builds a two-post bar pull spanning most of the front, a different visible hardware topology from a central knob. |
| mirror_form | swing_ring_mirror | framed mirror hinged on the worktop | rec_picturex_0611__dressing_table__002__png__airflex_batch_20260710_8b07b10648bb4d5aa2826cb22b419f51/rev_000001 | model.py:L89-L101, model.py:L315-L353 | structure+motion | `_mirror_ring`/`_mirror_panel` build a framed glass panel on one `frame_to_mirror` revolute rising from the worktop. |
| mirror_form | trunnion_oval_mirror | oval frame between two turned posts | rec_dressing_table_var_trunnion_oval_mirror_20260714/rev_000001 | model.py:L94-L119, model.py:L329-L384, model.py:L440-L480 | structure+motion | `_turned_post`/`_pivot_boss` carry an oval `_mirror_frame_mesh` on trunnions, so the mirror hangs between posts rather than off the worktop. |
| mirror_form | lift_top_mirror | hinged lid carrying the mirror underneath | rec_dressing_table_var_lift_top_mirror/rev_000001 | model.py:L232-L285, model.py:L286-L320 | structure+motion | A `lid` part on `frame_to_lid` carries the `mirror` on a second `lid_to_mirror` revolute; two chained hinges instead of one. |
| mirror_form | sliding_mirror_storage | mirror panel sliding on a worktop rail | rec_dressing_table_var_sliding_mirror_storage_20260714/rev_000001 | model.py:L448-L495 | structure+motion | `slide_mirror` runs on a `body_to_slide_mirror` prismatic joint, revealing storage beneath instead of tilting. |
| mirror_form | jewellery_door_mirror | mirror-faced door on a jewellery cabinet | rec_dressing_table_var_mirror_jewellery_door_20260714/rev_000001 | model.py:L157-L268, model.py:L497-L556 | structure+motion | `_add_jewellery_cabinet_box` stands a real cabinet on the worktop and `mirror_door` swings on a vertical hinge as its mirrored face. |

## Rejected and reference notes

- 006.png duplicates the trunnion oval fork exactly, so it contributes no separate candidate.
- 001.png is a fragmentary record without a carcass part; it is reviewed for drawer proportions only.
- Knob, ring-pull and recessed-grip hardware beyond the two accepted front families change only a small
  solid on the same front panel and are derived detail, not candidates.

## Multiplicity

- `drawer_count = 2 | 3 | 4 | 5 | 6`, applied to `drawer_front`.
  N=2 evidence `rec_dressing_table_var_drawer_n2_20260714/rev_000001` model.py:L118-L220;
  N=6 evidence `rec_dressing_table_var_drawer_n6_20260714/rev_000001` model.py:L118-L224.
  The row is distributed across the apron for the leg and panel bodies and split into two vertical
  stacks for the pedestal body; drawer width, front height, box depth and travel derive from the host
  drawer zone and from N.
