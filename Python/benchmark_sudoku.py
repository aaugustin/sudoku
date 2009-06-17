#!/usr/bin/env python
# Copyright (C) 2008-2009 Aymeric Augustin

import sudoku, time

stats = []
for problem in open('../tests/95_hard_puzzles'):
    t = time.time()
    s = sudoku.SuDoKu()
    s.from_string(problem)
    s.resolve()
    t = time.time() - t
    l, f = s.estimate()
    stats.append((t, l, f))
    break

print "test\ttime\tlevel\tforks"
print "-----------------------------"
for i, (t, l, f) in enumerate(stats):
    print "%d\t%.3f\t%.3f\t%d" % (i + 1, t, l, f)
print "-----------------------------"

times = map(lambda x: x[0], stats)
print "Problems solved:     %d" % len(times)
print "Total time:          %.2f" % sum(times)
print "Problems / second:   %.2f" % (len(times) / sum(times))
