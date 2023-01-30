#!/usr/bin/env python3

import sys
sys.path.append(r'C:\Users\nya\Packages\Moniman')
from common.boilerplate import boilerplate
from solver.plaxis2d.building_on_raft_input.generate_model import (create_soils, create_structures,
                                           create_loads, create_mesh,
                                           create_phases, calculate)

PLAXIS_SCRIPTING_PATH = r'C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages'
PORT = 10000
PASSWORD = 'mypassword'

if __name__ == '__main__':
   
    boilerplate(PLAXIS_SCRIPTING_PATH)

    ## Initialize Input server which has been opened at Port number PORT
    from plxscripting.easy import new_server
    s_i, g_i = new_server('localhost', PORT, password = PASSWORD)
        
    ## Start a new project
    create_soils(s_i, g_i)
    #create_structures(g_i)
    #create_loads(g_i)
    #create_mesh(g_i)
    #create_phases(g_i)
    #calculate(g_i)
    
    