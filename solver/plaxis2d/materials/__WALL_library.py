# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 16:25:18 2018

@author: nya
"""

import os
import numpy as np
#import sys
#sys.path.append(r'C:\Users\nya\Packages\Moniman')
import json

path_out = r'D:\Data\3Packages\Moniman\solver\plaxis2d\materials'

dwall_params = [("MaterialName", "Dwall"),
               ("Colour", 16711680),
               ("Elasticity", 0),
               ("EA", 36000000),
               ("EA2", 36000000),
               ("EI", 4320000),
               ("nu", 0.2),
               ("d", 1.2),
               ("w", 12),
               ("Gref", 12500000)]  
with open(os.path.join(path_out, "WALL_Dwall.json"), "w") as write_file:
    json.dump(dwall_params, write_file)
    

# MIP 550
MIPwall_params = [("MaterialName", "MIP"),
               ("Colour", 16711680),
               ("Elasticity", 0),
               ("EA", 2750000),
               ("EA2", 2750000),
               ("EI", 69322.92),
               ("nu", 0.2),
               ("d", 0.55),
               ("w", 12),
               ("Gref", 2083333.33),
		("fmk", 4.0),     		# MIP strength, user defined parameter
                ("fines_percentage", 60.0)]  	# fines content in percentage, user defined parameter
with open(os.path.join(path_out, "WALL_MIP.json"), "w") as write_file:
    json.dump(MIPwall_params, write_file)


SPW_params = [("MaterialName", "SPW"),
               ("Colour", 16711680),
               ("Elasticity", 0),
               ("EA", 12164246.75469968),
               ("EA2", 12164246.75469968),
               ("EI", 12164246.75469968),
               ("nu", 0.2),
               ("d", 0.76210235533),
               ("w", 12),
               ("Gref", 6650597.66886),
               ("D", 0.88),  # user defined parameter
               ("S", 0.75)]  # user defined parameter
with open(os.path.join(path_out, "WALL_SPW.json"), "w") as write_file:
    json.dump(SPW_params, write_file)    
    

CPW_params = [("MaterialName", "CPW"),
               ("Colour", 16711680),
               ("Elasticity", 0),
               ("EA", 24328493.50939936),
               ("EA2", 24328493.50939936),
               ("EI", 1177499.085854929),
               ("nu", 0.2),
               ("d", 0.76210235533),
               ("w", 12),
               ("Gref", 6650597.66886),
               ("D", 0.88),  # user defined parameter
               ("S", 0.75)]  # user defined parameter
with open(os.path.join(path_out, "WALL_CPW.json"), "w") as write_file:
    json.dump(CPW_params, write_file)  


E = 210000000.0 # [kN/m^2]
nu = 0.3
G = E/(2*(1 + nu))
profile_name = "HEB200"
profile_nos = int(1)
EI, EA = profile_nos*3990.0, profile_nos*546700.0
Profile_params = [("MaterialName", profile_name),
               ("Colour", 16711680),
               ("Elasticity", 0),
               ("EA", EA),      # [kN/m], value with spacing 3 m
               ("EA2", EA),     # [kN/m], value with spacing 3 m
               ("EI", EI),      # [kN^2/m], value with spacing 3 m
               ("nu", nu),
               ("d", np.sqrt(12*EI/EA)),
               ("w", 58),       # 78 - 20
               ("Gref", G),
               ("S", 3.0),     # spacing, a user defined parameter
                ("nos", profile_nos)]     # number of profiles, user defined parameter
with open(os.path.join(path_out, "WALL_Profile.json"), "w") as write_file:
    json.dump(Profile_params, write_file)  