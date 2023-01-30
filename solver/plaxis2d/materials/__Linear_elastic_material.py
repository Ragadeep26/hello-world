# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 20:57:19 2020

@author: nya
"""

import json

E = 40.0E3
nu = 0.3
G = E/(2*(1 + nu))
material_LE = [("MaterialName", "Linear elastic"),
               ("Colour", 15262369),
               ("SoilModel", 1), #1 for Linear Elastic
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.0005),
               ("perm_vertical_axis", 0.0005),
               ("Gref", G),
               ("nu", nu),
               ("Rinter", 0.67)]
with open("LINEAR_ELASTIC_material.json", "w") as write_file:    
    json.dump(material_LE, write_file)