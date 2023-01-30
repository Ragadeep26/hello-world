# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:00:04 2018

@author: nya
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import os

def get_plate_outputs(path, g_o, x_wall, phasenumber = 1):
    """ Get the requested outputs for wall
    """
    # path is where deflection and internal forces are written out
    # g_o is plaxis output object
    # phasenumber for getting the outputs is to specify
    
    # set the phase
    phasenumber = max(1, phasenumber) # exclude phasenummber=0 ('InitialPhase')
    phase_i = 'Phase_' + str(phasenumber)
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
            phase_o_name = phase.Identification.value

    X = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')
    Ux = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Ux, 'node')
    Nx2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx2D, 'node')
    Nx_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMax2D, 'node')
    Nx_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMin2D, 'node')
    M2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M2D, 'node')
    M_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMax2D, 'node')
    M_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMin2D, 'node')
    Q2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q2D, 'node')
    Q_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMax2D, 'node')
    Q_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMin2D, 'node')
    
    
    X_plate = x_wall
    Y_plate = []
    Ux_plate = []
    Nx2D_plate = []
    Nx_EnvelopeMax2D_plate = []
    Nx_EnvelopeMin2D_plate = []
    M2D_plate = []
    M_EnvelopeMax2D_plate = []
    M_EnvelopeMin2D_plate = []
    Q2D_plate = []
    Q_EnvelopeMax2D_plate = []
    Q_EnvelopeMin2D_plate = []
    for x, y, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Ux, 
                                                Nx2D, Nx_EnvelopeMax2D, Nx_EnvelopeMin2D,
                                                M2D, M_EnvelopeMax2D, M_EnvelopeMin2D,
                                                Q2D, Q_EnvelopeMax2D, Q_EnvelopeMin2D):
        if abs(x - X_plate) < 1.0E-5:
            #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Ux)))
            Y_plate.append(y)
            Ux_plate.append(ux)
            Nx2D_plate.append(Nx)
            Nx_EnvelopeMax2D_plate.append(Nxemax)
            Nx_EnvelopeMin2D_plate.append(Nxemin)
            M2D_plate.append(M)
            M_EnvelopeMax2D_plate.append(Memax)
            M_EnvelopeMin2D_plate.append(Memin)
            Q2D_plate.append(Q)
            Q_EnvelopeMax2D_plate.append(Qemax)
            Q_EnvelopeMin2D_plate.append(Qemin)
    
    # save text file
    with open(os.path.join(path,'retaining_wall_WALL_OUTPUTS.txt'), "w") as f:
        f.write("{0}\t\t {1}\t\t {2}\t\t {3}\t\t {4}\t\t {5}\t\t {6}\t\t {7}\t\t {8} \t\t {9}\t\t {10}\n".format('y', 'Ux', 'N', 'Nemax', 'Nemin', 'M', 'Memax', 'Memin', 'Q', 'Qemax', 'Qemin'))
        for (y, Ux, N, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin) in zip(Y_plate, Ux_plate, Nx2D_plate, Nx_EnvelopeMax2D_plate, Nx_EnvelopeMin2D_plate,
                                                                M2D_plate,M_EnvelopeMax2D_plate, M_EnvelopeMin2D_plate, Q2D_plate, Q_EnvelopeMax2D_plate,
                                                                Q_EnvelopeMin2D_plate):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\t {5:.4E}\t {6:.4E}\t {7:.4E}\t {8:.4E} \t {9:.4E}\t {10:.4E}\n".format(y, Ux, N, Nxemax, Nxemin, 
                                                                                                                                        M, Memax, Memin, Q, Qemax, Qemin))
    
    return (phase_o_name, Y_plate, Ux_plate, Nx2D_plate, Nx_EnvelopeMax2D_plate, Nx_EnvelopeMin2D_plate, M2D_plate, M_EnvelopeMax2D_plate, 
            M_EnvelopeMin2D_plate, Q2D_plate, Q_EnvelopeMax2D_plate, Q_EnvelopeMin2D_plate)


