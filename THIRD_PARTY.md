# Third-Party Software

RFW-A's own code is licensed under [Apache-2.0](LICENSE). That license does not
extend to the third-party packages below; each remains under its own license.
Runtime packages are installed from PyPI as unmodified wheels and are linked or
imported dynamically. Development-only tools are not distributed with the code.

## CAD kernel chain (LGPL family — read this first)

The geometry stack is pulled in by `cadquery` and includes copyleft-licensed
components. Using them as unmodified, dynamically linked pip dependencies is
permitted by their licenses, but **they are not covered by Apache-2.0**:

| Package | License | Note |
| --- | --- | --- |
| `cadquery` | Apache-2.0 | Parametric CAD API |
| `cadquery-ocp` | Apache-2.0 (bindings) | Binary wheels bundle **Open CASCADE Technology (OCCT)**, licensed **LGPL-2.1-only with the OCCT linking exception** |
| `casadi` | LGPL-3.0-or-later | Pulled in by cadquery |
| `nlopt` | MIT (Python wrapper) / **LGPL-2.1-or-later** (compiled library, via the bundled `luksan` routines) | Pulled in by cadquery |
| `vtk` | BSD-3-Clause | Pulled in via `cadquery-ocp` / `trame-vtk` |

## Vendored source

- `sdk/gears.py` and `sdk/v0/gears.py` are adapted from
  [cq_gears](https://github.com/meadiode/cq_gears), copyright 2021
  meadiode@github, distributed under Apache-2.0 consistent with the upstream
  license. See [NOTICE](NOTICE).

## Runtime dependencies

| Package | License |
| --- | --- |
| `aiofiles` | Apache-2.0 |
| `aiohappyeyeballs` | Python Software Foundation License |
| `aiohttp` | Apache-2.0 AND MIT |
| `aiosignal` | Apache-2.0 |
| `annotated-doc` | MIT |
| `annotated-types` | MIT |
| `anthropic` | Apache-2.0 |
| `anyio` | MIT |
| `attrs` | MIT |
| `bm25s` | MIT |
| `cadquery` | Apache-2.0 |
| `cadquery-ocp` | Apache-2.0 (bindings); bundles OCCT (LGPL-2.1-only WITH OCCT exception) |
| `cadquery-ocp-proxy` | Apache Software License |
| `casadi` | LGPL-3.0-or-later |
| `certifi` | Mozilla Public License 2.0 (MPL 2.0) |
| `cffi` | MIT-0 |
| `charset-normalizer` | MIT |
| `click` | BSD-3-Clause |
| `contourpy` | BSD-3-Clause |
| `cryptography` | Apache-2.0 OR BSD-3-Clause |
| `cycler` | BSD-3-Clause |
| `Cython` | Apache-2.0 |
| `distro` | Apache Software License |
| `docstring_parser` | MIT |
| `ezdxf` | MIT |
| `fastapi` | MIT |
| `fonttools` | MIT |
| `frozenlist` | Apache-2.0 |
| `google-auth` | Apache Software License |
| `google-genai` | Apache-2.0 |
| `h11` | MIT License |
| `httpcore` | BSD-3-Clause |
| `httpcore2` | BSD-3-Clause |
| `httpx` | BSD-3-Clause |
| `httpx2` | BSD-3-Clause |
| `idna` | BSD-3-Clause |
| `jiter` | MIT |
| `kiwisolver` | BSD-3-Clause |
| `llvmlite` | BSD-2-Clause AND Apache-2.0 WITH LLVM-exception |
| `manifold3d` | Apache-2.0 |
| `markdown-it-py` | MIT License |
| `matplotlib` | PSF-based (BSD-compatible) |
| `mdurl` | MIT License |
| `more-itertools` | MIT |
| `msgpack` | Apache-2.0 |
| `multidict` | Apache-2.0 |
| `multimethod` | Apache-2.0 |
| `networkx` | BSD-3-Clause |
| `nlopt` | MIT (wrapper); LGPL-2.1-or-later (compiled library) |
| `numba` | BSD-2-Clause |
| `numpy` | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| `openai` | Apache-2.0 |
| `opentelemetry-api` | Apache-2.0 |
| `packaging` | Apache-2.0 OR BSD-2-Clause |
| `pillow` | MIT-CMU (HPND) |
| `propcache` | Apache-2.0 |
| `pyasn1` | BSD-2-Clause |
| `pyasn1_modules` | BSD-2-Clause |
| `pycparser` | BSD-3-Clause |
| `pydantic` | MIT |
| `pydantic_core` | MIT |
| `Pygments` | BSD-2-Clause |
| `pyparsing` | MIT |
| `python-dateutil` | Apache-2.0 OR BSD-3-Clause |
| `python-discovery` | MIT License |
| `python-dotenv` | BSD-3-Clause |
| `python-fcl` | BSD License |
| `PyYAML` | MIT |
| `requests` | Apache Software License |
| `rich` | MIT |
| `rtree` | MIT |
| `runtype` | MIT |
| `scipy` | BSD-3-Clause |
| `six` | MIT |
| `sniffio` | MIT License; Apache Software License |
| `starlette` | BSD-3-Clause |
| `tenacity` | Apache Software License |
| `trame` | Apache-2.0 |
| `trame-client` | MIT |
| `trame-common` | Apache-2.0 |
| `trame-components` | Apache-2.0 |
| `trame-server` | Apache-2.0 |
| `trame-vtk` | BSD-3-Clause |
| `trame-vuetify` | MIT |
| `trimesh` | MIT License |
| `truststore` | MIT |
| `typing-inspection` | MIT |
| `typing_extensions` | PSF-2.0 |
| `tzdata` | Apache-2.0 |
| `urllib3` | MIT |
| `uvicorn` | BSD-3-Clause |
| `vtk` | BSD-3-Clause |
| `websockets` | BSD-3-Clause |
| `wslink` | BSD-3-Clause |
| `yarl` | Apache-2.0 |
| `zstandard` | BSD-3-Clause |

## Development-only tools (not distributed)

| Package | License |
| --- | --- |
| `cfgv` | MIT |
| `distlib` | Python Software Foundation License |
| `execnet` | MIT |
| `filelock` | MIT |
| `identify` | MIT |
| `iniconfig` | MIT |
| `nodeenv` | BSD-3-Clause |
| `platformdirs` | MIT |
| `pluggy` | MIT License |
| `pre_commit` | MIT |
| `pytest` | MIT |
| `pytest-xdist` | MIT |
| `ruff` | MIT |
| `virtualenv` | MIT |
