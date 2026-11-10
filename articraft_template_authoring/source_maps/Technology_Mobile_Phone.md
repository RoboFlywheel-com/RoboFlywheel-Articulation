# Technology_Mobile_Phone — SourceMap

source_map_schema: 1
export_category: Technology_Mobile_Phone
picture_category: Technology
picture_subcategory: Mobile_Phone
category_scope: Handheld mobile telephones whose recognizable body, display, user-input surface, and optional opening, sliding, swiveling, or telescoping mechanism form one portable device; desk phones, conference phones, and game consoles are outside the category.

sync_records:
  - rec_black-clamshell-flip-phone-for-seniors-with-a-hi_20260605_174014_810624_7ec9acc7
  - rec_mobile_phone_var_numeric_only
  - rec_mobile_phone_var_qwerty
  - rec_mobile_phone_var_slider
  - rec_mobile_phone_var_swivel
  - rec_mobile_phone_var_telescoping_antenna
  - rec_mobile_phone_var_touch_slab
  - rec_nokia-3310-candybar-mobile-phone-dark-blue-with-_20260605_174005_164763_8c6bf79a

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_black-clamshell-flip-phone-for-seniors-with-a-hi_20260605_174014_810624_7ec9acc7/rev_000001 | reviewed | used | Independent clamshell parent contributes one global host-mechanism family and its large senior-keypad front module; lid display and hinge remain part of the structural host. |
| rec_mobile_phone_var_numeric_only/rev_000001 | reviewed | used | Single-axis child of the classic candybar parent contributes only the numeric-only front-module delta: one recessed 4-by-3 well and twelve pressable caps. Its unchanged shell and display are de-duplicated to the parent. |
| rec_mobile_phone_var_qwerty/rev_000001 | reviewed | used | Single-axis child of the classic candybar parent contributes only the QWERTY front-module delta and its wider footprint requirement. Unchanged shell/display construction is de-duplicated to the parent. |
| rec_mobile_phone_var_slider/rev_000001 | reviewed | used | Prompt-declared primary-form-family change contributes the two-deck host mechanism: lower slab, overlapping upper carrier, and longitudinal slide. The unchanged classic controls are de-duplicated to the parent front module. |
| rec_mobile_phone_var_swivel/rev_000001 | reviewed | used | Prompt-declared primary-form-family change contributes the split host, corner post/hub, and face-normal swivel joint. Unchanged classic controls are de-duplicated to the parent front module. |
| rec_mobile_phone_var_telescoping_antenna/rev_000001 | reviewed | used | Single-axis child of the clamshell parent contributes only the external antenna module: seated boss, guide sleeve, mast, tip, and prismatic extension. All clamshell parts are de-duplicated to its parent. |
| rec_mobile_phone_var_touch_slab/rev_000001 | reviewed | used | Prompt-declared front-family change contributes only the edge-to-edge touch/glass and four-button front module plus its footprint requirement; the shared monoblock host envelope is de-duplicated to the candybar parent. |
| rec_nokia-3310-candybar-mobile-phone-dark-blue-with-_20260605_174005_164763_8c6bf79a/rev_000001 | reviewed | used | Canonical parent contributes the curved monoblock host and the reusable classic function-plus-numeric front module, including its LCD and press construction. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| host_mechanism | curved_monoblock | curved single-piece handset host | rec_nokia-3310-candybar-mobile-phone-dark-blue-with-_20260605_174005_164763_8c6bf79a/rev_000001 | model.py:L267-L318 | structure | Boolean-unioned rounded shell sections form the parent monoblock; front-module pockets remain a derived host adaptation instead of additional host candidates. |
| host_mechanism | vertical_slider | two-deck longitudinal slider host | rec_mobile_phone_var_slider/rev_000001 | model.py:L256-L321; model.py:L375-L491 | structure+motion | Separate lower and upper rounded slabs retain a flush slide face and a +Y prismatic carrier; unchanged keypad construction is intentionally excluded from this candidate. |
| host_mechanism | corner_swivel | corner-post swiveling host | rec_mobile_phone_var_swivel/rev_000001 | model.py:L102-L154; model.py:L375-L505 | structure+motion | Lower and upper shells, visible corner post/hub and face-normal revolute joint are the topology-changing delta; inherited controls are excluded. |
| host_mechanism | senior_clamshell | hinged clamshell host with display lid | rec_black-clamshell-flip-phone-for-seniors-with-a-hi_20260605_174014_810624_7ec9acc7/rev_000001 | model.py:L570-L750 | structure+motion | Thick lower shell, split body knuckles, bridged display lid and horizontal hinge necessarily form one structural family because the whole host topology changes. |
| front_module | classic_function_numeric | classic LCD, function cluster and numeric keypad | rec_nokia-3310-candybar-mobile-phone-dark-blue-with-_20260605_174005_164763_8c6bf79a/rev_000001 | model.py:L319-L534 | structure+motion | Parent front module combines a small inset LCD, three shaped function controls and twelve numeric press parts. |
| front_module | numeric_only_12 | bare 4-by-3 numeric keypad front | rec_mobile_phone_var_numeric_only/rev_000001 | model.py:L255-L264; model.py:L377-L425 | structure+motion | Variant-only delta removes the function well and emits exactly twelve numeric press parts by the inherited grid rule. |
| front_module | qwerty_40 | four-row QWERTY front | rec_mobile_phone_var_qwerty/rev_000001 | model.py:L209-L231; model.py:L336-L393 | structure+motion | Variant-only delta changes the front opening and emits forty small square press parts; its larger footprint is a host-capacity input. |
| front_module | full_touch | broad touchscreen and four physical controls | rec_mobile_phone_var_touch_slab/rev_000001 | model.py:L128-L235 | structure+motion | Variant-only delta replaces the keypad front with edge-to-edge glass, narrow bezel, earpiece/camera details, and four looped prismatic controls. |
| front_module | senior_large_keypad | large high-contrast senior keypad | rec_black-clamshell-flip-phone-for-seniors-with-a-hi_20260605_174014_810624_7ec9acc7/rev_000001 | model.py:L753-L833 | structure+motion | Independent parent front module has nine navigation/function controls plus twelve large numeric keys and a recessed supporting tray. |
| antenna_module | integrated_internal | handset without an external mast | rec_black-clamshell-flip-phone-for-seniors-with-a-hi_20260605_174014_810624_7ec9acc7/rev_000001 | model.py:L602-L668 | structure | Parent host terminates at its molded shell and hinge without a separate external antenna, providing the de-duplicated baseline. |
| antenna_module | telescoping_mast | externally guided telescoping antenna | rec_mobile_phone_var_telescoping_antenna/rev_000001 | model.py:L681-L699; model.py:L790-L832 | structure+motion | Variant-only delta adds a seated boss/sleeve and one cylindrical mast-plus-tip child on an extending prismatic axis. |
