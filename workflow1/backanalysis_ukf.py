# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 09:38:37 2019

@author: nya
"""
import os
import sys
import time
import numpy as np
import glob
from PyQt5 import QtWidgets
from solver.plaxis2d.plaxis2d import plaxis2d
from tools.file_tools import savetxt, remove
from optimize.ukf import ScaledSymSigmaPoints, Ukf, ApplyConstraints
from optimize import misfit

MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
MEASUREMENT = sys.modules['moniman_paths']['MEASUREMENT']
MODEL = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.py')
MATERIAL_LIBRARY = os.path.join(MONIMAN_OUTPUTS,'materials')
PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
PLAXIS2D_SCRIPTING = sys.modules['moniman_paths']['PLAXIS2D_SCRIPTING']
BACKMAN = os.path.join(MONIMAN_OUTPUTS, 'backman')

class Backanalysis_Ukf():
    """ This class implements Back-analysis workflow following the UKF
    """
    def __init__(self, Data=None, Parameters=None, Parameters_wall=None, Soilmaterials=None, Points_obs = None, d_obs = None, m0 = None, m_min = None, m_max = None, P0 = None, Q = None, lambda_ = 1.0, iter_max = 0, WallFootUx_Is_Zero=False):
        """ Initializes observation and model
        """
        self.Parameters = Parameters            # unflattened soil parameters
        self.Parameters_wall = Parameters_wall  # unflattened wall parameters
        self.Soilmaterials = Soilmaterials
        self.Points_obs = Points_obs        # unflattened observation sets
        self.d_obs = d_obs                  # flattened measured data
        self.d_sim = None                   # flattened simulation data (temporary data after returned after each simulation)
        self.m = m0                         # vector of estimated parameters at the current iteration
        self.m_min = m_min                  # minimum parameter values for applying constraints
        self.m_max = m_max                  # maxinum parameter values for applying constraints
        self.P = P0                         # parameter estimation error covariance matrix
        self.Q = Q                          # assumed covariance matrix for process noise
        self.Data = Data                    # measured data, each item corresponds to the observation set in Points_obs
        self.misfit = None                  # misfit function
        self.J = np.nan                     # objective function value
        self.SigPnts = {}                   # sigma-points in 'unscented Kalman filter'
        self.lambda_ = lambda_              # lambda parameter of the 'unscented transformation'
        self.iter = 0                       # current iteration number
        self.iter_max = iter_max            # maximum number of iterations
        self.path_iter = None               # path to data belonging to the current iteration
        self.path_iter0 = None              # path to data belonging to the initial iteration
        self.WallFootUx_Is_Zero = WallFootUx_Is_Zero  # displace WallUx by Ux at toe of the wall
    
    def check_data(self):
        """ Checks parameters and paths
        """
        check_passed = True
        if len(self.Data) < 1:
            check_passed = False
        return check_passed


    def setup(self):
        """ Sets up run parameters. Loading settings for the current iteration when resumed
        """
        QtWidgets.QApplication.processEvents()

        # prepare directory for backman
        if not os.path.exists(BACKMAN):
            os.makedirs(BACKMAN)
        for item in glob.glob(BACKMAN + '\\iter_*'):
            remove(item)

        # select misfit
        self.misfit = getattr(misfit, 'L2')

        # save initial settings
        path_iter0 = os.path.join(BACKMAN, 'iter_' + str(0).zfill(4))
        if not os.path.exists(path_iter0):
            os.makedirs(path_iter0)
        self.d_sim = self.evaluate_function(self.m, self.Parameters, self.Parameters_wall, self.Soilmaterials, self.Points_obs, path_iter0, '_sigPnt_000', self.WallFootUx_Is_Zero)

        innov = self.d_obs['data'] - self.d_sim
        self.J = np.dot(np.mat(innov),np.dot(np.linalg.inv(self.d_obs['R']),np.mat(innov).transpose())) # misfit measure

        self.save_results(path_iter0)

        self.path_iter = path_iter0
        self.path_iter0 = path_iter0    # keep path_iter0


    def iterate(self):
        """ Executes one step of UKF to go to the next iteration
        """
        # create directory for the current iteration
        path_iter = os.path.join(BACKMAN, 'iter_' + str(self.iter + 1).zfill(4))
        if not os.path.exists(path_iter):
            os.makedirs(path_iter)

        # build sigma-points
        (self.SigPnts['xSigPnts'], self.SigPnts['wSigPnts'], 
        self.SigPnts['nSigPnts']) = self.get_sigma_points(self.m, self.P, self.lambda_)
        for i in range(self.SigPnts['nSigPnts']):
            self.SigPnts['xSigPnts'][:,i] = ApplyConstraints(self.SigPnts['xSigPnts'][:,i], self.m_min, self.m_max)

        # evaluate sigma-points
        self.evaluate_sigma_points(path_iter)

        Jx = np.identity(self.m.size) # Jacobian
        PPred = self.Q + np.dot(Jx,np.dot(self.P, Jx.transpose()))	

        # correction
        data = self.d_obs['data']
        R = self.d_obs['R']
        self.m, self.P, innov = Ukf(self.m, PPred, self.Q, self.SigPnts, data, R)

        self.J = np.dot(np.mat(innov),np.dot(np.linalg.inv(R),np.mat(innov).transpose())) # misfit measure

        # save results
        self.save_results(path_iter)

        self.path_iter = path_iter

        self.iter += 1


    def get_sigma_points(self, m, P, lambda_):
        """ Get sigma-points from current mean m and covariance P
        """
        xPts, wPnts, nPts = ScaledSymSigmaPoints(m, P, lambda_)
        return xPts, wPnts, nPts


    def evaluate_sigma_points(self, path_output):
        """ Evaluates all sigma-points
        """
        n = self.d_obs['data'].size
        nSigPnts = self.SigPnts['nSigPnts']
        self.SigPnts['zPredSigPnts'] = np.zeros((n,nSigPnts))

        # tasks 
        queued_tasks = list(range(self.SigPnts['nSigPnts']))
        dest_xSigPnts = os.path.join(path_output, 'sigPnts')
        savetxt(dest_xSigPnts, self.SigPnts['xSigPnts'])

        # run tasks
        while queued_tasks:
            task_i = queued_tasks.pop(0)
            time.sleep(.1)
            # evaluate the sigma-point numbered task_i
            self.SigPnts['zPredSigPnts'][:,task_i] = self.evaluate_function(self.SigPnts['xSigPnts'][:,task_i], self.Parameters, self.Parameters_wall, self.Soilmaterials, self.Points_obs, path_output, '_sigPnt_' + str(task_i).zfill(3), self.WallFootUx_Is_Zero)


    def evaluate_function(self, m, Parameters, Parameters_wall, Soilmaterials, Points_obs, path_output, suffix = '', WallFootUx_Is_Zero=False):
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
        pl.read_point_outputs(Points_obs, WallFootUx_Is_Zero) # read all outputs and store in Points_obs[obs_set]['data']
        pl.write_point_outputs(Points_obs, path_output, suffix)
        
        return self.merge_simulation_data()


    def merge_simulation_data(self):
        """ Merges simulation data into a nparray vector
        """
        data_all = []
        for obs_set in self.Points_obs:
            data_all.append(obs_set['data'])
        
        return np.concatenate(data_all)


    def save_results(self, path_iter):
        """ Saves back-analysis results for the current iteration
        """
        dest_m = os.path.join(path_iter, 'm')
        dest_P = os.path.join(path_iter, 'P')
        dest_J = os.path.join(path_iter, 'J')
        savetxt(dest_m, self.m)
        savetxt(dest_P, self.P)
        savetxt(dest_J, self.J)

