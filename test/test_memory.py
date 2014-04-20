#!/usr/bin/env python
# Copyright (c) 2008-2014 Aymeric Augustin

"""Memory debugging script for the C implementation."""

import os.path
import sys
sys.path[:0] = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))]
from sudoku import SuDoKu
from guppy import hpy

with open(os.path.join(os.path.dirname(__file__), 'hardest_sudoku.sdk')) as f:
    problem = f.read()


def run_tests():
    hpy().heapu() # pre-heating
    print('\n========   begin    ========\n')
    print(hpy().heapu())
    print('\n========    init    ========\n')
    s = SuDoKu()
    print(hpy().heapu())
    print('\n========    read    ========\n')
    s.from_string(problem)
    print(hpy().heapu())
    print('\n========  resolve   ========\n')
    s.resolve()
    print(hpy().heapu())
    print('\n========  generate  ========\n')
    s.generate()
    print(hpy().heapu())
    print('\n========    end     ========\n')


if __name__ == '__main__':
    run_tests()
