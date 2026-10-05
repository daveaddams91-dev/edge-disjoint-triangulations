"""Experiment 4: figures.

Each figure answers a specific mathematical question; nothing here is decorative.

fig1_canonical_resolution.png
    The canonical resolution of ``P_12``: six snakes, each drawn in its own colour.  Shows
    directly that the ``n/2`` snakes partition the diagonals and that each snake has
    exactly two ears, which are antipodal.

fig2_word_enumeration.png
    The ``2^{m-2}`` antipodal words of ``P_2m`` for ``m = 3 .. 8`` plotted as binary
    patterns (``L``=0, ``R``=1): the free first half and the forced complement are visible.

fig3_resolution_counts.png
    Observed versus predicted number of resolutions of ``P_{2m}``: ``2^{m-2}`` (log scale),
    with the brute-force counts for ``m <= 5`` overlaid as points.

fig4_packing_vs_bound.png
    ``M(n) = floor(n/2)`` together with the number of ``k``-member families of
    edge-disjoint triangulations (``k <= floor(n/2)``, log scale), the latter computed
    exactly for ``n <= 10``.

fig5_p_angulation_gap.png
    The ``p``-angulation generalisation: the counting bound versus the true optimum, showing
    that for ``p >= 4`` pure diagonal counting is not sharp.

Run: ``python experiments/make_figures.py``
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import edd
from common import FIGURES, RESULTS

plt.rcParams.update({"figure.dpi": 140, "font.size": 9, "axes.grid": True, "grid.alpha": 0.3})


def _circle(n: int, r: float = 1.0):
    ang = 2 * np.pi * np.arange(n) / n + np.pi / 2
    return r * np.cos(ang), r * np.sin(ang)


def _draw_polygon(ax, n: int) -> None:
    x, y = _circle(n)
    ax.plot(x, y, color="0.25", lw=1.0, zorder=1)
    ax.scatter(x, y, s=8, color="0.25", zorder=3)
    for i in range(n):
        ax.annotate(str(i), (x[i], y[i]), textcoords="offset points",
                    xytext=(4, 4), fontsize=6, color="0.35")


def fig1(n: int = 10) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.9))
    res = edd.resolution_from_word(edd.canonical_word(n), n)
    x, y = _circle(n)
    cmap = plt.get_cmap("tab10")
    for ax in axes:
        _draw_polygon(ax, n)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    for k, T in enumerate(res):
        col = cmap(k % 10)
        for a, b in T:
            for ax in axes:
                ax.plot([x[a], x[b]], [y[a], y[b]], color=col, lw=1.4, zorder=2)
        for v in edd.ear_vertices(T, n):
            axes[0].scatter([x[v]], [y[v]], s=60, facecolors="none", edgecolors=col,
                            lw=1.8, zorder=4)
    axes[0].set_title(f"canonical resolution of $P_{{{n}}}$\ncircles mark the two ears of each snake",
                      fontsize=8.5)
    axes[1].set_title("same colouring, no ear markers", fontsize=8.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = FIGURES / "fig1_canonical_resolution.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def fig2() -> Path:
    """Binary matrix of all antipodal words for m = 4, 5, 6: the first m-2 letters are free
    and the remaining ones are forced, so the matrix splits into two blocks that are
    complementary position by position."""
    ms = (4, 5, 6)
    fig, axes = plt.subplots(len(ms), 1, figsize=(5.6, 4.6))
    for ax, m in zip(axes, ms):
        words = edd.antipodal_words(2 * m)
        bits = np.array([[0 if c == "L" else 1 for c in w] for w in words])
        ax.imshow(bits, cmap="binary", aspect="auto", interpolation="nearest",
                  vmin=0, vmax=1)
        ax.axvline(m - 2 - 0.5, color="C3", lw=1.4)
        ax.set_title(f"$P_{{{2*m}}}$: $2^{{{m-2}}} = {len(words)}$ antipodal words "
                     f"(free half | forced complementary half)", fontsize=8)
        ax.set_yticks([])
        ax.set_xticks(range(bits.shape[1]))
        ax.set_xticklabels(list("LRLR"[: bits.shape[1]]) if bits.shape[1] <= 4 else
                           ["" for _ in range(bits.shape[1])], fontsize=6)
        ax.grid(False)
    axes[-1].set_xlabel("position in the word", fontsize=8)
    fig.tight_layout()
    path = FIGURES / "fig2_word_enumeration.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def fig3() -> Path:
    m = np.arange(3, 9)
    pred = 2.0 ** (m - 2)
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(m, pred, "o-", color="C0", label="Theorem 3: $2^{m-2}$")
    bf = [(mm, edd.brute_force_count_resolutions(2 * mm)) for mm in range(3, 6)]
    ax.plot([b[0] for b in bf], [b[1] for b in bf], "s", ms=9, mfc="none",
            color="C3", label="exhaustive search ($n\\leq 10$)")
    ax.set_yscale("log", base=2)
    ax.set_xlabel("$m$  (polygon $P_{2m}$)")
    ax.set_ylabel("number of resolutions")
    ax.set_title("Number of resolutions of $P_{2m}$", fontsize=9)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    path = FIGURES / "fig3_resolution_counts.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def fig4() -> Path:
    rows = list(csv.DictReader((RESULTS / "small_cases.csv").open(encoding="utf-8")))
    ns = [int(r["n"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot(ns, [int(r["packing_number"]) for r in rows], "o-", color="C0",
            label="$M(n)=\\lfloor n/2\\rfloor$ (Thm 1 + 3)")
    for k, color in zip(range(1, 6), plt.get_cmap("viridis")(np.linspace(0.15, 0.9, 5))):
        xs, ys = [], []
        for r in rows:
            v = r.get(f"count_k_{k}", "")
            if v:
                xs.append(int(r["n"]))
                ys.append(int(v))
        if xs:
            ax.plot(xs, ys, "s--", ms=4, color=color, lw=1.0,
                    label=f"$k={k}$ families (exact, $n\\leq 10$)")
    ax.set_yscale("log")
    ax.set_xlabel("$n$")
    ax.set_ylabel("count (log scale)")
    ax.set_title("Packing number and exact counts of $k$-member families", fontsize=9)
    ax.legend(fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    path = FIGURES / "fig4_packing_vs_counts.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def fig5() -> Path:
    rows = list(csv.DictReader((RESULTS / "p_angulations.csv").open(encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    for p, col in ((3, "C0"), (4, "C1"), (5, "C2"), (6, "C3")):
        sub = [r for r in rows if int(r["p"]) == p and int(r["counting_bound"]) > 0]
        if not sub:
            continue
        ax.plot([int(r["n"]) for r in sub], [int(r["counting_bound"]) for r in sub],
                "x--", color=col, ms=6, label=f"$p={p}$ counting bound")
        ax.plot([int(r["n"]) for r in sub], [int(r["max_disjoint"]) for r in sub],
                "o-", color=col, ms=4, label=f"$p={p}$ optimum")
    ax.set_yscale("log")
    ax.set_xlabel("$n$")
    ax.set_ylabel("max pairwise edge-disjoint $p$-angulations (log)")
    ax.set_title("Counting bound vs. optimum: sharp only for $p=3$", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    path = FIGURES / "fig5_p_angulation_gap.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    for fn in (fig1, fig2, fig3, fig4, fig5):
        p = fn()
        print("wrote", p)


if __name__ == "__main__":
    main()