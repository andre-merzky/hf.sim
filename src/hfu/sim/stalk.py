
import sys
import random

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing
from .bast  import Bast

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# stalk states
FRESH     = 'fresh'
DRIED     = 'dried'
SELECTED  = 'selected'
CUT       = 'cut'
PEELED    = 'peeled'


# ------------------------------------------------------------------------------
#
class Stalk(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self, length, diameter):
        '''
        create a stalk of given geometry (values in mm).
        We assume constant width over whole length.  
        '''

        self._len   = length
        self._dia   = diameter
        self._vol   = PI * self._dia**2 * self._len
        self._scrap = {'stalk' : 0, 
                       'wood'  : 0, 
                       'fibres': 0}

        model = [FRESH, DRIED, SELECTED, CUT, PEELED]
        super(Stalk, self).__init__(model)

    @property
    def dia(self): return self._dia
    @property
    def len(self): return self._len

    # --------------------------------------------------------------------------
    #
    def dry(self):

        assert(self.state == FRESH)
        self.advance()     # DRIED

    # --------------------------------------------------------------------------
    #
    def select(self, cfg):
        '''
        Before peeling the stalk, select wrt. peeler configuration constrains.
        '''

        # parameterize
        assert(self.state == DRIED)

        if self.dia < cfg['min_dia']:
            self._scrap['stalk'] += self._len
            self._len = 0
            rep.progress('o')
            # FIXME: advance to scrapped
            return False

        if self.dia > cfg['max_dia']:
            self._scrap['stalk'] += self._len
            self._len = 0
            rep.progress('O')
            # FIXME: advance to scrapped
            return False

        if self.len < cfg['min_len']:
            self._scrap['stalk'] += self._len
            self._len = 0
            rep.progress('_')
            # FIXME: advance to scrapped
            return False

        self.advance()  # SELECTED
        return True


    # --------------------------------------------------------------------------
    #
    def cut(self, length):
        '''
        cut the stalk to the given length.
        '''
        assert(self.state == SELECTED)

        # FIXME: this is a dumb cut: we always cut from the thin end, event if
        #        that is not advantegious.

        if length < self.len:
            self._scrap['stalk'] += self.len - length
            self._len = length
        else:
            # nothing to cut
            pass

        self.advance()  # CUT


    # --------------------------------------------------------------------------
    #
    def scrap(self):
        '''
        the stalk will not be used further
        '''
        # FIXME: state check and transition

        self._scrap['stalk'] += self.len
        self._len = 0.0


    # --------------------------------------------------------------------------
    #
    def peel(self, cfg):
        '''
        peel the stalk, ie. produce 0, 1 or two pieces of fresh bast.  This also
        produces some waste, mostly wood and some bast fibers.
        '''

        assert(self.state == CUT)

        if self.len:
            # we have something to peel!
            pass

        basts       = list()
        bast_num    = 0
        bast_chance = random.random()
        if   bast_chance < 0.1: bast_num = 0   # failure
        elif bast_chance < 0.5: bast_num = 1   # partial failure
        else                  : bast_num = 2   # full success

        for bast in range(bast_num):
            # the newly peeled bast ban be at most of length `self.len`, and at
            # most of width `stalk.dia*PI/2`.  We assume the length is
            # distribution is heavily skewed toward the long end, and width is
            # fully preserved.  The `Bast.__init__` on the variation of the
            # diameter over length.
            #
            # compute successfully peeled length in %
            success = beta(n=1,  dmin=0, dmax=100,  dmean=90, dvar=1)[0]
            length  = self._len * success / 100
          # print success, '\t', length
            basts.append(Bast(length=length, width=self.dia*PI/2, cfg=cfg))

        self.advance()

        return basts


# ------------------------------------------------------------------------------

