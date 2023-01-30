# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 14:43:57 2022

@author: nya
"""


import sys
sys.path.append(r'D:\Data\3Packages\Moniman')
import time

#from dimensioning.py_StB.StB_R_As_and_a_s import StB_R_MN, StB_R_Q # current py_StB
#from dimensioning.py_StB.StB_K_As_and_a_s import StB_K_MN, StB_K_Q # current py_Stb

from dimensioning.py_StB_nya.StB_R_As_and_a_s import StB_R_MN, StB_R_Q
from dimensioning.py_StB_nya.StB_K_As_and_a_s import StB_K_MN, StB_K_Q


def test_calculations():
    for _ in range(100):
        A_s, a_s = evaluate_py_StB_circ(2, 1.5, 1.15, 1.35, 810, 0, 600 ,800, 100, 30, 0.909090909, 0.002, 0.0035, 2, 0.1818182, "0.10 0.2" ,500, 525, 200000, 0.025, 240, 1)
        #A_s1, A_s2, a_s = evaluate_py_StB_rect(2, 1.5, 1.15, 1.35, 810, 0, 600 ,800, 2800, 100, 100, 0, 30, 0.909090909, 0.002, 0.0035, 2, 0.1818182, "0.10 0.2" ,500, 525, 200000, 0.025, 240,1)



def evaluate_py_StB_circ(code, gam_c, gam_s, gam_perm, Mi, Ni, Qi, D, H, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew):
    """ Gets required reinforcement 
    This function will be called in pool by multiprocessing
    """
    A_s_i = StB_K_MN(code, gam_c, gam_s, gam_perm*Mi, gam_perm*Ni, Mi, Ni, D, H, 0.0, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 17)
    a_s_i = StB_K_Q(code, gam_c, gam_s, gam_perm*Mi, gam_perm*Ni, gam_perm*Qi, D, H, float(A_s_i), f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, 0.0, 0.0, 0.0, 19)
    return float(A_s_i), max(float(a_s_i), 0.0)


def evaluate_py_StB_rect(code, gam_c, gam_s, gam_perm, Mi, Ni, Qi, D, B, H1, H2, sym, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew):
    """ Gets required reinforcement 
    This function will be called in pool by multiprocessing
    """
    Ni = 0.0 if (0 < Ni < 10.0) else Ni # strange behavior in 0_stb: small tension force leads to large req. a_s
    Mi = 0.0 if (-10.0 < Mi < 10.0) else Mi # strange behavior in 0_stb: small moment leads to large req. a_s
    A_s1_i = StB_R_MN(code, gam_c, gam_s, gam_perm*Mi, gam_perm*Ni, Mi, Ni, D, B, H1, H2, sym, 0.0, 0.0 , f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 17)
    A_s2_i = StB_R_MN(code, gam_c, gam_s, gam_perm*Mi, gam_perm*Ni, Mi, Ni, D, B, H1, H2, sym, 0.0, 0.0 , f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 18)
    a_s_i = StB_R_Q(code, gam_c, gam_s, gam_perm*Mi, gam_perm*Ni, gam_perm*Qi, D, B, H1, H2, A_s1_i, A_s2_i, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, 0.0, 0.0, 0.0, 19)

    return float(A_s1_i), -float(A_s2_i), max(float(a_s_i), 0.0)
    
    
if __name__ == '__main__':
    start_time1 = time.time() 
    test_calculations()
    print("--- %s seconds ---" % (time.time() - start_time1))