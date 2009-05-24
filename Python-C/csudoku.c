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

#include "csudoku.h"

/******************************************************************************/

static int
CSuDoKu__reset(CSuDoKu *self)
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
    
    /* statistics */
    self->n = 0;
    Py_XDECREF(self->g);
    Py_INCREF(Py_None);
    self->g = Py_None;
    
    return 0;
}

static int
CSuDoKu__copy(CSuDoKu *self, CSuDoKu *t)
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
    Py_XDECREF(t->g);
    Py_INCREF(Py_None);
    t->g = Py_None;
    t->d = self->d;
    return 0;
}

static int
CSuDoKu__mark(CSuDoKu *self, int i, int n)
{
    int *rel, p, j;
    
    if (self->v[i] == n)
    {
        return 0;
    }
    if (!((self->p[i] >> n) & 1))
    {
        if (self->d)
        {
            printf("    Attempt to assign %d at (%d, %d) which is forbidden\n", n, i / 9, i % 9);
        }
        Py_DECREF(self->g);
        self->g = Py_BuildValue("ic", self->n, '-');
        return -2;
    }
    
    self->v[i] = n;
    self->n += 1;
    self->p[i] = 0;
    self->c[i] = 0;
    
    rel = CSuDoKu_relations[i];
    for (j = 0; j < 20; j++)
    {
        if (CSuDoKu__eliminate(self, rel[j], n) == -2)
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
        if (CSuDoKu__mark(self, i, n) == -2)
        {
            return -2;
        }
    }
    return 0;
}

