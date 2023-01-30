# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 09:54:21 2018

@author: nya
"""
import os
import sys
import imp
import subprocess
#import psutil
import time


def start_plaxis(app_path, portnr=10000, password='mypassword', no_controllers=False):
    """ Starts Plaxis2DInput.exe or Plaxis2DOutput.exe
    """
    args = [app_path]
    args.append('--AppServerPort={}'.format(portnr))
    if password:
        args.append('--AppServerPassword={}'.format(password))

    if no_controllers is True:
        args.append('--NO_CONTROLLERS')    
    p = subprocess.Popen(args)
    #print('args: ', args)
    # wait a second for the application to launch
    #print("Launched: {}".format(os.path.basename(app_path)))
    delay = 5 # 5 seconds
    time.sleep(delay)

    return p


def load_plxscripting(PLAXIS_SCRIPTING_PATH):
    """ PLAXIS BOILERPLATE
    To import plxscripting
    """
    ## Append Python path to use Plaxis scripting funtionalities
    sys.path.append(PLAXIS_SCRIPTING_PATH) # new path 
    
    try:
        found_module = imp.find_module('plxscripting', [PLAXIS_SCRIPTING_PATH])
        #print('found plxscripting module:', found_module)
        plxscripting = imp.load_module('plxscripting',*found_module)
    except ImportError:
        sys.exit("Please check if PLAXIS_SCRIPTING_PATH is correct!")
    
    #from plxscripting.easy import new_server

def get_calculation_status(g_i):
    """ Gathers calculation status of the phases
    """
    results = []
    allpassed = True
    for phase in g_i.Phases[:]:
        msg = 'Not calculated'
        if not phase.ShouldCalculate:
            if phase.CalculationResult == phase.CalculationResult.ok:
                msg = 'OK'
            else:
                msg = 'Failed with ErrorCode {0}'.format(phase.LogInfo)
                allpassed = False
        results.append('{0}: {1}'.format(phase.Name, msg))
        
    return allpassed, results
