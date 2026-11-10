# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from agent.template_pipeline import (
    TemplatePipelineBusyError,
    TemplatePipelineError,
)
from viewer.api.dependencies import (
    TemplatePipelineSchedulerDep,
    TemplatePipelineServiceDep,
)
from viewer.api.schemas import (
    TemplatePipelineCheckRequest,
    TemplatePipelineJobResponse,
    TemplatePipelineSourceMapInitRequest,
)

router = APIRouter(prefix="/api/template-pipeline", tags=["template-pipeline"])


def _pipeline_http_error(exc: TemplatePipelineError) -> HTTPException:
    return HTTPException(
        status_code=(
            status.HTTP_409_CONFLICT
            if isinstance(exc, TemplatePipelineBusyError)
            else status.HTTP_400_BAD_REQUEST
        ),
        detail=str(exc),
    )


@router.get("/jobs/{job_id}", response_model=TemplatePipelineJobResponse)
async def template_pipeline_job(
    job_id: str,
    scheduler: TemplatePipelineSchedulerDep,
    include_report: bool = Query(default=False),
) -> TemplatePipelineJobResponse:
    job = scheduler.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return TemplatePipelineJobResponse.model_validate(job.to_dict(include_report=include_report))


@router.post("/source-maps", status_code=status.HTTP_201_CREATED)
async def template_pipeline_source_map_init(
    payload: TemplatePipelineSourceMapInitRequest,
    service: TemplatePipelineServiceDep,
) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(
            service.source_map_init,
            slug=payload.slug,
            picture_category=payload.picture_category,
            picture_subcategory=payload.picture_subcategory,
        )
    except TemplatePipelineError as exc:
        raise _pipeline_http_error(exc) from exc


@router.get("/{slug}")
async def template_pipeline_status(
    slug: str,
    service: TemplatePipelineServiceDep,
) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(service.inspect, slug=slug)
    except TemplatePipelineError as exc:
        raise _pipeline_http_error(exc) from exc


@router.post("/{slug}/source-map/check")
async def template_pipeline_source_map_check(
    slug: str,
    service: TemplatePipelineServiceDep,
) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(service.source_map_check, slug=slug)
    except TemplatePipelineError as exc:
        raise _pipeline_http_error(exc) from exc


@router.post("/{slug}/design", status_code=status.HTTP_201_CREATED)
async def template_pipeline_design_init(
    slug: str,
    service: TemplatePipelineServiceDep,
) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(service.design_init, slug=slug)
    except TemplatePipelineError as exc:
        raise _pipeline_http_error(exc) from exc


@router.post(
    "/{slug}/checks",
    response_model=TemplatePipelineJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def template_pipeline_check_submit(
    slug: str,
    payload: TemplatePipelineCheckRequest,
    scheduler: TemplatePipelineSchedulerDep,
) -> TemplatePipelineJobResponse:
    try:
        job = scheduler.submit_check(
            slug=slug,
            stage=payload.stage,
            idempotency_key=payload.idempotency_key,
            pass_threshold=payload.pass_threshold,
            max_workers=payload.max_workers,
            compile_timeout_s=payload.compile_timeout_s,
            expected_quality_contract_sha256=(payload.expected_quality_contract_sha256),
        )
    except TemplatePipelineError as exc:
        raise _pipeline_http_error(exc) from exc
    return TemplatePipelineJobResponse.model_validate(job.to_dict())
