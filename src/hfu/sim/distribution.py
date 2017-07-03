
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

    vmin  = float(dmin)
    vmax  = float(dmax)
    vmean = float(dmean)
    vvar  = float(dvar)

    dif   =  vmax  - vmin
    wmean = (vmean - vmin) / dif   # weighted mean in 0..1 range
    wvar  =  vvar / dif            # weighted variance

  # print vmin
  # print vmax
  # print dif
  # print wmean
  # print wvar
    
    assert(wmean > 0 and wmean < 1.00)
  # assert(wvar  > 0 and wvar  < 0.25)
    
    alpha = ((1 - wmean) / wvar - 1 / wmean) * wmean**2
    beta  = alpha * (1 / wmean - 1)
    vals  = list()

    for n in range(n):
        vals.append((random.betavariate(alpha, beta) * dif) + vmin)
    
    # mode: most frequent value
    mode     = (((alpha - 1) / (alpha + beta - 2)      ) * dif) + vmin
    mean     = ((1 / (1 + beta  /   alpha)             ) * dif) + vmin
    median   = (((alpha -  1/3) / ( alpha + beta - 2/3)) * dif) + vmin
    variance = (((alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))) * dif)
    
  # print 'alpha   : %3.2f' % alpha
  # print 'beta    : %3.2f' % beta
  # print 'min     : %3.2f' % vmin
  # print 'max     : %3.2f' % vmax
  # print 'mode    : %3.2f' % mode
  # print 'mean    : %3.2f' % mean
  # print 'median  : %3.2f' % median
  # print 'variance: %3.2f' % variance

    return vals


# ------------------------------------------------------------------------------
# 
def create_flat_distribution(n, dmin, dmax):
    '''
    create a flat distribution of values in the given range

      dmin: lower bound of the distribution
      dmax: upper bound of the distribution
    '''

    dif = dmax - dmin

    vals = list()
    for n in range(n):
        vals.append((random.random() * dif) + dmin)

    mean = sum(vals) / float(n)
    
  # print 'min     : %3.2f' % dmin
  # print 'max     : %3.2f' % dmax
  # print 'mean    : %3.2f' % mean

    return vals

# ------------------------------------------------------------------------------


