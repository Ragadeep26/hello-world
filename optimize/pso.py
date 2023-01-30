# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:10:12 2019

@author: nya
"""

import  numpy as np
import copy
import random
from pyDOE import lhs
#from Fitnessfunction import Costfunction

class Particles:
    def __init__(self, population, c1, c2, Xbott, Xtop, d_obs, misfit, metamodel):
        self.position = None        # current position of particles
        self.velocity = []          # current velocity of particles
        self.bestposition = []      # best position met by each particle
        self.Xmax = Xtop
        self.Xmin = Xbott
        self.c1 = c1                # acceleration constant for particle best position
        self.c2 = c2                # acceleration constant for global best or group best position
        self.pop = population       # how big the population is for instance 100
        self.create_particles()     # initilizes the particles and set position of population to randon parameters or assign position to particles based on lhs hypercube and set the begining velocity of particles to zero
        #self.globalbest = []        # the global best of every iteration saves here, we can plot them at the end to see convergence of PSO
        self.globalbest = None      # single global best
        
        self.d_obs = d_obs          # measured data
        self.misfit = misfit        # objective function to minimize
        self.metamodel = metamodel  # metamodel

    def create_particles(self):
        #initilizing positions
        lhd = lhs(self.Xmax.size, samples=self.pop)
        self.position = (lhd * (self.Xmax - self.Xmin) + self.Xmin).transpose()

        #initilizing velocities
        self.velocity = np.zeros((self.Xmax.size, self.pop))

        #initilizing personal bests:
        self.bestposition = copy.deepcopy(self.position)
        

    def update_velocity(self, Vmax, Vmin,w):
        globest = self.find_iteration_best()
        for i in range(0,self.pop):
            #c1 and c2 are acceleration constants used to scale the contribution of particle personal best and social personal best.
            self.phi1 = self.c1 * random.uniform(0, 1)
            self.phi2 = self.c2 * random.uniform(0, 1)

            #this formula can be find in every PSO literatures
            self.velocity[:,i] = w*self.velocity[:,i] +self.phi1*(self.bestposition[:,i] -self.position[:,i] ) + self.phi2*(globest-self.position[:,i] )

            #checking boundary condition to avoid velocity clamping
            self.velocity[:, i] = np.where(self.velocity[:, i] <= Vmax, self.velocity[:, i], Vmax)
            self.velocity[:, i] = np.where(self.velocity[:, i] >= Vmin, self.velocity[:, i], Vmin)


    def update_position(self):
        # after calculating velocity, we use it to update the position of each particle past on:x(t+1)=x(t)+v(t)
        for i in range(0,(self.pop)):
            self.position[:,i] = self.position[:,i] + self.velocity[:,i]
            # we check boundary condition to avoid boundary clamping
            self.position[:, i] = np.where(self.position[:, i] <= self.Xmax, self.position[:, i],
                                           self.Xmax - (0.5 * random.uniform(0, 1) * (self.Xmax - self.Xmin)))

            self.position[:, i] = np.where(self.position[:, i] >= self.Xmin, self.position[:, i],
                                           self.Xmin + (0.5 * random.uniform(0, 1) * (self.Xmax - self.Xmin)))


    def update_personal_best(self):
        # in this method we find the best position of each point met during iterations, we use this in velocity formula
        for i in range(self.pop):
            if self.misfit(self.metamodel.predict(self.bestposition[:, i].reshape(1, -1)), self.d_obs['data']) > self.misfit(self.metamodel.predict(self.position[:, i].reshape(1, -1)), self.d_obs['data']):
                self.bestposition[:, i] = self.position[:, i]


    def find_iteration_best(self):
        # at this method we find the social best in every iteration and we use it in velocity formula for updating the positions
        gB = self.bestposition[:, 0]
        # this finds the best gBest for every iteration
        for i in range(0, self.position.shape[1]):
            if self.misfit(self.metamodel.predict(self.bestposition[:,i].reshape(1, -1)), self.d_obs['data']) < self.misfit(self.metamodel.predict(gB.reshape(1, -1)), self.d_obs['data']):
                gB = self.bestposition[:, i]

        self.globalbest = gB

        #self.globalbest.append(gB)
        #print(gB)
        #bestPerIteration = self.misfit(self.metamodel.predict(gB), self.d_obs['data'])
        #print("Cost Function: ")
        #print(bestPerIteration)

        return gB
