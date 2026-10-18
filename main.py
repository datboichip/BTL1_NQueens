"""Command-line interface for the N-Queens SAT project."""

import argparse
import csv
import json

from core.solver import solve_nqueens, SUPPORTED_SOLVERS
from misc.generateNQueensProblem import (
    print_board,
    is_valid_solution,
)
from misc.solverCPSAT import solve_cpsat


def run_solve(args):
    result = solve_nqueens(
        args.n,
        args.encoding,
        args.solver,
    )

    summary = {
        key: value
        for key, value in result.items()
        if key != "positions"
    }

    print(json.dumps(summary, indent=2))

    if result["satisfiable"]:
        print("Positions (row, column):", result["positions"])
        print(
            "Valid solution:",
            is_valid_solution(args.n, result["positions"]),
        )

        if args.show_board:
            print_board(args.n, result["positions"])
    else:
        print("No solution exists for this board size.")


def run_benchmark(args):
    rows = []

    for n in range(args.min_n, args.max_n + 1):
        result = solve_nqueens(
            n,
            args.encoding,
            args.solver,
        )

        row = {
            "n": n,
            "satisfiable": result["satisfiable"],
            "encoding": result["encoding"],
            "solver": result["solver"],
            "variables_base": result["variables_base"],
            "clauses": result["clauses"],
            "build_time_seconds": result["build_time_seconds"],
            "solve_time_seconds": result["solve_time_seconds"],
        }

        rows.append(row)

        print(
            f"N={n:3} "
            f"SAT={result['satisfiable']} "
            f"clauses={result['clauses']} "
            f"build={result['build_time_seconds']:.4f}s "
            f"solve={result['solve_time_seconds']:.4f}s"
        )

    if rows:
        with open(
            args.output,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(rows[0].keys()),
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"Saved results to {args.output}")


def run_compare_cpsat(args):
    result = solve_cpsat(args.n)

    summary = {
        key: value
        for key, value in result.items()
        if key != "positions"
    }

    print(json.dumps(summary, indent=2))
    print("Positions (row, column):", result["positions"])
    print(
        "Valid solution:",
        is_valid_solution(args.n, result["positions"]),
    )

    if args.show_board and result["satisfiable"]:
        print_board(args.n, result["positions"])


def main():
    print("=== N-Queens SAT Solver ===")

    while True:
        try:
            n = int(input("Enter board size N: "))

            if n < 1:
                print("Please enter a positive integer.")
                continue

            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print("\nChoose SAT encoding:")
    print("1. Pairwise")
    print("2. Sequential counter")

    while True:
        encoding_choice = input("Your choice (1/2, default 2): ").strip()

        if encoding_choice in ("", "2"):
            encoding = "sequential"
            break
        elif encoding_choice == "1":
            encoding = "pairwise"
            break
        else:
            print("Invalid choice. Enter 1 or 2.")

    result = solve_nqueens(
        n=n,
        encoding=encoding,
        solver_name="glucose3",
    )

    print("\n=== Results ===")
    print(f"Board size: {n} x {n}")
    print(f"Encoding: {encoding}")
    print(f"SAT solver: {result['solver']}")
    print(f"Satisfiable: {result['satisfiable']}")
    print(f"Number of clauses: {result['clauses']}")
    print(f"Encoding time: {result['build_time_seconds']:.6f} seconds")
    print(f"Solving time: {result['solve_time_seconds']:.6f} seconds")

    if result["satisfiable"]:
        positions = result["positions"]

        print("\nQueen positions (row, column):")
        print(positions)

        print("\nValid solution:", is_valid_solution(n, positions))

        show_board = input("\nDisplay board? (y/n): ").strip().lower()

        if show_board == "y":
            print_board(n, positions)
    else:
        print("No solution exists for this board size.")


if __name__ == "__main__":
    main()