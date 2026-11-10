# SPDX-License-Identifier: Apache-2.0

"""Generator snapshots and visual-editing adapters."""

from __future__ import annotations

from .catalog import (
    AxisDescriptor,
    CatalogError,
    GeneratorAdapter,
    get_generator,
    list_generators,
)

__all__ = [
    "AxisDescriptor",
    "CatalogError",
    "GeneratorAdapter",
    "get_generator",
    "list_generators",
]
