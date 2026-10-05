# Mathematical notes

Working notes: how the results in `paper/main.tex` were found, what was proved, what was
tried and abandoned, and exactly where the open part stops.  Section numbers refer to the
paper.

## 1. Where the question came from

The starting point was the observation that a "perfect dissection" of a convex polygon is
its classical name for a triangulation by diagonals, and that families of perfect
dissections are natural objects.  The first question worth asking is how many of them can
coexist if they may not share a diagonal.  Diagonal counting immediately gives

$$k\cdot(n-3)\ \le\ \frac{n(n-3)}{2}\qquad\Longrightarrow\qquad k\le\frac n2 ,$$

which is *not* the sharp answer we wanted: for odd $n$ it gives $k\le n/2$, i.e.
$k\le (n-1)/2$ after taking the floor — the same as the true answer, but the argument
gives nothing for even $n$ either.  What is interesting is that the answer is always
$\lfloor n/2\rfloor$, i.e. the counting bound *is* sharp for triangles.  That suggested
looking for the structure of extremal families rather than the number alone.

## 2. The two ingredients that do the work

**(a) Ears.**  The dual graph of a triangulation of $P_n$ is a tree with $n-2$ vertices, so
it has at least two leaves, i.e. the triangulation has at least two ears, i.e. it uses at
least two short diagonals $s_v=(v-1,v+1)$.  Since there are exactly $n$ short diagonals and
the members of a packing must use disjoint sets of them, $2k\le n$.  (Lemma 1.)

**(b) Snakes as words.**  A snake is a triangulation with no interior triangle.  Reading its
strip from one ear to the other, each step absorbs one polygon side, at either end of the
consumed arc; this gives a word $w\in\{\mathrm{L},\mathrm{R}\}^{n-4}$.  Two facts fell out
of this encoding immediately:

* the other endpoint is $v=u+\#\mathrm{R}(w)+2$ — so a snake's endpoints are determined by
  the number of right moves;
* the $i$-th strip diagonal is $\{u-1-L_i,\ u+1+R_i\}$, whose endpoints differ by
  $i+2$, so its **level** (cyclic distance) is $\min(i+2,n-i-2)$, *independent of the word*.

The second fact is the crucial one: it means a snake contains exactly two diagonals of each
level $j<n/2$ and exactly one diameter, no matter which word it follows.  So a family of
snakes covers the diagonals of a given level only if the $2m$ "starts" of those diagonals
run through all residues — and that is a purely arithmetic condition.

## 3. The classification (Theorem 3)

Fix $n=2m$ and a word $w$ with $m-2$ right moves; let $T_u$ be the snake with endpoints
$u,u+m$.  At level $j=i+2\le m-1$ the strip positions $i$ and $n-2-i$ both have level $j$,
and their starts are

$$\alpha_u=u-1-L_i \qquad\text{and}\qquad y_u=u+1+R_{n-2-i}=u+m-1-\widehat\rho_i,$$

where $L_i$ = number of L's in the first $i$ letters and $\widehat\rho_i$ = number of R's in
the last $i$ letters.  The family covers level $j$ iff $\{\alpha_u\}\sqcup\{y_u\}=\Z_{2m}$.

*If the word is anti-palindromic*, the last $i$ letters are the letterwise complement of the
first $i$ ones, so $\widehat\rho_i=L_i$ and $y_u=\alpha_u+m$: the two sets of starts are two
disjoint blocks of $m$ consecutive residues, i.e. a partition.  The diameter level is
automatic.  Conversely, if the family is a resolution then $A=\{\alpha_u\}$ is a block of
$m$ consecutive residues and $A\sqcup(A+\delta)=\Z_{2m}$ forces $\delta\equiv m$, hence
$L_i=\widehat\rho_i$; consecutive differences give "letters in positions $i$ and $n-2-i$
differ" for $i\le m-3$, and the total count of letters settles the last pair.  QED.

The condition "letters in positions $i$ and $n-2-i$ differ" for $i=1,\dots,m-2$ forces
exactly one letter per pair, so the first $m-2$ letters are free: $2^{m-2}$ words, hence
$2^{m-2}$ common-word resolutions (Corollary 4).

