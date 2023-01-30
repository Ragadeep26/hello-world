###----DIMENSIONING OF CIRCULAR REINFORCEMNT-----###
'''
Date of Original Version -26th July, 2017 -
Date of Python version - 6th Feb, 2020 - ----
'''
###----Python Version created by RAGADEEP BOJJA (Translate of 0_stb created in VBA by Dr. Berthold Klobe)----###
#------------------------------------------------------------------------------------------------------#
#
#Required Modules
import math 
from dimensioning.py_StB_nya.GlobalVar import *
#Constants for Threshold stress limits for stboNorm = 0 (DIN 1045:1988)#
stbkitmax = 50
stbkepse3 = 0.0001
stbkepse5 =0.00001
stbkepse7 = 0.0000001
#stbofck (beta_WN) = 15
stbk15tau012 = 0.5
stbk15tau02 = 1.2
stbk15tau03 = 2
stbk15tau1 = 1.4           #Verbundbereich I
stbk15tau2 = 0.7           #Verbundbereich II
#stbofck (beta_WN) = 25
stbk25tau012 = 0.75
stbk25tau02 = 1.8
stbk25tau03 = 3
stbk25tau1 = 1.8           #Verbundbereich I
stbk25tau2 = 0.9           #Verbundbereich II
#stbofck (beta_WN) = 35
stbk35tau012 = 1
stbk35tau02 = 2.4
stbk35tau03 = 4
stbk35tau1 = 2.2           #Verbundbereich I 
stbk35tau2 = 1.1           #Verbundbereich II
#stbofck (beta_WN) = 45
stbk45tau012 = 1.1
stbk45tau02 = 2.7
stbk45tau03 = 4.5
stbk45tau1 = 2.6           #Verbundbereich I
stbk45tau2 = 1.3           #Verbundbereich II
#stbofck (beta_WN) = 55
stbk55tau012 = 1.25
stbk55tau02 = 3
stbk55tau03 = 5
stbk55tau1 = 3             #Verbundbereich I 
stbk55tau2 = 1.5           #Verbundbereich II

# Fixed Values #
# Gaping gap:
# Regardless of the selected standard, the regulation from DIN EN 1992-1-1: 2004 + AC: 2010 + NA: 2011 (stboNorm = 3) is applied uniformly.
# This regulation says that in the unreinforced rectangular cross-section, a center to the maximum e = 0.4 * stboD is permitted for the design internal forces.
# This corresponds to an elongation eps_c1 / eps_c2 = -0.35% / 1.105%. For circular cross sections, this elongation state is reached for e = 0.3803 * stboD.
stbkKemax = 0.3803
stbkRemax = 0.4
#------------------------------------------------------------------------------------------------------#
'''
# stboNorm:      0 = DIN 1045:1988
#                1 = DIN 1045:2008
#                2 = EN 1992-1-1:2004  (Eurocode 2)
#                3 = DIN EN 1992-1-1:2004 + AC:2010 + NA:2011
'''
#------------------------------------------------------------------------------------------------------#
##############################----Input and output values###############################################
#------------------------------------------------------------------------------------------------------#  
'''
# Input and output values
# Norm: 0 = DIN 1045: 1988
# 1 = DIN 1045: 2008
# 2 = EN 1992-1-1: 2004 (Eurocode 2)
# 3 = DIN EN 1992-1-1: 2004 + AC: 2010 + NA: 2011

# gam_c: safety factor / partial safety factor for concrete (depending on standards) [1]
# gam_s: partial safety factor for reinforcement (only for norm> 0) [1]

# Md: design value of the bending moment, negative values ​​result in tension for As2 [kNm]
# ND: design value of normal force, tension positive, pressure negative [kN]
# QD: design value of the shear force [kN]

# DD: circle diameter [mm]
# HH_: edge distance of the reinforcement [mm]
# vorAs0: existing reinforcement As [cm ^ 2]

# f_ck: Concrete compressive strength (cube strength for standard = 0, cylinder strength for standard> 0) [MN / m ^ 2]
# alpha: reduction factor for the concrete compressive strength [1]
# eps_cy: start of plastic concrete expansion (end of the parabola branch) [1]
# eps_cu: elongation at break of the concrete (end of plastic compression) [1]
# n2: parabola exponent of the concrete [1]
# delt_S: Increased safety for pressed concrete cross section / unreinforced concrete (depending on the standard) [1]
# delt_K: associated expansion range / proportion of the compressive force that must be covered by reinforcement (depending on the standard) [String]

# f_yk: yield strength of the reinforcement [MN / m ^ 2]
# f_tk: tensile strength of the reinforcement [MN / m ^ 2]
# Es: Young's modulus of reinforcement [MN / m ^ 2]
# eps_su: elongation at break of the reinforcement (end of plastic elongation) [1]

# TauP1: for norm = 0: specification of tau_012 [MN / m ^ 2]
# TauP2: for norm = 0: specification of tau_02 [MN / m ^ 2]
# TauP3: for norm = 0: specification of tau_03 [MN / m ^ 2]

# for norm> 0: specification of cot (theta), min. 1.00, max. 3.00 [1]

# ii: Switch for the return value
# 11 = concrete compressive force [kN]
# 12 = lever arm of the concrete pressure force [mm]
# 13 = steel tensile force [kN]
# 14 = lever arm of steel tensile force [mm]
# 15 = steel pressure force [kN]
# 16 = lever arm of the steel pressure force [mm]
# 17 = resulting pair of forces [kN]
# 18 = lever arm of the resulting pair of forces [mm]
# 19 = required shear reinforcement stbZerfas [cm ^ 2 / m]
# stbZerfas = -1 #: impermissibly high shear load
# for norm = 0
# 20 = tau_0 [MPa]
# 21 = tau_012 [MPa]
# 22 = tau_02 [MPa]
# 23 = tau_03 [MPa]
# for norm> 0
# 20 = stbZminas [cm ^ 2 / m]
# 21 = stbZVRdc [kN]
# reinforced cross section
# 22 = stbZVRdmax [kN]
# 23 = stbZcottheta [1]
# unreinforced cross section
# 22 = stbZtaucp [MPa]
# 23 = stbZfcvd [MPa]
'''
#------------------------------------------------------------------------------------------------------#
#################################----Input Functions----################################################
#------------------------------------------------------------------------------------------------------# 

def StB_K_MN(Norm, gam_c, gam_s, Md, Nd, Mk,Nk ,DD, HH_, vorAs0 ,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K,f_yk, f_tk, Es, eps_su, RissP1, minBew,ii):
    # Function that calculates the Longitudinal reinforcement Dimensions of the Desired Circular cross- section
    mue0 = [0,0,0]

    # Evidence and cross section
    stboNachweis = 1
    stboQuer = 1

    RechenWerte(Norm, gam_c, gam_s, Md, Nd, 0, Mk, Nk, DD, 0, HH_, HH_, True, vorAs0, 0, 0, 0,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 0, 0, 0, ii)

    if stbZbFehler ==  True : 
        print('error = ',stbZbFehler)
    
    # Determination of the fracture condition: safety factors, strains, internal forces, associated lever arms
    if stboNullSd ==  True :
        stbZerfmue0[0] = 0
        stbZmue0[0] = stbovormue0[0]
        if stbobminBew ==  True :
            stbZmue0[0] = max(stbZmue0[0], stbomue0Riss[0])

    else:
        if stbobDruc[2] == True and stbovormue0[0] <= stbkepse7 and stbobminBew == False :
            Snue0_K()
            if stbZnue0 > 0 :
                stbZerfmue0[0] = 0
                stbZmue0[0] = 0
                
        else:
            stbZnue0 = -1

        if stbZnue0 < 0 :
            SRissB()

    # Conditions to give the output
    # Inputs must be specified properly to get correct outputs
    if stbZbFehler :
        StB_K_Mn = "Error[0]"

    elif stboii == 11 :
        # ultimate strain of concrete    ε_c		
        StB_K_Mn = stbZepscd[1 + stboVMd]

    elif stboii == 12 :
        # ultimate strain of concrete    ε_c
        StB_K_Mn = stbZepscd[2 - stboVMd]

    elif stboii == 13 :
        # ultimate strain of steel         ε_s		
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbZepssd[1 + stboVMd]

    elif stboii == 14 :
        # ultimate strain of steel         ε_s
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbZepssd[2 - stboVMd]

    elif stboii == 15 :
        #internal forces R_Md [KNm]	
        StB_K_Mn = math.copysign(1,Md) * stbZRMd * 1000 * stboKR ** 3 * stbofck

    elif stboii == 16 :
        #internal forces R_Nd [KN]	
        StB_K_Mn = stbZRNd * 1000 * stboKR ** 2 * stbofck

    elif stboii == 17 :
        #Reinforcement Area A_s [cm2]
        StB_K_Mn = 10000 * stbZmue0[0] * math.pi * stboKR ** 2 * stbofck / stboftk

    elif stboii == 19 :
        # utilization   =   req. A_s / A_s		
        if stboNullSd :
            StB_K_Mn = 0
        else:
            if stbZmue0[0] < stbkepse7 :
                StB_K_Mn = stboNd / stbZRNd
            else:
                if vorAs0 < stbkepse7 :
                    StB_K_Mn = max(stbZerfmue0[0], 0) / stbZmue0[0]
                else:
                    mue0[0] = stbZmue0[0]
                    StB_K_Mn = StB_K_MN(Norm, gam_c, gam_s, Md, Nd, Mk, Nk,DD, HH_, 0,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, 0, minBew, 17)/ 10000 / math.pi / stboKR ** 2 / stbofck * stboftk / mue0[0]
    
    # Stbziz = 2 from here (Cracked Concrete)
    elif stboii == 21 :
        # strain of concrete   ε_c
        StB_K_Mn = stbZepsck[1 + stboVMk]

    elif stboii == 22 :
        # strain of concrete   ε_c
        StB_K_Mn = stbZepsck[2 - stboVMk]

    elif stboii == 23 :
        # strain of steel     ε_s	
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbZepssk[1 + stboVMk]

    elif stboii == 24 :
        # strain of steel     ε_s
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbZepssk[2 - stboVMk]

    elif stboii == 25 :
        #internal forces R_Mk [KNm]
        StB_K_Mn = math.copysign(1,Mk) * stbZRMk * 1000 * stboKR ** 3 * stbofck

    elif stboii == 26 :
        #internal forces R_Nk [KN]
        StB_K_Mn = stbZRNk * 1000 * stboKR ** 2 * stbofck

    elif stboii == 27 :
        #reinforce. stress σs [MPa]	
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbfsig_s(stbZepssk[1 + stboVMk])

    elif stboii == 28 :
        #reinforce. stress σs [MPa]	
        if stbZmue0[0] < stbkepse7 :
            StB_K_Mn = ""
        else:
            StB_K_Mn = stbfsig_s(stbZepssk[2 - stboVMk])

    else:
        StB_K_Mn = ""

    return StB_K_Mn
#------------------------------------------------------------------------------------------------------#  
    
def StB_K_Q(Norm, gam_c, gam_s, Md, Nd, Qd, DD, HH_, vorAs0, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, TauP1, TauP2, TauP3, ii):
    # Function that calculates the Shear reinforcement Dimensions of the Desired Circular cross- section

    RechenWerte(Norm, gam_c, gam_s, Md, Nd, Qd, 0, 0, DD, 0, HH_, HH_, False, vorAs0, 0, 0, 0, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, 0, 0, TauP1, TauP2, TauP3, ii)
    
    if stbZbFehler :
         print('error = ',stbZbFehler)

    # # Determination of the fracture condition: safety factors, strains, internal forces, associated lever arms
    if not stboNullSd :
        BruchC1S1()

    if stboNorm == 0 :
        QuerBemessN0()
    elif stboNorm > 0 :
        QuerBemessN123()

    # Conditions to give the output
    # Inputs must be specified properly to get correct outputs
    if stbZbFehler == True :
        StB_K_Q = "Error[0]"

    elif stboii == 11 :
        # Internal Force [kN] - C_Cu
        if stbZNucs[0] > -stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = stbZNucs[0] * 1000 * stboKR ** 2 * stbofck

    elif stboii == 12 :
        # Lever Arm [mm] - C_Cu
        if stbZNucs[0] > -stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = math.copysign(1,Md) * stbZzi[0] * 1000

    elif stboii == 13 :
        # Internal Force [kN] - T_Su
        if stbZNucs[1] < stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = stbZNucs[1] * 1000 * stboKR ** 2 * stbofck

    elif stboii == 14 :
        # Lever Arm [mm] - T_Su
        if stbZNucs[1] < stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = math.copysign(1,Md) * stbZzi[1] * 1000

    elif stboii == 15 :
        # Internal Force [kN] - C_Su
        if stbZNucs[2] > -stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = stbZNucs[2] * 1000 * stboKR ** 2 * stbofck

    elif stboii == 16 :
        # Lever Arm [mm] - C_Su
        if stbZNucs[2] > -stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = math.copysign(1,Md) * stbZzi[2] * 1000

    elif stboii == 17 :
        # Internal Force [kN] - Couple of Forces
        if stbZNucs[3] < stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = stbZNucs[3] * 1000 * stboKR ** 2 * stbofck

    elif stboii == 18 :
        # Lever Arm [mm] - Couple of Forces
        if stbZNucs[3] < stbkepse7 :
            StB_K_Q = ""
        else:
            StB_K_Q = stbZzi[3] * 1000

    elif stboii == 19 :
        # shear reinforce.   req. a_s [cm²/m]		
        StB_K_Q = stbZerfas
        
    elif stboii == 20 :
        # min. a_s    [cm²/m]	
        if stboNorm == 0 :
            StB_K_Q = stbZtau0
        else:
            StB_K_Q = stbZminas

    elif stboii == 21 :
        # V_Rdc [KN]
        if stboNorm == 0 :
            StB_K_Q = stbotau012
        else:
            StB_K_Q = stbZVRdc * 1000

    elif stboii == 22 :
        # V_Rdmax [KN]
        if stboNorm == 0 :
            StB_K_Q =stbotau02
        else:
            if stbZmue0[0] < stbkepse7 :
                StB_K_Q = stbZtaucp
            else:
                StB_K_Q = stbZVRdmax * 1000

    elif stboii == 23 :
        # cot(θ) [1]
        if stboNorm == 0 :
            StB_K_Q = stbotau03
        else:
            if stbZmue0[0] < stbkepse7 :
                StB_K_Q = stbZfcvd
            else:
                StB_K_Q = stbZcottheta

    else:
        StB_K_Q = ""
        
    return StB_K_Q

