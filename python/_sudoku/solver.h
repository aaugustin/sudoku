#ifndef SUDOKU_SOLVER_H
#define SUDOKU_SOLVER_H

// solver implements the Sudoku solving algorithm.
//
// Using a solver properly takes three steps.
// First, call solver_init with a pointer to an array of 81 size_t values.
// Using a local variable avoids allocating memory on the heap.
// Second, call solver_mark for each cell whose value is known.
// Third, call solver_search to look for solutions.
typedef struct {
    size_t *next;
    size_t next_in;
    size_t next_out;
    uint8_t progress;
    uint8_t grid[81];
    uint16_t conflicts[81];
} solver;

void solver_init(solver *s, size_t next[]);

bool solver_mark(solver *s, size_t cell, uint8_t value);

bool solver_search(solver *s, bool callback(uint8_t[], void *), void *arg);

bool grid_solve(uint8_t grid[], bool callback(uint8_t[], void *), void *arg);

#endif
