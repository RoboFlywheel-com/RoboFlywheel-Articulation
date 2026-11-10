# double_door — Modular Spec (SPEC_ONLY)

> Authored from the source map + every 5★ `model.py` (6 parents + 8 variants).
> All `model.py:Lx-Ly` spans below are real line spans verified by reading each
> source. `stage` stays `SPEC_ONLY_DRAFT`, `reviewer status` stays `pending`.

## 元信息
| 项 | 值 |
|---|---|
| slug | `double_door` |
| template path | `agent/templates/Door_Double_Door.py` |
| test path (optional) | `tests/agent/test_double_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`: two mirror leaves (a 2-copy `multiplicity` of the leaf module) hang on a
fixed frame root via two mirrored revolute hinges (`parallel_children`), and the
per-leaf infill is itself a `multiplicity` of stacked panels / divided lites /
slats / boards. The spine is the two leaf↔frame hinges.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star samples in this category (6 parents + 8 workbench variants) |
| source_index_policy | only adopted module sources are indexed below |

Reading summary (every file read in full):

- **Common spine.** All 14 author ONE leaf in a leaf-local frame (hinge edge at
  local X=0, body extending toward `sign`, thickness on Y with front face +Y) and
  produce the second leaf by a `sign` flip or a `mirror=True`/`_mirror_x` helper.
  Both leaves keep the SAME world-facing front (+Y). Frame is the fixed root part
  carrying two side jambs + a head member + a base/threshold + doorstop beads
  (classic `_build_frame_members` L73-L132). The two leaf↔frame revolute hinges
  (one +Z, one −Z, mirrored) are the canonical spine.
- **Leaf-infill is the dominant structural axis (Slot A).** Eight structurally
  distinct infills appear: stacked raised/fielded panels (classic + panels_two/six),
  vision-window + glass + stainless push-bar (hospital), carved-circle raised-molding
  ring + dark inset disc (ornate), upper divided-glass-over-lower-X-braced-boards
  (carriage), framed horizontal louver field (saloon spring + louvered_infill
  revolute), full single glass pane in a narrow stile frame (storefront), and a
  full-height ledged-and-X-braced tongue-and-groove board field (x_brace_solid).
- **Head/top profile is a second axis (Slot B).** Flat head jamb (classic), arched
  stone surround with keystone (carriage), scalloped/ogee leaf-crown (saloon),
  rectangular fixed transom + sidelights surround (ornate), and arched LEAF top
  (arched_louvered profile-based, arched_glazed `threePointArc` + matching ring
  frame header). The scalloped crown and arched leaf top live in the LEAF profile;
  the stone/transom heads live in the FRAME surround — this drives the
  compatibility matrix (an arched leaf top double-arches with a stone/transom head).
- **Swing mechanism is a third axis (Slot C).** Both-revolute-opposite (the great
  majority; +Z / −Z hinges, outward swing, lower=0 upper≈1.4–1.92), double-acting
  spring (saloon + arched_louvered; symmetric ±1.2, rest at 0), and active/inactive
  with astragal (one_active_astragal: only door_0 is a real revolute; the inactive
  leaf, its hardware, and the meeting astragal bead are INLINE FRAME VISUALS, not a
  jointed part).
- **Multiplicity.** Per-leaf stacked raised panels (`panel_count` {2,3,6}), divided
  lite grid (`N_ROWS × N_COLS`, e.g. 2×3=6), louver slats (`slat_count`=18), and
  X-buck boards (`BOARD_COUNT`=7) are all loop-emitted via a shared per-feature
  helper. The two leaves themselves are the multiplicity-2 of the leaf module.
- **Palette.** Sources span dark walnut, honey-brown wood, warm carriage wood with
  light stone, off-white hospital steel + stainless + tinted glass, and anodized
  aluminum storefront + glass — a natural ≥4-way `palette_style` enum.

## 核心身份

A **double door** is a fixed frame/surround root carrying **two mirror-symmetric
operable leaves** that meet at the center. The defining, must-not-lose facts:

1. **Exactly two leaves**, mirror-symmetric across the world X=0 plane, on a single
   shared frame, meeting at a central reveal (small gap, no interpenetration when
   closed). This is the single hard distinction from a single Door.
2. **At least one real moving leaf.** Normally BOTH leaves carry a real revolute
   (or double-acting spring-pivot) hinge with a vertical (Z) axis at the outer jamb,
   the two hinges mirrored (+Z and −Z). The one documented exception is the
   active/inactive astragal mode where one leaf is fixed inline to the frame and only
   the active leaf hinges — but a real hinge always exists.
3. **A frame surround** (two jambs + head + base/threshold + doorstop beads) as the
   root. Optional sidelights / transom extend the surround but never replace the
   two-leaf core.
4. Closed pose: leaves meet at center with a reveal and both hinge edges contact
   their jambs; open pose: leaves swing clear (outward +Y or, for spring, both ways).

Default maturity domain: residential and commercial entry/interior double doors
~1.6–1.8 m clear width, ~2.0–2.1 m tall, each leaf ~0.045–0.06 m thick.

## 槽位 + 候选模块表

### Slot A：leaf infill style

