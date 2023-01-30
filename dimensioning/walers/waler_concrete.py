# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:34:14 2023

@author: nya
"""
import numpy as np
from dimensioning.py_StB.StB_R_As_and_a_s import StB_R_MN, StB_R_Q

class walerConcrete(object):
    """ Class for concrete waler beam
    """
    def __init__(self, fck, fyk, psf, b, h, edge_sep):
        self.fck = fck
        self.fyk = fyk
        self.psf = psf          # partial safety factors
        self.b = b              # cross-section width, m
        self.h = h              # cross-section height, m
        self.co = edge_sep      # concrete cover, mm
    

    def get_required_reinforcements(self, Nd, Md, Qd):
        """ Gets the required reinforcement for rectangular RC cross-section
        """
        code = 3
        D, B, H1, H2 = self.b*1000, self.h*1000-2*self.co, self.co, self.co   # units are mm
        sym = False  # non-symmetry gives very low As !!
        alpha = 0.85
        eps_c2 = 2.0/1000
        eps_c2u = 3.5/1000
        exp = 2.0
        delta_S = 0.15
        delta_K = '0.15 0.0'
        Es = 200000.0 # MPa
        eps_su = 25.0/1000
        RissP1 = 0.0
        minBew = 1
        A_s1_i = StB_R_MN(code, self.psf['gamma_c'], self.psf['gamma_s'], Md, Nd, Md/self.psf['permanent'], Nd/self.psf['permanent'], D, B, H1, H2, sym, 1.5, 0.0 , self.fck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, self.fyk, self.fyk*1.05, Es, eps_su, RissP1, minBew, 17)   # tension side
        A_s2_i = StB_R_MN(code, self.psf['gamma_c'], self.psf['gamma_s'], Md, Nd, Md/self.psf['permanent'], Nd/self.psf['permanent'], D, B, H1, H2, sym, 1.5, 0.0 , self.fck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, self.fyk, self.fyk*1.05, Es, eps_su, RissP1, minBew, 18)   # compression side
        a_s_i =   StB_R_Q(code, self.psf['gamma_c'], self.psf['gamma_s'], Md, Nd, Qd, D, B, H1, H2, A_s1_i, A_s2_i, self.fck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, self.fyk, self.fyk*1.05, Es, eps_su, 0.0, 0.0, 0.0, 19)

        A_s1 = float(A_s1_i)
        A_s2 = -float(A_s2_i)
        a_s = max(float(a_s_i), 0.0)

        return A_s1, A_s2, a_s


    def calc_A_s(self, n, dia_string):
        """ Calculates A_s
        n: number of vertical bars
        dia_string: string for diameter of bars in mm. This can be 'xx' or 'Dxx'
        H: separation to edge in mm
        """
        try: # single bars
            dia = float(dia_string)   #'xx'
            A_s = (n*1/4*np.pi*dia**2) * 1e-2 # cm^2
            clearance = ((self.h*1000-2*self.co)/(n-1) - dia) * 1e-1  #cm
        except ValueError: # double bars
            dia = float(dia_string[1:])   #'Dxx'
            A_s = 2*(n*1/4*np.pi*dia**2) * 1e-2 # cm^2
            clearance = ((self.h*1000-2*self.co)/(n-1) - 2*dia) * 1e-1 #cm

        return (A_s, clearance)


    def calc_a_s(self, n_legs, dia_string, spacing):
        """ Calculates a_s
        n: number of vertical bars
        dia_string: string for diameter of bars in mm. This can be 'xx' or 'Dxx'
        """
        try: # single bars
            dia = float(dia_string)   #'xx'
            area = (1/4*np.pi*dia**2) * 1e-2 # cm^2
            a_s = area * n_legs * 100.0/spacing #cm^2/m
        except ValueError: # double bars
            dia = float(dia_string[1:])   #'Dxx'
            area = (1/4*np.pi*dia**2) * 1e-2 # cm^2
            a_s = area * n_legs * 100.0/spacing #cm^2/m

        return a_s


    def calc_weight_A_s(self, A_s, length):
        """ Calculates steel weight for a longitudinal segment
        As is in cm^2, length is in meter.
        """
        return abs(A_s * length *0.785) # Kg


    def calc_weight_a_s(self, a_s, length, n_legs):
        """ Calculates steel weight for a shear segment
        length: barrette length in meter
        """
        perimeter = (2*self.h*1000 + n_legs*(self.b*1000-2*self.co))*0.001 #m
        volume = perimeter*length
        weight = volume*a_s*0.785/n_legs
        return abs(weight)   # Kg