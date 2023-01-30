# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:05:54 2019

@author: nya
"""
import os, sys, glob
import random
from PyQt5 import QtWidgets
#from optimize.pso import Particles
from optimize.pso_vectorized import Particles
from tools.file_tools import savetxt, remove

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
BACKMAN = os.path.join(MONIMAN_OUTPUTS, 'backman')
BACKMAN_PSO = os.path.join(BACKMAN, 'pso')


class Backanalysis_PSO():
    """ This class implements back-analysis workflow based on particle swarm optimization (PSO)
    """
    def __init__(self, d_obs=None, metamodel=None, misfit=None, m_min=None, m_max=None, iter_max=0, population=1, c1=0.5, c2=1.25, structure='Ring'):
        self.d_obs = d_obs                  # flattened measured data
        self.metamodel = metamodel          # metamodel on which PSO back-analysis is based on
        self.misfit = misfit                # cost function for minimization
        self.m_min = m_min                  # minimum parameter values for applying constraints
        self.m_max = m_max                  # maxinum parameter values for applying constraints
        self.swarm = None                   # swarm of particles, needs to be initialized

        self.iter_max = iter_max            # maxinum number of iterations
        self.iter = 0                       # current iteration number 
        self.population = population        # numer of particles in the swarm
        self.c1 = c1                        # acceleration constant for particle best position
        self.c2 = c2                        # acceleration constant for global best or group best position
        self.structure = structure          # structure for velocity updating: Ring or Star

        #self.path_iter = None               # path to data belonging to the current iteration

        #self.setup()                        # set up particles in the swarm


    def check_data(self):
        """ Checks parameters and paths
        """
        if not self.d_obs: # if d_obs is empty
            return False
        else:
            return True
    

    def setup(self):
        """ Sets up run parameters
        """
        # create particles of the swarm
        self.swarm = Particles(self.population, self.c1, self.c2, self.m_min, self.m_max, self.d_obs, self.misfit, self.metamodel)

        # prepare directory for backman
        if not os.path.exists(BACKMAN):
            os.makedirs(BACKMAN)
        if not os.path.exists(BACKMAN_PSO):
            os.makedirs(BACKMAN_PSO)
        #for item in glob.glob(BACKMAN_PSO + '\\iter_*'):
        #    remove(item)

        # run the 1st iteration
        self.iterate()
    

    def iterate(self):
        """ Executes one step of the PSO
        """
        v_max = (self.m_max - self.m_min) * random.uniform(0,1)
        v_min = - v_max
        w = ((0.9 - 0.4) * (self.iter_max - self.iter) / self.iter_max) + 0.4
        self.swarm.update_velocity_star(v_max, v_min, w)
        self.swarm.update_position()
        self.swarm.update_personal_best()

        self.iter += 1


    def main(self):
        """ Executes all iterations of the PSO, for debugging
        """
        QtWidgets.QApplication.processEvents()

        while self.iter < self.iter_max:
            v_max = (self.m_max - self.m_min) * random.uniform(0,1)
            v_min = - v_max
            w = ((0.9 - 0.4) * (self.iter_max - self.iter) / self.iter_max) + 0.4
            if self.structure == 'Ring':
                self.swarm.update_velocity_ring(v_max, v_min, w)
            else:
                self.swarm.update_velocity_star(v_max, v_min, w)

            self.swarm.update_position()
            self.swarm.update_personal_best()

            print('global best: {}'.format(self.swarm.globalbest))
            print('misfit at global best: {}'.format(self.misfit(self.metamodel.predict(self.swarm.globalbest.reshape(1, -1)), self.d_obs['data'])))

            self.iter += 1