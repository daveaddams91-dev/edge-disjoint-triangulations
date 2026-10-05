"""Experiment 3: the ``p``-angulation generalisation.

For ``p in {3, 4, 5, 6}`` and small ``n``, compute the number of ``p``-angulations of
``P_n`` and the maximum number of pairwise edge-disjoint ``p``-angulations, together with
the counting upper bound ``floor( (n(n-3)/2) / ((n-p)/(p-2)) )``.

Outputs ``results/p_angulations.csv``.  This experiment is *exploratory*: it shows that the
counting bound is not always attained -- already for quadrilateral dissections of a
hexagon -- which is why Theorem 1 needs the ear argument rather than pure counting.

Run: ``python experiments/exp_p_angulations.py``
"""

from __future__ import annotations

import edd
from edd.polygon import diagonal_index
from common import write_csv


def counting_bound(n: int, p: int) -> int:
    """``floor( (n(n-3)/2) / ((n-p)/(p-2)) )``: the number of edge-disjoint p-angulations
    that pure diagonal counting permits."""
    d = edd.p_angulation_diagonals(n, p)
    if d == 0:
        return 0
    return len(edd.diagonals(n)) // d


def max_disjoint(n: int, p: int) -> int:
    """Maximum number of pairwise edge-disjoint ``p``-angulations of ``P_n``, by ILP."""
    angs = edd.p_angulations(n, p)
    if not angs:
        return 0
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix

    D = edd.diagonals(n)
    didx = diagonal_index(n)
    rows, cols = [], []
    for t, A in enumerate(angs):
        for d in A:
            rows.append(didx[d])
            cols.append(t)
    M = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(D), len(angs)))
    res = milp(
        c=-np.ones(len(angs)),
        constraints=[LinearConstraint(M.tocsr(), -np.inf, np.ones(len(D)))],
        integrality=np.ones(len(angs)),
        bounds=Bounds(0, 1),
    )
    return int(round(-res.fun))


def main() -> None:
    rows = []
    for p in (3, 4, 5, 6):
        n_max = 12 if p == 3 else 10
        for n in range(3, n_max + 1):
            if n < p or (n - 2) % (p - 2) != 0:
                continue
            num = len(edd.p_angulations(n, p))
            bound = counting_bound(n, p)
            # for p = 3 the exact value is Theorem 1, so no ILP is needed
            best = edd.max_packing(n) if p == 3 else max_disjoint(n, p)
            rows.append(
                {
                    "p": p,
                    "n": n,
                    "diagonals_per_p_angulation": edd.p_angulation_diagonals(n, p),
                    "num_p_angulations": num,
                    "counting_bound": bound,
                    "max_disjoint": best,
                    "bound_attained": best == bound,
                }
            )
            print(
                f"p={p} n={n:2d}: #p-angulations={num:6d} counting bound={bound:3d} "
                f"optimum={best:3d} attained={best == bound}",
                flush=True,
            )
    write_csv(
        "p_angulations.csv",
        [
            "p",
            "n",
            "diagonals_per_p_angulation",
            "num_p_angulations",
            "counting_bound",
            "max_disjoint",
            "bound_attained",
        ],
        rows,
    )
    print("wrote results/p_angulations.csv")


if __name__ == "__main__":
    main()