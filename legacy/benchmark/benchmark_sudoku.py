#!/usr/bin/env python
# Copyright (c) 2008-2014 Aymeric Augustin

"""Benchmarking script for the Python and C implementations."""

from __future__ import division
import gc
import os.path
import sys
import time

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path[:0] = [BASEDIR]

if len(sys.argv) == 2 and sys.argv[1] == 'C':
    from sudoku.csudoku import SuDoKu
    repeat_count = 10
elif len(sys.argv) == 2 and sys.argv[1] == 'Python':
    from sudoku.pysudoku import SuDoKu
    repeat_count = 1
else:
    print('Usage: %s [C|Python]' % os.path.basename(sys.argv[0]))
    sys.exit(2)

puzzles = os.path.join(BASEDIR, 'benchmark', '95_hard_puzzles')
stats = []
repeats = [None] * repeat_count
for problem in open(puzzles):
    # Disable GC during resolution to avoid artifacts
    gc.disable()
    t0 = time.time()
    for i in repeats:
        s = SuDoKu(problem, estimate=False)
        s.resolve()
    t1 = time.time()
    for i in repeats:
        s = SuDoKu(problem, estimate=True)
        s.resolve()
    t2 = time.time()
    gc.enable()
    l, f = s.estimate()
    stats.append(((t1 - t0) / repeat_count, (t2 - t1) / repeat_count, l, f))
    del s
    gc.collect()

print("test\ttime 1\ttime 2\tlevel\tforks")
print("-------------------------------------")
for i, (t1, t2, l, f) in enumerate(stats):
    print("%d\t%.4f\t%.4f\t%.4f\t%d" % (i + 1, t1, t2, l, f))
print("-------------------------------------")

times = [x[0] for x in stats]
print("Problems solved:     %d" % len(times))
print("Total time:          %.3f" % sum(times))
print("Problems / second:   %.3f" % (len(times) / sum(times)))
