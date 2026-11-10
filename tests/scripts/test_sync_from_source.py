# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.sync_from_source import (
    _export_category_from_source_map,
    _record_ids_from_source_map,
    _stamp_metadata,
)


def _record_dirs(root: Path, *record_ids: str) -> Path:
    records = root / "records"
    records.mkdir()
    for record_id in record_ids:
        (records / record_id).mkdir()
    return records


def test_explicit_sync_manifest_excludes_blocked_record_mentions(tmp_path: Path) -> None:
    records = _record_dirs(tmp_path, "rec_accepted", "rec_blocked")
    source_map = tmp_path / "source_map.md"
    source_map.write_text(
        """# source map

```yaml
sync_records:
  - rec_accepted
```

## Blocked / Excluded
- `rec_blocked`: invalid host geometry.
""",
        encoding="utf-8",
    )

    assert _record_ids_from_source_map(str(source_map), str(records)) == ["rec_accepted"]


def test_legacy_source_map_still_resolves_existing_record_tokens(tmp_path: Path) -> None:
    records = _record_dirs(tmp_path, "rec_first", "rec_second")
    source_map = tmp_path / "legacy.md"
    source_map.write_text("accepted: rec_first\nblocked: rec_second\n", encoding="utf-8")

    assert _record_ids_from_source_map(str(source_map), str(records)) == [
        "rec_first",
        "rec_second",
    ]


def test_explicit_sync_manifest_rejects_missing_records(tmp_path: Path) -> None:
    records = _record_dirs(tmp_path, "rec_present")
    source_map = tmp_path / "source_map.md"
    source_map.write_text("sync_records:\n  - rec_missing\n", encoding="utf-8")

    with pytest.raises(ValueError, match="rec_missing"):
        _record_ids_from_source_map(str(source_map), str(records))


def test_export_category_is_read_from_category_binding(tmp_path: Path) -> None:
    source_map = tmp_path / "source_map.md"
    source_map.write_text(
        """```yaml
category_binding:
  category_id: speed_gate
  export_category: speed_gate
```
""",
        encoding="utf-8",
    )

    assert _export_category_from_source_map(str(source_map)) == "speed_gate"


def test_stamp_metadata_sets_rating_and_category(tmp_path: Path) -> None:
    record_json = tmp_path / "record.json"
    record_json.write_text(
        '{"record_id": "rec_test", "rating": null, "category_slug": null}\n',
        encoding="utf-8",
    )

    status, changed = _stamp_metadata(
        str(record_json), 5, "speed_gate", execute=True
    )

    assert changed is True
    assert status == "rating->5 category->speed_gate"
    assert record_json.read_text(encoding="utf-8").endswith("\n")
    assert json.loads(record_json.read_text(encoding="utf-8")) == {
        "record_id": "rec_test",
        "rating": 5,
        "category_slug": "speed_gate",
    }
