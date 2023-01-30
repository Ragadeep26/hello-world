# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:08:37 2020

@author: nya
"""

import os, sys
import glob
import numpy as np
from platypus import Problem, Real, Subset
from solver.plaxis2d.plaxis2d import plaxis2d
from tools.file_tools import savetxt
from tools.list_functions import flatten_list

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
NSGAII_PATH = os.path.join(OPTIMAN, 'nsga2')

class Problem_SC_Wrapper(Problem):
    """ This class is a wrapper of Problem for evaluating SPECFEM2D model and getting objectives and constraints.
    The problem at hand is updating the improved soil properties provided by stone colums.
    This problem class is used in combination with Platypus NSGA algorithms.
    """

    def __init__(self, variables_stone_columns, v, v_min, v_max, v_subset, objectives, constraint_items, plaxman_ap):
        nvars = len(v)
        nobjs = len(objectives)
        super().__init__(nvars, nobjs, 1)   # 1 constraint  for all constraint items
        self.types[:] = tuple(Real(v_min[i], v_max[i]) for i in range(nvars))   # design variables' type and min./ max. values
        self.constraints[:] = "==0"
        self.v = v                              # current design variables
        self.set_types(v_min, v_max, v_subset)
        self.variables_stone_columns = variables_stone_columns
        self.objectives = objectives            # The included objectives for optimization
        self.constraint_items = constraint_items    # All constraint items to consider
        self.plaxman_ap = plaxman_ap
        

    def set_types(self, v_min, v_max, v_subset):
        """ Set data types for design variables
        """
        for i in range(len(self.v)):
            if not v_subset[i]: # []
                self.types[i] = Real(v_min[i], v_max[i])    # Real type within min./ max. values
            else:
                self.types[i] = Subset(v_subset[i], 1)      # Subset type with subset values

    
    def check_legal(self, solution):
        """ Checks if a solution is legal or not.
        This function is used for generating an initial population whose individuals are all legal
        """
        self.v = list(flatten_list(solution.variables[:]))     # design variables
        # update design variables to model for stone columns
        self.plaxman_ap.assign_design_variables_to_model_sc(self.v, self.variables_stone_columns)

        # check constraints
        constraint_value = self.plaxman_ap.check_constraints(self.constraint_items)

        return constraint_value # 0 is legal, > 0 is illegal


    #@profile
    def evaluate(self, solution):
        """ Evaluates problem and assigns the evaluated objectives and constraints
        To be used with Platypus, this function must be named 'evaluate'
        """
        self.v = list(flatten_list(solution.variables[:]))     # design variables

        # update design variables to model for stone columns
        self.plaxman_ap.assign_design_variables_to_model_sc(self.v, self.variables_stone_columns)

        # regenerate calculation phases
        #self.plaxman_ap.setup_automated_phases_porepressure_interpolation__()

        # CHECK CONSTRAINTS HERE, RUN FEM EVALUATION ONLY IF CONSTRAINTS ARE PASSED
        constraint_value = self.plaxman_ap.check_constraints(self.constraint_items)

        if constraint_value == 0:
            # calculate stone columns
            u_z_c  = self.plaxman_ap.calculate_stone_columns_no_PLAXIS__()

            path_output = NSGAII_PATH
            isPassed = True
            if isPassed == True: # get simulation data and calculate objectives
                
                file_data = os.path.join(path_output, 'data_u_z_c')
                savetxt(file_data, [u_z_c])
                # estimate relative cost of the design
                cost = self.plaxman_ap.estimate_total_cost_sc()
                file_data = os.path.join(path_output, 'data_Cost')
                savetxt(file_data, [cost])

                # get objectives
                for i, objective in enumerate(self.objectives.keys()):
                    if objective == 'Max SoilUy':     # vertical displacement of horizontally laid plate
                        data_SoilUy = u_z_c*0.001 # !! settlement at top soil [m]
                        solution.objectives[i] = data_SoilUy
                    elif objective == 'Cost':
                        data_Cost = np.loadtxt(os.path.join(path_output, 'data_Cost'))
                        solution.objectives[i] = float(data_Cost)

            else: # PLAXIS2D simulation fails
                solution.objectives[:] = 1.0e10

        else: # unrealistically large objective function values if constraints are not satisfied
            solution.objectives[:] = 1.0e10
        
        # get constraints
        solution.constraints[:] = constraint_value
    

    def get_max_wall_forces(self):
        """ Gets maximum internal wall forces for dimensioning and calculation of reinforcement steel cost
        """
        Nx_max, M_max, Q_max = 0.0, 0.0, 0.0
        for obs_set in self.plaxman_ap.Points_obs:
            if obs_set['obs_type'] == 'WallNxMQ_Envelope':
                Nx_max = np.max(np.abs(obs_set['data'][:, 1:3]))
                M_max = np.max(np.abs(obs_set['data'][:, 3:5]))
                Q_max = np.max(np.abs(obs_set['data'][:, 5:7]))
        
        return Nx_max, M_max, Q_max


