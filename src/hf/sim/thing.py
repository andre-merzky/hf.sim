
import sys

import radical.utils as ru

PI  = 3.1415926
rep = ru.Reporter(name='hf.sim')

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
    def __init__(self, model, name=None):
        '''
        Define the state model and set initial state.
        '''

        self._model = model
        self._sidx  = 0
        self._state = model[0]
        self._uid   = None

        if name:
            self._uid = ru.generate_id(name)


    # --------------------------------------------------------------------------
    #
    @property
    def state(self): return self._state
    @property
    def uid(self)  : return self._uid


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

