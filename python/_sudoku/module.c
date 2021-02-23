#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

#include "generator.h"
#include "solver.h"
#include "utils.h"

static PyObject *
_sudoku_solve(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"grid", "multiple", NULL};
    PyObject *grid;
    bool multiple = false;
    uint8_t values[81];
    PyObject *grids;
    solver s;
    size_t next[81];
    double difficulty;
    PyObject *result;

    // borrows a reference to grid
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|p", kwlist, &grid, &multiple)) {
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
        if (solver_search(&s, grids, multiple) < 0) {
            Py_DECREF(grids);
            return NULL;
        }
    }
    Py_END_ALLOW_THREADS

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
     PyDoc_STR("Solve a grid.")},
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