#------------------------------------------------------------------------------------------------------#  
#------------------------------------------------------------------------------------------------------#
#################################----Module Begins Here----#############################################
#------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------#
def RechenWerte(Norm, gam_c, gam_s, Md, Nd, Qd, Mk, Nk,DD, BB, HH_, H__, sym0 , vorAs0, delta, vorAs1, vorAs2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K,f_yk, f_tk, Es, eps_su, RissP1, minBew, TauP1, TauP2, TauP3, ii):

    #Norm
    stboNorm = Norm
    stboQuer = 1

    #Geometry
    stboD = DD / 1000
    stboRB = BB / 1000
    stboKR = stboD / 2
    stboH[1] = HH_ / 1000
    stboH[2] = H__ / 1000
    stboRe = stboKR - stboH[1]
    stbodelt2 = delta / 2
    if abs(stboH[1] - stboH[2]) > stbkepse5:
        stbobHkrit = True
    else:
        stbobHkrit = False
    
    #Concrete
    stbofck = f_ck
    stboalpha = alpha
    stboepscy = eps_cy
    stboepscu = eps_cu
    stbon2 = n2

    #Reinforcement (Steel)
    stbofyk = f_yk
    stboftk = f_tk
    stboepssy = f_yk / Es
    stboepssu = eps_su
    Nd1 = Nd

    #Dimensionless Internal Forces
    stboNd = Nd1 / 1000 / stboKR ** 2 / stbofck
    stboMd = abs(Md) / 1000 / stboKR ** 3 / stbofck
    stboQd = abs(Qd) / 1000 / stboKR ** 2 / stbofck
    stboNk = Nk / 1000 / stboKR ** 2 / stbofck
    stboMk = abs(Mk) / 1000 / stboKR ** 3 / stbofck
    stboHQ = stboD * math.sqrt(math.pi / 4)
    stboBQ = stboD * math.sqrt(math.pi / 4)

    #LoadfromMiddle
    if abs(stboNd) < stbkepse7:
        stboeNd = stboMd / stbkepse7
    else:
        stboeNd = stboMd / stboNd
    
    if abs(stboNk) < stbkepse7:
        stboeNk = stboMk / stbkepse7
    else:
        stboeNk = stboMk / stboNk

    #Intiating Zero pressures
    if abs(stboNd) < stbkepse5 and stboMd < stbkepse5:
        #For DesignForces
        stboNullSd = True
        stboVMd = 0
        #For Characteristic Forces
        stboNullSk = True
        stboVMk = 0
    else:
        #For DesignForces
        stboNullSd = False
        if Md >= 0:
            stboVMd = 0
        else:
            stboVMd = 1
        
        #For DesignForces
        if abs(stboNk) < stbkepse5 and stboMk < stbkepse5:
            stboNullSk = True
        else:
            stboNullSk = False
            if Mk >= 0:
                stboVMk = 0
            else:
                stboVMk = 1

        #Pressure bar (stbobDruc) Boolean
        if stboNd < -stbkepse5:
            stbobDruc[1] = True
            if (((stboQuer == 1 or stboQuer == 2) and stboMd / abs(stboNd) < 1) or (stboQuer == 3 and stboMd/abs(stboNd) < 0.5)):
                stbobDruc[2] = True
                if ((stboQuer == 1 or stboQuer == 2) and stboMd / abs(stboNd) < 2 * stbkKemax)or(stboQuer == 3 and stboMd / abs(stboNd) < stbkRemax):
                    stbobDruc[3] = True
                else:
                    stbobDruc[3] = False
                
            else:
                stbobDruc[2] = False
                stbobDruc[3] = False
            
        else:
            stbobDruc[1] = False
            stbobDruc[2] = False
            stbobDruc[3] = False
        
    #Specified Reinforcement (Basic and Minimum)
    if stboNachweis == 1:
        vAs1 = max(vorAs1, vorAs2)
        vAs2 = min(vorAs1, vorAs2)
    elif stboNachweis == 2:
        vAs1 = vorAs1
        vAs2 = vorAs2

    if stboQuer == 1 or stboQuer == 2:
        stbovormue0[0] = max(vorAs0 / 10000 / math.pi / stboKR ** 2 * stboftk / stbofck, 0)
        stbovormue0[1] = max(vAs1 / 10000 / math.pi / stboKR ** 2 * stboftk / stbofck, 0)
        stbovormue0[2] = max(vAs2 / 10000 / math.pi / stboKR ** 2 * stboftk / stbofck, 0)
    elif stboQuer == 3:
        stbovormue0[0] = 0
        stbovormue0[1] = max(vAs1 / 10000 / stboD / stboRB * stboftk / stbofck, 0)
        stbovormue0[2] = max(vAs2 / 10000 / stboD / stboRB * stboftk / stbofck, 0)
    
    if sym0:
        stbovormue0[2] = stbovormue0[1]
    
    #Basic values ​​of the safety factors and auxiliary variables
    SgamCSini(gam_c, gam_s, delt_S, delt_K, stboalpha)

    # Without torque stress (or stboeNd = stbfeBew) or with an unequal sign of the moments for design and
    # Usage internal forces or by default, the statically required reinforcement is symmetrical.
    # For uneven edge distances of the reinforcement (stbobHkrit = True) and stbosymmue0 = True exists for (almost) centric
    # Tensile load is not a solution. Therefore this case is excluded.
    stbZiZ = 1                  
    # The function stbfeBew() is executed with fractional values from geometry
    if (abs(stboeNd - stbfeBew()) < stbkepse7 and stboNd > stbkepse5) or (abs(stboeNd) < stbkepse7 and stboNd < -stbkepse5) or((stboVMd != stboVMk or sym0 == True) and stbobHkrit == False):
        stbosymmue0 = True
    else:
        stbosymmue0 = False

    # Crack width limitation: maximum steel tension when in use, 
    # stboRissP1 <1 # -> no crack width limitation
    stboRissP1 = RissP1

    # '' Critical strain states are required for the iterative determination of the equilibrium states
    stbZiZ = 1   # The Sdehnkrit routine is carried out with fractional values         
    Sdehnkrit()

    # Minimum reinforcement (stbZmue0> = stbomue0Riss)
    if stboNachweis == 1:
        # Determination of the minimum reinforcement stbomue0Riss for the crack moment
        Smue0Riss()        
        if minBew > 0 or (stbkbKlaffPruef and stbobDruc[2] and stbobDruc[3] == False):
            stbobminBew = True
        else:
            stbobminBew = False
        
    elif stboNachweis == 2:
        stbobminBew = False

    stboii = ii

    if stboNachweis == 1:
        if stboii < 20:
            stbZiZ = 1
        else:
            stbZiZ = 2
    elif stboNachweis == 2:
        # design for the fracture state
        stbZiZ = 1
        # Reinforcement content is specified, is not calculated
        stbZmue0[0] = stbovormue0[0]
        stbZmue0[1] = stbovormue0[1]
        stbZmue0[2] = stbovormue0[2]
        # Initial values ​​are pre-assigned
        stbZgamC[1] = stbogamC[1]
        stbZgamS[1] = stbogamS[1]
        for i in range(0,4):
            stbZNucs[i] = 0
            stbZzi[i] = 0

        # Specifications for the shear force design (Anchorage and Shock)
        if stboNorm == 0:
            # Limits of shear stress and bond stresses
            if stbofck <= 15:
                stbotau012 = round(stbk15tau012 * stbofck / 15, 2)
                stbotau02 = round(stbk15tau02 * stbofck / 15, 2)
                stbotau03 = round(stbk15tau03 * stbofck / 15, 2)
                stbotau1 = round(stbk15tau1 * stbofck / 15, 2)
                stbotau2 = round(stbk15tau2 * stbofck / 15, 2)
            elif stbofck <= 25:
                stbotau012 = round(stbk15tau012 + (stbk25tau012 - stbk15tau012) * (stbofck - 15) / 10, 2)
                stbotau02 = round(stbk15tau02 + (stbk25tau02 - stbk15tau02) * (stbofck - 15) / 10, 2)
                stbotau03 = round(stbk15tau03 + (stbk25tau03 - stbk15tau03) * (stbofck - 15) / 10, 2)
                stbotau1 = round(stbk15tau1 + (stbk25tau1 - stbk15tau1) * (stbofck - 15) / 10, 2)
                stbotau2 = round(stbk15tau2 + (stbk25tau2 - stbk15tau2) * (stbofck - 15) / 10, 2)
            elif stbofck <= 35:
                stbotau012 = round(stbk25tau012 + (stbk35tau012 - stbk25tau012) * (stbofck - 25) / 10, 2)
                stbotau02 = round(stbk25tau02 + (stbk35tau02 - stbk25tau02) * (stbofck - 25) / 10, 2)
                stbotau03 = round(stbk25tau03 + (stbk35tau03 - stbk25tau03) * (stbofck - 25) / 10, 2)
                stbotau1 = round(stbk25tau1 + (stbk35tau1 - stbk25tau1) * (stbofck - 25) / 10, 2)
                stbotau2 = round(stbk25tau2 + (stbk35tau2 - stbk25tau2) * (stbofck - 25) / 10, 2)
            elif stbofck <= 45:
                stbotau012 = round(stbk35tau012 + (stbk45tau012 - stbk35tau012) * (stbofck - 35) / 10, 2)
                stbotau02 = round(stbk35tau02 + (stbk45tau02 - stbk35tau02) * (stbofck - 35) / 10, 2)
                stbotau03 = round(stbk35tau03 + (stbk45tau03 - stbk35tau03) * (stbofck - 35) / 10, 2)
                stbotau1 = round(stbk35tau1 + (stbk45tau1 - stbk35tau1) * (stbofck - 35) / 10, 2)
                stbotau2 = round(stbk35tau2 + (stbk45tau2 - stbk35tau2) * (stbofck - 35) / 10, 2)
            elif stbofck <= 55:
                stbotau012 = round(stbk45tau012 + (stbk55tau012 - stbk45tau012) * (stbofck - 45) / 10, 2)
                stbotau02 = round(stbk45tau02 + (stbk55tau02 - stbk45tau02) * (stbofck - 45) / 10, 2)
                stbotau03 = round(stbk45tau03 + (stbk55tau03 - stbk45tau03) * (stbofck - 45) / 10, 2)
                stbotau1 = round(stbk45tau1 + (stbk55tau1 - stbk45tau1) * (stbofck - 45) / 10, 2)
                stbotau2 = round(stbk45tau2 + (stbk55tau2 - stbk45tau2) * (stbofck - 45) / 10, 2)
            else:
                stbotau012 = stbk55tau012
                stbotau02 = stbk55tau02
                stbotau03 = stbk55tau03
                stbotau1 = stbk55tau1
                stbotau2 = stbk55tau2
            
            if TauP1 > stbkepse3:
                stbotau012 = TauP1
            
            if TauP2 > stbkepse3:
                stbotau02 = TauP2
            
            if TauP3 > stbkepse3:
                stbotau03 = TauP3
            
        elif stboNorm > 0:
            stbomaxcottheta = TauP3
       
    stbZeps_c[1] = 0
    stbZeps_c[2] = 0
    stbZeps_s[1] = 0
    stbZeps_s[2] = 0
    stbZeps_s[2] = 0
    SRechenWerteZ(2)

    # Initial Values are calculated (Check if there is any error with the values =-> stbZbFehler = True/False)
    if stboNorm < 0 or stboD < stbkepse5 or ((stboQuer == 1 or stboQuer == 2) and stboKR < stbkepse5) or (stboQuer == 3 and stboRB < stbkepse5) or stboD - stboH[1] - stboH[2] < -stbkepse5 or stbofck < stbkepse5 or stboalpha < stbkepse5 or stboepscy < stbkepse7 or stboepscu < stboepscy - stbkepse7 or stbofyk < stbkepse5 or stboftk < stbofyk - stbkepse5 or stboepssy < stbkepse7 or stboepssu < stboepssy - stbkepse7 or stbogamC[0] < stbkepse5 or stbogamC[1] < stbkepse5 or stbogamS[0] < stbkepse5 or stbogamS[1] < stbkepse5 or (stboNachweis == 2 and stbotau02 < stbotau012 - stbkepse7) or (stboNachweis == 2 and stbotau03 < stbotau02 - stbkepse7):
        stbZbFehler = True
    else:
        stbZbFehler = False                        #print(RechenWerte)
#------------------------------------------------------------------------------------------------------#

