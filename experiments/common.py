"""Shared helpers for the experiment scripts (deterministic, no randomness)."""

from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

__all__ = ["ROOT", "RESULTS", "FIGURES", "write_csv", "write_json", "timer", "ensure_dirs"]


def ensure_dirs() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)


def write_csv(name: str, fieldnames: list[str], rows: list[dict]) -> Path:
    ensure_dirs()
    path = RESULTS / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_json(name: str, payload) -> Path:
    ensure_dirs()
    path = RESULTS / name
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


class timer:
    """Context manager measuring wall-clock seconds in ``.seconds``."""

    def __enter__(self):
        self.seconds = 0.0
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self._t0
        return False