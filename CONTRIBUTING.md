# Contributing

Use Python 3.11/3.12 and `uv sync --group dev`. Run focused pytest regressions
for changes and use Ruff on changed Python files. See
[docs/architecture.md](docs/architecture.md) and
[docs/generator_construction.md](docs/generator_construction.md) before changing
generator authoring behavior.

Keep paper terminology in public documentation: source map, category blueprint,
generator, Revision Module and procedural sampling. Preserve inherited licenses,
notices and provenance, and do not change source ratings or dataset counts.
Generated data, provider credentials and material libraries stay outside Git.

Describe the changed behavior, how you checked it, and any affected contract
versions when submitting a change.

## Developer Certificate of Origin

All contributions must carry a `Signed-off-by:` line (`git commit -s`),
certifying the contribution under the
[Developer Certificate of Origin 1.1](https://developercertificate.org/):

> By making a contribution to this project, I certify that the contribution was
> created in whole or in part by me and I have the right to submit it under the
> open source license indicated in the file; or that it is based upon previous
> work that, to the best of my knowledge, is covered under an appropriate open
> source license and I have the right to submit that work with modifications
> under the same license; and that I understand and agree that this project and
> the contribution are public and that a record of the contribution is
> maintained indefinitely.
