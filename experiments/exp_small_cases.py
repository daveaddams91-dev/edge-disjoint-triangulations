"""Experiment 1: small cases.

Produces ``results/small_cases.csv`` with, for every ``n = 4 .. 16``:

* ``M(n)`` (the packing number, ``floor(n/2)``) and whether the explicit witness attains it;
* the number of ``k``-member families of pairwise edge-disjoint triangulations, for
  ``0 <= k <= floor(n/2)`` (exact for ``n <= 10``; blank beyond, see ``README``);
* the number of triangulations (Catalan ``C_{n-2}``), snakes (``n * 2^{n-5}``) and
  resolutions (``2^{n/2-2}`` for even ``n``).

Run: ``python experiments/exp_small_cases.py``
"""

from __future__ import annotations

import edd
from common import timer, write_csv

MAX_COUNT_N = 10  # exact k-dissection counts are computed up to this n


def main() -> None:
    rows = []
    for n in range(4, 17):
        witness = edd.packing_witness(n)
        assert edd.is_edge_disjoint_family(witness)
        assert len(witness) == n // 2
        row = {
            "n": n,
            "num_triangulations": edd.num_triangulations(n),
            "num_snakes": edd.num_snakes(n),
            "packing_number": edd.max_packing(n),
            "packing_upper_bound": edd.packing_upper_bound(n),
            "witness_size": len(witness),
            "bound_attained": len(witness) == n // 2,
            "num_resolutions": edd.count_resolutions(n) if n % 2 == 0 else "",
            "num_diagonals": len(edd.diagonals(n)),
        }
        for k in range(n // 2 + 1):
            row[f"count_k_{k}"] = edd.count_k_dissections(n, k) if n <= MAX_COUNT_N else ""
        with timer() as t:
            row["ilp_packing_number"] = edd.packing_ilp(n) if n <= 12 else ""
        if n <= 12:
            print(f"    ILP check for n={n}: {row['ilp_packing_number']} "
                  f"in {t.seconds:.2f}s", flush=True)
        rows.append(row)
        print(
            f"n={n:2d} M={row['packing_number']} witness={row['witness_size']} "
            f"resolutions={row['num_resolutions']} tri={row['num_triangulations']} "
            f"snakes={row['num_snakes']} ilp={row['ilp_packing_number']}"
        )
    fields = [
        "n",
        "num_triangulations",
        "num_snakes",
        "num_diagonals",
        "packing_number",
        "packing_upper_bound",
        "witness_size",
        "bound_attained",
        "num_resolutions",
        *[f"count_k_{k}" for k in range(9)],
        "ilp_packing_number",
    ]
    path = write_csv("small_cases.csv", fields, rows)
    print("wrote", path)


if __name__ == "__main__":
    main()
