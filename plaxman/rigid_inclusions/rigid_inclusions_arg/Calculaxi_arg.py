import numpy as np
from scipy.stats import hmean
#import Module1
from plaxman.rigid_inclusions.rigid_inclusions_arg import Module1
#import GlobalVar_CMC_Slab as var
import plaxman.rigid_inclusions.rigid_inclusions_arg.GlobalVar_CMC_Slab as var
import time


def Found_a(wqp1):
    a_diffa = [0,0]
    for i in range (0,201):
        a_diffa[0] = i*wqp1/200
        matrice = Module1.Calcul(a_diffa[0])
        a_diffa[1] = matrice[0][29]
        index = matrice[1][29]
        if index == 0:
            break
    return a_diffa

def Found_b(wqp2):
    b_diffb = [0,0]
    fact = 10
    for j in range (0,11):
        b_diffb[0] = fact * wqp2 - j * (fact - 1) * wqp2 / 10
        matrice = Module1.Calcul(b_diffb[0])
        b_diffb[1] = matrice[0][29]
        index = matrice[1][29]
        if index == 0:
            break
    return b_diffb


def Solver (a,b,diffa):
    m = (a+b)/2
    matrice = Module1.Calcul(m)
    diffm = matrice[0][29]
    if ((diffm * diffa) > 0) :
        a = m
        matrice = Module1.Calcul(a)
        diffa = matrice[0][29]
    else:
        b = m

    nit = 0
    while ((matrice[2][29] > var.e1) or (matrice[3][29] > var.e2)) and (nit < 100):
        m = (a+b)/2
        matrice = Module1.Calcul(m)
        diffm = matrice[0][29]
        if ((diffm * diffa) > 0) :
            a = m
            matrice = Module1.Calcul(a)
            diffa = matrice[0][29]
        else:
            b = m
        nit += 1

    return m


def Calcul_Click(Parametres_matrix,Q_p_plus,gamma_eq_ULS,Eoed_If,Dc,qb,kq,Emc,h,Hm,Hlim,Hw,dq,As,Ec,dQ_Hm,Etat,e1,e2,wqp1,wqp2,Eoeda):
    var.Eoed_If = Eoed_If #R86
    var.Dc = Dc #C40
    var.Rc = Dc/2
    var.qb = qb #C56
    var.k = kq #C57
    var.kq = kq #C57
    var.Emc = Emc #C58
    var.h = h #C39
    var.Hm = Hm #c75
    var.Hlim = Hlim #C82
    var.Hw = Hw #C83
    var.dq = dq #I116
    var.Amaille = As #C71
    var.Ec = Ec #C50
    var.dQ_Hm = dQ_Hm #U114 #dQ_+IF(W76="A",R80,0)
    var.dQ_ = dq*As
    #var.qp = 0.0
    var.Etat = Etat #W76 #10 if E or 0 if null
    var.e1 = e1
    var.e2 = e2
    var.wqp1 = wqp1
    var.wqp2 = wqp2
    #var.Eoeda = Eoeda
    var.Parametres = Parametres_matrix
    #------------------------------------------------------
    #start_time = time.time()
    var.wqp1 = var.qb*var.Dc/(2*var.kq*var.Emc)
    var.wqp2 = 6*var.wqp1
    #output R86 CA

    a_diffa = Found_a(var.wqp1)
    a = a_diffa[0]
    diffa = a_diffa[1]
    b_diffb = Found_b(var.wqp2)
    b = b_diffb[0]
    diffb = b_diffb[1]
    pb = 0   
    if diffa > 0 or diffb < 0:
        pb = 1 
    else:
        m = Solver(a,b,diffa)
        var.matrice = Module1.Calcul(m)
        temp = m
        #outputs Y117 and B19(201,29) CA
        if var.Hm == 0:
            pass
        else:
            #application saved to workbook
            Eoedb = 1000
            col_6 = [row[6] for row in var.matrice]
            line_idx = col_6.index(0.0)
            Q_p = var.matrice[line_idx][18] # Load applied at inclusion head
            #print('Calculaxis_arg Q_p: ', Q_p)
            R87 = Q_p_plus/gamma_eq_ULS - Q_p
            #print(line_idx)
            #print(R87)
            var.diffEoeda = R87
            var.R87 = R87  #diff Qp, = (Qp*(hm)/Veq,ULs) - load applied on inclusion head ((LTP!C192)/M114)-F140
            var.diffEoedm = R87
            for n in range (0,16):
                if var.diffEoeda > 0 : 
                    break
                #if var.R87 <0.1 and var.R87>0:
                if var.R87 > 0.1 or var.R87 < 0:
                    Eoedm = (Eoeda + Eoedb) / 2
                    #Sheets("Calcul axi").Range("R86") = Eoedm
                    var.Eoed_If = Eoedm

                    a_diffa = Found_a(var.wqp1)
                    a = a_diffa[0]
                    diffa = a_diffa[1]

                    b_diffb = Found_b(var.wqp2)
                    b = b_diffb[0]
                    diffb = b_diffb[1]

                    pb = 0
                    if ((diffa > 0) or (diffb < 0)) :
                        pb = 1
                        break
                    else:
                        m = Solver(a, b, diffa)
                        var.matrice = Module1.Calcul(m)
                        temp = m
                        #Sheets("Calcul axi").Range("Y117") = m
                        #Sheets("calcul").Range("B19").Resize(201, 29) = matrice
                    #Application.Calculation = xlCalculationAutomatic
                    col_6 = [row[6] for row in var.matrice]
                    line_idx = col_6.index(0.0)
                    Q_p = var.matrice[line_idx][18] # Load applied at inclusion head
                    R87 = Q_p_plus/gamma_eq_ULS - Q_p
                    var.diffEoedm = R87
                    var.R87 = R87
                    #Application.Calculation = xlCalculationManual
                    if ((var.diffEoedm * var.diffEoeda) > 0) :
                        Eoeda = Eoedm
                        #Sheets("Calcul axi").Range("R86") = Eoeda
                        var.Eoed_If = Eoeda

                        var.diffEoeda = var.diffEoedm
                    else:
                        Eoedb = Eoedm
                        #Sheets("Calcul axi").Range("R86") = Eoedb
                        var.Eoed_If = Eoedb
    ##ref
    ##Application.Calculation = xlCalculationManual
    #if var.U121 > var.V121/100 or var.U122 > var.V122/100 :
    #    pb = 1
    #if pb != 0 :
        #print ("ERROR")
    #stoptime = time.time()
    #elapsedtime = stoptime-start_time

    #return temp, var.matrice    #!! temp, reference before assignment
    return var.matrice
                        

