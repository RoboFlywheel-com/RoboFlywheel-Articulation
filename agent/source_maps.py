# SPDX-License-Identifier: Apache-2.0

"""Strict SourceMap authoring boundary for template construction.

A SourceMap has two jobs:

1. account for every active workbench source in one picture subcategory; and
2. map the useful source-backed components to template slot candidates.

It deliberately does not contain parameter ranges, multiplicity domains,
interfaces, assembly bindings, or implementation code. Those decisions belong
to :mod:`agent.template_design`. SourceMaps never participate in seed runtime.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_MAP_SCHEMA_VERSION = 1

REVIEW_STATUSES = frozenset({"pending", "reviewed", "unavailable"})
REVIEW_DECISIONS = frozenset(
    {
        "pending",
        "used",
        "reference_only",
        "rejected_duplicate",
        "rejected_category_drift",
        "rejected_no_structural_value",
    }
)
CANDIDATE_DISTINCTIONS = frozenset({"structure", "motion", "structure+motion"})

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_RECORD_ID = re.compile(r"rec_[A-Za-z0-9_.-]+")
_REVISION_ID = re.compile(r"rev_\d+")
_RECORD_REVISION = re.compile(r"(rec_[A-Za-z0-9_.-]+)/(rev_\d+)")
_SOURCE_SPAN = re.compile(r"(?:model\.py:)?L(\d+)\s*-\s*L(\d+)", re.IGNORECASE)

_REVIEW_HEADERS = (
    "record/revision",
    "review status",
    "decision",
    "note",
)
_CANDIDATE_HEADERS = (
    "slot",
    "candidate",
    "component type",
    "record/revision",
    "exact model.py:lx-ly",
    "distinction",
    "evidence",
)


@dataclass(frozen=True, slots=True)
class SourceSpan:
    start_line: int
    end_line: int

    def __post_init__(self) -> None:
        if self.start_line < 1 or self.end_line < self.start_line:
            raise ValueError(f"invalid source span L{self.start_line}-L{self.end_line}")

    @property
    def code_ref(self) -> str:
        return f"model.py:L{self.start_line}-L{self.end_line}"

    def to_dict(self) -> dict[str, int | str]:
        return {
            "start_line": self.start_line,
            "end_line": self.end_line,
            "code_ref": self.code_ref,
        }


@dataclass(frozen=True, slots=True)
class SourcePoolRecord:
    record_id: str
    revision: str
    model_path: Path
    input_paths: tuple[Path, ...] = ()

    @property
    def source_ref(self) -> str:
        return f"{self.record_id}/{self.revision}"

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "revision": self.revision,
            "source_ref": self.source_ref,
            "model_path": str(self.model_path),
            "input_paths": [str(path) for path in self.input_paths],
        }


@dataclass(frozen=True, slots=True)
class SourcePoolResolution:
    records: tuple[SourcePoolRecord, ...]
    problems: tuple[str, ...] = ()

    @property
    def verdict(self) -> str:
        return "pass" if not self.problems else "fail"

    def to_dict(self) -> dict[str, object]:
        return {
            "records": [record.to_dict() for record in self.records],
            "record_count": len(self.records),
            "problems": list(self.problems),
            "verdict": self.verdict,
        }


@dataclass(frozen=True, slots=True)
class SourceReview:
    record_id: str | None
    revision: str | None
    review_status: str
    decision: str
    note: str
    row_index: int = 0

    @property
    def source_ref(self) -> str | None:
        if self.record_id and self.revision:
            return f"{self.record_id}/{self.revision}"
        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "revision": self.revision,
            "source_ref": self.source_ref,
            "review_status": self.review_status,
            "decision": self.decision,
            "note": self.note,
            "row_index": self.row_index,
        }


@dataclass(frozen=True, slots=True)
class SourceMapCandidate:
    slot: str
    candidate: str
    component_type: str
    record_id: str | None
    revision: str | None
    spans: tuple[SourceSpan, ...]
    distinction: str
    evidence: str
    row_index: int = 0

    @property
    def source_type(self) -> str:
        """Compatibility name used by TemplateDesign's mechanical scaffold."""

        return self.component_type

    def to_dict(self) -> dict[str, object]:
        return {
            "slot": self.slot,
            "candidate": self.candidate,
            "component_type": self.component_type,
            "record_id": self.record_id,
            "revision": self.revision,
            "spans": [span.to_dict() for span in self.spans],
            "distinction": self.distinction,
            "evidence": self.evidence,
            "row_index": self.row_index,
        }


