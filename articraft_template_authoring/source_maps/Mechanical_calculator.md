# Mechanical calculator — SourceMap

export_category: `Mechanical_calculator`

Note the capital `M`: `Mechanical_calculator` is the on-disk subcategory spelling
(it appears verbatim in `meta["category"]` of origin 002 and in every
`source_image` / `source_identifier` path, e.g.
`pictureX/0611/Mechanical_calculator/001.png`). The lowercase form
`mechanical_calculator` is the one used inside record ids
(`rec_picturex_0611__mechanical_calculator__001__…`,
`rec_0611_mechanical_calculator_var_…`). Both are recorded here because the
records root and the export category disagree on case.

Authoritative records live under `data/records` of the `articraft_data` repo
(`<ARTI_SKILL_ROOT>/articraft_data/data/records`). All spans below are
`revisions/rev_000001/model.py` of the named record.

The category is a **desk-scale hand-driven calculating machine**: a heavy cast
hull carrying a sloped or flat key bed with a matrix of independently sprung
keys, a raised rear register that displays digits on rotating wheels or drums, a
hand drive member (crank / lever / dial) on one hull face, and a small bank of
setting or clearing controls.

Source pool: **19 record dirs — 3 picture origins and 16 forked variants. All 19
were read in full before any candidate was chosen.** The three origins were read
line by line. Each variant is a byte-level fork of one origin, so it was read as
a full unified diff against that parent; every changed line was reviewed and the
unchanged remainder is identical to a file already read line by line. Parentage
was established by diff size, not by name:

| Variant | Parent origin | Changed lines |
|---|---|---|
| `calculator_topology_pinwheel_calculato` | 001 | 83 |
| `calculator_topology_lever_adding_machi` | 001 | 113 |
| `calculator_topology_stepped_drum_calcu` | 002 | 64 |
| `calculator_topology_rotary_dial_calcul` | 002 | 104 |
| `calculator_topology_direct_key_comptom` | 003 | 206 |
| `drive_vertical_pull_lever` | 001 | 79 |
| `drive_front_reciprocating_lever` | 001 | 122 |
| `drive_folding_side_crank` | 002 | 153 |
| `clearing_motion_carriage_reset_lever` | 003 | 126 |
| `clearing_motion_rotating_zeroing_knob` | 003 | 173 |
| `key_matrix_10_key_keypad` | 001 | 143 |
| `key_matrix_50_key_keyboard` | 002 | 134 |
| `key_matrix_90_key_full_keyboard` | 002 | 134 |
| `register_form_enclosed_window_bank` | 003 | 138 |
| `register_form_exposed_pinwheel_bank` | 003 | 147 |
| `register_form_traveling_carriage_regis` | 003 | 93 |

(Second-best parent is 900–1200 changed lines in every case, so parentage is
unambiguous.)

## Frame convention for the rebuild

- **`+Y` is machine rear.** The operator stands at `−Y`. All three origins put
  the key bed at negative Y and the register at positive Y: 001 `FRONT_Y=-0.240`,
  `REAR_Y=0.120` (L20-L21); 002 `DECK_CENTER_Y=-0.025` with the display at
  `y=0.095…0.118` (L30, L177-L206); 003 keyboard bed at `y=-0.095`, register
  tower at `y=0.1925` (L118-L152).
- **`X` is the transverse (left–right) axis and is the crank / counter-drum
  rotation axis.** `axis=(1,0,0)` for `crank_turn` and every counter wheel in 001
  (L394, L502) and 002 (L346, L427) and for `housing_to_crank` in 003 (L396).
  The one exception is 003's **exposed pinwheels**, `axis=(0,1,0)` (L322): they
  are stepped wheels read face-on from the front, not counter drums on a
  transverse shaft. Both axes are legitimate and belong to the register-member
  candidate, not to free choice.
- **`z=0` is the table plane and the underside of the cast hull.** 001's housing
  mesh starts at `z=0.000` (L40-L44) and its rubber feet hang to `z=-0.009`
  (L211-L216); 003's `base_floor` spans `0…0.025` (L88-L93) with feet to
  `z=-0.012` (L237-L244); 002's `base_skirt` spans `0…0.014` (L135-L140).
- Key-press prismatic axes are `(0,0,-1)` **in a deck-tilted joint frame**
  (`rpy=(DECK_PITCH,0,0)`), never world `-Z`, except in 003 where the bed is flat.

sync_records:
  - rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb
  - rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe
  - rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da
  - rec_0611_mechanical_calculator_var_calculator_topology_direct_key_comptom
  - rec_0611_mechanical_calculator_var_calculator_topology_lever_adding_machi
  - rec_0611_mechanical_calculator_var_calculator_topology_pinwheel_calculato
  - rec_0611_mechanical_calculator_var_calculator_topology_rotary_dial_calcul
  - rec_0611_mechanical_calculator_var_calculator_topology_stepped_drum_calcu
  - rec_0611_mechanical_calculator_var_drive_folding_side_crank
  - rec_0611_mechanical_calculator_var_drive_front_reciprocating_lever
  - rec_0611_mechanical_calculator_var_drive_vertical_pull_lever
  - rec_0611_mechanical_calculator_var_clearing_motion_carriage_reset_lever
  - rec_0611_mechanical_calculator_var_clearing_motion_rotating_zeroing_knob
  - rec_0611_mechanical_calculator_var_key_matrix_10_key_keypad
  - rec_0611_mechanical_calculator_var_key_matrix_50_key_keyboard
  - rec_0611_mechanical_calculator_var_key_matrix_90_key_full_keyboard
  - rec_0611_mechanical_calculator_var_register_form_enclosed_window_bank
  - rec_0611_mechanical_calculator_var_register_form_exposed_pinwheel_bank
  - rec_0611_mechanical_calculator_var_register_form_traveling_carriage_regis

---

## The `calculator_topology_*` question, decided first

The five `calculator_topology_*` records are the hard design question, so the
call is made here and the slot table below follows from it.

**Call: `calculator_topology` is NOT a slot at all — neither one structural
family nor five independent slots. The five records each contribute a candidate
to a *different* existing slot, and the one place where independence genuinely
fails (the rotary dial vs. the drive member) is resolved by putting the dial
*inside* the drive slot rather than beside it.**

This is decided from what the diffs actually change, not from the record names:

| Record | What the diff really changes | Part tree / joint graph |
|---|---|---|
| `…_pinwheel_calculato` | `_calculator_housing_mesh` only: the 8-point tapered wedge is replaced by a 20-point CCW plan outline lofted between `z=0` and `_deck_z(y)` with fan-capped top and bottom (L37-L82). Plus one author test (L560-L573). | **identical** |
| `…_lever_adding_machi` | `_calculator_housing_mesh` only: 4 transverse stations `(y, half_width, top_z)` swept into a drafted casting (L37-L86); and `crank_arm` becomes a 6-point lofted plate mesh instead of a Box (L510-L537). | **identical** |
| `…_stepped_drum_calcu` | `_number_wheel()` only: drum OD `0.010 → 0.0082` and nine teeth `rect(0.0030, 0.0042)` extruded `0.0035 + i·0.0015` at `40°` pitch, all `union`-ed into one solid (L54-L82). | **identical** |
| `…_rotary_dial_calcul` | Adds a `_rotary_selector_dial()` CAD disc ⌀0.100 × 0.012 with ten ⌀0.0124 finger holes on a 0.034 bolt circle (L71-L85); mounts it as **two more visuals on the existing `crank` part** (L478-L495) plus a housing backplate / scale ring / ten marks on the same axis (L292-L327). | **identical** |
| `…_direct_key_comptom` | Key cap becomes an 8-ring × 24-segment lathed concave mushroom mesh ⌀0.032 (L61-L118, mounted L299-L344), stem `⌀0.010×0.024 → ⌀0.009×0.030`, travel `0.007 → 0.009`. **And it deletes the entire three-slider selector bank** — 3 parts, 3 prismatic joints, 6 track visuals. | **changes**: −3 parts, −3 joints |

Four of the five are strictly local: a single mesh function, a single CAD
function, or two extra visuals on a part that already exists. Nothing about them
forces a host-topology change, so merging them into one 5-candidate family would
*destroy* legitimate combinations the sources plainly support (a pinwheel hull
with a stepped drum is buildable and historically correct). Per
`VISUAL_DIVERSITY_MODEL.md` "完整组合原则" the merge rule triggers only when a
candidate **must** change the whole host; it does not trigger here.

But they also cannot be five independent slots, because each touches a
*different* subsystem — a five-member "topology" slot would have to be five
one-member slots, which is not a decomposition. So each goes to the slot that
owns the subsystem it edits:

- pinwheel hull, lever-adder hull → **Slot A `housing_form`**
- stepped drum → **Slot B `register_assembly`**
- rotary dial → **Slot C `drive_member`**
- comptometer cap → **Slot D `key_form`**, and its slider deletion → **Slot E
  `setting_control` = `none`**

**The one real independence failure, and how it is fixed.** If the rotary dial
were an independent slot beside `drive_member`, the combination
`rotary_dial × drive_front_reciprocating_lever` would be unbuildable as a local
adaptation. The dial is a ⌀0.100 disc concentric with the drive pivot
(L478-L495, origin `(0.010,0,0)` in the crank frame). `drive_front_reciprocating_lever`
moves that pivot from the right flank `(0.179,-0.030,0.095)` to the **front
wall** at `(0.105,-0.247,0.030)` (L200-L208, L512-L523). A 0.058 m-radius disc
centred 0.030 m above the table would sweep 0.028 m *below* `z=0` and straight
through the key bed; and `drive_vertical_pull_lever` hangs its grip to `z≈0.047`
(L494-L500), which the dial would foul. Relocating the dial is not a shoulder,
transition frame or opening — it is a different machine. Per `AUTHORING.md` §4
and `MECHANICAL_PRIORS.md` §3 that is exactly the merge case, so
`coaxial_rotary_dial` becomes a **candidate of `drive_member`**, sharing the one
bearing-axis interface with the four crank/lever candidates. Every declared
combination then stays buildable with only local host adaptation (which face the
bearing is bored into, and how big the clear disc face on that face must be).

---

## Component slots and candidates

All record paths below are relative to
`data/records/<record>/revisions/rev_000001/model.py`.
Diversity axis: ① skeleton/topology ② joint/mechanism ③ form family.

