# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:08:19 2019

@author: nya
"""
import sys, os, glob
import numpy as np
from tools.file_tools import remove, savetxt
from platypus import NSGAII, Problem, Real
from platypus.core import Solution
from platypus.operators import InjectedPopulation, SBX
from workflow.evaluate_plaxis2d_model import Evaluate_Plaxis2DModel
from system.run_thread import RunThreadSingle
from tools.list_functions import flatten_list

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
NSGAII_PATH = os.path.join(OPTIMAN, 'nsga2')

class Optiman_NSGAII():
    def __init__(self, problem, N_POPULATION, N_GENERATION=10, initial_population=None):
        self.problem = problem
        self.n_population = N_POPULATION
        self.initial_population = initial_population
        self.algorithm = NSGAII(self.problem, N_POPULATION, variator=SBX())
        self.algorithm_name = 'NSGAII'
        if initial_population is None:
            legal_intial_solutions = self.generate_legal_initial_population(self.algorithm.population_size)
            self.algorithm.generator = InjectedPopulation(legal_intial_solutions)
        else:
            initial_solutions = self.generate_initial_population(initial_population)
            self.algorithm.generator = InjectedPopulation(initial_solutions)
        self.iter = 0
        self.iter_max = N_GENERATION
        self.path_iter = None # path for saving iterative results
        
    
    def check_initial_population_size(self):
        """ Checks the initial population size
        """
        out = True
        if self.initial_population is not None:
            if self.n_population != self.initial_population.shape[0]:   # check size of the initial population
                out = False

        return out


    def setup(self):
        """ Sets up prior to iterating
        """
        # prepare directory for local sensitivity
        if not os.path.exists(OPTIMAN):
            os.makedirs(OPTIMAN)
        if not os.path.exists(NSGAII_PATH):
            os.makedirs(NSGAII_PATH)
        for item in glob.glob(NSGAII_PATH + '\\*'):
            remove(item)
        
        #self.path_output = NSGAII_PATH

    def generate_legal_initial_population(self, population_size):
        """ Generates all legal individuals for the initial population
        """
        solutions = []

        while len(solutions) < population_size:
            solution = Solution(self.problem)
            solution.variables = [x.rand() for x in self.problem.types]
            constraint_value = self.problem.check_legal(solution)
            if constraint_value == 0:
                solutions.append(solution)

        return solutions


    def generate_initial_population(self, initial_population):
        """ Generates individuals for the initial population
        initial_population: numpy array of the initial population, size (populution_size x number of design variables)
        """
        solutions = []

        for i in range(initial_population.shape[0]):
            solution = Solution(self.problem)
            solution.variables = list(initial_population[i, :])
            solutions.append(solution)

        return solutions


    def iterate(self):
        """ Forwards one generation of the NSGAII 
        """
        # create output directory
        self.path_iter = os.path.join(NSGAII_PATH, 'gen_' + str(self.iter + 1).zfill(4))
        if not os.path.exists(self.path_iter):
            os.makedirs(self.path_iter)

        # run one generation
        #self.algorithm.run(self.N_POPULATION)
        self.algorithm.run(1) #ZeroDivisionError, why?

        # save results
        self.save_results()

        # next generation
        self.iter += 1
    

    def save_results(self):
        """ Saves NSGAII results for the current generation
        """
        variables_all_pop = []
        objectives_all_pop = []
        for solution in self.algorithm.result:
            variables_all_pop.append(list(flatten_list(solution.variables)))
            objectives_all_pop.append(solution.objectives)

        dest_variables = os.path.join(self.path_iter, 'variables')
        dest_objectives = os.path.join(self.path_iter, 'objectives')
        savetxt(dest_variables, np.array(variables_all_pop))
        savetxt(dest_objectives, np.array(objectives_all_pop))