def get_plate_outputs_with_y_limits(path, g_o, x_wall, wall, phasenumber = 1):
    """ Get the requested outputs for wall
    Data are retrieved within wall base and wall top. This is useful to read data from a wall that is below or below another wall
    """
    # path is where deflection and internal forces are written out
    # g_o is plaxis output object
    # phasenumber for getting the outputs is to specify
    
    # set y limits
    y_base = min(wall['point1'][1], wall['point2'][1])
    y_top = max(wall['point1'][1], wall['point2'][1])
    # set the phase
    phasenumber = max(1, phasenumber) # exclude phasenummber=0 ('InitialPhase')
    phase_i = 'Phase_' + str(phasenumber)
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
            phase_o_name = phase.Identification.value

    X = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')
    Ux = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Ux, 'node')
    Nx2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx2D, 'node')
    Nx_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMax2D, 'node')
    Nx_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMin2D, 'node')
    M2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M2D, 'node')
    M_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMax2D, 'node')
    M_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMin2D, 'node')
    Q2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q2D, 'node')
    Q_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMax2D, 'node')
    Q_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMin2D, 'node')
    
    
    X_plate = x_wall
    Y_plate = []
    Ux_plate = []
    Nx2D_plate = []
    Nx_EnvelopeMax2D_plate = []
    Nx_EnvelopeMin2D_plate = []
    M2D_plate = []
    M_EnvelopeMax2D_plate = []
    M_EnvelopeMin2D_plate = []
    Q2D_plate = []
    Q_EnvelopeMax2D_plate = []
    Q_EnvelopeMin2D_plate = []
    for x, y, ux, Nx, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin in zip(X, Y, Ux, 
                                                Nx2D, Nx_EnvelopeMax2D, Nx_EnvelopeMin2D,
                                                M2D, M_EnvelopeMax2D, M_EnvelopeMin2D,
                                                Q2D, Q_EnvelopeMax2D, Q_EnvelopeMin2D):
        if (abs(x - X_plate) < 1.0E-5) and (y_base <= y <= y_top):
            #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Ux)))
            Y_plate.append(y)
            Ux_plate.append(ux)
            Nx2D_plate.append(Nx)
            Nx_EnvelopeMax2D_plate.append(Nxemax)
            Nx_EnvelopeMin2D_plate.append(Nxemin)
            M2D_plate.append(M)
            M_EnvelopeMax2D_plate.append(Memax)
            M_EnvelopeMin2D_plate.append(Memin)
            Q2D_plate.append(Q)
            Q_EnvelopeMax2D_plate.append(Qemax)
            Q_EnvelopeMin2D_plate.append(Qemin)
    
    # save text file
    with open(os.path.join(path,'retaining_wall_WALL_OUTPUTS.txt'), "w") as f:
        f.write("{0}\t\t {1}\t\t {2}\t\t {3}\t\t {4}\t\t {5}\t\t {6}\t\t {7}\t\t {8} \t\t {9}\t\t {10}\n".format('y', 'Ux', 'N', 'Nemax', 'Nemin', 'M', 'Memax', 'Memin', 'Q', 'Qemax', 'Qemin'))
        for (y, Ux, N, Nxemax, Nxemin, M, Memax, Memin, Q, Qemax, Qemin) in zip(Y_plate, Ux_plate, Nx2D_plate, Nx_EnvelopeMax2D_plate, Nx_EnvelopeMin2D_plate,
                                                                M2D_plate,M_EnvelopeMax2D_plate, M_EnvelopeMin2D_plate, Q2D_plate, Q_EnvelopeMax2D_plate,
                                                                Q_EnvelopeMin2D_plate):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\t {5:.4E}\t {6:.4E}\t {7:.4E}\t {8:.4E} \t {9:.4E}\t {10:.4E}\n".format(y, Ux, N, Nxemax, Nxemin, 
                                                                                                                                        M, Memax, Memin, Q, Qemax, Qemin))
    
    return (phase_o_name, Y_plate, Ux_plate, Nx2D_plate, Nx_EnvelopeMax2D_plate, Nx_EnvelopeMin2D_plate, M2D_plate, M_EnvelopeMax2D_plate, 
            M_EnvelopeMin2D_plate, Q2D_plate, Q_EnvelopeMax2D_plate, Q_EnvelopeMin2D_plate)


