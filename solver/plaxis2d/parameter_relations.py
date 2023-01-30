# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 14:49:31 2019

@author: nya
"""
import sys
import os
import numpy as np
from scipy import interpolate
import pandas as pd


def get_interp_Edyn_over_Esta(Es, interp_function):
    """ Gets Ed/Es by interpolating the Edyn/Esta - Esta curve
    """
    #Edyn_over_Esta_interp = interpolate.interp1d(Esta_points, Edyn_over_Esta_points)
    Edyn_over_Esta = interp_function(Es)
    return Edyn_over_Esta

def get_interp_function_Edyn_over_Esta_Esta():
    """ Gets Ed/Es by interpolating the Edyn/Esta - Esta curve
    """
    MONIMAN = sys.modules['moniman_paths']['MONIMAN']
    cwd = os.path.join(MONIMAN, 'plaxis2d')
    df = pd.read_excel(open(os.path.join(cwd,'Edyn_over_Esta_Esta_data_points.xlsx'),'rb'), sheetname='soilpoints')
    Esta_points = df['Es (kN/m2)']
    Edyn_over_Esta_points = df['Ed/Es']
    interp_function = interpolate.interp1d(Esta_points, Edyn_over_Esta_points)

    return interp_function


def get_HS_moduli(ve, w, Pref, Eref50Oed, ErefUr50):
    """ Gets HS/ HSsmall moduli (EoedRef, E50ref, EurRef) 
    from ve, w, Pref, Eref50Oed, ErefUr50
    """
    Pat = 100 # Atmospheric pressure 100 KN/m^2
    
    EoedRef = ve*Pat*(Pref/Pat)**w # EoefRef is a derived parameter
    
    E50ref = EoedRef*Eref50Oed
    EurRef = E50ref*ErefUr50
    
    return EoedRef, E50ref, EurRef


def get_HSsmall_G0ref(EurRef, E_dyn_over_sta):
    """ Gets HSsmall small-strain reference shear modulus G0ref
    """
    G0ref = EurRef*E_dyn_over_sta/2.4
    
    return G0ref

def get_HS_K0nc(phi):
    """ Gets K0nc for HS/ HSmall model in relation with friction angle phi
    """
    K0nc = 1.0 - np.sin(phi*np.pi/180)
    
    return K0nc


def get_HS_K0nc_empirical(phi):
    """ Gets K0nc for HS/ HSmall model in relation with friction angle phi
    This functions is valid only if phi > 42.7 degree. The purpose is to avoid conflicts in PLAXIS2D with HS model with phi is large.
    """
    phi_out = phi
    if phi > 42.6:
        K0nc = 8.0e-5*phi**2 - 0.0129*phi + 0.7343

    elif phi >= 5.61: # normal case
        K0nc = 1.0 - np.sin(phi*np.pi/180)
    
    else: # phi cannot be larger than 5.56 degree
        K0nc = 1.0 - np.sin(5.61*np.pi/180)
        phi_out = 5.61
    
    return K0nc, phi_out


def get_psi(phi):
    """ gets psi based on the value of phi
    """
    if phi < 30:
        psi = 0.0
    else:
        psi = phi - 30
    
    return psi


def get_soil_parameters_based_on_correlations_with_ve(ve):
    """ Gets soil parameters phi, we, gammaSat, gammaUnsat based on correlation with ve
    Relation created by Fadi, according to Grundbau Taschenbuch.
    For now, these relations are used for HS, HSsmall models only.
    """
    #phi = 0.08*ve + 20
    tan_phi = 0.0014*ve + 0.4106
    phi_radian = np.arctan(tan_phi) # radian
    phi_deg = phi_radian*180/np.pi
    we = -0.0007*ve + 0.8
    gammaSat = 0.02*ve + 13
    #gamma_prime = 0.5*gammaSat + 1.5
    gammaUnsat = gammaSat

    return (phi_deg, we, gammaSat, gammaUnsat)


def get_SPW_parameters(D, S, Eref=30e6, nu=0.2, SPW131=False):
    """ Calculates SPW parameters from pile diameter D and spacing b/t piles
    """
    EA = Eref*(D**2*np.pi/(4*2*S))  # only secondary piles contribute to the axial stiffness
    #EA = Eref*(D**2*np.pi/(4*S))   # primary piles also contribute to the axial stiffness
    EA2 = EA
    EI = 0.0
    if SPW131:
        EI = Eref*(D**4*np.pi/(64*4*S))
    else:
        EI = Eref*(D**4*np.pi/(64*2*S))
    w = D**2*np.pi/(4*2*S)*10.0
    d = np.sqrt(12.0*EI/EA)
    Gref = EA/d/(2*(1 + nu)) #Gref must be followed by this relation

    return (EA, EA2, EI, w, d, Gref)



def get_CPW_parameters(D, S, Eref=30e6, nu=0.2):
    """ Calculates CPW parameters from pile diameter D and spacing b/t piles
    """
    EA = Eref*(D**2*np.pi/(4*S))
    EA2 = EA
    EI = Eref*(D**4*np.pi/(64*S))
    w = D**2*np.pi/(4*S)*10.0
    d = np.sqrt(12.0*EI/EA)
    Gref = EA/d/(2*(1 + nu)) #Gref must be followed by this relation

    return (EA, EA2, EI, w, d, Gref)


def get_steel_profile_parameters(A, I, S, E, nu):
    """ Gets parameters for the steel profile
    """
    EA = E*A*1.0e-4/S
    EA2 = EA
    EI = E*I*1.0e-8/S
    d = np.sqrt(12*EI/EA)
    Gref = EA/d/(2*(1 + nu))
    w = 58                  # 78 - 20
    return (EA, EA2, EI, w, d, Gref) 


def set_plaxis_datatypes(data):
    """ Converts a dictionary of PLAXIS2D material properties
    to data types that are expected by PLAXIS2D
    """
    for key, value in data.items():
        if key in ['MaterialName', 'SkinResistanceMultiLinear', 'SkinResistance','SkinResistanceTable', 'concrete_grade', 'IsIsotropic']:
            data[key] = value
        elif key in ['Colour', 'SoilModel', 'DrainageType', 'Elasticity', 'K0Determination', 'BeamType', 'PredefinedBeamType']:
            data[key] = int(value)
    #   elif key in ['SkinResistanceTable']:
    #       self.soil_edit_box.data[key] = ast.literal_eval(value)
        else:
            data[key] = float(value)
        
    return data


def set_nonplaxis_datatypes(data):
    """ Converts a dictionary of non PLAXIS2D material properties
    """
    for key, value in data.items():
        if key in ['nos']:
            data[key] = int(value)
        else:
            data[key] = value

    return data
    

def get_Eref_CPW(D, S, EA):
    """ Gets Eref for CPW
    """
    A = D**2 * np.pi / (4*S)
    Eref = EA/A  # Eref is reconstructed from EA and A (not from Gref)

    return Eref


def get_Eref_SPW(D, S, EA):
    """ Gets Eref for SPW
    """
    A = D**2 * np.pi / (4*2*S)
    Eref = EA/A  # Eref is reconstructed from EA and A (not from Gref)

    return Eref


def get_Eref_SPW131(D, S, EA):
    """ Gets Eref for SPW131
    """
    A = D**2 * np.pi / (4*S)
    Eref = EA/A  # Eref is reconstructed from EA and A (not from Gref)

    return Eref


def get_Eref_Dwall(Gref, nu):
    """ Gets Eref for Dwall
    """
    Eref = Gref*2*(1 + nu)

    return Eref


def calc_E_Modul_MIP(fmk, fines_content):
    """ Calculates E-Modulus for MIP in MPa"""
    if fines_content < 10.0:
        fines_content = 10.0

    fm_mittel = get_fm_mittel(fmk)
    E_modul = fm_mittel*550.0 + 79005.0 * fines_content**(-0.979)
    return E_modul


def get_fm_mittel(fm_k):
    """ Gets fm_mittel by searching"""
    fmk_found = False
    counter = 0
    tol = 0.0001

    search_fm_mittel = 0.0 
    decrease_factor = 2.0
    delta_fm = 1.0

    while not fmk_found:
        search_fm_mittel += delta_fm
        trail_fmk = get_a_factor(search_fm_mittel)*search_fm_mittel
        if abs(trail_fmk - fm_k) < tol:
            fmk_found = True
            break
        if trail_fmk > fm_k:
            search_fm_mittel -= delta_fm
            delta_fm = delta_fm/decrease_factor
        counter += 1

    return search_fm_mittel


def get_a_factor(fmk):
    """ Gets a-factor"""
    fmk_min = 4.0
    fmk_max = 12.0
    a_factor_fmk_min = 0.6
    a_factor_fmk_max = 0.75
    a_factor = (a_factor_fmk_max - a_factor_fmk_min) / (fmk_max - fmk_min) * (fmk - fmk_min) + a_factor_fmk_min
    if fmk <= fmk_min:
        a_factor = a_factor_fmk_min
    elif fmk >= fmk_max:
        a_factor = a_factor_fmk_max

    return a_factor