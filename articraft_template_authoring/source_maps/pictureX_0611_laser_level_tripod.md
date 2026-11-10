# Laser level tripod — SourceMap

export_category: pictureX_0611_laser_level_tripod
slug: pictureX_0611_laser_level_tripod

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

A laser level tripod is a rotating laser/instrument head carried on a 3-leg tripod. This rebuild
treats the object as: one shared `frame` host (yellow die-cast crown/hub + a slotted central column
+ sliding spreader collar + head seat), N=3 indexed leg units that each hinge outward from the crown
(spread revolute) and optionally telescope (prismatic), a slotted foot at each leg tip, and one
instrument head that pans on a vertical axis at the crown top and carries a slotted mounting
interface.

Both source records model the tripod as a single rigid `tripod_frame` part (the three legs are
static visuals) plus one articulated `pan_head`. The hinge cheeks / clevis / hinge-pin hardware and
the two-segment telescoping tubes with clamp collars are modeled as real geometry in the sources, so
elevating them to real spread-revolute and telescope-prismatic joints is an honest mechanism
reconstruction of visible hardware (MECHANICAL_PRIORS §4 rotation, §8 multi-joint supports), not a
fabricated mechanism. N is source-anchored at 3 (a tripod); it is not extrapolated.

sync_records:
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964

## Slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| leg_structure | telescoping | two-segment telescoping leg | rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964/rev_000001 | model.py:L93-L201 | accepted | separate `upper_leg_i` (L101-111) + `lower_leg_i` (L113-123) tubes with a molded `leg_clamp_i` / `yellow_latch_i` clamp collar (L137-164) at the overlap — an explicit slide/lock telescope; hinge shoulder at crown (L125-135) |
| leg_structure | fixed | one-piece kneed leg, clevis hinge, no telescope | rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964/rev_000001 | model.py:L114-L189 | accepted | single continuous kneed `leg_tube_i` (L123-127) with a molded `upper_bracket_i` clevis + transverse `hinge_pin_i` (L130-144) and a low `leg_clamp_i`/`clamp_band_i`/`rubber_boot_i` (L145-162); no second sliding segment |
| head | pan_disk | compact disk instrument head, bounded pan | rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964/rev_000001 | model.py:L217-L297 | accepted | `pan_base`+`head_body`+`mounting_plate`+`mounting_stud`+`laser_mount_disk` compact disk housing with side lock screw/knob and long pan handle; joint `frame_to_pan_head` REVOLUTE, z axis, lower/upper = -pi/+pi (L284-297) |
| head | pan_drum | tall graduated-drum head, continuous pan | rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964/rev_000001 | model.py:L242-L335 | accepted | `bearing_foot`+`pan_drum`+`graduated_ring`+`mounting_platform`+`anti_slip_pad`+`mounting_stud`+4 platform screws; taller housing with graduated bearing ring; joint `pan_rotation` CONTINUOUS, z axis, unbounded (L327-335) |
| center_column | plumb_hook | short suspended plumb/elevator column under the crown | rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964/rev_000001 | model.py:L61-L91 | accepted | `center_column` is r=0.013 L=0.720 centred at z=0.625, so it spans 0.265–0.985 under a 1.005 m crown: it **hangs clear of the floor** and terminates in the open, and it carries `cable_clip` (L80-85) + `clip_tether` (L86-91) retention hardware. No ground-contacting column element exists in this record. |
| center_column | plumb_rod | full-length plumb rod down to a rubber ground foot | rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964/rev_000001 | model.py:L77-L106 | accepted | `center_column` is r=0.014 L=1.205 centred at z=0.6825, so it spans 0.080–1.285 under a 1.285 m crown — it runs the **whole** height and lands on a rubber `column_foot` (L95-100, z 0.050–0.080) just clear of the floor; `collar_clamp_screw` (L101-106) + `collar_clamp_tab` (L107-112) lock the collar on the rod. Different part tree (extra ground foot + clamp hardware) and a different column envelope, not a dimension change. |
| head_mount | stud_disk | bare threaded stud on a laser-mount disk | rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964/rev_000001 | model.py:L230-L247 | accepted | `mounting_plate` Box(0.082,0.070,0.014) + `mounting_stud` Cyl(r=0.008,L=0.018) + `laser_mount_disk` Cyl(r=0.015,L=0.010). Three elements, no pad and no fasteners: the instrument screws straight onto the stud. |
| head_mount | qr_platform | screwed quick-release deck with anti-slip pad | rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964/rev_000001 | model.py:L261-L286 | accepted | `mounting_platform` Box(0.088,0.078,0.030) + `anti_slip_pad` Box(0.070,0.054,0.006) + four `platform_screw_*` Cyl(r=0.0032) at (±0.032,±0.027) + `mounting_stud` Cyl(r=0.006,L=0.028). Seven elements including a fastened pad — a different mounting interface, not a resized stud. |
| foot | rubber_pad | tapered rubber shell capped by a spherical pad | rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964/rev_000001 | model.py:L182-L201 | accepted | `rubber_foot_i` is a tapered tube shell (r=0.0165, 0.377→0.402 along the leg) closed by a separate `foot_pad_i` `Sphere(radius=0.018)` — a round pad foot. |
| foot | molded_boot | angled molded box boot under a clamp band | rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964/rev_000001 | model.py:L145-L162 | accepted | `rubber_boot_i` is a molded `Box((0.036,0.048,0.105))` (L158-162) sitting under `leg_clamp_i` Box (L145-150) and `clamp_band_i` Box (L151-156) — a flat-faced boot with a band, no spherical pad anywhere in this record. |

