#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <math.h>
#include <stdbool.h>

#include "solver.h"
#include "utils.h"

static size_t relations[81][20] = {
    { 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,18,19,20,27,36,45,54,63,72},
    { 0, 2, 3, 4, 5, 6, 7, 8, 9,10,11,18,19,20,28,37,46,55,64,73},
    { 0, 1, 3, 4, 5, 6, 7, 8, 9,10,11,18,19,20,29,38,47,56,65,74},
    { 0, 1, 2, 4, 5, 6, 7, 8,12,13,14,21,22,23,30,39,48,57,66,75},
    { 0, 1, 2, 3, 5, 6, 7, 8,12,13,14,21,22,23,31,40,49,58,67,76},
    { 0, 1, 2, 3, 4, 6, 7, 8,12,13,14,21,22,23,32,41,50,59,68,77},
    { 0, 1, 2, 3, 4, 5, 7, 8,15,16,17,24,25,26,33,42,51,60,69,78},
    { 0, 1, 2, 3, 4, 5, 6, 8,15,16,17,24,25,26,34,43,52,61,70,79},
    { 0, 1, 2, 3, 4, 5, 6, 7,15,16,17,24,25,26,35,44,53,62,71,80},
    { 0, 1, 2,10,11,12,13,14,15,16,17,18,19,20,27,36,45,54,63,72},
    { 0, 1, 2, 9,11,12,13,14,15,16,17,18,19,20,28,37,46,55,64,73},
    { 0, 1, 2, 9,10,12,13,14,15,16,17,18,19,20,29,38,47,56,65,74},
    { 3, 4, 5, 9,10,11,13,14,15,16,17,21,22,23,30,39,48,57,66,75},
    { 3, 4, 5, 9,10,11,12,14,15,16,17,21,22,23,31,40,49,58,67,76},
    { 3, 4, 5, 9,10,11,12,13,15,16,17,21,22,23,32,41,50,59,68,77},
    { 6, 7, 8, 9,10,11,12,13,14,16,17,24,25,26,33,42,51,60,69,78},
    { 6, 7, 8, 9,10,11,12,13,14,15,17,24,25,26,34,43,52,61,70,79},
    { 6, 7, 8, 9,10,11,12,13,14,15,16,24,25,26,35,44,53,62,71,80},
    { 0, 1, 2, 9,10,11,19,20,21,22,23,24,25,26,27,36,45,54,63,72},
    { 0, 1, 2, 9,10,11,18,20,21,22,23,24,25,26,28,37,46,55,64,73},
    { 0, 1, 2, 9,10,11,18,19,21,22,23,24,25,26,29,38,47,56,65,74},
    { 3, 4, 5,12,13,14,18,19,20,22,23,24,25,26,30,39,48,57,66,75},
    { 3, 4, 5,12,13,14,18,19,20,21,23,24,25,26,31,40,49,58,67,76},
    { 3, 4, 5,12,13,14,18,19,20,21,22,24,25,26,32,41,50,59,68,77},
    { 6, 7, 8,15,16,17,18,19,20,21,22,23,25,26,33,42,51,60,69,78},
    { 6, 7, 8,15,16,17,18,19,20,21,22,23,24,26,34,43,52,61,70,79},
    { 6, 7, 8,15,16,17,18,19,20,21,22,23,24,25,35,44,53,62,71,80},
    { 0, 9,18,28,29,30,31,32,33,34,35,36,37,38,45,46,47,54,63,72},
    { 1,10,19,27,29,30,31,32,33,34,35,36,37,38,45,46,47,55,64,73},
    { 2,11,20,27,28,30,31,32,33,34,35,36,37,38,45,46,47,56,65,74},
    { 3,12,21,27,28,29,31,32,33,34,35,39,40,41,48,49,50,57,66,75},
    { 4,13,22,27,28,29,30,32,33,34,35,39,40,41,48,49,50,58,67,76},
    { 5,14,23,27,28,29,30,31,33,34,35,39,40,41,48,49,50,59,68,77},
    { 6,15,24,27,28,29,30,31,32,34,35,42,43,44,51,52,53,60,69,78},
    { 7,16,25,27,28,29,30,31,32,33,35,42,43,44,51,52,53,61,70,79},
    { 8,17,26,27,28,29,30,31,32,33,34,42,43,44,51,52,53,62,71,80},
    { 0, 9,18,27,28,29,37,38,39,40,41,42,43,44,45,46,47,54,63,72},
    { 1,10,19,27,28,29,36,38,39,40,41,42,43,44,45,46,47,55,64,73},
    { 2,11,20,27,28,29,36,37,39,40,41,42,43,44,45,46,47,56,65,74},
    { 3,12,21,30,31,32,36,37,38,40,41,42,43,44,48,49,50,57,66,75},
    { 4,13,22,30,31,32,36,37,38,39,41,42,43,44,48,49,50,58,67,76},
    { 5,14,23,30,31,32,36,37,38,39,40,42,43,44,48,49,50,59,68,77},
    { 6,15,24,33,34,35,36,37,38,39,40,41,43,44,51,52,53,60,69,78},
    { 7,16,25,33,34,35,36,37,38,39,40,41,42,44,51,52,53,61,70,79},
    { 8,17,26,33,34,35,36,37,38,39,40,41,42,43,51,52,53,62,71,80},
    { 0, 9,18,27,28,29,36,37,38,46,47,48,49,50,51,52,53,54,63,72},
    { 1,10,19,27,28,29,36,37,38,45,47,48,49,50,51,52,53,55,64,73},
    { 2,11,20,27,28,29,36,37,38,45,46,48,49,50,51,52,53,56,65,74},
    { 3,12,21,30,31,32,39,40,41,45,46,47,49,50,51,52,53,57,66,75},
    { 4,13,22,30,31,32,39,40,41,45,46,47,48,50,51,52,53,58,67,76},
    { 5,14,23,30,31,32,39,40,41,45,46,47,48,49,51,52,53,59,68,77},
    { 6,15,24,33,34,35,42,43,44,45,46,47,48,49,50,52,53,60,69,78},
    { 7,16,25,33,34,35,42,43,44,45,46,47,48,49,50,51,53,61,70,79},
    { 8,17,26,33,34,35,42,43,44,45,46,47,48,49,50,51,52,62,71,80},
    { 0, 9,18,27,36,45,55,56,57,58,59,60,61,62,63,64,65,72,73,74},
    { 1,10,19,28,37,46,54,56,57,58,59,60,61,62,63,64,65,72,73,74},
    { 2,11,20,29,38,47,54,55,57,58,59,60,61,62,63,64,65,72,73,74},
    { 3,12,21,30,39,48,54,55,56,58,59,60,61,62,66,67,68,75,76,77},
    { 4,13,22,31,40,49,54,55,56,57,59,60,61,62,66,67,68,75,76,77},
    { 5,14,23,32,41,50,54,55,56,57,58,60,61,62,66,67,68,75,76,77},
    { 6,15,24,33,42,51,54,55,56,57,58,59,61,62,69,70,71,78,79,80},
    { 7,16,25,34,43,52,54,55,56,57,58,59,60,62,69,70,71,78,79,80},
    { 8,17,26,35,44,53,54,55,56,57,58,59,60,61,69,70,71,78,79,80},
    { 0, 9,18,27,36,45,54,55,56,64,65,66,67,68,69,70,71,72,73,74},
    { 1,10,19,28,37,46,54,55,56,63,65,66,67,68,69,70,71,72,73,74},
    { 2,11,20,29,38,47,54,55,56,63,64,66,67,68,69,70,71,72,73,74},
    { 3,12,21,30,39,48,57,58,59,63,64,65,67,68,69,70,71,75,76,77},
    { 4,13,22,31,40,49,57,58,59,63,64,65,66,68,69,70,71,75,76,77},
    { 5,14,23,32,41,50,57,58,59,63,64,65,66,67,69,70,71,75,76,77},
    { 6,15,24,33,42,51,60,61,62,63,64,65,66,67,68,70,71,78,79,80},
    { 7,16,25,34,43,52,60,61,62,63,64,65,66,67,68,69,71,78,79,80},
    { 8,17,26,35,44,53,60,61,62,63,64,65,66,67,68,69,70,78,79,80},
    { 0, 9,18,27,36,45,54,55,56,63,64,65,73,74,75,76,77,78,79,80},
    { 1,10,19,28,37,46,54,55,56,63,64,65,72,74,75,76,77,78,79,80},
    { 2,11,20,29,38,47,54,55,56,63,64,65,72,73,75,76,77,78,79,80},
    { 3,12,21,30,39,48,57,58,59,66,67,68,72,73,74,76,77,78,79,80},
    { 4,13,22,31,40,49,57,58,59,66,67,68,72,73,74,75,77,78,79,80},
    { 5,14,23,32,41,50,57,58,59,66,67,68,72,73,74,75,76,78,79,80},
    { 6,15,24,33,42,51,60,61,62,69,70,71,72,73,74,75,76,77,79,80},
    { 7,16,25,34,43,52,60,61,62,69,70,71,72,73,74,75,76,77,78,80},
    { 8,17,26,35,44,53,60,61,62,69,70,71,72,73,74,75,76,77,78,79}
};