def get_soilsection_uy(path, g_o, point1, point2, vicinity, phasenumber = 1):
    """ Get the requested outputs for wall
    """
    # path is where deflection and internal forces are written out
    # g_o is plaxis output object
    # phasenumber for getting the outputs is to specify
    
    # set the phase
    phase_i = 'Phase_' + str(phasenumber)
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    X = g_o.getresults(phase_o, g_o.ResultTypes.Soil.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Soil.Y, 'node')
    Uy = g_o.getresults(phase_o, g_o.ResultTypes.Soil.Uy, 'node')    
    
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    
    #slope
    m = (y2 - y1)/(x2 - x1)
    
    X_section = []
    Y_section = []
    Uy_section = []
    
    
    for x, y, uy in zip(X, Y, Uy):
        if (abs(y - y1 - m*(x - x1)) < vicinity) and (x > min(x1, x2)) and (x < max(x1, x2)):
            #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(uy)))
            X_section.append(x)
            Y_section.append(y)
            Uy_section.append(uy)
        
    
    # save text file
    with open(os.path.join(path,'retaining_wall_SOILSECTION_DISPLACEMENT.txt'), "w") as f:
        f.write("{0}\t\t {1}\t\t {2}\n".format('x', 'y', 'Uy'))
        for (x, y, uy) in zip(X_section, Y_section, Uy_section):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\n".format(x, y, uy))
    
    return (X_section, Y_section, Uy_section)


def get_wall_hoopforce(g_o, obs_set):
    """ Gets displacements of the requested component at given locations on wall (plate)
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
    
    # set observation type
    obs_type = g_o.ResultTypes.Plate.Nz2D

    out = []
    for point in obs_set['points']:
        out.append(float(g_o.getsingleresult(phase_o, obs_type, point)))

    return out


def get_wall_displ(g_o, obs_set):
    """ Gets displacements of the requested component at given locations on wall (plate)
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
    
    # set observation type
    if 'Ux' in obs_set['obs_type']:
        obs_type = g_o.ResultTypes.Plate.Ux
    elif 'Uy' in obs_set['obs_type']:
        obs_type = g_o.ResultTypes.Plate.Uy

    out = []
    for point in obs_set['points']:
        out.append(float(g_o.getsingleresult(phase_o, obs_type, point)))

    return out
    

#def get_wall_internal_forces_envelope(g_o, obs_set):
#    """ Gets enveloped internal forces at given locations on wall (plate)
#    """
#    # set the phase
#    phase_i = 'Phase_' + str(obs_set['obs_phase'])
#    for phase in g_o.Phases[:]:
#        if phase.Name.value == phase_i:
#            phase_o = phase
#    
#    # set observation type
#    if 'WallNx' in obs_set['obs_type']:
#        obs_type_max = g_o.ResultTypes.Plate.Nx_EnvelopeMax2D
#        obs_type_min = g_o.ResultTypes.Plate.Nx_EnvelopeMin2D
#    elif 'WallM' in obs_set['obs_type']:
#        obs_type_max = g_o.ResultTypes.Plate.M_EnvelopeMax2D
#        obs_type_min = g_o.ResultTypes.Plate.M_EnvelopeMin2D
#    elif 'WallQ' in obs_set['obs_type']:
#        obs_type_max = g_o.ResultTypes.Plate.Q_EnvelopeMax2D
#        obs_type_min = g_o.ResultTypes.Plate.Q_EnvelopeMin2D
#
#    out_max = []
#    out_min = []
#    for point in obs_set['points']:
#        out_max.append(float(g_o.getsingleresult(phase_o, obs_type_max, point)))
#        out_min.append(float(g_o.getsingleresult(phase_o, obs_type_min, point)))
#
#    return (out_max, out_min)


