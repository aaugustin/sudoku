/* SuDoKu solving library
 * 
 * Improves the performance of the pure Python version
 * 
 * Copyright (C) 2008-2009 Aymeric Augustin
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
    int n;
    /* statistics */
    PyObject *g;
    char e;
#ifdef DEBUG
    char d;
#endif
} SuDoKu;

/* generated with the following Python code:
print 'static int SuDoKu_relations[81][20] = {\n    {'                        \
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

static int SuDoKu_relations[81][20] = {
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

static PyObject *SuDoKu_Contradiction;

/******************************************************************************/

static int
SuDoKu__reset(SuDoKu *self);

static int
SuDoKu__copy(SuDoKu *self, SuDoKu *t);

static int
SuDoKu__mark(SuDoKu *self, int i, int n);

static int
SuDoKu__eliminate(SuDoKu *self, int i, int n);

static int
SuDoKu__search_min(SuDoKu *self);

static int
SuDoKu__resolve_aux(SuDoKu *self, PyObject **res);

#ifdef DEBUG
static int
SuDoKu__print_graph(PyObject *g);

static int
SuDoKu__print_graph_aux(PyObject *g, char *p);
#endif

static int
SuDoKu__graph_len(PyObject *g);

static int
SuDoKu__graph_len_aux(PyObject *g, int d);

static int
SuDoKu__graph_forks(PyObject *g);

static int
SuDoKu__unique_sol_aux(SuDoKu *self);

static int
SuDoKu__unique_sol(SuDoKu *self);

static int
SuDoKu__from_string(SuDoKu *self, const char *s, int l);

static int
SuDoKu__to_console(SuDoKu *self, const int *v, char *s);

static int
SuDoKu__to_html(SuDoKu *self, const int *v, char *s);

static int
SuDoKu__to_string(SuDoKu *self, const int *v, char *s);


/******************************************************************************/

#ifdef DEBUG
static PyObject*
SuDoKu_debug(SuDoKu *self, PyObject *args);
#endif

static PyObject*
SuDoKu_resolve(SuDoKu *self);

static PyObject*
SuDoKu_estimate(SuDoKu *self);

static PyObject*
SuDoKu_generate(SuDoKu *self);

static PyObject*
SuDoKu_from_string(SuDoKu *self, PyObject *args);

static PyObject*
SuDoKu_to_string(SuDoKu *self, PyObject *args, PyObject *kwds);

/******************************************************************************/

static PyObject*
SuDoKu_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

static int
SuDoKu_init(SuDoKu *self, PyObject *args, PyObject *kwds);

static PyObject*
SuDoKu_str(SuDoKu *self);

static PyObject*
SuDoKu_repr(SuDoKu *self);

static int
SuDoKu_traverse(SuDoKu *self, visitproc visit, void *arg);

static int 
SuDoKu_clear(SuDoKu *self);

static void
SuDoKu_dealloc(SuDoKu *self);

static PyObject *
SuDoKu_get2darray(int *a);

static int
SuDoKu_set2darray(int *a, PyObject *value);

static PyObject *
SuDoKu_getv(SuDoKu *self, void *closure);

static int
SuDoKu_setv(SuDoKu *self, PyObject *value, void *closure);

static PyObject *
SuDoKu_geto(SuDoKu *self, void *closure);

static int
SuDoKu_seto(SuDoKu *self, PyObject *value, void *closure);

static PyMemberDef SuDoKu_members[] = {
    {"n", T_INT,       offsetof(SuDoKu, n), READONLY, ""},
    {"e", T_BYTE,      offsetof(SuDoKu, e), 0, ""},
    {"g", T_OBJECT_EX, offsetof(SuDoKu, g), 0, ""},
#ifdef DEBUG
    {"d", T_BYTE,      offsetof(SuDoKu, d), 0, ""},
#endif
    {NULL}
};

static PyMethodDef SuDoKu_methods[] = {
#ifdef DEBUG
    {"debug",       (PyCFunction)SuDoKu_debug,          METH_VARARGS,   ""},
#endif DEBUG
    {"resolve",     (PyCFunction)SuDoKu_resolve,        METH_NOARGS,    ""},
    {"estimate",    (PyCFunction)SuDoKu_estimate,       METH_NOARGS,    ""},
    {"generate",    (PyCFunction)SuDoKu_generate,       METH_NOARGS,    ""},
    {"from_string", (PyCFunction)SuDoKu_from_string,    METH_VARARGS,   ""},
    {"to_string",   (PyCFunction)SuDoKu_to_string,      METH_KEYWORDS,  ""},
    {NULL}
};

static PyGetSetDef SuDoKu_getseters[] = {
    {"v", (getter)SuDoKu_getv, (setter)SuDoKu_setv, "Current grid", NULL},
    {"o", (getter)SuDoKu_geto, (setter)SuDoKu_seto, "Original grid", NULL},
    {NULL}
};


static PyTypeObject SuDoKuType = {
    PyObject_HEAD_INIT(NULL)
    0,                              /*ob_size*/
    "sudoku.csudoku.SuDoKu",        /*tp_name*/
    sizeof(SuDoKu),                 /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    (destructor)SuDoKu_dealloc,     /*tp_dealloc*/
    0,                              /*tp_print*/
    0,                              /*tp_getattr*/
    0,                              /*tp_setattr*/
    0,                              /*tp_compare*/
    (reprfunc)SuDoKu_repr,          /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash */
    0,                              /*tp_call*/
    (reprfunc)SuDoKu_str,           /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
    0,                              /* tp_doc */
    (traverseproc)SuDoKu_traverse,  /* tp_traverse */
    (inquiry)SuDoKu_clear,          /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    SuDoKu_methods,                 /* tp_methods */
    SuDoKu_members,                 /* tp_members */
    SuDoKu_getseters,               /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)SuDoKu_init,          /* tp_init */
    0,                              /* tp_alloc */
    SuDoKu_new,                     /* tp_new */
};

/******************************************************************************/

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcsudoku(void);
