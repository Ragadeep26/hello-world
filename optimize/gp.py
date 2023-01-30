# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:49:28 2019

@author: nya
"""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, RationalQuadratic, Matern, WhiteKernel
#from sklearn.gaussian_process.kernels import WhiteKernel, ConstantKernel as C
from PyQt5 import QtWidgets

class GaussianProcess():
    def __init__(self, samples, kernel_coeffs=[1.0, 1.0, 1.0]):
        self.data_train_x = samples['data_train_x']
        self.data_train_y = samples['data_train_y']
        self.data_validate_x = samples['data_validate_x']
        self.data_validate_y = samples['data_validate_y']
        self.length_scale = []
        self.kernel = None
        self.kernel_coeffs = kernel_coeffs
        self.gp = None
        
        self.set_length_scale()
        self.set_kernel()
        
    
    def set_length_scale(self):
        """ Sets length scales as fractions of ranges in parameter space
        """
        n = self.data_train_x.shape[1] # number of parameters
        for i in range(n):
            param_max = np.max(self.data_train_x[:,i])
            param_min = np.min(self.data_train_x[:,i])
            self.length_scale.append((param_max - param_min)/10)
        
        #print(self.length_scale)
        
    def set_kernel(self):
        """ Sets generic kernel in relation to ranges in parameter space
        """
        #self.kernel = 1*RBF(length_scale=self.length_scale) + RationalQuadratic(length_scale=0.1) + Matern(length_scale=self.length_scale)
        #self.kernel = self.kernel_coeffs[0]*RBF(length_scale=self.length_scale) + self.kernel_coeffs[1]*RationalQuadratic(length_scale=0.1) + self.kernel_coeffs[2]*Matern(length_scale=self.length_scale)
        #self.kernel = self.kernel_coeffs[0]*RBF(length_scale=self.length_scale) + self.kernel_coeffs[1]*RationalQuadratic(length_scale=0.1) 

        base_functions = [RBF(length_scale=self.length_scale), RationalQuadratic(length_scale=0.1), Matern(length_scale=self.length_scale)]
        kernel = 0.00001*RBF(length_scale=self.length_scale)
        for coeff, base in zip(self.kernel_coeffs, base_functions):
            if int(coeff) != 0:
                kernel += coeff*base 

        self.kernel = kernel
        self.gp = GaussianProcessRegressor(kernel=self.kernel, n_restarts_optimizer=9)
        
    

    #def train(self):
    def run(self):
        """ Trains the gaussian process model
        """
        #QtWidgets.QApplication.processEvents() # allows other IO processes (like print)

        self.gp.fit(self.data_train_x, self.data_train_y)

        
    def validate(self):
        """ Validates the gaussian process model
        """
        score = self.gp.score(self.data_validate_x, self.data_validate_y)
        y_predict = self.gp.predict(self.data_validate_x)

        return score, y_predict