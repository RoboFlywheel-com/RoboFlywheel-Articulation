# SPDX-License-Identifier: Apache-2.0

"""Registry-wide template contract smoke test.

Every slug in ``TEMPLATE_REGISTRY`` must import and expose the callables the
sweep's generated ``model.py`` binds to (``build_<stem>``, ``run_<stem>_tests``,
``config_from_seed``), and ``config_from_seed(0)`` must produce a config that
``resolve_config`` accepts. No geometry is compiled, so the whole registry
checks in seconds.

This is the cheap tripwire between SDK/API evolution and the template stock:
per-template asset tests are excluded from the default run (see conftest), and
sweeps only re-run when a template is edited, so without this test a template
calling a removed SDK symbol or drifting from its registry stem stays silently
broken until the next full census (in 2026-06 six templates rotted for three
weeks exactly this way).
"""

from __future__ import annotations

import importlib

import pytest

from agent.template_registry import TEMPLATE_REGISTRY
from sdk import TemplateDomain

_REGISTRY_ITEMS = sorted(TEMPLATE_REGISTRY.items())


@pytest.mark.parametrize(
    ("slug", "stem"), _REGISTRY_ITEMS, ids=[slug for slug, _ in _REGISTRY_ITEMS]
)
def test_template_module_honors_contract(slug: str, stem: str) -> None:
    module = importlib.import_module(f"agent.templates.{slug}")

    for attr in (f"build_{stem}", f"run_{stem}_tests", "config_from_seed"):
        fn = getattr(module, attr, None)
        assert callable(fn), f"{slug}: missing or non-callable {attr}"

    config = module.config_from_seed(0)
    assert config is not None, f"{slug}: config_from_seed(0) returned None"

    resolve = getattr(module, "resolve_config", None)
    if callable(resolve):
        assert resolve(config) is not None, f"{slug}: resolve_config rejected seed-0 config"


def _legacy_nonmodular() -> set[str]:
    from agent.template_sweep_coverage import _legacy_nonmodular_slugs

    return _legacy_nonmodular_slugs()


@pytest.mark.parametrize("slug", sorted(TEMPLATE_REGISTRY))
def test_template_uses_a_supported_structural_contract(slug: str) -> None:
    """Accept either the strict TemplateDomain contract or the legacy modular route."""
    module = importlib.import_module(f"agent.templates.{slug}")
    if isinstance(getattr(module, "TEMPLATE_DOMAIN", None), TemplateDomain):
        return
    if slug in _legacy_nonmodular():
        pytest.skip("frozen legacy non-modular stock (migration deferred)")
    assert getattr(module, "__modular__", False) is True, (
        f"{slug}: template must expose sdk.TemplateDomain or use the legacy "
        "modular compatibility route (__modular__ = True)"
    )
    assert callable(getattr(module, "slot_choices_for_seed", None)), (
        f"{slug}: modular templates must export slot_choices_for_seed"
    )
