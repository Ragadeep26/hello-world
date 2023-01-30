#from ukf_optimal import * # import ukf module
from ukf_test import ApplyConstraints, Ukf # import ukf module
import numpy as np
import matplotlib.pyplot as plt
import time

########## Ackley function
def ackley(x):
# Input x is of array type, each dimension has values in [-5, 5]
# f returns function value evaluated at x, f_min =0.0 at x=(0,0,..,0)
	global NFuncEvals
	NFuncEvals = NFuncEvals + 1
	n = len(x) # number of dimensions
	s1, s2 = 0, 0
	for i in range(n):
		s1 += x[i]**2
		s2 += np.cos(2*np.pi*x[i])
	f = -20*np.exp(-0.2*np.sqrt(1.0/n*s1)) - np.exp(1.0/n*s2) + 20 + np.exp(1)
	return np.array([f]) # array type


########## MAIN
NFuncEvals = 0

x0 = np.array([4.0,4.8]) # staring point 
#P0 = np.array([[0.2**2,0.0],[0.0,0.2**2]])
P0 = np.array([[0.4**2,0.0],[0.0,0.4**2]])

# Test generating sigma-points
#lamb = 1.0
#xSigmaPts, wSigmaPts, nsp = ScaledSymSigmaPoints(x, P, lamb)
#print xSigmaPts, '\n', wSigmaPts,'\n', nsp


Q = 0.01*P0
#Q = 0.0001*P0

#R = np.array([[1.0e-2**2]])
R = np.array([[1.0e-1**2]])

# synthetic measurement
x_min = np.array([0.0,0.0])
z = ackley(x_min)
print('z is: {}'.format(z))

N = 50 # number of iterations
n = max(x0.shape)	# number of states in state vector
m = len(z)	# number of measurements
xEst = x0
zEst = ackley(xEst)
PEst = P0
mu_ukf = np.zeros((n,N+1)) # store means
mu_ukf[:,0] = x0
J_ukf = np.zeros(N+1)
#innov = (z-zEst).reshape(1,m)
innov = (z-zEst)
J = np.dot(np.mat(innov).transpose(),np.dot(np.linalg.inv(R),np.mat(innov)))
J_ukf[0] = J


# Plot contour of Ackley function on 2d grid
xr = np.linspace(-6,6,200)
yr = np.linspace(-6,6,200)
xx, yy = np.meshgrid(xr, yr)
zz = np.zeros(xx.shape)
for i in range(xx.shape[0]):
	for j in range(xx.shape[1]):
		xy = np.array([xx[i,j],yy[i,j]])
		zij = ackley(xy)
		zz[i,j] = zij
#fig = plt.figure()
plt.figure(1)
plt.contourf(xx,yy,zz)
plt.colorbar()
plt.ion()
plt.gray()
#p1 = plt.scatter(xEst[0],xEst[1],s=40,c='b',label="staring point")
p1 = plt.plot(xEst[0],xEst[1],'rD',markersize=8, label="staring point")
plt.xlabel('x1'), plt.ylabel('x2')
plt.draw()
time.sleep(0.1)

# Plot Inital misfit
plt.figure(2)
plt.plot(0, J, marker='o', color='b')
plt.ylabel("Misfit")
plt.xlabel("Iteration")
plt.draw()
time.sleep(0.1)

# Start estimating
for k in range(1,N+1):
	print('Iteration ', k)
	#xPred = mu_ukf[:,k-1]
	xPred = xEst
	Jx = np.identity(n) # Jacobian
	PPred = Q + np.dot(Jx,np.dot(PEst,Jx.transpose()))	
	
	# call Ukf
	xEst, PEst, xSigmaPts, innov = Ukf(xPred,PPred,ackley,z,Q,R)
	
	# apply constraints
	xEst = ApplyConstraints(xEst, [-5, -5], [5, 5])
	
	J = np.dot(np.mat(innov).transpose(),np.dot(np.linalg.inv(R),np.mat(innov))) # misfit measure
	# store estimated results
	mu_ukf[:,k] = xEst
	J_ukf[k] = J	
	print('xEst = ', xEst)
	plt.figure(1)
	p2 = plt.plot([xPred[0],xEst[0]], [xPred[1],xEst[1]],marker='o', color='c') # plot trajectory
	plt.draw()
	for i in range(xSigmaPts.shape[1]):
		p3 = plt.plot(xSigmaPts[0,i], xSigmaPts[1,i],marker='*', markersize=2,color='k') # plot sigma-points
	plt.figure(2)
	plt.plot([k-1,k], [J_ukf[k-1], J_ukf[k]], marker='o', color='b') # plot misfit
	time.sleep(0.1)
# Mark final estimate
plt.figure(1)
p4 = plt.plot(xEst[0],xEst[1],'ro',label="ending point")
#plt.draw()
plt.legend(bbox_to_anchor=(0., 1.01, 1., 0.1), loc=3, ncol=2, mode="expand", borderaxespad=0.,numpoints=1)
#plt.legend([p1,p2,p3],["starting point","intermediate points","final point"])
#plt.savefig('Ackley_estimates.png')
#plt.figure(2)
#plt.savefig('Ackley_estimates_misfit.png')
plt.show()
print('Number of function evaluations = %i' % (NFuncEvals-200*200-2))



