# Modular Spec — Industrial / Mine cart

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Mine_cart` |
| template path | `agent/templates/Industrial_Mine_cart.py` |
| test path (optional) | `tests/agent/test_Industrial_Mine_cart_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root chassis + parallel-children tip/latch/wheels + 2 multiplicity axes) |
| function stem | `industrial_mine_cart` (exports `build_industrial_mine_cart`, `config_from_seed`, `run_industrial_mine_cart_tests`) |

`pattern = mixed`: a single root `chassis` (riveted iron frame on the track) carries
three parallel-children slots that each parent their own articulations directly to
the chassis (no serial chain joint): `tip_mechanism` (emits the tipping/hoisting
load `tub` + the defining joint), `latch` (emits the release hook/bolt + the end
hoop), and `wheels` (N rolling wheelsets). Two multiplicity axes ride on top:
`wheelset_count` (2 or 3 axles) and `strap_band_count` (2 or 4 wrap bands). The
tub Primary-Form family (`tub_form`) and the wheel form (`wheel_form`) are ③ axes
consumed by their emitting factories and reported in `slot_choices`, exactly as
`Urban_Environment_Tipping_Barrow` reports `tub_shape`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_a-rusty-iron-chaldron-style-mine-cart-on-four-bl_...c584b5ab` — ORIGIN 母本
  (riveted iron chassis, curved flared lofted chaldron tub on transverse-Y REVOLUTE
  tip, gravity latch hook on end hoop, 2 spoked wheelsets = 4 wheels).
- `rec_mine_cart_var_form_box_tub` — ③ tub form: upright rectangular riveted iron box.
- `rec_mine_cart_var_form_trapezoid_tub` — ③ tub form: flat-panel trapezoidal V-tipper (Kipplore).
- `rec_mine_cart_var_form_ubucket_tub` — ③ tub form: half-cylinder U-section rolled trough skip.
- `rec_mine_cart_var_form_disc_wheels` — ③ wheel form: solid cast disc plate wheel (vs open spokes).
- `rec_mine_cart_var_joint_prismatic_lift` — ② tip joint: REVOLUTE tip -> PRISMATIC vertical hoist on guide columns.
- `rec_mine_cart_var_joint_slide_bolt_latch` — ② latch joint: gravity hook REVOLUTE -> sliding bolt PRISMATIC.
- `rec_mine_cart_var_mult_strap_bands_four` — ④ multiplicity: 2 -> 4 wrap-around strap bands.
- `rec_mine_cart_var_mult_wheelsets_three` — ① multiplicity: 2 -> 3 rolling wheelsets (6 wheels).
- `rec_mine_cart_var_skel_side_tip_mount` — ① skeleton: transverse end-tip -> longitudinal side-tip (pivot along +Y rail, dumps over +Y).
- `rec_mine_cart_var_skel_tailgate_door` — ① skeleton: add a hinged end-discharge door (REVOLUTE, child of tub) at the +X dump lip.

## 核心身份

An **industrial mine cart / rail skip / tipping tramway wagon**: a low riveted-iron
**chassis** rolling on the track on flanged **wheelsets** (2 or 3 axles, each a
transverse axle + two rail wheels on an always-on CONTINUOUS roll), carrying a
sheet-metal / cast-iron **tub** load body that **dumps its ore** — either by
**tipping** about a REVOLUTE trunnion (end-tip over the +X lip, or side-tip over
the +Y lip) or by a **vertical PRISMATIC skip-hoist** up guide columns. The
identity feature is the raised **end hoop** carrying a **release mechanism**
(gravity latch hook that swings, or a sliding bolt that draws back) that retains
the tub until discharge; some skips add a hinged **tailgate door** at the dump
lip. At least one real non-fixed joint is always present (the wheels' CONTINUOUS
roll plus the tip/hoist joint). Default mature domain: ~1.5 m chaldron/box/skip
body, 4 wheels, gravity-latched end-tip.

Not to be confused with **Industrial / Mine cart track**, a **hand truck /
sack barrow** (no tub-tip joint, no rail wheelsets), a **wheelbarrow /
tipping barrow** (single/large pneumatic wheel, garden bowl — that is the
neighbouring `Urban_Environment_Tipping_Barrow`), or an open **rail flatcar /
gondola** with no tipping/hoist DOF.

## 槽位 + 候选模块表

### Slot A：chassis (root)

The riveted iron frame that grounds the cart and provides every mount datum. Single
candidate (root, like `Urban_Environment_Tipping_Barrow` `frame_body` and
`Urban_Environment_Tipping_Barrow` root). Same part tree regardless of downstream picks: two side
frame beams + two end frame beams + center plank(s) + 2 saddle bolsters + 4 raked
cradle braces + N*2 axleboxes + 4 buffer blocks/heads (all fused as `chassis`
part visuals, Rule 1). Tip-mount hardware (trunnion bolster+brackets+pin OR guide
columns) and latch hardware (hoop+keeper) are added onto the chassis by the tip /
latch factories so they stay orientation-consistent (Contract 3c: the chassis
exposes shared datums `axle_z`, `deck_top`, `pivot`/`column` points single-sourced
in `ResolvedConfig`).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `frame` | forked_anchor (origin) | `rec_a-...c584b5ab` | L199-L313 | eligible (root) | riveted iron chassis: side/end beams, planks, saddle bolsters, cradle braces, axleboxes, buffers. |

`cradle_brace_{0..3}` (origin L221-L232) are raked braces carrying the tub cradle
back into the headstocks. Their height is **derived per X side** from the tipping
tub's swept floor envelope: the trunnion sits only ~35 mm under the tub floor, so on
the discharge side the leading floor corner drops well below the deck (worst case the
full-length `ubucket`/`box` base). `_cradle_brace_z` scans the tip range and places
the pair under that minimum, or omits that pair when the swept band leaves no room.

Single-candidate root (allowed, matches Tipping_Barrow). All topology diversity is
carried by Slots B/C/D + the ③/multiplicity axes.

### Slot B：tip_mechanism (parallel child of chassis · ① skeleton + ② joint + ③ `tub_form`)

Owns the load `tub` part, the defining tip/hoist joint, and the chassis-side mount
hardware. The ③ `tub_form` axis selects the shell prototype (chaldron / box /
trapezoid / ubucket) independent of the tip topology, and the ③ `rim_profile` axis
selects the rim realization on the curved chaldron shell (`saddle` = the origin
母本's longitudinal rim cut, `flat` = the level rim of the flat-panel sources).

`hoist_lift` carries the two guide columns on ONE transverse `guide_bearer` posted
down onto both side beams outboard of the wheel faces, plus a `guide_head_cap` at
each crown; the column height is derived as `slider_top + lift_travel + head`. Bare
columns rising off thin outriggers read as two loose poles floating beside the frame,
which is the same failure mode as the rod-and-crossbar hoop (see Slot C).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `end_tip` | forked_anchor (origin) | `rec_a-...c584b5ab` | L241-L260, L315-L373 | eligible | tub tips forward about a **transverse-Y REVOLUTE** trunnion at +X; chassis gets trunnion bolster + brackets + pin; tub gets 2 pivot lugs + catch lug. Dumps over +X. |
| `side_tip` | forked_anchor | `rec_mine_cart_var_skel_side_tip_mount` | L52-L55, L246-L269, L366-L420 | eligible | ① skeleton change: tub tips sideways about a **longitudinal-X REVOLUTE** pin on the +Y side bearer; chassis gets a longitudinal bolster + brackets + long pin; tub lugs + catch lug on the +Y/-Y side. Dumps over +Y. |
| `hoist_lift` | forked_anchor | `rec_mine_cart_var_joint_prismatic_lift` | L241-L277, L333-L391 | eligible | ② joint change: tub rides **vertical-Z PRISMATIC** guide columns (skip hoist); chassis gets 2 guide columns + outriggers + crossbrace + gussets; tub gets 2 slider blocks wrapping the columns. Lifts straight up. |

### Slot C：latch (parallel child of chassis · ② joint + identity end hoop)

The identity feature: the raised end hoop + a release mechanism retaining the tub.
Oriented per the resolved `discharge` datum (end vs side) set by Slot B.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `gravity_hook` | forked_anchor (origin) | `rec_a-...c584b5ab` | L289-L313, L375-L398 | eligible | end hoop + mount plate + hinge ears + latch pin on chassis; latch part = hook_bar + toe on a **REVOLUTE** hinge (axis Y for end, X for side) that swings the toe clear of the tub catch lug. |
| `sliding_bolt` | forked_anchor | `rec_mine_cart_var_joint_slide_bolt_latch` | L307-L329, L391-L416 | eligible | end hoop + guide keeper + bolt guide rails on chassis; latch part = bolt_bar + head on a **PRISMATIC** slide (axis -X) that draws the bolt back out of the catch lug. |

`sliding_bolt` gated to `discharge == "end"` (the horizontal bolt reads on the
transverse -X end hoop; on side-tip the -Y side latch is a swinging hook). When
`side_tip` is picked, `latch` resolves to `gravity_hook`.

**Hoop primitive (identity, source-faithful).** Both sources cut `latch_hoop` as ONE
flat iron plate — a rounded-top outer rectangle minus a rounded-top inner rectangle,
extruded 35 mm — i.e. a U-shaped stirrup with two straight legs standing on the frame
beam (S1 `build_hoop` L129-L147, S10 L133-L151). Substituting two thin rods plus a
crossbar violates MECHANICAL_PRIORS §1 (characteristic profile) and reads, on the
`side_tip` skeleton in particular, as a stray length of **railway track** floating
across the middle of the deck rather than a stirrup arch. The template therefore
builds `_arch_plate_mesh` and:

- the end plate laps the -X end beam, legs sunk `HOOP_FOOT_EMBED` into it;
- the side plate stands outboard of the widest station it reaches **and** of the
  catch lug proud of that wall, carried back onto the side beam by `hoop_mount_{i}`;
- the end crown is trimmed to the last station clearing the plate's inner face, so a
  long low chaldron flaring past the frame end is not buried in the tub wall;
- `latch_mount_plate` / `bolt_mount_bracket` bridge the crown (resp. the end beam)
  down to `latch_pivot`, then `latch_hinge_ear_{i}` + `latch_pin`, or `guide_keeper`
  + `bolt_guide_rail_{i}`.

**Release engagement.** `latch_engage_z` is single-sourced (`DECK_TOP + 0.25`, the
S7 `BOLT_ORIGIN` height) and drives both the `catch_lug` height and the length of
the release member: `_release_reach` sizes `latch_toe` / `bolt_bar` from the realized
shell datum so the release really holds the lug at rest and draws clear when opened
(previously the toe hung ~200 mm below a lug it never touched). The bolt's nose also
satisfies `>= bolt_travel - keeper/2`, so it stays captured in the keeper at full
retraction instead of becoming an isolated part.

### Slot D：wheels (parallel children of chassis · ① multiplicity `wheelset_count` + ③ `wheel_form`)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `two_wheelsets` | forked_anchor (origin) | `rec_a-...c584b5ab` | L400-L434 | eligible | 2 wheelset parts (each = transverse axle + 2 rail wheels), CONTINUOUS roll (axis Y) parented to chassis, at x=+/-AXLE_X. |
| `three_wheelsets` | forked_anchor | `rec_mine_cart_var_mult_wheelsets_three` | L39, L216-L269, L412-L433 | eligible | ① multiplicity: 3 wheelset parts at x in (-0.46, 0, 0.46); chassis grows a middle axlebox pair + inter-axle cross planks. Three axles ride on smaller wheels (radius capped at 0.215) so the trio fits the short frame without wheel-wheel or wheel-to-end-beam overlap. |

### Slot E：track (new ROOT when present · ① skeleton + ② joint)

The narrow-gauge road the cart stands on. `none` keeps the current topology (chassis
is the root, wheels ride the ground plane z=0). Any other candidate emits a
`rail_track` part that **becomes the model root** and parents the chassis through a
`cart_travel` PRISMATIC joint, lifting the whole cart by the profile's derived
`rail_top` so the wheel treads are seated on the rail heads.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor (origin) | `rec_a-...c584b5ab` | L36-L607 | eligible | no track part; chassis is the root; `axle_z = wheel_radius` (ground contact). The origin 母本 and all 9 forked variants are cartless-of-track, so this stays the seed-0 anchor. |
| `sleeper_rail` | forked_anchor | `rec_a-dark-riveted-steel-mine-cart-a-tipping-trapezo_...6e20849c` | L35-L41, L154-L185, L250-L258 | eligible | 7+ wooden sleepers + two flat-bottom I-rails built as foot/web/head layers; `rail_top = 0.165`. |
| `steel_tie` | world_knowledge_extrapolation | — | — | eligible | pressed-steel ties under a light flat-bottom rail (foot + head, no tall web); `rail_top = 0.110`. |
| `stringer_strap` | world_knowledge_extrapolation | — | — | eligible | early tramway road: longitudinal timber stringers carrying a flat iron strap rail, sparse transverse ties holding gauge; `rail_top = 0.146`. |

`rail_top` is derived from each profile's layer stack, so the track type also sets the
cart's ride height. Gauge is derived from the template's own `WHEEL_Y`, NOT copied
from the source's 0.275 half-gauge.

### Slot F：track_shape (dependent slot · only exists when `track != none`)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `straight` | forked_anchor | `rec_a-dark-...6e20849c` | L154-L185 | eligible | source layout: ties on one line, rails as straight bars. |
| `curved` | world_knowledge_extrapolation | — | — | eligible | same section laid on an arc; ties fan out radially, rails sweep as one continuous swept-bar mesh each. The cart sits at the arc MIDPOINT where the tangent is +X, so the cart itself is unchanged and the track sweeps away from it in both directions. |

When `track == none`, `track_shape` is reported as `n/a` in `slot_choices` (the slot
does not exist), and `resolve_config` collapses it internally to `straight`.

**Curved radius is derived, not chosen.** A mine cart's wheelsets are rigid and square
to the frame (no steering bogie), so on a curve the rail walks sideways out from under
the tread by `station^2 / 2R`. `resolve_config` picks
`R = clamp(track_len / TRACK_ARC_SPAN, 3.0, 6.0)` and then shortens `cart_travel` to
`sqrt(2 * TRACK_RAIL_SEAT * R) - max|axle_x|`, so the OUTERMOST wheel still rides its
rail head at every pose the travel joint can reach. `_expect_track` asserts that
inequality directly. Radial (steered) wheelset placement was rejected: yawing a
wheelset swings its rim into the side frame beams.

`wheel_form ∈ {spoked, disc}` (③) is a per-wheel geometry axis: `spoked` uses
`WheelSpokes` (origin L406), `disc` uses `WheelFace` cast web
(`rec_mine_cart_var_form_disc_wheels` L406-L408). Same wheel part tree; only the
`WheelGeometry` sub-spec changes (Rule 3-compliant: still a `WheelGeometry` mesh).

硬约束满足：每个多候选 slot 结构不同 candidate（B=3, C=2, D=2, E=4, F=2）+ ③
`tub_form` 4 prototypes + ③ `rim_profile` 2 + ③ `wheel_form` 2。root chassis 单
candidate（allowed）。

**外推记录（2026-07-30，用户显式批准）**：Slot E 的 `steel_tie` / `stringer_strap` 与
Slot F 的 `curved` 是 `world_knowledge_extrapolation`——小类源池 12 条 record 中只有
`rec_a-dark-...6e20849c` 一条带轨道，且只有直轨一种铺法。其余候选全部 source-backed。
这三个外推候选不改变类别身份（仍是站在窄轨上的矿车），只扩展轨道这一件配景的形态；
如果后续为 `Industrial / Mine cart track` 生成了真实源资产，应回来把它们改挂 source。

## 槽位图（slot graph）

pattern: `mixed` (root chassis + parallel children + 2 multiplicity)

```
rail_track (root when track != none; sleepers/stringers + rails)
   └─[cart_travel PRISMATIC(X tangent); wheel treads seated on the rail heads]-> chassis
