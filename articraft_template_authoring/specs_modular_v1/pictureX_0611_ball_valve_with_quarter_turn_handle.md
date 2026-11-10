# Modular Spec — pictureX_0611_ball_valve_with_quarter_turn_handle

## 元信息

- slug: `pictureX_0611_ball_valve_with_quarter_turn_handle`
- template: `agent/templates/pictureX_0611_ball_valve_with_quarter_turn_handle.py`
- `__modular__ = True`
- stage: `IMPLEMENTED`
- status: `complete_visual_confirmed_2026-07-13`
- variant_gate: `confirmed_by_user_2026-07-12`
- category / subcategory: `0611` / `ball_valve_with_quarter_turn_handle`
- source map: `articraft_data/picture_expansion/template_source_maps/0611__ball_valve_with_quarter_turn_handle.md`
- geometry backend: **CadQuery** (`mesh_from_cadquery`) — mandatory; the ball bore
  and body chamber are cut/union boolean solids, never a Box/Cylinder downgrade
  (AUTHORING Rule 3).
- topology: **2 parts, 1 non-FIXED joint** — `valve_body` (grounded) →
  `body_to_rotor` REVOLUTE (axis +z, `[0, π/2]`) → `valve_rotor`. Every slot
  paints visuals onto one of these two parts; there is no serial part chain, so
  this is a flat enum-driven modular build (like the closest reference
  `pictureX_0611_butterfly_valve_with_lever_operator.py`), with `__modular__`
  reporting the per-slot picks through `slot_choices_for_seed`.

## 5 星样本阅读摘要

15 5★ sources synced at `data/records/<id>/revisions/rev_000001/model.py`
(1 origin `__001` + 12 normal forked variants + 2 compatibility probe-only records).
All share the identical helper set
(`_cylinder_x`/`_annulus_x`/`_hex_x`/`_annulus_z`/`_hex_z`/`_thread_rings_x`,
origin L21–L80) and the identical 2-part / 1-REVOLUTE topology; they differ only
in which slot geometry is present.

- **origin `__001`** (`.../__001__png__...`): the canonical inline 2-way valve.
  `valve_body` = main_body casting (sphere chamber + hex + right port, cut by a
  through-bore + spherical cavity, L119–142), `end_cap` (L146–158), raised
  `left/right_port_lip` (L161–180), stepped `left/right_threads` via
  `_thread_rings_x` (L184–203), body seams (L206–225), PTFE `seat_left/seat_right`
  (L229–248), `stem_packing`+`gland_nut`+`gland_washer` (L250–279), quarter-turn
  `stop_plate` with two lugs (L281–301), one embedded `body_fastener` (L305–316).
  `valve_rotor` = ported `ball` sphere cut by an X through-bore (L327–338),
  `stem` (L340–357), `handle_hub` (L359–370), stamped `handle_lever` polyline
  profile (L372–403), blue `grip` slot2D (L405–419), `stop_tab` (L423–437),
  `retaining_nut`+slot (L439–462). Joint `body_to_rotor` REVOLUTE axis z
  `[0, π/2]`, `qc_samples=[0, π/4, π/2]` (L464–481).
- **var_3way_lport / var_3way_tport**: add a third port along Y (added `_*_y`
  helpers L83–121) unioned+bored into `main_body`; **ball bore becomes L / T**
  (lport ball L413–415: X-partial + Y-through; tport ball L406–408: X-through +
  Y-branch). ③ ball internal_structure diversity.
- **var_angle_body**: `main_body` = central sphere + one X inlet + one Y outlet
  (L173–193) → 90° elbow; ball bore = X-channel + Y-channel meeting at center
  (L400–402). ① skeleton diversity.
- **var_flanged_ends**: `_flange_disc_x` raised-face flange with a bolt-hole loop
  `for i in range(bolt_count)` (L69–114); flanges replace threaded ports
  (L214–258); indexed `flange_bolt_hole_i` cut in a loop (L266–275). N=4 default.
- **var_flange_boltholes**: `_flange_with_bolt_holes_x` (L78–99), N=8 on a larger
  bolt circle — the multiplicity companion (gated on flanged ends).
- **var_compression_ends**: `_ferrule_x` (L69) + hex-nut/ferrule/tube-stub stack
  per side (L158–189).
- **var_hose_barb_ends**: `_barb_spigot_x` 3-ridge conical barb polyline
  (L69–117); spigots at both ports (L204–220).
- **var_solder_ends**: `_solder_cup_x` smooth slip-fit cup socket (L69–92); cups
  at both ports (L179–195).
- **var_tee_handle**: replaces the stamped lever with a Y-axis crossbar cylinder
  (`crossbar_length 0.090`, `crossbar_radius 0.006`, `crossbar_z 0.082`,
  L374–403). ③ operator family.
