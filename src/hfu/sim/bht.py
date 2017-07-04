
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing

rep = ru.LogReporter(name='hf.sim')

# bht states
SEWN = 'sewn'


# ------------------------------------------------------------------------------
#
class BHT(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self, res, segw, bht): 

        self._res  = res
        self._minw = segw
        self._bht  = bht

        model = [SEWN]
        super(BHT, self).__init__(model, 'bht')


    # --------------------------------------------------------------------------
    #
    def stats(self):

        assert(self.state == SEWN)

        rep.header('BHT Stats')
        rep.info('length: %d m\n' % (len(self._bht) * 10 / 10 / 100))

        data = list()
        x    = 0
        for section in self._bht:
            x += self._res
            y  = section[1]
            data.append([x, y])

        create_line_plot(fname='bht_thickness', 
                         title='BHT Thickness over Length',
                         ptitle='thickness',
                         xlabel='length [mm]', 
                         ylabel='number of layers', 
                         data=data)


# ------------------------------------------------------------------------------