def get_wall_internal_forces_envelope(g_o, obs_set, x_wall=0.0):
    """ Get the requested outputs for wall
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
    
    X = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    Y = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')
    #Ux = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Ux, 'node')
    #Nx2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx2D, 'node')
    Nx_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMax2D, 'node')
    Nx_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMin2D, 'node')
    #M2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M2D, 'node')
    M_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMax2D, 'node')
    M_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMin2D, 'node')
    #Q2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q2D, 'node')
    Q_EnvelopeMax2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMax2D, 'node')
    Q_EnvelopeMin2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMin2D, 'node')
    
    
    X_plate = x_wall
    Y_plate = []
    Nx_EnvelopeMax2D_plate = []
    Nx_EnvelopeMin2D_plate = []
    M_EnvelopeMax2D_plate = []
    M_EnvelopeMin2D_plate = []
    Q_EnvelopeMax2D_plate = []
    Q_EnvelopeMin2D_plate = []
    for x, y, Nxemax, Nxemin, Memax, Memin, Qemax, Qemin in zip(X, Y, 
                                                Nx_EnvelopeMax2D, Nx_EnvelopeMin2D,
                                                M_EnvelopeMax2D, M_EnvelopeMin2D,
                                                Q_EnvelopeMax2D, Q_EnvelopeMin2D):
        if abs(x - X_plate) < 1.0E-5:
            #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Ux)))
            Y_plate.append(y)
            Nx_EnvelopeMax2D_plate.append(Nxemax)
            Nx_EnvelopeMin2D_plate.append(Nxemin)
            M_EnvelopeMax2D_plate.append(Memax)
            M_EnvelopeMin2D_plate.append(Memin)
            Q_EnvelopeMax2D_plate.append(Qemax)
            Q_EnvelopeMin2D_plate.append(Qemin)
    
    return np.vstack((Y_plate, Nx_EnvelopeMax2D_plate, Nx_EnvelopeMin2D_plate, M_EnvelopeMax2D_plate, M_EnvelopeMin2D_plate, Q_EnvelopeMax2D_plate, Q_EnvelopeMin2D_plate)).T


def get_wall_internal_forces_envelope_at_points(g_o, obs_set):
    """ Gets displacements of the requested component at given locations on wall (plate)
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
    
    Y = []
    Nx_Max2D = []
    Nx_Min2D = []
    M_Max2D = []
    M_Min2D = []
    Q_Max2D = []
    Q_Min2D = []
    for point in obs_set['points']:
        #x = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.X, point)
        y = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.Y, point)
        Nx_EnvelopeMax2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMax2D, point)
        Nx_EnvelopeMin2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.Nx_EnvelopeMin2D, point)
        M_EnvelopeMax2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMax2D, point)
        M_EnvelopeMin2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMin2D, point)
        Q_EnvelopeMax2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMax2D, point)
        Q_EnvelopeMin2D = g_o.getsingleresult(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMin2D, point)

        Y.append(float(y))
        Nx_Max2D.append(float(Nx_EnvelopeMax2D))
        Nx_Min2D.append(float(Nx_EnvelopeMin2D))
        M_Max2D.append(float(M_EnvelopeMax2D))
        M_Min2D.append(float(M_EnvelopeMin2D))
        Q_Max2D.append(float(Q_EnvelopeMax2D))
        Q_Min2D.append(float(Q_EnvelopeMin2D))

    return np.vstack((Y, Nx_Max2D, Nx_Min2D, M_Max2D, M_Min2D, Q_Max2D, Q_Min2D)).T


def get_soil_displ(g_o, obs_set):
    """ Gets displacements of the requested component at given locations in soil
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase
    
    # set observation type
    if 'Ux' in obs_set['obs_type']:
        obs_type = g_o.ResultTypes.Soil.Ux
    elif 'Uy' in obs_set['obs_type']:
        obs_type = g_o.ResultTypes.Soil.Uy

    out = []
    for point in obs_set['points']:
        out.append(float(g_o.getsingleresult(phase_o, obs_type, point)))

    return out


def get_anchor_force(g_o, obs_set):
    """ Gets anchor force
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    out = []
    for point in obs_set['points']:
        out.append(float(g_o.getsingleresult(phase_o, g_o.ResultTypes.NodeToNodeAnchor.AnchorForce2D, point)))

    return out


