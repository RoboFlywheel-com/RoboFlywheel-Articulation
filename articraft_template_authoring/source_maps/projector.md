# projector — expanded reviewed SourceMap

export_category: projector

sync_records:
  - rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32
  - rec_0611_projector_var_body_form_slim_rectangular
  - rec_0611_projector_var_body_form_round_portable
  - rec_0611_projector_var_lens_layout_center_lens
  - rec_0611_projector_var_lens_layout_dual_lens
  - rec_0611_projector_var_optics_motion_vertical_lens_shift
  - rec_0611_projector_var_optics_motion_zoom_ring
  - rec_0611_projector_var_support_folding_kickstand
  - rec_0611_projector_var_support_ceiling_yoke
  - rec_0611_projector_var_closure_sliding_lens_shutter
  - rec_0611_projector_var_cooling_dual_side_fan_modules
  - rec_0611_projector_var_control_panel_tilting_panel

## Accepted independent slots

| slot | candidate | diversity_axis | source_type | record/revision | exact model.py:Lx-Ly | status | key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| body_form | compact_chamfered_body | ③ compact shell | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | chamfered shell and optical seat |
| body_form | slim_rectangular_body | ③ slim shell | forked_anchor | `rec_0611_projector_var_body_form_slim_rectangular/rev_000001` | `model.py:L1-L681` | accepted | low rectangular shell |
| body_form | wedge_chamfered_body | ③ angular shell | derived from slim rectangular fork | `rec_0611_projector_var_body_form_slim_rectangular/rev_000001` | `model.py:L69-L101` | accepted | angular tapered shell with stepped top shoulder; cylindrical source fork rejected because it does not match the requested projector family |
| lens_layout | offset_single_lens | ③ offset lens | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | single off-centre lens |
| lens_layout | center_single_lens | ③ centre lens | forked_anchor | `rec_0611_projector_var_lens_layout_center_lens/rev_000001` | `model.py:L1-L660` | accepted | centered aperture |
| lens_layout | dual_lens | ①/③ dual lens | forked_anchor | `rec_0611_projector_var_lens_layout_dual_lens/rev_000001` | `model.py:L1-L717` | accepted | paired seated lens layout |
| optics_motion | focus_ring | ② focus rotation | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | coaxial focus ring and negative-Y revolute |
| optics_motion | zoom_ring | ② zoom rotation | forked_anchor | `rec_0611_projector_var_optics_motion_zoom_ring/rev_000001` | `model.py:L1-L660` | accepted | stepped zoom ring and revolute |
| optics_motion | vertical_lens_shift | ② lens translation | forked_anchor | `rec_0611_projector_var_optics_motion_vertical_lens_shift/rev_000001` | `model.py:L1-L720` | accepted | bounded vertical optical carriage |
| support | base_feet | ② fixed base | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | integrated bottom support |
| support | folding_kickstand | ② folding support | forked_anchor | `rec_0611_projector_var_support_folding_kickstand/rev_000001` | `model.py:L1-L618` | accepted | underside hinged kickstand |
| support | ceiling_yoke | ② ceiling support | forked_anchor | `rec_0611_projector_var_support_ceiling_yoke/rev_000001` | `model.py:L1-L824` | accepted | yoke and column transition |
| closure | open_lens | ② open aperture | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | open front lens |
| closure | sliding_lens_shutter | ② lens shutter | forked_anchor | `rec_0611_projector_var_closure_sliding_lens_shutter/rev_000001` | `model.py:L1-L739` | accepted | sliding front shutter |
| cooling | standard_vents | ① standard ventilation | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | front/side/rear vents |
| cooling | dual_side_fan_modules | ① fan modules | forked_anchor | `rec_0611_projector_var_cooling_dual_side_fan_modules/rev_000001` | `model.py:L1-L828` | accepted | paired side fan housings |
| control_panel | fixed_top_panel | ③ fixed panel | parent | `rec_picturex_0611__projector__001__png_2526f16c5b7d4ad68b1f2be3b40e0a32/rev_000001` | `model.py:L1-L660` | accepted | fixed top seam/panel |
| control_panel | tilting_panel | ② tilting panel | forked_anchor | `rec_0611_projector_var_control_panel_tilting_panel/rev_000001` | `model.py:L1-L795` | accepted | hinged top control panel |

Source spans use the full parent/fork revisions: body 660–745 lines, lens 660/717,
motion 660/720, support 618/824, closure 739, cooling 828 and panel 795. Every
candidate changes geometry, part topology or joint semantics; none is palette-only.

## Assembly and fidelity decisions

- Body support, cooling and top-panel candidates are fused into the body host where
  they are fixed, avoiding false inter-part contact failures.
- Dual lens is a connected optical-core layout with a second seated barrel; center
  and offset layouts derive their aperture and barrel location from body dimensions.
- Focus/zoom use a negative-Y revolute axis. Vertical lens shift uses a Z prismatic
  carriage with the same optical-seat binding and a bounded travel.
- The full independent domain remains `3 × 3 × 3 × 3 × 2 × 2 × 2 = 648`, with no
  multiplicity.
