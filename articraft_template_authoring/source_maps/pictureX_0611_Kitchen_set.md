# Kitchen set — SourceMap

export_category: pictureX_0611_Kitchen_set

Authoritative records live under `data/records`. This rebuild is a single installed
wall-run kitchen cabinetry assembly: one fixed carcass (base run + shallow upper run +
tall left feature + stone countertop with real sink/cooktop cutouts + backsplash +
faucet), with N independently articulated fronts — N revolute upper cabinet doors and N
prismatic base drawers. The two source records are the structural-candidate pool; they
genuinely differ in the door front, the drawer front, and the tall left feature, so those
three become the three component slots. Common kitchen anchors (carcass, countertop
cutouts, sink basin, cooktop, backsplash, faucet) are shared, not slotted.

Frame convention for the rebuild: +X runs along the wall, +Y points toward the viewer
(front), +Z up. The carcass back sits at -Y (wall). Doors swing toward +Y; drawers slide
toward +Y. (Source 002 used front=-Y and source 003 used front=+Y; the rebuild standardizes
on +Y. This is a coordinate choice, not a structural difference.)

sync_records:
  - rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f
  - rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d

## Component slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| door_style | framed_panel | revolute cabinet door | rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f/rev_000001 | model.py:L229-L301 | accepted | perimeter-framed olive panel + two dark hinge knuckles at the hinge edge + optional edge pull; revolute vertical hinge, axis (0,0,±1), swings outward |
| door_style | slab | revolute cabinet door | rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d/rev_000001 | model.py:L65-L102 | accepted | handleless flat slab + narrow routed finger-edge reveal; revolute vertical hinge on the hinge line, axis (0,0,±1), swings outward. Distinct part-tree (no framing rails, no knuckles) |
| drawer_style | runner_tray | prismatic drawer | rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f/rev_000001 | model.py:L303-L390 | accepted | hollow tray (front + floor + two sides + back) with an edge-pull bar and two carcass-mounted side runners; prismatic pull toward viewer |
| drawer_style | reveal_tray | prismatic drawer | rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d/rev_000001 | model.py:L105-L161 | accepted | hollow tray (front + bottom + two sides + back) with a handleless finger reveal, retained by side overlap; prismatic pull toward viewer. Distinct part-tree (no edge-pull bar, no separate carcass runners) |
| tower_style | appliance_tower | fixed tall left feature | rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f/rev_000001 | model.py:L110-L126 | accepted | closed full-height tower: two side gables, top, back, internal shelves, integrated black oven chassis + glass + control + handle |
| tower_style | open_shelf_tower | fixed tall left feature | rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d/rev_000001 | model.py:L253-L265 | accepted | open full-height shelving tower: two side gables, ribbed charcoal back, stack of open horizontal shelves, vertical ribs. Distinct part-tree (open vs enclosed, no oven) |

| island_module | waterfall_peninsula | fixed counter-height return | rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f/rev_000001 | model.py:L24-L40, L178-L179 | accepted | T-shaped rear counter with an *integral waterfall peninsula*: the counter geometry itself unions a peninsula slab, plus a full-height waterfall oak side panel and a concealed rear brace making the load path explicit. Closed volume, no cubbies |
| island_module | open_cubby_return | fixed counter-height return | rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d/rev_000001 | model.py:L105-L161, L267-L268 | accepted | separate counter-height island: dark OPEN cubbies on one side and a bank of pale-oak drawer fronts on the other (`_add_island_drawer`). Distinct part tree (open compartments + front bank vs closed waterfall volume) |

## Shared (non-slotted) kitchen anchors

- Carcass base run (toe kick, back, floor, bay dividers, top rail): 002 model.py:L99-L143;
  003 model.py:L182-L251. Rebuilt as one fixed root part `carcass`.
- Shallow upper cabinet run (back, bottom, top, gables) above the backsplash: 002
  model.py:L136-L143; 003 model.py:L238-L251.
- Countertop with real through-cutouts for sink and cooktop (cadquery slab + cuts): 002
  model.py:L23-L40 & L162-L176; 003 model.py:L44-L62 & L199-L203. Preserved as
  `mesh_from_cadquery` characteristic geometry (not a box placeholder).
