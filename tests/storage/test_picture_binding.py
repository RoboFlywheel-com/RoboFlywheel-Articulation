# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from storage.collections import CollectionStore
from storage.models import (
    DisplayMetadata,
    Record,
    RecordArtifacts,
    SourceRef,
)
from storage.picture_binding import (
    PictureBinding,
    binding_from_picture_path,
    inherit_picture_binding,
    picture_path_to_subcat,
    read_binding,
    resolve_binding,
    write_binding,
)
from storage.records import RecordStore
from storage.repo import StorageRepo, atomic_write_text
from storage.subcat_index import (
    UNASSIGNED_SHARD,
    build_subcat_index,
    load_subcat_index,
    shard_name,
    subcat_index_signature,
)


def _make_record(record_id: str, *, parent: str | None = None, origin: str | None = None) -> Record:
    lineage = {
        "origin_record_id": origin or record_id,
        "parent_record_id": parent,
        "parent_revision_id": None,
        "edit_mode": "copy" if parent else "root",
    }
    return Record(
        schema_version=3,
        record_id=record_id,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        rating=None,
        kind="external_model",
        prompt_kind="single_prompt",
        category_slug=None,
        source=SourceRef(run_id=None),
        sdk_package="sdk",
        provider="openai",
        model_id="gpt-5.5",
        display=DisplayMetadata(title=record_id, prompt_preview=""),
        artifacts=RecordArtifacts(
            prompt_txt="prompt.txt",
            prompt_series_json=None,
            model_py="model.py",
            provenance_json="provenance.json",
            cost_json=None,
        ),
        collections=["workbench"],
        active_revision_id="rev_000001",
        lineage=lineage,
    )


def _add_workbench_record(repo: StorageRepo, record: Record) -> None:
    RecordStore(repo).write_record(record)
    CollectionStore(repo).append_workbench_entry(
        record_id=record.record_id,
        added_at=record.created_at,
        label=None,
        tags=[],
    )


def test_picture_path_to_subcat_parses_embedded_path() -> None:
    assert picture_path_to_subcat("picture/Chair/Folding chair/001.png") == (
        "Chair",
        "Folding chair",
    )
    # Embedded in a larger prompt string.
    assert picture_path_to_subcat("Build a chair. reference_image: picture/Bag/Tote/x.jpg now") == (
        "Bag",
        "Tote",
    )
    assert picture_path_to_subcat("no picture here") is None
    assert picture_path_to_subcat("picture/OnlyOneLevel.png") is None


def test_binding_round_trip(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    RecordStore(repo).write_record(_make_record("rec_a"))
    binding = binding_from_picture_path("picture/Chair/Folding chair/001.png")
    assert binding is not None
    write_binding(repo, "rec_a", binding)
    loaded = read_binding(repo, "rec_a")
    assert loaded == PictureBinding(
        category="Chair",
        subcategory="Folding chair",
        path="picture/Chair/Folding chair/001.png",
        source="explicit",
    )


def test_resolve_falls_back_along_lineage(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    RecordStore(repo).write_record(_make_record("rec_parent"))
    write_binding(repo, "rec_parent", PictureBinding("Bag", "Tote", source="explicit"))
    # Child has no own sidecar; resolves via parent lineage.
    child = _make_record("rec_child", parent="rec_parent", origin="rec_parent")
    RecordStore(repo).write_record(child)
    resolved = resolve_binding(repo, "rec_child", record=child.to_dict())
    assert resolved is not None
    assert (resolved.category, resolved.subcategory) == ("Bag", "Tote")


def test_inherit_copies_parent_binding_and_is_idempotent(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    RecordStore(repo).write_record(_make_record("rec_parent"))
    write_binding(repo, "rec_parent", PictureBinding("Window", "Sliding window", source="explicit"))
    RecordStore(repo).write_record(_make_record("rec_child", parent="rec_parent"))

    inherited = inherit_picture_binding(
        repo, child_record_id="rec_child", parent_record_id="rec_parent"
    )
    assert inherited is not None
    own = read_binding(repo, "rec_child")
    assert own is not None
    assert (own.category, own.subcategory, own.source) == ("Window", "Sliding window", "inherited")
    # Self-contained: survives parent deletion.
    RecordStore(repo).delete_record("rec_parent")
    assert read_binding(repo, "rec_child") is not None
    # Idempotent: re-running does not overwrite.
    assert (
        inherit_picture_binding(repo, child_record_id="rec_child", parent_record_id="rec_parent")
        is None
    )


def test_inherit_noop_when_parent_unbound(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    RecordStore(repo).write_record(_make_record("rec_parent"))
    RecordStore(repo).write_record(_make_record("rec_child", parent="rec_parent"))
    assert (
        inherit_picture_binding(repo, child_record_id="rec_child", parent_record_id="rec_parent")
        is None
    )
    assert read_binding(repo, "rec_child") is None


def test_build_subcat_index_groups_workbench_records(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    assert subcat_index_signature(repo) is None

    # Original (explicitly bound) + variant (inherits via lineage) + an unbound record.
    parent = _make_record("rec_parent")
    _add_workbench_record(repo, parent)
    write_binding(repo, "rec_parent", PictureBinding("Vehicle", "Sports car", source="explicit"))
    variant = _make_record("rec_variant", parent="rec_parent", origin="rec_parent")
    _add_workbench_record(repo, variant)
    _add_workbench_record(repo, _make_record("rec_orphan"))

    counts = build_subcat_index(repo)
    shard = shard_name("Vehicle", "Sports car")
    assert counts[shard] == 2  # parent + variant
    assert counts[UNASSIGNED_SHARD] == 1  # orphan
    assert subcat_index_signature(repo) is not None

    rows = load_subcat_index(repo)
    by_id = {r["record_id"]: r for r in rows}
    assert by_id["rec_variant"]["picture_subcategory"] == "Sports car"
    assert by_id["rec_orphan"]["picture_subcategory"] is None


def test_atomic_write_text_replaces_in_place(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "f.txt"
    atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
    atomic_write_text(target, "world")
    assert target.read_text(encoding="utf-8") == "world"
    # No leftover temp files in the directory.
    assert [p.name for p in target.parent.iterdir()] == ["f.txt"]
