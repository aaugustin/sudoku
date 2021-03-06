SuDoKu solver and generator
===========================

This program is a command-line utility to resolve and generate SuDoKu grids.

Installation
------------

Python >= 2.6 or >= 3.2 is required.

Run in a virtualenv (or as root for a systemwide install):

    $ make install

Usage
-----

To obtain detailed usage information, run:

    $ sudoku --help

When resolving a SuDoKu, the grid can be specified as an argument, on the
standard input, or in a file with the `--input` option. Known cells in the
grid are represented by the corresponding figure, empty cells by one these
characters: underscore, dash, space, dot, zero, and line breaks are ignored.
If there are several solutions to the grid, all of them are shown.

When generating a SuDoKu, no arguments are necessary. It is possible to
generate several grids at a time with the `--count` option.

If the `--estimate` option is set, an estimation of the difficulty of the grid
is printed. The estimation is a `(float, int)` pair and the figures are the
resolution time for a human and for a computer, respectively. Difficulty for
a human starts at 1 and is generally stays below 6, although no upper limit
is enforced. Difficulty for a computer is the number of resolution steps
required by the algorithm used in the program.

The output format in which the grids are displayed can be selected with the
`--format` option.

The `--debug` option is only available when using the Python implementation or
when the C implementation is compiled in debug mode.

Demo
----

Run:

    $ make demo


Tests
-----

The following tests can be run:

    $ make test         # Unit tests and comparison of the two implementations
    $ make test-cover   # Code coverage of tests on the Python implementation
    $ make test-memory  # Check for reference leaks in the C implementatino

If the test fail, run `make clean` and retry.

Programmer API
--------------

Internally, a Python module called `sudoku` is defined. Both a pure Python and
an equivalent C implementation are available for this module. It contains two
objects: a `SuDoKu` class and a `Contradiction` exception. The `sudoku` module will
automatically use the best implementation available. Public methods of the
SuDoKu class are documented in `sudoku/pysudoku.py`.

Copyright
---------

Copyright (c) 2008-2014 Aymeric Augustin. All rights reserved.
