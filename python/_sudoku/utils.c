#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdbool.h>

#include "utils.h"

// Convert a Python iterable of 81 integers to a C array.
bool Grid_AsArray(PyObject *grid, uint8_t values[]) {
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
PyObject * Grid_AsPyObject(uint8_t values[]) {
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