The replaceable structural/visual content of one leaf (mirrored to the other). Each
candidate differs in part tree / cut-union topology / loop-copied sub-features.

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| raised_panel_leaf | rec_double_door_var_panels_six | `_add_raised_panel` L138-L204 ; panel loop L247-L260 | eligible if compatible | leaf box + `for i in range(panel_count)` stacked fielded panels: cut recessed field, union bolection molding ring, union proud fielded pad; panels merged into leaf solid. Canonical panel-multiplicity loop source. |
| vision_window_pushbar_leaf | rec_commercial-hospital-double-door-in-off-white-ste_20260606_120526_255019_1fe7f29a (parent) | `_leaf_body` L93-L116 ; `_glass_pane` L119-L126 ; `_push_bar` L129-L160 ; `_bumper_stripe` L163-L171 | eligible if compatible | rectangular leaf with cut-through vision window + seated translucent glass pane + horizontal stainless push-bar on standoffs + two blue rubber bumper stripes |
| carved_circle_motif_leaf | rec_ornate-double-door-in-honey-brown-wood-with-a-da_20260606_115210_265714_26551efa (parent) | `_leaf_body` L85-L162 ; `_leaf_inset` L165-L188 ; `_handle` L191-L219 | eligible if compatible | recessed flat field + raised concentric molding half-ring forming a central circle at the meeting edge + dark recessed inset half-disc + vertical pull handle on standoffs |
| upper_glass_muntin_lower_xbrace_leaf | rec_arched-carriage-style-double-door-in-warm-wood-t_20260606_115230_910775_7b8384ab (parent) | `_leaf_frame_and_panels` L101-L198 (muntin grid L141-L155 ; lower X-brace boards L173-L192) | eligible if compatible | returns (wood_frame, glass, x_brace); upper divided-glass window (1 vertical + 2 horizontal muntins) over lower ledged-and-X-braced board panel |
| louvered_slat_leaf | rec_double_door_var_louvered_infill | `_build_louver_slat` L179-L191 ; slat loop L311-L320 | eligible if compatible | framed full-height field of horizontal angled louver slats via `for i in range(slat_count)` (slat_count=18) emitting `door_{idx}_slat_{i}` from a shared slat helper; swing-mode-agnostic (one infill, parametrized by Slot C). The saloon `_louver_grille_mesh` (VentGrilleGeometry, L105-L126) is the spring-leaf alternate of the same infill. |
| full_glass_single_pane_leaf | rec_aluminum-storefront-double-door-two-narrow-stile_20260606_115902_647305_38236092 (parent) | `_leaf_frame_body` L74-L105 ; `_glass_pane` L108-L117 ; `_push_bar_mesh` L120-L161 | eligible if compatible | narrow-stile aluminum frame (two stiles + top/bottom rails) around one large single glass pane + diagonal spline-tube push bar |
| divided_lite_glass_leaf | rec_double_door_var_six_light_glazed | `_glass_lite` L159-L172 ; `_muntin_grid` L128-L156 ; nested lite loop L244-L251 | eligible if compatible | full-window glazed leaf with a divided lite GRID: nested `for row in range(N_ROWS): for col in range(N_COLS)` emitting `lite_{row}_{col}` + a `_muntin_grid` of horizontal/vertical bars (2×3=6 lites). Canonical lite-grid multiplicity source; distinct from full_glass_single_pane (gridded vs single pane). |
| cross_buck_board_leaf | rec_double_door_var_x_brace_solid | `_make_tg_board` L196-L212 ; board loop L360-L367 (`BOARD_COUNT`=7) ; `_build_ledger` + `_build_xbrace` diagonals | eligible if compatible | full-height ledged-and-X-braced tongue-and-groove board field: `for i in range(BOARD_COUNT)` emitting `door_{idx}_board_{i}` from `_make_tg_board` + top/bottom ledgers + two diagonal braces; solid, no glass |

8 structurally distinct candidates. (`carved_circle_motif_leaf` differs from
`raised_panel_leaf` by the concentric molding half-ring + recessed inset disc topology,
not just decoration; `divided_lite_glass_leaf` differs from `full_glass_single_pane_leaf`
by the muntin-grid copy logic vs a single pane.)

### Slot B：head / top profile

Where the arch/crown/transom lives drives compatibility (LEAF profile vs FRAME surround).

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_head | rec_classic-double-entry-door-in-dark-walnut-wood-tw_20260606_115214_146776_3b44fd42 (parent) | `_build_frame_members` head_jamb L94-L98 (within L73-L132) | eligible if compatible | flat rectangular head jamb spanning the frame top; square leaf tops. Default/degrade head. |
| arched_stone_head | rec_arched-carriage-style-double-door-in-warm-wood-t_20260606_115230_910775_7b8384ab (parent) | `_stone_surround` L254-L331 (arch ring L292-L310 ; keystone L312-L317) | eligible if compatible | semicircular arched STONE surround (hollow concentric ring clipped to upper half) + central keystone wedge + pilasters/base; FRAME-surround arch, assumes flat/square leaf tops |
| scalloped_crown_head | rec_saloon-style-swinging-cafe-double-doors-batwing-_20260606_115237_933064_1a02f0ce (parent) | `_scalloped_leaf_profile` L73-L102 (crown arc L92-L99) | eligible if compatible | cyma/ogee scalloped crown sampled into the LEAF outer profile, peaking at the inner (center) edge so the mirrored pair forms a central hump; LEAF-profile head |
| transom_over_flat_head | rec_ornate-double-door-in-honey-brown-wood-with-a-da_20260606_115210_265714_26551efa (parent) | `_surround_members` head_rail (within L222-L263) ; `_fixed_panels` transom + sidelights L266-L302 | eligible if compatible | rectangular fixed transom band over flat-topped leaves, with optional fixed sidelight panels; FRAME-surround head, assumes square leaf tops |
| arched_leaf_top | rec_double_door_var_arched_glazed | `_arched_leaf_frame(sign)` L78-L174 (`threePointArc` L115) ; `_arched_glass_pane(sign)` L177-L218 ; `_arched_frame_header` L221-L253 | eligible if compatible | each leaf gets a quarter-circle arched top (rect + `threePointArc`, radius `ARCH_R`) so the closed pair completes one round arch; the FIXED frame carries a matching semicircular ring header (`r_inner=ARCH_R`, same circle) above the spring line. LEAF-profile arch + ring header. Infill- and swing-agnostic (proven with glass+revolute here, with louver+spring in arched_louvered `_arched_leaf_profile` L78-L119). |

