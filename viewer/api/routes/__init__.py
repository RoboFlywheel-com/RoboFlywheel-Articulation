# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from viewer.api.routes.collections import router as collections_router
from viewer.api.routes.files import router as files_router
from viewer.api.routes.records import router as records_router
from viewer.api.routes.runs import router as runs_router
from viewer.api.routes.status import router as status_router
from viewer.api.routes.template_pipeline import router as template_pipeline_router

__all__ = [
    "collections_router",
    "files_router",
    "records_router",
    "runs_router",
    "status_router",
    "template_pipeline_router",
]
