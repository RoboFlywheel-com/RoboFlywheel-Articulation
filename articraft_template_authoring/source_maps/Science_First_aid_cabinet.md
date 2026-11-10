# Science_First_aid_cabinet - SourceMap

source_map_schema: 1
export_category: Science_First_aid_cabinet
picture_category: Science
picture_subcategory: First aid cabinet
category_scope: A shallow wall-mounted first-aid cabinet with an open-front sheet-metal carcass, red-cross identity, at least one vertically hinged front leaf, interior shelves, and optional pull-out supply drawers; portable first-aid cases and freestanding medical carts are out of scope.

sync_records:
  - rec_build-a-realistic-articulated-3d-model-of-a-firs_20260609_183625_780787_99727092
  - rec_first_aid_cabinet_var_double_doors
  - rec_first_aid_cabinet_var_drawer_base
  - rec_first_aid_cabinet_var_drawer_stack
  - rec_first_aid_cabinet_var_one_shelf
  - rec_first_aid_cabinet_var_solid_door
  - rec_first_aid_cabinet_var_three_shelf

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_build-a-realistic-articulated-3d-model-of-a-firs_20260609_183625_780787_99727092/rev_000001 | reviewed | used | Reference single glazed door, hollow carcass, shelves, carry handle and red-cross identity; door geometry L145-L227, assembly L254-L404. |
| rec_first_aid_cabinet_var_double_doors/rev_000001 | reviewed | used | Distinct two-leaf door group; side-aware leaf geometry L140-L231 and two opposed vertical hinges L316-L389. |
| rec_first_aid_cabinet_var_drawer_base/rev_000001 | reviewed | used | Distinct single-drawer fitment with cut front opening, hollow tray and bilateral slide rails; geometry L115-L347, assembly L350-L576. |
| rec_first_aid_cabinet_var_drawer_stack/rev_000001 | reviewed | used | Distinct lower drawer-bank fitment with divider, three openings and three independent slides; geometry L80-L347, assembly L350-L518. |
| rec_first_aid_cabinet_var_one_shelf/rev_000001 | reviewed | reference_only | One-shelf endpoint for shelf_count multiplicity; shelf placement and assembly L254-L404. |
| rec_first_aid_cabinet_var_solid_door/rev_000001 | reviewed | used | Distinct solid sheet-metal leaf replacing the glazed frame; geometry L131-L205, assembly L208-L342. |
| rec_first_aid_cabinet_var_three_shelf/rev_000001 | reviewed | reference_only | Three-shelf endpoint for shelf_count multiplicity; equispaced shelf placement L254-L395. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| door_group | single_leaf | articulated component | rec_build-a-realistic-articulated-3d-model-of-a-firs_20260609_183625_780787_99727092/rev_000001 | model.py:L145-L227,L336-L401 | structure+motion | A single revolute child spans the front opening and carries frame/glass, cross, banner, knob and hinge knuckles. |
| door_group | double_leaf | articulated component | rec_first_aid_cabinet_var_double_doors/rev_000001 | model.py:L140-L231,L316-L389 | structure+motion | Left and right leaves have separate joints and opposite Z axes, meeting at cabinet center. |
| door_panel | glazed_window | structural component | rec_build-a-realistic-articulated-3d-model-of-a-firs_20260609_183625_780787_99727092/rev_000001 | model.py:L145-L211 | structure | The panel has a real window opening, separate glass volume, emblem and upper banner. |
| door_panel | solid_panel | structural component | rec_first_aid_cabinet_var_solid_door/rev_000001 | model.py:L131-L174 | structure | The solid door omits glass and places emblem/banner on the metal face. |
| interior_fitment | open_shelves | fixed component | rec_build-a-realistic-articulated-3d-model-of-a-firs_20260609_183625_780787_99727092/rev_000001 | model.py:L77-L142,L254-L335 | structure | Open-front hollow shell carries welded shelves and visible supply blocks. |
| interior_fitment | base_drawer | articulated component | rec_first_aid_cabinet_var_drawer_base/rev_000001 | model.py:L115-L347,L350-L576 | structure+motion | Cut lower opening, open-top hollow tray, side rails and one +Y prismatic joint. |
| interior_fitment | drawer_bank | articulated component | rec_first_aid_cabinet_var_drawer_stack/rev_000001 | model.py:L80-L265,L350-L518 | structure+motion | Lower front is divided into indexed openings with one hollow tray and +Y slide per level. |

## Multiplicity

- `shelf_count = 1 | 2 | 3`: one- and three-shelf records provide endpoints; shelves are equispaced in the available shelf zone and welded into the side/back walls.
- `drawer_count = 2 | 3 | 4` applies only to `interior_fitment=drawer_bank`; the source supplies N=3 and the same indexed opening/tray/slide construction is repeated at host-derived pitch. `base_drawer` always derives one drawer and `open_shelves` derives zero.

## Category identity and motion

- Exactly one wall-mounted hollow `cabinet_body` root with a carry handle, interior shelves and visible first-aid cross/banner identity.
- One or two `door_leaf` children revolve about their actual jamb hinge lines; paired leaves use opposed Z axes so both free edges swing forward.
- Every drawer is a hollow open-top tray on bilateral side rails and an independent +Y prismatic joint; the lower front openings, tray height and level pitch derive from the drawer count.
