# washing_machine — Modular Spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `washing_machine` |
| 大类 / 小类 (picture) | `Bathroom` / `washmachine` (front-loading washing machine) |
| source-map path | `articraft_data/picture_expansion/template_source_maps/Bathroom__washmachine.md` |
| parent record_id | `rec_white-front-loading-washing-machine-with-a-pull-_20260605_154143_807145_3205b533` |
| parent picture | `picture/Bathroom/washmachine/001.png` |
| template path | `agent/templates/Bathroom_washmachine.py` |
| test path (optional) | `tests/agent/test_washing_machine_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern = parallel_children`: the cabinet `body` is the root and carries several parallel child mechanisms (drum, door, control, dispenser, optional service panel) that mate to independent faces/recesses of the same chassis. No serial chain; the only depth-1 children hang directly off `body`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | parent + all 6 converged `rec_washmachine_var_*` (all rating=5 on disk) |
| source_index_policy | only adopted module sources are indexed below |

**Shared invariant structure (identical across all 7 samples, copy-paste verbatim):**
- Object-intrinsic frame: `+X` out of FRONT face, `+Z` up, `+Y` = width (LEFT = `+Y`). Body `0.60 W × 0.60 D × 0.85 H` m; back face `x=0`, front face `x=FRONT_X=BODY_D`. (every sample L42-L46.)
- `body` (root, white enamel cube) with a cylindrical **tub cavity** bored along `+X` (`TUB_R=0.205`, floor at `TUB_BACK_X=0.205`) and a shallow door recess cut into the front face. `_body_solid()` (parent L77-L116). Inertial mass ~70 kg.
- **drum**: a CONTINUOUS root child, stainless open-front tub (`DRUM_R=0.175`) recessed inside the tub cavity, spins about the front-back `+X` axis. `_drum_mesh()` + `body_to_drum` (parent L196-L222, L297-L313). Present in ALL 7 samples, **never** an articulation-axis variable — it is fixed module structure, not a slot.
- **door**: a REVOLUTE root child, hinge on a VERTICAL (`+Z`) edge on the LEFT (`+Y`) side of the opening, swings open ~100°; mass ~3 kg. `body_to_door` axis `(0,0,1)`, range `[0, 100°]` (parent L315-L357). Present in ALL 7.
- panel inset strip across the top of the front face + a dark sunken display block (`_panel_inset()` / `_display_solid()`, parent L119-L149); four black corner feet; a `Box` service hatch bottom-right of the front face.

**Per-sample differences (the real structural axes):**
| sample | door (Slot A) | control (Slot B) | dispenser (Slot C) | base/service (Slot D) |
|---|---|---|---|---|
| parent | round porthole (BezelGeometry circle + flat tinted glass disk) | single rotary dial (KnobGeometry CONTINUOUS) + side display | pull-out drawer (PRISMATIC) | flat flush service hatch (Box visual, no joint) |
| var_square_window | rounded-square window (BezelGeometry rounded_rect gasket + rounded-square glass) | single dial (inherited) | drawer (inherited) | flush hatch (inherited) |
| var_convex_porthole | deep convex porthole (chrome ring + spherical-cap dome + latch block) | single dial (inherited) | drawer (inherited) | flush hatch (inherited) |
| var_touch_panel | round porthole (inherited) | wide touch display + 5 flush button visuals, **dial joint removed** | drawer (inherited) | flush hatch (inherited) |
| var_twin_dial | round porthole (inherited) | **two** smaller rotary dials (2 CONTINUOUS parts) + compact display | drawer (inherited) | flush hatch (inherited) |
| var_flip_lid | round porthole (inherited) | single dial (inherited) | **flip-lid tray** (inline body tray + REVOLUTE top-edge Y-hinge lid) | flush hatch (inherited) |
| var_raised_plinth | round porthole (inherited) | single dial (inherited) | drawer (inherited) | **raised plinth + REVOLUTE bottom-edge Y-hinge flip-down service panel** |

Each variant changes exactly one slot off the parent baseline — clean single-axis isolation, ideal for modular recombination.

## 核心身份

A **front-loading (drum) washing machine**: a tall white-enamel cabinet (~0.6×0.6×0.85 m) standing on the floor, with (1) a CONTINUOUS stainless **drum** spinning about the horizontal front-back axis, recessed inside a cylindrical tub cavity; (2) a large hinged **glass door/window** on the front face (REVOLUTE, vertical side hinge) covering the drum mouth; (3) a **control interface** on the top strip (rotary dial(s) and/or touch display); (4) a top-front **detergent dispenser** (pull-out drawer or flip-lid tray); and (5) a **lower base / service area** (flush panel, or raised plinth with a flip-down service hatch). Default mature domain = residential white goods, ~7–10 kg load, front porthole, top-mounted controls.