static uint16_t conflict = (1 << 10) - (1 << 1); // set bits 1 to 9

void solver_init(solver *s, size_t next[]) {
    memset(s, 0, sizeof(solver));
    s->next = next;
}

bool solver_mark(solver *s, size_t cell, uint8_t value) {
    // If this value is already known, there's nothing to do.
    // This happens if the input is over-constrained.
    if (s->grid[cell] == value) {
        return true;
    }

    // If we hit an incompatibility, this value doesn't work.
    if ((s->conflicts[cell] & ((uint16_t)1 << value)) != 0) {
        return false;
    }

    // Assign value.
    s->conflicts[cell] = conflict;
    s->grid[cell] = value;
    s->steps++;

    // Apply constraints.
    size_t i;
    size_t related;
    for (i = 0; i < 20; i++) {
        related = relations[cell][i];
        // If the constraint was already known, move on.
        if ((s->conflicts[related] & ((uint16_t)1 << value)) != 0) {
            continue;
        }
        // Record the constraint.
        s->conflicts[related] |= ((uint16_t)1 << value);
        // If we create an incompatibility, this value doesn't work.
        if (s->conflicts[related] == conflict) {
            return false;
        }
        // If we can determine the value, add it to the queue.
        if (__builtin_popcount(s->conflicts[related]) == 8) {
            s->next[s->next_in++] = related;
        }
    }

    // If new values become known, mark them recursively.
    while (s->next_out < s->next_in) {
        cell = s->next[s->next_out++];
        value = (uint8_t)ffs(s->conflicts[cell] ^ conflict) - (uint8_t)1;
        if (!solver_mark(s, cell, value)) {
            return false;
        }
    }

    // No incompatibility was found.
    s->progress++;
    return true;
}

