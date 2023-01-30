# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 16:34:14 2022

@author: nya
"""
from abc import ABC, abstractmethod
import math

alpha_buckling_curves = {'a0': 0.13, 'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}

class crossSection(object):
    """ Base class for cross section"""
    def __init__(self, fyk, psf):
        self.fyk = fyk  # characteristic yield strength, MPa
        self.psf = psf
        self.epsilon = math.sqrt(235.0/self.fyk)

        # dummy values used for common calculation
        self.W_el_y = 1.0
        self.W_el_z = 1.0
        self.W_pl_y = 1.0
        self.W_pl_z = 1.0
        self.Iyy = 1.0
        self.Izz = 1.0
        self.buckling_curve = 'a'
        self.A = 1.0
        self.N_pl_d = 1.0
        self.QK = int(1)        # cross-section class


    @abstractmethod
    def get_cross_section_class(self):
        """ Gets cross section class
        To be implemented in concrete class
        """
        pass


    def get_additional_data_for_design(self, sy, sz, design_loads):
        """ Gets additional data for design
        sy, sz: buckling lengths
        """
        self.get_alpha_pl()
        self.get_N_cr(sy, sz)
        self.get_reduction_factor_chi_buckling()
        self.get_reduction_factor_k_moment(design_loads['Nd'])
        self.get_N_pl_Rd()
        self.get_M_pl_Rd()
        self.perform_design_checks_flexural_buckling(design_loads)


    def get_alpha_pl(self):
        """ Gets ratio W_pl/W_el
        """
        self.alpha_pl_y = self.W_pl_y/self.W_el_y
        self.alpha_pl_z = self.W_pl_z/self.W_el_z


    def get_N_cr(self, sy, sz):
        """ Gets buclking force N_cr [kN]
        sy, sz: buckling lengths
        """
        self.N_cr_yy = math.pi**2*210.0e6*self.Iyy*1.0e-8/sy**2    # kN
        self.N_cr_zz = math.pi**2*210.0e6*self.Izz*1.0e-8/sz**2    # kN
    

    def get_reduction_factor_chi_buckling(self):
        """ Gets reduction factor chi for buckling
        """
        if len(self.buckling_curve) == 1:    # tube
            alpha = alpha_buckling_curves[self.buckling_curve]     # imperfection factor alpha for buckling curve
            self.alpha_y = alpha
            self.alpha_z = alpha
        else: # profile, buckling curve for web and flange
            self.alpha_y = alpha_buckling_curves[self.buckling_curve.split('\\/')[0]]     # imperfection factor alpha for buckling curve
            self.alpha_z = alpha_buckling_curves[self.buckling_curve.split('\\/')[1]]     # imperfection factor alpha for buckling curve

        self.lambda_bar_yy = math.sqrt(self.A*self.fyk*0.1/self.N_cr_yy)
        self.lambda_bar_zz = math.sqrt(self.A*self.fyk*0.1/self.N_cr_zz)
        phi_yy = 0.5*(1+(self.alpha_y*(self.lambda_bar_yy - 0.2)) + self.lambda_bar_yy**2)
        phi_zz = 0.5*(1+(self.alpha_z*(self.lambda_bar_zz - 0.2)) + self.lambda_bar_zz**2)
        self.chi_yy = 1/(phi_yy + (phi_yy**2 - self.lambda_bar_yy**2)**0.5)
        self.chi_zz = 1/(phi_zz + (phi_zz**2 - self.lambda_bar_zz**2)**0.5)



    def get_reduction_factor_k_moment(self, N_d):
        """ Gets reduction factors kyy, kzz for moments
        N_d: design compression force, kN
        """
        n_y = math.fabs(N_d/(self.chi_yy*(self.N_pl_d*self.psf['gamma_M0']/self.psf['gamma_M1'])))
        n_z = math.fabs(N_d/(self.chi_zz*(self.N_pl_d*self.psf['gamma_M0']/self.psf['gamma_M1'])))
        c_LT = 1.0  # Zeta, Schneider S. 8.34

        if self.QK < 3:
            k_yy_a = c_LT * (1 + (self.lambda_bar_yy - 0.2)*n_y)
            k_yy_b = c_LT * (1 + 0.8*n_y)
            k_zz_a = c_LT * (1 + (self.lambda_bar_zz - 0.2)*n_z)
            k_zz_b = c_LT * (1 + 0.8*n_z)
        else:   # for cross-section class 3
            k_yy_a = c_LT * (1.0 + 0.6*self.lambda_bar_yy*n_y)
            k_yy_b = c_LT * (1.0 + 0.6*n_y)
            k_zz_a = c_LT * (1.0 + 0.6*self.lambda_bar_zz*n_z)
            k_zz_b = c_LT * (1.0 + 0.6*n_z)

        self.k_yy = min(k_yy_a, k_yy_b)
        self.k_zz = min(k_zz_a, k_zz_b)
    

    def get_N_pl_Rd(self):
        """ Gets N_pl_Rd
        """
        self.N_pl_Rd = self.A * self.fyk * 0.1 / self.psf['gamma_M1']


    def get_M_pl_Rd(self):
        """ Gets M_pl_Rd
        """
        self.M_pl_Rd_y = self.W_pl_y * self.fyk * 0.001 / self.psf['gamma_M1']
        self.M_pl_Rd_z = self.W_pl_z * self.fyk * 0.001 / self.psf['gamma_M1']


    def perform_design_checks_flexural_buckling(self, design_loads):
        """ Performs design checks
        """
        if self.QK < 3: # QK 1/2: plastic resistance
            Wy = self.W_pl_y
            Wz = self.W_pl_z
        else:   # QK 3: elastic resistance
            Wy = self.W_el_y
            Wz = self.W_el_z

        M_y_Rk = self.fyk*Wy* 1000/(100**3)    # Wy depends on QK, kNm
        M_z_Rk = self.fyk*Wz* 1000/(100**3)    # Wy depends on QK, kNm

        self.util_N_d_y = design_loads['Nd'] / (self.chi_yy * self.N_pl_Rd)
        self.util_N_d_z = design_loads['Nd'] / (self.chi_zz * self.N_pl_Rd)
        #self.util_M_d_y = abs(design_loads['Myd']) * self.k_yy / self.M_pl_Rd_y
        #self.util_M_d_z = abs(design_loads['Mzd']) * self.k_zz / self.M_pl_Rd_z
        self.util_M_d_y = abs(design_loads['Myd']) * self.k_yy / (M_y_Rk/self.psf['gamma_M1'])
        self.util_M_d_z = abs(design_loads['Mzd']) * self.k_zz / (M_z_Rk/self.psf['gamma_M1'])
        self.util_total_y = self.util_N_d_y + self.util_M_d_y
        self.util_total_z = self.util_N_d_z + self.util_M_d_z