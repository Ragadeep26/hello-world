###----DIMENSIONING OF CIRCULAR REINFORCEMNT-----###
'''
Date of Original Version -26th July, 2017 -
Date of Python version - 18th Feb, 2020 - ----
'''
###----Python Version created by RAGADEEP BOJJA (Translate of 0_stb created in VBA by Dr. Berthold Klobe)----###
#------------------------------------------------------------------------------------------------------#
#
#Required Modules
import math 
#import Klobe3_GlobalVarR as Variable
#from dimensioning.py_StB_nya.GlobalVarR import *

stbkitmax = 50
stbkepse3 = 0.0001
stbkepse5 =0.00001
stbkepse7 = 0.0000001
#stbofck (beta_WN) = 15
stbk15tau012 = 0.5
stbk15tau02 = 1.2
stbk15tau03 = 2
stbk15tau1 = 1.4     
stbk15tau2 = 0.7     
#stbofck (beta_WN) = 25
stbk25tau012 = 0.75
stbk25tau02 = 1.8
stbk25tau03 = 3
stbk25tau1 = 1.8     
stbk25tau2 = 0.9     
#stbofck (beta_WN) = 35
stbk35tau012 = 1
stbk35tau02 = 2.4
stbk35tau03 = 4
stbk35tau1 = 2.2     
stbk35tau2 = 1.1     
#stbofck (beta_WN) = 45
stbk45tau012 = 1.1
stbk45tau02 = 2.7
stbk45tau03 = 4.5
stbk45tau1 = 2.6     
stbk45tau2 = 1.3     
#stbofck (beta_WN) = 55
stbk55tau012 = 1.25
stbk55tau02 = 3
stbk55tau03 = 5
stbk55tau1 = 3      
stbk55tau2 = 1.5  
stbkKemax = 0.3803
stbkRemax = 0.4

def RechenWerte(Norm, gam_c, gam_s, Md, Nd, Qd, Mk, Nk,DD, BB, HH_, H__, sym0 , vorAs0, delta, vorAs1, vorAs2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K,f_yk, f_tk, Es, eps_su, RissP1, minBew, TauP1, TauP2, TauP3, ii):
    stboNorm = Norm
    stboQuer = 3
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
    
    stbofck = f_ck
    stboalpha = alpha
    stboepscy = eps_cy
    stboepscu = eps_cu
    stbon2 = n2

    stbofyk = f_yk
    stboftk = f_tk
    stboepssy = f_yk / Es
    stboepssu = eps_su
    Nd1 = 0
    if stboQuer == 1 or stboQuer == 2:
        stboNd = Nd / 1000 / stboKR ** 2 / stbofck
        stboMd = abs(Md) / 1000 / stboKR ** 3 / stbofck
        stboQd = abs(Qd) / 1000 / stboKR ** 2 / stbofck
        stboNk = Nk / 1000 / stboKR ** 2 / stbofck
        stboMk = abs(Mk) / 1000 / stboKR ** 3 / stbofck
        stboHQ = stboD * math.sqrt(math.pi / 4)
        stboBQ = stboD * math.sqrt(math.pi / 4)
    elif stboQuer == 3:
        stboNd = Nd/ 1000 / stboRB / stboD / stbofck
        stboMd = abs(Md) / 1000 / stboRB / stboD ** 2 / stbofck
        stboQd = abs(Qd) / 1000 / stboRB / stboD / stbofck
        stboNk = Nk / 1000 / stboRB / stboD / stbofck
        stboMk = abs(Mk) / 1000 / stboRB / stboD ** 2 / stbofck
        stboHQ = stboD
        stboBQ = stboRB

    if abs(stboNd) < stbkepse7:
        stboeNd = stboMd / stbkepse7
    else:
        stboeNd = stboMd / stboNd
    
    if abs(stboNk) < stbkepse7:
        stboeNk = stboMk / stbkepse7
    else:
        stboeNk = stboMk / stboNk

    if abs(stboNd) < stbkepse5 and stboMd < stbkepse5:
        stboNullSd = True
        stboVMd = 0
        stboNullSk = True
        stboVMk = 0
    else:
        stboNullSd = False
        if Md >= 0:
            stboVMd = 0
        else:
            stboVMd = 1
        
        if abs(stboNk) < stbkepse5 and stboMk < stbkepse5:
            stboNullSk = True
        else:
            stboNullSk = False
            if Mk >= 0:
                stboVMk = 0
            else:
                stboVMk = 1


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
    
    SgamCSini(gam_c, gam_s, delt_S, delt_K)

    stbZiZ = 1                  

    if (abs(stboeNd - stbfeBew()) < stbkepse7 and stboNd > stbkepse5) or (abs(stboeNd) < stbkepse7 and stboNd < -stbkepse5) or((stboVMd != stboVMk or sym0 == True) and stbobHkrit == False):
        stbosymmue0 = True
    else:
        stbosymmue0 = False

    stboRissP1 = RissP1
    stbZiZ = 1            
    Sdehnkrit()

    if stboNachweis == 1:
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
        stbZiZ = 1
        stbZmue0[0] = stbovormue0[0]
        stbZmue0[1] = stbovormue0[1]
        stbZmue0[2] = stbovormue0[2]
        stbZgamC[1] = stbogamC[1]
        stbZgamS[1] = stbogamS[1]

        
        for i in range(0,4):
            stbZNucs[i] = 0
            stbZzi[i] = 0

        if stboNorm == 0:
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
    if stboNorm < 0 or stboD < stbkepse5 or ((stboQuer == 1 or stboQuer == 2) and stboKR < stbkepse5) or (stboQuer == 3 and stboRB < stbkepse5) or stboD - stboH[1] - stboH[2] < -stbkepse5 or stbofck < stbkepse5 or stboalpha < stbkepse5 or stboepscy < stbkepse7 or stboepscu < stboepscy - stbkepse7 or stbofyk < stbkepse5 or stboftk < stbofyk - stbkepse5 or stboepssy < stbkepse7 or stboepssu < stboepssy - stbkepse7 or stbogamC[0] < stbkepse5 or stbogamC[1] < stbkepse5 or stbogamS[0] < stbkepse5 or stbogamS[1] < stbkepse5 or (stboNachweis == 2 and stbotau02 < stbotau012 - stbkepse7) or (stboNachweis == 2 and stbotau03 < stbotau02 - stbkepse7):
        stbZbFehler = True
    else:
        stbZbFehler = False
    #print(RechenWerte)


def SRechenWerteZ(InOut):
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
            stbZepssk[2] = stbZeps_s[2]
    #print (SRechenWerteZ)

def SgamCSini(gam_c, gam_s, delt_S, delt_K):
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
    Smue0Druc(delt_S, delt_K)
    #print(SgamCSini)

def stbfeBew():
    SRechenWerteZ(1)
    if stboQuer == 3 and stbobHkrit == True:
        stbfeBew = (stbZ_H[2] - stbZ_H[1]) / 2 / stboD
    else:
        stbfeBew = 0
    return stbfeBew


def Sdehnkrit():
    n_eU = [0,0,0]
    m_eU = [0,0,0]
    dehn = [0,0,0,0]  
    f_null = [0,1,0,0]  
    SRechenWerteZ(1)
    if stboQuer == 3 :
        for it_dehn in range (1,stbkitmax):
            if abs(f_null[1]) > stbkepse5:
                Sitdehn(dehn, f_null, it_dehn)
                Sdehnepscs(dehn[1])
                n_eU[1] = stbfRneU1()
                m_eU[1] = stbfRmeU1()
                n_eU[2] = stbfRneU2()
                m_eU[2] = stbfRmeU2()
                f_null[1] = n_eU[1] + n_eU[2] + m_eU[1] + m_eU[2]
            else:
                break
    stbodehnkrit[1] = dehn[1]
    if stboQuer == 3 :
        for it_dehn in range (1,stbkitmax):
            if abs(f_null[1]) > stbkepse5:
                Sitdehn(dehn, f_null, it_dehn)
                Sdehnepscs(dehn[1])
                n_eU[1] = stbfRneU1()
                m_eU[1] = stbfRmeU1()
                f_null[1] = n_eU[1] + m_eU[1]
            else:
                break
    stbodehnkrit[2] = dehn[1]
    stbZepscd[2] = stboepssu + (stboepssu + stboepscu) * stbZ_H[1] / (stboD - stbZ_H[1])   
    stbodehnkrit[3] = -0.5 * (stbZepscd[2] - stboepscu) / stbZepscd[2]           
    dehn[1] = -1
    dehn[2] = stbodehnkrit[3]
    dehn[3] = 1
    stbZgamC[1] = stbogamC[0]
    stbZgamS[1] = stbogamS[0]
    stbZgamC[2] = stbogamC[1]
    stbZgamS[2] = stbogamS[1]
    stbZgamC[3] = stbogamC[1]
    stbZgamS[3] = stbogamS[1]
    if stboQuer == 3 :
        for k in range(1,4):
            Sdehnepscs(dehn[k])
            n_bU = stbfRnbU()
            m_bU = stbfRmbU()
            n_eU[1] = stbfRneU1()
            m_eU[1] = stbfRmeU1()
            n_eU[2] = stbfRneU2()
            m_eU[2] = stbfRmeU2()
            stbomue0Dehn[1][k] = ((stboNd - n_bU / stbZgamC[k]) * m_eU[2] / stbZgamS[k] - (stboMd - m_bU / stbZgamC[k]) * n_eU[2] / stbZgamS[k]) / (n_eU[1] / stbZgamS[k] * m_eU[2] / stbZgamS[k] - m_eU[1] / stbZgamS[k] * n_eU[2] / stbZgamS[k])
            stbomue0Dehn[2][k] = (n_eU[1] / stbZgamS[k] * (stboMd - m_bU / stbZgamC[k]) - m_eU[1] / stbZgamS[k] * (stboNd - n_bU / stbZgamC[k])) / (n_eU[1] / stbZgamS[k] * m_eU[2] / stbZgamS[k] - m_eU[1] / stbZgamS[k] * n_eU[2] / stbZgamS[k])
            if stbomue0Dehn[1][k] < 0 or stbomue0Dehn[2][k] < 0 :
                stbomue0Dehn[3][k] = -1
            else:
                stbomue0Dehn[3][k] = stbomue0Dehn[1][k] + stbomue0Dehn[2][k]


