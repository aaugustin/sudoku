/* SuDoKu solving library
 * 
 * Improves the performance of the pure Python version
 * 
 * Copyright (C) 2008 Aymeric Augustin
 * Released under the GPL
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

#include <Python.h>
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    /* definition */
    int o[81];  // 1..9 or 0 = undefined
    int v[81];  // 1..9 or 0 = undefined
    /* resolution */
    int p[81];  // 00000000 00000000 000000xx xxxxxxxx0
    int c[81];  // number of x == 1 in p
    int q[81];
    int q_i;    // in = push position
    int q_o;    // out = pop position
    /* statistics */
    int n;
    PyObject *g;
    /* debug */
    int d;
} CSuDoKu;

/* generated with the following Python code:
print 'static int CSuDoKu_relations[81][20] = {\n    {'                        \
    + '},\n    {'.join([                                                       \
        ','.join([                                                             \
            '%2d' % (9 * k + l)                                                \
            for k in range(9) for l in range(9)                                \
            if (k == i or l == j or (k // 3 == i // 3 and l // 3 == j // 3))   \
               and not (k == i and l == j)                                     \
        ])                                                                     \
        for i in range(9) for j in range(9)                                    \
    ])                                                                         \
    + '}\n};'                                                                   
*/

static int CSuDoKu_relations[81][20] = {
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

static PyObject *CSuDoKu_Contradiction;

static PyObject *CSuDoKu_MultipleSolutionsFound;


/******************************************************************************/

static int
CSuDoKu__reset(CSuDoKu *self);

static int
CSuDoKu__copy(CSuDoKu *self, CSuDoKu *t);

static int
CSuDoKu__mark(CSuDoKu *self, int i, int n);

static int
CSuDoKu__eliminate(CSuDoKu *self, int i, int n);

static int
CSuDoKu__searchMin(CSuDoKu *self);

static PyObject*
CSuDoKu__resolveAux(CSuDoKu *self);

static int
CSuDoKu__uniqueSolAux(CSuDoKu *self);

static int
CSuDoKu__uniqueSol(CSuDoKu *self);

/******************************************************************************/

static PyObject*
CSuDoKu_debug(CSuDoKu *self, PyObject *args);

static PyObject*
CSuDoKu_markInput(CSuDoKu *self, PyObject *args);

static PyObject*
CSuDoKu_resolve(CSuDoKu *self);

static PyObject*
CSuDoKu_generate(CSuDoKu *self);

/******************************************************************************/

static void
CSuDoKu_dealloc(CSuDoKu *self);

static PyObject*
CSuDoKu_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

static int
CSuDoKu_init(CSuDoKu *self, PyObject *args, PyObject *kwds);\

static PyObject *
CSuDoKu_get2dArray(int *a);

static int
CSuDoKu_set2dArray(int *a, PyObject *value);

static PyObject *
CSuDoKu_getv(CSuDoKu *self, void *closure);

static int
CSuDoKu_setv(CSuDoKu *self, PyObject *value, void *closure);

static PyObject *
CSuDoKu_geto(CSuDoKu *self, void *closure);

static int
CSuDoKu_seto(CSuDoKu *self, PyObject *value, void *closure);

static PyMemberDef CSuDoKu_members[] = {
    {"n", T_INT,       offsetof(CSuDoKu, n), 0, ""},
    {"g", T_OBJECT_EX, offsetof(CSuDoKu, g), 0, ""},
    {"d", T_INT,       offsetof(CSuDoKu, d), 0, ""},
    {NULL}
};

static PyMethodDef CSuDoKu_methods[] = {
    {"debug",       (PyCFunction)CSuDoKu_debug,     METH_VARARGS, ""},
    {"markInput",   (PyCFunction)CSuDoKu_markInput, METH_VARARGS, ""},
    {"resolve",     (PyCFunction)CSuDoKu_resolve,   METH_NOARGS,  ""},
    {"generate",    (PyCFunction)CSuDoKu_generate,  METH_NOARGS,  ""},
    {NULL}
};

static PyGetSetDef CSuDoKu_getseters[] = {
    {"v", (getter)CSuDoKu_getv, (setter)CSuDoKu_setv, "v", NULL},
    {"o", (getter)CSuDoKu_geto, (setter)CSuDoKu_seto, "o", NULL},
    {NULL}
};


static PyTypeObject CSuDoKuType = {
    PyObject_HEAD_INIT(NULL)
    0,                              /*ob_size*/
    "csudoku.CSuDoKu",              /*tp_name*/
    sizeof(CSuDoKu),                /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    (destructor)CSuDoKu_dealloc,    /*tp_dealloc*/
    0,                              /*tp_print*/
    0,                              /*tp_getattr*/
    0,                              /*tp_setattr*/
    0,                              /*tp_compare*/
    0,                              /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash */
    0,                              /*tp_call*/
    0,                              /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "CSuDoKu",                      /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    CSuDoKu_methods,                /* tp_methods */
    CSuDoKu_members,                /* tp_members */
    CSuDoKu_getseters,              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)CSuDoKu_init,         /* tp_init */
    0,                              /* tp_alloc */
    CSuDoKu_new,                    /* tp_new */};

/******************************************************************************/

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcsudoku(void);
