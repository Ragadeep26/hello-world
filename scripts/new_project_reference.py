####!/usr/bin/env python3


localhostport = 10000
plaxis_path = r'C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages'
#workdir = r'C:\Users\nya\Packages\Moniman\scripts'
#print(workdir)
#from subprocess import Popen
#p = Popen(r'Plaxis2DXInput.exe --AppserverPassword=mypassword --AppServerPort=10000', \
#          cwd=r'C:\Program Files\Plaxis\PLAXIS 2D')

import sys
sys.path.append(r"C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages") # new path 
print(sys.path)

import imp
found_module = imp.find_module('plxscripting', [plaxis_path])
print('found plxscripting module:', found_module)
plxscripting = imp.load_module('plxscripting',*found_module)

from plxscripting.easy import *

# Connect to the scripting server opened at Port 10000
s_i, g_i = new_server('localhost', 10000, password='mypassword')
s_i.new()

# buid the model
g_i.SoilContour.initializerectangular(0, 0, 10, 10)
g_i.borehole(0)
g_i.soillayer(10)
material = g_i.soilmat()
material.setproperties("SoilModel", 1, "gammaUnsat", 16,
"gammaSat", 20, "Gref", 10000)
g_i.Soils[0].Material = material

g_i.gotostructures()
g_i.lineload((3, 0), (7, 0))

g_i.gotomesh()
g_i.mesh(0.2)

output_port = g_i.selectmeshpoints()
s_o, g_o = new_server('localhost', output_port, password='mypassword')
g_o.addcurvepoint('node', g_o.Soil_1_1, (5, 0))
g_o.update()

g_i.gotostages()
phase1 = g_i.phase(g_i.Phases[0])
g_i.LineLoads[0].Active[phase1] = True
g_i.calculate()

output_port = g_i.view(phase1)
s_o, g_o = new_server('localhost', output_port, password='mypassword')
utot = g_o.getcurveresults(g_o.CurvePoints.Nodes.value[0], g_o.Phases[1], g_o.Soil.Utot)

print(utot)

g_i.save(r'D:\Data\1Projekt\Plaxis_Tutorials\Tutorials\Tutorial_Python\scripting_sample')