def Smue0Riss():
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
    stbZiZ = 1
    if stboNorm == 0:
        stbZgamC[1] = 1 / stboalpha
    elif stboNorm > 0:
        stbZgamC[1] = stbogamC[1]
    stbZgamS[1] = 1
    if stboNorm == 0:
        stbofyk = 0.8 * stbofyk
        stboftk = stbofyk
    elif stboNorm > 0:
        stbofyk = stbofyk
        stboftk = stbofyk
    
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
    stboMd =  stbffctm() / stbofck / 6
    Serfmue0_R()
    stbZerfmue0[0] = 0 
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
    stbomue0Druc[2] = EingangWerte[9]
    #print(Smue0Riss)


def Smue0Druc(delt_S, delt_K):
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
                # else:
                #     mue0min = max((StrVek[2]) / 100, 0) * stboftk / stbofck
                
                if stboQuer == 3:
                    stbomue0Druc[0] = 0
                    stbomue0Druc[1] = max(NEdmin * abs(stboNd) * stbogamS[1] / 2 * stboftk / stbofyk, mue0min) / 2
                    stbomue0Druc[2] = stbomue0Druc[1] 
            else:
                NEdmin = StrVek[0]
                if stboQuer == 3:
                    stbomue0Druc[0] = 0
                    stbomue0Druc[1] = NEdmin * abs(stboNd) * stbogamS[1] * stboftk / stbofyk / 2
                    stbomue0Druc[2] = stbomue0Druc[1]  
        else:     
            stbomue0Druc[0] = 0
            stbomue0Druc[1] = 0
            stbomue0Druc[2] = 0
    #print(Smue0Druc)


def stbffctm():
    if stboNorm == 0:
        stbffctm = 0.25 * max(stbofck, 35) ** (2 / 3)
    elif stboNorm > 0:
        if stbofck < 52.5:
            stbffctm = 0.3 * stbofck ** (2 / 3)
        else:
            stbffctm = 2.12 * math.log(1 + (stbofck + 8) / 10)
    #print(stbffctm)
    return stbffctm


def Sdehnepscs(dehn):
    SRechenWerteZ(1)
    #imag = imag+1
    #arrdehn.append(imag)
    if dehn < -0.5:
        stbZeps_c[1] = -stboepscu + (stboepscu - stboepscy) * (-0.5 - dehn) / 0.5
    elif dehn < 0:
        stbZeps_c[1] = -stboepscu
    else:
        stbZeps_c[1] = -stboepscu + dehn * (stboepscu + stboepssu)
    if dehn < -0.5:
        eps_gr = -stboepscu * stbZ_H[1] / stboD
        stbZeps_s[1] = eps_gr + (stboepscy + eps_gr) * (dehn + 0.5) / 0.5
    elif dehn < 0:
        eps_gr = -stboepscu * stbZ_H[1] / stboD
        stbZeps_s[1] = stboepssu + (stboepssu - eps_gr) * dehn / 0.5
    else:
        stbZeps_s[1] = stboepssu
    SRechenWerteZ(2)
    Sepsc2s2()
    #print(Sdehnepscs)
    #print(1)
def Sepsc2s2():
    SRechenWerteZ(1)
    stbZeps_c[2] = stbZeps_c[1] + (stbZeps_s[1] - stbZeps_c[1]) * stboD / (stboD - stbZ_H[1])
    stbZeps_s[2] = stbZeps_c[1] + (stbZeps_s[1] - stbZeps_c[1]) * stbZ_H[2] / (stboD - stbZ_H[1])
    SRechenWerteZ(2)
    #print(Sepsc2s2)
    #print(2)

def Sitdehn(dehn, f_null, it_dehn):
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
        if Nd1 < -stbkepse5:
            if f_null[1] * f_null[2] < 0:
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
            else:
                dehn[2] = dehn[1]
                f_null[2] = f_null[1]
            
        else:
            if f_null[1] * f_null[3] < 0:
                dehn[2] = dehn[1]
                f_null[2] = f_null[1]
            else:
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
        dehn[1] = (dehn[2] + dehn[3]) / 2
    #print(Sitdehn)

def stbfsig_s(eps_s):
    if abs(eps_s) <= stboepssy:
        stbfsig_s = eps_s / stboepssy * stbofyk
    elif abs(eps_s) <= stboepssu:
        stbfsig_s = math.copysign(1,eps_s) * (stbofyk + (stboftk - stbofyk) * (abs(eps_s) - stboepssy) / (stboepssu - stboepssy))
    else:
        stbfsig_s = math.copysign(1,eps_s) * stboftk
    return stbfsig_s

def stbfalpha():
    if stboNorm == 0 or stboNorm == 1:
        stbfalpha = stboalpha
    elif stboNorm == 2 or stboNorm == 3:
        stbfalpha = stboalpha * stbogamC[1] / stbZgamC[1]
    return stbfalpha

def Sitdehn0(dehn, f_null, it_dehn):
    if it_dehn == 1:
        f_null[1] = 0
        dehn[1] = -1
    elif it_dehn == 2:
        dehn[2] = dehn[1]
        f_null[2] = f_null[1]
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
        
        dehn[1] = (dehn[2] + dehn[3]) / 2
    #print(Sitdehn0)



def Smue0opt(it_mue, mue_loop):
    bEnd = False
    if stbZerfmue0[1] < 0 or stbZerfmue0[2] < 0:
        sum_mue0 = -1
    else:
        sum_mue0 = stbZerfmue0[1] + stbZerfmue0[2]
    
    mimue0[1][2] = sum_mue0

    if it_mue == 1:
        if stbosymmue0==True or stbZerfmue0[2] <= stbovormue0[2] + stbkepse5:
            mue_loop = False
        else:
            mimue0[0][4] = stbZerfmue0[2]
            mimue0[1][4] = sum_mue0
            stbZerfmue0[2] = stbovormue0[2]
            stbZsymm = False
            mue_loop = True
        
    elif it_mue == 2:
        mimue0[0][0] = stbZerfmue0[2]
        mimue0[1][0] = sum_mue0
        mimue0[0][2] = mimue0[0][4]
        mimue0[1][2] = mimue0[1][4]
        if (mimue0[1][0] < mimue0[1][2] and mimue0[1][0] >= 0) or mimue0[1][2] < 0:
            mimue0[0][2] = mimue0[0][0]
            mimue0[1][2] = mimue0[1][0]
        
        for k in range(1,4):
            if (stbomue0Dehn[3][k] < mimue0[1][2] and stbomue0Dehn[3][k] >= 0) or mimue0[1][2] < 0:
                mimue0[0][2] = stbomue0Dehn[2][k]
                mimue0[1][2] = stbomue0Dehn[3][k]

        stbZerfmue0[2] = mimue0[0][2]
    elif it_mue == 3:
        stbZerfmue0[2] = max(mimue0[0][2] - stbkepse3, stbovormue0[2])
    elif it_mue == 4:
        mimue0[0][1]= stbZerfmue0[2]
        mimue0[1][1] = sum_mue0
        stbZerfmue0[2] = max(mimue0[0][2] + stbkepse3, stbovormue0[2])
    elif it_mue == 5:
        mimue0[0][3] = stbZerfmue0[2]
        mimue0[1][3] = sum_mue0
        bEnd = False
        if mimue0[1][2] < 0 or mimue0[1][2] > mimue0[1][4]:
            mimue0[0][1]= mimue0[0][2]
            mimue0[1][1] = mimue0[1][2]
            mimue0[0][3] = mimue0[0][4]
            mimue0[1][3] = mimue0[1][4]
            mimue0[0][2] = (mimue0[0][1]+ mimue0[0][3]) / 2
        elif mimue0[1][1] < mimue0[1][3] - stbkepse5 and mimue0[1][1] >= 0:
            mimue0[0][1]= mimue0[0][0]
            mimue0[1][1] = mimue0[1][0]
            mimue0[0][3] = mimue0[0][2]
            mimue0[1][3] = mimue0[1][2]
            mimue0[0][2] = (mimue0[0][1]+ mimue0[0][3]) / 2
        elif mimue0[1][3] < mimue0[1][1] - stbkepse5 and mimue0[1][3] >= 0:
            mimue0[0][1]= mimue0[0][2]
            mimue0[1][1] = mimue0[1][2]
            mimue0[0][3] = mimue0[0][4]
            mimue0[1][3] = mimue0[1][4]
            mimue0[0][2] = (mimue0[0][1]+ mimue0[0][3]) / 2
        else:
            bEnd = True
        
        stbZerfmue0[2] = mimue0[0][2]
    else:
        if stbZsymm == True:
            mue_loop = False
        elif bEnd:
            if sum_mue0 >= 0:
                mue_loop = False
            else:
                stbZsymm = True
            
        elif mimue0[0][3] - mimue0[0][1]< stbkepse5:
            if sum_mue0 >= 0:
                mue_loop = False
            else:
                stbZerfmue0[2] = mimue0[0][3]
                bEnd = True
            
        else:
            if mimue0[1][2] < mimue0[1][3] - stbkepse5 and mimue0[1][2] >= 0:
                mimue0[0][3] = mimue0[0][2]
                mimue0[1][3] = mimue0[1][2]
                mimue0[0][2] = (mimue0[0][1]+ mimue0[0][3]) / 2
            else:
                mimue0[0][1]= mimue0[0][2]
                mimue0[1][1] = mimue0[1][2]
                mimue0[0][2] = (mimue0[0][1]+ mimue0[0][3]) / 2
            
            stbZerfmue0[2] = mimue0[0][2]
    # print(Smue0opt)


