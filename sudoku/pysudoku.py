#!/usr/bin/env python
# Copyright (c) 2008-2014 Aymeric Augustin

"""SuDoKu generator and solver (pure Python implementation)."""

from __future__ import division

import copy
import math
import random


class Contradiction(Exception):
    """Contradiction in input, no solution exists."""


class _MultipleSolutionsFound(Exception):
    """More than one solution exists."""


class SuDoKu(object):

    def __init__(self, problem=None, estimate=True, debug=False):
        """Initialize a SuDoKu object.

        If problem is specified, the grid will be loaded from this argument.
        See from_string for a description of the format of this argument.

        If estimate is set to False, computations required for complexity
        estimation will be skipped.

        If debug is set to True, verbose debugging messages will be printed.
        """
        # Initial values: 1..9 or 0 = undefined
        self.o = [[0 for j in range(9)] for i in range(9)]
        if problem is not None:
            self.from_string(problem)
        # Estimate flag
        self.e = estimate
        # Debug flag
        self.d = debug

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return self.to_string()

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        args = []
        s = self.to_string()
        if s != 81 * '_':
            args.append('problem="%s"' % s)
        if not self.e:
            args.append('estimate=False')
        if self.d:
            args.append('debug=True')
        return "sudoku.SuDoKu(%s)" % ', '.join(args)

    def debug(self, msg):                                   #pragma: no cover
        """Print a debug message, only if the debug flag is set."""
        if self.d:
            print(msg)

    def _reset(self):
        # Resolution
        # Computed values: 1..9 or 0 = undefined
        self.v = [[0 for j in range(9)] for i in range(9)]
        # Possible values at each position: subset of 1..9
        self.p = [[list(range(1, 10)) for j in range(9)] for i in range(9)]
        # Queue of positions for which the value is known
        self.q = []
        # Number of known values
        self.n = 0

        # Statistics
        # Graph of resolution paths
        if self.e:
            self.g = None

    def _copy(self):
        # Copy the whole object, except the graph, which is not required
        # If self.e is False, there is no self.g anyway; it it is True,
        # store self.g in a temporary variable during the copy.
        if self.e:
            tmp_g = self.g
            self.g = None
        t = copy.deepcopy(self)
        if self.e:
            self.g = tmp_g
        return t

    # Resolution functions
    #---------------------

    def resolve(self):
        """Resolve a grid."""
        # Step 0: initialize for resolution
        self._reset()

        # Step 1: complete all trivial stuff
        for i in range(9):
            for j in range(9):
                if self.o[i][j] > 0:
                    self._mark(i, j, self.o[i][j])

        # Step 2: explore different paths
        return self._resolve_aux()

    def _mark(self, i, j, n):
        # Ignore if the position is already marked
        # This allows redundancy in the problems
        if self.v[i][j] == n:
            return
        # Check that the value is possible
        if self.p[i][j].count(n) == 0:
            self.debug('    Attempt to assign %d at (%d, %d)'
                       ' which is forbidden' % (n, i, j))
            if self.e:
                self.g = (self.n, '-')
            raise Contradiction
        # Record the value
        self.v[i][j] = n
        self.n += 1
        # Prevent further detection of a contradiction by _eliminate
        self.p[i][j] = []
        # Apply rules
        for k, l in SuDoKu._relations[i][j]:
            self._eliminate(k, l, n)
        # Apply recursively
        if len(self.q) > 0:
            i, j, n = self.q.pop(0)
            self._mark(i, j, n)

    def _eliminate(self, i, j, n):
        # Remove the element from the list of possible values
        try:
            self.p[i][j].remove(n)
        except ValueError:
            return

        # What follows is executed only when an element has actually been
        # removed from the list, e.g. no more than once for a value of
        # len(self.p[i][j])

        # If there's no possible value, we are on a wrong branch
        if len(self.p[i][j]) == 0:
            self.debug('    Impossibility at (%d, %d),'
                       ' search depth = %d' % (i, j, self.n))
            if self.e:
                self.g = (self.n, '-')
            raise Contradiction

        # If there's one possible value, add it to the queue for marking
        elif len(self.p[i][j]) == 1:
            self.q.append((i, j, self.p[i][j][0]))

    def _search_min(self):
        # Find the position with the smallest set of possible values
        im = jm = -1
        lm = 10
        for i in range(9):
            for j in range(9):
                if self.v[i][j] == 0 and len(self.p[i][j]) < lm:
                    im, jm, lm = i, j, len(self.p[i][j])
        return im, jm

    def _resolve_aux(self):
        # If the grid is complete, there is a unique solution
        if self.n == 81:
            self.debug('    Found a solution:'
                       ' %s' % self.to_string(values=self.v))
            if self.e:
                self.g = (self.n, '+')
            return [self.v]
        # Otherwise, look for the position that has the least alternatives,
        # and try each alternative by recursively calling ourself
        i, j = self._search_min()
        r = []
        if self.e:
            self.g = (self.n, [])
        for n in self.p[i][j]:
            self.debug('Trying %d at (%d, %d),'
                       ' search depth = %d' % (n, i, j, self.n))
            t = self._copy()
            try:
                t._mark(i, j, n)
            except Contradiction:
                if self.e:
                    self.g[1].append(t.g)
                continue
            r.extend(t._resolve_aux())
            if self.e:
                self.g[1].append(t.g)
        return r

    # Estimation functions
    #---------------------

    def estimate(self):
        """Estimate the difficulty of a grid.

        A tuple of two numbers is returned. The first one is an estimation
        of the complexity of the grid for a human being. The second one is
        the complexity for a computer, given the algorithm used in resolve.

        This method must only be called after resolve has been called with
        e set to True. Otherwise, it will return None.
        """
        if not self.e or not hasattr(self, 'g') or self.g is None:
            return
        if self.d:                                          #pragma: no cover
            self._print_graph()
        return (math.log(self._graph_len() / 81) + 1), self._graph_forks()

    def _print_graph(self, g=None, p=''):                   #pragma: no cover
        if g is None:
            g = self.g
        if isinstance(g[1], list):
            print('%s%02d' % (p, g[0]))
            for sg in g[1]:
                self._print_graph(sg, '  ' + p)
        else:
            print('%s%02d %s' % (p, g[0], g[1]))

    def _graph_len(self, g=None, d=0):
        if g is None:
            g = self.g
        l = g[0] - d
        if isinstance(g[1], list):
            for sg in g[1]:
                l += self._graph_len(sg, g[0])
        return l

    def _graph_forks(self, g=None):
        if g is None:
            g = self.g
        f = 0
        if isinstance(g[1], list):
            for sg in g[1]:
                f += self._graph_forks(sg) + 1
        return f

    # Generation functions
    #---------------------

    def generate(self):
        """Generate a random grid."""
        # Step 0: initialize for generation
        self._reset()
        e, self.e = self.e, False

        # Step 1: generate problem
        self.debug('Generating a random grid...')
        count = 0
        order = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(order)
        while True:
            try:
                count += 1
                self._reset()
                for i, j in order:
                    if self.v[i][j] > 0:
                        continue
                    else:
                        self._mark(i, j, random.choice(self.p[i][j]))
                break
            except Contradiction:
                continue
        self.debug('    Found a grid after %d tries.' % count)

        # Step 2: minimize problem
        self.debug('Minimizing problem...')
        for i in range(9):
            for j in range(9):
                self.o[i][j] = self.v[i][j]
        random.shuffle(order)
        for i, j in order:
            n = self.o[i][j]
            self.o[i][j] = 0
            if self._unique_sol():
                self.debug('    Removing %d at (%d, %d)' % (n, i, j))
            else:
                self.debug('    Keeping %d at (%d, %d)' % (n, i, j))
                self.o[i][j] = n
        self.debug('    Done.')

        self.e = e
        return self.o

    def _unique_sol(self):
        # Simplified version of resolve(self)
        self._reset()
        for i in range(9):
            for j in range(9):
                if self.o[i][j] > 0:
                    self._mark(i, j, self.o[i][j])
        try:
            self._unique_sol_aux()
            return True
        except _MultipleSolutionsFound:
            return False

    def _unique_sol_aux(self):
        # Simplified version of _resolve_aux(self)
        i, j = self._search_min()
        if i == -1:
            return 1
        else:
            count = 0
            for n in self.p[i][j]:
                t = self._copy()
                try:
                    t._mark(i, j, n)
                except Contradiction:
                    continue
                count += t._unique_sol_aux()
                if count > 1:
                    raise _MultipleSolutionsFound
            return count # == 0 or 1

    # Input functions
    #----------------

    def from_string(self, s):
        """Parse a string to load a grid.

        Non-empty cells are represented by a digit and empty cells by one of
        '_', '-', ' ', '.', and '0'. Line breaks are ignored.
        """
        i = j = 0
        for c in s:
            if c in '123456789':
                self.o[i][j] = int(c)
            elif c in '\n\r':
                continue
            elif c in '_- .0':
                pass
            else:
                raise ValueError('Invalid caracter: %s.' % c)
            if j < 8:
                j += 1
            else:
                i += 1
                j = 0
        if 9 * i + j < 81:
            raise ValueError('Bad input: not enough data.')
        if 9 * i + j > 81:
            raise ValueError('Bad input: too much data.')

    # Output functions
    #-----------------

    def to_string(self, format='string', values=None):
        """Format a grid and return a string.

        Available formats are:

        - console: console representation, suitable for humans,
        - string: compact representation, suitable for computers,
        - html: export format, suitable for the web.

        If values is specified, this grid will be displayed. Otherwise,
        the original grid of this instance will be used.
        """
        if format in ('console', 'html', 'string'):
            return getattr(self, '_to_' + format)(values or self.o)
        raise ValueError('Invalid format: %s.' % format)

    def _to_console(self, v):
        cells = [[str(c) for c in r] for r in v]
        rows = ['| ' + ' | '.join(r) + ' |\n' for r in cells]
        sep = '---'.join([' '] * 10) + '\n'
        return (sep + sep.join(rows) + sep).replace('0', ' ')

    def _to_html(self, v):
        cells = [['<td>' + str(c) + '</td>' for c in r] for r in v]
        rows = ['<tr>' + ''.join(r) + '</tr>' for r in cells]
        table = '<table class="sudoku">' + ''.join(rows) + '</table>'
        return table.replace('0', '&nbsp;')

    def _to_string(self, v):
        s =''.join([''.join([str(c) for c in r]) for r in v])
        s = s.replace('0', '_')
        return s

# Precompute relation map

def _related(i, j, k, l):
    if k == i and l == j:
        return False
    if k == i:
        return True
    if l == j:
        return True
    if k // 3 == i // 3 and l // 3 == j // 3:
        return True
    return False

SuDoKu._relations = [[[(k, l) for k in range(9) for l in range(9)
                              if _related(i, j, k, l)]
                     for j in range(9)] for i in range(9)]
