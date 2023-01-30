# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 17:20:25 2018

@author: nya
"""
PLAXIS2D_SCRIPTING = r'C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages'
PLAXIS2D = r'C:\Program Files\Plaxis\PLAXIS 2D'
MONIMAN = r'C:\Users\nya\Packages\Moniman'
MONIMAN_OUTPUTS = r'C:\Users\nya\Packages\Moniman\MONIMAN_OUTPUTS'
import sys, os
sys.path.append(PLAXIS2D_SCRIPTING)
sys.path.append(PLAXIS2D)
sys.path.append(MONIMAN)
sys.path.append(MONIMAN_OUTPUTS)

from solver.plaxis2d.output_commands import get_soilsection_uy
#from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots
from common.boilerplate import start_plaxis
from plxscripting.easy import new_server
import numpy as np
import matplotlib.pyplot as plt

print('Launched PLAXIS2D OUTPUT again\n')
subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)
output_database = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.p2dx')
s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
s_o.open(output_database)

point1 = (0, 10)
point2 = (40, 10)
(x_soilsection, y_soilsection, Uy_section) = get_soilsection_uy(MONIMAN_OUTPUTS, g_o, point1, point2, 10E-1, 1)
print(len(x_soilsection))
print(len(y_soilsection))
print(len(Uy_section)) 

plt.fill_between(np.array(x_soilsection), np.array(y_soilsection) + 500*np.array(Uy_section), np.array(y_soilsection), hatch = '|', facecolor = 'blue')

#plt.plot(np.array(x_soilsection), np.array(y_soilsection))
#plt.plot(np.array(x_soilsection), np.array(y_soilsection) + np.array(Uy_section))

#canvas = MyStaticMplCanvasSubplots()
#canvas.plot_soilsection_settlement(x_soilsection, y_soilsection, np.array(Uy_section)*1000, 'Ux [mm]', 'Y [m]')