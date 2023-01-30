import os
import  numpy as np
from numpy import linalg as la
import copy
import random
from pyDOE import *
# from skmetamodel import gp
from denorm import denormalize
import matplotlib.pyplot as plt
from Fitnessfunction import Costfunction
from norm import normalize
from inputs_outputs import Fem_result,U_Range
# from data_ranges import U_Range
# from normalizing_data import Fem_resultN
Fem_resultN=normalize(Fem_result.shape[0],Fem_result.shape[1],Fem_result,U_Range)


#==================This class is responsible for creating the particles and updating the velocity and position for each particle=======
class particle:
    def __init__(self, dimension, population, c1,c2,Xbott,Xtop,Fem_resultN):
        self.position = [] #current position of particles
        self.velocity = [] #current velocity of particles
        self.bestposition = [] # best position met by each particle
        self.Xmax = Xtop
        self.Xmin = Xbott
        self.c1 = c1 #acceleration constant for partivle best postion
        self.c2 = c2 #acceleration constant for global best or group best position
        self.pop = population #how big the population is for intance 100
        self.dim = dimension # dimension of inputs for insttance 5 if we are doing backanalysis for five parameter of soil
        self.creatingparticles() #initilizes the particles and set position of population to randon parameters or assign position to partivcles based on lhs hypercube and set the begining velocity of particles to zero
        self.Fem_resultN=Fem_resultN #FEM solution of construction site data we use for back analysis and our cost finction:||Fem-measurments||
        self.globalbest=[] #the global best of every iteration saves here, we can plot them at the end to see convergence of PSO







    def creatingparticles(self):
        #initilizing positions
        lhd = lhs(self.dim, samples=self.pop)
        self.position = lhd * (self.Xmax - self.Xmin) + self.Xmin
        self.position = self.position.transpose()


        #initilizing velocities
        for i in range(0,self.pop):
            p_vel = np.zeros(self.dim)
            self.velocity.append(p_vel)
        self.velocity = np.asarray(self.velocity)
        self.velocity=self.velocity.transpose()

        #initilizing personal bests:
        self.bestposition = copy.deepcopy(self.position)
        self.bestposition= np.asarray(self.bestposition)


    def updatingvelocity(self,Vmax, Vmin,w): #in PSO we have : X(t+1)=x(t)+v(t), here we calculate v(t), the velocity



        for i in range(0,self.pop):
            self.phi1 = self.c1 * random.uniform(0, 1)
            self.phi2 = self.c2 * random.uniform(0, 1)
            # w = self.phi1 + self.phi2

            index = self.groupbest(i) # here instead of global best we find the group best for each particle and we use it to update the velocity

            # self.velocity[i] = self.chi*(self.velocity[i]+self.phi1*(self.bestposition[i]-self.position[i]) + self.phi2*(globest-self.position[i]))
            self.velocity[:,i] = w*self.velocity[:,i]+self.phi1*(self.bestposition[:,i]-self.position[:,i]) + self.phi2*(self.bestposition[:,index]-self.position[:,i])

            self.velocity[:,i] =  np.where(self.velocity[:,i]<= Vmax,self.velocity[:,i],Vmax)
            self.velocity[:,i] =  np.where(self.velocity[:,i]>= Vmin,self.velocity[:,i],Vmin)
        self.globalbest.append(self.finditerationbest())


# we update the positin of particles based on the calculated velocity
    def updatingposition(self):
        for i in range(0,self.pop):
            self.position[:,i] = self.position[:,i] + self.velocity[:,i]

            #we check the particle position and compare in with the boundary of our domain, in order to not letting the poins leave our searching area
            #based on an article to not let having boundary clamping in pso, if a particle reached the boundaries we will set its new position somewhere in the middle of our searching area.
            self.position[:,i] = np.where(self.position[:,i] <= self.Xmax,self.position[:,i], self.Xmax -(0.5*random.uniform(0,1)*(self.Xmax-self.Xmin)))
            self.position[:,i] = np.where(self.position[:,i] >= self.Xmin,self.position[:,i], self.Xmin +(0.5*random.uniform(0,1)*(self.Xmax-self.Xmin)))


#in every iteration we will compare the current position of a particle and we compare it with the best position it has met so far
    def updatepersonalbest(self):
        for i in range(self.pop):
            # if((la.norm((gp.predict(np.reshape(self.bestposition[:,i].T,(1,self.dim)))-self.Fem_resultN.T)))> (la.norm(((gp.predict(np.reshape(self.position[:,i].T,(1,self.dim)))-self.Fem_resultN.T))))):
            if ((Costfunction(self.bestposition[:, i])) > (Costfunction(self.position[:, i]))):

                x= self.position[:,i]
                self.bestposition[:,i] = x


