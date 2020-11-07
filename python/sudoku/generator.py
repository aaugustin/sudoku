import random

from .grid import Grid
from .solver import Solver

__all__ = ["generate"]


def random_order():
    order = list(range(81))
    random.shuffle(order)
    return order


def random_grid():
    while True:
        solver = Solver()
        # Fill cells with random values until the grid is complete
        for cell in random_order():
            if solver.values[cell]:
                continue
            value = random.choice(list(solver.choices[cell]))
            if not solver.mark(cell, value):
                break
        else:
            return Grid(solver.values)


def minimize(grid):
    grid = grid.copy()
    for cell in random_order():
        grid.values[cell], value = 0, grid.values[cell]
        solver = Solver()
        assert solver.load(grid), "minimize expects a valid grid"
        grids = list(solver.search())
        assert grids, "minimize expects a valid grid"
        if len(grids) > 1:
            grid.values[cell] = value
    return grid


def generate():
    """
    Generate a grid.

    """
    grid = random_grid()
    grid = minimize(grid)
    return grid
