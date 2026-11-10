# Bag_Suitcase_Shopping_bucket — SourceMap

source_map_schema: 1
export_category: Bag_Suitcase_Shopping_bucket
picture_category: Bag_Suitcase
picture_subcategory: Shopping bucket
category_scope: A hand-held / nestable shopping basket: one open-mouth tapered tub sitting on the floor, thin-walled and hollow with a rolled rim, carrying at least one rim-hinged or rim-guided carry handle, optionally a rim- or bottom-hinged closure and optional secondary storage, and The wall and floor stay closed: no opening is cut through the side and nothing hangs under the base. Excludes stacks or nests of several baskets, wheeled/trolley baskets, side-opening gates or tilt panels, under-basket drawers, telescoping pull-up bars on posts sunk into the body, collapsible crates, and multi-tier carry caddies.

sync_records:
  - rec_a-rectangular-blue-plastic-hand-held-shopping-ba_20260608_160205_213315_254643d5
  - rec_a-rectangular-red-plastic-shopping-basket-with-r_20260608_160213_314844_c383d977
  - rec_add-a-hinged-drop-front-gate-to-the-wire-mesh-ba_20260609_054819_398495_4598924c
  - rec_add-a-hinged-top-lid-to-make-the-basket-articula_20260609_062924_147603_ab5a00e2
  - rec_add-a-removable-inner-caddy-tray-that-seats-on-t_20260609_135308_824047_5030ab7f
  - rec_add-a-single-central-swing-bail-handle-to-make-t_20260609_062931_487782_287b16ac
  - rec_add-a-slide-out-under-basket-drawer-tray-at-the-_20260609_065801_743480_52ba7599
  - rec_add-a-two-leaf-clamshell-lid-two-top-flaps-hinge_20260609_135304_181832_2822118b
  - rec_add-two-folding-bail-handles-to-make-the-tray-ar_20260609_062932_854922_35468439
  - rec_change-the-body-material-to-a-stainless-steel-wi_20260609_051950_402636_1d416a15
  - rec_change-the-footprint-to-a-round-cylindrical-buck_20260609_054825_387710_e78fd94a
  - rec_change-the-handle-structure-replace-the-single-f_20260609_052816_880253_08aedfc5
  - rec_change-the-overall-shape-to-a-rounded-oval-deep-_20260609_052813_481554_2ec27abe
  - rec_change-the-proportions-to-a-shallow-wide-tray-li_20260609_052818_608677_b5cd2054
  - rec_convert-into-a-wheeled-pull-along-shopping-baske_20260609_133943_516464_43ad0ea4
  - rec_keep-the-same-rectangular-hand-held-shopping-bas_20260616_152752_435107_77eca573
  - rec_make-it-a-two-compartment-divided-basket-add-a-f_20260609_054821_407943_31a4dbd5
  - rec_make-it-a-two-tier-stacked-carry-basket-on-a-sha_20260609_135302_065520_332f5cbc
  - rec_make-the-four-side-walls-hinge-so-the-basket-col_20260609_135259_845833_651978c4
  - rec_make-the-front-wall-a-low-hinged-panel-that-tilt_20260609_135307_236890_85ab5e66
  - rec_plastic-shopping-basket-with-perforated-slotted-_20260605_133637_322465_b050efd5
  - rec_redesign-as-a-tapered-stackable-nesting-shopping_20260609_054812_490053_6a8aa2c9
  - rec_replace-the-two-folding-carry-handles-with-a-sin_20260609_065759_301946_09d0f958
  - rec_restructure-into-a-hexagonal-footprint-shopping-_20260609_054804_556262_50948264
  - rec_restructure-the-parent-into-a-vertical-nesting-s_20260616_153521_561026_465484ba
  - rec_restructure-the-parent-into-a-vertical-nesting-s_20260616_155259_758160_27719f51

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_a-rectangular-red-plastic-shopping-basket-with-r_20260608_160213_314844_c383d977/rev_000001 | reviewed | used | Red rectangular parent. Owns the rectangular tapered tub and the fixed central arched bail; the baseline every fork was cut from. |
| rec_a-rectangular-blue-plastic-hand-held-shopping-ba_20260608_160205_213315_254643d5/rev_000001 | reviewed | used | Blue rectangular parent, same baseline cell as c383d977 but with a dedicated `_cut_slots` helper; adopted as the slotted/perforated wall source. |
| rec_plastic-shopping-basket-with-perforated-slotted-_20260605_133637_322465_b050efd5/rev_000001 | reviewed | used | Third parent. Its walls are `SlotPatternPanelGeometry` panels with HORIZONTAL slot rows on a brick pitch (slot 70x8 mm, pitch 90x20 mm, optional stagger) -- a different perforation family from the vertical slot columns of 254643d5, so it owns its own wall candidate. |
| rec_change-the-overall-shape-to-a-rounded-oval-deep-_20260609_052813_481554_2ec27abe/rev_000001 | reviewed | used | Rounded oval deep body: elliptical loft (`_tapered_oval`/`_ellipse_at_z`) with matching oval rim and slots. Distinct footprint family. |
| rec_restructure-into-a-hexagonal-footprint-shopping-_20260609_054804_556262_50948264/rev_000001 | reviewed | used | Hexagonal footprint with per-face lattice wall and hex rim. Distinct footprint family. |
| rec_change-the-footprint-to-a-round-cylindrical-buck_20260609_054825_387710_e78fd94a/rev_000001 | reviewed | used | Round cylindrical bucket body (circular section, X~=Y). Distinct footprint family. |
| rec_redesign-as-a-tapered-stackable-nesting-shopping_20260609_054812_490053_6a8aa2c9/rev_000001 | reviewed | used | Strongly tapered tub with a markedly narrower base than mouth. Distinct footprint family (the shape reads as stackable; the template builds one basket, not a stack). |
| rec_change-the-proportions-to-a-shallow-wide-tray-li_20260609_052818_608677_b5cd2054/rev_000001 | reviewed | used | Shallow wide tray proportions (low H, wide X). Distinct footprint family. |
| rec_change-the-body-material-to-a-stainless-steel-wi_20260609_051950_402636_1d416a15/rev_000001 | reviewed | used | Stainless wire-mesh basket: welded vertical/horizontal wires plus frame wires and corner posts. Distinct wall family. |
| rec_keep-the-same-rectangular-hand-held-shopping-bas_20260616_152752_435107_77eca573/rev_000001 | reviewed | used | Fully closed smooth-wall tub (shell with no slot cuts). Distinct wall family. |
| rec_add-a-single-central-swing-bail-handle-to-make-t_20260609_062931_487782_287b16ac/rev_000001 | reviewed | used | Single central semicircular swing bail, X-axis REVOLUTE folded<->upright. Distinct handle mechanism. |
| rec_add-two-folding-bail-handles-to-make-the-tray-ar_20260609_062932_854922_35468439/rev_000001 | reviewed | used | Two independent folding side bails, one REVOLUTE each about mirrored Y axes. Distinct handle mechanism. |
| rec_change-the-handle-structure-replace-the-single-f_20260609_052816_880253_08aedfc5/rev_000001 | reviewed | rejected_duplicate | Dual independent handles; topologically identical to the two folding bails already adopted from 35468439. |
| rec_replace-the-two-folding-carry-handles-with-a-sin_20260609_065759_301946_09d0f958/rev_000001 | reviewed | rejected_category_drift | U-shaped telescoping pull-up bar on two posts that sink into the basket body. That is trolley/luggage hardware, not a hand-carried basket handle; it also reads as the wrong small-category in review. |
| rec_add-a-hinged-top-lid-to-make-the-basket-articula_20260609_062924_147603_ab5a00e2/rev_000001 | reviewed | used | Hinged top lid: single panel REVOLUTE about the +Y long rim, closed at q=0, ~115 deg open. |
| rec_add-a-two-leaf-clamshell-lid-two-top-flaps-hinge_20260609_135304_181832_2822118b/rev_000001 | reviewed | used | Two-leaf clamshell lid: mirrored REVOLUTE leaves on the two long rims meeting at the centreline. |
| rec_add-a-hinged-drop-front-gate-to-the-wire-mesh-ba_20260609_054819_398495_4598924c/rev_000001 | reviewed | rejected_category_drift | Drop-front gate: the +Y wall becomes a hinged part, which means punching a rectangular opening through the basket wall. On a round or oval plan that reads as a bin/hopper rather than a hand-held shopping basket; reviewer excluded it from the category scope. |
| rec_make-the-front-wall-a-low-hinged-panel-that-tilt_20260609_135307_236890_85ab5e66/rev_000001 | reviewed | rejected_category_drift | Tilt-down front panel: same wall-opening structure as 4598924c and excluded for the same reason -- a shopping basket does not have a hole cut in its side. |
| rec_make-it-a-two-compartment-divided-basket-add-a-f_20260609_054821_407943_31a4dbd5/rev_000001 | reviewed | used | Two-compartment basket with a fixed central divider wall fused into the tub. |
| rec_add-a-removable-inner-caddy-tray-that-seats-on-t_20260609_135308_824047_5030ab7f/rev_000001 | reviewed | used | Removable inner caddy tray on a PRISMATIC Z lift plus a folding REVOLUTE grip on the tray. |
| rec_add-a-slide-out-under-basket-drawer-tray-at-the-_20260609_065801_743480_52ba7599/rev_000001 | reviewed | rejected_category_drift | Slide-out under-basket drawer: requires a skirt built under the floor and a pocket cut into the base, turning the basket into a cabinet-like carrier. Reviewer excluded it from the category scope. |
| rec_restructure-the-parent-into-a-vertical-nesting-s_20260616_155259_758160_27719f51/rev_000001 | reviewed | rejected_category_drift | Vertical nesting stack of N tapered baskets (a qwen `neststack-n5par` family fork). A stack is several baskets rather than the one hand-held basket this category names; the stackable body shape itself is already covered by 6a8aa2c9. |
| rec_restructure-the-parent-into-a-vertical-nesting-s_20260616_153521_561026_465484ba/rev_000001 | reviewed | rejected_category_drift | Second vertical nesting stack (`neststack-n3`); same reason as 27719f51, and duplicate chain topology besides. |
| rec_convert-into-a-wheeled-pull-along-shopping-baske_20260609_133943_516464_43ad0ea4/rev_000001 | reviewed | rejected_category_drift | Wheeled pull-along basket with rolling axle and telescoping trolley handle; has left the hand-held basket identity. |
| rec_make-the-four-side-walls-hinge-so-the-basket-col_20260609_135259_845833_651978c4/rev_000001 | reviewed | rejected_category_drift | Four hinged walls that collapse flat onto the base; a collapsible crate, not a hand-held shopping basket. |
| rec_make-it-a-two-tier-stacked-carry-basket-on-a-sha_20260609_135302_065520_332f5cbc/rev_000001 | reviewed | rejected_category_drift | Two-tier stacked carry basket on a shared carry post; a two-tier caddy rather than a single hand basket. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_form | rectangular | tub body | rec_a-rectangular-red-plastic-shopping-basket-with-r_20260608_160213_314844_c383d977/rev_000001 | L67-L135 | structure | `_tub_mesh` lofts the double-filleted rectangular section from L_BOT to L_TOP and shells it open-top. |
| body_form | rounded_oval_deep | tub body | rec_change-the-overall-shape-to-a-rounded-oval-deep-_20260609_052813_481554_2ec27abe/rev_000001 | L76-L88, L96-L166 | structure | `_tapered_oval`/`_ellipse_at_z` loft an elliptical deep section; `_build_body` carries the matching oval rim. |
| body_form | hexagonal_footprint | tub body | rec_restructure-into-a-hexagonal-footprint-shopping-_20260609_054804_556262_50948264/rev_000001 | L101-L113, L219-L287 | structure | `_tapered_hex` + `_build_body` give a six-sided prism footprint with a hex rim. |
| body_form | round_cylindrical_bucket | tub body | rec_change-the-footprint-to-a-round-cylindrical-buck_20260609_054825_387710_e78fd94a/rev_000001 | L65-L150 | structure | `_bucket_mesh` builds a circular-section tapered pail (X ~= Y). |
| body_form | tapered_stackable | tub body | rec_redesign-as-a-tapered-stackable-nesting-shopping_20260609_054812_490053_6a8aa2c9/rev_000001 | L73-L177 | structure | `_tub_mesh` uses a strong inward taper (L_BOT << L_TOP), giving a visibly cone-like body distinct from the other footprints. |
| body_form | shallow_wide_tray | tub body | rec_change-the-proportions-to-a-shallow-wide-tray-li_20260609_052818_608677_b5cd2054/rev_000001 | L68-L136 | structure | `_tub_mesh` with a low height and wide X footprint gives the shallow tray proportion. |
| wall_style | slotted_perforated | wall treatment | rec_a-rectangular-blue-plastic-hand-held-shopping-ba_20260608_160205_213315_254643d5/rev_000001 | L157-L194 | structure | `_cut_slots` cuts the vertical slot pattern through the long and short walls. |
| wall_style | steel_wire_mesh | wall treatment | rec_change-the-body-material-to-a-stainless-steel-wi_20260609_051950_402636_1d416a15/rev_000001 | L128-L325 | structure | `_build_wire_basket` welds vertical/horizontal wire grids with frame wires and corner posts. |
| wall_style | horizontal_slot_grid | wall treatment | rec_plastic-shopping-basket-with-perforated-slotted-_20260605_133637_322465_b050efd5/rev_000001 | L25-L37, L54-L70 | structure | `_slot_wall` emits `SlotPatternPanelGeometry` walls whose openings are wide short slots laid out on a brick pitch with an optional row stagger. |
| wall_style | diagonal_lattice | wall treatment | rec_restructure-into-a-hexagonal-footprint-shopping-_20260609_054804_556262_50948264/rev_000001 | L116-L195 | structure | `_build_lattice_wall` crosses +45 and -45 degree bars into an X-pattern lattice panel, framed at the edges; the openings are diamonds rather than slots or an orthogonal grid. |
| wall_style | solid_smooth | wall treatment | rec_keep-the-same-rectangular-hand-held-shopping-bas_20260616_152752_435107_77eca573/rev_000001 | L59-L120 | structure | `_tub_mesh` shells the body and cuts no openings, giving a continuous closed wall. |
| top_configuration | open_bail_fixed_arch | mouth mechanism | rec_a-rectangular-red-plastic-shopping-basket-with-r_20260608_160213_314844_c383d977/rev_000001 | L138-L165, L198-L211 | structure+motion | `_handle_mesh` arch plus the `tub_to_handle` REVOLUTE about X captured in the short-wall pivot bosses; open mouth, no closure. |
| top_configuration | open_bail_swing | mouth mechanism | rec_add-a-single-central-swing-bail-handle-to-make-t_20260609_062931_487782_287b16ac/rev_000001 | L214-L250, L281-L296 | structure+motion | `_bail_handle_mesh` semicircular bail on the `tub_to_bail` REVOLUTE swinging folded<->upright; open mouth. |
| top_configuration | open_bail_dual_fold | mouth mechanism | rec_add-two-folding-bail-handles-to-make-the-tray-ar_20260609_062932_854922_35468439/rev_000001 | L243-L277, L309-L333 | structure+motion | `_bail_handle_mesh` reused for two side bails, each its own REVOLUTE about mirrored Y axes; open mouth. |
| top_configuration | lid_hinged_top | mouth mechanism | rec_add-a-hinged-top-lid-to-make-the-basket-articula_20260609_062924_147603_ab5a00e2/rev_000001 | L76-L172, L216-L273, L306-L319 | structure+motion | `_build_lid` panel hinged on the rim line (`body_to_lid` REVOLUTE about -X); this source carries no bail and instead recesses molded grip cutouts with reinforcing surrounds into the two short walls (`_build_body` L116-L140). |
| top_configuration | lid_clamshell | mouth mechanism | rec_add-a-two-leaf-clamshell-lid-two-top-flaps-hinge_20260609_135304_181832_2822118b/rev_000001 | L173-L215, L287-L318 | structure+motion | `_lid_leaf_mesh` leaf reused mirrored; `tub_to_left_lid`/`tub_to_right_lid` REVOLUTE on the two long rims, meeting at the centreline. |
| secondary_storage | none | interior | rec_a-rectangular-red-plastic-shopping-basket-with-r_20260608_160213_314844_c383d977/rev_000001 | L171-L213 | structure | `build_object_model` emits no interior part: the plain single-compartment basket. |
| secondary_storage | two_compartment_divider | interior | rec_make-it-a-two-compartment-divided-basket-add-a-f_20260609_054821_407943_31a4dbd5/rev_000001 | L98-L188 | structure | `_build_body` fuses a central divider wall into the tub, splitting the cavity in two. |
| secondary_storage | removable_inner_caddy | interior | rec_add-a-removable-inner-caddy-tray-that-seats-on-t_20260609_135308_824047_5030ab7f/rev_000001 | L194-L287, L348-L390 | structure+motion | `_caddy_mesh`/`_caddy_grip_mesh` tray and grip; `tub_to_caddy` PRISMATIC lift plus `caddy_to_grip` REVOLUTE fold. |
