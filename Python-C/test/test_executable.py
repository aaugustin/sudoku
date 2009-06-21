#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin


"""Comparative tests of the Python and C implementations."""


import glob, os, os.path, subprocess

TESTS = (
    ([], ''),
)
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
POPENOPTIONS = {
    'bufsize': 1,
    'executable': 'bin/sudoku',
    'stdin': subprocess.PIPE,
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE,
    'cwd': BASEDIR,
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
            raise OSError('compiled module csudoku.so exists and is not a symlink')
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
    py_results = []
    select_implementation('Python')
    for args, stdin in TESTS:
        p = subprocess.Popen(args, **POPENOPTIONS)
        py_results.append(p.communicate(stdin))
    c_results = []
    select_implementation('C')
    for args, stdin in TESTS:
        p = subprocess.Popen(args, **POPENOPTIONS)
        c_results.append(p.communicate(stdin))
    success = failure = 0
    for i, (py_result, c_result) in enumerate(zip(py_results, c_results)):
        if py_result == c_result:
            success += 1
        else:
            failure += 1
            print "Test %d failed."
            print "  Python output:", py_result
            print "  C output:     ", c_result
    if failure == 0:
        print "All tests passed (success=%d)." % success
    else:
        print "Some tests failed (success=%d, failure=%d)." % (success, failure)

if __name__ == '__main__':
    run_tests()
