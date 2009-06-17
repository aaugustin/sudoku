#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin

from distutils.core import setup, Extension

setup(
    name='csudoku',
    version='2.0',
    author='Aymeric Augustin',
    author_email='aymeric.augustin@m4x.org',
    description='SuDoKu generator and solver',
    scripts=['sudoku'],
    py_modules=['sudoku'],
    ext_modules=[Extension('csudoku', ['csudoku.c'])],
)
