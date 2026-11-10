# Rivet squeeze — SourceMap

export_category: rivet_squeeze

Authoritative records live under `data/records` of the `articraft_data` repo
(`<ARTI_SKILL_ROOT>/articraft_data/data/records`). The category is a
hand-held **compression** riveter: a forged C-yoke or straight-head frame whose
throat carries **two opposed dies on one shared axis**, a hand lever that drives
the upper die toward the lower one, and an independently adjustable lower
die/anvil that sets rivet length.

It is explicitly **not** a blind-rivet puller (`rec_rivet_squeeze1_var_*` is the
`must_not_become` sibling: single nose, mandrel pulled *away* from the work). One
record in this pool — origin 003 — actually modelled a pop-rivet gun and says so
in its own `run_notes` (L85-L91); its corrective fork `alligator_jaw` rotates the
receiver onto a vertical squeeze axis and adds a real opposed lower jaw. That
distinction drives the rejection in Slot A and category anchor 8.

Source pool: **13 record dirs — 3 picture origins and 10 forked variants. All 13
were read in full before any candidate was chosen.** The three origins were read
line by line. Each variant is a byte-level fork of one origin, so it was read as a
full unified diff against that parent: every changed line was reviewed and the
unchanged remainder is identical to a file already read line by line. Parentage
was established by diff size against all three origins, not by name:

| Variant | Parent origin | Changed lines (vs parent) | vs. the other two origins |
|---|---|---|---|
| `yoke_frame_compact_straight_head` | 001 | 48 | 1140 / 1130 |
| `return_leaf_return_spring` | 001 | 67 | 1157 / 1149 |
| `head_module_rotating_set_holder` | 001 | 79 | 1195 / 1179 |
| `return_torsion_handle_spring` | 001 | 97 | 1179 / 1169 |
| `yoke_frame_deep_c_yoke` | 002 | 97 | 1155 / 1143 |
| `squeeze_mechanism_compound_toggle` | 002 | 97 | 1161 / 1163 |
| `squeeze_mechanism_eccentric_cam_lever` | 002 | 107 | 1199 / 1183 |
| `squeeze_mechanism_screw_press` | 002 | 298 | 1186 / 1158 |
| `head_module_quick_change_yoke` | 003 | 62 | 1162 / 1160 |
| `yoke_frame_alligator_jaw` | 003 | 376 | 1366 / 1348 |

**Frame convention for the rebuild.** Origin 002's frame is adopted: the tool lies
horizontally, the main handle pivot is at the origin, grips extend toward **+X**,
the jaw throat opens toward **−X**, and the tool's width runs along **Y**.

* **`±Y` is the lever/pivot axis.** Every hinge in the pool turns about `±Y`:
  001 L338-L339 `(0,1,0)`, 002 L302-L303 `(0,−1,0)`, 003 L308-L309 `(0,1,0)`,
  003 latch L404 `(0,−1,0)`, 001 latch L459. Thirteen of thirteen records agree.
  The one exception is the `screw_press` drive head (L288), which turns about the
  squeeze axis itself — that is the candidate's whole point, and it is called out
  in the anchors rather than smoothed away.
* **`+Z` is the squeeze/die axis.** 001 (L379, L423), 002 (L363, L416) and both
  their fork families put the ram and anvil prismatic axes on `(0,0,∓1)`. 003 uses
  `(−1,0,0)` because it is the pop-rivet outlier; its own fork `alligator_jaw`
  corrects this by giving the nose joint `rpy=(0,−π/2,0)` at L357, which maps the
  local `−X` travel onto world `−Z`. So 4 of the 5 accepted frame candidates, and
  the corrected 5th, squeeze along Z.
* 001 and 003 model the tool standing upright (handles hanging to `−Z`, jaws near
  `z≈0.32-0.39`); that is the same mechanism rotated 90° about Y and is treated as
  a rigid re-framing, not a structural difference.

sync_records:
  - rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586
  - rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83
  - rec_picturex_0611__rivet_squeeze__003__png_7c15724dd1fc4e4a9c3ba1c34794454c
  - rec_0611_rivet_squeeze_var_yoke_frame_deep_c_yoke
  - rec_0611_rivet_squeeze_var_yoke_frame_alligator_jaw
  - rec_0611_rivet_squeeze_var_yoke_frame_compact_straight_head
  - rec_0611_rivet_squeeze_var_squeeze_mechanism_compound_toggle
  - rec_0611_rivet_squeeze_var_squeeze_mechanism_eccentric_cam_lever
  - rec_0611_rivet_squeeze_var_squeeze_mechanism_screw_press
  - rec_0611_rivet_squeeze_var_head_module_quick_change_yoke
  - rec_0611_rivet_squeeze_var_head_module_rotating_set_holder
  - rec_0611_rivet_squeeze_var_return_torsion_handle_spring
  - rec_0611_rivet_squeeze_var_return_leaf_return_spring

## Component slots and candidates

All spans are `data/records/<record>/revisions/rev_000001/model.py` lines.
Record ids are abbreviated after their first appearance.

### Slot A — `yoke_frame` (grounded forging carrying both dies; ① silhouette + part tree)

| Candidate | Record | Exact span | Diversity axis | Key construction |
|---|---|---|---|---|
| `deep_c_yoke_forging` | `…__001__png_2ba6198e3af4438abc2a873af2483586` | L38-L122 | ① silhouette / built-up jaw beams | An **18-point** XZ side profile (x −50…35 mm, z 41…390 mm) extruded ±10 mm by `_plate_from_profile` (L25-L35), then two jaw beams *unioned on*: upper `rect(96,30)` at `(-82,375)` + `circle(15)` boss at `(-130,375)`, lower `rect(76,22)` at `(-72,311)` + `circle(11)` boss at `(-110,311)`, both extruded ±10 mm. Four bores are then **cut**: a `r=8` fixture hole at `(8,365)`, an `r=7.2` pivot bore at `(0,320)`, and two *vertical* clearance bores at `x=−102` — `r=6.4 × 58 mm` for the ram (L108-L114) and `r=5.6 × 42 mm` for the anvil (L115-L121). One welded solid, one visual |
| `throated_forged_body` | `…__002__png_7a78c071827541ed822cff3fb676aa83` | L49-L100 | ① silhouette / cut throat | The inverse construction: an 8-point **outer** silhouette (x −0.145…0.066, z −0.052…0.055) filleted 4 mm on `\|Y` edges, then a 5-point **throat** profile 0.050 m wide (wider than the 0.030 m body, so it cuts clean through) subtracted at L65-L77. Bores are stopped, not through: `upper_bore r=0.0052 × 0.047` and `lower_bore r=0.0072 × 0.060` both at `x=−0.124` (L81-L94) stop at the throat "so both jaw beams remain structural". Pivot cuts `r=0.0054` at `(0.046,0.013)` and `r=0.0042` at `(0.022,0.035)` (L98-L99) |
| `long_c_yoke_throat` | `…_var_yoke_frame_deep_c_yoke` | L49-L114 (+ side cover L189-L211) | ① silhouette / throat topology | Fork of `throated_forged_body`. Outer profile **8 → 12 points** (nose out to `x=−0.160`), throat profile **5 → 13 points** with the fillet dropped 3 → 2 mm — a gently tapering throat with a rounded inner heel instead of a boxy relief. The die station stays at `x=−0.124`, so this candidate lengthens the *frame* rather than the throat depth. Its `side_cover` also changes topology: 7 → 11 points, relocated from spanning the whole body to a compact heel cheek that "does not bridge across or visually cap the open throat". Author test raises the x-extent floor 0.195 → 0.225 and z 0.095 → 0.108 (L645-L652) and asserts `lever_x − ram_x > 0.160` (L653-L665) |
| `compact_straight_head` | `…_var_yoke_frame_compact_straight_head` | L38-L125 | ① silhouette / jaw proportion + station | Fork of `deep_c_yoke_forging`. Jaw beams shorten and the bosses pull in: upper `rect(96,30)@(-82,375)` → `rect(52,30)@(-50,375)` with the boss `circle(15)` moving `-130 → -76`; lower `rect(76,22)@(-72,311)` → `rect(48,24)@(-48,316)` with the boss `circle(11)@-110` → `circle(12)@-72`. Both die bores and **both prismatic joint origins** move `x −0.102 → −0.065` (L113, L120, L383, L427) — the station is re-derived, not just the visual. Author test inverts to an upper bound: x-extent must be `0.105 … 0.130` (L604-L613) plus an explicit check that both joint origins sit at `−0.065` (L614-L625) |
| `alligator_jaw` | `…_var_yoke_frame_alligator_jaw` | L102-L144 (frame), L200 + L352-L365 (vertical receiver), L273-L316 (lower jaw on the lever) | ① silhouette / **which part carries the lower die** | Fork of 003 and the only candidate where the lower die belongs to the *moving* member. The frame outline goes **22 → 25 points** and the nose extends `x −52 → −170 mm`, forming a long upper jaw. The barrel receiver is re-origined from `(-0.081,0,0.307)` to `(-0.145,0.021,0.329)` with `rpy=(0,−π/2,0)`, turning the horizontal pop-rivet nose into a vertical rivet-set receiver. The lever's `moving_grip` becomes a **19 → 23 point** matching lower jaw in `dark_steel` (not rubber), 25 → 12 mm thick, with a `circle(5.0).extrude(17)` lower rivet set unioned in at `x=−172 mm` (L299-L306). Lever travel collapses `24° → 2°` (L331) because the handle *is* the jaw |

