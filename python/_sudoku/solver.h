#ifndef SUDOKU_SOLVER_H
#define SUDOKU_SOLVER_H

#include <stdbool.h>

// solver implements the Sudoku solving algorithm.
//
// Using a solver properly takes three steps.
// First, call solver_init with a pointer to an array of 81 size_t values.
// Using a local variable avoids allocating memory on the heap.
// Second, call solver_mark for each cell whose value is known; alternatively,
// call solver_load to load a grid.
// Third, call solver_search to look for solutions.
typedef struct {
    size_t *next;
    size_t next_in;
    size_t next_out;
    int steps;
    uint8_t progress;
    uint8_t grid[81];
    uint16_t conflicts[81];
} solver;

void solver_init(solver *s, size_t next[]);

bool solver_mark(solver *s, size_t cell, uint8_t value);

bool solver_load(solver *s, uint8_t grid[]);

int solver_search(solver *s, PyObject *grids, bool multiple);

double solver_difficulty(solver *s);

#endif
