
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .thing import Thing

rep = ru.LogReporter(name='hf.sim')

# bht states
SEWN = 'sewn'


# ------------------------------------------------------------------------------
#
class BHT(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self): 

        model = [SEWN]
        super(BHT, self).__init__(model)


    # --------------------------------------------------------------------------
    #
    def stats(self):

        assert(self.state == SEWN)

        print self


# ------------------------------------------------------------------------------
