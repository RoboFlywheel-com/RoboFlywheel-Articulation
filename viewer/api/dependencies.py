# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from agent.template_pipeline import TemplatePipelineScheduler, TemplatePipelineService
from viewer.api.file_resolver import ViewerFileResolver
from viewer.api.store import ViewerStore


def get_viewer_store(request: Request) -> ViewerStore:
    return cast(ViewerStore, request.app.state.viewer_store)


def get_file_resolver(request: Request) -> ViewerFileResolver:
    return cast(ViewerFileResolver, request.app.state.file_resolver)


def get_template_pipeline_service(request: Request) -> TemplatePipelineService:
    return cast(TemplatePipelineService, request.app.state.template_pipeline_service)


def get_template_pipeline_scheduler(request: Request) -> TemplatePipelineScheduler:
    return cast(TemplatePipelineScheduler, request.app.state.template_pipeline_scheduler)


ViewerStoreDep = Annotated[ViewerStore, Depends(get_viewer_store)]
FileResolverDep = Annotated[ViewerFileResolver, Depends(get_file_resolver)]
TemplatePipelineServiceDep = Annotated[
    TemplatePipelineService,
    Depends(get_template_pipeline_service),
]
TemplatePipelineSchedulerDep = Annotated[
    TemplatePipelineScheduler,
    Depends(get_template_pipeline_scheduler),
]
