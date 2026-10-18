"""N-Queens encoding using PySAT cardinality constraints."""

from typing import List
from pysat.card import CardEnc, EncType
from misc.generateNQueensClauses import var_id


def build_clauses(
    n: int,
    amo_encoding: str = "sequential",
) -> List[List[int]]:
    if n < 1:
        raise ValueError("n must be >= 1")

    if amo_encoding not in ("pairwise", "sequential"):
        raise ValueError(
            "amo_encoding must be 'pairwise' or 'sequential'"
        )

    clauses = []
    top_id = n * n

    # Exactly one queen in each row.
    for r in range(n):
        row = [var_id(r, c, n) for c in range(n)]

        # At least one queen in the row.
        clauses.append(row)

        # At most one queen in the row.
        if amo_encoding == "pairwise":
            for i in range(len(row)):
                for j in range(i + 1, len(row)):
                    clauses.append([-row[i], -row[j]])
        else:
            enc = CardEnc.atmost(
                lits=row,
                bound=1,
                encoding=EncType.seqcounter,
                top_id=top_id,
            )
            clauses.extend(enc.clauses)
            top_id = enc.nv

    # Columns.
    groups = [
        [var_id(r, c, n) for r in range(n)]
        for c in range(n)
    ]

    # Main diagonals.
    for d in range(-(n - 1), n):
        groups.append([
            var_id(r, c, n)
            for r in range(n)
            for c in range(n)
            if c - r == d
        ])

    # Anti-diagonals.
    for s in range(2 * n - 1):
        groups.append([
            var_id(r, c, n)
            for r in range(n)
            for c in range(n)
            if r + c == s
        ])

    # At most one queen in each column or diagonal.
    for group in groups:
        if len(group) <= 1:
            continue

        if amo_encoding == "pairwise":
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    clauses.append([-group[i], -group[j]])
        else:
            enc = CardEnc.atmost(
                lits=group,
                bound=1,
                encoding=EncType.seqcounter,
                top_id=top_id,
            )
            clauses.extend(enc.clauses)
            top_id = enc.nv

    return clauses
