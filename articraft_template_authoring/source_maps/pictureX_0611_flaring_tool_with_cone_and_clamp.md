# Flaring tool with cone and clamp — SourceMap

export_category: pictureX_0611_flaring_tool_with_cone_and_clamp

Records root: `<ARTI_SKILL_ROOT>/arti-template/data/records`

SOURCES = 2. These two records are the entire structural-candidate pool. Each is a
plumbing/tubing flaring tool: a split clamp bar with a row of progressively sized
tube seats, a cast yoke that positions a feed screw over one seat, a rotary feed
screw that drives a conical die axially into the tube end, and a side yoke-lock
screw. The screw-fed cone (rotary drive + prismatic axial advance) and the split
clamp bar are the core mechanism and are shared by every candidate; slots are
declared only where the two records genuinely differ in part tree, joint, or
interface.

sync_records:
  - rec_picturex_0611__flaring_tool_with_cone_and_clamp__001__png__airflex_batch_20260710_52f7016c9eb84902806fb01f2892cffe
  - rec_picturex_0611__flaring_tool_with_cone_and_clamp__002__png__airflex_batch_20260710_11b92ba5965f4a87b12afcd7024803e9

Short record ids used below:
  - REC001 = rec_picturex_0611__flaring_tool_with_cone_and_clamp__001__png__airflex_batch_20260710_52f7016c9eb84902806fb01f2892cffe
  - REC002 = rec_picturex_0611__flaring_tool_with_cone_and_clamp__002__png__airflex_batch_20260710_11b92ba5965f4a87b12afcd7024803e9

## What each record actually models

REC001 (`.../REC001/revisions/rev_000001/model.py`, 600 lines) — "bench_tube_flaring_tool":
parts fixed_jaw (root single-piece box bar), moving_jaw (swinging half), yoke (cast
inverted-U windowed frame), feed_screw (threaded shaft + straight sliding tommy handle
with two ball ends), flaring_cone (loft cone die), lock_screw (side yoke clamp with a
straight tommy handle). 5 counterbored tube holes at 40 mm pitch, 5.0–12.7 mm diameters.
Yoke SLIDES along the hole row (`yoke_slide`, PRISMATIC +X, ±0.080). Joints: jaw_pivot
REV +Z (0..0.44); yoke_slide PRISM X; feed_screw_turn REV Z (0..8π); cone_feed PRISM -Z
(0..0.008, `constrained_by` the feed turn); lock_screw_turn REV Y. No end clamp screw.

REC002 (`.../REC002/revisions/rev_000001/model.py`, 732 lines) — "flaring_tool_002":
parts rear_jaw (root split half), front_jaw (moving split half, semicircular tube seats
+ three-knuckle hinge), clamp_screw (end wing screw tightening the split bar), yoke (cast
twin-cheek frame + top bridge + threaded collar), yoke_lock (tommy bar), feed_screw
(lathed ring-thread shaft + broad cast butterfly WING handle), cone (lathe die). 6 split
tube holes at 42 mm pitch, 6–16 mm diameters. Yoke PIVOTS about a vertical axis at the
working hole (`yoke_pivot`, REVOLUTE Z, ±0.16). Extra `clamp_rotation` REV Z end screw.
Joints: jaw_pivot REV -Z; clamp_rotation REV Z; yoke_pivot REV Z; yoke_lock_rotation REV Y;
feed_rotation REV Z (0..6π); cone_travel PRISM -Z (0..0.015).

## Slots → candidates (candidate anchoring)

| Slot | Candidate | Source type | Record/Revision | model.py:Lx-Ly | Status | Distinction |
|---|---|---|---|---|---|---|
| handle_style | tommy_bar | straight sliding T-handle + ball ends | REC001/rev_000001 | model.py:L251-L313 | accepted | thin chrome tommy bar through a hub with two spherical stops; dresses the feed, lock (and end) screws — adds 3 elements per screw |
| handle_style | wing_handle | broad cast butterfly wing | REC002/rev_000001 | model.py:L142-L163, L328-L345 | accepted | lofted two-lobe cast wing on a hub; one broad element per screw, distinct silhouette |
| yoke_frame | inverted_u_cast | cast inverted-U windowed frame | REC001/rev_000001 | model.py:L78-L121 | accepted | ONE continuous cast arch with an open lower window, arched crown, narrow top boss |
| yoke_frame | twin_cheek_cast | cast twin-cheek frame + bridge + collar | REC002/rev_000001 | model.py:L96-L139 | accepted | TWO opposed cheeks, separate top bridge box and a bored wide collar; open between the cheeks |
| yoke_mount | sliding | PRISMATIC yoke carriage | REC001/rev_000001 | model.py:L324-L332 | accepted | yoke indexes along +X across the seat row (prismatic X, travel = the seat row) |
| yoke_mount | pivoting | REVOLUTE yoke pivot | REC002/rev_000001 | model.py:L372-L380 | accepted | yoke swings ±0.16 rad about the vertical axis at the working seat (revolute Z) |
| end_clamp | plain_hinge | split jaw, hinge only, no end screw | REC001/rev_000001 | model.py:L31-L75, L315-L323 | accepted | bar closed by the moving-jaw hinge alone; pin + retainer on the bar, clearance barrel on the jaw (no captured screw) |
| end_clamp | screw_clamp | split jaw + captured end screw | REC002/rev_000001 | model.py:L57-L93, L275-L287, L363-L371 | accepted | adds a rotary clamp screw part (REV Z) captured in a real split end bore that tightens the bar |

