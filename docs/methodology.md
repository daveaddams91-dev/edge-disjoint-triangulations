# Methodology

How the computational claims are produced, how they are validated, and where they could be
wrong.

## 1. Principles

1. **Exactness.** Every combinatorial computation is exact integer arithmetic.  The only
   floating point anywhere in the project is inside matplotlib.  Integer programming is used
   only where a decision problem (feasibility) rather than a number is needed.
2. **No randomness.** No experiment samples; there are no seeds to record.  Re-running
   `experiments/run_all.py` reproduces every file in `results/` and `figures/` byte for byte
   (the figures are deterministic too, since matplotlib is used in `Agg` mode without
   timestamps in the metadata).
3. **Independent validation.** Every enumerator is cross-checked against a second, differently
   implemented method.  This caught three real bugs (see §5).
4. **Falsification first.** The main verification effort went into *refuting* Conjecture 5,
   not into confirming it (see §3).

## 2. Enumerators and their validation

| object | method | independent check |
|---|---|---|
| triangulations of $P_n$ | recursion on the cell containing the side $(0,n-1)$ | Catalan number $C_{n-2}$; and `cells()` (face tracing) recovers $n-2$ triangles for every one |
| all dissections of $P_n$ | same recursion, no cell-size bound | little Schröder numbers $3,11,45,197,903,4279$ for $n=4,\dots,10$ |
| $p$-angulations of $P_n$ | same recursion, cells of size $\le p$, filtered by the diagonal count from Euler's formula | brute force over $\binom{|\mathcal{D}|}{(n-p)/(p-2)}$ subsets, filtered by non-crossing and by `cells()` having $(n-2)/(p-2)$ cells of size $p$ |
| cells of a dissection | planar face tracing with the rotation system of the convex position | cross-checked against the recursive enumerator (they must agree on every triangulation) |

The two `cells()` implementations are deliberately different in kind: one walks the planar
graph, the other decomposes recursively at a side.  Agreement on ~250 000 triangulations
($n\le12$) is a strong consistency check.

## 3. The Conjecture-5 check (the main verification effort)

To test Conjecture 5 ("every resolution follows a common word, hence is antipodal") we
do **not** enumerate resolutions (the number is
not known a priori), and we do not rely on the classification.  Instead, for each snake $S$
of $P_{2m}$ whose ear pair is not antipodal we ask:

> can $\mathcal{D}_{2m}\setminus S$ be partitioned into $m-1$ snakes?

This is a set-partitioning integer program: variables $y_T\in\{0,1\}$ for every snake $T$
edge-disjoint from $S$, constraints $\sum_{T\ni d}y_T = 1$ for each remaining diagonal $d$,
objective $\max \sum_T y_T$ (the value is $m-1$ automatically if the system is feasible).
It is solved by HiGHS through `scipy.optimize.milp`.

* Any **positive** answer would be re-validated independently: the witness is extracted
  from the solver output and re-checked to be a genuine partition of $\mathcal{D}_{2m}$
  (`_validate_resolution` raises if not).  No positive answer occurred.
* **Negative** answers are taken from the solver.  This is the one place where the argument
  is not a proof in the mathematical sense: HiGHS' branch-and-bound is a floating-point
  algorithm, and we do not obtain independently checkable certificates of infeasibility.
  In practice the relaxation of these problems is very tight (the constraint matrix is
  $0/1$ with $-1$ costs on a set-partitioning structure) and the solver terminates with a
  status that a solver-independent check would be desirable for.  We therefore *also*
  verify the count independently by exhaustive search for $m\le5$, where brute-force
  enumeration over all families of snakes is feasible (`edd.brute_force_resolutions`), and
  the two methods agree ($1,2,4,8$ resolutions for $n=4,6,8,10$), and the counts equal
$2^{m-2}$.

Cost: 5 404 integer programs for $n=14$, about five minutes; the count of non-antipodal
snakes grows like $\Theta(n2^{n-5})$, so the check grows by roughly a factor $4$ per two
vertices.  $n=16$ (32 256 non-antipodal snakes) is feasible but slow (hours); it is
available with `run_all.py --full` and is not included in the committed tables.

## 4. Complexity of the algorithms

| algorithm | time | space | note |
|---|---|---|---|
| enumerate triangulations of $P_n$ | $O(n\,C_{n-2})$ | $O(n)$ per level | optimal up to the output size |
| `snake_from_word` | $O(n)$ | $O(n)$ | |
| packing ILP | $\binom{n-2}{n-3}=\Theta(4^n/n^{3/2})$ variables | | exact for $n\le13$ in seconds |
| packing certificate | $O(n^2)$ | | the LP-dual solution $x=\tfrac12$ on short diagonals certifies optimality |
| count $k$-packings | exponential | $O(1)$ bit masks of $\binom n2-n$ bits | exact to $n=10$ |
| Conjecture-5 check | $O(\#\text{snakes}\cdot \text{ILP})$ | | |

## 5. Bugs found by the validation (recorded for honesty)

1. `sides()` returned vertex pairs in the order produced by the generator, i.e. not sorted.
   Every membership test against a side therefore failed, and face tracing produced
   nonsense.  Symptom: `cells()` returned the whole polygon as a single cell for $n=4$.
2. The recursive enumerator recursed into only the *first* and *last* region left by the
   cell containing the side $(0,n-1)$, instead of into every region.  For triangulations the
   cell is a triangle and there are exactly two regions, so the bug was invisible; for
   quadrangulations it produced "dissections" containing pentagons, and the counts were
   13/80/595 instead of 12/55/273 (the correct values, confirmed by brute force).
3. Sub-dissections were requested with the number of *edges* of a region instead of its
   number of *vertices*, which under-counted triangulations of small polygons.
4. `word_from_snake` compared `frozenset` objects against a `set` of tuples; every membership
   test failed, so the function silently returned the wrong word for words containing R.

Two further errors were in the *tests* rather than the library, and are worth recording
because they produced false confidence: words were generated with
`itertools.combinations("LR", n-4)` (which enumerates letters *without* repetition, so for
$n\ge8$ exactly one "word" was produced) and the expected little Schröder numbers were
off by one index.

## 6. Threats to validity

* The ILP-based infeasibility conclusions are not accompanied by mathematical certificates
  (§3).  The independent brute-force confirmation for $n\le10$ and the $n=4$ case proof are
  what make us confident in the general claim.
* Counts of $k$-packings are only computed to $n=10$ because the backtracking is
  exponential; the paper does not extrapolate them.
* The classification is proved for common-word resolutions, which are automatically
  antipodal (Corollary 4(i) of the paper).  The number $2^{m-2}$ is claimed for *all*
  resolutions only for $m\le7$, where Conjecture 5 has been verified.
* Figures are schematic (regular polygons); no geometric property of the drawing is claimed.
  The combinatorics is independent of the embedding because a convex polygon is determined,
  up to the crossing pattern, by its labelling.