Identity anchors that must always hold: the drum is a continuous spin child recessed behind the door; the door is a side-hinged revolute window over the drum mouth; controls + dispenser live on the front/top face; the whole thing reads as a freestanding white box appliance.

## 槽位 + 候选模块表

### Slot A：front door / window module (REVOLUTE, vertical +Z side hinge on +Y)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_porthole_door | parent `rec_white-front-loading…_3205b533` | mesh L152-L193 (`_door_bezel_mesh`, `_door_glass_mesh`, `_door_hinge_leaf_mesh`); door build L315-L357 | eligible if compatible | BezelGeometry circle bezel (depth 0.060) + flat tinted glass disk (`OPENING_R*0.90`) + left hinge leaf; door part frame on hinge line, opening center at `-(OPENING_R+0.030)` in Y |
| rounded_square_window | `rec_washmachine_var_square_window_door` | mesh L160-L210 (`_door_gasket_mesh` rounded_rect, `_door_glass_mesh` rounded-square, `_door_hinge_leaf_mesh`); door build L348-L391; dims L51-L62 | eligible if compatible | BezelGeometry rounded_rect thick gasket (`GASKET_SIZE=0.370`, depth 0.060) + filleted rounded-square glass panel; window-shaped recess cut (body L101-L112); hinge at `DOOR_CY+GASKET_SIZE/2` |
| convex_porthole | `rec_washmachine_var_convex_porthole_door` | mesh L152-L271 (`_door_chrome_ring_mesh` L152-L175, `_door_porthole_glass_mesh` spherical cap L178-L236, `_door_latch_mesh` L239-L256, `_door_hinge_leaf_mesh` L259-L271); door build L394-L449 | eligible if compatible | thick chrome annular ring (depth 0.055) + deep convex spherical-cap glass dome (50 mm forward bulge) + visible latch block on `-Y` free edge; uses `allow_isolated_part(drum)` |

### Slot B：control interface (top front strip)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_dial_display | parent `rec_white-front-loading…_3205b533` | dial KnobGeometry + `body_to_dial` L359-L385; panel inset + display L119-L149 | eligible if compatible | ONE skirted rotary `dial` part, CONTINUOUS about `+X` (effort 0.5); + side dark display block. Part tree: body→dial (1 continuous joint) |
| touch_panel_buttons | `rec_washmachine_var_touch_panel_controls` | touch display `_touch_display` L149-L157 + `_button_mesh` L160-L166; wide pocket panel L127-L146; button loop L294-L301; dims L60-L70 | eligible if compatible | NO dial part/joint — wide black touch display (`DISPLAY_W=0.350`) + a row of `BUTTON_COUNT=5` flush `button_{i}` body visuals (inline, not articulated). Removes one articulation vs other Slot-B modules (intentional) |
| twin_dial_controls | `rec_washmachine_var_twin_dial_controls` | dial loop `body_to_dial_{i}` L389-L411; shared `_dial_knob_mesh` helper L269-L284; compact display L153-L161; positions L63-L74 | eligible if compatible | TWO smaller rotary `dial_{i}` parts (i=0,1), each CONTINUOUS about `+X` + compact display. Part tree: body→dial_0, body→dial_1 (2 continuous joints) |

### Slot C：detergent dispenser (top-left front)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pull_out_drawer | parent `rec_white-front-loading…_3205b533` | `_drawer_mesh` L225-L254; drawer build + `body_to_drawer` L387-L412; slot cut L106-L114 | eligible if compatible | shelled tray with 2 dividers + front plate + finger pull; PRISMATIC about `+X`, travel `DRAWER_TRAVEL=0.150`. Part tree: body→drawer (1 prismatic joint) |
| flip_lid_tray | `rec_washmachine_var_flip_lid_dispenser` | inline `dispenser_tray` (body visual) L227-L275 + L431-L439; `_dispenser_lid_mesh` L278-L298; lid part + `body_to_dispenser_lid` L441-L468; dims L65-L72 | eligible if compatible | fixed compartment tray (body visual, connected solid) + a `dispenser_lid` REVOLUTE part, top-edge horizontal `(0,-1,0)` hinge, opens 75° forward/down. Part tree: body→dispenser_lid (1 revolute joint) |

### Slot D：lower base / service panel (front lower face)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_service_panel | parent `rec_white-front-loading…_3205b533` | service hatch Box visual L276-L282; corner feet L283-L291 | eligible if compatible | small flush rectangular service hatch (`Box(0.010,0.150,0.150)`) as a non-articulated body visual on the front face, bottom-right; 4 corner feet at `z≈-0.01`. NO joint |
| raised_plinth_flip_panel | `rec_washmachine_var_raised_plinth_panel` | `_plinth_solid` L265-L284; plinth body visual + low feet L335-L346; `_service_panel_mesh` L287-L312; service panel part + `body_to_panel` L469-L490; dims L74-L82 | eligible if compatible | raised plinth platform (`PLINTH_H=0.12`) below body with a rectangular cutout + a `service_panel` REVOLUTE part, bottom-edge `(0,1,0)` hinge, flips down 75°; feet drop to `z≈-PLINTH_H-0.01`. Part tree: body→service_panel (1 revolute joint) |