5 structurally distinct candidates. `scalloped_crown_head` and `arched_leaf_top` are
both LEAF-profile heads but topologically different (ogee polyline crown vs
threePointArc semicircle + ring header) and mutually exclusive on one leaf.

### Slot C：swing mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| both_revolute_opposite | rec_classic-double-entry-door-in-dark-walnut-wood-tw_20260606_115214_146776_3b44fd42 (parent) | `frame_to_door_0` L358-L366 (axis +Z) ; `frame_to_door_1` L371-L379 (axis −Z) | eligible if compatible | both leaves real REVOLUTE, vertical axes mirrored (+Z / −Z) at the outer jambs, swing outward symmetric, lower=0 upper≈1.4–1.92 |
| double_acting_spring | rec_saloon-style-swinging-cafe-double-doors-batwing-_20260606_115237_933064_1a02f0ce (parent) | `frame_to_door_0` L249-L257 ; `frame_to_door_1` L258-L266 (both axis +Z, symmetric ±1.2, rest 0) | eligible if compatible | both leaves spring pivots swinging BOTH directions, symmetric limits (lower=−1.2 upper=1.2), rest at 0 (batwing/cafe) |
| active_inactive_astragal | rec_double_door_var_one_active_astragal | active hinge `frame_to_door_0` L442-L450 (REVOLUTE +Z) ; inactive leaf inline frame visuals L372-L399 ; `_build_astragal` L308-L345 → `frame_astragal` visual L401-L405 | eligible if compatible | ONE active revolute leaf; the other leaf + its hardware are INLINE FRAME VISUALS (not a jointed part) + a vertical overlapping astragal meeting bead at the center. Drops the second hinge; changes the mirror-leaf assumption. |

3 structurally distinct candidates (≥2 satisfied; ≥3 satisfied). All three are real
distinct joint topologies (2 revolute vs 2 spring vs 1 revolute + fixed inline leaf).

## 槽位图（slot graph）

pattern: mixed

```
                         frame (root, fixed)
                  jambs + head[Slot B] + base + doorstops
                          /                    \
   [Slot C hinge L, +Z @ left jamb]      [Slot C hinge R, −Z @ right jamb]
   origin=(-(W/2 - reveal),0,Z)          origin=(+(W/2 - reveal),0,Z)
   REVOLUTE | SPRING                      REVOLUTE | SPRING | (DROPPED if astragal)
              |                                       |
          door_0 (leaf module, sign=+1)          door_1 (leaf module, sign=-1 / mirror)
          Slot A infill  +  per-leaf multiplicity (panels / lites / slats / boards)
          Slot B leaf-profile head (if arched/scalloped)  +  optional lever sub-joint
              \________ meet at center reveal (X≈0) ________/
                       (astragal bead bridges if active_inactive)
```

- **Spine.** The two leaf↔frame hinges are the spine. door_0 = +Z hinge at the left
  jamb; door_1 = −Z hinge at the right jamb (mirror). For `double_acting_spring` both
  axes are +Z with symmetric ±limits. For `active_inactive_astragal`, only door_0 keeps
  a hinge; door_1 collapses into the frame as inline visuals.
- **Interface points.** Each hinge origin sits on the outer jamb face at floor datum
  (`x = ±(OPENING_W/2 − JAMB_REVEAL)`, axis ±Z). Closed-pose mating contract: the two
  leaf meeting edges meet at X≈0 with a small reveal (`CENTER_REVEAL`), and each leaf
  hinge edge contacts its jamb (`expect_contact`, tol≈0.02).
- **Slot B placement.** `flat_head` / `arched_stone_head` / `transom_over_flat_head` are
  FRAME-surround members (consumed by the frame root). `scalloped_crown_head` and
  `arched_leaf_top` reprofile the LEAF body (consumed by the leaf module); `arched_leaf_top`
  additionally adds the matching ring header to the frame root. The two arched leaf tops
  share ONE circle centered at the opening midpoint so the closed pair completes the arch.
- **Optional moving child.** Walnut leaves may carry a per-leaf lever sub-joint
  (`door_{idx}_to_lever`, REVOLUTE about the spindle Y axis, classic L346-L354); optional,
  mirrored, only on hardware-bearing wood leaves.
- **Mutual exclusion / derivation.** Slot C is mutually exclusive (one swing mode).
  `active_inactive_astragal` excludes `double_acting_spring` and forces dropping the second
  hinge + adding the astragal. `arched_leaf_top` (LEAF arch) excludes `arched_stone_head`
  and `transom_over_flat_head` (FRAME arches/transom) to avoid double-arching; pairing
  `arched_leaf_top` with `scalloped_crown_head` is also excluded (two LEAF-profile heads).

## 每槽位 Module Emits / Interfaces

### Slot A / module raised_panel_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf solid `door_{idx}_leaf` with N fielded raised panels merged in; optional `door_{idx}_handle` brass escutcheon/rose | panels_six L138-L204, L247-L260 |
| internal joints | optional lever `door_{idx}_to_lever` REVOLUTE about leaf-local Y | classic L346-L354 |
| upstream interface | hinge edge at leaf-local X=0, consumed by Slot C hinge at the jamb | panels_six L398-L419 |
| downstream interface | meeting edge at X=sign·LEAF_W, meets sibling leaf at center reveal | classic L48-L50, closed-pose test |

