/* SuDoKu solving library
 *
 * Improves the performance of the pure Python version
 *
 * Copyright (c) 2008-2009 Aymeric Augustin
   # Copyright (c) 2008-2009 Aymeric Augustin
 */

#include "csudoku.h"
#include "math.h"

/******************************************************************************/

static int
SuDoKu__reset(SuDoKu *self)
{
    int i;

    /* resolution */
    for (i = 0; i < 81; i++)
    {
        self->v[i] = 0;
        self->p[i] = 1022; /* (1 << 10) - 2 */
        self->c[i] = 9;
        self->q[i] = -1;
    }
    self->q_i = 0;
    self->q_o = 0;
    self->n = 0;

    /* statistics */
    if (self->e)
    {
        Py_XDECREF(self->g);
        Py_INCREF(Py_None);
        self->g = Py_None;
    }

    return 0;
}

static int
SuDoKu__copy(SuDoKu *self, SuDoKu *t)
{
    memcpy(t->o, self->o, 81 * sizeof(int));
    memcpy(t->v, self->v, 81 * sizeof(int));
    memcpy(t->p, self->p, 81 * sizeof(int));
    memcpy(t->c, self->c, 81 * sizeof(int));
    memcpy(t->q, self->q, 81 * sizeof(int));
    t->q_i = self->q_i;
    t->q_o = self->q_o;
    t->n = self->n;

    /* self->g is not copied; that does not matter for the algorithm */
    if (self->e)
    {
        Py_XDECREF(t->g);
        Py_INCREF(Py_None);
        t->g = Py_None;
    }

#ifdef DEBUG
    t->d = self->d;
#endif

    return 0;
}

static int
SuDoKu__mark(SuDoKu *self, int i, int n)
{
    int *rel, p, j;

    if (self->v[i] == n)
    {
        return 0;
    }

    if (!((self->p[i] >> n) & 1))
    {
#ifdef DEBUG
        if (self->d)
        {
            PySys_WriteStdout("    Attempt to assign %d at (%d, %d) which is forbidden\n", n, i / 9, i % 9);
        }
#endif  
        if (self->e)
        {
            // XXXXX Safe ?
            Py_DECREF(self->g);
            self->g = Py_BuildValue("ic", self->n, '-');
        }

        PyErr_SetNone(SuDoKu_Contradiction);
        return -2;
    }

    self->v[i] = n;
    self->n += 1;
    self->p[i] = 0;
    self->c[i] = 0;

    rel = SuDoKu_relations[i];
    for (j = 0; j < 20; j++)
    {
        if (SuDoKu__eliminate(self, rel[j], n) == -2)
        {
            return -2;
        }
    }

    while (self->q_o < self->q_i)
    {
        i = self->q[self->q_o];
        self->q_o += 1;
        p = self->p[i];
        if (p < 0)
        {
            return -2;
        }
        n = 0;
        while ((p & 1) == 0)
        {
            p >>= 1;
            n += 1;
        }
        if (SuDoKu__mark(self, i, n) == -2)
        {
            return -2;
        }
    }
    return 0;
}

static int
SuDoKu__eliminate(SuDoKu *self, int i, int n)
{
    if ((self->p[i] >> n) & 1)
    {
        self->p[i] &= 1022 - (1 << n);
        self->c[i] -= 1;
        if (self->c[i] == 0)
        {
#ifdef DEBUG
            if (self->d)
            {
                PySys_WriteStdout("    Impossibility at (%d, %d), search depth = %d\n", i / 9, i % 9, self->n);
            }
#endif
            if (self->e)
            {
                // XXXXX Safe ?
                Py_DECREF(self->g);
                self->g = Py_BuildValue("ic", self->n, '-');
            }
            return -2;
        }
        else if (self->c[i] == 1)
        {
            self->q[self->q_i] = i;
            self->q_i += 1;
            return 0;
        }

    }
    return 0;
}

static int
SuDoKu__search_min(SuDoKu *self)
{
    int i, im, cm;

    im = -1;
    cm = 10;
    for (i = 0; i < 81; i++)
    {
        if (self->v[i] == 0 && self->c[i] < cm)
        {
            im = i;
            cm = self->c[i];
        }
    }
    return im;
}

