#!/usr/bin/env python

from time import time

from SuDoKu import SuDoKu

times = []
for problem in open('../tests/95_hard_puzzles'):
    t = time()
    s = SuDoKu()
    s.fromString(problem)
    s.resolve()
    times.append(time() - t)

solved_per_second = len(times) / sum(times)
print "Solved %.2f problems / second." % solved_per_second