core_domain = 2 × 2 × 2 × 2 = 16. `tube_hole_count` is multiplicity and is NOT counted.

## Shared core mechanism (every candidate)

- clamp bar (root, role `clamp_bar`) with N progressively sized through seats, a per-seat
  counterbore, a hinge pin and two fixed knuckles — REC001 L31-48/L177-193, REC002 L57-93/L248-259.
- moving_jaw (role `moving_jaw`) with a barrel turning inside the fixed knuckles on a real
  running clearance — REC001 L51-75, REC002 L57-93 (three-knuckle hinge).
- feed_screw (role `feed_screw`): lathed ring-thread shaft, REVOLUTE about the true spindle
  Z axis at the yoke collar — REC001 L222-256/L333-342, REC002 L165-183/L328-345/L390-399.
- flaring_cone (role `flaring_cone`): conical die on a PRISMATIC -Z axial advance riding the
  SAME spindle axis down into the working seat; separate scalar joint `constrained_by` the
  feed turn — REC001 L124-135/L343-356, REC002 L186-199/L400-412.
- yoke_lock (role `yoke_lock`): side yoke-lock screw, REVOLUTE about Y — REC001 L280-313/L357-365,
  REC002 L296-326/L381-389.

## Multiplicity and derivations

- `tube_hole_count = 4 | 5 | 6 | 7`, item_slot = `end_clamp`. REC001 shows 5, REC002 shows 6.
  N sets the number of through seats, their counterbores, the N `<slot>__<candidate>__hole_size_marker_i`
  plates and the clamp-bar length. Seats are indexed about the working seat at x=0:
  seat i at x=(i - N//2)·pitch; diameters increase monotonically across the row.
- Independent params: `bar_pitch_m` (0.038–0.046; source ~0.040/0.042), `bar_width_m`
  (0.024–0.030; source 0.026/0.028), `bar_height_m` (0.018–0.030; source 0.028/0.018).
- Derived: end margin = 1.4·pitch; bar length; yoke travel = the seat row; yoke straddle span
  = bar_width − 0.003; leg foot z = bar_height − 0.0006; cone radius at the bar's top plane
  from the groove half width; every bore radius from the part it clears.

## Mechanism entities / axes / ranges / envelopes

- feed_screw_turn: REVOLUTE, axis Z on the spindle centreline at the yoke collar top;
  `mate_axes` + `register_interface_mate`. Range 0..8π.
- cone_feed: PRISMATIC, axis (0,0,-1) on the SAME spindle line, 0..0.017 (12 mm retract +
  5 mm penetration). The cone tip descends into the bar's flare groove with 1 mm floor
  clearance and >0.8 mm radial clearance, so full advance is real clearance, not masked overlap.
- yoke_mount sliding: PRISMATIC +X, travel = seat row. pivoting: REVOLUTE Z at the working
  seat, ±0.16 rad — that axis IS the spindle axis, so the cone never leaves the bore.
- jaw_pivot: REVOLUTE +Z at the hinge, 0..0.45. MEASURED: +q lifts the free end into +Y,
  away from the fixed half; −q would drive it through the fixed jaw.
- yoke_lock_turn: REVOLUTE Y (registered). clamp_rotation (screw_clamp only): REVOLUTE Z
  at the bar's end bore (registered).

## Per-element legit contacts (no allow_overlap anywhere)

- yoke legs seat on the bar's top face, 0.6 mm vertical lap, invariant for every yoke pose.
- fixed upper/lower knuckles lap the moving jaw's barrel by 0.6 mm in Z, concentric with the
  pivot, so the capture holds at every jaw angle.
- feed-screw thrust flange bears on the collar top, 0.6 mm in Z, spin invariant.
- four ball detents on the yoke's guide ribs graze the cone's shank by 0.6 mm across the WHOLE
  stroke (spheres: orientation-invariant AABB, wholly inside the cone's AABB).
- two ball detents on the lock stem graze the lock bore by 0.6 mm, spin and pivot invariant.
- clamp-screw flange bears on the bar's top face, 0.6 mm in Z, spin invariant.
- everything else is a real CAD clearance fit (knuckle bore > pin, yoke bore > cone envelope,
  collar bore > shaft, lock/clamp bore > stem): AABBs interpenetrate but fcl reports no contact.

## Deviations from the sources, and why

- Both source yokes straddle the bar in Y (REC001 legs at y=±0.042; REC002 cheeks at y=±0.033)
  and both sources hid the consequence behind `allow_overlap` / an unexercised jaw. With the
  hinge exercised to its limit the moving jaw sweeps a·tan(q) sideways at the yoke station
  (~63 mm at q=0.45, a=130 mm), so no Y cheek clearance is achievable at any credible bar
  width. The rebuild keeps both cast yoke silhouettes but bridges the working seat in X: the
  legs come down fore and aft of the seat and seat on the bar's top face. Clamp-open and yoke
  poses become genuinely independent, and the cone passes between the legs.
- The bar carries a continuous flare groove along the seat row (a real chamfered vee on this
  tool family). The sliding yoke can stop between seats in random motion-QC poses, so the
  cone's clearance is derived from the groove rather than from a single seat diameter.

## Rejected decompositions

- Independent "clamp bar profile" slot beyond seat count: the two bars differ only in seat
  count (multiplicity) and the presence of the end screw (captured by end_clamp), so a
  separate profile slot would be material-only. Rejected.
- Treating cone advance as a mimic of the feed screw: cross-domain revolute→prismatic mimic
  is unsupported; both sources keep a separate constrained scalar prismatic. Kept as source.
