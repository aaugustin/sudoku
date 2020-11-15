import random

from .grid import Grid
from .solver import Solver

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
    difficulty = 0
    # Clear cells until this creates multiple solutions.
    for cell in random_order():
        grid.values[cell], value = 0, grid.values[cell]
        solver = Solver()
        assert solver.load(grid), "minimize expects a valid grid"
        solutions = solver.search()
        try:
            next(solutions)
        except StopIteration:  # pragma: no cover
            raise AssertionError("minimize expects a valid grid")
        try:
            next(solutions)
        except StopIteration:
            # Only one solution was found.
            difficulty = solver.difficulty
        else:
            # More than one solution was found, restore cell.
            grid.values[cell] = value
    return difficulty


def generate():
    """
    Create a random problem.

    """
    grid = random_grid()
    difficulty = minimize(grid)
    return grid, difficulty


try:
    from _sudoku import generate
except ImportError:
    pass