### Slot A — `housing_form` (root cast hull; ① silhouette + part tree)

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `tapered_wedge` | `…__001__png_3c15e…` | L37-L57 (mesh), L97-L120 + L207-L216 (dress) | ① | 8-vertex closed wedge, `x` half-width 0.145 at the front growing to 0.175 at the rear, deck rising `FRONT_DECK_Z=0.055 → REAR_DECK_Z=0.155` over `y −0.240 → +0.120`. `DECK_PITCH = atan2(0.100, 0.360) = 0.271 rad`. Six quads via `_add_quad`. Dressed with a 0.286 front lip, 0.280 steel trim, blank badge, and four ⌀0.024 rubber feet |
| `rounded_rear_flared` | `…_var_calculator_topology_pinwheel_calculato` | L37-L82 | ① | 20-point CCW plan outline (front apron half-width 0.116 opening to 0.181 register shoulders), lofted bottom→`_deck_z(y)` with a fan-capped centre vertex at `(0,-0.055)` at both ends. 20 side quads + 40 cap triangles. Author test L560-L573 asserts the hull is >0.355 × >0.360 m, i.e. the flare is real |
| `flared_four_station` | `…_var_calculator_topology_lever_adding_machi` | L37-L86 | ① | Four transverse stations `(y, half_width, top_z)`: `(-0.240, 0.150, 0.055)`, `(-0.165, 0.154, …)`, `(0.050, 0.166, …)`, `(0.120, 0.178, 0.155)` — a broad foot, pinched keyboard waist and heavy register shoulder. Sweeps bottom, deck and two drafted side walls per station pair, plus two end caps |
| `cast_side_profile` | `…__002__png_bfb3ab…` | L33-L51 (CAD), L129-L175 (dress) | ① | The only *CadQuery* hull: an 8-point side profile on the `YZ` plane at `x=-0.175` extruded 0.350 in X, then `edges("\|X").fillet(0.007)`. Profile rises `z=0.014` at the front to a 0.153 crest at `y=0.100` then falls to 0.071 — a true cast-machine silhouette. Carries a 0.350×0.340×0.014 `base_skirt` and a two-layer tilted deck (`keyboard_cover` 0.252×0.198×0.012 and `key_plate` 0.222×0.174×0.004, both at `rpy=(DECK_TILT,0,0)`, `DECK_TILT=12.5°`) |
| `open_frame_side_cheek` | `…__003__png_6c29e0…` | L87-L158 | ① | Not a monocoque: a 0.380×0.440×0.025 `base_floor`, two `_wedge_box(0.025, 0.410, 0.055, 0.195)` side cheeks at `x=±0.1775`, a `_wedge_box(0.350, 0.060, 0.055, 0.082)` front fascia, a 0.330×0.190×0.018 keyboard bed, a 0.330×0.140×0.015 mechanism floor, two 0.340×0.020×0.050 shaft rails at `y=0.020/0.170`, and a 0.350×0.055×0.180 register tower. Flat deck (`DECK_PITCH = 0`) |

`_wedge_box` (003 L32-L59) is the reusable primitive: a closed 8-vertex wedge
with its bottom at local `z=0` and its front at local `−Y`, used for both cheeks
and the fascia.

### Slot B — `register_assembly` (bank shell + digit member + carry train, as one family; ①② part tree, joint set and spin axis)

**This slot is a deliberate merge of three subsystems** (`register_bank_form`,
`register_wheel_form`, `carry_mechanism`) — justification in *Domain reduction*
below. Each candidate is one coherent register: the shell, the rotating digit
member, and the carry train that co-vary with it.

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `mullion_counter_bank` | `…__001__png_3c15e…` | L122-L167 (shell), L361-L401 (wheels), L403-L441 (carry) | ①② spin `(1,0,0)`, 9 digits | Open brow/sill frame: 0.276×0.026 sill at `z=0.150`, 0.302×0.060 brow at `z=0.207`, 0.310×0.080×0.066 rear cover, two side posts, **ten mullions** at `[-0.110] + 8 wheel midpoints + [0.110]` each 0.006×0.008×0.044, and nine 0.017×0.002×0.034 translucent panes (α=0.38). Wheels: ⌀0.0035 bearing sphere at `(0,-0.0025,-0.01725)`, ⌀0.032×0.014 drum, ⌀0.014×0.017 hub protruding 1.5 mm each side as a real journal, 0.013×0.005×0.010 digit patch. Carry: eight ⌀0.018×0.007 stepped wheels + ⌀0.012×0.011 hubs + 0.006×0.017×0.004 pawls at the wheel midpoints, `±0.45 rad` |
| `railed_drum_bank` | `…__002__png_bfb3ab…` | L177-L237 (shell), L325-L354 (drums), L387-L414 (carry) | ①② spin `(1,0,0)`, 10 digits | Two 0.236×0.006×0.007 rails at `z=0.151/0.179`, two 0.004 side stiles at `x=±0.118`, one 0.232×0.004×0.030 backing, **nine 0.002×0.006×0.021 dividers** at `(i-4)·0.021`, a ⌀0.0044×0.245 common `wheel_axle`, two 0.016×0.027×0.037 supports at `x=±0.128`, two 0.006 bridges at `x=±0.113`. Drum: `circle(0.010).circle(0.0021).extrude(0.016)` from `z=-0.008` unioned with a `circle(0.0078).circle(0.0021).extrude(0.002)` hub — a stepped annulus with a real through-bore. Carry: **one** part, a 0.210×0.004×0.004 rack bar + 10 pawls, PRISMATIC `(1,0,0)` `±0.003` in two 0.012² guides at `x=±0.111` |
| `stepped_drum_bank` | `…_var_calculator_topology_stepped_drum_calcu` | L54-L82 (drum CAD), L195-L255 (shell), L343-L432 (drums + carry) | ①② spin `(1,0,0)`, 10 digits | Same shell and rack as `railed_drum_bank`; the drum becomes a Leibniz stepped drum — OD `0.010 → 0.0082`, nine teeth `rect(0.0030, 0.0042)` at `center(0, 0.0088)` extruded `0.0035 + i·0.0015` (3.5 → 15.5 mm) and rotated `i·40°`, all `union`-ed into **one solid**. The progressive axial engagement length *is* the mechanism. Test L661-L674 asserts a ≥0.0175 × ≥0.020 × ≥0.020 envelope |
| `bezel_pinwheel_tower` | `…_var_register_form_exposed_pinwheel_bank` | L64-L91 (tower CAD), L198-L254 (readout + carry), L318-L357 (pinwheels) | ①② spin **`(0,1,0)`**, 7 digits | The only face-on register. Tower: `box(0.350,0.055,0.180)` minus seven open bays `box(0.032, d+0.010, 0.112)` at `-0.132 + 0.044·i`, `z=-0.005`, minus a rear relief `box(w-0.024, d-0.010, h-0.030)` at `(0,-0.007,-0.003)` leaving a continuous rear spine — a cast cage, not a perforated block (`tolerance=0.0006, angular_tolerance=0.08`). Readout per wheel: 0.026×0.003×0.030 card, a `BezelGeometry((0.024,0.026),(0.036,0.043),0.004, rounded_rect, corner radii 0.003/0.004)` rotated `rpy=(π/2,0,0)`, a 0.020×0.0015×0.005 smoked pane. Wheel: ⌀0.010×0.130 shaft, ⌀0.035×0.062 core, eight Box teeth at `r=0.018`, depth `0.012 + 0.0025·((i+wheel)%5)` — the per-wheel phase makes the bank read as a set stack. Carry is static: two 0.012×0.018×0.080 uprights at `x=±0.150`, a 0.312×0.014×0.012 brass rack, one bronze pawl per wheel |
| `enclosed_window_bank` | `…_var_register_form_enclosed_window_bank` | L64-L86 (casing CAD), L198-L254 (readout + carry), L318-L357 (wheels) | ①② spin **`(0,1,0)`**, 7 digits | **The only record in the pool that cuts real openings in a shell (§7), so it is this category's §7 reference.** `box(w,d,h)` minus an inner cavity `box(w-0.024, d-0.010, h-0.034)` shifted `+0.003` in Y — wall 0.012 in X, 0.005 in Y, 0.017 in Z — then one `box(0.028, 0.014, 0.034)` cut at each `wheel_x` on the front face at `window_z=0.058` (world `z = 0.130+0.058 = 0.188`, exactly the display-card plane; cut 0.028 wide vs a 0.026 card → 0.001 per side; cut height 0.034 = card height exactly). Meshed at `tolerance=0.0005`. Author tests L528-L545 assert each pane is `expect_within` the casing in `xz` |

### Slot C — `drive_member` (hand drive on one hull face; ② joint axis + mechanism)

| Candidate | Record | Exact span | Joint / axis / limits | Key construction |
|---|---|---|---|---|
| `side_rotary_crank` | `…__003__png_6c29e0…` | L366-L404 (crank), L406-L441 (grip) | `housing_to_crank` REVOLUTE `(1,0,0)` `±π`; `crank_to_grip` REVOLUTE `(1,0,0)` `±π` | ⌀0.016×0.035 shaft, 0.010×0.075×0.012 arm, ⌀0.022×0.008 grip boss; the grip is its **own part** — ⌀0.020×0.055 rubber sleeve, ⌀0.022 ball end, 0.018×0.004×0.004 brass marker. Throw 0.075, effort 15.0. (001 L471-L509 and 002 L416-L456 are the same mechanism at throw 0.050 and 0.152; 002 builds its crank as a 7-point catmull-rom `tube_from_spline_points` r=0.004 and its grip as a `CapsuleGeometry(0.009, 0.032)`) |
| `folding_side_crank` | `…_var_drive_folding_side_crank` | L71-L106 (CAD), L466-L483 (fold joint) | `grip_spin` REVOLUTE **`(0,1,0)`**, **`0 → 84°`** | Welded CAD crank: ⌀0.009×0.036 drive shaft, ⌀0.022×0.012 hub, 0.012×0.014×0.076 arm, ⌀0.018×0.020 fold knuckle and ⌀0.007×0.026 hinge pin at `(0.026, z=0.080)`. **The grip stops being a free-spinning handle and becomes a folding one** — a joint-semantics change, not a shape change. Test L787-L813 requires the folded grip to drop ≥0.025 in Z and ≥0.020 in X |
| `front_reciprocating_lever` | `…_var_drive_front_reciprocating_lever` | L200-L208 (bearing), L474-L523 (member) | `crank_turn` REVOLUTE **`(0,1,0)`**, `±0.48 rad` | Moves the drive to the **front wall**: pivot `(0.105,-0.247,0.030)`, bearing collar `rpy=(π/2,0,0)`. Shaft ⌀0.011×0.026, ⌀0.022×0.012 hub, a 0.012×0.010×0.096 arm rotated `-0.610 rad` about Y, ⌀0.020×0.042 grip at local `(-0.058,-0.040,0.079)`. The host adapts: `front_lip` and `front_trim` are pushed forward and thinned (L106-L118) to clear the sweep. Test L713-L730 requires \|Δx\|>0.045, \|Δz\|>0.015 and both extremes at `y < -0.270` |
| `vertical_pull_lever` | `…_var_drive_vertical_pull_lever` | L197-L205 (bearing), L471-L515 (member) | `lever_pull` REVOLUTE **`(-1,0,0)`**, **`0 → 0.95 rad`** (one-way stroke) | Same pivot as 001 but the member hangs *down*: ⌀0.012×0.025 pivot shaft, ⌀0.022×0.010 hub, a 0.012×0.012×**0.112** arm at local `z=-0.056`, and a ⌀0.024×0.050 grip at local `z=-0.118` whose **axis is Z, not X** — a hand column, not a stub. `crank_bearing` is renamed `vertical_lever_bearing`. Tests L678-L691: grip rests with `z_min<0.055, z_max<0.100`, and the pull carries it ≥0.070 m in `−Y`. One part, one joint — no grip child |
| `coaxial_rotary_dial` | `…_var_calculator_topology_rotary_dial_calcul` | L71-L85 (dial CAD), L292-L327 (host scale), L478-L495 (member) | `crank_turn` REVOLUTE `(1,0,0)`, `±π` | Entry moves onto the drive axis. `circle(0.050).extrude(0.006, both=True)` minus ten `circle(0.0062)` finger holes on a 0.034 bolt circle, mounted on the crank part at local `(0.010,0,0)`, `rpy=(0,π/2,0)`, plus a ⌀0.020×0.014 red hub. The host grows a ⌀0.116×0.003 backplate at `x=0.1765`, a `TorusGeometry(0.052, 0.0018)` scale ring and **ten 0.002×0.008×0.0025 index marks** at `r=0.052`, each rotated `rpy=(dial_angle,0,0)`. Test L550-L580 requires the dial ≥0.095 in Y and Z and <0.014 thick |

