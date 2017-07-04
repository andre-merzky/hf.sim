
import sys
import random

import radical.utils as ru

from .distribution import create_beta_distribution as beta
from .distribution import create_flat_distribution as flat

from .distribution import create_line_plot
from .distribution import create_hist_plot

from .thing import Thing

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

# peeler states
ON  = 'on'
OFF = 'off'


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
    def __init__(self, cfg): 
        '''
        Peeler starts working
        '''

        rep.header('Initialize peeler')

        self._cfg      = cfg
        self._input    = list()
        self._selected = list()
        self._cut      = list()
        self._scrapped = list()

        model = [ON, OFF]
        super(Peeler, self).__init__(model, 'peeler')


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
                self._selected.append(stalk)
            else:
                self._scrapped.append(stalk)

        # all inputs have been selected
        self._input = list()
        rep.ok('>> ok\n')

        data = list()
        for stalk in self._selected:
            data.append(stalk.dia)
        create_hist_plot(fname='stalk_dia_selected', 
                         title='Stalk Diameter Histogram (after selection)',
                         ptitle='diameter',
                         xlabel='diameter [mm]', 
                         ylabel='number of stalks', 
                         data=data)


        data = list()
        for stalk in self._selected:
            data.append(stalk.len)
        create_hist_plot(fname='stalk_len_selected', 
                         title='Stalk Length Histogram (after selection)',
                         ptitle='length',
                         xlabel='length [mm]', 
                         ylabel='number of stalks', 
                         data=data)


    # --------------------------------------------------------------------------
    #
    def cut(self):
        '''
        we have to cut stalks to the peelers max length.
        '''

        assert(self.state == ON)

        rep.info('cut %d stalks' % len(self._selected))

        max_len = self._cfg['max_len']
        for stalk in self._selected:
            length = flat(n=2, dmin=max_len * 0.99,  dmax=max_len * 1.01)
            stalk.cut(length[0])
            self._cut.append(stalk)

        # all selected stalks have been cut
        self._selected = list()
        rep.ok('>> ok\n')

        data = list()
        for stalk in self._cut:
            data.append(stalk.dia)

        create_hist_plot(fname='stalk_dia_cut', 
                         title='Stalk Diameter Histogram (after cutting)',
                         ptitle='diameter',
                         xlabel='diameter [mm]', 
                         ylabel='number of stalks', 
                         data=data)


        data = list()
        for stalk in self._cut:
            data.append(stalk.len)
        create_hist_plot(fname='stalk_len_cut', 
                         title='Stalk Length Histogram (after cutting)',
                         ptitle='length',
                         xlabel='length [mm]', 
                         ylabel='number of stalks', 
                         data=data)


    # --------------------------------------------------------------------------
    #
    def peel(self):

        assert(self.state == ON)

        rep.info('peeling %d stalks' % len(self._cut))

        bast = list()
        for stalk in self._cut:

            # we randomly fail on some stalks
            if (random.random()*100) > self._cfg['prep_efficiency']:
                stalk.scrap()
                self._scrapped.append(stalk)
                continue

            bast.extend(stalk.peel(self._cfg))
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