chassis (root when track == none; riveted iron frame)
   ├─[+X trunnion REVOLUTE(Y) | +Y bolster REVOLUTE(X) | guide-column PRISMATIC(Z); captured pin/slider]-> tip_mechanism (tub, N strap bands, optional tailgate)
   ├─[-X end hoop REVOLUTE(Y/X) | -X keeper PRISMATIC(-X); captured hinge pin / keeper]-> latch          (hook or bolt)
   └─[axle CONTINUOUS(Y); axle journal in axlebox]-> wheels                                              (x N wheelsets)
```

- **slot 顺序 / parent**：`chassis` is the root and only reused parent. `tip_mechanism`,
  `latch`, `wheels` each parent their own `model.articulation(parent=chassis, ...)`;
  each declares only a `downstream` interface (re-export chassis) and NO `upstream`,
  so `assemble(..., selection_mode="anchor_choices")` emits no auto chain joint (each
  module emits its raw joint, matching all 5-star sources and the Tipping_Barrow idiom).
- **接口点位**：tip -> chassis trunnion/pin at world `TIP_PIVOT` (end: (0.45,0,0.62);
  side: (0,0.44,0.62)) or guide columns at x=0.45, y=+/-0.60; latch -> chassis end
  hoop at -X (`LATCH_PIVOT` (-0.79,0,0.94)) or -Y side; wheels -> axleboxes at
  (x, 0, axle_z), x per wheelset.
- **跨 slot joint type/axis/range**：tip REVOLUTE(Y or X, [0, tip_upper<=0.7]) |
  PRISMATIC(Z, [0, lift_travel<=0.55]); latch REVOLUTE(Y or X, [0, latch_range<=1.1])
  | PRISMATIC(-X, [0, bolt_travel<=0.20]); wheels CONTINUOUS(Y).
- **互斥/派生**：`sliding_bolt` requires `discharge=="end"` (else forced
  `gravity_hook`); `tailgate` (① end door) requires `end_tip` AND `tub_form ∈
  {box, trapezoid}` (flat +X end wall to seat against); `tub_form` and `wheel_form`
  are orthogonal to every other axis.

## 每槽位 Module Emits / Interfaces

### Slot A / module frame (root)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (single root part) | origin L200 |
| visuals | `side_frame_beam_{0,1}` + `end_frame_beam_{0,1}` + `center/cross_plank*` + `saddle_bolster_{0,1}` + `cradle_brace_{0..3}` + `axlebox_{0..2N-1}` + `buffer_block/head_{0..3}` | origin L202-L288 |
| internal joints | none (root) | — |
| downstream interface | `chassis` part, `center_cross_plank` visual, face `positive_z`, anchor `(0,0,deck_top)` (informational; children wire manually) | — |

### Slot B / module end_tip | side_tip | hoist_lift
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tub` (+ optional `end_door` for tailgate) | origin L316; tailgate L399 |
| visuals (tub) | `tub_shell` (lofted mesh per tub_form) + `strap_band_{i}` xN + `rim_rivets` + `band_rivets_{i}` + pivot lugs / slider blocks + `catch_lug`; chassis-side hardware appended (`trunnion_bolster`/`trunnion_bracket_{i}`/`tip_pivot_pin` OR `guide_column_{i}`/`guide_outrigger_{i}`/`guide_crossbrace`/`guide_base_bracket_{i}`) | origin L242-L362; lift L241-L370; side L246-L376 |
| internal joints | `tub_tip` REVOLUTE(Y|X) OR `tub_lift` PRISMATIC(Z); (tailgate) `door_hinge` REVOLUTE(Y) parent=tub | origin L364-L373; lift L383-L391; tailgate L465-L473 |
| upstream interface | **none declared** (parallel child; parents to `chassis`) | — |
| downstream interface | re-export chassis (passthrough) | — |

