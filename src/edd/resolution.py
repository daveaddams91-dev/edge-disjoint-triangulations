r"""Resolutions of convex polygons: structure, classification, and counting.

Definitions
-----------
Let ``P_{2m}`` be a convex ``2m``-gon.  The set of its diagonals has cardinality
``m(2m-3)``, and every triangulation uses ``2m-3`` of them.  A *resolution* of ``P_{2m}``
is a family of ``m`` pairwise edge-disjoint snakes whose union is the set of all
diagonals.  Equivalently it is a partition of the diagonals into ``m`` snakes.

Why this is the right object
----------------------------
Any family of ``m`` edge-disjoint triangulations of ``P_{2m}`` uses ``m(2m-3)``
diagonals, i.e. all of them; and since every triangulation uses at least two of the ``2m``
short diagonals, each of the ``m`` triangulations uses exactly two short diagonals and no
triangulation has more than two ears.  So *every* extremal family for even ``n`` is a
resolution, and every resolution consists of snakes.

The antipodal family
--------------------
A snake is *antipodal* if its two endpoints are at cyclic distance ``m``.  The resolution
built from an antipodal word (see :func:`edd.snakes.antipodal_words`) has ``m`` antipodal
snakes, one for each pair ``{u, u+m}``, and these pairs are forced by the fact that the
``2m`` short diagonals are partitioned two per snake.  Theorem :data:`CLASSIFICATION` says
that the words producing a resolution are exactly the antipodal ones, of which there are
``2^{m-2}``.

:data:`COMPLETENESS_OPEN` records what is *not* proved here: that no resolution with
non-antipodal ears exists for any ``m``.  That statement is verified exhaustively for
``m <= 8`` by :mod:`edd.verify` and is stated as Conjecture 1 of the paper.
"""

from __future__ import annotations

from functools import lru_cache

from .polygon import Diagonal, Triangulation, diagonals, is_snake, short_diagonals
from .snakes import antipodal_resolution, antipodal_words, snake_from_word, word_from_snake

__all__ = [
    "Resolution",
    "resolution_from_word",
    "antipodal_resolutions",
    "num_antipodal_resolutions",
    "resolution_from_families",
    "family_word",
    "ear_matching",
    "is_antipodal_family",
    "strip_diagonals",
    "diagonal_starts",
    "level_condition",
    "level_condition_holds",
    "CLASSIFICATION",
    "COMPLETENESS_OPEN",
]

#: The proved classification statement (see the module docstring).
CLASSIFICATION = (
    "For n = 2m >= 6 and any word w in {L,R}^(n-4): the m antipodal snakes "
    "T_u = snake_from_word(w, u, n), u = 0..m-1, form a resolution of P_n if and only if "
    "w[i-1] != w[n-2-i] for every 1 <= i <= m-2.  Consequently there are exactly "
    "2^(m-2) such (antipodal) resolutions."
)

#: What remains open (Conjecture 1 of the paper).
COMPLETENESS_OPEN = (
    "Every resolution of P_{2m} is antipodal (all m snakes have their two ears at "
    "antipodal vertices).  Verified exhaustively for m <= 8; open in general."
)


