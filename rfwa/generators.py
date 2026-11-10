# SPDX-License-Identifier: Apache-2.0

"""Adapters for the existing, independently executable generator collection."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any


def registered_stem(slug: str) -> str:
    from agent.template_registry import TEMPLATE_REGISTRY

    if slug not in TEMPLATE_REGISTRY:
        raise ValueError(f"unknown generator: {slug!r}; use `rfwa generators`")
    return TEMPLATE_REGISTRY[slug]


def configuration(slug: str, seed: int) -> dict[str, Any]:
    registered_stem(slug)
    module = importlib.import_module(f"agent.templates.{slug}")
    config = module.config_from_seed(seed)
    resolve = getattr(module, "resolve_config", None)
    if callable(resolve):
        config = resolve(config)
    if dataclasses.is_dataclass(config):
        return dataclasses.asdict(config)
    if isinstance(config, dict):
        return dict(config)
    return vars(config)


def describe(slug: str, root: Path) -> dict[str, Any]:
    from sdk import TemplateDomain

    stem = registered_stem(slug)
    module = importlib.import_module(f"agent.templates.{slug}")
    domain = getattr(module, "TEMPLATE_DOMAIN", None)
    design = root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    return {
        "generator": slug,
        "build_function": f"build_{stem}",
        "blueprint": str(design) if design.is_file() else None,
        "declared_domain": domain.audit() if isinstance(domain, TemplateDomain) else None,
        "seed_0_config": configuration(slug, 0),
        "release_status": "not_evaluated",
    }


def construction_provenance(slug: str, root: Path) -> dict[str, Any]:
    """Retain source identities without requiring source records during sampling."""
    generator = root / "agent" / "templates" / f"{slug}.py"
    result: dict[str, Any] = {
        "generator_sha256": hashlib.sha256(generator.read_bytes()).hexdigest(),
        "blueprint_sha256": None,
        "source_components": [],
    }
    blueprint = root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    if blueprint.is_file():
        payload = json.loads(blueprint.read_text())
        result["blueprint_sha256"] = hashlib.sha256(blueprint.read_bytes()).hexdigest()
        for slot in payload.get("slots", []):
            for candidate in slot.get("candidates", []):
                result["source_components"].append(
                    {
                        "role": slot.get("name"),
                        "candidate": candidate.get("name"),
                        "record_id": candidate.get("record_id"),
                        "revision": candidate.get("revision"),
                        "source_spans": candidate.get("source_spans", []),
                    }
                )
    return result
