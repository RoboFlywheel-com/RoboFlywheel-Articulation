# Technology_Laptop — SourceMap

source_map_schema: 1
export_category: Technology_Laptop
picture_category: Technology
picture_subcategory: Laptop
category_scope: Portable clamshell computers with a keyboard-and-pointing base, display lid, and rear screen hinge; source-backed shell, hinge, pointing, and support variations remain inside the category.

sync_records:
  - rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd
  - rec_laptop_var_dualhinge
  - rec_laptop_var_feet4
  - rec_laptop_var_rugged
  - rec_laptop_var_trackbtn
  - rec_laptop_var_trackpoint
  - rec_silver-thin-and-light-laptop-computer-with-a-hin_20260605_173856_302145_c183f0ed

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd/rev_000001 | reviewed | used | Budget plastic clamshell supplies the full-size base, screen/webcam lid, full-width hinge, island keyboard, clickpad, and two-foot baseline. |
| rec_laptop_var_dualhinge/rev_000001 | reviewed | used | Two separated base barrels and matching lid-side covers preserve one screen joint while changing visible hinge support. |
| rec_laptop_var_feet4/rev_000001 | reviewed | used | Four regularly placed corner feet provide multiplicity and stable underside support evidence. |
| rec_laptop_var_rugged/rev_000001 | reviewed | used | Thickened base/lid and four reinforced corner bumpers form a distinct rugged workstation envelope. |
| rec_laptop_var_trackbtn/rev_000001 | reviewed | used | Non-clicking touch surface plus two independently pressing physical buttons provides a second pointing mechanism. |
| rec_laptop_var_trackpoint/rev_000001 | reviewed | used | Red pointing nub and three independently pressing upper buttons provide a business-laptop pointing system. |
| rec_silver-thin-and-light-laptop-computer-with-a-hin_20260605_173856_302145_c183f0ed/rev_000001 | reviewed | used | Filleted aluminum base with real keyboard/trackpad recesses and thin display lid provides the thin-and-light shell family. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| shell_family | budget_plastic | budget clamshell enclosure | rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd/rev_000001 | model.py:L81-L163 | structure | Matte plastic lower shell, palm deck, speakers, webcam lid, and hinge cover form a complete 15.6-inch host. |
| hinge_style | full_width_barrel | full-width rear hinge | rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd/rev_000001 | model.py:L107-L110; model.py:L154-L163 | structure | Long base barrel and centered lid cover visibly support the common screen pivot. |
| pointing_system | integrated_clickpad | single pressing clickpad | rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd/rev_000001 | model.py:L209-L230 | structure+motion | Broad palm-rest pad and front click seam move together on a short downward prismatic joint. |
| support_count_evidence | two_front_feet | two-foot support rule | rec_a-black-budget-15-6-inch-clamshell-laptop-open-a_20260624_123651_161143_65d6f0bd/rev_000001 | model.py:L112-L127 | structure | Two regularly emitted underside feet establish the lower multiplicity value. |
| hinge_style | dual_side_barrels | separated side hinge pair | rec_laptop_var_dualhinge/rev_000001 | model.py:L104-L119; model.py:L155-L167 | structure | Two short mirrored barrels and two matching lid covers share the same screen rotation axis. |
| support_count_evidence | four_corner_feet | four-foot support rule | rec_laptop_var_feet4/rev_000001 | model.py:L113-L128 | structure | Shared rubber-foot geometry repeats at all four underside corners. |
| shell_family | rugged_bumper | thick rugged workstation enclosure | rec_laptop_var_rugged/rev_000001 | model.py:L17-L56; model.py:L91-L177 | structure | Thick base and lid combine with four loop-emitted bumper guards at the host corners. |
| pointing_system | dual_mouse_buttons | touchpad with two physical buttons | rec_laptop_var_trackbtn/rev_000001 | model.py:L35-L100; model.py:L233-L266 | structure+motion | A non-clicking pad is paired with two rounded front buttons on independent downward prismatic joints. |
| pointing_system | trackpoint_three_button | pointing nub with three buttons | rec_laptop_var_trackpoint/rev_000001 | model.py:L71-L221; model.py:L246-L389 | structure+motion | A seated red nub between keys and three upper physical buttons define the business pointing system. |
| shell_family | thin_aluminum | thin-and-light filleted enclosure | rec_silver-thin-and-light-laptop-computer-with-a-hin_20260605_173856_302145_c183f0ed/rev_000001 | model.py:L68-L171; model.py:L173-L252 | structure | Filleted aluminum slab contains true keyboard and trackpad recesses and carries a thin rounded lid. |
| key_array | island_keyboard | repeated island key array | rec_silver-thin-and-light-laptop-computer-with-a-hin_20260605_173856_302145_c183f0ed/rev_000001 | model.py:L146-L171; model.py:L290-L326 | structure+motion | Reused rounded island caps populate a recessed well and press downward on indexed prismatic joints. |