@dataclass(frozen=True, slots=True)
class SourceMapResolution:
    path: Path
    sha256: str
    schema_version: int | None
    export_category: str | None
    picture_category: str | None
    picture_subcategory: str | None
    category_scope: str | None
    record_ids: tuple[str, ...]
    source_pool: tuple[SourcePoolRecord, ...]
    reviews: tuple[SourceReview, ...]
    candidates: tuple[SourceMapCandidate, ...]
    problems: tuple[str, ...] = ()

    @property
    def accepted_candidates(self) -> tuple[SourceMapCandidate, ...]:
        """Every row in the strict candidate table is accepted."""

        return self.candidates

    @property
    def verdict(self) -> str:
        return "pass" if not self.problems else "fail"

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "sha256": self.sha256,
            "schema_version": self.schema_version,
            "export_category": self.export_category,
            "picture_category": self.picture_category,
            "picture_subcategory": self.picture_subcategory,
            "category_scope": self.category_scope,
            "record_ids": list(self.record_ids),
            "record_count": len(self.record_ids),
            "source_pool": [record.to_dict() for record in self.source_pool],
            "source_pool_count": len(self.source_pool),
            "reviews": [review.to_dict() for review in self.reviews],
            "reviewed_count": sum(
                review.review_status == "reviewed" for review in self.reviews
            ),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "candidate_count": len(self.candidates),
            "problems": list(self.problems),
            "verdict": self.verdict,
        }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def discover_source_pool(
    records_root: Path,
    *,
    picture_category: str,
    picture_subcategory: str,
) -> SourcePoolResolution:
    """Discover the active workbench records for one exact picture subcategory."""

    records_root = records_root.resolve()
    if not records_root.is_dir():
        return SourcePoolResolution((), (f"records_root_unavailable:{records_root}",))

    records: list[SourcePoolRecord] = []
    problems: list[str] = []
    # Source maps record provenance, so cached membership must never hide a newly
    # imported, forked or unarchived source. Read current sidecars even when a
    # category shard exists: those shards are derived, independently updated data.
    record_dirs = sorted(path for path in records_root.iterdir() if path.is_dir())
    for record_dir in record_dirs:
        picture = _read_json(record_dir / "picture.json")
        if not picture:
            continue
        if str(picture.get("category") or "") != picture_category:
            continue
        if str(picture.get("subcategory") or "") != picture_subcategory:
            continue

        record_id = record_dir.name
        metadata = _read_json(record_dir / "record.json")
        if metadata is None:
            problems.append(f"source_record_metadata_invalid:{record_id}")
            continue
        collections = metadata.get("collections")
        if not (isinstance(collections, list) and "workbench" in collections):
            continue
        workbench = _read_json(record_dir / "collections" / "workbench.json")
        if workbench and bool(workbench.get("archived", False)):
            continue

        revision = str(metadata.get("active_revision_id") or "")
        if not _REVISION_ID.fullmatch(revision):
            problems.append(f"source_active_revision_invalid:{record_id}")
            continue
        revision_dir = record_dir / "revisions" / revision
        model_path = revision_dir / "model.py"
        if not model_path.is_file():
            problems.append(f"source_model_missing:{record_id}/{revision}")
            continue
        inputs_dir = revision_dir / "inputs"
        inputs = (
            tuple(sorted(path for path in inputs_dir.iterdir() if path.is_file()))
            if inputs_dir.is_dir()
            else ()
        )
        records.append(
            SourcePoolRecord(
                record_id=record_id,
                revision=revision,
                model_path=model_path,
                input_paths=inputs,
            )
        )

    if not records:
        problems.append(
            f"source_pool_empty:{picture_category}/{picture_subcategory}"
        )
    return SourcePoolResolution(
        records=tuple(records),
        problems=tuple(dict.fromkeys(problems)),
    )


def _strip_markdown(value: str) -> str:
    return re.sub(r"[`*]", "", value).strip()