class Resolution(tuple):
    """A family of ``n/2`` snakes of ``P_n`` (even ``n >= 4``) that partitions the diagonals.

    Behaves as an ordinary tuple of frozensets of diagonals; additionally exposes the
    word that generated it (when it was obtained from :func:`resolution_from_word`).
    """

    word: str | None = None

    def __new__(cls, family, word: str | None = None):
        obj = super().__new__(cls, family)
        obj.word = word
        return obj

    @property
    def n(self) -> int:
        """Number of vertices of the polygon (twice the number of snakes)."""
        return 2 * len(self)

    def ears(self) -> tuple[tuple[int, ...], ...]:
        """The sorted pair of ear vertices of each snake, in the order of the snakes."""
        from .polygon import ear_vertices

        return tuple(ear_vertices(T, self.n) for T in self)

    def diameters(self) -> tuple[Diagonal, ...]:
        """The ``n/2`` diagonals of maximum level (the diameters) and which snake owns each."""
        from .polygon import diagonal_level

        return tuple(d for T in self for d in sorted(T) if diagonal_level(d, self.n) == self.n // 2)


def resolution_from_word(word: str, n: int) -> Resolution:
    """The family of ``n/2`` snakes read from endpoints ``0..n/2-1`` following ``word``."""
    return Resolution(antipodal_resolution(n, word), word)


def antipodal_resolutions(n: int) -> tuple[Resolution, ...]:
    """All antipodal resolutions of ``P_n`` (even ``n >= 4``), one per antipodal word."""
    return tuple(resolution_from_word(w, n) for w in antipodal_words(n))


@lru_cache(maxsize=None)
def num_antipodal_resolutions(n: int) -> int:
    """``2^(n/2-2)`` for even ``n >= 4``: the number of antipodal resolutions of ``P_n``."""
    if n < 4 or n % 2 != 0:
        raise ValueError("resolutions are defined for even n >= 4")
    return 2 ** (n // 2 - 2)


def resolution_from_families(family) -> Resolution | None:
    """Wrap ``family`` as a :class:`Resolution` if it really is one, else return ``None``."""
    fam = tuple(tuple(sorted(T)) for T in family)
    fam = tuple(frozenset(T) for T in fam)
    n = 2 * len(fam)
    if not _is_resolution(fam, n):
        return None
    return Resolution(fam)


def _is_resolution(fam, n: int) -> bool:
    seen: set[Diagonal] = set()
    for T in fam:
        if len(T) != n - 3 or not is_snake(T, n):
            return False
        if seen & set(T):
            return False
        seen |= set(T)
    return seen == set(diagonals(n))


def family_word(family) -> str | None:
    """The common word of a resolution, if the ``n/2`` snakes share one.

    Returns ``None`` if the family is not a resolution, or if the snakes do not share a
    single word (this is the situation ruled out only conjecturally, see
    :data:`COMPLETENESS_OPEN`).
    """
    fam = tuple(frozenset(T) for T in family)
    n = 2 * len(fam)
    if not _is_resolution(fam, n):
        return None
    words = set()
    for u in range(n // 2):
        found = None
        for T in fam:
            try:
                found = word_from_snake(T, u, n)
                break
            except ValueError:
                continue
        if found is None:
            return None
        words.add(found)
    return words.pop() if len(words) == 1 else None


def ear_matching(family) -> tuple[frozenset[int], ...]:
    """The ear pairs of a resolution, as a family of 2-element sets of vertices."""
    from .polygon import ear_vertices

    n = 2 * len(family)
    return tuple(frozenset(ear_vertices(T, n)) for T in family)


def is_antipodal_family(family, n: int) -> bool:
    r"""True iff each snake of ``family`` has its two ears at cyclic distance ``n/2``."""
    from .polygon import ear_vertices

    m = n // 2
    for T in family:
        ev = ear_vertices(T, n)
        if len(ev) != 2:
            return False
        if (ev[1] - ev[0]) % n != m:
            return False
    return True


def strip_diagonals(word: str, u: int, n: int) -> tuple[Diagonal, ...]:
    r"""The ``n-3`` diagonals of the strip of ``snake_from_word(word, u, n)``, in strip order.

    Position ``i`` of the returned tuple is ``F_i = {u-1-L_i, u+1+R_i}`` and has cyclic
    distance ``min(i+2, n-i-2)`` independently of ``word``.
    """
    from .polygon import diagonals as _diags

    D = set(_diags(n))
    Lset = {i + 1 for i, c in enumerate(word) if c == "L"}
    out: list[Diagonal] = []
    li = 0
    for i in range(n - 3):
        if i in Lset:
            li += 1
        d = tuple(sorted(((u - 1 - li) % n, (u + 1 + (i - li)) % n)))
        if d not in D:
            raise AssertionError(f"word {word!r} at u={u} produced a non-diagonal {d}")
        out.append(d)
    return tuple(out)


def diagonal_starts(res: Resolution, i: int) -> tuple[tuple[Diagonal, ...], tuple[Diagonal, ...]]:
    r"""The strip diagonals at positions ``i`` and ``2m-4-i`` of every snake of ``res``.

    ``i`` must satisfy ``0 <= i <= m-2``.  All ``2m`` returned diagonals have cyclic
    distance ``min(i+2, 2m-i-2)``; the covering condition at level ``i`` (see
    :func:`level_condition_holds`) says that these are exactly the ``2m`` diagonals of that
    distance, each appearing once.
    """
    m = res.n // 2
    if not 0 <= i <= m - 2:
        raise ValueError(f"i must lie in 0 .. {m - 2}")
    assert res.word is not None, "resolution must carry its word"
    left: list[Diagonal] = []
    right: list[Diagonal] = []
    for u in range(m):
        strip = strip_diagonals(res.word, u, res.n)
        left.append(strip[i])
        right.append(strip[2 * m - 4 - i])
    return tuple(left), tuple(right)


def level_condition(res: Resolution, i: int) -> bool:
    r"""Directly check the level-``i`` condition for a word-generated resolution.

    For ``i < m-2`` this says that the ``2m`` strip diagonals at positions ``i`` and
    ``2m-4-i`` are pairwise distinct; for ``i = m-2`` the two positions coincide and the
    condition says that the ``m`` strip diagonals there are the ``m`` diameters of ``P_n``
    (pairwise distinct modulo ``m``).
    """
    m = res.n // 2
    left, right = diagonal_starts(res, i)
    if i == m - 2:
        return len({d[0] % m for d in left}) == m
    return len(set(left) | set(right)) == 2 * m


def level_condition_holds(word: str, n: int) -> bool:
    r"""The covering condition of Theorem 2 in closed form.

    ``True`` iff ``w[j-1] != w[n-2-j]`` for all ``1 <= j <= n/2 - 2``, i.e. iff ``word``
    is an antipodal word.
    """
    m = n // 2
    if m < 3:
        return True
    return all(word[j - 1] != word[n - 4 - j] for j in range(1, m - 1))