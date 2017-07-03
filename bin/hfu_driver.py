#!/usr/bin/env python 

import sys

import radical.utils as ru
import hfu.sim       as sim

beta   = sim.create_beta_distribution
flat   = sim.create_flat_distribution
rep    = ru.LogReporter(name='hf')

if len(sys.argv) == 1:
    farmer = sim.Farmer()
  # farmer.plant(areas=[100, 50, 10])
    farmer.plant(areas=[1])
    farmer.harvest()
    farmer.dry()
    stalks = farmer.buy()
    
    with open('stalks.dat', 'w+') as f:
        for stalk in stalks:
            f.write('%5.2f %5.2f\n' % (stalk.dia, stalk.len))

    peeler = sim.Peeler()
    peeler.feed(stalks)
    peeler.select()
    peeler.cut()
    bast = peeler.peel()

    for b in bast:
        print '%7d [%2d - %2d]' % (b.length, b.width[0], b.width[1])
    
    stitcher = sim.Stitcher()
    stitcher.feed(bast)
    stitcher.cut(length=300)
    stitcher.slice(width=8)
    bht = stitcher.sew()
    
    bht.stats()

else:

    # vals = beta(n=100000, dmin=600, dmax=1000, dmean=800, dvar=100)
    vals = beta(n=10000,  dmin=-10, dmax=12*3.1415/2,  dmean=12, dvar=0.7)

    with open('dist.dat', 'w+') as f:
        for val in vals:
            if val < 0:
                val = -val
            f.write('%5.2f\n' % (val))