**Single-candidate degrade note:** Slots C and D each have exactly **2** candidates (≥2 minimum satisfied, below the 3–6 target). Reason: the picture batch for this 小类 converged exactly these and only these structurally-distinct mechanisms — for C, prismatic drawer vs. revolute flip-lid (no third dispenser topology exists in the 5★ pool); for D, no-joint flush hatch vs. revolute flip-down service panel on a plinth (no third base topology). Each pair is genuinely structurally different (joint type / part count / chassis change), so neither is a mere size/color variant and neither needs to be folded. Inventing a third candidate without a 5★ source is prohibited; left at 2 for reviewer approval.

## 槽位图（slot graph）

pattern: parallel_children

```
                         body (root cabinet)
                          |  (white enamel cube; tub cavity bored along +X)
   ┌───────────┬──────────┼───────────┬─────────────────┐
   ▼           ▼          ▼           ▼                 ▼
  drum        door     Slot B       Slot C            Slot D
(CONTINUOUS  (REVOLUTE  control     dispenser         base/service
 +X spin,    +Z side    interface   (drawer/flip)     (flush/plinth)
 fixed)      hinge)
```

Fixed (non-slot) children always present:
- `drum` → `body_to_drum`: CONTINUOUS, origin `(DRUM_FRONT_X, DOOR_CY, DOOR_CZ)`, axis `(1,0,0)`, no limits. Mates to the **tub-cavity bore** (contact plane = cylindrical tub wall, radial clearance; retained by the spin joint, declared `allow_overlap(drum,body)` + on some variants `allow_isolated_part(drum)`).
- `door` → `body_to_door`: REVOLUTE, origin `(FRONT_X-0.005, HINGE_Y, DOOR_CZ)`, axis `(0,0,1)`, range `[0, 100°]`. Mates to the **front opening recess** (mating face = front-face door recess; hinge pivot = left/`+Y` edge). `HINGE_Y` derives from the chosen Slot-A frame half-width.

Slot interfaces (all to `body`, parallel):
- **Slot A** ⟷ body: front-face circular/rounded recess (mating contact plane = front face at `x≈FRONT_X`); pivot axis vertical `+Z` at the LEFT (`+Y`) outer rim. Slot A choice sets `HINGE_Y`, recess shape (circle vs rounded-rect), and whether a latch visual exists. The door joint itself is **invariant** in type/axis/range across all Slot-A modules; only mesh + `HINGE_Y` change.
- **Slot B** ⟷ body: control-panel strip face (`PANEL_Z0..PANEL_Z1`); dial(s) mount proud of the front face on the `+X` socket axis (CONTINUOUS); touch module uses inline visuals only (no joint). Mutually exclusive: a seed picks exactly one Slot-B module → 0, 1, or 2 continuous dial joints.
- **Slot C** ⟷ body: top-left front recess pocket. drawer = PRISMATIC rail along `+X`; flip_lid = REVOLUTE top-edge `−Y`-axis hinge + a fixed body tray visual. Mutually exclusive.
- **Slot D** ⟷ body: lower front face / plinth. flush = body visual only; plinth = adds a plinth body visual + REVOLUTE bottom-edge `+Y`-axis flip-down panel; plinth also lowers the feet. Mutually exclusive.

Cross-slot clearance rule (derived constraint, not a joint): a front-face revolute mechanism in Slot C (flip_lid swings to ~`+X 0.05`) or Slot D (flip-down panel) must not collide with the large door swing arc. Slot C sits top-left (`DRAWER_CY=0.205`) and Slot D sits low on the plinth, both laterally/vertically clear of the door (centered `DOOR_CY=-0.02, DOOR_CZ=0.40`), so all combinations are geometrically compatible.

## 每槽位 Module Emits / Interfaces

