# Studio lamp — SourceMap

export_category: studio_lamp

The authoritative source pool is `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
The three originals and eleven authored variants are all retained as quality evidence. This map
records semantic candidates, exact source spans, interface decisions, and multiplicity behavior;
it is not a runtime dependency closure and copies no source implementation.

sync_records:
  - rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96
  - rec_picturex_0611__studio_lamp__002__png_307b9e5c7dcc41b6ae3c8ad0c75c7c32
  - rec_picturex_0611__studio_lamp__003__png_ced1daa79fcf48e8bc507994cbf1a3a8
  - rec_0611_studio_lamp_var_folding_collapsible_tripod
  - rec_0611_studio_lamp_var_head_family_fresnel
  - rec_0611_studio_lamp_var_head_family_led_panel
  - rec_0611_studio_lamp_var_head_family_round_reflector
  - rec_0611_studio_lamp_var_head_module_4_barn_doors
  - rec_0611_studio_lamp_var_head_module_focus_barrel
  - rec_0611_studio_lamp_var_mast_count_1
  - rec_0611_studio_lamp_var_mast_count_3
  - rec_0611_studio_lamp_var_support_counterweighted_boom
  - rec_0611_studio_lamp_var_support_rolling_base
  - rec_0611_studio_lamp_var_yoke_dual_axis_yoke

## Accepted component candidates

| Slot | Candidate | Diversity axis | Record/Revision | Exact model.py:Lx-Ly | Status | Source-bound geometry, detail, and finish |
|---|---|---|---|---|---|---|
| ground_support | classic_hinged_tripod | hinged radial tripod | rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96/rev_000001 | model.py:L142-L245 | accepted | Black cast hub, long square/tubular legs, hinge barrels, feet and captured hardware. |
| ground_support | radial_tube_spider | hinged low spider | rec_picturex_0611__studio_lamp__002__png_307b9e5c7dcc41b6ae3c8ad0c75c7c32/rev_000001 | model.py:L88-L174 | accepted | Compact center socket, shallow-curved radial tubes, tangent hinge pins and rounded contact ends. |
| ground_support | folding_braced_spider | folding braced support | rec_0611_studio_lamp_var_folding_collapsible_tripod/rev_000001 | model.py:L98-L219 | accepted | Sliding collar, radial feet, one brace per leg, pivots and source-like black finish. |
| ground_support | vintage_clevis_tripod | silver clevis tripod | rec_picturex_0611__studio_lamp__003__png_ced1daa79fcf48e8bc507994cbf1a3a8/rev_000001 | model.py:L116-L256 | accepted | Cast lower hub, three clevis-supported black legs, braces, pads and bright clamp hardware. |
| ground_support | rolling_caster_star | rolling radial base | rec_0611_studio_lamp_var_support_rolling_base/rev_000001 | model.py:L178-L273 | accepted | Wide radial arms, end forks, captured caster swivels and true rolling wheels. |
| ground_support | weighted_disk | counterweighted disk | rec_0611_studio_lamp_var_support_counterweighted_boom/rev_000001 | model.py:L161-L198 | accepted | Broad stepped cast disk, rubber underside and central mast socket; no invented tripod legs. |
| mast_profile | classic_black_nested_tubes | black nested mast | rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96/rev_000001 | model.py:L247-L295 | accepted | Real nested round tubes, stepped clamp collars, side knobs and black powder coat. |
| mast_profile | boom_heavy_riser | heavy boom riser | rec_picturex_0611__studio_lamp__002__png_307b9e5c7dcc41b6ae3c8ad0c75c7c32/rev_000001 | model.py:L175-L243 | accepted | Large lower riser, silver upper tube, reinforced boom clamp and tightening hardware. |
| mast_profile | vintage_silver_drop_mast | vintage mixed-finish mast | rec_picturex_0611__studio_lamp__003__png_ced1daa79fcf48e8bc507994cbf1a3a8/rev_000001 | model.py:L257-L328 | accepted | Black lower tube, telescoping silver upper tube, bright collars and compact top receiver. |
| head_support_mechanism | adaptive_direct_trunnion_yoke | direct wide yoke | rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96/rev_000001 | model.py:L297-L336 | accepted | Rectangular lower bridge and tall side cheeks; span and height derive from the selected head envelope. |
| head_support_mechanism | counterbalance_boom_fork | counterweighted boom | rec_picturex_0611__studio_lamp__002__png_307b9e5c7dcc41b6ae3c8ad0c75c7c32/rev_000001 | model.py:L244-L328 | accepted | Long tilting boom, rear counterweight/handle, mast clamp and compact terminal fork. |
| head_support_mechanism | compact_round_tube_u_yoke | compact U-yoke | rec_picturex_0611__studio_lamp__003__png_ced1daa79fcf48e8bc507994cbf1a3a8/rev_000001 | model.py:L279-L328 | accepted | Round-tube U frame integrated at the top receiver with paired trunnion pivots. |
| head_support_mechanism | dual_axis_pan_u_yoke | pan-and-tilt yoke | rec_0611_studio_lamp_var_yoke_dual_axis_yoke/rev_000001 | model.py:L279-L370 | accepted | Captured vertical pan bearing below a U-yoke plus a separate horizontal head-tilt axis. |
| lamp_head_assembly | portrait_softbox | portrait softbox | rec_picturex_0611__studio_lamp__001__png_8ec4826c28154fafa47cecef308a7e96/rev_000001 | model.py:L338-L430 | accepted | Deep tapered black fabric body, graphite rear speed ring, framed warm diffuser and side bosses. |
| lamp_head_assembly | portrait_softbox_barn_doors | portrait softbox plus doors | rec_0611_studio_lamp_var_head_module_4_barn_doors/rev_000001 | model.py:L346-L520 | accepted | Source softbox plus four brackets, hinge barrels, captured pins and independently rotating black leaves. |
| lamp_head_assembly | landscape_softbox | landscape softbox | rec_picturex_0611__studio_lamp__002__png_307b9e5c7dcc41b6ae3c8ad0c75c7c32/rev_000001 | model.py:L329-L429 | accepted | Wide tapered fabric shell, rigid front frame, cream diffusion panel and rear lamp socket detail. |
| lamp_head_assembly | landscape_softbox_focus_ring | focus-ring softbox | rec_0611_studio_lamp_var_head_module_focus_barrel/rev_000001 | model.py:L360-L464 | accepted | Landscape softbox plus rear focus barrel, rotating ring and 24 real grip grooves about the optical axis. |
| lamp_head_assembly | round_beauty_dish | round reflector | rec_0611_studio_lamp_var_head_family_round_reflector/rev_000001 | model.py:L364-L464 | accepted | Shallow spun dish, rolled rim, central deflector, stem and rear speed ring in source-bound finishes. |
| lamp_head_assembly | led_panel | LED panel | rec_0611_studio_lamp_var_head_family_led_panel/rev_000001 | model.py:L321-L407 | accepted | Rounded rectangular body, pale emitter, rear heatsink plate, six fins, dimmer and indicator. |
| lamp_head_assembly | fresnel_can | Fresnel fixture | rec_0611_studio_lamp_var_head_family_fresnel/rev_000001 | model.py:L362-L449 | accepted | Stepped cylindrical can, front Fresnel lens profile, vent bands, rear cap and side tilt bosses. |
| lamp_head_assembly | vintage_spotlight_can | vintage spotlight | rec_picturex_0611__studio_lamp__003__png_ced1daa79fcf48e8bc507994cbf1a3a8/rev_000001 | model.py:L330-L426 | accepted | Satin-aluminum barrel, rolled front bezel, convex pale lens, dark vents and top carry handle. |

## Accepted multiplicities

| Multiplicity | Values | Repeated item | Host derivation | Evidence and semantics |
|---|---|---|---|---|
| radial_support_count | N=3–7 | radial support module | Angular pitch is `2π/N`; hub/rim attachment widths, wheel/fork spacing, brace anchors, disk ribs and ground pads are derived from N. | Original and support variants establish radial support construction. Every support family emits N load-bearing or stabilizing modules: legs/arms for tripod and rolling families; integral cast ribs with underside ground pads for the weighted disk. N is never a metadata-only value. |
| mast_stage_count | N=1–3 | nested mast stage | Tube radius decreases per stage; collar radius, insertion overlap, exposed length, travel limits and top-interface height derive cumulatively from N. | One-stage and three-stage variants at model.py:L315-L338 and model.py:L218-L328 establish true nested-stage behavior. Every mast profile generates N actual progressively smaller tubes. |

## Rejected independent axes

- `palette_style` is removed. Source finishes belong to structural/head families: powder-black and
  graphite fabric for softboxes, dark anodized metal for LED/boom hardware, satin aluminum and
  bright collars for vintage fixtures, and cast iron/rubber for disk bases. A global recoloring
  axis would erase source identity and is not a structural slot.
- `head_module` is not independent. Barn-door brackets and focus barrels alter the host head's
  front/rear interface and articulation graph, so they are absorbed into
  `portrait_softbox_barn_doors` and `landscape_softbox_focus_ring`.
- `column_length_scale`, `mast_travel_scale`, and `head_scale` remain bounded continuous
  proportions only. Ground-support dimensions are candidate-local, direct metre-valued parameters:
  each tripod/spider has its own leg reach, `rolling_caster_star` has
  `rolling_caster_arm_length_m`, and `weighted_disk` has `weighted_disk_radius_m` in 0.20–0.50 m.
  Ribs and pads follow the weighted-disk footprint. None of these continuous values contributes to
  the discrete domain.

## Locked domain, interfaces, and derivation graph

- Component domain: `ground_support` (6) × `mast_profile` (3) ×
  `head_support_mechanism` (4) × `lamp_head_assembly` (8) = **576 core combinations**.
- Global multiplicities: `radial_support_count` (5) × `mast_stage_count` (3), giving
  **8640 raw combinations**. The full Cartesian domain must build; there is no compatibility gate
  or silent downgrade.
- Each ground support provides a centered vertical mast socket. Each mast consumes that socket,
  derives all nested stages, and provides a centered top receiver. Each support mechanism consumes
  the top receiver and provides a head-tilt axis. Every head exposes a source-envelope descriptor
  and consumes that tilt axis.
- Head envelope drives yoke/fork inside width, cheek height, pin length, boom-tip clearance and
  sweep radius. Mechanism family never forces a universal rectangular frame around every head.
- The dual-axis mechanism adds a captured vertical pan axis; the boom adds a captured horizontal
  boom axis. All pan, boom, head-tilt, leg-hinge, caster, barn-door and focus-ring revolutes are
  created through `AxisInterface`, `mate_axes`, and registered interface mates.
- `radial_support_count` drives real indexed geometry for every base family. For `weighted_disk`, N
  controls integral top ribs and matching underside rubber contact pads while preserving the source
  disk silhouette; it does not add fictitious legs. Disk radius is independently continuous from
  0.20 m to 0.50 m and does not alter core/raw diversity accounting.
- `mast_stage_count` drives stage topology, not a visual stripe: each stage is a separate nested tube
  with decreasing radius, a captured collar and a prismatic extension joint where applicable.
- Materials are selected by source family and semantic role. The DAG derives all dependent radii,
  clearances, offsets, joint limits, host capacities and total height before geometry is emitted.