- **var_oval_lever**: flat elongated loop plate (annulus) on the hub, oval eye cut
  (L372–391). ③ operator family.
- **var_lockable_lever**: straight lever + a lever lug and two body-mounted
  lockout ears with padlock holes (`lockout_ear_open`/`_closed`, L307–337) +
  taller stop plate (L284). ③ operator family (lockout is a FIXED lug/ear, **not**
  a second joint).
- **var_iso5211_pad**: taller bonnet neck (L272) + circular ISO-5211 pad with
  center bore + stop lugs (L288–315) + a 4-bolt indexed pattern
  `iso_bolt_hole_i` (L318–335). Actuator body itself is NOT modeled. ① stem/mount.
- **var_stem_extension**: tall `standoff_column` annulus (`COLUMN_RISE 0.060`,
  L283–310) raising the whole handle assembly; extended stem (L371–394). ① mount.
- **var_gear_operated** (PROBE only): worm-gearbox housing + handwheel + red rim
  (L112, L409–436) replacing the direct lever. Kept **probe-only** because a
  multi-turn round handwheel drifts toward a gate-valve silhouette; the ordinary
  seed domain never samples it (see §10 / boundary §11).

Result: **≥5 sources present (15)** → proceed.

## 核心身份

A **quarter-turn ball valve**: a bored spherical ball inside a flow body, sealed
by PTFE seats, rotated **exactly ~90°** by a stem+manual lever through a packing
gland. The identity mechanism is the single `body_to_rotor` REVOLUTE
(`axis=(0,0,1)`, `lower=0`, `upper=π/2`) — real and articulate in **every** seed.

- must_keep: flow body with inlet/outlet ports; internal ported ball + PTFE
  seats; stem through a packing gland; single ~90° lever revolute.
- must_not_become: gate valve (rising stem / multi-turn round handwheel), globe
  valve, plug/tapered-cock valve, faucet/bibcock tap.

## 槽位 + 候选模块表

### Slot A — `body_form` (③ Primary Form Family + ① skeleton) — **the registered ③ slot**