### Slot A / module vision_window_pushbar_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_leaf_{n}_leaf` (window cut), `_glass`, `_push_bar`, `_stripe_upper/lower` | hospital L93-L171, L174-L214 |
| internal joints | none (push bar fixed) | hospital L174-L214 |
| upstream interface | hinge edge at X=0 → Slot C | hospital L300-L319 |
| downstream interface | center meeting reveal | hospital closed-pose test |

### Slot A / module carved_circle_motif_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_body_{idx}` (molding ring), `door_inset_{idx}` (dark disc), `door_handle_{idx}` | ornate L85-L219, L335-L353 |
| internal joints | none | ornate L335-L353 |
| upstream interface | hinge edge X=0 → Slot C (`surround_to_door_{idx}`) | ornate L360-L381 |
| downstream interface | half-disc + half-ring complete a full circle/disc at center | ornate L165-L188 |

### Slot A / module upper_glass_muntin_lower_xbrace_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_frame_{idx}`, `door_glass_{idx}` (gridded upper window), `door_xbrace_{idx}`, `door_strap_{i}_{idx}`, `door_ring_{idx}` | carriage L101-L198, L349-L378 |
| internal joints | none (straps/ring fixed) | carriage L349-L378 |
| upstream interface | hinge edge X=0 → Slot C (`surround_to_door_{idx}`) | carriage L387-L404 |
| downstream interface | center reveal | carriage closed-pose test |

### Slot A / module louvered_slat_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf frame + `door_{idx}_slat_{i}` × slat_count from `_build_louver_slat` | louvered_infill L179-L191, L311-L320 |
| internal joints | none (slats fixed) | louvered_infill L311-L320 |
| upstream interface | hinge edge X=0 → Slot C (revolute) or spring | louvered_infill L349-L370 |
| downstream interface | center reveal | louvered_infill closed-pose test |

### Slot A / module full_glass_single_pane_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_leaf_{n}_frame` (narrow stiles+rails), `_glass` (single pane), `_push_bar` (spline tube) | storefront L74-L161, L164-L189 |
| internal joints | none | storefront L164-L189 |
| upstream interface | hinge edge X=0 → Slot C | storefront L242-L259 |
| downstream interface | center reveal | storefront closed-pose test |

### Slot A / module divided_lite_glass_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf frame + `lite_{row}_{col}` grid + `_muntin_grid` bars | six_light_glazed L128-L172, L244-L251 |
| internal joints | none | six_light_glazed L244-L251 |
| upstream interface | hinge edge X=0 → Slot C | six_light_glazed L357-L376 |
| downstream interface | center reveal | six_light_glazed closed-pose test |

### Slot A / module cross_buck_board_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{idx}_board_{i}` × BOARD_COUNT + ledgers + two diagonal braces | x_brace_solid L196-L212, L360-L367 |
| internal joints | none | x_brace_solid L360-L367 |
| upstream interface | hinge edge X=0 → Slot C | x_brace_solid L413-L433 |
| downstream interface | center reveal | x_brace_solid closed-pose test |

### Slot B / module flat_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame_head_jamb` visual on the frame root | classic L94-L98 |
| internal joints | none (fixed surround) | classic L73-L132 |
| upstream interface | spans both jamb tops | classic L94-L98 |
| downstream interface | square leaf tops below | classic L135-L153 |

### Slot B / module arched_stone_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `arch_ring`, `keystone`, pilasters, base on frame root | carriage L254-L331 |
| internal joints | none | carriage L254-L331 |
| upstream interface | seated above the spring line on the jambs | carriage L292-L310 |
| downstream interface | assumes flat/square leaf tops below | carriage (excludes arched_leaf_top) |

### Slot B / module scalloped_crown_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | crown baked into the LEAF outer profile (`{part}_slab`) | saloon L73-L102 |
| internal joints | none | saloon L129-L204 |
| upstream interface | reprofiles leaf top; mirrored pair peaks at center | saloon L92-L99 |
| downstream interface | requires short batwing leaf body | saloon (compat note) |

### Slot B / module transom_over_flat_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head_rail` + fixed `transom_panel` + optional sidelight panels | ornate L222-L263, L266-L302 |
| internal joints | none (fixed lights) | ornate L266-L302 |
| upstream interface | transom band above the leaf head rail | ornate L222-L263 |
| downstream interface | assumes flat/square leaf tops | ornate (excludes arched_leaf_top) |

### Slot B / module arched_leaf_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | arched leaf outer profile (`_arched_leaf_frame`), inner-arch glass (`_arched_glass_pane`), frame ring header (`_arched_frame_header`) | arched_glazed L78-L253 |
| internal joints | none (header fixed; leaf still uses Slot C hinge) | arched_glazed L361-L380 |
| upstream interface | leaf arch radius `ARCH_R`; ring header `r_inner=ARCH_R` (SAME circle) above spring line | arched_glazed L91, L221-L253 |
| downstream interface | two leaf arches share one circle at opening midpoint → closed pair completes full arch | arched_glazed L115, L207 |

### Slot C / module both_revolute_opposite
| emits | 描述 | 来源 |
|---|---|---|
| parts | (no new parts; wires hinges) | classic L356-L379 |
| internal joints | `frame_to_door_0` REVOLUTE +Z, `frame_to_door_1` REVOLUTE −Z; lower=0 upper≈1.4–1.92 | classic L358-L379 |
| upstream interface | origin on outer jamb face at floor datum | classic L357, L370 |
| downstream interface | leaves swing outward +Y, meet at center reveal when closed | classic closed/open tests |

