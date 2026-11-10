# SPDX-License-Identifier: Apache-2.0

"""Registry and adapters for controlled morphology generators."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class RegistryError(ValueError):
    """Raised when a generator does not satisfy the controlled pipeline contract."""


@dataclass(frozen=True, slots=True)
class GeneratorRegistration:
    generator_id: str
    module_name: str
    source_filename: str
    upstream_template_filename: str
    asset_category: str
    build_function: str
    test_function: str
    version: str = "1"
    metadata_function: str = "benchmark_metadata"
    variable_space_function: str = "variable_space"

    @property
    def source_path(self) -> Path:
        return Path(__file__).resolve().parent / "generators" / self.source_filename

    @property
    def upstream_template_path(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "agent"
            / "templates"
            / self.upstream_template_filename
        )

    @property
    def upstream_generator_id(self) -> str:
        return Path(self.upstream_template_filename).stem

    def load_module(self) -> ModuleType:
        if not self.source_path.is_file():
            raise RegistryError(
                f"Generator {self.generator_id!r} is registered but missing: {self.source_path}"
            )
        return importlib.import_module(self.module_name)

    def source_sha256(self) -> str:
        return hashlib.sha256(self.source_path.read_bytes()).hexdigest()

    def upstream_template_sha256(self) -> str:
        if not self.upstream_template_path.is_file():
            raise RegistryError(
                f"Generator {self.generator_id!r} has missing upstream template: "
                f"{self.upstream_template_path}"
            )
        return hashlib.sha256(self.upstream_template_path.read_bytes()).hexdigest()

    def _callable(self, module: ModuleType, name: str) -> Callable[..., Any]:
        value = getattr(module, name, None)
        if not callable(value):
            raise RegistryError(f"Generator {self.generator_id!r} must expose callable {name}()")
        return value

    def validate_contract(self) -> ModuleType:
        module = self.load_module()
        self.upstream_template_sha256()
        config_type = getattr(module, "Config", None)
        if not isinstance(config_type, type) or not dataclasses.is_dataclass(config_type):
            raise RegistryError(f"Generator {self.generator_id!r} must expose dataclass Config")
        self._callable(module, self.build_function)
        self._callable(module, self.test_function)
        self._callable(module, "resolve_config")
        self._callable(module, self.metadata_function)
        self._callable(module, self.variable_space_function)
        return module

    def make_config(self, values: dict[str, Any]) -> Any:
        module = self.validate_contract()
        config_type = module.Config
        fields = {field.name for field in dataclasses.fields(config_type)}
        unknown = sorted(set(values) - fields)
        if unknown:
            raise RegistryError(
                f"Unknown Config field(s) for {self.generator_id}: {', '.join(unknown)}"
            )
        try:
            return config_type(**values)
        except TypeError as exc:
            raise RegistryError(f"Invalid Config for {self.generator_id}: {exc}") from exc

    def resolve_config(self, config: Any) -> Any:
        module = self.validate_contract()
        return module.resolve_config(config)

    def benchmark_metadata(self, config: Any) -> dict[str, Any]:
        module = self.validate_contract()
        metadata = self._callable(module, self.metadata_function)(config)
        if not isinstance(metadata, dict):
            raise RegistryError(
                f"{self.generator_id}.{self.metadata_function}() must return a dictionary"
            )
        required = {
            "target_joint",
            "target_link",
            "joint_type",
            "axis",
            "limits",
            "opening_sign",
            "opening_endpoint",
            "handle_frame",
            "front_axis",
            "up_axis",
        }
        missing = sorted(required - set(metadata))
        if missing:
            raise RegistryError(
                f"{self.generator_id}.{self.metadata_function}() is missing: {', '.join(missing)}"
            )
        return metadata

    def variable_space(self) -> dict[str, Any]:
        module = self.validate_contract()
        payload = self._callable(module, self.variable_space_function)()
        if not isinstance(payload, dict):
            raise RegistryError(
                f"{self.generator_id}.{self.variable_space_function}() must return a dictionary"
            )
        variables = payload.get("variables")
        if payload.get("schema_version") != 1 or not isinstance(variables, dict):
            raise RegistryError(
                f"{self.generator_id}.{self.variable_space_function}() must expose "
                "schema_version=1 and variables"
            )
        payload = dict(payload)
        payload["provenance"] = {
            "upstream_template_path": f"agent/templates/{self.upstream_template_filename}",
            "upstream_template_sha256": self.upstream_template_sha256(),
            "upstream_generator_id": self.upstream_generator_id,
            "asset_category": self.asset_category,
            "task_variant": self.generator_id,
            "task_copy_path": f"controlled_morphology/generators/{self.source_filename}",
        }
        return payload


_REGISTRY: dict[str, GeneratorRegistration] = {
    "single_door_cabinet": GeneratorRegistration(
        generator_id="single_door_cabinet",
        module_name="controlled_morphology.generators.single_door_cabinet",
        source_filename="single_door_cabinet.py",
        upstream_template_filename="pictureX_0611_Cabinet_with_doors.py",
        asset_category="cabinet_with_doors",
        build_function="build_single_door_cabinet",
        test_function="run_single_door_cabinet_tests",
        version="4",
    ),
    "single_drawer_cabinet": GeneratorRegistration(
        generator_id="single_drawer_cabinet",
        module_name="controlled_morphology.generators.single_drawer_cabinet",
        source_filename="single_drawer_cabinet.py",
        upstream_template_filename="pictureX_0611_kitchen_cabinet.py",
        asset_category="kitchen_cabinet",
        build_function="build_single_drawer_cabinet",
        test_function="run_single_drawer_cabinet_tests",
        version="4",
    ),
    "multi_door_cabinet": GeneratorRegistration(
        generator_id="multi_door_cabinet",
        module_name="controlled_morphology.generators.multi_door_cabinet",
        source_filename="multi_door_cabinet.py",
        upstream_template_filename="pictureX_0611_Cabinet_with_doors.py",
        asset_category="cabinet_with_doors",
        build_function="build_multi_door_cabinet",
        test_function="run_multi_door_cabinet_tests",
        version="3",
    ),
    "multi_drawer_cabinet": GeneratorRegistration(
        generator_id="multi_drawer_cabinet",
        module_name="controlled_morphology.generators.multi_drawer_cabinet",
        source_filename="multi_drawer_cabinet.py",
        upstream_template_filename="drawer_cabinet_with_sliding_drawers.py",
        asset_category="drawer_cabinet_with_sliding_drawers",
        build_function="build_multi_drawer_cabinet",
        test_function="run_multi_drawer_cabinet_tests",
    ),
    "kitchen_cabinet_access": GeneratorRegistration(
        generator_id="kitchen_cabinet_access",
        module_name="controlled_morphology.generators.kitchen_cabinet_access",
        source_filename="kitchen_cabinet_access.py",
        upstream_template_filename="pictureX_0611_kitchen_cabinet.py",
        asset_category="kitchen_cabinet",
        build_function="build_kitchen_cabinet_access",
        test_function="run_kitchen_cabinet_access_tests",
        version="3",
    ),
}


def list_generators() -> tuple[str, ...]:
    """Return registered generator ids in deterministic order."""

    return tuple(sorted(_REGISTRY))


def get_generator(generator_id: str) -> GeneratorRegistration:
    """Look up one generator, raising a user-facing error for unknown ids."""

    try:
        return _REGISTRY[generator_id]
    except KeyError as exc:
        choices = ", ".join(list_generators())
        raise RegistryError(
            f"Unknown generator {generator_id!r}; choose one of: {choices}"
        ) from exc


__all__ = [
    "GeneratorRegistration",
    "RegistryError",
    "get_generator",
    "list_generators",
]
