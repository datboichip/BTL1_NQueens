"""Helpers for generating N-Queens SAT clauses."""

from typing import Iterable, List


def var_id(row: int, col: int, n: int) -> int:
    """Map a board cell to a positive SAT variable."""
    return row * n + col + 1


def at_most_one_pairwise(
    literals: Iterable[int],
) -> List[List[int]]:
    """Generate pairwise clauses enforcing at most one true literal."""
    values = list(literals)
    clauses = []

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            clauses.append([-values[i], -values[j]])

    return clauses


def exactly_one(literals: Iterable[int]) -> List[List[int]]:
    """Generate clauses enforcing exactly one true literal."""
    values = list(literals)

    if not values:
        return [[]]

    return [values] + at_most_one_pairwise(values)
