r"""Snakes of a convex polygon and their encoding by lattice paths / words.

Definitions
-----------
A *snake* is a triangulation of the convex ``n``-gon with no interior triangle
(equivalently: every triangle has a side of the polygon as an edge; equivalently the dual
graph is a path).  For ``n >= 5`` a snake has exactly two *ears*, and we call their
vertices the two *endpoints* of the snake.

The path correspondence
-----------------------
Fix the labelling ``0, 1, ..., n-1`` (cyclic).  Let ``u`` be one endpoint of a snake and
``v`` its other endpoint.  Reading the strip of triangles of the snake from the ear at
``u`` towards the ear at ``v``, one triangle at a time, each triangle absorbs exactly one
new polygon side; a side is absorbed either at the counterclockwise end of the consumed arc
(a move ``L``) or at the clockwise end (a move ``R``).  Since the two end triangles -- the
ears -- each absorb two sides, there are exactly ``n - 4`` moves.

Let ``L_i`` (resp. ``R_i``) be the number of ``L``-moves (resp. ``R``-moves) among the first
``i`` moves, so ``L_i + R_i = i``.  The ``i``-th diagonal met by the strip is

.. math::  F_i \;=\; \{\, u - 1 - L_i,\; u + 1 + R_i \,\} \pmod n, \qquad i = 0,1,\dots,n-4,

with ``F_0 = (u-1, u+1)`` and ``F_{n-4} = (v-1, v+1)`` the short diagonals at the endpoints.
Three consequences are used throughout:

1. the endpoints satisfy ``v = u + R_{n-4} + 2 = u + #R(word) + 2`` (mod ``n``), and the
   snake uses ``#R(word)`` right moves and ``n - 4 - #R(word)`` left moves;
2. the ``i``-th diagonal of the strip has cyclic distance ``min(i+2, n-i-2)`` --
   *independent of the word*.  Hence every snake contains exactly two diagonals of each
   level ``j < n/2`` and exactly one diagonal of level ``n/2`` (a diameter);
3. snakes with prescribed endpoints correspond bijectively to words in ``{L, R}`` of length
   ``n-4`` with the prescribed number of ``R``'s; there are ``binom(n-4, #R)`` of them.
"""

from __future__ import annotations

from functools import lru_cache

from .polygon import Diagonal, Triangulation, diagonals, is_snake

__all__ = [
    "L",
    "R",
    "snakes",
    "num_snakes",
    "snake_from_word",
    "word_from_snake",
    "strip_level",
    "antipodal_words",
    "antipodal_resolution",
    "is_resolution_family",
]

L = "L"
R = "R"


@lru_cache(maxsize=None)
def snakes(n: int) -> tuple[Triangulation, ...]:
    """All snakes of the convex ``n``-gon, as frozensets of diagonals.

    Their number is ``n * 2^(n-5)`` for ``n >= 5``, and ``2`` for ``n = 4``.
    """
    from .dissections import triangulations

    return tuple(T for T in triangulations(n) if is_snake(T, n))


@lru_cache(maxsize=None)
def num_snakes(n: int) -> int:
    """``n * 2^(n-5)`` for ``n >= 5``, else the number of triangulations of ``P_n``."""
    from .dissections import num_triangulations

    return n * 2 ** (n - 5) if n >= 5 else num_triangulations(n)


def strip_level(word: str, i: int) -> int:
    """Cyclic distance of the ``i``-th diagonal of a strip following ``word``.

    Equals ``min(i+2, n-i-2)`` with ``n = len(word) + 4`` and does not depend on ``word``.
    """
    n = len(word) + 4
    if not 0 <= i <= n - 4:
        raise ValueError(f"i must lie in 0 .. {n - 4}")
    return min(i + 2, n - i - 2)