bool solver_load(solver *s, uint8_t grid[]) {
    size_t cell;
    uint8_t value;
    for (cell = 0; cell < 81; cell++) {
        value = grid[cell];
        if (value == 0) {
            continue;
        }
        if (!solver_mark(s, cell, value)) {
            return false;
        }
    }
    return true;
}

static size_t solver_candidate(solver *s) {
    // Find the cell with the most conflicts.
    size_t cell = 0, candidate = 0;
    uint8_t conflicts = 0, score = 0;
    for (cell = 0; cell < 81; cell++) {
        if (s->grid[cell] == 0) {
            conflicts = __builtin_popcount(s->conflicts[cell]);
            if (conflicts > score) {
                candidate = cell;
                score = conflicts;
                // candidate() runs when all empty cells have at least 2 choices i.e. at
                // most 7 conflicts. Stop searching if we find a cell with 7 conflicts.
                if (score >= 7) {
                    break;
                }
            }
        }
    }
    return candidate;
}

static bool record_solution(PyObject *grids, uint8_t values[]) {
    // Re-acquire the GIL, which is released when solver_search runs.
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    PyObject *grid = Grid_AsPyObject(values);
    if (grid == NULL) {
        PyGILState_Release(gstate);
        return false;
    }
    if (PyList_Append(grids, grid) < 0) {
        PyGILState_Release(gstate);
        return false;
    }

    PyGILState_Release(gstate);
    return true;
}

// Return the number of solutions found, or -1 if an error occurred.
int solver_search(solver *s, PyObject *grids, bool multiple) {
    // If the grid is complete, there is a solution in this branch.
    if (s->progress == 81) {
        if (grids != NULL) {
            if (!record_solution(grids, s->grid)) {
                return -1;
            };
        }
        return 1;
    }

    // Since next is empty, sharing the underlying array with a copy is OK.
    // Indeed, mark only pushes next steps in the queue and then pops them.
    // Since search explores options sequentially, reusing the same memory
    // space for next steps doesn't cause problems.
    assert(s->next_out >= s->next_in);

    // Try all possible values of the cell with the fewest choices.
    solver copy;
    uint8_t value;
    size_t cell = solver_candidate(s);
    int solutions = 0;
    int new_solutions;
    for (value = 1; value < 10; value++) {
        if ((s->conflicts[cell] & ((uint16_t)1 << value)) == 0) {
            memcpy(&copy, s, sizeof(solver));
            if (solver_mark(&copy, cell, value)) {
                new_solutions = solver_search(&copy, grids, multiple);
                if (new_solutions < 0) {
                    s->steps = copy.steps;
                    return new_solutions;
                }
                solutions += new_solutions;
                // Abort search when two solutions are found and we don't look for more.
                if (!multiple && solutions > 1) {
                    s->steps = copy.steps;
                    return solutions;
                }
            }
            s->steps = copy.steps;
        }
    }
    return solutions;
}

double solver_difficulty(solver *s) {
    return log(fmax((double)s->steps / 81.0, 1.0)) + 1.0;
}
