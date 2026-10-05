"""A guided tour of the library.  Run: ``python examples/tour.py``."""

from __future__ import annotations

import edd


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    section("1. The objects")
    n = 8
    print(f"diagonals of P_{n}: {len(edd.diagonals(n))} (n(n-3)/2 = {n * (n - 3) // 2})")
    print(f"triangulations of P_{n}: {len(edd.triangulations(n))} (Catalan C_6 = 132)")
    print(f"snakes of P_{n}: {len(edd.snakes(n))} (n*2^(n-5) = {n * 2 ** (n - 5)})")
    print(f"short diagonals of P_{n}: {edd.short_diagonals(n)}")

    section("2. Snakes as words (Lemma 3)")
    for word in ("LRLR", "RRLL"):
        T = edd.snake_from_word(word, 0, n)
        strip = edd.strip_diagonals(word, 0, n)
        print(f"word {word}: snake {sorted(T)}")
        print(f"   strip order {strip}")
        print(f"   strip levels {[edd.strip_level(word, i) for i in range(len(strip))]}")
        print(f"   ears {edd.ear_vertices(T, n)}, word recovered: "
              f"{edd.word_from_snake(T, 0, n)!r}")

    section("3. Resolutions of P_8 (Theorem 3): exactly 2^(4-2) = 4")
    for res in edd.antipodal_resolutions(n):
        print(f"word {res.word!r}: ear pairs {res.ears()}")
    print("exhaustive search over all families of snakes agrees:",
          edd.brute_force_count_resolutions(n))

    section("4. Packing numbers (Theorem 1)")
    for k in (4, 5, 6, 7, 8, 9, 10):
        W = edd.packing_witness(k)
        kind = "resolution" if k % 2 == 0 else "vertex deletion"
        print(f"P_{k:2d}: |packing| = {len(W)} = floor({k}/2)  (witness: {kind}),"
              f" edge-disjoint = {edd.is_edge_disjoint_family(W)}")

    section("5. Exact counts of k-packings")
    for k in (5, 6, 7):
        print(f"P_{k}: {edd.count_all_packs(k)}")

    section("6. The p-angulation generalisation (Proposition 7)")
    for p in (3, 4, 5):
        for k in (6, 8, 10):
            if (k - 2) % (p - 2) != 0 or k < p:
                continue
            num = len(edd.p_angulations(k, p))
            diagonals_each = edd.p_angulation_diagonals(k, p)
            bound = len(edd.diagonals(k)) // diagonals_each if diagonals_each else 0
            print(f"p={p} n={k}: {num} p-angulations, each with {diagonals_each} diagonals;"
                  f" counting bound {bound}")

    section("7. Conjecture 5 (every resolution is antipodal)")
    for k in (6, 8, 10):
        rep = edd.verify_completeness(k, brute_force=(k <= 10))
        print(f"n={k}: {rep.num_non_antipodal_snakes} non-antipodal snakes tested, "
              f"{rep.num_extensions_found} extend to a resolution -> "
              f"conjecture holds = {rep.conjecture_holds}")


if __name__ == "__main__":
    main()