# Contributing

Use Python 3.11/3.12 and [uv](https://docs.astral.sh/uv/). Set up from the
repository root with `uv sync --locked --group dev`, run the tests with
`uv run pytest`, and run Ruff on changed Python files. If you change generator
authoring behavior, read [docs/architecture.md](docs/architecture.md) and
[docs/generator_construction.md](docs/generator_construction.md) first.

Do not commit credentials, provider API keys, generated asset data, or material
libraries. Preserve inherited licenses, notices and provenance headers, and keep
failure records intact when repairing generators.

Describe the changed behavior, how you checked it, and which commands you ran
when submitting a change.

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
