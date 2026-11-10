# SPDX-License-Identifier: Apache-2.0

"""Shared orchestration for Agent- and API-driven template authoring.

The service owns step ordering and filesystem locations, while the existing
SourceMap, TemplateDesign, and mechanical checker modules remain authoritative
for each step.  The scheduler is intentionally local and lightweight: it only
serializes long-running checks per template and persists their reports under
``.artifacts``.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from agent.source_maps import (
    discover_source_pool,
    parse_source_map,
    render_source_map_scaffold,
)
from agent.template_check import CHECK_STAGES, CheckStage, check_template
from agent.template_design import (
    TemplateDesignError,
    load_template_design,
    scaffold_template_design,
    write_template_design,
)

_SLUG = re.compile(r"[A-Za-z0-9_.-]+")


class TemplatePipelineError(ValueError):
    """A pipeline request is invalid or cannot advance safely."""


class TemplatePipelineBusyError(TemplatePipelineError):
    """A long-running check is already active for the requested template."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class TemplatePipelinePaths:
    source_map: Path
    design: Path
    template: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "source_map": str(self.source_map),
            "design": str(self.design),
            "template": str(self.template),
        }


class TemplatePipelineService:
    """Synchronous pipeline steps shared by CLI commands and API jobs."""

    def __init__(self, *, repo_root: Path, records_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.records_root = records_root.resolve()

    @staticmethod
    def validate_slug(slug: str) -> str:
        if not _SLUG.fullmatch(slug):
            raise TemplatePipelineError(f"invalid template slug: {slug!r}")
        return slug

    def paths(self, slug: str) -> TemplatePipelinePaths:
        slug = self.validate_slug(slug)
        authoring = self.repo_root / "articraft_template_authoring"
        return TemplatePipelinePaths(
            source_map=authoring / "source_maps" / f"{slug}.md",
            design=authoring / "designs" / f"{slug}.json",
            template=self.repo_root / "agent" / "templates" / f"{slug}.py",
        )

    def source_map_init(
        self,
        *,
        slug: str,
        picture_category: str,
        picture_subcategory: str,
        out_path: Path | None = None,
    ) -> dict[str, Any]:
        paths = self.paths(slug)
        target = (out_path or paths.source_map).resolve()
        if target.exists():
            raise TemplatePipelineError(f"SourceMap already exists: {target}")
        source_pool = discover_source_pool(
            self.records_root,
            picture_category=picture_category,
            picture_subcategory=picture_subcategory,
        )
        if source_pool.problems:
            raise TemplatePipelineError("; ".join(source_pool.problems))
        text = render_source_map_scaffold(
            slug=slug,
            picture_category=picture_category,
            picture_subcategory=picture_subcategory,
            source_pool=source_pool,
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(text)
        except FileExistsError as exc:
            raise TemplatePipelineError(f"SourceMap already exists: {target}") from exc
        return {
            "status": "pending_review",
            "path": str(target),
            "sha256": _sha256(target),
            "source_count": len(source_pool.records),
        }

    def source_map_check(
        self,
        *,
        slug: str,
        source_map: Path | None = None,
    ) -> dict[str, Any]:
        target = (source_map or self.paths(slug).source_map).resolve()
        return parse_source_map(target, self.records_root).to_dict()

    def design_init(
        self,
        *,
        slug: str,
        source_map: Path | None = None,
        out_path: Path | None = None,
    ) -> dict[str, Any]:
        paths = self.paths(slug)
        source = (source_map or paths.source_map).resolve()
        target = (out_path or paths.design).resolve()
        if target.exists():
            raise TemplatePipelineError(f"TemplateDesign already exists: {target}")
        try:
            design, resolution = scaffold_template_design(
                slug=slug,
                source_map=source,
                records_root=self.records_root,
            )
            write_template_design(design, target)
        except (OSError, TemplateDesignError, ValueError) as exc:
            raise TemplatePipelineError(str(exc)) from exc
        return {
            "status": "written",
            "path": str(target),
            "sha256": _sha256(target),
            "source_count": len(resolution.source_pool),
            "reviewed_count": len(resolution.reviews),
            "slot_count": len(design.slots),
            "candidate_count": sum(len(slot.candidates) for slot in design.slots),
        }

    def inspect(self, *, slug: str) -> dict[str, Any]:
        paths = self.paths(slug)
        source_status: dict[str, Any] = {
            "exists": paths.source_map.is_file(),
            "path": str(paths.source_map),
        }
        if paths.source_map.is_file():
            resolution = parse_source_map(paths.source_map, self.records_root)
            source_status.update(
                {
                    "sha256": resolution.sha256,
                    "verdict": resolution.verdict,
                    "source_count": len(resolution.source_pool),
                    "reviewed_count": len(resolution.reviews),
                    "candidate_count": len(resolution.candidates),
                    "problems": list(resolution.problems),
                }
            )

        design_status: dict[str, Any] = {
            "exists": paths.design.is_file(),
            "path": str(paths.design),
        }
        if paths.design.is_file():
            try:
                design = load_template_design(paths.design)
                current_source_sha = (
                    _sha256(paths.source_map) if paths.source_map.is_file() else None
                )
                design_status.update(
                    {
                        "verdict": "pass",
                        "sha256": _sha256(paths.design),
                        "slot_count": len(design.slots),
                        "candidate_count": sum(len(slot.candidates) for slot in design.slots),
                        "source_map_current": (
                            current_source_sha == design.source_map_sha256
                            if current_source_sha
                            else False
                        ),
                    }
                )
            except (OSError, TemplateDesignError, ValueError) as exc:
                design_status.update({"verdict": "fail", "problem": str(exc)})

        template_status = {
            "exists": paths.template.is_file(),
            "path": str(paths.template),
            "sha256": _sha256(paths.template) if paths.template.is_file() else None,
        }
        if not source_status["exists"]:
            next_step = "source-map-init"
        elif source_status.get("verdict") != "pass":
            next_step = "source-review"
        elif not design_status["exists"]:
            next_step = "design-init"
        elif design_status.get("verdict") != "pass" or not design_status.get("source_map_current"):
            next_step = "repair-design"
        elif not template_status["exists"]:
            next_step = "write-template"
        else:
            next_step = "random-16"
        return {
            "slug": slug,
            "paths": paths.to_dict(),
            "source_map": source_status,
            "design": design_status,
            "template": template_status,
            "next_step": next_step,
        }

    def run_check(
        self,
        *,
        slug: str,
        stem: str,
        stage: CheckStage,
        pass_threshold: float = 0.9,
        max_workers: int | None = None,
        compile_timeout_s: float = 90.0,
        cache_dir: Path | None = None,
        progress: Callable[[Any], None] | None = None,
        expected_quality_contract_sha256: str | None = None,
    ) -> dict[str, Any]:
        self.validate_slug(slug)
        if stage not in CHECK_STAGES:
            raise TemplatePipelineError(f"unsupported check stage: {stage!r}")
        return check_template(
            repo_root=self.repo_root,
            slug=slug,
            stem=stem,
            stage=stage,
            cache_dir=cache_dir,
            pass_threshold=pass_threshold,
            max_workers=max_workers,
            compile_timeout_s=compile_timeout_s,
            progress=progress,
            expected_quality_contract_sha256=expected_quality_contract_sha256,
        )


@dataclass(slots=True)
class TemplatePipelineJob:
    job_id: str
    idempotency_key: str
    slug: str
    stage: CheckStage
    request_signature: str = field(repr=False)
    status: str = "queued"
    created_at: str = field(default_factory=_now)
    started_at: str | None = None
    finished_at: str | None = None
    verdict: str | None = None
    report_path: str | None = None
    error: str | None = None
    report: dict[str, Any] | None = None

    def to_dict(self, *, include_report: bool = False) -> dict[str, Any]:
        payload = {
            "job_id": self.job_id,
            "idempotency_key": self.idempotency_key,
            "slug": self.slug,
            "stage": self.stage,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "verdict": self.verdict,
            "report_path": self.report_path,
            "error": self.error,
        }
        if include_report:
            payload["report"] = self.report
        return payload


class TemplatePipelineScheduler:
    """In-process scheduler with idempotency and one active check per slug."""

    def __init__(
        self,
        *,
        service: TemplatePipelineService,
        template_stems: Mapping[str, str],
        max_workers: int = 1,
    ) -> None:
        self.service = service
        self.template_stems = dict(template_stems)
        self._executor = ThreadPoolExecutor(
            max_workers=max(1, int(max_workers)),
            thread_name_prefix="template-pipeline",
        )
        self._lock = threading.Lock()
        self._jobs: dict[str, TemplatePipelineJob] = {}
        self._idempotency: dict[str, str] = {}
        self._active_by_slug: dict[str, str] = {}

    def submit_check(
        self,
        *,
        slug: str,
        stage: CheckStage,
        idempotency_key: str,
        pass_threshold: float = 0.9,
        max_workers: int | None = None,
        compile_timeout_s: float = 90.0,
        expected_quality_contract_sha256: str | None = None,
    ) -> TemplatePipelineJob:
        if not idempotency_key.strip():
            raise TemplatePipelineError("idempotency_key is required")
        stem = self.template_stems.get(slug)
        if stem is None:
            raise TemplatePipelineError(f"unknown template slug: {slug}")
        if stage not in CHECK_STAGES:
            raise TemplatePipelineError(f"unsupported check stage: {stage!r}")
        request_signature = json.dumps(
            {
                "slug": slug,
                "stage": stage,
                "pass_threshold": pass_threshold,
                "max_workers": max_workers,
                "compile_timeout_s": compile_timeout_s,
                "expected_quality_contract_sha256": expected_quality_contract_sha256,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        with self._lock:
            existing_id = self._idempotency.get(idempotency_key)
            if existing_id is not None:
                existing = self._jobs[existing_id]
                if existing.request_signature != request_signature:
                    raise TemplatePipelineError(
                        "idempotency_key was already used for a different request"
                    )
                return existing
            active_id = self._active_by_slug.get(slug)
            if active_id is not None:
                raise TemplatePipelineBusyError(
                    f"template check already active for {slug}: {active_id}"
                )
            job = TemplatePipelineJob(
                job_id=uuid.uuid4().hex,
                idempotency_key=idempotency_key,
                slug=slug,
                stage=stage,
                request_signature=request_signature,
            )
            self._jobs[job.job_id] = job
            self._idempotency[idempotency_key] = job.job_id
            self._active_by_slug[slug] = job.job_id
            self._executor.submit(
                self._run,
                job.job_id,
                stem,
                pass_threshold,
                max_workers,
                compile_timeout_s,
                expected_quality_contract_sha256,
            )
            return job

    def get_job(self, job_id: str) -> TemplatePipelineJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def _run(
        self,
        job_id: str,
        stem: str,
        pass_threshold: float,
        max_workers: int | None,
        compile_timeout_s: float,
        expected_quality_contract_sha256: str | None,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"
            job.started_at = _now()
        try:
            report = self.service.run_check(
                slug=job.slug,
                stem=stem,
                stage=job.stage,
                pass_threshold=pass_threshold,
                max_workers=max_workers,
                compile_timeout_s=compile_timeout_s,
                expected_quality_contract_sha256=expected_quality_contract_sha256,
            )
            report_dir = self.service.repo_root / ".artifacts" / "template_pipeline" / "jobs"
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / f"{job.job_id}.json"
            temporary = report_path.with_suffix(".json.tmp")
            temporary.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            temporary.replace(report_path)
            with self._lock:
                job.report = report
                job.report_path = str(report_path)
                job.verdict = str(report.get("verdict") or "")
                job.status = "completed"
        except Exception as exc:  # keep background failures observable through the job
            with self._lock:
                job.status = "failed"
                job.error = f"{type(exc).__name__}: {exc}"
        finally:
            with self._lock:
                job.finished_at = _now()
                self._active_by_slug.pop(job.slug, None)

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=False)


__all__ = [
    "TemplatePipelineBusyError",
    "TemplatePipelineError",
    "TemplatePipelineJob",
    "TemplatePipelinePaths",
    "TemplatePipelineScheduler",
    "TemplatePipelineService",
]
