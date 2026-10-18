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
    parser = argparse.ArgumentParser(
        description="N-Queens SAT solver"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Solve one instance.
    solve_parser = subparsers.add_parser(
        "solve",
        help="solve one N-Queens instance with SAT",
    )
    solve_parser.add_argument("--n", type=int, required=True)
    solve_parser.add_argument(
        "--encoding",
        choices=["pairwise", "sequential"],
        default="sequential",
    )
    solve_parser.add_argument(
        "--solver",
        choices=SUPPORTED_SOLVERS,
        default="glucose3",
    )
    solve_parser.add_argument(
        "--show-board",
        action="store_true",
    )
    solve_parser.set_defaults(func=run_solve)

    # Benchmark a range of board sizes.
    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="benchmark multiple board sizes",
    )
    benchmark_parser.add_argument("--min-n", type=int, default=4)
    benchmark_parser.add_argument("--max-n", type=int, default=30)
    benchmark_parser.add_argument(
        "--encoding",
        choices=["pairwise", "sequential"],
        default="sequential",
    )
    benchmark_parser.add_argument(
        "--solver",
        choices=SUPPORTED_SOLVERS,
        default="glucose3",
    )
    benchmark_parser.add_argument(
        "--output",
        default="results.csv",
    )
    benchmark_parser.set_defaults(func=run_benchmark)

    # Optional CP-SAT comparison.
    cpsat_parser = subparsers.add_parser(
        "compare-cpsat",
        help="solve using optional OR-Tools CP-SAT",
    )
    cpsat_parser.add_argument("--n", type=int, required=True)
    cpsat_parser.add_argument(
        "--show-board",
        action="store_true",
    )
    cpsat_parser.set_defaults(func=run_compare_cpsat)

    args = parser.parse_args()

    if getattr(args, "n", 1) < 1:
        parser.error("--n must be >= 1")

    if getattr(args, "min_n", 1) < 1:
        parser.error("--min-n must be >= 1")

    if getattr(args, "max_n", 1) < getattr(args, "min_n", 1):
        parser.error("--max-n must be >= --min-n")

    args.func(args)


if __name__ == "__main__":
    main()
