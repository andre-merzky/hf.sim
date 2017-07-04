#!/usr/bin/env python 

import sys

import radical.utils as ru
import hfu.sim       as sim

beta   = sim.create_beta_distribution
flat   = sim.create_flat_distribution
rep    = ru.LogReporter(name='hf')


cfg = { 'farmer'   : { 'sprout'   : { 'min'  :  100,
                                      'max'  :  250,
                                      'mean' :  150,
                                      'var'  :    5
                                     },
                       'length'   : { 'min'  : 2000,
                                      'max'  : 3000,
                                      'mean' : 2750,
                                      'var'  :    5
                                     },
                       'diameter' : { 'min'  : 4,
                                      'max'  : 15,
                                     },
                     },
        'peeler'   : { 'min_len'         :  300,
                       'max_len'         : 1600, 
                       'min_dia'         :    6,
                       'max_dia'         :   12,
                       'prep_efficiency' :   99, # in percent
                       'peel_efficiency' :   90  # in percent
                     },
        'stitcher' : { 'resolution'  :  10,
                       'seg_width'   :  14,
                       'seg_length'  : 300, 
                       'mode'        : 'continuous'
                     },
      }


farmer = sim.Farmer(cfg['farmer'])
farmer.plant(areas=10)
farmer.harvest()
farmer.dry()
stalks = farmer.get()

peeler = sim.Peeler(cfg['peeler'])
peeler.feed(stalks)
peeler.select()
peeler.cut()
bast = peeler.peel()

stitcher = sim.Stitcher(cfg['stitcher'])
stitcher.feed(bast)
stitcher.cut(length=300)
stitcher.splice(width=8)
bht = stitcher.sew()

bht.stats()