### Slot D — `key_form` (the individual key; ③ form family)

| Candidate | Record | Exact span | Visuals/key | Key construction |
|---|---|---|---|---|
| `stepped_box_cap` | `…__002__png_bfb3ab…` | L273-L323 | 3 | 0.006²×0.004 stem, 0.015²×0.009 moulded cap, 0.006×0.004×0.0006 number inset; three-colour column grouping (`column ≤ 2` ivory, `≤ 6` teal, else sage). 001 L218-L265 is the same family with a fourth ⌀0.003 support sphere and a 0.0125² cap |
| `cylindrical_plunger` | `…__003__png_6c29e0…` | L246-L288 | 3 | ⌀0.010×0.024 steel stem, ⌀0.034×0.010 coloured cap, ⌀0.019×0.0015 ivory legend disc. Row 0 green, the last row's corners red. Guided between 0.326×0.004×0.008 brass key-guide strips at `y = -0.1775 + 0.045·row` (L219-L226) |
| `concave_mushroom_cap` | `…_var_calculator_topology_direct_key_comptom` | L61-L118 (mesh), L299-L344 (mount) | 3 | `_direct_key_cap(radius=0.016, height=0.013, segments=24)`: an 8-ring lathed profile `(0,0) → (0.68r,0) → (0.91r,0.18h) → (r,0.42h) → (0.97r,0.68h) → (0.82r,0.88h) → (0.52r,0.82h) → (0,0.78h)` — a broad shoulder with a **concave finger dish** (the last two rings fall back below the rim), ≈336 faces, built **once** and shared across all keys. Stem ⌀0.009×0.030, travel `0.007 → 0.009`. Test L612-L640 requires cap ≥0.031 in X and Y, `0.009 ≤ h ≤ 0.014`, stem ≥0.029 deep |

### Slot E — `setting_control` (the small control bank; ①② part tree / joint type)

| Candidate | Record | Exact span | Joint | Key construction |
|---|---|---|---|---|
| `slider_bank` | `…__003__png_6c29e0…` | L227-L235 (rails), L331-L364 (carriages) | `slider_count` × PRISMATIC `(0,-1,0)`, `0 → 0.028` | **The §6-conformant construction, adopted for all slider counts.** Two rails per slider at `x ± 0.009`, each 0.004×0.060×0.006; the carriage is a genuine 3-piece member (0.014×0.012×0.006 carriage + ⌀0.009×0.022 stem + 0.014×0.010×0.012 grip). `slider_count ∈ {2,3,4}` is a discrete parameter covering 002's flank pair (L239-L246, L356-L385, `±0.006` travel) and 001's four-slider deck lane (L314-L359, `±0.010`), whose seat is derived **along the deck normal** (`y − sin(pitch)·0.00125`, `z + 0.0008 + cos(pitch)·0.00125`, L344-L351) |
| `zeroing_knob` | `…_var_clearing_motion_rotating_zeroing_knob` | L326-L369 | 1 × REVOLUTE **`(0,0,1)`**, `±π` | The pool's **only** vertical-axis joint. `KnobGeometry(0.044, 0.022, body_style="faceted", base 0.040 / top 0.034, edge_radius 0.001, KnobGrip(ribbed, 12, depth 0.0012, width 0.0022), center=False)` seated on the register cover at `(0.145, 0.190, 0.240)`, plus a ⌀0.018×0.003 brass cap and a 0.014×0.003×0.0015 ivory marker. `mechanism_floor` is renamed `mechanism_deck`; author test L563-L568 asserts the rename, L616-L621 the seating at `contact_tol=1e-4` |
| `none` | `…_var_calculator_topology_direct_key_comptom` | L284-L293 (rails deleted), L384 (parts deleted) | none | A true Comptometer has direct-action keys and no setting bank at all: the fork removes 3 parts, 3 prismatic joints and 6 track visuals, and drops the corresponding author tests (L612-L616, L669-L681). Also the configuration of all three `register_form_*` forks and both `clearing_motion_*` forks — **8 of 19 records carry no setting control**, so this is the pool's most common configuration, not an absence |

### Slot F — `key_matrix` (multiplicity N) — see the dedicated section below

## Domain reduction — what was merged, demoted, and why

The first pass declared ten slots at `5·6·5·4·3·3·6·2·2 = 259,200` core
combinations. `TemplateDomain` has no compatibility gates, so every one of those
must build, and preflight builds each candidate against a fixed rest — 41
baseline probes against a 120 s soft budget and a 150 s watchdog. That is not a
usable domain. Six slots at **`5·5·5·3·3 = 1,125`** core combinations and 21
baseline probes is. Every decision below is the `VISUAL_DIVERSITY_MODEL.md` test
applied honestly — *does the candidate change the part tree, the joint set, or
the primary silhouette on its own?* — and nothing already documented is dropped
silently.

**Merged: `register_bank_form` (6) + `register_wheel_form` (4) + `carry_mechanism`
(3) → `register_assembly` (5).**
Individually each of the thirteen candidates passes the VDM test, so this is not
a "they were only decoration" merge — it is the `AUTHORING.md` §4 /
`MECHANICAL_PRIORS.md` §3 merge rule. **The register's spin axis is set by the
wheel candidate, but the bank's window slots, divider planting and readout plane
are derived from that axis.** `exposed_stepped_pinwheel` spins about `(0,1,0)`
and is read face-on through a bezel; `wide_counter_wheel` and the annular drums
spin about `(1,0,0)` and are read edge-on through a slot between mullions. Pairing
a face-on pinwheel with a mullion window row means the window slot runs
perpendicular to the digit face — the shell would have to be re-authored, not
locally adapted, which is exactly the "必须改变整个宿主拓扑" case. The pool
confirms the co-variance: **no record mixes them.** All three origins and all
sixteen forks keep shell, wheel and carry train together as one subsystem.
Declaring them independent would assert `6·4·3 = 72` register combinations of
which the pool attests three.
Nothing is lost: all six shells, all four wheel members and all three carry
trains survive inside the five candidates.

**Demoted to continuous parameters: `wide_overhanging_carriage_tower` and
`traveling_carriage_register`.** The source record builds **no carriage** — no
prismatic joint, no rails, no cavity, only a Box resize
(`0.350×0.055×0.180 @ (0,0.1925,0.130)` → `0.398×0.075×0.120 @ (0,0.2025,0.155)`)
plus the slider deletion. A pure proportion change is not a candidate. The resize
becomes `register_tower_width/depth/height`. The *real* traveling carriage would
have been an extrapolation that reparents all N register wheels from the housing
to a moving carriage — a part-tree change with no source attestation, on the one
axis where the budget is tightest. **Rejected, and the reasoning kept here so the
decision survives.** Its mechanical template, should it ever be built, is 003's
paired-rail slide scaled up (rails along `±X`, prismatic `(1,0,0)`, travel
`wheel_pitch × (digits-1)`, cavity = envelope + 0.001 on every face).

**Demoted to a slot-local discrete parameter: `paper_transport` (2 members).**
`roll_and_carry_bridge` does add 1 part + 1 REVOLUTE, so it is structurally real
— but a two-member `{present, none}` slot doubles the whole cartesian product to
buy one optional dressing assembly that appears in exactly **1 of 19 records**.
It becomes `has_paper_transport ∈ {0,1}`, a discrete parameter of the
`tapered_wedge` housing candidate only (the only lineage that prints). Preflight
covers every choice of a discrete parameter when its candidate is active
(`AUTHORING.md` §5), so coverage is preserved at 1/5 of the probe cost, and it
stays out of `core_domain` where it does not belong.

**Demoted to a slot-local discrete parameter: `function_key_block` (2 members).**
Its six keys are **the same mechanism as the key matrix** — PRISMATIC `(0,0,-1)`
in the deck frame, `0 → 0.005`, differing only in cap size (0.020×0.017×0.008)
and effort (12.0 vs 8.0). No new joint type, no new silhouette: under VDM that is
a parameter, not a candidate. It becomes `function_key_count ∈ {0, 6}` on the
`tapered_wedge` candidate, default 0, and its +6 parts / +6 joints are charged
against the N budget below.

**Collapsed 3 → 1: the three slider banks.** `deck_slider_lane` (001, 4),
`flank_pair_sliders` (002, 2) and `railed_selector_carriages` (003, 3) are all
"count × PRISMATIC slider parts on tracks". They differ in **count**, **placement**
and **rail construction** — and count and placement alone are not candidates
under VDM. The only genuine structural difference is 003's **paired rails plus a
3-piece carriage** against the others' single track plus a 2-piece tab, and per
`MECHANICAL_PRIORS.md` §6 the paired-rail form is the correct one anyway. So one
`slider_bank` candidate adopts 003's construction and `slider_count ∈ {2,3,4}`
plus derived `slider_x_positions` reproduces all three source configurations.

