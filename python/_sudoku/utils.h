#ifndef SUDOKU_UTILS_H
#define SUDOKU_UTILS_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

bool Grid_AsArray(PyObject *grid, uint8_t values[]);

PyObject * Grid_AsPyObject(uint8_t values[]);

#endif