**Rejected — `compact_gun_head` (003 L102-L144 as authored).** 003's frame is a
compact head with a horizontal `_axis_x_tube(10.5, 7.2, 34.0)` barrel (L191) and a
single prismatic `nosepiece` on `(−1,0,0)` (L340-L347) — one die, no opposed pair,
work axis horizontal. The record's own `run_notes` (L86-L89) and its author test
`"category mismatch is recorded in run notes"` (L442-L446) concede it is a
blind/pop riveter. Accepting it would break anchors 3 and 8 and collapse the
distinction from the `must_not_become` sibling. Its *corrected* fork
`alligator_jaw` is accepted instead, and its head hardware still supplies Slot C's
`quick_change_yoke_clip` and Slot E's `eye_and_wire_loop_latch`. **This rejection
is host-level, not record-level — see "Resolving the 003 rejection" below, which
states the disqualifying feature precisely and justifies each of the three things
the rebuild still takes from 003 and its forks.**

### Slot B — `squeeze_mechanism` (what drives the upper die; ② joint set / coupling)

| Candidate | Record | Exact span | Joint topology | Key construction |
|---|---|---|---|---|
| `hidden_internal_toggle` | 001 | L349-L391 (ram + joint) | frame → ram PRISMATIC only; **no link part** | The mechanism is deliberately not exposed: `frame_to_ram` carries `meta["mechanism_note"] = "Actuated by the internal compound toggle hidden by the frame."` (L389). Effort **9000**, velocity 0.025, travel `0 → 0.0040` m. The whole squeeze layer is 1 joint and 0 extra parts — the low-part-count baseline of the slot |
| `dogbone_mimic_link` | 002 | `_linkage_shape` L125-L140, part+joint L315-L340 | frame → lever REVOLUTE → link REVOLUTE (`Mimic`), frame → ram PRISMATIC | A 5-point dog-bone plate 0.004 m thick, offset to the outer cheek by `.translate((0,0.026,0))`, with two `r=0.0032` eyes cut at `(0,0)` and `(0.046,0.019)`. The link is a **mimic** child of the lever: `Mimic(joint=lever, multiplier=−0.70)` (L334-L338) — it counter-rotates. The ram is coupled only by metadata (`mechanical_driver`, `coupling_note="revolute-to-prismatic cam coupling"`, L373-L374) |
| `long_toggle_cheek` | `…_var_squeeze_mechanism_compound_toggle` | `_linkage_shape` L125-L158, ram head L373-L384, joint L339-L360 | same tree, but the link **reaches the ram** | The dog-bone becomes a computed-normal rectangular web from `(0,0)` to `(−0.196, 0.033)` (`half_width=0.006`, normals from `math.hypot`) with `circle(0.008)` bosses at both ends and `r=0.00315` bores. The ram grows a `Box(0.018,0.020,0.008)` `ram_head` and a `Cylinder(r=0.0032, len=0.062)` `ram_toggle_pin`, so the toggle actually terminates on the ram instead of in mid-air. Mimic flips sign and magnitude: `−0.70 → +0.65` (L354) |
| `eccentric_cam` | `…_var_squeeze_mechanism_eccentric_cam_lever` | cam lobe L330-L339, reaction bracket L254-L284, follower head L409-L414 | same tree + a **reaction structure on the fixed handle** | A `r=0.018` lobe offset `(0.009, 0.003)` from the pivot with a `r=0.0056` bore cut on the axis, on the outer cheek at `y=−0.0245`. The fixed handle grows a 6-point `cam_reaction_bracket` (0.004 m, fork slot 0.065) with a `r=0.007` reaction pin at `(0.058,−0.017)`, plus a `Box(0.030,0.004,0.050)` bridge. The ram grows a `r=0.008 × 0.005` `cam_follower_head`. Mimic `−0.70 → −0.55`. Author test asserts the lobe centre sits ≥7 mm ahead of the pivot centre (L655-L671) — the eccentricity is checked, not assumed |
| `screw_press` | `…_var_squeeze_mechanism_screw_press` | drive hub L262-L280, lever joint L282-L299, tommy bar L304-L338, threaded ram L343-L362 | **lever REVOLUTE about the squeeze axis; link becomes PRISMATIC** | The hand lever is replaced by a `circle(0.014).extrude(0.018)` drive hub with a `r=0.010 × 0.003` seating register below, a transverse `r=0.0042` tommy bore, and a `r=0.0075 × 0.004` keying boss on top. Its joint moves to the die station `(-0.124, 0, 0.055)` with axis `(0,0,−1)` and travel `0 → 180°` — **the only joint in the pool that is not about ±Y**. `lever_to_compound_link` changes REVOLUTE → **PRISMATIC** along `(0,1,0)`, `±0.025` m: a real sliding tommy bar (`r=0.0034 × 0.170` + `r=0.0042` bushing + two `r=0.0070` end knobs). Ram effort 5200 → **7600**, velocity 0.05 → 0.012, and the joint gains `meta["lead_m_per_turn"]=0.00175` |

### Slot C — `head_module` (die / rivet-set holders and their retention; ③ form family)

| Candidate | Record | Exact span | Diversity axis | Key construction |
|---|---|---|---|---|
| `stepped_cylinder_dies` | 001 | ram L349-L373, anvil L393-L417 | ③ stacked-turning form | Four cylinders per part. Ram: shaft `r=0.0052 × 0.052` @z 0.016, holder `r=0.0080 × 0.005` @−0.0065, tip `r=0.0035 × 0.008` @−0.013, cap `r=0.0080 × 0.006` @0.043. Anvil: shank `r=0.0045 × 0.042` @−0.010, adjuster wheel `r=0.0080 × 0.005` @−0.0305, holder `r=0.0075 × 0.004` @0.002, tip `r=0.0035 × 0.003` @0.0055. **The two tips are identical `r=0.0035`** — the opposed-set signature |
| `plain_die_pair` | 002 | ram L345-L357, anvil L380-L410 | ③ minimal turned form | Ram is 2 cylinders (`r=0.0052 × 0.035` shaft + `r=0.0062 × 0.012` die). Anvil is 5: stem `r=0.0047 × 0.075`, die `r=0.0060 × 0.010` @0.035, knurled adjuster `r=0.0072 × 0.044` @−0.045, stop `r=0.0090 × 0.005` @−0.069, collar `r=0.0100 × 0.006` @−0.004. The long knurled tail below the jaw is what reads as "adjustable anvil" |
| `rotating_set_holder` | `…_var_head_module_rotating_set_holder` | `_rotating_set_holder_shape` L220-L249, upper L388-L399, lower L444-L455 | ③ faceted, hand-turnable socket | A **single welded CadQuery solid** per holder, parameterised by height: `circle(5.6).extrude(1.2)` lower land ∪ `polygon(12, 16.8)` grip collar (offset 0.9, height `h−1.7`) ∪ `circle(6.2).extrude(0.8)` upper land, minus a `circle(3.55).extrude(1.7)` blind socket at offset −0.05. Called at `h=5.0` (upper, origin z −0.009) and `h=4.0` (lower, origin z 0.0). Author test asserts both collars measure **0.016–0.018 m across both X and Y** (L677-L691) — a genuine 12-sided form, not a scaled cylinder |
| `quick_change_yoke_clip` | `…_var_head_module_quick_change_yoke` | `_quick_change_yoke_shape` L80-L107, visual L254-L264 | ③ **retention topology** (a clip, not a shoulder) | A stamped horseshoe in the XZ plane: `circle(7.2).circle(3.3).extrude(±1.5)` annulus, minus a `rect(10,3.8)@(-5,0)` release slot that opens the ring toward −X, plus a `rect(6,5)@(8.7,0)` thumb tab pierced by `circle(1.2)@(9.4,0)`. It replaces the parent's plain `Cylinder(r=0.0034, len=0.004)` jaw fastener. It is a **visual on the frame part**, seated at `y=−0.0165` so its inner face is tangent to the frame cheek at `y=−0.015` |

### Slot D — `return_element` (③ form family; three real forms plus a source-attested absence)