Registered ③ Primary Form Family slot (recognizable body/bore prototypes;
carries the primary structural diversity, drives the ball's internal bore).

| candidate | prototype | source | key geometry (real model.py:Lx-Ly) |
|---|---|---|---|
| `inline_2way` | straight-through Volumetric Envelope | origin `__001` | main_body L119–142; ball straight X-bore L327–338 |
| `lport_3way` | 3-port L-diverter | var_3way_lport | +Y port L172–176; **L-bore ball L413–415** |
| `tport_3way` | 3-port T-diverter | var_3way_tport | +Y port L170–174; **T-bore ball L406–408** |
| `angle_body` | 90° elbow envelope | var_angle_body | bent body L173–193; **angle-bore ball L400–402** |

### Slot B — `connection_ends` (① end interface)

| candidate | source | key geometry (real model.py:Lx-Ly) | gates |
|---|---|---|---|
| `threaded` | origin `__001` | `_thread_rings_x` L69–80; port_lip L161–180 | — |
| `flanged` | var_flanged_ends | `_flange_disc_x`+bolt loop L69–114, L214–275 | **enables `flange_bolt_hole_count` N** |
| `compression` | var_compression_ends | `_ferrule_x` L69 + nut/ferrule/stub stack L158–189 | — |
| `hose_barb` | var_hose_barb_ends | `_barb_spigot_x` L69–117; spigots L204–220 | — |
| `solder` | var_solder_ends | `_solder_cup_x` L69–92; cups L179–195 | — |

### Slot C — `handle` (③ operator family)

| candidate | source | key geometry (real model.py:Lx-Ly) |
|---|---|---|
| `straight_lever` | origin `__001` | stamped polyline lever L372–403 + slot2D grip L405–419 |
| `tee_bar` | var_tee_handle | Y-axis crossbar cylinder L374–403 |
| `oval_loop` | var_oval_lever | flat loop plate + eye cut L372–391 |
| `lockable_lever` | var_lockable_lever | straight lever + lug + 2 body lockout ears L307–337 |

### Slot D — `stem_mount` (① stem/bonnet)

| candidate | source | key geometry (real model.py:Lx-Ly) |
|---|---|---|
| `integral_gland` | origin `__001` | stem_packing+gland_nut+gland_washer L250–279 |
| `iso5211_pad` | var_iso5211_pad | neck L272 + pad+lugs L288–315 + 4-bolt loop L318–335 |
| `extended_stem` | var_stem_extension | standoff column L283–310 + extended stem L371–394 |

No undocumented single-candidate slot: A=4, B=5, C=4, D=3.

## 槽位图（slot graph）

```
                 valve_body (grounded root)
        ┌────────────┬──────────────┬─────────────┐
   [A body_form]  [B ends]   [D stem_mount]   (all paint body visuals)
        │  cuts the                     provides gland_top_z ──┐
        │  ball bore                                           │ derives
        ▼                                                      ▼
   body_to_rotor REVOLUTE (axis z, [0, π/2]) ── valve_rotor ── [C handle]
                                                 (ball+stem+hub+lever…)
```

- Slots A/B/D are **parallel children of `valve_body`** (all paint the one
  grounded body). Slot C paints `valve_rotor`. A single shared quantity
  `gland_top_z` (produced by D, consumed by rotor stem length + hub_z + C) is the
  single-sourced seating height (Contract 3c).

## 每槽位 Module Emits / Interfaces

- **A `body_form`** → body visuals `main_body`,`end_cap`,seams,seats + rotor
  visual `ball` (bore cut per A). Straight/L/T/angle bore.
- **B `connection_ends`** → per-port visuals (threads+lips / flange discs +
  `flange_bolt_hole_i` / ferrule stack / barb spigots / solder cups) on `valve_body`.
- **C `handle`** → rotor visuals `handle_hub`,`handle_lever|crossbar|loop`,`grip`,
  `stop_tab`,`retaining_nut` (+ body `lockout_ear_*` when lockable).
- **D `stem_mount`** → body visuals `stem_packing`,`gland_nut`,`gland_washer`,
  `stop_plate` (+ `standoff_column`/`iso_mounting_pad`+`iso_bolt_hole_i`); sets
  `gland_top_z`.
- **joint** `body_to_rotor` REVOLUTE, `MatingContract` pinning rotor `ball`
  centered face to body `main_body` chamber face (axis-normal in contact); PTFE
  seat↔ball contact declared via element-scoped `allow_overlap` (intended seal
  compression) + `expect_contact`.

## 参数范围汇总

| field | range | basis |
|---|---|---|
| `bore_radius` | 0.0090–0.0125 | DN15–DN25 through-bore (origin 0.0100) |
| `ball_radius` | 0.0170–0.0205 | ⊃ bore; origin 0.0185 |
| `body_hex_across` | 0.052–0.062 | hex body flats; origin 0.057 |
| `lever_length` | 0.110–0.170 | ~1 hand-span; origin ~0.151 |
| `flange_bolt_hole_count` | {4,6,8,12} | multiplicity, flanged only (src 4 & 8) |
| `travel` | fixed π/2 | quarter-turn identity — **not** sampled |
| `palette_style` | 5 colorways | §8.5 ⑥ |

All continuous fields clamped/derived in `resolve_config`; `gland_top_z` derived
from `stem_mount`. `travel` is a frozen identity constant (never a diversity axis).

### 7.5 编译预算 / compile budget

**≤ 20 s/seed** (target ~12–16 s). Each seed runs ~30–45 CadQuery boolean ops at
the origin's tessellation tolerances (`tolerance≈3e-4`, `angular_tolerance≈0.06`).
The origin + all 14 variants each compile individually within the simple/normal
budget (GATE P1 all-success). Hang-guard `--compile-timeout 120` (~6× budget).

## Multiplicity / Copy Logic

- count_param: `flange_bolt_hole_count`, **gated on `connection_ends == "flanged"`**
  (threaded/compression/barb/solder bodies have no bolt circle → N is inert).
- N ∈ {4, 6, 8, 12}; sources realize N=4 (var_flanged_ends) & N=8
  (var_flange_boltholes); 6/12 are interpolated on the same even-radial loop.
- copied object `flange_bolt_hole`; naming `flange_bolt_hole_i`; placement = even
  radial spacing `angle=i*2π/N` on a fixed bolt circle; joint policy = FIXED cuts
  in `valve_body`, no new joints.
- `slot_choices_for_seed` emits `flange_bolt_hole_count` only when flanged (band:
  raw N since range is narrow).

## 视觉多样性 6 轴考察

| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | **source-backed slot** | body_form inline/L/T/angle; ends threaded/flanged/compression/barb/solder; stem_mount integral/iso/extended |
| ② joint / mechanism | fixed identity | single 90° REVOLUTE `body_to_rotor` in every seed; gear+handwheel input is PROBE-only |
| ③ primary form family | **registered slot (A + C)** | body/bore prototype straight/L/T/angle **and** operator family lever/tee/oval/lockable — both in `slot_choices` |
| ④ surface decoration | host-conformal / record_only | seams, port lips, thread rings, retaining-nut slot ride the host radius; no dedicated variant |
| ⑤ proportion / size / travel | record_only | DN15–DN25, lever hand-span, extended-stem column rise; travel fixed π/2 |
| ⑥ material / palette / finish | **`palette_style` (5)** | stainless / brass / cast-iron / PVC bodies × red/yellow/blue/black vinyl grips |

Form-dominated: the ③ Primary Form Family slot `body_form` (+ operator `handle`)
is registered into `slot_choices`; diversity is not carried by size/paint alone.

## 采样与覆盖审计

- `config_from_seed(seed)`: fully procedural incl. seed 0 (no curated table).
  `rng = random.Random(seed)`; each slot `rng.choice(...)`; N via
  `rng.choice((4,6,8,12))`; `palette_style` via `rng.choice(PALETTE_STYLES)`.
  Default seed **not** special-cased.
- `slot_choices_for_seed(seed)` → `[(body_form,·),(connection_ends,·),(handle,·),
  (stem_mount,·),(palette_style,·)]` + `(flange_bolt_hole_count, N)` when flanged.
- Coverage audit via `report.axis_realization`: confirm all 4 body_form, 5 ends,
  4 handle, 3 stem_mount, ≥3 N values, all palettes appear across 0–35.

## Validator（run_tests）

`run_..._tests(model, config)` via `TestContext`:

1. topology: exactly parts `{valve_body, valve_rotor}`, joint `body_to_rotor`
   REVOLUTE axis z, `lower==0`, `upper≈π/2`.
2. required body visuals present per slot; required rotor train
   (`ball`,`stem`,`handle_hub`,handle-op,`grip`|crossbar,`stop_tab`,`retaining_nut`).
3. slot_choices recorded for every declared slot key.
4. palette: every `.visual` material drawn from the seed's `mats` dict; grip uses
   the palette grip color.
5. seats: `allow_overlap(seat_*↔ball)` + `expect_contact` (intended seal).
6. **Rule 5**: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96)` +
   targeted `ctx.pose({body_to_rotor: π/2})` asserting the grip sweeps from
   pipe-parallel (+X) to closed (+Y) and the ball stays chamber-centered.
7. `motion_test_plan`: joint sampled at `{0, π/4, π/2}`; open=lever ∥ pipe,
   closed=lever ⟂ pipe; no closed-pose or mid-travel 穿模 (seats exempted).

## Reject cases

- Round multi-turn handwheel as the DIRECT operator → **reject** (gate-valve
  drift); only via the gear PROBE.
- Ball bore as a Box/Cylinder cut placeholder → reject (Rule 3 downgrade).
- `upper != π/2` / rising-stem prismatic → reject (identity).
- Separate articulated padlock part on lockable lever → reject (lockout is a FIXED
  lug/ear, no 2nd joint).
- `flange_bolt_hole_count` on a non-flanged body → reject (inert multiplicity).
- Full actuator body on ISO pad → reject (out of subcategory; interface only).

## 与相邻类别的边界

- vs **gate/globe valve**: no rising stem, no multi-turn round handwheel; fixed
  90° revolute. A round handwheel is probe/gated only.
- vs **plug/cock valve**: bored *sphere* (not tapered plug) + PTFE seats.
- vs **faucet/bibcock**: industrial in-line flow body with two coaxial ports and a
  packing gland, not a spout/aerator tap.

## Blocked / Excluded

- `var_gear_operated` — PROBE only, excluded from the ordinary seed domain (②
  identity risk: handwheel silhouette drifts to gate valve).
- Material-only forks (brass/PVC/red-grip) — folded into `palette_style` (⑥
  record_only), not candidate count.
- Direct round handwheel operator — blocked (identity).

## 审核记录

| item | value |
|---|---|
| sources read | 15 / 15 (≥5 ✓) |
| slots ≥2 candidates | A=4 B=5 C=4 D=3 ✓ |
| every candidate real model.py:Lx-Ly | ✓ |
| ③ slot registered in slot_choices | body_form + handle ✓ |
| compile budget declared | ≤20 s/seed ✓ |
| GATE P3 | **PASS — proceed to template** |

## Module Source Index

- inline_2way / threaded / straight_lever / integral_gland: origin `__001`
- lport_3way: var_3way_lport · tport_3way: var_3way_tport · angle_body: var_angle_body
- flanged: var_flanged_ends (+N: var_flange_boltholes) · compression:
  var_compression_ends · hose_barb: var_hose_barb_ends · solder: var_solder_ends
- tee_bar: var_tee_handle · oval_loop: var_oval_lever · lockable_lever: var_lockable_lever
- iso5211_pad: var_iso5211_pad · extended_stem: var_stem_extension
- PROBE gear_operated: var_gear_operated (excluded from seed domain)
