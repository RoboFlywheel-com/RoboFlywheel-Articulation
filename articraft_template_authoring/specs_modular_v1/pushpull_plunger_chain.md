# Modular Spec: pushpull_plunger_chain

## 1. Core Identity

- Category slug: `pushpull_plunger_chain`
- Dataset path: `data`
- 5-star sample audit: 38 complete 5-star records were read for `model.py`, `revision.json`, `record.json`, prompt, and metadata. The category has enough 5-star samples to proceed.
- Core identity: a grounded guide, frame, or sleeve constrains one or more coaxial plunger rods with PRISMATIC translation along the push-pull axis. Many samples add a carried terminal clevis, hinged tab, or lever output so the sliding rod exposes useful end actuation instead of being a bare block.
- Required articulation identity: at least one PRISMATIC joint along the main plunger axis; optional additional PRISMATIC stages in series and optional REVOLUTE output flap/lever.
- Non-identity variation: paint, material color, decorative bolt count, and small scale-only changes are not valid module candidates.

## 2. Slot Graph

```text
grounded_support
  -> guide_module        [FIXED or integrated]
  -> primary_plunger     [PRISMATIC, +X push-pull axis]
      -> secondary_plunger? [PRISMATIC, +X, telescoping variants]
          -> terminal_output [FIXED clevis/pad or REVOLUTE flap]
```

## 3. Candidate Module Table

| Slot | Candidate | Structural/function difference | 5-star source |
|---|---|---|---|
| grounded_support | compact_bridge_guide | Small bridge frame with top bar, paired posts, rear stop, and front ears supporting a single slider plus hinged tab. | `data/records/rec_pushpull_plunger_chain_c7ca5be6000d495396085a39afa1e027/revisions/rev_000001/model.py:L47-L65`, parts/articulation `L103-L170` |
| grounded_support | fork_sleeve_frame | Forked cheek frame with base bridge, mount block, circular sleeve, and pivot ears for an independent lever. | `data/records/rec_pushpull_plunger_chain_e2c53e13b8a5433f8e812f28d35566c2/revisions/rev_000001/model.py:L66-L123`, parts/articulation `L174-L230` |
| grounded_support | rail_bed_sleeve | Long base plate with center and side rails, fixed guide sleeve, bushings, pedestal, clamp, and clamp bolts. | `data/records/rec_pushpull_plunger_chain_64b64997d8dd44d9a8bd4b9c6751fd26/revisions/rev_000001/model.py:L63-L122` |
| grounded_support | bored_base_stack | Bored base block plus fixed guide stack for stepped coaxial ejector rods. | `data/records/rec_pushpull_plunger_chain_c89fe24895d849879d484ce4d5c86e6d/revisions/rev_000001/model.py:L106-L122`, assembly `L149-L179` |
| guide_module | open_channel | U-channel/open rail mouth where the rod slides visibly between side rails. | `rec_pushpull_plunger_chain_813da5de81434fbd994b9b766271e5bb/model.py:L53-L85` |
| guide_module | circular_sleeve | Cylindrical or annular sleeve/bushing coaxial with the rod. | `rec_pushpull_plunger_chain_e2c53e13b8a5433f8e812f28d35566c2/model.py:L94-L101`, `rec_pushpull_plunger_chain_64b64997d8dd44d9a8bd4b9c6751fd26/model.py:L84-L96` |
| primary_plunger | rectangular_rod_with_button | Rectangular shank plus wider tip and rear button. | `rec_pushpull_plunger_chain_c7ca5be6000d495396085a39afa1e027/model.py:L68-L81`, visual parts `L117-L135` |
| primary_plunger | round_stepped_rod | Round tail/collar/rod/tip cylinder stack. | `rec_pushpull_plunger_chain_e2c53e13b8a5433f8e812f28d35566c2/model.py:L126-L150` |
| primary_plunger | carried_sleeve_plunger | Rod carries its own guide sleeve, bushings, bridge, shoe, and optional push pad. | `rec_pushpull_plunger_chain_64b64997d8dd44d9a8bd4b9c6751fd26/model.py:L124-L183` |
| primary_plunger | stepped_ejector_section | Short stepped rod sections nested through a guide stack. | `rec_pushpull_plunger_chain_c89fe24895d849879d484ce4d5c86e6d/model.py:L137-L146`, parts `L181-L200` |
| secondary_plunger | none | Single sliding plunger only, still category-valid when paired with terminal output. | `rec_pushpull_plunger_chain_c7ca5be6000d495396085a39afa1e027/model.py:L144-L170` |
| secondary_plunger | telescoping_second_stage | Additional PRISMATIC rod nested inside/carrying from the first stage. | `rec_pushpull_plunger_chain_c89fe24895d849879d484ce4d5c86e6d/model.py:L223-L245` |
| secondary_plunger | triple_telescoping_stage | Three serial PRISMATIC rods with carried sleeves/collars. | `rec_pushpull_plunger_chain_64b64997d8dd44d9a8bd4b9c6751fd26/model.py:L221-L247` |
| terminal_output | hinged_tab | REVOLUTE flap/tab on the guide or rod nose. | `rec_pushpull_plunger_chain_c7ca5be6000d495396085a39afa1e027/model.py:L84-L100`, hinge `L159-L170`; `rec_pushpull_plunger_chain_813da5de81434fbd994b9b766271e5bb/model.py:L120-L132`, `L196-L209` |
| terminal_output | fork_lever | Separate pivoting lever/cam adjacent to the sleeve. | `rec_pushpull_plunger_chain_e2c53e13b8a5433f8e812f28d35566c2/model.py:L153-L171`, hinge `L220-L230` |
| terminal_output | terminal_clevis | Fork/clevis at the output rod with a cross pin. | `rec_pushpull_plunger_chain_64b64997d8dd44d9a8bd4b9c6751fd26/model.py:L201-L219`; `rec_pushpull_plunger_chain_c89fe24895d849879d484ce4d5c86e6d/model.py:L195-L200` |

