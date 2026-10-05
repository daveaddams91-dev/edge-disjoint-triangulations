"""Tests for :mod:`edd.polygon`: combinatorics of diagonals, cells, ears and snakes."""

from __future__ import annotations

import pytest

import edd
from edd.polygon import (
    cells,
    crosses,
    cyclic_dist,
    delete_vertex,
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

N_SMALL = range(3, 11)


@pytest.mark.parametrize("n", N_SMALL)
def test_counts_of_sides_and_diagonals(n: int) -> None:
    assert len(sides(n)) == n
    assert len(diagonals(n)) == n * (n - 3) // 2
    assert not set(sides(n)) & set(diagonals(n))
    for d in diagonals(n):
        assert 0 <= d[0] < d[1] <= n - 1
        assert diagonal_level(d, n) >= 2


@pytest.mark.parametrize("n", range(4, 12))
def test_short_diagonals_are_n_and_cut_off_one_vertex(n: int) -> None:
    S = short_diagonals(n)
    assert len(S) == n
    assert all(diagonal_level(d, n) == 2 for d in S)
    for v in range(n):
        assert tuple(sorted(((v - 1) % n, (v + 1) % n))) in S


@pytest.mark.parametrize("n", N_SMALL)
def test_crossing_is_symmetric_and_matches_interleaving(n: int) -> None:
    D = diagonals(n)
    for a in D:
        for b in D:
            assert crosses(a, b, n) == crosses(b, a, n)
            assert not crosses(a, a, n)
            # manual interleaving check
            if len({a[0], a[1], b[0], b[1]}) < 4:
                continue
            a0, a1, b0, b1 = a[0], a[1], b[0], b[1]
            expect = (a0 < b0 < a1 < b1) or (b0 < a0 < b1 < a1)
            assert crosses(a, b, n) == expect


def test_cyclic_dist_and_levels() -> None:
    assert cyclic_dist(0, 2, 6) == 2
    assert cyclic_dist(0, 3, 6) == 3
    assert cyclic_dist(5, 1, 6) == 2
    assert [diagonal_level(d, 8) for d in diagonals(8)][:4] == [2, 3, 4, 3]


@pytest.mark.parametrize("n", range(4, 10))
def test_triangles_of_a_triangulation(n: int) -> None:
    for T in edd.triangulations(n):
        tris = triangles(T, n)
        assert len(tris) == n - 2
        assert all(len(t) == 3 for t in tris)
        # the cells function agrees with the triangle walker
        assert {frozenset(c) for c in cells(T, n)} == set(tris)
        # interior edge count
        edges = set()
        for a, b, c in tris:
            edges |= {tuple(sorted((a, b))), tuple(sorted((a, c))), tuple(sorted((b, c)))}
        assert edges == set(sides(n)) | set(T)


@pytest.mark.parametrize("n", range(4, 10))
def test_cells_of_dissections_are_valid(n: int) -> None:
    for D in edd.dissections(n):
        cs = cells(D, n)
        assert sum(len(c) for c in cs) == 2 * len(D) + n
        assert all(len(c) >= 3 for c in cs)
        assert len(cs) == len(D) + 1


@pytest.mark.parametrize("n", range(4, 10))
def test_ears_and_snakes(n: int) -> None:
    for T in edd.triangulations(n):
        ev = ear_vertices(T, n)
        assert len(ev) == num_ears(T, n)
        assert len(set(ev)) == len(ev)
        # an ear vertex has no diagonal of T incident to it
        for v in ev:
            assert not any(v in d for d in T)
        if n >= 5:
            # every triangulation has at least two ears and it is a snake iff exactly two
            assert len(ev) >= 2
            assert is_snake(T, n) == (len(ev) == 2)
        else:
            assert is_snake(T, n)


def test_hexagon_interior_triangles() -> None:
    T = frozenset({(0, 2), (2, 4), (0, 4)})
    assert interior_triangles(T, 6) == (frozenset({0, 2, 4}),)
    assert not is_snake(T, 6)
    # a snake of the hexagon uses 3 diagonals and has exactly 2 ears
    S = edd.snake_from_word("RL", 0, 6)
    assert is_snake(S, 6) and ear_vertices(S, 6) == (0, 3)


@pytest.mark.parametrize("n", range(6, 13))
def test_delete_vertex_of_a_snake(n: int) -> None:
    r"""Deleting the last vertex from a snake yields a triangulation of ``P_{n-1}`` exactly
    when at most one of its diagonals meets that vertex."""
    word = "R" * (n - 4)
    ok = 0
    for u in range(n):
        S = edd.snake_from_word(word, u, n)
        incident = sum(1 for d in S if n - 1 in d)
        D = delete_vertex(S, n, n - 1)
        if incident <= 1:
            assert D is not None
            assert len(D) == n - 4
            assert D in set(edd.triangulations(n - 1))
            ok += 1
        else:
            assert D is None
    assert ok >= (n - 1) // 2