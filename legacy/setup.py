#!/usr/bin/env python
# Copyright (c) 2008-2014 Aymeric Augustin

import sys
from distutils.core import setup, Extension

define_macros = []
if '--debug' in sys.argv:
    define_macros.append(('DEBUG', None))

setup(
    name='sudoku',
    version='3.0',
    author='Aymeric Augustin',
    author_email='aymeric.augustin@m4x.org',
    url='http://myks.org/',
    license='Proprietary',
    description='SuDoKu generator and solver',
    long_description='This program is a command-line utility to resolve'
                     ' and generate SuDoKu grids.',
    platforms='All',
    scripts=['bin/sudoku'],
    py_modules=['sudoku.pysudoku'],
    ext_modules=[Extension('sudoku.csudoku',
                           ['sudoku/csudoku.c'],
                           define_macros=define_macros)],
)