## 4. Interface Points

- `support.slide_axis`: +X line through the guide/sleeve center; provides `parent_axis=(1,0,0)` and `MotionLimits(lower=0, upper=stroke)`.
- `support.front_face`: fixed or near-fixed guide exit where terminal outputs must sit ahead of the housing.
- `plunger.upstream_axis`: child origin on the rod centerline; consumes the support slide interface.
- `plunger.downstream_axis`: optional serial PRISMATIC interface for secondary rods; same +X axis.
- `plunger.terminal_mount`: fixed clevis/pad or REVOLUTE hinge point, usually near the front end of the last rod.
- `lever_or_tab.pivot`: Y-axis REVOLUTE hinge, separated from the slide axis enough to avoid current-pose overlap.

## 5. Multiplicity / Copy Logic

- `stage_count=1`: support + primary plunger + optional hinged tab/lever.
- `stage_count=2`: support + primary plunger + secondary plunger + fixed clevis or pad.
- `stage_count=3`: support + three carried/nested plunger sections; terminal clevis required.
- Repeated PRISMATIC stages copy the +X axis, decreasing rod radius/width and decreasing stroke from rear to front.
- Terminal outputs are not repeated. A hinged tab or lever may appear only once on the guide/rod nose; a terminal clevis appears only on the final stage.

## 6. Compatibility Matrix

| Combination | Status | Reason |
|---|---|---|
| compact_bridge_guide + rectangular_rod_with_button + hinged_tab | allowed | Source-backed single-slider with front tab. |
| fork_sleeve_frame + round_stepped_rod + fork_lever | allowed | Source-backed sleeve plus independent lever/cam. |
| rail_bed_sleeve + carried_sleeve_plunger + triple_telescoping_stage + terminal_clevis | allowed | Source-backed carried sleeve cascade. |
| bored_base_stack + stepped_ejector_section + telescoping_second_stage + terminal_clevis | allowed | Source-backed coaxial nested ejector stack. |
| open_channel + rectangular rod + hinged_tab | allowed | Open rail block and rod-carried flap are both 5-star structures. |
| hinged_tab with triple_telescoping_stage | reject | Samples with multi-stage plungers use clevis/pad outputs; a hinged flap would collide or misrepresent the long coaxial stack. |
| fork_lever with stage_count > 1 | reject | Fork lever samples are single plunger plus lever/cam, not telescoping rods. |
| PRISMATIC axis not +X | reject | All cited 5-star push-pull mechanisms translate along the rod axis. |

## 7. Topology Diversity Audit

- Support topology varies between compact bridge, fork sleeve frame, long rail bed, open U-channel, and bored base/guide stack.
- Moving topology varies between single rectangular rod, round stepped rod, carried-sleeve rod, two-stage telescoping rod, and three-stage cascade.
- Output topology varies between no separate moving output, REVOLUTE flap/tab, independent REVOLUTE lever, and fixed terminal clevis.
- Joint topology must cover `1P+1R`, `1P`, `2P+F`, and `3P+F` families across sweep seeds.

## 8. Procedural Sampling / Sweep Plan

- `config_from_seed(seed)` uses `random.Random(seed)`; seed 0 is not special.
- Sample implemented topology family first, then sample compatible modules within that family. Do not use a modulo table or sample modules not built/tested.
- Sweep seeds must cover support family, stage count, plunger profile, terminal output, stroke length, rod radius/width, and frame spacing.

## 9. Controlled Local Parameterization

- Stroke range: `0.035-0.18` m, decreasing for later telescoping stages.
- Rod radius/half-width: controlled per profile; secondary rods are smaller than upstream rods.
- Guide clearance: visual sleeves/rails must sit around, not deeply intersect, current-pose moving rods unless explicitly allowed by tests.
- Terminal hinge limits: flap/lever lower/upper bounds remain small enough to preserve closed-pose identity.
- Support length scales with stage count so terminal clevis remains ahead of guide front.

## 10. Validator

- Must contain at least one PRISMATIC articulation with axis `(1, 0, 0)`.
- Stage count must match the selected topology family.
- For flap/lever families, must contain a REVOLUTE joint with Y-axis hinge.
- For telescoping families, all serial PRISMATIC joints must be coaxial and ordered parent-to-child.
- Terminal output must be on the final moving stage or a source-backed guide pivot.
- Current pose must have one root, no disconnected geometry islands, and no unapproved 3D overlaps.

## 11. Reject Cases

- A plain decorative cylinder sliding without a guide/frame.
- Color/material-only candidate changes.
- A revolute-only lever without any push-pull PRISMATIC plunger.
- Telescoping rods sampled with a flap/lever terminal that was not implemented/tested.
- Non-coaxial PRISMATIC axes or mixed random axes.
- Replacing source-backed sleeve/rail/clevis complexity with a single anonymous box when the module claims that source candidate.
