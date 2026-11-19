<div align="center">

# RFW-A: Agentic Procedural Generation of 400K Articulated Assets over 500 Categories

Yuanbo Lyu<sup>1,\*</sup>, Changjian Pan<sup>2,3,\*</sup>, Saining Zhang<sup>2,4,\*,†</sup>, Yi Yang<sup>1,\*</sup>, Peishuo Li<sup>4</sup>, Zhiheng Li<sup>2</sup>, Jialu Liu<sup>2</sup>, Junhao Chen<sup>2</sup>, Jiawei Weng<sup>1</sup>, Yupeng Gao<sup>5</sup>, Weiqing Xiao<sup>5</sup>, Wenyi Li<sup>1,2</sup>, Jiarui Guo<sup>1,2</sup>, Rui Zhang<sup>1,2</sup>, Jingrun Du<sup>1,2</sup>, Weiyi Lin<sup>1</sup>, Zenan Meng<sup>1,‡</sup>, Hu Wei<sup>1,‡</sup>, Lin Qu<sup>1</sup>, Zongzheng Zhang<sup>2</sup>, Hao Zhao<sup>2</sup>, Chaojian Li<sup>6,‡</sup>

<sup>1</sup>Alibaba Group &nbsp; <sup>2</sup>Tsinghua University &nbsp; <sup>3</sup>Peking University &nbsp; <sup>4</sup>Nanyang Technological University &nbsp; <sup>5</sup>Nanjing University &nbsp; <sup>6</sup>The Hong Kong University of Science and Technology

<sub>\*Equal contribution. †Project leader. ‡Corresponding authors.</sub>

</div>

<div align="center">
  <a href="https://roboflywheel-com.github.io/RoboFlywheel-Articulation/"><img src="https://img.shields.io/badge/Project%20Page-333399.svg?logo=googlehome" height="22px"></a>
  <a href="https://arxiv.org/abs/2610.40333"><img src="https://img.shields.io/badge/arXiv-2610.40333-b5212f.svg?logo=arxiv" height="22px"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" height="22px"></a>
  <a href="https://modelscope.cn/datasets/RoboFlywheel/Articulation"><img src="https://img.shields.io/badge/ModelScope-Dataset-624AFF.svg" height="22px"></a>
  <a href="README_zh.md"><img src="https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87%E8%AF%B4%E6%98%8E-green.svg" height="22px"></a>
</div>

<div align="center">
  <img src="figures/Teaser_PV_A.png" alt="RFW-A-400K overview" width="95%">
</div>

**RoboFlywheel-Articulation (RFW-A)** combines agentic synthesis with procedural
generation: agents construct reusable category-level generators once, and
procedural execution then produces diverse simulation-ready articulated assets
with no further model calls or token charges.

[中文说明](README_zh.md) · [Generator construction](docs/generator_construction.md) · [Sampling and editing](docs/usage.md) · [Paper-to-code mapping](docs/architecture.md) · [External source data](EXTERNAL_AGENT_DATA.md)

## 📰 News

