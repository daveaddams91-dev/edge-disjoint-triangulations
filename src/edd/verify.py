r"""Exhaustive verification: resolution counts and Conjecture 1.

Three independent checks are provided.

``brute_force_resolutions(n)``
    Counts *every* resolution of ``P_n`` (even ``n >= 4``) by backtracking over snakes,
    pruning with the *proved* necessary condition that the ``n/2`` ear pairs partition the
    vertex set.  This is an implementation-independent cross-check of the classification
    and is feasible up to ``n = 10`` (about a second).

``count_resolutions(n)``
    The number of antipodal resolutions of ``P_n``, i.e. ``2^(n/2-2)`` (Theorem 3).  This
    equals the total number of resolutions whenever Conjecture 1 has been verified for
    ``n``; :func:`verify_completeness` does that verification.

``verify_completeness(n)``
    Conjecture 1 states that every resolution of ``P_{2m}`` is antipodal (all ``m`` snakes
    have their ears ``m`` apart).  It is verified by checking, for every snake of ``P_n``
    with non-antipodal ears, whether that snake extends to a resolution.  The extension
    question is a set-partitioning integer program (``sum_{T contains d} y_T = 1`` for each
    remaining diagonal) solved by HiGHS; positive answers are validated independently by
    extracting and re-checking the witness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from .polygon import diagonals, diagonal_index, ear_vertices, is_snake
from .snakes import antipodal_words, snakes as all_snakes

__all__ = [
    "ResolutionReport",
    "brute_force_resolutions",
    "brute_force_count_resolutions",
    "count_resolutions",
    "extends_to_resolution",
    "verify_completeness",
    "is_antipodal",
]


def is_antipodal(family, n: int) -> bool:
    r"""True iff every snake of ``family`` has its two ears at cyclic distance ``n/2``."""
    m = n // 2
    for T in family:
        ev = ear_vertices(T, n)
        if len(ev) != 2 or (ev[1] - ev[0]) % n != m:
            return False
    return True


def _validate_resolution(family, n: int) -> bool:
    D = set(diagonals(n))
    seen: set = set()
    for T in family:
        if len(T) != n - 3 or not is_snake(T, n):
            return False
        if seen & set(T):
            return False
        seen |= set(T)
    return seen == D


def brute_force_resolutions(n: int, limit: int | None = None) -> list[tuple[frozenset, ...]]:
    """Every resolution of ``P_n`` (even ``n >= 4``) as unordered families of snakes.

    Exhaustive: candidates are the ``n * 2^(n-5)`` snakes of ``P_n``; the search prunes with
    the proved necessary condition that the ear pairs partition the vertex set.  Only
    practical up to ``n = 10``.
    """
    if n < 4 or n % 2 != 0:
        raise ValueError("resolutions are defined for even n >= 4 only")
    m = n // 2
    didx = diagonal_index(n)
    masks = {T: sum(1 << didx[d] for d in T) for T in all_snakes(n)}
    earpairs = {T: frozenset(ear_vertices(T, n)) for T in masks}
    items = sorted(masks.items(), key=lambda kv: (-bin(kv[1]).count("1"), sorted(kv[0])))
    out: list[tuple[frozenset, ...]] = []

    def rec(start: int, used: int, used_ears: frozenset, chosen: list) -> None:
        if limit is not None and len(out) >= limit:
            return
        if len(chosen) == m:
            out.append(tuple(chosen))
            return
        for oi in range(start, len(items)):
            T, mask = items[oi]
            ep = earpairs[T]
            if ep & used_ears or mask & used:
                continue
            rec(oi + 1, used | mask, used_ears | ep, chosen + [T])

    rec(0, 0, frozenset(), [])
    return out


@lru_cache(maxsize=None)
def brute_force_count_resolutions(n: int) -> int:
    """Number of resolutions of ``P_n`` found by exhaustive search (feasible up to ``n=10``)."""
    return len(brute_force_resolutions(n))


def count_resolutions(n: int) -> int:
    r"""Number of *antipodal* resolutions of ``P_n``: ``2^(n/2-2)`` for even ``n >= 4``.

    This equals the total number of resolutions of ``P_n`` as soon as Conjecture 1
    ("every resolution is antipodal") has been verified for that ``n``; see
    :func:`verify_completeness`.  The equality is also checked directly against exhaustive
    search for ``n <= 10`` in the test suite.
    """
    if n < 4 or n % 2 != 0:
        raise ValueError("resolutions are defined for even n >= 4 only")
    return len(antipodal_words(n))


@dataclass
class ResolutionReport:
    """Structured result of :func:`verify_completeness`."""

    n: int
    m: int
    num_snakes: int
    num_non_antipodal_snakes: int
    num_extensions_found: int = 0
    witnesses: list = field(default_factory=list)
    antipodal_resolutions: int = 0
    brute_force_checked: bool = False
    brute_force_count: int = -1

    @property
    def conjecture_holds(self) -> bool:
        """True iff no snake with non-antipodal ears extends to a resolution of ``P_n``."""
        return self.num_extensions_found == 0

    @property
    def total_resolutions(self) -> int:
        """Total number of resolutions, given the conjecture holds for this ``n``."""
        if not self.conjecture_holds:
            raise ValueError("a non-antipodal resolution was found; the count is larger")
        return self.antipodal_resolutions

    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "m": self.m,
            "num_snakes": self.num_snakes,
            "num_non_antipodal_snakes": self.num_non_antipodal_snakes,
            "num_extensions_found": self.num_extensions_found,
            "antipodal_resolutions": self.antipodal_resolutions,
            "total_resolutions": (
                self.antipodal_resolutions if self.conjecture_holds else None
            ),
            "brute_force_checked": self.brute_force_checked,
            "brute_force_count": self.brute_force_count,
            "conjecture_holds": self.conjecture_holds,
            "witnesses": [sorted(sorted(T) for T in w) for w in self.witnesses],
        }


def extends_to_resolution(T: frozenset, n: int) -> tuple[bool, list]:
    r"""Can the snake ``T`` be completed to a resolution of ``P_n``?

    Returns ``(feasible, witness)``, where ``witness`` is the complementary family of
    ``n/2 - 1`` snakes, independently re-validated to be edge-disjoint from ``T`` and from
    each other and to cover the remaining diagonals.
    """
    if n % 2 != 0 or n < 4:
        raise ValueError("resolutions are defined for even n >= 4 only")
    m = n // 2
    if not is_snake(T, n):
        raise ValueError("T is not a snake of P_n")
    Tset = set(T)
    candidates = [S for S in all_snakes(n) if S != T and not (S & Tset)]
    remaining = [d for d in diagonals(n) if d not in Tset]
    ridx = {d: k for k, d in enumerate(remaining)}
    rows, cols = [], []
    for t, S in enumerate(candidates):
        for d in S:
            k = ridx.get(d)
            if k is not None:
                rows.append(k)
                cols.append(t)
    A = coo_matrix(
        (np.ones(len(rows)), (rows, cols)), shape=(len(remaining), len(candidates)), dtype=float
    )
    cons = LinearConstraint(A.tocsr(), np.ones(len(remaining)), np.ones(len(remaining)))
    res = milp(
        c=-np.ones(len(candidates)),
        constraints=[cons],
        integrality=np.ones(len(candidates)),
        bounds=Bounds(0, 1),
    )
    if res.status != 0 or not res.success:
        return False, []
    k = int(round(-res.fun))
    if k != m - 1:
        return False, []
    x = np.rint(np.asarray(res.x)).astype(bool)
    witness = [S for S, xi in zip(candidates, x) if xi]
    if not _validate_resolution([frozenset(T), *map(frozenset, witness)], n):
        raise AssertionError("ILP witness failed independent validation")
    return True, witness


def verify_completeness(n: int, brute_force: bool = False) -> ResolutionReport:
    r"""Verify Conjecture 1 ("every resolution of ``P_{2m}`` is antipodal") for ``P_n``.

    For every snake of ``P_n`` whose ear pair is not antipodal we ask whether the snake
    extends to a resolution (an exact-cover ILP).  If none does, every resolution of
    ``P_n`` is antipodal and hence, by Theorem 3, there are exactly ``2^(m-2)`` of them.
    Set ``brute_force=True`` to additionally cross-check the count by exhaustive search
    (only feasible for ``n <= 10``).
    """
    m = n // 2
    if n < 6 or n % 2 != 0:
        raise ValueError("Conjecture 1 concerns even n >= 6")
    snake_list = all_snakes(n)
    report = ResolutionReport(
        n=n,
        m=m,
        num_snakes=len(snake_list),
        num_non_antipodal_snakes=0,
        antipodal_resolutions=count_resolutions(n),
    )
    for T in snake_list:
        ev = ear_vertices(T, n)
        if len(ev) == 2 and (ev[1] - ev[0]) % n == m:
            continue
        report.num_non_antipodal_snakes += 1
        ok, witness = extends_to_resolution(frozenset(T), n)
        if ok:
            report.num_extensions_found += 1
            report.witnesses.append([frozenset(T), *map(frozenset, witness)])
    if brute_force:
        report.brute_force_checked = True
        report.brute_force_count = brute_force_count_resolutions(n)
    return report