def snake_from_word(word: str, u: int, n: int) -> Triangulation:
    r"""The snake of ``P_n`` whose strip, read from endpoint ``u``, follows ``word``.

    ``word`` is a string over ``{L, R}`` of length ``n - 4``; the snake has one endpoint
    at ``u`` and the other at ``u + #R(word) + 2`` (mod ``n``).
    """
    if len(word) != n - 4 or any(c not in (L, R) for c in word):
        raise ValueError(f"word must be a string of length {n - 4} over {{L, R}}")
    D = set(diagonals(n))
    Lset = {i + 1 for i, c in enumerate(word) if c == L}
    out: set[frozenset[int]] = set()
    li = 0
    for i in range(n - 3):
        if i in Lset:
            li += 1
        out.add(frozenset(((u - 1 - li) % n, (u + 1 + (i - li)) % n)))
    T = frozenset(tuple(sorted(d)) for d in out if tuple(sorted(d)) in D)
    if len(T) != n - 3 or not is_snake(T, n):
        raise AssertionError(f"word {word!r} at u={u} does not produce a snake of P_{n}")
    return T


def word_from_snake(T: Triangulation, u: int, n: int) -> str:
    r"""The word of the snake ``T`` read from endpoint ``u``; inverse of :func:`snake_from_word`.

    Raises ``ValueError`` if ``T`` is not a snake or if ``u`` is not an endpoint of ``T``.
    """
    S = set(T)
    short = {v for v in range(n) if tuple(sorted(((v - 1) % n, (v + 1) % n))) in S}
    if u not in short or not is_snake(T, n):
        raise ValueError(f"u={u} is not an endpoint of the given snake of P_{n}")
    letters: list[str] = []
    li = 0
    for i in range(1, n - 3):
        cand = frozenset(((u - 2 - li) % n, (u + 1 + (i - 1 - li)) % n))
        if cand in S:
            letters.append(L)
            li += 1
        else:
            letters.append(R)
    word = "".join(letters)
    if snake_from_word(word, u, n) != T:
        raise ValueError("given set is not a snake of P_{} (or the endpoints are swapped)".format(n))
    return word


@lru_cache(maxsize=None)
def antipodal_words(n: int) -> tuple[str, ...]:
    r"""Words ``w in {L,R}^(n-4)`` with ``w[i-1] != w[n-2-i]`` for all ``1 <= i <= n/2 - 2``.

    For ``n = 2m`` these are exactly the words whose ``m`` antipodal snakes partition all
    diagonals of ``P_n``.  There are ``2^(m-2)`` of them: each is determined freely by its
    first ``m-2`` letters.
    """
    if n < 4 or n % 2 != 0:
        raise ValueError("antipodal words are defined for even n >= 4 only")
    m = n // 2
    ln = n - 4
    head_len = max(m - 2, 0)
    out: list[str] = []
    for mask in range(1 << head_len):
        head = "".join(R if (mask >> k) & 1 else L for k in range(head_len))
        letters: list[str | None] = list(head) + [None] * (ln - head_len)
        for k in range(head_len):
            letters[ln - 1 - k] = R if letters[k] == L else L
        if any(c is None for c in letters):
            raise AssertionError("antipodal word construction failed")
        out.append("".join(letters))  # type: ignore[arg-type]
    return tuple(sorted(out))


def antipodal_resolution(n: int, word: str) -> tuple[Triangulation, ...]:
    r"""The resolution of ``P_n`` (even ``n >= 4``) determined by an antipodal word.

    The ``m = n/2`` snakes are indexed by ``u = 0, 1, ..., m-1``, each read from endpoint
    ``u``; every snake has endpoints ``u`` and ``u + m``, and the ``m`` snakes partition all
    diagonals of ``P_n``.
    """
    return tuple(snake_from_word(word, u, n) for u in range(n // 2))


def is_resolution_family(family, n: int) -> bool:
    r"""True iff ``family`` consists of ``n/2`` edge-disjoint snakes covering all diagonals."""
    m = n // 2
    if len(family) != m:
        return False
    seen: set[Diagonal] = set()
    for T in family:
        if len(T) != n - 3 or not is_snake(T, n):
            return False
        if seen & set(T):
            return False
        seen |= set(T)
    return seen == set(diagonals(n))