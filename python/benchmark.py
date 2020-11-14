#!/usr/bin/env python

import pathlib
import sys
import timeit

try:
    from _sudoku import generate, solve  # noqa
except ImportError:
    number = 100  # Python
else:
    number = 1000  # C


def benchmark_solve():
    root = pathlib.Path(__file__).parent.parent
    with (root / "samples" / "95_hard_puzzles").open() as file:
        lines = list(file)
    t = timeit.timeit(
        """\
sudoku.solve(grids[index])
index = (index + 1) % len(grids)
""",
        f"""\
import sudoku
grids = [sudoku.Grid.from_string(line) for line in {lines!r}]
index = 0
""",
        number=number,
    )
    print(f"solve: {t / number * 1_000_000_000:.0f} ns/op")


def benchmark_generate():
    t = timeit.timeit(
        """\
sudoku.generate()
""",
        """\
import random
import sudoku
random.seed(42)
""",
        number=number,
    )
    print(f"generate: {t / number * 1_000_000_000:.0f} ns/op")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["solve", "generate"]:
        sys.stderr.write(f"usage: {sys.argv[0]} [solve|generate]\n")
        sys.exit(2)
    globals()[f"benchmark_{sys.argv[1]}"]()