Both records: three legs at azimuths `-pi/2 + 120*i` (rec1 L93, rec2 L114) → N=3, 120 deg apart.
Both records: vertical pan axis at crown top, `axis=(0,0,1)` (rec1 L293, rec2 L333) → head pan is
about world +Z at the head seat.

## Multiplicity, N derivation

- `leg_count` multiplicity, item_slot=`leg_structure`, values = {3}. Both records model exactly three
  legs and the object is definitionally a tripod; 3 is source-anchored and NOT extrapolated to other
  counts. Each N adds one full indexed leg unit (spread revolute; telescope prismatic + lower segment
  for `telescoping`) at azimuth `-pi/2 + 2*pi*i/N`.

## Independent parameters and derivations (continuous — not counted in core/raw)

- `overall_scale` (ratio, 0.90–1.10): uniform proportion scale on the whole tripod.
- `leg_spread_deploy` (rad, 0.10–0.34): neutral outward spread angle of the legs from the source
  near-vertical rest; also the geometric splay used to keep feet grounded at the neutral pose.
- `telescope_travel_scale` (ratio, 0.80–1.15): scales the telescoping prismatic half-range about the
  source overlap (telescoping candidate only).
- `head_scale` (ratio, 0.90–1.15): scales the head housing and its mounting interface.
- palette_style: colorway only (safety-yellow/graphite/silver). Not a structural candidate.

Derived per-leg: leg direction unit `u` from hinge to grounded foot, foot drop = `hinge_z`, leg
reach and length from `overall_scale`; telescope junction at 0.50*L; prismatic origin/axis = leg
junction/`u`; spread revolute origin = hinge point, axis = tangential `(-sin a, cos a, 0)`. Head seat
z derived from crown stack height * overall_scale.

## Category identity and motion (author checks)

- Exactly one `frame`, N=3 leg units, one instrument head. `slot_choices` recorded in meta.
- Every leg spreads via a registered REVOLUTE about a horizontal tangential crown axis; feet are
  grounded (z≈0) at the neutral spread+telescope pose. The three legs occupy disjoint 120 deg sectors
  and cannot intersect one another across the full spread range.
- `telescoping` legs add a real PRISMATIC lower segment sliding along the leg axis; the upper segment
  is an OPEN CHANNEL (two walls + web) so the bore is genuinely empty and the lower tube is gripped
  by ball detents. No overlap allowance is declared anywhere in the template.
- Head pans about vertical crown axis; `pan_disk` is bounded REVOLUTE (±pi), `pan_drum` is CONTINUOUS.
  Head base seats on the crown top (expect_contact). The pan handle sweeps horizontally under rotation.
