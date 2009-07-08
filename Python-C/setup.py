#!/usr/bin/env python
# Copyright (c) 2008-2009 Aymeric Augustin

import sys
from distutils.core import setup, Extension

define_macros = []
if '--debug' in sys.argv:
    define_macros.append(('DEBUG', None))

setup(
    name='csudoku',
    version='2.0',
    author='Aymeric Augustin',
    author_email='aymeric.augustin@m4x.org',
    url='http://myks.org/',
    description='SuDoKu generator and solver',
    scripts=['bin/sudoku'],
    py_modules=['sudoku.pysudoku'],
    ext_modules=[Extension('sudoku.csudoku',
                           ['sudoku/csudoku.c'],
                           define_macros=define_macros)],
)
