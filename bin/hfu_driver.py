#!/usr/bin/env python 

import hfu.sim as sim

vals = sim.create_beta_distribution(n=100000, dmin=10, dmax=20, 
                                    dmean=0.45, dvar=0.0001)

with open('dist.dat', 'w+') as f:
    for val in vals:
        f.write('%5.20f\n' % val)


