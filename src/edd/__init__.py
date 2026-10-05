"""edd: edge-disjoint triangulations of convex polygons.

Reference
---------
D. A. Smith, *Edge-disjoint triangulations of convex polygons: packing numbers,
resolutions and their classification* (2026); see ``paper/main.tex``.

Quick start
-----------
>>> from edd import max_packing, num_antipodal_resolutions, antipodal_resolutions
>>> max_packing(12)
6
>>> num_antipodal_resolutions(12)
16
>>> res = antipodal_resolutions(12)[0]
>>> len(res), res.n
(6, 12)
"""

from __future__ import annotations

from .polygon import (
    cyclic_dist,
    diagonal_level,
    diagonals,
    ear_vertices,
    interior_triangles,
    is_non_crossing,
    is_snake,
    num_ears,
    short_diagonals,
    sides,
    triangles,
)
from .dissections import (
    dissections,
    num_dissections,
    num_triangulations,
    p_angulation_diagonals,
    p_angulations,
    triangulations,
)
from .snakes import (
    antipodal_resolution,
    antipodal_words,
    num_snakes,
    snake_from_word,
    snakes,
    strip_level,
    word_from_snake,
)
from .resolution import (
    CLASSIFICATION,
    COMPLETENESS_OPEN,
    Resolution,
    antipodal_resolutions,
    diagonal_starts,
    ear_matching,
    family_word,
    is_antipodal_family,
    level_condition,
    level_condition_holds,
    num_antipodal_resolutions,
    resolution_from_word,
    strip_diagonals,
)
from .packing import (
    count_all_packs,
    count_k_dissections,
    ilp_certificate,
    max_packing,
    packing_feasible,
    packing_ilp,
    packing_upper_bound,
)
from .verify import (
    ResolutionReport,
    brute_force_count_resolutions,
    brute_force_resolutions,
    count_resolutions,
    extends_to_resolution,
    verify_completeness,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # polygon
    "sides",
    "diagonals",
    "diagonal_level",
    "cyclic_dist",
    "short_diagonals",
    "triangles",
    "ear_vertices",
    "num_ears",
    "interior_triangles",
    "is_snake",
    "is_non_crossing",
    # dissections
    "dissections",
    "triangulations",
    "p_angulations",
    "p_angulation_diagonals",
    "num_triangulations",
    "num_dissections",
    # snakes
    "snakes",
    "num_snakes",
    "snake_from_word",
    "word_from_snake",
    "strip_level",
    "antipodal_words",
    "antipodal_resolution",
    # resolutions
    "Resolution",
    "resolution_from_word",
    "antipodal_resolutions",
    "num_antipodal_resolutions",
    "ear_matching",
    "is_antipodal_family",
    "family_word",
    "strip_diagonals",
    "diagonal_starts",
    "level_condition",
    "level_condition_holds",
    "CLASSIFICATION",
    "COMPLETENESS_OPEN",
    # packing
    "max_packing",
    "packing_upper_bound",
    "packing_ilp",
    "packing_feasible",
    "count_k_dissections",
    "count_all_packs",
    "ilp_certificate",
    # verification
    "ResolutionReport",
    "count_resolutions",
    "brute_force_resolutions",
    "brute_force_count_resolutions",
    "extends_to_resolution",
    "verify_completeness",
]