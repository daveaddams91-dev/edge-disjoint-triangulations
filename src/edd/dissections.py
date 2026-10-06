"""Enumeration of dissections, triangulations and ``p``-angulations of a convex ``n``-gon.

A *dissection* of the convex ``n``-gon is a set of pairwise non-crossing diagonals; it
cuts the polygon into ``|D| + 1`` convex cells.  It is a *triangulation* (classical name:
*perfect dissection*) when every cell is a triangle, and a *``p``-angulation* when every
cell is a ``p``-gon.  A ``p``-angulation exists only if ``p`` divides ``n - 2``, and then
it uses exactly ``(n-p)/(p-2)`` diagonals (Euler's formula; see
:func:`p_angulation_diagonals`).

Enumeration uses the cell that contains the side ``(0, n-1)``: that cell is
``(0, c_1, ..., c_s, n-1)`` for some ``1 <= c_1 < ... < c_s <= n-2``, and the rest of the
polygon splits into the two smaller polygons ``0..c_1`` and ``c_s..n-1``.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import comb

from .polygon import Diagonal, Triangulation, diagonals, is_non_crossing



__all__ = [
    "dissections",
    "triangulations",
    "p_angulations",
    "dissections_upto",
    "p_angulation_diagonals",
    "num_triangulations",
    "num_dissections",
    "is_dissection",
    "is_triangulation",
]


@lru_cache(maxsize=None)
def _cells(n: int, max_cell_sides: int | None) -> tuple[tuple[int, ...], ...]:
    """Candidate vertex sets (excluding 0 and n-1) of the cell containing the side (0, n-1)."""
    interior = tuple(range(1, n - 1))
    if max_cell_sides is None:
        sizes = range(1, len(interior) + 1)
    else:
        sizes = range(1, min(max_cell_sides - 2, len(interior)) + 1)
    out: list[tuple[int, ...]] = []
    for s in sizes:
        out.extend(combinations(interior, s))
    return tuple(out)


@lru_cache(maxsize=None)
def _dissections_upto(n: int, max_cell_sides: int | None) -> tuple[frozenset[Diagonal], ...]:
    """All dissections of ``P_n`` whose cells have at most ``max_cell_sides`` sides.

    Recursion on the cell ``(0, c_1, ..., c_s, n-1)`` that contains the side ``(0, n-1)``:
    its boundary consists of the ``s+1`` diagonals ``(0, c_1), (c_1, c_2), ...,
    (c_s, n-1)`` that are diagonals of ``P_n``, and it leaves ``s+1`` regions
    ``(0..c_1), (c_1..c_2), ..., (c_s..n-1)``, each dissected independently.  This is a
    bijection between such dissections and (cell, choice of sub-dissection per region).
    """
    if n <= 2:
        return (frozenset(),)
    if n == 3:
        return (frozenset(),)
    all_d = set(diagonals(n))
    out: set[frozenset[Diagonal]] = set()
    for cell in _cells(n, max_cell_sides):
        verts = (0, *cell, n - 1)
        base: set[Diagonal] = set()
        for a, b in zip(verts, verts[1:
            ]):
            if b - a >= 2 and not (a == 0 and b == n - 1):
                base.add((a, b))
        subs = [
            _dissections_upto(b - a + 1, max_cell_sides) for a, b in zip(verts, verts[1:])
        ]

        @functools.lru_cache(maxsize=None)
        def combine(idx: int, acc: set[Diagonal], off: int) -> None:
            """Combine.
            
            Args:
                idx:
                acc:
                off:
            
            """
            if idx == len(subs):
                out.add(frozenset(acc))
                return
            a = verts[idx]
            for sub in subs[idx]:
                combine(
                    idx + 1,
                    acc | {(a + p, a + q) for p, q in sub},
                    off,
                )

        combine(0, set(base), 0)
    return tuple(sorted(out, key=lambda D: (len(D), sorted(D))))


def dissections(n: int) -> tuple[frozenset[Diagonal], ...]:
    """All dissections of the convex ``n``-gon (all non-crossing sets of diagonals)."""
    return _dissections_upto(n, None)


def dissections_upto(n: int, max_cell_sides: int) -> tuple[frozenset[Diagonal], ...]:
    """All dissections of ``P_n`` whose cells have at most ``max_cell_sides`` sides."""
    return _dissections_upto(n, max_cell_sides)


def triangulations(n: int) -> tuple[Triangulation, ...]:
    """All triangulations of the convex ``n``-gon, as frozensets of diagonals.

    The count is the Catalan number ``C_{n-2}`` (e.g. ``n = 8`` gives 132).
    """
    return _dissections_upto(n, 3)  # type: ignore[return-value]


def p_angulations(n: int, p: int) -> tuple[frozenset[Diagonal], ...]:
    """All ``p``-angulations (dissections into ``p``-gons) of the convex ``n``-gon.

    Empty unless ``(p - 2)`` divides ``n - 2``: Euler's formula forces the number of cells
    to be ``(n-2)/(p-2)`` and the number of diagonals to be ``(n-p)/(p-2)``.
    """
    if p < 3 or n < p or (n - 2) % (p - 2) != 0:
        return ()
    want = p_angulation_diagonals(n, p)
    return tuple(D for D in _dissections_upto(n, p) if len(D) == want)


def p_angulation_diagonals(n: int, p: int) -> int:
    """Number of diagonals in a ``p``-angulation of the ``n``-gon: ``(n-p)/(p-2)``.

    From ``p F = 2 D + n`` (each cell has ``p`` sides; interior diagonals are counted
    twice, the ``n`` sides once) together with Euler's identity ``F = D + 1``.  In
    particular a ``p``-angulation exists only if ``(p-2)`` divides ``n-2``, and then it
    has ``(n-2)/(p-2)`` cells.
    """
    return (n - p) // (p - 2)


def num_triangulations(n: int) -> int:
    """The Catalan number ``C_{n-2}``, i.e. the number of triangulations of ``P_n``."""
    return comb(2 * (n - 2), n - 2) // (n - 1)


def num_dissections(n: int) -> int:
    """The little Schroeder number ``s_{n-2}``, i.e. the number of dissections of ``P_n``."""
    return len(dissections(n))


def is_dissection(D: frozenset[Diagonal], n: int) -> bool:
    """True iff ``D`` is a non-crossing set of diagonals of the ``n``-gon."""
    return is_non_crossing(D, n)


def is_triangulation(D: frozenset[Diagonal], n: int) -> bool:
    """True iff ``D`` is a triangulation of the ``n``-gon."""
    return len(D) == n - 3 and D in set(triangulations(n))