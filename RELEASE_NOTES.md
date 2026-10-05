# Edge-disjoint triangulations of convex polygons — v1.0.0

## Research question

How many triangulations of a convex $n$-gon can be drawn at the same time if no two of them
may share a diagonal? Write $M(n)$ for this maximum ("packing number") and call a family of
$k$ edge-disjoint triangulations a *$k$-packing*.

## Main theorem

$$M(n)=\Big\lfloor \frac n2\Big\rfloor \qquad \text{for every } n\ge 4 .$$

* **Upper bound** — every triangulation of a convex polygon has at least two ears (its dual
  graph is a tree with at least two leaves), and each ear requires a distinct short diagonal
  $(v-1,v+1)$; there are only $n$ of them, so $2k\le n$.
* **Sharpness, even $n=2m$** — the canonical resolution: the $m$ snakes
  $T_u$ = (fan at $u-1$) $\cup$ (fan at $u-1+m$), $u\in\mathbb Z_m$, partition all diagonals.
* **Sharpness, odd $n=2m-1$** — delete one vertex from the canonical resolution of $P_{2m}$;
  exactly $m-1$ of the snakes survive as triangulations of $P_{2m-1}$.

## Main classification

For even $n=2m$ the extremal question is rigid: an $m$-packing uses $m(2m-3)$ diagonals out of
exactly $m(2m-3)$, so it *is* a partition of all diagonals, and since each member needs at least
two of the $2m$ short diagonals, every member is a **snake** (a triangulation with no interior
triangle) whose two ears, taken over the family, partition the vertex set.

Encoding a snake as a lattice path — a word $w\in\{\mathrm{L},\mathrm{R}\}^{n-4}$ recording
which end of the consumed arc absorbs each polygon side — gives:

* the other endpoint is $u+\#\mathrm{R}(w)+2$;
* the $i$-th strip diagonal has cyclic distance $\min(i+2,\,n-i-2)$, **independently of the
  word** (hence every snake has two diagonals of each level $j<n/2$ and one diameter, and
  $P_n$ has exactly $n\,2^{n-5}$ snakes);
* if $w$ has $m-2$ letters $\mathrm{R}$, then the $m$ snakes based at the antipodal pairs
  $\{u,u+m\}$ partition all diagonals **iff** $w$ is anti-palindromic,
  $w_i\neq w_{2m-3-i}$ for $1\le i\le m-2$.

Consequently the resolutions whose $m$ snakes follow a common word (these are automatically
antipodal) are in bijection with the free first half of the word, and there are **exactly
$2^{m-2}$** of them for $P_{2m}$.

Also proved: a $p$-angulation of $P_n$ exists iff $(p-2)\mid(n-2)$; exact counts of $k$-packings
for $n\le10$; and the fact that the naive counting bound on edge-disjoint $p$-angulations is
*not* sharp for $p\ge4$ (4 instead of 10 for $P_8$), which is why Theorem 1 needs the ear
argument rather than counting.

## Open part (stated honestly)

**Conjecture.** Every resolution of $P_{2m}$ follows a common word (and is therefore
antipodal). Verified exhaustively for $m\le7$ ($n\le14$) by exact-cover integer programming
plus, for $m\le5$, by brute-force enumeration of all families of snakes. Not proved in
general; §7 of the paper localises exactly the step of the argument that fails.

## Computational contribution

* Recursive enumerators for dissections, triangulations and $p$-angulations, cross-validated
  against Catalan/Schröder numbers, against brute force over diagonal subsets, and against an
  independent planar face-tracing routine.
* Exact integer programs for the packing number and for the completeness check, with an
  explicit LP-dual certificate of the bound.
* **188 unit tests** and a **43-check falsification suite** (`falsification/`) that actively
  tries to refute every theorem, including a search over all words and all ear-pairings for a
  counterexample to Corollary 4(i). All checks pass.
* Five figures, each answering a specific mathematical question.

## Reproducing

```bash
pip install -e .
python -m pytest tests -q                    # 188 tests
python falsification/run_falsification.py    # 43 adversarial checks
python experiments/run_all.py                # regenerates results/ and figures/
```

No random numbers are used anywhere, so no seeds are needed; re-running the pipeline
reproduces every table in `results/` and every figure byte for byte (verified by deleting and
regenerating). The only numerical dependency is HiGHS via SciPy; all other computation is
exact integer arithmetic.

The manuscript is `paper/main.tex`. No LaTeX toolchain was available in the authoring
environment, so no PDF is attached; build it with `pdflatex paper/main.tex` (twice) — the
figures are included from `figures/`.

## Known limitations

* Conjecture 5 (completeness of the classification) is open; the count $2^{m-2}$ is therefore
  claimed for *all* resolutions only for $m\le7$.
* Infeasibility conclusions of the integer programs are not accompanied by mathematical
  certificates; they are corroborated by an independent brute-force count for $n\le10$ and by a
  hand proof for $n=6$.
* Counts of $k$-packings are computed only for $n\le10$ (the backtracking is exponential) and
  are not extrapolated.
* The optimum for edge-disjoint $p$-angulations, $p\ge4$, is computed only for $n\le10$.
* The $n=16$ completeness check is implemented but was not run to completion here (it takes
  hours); `experiments/run_all.py --full` runs it.
* Literature: no prior result for these statements was found, but the search was keyword-based
  and the terminology for these objects is not standardised; see `docs/literature.md`.

## Licence

MIT.