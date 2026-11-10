# pictureX_0611_industrial_crane_featuring_advanced_hydraulic — SourceMap

source_map_schema: 1
export_category: pictureX_0611_industrial_crane_featuring_advanced_hydraulic
picture_category: 0611
picture_subcategory: industrial_crane_featuring_advanced_hydraulic
category_scope: A mobile hydraulic shop crane (engine hoist) — a wheeled floor frame with a mast, a boom that luffs on a hydraulic ram fed by a hand pump, and a hook at the boom tip. Tower cranes, truck-mounted cranes and fixed jib hoists without a rolling frame are outside this host.

sync_records:
  - rec_industrial_crane_hydraulic_var_counterweight_base_refill
  - rec_industrial_crane_hydraulic_var_foldable_shop
  - rec_industrial_crane_hydraulic_var_knuckle_boom_refill
  - rec_industrial_crane_hydraulic_var_swing_out_outriggers_gt10
  - rec_industrial_crane_hydraulic_var_telescoping_boom_refill
  - rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8
  - rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_industrial_crane_hydraulic_var_counterweight_base_refill/rev_000001 | reviewed | used | Adds a ballast box and a stiffened rear beam to the base so the crane balances a heavier load. Distinct frame family. |
| rec_industrial_crane_hydraulic_var_foldable_shop/rev_000001 | reviewed | used | Rebuilds the base as a folding shop frame with a hinged mast strut and shorter stowable legs. Distinct frame family. |
| rec_industrial_crane_hydraulic_var_knuckle_boom_refill/rev_000001 | reviewed | used | Replaces the sliding extension with a `secondary_jib` on its own REVOLUTE knuckle plus a second `jib_cylinder`/`jib_rod` ram. Distinct boom family with four extra joints. |
| rec_industrial_crane_hydraulic_var_swing_out_outriggers_gt10/rev_000001 | reviewed | used | Adds indexed `outrigger_i` legs that swing out on REVOLUTE joints to widen the footprint. Its base is otherwise the origin A-frame, so the outriggers are a stabilizer component, not a base family. |
| rec_industrial_crane_hydraulic_var_telescoping_boom_refill/rev_000001 | reviewed | used | Replaces the single extension with a chain of indexed `boom_stage_i` PRISMATIC sections. Distinct boom family. |
| rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8/rev_000001 | reviewed | used | Origin anchor: A-frame rolling base with swivel casters, mast, luffing boom with a single sliding extension, lift ram with pump handle and a swivel hook. |
| rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d/rev_000001 | reviewed | used | Second origin: a compact shop crane whose base is one short welded frame with a low mast and a stubbier boom. Different base family from 001. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| frame_style | a_frame_base | crane base | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8/rev_000001 | model.py:L161-L295 | structure | The long A-frame legs, the cross beam and the tall welded mast of the classic engine hoist. |
| frame_style | compact_shop_base | crane base | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d/rev_000001 | model.py:L146-L219 | structure | One short welded box frame with a low mast — a compact shop crane rather than the long A-frame. |
| frame_style | counterweight_base | crane base | rec_industrial_crane_hydraulic_var_counterweight_base_refill/rev_000001 | model.py:L165-L335 | structure | A ballast box and a stiffened rear beam behind the mast, which no other base carries. |
| frame_style | foldable_shop_base | crane base | rec_industrial_crane_hydraulic_var_foldable_shop/rev_000001 | model.py:L162-L314 | structure | A folding shop frame: shortened stowable legs and a braced mast strut instead of the welded A-frame. |
| stabilizer | fixed_stance | base stance | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8/rev_000001 | model.py:L161-L295 | structure | The A-frame stands on its own leg run and casters; there is no separate ground-bearing member. |
| stabilizer | swing_out_outriggers | swing-out stabilizer legs | rec_industrial_crane_hydraulic_var_swing_out_outriggers_gt10/rev_000001 | model.py:L140-L221 | structure+motion | `_add_outrigger` bolts an arm beam, pivot barrel, foot leg and foot pad to the frame on its own REVOLUTE swing (L189-L197); the base underneath is unchanged. |
| boom_style | single_extension | crane boom | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8/rev_000001 | model.py:L296-L410 | structure+motion | One boom with a single `boom_extension` on a PRISMATIC joint (L359-L367) and the hook swivelling at its tip. |
| boom_style | telescoping_stages | crane boom | rec_industrial_crane_hydraulic_var_telescoping_boom_refill/rev_000001 | model.py:L373-L479 | structure+motion | A chain of indexed `boom_stage_i` sections, each on its own PRISMATIC joint (L400-L410), so the boom telescopes in stages. |
| boom_style | knuckle_jib | crane boom | rec_industrial_crane_hydraulic_var_knuckle_boom_refill/rev_000001 | model.py:L374-L593 | structure+motion | A `secondary_jib` folds on a REVOLUTE knuckle (L430-L438) driven by its own `jib_cylinder`/`jib_rod` ram (L562-L593). |
| hook_style | chain_hook | load hook | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8/rev_000001 | model.py:L369-L400 | structure | A slender r=0.006 zig-zag chain run hanging 0.275 m and curling into a small hook, built as one continuous spline tube plus a `swivel_body` collar. |
| hook_style | ball_hook | load hook | rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d/rev_000001 | model.py:L281-L296 | structure | A short rigid r=0.009 `chain_shank`, a `hook_bowl` Sphere swivel and three heavy r=0.012-0.015 forged bends — a different hanging assembly from 001's chain. |

## Coverage note

All seven active records in the `0611 / industrial_crane_featuring_advanced_hydraulic` workbench
pool are reviewed and all seven contribute a candidate. The rolling casters and the lift ram with
its three-piece pump lever (`handle_hub` + `handle_bar` + `handle_grip`, identical in both origin
lineages) are the shared host. The hook is **not** shared: the two origins build two different
hanging assemblies, so it is its own slot.

The outrigger fork keeps the origin base and only bolts stabilizer legs onto it, so the outriggers are
their own slot rather than a fifth base family; every base candidate can carry them because the
brackets sit outboard of the leg run, clear of the braces, the ballast straps, the fold lugs and the
mast struts.

`core_domain = 4 (frame_style) x 2 (stabilizer) x 3 (boom_style) x 2 (hook_style) = 48`; with the
`caster_count` multiplicity (4 or 6 swivel caster stations, each a caster plus a wheel on two joints)
`raw_domain = 96`.
