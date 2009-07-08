#!/usr/bin/env python
# Copyright (c) 2008-2009 Aymeric Augustin

"""Comparative tests of the Python and C implementations."""

import difflib
import glob
import os
import os.path
import subprocess
import sys
import time

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SDKFILE = os.path.join(BASEDIR, 'test', 'test2.sdk')
SDK = open(SDKFILE).read()

TESTS = (
    ([], None),
    (['-h'], None),
    # Resolution options
    (['-r', SDK], None),
    (['-r', '-d', SDK], None),
    (['-r', '-e', SDK], None),
    (['-r', '-e', '-d', SDK], None),
    # Input from stdin, argument or file
    (['-s'], SDK),
    (['-s', SDK], None),
    (['-s', '-i', SDKFILE], None),
    # Outuput formats
    (['-s'], SDK),
    (['-s', '-f', 'console'], SDK),
    (['-s', '-f', 'html'], SDK),
    (['-s', '-f', 'string'], SDK),
)

POPENOPTIONS = {
    'bufsize': 1,
    'executable': 'bin/sudoku',
    'stdin': subprocess.PIPE,
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE,
    'cwd': BASEDIR,
    'env': {'PYTHONPATH': BASEDIR},
}


def select_implementation(implementation):
    dst = os.path.join(BASEDIR, 'sudoku', 'csudoku.so')
    if implementation == 'Python':
        if os.path.islink(dst):
            os.unlink(dst)
            return
        elif not os.path.exists(dst):
            return
        else:
            raise OSError('compiled module csudoku.so exists '
                          'and is not a symlink')
    elif implementation == 'C':
        src = os.path.join(BASEDIR, 'build', 'lib.*', 'sudoku', 'csudoku.so')
        gsrc = glob.glob(src)
        if len(gsrc) == 0:
            raise EnvironmentError('compiled module csudoku.so not found')
        elif len(gsrc) == 1:
            src = gsrc[0]
            os.symlink(src, dst)
        else:
            raise EnvironmentError('compiled module csudoku.so not unique')
    else:
        raise ValueError('available implementations are Python and C')


def run_tests():

    t = time.time()

    # Run the tests cases with the Python implementation
    py_results = []
    select_implementation('Python')
    for args, stdin in TESTS:
        p = subprocess.Popen(args, **POPENOPTIONS)
        py_results.append(p.communicate(stdin))
        sys.stdout.write('P')
        sys.stdout.flush()
    sys.stdout.write('\n')

    # Run the tests cases with the C implementation
    c_results = []
    select_implementation('C')
    for args, stdin in TESTS:
        p = subprocess.Popen(args, **POPENOPTIONS)
        c_results.append(p.communicate(stdin))
        sys.stdout.write('C')
        sys.stdout.flush()
    sys.stdout.write('\n')

    # Identify failures
    failures = []
    for i, (py_result, c_result) in enumerate(zip(py_results, c_results)):
        if py_result == c_result:
            sys.stdout.write('.')
            sys.stdout.flush()
        else:
            sys.stdout.write('F')
            sys.stdout.flush()
            failures.append((i, py_result, c_result))
    sys.stdout.write('\n')

    t = time.time() - t

    # Print failures
    for i, py_result, c_result in failures:
        print '=' * 70
        print "FAIL: test: %d %s." % (i, TESTS[i])
        print '-' * 70
        for line in difflib.unified_diff(
            py_result[0].split('\n'), c_result[0].split('\n'),
            fromfile='Python stdout', tofile='C stdout', lineterm=''):
            print line
        for line in difflib.unified_diff(
            py_result[1].split('\n'), c_result[1].split('\n'),
            fromfile='Python stderr', tofile='C stderr', lineterm=''):
            print line
        print

    # Print summary
    print '-' * 70
    print 'Ran %d tests in %.3fs' % (len(TESTS), t)
    print
    if failures:
        print "FAILED (failures=%d)" % len(failures)
    else:
        print "OK"


if __name__ == '__main__':
    run_tests()