### fixed / drum
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drum` (steel `drum_shell`: open-front cylinder + back wall + 3 lifter ribs; convex/square variants add a front flange) | parent L196-L222 |
| internal joints | `body_to_drum` CONTINUOUS, axis `(1,0,0)`, origin `(DRUM_FRONT_X,DOOR_CY,DOOR_CZ)`, no limits | parent L303-L313 |
| upstream interface | child of body; nested in tub cavity bore, radial clearance | parent L297-L302 |
| downstream interface | none (leaf); `allow_overlap(drum_shell, body_shell)` always | parent L446-L449 |

### fixed / door (shape from Slot A)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door` (bezel/gasket/ring + glass + hinge leaf [+ latch on convex]) | parent L319-L339 |
| internal joints | `body_to_door` REVOLUTE, axis `(0,0,1)`, origin `(FRONT_X-0.005,HINGE_Y,DOOR_CZ)`, range `[0,100°]` | parent L345-L357 |
| upstream interface | child of body; bezel rim seats over front opening recess; `expect_overlap yz min 0.05` | parent L482-L486 |
| downstream interface | none (leaf); `allow_overlap(door_bezel/gasket/ring, body_shell)` + `allow_overlap(glass, bezel)` | parent L450-L473 |

### Slot A / round_porthole_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_bezel` (BezelGeometry circle), `door_glass` (flat tinted disk), `door_hinge_leaf` | parent L152-L193, L322-L339 |
| internal joints | (uses fixed `body_to_door`); `HINGE_Y = DOOR_CY+(OPENING_R+0.030)` | parent L318 |
| upstream interface | front circular recess (`OPENING_R+0.040` wide, 0.035 deep) | parent L96-L104 |
| downstream interface | none | — |

### Slot A / rounded_square_window
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_gasket` (BezelGeometry rounded_rect), `door_glass` (rounded-square panel), `door_hinge_leaf` | square L160-L210 |
| internal joints | (fixed `body_to_door`); `HINGE_Y = DOOR_CY+GASKET_SIZE/2`; variant test asserts gasket Y≈Z extent & thick | square L351, L591-L616 |
| upstream interface | rounded-square front recess (filleted), distinct from circular | square L101-L112 |
| downstream interface | none | — |

### Slot A / convex_porthole
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_chrome_ring`, `door_porthole_glass` (spherical-cap dome, 50 mm bulge), `door_hinge_leaf`, `door_latch` (free `-Y` edge) | convex L152-L271, L394-L431 |
| internal joints | (fixed `body_to_door`); `HINGE_Y = DOOR_CY+(OPENING_R+0.040)` | convex L397 |
| upstream interface | circular recess; `allow_overlap(porthole_glass,chrome_ring)` + `allow_isolated_part(drum)` | convex L569-L572, L544-L548 |
| downstream interface | none; latch test: latch on `-Y` side, dome bulges past ring | convex L587-L617 |

### Slot B / single_dial_display
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dial` (KnobGeometry skirted cap), body `display` + `panel_inset` visuals | parent L360-L372, L119-L149 |
| internal joints | `body_to_dial` CONTINUOUS, axis `(1,0,0)`, origin `(FRONT_X-0.001, DIAL_CY, DIAL_CZ)` | parent L376-L385 |
| upstream interface | dial seats against panel inset; `allow_overlap(dial_cap, panel_inset/body_shell)` | parent L462-L469 |
| downstream interface | none | — |

### Slot B / touch_panel_buttons
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visuals only: `touch_display` (wide dark block) + `button_0..4` (flush disks) | touch L149-L166, L291-L301 |
| internal joints | **none** (no dial articulation) | touch (absence) |
| upstream interface | recessed into wide panel pocket; buttons proud at `FRONT_X+0.002` | touch L127-L146 |
| downstream interface | none; tests: display width ≥0.30, centered, 5 buttons below display | touch L557-L587 |

### Slot B / twin_dial_controls
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dial_0`, `dial_1` (smaller KnobGeometry caps via shared `_dial_knob_mesh`), compact body `display` | twin L269-L284, L391-L402 |
| internal joints | `body_to_dial_0`, `body_to_dial_1` CONTINUOUS, axis `(1,0,0)`, origins from `DIAL_POSITIONS` `(±0.06, DIAL_CZ)` | twin L403-L411 |
| upstream interface | both seat on panel; `allow_overlap(dial_i_cap, panel_inset/body_shell)` per i | twin L494-L502 |
| downstream interface | none; tests: 2 dials laterally separated, same height | twin L508-L533 |

### Slot C / pull_out_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer` (`drawer_tray` shelled + dividers + front plate, `drawer_pull` box) | parent L225-L254, L388-L396 |
| internal joints | `body_to_drawer` PRISMATIC, axis `(1,0,0)`, range `[0, DRAWER_TRAVEL=0.150]`, origin `(FRONT_X-DRAWER_DEPTH-0.004, DRAWER_CY, DRAWER_CZ)` | parent L401-L412 |
| upstream interface | seated in front-face slot pocket; `allow_overlap(drawer_tray, body_shell)`; `expect_overlap x min 0.05` | parent L458-L461, L567-L571 |
| downstream interface | none | — |

