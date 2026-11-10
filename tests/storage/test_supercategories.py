# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from storage.models import SupercategoryEntry, SupercategoryManifest
from storage.repo import StorageRepo
from storage.supercategories import SupercategoryStore


def test_round_trip_save_and_load(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)

    manifest = SupercategoryManifest(
        schema_version=1,
        supercategories=[
            SupercategoryEntry(
                slug="chains",
                title="Kinematic Chains",
                description="Multi-joint serial chains",
                category_slugs=["twojoint_revolute_chain", "threejoint_revolute_chain"],
            ),
            SupercategoryEntry(
                slug="arms",
                title="Robotic Arms",
                description="",
                category_slugs=["serial_elbow_arm"],
            ),
        ],
    )
    store.save(manifest)

    loaded = store.load_manifest()
    assert loaded is not None
    assert loaded.schema_version == 1
    assert len(loaded.supercategories) == 2
    assert loaded.supercategories[0].slug == "chains"
    assert loaded.supercategories[0].title == "Kinematic Chains"
    assert loaded.supercategories[0].description == "Multi-joint serial chains"
    assert loaded.supercategories[0].category_slugs == [
        "twojoint_revolute_chain",
        "threejoint_revolute_chain",
    ]
    assert loaded.supercategories[1].slug == "arms"
    assert loaded.supercategories[1].category_slugs == ["serial_elbow_arm"]


def test_load_missing_file_returns_none(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)
    assert store.load_manifest() is None


def test_category_to_supercategory_map(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)

    manifest = SupercategoryManifest(
        schema_version=1,
        supercategories=[
            SupercategoryEntry(
                slug="chains",
                title="Kinematic Chains",
                category_slugs=["twojoint_revolute_chain", "threejoint_revolute_chain"],
            ),
            SupercategoryEntry(
                slug="arms",
                title="Robotic Arms",
                category_slugs=["serial_elbow_arm"],
            ),
        ],
    )
    store.save(manifest)

    cat_map = store.build_category_to_supercategory_map()
    assert cat_map == {
        "twojoint_revolute_chain": "chains",
        "threejoint_revolute_chain": "chains",
        "serial_elbow_arm": "arms",
    }


def test_category_to_supercategory_map_empty_when_missing(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)
    assert store.build_category_to_supercategory_map() == {}


def test_duplicate_category_first_wins(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)

    manifest = SupercategoryManifest(
        schema_version=1,
        supercategories=[
            SupercategoryEntry(
                slug="group_a",
                title="Group A",
                category_slugs=["shared_cat"],
            ),
            SupercategoryEntry(
                slug="group_b",
                title="Group B",
                category_slugs=["shared_cat"],
            ),
        ],
    )
    store.save(manifest)

    cat_map = store.build_category_to_supercategory_map()
    assert cat_map["shared_cat"] == "group_a"


def test_to_dict_round_trips(tmp_path: Path) -> None:
    manifest = SupercategoryManifest(
        schema_version=1,
        supercategories=[
            SupercategoryEntry(
                slug="test",
                title="Test",
                description="desc",
                category_slugs=["cat_a", "cat_b"],
            ),
        ],
    )
    data = manifest.to_dict()
    assert data["schema_version"] == 1
    assert len(data["supercategories"]) == 1
    assert data["supercategories"][0]["slug"] == "test"
    assert data["supercategories"][0]["category_slugs"] == ["cat_a", "cat_b"]


def test_save_entry_updates_existing(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)

    created_entry, created = store.save_entry(
        SupercategoryEntry(
            slug="chains",
            title="Chains",
            description="Initial",
            category_slugs=["cat_a"],
        )
    )
    assert created is True
    assert created_entry.category_slugs == ["cat_a"]

    updated_entry, created = store.save_entry(
        SupercategoryEntry(
            slug="chains",
            title="Kinematic Chains",
            description="Updated",
            category_slugs=["cat_a", "cat_b", "cat_a", ""],
        )
    )
    assert created is False
    assert updated_entry.title == "Kinematic Chains"
    assert updated_entry.category_slugs == ["cat_a", "cat_b"]

    loaded = store.load_entry("chains")
    assert loaded is not None
    assert loaded.description == "Updated"
    assert loaded.category_slugs == ["cat_a", "cat_b"]


def test_assign_category_rehomes_existing_membership(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)
    store.save(
        SupercategoryManifest(
            schema_version=1,
            supercategories=[
                SupercategoryEntry(
                    slug="chains",
                    title="Chains",
                    category_slugs=["shared_cat", "shared_cat", "cat_a"],
                ),
                SupercategoryEntry(
                    slug="arms",
                    title="Arms",
                    category_slugs=["cat_b"],
                ),
            ],
        )
    )

    previous_supercategory_slug = store.assign_category(
        category_slug="shared_cat",
        supercategory_slug="arms",
    )

    assert previous_supercategory_slug == "chains"
    manifest = store.load_manifest()
    assert manifest is not None
    assert manifest.supercategories[0].category_slugs == ["cat_a"]
    assert manifest.supercategories[1].category_slugs == ["cat_b", "shared_cat"]


def test_remove_category_and_delete_supercategory(tmp_path: Path) -> None:
    repo = StorageRepo(tmp_path)
    repo.ensure_layout()
    store = SupercategoryStore(repo)
    store.save(
        SupercategoryManifest(
            schema_version=1,
            supercategories=[
                SupercategoryEntry(
                    slug="chains",
                    title="Chains",
                    category_slugs=["cat_a", "cat_b"],
                ),
                SupercategoryEntry(
                    slug="arms",
                    title="Arms",
                    category_slugs=["cat_c"],
                ),
            ],
        )
    )

    previous_supercategory_slug = store.remove_category("cat_b")
    assert previous_supercategory_slug == "chains"

    deleted_entry = store.delete_supercategory("arms")
    assert deleted_entry is not None
    assert deleted_entry.slug == "arms"

    manifest = store.load_manifest()
    assert manifest is not None
    assert [entry.slug for entry in manifest.supercategories] == ["chains"]
    assert manifest.supercategories[0].category_slugs == ["cat_a"]
