# Floor-standing drafting table — SourceMap

export_category: pictureX_0611_Floor_standing_drafting_table

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

SOURCES = 1. The single source record is a freestanding wooden A-frame writing
easel: two splayed oak side-rail frames with square floor feet, a tall narrow
matte writing panel framed by top/lower rails, a top hinge crown carrying a steel
hinge pin, two revolute folding hinges about a shared +X pin, and a rigid side
strap (spreader) that acts as a revolute deployed-stance travel stop.

For the `Floor_standing_drafting_table` category the recognizable identity is a
grounded floor stand carrying a single tiltable drawing surface with a
height/tilt adjustment mechanism. The source supplies, directly, the splayed
oak leg/foot family, the tall framed writing panel (→ the tilting drawing
board), the +X hinge line and captured hinge-pin mechanism (→ the board tilt
revolute), and the side prop/travel-stop hardware (→ the angle-hold family).
There is no height column in the source; per the category definition ("height
column is core mechanism") a central telescoping lift is added by controlled
world-knowledge extrapolation of real floor drafting tables — it is a genuine
prismatic mechanism, not decorative. Additional stand-leg families and rotary
lock controls are extrapolated as structurally distinct floor-stand variants; no
fake internal structure is fabricated.

sync_records:
  - rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92

## Slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| stand_base | splayed_aframe | splayed oak side-rail A-frame leg family | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L38-L75 | accepted | source splayed side rails (`LEG_SPLAY`), end-grain square feet, integral leg style |
| stand_base | xbrace_splayed | splayed legs + floor runners + X side braces | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L38-L75 | accepted (world-knowledge fork of the splayed source frame) | same splayed-leg source family with added floor runners and diagonal X side bracing |
| stand_base | four_post | four straight corner posts + box apron | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L38-L75 | accepted (world-knowledge floor-stand variant) | vertical corner posts replacing splay; standard floor drafting-stand leg topology |
| stand_base | trestle_pair | paired A-frame trestle ends tied by stretchers | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L38-L75 | accepted (world-knowledge floor-stand variant) | two end trestles + lengthwise stretchers; classic drawing-table stand |
| angle_lock | friction_cheeks | plain friction hinge cheeks (no teeth) | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L229-L260 | accepted | source side strap / prop is a friction-held stance stop; cheeks host visual |
| angle_lock | toothed_ratchet | linear toothed ratchet racks under the board | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L229-L260 | accepted (world-knowledge angle-hold fork) | ratchet racks are the common toothed variant of the prop travel-stop |
| angle_lock | curved_quadrant | annular toothed quadrant plate about the tilt axis | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L229-L260 | accepted (world-knowledge angle-hold fork) | curved quadrant on the +X tilt axis; standard drafting-board angle plate |
| control_form | paired_disk_knobs | two symmetric side lock disks (revolute) | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L309-L330 | accepted | source spreader is a real side revolute control; two symmetric knob disks |
| control_form | lobed_knobs | two lobed grip knobs (revolute) | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L309-L330 | accepted (world-knowledge control fork) | lobed hand-knob variant of the side lock control |
| control_form | crank_winders | two crank/winder handles (revolute) | rec_picturex_0611__floor_standing_drafting_table__001__png_385aa10c9a924b5f984d263495556b92/rev_000001 | model.py:L309-L330 | accepted (world-knowledge control fork) | crank-winder variant of the side lock control |

## Core mechanism entities, supports, joint axes and ranges

- Tilting drawing board — REVOLUTE about +X, hinge line on the board front/low
  edge. Source hinge pin `hinge_pin` (model.py:L175-L183) + folding revolute
  hinges `front_hinge`/`rear_hinge` about `axis=(1,0,0)` (model.py:L262-L305).
  Board authored flat in its own frame; a captured tilt barrel represents the
  board knuckle around the carriage hinge pin. Range derived: lower≈-0.30 rad
  (front-low) .. upper≈+0.55 rad (steep). This is the "surface flat vs max
  tilt" edge pair.
- Height lift — PRISMATIC +Z. Central/paired telescoping guide: grounded stand
  presents outer sleeves at the four corner positions, the lift carriage rides
  inner tubes inside them. Range 0 .. `lift_travel_m` (0.10–0.20 m). This is the
  "min/max height" edge pair. World-knowledge extrapolation (no source column).
- Two side lock controls — REVOLUTE +X on the carriage, source spreader pivot
  `spreader_pivot` axis=(1,0,0) (model.py:L309-L330). Full-turn rotary knobs.
- Supports: every stand candidate builds its floor legs up to ONE shared
  four-corner sleeve interface (front y≈-0.43, rear y≈+0.43, x=±SIDE_X). The
  carriage's four inner tubes + upper hinge/knob frame mate identically to every
  base. Board hinge rail spans the full board width; angle-hold hardware and
  tool trays sit in the under-board zone the tilting board provably clears.

## Multiplicity and parameters

- `tray_count = 0 | 1 | 2 | 3`, applied to `stand_base`. Adds N cosmetic tool /
  supply drawer faces + pulls in the stand front apron zone under the board.
  Extrapolated repeated unit; contributes to raw domain only.
- `board_width_scale` (0.92–1.10 ratio) scales board width and derives hinge
  rail span, side-rail track, tray apron width.
- `board_depth_scale` (0.95–1.08 ratio) scales board depth and derives lip/paper
  channel reach and the flat-pose over-mast clearance.
- `lift_travel_m` (0.10–0.20 m) sets the prismatic upper limit and derives inner
  tube length, sleeve length and tube insertion overlap.
- Derived: half_width, board_depth, hinge span, sleeve/tube overlap, tray cell
  width, tilt lower/upper all recomputed from the independent params.

## Category identity and motion

- Exactly one grounded `floor_stand`, one prismatic `lift_carriage`, one revolute
  tilting `drawing_board`, and two revolute `lock_control` parts are required.
- Every stand candidate keeps a recognizable floor-standing drafting-table
  silhouette: floor feet, a lift column, a wide tiltable drawing surface.
- No motion clamping. The tilt and lift joints have real mechanical travel;
  angle-hold hardware and trays are placed to clear the full board sweep.

## Rejected decompositions

- Independent leg × board × tray slots with topology conflicts are rejected;
  all bases build to the single shared sleeve interface so every combination
  builds (no compatibility gate).
- A dual-fold easel (the raw source topology) is not carried as-is: the category
  is a single-surface floor drafting table, so the two folding frames collapse to
  one tilting drawing board on a floor stand.
- Color / material-only and pure uniform-scale variants are not candidates.
