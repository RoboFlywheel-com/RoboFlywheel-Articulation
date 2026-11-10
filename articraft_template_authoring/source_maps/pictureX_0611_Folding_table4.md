# pictureX_0611_Folding_table4 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_table4
picture_category: 0611
picture_subcategory: Folding_table4

category_scope: A large round dining table carrying a rotating lazy-susan turntable on its own vertical-axis bearing at the centre of the top, standing on a collapsible or pedestal base. The fixed round top plus a concentric powered-by-hand turntable is the category identity; tables whose top itself folds or drops belong to pictureX_0611_Folding_table3, and plain fixed round tables without a turntable are out of scope.

sync_records:
  - rec_picturex0611_folding_table4_var_flush_recessed_tray
  - rec_picturex0611_folding_table4_var_indexed_detent_tray
  - rec_picturex0611_folding_table4_var_leg_count_n6
  - rec_picturex0611_folding_table4_var_pedestal_base
  - rec_picturex0611_folding_table4_var_raised_guard_rim
  - rec_picturex0611_folding_table4_var_ring_bearing_tray
  - rec_picturex0611_folding_table4_var_roller_bearing_n12
  - rec_picturex0611_folding_table4_var_segmented_lazy_susan_n4
  - rec_picturex0611_folding_table4_var_segmented_lazy_susan_n6
  - rec_picturex0611_folding_table4_var_tripod_pedestal_base
  - rec_picturex0611_folding_table4_var_two_tier_turntable
  - rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e/rev_000001 | reviewed | used | Image-grounded base for 001.png: 1.20 m pale-oak round top on a circular apron and radial steel frame, a central bearing pedestal and race carrying an 0.80 m grey woven-lattice turntable, and four individually hinged square-tube folding legs on fork-and-pin brackets. Supplies the woven_lattice tray and the folding_legs base. |
| rec_picturex0611_folding_table4_var_flush_recessed_tray/rev_000001 | reviewed | used | Sinks the turntable into a machined pocket in the top with its own bearing lip, so the tray reads flush with the surrounding surface instead of sitting proud of it. Source for the flush_recessed tray. |
| rec_picturex0611_folding_table4_var_indexed_detent_tray/rev_000001 | reviewed | used | Adds a detent ring with cut pockets under the tray plus a spring pin housing, tip and set screw on the tray, so the turntable indexes to discrete stations. Source for the detent_index bearing. |
| rec_picturex0611_folding_table4_var_raised_guard_rim/rev_000001 | reviewed | used | Carries a tall retaining rim with an inlay band around the tray edge instead of a flat seam. Source for the raised_guard_rim tray. |
| rec_picturex0611_folding_table4_var_ring_bearing_tray/rev_000001 | reviewed | used | Replaces the central bearing pedestal with a wide annular bearing ring on a short column and a hub plate under the tray, moving the load path out to a large-diameter race. Source for the ring_and_hub bearing. |
| rec_picturex0611_folding_table4_var_roller_bearing_n12/rev_000001 | reviewed | used | Adds a roller retainer ring and its individual rollers between the race and the tray, so the bearing is visibly a roller set rather than a plain plate. Source for the roller_retainer bearing. |
| rec_picturex0611_folding_table4_var_two_tier_turntable/rev_000001 | reviewed | used | Adds a fixed lower shelf below the rotating tray with its own edge band, making the centre a two-level server. Source for the two_tier tray and its host shelf. |
| rec_picturex0611_folding_table4_var_segmented_lazy_susan_n6/rev_000001 | reviewed | used | Builds the tray out of separate wedge sectors with radial seams instead of one disc. Source for the segmented_wedge tray. |
| rec_picturex0611_folding_table4_var_segmented_lazy_susan_n4/rev_000001 | reviewed | rejected_duplicate | The same wedge-sector construction as the n6 record with only the sector count changed, so it produces no distinct candidate; it is kept as evidence that the sector count is a free parameter of that tray. |
| rec_picturex0611_folding_table4_var_pedestal_base/rev_000001 | reviewed | used | Replaces the folding legs with a turned pedestal column, top plate, upper collar and a lobed base hub with a lower ring. Source for the pedestal_column base. |
| rec_picturex0611_folding_table4_var_tripod_pedestal_base/rev_000001 | reviewed | used | Central column on a mounting plate and collar standing on a hub with radiating cast feet. Source for the tripod_pedestal base. |
| rec_picturex0611_folding_table4_var_leg_count_n6/rev_000001 | reviewed | reference_only | Identical leg construction to 001 with NUM_LEGS raised to six and the hinge angles recomputed from it. It is evidence that the support count is index-general multiplicity on the base rather than a separate structural candidate. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| tray_build | woven_lattice | turntable tray | rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e/rev_000001 | model.py:L189-L253 | structure | Flat grey tray with a dark perimeter seam, crossed woven slats and a warm-metal centre cap. |
| tray_build | flush_recessed | turntable tray | rec_picturex0611_folding_table4_var_flush_recessed_tray/rev_000001 | model.py:L125-L145 | structure | Tray dropped into a machined pocket with its own bearing lip so it reads flush with the top. |
| tray_build | raised_guard_rim | turntable tray | rec_picturex0611_folding_table4_var_raised_guard_rim/rev_000001 | model.py:L240-L262 | structure | Tall retaining rim with an inlay band standing above the tray surface. |
| tray_build | two_tier | turntable tray | rec_picturex0611_folding_table4_var_two_tier_turntable/rev_000001 | model.py:L186-L210 | structure | Fixed lower shelf with its own edge band beneath the rotating tray. |
| tray_build | segmented_wedge | turntable tray | rec_picturex0611_folding_table4_var_segmented_lazy_susan_n6/rev_000001 | model.py:L37-L67 | structure | Tray built from separate wedge sectors with radial seams rather than one disc. |
| base_build | folding_legs | table base | rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e/rev_000001 | model.py:L254-L310 | structure+motion | Square-tube legs on fork-and-pin hinge brackets, each folding inward and upward under the top. |
| base_build | pedestal_column | table base | rec_picturex0611_folding_table4_var_pedestal_base/rev_000001 | model.py:L140-L200 | structure | Turned pedestal column with top plate, upper collar and a lobed base hub on a lower ring. |
| base_build | tripod_pedestal | table base | rec_picturex0611_folding_table4_var_tripod_pedestal_base/rev_000001 | model.py:L62-L97 | structure | Central column on a mounting plate and collar standing on a hub with radiating cast feet. |
| bearing_build | race_and_plate | turntable bearing | rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e/rev_000001 | model.py:L112-L130, L200-L212 | structure | Central pedestal closed by one flat race that the tray's bearing plate rides on directly, with no ring, cage or index. |
| bearing_build | ring_and_hub | turntable bearing | rec_picturex0611_folding_table4_var_ring_bearing_tray/rev_000001 | model.py:L118-L136, L215-L228 | structure | The pedestal is replaced by a short column carrying a wide annular race at 0.62 of the tray radius, met by a spoked hub plate under the tray. |
| bearing_build | roller_retainer | turntable bearing | rec_picturex0611_folding_table4_var_roller_bearing_n12/rev_000001 | model.py:L131-L165 | structure | A cage ring holds discrete rollers between the race and a tray-side track, so the tray runs on rolling elements instead of a flat plate. |
| bearing_build | detent_index | turntable bearing | rec_picturex0611_folding_table4_var_indexed_detent_tray/rev_000001 | model.py:L137-L162, L260-L278 | structure+motion | A pocketed detent ring on the host is indexed by a spring pin housing, tip and set screw carried on the tray, so rotation stops at discrete stations. |