| Candidate | Record | Exact span | Key construction |
|---|---|---|---|
| `wire_extension_spring` | 001 | L262-L281 | `tube_from_spline_points` over **7 zig-zag points** (x alternating −0.039/−0.046, z 0.292 → 0.232), `radius=0.0012`, 6 samples/segment, 12 radial segments, capped. Emitted as a visual on the **frame**, at `y≈−0.0115`, i.e. straddling the frame's `−0.010` cheek face — legal because it is the same part (`MECHANICAL_PRIORS` §1c) |
| `leaf_return_spring` | `…_var_return_leaf_return_spring` | `_leaf_return_spring_shape` L220-L245, visual L291-L302 | A **17-point** closed side profile (x −34…−49.5 mm, z 231…296 mm) extruded to just **1.6 mm** by the parent's own `_plate_from_profile`, so it is a genuine pre-bowed leaf with a broad clamped upper tang and a narrow bowed lower end. Placed at `y=−0.0095` → spans −0.0087…−0.0103, i.e. 0.3 mm into the frame cheek; same part, free. Author test bounds it as long-and-thin: z-extent 0.055-0.075, x-extent 0.008-0.020, **y-extent ≤ 0.002** (L632-L642) |
| `torsion_handle_spring` | `…_var_return_torsion_handle_spring` | `_torsion_handle_spring_geometry` L220-L261, visual L308-L315 | A real helix generated in code: `coil_radius=0.0115` about the pivot `(0, 0.320)`, `start_angle=225°`, `turns=2.25`, **34 samples**, with the Y coordinate walking `−0.0215 → −0.0275` so the coil advances axially. Three formed reaction-leg points precede the coil and three follow it; the whole 40-point path becomes one `tube_from_spline_points(radius=0.00115)` mesh. It also writes `return_element` meta onto both the part and the joint (L321, L385-L386), which the author test then checks along with a pivot-centred AABB (L651-L667) |
| `none` | 002, 003 | — | 002 (6 parts) and 003 (4 parts) carry no return element at all. 2 of 3 origins; the absence is source-attested, not a modelling gap |

### Slot E — `handle_lock` (③ joint count / capture topology)

| Candidate | Record | Exact span | Key construction |
|---|---|---|---|
| `wire_hook_latch` | 001 | part L434-L452, joint L453-L467, host pin L323-L331 | A 5-point open spline (`(0,0,0)` → `(−0.073,0.020,0.004)`) tubed at `r=0.0012`, 10 samples/segment, 14 radial segments. **Parented to the moving handle**, not the frame: `handle_to_latch` REVOLUTE about `(0,1,0)` at `(0.020,−0.034,−0.220)`, limits `−0.05 … 1.10` rad, effort 2.0. The host pin is `Cylinder(r=0.0032, len=0.006)` at `(0.020,−0.031,−0.220)` — **3 mm off the hinge axis**, which is why the record needs `allow_overlap` |
| `eye_and_wire_loop_latch` | 003 | eye L349-L369, wire L370-L390, axle L392-L397, joint L398-L412 | A real **annulus** `circle(4.5).circle(2.2).extrude(±2.0)` rotated onto the Y axis, plus a **closed 8-point loop** tubed at `r=0.0011` (12 samples/segment, 14 radial). Parented to the **frame**, REVOLUTE about `(0,−1,0)` at `(−0.062,−0.019,0.055)`, `0 → 78°`, effort 2.0. The axle is `Cylinder(r=0.0020, len=0.008)` at exactly the joint origin — **eye ID 2.2 mm over a 2.0 mm axle = 0.2 mm radial clearance**, verified by `expect_within(..., margin=0.001)` at L546-L554 **with no `allow_overlap`**. This is the construction the rebuild should copy everywhere |
| `none` | 002 | — | 002 has no latch |

## Mating mechanisms (sampled across records, not one per candidate)

Per `MECHANICAL_PRIORS.md` §1b these were read across *all thirteen* records. They
are what decides whether the assembly stands up, and they are invisible to
mechanical extraction.

### 1. The pin/bore rule — and the fact that most of the pool gets it wrong

| Record | Frame bore r | Moving-member bore r | Pin r | Pin's owning part | Result |
|---|---|---|---|---|---|
| 001 | 7.2 mm (L99-L104) | 6.8 mm (L150-L154) | **6.2 mm** (L312) | **`moving_handle`** | +0.6 mm to its own bore, +1.0 mm to the frame → **clean, no allowance** |
| 002 | 5.4 mm (L98) | 5.5 mm (L121) | 5.5 mm (L194) | `frame` | **exactly 0** to the lever, −0.1 mm to the frame → `allow_overlap` L481 |
| 002 upper mount | 4.2 mm (L99) | fork slot only | 5.5 mm (L199) | `frame` | **−1.3 mm interference** → `allow_overlap` L464 |
| 003 | 6.5 mm (L137-L143) | 5.6 mm (L249-L254) | 5.8 mm (L204) | `frame` | **−0.2 mm interference** → `allow_overlap` L518 + `expect_contact(tol=0.0003)` |
| 002 link eye | — | 3.2 mm (L138-L139) | 3.2 mm (L291) | `squeeze_lever` | **exactly 0** → `allow_overlap` L524 |
| toggle fork link | — | 3.15 mm (L156-L157) | 3.2 mm (L380) | `squeeze_ram` | −0.05 mm, self-described "slight modeled press-fit" → `allow_overlap` L574 |

**Derivation rule for the rebuild** — take 001's, which is the only record that
needs no allowance:

```
pin_r      = min(host_bore_r, member_bore_r) − 0.6 mm     # 001: 6.8 − 0.6 = 6.2
host_bore_r = member_bore_r + 0.4 mm                       # 001: 6.8 + 0.4 = 7.2
```

and, decisively, **the pin visual belongs to the moving member, not the frame**
(001 L311-L316). Intra-part embedding is free (`MECHANICAL_PRIORS` §1c), so the
pin may sit inside the lever's own hub with zero clearance; only the frame bore
has to be a real cross-part clearance, and 1.0 mm is what 001 gives it.

### 2. Ram / anvil guide-bore fits

| Record | Ram bore r | Ram shaft r | Radial clearance | Anvil bore r | Anvil stem r | Clearance |
|---|---|---|---|---|---|---|
| 001 | 6.4 mm (L108-L114) | 5.2 mm (L351) | **+1.2 mm** | 5.6 mm (L115-L121) | 4.5 mm (L395) | **+1.1 mm** |
| 002 | 5.2 mm (L81-L87) | 5.2 mm (L347) | **0** → `allow_overlap` L498 | 7.2 mm (L88-L94) | 4.7 mm (L382) | +2.5 mm |
| screw_press | 5.2 mm (inherited) | 4.6 mm (L347-L351) | +0.6 mm, but thread crests `r=0.0050` (L352-L358) leave **+0.2 mm** → `allow_overlap` L517 |
| 003 barrel | tube ID 7.2 mm (L191) | shank 6.2 mm (L53-L58) | +1.0 mm, but the `circle(9.0)` collar (L59-L64) is **1.8 mm larger than the ID** → `allow_overlap` L507 |

