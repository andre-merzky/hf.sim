#!/usr/bin/env python

import os
import sys
import numpy

fname = sys.argv[1]
rows  = list()
with open('%s.dat' % fname, 'r') as fin:
    for line in fin.readlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        rows.append(line.split())

nrows = len(rows[0])
for row in rows:
    if len(row) != nrows:
        raise ValueError('inconsistent data')

for n in range(nrows):

    vals = list()
    for row in rows:
        vals.append(float(row[n]))

    with open('%s.row.%d' % (fname, n+1), 'w') as fout:
        for val in vals:
            fout.write('%f\n' % val)

    print('row : %7d '  % (n+1))
    print('min : %7.2f' % min(vals))
    print('max : %7.2f' % max(vals))
    print('mean: %7.2f' % numpy.mean(vals))
    print('var : %7.2f' % numpy.std(vals))

    print()
