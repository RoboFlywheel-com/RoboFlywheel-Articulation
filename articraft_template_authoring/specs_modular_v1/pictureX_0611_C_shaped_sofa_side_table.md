# pictureX/0611/C-shaped_sofa_side_table

Source: `articraft_data/picture/0611/C-shaped_sofa_side_table/001.png`.

Identity boundary: C-shaped side table that slides over/around sofa arms, with low foot, rear uprights, and cantilevered top. Excludes ordinary four-leg end table and tray stand.

Slots: `base_style` = flat_c_base / sled_base / caster_base; `top_module` = fixed_tray_with_pivot / height_adjustable_top / swing_out_leaf; `palette_style` = oak / painted / industrial / walnut; height band is sampled from resolved dimensions.

Motion semantics: top module is either height-adjustable prismatic or revolute about the rear corner. The motion is constrained by visible rear uprights.

Sampling and validation: seed 0 is a flat C-base with height-adjustable top. Validator checks body, table top, active joint, and slot metadata.
