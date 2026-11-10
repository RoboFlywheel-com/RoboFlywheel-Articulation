# pictureX_0611_elevator_button_panel — SourceMap

source_map_schema: 1
export_category: pictureX_0611_elevator_button_panel
picture_category: 0611
picture_subcategory: elevator_button_panel
category_scope: An elevator car operating panel — one faceplate or console carrying N visibly numbered floor selectors, mechanical or touch, plus an auxiliary control module and the usual indicator hardware. Hall call stations with only two buttons, standalone floor indicators and lift control cabinets are outside this host.

sync_records:
  - rec_elevator_panel_var_accessibility_paddles_20260714
  - rec_elevator_panel_var_corner_wrap_console_20260714
  - rec_elevator_panel_var_destination_keypad
  - rec_elevator_panel_var_fire_service_cover_20260714
  - rec_elevator_panel_var_floor_n30_three_column_20260714
  - rec_elevator_panel_var_floor_n6_two_column_20260714
  - rec_elevator_panel_var_glass_touch_hybrid
  - rec_elevator_panel_var_horizontal_console
  - rec_elevator_panel_var_single_column_8
  - rec_elevator_panel_var_split_zone_banks
  - rec_elevator_panel_var_square_buttons
  - rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40
  - rec_picturex_0611__elevator_button_panel__002__png__airflex_batch_20260710_e78767714b92403da1268cdbe3f5a877

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_elevator_panel_var_accessibility_paddles_20260714/rev_000001 | reviewed | used | Adds oversized accessible paddle controls on their own prismatic plungers beside the floor buttons. Distinct auxiliary control. |
| rec_elevator_panel_var_corner_wrap_console_20260714/rev_000001 | reviewed | used | Wraps the faceplate around a car corner: two panes meeting at a right angle instead of one flat plate. Distinct panel family. |
| rec_elevator_panel_var_destination_keypad/rev_000001 | reviewed | used | Supplies a structurally distinct three-column destination-matrix faceplate with a separated action row. The template reuses that inspected matrix-and-action-rail host topology while keeping every multiplicity item a floor-labelled selector. |
| rec_elevator_panel_var_fire_service_cover_20260714/rev_000001 | reviewed | used | Adds a hinged `service_cover` on a REVOLUTE joint over the fireman controls. Distinct auxiliary control. |
| rec_elevator_panel_var_floor_n30_three_column_20260714/rev_000001 | reviewed | used | Spreads the floor buttons over three columns for a tall building. Distinct layout. |
| rec_elevator_panel_var_floor_n6_two_column_20260714/rev_000001 | reviewed | reference_only | Confirms that the two-column rule remains valid at N=6 and that every floor button keeps its own numbered moving cap; its structure is already represented by the compact and service two-column families. |
| rec_elevator_panel_var_glass_touch_hybrid/rev_000001 | reviewed | used | Supplies both a black-glass inset host and individually visible fixed touch cells. These enter separately as a panel host and a numbered touch-selector candidate; the touch candidate honestly uses fixed rather than prismatic selectors. |
| rec_elevator_panel_var_horizontal_console/rev_000001 | reviewed | used | A landscape console plate that runs across the car wall rather than down it. Distinct panel family. |
| rec_elevator_panel_var_single_column_8/rev_000001 | reviewed | used | One tall column of floor buttons. Distinct layout. |
| rec_elevator_panel_var_split_zone_banks/rev_000001 | reviewed | used | Two separated banks with a real gap and a divider between the zones. Distinct layout. |
| rec_elevator_panel_var_square_buttons/rev_000001 | reviewed | used | Square button lenses in square bezels instead of the round ones. Distinct button component. |
| rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40/rev_000001 | reviewed | used | Origin anchor: a compact flush stainless faceplate with a recessed tray, twelve explicitly numbered round illuminated buttons on prismatic plungers, door controls, alarm and key switch. |
| rec_picturex_0611__elevator_button_panel__002__png__airflex_batch_20260710_e78767714b92403da1268cdbe3f5a877/rev_000001 | reviewed | used | Second origin: a full-height service console whose display, message lens, speaker grille, screws and two-column floor field form a different host/layout family from the compact 001 plate. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| panel_family | compact_pair | panel + N layout | rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40/rev_000001 | model.py:L60-L156, model.py:L260-L444 | structure+motion | A compact filleted faceplate over a recessed tray with a two-column field; the source also puts a real one- or two-digit legend on every moving floor cap. |
| panel_family | service_pair | panel + N layout | rec_picturex_0611__elevator_button_panel__002__png__airflex_batch_20260710_e78767714b92403da1268cdbe3f5a877/rev_000001 | model.py:L78-L459 | structure+motion | A tall narrow service console carries display, message lens, grille and screws around a two-column floor field. |
| panel_family | single_column | panel + N layout | rec_elevator_panel_var_single_column_8/rev_000001 | model.py:L53-L223, model.py:L410-L465 | structure+motion | One centered column of individually numbered prismatic floor buttons; the host height follows the row count. |
| panel_family | three_column | panel + N layout | rec_elevator_panel_var_floor_n30_three_column_20260714/rev_000001 | model.py:L23-L45, model.py:L84-L467 | structure+motion | Three columns support the source's full thirty-floor field, proving the high-N host capacity and repeat rule. |
| panel_family | split_zone | panel + N layout | rec_elevator_panel_var_split_zone_banks/rev_000001 | model.py:L23-L66, model.py:L96-L539 | structure+motion | Two numbered banks have separate frames, a visible separator and an internal divider rather than a continuous undifferentiated grid. |
| panel_family | horizontal_console | panel + N layout | rec_elevator_panel_var_horizontal_console/rev_000001 | model.py:L28-L69, model.py:L100-L496 | structure+motion | A low wide console reflows N floor selectors across six columns and relocates display, message lens and grille into a landscape shell. |
| panel_family | corner_wrap | panel + N layout | rec_elevator_panel_var_corner_wrap_console_20260714/rev_000001 | model.py:L25-L100, model.py:L123-L532 | structure+motion | Two tilted faces meet at a spine and divide the floor selectors between their local planes; this is a different mounting topology, not a decorative wing. |
| panel_family | destination_matrix | panel + N layout | rec_elevator_panel_var_destination_keypad/rev_000001 | model.py:L23-L100, model.py:L342-L535 | structure+motion | A three-column matrix is separated from a two-control action rail by a real crossbar; the host rule grows the matrix by complete rows while retaining the source's distinct action zone. |
| panel_family | glass_inlay | panel + N layout | rec_elevator_panel_var_glass_touch_hybrid/rev_000001 | model.py:L141-L178, model.py:L423-L470 | structure | A tall stainless shell contains a framed black-glass inset and separate information apertures; N stations are allocated inside the inset rather than directly in bare metal. |
| panel_family | protected_service_bay | panel + N layout | rec_elevator_panel_var_fire_service_cover_20260714/rev_000001 | model.py:L311-L370, model.py:L492-L539 | structure+motion | The lower control zone is a recessed protected bay with a lintel and exposed hinge barrels, giving the auxiliary module a different host interface from an unbroken faceplate. |
| button_style | round_numbered | moving button | rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40/rev_000001 | model.py:L100-L156, model.py:L389-L444 | structure+motion | Round carrier and illuminated lens in an annular bezel, with the floor number built on the moving lens itself. |
| button_style | square_numbered | moving button | rec_elevator_panel_var_square_buttons/rev_000001 | model.py:L44-L56, model.py:L129-L207, model.py:L453-L502 | structure+motion | Square tactile carrier, square guide and square bezel, still carrying the numeric legend and the same bounded press joint. |
| button_style | wide_tactile_numbered | moving button | rec_elevator_panel_var_accessibility_paddles_20260714/rev_000001 | model.py:L142-L205, model.py:L502-L594 | structure+motion | A wide filleted rectangular cap, matching rectangular guide and tactile ridge form a genuinely different prismatic selector footprint; the floor number remains on the moving cap. |
| button_style | glass_touch_numbered | fixed touch selector | rec_elevator_panel_var_glass_touch_hybrid/rev_000001 | model.py:L423-L470 | structure | Each floor selector is an individually indexed illuminated cell on a connected black-glass backing. It is fixed by design and therefore does not pretend to have a mechanical press joint. |
| aux_style | key_switch | auxiliary control | rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40/rev_000001 | model.py:L333-L387 | structure+motion | A barrel key switch turns on a REVOLUTE joint about the panel normal. |
| aux_style | fire_service_cover | auxiliary control | rec_elevator_panel_var_fire_service_cover_20260714/rev_000001 | model.py:L118-L153, model.py:L494-L539 | structure+motion | A real cover plate and knuckle swing on a horizontal REVOLUTE hinge over the fire-service recess. |
| aux_style | accessibility_paddles | auxiliary control | rec_elevator_panel_var_accessibility_paddles_20260714/rev_000001 | model.py:L142-L205, model.py:L501-L607 | structure+motion | Three oversized rectangular accessibility paddles have distinct caps, guide wells, tactile bars and individual PRISMATIC plungers. |
| aux_style | door_alarm_cluster | auxiliary control | rec_picturex_0611__elevator_button_panel__001__png__airflex_batch_20260710_5af95b11f6ac4c81a8fbe8dc79222d40/rev_000001 | model.py:L155-L205, model.py:L388-L445 | structure+motion | Door-open, door-close and alarm are three separately iconed illuminated controls with independent prismatic plungers rather than one generic auxiliary block. |
| aux_style | emergency_intercom | auxiliary control | rec_picturex_0611__elevator_button_panel__002__png__airflex_batch_20260710_e78767714b92403da1268cdbe3f5a877/rev_000001 | model.py:L327-L420 | structure+motion | One red alarm plunger is paired with a separately mounted perforated speaker/intercom grille, changing both part tree and functional topology. |