def SRechenWerteZ(InOut):

    # There are some routines that are performed for both the fracture state (stbZiZ = 1) and the usage state (stbZiZ = 2).
    # With the call SRechenWerteZ (1), depending on the value of the status flag, the relevant quantities are saved in the "neutral" calculation variables.
    # With the call SRechenWerteZ (2) at the end of the routine the values ​​of the "neutral" calculation variables can be saved back into the appropriate sizes.
    # There are some routines that are performed for both the fracture state (stbZiZ = 1) and the use state (stbZiZ = 2).
    # With the call SRechenWerteZ (1), depending on the value of the status flag, the relevant quantities are saved in the "neutral" calculation variables.
    # With the call SRechenWerteZ (2) at the end of the routine the values ​​of the "neutral" calculation variables can be saved back into the appropriate sizes.
    
    if InOut == 1:
        if stbZiZ == 1:
            stbZ_H[1] = stboH[1 + stboVMd]
            stbZ_H[2] = stboH[2 - stboVMd]
            stbZeps_c[1] = stbZepscd[1]
            stbZeps_c[2] = stbZepscd[2]
            stbZeps_s[1] = stbZepssd[1]
            stbZeps_s[2] = stbZepssd[2]
        elif stbZiZ == 2:
            stbZ_H[1] = stboH[1 + stboVMk]
            stbZ_H[2] = stboH[2 - stboVMk]
            stbZeps_c[1] = stbZepsck[1]
            stbZeps_c[2] = stbZepsck[2]
            stbZeps_s[1] = stbZepssk[1]
            stbZeps_s[2] = stbZepssk[2]
        
    elif InOut == 2:
        if stbZiZ == 1:
            stbZepscd[1] = stbZeps_c[1]
            stbZepscd[2] = stbZeps_c[2]
            stbZepssd[1] = stbZeps_s[1]
            stbZepssd[2] = stbZeps_s[2]
        elif stbZiZ == 2:
            stbZepsck[1] = stbZeps_c[1]
            stbZepsck[2] = stbZeps_c[2]
            stbZepssk[1] = stbZeps_s[1]
            stbZepssk[2] = stbZeps_s[2]                #print (SRechenWerteZ)
#------------------------------------------------------------------------------------------------------#

def SgamCSini(gam_c, gam_s, delt_S, delt_K, stboalpha):
    # Partial safety factors
    stbogamC[1] = gam_c / stboalpha
    if stboNorm == 0:
        stbogamC[0] = (gam_c + delt_S) / stboalpha
    elif stboNorm == 1:
        stbogamC[0] = (gam_c + delt_S) / stboalpha
    elif stboNorm == 2:
        stbogamC[0] = gam_c / (stboalpha - delt_S)
    elif stboNorm == 3:
        stbogamC[0] = gam_c / (stboalpha - delt_S)

    if stboNorm == 0:
        stbogamS[1] = gam_c
        stbogamS[0] = gam_c + delt_S
    elif stboNorm > 0:
        stbogamS[1] = gam_s
        stbogamS[0] = gam_s
    Smue0Druc(delt_S, delt_K)                                           #print(SgamCSini)
#------------------------------------------------------------------------------------------------------#

def stbfeBew():
    # Reinforcement Geometries Dimensionless
    SRechenWerteZ(1)
    if stboQuer == 3 and stbobHkrit == True:
        stbfeBew = (stbZ_H[2] - stbZ_H[1]) / 2 / stboD
    else:
        stbfeBew = 0
    return stbfeBew
#------------------------------------------------------------------------------------------------------#    

def Sdehnkrit():
    #Critical strain states are required for the iterative determination of the equilibrium states
    #Related or reduced internal forces
    f_null = [0,1,0,0]
    dehn = [0,0,0,0]
    SRechenWerteZ(1)
    for it_dehn in range (1,stbkitmax+1):
        if abs(f_null[1]) > stbkepse5:
            Sitdehn(dehn, f_null, it_dehn)
            Sdehnepscs(dehn[1])
            n_eU = stbfKneU()
            m_eU = stbfKmeU()
            f_null[1] = n_eU + m_eU
        else:
            break
    stbodehnkrit[0] = dehn[1]                                  #print(Sdehnkrit)
#------------------------------------------------------------------------------------------------------#

def Smue0Riss():
    # Determination of the minimum reinforcement stbomue0Riss () for the crack moment
    EingangWerte = [0 for i in range(0,10)]
    EingangWerte[0] = stboNd
    EingangWerte[1] = stboMd
    EingangWerte[2] = stbofyk
    EingangWerte[3] = stboftk
    EingangWerte[4] = stbovormue0[0]
    EingangWerte[5] = stbovormue0[1]
    EingangWerte[6] = stbovormue0[2]
    EingangWerte[7] = stbomue0Druc[0]
    EingangWerte[8] = stbomue0Druc[1]
    EingangWerte[9] = stbomue0Druc[2]

    #Fracture state
    stbZiZ = 1

    #Exploitation of concrete
    if stboNorm == 0:
        stbZgamC[1] = 1 / stboalpha
    elif stboNorm > 0:
        stbZgamC[1] = stbogamC[1]
    
    #Use of reinforcement
    stbZgamS[1] = 1

    ''' 
    For stboNorm = 0 becomes
    '   f_yk = 0.8 * stbofyk
    '   f_tk = 0.8 * stbofyk
    'otherwise
    '   f_yk = 1.0 * stbofyk
    '   f_tk = 1.0 * stbofyk
    'set
    '''
    
    if stboNorm == 0:
        stbofyk = 0.8 * stbofyk
        stboftk = stbofyk
    elif stboNorm > 0:
        stbofyk = stbofyk
        stboftk = stbofyk
    
    # Determination of stbomue0Riss ()
    stbovormue0[0] = stbovormue0[0] * stboftk / EingangWerte[3]
    stbovormue0[1] = stbovormue0[1] * stboftk / EingangWerte[3]
    stbovormue0[2] = stbovormue0[2] * stboftk / EingangWerte[3]
    stbomue0Druc[0] = stbomue0Druc[0] * stboftk / EingangWerte[3]
    stbomue0Druc[1] = stbomue0Druc[1] * stboftk / EingangWerte[3]
    stbomue0Druc[2] = stbomue0Druc[2] * stboftk / EingangWerte[3] 
    stboNd = 0
    stbomue0Riss[0] = 0
    stbomue0Riss[1] = 0
    stbomue0Riss[2] = 0
    stboMd = math.pi * stbffctm() / stbofck / 6
    Serfmue0_K()
    stbZerfmue0[1] = 0
    stbZerfmue0[2] = 0   
    stbomue0Riss[0] = stbZerfmue0[0] * EingangWerte[3] / stboftk
    stbomue0Riss[1] = stbZerfmue0[1] * EingangWerte[3] / stboftk
    stbomue0Riss[2] = stbZerfmue0[2] * EingangWerte[3] / stboftk
    stboNd = EingangWerte[0]
    stboMd = EingangWerte[1]
    stbofyk = EingangWerte[2]
    stboftk = EingangWerte[3]
    stbovormue0[0] = EingangWerte[4]
    stbovormue0[1] = EingangWerte[5]
    stbovormue0[2] = EingangWerte[6]
    stbomue0Druc[0] = EingangWerte[7]
    stbomue0Druc[1] = EingangWerte[8]
    stbomue0Druc[2] = EingangWerte[9]                                  #print(Smue0Riss)
#------------------------------------------------------------------------------------------------------#

def Smue0Druc(delt_S, delt_K):
    # For stboNorm = 0
    # Strain limits for the reinforcement of the train side to increase the safety factor
    # otherwise
    # Minimum reinforcement content for pressure-loaded components to increase the partial safety factor for concrete determined
   
    NEdmin = 0
    mue0min = 0
    StrVek = delt_K.split(" ")
    StrVek[0] = float(StrVek[0])
    StrVek[1] = float(StrVek[1])

    if stboNorm == 0:
        stboepsSmin[1] = StrVek[0]/ 1000
        if StrVek[1] == StrVek[0]:
            stboepsSmin[2] = 0
        else:
            stboepsSmin[2] = (StrVek[0]+1)/ 1000
        stbomue0Druc[0] = 0
        stbomue0Druc[1] = 0
        stbomue0Druc[2] = 0

    elif stboNorm > 0:
        if stbobDruc[1]:
            if stboNorm == 2:
                NEdmin = StrVek[0]
                if StrVek[1] == StrVek[0]:
                    mue0min = 0.002 * stboftk / stbofck
                else:
                    mue0min = max((StrVek[0] + 1) / 100, 0) * stboftk / stbofck
                
                if stboQuer == 1 or stboQuer == 2:
                    stbomue0Druc[0] = max(NEdmin * abs(stboNd) * stbogamS[1] / math.pi * stboftk / stbofyk, mue0min)
                    stbomue0Druc[1] = 0
                    stbomue0Druc[2] = 0
            else:
                NEdmin = StrVek[0]
                if stboQuer == 1 or stboQuer == 2:
                    stbomue0Druc[0] = NEdmin * abs(stboNd) * stbogamS[1] / math.pi * stboftk / stbofyk
                    stbomue0Druc[1] = 0
                    stbomue0Druc[2] = 0
        else:     
            stbomue0Druc[0] = 0
            stbomue0Druc[1] = 0
            stbomue0Druc[2] = 0                                #print(Smue0Druc)
#------------------------------------------------------------------------------------------------------#

def Sitdehn(dehn, f_null, it_dehn):
    # Iteration procedure to determine the state of elongation at break

    # The fracture-elongation states are measured with the variable "dehn"
    # described. "dehn" can take values ​​from the interval [-1, +1]
    # The values ​​have the following meaning:
    '''
    # dehn      stbZepscd [1]   stbZepssd [1]   stbZepscd [2]

    # -1.0      -stboepscy      -stboepscy
    # -0.5      -stboepscu                      0.0
    # 0.0       -stboepscu      + stboeps_su
    # +1.0      + stboeps_su    + stboeps_su

    # '''
    # For intermediate values ​​of "dehn", the steel or concrete strain is interpolated linearly.
    # In the first two steps, the fractional internal forces
    # calculated for the outer interval limits of the variable dehn.
    # Then the interval size is continuously halved,
    # where the new interval by comparing the signs of the
    # Zero function f_Null is determined.
    if it_dehn == 1:
        f_null[1] = 0
        dehn[1] = -1
    elif it_dehn == 2:
        dehn[2] = dehn[1]
        f_null[2] = f_null[1]
        dehn[1] = 1
    elif it_dehn == 3:
        dehn[3] = dehn[1]
        f_null[3] = f_null[1]
        dehn[1] = (dehn[2] + dehn[3]) / 2
    else:
        if Nd1 < -stbkepse3:
            if f_null[1] * f_null[2] < 0:
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
            else:
                dehn[2] = dehn[1]
                f_null[2] = f_null[1]
            
        else:
            if f_null[1] * f_null[3] < 0:
                #print("at1")
                dehn[2] = dehn[1]
                f_null[2] = f_null[1]
            else:
                #print("at2")
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
        dehn[1] = (dehn[2] + dehn[3]) / 2                               #print(Sitdehn)
#------------------------------------------------------------------------------------------------------#

def Sdehnepscs(dehn):
    # Calculates the concrete and steel strain for a specific value of the variable "dehn"
    SRechenWerteZ(1)

    # Calculates the concrete strain stbZepscd (1) for a certain value of the variable "dehn".
    if dehn < -0.5:
        stbZeps_c[1] = -stboepscu + (stboepscu - stboepscy) * (-0.5 - dehn) / 0.5
    elif dehn < 0:
        stbZeps_c[1] = -stboepscu
    else:
        stbZeps_c[1] = -stboepscu + dehn * (stboepscu + stboepssu)
    
    # Calculates the steel strain stbZepssd (1) for a certain value of the variable "dehn".
    if dehn < -0.5:
        eps_gr = -stboepscu * stbZ_H[1] / stboD
        stbZeps_s[1] = eps_gr + (stboepscy + eps_gr) * (dehn + 0.5) / 0.5
    elif dehn < 0:
        eps_gr = -stboepscu * stbZ_H[1] / stboD
        stbZeps_s[1] = stboepssu + (stboepssu - eps_gr) * dehn / 0.5
    else:
        stbZeps_s[1] = stboepssu

    SRechenWerteZ(2)
    # Sepsc2s2 Calculates the strains stbZepscd (2) and stbZepssd (2)
    Sepsc2s2()
#------------------------------------------------------------------------------------------------------#

def Sepsc2s2():
    # Calculates the strains stbZepscd (2) and stbZepssd (2)
    SRechenWerteZ(1)
    
    stbZeps_c[2] = stbZeps_c[1] + (stbZeps_s[1] - stbZeps_c[1]) * stboD / (stboD - stbZ_H[1])
    stbZeps_s[2] = stbZeps_c[1] + (stbZeps_s[1] - stbZeps_c[1]) * stbZ_H[2] / (stboD - stbZ_H[1])
    
    SRechenWerteZ(2)
#------------------------------------------------------------------------------------------------------#


def stbffctm():
    # Tensile strength of the concrete
    if stboNorm == 0:
        stbffctm = 0.25 * max(stbofck, 35) ** (2 / 3)
    elif stboNorm > 0:
        if stbofck < 52.5:
            stbffctm = 0.3 * stbofck ** (2 / 3)
        else:
            stbffctm = 2.12 * math.log(1 + (stbofck + 8) / 10)
    return stbffctm
#------------------------------------------------------------------------------------------------------#    