def SRissB():
    SgamC1()
    if stboRissP1 >= 1 or stboii >= 20:
        Gebrauch_R()
    if stboRissP1 >= 1 and stbfsig_s(stbZepssk[1]) > stboRissP1:
        SigVor_R()
    if stboQuer == 3 and (stbZmue0[1] > stbZerfmue0[1] + stbkepse5 or stbZmue0[2] > stbZerfmue0[2] + stbkepse5):
        Bruch_R()
    #print(SRissB)


def SgamC1():
    fnullC = [0,0,0,0]
    erfmue2 = [0,0,0]
    stbZiZ = 1
    SRechenWerteZ(1)
    if stbobminBew :
        vormue0_3 = max(stbovormue0[0], stbomue0Riss[0]) + max(stbovormue0[1], stbomue0Riss[1]) + max(stbovormue0[2], stbomue0Riss[2])
    else:
        vormue0_3 = stbovormue0[0] + stbovormue0[1] + stbovormue0[2]
    

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
    if stboQuer == 3 :
        Serfmue0_R()
        erfmue_0 = stbZerfmue0[1] + stbZerfmue0[2]
    
    if stboQuer == 3 :
        stbZmue0[0] = 0
        stbZmue0[1] = max(stbZerfmue0[1], stbovormue0[1])
        if stbosymmue0 == True:
            stbZmue0[2] = stbZmue0[1]
        else:
            stbZmue0[2] = max(stbZerfmue0[2], stbovormue0[2])
        
        if stboNd > stbkepse5 and stbZmue0[1] > (stbZerfmue0[1] + stbkepse7) and stbosymmue0 == False:
            if stboMd / stboNd < 0.5 - stbZ_H[1] / stboD:
                erfmue2[1] = stbZmue0[1]
                Serfmue2_R(erfmue2)
                stbZmue0[2] = max(erfmue2[2], stbZmue0[2])
        
    if bLastLoop :
        bLoop = False
    else:
        if stboNorm == 0 :
            if erfmue_0 < stbkepse7 :
                interpol = 0
            else:
                if stboQuer == 3 and (stbZmue0[1] > stbZerfmue0[1] + stbkepse5 or stbZmue0[2] > stbZerfmue0[2] + stbkepse5):
                    Bruch_R()
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

        if stboQuer == 3 :
            Serfmue0_R()
            erfmue_0 = stbZerfmue0[1] + stbZerfmue0[2]
        
        if stboQuer == 3 :
            stbZmue0[0] = 0
            stbZmue0[1] = max(stbZerfmue0[1], stbovormue0[1])
            if stbosymmue0 == True:
                stbZmue0[2] = stbZmue0[1]
            else:
                stbZmue0[2] = max(stbZerfmue0[2], stbovormue0[2])
            
            if stboNd > stbkepse5 and stbZmue0[1] > (stbZerfmue0[1] + stbkepse7) and stbosymmue0 == False:
                if stboMd / stboNd < 0.5 - stbZ_H[1] / stboD:
                    erfmue2[1] = stbZmue0[1]
                    Serfmue2_R(erfmue2)
                    stbZmue0[2] = max(erfmue2[2], stbZmue0[2])
                
        if bLastLoop :
            bLoop = False
        else:
            if stboNorm == 0 :
                if erfmue_0 < stbkepse7 :
                    interpol = 0
                else:
                    if stboQuer == 3 and (stbZmue0[1] > stbZerfmue0[1] + stbkepse5 or stbZmue0[2] > stbZerfmue0[2] + stbkepse5):
                        Bruch_R()
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
        print("sgamc1 lo")
        stbZbFehler = True
    #print(stbZeps_c)
    #print(SgamC1)
#############################K - requirements#######################################################
i2n = 9
def stbfphiAo():
    SRechenWerteZ(1)
    r1 = 1
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

def stbfphiAu():

    SRechenWerteZ(1)
    r1 = 1
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

def stbfKnbU():
    SRechenWerteZ(1)
    phiAo = stbfphiAo()
    phiAu = stbfphiAu()
    phiBo = phiAu
    phiBu = 0
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

def stbfKmbU():
    SRechenWerteZ(1)
    phiAo = stbfphiAo()
    phiAu = stbfphiAu()
    phiBo = phiAu
    phiBu = 0
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


#############################Getting into R things#################################################
def StB_R_MN(Norm , gam_c , gam_s , Md , Nd , Mk , Nk , DD , BB , HH_ , H__ , sym0 , vorAs1 , vorAs2 , f_ck , alpha , eps_cy , eps_cu , n2 , delt_S , delt_K , f_yk , f_tk , Es , eps_su , RissP1 , minBew ,  ii ) :

    mue0 = [0,0,0]

    stboNachweis = 1
    stboQuer = 3

    RechenWerte(Norm, gam_c, gam_s, Md, Nd, 0, Mk, Nk, DD, BB, HH_, H__, sym0, 0, 0, vorAs1, vorAs2, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 0, 0, 0, ii)
    if stbZbFehler : 
        print('Error')
    if stboNullSd :
        stbZerfmue0[1] = 0
        stbZerfmue0[2] = 0
        stbZmue0[1] = stbovormue0[1]
        stbZmue0[2] = stbovormue0[2]
        if stbobminBew :
            stbZmue0[1] = max(stbZmue0[1], stbomue0Riss[1])
            stbZmue0[2] = max(stbZmue0[2], stbomue0Riss[2])
    else:
        if stbobDruc[2] and stbovormue0[1] <= stbkepse7 and stbobminBew == False :
            Snue0_R()
            if stbZnue0 > 0 :
                stbZerfmue0[1] = 0
                stbZerfmue0[2] = 0
                stbZmue0[1] = 0
                stbZmue0[2] = 0
            
        else:
            stbZnue0 = -1
        if stbZnue0 < 0 :
            SRissB()

    if stbZbFehler :
        StB_R_Mn = 0
    elif stboii == 11 :
        StB_R_Mn = stbZepscd[1 + stboVMd]
    elif stboii == 12 :
        StB_R_Mn = stbZepscd[2 - stboVMd]
    elif stboii == 13 :
        if stbZmue0[1 + stboVMd] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbZepssd[1 + stboVMd]
        
    elif stboii == 14 :
        if stbZmue0[2 - stboVMd] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbZepssd[2 - stboVMd]
        
    elif stboii == 15 :
        StB_R_Mn = math.copysign(1,Md) * stbZRMd * 1000 * stboRB * stboD ** 2 * stbofck
    elif stboii == 16 :
        StB_R_Mn = stbZRNd * 1000 * stboRB * stboD * stbofck
    elif stboii == 17 :
        StB_R_Mn = 10000 * stbZmue0[1 + stboVMd] * stboRB * stboD * stbofck / stboftk
    elif stboii == 18 :
        StB_R_Mn = 10000 * stbZmue0[2 - stboVMd] * stboRB * stboD * stbofck / stboftk
    elif stboii == 19 :
        if stboNullSd :
            StB_R_Mn = 0
        else:
            if stbZmue0[1] + stbZmue0[2] < stbkepse7 :
                StB_R_Mn = stboNd / stbZRNd
            else:
                if vorAs1 < stbkepse7 and vorAs2 < stbkepse7 :
                    StB_R_Mn = max(stbZerfmue0[1] + stbZerfmue0[2], 0) / (stbZmue0[1] + stbZmue0[2])
                else:
                    mue0[1] = stbZmue0[1]
                    mue0[2] = stbZmue0[2]
                    StB_R_Mn = (StB_R_MN(Norm, gam_c, gam_s, Md, Nd, Mk, Nk,DD, BB, HH_, H__, sym0, 0, 0, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, 0, minBew, 17) + StB_R_MN(Norm, gam_c, gam_s, Md, Nd, Mk, Nk,DD, BB, HH_, H__, sym0, 0, 0, f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, 0, minBew, 18)) / 10000 / stboRB / stboD / stbofck * stboftk / (mue0[1] + mue0[2])
                
    elif stboii == 21 :
        StB_R_Mn = stbZepsck[1 + stboVMk]
    elif stboii == 22 :
        StB_R_Mn = stbZepsck[2 - stboVMk]
    elif stboii == 23 :
        if stbZmue0[1 + stboVMk] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbZepssk[1 + stboVMk]
        
    elif stboii == 24 :
        if stbZmue0[2 - stboVMk] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbZepssk[2 - stboVMk]
        
    elif stboii == 25 :
        StB_R_Mn = math.copysign(1,Mk) * stbZRMk * 1000 * stboRB * stboD ** 2 * stbofck
    elif stboii == 26 :
        StB_R_Mn = stbZRNk * 1000 * stboRB * stboD * stbofck
    elif stboii == 27 :
        if stbZmue0[1 + stboVMk] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbfsig_s(stbZepssk[1 + stboVMk])
        
    elif stboii == 28 :
        if stbZmue0[2 - stboVMk] < stbkepse7 :
            StB_R_Mn = ""
        else:
            StB_R_Mn = stbfsig_s(stbZepssk[2 - stboVMk])
        
    else:
        StB_R_Mn = ""
    return StB_R_Mn