- Sink basin (open-top recessed basin walls + bottom): 003 model.py:L205-L211; 002
  model.py:L43-L68. Hung from the counter at the rear of one base bay, behind the drawer box.
- Cooktop / induction hob (flush thin slab on the counter + burner marks): 002
  model.py:L184-L198; 003 model.py:L213-L216. Flush — no downward intrusion.
- Backsplash panel between counter and uppers: 002 model.py:L129; 003 model.py:L218-L236.
- Faucet (deck flange + riser + spout cylinders): 002 model.py:L200-L224; 003 model.py:L286-L295.

## Multiplicity and source-derived placement

- `bay_count = 2 | 3 | 4 | 5`, item_slot `drawer_style`. N is the number of base bays. Each
  bay owns exactly one base drawer (prismatic) and one upper door (revolute), so N drives
  both the drawer count and the upper-door count, plus N+1 base dividers and N+1 upper gables.
- Source-derived: 002 has a 4-bay upper run with 4 hinged upper doors (model.py:L392-L407) and
  a base run divided at 5 gables (model.py:L102-L107); 003 has a 4-bay lower run
  (model.py:L192-L195) with 3 handleless upper slab doors (model.py:L299-L331). Observed bay
  counts cluster at 3–5; the rebuild range 2–5 brackets this with a modest low extreme.
- Spacing: bay centers derive from `bay_width_m`; run width = `bay_count * bay_width_m`.
  Sink is placed over bay 0, cooktop over bay `bay_count-1` (distinct for all N>=2).

## Parameters and derivations

- `bay_width_m` (0.50–0.75 m) sets each bay width; run width, bay centers, door/drawer widths,
  divider and gable spacing all derive from it and `bay_count`.
- `counter_depth_m` (0.55–0.66 m) sets carcass Y depth; drawer box depth, basin depth-behind,
  upper run depth, and counter footprint derive from it.
- `base_height_m` (0.82–0.92 m) sets the counter top height; toe-kick, drawer height/seat,
  basin drop, backsplash and upper-run vertical placement derive from it.
- Door width = bay_width − reveal; door height derived per row. Drawer front width = bay_width −
  reveal; drawer box depth = counter_depth − front/back clearance; drawer travel derives from
  box depth so the tray stays retained. Sink basin bottom derives below the counter and sits at
  the rear of the bay, cleared from the drawer box in Y.

## Category identity and motion

- Exactly one fixed `carcass` root part; N `door` parts (revolute, axis (0,0,±1), swing toward
  +Y); N `drawer` parts (prismatic, axis (0,1,0), pull toward +Y). All fronts are direct
  children of the carcass.
- Every door hinge uses `AxisInterface`/`mate_axes` + `register_interface_mate` (vertical axis
  on the real hinge line, child origin on the axis). Every drawer uses a prismatic joint whose
  axis is the real pull direction, with lower=closed / upper=full-extension.
- Drawers are hollow trays (front + bottom + two sides + back), never solid boxes. Doors carry
  the framed-panel vs slab distinction; drawers carry the runner-tray vs reveal-tray distinction;
  the tall left feature carries the appliance-tower vs open-shelf-tower distinction.

## Rejected decompositions

- Making the sink/cooktop/faucet/backsplash their own slots is rejected: they are shared
  identity anchors present in both records, not interchangeable structural variants.
- Independent per-bay door-vs-drawer selection is not modeled as a slot: the door_style and
  drawer_style slots already capture the two front part-trees, applied to the upper row (doors)
  and base row (drawers) respectively; a free per-bay kind flag would add combinatorics without
  new source-anchored structure.
- (SUPERSEDED) The 002 peninsula vs 003 island was previously rejected as "not a clean drop-in
  interchange". That was over-cautious: `TemplateDomain` has no compatibility gates precisely
  because host adaptation is expected to absorb this, and the two records differ in part tree
  (closed waterfall volume vs open cubbies + drawer-front bank), which is exactly what makes a
  structural candidate. It is now the `island_module` slot, taking core_domain 8 -> 16.
- Both island candidates are modelled as counter-height returns ATTACHED to the run rather than a
  detached volume: a genuinely freestanding island touches nothing and QC reports it as an
  isolated part. 003's island drawers are rendered as a fixed drawer-front bank because the
  working-drawer axis is already carried by `drawer_style`; duplicating it here would repeat an
  existing axis instead of adding a new one.