def SRissB():
    # Design taking into account the crack width limitation.
    # statically required reinforcement stbZerfmue0 and associated safety factors stbZgamC (1), stbZgamS (1)
    # Information on minimum reinforcement is also taken into account.
    SgamC1()

    if stboRissP1 >= 1 or stboii >= 20:
        #Condition of use
        #The characteristic internal forces stbZRNk, stbZRMk and the associated elongation state stbZepsck, stbZepssk are determined.
        #Characteristic state
        #The characteristic internal forces stbZRNk, stbZRMk and the associated strain state stbZepsck, stbZepssk are determined.
        Gebrauch_K()

    if stboRissP1 >= 1 and stbfsig_s(stbZepssk[1]) > stboRissP1:
        # Determination of the required reinforcement content for a given steel stress / strain
        # Determination of the required reinforcement content for a given steel tension / steel elongation
        # If stboRissP1> = 1 # And stbfsig_s (stbZepssk (1))> stboRissP1 Then
        SigVor_K()

    if stboQuer == 1 and stbZmue0[0] > stbZerfmue0[0] + stbkepse5:
        # Elongation at break
        #The fracture internal forces stbZRNd, stbZRMd and the elongation state stbZepscd, stbZepssd are determined.
        #Elongation state
        #The fracture intersection sizes stbZRNd, stbZRMd and the strain state stbZepscd, stbZepssd are determined.
        Bruch_K()
#------------------------------------------------------------------------------------------------------#

def SgamC1():
    # The safety factors stbZgamC [1], stbZgamS [1] are determined iteratively
    # The corresponding statically required reinforcement is determined.
    # Auxiliary quantities
    fnullC = [0,0,0,0]

    stbZiZ = 1
    SRechenWerteZ(1)

    # Specified reinforcement
    if stbobminBew :
        vormue0_3 = max(stbovormue0[0], stbomue0Riss[0]) + max(stbovormue0[1], stbomue0Riss[1]) + max(stbovormue0[2], stbomue0Riss[2])
    else:
        vormue0_3 = stbovormue0[0] + stbovormue0[1] + stbovormue0[2]
    
    # If stbobDruc [1] = True and (stboNorm = 0 or stbomue0Druc [0] + stbomue0Druc [1] + stbomue0Druc [1] - vormue0_3> stbkepse7 or stbobHkrit = True) applies,
    # the value of stbZgamC [1] must be iterated from stbogamC [0] (increased security level),
    # to guarantee continuity of the solution and thus convergence
    if stbobDruc[1] and (stboNorm == 0 or stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2] - vormue0_3 > stbkepse7 or stbobHkrit) :
        stbZgamC[1] = stbogamC[0]
        stbZgamS[1] = stbogamS[0]
        bLastLoop = False
    else:
        stbZgamC[1] = stbogamC[1]
        stbZgamS[1] = stbogamS[1]
        bLastLoop = True
    
    bLoop = True
    it_gamC = 1
    # Determination of the required reinforcement contents stbZerfmue0 [0]
    if stboQuer == 1 :
        Serfmue0_K()
        erfmue_0 = stbZerfmue0[0]

    # Maximum from required reinforcement and reinforcement specifications
    if stboQuer == 1 :
        stbZmue0[0] = max(stbZerfmue0[0], stbovormue0[0])
        stbZmue0[1] = 0
        stbZmue0[2] = 0
        
    if bLastLoop :
        bLoop = False
    else:
        if stboNorm == 0 :
            if erfmue_0 < stbkepse7 :
                interpol = 0
            else:
                # The correct elongation at break must be known for the interpolation.
                if stboQuer == 1 and stbZmue0[0] > stbZerfmue0[0] + stbkepse5 :
                    Bruch_K()
                interpol = max((stbZepssd[1] - stboepsSmin[2]) / (stboepsSmin[1] - stboepsSmin[2]), 0)
            
        else:
            interpol = (stbZmue0[0] + stbZmue0[1] + stbZmue0[2]) / (stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2])
        
        fnullC[1] = stbZgamC[1] - stbogamC[0] + (stbogamC[0] - stbogamC[1]) * interpol
        if it_gamC == 1 :
            if interpol > stbkepse5 :
                fnullC[3] = fnullC[1]
                stbZgamC[3] = stbZgamC[1]
                stbZgamC[1] = stbogamC[1]
                stbZgamS[3] = stbZgamS[1]
                stbZgamS[1] = stbogamS[1]
            else:
                bLoop = False
            
        elif it_gamC == 2 :
            if interpol < 1 - stbkepse5 :
                fnullC[2] = fnullC[1]
                stbZgamC[2] = stbZgamC[1]
                stbZgamC[1] = (stbZgamC[2] + stbZgamC[3]) / 2
                stbZgamS[2] = stbZgamS[1]
                stbZgamS[1] = (stbZgamS[2] + stbZgamS[3]) / 2
            else:
                bLoop = False
            
        else:
            if fnullC[1] * fnullC[2] < 0 :
                stbZgamC[3] = stbZgamC[1]
                stbZgamS[3] = stbZgamS[1]
                fnullC[3] = fnullC[1]
            else:
                stbZgamC[2] = stbZgamC[1]
                stbZgamS[2] = stbZgamS[1]
                fnullC[2] = fnullC[1]
            
            stbZgamC[1] = (stbZgamC[2] + stbZgamC[3]) / 2
            stbZgamS[1] = (stbZgamS[2] + stbZgamS[3]) / 2
            if stbZgamC[3] - stbZgamC[2] < stbkepse3 :
                bLastLoop = True
                if stbobHkrit :
                    stbZgamC[1] = stbZgamC[3]
                    stbZgamS[1] = stbZgamS[3]
    while bLoop and it_gamC < stbkitmax:

        it_gamC = it_gamC + 1
        # Determination of the required reinforcement contents stbZerfmue0 [0]
        if stboQuer == 1 :
            Serfmue0_K()
            erfmue_0 = stbZerfmue0[0]
        
        if stboQuer == 1 :
            stbZmue0[0] = max(stbZerfmue0[0], stbovormue0[0])
            stbZmue0[1] = 0
            stbZmue0[2] = 0
            
        # Maximum from required reinforcement and reinforcement specifications
        if bLastLoop :
            bLoop = False
        else:
            if stboNorm == 0 :
                if erfmue_0 < stbkepse7 :
                    interpol = 0
                else:
                    # The correct elongation at break must be known for the interpolation.
                    if stboQuer == 1 and stbZmue0[0] > stbZerfmue0[0] + stbkepse5 :
                        Bruch_K()
                    interpol = max((stbZepssd[1] - stboepsSmin[2]) / (stboepsSmin[1] - stboepsSmin[2]), 0)
                
            else:
                interpol = (stbZmue0[0] + stbZmue0[1] + stbZmue0[2]) / (stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2])
            
            fnullC[1] = stbZgamC[1] - stbogamC[0] + (stbogamC[0] - stbogamC[1]) * interpol
            if it_gamC == 1 :
                if interpol > stbkepse5 :
                    fnullC[3] = fnullC[1]
                    stbZgamC[3] = stbZgamC[1]
                    stbZgamC[1] = stbogamC[1]
                    stbZgamS[3] = stbZgamS[1]
                    stbZgamS[1] = stbogamS[1]
                else:
                    bLoop = False
                
            elif it_gamC == 2 :
                if interpol < 1 - stbkepse5 :
                    fnullC[2] = fnullC[1]
                    stbZgamC[2] = stbZgamC[1]
                    stbZgamC[1] = (stbZgamC[2] + stbZgamC[3]) / 2
                    stbZgamS[2] = stbZgamS[1]
                    stbZgamS[1] = (stbZgamS[2] + stbZgamS[3]) / 2
                else:
                    bLoop = False
                
            else:
                if fnullC[1] * fnullC[2] < 0 :
                    stbZgamC[3] = stbZgamC[1]
                    stbZgamS[3] = stbZgamS[1]
                    fnullC[3] = fnullC[1]
                else:
                    stbZgamC[2] = stbZgamC[1]
                    stbZgamS[2] = stbZgamS[1]
                    fnullC[2] = fnullC[1]
                
                stbZgamC[1] = (stbZgamC[2] + stbZgamC[3]) / 2
                stbZgamS[1] = (stbZgamS[2] + stbZgamS[3]) / 2
                if stbZgamC[3] - stbZgamC[2] < stbkepse3 :
                    bLastLoop = True
                    if stbobHkrit :
                        stbZgamC[1] = stbZgamC[3]
                        stbZgamS[1] = stbZgamS[3]

    if it_gamC == stbkitmax :
        print(" Error in sgamc1")
        stbZbFehler = True
#------------------------------------------------------------------------------------------------------#

def Sitdehn0(dehn, f_null, it_dehn):
    # Iteration process for the unreinforced cross section
    if it_dehn == 1:
        f_null[1] = 0
        dehn[1] = -1
    elif it_dehn == 2:
        dehn[2] = dehn[1]
        f_null[2] = f_null[1]
        # Expansion state with the maximum possible load center for the unreinforced cross-section
        # stbZepscd (1) = very small negative value
        # stbZepssd (1) = stboepssu
        dehn[1] = stboepscu / (stboepscu + stboepssu) - stbkepse5
    elif it_dehn == 3:
        dehn[3] = dehn[1]
        f_null[3] = f_null[1]
        dehn[1] = (dehn[2] + dehn[3]) / 2
    else:
        if f_null[1] * f_null[2] < 0:
            dehn[3] = dehn[1]
            f_null[3] = f_null[1]
        else:
            dehn[2] = dehn[1]
            f_null[2] = f_null[1]
        
        dehn[1] = (dehn[2] + dehn[3]) / 2                                               #print(Sitdehn0)
#------------------------------------------------------------------------------------------------------#

def stbfalpha():
    # Determines the iteratively adjusted reduction value alpha
    if stboNorm == 0 or stboNorm == 1:
        stbfalpha = stboalpha
    elif stboNorm == 2 or stboNorm == 3:
        stbfalpha = stboalpha * stbogamC[1] / stbZgamC[1]
    return stbfalpha
#------------------------------------------------------------------------------------------------------#

def stbfsig_s(eps_s):
    # Calculates the steel stress depending on the steel strain "eps_s".
    if abs(eps_s) <= stboepssy:
        stbfsig_s = eps_s / stboepssy * stbofyk
    elif abs(eps_s) <= stboepssu:
        stbfsig_s = math.copysign(1,eps_s) * (stbofyk + (stboftk - stbofyk) * (abs(eps_s) - stboepssy) / (stboepssu - stboepssy))
    else:
        stbfsig_s = math.copysign(1,eps_s) * stboftk
    return stbfsig_s
#------------------------------------------------------------------------------------------------------#
#############################----Circular Cross-Sectional Specification----#############################
# Constants
i2n = 9
# Numerical integration according to the Simpson rule: number of support points = 2 * i2n + 1
# with i2n = 5 the convergence in function Snue0_K is extremely slow with an internal force combination for which dehn (1) = -0.5 applies
#------------------------------------------------------------------------------------------------------#
def Serfmue0_K():
    # Related or reduced internal forces
    dehn = [0,0,0,0]
    f_null = [0,1,0,0]

    # Iteration procedure to determine the statically required reinforcement stbZerfmue0[0]
    for it_dehn in range(1,stbkitmax):
        if (it_dehn==1 and (stboNd >= stbkepse5 or stboMd >= stbkepse5))or((it_dehn == 2 and (stboNd <= -stbkepse5 or stboMd >= stbkepse5)) or it_dehn == 3 or abs(f_null[1]) > stbkepse7):
            # The dehn (elongation) at break for the next step is determined
            if it_dehn == 3 :
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
                dehn[1] = stbodehnkrit[0]
            else:
                Sitdehn(dehn, f_null, it_dehn)
            # Concrete and steel expansions
            Sdehnepscs(dehn[1])

            # Related internal forces of the concrete pressure zone
            n_bU = stbfKnbU()
            m_bU = stbfKmbU()

            # Reduced internal forces of the reinforcement ring
            n_eU = stbfKneU()
            m_eU = stbfKmeU()

            if abs(n_eU + m_eU) > stbkepse5 :
                stbZerfmue0[0] = stbZgamS[1] * (stboNd - n_bU / stbZgamC[1] + stboMd - m_bU / stbZgamC[1]) / (n_eU + m_eU)
            else:
                stbZerfmue0[0] = 1 / stbkepse7
            
            # Function whose zero point is Desired
            f_null[1] = m_eU * (stboNd - n_bU / stbZgamC[1]) - n_eU * (stboMd - m_bU / stbZgamC[1])
            # The optimization function Sub Smue0opt converges more evenly.
            # (otherwise erratic change between symmetrical and non-symmetrical reinforcement with little change in the center)
        
        else:
            break

    if it_dehn == stbkitmax : 
        print('error = ',stbZbFehler)

    # Check minimum reinforcement and determine fracture internal forces
    if stbobminBew ==  True and stbZerfmue0[0] < stbomue0Riss[0] :
        stbZerfmue0[0] = stbomue0Riss[0]
        stbZmue0[0] = stbZerfmue0[0]
        Bruch_K()
    else:
        stbZRNd = n_bU / stbZgamC[1] + stbZerfmue0[0] * n_eU / stbZgamS[1]
        stbZRMd = m_bU / stbZgamC[1] + stbZerfmue0[0] * m_eU / stbZgamS[1]                              #print(Serfmue0_K)
#------------------------------------------------------------------------------------------------------#