### Slot C / module gravity_hook | sliding_bolt
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch_hook` (hook or bolt part) | origin L376 |
| visuals (latch) | hook: `hook_bar` + `latch_toe`; bolt: `bolt_bar` + `bolt_head`; chassis-side: `latch_hoop` + (`latch_mount_plate`+`latch_hinge_ear_{i}`+`latch_pin`) OR (`bolt_mount_bracket`+`guide_keeper`+`bolt_guide_rail_{i}`) | origin L289-L313, L377-L388; bolt L307-L406 |
| internal joints | `latch_pivot` REVOLUTE(Y|X) OR PRISMATIC(-X) parent=chassis | origin L389-L398; bolt L409-L416 |
| upstream interface | **none declared** | — |
| downstream interface | re-export chassis (passthrough) | — |

### Slot D / module two_wheelsets | three_wheelsets
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheelset_{0..N-1}` (each = axle + 2 wheels) | origin L411 |
| visuals | `axle` + `wheel_{0,1}` (WheelGeometry mesh; spoked or disc web) | origin L412-L425 |
| internal joints | `wheelset_{i}_roll` CONTINUOUS(Y) parent=chassis | origin L426-L434 |
| upstream interface | **none declared** | — |
| downstream interface | re-export chassis (passthrough) | — |

