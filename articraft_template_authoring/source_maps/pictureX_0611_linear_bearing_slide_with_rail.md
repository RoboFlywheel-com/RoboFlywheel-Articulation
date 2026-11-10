# Linear bearing slide with rail — SourceMap

export_category: pictureX_0611_linear_bearing_slide_with_rail
slug: pictureX_0611_linear_bearing_slide_with_rail

Authoritative records live under `data/records`. This rebuild replaces the forbidden
`picturex_0611_source_replay` thin shell (which froze every joint at its rest pose) with a
self-contained single-file `TEMPLATE_DOMAIN` template.

The category identity is the prismatic slide: one guide rail and N bearing carriages that
translate genuinely end-to-end along the rail X axis. The carriage captures the rail through an
open cavity (round bore around a shaft, or a stepped open channel wrapping a profiled crown) plus
discrete bearing balls that graze the rail race. No `allow_overlap`, no motion clamping, no solid
block nested around a solid rail.

sync_records:
  - rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_093549_584407_4387eb47
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_101220_741681_83d08292
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47

## Source records (all five read in full)

| Record | Rev | model.py | Rail cross-section | Carriage/block | Rail-to-ground mount | Carriages | End treatment |
|---|---|---|---|---|---|---|---|
| rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b | rev_000001 | 452 L | round supported shaft (SBR) | compact filleted block, round bore + underside slot, C-seals | continuous full-length support foot L45-L49 **and** two discrete recessed cross ties L77-L83 | 4 (2 per rail) | open ends |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_093549_584407_4387eb47 | rev_000001 | 327 L | round supported shaft (SBR) | block + **wider overhanging top flange** (0.072 > body 0.064), annular wipers | continuous broad foot L57 **and** two discrete end plates L52-L53 | 4 (2 per rail) | open ends |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292 | rev_000001 | 268 L | profiled crown rail (base + crown) | **U-channel** block (top web + two legs), race liners | rail base bolted flat, no separate mount | **1** | open ends |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_101220_741681_83d08292 | rev_000001 | 275 L | profiled crown rail with race grooves | one-piece block, open-bottom channel, bearing retainers | rail base bolted flat, no separate mount | **1** | open ends |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47 | rev_000001 | 307 L | profiled stepped crown rail | stepped channel shell + **raised top plate on a pedestal** L68-L73 | two discrete **mounting bridges** L173-L180 | 4 (2 per rail) | **end-stop blocks** L165-L171 + limit sensor |

## Slots → candidates (accepted)

`rail_profile` is a structural-family slot: the rail cross-section and the carriage capture cavity
are inseparable (a round bore only captures a round shaft; an open channel only wraps a profiled
crown), so per hard-boundary #7 the rail↔capture pair is one slot. `carriage_block` (block
silhouette above the capture cavity), `rail_mount` (how the rail meets ground) and `end_treatment`
(end-of-travel hardware) are independently combinable with either rail profile: all three are
purely additive above/below the capture cavity and adapt through derived heights and travel insets.

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| rail_profile | round_shaft | supported round rail: stepped aluminium support (base, neck rib, shoulder strips) + hardened cylindrical shaft; carriage has a round bore and an underside clearance slot | rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b/rev_000001 | model.py:L39-L106, L109-L156, L159-L174, L260-L283 | accepted | continuous neck rib carries a Ø17 shaft at SHAFT_Z; block bore Ø17.3 with a 15 mm underside slot; secondary anchor 093549 model.py:L49-L64, L67-L83, L170-L176 |
| rail_profile | profile_rail | profiled crown rail: rectangular base + narrower crown with longitudinal race grooves; carriage is a stepped open channel wrapping the crown | rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292/rev_000001 | model.py:L19-L45, L48-L83, L153-L167 | accepted | base 18×4 + crown 10×5, carriage top web + two legs, race liners bridge to the crown flanks; secondary anchors 101220 model.py:L27-L66, L69-L121, L178-L184 and 101508 model.py:L26-L47, L50-L73 |
| carriage_block | plain_block | compact block, top face flush with the body, four blind top mounting bores | rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b/rev_000001 | model.py:L109-L156 | accepted | filleted block with no overhanging flange, four blind threaded top holes; also 101220 model.py:L69-L121 and 101211 model.py:L48-L83 |
| carriage_block | top_flanged_block | integral top flange overhanging the body on all four sides, screws on the flange | rec_use-the-attached-reference-image-as-the-primary-_20260712_093549_584407_4387eb47/rev_000001 | model.py:L67-L83, L113-L121 | accepted | `top_flange` 0.072×0.060 fused over a 0.064×0.052 body — wider in both X and Y, a genuinely different mounting silhouette |
| carriage_block | pedestal_plate_block | raised top plate standing off the shell on a short pedestal riser | rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47/rev_000001 | model.py:L68-L73, L115-L123 | accepted | `top_plate` 0.052×0.044×0.004 at z=0.054 above a 0.064×0.052 stepped shell whose top is lower — a separate raised machine table, not a flange |
| rail_mount | continuous_base_plate | one full-length plate running under the whole rail | rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b/rev_000001 | model.py:L45-L49 | accepted | `base` box spanning the whole RAIL_LENGTH under each rail; also 093549 model.py:L57 broad full-length aluminium foot |
| rail_mount | end_pillow_feet | two discrete transverse feet/bridges at the rail ends, rail elevated and open underneath between them | rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47/rev_000001 | model.py:L173-L180 | accepted | two `mounting_bridge_*` boxes at x=±0.218 only; also 002 model.py:L77-L83 recessed end ties and 093549 model.py:L52-L53, L62-L63 discrete end plates/pads |
| end_treatment | open_ends | bare rail ends, travel bounded only by the rail length | rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292/rev_000001 | model.py:L19-L45 | accepted | plain rail ends with no stop hardware; also 002, 093549, 101220 |
| end_treatment | capped_end_stops | end-stop blocks capping travel at both rail ends | rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47/rev_000001 | model.py:L165-L171 | accepted | `rail_*_end_stop_*` boxes 0.003×0.032×0.018 standing proud of the rail at x=±0.2315, shortening the usable travel envelope |