**Rejected entirely: `carriage_reset_lever`.** It adds **no part and no joint**.
It deletes the slider bank (already reachable as `setting_control=none`) and
resizes the crank arm (`0.010×0.075×0.012 → 0.014×0.085×0.018`) and mechanism
floor (`0.140 → 0.118` deep). All of that is already captured by
`crank_arm_width/length/thickness` and `mechanism_floor_depth`. Under VDM it is
not a candidate; the record stays in `sync_records` and in the review ledger.

**Deliberate construction deviation, stated not hidden: per-column carry wheels
become visuals on one rack part.** `mullion_counter_bank` inherits 001's eight
independently articulated carry wheels (8 parts + 8 REVOLUTE joints, L403-L441)
— the single largest non-key part cost in the pool, and 001's own author tests
never check their motion, only their joint limits (L579-L598). The rebuild keeps
all 24 visuals (stepped wheel, hub, pawl per station) and the identical visible
mechanism, but carries them on **one** part with **one** joint, following the
construction 002 already uses for the same function (`shifting_carry_rack`,
L387-L414). Cost: 8 parts / 8 joints → 1 part / 1 joint. This changes *how* the
carry train is emitted, not what it looks like, and it is what buys the N range
below.


---

## Mating mechanisms (sampled across records, not per candidate)

Per `MECHANICAL_PRIORS.md` §1b these were read across *all* 19 records rather
than one per candidate. Every number below is a derivation rule, not a magic
constant.

### 1. Key seating plane — the joint origin **is** the deck top face

| Record | Deck/plate element | Its top face z | Key joint origin z | Key's lowest visual at local z |
|---|---|---|---|---|
| 001 (L221-L265) | housing mesh deck | `_deck_z(y)` | `_deck_z(y)`, `rpy=(DECK_PITCH,0,0)` | `Sphere(0.0015)` centred `0.0015` → bottom **exactly 0** |
| 002 (L157-L169, L305-L323) | `key_plate` 0.004 thick, centred at `surface − 0.002·normal` | `DECK_SURFACE_Z = 0.122` | `DECK_SURFACE_Z + local_y·sin(tilt)` | `Box(…,0.004)` at `z=0.002` → bottom **exactly 0** |
| 003 (L118-L122, L275-L288) | `keyboard_bed` 0.018 at `z=0.072` | `0.081` | `0.081` | `Cylinder(len 0.024)` at `z=0.012` → bottom **exactly 0** |

**RULE:** `key_joint_origin_z = deck_top_face_z` and every key's lowest visual has
its base plane at local `z = 0`. That gives tangent contact with zero gap, which
is what 002 asserts as `expect_contact(elem_a="stem", elem_b="key_plate",
contact_tol=0.0002)` (L580-L595) and 003 as `contact_tol=1e-5` (L590-L595).
Both the key stack *inside* the part and the deck stack inside the housing are
tangent stacks — legal free embedding per §1c — but the key-to-housing plane is a
cross-part contact and must land within the tolerance above.

Within-key tangency (001, L224-L248): sphere `0…0.003`, stem `0.003…0.009`, cap
`0.009…0.013`, legend `0.013…0.0135`. Nothing overlaps and nothing floats.

### 2. Key aperture in the top plate — **absent in every source record, must be added**

| Record | Key travel | Plate thickness at the key | Stem footprint | Aperture in the source |
|---|---|---|---|---|
| 001 | 0.006 (L259-L264) | solid hull deck | 0.0150 × 0.0150 | **none** |
| 002 | 0.004 (L317-L322) | 0.004 `key_plate` | 0.006 × 0.006 | **none** |
| 003 | 0.007 (L282-L287) | 0.018 `keyboard_bed` | ⌀0.010 | **none** |
| comptometer fork | **0.009** (L336-L341) | 0.018 | ⌀0.009 | **none** |

At full press every source key sinks its stem into a solid plate. Static poses
look fine, which is exactly the failure mode `MECHANICAL_PRIORS.md` §1 and §7
warn about; motion QC exercises the `upper` bound of every bounded prismatic
joint and will find it.

**RULE for the rebuild:** cut a real aperture per key at the joint origin,
`aperture_side = stem_side + 2 × 0.0005` (002: 0.006 → 0.007 square) or
`aperture_d = stem_d + 0.001` (003: 0.010 → 0.011), depth ≥ `key_travel`, sized
from the moving member's envelope and never from a fixed magic number. Cutting
the whole matrix into the plate as one CAD operation keeps the plate at one
visual (see the collision-budget section).

### 3. Key pitch, cap size, neighbour clearance

| Record | pitch X | pitch Y | cap footprint | min neighbour gap | cap / min-pitch |
|---|---|---|---|---|---|
| 001 (L219-L220, L237-L242) | 0.021 | 0.0225 | 0.0125 × 0.0125 | 0.0085 | 0.60 |
| 002 (L273-L297) | 0.020 | 0.020 | 0.015 × 0.015 | **0.005** | 0.75 |
| 003 (L247-L268) | 0.055 | 0.045 | ⌀0.034 | 0.011 | 0.62 |
| comptometer fork | 0.055 | 0.045 | ⌀0.032 | 0.013 | 0.58 |
| 10-key fork (L249-L258) | 0.050 | 0.043 | 0.028 × 0.026 | 0.017 | 0.56 |
| 90-key fork (L298-L299) | 0.020 | **0.0185** | 0.015 × 0.015 | **0.0035** | 0.81 |

**RULE:** `cap ≤ 0.75 × min(pitch_x, pitch_y)`, keeping ≥0.005 m between
neighbouring caps. The 90-key fork is the tightest case in the pool at 0.0035 m
and sets the practical floor.

### 4. Crank axle radius vs. case bore — the pool's two `allow_overlap` causes

| Record | Bearing element | Bore radius | Shaft radius | Axial relation | Result |
|---|---|---|---|---|---|
| 001 (L197-L205, L472-L480) | solid `Cylinder(0.012, 0.014)` at `x 0.143…0.157` | none (solid boss) | 0.006 | shaft local `x0 = 0` → world 0.157 = **bearing outer face** | butt contact, clean |
| 002 (L257-L271, L416-L421) | `TorusGeometry(radius=0.008, tube=0.004)` → hole radius **0.004** | 0.004 | 0.004 (tube) | passes through | exact tangent; `expect_overlap(axes="x", min 0.004)` L660-L668, clean |
| 003 (L99-L105, L366-L375) | `side_cheek` outer face at `x = 0.1775 + 0.0125 = 0.190` | none | 0.008 | shaft local `x0 = 0` → world 0.190 = **cheek outer face** | `expect_contact(1e-5)` L602-L607, clean |
| folding fork (L73-L77) | same torus hole 0.004 | 0.004 | **0.0045** | 0.0005 **interference** | `allow_overlap` L689-L698 |
| front-lever fork (L200-L208, L476-L484) | solid `Cylinder(0.013, 0.014)` | none (solid boss) | 0.0055 | shaft buried 0.007 into solid metal | `allow_overlap` L686-L695 |

**RULE:** the bearing must be an **annulus** with `bore_r = shaft_r + 0.0005…0.001`,
and the shaft's inner end plane must coincide with the bearing / hull face
(`shaft local x0 = 0`, length = the outboard standoff). Both `allow_overlap`
sites in the pool disappear under this rule with no change to the visible form.

### 5. Crank handle offset (throw) and the sweep envelope

| Record | Pivot (world) | Arm | Throw | Grip |
|---|---|---|---|---|
| 001 (L481-L509) | `(0.157, 0.176, 0.190)` — behind `REAR_Y=0.120` and above `REAR_DECK_Z=0.155` | Box 0.008×0.055×0.010 at local `(0.027,0.022,0)` | **0.050** | ⌀0.018×0.026 at local `(0.044,0.050,0)`, axis X |
| 002 (L71-L91, L443-L456) | `(0.179, -0.030, 0.095)` — right flank at mid-height | spline tube, 7 control points | **0.152** (`√(0.036² + 0.148²)`) | `CapsuleGeometry(0.009, 0.032)`, own part, own REVOLUTE |
| 003 (L376-L404, L428-L441) | `(0.190, 0.105, 0.135)` — exactly on the side-cheek outer face | Box 0.010×0.075×0.012 at local `(0.038,-0.0375,0)` | **0.075** | ⌀0.020×0.055 sleeve + ⌀0.022 ball, own part |
| folding fork (L88-L100) | same as 002 | Box 0.012×0.014×0.076 | **0.080** (knuckle at local `z=0.080`) | folds `0 → 84°` about `(0,1,0)` |
| front-lever fork (L493-L510) | `(0.105, -0.247, 0.030)` — front wall | Box 0.012×0.010×0.096, `rpy=(0,-0.610,0)` | ≈0.098 | ⌀0.020×0.042 at local `(-0.058,-0.040,0.079)` |
| pull-lever fork (L490-L500) | `(0.157, 0.176, 0.190)` | Box 0.012×0.012×**0.112** hanging down | 0.112 | ⌀0.024×0.050, **axis Z** (hand column, not a stub) |

**RULE:** the drive pivot always sits **on** a hull face (never inset, never
floating), the grip stub axis is parallel to the pivot axis for crank candidates
and perpendicular for the pull lever, and the member's entire swept circle
`throw + grip_radius` must lie outside the hull footprint. 001 satisfies this by
placing the pivot 0.056 m behind the rear wall; 003 by placing it exactly on the
cheek face so the whole 0.075 circle is outboard of `x = 0.190`. Throw range
0.050–0.152 m; grip radius 0.009–0.012 m; grip length 0.026–0.055 m.

### 6. Register drum / wheel axial clearance in its window bank

| Record | Wheel pitch | Drum axial length | Inter-wheel gap | Divider width | Clearance per side |
|---|---|---|---|---|---|
| 001 (L149-L167, L362-L387) | 0.022 | 0.014 | 0.008 | 0.006 (at the midpoints, L150-L153) | **0.001** |
| 002 (L207-L214, L325-L340) | 0.021 | 0.016 + 0.002 hub = 0.018 | 0.003 | 0.002 | **0.0005** |
| 003 (L172-L194, L291-L315) | 0.044 | 0.062 **along Y** (front-to-back axis) | — | — | rim-to-rim: tooth envelope `r = 0.018 + 0.003 = 0.021`, `2r = 0.042` vs pitch 0.044 → **0.001 per side** |

