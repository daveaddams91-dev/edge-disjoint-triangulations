"""Tests for :mod:`edd.dissections` (enumerators) cross-validated against brute force."""

from __future__ import annotations

from itertools import combinations

import pytest

import edd
from edd.polygon import cells, diagonals, is_non_crossing

N_SMALL = range(3, 11)


@pytest.mark.parametrize("n", N_SMALL)
def test_triangulations_are_catalan(n: int) -> None:
    T = edd.triangulations(n)
    assert len(T) == edd.num_triangulations(n)
    assert len(set(T)) == len(T)
    for t in T:
        assert len(t) == n - 3
        assert is_non_crossing(t, n)
        assert t <= set(diagonals(n))


@pytest.mark.parametrize("n", range(4, 11))
def test_dissections_counts_are_little_schroeder(n: int) -> None:
    # number of dissections of P_n is the little Schroeder number s_{n-2}:
    # 1, 1, 3, 11, 45, 197, 903, 4279 for n = 3, 4, 5, 6, 7, 8, 9, 10
    expected = {4: 3, 5: 11, 6: 45, 7: 197, 8: 903, 9: 4279, 10: 20793}
    if n in expected:
        assert len(edd.dissections(n)) == expected[n]


@pytest.mark.parametrize("p", (3, 4, 5, 6))
def test_p_angulation_counts_match_brute_force(p: int) -> None:
    n_max = 8 if p >= 4 else 9
    for n in range(p, n_max + 1):
        if (n - 2) % (p - 2) != 0:
            assert edd.p_angulations(n, p) == ()
            continue
        want = edd.p_angulation_diagonals(n, p)
        assert want == (n - p) // (p - 2)
        brute = 0
        for combo in combinations(diagonals(n), want):
            if not is_non_crossing(combo, n):
                continue
            cs = cells(frozenset(combo), n)
            if len(cs) == (n - 2) // (p - 2) and all(len(c) == p for c in cs):
                brute += 1
        assert len(edd.p_angulations(n, p)) == brute


def test_quadrangulation_counts() -> None:
    # number of quadrangulations of P_{2k}: 1, 3, 12, 55, 273 for k = 1..5
    for n, k in ((4, 1), (6, 3), (8, 12), (10, 55), (12, 273)):
        assert len(edd.p_angulations(n, 4)) == k


def test_p_angulation_cells_all_have_p_sides() -> None:
    for p in (3, 4, 5):
        for n in range(p, 10):
            for A in edd.p_angulations(n, p):
                cs = cells(A, n)
                assert len(cs) == (n - 2) // (p - 2)
                assert all(len(c) == p for c in cs)