static int
CSuDoKu__eliminate(CSuDoKu *self, int i, int n)
{
    if ((self->p[i] >> n) & 1)
    {
        self->p[i] &= 1022 - (1 << n);
        self->c[i] -= 1;
        if (self->c[i] == 0)
        {
            if (self->d)
            {
                printf("    Impossibility at (%d, %d), search depth = %d\n", i / 9, i % 9, self->n);
            }
            Py_DECREF(self->g);
            self->g = Py_BuildValue("ic", self->n, '-');
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
CSuDoKu__searchMin(CSuDoKu *self)
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
CSuDoKu__resolveAux(CSuDoKu *self)
{
    PyObject *res, *sres, *grid, *sg;
    CSuDoKu *t;
    int i, n, x;
    
    res = PyList_New(0);
    if (res == NULL)
    {
        Py_DECREF(res);
        return NULL;
    }
    
    if (self->n == 81)
    {
        if (self->d)
        {
            printf("    Found a solution: ");
            for (i = 0; i < 81; i++)
            {
                printf("%d", self->v[i]);
            }
            printf("\n");
        }
        Py_DECREF(self->g);
        self->g = Py_BuildValue("ic", self->n, '+');
        if (PyList_Append(res, CSuDoKu_get2dArray(self->v)) < 0)
        {
            return NULL;
        }
        return res;
    }
    
    i = CSuDoKu__searchMin(self);
    
    t = (CSuDoKu*)PyType_GenericNew(&CSuDoKuType, NULL, NULL);
    
    sg = PyList_New(0);
    if (sg == NULL)
    {
        Py_DECREF(sg);
        return NULL;
    }
    
    for (n = 1; n < 10; n++)
    {
        if ((self->p[i] >> n) & 1)
        {
            if (self->d)
            {
                printf("Trying %d at (%d, %d), search depth = %d\n", n, i / 9, i % 9, self->n);
            }
            CSuDoKu__copy(self, t);
            if (CSuDoKu__mark(t, i, n) == -2)
            {
                if (PyList_Append(sg, t->g))
                {
                    return NULL;
                }
                continue;
            }
            sres = CSuDoKu__resolveAux(t);
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
            if (PyList_Append(sg, t->g))
            {
                return NULL;
            }
        }
    }
    
    Py_DECREF(self->g);
    self->g = Py_BuildValue("iO", self->n, sg);
    
    return res;
}

static int
CSuDoKu__uniqueSolAux(CSuDoKu *self)
{
    CSuDoKu *t;
    int i, n, count, scount;
    
    if (self->n == 81)
    {
        return 1;
    }
    
    i = CSuDoKu__searchMin(self);
    
    t = (CSuDoKu*)PyType_GenericNew(&CSuDoKuType, NULL, NULL);
    
    count = 0;
    for (n = 1; n < 10; n++)
    {
        if ((self->p[i] >> n) & 1)
        {
            CSuDoKu__copy(self, t);
            if (CSuDoKu__mark(t, i, n) == -2)
            {
                continue;
            }
            scount = CSuDoKu__uniqueSolAux(t);
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
CSuDoKu__uniqueSol(CSuDoKu *self)
{
    int i;
    
    CSuDoKu__reset(self);
    
    for (i = 0; i < 81; i++)
    {
        if (self->o[i] > 0)
        {
            CSuDoKu__mark(self, i, self->o[i]);
        }
    }
    
    return CSuDoKu__uniqueSolAux(self) != -2;
}

/******************************************************************************/

static PyObject*
CSuDoKu_debug(CSuDoKu *self, PyObject *args)
{
    const char *msg;
    
    if (!PyArg_ParseTuple(args, "s", &msg))
    {
        return NULL;
    }
    
    if (printf("%s\n", msg) < 0)
    {
        PyErr_SetString(PyExc_IOError, "Unable to print debug info");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject*
CSuDoKu_markInput(CSuDoKu *self, PyObject *args)
{
    int i, j, n;
    
    if (!PyArg_ParseTuple(args, "iii", &i, &j, &n))
    {
        return NULL;
    }
    
    self->o[9 * i + j] = n;
    
    Py_RETURN_NONE;
}

static PyObject*
CSuDoKu_resolve(CSuDoKu *self)
{
    int i;
    
    /* Step 0 */
    CSuDoKu__reset(self);
    
    /* Step 1 */
    for (i = 0; i < 81; i++)
    {
        if (self->o[i] > 0)
        {
            CSuDoKu__mark(self, i, self->o[i]);
        }
    }
    
    /* Step 2 */
    return CSuDoKu__resolveAux(self);
}

static PyObject*
CSuDoKu_generate(CSuDoKu *self)
{
    int i, j, order[81], count, n, ok;
    
    /* Step 0 */
    CSuDoKu__reset(self);
    
    /* Step 1 */
    if (self->d)
    {
        printf("Shuffling positions...\n");
    }
    srandomdev();
    for (i = 0; i < 81; i++)
    {
        j = random() % (i + 1);
        order[i] = order[j];
        order[j] = i;
    }
    if (self->d)
    {
        printf("    Done.\n");
    }
    
    /* Step 2 */
    if (self->d)
    {
        printf("Generating a random grid...\n");
    }
    count = 0;
    while (1)
    {
        count += 1;
        CSuDoKu__reset(self);
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
                if (CSuDoKu__mark(self, order[i], n) == -2)
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
    if (self->d)
    {
        printf("    Found a grid after %d tries.\n", count);
    }
    
    /* Step 3 */
    if (self->d)
    {
        printf("Minimizing problem...\n");
    }
    memcpy(self->o, self->v, 81 * sizeof(int));
    for (i = 0; i < 81; i++)
    {
        n = self->o[order[i]];
        self->o[order[i]] = 0;
        if (CSuDoKu__uniqueSol(self))
        {
            if (self->d)
            {
                printf("    Removing %d at (%d, %d)\n", n, order[i] / 9, order[i] % 9);
            }
        }
        else
        {
            self->o[order[i]] = n;
            if (self->d)
            {
                printf("    Keeping %d at (%d, %d)\n", n, order[i] / 9, order[i] % 9);
            }
        }
    }
    
    if (self->d)
    {
        printf("    Done.\n");
    }
    
    Py_RETURN_NONE;
}


/******************************************************************************/

static void
CSuDoKu_dealloc(CSuDoKu *self)
{
    Py_XDECREF(self->g);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject*
CSuDoKu_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CSuDoKu* self;
    
    self = (CSuDoKu*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->d = 0;
    }
    
    return (PyObject*)self;
}

static int
CSuDoKu_init(CSuDoKu *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"debug", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &self->d))
    {
        return -1;
    }
    
    return 0;
}

static PyObject *
CSuDoKu_get2dArray(int *a)
{
    PyObject *v, *r, *c; /* values, row, cell */
    int i, j;
    
    v = PyList_New(9);
    if (v == NULL)
    {
        Py_DECREF(v);
        return NULL;
    }
    for (i = 0; i < 9; i++)
    {
        r = PyList_New(9);
        if (r == NULL)
        {
            Py_DECREF(v);
            Py_DECREF(r);
            return NULL;
        }
        for (j = 0; j < 9; j++)
        {
            c = PyInt_FromLong(a[9 * i + j]);
            if (c == NULL)
            {
                Py_DECREF(v);
                Py_DECREF(r);
                Py_DECREF(c);
                return NULL;
            }
            PyList_SET_ITEM(r, j, c);
        }
        PyList_SET_ITEM(v, i, r);
    }
    return v;
}

static int
CSuDoKu_set2dArray(int *a, PyObject *v)
{
    PyObject *r, *c;
    int i, j;
    
    if (!PyList_Check(v) || PyList_Size(v) != 9)
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
CSuDoKu_getv(CSuDoKu *self, void *closure)
{
    return CSuDoKu_get2dArray(self->v);
}

static int
CSuDoKu_setv(CSuDoKu *self, PyObject *value, void *closure)
{
    return CSuDoKu_set2dArray(self->v, value);
}

static PyObject *
CSuDoKu_geto(CSuDoKu *self, void *closure)
{
    return CSuDoKu_get2dArray(self->o);
}

static int
CSuDoKu_seto(CSuDoKu *self, PyObject *value, void *closure)
{
    return CSuDoKu_set2dArray(self->o, value);
}

/******************************************************************************/

PyMODINIT_FUNC
initcsudoku(void) 
{
    PyObject* m;
    
    if (PyType_Ready(&CSuDoKuType) < 0)
        return;
    
    m = Py_InitModule3("csudoku", module_methods, "CSuDoKu module.");
    
    if (m == NULL)
        return;
    
    Py_INCREF(&CSuDoKuType);
    PyModule_AddObject(m, "CSuDoKu", (PyObject *)&CSuDoKuType);
    
    CSuDoKu_Contradiction = PyErr_NewException("csudoku.Contradiction", NULL, NULL);
    Py_INCREF(CSuDoKu_Contradiction);
    PyModule_AddObject(m, "Contradiction", CSuDoKu_Contradiction);
    
    CSuDoKu_MultipleSolutionsFound = PyErr_NewException("csudoku.MultipleSolutionsFound", NULL, NULL);
    Py_INCREF(CSuDoKu_MultipleSolutionsFound);
    PyModule_AddObject(m, "MultipleSolutionsFound", CSuDoKu_MultipleSolutionsFound);
}
