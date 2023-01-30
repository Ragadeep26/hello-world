# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 16:23:34 2018

@author: nya
"""

import json
import math

# free length anchor material
strand_elastic_params = [("MaterialName", "Strand elastic"),
                         ("Colour", 0),
                         ("Elasticity", 0),
                         ("EA", 170E3),
                         ("Lspacing", 1.5)]
with open("ANCHOR_STRAND_Elastic.json", "w") as write_file:
    json.dump(strand_elastic_params, write_file)
    
strand_elastoplastic_params = [("MaterialName", "Strand elastoplastic"),
                         ("Colour", 0),
                         ("Elasticity", 1),
                         ("EA", 170E3),
                         ("FMaxTens", 1000000000000),
                         ("FMaxComp", 1000000000000),
                         ("Lspacing", 1.5)]

with open("ANCHOR_STRAND_Elastoplastic.json", "w") as write_file:
    json.dump(strand_elastoplastic_params, write_file)
    
# fixed length anchor material
grout_linear_params = [("MaterialName", "Embedded beam row - Linear"),
                        ("Colour", 9392839),
                        ("Elasticity", 0),
                        ("BeamType", 0),
                        ("PredefinedBeamType", 0),
                        ("Diameter", 0.22),
                        ("A", math.pi*(0.22/2)**2 ),
                        ("E", 195.0E6),
                        ("w",1),
                        ("Lspacing", 1.5),
                        ("SkinResistance", "Linear"), #0
                        ("Tstart", 200),
                        ("Tend", 200),]
with open("ANCHOR_GROUT_Linear.json", "w") as write_file:
    json.dump(grout_linear_params, write_file)
    
grout_multilinear_params = [("MaterialName", "Embedded beam row - Multilinear"),
                        ("Colour", 9392839),
                        ("Elasticity", 0),
                        ("BeamType", 0),
                        ("PredefinedBeamType", 0),
                        ("Diameter", 0.22),
                        ("A", math.pi*(0.22/2)**2 ),
                        ("Diameter", 0.22),
                        ("E", 195.0E6),
                        ("w",1),
                        ("Lspacing", 1.5),
                        ("SkinResistance", "Multi-linear"), #1
                        ("SkinResistanceMultiLinear", "Axial skin resistance table"),
                        ("SkinResistanceTable", [0, 150, 1, 200])]
with open("ANCHOR_GROUT_Multilinear.json", "w") as write_file:
    json.dump(grout_multilinear_params, write_file)
    
# Strut
strut_elastic_params = [("MaterialName", "Strut elastic"),
                         ("Colour", 0),
                         ("Elasticity", 0),
                         ("EA", 170E3),
                         ("Lspacing", 1.5)]
with open("STRUT_Elastic.json", "w") as write_file:
    json.dump(strut_elastic_params, write_file)
    
strut_elastoplastic_params = [("MaterialName", "Strut elastoplastic"),
                         ("Colour", 0),
                         ("Elasticity", 1),
                         ("EA", 170E3),
                         ("FMaxTens", 1000000000000),
                         ("FMaxComp", 1000000000000),
                         ("Lspacing", 1.5)]

with open("STRUT_Elastoplastic.json", "w") as write_file:
    json.dump(strut_elastoplastic_params, write_file)