
import sys

import radical.utils as ru

PI  = 3.1415926
rep = ru.LogReporter(name='hf.sim')

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