def get_unreinforced_soil_settlement(Parameteres_FDC, Eoed_unreinforced, Parameteres_below_FDC, q, gammaSat_LTP, Ey_LTP, nu_LTP, Hc, hM, Hlim, Hw, dq, Etat):#Hc - C39
    """ Gets unreinforced soil settlement
    q = dq + gamma_LTP*hM: surcharge + LTP weight
    Eoed_unreinforced: stress-dependent soil Eoed within FDC
    """
    E_list = Parameteres_below_FDC[:, 6]    # Eoed
    #Hw,Hm,N87
    #find gamma first
    if Hw >= hM:
        gamma =  gammaSat_LTP
    else:
        if Hw <=0:
            gamma = gammaSat_LTP - 10
        else:
            gamma = (Hw*gammaSat_LTP + (hM-Hw)*(gammaSat_LTP-10))/hM
    
    #R79
    R79 = gamma*hM

    # Calculate reinforced settlement at the surface
    if Etat == 10:
        temp = 0
    else:
        temp = R79/2

    Depth = Parameteres_FDC[:, 0]
    #E_val = Parameteres_FDC[:200, 6]    # Eoed
    E_val = Eoed_unreinforced
    i = 0
    while Depth[i] <= hM:
        i = i+1
    #print(i)
    #print(E_val[i:])
    Mean26 = hmean(E_val[i:])
    Mean19 = hmean(E_list)
    #print('Mean26: ', Mean26)
    #print('Mean19: ', Mean19)
    #w_top = (temp+dq)*(hM/(Ey_LTP*((1-nu_LTP)/((1+nu_LTP)*(1-2*nu_LTP)))))*1000+(temp+dq)*((Hc-hM)/Mean26+(Hlim-Hc)/Mean19)*1000
    w_top = dq*(hM/(Ey_LTP*((1-nu_LTP)/((1+nu_LTP)*(1-2*nu_LTP)))))*1000 + dq*((Hc-hM)/Mean26+(Hlim-Hc)/Mean19)*1000

    # Calculate (unreinforced) settlement from below FDC until the end of the considered depth H_lim
    Parameteres_below_FDC = np.c_[Parameteres_below_FDC, np.zeros(Parameteres_below_FDC.shape[0])]    # stack a column to Parameteres for keeping settlement
    for i in range(Parameteres_below_FDC.shape[0]-2, -1, -1):
        delta_z_i = Parameteres_below_FDC[i, 1] - Parameteres_below_FDC[i, 0]
        E_oed = Parameteres_below_FDC[i, 6]
        u_i = dq*delta_z_i/E_oed * 1000
        Parameteres_below_FDC[i, -1]  = Parameteres_below_FDC[i+1, -1] + u_i

    # Calculate unreinforced settlement within FDC
    Parameteres_FDC = np.c_[Parameteres_FDC, np.zeros(Parameteres_FDC.shape[0])]    # stack a column to Parameteres for keeping settlement
    Parameteres_FDC[-1, -1] = Parameteres_below_FDC[0, -1]
    for i in range(Parameteres_FDC.shape[0]-2, -1, -1):
        delta_z_i = Parameteres_FDC[i, 1] - Parameteres_FDC[i, 0]
        #E_oed = Parameteres_FDC[i, 6]
        E_oed = Eoed_unreinforced[i]
        u_i = dq*delta_z_i/E_oed * 1000
        Parameteres_FDC[i, -1]  = Parameteres_FDC[i+1, -1] + u_i


    return w_top, Parameteres_below_FDC, Parameteres_FDC

