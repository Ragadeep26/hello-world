# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 13:52:06 2018

@author: nya
"""
import numpy as np
import json

E = 40.0E3
nu = 0.3
G = E/(2*(1 + nu))
cobbles_MC = [("MaterialName", "Cobbles"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 1.0),
               ("perm_vertical_axis", 1.0),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 40),
               ("psi", 10),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*40/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Cobbles_MC.json", "w") as write_file:    
    json.dump(cobbles_MC, write_file)

E = 120.0E3
nu = 0.3
G = E/(2*(1 + nu))
gravel_dense_MC = [("MaterialName", "Gravel dense"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.001),
               ("perm_vertical_axis", 0.001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 37.5),
               ("psi", 7.5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*37.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Gravel_dense_MC.json", "w") as write_file:    
    json.dump(gravel_dense_MC, write_file)
    

E = 90.0E3
nu = 0.3
G = E/(2*(1 + nu))
gravel_medium_MC = [("MaterialName", "Gravel medium"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.005),
               ("perm_vertical_axis", 0.005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 35),
               ("psi", 5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*35/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Gravel_medium_MC.json", "w") as write_file:    
    json.dump(gravel_medium_MC, write_file)

E = 50.0E3
nu = 0.3
G = E/(2*(1 + nu))
gravel_loose_MC = [("MaterialName", "Gravel loose"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.01),
               ("perm_vertical_axis", 0.01),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 32.5),
               ("psi", 2.5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*32.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Gravel_loose_MC.json", "w") as write_file:    
    json.dump(gravel_loose_MC, write_file)    
    
E = 65.0E3
nu = 0.3
G = E/(2*(1 + nu))
sand_dense_MC = [("MaterialName", "Sand dense"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0001),
               ("perm_vertical_axis", 0.0001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 35),
               ("psi", 5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*35/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Sand_dense_MC.json", "w") as write_file:    
    json.dump(sand_dense_MC, write_file)

    
E = 40.0E3
nu = 0.3
G = E/(2*(1 + nu))
sand_medium_MC = [("MaterialName", "Sand medium"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.0005),
               ("perm_vertical_axis", 0.0005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 32.5),
               ("psi", 2.5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*32.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Sand_medium_MC.json", "w") as write_file:    
    json.dump(sand_medium_MC, write_file)

    
E = 20.0E3
nu = 0.3
G = E/(2*(1 + nu))
sand_loose_MC = [("MaterialName", "Sand loose"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.001),
               ("perm_vertical_axis", 0.001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 30),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*30/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Sand_loose_MC.json", "w") as write_file:    
    json.dump(sand_loose_MC, write_file)

E = 20.0E3
nu = 0.3
G = E/(2*(1 + nu))
silt_hard_MC = [("MaterialName", "Silt hard"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0000001),
               ("perm_vertical_axis", 0.0000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 10),
               ("phi", 27.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*27.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Silt_hard_MC.json", "w") as write_file:    
    json.dump(silt_hard_MC, write_file)

E = 14.0E3
nu = 0.3
G = E/(2*(1 + nu))
silt_stiff_MC = [("MaterialName", "Silt stiff"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 21),
               ("gammaSat", 22),
               ("perm_primary_horizontal_axis", 0.0000005),
               ("perm_vertical_axis", 0.0000005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 5),
               ("phi", 27.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*27.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Silt_stiff_MC.json", "w") as write_file:    
    json.dump(silt_stiff_MC, write_file)
    
E = 8.0E3
nu = 0.35
G = E/(2*(1 + nu))
silt_firm_MC = [("MaterialName", "Silt firm"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20.5),
               ("gammaSat", 21.5),
               ("perm_primary_horizontal_axis", 0.000001),
               ("perm_vertical_axis", 0.000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 2),
               ("phi", 27.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*27.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Silt_firm_MC.json", "w") as write_file:    
    json.dump(silt_firm_MC, write_file)
    
E = 4.0E3
nu = 0.4
G = E/(2*(1 + nu))
silt_soft_MC = [("MaterialName", "Silt soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.000005),
               ("perm_vertical_axis", 0.000005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 25),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*25/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Silt_soft_MC.json", "w") as write_file:    
    json.dump(silt_soft_MC, write_file)
    
E = 2.0E3
nu = 0.4
G = E/(2*(1 + nu))
silt_very_soft_MC = [("MaterialName", "Silt very soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.00001),
               ("perm_vertical_axis", 0.00001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 22.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*22.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Silt_very_soft_MC.json", "w") as write_file:    
    json.dump(silt_very_soft_MC, write_file)
    
E = 50.0E3
nu = 0.3
G = E/(2*(1 + nu))
clay_hard_MC = [("MaterialName", "Clay hard"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 0.000000001),
               ("perm_vertical_axis", 0.000000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 50),
               ("phi", 17.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*17.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Clay_hard_MC.json", "w") as write_file:    
    json.dump(clay_hard_MC, write_file)
    
E = 30.0E3
nu = 0.35
G = E/(2*(1 + nu))
clay_stiff_MC = [("MaterialName", "Clay stiff"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.000000005),
               ("perm_vertical_axis", 0.000000005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 25),
               ("phi", 17.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*17.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Clay_stiff_MC.json", "w") as write_file:    
    json.dump(clay_stiff_MC, write_file)
    
E = 10.0E3
nu = 0.4
G = E/(2*(1 + nu))
clay_firm_MC = [("MaterialName", "Clay firm"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.00000001),
               ("perm_vertical_axis", 0.00000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 10),
               ("phi", 17.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*17.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Clay_firm_MC.json", "w") as write_file:    
    json.dump(clay_firm_MC, write_file)
    
E = 4.0E3
nu = 0.42
G = E/(2*(1 + nu))
clay_soft_MC = [("MaterialName", "Clay soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.00000005),
               ("perm_vertical_axis", 0.00000005),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 15),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*15/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Clay_soft_MC.json", "w") as write_file:    
    json.dump(clay_soft_MC, write_file)
    
E = 2.0E3
nu = 0.42
G = E/(2*(1 + nu))
clay_very_soft_MC = [("MaterialName", "Clay very soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 17),
               ("gammaSat", 18),
               ("perm_primary_horizontal_axis", 0.0000001),
               ("perm_vertical_axis", 0.0000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 10),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*10/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Clay_very_soft_MC.json", "w") as write_file:    
    json.dump(clay_very_soft_MC, write_file)

E = 300.0E3
nu = 0.3
G = E/(2*(1 + nu))
marl_hard_MC = [("MaterialName", "Marl hard"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 24),
               ("gammaSat", 25),
               ("perm_primary_horizontal_axis", 0.00000000001),
               ("perm_vertical_axis", 0.00000000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 10),
               ("phi", 35),
               ("psi", 5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*35/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Marl_hard_MC.json", "w") as write_file:    
    json.dump(marl_hard_MC, write_file)

E = 150.0E3
nu = 0.3
G = E/(2*(1 + nu))
marl_stiff_MC = [("MaterialName", "Marl stiff"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 22),
               ("gammaSat", 23),
               ("perm_primary_horizontal_axis", 0.0000000001),
               ("perm_vertical_axis", 0.0000000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 5),
               ("phi", 32.5),
               ("psi", 2.5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*32.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Marl_stiff_MC.json", "w") as write_file:    
    json.dump(marl_stiff_MC, write_file)
    
E = 100.0E3
nu = 0.3
G = E/(2*(1 + nu))
marl_firm_MC = [("MaterialName", "Marl firm"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 20),
               ("gammaSat", 21),
               ("perm_primary_horizontal_axis", 0.000000001),
               ("perm_vertical_axis", 0.000000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 3),
               ("phi", 30.0),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*30/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Marl_firm_MC.json", "w") as write_file:    
    json.dump(marl_firm_MC, write_file)    


E = 60.0E3
nu = 0.3
G = E/(2*(1 + nu))
marl_soft_MC = [("MaterialName", "Marl soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 19),
               ("gammaSat", 20),
               ("perm_primary_horizontal_axis", 0.00000001),
               ("perm_vertical_axis", 0.00000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 25.0),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*25/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Marl_soft_MC.json", "w") as write_file:    
    json.dump(marl_soft_MC, write_file)   
    
E = 30.0E3
nu = 0.3
G = E/(2*(1 + nu))
marl_very_soft_MC = [("MaterialName", "Marl very soft"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.0000001),
               ("perm_vertical_axis", 0.0000001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 22.5),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*22.5/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Marl_very_soft_MC.json", "w") as write_file:    
    json.dump(marl_very_soft_MC, write_file)      

   
E = 15.0E3
nu = 0.3
G = E/(2*(1 + nu))
fill_MC = [("MaterialName", "Fill"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 18),
               ("gammaSat", 19),
               ("perm_primary_horizontal_axis", 0.001),
               ("perm_vertical_axis", 0.001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 0),
               ("phi", 30),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*30/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Fill_MC.json", "w") as write_file:    
    json.dump(fill_MC, write_file)
    
E = 500.0E3
nu = 0.2
G = E/(2*(1 + nu))
rock_intact_MC = [("MaterialName", "Rock intact"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 25),
               ("gammaSat", 26),
               ("perm_primary_horizontal_axis", 0.00001),
               ("perm_vertical_axis", 0.00001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 100),
               ("phi", 40),
               ("psi", 10),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*40/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Rock_intact_MC.json", "w") as write_file:    
    json.dump(rock_intact_MC, write_file)
    
E = 200.0E3
nu = 0.25
G = E/(2*(1 + nu))
rock_m_weathered_MC = [("MaterialName", "Rock m. weathered"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 24),
               ("gammaSat", 25),
               ("perm_primary_horizontal_axis", 0.00001),
               ("perm_vertical_axis", 0.00001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 50),
               ("phi", 35),
               ("psi", 5),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*35/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Rock_m._weathered_MC.json", "w") as write_file:    
    json.dump(rock_m_weathered_MC, write_file)
    
E = 50.0E3
nu = 0.3
G = E/(2*(1 + nu))
rock_h_weathered_MC = [("MaterialName", "Rock h. weathered"),
               ("Colour", 15262369),
               ("SoilModel", 2), #2 for Mohr-Coulomb
               ("DrainageType", 0), # Drained
               ("gammaUnsat", 23),
               ("gammaSat", 24),
               ("perm_primary_horizontal_axis", 0.00001),
               ("perm_vertical_axis", 0.00001),
               ("Gref", G),
               ("nu", nu),
               ("cref", 25),
               ("phi", 30),
               ("psi", 0),
               ("K0Determination", 1),  # 0: Manual, 1: Automatic (default)
               ("K0Primary", 1.0 - np.sin(np.pi*30/180)),  # K0Secondary = K0Primary
               ("Rinter", 0.67)]
with open("Rock_h._weathered_MC.json", "w") as write_file:    
    json.dump(rock_h_weathered_MC, write_file)