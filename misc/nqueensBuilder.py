"""Facade for selecting an N-Queens SAT encoding."""

from core.encoderCustom import build_clauses as pairwise_clauses
from core.encoderPySATDefault import build_clauses as pysat_clauses


def build_problem(n: int, encoding: str = "sequential"):
    if encoding == "pairwise":
        return pairwise_clauses(n)

    if encoding == "sequential":
        return pysat_clauses(n, "sequential")

    raise ValueError(f"Unknown encoding: {encoding}")