static PyObject*
SuDoKu__resolve_aux(SuDoKu *self)
{
    PyObject *res, *sres, *grid, *sg = NULL;
    SuDoKu *t;
    int i, n, x;

    res = PyList_New(0);
    if (res == NULL)
    {
        Py_DECREF(res);
        return NULL;
    }

    if (self->n == 81)
    {
#ifdef DEBUG
        if (self->d)
        {
            PySys_WriteStdout("    Found a solution: ");
            for (i = 0; i < 81; i++)
            {
                PySys_WriteStdout("%d", self->v[i]);
            }
            PySys_WriteStdout("\n");
        }
#endif
        if (self->e)
        {
            Py_DECREF(self->g);
            self->g = Py_BuildValue("ic", self->n, '+');
        }
        if (PyList_Append(res, SuDoKu_get2darray(self->v)) < 0)
        {
            return NULL;
        }
        return res;
    }

    i = SuDoKu__search_min(self);

    t = (SuDoKu*)PyType_GenericNew(&SuDoKuType, NULL, NULL);

    if (self->e)
    {
        sg = PyList_New(0);
        if (sg == NULL)
        {
            Py_DECREF(sg);
            return NULL;
        }
    }

    for (n = 1; n < 10; n++)
    {
        if ((self->p[i] >> n) & 1)
        {
#ifdef DEBUG
            if (self->d)
            {
                PySys_WriteStdout("Trying %d at (%d, %d), search depth = %d\n", n, i / 9, i % 9, self->n);
            }
#endif
            SuDoKu__copy(self, t);
            if (SuDoKu__mark(t, i, n) == -2)
            {
                if (self->e)
                {
                    if (PyList_Append(sg, t->g))
                    {
                        return NULL;
                    }
                }
                continue;
            }
            sres = SuDoKu__resolve_aux(t);
            for (x = 0; x < PyList_Size(sres); x++)
            {
                grid = PyList_GetItem(sres, x);
                if (grid == NULL)
                {
                    return NULL;
                }
                if (PyList_Append(res, grid) < 0)
                {
                    return NULL;
                }
            }
            if (self->e)
            {
                if (PyList_Append(sg, t->g))
                {
                    return NULL;
                }
            }
        }
    }

    if (self->e)
    {
        Py_DECREF(self->g);
        self->g = Py_BuildValue("iO", self->n, sg);
    }

    return res;
}

#ifdef DEBUG
static int
SuDoKu__print_graph(PyObject *g)
{
    return SuDoKu__print_graph_aux(g, "");
}

static int
SuDoKu__print_graph_aux(PyObject *g, char *p)
{
    return 0;
}
#endif

static int
SuDoKu__graph_len(PyObject *g)
{
    return SuDoKu__graph_len_aux(g, 0);
}

static int
SuDoKu__graph_len_aux(PyObject *g, int d)
{
    return 0;
}

static int
SuDoKu__graph_forks(PyObject *g)
{
    return 0;
}

static int
SuDoKu__unique_sol_aux(SuDoKu *self)
{
    SuDoKu *t;
    int i, n, count, scount;

    if (self->n == 81)
    {
        return 1;
    }

    i = SuDoKu__search_min(self);

    t = (SuDoKu*)PyType_GenericNew(&SuDoKuType, NULL, NULL);

    count = 0;
    for (n = 1; n < 10; n++)
    {
        if ((self->p[i] >> n) & 1)
        {
            SuDoKu__copy(self, t);
            if (SuDoKu__mark(t, i, n) == -2)
            {
                continue;
            }
            scount = SuDoKu__unique_sol_aux(t);
            if (scount == -2)
            {
                return -2;
            }
            count += scount;
            if (count > 1)
            {
                return -2;
            }
        }
    }
    return count;
}

static int
SuDoKu__unique_sol(SuDoKu *self)
{
    int i;

    SuDoKu__reset(self);

    for (i = 0; i < 81; i++)
    {
        if (self->o[i] > 0)
        {
            SuDoKu__mark(self, i, self->o[i]);
        }
    }

    return SuDoKu__unique_sol_aux(self) != -2;
}

