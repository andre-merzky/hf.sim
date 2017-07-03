
import sys

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

PI        = 3.1415926
rep       = ru.LogReporter(name='hf.sim', title='Hemp: from cradle to crate')

# farmer states
ACTIVE    = 'active'
RETIRED   = 'retired'

# peeler states
ON        = 'on'
OFF       = 'off'

# field states
SOWN      = 'sown'
GROWN     = 'grown'
HARVESTED = 'harvested'

# stalk states
FRESH     = 'fresh'
DRIED     = 'dried'
SELECTED  = 'selected'
CUT       = 'cut'
PEELED    = 'peeled'

# bast states
FRESH     = 'fresh'
SHORTENED = 'shortened'
SPLICED   = 'spliced'
SEWN      = 'sewn'


# ------------------------------------------------------------------------------
#
class Thing(object):
    '''
    Abstract base class for a stateful object.

    This class is really just a container for a state model and the respective
    state model transitions (by calling `self.advance()`)
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, model):
        '''
        Define the state model and set initial state.
        '''

        self._model = model
        self._sidx  = 0
        self._state = model[0]


    # --------------------------------------------------------------------------
    #
    @property
    def state(self):
        return self._state


    # --------------------------------------------------------------------------
    #
    def advance(self):
        '''
        Transision to the next state in the state model.
        '''
        
        assert(self._state in self._model)
        assert(self._sidx  < (len(self._model)-1))

        self._sidx  += 1
        self._state  = self._model[self._sidx]


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

        self._fields = dict()
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
            field = Field(area)
            self._fields[field.uid] = field

        for field in self._fields.values():
            field.sow()
            field.grow()

        return self._fields.values()


    # --------------------------------------------------------------------------
    #
    def harvest(self, fields=None):
        '''
        For all fields (or for a given specific field), collect and return all
        grown stalks.
        '''

        assert(self.state == ACTIVE)

        if fields:
            if not isinstance(fields, list):
                fields = [fields]
            for field in fields:
                assert(field.uid in self._fields)
        else:
            fields = self._fields.values()

        assert(fields)

        rep.header('Harvest %d field(s): %s' \
                 % (len(fields), ' '.join([f.uid for f in fields])))
        stalks = list()
        for field in fields:
            stalks.extend(field.harvest())
        return stalks


    # --------------------------------------------------------------------------
    #
    def retire(self):
        '''
        stop working
        '''

        assert(self.state == ACTIVE)
        self.advance(RETIRED)


# ------------------------------------------------------------------------------
#
class Peeler(Thing):
    '''
    This class models the operations of a Peeler, who obtains a set of stalks,
    shortens them to a certain fixed length, selects them for peeling (sort out
    unusable geometries), peels them, and thus produces bast.  The class will
    keep track of the scrap byproducts used while peeling. The Peeler could be
    considered to represent a worker or a (set of) machine(s).  
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self): 
        '''
        Peeler starts working
        '''

        rep.header('Initialize peeler')

        self._input    = list()
        self._selected = list()
        self._cut      = list()
        self._scrapped = list()
        self._cfg      = {  # make configurable
                'min_len'         :  300,
                'max_len'         : 1600, 
                'min_dia'         :    6,
                'max_dia'         :   12,
                'prep_efficiency' :   99, # in percent
                'peel_efficiency' :   90  # in percent
                }

        model = [ON, OFF]
        super(Peeler, self).__init__(model)


    # --------------------------------------------------------------------------
    #
    def feed(self, stalks):
        '''
        Fresh stalks are given to the peeler
        '''

        assert(self.state == ON)

        self._input.extend(stalks)
        rep.info('input: %d stalks' % len(stalks))
        rep.ok('>> ok\n')


    # --------------------------------------------------------------------------
    #
    def select(self):
        '''
        Not all stalks are eligible for peeling.  This can result in some waste.
        '''

        assert(self.state == ON)

        rep.info('select from %d stalks' % len(self._input))
        for stalk in self._input:
            if stalk.select(self._cfg):
                self.selected.append(stalk)
            else:
                self.scrapped.append(stalk)

        # all inputs have been selected
        self._input = list()
        rep.ok('>> ok\n')


    # --------------------------------------------------------------------------
    #
    def cut(self):
        '''
        we have to cut stalks to the peelers max length.
        '''

        assert(self.state == ON)

        rep.info('cut %d stalks' % len(self._selected))

        for stalk in self._selected:
            stalk.cut(length=self._cfg['max_len'])
            self._cut.append(stalk)

        # all selected stalks have been cut
        self._selected = list()
        rep.ok('>> ok\n')


    # --------------------------------------------------------------------------
    #
    def peel(self):

        assert(self.state == ON)

        rep.info('peeling %d stalks' % len(self._prepped))

        bast = list()
        for stalk in self._cut:

            # we randomly fail on some stalks
            if (random.random()*100) > self._cfg['prep_efficiancy']:
                stalk.scrap()
                self._scrapped.append(stalk)
                continue

            bast.append(stalk.peel())
            self._scrapped.append(stalk)  # scrap remains
            rep.progress('V')

        self._cut = list()

        rep.ok('>> ok\n')
        return bast


    # --------------------------------------------------------------------------
    #
    def turn_off(self):

        assert(self.state == ON)
        self.advance()


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

        if self.len > cfg['max_len']:
            self._scrap['stalk'] += self._len
            self._len = 0
            rep.progress('=')
            # FIXME: advance to scrapped
            return False

        self.advance()  # SELECTED


    # --------------------------------------------------------------------------
    #
    def cut(self, new_len):
        '''
        cut the stalk to the given length.
        '''
        assert(self.state == SELECTED)

        # FIXME: this is a dumb cut: we always cut from the thin end, event if
        #        that is not advantegious.

        if new_len < self.len:
            self._scrap['stalk'] += self.len - new_len
            self._len = new_len
        else:
            # nothing to cut
            pass

        self.advance()  # CUT


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
            # the newly peeled bast ban be at most of length `self.len`, and at
            # most of width `stalk.dia*PI/2`.  We assume the length is
            # distribution is heavily skewed toward the long end, and width is
            # fully preserved.  The `Bast.__init__` on the variation of the
            # diameter over length.
            #
            # compute successfully peeled length in %
            success = beta(n=1,  dmin=0, dmax=100,  dmean=90, dvar=1)
            length  = self._len * success / 100
            basts.append(Bast(length=length, width=self.dia*PI/2))

        self.advance()

        return basts


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

        self._len   = length
        self._width = width

        max_width   = cfg['max_dia'] * PI / 2
        mean_width  = max_width * 2/3
        self._end   = beta(n=1, dmin=0, dmax=max_width, dmean=mean_width, dvar=0.7)

        model = [FRESH, CUT, SLICED, PEELED]
        super(Bast, self).__init__(model)


    # --------------------------------------------------------------------------
    #
    def cut(self, new_len):
        '''
        cut the bast to the given length, reducing the length of this bast to
        the given value, but also producing more bast in the process
        '''
        assert(self.state == DRIED)

        # FIXME: this is a dumb cut: we always cut from the thin end, event if
        #        that is not advantegious.

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
#
class Stitcher(Thing):
    pass


# ------------------------------------------------------------------------------
