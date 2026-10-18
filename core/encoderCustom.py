"""Handwritten pairwise SAT encoding for N-Queens."""

from typing import List
from misc.generateNQueensClauses import (
    var_id,
    exactly_one,
    at_most_one_pairwise,
)


def build_clauses(n: int) -> List[List[int]]:
    """Return CNF clauses for an N x N N-Queens board."""
    if n < 1:
        raise ValueError("n must be >= 1")

    clauses = []

    # Exactly one queen in every row.
    for r in range(n):
        row_vars = [var_id(r, c, n) for c in range(n)]
        clauses.extend(exactly_one(row_vars))

    # At most one queen in every column.
    for c in range(n):
        col_vars = [var_id(r, c, n) for r in range(n)]
        clauses.extend(at_most_one_pairwise(col_vars))

    # Main diagonals.
    for d in range(-(n - 1), n):
        diagonal = [
            var_id(r, c, n)
            for r in range(n)
            for c in range(n)
            if c - r == d
        ]
        clauses.extend(at_most_one_pairwise(diagonal))

    # Anti-diagonals.
    for s in range(2 * n - 1):
        diagonal = [
            var_id(r, c, n)
            for r in range(n)
            for c in range(n)
            if r + c == s
        ]
        clauses.extend(at_most_one_pairwise(diagonal))

    return clauses