**RULE:** `divider_width = wheel_pitch − drum_axial_length − 2 × 0.0005`, dividers
planted at the wheel midpoints. For the face-on pinwheel bank the equivalent is
`tooth_envelope_diameter ≤ wheel_pitch − 0.002`.

**Reading clearance (001, L164, L382-L387):** glass pane 0.017 wide vs drum
0.014 → 0.0015 lateral each side; `digit_patch` front face at `y = 0.105 − 0.014
− 0.0025 = 0.0885` vs glass rear at `0.088` → **0.0005 m** of air between the
printed digit and the pane. 003 stacks the same idea in 1.5 mm steps:
`display_card` at `y=0.1645`, glass at `0.1640`, bezel at `0.163`.

**Drum bore vs common axle (002, L54-L61 vs L215-L223):** drum bore `r = 0.0021`,
`wheel_axle` `r = 0.0022` → **−0.0001 m interference**, which is the direct cause
of the ten `allow_overlap` calls at L599-L608. **RULE:** `drum_bore_r = axle_r +
0.0003…0.0005`, never `≤ axle_r`.

**Tower stand-off (the one number the register forks assert):** exposed-pinwheel
fork L565-L573 requires `expect_gap(register_tower, wheel_shaft, axis="y",
0.004…0.006)`. In 003 geometry the tower front face is at `y = 0.1925 − 0.0275 =
0.165` and the ⌀0.010 × 0.130 wheel shaft (about `y = 0.095`) ends at `0.160` →
**0.005 m**. **RULE:** `tower_front_y = wheel_shaft_far_end + 0.005`.

### 7. Linear slides — rails, spacing, travel and the cavity that receives them (§6)

| Record | Rails | Clear span | Carriage | Travel | Rail length | Joint origin z |
|---|---|---|---|---|---|---|
| 001 (L314-L359) | one 0.020×0.039×0.0025 slot **visual** | 0.020 | 0.016×0.014×0.008 tab | ±0.010 | 0.039 | slot top face, reached via `(0.111, y − sin(pitch)·0.00125, _deck_z(y) + 0.0008 + cos(pitch)·0.00125)` — the seat is **derived along the deck normal**, not authored |
| 002 (L239-L246, L372-L385) | one 0.024×0.042×0.006 track at `z 0.151…0.157` | 0.024 | 0.016×0.012×0.008 thumb piece | ±0.006 | 0.042 | 0.157 = track top face |
| 003 (L227-L235, L351-L364) | **two** 0.004×0.060×0.006 rails at `x ± 0.009` | **0.014** (rail inner faces at ±0.007) | 0.014 wide carriage → **zero side clearance, tangent** | 0 → 0.028 | 0.060 | 0.081 = keyboard-bed top face |

003 is the only construction that satisfies §6 ("滑移接口位于抽屉左右两侧的导轨/滑块").
**RULE for the rebuild:** `rail_clear_span = carriage_width + 2 × 0.0005` (003's
exact-fit 0.014 is a zero-distance contact and will read as a collision — open it
to 0.015); `rail_length ≥ travel + carriage_depth + 0.020`; the prismatic axis is
expressed in the deck-tilted joint frame, not in world coordinates; and the host
must actually contain a cavity or channel of that span, not just two surface
strips.

For the extrapolated `traveling_carriage_register` candidate the same rule scales
up: rails along `±X` at the carriage's left and right edges, prismatic axis
`(1,0,0)`, travel = `wheel_pitch × (digits − 1)` (one digit shift per step,
i.e. 0.044 × 6 = 0.264 m at 003's pitch — clamp to something the 0.398 m tower
can contain, e.g. ±0.044), and a real cut cavity in the tower of
`carriage_envelope + 0.001` on every face.

### 8. Lever and knob pivot heights, and the plane-mount extent (§2)

- **Drive pivot heights are derived from the hull face they sit on, never
  authored twice.** 001 `(z=0.190)` = `REAR_DECK_Z 0.155` + the 0.035 rear-cover
  rise; 002 `(z=0.095)` = mid-height of the 0.014…0.153 side profile; 003
  `(z=0.135)` = mid-height of the 0.055…0.195 side cheek; the front-lever fork
  `(z=0.030)` = mid-height of the 0.055-high front fascia. **RULE:** the pivot is
  at the local mid-height of the face it is bored into.
- **Zeroing knob (L326-L369, `clearing_motion_rotating_zeroing_knob`).** Joint
  origin `(0.145, 0.190, 0.240)`, axis `(0,0,1)`. `tower_cover` is
  `Box(0.350, 0.060, 0.030)` at `(0, 0.190, 0.225)` → its top face is **exactly
  0.240**. `KnobGeometry(..., center=False)` puts the knob base at local `z = 0`,
  so the seat is a tangent contact, asserted `expect_contact(contact_tol=1e-4)`
  at L616-L621.
  **This is the `PlaneInterface.extent` case.** The knob is ⌀0.044 at `x = 0.145`
  on a cover that only reaches `x = 0.175` → nearest edge margin
  `0.175 − 0.145 − 0.022 = 0.008 m`. A wider knob, a narrower tower or a more
  outboard `x` and the knob half-overhangs. The rebuild must publish the cover's
  real bearing rectangle as `PlaneInterface.extent` and let `mate_planes` reject
  the overhang, rather than trusting the hull AABB.

### 9. Effort / velocity / scale envelope across the pool

Key presses: effort 3.0–8.0, velocity 0.09–0.10, travel 0.004–0.009 m.
Function keys: effort 12.0. Sliders: effort 4.0–10.0, velocity 0.08.
Carry rack: effort 8.0, velocity 0.05. Counter wheels: effort 0.6–2.0, velocity
6.0–8.0. Cranks: effort 15.0–25.0, velocity 3.0–5.0; the two hand levers raise it
to **35.0** with velocity 1.8–2.5. Grips: effort 0.4–1.5.
Hull footprints: 0.350–0.398 m wide, 0.340–0.440 m deep, 0.180–0.272 m tall.
There is no small or large outlier in the pool — every record is a desk machine.

---

## Multiplicity (N) — the `key_matrix` slot

Three records sample N directly: **10** (`key_matrix_10_key_keypad`, fork of 001),
**50** (`key_matrix_50_key_keyboard`, fork of 002) and **90**
(`key_matrix_90_key_full_keyboard`, fork of 002). The origins add **81** (001,
9 × 9), **80** (002, 8 × 10) and **20** (003, 4 × 5).

### The exact index-general rule (preserved in full, correct for any N)

Both 002-lineage forks converge on the *same* code (50-key L296-L329; 90-key
L296-L331), which is the rule to implement. It is recorded here in full
regardless of where the declared domain is capped:

```
KEY_COLUMNS = 10                       # constant in 002, 50-key and 90-key
KEY_ROWS    = ceil(N / KEY_COLUMNS)
row, column = divmod(key_index, KEY_COLUMNS)          # flat index, not nested loops
local_x = (column - (KEY_COLUMNS - 1) / 2) * pitch_x
local_y = (row    - (KEY_ROWS    - 1) / 2) * pitch_y  # matrix centred on the deck
world_y = DECK_CENTER_Y  + local_y * cos(DECK_TILT)
world_z = DECK_SURFACE_Z + local_y * sin(DECK_TILT)
joint origin = Origin(xyz=(local_x, world_y, world_z), rpy=(DECK_TILT, 0, 0))
axis         = (0, 0, -1);  limits 0 -> key_travel
part  name   = f"key_{row}_{column}"
joint name   = f"key_{row}_{column}_press"
parent       = housing                 # flat, never chained key-to-key
```

- **Pitch in X:** `0.020` in 002, the 50-key fork and the 90-key fork alike —
  constant, never re-derived.
- **Pitch in Y:** `0.020` at N=50/80, **`0.0185` at N=90** (L299). The reason is
  visible in the diffs: the 50-key fork shrinks the *deck* to fit the matrix, the
  90-key fork shrinks the *pitch* to fit the deck.
  - 50-key (L165-L191): `keyboard_cover` `0.252×0.198 → 0.252×0.138`,
    `key_plate` `0.222×0.174 → 0.222×0.114`. That is exactly
    `cover_depth = KEY_ROWS · pitch_y + 0.038` and
    `plate_depth = KEY_ROWS · pitch_y + 0.014` (8 rows → 0.198/0.174 ✓;
    5 rows → 0.138/0.114 ✓).
  - 90-key: the deck is **untouched** (still 0.198/0.174) and `pitch_y` drops
    instead, because 9 rows at 0.020 would span `8 × 0.020 + cap 0.015 = 0.175 >
    0.174` — a 1 mm overflow. At 0.0185 the span is `8 × 0.0185 + 0.015 = 0.163`,
    inside the plate with 0.0055 m of margin per side.
  - **Unified rule:** derive the plate from the matrix, then clamp the pitch —
    `plate_depth = KEY_ROWS · pitch_y + 0.014` with
    `pitch_y = min(0.020, (plate_depth_max − cap_y − 2 × 0.005) / (KEY_ROWS − 1))`.
    Both source endpoints are reproduced exactly.
- **First-key inset from the case edge** (002 lineage): the field spans
  `9 × 0.020 + cap 0.015 = 0.195` in X; `key_plate` is 0.222 → **0.0135 per
  side**; `keyboard_cover` is 0.252 → **0.0285 per side**; the hull is 0.350 →
  0.0775 per side. In Y the plate margin is `(plate_depth − field_span) / 2`,
  0.0055 at N=90 and 0.007 at N=50/80.
- **Ragged last row** (a stated generalisation, since no source record has one):
  when `N` is not a multiple of `KEY_COLUMNS`, the last row is centred on its own
  occupancy — `local_x = (column − (row_occupancy − 1)/2) · pitch_x` — instead of
  on `KEY_COLUMNS`. Every source sample is exact (10, 20, 50, 80, 81, 90) so this
  changes nothing the pool attests, and it keeps the field visually centred.
- **Naming:** `key_{row}_{column}` / `key_{row}_{column}_press` in the 002
  lineage; 001 uses joint `key_press_{row}_{column}`; 003 uses
  `housing_to_key_{row}_{column}`. The rebuild uses
  `key_matrix__<candidate>__key_{row}_{column}` per `AUTHORING.md` §6.
- **Parenting:** every key parents directly to the housing/frame part in all six
  N samples. There is no key-to-key chaining and no intermediate key-bed part.

### The small-N layout exception

