#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin

from distutils.core import setup, Extension

setup(
    name="csudoku",
    version="1.0",
    ext_modules=[Extension("csudoku", ["csudoku.c"])]
)
