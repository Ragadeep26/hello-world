# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 18:18:53 2019

@author: nya
"""
import numpy as np

def L2(syn, obs):
    """ L2 misfit 
    """
    rsd = syn-obs

    return np.sqrt(np.sum(rsd*rsd))


def L1(syn, obs):
    """ L1 misfit 
    """
    rsd = syn-obs

    return np.sum(np.abs(rsd))


def Linf(syn, obs):
    """ L-infinity norm
    """
    rsd = syn-obs
    
    return np.abs(np.max(rsd))