- Characteristic geometry preserved: yellow crown/hub, central plumb column, sliding spreader collar,
  hinge clevis/pin, telescoping tubes + clamp latch, rubber feet, graduated head housing, pan handle,
  side lock knob, threaded laser mount stud. No box/cylinder placeholders for these.

## Legit captured contacts (real geometry under the 1 mm collision tolerance — NO allow_overlap)

- frame.hinge_boss_i (sphere) ↔ leg hinge ball (sphere) at each crown hinge: the centres differ
  purely in Z so the world-AABB overlap is `_MOUNT` for every leg azimuth.
- frame.spreader_brace_i ↔ leg brace_lug_i (brace terminates at the leg's outer face).
- clamp ball detents ↔ telescoping lower tube (spherical, orientation-invariant AABB).
- head base ↔ frame head_seat (seated bearing, lapped by `_MOUNT`).

## Diversity accounting

core_domain = leg_structure(2) x head(2) x center_column(2) x head_mount(2) x foot(2) = **32**.
raw_domain = 32 (leg_count has the single source-anchored value 3).
All five slots are freely combinable; `TemplateDomain` applies no compatibility gate and all 32
combinations are built and author-checked.

`center_column` and `head_mount` are wholly internal to one part each (the shared `frame` host and
the rotating instrument head respectively), so their seams are intra-part and free
(MECHANICAL_PRIORS §1c); `foot` is emitted onto whichever part carries the leg tip (the one-piece
leg for `fixed`, the sliding lower tube for `telescoping`) and both candidates put their lowest
surface at the identical leg-local offset, so the grounded-neutral-pose invariant is unchanged.

## Rejected decompositions

- Separate "hinge" and "telescope" slots are rejected: the two-segment telescoping leg vs the
  one-piece kneed leg is one coherent leg-structure family per record; splitting them admits
  incoherent half-source legs.
- Head tilt: neither source tilts the head (both articulate pan only). A tilt yoke is not
  source-supported and is intentionally NOT fabricated; pan extremes (bounded ±pi vs continuous)
  supply the head motion diversity. **This rejection stands** — it was re-checked against both
  `model.py` files and neither has a tilt yoke, trunnion or non-vertical joint axis.
- Varying leg count away from 3 is rejected (not a tripod / not source-supported).
- Leg clamp family (rec1 molded clamp collar + yellow latch, L137-164 vs rec2 clamp band + bolt,
  L145-171) was examined as a separate slot and rejected on a *source* ground, not a compatibility
  ground: in rec1 the clamp sits at the telescope overlap (z≈0.35, mid-leg) and exists precisely to
  lock the sliding segment, while in rec2 it sits low on the leg at z≈0.16 immediately above the
  boot. It is not the same component at the same station, so it is not interchangeable hardware; the
  telescope-locking clamp stays inside `leg_structure` and the low band is folded into the
  `molded_boot` foot candidate (`foot__molded_boot__boot_band_i`) where the source puts it.
- Spreader family (rec1 `collar_lock_ring` + curved 3-point braces L74-79/L166-180 vs rec2
  `collar_guard` + `collar_clamp_screw`/`collar_clamp_tab` + straight braces L89-112/L173-189) is
  real source variation, but the clamp hardware that carries it is bolted to the *column*, so it is
  folded into `center_column.plumb_rod` rather than declared as a sixth slot; the collar itself is
  shared frame hardware present in both records.

### Superseded rejections

The first pass declared only `leg_structure` and `head` (core_domain 4) and treated the crown/hub,
central column, head mounting interface and foot as fixed frame/host detail. That is **overturned**
for `center_column`, `head_mount` and `foot`: each differs between the two records in part count and
geometric form (see the slot table above for exact spans), and each changes the part tree of its
host, which VISUAL_DIVERSITY_MODEL §槽位 accepts as a structural candidate. The crown/hub casting
itself was re-examined and is **not** promoted: rec1 stacks `yellow_crown`/`crown_top`/
`center_socket` (L42-59) and rec2 stacks `crown_body`/`crown_top_plate`/`bearing_socket`/`pan_seat`
(L51-74), but the difference is a layer count and radii on the same cylindrical die-cast hub with
the same head-seat interface — a dimensional/decorative difference, so it is deliberately not
padded into a slot.