def stbfphiAo():
    # Angle required for numerical integration calculations 
    # Split in conditions due to arc tan
    SRechenWerteZ(1)
    r1 = 1

    # Determined by using stbZeps_c[1] and stbZeps_c[2]
    if stbZeps_c[1] < 0 :
        if stbZeps_c[2] < 0 or abs(stbZeps_c[1] - stbZeps_c[2]) < stbkepse7 :
            stbfphiAo = math.pi
        else:
            x = 2 * r1 * stbZeps_c[1] / (stbZeps_c[1] - stbZeps_c[2])
            q = (r1 - x) / r1
            if math.sqrt(1 - q ** 2) == 0:
                stbfphiAo = math.pi / 2 - math.copysign(1,q)*(math.pi / 2)
            else:
                stbfphiAo = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
    
    else:
        stbfphiAo = 0

    return stbfphiAo
#------------------------------------------------------------------------------------------------------#

def stbfphiAu():
    # Angle required for numerical integration calculations.
    SRechenWerteZ(1)
    r1 = 1

    # Determined by using stbZeps_c[1] and stbZeps_c[2]
    if stbZeps_c[1] < -stboepscy :
        if abs(stbZeps_c[1] - stbZeps_c[2]) < stbkepse7 :
            stbfphiAu = math.pi
        else:
            xgr = 2 * r1 * (stbZeps_c[1] + stboepscy) / (stbZeps_c[1] - stbZeps_c[2])
            q = (r1 - xgr) / r1
            stbfphiAu = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
    
    else:
        stbfphiAu = 0

    return stbfphiAu
#------------------------------------------------------------------------------------------------------#

