
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

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


    # --------------------------------------------------------------------------
    #
    def cut(self, length):
        
        print 'input  : %d' % len(self._input )
        for bast in self._input:
            self._cut.extend(bast.cut(length=300))
        self._input = list()


    # --------------------------------------------------------------------------
    #
    def splice(self, width):

        print 'cut    : %d' % len(self._cut   )
        for bast in self._cut:
            self._spliced.extend(bast.splice(width=8))
        self._cut = list()


    # --------------------------------------------------------------------------
    #
    def sew(self):

        print 'spliced: %d' % len(self._spliced)

        res  = self._cfg['resolution']   # len resolution
        minw = self._cfg['min_width']    # minmimal tot width
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
            while tot < minw:
                bast = self._spliced[idx]; idx += 1
                pos  = 0
                tot += bast.width_at(pos)
                cur.append([bast, pos])
            bht.append([tot, len(cur)])

            w = len(cur)
            if   w == 1: print '-',
            elif w == 2: print '=',
            elif w == 3: print '#',
            else       : print '?',

        print
        print len(bht), bht[-1]

        return BHT(res=res, minw=minw, bht=bht)


# ------------------------------------------------------------------------------

