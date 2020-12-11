
import sys
import math

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing

PI  = 3.1415926
rep = ru.Reporter(name='hf.sim')

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
    def __init__(self, length, width, cfg, state=None):
        '''
        Create a piece of bast of given geometry (values in mm).
        We assume that the width degrades over length, although the distribution
        is somewhat weighted towards constant length.  Width can also be givenm
        as a tuple though, which is then interpreted as width at begin and end
        of the bast, respectively.
        '''

        self._cfg = cfg

        if   isinstance(width, list) or \
             isinstance(width, tuple)   :
            self._width  = width

        elif isinstance(width, int)  or \
             isinstance(width, float)   :
             max_width   = width
             mean_width  = max_width * 2/3
             end_width   = beta(n=1, dmin=0, dmax=max_width, dmean=mean_width, dvar=0.7)
             self._width = [width, end_width[0]]

        else:
            raise TypeError('Cannot handle width type')

        self._len   = length
        self._wdiff = self._width[0] - self._width[1]
        self._grad  = self._wdiff / self._len

        model = [FRESH, CUT, SPLICED, SEWN]
        super(Bast, self).__init__(model)

        if state:
            while self.state != state:
                self.advance()


    @property
    def length(self): return self._len
    @property
    def width(self):  return self._width


    # --------------------------------------------------------------------------
    #
    def width_at(self, l):
        '''
        determine the width of the bast at length l
        '''
        if l > self._len:
            return 0
        else:
            return self._width[0] - self._grad * float(l)

    # --------------------------------------------------------------------------
    #
    def len_at(self, w):
        '''
        determine at what len the bast has width w
        '''
        assert(w <= self._width[0])
        assert(w >= self._width[1])

        return (self._width[0] - float(w)) / self._wdiff * self._len


    # --------------------------------------------------------------------------
    #
    def cut(self, length):
        '''
        cut the bast to the given length, reducing the length of this bast to
        the given value, but also producing more bast in the process.  we return
        the new bast segments.  This bast instance will represent the first
        segment.
        '''

        assert(self.state == FRESH)

        n_segments = int(math.ceil(self._len / length))
        segments   = list()

        for n in range(n_segments):

            start =  n    * length
            end   = (n+1) * length

            if  end >= self._len:
                end  = self._len

            new_width = [self.width_at(start), self.width_at(end)]
            segments.append(Bast(length=(end-start), width=new_width,
                                 cfg=self._cfg, state=CUT))

        self._len   = segments[0].length
        self._width = segments[0].width

        return segments


    # --------------------------------------------------------------------------
    #
    def splice(self, width):
        '''
        Splicing the bast which is too wide.
        '''

        assert(self.state == CUT)

        n_splices = int(math.ceil(self._width[0] / width))
        s_width   = [self._width[0] / n_splices,
                     self._width[1] / n_splices]
        splices   = list()

        for n in range(n_splices):
            splices.append(Bast(length=self._len, width=s_width, cfg=self._cfg))

        self.advance()

        return splices


# ------------------------------------------------------------------------------