def _normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", _strip_markdown(value).casefold())


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _markdown_tables(text: str) -> list[tuple[tuple[str, ...], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[tuple[str, ...], list[dict[str, str]]]] = []
    index = 0
    while index + 1 < len(lines):
        header_line = lines[index].strip()
        separator_line = lines[index + 1].strip()
        if not (header_line.startswith("|") and separator_line.startswith("|")):
            index += 1
            continue
        separators = _table_cells(separator_line)
        if not separators or not all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in separators
        ):
            index += 1
            continue
        headers = tuple(_normalize_header(cell) for cell in _table_cells(header_line))
        if len(headers) != len(separators):
            index += 1
            continue
        rows: list[dict[str, str]] = []
        row_index = index + 3
        index += 2
        while index < len(lines) and lines[index].strip().startswith("|"):
            values = _table_cells(lines[index])
            if len(values) == len(headers):
                row = dict(zip(headers, values, strict=True))
                row["__row_index__"] = str(row_index)
                rows.append(row)
            row_index += 1
            index += 1
        tables.append((headers, rows))
    return tables


def _metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", text)
    if not match:
        return None
    value = _strip_markdown(match.group(1)).strip("'\"")
    return value or None


def _manifest_ids(text: str) -> list[str]:
    ids: list[str] = []
    reading = False
    for line in text.splitlines():
        if re.fullmatch(r"\s*sync_records\s*:\s*", line):
            reading = True
            continue
        if not reading:
            continue
        match = re.fullmatch(r"\s*-\s*(rec_[A-Za-z0-9_.-]+)\s*", line)
        if match:
            ids.append(match.group(1))
            continue
        if not line.strip():
            if ids:
                break
            continue
        break
    return ids


def _parse_record_revision(value: str) -> tuple[str | None, str | None]:
    match = _RECORD_REVISION.fullmatch(_strip_markdown(value))
    if not match:
        return None, None
    return match.group(1), match.group(2)


def _table_rows(
    tables: list[tuple[tuple[str, ...], list[dict[str, str]]]],
    expected_headers: tuple[str, ...],
) -> tuple[list[dict[str, str]], bool]:
    matches = [rows for headers, rows in tables if headers == expected_headers]
    if len(matches) != 1:
        return [], False
    return matches[0], True


