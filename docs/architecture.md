# RFW-A paper-to-code mapping

**Default policy:** prioritize usable output. Checks use a configurable 90%
sampled pass-rate threshold. Sampling exports passing assets and logs/skips failed
seeds; a mixed batch returns `partial` and succeeds if it produces any valid assets.
Legacy blueprint/source gaps and corner failures are diagnostics, not default
category-wide blockers. Add `--strict` to `check` or `release` only when you want
all-cases-pass and complete coverage/provenance. The stricter requirements described
below refer to that optional mode.


RFW-A constructs a category-level generator once, then reuses its construction
logic across seeds. The code keeps the stages separate so sampling never needs
source records, blueprints, or provider credentials at runtime.

| Paper concept | Implementation | Responsibility |
| --- | --- | --- |
| Source Agent and source map | `agent/source_maps.py`, `rfwa import-source`, `rfwa author source-map-*` | Review the source pool, identify reusable component code, retain record/revision and exact source spans |
| Architect Agent and category blueprint | `agent/template_design.py`, `articraft_template_authoring/designs/` | Component choices, parameters, derivations, interfaces, multiplicities and assembly bindings |
| Code Agent and generator | `agent/templates/`, `agent/template_registry.py`, `sdk/` | `config_from_seed`, `resolve_config`, component construction, assembly and author tests |
| Revision Module | `agent/template_preflight.py`, `agent/template_check.py`, `rfwa/revision.py` | Blueprint consistency, cumulative configuration tests, motion checks, coverage, sampling readiness and optional strict certification |
| Repair Agent | Structured `repair_findings`, role instructions in `docs/roles/` | Revise the blueprint or implementation and rerun retained cases |
| Procedural sampling | `rfwa sample`, `agent/template_sweep.py` | Seeded construction and checked URDF/mesh export without model calls |
| Material grounding | `articraft/appearance/`, `articraft/materialization.py` | Frozen class pools, seeded material draws, portable appearance and six physical-property annotations |
| Directed editing | `specific_editing/`, `controlled_morphology/` | Change configuration inputs and rebuild dependent geometry and articulation |
| Source asset authoring | `agent/`, `storage/`, `rfwa source` | Existing per-asset generation, external-agent workflow, records and revisions |

## Runtime and authoring boundaries

The four agents are authoring roles. The included tools prepare artifacts and
produce repair diagnostics; a human or external agent coordinates their execution.
There is no newly claimed automatic four-agent service. A released generator is
ordinary Python, not a model call or interpreter for a blueprint graph.

Public RFW-A terminology maps to legacy implementation names as follows:
`SourceMap` = source map, `TemplateDesign` = category blueprint, `template` =
category generator. Those internal names and the `sdk`, `agent.templates`,
`articraft` packages remain stable for existing programs. The Python distribution
and primary CLI are named `rfwa`; `articraft` remains a compatibility CLI.

Mechanical checks run before material binding. The optional strict RFW-A release gate uses a
100% pass threshold for fixed seeds 0–15 and 0–35, followed by supplemental
component choices, multiplicity boundaries and authored corner configurations.
Previously failed corner configurations are retained in the state directory
across code changes. The final gate checks passing evidence for every declared
domain value, not merely that a value was sampled. New continuous boundaries and
important coupled configurations must be declared as authored corners.

`release.json` records a mechanical-code fingerprint and blueprint/source-map
hashes. It describes the current checkout and tested cases; it is not a guarantee
of all possible parameter combinations or a dynamics certificate. Sampling can be
used during development and explicitly records `release_status: not_evaluated`.
Keep the same `--state-root` across repair rounds to preserve regression cases.
Do not run concurrent checks for the same generator in the same state directory.

## Data and simulator boundaries

The paper's RFW-A-400K release contains 402,410 assets across more than 500
categories. Those dataset counts describe the paper artifact, not a local export
or the number of independently certified programs in this initial code migration.

The paper's four-simulator experiments are distinct from the local mechanical
checker. This checkout exports URDFs and motion diagnostics; it does not bundle
the original Genesis/PyBullet/MuJoCo/Isaac Sim evaluation harness or downstream
training checkpoints. Exporting an asset does not reproduce those experiments.

Material grounding uses a separately supplied frozen library. The paper describes
8,295 materials, 124 leaf classes and 18 families; no empty replacement library is
shipped here. The exporter copies physical-property annotations to `physics.json`
and preserves authored URDF mass/inertia. Simulator-specific friction/material
setup requires the corresponding simulator adapter.