### Slot C / module double_acting_spring
| emits | 描述 | 来源 |
|---|---|---|
| parts | spring pivot barrel on each leaf outer edge (`{part}_pivot`) | saloon L199-L204 |
| internal joints | `frame_to_door_0/1` REVOLUTE, symmetric ±1.2, rest at 0 | saloon L249-L266 |
| upstream interface | pivot origin at inner jamb (`±(DOOR_HALF−JAMB_WIDTH)`) | saloon L249-L266 |
| downstream interface | both leaves swing both directions, rest closed at center | saloon tests |

### Slot C / module active_inactive_astragal
| emits | 描述 | 来源 |
|---|---|---|
| parts | active `door_0`; inactive leaf + hardware as INLINE FRAME VISUALS `frame_inactive_leaf/handle/lever`; `frame_astragal` bead | one_active_astragal L372-L399, L401-L405 |
| internal joints | single `frame_to_door_0` REVOLUTE +Z, lower=0 upper=1.92 | one_active_astragal L442-L450 |
| upstream interface | active hinge at left jamb; astragal embedded 1 mm into inactive leaf face, overlaps toward active leaf | one_active_astragal L308-L345 |
| downstream interface | astragal bridges the center reveal; no second hinge | one_active_astragal L401-L405 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `infill_style` | enum | raised_panel / vision_window_pushbar / carved_circle_motif / upper_glass_muntin_lower_xbrace / louvered_slat / full_glass_single_pane / divided_lite_glass / cross_buck_board | — | choice | deterministic procedural sampler over Slot A | Slot A table |
| `head_style` | enum | flat_head / arched_stone_head / scalloped_crown_head / transom_over_flat_head / arched_leaf_top | flat_head | choice | sampler over Slot B, gated by compatibility matrix | Slot B table |
| `swing_mode` | enum | both_revolute_opposite / double_acting_spring / active_inactive_astragal | both_revolute_opposite | choice | sampler over Slot C, mutually exclusive | Slot C table |
| `palette_style` | enum | dark_walnut / honey_brown_wood / warm_wood_stone / off_white_steel / anodized_aluminum / wrought_iron_oak | dark_walnut | choice | colorway lookup; ≥4 realistic colorways drawn from sources | palette note below |
| `panel_count` | int | [1, 6] | 3 | conditional | only when infill=raised_panel; per-leaf stacked panels | panels_two L230 (=2), classic L175 (=3), panels_six L135 (=6) |
| `lite_rows` | int | [1, 4] | 2 | conditional | only when infill=divided_lite_glass | six_light_glazed L68 (N_ROWS=2) |
| `lite_cols` | int | [1, 3] | 3 | conditional | only when infill=divided_lite_glass | six_light_glazed L69 (N_COLS=3) |
| `slat_count` | int | [8, 28] | 18 | conditional | only when infill=louvered_slat; vertical pitch derived from count | louvered_infill L311 (=18) |
| `board_count` | int | [4, 9] | 7 | conditional | only when infill=cross_buck_board | x_brace_solid L64 (BOARD_COUNT=7) |
| `opening_width_scale` | float | [0.92, 1.08] | 1.0 | independent | clamp; scales OPENING_W → LEAF_W derived | classic L44, L50 |
| `opening_height_scale` | float | [0.95, 1.05] | 1.0 | independent | clamp; scales OPENING_H → LEAF_H derived | classic L45, L51 |
| `leaf_thickness_scale` | float | [0.85, 1.25] | 1.0 | independent | clamp; scales LEAF_T | classic L52 |
| `jamb_width_scale` | float | [0.8, 1.4] | 1.0 | independent | clamp; scales JAMB_W | classic L54 |
| `swing_open_angle` | float | [1.2, 1.92] rad | 1.4 | conditional | revolute upper limit; spring uses symmetric ±[1.0,1.3] | classic L365, saloon L257 |
| (—) | constraint | — | — | equation | `LEAF_W = (OPENING_W − CENTER_REVEAL − 2·JAMB_REVEAL)/2` (each leaf is half the opening) | classic L50 |
| (—) | constraint | — | — | equation | `panel_h = (LEAF_H − 2·rail − (panel_count−1)·rail)/panel_count` (panel pitch derived from count) | classic L176-L178 |
| (—) | constraint | — | — | inequality | center reveal: `0 ≤ gap(leaf1,leaf0) ≤ 0.05` at closed pose; leaves never interpenetrate | classic L536-L545 |
| (—) | constraint | — | — | inequality | arch coherence: arched_leaf_top → leaf arch radius `ARCH_R = OPENING_W/2`; ring header `r_inner = ARCH_R` (same circle) | arched_glazed L44, L230 |

`palette_style` (≥4 realistic colorways drawn from the sources):

- **dark_walnut** — WALNUT (0.28,0.16,0.09), WALNUT_DARK (0.20,0.11,0.06), BRASS (0.78,0.60,0.22) — classic/panels/louvered/x_brace (L65-L68 family)
- **honey_brown_wood** — honey_wood (0.78,0.47,0.22), wood_shadow (0.58,0.33,0.15), dark_steel surround (0.20,0.22,0.24), bronze handle (0.28,0.24,0.20) — ornate (L69-L73)
- **warm_wood_stone** — warm_wood (0.80,0.48,0.24), board_shadow (0.60,0.34,0.16), light_stone (0.82,0.80,0.74), door_glass (0.30,0.42,0.46,0.45), wrought_iron (0.08,0.08,0.09) — carriage (L60-L64)
- **off_white_steel** — STEEL_OFFWHITE (0.90,0.89,0.85), STEEL_FRAME (0.80,0.80,0.78), STAINLESS (0.75,0.76,0.78), GLASS (0.78,0.85,0.88,0.45), BLUE_RUBBER (0.40,0.55,0.72) — hospital (L78-L82)
- **anodized_aluminum** — ALU_RGBA (0.82,0.83,0.84), GLASS_RGBA (0.62,0.72,0.78,0.45) — storefront/arched_glazed (L63-L64 / L66-L67)
- **wrought_iron_oak** — warm_wood + near-black wrought_iron + light_stone accent (carriage palette recolored for board/carriage leaves)

