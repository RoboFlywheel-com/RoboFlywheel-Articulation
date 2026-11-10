# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from agent.template_pipeline import TemplatePipelineScheduler, TemplatePipelineService
from agent.template_registry import TEMPLATE_REGISTRY
from viewer.api.file_resolver import ViewerFileResolver
from viewer.api.frontend import install_frontend_routes
from viewer.api.routes import (
    collections_router,
    files_router,
    records_router,
    runs_router,
    status_router,
    template_pipeline_router,
)
from viewer.api.store import ViewerStore


def _resolve_repo_root(repo_root: Path | None) -> Path:
    if repo_root is not None:
        return repo_root.resolve()
    configured = os.getenv("ARTICRAFT_REPO_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path.cwd().resolve()


def _install_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:8765",
            "http://localhost:8765",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_records_root(repo_root: Path) -> Path:
    configured = os.getenv("RFWA_RECORDS_ROOT") or os.getenv("ARTICRAFT_RECORDS_ROOT")
    if configured:
        return Path(configured).resolve()
    return (repo_root / "data" / "records").resolve()


def create_app(*, repo_root: Path | None = None) -> FastAPI:
    app = FastAPI(title="Articraft Viewer API")
    resolved_repo_root = _resolve_repo_root(repo_root)
    store = ViewerStore(
        resolved_repo_root,
        ensure_search_index=not _env_flag("ARTICRAFT_VIEWER_SKIP_SEARCH_INDEX"),
    )

    app.state.repo_root = resolved_repo_root
    app.state.viewer_store = store
    app.state.file_resolver = ViewerFileResolver(store.materialization)
    template_pipeline_service = TemplatePipelineService(
        repo_root=resolved_repo_root,
        records_root=_resolve_records_root(resolved_repo_root),
    )
    template_pipeline_scheduler = TemplatePipelineScheduler(
        service=template_pipeline_service,
        template_stems=TEMPLATE_REGISTRY,
        max_workers=int(os.getenv("ARTICRAFT_TEMPLATE_PIPELINE_WORKERS", "1")),
    )
    app.state.template_pipeline_service = template_pipeline_service
    app.state.template_pipeline_scheduler = template_pipeline_scheduler
    app.router.add_event_handler("shutdown", template_pipeline_scheduler.close)

    _install_middleware(app)
    app.include_router(status_router)
    app.include_router(collections_router)
    app.include_router(records_router)
    app.include_router(runs_router)
    app.include_router(files_router)
    app.include_router(template_pipeline_router)
    install_frontend_routes(app)
    return app


app = create_app()
