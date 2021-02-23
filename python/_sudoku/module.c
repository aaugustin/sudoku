#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

#include "generator.h"
#include "solver.h"
#include "utils.h"

static bool solve_callback(uint8_t values[], void *grids) {
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    PyObject *grid = Grid_AsPyObject(values);
    if (grid == NULL) {
        PyGILState_Release(gstate);
        return false;
    }
    if (PyList_Append((PyObject *)grids, grid) < 0) {
        PyGILState_Release(gstate);
        return false;
    }

    PyGILState_Release(gstate);
    return true;
}

static PyObject *
_sudoku_solve(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"grid", NULL};
    PyObject *grid;
    uint8_t values[81];
    PyObject *grids;
    solver s;
    size_t next[81];
    double difficulty;
    PyObject *result;

    // borrows a reference to grid
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &grid)) {
        return NULL;
    }

    if (!Grid_AsArray(grid, values)) {
        return NULL;
    }

    grids = PyList_New(0);
    if (grids == NULL) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    solver_init(&s, next);
    if (solver_load(&s, values)) {
        solver_search(&s, solve_callback, grids);
    }
    Py_END_ALLOW_THREADS
    // solve_callback may cause a Python error.
    if (PyErr_Occurred()) {
        Py_DECREF(grids);
        return NULL;
    }
    difficulty = solver_difficulty(&s);

    result = Py_BuildValue("Od", grids, difficulty);
    Py_DECREF(grids);
    return result; // may be NULL
}

static PyObject *
_sudoku_generate(PyObject *self, PyObject *args) {
    uint8_t values[81];
    double difficulty;
    PyObject *grid;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    random_grid(values);
    difficulty = minimize(values);
    Py_END_ALLOW_THREADS

    grid = Grid_AsPyObject(values);
    if (grid == NULL) {
        return NULL;
    }

    result = Py_BuildValue("Od", grid, difficulty);
    Py_DECREF(grid);
    return result; // may be NULL
}

static PyMethodDef _sudoku_methods[] = {
    {"solve",  (PyCFunction)_sudoku_solve, METH_VARARGS | METH_KEYWORDS,
     PyDoc_STR("Solve a grid.\n\nReturn a list of 0, 1, or several solutions.")},
    {"generate", (PyCFunction)_sudoku_generate, METH_VARARGS,
     PyDoc_STR("Create a random problem.")},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef _sudokumodule = {
    PyModuleDef_HEAD_INIT,
    "_sudoku",
    NULL,
    0,
    _sudoku_methods,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__sudoku(void) {
    return PyModuleDef_Init(&_sudokumodule);
}
