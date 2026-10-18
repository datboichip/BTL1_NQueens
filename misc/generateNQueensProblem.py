"""Create, validate, and display N-Queens boards."""

from typing import List, Tuple


def board_from_positions(
    n: int,
    positions: List[Tuple[int, int]],
) -> List[List[str]]:
    board = [["." for _ in range(n)] for _ in range(n)]

    for r, c in positions:
        board[r][c] = "Q"

    return board


def is_valid_solution(
    n: int,
    positions: List[Tuple[int, int]],
) -> bool:
    if len(positions) != n:
        return False

    if any(
        not (0 <= r < n and 0 <= c < n)
        for r, c in positions
    ):
        return False

    rows = [r for r, _ in positions]
    cols = [c for _, c in positions]
    main_diagonals = [r - c for r, c in positions]
    anti_diagonals = [r + c for r, c in positions]

    return (
        len(set(rows)) == n
        and len(set(cols)) == n
        and len(set(main_diagonals)) == n
        and len(set(anti_diagonals)) == n
    )


def print_board(
    n: int,
    positions: List[Tuple[int, int]],
) -> None:
    board = board_from_positions(n, positions)

    for row in board:
        print(" ".join(row))
