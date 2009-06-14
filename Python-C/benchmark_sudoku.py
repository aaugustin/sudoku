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
    d = s.graph_forks()
    stats.append((t, d))

print "test\ttime\tforks"
print "---------------------"
for i, (t, d) in enumerate(stats):
    print "%d\t%.2f\t%d" % (i + 1, t, d)
print "---------------------"

times = map(lambda x: x[0], stats)
print "Problems solved:     %d" % len(times)
print "Total time:          %.2f" % sum(times)
print "Problems / second:   %.2f" % (len(times) / sum(times))
