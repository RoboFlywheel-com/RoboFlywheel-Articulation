# RFW-A development guidelines

Use Python 3.11/3.12 and `uv sync --group dev`. Read `docs/architecture.md` and
`docs/generator_construction.md` before changing generator authoring behavior.
`rfwa` is the public CLI; the inherited `sdk`, `agent`, `storage`, `cli` and
`articraft` modules retain compatibility with existing source programs.

Keep paper terminology in public documentation: source map, category blueprint,
generator, Revision Module and procedural sampling. Preserve inherited licenses,
notices and provenance. Do not change source ratings or dataset counts during
code migration. Generated data, provider credentials and material libraries stay
outside Git. When an external agent creates source records, follow
`EXTERNAL_AGENT_DATA.md` through `rfwa source external ...`.

Default to practical generation: accept a generator at a configurable sampled
pass rate (90% by default), export passing assets and skip/report failing seeds.
Keep incomplete blueprints/provenance and uncovered corners as repair diagnostics
rather than blocking an otherwise useful legacy generator. `--strict` is opt-in
for formal all-cases-pass release checks. Preserve failure records across repairs.
Sampling and editing must not call a model. Do not describe visual-only editing
outputs as simulation-ready assets.

Run focused pytest regressions for changes; use Ruff on changed Python files.
The inherited test baseline in `tests/known_failures.txt` documents old failures;
do not add new failures to it. Keep tests independent of local source-record and
material-library paths. Build artifacts and validation logs belong in `/tmp`.
