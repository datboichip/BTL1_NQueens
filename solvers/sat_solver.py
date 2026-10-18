
"""PySAT solver wrapper for the N-Queens problem."""

from threading import Timer
from time import perf_counter

from pysat.solvers import Solver

from core.encoderCustom import build_clauses as build_pairwise
from core.encoderPySATDefault import build_clauses as build_pysat


SUPPORTED_SOLVERS = [
    "glucose3",
    "g4",
    "minisat22",
    "cadical153",
]


def solve_nqueens(
    n: int,
    encoding: str = "sequential",
    solver_name: str = "glucose3",
    time_limit: int = 40,
) -> dict:
    """Solve an N-Queens instance using a SAT encoding.

    Args:
        n: Board size.
        encoding: Either 'pairwise' or 'sequential'.
        solver_name: PySAT solver name.
        time_limit: Maximum solving time in seconds.

    Returns:
        Dictionary containing status, solution, and timing information.
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    if encoding not in ("pairwise", "sequential"):
        raise ValueError(
            "encoding must be 'pairwise' or 'sequential'"
        )

    if solver_name not in SUPPORTED_SOLVERS:
        raise ValueError(
            f"Unsupported solver: {solver_name}. "
            f"Choose from {SUPPORTED_SOLVERS}"
        )

    if time_limit <= 0:
        raise ValueError("time_limit must be greater than 0")

    # Build the CNF formula.
    start_build = perf_counter()

    if encoding == "pairwise":
        clauses = build_pairwise(n)
    else:
        clauses = build_pysat(n, "sequential")

    build_time = perf_counter() - start_build

    # Solve the SAT instance with an interrupt-based timeout.
    start_solve = perf_counter()

    result = None
    model = None

    with Solver(
        name=solver_name,
        bootstrap_with=clauses,
    ) as solver:
        timer = Timer(time_limit, solver.interrupt)
        timer.daemon = True
        timer.start()

        try:
            result = solver.solve_limited(
                expect_interrupt=True
            )
            if result is True:
                model = solver.get_model()
        finally:
            timer.cancel()
            solver.clear_interrupt()

    solve_time = perf_counter() - start_solve

    # Determine the solver status.
    if result is True:
        status = "SAT"
    elif result is False:
        status = "UNSAT"
    else:
        status = "TIMEOUT"

    # Convert positive SAT variables into queen positions.
    positions = []

    if model:
        positive = {lit for lit in model if lit > 0}

        for r in range(n):
            for c in range(n):
                variable = r * n + c + 1
                if variable in positive:
                    positions.append((r, c))

    return {
        "n": n,
        "status": status,
        "satisfiable": result is True,
        "positions": positions,
        "clauses": len(clauses),
        "variables_base": n * n,
        "build_time_seconds": build_time,
        "solve_time_seconds": solve_time,
        "solver": solver_name,
        "encoding": encoding,
    }


if __name__ == "__main__":
    for n in [4, 8, 16, 32, 48, 64]:
        for encoding in ["pairwise", "sequential"]:
            result = solve_nqueens(
                n,
                encoding=encoding,
                solver_name="glucose3",
                time_limit=40,
            )

            print(
                f"N={n:2d} | "
                f"Encoding={encoding:10s} | "
                f"Status={result['status']:6s} | "
                f"Build={result['build_time_seconds']:.4f}s | "
                f"Solve={result['solve_time_seconds']:.4f}s"
            )
