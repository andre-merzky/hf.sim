
import sys
import random

# ------------------------------------------------------------------------------
#
# see https://stats.stackexchange.com/questions/12232/
# 
def create_beta_distribution(n, dmin, dmax, dmean, dvar):
    '''
    Create `n` numbers according to a beta distribution with the given boundary
    conditions:

      dmin: lower bound of the distribution
      dmax: upper bound of the distribution
      dmax: mean        of the distribution
      dvar: variance    of the distribution
    '''

    dif = dmax - dmin
    
    assert(dmean > 0 and dmean < 1.00)
    assert(dvar  > 0 and dvar  < 0.25)
    
    alpha = ((1 - dmean) / dvar - 1 / dmean) * dmean * dmean
    beta  = alpha * (1 / dmean - 1)
    vals  = list()
    
    for n in range(n):
        vals.append((random.betavariate(alpha, beta) * dif) + dmin)
    
    # mode: most frequent value
    mode     = (((alpha - 1) / (alpha + beta - 2)    ) * dif) + dmin
    mean     = ((1 / (1 + beta / alpha)              ) * dif) + dmin
    median   = (((alpha - 1/3) / (alpha + beta - 2/3)) * dif) + dmin
    variance = (((alpha * beta) / \
                ((alpha + beta) * (alpha + beta) * (alpha + beta + 1))) * dif)
    
    print 'alpha   : %3.2f' % alpha
    print 'beta    : %3.2f' % beta
    print 'mode    : %3.2f' % mode
    print 'mean    : %3.2f' % mean
    print 'median  : %3.2f' % median
    print 'variance: %3.2f' % variance


    return vals

# ------------------------------------------------------------------------------

