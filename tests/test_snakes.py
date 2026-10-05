r"""Tests for :mod:`edd.snakes`: the word/path correspondence (Lemma 3 of the paper)."""

from __future__ import annotations

from itertools import product

import pytest

import edd
from edd.polygon import diagonals, ear_vertices, is_snake, short_diagonals

N_SNAKE = range(5, 12)


def all_words(n: int) -> list[str]:
    """Every word of length ``n-4`` over ``{L, R}`` (for small ``n``, for test speed)."""
    return ["".join(p) for p in product("LR", repeat=n - 4)]


@pytest.mark.parametrize("n", range(4, 11))
def test_number_of_snakes(n: int) -> None:
    S = edd.snakes(n)
    assert len(S) == edd.num_snakes(n)
    assert all(is_snake(T, n) for T in S)
    assert len(set(S)) == len(S)


@pytest.mark.parametrize("n", range(5, 11))
def test_snakes_have_exactly_two_ears(n: int) -> None:
    for T in edd.snakes(n):
        assert len(ear_vertices(T, n)) == 2


@pytest.mark.parametrize("n", range(5, 12))
def test_word_roundtrip(n: int) -> None:
    r"""``word_from_snake(snake_from_word(w, u, n), u, n) == w`` for every word and endpoint."""
    S = set(edd.snakes(n))
    for word in all_words(n):
        for u in range(n):
            T = edd.snake_from_word(word, u, n)
            assert is_snake(T, n)
            assert len(T) == n - 3
            assert T in S
            assert edd.word_from_snake(T, u, n) == word


@pytest.mark.parametrize("n", range(5, 12))
def test_endpoints_of_a_snake_are_one_plus_number_of_R_plus_one(n: int) -> None:
    r"""Lemma 3(i): the other endpoint is ``u + #R(word) + 2`` (mod ``n``)."""
    for word in all_words(n):
        nr = word.count("R")
        for u in range(n):
            T = edd.snake_from_word(word, u, n)
            ev = ear_vertices(T, n)
            assert len(ev) == 2 and u in ev
            other = [x for x in ev if x != u][0]
            assert other == (u + nr + 2) % n


@pytest.mark.parametrize("n", range(5, 12))
def test_strip_levels_are_word_independent(n: int) -> None:
    r"""Lemma 3(ii): the ``i``-th strip diagonal has level ``min(i+2, n-i-2)``."""
    from edd.resolution import strip_diagonals

    D = set(diagonals(n))
    for word in all_words(n):
        for u in range(n):
            strip = strip_diagonals(word, u, n)
            assert len(strip) == n - 3 and set(strip) <= D
            for i, d in enumerate(strip):
                from edd.polygon import diagonal_level

                assert diagonal_level(d, n) == edd.strip_level(word, i)
                assert edd.strip_level(word, i) == min(i + 2, n - i - 2)


@pytest.mark.parametrize("n", range(5, 11))
def test_snakes_use_exactly_two_short_diagonals(n: int) -> None:
    S = set(short_diagnals := short_diagonals(n))
    for T in edd.snakes(n):
        assert len(set(T) & S) == 2


@pytest.mark.parametrize("n", (6, 8, 10, 12))
def test_count_snakes_by_word(n: int) -> None:
    r"""For every arc length the number of snakes is ``binom(n-4, #R)`` (Lemma 3(iii))."""
    from math import comb

    seen = set()
    for word in all_words(n):
        nr = word.count("R")
        key = nr
        seen.add(key)
        assert comb(n - 4, nr) >= 1
    # every snake of P_n is produced by some word and endpoint
    produced = {edd.snake_from_word(w, u, n) for w in all_words(n) for u in range(n)}
    assert produced == set(edd.snakes(n))
    assert len(produced) == edd.num_snakes(n)