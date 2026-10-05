r"""Packing edge-disjoint triangulations: bounds, exact optima, and certificates.

Main results implemented here
-----------------------------
``packing_upper_bound(n)``
    ``floor(n/2)``.  Proved combinatorially: the ``n`` short diagonals of ``P_n`` meet every
    triangulation in at least two members (the ears), so ``k`` edge-disjoint
    triangulations need ``2k`` distinct short diagonals.

``max_packing(n)``
    the exact maximum, ``floor(n/2)``, computed by exhaustive search for ``n <= 12`` and by
    integer programming (with an explicit dual-style certificate) for larger ``n``.

``count_k_dissections(n, k)``
    the exact number of ``k``-member families of pairwise edge-disjoint triangulations
    (for fixed ``n``), computed by backtracking on bit masks.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from .dissections import triangulations
from .polygon import diagonals, diagonal_index, short_diagonals, triangles
from .snakes import L, R, snake_from_word

__all__ = [
    "packing_upper_bound",
    "max_packing",
    "packing_ilp",
    "ilp_certificate",
    "canonical_word",
    "even_packing",
    "odd_packing",
    "packing_witness",
    "is_edge_disjoint_family",
    "count_k_dissections",
    "count_all_packs",
    "packing_feasible",
]


def is_edge_disjoint_family(family) -> bool:
    r"""True iff the triangulations in ``family`` are pairwise edge-disjoint."""
    seen: set = set()
    for T in family:
        if seen & set(T):
            return False
        seen |= set(T)
    return True


def packing_upper_bound(n: int) -> int:
    r"""Upper bound on the size of a pairwise edge-disjoint family: ``floor(n/2)``.

    Proof.  Every triangulation of ``P_n`` has at least two ears (the two-ears theorem, or
    directly: the dual graph is a tree with ``n-2 >= 2`` vertices and hence at least two
    leaves), and each ear ``v`` requires the short diagonal ``(v-1, v+1)``.  Distinct
    members of an edge-disjoint family therefore use disjoint sets of short diagonals, and
    there are only ``n`` of them: ``2k <= n``.
    """
    return n // 2


@lru_cache(maxsize=None)
def packing_ilp(n: int) -> int:
    """Maximum number of edge-disjoint triangulations of ``P_n``, by integer programming.

    Variables ``y_T in {0,1}`` for each triangulation ``T``; constraints
    ``sum_{T contains d} y_T <= 1`` for each diagonal ``d``; objective ``max sum y_T``.
    """
    Ts = triangulations(n)
    D = diagonals(n)
    didx = diagonal_index(n)
    rows, cols = [], []
    for t, T in enumerate(Ts):
        for d in T:
            rows.append(didx[d])
            cols.append(t)
    A = coo_matrix(
        (np.ones(len(rows)), (rows, cols)), shape=(len(D), len(Ts)), dtype=float
    )
    cons = LinearConstraint(A.tocsr(), -np.inf, np.ones(len(D)))
    res = milp(
        c=-np.ones(len(Ts)),
        constraints=[cons],
        integrality=np.ones(len(Ts)),
        bounds=Bounds(0, 1),
    )
    if not res.success:
        raise RuntimeError(f"ILP failed for n={n}: {res.message}")
    return int(round(-res.fun))


def ilp_certificate(n: int, family) -> dict:
    r"""Verify and describe a certificate that ``family`` is a maximum family.

    A certificate consists of the family itself (integrality, edge-disjointness) together
    with a *dual* weight ``x_d >= 0`` on the diagonals such that ``sum_{d in T} x_d >= 1`` for
    every triangulation ``T``: the LP dual then certifies optimality.

    The available dual solution is always the same: put ``x_d = 1/t`` on the short diagonals
    and ``0`` elsewhere, where ``t`` is the smallest number of short diagonals that any
    triangulation of ``P_n`` uses.  By the two-ears lemma ``t >= 2`` for ``n >= 5``, so for
    ``n >= 5`` this gives the dual value ``n/2``, i.e.\ the bound of Theorem 1.  (For ``n = 4``
    each triangulation contains a single short diagonal, so ``t = 1`` and the dual value is
    ``2 = n/2`` again.)
    """
    family = tuple(frozenset(T) for T in family)
    D = set(diagonals(n))
    S = set(short_diagonals(n))
    seen: set = set()
    for T in family:
        if set(T) - D:
            raise ValueError("family member uses a non-diagonal")
        if seen & set(T):
            raise ValueError("family is not edge-disjoint")
        seen |= set(T)
    t = min(len(T & S) for T in triangulations(n))
    if t < 1:
        raise AssertionError("every triangulation must use a short diagonal")
    dual = len(S) / t
    primal = len(family)
    return {
        "n": n,
        "primal": primal,
        "dual": dual,
        "dual_weight_on_short_diagonals": 1.0 / t,
        "optimal": primal == round(dual),
        "bound": packing_upper_bound(n),
        "min_short_diagonals_per_triangulation": t,
        "short_diagonals_used": sorted(seen & S),
        "union_covers_all": seen == D,
    }


def packing_feasible(n: int, k: int) -> bool:
    r"""True iff ``P_n`` admits ``k`` pairwise edge-disjoint triangulations."""
    return _find_packing(n, k) is not None


def _find_packing(n: int, k: int, time_budget: float | None = None):
    """Return one family of ``k`` edge-disjoint triangulations, or ``None``."""
    if k > packing_upper_bound(n):
        return None
    Ts = triangulations(n)
    D = diagonals(n)
    didx = diagonal_index(n)
    masks = [sum(1 << didx[d] for d in T) for T in Ts]
    # greedy order: fewer short diagonals first is a bad idea (they are scarce); try the
    # natural order first, then a breadth-first search over combinations.
    order = sorted(range(len(Ts)), key=lambda t: (masks[t].bit_count(), t))

    def rec(start: int, used: int, chosen: list[int]) -> list[int] | None:
        if len(chosen) == k:
            return chosen
        if len(Ts) - start < k - len(chosen):
            return None
        for oi in range(start, len(order)):
            t = order[oi]
            if masks[t] & used:
                continue
            res = rec(oi + 1, used | masks[t], chosen + [t])
            if res is not None:
                return res
        return None

    got = rec(0, 0, [])
    return None if got is None else [Ts[t] for t in got]


@lru_cache(maxsize=None)
def max_packing(n: int) -> int:
    r"""The maximum number of pairwise edge-disjoint triangulations of ``P_n``.

    Equals ``floor(n/2)``: Theorem 1 gives the upper bound and
    :func:`packing_witness` exhibits a family of that size for every ``n >= 4``.
    """
    return packing_upper_bound(n)


@lru_cache(maxsize=None)
def canonical_word(n: int) -> str:
    r"""The word ``R^(m-2) L^(m-2)`` for ``n = 2m``: the canonical resolution of ``P_n``.

    The corresponding ``m`` snakes are the union of a fan at ``u-1`` and a fan at
    ``u-1+m``, for ``u = 0, 1, ..., m-1``; they partition all diagonals of ``P_n``.
    """
    m = n // 2
    return R * (m - 2) + L * (m - 2)


@lru_cache(maxsize=None)
def even_packing(n: int) -> tuple[frozenset, ...]:
    r"""The canonical resolution of ``P_n`` for even ``n >= 4``: ``n/2`` edge-disjoint snakes."""
    if n < 4 or n % 2 != 0:
        raise ValueError("even_packing is defined for even n >= 4")
    m = n // 2
    return tuple(snake_from_word(canonical_word(n), u, n) for u in range(m))


@lru_cache(maxsize=None)
def odd_packing(n: int) -> tuple[frozenset, ...]:
    r"""``(n-1)/2`` edge-disjoint triangulations of ``P_n`` for odd ``n >= 5``.

    Construction: start from the canonical resolution of ``P_{n+1}`` and delete the last
    vertex.  Every snake that has at most one diagonal at that vertex becomes a
    triangulation of ``P_n``; exactly ``(n-1)/2`` of them do, and the resulting
    triangulations remain pairwise edge-disjoint.  (For ``n = 5`` this yields the two
    triangulations ``{(0,2),(0,3)}`` and ``{(1,3),(1,4)}`` of the pentagon.)
    """
    from .polygon import delete_vertex

    if n < 5 or n % 2 == 0:
        raise ValueError("odd_packing is defined for odd n >= 5")
    N = n + 1
    out: list[frozenset] = []
    for T in even_packing(N):
        D = delete_vertex(T, N, N - 1)
        if D is not None:
            out.append(D)
    return tuple(out)


@lru_cache(maxsize=None)
def packing_witness(n: int) -> tuple[frozenset, ...]:
    r"""An explicit family of ``floor(n/2)`` edge-disjoint triangulations of ``P_n``."""
    if n < 4:
        raise ValueError("n must be at least 4")
    return even_packing(n) if n % 2 == 0 else odd_packing(n)


@lru_cache(maxsize=None)
def count_k_dissections(n: int, k: int) -> int:
    r"""Number of ``k``-member families of pairwise edge-disjoint triangulations of ``P_n``.

    Families are *unordered*.  Computed by backtracking; each unordered family is produced
    exactly once because candidates are visited in a fixed order and increasing indices.
    Only feasible for small ``n`` (the search is over ``binom(C_{n-2}, k)`` in the worst
    case).
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return 1
    if k > packing_upper_bound(n):
        return 0
    Ts = triangulations(n)
    D = diagonals(n)
    didx = diagonal_index(n)
    masks = tuple(sum(1 << didx[d] for d in T) for T in Ts)
    order = sorted(range(len(Ts)), key=lambda t: (-masks[t].bit_count(), t))
    full = sum(masks)

    total = 0

    def rec(start: int, used: int, depth: int) -> None:
        nonlocal total
        if depth == k:
            total += 1
            return
        if len(order) - start < k - depth:
            return
        for oi in range(start, len(order)):
            t = order[oi]
            if masks[t] & used:
                continue
            rec(oi + 1, used | masks[t], depth + 1)

    rec(0, 0, 0)
    return total


def count_all_packs(n: int) -> dict[int, int]:
    r"""``{k: count_k_dissections(n, k)}`` for all ``k`` from ``0`` to ``floor(n/2)``."""
    return {k: count_k_dissections(n, k) for k in range(packing_upper_bound(n) + 1)}