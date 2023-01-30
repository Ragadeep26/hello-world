# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 10:51:07 2019

@author: nya
"""
import os
import sys
import numpy as np
from tools.file_tools import savetxt, remove
from solver.plaxis2d.plaxis2d import plaxis2d
from tools.math import generate_LHS_samples

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
METAMODEL = os.path.join(SENSIMAN, 'metamodel')

class Metamodeling():
    """ This class implements metamodeling including random data generation
    and building the meta model
    """
    def __init__(self, Parameters, Parameters_wall, Soilmaterials, Points_obs, iter_):
        """ Initializes Metamodeling attributes
        """
        self.m = None                           # current parameter values
        
        self.Parameters = Parameters            # soil parameters
        self.Parameters_wall = Parameters_wall  # wall parameters
        self.Soilmaterials = Soilmaterials
        self.Points_obs = Points_obs

        self.d_sim = None                       # flattened simulation data (temporary data after returned after each simulation)

        self.iter = iter_                           # current iteration
        self.iter_max = 0                       # max iteration
        self.path_output = None                 # output path
        self.samples_input = None               # np array holding (random) parameter sets to evaluate
        
        
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
        if not os.path.exists(SENSIMAN):
            os.makedirs(SENSIMAN)
        if not os.path.exists(METAMODEL):
            os.makedirs(METAMODEL)

        self.path_output = METAMODEL

    
    def iterate(self):
        """ Iterates one step forward
        """
        self.m = self.samples_input[self.iter, :] # evaluate this parameter set

        self.d_sim = self.evaluate_function(self.m, self.Parameters, self.Parameters_wall, self.Soilmaterials, self.Points_obs, self.path_output, suffix='_sample_' + str(self.iter).zfill(4))

        # write data to file only if data is there (simulation succeeds)
        if self.d_sim is not None:
            file_data_all = os.path.join(self.path_output, 'data_all_sample_' + str(self.iter).zfill(4))
            savetxt(file_data_all, self.d_sim)

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
        isPassed = pl.write_plaxis_calc_status(dest_plaxisinfo)

        # return None if PLAXIS2D simulation fails
        if not isPassed:
            return None

        else:
            pl.read_point_outputs(Points_obs) # read all outputs and store in Points_obs[obs_set]['data']
            pl.write_point_outputs(Points_obs, path_output, suffix)
        
            return self.merge_simulation_data()


    def merge_simulation_data(self):
        """ Merges simulation data into a nparray vector
        """
        data_all = []
        for obs_set in self.Points_obs:
            data_all.append(obs_set['data'])
        
        return np.concatenate(data_all)
        
    
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
        if not os.path.exists(SENSIMAN):
            os.makedirs(SENSIMAN)
        if not os.path.exists(METAMODEL):
            os.makedirs(METAMODEL)
        file_path = os.path.join(METAMODEL, 'lhs_samples')
        savetxt(file_path, samples_input)

        return file_path
