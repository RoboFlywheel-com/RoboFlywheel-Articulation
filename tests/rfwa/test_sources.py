# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json

import pytest

from rfwa.sources import import_record


def source_record(root):
    record = root / "data/records/rec_example"
    record.mkdir(parents=True)
    (record / "record.json").write_text(json.dumps({"rating": 2, "collections": ["workbench"]}))
    (record / "model.py").write_text("# existing source\n")
    return record


def test_import_preserves_metadata_and_records_file_hashes(tmp_path):
    source = source_record(tmp_path / "source")
    target = import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    assert (target / "record.json").read_bytes() == (source / "record.json").read_bytes()
    receipt = json.loads((tmp_path / "target/data/source_imports/rec_example.json").read_text())
    assert len(receipt["files"]["model.py"]) == 64
    with pytest.raises(FileExistsError):
        import_record(tmp_path / "source", tmp_path / "target", "rec_example")


def test_source_import_rejects_symlinks_and_path_traversal(tmp_path):
    source = source_record(tmp_path / "source")
    (source / "outside").symlink_to(tmp_path)
    with pytest.raises(ValueError, match="symlink"):
        import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    with pytest.raises(ValueError, match="record ID"):
        import_record(tmp_path / "source", tmp_path / "target", "rec_../../escape")


def test_import_keeps_reference_image_and_reports_missing_images(tmp_path):
    source = source_record(tmp_path / "source")
    image = tmp_path / "source/picture/Demo/widget/ref.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"reference image fixture")
    (source / "picture.json").write_text(
        json.dumps(
            {"category": "Demo", "subcategory": "widget", "path": "picture/Demo/widget/ref.png"}
        )
    )
    import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    assert (tmp_path / "target/picture/Demo/widget/ref.png").read_bytes() == image.read_bytes()
    receipt = json.loads((tmp_path / "target/data/source_imports/rec_example.json").read_text())
    assert receipt["reference_picture_sha256"] == hashlib.sha256(image.read_bytes()).hexdigest()
    image.unlink()
    import_record(tmp_path / "source", tmp_path / "target_missing", "rec_example")
    receipt = json.loads(
        (tmp_path / "target_missing/data/source_imports/rec_example.json").read_text()
    )
    assert receipt["reference_picture"] == "missing_in_source"


def test_import_picture_conflict_does_not_copy_record(tmp_path):
    source = source_record(tmp_path / "source")
    relative = "picture/Demo/widget/ref.png"
    (source / "picture.json").write_text(json.dumps({"path": relative}))
    for root, content in (("source", b"source"), ("target", b"different")):
        image = tmp_path / root / relative
        image.parent.mkdir(parents=True)
        image.write_bytes(content)
    with pytest.raises(FileExistsError, match="different reference picture"):
        import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    assert not (tmp_path / "target/data/records/rec_example").exists()


def test_invalid_empty_picture_path_is_rejected_before_import(tmp_path):
    source = source_record(tmp_path / "source")
    (source / "picture.json").write_text(json.dumps({"path": "."}))
    with pytest.raises(ValueError, match="unsafe picture"):
        import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    assert not (tmp_path / "target/data/records/rec_example").exists()


def test_failed_picture_copy_does_not_publish_record(monkeypatch, tmp_path):
    import rfwa.sources

    source = source_record(tmp_path / "source")
    image = tmp_path / "source/picture/Demo/widget/ref.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"reference")
    (source / "picture.json").write_text(json.dumps({"path": "picture/Demo/widget/ref.png"}))
    original = rfwa.sources.shutil.copy2

    def copy(source_path, target_path, **kwargs):
        if source_path == image:
            raise OSError("fixture image copy failure")
        return original(source_path, target_path, **kwargs)

    monkeypatch.setattr(rfwa.sources.shutil, "copy2", copy)
    with pytest.raises(OSError, match="image copy failure"):
        import_record(tmp_path / "source", tmp_path / "target", "rec_example")
    assert not (tmp_path / "target/data/records/rec_example").exists()
    monkeypatch.setattr(rfwa.sources.shutil, "copy2", original)
    assert import_record(tmp_path / "source", tmp_path / "target", "rec_example").is_dir()
