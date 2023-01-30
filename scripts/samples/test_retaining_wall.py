#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 10:40:57 2018

@author: nya
"""

import sys
sys.path.append(r'C:\Users\nya\Packages\Moniman')
import os
from common.boilerplate import start_plaxis, load_plxscripting
from solver.plaxis2d.retaining_wall_input.generate_model import (create_model, 
                                                          calculate_model)
from solver.plaxis2d.retaining_wall_output.get_outputs import (plot_plate_outputs)

PLAXIS_PATH = r'C:\Program Files\Plaxis\PLAXIS 2D'
PLAXIS_INPUT = os.path.join(PLAXIS_PATH, 'Plaxis2DXInput.exe')
PLAXIS_OUTPUT = os.path.join(PLAXIS_PATH, 'Plaxis2DOutput.exe')
PLAXIS_SCRIPTING_PATH = r'C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages'
SCRATCH = r'C:\Users\nya\Packages\Moniman\scratch'
PORT = 20000
PASSWORD = 'mypassword'

if __name__ == '__main__':
   
    ## Load Plaxis Scripting Interface
    load_plxscripting(PLAXIS_SCRIPTING_PATH)
    from plxscripting.easy import new_server
    
#    # Boilerplate for INPUT
#    start_plaxis(PLAXIS_INPUT, PORT, PASSWORD, no_controllers=False)
#
#    # Initialize Input server which has been opened at Port number PORT
#    s_i, g_i = new_server('localhost', PORT, password = PASSWORD)
#        
#    # Start a new project and create the desired model.
#    s_i.new()
#    create_model(g_i)
#    
#    # Perform calculaition
#    calculate_model(g_i)
#    g_i.save(os.path.join(SCRATCH, 'retaining_wall.p2dx'))



    
    # Set requested outputs and initialize Output server
    
    # Boilerplate for OUTPUT
    #start_plaxis(PLAXIS_OUTPUT, PORT+1, PASSWORD, no_controllers=True)
    start_plaxis(PLAXIS_OUTPUT, 10001, PASSWORD, no_controllers=True)
    #s_o, g_o = new_server('localhost', PORT+1, password = PASSWORD)
    s_o, g_o = new_server('localhost', 10001, password = PASSWORD)
    
    s_o.open(os.path.join(SCRATCH, 'retaining_wall.p2dx'))
    
    ## Select phase for OUTPUT 
    plot_plate_outputs(SCRATCH, g_o, 1) # plot plate outputs at Phase_4
    
    
    
    
    