def stbfKnbU():
    # Integration limits, integration variable, delta_value
    # Related or reduced internal forces
    SRechenWerteZ(1)
    # Integration limits for the concrete cross section
    phiAo = stbfphiAo()
    phiAu = stbfphiAu()
    phiBo = phiAu
    phiBu = 0

    # Related internal forces of the concrete pressure zone
    if stbZeps_c[1] < 0 :
        k1 = -(stbZeps_c[1] + stbZeps_c[2]) / stboepscy / 2
        k2 = -(stbZeps_c[1] - stbZeps_c[2]) / stboepscy / 2
        if abs(phiAo - phiAu) < stbkepse7 :
            nAbU = 0
        elif abs(k2) < stbkepse7 :
            if k1 <= 0 :
                nAbU = 0
            elif k1 >= 1 :
                nAbU = -math.pi
            else:
                nAbU = -math.pi * (1 - (1 - k1) ** stbon2)

        else:
            nAbU = 0
            dphi = (phiAo - phiAu) / i2n
            phi = phiAu
            nAbU = nAbU + (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2
            phi = phiAo
            nAbU = nAbU + (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2
            phi = phiAu - dphi / 2
            for i in range(0 , i2n):
                phi = phi + dphi
                nAbU = nAbU + 4 * (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2
            phi = phiAu
            for i in range( 0, i2n-1):
                phi = phi + dphi
                nAbU = nAbU + 2 * (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2
            nAbU = nAbU * dphi / 3
        nBbU = -phiBo + math.sin(2 * phiBo) / 2 + phiBu - math.sin(2 * phiBu) / 2
    
    else:
        nAbU = 0
        nBbU = 0
    stbfKnbU = nAbU + nBbU
    
    return stbfKnbU
#------------------------------------------------------------------------------------------------------#

def stbfKmbU():
    # Integration limits, integration variable, delta_value
    # Related or reduced internal forces
    SRechenWerteZ(1)
    # Integration limits for the concrete cross section
    phiAo = stbfphiAo()
    phiAu = stbfphiAu()
    phiBo = phiAu
    phiBu = 0

    # Related internal forces of the concrete pressure zone
    if stbZeps_c[1] < 0 :
        k1 = -(stbZeps_c[1] + stbZeps_c[2]) / stboepscy / 2
        k2 = -(stbZeps_c[1] - stbZeps_c[2]) / stboepscy / 2
        if abs(phiAo - phiAu) < stbkepse7 :
            mAbU = 0
        elif abs(k2) < stbkepse7 :
            mAbU = 0
        else:
            mAbU = 0
            dphi = (phiAo - phiAu) / i2n
            phi = phiAu
            mAbU = mAbU + (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2 * math.cos(phi)
            phi = phiAo
            mAbU = mAbU + (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2 * math.cos(phi)
            phi = phiAu - dphi / 2
            for i in range(0 , i2n):
                phi = phi + dphi
                mAbU = mAbU + 4 * (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2 * math.cos(phi)
            phi = phiAu
            for i in range(0 , i2n-1):
                phi = phi + dphi
                mAbU = mAbU + 2 * (abs(k1 + k2 * math.cos(phi) - 1) ** stbon2 - 1) * math.sin(phi) ** 2 * math.cos(phi)
            mAbU = -mAbU * dphi / 3
        mBbU = 2 / 3 * (math.sin(phiBo) ** 3 - math.sin(phiBu) ** 3) #
    
    else:
        mAbU = 0
        mBbU = 0
    stbfKmbU = mAbU + mBbU
    
    return stbfKmbU
#------------------------------------------------------------------------------------------------------#

def stbfphiEu():
    # Angle required for numerical integration calculations
    SRechenWerteZ(1)
    R_e1 = 1

    # Determined by using stbZeps_c[1] and stbZeps_c[2]
    if stbZeps_s[1] > 0 + stbkepse7 :
        if stbZeps_s[2] < 0 - stbkepse7 :
            if stbZeps_s[2] < -stboepssy - stbkepse7 :
                xgr = 2 * R_e1 * (stbZeps_s[2] + stboepssy) / (stbZeps_s[2] - stbZeps_s[1])
                q = (R_e1 - xgr) / R_e1
                stbfphiEu = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
            else:
                stbfphiEu = 0

        else:
            stbfphiEu = 0
    else:
        if stbZeps_s[2] < -stboepssy - stbkepse7 :
            if stbZeps_s[1] > -stboepssy + stbkepse7 :
                xgr = 2 * R_e1 * (stbZeps_s[2] + stboepssy) / (stbZeps_s[2] - stbZeps_s[1])
                q = (R_e1 - xgr) / R_e1
                stbfphiEu = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
            else:
                stbfphiEu = math.pi

        else:
            stbfphiEu = 0
    
    return stbfphiEu
#------------------------------------------------------------------------------------------------------#

def stbfphiEo():
    # Angle required for numerical integration calculations
    SRechenWerteZ(1)
    R_e1 = 1

    # Determined by using stbZeps_c[1] and stbZeps_c[2]
    if stbZeps_s[1] > stbkepse7 :
        if stbZeps_s[2] < -stbkepse7 :
            if stbZeps_s[1] > stboepssy + stbkepse7 :
                xgr = 2 * R_e1 * (stbZeps_s[2] - stboepssy) / (stbZeps_s[2] - stbZeps_s[1])
                q = (R_e1 - xgr) / R_e1
                stbfphiEo = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
            else:
                stbfphiEo = math.pi

        else:
            if stbZeps_s[2] < stboepssy - stbkepse7 :
                if stbZeps_s[1] > stboepssy + stbkepse7 :
                    xgr = 2 * R_e1 * (stbZeps_s[2] - stboepssy) / (stbZeps_s[2] - stbZeps_s[1])
                    q = (R_e1 - xgr) / R_e1
                    stbfphiEo = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
                else:
                    stbfphiEo = math.pi
    
            else:
                stbfphiEo = 0

    else:
        stbfphiEo = math.pi
    
    return stbfphiEo
#------------------------------------------------------------------------------------------------------#

def stbfKneU():
    # Integration limits, integration variable, delta_value
    # Related or reduced internal forces
    SRechenWerteZ(1)

    # Integration limits for the reinforcement ring
    phiEu = stbfphiEu()
    phiEo = stbfphiEo()

    # Elastic Range
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / stboepssy / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / stboepssy / 2

    #Plastic Range
    phi_u = phiEu
    phi_o = phiEo
    n_EeU = (k1 * phi_o - k2 * math.sin(phi_o)) - (k1 * phi_u - k2 * math.sin(phi_u))
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / (stboepssu - stboepssy) / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / (stboepssu - stboepssy) / 2

    #Pressure Zone
    phi_u = 0
    phi_o = phiEu
    n_PaU = (((k1 + stboepssy / (stboepssu - stboepssy)) * phi_o - k2 * math.sin(phi_o)) * (stboftk / stbofyk - 1) - phi_o) - (((k1 + stboepssy / (stboepssu - stboepssy)) * phi_u - k2 * math.sin(phi_u)) * (stboftk / stbofyk - 1) - phi_u)
    
    #drawn zone
    phi_u = phiEo
    phi_o = math.pi
    n_PbU = (((k1 - stboepssy / (stboepssu - stboepssy)) * phi_o - k2 * math.sin(phi_o)) * (stboftk / stbofyk - 1) + phi_o)- (((k1 - stboepssy / (stboepssu - stboepssy)) * phi_u - k2 * math.sin(phi_u)) * (stboftk / stbofyk - 1) + phi_u)
    
    #reduced cutting size
    stbfKneU = (n_EeU + n_PaU + n_PbU) * stbofyk / stboftk
   
    return stbfKneU
#------------------------------------------------------------------------------------------------------#

def stbfKmeU():
    # Integration limits, integration variable, delta_value
    # Related or reduced internal forces
    SRechenWerteZ(1)

    # Integration limits for the reinforcement ring
    phiEu = stbfphiEu()
    phiEo = stbfphiEo()

    # Elastic Range
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / stboepssy / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / stboepssy / 2

    #Plastic Range
    phi_u = phiEu
    phi_o = phiEo
    m_EeU = (k1 * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2))- (k1 * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2))
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / (stboepssu - stboepssy) / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / (stboepssu - stboepssy) / 2
    
    #Pressure Zone
    phi_u = 0
    phi_o = phiEu
    m_PaU = (((k1 + stboepssy / (stboepssu - stboepssy)) * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2)) * (stboftk / stbofyk - 1) - math.sin(phi_o))- (((k1 + stboepssy / (stboepssu - stboepssy)) * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2)) * (stboftk / stbofyk - 1) - math.sin(phi_u))   
    
    #Drawn Zone
    phi_u = phiEo
    phi_o = math.pi
    m_PbU = (((k1 - stboepssy / (stboepssu - stboepssy)) * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2)) * (stboftk / stbofyk - 1) + math.sin(phi_o))- (((k1 - stboepssy / (stboepssu - stboepssy)) * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2)) * (stboftk / stbofyk - 1) + math.sin(phi_u))
    
    #reduced cutting size
    stbfKmeU = -stboRe / stboKR * (m_EeU + m_PaU + m_PbU) * stbofyk / stboftk
    
    return stbfKmeU
#------------------------------------------------------------------------------------------------------#

def Bruch_K():
    # Related or reduced internal forces
    dehn = [0,0,0,0]
    f_null = [0,0,0,0]

    stbZiZ = 1

    if abs(stboeNd) < stbkepse7 :
        if stboNd < 0 :
            itmin = 0
        else:
            itmin = 1
    else:
        itmin = 2

    # Strain state with maximum possible load center for the unreinforced cross-section
    # stbZepscd (1) = very small negative value
    # stbZepssd (1) = stboepssu
    dehnkrit = stboepscu / (stboepscu + stboepssu) - stbkepse5

    it_dehn = 1
    # Elongation at break for the next step is determined
    Sitdehn(dehn, f_null, it_dehn)
    # Concrete and steel expansions
    Sdehnepscs(dehn[1])
    n_bU = stbfKnbU()
    m_bU = stbfKmbU()
    n_i = n_bU / stbZgamC[1]
    m_i = m_bU / stbZgamC[1]
    n_eU = stbfKneU()
    m_eU = stbfKmeU()
    n_i = n_i + stbZmue0[0] * n_eU / stbZgamS[1]
    m_i = m_i + stbZmue0[0] * m_eU / stbZgamS[1]
    f_null[1] = stboMd * n_i - stboNd * m_i
    for it_dehn in range (0,stbkitmax):
        if (it_dehn <= itmin or it_dehn == 3 or abs(f_null[1]) > stbkepse5):
            # Elongation at break for the next step is determined
            if it_dehn == 3 :
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
                dehn[1] = dehnkrit
            else:
                # Elongation at break for the next step is determined
                Sitdehn(dehn, f_null, it_dehn)
            # Concrete and steel expansions
            Sdehnepscs(dehn[1])

            # Related internal forces of the concrete pressure zone
            n_bU = stbfKnbU()
            m_bU = stbfKmbU()
            n_i = n_bU / stbZgamC[1]
            m_i = m_bU / stbZgamC[1]

            # Reduced internal forces of the reinforcement ring
            n_eU = stbfKneU()
            m_eU = stbfKmeU()
            n_i = n_i + stbZmue0[0] * n_eU / stbZgamS[1]
            m_i = m_i + stbZmue0[0] * m_eU / stbZgamS[1]

            # Function whose zero point is Desired:
            f_null[1] = stboMd * n_i - stboNd * m_i

        else:
            break

    if it_dehn == stbkitmax : 
        print('error = ',stbZbFehler)

    #Fractional cut sizes
    stbZRNd = n_bU / stbZgamC[1] + stbZmue0[0] * n_eU / stbZgamS[1]
    stbZRMd = m_bU / stbZgamC[1] + stbZmue0[0] * m_eU / stbZgamS[1]                             #print(Bruch_K)
#------------------------------------------------------------------------------------------------------#

def Snue0_K():
    # Related or reduced internal forces
    dehn = [0,0,0,0]
    f_null = [0,1,0,0]

    # When checking the zero f_null (1) a high accuracy stbkepse7 is required, otherwise
    # The internal balance check does not work for small values ​​of stboNd and stboMd.
    for it_dehn in range(1,stbkitmax+1):
        if it_dehn == 2 or abs(f_null[1]) > stbkepse7: 
            # The strain at break for the next step is determined
            Sitdehn0(dehn, f_null, it_dehn)

            # Concrete and steel strains
            Sdehnepscs(dehn[1])

            # Related internal forces of the concrete pressure zone
            n_bU = stbfKnbU()
            m_bU = stbfKmbU()

            # Function whose zero point is Desired:
            f_null[1] = stboMd * n_bU - stboNd * m_bU

        else:
            break

    if it_dehn == stbkitmax :
        print('error = ',stbZbFehler)

    stbZnue0 = (abs(n_bU) + m_bU) / (abs(stboNd) + stboMd)

    if stbZnue0 >= stbogamC[0] - stbkepse5 and stbZbFehler == False :
        stbZgamC[1] = stbogamC[0]
        stbZgamS[1] = stbogamS[0]

        # Fractional cut sizes
        stbZRNd = n_bU / stbZgamC[1]
        stbZRMd = m_bU / stbZgamC[1]

        if stboii >= 20 :
            # Condition of use
            Gebrauch_K()

    else:
        stbZnue0 = -stbZnue0                              #print(Snue0_K)
#------------------------------------------------------------------------------------------------------#

def Gebrauch_K():
    # Condition of use (It is used to determine the Characteristic design related internal forces and values)
    eps1=[0,0,0,0]
    eps2 = [0,0,0,0]
    fnull_m = [0,0,0,0]
    fnull_n = [0,0,0,0]

    stbZiZ = 2

    # Determination of the uniform basic expansion eps0 for stboMk = 0 #
    if abs(stboNk) < stbkepse5 :
        eps0 = 0
    elif stboNk < 0 :

        it_n = 1
        eps2[1] = 0
        stbZepssk[1] = eps2[1]
        stbZepsck[1] = eps2[1]
        stbZepssk[2] = eps2[1]
        stbZepsck[2] = eps2[1]

        # Related cutting size
        stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()

        # Function whose zero point is Desired:
        fnull_n[1] = stboNk - stbZRNk
        while abs(fnull_n[1]) > stbkepse5 / 2 and it_n < stbkitmax:

            it_n = it_n + 1

            if it_n == 2 :
                fnull_n[2] = fnull_n[1]
                eps2[2] = eps2[1]
                eps2[1] = -stboepscy
            elif it_n == 3 :
                fnull_n[3] = fnull_n[1]
                eps2[3] = eps2[1]
                eps2[1] = -stboepscy / 2
            else:
                if fnull_n[1] * fnull_n[2] < 0 :
                    fnull_n[3] = fnull_n[1]
                    eps2[3] = eps2[1]
                else:
                    fnull_n[2] = fnull_n[1]
                    eps2[2] = eps2[1]
                
                eps2[1] = (eps2[2] + eps2[3]) / 2
            
            stbZepssk[1] = eps2[1]
            stbZepsck[1] = eps2[1]
            stbZepssk[2] = eps2[1]
            stbZepsck[2] = eps2[1]
            # Related cutting size
            stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()

            # Function whose zero point is Desired:
            fnull_n[1] = stboNk - stbZRNk

        if it_n == stbkitmax : 
            stbZbFehler = True

        eps0 = eps2[1]     

    else:
        Nkgr = math.pi * stbZmue0[0]   

        if stboNk <= math.pi * stbZmue0[0] * stbofyk / stboftk :
            eps0 = stboepssy * stboNk / (Nkgr * stbofyk / stboftk)   

        else:
            eps0 = stboepssy + (stboepssu - stboepssy) * (stboNk - math.pi * stbZmue0[0] * stbofyk / stboftk) / (Nkgr * (1 - stbofyk / stboftk))                     
        

    # The elongation in use must be determined numerically.
    # To do this, the edge strains are varied starting from eps0:
    # eps1 stands for stbZepssk (1)
    # eps2 stands for stbZepsck (1)
    # The moment equilibrium is checked in the outer DO loop (variation of eps1):
    # stboMk - stbfalpha () * m_bU - stbZmue0 (0) * m_eU = 0 #
    # The normal force balance is checked in the inner DO loop (variation of eps2):
    # stboNk - stbfalpha () * n_bU - stbZmue0 (0) * n_eU = 0 #
    it_m = 1
    it_ult = 1
    eps1[1] = eps0
    it_n = 1
    eps2[1] = eps0
    stbZepssk[1] = eps1[1]
    stbZepsck[1] = eps2[1]
    Sepsc2s2()
    stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()
    fnull_n[1] = stboNk - stbZRNk

    while abs(fnull_n[1]) > stbkepse5 and it_n < stbkitmax:
        it_n = it_n + 1
        if it_n == 2 :
            fnull_n[2] = fnull_n[1]
            eps2[2] = eps2[1]
            eps2[1] = -stboepscu
        elif it_n == 3 :
            if fnull_n[1] * fnull_n[2] < 0 :
                fnull_n[3] = fnull_n[1]
                eps2[3] = eps2[1]
                eps2[1] = (eps2[2] + eps2[3]) / 2
            else:
                break
            
        else:
            if fnull_n[1] * fnull_n[2] < 0 :
                fnull_n[3] = fnull_n[1]
                eps2[3] = eps2[1]
            else:
                fnull_n[2] = fnull_n[1]
                eps2[2] = eps2[1]
            
            eps2[1] = (eps2[2] + eps2[3]) / 2
        
        stbZepssk[1] = eps1[1]
        stbZepsck[1] = eps2[1]

        Sepsc2s2()

        stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()
        fnull_n[1] = stboNk - stbZRNk

    stbZRMk = stbfalpha() * stbfKmbU() + stbZmue0[0] * stbfKmeU()
    fnull_m[1] = stboMk - stbZRMk

    # If no solution was found for the balance of normal force in the first iteration step,
    # the first iteration step is repeated with a changed start value.
    while abs(fnull_m[1]) > stbkepse5 and it_ult < stbkitmax:
        it_m = it_m + 1
        it_ult = it_ult + 1
        if it_m == 2 :
            
            # If no solution was found for the balance of normal force in the second iteration step,
            # the second iteration step is repeated with a changed start value.
            if abs(fnull_n[1]) > stbkepse5 :
                it_m = 1
                if fnull_n[1] * stboNk < 0 :
                    eps1[1] = eps1[1] / 2
                else:
                    eps1[1] = 2 * eps1[1]
                    if stboNk < 0 :
                        eps1[1] = max(eps1[1], -stboepscu)
                    else:
                        eps1[1] = min(eps1[1], stboepssu)
                    
                
            else:
                fnull_m[2] = fnull_m[1]
                eps1[2] = eps1[1]
                eps1[1] = stboepssu
            
        elif it_m == 3 :
            if abs(fnull_n[1]) > stbkepse5 :
                it_m = 2
                eps1[1] = eps1[1] / 2
            else:
                if fnull_m[1] * fnull_m[2] < 0 :
                    fnull_m[3] = fnull_m[1]
                    eps1[3] = eps1[1]
                else:
                    eps1[3] = stboepssu
                    eps1[2] = eps1[1]
                
                eps1[1] = (eps1[2] + eps1[3]) / 2
            
        # It is checked whether the solution is included with eps1 (2) and eps1 (1).
        # This is the case if fnull_m (1) * fnull_m (2) <0 # applies.
        # If this is not the case, the solution between eps1 (1) and stboepssu is Desired.
        else:
            if fnull_m[1] * fnull_m[2] < 0 :
                fnull_m[3] = fnull_m[1]
                eps1[3] = eps1[1]
            else:
                fnull_m[2] = fnull_m[1]
                eps1[2] = eps1[1]
            
            eps1[1] = (eps1[2] + eps1[3]) / 2
        
        it_n = 1

        eps2[1] = eps0

        stbZepssk[1] = eps1[1]
        stbZepsck[1] = eps2[1]

        Sepsc2s2()

        # Related internal forces
        stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()
        fnull_n[1] = stboNk - stbZRNk

        while abs(fnull_n[1]) > stbkepse5 and it_n < stbkitmax:
            it_n = it_n + 1
            if it_n == 2 :
                fnull_n[2] = fnull_n[1]
                eps2[2] = eps2[1]
                eps2[1] = -stboepscu
            elif it_n == 3 :
                if fnull_n[1] * fnull_n[2] < 0 :
                    fnull_n[3] = fnull_n[1]
                    eps2[3] = eps2[1]
                    eps2[1] = (eps2[2] + eps2[3]) / 2
                else:
                    break
                
            else:
                if fnull_n[1] * fnull_n[2] < 0 :
                    fnull_n[3] = fnull_n[1]
                    eps2[3] = eps2[1]
                else:
                    fnull_n[2] = fnull_n[1]
                    eps2[2] = eps2[1]
                
                eps2[1] = (eps2[2] + eps2[3]) / 2
            
            stbZepssk[1] = eps1[1]
            stbZepsck[1] = eps2[1]

            Sepsc2s2()

            # Related internal forces
            stbZRNk = stbfalpha() * stbfKnbU() + stbZmue0[0] * stbfKneU()
            fnull_n[1] = stboNk - stbZRNk

        stbZRMk = stbfalpha() * stbfKmbU() + stbZmue0[0] * stbfKmeU()
        # Function whose zero point is Desired:
        fnull_m[1] = stboMk - stbZRMk

    if it_ult == stbkitmax : 
        stbZbFehler = True                                                         #print(Gebrauch_K)
#------------------------------------------------------------------------------------------------------#\

def SigVor_K():
    # stbZepssk (1] is fixed via the steel tension stboRissP1
    # The required reinforcement content for maintaining the steel tension stboRissP1 is determined numerically.
    # StbZmue0[0] is used as the starting value, the correct reinforcement content is larger.
    # eps2 stands for stbZepsck [1]
    # Only used when there is min reinforcement required
    faktor=[0,0,0,0]
    eps2 = [0,0,0,0]
    fnull_m = [0,1,0,0]
    fnull_n = [0,1,0,0]  
    stbZiZ = 2    

    fakmue01_2 = stbfsig_s(stbZepssk[1]) / stboRissP1

    # Specification of steel expansion
    if stboRissP1 <= stbofyk + 0.1 :
        stbZepssk[1] = stboRissP1 / (stbofyk / stboepssy)
    else:
        stbZepssk[1] = stboepssy + (stboepssu - stboepssy) * (stboRissP1 - stbofyk) / (stboftk - stbofyk)
    
    # Initial value for the iterative determination of the concrete expansion
    # In the middle of a pulling force
    if stboNk < stbkepse5 :
        eps0 = 0
    else:
        eps0 = stbZepssk[1]
    
    # There is no concrete compressive force for centric or approximately centric tensile force.
    if stboNk > stbkepse5 and stboeNk < stbkepse7 :

        # Central traction
        stbZepsck[1] = stbZepssk[1]
        Sepsc2s2()
        faktor[1] = stboNk / math.pi * stboftk / stboRissP1 / stbZmue0[0]
        stbZRNk = faktor[1] * stbZmue0[0] * stbfKneU()
        stbZRMk = 0
        stbZmue0[0] = faktor[1] * stbZmue0[0]

    elif stboNk > stbkepse5 and stboeNk < stboRe / stboKR :

        # Traction with a small center
        # In the first iteration procedure, the state of expansion is calculated without the participation of the concrete.
        it_m = 1
        eps2[1] = eps0
        stbZepsck[1] = eps2[1]

        Sepsc2s2()

        fnull_m[1] = stboeNk - stbfKmeU() / stbfKneU()
        while abs(fnull_m[1]) > stbkepse5 and it_m < stbkitmax:
            it_m = it_m + 1
            if it_m == 2 :
                fnull_m[2] = fnull_m[1]
                eps2[2] = eps2[1]
                eps2[1] = -stboepscu
            elif it_m == 3 :
                fnull_m[3] = fnull_m[1]
                eps2[3] = eps2[1]
                eps2[1] = (eps2[2] + eps2[3]) / 2
            else:
                if fnull_m[1] * fnull_m[2] < 0 :
                    fnull_m[3] = fnull_m[1]
                    eps2[3] = eps2[1]
                else:
                    fnull_m[2] = fnull_m[1]
                    eps2[2] = eps2[1]               
                eps2[1] = (eps2[2] + eps2[3]) / 2

            stbZepsck[1] = eps2[1]
            Sepsc2s2()

            fnull_m[1] = stboeNk - stbfKmeU() / stbfKneU()
        
        #It is checked whether a concrete compressive force occurs or whether no solution was found for the specified steel tension
        if stbZepsck[1] < 0 or it_m == stbkitmax :
            pass
        #Goes to Moment Iteration

        else:
            it_n = 1
            it_ult = 1
            faktor[1] = 1

            stbZRNk = faktor[1] * stbZmue0[0] * stbfKneU()

            fnull_n[1] = stboNk - stbZRNk

            while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
                it_n = it_n + 1
                it_ult = it_ult + 1          
                if it_n == 2 :
                    fnull_n[2] = fnull_n[1]
                    faktor[2] = faktor[1]
                    faktor[1] = fakmue01_2
                elif it_n == 3 :
                    if fnull_n[1] * fnull_n[2] > 0 :
                        it_n = 2
                        fnull_n[2] = fnull_n[1]
                        faktor[2] = faktor[1]
                        faktor[1] = 2 * faktor[1]
                    else:
                        fnull_n[3] = fnull_n[1]
                        faktor[3] = faktor[1]
                        faktor[1] = (faktor[2] + faktor[3]) / 2
                    
                else:
                    if fnull_n[1] * fnull_n[2] < 0 :
                        fnull_n[3] = fnull_n[1]
                        faktor[3] = faktor[1]
                    else:
                        fnull_n[2] = fnull_n[1]
                        faktor[2] = faktor[1]
                    
                    faktor[1] = (faktor[2] + faktor[3]) / 2
                stbZRNk = faktor[1] * stbZmue0[0] * stbfKneU()
                fnull_n[1] = stboNk - stbZRNk
            stbZRMk = faktor[1] * stbZmue0[0] * stbfKmeU()

    #MomentIteration
    # The normal force balance is checked in the outer DO loop (variation of factor):
    # stboNk - stbfalpha () * n_bU - factor (1) * stbZmue0 (0) * n_eU = 0 #
    # The moment equilibrium is checked in the inner DO loop (variation of eps2):
    # stboMk - stbfalpha () * m_bU - factor (1) * stbZmue0 (0) * m_eU = 0 #
    # In order for this algorithm to converge safely, iterations must be iterated in the inner loop with increased accuracy.
    it_n = 1
    it_ult = 1

    #Initial value for the iterative determination of the reinforcement content
    faktor[1] = 1 
    it_m = 1
    eps2[1] = eps0
    stbZepsck[1] = eps2[1]

    Sepsc2s2()
    stbZRMk = stbfalpha() * stbfKmbU() + faktor[1] * stbZmue0[0] * stbfKmeU()

    fnull_m[1] = stboMk - stbZRMk

    while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax :
        it_m = it_m + 1
        if it_m == 2 :
            fnull_m[2] = fnull_m[1]
            eps2[2] = eps2[1]
            eps2[1] = -stboepscu
        elif it_m == 3 :
            fnull_m[3] = fnull_m[1]
            eps2[3] = eps2[1]
            eps2[1] = (eps2[2] + eps2[3]) / 2
        else:
            if fnull_m[1] * fnull_m[2] < 0 :
                fnull_m[3] = fnull_m[1]
                eps2[3] = eps2[1]
            else:
                fnull_m[2] = fnull_m[1]
                eps2[2] = eps2[1]
            eps2[1] = (eps2[2] + eps2[3]) / 2
        stbZepsck[1] = eps2[1]
        Sepsc2s2()
        stbZRMk = stbfalpha() * stbfKmbU() + faktor[1] * stbZmue0[0] * stbfKmeU()
        fnull_m[1] = stboMk - stbZRMk

    stbZRNk = stbfalpha() * stbfKnbU() + faktor[1] * stbZmue0[0] * stbfKneU()

    fnull_n[1] = stboNk - stbZRNk

    while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
        it_n = it_n + 1
        it_ult = it_ult + 1             
        if it_n == 2 :
            fnull_n[2] = fnull_n[1]
            faktor[2] = faktor[1]
            faktor[1] = fakmue01_2
        elif it_n == 3 :
            if fnull_n[1] * fnull_n[2] > 0 :
                it_n = 2
                fnull_n[2] = fnull_n[1]
                faktor[2] = faktor[1]
                faktor[1] = 2 * faktor[1]
            else:
                fnull_n[3] = fnull_n[1]
                faktor[3] = faktor[1]
                faktor[1] = (faktor[2] + faktor[3]) / 2
            
        else:
            if fnull_n[1] * fnull_n[2] < 0 :
                fnull_n[3] = fnull_n[1]
                faktor[3] = faktor[1]
            else:
                fnull_n[2] = fnull_n[1]
                faktor[2] = faktor[1]
            
            faktor[1] = (faktor[2] + faktor[3]) / 2
        it_m = 1
        eps2[1] = eps0
        stbZepsck[1] = eps2[1]

        Sepsc2s2()
        stbZRMk = stbfalpha() * stbfKmbU() + faktor[1] * stbZmue0[0] * stbfKmeU()

        fnull_m[1] = stboMk - stbZRMk

        while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax :
            it_m = it_m + 1
            if it_m == 2 :
                fnull_m[2] = fnull_m[1]
                eps2[2] = eps2[1]
                eps2[1] = -stboepscu
            elif it_m == 3 :
                fnull_m[3] = fnull_m[1]
                eps2[3] = eps2[1]
                eps2[1] = (eps2[2] + eps2[3]) / 2
            else:
                if fnull_m[1] * fnull_m[2] < 0 :
                    fnull_m[3] = fnull_m[1]
                    eps2[3] = eps2[1]
                else:
                    fnull_m[2] = fnull_m[1]
                    eps2[2] = eps2[1]
                eps2[1] = (eps2[2] + eps2[3]) / 2
            stbZepsck[1] = eps2[1]
            Sepsc2s2()
            stbZRMk = stbfalpha() * stbfKmbU() + faktor[1] * stbZmue0[0] * stbfKmeU()
            fnull_m[1] = stboMk - stbZRMk

        stbZRNk = stbfalpha() * stbfKnbU() + faktor[1] * stbZmue0[0] * stbfKneU()

        fnull_n[1] = stboNk - stbZRNk
        
    if it_ult == stbkitmax :
        stbZbFehler = True     

    else:
        stbZmue0[0] = faktor[1] * stbZmue0[0]                             #print(SigVor_K,faktor[1])
#------------------------------------------------------------------------------------------------------#        

def stbfphix():
    # Simple Mathematical function used in SKnmeU(n_eU1, m_eU1, n_eU2, m_eU2)
    SRechenWerteZ(1)
    R_e1 = 1
    if stbZeps_s[1] > stbkepse7 :
        if stbZeps_s[2] < -stbkepse7 :
            xgr = 2 * R_e1 * stbZeps_s[2] / (stbZeps_s[2] - stbZeps_s[1])
            q = (R_e1 - xgr) / R_e1
            if math.sqrt(1 - q ** 2) == 0:
                stbfphix = math.pi / 2 - math.copysign(1,q)*(math.pi / 2)
            else:
                stbfphix = math.pi / 2 - math.atan(q / math.sqrt(1 - q ** 2))
        else:
            stbfphix = 0
    else:
        stbfphix = math.pi
    return stbfphix
#------------------------------------------------------------------------------------------------------#   

def SKnmeU(n_eU1, m_eU1, n_eU2, m_eU2):
    # Limits of integration
    SRechenWerteZ(1)

    # Integration limits for the reinforcement ring
    phiEu = stbfphiEu()
    phiEo = stbfphiEo()
    phix = stbfphix()

    #Elastic Zone
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / stboepssy / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / stboepssy / 2

    #Drawn Zone
    phi_u = phix
    phi_o = phiEo
    n_eU1 = (k1 * phi_o - k2 * math.sin(phi_o))- (k1 * phi_u - k2 * math.sin(phi_u))
    m_eU1 = (k1 * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2))- (k1 * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2))

    #Pressure Zone
    phi_u = phiEu
    phi_o = phix
    n_eU2 = (k1 * phi_o - k2 * math.sin(phi_o))- (k1 * phi_u - k2 * math.sin(phi_u))
    m_eU2 = (k1 * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2))- (k1 * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2))
    
    #Plastic Zone
    k1 = (stbZeps_s[1] + stbZeps_s[2]) / (stboepssu - stboepssy) / 2
    k2 = (stbZeps_s[1] - stbZeps_s[2]) / (stboepssu - stboepssy) / 2

    #Drawn Zone
    phi_u = phiEo
    phi_o = math.pi
    n_eU1 = n_eU1 + (((k1 - stboepssy / (stboepssu - stboepssy)) * phi_o - k2 * math.sin(phi_o)) * (stboftk / stbofyk - 1) + phi_o) - (((k1 - stboepssy / (stboepssu - stboepssy)) * phi_u - k2 * math.sin(phi_u)) * (stboftk / stbofyk - 1) + phi_u)
    m_eU1 = m_eU1 + (((k1 - stboepssy / (stboepssu - stboepssy)) * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2)) * (stboftk / stbofyk - 1) + math.sin(phi_o)) - (((k1 - stboepssy / (stboepssu - stboepssy)) * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2)) * (stboftk / stbofyk - 1) + math.sin(phi_u))
    
    #Pressure Zone
    phi_u = 0
    phi_o = phiEu
    n_eU2 = n_eU2 + (((k1 + stboepssy / (stboepssu - stboepssy)) * phi_o - k2 * math.sin(phi_o)) * (stboftk / stbofyk - 1) - phi_o)  - (((k1 + stboepssy / (stboepssu - stboepssy)) * phi_u - k2 * math.sin(phi_u)) * (stboftk / stbofyk - 1) - phi_u)
    m_eU2 = m_eU2 + (((k1 + stboepssy / (stboepssu - stboepssy)) * math.sin(phi_o) - k2 / 2 * (phi_o + math.sin(2 * phi_o) / 2)) * (stboftk / stbofyk - 1) - math.sin(phi_o))  - (((k1 + stboepssy / (stboepssu - stboepssy)) * math.sin(phi_u) - k2 / 2 * (phi_u + math.sin(2 * phi_u) / 2)) * (stboftk / stbofyk - 1) - math.sin(phi_u))
    
    # reduced internal forces
    n_eU1 = n_eU1 * stbofyk / stboftk
    m_eU1 = -stboRe / stboKR * m_eU1 * stbofyk / stboftk
    n_eU2 = n_eU2 * stbofyk / stboftk
    m_eU2 = -stboRe / stboKR * m_eU2 * stbofyk / stboftk

    return n_eU1, m_eU1, n_eU2, m_eU2