core_domain = 2 (rail_profile) × 3 (carriage_block) × 2 (rail_mount) × 2 (end_treatment) = **24**.

## Multiplicity `carriage_count` (N), item_slot = carriage_block

- Observed: N=1 single carriage (101211 model.py:L189-L198, 101220 model.py:L186-L201); the
  twin-rail records carry 2 carriages **per rail** (002 model.py:L285-L331, 093549
  model.py:L198-L237, 101508 model.py:L214-L237).
- Derivation: this template models one guide rail carrying N independent carriages. Observed
  per-rail counts are 1 and 2; the derived upper bound is 3, admissible because
  `rail_length ≥ 0.30` and `carriage_length ≤ 0.064` leave three non-colliding travel zones with
  clearance even with end stops fitted.
- N range: **1, 2, 3**. Spacing: the usable rail (after the end-treatment inset) is partitioned
  into N equal zones; carriage i homes at its zone centre and its symmetric prismatic bound is
  `b = (zone_len - carriage_footprint_x - inter_carriage_gap) / 2`, so adjacent carriages keep a
  positive gap at both extremes. Carriages on one rail physically cannot pass one another; this is
  a real kinematic bound, not motion clamping.
- Validation: the max-N corner drives every carriage to both limits; each stays captured on the
  rail and clear of its neighbours and of the end stops.

## Parameters and derivations

Independent (continuous — not counted in core/raw):
- `rail_length_m` (0.30–0.50 m) — source rails 0.300 / 0.460 / 0.500; derives usable span, zone
  length and travel.
- `carriage_length_m` (0.030–0.064 m) — source blocks 0.030 / 0.036 / 0.060 / 0.064; derives zone
  occupancy, travel and bearing-ball spacing.

Derived (local DAG):
- `rail_mount` sets `mount_top_z` (continuous plate 0.010 m; end feet 0.018 m) — every rail, shaft,
  carriage and stop height is re-derived from it.
- round_shaft: `shaft_radius = 0.0085`, `rib_top = mount_top_z + neck_h`,
  `shaft_z = rib_top + 0.4·shaft_radius`; carriage `bore_radius = shaft_radius + 0.0012` so the
  aluminium housing never touches the shaft, plus an underside slot clearing the neck rib.
- profile_rail: `rail_base_top = mount_top_z + base_t`, `rail_top_z = rail_base_top + crown_h`;
  carriage stepped channel = base envelope + 0.0012 and crown envelope + 0.0012 per side.
- carriage seat plane is derived by `mate_planes` from the rail's load-carrying top plane, so the
  block height follows `mount_top_z` and the active rail profile.
- `carriage_footprint_x = carriage_length + (0.006 if top_flanged_block else 0)`.
- `usable_half = rail_length/2 - end_margin`, `end_margin = 0.008` (open ends) or `0.014`
  (capped end stops, i.e. stop thickness + inset + running clearance).
- `zone_len = 2·usable_half / carriage_count`, `home_x_i`, travel bound `b` as above.

## Slide mechanism (entities / supports / axis / envelope / captured contact)

- Entities: one `guide_rail` part (`part.meta.role = "guide_rail"`) owning the rail profile, the
  mount and the end stops; N `bearing_carriage` parts (`role = "bearing_carriage"`).
- Support path: `rail_mount` → rail base / neck rib → shaft or crown → bearing balls → carriage.
- Prismatic axis: `+X`, the true travel direction, verified by a `ctx.pose` probe; joint origin at
  each carriage home `(home_x_i, 0, seat_z)` with `lower = -b`, `upper = +b`, both exercised.
- Envelope: the carriage cavity clears the rail by 1.2 mm on every face; adjacent carriages and the
  end stops bound the travel; the mount stays below the carriage's lowest geometry.
- Captured contact without any allowance: discrete bearing balls (spheres) on the carriage
  penetrate the rail race by **0.6 mm**. Spheres have an orientation-invariant AABB, and the
  penetrated axis' AABB intersection depth is exactly 0.6 mm, i.e. below the 1 mm overlap
  tolerance on that axis, so the pair is connected for `fail_if_isolated_parts` and never reported
  by `fail_if_parts_overlap_*`. The rail base/crown (and the shaft) are separate visual elements so
  the grazed element's AABB is the race itself, not the whole rail.
  - round_shaft: `bearing_ball_{0,1}` sit at the top of the bore on the shaft crest.
  - profile_rail: `bearing_ball_{0..3}` sit against the two crown flanks.

## Rejected decompositions

- Independent rail-profile × carriage-capture slots rejected: a round bore cannot capture a
  profiled crown, so capture topology follows the cross-section and they form one family slot.
- Twin parallel rails as a rail-count slot rejected in favour of N carriages on one rail: the
  multiplicity axis of the category is carriage count, and per-rail counts (1, 2) anchor N.
- A drive element (leadscrew / belt) was looked for in all five records and **not found** — none of
  them models a screw, nut, pulley or belt, so no drive slot is invented.
- The 101508 limit sensor + bracket + gland + cable is host-conformal decoration on the rail part;
  it is emitted with `capped_end_stops` but is not claimed as a structural axis.
- Motion clamping, whole-part `allow_overlap`, and box placeholders for the rail profile or the
  block cavity are rejected outright (hard bans).
