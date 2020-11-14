import random

from .grid import Grid
from .solver import Solver, _solve

__all__ = ["generate"]


def random_order():
    order = list(range(81))
    random.shuffle(order)
    return order


def random_grid():
    """
    Create a solution i.e. a valid, complete grid.

    """
    while True:
        solver = Solver()
        # Fill cells with random values until the grid is complete.
        for cell in random_order():
            if solver.values[cell]:
                continue
            value = random.choice(list(solver.choices[cell]))
            if not solver.mark(cell, value):
                break
        # If all cells were filled succesfully, the grid is valid.
        else:
            return Grid(solver.values)


def minimize(grid):
    """
    Turn a solution into a problem by removing values from cells.

    """

    def unique(_):
        nonlocal solved
        # Another solution was already found, abort.
        if solved:
            return False
        # First solution is found, continue.
        solved = True
        return True

    # Clear cells until this creates multiple solutions.
    for cell in random_order():
        grid.values[cell], value = 0, grid.values[cell]
        solved = False
        if not _solve(grid, unique):
            # More than one solution was found, restore cell.
            grid.values[cell] = value
        assert solved, "minimize expects a valid grid"


def generate():
    """
    Create a random problem.

    """
    grid = random_grid()
    minimize(grid)
    return grid


try:
    from _sudoku import generate
except ImportError:
    pass
