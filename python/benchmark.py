#!/usr/bin/env python

import pathlib
import timeit


def benchmark_solve():
    root = pathlib.Path(__file__).parent.parent
    with (root / "samples" / "95_hard_puzzles").open() as file:
        lines = list(file)
    t = timeit.timeit(
        """\
for grid in grids:
    sudoku.solve(grid)
""",
        f"""\
import sudoku
grids = [sudoku.Grid.from_string(line) for line in {lines!r}]
""",
        number=1,
    )
    print(f"solve: {t / len(lines) * 1000:.0f} ms/op")


def benchmark_generate():
    iterations = 50
    t = timeit.timeit(
        f"""\
for n in range({iterations}):
    random.seed(42 * n)
    sudoku.generate()
""",
        """\
import random
import sudoku
""",
        number=1,
    )
    print(f"generate: {t / iterations * 1000:.0f} ms/op")


if __name__ == "__main__":
    benchmark_solve()
    benchmark_generate()
