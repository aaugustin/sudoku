#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

#include "generator.h"
#include "solver.h"

static uint16_t conflict = (1 << 10) - (1 << 1); // set bits 1 to 9

// random_intn generates a random integer in [0, n).
static int random_intn(int n) {
    int result;
    int mask = (1 << fls(n)) - 1;
    do {
        result = rand() & mask;
    } while (result >= n);
    return result;
}

// random_order generates a random permutation of [0, 81).
static void random_order(size_t order[]) {
    size_t i, j;
    order[0] = 0;
    for (i = 1; i < 81; i++) {
        j = (size_t)random_intn((int)i + 1);
        order[i] = order[j];
        order[j] = i;
    }
}

// random_value returns the index of a bit randomly chosen in a bitmask.
static uint8_t random_value(uint16_t choices) {
    int i;
    // Final value will be the position the n-th (0-indexed)
    // least significant bit set to 1 in the choices bitmask.
    int n = random_intn(__builtin_popcount(choices));
    for (i = 0; i < n; i++) {
        // Set least significant bit to 0.
        choices &= choices - (uint16_t)1;
    }
    // Find position of least significant bit.
    return (uint8_t)ffs(choices) - (uint8_t)1;
}

// random_grid creates a solution i.e. a valid, complete grid.
void random_grid(uint8_t grid[]) {
    solver s;
    size_t next[81];
    size_t order[81];
    size_t i;
    size_t cell;
    uint16_t choices;
    uint8_t value;

    do {
        solver_init(&s, next);
        // Fill cells with random values until the grid is complete.
        random_order(order);
        for (i = 0; i < 81; i++) {
            cell = order[i];
            if (s.grid[cell] != 0) {
                continue;
            }
            // Swap bits so 1 indicates "choice" rather than "conflict".
            choices = s.conflicts[cell] ^ conflict;
            value = random_value(choices);
            if (!solver_mark(&s, cell, value)) {
                break;
            }
        }
    // If all cells were filled succesfully, the grid is valid.
    } while (s.progress < 81);

    memcpy(grid, s.grid, sizeof(s.grid));
}

static bool minimize_callback(uint8_t grid[], void *solved) {
    // Another solution was already found, abort.
    if (*(bool *)solved) {
        return false;
    }
    // First solution is found, continue.
    *(bool *)solved = true;
    return true;
}

// minimize turns a solution into a problem by removing values from cells.
void minimize(uint8_t grid[]) {
    size_t order[81];
    size_t i;
    size_t cell;
    uint8_t value;
    bool solved;
    // Clear cells until this creates multiple solutions.
    random_order(order);
    for (i = 0; i < 81; i++) {
        cell = order[i];
        value = grid[cell];
        grid[cell] = (uint8_t)0;
        solved = false;
        if (!grid_solve(grid, &minimize_callback, (void *)&solved)) {
            // More than one solution was found, restore cell.
            grid[cell] = value;
        }
        assert(solved);
    }
}
