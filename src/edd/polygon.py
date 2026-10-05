"""Convex polygons, their diagonals, and the local structure of triangulations.

Vertices of the convex ``n``-gon are labelled ``0, 1, ..., n-1`` in cyclic order.
Because the polygon is convex, two diagonals cross if and only if their endpoints
alternate in cyclic order; the geometric embedding is therefore irrelevant and all
questions in this package are purely combinatorial.

Conventions
-----------
* a *side* is a pair ``(i, i+1 mod n)``; a *diagonal* is a pair of vertices that is
  not a side, written with ``i < j``;
* ``(i, j)`` and ``(j, i)`` denote the same diagonal; we always store ``i < j``;
* ``cyclic_dist(i, j, n) = min(j - i, n - (j - i))`` is the cyclic distance
  between two vertices; the *level* of a diagonal is this distance, and it ranges
  over ``{2, ..., floor(n/2)}``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import FrozenSet, Iterable, Iterator

Diagonal = tuple[int, int]
Triangulation = FrozenSet[Diagonal]

__all__ = [
    "n_vertices",
    "sides",
    "diagonals",
    "diagonal_index",
    "cyclic_dist",
    "diagonal_level",
    "short_diagonals",
    "crosses",
    "crosses_any",
    "is_non_crossing",
    "edge_set",
    "triangles",
    "ear_vertices",
    "num_ears",
    "interior_triangles",
    "is_snake",
]


def n_vertices(poly: Iterable[object] | int) -> int:
    """Number of vertices (accepts an ``int`` for convenience)."""
    if isinstance(poly, int):
        return poly
    return len(tuple(poly))


@lru_cache(maxsize=None)
def sides(n: int) -> tuple[Diagonal, ...]:
    """The ``n`` sides of the convex ``n``-gon, in cyclic order starting at side ``(0,1)``."""
    if n < 3:
        raise ValueError("a polygon needs at least 3 vertices")
    return tuple(sorted({(i, (i + 1) % n) for i in range(n)}))


@lru_cache(maxsize=None)
def diagonals(n: int) -> tuple[Diagonal, ...]:
    """All diagonals of the convex ``n``-gon in lexicographic order.

    There are ``n(n-3)/2`` of them, indexed by position in this tuple.
    """
    if n < 3:
        raise ValueError("a polygon needs at least 3 vertices")
    return tuple(
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if j - i >= 2 and not (i == 0 and j == n - 1)
    )


@lru_cache(maxsize=None)
def diagonal_index(n: int) -> dict[Diagonal, int]:
    """Map each diagonal to its position in :func:`diagonals`."""
    return {d: k for k, d in enumerate(diagonals(n))}


def cyclic_dist(i: int, j: int, n: int) -> int:
    """Cyclic distance between vertices ``i`` and ``j`` of the ``n``-gon."""
    d = (j - i) % n
    return min(d, n - d)


def diagonal_level(d: Diagonal, n: int) -> int:
    """Level (cyclic distance) of the diagonal ``d = (i, j)``; values in ``2 .. floor(n/2)``."""
    return cyclic_dist(d[0], d[1], n)


@lru_cache(maxsize=None)
def short_diagonals(n: int) -> tuple[Diagonal, ...]:
    """The ``n`` diagonals of level 2, i.e. ``(v-1, v+1)`` for ``v`` in ``Z/nZ``.

    Diagonal ``(v-1, v+1)`` cuts off the vertex ``v``, so we call ``v`` its *ear vertex*.
    """
    return tuple(sorted(_norm_pair((v - 1) % n, (v + 1) % n) for v in range(n)))


def _norm_pair(i: int, j: int) -> Diagonal:
    return (i, j) if i < j else (j, i)


def crosses(a: Diagonal, b: Diagonal, n: int) -> bool:
    """Do the diagonals ``a`` and ``b`` cross in the interior of the convex ``n``-gon?

    Chords of a convex polygon cross exactly when their endpoints interleave:
    with ``a = (a0, a1)``, ``b = (b0, b1)`` and ``a0 < a1``, ``b0 < b1``, this
    means ``a0 < b0 < a1 < b1`` or ``b0 < a0 < b1 < a1``.  Chords sharing an
    endpoint never cross.  (No wrap-around case is needed because we only ever
    test diagonals, and the only chord whose endpoints are ``0`` and ``n-1`` is a side.)
    """
    if a == b or len({a[0], a[1], b[0], b[1]}) < 4:
        return False
    a0, a1 = a
    b0, b1 = b
    return (a0 < b0 < a1 < b1) or (b0 < a0 < b1 < a1)


def crosses_any(dset: Iterable[Diagonal], n: int) -> Diagonal | None:
    """Return a crossing pair inside ``dset``, or ``None`` if it is non-crossing."""
    items = list(dset)
    for x in range(len(items)):
        for y in range(x + 1, len(items)):
            if crosses(items[x], items[y], n):
                return (items[x], items[y])
    return None


def is_non_crossing(dset: Iterable[Diagonal], n: int) -> bool:
    """True iff no two members of ``dset`` cross."""
    return crosses_any(dset, n) is None


def edge_set(n: int) -> frozenset[Diagonal]:
    """All sides together with all diagonals: every edge of the complete graph on the vertices."""
    return frozenset(sides(n)) | frozenset(diagonals(n))


def triangles(T: Triangulation, n: int) -> tuple[frozenset[int], ...]:
    """The ``n-2`` triangles of the triangulation ``T`` (each as a frozenset of 3 vertices).

    The cell that contains the side ``(0, n-1)`` is found first and the recursion proceeds
    along its other two edges; for an edge ``(a, b)`` of the triangulation there is exactly
    one vertex ``c`` strictly between ``a`` and ``b`` with both ``(a, c)`` and ``(c, b)``
    present in ``sides(n) | T``.
    """
    E = set(sides(n)) | set(T)
    out: list[frozenset[int]] = []
    seen: set[frozenset[int]] = set()

    def walk(a: int, b: int) -> None:
        """Add the triangle on the arc (a, b) that contains the edge (a, b)."""
        if b - a < 2:
            return  # the edge (a, b) is a side of the polygon: nothing to recurse into
        for c in range(a + 1, b):
            if (a, c) in E and (c, b) in E:
                tri = frozenset({a, c, b})
                if tri not in seen:
                    seen.add(tri)
                    out.append(tri)
                walk(a, c)
                walk(c, b)
                return
        raise AssertionError(f"edge {(a, b)} is not covered by a triangle of {sorted(T)}")

    walk(0, n - 1)
    if len(out) != n - 2:
        raise AssertionError(f"{sorted(T)} does not triangulate P_{n}")
    return tuple(out)


def ear_vertices(T: Triangulation, n: int) -> tuple[int, ...]:
    """Vertices ``v`` whose incident triangle is the ear ``(v-1, v, v+1)``.

    Equivalently, the vertices ``v`` for which the short diagonal ``(v-1, v+1)``
    belongs to ``T``.  Returned in increasing order.
    """
    S = set(T)
    return tuple(v for v in range(n) if _norm_pair((v - 1) % n, (v + 1) % n) in S)


def num_ears(T: Triangulation, n: int) -> int:
    """Number of ears of ``T`` (equal to the number of level-2 diagonals of ``T``)."""
    return len(ear_vertices(T, n))


def interior_triangles(T: Triangulation, n: int) -> tuple[frozenset[int], ...]:
    """Triangles of ``T`` all three of whose edges are diagonals."""
    D = set(T)
    return tuple(tri for tri in triangles(T, n) if all(_norm_pair(a, b) in D for a, b in _pairs(tri)))


def _pairs(tri: FrozenSet[int]) -> Iterator[Diagonal]:
    ts = sorted(tri)
    return iter(((ts[0], ts[1]), (ts[0], ts[2]), (ts[1], ts[2])))


def is_snake(T: Triangulation, n: int) -> bool:
    """True iff ``T`` is a *snake*: a triangulation with no interior triangle.

    Equivalently, every triangle of ``T`` has a side of the polygon as one of its
    edges, equivalently the dual graph of ``T`` is a path.  For ``n >= 5`` this is
    also equivalent to ``T`` having exactly two ears.
    """
    return not interior_triangles(T, n)


def delete_vertex(T: Triangulation, n: int, x: int) -> Triangulation | None:
    r"""Delete vertex ``x`` of the ``n``-gon and return the induced dissection of ``P_{n-1}``.

    All diagonals meeting ``x`` are discarded, as is the short diagonal ``(x-1, x+1)``
    (which becomes a side of the smaller polygon).  The result is a triangulation of
    ``P_{n-1}`` exactly when at most one diagonal of ``T`` meets ``x``; otherwise
    ``None`` is returned.

    Only ``x = n-1`` is supported, with the labelling preserved (no relabelling); this is
    what :func:`edd.packing.odd_packing` needs.
    """
    if x != n - 1:
        raise ValueError("only deletion of the last vertex is supported")
    short = _norm_pair((x - 1) % n, (x + 1) % n)
    if sum(1 for d in T if x in d) > 1:
        return None
    return frozenset(d for d in T if x not in d and d != short)