#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin


"""SuDoKu generator and solver"""


from __future__ import with_statement


import copy, math, random, sys
from optparse import OptionParser
from csudoku import CSuDoKu, Contradiction, MultipleSolutionsFound


class SuDoKu(CSuDoKu):

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
                raise ValueError, 'Invalid caracter: %s' % c
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

    def out(self, format='console', values=None):           #pragma: no cover
        if format in ('console', 'html', 'string'):
            print getattr(self, 'to_' + format)(values)
        else:
            raise ValueError, 'Invalid format: %s' % format

    def to_console(self, values=None):
        if values is None:
            values = self.o
        cells = [[str(c) for c in r] for r in values]
        rows = ['| ' + ' | '.join(r) + ' |\n' for r in cells]
        sep = '---'.join([' '] * 10)
        sepnl = sep + '\n'
        return (sepnl + sepnl.join(rows) + sep).replace('0', ' ')

    def to_html(self, values=None):
        if values is None:
            values = self.o
        cells = [['<td>' + str(c) + '</td>' for c in r] for r in values]
        rows = ['<tr>' + ''.join(r) + '</tr>' for r in cells]
        table = '<table class="sudoku">' + ''.join(rows) + '</table>'
        return table.replace('0', '&nbsp;')

    def to_string(self, values=None):
        if values is None:
            values = self.o
        s =''.join([''.join([str(c) for c in r]) for r in values])
        s = s.replace('0', '_')
        return s


if __name__ == '__main__':                                  #pragma: no cover

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
            s.out(options.format, grid)
        if options.estimate:
            print s.estimate()

    if options.generate:
        for i in range(options.count or 1):
            s.generate()
            s.out(options.format)
            if options.estimate:
                s.resolve()
                print s.estimate()

    if options.show:
        s.out(options.format)
