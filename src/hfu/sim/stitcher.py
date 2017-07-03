
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
    def __init__(self):

        model = [ON, OFF]
        super(Stitcher, self).__init__(model)

    # --------------------------------------------------------------------------
    #
    def feed(self, bast):
        pass

    # --------------------------------------------------------------------------
    #
    def cut(self, length):
        pass

    # --------------------------------------------------------------------------
    #
    def slice(self, width):
        pass

    # --------------------------------------------------------------------------
    #
    def sew(self):
        return BHT()

# ------------------------------------------------------------------------------

