
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing
from .stalk import Stalk

PI  = 3.1415926
rep = ru.Reporter(name='hf.sim')

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
    def __init__(self, area, cfg):
        '''
        area: area of field in square meter (default: 1 acre == 10,000m^2)
        '''

        self._cfg    = cfg
        self._area   = area
        self._stalks = list()

        model = [FRESH, SOWN, GROWN, HARVESTED]
        super(Field, self).__init__(model, 'field')

        rep.header('Planting new field %s: %6d m^2' % (self.uid, area))


    @property
    def stalks(self): return self._stalks
    @property
    def nstalks(self): return self._nstalks


    # --------------------------------------------------------------------------
    #
    def sow(self):

        assert(self.state == FRESH)
        self.advance()     # SOWN


    # --------------------------------------------------------------------------
    #
    def grow(self):

        assert(self.state == SOWN)
        self.advance()     # GROWN

        # FIXME: model loss over growth period
        #
        # we assume the following stalk parameter distributions
        # length:
        # #/m^2   :  200 /  250 /  350 m^-2
        # length  : 2.00 / 2.75 / 3.00 m
        # diameter:    6 /    8 /   10 mm
        sprout_min  = self._cfg['sprout']['min']
        sprout_max  = self._cfg['sprout']['max']
        sprout_mean = self._cfg['sprout']['mean']
        sprout_var  = self._cfg['sprout']['var']

        self._nstalks = beta(n=self._area, dmin=sprout_min, dmax=sprout_max,
                             dmean=sprout_mean, dvar=sprout_var)

        rep.info('area: %d m^2>>' % self._area)
        for n in self._nstalks:

            len_min     = self._cfg['length']['min']
            len_max     = self._cfg['length']['max']
            len_mean    = self._cfg['length']['mean']
            len_var     = self._cfg['length']['var']

            dia_min     = self._cfg['diameter']['min']
            dia_max     = self._cfg['diameter']['max']

            length_list = beta(n=int(n), dmin=len_min,   dmax=len_max,
                                         dmean=len_mean, dvar=len_var)
            diam_list   = flat(n=int(n), dmin=dia_min,   dmax=dia_max)

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
    def harvest(self):

        assert(self.state == GROWN)
        self.advance()     # HARVESTED

        rep.info('harvest field %s' % self.uid)
        rep.ok('>> %d stalks\n' % len(self._stalks))

        return self._stalks


# ------------------------------------------------------------------------------

