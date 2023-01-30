# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 09:18:53 2020

@author: nya
"""

import os
import sys
import glob
import numpy as np
from tools.file_tools import savetxt, remove
from solver.plaxis2d.plaxis2d import plaxis2d
from tools.math import generate_LHS_samples

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
METAMODEL = os.path.join(OPTIMAN, 'metamodel')


class OptimanMetamodeling():
    """ This class implements metamodeling including random data generation
    and building the meta model
    """
    plaxman_ap = None   # class attribute

    def __init__(self, variables_wall, variables_anchors, variables_struts, v, v_min, v_max, Points_obs, objectives, constraint_items, iter_, check_legal_only=False):
        """ Initializes Metamodeling attributes
        """
        # Merged design variables and their bounds
        self.v0 = v
        self.v_min = v_min
        self.v_max = v_max
        self.v = None                           # current design variables
        
        self.variables_wall = variables_wall
        self.variables_anchors = variables_anchors
        self.variables_struts = variables_struts
        self.Points_obs = Points_obs            # Observation points for calculating max. wall deflection or max. surface settelment
        self.objectives = objectives            # objectives for optimization
               
        #self.d_sim = None                       # flattened simulation data (temporary data returned after each simulation)

        self.iter = iter_                           # current iteration
        self.iter_max = 0                       # max iteration
        self.samples_input = None               # np array holding parameter sets to evaluate
        self.misfit = None                      # misfit function for calculating sensitivity scores
        self.path_output = None                 # local sensitivity output pat
        self.constraint_items = constraint_items    # All constraint items to consider
        self.check_legal_only = check_legal_only    # If this argument is set True, then only the constrainsts are checked. No FEM calculations are performed.
        self.constraints_value = None               # Constraints value (0: legal, >0: illegal)
        self.number_iter_success = 0                # Numer of sucess iterations (used for the report of samples' legal check)
        
        
    def check(self):
        """ Checks required parameters and paths
        """
        check_passed = True
        if not self.Points_obs:
            check_passed = False
        return check_passed

    
    def setup(self):
        """ Sets up prior to iterating
        """
        # prepare directory for local sensitivity
        # prepare directory for local sensitivity
        if not os.path.exists(OPTIMAN):
            os.makedirs(OPTIMAN)
        if not os.path.exists(METAMODEL):
            os.makedirs(METAMODEL)
        #for item in glob.glob(METAMODEL + '\\*'):
        #    remove(item)
        
        self.path_output = METAMODEL

    
    def iterate(self):
        """ Iterates one step forward
        """
        if self.samples_input.size/self.samples_input.shape[0] == 1.0: # 1 design varialbe
            self.samples_input = np.reshape(self.samples_input, (-1, 1))
        self.v = self.samples_input[self.iter, :] # evaluate this parameter set
        #print(self.v)
        if not self.check_legal_only: # normal FEM evaluation
            #(constraintAccepted, d_sim) = self.evaluate_function(self.path_output, suffix= '_sample_' + str(self.iter).zfill(3))
            constraintAccepted = self.evaluate_function(self.path_output, suffix= '_sample_' + str(self.iter).zfill(3))
            #self.d_sim =  d_sim
        
            if constraintAccepted:
            	#file_data_all = os.path.join(self.path_output, 'data_all_sample_' + str(self.iter).zfill(3))
            	#savetxt(file_data_all, self.d_sim) # combined data for all phases

            	# Estimate relative cost of the design
                (Nx_max, M_max, Q_max) = self.get_max_wall_forces()
                cost = OptimanMetamodeling.plaxman_ap.estimate_total_cost(Nx_max, M_max, Q_max)
                file_data = os.path.join(self.path_output, 'data_Cost_sample_{0}'.format(str(self.iter).zfill(3)))
                savetxt(file_data, [cost])

        else: # only check contraints
            self.constraints_value = int(self.get_constraints())
            if self.constraints_value == 0:
                # write out legal samples
                with open(os.path.join(self.path_output, 'lhs_samples_legal'), 'a') as fileout:
                    v_str = ' '.join(str(v_i) for v_i in list(self.v))
                    fileout.write(v_str)
                    fileout.write('\n')
                self.number_iter_success += 1

        self.iter += 1


    def evaluate_function(self, path_output, suffix = ''):
        """ Assigns model parameter, performs forward simulation, and returns requested outputs.
        Returned simulation data are merged and stored in self.d_sim
        """
        # assign design variables to plaxis model            
        OptimanMetamodeling.plaxman_ap.assign_design_variables_to_model(self.v, self.variables_wall, self.variables_anchors, self.variables_struts)
        
        # regenerate calculation phases
        OptimanMetamodeling.plaxman_ap.setup_automated_phases_porepressure_interpolation__()
              
        # CHECK CONSTRAINTS HERE, RUN FEM EVALUATION ONLY IF CONSTRAINTS ARE PASSED
        constraint_value = OptimanMetamodeling.plaxman_ap.check_constraints(self.constraint_items)
        #constraint_value = 0    # for debugging

        if constraint_value == 0:
            # run PLAXIS2D Input
            pl = plaxis2d()
            pl.calculate()

            # write output to file
            dest_plaxisinfo = os.path.join(path_output, 'plaxisinfo_' + str(suffix))
            pl.write_plaxis_calc_status(dest_plaxisinfo)
            pl.read_point_outputs(self.Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
            pl.write_point_outputs_data_type(self.Points_obs, path_output, suffix)
        
            #return (constraint_value == 0), self.merge_simulation_data() # success=True, simulation data
        
        #else:
            #return (constraint_value == 0), 10e10   # success = False, dummy number
        return (constraint_value == 0)   # success = True/ False
    

    def get_constraints(self):
        """ Check if the design variables stored in self.v satisfy design constraints
        """
        # assign design variables to plaxis model            
        OptimanMetamodeling.plaxman_ap.assign_design_variables_to_model(self.v, self.variables_wall, self.variables_anchors, self.variables_struts)
        
        # regenerate calculation phases
        #OptimanMetamodeling.plaxman_ap.setup_automated_phases_porepressure_interpolation__() # time consuming
              
        # CHECK CONSTRAINTS HERE, RUN FEM EVALUATION ONLY IF CONSTRAINTS ARE PASSED
        constraints_value = OptimanMetamodeling.plaxman_ap.check_constraints(self.constraint_items)

        return constraints_value


    #def merge_simulation_data(self):
    #    """ Merges simulation data into a nparray vector
    #    """
    #    data_all = []
    #    for obs_set in self.Points_obs:
    #        data_all.append(obs_set['data'])
    #    
    #    return np.concatenate(data_all)
        

    def get_max_wall_forces(self):
        """ Gets maximum internal wall forces for dimensioning and calculation of reinforcement steel cost
        """
        Nx_max, M_max, Q_max = 0.0, 0.0, 0.0
        for obs_set in self.Points_obs:
            if obs_set['obs_type'] == 'WallNxMQ_Envelope':
                Nx_max = np.max(np.abs(obs_set['data'][:, 1:3]))
                M_max = np.max(np.abs(obs_set['data'][:, 3:5]))
                Q_max = np.max(np.abs(obs_set['data'][:, 5:7]))
        
        return Nx_max, M_max, Q_max
    

    def set_input_samples(self, samples_input):
        """ Sets random inputs
        """
        self.samples_input = samples_input
        self.iter_max = samples_input.shape[0]


    @staticmethod
    def generate_input_samples(m_min, m_max, num_points):
        """ Generate LHS points (samples)
        """
        samples_input = generate_LHS_samples(m_min, m_max, num_points)

        samples_input = samples_input
        # write to file
        if not os.path.exists(OPTIMAN):
            os.makedirs(OPTIMAN)
        if not os.path.exists(METAMODEL):
            os.makedirs(METAMODEL)
        file_path = os.path.join(METAMODEL, 'lhs_samples')
        savetxt(file_path, samples_input)

        # remove lhs_samples_legal
        try:
            os.remove(os.path.join(METAMODEL, 'lhs_samples_legal'))
        except OSError:
            pass

        return file_path
