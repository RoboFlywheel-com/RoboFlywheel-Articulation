# pictureX/0611/bookcase1

Sources: `articraft_data/picture/0611/bookcase1/001.png`, `002.png`, `003.png`.

Identity boundary: tall household bookcase/display case with shelves, vertical side boards, back panel, books or display contents. Excludes drawer cabinets, desks, wardrobes, and empty abstract frames.

Slots: `frame_style` = tall_open / stepped_display / lower_cabinet; `front_style` = single_glass_door / paired_glass_doors / pullout_book_crate; `shelf_count` = 2-7; `palette_style` = oak / painted / walnut.

Motion semantics: glass fronts are vertical-edge revolute doors; pullout crate is a prismatic book tray. These motions are visible and supported by the front frame.

Sampling and validation: seed 0 is the reference tall open glass-door case. Sweeps should cover each front module and multiple shelf counts. Validator checks body, active child, joint metadata, and slot reporting.