# we will find the best position in a three membered groups, and we will use the position in our velocity formula
    #it sould be noted that for the first particle, we make group of the particle index 0 1 and -1(last particle)
    #for the last particle we make group as last partcle, one partcle before that and the first particle of the swarm
    def groupbest(self,index):



        #here we just calculate the cost function in the three member of the group and compare them and return the best index.it returns index,index-1 or index+1

        if(index!=self.pop-1): #if it is not the last particle of the swarm
            bestindex = index
            nindex = 0
            # if ((la.norm(gp.predict(np.reshape(self.bestposition[:,index+1].T,(1,self.dim)))-self.Fem_resultN.T)) > (la.norm(gp.predict(np.reshape(self.bestposition[:,index-1].T,(1,self.dim)))-self.Fem_resultN.T))):
            if ((Costfunction(self.bestposition[:,index+1])) > (Costfunction(self.bestposition[:,index-1]))):

                nindex = -1
            # if ((la.norm(gp.predict(np.reshape(self.bestposition[:,index+1].T,(1,self.dim)))-self.Fem_resultN.T))<(la.norm(gp.predict(np.reshape(self.bestposition[:,index-1].T,(1,self.dim)))-self.Fem_resultN.T))):
            if ((Costfunction(self.bestposition[:, index + 1])) < (Costfunction(self.bestposition[:,index-1]))):
                nindex = +1

            if(nindex == 1):
                # if ((la.norm(gp.predict(np.reshape(self.bestposition[:,index+1].T,(1,self.dim)))-self.Fem_resultN.T))> (la.norm(gp.predict(np.reshape(self.bestposition[:,index].T,(1,self.dim)))-self.Fem_resultN.T))):
                if ((Costfunction(self.bestposition[:, index + 1])) > (Costfunction(self.bestposition[:, index]))):
                    nindex =0
            if (nindex == -1):
                # if ((la.norm(gp.predict(np.reshape(self.bestposition[:,index-1].T,(1,self.dim)))-self.Fem_resultN.T))> (la.norm(gp.predict(np.reshape(self.bestposition[:,index].T,(1,self.dim)))-self.Fem_resultN.T))):
                if ((Costfunction(self.bestposition[:, index - 1])) >(Costfunction(self.bestposition[:, index]))):
                    nindex = 0
            bestindex = bestindex + nindex


        if (index == self.pop - 1):
            bestindex = index
            test = 0
            # if (la.norm(np.add(mmeval(self.bestposition[:, index - 1], MMset),-self.Fem_resultN)) < la.norm(np.add(mmeval(self.bestposition[:, index], MMset),-self.Fem_resultN))):
            if(Costfunction(self.bestposition[:, index - 1])<Costfunction(self.bestposition[:, index])):
                test = -1
            bestindex = bestindex + test

        return bestindex


#in pso ring this method has no use, because in the velocity formula we use group best instead the global best,
    #but we still calculate it and print the global best in every iteration
    #in every iteration we supose that the first particle has the best solution(gB as global best), then we compare other particles with that(baed on the artificial intelligence book)
    def finditerationbest(self):

        gB = self.bestposition[:, 0]
        ##this finds the best gBest for every iteration
        for i in range(0, self.position.shape[1]):

            # if ((la.norm(gp.predict(np.reshape(self.bestposition[:,i].T,(1,self.dim)))-self.Fem_resultN.T))< (la.norm(gp.predict(np.reshape(gB.T,(1,self.dim)))-self.Fem_resultN.T))):
            if ((Costfunction(self.bestposition[:,i])< Costfunction(gB))):

                # bestPerIteration.append(Costfunction(gB[-1], self.Fem_resultN, len(self.Xbott)))

                gB = self.bestposition[:, i]


        print(gB)
        bestPerIteration = Costfunction(gB)
        print("Cost Function: ")
        print(bestPerIteration)
        return gB









class PSO:
    def __init__(self,iteration , population, c1,c2,Xbott,Xtop,Fem_resultN):
        self. swarm = particle(len(Xtop),population,c1,c2,Xbott,Xtop,Fem_resultN) # we initilize the swarm based on the information the user gives us in backanalysis.npy
        self.Xbott = Xbott
        self.Xtop = Xtop
        self.iteration = iteration#the user specifies the number of iteration of pso for instance 1000
        self.Fem_resultN=Fem_resultN #fem or construction site outputs

    #optimization process s\tarts with this method
    def optimization(self):

        gB= []#at each iteration the global best will be appended in this list
        bestPerIteration = []#at each iteration the swarm best position will be appended in this list
        swarmposition=[] #at each iteration the whole swarm position will be appended in this list

        # prints the the current iteration number
        for itr in range(0,self.iteration):
            string = "this itr:" +str(itr)
            print(string)

            #at each iteration we will change velocity boundaries, this will give use big or small velocities during the whole iteration
            #this approach provides us with better searching power in whole domain, it works better than having a constant velocity because it might be possible we lose some good positions in our searching domain
            Vmax = np.add(self.Xtop, -self.Xbott) * random.uniform(0, 1)
            Vmin = -Vmax
            w = ((0.9 - 0.4) * (self.iteration - itr) / self.iteration) + 0.4 #inertia factor which gives us better searching ability and denies the velocity clamping(Based on the social inteliigence book)


            swarmposition.append(copy.deepcopy(self.swarm.bestposition))

            #==Updating velocity, positions and best positions======
            self.swarm.updatingvelocity(Vmax,Vmin,w)
            self.swarm.updatingposition()
            self.swarm.updatepersonalbest()
            #========================================================
       
    





        return np.array(self.swarm.globalbest)