The 10-key fork (L247-L282, helper L76-L101) does **not** use the 10-column rule.
It builds `1…9` as a 3 × 3 field plus a zero centred below:
`row = i//3, column = i%3` for `i < 9`, then `row = 3, column = 1` for the zero;
`x = -0.050 + column · 0.050`, `y = -0.178 + row · 0.043`. The keys are also
**physically larger** — cap `0.028 × 0.026 × 0.006` against 002's `0.015²`. That
is the historically correct ten-key pad, so the rebuild selects the layout by N:

- `N ≤ 12` → **keypad mode**: 3 columns, `pitch = (0.050, 0.043)`, cap
  `0.028 × 0.026`, remainder centred on the last row.
- `N > 12` → **matrix mode**: 10 columns for the 001/002 lineages, 5 columns at
  pitch `0.055 × 0.045` for the 003 lineage, pitch and cap per the rule above.

### Measured basis for the N cap

The first pass declared N ∈ [10, 90] on the strength of the source alone. That
was wrong, and the measurement says so. Two things were measured before choosing
a cap.

**1. What part/joint scale this fleet actually sustains.** Parsing the 452 cached
preflight reports under `.cache/template_check/*/preflight/*.json` for emitted
`parts` / `joints` counts (22 templates report them):

| Measure | Value | Template |
|---|---|---|
| **Largest shipped template, parts** | **33** | `shelving_unit_with_adjustable_shelves` |
| Largest shipped template, joints | 32 | `shelving_unit_with_adjustable_shelves` |
| 2nd largest | 25 / 24 | `pictureX_0611_flexible_track_lighting_system` |
| 3rd largest | 19 / 18 | `pictureX_0611_folders` |
| p90 across the fleet | 19 parts | — |
| Median across the fleet | 8.5 parts | — |

Nothing in this fleet has ever shipped above **33 parts / 32 joints**.

**2. What the preflight budget actually costs.** From the same artifacts,
`elapsed_s` and `builds`:

| Template | parts | probe builds | preflight elapsed |
|---|---|---|---|
| `wrench_set` | 12 | — | **128.5 s** |
| `makeup` | 10 | 58 | 120.7 s |
| `lighthouse_with_rotating_beacon_assembly` | — | 78 | 94.8 s |
| `studio_lamp` | 14 | **103** | — |
| `shelving_unit_with_adjustable_shelves` | 33 | 54 | — |

`wrench_set` at **12 parts already burns 128.5 s**, over the 120 s soft budget
and inside the 150 s watchdog. The binding cost is not part count alone but
`builds × per-build cost`, and the largest probe counts observed are ~103.

**3. The conclusion.** The first pass projected 106–120 parts and 336–494 exact
collision solids at N=90 — **3.2 to 3.6× larger than anything this fleet has ever
built**, with ~200–240 mandatory motion-QC poses (every bounded prismatic gets
`lower` and `upper`). That is not a tight fit; it is off the measured scale
entirely, and corner would not run.

### Host cost after the domain reduction

| Component | Parts | Joints |
|---|---|---|
| housing (any `housing_form`) | 1 | 0 |
| `register_assembly = mullion_counter_bank` | 9 wheels + 1 carry rack = **10** | 10 |
| `register_assembly = railed_drum_bank` / `stepped_drum_bank` | 10 drums + 1 rack = **11** | 11 |
| `register_assembly = bezel_pinwheel_tower` / `enclosed_window_bank` | 7 wheels + 0 = **7** | 7 |
| `drive_member` = crank candidates | 2 (crank + grip) | 2 |
| `drive_member` = lever / dial candidates | 1 | 1 |
| `setting_control = slider_bank` | 2–4 | 2–4 |
| `setting_control = zeroing_knob` | 1 | 1 |
| `setting_control = none` | 0 | 0 |
| `has_paper_transport = 1` | +1 | +1 |
| `function_key_count = 6` | +6 | +6 |

- **Worst host** = `1 + 11 + 2 + 4 = 18` parts (`railed_drum_bank` + crank & grip
  + 4 sliders), or **25** with both optional dressings on.
- **Best host** = `1 + 7 + 1 + 0 = 9` parts.

### Declared range: **N ∈ [10, 16]** — capped, and said plainly

- **Upper bound 16** is chosen so the worst host plus the matrix lands at
  `18 + 16 = 34` parts / 33 joints, i.e. **at the measured fleet ceiling of
  33/32**, not past it. The two optional dressings (`has_paper_transport`,
  `function_key_count = 6`) are therefore restricted to `N ≤ 9`… which is below
  the lower bound, so in practice **they are mutually exclusive with the upper
  half of the N range**, enforced by a derived constraint in `resolve_config`
  rather than by removing a combination (`AUTHORING.md` §6 forbids the latter):
  `function_key_count = 6` and `has_paper_transport = 1` are only permitted while
  `N + host_parts ≤ 33`.
- **Lower bound 10** is the smallest sample in the pool and a real machine — a
  ten-key adding pad. Below 10 there is no source and no complete digit set.
- Best case is `9 + 10 = 19` parts, exactly the fleet p90; worst case is 34,
  exactly the fleet maximum. The whole declared range sits inside measured,
  demonstrated territory.

**What this gives up, stated plainly.** The source's **20-, 50-, 80-, 81- and
90-key records are outside the declared domain.** Five of the six N samples in
the pool cannot be reproduced at full count. The rebuild is a mechanically
faithful calculator whose key field is smaller than four of the six sources.
That is a real loss of source fidelity and it is accepted deliberately, because
the alternative — an aspirational N=90 that makes `corner` unrunnable — is worse.
The index-general rule above is preserved verbatim and is correct for any N, so
raising the cap later is a one-line domain change once the fleet demonstrates it
can carry 100+ parts.

**No faking.** The cap is a cap. Every key in the declared range is a real,
independently articulated part with its own PRISMATIC joint and its own aperture
in the deck. Nothing is welded into the deck to inflate an apparent count, and no
token subset is articulated in front of a static painted-on remainder.

### Implied counts across the declared range

`sdk/_core/v0/exact_collisions.py` `_generate_part_collisions` (L94-L104) loops
`for visual in part.visuals` and derives one collision solid per visual, 1:1 — so
the visual count *is* the collision-solid count. With each key welded into one
solid (§1c makes intra-part embedding free; the `stepped_drum_bank` candidate
already demonstrates the technique by unioning eleven features into one visual,
L54-L82) and each register wheel likewise:

| N | Worst host (18 p) parts / joints / collisions | Best host (9 p) parts / joints / collisions |
|---|---|---|
| 10 | 28 / 27 / ~62 | 19 / 18 / ~44 |
| 13 | 31 / 30 / ~65 | 22 / 21 / ~47 |
| **16** | **34 / 33 / ~68** | 25 / 24 / ~50 |

Mandatory motion-QC poses at N=16, worst host: 16 key bounds × 2 + 10 wheel
revolutes × 2 + 4 slider bounds × 2 + crank/grip continuous ≈ **66** — comparable
to `shelving_unit_with_adjustable_shelves`, which the fleet already runs.

Without the welding deviation the same worst case would emit ~120 collision
solids; the deviation is what keeps the model inside a demonstrated envelope, and
it is recorded in *Domain reduction* rather than applied silently.


---

## Every `ctx.allow_overlap(...)` site in the pool

Preflight **blocks `allow_overlap` for Design-backed templates**
(`AUTHORING.md` §5), including calls made through helpers or aliases, and it
re-checks the emitted allowances in the author-test report.
`ctx.allow_isolated_part(...)` is **not** blocked and remains available.
Seven of the 19 records emit allowances; none appear in 001 or 003.

| Record | Line | Pair / elements | Real cause | How to express it without an allowance |
|---|---|---|---|---|
| `…__002__…` | L599-L608 (× `WHEEL_COUNT`, i.e. 10 sites) | `wheel_i.number_drum` ↔ `housing.wheel_axle` | drum bore `r=0.0021` < axle `r=0.0022` — a 0.1 mm interference fit | **Open the bore**: `bore_r = axle_r + 0.0004 = 0.0026`. Tangency then comes from a short journal shoulder, and `expect_contact(contact_tol=0.0002)` (already present at L627-L634) still passes |
| `…__002__…` | L669-L677 | `grip.handgrip` ↔ `crank.crank_tube` | the ⌀0.018 capsule's near cap at local `x=0.0114` swallows the ⌀0.008 tube end at `x=0` | Give the crank a real ⌀0.007 end **pin** and the grip a matching bore with 0.0005 radial clearance, with a thin shoulder washer providing the tangent face contact |
| `…_topology_stepped_drum_calcu` | L624, L727 | inherited from 002 | same two causes | same two fixes |
| `…_topology_rotary_dial_calcul` | L701, L771 | inherited from 002 | same | same |
| `…_key_matrix_50_key_keyboard` | L625, L695 | inherited from 002 | same | same |
| `…_key_matrix_90_key_full_keyboard` | L633, L703 | inherited from 002 | same | same |
| `…_drive_folding_side_crank` | L628, L708 | inherited from 002 | same | same |
| `…_drive_folding_side_crank` | **L689-L698** | `crank.crank_tube` ↔ `housing.crank_bearing` | drive journal `r=0.0045` vs torus hole `r=0.004` — 0.5 mm interference | `bore_r = shaft_r + 0.0005 = 0.005` (raise `TorusGeometry.tube` from 0.004 to 0.0035 at the same 0.008 mean radius, or raise the mean radius) |
| `…_drive_front_reciprocating_lever` | **L686-L695** | `crank.crank_shaft` ↔ `frame.crank_bearing` | the ⌀0.011 shaft is buried 0.007 m inside a **solid** ⌀0.026 boss | Make the bearing an annular collar with a ⌀0.012 through-bore. The existing `expect_within(axes="xz")` and `expect_overlap(axes="y", min 0.006)` (L696-L712) still express the capture |

Where the source genuinely needed a *merged* solution rather than a clearance —
e.g. the 001 hull's front lip and trim, or 003's bezel/card/glass stack — those
are already **multiple visuals on one part** and cost nothing (§1c). None of the
nine allowance sites is of that kind; all nine are cross-part fits that a
0.3–1.0 mm bore correction removes.

---

## Folded into continuous parameters rather than candidates

Per `VISUAL_DIVERSITY_MODEL.md`, pure proportion changes are not candidates.

