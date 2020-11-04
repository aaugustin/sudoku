import collections

from .grid import Grid

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
    def __init__(self):
        self.choices = [set(range(1, 10)) for _ in range(81)]
        self.values = [0 for _ in range(81)]
        self.progress = 0
        self.next = collections.deque()

    def copy(self):
        assert not self.next, "must process next before making copy"
        copy = Solver.__new__(Solver)
        copy.choices = [choices.copy() for choices in self.choices]
        copy.values = self.values.copy()
        copy.progress = self.progress
        copy.next = collections.deque()
        return copy

    def load(self, grid):
        for cell, value in enumerate(grid):
            if not value:
                continue
            if not self.mark(cell, value):
                return False
        return True

    def mark(self, cell, value):
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
        self.progress += 1

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
        return True

    def search(self):
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


def solve(grid):
    """
    Solve a grid.

    Return an iterator of 0, 1, or several solutions.

    """
    solver = Solver()
    if solver.load(grid):
        yield from solver.search()
