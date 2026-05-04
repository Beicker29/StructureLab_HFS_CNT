"""Common reusable equations across multiple connection families."""

from .bolt_group_elastic import solve_elastic_center_of_rotation
from .bolt_group_elastic import solve_elastic_superposition
from .bolt_group_geometry import build_bolt_group_geometry
from .bolt_group_geometry import build_in_plane_load
from .bolt_group_geometry import build_in_plane_load_from_explicit_eccentricity
from .bolt_group_geometry import build_rectangular_bolt_pattern
from .bolt_group_icr import ICRLawParameters
from .bolt_group_icr import solve_instant_center_of_rotation
from .bolt_group_solver import BoltGroupSolverOptions
from .bolt_group_solver import solve_bolt_group_method
from .bolt_group_types import BoltCoordinate
from .bolt_group_types import BoltGroupMethod
from .bolts import compute_bolt_tension_rupture_capacity_per_bolt
from .bolts import compute_bolt_shear_rupture_capacity_per_bolt
from .bolts import compute_bolt_hole_dimensions_j33
from .bolts import compute_minimum_bolt_spacing_j33
from .bolts import compute_minimum_edge_distance_standard_hole_j34
from .bolts import compute_standard_hole_diameter_j33
from .bolts import compute_spacing_requirements_j33
from .bolts import compute_max_spacing_and_edge_distance_limits_j36
from .bolts import compute_maximum_bolt_spacing_j36
from .prequalified_ep import compute_limites_precalificacion_conexion_tipo_ep
from .utilization import compute_dcr_ratio

__all__ = [
    "BoltCoordinate",
    "BoltGroupMethod",
    "BoltGroupSolverOptions",
    "ICRLawParameters",
    "build_bolt_group_geometry",
    "build_in_plane_load",
    "build_in_plane_load_from_explicit_eccentricity",
    "build_rectangular_bolt_pattern",
    "compute_bolt_tension_rupture_capacity_per_bolt",
    "compute_bolt_shear_rupture_capacity_per_bolt",
    "compute_bolt_hole_dimensions_j33",
    "compute_minimum_bolt_spacing_j33",
    "compute_minimum_edge_distance_standard_hole_j34",
    "compute_standard_hole_diameter_j33",
    "compute_spacing_requirements_j33",
    "compute_max_spacing_and_edge_distance_limits_j36",
    "compute_maximum_bolt_spacing_j36",
    "compute_limites_precalificacion_conexion_tipo_ep",
    "compute_dcr_ratio",
    "solve_bolt_group_method",
    "solve_elastic_superposition",
    "solve_elastic_center_of_rotation",
    "solve_instant_center_of_rotation",
]
