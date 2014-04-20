#!/usr/bin/env python
# Copyright (c) 2008-2014 Aymeric Augustin

"""Command-line interface for the SuDoKu solver and generator.

If the C version of the SuDoKu class is available, it will be used. Otherwise,
the pure Python version will be used. This can be determined at runtime by
testing whether 'implementation' is set to 'C' or 'Python'.
"""

from __future__ import with_statement

import optparse
import os.path
import sys

try:
    from csudoku import SuDoKu, Contradiction
    implementation = 'C'
except ImportError:
    from pysudoku import SuDoKu, Contradiction
    implementation = 'Python'


# submodules are only an internal implementation choice
__all__ = ['SuDoKu', 'Contradiction']


def main():

    p = optparse.OptionParser(usage='usage: %s [options] [problem]'
                                    % os.path.basename(sys.argv[0]))

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
                 help='read problem from a file instead of args or stdin')
    p.add_option('-f', '--format',
                 default='console', dest='format', metavar='FMT',
                 help='output format: console (default), html, string')
    p.add_option('-c', '--count',
                 dest='count', type='int', metavar='CNT',
                 help='number of problems to generate')
    if hasattr(SuDoKu, 'debug'):
        p.add_option('-d', '--debug',
                     action='store_true', default=False, dest='debug',
                     help='enable verbose debug')
    (options, args) = p.parse_args()

    def exit_on_error(error): # Code factorization
        print error
        print
        p.print_help()
        sys.exit(2)

    # Create a SuDoKu object
    if hasattr(options, 'debug'):
        s = SuDoKu(estimate=options.estimate, debug=options.debug)
    else:
        s = SuDoKu(estimate=options.estimate)

    # Special case to enable a default behavior
    resolve_by_default = not any([options.resolve,
                                  options.generate,
                                  options.show])

    # Read problem if necessary
    if resolve_by_default or options.resolve or options.show:
        problem = ''
        if len(args) == 1:
            problem = args[0]
        elif options.filename != '':
            with open(options.filename) as filein:
                problem = filein.read()
        elif not sys.stdin.isatty():
            problem = sys.stdin.read()
        if problem:
            s.from_string(problem)
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
            grid = s.generate()
            print s.to_string(options.format, grid)
            if options.estimate:
                s.resolve()
                print s.estimate()

    if options.show:
        print s.to_string(options.format)
