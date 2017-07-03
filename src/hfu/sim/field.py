
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .thing import Thing
from .stalk import Stalk

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# field states
FRESH     = 'fresh'
SOWN      = 'sown'
GROWN     = 'grown'
HARVESTED = 'harvested'


# ------------------------------------------------------------------------------
#
class Field(Thing):

    # --------------------------------------------------------------------------
    #
    def __init__(self, area=10000): 
        '''
        area: area of field in square meter (default: 1 acre == 10,000m^2)
        '''

        self._area   = area
        self._stalks = list()

        self.uid = ru.generate_id('field')
        rep.header('Planting new field %s: %6d m^2' % (self.uid, area))

        model = [FRESH, SOWN, GROWN, HARVESTED]
        super(Field, self).__init__(model)

    @property
    def stalks(self):
        return self._stalks


    # --------------------------------------------------------------------------
    #
    def sow(self):

        assert(self.state == FRESH)
        self.advance()     # SOWN

        # we assume the following stalk parameter distributions
        # length: 
        # #/m^2   :  200 /  250 /  350 m^-2
        # length  : 2.00 / 2.75 / 3.00 m
        # diameter:    6 /    8 /   10 mm
        nstalks_list    = beta(n=self._area, dmin=200, dmax=350, 
                               dmean=250, dvar=5)

        rep.info('area: %d m^2>>' % self._area)
        for nstalks in nstalks_list:

            nstalks     = int(nstalks)
            length_list = beta(n=nstalks, dmin=2000, dmax=3000, dmean=2750, dvar=5)
            diam_list   = flat(n=nstalks, dmin=6, dmax=10)

            idx = 0
            for l,d in zip(length_list, diam_list):
                self._stalks.append(Stalk(l, d))
                if not idx % 10:
                    rep.progress('|')
                idx += 1
            rep.progress(' ')
        rep.ok('>> ok\n')


    # --------------------------------------------------------------------------
    #
    def grow(self):

        assert(self.state == SOWN)
        self.advance()     # GROWN

        # FIXME: model loss over growth period


    # --------------------------------------------------------------------------
    #
    def harvest(self):

        assert(self.state == GROWN)
        self.advance()     # HARVESTED

        rep.info('harvest field %s' % self.uid)
        rep.ok('>> %d stalks\n' % len(self._stalks))

        return self._stalks


# ------------------------------------------------------------------------------

