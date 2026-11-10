# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import sys

from agent.template_sweep import _compile_one

SLUG = "box_fan_with_control_knob"
STEM = "box_fan"


def main() -> int:
    spec = sys.argv[1] if len(sys.argv) > 1 else "0-15"
    seeds: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            seeds.extend(range(int(a), int(b) + 1))
        elif chunk:
            seeds.append(int(chunk))
    n_pass = 0
    for seed in seeds:
        outcome = _compile_one(SLUG, STEM, seed, sdk_package="sdk", motion_qc=True)
        if outcome.verdict == "pass":
            n_pass += 1
            print(f"seed {seed:3d}: PASS")
        else:
            det = (outcome.failure_details or "").strip().replace("\n", "\n    ")
            print(f"seed {seed:3d}: FAIL [{outcome.failure_type}]\n    {det[:1500]}")
    print(f"\n{n_pass}/{len(seeds)} passed ({n_pass / len(seeds):.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