| Parameter | Unit | Source range | Evidence |
|---|---|---|---|
| `deck_tilt` | rad | **0.0 – 0.271** | 003 flat bed (L280, no `rpy`); 002 `DECK_TILT = 12.5° = 0.218` (L28); 001 `DECK_PITCH = atan2(0.100, 0.360) = 0.271` (L24) |
| `key_travel` | m | **0.004 – 0.009** | 002 L321, 001 L261, 003 L286, comptometer fork L339 |
| `register_tower_width` | m | 0.350 – 0.398 | 003 L148 vs traveling-carriage fork L149 |
| `register_tower_depth` | m | 0.055 – 0.075 | same |
| `register_tower_height` | m | 0.120 – 0.180 | same |
| `mechanism_floor_depth` | m | 0.118 – 0.140 | 003 L130 vs carriage-reset fork L131 |
| `crank_arm_width/length/thickness` | m | 0.010–0.014 / 0.075–0.085 / 0.012–0.018 | 003 L377 vs carriage-reset fork L333 |
| `crank_throw` | m | 0.050 – 0.152 | 001 L483, 003 L378, 002 L79 |
| `wheel_pitch` | m | 0.021 – 0.044 | 002 L327, 001 L149, 003 L172 |
| `key_pitch_y` | m | 0.0185 – 0.045 | 90-key fork L299 … 003 L248 |
| `hull_width / hull_depth` | m | 0.350–0.398 / 0.340–0.440 | 002 L136, 003 L89, pinwheel fork L42-L61 |

The `lever_adding_machine` crank arm (a 6-point lofted plate mesh, L510-L537) is
*not* folded away — it changes the arm from a Box to a shaped casting, i.e. a
form-family change, and it belongs to the `side_rotary_crank` candidate as an
alternate arm profile driven by the same three continuous parameters.

---

## Category anchors (machine-checkable)

1. **Exactly one root part**, the cast hull (`frame` in 001, `housing` in 002/003),
   and `len(articulations) == len(parts) - 1`. All three origins assert this
   themselves (001 L517-L530, 002 L512-L524, 003 L450-L463). Every other part is
   a direct child of the hull; the only legal two-level chain in the pool is
   `hull → crank → grip` (002 L443-L456, 003 L428-L441).
2. **`10 ≤ N ≤ 16` key parts, each with its own `PRISMATIC` joint** whose axis is
   `(0,0,-1)` in the joint frame, whose `lower == 0.0` and whose
   `0.004 ≤ upper ≤ 0.009`, all parented directly to the hull. The axis, the
   zero lower bound and the flat parenting are invariant across all six source
   N samples; the range is the capped domain.
3. **A register bank of ≥ 5 wheel/drum parts, each with its own `REVOLUTE` joint**
   on a *common* axis — `(1,0,0)` for counter drums, `(0,1,0)` for face-on
   pinwheels — with `lower = -π, upper = +π`, evenly pitched in X, all parented to
   the hull. The bank's window slots, dividers and readout plane must be derived
   from that spin axis, which is why bank and wheel are one candidate.
4. **Exactly one drive member part** with a `REVOLUTE` joint whose origin lies on
   a hull face and whose axis is that face's outward normal
   (`(1,0,0)` for the flank, `(0,1,0)` for the front wall). Its `effort` is the
   largest in the model (15.0–35.0). A second `REVOLUTE` grip child is optional
   but, when present, its origin equals the crank's handle point exactly.
5. **Real bores, no interference.** Every rotating member that runs on a shaft
   must have `bore_r ≥ shaft_r + 0.0003`, and **no `allow_overlap` may be emitted
   anywhere** in the model.
6. **Real key apertures.** For each key, the deck/plate carries a cut opening at
   the joint origin at least `stem_size + 0.001` across and at least `key_travel`
   deep, so that the `upper` pose does not drive the stem into solid material.
7. **Key seating.** The representative key's lowest visual contacts the deck's top
   face within `1e-4 m` at the rest pose (`expect_contact`, as in 002 L580-L595
   and 003 L590-L595), and the pressed pose moves the key down by at least
   `key_travel − 0.001`.
8. **Register capture.** Each wheel is `expect_within` the register bank in the
   two axes normal to its spin axis with `margin ≥ 0.001` (001 L603-L618, 002
   L609-L617, 003 L622-L628), and the tower's front face stands `0.004…0.006 m`
   clear of the wheel shaft.
9. **The drive sweeps clear.** At `±π/2` the grip's world position must move by
   more than `0.7 × crank_throw` and the member's swept envelope must not
   intersect the hull — asserted in every origin (001 L667-L678, 002 L725-L745,
   003 L656-L667).
10. **At most one vertical-axis joint.** `(0,0,1)` appears exactly once in the
    pool, on `rotating_zeroing_knob` (L358-L368). Any other `(0,0,1)` joint is a
    modelling error for this category.

---

## Review ledger — one line per record, read before judged

| # | Record | Verdict |
|---|---|---|
| 1 | `…__001__png_3c15e16013b5410bb59e4a17fa83e3fb` | **Used.** Richest topology in the pool (111 parts): tapered wedge hull, 81-key matrix, function-key block, 4-slider lane, 9 counter + 8 carry wheels, paper transport, side crank. Source of `housing_form=tapered_wedge`, `register_assembly=mullion_counter_bank`, the `slider_count=4` parameter value, and both optional dressings (`has_paper_transport`, `function_key_count`). Its 111 parts are 3.4× the fleet maximum and are what forced the N cap. |
| 2 | `…__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe` | **Used.** The only CadQuery hull and the only common-axle drum bank; source of the exact key-matrix rule, the spline crank, the shifting carry rack. Also the origin of both `allow_overlap` causes. |
| 3 | `…__003__png_6c29e006127e48e78c56f9b8f384a8da` | **Used.** Open-frame side-cheek hull, flat bed, face-on exposed pinwheels, bezel/card/glass readout, and the pool's only §6-conformant paired-rail slide. Emits no allowances. |
| 4 | `…_var_calculator_topology_pinwheel_calculato` | **Used** as `housing_form=rounded_rear_flared`. 20-point lofted plan outline; part tree untouched — hence not a topology slot. |
| 5 | `…_var_calculator_topology_lever_adding_machi` | **Used** as `housing_form=flared_four_station` + an alternate lofted crank-arm profile. Part tree untouched. |
| 6 | `…_var_calculator_topology_stepped_drum_calcu` | **Used** as `register_assembly=stepped_drum_bank`. Also the pool's best example of welding many features into one CAD solid — the technique the whole rebuild adopts to fit the compile budget. |
| 7 | `…_var_calculator_topology_rotary_dial_calcul` | **Used** as `drive_member=coaxial_rotary_dial` — *moved into the drive slot*, because it cannot combine with the front/vertical lever candidates as a local adaptation. |
| 8 | `…_var_calculator_topology_direct_key_comptom` | **Used** as `key_form=concave_mushroom_cap` + `setting_control=none`. The only topology fork that changes the part tree (−3 parts, −3 joints). |
| 9 | `…_var_drive_folding_side_crank` | **Used** as `drive_member=folding_side_crank`. Genuine joint-semantics change (free spin → 0–84° fold). Contributes one new `allow_overlap` cause (0.5 mm journal interference). |
| 10 | `…_var_drive_front_reciprocating_lever` | **Used** as `drive_member=front_reciprocating_lever`. The only record that moves the drive to another hull face, and the only one with attested host adaptation (front lip/trim re-derived). |
| 11 | `…_var_drive_vertical_pull_lever` | **Used** as `drive_member=vertical_pull_lever`. One-way 0→0.95 rad stroke and a Z-axis hand column — the pool's only non-`±π` drive range apart from the front lever. |
| 12 | `…_var_clearing_motion_carriage_reset_lever` | **Read, then rejected as a candidate.** It adds no part and no joint: only a slider deletion (already reachable as `setting_control=none`) plus crank-arm `0.010×0.075×0.012 → 0.014×0.085×0.018` and mechanism-floor `0.140 → 0.118` resizes. Both resizes survive as continuous parameters; the record stays in `sync_records`. |
| 13 | `…_var_clearing_motion_rotating_zeroing_knob` | **Used** as `setting_control=rotating_zeroing_knob`. Adds the pool's only `(0,0,1)` joint and the only `KnobGeometry`; the cleanest §2 plane-mount example (derived seat plane, 8 mm extent margin). |
| 14 | `…_var_key_matrix_10_key_keypad` | **Used.** N=10 sample, the declared lower bound, **and** the small-N layout exception (3×3 + centred zero, larger caps at pitch 0.050/0.043). Not just a count change — the only record fully reproducible at its source count. |
| 15 | `…_var_key_matrix_50_key_keyboard` | **Used for its rule, not its count.** Supplies the *deck-shrinks-to-fit* half of the pitch derivation (`plate_depth = rows·pitch + 0.014`, `cover = +0.038`), verified against both its own 5-row and the parent's 8-row geometry. N=50 is **outside the declared domain** — 66 parts against a measured fleet maximum of 33. |
| 16 | `…_var_key_matrix_90_key_full_keyboard` | **Used for its rule, not its count.** Supplies the *pitch-shrinks-to-fit* half of the derivation (`pitch_y = 0.0185` because 9 rows at 0.020 overflow the 0.174 plate by 1 mm). N=90 is **far outside the declared domain** — 106–120 parts and 336–494 collision solids against a fleet maximum of 33 parts. This record is the direct evidence for the cap. |
| 17 | `…_var_register_form_enclosed_window_bank` | **Used** as `register_assembly=enclosed_window_bank`. The **only** record in the pool that cuts real openings in a shell, so it is the §7 reference for the whole category. |
| 18 | `…_var_register_form_exposed_pinwheel_bank` | **Used** as `register_assembly=bezel_pinwheel_tower`. Contributes the derived 0.005 m tower-to-shaft stand-off, the pool's most useful register mating number. |
| 19 | `…_var_register_form_traveling_carriage_regis` | **Read, then rejected as a candidate.** Despite its name it builds no carriage: no prismatic joint, no rails, no cavity — only a static Box resize (`0.350×0.055×0.180 → 0.398×0.075×0.120`) plus the slider deletion. The resize becomes `register_tower_width/depth/height`. A real traveling carriage would have been an unattested extrapolation reparenting all N wheels; rejected, with its mechanical template recorded in *Domain reduction* should it ever be built. |

---

## Accepted candidate manifest (machine-readable)

Six slots. `core_domain = 5 × 5 × 5 × 3 × 3 = 1,125`; `key_matrix` is
multiplicity and is excluded from core per `AUTHORING.md` §4, giving
`raw_domain = 1,125 × 7 = 7,875` for `N ∈ [10, 16]`. Rejected rows are retained
so the reasoning behind every merge and demotion survives in machine-readable
form; they are not part of any domain.