def StB_R_Q(Norm , gam_c , gam_s , Md , Nd , Qd , DD , BB , HH_ , H__ , vorAs1 , vorAs2 , f_ck , alpha , eps_cy , eps_cu , n2 , delt_S , delt_K , f_yk , f_tk , Es , eps_su ,TauP1 , TauP2 , TauP3 , ii ) :
    stboNachweis = 2
    stboQuer = 3

    RechenWerte(Norm, gam_c, gam_s, Md, Nd, Qd, 0, 0, DD, BB, HH_, H__, False, 0, 0, vorAs1, vorAs2,f_ck, alpha, eps_cy, eps_cu, n2, delt_S, delt_K, f_yk, f_tk, Es, eps_su, 0, 0, TauP1, TauP2, TauP3, ii)
    if stbZbFehler : 
        print("error")

    if not stboNullSd :
        BruchC1S1()
    

    if stboNorm == 0 :
        QuerBemessN0()
    elif stboNorm > 0 :
        QuerBemessN123()
    

    if stbZbFehler :
        StB_R_Q = 0
    elif stboii == 11 :
        if stbZNucs[0] > -stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = stbZNucs[0] * 1000 * stboRB * stboD * stbofck
        
    elif stboii == 12 :
        if stbZNucs[0] > -stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = math.copysign(1,Md) * stbZzi[0] * 1000
        
    elif stboii == 13 :
        if stbZNucs[1] < stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = stbZNucs[1] * 1000 * stboRB * stboD * stbofck
        
    elif stboii == 14 :
        if stbZNucs[1] < stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = math.copysign(1,Md) * stbZzi[1] * 1000
        
    elif stboii == 15 :
        if stbZNucs[2] > -stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = stbZNucs[2] * 1000 * stboRB * stboD * stbofck
        
    elif stboii == 16 :
        if stbZNucs[2] > -stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = math.copysign(1,Md) * stbZzi[2] * 1000
        
    elif stboii == 17 :
        if stbZNucs[3] < stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = stbZNucs[3] * 1000 * stboRB * stboD * stbofck
        
    elif stboii == 18 :
        if stbZNucs[3] < stbkepse7 :
            StB_R_Q = ""
        else:
            StB_R_Q = stbZzi[3] * 1000
        
    elif stboii == 19 :
        StB_R_Q = stbZerfas
    elif stboii == 20 :
        if stboNorm == 0 :
            StB_R_Q = stbZtau0
        else:
            StB_R_Q = stbZminas
        
    elif stboii == 21 :
        if stboNorm == 0 :
            StB_R_Q = stbotau012
        else:
            StB_R_Q = stbZVRdc * 1000
        
    elif stboii == 22 :
        if stboNorm == 0 :
            StB_R_Q = stbotau02
        else:
            if stbZmue0[1] < stbkepse7 :
                StB_R_Q = stbZtaucp
            else:
                StB_R_Q = stbZVRdmax * 1000
            
        
    elif stboii == 23 :
        if stboNorm == 0 :
            StB_R_Q = stbotau03
        else:
            if stbZmue0[1] < stbkepse7 :
                StB_R_Q = stbZfcvd
            else:
                StB_R_Q = stbZcottheta
            
        
    else:
        StB_R_Q = ""
    return StB_R_Q

def Snue0_R():
    dehn = [0,0,0,0] 
    f_null= [0,1,0,0]

    for it_dehn in range(1,stbkitmax):
        if it_dehn == 2 or abs(f_null[1]) > stbkepse7:
            Sitdehn0(dehn, f_null, it_dehn)
            Sdehnepscs(dehn[1])
            n_bU = stbfRnbU()
            m_bU = stbfRmbU()
            f_null[1] = stboMd * n_bU - stboNd * m_bU
        else:
            break

    if it_dehn == stbkitmax : 
        stbZbFehler = True

    stbZnue0 = (abs(n_bU) + m_bU) / (abs(stboNd) + stboMd)
    if stbZnue0 >= stbogamC[0] - stbkepse5 and stbZbFehler == False :
        stbZgamC[1] = stbogamC[0]
        stbZgamS[1] = stbogamS[0]
        stbZRNd = n_bU / stbZgamC[1]
        stbZRMd = m_bU / stbZgamC[1]
        if stboii >= 20 :
            Gebrauch_R()
        
    else:
        stbZnue0 = -stbZnue0
    


def stbfyAo() :
    SRechenWerteZ(1)
    D1 = 1
    if stbZeps_c[1] < 0 :
        if stbZeps_c[2] < 0 or abs(stbZeps_c[1] - stbZeps_c[2]) < stbkepse7 :
            stbfyAo = D1 / 2
        else:
            stbfyAo = (stbZeps_c[1] + stbZeps_c[2]) / 2 * D1 / (stbZeps_c[1] - stbZeps_c[2])
        
    else:
        stbfyAo = -D1 / 2
    return stbfyAo


def stbfyAu() :
    SRechenWerteZ(1)
    D1 = 1
    if stbZeps_c[1] < -stboepscy :
        if abs(stbZeps_c[1] - stbZeps_c[2]) < stbkepse7 :
            stbfyAu = D1 / 2
        else:
            stbfyAu = (stboepscy + (stbZeps_c[1] + stbZeps_c[2]) / 2) * D1 / (stbZeps_c[1] - stbZeps_c[2])  
    else:
        stbfyAu = -D1 / 2
    return stbfyAu


def stbfRnbU(): 
    SRechenWerteZ(1)
    yAo = stbfyAo()
    yAu = stbfyAu()
    yBo = yAu
    yBu = -0.5
    if stbZeps_c[1] < 0 :
        m1 = -(stbZeps_c[2] + stbZeps_c[1]) / stboepscy / 2
        m2 = -(stbZeps_c[2] - stbZeps_c[1]) / stboepscy
        if abs(yAo - yAu) < stbkepse7 :
            nAbU = 0
        elif abs(m2) < stbkepse7 :
            if m1 <= 0 :
                nAbU = 0
            elif m1 >= 1 :
                nAbU = -1
            else:
                nAbU = -1 * (1 - (1 - m1) ** stbon2)
            
        else:
            nAbU = (abs(1 - m1 - m2 * yAu) ** (stbon2 + 1) - abs(1 - m1 - m2 * yAo) ** (stbon2 + 1)) / m2 / (stbon2 + 1) + (yAu - yAo)
        
        nBbU = yBu - yBo
    else:
        nAbU = 0
        nBbU = 0
    stbfRnbU = nAbU + nBbU
    return stbfRnbU

def stbfRmbU(): 
    SRechenWerteZ(1)
    yAo = stbfyAo()
    yAu = stbfyAu()
    yBo = yAu
    yBu = -0.5
    if stbZeps_c[1] < 0 :
        m1 = -(stbZeps_c[2] + stbZeps_c[1]) / stboepscy / 2
        m2 = -(stbZeps_c[2] - stbZeps_c[1]) / stboepscy
        if abs(yAo - yAu) < stbkepse7 :
            mAbU = 0
        elif abs(m2) < stbkepse7 :
            mAbU = 0
        else:
            mAbU = (abs(1 - m1 - m2 * yAo) ** (stbon2 + 2) - abs(1 - m1 - m2 * yAu) ** (stbon2 + 2)) / m2 ** 2 / (stbon2 + 2) + (abs(1 - m1 - m2 * yAo) ** (stbon2 + 1) - abs(1 - m1 - m2 * yAu) ** (stbon2 + 1)) / m2 ** 2 / (stbon2 + 1) * (m1 - 1) - (yAo ** 2 - yAu ** 2) / 2 
        mBbU = (yBu ** 2 - yBo ** 2) / 2
    else:
        mAbU = 0
        mBbU = 0
    return mAbU + mBbU

def stbfRneU1(): 
    SRechenWerteZ(1)
    if abs(stbZeps_s[1]) <= stboepssy :
        stbfRneU1 = stbZeps_s[1] / stboepssy * stbofyk / stboftk
    else:
        stbfRneU1 = math.copysign(1,stbZeps_s[1]) * (stbofyk / stboftk + (1 - stbofyk / stboftk) * (abs(stbZeps_s[1]) - stboepssy) / (stboepssu - stboepssy))
    return stbfRneU1


def stbfRmeU1(): 
    SRechenWerteZ(1)
    stbfRmeU1 = stbfRneU1() * (stboD / 2 - stbZ_H[1]) / stboD
    return stbfRmeU1

def stbfRneU2(): 
    SRechenWerteZ(1)
    if abs(stbZeps_s[2]) <= stboepssy :
        stbfRneU2 = stbZeps_s[2] / stboepssy * stbofyk / stboftk
    else:
        stbfRneU2 = math.copysign(1,stbZeps_s[2]) * (stbofyk / stboftk + (1 - stbofyk / stboftk) * (abs(stbZeps_s[2]) - stboepssy) / (stboepssu - stboepssy))
    return stbfRneU2


def stbfRmeU2(): 
    SRechenWerteZ(1)
    stbfRmeU2 = -stbfRneU2() * (stboD / 2 - stbZ_H[2]) / stboD
    return stbfRmeU2

def Serfmue2_R(erfmue2):
    n_eU = [0,0,0]
    m_eU = [0,0,0]
    Sdehnepscs(1)

    n_bU = stbfRnbU()
    m_bU = stbfRmbU()

    n_eU[1] = stbfRneU1()
    m_eU[1] = stbfRmeU1()
    n_eU[2] = stbfRneU2()
    m_eU[2] = stbfRmeU2()

    if abs(m_eU[2]) > stbkepse7 :
        erfmue2[2] = stbZgamS[1] * (stboMd - m_bU / stbZgamC[1] - erfmue2[1] * m_eU[1] / stbZgamS[1]) / m_eU[2]
    else:
        erfmue2[2] = 1 / stbkepse7

    stbZRNd = n_bU / stbZgamC[1] + erfmue2[1] * n_eU[1] / stbZgamS[1] + erfmue2[2] * n_eU[2] / stbZgamS[1]
    stbZRMd = m_bU / stbZgamC[1] + erfmue2[1] * m_eU[1] / stbZgamS[1] + erfmue2[2] * m_eU[2] / stbZgamS[1]

