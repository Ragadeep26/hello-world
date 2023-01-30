#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 09:51:45 2018

@author: nya
"""
import sys
import os
import shutil
import subprocess
from datetime import datetime#, timedelta
import socket
from PyQt5.QtWidgets import (QAction, qApp, QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout)
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import pyqtSlot
from gui.gui_main_matplotlib import MyStaticMplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.gui_main_ui import Ui_MainWindow
from gui.gui_all_dialogs_ui import Ui_Dialog
from gui.gui_all_forms_ui import Ui_Form
from tools.text_logging import OutLog
from tools.file_tools import write_traceback_to_file
from system.system import get_uuid
from tools.file_tools import loadpy
from plaxman.plaxman import Plaxman
from plaxman.plaxman_combinedphases import Plaxman_CombinedPhases
from plaxman.plaxman_automatedphases_phreatic import Plaxman_AutomatedPhases_Phreatic
from plaxman.plaxman_automatedphases_steadystatewater import Plaxman_AutomatedPhases_SteadyStateWater
from backman.backman import Backman
from sensiman.sensiman import Sensiman
from optiman.optiman import Optiman
import solver.plaxis2d.input_scripting_commands as plaxis2d_input
from plaxman.plaxman_3d import Plaxman3D
from system.system import load_paths

# load PATHS.py
load_paths(r'common\\PATHS.py')
ACROBAT = sys.modules['moniman_paths']['ACROBAT']
        
class Moniman_EXEC():
    """ Moniman's main program executable
    """
       
    def __init__(self):
        """ Initialize Moniman's main window
        """
        app = QApplication(sys.argv)        
        MainWindow = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(MainWindow) 
        self.ui.splitter.setSizes([500, 500]) # resize widgets' size around splitter
        self.ui.splitter_2.setSizes([500, 150]) # resize widgets' size around splitter

        self.dialog = Ui_Dialog()   # object of Ui_Dialog class 
        self.form = Ui_Form()
        
        # Log outputs and errors
        sys.stdout = OutLog(self.ui.plainTextEdit, sys.stdout)
        sys.stderr = OutLog(self.ui.plainTextEdit, QColor(255,0,0))
        
        # Security
        self.uuids = {'Luan': '4333234C-334C-11B2-A85C-FE3F6408CBD9', 'Luan_VM': '11A63C42-D669-7E93-A784-8B95920AB4B3', 'Fadi': '38D55FCC-3406-11B2-A85C-870F4CCE931D', 'Semeone': '8779764C-23D3-11B2-A85C-DA310DC4C150', 
                      'Pablo':'2EBF7BCC-2069-11B2-A85C-F1A0045C188D', 'Workstation': '37412BE0-1295-11E5-9C43-BC0000680000',
                      'Mahesh_AbuDhabi': 'C3BEEACC-2529-11B2-A85C-F942566164D5', 'Mahesh_AbuDhabi_supercomputer': '28F4AD6A-FAA4-11E5-9C43-BC0000EE0000',
                      'Onur': '1A4BFF3E-970F-5D64-993A-A32388E142FF', 'Onur_RemoteDesktop': '453D1542-D2C7-FF17-4FE0-9B8E2D8D85D0', 'Onur_2nd_laptop': '6C90C44C-20AA-11B2-A85C-D9A7374AAA4C',
                      'Ragadeep': 'B0E66C4C-1FA5-11B2-A85C-CB4AD50CBBD4', 
                      'JingXien_Malaysia': '4C4C4544-0032-3810-8042-CAC04F484A32', 'YokeLin_Malaysia': '00CD17CC-2944-11B2-A85C-9F0A3F49A2EC', 'YongYau_Malaysia': '82EB3DCC-34F9-11B2-A85C-D35145CC4814',
                      'Adul_Rahman_Malaysia': '4C4C4544-0032-3710-8047-CAC04F484A32', 'JiaWei_Malaysia': '4C4C4544-0052-5A10-8047-C8C04F484A32',
                      'Adly_Egypt': 'E257244C-2923-11B2-A85C-884A54FD5617', 'Basanagouda': 'B633FE4C-2CA9-11B2-A85C-9F0DFBEC6AEE', 'Armel': '5C77E54C-20A8-11B2-A85C-F8BA82D49FC3',
                      'Philipp_Schober': 'C1DC0DCC-2DEC-11B2-A85C-EB7A09CDBC92'}

        self.uuids_temporary = {'Luan': '4333234C-334C-11B2-A85C-FE3F6408CBD9_'}    # for temporary users
        self.bauer_ip = ['10.6.13.102']                                             # legal IP addresses
            
        # Initially, MONIMAN has not been loaded
        self.isLoaded = False    # True if MONIMAN has been loaded

        # The main plot canvas
        # matplotlib canvas and toolbar
        self.plot_layout = QVBoxLayout(self.ui.widget)
        self.plot_canvas = MyStaticMplCanvas(self.ui.widget, width=5, height=4, dpi=100)        
        self.plot_toolbar = NavigationToolbar(self.plot_canvas, None)        
        self.plot_layout.addWidget(self.plot_toolbar)
        #self.plot_layout.addWidget(NavigationToolbar(self.plot_canvas, None))
        self.plot_layout.addWidget(self.plot_canvas)   

        # Plaxman
        self.plaxman = Plaxman(self.ui, self.plot_canvas)
        # Plaxman combined phases
        self.plaxman_cp = Plaxman_CombinedPhases(self.ui, self.plot_canvas)
        # Plaxman automated phases, select between options with phreatic water level and steady state groundwater flow
        self.plaxman_ap = Plaxman_AutomatedPhases_Phreatic(self.ui, self.plot_canvas)
        self.plaxman_ap_steadystate = Plaxman_AutomatedPhases_SteadyStateWater(self.ui, self.plot_canvas)

        # Plaxman3D
        self.plaxman3d = Plaxman3D()

        # Backman
        self.backman = Backman(self.plaxman)

        # Sensiman
        self.sensiman =  Sensiman(self.plaxman)

        # Optiman
        #self.optiman = Optiman(self.plaxman_ap)
        self.optiman = Optiman(self.plaxman)

        # Edit > Paths
        self.ui.actionPaths.triggered.connect(lambda: self.dialog.open_text_edit(r'common\\PATHS.py'))
        self.ui.actionPaths.triggered.connect(self.plaxman.set_paths_and_file)

        # File > New
        self.ui.actionNew_project.triggered.connect(self.new)

        # File > Save
        self.ui.actionSave.triggered.connect(self.save)

        # File > Save As
        self.ui.actionSave_As.triggered.connect(self.save_as)

        # File > Load
        self.ui.actionLoad.triggered.connect(self.load)

        # Walls > Generate input file (for Walls)
        #self.ui.actionInput_file.triggered.connect()

        # Walls > Calculate (with Walls)
        #self.ui.actionCalculate_walls.triggered.connect()

        # Walls > Determine embedment depth (with Walls)
        #self.ui.actionDetermine_embedment_depth.triggered.connect()

        # Help > About
        self.ui.actionAbout.triggered.connect(self.form.open_form_About)

        # Help > Literature
        self.ui.actionLiterature.triggered.connect(self.form.open_form_Literature)

        # Help > PDF Tutorials
        self.ui.actionRetaining_wall_with_anchors.triggered.connect(self.open_PDF_tutorial1)
        self.ui.actionRetaining_wall_with_struts.triggered.connect(self.open_PDF_tutorial2)
        self.ui.actionRetaining_wall_with_berm_and_struts_reconstruction.triggered.connect(self.open_PDF_tutorial3)

        # Toolbar for file actions
        exitAct = QAction(QIcon(r'icons\exit.png'), 'Exit', MainWindow)
        exitAct.triggered.connect(qApp.quit)
        openAct = QAction(QIcon(r'icons\open.png'), 'Open project', MainWindow)
        openAct.triggered.connect(self.load)
        newAct = QAction(QIcon(r'icons\new.png'), 'New project', MainWindow)
        newAct.triggered.connect(self.new)
        saveAct = QAction(QIcon(r'icons\save.png'), 'Save project', MainWindow)
        saveAct.triggered.connect(self.save)
        self.toolbar_file = MainWindow.addToolBar('File')
        self.toolbar_file.addAction(exitAct)
        self.toolbar_file.addAction(openAct)
        self.toolbar_file.addAction(newAct)
        self.toolbar_file.addAction(saveAct)
        # Toolbar for Plaxman
        soilAct = QAction(QIcon(r'icons\soils.png'), 'Soils', MainWindow)
        soilAct.triggered.connect(self.go_to_soil)
        wallAct = QAction(QIcon(r'icons\wall.png'), 'Wall', MainWindow)
        wallAct.triggered.connect(self.go_to_wall)
        anchorAct = QAction(QIcon(r'icons\anchors.png'), 'Anchors', MainWindow)
        anchorAct.triggered.connect(self.go_to_anchors)
        strutAct = QAction(QIcon(r'icons\strut.png'), 'Struts', MainWindow)
        strutAct.triggered.connect(self.go_to_struts)
        lineloadAct = QAction(QIcon(r'icons\lineload.png'), 'Line loads', MainWindow)
        lineloadAct.triggered.connect(self.go_to_lineloads)
        pointloadAct = QAction(QIcon(r'icons\pointload.png'), 'Point loads', MainWindow)
        pointloadAct.triggered.connect(self.go_to_pointloads)
        soilpolygonAct = QAction(QIcon(r'icons\soilpolygon.png'), 'Soil polygons', MainWindow)
        soilpolygonAct.triggered.connect(self.go_to_soilpolygons)
        meshAct = QAction(QIcon(r'icons\mesh.png'), 'Mesh', MainWindow)
        meshAct.triggered.connect(self.go_to_mesh)
        self.toolbar_plaxman = MainWindow.addToolBar('Plaxman')
        self.toolbar_plaxman.addAction(soilAct)
        self.toolbar_plaxman.addAction(wallAct)
        self.toolbar_plaxman.addAction(anchorAct)
        self.toolbar_plaxman.addAction(strutAct)
        self.toolbar_plaxman.addAction(lineloadAct)
        self.toolbar_plaxman.addAction(pointloadAct)
        self.toolbar_plaxman.addAction(soilpolygonAct)
        self.toolbar_plaxman.addAction(meshAct)
        # Toolbar for Phases
        soilclusterAct = QAction(QIcon(r'icons\soilcluster.png'), 'Soil clusters', MainWindow)
        soilclusterAct.triggered.connect(self.go_to_soilclusters)
        automatedphasesAct = QAction(QIcon(r'icons\automation.png'), 'Automated phases', MainWindow)
        automatedphasesAct.triggered.connect(self.go_to_automated_phases)
        calculateAct = QAction(QIcon(r'icons\plaxis2d.png'), 'Calculate', MainWindow)
        calculateAct.triggered.connect(self.plaxman.calculate)
        outputAct = QAction(QIcon(r'icons\output.png'), 'Wall forces', MainWindow)
        outputAct.triggered.connect(self.plaxman.view_wall_outputs)
        self.toolbar_phases = MainWindow.addToolBar('Phases')
        self.toolbar_phases.addAction(soilclusterAct)
        self.toolbar_phases.addAction(automatedphasesAct)
        self.toolbar_phases.addAction(calculateAct)
        self.toolbar_phases.addAction(outputAct)
        # Toolbar for Sensiman/ Backman/ Optiman
        sensimanAct = QAction(QIcon(r'icons\bars.png'), 'Sensitivity', MainWindow)
        sensimanAct.triggered.connect(self.go_to_sensitivity)
        #backmanAct = QAction(QIcon(r'icons\backward.png'), 'Back-analysis', MainWindow)
        backmanAct = QAction(QIcon(r'icons\bayes.png'), 'Back-analysis', MainWindow)
        backmanAct.triggered.connect(self.go_to_backanalysis)
        optimanAct = QAction(QIcon(r'icons\dart.png'), 'Optimization', MainWindow)
        optimanAct.triggered.connect(self.go_to_optimization)
        self.toolbar_tools = MainWindow.addToolBar('Tools')
        self.toolbar_tools.addAction(sensimanAct)
        self.toolbar_tools.addAction(backmanAct)
        self.toolbar_tools.addAction(optimanAct)


        # Connect with botton clicked events
        self.ui.pushButton_2.clicked.connect(self.plaxman.update_geometry)                  # Start by updating geometry
        self.ui.pushButton.clicked.connect(self.plaxman.add_borehole)                       # Create borehole        
        self.ui.pushButton_96.clicked.connect(self.plaxman.edit_borehole)                   # Edit borehole        
        self.ui.pushButton_11.clicked.connect(self.plaxman.remove_borehole)                 # Remove borehole
        self.ui.pushButton_4.clicked.connect(self.plaxman.add_layer)                        # Add layer
        self.ui.pushButton_12.clicked.connect(self.plaxman.remove_layer)                    # Remove layer
        self.ui.pushButton_147.clicked.connect(self.plaxman.edit_all_layers)                # View/ edit all layers
        self.ui.pushButton_3.clicked.connect(self.plaxman.define_soil_material)             # Edit material
        self.ui.pushButton_47.clicked.connect(self.plaxman.change_soil_properties)          # Change soil properties
        self.ui.pushButton_144.clicked.connect(self.plaxman.edit_all_soils)                 # View/ change soil properties for all soils
        self.ui.pushButton_67.clicked.connect(self.plaxman.delete_soil)                     # Change soil properties
        self.ui.pushButton_5.clicked.connect(self.plaxman.assign_material)                  # Assign material
        self.ui.pushButton_13.clicked.connect(self.plaxman.undo_assign_material)            # Undo assigning material        
        self.ui.pushButton_146.clicked.connect(self.plaxman.undo_assign_materials)          # Undo assigning material for all layers 
        self.ui.pushButton_8.clicked.connect(self.plaxman.define_wall)                      # Define wall
        self.ui.pushButton_48.clicked.connect(self.plaxman.change_wall_properties)          # Change wall properties
        self.ui.pushButton_6.clicked.connect(self.plaxman.delete_wall_material)             # Delete the selected wall material
        self.ui.pushButton_7.clicked.connect(self.plaxman.add_wall)                         # Add wall
        self.ui.pushButton_7.clicked.connect(self.plaxman_cp.update_walls)                  # Display walls in Plaxman combined phases
        self.ui.pushButton_7.clicked.connect(self.plaxman_ap.update_walls)                  # Display walls in Plaxman automated phases
        self.ui.pushButton_14.clicked.connect(self.plaxman.remove_wall)                     # Remove wall
        self.ui.pushButton_14.clicked.connect(self.plaxman_cp.update_walls)                  # Display walls in Plaxman combined phases
        self.ui.pushButton_14.clicked.connect(self.plaxman_ap.update_walls)                  # Display walls in Plaxman automated phases
        self.ui.pushButton_9.clicked.connect(self.plaxman.edit_strand)                      # Edit strand
        self.ui.pushButton_49.clicked.connect(self.plaxman.change_strand_properties)        # Change strand properties
        self.ui.pushButton_16.clicked.connect(self.plaxman.edit_grout)                      # Edit grout
        self.ui.pushButton_50.clicked.connect(self.plaxman.change_grout_properties)         # Change grout properties
        self.ui.pushButton_10.clicked.connect(self.plaxman.add_ground_anchor)               # Add ground anchor
        self.ui.pushButton_10.clicked.connect(self.plaxman_cp.update_ground_anchors)        # Display ground anchors in Plaxman combined phases
        self.ui.pushButton_15.clicked.connect(self.plaxman.remove_ground_anchor)            # Remove ground anchor
        self.ui.pushButton_15.clicked.connect(self.plaxman_cp.update_ground_anchors)        # Display ground anchors in Plaxman combined phases
        self.ui.pushButton_21.clicked.connect(self.plaxman.edit_strut)                      # Edit strut
        self.ui.pushButton_51.clicked.connect(self.plaxman.change_strut_properties)         # Change strut properties
        self.ui.pushButton_22.clicked.connect(self.plaxman.add_strut)                       # Add strut
        self.ui.pushButton_22.clicked.connect(self.plaxman_cp.update_struts)                # Display struts in Combined phases
        self.ui.pushButton_23.clicked.connect(self.plaxman.remove_strut)                    # Remove strut
        self.ui.pushButton_23.clicked.connect(self.plaxman_cp.update_struts)                # Display struts in Combined phases
        self.ui.pushButton_17.clicked.connect(self.plaxman.add_lineload)                    # Add Lineload
        self.ui.pushButton_17.clicked.connect(self.plaxman_cp.update_lineloads)             # Display line loads in Plaxman combined phases
        self.ui.pushButton_18.clicked.connect(self.plaxman.remove_lineload)                 # Remove a line load
        self.ui.pushButton_18.clicked.connect(self.plaxman_cp.update_lineloads)             # Display line loads in Plaxman combined phases
        self.ui.pushButton_20.clicked.connect(self.plaxman.add_pointload)                   # Add a point load
        self.ui.pushButton_20.clicked.connect(self.plaxman_cp.update_pointloads)            # Display point loads in Plaxman combined phases
        self.ui.pushButton_19.clicked.connect(self.plaxman.remove_pointload)                # Remove Lineload
        self.ui.pushButton_19.clicked.connect(self.plaxman_cp.update_pointloads)            # Display point loads in Plaxman combined phases
        self.ui.pushButton_24.clicked.connect(self.plaxman.add_soilcluster)                 # Add soil cluster
        self.ui.pushButton_24.clicked.connect(self.plaxman_cp.update_soilclusters)          # Display soil clusters in Plaxman combined phases
        self.ui.pushButton_25.clicked.connect(self.plaxman.remove_soilcluster)              # Remove soil cluster
        self.ui.pushButton_25.clicked.connect(self.plaxman_cp.update_soilclusters)          # Display soil clusters in Plaxman combined phases
        self.ui.pushButton_26.clicked.connect(self.plaxman.add_waterlevel)                  # Add waterlevel  
        self.ui.pushButton_26.clicked.connect(self.plaxman_cp.update_waterlevels)           # Display waterlevels in Plaxman combined phases
        self.ui.pushButton_27.clicked.connect(self.plaxman.remove_waterlevel)               # Remove waterlevel
        self.ui.pushButton_27.clicked.connect(self.plaxman_cp.update_waterlevels)           # Display waterlevels in Plaxman combined phases
        self.ui.pushButton_36.clicked.connect(self.plaxman.apply_mesh)                      # Apply mesh
        self.ui.pushButton_31.clicked.connect(self.plaxman.select_struts)                   # Select struts for phase   
        self.ui.pushButton_32.clicked.connect(self.plaxman.select_anchors)                  # Select ground anchors for phase 
        self.ui.pushButton_33.clicked.connect(self.plaxman.select_soilclusters)             # Select soil clusters for phase 
        self.ui.pushButton_34.clicked.connect(self.plaxman.waterlevel_select_soilclusters)  # Select soil clusters for assigning user water level
        self.ui.pushButton_29.clicked.connect(self.plaxman.add_predefined_phase)            # Add a predefined phase
        self.ui.pushButton_30.clicked.connect(self.plaxman.remove_phase)                    # Remove a predefined phase
        self.ui.pushButton_28.clicked.connect(self.plaxman.add_drain)                       # Add drain
        self.ui.pushButton_28.clicked.connect(self.plaxman_cp.update_drain)                 # Display drain in Plaxman combined phases
        self.ui.pushButton_37.clicked.connect(self.plaxman.remove_drain)                    # Remove drain
        self.ui.pushButton_37.clicked.connect(self.plaxman_cp.update_drain)                 # Display drain in Plaxman combined phases
        self.ui.pushButton_35.clicked.connect(self.plaxman.calculate)                       # Calculate  (at phases)       
        self.ui.pushButton_61.clicked.connect(self.plaxman.calculate_obs)                   # Calculate (at observed points)      
        self.ui.pushButton_38.clicked.connect(self.plaxman.view_wall_outputs)               # Plot wall outputs
        self.ui.pushButton_54.clicked.connect(self.plaxman3d.plot_wall_outputs)             # Plot wall outputs
        self.ui.pushButton_91.clicked.connect(self.plaxman.open_dim_wall_tool)              # Open dimensioning tool for wall
        self.ui.pushButton_45.clicked.connect(self.plaxman.open_dim_cross_section_tool)     # Open dimensioning tool for cross-section
        self.ui.pushButton_145.clicked.connect(self.plaxman.open_dim_anchor_tool)           # Open dimensioning tool for anchors
        self.ui.pushButton_77.clicked.connect(self.plaxman.open_dim_strut_tool)            # Open dimensioning tool for struts
        self.ui.pushButton_95.clicked.connect(self.plaxman.open_dim_waler_tool)            # Open dimensioning tool for struts
        self.ui.pushButton_151.clicked.connect(self.plaxman.open_dim_wall_inserted_profile_beam_tool)       # Open dimensioning tool for inserted steel profile
        self.ui.pushButton_152.clicked.connect(self.plaxman.open_dim_wall_MIP_profile_beam_tool)            # Open dimensioning tool for inserted steel profile
        self.ui.pushButton_39.clicked.connect(self.plaxman.plot_soilsection_settlement)     # Plot settlement in soil section
        self.ui.pushButton_40.clicked.connect(self.plaxman.add_new_material)                # Add a new material for free polygons/ rectangular soil clusters
        self.ui.pushButton_41.clicked.connect(lambda: self.plaxman.add_polygon_point(self.ui.lineEdit_42.text()))
        self.ui.pushButton_44.clicked.connect(self.plaxman.remove_polygon_point_onclick)
        self.ui.pushButton_42.clicked.connect(self.plaxman.add_polygon)
        self.ui.pushButton_43.clicked.connect(self.plaxman.remove_polygon)
        self.ui.pushButton_46.clicked.connect(self.plaxman.change_polygon_points)
        self.ui.pushButton_59.clicked.connect(self.plaxman.add_observed_points)             # Add observed points for sensitivity and back-analysis
        self.ui.pushButton_60.clicked.connect(self.plaxman.remove_observed_points)          # Remove observed points for sensitivity and back-analysis
        self.ui.pushButton_90.clicked.connect(self.plaxman.load_observed_points)            # Load observed points from file
        self.ui.pushButton_121.clicked.connect(self.plaxman.open_borelogs_analyzer)         # Open borelogs analysis tool
        self.ui.pushButton_140.clicked.connect(self.plaxman.print_report)                   # Print report

        # Stone columns/ rigid inclusions
        self.ui.pushButton_122.clicked.connect(self.plaxman.define_soil_improvement_structure) # Define stone columns/ rigid inclusions
        self.ui.pushButton_131.clicked.connect(self.plaxman.change_soil_improvement_structure_properties) # Change properties of stone columns/ rigid inclusions
        self.ui.pushButton_123.clicked.connect(self.plaxman.remove_soil_improvement_structure) # Remove soil improvement structure
        self.ui.pushButton_126.clicked.connect(self.plaxman.define_soil_improvement_soil_clusters)
        self.ui.pushButton_127.clicked.connect(self.plaxman.remove_soil_improvement_soil_clusters_onclick)

        # Add/ remove a combined phase
        self.ui.pushButton_57.clicked.connect(self.plaxman_cp.add_combined_phase)
        self.ui.pushButton_68.clicked.connect(self.plaxman_cp.remove_combined_phase)

        # Create automated phases
        self.ui.pushButton_101.clicked.connect(self.plaxman_ap.setup_automated_phases)                      # Generate automated phases, phreatic water levels
        self.ui.pushButton_101.clicked.connect(self.plaxman_ap_steadystate.setup_automated_phases)          # Generate automated phases, steady state ground water flow
        self.ui.pushButton_101.clicked.connect(self.plaxman_cp.display_all_model_components)    # Display all model compenents in Plaxman combined phases
        self.ui.pushButton_101.clicked.connect(self.optiman.display_all_model_components)       # Transfer Anchors to Optiman

        self.ui.pushButton_102.clicked.connect(self.plaxman_ap.remove_automated_phases)         # Remove automated phases       
        self.ui.pushButton_102.clicked.connect(self.plaxman_cp.display_all_model_components)    # Display all model compenents in Plaxman combined phases

        # Backman UKF
        self.ui.pushButton_56.clicked.connect(self.backman.open_data_site)              # load site measurement
        self.ui.pushButton_58.clicked.connect(self.backman.remove_data_site)            # Remove the last observation set
        self.ui.pushButton_53.clicked.connect(self.backman.select_soil_parameters)      # Select soil parameters for back-analysis
        self.ui.pushButton_55.clicked.connect(self.backman.remove_soil_parameters)      # Remove soil parameters for back-analysis
        self.ui.pushButton_150.clicked.connect(self.backman.select_wall_parameters)     # Select wall parameters for sensivity analysis
        self.ui.pushButton_149.clicked.connect(self.backman.add_wall_parameters)        # Add wall parameters for sensivity analysis
        self.ui.pushButton_148.clicked.connect(self.backman.remove_wall_parameters)     # Remove wall parameters for sensivity analysis
        self.ui.pushButton_52.clicked.connect(self.backman.go_to_inversion)             # Go to inversion
        self.ui.pushButton_65.clicked.connect(self.backman.start_inversion_ukf)         # Start UKF back-analysis
        self.ui.pushButton_63.clicked.connect(self.backman.stop_inversion_ukf)          # Stop UKF back-analysis
        self.ui.pushButton_64.clicked.connect(self.backman.resume_inversion_ukf)        # Resume UKF back-analysis
        self.ui.pushButton_66.clicked.connect(self.backman.load_available_results_ukf)  # Load UKF back-analysis results
        # Backman PSO
        self.ui.pushButton_85.clicked.connect(self.backman.load_metamodel_pso)          # Load metamodel for PSO back-analysis
        self.ui.pushButton_86.clicked.connect(self.backman.start_inversion_pso)         # Start PSO back-analysis
        self.ui.pushButton_87.clicked.connect(self.backman.resume_inversion_pso)        # Resume PSO back-analysis
        self.ui.pushButton_88.clicked.connect(self.backman.stop_inversion_pso)          # Stop PSO back-analysis
        self.ui.pushButton_89.clicked.connect(self.backman.inspect_misfit_pso)          # Inspect misfit after PSO back-analysis
        
        # Sensiman
        self.ui.pushButton_79.clicked.connect(self.sensiman.select_soil_parameters)            # Select soil parameters for sensivity analysis
        self.ui.pushButton_78.clicked.connect(self.sensiman.remove_soil_parameters)            # Remove soil parameters for sensivity analysis
        self.ui.pushButton_80.clicked.connect(self.sensiman.go_to_metamodeling)                # Go to metamodeling
        self.ui.pushButton_124.clicked.connect(self.sensiman.select_wall_parameters)           # Select wall parameters for sensivity analysis
        self.ui.pushButton_133.clicked.connect(self.sensiman.add_wall_parameters)              # Add wall parameters for sensivity analysis
        self.ui.pushButton_125.clicked.connect(self.sensiman.remove_wall_parameters)           # Remove wall parameters for sensivity analysis
        self.ui.pushButton_134.clicked.connect(self.sensiman.select_strut_parameters)          # Select strut parameters for sensivity analysis
        self.ui.pushButton_139.clicked.connect(self.sensiman.add_strut_parameters)             # Add strut parameters for sensivity analysis
        self.ui.pushButton_135.clicked.connect(self.sensiman.remove_strut_parameters)          # Remove strut parameters for sensivity analysis
        # Sensiman/Metamodeling
        self.ui.pushButton_70.clicked.connect(self.sensiman.generate_database_input)           # Generate random inputs
        self.ui.pushButton_74.clicked.connect(self.sensiman.load_existing_database_input)      # Load existing input data file
        self.ui.pushButton_71.clicked.connect(self.sensiman.start_generate_database_output)    # Start generating random outputs
        self.ui.pushButton_73.clicked.connect(self.sensiman.stop_generate_database_output)     # Stop generating random outputs
        self.ui.pushButton_72.clicked.connect(self.sensiman.resume_generate_database_output)   # Stop generating random outputs
        self.ui.pushButton_62.clicked.connect(self.sensiman.load_samples_metamodel)            # Load random samples for metamodel training/ validation
        self.ui.pushButton_141.clicked.connect(self.sensiman.select_observation_phases_metamodel) # Load random samples for metamodel training/ validation
        self.ui.pushButton_75.clicked.connect(self.sensiman.remove_samples_metamodel)          # Remove random samples for metamodel training/ validation
        self.ui.pushButton_76.clicked.connect(self.sensiman.train_metamodel)                   # Train the metamodel
        self.ui.pushButton_142.clicked.connect(self.sensiman.view_prediction_metamodel)        # View metamodel for prediction
        self.ui.pushButton_143.clicked.connect(self.sensiman.remove_metamodel)                 # Remove a selected metamodel
        # Sensiman/Local sensitivity analysis
        self.ui.pushButton_81.clicked.connect(self.sensiman.go_to_local_sensitivity)           # Go to local sensitivity
        self.ui.pushButton_83.clicked.connect(self.sensiman.start_local_sensitivity)           # Start database generation for local sensitivity analysis
        self.ui.pushButton_84.clicked.connect(self.sensiman.stop_local_sensitivity)            # Stop database generation for local sensitivity analysis
        self.ui.pushButton_82.clicked.connect(self.sensiman.resume_local_sensitivity)          # Resume database generation for local sensitivity analysis

        # Optiman
        self.ui.pushButton_92.clicked.connect(self.optiman.select_wall_variables)               # Select wall variables for desian optimization
        self.ui.pushButton_94.clicked.connect(self.optiman.add_wall_variables)                  # Add wall variables for design optimization
        self.ui.pushButton_93.clicked.connect(self.optiman.select_anchor_variables)             # Select anchor variables for design optimization
        self.ui.pushButton_98.clicked.connect(self.optiman.add_anchor_variables)                # Add anchor variables for design optimization
        self.ui.pushButton_99.clicked.connect(self.optiman.remove_anchor_variables)             # Remove anchor variables for design optimization
        self.ui.pushButton_97.clicked.connect(self.optiman.select_strut_variables)              # Select strut variables for design optimization
        self.ui.pushButton_69.clicked.connect(self.optiman.add_strut_variables)                 # Add strut variables for design optimization
        self.ui.pushButton_103.clicked.connect(self.optiman.remove_strut_variables)             # Remove strut variables for design optimization
        self.ui.pushButton_107.clicked.connect(self.optiman.go_to_nsga2)                        # Go to Optiman/NSGAII
        self.ui.pushButton_108.clicked.connect(self.optiman.go_to_sensitivity)                  # Go to Optiman/Sensitivity
        self.ui.pushButton_117.clicked.connect(self.optiman.go_to_metamodeling)                 # Go to Optiman/Metamodeling
        self.ui.pushButton_109.clicked.connect(self.optiman.start_local_sensitivity)            # Start Optiman/Sensitivity
        self.ui.pushButton_111.clicked.connect(self.optiman.stop_local_sensitivity)             # Stop Optiman/Sensitivity
        self.ui.pushButton_110.clicked.connect(self.optiman.resume_local_sensitivity)           # Resume Optiman/Sensitivity
        self.ui.pushButton_132.clicked.connect(self.optiman.load_initial_population)            # Load initial population for NSGAII/III
        self.ui.pushButton_130.clicked.connect(self.optiman.start_nsga2)                        # Test (Run) design optimization
        self.ui.pushButton_129.clicked.connect(self.optiman.stop_nsga2)                         # Stop design optimization (Stop running NSGAII)
        self.ui.pushButton_128.clicked.connect(self.optiman.resume_nsga2)                       # Resume design optimization (Stop running NSGAII)
        self.ui.pushButton_105.clicked.connect(self.optiman.generate_database_input)            # Generate random samples for Optiman/Metamodeling
        self.ui.pushButton_119.clicked.connect(self.optiman.load_existing_database_input)       # Load random samples for Optiman/Metamodeling
        self.ui.pushButton_104.clicked.connect(self.optiman.start_check_legal_samples)          # Check for legal samples in Optiman/Metamodeling
        self.ui.pushButton_118.clicked.connect(self.optiman.stop_check_legal_samples)           # Stop checking for legal samples in Optiman/Metamodeling
        self.ui.pushButton_112.clicked.connect(self.optiman.start_generate_database_output)     # Evaluate random samples for Optiman/Metamodeling
        self.ui.pushButton_113.clicked.connect(self.optiman.stop_generate_database_output)      # Stop/Pause evaluating random samples for Optiman/Metamodeling
        self.ui.pushButton_106.clicked.connect(self.optiman.resume_generate_database_output)    # Stop/Pause evaluating random samples for Optiman/Metamodeling
        self.ui.pushButton_120.clicked.connect(self.optiman.view_pareto_front)                  # Stop/Pause evaluating random samples for Optiman/Metamodeling

        self.ui.pushButton_138.clicked.connect(self.optiman.select_soil_improvement_variables)  # Select stone columns/ rigid inclusions variables for design optimization
        self.ui.pushButton_136.clicked.connect(self.optiman.add_soil_improvement_variables)     # Add stone columns/ rigid inclusions variables for design optimization
        self.ui.pushButton_137.clicked.connect(self.optiman.remove_soil_improvement_variables)  # Remove stone columns/ rigid inclusions variables for design optimization
        # Show the Moniman's main window and capture exit if security check is passed
        self.check_security()
        MainWindow.showMaximized()
        MainWindow.show()
        sys.exit(app.exec_()) 
    

    def go_to_soil(self):
        """ Goes to soil tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(0)


    def go_to_wall(self):
        """ Goes to wall tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(0)


    def go_to_anchors(self):
        """ Goes to ground anchors tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(1)


    def go_to_struts(self):
        """ Goes to struts tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(2)


    def go_to_lineloads(self):
        """ Goes to lineloads tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(3)

    def go_to_pointloads(self):
        """ Goes to pointloads tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(4)


    def go_to_soilpolygons(self):
        """ Goes to pointloads tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(5)


    def go_to_mesh(self):
        """ Goes to pointloads tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(1)
        self.ui.tabWidget_5.setCurrentIndex(6)

    def go_to_soilclusters(self):
        """ Goes to soilclusters tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(2)
        self.ui.tabWidget_6.setCurrentIndex(0)

    def go_to_automated_phases(self):
        """ Goes to automated phases tab
        """
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget_2.setCurrentIndex(2)
        self.ui.tabWidget_6.setCurrentIndex(5)
        self.ui.tabWidget_10.setCurrentIndex(0)


    def go_to_sensitivity(self):
        """ Goes to Sensiman > Settings  tab
        """
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tabWidget_3.setCurrentIndex(0)


    def go_to_backanalysis(self):
        """ Goes to Sensiman > Settings  tab
        """
        self.ui.tabWidget.setCurrentIndex(2)
        self.ui.tabWidget_4.setCurrentIndex(0)


    def go_to_optimization(self):
        """ Goes to Sensiman > Settings  tab
        """
        self.ui.tabWidget.setCurrentIndex(3)
        self.ui.tabWidget_7.setCurrentIndex(0)
        self.ui.tabWidget_8.setCurrentIndex(0)


    def check_security(self):
        """ Checks UUID code
        """
        uuid = get_uuid()        
        today = datetime.now()
        expired_date = datetime.strptime('2019-06-30',"%Y-%m-%d")   # expiration date for temporary user
        local_ip = self.get_ip_address()
        if local_ip in self.bauer_ip:   # always allowed if user is in bauer network
            pass
        elif (uuid not in self.uuids.values()) and (not ((uuid in self.uuids_temporary) and (today > expired_date))): 
            self.dialog.show_message_box('Warning', 'Your computer is not authorized to run this program!')
            sys.exit()


    def get_ip_address(self):
        """ Gets user IP address
        """
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip


    def save(self):
        """ Saves MONIMAN state
        """
        try:
            filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_state.mon')

            if os.path.isfile(filename): # checks if plaxman's state file exists 
                answer = self.dialog.show_save_box(os.path.basename(filename))
                if answer == QMessageBox.Yes:
                    self.plaxman.save()
                    self.plaxman_ap.save()
                    self.backman.save()
                    self.sensiman.save()
                    self.optiman.save()
            else:
                self.plaxman.save()
                self.plaxman_ap.save()
                self.backman.save()
                self.sensiman.save()
                self.optiman.save()

        except KeyError:
            self.dialog.show_message_box('Warning', 'There is nothing to save!')


    def save_as(self):
        """ Saves MONIMAN
        """
        try:
            _ = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_state.mon') # for handling exception when there is nothing to save

            paths_dict = loadpy(r'common\\PATHS.py') # by default, save in last opened project
            project_dir = QFileDialog.getExistingDirectory(QFileDialog(), 'Select project folder', paths_dict['MONIMAN_OUTPUTS'])
            source = paths_dict['MONIMAN_OUTPUTS']

            if (project_dir != source) and (project_dir !=''):
                # set project_dir to 'MONIMAN_OUTPUTS' in 'PATHS.py'
                self.update_project_dir(project_dir)

                # copy necessary directories
                dest = project_dir
                if os.path.exists(os.path.join(source, 'materials')):
                    if os.path.exists(os.path.join(dest, 'materials')):
                        shutil.rmtree(os.path.join(dest, 'materials'))
                    shutil.copytree(os.path.join(source, 'materials'), os.path.join(dest, 'materials'))
                if os.path.exists(os.path.join(source, 'measurement')):
                    if os.path.exists(os.path.join(dest, 'measurement')):
                        shutil.rmtree(os.path.join(dest, 'measurement'))
                    shutil.copytree(os.path.join(source, 'measurement'), os.path.join(dest, 'measurement'))
                if os.path.exists(os.path.join(source, 'backman')):
                    if os.path.exists(os.path.join(dest, 'backman')):
                        shutil.rmtree(os.path.join(dest, 'backman'))
                    shutil.copytree(os.path.join(source, 'backman'), os.path.join(dest, 'backman'))
                if os.path.exists(os.path.join(source, 'sensiman')):
                    if os.path.exists(os.path.join(dest, 'sensiman')):
                        shutil.rmtree(os.path.join(dest, 'sensiman'))
                    shutil.copytree(os.path.join(source, 'sensiman'), os.path.join(dest, 'sensiman'))
                if os.path.exists(os.path.join(source, 'optiman')):
                    if os.path.exists(os.path.join(dest, 'optiman')):
                        shutil.rmtree(os.path.join(dest, 'optiman'))
                    shutil.copytree(os.path.join(source, 'optiman'), os.path.join(dest, 'optiman'))

                # copy retaining_wall.py
                if os.path.exists(os.path.join(source, 'retaining_wall.py')):
                    if os.path.exists(os.path.join(dest, 'retaining_wall.py')):
                        os.remove(os.path.join(dest, 'retaining_wall.py'))
                    shutil.copyfile(os.path.join(source, 'retaining_wall.py'), os.path.join(dest, 'retaining_wall.py'))
                # reset MONIMAN_OUTPUTS in retaining_wall.py
                self.plaxman.set_paths_and_file()
                plaxis2d_input.rewrite_imports(self.plaxman.plaxis2d_input_file, sys.modules['moniman_paths'])

                self.plaxman.save()
                self.plaxman_ap.save()
                self.backman.save()
                self.sensiman.save()
                self.optiman.save()

                # reloading for updating material paths
                self.reload_moniman()

        except KeyError:
            self.dialog.show_message_box('Warning', 'There is nothing to save!')


    def load(self):
        """ Loads (Opens) MONIMAN
        """
        paths_dict = loadpy(r'common\\PATHS.py') # by default, load from last opened project
        project_dir = QFileDialog.getExistingDirectory(QFileDialog(), 'Select project folder', paths_dict['MONIMAN_OUTPUTS'])

        if project_dir:
            # set project_dir to 'MONIMAN_OUTPUTS' in 'PATHS.py'
            self.update_project_dir(project_dir)
            self.reload_moniman()


    def reload_moniman(self):
        """ Reloads MONIMAN after project dir is defined
        """
        # load MONIMAN
        self.plaxman.load()
        self.plaxman_cp.load()
        self.plaxman_ap.load()

        self.backman.load()
        self.sensiman.load()
        self.optiman.load()

        self.isLoaded = True    # True if MONIMAN has been loaded
        
    
    def new(self):
        """ Creates a new project
        """
        paths_dict = loadpy(r'common\\PATHS.py') # by default, load from last opened project
        project_dir = QFileDialog.getExistingDirectory(QFileDialog(), 'Select project folder', paths_dict['MONIMAN_OUTPUTS'])

        if project_dir:
            plaxman_file = os.path.join(project_dir, 'plaxman_state.mon')
            if os.path.isfile(plaxman_file): # checks if plaxman's state file exists 
                answer = self.dialog.show_new_project_box(os.path.basename(plaxman_file))
                if answer == QMessageBox.Yes:
                    # set project_dir to 'MONIMAN_OUTPUTS' in 'PATHS.py'
                    self.update_project_dir(project_dir)
                    self.plaxman.set_paths_and_file()
                    self.plaxman.assign_default_geometry()
            else:
                # set project_dir to 'MONIMAN_OUTPUTS' in 'PATHS.py'
                self.update_project_dir(project_dir)
                self.plaxman.set_paths_and_file()
                self.plaxman.assign_default_geometry()


    def update_project_dir(self, project_dir):
        """ Updates project_dir
        """
        paths_dict = loadpy(r'common\\PATHS.py')
        # update MONIMAN path
        cwd = os.getcwd()
        paths_dict['MONIMAN'] = cwd
        # update MONIMAN_OUTPUTS path
        paths_dict['MONIMAN_OUTPUTS'] = project_dir
        paths_dict['MEASUREMENT'] = os.path.join(project_dir, 'measurement')
        with open(r'common\\PATHS.py', 'w') as f:
            for key, value in paths_dict.items():
                text = key + ' = ' + 'r' + "'" + value.replace("/", "\\") + "'" + '\n\n'
                f.write(text)


    def open_PDF_tutorial1(self):
        """ Opens PDF tutorial 1
        """
        try:
            cwd = os.getcwd()
            filename = os.path.join(cwd, 'docs\\tutorials\\RetainingWall_Anchors.pdf')

            cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
            cmd.append(filename)
            subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)

        except:
            self.dialog.show_message_box('Warning', 'Cannot open file! Please manually open the folder you installed MONIMAN and then go to docs\\tutorials.')
                    

    def open_PDF_tutorial2(self):
        """ Opens PDF tutorial 2
        """
        try:
            cwd = os.getcwd()
            filename = os.path.join(cwd, 'docs\\tutorials\\RetainingWall_Struts.pdf')

            cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
            cmd.append(filename)
            subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)

        except:
            self.dialog.show_message_box('Warning', 'Cannot open file! Please manually open the folder you installed MONIMAN and then go to docs\\tutorials.')


    def open_PDF_tutorial3(self):
        """ Opens PDF tutorial 3
        """
        try:
            cwd = os.getcwd()
            filename = os.path.join(cwd, 'docs\\tutorials\\RetainingWall_Berms_Struts_Reconstruction.pdf')

            cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
            cmd.append(filename)
            subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)

        except:
            self.dialog.show_message_box('Warning', 'Cannot open file! Please manually open the folder you installed MONIMAN and then go to docs\\tutorials.')


if __name__ == "__main__":
    try:
        Moniman_EXEC()

    except Exception as e:
        write_traceback_to_file(os.getcwd(), e)
        #Moniman_EXEC.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(os.getcwd())))
    