## 4. Dead ends and things that did *not* work

* **Lattice paths in the Tamari lattice / associahedron.**  Triangulations of $P_{2m}$
  correspond to binary trees and the flip graph to the associahedron, whose automorphism
  group is the hyperoctahedral group; classifying *orbits* of triangulations under it is
  known territory and would have been a rediscovery.  Abandoned in favour of the ear/strip
  structure, which is genuinely about the covering condition.

* **Trying to prove Conjecture 5 by induction over the levels.**  The covering argument in
  §3 relies on the starts at a fixed level forming two blocks of consecutive residues.  In
  the general (non-antipodal) case the starts are
  $a_u - 1 - \ell^{(u)}_i$ and $b_u - 1 - \hat\rho^{(u)}_i$, and $\ell^{(u)}_i$,
  $\hat\rho^{(u)}_i$ depend on $u$, so the block argument does not apply.  What we could
  prove:

  - from the level-$1$ covering condition and a "winding number" argument on the induced
    permutation $x\mapsto x-d(x)$: **all snakes agree on their first move and on their
    last move** (either all start with R and end with L, or all start with L and end with R);
  - similarly the level-$2$ condition forces agreement on the second and second-to-last
    moves, provided the parity of the common prefix/suffix contributions agrees;
  - the level-$m-2$ (diameter) condition forces agreement on move $m-2$ whenever two
    arc-start vertices are consecutive mod $m$.

  The induction that would propagate agreement to all $2m-4$ positions needs, at each level,
  the condition $\sum_u (\ell^{(u)}_i + \hat\rho^{(u)}_i)\equiv 0 \pmod{2m}$ with the
  summands independent of $u$, and that is exactly what the parity caveat breaks: when the
  common prefix contributes an L and the common suffix contributes an R, the sum can be
  $m$ instead of $0$ and the argument only forces "half of the snakes".  This is the
  precise point where the argument stops; see §7 of the paper.

* **Induction by deleting two vertices.**  Tried: given a resolution of $P_{2m}$, delete two
  vertices and repair.  The repair is not local — deleting a vertex forces the snake
  containing it to lose up to $m-1$ diagonals — so no clean recursion appears.

* **Counting $k$-packings by the symmetry of $D_n$.**  The dihedral group does not act
  transitively on triangulations, so the "count the packings through one triangulation and
  multiply" trick needs orbit bookkeeping.  We instead used a brute-force double count
  $\sum_T \#\{k\text{-packings containing }T\} = k N_k$ as a *test* of the backtracking
  counter (`tests/test_packing.py`), which is exact and implementation-independent.

## 5. Boundary cases checked

* $n=4$: a square has 2 triangulations, they are edge-disjoint, and the resolution of $P_4$
  is the pair of them; the word is empty and $2^{m-2}=1$.
* $n=5$: $M(5)=2$; the deletion construction gives $\{(0,2),(0,3)\}$ and $\{(1,3),(1,4)\}$.
* $n=6$: the 2 resolutions correspond to the words `LR` and `RL`; the 6 snakes with
  non-antipodal ears do not extend to a resolution (checked by ILP).
* Ear distance $2$ forces a fan: if a snake has ears at $u$ and $u+2$, both end triangles of
  the dual path contain $u+1$, and since the triangles containing a fixed vertex form a
  connected sub-path of the dual path, *every* triangle contains $u+1$, i.e. the snake is a
  fan; a fan uses $n-3$ diagonals at a single vertex and cannot be a member of a resolution
  with more than one member.  This is the $m=3$ case of Conjecture 5.

## 6. Things that were computed and are not in the paper

* Exact counts of $k$-packings for $n\le10$ (in `results/small_cases.csv`), e.g. $2\,436$
  pairs and $2\,472$ triples for $P_8$.
* The number of snakes $n2^{n-5}$ and the number of dissections (little Schröder) were used
  to validate the enumerators, not as results.
* Quadrangulation counts $1,3,12,55,273$ for $P_4,\dots,P_{12}$, and the corresponding
  packing optima $1,3,4,5$.