def Serfmue0_R():
    n_eU = [0,0,0]
    m_eU = [0,0,0]
    dehn = [0,0,0,0] 

    f_null = [0,1,0,0] 

    it_mue = 1
    stbZsymm = True 
    mue_loop = False
    it_dehn = 1
    while (((it_dehn == 1 or (stboNd >= stbkepse5 or stboMd >= stbkepse5)) or (it_dehn == 2 and (stboNd <= -stbkepse5 or stboMd >= stbkepse5)) or it_dehn == 3 or abs(f_null[1]) > stbkepse7)) and it_dehn < stbkitmax:
        it_dehn = it_dehn + 1
        if it_dehn == 3 :
            dehn[3] = dehn[1]
            f_null[3] = f_null[1]
            if stbZsymm :
                dehn[1] = stbodehnkrit[1]
            else:
                dehn[1] = stbodehnkrit[2] - stbkepse3
            
        elif it_dehn == 4 and stbZsymm == False :
            fnull2 = f_null[1]
            dehn[1] = stbodehnkrit[2] + stbkepse3
        elif it_dehn == 5 and stbZsymm == False :
            fnull3 = f_null[1]
            if fnull2 * f_null[2] < 0 :
                dehn[3] = stbodehnkrit[2] - stbkepse3
                f_null[3] = fnull2
                dehn[1] = (dehn[2] + dehn[3]) / 2
            elif fnull3 * f_null[3] < 0 :
                dehn[2] = stbodehnkrit[2] + stbkepse3
                f_null[2] = fnull3
                dehn[1] = (dehn[2] + dehn[3]) / 2
            else:
                dehn[1] = stbodehnkrit[3]
            
        else:
            Sitdehn(dehn, f_null, it_dehn)
        
        
        Sdehnepscs(dehn[1])
        n_bU = stbfRnbU()
        m_bU = stbfRmbU()

        n_eU[1] = stbfRneU1()
        m_eU[1] = stbfRmeU1()
        n_eU[2] = stbfRneU2()
        m_eU[2] = stbfRmeU2()
        if stbZsymm :
            if abs(n_eU[1] + n_eU[2] + m_eU[1] + m_eU[2]) > stbkepse7 :
                stbZerfmue0[1] = stbZgamS[1] * (stboNd - n_bU / stbZgamC[1] + stboMd - m_bU / stbZgamC[1]) / (n_eU[1] + n_eU[2] + m_eU[1] + m_eU[2])
            else:
                stbZerfmue0[1] = 1 / stbkepse7
            
            stbZerfmue0[2] = stbZerfmue0[1]
            f_null[1] = (m_eU[1] + m_eU[2]) * (stboNd - n_bU / stbZgamC[1]) - (n_eU[1] + n_eU[2]) * (stboMd - m_bU / stbZgamC[1])

        else:

            if abs(n_eU[1] + m_eU[1]) > stbkepse7 :
                stbZerfmue0[1] = stbZgamS[1] * (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1] + stboMd - m_bU / stbZgamC[1] - stbZerfmue0[2] * m_eU[2] / stbZgamS[1]) / (n_eU[1] + m_eU[1])
            else:
                stbZerfmue0[1] = 1 / stbkepse7
            
            f_null[1] = m_eU[1] * (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1]) - n_eU[1] * (stboMd - m_bU / stbZgamC[1] - stbZerfmue0[2] * m_eU[2] / stbZgamS[1])
    if stbZsymm and (it_dehn == stbkitmax or stbZerfmue0[1] < 0) and abs(stboNd) > stbkepse5 :
        if stboNd < -stbkepse5 and abs(stboeNd) < 0.5 - max(stboH[1], stboH[2]) / stboD :
            dehn[1] = -1
            bHlp = True
        elif stboNd > stbkepse5 and stboeNd < 0.5 - stbZ_H[1] / stboD :
            dehn[1] = 1
            bHlp = True
        else:
            bHlp = False
        
        if bHlp :
            Sdehnepscs(dehn[1])
            n_bU = stbfKnbU()
            m_bU = stbfKmbU()
            n_eU[1] = stbfRneU1()
            m_eU[1] = stbfRmeU1()
            n_eU[2] = stbfRneU2()
            m_eU[2] = stbfRmeU2()
            if abs(m_eU[1]) < stbkepse7 :
                stbZerfmue0[2] = (stboMd - m_bU / stbZgamC[1]) / m_eU[2] * stbZgamS[1]
                stbZerfmue0[1] = (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1]) / n_eU[1] * stbZgamS[1]
            elif abs(m_eU[2]) < stbkepse7 :
                stbZerfmue0[1] = (stboMd - m_bU / stbZgamC[1]) / m_eU[1] * stbZgamS[1]
                stbZerfmue0[2] = (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[1] * n_eU[1] / stbZgamS[1]) / n_eU[2] * stbZgamS[1]
            else:
                stbZerfmue0[2] = ((stboNd - n_bU / stbZgamC[1]) / n_eU[1] - (stboMd - m_bU / stbZgamC[1]) / m_eU[1]) * stbZgamS[1] / (n_eU[2] / n_eU[1] - m_eU[2] / m_eU[1])
                stbZerfmue0[1] = ((stboNd - n_bU / stbZgamC[1]) / n_eU[2] - (stboMd - m_bU / stbZgamC[1]) / m_eU[2]) * stbZgamS[1] / (n_eU[1] / n_eU[2] - m_eU[1] / m_eU[2])
            
            if abs(stbZmue0[1] - stbZmue0[2]) < stbkepse7 :
                stbZsymm = True
            else:
                stbZsymm = False
    Smue0opt(it_mue, mue_loop)
    while mue_loop and it_mue < stbkitmax:
        it_mue = it_mue + 1
        it_dehn = 1
        while (((it_dehn == 1 or (stboNd >= stbkepse5 or stboMd >= stbkepse5)) or (it_dehn == 2 and (stboNd <= -stbkepse5 or stboMd >= stbkepse5)) or it_dehn == 3 or abs(f_null[1]) > stbkepse7)) and it_dehn < stbkitmax:
            it_dehn = it_dehn + 1
            if it_dehn == 3 :
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
                if stbZsymm :
                    dehn[1] = stbodehnkrit[1]
                else:
                    dehn[1] = stbodehnkrit[2] - stbkepse3
                
            elif it_dehn == 4 and stbZsymm == False :
                fnull2 = f_null[1]
                dehn[1] = stbodehnkrit[2] + stbkepse3
            elif it_dehn == 5 and stbZsymm == False :
                fnull3 = f_null[1]
                if fnull2 * f_null[2] < 0 :
                    dehn[3] = stbodehnkrit[2] - stbkepse3
                    f_null[3] = fnull2
                    dehn[1] = (dehn[2] + dehn[3]) / 2
                elif fnull3 * f_null[3] < 0 :
                    dehn[2] = stbodehnkrit[2] + stbkepse3
                    f_null[2] = fnull3
                    dehn[1] = (dehn[2] + dehn[3]) / 2
                else:
                    dehn[1] = stbodehnkrit[3]
                
            else:
                Sitdehn(dehn, f_null, it_dehn)
            
            
            Sdehnepscs(dehn[1])
            n_bU = stbfRnbU()
            m_bU = stbfRmbU()

            n_eU[1] = stbfRneU1()
            m_eU[1] = stbfRmeU1()
            n_eU[2] = stbfRneU2()
            m_eU[2] = stbfRmeU2()
            if stbZsymm :
                if abs(n_eU[1] + n_eU[2] + m_eU[1] + m_eU[2]) > stbkepse7 :
                    stbZerfmue0[1] = stbZgamS[1] * (stboNd - n_bU / stbZgamC[1] + stboMd - m_bU / stbZgamC[1]) / (n_eU[1] + n_eU[2] + m_eU[1] + m_eU[2])
                else:
                    stbZerfmue0[1] = 1 / stbkepse7
                
                stbZerfmue0[2] = stbZerfmue0[1]
                f_null[1] = (m_eU[1] + m_eU[2]) * (stboNd - n_bU / stbZgamC[1]) - (n_eU[1] + n_eU[2]) * (stboMd - m_bU / stbZgamC[1])

            else:

                if abs(n_eU[1] + m_eU[1]) > stbkepse7 :
                    stbZerfmue0[1] = stbZgamS[1] * (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1] + stboMd - m_bU / stbZgamC[1] - stbZerfmue0[2] * m_eU[2] / stbZgamS[1]) / (n_eU[1] + m_eU[1])
                else:
                    stbZerfmue0[1] = 1 / stbkepse7
                
                f_null[1] = m_eU[1] * (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1]) - n_eU[1] * (stboMd - m_bU / stbZgamC[1] - stbZerfmue0[2] * m_eU[2] / stbZgamS[1])
        if stbZsymm and (it_dehn == stbkitmax or stbZerfmue0[1] < 0) and abs(stboNd) > stbkepse5 :
            if stboNd < -stbkepse5 and abs(stboeNd) < 0.5 - max(stboH[1], stboH[2]) / stboD :
                dehn[1] = -1
                bHlp = True
            elif stboNd > stbkepse5 and stboeNd < 0.5 - stbZ_H[1] / stboD :
                dehn[1] = 1
                bHlp = True
            else:
                bHlp = False
            
            if bHlp :
                Sdehnepscs(dehn[1])
                n_bU = stbfKnbU()
                m_bU = stbfKmbU()
                n_eU[1] = stbfRneU1()
                m_eU[1] = stbfRmeU1()
                n_eU[2] = stbfRneU2()
                m_eU[2] = stbfRmeU2()
                if abs(m_eU[1]) < stbkepse7 :
                    stbZerfmue0[2] = (stboMd - m_bU / stbZgamC[1]) / m_eU[2] * stbZgamS[1]
                    stbZerfmue0[1] = (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[2] * n_eU[2] / stbZgamS[1]) / n_eU[1] * stbZgamS[1]
                elif abs(m_eU[2]) < stbkepse7 :
                    stbZerfmue0[1] = (stboMd - m_bU / stbZgamC[1]) / m_eU[1] * stbZgamS[1]
                    stbZerfmue0[2] = (stboNd - n_bU / stbZgamC[1] - stbZerfmue0[1] * n_eU[1] / stbZgamS[1]) / n_eU[2] * stbZgamS[1]
                else:
                    stbZerfmue0[2] = ((stboNd - n_bU / stbZgamC[1]) / n_eU[1] - (stboMd - m_bU / stbZgamC[1]) / m_eU[1]) * stbZgamS[1] / (n_eU[2] / n_eU[1] - m_eU[2] / m_eU[1])
                    stbZerfmue0[1] = ((stboNd - n_bU / stbZgamC[1]) / n_eU[2] - (stboMd - m_bU / stbZgamC[1]) / m_eU[2]) * stbZgamS[1] / (n_eU[1] / n_eU[2] - m_eU[1] / m_eU[2])
                
                if abs(stbZmue0[1] - stbZmue0[2]) < stbkepse7 :
                    stbZsymm = True
                else:
                    stbZsymm = False
        Smue0opt(it_mue, mue_loop)
        if it_mue == stbkitmax : 
            stbZbFehler = True

    if stbobminBew and ((stbZerfmue0[1] <= stbomue0Riss[1] or stbZerfmue0[2] <= stbomue0Riss[2]) and (stbomue0Riss[1] > 20*stbkepse3 and stbomue0Riss[2] > 20*stbkepse3)) :
        stbZerfmue0[1] = stbomue0Riss[1]
        stbZerfmue0[2] = stbomue0Riss[2]
        stbZmue0[1] = stbZerfmue0[1]
        stbZmue0[2] = stbZerfmue0[2]
        Bruch_R()
    else:
        stbZRNd = n_bU / stbZgamC[1] + stbZerfmue0[1] * n_eU[1] / stbZgamS[1] + stbZerfmue0[2] * n_eU[2] / stbZgamS[1]
        stbZRMd = m_bU / stbZgamC[1] + stbZerfmue0[1] * m_eU[1] / stbZgamS[1] + stbZerfmue0[2] * m_eU[2] / stbZgamS[1]
    mimue0 = [[0,0,0,0,0],[0,0,0,0,0]]
    # print(Serfmue0_R)
    #print(stbZeps_c)
    


