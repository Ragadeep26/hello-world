# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 12:33:34 2018

@author: nya
"""

import json
import numpy as np

we = 0.5
powerm = we
phi = 40
K0nc = 1.0 - np.sin(phi*np.pi/180)
OCR = 1.0
cobbles_HS = [("MaterialName", "Cobbles"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 1.0),
               ("perm_vertical_axis", 1.0),
               ("E50ref", 35000),
               ("EoedRef", 35000),
               ("EurRef", 105000),               
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 10),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 350),     # user parameter
               ("we", we)]     # user parameter

with open("Cobbles_HS.json", "w") as write_file:    
    json.dump(cobbles_HS, write_file)

we = 0.4
powerm = we 
phi = 37.5
K0nc = 1.0 - np.sin(phi*np.pi/180)
gravel_dense_HS = [("MaterialName", "Gravel dense"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 0.001),
               ("perm_vertical_axis", 0.001),
               ("E50ref", 120000),
               ("EoedRef", 120000),
               ("EurRef", 360000),               
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 7.5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 1200),     # user parameter
               ("we", we)]     # user parameter

with open("Gravel_dense_HS.json", "w") as write_file:    
    json.dump(gravel_dense_HS, write_file)

we = 0.45
powerm = we 
phi = 35
K0nc = 1.0 - np.sin(phi*np.pi/180)
gravel_medium_HS = [("MaterialName", "Gravel medium"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.005),
               ("perm_vertical_axis", 0.005),
               ("E50ref", 90000),
               ("EoedRef", 90000),
               ("EurRef", 270000),               
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", 35),
               ("psi", 5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 900),     # user parameter
               ("we", we)]     # user parameter

with open("Gravel_medium_HS.json", "w") as write_file:    
    json.dump(gravel_medium_HS, write_file)

we = 0.65
powerm = we 
phi = 32.5
K0nc = 1.0 - np.sin(phi*np.pi/180)
gravel_loose_HS = [("MaterialName", "Gravel loose"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.01),
               ("perm_vertical_axis", 0.01),
               ("E50ref", 40000),
               ("EoedRef", 40000),
               ("EurRef", 120000),               
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 2.5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 400),     # user parameter
               ("we", we)]     # user parameter

with open("Gravel_loose_HS.json", "w") as write_file:    
    json.dump(gravel_loose_HS, write_file)
    
we = 0.55
powerm = we 
phi = 35
K0nc = 1.0 - np.sin(phi*np.pi/180)   
sand_dense_HS = [("MaterialName", "Sand dense"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0001),
               ("perm_vertical_axis", 0.0001),
               ("E50ref", 40000),
               ("EoedRef", 40000),
               ("EurRef", 120000),               
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 400),     # user parameter
               ("we", we)]     # user parameter

with open("Sand_dense_HS.json", "w") as write_file:    
    json.dump(sand_dense_HS, write_file)

    
we = 0.6
powerm = we 
phi = 32.5
K0nc = 1.0 - np.sin(phi*np.pi/180)
sand_medium_HS = [("MaterialName", "Sand medium"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.0005),
               ("perm_vertical_axis", 0.0005),
               ("E50ref", 30000),
               ("EoedRef", 30000),
               ("EurRef", 90000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 2.5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 300),     # user parameter
               ("we", 0.6)]     # user parameter

with open("Sand_medium_HS.json", "w") as write_file:    
    json.dump(sand_medium_HS, write_file)

we = 0.7
powerm = we 
phi = 32.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
sand_loose_HS = [("MaterialName", "Sand loose"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.01),
               ("perm_vertical_axis", 0.01),
               ("E50ref", 20000),
               ("EoedRef", 20000),
               ("EurRef", 60000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 2.5),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 200),     # user parameter
               ("we", we)]     # user parameter

with open("Sand_loose_HS.json", "w") as write_file:    
    json.dump(sand_loose_HS, write_file)

we = 0.55
powerm = we 
phi = 27.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
silt_hard_HS = [("MaterialName", "Silt hard"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0000001),
               ("perm_vertical_axis", 0.0000001),
               ("E50ref", 15000),
               ("EoedRef", 15000),
               ("EurRef", 45000),
               ("nu", 0.2),
               ("Cref", 10),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 150),     # user parameter
               ("we", 0.55)]     # user parameter

with open("Silt_hard_HS.json", "w") as write_file:    
    json.dump(silt_hard_HS, write_file)

we = 0.6
powerm = we  
phi = 27.5
K0nc = 1.0 - np.sin(phi*np.pi/180)
silt_stiff_HS = [("MaterialName", "Silt stiff"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0000005),
               ("perm_vertical_axis", 0.0000005),
               ("E50ref", 11000),
               ("EoedRef", 11000),
               ("EurRef", 33000),
               ("nu", 0.2),
               ("Cref", 5),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 110),     # user parameter
               ("we", we)]     # user parameter

with open("Silt_stiff_HS.json", "w") as write_file:    
    json.dump(silt_stiff_HS, write_file)

we = 0.7
powerm = we 
phi = 27.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
silt_firm_HS = [("MaterialName", "Silt firm"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20.5),
               ("gammaSat", 21.5),
               ("perm_primary_horizontal_axis", 0.000001),
               ("perm_vertical_axis", 0.000001),
               ("E50ref", 7000),
               ("EoedRef", 7000),
               ("EurRef", 21000),
               ("nu", 0.2),
               ("Cref", 2),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 70),     # user parameter
               ("we", we)]     # user parameter

with open("Silt_firm_HS.json", "w") as write_file:    
    json.dump(silt_firm_HS, write_file)

we = 0.8
powerm = we 
phi = 25
K0nc = 1.0 - np.sin(phi*np.pi/180)    
silt_soft_HS = [("MaterialName", "Silt soft"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.000005),
               ("perm_vertical_axis", 0.000005),
               ("E50ref", 4000),
               ("EoedRef", 4000),
               ("EurRef", 16000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 40),     # user parameter
               ("we", we)]     # user parameter

with open("Silt_soft_HS.json", "w") as write_file:    
    json.dump(silt_soft_HS, write_file)

we = 0.9
powerm = we 
phi = 22.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
silt_very_soft_HS = [("MaterialName", "Silt very soft"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.00001),
               ("perm_vertical_axis", 0.00001),
               ("E50ref", 3000),
               ("EoedRef", 3000),
               ("EurRef", 15000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 30),     # user parameter
               ("we", we)]     # user parameter

with open("Silt_very_soft_HS.json", "w") as write_file:    
    json.dump(silt_very_soft_HS, write_file)


we = 0.9
powerm = we 
phi = 17.5
K0nc = 1.0 - np.sin(phi*np.pi/180)
clay_hard_HS = [("MaterialName", "Clay hard"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 0.000000001),
               ("perm_vertical_axis", 0.000000001),
               ("E50ref", 7000),
               ("EoedRef", 7000),
               ("EurRef", 21000),
               ("nu", 0.2),
               ("Cref", 50),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 70),     # user parameter
               ("we", we)]     # user parameter

with open("Clay_hard_HS.json", "w") as write_file:    
    json.dump(clay_hard_HS, write_file)

we = 0.95
powerm = we 
phi = 17.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
clay_stiff_HS = [("MaterialName", "Clay stiff"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.000000005),
               ("perm_vertical_axis", 0.000000005),
               ("E50ref", 5000),
               ("EoedRef", 5000),
               ("EurRef", 15000),
               ("nu", 0.2),
               ("Cref", 25),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 50),     # user parameter
               ("we", 0.95)]     # user parameter

with open("Clay_stiff_HS.json", "w") as write_file:    
    json.dump(clay_hard_HS, write_file)

we = 1.0
powerm = we 
phi = 17.5
K0nc = 1.0 - np.sin(phi*np.pi/180)    
clay_firm_HS = [("MaterialName", "Clay firm"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.00000001),
               ("perm_vertical_axis", 0.00000001),
               ("E50ref", 3000),
               ("EoedRef", 3000),
               ("EurRef", 12000),
               ("nu", 0.2),
               ("Cref", 10),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 30),     # user parameter
               ("we", we)]     # user parameter

with open("Clay_firm_HS.json", "w") as write_file:    
    json.dump(clay_firm_HS, write_file)
    

we = 1.0
powerm = we 
phi = 15
K0nc = 1.0 - np.sin(phi*np.pi/180)
clay_soft_HS = [("MaterialName", "Clay soft"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.00000005),
               ("perm_vertical_axis", 0.00000005),
               ("E50ref", 2000),
               ("EoedRef", 2000),
               ("EurRef", 10000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 20),     # user parameter
               ("we", we)]     # user parameter

with open("Clay_soft_HS.json", "w") as write_file:    
    json.dump(clay_soft_HS, write_file)
    
we = 1.0
powerm = we 
phi = 10
K0nc = 1.0 - np.sin(phi*np.pi/180)
clay_very_soft_HS = [("MaterialName", "Clay very soft"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 17),
               ("gammaSat", 18),
               ("perm_primary_horizontal_axis", 0.0000001),
               ("perm_vertical_axis", 0.0000001),
               ("E50ref", 600),
               ("EoedRef", 600),
               ("EurRef", 3000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 6),     # user parameter
               ("we", we)]     # user parameter

with open("Clay_very_soft_HS.json", "w") as write_file:    
    json.dump(clay_very_soft_HS, write_file)

we = 0.6
powerm = we 
phi = 30
K0nc = 1.0 - np.sin(phi*np.pi/180)    
fill_HS = [("MaterialName", "Fill"),
               ("Colour", 10676870),
               ("SoilModel", 3), #3 for Hardening Soil
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.001),
               ("perm_vertical_axis", 0.001),
               ("E50ref", 30000),
               ("EoedRef", 30000),
               ("EurRef", 90000),
               ("nu", 0.2),
               ("Cref", 0),
               ("phi", phi),
               ("psi", 0),
               ("K0Determination", 1),
               ("K0nc", K0nc),
               ("Rinter", 0.67), 
               ("powerm", powerm),
               ("Rf", 0.9),
               ("Pref", 100),
               ("OCR", OCR),
               ("ve", 300),     # user parameter
               ("we", we)]     # user parameter

with open("Fill_HS.json", "w") as write_file:    
    json.dump(fill_HS, write_file)