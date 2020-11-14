#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

#include "generator.h"
#include "solver.h"

// Convert a Python iterable of 81 integers to a C array.
static bool
Grid_AsArray(PyObject *grid, uint8_t values[]) {
    PyObject *iter;
    PyObject *item;
    Py_ssize_t cell;

    iter = PyObject_GetIter(grid);
    if (iter == NULL) {
        return false;
    }

    cell = 0;
    // must check cell < 81 first to avoid leaking a referance to item.
    while (cell < 81 && (item = PyIter_Next(iter)) != NULL) {
        values[cell++] = (uint8_t)PyLong_AsLong(item);
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) {
        return false;
    }

    while (cell < 81) {
        values[cell++] = (uint8_t)0;
    }

    return true;
}

// Convert a C array of 81 integers to a Python list.
// Return value: New reference.
static PyObject *
Grid_AsPyObject(uint8_t values[]) {
    PyObject *module;
    PyObject *class;
    PyObject *list;
    Py_ssize_t cell;
    PyObject *item;
    PyObject *grid;

    module = PyImport_ImportModule("sudoku.grid");
    if (module == NULL) {
        return NULL;
    }
    class = PyObject_GetAttrString(module, "Grid");
    Py_DECREF(module);
    if (class == NULL) {
        return NULL;
    }

    list = PyList_New(81);
    if (list == NULL) {
        Py_DECREF(class);
        return NULL;
    }
    for (cell = 0; cell < 81; cell++) {
        item = PyLong_FromLong((long)values[cell]);
        if (item == NULL) {
            Py_DECREF(class);
            Py_DECREF(list);
            return NULL;
        }
        // steals a reference to item
        PyList_SET_ITEM(list, cell, item);
    }

    grid = PyObject_CallFunctionObjArgs(class, list, NULL);
    Py_DECREF(class);
    Py_DECREF(list);
    return grid; // may be NULL
}

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
    bool ok;

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
    ok = grid_solve(values, solve_callback, grids);
    Py_END_ALLOW_THREADS
    if (!ok) {
        // solve_callback may return false because a Python error occurred or
        // because there is no solution. Disambiguate.
        if (PyErr_Occurred()) {
            Py_DECREF(grids);
            return NULL;
        }
    }
    return grids;
}

static PyObject *
_sudoku_generate(PyObject *self, PyObject *args) {
    uint8_t values[81];

    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    random_grid(values);
    minimize(values);
    Py_END_ALLOW_THREADS
    return Grid_AsPyObject(values); // may be NULL
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