活动件语义：tip/lift joint dumps/hoists the load; latch joint releases; wheels roll.
不动细节（beams/bolsters/rivets/hoop/strap bands）写成宿主 part visual，非独立 part
（Rule 1）。captured trunnion-pin-in-lug / slider-on-column / hinge-pin-in-hook /
axle-in-axlebox 用 element-scoped allow_overlap（Rule 2 例外）；REVOLUTE/CONTINUOUS
joint 原点落在真实 hardware（pin/axle）几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `tip_mechanism` | enum | end_tip / side_tip / hoist_lift | end_tip | choice | procedural sampler | Slot B |
| `tub_form` | enum | chaldron / box / trapezoid / ubucket | chaldron | choice | procedural sampler | ③ (origin+3 form variants) |
| `rim_profile` | enum | flat / saddle | saddle | conditional | `saddle` only for `tub_form == "chaldron"`; the flat-panel prototypes keep the level rim their own sources use | ③ (origin L36-L47/L76-L79/L107 saddle cut; S2/S3/S4 level rims) |
| `saddle_radius` | float | derived | — | equation | arc through `(+/-half_len, tub_top_z)` and `(0, tub_top_z - dip)`; `dip = min(nominal, 0.55*(tub_top_z - mid_station))` and `nominal` reproduces the source R=1.6 cut at nominal scale | derived |
| `rim_min_z` | float | derived | — | equation | `= tub_top_z - dip` (`== tub_top_z` when flat); caps strap-band placement so bands stay on the wall | derived |
| `latch_engage_z` | float | derived | 0.75 | equation | `= DECK_TOP + 0.25` (S7 `BOLT_ORIGIN` height); drives the `catch_lug` height and `_release_reach` | derived |
| `hoop_plane` / `hoop_top` | float | derived | — | inequality | side plate stands clear of `max(shell half-width over the leg span, lug outer face)`; end crown trimmed to the last station clearing the plate's inner face | derived |
| `latch_module` | enum | gravity_hook / sliding_bolt | gravity_hook | conditional | sliding_bolt only if discharge==end; else gravity_hook | Slot C |
| `wheel_module` | enum | two_wheelsets / three_wheelsets | two_wheelsets | choice | procedural sampler | Slot D |
| `wheel_form` | enum | spoked / disc | spoked | choice | procedural sampler | ③ (origin, disc_wheels) |
| `track_module` | enum | none / sleeper_rail / stringer_strap / steel_tie | none | choice | weighted {none:0.42, sleeper_rail:0.26, stringer_strap:0.16, steel_tie:0.16} | Slot E |
| `track_shape` | enum | straight / curved | straight | conditional | slot only exists when `track_module != "none"`; else reported `n/a` | Slot F |
| `cart_travel` | float | [0.18, 0.30] | 0.24 | conditional | PRISMATIC travel per side; 0.0 without a track; on a curve re-solved to `sqrt(2*TRACK_RAIL_SEAT*R) - max|axle_x|` | S12 L250-L258 |
| `rail_top` | float | derived | — | equation | sum of the chosen profile's tie/stringer/rail layer heights; lifts the whole cart so treads seat on the rail heads | Slot E |
| `track_len` | float | derived | — | equation | `= 2*(CART_HALF_LEN + cart_travel + TRACK_END_MARGIN)`, so the cart never runs off the rail ends | Slot E |
| `track_radius` | float | derived | — | inequality | `clamp(track_len / TRACK_ARC_SPAN, 3.0, 6.0)`; must satisfy `(max|axle_x| + cart_travel)^2 / 2R <= TRACK_RAIL_SEAT` | Slot F |
| `has_tailgate` | bool | {False, True} | False | conditional | True only if tip==end_tip and tub_form in {box, trapezoid} | tailgate variant |
| `strap_band_count` | int | {2, 4} (obs: 2 origin, 4 bands_four) | 2 | independent | weighted {2:0.6, 4:0.4}; evenly spaced over tub height | origin L324-L335, bands_four L52-L56 |
| `wheelset_count` | int | {2, 3} (derived from wheel_module) | 2 | equation | `= 2 if two_wheelsets else 3` | origin L410, wheelsets_three L39 |
| `tub_height_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; tub body height / depth | origin L43-L47 |
| `tub_len_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform, clamp; tub length + width (保形 together) | origin L58-L67 |
| `wheel_radius_scale` | float | [0.92, 1.08] | 1.0 | independent | uniform, clamp; wheel radius; axle_z = 0.24*scale (ground contact) | origin L40 |
| `axle_z` | float | derived | — | equation | `= wheel_radius = 0.24*wheel_radius_scale`, then `min(., 0.215)` for three_wheelsets (ground contact) | origin L38,L40 |
| `tip_upper` | float | [0.45, 0.70] | 0.6 | conditional | REVOLUTE tip range (rad); only for end_tip/side_tip | origin L372 |
| `lift_travel` | float | [0.35, 0.55] | 0.50 | conditional | PRISMATIC hoist range (m); only for hoist_lift | lift L384 |
| `latch_range` | float | [0.8, 1.1] | 1.0 | conditional | gravity_hook REVOLUTE range (rad) | origin L397 |
| `bolt_travel` | float | [0.14, 0.20] | 0.18 | conditional | sliding_bolt PRISMATIC range (m) | bolt L413 |
| (—) | constraint | — | — | inequality | tub half-width must clear the side beams (y=+/-0.44) at max flare; if `tub_len_scale` widens past clearance, clamp tub_len_scale | interface / clearance |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 20 s** (hang-guard `--compile-timeout 60`). NO cadquery
boolean sculpting (the 5-star sources use cadquery loft/cut; the template reproduces
the SAME lofted-shell / half-cylinder primitive family via hand-built `MeshGeometry`
lofts — Rule 3 preserves the primitive family, not the construction tool, exactly as
`Urban_Environment_Tipping_Barrow._lofted_tub_mesh`). Geometry cost: one tub-shell
loft mesh (<=28-seg rounded-rect rings x 2-3 stations, or a <=24-seg half-cylinder
arc) + rivet spheres (10-seg) merged into ONE mesh per row + 2N wheel meshes sharing
ONE `WheelGeometry` mesh. Tessellation tiers: rounded-rect corner segments <=8,
half-cylinder arc <=24, rivet sphere 10x8, wheel spokes/face default. Expect 3-8
s/seed; downgrade seg counts first if over.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 — `wheelset_count`（滚动轮对数）
- `count_param`: `wheelset_count`; `N_range` product `{2,3}`, test `{2,3}`; sampling
  domain 由 `wheel_module` enum 决定（`two_wheelsets`=2 weight 0.6, `three_wheelsets`=3 weight 0.4，小 N 偏多）。
