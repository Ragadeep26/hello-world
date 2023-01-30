# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 11:16:15 2020

@author: nya
"""

import os
import sys
import xlwings as xw

def get_steel_areas_dw(M,N,Q, DD=1200, BB=2800, Ho=10, Ho2=10, Spacing=1.0):
    """ Gets steel areas
    """
    PATH = r'D:\Data\3Packages\Moniman'
    wb = xw.Book(os.path.join(PATH, r'dimensioning\0_stb.xlsm'))
    #wb = xw.Book(os.path.join(r'C:\Users\nya\Packages\Moniman', r'dimensioning\0_stb.xlsm')) # for debugging
    
    xw.Visible = False

    StB_R_MN1 = wb.macro('StB_R_MN')
    StB_R_Q= wb.macro('StB_R_Q')

    #common parameters (optional)
    cod=4  # EC = 3, Combined=4

    #concrete parametes
    f_ck        = 35          #30MPA
    alpha       = 0.85        #0.85
    eps_cy      = 0.002   #0.002
    eps_cu      = 0.0035     #0.0035
    n2          = 2.0          #2
    delt_S      = 0.15          #0.15
    #delt_K      = "0.10 0.2"          #0.15
    delt_K      = '0.15 0.0'          #0.15

    #steel Parameters Vertical[0]
    f_yk        = 500
    f_tk        = 600
    Es          = 200000         #200000
    eps_su      = 0.025    #0.025
    RissP1      = 0       #240 crack variable = 0 with no crack


    #steel Parameters Shear
    f_yk_sh     = 500
    f_tk_sh     = 600
    #Es_sh       = 200000        #200000
    #eps_su_sh   = 0.025         #0.025

    #factors
    gam_load    = 1.35
    gam_c       = 1.50
    gam_s       = 1.15

    #shear parameters
    TauP1=0; TauP2=0; TauP3=0


    #dw Parameters
    vorAs1      = 0                              #manual min steel reinforcement area, As1
    vorAs2      = 0                              #manual min steel reinforcement area, As2


    sym0=False
    minBew  = 2 #2 with min. reinforcement

    #internal forces
    Mk= M*Spacing
    Nk= N*Spacing 
    Qk= Q*Spacing 

    Md=Mk*gam_load 

    #################################
    Nd=Nk*gam_load # "favourable"
        
    Qd=Qk*gam_load  

    A_s1=0;A_s2=0;Asw=0


    A_s1 = StB_R_MN1(cod-1,gam_c,gam_s,Md,Nd,Mk,Nk,DD,BB,Ho,Ho2,sym0, vorAs1, vorAs2,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk ,Es, eps_su, RissP1, minBew,17)
    A_s2 = StB_R_MN1(cod-1,gam_c,gam_s,Md,Nd,Mk,Nk,DD,BB,Ho,Ho2,sym0, vorAs2, vorAs2,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk,Es, eps_su, RissP1, minBew,18)
    Asw = StB_R_Q(cod-1,gam_c,gam_s,Md,Nd,Qd, DD,BB,Ho,Ho2, A_s1, A_s2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk_sh,f_tk_sh, Es, eps_su, TauP1, TauP2, TauP3,19)
    print((cod-1,gam_c,gam_s,Md,Nd,Qd, DD,BB,Ho,Ho2, A_s1, A_s2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk_sh,f_tk_sh, Es, eps_su, TauP1, TauP2, TauP3,19))

    #print(cod,gam_c,gam_s,Md,Nd,Qd, DD,BB,Ho,Ho2, A_s1, A_s2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk_sh,f_tk_sh, Es, eps_su, TauP1, TauP2, TauP3,19)
    #print(A_s1,A_s2,Asw)
    return (A_s1,A_s2,Asw)

if __name__ == '__main__':
    As1, As2, Asw = get_steel_areas_dw(1140, 472, 339, DD=800, BB=2800)
    print(As1, As2, Asw)
    
    As1, As2, Asw = get_steel_areas_dw(615, 567, 289, DD=800, BB=2800)
    print(As1, As2, Asw)

    As1, As2, Asw = get_steel_areas_dw(615, 567, 289, DD=800, BB=2800, Ho=10, Ho2=10, Spacing=1.0)      #from excel
    print(As1, As2, Asw)

    As1, As2, Asw = get_steel_areas_dw(abs(-108.4), 237.9, -128.6, DD=1000, BB=2600, Ho=100, Ho2=100)      #from excel
    print(As1, As2, Asw)
