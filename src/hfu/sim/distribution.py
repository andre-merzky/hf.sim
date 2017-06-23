#!/usr/bin/env python 

import sys
import random

N = 100000
M = 0.45    # mean, location
V = 0.0001    # variance

MIN = 10
MAX = 20
DIF = MAX - MIN

assert(M > 0 and M < 1.00)
assert(V > 0 and V < 0.25)

# https://stats.stackexchange.com/questions/12232/calculating-the-parameters-of-a-beta-distribution-using-the-mean-and-variance
A = ((1 - M) / V - 1 / M) * M * M
B = A * (1 / M - 1)

with open('dist.dat', 'w+') as f:
    for n in range(N):
        if not n%1000: 
            sys.stdout.write('.')
            sys.stdout.flush()
        val = (random.betavariate(A, B) * DIF) + MIN
        f.write('%5.20f\n' % val)
    print

# mode: most frequent value
mode     = (((A - 1) / (A + B - 2)                      ) * DIF) + MIN
mean     = ((1 / (1 + B / A)                            ) * DIF) + MIN
median   = (((A - 1/3) / (A + B - 2/3)                  ) * DIF) + MIN
variance = (((A * B) / ((A + B) * (A + B) * (A + B + 1))) * DIF)

print 'alpha   : %3.2f' % A
print 'beta    : %3.2f' % B
print 'mode    : %3.2f' % mode
print 'mean    : %3.2f' % mean
print 'median  : %3.2f' % median
print 'variance: %3.2f' % variance


