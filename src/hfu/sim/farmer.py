
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .thing import Thing
from .field import Field

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# farmer states
ACTIVE    = 'active'
RETIRED   = 'retired'


# ------------------------------------------------------------------------------
#
class Farmer(Thing):
    '''
    This class is a manager class for `Field` instances - most operations
    directly translate into operations on those fields.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        self._fields = list()
        self._stalks = list()
        model = [ACTIVE, RETIRED]
        super(Farmer, self).__init__(model)

        rep.header('Farmer')


    # --------------------------------------------------------------------------
    #
    def plant(self, areas):
        '''
        Create a set of fields and sow hemp on them, then let them grow.
        '''

        assert(self.state == ACTIVE)

        if not isinstance(areas, list):
            areas = [areas]

        for area in areas:
            self._fields.append(Field(area))

        for field in self._fields:
            field.sow()
            field.grow()


    # --------------------------------------------------------------------------
    #
    def dry(self):
        '''
        For all fields (or for a given specific field), collect and return all
        grown stalks.
        '''

        assert(self.state == ACTIVE)

        rep.header('Dry harvest: %d stalks' \
                 % sum([len(f.stalks) for f in self._fields]))

        for stalk in self._stalks:
            stalk.dry()
        rep.ok('>> ok')


    # --------------------------------------------------------------------------
    #
    def harvest(self):
        '''
        For all fields, collect all grown stalks.
        '''

        assert(self.state == ACTIVE)

        rep.header('Harvest %d field(s): %s' \
                 % (len(self._fields), ' '.join([f.uid for f in self._fields])))
        for field in self._fields:
            self._stalks.extend(field.harvest())
            rep.progress('.')
        rep.ok('>> ok')


    # --------------------------------------------------------------------------
    #
    def buy(self):
        '''
        return all dried stalks
        '''

        assert(self.state == ACTIVE)

        rep.header('Buy %d stalks' % len(self._stalks))
        rep.ok('>> ok')

        ret = self._stalks
        self._stalks = list()
        return ret


    # --------------------------------------------------------------------------
    #
    def retire(self):
        '''
        stop working
        '''

        assert(self.state == ACTIVE)
        self.advance(RETIRED)


# ------------------------------------------------------------------------------

