# pictureX/0611/Bookshelf_with_books

Source: `articraft_data/picture/0611/Bookshelf_with_books/001.png`.

Identity boundary: open bookshelf whose contents are visibly books, stacks, or display objects. Excludes closed bookcase variants where doors dominate and non-book storage racks.

Slots: `shelf_layout` = open_grid / leaning_ladder / low_console; `book_arrangement` = dense_rows / mixed_stacks / display_objects; `motion_module` = sliding_bookend / pullout_reference_shelf / hinged_secret_panel; `palette_style` = oak / painted / industrial.

Motion semantics: the movable element is a plausible furniture accessory, not the shelf identity itself: sliding bookend, pullout shelf, or hinged panel.

Sampling and validation: seed 0 creates an open grid with dense books and a sliding bookend. Validator confirms body, active accessory joint, and slot metadata.
