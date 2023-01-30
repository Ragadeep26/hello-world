# -*- coding: utf-8 -*-
"""
Created on Tue Dec 07 09:40:14 2022

@author: nya
"""
import json
import math
from collections import OrderedDict
from dimensioning.struts.cross_section import crossSection
#from cross_section import crossSection  # for debugging

alpha_buckling_curves = {'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}

class SteelProfile(crossSection):
    """ Tube class"""
    def __init__(self, fyk, psf, design_loads, h, b, tw, tf, r, A, Sy, Iyy, Izz, Itor, Iw, W_y, W_z, g, buckling_curve='a', nos=1, distance_beam2beam=100.0):
        super(SteelProfile, self).__init__(fyk, psf)
        #self.D = D                                  # diameter, mm
        #self.t = t                                  # thickness, mm
        self.h = h 
        self.b = b 
        self.tw = tw
        self.tf = tf
        self.r = r
        self.Sy = Sy                                        # area moment, cm^3
        self.Iyy_single = Iyy                                      # second moment of inertia, cm^4
        self.Izz_single = Izz                                      # second moment of inertia, cm^4
        self.W_el_y_single = W_y                                   # 
        self.W_el_z_single = W_z                                   # 
        #self.W_pl = 2*Sy                                   # 
        self.G = g*nos                                          # self weigth kg/m
        self.g = g*nos*0.01                                     # self weigth kN/m
        self.p = 1                                          # kN/N
        self.buckling_curve = buckling_curve                # a character indicating buckling curve
        self.nos= nos                                       # number of tube: 1 or 2
        self.distance_beam2beam = distance_beam2beam        # distance beam to beam in case more than 1 strut are used, mm
        # note that, normal axial force is positive in compression, whereas in cross section calculation negative sign denotes compression
        # a negation of normal force in (stress) calculation is used for this conversion
        self.design_loads = self.divide_design_loads(design_loads)                      # design loads are needed for the determination of cross-section class

        self.A = self.get_area_total(A)                                                 # total area, cm^2
        self.A_single = A                                                               # area for 1 profile only, used for the determination of cross-section, cm^2!!
        self.QK, self.QK_w, self.QK_f = self.get_cross_section_class(self.design_loads)

        self.Iyy, self.W_el_y, self.W_pl_y = self.get_Iyy_Wel_y_Wpl_y_total(Iyy, W_y)                    # second moment of inertia, cm^4
        self.Izz, self.W_el_z, self.W_pl_z = self.get_Izz_Wel_z_Wpl_z_total(Izz, W_z)                    # second moment of inertia, cm^4
        self.Itor = Itor*self.nos    # total I torsion, cm^4
        self.Iw = Iw*1000*self.nos    # total I torsion, cm^6

        self.N_pl_d = self.get_N_pl_d()
        self.M_pl_d_y, self.M_pl_d_z = self.get_Mpl_d()
        self.V_pl_d = self.get_V_pl_d()


    def get_area_total(self, A):
        """ Gets total cross section area
        """
        return self.nos*A


    def divide_design_loads(self, design_loads):
        """ Divides design loads by the number of profiles
        Used for the determination of cross-section, together with using cross-section area for a single profile
        """
        design_loads_new = {'Nd': 0.0, 'Myd': 0.0, 'Mzd': 0.0}
        for key, value in design_loads.items():
            design_loads_new[key] = value/self.nos

        return design_loads_new


    def get_Iyy_Wel_y_Wpl_y_total(self, I, W_el):
        """ Get total Iyy
        """
        Iyy = self.nos*I
        W_el_y = W_el
        if self.nos> 1:
            W_el_y = 2*Iyy/self.h * 10
        W_pl_y = 2*self.Sy*self.nos
        return Iyy, W_el_y, W_pl_y


    def get_Izz_Wel_z_Wpl_z_total(self, I, W_el):
        """ Get total Iyy
        """
        distance_center2center = (self.nos- 1)*self.b + (self.nos- 1)*self.distance_beam2beam
        Izz = self.nos*I + (distance_center2center/20)**2 * self.A
        W_el_z = W_el
        if self.nos> 1:
            distance_center2center = (self.nos- 1)*self.b + (self.nos- 1)*self.distance_beam2beam
            W_el_z = 2*Izz/distance_center2center * 10
        if self.nos > 1:
            W_pl_z = self.A/self.nos * distance_center2center/10    
        else:
            W_pl_z = 2*self.b*0.1/2*self.tf*0.1 * self.b*0.1/2  # cm^3

        return Izz, W_el_z, W_pl_z


    def get_N_pl_d(self):
        """ Gets plastic axial force resistance N_pl [kN]
        """
        if 'gamma_M0' not in self.psf:
            N_pl_d = self.fyk*self.A/1.0 * 1000/(100**2)  #  kN
        else:
            N_pl_d = self.fyk*self.A/self.psf['gamma_M0'] * 1000/(100**2)  #  kN
        return N_pl_d


    def get_Mpl_d(self):
        """ Gets plastic moment M_pl_y, M_pl_z [kNm]
        """
        if 'gamma_M0' not in self.psf:
            M_pl_d_y = self.fyk*self.W_pl_y/1.0 * 1000/(100**3) # kNm
            M_pl_d_z = self.fyk*self.W_pl_z/1.0 * 1000/(100**3) # kNm
        else:
            M_pl_d_y = self.fyk*self.W_pl_y/self.psf['gamma_M0'] * 1000/(100**3) # kNm
            M_pl_d_z = self.fyk*self.W_pl_z/self.psf['gamma_M0'] * 1000/(100**3) # kNm
        return M_pl_d_y, M_pl_d_z


    def get_V_pl_d(self):
        """ Gets plastic shear resistance [kN]
        """
        V_pl_d = self.nos*(self.A_single*100 - 2*self.b*self.tf + (self.tw + 2*self.r)*self.tf) * self.fyk/math.sqrt(3)/self.psf['gamma_M0']/1000
        return V_pl_d
    

    def get_cross_section_class(self, design_loads):
        """ Gets cross section class for cross-section
        """
        QK_w = self.get_cross_section_class_web(design_loads)
        QK_f = self.get_cross_section_class_flange(design_loads)
        return max(QK_w, QK_f), QK_w, QK_f


    def get_cross_section_class_web(self, design_loads):
        """ Gets cross section class for web
        """
        c_steg = self.h - 2*(self.tf + self.r)   # mm
        c = self.h/2 # lever arm
        # plastic null-line
        if 'gamma_M0' not in self.psf:
            alpha_web = 0.5 - (-design_loads['Nd']*1.0/(2*c_steg*0.1*self.tw*0.1*self.fyk*0.1))  # mm, negation of normal force because compression is positive with input data
        else:
            alpha_web = 0.5 - (-design_loads['Nd']*self.psf['gamma_M0']/(2*c_steg*0.1*self.tw*0.1*self.fyk*0.1))  # mm, negation of normal force because compression is positive with input data
        self.alpha_web = min(alpha_web, 1.0)    # alpha max is 1.0: the cross-section is fully plastified
        if self.design_loads['Myd'] > 0:    # at span
            self.sigma_1_web = -design_loads['Nd']/ (self.A_single) - design_loads['Myd']*100/(2*self.Iyy_single/(c*0.1))  # kN/cm^2, compression
            self.sigma_2_web = -design_loads['Nd']/ (self.A_single) + design_loads['Myd']*100/(2*self.Iyy_single/(c*0.1))  # kN/cm^2, tension
        else:   # at supports
            self.sigma_2_web = -design_loads['Nd']/ (self.A_single) - design_loads['Myd']*100/(2*self.Iyy_single/(c*0.1))  # kN/cm^2, tension
            self.sigma_1_web = -design_loads['Nd']/ (self.A_single) + design_loads['Myd']*100/(2*self.Iyy_single/(c*0.1))  # kN/cm^2, compression
        self.psi_web = self.sigma_2_web/self.sigma_1_web
        # web
        self.c_over_tw = c_steg/self.tw

        if (self.c_over_tw <= 396*self.epsilon/(13*self.alpha_web - 1)) and (self.alpha_web > 0.5):
            self.c_over_tw_zul = 396*self.epsilon/(13*self.alpha_web - 1)
            return 1
        elif (self.c_over_tw <= 36*self.epsilon/self.alpha_web) and (self.alpha_web <= 0.5):
            self.c_over_tw_zul = 36*self.epsilon/self.alpha_web
            return 1
        elif (self.c_over_tw <= 456*self.epsilon/(13*self.alpha_web - 1)) and (self.alpha_web > 0.5):
            self.c_over_tw_zul = 456*self.epsilon/(13*self.alpha_web - 1)
            return 2
        elif (self.c_over_tw <= 41.5*self.epsilon/self.alpha_web) and (self.alpha_web <= 0.5):
            self.c_over_tw_zul = 41.5*self.epsilon/self.alpha_web
            return 2
        else: # QK 3
            if (self.psi_web > -1) and (self.c_over_tw <= 42*self.epsilon/(0.67 + 0.33*self.psi_web)):
                self.c_over_tw_zul = 42*self.epsilon/(0.67 + 0.33*self.psi_web)
                return 3
            elif (self.psi_web <= -1) and (self.c_over_tw <= 62*self.epsilon*(1-self.psi_web)*math.sqrt(-self.psi_web)):
                self.c_over_tw_zul = 62*self.epsilon*(1-self.psi_web)*math.sqrt(-self.psi_web)
                return 3
            else: 
                self.c_over_tw_zul = 0
                return 4


    def get_cross_section_class_flange(self, design_loads):
        """ Gets cross section class for flange
        """
        c = self.b/2 - self.r - self.tw/2
        self.c_over_tf = c/self.tf  # c_over_tf is needed in further calculation steps
        lever_arm_compression = c/2
        lever_arm_tension = c/2

        if abs(self.design_loads['Mzd']) > 0.01 and self.nos == 1:  # the case Mzd != 0 and nos == 1
            # compute alpha value for the determination of QK 1/2
            alpha_LO, flanschrand_im_druck_LO, alpha_RO, flanschrand_im_druck_RO, alpha_LU, flanschrand_im_druck_LU, alpha_RU, flanschrand_im_druck_RU = self.alpha_Wert_flansch_infolge_Mz()

            # compute stress in the upper and lower flanges of the I profile for the determination of QK3
            sigmaLO, sigmaRO, sigmaMO, sigmaLU, sigmaRU, sigmaMU = self.spannungLRM_im_I_Flansch_NMyMz()

            # get the psi and k_sigma for Flansh Oben (Left + Right)
            psi_LO, psi_RO, k_sigmaLO, k_sigmaRO = self.get_psi_k_sigma_Links_Rechts(sigmaLO, sigmaRO, sigmaMO)
            # get the psi and k_sigma for Flansh Unten (Left + Right)
            psi_LU, psi_RU, k_sigmaLU, k_sigmaRU = self.get_psi_k_sigma_Links_Rechts(sigmaLU, sigmaRU, sigmaMU)

            # determine the QK0/1/2/3/4 for four Flanch ends LO, LU, RO, and RU, one after another
            QK_f_LO, c_over_tf_LO_zul = self.einseitig_gestuetzte_QS_universal(alpha_LO, k_sigmaLO, flanschrand_im_druck_LO)
            QK_f_RO, c_over_tf_RO_zul = self.einseitig_gestuetzte_QS_universal(alpha_RO, k_sigmaRO, flanschrand_im_druck_RO)
            QK_f_LU, c_over_tf_LU_zul = self.einseitig_gestuetzte_QS_universal(alpha_LU, k_sigmaLU, flanschrand_im_druck_LU)
            QK_f_RU, c_over_tf_RU_zul = self.einseitig_gestuetzte_QS_universal(alpha_RU, k_sigmaRU, flanschrand_im_druck_RU)

            # get cross-section class and allowable c/t ratio
            QK_f_all = [QK_f_LO, QK_f_RO, QK_f_LU, QK_f_RU]
            c_over_tf_zul_all = [c_over_tf_LO_zul, c_over_tf_RO_zul, c_over_tf_LU_zul, c_over_tf_RU_zul]
            QK_f = max(QK_f_all)
            QK_f_indices = [i for i, qk in enumerate(QK_f_all) if qk == QK_f]
            self.c_over_tf_zul = max(c_over_tf_zul_all[i] for i in QK_f_indices)    # store for display
            
            # store additional intermediate values for display
            self.alpha_f_all = [round(alpha_LO, 1), round(alpha_RO, 1), round(alpha_LU, 1), round(alpha_RU, 1)]
            self.psi_f_all = [round(psi_LO, 1), round(psi_RO, 1), round(psi_LU, 1), round(psi_RU, 1)]
            self.sigma_f_all = [round(sigmaLO, 1), round(sigmaRO, 1), round(sigmaLU, 1), round(sigmaRU, 1)]
            self.k_sigma_f_all = [round(k_sigmaLO, 1), round(k_sigmaRO, 1), round(k_sigmaLU, 1), round(k_sigmaRU, 1)]

            return QK_f

        else:
            self.sigma_1_flange = -design_loads['Nd']/ (self.A_single) - design_loads['Myd']*100/(self.Iyy_single/(lever_arm_compression*0.1))  # kN/cm^2, compression
            self.sigma_2_flange = -design_loads['Nd']/ (self.A_single) + design_loads['Myd']*100/(self.Iyy_single/(lever_arm_tension*0.1))  # kN/cm^2, tension
            if (self.sigma_1_flange > 0) and (self.sigma_2_flange > 0): # the whole cross-section is subject to tension stress
                self.c_over_tf_zul = 0.0
                return 0
            else:
                # one-side supported elements for structural elements subject only to compression (Table 5.2 DIN EN 1993-1-1)
                #self.psi_flange = self.sigma_2_flange/self.sigma_1_flange
                if self.c_over_tf <= 9*self.epsilon:
                    self.c_over_tf_zul = 9*self.epsilon
                    return 1
                elif self.c_over_tf <= 10*self.epsilon:
                    self.c_over_tf_zul = 10*self.epsilon
                    return 2
                elif self.c_over_tf <= 14*self.epsilon:
                    self.c_over_tf_zul = 14*self.epsilon
                    return 3
                else:
                    self.c_over_tf_zul = 14*self.epsilon
                    return 4


    def alpha_Wert_flansch_infolge_Mz(self):
        """ Abc
        """
        c = self.b/2
        # width of flange that takes Mz at 4 flange free ends
        c_temp = (self.b*0.1)**2 - 4*self.design_loads['Mzd']*100/ (2*self.tf*0.1*(self.fyk*0.1))    # fyk*0.1 [kN/cm^2]
        if c_temp < 0.0: # Mz is so large that the whole flange will be used for taking Mz
            c_temp = 0.0
        
        b_p = 0.5*(self.b*0.1 - math.sqrt(c_temp)) * 10 # mm

        # QK 1/ 2, Mz > 0
        if self.design_loads['Mzd'] > 0.0:  
            # Oben/ Erdseite
            alpha_LO = 1 # Flanschende nur auf Druck
            flanschrand_im_druck_LO = True

            alpha_RO = (c - b_p)/c  # Flanschende im Zugbereich (Tabelle 5.2, DIN EN 1993-1-1)
            if abs(alpha_RO) < 1.0e-10: # When Mz is very large, the whole area is under tension, b_p = c, therefore alpha = 0
                alpha_RO = -1   # Flanschende nur auf Zug, und lasse alpha < 0 here.  When alpha < 0, set QK = 0
            flanschrand_im_druck_RO = False

            # Unten/ Luftseite
            alpha_LU = b_p/c # Flanschende im Druckbereich (Tablle 5.2, DIN EN 1993-1-1)
            flanschrand_im_druck_LU = True

            alpha_RU = -1 # Flanschende nur auf Zug, und lasse alpha < 0 here.  When alpha < 0, set QK = 0.
            flanschrand_im_druck_RU = False

        elif self.design_loads['Mzd'] < 0.0:   
            # Oben/ Erdseite
            alpha_LO = (c - b_p)/c  # Flanschende im Zugbereich (Tabelle 5.2, DIN EN 1993-1-1)
            if abs(alpha_LO) < 1.0e-10: # When Mz is very large, the whole area is under tension, b_p = c, therefore alpha = 0
                alpha_LO = -1   # in tension only
            flanschrand_im_druck_LO = False

            alpha_RO = 1 # Flanschende nur auf Druck
            flanschrand_im_druck_RO = True

            # Unten/ Luftseite
            alpha_LU = -1 # Flanschende nur auf Zug, und lasse aphla < 0 here.  When alpha < 0, set QK = 0
            flanschrand_im_druck_LU = False

            alpha_RU = b_p/c # Flanschende im Druckbereich (Tablle 5.2, DIN EN 1993-1-1)
            flanschrand_im_druck_RU = True


        if self.design_loads['Myd'] < 0:    #Wenn My negative ist, unten und oben müssen gewechselt werden
            alpha_LO_temp = alpha_LO
            alpha_LU_temp = alpha_LU
            alpha_RO_temp = alpha_RO
            alpha_RU_temp = alpha_RU

            alpha_LU = alpha_LO_temp
            alpha_LO = alpha_LU_temp
            alpha_RU = alpha_RO_temp
            alpha_RO = alpha_RU_temp

        return alpha_LO, flanschrand_im_druck_LO, alpha_RO, flanschrand_im_druck_RO, alpha_LU, flanschrand_im_druck_LU, alpha_RU, flanschrand_im_druck_RU

    
    def spannungLRM_im_I_Flansch_NMyMz(self):
        """ Hier wird die Spannung im Flansch gerechnet, sodass die Information
        weiter für die Berechung der SPannungsverhältness psi im Flansch für QK3 weitergeben kann.
        Hier wird N, My, und Mz mit gerücksichtigt. Die Spannung im oberen und unteren Flansch, am 4 Freie Rände und in der mittle
        des flansches werden gebrechnet.

        N negativ = Druck
        My positiv = oben/Erdseite Druck, unten/Luftseite Zug
        Mz positiv = Links Druck, rechts Zug

        N =  normal draft kN (bemessungswert)
        My =  bemessungswert  kNcm: My+ imposes comp. in the earth-side Flansh
        Mz =  bemessungswert  kNcm: Mz+ imposes comp. in the Left-side Flansh (positive z points downwards)
        A =  cm2 , Cross-section area
        h =  cm , Träger Höhe
        b =  cm , Träger (Flansch) Breite

        Iy, Iz =  cm ^ 4,  Trägkeitsmoment

        Dim sigmaOL  As Double '= Oben links (Flansch freier rand)  ' kN/cm2
        Dim sigmaOR  As Double '= oben rechts (Flansch freier rand) ' kN/cm2
        Dim sigmaOM  As Double '= oben mitte (Flansch mitte)  ' kN/cm2

        Dim sigmaUL  As Double '= unten links (Flansch freier rand)  ' kN/cm2
        Dim sigmaUR  As Double '= unten rechts (Flansch freier rand) ' kN/cm2
        Dim sigmaUM  As Double '= unten mitte (Flansch mitte) ' kN/cm2
        """

        # note, negation of compression force 
        sigmaOL = -self.design_loads['Nd'] / self.A_single - self.design_loads['Myd']*100 * (self.h*0.1 / 2) / self.Iyy_single - self.design_loads['Mzd']*100 * (self.b*0.1 / 2) / self.Izz_single # kN/cm^2
        sigmaOR = -self.design_loads['Nd'] / self.A_single - self.design_loads['Myd']*100 * (self.h*0.1 / 2) / self.Iyy_single + self.design_loads['Mzd']*100 * (self.b*0.1 / 2) / self.Izz_single # kN/cm^2
        sigmaOM = (sigmaOL + sigmaOR) / 2   # kN/cm^2

        # note, negation of compression force 
        sigmaUL = -self.design_loads['Nd'] / self.A_single + self.design_loads['Myd']*100 * (self.h*0.1 / 2) / self.Iyy_single - self.design_loads['Mzd']*100 * (self.b*0.1 / 2) / self.Izz_single # kN/cm^2
        sigmaUR = -self.design_loads['Nd'] / self.A_single + self.design_loads['Myd']*100 * (self.h*0.1 / 2) / self.Iyy_single + self.design_loads['Mzd']*100 * (self.b*0.1 / 2) / self.Izz_single # kN/cm^2
        sigmaUM = (sigmaUL + sigmaUR) / 2   # kN/cm^2

        return (sigmaOL, sigmaOR, sigmaOM, sigmaUL, sigmaUR, sigmaUM)


    def get_psi_k_sigma_Links_Rechts(self, sigmaL, sigmaR, sigmaM):
        """ Hier wird spannungsverhältniss psi gerechnet.
        Gegeben sind die 3 spannungen im oberen Flansch oder in unteren Flansch, jenach dem
        was eingegeben sind. Die 3 Spannung sind die Spannungen an 3 Punkten des Flansches einer I-Profil:
          1) sigmaL  : links (Flansch freier rand)  (Freies links Ende Spannung sf)   '  kN/cm2
          2) sigmaR  : rechts (Flansch freier rand) (Freies rechts Ende Spannung sf)  '  kN/cm2
          3) sigmaM  : mitte (Flansch mitte)  (Stützen Spannung ss)  '  kN/cm2
        k_simga wird in Tabelle 5.2, DIN EN 1993-1-1 für die abstimmung der QK 3 oder 4 weiter verwendet.
        """
        psi_L, k_sigmaL = self.get_psi_k_sigma_aus_spanungsverteilung(sigmaM, sigmaL)
        psi_R, k_sigmaR = self.get_psi_k_sigma_aus_spanungsverteilung(sigmaM, sigmaR)
        return psi_L, psi_R, k_sigmaL, k_sigmaR



    def get_psi_k_sigma_aus_spanungsverteilung(self, ss, sf):
        """ This sub only considers the one-side supported cross-section (einseitig gestützte Querschnitt).
        Using sigmaL, sigmaR, sigmaM, the psi and k_sigma will be computed according to EC 1993-1-5 or
         "Tabelle 13.4 Wirksame Breiten für einseitig gestützte Teile" in Prof Kindmann's book.

        In this subroutine, the psi and k_sigma of one of the 4 flanch-ends will be determined.
        Thus, the first step is to retrieve the stress and the freed end and the fixed end of a flanch end,
        given the stress distribution sigmaL, sigmaR, sigmaM. The three stress values must be assigned to ss
        or sf correctly: 
        ss = stress at support (middle of flanch, stütz punkt) 
        sf = stress at free end (two ends of flansh)  
        psi = sigma2 / sigma1 (gem. 1993-1-5)

        k_simga wird spater (in einem anderen Sub) für  Tabelle 5.2, DIN EN 1993-1-1 für die
         abstimmung der QK 3 oder 4 weiter verwendet.               
        Note:
          k_sigma = 0# 'this will lead to QK4.
          k_sigma <0 (=-1 here),  QK will be set to be 0, meaning the cross-section is only subject to tensile stress
        """
        if (ss <= 0 and sf <= 0 and abs(sf) >= abs(ss)) or (ss >= 0 and sf <= 0):
            sigma2 = ss
            sigma1 = sf
            psi = sigma2/sigma1
            if psi <=1 and psi >= -1:
                k_sigma = 0.57 - 0.21*psi + 0.07*psi**2
            else:
                k_sigma = 0.0   # this leads to QK 4

        elif (ss <= 0 and sf <= 0 and abs(sf) < abs(ss)) or (ss <= 0 and sf >= 0):
            sigma1 = ss
            sigma2 = sf
            psi = sigma2/sigma1
            if psi <=1 and psi >= -1:
                k_sigma = 1.7 - 5.0*psi + 17.1*psi**2
            else:
                k_sigma = 0.0   # this leads to QK 4

        elif (ss >= 0.0) and (sf >= 0.0):   # the whole cross-section is subject to tension
            #psi = 0.0
            k_sigma = -1 # k_sigma = -1: QK will be set to 0
        
        if ss > 0 and sf > 0:
            psi = 0.0
            k_sigma = -1
        
        return psi, k_sigma


    def einseitig_gestuetzte_QS_universal(self, alpha, k_sigma, flanschrand_im_druck):
        """
        This sub computes the QK for one-side supported elements (See. Table 5.2, DIN EN 1993-1-1)

        Table 5.2 in DIN EN 1993-1-1: einseitig gestützte Flansche:
        Spalte (1) nur auf druck
        Spalte (2) freierrand im Druckbereich: Flanschrand_im_Druck = true
        Spalte (3) freierrand im Zugbereich: Flanschrand_im_Druck = false

        Für QK 1 and 2. wenn alpha = 1. spalte (1) is included in Spalte 2 und 3.
        Für QK 3, wenn spannung gleich verteilt --> psi = 1 und spannung < 0, und ksigma = 0,43 --> Spalte (1) ist auch inclusive

        alpha = -1 --> Nur auf zug
        k_sigma = -1 --> nur auf zug
        k_sigma = 0 --> psi auf of applicable boundary for computing k_sigma. k_sigma 0 will directly lead to QK 4.
        """
        if alpha < 0.0: # a negative value of alpha indicates only tension in the cross-section.
            QK = 0
            c_over_tf_zul = 0  # 0 or a large number???
        else:
            if flanschrand_im_druck:
                alpha_temp = self.epsilon/alpha
            else:
                alpha_temp = self.epsilon*alpha/math.sqrt(alpha)

            if self.c_over_tf <= 9*alpha_temp:
                c_over_tf_zul =9*alpha_temp 
                QK = 1
            elif self.c_over_tf <= 10*alpha_temp:
                c_over_tf_zul = 10*alpha_temp
                QK = 2
            else: # QK 3/4
                if k_sigma < 0:
                    QK = 0  # cross-section is in only tension
                elif self.c_over_tf <= 21*self.epsilon*math.sqrt(k_sigma):
                    c_over_tf_zul = 21*self.epsilon*math.sqrt(k_sigma) 
                    QK = 3
                else: # QK 4
                    c_over_tf_zul = 21*self.epsilon*math.sqrt(k_sigma) 
                    QK = 4
        
        return QK, c_over_tf_zul


    def perform_design_checks_lateral_torsional_buckling(self, design_loads, sy, sz):
        """ Performs design checks for lateral torsional buckling
        Formel: Schneider Seite 8.34"""
        # constants after Kindmann
        self.c_LT = 1.0 # Momentbeiwert
        xi = 1.12
        kc = 0.95
        self.c2 = (self.Iw +0.039*(sz*100)**2*self.Itor)/self.Izz   # square of torsional radius, cm^2
        if self.QK < 3: # QK 1/2: plastic resistance
            Wy = self.W_pl_y
            Wz = self.W_pl_z
        else:   # QK 3: elastic resistance
            Wy = self.W_el_y
            Wz = self.W_el_z

        # get N_cr
        self.get_N_cr(sy, sz)

        zp_y = -self.h/20 # Lastanriffspunkt, cm
        self.M_cr = xi * self.N_cr_zz * (math.sqrt(self.c2 + 0.45*zp_y**2) + 0.5*zp_y)/100    # kNm

        self.lambda_LT = math.sqrt(Wy*1.0e-6*self.fyk*1.0e3/self.M_cr)     # sqrt(W*fyk/Mcr)

        h_over_h = self.h/self.b
        buckling_curve = 'b'
        if h_over_h > 2:
            buckling_curve = 'c'

        alpha_LT_y = alpha_buckling_curves[buckling_curve]    # imperfection factor alpha for buckling curve
        alpha_LT_z = alpha_buckling_curves[buckling_curve]    # imperfection factor alpha for buckling curve

        # phi
        phi_LT_y = 0.5*(1 + alpha_LT_y*(self.lambda_LT - 0.4) + 0.75*self.lambda_LT**2)
        phi_LT_z = 0.5*(1 + alpha_LT_z*(self.lambda_LT - 0.4) + 0.75*self.lambda_LT**2)

        # chi (or kappa)
        self.get_reduction_factor_chi_buckling()    # get self.chi_yy, self.chi_zz, self.lambda_bar_zz
        chi_LT_1_y = 1.0/(phi_LT_y + math.sqrt(phi_LT_y**2 - 0.75*self.lambda_LT**2))
        chi_LT_1_z = 1.0/(phi_LT_z + math.sqrt(phi_LT_z**2 - 0.75*self.lambda_LT**2))
        factor_chi_LT_y = min(1.0, 1.0 - 0.5*(1.0 - kc)*(1.0 - 2*(self.lambda_bar_yy - 0.8)**2))
        chi_LT_y = min(chi_LT_1_y, 1.0, 1/(self.lambda_LT**2)) * factor_chi_LT_y
        self.chi_LT_z = min(chi_LT_1_z, 1.0, 1/(self.lambda_LT**2))

        # Momentbeiwert kyz, QK-abhangig
        n_y = math.fabs(design_loads['Nd']/(self.chi_yy*(self.N_pl_d*self.psf['gamma_M0']/self.psf['gamma_M1'])))  # total design loads (no multiplication with nos)
        n_z = math.fabs(design_loads['Nd']/(self.chi_zz*(self.N_pl_d*self.psf['gamma_M0']/self.psf['gamma_M1'])))  # total design loads (no multiplication with nos)
        if self.QK < 3:
            kzz_1 = self.c_LT*(1 + (self.lambda_LT - 0.2)*n_z)
            kzz_2 = self.c_LT*(1 + 0.8*n_z)
            kzz = min(kzz_1, kzz_2)*0.6
            kyy_1 = self.c_LT*(1 + (self.lambda_LT - 0.2)*n_y)
            kyy_2 = self.c_LT*(1 + 0.8*n_y)
            #kyy = min(kyy_1, kyy_2)
        else: # QK3
            kzz_1 = self.c_LT*(1 + 0.6*self.lambda_LT*n_z)
            kzz_2 = self.c_LT*(1 + 0.6*n_z)
            kzz = min(kzz_1, kzz_2)
            kyy_1 = self.c_LT*(1 + 0.6*self.lambda_LT*n_y)
            kyy_2 = self.c_LT*(1 + 0.6*n_y)
            #kyy = min(kyy_1, kyy_2)
        self.kzz = min(kzz_1, kzz_2)
        self.kyy = min(kyy_1, kyy_2)
        self.kyz = kzz

        # Momentbeiwert kzy, QK-abhangig
        if self.QK < 3:
            if self.lambda_bar_zz != 0.4:
                kzy_1 = 1 - 0.1*self.lambda_bar_zz/(self.c_LT - 0.25)*n_z
                kzy_2= 1 - 0.1/(self.c_LT - 0.25)*n_z
                kzy = max(kzy_1, kzy_2)
            else:
                kzy_1 = 0.6*self.lambda_bar_zz
                kzy_2 = 1 - 0.1*self.lambda_bar_zz/(self.c_LT - 0.25)*n_z
                kzy = min(kzy_1, kzy_2)
        else: # QK3
            kzy_1 = 1 - 0.05*self.lambda_bar_zz/(self.c_LT - 0.25)*n_z
            kzy_2 = 1 - 0.05/(self.c_LT - 0.25)*n_z
            kzy = max(kzy_1, kzy_2)
        self.kzy = kzy

        # design checks
        M_y_Rk = self.fyk*Wy* 1000/(100**3)    # Wy depends on QK, kNm
        M_z_Rk = self.fyk*Wz* 1000/(100**3)    # Wy depends on QK, kNm
        
        util_N_1 = design_loads['Nd'] / (self.chi_yy * self.N_pl_d/self.psf['gamma_M1'])
        util_N_2 = design_loads['Nd'] / (self.chi_zz * self.N_pl_d/self.psf['gamma_M1'])
        util_M_d_y_1 = abs(design_loads['Myd']) * self.kyy / (chi_LT_y*M_y_Rk/self.psf['gamma_M1'])
        util_M_d_y_2 = abs(design_loads['Myd']) * self.kzy / (chi_LT_y*M_y_Rk/self.psf['gamma_M1'])
        util_M_d_z_1 = design_loads['Mzd'] * self.kyz / (M_z_Rk/self.psf['gamma_M1'])
        util_M_d_z_2 = design_loads['Mzd'] * self.kzz / (M_z_Rk/self.psf['gamma_M1'])

        if (util_N_1 + util_M_d_y_1 + util_M_d_z_1) > (util_N_2 + util_M_d_y_2 + util_M_d_z_2):
            self.util_N_d = util_N_1
            self.util_M_d_y = util_M_d_y_1
            self.util_M_d_z = util_M_d_z_1
        else:
            self.util_N_d = util_N_2
            self.util_M_d_y = util_M_d_y_2
            self.util_M_d_z = util_M_d_z_2

        self.util_total = self.util_N_d + self.util_M_d_y + self.util_M_d_z


    def perform_interaction_stress_verification_QK1_QK2(self, design_loads):
        """ Performs stress verfification for QK 1 or QK 2
        Calculation steps are from Schneider book 8.18
        """
        Vz_Ed = design_loads['Vd']
        N_Ed = design_loads['Nd']
        My_Ed = design_loads['Myd']

        Vz_pl_Rd = self.V_pl_d
        N_pl_Rd = self.N_pl_d
        My_pl_Rd = self.M_pl_d_y

        if Vz_Ed <= 0.5*Vz_pl_Rd:
            if N_Ed > min(0.25*N_pl_Rd, 0.5*self.h*self.tw*self.fyk/self.psf['gamma_M0']/1000):
                n = N_Ed/N_pl_Rd
                a_star = min(0.5, (self.A_single - 2*self.b*0.1*self.tf*0.1)/self.A_single)
            else:
                n = 0.0
                a_star = 0.0

            My_N_Rd = min(My_pl_Rd, My_pl_Rd*(1.0 - n)/(1.0 - 0.5*a_star))
            util = abs(My_Ed/My_N_Rd)

        else:
            rho = (2*Vz_Ed/Vz_pl_Rd - 1.0)**2
            Av1 = self.A_single - 2*self.b*self.tf/100 + (self.tw + 2*self.r)*self.tf/100   # cm^2
            Av2 = (self.h - 2*self.tf)*self.tw/100  # cm^2
            Av = max(Av1, Av2)*self.nos # cm^2
            My_V_Rd = (self.W_pl_y - rho*Av**2/(4*self.tw*0.1))*1.0e-6 * self.fyk*1.0e3/self.psf['gamma_M0']    # kNm
            aV = Av/self.A
            N_V_Rd = N_pl_Rd*(1.0 - aV*rho)

            if N_Ed > min(0.25*N_V_Rd, self.h*self.tw*self.fyk*1.0e-3*(1-rho)/2/self.psf['gamma_M0']):
                n_v = N_Ed/N_V_Rd
                A_red = self.A*(1.0 - rho*self.psf['gamma_M0'])
                a_star = min((A_red/self.nos - 2*self.b*self.tf/100)/(A_red/self.nos), 0.5)
            else:
                n_v = 0.0
                a_star = 0.0

            My_NV_Rd = min(My_V_Rd, My_V_Rd*(1 - n_v)/(1.0 - 0.5*a_star))
            util = abs(My_Ed/My_NV_Rd)
        
        return util


    
    def perform_interaction_stress_verification_QK3(self, design_loads):
        """ Performs stress verfification for QK 3
        Design loads are total loads, they will be devided inside the verification
        Cross-section parameters are for a single beam
        """
        Vz_Ed = design_loads['Vd']
        N_Ed = design_loads['Nd']
        My_Ed = design_loads['Myd']

        Vz_pl_Rd = self.V_pl_d
        #N_pl_Rd = self.N_pl_d
        #My_pl_Rd = self.M_pl_d_y
        #z_max = (self.h - self.Iyy_single/self.W_el_y_single)/10  # cm
        #z_min = self.Iyy_single/self.W_el_y_single/10             # cm
        e = self.h/20   # cm
        sigma_ruecken = 1/self.nos*(-N_Ed/self.A_single - My_Ed*100/self.Iyy_single*e)  # earth side, kN/cm^2
        sigma_schloss = 1/self.nos*(-N_Ed/self.A_single + My_Ed*100/self.Iyy_single*e)  # air side, kN/cm^2
        psi = sigma_ruecken/sigma_schloss if My_Ed >= 0 else sigma_schloss/sigma_ruecken

        sigma_normal = max(abs(sigma_ruecken), abs(sigma_schloss))
        Av1 = self.A_single - 2*self.b*self.tf/100 + (self.tw + 2*self.r)*self.tf/100   # cm^2
        Av2 = (self.h - 2*self.tf)*self.tw/100  # cm^2
        Av = max(Av1, Av2)*self.nos # cm^2
        sigma_shear = Vz_Ed/Av
        sigma_von_Mises = math.sqrt(sigma_normal**2 + 3*sigma_shear**2)

        if Vz_Ed <= 0.5*Vz_pl_Rd:
            util = sigma_normal/(self.fyk/10)/self.psf['gamma_M0']
        else:
            util = sigma_von_Mises/(self.fyk/10)
        
        return util


if __name__ == '__main__':
    #json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', profile_id + '.json')
    json_item = r"D:\Data\3Packages\Moniman\solver\plaxis2d\profile_steels\jsons\HEB300.JSON"
    with open(json_item, "r") as read_file:
        params = json.load(read_file, object_pairs_hook = OrderedDict)
    # instantiate cross section
    psf_p = {'permanent': 1.35, 'transient': 1.5, 'gamma_c': 1.5, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
    psf_t = {'permanent': 1.2, 'transient': 1.3, 'gamma_c': 1.5, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
    psf_a = {'permanent': 1.1, 'transient': 1.1, 'gamma_c': 1.3, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
    psf_e = {'permanent': 1.0, 'transient': 1.0, 'gamma_c': 1.3, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
    PSFs = {'BS-P: Persistent': psf_p, 'BS-T: Transient': psf_t, 'BS-A: Accidential': psf_a, 'BS-E: Seismic': psf_e}
    design_loads = {'Nd': 3156.0, 'Myd': 691.0, 'Mzd': -782}
    nos = 2
    cross_section = SteelProfile(355.0, PSFs['BS-P: Persistent'], design_loads, float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                        float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                        float(params['g']), buckling_curve=params['Knick'], nos=nos)
    
    print('t_w = ', float(params['t-s']))
    print('t_f = ', float(params['t-g']))
    print('r = ', float(params['r']))
    items_to_list = ['QK', 'epsilon', 'alpha_web', 'c_over_tw', 'c_over_tw_zul', 'QK_w', 'sigma_1_web', 'sigma_2_web', 'psi_web',
                    'c_over_tf', 'c_over_tf_zul', 'QK_f']
    items_to_list_additinal = ['alpha_f_all', 'psi_f_all', 'sigma_f_all', 'k_sigma_f_all']

    # Teilfläche-Verfahren works only for single profile and is considered only when abs(Mz) > 0
    if abs(design_loads['Mzd']) > 0.01 and nos == 1:
        items_to_list += items_to_list_additinal

    for i, item in enumerate(items_to_list):
        print(items_to_list[i] + '=' , getattr(cross_section, item))
    

    # lateral torsional buckling
    print('\nlateral torsional buckling')
    cross_section.perform_design_checks_lateral_torsional_buckling(32, 32)
    items_to_list = ['util_N_d', 'util_M_d_y', 'util_M_d_z', 'util_total']
    for i, item in enumerate(items_to_list):
        print(items_to_list[i] + '=' , getattr(cross_section, item))