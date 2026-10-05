r"""Tests for the resolution classification (Theorems 2 and 3) and Conjecture 1."""

from __future__ import annotations

import pytest

import edd
from edd.polygon import diagonals, ear_vertices, is_snake

EVEN = (4, 6, 8, 10, 12, 14)


@pytest.mark.parametrize("n", EVEN)
def test_antipodal_words_count_and_property(n: int) -> None:
    words = edd.antipodal_words(n)
    assert len(words) == 2 ** (n // 2 - 2)
    assert len(set(words)) == len(words)
    for w in words:
        assert len(w) == n - 4
        assert set(w) <= {"L", "R"}
        assert w.count("L") == n // 2 - 2
        assert edd.level_condition_holds(w, n)


@pytest.mark.parametrize("n", EVEN)
def test_antipodal_resolutions_are_resolutions(n: int) -> None:
    for res in edd.antipodal_resolutions(n):
        assert len(res) == n // 2
        assert res.word in edd.antipodal_words(n)
        seen: set = set()
        for T in res:
            assert is_snake(T, n)
            assert len(T) == n - 3
            assert not seen & set(T)
            seen |= set(T)
        assert seen == set(diagonals(n))
        # all snakes are antipodal
        for T in res:
            ev = ear_vertices(T, n)
            assert len(ev) == 2 and (ev[1] - ev[0]) % n == n // 2


@pytest.mark.parametrize("n", EVEN)
def test_antipodal_resolutions_are_pairwise_distinct(n: int) -> None:
    sigs = set()
    for res in edd.antipodal_resolutions(n):
        sigs.add(frozenset(res))
    assert len(sigs) == len(edd.antipodal_resolutions(n))


@pytest.mark.parametrize("n", (6, 8, 10))
def test_level_condition_directly(n: int) -> None:
    """The covering condition of Theorem 2, checked both directly and in closed form."""
    from itertools import product

    m = n // 2
    for w in ("".join(p) for p in product("LR", repeat=n - 4)):
            res = edd.resolution_from_word(w, n)
            direct = all(edd.level_condition(res, i) for i in range(m - 1))
            assert direct == edd.level_condition_holds(w, n)


@pytest.mark.parametrize("n", (6, 8, 10))
def test_nonantipodal_words_do_not_give_resolutions(n: int) -> None:
    from itertools import product

    bad = 0
    for w in ("".join(p) for p in product("LR", repeat=n - 4)):
            if edd.level_condition_holds(w, n):
                continue
            res = edd.resolution_from_word(w, n)
            assert not edd.is_resolution_family(res, n)
            bad += 1
    assert bad > 0


@pytest.mark.parametrize("n", (4, 6, 8, 10))
def test_brute_force_agrees_with_the_classification(n: int) -> None:
    """Exhaustive search over *all* families of snakes finds exactly ``2^(m-2)``."""
    brute = edd.brute_force_count_resolutions(n)
    assert brute == edd.count_resolutions(n) == 2 ** (n // 2 - 2)


@pytest.mark.parametrize("n", (6, 8, 10))
def test_conjecture_1_verified(n: int) -> None:
    report = edd.verify_completeness(n, brute_force=True)
    assert report.conjecture_holds
    assert report.num_extensions_found == 0
    assert report.brute_force_checked
    assert report.brute_force_count == report.antipodal_resolutions
    assert report.total_resolutions == 2 ** (n // 2 - 2)


def test_resolution_rejects_non_resolutions() -> None:
    n = 8
    # a fan at 0 is a snake (no interior triangle) but has non-antipodal ears, so it cannot
    # be a member of a resolution
    fan = frozenset((0, j) for j in range(2, n - 1))
    assert is_snake(fan, n)
    assert (edd.ear_vertices(fan, n)[1] - edd.ear_vertices(fan, n)[0]) % n != n // 2
    assert not edd.is_antipodal_family([fan], n)
    # two copies of the same snake are not edge-disjoint
    T = edd.snake_from_word("RLRL", 0, n)
    assert not edd.is_resolution_family([T, T], n)
    # a family of the right size but not covering all diagonals is not a resolution
    fam = [edd.snake_from_word("RLRL", u, n) for u in range(n // 2 - 1)] + [fan]
    assert len(fam) == n // 2
    assert not edd.is_resolution_family(fam, n)


def test_strip_diagonals_reconstruct_the_snake() -> None:
    n = 12
    for w in edd.antipodal_words(n):
        for u in range(n // 2):
            strip = edd.strip_diagonals(w, u, n)
            assert frozenset(strip) == edd.snake_from_word(w, u, n)


def test_family_word_and_ear_matching() -> None:
    n = 10
    res = edd.antipodal_resolutions(n)[0]
    assert edd.family_word(res) == res.word
    pairs = edd.ear_matching(res)
    assert sorted(x for p in pairs for x in p) == list(range(n))
    assert edd.is_antipodal_family(res, n)