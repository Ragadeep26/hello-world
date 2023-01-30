#!/usr/bin/env python3

import os

#==============================================================================
# ## Open Plaxis Scripting Server
# from subprocess import check_output, call, Popen, PIPE
# from time import sleep
# os.chdir(r"C:\Program Files\Plaxis\PLAXIS 2D")
# #call("Plaxis2DXInput.exe --AppserverPassword=mypassword --AppServerPort=10000\n", shell=True)
# #call("CMD /k Plaxis2DXInput.exe", shell=True)
# process = Popen("Plaxis2DXInput.exe --AppserverPassword=mypassword --AppServerPort=10000", stdout=PIPE, stderr=PIPE)
# stdout, stderr = process.communicate()
# print(stdout)
# call("dir", shell=False)
# sleep(5.)
#==============================================================================

PORT = 10000
PLAXIS_SCRIPTING_PATH = r'C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages'
PLAXIS_RUN_PATH = r'C:\Users\nya\Packages\Moniman\tests'
os.chdir(PLAXIS_RUN_PATH)


## Append Python path to use Plaxis scripting funtionalities
import sys
#sys.path.append(r"C:\Program Files\Plaxis\PLAXIS 2D\python\Lib\site-packages") # new path 
sys.path.append(PLAXIS_SCRIPTING_PATH) # new path 
#print(sys.path)

import imp
found_module = imp.find_module('plxscripting', [PLAXIS_SCRIPTING_PATH])
print('found plxscripting module:', found_module)
plxscripting = imp.load_module('plxscripting',*found_module)

from plxscripting.easy import *

## Initialize Input server which has been opened at Port 10000
try:
    s_i, g_i = new_server('localhost', 10000, password='mypassword')
except:
    print("Please start Plaxis Scripting Server first!")


## 01. Start a new project
s_i.new()
projecttitle = 'Test automating Plaxis 2D simulation' #add your own title here

g_i.Project.setproperties("Title", projecttitle,
                          "UnitForce", "kN",
                          "UnitLength", "m",
                          "UnitTime", "day",
                          "ModelType", "Plane strain",
                          "ElementType", "15-Noded")

## 02. Define soil layers
xmin, xmax, ymin, ymax = -50, 50, 0, 20
g_i.SoilContour.initializerectangular(xmin, ymin, xmax, ymax)
a_borehole = g_i.borehole(0)
g_i.soillayer(0)
g_i.setsoillayerlevel(a_borehole, 0, 20)
a_borehole.Head = 10
# Add more soil layer???
#g_i.soillayer(5)
#g_i.setsoillayerlevel(a_borehole, 1, -15)

# define Clay material
clay_E = 5E3
clay_nu = 0.35
clay_G = clay_E/(2*(1+clay_nu))
Clay = g_i.soilmat("MaterialName", "Clay",
                   "Colour", 15262369,
                   "SoilModel", 2,
                   "DrainageType", 0,
                   "gammaUnsat", 16,
                   "gammaSat", 18,
                   "Gref", clay_G,
                   "nu",clay_nu,
                   "cref",5,
                   "phi",20,
                   "psi",0
                   )

# assign Clay material
g_i.Soils[0].setmaterial(Clay)


## 03. Create raft
g_i.gotostructures()

raft_thick = 0.6
pg_xmin = -15
pg_xmax = 15
pg_ymin = 20
pg_ymax = pg_ymin+raft_thick
raft, r_soil = g_i.polygon(pg_xmin,pg_ymin,
                        pg_xmax,pg_ymin,
                        pg_xmax,pg_ymax,
                        pg_xmin,pg_ymax)
                
# define concrete material
concrete_E = 30E6
concrete_nu = 0.35
concrete_G = concrete_E / (2 * (1 + concrete_nu))
Concrete = g_i.soilmat("MaterialName", "Concrete",
                       "Colour", 12632256,
                       "SoilModel", 1,
                       "DrainageType", 4,
                       "K0Determination", "Automatic",
                       "gammaUnsat", 24,
                       "Gref", concrete_G,
                       "nu", clay_nu,
                       "cref", concrete_nu
                       )
# and assign the concrete material
#g_i.Polygons[-1].Soil.setmaterial(Concrete)
raft.Soil.setmaterial(Concrete)

## 04. Create loads
g_i.lineload(pg_xmin,pg_ymax,pg_xmax,pg_ymax)
g_i.pointload(pg_xmin,pg_ymax)
g_i.pointload(0,pg_ymax)
g_i.pointload(pg_xmax,pg_ymax)

