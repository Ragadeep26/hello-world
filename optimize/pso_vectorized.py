# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:10:12 2019

@author: nya
"""
import numpy as np
import copy
import random
from pyDOE import lhs

class Particles:
    def __init__(self, population, c1, c2, Xbott, Xtop, d_obs, misfit, metamodel):
        self.position = None        # current position of particles
        self.velocity = None        # current velocity of particles
        self.bestposition = None    # best position met by each particle
        self.Xmax = Xtop
        self.Xmin = Xbott
        self.c1 = c1                # acceleration constant for particle best position
        self.c2 = c2                # acceleration constant for global best or group best position
        self.pop = population       # how big the population is for instance 100
        self.create_particles()     # initilizes the particles and set position of population to randon parameters or assign position to particles based on lhs hypercube and set the begining velocity of particles to zero
        self.globalbest = None      # single history global best
        
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
        

    def update_velocity_star(self, Vmax, Vmin,w):
        """ Updates velocity following the start topology
        """
        globest = self.find_iteration_best()

        # c1 and c2 are acceleration constants used to scale the contribution of particle personal best and social personal best.
        phi1 = self.c1 * np.random.uniform(0, 1, (1, self.pop))
        phi2 = self.c2 * np.random.uniform(0, 1, (1, self.pop))

        # this formula can be find in every PSO literatures
        self.velocity = w*self.velocity + np.multiply(phi1, (self.bestposition - self.position)) + np.multiply(phi2, (np.tile(globest.reshape(-1, 1), (1, self.pop)) - self.position))

        # checking boundary condition to avoid velocity clamping
        self.velocity = np.where(self.velocity <= np.tile(Vmax.reshape(-1, 1), (1, self.pop)), self.velocity, np.tile(Vmax.reshape(-1, 1), (1, self.pop)))
        self.velocity = np.where(self.velocity >= np.tile(Vmin.reshape(-1, 1), (1, self.pop)), self.velocity, np.tile(Vmin.reshape(-1, 1), (1, self.pop)))


    def update_velocity_ring(self, Vmax, Vmin,w):
        """ Updates velocity following the ring topology
        """
        groupbest = self.bestposition
        for i in range(0, self.pop):
            groupbest_index = self.find_iteration_groupbest_index(i)
            groupbest[:, groupbest_index-1:(groupbest_index+1) % self.pop] = self.bestposition[:, groupbest_index]

        # c1 and c2 are acceleration constants used to scale the contribution of particle personal best and social personal best.
        phi1 = self.c1 * np.random.uniform(0, 1, (1, self.pop))
        phi2 = self.c2 * np.random.uniform(0, 1, (1, self.pop))

        # this formula can be find in every PSO literatures
        self.velocity = w*self.velocity + np.multiply(phi1, (self.bestposition - self.position)) + np.multiply(phi2, (groupbest - self.position))

        # checking boundary condition to avoid velocity clamping
        self.velocity = np.where(self.velocity <= np.tile(Vmax.reshape(-1, 1), (1, self.pop)), self.velocity, np.tile(Vmax.reshape(-1, 1), (1, self.pop)))
        self.velocity = np.where(self.velocity >= np.tile(Vmin.reshape(-1, 1), (1, self.pop)), self.velocity, np.tile(Vmin.reshape(-1, 1), (1, self.pop)))


    def update_position(self):
        # after calculating velocity, we use it to update the position of each particle past on:x(t+1)=x(t)+v(t)
        self.position = self.position + self.velocity
        
        # we check boundary condition to avoid boundary clamping
        self.position = np.where(self.position <= np.tile(self.Xmax.reshape(-1, 1), (1, self.pop)), self.position,
                                        np.tile(self.Xmax.reshape(-1, 1), (1, self.pop)) - (0.5 * np.multiply(np.random.uniform(0, 1, (1, self.pop)), np.tile((self.Xmax - self.Xmin).reshape(-1, 1), (1, self.pop)))))
        self.position = np.where(self.position >= np.tile(self.Xmin.reshape(-1, 1), (1, self.pop)), self.position,
                                        np.tile(self.Xmin.reshape(-1, 1), (1, self.pop)) + (0.5 * np.multiply(np.random.uniform(0, 1, (1, self.pop)), np.tile((self.Xmax - self.Xmin).reshape(-1, 1), (1, self.pop)))))


    def update_personal_best(self):
        # in this method we find the best position of each point met during iterations, we use this in velocity formula
        d_sim_bestposition = self.metamodel.predict(self.bestposition.transpose())
        d_sim_position = self.metamodel.predict(self.position.transpose())
        for i in range(self.pop):
            if self.misfit(d_sim_bestposition[i, :], self.d_obs['data']) > self.misfit(d_sim_position[i, :], self.d_obs['data']):
                self.bestposition[:, i] = self.position[:, i]


    def find_iteration_best(self):
        # at this method we find the social best in every iteration and we use it in velocity formula for updating the positions
        gB = self.bestposition[:, 0]
        # this finds the best gBest for every iteration
        d_sim_swarm = self.metamodel.predict(self.bestposition.transpose())
        d_sim_gB = self.metamodel.predict(gB.reshape(1, -1))
        misfit_gB = self.misfit(d_sim_gB, self.d_obs['data'])
        for i in range(0, self.position.shape[1]):
            if self.misfit(d_sim_swarm[i, :], self.d_obs['data']) < misfit_gB:
                gB = self.bestposition[:, i]
                d_sim_gB = self.metamodel.predict(gB.reshape(1, -1))
                misfit_gB = self.misfit(d_sim_gB, self.d_obs['data'])

        self.globalbest = gB

        return gB


    def find_iteration_groupbest_index(self, particle_index):
        """ Finds best position in a three-member group
        """
        d_sim_bestposition = self.metamodel.predict(self.bestposition.transpose())

        groupbest_index = particle_index
        if (self.misfit(d_sim_bestposition[:, particle_index - 1], self.d_obs['data']) < self.misfit(d_sim_bestposition[:, particle_index], self.d_obs['data'])) \
            and (self.misfit(d_sim_bestposition[:, particle_index - 1], self.d_obs['data']) < self.misfit(d_sim_bestposition[:, (particle_index + 1) % self.pop], self.d_obs['data'])):
            groupbest_index -= 1
        elif (self.misfit(d_sim_bestposition[:, (particle_index + 1) % self.pop], self.d_obs['data']) < self.misfit(d_sim_bestposition[:, particle_index], self.d_obs['data'])) \
            and (self.misfit(d_sim_bestposition[:, (particle_index + 1) % self.pop], self.d_obs['data']) < self.misfit(d_sim_bestposition[:, particle_index - 1], self.d_obs['data'])):
            groupbest_index += 1

        return groupbest_index
            

            