#------------------------------------------------------------------------------------------------------#   

def BruchC1S1():
    # The state of fracture (strains), the associated safety factors stbZgamC (1), stbZgamS (1)
    # and the internal forces stbZNucs () and the associated lever arms stbZzi () are determined.
    # For stboNorm = 0 an iterative determination for stbZgamC (1), stbZgamS (1) is required.
    # Related or reduced internal forces
    Nui = [0,0,0]
    Mui = [0,0,0]

    # Determination of the safety factors for the fracture state
    if stboNorm == 0:
        SgamC1()

    elif stboNorm > 0:
        if stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2] > stbZmue0[0] + stbZmue0[1] + stbZmue0[2] + stbkepse7:
            stbZgamC[1] = stbogamC[1]+(stbogamC[0] - stbogamC[1]) * (1 - (stbZmue0[0] + stbZmue0[1] + stbZmue0[2]) / (stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2]))
        else:
            stbZgamC[1] = stbogamC[1]
        stbZgamS[1] = stbogamS[1]
    
    # Determination of the fracture state (strains)
    Bruch_K()

    # Internal forces and lever arms
    Nui[0] = stbfKnbU()
    Mui[0] = stbfKmbU()
    stbZNucs[0] = Nui[0] / stbZgamC[1]
    if Nui[0] < -stbkepse7:
        stbZzi[0] = Mui[0] / Nui[0] * stboKR
    else:
        stbZzi[0] = 0
    
    if stbZmue0[0] > stbkepse7:
        Nui[1], Mui[1], Nui[2], Mui[2] = SKnmeU(Nui[1], Mui[1], Nui[2], Mui[2])
        if Nui[1] > stbkepse7:
            stbZNucs[1] = stbZmue0[0] * Nui[1] / stbZgamS[1]
            stbZzi[1] = Mui[1] / Nui[1] * stboKR
        else:
            stbZNucs[1] = 0
            stbZzi[1] = 0
        
        if Nui[2] < -stbkepse7:
            stbZNucs[2] = stbZmue0[0] * Nui[2] / stbZgamS[1]
            stbZzi[2] = Mui[2] / Nui[2] * stboKR
        else:
            stbZNucs[2] = 0
            stbZzi[2] = 0
        
    else:
        stbZNucs[1] = 0
        stbZNucs[2] = 0
        stbZzi[1] = 0
        stbZzi[2] = 0

    if stbZNucs[0] < -stbkepse7 and stbZNucs[1] > stbkepse7:
        zD = (stbZzi[0] * stbZNucs[0] + stbZzi[2] * stbZNucs[2]) / (stbZNucs[0] + stbZNucs[2])
        stbZNucs[3] = min(abs(stbZNucs[0] + stbZNucs[2]), stbZNucs[1])
        stbZzi[3] = stbZzi[1] - zD
    else:
        stbZNucs[3] = 0
        stbZzi[3] = 0                                  #print(BruchC1S1)
#------------------------------------------------------------------------------------------------------#  

def stbfzi():
    # Lever arm of internal forces
    mue1 = 0
    mue2 = 0

    SRechenWerteZ(1)

    mue1 = stbZmue0[0] / 2
    mue2 = stbZmue0[0] / 2
    
    # The following modifications for zi are taken from DIN 1045-1: 2008 paragraph 10.3.4 (2).
    # They are necessary to avoid singularities at a small moment.
    stbfzi = stbZzi[3]

    if stbZepscd[1] > -stbkepse5 and mue1 > stbkepse7 and mue2 > stbkepse7:
        # fully drawn cross section
        stbfzi = stboHQ - stbZ_H[1] - stbZ_H[2]
    else:
        stbfzi = max(stbfzi, 0.9 * (stboHQ - stbZ_H[1]))
        stbfzi = min(stbfzi, max(stboHQ - 2 * stbZ_H[2], stboHQ - stbZ_H[2] - 0.03))
    return stbfzi
#------------------------------------------------------------------------------------------------------#  

