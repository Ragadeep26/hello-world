# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 14:51:10 2019

@author: nya
"""
import sys
sys.path.append(r'C:\Users\nya\Packages\Moniman')
from optimize.ukf import ScaledSymSigmaPoints, Ukf, ApplyConstraints
from optimize.pso_vectorized import Particles
import numpy as np
import numpy.testing as npt
import random


def ackley(x):
    """ Test function
    Input x is of array type, each dimension has values in [-5, 5]
    f returns function value evaluated at x, f_min = 0.0 at x = (0,0,..,0)
    """
    global NFuncEvals
    NFuncEvals = NFuncEvals + 1
    n = len(x) # number of dimensions
    s1, s2 = 0, 0
    for i in range(n):
        s1 += x[i]**2
        s2 += np.cos(2*np.pi*x[i])
    f = -20*np.exp(-0.2*np.sqrt(1.0/n*s1)) - np.exp(1.0/n*s2) + 20 + np.exp(1)
    return np.array([f]) # array type
    

def run_test_ukf():
    """ Runs UKF iterations
    """
    x0 = np.array([4.0,4.8]) # staring point 
    P0 = np.array([[0.4**2,0.0],[0.0,0.4**2]])
    
    Q = 0.01*P0
    R = np.array([[1.0e-1**2]])
    
    # synthetic measurement
    x_min = np.array([0.0,0.0])
    z = ackley(x_min)
    m = len(z)
    print('z is: {}'.format(z))
    
    N = 50 # number of iterations
    n = max(x0.shape)	# number of states in state vector

    xEst = x0
    zEst = ackley(xEst)
    PEst = P0
    mu_ukf = np.zeros((n,N+1)) # store means
    mu_ukf[:,0] = x0
    J_ukf = np.zeros(N+1)
    innov = (z-zEst)
    J = np.dot(np.mat(innov).transpose(),np.dot(np.linalg.inv(R),np.mat(innov)))
    J_ukf[0] = J
    SigPnts = {}
    
    # Start estimating
    for k in range(1,N+1):
        print('Iteration ', k)
        #xPred = mu_ukf[:,k-1]
        xPred = xEst
        Jx = np.identity(n) # Jacobian
        PPred = Q + np.dot(Jx,np.dot(PEst,Jx.transpose()))	
    	
        #sigma points
        SigPnts['xSigPnts'], SigPnts['wSigPnts'], SigPnts['nSigPnts'] = ScaledSymSigmaPoints(xPred, PPred)
        SigPnts['zPredSigPnts'] = np.zeros((m, SigPnts['nSigPnts']))
        for i in range(SigPnts['nSigPnts']):
            SigPnts['zPredSigPnts'][:, i] = ackley(SigPnts['xSigPnts'][:, i])

        # call Ukf
        xEst, PEst, innov = Ukf(xPred, PPred, Q, SigPnts, z, R)
    	
        # apply constraints
        xEst = ApplyConstraints(xEst, [-5, -5], [5, 5])
    	
        J = np.dot(np.mat(innov).transpose(),np.dot(np.linalg.inv(R),np.mat(innov))) # misfit measure
        # store estimated results
        mu_ukf[:,k] = xEst
        J_ukf[k] = J	
        print('xEst = ', xEst)
        print('Number of function evaluations = %i' % (NFuncEvals))

    return xEst


#def run_test_pso_star():
#    """ Runs PSO star iterations
#    """
#    iter_max = 500
#    x_min = np.array([-5, 5])
#    x_max = np.array([-5, 5])
#    v_max = (x_max - x_min) * random.uniform(0,1)
#    v_min = -v_max
#
#    swarm = Particles(population=50, c1=0.5, c2=80, Xbott=x_min, Xtop=x_max, self.d_obs, self.misfit, self.metamodel)
#    iter = 0
#    while iter < iter_max:
#        w = ((0.9 - 0.4) * (iter_max - iter) / iter_max) + 0.4


def run_test_pso_ring():
    """ Runs PSO ring iterations
    """
    pass


if __name__ == '__main__':
    try:
        print('Test UKF by finding the local minimum of Ackley test function...')
        NFuncEvals = 0
        r = run_test_ukf()
        npt.assert_almost_equal(r, np.array([0, 0]), 7)
        print('Test UKF: Passed')

    except(AssertionError):
        print('Test UKF: Failed')