def Bruch_R():
    n_eU = [0,0,0]
    m_eU = [0,0,0]
    dehn = [0,0,0,0] 
    f_null = [0,0,0,0] 
    stbZiZ = 1

    eZug = stboeNd - stbfeBew()
    if stboNd < -stbkepse5 and abs(stboeNd) < stbkepse7 and (stbZmue0[1] + stbZmue0[2] < stbkepse7 or (stbobHkrit == False and abs(stbZmue0[1] - stbZmue0[2]) < stbkepse7)) :
        itmin = 0
    elif stboNd > stbkepse5 and (abs(eZug) < stbkepse7 or stboeNd < 0.5 - stbZ_H[1] / stboD) :
        itmin = 1
    else:
        itmin = 2

    dehnkrit = stboepscu / (stboepscu + stboepssu) - stbkepse5

    for it_dehn in range(0,stbkitmax):
        if it_dehn <= itmin or it_dehn == 3 or abs(f_null[1]) > stbkepse5:
            if it_dehn == 3 :
                dehn[3] = dehn[1]
                f_null[3] = f_null[1]
                dehn[1] = dehnkrit
            else:
                Sitdehn(dehn, f_null, it_dehn)
            Sdehnepscs(dehn[1])
            n_bU = stbfRnbU()
            m_bU = stbfRmbU()
            n_i = n_bU / stbZgamC[1]
            m_i = m_bU / stbZgamC[1]
            n_eU[1] = stbfRneU1()
            m_eU[1] = stbfRmeU1()
            n_i = n_i + stbZmue0[1] * n_eU[1] / stbZgamS[1]
            m_i = m_i + stbZmue0[1] * m_eU[1] / stbZgamS[1]
            n_eU[2] = stbfRneU2()
            m_eU[2] = stbfRmeU2()
            n_i = n_i + stbZmue0[2] * n_eU[2] / stbZgamS[1]
            m_i = m_i + stbZmue0[2] * m_eU[2] / stbZgamS[1]
            f_null[1] = stboMd * n_i - stboNd * m_i
        else:
            break

    if it_dehn == stbkitmax :
         stbZbFehler = True

    stbZRNd = n_bU / stbZgamC[1] + stbZmue0[1] * n_eU[1] / stbZgamS[1] + stbZmue0[2] * n_eU[2] / stbZgamS[1]
    stbZRMd = m_bU / stbZgamC[1] + stbZmue0[1] * m_eU[1] / stbZgamS[1] + stbZmue0[2] * m_eU[2] / stbZgamS[1]
    
    # print(Bruch_R)


def Gebrauch_R():
    eps0 = [0,0,0] 
    eps1= [0,0,0,0]
    eps2 = [0,0,0,0] 
    fnull_n= [0,0,0,0] 
    fnull_m = [0,0,0,0] 
    stbZiZ = 2
    if abs(stboNk) < stbkepse5 :
        eps0[1] = 0
    elif stboNk < 0 :
        it_n = 1
        eps2[1] = 0
        stbZepssk[1] = eps2[1]
        stbZepsck[1] = eps2[1]
        stbZepssk[2] = eps2[1]
        stbZepsck[2] = eps2[1]
        stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
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
            stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
            fnull_n[1] = stboNk - stbZRNk
        if it_n == stbkitmax : 
            stbZbFehler = True
        eps0[1] = eps2[1]                                                   
    else:
        Nkgr = stbZmue0[1] + stbZmue0[2]                                  
        if stboNk <= (stbZmue0[1] + stbZmue0[2]) * stbofyk / stboftk :
            eps0[1] = stboepssy * stboNk / (Nkgr * stbofyk / stboftk)       
        else:
            eps0[1] = stboepssy + (stboepssu - stboepssy) * (stboNk - (stbZmue0[1] + stbZmue0[2]) * stbofyk / stboftk) / (stbZnue0 * (1 - stbofyk / stboftk))            
        stbZepssk[1] = eps0[1]
        stbZepsck[1] = eps0[1]
        stbZepssk[2] = eps0[1]
        stbZepsck[2] = eps0[1]
    
    eps0[2] = eps0[1]
    stbZRMk = stbfalpha() * stbfRmbU() + stbZmue0[1] * stbfRmeU1() + stbZmue0[2] * stbfRmeU2()
    if stbZRMk > stboMk + stbkepse5 :
        if stboNk < 0 :
            eps0[2] = eps0[2] / 2
        else:
            eps0[1] = eps0[1] / 2

    it_m = 1
    it_ult = 1
    eps1[1] = eps0[1]
    it_n = 1
    eps2[1] = eps0[2]
    stbZepssk[1] = eps1[1]
    stbZepsck[1] = eps2[1]
    Sepsc2s2()
    stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
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
        stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
        fnull_n[1] = stboNk - stbZRNk
    stbZRMk = stbfalpha() * stbfRmbU() + stbZmue0[1] * stbfRmeU1() + stbZmue0[2] * stbfRmeU2()
    fnull_m[1] = stboMk - stbZRMk
    while abs(fnull_m[1]) > stbkepse5 and it_ult < stbkitmax:
        it_m = it_m + 1
        it_ult = it_ult + 1
        if it_m == 2 :
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
            
        else:
            if fnull_m[1] * fnull_m[2] < 0 :
                fnull_m[3] = fnull_m[1]
                eps1[3] = eps1[1]
            else:
                fnull_m[2] = fnull_m[1]
                eps1[2] = eps1[1]
            
            eps1[1] = (eps1[2] + eps1[3]) / 2
        
        it_n = 1
        eps2[1] = eps0[2]
        stbZepssk[1] = eps1[1]
        stbZepsck[1] = eps2[1]
        Sepsc2s2()
        stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
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
            stbZRNk = stbfalpha() * stbfRnbU() + stbZmue0[1] * stbfRneU1() + stbZmue0[2] * stbfRneU2()
            fnull_n[1] = stboNk - stbZRNk
        stbZRMk = stbfalpha() * stbfRmbU() + stbZmue0[1] * stbfRmeU1() + stbZmue0[2] * stbfRmeU2()
        fnull_m[1] = stboMk - stbZRMk
    if it_ult == stbkitmax : 
        stbZbFehler = True
    # print(Gebrauch_R)

