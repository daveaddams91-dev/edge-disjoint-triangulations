"""Falsification suite: actively try to break every theorem of the paper.

Nothing here assumes the results; each check is written from the point of view of an
adversary.  All checks must pass for the paper's claims to stand.  Output:
``results/falsification.json``.

Run: ``python falsification/run_falsification.py [n_max]``   (default 10)
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, product
from pathlib import Path

import edd
from edd.polygon import cells, diagonals, ear_vertices, interior_triangles, is_snake, num_ears
from edd.resolution import strip_diagonals

ROOT = Path(__file__).resolve().parents[1]


def check(name: str, ok: bool, detail) -> dict:
    """Check whether the condition holds.
    
    Args:
        name:
        ok:
        detail:
    
    Returns:
        dict: Result of type dict
    
    """
    return {"check": name, "passed": bool(ok), "detail": detail}


def f1_odd_boundary(n_max: int) -> list[dict]:
    r"""Proposition 2 is stated for *even* ``n``.  This check documents the boundary: for odd
    ``n`` maximal packings do exist whose members are not snakes, so the rigidity of
    Proposition 2 genuinely fails there (and the ear argument of Theorem 1 is still enough
    for the bound)."""
    out = []
    for n in (7, 9):
        if n > n_max:
            continue
        k = n // 2
        non_snake = 0
        total = 0
        for fam in _maximal_packs(n, k):
            total += 1
            if any(not is_snake(T, n) for T in fam):
                non_snake += 1
        out.append(check(f"odd_n_maximal_packs_contain_non_snakes(n={n})", non_snake > 0,
                         {"families": total, "with_a_non_snake_member": non_snake,
                          "note": "n = 5 is excluded: every triangulation of a pentagon is a fan, "
                                  "hence a snake, so the rigidity does not fail there; n = 11 is "
                                  "excluded because enumerating all maximal packings is too slow"}))
    return out


def f1b_not_every_snake_fits(n_max: int) -> list[dict]:
    r"""Not every snake of ``P_{2m}`` belongs to some resolution: if some did, Prop 2 would
    be vacuous.  Counts, for each even ``n``, the snakes that do not extend to a resolution
    (an exact-cover ILP decision per snake)."""
    out = []
    for n in range(6, min(n_max, 10) + 1, 2):
        fits = 0
        for T in edd.snakes(n):
            ok, _ = edd.extends_to_resolution(T, n)
            if ok:
                fits += 1
        out.append(check(f"some_snakes_fit_and_some_do_not(n={n})", 0 < fits < len(edd.snakes(n)),
                         {"snakes": len(edd.snakes(n)), "extend_to_a_resolution": fits}))
    return out


def f2_no_bigger_packing(n_max: int) -> list[dict]:
    r"""Theorem 1 says ``M(n) = floor(n/2)``: ask the ILP for a strictly larger family."""
    out = []
    for n in range(4, min(n_max, 13) + 1):
        opt = edd.packing_ilp(n)
        out.append(check(f"ilp_optimum_equals_floor(n/2)(n={n})",
                         opt == n // 2, {"ilp_optimum": opt, "bound": n // 2}))
    return out


def f3_extremal_families_are_resolutions(n_max: int) -> list[dict]:
    r"""Proposition 2: every maximal (i.e. ``floor(n/2)``-member) packing of even ``P_n`` is a
    resolution into snakes whose ear pairs partition the vertex set.  Checked on *all*
    families, not only on the constructed ones.  Restricted to ``n <= 10`` because the
    backtracking cost grows steeply (``n = 10`` takes about a minute, ``n = 11`` hours)."""
    out = []
    for n in range(4, min(n_max, 10) + 1):
        k = n // 2
        counter = []
        seen = 0
        for fam in _maximal_packs(n, k):
            seen += 1
            if n % 2:
                # Proposition 2 concerns even n; for odd n only edge-disjointness is asserted
                if not edd.is_edge_disjoint_family(fam):
                    counter.append("family not edge-disjoint")
                continue
            if not edd.is_resolution_family(fam, n):
                counter.append("not a resolution")
            for T in fam:
                if not is_snake(T, n):
                    counter.append("member is not a snake")
            ev = [v for T in fam for v in ear_vertices(T, n)]
            if sorted(ev) != list(range(n)):
                counter.append("ear vertices do not partition")
        out.append(check(f"maximal_packs_are_resolutions(n={n})", not counter,
                         {"families_examined": seen, "problems": counter[:3]}))
    return out


def _maximal_packs(n: int, k: int):
    """All ``k``-member edge-disjoint families of ``P_n`` (small ``n`` only)."""
    Ts = edd.triangulations(n)
    from edd.polygon import diagonal_index

    didx = diagonal_index(n)
    masks = [sum(1 << didx[d] for d in T) for T in Ts]
    order = sorted(range(len(Ts)), key=lambda t: (-masks[t].bit_count(), t))
    out = []

    def rec(start, used, depth, chosen):
        """Rec.
        
        Args:
            start:
            used:
            depth:
            chosen:
        
        """
        if depth == k:
            out.append(tuple(Ts[t] for t in chosen))
            return
        if len(order) - start < k - depth:
            return
        for oi in range(start, len(order)):
            t = order[oi]
            if masks[t] & used:
                continue
            rec(oi + 1, used | masks[t], depth + 1, chosen + [t])

    rec(0, 0, 0, [])
    return out


def f4_criterion_is_necessary(n_max: int) -> list[dict]:
    r"""Theorem 3's necessity direction: *every* word that fails (CP) (or has the wrong number
    of R's) must fail to give a resolution.  All words are tested, not only the ones with
    ``m-2`` R's."""
    out = []
    for n in range(4, min(n_max, 12) + 1, 2):
        m = n // 2
        bad, tested = [], 0
        for w in ("".join(p) for p in product("LR", repeat=n - 4)):
            if w.count("R") != m - 2:
                continue
            tested += 1
            fam = [edd.snake_from_word(w, u, n) for u in range(m)]
            predicted = edd.level_condition_holds(w, n)
            actual = edd.is_resolution_family(fam, n)
            if predicted != actual:
                bad.append((w, predicted, actual))
        out.append(check(f"criterion_necessary_and_sufficient(n={n})", not bad,
                         {"words_tested": tested, "mismatches": bad[:3]}))
    return out