### Slot C / flip_lid_tray
| emits | 描述 | 来源 |
|---|---|---|
| parts | body `dispenser_tray` (fixed connected solid) + `dispenser_lid` part (`dispenser_lid_panel` + grip tab) | flip L227-L298, L431-L449 |
| internal joints | `body_to_dispenser_lid` REVOLUTE, axis `(0,-1,0)` (top-edge), range `[0, 75°]`, origin `(FRONT_X-0.002, DISPENSER_CY, DISPENSER_CZ+DISPENSER_H/2)` | flip L454-L468 |
| upstream interface | lid flush in recess; `allow_overlap(lid_panel, body_shell)` + `allow_overlap(lid_panel, dispenser_tray)` | flip L519-L526 |
| downstream interface | none; tests: lid opens forward (+X), hinge horizontal (Y preserved) | flip L622-L643 |

### Slot D / flat_service_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `service_hatch` (`Box(0.010,0.150,0.150)`) + 4 corner `foot_*` boxes at `z≈-0.01` | parent L276-L291 |
| internal joints | **none** | parent (absence) |
| upstream interface | flush on front face at `(FRONT_X-0.003, HATCH_CY, HATCH_CZ)` | parent L277-L282 |
| downstream interface | none | — |

### Slot D / raised_plinth_flip_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | body `plinth_base` (plinth with front cutout) + low feet; `service_panel` part (`service_panel` mesh: plate + pull lip + pivot blocks) | plinth L265-L312, L335-L346, L472-L473 |
| internal joints | `body_to_panel` REVOLUTE, axis `(0,1,0)` (bottom-edge), range `[0, 75°]`, origin `(FRONT_X, 0.0, PANEL_HINGE_Z=-PLINTH_H+0.008)` | plinth L478-L490 |
| upstream interface | panel seats in plinth cutout; `allow_overlap(service_panel, plinth_base)`; feet at `z≈-PLINTH_H-0.01` | plinth L554-L557, L339-L346 |
| downstream interface | none; tests: panel width ≥0.30, flips forward+down, hinge at bottom edge | plinth L681-L733 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `door_module` (Slot A) | enum | round_porthole_door / rounded_square_window / convex_porthole | round_porthole_door | choice | deterministic procedural sampler | Slot A table |
| `control_module` (Slot B) | enum | single_dial_display / touch_panel_buttons / twin_dial_controls | single_dial_display | choice | deterministic procedural sampler | Slot B table |
| `dispenser_module` (Slot C) | enum | pull_out_drawer / flip_lid_tray | pull_out_drawer | choice | deterministic procedural sampler | Slot C table |
| `base_module` (Slot D) | enum | flat_service_panel / raised_plinth_flip_panel | flat_service_panel | choice | deterministic procedural sampler | Slot D table |
| `palette_style` | enum | classic_white / graphite_dark / inox_silver / matte_black / champagne_gold / retro_cream | classic_white | choice | per-seed colorway pick (§7 below) | materials across all 7 samples |
| `body_width_scale` | float | [0.92, 1.10] | 1.0 | independent | scales `BODY_W`; sampled then clamp | parent L43 |
| `body_height_scale` | float | [0.94, 1.08] | 1.0 | independent | scales `BODY_H`, `PANEL_Z0`, `DOOR_CZ`, `DRAWER_CZ` proportionally | parent L43-L70 |
| `body_depth_scale` | float | [0.94, 1.06] | 1.0 | independent | scales `BODY_D`/`FRONT_X` and dependent `TUB_BACK_X`, `DRUM_*_X`, `DRAWER_DEPTH` | parent L44-L69 |
| `opening_r` | float | derived | 0.165 | equation | `= clamp(0.165·body_width_scale, 0.14, 0.185)`; drives recess + door mesh | parent L51 |
| `tub_r` | float | derived | 0.205 | equation | `= opening_r + 0.040` (tub wall sits outside opening) | parent L52-L53 |
| `drum_r` | float | derived | 0.175 | equation | `= tub_r - 0.030` (radial clearance to tub wall) | parent L54 |
| `door_open_angle` | float | [90°, 105°] | 100° | independent | `body_to_door` upper limit; clamp | parent L355 |
| `drawer_travel` | float | [0.12, 0.17] | 0.150 | conditional | only for `pull_out_drawer`; `≤ DRAWER_DEPTH - 0.05` | parent L70, L410 |
| `dispenser_open_angle` | float | [65°, 80°] | 75° | conditional | only for `flip_lid_tray` lid | flip L72 |
| `panel_open_angle` | float | [65°, 80°] | 75° | conditional | only for `raised_plinth_flip_panel` | plinth L82 |
| `plinth_h` | float | [0.10, 0.14] | 0.12 | conditional | only for `raised_plinth_flip_panel`; feet drop with it | plinth L75 |
| (—) | constraint | — | — | inequality | `drum_r + clearance ≤ tub_r` and `tub_r + 0.02 ≤ min(BODY_W,BODY_H)/2`; door recess width `opening_r+0.040 ≤ BODY_H/2 - 0.02`; violate → shrink `opening_r` then re-derive | tub/opening interfaces |
| (—) | constraint | — | — | inequality | `HINGE_Y` (Slot-A frame half-width) `≤ BODY_W/2 - 0.02` so hinge stays on the front face | Slot A meshes |