static int
SuDoKu__from_string(SuDoKu *self, const char *s, const int l)
{
    int i, k;
    char c;
    char err_msg[32];

    i = 0;
    for (k = 0; k < l; k++)
    {
        c = s[k];
        if (c == '\n' || c == '\r')
        {
            // ignore non-significant characters
            continue;
        }
        else if (i >= 81)
        {
            // must be checked here to allow trailing whitespace
            break;
        }
        else if (c >= '1' && c <= '9')
        {
            self->o[i] = (int)c - (int)'0';
        }
        else if (c == '_' || c == '-' || c == ' ' || c == '.' || c == '0')
        {
            // nothing to do
        }
        else
        {
            PyOS_snprintf(err_msg, 32, "Invalid character: %c.", c);
            PyErr_SetString(PyExc_ValueError, err_msg);
            return -1;
        }
        i += 1;
    }
    if (i < 81)
    {
        PyErr_SetString(PyExc_ValueError, "Bad input: not enough data.");
        return -1;
    }
    if (k < l)
    {
        PyErr_SetString(PyExc_ValueError, "Bad input: too much data.");
        return -1;
    }
    return 0;
}

static int
SuDoKu__to_console(SuDoKu *self, const int *v, char *s)
{
    int i, j, k;
    char *sep = " --- --- --- --- --- --- --- --- --- \n";
    char *lin = "|   |   |   |   |   |   |   |   |   |\n";
    char *p1, *p2;

    p1 = stpcpy(s, sep);
    for (i = 0; i < 9; i++)
    {
        p2 = stpcpy(p1, lin);
        for (j = 0; j < 9; j++)
        {
            k = v[9 * i + j];
            if (k >= 1 && k <= 9)
            {
                p1[4 * j + 2] = (char)(k + (int)'0');
            }
        }
        p1 = stpcpy(p2, sep);
    }
    p1[-1] = '\0'; // remove the last \n
    return 0;
}

static int
SuDoKu__to_html(SuDoKu *self, const int *v, char *s)
{
    int i, j, k;
    char *p;

    p = stpcpy(s, "<table class=\"sudoku\">");
    for (i = 0; i < 9; i++)
    {
        p = stpcpy(p, "<tr>");
        for (j = 0; j < 9; j++)
        {
            p = stpcpy(p, "<td>");
            k = v[9 * i + j];
            if (k == 0)
            {
                p = stpcpy(p, "&nbsp;");
            }
            if (k >= 1 && k <= 9)
            {
                p[0] = (char)(k + (int)'0');
                p[1] = '\0';
                p = &p[1];
            }
            p = stpcpy(p, "</td>");
        }
        p = stpcpy(p, "</tr>");
    }
    p = stpcpy(p, "</table>");
    return 0;
}

static int
SuDoKu__to_string(SuDoKu *self, const int *v, char *s)
{
    int i;

    for (i = 0; i < 81; i++)
    {
        if (v[i] == 0)
        {
            s[i] = '_';
        }
        else if (v[i] >= 1 && v[i] <= 9)
        {
            s[i] = (char)(v[i] + (int)'0');
        }
        else
        {
            PyErr_SetString(PyExc_ValueError, "Invalid value in grid.");
            return -1;
        }
    }
    return 0;
}


/******************************************************************************/

#ifdef DEBUG
static PyObject*
SuDoKu_debug(SuDoKu *self, PyObject *args)
{
    const char *msg = NULL;

    if (!PyArg_ParseTuple(args, "s", &msg))
    {
        return NULL;
    }

    PySys_WriteStdout("%s\n", msg);

    Py_RETURN_NONE;
}
#endif

static PyObject*
SuDoKu_resolve(SuDoKu *self)
{
    int i;

    /* Step 0 */
    SuDoKu__reset(self);

    /* Step 1 */
    for (i = 0; i < 81; i++)
    {
        if (self->o[i] > 0)
        {
            if (SuDoKu__mark(self, i, self->o[i]) == -2)
            {
                return NULL;
            }
        }
    }

    /* Step 2 */
    return SuDoKu__resolve_aux(self);
}

static PyObject*
SuDoKu_estimate(SuDoKu *self)
{
    int l, f;

    if (!self->e || self->g == NULL)
    {
        Py_RETURN_NONE;
    }
#ifdef DEBUG
    if (self->d)
    {
        SuDoKu__print_graph(self->g);
    }
#endif

    l = SuDoKu__graph_len(self->g);
    f = SuDoKu__graph_forks(self->g);
    return Py_BuildValue("di", log((double)l / 81.0) + 1.0, f);
}

static PyObject*
SuDoKu_generate(SuDoKu *self)
{
    int i, j, order[81], count, n, ok;

    /* Step 0 */
    SuDoKu__reset(self);

    /* Step 1 */
#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("Shuffling positions...\n");
    }
