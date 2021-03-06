import collections
import math

from .grid import Grid

__all__ = ["solve"]


RELATIONS = [[] for _ in range(81)]

for i1 in range(9):
    for j1 in range(9):
        for i2 in range(9):
            for j2 in range(9):
                if (
                    (i1 == i2) != (j1 == j2)
                    or
                    # i1 != i2 implies j1 != j2 at this point
                    (i1 // 3 == i2 // 3 and j1 // 3 == j2 // 3 and i1 != i2)
                ):
                    RELATIONS[9 * i1 + j1].append(9 * i2 + j2)


class Solver:
    """
    Implement the Sudoku solving algorithm.

    Using a Solver takes two steps:

    1. Call mark for each cell whose value is known.
    2. Call search to look for solutions.

    """

    def __init__(self):
        self.choices = [set(range(1, 10)) for _ in range(81)]
        self.values = [0 for _ in range(81)]
        self.progress = 0
        self.steps = 0
        self.next = collections.deque()

    @property
    def difficulty(self):
        """
        Estimate how difficult the grid is.

        The value usually rounds down to an integer between 1 and 5, making it
        suitable for a rating. 6 or more is possible but uncommon.

        """
        return math.log(max(self.steps / 81, 1)) + 1

    def copy(self):
        assert not self.next, "must process next before making copy"
        copy = Solver.__new__(Solver)
        copy.choices = [choices.copy() for choices in self.choices]
        copy.values = self.values.copy()
        copy.progress = self.progress
        copy.steps = self.steps
        copy.next = collections.deque()
        return copy

    def load(self, grid):
        """
        Mark all cells whose value is known.

        The return value is the same as in ``mark``.

        """
        for cell, value in enumerate(grid):
            if not value:
                continue
            if not self.mark(cell, value):
                return False
        return True

    def mark(self, cell, value):
        """
        Attempt to set the value of a cell.

        If value could be set, ``mark`` returns ``True``. This doesn't imply
        that the problem has at least a solution.

        If the value couldn't be set without breaking the rules, ``mark``
        returns ``False``. This makes the solver unusable. It must be
        discarded.

        """
        # If this value is already known, there's nothing to do.
        # This happens if the input is over-constrained.
        if self.values[cell] == value:
            return True

        # If we hit an incompatibility, this value doesn't work.
        if value not in self.choices[cell]:
            return False

        # Assign value.
        self.choices[cell].clear()
        self.values[cell] = value
        self.steps += 1

        # Apply constraints.
        for rel_cell in RELATIONS[cell]:
            choices = self.choices[rel_cell]
            # Record the constraint.
            try:
                choices.remove(value)
            # If the constraint was already known, move on.
            except KeyError:
                continue
            # If we create an incompatibility, this value doesn't work.
            if not choices:
                return False
            # If we can determine the value, add it to the queue.
            if len(choices) == 1:
                rel_value = next(iter(choices))
                self.next.append((rel_cell, rel_value))

        # If new values become known, mark them recursively.
        while self.next:
            cell, value = self.next.popleft()
            if not self.mark(cell, value):
                return False

        # No incompatibility was found.
        self.progress += 1
        return True

    def search(self):
        """
        Find all solutions.

        ``search`` returns a generator. To abort the search, stop iterating.

        """
        # If the grid is complete, there is a solution in this branch.
        if self.progress == 81:
            yield Grid(self.values)
            return

        # Try all possible values of the cell with the fewest choices.
        cell = min(
            (cell for cell, value in enumerate(self.values) if not value),
            key=lambda cell: len(self.choices[cell]),
        )
        for value in self.choices[cell]:
            copy = self.copy()
            if copy.mark(cell, value):
                yield from copy.search()
            self.steps = copy.steps


def solve(grid, multiple=False):
    """
    Solve a grid.

    Return a list of 0, 1, or several solutions and an estimate of how
    difficult the grid is.

    When multiple is false and there are multiple solutions, stop searching as
    soon as two solutions are found.

    """
    solver = Solver()
    if solver.load(grid):
        solutions = []
        for index, solution in enumerate(solver.search()):
            solutions.append(solution)
            if not multiple and index > 0:
                break
    else:
        solutions = []
    return solutions, solver.difficulty


try:
    from _sudoku import solve
except ImportError:
    pass
