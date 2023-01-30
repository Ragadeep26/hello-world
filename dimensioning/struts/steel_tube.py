# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 16:34:14 2022

@author: nya
"""

from dimensioning.struts.cross_section import crossSection

class SteelTube(crossSection):
    """ Tube class"""
    def __init__(self, fyk, psf, D, t, A, Sy, I, W_el, G, buckling_curve='a', nos=1, distance_beam2beam=100.0):
        super(SteelTube, self).__init__(fyk, psf)
        self.D = D                                          # diameter, mm
        self.t = t                                          # thickness, mm
        self.Sy = Sy                                        # area moment, cm^3
        #self.W_el = W_el                                   # 
        #self.W_pl = 2*Sy                                   # 
        self.G = G                                          # self weigth kg/m
        self.g = self.G*0.01                                # tube self-weight, kN/m
        self.p = 1.0                                        # kN/N
        self.buckling_curve = buckling_curve                # a character indicating buckling curve
        self.nos= nos                                       # number of tube: 1 or 2
        self.distance_beam2beam = distance_beam2beam        # distance beam to beam in case more than 1 strut are used, mm

        # calculated cross section parameters
        self.A = self.get_area_total(A)                     # area, cm^2
        self.QK = self.get_cross_section_class()
        self.Iyy, self.W_el_y, self.W_pl_y = self.get_Iyy_Wel_y_Wpl_y_total(I, W_el)                    # second moment of inertia, cm^4
        self.Izz, self.W_el_z, self.W_pl_z = self.get_Izz_Wel_z_Wpl_z_total(I, W_el)                    # second moment of inertia, cm^4
        self.N_pl_d = self.get_N_pl_d()
        self.M_pl_d_y, self.M_pl_d_z = self.get_Mpl_d()


    def get_cross_section_class(self):
        """ Gets cross section class
        """
        self.d_over_t = self.D / self.t
        if self.d_over_t <= 50 * self.epsilon**2:
            self.d_over_t_zul = 50 * self.epsilon**2
            return 1
        elif self.d_over_t <= 70 * self.epsilon**2:
            self.d_over_t_zul = 70 * self.epsilon**2
            return 2
        elif self.d_over_t <= 90 * self.epsilon**2:
            self.d_over_t_zul = 90 * self.epsilon**2
            return 3
        else:
            self.d_over_t_zul = 90 * self.epsilon**2
            return 4
    

    def get_area_total(self, A):
        """ Gets total cross section area
        """
        return self.nos*A


    def get_Iyy_Wel_y_Wpl_y_total(self, I, W_el):
        """ Get total Iyy
        """
        Iyy = self.nos*I
        W_el_y = W_el
        if self.nos> 1:
            W_el_y = 2*Iyy/self.D * 10
        W_pl_y = 2*self.Sy*self.nos
        return Iyy, W_el_y, W_pl_y


    def get_Izz_Wel_z_Wpl_z_total(self, I, W_el):
        """ Get total Iyy
        """
        distance_center2center = (self.nos- 1)*self.D + (self.nos- 1)*self.distance_beam2beam
        Izz = self.nos*I + (distance_center2center/20)**2 * self.A
        W_el_z = W_el
        if self.nos> 1:
            distance_center2center = (self.nos- 1)*self.D + (self.nos- 1)*self.distance_beam2beam
            W_el_z = 2*Izz/distance_center2center * 10
        if self.nos > 1:
            W_pl_z = self.A/self.nos * distance_center2center/10
        else:
            W_pl_z = 2*self.Sy*self.nos

        return Izz, W_el_z, W_pl_z


    def get_N_pl_d(self):
        """ Gets design N_pl [kN]
        """
        N_pl_d = self.fyk*self.A/self.psf['gamma_M0'] * 1000/(100**2)  #  kN
        return N_pl_d


    def get_Mpl_d(self):
        """ Gets design M_pl_y, M_pl_z [kN]
        """
        M_pl_d_y = self.fyk*self.W_pl_y/self.psf['gamma_M0'] * 1000/(100**3) # kNm
        M_pl_d_z = self.fyk*self.W_pl_z/self.psf['gamma_M0'] * 1000/(100**3) # kNm
        return M_pl_d_y, M_pl_d_z