import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
#import time

########## Scaled symetric sigma points
def ScaledSymSigmaPoints(xEst, PEst, lamb=1.0):
# INPUT
# eEst: current estimate
# PEst: current estimation error cov. matrix 
# *parameters: a set of parameters characterizing the spread of sigma points
# RETURN
# xPts: sigma-points
# wPts: weights
# nPts: number of sigma-points

	n = xEst.size # number of states
	xEst = xEst.reshape(n,1)  # vector to 'single column matrix'
	nPts = 2*n + 1
	xPts = np.zeros((n,nPts))
	wPts = np.zeros((1,nPts))
	
	Psqrt = np.linalg.cholesky((n+lamb)*PEst).transpose()	# matrix square root
	
	xPts[:,0] = xEst[:,0]	# center point
	xPts[:,1:n+1] = np.tile(xEst,(1,n)) + Psqrt	# points in the negative side to center
	xPts[:,n+1:nPts] = np.tile(xEst,(1,n)) - Psqrt	# points in the positive side to center
	
	wPts[0,0] = lamb/(n+lamb)
	wPts[0,1:nPts] = 0.5*np.ones((1,nPts-1))/(n+lamb)
	
	return xPts, wPts, nPts


########## Unscented Kalman filter
def Ukf(xEst, PEst, Q, SigPnts, z, R):
# INPUT
# eEst: current estimate
# PEst: current estimation error cov. matrix 
# ffun: state transition equation
# hfun: obvervation equation
# z: measurement data
# Q, R: cov. matrices for system noise and measurement noise
# RETURN
# xEst_new
# PEst_new
# xSigmaPts
# innov: innovation 

	n = xEst.size	# number of states in state vector
	m = z.size	# number of measurements
	#m = 1	# number of measurements
	
	## Assign sigma-points
	##lamb = 1.0 # lambda
	##xSigmaPts, wSigmaPts, nsp = ScaledSymSigmaPoints(xEst, PEst, lamb)
	#	
	## Project the sigma-points
	#xPredSigmaPts = np.zeros((n,nsp))
	#zPredSigmaPts = np.zeros((m,nsp))
	#for i in range(nsp):
	#	#xSigmaPts[:,i] = ApplyConstraints(xSigmaPts[:,i], [-500, -500], [500, 500])  # this constraints are necessary when function evaluation out of bounds is not valid
	#	xPredSigmaPts[:,i] = xSigmaPts[:,i]			# ffunc
	#	zPredSigmaPts[:,i] = hfunc(xPredSigmaPts[:,i]) 	# hfunc
	
	xPredSigmaPts = SigPnts['xSigPnts']
	wSigmaPts = SigPnts['wSigPnts']
	nSigmaPts = SigPnts['nSigPnts']
	zPredSigmaPts = SigPnts['zPredSigPnts']


	# Mean
	xPred = np.zeros(n)
	zPred = np.zeros(m)
	for i in range(nSigmaPts):
		xPred += wSigmaPts[0,i]*xPredSigmaPts[:,i]
		zPred += wSigmaPts[0,i]*zPredSigmaPts[:,i]
	
	# Covariances and cross-covariances
	PPred = np.zeros((n,n))
	PxzPred = np.zeros((n,m))
	S = np.zeros((m,m))

	for i in range(nSigmaPts):
		PPred   += wSigmaPts[0,i] * np.dot(np.mat((xPredSigmaPts[:,i]-xPred)).transpose(),np.mat((xPredSigmaPts[:,i]-xPred)))
		PxzPred += wSigmaPts[0,i] * np.dot(np.mat((xPredSigmaPts[:,i]-xPred)).transpose(),np.mat((zPredSigmaPts[:,i]-zPred)))
		S       += wSigmaPts[0,i] * np.dot(np.mat((zPredSigmaPts[:,i]-zPred)).transpose(),np.mat((zPredSigmaPts[:,i]-zPred)))

	PPred = PPred + Q
	S     = S + R
	
	# Measurement update
	K = np.dot(PxzPred,np.linalg.inv(S))		# Kalman gain
	innov = z - zPred				# innovation
	#innov = zPred - z				# innovation
	#innov = 0.0 - zPred				# innovation for optimization of a quadratic term
	xEst = xPred + np.dot(K,innov)					# posterior estimate
	PEst = PPred - np.dot(K,np.dot(S,K.transpose()))# posterior est. err. cov.
	
	return xEst.ravel(), PEst, innov		# xEst to 1D array

########## Apply constraints
def ApplyConstraints(x, lowerbounds, upperbounds):
# Bring x back to the boundary when it is out of range
	for i in range(x.size):
		if x[i] < lowerbounds[i]:
			x[i] = lowerbounds[i]
		elif x[i] > upperbounds[i]:
			x[i] = upperbounds[i]
	return x

