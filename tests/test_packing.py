r"""Tests for :mod:`edd.packing`: the packing number and its witnesses."""

from __future__ import annotations

import pytest

import edd
from edd.polygon import diagonals, triangles

N = range(4, 15)


@pytest.mark.parametrize("n", N)
def test_witness_attains_the_bound(n: int) -> None:
    W = edd.packing_witness(n)
    assert len(W) == n // 2 == edd.packing_upper_bound(n)
    assert edd.is_edge_disjoint_family(W)
    tri = set(edd.triangulations(n))
    for T in W:
        assert T in tri
        assert len(T) == n - 3


@pytest.mark.parametrize("n", (4, 5, 6, 7))
def test_odd_and_even_witnesses_are_distinct_constructions(n: int) -> None:
    W = edd.packing_witness(n)
    if n % 2 == 0:
        assert W == edd.even_packing(n)
        assert edd.canonical_word(n) in edd.antipodal_words(n)
    else:
        assert W == edd.odd_packing(n)
        # each member of an odd witness has at most 2 ears, as any triangulation does
        for T in W:
            assert 2 <= len(edd.ear_vertices(T, n)) <= n - 2


@pytest.mark.parametrize("n", (6, 8, 10, 12))
def test_even_packing_is_a_resolution(n: int) -> None:
    res = edd.even_packing(n)
    assert edd.is_resolution_family(res, n)


@pytest.mark.parametrize("n", range(6, 13))
def test_ilp_agrees_with_the_theorem(n: int) -> None:
    assert edd.packing_ilp(n) == n // 2


@pytest.mark.parametrize("n", (6, 8, 10))
def test_certificate(n: int) -> None:
    cert = edd.ilp_certificate(n, edd.packing_witness(n))
    assert cert["primal"] == n // 2
    assert cert["dual"] == n / 2
    assert cert["optimal"]
    assert cert["min_ears_over_all_triangulations"] >= 2


@pytest.mark.parametrize("n", (5, 6, 7, 8))
def test_k_dissection_counts(n: int) -> None:
    counts = edd.count_all_packs(n)
    assert counts[0] == 1
    assert counts[1] == edd.num_triangulations(n)
    assert counts[n // 2] > 0
    # monotone in k up to the maximum and zero beyond it
    assert edd.count_k_dissections(n, n // 2 + 1) == 0


@pytest.mark.parametrize("n", (5, 6, 7, 8, 9))
def test_k_dissection_counts_symmetry(n: int) -> None:
    r"""Double count: ``sum_T #{k-dissolutions containing T} = k * N_k``.

    This is an independent check of the backtracking counter.
    """
    from edd.polygon import diagonal_index

    Ts = edd.triangulations(n)
    didx = diagonal_index(n)
    masks = [sum(1 << didx[d] for d in T) for T in Ts]
    for k in (2, min(3, n // 2)):
        total = 0
        for t in range(len(Ts)):
            sub = _count_containing(n, k, masks, t)
            total += sub
        assert total == k * edd.count_k_dissections(n, k)


def _count_containing(n: int, k: int, masks, fixed: int) -> int:
    count = 0

    def rec(start: int, used: int, depth: int) -> None:
        nonlocal count
        if depth == k:
            count += 1
            return
        for i in range(start, len(masks)):
            if masks[i] & used:
                continue
            rec(i + 1, used | masks[i], depth + 1)

    rec(0, masks[fixed], 1)
    return count