| slot | candidate | diversity axis | source type | record/revision | exact model.py:Lx-Ly | key parts/joints/helpers | status |
|---|---|---|---|---|---|---|---|
| housing_form | tapered_wedge | ① silhouette + part tree | picture origin | rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb/rev_000001 | model.py:L37-L57, model.py:L97-L120, model.py:L207-L216 | part `frame`; helpers `_calculator_housing_mesh`, `_add_quad`, `_deck_z`; 8-vertex wedge, DECK_PITCH 0.271 rad, 4 feet | accepted |
| housing_form | rounded_rear_flared | ① silhouette | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_pinwheel_calculato/rev_000001 | model.py:L37-L82 | helper `_calculator_housing_mesh`; 20-point plan outline, fan-capped top and bottom, 20 side quads | accepted |
| housing_form | flared_four_station | ① silhouette | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_lever_adding_machi/rev_000001 | model.py:L37-L86, model.py:L510-L537 | helper `_calculator_housing_mesh`; 4 transverse stations, drafted side walls; lofted 6-point `crank_arm` plate | accepted |
| housing_form | cast_side_profile | ① silhouette + tilted deck | picture origin | rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe/rev_000001 | model.py:L33-L51, model.py:L129-L175 | part `housing`; helper `_housing_shell` (CadQuery, 8-point YZ profile, fillet 0.007); two-layer deck at DECK_TILT 12.5° | accepted |
| housing_form | open_frame_side_cheek | ① part tree + flat bed | picture origin | rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da/rev_000001 | model.py:L32-L59, model.py:L87-L158 | part `housing`; helper `_wedge_box`; base floor + 2 cheeks + fascia + bed + 2 shaft rails + tower, DECK_PITCH 0 | accepted |
| register_assembly | mullion_counter_bank | ①② part tree + spin axis (1,0,0) | picture origin | rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb/rev_000001 | model.py:L122-L167, model.py:L361-L401, model.py:L403-L441 | 9 `number_wheel_i` parts + 9 REVOLUTE; carry train welded to 1 rack part (from 8 `carry_wheel_i`); 10 mullions, 9 panes | accepted |
| register_assembly | railed_drum_bank | ①② common axle + PRISMATIC carry | picture origin | rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe/rev_000001 | model.py:L177-L237, model.py:L325-L354, model.py:L387-L414 | 10 `wheel_i` parts + 10 REVOLUTE; 1 `carry_rack` + 1 PRISMATIC; helper `_number_wheel`; 9 dividers, common axle r 0.0022 | accepted |
| register_assembly | stepped_drum_bank | ①② Leibniz stepped member | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_stepped_drum_calcu/rev_000001 | model.py:L54-L82, model.py:L195-L255, model.py:L343-L432 | helper `_number_wheel` with 9 unioned teeth 3.5→15.5 mm at 40° pitch; 10 wheels + rack as above; 1 visual per drum | accepted |
| register_assembly | bezel_pinwheel_tower | ①② spin axis (0,1,0), face-on readout | forked variant | rec_0611_mechanical_calculator_var_register_form_exposed_pinwheel_bank/rev_000001 | model.py:L64-L91, model.py:L198-L254, model.py:L318-L357 | helper `_exposed_pinwheel_bank` (7 cut bays + rear relief); 7 `wheel_i` + 7 REVOLUTE; BezelGeometry readout; static brass rack | accepted |
| register_assembly | enclosed_window_bank | ①② closed casing with cut windows | forked variant | rec_0611_mechanical_calculator_var_register_form_enclosed_window_bank/rev_000001 | model.py:L64-L86, model.py:L198-L254, model.py:L318-L357 | helper `_enclosed_window_bank` (cavity + 7 window cuts, the pool's only §7 real openings); 7 wheels + 7 REVOLUTE | accepted |
| drive_member | side_rotary_crank | ② REVOLUTE (1,0,0) ±π + grip child | picture origin | rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da/rev_000001 | model.py:L366-L404, model.py:L406-L441 | parts `crank`, `crank_grip`; 2 REVOLUTE; throw 0.075, effort 15.0; grip sleeve + ball + marker | accepted |
| drive_member | folding_side_crank | ② grip REVOLUTE (0,1,0) 0→84° | forked variant | rec_0611_mechanical_calculator_var_drive_folding_side_crank/rev_000001 | model.py:L71-L106, model.py:L466-L483 | helper `_crank_tube_mesh` (CadQuery weld: shaft, hub, arm, knuckle, hinge pin); free spin becomes a bounded fold | accepted |
| drive_member | front_reciprocating_lever | ② REVOLUTE (0,1,0) ±0.48, front wall | forked variant | rec_0611_mechanical_calculator_var_drive_front_reciprocating_lever/rev_000001 | model.py:L200-L208, model.py:L474-L523 | part `crank`, 1 REVOLUTE; pivot moved to (0.105,-0.247,0.030); host front lip and trim re-derived | accepted |
| drive_member | vertical_pull_lever | ② REVOLUTE (-1,0,0) 0→0.95 one-way | forked variant | rec_0611_mechanical_calculator_var_drive_vertical_pull_lever/rev_000001 | model.py:L197-L205, model.py:L471-L515 | part `vertical_pull_lever`, 1 REVOLUTE, no grip child; 0.112 arm hanging down, Z-axis hand column | accepted |
| drive_member | coaxial_rotary_dial | ② entry actuator on the drive axis | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_rotary_dial_calcul/rev_000001 | model.py:L71-L85, model.py:L292-L327, model.py:L478-L495 | helper `_rotary_selector_dial` (⌀0.100, 10 finger holes); dial + hub on the crank part; host backplate, scale ring, 10 marks | accepted |
| key_form | stepped_box_cap | ③ form family | picture origin | rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe/rev_000001 | model.py:L273-L323 | 3 visuals per key: 0.006² stem, 0.015² cap, number inset; three-colour column grouping | accepted |
| key_form | cylindrical_plunger | ③ form family | picture origin | rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da/rev_000001 | model.py:L246-L288 | 3 visuals: ⌀0.010×0.024 stem, ⌀0.034×0.010 cap, ⌀0.019 legend disc; brass key-guide strips between rows | accepted |
| key_form | concave_mushroom_cap | ③ form family | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_direct_key_comptom/rev_000001 | model.py:L61-L118, model.py:L299-L344 | helper `_direct_key_cap` (8-ring × 24-segment lathe, concave dish); stem ⌀0.009×0.030, travel 0.009; mesh built once and shared | accepted |
| setting_control | slider_bank | ①② N × PRISMATIC on paired rails | picture origin | rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da/rev_000001 | model.py:L227-L235, model.py:L331-L364 | `slider_count` ∈ {2,3,4} parts + PRISMATIC (0,-1,0) 0→0.028; 2 rails per slider at x±0.009; 3-piece carriage | accepted |
| setting_control | zeroing_knob | ② REVOLUTE (0,0,1), the pool's only vertical axis | forked variant | rec_0611_mechanical_calculator_var_clearing_motion_rotating_zeroing_knob/rev_000001 | model.py:L326-L369 | part `zeroing_knob` + 1 REVOLUTE; KnobGeometry faceted + ribbed KnobGrip, center=False so the base seats at local z=0 | accepted |
| setting_control | none | ① part tree (no control bank) | forked variant | rec_0611_mechanical_calculator_var_calculator_topology_direct_key_comptom/rev_000001 | model.py:L278-L293, model.py:L387-L396 | 0 parts, 0 joints; the Comptometer configuration and that of 8 of 19 records; key-guide strips and crank survive unchanged | accepted |
| key_matrix | keypad_layout | ① multiplicity, N ≤ 12 | forked variant | rec_0611_mechanical_calculator_var_key_matrix_10_key_keypad/rev_000001 | model.py:L76-L101, model.py:L247-L282 | helper `_add_key_geometry`; 3×3 + centred zero, pitch 0.050/0.043, cap 0.028×0.026; N parts + N PRISMATIC, flat to housing | accepted |
| key_matrix | matrix_layout | ① multiplicity, N > 12 | forked variant | rec_0611_mechanical_calculator_var_key_matrix_50_key_keyboard/rev_000001 | model.py:L102-L122, model.py:L296-L329 | helper `_add_keyboard_key_visuals`; divmod(index, KEY_COLUMNS), plate_depth = rows·pitch + 0.014; N parts + N PRISMATIC | accepted |
| key_matrix | full_90_key_count | ① multiplicity | forked variant | rec_0611_mechanical_calculator_var_key_matrix_90_key_full_keyboard/rev_000001 | model.py:L296-L331 | 90 parts + 90 PRISMATIC | rejected — count outside the capped domain N ∈ [10,16]; 106-120 parts vs a measured fleet maximum of 33; its pitch_y = 0.0185 derivation is adopted by matrix_layout |
| register_assembly | traveling_carriage_bank | ③ proportion only | forked variant | rec_0611_mechanical_calculator_var_register_form_traveling_carriage_regis/rev_000001 | model.py:L148-L153 | 0 new parts, 0 new joints | rejected — the record builds no carriage (no prismatic, no rails, no cavity); a Box resize is a proportion change, folded into register_tower_width/depth/height |
| setting_control | carriage_reset_lever | ③ proportion only | forked variant | rec_0611_mechanical_calculator_var_clearing_motion_carriage_reset_lever/rev_000001 | model.py:L130-L135, model.py:L332-L337 | 0 new parts, 0 new joints | rejected — adds no part or joint; deletion reachable as setting_control=none, resizes folded into crank_arm_* and mechanism_floor_depth |
| setting_control | deck_slider_lane | ② count and placement only | picture origin | rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb/rev_000001 | model.py:L314-L359 | 4 parts + 4 PRISMATIC | rejected — collapsed into slider_bank as slider_count=4; its deck-normal seat derivation is adopted there |
| setting_control | flank_pair_sliders | ② count and placement only | picture origin | rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe/rev_000001 | model.py:L239-L246, model.py:L356-L385 | 2 parts + 2 PRISMATIC | rejected — collapsed into slider_bank as slider_count=2 |
| paper_transport | roll_and_carry_bridge | ① part tree | picture origin | rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb/rev_000001 | model.py:L169-L194, model.py:L443-L469 | 1 part + 1 REVOLUTE | rejected as a slot — demoted to the discrete parameter has_paper_transport ∈ {0,1} on tapered_wedge; a 2-member slot doubles core_domain for 1 of 19 records |
| function_key_block | six_key_corner_block | ① presence | picture origin | rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb/rev_000001 | model.py:L267-L312 | 6 parts + 6 PRISMATIC | rejected as a slot — demoted to the discrete parameter function_key_count ∈ {0,6}; same mechanism as key_matrix, differing only in cap size and effort |
