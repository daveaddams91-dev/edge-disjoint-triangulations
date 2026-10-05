# Changelog

All notable changes to this project are documented here.  The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-05

### Mathematics

- **Theorem 1** — the packing number of a convex $n$-gon is $\lfloor n/2\rfloor$ for every
  $n \ge 4$; upper bound by an ear argument, sharpness by an explicit canonical resolution
  (even $n$) and by a vertex-deletion construction (odd $n$).
- **Proposition 2** — for $n = 2m$, every $m$-packing is a *resolution*: it partitions all
  diagonals into $m$ snakes, each with exactly two ears, and the ear pairs partition the
  vertex set.
- **Lemma 3** — bijection between snakes with prescribed endpoints and words in
  `{L,R}^{n-4}`; the endpoints satisfy $v = u + \#R + 2$ and the level of the $i$-th strip
  diagonal is $\min(i+2, n-i-2)$, independent of the word.  Yields $\#\text{snakes} = n 2^{n-5}$.
- **Theorem 3 / Corollary 4** — the $m$ snakes based at the antipodal pairs and read from a
  common word $w$ partition all diagonals iff $w_i \ne w_{2m-3-i}$; consequently $P_{2m}$ has
  exactly $2^{m-2}$ antipodal resolutions, in bijection with $\{0,1\}^{m-2}$.
- **Proposition 7** — a $p$-angulation of $P_n$ exists iff $(p-2) \mid (n-2)$, and the
  counting bound on edge-disjoint $p$-angulations is not attained for $p \ge 4$.
- **Conjecture 5** — every resolution is antipodal; verified exhaustively for $m \le 7$
  (`n \le 14`); the $n = 16$ check is available with `experiments/run_all.py --full`.

### Software

- `edd.polygon` — diagonals, levels, crossing, cells (face tracing), ears, snakes, vertex
  deletion.
- `edd.dissections` — recursive enumerator for dissections, triangulations and
  $p$-angulations, cross-validated against Catalan numbers and independent brute force.
- `edd.snakes` — the word/path correspondence and its inverse.
- `edd.resolution` — resolutions, the classification, direct and closed-form level checks.
- `edd.packing` — packing number, witnesses for even and odd $n$, ILP with LP-dual
  certificates, exact counting of $k$-packings.
- `edd.verify` — exhaustive resolution counting and the Conjecture 5 exact-cover check.
- 188 tests; five experiments; five figures; manuscript in `paper/main.tex`.

### Fixed during development

- `sides()` returned unsorted vertex pairs, which broke every membership test.
- the dissection enumerator recursed into only the first and last region of the cell
  containing the side $(0, n-1)$; this silently produced non-valid "dissections" for cell
  sizes $\ge 4$ (quadrangulation counts were 13/80/595 instead of 12/55/273).
- sub-dissections were called with the number of edges instead of the number of vertices of
  the region.
- `word_from_snake` compared frozensets against a set of tuples.