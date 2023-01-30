# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 08:59:15 2019

@author: nya
"""

import os
import sys
import glob
import numpy as np
from tools.file_tools import savetxt, remove
from optimize import misfit
from solver.plaxis2d.plaxis2d import plaxis2d
from tools.math import generate_FD_samples

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
SENSITIVITY = os.path.join(OPTIMAN, 'sensitivity')

class OptimanSensitivity():
    """ This class implements sensitivity analysis for design optimization
    """
    plaxman_ap = None
    
    def __init__(self, variables_wall, variables_anchors, variables_struts, v0, v_min, v_max, Points_obs, objectives=None):
        
        #self.plaxman_ap = plaxman_ap            # Automated phases used for updating the model and calculation phases
        
        # Merged design variables and their bounds
        self.v0 = v0
        self.v_min = v_min
        self.v_max = v_max
        self.v = None                           # current design variables
        
        self.variables_wall = variables_wall
        self.variables_anchors = variables_anchors
        self.variables_struts = variables_struts
        self.Points_obs = Points_obs            # Observation points for calculating max. wall deflection or max. surface settelment
        self.objectives = objectives            # objectives for optimization
               
        #self.d_sim = None                       # flattened simulation data (temporary data returned after each simulation)

        self.iter = 0                           # current iteration
        self.iter_max = 0                       # max iteration
        self.samples_input = None               # np array holding parameter sets to evaluate
        self.misfit = None                      # misfit function for calculating sensitivity scores
        self.path_output = None                 # local sensitivity output pat
        
        
    def check(self):
        """ Checks required parameters and paths
        """
        check_passed = 0    # passed
        if not self.Points_obs:
            check_passed = 1    # no observed points

        # check if observed data contains wall internal forces. This is for the calculation of reinforcement steel cost
        obs_types = [obs_set['obs_type'] for obs_set in self.Points_obs]
        if 'WallNxMQ_Envelope' not in obs_types:
            check_passed = 2    # no wall internal forces

        return int(check_passed)
    
    
    def setup(self):
        """ Sets up prior to iterating
        """
        # prepare directory for local sensitivity
        if not os.path.exists(OPTIMAN):
            os.makedirs(OPTIMAN)
        if not os.path.exists(SENSITIVITY):
            os.makedirs(SENSITIVITY)
        for item in glob.glob(SENSITIVITY + '\\*'):
            remove(item)
        
        self.path_output = SENSITIVITY
        
        
    def generate_input_samples(self):
        """ Generate finite-difference points (samples)
        """
        samples_input = generate_FD_samples(self.v0, self.v_min, self.v_max)
        self.iter_max = samples_input.shape[0]
        self.samples_input = samples_input
        # write to file
        savetxt(os.path.join(SENSITIVITY, 'fd_samples'), samples_input)
        
        
        
    def iterate(self):
        """ Iterates one step forward
        """
        if self.samples_input.size/self.samples_input.shape[0] == 1.0: # 1 design varialbe
            self.samples_input = np.reshape(self.samples_input, (-1, 1))
        self.v = self.samples_input[self.iter, :] # evaluate this parameter set
        #self.d_sim = self.evaluate_function(self.path_output, suffix= '_sample_' + str(self.iter).zfill(3))
        self.evaluate_function(self.path_output, suffix= '_sample_' + str(self.iter).zfill(3))
        
        #file_data_all = os.path.join(self.path_output, 'data_all_sample_' + str(self.iter).zfill(3))
        #savetxt(file_data_all, self.d_sim) # combined data for all phases

        # Estimate relative cost of the design
        (Nx_max, M_max, Q_max) = self.get_max_wall_forces()
        cost = OptimanSensitivity.plaxman_ap.estimate_total_cost(Nx_max, M_max, Q_max)
        file_data = os.path.join(self.path_output, 'data_Cost_sample_{0}'.format(str(self.iter).zfill(3)))
        savetxt(file_data, [cost])

        self.iter += 1
        
    
    def evaluate_function(self, path_output, suffix = ''):
        """ Assigns model parameter, performs forward simulation, and returns requested outputs.
        Returned simulation data are merged and stored in self.d_sim
        """
        # assign design variables to plaxis model            
        OptimanSensitivity.plaxman_ap.assign_design_variables_to_model(self.v, self.variables_wall, self.variables_anchors, self.variables_struts)
        
        # regenerate calculation phases
        OptimanSensitivity.plaxman_ap.setup_automated_phases_porepressure_interpolation__()
              
        # run PLAXIS2D Input
        pl = plaxis2d()
        pl.calculate()

        # write output to file
        dest_plaxisinfo = os.path.join(path_output, 'plaxisinfo_' + str(suffix))
        pl.write_plaxis_calc_status(dest_plaxisinfo)
        pl.read_point_outputs(self.Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
        #pl.write_point_outputs_data_type(self.Points_obs, path_output, suffix)
        pl.write_point_outputs_data_type_optiman_sensitivity(self.Points_obs, path_output, suffix)
        
        #return self.merge_simulation_data()

    
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


    def calc_sensitivity(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for the combined (all) data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_all_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_all_sample_' + str(2*i+1).zfill(3)))
            #score = self.misfit(data_xmin, data_xmax)
            score = self.misfit(np.max(np.abs(data_xmin)), np.max(np.abs(data_xmax)))
            scores.append(score)

        return np.array(scores), vector_norm


    def calc_sensitivity_objective_WallUx(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for WallUx data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_WallUx_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_WallUx_sample_' + str(2*i+1).zfill(3)))
            #score = self.misfit(data_xmin, data_xmax)
            score = self.misfit(np.max(np.abs(data_xmin)), np.max(np.abs(data_xmax)))
            scores.append(score)

        return np.array(scores)


    def calc_sensitivity_objective_WallNx(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for wall normal force WallNx data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i+1).zfill(3)))
            Nx_xmin = data_xmin[:, 1:3].flatten()
            Nx_xmax = data_xmax[:, 1:3].flatten()
            score = self.misfit(np.max(np.abs(Nx_xmin)), np.max(np.abs(Nx_xmax)))
            scores.append(score)

        return np.array(scores)


    def calc_sensitivity_objective_WallM(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for wall bending moment WallM data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i+1).zfill(3)))
            Nx_xmin = data_xmin[:, 3:5].flatten()
            Nx_xmax = data_xmax[:, 3:5].flatten()
            score = self.misfit(np.max(np.abs(Nx_xmin)), np.max(np.abs(Nx_xmax)))
            scores.append(score)

        return np.array(scores)


    def calc_sensitivity_objective_WallQ(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for wall shear force WallQ data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_WallNxMQ_Envelope_sample_' + str(2*i+1).zfill(3)))
            Nx_xmin = data_xmin[:, 5:7].flatten()
            Nx_xmax = data_xmax[:, 5:7].flatten()
            score = self.misfit(np.max(np.abs(Nx_xmin)), np.max(np.abs(Nx_xmax)))
            scores.append(score)

        return np.array(scores)


    def calc_sensitivity_objective_FoS(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for FoS are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_FoS_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_FoS_sample_' + str(2*i+1).zfill(3)))
            #score = self.misfit(data_xmin, data_xmax)
            score = self.misfit(np.max(np.abs(data_xmin)), np.max(np.abs(data_xmax)))
            scores.append(score)

        return np.array(scores)


    def calc_sensitivity_objective_Cost(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for FoS are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.v.size):
            data_xmin_file = os.path.join(self.path_output, 'data_Cost_sample_' + str(2*i).zfill(3))
            data_xmax_file = os.path.join(self.path_output, 'data_Cost_sample_' + str(2*i+1).zfill(3))
            print('Reading file {0}'.format(data_xmin_file))
            print('Reading file {0}'.format(data_xmax_file))
            data_xmin = np.loadtxt(data_xmin_file)
            data_xmax = np.loadtxt(data_xmax_file)
            #score = self.misfit(data_xmin, data_xmax)
            score = self.misfit(np.max(np.abs(data_xmin)), np.max(np.abs(data_xmax)))
            scores.append(score)

        return np.array(scores)