- **November 2026:** RFW-A-Light dataset released on [ModelScope](https://modelscope.cn/datasets/RoboFlywheel/Articulation) — 10,000 articulated assets across 531 categories.
- **October 2026:** Open-source code release under Apache-2.0 — generator-construction tools, procedural sampling runtime, articulated-object SDK, mechanical checks, material binding, and directed editing. Paper on [arXiv](https://arxiv.org/abs/2610.40333).

## ✨ Highlights

- **Category-level reuse** — agents construct a generator once per category; procedural sampling reuses its construction logic across seeds with no model inference
- **RFW-A-400K** — 402,410 articulated assets across more than 500 object categories, each with explicit part structure, kinematics, estimated physical properties, and reproducible generation parameters
- **Checked generation** — sampled assets pass geometry, URDF and sampled-motion checks; failing seeds are logged and skipped
- **Cross-simulator evidence** — the paper evaluates structural and kinematic validity and compatibility in Genesis, PyBullet, MuJoCo, and Isaac Sim

## 📊 Resource at a Glance

| Release | Assets | Categories | Availability |
| --- | ---: | ---: | --- |
| RFW-A-400K (paper dataset) | 402,410 | 531 | see dataset section |
| RFW-A-Light | 10,000 | 531 | [ModelScope](https://modelscope.cn/datasets/RoboFlywheel/Articulation) |

Each light-release asset directory contains `model.urdf`, `part_physics.json`
(whole-body and per-part physical properties), `appearance.json` (PBR material
bindings), meshes and textures, and affordance annotations. The dataset page
documents simulator import notes for PyBullet, MuJoCo, Genesis, SAPIEN, and
Isaac Sim.

## 🛠️ Quick Start

Python 3.11 or 3.12 and [uv](https://docs.astral.sh/uv/) are required. Run these
commands from the repository root (Linux is the tested platform):

```bash
uv sync --locked --group dev
uv run rfwa generators
uv run rfwa config single_revolute_hinge --seed 0
uv run rfwa sample single_revolute_hinge --seeds 0-2 --out /tmp/rfwa-hinges
```

Sampling runs geometry, URDF and sampled-motion checks and writes each passing
seed's assets and a `sampling.json` construction record. It uses no model API.
The output directory must be empty. Bundled generators include legacy programs;
the inventory is not a claim that every generator meets the current release gate.

For new categories, use the source-map and blueprint tools, implement the
generator, then assess the generator before sampling at scale:

```bash
uv run rfwa author --help
uv run rfwa check <generator> --stage random-16
uv run rfwa check <generator> --stage random-36
uv run rfwa release <generator>
```

`check` and `release` default to a practical 90% sampled pass-rate threshold;
default readiness checks use random-16 and random-36. Passing assets are
retained; failing seeds are logged and skipped. Use `--pass-threshold` to adjust
the target, or `--strict` to opt into all-cases-pass, complete-coverage and
provenance requirements.

The generator-construction pipeline is not tied to Articraft sources. Any
procedural CAD pipeline — code-authored parametric geometry with explicit part
structure and articulation — can supply source assets: an external agent or
human author imports them with `rfwa source external` (see
[EXTERNAL_AGENT_DATA.md](EXTERNAL_AGENT_DATA.md)), after which source maps,
blueprints and generators are built the same way.

## 🗂️ What This Code Release Contains

| Directory | Contents |
| --- | --- |
| `rfwa/` | Public CLI: `generators`, `config`, `sample`, `author`, `check`, `release`, `source` |
| `agent/` | Source maps, blueprint design, preflight and motion checks, template registry, sampling sweeps |
| `sdk/` | Component construction, dependency resolution and assembly runtime used by generators |
| `articraft/` | Inherited Articraft runtime: appearance and material grounding, physical-property annotation |
| `articraft_template_authoring/` | Category blueprint designs and authoring guidance |
| `controlled_morphology/`, `specific_editing/` | Directed editing of configurations, geometry and articulation |
| `storage/`, `cli/` | Source records and revisions; compatibility CLI |
| `data/`, `viewer/` | Bundled frozen pools and prompts; local asset viewer |
| `docs/` | [Architecture](docs/architecture.md), [generator construction](docs/generator_construction.md), [usage](docs/usage.md), [verification](docs/verification.md) |
| `tests/` | Local regression tests |

This repository contains code only. The 400K dataset, source-record collection
and frozen PBR material library are separate artifacts and are not bundled in
this checkout; the paper's evaluation scripts, training checkpoints and
cross-simulator experiment harness are likewise not included. Local mechanical
and sampled-motion checks do not reproduce those experiments.

Material-grounded export accepts `--library-pointer /path/to/unified/latest.json`.
The six physical properties are estimated annotations; material binding
preserves authored URDF inertias.

## 📦 Dataset

The **RFW-A-Light** release is available on ModelScope:
[RoboFlywheel/Articulation](https://modelscope.cn/datasets/RoboFlywheel/Articulation)
— 10,000 articulated assets across 531 categories under Apache-2.0. Every asset
is one deterministic `generator(seed)` draw of a category-level procedural
generator, so it is reproducible from its category and seed. The dataset page
documents the directory layout, per-engine import notes, and friction/fixed-base
caveats. The full RFW-A-400K collection is a separate artifact; its release
terms will accompany it.

## 📖 Citation

The associated manuscript is **RFW-A: Agentic Procedural Generation of 400K
Articulated Assets over 500 Categories**
([arXiv:2610.40333](https://arxiv.org/abs/2610.40333), October 2026). See also
[CITATION.cff](CITATION.cff).

```bibtex
@misc{rfwa2026,
  title={RFW-A: Agentic Procedural Generation of 400K Articulated Assets over 500 Categories},
  author={Yuanbo Lyu and Changjian Pan and Saining Zhang and Yi Yang and Peishuo Li and Zhiheng Li and Jialu Liu and Junhao Chen and Jiawei Weng and Yupeng Gao and Weiqing Xiao and Wenyi Li and Jiarui Guo and Rui Zhang and Jingrun Du and Weiyi Lin and Zenan Meng and Hu Wei and Lin Qu and Zongzheng Zhang and Hao Zhao and Chaojian Li},
  year={2026},
  eprint={2610.40333},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  doi={10.48550/arXiv.2610.40333}
}
```

## 🙏 Acknowledgements

Validation and loading examples use [Genesis](https://genesis-embodied-ai.github.io/), PyBullet, MuJoCo, Isaac Sim, and SAPIEN. External models, software, and separately distributed datasets retain their own terms; see [THIRD_PARTY.md](THIRD_PARTY.md).

## License

Original source code is licensed under [Apache-2.0](LICENSE), with inherited
notices retained in [NOTICE](NOTICE) and third-party dependency licenses listed
in [THIRD_PARTY.md](THIRD_PARTY.md). The Apache-2.0 grant covers only this
repository's original code: it does **not** extend to third-party model weights,
simulation runtimes, or separately distributed datasets, each of which remains
under its own license. Dataset and material-library terms accompany their own
releases. [Contribution guidelines](CONTRIBUTING.md) describe local checks and
release boundaries.

---

## Category scope of this release

The bundled generator inventory lists **507 registered generator templates** (see
`agent/template_registry.py` for the authoritative list). Categories whose primary
use is military, law-enforcement crowd control, surveillance, or weapon/unmanned
platforms are **not included** in this public release, and their implementations,
specs, source records and tests have been removed. The paper's dataset figures
(402,410 assets across more than 500 categories) describe the full research
dataset; the code release scope is defined by the registry in this repository.
