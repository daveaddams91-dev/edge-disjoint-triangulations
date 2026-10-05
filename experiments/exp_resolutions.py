"""Experiment 2: resolutions and Conjecture 1 (completeness of the classification).

For each even ``n`` in ``6, 8, ..., n_max``:

* counts the antipodal resolutions (``2^{n/2-2}``, Theorem 3) and, for ``n <= 10``,
  cross-checks against exhaustive search over *all* families of snakes;
* verifies Conjecture 1 for that ``n``: no snake with non-antipodal ears extends to a
  resolution (an exact-cover integer program per snake, see ``edd.verify``).

Outputs ``results/resolutions.csv`` and ``results/completeness.json``.

Run: ``python experiments/exp_resolutions.py [n_max]``
"""

from __future__ import annotations

import sys

import edd
from common import timer, write_csv, write_json


def main() -> None:
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    rows = []
    reports = []
    for n in range(6, n_max + 1, 2):
        with timer() as t:
            report = edd.verify_completeness(n, brute_force=(n <= 10))
        d = report.to_dict()
        d.pop("witnesses")
        seconds = round(t.seconds, 2)
        reports.append(d)
        row = {
            "n": n,
            "m": n // 2,
            "num_snakes": d["num_snakes"],
            "num_non_antipodal_snakes": d["num_non_antipodal_snakes"],
            "antipodal_resolutions": d["antipodal_resolutions"],
            "predicted_2_pow_m_minus_2": 2 ** (n // 2 - 2),
            "brute_force_count": d["brute_force_count"] if d["brute_force_checked"] else "",
            "conjecture_holds": d["conjecture_holds"],
        }
        rows.append(row)
        print(
            f"n={n:2d}: snakes={d['num_snakes']:6d} "
            f"non-antipodal={d['num_non_antipodal_snakes']:6d} "
            f"antipodal resolutions={d['antipodal_resolutions']:4d} "
            f"conjecture_holds={d['conjecture_holds']} ({seconds}s)"
        )
        if d["brute_force_checked"] and d["brute_force_count"] != d["antipodal_resolutions"]:
            print(f"  WARNING: brute force {d['brute_force_count']} != {d['antipodal_resolutions']}")
    write_csv(
        "resolutions.csv",
        [
            "n",
            "m",
            "num_snakes",
            "num_non_antipodal_snakes",
            "antipodal_resolutions",
            "predicted_2_pow_m_minus_2",
            "brute_force_count",
            "conjecture_holds",
        ],
        rows,
    )
    write_json("completeness.json", {"reports": reports})
    print("wrote results/resolutions.csv and results/completeness.json")


if __name__ == "__main__":
    main()