## Multiplicity and N derivation

- `floor_count = 6 | 8 | 12 | 18 | 30`, applied to `panel_family`.
  - `observed_N`: all five values are directly evidenced: 6 in the short pair fork, 8 in the
    single-column fork, 12 in origin 001, 18 in origin 002, and 30 in the three-column fork.
  - `derived_N_range`: each family is index-general over the complete five-value set. The compact,
    portrait and split hosts grow in height; the horizontal host adds rows; the corner host
    rebalances the two local faces. Thirty remains inside the source-proven motion budget, and
    repeated button joints use one honest QC repeat group rather than deleting the high-N source.
  - validation: every increment adds one complete numbered selector. Mechanical styles add a cap,
    carrier/stem, bezel/aperture and prismatic joint; the source-backed glass-touch style adds one
    indexed illuminated cell to its fixed connected glass module. Host width/height, row count,
    service-band position, display position, inset capacity and corner-face allocation are all
    re-derived from N.

## Coverage note

All thirteen active records in the `0611 / elevator_button_panel` pool are reviewed. Twelve provide
runtime candidate evidence. The N=6 fork is retained as multiplicity evidence because its host is
otherwise structurally duplicate. Destination keypad contributes its matrix/action-zone host, and
glass touch contributes both its inset host and its honest fixed-selector topology.

The structural family intentionally bundles host silhouette with the N layout it must support.
The destination-derived family grows only its floor-selector matrix and keeps its action rail
separate. The glass-touch selector remains fixed when crossed with any host; mechanical selector
candidates remain prismatic. No candidate silently changes its joint topology to satisfy a host.

`core_domain = 10 (panel_family) x 4 (button_style) x 5 (aux_style) = 200`;
`raw_domain = 200 x 5 (floor_count) = 1000`.

Numeric legend rendering is an independent surface-detail parameter, not a core slot. Every style
still builds the actual floor designation on its selector surface, but numeral styling does not
inflate core/raw diversity.