Rule: `bore_r = shaft_r + 1.1…1.2 mm` (001's number), and **every step of the die
stack must be ≤ `bore_r − 1.1 mm`**, which is precisely what 002, 003 and
`screw_press` violate.

### 3. Open die gap, ram stroke, and their derivation

| Record | Upper tip face | Lower tip face | **Open gap** | Ram stroke | Residual at full squeeze | Asserted |
|---|---|---|---|---|---|---|
| 001 | 0.350 − 0.013 − 0.004 = **0.333** | 0.322 + 0.0055 + 0.0015 = **0.329** | **4.0 mm** | 0.0040 (L385) | ≈ 0 | open 3.5-4.5 mm (L618-L627); closed `max_gap=0.00025`, `max_penetration=0.0002` (L651-L660) |
| 002 | 0.055 − 0.041 − 0.006 = **0.008** | −0.045 + 0.035 + 0.005 = **−0.005** | **13.0 mm** | 0.011 (L369) | 2.0 mm | open 10-16 mm (L610-L619); closed 1-6 mm (L645-L654) |

**`ram_travel = open_die_gap − closing_residual`**, with `closing_residual` 0 mm
(001) or 2 mm (002). It is never a free constant. The anvil then adds a symmetric
adjust range on top: `±0.003` m (001 L428-L429) or `±0.004` m (002 L421-L422),
which must not be allowed to close the gap on its own.

### 4. Coaxiality of the die pair — the category's defining assertion

* 001 L611-L617: `expect_origin_distance(ram, adjustment_die, axes="xy", max_dist=0.0005)`
* 002 L601-L609: `expect_overlap(ram, anvil, axes="xy", elem_a="upper_die", elem_b="lower_die", min_overlap=0.008)`
* 002 L678-L686 repeats it **inside** the anvil-adjusted pose, so adjustment may
  not break coaxiality
* `rotating_set_holder` L692-L698 adds a third, independent restatement

The tolerance is **0.5 mm** and both prismatic joint origins share the same
`x` (001: `−0.102` for both, L379/L423; 002: `−0.124` for both, L363/L416;
`compact_straight_head`: `−0.065` for both, and its author test L614-L625 checks
that the two origins are equal to `1e-9`). One `die_station_x` parameter feeds
both joints.

### 5. Lever lateral stand-off — three different, all-legal solutions

* **001 — offset plate.** Both moving-handle visuals carry `origin=Origin(xyz=(0,−0.015,0))`
  (L293, L305) while the joint origin has no Y term. Handle plate half-thickness
  4 mm → inner face at `y=−0.011`; frame plate half-thickness 10 mm → outer face at
  `y=−0.010`. **1.0 mm air gap.**
* **002 — forked root.** `_handle_shape(fork_length=…)` (L113-L119) cuts a
  `fork_length × 0.032 × 0.075` slot through the handle root. The frame is
  **0.030 m** wide → **1.0 mm per side**. Used at `fork_length=0.043` (fixed
  handle, L232) and `0.045` (lever, L277). The 002 fork family inherits this, and
  `eccentric_cam` reuses it at `0.065` for the reaction bracket (L265).
* **003 — outboard of the cheek.** Joint origin `y=+0.021` (L308); frame half-width
  15 mm, lever plate 9.5 mm thick → lever spans `y 16.25…25.75 mm`. **1.25 mm
  gap** to the frame face. The frame separately cuts a `70 × 105 × 12.5` lever
  relief slot (L129-L135) "while retaining two substantial cheek plates" — the slot
  is genuinely cut even though this record's lever does not use it.

Rule: `lever_standoff ≥ 1.0 mm`, or a fork slot `frame_width + 2.0 mm`.

### 6. Grip gap at full close

* 001 L638-L647, inside `ctx.pose({handle_joint: 0.15})`:
  `expect_gap(moving_grip, fixed_grip, axis="x", min_gap=0.001, max_gap=0.005)`
  — the closed handles keep **1-5 mm** and never touch. The same block requires
  the grip centre to travel **> 25 mm** (L661-L670).
* 002 L656-L671 states it as a strict inequality instead:
  `squeezed_lever_box[1][2] < fixed_end_box[0][2] − 0.0005` — a **0.5 mm**
  minimum, with the lever end rising **> 45 mm**.
* 003 L581-L587 checks the *open* pose: grips separated by **≥ 55 mm** in x; and
  L606-L614 that the squeeze moves the grip **≥ 70 mm**.

So: closed grip gap ∈ [0.5, 5.0] mm, and the handle travel must produce ≥ 25 mm of
grip motion. That pair of constraints is what fixes the lever length against the
lever travel — they cannot be sampled independently.

### 7. Return-spring stand-offs (the only cross-part spring problem)

* 001's wire spring sits at `y ≈ −0.0098 … −0.0132` against a frame face at
  `−0.010`; the leaf spring at `−0.0087 … −0.0103`. **Both are visuals on the
  frame part**, so the 0.2-0.3 mm embed costs nothing (§1c).
* The **torsion spring is the exception**: its coil runs `y −0.0204 … −0.0287`
  (centre −0.0215 → −0.0275, `r=0.00115`) while it is still a visual on the
  frame — but the *moving handle* plate occupies `y −0.011 … −0.019`. Clearance
  between the coil and the moving part is **1.7 mm**, and the author test
  (L651-L667) requires the coil to straddle the pivot in both X and Z
  (extent ≥ 0.030 and ≥ 0.035). Any tightening of the handle stand-off eats
  directly into that 1.7 mm.

### 8. Same-part tangent seating (the sanctioned alternative to `allow_overlap`)

`quick_change_yoke` L528-L537 is the cleanest statement in the pool:

```
expect_gap(frame, frame, axis="y",
           positive_elem="body_shell", negative_elem="jaw_fastener",
           min_gap=-0.0002, max_gap=0.0002)
```

A **frame-to-frame** gap check, tolerance **±0.2 mm** around zero — two visuals of
one part. No collision is computed, no allowance is needed.

> **Correction (MECHANICAL_PRIORS §1c was rewritten after this section was
> written).** The *topology* reference above stands — a retainer that belongs to
> the host part costs nothing. The **knife-edge fit does not**: §1c now declares
> exact part-to-part tangency fragile, because CadQuery's `union` can leave
> tangent solids separate, triangulation can open at the seam, and the
> connectivity check's tolerance is `1e-6`. Anywhere two *different* parts must
> read as connected, the rebuild uses a deliberate overlap along the contact
> normal instead of a zero-distance kiss. It is invisible to the overlap gate:
> `geometry_qc.find_geometry_overlaps` (L1783-L1793) only calls `fcl.collide`
> when the AABB intersection depth exceeds `overlap_tol` on **all three** axes,
> and `overlap_tol` defaults to `1e-3` with fleet templates authoring 0.002-0.006.
> The TemplateDesign carries this as one named derived parameter,
> `contact_policy.connection_overlap_m`. Running fits — the 0.6 mm pin/bore and
> the 1.1-1.2 mm guide clearances derived from 001 — stay real gaps and are
> **not** affected. 002 uses the same trick implicitly for `side_cover` (0.002 m thick at
`y=+0.015`, half-embedded in a face at `+0.015`, L175-L192) and the two
`jaw_fastener_*` studs at `y=+0.0160` (L205-L211); 003 for `main_pivot_cap`
(`y=−0.0165`, 0.5 mm into a `−0.015` face, L209-L214).

### 9. Effort hierarchy and scale

| Joint role | Effort range | Velocity | Records |
|---|---|---|---|
| ram (squeeze) | **5200 – 9000** | 0.012 – 0.05 | 001: 9000, screw_press: 7600, 002: 5200 |
| anvil (adjust) | 1200 – 1800 | 0.006 – 0.015 | 001: 1200, 002: 1800 |
| hand lever | 180 – 420 | 1.0 – 2.0 | 002: 320, 001/003: 420, screw_press: 180 |
| compound link | 80 – 90 | 0.15 – 2.0 | 002: 90, screw_press: 80 |
| nosepiece / set | 90 | 0.015 | 003, alligator |
| latch | **2.0** | 2.5 – 4.0 | 001, 003 |

Three and a half orders of magnitude, strictly ordered ram ≫ anvil ≫ lever ≫
latch. Overall scale: frame length 0.21 m (002) to 0.35 m (001/003); tool width
0.020 m (001 plate) / 0.030 m (002, 003); lever plate 0.008 m (001), 0.0095 m
(003), 0.044 m (002).

## `allow_overlap` sites — all 13 records use it, and preflight blocks it

`allow_overlap` appears in **every record in the pool** (2-6 calls each; 41 calls
in total across the 13 `run_tests`, plus 2 more in `alligator_jaw`'s dead
`_run_parent_tests` at L524/L535). Because a Design-backed template has
`allow_overlap` **blocked in preflight**, every one of these must be re-expressed.
`ctx.allow_isolated_part(...)` remains permitted and is the intended escape for
joint-carried members.

| # | Site (record : lines) | What is overlapping | Rebuild route |
|---|---|---|---|
| 1 | 001 L486-L492 (also in all four 001-forks: compact L490, rotating L530, torsion L526, leaf L507) | `latch_wire` ↔ `latch_pin`, pin 3 mm off the hinge axis, wire `r=1.2` → **1.4 mm interference** | Copy 003's `eye_and_wire_loop_latch`: a real annular eye of ID `axle_r + 0.2 mm` centred **on** the joint origin, verified with `expect_within`, not `allow_overlap` |
| 2 | 001 L501-L507 (+ same four forks) | `latch_wire` ↔ `fixed_grip`, hook engaged around the rubber grip in the rest pose | Drop the interference. The latch is carried by its hinge (003 asserts no host contact at all); declare `ctx.allow_isolated_part(latch, …)` and keep the hook tangent at ≥ 0.3 mm |
| 3 | 002 L444-L453 (deep_c L462, toggle L477, cam L502, screw L460) | `adjuster_collar` (`r=0.0100`) ↔ `forged_frame`; `expect_gap` demands **−0.0065 … −0.0050**, i.e. 5-6.5 mm *inside* the jaw | Cut a real counterbore of `collar_r + 0.5 mm` into the jaw underside in `_frame_shape`, and shorten the collar so it seats in it with 0.3 mm radial and 0.2 mm axial clearance |
| 4 | 002 L464-L473 (deep_c L482, toggle L497, cam L522, screw L480) | `fixed_handle_body` ↔ `upper_mount_pin`, **1.3 mm interference** | Move the mount pin's visual onto `fixed_handle` (it is a FIXED child anyway, L252-L258) — or better, merge the fixed handle into the frame part entirely, since a FIXED joint buys nothing. §1c then makes the capture free |
| 5 | 002 L481-L490 (deep_c L499, toggle L514, cam L539) | `squeeze_lever_body` ↔ `main_pivot_pin`, **zero clearance** | Apply the §1 rule: pin moves onto `squeeze_lever`, frame bore = lever bore + 0.4 mm |
| 6 | 002 L498-L507 (deep_c L516, toggle L531, cam L572) | `ram_shaft` (`r=0.0052`) ↔ upper bore (`r=0.0052`) | `bore_r = shaft_r + 1.2 mm` per 001 |
| 7 | 002 L524-L533 (deep_c L542, toggle L557, cam L598) | `compound_link_plate` ↔ `linkage_pin`, zero clearance | Pin visual moves onto `compound_link`; the lever's clevis bore is cut `+0.4 mm` |
| 8 | toggle L574-L583 | `compound_link_plate` ↔ `ram_toggle_pin`, −0.05 mm "modeled press-fit" | Same as #7 on the ram end. Note the link then touches *neither* pin's host — declare `allow_isolated_part(compound_link)` |
| 9 | 003 L507-L517 (quick_change L565, alligator L739) | `barrel_shell` (ID 7.2) ↔ `nosepiece_shell` collar (`r=9.0`) | Collar `r ≤ 6.4 mm`, or enlarge the tube ID to `collar_r + 0.8 mm`. Since the barrel is a frame visual, the *cleanest* route is to union it into `_frame_shape` and cut the receiver bore there |
| 10 | 003 L518-L528 (quick_change L576, alligator L759) | `main_pivot_shaft` (`r=5.8`) ↔ `lever_core` bore (`r=5.6`), −0.2 mm | Same as #5 |
| 11 | alligator L749-L757 | `body_shell` ↔ `nosepiece_shell`, the set passing through the forged jaw tip | Cut the through-bore in the jaw at `set_r + 1.0 mm` — the record simply never cut it |
| 12 | screw_press L497-L506 | `screw_drive_hub` register ↔ `forged_frame`, `max_penetration=0.0035` | Cut the 3.5 mm counterbore in `_frame_shape` for real; the hub then drops in with a 0.2 mm axial gap |
| 13 | screw_press L517-L527 | `press_screw` thread crests (`r=0.0050`) ↔ bore (`r=0.0052`) | Bore to `crest_r + 1.1 mm`, i.e. 6.1 mm |
| 14 | screw_press L563-L577 | `bar_bushing` (`r=0.0042`) ↔ `screw_drive_hub` tommy bore (`r=0.0042`) | Bushing `r=0.0036` in a 0.0042 bore (0.6 mm, 001's number) |

Everything reduces to three moves: **(a)** put the pin visual on the part whose
bore is tightest and give the *other* part real clearance; **(b)** cut counterbores
and through-bores that the source asserted but never machined; **(c)** use
`allow_isolated_part` for members whose only support is their joint — the lever,
the compound link and the latch. There is no site in this pool that genuinely
requires `allow_overlap`.

## Deliberate deviation — one welded solid per die stack

`sdk/_core/v0/exact_collisions.py:94-118` derives **one collision solid per
visual**, 1:1. The pool's die stacks are built from loose primitives:

| Part | Visual count | Record |
|---|---|---|
| `squeeze_ram` | **9** (screw + 7 thread crests + die) | `screw_press` L343-L362 |
| `anvil_screw` | **13** (stem + 8 thread crests + 4 turnings) | `screw_press` L386-L423 |
| `ram` / `adjustment_die` | 4 + 4 | 001 L349-L417 |
| `anvil_screw` | 5 | 002 L380-L410 |

Every crest ring is concentric with and embedded in the shaft it decorates. That
is legal — all of it is intra-part (§1c) — but it turns two 15 mm parts into 22
collision solids, and 22 embedded solids per part is exactly the construction that
made the lighthouse category the fleet's only Genesis failure.

**The pool already contains the better route.** `_rotating_set_holder_shape`
(L220-L249) unions three turnings and cuts a socket into **one** CadQuery solid
emitted as **one** visual, and `_nosepiece_shape` (003 L52-L77) does the same for
shank ∪ collar ∪ tip − bore. The grip ribs in 001 (L178-L185) and its moving grip
(L209-L216) are likewise `.union()`ed into the grip solid rather than stacked as
boxes.

The rebuild uses the welded route for **every** die, set holder, anvil and screw:
thread crests become a lathed groove profile in the same solid. This changes *how*
the source's stacks are emitted, not what they look like, and it is the
construction 3 of the pool's own helpers already use.

## Folded into continuous parameters rather than candidates

Per `VISUAL_DIVERSITY_MODEL.md`, pure proportion changes are not candidates.

| Parameter | Unit | Source range | Evidence |
|---|---|---|---|
| `die_station_x` (throat depth) | m | **0.065 – 0.124** | compact `−0.065` (L113/L120/L383/L427), 001 `−0.102`, 002 & deep_c `−0.124`. Note `long_c_yoke_throat` lengthens the frame to `x=−0.160` **without** moving the station, so frame nose and station are two parameters, not one |
| `open_die_gap` | m | **0.004 – 0.013** | 001 L618-L627, 002 L610-L619 |
| `ram_travel` | m | derived = `open_die_gap − closing_residual` | 001 0.0040, 002 0.011 |
| `anvil_adjust_range` | m | ±0.003 – ±0.004 | 001 L428-L429, 002 L421-L422 |
| `lever_travel` | rad | **0.035 – 0.42** | alligator 2° (L331), 001 0.15, 002 14°, 003 24°. Coupled to the frame candidate: `alligator_jaw` needs the short arc because the handle *is* the jaw |
| `tool_width` | m | 0.020 – 0.030 | 001 `_plate_from_profile(…, 20)`, 002 `_side_extrusion(…, 0.030)`, 003 `_front_plate(…, 30.0)` |
| `lever_plate_width` | m | 0.008 – 0.044 | 001 L147, 003 L248, 002 L230/L276 |
| `grip_rib_count` | count | 6 | 001 L178, L209 — decoration density, explicitly **not** a candidate or an N axis |
| `thread_crest_count` | count | 7 (ram) / 8 (anvil) | screw_press L352-L358, L393-L399 — likewise decoration |

`long_c_yoke_throat` is kept as a **candidate** rather than a parameter of
`throated_forged_body` because the throat profile goes 5 → 13 points and the
`side_cover` changes topology (full-body cover → heel-only cheek that no longer
bridges the throat). `compact_straight_head` is kept as a candidate because it
re-derives the die station and inverts its author test from a lower bound to an
upper bound. Both clear the "part tree or major geometric form" bar in
`VISUAL_DIVERSITY_MODEL.md`; the throat *depth* alone would not.

## Multiplicity (N)

**There is no repeated-part axis in this pool, and none should be invented.**

Every one of the 13 records has exactly **two** dies — one upper, one lower — and
that count is load-bearing for the category identity (anchor 3). No record has a
second lever, a second link, a turret of sets, or an indexed jaw. The only
index-general loops in the entire pool are decorative surface features on a single
welded or single part:

* 001 L178 / L209 — 6 grip ribs, `.union()`ed into the grip solid;
* 002 L205-L211 — 2 jaw fastener studs, both visuals on the frame;
* `screw_press` L352-L358 / L393-L399 — 7 and 8 thread crests;
* `screw_press` L317-L323 — 2 tommy-bar end knobs (a fixed pair, not an N).

Per `VISUAL_DIVERSITY_MODEL.md` decoration density does not enter core or raw, and
N must not be used to inflate the domain. The template should declare **no
multiplicity slot**. `raw_domain == core_domain` here, and that is the honest
number: 5 frames × 5 mechanisms × 4 head modules × 4 returns × 3 locks = 1200
combinations from structure alone.

## Category anchors

1. **One grounded root `frame` part** carrying the fixed grip and both die bores.
   13/13 records: `root_parts() == ["frame"]` is asserted explicitly in 002
   (L547-L553) and 003 (L447-L451).
2. **Exactly one hand lever** with a `REVOLUTE` joint parented to the frame, axis
   `(0,±1,0)`, `lower == 0.0` (all 13), `upper ∈ [0.03, 0.45]` rad.
3. **Two opposed die/set parts sharing one squeeze axis.** Their prismatic joint
   origins must agree in `x` and `y` to **0.5 mm**
   (`expect_origin_distance(axes="xy", max_dist=0.0005)`, 001 L611-L617) or overlap
   ≥ 8 mm in plan (002 L601-L609). This is the invariant that separates a squeezer
   from the `must_not_become` blind riveter, which has one die.
4. **Upper die = `PRISMATIC` child of the frame along the squeeze axis**, travel
   0.004-0.011 m, carrying `meta["mechanical_driver"]` naming the lever joint
   (002 L373, checked at L574-L580). **Lower die = a second `PRISMATIC` child**
   with a bidirectional range (`lower < 0 < upper`, 001 L576-L577).
5. **The squeeze stroke really closes the gap**: at `ram_joint.upper` the tip gap
   must fall to ≤ 6 mm with penetration ≤ 0.2 mm (001 L651-L660, 002 L645-L654),
   and coaxiality must survive the anvil's full adjustment (002 L678-L686).
6. **Closed handles never touch**: grip gap ∈ [0.5, 5.0] mm at full lever travel
   (001 L638-L647, 002 L664), with ≥ 25 mm of grip motion (001 L661-L670).
7. **Effort ordering** `ram > anvil > lever > latch`, spanning ~9000 → 2.0. A flat
   effort constant cannot drive a 9 kN squeeze and a 2 N·m wire latch from the same
   number.
8. **Not a blind riveter**: no single-die head, and no prismatic member whose
   travel points *away* from an opposed die along a horizontal barrel. 003 is the
   pool's own negative example and `alligator_jaw` its correction.
9. **Every revolute is about `±Y`** except the `screw_press` drive head, which is
   about the squeeze axis (L288) — a candidate-scoped exception, declared, not an
   escape hatch.

## Review ledger

Every one of the 13 records was opened and read in full — origins line by line,
variants as complete unified diffs against the parent established by diff size —
before deciding what each contributes. Records that back no candidate still get a
verdict here, so "not cited" is a stated judgement rather than an unread gap.

| Record | Depth | Verdict |
|---|---|---|
| `…__001__png_2ba6198e…` | full | **Candidate ×4 + the pool's only clean mating numbers**: `deep_c_yoke_forging`, `hidden_internal_toggle`, `stepped_cylinder_dies`, `wire_extension_spring`, `wire_hook_latch`. The **only** record whose pivot pin and both guide bores need no `allow_overlap` — it owns the `pin_r = bore_r − 0.6`, `bore_r = shaft_r + 1.2` and `ram_travel = open_gap` rules |
| `…__002__png_7a78c071…` | full | **Candidate ×3 + the frame convention**: `throated_forged_body`, `dogbone_mimic_link`, `plain_die_pair`. Supplies the fork-slot stand-off (`frame_width + 2 mm`), the 13 mm open gap with a 2 mm closing residual, and the `Mimic` coupling idiom. Also the worst offender: 5 `allow_overlap` calls, four of them zero-clearance |
| `…__003__png_7c15724d…` | full | **Rejected as a frame** (self-declared pop-rivet gun, L86-L89) but **candidate ×1**: `eye_and_wire_loop_latch` — and it is the pool's single most valuable construction, a 2.2 mm eye on a 2.0 mm axle verified by `expect_within` with **no allowance** (L546-L554). Also gives the 1.25 mm outboard lever stand-off and a genuinely cut lever relief slot (L129-L135) |
| `…_var_yoke_frame_deep_c_yoke` | full diff (97) | **Candidate**: `long_c_yoke_throat`. Throat 5→13 points, outer 8→12, `side_cover` retopologised to a heel cheek. Proves frame nose and die station are independent parameters — the station stayed at `−0.124` |
| `…_var_yoke_frame_alligator_jaw` | full diff (376) | **Candidate**: `alligator_jaw` — the only record where the lower die rides the moving member, and the corrective proof that 003's mechanism can be re-axised into a real squeezer (`rpy=(0,−π/2,0)` at L357, travel 24°→2°). Carries a dead `_run_parent_tests` (L444-L673) that the live `run_tests` (L675+) shadows; only the live one counts |
| `…_var_yoke_frame_compact_straight_head` | full diff (48) | **Candidate**: `compact_straight_head`. Smallest diff in the pool but a real structural one — it re-derives both prismatic joint origins with the jaw geometry and asserts their equality to `1e-9` (L614-L625), which is where the `die_station_x` single-parameter rule comes from |
| `…_var_squeeze_mechanism_compound_toggle` | full diff (97) | **Candidate**: `long_toggle_cheek`. Computed-normal web geometry, and the first link in the pool that actually terminates on the ram. Adds a 6th `allow_overlap` |
| `…_var_squeeze_mechanism_eccentric_cam_lever` | full diff (107) | **Candidate**: `eccentric_cam`. The only candidate that grows a **reaction structure on a different part** (bracket + bridge on `fixed_handle`), which is why the fixed handle cannot simply be merged into the frame for this candidate — noted against rebuild route #4 |
| `…_var_squeeze_mechanism_screw_press` | full diff (298) | **Candidate**: `screw_press`. Changes joint *types* (revolute→about-Z, link revolute→prismatic) and effort, not just shape — the strongest ② candidate in the pool. Also the worst collision-count offender (9 + 13 visuals on two small parts) and the source of the `lead_m_per_turn` idiom |
| `…_var_head_module_quick_change_yoke` | full diff (62) | **Candidate**: `quick_change_yoke_clip`, **and** the pool's only demonstration of same-part tangent seating: `expect_gap(frame, frame, axis="y", ±0.0002)` at L528-L537. That check is the template for replacing every allowance in section #8 |
| `…_var_head_module_rotating_set_holder` | full diff (79) | **Candidate**: `rotating_set_holder`, and the pool's reference **welded-solid** construction — three turnings unioned and a socket cut into one CadQuery body, one visual. This is the deviation route recommended for all die stacks |
| `…_var_return_torsion_handle_spring` | full diff (97) | **Candidate**: `torsion_handle_spring`. Procedurally generated 2.25-turn, 34-sample helix with axial advance. The **only** spring in the pool with a real cross-part clearance problem (1.7 mm to the moving handle plate) — an assembly number that appears in no other record |
| `…_var_return_leaf_return_spring` | full diff (67) | **Candidate**: `leaf_return_spring`. Reuses the parent's own `_plate_from_profile` at 1.6 mm to make a genuine bowed leaf, and its author test's `y-extent ≤ 0.002` bound is what keeps it a leaf rather than a bar |

**What the ledger changed.** Three findings came only from records that back no
frame or mechanism candidate. 003 — rejected as a frame — supplies the single
construction that makes the whole `allow_overlap` removal possible. `quick_change_yoke`,
a 62-line diff, supplies the frame-to-frame tangent gap check. `torsion_handle_spring`
supplies the only cross-part spring clearance in the pool. Deciding what to read
from the candidate list alone would have missed all three, and the rebuild would
have run into the `allow_overlap` block with no source-attested way out.

**One caution the pool cannot answer.** The source author tests are much lighter
than the template checks — they lean on `allow_overlap` precisely *because*
`fail_if_parts_overlap_*` was never run against them. A construction being
source-attested here does not mean it survives
`fail_if_parts_overlap_in_sampled_poses`; 41 of the pool's own assertions are
declarations that it would not.

## Resolving the 003 rejection

The first draft rejected origin 003 while accepting two candidates forked from
it. That was inconsistent as stated, because it leaned on 003's `run_notes`
self-description (L86-L89) rather than on a structural feature. Resolved here in
favour of **keeping the rejection, but scoping it to the host frame and naming the
disqualifier structurally**. An authoring comment is evidence of intent, not of
geometry; the geometry has to carry the argument on its own.

### The disqualifying feature, stated structurally

003 is out of category for exactly one reason, and it is not the comment:

> **There is no second, opposed die.** 003 has a single prismatic member
> (`nosepiece`, L324-L349) whose travel axis `(−1,0,0)` points *outward* along a
> horizontal barrel with nothing facing it. Category anchor 3 — two die parts on
> one shared axis, coaxial to 0.5 mm — cannot be evaluated at all, because there
> is only one die.

Three independent structural facts confirm this rather than restate it:

1. **Part tree.** `{frame, lever, nosepiece, latch}` (asserted at L453-L457).
   There is no ram/anvil pair. Compare 001 `{frame, moving_handle, ram,
   adjustment_die, grip_latch}` (L523-L534) and 002's 6 parts (L547-L553).
2. **Absent assertion.** 003 contains **no** `expect_origin_distance(axes="xy")`
   and no `expect_overlap(axes="xy")` between two dies — the assertion that both
   other origins make (001 L611-L617, 002 L601-L609) and that three of the forks
   restate. It cannot make it; there is no pair.
3. **Inverted geometry test.** 003 L588-L594 asserts
   `nose_box[0][0] < body_box[0][0] − 0.025` — the nose must *project past* the
   head. A squeezer asserts the opposite topology: the working axis lies *inside*
   a throat, between two beams (002's throat cut L65-L77, 001's ram/die bores
   L108-L121).

That is the `must_not_become` signature — a mandrel-pulling nose, not a
compression throat. The rejection stands, and `compact_gun_head` is carried in the
manifest as an explicit `rejected` row so the judgement is recorded rather than
silently omitted.

### Why `alligator_jaw` does not inherit it

The fork removes the disqualifying feature outright, at four identifiable diff
hunks. It is the largest diff in the pool (376 changed lines) precisely because
this is a mechanism change, not a reskin:

| What changes | Lines in the fork | Effect on the disqualifier |
|---|---|---|
| **A second, opposed die is created** | L299-L306 — `circle(5.0).extrude(17.0).translate((0,0,−25.0))` is unioned into `moving_grip_shape` | The missing lower rivet set now exists. This is the whole rejection, undone |
| **The work axis is verticalised** | L200 and L357 — receiver and joint re-origined `(-0.081,0,0.307) → (-0.145,0.021,0.329)` with `rpy=(0,−π/2,0)`; local `−X` travel maps to world `−Z` | The set now travels *toward* its opposite number instead of outward |
| **The barrel becomes a throat** | L102-L128 — frame outline 22 → 25 points, nose `x −52 → −170 mm`, forming a long upper jaw over the new lower jaw | The "nose projects past the head" topology is replaced by a jaw pair |
| **The pair is asserted** | L749-L757 — `"opposed rivet sets align at the alligator jaw tip"`: `moving_box[0][0] < nose_box[0][0] < moving_box[1][0]` plus Y-interval overlap | Anchor 3 becomes evaluable and is evaluated |

Supporting changes are consistent with a squeezer and inconsistent with a puller:
lever travel collapses `24° → 2°` (L331, `qc_samples` L432) because the handle now
*is* the jaw and a 24° arc would drive the jaws through each other; the lower jaw
changes material `black_rubber → dark_steel` (L314) because it is now structure,
not a grip; and the fork replaces `run_tests` wholesale (L675+) rather than
patching it, retiring the parent's pop-rivet assertions into a dead
`_run_parent_tests` (L444-L673) that nothing calls.

So `alligator_jaw` is accepted **on its own geometry**, not on its parentage.

### Why the two component excerpts do not inherit it

`quick_change_yoke_clip` and `eye_and_wire_loop_latch` are a different case, and it
should be said plainly: **neither fork removes the disqualifier.**
`head_module_quick_change_yoke` is a 62-line diff that changes one visual and adds
two tests; it is still, as a whole object, a pop-rivet gun. Accepting these is
therefore a **component-level acceptance from a host-level rejection**, and it is
only sound under a stated rule:

> A component may be excerpted from an out-of-category record **iff** the
> disqualifying feature is host-level and the component's own geometry, mating
> and joint semantics do not depend on it.

Checked against each:

* **`quick_change_yoke_clip`** (`_quick_change_yoke_shape` L80-L107, visual
  L254-L264, seating check L528-L537). A 28-line self-contained CAD helper
  producing a stamped horseshoe in the XZ plane, plus one frame visual and one
  **frame-to-frame** `expect_gap(axis="y", ±0.0002)`. It references no die, no die
  count, no prismatic axis and no joint. It is a *set-retention scheme* — a clip
  that captures a set from the side instead of a machined shoulder — and it seats
  by tangent contact against a cheek face, which every frame candidate has. Drop
  it onto `deep_c_yoke_forging` and nothing about it needs to change.
* **`eye_and_wire_loop_latch`** (part L352-L390, axle L392-L412). A handle lock:
  an annular eye on a frame-mounted axle with a `(0,−1,0)` hinge at the *heel of
  the fixed grip* (`x=−0.062, z=0.055`), far from the head. Its geometry is
  entirely determined by the grip pair, which 003 shares with 001 and 002. It is
  also the pool's only allowance-free rotary capture (2.2 mm eye ID over a 2.0 mm
  axle, `expect_within` at L546-L554), which is why discarding it would cost the
  rebuild a construction it has no substitute for.

The negative control matters as much as the positive: 003's `nosepiece`
(`_nosepiece_shape` L52-L77) and its `barrel_shell` (L188-L199) are **not**
excerpted, precisely because they *are* the disqualifying feature — a single die
in an outward-facing barrel. They enter this SourceMap only as `allow_overlap`
sites #9 and #11 to be removed, and only in `alligator_jaw`'s re-axised form.

### What this means for the manifest

`compact_gun_head` appears as a `rejected` row. `alligator_jaw`,
`quick_change_yoke_clip` and `eye_and_wire_loop_latch` appear as `accepted` rows,
the first on its own reworked geometry and the latter two under the excerpt rule
above. 003 remains in `sync_records` — it is read, cited for mechanism numbers,
and is the pool's own negative example for anchor 8.

## Accepted candidate manifest (machine-readable)

| slot | candidate | diversity axis | source type | record/revision | exact model.py:Lx-Ly | key parts/joints/helpers | status |
|---|---|---|---|---|---|---|---|
| yoke_frame | deep_c_yoke_forging | ① silhouette / built-up jaw beams | grounded frame forging | rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586/rev_000001 | model.py:L38-L122 | `_plate_from_profile` 18-point XZ profile ±10 mm; upper/lower jaw beams unioned as rect+circle boss; four cut bores (fixture r8, pivot r7.2, ram r6.4x58, die r5.6x42) at station x=-102 mm; one welded solid, one visual | accepted |
| yoke_frame | throated_forged_body | ① silhouette / cut throat | grounded frame forging | rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83/rev_000001 | model.py:L49-L100 | `_side_extrusion` 8-point outer, fillet 4 mm; 5-point throat 0.050 m wide cut through a 0.030 m body; stopped bores r0.0052 and r0.0072 at x=-0.124; pivot cuts r0.0054 and r0.0042 | accepted |
| yoke_frame | long_c_yoke_throat | ① silhouette / throat topology | grounded frame forging | rec_0611_rivet_squeeze_var_yoke_frame_deep_c_yoke/rev_000001 | model.py:L49-L114, model.py:L189-L211 | outer 8 to 12 points (nose x=-0.160), throat 5 to 13 points, fillet 3 to 2 mm; `side_cover` retopologised 7 to 11 points into a heel-only cheek; die station unchanged at x=-0.124 | accepted |
| yoke_frame | compact_straight_head | ① silhouette / jaw proportion and station | grounded frame forging | rec_0611_rivet_squeeze_var_yoke_frame_compact_straight_head/rev_000001 | model.py:L38-L125 | jaw beams rect(96,30) to rect(52,30) and rect(76,22) to rect(48,24), bosses pulled in; both die bores and both PRISMATIC joint origins re-derived x -0.102 to -0.065 | accepted |
| yoke_frame | alligator_jaw | ① silhouette / long upper jaw with a vertical receiver | grounded frame forging | rec_0611_rivet_squeeze_var_yoke_frame_alligator_jaw/rev_000001 | model.py:L102-L147, model.py:L193-L203, model.py:L352-L365 | frame outline 22 to 25 points, upper jaw reaching x=-170 mm; receiver re-origined to (-0.145,0.021,0.329) with rpy=(0,-pi/2,0) so the set travel maps to world -Z. The record's swinging lower jaw is NOT part of this row — see slot-decomposition note below | accepted |
| yoke_frame | compact_gun_head | ① silhouette / single-die head | grounded frame casting | rec_picturex_0611__rivet_squeeze__003__png_7c15724dd1fc4e4a9c3ba1c34794454c/rev_000001 | model.py:L102-L144 | 22-point casting, cut lever slot 70x105x12.5, pivot bore r6.5, horizontal `_axis_x_tube(10.5,7.2,34.0)` barrel | rejected — single die on an outward horizontal axis with no opposed member; breaks anchors 3 and 8 and is the `must_not_become` blind-riveter signature |
| squeeze_mechanism | hidden_internal_toggle | ② joint set / coupling | ram drive layer | rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586/rev_000001 | model.py:L349-L391 | one PRISMATIC `frame_to_ram`, no link part; effort 9000, velocity 0.025, travel 0 to 0.0040 m; `meta["mechanism_note"]` declares the toggle hidden inside the frame | accepted |
| squeeze_mechanism | dogbone_mimic_link | ② joint set / coupling | ram drive layer | rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83/rev_000001 | model.py:L125-L140, model.py:L315-L340 | `_linkage_shape` 5-point dog-bone 0.004 m on the outer cheek, two r0.0032 eyes; `compound_link` REVOLUTE child of the lever with `Mimic(multiplier=-0.70)`; ram coupled by `mechanical_driver` meta | accepted |
| squeeze_mechanism | long_toggle_cheek | ② joint set / coupling | ram drive layer | rec_0611_rivet_squeeze_var_squeeze_mechanism_compound_toggle/rev_000001 | model.py:L125-L158, model.py:L339-L360, model.py:L373-L384 | computed-normal web from (0,0) to (-0.196,0.033) with r0.008 end bosses and r0.00315 bores; ram grows `ram_head` Box(0.018,0.020,0.008) and `ram_toggle_pin` r0.0032x0.062; Mimic -0.70 to +0.65 | accepted |
| squeeze_mechanism | eccentric_cam | ② joint set / coupling plus host reaction structure | ram drive layer | rec_0611_rivet_squeeze_var_squeeze_mechanism_eccentric_cam_lever/rev_000001 | model.py:L254-L284, model.py:L330-L339, model.py:L409-L414 | r0.018 lobe offset (0.009,0.003) with r0.0056 axis bore; `cam_reaction_bracket` 6-point + r0.007 reaction pin + Box bridge on `fixed_handle`; `cam_follower_head` r0.008 on the ram; Mimic -0.55 | accepted |
| squeeze_mechanism | screw_press | ② joint types and axes | ram drive layer | rec_0611_rivet_squeeze_var_squeeze_mechanism_screw_press/rev_000001 | model.py:L262-L280, model.py:L282-L299, model.py:L304-L338, model.py:L343-L362 | drive hub circle(0.014)x0.018 with r0.010 register, r0.0042 tommy bore, r0.0075 keying boss; lever joint moves to the die station, axis (0,0,-1), 0 to 180 deg; link becomes PRISMATIC ±0.025 m sliding tommy bar; ram effort 7600, `lead_m_per_turn` 0.00175 | accepted |
| squeeze_mechanism | direct_jaw_lever | ② joint set / the handle IS the moving jaw, no ram at all | ram drive layer | rec_0611_rivet_squeeze_var_yoke_frame_alligator_jaw/rev_000001 | model.py:L261-L316, model.py:L318-L337 | `lever` carries a 23-point long lower jaw 12 mm thick in `dark_steel` with a `circle(5.0).extrude(17.0)` lower rivet set unioned in at x=-172 mm; REVOLUTE about (0,1,0) at (0.027,0.021,0.300), travel 0 to 2 deg, effort 420; there is no ram and no compound link, so the squeeze reaches the work directly through the handle | accepted |
| head_module | stepped_cylinder_dies | ③ stacked-turning form | opposed die pair | rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586/rev_000001 | model.py:L349-L373, model.py:L393-L417 | four cylinders per part; ram shaft r0.0052x0.052, holder r0.0080, tip r0.0035, cap r0.0080; anvil shank r0.0045x0.042, adjuster wheel r0.0080, holder r0.0075, tip r0.0035; identical r0.0035 opposed tips | accepted |
| head_module | plain_die_pair | ③ minimal turned form | opposed die pair | rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83/rev_000001 | model.py:L345-L357, model.py:L380-L410 | ram = shaft r0.0052x0.035 + die r0.0062x0.012; anvil = stem r0.0047x0.075, die r0.0060, knurled adjuster r0.0072x0.044, stop r0.0090, collar r0.0100 | accepted |
| head_module | rotating_set_holder | ③ faceted hand-turnable socket | opposed die pair | rec_0611_rivet_squeeze_var_head_module_rotating_set_holder/rev_000001 | model.py:L220-L249, model.py:L388-L399, model.py:L444-L455 | `_rotating_set_holder_shape(height_mm)` unions circle(5.6)x1.2 land, polygon(12,16.8) collar, circle(6.2)x0.8 land and cuts a circle(3.55)x1.7 blind socket into ONE solid, ONE visual; called at h=5.0 upper and h=4.0 lower | accepted |
| head_module | quick_change_yoke_clip | ③ set form plus retention topology | opposed die pair with clip retention | rec_0611_rivet_squeeze_var_head_module_quick_change_yoke/rev_000001 | model.py:L52-L77, model.py:L80-L107, model.py:L254-L264 | `_nosepiece_shape` supplies the set form itself (shank r6.2 union collar r9.0 union tip r4.5 minus bore r1.8, one welded solid); `_quick_change_yoke_shape` circle(7.2)/circle(3.3) annulus ±1.5 minus a rect(10,3.8) release slot opening to -X, plus a pierced rect(6,5) thumb tab; seats tangent to the frame cheek at y=-0.0165, verified frame-to-frame at L528-L537 | accepted |
| return_element | wire_extension_spring | ③ spring form family | return element | rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586/rev_000001 | model.py:L262-L281 | `tube_from_spline_points` over 7 zig-zag points, radius 0.0012, 6 samples/segment, 12 radial segments, capped; a visual on the frame so its 0.2 mm cheek embed is intra-part and free | accepted |
| return_element | leaf_return_spring | ③ spring form family | return element | rec_0611_rivet_squeeze_var_return_leaf_return_spring/rev_000001 | model.py:L220-L245, model.py:L291-L302 | `_leaf_return_spring_shape` 17-point closed profile extruded to 1.6 mm via the parent `_plate_from_profile`; broad clamped tang, bowed lower end; author test bounds y-extent <= 0.002 | accepted |
| return_element | torsion_handle_spring | ③ spring form family | return element | rec_0611_rivet_squeeze_var_return_torsion_handle_spring/rev_000001 | model.py:L220-L261, model.py:L308-L315 | procedural helix, coil_radius 0.0115 about the pivot, start 225 deg, 2.25 turns, 34 samples with axial advance in Y, plus 3+3 formed reaction-leg points, tubed at radius 0.00115; 1.7 mm clearance to the moving handle plate | accepted |
| return_element | no_return_element | ③ spring form family (source-attested absence) | return element | rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83/rev_000001 | model.py:L166-L211 | the complete frame visual list — `forged_frame`, `side_cover`, `main_pivot_pin`, `upper_mount_pin`, two `jaw_fastener_*` — contains no spring; 2 of 3 origins are built this way | accepted |
| handle_lock | wire_hook_latch | ③ joint count / capture topology | handle lock | rec_picturex_0611__rivet_squeeze__001__png_2ba6198e3af4438abc2a873af2483586/rev_000001 | model.py:L323-L331, model.py:L434-L467 | 5-point open spline tubed at r0.0012, 10 samples/segment, 14 radial; REVOLUTE `handle_to_latch` parented to the MOVING HANDLE, axis (0,1,0), limits -0.05 to 1.10, effort 2.0; host pin r0.0032 sits 3 mm off the hinge axis | accepted |
| handle_lock | eye_and_wire_loop_latch | ③ joint count / capture topology | handle lock | rec_picturex_0611__rivet_squeeze__003__png_7c15724dd1fc4e4a9c3ba1c34794454c/rev_000001 | model.py:L352-L390, model.py:L392-L412 | annular eye circle(4.5)/circle(2.2) ±2.0 rotated onto Y plus a closed 8-point wire loop at r0.0011; REVOLUTE parented to the frame at the grip heel, 0 to 78 deg; axle r0.0020 gives 0.2 mm radial clearance verified by `expect_within` with NO allowance | accepted |
| handle_lock | no_handle_lock | ③ joint count / capture topology (source-attested absence) | handle lock | rec_picturex_0611__rivet_squeeze__002__png_7a78c071827541ed822cff3fb676aa83/rev_000001 | model.py:L547-L553 | `"single connected hierarchy"` asserts exactly 6 parts rooted at `frame` — `frame`, `fixed_handle`, `squeeze_lever`, `compound_link`, `squeeze_ram`, `anvil_screw` — with no latch among them | accepted |

## Slot-decomposition correction (phase B)

Filling the TemplateDesign forced two corrections to the slot boundaries drawn
above. `TemplateDomain` has no compatibility gates — every declared combination
must build — so a combination that cannot build is a decomposition error, not a
reason for a gate. Both are recorded here rather than fixed silently.

**1. `alligator_jaw` was carrying two slots' worth of structure.**

As first written it bundled the long upper-jaw frame *and* the swinging lower jaw
that carries the lower rivet set. That made `alligator_jaw × screw_press`
unbuildable: `screw_press` replaces the hand lever with a rotating drive head at
the die station (L282-L299), so there is no swinging member left to carry the
lower set, and the combination would have had one die.

The source shows why the bundling happened, and that it is not intrinsic: the fork
welds its lower set into `moving_grip` (L299-L306) **because its parent 003 has no
anvil part at all** — 003's tree is `{frame, lever, nosepiece, latch}`. The
001 and 002 families both carry a separate lower-die part, so "the lower die rides
the moving member" is a property of the *drive layer*, not of the jaw silhouette.

Split accordingly: `yoke_frame.alligator_jaw` keeps the frame (L102-L147, L193-L203,
L352-L365), and the swinging jaw becomes a sixth `squeeze_mechanism` candidate,
`direct_jaw_lever` (L261-L316, L318-L337). That is also the cleanest ② axis in the
set — the five drive layers now read as *hidden toggle / visible link / long toggle
/ cam / screw / none at all, the handle is the jaw*. Every combination builds:
`alligator_jaw × direct_jaw_lever` is the source object; `long_c_yoke_throat ×
direct_jaw_lever` is a C-yoke with a swinging lower jaw; `alligator_jaw ×
screw_press` is a screw press under a long upper jaw with a normal anvil in the
throat.

**2. `quick_change_yoke_clip` was a retainer with no die.**

Slot C is the die-pair form, but this candidate as first cited was only the
horseshoe clip (L80-L107) — under it, the seed would have had a retainer and no
set. Its own record supplies the missing half: `_nosepiece_shape` (L52-L77) is a
real welded set form (shank ∪ collar ∪ tip − through bore). The row now cites both,
so every Slot C candidate is homogeneous: a set-pair form plus its retention
scheme, machined shoulder for three of them and a spring clip for this one.

**Result.** `core_domain` = 5 yoke_frame × 6 squeeze_mechanism × 4 head_module ×
4 return_element × 3 handle_lock = **1440**, and `raw_domain` = 1440 (no
multiplicity). All 1440 must build; the four cross-slot risks that remain are
resolved by derivation in the TemplateDesign bindings, not by exclusion.
