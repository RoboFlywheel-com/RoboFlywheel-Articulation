# Technology_Keyboard — SourceMap

source_map_schema: 1
export_category: Technology_Keyboard
picture_category: Technology
picture_subcategory: Keyboard
category_scope: Standalone desktop computer keyboards with a chassis-supported repeated key array; source-backed layout counts, case profiles, media control, and rear tilt support remain inside the category.

sync_records:
  - rec_a-white-compact-wireless-computer-keyboard-tenke_20260624_123545_283861_38c84f4e
  - rec_full-size-black-wireless-computer-keyboard-with-_20260605_173906_815714_c52b6770
  - rec_keyboard_var_compact60
  - rec_keyboard_var_highprofile
  - rec_keyboard_var_knob
  - rec_keyboard_var_macrocolumn
  - rec_keyboard_var_numpad
  - rec_keyboard_var_split
  - rec_keyboard_var_tiltfeet

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_a-white-compact-wireless-computer-keyboard-tenke_20260624_123545_283861_38c84f4e/rev_000001 | reviewed | used | Low tapered wireless chassis, sculpted low-profile caps, per-key press construction, and the 87-key tenkeyless placement rule are reusable. |
| rec_full-size-black-wireless-computer-keyboard-with-_20260605_173906_815714_c52b6770/rev_000001 | reviewed | used | Recessed key well with four rim walls provides a second real case family and fixed underside support evidence. |
| rec_keyboard_var_compact60/rev_000001 | reviewed | used | The 61-key source removes function, navigation, and arrow blocks while deriving a narrower host footprint. |
| rec_keyboard_var_highprofile/rev_000001 | reviewed | used | Tall stepped case, exterior groove, and deep raised rim form a distinct high-profile mechanical-keyboard enclosure. |
| rec_keyboard_var_knob/rev_000001 | reviewed | used | Top-right rotary media knob includes a real deck boss and a vertical revolute axis. |
| rec_keyboard_var_macrocolumn/rev_000001 | reviewed | used | Six-key macro column extends the repeated array to 93 keys and introduces a visible group gap plus host-width growth. |
| rec_keyboard_var_numpad/rev_000001 | reviewed | used | Seventeen-key numeric block extends the repeated array to 104 keys with a widened host and separated right-hand block. |
| rec_keyboard_var_split/rev_000001 | reviewed | used | Two mirrored tented surfaces, central bridge, and surface-normal key travel create a distinct ergonomic split enclosure. |
| rec_keyboard_var_tiltfeet/rev_000001 | reviewed | used | Paired underside hinge pads and fold-out rear legs provide a real adjustable support mechanism. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| chassis_family | tapered_low_profile | tapered desktop keyboard shell | rec_a-white-compact-wireless-computer-keyboard-tenke_20260624_123545_283861_38c84f4e/rev_000001 | model.py:L95-L129; model.py:L411-L451 | structure | Closed tapered mesh has a shallow front lip, higher rear deck, and separate raised back edge. |
| key_array | sculpted_prismatic_keys | repeated sculpted keycap array | rec_a-white-compact-wireless-computer-keyboard-tenke_20260624_123545_283861_38c84f4e/rev_000001 | model.py:L130-L290 | structure+motion | Rounded loft caps, plungers, switch feet, legends, and downward prismatic travel retain recognizable keyboard construction. |
| key_count_evidence | tenkeyless_87 | 87-key placement rule | rec_a-white-compact-wireless-computer-keyboard-tenke_20260624_123545_283861_38c84f4e/rev_000001 | model.py:L292-L408 | structure | Function, alphanumeric, navigation, and arrow blocks form the tenkeyless count and footprint baseline. |
| chassis_family | recessed_well_slab | recessed key-well shell | rec_full-size-black-wireless-computer-keyboard-with-_20260605_173906_815714_c52b6770/rev_000001 | model.py:L97-L187 | structure | Raked slab plus left, right, front, and rear walls visibly nests the repeated key field. |
| key_count_evidence | compact_61 | 61-key placement rule | rec_keyboard_var_compact60/rev_000001 | model.py:L20-L27; model.py:L292-L387 | structure | The rule removes function, navigation, and arrow groups and derives a compact 60-percent footprint. |
| chassis_family | stepped_high_profile | stepped deep-well enclosure | rec_keyboard_var_highprofile/rev_000001 | model.py:L102-L222; model.py:L224-L351 | structure | A tall grooved body and rim walls above the cap tops produce a source-recognizable high-profile tray. |
| control_module | rotary_media_knob | deck-mounted rotary control | rec_keyboard_var_knob/rev_000001 | model.py:L454-L515 | structure+motion | Knurled cylindrical knob seats on a raised boss and rotates about a vertical deck axis. |
| key_count_evidence | macro_93 | 93-key macro-column placement rule | rec_keyboard_var_macrocolumn/rev_000001 | model.py:L33-L36; model.py:L64-L78; model.py:L137-L251 | structure | Six repeated macro keys, a group gap, and wider host extend the tenkeyless array without changing key construction. |
| key_count_evidence | full_size_104 | 104-key numpad placement rule | rec_keyboard_var_numpad/rev_000001 | model.py:L29-L76; model.py:L143-L262 | structure | A separated seventeen-key numeric block and double-width zero key derive a full-size host footprint. |
| chassis_family | tented_split | bridged tented split enclosure | rec_keyboard_var_split/rev_000001 | model.py:L113-L201; model.py:L298-L369; model.py:L489-L541 | structure+motion | Mirrored tilted shells and surface-normal key axes preserve the ergonomic split profile and press direction. |
| support_module | flip_tilt_feet | paired fold-out rear supports | rec_keyboard_var_tiltfeet/rev_000001 | model.py:L49-L60; model.py:L193-L213; model.py:L268-L311 | structure+motion | Two rear hinge pads carry folding legs that rotate downward to prop the chassis. |