#endif
    srandomdev();
    for (i = 0; i < 81; i++)
    {
        j = random() % (i + 1);
        order[i] = order[j];
        order[j] = i;
    }
#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("    Done.\n");
    }
#endif

    /* Step 2 */
#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("Generating a random grid...\n");
    }
#endif
    count = 0;
    while (1)
    {
        count += 1;
        SuDoKu__reset(self);
        ok = 1;
        for (i = 0; i < 81; i++)
        {
            if (self->v[order[i]] == 0)
            {
                n = 0;
                j = (random() % self->c[order[i]]) + 1;
                while (j > 0)
                {
                    n += 1;
                    if ((self->p[order[i]] >> n) & 1)
                    {
                        j -= 1;
                    }
                }
                if (SuDoKu__mark(self, order[i], n) == -2)
                {
                    ok = 0;
                    break;
                }
            }
        }
        if (ok)
        {
            break;
        }
    }
#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("    Found a grid after %d tries.\n", count);
    }
#endif

    /* Step 3 */
#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("Minimizing problem...\n");
    }
#endif
    memcpy(self->o, self->v, 81 * sizeof(int));
    for (i = 0; i < 81; i++)
    {
        n = self->o[order[i]];
        self->o[order[i]] = 0;
        if (SuDoKu__unique_sol(self))
        {
#ifdef DEBUG
            if (self->d)
            {
                PySys_WriteStdout("    Removing %d at (%d, %d)\n", n, order[i] / 9, order[i] % 9);
            }
#endif
        }
        else
        {
            self->o[order[i]] = n;
#ifdef DEBUG
            if (self->d)
            {
                PySys_WriteStdout("    Keeping %d at (%d, %d)\n", n, order[i] / 9, order[i] % 9);
            }
#endif
        }
    }

#ifdef DEBUG
    if (self->d)
    {
        PySys_WriteStdout("    Done.\n");
    }
#endif

    Py_RETURN_NONE;
}

static PyObject*
SuDoKu_from_string(SuDoKu *self, PyObject *args)
{
    int l = 0;
    const char *s = NULL;

    if (!PyArg_ParseTuple(args, "s#", &s, &l))
    {
        return NULL;
    }

    if (SuDoKu__from_string(self, s, l) < 0)
    {
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject*
SuDoKu_to_string(SuDoKu *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"format", "values", NULL};
    const char *format = "string";
    PyObject *values = NULL;
    int cvalues[81];
    int coutlen;
    static int (*formatter)(SuDoKu *self, const int *v, char *s);
    char err_msg[32];
    char *coutput = NULL;
    PyObject *output = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|sO", kwlist, &format, &values))
    {
        return NULL;
    }

    if (values == NULL)
    {
        memcpy(cvalues, self->o, 81 * sizeof(int));
    }
    else
    {
        SuDoKu_set2darray(cvalues, values);
    }

    if (strcmp(format, "console") == 0)
    {
        coutlen = 19 /* lines */ * 38 /* columns */ + 1 /* \0 */;
        formatter = SuDoKu__to_console;
    }
    else if (strcmp(format, "html") == 0)
    {
        coutlen = 9 /* rows */ * 144 /* max row len */ + 30 + 1 /* \0 */;
        formatter = SuDoKu__to_html;
    }
    else if (strcmp(format, "string") == 0)
    {
        coutlen = 81 /* characters */ + 1 /* \0 */;
        formatter = SuDoKu__to_string;
    }
    else
    {
        PyOS_snprintf(err_msg, 32, "Invalid format: %s.", format);
        PyErr_SetString(PyExc_ValueError, err_msg);
        return NULL;
    }

    coutput = (char *)calloc(coutlen, sizeof(char));
    if (coutput == NULL)
    {
        return PyErr_NoMemory();
    }

    if (formatter(self, cvalues, coutput) >= 0)
    {
        output = PyString_FromString(coutput);
    }

    free(coutput);
    return output;
}

/******************************************************************************/

static PyObject*
SuDoKu_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SuDoKu* self;

    self = (SuDoKu*)type->tp_alloc(type, 0);

    if (self != NULL)
    {
        self->e = 1;
#ifdef DEBUG
        self->d = 0;
#endif
    }

    return (PyObject*)self;
}