def QuerBemessN0():
    # Shear design for stboNorm = 0
    # The following values ​​are determined:
    # stbZtau0
    # stbZerfas

    # Design value of tensile strength
    f_ctd = stbffctm() / stbZgamC[1] 

    # Basic value of the shear stress                                                        
    Nd1 = stboNd * stboKR ** 2 * stbofck
    Qd = stboQd * stboKR ** 2 * stbofck
    vormue1 = stbZmue0[0] / 2 + stbZmue0[1]
    Rctd = f_ctd * math.pi * stboKR ** 2
    
    if vormue1 < stbkepse7:
        stbZtau0 = Qd / stbfAcc()                                      
        sig_x = Nd1 / stbfAcc()                                          
        stbZtau0 = sig_x / 2 + math.sqrt((sig_x / 2) ** 2 + stbZtau0 ** 2)   

        if stbZtau0 <= stbotau012:
            stbZerfas = 0

        else:
            stbZerfas = -1
        
    else:
        if stbZepscd[2] < stbkepse5:
            # completely suppressed cross section
            stbZtau0 = Qd / stbfAcc()
            sig_x = Nd1 / stbfAcc()
            stbZtau0 = sig_x / 2 + math.sqrt((sig_x / 2) ** 2 + stbZtau0 ** 2)

        else:
            stbZtau0 = Qd / stboBQ / stbfzi()
        
        # required shear reinforcement
        if stbZtau0 <= stbotau012:
            if Nd1 > Rctd:
                # full thrust coverage
                tau = stbZtau0

            else:
                # reduced thrust cover
                tau = 0.4 * stbZtau0
                if Nd1 > 0:
                    tau = tau + (stbZtau0 - tau) * Nd1 / Rctd
                 
        elif stbZtau0 <= stbotau02:
            if Nd1 > Rctd:
                # full thrust coverage
                tau = stbZtau0

            else:
                # reduced thrust cover
                tau = max(stbZtau0 ** 2 / stbotau02, 0.4 * stbZtau0)
                if Nd1 > 0:
                    tau = tau + (stbZtau0 - tau) * Nd1 / Rctd
                
            
        elif stbZtau0 <= stbotau03:
            if stbZepscd[1] > -stbkepse5:
                #impermissibly high shear load
                tau = -1 

            else:
                # full thrust coverage
                tau = stbZtau0
            
        else:
            #impermissibly high shear load
            tau = -1
        
        if tau <= -0.5:
            stbZerfas = -1
        else:
            stbZerfas = tau * stboBQ / (stbofyk / stbogamS[1]) * 10000                      #print(QuerBemessN0)
#------------------------------------------------------------------------------------------------------#  

def QuerBemessN123():
    # Shear design for stboNorm> 0
    # The following values ​​are determined for unreinforced cross sections:
    # stbZerfas
    # stbZminas
    # stbZVRdc
    # stbZtaucp
    # stbZfcvd
    # The following values ​​are determined for reinforced cross-sections:
    # stbZerfas
    # stbZminas
    # stbZVRdc
    # stbZVRdmax
    # stbZcottheta
    # [1] = DIN 1045: 2008
    # [2] = EN 1992-1-1: 2004 (Eurocode 2)
    # [3] = DIN EN 1992-1-1: 2004 + AC: 2010 + NA: 2011, cited here from the EUROCODE 2 standards manual for Germany, commented version, 1st edition 2012
    # The variable names are largely based on the formula symbols in [3]
    zi = 0

    SRechenWerteZ(1)

    # Design value of compressive strength
    f_cd = stbofck / stbZgamC[1]   

    #Design value of tensile strength                                                             
    f_ctd = stbffctm() / stbZgamC[1]  

    # Design value of compressive Reinforcement yield strength                                                         
    f_yd = stbofyk / stbogamS[1]   

    Nd1 = stboNd * stboKR ** 2 * stbofck
    Qd = stboQd * stboKR ** 2 * stbofck
    vormue1 = stbZmue0[0] / 2 + stbZmue0[1]
    Rctd = f_ctd * math.pi * stboKR ** 2

    if vormue1 < stbkepse7:
        # medium compressive stress: sigcp is positive for compressive stresses and negative for tension
        if stboNorm == 1:
            sigcp = -Nd1 / stboBQ / stboHQ     # [1]                                                 
        elif stboNorm == 2 or stboNorm == 3:   # [2],[3]
            sigcp = -Nd1 / stbfAcc()                                                             

        # Determine stbZtaucp, stbZfcvd, stbZVRdc                                                                       
        if stboNorm == 1:
            stbZtaucp = 1.5 * Qd / stboBQ / stboHQ      #[1]                                       
            stbZfcvd = math.sqrt(f_ctd ** 2 + sigcp * f_ctd)   

        elif stboNorm == 2 or stboNorm == 3:
            stbZtaucp = 1.5 * Qd / stbfAcc()                                                   
            sig_clim = f_cd - 2 * math.sqrt(f_ctd * (f_ctd + f_cd))                #[2], [3]              
            if sigcp <= sig_clim:                                                         
                stbZfcvd = math.sqrt(f_ctd ** 2 + sigcp * f_ctd)
            else:
                stbZfcvd = math.sqrt(max(f_ctd ** 2 + sigcp * f_ctd - (sigcp - sig_clim) ** 2 / 4, 0))
            
            stbZVRdc = stbfAcc() * stbZfcvd / 1.5

        # Minimum shear reinforcement [cm ^ 2 / m]
        stbZminas = 0

        # required shear reinforcement
        if Qd <= stbZVRdc + stbkepse5:
            stbZerfas = 0
        else:
            stbZerfas = -1

    else:
        # Lever arm of internal forces
        zi = stbfzi()

        # static usable height [1],[2] and [3]
        DQ = stboHQ - stbZ_H[1]    

        #Average compressive stress in relation to the total cross-section: sigcp is positive for compressive stresses and negative for tension
        # [1]                                      
        sigcp = -Nd1 / stboBQ / stboHQ   

        # Determine stbZVRdc [1]                                        
        vorAs1 = 10000 * vormue1 * stboBQ * stboHQ * stbofck / stboftk
        rho1 = min(vorAs1 / 10000 / stboBQ / DQ, 0.02)
        kappa = min(1 + math.sqrt(0.2 / DQ), 2)

        if stboNorm == 1 or stboNorm == 3:
            k1 = 0.12
            k2 = 0.15
            if DQ <= 0.6:
                kappa1 = 0.0525
            elif DQ > 0.8:
                kappa1 = 0.0375
            else:
                kappa1 = 0.0525 - 0.015 * (DQ - 0.6) / 0.2
            
            nuemin = kappa1 / (stbfalpha() * stbZgamC[1]) * math.sqrt(kappa ** 3 * stbofck)
        elif stboNorm == 2:
            k1 = 0.15
            k2 = 0.18
            kappa1 = 0.035
            nuemin = kappa1 * math.sqrt(kappa ** 3 * stbofck)
        
        if stboNorm == 1:
            stbZVRdc = (k2 / (stbfalpha() * stbZgamC[1]) * kappa * (100 * rho1 * stbofck) ** (1 / 3) + k1 * sigcp) * stboBQ * DQ  
            VRdctmin = (nuemin + k1 * sigcp) * stboBQ * DQ
        elif stboNorm == 2 or stboNorm == 3:
            stbZVRdc = (k2 / (stbfalpha() * stbZgamC[1]) * kappa * (100 * rho1 * stbofck) ** (1 / 3) + k1 * min(sigcp, 0.2 * f_cd)) * stboBQ * DQ  
            VRdctmin = (nuemin + k1 * min(sigcp, 0.2 * f_cd)) * stboBQ * DQ                                                                       
        
        stbZVRdc = max(max(stbZVRdc, VRdctmin), 0)

        # Determine stbZcottheta and stbZVRdmax
        if stboNorm == 1 or stboNorm == 3:
            nue1 = 0.75                              #[1]  and [3]                                        
        elif stboNorm == 2:
            nue1 = 0.6                               #[2]                                  
        
        if Qd <= stbZVRdc + stbkepse5:
            stbZcottheta = 1
            stbZVRdmax = stboBQ * zi * nue1 * f_cd / (stbZcottheta + 1 / stbZcottheta)
        else:
            if stboNorm == 1 or stboNorm == 3:
                if Nd1 > Rctd:
                    maxcot = 1                                                                
                else:
                    VRdc = 0.24 * stbofck ** (1 / 3) * (1 - 1.2 * sigcp / f_cd) * stboBQ * zi 
                    if 1 - VRdc / Qd < stbkepse7:                                        
                        maxcot = 3                                                         
                    else:
                        maxcot = min((1.2 + 1.4 * sigcp / f_cd) / (1 - VRdc / Qd), 3)
                    if Nd1 > 0:
                        maxcot = 1 + (maxcot - 1) * (Rctd - Nd1) / Rctd                        
            elif stboNorm == 2:
                maxcot = 2.5
            if stbomaxcottheta > stbkepse3:
                maxcot = min(max(stbomaxcottheta, 1), maxcot)                 
            stbZVRdmax = stboBQ * zi * nue1 * f_cd / (maxcot + 1 / maxcot)                     
            if Qd <= stbZVRdmax + stbkepse5:
                stbZcottheta = maxcot
            elif Qd <= stboBQ * zi * nue1 * f_cd / (1 + 1 / 1) + stbkepse5:           
                Term = 2 * Qd / (stboBQ * zi * nue1 * f_cd)
                theta = 0.5 *  math.atan(Term / math.sqrt(-Term * Term + 1))
                stbZcottheta = max(1 / math.tan(theta), 1)
                stbZVRdmax = stboBQ * zi * nue1 * f_cd / (stbZcottheta + 1 / stbZcottheta)
            else:                                                                              
                stbZcottheta = 1
                stbZVRdmax = stboBQ * zi * nue1 * f_cd / (stbZcottheta + 1 / stbZcottheta)
        
        # Minimum shear reinforcement [cm ^ 2 / m]
        if stboNorm == 1 or stboNorm == 3:                                                  
            stbZminas = 0.16 * stbffctm() / stbofyk * stboBQ * 10000                           
        elif stboNorm == 2:
            stbZminas = 0.08 * math.sqrt(stbofck) / stbofyk * stboBQ * 10000                        
        
        # required shear reinforcement
        if Qd <= stbZVRdc + stbkepse5:
            stbZerfas = stbZminas
        elif Qd <= stbZVRdmax + stbkepse5:
            stbZerfas = Qd / f_yd / zi / stbZcottheta * 10000
            if stbZerfas < stbZminas:
                stbZerfas = stbZminas
                if stbZcottheta > 1 + stbkepse5 and stbomaxcottheta <= stbkepse3:

                    # stbZcottheta is reduced so that stbZerfas = stbZminas applies
                    stbZcottheta = max(Qd / f_yd / zi / stbZerfas * 10000, 1)   

                    #for the reduced value of stbZcottheta there is a higher value of stbZVRdmax        
                    stbZVRdmax = stboBQ * zi * nue1 * f_cd / (stbZcottheta + 1 / stbZcottheta) 
        
        else:
            stbZerfas = -1                                 #print( QuerBemessN123)
#------------------------------------------------------------------------------------------------------#  

def stbfAcc():
    xgr = 0
    q = 0
    phi0 = 0
    if stbZepscd[2] < stbkepse7:
        stbfAcc = math.pi * stboKR ** 2
        
    elif stbZepscd[1] > -stbkepse7:
        stbfAcc = 0

    else:
        xgr = stboD * stbZepscd[1] / (stbZepscd[1] - stbZepscd[2])
        q = (stboKR - xgr) / stboKR
        phi0 = math.pi / 2 -  math.atan(q / math.sqrt(1 - q ** 2))
        stbfAcc = stboKR ** 2 * (2 * phi0 - math.sin(2 * phi0)) / 2

    return stbfAcc
#------------------------------------------------------------------------------------------------------#  

#------------------------------------------------------------------------------------------------------#  
#################################----End of Module----################################################
#------------------------------------------------------------------------------------------------------#  

if __name__ == "__main__":
    for i in range(11,29):
        print(StB_K_MN(2, 1.5, 1.15,810,0, 600,0 ,700, 98, 0 ,45, 0.909090909, 0.002, 0.0035, 2, 0.1818182, "0.10 0.2" ,500, 525, 200000, 0.025, 240,1,i))
    for i in range(11,24):
        print(StB_K_Q(2, 1.5, 1.15, 810, 0, 1607 ,700, 98, 0 ,45, 0.9090909, 0.002, 0.0035, 2.00, 0.181818182, "0.10 0.2",500, 525, 200000, 0.025, 0,0,0,i))
#     # A = StB_K_MN(2, 1.5, 1.15, 1.35*90.03, 1.35*-624.9, 90.03, -624.9, 900, 100, 0.0, 35.0, 0.91, 0.002, 0.0035, 2.0, 0.18, '0.1 0.2', 500, 525, 200000.0, 0.025, 0,1, 17)
#     # print(StB_K_MN(2, 1.5, 1.15, 1.35*90.03, 1.35*-624.9, 90.03, -624.9, 900, 100, 0.0, 35.0, 0.91, 0.002, 0.0035, 2.0, 0.18, '0.1 0.2', 500, 525, 200000.0, 0.025, 0,1, 17))
#     # print(StB_K_Q(2, 1.5, 1.15, 1.35*90.03, 1.35*-624.9, 1.35*-634.4, 900, 100, A, 35.0, 0.91, 0.002, 0.0035, 2.0, 0.18, '0.1 0.2', 500, 525, 200000.0, 0.025, 0.0, 0.0, 0.0, 19))

#------------------------------------------------------------------------------------------------------#  
#################################----End of Codee----################################################
#------------------------------------------------------------------------------------------------------# 