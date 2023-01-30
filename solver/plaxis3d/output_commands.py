# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:00:04 2018

@author: nya
"""
import os
#import math
from tools.math import calc_dist_2p, is_in_box
EPSILON = 1.0E-10

def get_plate_outputs_in_line(path, g_o, point1, point2, phasenumber = 1, z_top=None, z_bottom=None):
    """ Get the requested outputs for wall in a line defined by point1 and point2
    If z_top and z_bottom are given, only values within this z range are read out
    path is where deflection and internal forces are written out
    g_o is plaxis output object
    phasenumber for getting the outputs is to specify
    """
    # set the phase
    #if phasenumber == 0:
    #    phase_i = 'InitialPhase'
    #else:
    #    phase_i = 'Phase_' + str(phasenumber)
    #for phase in g_o.Phases[:]:
    #    if phase.Name.value == phase_i:
    #        phase_o = phase
    #        phase_o_name = phase.Identification.value
    #        break
    phase_o = g_o.Phases[phasenumber]
    phase_o_name = g_o.Phases[phasenumber].Identification.value

    X = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')    
    Z = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Z, 'node')    # Z is depth
    Utot = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Utot, 'node', True)  # total displacement
    N11 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11,   'node', True)
    M11 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11,   'node', True)
    Q13 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13,   'node', True)
    N11_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11_EnvelopeMax, 'node', True)
    N11_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11_EnvelopeMin, 'node', True)
    M11_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11_EnvelopeMax, 'node', True)
    M11_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11_EnvelopeMin, 'node', True)
    Q13_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13_EnvelopeMax, 'node', True)
    Q13_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13_EnvelopeMin, 'node', True)
    
    
    # get anchor forces here (avoid reading plaxis3d database multiple times)
    F_anchors = get_all_anchors_force(g_o, phasenumber, z_top, z_bottom)
    
    #X_plate = x_wall
    X_plate = []
    Y_plate = []
    Z_plate = []
    Utot_plate = []
    N11_plate = []
    N11_EnvelopeMax_plate = []
    N11_EnvelopeMin_plate = []
    M11_plate = []
    M11_EnvelopeMax_plate = []
    M11_EnvelopeMin_plate = []
    Q13_plate = []
    Q13_EnvelopeMax_plate = []
    Q13_EnvelopeMin_plate = []
    if (z_top is None) or (z_bottom is None):
        for x, y, z, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Z, Utot, 
                                                    N11, N11_EnvelopeMax, N11_EnvelopeMin,
                                                    M11, M11_EnvelopeMax, M11_EnvelopeMin,
                                                    Q13, Q13_EnvelopeMax, Q13_EnvelopeMin):
            if (abs(calc_dist_2p(point1, (x, y)) + calc_dist_2p(point2, (x, y)) - calc_dist_2p(point1, point2)) < EPSILON
                and is_in_box(point1, point2, x, y)):
                #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Utot)))
                X_plate.append(x)
                Y_plate.append(y)
                Z_plate.append(z)
                Utot_plate.append(ux)
                N11_plate.append(Nx)
                N11_EnvelopeMax_plate.append(Nxemax)
                N11_EnvelopeMin_plate.append(Nxemin)
                M11_plate.append(M)
                M11_EnvelopeMax_plate.append(Memax)
                M11_EnvelopeMin_plate.append(Memin)
                Q13_plate.append(Q)
                Q13_EnvelopeMax_plate.append(Qemax)
                Q13_EnvelopeMin_plate.append(Qemin)

    else: # filtering condition should also consider z
        for x, y, z, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Z, Utot, 
                                                    N11, N11_EnvelopeMax, N11_EnvelopeMin,
                                                    M11, M11_EnvelopeMax, M11_EnvelopeMin,
                                                    Q13, Q13_EnvelopeMax, Q13_EnvelopeMin):
            if (abs(calc_dist_2p(point1, (x, y)) + calc_dist_2p(point2, (x, y)) - calc_dist_2p(point1, point2)) < EPSILON
                and is_in_box(point1, point2, x, y) and (z_bottom <= z <= z_top)):
                #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Utot)))
                X_plate.append(x)
                Y_plate.append(y)
                Z_plate.append(z)
                Utot_plate.append(ux)
                N11_plate.append(Nx)
                N11_EnvelopeMax_plate.append(Nxemax)
                N11_EnvelopeMin_plate.append(Nxemin)
                M11_plate.append(M)
                M11_EnvelopeMax_plate.append(Memax)
                M11_EnvelopeMin_plate.append(Memin)
                Q13_plate.append(Q)
                Q13_EnvelopeMax_plate.append(Qemax)
                Q13_EnvelopeMin_plate.append(Qemin)
    
    # save text file
    with open(os.path.join(path,'retaining_wall_WALL_OUTPUTS.txt'), "w") as f:
        f.write("{0}\t {1}\t {2}\t {3}\t {4}\t {5}\t {6}\t {7}\t {8} \t {9}\t {10}\t {11}\t {12}\n".format('x', 'y', 'z', 'Utot', 'N11', 'N11emax', 'N11emin', 'M11', 'M11emax', 'M11emin', 'Q13', 'Q13emax', 'Q13emin'))
        for (x, y, z, Utot, N, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin) in zip(X_plate, Y_plate, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate,
                                                                M11_plate,M11_EnvelopeMax_plate, M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate,
                                                                Q13_EnvelopeMin_plate):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\t {5:.4E}\t {6:.4E}\t {7:.4E}\t {8:.4E} \t {9:.4E}\t {10:.4E} \t {11:.4E}\t {12:.4E}\t \n".format(x, y, z, Utot, N, Nxemax, Nxemin, 
                                                                                                                                        M, Memax, Memin, Q, Qemax, Qemin))
    
    return (len(g_o.Phases[:]), phase_o_name, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate, M11_plate, M11_EnvelopeMax_plate, 
            M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate, Q13_EnvelopeMin_plate, F_anchors)


def get_plate_outputs_in_box(path, g_o, point1, point2, phasenumber = 1, z_top=None, z_bottom=None):
    """ Get the requested outputs for wall in a box defined by point1 and point2
    If z_top and z_bottom are given, only values within this z range are read out
    path is where deflection and internal forces are written out
    g_o is plaxis output object
    phasenumber for getting the outputs is to specify
    """
    # set the phase
    phase_o = g_o.Phases[phasenumber]
    phase_o_name = g_o.Phases[phasenumber].Identification.value

    X = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')    
    Z = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Z, 'node')    # Z is depth
    Utot = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Utot, 'node', True)  # total displacement
    N11 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11,   'node', True)
    M11 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11,   'node', True)
    Q13 = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13,   'node', True)
    N11_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11_EnvelopeMax, 'node', True)
    N11_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.N11_EnvelopeMin, 'node', True)
    M11_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11_EnvelopeMax, 'node', True)
    M11_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M11_EnvelopeMin, 'node', True)
    Q13_EnvelopeMax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13_EnvelopeMax, 'node', True)
    Q13_EnvelopeMin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q13_EnvelopeMin, 'node', True)
    
    
    # get anchor forces here (avoid reading plaxis3d database multiple times)
    F_anchors = get_all_anchors_force(g_o, phasenumber, z_top, z_bottom)
    
    #X_plate = x_wall
    X_plate = []
    Y_plate = []
    Z_plate = []
    Utot_plate = []
    N11_plate = []
    N11_EnvelopeMax_plate = []
    N11_EnvelopeMin_plate = []
    M11_plate = []
    M11_EnvelopeMax_plate = []
    M11_EnvelopeMin_plate = []
    Q13_plate = []
    Q13_EnvelopeMax_plate = []
    Q13_EnvelopeMin_plate = []
    if (z_top is None) or (z_bottom is None):
        for x, y, z, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Z, Utot, 
                                                    N11, N11_EnvelopeMax, N11_EnvelopeMin,
                                                    M11, M11_EnvelopeMax, M11_EnvelopeMin,
                                                    Q13, Q13_EnvelopeMax, Q13_EnvelopeMin):
            if is_in_box(point1, point2, x, y):
                #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Utot)))
                X_plate.append(x)
                Y_plate.append(y)
                Z_plate.append(z)
                Utot_plate.append(ux)
                N11_plate.append(Nx)
                N11_EnvelopeMax_plate.append(Nxemax)
                N11_EnvelopeMin_plate.append(Nxemin)
                M11_plate.append(M)
                M11_EnvelopeMax_plate.append(Memax)
                M11_EnvelopeMin_plate.append(Memin)
                Q13_plate.append(Q)
                Q13_EnvelopeMax_plate.append(Qemax)
                Q13_EnvelopeMin_plate.append(Qemin)

    else: # filtering condition should also consider z
        for x, y, z, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Z, Utot, 
                                                    N11, N11_EnvelopeMax, N11_EnvelopeMin,
                                                    M11, M11_EnvelopeMax, M11_EnvelopeMin,
                                                    Q13, Q13_EnvelopeMax, Q13_EnvelopeMin):
            if is_in_box(point1, point2, x, y) and (z_bottom <= z <= z_top):
                #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Utot)))
                X_plate.append(x)
                Y_plate.append(y)
                Z_plate.append(z)
                Utot_plate.append(ux)
                N11_plate.append(Nx)
                N11_EnvelopeMax_plate.append(Nxemax)
                N11_EnvelopeMin_plate.append(Nxemin)
                M11_plate.append(M)
                M11_EnvelopeMax_plate.append(Memax)
                M11_EnvelopeMin_plate.append(Memin)
                Q13_plate.append(Q)
                Q13_EnvelopeMax_plate.append(Qemax)
                Q13_EnvelopeMin_plate.append(Qemin)
    
    # save text file
    with open(os.path.join(path,'retaining_wall_WALL_OUTPUTS.txt'), "w") as f:
        f.write("{0}\t {1}\t {2}\t {3}\t {4}\t {5}\t {6}\t {7}\t {8} \t {9}\t {10}\t {11}\t {12}\n".format('x', 'y', 'z', 'Utot', 'N11', 'N11emax', 'N11emin', 'M11', 'M11emax', 'M11emin', 'Q13', 'Q13emax', 'Q13emin'))
        for (x, y, z, Utot, N, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin) in zip(X_plate, Y_plate, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate,
                                                                M11_plate,M11_EnvelopeMax_plate, M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate,
                                                                Q13_EnvelopeMin_plate):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\t {5:.4E}\t {6:.4E}\t {7:.4E}\t {8:.4E} \t {9:.4E}\t {10:.4E} \t {11:.4E}\t {12:.4E}\t \n".format(x, y, z, Utot, N, Nxemax, Nxemin, 
                                                                                                                                        M, Memax, Memin, Q, Qemax, Qemin))
    
    return (len(g_o.Phases[:]), phase_o_name, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate, M11_plate, M11_EnvelopeMax_plate, 
            M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate, Q13_EnvelopeMin_plate, F_anchors)



def get_all_anchors_force(g_o, phasenumber=1, z_top=None, z_bottom=None):
    """ Gets all current and maximal forces for all anchors in the wall section from point1 to point2
    Return a variable list for anchor forces
    Return an empty list if no anchor forces are available
    """
    phase_o = g_o.Phases[phasenumber]
    #phase_o_name = g_o.Phases[phasenumber].Identification.value
    F_anchors = {}
    try:
        X = g_o.getresults(phase_o, g_o.ResultTypes.NodeToNodeAnchor.X, 'node')
        Y = g_o.getresults(phase_o, g_o.ResultTypes.NodeToNodeAnchor.Y, 'node')    
        Z = g_o.getresults(phase_o, g_o.ResultTypes.NodeToNodeAnchor.Z, 'node')    # Z is depth
        Force3D = g_o.getresults(phase_o, g_o.ResultTypes.NodeToNodeAnchor.AnchorForce3D, 'node')    # Z is depth

        if (z_top is None) or (z_bottom is None):
            F_anchors['X'] = [x for x in X]
            F_anchors['Y'] = [y for y in Y]
            F_anchors['Z'] = [z for z in Z]
            F_anchors['Force3D'] = [f for f in Force3D]
        else:   # filter for z
            F_anchors['X'] = []
            F_anchors['Y'] = []
            F_anchors['Z'] = []
            F_anchors['Force3D'] = []
            for x, y, z, force3d in zip(X, Y, Z, Force3D):
                if (z <= z_top) and (z >= z_bottom):
                    F_anchors['X'].append(x)
                    F_anchors['Y'].append(y)
                    F_anchors['Z'].append(z)
                    F_anchors['Force3D'].append(force3d)

    except: # Unsucessful command
        pass
    
    return F_anchors

