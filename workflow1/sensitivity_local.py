# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 17:21:31 2019

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
SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
LOCAL_SENSITIVITY = os.path.join(SENSIMAN, 'local_sensitivity')

class LocalSensitivity():
    """ This class implements local sensitity analysis
    """
    def __init__(self, Parameters, Parameters_wall, Soilmaterials, Points_obs, m0, m_min, m_max):
        self.m0 = m0                            # mean parameter set
        self.m_min = m_min                      # min parameter set
        self.m_max = m_max                      # max parameter set

        self.m = None                           # current parameter values
        self.Parameters = Parameters            # soil parameters
        self.Parameters_wall = Parameters_wall  # wall parameters
        self.Soilmaterials = Soilmaterials
        self.Points_obs = Points_obs

        self.d_sim = None                       # flattened simulation data (temporary data after returned after each simulation)

        self.iter = 0                           # current iteration
        self.iter_max = 0                       # max iteration
        self.samples_input = None               # np array holding parameter sets to evaluate
        self.misfit = None                      # misfit function for calculating sensitivity scores
        self.path_output = None                 # local sensitivity output path
        

    def check(self):
        """ Checks required parameters and paths
        """
        if not self.Points_obs:
            return 1
        else:
            obs_type = [points_obs['obs_type'] for points_obs in self.Points_obs]
            if len(set(obs_type)) > 1:
                return 2
            else:
                return 0 # passed
        
    
    def setup(self):
        """ Sets up prior to iterating
        """
        # prepare directory for local sensitivity
        if not os.path.exists(SENSIMAN):
            os.makedirs(SENSIMAN)
        if not os.path.exists(LOCAL_SENSITIVITY):
            os.makedirs(LOCAL_SENSITIVITY)
        for item in glob.glob(LOCAL_SENSITIVITY + '\\*'):
            remove(item)
        
        self.path_output = LOCAL_SENSITIVITY

    
    def iterate(self):
        """ Iterates one step forward
        """
        self.m = self.samples_input[self.iter, :] # evaluate this parameter set
        #print(self.m)
        self.d_sim = self.evaluate_function(self.m, self.Parameters, self.Parameters_wall, self.Soilmaterials, self.Points_obs, self.path_output, suffix= '_sample_' + str(self.iter).zfill(3))
        
        file_data_all = os.path.join(self.path_output, 'data_all_sample_' + str(self.iter).zfill(3))
        savetxt(file_data_all, self.d_sim) # combined data for all phases

        # save observed data for each of the phases
        for obs_set in self.Points_obs:
            file_data_phase = os.path.join(self.path_output, 'data_phase_{0}_sample_{1}'.format(obs_set['obs_phase'], str(self.iter).zfill(3)))
            savetxt(file_data_phase, obs_set['data'])

        self.iter += 1

    
    def evaluate_function(self, m, Parameters, Parameters_wall, Soilmaterials, Points_obs, path_output, suffix = ''):
        """ Assigns model parameter, performs forward simulation, and returns requested outputs.
        Returned simulation data are merged and stored in self.d_sim
        """
        # assign model parameters
        pl = plaxis2d()
        cnt_para = pl.assign_model_parameters(m, Parameters, Soilmaterials)
        pl.assign_wall_parameters(m, Parameters_wall, cnt_para)

        # run PLAXIS2D Input
        pl.calculate()
        
        # write output to file
        dest_plaxisinfo = os.path.join(path_output, 'plaxisinfo_' + str(suffix))
        pl.write_plaxis_calc_status(dest_plaxisinfo)
        pl.read_point_outputs(Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
        pl.write_point_outputs_local_sensitivity(Points_obs, path_output, suffix)
        
        return self.merge_simulation_data()


    def merge_simulation_data(self):
        """ Merges simulation data into a nparray vector
        """
        data_all = []
        for obs_set in self.Points_obs:
            data_all.append(obs_set['data'])
        
        return np.concatenate(data_all)


    def generate_input_samples(self):
        """ Generate finite-difference points (samples)
        """
        samples_input = generate_FD_samples(self.m0, self.m_min, self.m_max)
        self.iter_max = samples_input.shape[0]
        self.samples_input = samples_input
        # write to file
        savetxt(os.path.join(LOCAL_SENSITIVITY, 'fd_samples'), samples_input)



    def calc_sensitivity(self, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for the combined (all) data are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        #print(vector_norm)
        
        scores = []
        for i in range(self.m.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_all_sample_' + str(2*i).zfill(3)))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_all_sample_' + str(2*i+1).zfill(3)))
            score = self.misfit(data_xmin, data_xmax)
            scores.append(score)

        return np.array(scores), vector_norm


    def calc_sensitivity_phase(self, phase_number, vector_norm='L2'):
        """ Calculates sensitivity scores after all finite-difference samples are evaluated.
        The sensitivity scores for data at one phase (indexed by phase_number) are calculated.
        """
        self.misfit = getattr(misfit, vector_norm)
        
        scores = []
        for i in range(self.m.size):
            data_xmin = np.loadtxt(os.path.join(self.path_output, 'data_phase_{0}_sample_{1}'.format(phase_number, str(2*i).zfill(3))))
            data_xmax = np.loadtxt(os.path.join(self.path_output, 'data_phase_{0}_sample_{1}'.format(phase_number, str(2*i+1).zfill(3))))
            score = self.misfit(data_xmin, data_xmax)
            scores.append(score)

        return np.array(scores), vector_norm