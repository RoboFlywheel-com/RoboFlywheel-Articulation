# SPDX-License-Identifier: Apache-2.0

"""Exercise the real filesystem chain, with no provider/model calls."""

import json

from PIL import Image

from agent.source_maps import discover_source_pool
from cli.external import main
from cli.template import main as author
from storage.picture_binding import read_binding
from storage.repo import StorageRepo
from storage.revisions import active_inputs_dir, active_model_path


def reference(root):
    image = root / "picture/Demo/widget/reference.png"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (8, 8), "white").save(image)
    return image


def test_image_seed_fork_source_map_and_blueprint(tmp_path):
    image = reference(tmp_path)
    repo = StorageRepo(tmp_path)
    assert (
        main(
            [
                "--repo-root",
                str(tmp_path),
                "seed",
                "Demo/widget",
                "test widget",
                "--agent",
                "codex",
                "--record-id",
                "rec_seed",
            ]
        )
        == 0
    )
    assert read_binding(repo, "rec_seed").path == "picture/Demo/widget/reference.png"
    inputs = active_inputs_dir(repo, "rec_seed")
    assert any(p.read_bytes() == image.read_bytes() for p in inputs.iterdir() if p.is_file())
    # Fixture source stands in for the external agent's authored model; no synthesis claim.
    model = active_model_path(repo, "rec_seed")
    model.write_text("# source fixture\n" * 30)
    original = model.read_bytes()
    assert (
        main(
            [
                "--repo-root",
                str(tmp_path),
                "fork",
                "rec_seed",
                "wider body",
                "--agent",
                "codex",
                "--record-id",
                "rec_variant",
            ]
        )
        == 0
    )
    assert model.read_bytes() == original
    assert read_binding(repo, "rec_variant").source == "inherited"
    pool = discover_source_pool(
        repo.layout.records_root, picture_category="Demo", picture_subcategory="widget"
    )
    assert {r.record_id for r in pool.records} == {"rec_seed", "rec_variant"}
    source_map = tmp_path / "source.md"
    base = ["--repo-root", str(tmp_path)]
    assert (
        author(
            base
            + [
                "source-map-init",
                "demo",
                "--records-root",
                str(repo.layout.records_root),
                "--picture-category",
                "Demo",
                "--picture-subcategory",
                "widget",
                "--out",
                str(source_map),
            ]
        )
        == 0
    )
    assert "rec_variant" in source_map.read_text()
    # Model review is a separate authoring step. Supply explicit fixture review/evidence.
    ids = ("rec_seed", "rec_variant")
    source_map.write_text(
        "source_map_schema: 1\nexport_category: demo\npicture_category: Demo\n"
        "picture_subcategory: widget\ncategory_scope: test widget\nsync_records:\n"
        + "".join(f"  - {r}\n" for r in ids)
        + "\n| Record/Revision | Review status | Decision | Note |\n|---|---|---|---|\n"
        + "".join(f"| {r}/rev_000001 | reviewed | used | fixture review |\n" for r in ids)
        + "\n| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |\n"
        "|---|---|---|---|---|---|---|\n"
        + "".join(
            f"| body | body_{i} | enclosure | {r}/rev_000001 | model.py:L5-L25 | structure | test body |\n"
            for i, r in enumerate(ids)
        )
    )
    blueprint = tmp_path / "demo.json"
    assert (
        author(
            base
            + [
                "design-init",
                "demo",
                "--source-map",
                str(source_map),
                "--records-root",
                str(repo.layout.records_root),
                "--out",
                str(blueprint),
            ]
        )
        == 0
    )
    assert json.loads(blueprint.read_text())["slug"] == "demo"


def test_init_picture_and_missing_seed_leave_no_unbound_record(tmp_path):
    reference(tmp_path)
    assert (
        main(
            [
                "--repo-root",
                str(tmp_path),
                "init",
                "test",
                "--agent",
                "codex",
                "--picture",
                "picture/Demo/widget/reference.png",
                "--record-id",
                "rec_bound",
            ]
        )
        == 0
    )
    assert read_binding(StorageRepo(tmp_path), "rec_bound").category == "Demo"
    assert (
        main(
            [
                "--repo-root",
                str(tmp_path),
                "seed",
                "Demo/missing",
                "test",
                "--agent",
                "codex",
                "--record-id",
                "rec_missing",
            ]
        )
        == 1
    )
    assert not (tmp_path / "data/records/rec_missing").exists()
