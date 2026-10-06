"""Regenerate every table and figure in the repository.

Usage
-----
    python experiments/run_all.py            # default: fast pass (about 5 minutes)
    python experiments/run_all.py --full     # includes the n = 16 completeness check
                                            # (hours) and the k-packing counts for n = 10

The pass is fully deterministic: no random numbers are drawn anywhere in the project, so no
seeds need to be set.  Files written:

    results/small_cases.csv        packing numbers, counts of k-packings (n <= 10), ILP check
    results/resolutions.csv        resolution counts and the Conjecture C1 check (n <= 14)
    results/completeness.json      the same, machine readable
    results/p_angulations.csv      p-angulations: counts, counting bound, ILP optimum
    results/falsification.json     the falsification suite (attempts to refute every theorem)
    figures/fig1..fig5*.png        the five figures of the paper
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> float:
    """Worker function for parallel processing.
    
    Args:
        script:
    
    Returns:
        The computed result
    
    """
    print(f"\n=== {script} {' '.join(args)} ".ljust(78, "="), flush=True)
    t0 = time.perf_counter()
    subprocess.run([sys.executable, str(HERE / script), *args], check=True, cwd=HERE)
    dt = time.perf_counter() - t0
    print(f"--- {script} finished in {dt:.1f}s", flush=True)
    return dt


def main() -> None:
    """Entry point — parse arguments and run the main computation.
    
    """
    full = "--full" in sys.argv
    n_max_res = "16" if full else "14"
    t0 = time.perf_counter()
    run("exp_small_cases.py")
    run("exp_p_angulations.py")
    run("exp_resolutions.py", n_max_res)
    run("make_figures.py")
    run("..\\falsification\\run_falsification.py", "10")
    print(f"\nall experiments finished in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()