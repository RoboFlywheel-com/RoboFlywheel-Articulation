# Technology_Remote_Control — SourceMap

source_map_schema: 1
export_category: Technology_Remote_Control
picture_category: Technology
picture_subcategory: Remote_Control
category_scope: Handheld consumer remote controls with a shaped enclosure, a front-face field of independently pressable buttons, and optional directional, rotary, or protective-cover mechanisms.

sync_records:
  - rec_a-black-handheld-thermostat-style-remote-control_20260624_124939_052056_fdc967f6
  - rec_black-sony-soundbar-remote-control-a-slim-rectan_20260605_173757_125686_b2c6bc8a
  - rec_remote_control_var_ergonomic_contour
  - rec_remote_control_var_flip_cover
  - rec_remote_control_var_jog_wheel
  - rec_remote_control_var_minimal_cluster
  - rec_remote_control_var_numeric_keypad
  - rec_remote_control_var_slide_cover
  - rec_remote_control_var_tapered_wedge

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_a-black-handheld-thermostat-style-remote-control_20260624_124939_052056_fdc967f6/rev_000001 | reviewed | used | Rounded thermostat enclosure, inset LCD, circular directional pad, and seven independent front-face press joints establish the upright handheld family. |
| rec_black-sony-soundbar-remote-control-a-slim-rectan_20260605_173757_125686_b2c6bc8a/rev_000001 | reviewed | used | Slim soundbar wand supplies the long enclosure, repeated rubber-button field, recessed wells, and central Y-axis volume rocker. |
| rec_remote_control_var_ergonomic_contour/rev_000001 | reviewed | used | Waisted spline perimeter is a genuine enclosure-form alternative while preserving the common planar control face. |
| rec_remote_control_var_flip_cover/rev_000001 | reviewed | used | Adds a visible body knuckle and widthwise revolute flip cover over the lower controls. |
| rec_remote_control_var_jog_wheel/rev_000001 | reviewed | used | Replaces the rocker with a continuously rotating, radially knurled +Z jog wheel. |
| rec_remote_control_var_minimal_cluster/rev_000001 | reviewed | used | Demonstrates the low-count end of the same loop-emitted button mechanism with four independent pressable media keys. |
| rec_remote_control_var_numeric_keypad/rev_000001 | reviewed | used | Demonstrates the high-count repeated keypad as a regular nested-loop grid with twelve independently pressable keys. |
| rec_remote_control_var_slide_cover/rev_000001 | reviewed | used | Adds visible longitudinal rails and a prismatic cover that travels along the body to expose the controls. |
| rec_remote_control_var_tapered_wedge/rev_000001 | reviewed | used | Tapered hull footprint supplies a distinct slim-wand enclosure with a wide control end and narrow logo end. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| enclosure_family | rounded_thermostat | handheld enclosure | rec_a-black-handheld-thermostat-style-remote-control_20260624_124939_052056_fdc967f6/rev_000001 | model.py:L188-L330 | structure | Rounded, filleted slab carries an inset LCD/bezel and a recessed circular control well on one planar front face. |
| enclosure_family | ergonomic_waisted | handheld enclosure | rec_remote_control_var_ergonomic_contour/rev_000001 | model.py:L26-L85; model.py:L254-L259 | structure | Closed spline narrows at the waist and flares around the LCD and directional-pad ends without changing the control plane. |
| enclosure_family | slim_wand | handheld enclosure | rec_black-sony-soundbar-remote-control-a-slim-rectan_20260605_173757_125686_b2c6bc8a/rev_000001 | model.py:L51-L129; model.py:L355-L366 | structure | Long, narrow CadQuery shell with softened edges and carved front-face wells establishes the soundbar-remote wand. |
| enclosure_family | tapered_wand | handheld enclosure | rec_remote_control_var_tapered_wedge/rev_000001 | model.py:L54-L87; model.py:L382-L394 | structure | Hull of unequal end circles produces a smoothly tapered body, wider at the control end than the logo end. |
| primary_control | directional_pad | front-face directional control | rec_a-black-handheld-thermostat-style-remote-control_20260624_124939_052056_fdc967f6/rev_000001 | model.py:L323-L431 | structure+motion | Four annular-sector buttons surround a round MODE button; every visible control is a separate short-travel prismatic child. |
| primary_control | volume_rocker | central volume control | rec_black-sony-soundbar-remote-control-a-slim-rectan_20260605_173757_125686_b2c6bc8a/rev_000001 | model.py:L472-L504 | structure+motion | Large disc and shallow dome tilt about a real Y-axis at the center of the recessed well. |
| primary_control | jog_wheel | central scroll control | rec_remote_control_var_jog_wheel/rev_000001 | model.py:L474-L518 | structure+motion | Thin circular disc, raised hub, and radial knurl ribs rotate continuously around the front-face +Z axis. |
| button_array | media_round_grid | repeated round press-button array | rec_remote_control_var_minimal_cluster/rev_000001 | model.py:L333-L354; model.py:L368-L456 | structure+motion | Four-button source retains shared loop construction and one prismatic joint per circular cap. |
| button_array | numeric_square_grid | repeated numeric press-button array | rec_remote_control_var_numeric_keypad/rev_000001 | model.py:L428-L501 | structure+motion | Twelve-key source uses one helper inside a regular three-column by four-row nested loop, with a visible mounting recess. |
| cover_module | open_face | uncovered control face | rec_a-black-handheld-thermostat-style-remote-control_20260624_124939_052056_fdc967f6/rev_000001 | model.py:L323-L431 | structure | Baseline control field is directly exposed on the recessed face with no additional moving cover. |
| cover_module | flip_cover | hinged protective cover | rec_remote_control_var_flip_cover/rev_000001 | model.py:L328-L368; model.py:L463-L491 | structure+motion | Visible hinge boss and barrel support a thin rounded cover on a widthwise revolute joint. |
| cover_module | slide_cover | rail-guided protective cover | rec_remote_control_var_slide_cover/rev_000001 | model.py:L153-L174; model.py:L397-L404; model.py:L544-L575 | structure+motion | Two raised longitudinal rails carry a thin grip-equipped cover on a long-axis prismatic joint. |
