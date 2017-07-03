
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .thing import Thing

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# bast states
FRESH     = 'fresh'
CUT       = 'cut'
SPLICED   = 'spliced'
SEWN      = 'sewn'


# ------------------------------------------------------------------------------
#
class Bast(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self, length, width, cfg):
        '''
        Create a piece of bast of given geometry (values in mm).
        We assume that the width degrades over length, although the distribution
        is somewhat weighted towards constant length.
        '''


        max_width   = width
        mean_width  = max_width * 2/3
        end_width   = beta(n=1, dmin=0, dmax=max_width, dmean=mean_width, dvar=0.7)

        self._len   = length
        self._width = [width, end_width[0]]

        model = [FRESH, CUT, SPLICED, SEWN]
        super(Bast, self).__init__(model)

    @property
    def length(self): return self._len
    @property
    def width(self):  return self._width


    # --------------------------------------------------------------------------
    #
    def cut(self, new_len):
        '''
        cut the bast to the given length, reducing the length of this bast to
        the given value, but also producing more bast in the process
        '''
        assert(self.state == FRESH)

        if new_len < self.len:
            self._scrap['stalk'] += self.len - new_len
            self._len = new_len
        else:
            # nothing to cut
            pass

        self.advance()  # CUT


    # --------------------------------------------------------------------------
    #
    def slice(self):
        '''
        Slicing the bast which is too wide.
        '''

        # parameterize

        assert(self.state == CUT)

        # we can't use stalks thicker than 12mm
        # FIXME: check
        if self.dia > 12:
            self._scrap['stalk'] += self._len
            self._len = 0

        # we can't use stalks thinner than  6mm
        # FIXME: check
        if self.dia < 6:
            self._scrap['stalk'] += self._len
            self._len = 0

        # we assume a preparation failure rate of 1%, covering broken or bent
        # stalks, etc
        # FIXME: gauge
        if random.random() <= 0.01:
            self._scrap['stalk'] += self._len
            self._len = 0

        # if stalk is too short, we can't peel it
        # FIXME: check
        if self._len < 300:
            self._scrap['stalk'] += self._len
            self._len = 0

        self.advance()


    # --------------------------------------------------------------------------
    #
    def peel(self):
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

        for bast in bast_num:
            # the newly peeled bast ban be at most of length `stalk.len`, and at
            # most of width `stalk.dia*PI/2`.  We assume the length is
            # distribution is heavily skewed toward the long end, and width is
            # fully preserved.  The `Bast.__init__` on the variation of the
            # diameter over length.
            # TODO: len distribution
            # TODO: failure rate
            # compute successfully peeled length in %
            success = beta(n=1,  dmin=0, dmax=100,  dmean=90, dvar=1)
            length  = self._len * success / 100
            basts.append(Bast(length=length, width=self.dia*PI/2))

        self.advance()

        return basts


# ------------------------------------------------------------------------------
