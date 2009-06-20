#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin

import os.path, sys, time
sys.path[:0] = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))]

if len(sys.argv) == 2 and sys.argv[1] == 'C':
    from sudoku.csudoku import SuDoKu
elif len(sys.argv) == 2 and sys.argv[1] == 'Python':
    from sudoku.pysudoku import SuDoKu
else:
    print 'Usage: %s [C|Python]' % os.path.basename(sys.argv[0])
    sys.exit(2)

puzzles = os.path.join(os.path.dirname(__file__), '95_hard_puzzles')
stats = []
for problem in open(puzzles):
    t = time.time()
    s = SuDoKu(problem)
    s.resolve()
    t = time.time() - t
    l, f = s.estimate()
    stats.append((t, l, f))

print "test\ttime\tlevel\tforks"
print "-----------------------------"
for i, (t, l, f) in enumerate(stats):
    print "%d\t%.3f\t%.3f\t%d" % (i + 1, t, l, f)
print "-----------------------------"

times = map(lambda x: x[0], stats)
print "Problems solved:     %d" % len(times)
print "Total time:          %.2f" % sum(times)
print "Problems / second:   %.2f" % (len(times) / sum(times))