def render_source_map_scaffold(
    *,
    slug: str,
    picture_category: str,
    picture_subcategory: str,
    source_pool: SourcePoolResolution,
) -> str:
    """Render one strict SourceMap with every discovered record pending review."""

    if source_pool.problems:
        raise ValueError("; ".join(source_pool.problems))
    if not source_pool.records:
        raise ValueError("source pool is empty")

    lines = [
        f"# {slug} — SourceMap",
        "",
        f"source_map_schema: {SOURCE_MAP_SCHEMA_VERSION}",
        f"export_category: {slug}",
        f"picture_category: {picture_category}",
        f"picture_subcategory: {picture_subcategory}",
        "category_scope: TODO define the exact small-category host boundary.",
        "",
        "sync_records:",
    ]
    lines.extend(f"  - {record.record_id}" for record in source_pool.records)
    lines.extend(
        [
            "",
            "## Source review",
            "",
            "| Record/Revision | Review status | Decision | Note |",
            "|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {record.source_ref} | pending | pending | TODO inspect source image and model.py |"
        for record in source_pool.records
    )
    lines.extend(
        [
            "",
            "## Candidate map",
            "",
            "| Slot | Candidate | Component type | Record/Revision | "
            "Exact model.py:Lx-Ly | Distinction | Evidence |",
            "|---|---|---|---|---|---|---|",
            "",
        ]
    )
    return "\n".join(lines)


def parse_source_map(source_map: Path, records_root: Path) -> SourceMapResolution:
    """Parse and strictly audit one SourceMap against its complete source pool."""

    source_map = source_map.resolve()
    if not source_map.is_file():
        return SourceMapResolution(
            path=source_map,
            sha256="",
            schema_version=None,
            export_category=None,
            picture_category=None,
            picture_subcategory=None,
            category_scope=None,
            record_ids=(),
            source_pool=(),
            reviews=(),
            candidates=(),
            problems=("source_map_missing",),
        )

    text = source_map.read_text(encoding="utf-8", errors="replace")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    problems: list[str] = []

    raw_schema = _metadata_value(text, "source_map_schema")
    try:
        schema_version = int(raw_schema) if raw_schema is not None else None
    except ValueError:
        schema_version = None
    if schema_version != SOURCE_MAP_SCHEMA_VERSION:
        problems.append("source_map_schema_invalid")

    export_category = _metadata_value(text, "export_category")
    picture_category = _metadata_value(text, "picture_category")
    picture_subcategory = _metadata_value(text, "picture_subcategory")
    category_scope = _metadata_value(text, "category_scope")
    if not export_category:
        problems.append("export_category_missing")
    if not picture_category:
        problems.append("picture_category_missing")
    if not picture_subcategory:
        problems.append("picture_subcategory_missing")
    if not category_scope or category_scope.casefold().startswith("todo"):
        problems.append("category_scope_incomplete")

    manifest_ids = _manifest_ids(text)
    if not manifest_ids:
        problems.append("sync_records_empty")
    if len(manifest_ids) != len(set(manifest_ids)):
        problems.append("sync_records_duplicate")
    record_ids = tuple(dict.fromkeys(manifest_ids))

    source_pool_resolution = (
        discover_source_pool(
            records_root,
            picture_category=picture_category,
            picture_subcategory=picture_subcategory,
        )
        if picture_category and picture_subcategory
        else SourcePoolResolution((), ())
    )
    problems.extend(source_pool_resolution.problems)
    source_pool = source_pool_resolution.records
    pool_by_id = {record.record_id: record for record in source_pool}
    manifest_set = set(record_ids)
    pool_set = set(pool_by_id)
    missing_from_map = sorted(pool_set - manifest_set)
    outside_pool = sorted(manifest_set - pool_set)
    if missing_from_map:
        problems.append(
            "source_pool_records_missing_from_sync:" + ",".join(missing_from_map)
        )
    if outside_pool:
        problems.append("sync_records_outside_source_pool:" + ",".join(outside_pool))

    tables = _markdown_tables(text)
    review_rows, review_table_found = _table_rows(tables, _REVIEW_HEADERS)
    if not review_table_found:
        problems.append("source_review_table_invalid")
    reviews: list[SourceReview] = []
    for row in review_rows:
        record_id, revision = _parse_record_revision(row["record/revision"])
        review = SourceReview(
            record_id=record_id,
            revision=revision,
            review_status=_strip_markdown(row["review status"]).casefold(),
            decision=_strip_markdown(row["decision"]).casefold(),
            note=_strip_markdown(row["note"]),
            row_index=int(row["__row_index__"]),
        )
        reviews.append(review)

    review_ids = [review.record_id for review in reviews if review.record_id]
    if any(review.record_id is None or review.revision is None for review in reviews):
        problems.append("source_review_record_revision_invalid")
    if len(review_ids) != len(set(review_ids)):
        problems.append("source_review_record_duplicate")
    review_by_id = {
        review.record_id: review for review in reviews if review.record_id is not None
    }
    missing_reviews = sorted(manifest_set - set(review_by_id))
    extra_reviews = sorted(set(review_by_id) - manifest_set)
    if missing_reviews:
        problems.append("sync_records_missing_review:" + ",".join(missing_reviews))
    if extra_reviews:
        problems.append("source_review_outside_sync:" + ",".join(extra_reviews))

    for review in reviews:
        label = review.record_id or f"row_{review.row_index}"
        if review.review_status not in REVIEW_STATUSES:
            problems.append(f"source_review_status_invalid:{label}")
        if review.decision not in REVIEW_DECISIONS:
            problems.append(f"source_review_decision_invalid:{label}")
        if not review.note:
            problems.append(f"source_review_note_missing:{label}")
        if review.review_status != "reviewed":
            problems.append(f"source_not_reviewed:{label}")
        if review.review_status == "reviewed" and review.decision == "pending":
            problems.append(f"source_review_decision_pending:{label}")
        pool_record = pool_by_id.get(review.record_id or "")
        if pool_record and review.revision != pool_record.revision:
            problems.append(f"source_review_revision_stale:{label}")

    candidate_rows, candidate_table_found = _table_rows(tables, _CANDIDATE_HEADERS)
    if not candidate_table_found:
        problems.append("candidate_map_table_invalid")
    candidates: list[SourceMapCandidate] = []
    for row in candidate_rows:
        record_id, revision = _parse_record_revision(row["record/revision"])
        spans = tuple(
            SourceSpan(int(match.group(1)), int(match.group(2)))
            for match in _SOURCE_SPAN.finditer(_strip_markdown(row["exact model.py:lx-ly"]))
        )
        candidates.append(
            SourceMapCandidate(
                slot=_strip_markdown(row["slot"]),
                candidate=_strip_markdown(row["candidate"]),
                component_type=_strip_markdown(row["component type"]),
                record_id=record_id,
                revision=revision,
                spans=spans,
                distinction=_strip_markdown(row["distinction"]).casefold(),
                evidence=_strip_markdown(row["evidence"]),
                row_index=int(row["__row_index__"]),
            )
        )

    if not candidates:
        problems.append("source_candidates_missing")
    candidate_keys = [(candidate.slot, candidate.candidate) for candidate in candidates]
    if len(candidate_keys) != len(set(candidate_keys)):
        problems.append("source_candidate_duplicate")

    candidate_record_ids: set[str] = set()
    for candidate in candidates:
        label = candidate.candidate or f"row_{candidate.row_index}"
        if not _IDENTIFIER.fullmatch(candidate.slot):
            problems.append(f"candidate_slot_invalid:{label}")
        if not _IDENTIFIER.fullmatch(candidate.candidate):
            problems.append(f"candidate_name_invalid:{label}")
        if not candidate.component_type:
            problems.append(f"candidate_component_type_missing:{label}")
        if not candidate.record_id or not candidate.revision:
            problems.append(f"candidate_record_revision_invalid:{label}")
            continue
        candidate_record_ids.add(candidate.record_id)
        review = review_by_id.get(candidate.record_id)
        if review is None:
            problems.append(f"candidate_source_not_reviewed:{label}")
        else:
            if review.review_status != "reviewed":
                problems.append(f"candidate_source_not_reviewed:{label}")
            if review.decision != "used":
                problems.append(f"candidate_source_not_marked_used:{label}")
            if candidate.revision != review.revision:
                problems.append(f"candidate_revision_mismatch:{label}")
        pool_record = pool_by_id.get(candidate.record_id)
        if pool_record is None:
            problems.append(f"candidate_source_outside_pool:{label}")
        elif candidate.revision != pool_record.revision:
            problems.append(f"candidate_revision_stale:{label}")
        if not candidate.spans:
            problems.append(f"candidate_source_spans_missing:{label}")
        elif pool_record is not None:
            line_count = len(
                pool_record.model_path.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
            )
            if any(span.end_line > line_count for span in candidate.spans):
                problems.append(f"candidate_source_span_out_of_range:{label}")
        if candidate.distinction not in CANDIDATE_DISTINCTIONS:
            problems.append(f"candidate_distinction_invalid:{label}")
        if not candidate.evidence:
            problems.append(f"candidate_evidence_missing:{label}")

    for review in reviews:
        if review.decision == "used" and review.record_id not in candidate_record_ids:
            problems.append(f"used_source_has_no_candidate:{review.record_id}")

    return SourceMapResolution(
        path=source_map,
        sha256=digest,
        schema_version=schema_version,
        export_category=export_category,
        picture_category=picture_category,
        picture_subcategory=picture_subcategory,
        category_scope=category_scope,
        record_ids=record_ids,
        source_pool=source_pool,
        reviews=tuple(reviews),
        candidates=tuple(candidates),
        problems=tuple(dict.fromkeys(problems)),
    )


__all__ = [
    "CANDIDATE_DISTINCTIONS",
    "REVIEW_DECISIONS",
    "REVIEW_STATUSES",
    "SOURCE_MAP_SCHEMA_VERSION",
    "SourceMapCandidate",
    "SourceMapResolution",
    "SourcePoolRecord",
    "SourcePoolResolution",
    "SourceReview",
    "SourceSpan",
    "discover_source_pool",
    "parse_source_map",
    "render_source_map_scaffold",
]
