# SPDX-License-Identifier: Apache-2.0

"""Shared internal SDK v0 implementation."""

# ruff: noqa: F401
from .articulated_object import ArticulatedObject
from .assets import AssetContext, AssetSession, activate_asset_session
from .errors import SDKError, ValidationError
from .geometry_qc import find_geometry_overlaps_in_poses
from .geometry_scale import scale_geometry_to_size
from .mechanisms import coupled_chain, hinged_panel
from .motion_solve import ClearanceProbe
from .placement import (
    AxisInterface,
    InterfaceMate,
    InterfaceMateFinding,
    PlaneInterface,
    SurfaceFrame,
    SurfaceWrapMapping,
    align_centers,
    find_interface_mate_findings,
    mate_axes,
    mate_planes,
    part_local_aabb,
    place_on_face,
    place_on_face_uv,
    place_on_surface,
    proud_for_flush_mount,
    register_interface_mate,
    surface_frame,
    wrap_mesh_onto_surface,
    wrap_profile_onto_surface,
)
from .template_domain import (
    CornerCase,
    DomainSlot,
    TemplateDomain,
    TemplateDomainError,
    component_slot,
    corner_case,
    multiplicity_slot,
)
from .testing import TestContext, TestFailure, TestReport
from .types import (
    BLENDERKIT_MATERIAL_CATEGORIES,
    AppearanceOnlyKind,
    AppearanceOnlySpec,
    Articulation,
    ArticulationType,
    Box,
    Cylinder,
    Inertia,
    Inertial,
    Material,
    MatingContract,
    Mesh,
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    Part,
    Sphere,
    Visual,
)
