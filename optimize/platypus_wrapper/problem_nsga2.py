# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 13:39:17 2019

@author: nya
"""
#from memory_profiler import profile
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

class Problem_Wrapper(Problem):
    """ This class is a wrapper of Problem for evaluating SPECFEM2D retaining wall model and getting objectives and constraints.
    This problem class is used in combination with Platypus NSGA algorithms.
    """

    #plaxman_ap = None      # class attribute for handing the model parameter asissignment and generating calculation phases

    def __init__(self, variables_wall, variables_anchors, variables_struts, v, v_min, v_max, v_subset, objectives, constraint_items, plaxman_ap):
        nvars = len(v)
        nobjs = len(objectives)
        super().__init__(nvars, nobjs, 1)   # 1 constraint  for all constraint items
        #self.types[:] = tuple(Real(v_min[i], v_max[i]) for i in range(nvars))   # design variables' type and min./ max. values
        self.constraints[:] = "==0"
        self.v = v                              # current design variables
        self.set_types(v_min, v_max, v_subset)
        self.variables_wall = variables_wall
        self.variables_anchors = variables_anchors
        self.variables_struts = variables_struts
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
    
    #def set_directions(self):
    #    """ 
    #    """
    #    for i, key in enumerate(self.objectives.keys()):
    #        if key == 'FoS':
    #            self.directions[i] = Problem.MAXIMIZE
    #        else:
    #            self.directions[i] = Problem.MINIMIZE


    def check_legal(self, solution):
        """ Checks if a solution is legal or not.
        This function is used for generating an initial population whose individuals are all legal
        """
        self.v = list(flatten_list(solution.variables[:]))     # design variables
        # update design variables to model
        self.plaxman_ap.assign_design_variables_to_model(self.v, self.variables_wall, self.variables_anchors, self.variables_struts)

        # regenerate calculation phases, time consuming!!
        #self.plaxman_ap.plaxman_ap.setup_automated_phases_porepressure_interpolation__()

        # check constraints
        constraint_value = self.plaxman_ap.check_constraints(self.constraint_items)

        return constraint_value # 0 is legal, > 0 is illegal


    #@profile
    def evaluate(self, solution):
        """ Evaluates problem and assigns the evaluated objectives and constraints
        To be used with Platypus, this function must be named 'evaluate'
        """
        self.v = list(flatten_list(solution.variables[:]))     # design variables
        
        # update design variables to model
        self.plaxman_ap.assign_design_variables_to_model(self.v, self.variables_wall, self.variables_anchors, self.variables_struts)

        # regenerate calculation phases
        self.plaxman_ap.setup_automated_phases_porepressure_interpolation__()

        # CHECK CONSTRAINTS HERE, RUN FEM EVALUATION ONLY IF CONSTRAINTS ARE PASSED
        constraint_value = self.plaxman_ap.check_constraints(self.constraint_items)

        if constraint_value == 0:
            # run PLAXIS2D Input
            pl = plaxis2d()
            pl.calculate()
    
            # write FEM outputs
            suffix = ''
            path_output = NSGAII_PATH
            dest_plaxisinfo = os.path.join(path_output, 'plaxisinfo_' + str(suffix))
            pl.write_plaxis_calc_status(dest_plaxisinfo)

            # check if PLAXIS2D simulation is sucessful 
            isPassed = False
            plaxisinfo = 'plaxisinfo' + '_*'
            reg_expr = os.path.join(path_output, plaxisinfo)
            for fname in glob.glob(reg_expr):
                if 'PASSED' in fname:
                    isPassed = True
                    break

            if isPassed == True: # get simulation data and calculate objectives
                #pl.read_point_outputs(Problem_Wrapper.plaxman_ap.Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
                pl.read_point_outputs(self.plaxman_ap.Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
                #pl.write_point_outputs_data_type(Problem_Wrapper.plaxman_ap.Points_obs, path_output, suffix)
                pl.write_point_outputs_data_type(self.plaxman_ap.Points_obs, path_output, suffix)
                # estimate relative cost of the design
                (Nx_max, M_max, Q_max) = self.get_max_wall_forces()
                #cost = Problem_Wrapper.plaxman_ap.estimate_total_cost(self.v, self.variables_wall, self.variables_anchors, Nx_max, M_max, Q_max)
                cost = self.plaxman_ap.estimate_total_cost(Nx_max, M_max, Q_max)
                file_data = os.path.join(path_output, 'data_Cost')
                savetxt(file_data, [cost])

                # get objectives
                for i, objective in enumerate(self.objectives.keys()):
                    if objective == 'Max WallUx':
                        #data_WallUx = np.loadtxt(os.path.join(path_output, 'data_WallUx'))
                        data_WallUx = np.zeros(0)
                        for points_obs in self.plaxman_ap.Points_obs:
                            if points_obs['obs_type'] == 'WallUx':
                                data_WallUx = np.hstack(points_obs['data'])
                        solution.objectives[i] = np.max(np.abs(data_WallUx))
                    elif objective == 'Max WallUy':     # vertical displacement of horizontally laid plate
                        data_WallUy = np.zeros(0)
                        for points_obs in self.plaxman_ap.Points_obs:
                            if points_obs['obs_type'] == 'WallUy':
                                data_WallUy = np.hstack(points_obs['data'])
                        solution.objectives[i] = np.max(np.abs(data_WallUy))
                    elif objective == 'FoS':
                        #data_FoS = np.loadtxt(os.path.join(path_output, 'data_FoS'))
                        for points_obs in self.plaxman_ap.Points_obs:
                            if points_obs['obs_type'] == 'FoS':
                                data_FoS = points_obs['data']
                        solution.objectives[i] = - float(data_FoS[0]) # !!NEGATION for FoS
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