- copied object: whole `wheelset_i` part (axle + 2 wheels) + its `wheelset_i_roll`
  CONTINUOUS joint + chassis `axlebox_{2i,2i+1}`. N=3 adds inter-axle cross planks.
- naming: `wheelset_{i}` / `wheelset_{i}_roll` / `axlebox_{2i}`,`axlebox_{2i+1}`.
  placement: even along X — N=2 at x=+/-AXLE_X; N=3 at x in (-0.46,0,0.46) on wheels capped to radius 0.215. joint policy:
  per-wheelset CONTINUOUS roll axis Y.
- source/gating: origin (N=2) L410-L434, wheelsets_three (N=3) L39,L412-L433.
- N 不改主体机制（tub/tip 不变）。

### 轴 2 — `strap_band_count`（缠绕铁箍数）
- `count_param`: `strap_band_count`; `N_range` `{2,4}`, test `{2,4}`; sampling domain
  加权 `{2:0.6, 4:0.4}`。
- copied object: `strap_band_{i}` thin ring band wrapping the tub shell + `band_rivets_{i}`
  rivet row on each band (④ decoration; host-derived — each band and its rivets sample
  the shell surface at the band's z, so they hug chaldron/box/trapezoid/ubucket walls).
- naming: `strap_band_{i}` / `band_rivets_{i}`. placement: evenly spaced over the tub
  body height. joint policy: none (fused tub visuals, Rule 1).
- source/gating: origin (N=2) L324-L335, bands_four (N=4) L52-L56,L331-L352. ubucket
  bands wrap the half-cylinder (host-derived radius), not the box walls.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | tip skeleton: end-tip 2-part (origin) / side-tip longitudinal pivot (skel_side_tip_mount) / hoist_lift guide-column slider (joint_prismatic_lift); optional tailgate adds a `end_door` REVOLUTE part (skel_tailgate_door, part count 4->5). multiplicity: wheelset_count {2,3} (wheelsets_three). 全部 forked_anchor/source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：wheelset_count {2,3}（origin/wheelsets_three），strap_band_count {2,4}（origin/bands_four）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | tip REVOLUTE(Y/X)（origin/side） ↔ PRISMATIC(Z)（prismatic_lift）; latch REVOLUTE(Y/X)（origin） ↔ PRISMATIC(-X)（slide_bolt_latch）; wheels CONTINUOUS(Y)（origin, always）。全部 forked_anchor；每种类型在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **tub_form (registered in slot_choices)**: chaldron 曲面外扩 lofted（origin, Volumetric Envelope Form）/ box 直壁矩形（form_box_tub, Planar Boundary Form）/ trapezoid 平板梯形 V-tipper（form_trapezoid_tub, Planar Boundary Form）/ ubucket 半圆滚制槽（form_ubucket_tub, Macro Surface Construction）。**rim_profile (registered in slot_choices)**: saddle 纵向马鞍口沿（origin 母本 `rim_z`/`_saddle_cutter`，中部下凹、两端上扬，改变 tub 最显眼的上缘轮廓与俯视口宽）/ flat 水平口沿（S2/S3/S4 平板系源）；gated 到 chaldron。**wheel_form**: spoked open web（origin, Macro Surface Construction）/ disc solid cast plate（form_disc_wheels, Planar Boundary Form）。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `strap_band_{i}` wrap bands（数量档 {2,4}）+ `rim_rivets` + `band_rivets_{i}` iron rivet studs + buffers/hoop hardware。host-conformal：每根 band 与 rivet 行由宿主 shell 表面在该 z 逐-z 派生半径/半宽（随 ③ tub_form 与 ⑤ 缩放共形），source_type=record_only（origin/bands_four）。派生顺序 ③ tub_form -> ⑤ scale -> ④ bands/rivets。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：tub_height_scale[0.90,1.15]、tub_len_scale[0.90,1.12]、wheel_radius_scale[0.92,1.08]。关节运动包络（每个非-continuous joint）：tip REVOLUTE axis Y(end)/X(side)，open 单向 raise，[闭合 0, 可行 tip_upper<=0.70]；hoist PRISMATIC axis Z，[0, lift_travel<=0.55] m；latch REVOLUTE axis Y/X [0, latch_range<=1.1] / bolt PRISMATIC axis -X [0, bolt_travel<=0.20]；door_hinge REVOLUTE axis Y [0, 1.2]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；targeted `ctx.pose` — tip 抬升 catch_lug（end 升 z / side 升 far-side）、hoist 竖直升 tub、latch 摆/抽 toe/bolt 离开 lug、door 摆开。wheels CONTINUOUS 采 {0,+/-90,180}。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal/painted；配色 >=5 colorway：`rust_iron`（默认，铁锈体+黑铁件）、`weathered_steel`、`painted_green`、`coal_black`、`galvanized`、`oxide_red`。材质大类覆盖 >= ceil(0.5x6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 chaldron/box/trapezoid/ubucket 四种 tub、
flat/saddle 两种口沿、spoked/disc 两种轮、end/side/hoist 三种 tip、hook/bolt 两种
latch、2/3 轮对、2/4 铁箍、材质配色多样、tip/hoist/latch/door 全程不穿模。
另须确认 `latch_hoop` 在任何 tip skeleton 下都读作立在车架横梁上的单片马镫拱，而不是
悬在车斗中间的一段「铁轨」；`hoist_lift` 的导柱须坐在横承梁上并带柱帽。轨道 seed 还须
肉眼确认：轮踏面**压在轨顶**（不悬空也不陷进去）、轨距对准轮平面、弯轨从车下向两侧扫开
而车仍停在弧的切点上、三种轨型（木枕工字轨 / 钢枕轻轨 / 纵梁条铁轨）互相可辨。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- tip(3) x tub_form(4) x rim_profile(<=2) x latch(<=2) x wheel_module(2) x wheel_form(2)
  x track(4) x track_shape(<=2) x bands(2) x tailgate(<=2)。
  Gated: rim_profile=2 only for chaldron (other forms force flat); latch=2 only when end/hoist
  (side forces 1); track_shape=2 only when track != none (1/4 of the track domain has none);
  tailgate=2 only for end_tip+box/trapezoid.
  ~ 3 x 4 x ~1.25 x ~1.7 x 2 x 2 x (1 + 3x2) x 2 x ~1.2 ~= **~1750** legal tuples，
  已远超富类别建议的 300。

理由：加入 track/track_shape 前只有 ~200，低于富类别建议的 300——真实结构词汇在此
收敛，所有样本共享同一「chassis + 可动 tub + release + 滚动轮对」cell。轨道槽位把车所
站的道路本身变成结构候选（并新增 `cart_travel` 一个自由度），组合空间随之打开。
report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 tip_mechanism、tub_form、wheel_module、wheel_form、latch（按 discharge gate）、
has_tailgate（按 gate）、strap_band_count、palette、连续 scale、rim_profile，最后抽
track_module / track_shape / cart_travel。**新轴一律追加在抽样序列末尾**，这样已存在
seed 的其余全部轴取值不变（seed 身份稳定，导出目录可原地刷新）。seed 0 pinned 到 origin
母本组合（end_tip + chaldron saddle + gravity_hook + two_wheelsets spoked, 2 bands,
rust_iron, **track=none**）作为 documented regression anchor（sparse override，其余 seed
全 procedural）。random sweep `0-15`（fast）-> `0-35`（final）-> corner。

legacy 模板没有 `TemplateDomain`，`TEMPLATE_CORNERS` 不会被 corner 阶段读取（那条路径
只对 Design-backed 模板生效），因此 track 槽位的高风险全组合改用一次显式
cross-product 扫描验收：track(4) x track_shape(2) x tip(3) x wheels(2) x tub(chaldron,
ubucket) = 96 组，全部取连续参数最大值（tub_height 1.15 / tub_len 1.12 /
wheel_radius 1.05 / tip_upper 0.70 / lift_travel 0.55 / cart_travel 0.30），96/96 通过。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 ~200
（见上），低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`tub_height_scale`、`tub_len_scale`（len+wid 保形）、
`wheel_radius_scale`（axle_z 由其派生）、`tip_upper`/`lift_travel`/`latch_range`/
`bolt_travel`（conditional joint ranges）。全部在 `resolve_config` clamp / 派生；不破坏
captured-pin/slider 接口、joint 原点、multiplicity。连续尺寸契约：先采 independent
（height/len/wheel_radius）-> equation 派生 axle_z + tub half-extents -> inequality 投影
tub 半宽不撞侧梁 -> conditional 解析 joint ranges/latch/tailgate。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 tip->tub_form->wheel->latch(gate)->tailgate(gate)->bands->scales，加权 choice | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | sliding_bolt 需 discharge==end（else gravity_hook）；tailgate 需 end_tip+box/trapezoid；tub_form/wheel_form 正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 4+ clamp 连续 scale + conditional joint ranges | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| chassis | 1 | no | no | root single-candidate (allowed, matches Tipping_Barrow) |
| tip_mechanism | 3 | yes | yes | end/side/hoist |
| latch | 2 | yes | no | hook/bolt (2 source-backed; sliding_bolt gated) |
| wheels | 2 | yes | no | two/three wheelsets |
| tub_form (③ axis) | 4 | yes | yes | chaldron/box/trapezoid/ubucket |
| rim_profile (③ axis) | 2 | yes | no | flat/saddle (source-backed; gated to chaldron) |
| track | 4 | yes | yes | none/sleeper_rail/stringer_strap/steel_tie (1 source-backed + 2 extrapolated + none) |
| track_shape | 2 | yes | no | straight/curved; dependent slot, only exists when track != none |
| wheel_form (③ axis) | 2 | yes | no | spoked/disc |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ tub_form/rim_profile/wheel_form/track/track_shape/wheelset/band/tailgate axes); `track_shape` reports `n/a` when the slot does not exist
- `_expect_track` checks: no track part AND no `cart_travel` joint when `track == none`; otherwise the track is laid on z=0, each `rail_head_{j}` runs under its own wheel plane, the rail head top IS `rail_top`, `cart_travel` is PRISMATIC along the track and keeps the cart on the rails at full stroke, and the shape slot is geometrically real (curved sweeps laterally, straight does not)
- `_expect_wheels` checks the wheelsets ride the running surface — the ground plane with no track, the rail heads (`rail_top`) with one
- `_expect_hoop_and_release` checks the hoop is ONE flat plate (thinnest span <= 2x plate thickness), stands on the frame beam at the discharge-facing end, and that the release member holds the catch lug at rest and draws clear when opened
- `_expect_rim` checks the saddle dip is real, stays above the mid station, and that the shell top matches the raised rim ends
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (sliding_bolt->end only; tailgate->end_tip+box/trapezoid; side_tip->gravity_hook) in `resolve_config`
- controlled local scales clamped; cannot break captured-pin/slider interfaces, joint origin honesty, or multiplicity
- cross-part scale dependencies (axle_z, tub half-extents, side-beam clearance) derived/projected in `resolve_config`
- captured trunnion-pin/slider/hinge-pin/axle-journal overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: tip REVOLUTE(Y/X)/PRISMATIC(Z); latch REVOLUTE(Y/X)/PRISMATIC(-X); wheels CONTINUOUS(Y); door REVOLUTE(Y)
- copied `wheelset_i` / `strap_band_i` follow naming + placement policy
- `run_industrial_mine_cart_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Tipped/lifted tub collides with the chassis or hoop at joint min/max -> shrink `tip_upper`/`lift_travel` or move the pivot/columns off the collision line.
- Tub shell island: a strap band / rivet row / pivot lug / slider block floats off the shell (constant-radius decoration on a flared/round wall) -> derive band radius + rivet half-width from the realized shell surface at that z (Rule 4).
- Slider block / pivot lug doesn't reach its guide column / trunnion pin (gap) -> extend the lug/slider out to wrap the chassis hardware (captured fit, element-scoped allow_overlap).
- side_tip latch placed on the -X end (wrong face) while the tub dumps over +Y -> orient hoop+hook per resolved `discharge`.
- Downgrading the lofted `tub_shell` / half-cylinder trough to a crude single `Box` (Rule 3 violation) -> keep the MeshGeometry loft / arc shell.
- Wheels float above z=0 or clip the side beams -> axle_z = wheel_radius (ground contact); wheels stay inboard of side beams.
- tailgate door hinged on a curved chaldron / round ubucket end (won't seat) -> gate tailgate to box/trapezoid flat +X walls.

## 与相邻类别的边界

- 不该混入：**Urban_Environment / Tipping barrow (wheelbarrow)**（园艺独轮/大充气轮翻斗车，非铁轨轮对、非 riveted 铁 chaldron/skip 身份）。
- 不该混入：**Industrial / Mine cart track**（把轨道本身当主体）。注意区别：Slot E 的轨道
  是矿车所站的**配景**，主体身份仍是车——`none` 永远是合法候选且是 seed 0 锚点，轨道
  不带任何自身自由度（唯一新增关节 `cart_travel` 描述的是车相对轨道的运动）。
- 不该混入：无翻转/提升 DOF 的开放平板 rail flatcar / gondola（缺定义关节）。
- 不该混入：hand truck / sack barrow（无 tub-tip 关节、无轨道轮对）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | (1) tub shells + trough built as hand `MeshGeometry` lofts instead of the sources' cadquery boolean loft/cut to hold the <=20 s/seed compile budget (same lofted-shell/half-cylinder primitive family; Rule 3-compliant). (2) tailgate door overlays the flat +X end wall (no boolean door-cut in the shell) and is gated to box/trapezoid forms; source cut the opening with cadquery. (3) RESOLVED 2026-07-30 — the chaldron saddle rim is now a real ③ axis (`rim_profile`): the top loft ring drops to `_rim_z(x)` and re-samples the section there, reproducing the source cylinder cut without a boolean; the straight profile runs are subdivided (`PROFILE_SIDE_SEGMENTS`) so the long rim edges actually curve instead of chording, and the rim-rivet row is sampled from the same realized ring. (4) RESOLVED 2026-07-30 — `latch_hoop` had degenerated into 2 rods + a crossbar, which read as a floating section of railway track across the deck (worst on `side_tip`) and left the release toe hanging past a lug it never touched; it is now the sources' single arch plate on the frame beam, with derived stand-off/crown trim and a derived release reach. `hoist_lift`'s guide columns likewise now stand on a posted transverse bearer with head caps instead of floating outboard. |

## 模板实现备注（可选）

- Shared datums (`axle_z`, `deck_top`, `TIP_PIVOT`/`LATCH_PIVOT`/`discharge`, tub half-extents) single-sourced in `ResolvedConfig` (Contract 3c); tip + latch factories read `discharge` so hoop/hook orientation stays consistent.
- captured trunnion-pin-in-lug / slider-on-column / hinge-pin-in-hook / axle-in-axlebox -> raw joint (no MatingContract, grandfathered) + element-scoped `allow_overlap`, matching every 5-star source (Rule 2 exception).
- all 2N wheels share ONE `WheelGeometry` mesh (spoked or disc); one tub-shell mesh; rivet rows merged into one `MeshGeometry` each -> holds the compile budget.
- tub is authored in world canonical coords then seated by `-TIP_PIVOT` (or column-base for lift) so q=0 = authored pose and the tip joint origin lies in the pivot-lug geometry (origin honesty).
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：chassis root 声明 downstream；tip/latch/wheels 只声明 downstream（re-export chassis）-> 无自动 chain joint，各模块发原始 joint 到 chassis（parallel-children，同 Tipping_Barrow）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | frame + end_tip + gravity_hook + two_wheelsets(spoked) + chaldron | `rec_a-...c584b5ab` (origin 母本) | L36-L607 | chassis part tree（含 L221-L232 cradle braces）, chaldron tub loft + REVOLUTE tip, saddle rim cut（L44-L47 `SADDLE_R`/`SADDLE_CZ`, L76-L79 `rim_z`, L107 `_saddle_cutter`）, stirrup hoop plate（L129-L147 `build_hoop`）+ latch mount plate/ears/pin（L295-L311）, gravity hook latch, spoked wheelset, 全部 test 语义 |
| S2 | B ③ | box tub | `rec_mine_cart_var_form_box_tub` | L44-L92 | upright rectangular box shell (Planar Boundary) |
| S3 | B ③ | trapezoid tub | `rec_mine_cart_var_form_trapezoid_tub` | L45-L119, L351-L359 | flat-panel V-tipper shell + catch bracket (Planar Boundary) |
| S4 | B ③ | ubucket tub | `rec_mine_cart_var_form_ubucket_tub` | L44-L124 | half-cylinder rolled trough skip (Macro Surface) |
| S5 | D ③ | disc wheel | `rec_mine_cart_var_form_disc_wheels` | L30, L406-L408 | solid cast disc plate wheel (WheelFace) |
| S6 | B ② | hoist_lift | `rec_mine_cart_var_joint_prismatic_lift` | L241-L277, L333-L391 | vertical PRISMATIC skip hoist + guide columns/slider |
| S7 | C ② | sliding_bolt | `rec_mine_cart_var_joint_slide_bolt_latch` | L52, L307-L329, L391-L416 | PRISMATIC sliding bolt latch + `bolt_mount_bracket` off the end beam + guide keeper/rails; `BOLT_ORIGIN` z=0.75 sets `latch_engage_z` |
| S12 | E ①/② | rail track + cart_travel | `rec_a-dark-riveted-steel-mine-cart-a-tipping-trapezo_20260708_085212_805612_6e20849c`（picture 001，workbench，**unrated**） | L35-L41, L154-L185, L250-L258 | `rail_track` root part（木枕 + foot/web/head 工字轨）、`cart_travel` PRISMATIC、`AXLE_Z = RAIL_TOP_Z + WHEEL_R` 轮踏面坐轨顶的竖向基准 |
| S10b | C ① | side stirrup plate | `rec_mine_cart_var_skel_side_tip_mount` | L133-L151, L299-L311 | -Y arch plate `build_hoop` + `hoop_mount_{i}` feet onto the side beam |
| S8 | B ④/mult | strap bands x4 | `rec_mine_cart_var_mult_strap_bands_four` | L52-L56, L331-L352 | strap_band_count multiplicity + per-band rivets |
| S9 | D ①/mult | 3 wheelsets | `rec_mine_cart_var_mult_wheelsets_three` | L39, L216-L269, L412-L433 | wheelset_count=3 + inter-axle planks + middle axleboxes |
| S10 | B ① | side_tip | `rec_mine_cart_var_skel_side_tip_mount` | L52-L55, L246-L269, L366-L420 | longitudinal side-tipping pivot skeleton |
| S11 | B ① | tailgate door | `rec_mine_cart_var_skel_tailgate_door` | L120-L129, L202-L214, L399-L473 | hinged end-discharge door REVOLUTE child of tub |
