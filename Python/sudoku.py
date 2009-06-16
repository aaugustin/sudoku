#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin


"""SuDoKu generator and solver"""


from __future__ import with_statement

import copy, math, random, sys
from optparse import OptionParser


class Contradiction(Exception):
    pass


class MultipleSolutionsFound(Exception):
    pass


class SuDoKu(object):

    # precompute relation map
    relations = [[[(k, l) for k in range(9) for l in range(9) if (k == i or l == j or (k // 3 == i // 3 and l // 3 == j // 3)) and not (k == i and l == j)] for j in range(9)] for i in range(9)]

    def __init__(self, problem=None, debug=False):
        # initial values: 1..9 or 0 = undefined
        self.o = [[0 for j in range(9)] for i in range(9)]
        if problem is not None:
            self.from_string(problem)
        # set to true to enable verbose debugging
        self.d = debug

    def debug(self, msg):                                   #pragma: no cover
        if self.d:
            print msg

    def reset(self):
        # Resolution
        # computed values: 1..9 or 0 = undefined
        self.v = [[0 for j in range(9)] for i in range(9)]
        # possible values at each position: subset of 1..9
        self.p = [[range(1, 10) for j in range(9)] for i in range(9)]
        # queue of positions for which the value is known
        self.q = []

        # Statistics
        # number of known values
        self.n = 0
        # graph of resolution paths
        self.g = None

    # Resolution functions
    #---------------------

    def mark(self, i, j, n):
        # Ignore if the position is already marked
        # This allows redundancy in the problems
        if self.v[i][j] == n:
            return
        # Check that the value is possible
        if self.p[i][j].count(n) == 0:
            self.debug('    Attempt to assign %d at (%d, %d) which is forbidden' % (n, i, j))
            self.g = (self.n, '-')
            raise Contradiction
        # Record the value
        self.v[i][j] = n
        self.n += 1
        # Prevent detection of a contradiction at this position
        self.p[i][j] = []
        # Apply rules
        for (k, l) in SuDoKu.relations[i][j]:
            self.eliminate(k, l, n)
        # Apply recursively
        if len(self.q) > 0:
            i, j, n = self.q.pop(0)
            self.mark(i, j, n)

    def eliminate(self, i, j, n):
        # Remove the element from the list of possible values
        try:
            self.p[i][j].remove(n)
        except ValueError:
            return
        # This is executed only when an element has actually been
        # removed from the list, e.g. no more than once for a value of
        # len(self.p[i][j])
        #
        # If there's no possible value, we are on a wrong branch
        if len(self.p[i][j]) == 0:
            self.debug('    Impossibility at (%d, %d), search depth = %d' % (i, j, self.n))
            self.g = (self.n, '-')
            raise Contradiction
        # If there's one possible value, we mark it
        elif len(self.p[i][j]) == 1:
            self.q.append((i, j, self.p[i][j][0]))

    def search_min(self):
        im = jm = -1
        lm = 10
        for i in range(9):
            for j in range(9):
                if self.v[i][j] == 0 and len(self.p[i][j]) < lm:
                    im = i
                    jm = j
                    lm = len(self.p[i][j])
        return im, jm

    def resolve_aux(self):
        # If the grid is complete
        if self.n == 81:
            self.debug('    Found a solution: %s' % self.to_string(values=self.v))
            self.g = (self.n, '+')
            return [self.v]
        # Otherwise look for the position that has the least alternatives
        i, j = self.search_min()
        # Try each alternative
        r = []
        self.g = (self.n, [])
        for n in self.p[i][j]:
            self.debug('Trying %d at (%d, %d), search depth = %d' % (n, i, j, self.n))
            t = copy.deepcopy(self)
            try:
                t.mark(i, j, n)
            except Contradiction:
                self.g[1].append(t.g)
                continue
            r.extend(t.resolve_aux())
            self.g[1].append(t.g)
        return r

    def resolve(self):
        # Step 0: initialize for resolution
        self.reset()

        # Step 1: complete all trivial stuff
        for i in range(9):
            for j in range(9):
                if self.o[i][j] > 0:
                    self.mark(i, j, self.o[i][j])

        # Step 2: explore different paths
        return self.resolve_aux()

    # Estimation functions
    #---------------------

    def print_graph(self, g=None, p=''):                    #pragma: no cover
        if g is None:
            g = self.g
        if isinstance(g[1], list):
            print p + str(g[0]).zfill(2)
            for sg in g[1]:
                self.print_graph(sg, '  ' + p)
        else:
            print p + str(g[0]).zfill(2) + ' ' + g[1]

    def graph_len(self, g=None, d=0):
        if g is None:
            g = self.g
        l = g[0] - d
        if isinstance(g[1], list):
            for sg in g[1]:
                l += self.graph_len(sg, g[0])
        return l

    def graph_forks(self, g=None):
        if g is None:
            g = self.g
        f = 0
        if isinstance(g[1], list):
            for sg in g[1]:
                f += self.graph_forks(sg) + 1
        return f

    def estimate(self):
        # Print resolution graph
        if self.d:                                          #pragma: no cover
            self.print_graph()
        # Compute "graph length"
        l = self.graph_len()
        return math.log(l / 81) + 1

    # Generation functions
    #---------------------

    def unique_sol_aux(self):
        # Based on resolve
        i, j = self.search_min()
        if i == -1:
            return 1
        else:
            count = 0
            for n in self.p[i][j]:
                t = copy.deepcopy(self)
                try:
                    t.mark(i, j, n)
                except Contradiction:
                    continue
                count += t.unique_sol_aux()
                if count > 1:
                    raise MultipleSolutionsFound
            return count

    def unique_sol(self):
        self.reset()
        for i in range(9):
            for j in range(9):
                if self.o[i][j] > 0:
                    self.mark(i, j, self.o[i][j])
        try:
            self.unique_sol_aux()
            return True
        except MultipleSolutionsFound:
            return False

    def generate(self):
        # Step 0: initialize for generation
        self.reset()

        # Step 1: generate problem
        self.debug('Generating a random grid...')
        count = 0
        order = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(order)
        while True:
            try:
                count += 1
                self.reset()
                for i, j in order:
                    if self.v[i][j] > 0:
                        continue
                    else:
                        self.mark(i, j, random.choice(self.p[i][j]))
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
            if self.unique_sol():
                self.debug('    Removing %d at (%d, %d)' % (n, i, j))
            else:
                self.debug('    Keeping %d at (%d, %d)' % (n, i, j))
                self.o[i][j] = n
        self.debug('    Done.')

    # Input functions
    #----------------

    def from_string(self, s):
        """Loads a problem from string s and stores it in self.o."""
        i = j = 0
        for c in s:
            if c in '123456789':
                self.o[i][j] = int(c)
            elif c in '\n\r':
                continue
            elif c in '_- .0':
                pass
            else:
                raise ValueError, 'Invalid caracter: %s.' % c
            if j < 8:
                j = j + 1
            else:
                i, j = i +1, 0
        if 9 * i + j < 81:
            raise ValueError, 'Bad input: not enough data.'
        if 9 * i + j > 81:
            raise ValueError, 'Bad input: too much data.'

    # Output funtions
    #----------------

    def to_string(self, format='string', values=None):
        if format in ('console', 'html', 'string'):
            return getattr(self, '_to_' + format)(values or self.o)
        raise ValueError, 'Invalid format: %s.' % format

    def _to_console(self, v):
        cells = [[str(c) for c in r] for r in v]
        rows = ['| ' + ' | '.join(r) + ' |\n' for r in cells]
        sep = '---'.join([' '] * 10)
        sepnl = sep + '\n'
        return (sepnl + sepnl.join(rows) + sep).replace('0', ' ')

    def _to_html(self, v):
        cells = [['<td>' + str(c) + '</td>' for c in r] for r in v]
        rows = ['<tr>' + ''.join(r) + '</tr>' for r in cells]
        table = '<table class="sudoku">' + ''.join(rows) + '</table>'
        return table.replace('0', '&nbsp;')

    def _to_string(self, v):
        s =''.join([''.join([str(c) for c in r]) for r in v])
        s = s.replace('0', '_')
        return s

# Main
#-----

def main():                                                 #pragma: no cover

    p = OptionParser(usage='usage: %prog [options] [problem]')
    # Actions
    p.add_option('-r', '--resolve',
                 action='store_true', default=False, dest='resolve',
                 help='resolve a problem (default)')
    p.add_option('-g', '--generate',
                 action='store_true', default=False, dest='generate',
                 help='generate a problem')
    p.add_option('-e', '--estimate',
                 action='store_true', default=False, dest='estimate',
                 help='estimate the difficulty of a problem')
    p.add_option('-s', '--show',
                 action='store_true', default=False, dest='show',
                 help='print a problem without resolving it')
    # Options
    p.add_option('-i', '--input',
                 default='', dest='filename', metavar='SDK',
                 help='read problem from a file instead of command line')
    p.add_option('-f', '--format',
                 default='console', dest='format', metavar='FMT',
                 help='output format: console (default), html, string')
    p.add_option('-c', '--count',
                 dest='count', type='int', metavar='CNT',
                 help='number of problems to generate')
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='enable verbose debug')
    (options, args) = p.parse_args()

    def exit_on_error(error):
        print error
        print
        p.print_help()
        sys.exit(1)

    resolve_by_default = not any([options.resolve, options.generate,
                                  options.estimate, options.show])

    # Read problem if necessary
    s = SuDoKu(debug=options.debug)
    if resolve_by_default or options.resolve or options.show:
        if len(args) == 1:
            s.from_string(args[0])
        elif options.filename == '-':
            s.from_string(sys.stdin.read())
        elif options.filename != '':
            with open(options.filename) as filein:
                s.from_string(filein.read())
        else:
            exit_on_error('Error: No problem specified.')

    # Check actions
    if resolve_by_default:
        options.resolve = True

    if (options.resolve and options.generate):
        exit_on_error('Incompatible options: --resolve and --generate.')

    if (options.resolve and options.show):
        exit_on_error('Incompatible options: --resolve and --show.')

    if (options.generate and options.show):
        exit_on_error('Incompatible options: --generate and --show.')

    if options.estimate and not (options.resolve or options.generate):
        exit_on_error('--estimate requires --resolve or --generate.')

    if options.count is not None and not options.generate:
        exit_on_error('--count requires --generate.')

    # Execute actions
    if options.resolve:
        for grid in s.resolve():
            print s.to_string(options.format, grid)
        if options.estimate:
            print s.estimate()

    if options.generate:
        for i in range(options.count or 1):
            s.generate()
            print s.to_string(options.format)
            if options.estimate:
                s.resolve()
                print s.estimate()

    if options.show:
        print s.to_string(options.format)

if __name__ == '__main__':                                  #pragma: no cover
    main()