**palette_style colorways** (each picks body/door-frame/glass/control + accent materials, all observed or trivially recolored from the 7 samples; rgba kept plausible):
- `classic_white` — body enamel_white `(0.94,0.94,0.95)`, bezel_black `(0.07,0.07,0.08)`, tinted_glass `(0.18,0.20,0.24,0.45)`, drum_steel `(0.72,0.73,0.76)`, dial_metal `(0.78,0.79,0.81)`. (parent / all baseline samples.)
- `graphite_dark` — body `(0.22,0.23,0.25)`, chrome/silver frame `(0.80,0.82,0.85)`, tinted_glass `(0.10,0.11,0.14,0.5)`, steel drum, light-gray controls. (mirrors convex chrome accent L343.)
- `inox_silver` — body brushed steel `(0.66,0.68,0.71)`, bezel_black frame, tinted_glass, polished dial_metal, dark display. (inox/stainless front-loader.)
- `matte_black` — body `(0.08,0.08,0.09)`, dark-gray frame `(0.20,0.20,0.22)`, smoky glass `(0.06,0.07,0.09,0.55)`, steel drum, chrome accents.
- `champagne_gold` — body warm beige `(0.86,0.80,0.66)`, bronze frame `(0.55,0.45,0.30)`, tinted_glass, gold dial `(0.80,0.68,0.40)`.
- `retro_cream` — body cream `(0.92,0.88,0.78)`, chrome ring frame `(0.85,0.86,0.88)`, blue-tinted glass `(0.16,0.22,0.30,0.45)`, steel drum, cream/chrome controls.

(≥3 required; 6 provided. Each is sampled per seed so template output is color-diverse.)

## Multiplicity / Copy Logic

- **无模板级 multiplicity 轴 (no count_param)。** 核心结构由固定 named slots (door/drum + Slot A/B/C/D) 表达，不暴露 `*_count`，也不通过循环复制模板级 part/joint。
- The **only** loop-emitted repeated objects are local, fixed-count, and gated inside a single module:
  - `touch_panel_buttons` (Slot B): `BUTTON_COUNT=5` flush `button_{i}` **body visuals** (touch L294-L301) — non-articulated decorative visuals, fixed count, NOT a template multiplicity slot.
  - `twin_dial_controls` (Slot B): exactly **2** `dial_{i}` parts/joints via `DIAL_POSITIONS` (twin L391-L411) — this "2" is the module's identity (twin), not a variable `N`; it is fixed by module choice, not sampled.
- copied object / naming / placement / joint policy: if a future sample introduces a variable button grid or articulated repeated controls, it would become a module-local fixed structure first; only a genuinely articulated repeated-child family with ≥2 distinct N samples would justify promoting to a multiplicity axis. None exists today.
- N_range / sampling domain: **N/A** (no axis).

## 拓扑多样性审计

总组合数：Slot A(3) × Slot B(3) × Slot C(2) × Slot D(2) = **36** distinct topology combinations.
（无 multiplicity 轴，所以 36 即纯拓扑组合数。）