## 05. Generate the mesh
g_i.gotomesh()
g_i.refine(g_i.Polygon_1)
g_i.mesh(0.04002)
#g_i.viewmesh()

## 06. Initial phase: only soil
g_i.gotostages()
g_i.deactivate(g_i.Polygons, g_i.InitialPhase)
#K0 is used to generate the initial stresses, explicit setting is not necessary

## 07. First phase: construct concrete raft
raftphase = g_i.phase(g_i.InitialPhase)
g_i.setcurrentphase(raftphase)
raftphase.Identification = 'Construct concrete raft'
g_i.activate(g_i.Polygons, raftphase)


## 08. Second phase: activate live load on raft
loadphase = g_i.phase(raftphase)
g_i.setcurrentphase(loadphase)
loadphase.Identification = 'Live load on raft'
for ll in g_i.LineLoads:
    ll.activate(loadphase)
    ll.qy_start.set(loadphase, -15)


## 09. Third phase: build Floor 1
floorphase = g_i.phase(loadphase)
g_i.setcurrentphase(floorphase)
floorphase.Identification = 'Build floor 1'
columnload = -150
for pointload in g_i.PointLoads:
    pointload.activate(floorphase)
    pointload.Fy.set(floorphase, columnload)

#g_i.PointLoad_1_1.activate(floorphase)
#g_i.PointLoad_1_1.Fy.set(floorphase, columnload)
#g_i.PointLoad_2_1.activate(floorphase)
#g_i.PointLoad_2_1.Fy.set(floorphase, columnload)
#g_i.PointLoad_3_1.activate(floorphase)
#g_i.PointLoad_3_1.Fy.set(floorphase, columnload)

## 10. Fourth phase: Wind load
windphase = g_i.phase(floorphase)
g_i.setcurrentphase(windphase)
windphase.Identification = 'Wind load on floor 1'
windphase.Comments = 'Wind load: 25% of vertical load of floor'
#g_i.PointLoad_1_1.Fx.set(windphase, 0.25*columnload)
#g_i.PointLoad_2_1.Fx.set(windphase, 0.25*columnload)
#g_i.PointLoad_3_1.Fx.set(windphase, 0.25*columnload)
for pointload in g_i.PointLoads:
    pointload.activate(windphase)
    pointload.Fx.set(windphase, 0.25*columnload)

## 11. Third phase: build Floor 2
floorphase = g_i.phase(floorphase)
g_i.setcurrentphase(floorphase)
floorphase.Identification = 'Build floor 2'
#g_i.PointLoad_1_1.Fy.set(floorphase, 2*columnload)
#g_i.PointLoad_2_1.Fy.set(floorphase, 2*columnload)
#g_i.PointLoad_3_1.Fy.set(floorphase, 2*columnload)
for pointload in g_i.PointLoads:
    pointload.activate(floorphase)
    pointload.Fy.set(floorphase, 2*columnload)

windphase = g_i.phase(floorphase)
g_i.setcurrentphase(windphase)
windphase.Identification = 'Wind load on floor 2'
windphase.Comments = 'Wind load: 25% of vertical load of floor'
for pointload in g_i.PointLoads:
    pointload.activate(windphase)
    pointload.Fx.set(windphase, 0.25*2*columnload)


## 12. Settings prior to calculation
for phase in g_i.Phases[1:]:
    phase.MaxCores = 1


## 13. Calculate model
g_i.calculate()

## 14. Compute building rotation using Output
phase_i = windphase
outputport = g_i.view(phase_i)
s_o, g_o = new_server('localhost', outputport, password='mypassword')

# search for the expected phase in Output
phase_o = None
for any_phase in g_o.Phases[:]:
    if any_phase.Name.value == phase_i.Name.value:
        phase_o = any_phase
        print(phase_o)
        #dir(phase_o)

if phase_o:
    # use phase_o to obtain results
    r_uy = g_o.ResultTypes.Soil.Uy
    uy_l = float(g_o.getsingleresult(phase_o, r_uy, (pg_xmin, pg_ymax)))
    uy_r = float(g_o.getsingleresult(phase_o, r_uy, (pg_xmax, pg_ymax)))
    
    # compute differential settlement
    duy = uy_l - uy_r
    # compute width of raft
    w = pg_xmax - pg_xmin
    # compute rotation
    rotation = w/duy
    
    print("The rotation for {} is: 1 : {:.0f}".format(phase_o.Name.value, rotation))

#s_o.close()