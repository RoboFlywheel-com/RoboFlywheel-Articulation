# SPDX-License-Identifier: Apache-2.0

"""Deterministic material-pool retrieval and seed materialization."""

from .catalog import (
    MaterialCatalog,
    MaterialPhysics,
    MaterialPhysicsReference,
    MaterialRecord,
)
from .generator_annotations import (
    GENERATOR_CLASS_ANNOTATION_POLICY,
    GENERATOR_CLASS_ANNOTATIONS_SCHEMA,
    GENERATOR_CLASS_PROPOSALS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTING_KIND,
    MAX_MATERIAL_CLASS_VARIANTS,
    annotation_digest,
    build_generator_class_annotations,
    validate_generator_class_annotations,
)
from .lock import materialize_appearance_lock
from .material_classes import (
    MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
    MATERIAL_CLASS_POLICY_VERSION,
    MATERIAL_CLASS_REGISTRY_SCHEMA,
    MaterialClassAssignments,
    MaterialClassDefinition,
    MaterialClassRegistry,
    build_assignment_document,
)
from .pool_runtime import (
    PHYSICS_INDEX_SCHEMA,
    PHYSICS_REF_SCHEMA,
    PHYSICS_SIDECAR_SCHEMA,
    POINTER_SCHEMA,
    POOL_INDEX_SCHEMA,
    POOL_SCHEMA,
    RELEASE_SCHEMA,
    LoadedMaterialPools,
    load_material_physics,
    load_material_pools,
)
from .retrieval import (
    MATERIAL_CLASS_SELECTION_ALGORITHM,
    AppearanceRequest,
    ResolvedAppearance,
    appearance_requests_from_model,
    resolve_appearances_from_pools,
)

__all__ = [
    "AppearanceRequest",
    "MaterialCatalog",
    "MaterialClassAssignments",
    "MaterialClassDefinition",
    "MaterialClassRegistry",
    "MaterialRecord",
    "MaterialPhysics",
    "MaterialPhysicsReference",
    "LoadedMaterialPools",
    "ResolvedAppearance",
    "GENERATOR_CLASS_ANNOTATION_POLICY",
    "GENERATOR_CLASS_ANNOTATIONS_SCHEMA",
    "GENERATOR_CLASS_PROPOSALS_SCHEMA",
    "GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA",
    "GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY",
    "GENERATOR_CLASS_ROLE_ROUTING_KIND",
    "MAX_MATERIAL_CLASS_VARIANTS",
    "MATERIAL_CLASS_ASSIGNMENTS_SCHEMA",
    "MATERIAL_CLASS_POLICY_VERSION",
    "MATERIAL_CLASS_REGISTRY_SCHEMA",
    "MATERIAL_CLASS_SELECTION_ALGORITHM",
    "POINTER_SCHEMA",
    "POOL_INDEX_SCHEMA",
    "POOL_SCHEMA",
    "PHYSICS_INDEX_SCHEMA",
    "PHYSICS_REF_SCHEMA",
    "PHYSICS_SIDECAR_SCHEMA",
    "RELEASE_SCHEMA",
    "appearance_requests_from_model",
    "annotation_digest",
    "build_assignment_document",
    "build_generator_class_annotations",
    "materialize_appearance_lock",
    "load_material_pools",
    "load_material_physics",
    "resolve_appearances_from_pools",
    "validate_generator_class_annotations",
]