Target 4-6 colorways; 6 listed, all sourced. Compatibility: glass-heavy palettes
(off_white_steel, anodized_aluminum) pair with glass infills; wood palettes pair with
panel/board/louver infills, but palette is purely material (no topology), so any palette
is legal with any slot combo and only viewer aesthetics gate the default mapping.

## Multiplicity / Copy Logic

This template has **multiple multiplicity axes** (the leaf-count axis is fixed at 2; the
per-leaf feature axes are variable and conditional on the chosen infill).

**Axis 0 — leaves (FIXED N=2, the category identity).**
- `count_param`: none exposed (always 2).
- copied object: the leaf module.
- naming: `door_0` / `door_1` (or `door_leaf_0/1`).
- placement: mirror across X=0 via `sign=+1/−1` or `mirror=True`/`_mirror_x`; both front faces +Y.
- joint policy: door_0 = +Z hinge at left jamb, door_1 = −Z hinge at right jamb
  (`double_acting_spring`: both +Z symmetric; `active_inactive_astragal`: door_1 is an inline
  frame visual, no joint).
- source/gating: classic L316-L379; mirror policy is canonical across all 14 sources.

**Axis 1 — raised panels (variable, only when infill=raised_panel).**
- `count_param`: `panel_count`.
- `N_range`: [1, 6] (real raised-panel doors run 1–6 stacked fields; tests small, product full).
- sampling domain: weighted — small N high frequency (2–4 common), N=5–6 rare.
- copied object: one fielded panel (cut field + molding ring + proud pad) per iteration.
- naming: `panel_{i}` (canonical loop from panels_six; classic/panels_two use `for _` without names — prefer panels_six's `_add_raised_panel` + `panel_{i}` loop).
- placement: regular vertical pitch `panel_h` derived from `panel_count` and rail height.
- joint policy: non-jointed; panels merged (cut/union) into the leaf solid.
- source/gating: panels_six L138-L204, L247-L260.

**Axis 2 — divided lites (variable, only when infill=divided_lite_glass).**
- `count_param`: `lite_rows` × `lite_cols`.
- `N_range`: rows [1,4], cols [1,3] (single pane up to multi-lite French grid; total ≤12).
- sampling domain: weighted — 1×1, 2×2, 2×3 common; larger grids rare.
- copied object: one glass lite per (row,col) + muntin grid bars.
- naming: `lite_{row}_{col}` via nested `for row in range(N_ROWS): for col in range(N_COLS)`.
- placement: regular grid spacing inside the cut window opening; uniform fixed policy.
- joint policy: non-jointed; lites + muntins seated into the window opening.
- source/gating: six_light_glazed L128-L172, L244-L251.

**Axis 3 — louver slats (variable, only when infill=louvered_slat).**
- `count_param`: `slat_count`.
- `N_range`: [8, 28] (full-height horizontal louver field).
- sampling domain: weighted — 14–20 common.
- copied object: one angled slat per iteration from `_build_louver_slat`.
- naming: `door_{idx}_slat_{i}` via `for i in range(slat_count)`.
- placement: equal vertical spacing; constant tilt angle.
- joint policy: non-jointed; slats fixed in the leaf opening.
- source/gating: louvered_infill L179-L191, L311-L320.

**Axis 4 — X-buck boards (variable, only when infill=cross_buck_board).**
- `count_param`: `board_count` (BOARD_COUNT).
- `N_range`: [4, 9] (tongue-and-groove board field width).
- sampling domain: weighted — 6–8 common.
- copied object: one T&G board per iteration from `_make_tg_board`.
- naming: `door_{idx}_board_{i}` via `for i in range(BOARD_COUNT)`.
- placement: side-by-side horizontal pitch across the leaf width + 2 ledgers + 2 diagonal braces.
- joint policy: non-jointed; boards + braces merged into the leaf solid.
- source/gating: x_brace_solid L196-L212, L360-L367.

Per-leaf copy logic is identical on both mirror leaves. Axes 1-4 are mutually exclusive
(selected by `infill_style`); only the matching `*_count` is sampled, others are dormant.

## 拓扑多样性审计

总组合数：Slot A (8) × Slot B (5) × Slot C (3) = **120** legal-before-gating, minus
compatibility exclusions. With the primary multiplicity axis distinct-N counted in
(panel_count distinct {2,3,6} = 3 at minimum, real domain wider):
combined ≈ 120 × 3 = **360**. Even after compatibility pruning
(arched_leaf_top excludes 2 of 5 heads; scalloped_crown needs short leaves; astragal drops
a hinge) the legal slot product stays ≈ 80-100 × multiple N values.

理由：Slot A alone has 8 distinct part-tree topologies (panel-merge, window-cut+pane,
ring+inset, glass-over-xbrace, slat-loop, single-pane, lite-grid, board-loop); Slot C adds
3 distinct joint topologies (2 revolute / 2 spring / 1 revolute + inline leaf). The smallest
two-slot product (C=3 × B=5 = 15) already exceeds 10; A=8 × distinct-N(3) = 24 exceeds 10.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan: `config_from_seed` uses deterministic procedural
sampling (seed=0 not special). Order: (1) sample `swing_mode` (Slot C); (2) sample
`head_style` (Slot B) filtered by the compatibility matrix against swing_mode and the
chosen leaf-top family; (3) sample `infill_style` (Slot A) filtered against head_style
(scalloped/arched leaf tops require reprofile-capable infills); (4) sample the matching
multiplicity `*_count` with weighted small-N draw; (5) sample `palette_style`; (6) sample
the independent continuous scales, derive equation scales (LEAF_W, panel_h, ARCH_R),
project/clamp via the inequality constraints (center reveal, arch coherence). A handful of
regression overrides MAY pin the 6 parent identities (classic / hospital / ornate / carriage
/ saloon / storefront) for visual regression — sparse and justified, NOT the main domain.

Topology target: 1000-seed slot choice tuple distinct should comfortably exceed 100 (8×5×3 slot（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
product before gating = 120, plus distinct-N and palette variation). No
category/compatibility reason to fall short.

Controlled local parameterization: `opening_width_scale`, `opening_height_scale`,
`leaf_thickness_scale`, `jamb_width_scale`, `swing_open_angle` — all clamped in
`resolve_config`. `LEAF_W` is a derived equation of `OPENING_W`; `panel_h` derived from
`panel_count`; `ARCH_R = OPENING_W/2` keeps the two leaf arches + frame ring on one circle.
None of these break the InterfaceSpec (hinge origins stay on jamb faces), the center-reveal
MatingContract, or the multiplicity (counts clamp to N_range). Per §7: sample independent
scales → derive equations → project/clamp inequalities (center reveal, arch coherence) →
resolve conditional ranges (which `*_count` is live, spring vs revolute limits).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | Slot C → Slot B (gated) → Slot A (gated) → matching `*_count` (weighted small-N) → palette → scales | slot_choices_for_seed matches build choices |
| compatibility matrix | see matrix below; mutually exclusive Slot C; LEAF-arch vs FRAME-arch exclusion; scalloped needs short leaf | no double-arch, no floating leaf, no two-LEAF-heads, astragal drops 2nd hinge |
| controlled local variation | 5 continuous scales clamped; LEAF_W/panel_h/ARCH_R derived | proportions vary without breaking hinge origins, center reveal, arch circle, identity |
| regression overrides | optionally pin 6 parent identities for visual regression; sparse + justified | parent-identity snapshots only, not the main seed domain |
| random sweep | seeds 0-49 initial; 0-999 maturity | contract failures |

Compatibility matrix (key gates):

| combo | legal? | policy |
|---|---|---|
| arched_leaf_top × arched_stone_head | NO | double-arch (LEAF arch + FRAME arch); fall back to flat ring header |
| arched_leaf_top × transom_over_flat_head | NO | transom assumes square leaf top; exclude |
| arched_leaf_top × scalloped_crown_head | NO | two LEAF-profile heads on one leaf; mutually exclusive |
| arched_leaf_top × flat_head | YES | arch ring header replaces/augments the flat head (canonical pairing) |
| scalloped_crown_head × full-height square infill | DEGRADE | needs short batwing leaf; pair scalloped with louvered/short leaves only |
| active_inactive_astragal × double_acting_spring | NO | Slot C mutually exclusive |
| active_inactive_astragal × any infill | YES | door_1 becomes inline frame visual; astragal added; 2nd hinge dropped |
| double_acting_spring × louvered_slat / scalloped | YES | canonical batwing pairing |
| any LEAF-arch/scalloped × glass single-pane / divided-lite | YES (reprofile leaf) | arched_glazed proves arch + glass + revolute coexist |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A (leaf infill) | 8 | yes | yes | all part-tree distinct |
| B (head/top) | 5 | yes | yes | LEAF-profile vs FRAME-surround split |
| C (swing) | 3 | yes | yes | 2-revolute / 2-spring / 1-revolute+inline |

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility matrix / gating prevents illegal combos (double-arch, two LEAF-heads, spring+astragal)
- optional regression overrides (≤6 parent identities) are sparse and justified
- final template does not endlessly cycle a small curated table as the main seed domain
- controlled local scales (`opening_width_scale`, `opening_height_scale`, `leaf_thickness_scale`, `jamb_width_scale`, `swing_open_angle`) are clamped and cannot break hinge origins, center reveal, arch circle, or the fixed N=2 leaf count
- cross-part scale dependencies (LEAF_W equation, panel_h equation, ARCH_R coherence, center-reveal inequality) resolved in `resolve_config`, not the builder
- critical InterfaceSpec / MatingContract: two hinge origins on outer jamb faces; closed center reveal 0–0.05; each leaf hinge edge contacts its jamb
- key joints: `frame_to_door_0` REVOLUTE +Z, `frame_to_door_1` REVOLUTE −Z (or both +Z symmetric for spring; single hinge for astragal); upper limit in [1.2,1.92] revolute / ±1.0–1.3 spring
- copied objects follow naming + placement (`door_{idx}`, `panel_{i}`, `lite_{row}_{col}`, `door_{idx}_slat_{i}`, `door_{idx}_board_{i}`; both leaves mirrored)

## Reject cases

- Only one leaf with a hinge AND no astragal/inactive-leaf bridge (looks like a single Door, not a double door).
- Leaves interpenetrate at the center when closed (center reveal < 0 or > 0.05), or a visible gap that reads as a missing leaf.
- Both an arched LEAF top and an arched/transom FRAME head selected together (double-arch) — or two LEAF-profile heads (scalloped + arched) on one leaf.
- `active_inactive_astragal` combined with `double_acting_spring`, or astragal mode that keeps a second real hinge (contradictory swing topology).
- Leaf hinge edge floats off its jamb (hinge origin not on the jamb face) — leaf appears disconnected.
- Per-leaf multiplicity count out of N_range (e.g. panel_count 0 or > 6, lite grid > 12) or asymmetric between the two leaves (mirror broken).
- A `*_count` sampled for a non-matching infill (e.g. slat_count live when infill=raised_panel) producing phantom geometry.
- Scalloped crown applied to a full-height square leaf without reprofiling (crown intersects/floats).

## 与相邻类别的边界

- 不该混入：`door`（single door）— a single door has ONE leaf on a frame; double_door's identity is exactly TWO mirror leaves meeting at a center reveal on a shared frame. Do not collapse to one leaf (except the astragal mode, which still keeps a second leaf as an inline frame visual + bridge).
- 不该混入：`cabinet` / double-leaf cabinet doors — cabinets are box carcasses with shallow swing doors; double_door is a full-height architectural opening with a frame surround, jambs, threshold, and ~2 m leaves, not a storage carcass.
- 不该混入：`window` / French casement — windows are glazed sashes in a sill-bearing frame without a floor threshold or walk-through opening; double_door always has a base/threshold at floor datum and full-height leaves.
- 不该混入：`gate` / `garage_door` — gates/garage doors use sliding, folding, or roll-up motion or pickets; double_door uses leaf revolute/spring swing about vertical jamb axes.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- All leaf modules share the leaf-local frame convention (hinge edge X=0, body toward `sign`, front +Y) and the `sign`/`mirror=True`/`_mirror_x` mirror helper — extract ONE mirror helper.
- Treat louvered_slat as ONE infill module parametrized by Slot C (revolute leaf = louvered_infill `_build_louver_slat` loop; spring leaf = saloon `_louver_grille_mesh`); do NOT make two infill candidates for the same louver field.
- arched_leaf_top is the canonical source for arch-top + matching FRAME ring header (`_arched_frame_header`, same `ARCH_R` circle); pair it ONLY with flat_head, never with arched_stone_head / transom / scalloped.
- active_inactive_astragal is the ONLY source where a leaf is an inline frame visual; it is NOT a mirror-leaf source — special-case the builder (drop door_1 part, emit `frame_inactive_*` + `frame_astragal`).
- Closed-pose center-reveal + jamb-contact are the load-bearing MatingContracts; replicate the classic `expect_gap` (0–0.05) and `expect_contact` (tol 0.02) checks across all infills.
- Prefer panels_six for the panel loop (`panel_{i}` names) and six_light_glazed for the lite grid (`lite_{row}_{col}`); classic/panels_two use unnamed `for _` loops.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C/B | raised_panel + both_revolute + flat_head | rec_classic-...3b44fd42 (parent) | frame L73-L132 ; leaf L135-L228 ; hinges L356-L379 ; head_jamb L94-L98 | canonical spine + frame + flat head + revolute swing |
| S2 | A | vision_window_pushbar_leaf | rec_commercial-hospital-...1fe7f29a (parent) | L93-L171 ; L174-L214 | window-cut + glass + push-bar infill |
| S3 | A/B | carved_circle_motif + transom_over_flat | rec_ornate-...26551efa (parent) | leaf L85-L219 ; surround L222-L302 | ring/inset infill + transom+sidelights head |
| S4 | A/B | upper_glass_muntin_lower_xbrace + arched_stone | rec_arched-carriage-...7b8384ab (parent) | leaf L101-L198 ; stone L254-L331 | glass-over-xbrace infill + stone arch surround |
| S5 | A/B/C | louvered_slat (spring) + scalloped_crown + double_acting_spring | rec_saloon-...1a02f0ce (parent) | crown L73-L102 ; louver L105-L126 ; leaf L129-L204 ; spring L249-L266 | spring swing + scalloped crown + louver mesh |
| S6 | A | full_glass_single_pane_leaf | rec_aluminum-storefront-...38236092 (parent) | L74-L161 ; L164-L189 | narrow-stile single glass pane infill |
| S7 | A | louvered_slat_leaf (revolute) | rec_double_door_var_louvered_infill | L179-L191 ; L311-L320 | louver-slat multiplicity loop (`door_{idx}_slat_{i}`) |
| S8 | A | cross_buck_board_leaf | rec_double_door_var_x_brace_solid | L196-L212 ; L360-L367 | board multiplicity loop (`door_{idx}_board_{i}`) |
| S9 | B | arched_leaf_top (spring) | rec_double_door_var_arched_louvered | `_arched_leaf_profile` L78-L119 ; spring L268-L285 | arch-top leaf profile on spring leaf |
| S10 | B | arched_leaf_top (revolute + ring header) | rec_double_door_var_arched_glazed | `_arched_leaf_frame` L78-L174 ; `_arched_glass_pane` L177-L218 ; `_arched_frame_header` L221-L253 ; hinges L361-L380 | arch-top + matching ring header + glass + revolute |
| S11 | C | active_inactive_astragal | rec_double_door_var_one_active_astragal | astragal L308-L345 ; inline leaf L372-L399 ; hinge L442-L450 | single active hinge + inline inactive leaf + astragal |
| S12 | A(mult) | raised_panel loop | rec_double_door_var_panels_six | L138-L204 ; L247-L260 | `panel_count` loop with `panel_{i}` naming |
| S13 | A(mult) | divided_lite_glass | rec_double_door_var_six_light_glazed | L128-L172 ; L244-L251 | `lite_{row}_{col}` nested grid loop |
| S14 | A(mult) | raised_panel N=2 | rec_double_door_var_panels_two | L136-L187 ; L230, L237-L249 | small-N panel domain coverage (panel_count=2) |
