# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:28:24 2019

@author: nya
"""
import numpy as np
from pyDOE import lhs

def generate_LHS_samples(x_min, x_max, samples=1):
    """ Generates Latin Hypercube Samples
    """
    rnd_points = lhs(x_min.size, samples)

    return rnd_points * (x_max - x_min) + x_min


def generate_FD_samples(x, x_min, x_max):
    """ Generates finite-diffence samples about x given lower and upper bounds
    """
    fd_points = []
    for i in range(x.size): # loop over each dimesion
        point_min = np.copy(x)
        point_min[i] = x_min[i] # perturb to min
        fd_points.append(point_min)
        point_max = np.copy(x)
        point_max[i] = x_max[i] # perturb to max
        fd_points.append(point_max)
        
    #n = 2*(x.size) # number of points
    #fd_points =  np.tile(x, (n, 1))
    # to implement

    return np.array(fd_points)


def hex_to_rgb(hex_text):
    """ Convert color's hex code to (R,G,B)
    """
    hex_text = hex_text.lstrip('#')
    lv = len(hex_text)
    return tuple(int(hex_text[i:i+lv//3], 16) for i in range(0, lv, lv//3)) 


def rgb_to_integer(rgb):
    """ Convert (R,G,B) to PLAXIS' integer color code
    """
    iB = rgb[2]<<16
    iG = rgb[1]<<8
    iR = rgb[0]
    return iR + iG + iB


def get_anchor_grout_endpoints(position, angle, length_free, length_fixed):
    """ Gets two end points of the ground anchors
    """
    point1_x = position[0]
    point1_y = position[1]
        
    x1 = np.cos(angle*np.pi/180) * length_free
    y1 = np.tan(angle*np.pi/180) * x1
    point2_x = point1_x + x1
    point2_y = point1_y + y1
    x2 = np.cos(angle*np.pi/180) * (length_free + length_fixed)
    y2 = np.tan(angle*np.pi/180) * x2
    point3_x = point1_x + x2
    point3_y = point1_y + y2
        
    return [point2_x, point2_y], [point3_x, point3_y]


def get_anchor_soillayer_intersection_point(grout_point_start, grout_point_end, angle, layer_bottom):
    """ Gets intersection point between anchor's grout body and soil layer' bottom
    """
    x_start = grout_point_start[0]
    y_start = grout_point_start[1]
    y_end = grout_point_end[1]
    if ((layer_bottom+0.2) < y_start) and ((layer_bottom-0.2) > y_end):
        y_intersect = layer_bottom
        h = y_start - y_intersect
        w = h/np.tan(abs(angle)*np.pi/180)
        x_intersect = x_start + w

        point_intersect = (x_intersect, y_intersect)
        point_intersect_minus = move_point(point_intersect, angle, -0.2)    # move by 0.2 m backward
        point_intersect_plus = move_point(point_intersect, angle, 0.2)      # move by 0.2 m forward
    
        return point_intersect_minus, point_intersect_plus

    else:
        return None, None
    

def move_point(point, angle, d):
    """ Moves a 2D point with angle by a distance d
    """
    x_point = point[0]
    y_point = point[1]
    d_x = d*np.cos(angle*np.pi/180)
    d_y = d*np.sin(angle*np.pi/180)

    x = x_point + d_x
    y = y_point + d_y

    return (x, y)


def swap_2points(point1, point2):
    """ Swaps 2 points
    """
    point_temp = point2
    point2 = point1
    point1 = point_temp
    return point1, point2


def calc_dist_2p(point1, point2):
    """ Calculates length (distance) between two points
    """
    return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


def is_in_box(point1, point2, x, y):
    """ Checks if (x,y) is in the box defined by point1 and point2
    """
    violations = 0
    # check for x
    if point1[0] <= point2[0]:
        if (point1[0] <= x <= point2[0]):
            pass
        else:
            violations += 1
    else:
        if (point2[0] <= x <= point1[0]):
            pass
        else:
            violations += 1
    # check for y
    if point1[1] <= point2[1]:
        if (point1[1] <= y <= point2[1]):
            pass
        else:
            violations += 1
    else:
        if (point2[1] <= y <= point1[1]):
            pass
        else:
            violations += 1

    return (violations==0)


if __name__ == '__main__':
    x = np.array([2, 4, 5, 8], dtype=float)
    x_min = x - 0.1*x
    x_max = x + 0.1*x
    fd_points = generate_FD_samples(x, x_min, x_max)
    print(fd_points)
    print(fd_points.shape)