理由：36 ≥ 10 with margin. The four slots produce genuinely different part trees / joint sets:
- Slot B alone changes the joint count (touch = 0 continuous dial joints, single = 1, twin = 2).
- Slot C changes joint type (prismatic drawer vs revolute lid + extra body tray visual).
- Slot D changes part count (flush hatch = 0 extra joints, plinth = +1 revolute panel + plinth visual + feet relocation).
- Slot A changes the door mesh family + recess shape + `HINGE_Y` + presence of a latch visual.
A 1000-seed sweep over 36 combos (with per-combo continuous scale jitter) easily clears 10 slot choice tuple distinct classes; the realistic distinct-topology ceiling is exactly 36, well above the ≥10 floor (below the ≥300 rich-category guideline only because the category genuinely has 36 legal topologies — documented category constraint, not a sampler defect).

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` does a deterministic per-seed weighted draw over the 4 slot enums (all combos legal → near-uniform; mild weighting toward the parent baseline `single_dial_display + pull_out_drawer + flat_service_panel + round_porthole_door` so the common residential machine appears often). Then sample independent body scales, derive `opening_r/tub_r/drum_r`, then resolve conditional dims (`drawer_travel` / lid+panel angles / `plinth_h`) only for the chosen modules, then project the inequality constraints (shrink `opening_r` if tub/drum/recess don't fit). `seed=0` is not special.

Topology target：1000-seed slot choice tuple distinct expected = 36 (the full legal set). Below the ≥300 suggestion because the category has exactly 36 legal topologies; this is a category cardinality limit, not a sampling weakness.（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：`body_width_scale` / `body_height_scale` / `body_depth_scale` (independent, clamped), with `opening_r`→`tub_r`→`drum_r` as an `equation` chain and the joint ranges (`door_open_angle`, `drawer_travel`, lid/panel angles) as independent/conditional. All resolved/clamped in `resolve_config`; none changes a declared topology, multiplicity, or interface semantics — they only adjust safe proportions/clearance. Sampling contract: independent scales first → derive `opening_r/tub_r/drum_r` → project tub/opening inequalities → resolve conditional dims by chosen module.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted draw over 4 slot enums (slight baseline bias) + per-combo scale jitter; deterministic from seed | `slot_choices_for_seed` matches build choices |
| compatibility matrix | all 36 cells legal; gate only: (a) drum/door are fixed-always; (b) conditional dims resolved per chosen Slot C/D module; (c) clearance inequality between front-face revolute mechanisms (Slot C flip-lid / Slot D panel) and the door swing — satisfied by fixed top-left / low-plinth placement | no floating, no collision, correct joint axis/range, closed-pose seal of door over drum mouth |
| controlled local variation | body scales + opening/tub/drum equation chain + joint-range jitter; clamp per §7 | proportions vary without breaking door recess seat, drum clearance, dial socket, or hinge-on-front-face |
| regression overrides | none | — |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit |and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A door | 3 | yes | yes | |
| B control | 3 | yes | yes | touch=0/single=1/twin=2 dial joints |
| C dispenser | 2 | yes | no | only 2 structurally-distinct mechanisms in 5★ pool (prismatic vs revolute); degrade documented |
| D base/service | 2 | yes | no | only 2 in 5★ pool (no-joint flush vs revolute plinth panel); degrade documented |

## Validator

- `slot_choices_for_seed` returns implemented module names for all 4 slots (A/B/C/D)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility matrix / gating: all 36 cells legal; conditional dims resolved only for chosen Slot C/D module; no illegal combos generated
- optional regression overrides: none
- final template does not endlessly cycle a small curated table as the main seed domain (full 4-enum product is the domain)
- controlled local scale params (`body_*_scale`, `opening_r`/`tub_r`/`drum_r` chain, joint angles/travel) are clamped and cannot break the door recess seat, drum-in-tub clearance, dial socket, or hinge placement
- cross-part scale dependencies (`opening_r`→`tub_r`→`drum_r` equation; tub/opening/recess inequalities) resolved in `resolve_config`, not in the builder
- critical InterfaceSpec / MatingContract points exist: drum↔tub-cavity, door↔front-recess, dial↔panel, drawer/lid↔dispenser-pocket, panel↔plinth-cutout
- key joints have expected type/axis/range: `body_to_drum` CONTINUOUS `+X`; `body_to_door` REVOLUTE `+Z` `[0,~100°]`; dial(s) CONTINUOUS `+X`; drawer PRISMATIC `+X`; flip-lid REVOLUTE `−Y`; service panel REVOLUTE `+Y`
- copied objects (touch buttons, twin dials) follow fixed-count naming `button_{i}` / `dial_{i}` and regular placement

## Reject cases

- Drum modeled as anything other than a CONTINUOUS `+X` spin child recessed inside the tub cavity (e.g. drum welded to body, drum proud of front face, or drum axis vertical).
- Door not REVOLUTE on a vertical `+Z` side hinge, or door not seating over the front opening / not covering the drum mouth in closed pose (drum mouth visible/unsealed).
- A Slot-B touch module that still emits a phantom dial joint, or a twin module that doesn't produce exactly 2 separated continuous dials at equal height.
- Slot-C flip-lid emitting the lid as a floating part (tray not fixed to body), or drawer travel exceeding the pocket depth and sliding fully out / detaching.
- Slot-D plinth panel hinged at the top or sides instead of the bottom edge, or plinth without lowering the feet (feet floating above the floor) / panel not seating in the cutout.
- Front-face revolute mechanism (flip-lid / service panel) whose swing arc collides with the open door, or any module floating/penetrating because an interface anchor wasn't recomputed after a body scale.
- `opening_r`/`tub_r`/`drum_r` chain left un-derived so a scaled body breaks drum clearance or the door recess seat (boolean failure or穿模).
- Inventing a 3rd Slot-C or Slot-D candidate with no 5★ source.

## 与相邻类别的边界

- 不该混入：**top-loading washing machine** — a top-loading washer has a top-hinged LID and a VERTICAL-axis agitator/drum, not a front porthole + horizontal-axis drum. This template is front-loading only (door on the front face, drum spins about `+X`).
- 不该混入：**clothes dryer / combo dryer** — visually similar white box with a porthole door, but no detergent dispenser drawer and typically a lint area / vent; do not add dryer-specific lint mechanisms. Keep the detergent dispenser (drawer/flip-lid) as a defining feature.
- 不该混入：**dishwasher** — also a front-panel white appliance with a door, but the dishwasher door is bottom-hinged (drops down) and there is no spinning drum behind a glass porthole. Our door is side-hinged with a glass window over a visible drum.
- 不该混入：**built-in oven / microwave** — front glass door + dial controls superficially overlap, but those have a heating cavity, no spinning drum, no detergent dispenser; identity here is the laundry drum + dispenser.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slots A/B = 3 candidates; Slots C/D = 2 candidates each (degrade documented — 5★ pool converged exactly 2 structurally-distinct mechanisms per slot, neither a size/color variant). 36 topology combos ≥10. Drum is a fixed CONTINUOUS root child (not a slot); door is a fixed REVOLUTE root child whose mesh+HINGE_Y are set by Slot A. palette_style = 6 colorways. No multiplicity axis (touch buttons / twin dials are module-local fixed-count). |

## 模板实现备注（可选）

- Shared helpers across modules: `_body_solid` (recess shape depends on Slot A: circle vs rounded_rect), `_panel_inset`/`_display_solid` (pocket size depends on Slot B), `_drum_mesh`, `_door_hinge_leaf_mesh`, `_ext`/`_center` test helpers — all common across the 7 samples.
- `HINGE_Y` for the door must be recomputed from the chosen Slot-A frame half-width (`OPENING_R+0.030` round, `GASKET_SIZE/2` square, `OPENING_R+0.040` convex) — a hard interface dependency between Slot A choice and the fixed `body_to_door` origin.
- The body front recess geometry is itself Slot-A-dependent (circular for round/convex, rounded-square for the window module) — Slot A must drive both the door mesh AND the body recess cut to keep them seated.
- `flip_lid_tray` (Slot C) emits a FIXED `dispenser_tray` as a **body** visual plus the articulated lid part — replicate `allow_overlap(dispenser_lid_panel, dispenser_tray)` and `(…, body_shell)`.
- `raised_plinth_flip_panel` (Slot D) changes the BODY (adds `plinth_base` visual, lowers feet to `z≈-PLINTH_H-0.01`); the flush module keeps feet at `z≈-0.01`. The base module must own foot placement.
- Per-combo `allow_overlap` declarations must be emitted conditionally for whichever modules are present (drum/door always; dial(s) for single/twin; drawer/lid for C; panel/plinth for D). `allow_isolated_part(drum)` appears on several variants (convex/touch/twin/flip/plinth) — safe to always declare for the drum.
- New slug `washing_machine` must be added to `cli/template.py TEMPLATE_REGISTRY` allow-list at template-build time (per memory: importlib filename auto-discovery alone is not enough for the sweep/batch CLI). Not done here (SPEC_ONLY).

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | fixed | body+drum+door core | parent `…_3205b533` | L42-L116 (body), L196-L222/L297-L313 (drum), L315-L357 (door) | shared chassis + fixed continuous drum + fixed revolute door |
| S1 | A | round_porthole_door | parent `…_3205b533` | L152-L193, L315-L357 | circular bezel + flat glass door |
| S2 | A | rounded_square_window | `rec_washmachine_var_square_window_door` | L160-L210, L348-L391 | rounded-rect gasket window |
| S3 | A | convex_porthole | `rec_washmachine_var_convex_porthole_door` | L152-L271, L394-L449 | chrome ring + convex dome + latch |
| S4 | B | single_dial_display | parent `…_3205b533` | L359-L385, L119-L149 | one continuous dial + display |
| S5 | B | touch_panel_buttons | `rec_washmachine_var_touch_panel_controls` | L149-L166, L291-L301 | touch display + 5 flush button visuals (no joint) |
| S6 | B | twin_dial_controls | `rec_washmachine_var_twin_dial_controls` | L269-L284, L389-L411 | two continuous dials + compact display |
| S7 | C | pull_out_drawer | parent `…_3205b533` | L225-L254, L387-L412 | prismatic detergent drawer |
| S8 | C | flip_lid_tray | `rec_washmachine_var_flip_lid_dispenser` | L227-L298, L431-L468 | fixed tray + revolute top-edge flip lid |
| S9 | D | flat_service_panel | parent `…_3205b533` | L276-L291 | flush hatch visual + feet (no joint) |
| S10 | D | raised_plinth_flip_panel | `rec_washmachine_var_raised_plinth_panel` | L265-L312, L469-L490 | plinth + revolute bottom-edge service panel |