def SigVor_R():
    mue01 = [0,0,0,0]
    eps2= [0,0,0,0]
    fnull_n= [0,0,0,0]
    fnull_m= [0,0,0,0]

    stbZiZ = 2

    if stboRissP1 <= stbofyk + 0.1 :
        stbZepssk[1] = stboRissP1 / (stbofyk / stboepssy)
    else:
        stbZepssk[1] = stboepssy + (stboepssu - stboepssy) * (stboRissP1 - stbofyk) / (stboftk - stbofyk)

    if stboNk < stbkepse5 :
        eps0 = 0
    else:
        eps0 = stbZepssk[1]

    if stboNk > stbkepse5 and abs(stboeNk - stbfeBew()) < stbkepse7 :
        stbZsymm = True
        stbZepsck[1] = stbZepssk[1]
        Sepsc2s2()
        mue01[1] = stboNk * stboftk / stboRissP1 / 2
        mue02 = mue01[1]
        stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
        stbZRMk = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()

        stbZmue0[1] = mue01[1]
        stbZmue0[2] = mue02

    elif stboNk > stbkepse5 and stboeNk < 0.5 - stbZ_H[1] / stboD  and (stbobHkrit or stbZsymm == False) :
        mue02 = stbZmue0[2]
        stbZepsck[1] = stbZepssk[1]
        Sepsc2s2()
        mue01[1] = stboNk * stboftk / stboRissP1 - mue02
        RMk0 = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
        stbZepsck[1] = 0
        Sepsc2s2()
        mue01[1] = (stboNk - mue02 * stbfRneU2()) / stbfRneU1()
        RMk1 = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
        if stboMk <= RMk0 :
            stbZepsck[1] = stbZepssk[1]
            Sepsc2s2()
            Det0 = stbfRmeU2() - stbfRmeU1()
            Det1 = stboNk * stboftk / stboRissP1 * stbfRmeU2() - stboMk
            Det2 = stboMk - stboNk * stboftk / stboRissP1 * stbfRmeU1()
            mue01[1] = Det1 / Det0
            mue02 = Det2 / Det0
            stbZRMk = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
            stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()

            stbZmue0[1] = mue01[1]
            stbZmue0[2] = mue02
        elif stboMk <= RMk1 :
            it_m = 1
            eps2[1] = eps0
            stbZepsck[1] = eps2[1]
            Sepsc2s2()
            it_n = 1
            it_ult = 1
            mue01[1] = stbZmue0[1]  
            stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
            fnull_n[1] = stboNk - stbZRNk
            while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
                it_n = it_n + 1
                it_ult = it_ult + 1
                if it_n == 2 :
                    fnull_n[2] = fnull_n[1]
                    mue01[2] = mue01[1]
                    mue01[1] = 2 * mue01[1]
                elif it_n == 3 :
                    if fnull_n[1] * fnull_n[2] > 0 :
                        it_n = 2
                        fnull_n[2] = fnull_n[1]
                        mue01[2] = mue01[1]
                        mue01[1] = 2 * mue01[1]
                    else:
                        fnull_n[3] = fnull_n[1]
                        mue01[3] = mue01[1]
                        mue01[1] = (mue01[2] + mue01[3]) / 2
                    
                else:
                    if fnull_n[1] * fnull_n[2] < 0 :
                        fnull_n[3] = fnull_n[1]
                        mue01[3] = mue01[1]
                    else:
                        fnull_n[2] = fnull_n[1]
                        mue01[2] = mue01[1]
                    mue01[1] = (mue01[2] + mue01[3]) / 2
                stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
                fnull_n[1] = stboNk - stbZRNk
            stbZRMk = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
            fnull_m[1] = stboMk - stbZRMk
            while abs(fnull_m[1]) > stbkepse5 and it_m < stbkitmax:
                it_m = it_m + 1    
                if it_m == 2 :
                    fnull_m[2] = fnull_m[1]
                    eps2[2] = eps2[1]
                    eps2[1] = 0
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
                it_n = 1
                it_ult = 1
                mue01[1] = stbZmue0[1]  
                stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
                fnull_n[1] = stboNk - stbZRNk
                while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
                    it_n = it_n + 1
                    it_ult = it_ult + 1
                    if it_n == 2 :
                        fnull_n[2] = fnull_n[1]
                        mue01[2] = mue01[1]
                        mue01[1] = 2 * mue01[1]
                    elif it_n == 3 :
                        if fnull_n[1] * fnull_n[2] > 0 :
                            it_n = 2
                            fnull_n[2] = fnull_n[1]
                            mue01[2] = mue01[1]
                            mue01[1] = 2 * mue01[1]
                        else:
                            fnull_n[3] = fnull_n[1]
                            mue01[3] = mue01[1]
                            mue01[1] = (mue01[2] + mue01[3]) / 2
                        
                    else:
                        if fnull_n[1] * fnull_n[2] < 0 :
                            fnull_n[3] = fnull_n[1]
                            mue01[3] = mue01[1]
                        else:
                            fnull_n[2] = fnull_n[1]
                            mue01[2] = mue01[1]
                        mue01[1] = (mue01[2] + mue01[3]) / 2
                    stbZRNk = mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
                    fnull_n[1] = stboNk - stbZRNk
                stbZRMk = mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
                fnull_m[1] = stboMk - stbZRMk
            if it_ult == stbkitmax :
                stbZbFehler = True
            else:
                stbZmue0[1] = mue01[1]
                stbZmue0[2] = mue02
    elif stbZsymm == True :
        it_n = 1
        it_ult = 1
        mue01[1] = stbZmue0[1] 
        mue02 = mue01[1]
        it_m = 1
        eps2[1] = eps0
        stbZepsck[1] = eps2[1]
        Sepsc2s2()
        stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
        fnull_m[1] = stboMk - stbZRMk
        while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax:
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
            stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
            fnull_m[1] = stboMk - stbZRMk
        stbZRNk = stbfalpha() * stbfRnbU() + mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
        fnull_n[1] = stboNk - stbZRNk
        while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
            it_n = it_n + 1
            it_ult = it_ult + 1
            if it_n == 2 :
                if it_m == stbkitmax :    
                    it_n = 1
                else:
                    fnull_n[2] = fnull_n[1]
                    mue01[2] = mue01[1]
                
                mue01[1] = 2 * mue01[1]
            elif it_n == 3 :
                if fnull_n[1] * fnull_n[2] > 0 :
                    it_n = 2
                    fnull_n[2] = fnull_n[1]
                    mue01[2] = mue01[1]
                    mue01[1] = 2 * mue01[1]
                else:
                    fnull_n[3] = fnull_n[1]
                    mue01[3] = mue01[1]
                    mue01[1] = (mue01[2] + mue01[3]) / 2
                
            else:
                if fnull_n[1] * fnull_n[2] < 0 :
                    fnull_n[3] = fnull_n[1]
                    mue01[3] = mue01[1]
                else:
                    fnull_n[2] = fnull_n[1]
                    mue01[2] = mue01[1]
                
                mue01[1] = (mue01[2] + mue01[3]) / 2
            
            mue02 = mue01[1]
            it_m = 1
            eps2[1] = eps0
            stbZepsck[1] = eps2[1]
            Sepsc2s2()
            stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
            fnull_m[1] = stboMk - stbZRMk
            while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax:
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
                stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
                fnull_m[1] = stboMk - stbZRMk
            stbZRNk = stbfalpha() * stbfRnbU() + mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
            fnull_n[1] = stboNk - stbZRNk
        
        if it_ult == stbkitmax :
            stbZbFehler = True
        else:
            stbZmue0[1] = mue01[1]
            stbZmue0[2] = mue02
    mue02 = stbZmue0[2]
    it_n = 1
    it_ult = 1
    mue01[1] = stbZmue0[1]
    it_m = 1
    eps2[1] = eps0
    stbZepsck[1] = eps2[1]
    Sepsc2s2()
    stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
    fnull_m[1] = stboMk - stbZRMk
    while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax: 
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
        stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
        fnull_m[1] = stboMk - stbZRMk
    stbZRNk = stbfalpha() * stbfRnbU() + mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
    fnull_n[1] = stboNk - stbZRNk
    while abs(fnull_n[1]) > stbkepse5 and it_ult < stbkitmax:
        it_n = it_n + 1
        it_ult = it_ult + 1
        if it_n == 2 :
            if it_m == stbkitmax :   
                it_n = 1
            else:
                fnull_n[2] = fnull_n[1]
                mue01[2] = mue01[1]
            
            mue01[1] = 2 * mue01[1]
        elif it_n == 3 :
            if fnull_n[1] * fnull_n[2] > 0 :
                it_n = 2
                fnull_n[2] = fnull_n[1]
                mue01[2] = mue01[1]
                mue01[1] = 2 * mue01[1]
            else:
                fnull_n[3] = fnull_n[1]
                mue01[3] = mue01[1]
                mue01[1] = (mue01[2] + mue01[3]) / 2
            
        else:
            if fnull_n[1] * fnull_n[2] < 0 :
                fnull_n[3] = fnull_n[1]
                mue01[3] = mue01[1]
            else:
                fnull_n[2] = fnull_n[1]
                mue01[2] = mue01[1]
            
            mue01[1] = (mue01[2] + mue01[3]) / 2
        
        it_m = 1
        eps2[1] = eps0
        stbZepsck[1] = eps2[1]
        Sepsc2s2()
        stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
        fnull_m[1] = stboMk - stbZRMk
        while abs(fnull_m[1]) > stbkepse7 and it_m < stbkitmax: 
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
            stbZRMk = stbfalpha() * stbfRmbU() + mue01[1] * stbfRmeU1() + mue02 * stbfRmeU2()
            fnull_m[1] = stboMk - stbZRMk
        stbZRNk = stbfalpha() * stbfRnbU() + mue01[1] * stbfRneU1() + mue02 * stbfRneU2()
        fnull_n[1] = stboNk - stbZRNk

    if it_ult == stbkitmax :
        stbZbFehler = True
    else:
        stbZmue0[1] = mue01[1]
        stbZmue0[2] = mue02
    # print("SIGVOR_r")