def f5_snake_iff_two_ears(n_max: int) -> list[dict]:
    r"""Lemma 1: a triangulation is a snake iff it has exactly two ear vertices."""
    out = []
    for n in range(5, min(n_max, 10) + 1):
        bad = []
        for T in edd.triangulations(n):
            if is_snake(T, n) != (num_ears(T, n) == 2):
                bad.append(sorted(T))
            if len(interior_triangles(T, n)) and is_snake(T, n):
                bad.append(sorted(T))
        out.append(check(f"snake_iff_two_ears(n={n})", not bad,
                         {"triangulations": len(edd.triangulations(n)),
                          "counterexamples": bad[:3]}))
    return out


def f6_boundary_cases(n_max: int = 10) -> list[dict]:
    r"""Degenerate inputs: ``n = 4``, the empty word, words with all-L and all-R."""
    out = []
    out.append(check("square_has_two_triangulations_and_one_resolution",
                     len(edd.triangulations(4)) == 2
                     and edd.brute_force_count_resolutions(4) == 1
                     and edd.num_antipodal_resolutions(4) == 1,
                     {"triangulations": len(edd.triangulations(4)),
                      "resolutions": edd.brute_force_count_resolutions(4)}))
    out.append(check("empty_word_gives_the_square_resolution",
                     edd.is_resolution_family(edd.antipodal_resolution(4, ""), 4), {}))
    bad = []
    for n in range(6, 14, 2):
        m = n // 2
        for w in ("L" * (n - 4), "R" * (n - 4)):
            fam = [edd.snake_from_word(w, u, n) for u in range(m)]
            # these words have 0 resp. n-4 letters R, so they cannot be resolutions
            if edd.is_resolution_family(fam, n):
                bad.append((n, w))
    out.append(check("degenerate_words_never_give_resolutions", not bad, {"bad": bad}))
    bad = []
    for n in range(4, 15):
        w = edd.canonical_word(n)
        if n % 2 == 0:
            fam = [edd.snake_from_word(w, u, n) for u in range(n // 2)]
            if not edd.is_resolution_family(fam, n):
                bad.append(n)
        else:
            if not edd.is_edge_disjoint_family(edd.packing_witness(n)):
                bad.append(n)
    out.append(check("explicit_witnesses_are_valid", not bad, {"n_with_failure": bad}))
    return out


def f7_ear_distance_two_forces_fan(n_max: int) -> list[dict]:
    r"""A claim used in the proof of the ``m = 3`` case of Conjecture 5: a snake whose two
    ears are at cyclic distance 2 must be a fan."""
    out = []
    for n in range(6, min(n_max, 11) + 1):
        bad = []
        for T in edd.snakes(n):
            ev = ear_vertices(T, n)
            if len(ev) == 2 and (ev[1] - ev[0]) % n == 2:
                hub = max(range(n), key=lambda v: sum(1 for e in T if v in e))
                if sum(1 for e in T if hub in e) != n - 3:
                    bad.append(sorted(T))
        out.append(check(f"ear_distance_two_is_a_fan(n={n})", not bad,
                         {"counterexamples": bad[:3]}))
    return out


def f8_common_word_resolutions_are_antipodal(n_max: int) -> list[dict]:
    r"""Corollary 4(i): every resolution whose snakes follow a common word is antipodal.
    Search over *all* words (any number of R's) and all admissible arc-start sets."""
    out = []
    for n in range(4, min(n_max, 12) + 1, 2):
        m = n // 2
        D = set(diagonals(n))
        found: dict[int, list[str]] = {}
        for w in ("".join(p) for p in product("LR", repeat=n - 4)):
            nr = w.count("R")
            if (nr + 2) % n == 0:
                continue
            hit = None
            for mask in range(1 << m):
                U = [u for u in range(m) if (mask >> u) & 1]
                if len(U) != m:
                    continue
                if sorted(list(U) + [(u + nr + 2) % n for u in U]) != list(range(n)):
                    continue
                seen: set = set()
                good = True
                for u in U:
                    T = edd.snake_from_word(w, u, n)
                    if seen & set(T):
                        good = False
                        break
                    seen |= set(T)
                if good and len(seen) == len(D):
                    hit = U
                    break
            if hit is not None:
                found.setdefault(nr, []).append(w)
        non_antipodal = {k: v[:2] for k, v in found.items() if k != m - 2}
        out.append(check(f"common_word_resolutions_are_antipodal(n={n})", not non_antipodal,
                         {"counts_by_num_R": {k: len(v) for k, v in sorted(found.items())},
                          "non_antipodal_examples": non_antipodal}))
    return out


def f9_strip_formula(n_max: int) -> list[dict]:
    r"""Formula (1) of the paper, checked against the reconstructed strip for every word and
    endpoint with ``n`` small enough to enumerate words."""
    bad = []
    checked = 0
    for n in range(5, min(n_max, 11) + 1):
        D = set(diagonals(n))
        for w in ("".join(p) for p in product("LR", repeat=n - 4)):
            for u in range(n):
                strip = strip_diagonals(w, u, n)
                checked += 1
                if set(strip) != set(edd.snake_from_word(w, u, n)) or len(strip) != n - 3:
                    bad.append((n, w, u, "strip != snake"))
                if any(d not in D for d in strip):
                    bad.append((n, w, u, "non-diagonal in strip"))
                Ls = {i + 1 for i, c in enumerate(w) if c == "L"}
                li = 0
                for i, d in enumerate(strip):
                    if i in Ls:
                        li += 1
                    if d != tuple(sorted(((u - 1 - li) % n, (u + 1 + (i - li)) % n))):
                        bad.append((n, w, u, f"formula mismatch at i={i}"))
    return [check("strip_formula_and_level_claims", not bad,
                  {"checked": checked, "counterexamples": bad[:5]})]


def main() -> None:
    """Entry point — parse arguments and run the main computation.
    
    """
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    report: dict = {"n_max": n_max, "checks": []}
    print(f"falsification suite, n_max = {n_max}\n" + "=" * 70)
    for fn in (f2_no_bigger_packing, f6_boundary_cases, f9_strip_formula, f4_criterion_is_necessary,
               f5_snake_iff_two_ears, f7_ear_distance_two_forces_fan, f3_extremal_families_are_resolutions,
               f8_common_word_resolutions_are_antipodal, f1_odd_boundary, f1b_not_every_snake_fits):
        for res in fn(n_max):
            report["checks"].append(res)
            flag = "PASS" if res["passed"] else "FAIL"
            print(f"[{flag}] {res['check']}")
            if not res["passed"]:
                print(f"        detail: {res['detail']}")
    failed = [c["check"] for c in report["checks"] if not c["passed"]]
    report["all_passed"] = not failed
    report["failed"] = failed
    out = ROOT / "results" / "falsification.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("=" * 70)
    print(f"{len(report['checks'])} checks, {len(failed)} failures -> {out}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()