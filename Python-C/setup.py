#!/usr/bin/env python2.4

from distutils.core import setup, Extension

setup(
	name="csudoku",
	version="1.0",
	ext_modules=[Extension("csudoku", ["csudoku.c"])]
)