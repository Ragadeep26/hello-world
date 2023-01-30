# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 14:24:14 2020

@author: nya
"""

import numpy as np

class FDC_Loading():
    def __init__(self, G=60.0, Q=40.0, gammaG=1.35, gammaQ=1.5):
        self.G = G  # kPa
        self.Q = Q  # kPa
        self.gammaG = gammaG
        self.gammaQ = gammaQ
    

    def set_G(self, value):
        """ Sets new value for G
        """
        self.G = value


    def set_Q(self, value):
        """ Sets new value for Q
        """
        self.Q = value


    def set_gammaG(self, value):
        """ Sets new value for gammaG
        """
        self.gammaG = value


    def set_gammaQ(self, value):
        """ Sets new value for gammaG
        """
        self.gammaQ = value


    def get_q0(self):
        """ Gets stress at the LTP base
        """
        return self.G*self.gammaG + self.Q*self.gammaQ


    def get_q0_unfactored(self):
        """ Gets stress at the LTP base
        """
        return self.G + self.Q


    def get_Q(self, a):
        """ Gets load applied on the unit rectangular grid
        a: spacing between columns (FDC.FDC_params['a'])
        """
        q0 = self.get_q0()
        A = a*a
        return q0*A


    def get_gamma_eq_ULS(self):
        """
        """
        gamma = (self.gammaG*self.G + self.gammaQ*self.Q)/(self.G + self.Q)
        return gamma

    
class LTP_calc():
    """ This class implements the limit stresses q_p_plus and p_s_plus w.r.t. the LTP thickness
    """
    def __init__(self, LTP_params, FDC_params, FDC_loading):
        self.LTP_params = LTP_params
        self.FDC_params = FDC_params
        self.FDC_loading = FDC_loading


    def get_alpha(self):
        """ Gets ratio of area replacemnt A_p/As
        """
        Ap = (self.FDC_params['Dc']**2) * np.pi * 1/4
        As = self.FDC_params['a'] * self.FDC_params['a']
        return Ap/As


    def get_Nq_Prandtl(self):
        """ Gets dimensionless factor Nq
        """
        phi_in_rad = self.LTP_params['phi']*np.pi/180
        s1 = np.tan(np.pi/4 + phi_in_rad/2)
        s2 = np.pi*np.tan(phi_in_rad)
        s = s1**2 * np.exp(s2)
        return s


    def get_Nc_Prandtl(self):
        """ Gets dimensionless factor Nc
        """
        phi_in_rad = self.LTP_params['phi']*np.pi/180
        Nq = self.get_Nq_Prandtl()
        s1 = 1/np.tan(phi_in_rad)
        s = (Nq - 1)*s1
        return s


    def get_q_p_plus(self, q0):
        """ Gets (vertical) stress on columns
        q0: average total stress at the LTP base
        """
        Nq = self.get_Nq_Prandtl()
        Nc = self.get_Nc_Prandtl()
        #print('Nq: ', Nq)
        #print('Nc: ', Nc)
        alpha = self.get_alpha()

        s_q = self.LTP_params['s_q']
        s_c = self.LTP_params['s_c']
        c = self.LTP_params['c']
        s1 = s_q*Nq*q0
        s2 = s_c*Nc*c*(1-alpha)
        s3 = 1.0 - alpha + s_q*Nq*alpha
        s = (s1 + s2)/s3
        return s


    def get_q_s_plus(self, q0, q_p_plus):
        """ Gets (vertical) stress acting on soil
        q0: average total stress at the LTP base
        q_p_plus: vertical stress on columns
        """
        alpha = self.get_alpha()

        s = (q0 - alpha*q_p_plus)/(1-alpha)
        return s
        
    
    def get_H_max(self):
        """ Gets height of Prandtl mechanism
        """
        phi_in_rad = self.LTP_params['phi']*np.pi/180
        Dc = self.FDC_params['Dc']

        h1 = Dc/2 * np.tan(np.pi/4 + phi_in_rad/2)
        theta_max = np.arctan(1/np.tan(phi_in_rad))
        r0 = Dc * np.exp(np.tan(phi_in_rad)*np.pi/2) * 1/(2*np.cos(np.pi/4 + phi_in_rad/2))

        h2 = r0 * np.exp(-np.tan(phi_in_rad)*(theta_max - (np.pi/4 - phi_in_rad/2))) * np.sin(theta_max) - h1
        #print('h1: ', h1)
        #print('theta_max: ', theta_max)
        #print('r0: ', r0)
        #print('h2: ', h2)

        H_max = h1 + h2

        return (H_max, h1, h2)


    def get_q_p_Rd(self, q_s_plus, f_cd, H_max, h1, h2, hM):
        """ Gets limit (allowable) pressure of the LTP material
        """
        phi_in_rad = self.LTP_params['phi']*np.pi/180
        nabla_in_rad = self.LTP_params['nabla']*np.pi/180
        gammaR = self.LTP_params['gammaR']
        Nd0 = (np.tan(phi_in_rad) + np.sqrt(1 + np.tan(phi_in_rad)**2))**2 * np.exp(2*nabla_in_rad*np.tan(phi_in_rad))
        
        q_p_Rd = Nd0*q_s_plus/gammaR
        q_p_Rd_h1 = (f_cd - q_p_Rd)*h2/H_max + q_p_Rd
        m = f_cd - q_p_Rd
        k = -np.log(1/m)/(H_max**3)/2
        n = np.log(np.log((q_p_Rd_h1 - q_p_Rd)/m)/(-k)) / np.log(h1)
        q_p_Rd_adj = m*np.exp(-k*hM**n) + q_p_Rd

        q_p_min = q_p_Rd
        q_p_max = f_cd

        #print(q_p_Rd)

        return (max(q_p_Rd, q_p_Rd_adj), q_p_min, q_p_max, k, n)

    
    def get_q_p_Rd_Menard(self, q_p_plus, f_cd, H_max, hM):
        """ Gets limit (allowable) pressure of the LTP material following Menard
        """

        q_p_Rd = f_cd + hM/H_max*(q_p_plus - f_cd)

        return min(q_p_Rd, f_cd)