static int
SuDoKu_init(SuDoKu *self, PyObject *args, PyObject *kwds)
{
    const char *problem = NULL;
    int len = 0;

#ifdef DEBUG
    static char *kwlist[] = {"problem", "estimate", "debug", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s#bb", kwlist,
                                     &problem, &len, &self->e, &self->d))
#else
    static char *kwlist[] = {"problem", "estimate", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s#b", kwlist,
                                     &problem, &len, &self->e))
#endif
    {
        return -1;
    }

    if (problem != NULL)
    {
        if (SuDoKu__from_string(self, problem, len) < 0)
        {
            return -1;
        }
    }

    return 0;
}

static int
SuDoKu_traverse(SuDoKu *self, visitproc visit, void *arg)
{
    Py_VISIT(self->g);
    return 0;
}

static int 
SuDoKu_clear(SuDoKu *self)
{
    Py_CLEAR(self->g);
    return 0;
}

static void
SuDoKu_dealloc(SuDoKu *self)
{
    Py_CLEAR(self->g);
    self->ob_type->tp_free((PyObject*)self);
}

/* Returns a new reference */
static PyObject *
SuDoKu_get2darray(int *a)
{
    PyObject *v, *r, *c; /* values, row, cell */
    int i, j;

    v = PyList_New(9);
    if (v == NULL)
    {
        return NULL;
    }
    for (i = 0; i < 9; i++)
    {
        r = PyList_New(9);
        if (r == NULL)
        {
            Py_DECREF(v);
            return NULL;
        }
        for (j = 0; j < 9; j++)
        {
            c = PyInt_FromLong(a[9 * i + j]);
            if (c == NULL)
            {
                Py_DECREF(v);
                Py_DECREF(r);
                return NULL;
            }
            PyList_SET_ITEM(r, j, c);
        }
        PyList_SET_ITEM(v, i, r);
    }
    return v;
}

static int
SuDoKu_set2darray(int *a, PyObject *v)
{
    PyObject *r, *c; /* row, cell */
    int i, j;

    if (v == NULL || !PyList_Check(v) || PyList_Size(v) != 9)
    {
        return -1;
    }
    for (i = 0; i < 9; i++)
    {
        r = PyList_GetItem(v, i);
        if (r == NULL || !PyList_Check(r) || PyList_Size(r) != 9)
        {
            return -1;
        }
        for (j = 0; j < 9; j++)
        {
            c = PyList_GetItem(r, j);
            if (c == NULL || !PyInt_Check(c))
            {
                return -1;
            }
            a[9 * i + j] = (int)PyInt_AsLong(c);
        }
    }
    return 0;
}

static PyObject *
SuDoKu_getv(SuDoKu *self, void *closure)
{
    return SuDoKu_get2darray(self->v);
}

static int
SuDoKu_setv(SuDoKu *self, PyObject *value, void *closure)
{
    return SuDoKu_set2darray(self->v, value);
}

static PyObject *
SuDoKu_geto(SuDoKu *self, void *closure)
{
    return SuDoKu_get2darray(self->o);
}

static int
SuDoKu_seto(SuDoKu *self, PyObject *value, void *closure)
{
    return SuDoKu_set2darray(self->o, value);
}

/******************************************************************************/

PyMODINIT_FUNC
initcsudoku(void)
{
    PyObject *d, *m;

    if (PyType_Ready(&SuDoKuType) < 0) return;

    // create SuDoKu_Contradiction
    d = Py_BuildValue("{ss}", "__doc__",
                              "Contradiction in input, no solution exists.");
    if (d == NULL) return;

    SuDoKu_Contradiction = PyErr_NewException("csudoku.Contradiction", NULL, d);
    Py_DECREF(d);
    if (SuDoKu_Contradiction == NULL) return;

    // initialize module
    m = Py_InitModule3("csudoku", module_methods,
                       "SuDoKu generator and solver (C implementation).");
    if (m == NULL) return;

    // insert a new reference to objects in the module dictionnary
    Py_INCREF(&SuDoKuType);
    if (PyModule_AddObject(m, "SuDoKu", (PyObject *)&SuDoKuType) < 0)
    {
        Py_DECREF(&SuDoKuType);
    }
    Py_INCREF(SuDoKu_Contradiction);
    if (PyModule_AddObject(m, "Contradiction", SuDoKu_Contradiction) < 0)
    {
        Py_DECREF(SuDoKu_Contradiction);
    }
}