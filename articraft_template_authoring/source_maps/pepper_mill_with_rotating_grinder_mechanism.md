# pepper_mill_with_rotating_grinder_mechanism — expanded reviewed SourceMap

export_category: pepper_mill_with_rotating_grinder_mechanism

sync_records:
  - rec_picturex_0611__pepper_mill_with_rotating_grinder_mechanism__001__png_05147042d0f6482383d51f7b7fb9f35a
  - rec_0611_pepper_mill_with_rotating_grin_var_body_form_waisted_wood
  - rec_0611_pepper_mill_with_rotating_grin_var_body_form_straight_glass
  - rec_0611_pepper_mill_with_rotating_grin_var_body_form_faceted_metal
  - rec_0611_pepper_mill_with_rotating_grin_var_drive_top_crank
  - rec_0611_pepper_mill_with_rotating_grin_var_drive_side_crank
  - rec_0611_pepper_mill_with_rotating_grin_var_adjustment_top_nut
  - rec_0611_pepper_mill_with_rotating_grin_var_adjustment_indexed_base_collar
  - rec_0611_pepper_mill_with_rotating_grin_var_selector_coarse_fine_slide
  - rec_0611_pepper_mill_with_rotating_grin_var_reservoir_count_dual_chamber
  - rec_0611_pepper_mill_with_rotating_grin_var_closure_hinged_dust_cap

## Accepted independent slots

| slot | candidate | diversity_axis | source_type | record/revision | exact model.py:Lx-Ly | status | key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| body_form | white_clear_selector_body | ③ parent body | parent | `rec_picturex_0611__pepper_mill_with_rotating_grinder_mechanism__001__png_05147042d0f6482383d51f7b7fb9f35a/rev_000001` | `model.py:L1-L699` | accepted | clear selector body, reservoir and grinder bridge |
| body_form | waisted_wood_body | ③ waisted wood | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_body_form_waisted_wood/rev_000001` | `model.py:L1-L723` | accepted | waisted shell and flared foot |
| body_form | straight_glass_body | ③ straight glass | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_body_form_straight_glass/rev_000001` | `model.py:L1-L700` | accepted | clear cylindrical reservoir |
| body_form | faceted_metal_body | ①/③ faceted metal | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_body_form_faceted_metal/rev_000001` | `model.py:L1-L731` | accepted | polygonal metal reservoir |
| drive | top_twist_cap | ② twist input | parent | `rec_picturex_0611__pepper_mill_with_rotating_grinder_mechanism__001__png_05147042d0f6482383d51f7b7fb9f35a/rev_000001` | `model.py:L1-L699` | accepted | top cap on vertical rotor |
| drive | top_crank | ② top crank | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_drive_top_crank/rev_000001` | `model.py:L1-L734` | accepted | offset crank and grip |
| drive | side_crank | ② side crank | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_drive_side_crank/rev_000001` | `model.py:L1-L844` | accepted | lateral crank on vertical shaft |
| adjustment | top_nut | ② top nut | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_adjustment_top_nut/rev_000001` | `model.py:L1-L679` | accepted | adjustment nut and ring |
| adjustment | indexed_base_collar | ② indexed collar | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_adjustment_indexed_base_collar/rev_000001` | `model.py:L1-L784` | accepted | base collar with index marks |
| adjustment | coarse_fine_slide | ② selector slide | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_selector_coarse_fine_slide/rev_000001` | `model.py:L1-L706` | accepted | coarse/fine side selector |
| reservoir | single_chamber | ① single reservoir | parent | `rec_picturex_0611__pepper_mill_with_rotating_grinder_mechanism__001__png_05147042d0f6482383d51f7b7fb9f35a/rev_000001` | `model.py:L1-L699` | accepted | one enclosed chamber |
| reservoir | dual_chamber | ① dual reservoir | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_reservoir_count_dual_chamber/rev_000001` | `model.py:L1-L826` | accepted | connected divider and second chamber |
| closure | open_top | ② open grinder seat | parent | `rec_picturex_0611__pepper_mill_with_rotating_grinder_mechanism__001__png_05147042d0f6482383d51f7b7fb9f35a/rev_000001` | `model.py:L1-L699` | accepted | open top shoulder |
| closure | hinged_dust_cap | ② dust cap | forked_anchor | `rec_0611_pepper_mill_with_rotating_grin_var_closure_hinged_dust_cap/rev_000001` | `model.py:L1-L718` | accepted | hinged cap carried by shoulder |

Source spans cover each full revision because each fork changes its helper and assembly
section: body revisions 700–731 lines, drive revisions 699/734/844, adjustment
679/784/706, dual chamber 826 and dust cap 718. The parent is
`model.py:L1-L699`.

## Assembly and fidelity decisions

- The body slot owns reservoir walls, cavity, grinder bridge and a derived drive
  bearing. Dual-chamber adds a connected internal divider; it is not a second
  unrelated object.
- Drive remains a vertical Z continuous joint for all three inputs. Side crank is
  still a lateral arm on the vertical rotor, as confirmed in its source revision.
- Adjustment candidates are embedded into the rotating drive or its local body
  seat with source-backed nut, collar or coarse/fine slide geometry.
- The full independent domain is `4 × 3 × 3 × 2 × 2 = 144`, with no multiplicity.