def get_all_anchors_force(g_o, Anchors, phasenumber=1):
    """ Gets all current and maximal forces for all anchors
    Return a variable list for anchor forces
    Return an empty list if no anchor forces are available
    """
    # set the phase
    phasenumber = max(1, phasenumber) # exclude phasenummber=0 ('InitialPhase')
    phase_i = 'Phase_' + str(phasenumber)
    phase_o = None
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    F_anchors = []
    for anchor in Anchors:
        point = anchor['position']
        Fcurrent = g_o.getsingleresult(phase_o, g_o.ResultTypes.NodeToNodeAnchor.AnchorForce2D, point)
        Fmax = g_o.getsingleresult(phase_o, g_o.ResultTypes.NodeToNodeAnchor.AnchorForceMax2D, point)
        if not math.isnan(Fmax):
            F_anchor = {'position': point}
            F_anchor['AnchorForce2D'] = float(Fcurrent)
            F_anchor['AnchorForceMax2D'] = float(Fmax)
            F_anchors.append(F_anchor)

            anchor['F_anchor'] = float(Fmax)    # store max. anchor force for dimensioning
            anchor['F_support'] = float(Fmax)   # for waler design
    
    return F_anchors


def get_strut_force(g_o, obs_set):
    """ Gets strut force
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    phase_o = None
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    out = []
    for point in obs_set['points']:
        out.append(float(g_o.getsingleresult(phase_o, g_o.ResultTypes.FixedEndAnchor.AnchorForce2D, point)))

    return out


def get_all_struts_force(g_o, Struts, phasenumber=1):
    """ Gets all current and minimal forces for all struts
    Return a variable list for strut forces
    Return an empty list if no strut forces are available
    """
    # set the phase
    phasenumber = max(1, phasenumber) # exclude phasenummber=0 ('InitialPhase')
    phase_i = 'Phase_' + str(phasenumber)
    phase_o = None
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    F_struts = []
    for strut in Struts:
        point = strut['position']
        Fcurrent = g_o.getsingleresult(phase_o, g_o.ResultTypes.FixedEndAnchor.AnchorForce2D, point)
        Fmax = g_o.getsingleresult(phase_o, g_o.ResultTypes.FixedEndAnchor.AnchorForceMin2D, point)
        if not math.isnan(Fmax):
            F_strut = {'position': point}
            F_strut['AnchorForce2D'] = float(Fcurrent)
            F_strut['AnchorForceMax2D'] = float(Fmax)
            F_struts.append(F_strut)

            strut['F_strut'] = -float(Fmax)    # store max. strut force for dimensioning, compression is positive
            strut['F_support'] = - float(Fmax) # for waler design
    
    return F_struts


def get_msf(g_o, obs_set):
    """ Gets safety factor
    """
    # set the phase
    phase_i = 'Phase_' + str(obs_set['obs_phase'])
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    calc_info_last_step = phase_o.Steps.value[-1]
    if hasattr(calc_info_last_step, 'Reached'):
        msf = calc_info_last_step.Reached.SumMsf.value
    else:
        msf = 0.0

    return [msf]


def get_msf_points(g_o, num_phase):
    ''' gets data to plot safety curve
    '''
    msf = []
    phase_i = 'Phase_' + str(num_phase)
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    calc_info_steps = phase_o.Steps.value
    for i in range(0,len(calc_info_steps)):
        if hasattr(calc_info_steps[i], 'Reached'):
            msf.append(calc_info_steps[i].Reached.SumMsf.value)
        else:
            msf.append(0.0)

    return msf	 


def get_plate_outputs_old(path, g_o, x_wall, phasenumber = 1):
    """ Get the requested outputs for wall
    """
    # path is where deflection and internal forces are written out
    # g_o is plaxis output object
    # phasenumber for getting the outputs is to specify
    
    # set the phase
    phase_i = 'Phase_' + str(phasenumber)
    for phase in g_o.Phases[:]:
        if phase.Name.value == phase_i:
            phase_o = phase

    plateX = g_o.getresults(phase_o, g_o.ResultTypes.Plate.X, 'node')
    plateY = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Y, 'node')
    plateUx = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Ux, 'node')
    plateNx2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Nx2D, 'node')
    plateM2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M2D, 'node')
    plateM2Demax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMax2D, 'node')
    plateM2Demin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.M_EnvelopeMin2D, 'node')
    plateQ2D = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q2D, 'node')
    plateQ2Demax = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMax2D, 'node')
    plateQ2Demin = g_o.getresults(phase_o, g_o.ResultTypes.Plate.Q_EnvelopeMin2D, 'node')
    
    
    x_plate = x_wall
    y_plate = []
    Ux_plate = []
    Nx2D_plate = []
    M2D_plate = []
    M2Demax_plate = []
    M2Demin_plate = []
    Q2D_plate = []
    Q2Demax_plate = []
    Q2Demin_plate = []
    for x, y, Ux, Nx, M, Memax, Memin, Q, Qemax, Qemin in zip(plateX, plateY, plateUx, 
                                                plateNx2D, plateM2D, 
                                                plateM2Demax, plateM2Demin,
                                                plateQ2D, plateQ2Demax,
                                                plateQ2Demin):
        if abs(x - x_plate) < 1.0E-5:
            #print('{:7.6f}{:7.6f}{:7.6f}'.format(float(x), float(y), float(Ux)))
            y_plate.append(y)
            Ux_plate.append(Ux)
            Nx2D_plate.append(Nx)
            M2D_plate.append(M)
            M2Demax_plate.append(Memax)
            M2Demin_plate.append(Memin)
            Q2D_plate.append(Q)
            Q2Demax_plate.append(Qemax)
            Q2Demin_plate.append(Qemin)
    
    # save text file
    with open(os.path.join(path,'retaining_wall_WALL_OUTPUTS.txt'), "w") as f:
        f.write("{0}\t\t {1}\t\t {2}\t\t {3}\t\t {4}\t\t {5}\t\t {6}\t\t {7}\t\t {8}\n".format('y', 'Ux', 'N', 'M', 'Memax', 'Memin', 'Q', 'Qemax', 'Qemin'))
        for (y, Ux, N, M, Memax, Memin, Q, Qemax, Qemin) in zip(y_plate, Ux_plate, Nx2D_plate, M2D_plate, M2Demax_plate, M2Demin_plate, Q2D_plate, Q2Demax_plate, Q2Demin_plate):
            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\t {5:.4E}\t {6:.4E}\t {7:.4E}\t {8:.4E}\n".format(y, Ux, N, M, Memax, Memin, Q, Qemax, Qemin))
    
    return (y_plate, Ux_plate, Nx2D_plate, M2D_plate, M2Demax_plate, 
            M2Demin_plate, Q2D_plate, Q2Demax_plate, Q2Demin_plate)


def plot_plate_outputs(path, g_o, x_wall, phasenumber):
    """ Plot requested plate outputs
    """
    # path is where deflection and internal forces are written out
    # g_o is plaxis output object
    # phasenumber for getting the outputs is to specify
    
    (y_plate, Ux_plate, Nx2D_plate, M2D_plate, 
     M2Demax_plate, M2Demin_plate, Q2D_plate, 
     Q2Demax_plate, Q2Demin_plate) = get_plate_outputs(path, g_o, x_wall, phasenumber)
    
    fig, (ax1, ax2, ax3, ax3e, ax4, ax4e) = plt.subplots(1, 6, sharey = True, figsize = (12,8))
    plt.setp(ax1.get_xticklabels(), rotation=70, horizontalalignment='center')
    plt.setp(ax2.get_xticklabels(), rotation=70, horizontalalignment='center')
    plt.setp(ax3.get_xticklabels(), rotation=70, horizontalalignment='center')
    plt.setp(ax3e.get_xticklabels(), rotation=70, horizontalalignment='center')
    plt.setp(ax4.get_xticklabels(), rotation=70, horizontalalignment='center')
    plt.setp(ax4e.get_xticklabels(), rotation=70, horizontalalignment='center')
    
    ax1.fill_betweenx(y_plate, 1000.0*np.array(Ux_plate), 0, hatch = '-', facecolor = 'blue')
    #ax1.set_xlim(1000*min(Ux_plate), 1000*max(Ux_plate))
    Uxmin = min(Ux_plate)
    ymin = float(y_plate[np.where(np.array(Ux_plate) == Uxmin)[0][0]])
    annotate_min(Uxmin*1000, ymin, Uxmin*1000, ax1)
    Uxmax = max(Ux_plate)
    ymax = float(y_plate[np.where(np.array(Ux_plate) == Uxmax)[0][0]])
    annotate_max(Uxmin*1000, ymax, Uxmax*1000, ax1)
    ax1.set_ylabel('y [m]')
    ax1.set_xlabel('Ux [mm]')
    ax1.set_xticks(ticks=[Uxmin*1000, Uxmax*1000])
    
    ax2.fill_betweenx(y_plate, Nx2D_plate, 0, hatch = '-', facecolor = 'red')
    Nmin = min(Nx2D_plate)
    ymin = float(y_plate[np.where(np.array(Nx2D_plate) == Nmin)[0][0]])
    annotate_min(Nmin, ymin, Nmin, ax2)
    Nmax = max(Nx2D_plate)
    ymax = float(y_plate[np.where(np.array(Nx2D_plate) == Nmax)[0][0]])
    annotate_max(Nmin, ymax, Nmax, ax2)
    ax2.set_xlabel('N [kN/m]')
    ax2.set_xticks(ticks=[Nmin, Nmax])
    
    ax3.fill_betweenx(y_plate, M2D_plate, 0, hatch = '-', facecolor = 'red')
    Mmin = min(M2D_plate)
    ymin = float(y_plate[np.where(np.array(M2D_plate) == Mmin)[0][0]])
    annotate_min(Mmin, ymin, Mmin, ax3)
    Mmax = max(M2D_plate)
    ymax = float(y_plate[np.where(np.array(M2D_plate) == Mmax)[0][0]])
    annotate_max(Mmin, ymax, Mmax, ax3)
    ax3.set_xlabel('M [kNm/m]')   
    ax3.set_xticks(ticks=[Mmin, Mmax])
    
    ax3e.fill_betweenx(y_plate, M2Demin_plate, 0, hatch = '-', facecolor = 'orange')
    Memin = min(M2Demin_plate)
    ymin = float(y_plate[np.where(np.array(M2Demin_plate) == Memin)[0][0]])
    annotate_min(Memin, ymin, Memin, ax3e)
    ax3e.fill_betweenx(y_plate, M2Demax_plate, 0, hatch = '-', facecolor = 'yellow')
    Memax = max(M2Demax_plate)
    ymax = float(y_plate[np.where(np.array(M2Demax_plate) == Memax)[0][0]])
    annotate_max(Memin, ymax, Memax, ax3e)
    ax3e.set_xlabel('Me [kNm/m]')
    ax3e.set_xticks(ticks=[Memin, Memax])
    
    ax4.fill_betweenx(y_plate, Q2D_plate, 0, hatch = '-', facecolor = 'red')
    Qmin = min(Q2D_plate)
    ymin = float(y_plate[np.where(np.array(Q2D_plate) == Qmin)[0][0]])
    annotate_min(Qmin, ymin, Qmin, ax4)
    Qmax = max(Q2D_plate)
    ymax = float(y_plate[np.where(np.array(Q2D_plate) == Qmax)[0][0]])
    annotate_max(Qmin, ymax, Qmax, ax4)
    ax4.set_xlabel('Q [kN/m]')
    ax4.set_xticks(ticks=[Qmin, Qmax])
    
    ax4e.fill_betweenx(y_plate, Q2Demin_plate, 0, hatch = '-', facecolor = 'orange')
    Qemin = min(Q2Demin_plate)
    ymin = float(y_plate[np.where(np.array(Q2Demin_plate) == Qemin)[0][0]])
    annotate_min(Qemin, ymin, Qemin, ax4e)
    ax4e.fill_betweenx(y_plate, Q2Demax_plate, 0, hatch = '-', facecolor = 'yellow')
    Qemax = max(Q2Demax_plate)
    ymax = float(y_plate[np.where(np.array(Q2Demax_plate) == Qemax)[0][0]])
    annotate_max(Qemin, ymax, Qemax, ax4e)
    ax4e.set_xlabel('Qe [kN/m]')
    ax4e.set_xticks(ticks=[Qemin, Qemax])
    
    plt.show()
    
def annotate_min(x, y, value, ax=None):
    ax.axvline(x, color='black', linestyle='--')
    
    
def annotate_max(x, y, value, ax=None):
    ax.axvline(value, color='black', linestyle='--')
