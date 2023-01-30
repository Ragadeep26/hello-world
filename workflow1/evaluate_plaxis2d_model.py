# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 11:09:53 2019

@author: nya
"""

import os
from tools.file_tools import savetxt

class Evaluate_Plaxis2DModel():
    """ This class implements the single evaluation of the current PLAXIS2D model.
    No parameter assignment to the model is involved.
    Read and store output database if requested.
    """
    def __init__(self, Points_obs=None, path_output=None):
        """ Initializes Evaluate_Plaxis2DModel
        """
        self.Points_obs = Points_obs
        #self.obs_points = obs_points            # observation points 
        #self.obs_phase = obs_phase              # observation phase 
        #self.obs_type = obs_type                # observation points 
        self.path_output = path_output          # output path
        
        
    def check(self):
        """ Checks required parameters and paths
        """
        pass

    
    def setup(self):
        """ Sets up prior to iterating
        """
        pass

    
    def run(self):
        """ Runs model
        """

        self.evaluate_function(self.Points_obs, self.path_output)

    
    def evaluate_function(self, Points_obs, path_output, suffix = ''):
        """ Performs forward simulation and returns requested outputs
        """
        from solver.plaxis2d.plaxis2d import plaxis2d
        pl = plaxis2d()

        # run PLAXIS2D Input
        pl.calculate()
        

        if self.path_output is not None:
            # write calculation status
            dest_plaxisinfo = os.path.join(path_output, 'plaxisinfo_' + suffix)
            pl.write_plaxis_calc_status(dest_plaxisinfo)

            # read all requested outputs from database and store in Points_obs
            pl.read_point_outputs(Points_obs)
            #for obs_set in Points_obs:
            #    print(obs_set['data'])

            # write all requested outputs to disc
            pl.write_point_outputs(Points_obs, path_output, suffix)