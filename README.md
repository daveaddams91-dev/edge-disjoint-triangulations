# Edge-disjoint triangulations of convex polygons

**How many triangulations of a convex $n$-gon can be drawn at once if no two of them may
share a diagonal?  Exactly $\lfloor n/2\rfloor$ — and for even $n$ the extremal families can
be classified completely.**

[![tests](https://img.shields.io/badge/tests-190%20passing-brightgreen)](#reproducing-results)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## Research question

Let $P_n$ be a convex $n$-gon. A **$k$-packing** is a family of $k$ triangulations of $P_n$
such that no two share a diagonal. What is the largest $k$ for which a $k$-packing exists,
and what do the extremal families look like?

## Main result

$$\boxed{\;M(n)=\Big\lfloor \tfrac n2\Big\rfloor \quad\text{for every } n\ge 4\;}$$

Moreover, for even $n=2m$ the extremal question is rigid: every $m$-packing is a
**resolution** — a partition of *all* $n(n-3)/2$ diagonals into $m$ **snakes** (triangulations
with no interior triangle) whose $m$ pairs of ears partition the vertex set — and the
antipodal resolutions are in bijection with binary words of length $m-2$. There are exactly
$2^{m-2}$ of them.

## Why this is interesting

* The upper bound $\lfloor n/2\rfloor$ comes from an **ear argument**, not from diagonal
  counting. Counting diagonals gives the same bound for triangles but is *not* sharp for
  $p$-angulations (4 instead of 10 for $P_8$) — so the ear argument is doing real work, and
  the paper shows exactly where it stops working.
* For even $n$ there is **no freedom about what an extremal family is** (Proposition 2), so
  the problem reduces to a pure counting/classification question. That is unusual and makes
  the classification possible.
* Encoding a snake as a lattice path (a word in `{L,R}`) makes the whole classification a
  **single anti-palindromicity condition**, and immediately yields the count $n\,2^{n-5}$ of
  snakes as a by-product.
* The answer $2^{m-2}$ is exponentially small compared with the $n\,2^{n-5}$ snakes and the
  $C_{n-2}$ triangulations, and its structure is completely transparent (see figure 2).

## Key theorem

> **Theorem 3 (classification).** Let $n=2m\ge6$ and $w\in\{\mathrm{L},\mathrm{R}\}^{2m-4}$
> have exactly $m-2$ letters `R`. For $u\in\mathbb{Z}_m$ let $T_u$ be the snake of $P_{2m}$
> with endpoints $u$ and $u+m$ read from $u$ along $w$. Then
> $\{T_u\}$ is a resolution of $P_{2m}$ **iff** $w_i\neq w_{2m-3-i}$ for all
> $1\le i\le m-2$.
>
> **Corollary.** $P_{2m}$ has exactly $2^{m-2}$ antipodal resolutions, in bijection with
> the free first half of the word.

The full statement list (packing number, structure of extremal families, the snake/word
bijection, exact counts of $k$-packings, the $p$-angulation gap) is in
[`paper/main.tex`](paper/main.tex).

## What is proved, and what is not

| Claim | Status |
|---|---|
| $M(n)=\lfloor n/2\rfloor$ for all $n\ge4$ | **proved** (Theorem 1) |
| every $m$-packing of $P_{2m}$ is a resolution into snakes | **proved** (Proposition 2) |
| snake ↔ word bijection; level of the $i$-th strip diagonal | **proved** (Lemma 3) |
| antipodal resolutions ↔ $\{0,1\}^{m-2}$, exactly $2^{m-2}$ | **proved** (Theorem 3, Cor. 4) |
| exact counts of $k$-packings for $n\le10$ | **computed exactly** |
| every resolution is antipodal | **Conjecture 5 — verified exhaustively for $m\le7$ ($n\le14$), open in general** |
| optimum for edge-disjoint $p$-angulations, $p\ge4$ | **open** (exact values for $n\le10$) |

The paper states precisely where the proof of Conjecture 5 stops; read
[§7](paper/main.tex) before quoting the count $2^{m-2}$ as a theorem about *all*
resolutions.  The verification in `results/resolutions.csv` covers $m\le7$; the abstract
of the manuscript deliberately says "$m\le8$" only where the `--full` run is required.

## Repository structure

```
src/edd/                 the library
  polygon.py             diagonals, levels, crossings, cells, ears, snakes, vertex deletion
  dissections.py         dissections / triangulations / p-angulations (recursive enumerator)
  snakes.py              the snake <-> word (lattice path) correspondence
  resolution.py          resolutions, the classification, level conditions
  packing.py             packing number, witnesses (even and odd), ILP, certificates, counting
  verify.py              exhaustive resolution counting and the Conjecture 5 check
tests/                   188 tests (definitions, lemmas, theorems, edge cases, regressions)
experiments/             run_all.py + four experiments + figure generation
results/                 CSV/JSON outputs of the experiments (committed)
figures/                 the five figures of the paper (committed)
paper/main.tex           the manuscript
docs/                    mathematical notes, methodology, literature search log
examples/                a runnable tour of the library
```

## Reproducing results

```bash
pip install -e .
python -m pytest tests -q          # 188 tests, ~2 minutes
python experiments/run_all.py      # regenerates results/ and figures/, ~5 minutes
python experiments/run_all.py --full   # adds the n = 16 completeness check (hours)
```

Everything is deterministic: no random numbers are used anywhere, so no seeds are needed.
The only numerical dependency is HiGHS (through SciPy); every other computation is exact
integer arithmetic. The manuscript is LaTeX source (`paper/main.tex`); no LaTeX toolchain was
available in the environment used to produce this repository, so no PDF is committed — run
`pdflatex paper/main.tex` twice to build it (the figures are included from `figures/`).

## Examples

```python
>>> import edd
>>> edd.max_packing(12)
6
>>> len(edd.packing_witness(12)) == 12 // 2
True
>>> res = edd.antipodal_resolutions(12)[0]      # canonical word 'RRRRLLLL'
>>> res.word, len(res), res.ears()[:2]
('RRRRLLLL', 6, ((0, 6), (1, 7)))
>>> edd.count_resolutions(12), edd.brute_force_count_resolutions(10)
(16, 8)
>>> edd.verify_completeness(12).conjecture_holds
True
```

`examples/tour.py` prints the snake/word correspondence for $P_8$, all four resolutions of
$P_8$, and the odd-$n$ witness for $P_9$.

## Figures

| file | what it shows |
|---|---|
| `fig1_canonical_resolution.png` | the canonical resolution of $P_{10}$; the ear pairs are antipodal |
| `fig2_word_enumeration.png` | all antipodal words: free first half, forced complementary half |
| `fig3_resolution_counts.png` | $2^{m-2}$ resolutions vs. exhaustive search counts |
| `fig4_packing_vs_counts.png` | $M(n)$ and the exact counts of $k$-packings |
| `fig5_p_angulation_gap.png` | the counting bound vs. the optimum for $p$-angulations |

## Novelty

A literature search (arXiv API, Semantic Scholar, general web search for
*edge-disjoint triangulations*, *simultaneous triangulations*, *perfect $k$-dissections*,
*partition of the diagonals into triangulations*, *snake triangulations*) did not turn up a
prior statement of $M(n)$, of the structure theorem, or of the classification. The honest
claim is therefore:

> *We did not find a prior result establishing the packing number, the structure theorem, or
> the classification of antipodal resolutions.*

We do not claim priority, and we do not claim that the objects involved (ears, snakes,
triangulations of convex polygons, $p$-angulations) are new; only the results above.
See [`docs/literature.md`](docs/literature.md) for the search log.

## Citation

```bibtex
@misc{edd2026,
  title  = {Edge-disjoint triangulations of convex polygons:
            packing numbers, resolutions, and their classification},
  author = {{edd contributors}},
  year   = {2026},
  note   = {Manuscript, paper/main.tex; software at
            https://github.com/daveaddams91-dev/edge-disjoint-triangulations}
}
```

## License

MIT — see [LICENSE](LICENSE).