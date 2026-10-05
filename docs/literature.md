# Literature search log

What was searched, when, and what was found.  The purpose is to document the novelty claim
honestly, including its limits.  All searches were run in October 2026.

## Tools used

* arXiv API (`export.arxiv.org/api/query`) with field queries.
* Semantic Scholar Graph API search endpoint.
* General web search (DuckDuckGo HTML/lite endpoints) with quoted and unquoted phrases.
* Crossref-style keyword reasoning offline (no MathSciNet access from this environment).

## Queries run

| # | query | outcome |
|---|---|---|
| 1 | `all:"Turán number" AND all:"7-vertex"` | 1 hit, unrelated (VCD minors) — a first reconnaissance of the extremal-graph-theory neighbourhood, then dropped |
| 2 | `Turán numbers of graphs on 7 vertices unknown` | generic extremal-graph-theory pages only |
| 3 | `number of distinct values of the determinant of n x n 0-1 matrix` | search backend returned nothing; a candidate direction that was abandoned in favour of the polygon problem |
| 4 | `cap number m_2(4,q)` (finite geometry) | nothing; also abandoned |
| 5 | `Hall's principle geometric Hall algebra quiver` | nothing; also abandoned |
| 6 | `"perfect k-dissection" polygon edge-disjoint triangulations` | **no results** |
| 7 | `"edge-disjoint triangulations" convex polygon maximum number` | **no results** |
| 8 | `"partition of the diagonals" triangulations convex polygon snake triangulation` | **no results** |
| 9 | `edge-disjoint triangulations convex polygon simultaneously` | **no results** |
| 10 | `"snake triangulation" polygon dual graph path number` | **no results** |
| 11 | `diagonal set partitioned into triangulations of convex polygon snake resolution` | only generic pages on polygon triangulation |
| 12 | `maximum number of triangulations of a convex polygon with no common diagonals mathoverflow` | generic pages (Catalan counts, DP algorithms); no MathOverflow question on the packing problem was found |

## Adjacent literature that does exist and is *not* claimed as new

* Triangulations of convex polygons: Catalan numbers (OEIS A000108); the recursive
  enumeration by the cell containing a fixed side is textbook.
* Ears of a polygon and the "two ears theorem": classical; our Lemma 1 gives the version we
  need (dual tree has $\ge2$ leaves) rather than citing the classical statement.
* "Snake" / "path" / "serpentine" triangulations of a convex polygon: a standard object; the
  count $n2^{n-5}$ appears in the literature in various forms.  We re-derive it from our own
  encoding (Lemma 3) because we could not identify a reference to cite with confidence for
  the precise statement and proof we use; this is a deliberate choice, not a novelty claim.
* Dissections of a convex polygon into $p$-gons: classical, counted by the little Schröder
  numbers; existence iff $(p-2)\mid(n-2)$ is immediate from Euler's formula (our
  Proposition 7(i)).  The *packing* question for $p$-angulations is, as far as we could
  determine, not addressed anywhere.
* Integer programming via HiGHS (Huangfu–Hall 2018) and SciPy (Virtanen et al. 2020) are
  used as computational tools.

## Conclusion

> We did not find a prior result establishing:
> * the packing number $M(n)=\lfloor n/2\rfloor$ for pairwise edge-disjoint triangulations of a convex polygon;
> * the statement that for even $n=2m$ every $m$-packing is a partition of all diagonals into snakes with distinct ear pairs;
> * the classification of antipodal resolutions, or the count $2^{m-2}$.

We do **not** claim priority, and we make no claim that any of the underlying objects (ears,
snakes, triangulations, $p$-angulations, Catalan/Schröder numbers) are new.  The honest
statement is that the results above were not found in the searched sources.

## Residual risk

The searches were keyword-based and the relevant terminology is not standardised: the same
object could appear in the literature as a "$\Delta$-triangulation", "sail" of a
Garside–Deligne complex, "cluster triangulation", "flip-connected triangulation", or under
the classical term "perfect dissection" with a different notion of edge-disjointness.  A
mathematician with access to MathSciNet and to the triangulated-sphere literature would be
in a better position to rule out an earlier statement of Theorem 1 or Theorem 3.