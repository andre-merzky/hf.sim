
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing
from .bht   import BHT

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# stitcher states
ON  = 'on'
OFF = 'off'

# ------------------------------------------------------------------------------
#
class Stitcher(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg):

        self._cfg     = cfg
        self._input   = list()
        self._cut     = list()
        self._spliced = list()

        model = [ON, OFF]
        super(Stitcher, self).__init__(model, 'stitcher')


    # --------------------------------------------------------------------------
    #
    def feed(self, bast):
        
        self._input.extend(bast)

        data = list()
        for bast in self._input:
            data.append(bast.width[0])
        create_hist_plot(fname='bast_width_peel', 
                         title='Bast Width Histogram (after peeling)',
                         ptitle='width',
                         xlabel='width [mm]', 
                         ylabel='number of basts', 
                         data=data)


        data = list()
        for bast in self._input:
            data.append(bast.length)
        create_hist_plot(fname='bast_len_peel', 
                         title='Bast Length Histogram (after peeling)',
                         ptitle='length',
                         xlabel='length [mm]', 
                         ylabel='number of basts', 
                         data=data)


    # --------------------------------------------------------------------------
    #
    def cut(self):
        
        print 'input  : %d' % len(self._input )
        for bast in self._input:
            self._cut.extend(bast.cut(length=self._cfg['seg_length']))
        self._input = list()


        data = list()
        for bast in self._cut:
            data.append(bast.width[0])
        create_hist_plot(fname='bast_width_cut', 
                         title='Bast Width Histogram (after cutting)',
                         ptitle='width',
                         xlabel='width [mm]', 
                         ylabel='number of basts', 
                         data=data)

        data = list()
        for bast in self._cut:
            data.append(bast.length)
        create_hist_plot(fname='bast_len_cut', 
                         title='Bast Length Histogram (after cutting)',
                         ptitle='length',
                         xlabel='length [mm]', 
                         ylabel='number of basts', 
                         data=data)


    # --------------------------------------------------------------------------
    #
    def splice(self):

        print 'cut    : %d' % len(self._cut   )
        for bast in self._cut:
            self._spliced.extend(bast.splice(width=self._cfg['splice_width']))
        self._cut = list()

        data = list()
        for bast in self._spliced:
            data.append(bast.width[0])
        create_hist_plot(fname='bast_width_spliced', 
                         title='Bast Width Histogram (after splicing)',
                         ptitle='width',
                         xlabel='width [mm]', 
                         ylabel='number of basts', 
                         data=data)

        data = list()
        for bast in self._spliced:
            data.append(bast.length)
        create_hist_plot(fname='bast_len_spliced', 
                         title='Bast Length Histogram (after splicing)',
                         ptitle='length',
                         xlabel='length [mm]', 
                         ylabel='number of basts', 
                         data=data)


    # --------------------------------------------------------------------------
    #
    def sew(self):

        print 'spliced: %d' % len(self._spliced)

        res  = self._cfg['resolution']   # len resolution
        segw = self._cfg['seg_width']    # minmimal tot width
        bht  = list()
        cur  = list()
        idx  = 0

        # TODO: also add to cur if basts are near their end

        while idx < len(self._spliced):
            tot  = 0
            keep = list()
            # what is stitched currently:
            for bast, pos in cur:
                pos += res
                w    = bast.width_at(pos)
                if w:
                    tot += w
                    keep.append([bast, pos])
            cur = keep
            while tot < segw:
                bast = self._spliced[idx]; idx += 1
                pos  = 0
                tot += bast.width_at(pos)
                cur.append([bast, pos])
            bht.append([tot, len(cur)])

          # w = len(cur)
          # if   w == 1: print '-',
          # elif w == 2: print '=',
          # elif w == 3: print '#',
          # else       : print '?',

        return BHT(res=res, segw=segw, bht=bht)


# ------------------------------------------------------------------------------

