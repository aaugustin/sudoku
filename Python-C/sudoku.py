#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin


"""SuDoKu generator and solver"""


from __future__ import with_statement

import copy, math, random, sys
from optparse import OptionParser
from csudoku import SuDoKu, Contradiction


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

if __name__ == '__main__':
    main()