def BruchC1S1():
    Nui = [0,0,0]
    Mui = [0,0,0]

    if stboNorm == 0:
        SgamC1()
    elif stboNorm > 0:
        if stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2] > stbZmue0[0] + stbZmue0[1] + stbZmue0[2] + stbkepse7:
            stbZgamC[1] = stbogamC[1]+(stbogamC[0] - stbogamC[1]) * (1 - (stbZmue0[0] + stbZmue0[1] + stbZmue0[2]) / (stbomue0Druc[0] + stbomue0Druc[1] + stbomue0Druc[2]))
        else:
            stbZgamC[1] = stbogamC[1]
        
        stbZgamS[1] = stbogamS[1]
    

    Bruch_R()
    
    Nui[0] = stbfRnbU()
    Mui[0] = stbfRmbU()
    stbZNucs[0] = Nui[0] / stbZgamC[1]
    if Nui[0] < -stbkepse7:
        stbZzi[0] = Mui[0] / Nui[0] * stboD
    else:
        stbZzi[0] = 0
    
    stbZNucs[1] = 0
    stbZNucs[2] = 0
    stbZzi[1] = 0
    stbZzi[2] = 0
    Nui[1] = stbfRneU1()
    Mui[1] = stbfRmeU1()
    Nui[2] = stbfRneU2()
    Mui[2] = stbfRmeU2()
    if stbZmue0[1] > stbkepse7:
        if Nui[1] > stbkepse7:
            stbZNucs[1] = stbZNucs[1] + stbZmue0[1] * Nui[1] / stbZgamS[1]
            stbZzi[1] = (stbZzi[1] * stbZNucs[1] + Mui[1] / Nui[1] * stboD * stbZmue0[1] * Nui[1] / stbZgamS[1]) / stbZNucs[1]
        elif Nui[1] < -stbkepse7:
            stbZNucs[2] = stbZNucs[2] + stbZmue0[1] * Nui[1] / stbZgamS[1]
            stbZzi[2] = (stbZzi[2] * stbZNucs[2] + Mui[1] / Nui[1] * stboD * stbZmue0[1] * Nui[1] / stbZgamS[1]) / stbZNucs[2]
        
    
    if stbZmue0[2] > stbkepse7:
        if Nui[2] < -stbkepse7:
            stbZNucs[2] = stbZNucs[2] + stbZmue0[2] * Nui[2] / stbZgamS[1]
            stbZzi[2] = (stbZzi[2] * stbZNucs[2] + Mui[2] / Nui[2] * stboD * stbZmue0[2] * Nui[2] / stbZgamS[1]) / stbZNucs[2]
        elif Nui[2] > stbkepse7:
            stbZNucs[1] = stbZNucs[1] + stbZmue0[2] * Nui[2] / stbZgamS[1]
            stbZzi[1] = (stbZzi[1] * stbZNucs[1] + Mui[2] / Nui[2] * stboD * stbZmue0[2] * Nui[2] / stbZgamS[1]) / stbZNucs[1]
        
    if stbZNucs[0] < -stbkepse7 and stbZNucs[1] > stbkepse7:
        zD = (stbZzi[0] * stbZNucs[0] + stbZzi[2] * stbZNucs[2]) / (stbZNucs[0] + stbZNucs[2])
        stbZNucs[3] = min(abs(stbZNucs[0] + stbZNucs[2]), stbZNucs[1])
        stbZzi[3] = stbZzi[1] - zD
    else:
        stbZNucs[3] = 0
        stbZzi[3] = 0
    #print(BruchC1S1)


def stbfAcc():
    if stbZepscd[2] < stbkepse7:
        stbfAcc = stboRB * stboD
        
    elif stbZepscd[1] > -stbkepse7:
        stbfAcc = 0
    else:
        xgr = stboD * stbZepscd[1] / (stbZepscd[1] - stbZepscd[2])
        stbfAcc = stboRB * xgr
    return stbfAcc

def stbfzi():
    mue1 = 0
    mue2 = 0
    SRechenWerteZ(1)
    mue1 = stbZmue0[1] 
    mue2 = stbZmue0[2] 
    
    stbfzi = stbZzi[3]
    if stbZepscd[1] > -stbkepse5 and mue1 > stbkepse7 and mue2 > stbkepse7:
        stbfzi = stboHQ - stbZ_H[1] - stbZ_H[2]
    else:
        stbfzi = max(stbfzi, 0.9 * (stboHQ - stbZ_H[1]))
        stbfzi = min(stbfzi, max(stboHQ - 2 * stbZ_H[2], stboHQ - stbZ_H[2] - 0.03))
    return stbfzi


def QuerBemessN0():
    f_ctd = stbffctm() / stbZgamC[1]                                                         
    Nd1 = stboNd * stboRB * stboD * stbofck
    Qd = stboQd * stboRB * stboD * stbofck
    vormue1 = stbZmue0[1]
    Rctd = f_ctd * stboRB * stboD
    

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
            stbZtau0 = Qd / stbfAcc()
            sig_x = Nd1 / stbfAcc()
            stbZtau0 = sig_x / 2 + math.sqrt((sig_x / 2) ** 2 + stbZtau0 ** 2)
        else:
            stbZtau0 = Qd / stboBQ / stbfzi()
        

        if stbZtau0 <= stbotau012:
            if Nd1 > Rctd:
                tau = stbZtau0
            else:
                tau = 0.4 * stbZtau0
                if Nd1 > 0:
                    tau = tau + (stbZtau0 - tau) * Nd1 / Rctd
                
            
        elif stbZtau0 <= stbotau02:
            if Nd1 > Rctd:
                tau = stbZtau0
            else:
                tau = max(stbZtau0 ** 2 / stbotau02, 0.4 * stbZtau0)
                if Nd1 > 0:
                    tau = tau + (stbZtau0 - tau) * Nd1 / Rctd
                
            
        elif stbZtau0 <= stbotau03:
            if stbZepscd[1] > -stbkepse5:
                tau = -1
            else:
                tau = stbZtau0
            
        else:
            tau = -1
        
        if tau <= -0.5:
            stbZerfas = -1
        else:
            stbZerfas = tau * stboBQ / (stbofyk / stbogamS[1]) * 10000
    #print(QuerBemessN0)


def QuerBemessN123():
    zi = 0
    SRechenWerteZ(1)
    f_cd = stbofck / stbZgamC[1]                                                                
    f_ctd = stbffctm() / stbZgamC[1]                                                            
    f_yd = stbofyk / stbogamS[1]                                                                
    Nd1 = stboNd * stboRB * stboD * stbofck
    Qd = stboQd * stboRB * stboD * stbofck
    vormue1 = stbZmue0[1]
    Rctd = f_ctd * stboRB * stboD

    if vormue1 < stbkepse7:
        if stboNorm == 1:
            sigcp = -Nd1 / stboBQ / stboHQ                                                      
        elif stboNorm == 2 or stboNorm == 3:
            sigcp = -Nd1 / stbfAcc()                                                             
                                                                                         
        if stboNorm == 1:
            stbZtaucp = 1.5 * Qd / stboBQ / stboHQ                                             
            stbZfcvd = math.sqrt(f_ctd ** 2 + sigcp * f_ctd)                                         
        elif stboNorm == 2 or stboNorm == 3:
            stbZtaucp = 1.5 * Qd / stbfAcc()                                                   
            sig_clim = f_cd - 2 * math.sqrt(f_ctd * (f_ctd + f_cd))                               
            if sigcp <= sig_clim:                                                         
                stbZfcvd = math.sqrt(f_ctd ** 2 + sigcp * f_ctd)
            else:
                stbZfcvd = math.sqrt(max(f_ctd ** 2 + sigcp * f_ctd - (sigcp - sig_clim) ** 2 / 4, 0))
            
            stbZVRdc = stbfAcc() * stbZfcvd / 1.5
    
        stbZminas = 0
        if Qd <= stbZVRdc + stbkepse5:
            stbZerfas = 0
        else:
            stbZerfas = -1
    else:
        zi = stbfzi()
        DQ = stboHQ - stbZ_H[1]                                          
        sigcp = -Nd1 / stboBQ / stboHQ                                           
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
        if stboNorm == 1 or stboNorm == 3:
            nue1 = 0.75                                                                        
        elif stboNorm == 2:
            nue1 = 0.6                                                                   
        
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
        if stboNorm == 1 or stboNorm == 3:                                                  
            stbZminas = 0.16 * stbffctm() / stbofyk * stboBQ * 10000                           
        elif stboNorm == 2:
            stbZminas = 0.08 * math.sqrt(stbofck) / stbofyk * stboBQ * 10000                        
        if Qd <= stbZVRdc + stbkepse5:
            stbZerfas = stbZminas
        elif Qd <= stbZVRdmax + stbkepse5:
            stbZerfas = Qd / f_yd / zi / stbZcottheta * 10000
            if stbZerfas < stbZminas:
                stbZerfas = stbZminas
                if stbZcottheta > 1 + stbkepse5 and stbomaxcottheta <= stbkepse3:
                    stbZcottheta = max(Qd / f_yd / zi / stbZerfas * 10000, 1)           
                    stbZVRdmax = stboBQ * zi * nue1 * f_cd / (stbZcottheta + 1 / stbZcottheta) 
        else:
            stbZerfas = -1
    #print( QuerBemessN123)


if __name__ == "__main__":
    for i in range(11,29):
        print(StB_R_MN(3,1.5,1.15,26616.89535,0,19716.2191,0,1500,2500,100,100,False,5,5,25,0.85,0.002,0.0035,2,0.15,"0.15 0",500,520,200000,0.025,200,1,i))
    for i in range(11,24):
        print(i,StB_R_Q(3,1.5,1.15,26616.89535,0,1229,1500,2500,100,100,5,5,25,0.85,0.002,0.0035,2,0.15,"0.15 0",500,520,200000,0.025,0,0,0,i))
    As1 = StB_R_MN(3,1.5,1.15,4.25388051219,0.0,3.15102260162,0,800.0,2800.0,100.0,100.0,False,5,5,35.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,240.0,1,17)
    As2 = StB_R_MN(3,1.5,1.15,4.25388051219,0.0,3.15102260162,0,800.0,2800.0,100.0,100.0,False,5,5,35.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,240.0,1,18)
    asl = StB_R_Q(3,1.5,1.15,4.25388051219,0.0,36.8160369762,800.0,2800.0,100.0,100.0,As1,As2,35.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,0,0,0,19)
    print(As1,As2,asl)
    t = StB_R_MN(3,1.5,1.15,-377.603311774,0,-188.801655887,0,500.0,2500.0,100.0,100.0,False,5,5,25.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,300.0,2,18)
    k = StB_R_MN(3,1.5,1.15,14601.3484044,0,10815.8136329,0,1800,2500,100,100,False,5,5,30,0.85,0.002,0.0035,2,0.15,"0.15 0",500,520,200000,0.025,300,1,17)
    print(t,k)
    print(StB_R_Q(3,1.5,1.15,8841.43665144,0,-5361.23283345,1800.0,2500.0,100.0,100.0,0,0,30.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,0,0,0,19))
    StB_R_MN(3,1.5,1.15,-377.603311774,0,-188.801655887,0,500.0,2500.0,100.0,100.0,False,5,5,25.0,0.85,0.002,0.0035,2.0,0.15,"0.15 0",500.0,520.0,200000.0,0.025,300.0,2,17)