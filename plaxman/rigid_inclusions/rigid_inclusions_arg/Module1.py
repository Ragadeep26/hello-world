import numpy
#import GlobalVar_CMC_Slab as var
import plaxman.rigid_inclusions.rigid_inclusions_arg.GlobalVar_CMC_Slab as var
#--------------------------------------------------#
#                      CALCUL                      #
#--------------------------------------------------#
def Calcul(wqp):
    #var.matrice = matrice = [[0.0 for i in range (0,30)] for i in range(0,201)]
    if wqp <= var.qb * var.Dc / (2 * var.k * var.Emc) :
        qp = var.k * var.Emc / var.Dc * wqp
    elif wqp <= 3 * var.qb * var.Dc / (var.k * var.Emc) :
        qp = var.k * var.Emc / (5 * var.Dc) * wqp + 2 / 5 * var.qb
    else:
        qp = var.qb
    Gqp = numpy.pi * var.Rc * var.Rc * qp
    #0-Toit de la tranche i
    for i in range(0,201) :
        var.matrice[i][0] = var.Parametres[i][0]

    #1-Test : Si le long de la colonne -> 1 sinon -> 0
    for i in range (1,201) :
        if var.matrice[i][0] > var.h :
            var.matrice[i][1] = 0
        else:
            var.matrice[i][1] = 1
        
    #2-Si le long de la colonne -> incrémente sinon -> 0
    var.matrice[200][2] = 1
    for i in range (1,201) :
        var.matrice[200 - i][2] = var.matrice[200 - i + 1][2] + var.matrice[200 - i][1]

    #3-Module pressio
    for i in range(0,201) :
        var.matrice[i][3] = var.Parametres[i][1]

    #4-Module de Young
    for i in range(0,201) :
        var.matrice[i][4] = var.Parametres[i][2]

    #5-Module oedometrique
    for i in range(0,201) :
        var.matrice[i][5] = var.Parametres[i][3]

    #6-Module de Young dans la colonne fictive
    for i in range(0,201) :
        if var.matrice[i][0] < var.Hm :
            var.matrice[i][6] = var.Eoed_If
        else:
            var.matrice[i][6] = 0
        

    #7-Frottement lateral unitaire qs
    for i in range(0,201) :
        var.matrice[i][7] = var.Parametres[i][4]

    #8-2nd coeff de Frank et Zhao K#
    for i in range(0,201) :
        var.matrice[i][8] = var.Parametres[i][5]

    #9-Poids volumique#
    for i in range(0,201) :
        var.matrice[i][9] = var.Parametres[i][6]

    #10-Ktan_delta#
    for i in range(0,201) :
        var.matrice[i][10] = var.Parametres[i][7]

    #11-Poids volumique déjaugé#
    for i in range(0,200) :
        if var.Hw == var.Hlim :
            var.matrice[i][11] = var.matrice[i][9]
        else:
            if var.matrice[i][0] >= var.Hw :
                var.matrice[i][11] = var.matrice[i][9] - 10
            else:
                if var.matrice[i + 1][0] <= var.Hw :
                    var.matrice[i][11] = var.matrice[i][9]
                else:
                    var.matrice[i][11] = var.matrice[i][9] * (var.Hw - var.matrice[i][0]) + (var.matrice[i][9] - 10) *(var.matrice[i + 1][0] - var.Hw) / (var.matrice[i + 1][0] - var.matrice[i][0])
                
    #dQmaille#
    if var.Etat == 10:
        for i in range(0,201) :
            var.dQ_mat[i] = var.dQ_

    else:
        var.dQ_mat[0] = var.dQ_
        for i in range (0,201) :
            if var.matrice[i][0] <= var.Hm :
                var.dQ_mat[i] = var.dQ_mat[i - 1] + (var.matrice[i][0] - var.matrice[i - 1][0]) * var.matrice[i][11] * var.Amaille
            else:
                var.dQ_mat[i] = var.dQ_Hm

    #13-Sigma_v0#
    var.matrice[0][13] = 0
    if var.Etat == 10 or var.Hm == 0 :
        for i in range (1,201) :
            var.matrice[i][13] = var.matrice[i - 1][11] * (var.matrice[i][0] - var.matrice[i - 1][0]) + var.matrice[i - 1][13]
    else:
        for i in range (1,201) :
            if var.matrice[i][0] <= var.Hm :
                var.matrice[i][13] = 0
            else:
                var.matrice[i][13] = var.matrice[i - 1][11] * (var.matrice[i][0] - var.matrice[i - 1][0]) + var.matrice[i - 1][13]
        
    if wqp < 0 :
        var.matrice[1][29] = 1
        Calcul = var.matrice
        return

    var.matrice[200][16] = 0
    var.matrice[200][17] = 0
    var.matrice[200][18] = Gqp
    var.matrice[200][22] = var.matrice[200][18] / (numpy.pi * var.Rc * var.Rc)
    var.matrice[200][23] = var.dQ_mat[200] - var.matrice[200][18]
    var.matrice[200][24] = var.matrice[200][23] / (var.Amaille - numpy.pi * var.Rc * var.Rc)
    var.matrice[200][25] = 0
    var.matrice[200][26] = wqp
    var.matrice[200][27] = 0
    var.matrice[200][28] = 0

    for ni in range (1,61) :
        
        #12-Tassement relatif entre sol et CMC
        for i in range(0,201) :
            if ni == 1 :
                var.matrice[200 - i][12] = wqp
            else:
                var.matrice[200 - i][12] = var.matrice[200 - i][26] - var.matrice[200 - i][28]
            
        #15-Taux de frottement mobilisé maximal
        for i in range(0,201) :
            if var.matrice[200 - i][0] < var.Hm :
                if ni == 1 :
                    var.matrice[200 - i][15] = var.matrice[200 - i][10] * (var.dq + var.matrice[200 - i][13])
                elif var.matrice[200 - i][12] >= 0 :
                    var.matrice[200 - i][15] = var.matrice[200 - i][10] * (var.matrice[200 - i][24] + var.matrice[200 - i][13])
                else:
                    var.matrice[200 - i][15] = -var.matrice[200 - i][10] * (var.matrice[200 - i][24] + var.matrice[200 - i][13]) 
                
            elif var.matrice[200 - i][12] >= 0 :
                var.matrice[200 - i][15] = var.matrice[200 - i][7]
            else:
                var.matrice[200 - i][15] = -var.matrice[200 - i][10] * (var.matrice[200 - i][24] + var.matrice[200 - i][13])
            

        
        #14-Taux de frottement mobilisé
        for i in range(0,201) :
            #print( (2 * var.matrice[200 - i][8] * var.matrice[200 - i][3]))
            if abs(var.matrice[200 - i][12]) <= abs(var.matrice[200 - i][15]) * var.Dc / (2 * var.matrice[200 - i][8] * var.matrice[200 - i][3]) :
                var.matrice[200 - i][14] = var.matrice[200 - i][8] * var.matrice[200 - i][3] / var.Dc * var.matrice[200 - i][12]
            elif abs(var.matrice[200 - i][12]) <= 3 * abs(var.matrice[200 - i][15]) * var.Dc / (var.matrice[200 - i][8] * var.matrice[200 - i][3]) :
                var.matrice[200 - i][14] = var.matrice[200 - i][8] * var.matrice[200 - i][3] / (5 * var.Dc) * var.matrice[200 - i][12] + 2 / 5 * var.matrice[200 - i][15]
            else:
                var.matrice[200 - i][14] = var.matrice[200 - i][15]
            

        
        #16-Frottement latéral
        for i in range (0,200) :
            var.matrice[199 - i][16] = numpy.pi * var.Dc * (var.matrice[199 - i][14] + var.matrice[199 - i + 1][14]) / 2 * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0])
            if var.dQ_mat[199 - i] != var.dQ_Hm : 
                var.matrice[199 - i][16] = var.matrice[199 - i][16] - numpy.pi * var.Rc * var.Rc * var.matrice[199 - i][11] * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0])

        
        #17-Frottement latéral cumulé
        #var.matrice[200][7] = 0
        for i in range (0,200) :
            var.matrice[199 - i][17] = var.matrice[199 - i + 1][17] + var.matrice[199 - i][16]

        #18-Effort normal dans la colonne
        for i in range(0,200) :
            if var.matrice[199 - i][0] < var.Hm :
                var.matrice[199 - i][18] = max((var.matrice[199 - i][17] + Gqp), 0)
            else:
                var.matrice[199 - i][18] = max(min(var.matrice[199 - i][17] + Gqp, var.dQ_mat[199 - i]), 0)
            
        #19-Frottement latéral limite
        for i in range(0,200) :
            var.matrice[199 - i][19] = numpy.pi * var.Dc * (var.matrice[199 - i][15] + var.matrice[199 - i + 1][15]) / 2 * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0])

        #20-Frottement latéral négatif
        for i in range(0,200) :
            if var.matrice[199 - i][0] < var.Hm :
                var.matrice[199 - i][20] = 0
            elif var.matrice[199 - i][16] < 0 :
                var.matrice[199 - i][20] = var.matrice[199 - i][16]
            else:
                var.matrice[199 - i][20] = 0
            

        
        #21-Frottement latéral positif
        for i in range(0,200) :
            if var.matrice[199 - i][0] < var.Hm :
                var.matrice[199 - i][21] = 0
            elif var.matrice[199 - i][16] >= 0 :
                var.matrice[199 - i][21] = var.matrice[199 - i][16]
            else:
                var.matrice[199 - i][21] = 0
            

        
        #22-Contrainte normale dans la colonne
        for i in range(0,200) :
            var.matrice[199 - i][22] = var.matrice[199 - i][18] / (numpy.pi * var.Rc * var.Rc)

        
        #23-Charge apportée au sol
        for i in range(0,200) :
            var.matrice[199 - i][23] = var.dQ_mat[199 - i] - var.matrice[199 - i][18]

        
        #24-Contrainte apportée au sol
        for i in range(0,200) :
            var.matrice[199 - i][24] = var.matrice[199 - i][23] / (var.Amaille - numpy.pi * var.Rc * var.Rc)

        
        #25-Raccourcissement élastique de la colonne sur la tranche i
        for i in range(0,200) :
            if var.matrice[199 - i][0] < var.Hm :
                var.matrice[199 - i][25] = (var.matrice[199 - i][22] + var.matrice[199 - i + 1][22]) / 2 * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0]) / var.matrice[199 - i][6]
            else:
                var.matrice[199 - i][25] = (var.matrice[199 - i][22] + var.matrice[199 - i + 1][22]) / 2 * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0]) / var.Ec
            

        
        #26-Tassement de la colonne
        for i in range(0,200) :
            var.matrice[199 - i][26] = var.matrice[199 - i + 1][26] + var.matrice[199 - i][25]

        
        #27-Raccourcissement du sol sur la tranche i
        for i in range(0,200) :
            var.matrice[199 - i][27] = (var.matrice[199 - i][24] + var.matrice[199 - i + 1][24]) / 2 * (var.matrice[199 - i + 1][0] - var.matrice[199 - i][0]) / var.matrice[199 - i][5]


        #28-Tassement du sol
        #var.matrice[200][8] = 0
        for i in range(0,200) :
            var.matrice[199 - i][28] = var.matrice[199 - i + 1][28] + var.matrice[199 - i][27]


    #--------------------------------------------------#
    #    Charge dans le sol en sous-face de dallage    #
    #--------------------------------------------------#
    Gqsol = var.matrice[0][23]

    #--------------------------------------------------#
    #            Somme du frottement latéral           #
    #--------------------------------------------------#
    Gqs = var.matrice[0][17]

    #--------------------------------------------------#
    #                Erreurs numeriques                #
    #--------------------------------------------------#
    diff = var.matrice[0][26] - var.matrice[0][28]
    erreur_num = abs((var.matrice[0][26] - var.matrice[0][28]) / var.matrice[0][28])
    erreur_num_charge = abs(Gqsol + Gqp + Gqs - var.dQ_) / var.dQ_
    var.matrice[0][29] = diff
    var.matrice[2][29] = erreur_num
    var.matrice[3][29] = erreur_num_charge

    Calcul = var.matrice
    return Calcul