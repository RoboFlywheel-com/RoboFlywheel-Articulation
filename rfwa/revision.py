# SPDX-License-Identifier: Apache-2.0

"""Practical generation checks with optional strict release certification.

Legacy development verdicts remain available through `articraft template`.
They are not release certificates. Failed corner configurations are retained
across changes; fixed random seed cases are rerun by each cumulative sweep.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

from rfwa.generators import registered_stem


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def release_findings(report: dict[str, Any]) -> list[str]:
    """Fail closed when the evidence needed for a release is absent."""
    findings = []
    if report.get("stage") != "corner" or report.get("verdict") != "pass":
        findings.append("final configuration and motion checks must pass")
    if report.get("template_mode") != "strict":
        findings.append("a category blueprint and TEMPLATE_DOMAIN are required")
    preflight = report.get("preflight", {})
    if preflight.get("status") != "pass":
        findings.append("blueprint/code preflight must pass")
    sweep = report.get("random_sweep", {})
    if sweep.get("failed") != 0 or sweep.get("passed") != 36:
        findings.append("all 36 retained random seeds must pass")
    if sweep.get("joint_motion_coverage", {}).get("status") != "pass":
        findings.append("joint motion coverage must pass")
    corner = report.get("corner_stage", {})
    if corner.get("status") != "pass" or corner.get("failed") != 0:
        findings.append("all corner and regression configurations must pass")
    coverage = sweep.get("candidate_coverage", {})
    rows = coverage.get("candidates", [])
    if not rows:
        findings.append("declared choices need passing coverage evidence")
    passing_configs = [
        case["config"]
        for case in corner.get("cases", [])
        if case.get("status") == "pass" and isinstance(case.get("config"), dict)
    ]
    for row in rows:
        covered = bool(row.get("passing_seeds")) or any(
            config.get(row["slot"]) == row["candidate"] for config in passing_configs
        )
        if not covered:
            findings.append(f"uncovered choice: {row['slot']}={row['candidate']!r}")
    return findings


def check_generator(
    root: Path,
    slug: str,
    stage: str,
    *,
    state_root: Path,
    workers: int = 1,
    timeout: float = 120,
    strict: bool = False,
    pass_threshold: float = 0.90,
) -> dict[str, Any]:
    from agent.template_check import check_template
    from sdk import corner_case

    stem = registered_stem(slug)
    module = importlib.import_module(f"agent.templates.{slug}")
    regression_path = state_root / slug / "regressions.json"
    regressions = json.loads(regression_path.read_text()) if regression_path.exists() else {}
    had_corners = hasattr(module, "TEMPLATE_CORNERS")
    original = getattr(module, "TEMPLATE_CORNERS", ())
    retained = tuple(
        corner_case(f"rfwa_regression_{key}", config, reason="retained failed configuration")
        for key, config in sorted(regressions.items())
    )
    module.TEMPLATE_CORNERS = (*tuple(original or ()), *retained)
    try:
        report = check_template(
            repo_root=root,
            slug=slug,
            stem=stem,
            stage=stage,
            cache_dir=state_root / "cache",
            pass_threshold=1.0 if strict else pass_threshold,
            max_workers=workers,
            compile_timeout_s=timeout,
        )
    finally:
        if not had_corners:
            delattr(module, "TEMPLATE_CORNERS")
        else:
            module.TEMPLATE_CORNERS = original
    failed_random = report.get("random_sweep", {}).get("failed_outcomes", [])
    cases = [*report.get("corner_stage", {}).get("cases", []), *failed_random]
    for case in cases:
        if case.get("status", case.get("verdict")) != "pass":
            config = case.get("config") or case.get("overrides")
            if config:
                key = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
                regressions[key] = config
    write_json(regression_path, regressions)
    report["rfwa_policy"] = {
        "mode": "strict" if strict else "practical",
        "random_pass_threshold": 1.0 if strict else pass_threshold,
        "retained_corner_cases": len(regressions),
    }
    if not strict:
        report["engine_verdict"] = report.get("verdict")
        sweep = report.get("random_sweep", {})
        passed = int(sweep.get("passed", 0))
        total = passed + int(sweep.get("failed", 0))
        report["verdict"] = (
            "pass"
            if report.get("preflight", {}).get("status") == "pass"
            and total > 0
            and passed / total >= pass_threshold
            else "fail"
        )
        report["warnings"] = []
        if sweep.get("failed", 0):
            report["warnings"].append(
                f"{sweep['failed']} sampled configurations failed; skip those assets during export"
            )
        if report.get("corner_stage", {}).get("status") not in {"pass", "not_run", None}:
            report["warnings"].append(
                "some corner checks are incomplete or failed; diagnostics retained for repair"
            )
        report["completion_status"] = (
            "ready_for_sampling" if report["verdict"] == "pass" else "needs_repair"
        )
    write_json(state_root / slug / f"{stage}.json", report)
    return report


def release_generator(
    root: Path,
    slug: str,
    *,
    state_root: Path,
    workers: int = 1,
    timeout: float = 120,
    strict: bool = False,
    pass_threshold: float = 0.90,
) -> dict[str, Any]:
    from agent.source_maps import parse_source_map
    from agent.template_check import mechanical_hash
    from agent.template_design import load_template_design

    stem = registered_stem(slug)
    reports = []
    stages = ("random-16", "random-36", "corner") if strict else ("random-16", "random-36")
    for stage in stages:
        report = check_generator(
            root,
            slug,
            stage,
            state_root=state_root,
            workers=workers,
            timeout=timeout,
            strict=strict,
            pass_threshold=pass_threshold,
        )
        reports.append(report)
        if report.get("verdict") != "pass":
            break
    strict_findings = release_findings(reports[-1])
    warnings = [] if strict else list(reports[-1].get("warnings", []))
    findings = (
        strict_findings
        if strict
        else (
            []
            if reports[-1].get("verdict") == "pass" and reports[-1].get("stage") == "random-36"
            else ["sample pass rate is below the configured threshold or preflight failed"]
        )
    )
    blueprint = root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    provenance: dict[str, Any] = {}
    try:
        design = load_template_design(blueprint)
        source = Path(design.source_map_path)
        if not source.is_absolute():
            source = root / source
        resolution = parse_source_map(source, root / "data" / "records")
        if resolution.verdict != "pass":
            (findings if strict else warnings).append(
                "source provenance must pass: " + "; ".join(resolution.problems)
            )
        provenance = {
            "blueprint_sha256": hashlib.sha256(blueprint.read_bytes()).hexdigest(),
            "source_map_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }
    except (OSError, ValueError) as exc:
        (findings if strict else warnings).append(f"source provenance unavailable: {exc}")
    result = {
        "schema": "rfwa-generator-release/v1",
        "generator": slug,
        "status": ("released" if strict else "ready_for_sampling") if not findings else "blocked",
        "policy": "strict" if strict else "practical",
        "warnings": warnings,
        "findings": findings,
        "mechanical_hash": mechanical_hash(root, slug, stem),
        **provenance,
        "stages": [{"stage": r["stage"], "verdict": r["verdict"]} for r in reports],
        "scope": "generator configuration and sampled motion checks; no dynamics certification",
    }
    write_json(state_root / slug / "release.json", result)
    return result
