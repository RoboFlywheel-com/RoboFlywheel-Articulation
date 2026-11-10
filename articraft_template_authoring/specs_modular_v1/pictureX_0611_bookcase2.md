# pictureX/0611/bookcase2

Sources: `articraft_data/picture/0611/bookcase2/001.png`, `002.png`, `003.png`.

Identity boundary: larger bookcase/library storage with repeated shelves, vertical dividers, and book contents. Excludes simple wall shelf, wardrobe, and drawer-only cabinet.

Slots: `tower_style` = narrow_tower / wide_library / asymmetric_cubbies; `motion_style` = sliding_ladder / sliding_glass_panel / tilt_down_display_leaf; `shelf_count` = 3-8; `palette_style` = oak / industrial / walnut.

Motion semantics: sliding ladder and glass panel use lateral prismatic rails; display leaf uses a revolute lower-front hinge.

Sampling and validation: seed 0 is a wide library with sliding ladder. Sweeps should exercise all motion styles and width bands. Validator checks active module, joint metadata, and slot coverage.
