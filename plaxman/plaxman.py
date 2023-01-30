# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 2018

@author: nya
"""
import os
import sys
import subprocess
import shutil
from os.path import join, exists, isfile
import math
import numpy as np
from random import randint
import json
import time
from collections import OrderedDict, namedtuple
from common.boilerplate import start_plaxis
from tools.file_tools import remove, write_traceback_to_file
from tools.math import hex_to_rgb, rgb_to_integer
from solver.plaxis2d.parameter_relations import (get_HS_K0nc, get_interp_function_Edyn_over_Esta_Esta,
                                                 get_interp_Edyn_over_Esta, get_HSsmall_G0ref)
from plxscripting.easy import new_server
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QStandardItem
from gui.gui_all_dialogs_ui import Ui_Dialog
from gui.gui_all_forms_ui import Ui_Form
from system.system import load_paths
from tools.file_tools import saveobjs, loadobjs, saveobjs_pathpatches_ignored
from tools.json_functions import read_data_in_json_item, set_material_color
import solver.plaxis2d.input_scripting_commands as plaxis2d_input
from plaxman.plaxman_load import loadPlaxman
from workflow1.evaluate_plaxis2d_model import Evaluate_Plaxis2DModel
from system.run_thread import RunThreadSingle
from matplotlib.backends.backend_pdf import PdfPages
from report.report_plaxman import Report as ReportPlaxman

# wall/ anchor/ strut dimensioning
from dimensioning.dim_cross_section import Dim_cross_section
from dimensioning.dim_wall import Dim_wall
from dimensioning.dim_anchor import Dim_anchor
from dimensioning.dim_strut import Dim_strut
from dimensioning.dim_waler import Dim_waler
from dimensioning.dim_wall_inserted_steel_profile import Dim_wall_inserted_steel_profile
from dimensioning.dim_MIP_steel_profile import Dim_MIP_steel_profile

# 3D borelog analyzer
from plaxman.borelogs.borelogs_analyzer import Borelogs_Analyzer
# stone columns
from plaxman.plaxman_stone_columns import StoneColumns, StoneColumnsSoilClusters
from optiman.structure_costs import StructureCostFactory
# rigid inclusions
from plaxman.plaxman_rigid_inclusions import FDC, FDC_SoilClusters
# extended plaxman
from plaxman.plaxman_extended import Plaxman_Extended
from plaxman.plaxman_walls import Plaxman_WALLS
from system.system import load_paths

# load PATHS.py
load_paths(r'common\\PATHS.py')
ACROBAT = sys.modules['moniman_paths']['ACROBAT']


class Plaxman():
    __shared_state = {'project_properties': {}, 'geometry': None, 'mesh': {}, 'Boreholes': [], 'Layer_polygons': [], 'material_json_item': '',
                      'strand_json_item': '', 'grout_json_item': '', 'strut_json_item': '', 'wall_json_item': '', 'Soilmaterials': [], 'Wallmaterials': [], 'Walls': [], 'Anchors': [],
                      'Struts': [], 'Lineloads': [], 'Pointloads': [], 'polygonPoints': [], 'Polygons': [], 'Soilclusters': [], 'Soilclusters_notdried': [], 'Waterlevels': [], 'Drains': [],
                      'Drain': {}, 'Phases': [], 'new_phase': {}, 'Points_obs': [], 'sc_params': {}, 'sc_name': '', 'sub_soillayers': [], 'sc_p0': None, 'sc_thickness_sublayer':2.0,
                      'sc_points_fine_mesh': [], 'SCs': [], 'FDCs': [], 'dim_params': {}, 'dim_params_cross_section': {}, 'dim_params_strut': {}, 'dim_params_waler': {},
                      'dim_params_inserted_steel_profile': {}, 'dim_params_MIP_steel_profile': {}}
#        self.project_properties = {}
#        self.geometry = None
#        self.mesh = {}              # mesh properties
#        self.Boreholes = []         # list of dictionaries for x, Head, Top, and Bottom of each borehole
#        self.Layer_polygons = []    # list of lists polygon (Path object) for each of the soil layers
#        self.material_json_item = ''# json item name of the edited material
#        self.Soilmaterials = []     # Soil materials for assiging to soil clusters
#        self.strand_json_item = ''
#        self.grout_json_item = ''
#        self.strut_json_item = ''
#        self.wall_json_item = ''
#        self.Wallmaterials = []     # Wall materials with additional information such as wall color
#        self.Walls = []             # list of dictionaries for wall properties
#        self.Anchors = []
#        self.Struts = []
#        self.Lineloads = []
#        self.Pointloads = []
#        self.polygonPoints = []     # list of points for free polygons
#        self.Polygons = []          # List of free polygons
#        self.Soilclusters = []      # List of soil clusters for excavation
#        self.Soilclusters_notdried = [] # soilclusters not yet excavated
#        self.Waterlevels = []
#        self.Drains = []           # drains for Automated phases with Steady state groundwater flow
#        self.Drain = {}
#        self.Phases = []
#        self.new_phase = {}
#        self.Points_obs = []        # list of points for measured points
#        self.sc_params = {}         # parameters of stone columns structure
#        self.sc_name = ''           # name of stone columns structure
#        self.sub_soillayers = []    # sub soilayers improved by stone columns
#        self.sc_p0 = None           # surcharge
#        self.sc_thickness_sublayer = None          # thickness of sublayer
#        self.SCs = []                              # list of stone columns soil improvement structures
#        self.FDCs = []                             # list of FDC soil improvement structures
#        self.dim_params = {}                       # parameters for dimensions of wall
#        self.dim_params_cross_section = {}         # parameters for dimensions of cross-section
#        self.dim_params_strut = {}                 # parameters for dimensions of strut


    def __init__(self, ui=None, plot_canvas=None):
        """ Initialize Plaxman attributes
        """
        self.__dict__ = self.__shared_state     # initialize monostate attributes

        # main gui and dialogs
        self.ui = ui
        self.dialog = Ui_Dialog()
        self.form = Ui_Form()

        # matplotlib canvas and toolbar
        self.plot_canvas = plot_canvas

        # Plaxis scripting input file
        self.plaxis2d_input_file = None

        # connect signals
        #self.connect_signals_to_slots()

        # extended Plaxman
        self.plaxman_x = Plaxman_Extended(ui, self.plaxis2d_input_file, plot_canvas=plot_canvas)

        # Plaxman for WALLS
        self.walls_input_file = None    # Input file for WALLS
        #self.plaxman_walls = Plaxman_WALLS(self.walls_input_file)


    def assign_default_geometry(self):
        """ Load default placeholder values for geometric boundaries and wall position
        """
        self.ui.lineEdit.setText(self.ui.lineEdit.placeholderText())
        self.ui.lineEdit_2.setText(self.ui.lineEdit_2.placeholderText())
        self.ui.lineEdit_3.setText(self.ui.lineEdit_3.placeholderText())
        self.ui.lineEdit_4.setText(self.ui.lineEdit_4.placeholderText())
        self.ui.lineEdit_5.setText(self.ui.lineEdit_5.placeholderText())
        self.ui.lineEdit_6.setText(self.ui.lineEdit_6.placeholderText())

        # for wall
        y_min = float(self.ui.lineEdit_2.text())
        y_max = float(self.ui.lineEdit_4.text())
        wall_length = abs(y_min - y_max)/2
        self.ui.lineEdit_7.setText(str(0) + ', ' + str(y_max))
        self.ui.lineEdit_9.setText(str(0) + ', ' + str(y_max - wall_length))


    def set_paths_and_file(self):
        """ Set MONIMAN paths and file to write out python script of the PLAXIS model
        """

        # load PATHS.py
        load_paths(r'common\\PATHS.py')

        ## alter paths for PLAXIS2d Connect edition
        #sys.modules['moniman_paths']['PLAXIS2D'] = r'C:\Program Files\Bentley\Geotechnical\PLAXIS 2D CONNECT Edition V20'
        #sys.modules['moniman_paths']['PLAXIS2D_SCRIPTING'] = r'C:\Program Files\Bentley\Geotechnical\PLAXIS Python Distribution\01.00\python\Lib\site-packages'

        # create OUTPUT directory if it does not exist
        if not exists(sys.modules['moniman_paths']['MONIMAN_OUTPUTS']):
            os.makedirs(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])

        # define plaxis2d python file to write out
        self.plaxis2d_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.py')

        # define WALLS input file to write out
        self.walls_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.walls')

        # assign plaxis2d_input_file as a property of Plaxman_Extended
        self.plaxman_x.plaxis2d_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.py')

        # remove all user redefined material json files
        #reg_exp = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials\*__.json')
        #remove_file_reg_expr(reg_exp)


    def update_geometry(self):
        """ Set geometry as defined in the user interface
        """
        if 'moniman_paths' not in sys.modules:
            self.dialog.show_message_box('Warning', 'Please set your paths before starting!')

        elif len(self.Boreholes) > 0:
            self.dialog.show_message_box('Warning', 'Please remove all created components to start over!')

        else:
            try:
                project_title = self.ui.lineEdit_13.text()
                model_type = self.ui.comboBox.currentText()
                element_type = self.ui.comboBox_2.currentText()
                x_min = float(self.ui.lineEdit.text())
                y_min = float(self.ui.lineEdit_2.text())
                x_max = float(self.ui.lineEdit_3.text())
                y_max = float(self.ui.lineEdit_4.text())

                if (model_type == 'Axisymmetry') and (x_min != 0.0):
                    self.dialog.show_message_box('Warning', 'Please set x_min to zero for axisymmetric model!')

                else:
                    self.geometry = [x_min, y_min, x_max, y_max]
                    self.plot_canvas.plot_geometry(self.geometry)

                    if element_type == '6 nodes':
                        element_type = '6noded'
                    else:
                        element_type = '15noded'

                    self.project_properties['project_title'] = project_title
                    self.project_properties['model_type'] = model_type
                    self.project_properties['element_type'] = element_type

                    plaxis2d_input.set_project_properties(self.plaxis2d_input_file, 'g_i', self.project_properties, sys.modules['moniman_paths'])
                    plaxis2d_input.set_geometry(self.plaxis2d_input_file, 'g_i', self.geometry)

                    # Set background color for x_min and x_max, indicating that they are responsive
                    self.ui.lineEdit.setStyleSheet("background-color: rgb(242, 255, 116);")
                    self.ui.lineEdit_3.setStyleSheet("background-color: rgb(242, 255, 116);")
                    self.ui.lineEdit.returnPressed.connect(lambda: self.update_geometry_xmin_xmax(float(self.ui.lineEdit.text()), float(self.ui.lineEdit_3.text())))
                    self.ui.lineEdit_3.returnPressed.connect(lambda: self.update_geometry_xmin_xmax(float(self.ui.lineEdit.text()), float(self.ui.lineEdit_3.text())))


                    # Set start-dependent user components
                    self.disable_push_buttons()
                    #self.ui.lineEdit_13.setEnabled(False)
                    self.ui.pushButton.setEnabled(True)
                    self.ui.pushButton_11.setEnabled(True)

                    print('Started, geometry is created')

                    #connect signals
                    self.connect_signals_to_slots()

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if values for model boundaries are correctly entered!')


    def connect_signals_to_slots(self):
        """ Connects signals to slots
        """
        self.ui.lineEdit_13.setStyleSheet("background-color: rgb(242, 255, 116);")
        self.ui.lineEdit_13.returnPressed.connect(lambda: self.update_project_title())


    @pyqtSlot()
    def update_project_title(self):
        """ Updates project title
        """
        project_title = self.ui.lineEdit_13.text()
        self.project_properties['project_title'] = project_title
        plaxis2d_input.set_project_title(self.plaxis2d_input_file, project_title)
        print('Project title is set as {}'.format(project_title))



    @pyqtSlot()
    def update_geometry_xmin_xmax(self, x_min, x_max):
        """ Updates x_min and x_max of the model
        """
        try:
            self.geometry[0] = x_min
            self.geometry[2] = x_max
            # update geometry in model
            plaxis2d_input.update_geometry(self.plaxis2d_input_file, 'g_i', self.geometry)

            # replot layers if any
            # remove and replot layers
            for i, layer_polygon in enumerate(self.Layer_polygons):
                self.plot_canvas.undo_plot_pathpatches((layer_polygon['pathpatch_top'], layer_polygon['pathpatch_bottom'], layer_polygon['pathpatches']))
                layer_polygon['path_polygon'], layer_polygon['pathpatch_top'], layer_polygon['pathpatch_bottom'], layer_polygon['pathpatches'] = self.plot_canvas.plot_layer(self.Boreholes, i, x_min, x_max)

                if layer_polygon['shaded'] == True: # if soil material has been assigned to layer
                    self.plot_canvas.undo_plot_pathpatches(layer_polygon['pathpatch_layer'])
                    layer_polygon['pathpatch_layer'] = self.plot_canvas.plot_assigned_layer(layer_polygon['path_polygon'], layer_polygon['color'])

            # update plot of borehole
            for borehole in self.Boreholes:
                self.plot_canvas.undo_plot_pathpatches(borehole['pathpatches'])
                borehole['pathpatches'] = self.plot_canvas.plot_borehole(len(self.Boreholes), borehole, self.geometry)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values for model boundaries are correctly entered!')


    def disable_push_buttons(self):
        """ Disable GUI push buttons for dependent soil creation steps
            Geometry -> Borehole -> Soil layer -> Define/ assign material to soil layer
        """
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_11.setEnabled(False)
        self.ui.pushButton_12.setEnabled(False)
        self.ui.pushButton_13.setEnabled(False)


    def add_borehole(self):
        """ Adds a new borehole
        """
        self.ui.pushButton_4.setEnabled(True)
        self.ui.pushButton_12.setEnabled(True)
        self.ui.tableWidget.blockSignals(True) # temporarily block signals
        name = self.ui.lineEdit_86.text()   # borehole name
        if len(self.Layer_polygons) > 0:
            self.dialog.show_message_box('Warning', 'Please remove all soil layers first!')
        elif name == '':
            self.dialog.show_message_box('Warning', 'Please give borehole a name!')
        else:
            # Add a borehole
            if len(self.Boreholes) < 10:
                try:
                    x = float(self.ui.lineEdit_5.text())
                    Head = float(self.ui.lineEdit_6.text())
                    
                    # Check against co-located boreholes
                    x_coords = [borehole['x'] for borehole in self.Boreholes]
                    if x not in x_coords:
                        y_min = self.geometry[1]
                        y_max = self.geometry[3]
                        
                        # Add the new borehole item for later soil layer creation
                        new_borehole = {'x': x, 'Head': Head}
                        new_borehole['name'] = name
                        new_borehole['id'] = randint(100000, 999999)
                        new_borehole['Top'] = []
                        new_borehole['Bottom'] = []
                        self.Boreholes.append(new_borehole)

                        item = self.ui.tableWidget.verticalHeaderItem(0)
                        item.setText(QCoreApplication.translate("MainWindow", "(Layer 1)"))
                        item_number = 2*(len(self.Boreholes) - 1)
                        item = self.ui.tableWidget.horizontalHeaderItem(item_number)
                        item.setText(QCoreApplication.translate("MainWindow", name + " - Top"))
                        item = self.ui.tableWidget.horizontalHeaderItem(item_number + 1)
                        item.setText(QCoreApplication.translate("MainWindow", name + " - Bottom"))
                        
                        # Suggest initial top and botom levels at boreholes for the first soil layer
                        self.ui.tableWidget.setItem(0, 2*(len(self.Boreholes) - 1) + 1, QtWidgets.QTableWidgetItem(str(y_min)))
                        self.ui.tableWidget.setItem(0, 2*(len(self.Boreholes) - 1), QtWidgets.QTableWidgetItem(str(y_max)))

                        new_borehole['pathpatches'] = self.plot_canvas.plot_borehole(len(self.Boreholes), new_borehole, self.geometry)
                        
                        plaxis2d_input.add_borehole(self.plaxis2d_input_file, 'g_i', len(self.Boreholes), new_borehole)

                        self.ui.comboBox_33.addItem(name)
                        
                        print('New borehole is added at x = {}'.format(new_borehole['x']))
                    
                    else:
                        self.dialog.show_message_box('Warning', 'Borehole position is repeated, please modify!')
                
                except ValueError:
                    self.dialog.show_message_box('Warning', 'Please check if values for x and Head are correctly entered!')
                
            else: 
                self.dialog.show_message_box('Warning', 'Only up to 10 boreholes are allowed at the moment!')

        self.ui.tableWidget.blockSignals(False)



    def edit_borehole(self):
        """ Edits location x and globlal ground water level Head of a selected borehole
        """
        if len(self.Boreholes) > 0:
            name_bh = self.ui.comboBox_33.currentText()
            #bh_number = int(selected_bh[2:]) - 1    # get borehole number
            #print(text)
            # which borehole
            bh_number = 0
            borehole_selected = None
            for bh_number, borehole in enumerate(self.Boreholes):
                if name_bh == borehole['name']:
                    borehole_selected = borehole

            if borehole_selected is not None:
                text = self.dialog.open_borehole_editor(borehole_selected['name'], borehole_selected['x'], borehole_selected['Head'])

                if text is not None:
                    try:
                        # update x, Head of borehole
                        name_bh = text.split(',')[0]
                        x = float(text.split(',')[1])
                        Head = float(text.split(',')[2])
                        self.Boreholes[bh_number]['name'] = name_bh
                        self.Boreholes[bh_number]['x'] = x
                        self.Boreholes[bh_number]['Head'] = Head

                        # update plaxis2d input file
                        plaxis2d_input.update_borehole(self.plaxis2d_input_file, 'g_i', self.Boreholes[bh_number], bh_number + 1)

                        # update plot of borehole
                        self.plot_canvas.undo_plot_pathpatches(self.Boreholes[bh_number]['pathpatches'])
                        self.Boreholes[bh_number]['pathpatches'] = self.plot_canvas.plot_borehole(len(self.Boreholes), self.Boreholes[bh_number], self.geometry)

                        # update combobox
                        self.ui.comboBox_33.clear()
                        for borehole in self.Boreholes:
                            self.ui.comboBox_33.addItem(borehole['name'])

                    except ValueError:
                        self.dialog.show_message_box('Warning', "Please enter borehole information following the format 'BH_name, x_value, Head_value'!")


    def remove_borehole(self):
        """ Removes the last borehole
        """
        # remove the last borehole
        if len(self.Layer_polygons) > 0:
            self.dialog.show_message_box('Warning', 'Please remove all soil layers first!')
        else:
            if len(self.Boreholes) > 0:
                
                deleted_borehole = self.Boreholes.pop()
                self.plot_canvas.undo_plot_pathpatches(deleted_borehole['pathpatches'])
                        
                item_number = 2*len(self.Boreholes)
                item = self.ui.tableWidget.horizontalHeaderItem(item_number)
                item.setText(QCoreApplication.translate("MainWindow", ""))
                item = self.ui.tableWidget.horizontalHeaderItem(item_number + 1)
                item.setText(QCoreApplication.translate("MainWindow", ""))
                    
                self.ui.tableWidget.setItem(0, 2*len(self.Boreholes), QtWidgets.QTableWidgetItem(''))
                self.ui.tableWidget.setItem(0, 2*len(self.Boreholes) + 1 , QtWidgets.QTableWidgetItem(''))
                
                plaxis2d_input.remove_structure(self.plaxis2d_input_file, deleted_borehole['id'], '##BOREHOLE', 4)
                
                self.ui.comboBox_33.removeItem(self.ui.comboBox_33.count() - 1)

                print('The last borehole is removed, {} boreholes remain'.format(len(self.Boreholes)))


    def remove_structure(self, Structures, dialog_title, signature, num_lines):
        """ General method for removing structures by matching IDs
        """
        if len(Structures) > 0:
            # Let user decide which ground anchor(s) to remove
            self.dialog.open_remove_structure_selection(Structures, dialog_title)
            removed_structures_id = self.dialog.removed_ids
            #print(removed_anchor_id)
            
            for structure_id in removed_structures_id:
                deleted_item = [item for item in Structures if item['id'] == structure_id][0]
                deleted_item_idx = Structures.index(deleted_item)
                #print(deleted_item_idx)
                
                deleted_item = Structures.pop(deleted_item_idx)
                self.plot_canvas.undo_plot_pathpatches(deleted_item['pathpatches'])  
                
                plaxis2d_input.remove_structure(self.plaxis2d_input_file, deleted_item['id'], signature, num_lines)
                
            
            print('Structure removal done, {} items remain'.format(len(Structures)))
            
            return removed_structures_id


    def remove_structure_string_id(self, Structures, dialog_title, signature, num_lines):
        """ General method for removing structures by matching IDs
        """
        if len(Structures) > 0:
            # Let user decide which ground anchor(s) to remove
            self.dialog.open_remove_structure_selection(Structures, dialog_title)
            removed_structures_id = self.dialog.removed_ids
            #print(removed_anchor_id)
            
            for structure_id in removed_structures_id:
                deleted_item = [item for item in Structures if item['id'] == structure_id][0]
                deleted_item_idx = Structures.index(deleted_item)
                #print(deleted_item_idx)
                
                deleted_item = Structures.pop(deleted_item_idx)
                self.plot_canvas.undo_plot_pathpatches(deleted_item['pathpatches'])  
                
                plaxis2d_input.remove_structure_string_id(self.plaxis2d_input_file, str(deleted_item['id']), signature, num_lines)
                
            
            print('Structure removal done, {} items remain'.format(len(Structures)))
            
            return removed_structures_id
    

    def add_layer(self):
        """ Add a soil layer
        """
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_13.setEnabled(True)
        self.ui.pushButton_5.setEnabled(True)
        # Add one more soil layer
        NUMBER_layer = len(self.Layer_polygons)
        if NUMBER_layer > 99:
            self.dialog.show_message_box('Warning', ' Only up to 100 layers are allowed!')
        
        else:
            try:
                self.ui.tableWidget.blockSignals(True)  # temporary block signals
                
                # Check input values in table
                tops = []
                bottoms = []
                borehole_i = int(1) 
                for borehole in self.Boreholes:
                    top = QtWidgets.QTableWidgetItem(self.ui.tableWidget.item(NUMBER_layer, 2*(borehole_i - 1))).text()
                    bottom = QtWidgets.QTableWidgetItem(self.ui.tableWidget.item(NUMBER_layer, 2*(borehole_i - 1) + 1)).text()
                    tops.append(float(top))
                    bottoms.append(float(bottom))
                    borehole_i += 1
                    
                if '' in (tops + bottoms ):
                    self.dialog.show_message_box('Warning', "Please check if values for layer's tops and bottoms have been entered!")
                    
                elif any([bottom >= top for bottom, top in zip(bottoms, tops)]):
                    self.dialog.show_message_box('Warning', "Layer's bottom cannot be at or above its top!")
                    
                else:
                    # Process adding layer further, connecting signals
                    layer_polygon = self.plaxman_x.process_adding_layer(self.Layer_polygons, self.Boreholes, tops, bottoms, self.geometry)

                    # Append a new layer polyon
                    self.Layer_polygons.append(layer_polygon)

                self.ui.tableWidget.blockSignals(False)  # unblock signals

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if top and bottom values are correctly entered!')


    def remove_layer(self):
        """ Remove the last soil layer
        """
        self.plaxman_x.remove_last_layer(self.Layer_polygons, self.Boreholes, self.geometry)


    def match_json_name_soil_model(self, user_soil_name, soil_model):
        """ Matches soil name for json_item by removing ',' and replacing ' ' with '_'
        If this matching rule is changed, the same should be changed in open_edit_soil_xx boxes in gui_all_dialogs_gui.py.
        """
        json_item = user_soil_name
        json_item = [item.strip() for item in json_item.split(',')]
        json_item.append(soil_model)
        json_item = '_'.join(json_item)
        json_item = json_item.replace(' ', '_')
        
        return json_item

    
    def define_soil_material(self):
        """ Define soil by loading and editing predefined library
        """
        soil_model = self.ui.comboBox_3.currentText()
        user_soil_name = self.ui.lineEdit_55.text()    # soil name is given by user
        soil_name_for_checking = self.match_json_name_soil_model(user_soil_name, soil_model)

        soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in self.Soilmaterials]
        if user_soil_name is '':
            self.dialog.show_message_box('Warning', "Soil name cannot be empty!")

        elif (soil_name_for_checking + '__' in soilmaterial_json_items):
            self.dialog.show_message_box('Warning', "Soil name '{}' is already given, please use another name for your soil!".format(user_soil_name))

        else:
            # proceed adding a new soil material
            if soil_model == 'HS':            
                self.dialog.open_edit_soil_HS(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'MC':
                self.dialog.open_edit_soil_MC(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'HSsmall':
                self.dialog.open_edit_soil_HSsmall(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'        
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'LE':
                self.dialog.open_edit_soil_LE(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'        
                    self.current_material_color = self.dialog.soil_edit_box.color

            # update the list of soil materials            
            if self.dialog.soil_edit_box.done is True:
                soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in self.Soilmaterials]
                if self.material_json_item not in soilmaterial_json_items:
                    new_soilmaterial ={'json_item': self.material_json_item, 'soil_model': soil_model, 'correlations_ve': self.dialog.soil_edit_box.correlations_ve}
                    new_soilmaterial['color'] = self.current_material_color
                    self.Soilmaterials.append(new_soilmaterial)
                    self.fill_soilmaterials_in_combobox(self.ui.comboBox_17, self.Soilmaterials)
                    self.ui.comboBox_17.setCurrentIndex(self.ui.comboBox_17.count() - 1)
                    self.fill_soilmaterials_in_combobox(self.ui.comboBox_18, self.Soilmaterials)
                    self.ui.comboBox_18.setCurrentIndex(self.ui.comboBox_18.count() - 1)
                    self.fill_soilmaterials_in_combobox(self.ui.comboBox_19, self.Soilmaterials)
                    self.fill_soilmaterials_in_combobox(self.ui.comboBox_29, self.Soilmaterials)

                print('Soil {} is defined'.format(self.material_json_item))


    def fill_soilmaterials_in_combobox(self, combobox, Soilmaterials):
        """ Fills soil materials in combobox, with color
        """
        def combo_changed():
            for soilmat in Soilmaterials:
                if soilmat['json_item'] == combobox.currentText():
                    combobox.setStyleSheet("QComboBox:editable{ background-color: %s}" % QColor('white').name())
                    combobox.setStyleSheet("QComboBox:editable{ color: %s}" % soilmat['color'])
                    
        combobox.clear()
        model = combobox.model()
        for soilmat in Soilmaterials:
            entry = QStandardItem(soilmat['json_item'])
            color = soilmat['color']
            entry.setForeground(QColor(color))
            entry.setBackground(QColor('white'))
            model.appendRow(entry)

        combobox.currentIndexChanged.connect(combo_changed)

    
    def change_soil_properties(self):
        """ Change soil properties
        """
        # which soil
        json_item_selected = self.ui.comboBox_18.currentText()
        selected_soil = None
        for soilmaterial in self.Soilmaterials:
            if soilmaterial['json_item'] == json_item_selected:
                selected_soil = soilmaterial
                break

        if 'MC'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_MC('MC', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user 
            self.current_material_color = self.dialog.soil_edit_box.color

        elif 'HSsmall'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_HSsmall('HSsmall', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user
            self.current_material_color = self.dialog.soil_edit_box.color

        elif 'HS'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_HS('HS', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user
            self.current_material_color = self.dialog.soil_edit_box.color

        elif 'LE'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_LE('LE', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user
            self.current_material_color = self.dialog.soil_edit_box.color
        
        if self.dialog.soil_edit_box.done is True:
            print('Properties of soil {} are modified'.format(self.material_json_item))
        
        # update correlations_ve, color
        selected_soil['correlations_ve'] = self.dialog.soil_edit_box.correlations_ve
        selected_soil['color'] = self.current_material_color
        self.update_soil_layer_color(selected_soil)


    def update_soil_layer_color(self, soilmaterial):
        """ Updates color for the asssigned soil layer
        """
        for i_layer, layer in enumerate(self.Layer_polygons):
            if layer['soilmaterial_layer'] == soilmaterial['json_item']:
                self.plot_canvas.undo_plot_pathpatches(layer['pathpatch_layer'])
                layer['pathpatch_layer'] = self.plot_canvas.plot_assigned_layer(layer['path_polygon'], soilmaterial['color'])

                # change material colour in json files
                PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
                material_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial['json_item'] + '.json')
                material_moniman_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial['json_item'] + 'moniman.json')
                set_material_color(material_file_path, soilmaterial['color'])
                set_material_color(material_moniman_file_path, soilmaterial['color'])
                for col in range(1, 2*len(self.Boreholes), 2):
                    self.ui.tableWidget.item(i_layer, col).setBackground(QColor(*hex_to_rgb(soilmaterial['color'])))


    def edit_all_layers(self):
        """ Opens all soil layers for viewing and editting
        """
        self.plaxman_x.open_all_layers(self.Layer_polygons, self.Boreholes, self.Soilmaterials, self.geometry)


    def edit_all_soils(self):
        """ Opens all soils for viewing and editting
        """
        self.plaxman_x.open_all_soils(self.Layer_polygons)


    def delete_soil(self):
        """ Deletes the selected soil
        """
        selected_soil = self.ui.comboBox_18.currentText() # json_item
        if self.check_soil_is_assigned(selected_soil):
            self.dialog.show_message_box('Warning', 'Please remove soil polygons/ clusters and undo soil layer assignments whose soil is {}!'.format(selected_soil))

        else:
            # remove the selected soil in comboboxes
            soilmaterial_to_delete = [soilmaterial for soilmaterial in self.Soilmaterials if soilmaterial['json_item'] == selected_soil]
            soilmaterial_to_delete_idx = self.Soilmaterials.index(soilmaterial_to_delete[0])
            soilmaterial_deleted = self.Soilmaterials.pop(soilmaterial_to_delete_idx)
                    

            self.remove_comboBoxItem(self.ui.comboBox_18, selected_soil)
            self.remove_comboBoxItem(self.ui.comboBox_15, selected_soil)
            self.remove_comboBoxItem(self.ui.comboBox_17, selected_soil)
            self.remove_comboBoxItem(self.ui.comboBox_19, selected_soil)    # in Backman
            self.remove_comboBoxItem(self.ui.comboBox_29, selected_soil)    # in Sensiman
            # remove corresponding material files
            PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
            material_file = join(PATH_MATERIAL_LIBRARY, selected_soil + '.json')
            material_file_moniman = join(PATH_MATERIAL_LIBRARY, selected_soil + 'moniman.json')
            remove(material_file)
            remove(material_file_moniman)

            print('Soil {} is deleted'.format(soilmaterial_deleted))


    def remove_comboBoxItem(self, comboBox, item_text):
        """ Removes item in comboBox
        """
        for i in range(comboBox.count()):
            if comboBox.itemText(i) == item_text:
                comboBox.removeItem(i)
                break


    def check_soil_is_assigned(self, soil):
        """ Checks if soil material is assinged in Layers, Polygons, or Soilclusters
        """
        isAssigned = False
        for layer in self.Layer_polygons:
            if 'soilmaterial_layer' in layer:
                if layer['soilmaterial_layer'] == soil:
                    isAssigned = True
                    break

        for soilcluster in self.Soilclusters:
            if soilcluster['soilmaterial'] == soil:
                isAssigned = True
                break

        for polygon in self.Polygons:
            if polygon['soilmaterial'] == soil:
                isAssigned = True
                break

        return isAssigned
        

    def assign_material(self):
        """ Assign material to soil layer
        """
        # change material_json_item to the selected item in comboBox_18
        selected_soil = self.ui.comboBox_18.currentText()
        i_layer = int(self.ui.comboBox_4.currentText().split()[-1]) - 1

        self.plaxman_x.process_assigning_material(selected_soil, i_layer, self.Soilmaterials, self.Layer_polygons, self.Boreholes)

        
    def undo_assign_material(self):
        """ Undo material assignment to the selected soil layer
        """
        current_layer = self.ui.comboBox_4.currentText().split()
        if self.Layer_polygons[int(current_layer[1]) - 1]['pathpatch_layer'] is not None:
            self.ui.tableWidget.blockSignals(True)  # temporary block signals
            layer_pathpathch_to_undo = self.Layer_polygons[int(current_layer[1]) - 1]['pathpatch_layer']
            
            self.Layer_polygons[int(current_layer[1]) - 1]['pathpatch_layer'] = None
            self.Layer_polygons[int(current_layer[1]) - 1]['soilmaterial_layer'] = None
            del self.Layer_polygons[int(current_layer[1]) - 1]['soilmaterial_layer']
            
            self.Layer_polygons[int(current_layer[1]) - 1]['shaded'] = False
            self.plot_canvas.undo_plot_pathpatches(layer_pathpathch_to_undo)
            
            plaxis2d_input.unassign_soil_layer(self.plaxis2d_input_file, int(current_layer[1]) - 1)

            for col in range(2*len(self.Boreholes)):
                self.ui.tableWidget.item(int(current_layer[1]) - 1, col).setBackground(QColor(255, 255, 255))
                
            print('Soil assigment to Layer {} is undone'.format(current_layer[1]))

            # refill color in cells for borehole's top
            for i_layer in range(len(self.Layer_polygons)+1):
                for borehole_i, _ in enumerate(self.Boreholes):
                    self.ui.tableWidget.item(i_layer, 2*borehole_i).setBackground(QColor(242, 255, 116)) # light yellow, predictive layer

            self.ui.tableWidget.blockSignals(False)  # unblock signals
    

    def undo_assign_materials(self):
        """ Undo all material assigment
        """
        self.plaxman_x.undo_all_assign_materials(self.Layer_polygons, self.Boreholes)
    

    def define_wall(self):
        """ Define wall properties
        """
        wall_type = self.ui.comboBox_5.currentText()       
        wall_name = self.ui.lineEdit_57.text()

        wallmaterial_json_items = [wallmaterial['json_item'] for wallmaterial in self.Wallmaterials]
        if wall_name is '' and wall_type != 'Steel profile H/U': # wall_name must not be empty
            self.dialog.show_message_box('Warning', "Wall name cannot be empty!")
        
        elif (wall_name in wallmaterial_json_items):
            self.dialog.show_message_box('Warning', "Wall name '{}' is already given, please use another name for your wall!".format(wall_name))
        
        else:
            SPW131=False
            if wall_type == 'Dwall':
                self.dialog.open_edit_wall_Dwall(wall_type, wall_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif wall_type == 'SPW':
                self.dialog.open_edit_wall_SPW(wall_type, wall_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color
                    SPW131 = self.dialog.soil_edit_box.SPW131  # SPW131 system or not

            elif wall_type == 'CPW':
                self.dialog.open_edit_wall_CPW(wall_type, wall_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color
            
            elif wall_type == 'Steel profile H/U':
                self.dialog.open_edit_wall_Steel_profile(wall_type, wall_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif wall_type == 'MIP':
                self.dialog.open_edit_wall_MIP(wall_type, wall_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            # update the list of soil materials            
            if self.dialog.soil_edit_box.done is True:
                new_wallmaterial = {'json_item': self.wall_json_item, 'SPW131': SPW131, 'wall_type': wall_type, 'color': self.current_material_color}
                self.Wallmaterials.append(new_wallmaterial)
                self.ui.comboBox_17.setCurrentIndex(self.ui.comboBox_32.count() - 1)
                self.fill_soilmaterials_in_combobox(self.ui.comboBox_32, self.Wallmaterials)

                print('Wall {} is defined'.format(self.wall_json_item))


    def change_wall_properties(self):
        """ Change wall properties
        """
        # which wall   
        user_wall_name =  self.ui.comboBox_32.currentText()
        selected_wallmaterial = None
        for wallmaterial in self.Wallmaterials:
            if wallmaterial['json_item'] == user_wall_name:
                selected_wallmaterial = wallmaterial
                break
            
        if user_wall_name != '':
            if 'Dwall' == selected_wallmaterial['wall_type']:
                self.dialog.open_edit_wall_Dwall('Dwall', selected_wallmaterial['json_item'], color=selected_wallmaterial['color'], isdefined=True)
                if self.dialog.soil_edit_box.json_item_user is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif 'SPW' == selected_wallmaterial['wall_type'] :
                self.dialog.open_edit_wall_SPW('SPW', selected_wallmaterial['json_item'], SPW131=selected_wallmaterial['SPW131'] ,color=selected_wallmaterial['color'], isdefined=True)
                if self.dialog.soil_edit_box.json_item_user is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif 'CPW' == selected_wallmaterial['wall_type']:
                self.dialog.open_edit_wall_CPW('CPW', selected_wallmaterial['json_item'], color=selected_wallmaterial['color'], isdefined=True)
                if self.dialog.soil_edit_box.json_item_user is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif 'Steel profile H/U' == selected_wallmaterial['wall_type']:
                self.dialog.open_edit_wall_Steel_profile('Steel profile H/U', selected_wallmaterial['json_item'], color=selected_wallmaterial['color'], isdefined=True)
                if self.dialog.soil_edit_box.json_item_user is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif 'MIP' == selected_wallmaterial['wall_type']:
                self.dialog.open_edit_wall_MIP('MIP', selected_wallmaterial['json_item'], color=selected_wallmaterial['color'], isdefined=True)
                if self.dialog.soil_edit_box.json_item_user is not None:
                    self.wall_json_item = self.dialog.soil_edit_box.json_item_user
                    self.current_material_color = self.dialog.soil_edit_box.color

            if self.dialog.soil_edit_box.done is True:
                print('Properties of wall {} are modified'.format(self.wall_json_item))

            # update color
            selected_wallmaterial['color'] = self.current_material_color
            self.update_wall_color(selected_wallmaterial)

            # replot wall after editing
            self.replot_wall_upon_editting(selected_wallmaterial)


    def replot_wall_upon_editting(self, wallmaterial):
        """ Replots wall after editing
        """
        for wall in self.Walls:
            if wall['json_item'] == wallmaterial['json_item']:
                # wall_thickness for plotting
                wall_thickness = 0.2
                profile_nos = int(1)
                if wall['wall_type'] in ['Dwall', 'MIP']:
                    wall_thickness = read_data_in_json_item(wall['json_item'], 'd')
                    spacing = 1.0   
                elif wall['wall_type'] in ['SPW', 'CPW']: # piled wall
                    wall_thickness = read_data_in_json_item(wall['json_item'], 'D')     # pile diameter
                    spacing = read_data_in_json_item(wall['json_item'], 'S')     # spacing between piles
                elif wall['wall_type'] == 'Steel profile H/U':
                    # read profile data from library
                    PATH_PROFILE_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN'],'solver\plaxis2d\profile_steels_H_U\jsons')
                    PATH_MONIMAN_OUTPUTS = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
                    profile_name = wall['json_item']
                    with open(join(PATH_PROFILE_LIBRARY, profile_name[0:-2] + '.json'), "r") as read_file:
                        data = json.load(read_file, object_pairs_hook = OrderedDict)
                    wall_thickness = float(data["h"])*0.001           # [m]
                    with open(join(PATH_MONIMAN_OUTPUTS, profile_name + 'moniman.json'), "r") as read_file:
                        data = json.load(read_file, object_pairs_hook = OrderedDict)
                    profile_nos = int(data["nos"])
                    spacing = read_data_in_json_item(wall['json_item'], 'S')     # spacing between piles

                wall['profile_nos'] = profile_nos   # store number of profiles for plotting
                wall['wall_thickness'] = wall_thickness
                wall['spacing'] = spacing

                # repaint plot canvas for all walls
                self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])
                wall['pathpatches'] = self.plot_canvas.plot_wall(wall, wall['color'])


    def update_wall_color(self, wallmaterial):
        """ Updates color information in wall material files, replot if needed
        """
        # change material colour in json files
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        material_file_path = join(PATH_MATERIAL_LIBRARY, wallmaterial['json_item'] + '.json')
        material_moniman_file_path = join(PATH_MATERIAL_LIBRARY, wallmaterial['json_item'] + 'moniman.json')
        set_material_color(material_file_path, wallmaterial['color'])
        set_material_color(material_moniman_file_path, wallmaterial['color'])

        for wall in self.Walls:
            if wall['json_item'] == wallmaterial['json_item']:
                # replot
                wall['color'] = [wallmaterial['color'], '#55ff00', '#55ff00', '#000000']   # color string for (wall, pos. interface, neg. interface, annotation)
                self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])
                wall['pathpatches'] = self.plot_canvas.plot_wall(wall, wall['color'])


    def delete_wall_material(self):
        """ Deletes the selected wall material
        """
        selected_wallmaterial = self.ui.comboBox_32.currentText() # json_item
        if self.check_wall_material_is_assigned(selected_wallmaterial):
            self.dialog.show_message_box('Warning', 'Wall material {} has been assigned to wall. Please remove wall first!'.format(selected_wallmaterial))

        else:
            # remove the selected soil in comboboxes
            wallmaterial_to_delete = [wallmaterial for wallmaterial in self.Wallmaterials if wallmaterial['json_item'] == selected_wallmaterial]
            wallmaterial_to_delete_idx = self.Wallmaterials.index(wallmaterial_to_delete[0])
            wallmaterial_deleted = self.Wallmaterials.pop(wallmaterial_to_delete_idx)
                    

            self.remove_comboBoxItem(self.ui.comboBox_32, selected_wallmaterial)
            # remove corresponding material files
            PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
            material_file = join(PATH_MATERIAL_LIBRARY, selected_wallmaterial + '.json')
            material_file_moniman = join(PATH_MATERIAL_LIBRARY, selected_wallmaterial + 'moniman.json')
            remove(material_file)
            remove(material_file_moniman)

            self.fill_soilmaterials_in_combobox(self.ui.comboBox_32, self.Wallmaterials)

            print('Wall material {} is deleted'.format(wallmaterial_deleted))


    def check_wall_material_is_assigned(self, json_item):
        """ Checks if the wall material has been assigned
        """
        isAssigned = False
        wallmaterial_json_items = [wall['json_item'] for wall in self.Walls]
        if json_item in wallmaterial_json_items:
            isAssigned = True

        return isAssigned


    def add_wall(self):
        """ Adds a wall
        """
        #wall_type = self.ui.comboBox_5.currentText()
        redefined_json_item =  self.ui.comboBox_32.currentText()
        #redefined_json_item = 'WALL_' + wall_type + '__'        
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        wall_file_path = join(PATH_MATERIAL_LIBRARY, redefined_json_item + '.json')
        
        # get color, wall type, SPW131 if secant piles, from the selected wall material
        SPW131 = False
        for wallmat in self.Wallmaterials:
            if wallmat['json_item'] == redefined_json_item:
                color = wallmat['color']
                wall_type = wallmat['wall_type']
                if 'SPW131' in wallmat:
                    SPW131 = wallmat['SPW131']

        if not isfile(wall_file_path):
            self.dialog.show_message_box('Warning', 'Please edit wall properties!')
        else:
            try:
                point1_text = self.ui.lineEdit_7.text()
                point2_text = self.ui.lineEdit_9.text()
                
                point1_x = float(point1_text.split(',')[0])
                point1_y = float(point1_text.split(',')[1])
                point2_x = float(point2_text.split(',')[0])
                point2_y = float(point2_text.split(',')[1])
                
                print('Wall properties file: {}'.format(wall_file_path))
                
                pos_interface = self.ui.checkBox.checkState()
                neg_interface = self.ui.checkBox_2.checkState()
                
                # set material colour
                #color = self.current_material_color.name()
                set_material_color(wall_file_path, color)

                # suggest values for ground anchors and struts
                self.ui.lineEdit_11.setText(str(point1_x) + ', ' + str(point1_y - 0.5*abs(point2_y - point1_y)))
                self.ui.lineEdit_29.setText(str(point1_x) + ', ' + str(point1_y - 0.5*abs(point2_y - point1_y)))
                # for soil clusters
                self.ui.lineEdit_34.setText(str(self.geometry[0]) + ', ' + str(self.geometry[-1]))
                self.ui.lineEdit_36.setText(str(self.geometry[0]) + ', ' + str(self.geometry[-1] - 3))
                self.ui.lineEdit_35.setText(str(point1_x) + ', ' + str(self.geometry[-1]))
                self.ui.lineEdit_37.setText(str(point1_x) + ', ' + str(self.geometry[-1] - 3))
                # for drain
                self.ui.lineEdit_10.setText(str(point2_x) + ', ' + str(point2_y))
                self.ui.lineEdit_40.setText(str(self.geometry[0]) + ', ' + str(point2_y - 5))
                self.ui.lineEdit_41.setText(str(point1_x) + ', ' + str(point2_y - 5))
                # for loads
                self.ui.lineEdit_17.setText(str(point1_x) + ', ' + str(self.geometry[-1]))
                self.ui.lineEdit_19.setText(str(self.geometry[2]) + ', ' + str(self.geometry[-1]))      
                self.ui.lineEdit_25.setText(str(abs(self.geometry[2] - point1_x)/2) + ', ' + str(self.geometry[-1]))
                # for outputs
                self.ui.lineEdit_18.setText(str(point1_x) + ', ' + str(self.geometry[-1]))
                self.ui.lineEdit_20.setText(str(self.geometry[2]) + ', ' + str(self.geometry[-1]))  
                self.ui.lineEdit_44.setText(str(point1_x) + ', ' + str(point1_y))
                self.ui.lineEdit_45.setText(str(point2_x) + ', ' + str(point2_y))
        
                new_wall = {}
                new_wall['point1'] = [point1_x, point1_y] # list instead of tuple for design optimization
                new_wall['point2'] = [point2_x, point2_y] # list instead of tuple for design optimization
                new_wall['interf_pos'] = (pos_interface == 2)
                new_wall['interf_neg'] = (neg_interface == 2)
                new_wall['json_item'] = redefined_json_item # for wall name used in plaxis2d_input
                new_wall['id'] = randint(100000, 999999)
                new_wall['wall_type'] = wall_type
                new_wall['wall_name'] = redefined_json_item         # for selecting wall in Optiman
                wall_length = np.sqrt((new_wall['point2'][1] - new_wall['point1'][1])**2 + (new_wall['point2'][0] - new_wall['point1'][0])**2)
                new_wall['wall_length'] = wall_length               # design varialbe in Optiman
                new_wall['color'] = [color, '#55ff00', '#55ff00', '#000000']   # color string for (wall, pos. interface, neg. interface, annotation)
                new_wall['SPW131'] = SPW131     # secant piles 1:3:1 or not

                # wall_thickness for plotting
                wall_thickness = 0.2
                profile_nos = int(1)
                if new_wall['wall_type'] in ['Dwall', 'MIP']:
                    wall_thickness = read_data_in_json_item(new_wall['json_item'], 'd')
                    spacing = 1.0   
                elif new_wall['wall_type'] in ['SPW', 'CPW']: # piled wall
                    wall_thickness = read_data_in_json_item(new_wall['json_item'], 'D')     # pile diameter
                    spacing = read_data_in_json_item(new_wall['json_item'], 'S')     # spacing between piles
                elif new_wall['wall_type'] == 'Steel profile H/U':
                    # read profile data from library
                    PATH_PROFILE_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN'],'solver\plaxis2d\profile_steels_H_U\jsons')
                    PATH_MONIMAN_OUTPUTS = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
                    profile_name = new_wall['json_item']
                    with open(join(PATH_PROFILE_LIBRARY, profile_name[0:-2] + '.json'), "r") as read_file:
                        data = json.load(read_file, object_pairs_hook = OrderedDict)
                    wall_thickness = float(data["h"])*0.001           # [m]
                    with open(join(PATH_MONIMAN_OUTPUTS, profile_name + 'moniman.json'), "r") as read_file:
                        data = json.load(read_file, object_pairs_hook = OrderedDict)
                    profile_nos = int(data["nos"])
                    spacing = read_data_in_json_item(new_wall['json_item'], 'S')     # spacing between piles

                new_wall['profile_nos'] = profile_nos   # store number of profiles for plotting
                new_wall['fyk'] = 235.0
                new_wall['wall_thickness'] = wall_thickness
                new_wall['spacing'] = spacing

                
                self.ui.comboBox_14.addItem(str(new_wall['id']))    # for wall outputs in Plaxman
                self.ui.comboBox_49.addItem(str(new_wall['id']))    # for selection of wall parameters in Sensiman
                self.ui.comboBox_53.addItem(str(new_wall['id']))    # for selection of wall parameters in Backman
                
                self.Walls.append(new_wall)
                
                wall_pathpatches = self.plot_canvas.plot_wall(new_wall, new_wall['color'])
                new_wall['pathpatches'] = wall_pathpatches
                plaxis2d_input.add_wall(self.plaxis2d_input_file, 'g_i', new_wall, new_wall['json_item'], wall_file_path)
                self.plaxman_x.display_walls_on_table(self.Walls)   # show walls on table
                print('A new wall with properties of {} is created'.format(new_wall['json_item']))    
                
            except (ValueError, IndexError) as e:
                self.dialog.show_message_box('Warning', 'Please check if all points are correctly entered!')
    

    def remove_wall(self): 
        """ Remove one or more walls
        """
        if len(self.Walls) > 0:
            removed_wall_ids = self.remove_structure(self.Walls, 'Wall selection for removal', '##WALL', 17)        
            for wall_id in removed_wall_ids:
                self.remove_comboBoxItem(self.ui.comboBox_14, str(wall_id))

            self.plaxman_x.display_walls_on_table(self.Walls)   # show walls on table


    def update_wall_bottom(self, wall_id, embedment_depth, final_excavation_level):
        """ Changes position for bottom of the wall
        """
        for wall in self.Walls:
            if wall['id'] == int(wall_id):
                # update wall properties in plaxman model
                wall['point2'][1] =  final_excavation_level - embedment_depth
                print('Wall bottom is at {}'.format(wall['point2'][1]))

                # update plaxis input file
                plaxis2d_input.update_wall(self.plaxis2d_input_file, 'g_i', wall)

                # repaint plot canvas
                self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])
                wall['pathpatches'] = self.plot_canvas.plot_wall(wall, wall['color'])

                break


    def edit_strand(self):                
        """ Defines free-length part of a ground anchor
        """
        anchor_name = self.ui.lineEdit_62.text()

        if anchor_name is '':
            self.dialog.show_message_box('Warning', 'Anchor name cannot be empty!')

        else:
            try: 
                strand_no = int(self.ui.lineEdit_23.text())
                strand_dia = self.ui.comboBox_6.currentText()
                Lspacing = float(self.ui.lineEdit_27.text())
        
                self.dialog.open_edit_strand(strand_dia, strand_no, Lspacing, anchor_name)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.strand_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                if self.dialog.soil_edit_box.done is True:
                    self.ui.comboBox_37.addItem(self.strand_json_item)
                    self.ui.comboBox_37.setCurrentIndex(self.ui.comboBox_37.count()-1)
                    print('Anchor strand {} is defined'.format(self.strand_json_item))

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if the number of strands is correctly entered!')
    

    def change_strand_properties(self):                
        """ Changes properties of the free-length part of a ground anchor
        """
        #print(self.strand_json_item)
        defined_strand_name = self.ui.comboBox_37.currentText() # selected strand name

        if defined_strand_name != '':
            try: 
                strand_no = int(self.ui.lineEdit_23.text())
                strand_dia = self.ui.comboBox_6.currentText()
                Lspacing = float(self.ui.lineEdit_27.text())
        
                self.dialog.open_edit_strand(strand_dia, strand_no, Lspacing, defined_strand_name, True)

                if self.dialog.soil_edit_box.done is True:
                    print('Properties of strand {} are modified'.format(defined_strand_name))

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if the number of strands is correctly entered!')


    def edit_grout(self):
        """ Defines fixed-length part of a ground anchor
        """
        anchor_name = self.ui.lineEdit_62.text()

        if anchor_name is '':
            self.dialog.show_message_box('Warning', 'Anchor name cannot be empty!')
        
        else:
            try: 
                strand_no = int(self.ui.lineEdit_23.text())
                strand_dia_input = self.ui.comboBox_6.currentText()
                if strand_dia_input == "0.6''":
                    strand_dia = 140.0E-6 # strand_area m^2
                    #strand_dia = 0.01524 # meter
                elif strand_dia_input == "0.62''":
                    strand_dia = 150.0E-6 # stran_area m^2
                    #strand_dia = 0.015748 # meter

                Lspacing = float(self.ui.lineEdit_27.text())
                grout_type = self.ui.comboBox_7.currentText()

                if grout_type == 'Linear':
                    self.dialog.open_edit_grout_Linear(strand_dia, strand_no, Lspacing, anchor_name)
                    if self.dialog.soil_edit_box.json_item is not None:
                        self.grout_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                elif grout_type == 'Multi-linear':
                    self.dialog.open_edit_grout_Multilinear(strand_dia, strand_no, Lspacing, anchor_name)
                    if self.dialog.soil_edit_box.json_item is not None:
                        self.grout_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                if self.dialog.soil_edit_box.done is True:
                    self.ui.comboBox_38.addItem(self.grout_json_item)
                    self.ui.comboBox_38.setCurrentIndex(self.ui.comboBox_38.count()-1)
                    print('Anchor grout {} is defined'.format(self.grout_json_item))

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if the number of strands is correctly entered!')
    
    
    def change_grout_properties(self):
        """ Change properties of the fixed-length part of a ground anchor
        """
        defined_grout_name = self.ui.comboBox_38.currentText() # selected grout name

        if defined_grout_name != '':
            try: 
                strand_no = int(self.ui.lineEdit_23.text())
                strand_dia_input = self.ui.comboBox_6.currentText()
                if strand_dia_input == "0.6''":
                    strand_dia = 140.0E-6
                elif strand_dia_input == "0.62''":
                    strand_dia = 150.0E-6

                Lspacing = float(self.ui.lineEdit_27.text())
                #grout_type = self.ui.comboBox_7.currentText()

                if 'Linear' in defined_grout_name:
                    self.dialog.open_edit_grout_Linear(strand_dia, strand_no, Lspacing, defined_grout_name, True)

                elif 'Multilinear' in defined_grout_name:
                    self.dialog.open_edit_grout_Multilinear(strand_dia, strand_no, Lspacing, defined_grout_name, True)

                if self.dialog.soil_edit_box.done is True:
                    print('Properties of grout {} are modified'.format(defined_grout_name))

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if the number of strands is correctly entered!')


    def add_ground_anchor(self):
        """ Add a new ground anchor
        """
        defined_strand_name = self.ui.comboBox_37.currentText() # selected strand name
        defined_grout_name = self.ui.comboBox_38.currentText() # selected grout name

        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        strand_file_path = join(PATH_MATERIAL_LIBRARY, defined_strand_name + '.json')
        grout_file_path = join(PATH_MATERIAL_LIBRARY, defined_grout_name + '.json')

        if defined_strand_name == '':
            self.dialog.show_message_box('Warning', 'Please edit strand properties!')
        elif defined_grout_name == '':
            self.dialog.show_message_box('Warning', 'Please edit grout properties!')
        else:
            try:
                print('Strand properties file: {}'.format(strand_file_path))
                print('Grout properties file: {}'.format(grout_file_path))
                
                point_text = self.ui.lineEdit_11.text()
                x = float(point_text.split(',')[0])
                y = float(point_text.split(',')[1])
                angle = float(self.ui.lineEdit_16.text())
                length_free = float(self.ui.lineEdit_14.text())
                length_fixed = float(self.ui.lineEdit_15.text())
                Lspacing = float(self.ui.lineEdit_27.text())
                
                new_anchor = {}
                new_anchor['position'] = [x, y]
                new_anchor['angle'] = angle
                new_anchor['length_free'] = length_free
                new_anchor['length_fixed'] = length_fixed
                new_anchor['Lspacing'] = Lspacing   # added for Optiman (but please use Lspacing from json file for model updating)
                new_anchor['grout_json_item'] = defined_grout_name
                new_anchor['strand_json_item'] = defined_strand_name
                new_anchor['id'] = randint(100000, 999999)
                new_anchor['F_prestress'] = 450.0

                # additional fields for anchor dimensioning
                strand_no = int(self.ui.lineEdit_23.text())
                strand_dia_input = self.ui.comboBox_6.currentText()
                new_anchor['strand number'] = strand_no
                new_anchor['strand diameter'] = strand_dia_input
                new_anchor['F_anchor'] = 200.0 # by default
                new_anchor['strand grade'] = '1570/1770' # by default
                new_anchor['design situation'] = 'Situation E' # by default
                                 
                # parameters for waler beam
                new_anchor['waler_width_support'] = 0.5 # width of support plate, m
                new_anchor['waler_width_influence'] = 0.0 # width of influence for the calculation of normal force, Nm
                new_anchor['waler_type'] = 'concrete'   # 'concrete' or 'steel_profile'
                new_anchor['waler_concrete'] = {'b': 0.5, 'h': 0.5, 'edge_sep': 50, 'fck': 25.0, 'fyk': 500.0}      # units are m, m, mm, MPa, MPa
                new_anchor['waler_concrete_reinf_As_E'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
                new_anchor['waler_concrete_reinf_As_L'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
                new_anchor['waler_concrete_reinf_as'] = {'dia': '10', 'n_legs': 4, 'spacing': 25.0}  # spacing is in cm
                new_anchor['waler_steel_profile'] = {'profile_id': 'HEA1000', 'nos': int(1), 'fyk': 235.0}    # units are -, -, MPa
                new_anchor['F_support'] = 200.0 # by default

                self.Anchors.append(new_anchor)
                
                anchor_pathpatches = self.plot_canvas.plot_ground_anchor(new_anchor)
                new_anchor['pathpatches'] = anchor_pathpatches
                          
                plaxis2d_input.add_ground_anchor(self.plaxis2d_input_file, 'g_i', new_anchor, 
                                                strand_file_path, grout_file_path)
                

                print('A new ground anchor with properties of strand {0} and grout {1} is inserted'.format(defined_strand_name, defined_grout_name))    

                # show all ground anchors on table
                self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_25)
                self.plaxman_x.display_ground_anchors_comboboxes(self.Anchors, self.ui.comboBox_38, self.ui.comboBox_37)

                
            except (ValueError, IndexError) as e:
                self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')


    def remove_ground_anchor(self):        
        """ Remove ground anchor(s)
        """
        self.remove_structure(self.Anchors, 'Ground anchor selection for removal', '##GROUND_ANCHOR', 18)        

        # show all ground anchors on table
        self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_25)
        self.plaxman_x.display_ground_anchors_comboboxes(self.Anchors, self.ui.comboBox_38, self.ui.comboBox_37)


    def edit_strut(self):
        """ Defines properties for strut
        """
        strut_name = self.ui.lineEdit_65.text()
        if strut_name is '':
            self.dialog.show_message_box('Warning', 'Strut name cannot be empty!')
        
        else:
            try:
                Lspacing = float(self.ui.lineEdit_31.text())
                strut_type = self.ui.comboBox_8.currentText()       

                if strut_type == 'Steel tube':
                    self.dialog.open_edit_strut_Steel_tube(Lspacing, strut_name)
                    if self.dialog.soil_edit_box.json_item is not None:
                        self.strut_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                elif strut_type == 'RC strut':
                    self.dialog.open_edit_strut_RC_bar(Lspacing, strut_name)
                    if self.dialog.soil_edit_box.json_item is not None:
                        self.strut_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                elif strut_type == 'RC slab':
                    self.dialog.open_edit_strut_RC_slab(strut_name)
                    if self.dialog.soil_edit_box.json_item is not None:
                        self.strut_json_item = self.dialog.soil_edit_box.json_item_user + '__'

                if self.dialog.soil_edit_box.done is True:
                    self.ui.comboBox_39.addItem(self.strut_json_item)
                    self.ui.comboBox_39.setCurrentIndex(self.ui.comboBox_39.count()-1)
                    print('Strut {} is defined'.format(self.strut_json_item))
        
            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if Lspacing is correctly entered!')
         

    def change_strut_properties(self):
        """ Change properties of a defined strut
        """
        defined_strut_name = self.ui.comboBox_39.currentText()

        if defined_strut_name != '':
            try:
                Lspacing = float(self.ui.lineEdit_31.text())
                #strut_type = self.ui.comboBox_8.currentText()       
                    
                if 'Steel_tube' in defined_strut_name:
                    self.dialog.open_edit_strut_Steel_tube(Lspacing, defined_strut_name, True)
                        
                elif 'RC_strut' in defined_strut_name:
                    self.dialog.open_edit_strut_RC_bar(Lspacing, defined_strut_name, True)
                
                elif 'RC_slab' in defined_strut_name:
                    self.dialog.open_edit_strut_RC_slab(defined_strut_name, True)
        
                if self.dialog.soil_edit_box.done is True:
                    print('Properties of strut {} are modified'.format(defined_strut_name))

            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if Lspacing is correctly entered!')



    def add_strut(self):
        """ Add a strut
        """
        defined_strut_name = self.ui.comboBox_39.currentText()

        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        strut_file_path = join(PATH_MATERIAL_LIBRARY, defined_strut_name + '.json')
        strut_usage = self.ui.comboBox_48.currentText() # either 'Strut' or 'Slab'
        Lspacing = float(self.ui.lineEdit_31.text())
            
                    
        if not isfile(strut_file_path):
            self.dialog.show_message_box('Warning', 'Please edit strut properties!')

        else:
            try:
                print('Strut properties file: {}'.format(strut_file_path))
                
                point_text = self.ui.lineEdit_29.text()
                x = float(point_text.split(',')[0])
                y = float(point_text.split(',')[1])
                
                direct_x = float(self.ui.lineEdit_32.text())
                direct_y = float(self.ui.lineEdit_33.text())
                                
                new_strut = {}
                new_strut['position'] = [x, y]
                new_strut['direct_x'] = direct_x
                new_strut['direct_y'] = direct_y
                new_strut['Lspacing'] = Lspacing
                new_strut['F_prestress'] = 0.0  # no prestress by default
                new_strut['usage'] = strut_usage
                new_strut['json_item'] = self.strut_json_item
                new_strut['id'] = randint(100000, 999999)

                # parameters for dimensioning, will be overwritten in the strut dimensing tool
                new_strut['F_strut'] = 200.0 # by default, to be overwriten
                new_strut['slope_vert'] = math.atan(abs(new_strut['direct_y'])/abs(new_strut['direct_x']))*180/math.pi  # deg, newly introduced
                new_strut['slope_horiz'] = 0.0                                                                  # deg, newly intorduced: horizontal inclination (default 0.0, to be changed by user)
                new_strut['buckling length sy'] = 2*math.sqrt(new_strut['direct_x']**2 + new_strut['direct_y']**2)      # m, newly introduced
                new_strut['buckling length sz'] = 2*math.sqrt(new_strut['direct_x']**2 + new_strut['direct_y']**2)      # m, newly introduced: to be adjusted by user
                new_strut['eccentricity e/h'] = 0.1
                new_strut['eccentricity e/b'] = 0.0
                new_strut['strut_type'] = 'SteelTube'                          # 'SteelTube' or 'SteelProfile'
                new_strut['profile_id'] = ''                                   # newly introduced, to be assigned update_strut_layer()
                new_strut['nos'] = int(1)                   # number of beams  
                new_strut['distance_beam2beam'] = 100.0     # distance beam-to-beam [mm] 
                new_strut['assigned'] = False
                new_strut['design_loads'] = {'Nd': 100.0, 'Myd': 0.0, 'Mzd': 0.0}

                # parameters for waler beam
                new_strut['waler_width_support'] = 0.5 # width of support plate, m
                new_strut['waler_width_influence'] = 0.0 # width of influence for the calculation of normal force, Nm
                new_strut['waler_type'] = 'concrete'   # 'concrete' or 'steel_profile'
                new_strut['waler_concrete'] = {'b': 0.5, 'h': 0.5, 'edge_sep': 50, 'fck': 25.0, 'fyk': 500.0}      # units are m, m, mm, MPa, MPa
                new_strut['waler_concrete_reinf_As_E'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
                new_strut['waler_concrete_reinf_As_L'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
                new_strut['waler_concrete_reinf_as'] = {'dia': '10', 'n_legs': 4, 'spacing': 25.0}  # spacing is in cm
                new_strut['waler_steel_profile'] = {'profile_id': 'HEA1000', 'nos': int(1), 'fyk': 235.0}    # units are -, -, MPa
                new_strut['F_support'] = 200.0 # by default
                                 
                self.Struts.append(new_strut)

                self.ui.comboBox_50.addItem(str(new_strut['id']))    # for selection of strut parameters in Sensiman
                
                y_min = self.geometry[1] #x_min, y_min, x_max, y_max
                y_max = self.geometry[3]
                strut_pathpatches = self.plot_canvas.plot_strut(new_strut, y_min, y_max)
                new_strut['pathpatches'] = strut_pathpatches
                          
                plaxis2d_input.add_strut(self.plaxis2d_input_file, 'g_i', new_strut, strut_file_path)

                # show all struts on table
                self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_26)
                
                print('Strut of properties of {0} is inserted'.format(defined_strut_name))    
                
            except (ValueError, IndexError) as e:
                self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')
    

    def remove_strut(self):        
        """ Remove strut(s)
        """
        self.remove_structure(self.Struts, 'Strut selection for removal', '##STRUT', 13)

        # show all struts on table
        self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_26)


    def add_lineload(self):
        """ Add a lineload
        """
        try:
            lineload = {}
            point1_text = self.ui.lineEdit_17.text()
            lineload['point1'] = [float(point1_text.split(',')[0]), float(point1_text.split(',')[1])]
            point2_text = self.ui.lineEdit_19.text()
            lineload['point2'] = [float(point2_text.split(',')[0]), float(point2_text.split(',')[1])]
            lineload['qx'] = float(self.ui.lineEdit_21.text())
            lineload['qy'] = float(self.ui.lineEdit_22.text())
            lineload['id'] = randint(100000, 999999)
            
            self.Lineloads.append(lineload)
            
            lineload_pathpatches = self.plot_canvas.plot_lineload(lineload, self.geometry[1], self.geometry[3])
            lineload['pathpatches'] = lineload_pathpatches
            
            plaxis2d_input.add_lineload(self.plaxis2d_input_file, 'g_i', lineload)

            # show lineloads on table
            self.plaxman_x.display_lineloads_on_table(self.Lineloads, self.geometry[1], self.geometry[3])

            print('Lineload is added')
                     
        except (ValueError, IndexError) as e:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')


    def remove_lineload(self):        
        """ Remove a lineload
        """
        self.remove_structure(self.Lineloads, 'Lineload selection for removal', '##LINELOAD', 7)
        # show lineloads on table
        self.plaxman_x.display_lineloads_on_table(self.Lineloads, self.geometry[1], self.geometry[3])

    
    def add_pointload(self):
        """ Add a pointload
        """
        try:
            pointload = {}
            point_text = self.ui.lineEdit_25.text()
            pointload['point'] = [float(point_text.split(',')[0]), float(point_text.split(',')[1])]
            pointload['Fx'] = float(self.ui.lineEdit_24.text())
            pointload['Fy'] = float(self.ui.lineEdit_28.text())
            pointload['id'] = randint(100000, 999999)
            
            self.Pointloads.append(pointload)
            
            pointload_pathpatches = self.plot_canvas.plot_pointload(pointload, self.geometry[1], self.geometry[3])
            pointload['pathpatches'] = pointload_pathpatches
            
            plaxis2d_input.add_pointload(self.plaxis2d_input_file, 'g_i', pointload)

            self.plaxman_x.display_pointloads_on_table(self.Pointloads, self.geometry[1], self.geometry[3])

            print('Pointload is added')
                     
        except (ValueError, IndexError) as e:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')


    def remove_pointload(self):        
        """ Remove a pointload
        """
        self.remove_structure(self.Pointloads, 'Pointload selection for removal', '##POINTLOAD', 5)  
        self.plaxman_x.display_pointloads_on_table(self.Pointloads, self.geometry[1], self.geometry[3])

    
    def add_new_material(self):
        """ Add a new material
        """
        soil_model = self.ui.comboBox_16.currentText()
        user_soil_name = self.ui.lineEdit_58.text()    # soil name is given by user
        soil_name_for_checking = self.match_json_name_soil_model(user_soil_name, soil_model)

        soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in self.Soilmaterials]
        if user_soil_name is '':
            self.dialog.show_message_box('Warning', "Soil name cannot be empty!")

        elif (soil_name_for_checking + '__' in soilmaterial_json_items):
            self.dialog.show_message_box('Warning', "Soil name '{}' is already given, please use another name for your soil!".format(user_soil_name))
        
        else:
            if soil_model == 'HS':            
                self.dialog.open_edit_soil_HS(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'MC':
                self.dialog.open_edit_soil_MC(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'HSsmall':
                self.dialog.open_edit_soil_HSsmall(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'        
                    self.current_material_color = self.dialog.soil_edit_box.color

            elif soil_model == 'LE':
                self.dialog.open_edit_soil_LE(soil_model, user_soil_name, isdefined=False)
                if self.dialog.soil_edit_box.json_item is not None:
                    self.material_json_item = self.dialog.soil_edit_box.json_item_user + '__'
                    self.current_material_color = self.dialog.soil_edit_box.color

            # update the list of soil materials            
            soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in self.Soilmaterials]
            if self.material_json_item not in soilmaterial_json_items:
                new_soilmaterial ={'json_item': self.material_json_item, 'soil_model': soil_model, 'correlations_ve': self.dialog.soil_edit_box.correlations_ve}
                new_soilmaterial['color'] = self.current_material_color
                self.Soilmaterials.append(new_soilmaterial)
                self.fill_soilmaterials_in_combobox(self.ui.comboBox_17, self.Soilmaterials)
                self.ui.comboBox_17.setCurrentIndex(self.ui.comboBox_17.count() - 1)
                self.fill_soilmaterials_in_combobox(self.ui.comboBox_18, self.Soilmaterials)
                self.ui.comboBox_18.setCurrentIndex(self.ui.comboBox_18.count() - 1)
                self.fill_soilmaterials_in_combobox(self.ui.comboBox_19, self.Soilmaterials)
                self.fill_soilmaterials_in_combobox(self.ui.comboBox_29, self.Soilmaterials)
    
    
    def add_polygon_point(self, point_text):
        """ Add a point for free polygon
        """
        try:
            point = {}
            point['point'] = (float(point_text.split(',')[0]), float(point_text.split(',')[1])) 
            point['pathpatch'] = self.plot_canvas.plot_point(point['point'])
            self.polygonPoints.append(point)
            
        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the point is correctly entered!') 
            

    def add_polygon_points_rectangle(self, polygonPoints_current):
        """ Add 4 points for a rectangular polygon
        Now this 4-point polygon is used for defining the region of soil improvement
        """
        pointTL_text = self.ui.lineEdit_76.text()
        pointTR_text = self.ui.lineEdit_77.text()
        pointBL_text = self.ui.lineEdit_78.text()
        pointBR_text = self.ui.lineEdit_81.text()
        pointTL = [float(pointTL_text.split(',')[0]), float(pointTL_text.split(',')[1])]
        pointTR = [float(pointTR_text.split(',')[0]), float(pointTR_text.split(',')[1])]
        pointBL = [float(pointBL_text.split(',')[0]), float(pointBL_text.split(',')[1])]
        pointBR = [float(pointBR_text.split(',')[0]), float(pointBR_text.split(',')[1])]
        points = [pointTL, pointTR, pointBR, pointBL]

        # remove previously defined polygon points
        while polygonPoints_current:
            self.remove_polygon_point(polygonPoints_current)

        # add 4 new polygon points
        polygonPoints = []
        for point in points:
            poly_point = {}
            poly_point['point'] = point
            poly_point['pathpatch'] = self.plot_canvas.plot_point(poly_point['point'])
            polygonPoints.append(poly_point)
            
        return polygonPoints
            
            

    def update_polygon_points_rectangle(self, points_new):
        """ Update 4 points for a rectangular polygon
        """
        # remove previously defined polygon points
        while self.polygonPoints:
            self.remove_polygon_point(self.polygonPoints)

        for pnt in points_new:
            poly_point = {}
            poly_point['point'] = pnt
            poly_point['pathpatch'] = self.plot_canvas.plot_point(poly_point['point'])
            self.polygonPoints.append(poly_point)

        self.ui.lineEdit_76.setText(str(self.polygonPoints[0]['point'][0]) + ', ' + str(self.polygonPoints[0]['point'][1]))
        self.ui.lineEdit_77.setText(str(self.polygonPoints[1]['point'][0]) + ', ' + str(self.polygonPoints[1]['point'][1]))
        self.ui.lineEdit_81.setText(str(self.polygonPoints[2]['point'][0]) + ', ' + str(self.polygonPoints[2]['point'][1]))
        self.ui.lineEdit_78.setText(str(self.polygonPoints[3]['point'][0]) + ', ' + str(self.polygonPoints[3]['point'][1]))


    def update_polygon_points_rectangle_FDC(self, points_new, polygonPoints_current):
        """ Update 4 points for a rectangular polygon
        """
        # remove previously defined polygon points
        while polygonPoints_current:
            self.remove_polygon_point(polygonPoints_current)

        polygonPoints = []
        for pnt in points_new:
            poly_point = {}
            poly_point['point'] = pnt
            poly_point['pathpatch'] = self.plot_canvas.plot_point(poly_point['point'])
            polygonPoints.append(poly_point)

        self.show_polygon_points_rectangle_FDC(polygonPoints)

        return polygonPoints


    def show_polygon_points_rectangle_FDC(self, polygonPoints):
        """ Shows polyPoitns on the user interface
        """
        self.ui.lineEdit_76.setText(str(polygonPoints[0]['point'][0]) + ', ' + str(polygonPoints[0]['point'][1]))
        self.ui.lineEdit_77.setText(str(polygonPoints[1]['point'][0]) + ', ' + str(polygonPoints[1]['point'][1]))
        self.ui.lineEdit_81.setText(str(polygonPoints[2]['point'][0]) + ', ' + str(polygonPoints[2]['point'][1]))
        self.ui.lineEdit_78.setText(str(polygonPoints[3]['point'][0]) + ', ' + str(polygonPoints[3]['point'][1]))


    def remove_polygon_point_onclick(self):
        """
        """
        self.remove_polygon_point(self.polygonPoints)


    def remove_polygon_point(self, polygonPoints):
        """ Remove the last polygon point
        """
        if len(polygonPoints) > 0:
            deleted_point = polygonPoints.pop()   
            self.plot_canvas.undo_plot_pathpatches(deleted_point['pathpatch'])


    def change_polygon_points(self):
        """ Change all polygon points
        """
        if len(self.polygonPoints) > 0:
            # open dialog to change point coordinates
            self.dialog.open_edit_points_free_polygon(self.polygonPoints)
            #print('Update points: {}\n'.format(self.dialog.points_updated))

            # update self.polygonPoints and replot
            for (i, pnt) in enumerate(self.polygonPoints):
                pnt['point'] = self.dialog.points_updated[i]
                self.plot_canvas.undo_plot_pathpatches(pnt['pathpatch'])
                pnt['pathpatch'] = self.plot_canvas.plot_point(pnt['point'])

        
    def add_polygon(self):
        """ Add a polygon
        """
        if len(self.polygonPoints) < 3:
            self.dialog.show_message_box('Warning', 'Please add at least 3 points for the polygon!') 
        else:    
            soilmaterial = self.ui.comboBox_17.currentText()
            PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
            material_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial + '.json')

            # get color from the selected soil material
            for soilmat in self.Soilmaterials:
                if soilmat['json_item'] == soilmaterial:
                    color = soilmat['color']
            
            polygon = {}
            polygon['id'] = randint(100000, 999999)
            polygon['soilmaterial'] = soilmaterial
            polygon['points'] = [point['point'] for point in self.polygonPoints]
            
            #color = self.current_material_color.name()
            polygon['color'] = color
            polygon['to_deactivate'] = self.ui.checkBox_19.checkState() == 2    # soil polygon for deactivation at the initial phase
            polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], color)
            
            self.Polygons.append(polygon)
            
            
            plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, material_file_path)
            plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)
            
            # set material colour
            set_material_color(material_file_path, color)
            
            print('Polygon of material {} is added'.format(soilmaterial))
        
                
    def remove_polygon(self):        
        """ Remove polygon(s)
        """
        if len(self.Polygons) > 0:
            removed_polygon_ids = self.remove_structure_string_id(self.Polygons, 'Strut selection for removal', '##SOIL_POLYGON', 10)
            for polygon_id in removed_polygon_ids:
                plaxis2d_input.remove_structure_string_id(self.plaxis2d_input_file, str(polygon_id), '##SOIL_POLYGON_IN_STAGE', 3)

            
    def add_soilcluster(self):
        """ Adds soil cluster
        """
        pointTL_text = self.ui.lineEdit_34.text()
        pointTR_text = self.ui.lineEdit_35.text()
        pointBL_text = self.ui.lineEdit_36.text()
        pointBR_text = self.ui.lineEdit_37.text()

        pointTL = [float(pointTL_text.split(',')[0]), float(pointTL_text.split(',')[1])]
        pointTR = [float(pointTR_text.split(',')[0]), float(pointTR_text.split(',')[1])]
        pointBL = [float(pointBL_text.split(',')[0]), float(pointBL_text.split(',')[1])]
        pointBR = [float(pointBR_text.split(',')[0]), float(pointBR_text.split(',')[1])]
        
        self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR)


    def add_soilcluster__(self, Soilclusters, Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, wall_thickness=0.0, soilmaterial=None, annotate=True, annotate_FEL=False):
        """ Adds a soil cluster (for excavation)
        wall_thickness is used only for plotting the soil cluster considering thickness of the wall
        """
        try:
            soilcluster = {}
            soilcluster['pointTL'] = pointTL 
            soilcluster['pointTR'] = pointTR 
            soilcluster['pointBL'] = pointBL 
            soilcluster['pointBR'] = pointBR
            soilcluster['isRectangular'] = True
            soilcluster['soilmaterial'] = soilmaterial
            soilcluster['annotate'] = annotate  # save annotation state for loading
            soilcluster['annotate_FEL'] = annotate_FEL  # save annotation state for loading
            
            soilcluster['id'] = randint(100000, 999999)
            
            Soilclusters.append(soilcluster)
            Soilclusters_notdried.append(soilcluster)
            
            soilcluster_pathpatches = self.plot_canvas.plot_soilcluster(soilcluster, wall_thickness, annotate=annotate, annotate_FEL=annotate_FEL)
            soilcluster['pathpatches'] = soilcluster_pathpatches
            
            plaxis2d_input.add_soilcluster(self.plaxis2d_input_file, 'g_i', soilcluster)
            #print('A soil rectangle is added, top = {0}, bottom = {1}'.format(pointTL[1], pointTR[1]))
            
            # Suggest values for the next soilcluster
            self.ui.lineEdit_34.setText(str(soilcluster['pointBL'][0]) + ', ' + str(soilcluster['pointBL'][1]))
            self.ui.lineEdit_35.setText(str(soilcluster['pointBR'][0]) + ', ' + str(soilcluster['pointBR'][1]))
            self.ui.lineEdit_36.setText(str(soilcluster['pointBL'][0]) + ', ' + str(soilcluster['pointBL'][1] - 3))
            self.ui.lineEdit_37.setText(str(soilcluster['pointBR'][0]) + ', ' + str(soilcluster['pointBR'][1] - 3))
            
            # Suggest values for the water level
            self.ui.lineEdit_38.setText(str(soilcluster['pointBL'][0] + 2) + ', ' + str(soilcluster['pointBL'][1] - 0.5))
            self.ui.lineEdit_39.setText(str(soilcluster['pointBR'][0] + 2) + ', ' + str(soilcluster['pointBR'][1] - 0.5))

            # show soilclusters on table
            self.plaxman_x.display_soilclusters_on_table(self.Soilclusters)
            
            return soilcluster['id']

                     
        except (ValueError, IndexError) as e:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')
            

    def remove_soilcluster(self):
        """ Removes soil cluster(s)
        """
        if len(self.Soilclusters) > 0: 
            removed_soilcluster_ids = self.remove_structure(self.Soilclusters, 'Soil cluster selection for removal', '##SOIL_CLUSTER', 6)  
            
            # update the remained soilclusters
            if self.Soilclusters_notdried:
                for soilcluster_id in removed_soilcluster_ids:
                    deleted_item = [item for item in self.Soilclusters_notdried if item['id'] == soilcluster_id][0]
                    deleted_item_idx = self.Soilclusters_notdried.index(deleted_item)
                    #print(deleted_item_idx)            
                    self.Soilclusters_notdried.pop(deleted_item_idx) 

            # show soilclusters on table
            self.plaxman_x.display_soilclusters_on_table(self.Soilclusters)


    def plot_final_excavation_level(self, level, x_min, x_wall):
        """ Plots final excavation level (used in Optiman)
        """
        pathpatch = self.plot_canvas.plot_final_excavation_level(level, x_min, x_wall)

        return pathpatch

        
    def add_waterlevel(self):
        """ Add a user water level
        """
        try:
            pointL_text = self.ui.lineEdit_38.text()
            pointR_text = self.ui.lineEdit_39.text()
            pointL = (float(pointL_text.split(',')[0]), float(pointL_text.split(',')[1]))
            pointR = (float(pointR_text.split(',')[0]), float(pointR_text.split(',')[1]))

            self.add_waterlevel__(pointL, pointR)
            
        except (ValueError, IndexError) as e:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')


    def add_waterlevel__(self, pointL, pointR):
            waterlevel = {}
            waterlevel['pointL'] = pointL
            waterlevel['pointR'] = pointR
            waterlevel['id'] = randint(100000, 999999)
            
            self.Waterlevels.append(waterlevel)
            
            waterlevel_pathpatches = self.plot_canvas.plot_waterlevel(waterlevel)
            waterlevel['pathpatches'] = waterlevel_pathpatches
            
            plaxis2d_input.add_waterlevel(self.plaxis2d_input_file, 'g_i', waterlevel)

            # show all water levels on table
            self.plaxman_x.display_waterlevels_on_table(self.Waterlevels)

            print('User water level is added')
            
            self.ui.comboBox_13.addItem(str(waterlevel['id']))


    def remove_waterlevel(self): 
        """ Remove user water level(s)
        """
        if len(self.Waterlevels) > 0:
            removed_water_ids = self.remove_structure(self.Waterlevels, 'Water level selection for removal', '##WATER_LEVEL', 2)  
            
            # Remove water ids in phases
            for water_id in removed_water_ids:
                self.remove_comboBoxItem(self.ui.comboBox_13, str(water_id))
        
            # show all water levels on table
            self.plaxman_x.display_waterlevels_on_table(self.Waterlevels)


    def add_drain(self):
        """ Add a drain (there is only 1 drain)
        """
        try:
            drain = {}
            pointL_text = self.ui.lineEdit_40.text()
            pointR_text = self.ui.lineEdit_41.text()
            point_wallfoot_text = self.ui.lineEdit_10.text()
            drain['pointL'] = (float(pointL_text.split(',')[0]), float(pointL_text.split(',')[1]))
            drain['pointR'] = (float(pointR_text.split(',')[0]), float(pointR_text.split(',')[1]))
            drain['wallfoot'] = (float(point_wallfoot_text.split(',')[0]), float(point_wallfoot_text.split(',')[1]))
            drain['islefthalfmodel'] = (self.ui.checkBox_4.checkState() == 2)
            
            drain['id'] = randint(100000, 999999)
            
            
            wall_length = abs(self.Walls[-1]['point1'][1] - self.Walls[-1]['point2'][1])    # wall_length for plotting
            drain['wall_length'] = wall_length
            self.Drain = dict(drain)
            drain_pathpatches = self.plot_canvas.plot_drain(drain)
            self.Drain['pathpatches'] = drain_pathpatches
            
            plaxis2d_input.add_drain(self.plaxis2d_input_file, 'g_i', drain)

            print('Drain is added')
                        
        except (ValueError, IndexError) as e:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')
    

    def remove_drain(self):
        """ Remove the drain
        """
        if self.Drain:
            plaxis2d_input.remove_structure(self.plaxis2d_input_file, self.Drain['id'], '##DRAIN', 9)
            self.plot_canvas.undo_plot_pathpatches(self.Drain['pathpatches'])
            
            self.Drain.clear()

                          
    def select_struts(self):
        """ Select struts (to activate)
        """
        if len(self.Struts) > 0:
            self.dialog.open_remove_structure_selection(self.Struts, 'Strut selection for phased calculation')
            element_ids = self.dialog.removed_ids
                    
            self.new_phase['strut_ids'] = element_ids
            
        else:
            self.dialog.show_message_box('Warning', 'There is no strut to select!')
            
    
    def select_anchors(self): 
        """ Select anchors (to activate)
        """
        if len(self.Anchors) > 0:
            self.dialog.open_remove_structure_selection(self.Anchors, 'Ground anchor selection for phased calculation')
            element_ids = self.dialog.removed_ids
                    
            self.new_phase['anchor_ids'] = element_ids
                          
        else:
            self.dialog.show_message_box('Warning', 'There is no ground anchor to select!')
    
    def select_soilclusters(self):
        """ Select soil clusters (to deactivate)
        """
        if len(self.Soilclusters) > 0:
            self.dialog.open_remove_structure_selection(self.Soilclusters, 'Soil cluster selection for phased calculation')
            element_ids = self.dialog.removed_ids
                    
            self.new_phase['soilcluster_ids'] = element_ids
                          
        else:
            self.dialog.show_message_box('Warning', 'There is no soil cluster to select!')

    def waterlevel_select_soilclusters(self):
        """ Select soil clusters to which a user water level is assigned 
        """
        if len(self.Soilclusters) > 0:
            self.dialog.open_remove_structure_selection(self.Soilclusters, 'Soil cluster selection for assigning user water level')
            element_ids = self.dialog.removed_ids
                    
            self.new_phase['waterlevel_soilcluster_ids'] = element_ids
                          
        else:
            self.dialog.show_message_box('Warning', 'There is no soil cluster to select!')

    
    def apply_mesh(self):
        """ Apply mesh properties
        """
        element_dist_text = self.ui.comboBox_9.currentText()
        is_enhanced_refinement = (self.ui.checkBox_3.checkState() == 2)
        
        element_dist = 0.06
        if element_dist_text == 'Coarse':
            element_dist = 0.08
        elif element_dist_text == 'Medium':
            element_dist = 0.06
        elif element_dist_text == 'Fine':
            element_dist = 0.04

        self.mesh['element_dist'] = element_dist
        self.mesh['is_enhanced_refinement'] = is_enhanced_refinement

        plaxis2d_input.apply_mesh(self.plaxis2d_input_file, 'g_i', self.mesh)
        
        for lineload in self.Lineloads:
            self.plot_canvas.set_grey_pathpatches(lineload['pathpatches'])
        for pointload in self.Pointloads:
            self.plot_canvas.set_grey_pathpatches(pointload['pathpatches'])
        for anchor in self.Anchors:
            self.plot_canvas.set_grey_pathpatches(anchor['pathpatches'])
        for strut in self.Struts:
            self.plot_canvas.set_grey_pathpatches(strut['pathpatches'])
        for wall in self.Walls:
            self.plot_canvas.set_grey_pathpatches(wall['pathpatches'])
        
        print(element_dist_text + ' mesh is applied')


    def update_phase_table(self, Phases):
        """ Updates the table of phases
        """
        #column_items = sorted(list(self.Phases[0].keys()))
        column_items = ['phase_id', 'phase_name', 'deform_calc_type', 'pore_pres_calc_type', 'loading_type', 'time_interval', 'water_level_id']
        row_number = len(Phases)
        column_number = len(column_items)
        self.ui.tableWidget_2.setRowCount(row_number)
        self.ui.tableWidget_2.setColumnCount(column_number)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(column_items)
        for i in range(len(Phases)):
            for j in range(len(column_items)):
                self.ui.tableWidget_2.setItem(i, j,  QtWidgets.QTableWidgetItem(str(Phases[i][column_items[j]])))
            #self.ui.tableWidget_2.setCellWidget(i, len(column_items) - 1, QtWidgets.QCheckBox('Select item?'))

    def remove_phase(self):    
        """ Remove the last calculation phase
        """
        if len(self.Phases) > 0:
            deleted_phase = self.Phases.pop()   
            
            self.update_phase_table(self.Phases)
            
            plaxis2d_input.remove_structure_inbetween(self.plaxis2d_input_file, deleted_phase['phase_id'], '##PHASE', '##END_OF_PHASE')

            # undo assigning colors of the previously added phase
            if 'pathpatches' in deleted_phase:
                for group_i, pathpathgroup in enumerate(deleted_phase['pathpatches']):
                    #[print(color) for color in deleted_phase['pathpatch_colors'][group_i]]
                    self.plot_canvas.set_colors(pathpathgroup, deleted_phase['pathpatch_colors'][group_i])

            self.ui.comboBox_31.removeItem(len(self.Phases)) # in Plaxman
            self.ui.comboBox_21.removeItem(len(self.Phases)) # in Backman
            #self.ui.comboBox_26.removeItem(len(self.Phases)) # in Sensiman

            # reset the dry soilclusters, if phase is of dewatering type
            if deleted_phase['phase_name'][:10] == 'Dewatering':
                #print(deleted_phase['phase_name'][:10])
                #print(self.Soilclusters_notdried)
                #print('\n')
                if 'setdry_soilcluster_ids' in deleted_phase:
                    for drysoilcluster_id in deleted_phase['setdry_soilcluster_ids']:
                        for soilcluster in self.Soilclusters:
                            if drysoilcluster_id == soilcluster['id']:
                                self.Soilclusters_notdried.append(soilcluster)
                    #print(self.Soilclusters_notdried)

            print('The last phase is removed, {} phases remain'.format(len(self.Phases)))


    def remove_all_phases(self):
        """ Removes all calculation phases
        """
        while len(self.Phases) > 0:
            self.remove_phase()
        
                        
    def add_predefined_phase(self):
        """ Adds a predefined calculation phase in 'Staged construction' of tab 'Phases'
        This method is called upon user pressing on 'Addd phase'.
        """
        phasename = self.ui.comboBox_10.currentText()
        reset_displ_zero = (self.ui.checkBox_5.checkState() == 2)
        deform_calc_type = self.ui.comboBox_11.currentText()
        loading_type = self.ui.comboBox_43.currentText()
        pore_pres_calc_type = self.ui.comboBox_12.currentText()
        time_interval = self.ui.lineEdit_84.text()
        if phasename == 'Wall construction':
            self.add_phase_wall_construction(self.Phases, self.Walls, self.Lineloads, self.Pointloads, self.Anchors, self.Struts, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)

        elif phasename == 'Excavation':
            if len(self.Phases) < 1:
                self.dialog.show_message_box('Warning', "Please add 'Wall construction' phase first!")
                return
            
            elif 'soilcluster_ids' not in self.new_phase.keys():
                self.dialog.show_message_box('Warning', "Please select soil cluster(s) to deactivate!")
                return
            else:
                self.add_phase_excavation(self.Phases, self.Soilclusters, self.new_phase['soilcluster_ids'], None, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)

        elif phasename == 'Anchoring':
            if len(self.Phases) < 1:
                self.dialog.show_message_box('Warning', "Please add 'Wall construction' phase first!")
                return
            elif 'anchor_ids' not in self.new_phase.keys():
                self.dialog.show_message_box('Warning', "Please select ground anchor(s) to activate!")
                return
            else:
                F_prestress = [anchor['F_prestress'] for anchor in self.Anchors if anchor['id'] in self.new_phase['anchor_ids']]
                self.add_phase_anchoring(self.Phases, self.Anchors, self.new_phase['anchor_ids'], F_prestress, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)

        elif phasename == 'Strut construction':
            if len(self.Phases) < 1:
                self.dialog.show_message_box('Warning', "Please add 'Wall construction' phase first!")
                return
            elif 'strut_ids' not in self.new_phase.keys():
                self.dialog.show_message_box('Warning', "Please select strut(s) to activate!")
            else:
                F_prestress = [strut['F_prestress'] for strut in self.Struts if strut['id'] in self.new_phase['strut_ids']]
                self.add_phase_struting(self.Phases, self.Struts, self.new_phase['strut_ids'], F_prestress, reset_displ_zero, False, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)

        elif phasename == 'Dewatering (lowering water level)':
            if len(self.Phases) < 1:
                self.dialog.show_message_box('Warning', "Please add 'Wall construction' phase first!")
                return
            elif 'waterlevel_soilcluster_ids' not in self.new_phase.keys():
                self.dialog.show_message_box('Warning', "Please select soil cluster(s) to which user water level is assigned!")
                return
            else:
                waterlevel_id = self.ui.comboBox_13.currentText()
                self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, waterlevel_id, self.new_phase['waterlevel_soilcluster_ids'],None, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)

        elif phasename == 'Dewatering (lowering drain head)':
            if len(self.Phases) < 1:
                self.dialog.show_message_box('Warning', "Please add 'Wall construction' phase first!")
                return
            elif not self.Drain:
                self.dialog.show_message_box('Warning', "Please add drain first!")
                return
            else:
                drain_head = float(self.ui.lineEdit_8.text())
                self.add_phase_dewatering_drain(self.Phases, self.Soilclusters_notdried, drain_head, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        
        # update phase table
        self.update_phase_table(self.Phases)


    def add_phase_wall_construction(self, Phases, Walls, Lineloads, Pointloads, Anchors, Struts, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds an excavation phase by deactivating the soil clusters whose ids are in soilcluster_ids
        """
        self.add_phase_wall_construction__(Phases, Walls, Lineloads, Pointloads, Anchors, Struts, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        print('{0} phase is created'.format(Phases[-1]['phase_name']))
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman


    def add_phase_wall_construction__(self, Phases, Walls, Lineloads, Pointloads, Anchors, Struts, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        """ Adds an excavation phase by deactivating the soil clusters whose ids are in soilcluster_ids
        """
        phasename = 'Wall construction'
        new_phase = {}
        new_phase['soilcluster_ids'] = None
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['water_level_id'] = None

        self.set_structures_grey(Lineloads, Pointloads, Anchors, Struts, Walls)   # mainly for setting structures grey for better visualization
        new_phase['water_level_id'] = None
        plaxis2d_input.add_phase_wall_construction(self.plaxis2d_input_file, 'g_i', new_phase)
            
        for lineload in Lineloads:
            new_phase['pathpatches'].append(lineload['pathpatches'])
            new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in lineload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
            self.plot_canvas.set_color(lineload['pathpatches'], 'blue')
        for pointload in Pointloads:
            new_phase['pathpatches'].append(pointload['pathpatches'])
            #new_phase['pathpatch_colors'].append(tuple(pointload['pathpatches'].get_facecolor()))
            new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in pointload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
            self.plot_canvas.set_color(pointload['pathpatches'], 'blue')
        for wall in Walls:
            new_phase['pathpatches'].append(wall['pathpatches'])
            #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in wall['pathpatches']))
            new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() if pathpatch_i is not None else None for pathpatch_i in wall['pathpatches'][:-2]))
            #[print(pathpatch_i.get_facecolor()) for pathpatch_i in wall['pathpatches']]
            self.plot_canvas.set_color(wall['pathpatches'][0], wall['color'][0])
            self.plot_canvas.set_color(wall['pathpatches'][1], wall['color'][1])
            self.plot_canvas.set_color(wall['pathpatches'][2], wall['color'][2])
            self.plot_canvas.set_color(wall['pathpatches'][3], wall['color'][3]) # annotation

        Phases.append(dict(new_phase))


    def add_phase_excavation(self, Phases, Soilclusters, soilcluster_ids, delta_support_to_ground=None, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds an excavation phase by deactivating the soil clusters whose ids are in soilcluster_ids
        """
        self.add_phase_excavation__(Phases, Soilclusters, soilcluster_ids, delta_support_to_ground, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        print('{0} phase until {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['soilcluster_bottom']))
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman


    def add_phase_excavation__(self, Phases, Soilclusters, soilcluster_ids, delta_support_to_ground=None, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        """ Adds an excavation phase by deactivating the soil clusters whose ids are in soilcluster_ids
        """
        phasename = 'Excavation'
        new_phase = {}
        new_phase['soilcluster_ids'] = soilcluster_ids
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['water_level_id'] = None
        new_phase['delta_support-excavation'] = delta_support_to_ground
        new_phase['soilcluster_bottom'] = None
        previous_phase = Phases[-1]

        plaxis2d_input.add_phase_excavation(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
                
        soilcluster = Soilclusters[0]
        soilcluster_last = Soilclusters[0]  # the last soilcluster to be excavated in this excavation phase
        for soilcluster in Soilclusters:
            if soilcluster['id'] in new_phase['soilcluster_ids']:
                new_phase['pathpatches'].append(soilcluster['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in soilcluster['pathpatches'][:-2]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                self.plot_canvas.set_color_excavated_soilcluster(soilcluster['pathpatches'])
                soilcluster_last = soilcluster

        soilcluster_bottom = None
        if 'points' not in soilcluster_last:    # rectangular soilcluster
            soilcluster_bottom = min(soilcluster_last['pointBL'][1], soilcluster_last['pointBR'][1])
        else:   # multi-point soilcluster
            soilcluster_bottom = min(point[1] for point in soilcluster_last['points'])
        
        new_phase['soilcluster_bottom'] = soilcluster_bottom

        Phases.append(dict(new_phase))


    def add_phase_anchoring(self, Phases, Anchors, anchor_ids, F_prestress, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds an anchoring phase
        """
        try:
            self.add_phase_anchoring__(Phases, Anchors, anchor_ids, F_prestress, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
            self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
            self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
            print('{0} phase at level {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['anchor_level']))

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if prestressed force is correctly entered!')
            return



    def add_phase_anchoring__(self, Phases, Anchors, anchor_ids, F_prestress, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        """ Adds an anchoring phase
        """
        phasename = 'Anchoring'
        new_phase = {}
        new_phase['anchor_ids'] = anchor_ids 
        new_phase['soilcluster_ids'] = None
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['water_level_id'] = None
        previous_phase = Phases[-1]
        new_phase['F_prestress'] = F_prestress
        new_phase['anchor_level'] = None
                    
        previous_phase = Phases[-1]
        plaxis2d_input.add_phase_anchoring(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
                    
        for anchor in Anchors:
            if anchor['id'] in new_phase['anchor_ids']:
                new_phase['pathpatches'].append(anchor['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple((anchor['pathpatches'][0].get_facecolor(), anchor['pathpatches'][1].get_facecolor())))
                self.plot_canvas.set_color(anchor['pathpatches'][0], 'black')
                self.plot_canvas.set_color(anchor['pathpatches'][1], 'magenta')
                self.plot_canvas.set_color(anchor['pathpatches'][2], 'black') # annotation
                anchor_level = anchor['position'][1]
                new_phase['anchor_level'] = anchor_level

        Phases.append(dict(new_phase))



    def add_phase_struting(self, Phases, Struts, strut_ids, F_prestress, reset_displ_zero=False, deconstruct=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds a struting phase
        """
        self.add_phase_struting__(Phases, Struts, strut_ids, F_prestress, reset_displ_zero, deconstruct, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
        print('{0} phase at level {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['strut_level']))


    def add_phase_struting__(self, Phases, Struts, strut_ids, F_prestress, reset_displ_zero=False, deconstruct=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        """ Adds a struting phase
        """
        #phasename = 'Strut construction'
        new_phase = {}
        new_phase['strut_ids'] = strut_ids 
        new_phase['soilcluster_ids'] = None
        new_phase['phase_id'] = randint(100000, 999999)
        #new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['strut_level'] = None
        new_phase['F_prestress'] = F_prestress
        #previous_phase = Phases[-1]
                    
        previous_phase = Phases[-1]

        # Coonstruction
        if not deconstruct:
            new_phase['phase_name'] = 'Strut/slab construction'
            plaxis2d_input.add_phase_strut_construction(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
            for strut in Struts:
                if strut['id'] in new_phase['strut_ids']:
                    new_phase['pathpatches'].append(strut['pathpatches'])
                    new_phase['pathpatch_colors'].append(tuple((strut['pathpatches'][0].get_facecolor(), strut['pathpatches'][1].get_facecolor())))
                    if strut['usage'] == 'Strut':
                        self.plot_canvas.set_color(strut['pathpatches'][0], 'black')
                        self.plot_canvas.set_color(strut['pathpatches'][1], 'black')
                        self.plot_canvas.set_color(strut['pathpatches'][2], 'black') # annotation
                    else:   # orange color for slabs
                        self.plot_canvas.set_color(strut['pathpatches'][0], 'orange')
                        self.plot_canvas.set_color(strut['pathpatches'][1], 'orange')
                        self.plot_canvas.set_color(strut['pathpatches'][2], 'black') # annotation
                    strut_level = strut['position'][1]
                    new_phase['strut_level'] = strut_level

        else:   # Deconstruction
            new_phase['phase_name'] = 'Strut deconstruction'
            plaxis2d_input.add_phase_strut_deconstruction(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
            for strut in Struts:
                if strut['id'] in new_phase['strut_ids']:
                    new_phase['pathpatches'].append(strut['pathpatches'])
                    new_phase['pathpatch_colors'].append(tuple((strut['pathpatches'][0].get_facecolor(), strut['pathpatches'][1].get_facecolor())))
                    self.plot_canvas.set_color(strut['pathpatches'][0], 'grey')
                    self.plot_canvas.set_color(strut['pathpatches'][1], 'grey')
                    strut_level = strut['position'][1]
                    new_phase['strut_level'] = strut_level

        Phases.append(dict(new_phase))


    def add_phase_dewatering(self, Phases, Waterlevels, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation=None, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds a dewatering phase
        """
        self.add_phase_dewatering__(Phases, Waterlevels, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
        print('{0} phase until level {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['y_ref']))


    def add_phase_dewatering__(self, Phases, Waterlevels, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        """ Adds a dewatering phase
        """
        phasename = 'Dewatering (lowering water level)'
        new_phase = {}
        #new_phase['soilcluster_ids'] = soilcluster_ids
        new_phase['waterlevel_soilcluster_ids'] = soilcluster_ids
        new_phase['water_level_id'] = waterlevel_id
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['y_ref'] = None
        #new_phase['delta_ground-water'] = delta_ground_to_water

        y_ref = None
        for waterlevel in Waterlevels:
            if waterlevel['id'] == int(new_phase['water_level_id']):
                y_ref = waterlevel['pointL'][1]
        new_phase['y_ref'] = y_ref
                
        setdry_soilcluster_ids = []
        for soilcluster in Soilclusters_notdried:
            if soilcluster['pointTR'] is not None:   # rectangular soil cluster
                if (soilcluster['pointBL'][1] > y_ref) and (soilcluster['pointBR'][1] > y_ref):
                    setdry_soilcluster_ids.append(soilcluster['id'])
            elif 'points' in soilcluster:   # muti-point soil cluster (for berms)
                y_min = min([point[1] for point in soilcluster['points']])
                if y_min > y_ref:
                    setdry_soilcluster_ids.append(soilcluster['id'])
        new_phase['setdry_soilcluster_ids'] = setdry_soilcluster_ids # add this back to self.Soilclusters_notdried in 'remove_phase'
        new_phase['soilcluster_ids_porepressure_interpolation'] = soilcluster_ids_porepressure_interpolation
                
        previous_phase = Phases[-1]
        if new_phase['soilcluster_ids_porepressure_interpolation'] is not None:
            plaxis2d_input.add_phase_dewatering1_porepressure_interpolation(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
        else:
            plaxis2d_input.add_phase_dewatering1(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
                
        # remove the soilclusters in self.Soilclusters_notdried that have not been dried
        for soilcluster_id in setdry_soilcluster_ids:
            deleted_item = [item for item in Soilclusters_notdried if item['id'] == soilcluster_id][0]
            deleted_item_idx = Soilclusters_notdried.index(deleted_item)
            #print(deleted_item_idx)            
            Soilclusters_notdried.pop(deleted_item_idx)                     
        #print(self.Soilclusters_notdried)

        Phases.append(dict(new_phase))


    def add_phase_dewatering_drain(self, Phases, Soilclusters_notdried, drain_head, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Phreatic', time_interval=0):
        """ Adds a dewatering phase by lowering drain head
        """
        try:
            self.add_phase_dewatering_drain__(Phases, Soilclusters_notdried, drain_head, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
            self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
            self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
            print('{0} phase until level {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['drain_head']))

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if drain head is correctly entered!')
            return


    def add_phase_dewatering_drain__(self, Phases, Soilclusters_notdried, drain_head, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Phreatic', TimeInterval=0):
        phasename = 'Dewatering (lowering drain head)'
        new_phase = {}
        #new_phase['soilcluster_ids'] = soilcluster_ids
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['drain_head'] = drain_head

        # select soilclusters above drain_head for automatically setting dry
        setdry_soilcluster_ids = []
        for soilcluster in Soilclusters_notdried:
        #for soilcluster in self.Soilclusters:
            if (soilcluster['pointBL'][1] > drain_head) and (soilcluster['pointBR'][1] > drain_head):
                setdry_soilcluster_ids.append(soilcluster['id'])
        #print(setdry_soilcluster_ids)
        new_phase['setdry_soilcluster_ids'] = setdry_soilcluster_ids # add this back to self.Soilclusters_notdried in 'remove_phase'
        previous_phase = self.Phases[-1]
        plaxis2d_input.add_phase_dewatering2(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase, self.Drain['id'])
                    
        # remove the soilclusters in self.Soilclusters_notdried that have not been dried
        for soilcluster_id in setdry_soilcluster_ids:
            deleted_item = [item for item in Soilclusters_notdried if item['id'] == soilcluster_id][0]
            deleted_item_idx = self.Soilclusters_notdried.index(deleted_item)
            #print(deleted_item_idx)            
            Soilclusters_notdried.pop(deleted_item_idx)                     
        #print(self.Soilclusters_notdried)

        Phases.append(dict(new_phase))

                    
    def set_structures_grey(self, Lineloads, Pointloads, Anchors, Struts, Walls):
        """ Set structures grey for visualizing phase constructions
        """
        for lineload in Lineloads:
            self.plot_canvas.set_grey_pathpatches(lineload['pathpatches'])
        for pointload in Pointloads:
            self.plot_canvas.set_grey_pathpatches(pointload['pathpatches'])
        for anchor in Anchors:
            self.plot_canvas.set_grey_pathpatches(anchor['pathpatches'])
        for strut in Struts:
            self.plot_canvas.set_grey_pathpatches(strut['pathpatches'])
        for wall in Walls:
            self.plot_canvas.set_grey_pathpatches(wall['pathpatches'])


    def calculate(self):
        """ Executes PLAXIS2D for calculating the Python script of the model
        """
        try:
            print('\nLaunched PLAXIS2D INPUT for calculation...')

            # take away code for termination of Plaxis2D Input
            plaxis2d_input.remove_termination(self.plaxis2d_input_file)

            self.model = Evaluate_Plaxis2DModel()
            #self.model.run()    # for debugging
            self.run_thread = RunThreadSingle(workflow=self.model)
            self.run_thread.start()

            # bring back code for termination of Plaxis2D Input after calculation is finised
            self.run_thread.isDone.connect(self.add_termination)
        
            #self.ui.spinBox.setMininum(1)
            self.ui.spinBox.setMaximum(len(self.Phases))
            self.ui.pushButton_38.setEnabled(True)
            #self.ui.spinBox_2.setMininum(1)
            self.ui.spinBox_2.setMaximum(len(self.Phases))
            self.ui.pushButton_39.setEnabled(True)

        except Exception as e:
            write_traceback_to_file(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])))
        

    def add_termination(self):
        """ Adds code lines for termination of Plaxis2D Input
        """
        time.sleep(1.0) # wait one second
        plaxis2d_input.add_termination(self.plaxis2d_input_file)


    def calculate_obs(self):
        """ Executes PLAXIS2D for calculating the Python script of the model
        and gets/ saves requested observation data
        """ 
        try:
            print('\nLaunched PLAXIS2D INPUT for calculation...')

            # take away code for termination of Plaxis2D Input
            plaxis2d_input.remove_termination(self.plaxis2d_input_file)

            path_output = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'measurement')
            if not os.path.exists(path_output):
                    os.makedirs(path_output)

            self.model = Evaluate_Plaxis2DModel(self.Points_obs, path_output)
            #self.model.run()
            self.run_thread = RunThreadSingle(workflow=self.model)
            self.run_thread.start()
            self.run_thread.isDone.connect(lambda: self.report_calculate_obs(path_output))

            # bring back code for termination of Plaxis2D Input after calculation is finised
            self.run_thread.isDone.connect(self.add_termination)

        except Exception as e:
            write_traceback_to_file(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])))


    def report_calculate_obs(self, path_output):
        """ Prints message after model run is finished
        """
        if self.run_thread.isDone:
            print('Synthetic data is stored in {}'.format(path_output))
            self.ui.spinBox.setMaximum(len(self.Phases))
            self.ui.spinBox_2.setMaximum(len(self.Phases))



    def merge_observation_points(self, Points_obs):
        """ Merge sets of observation points
        """
        pnt_obs = []
        for points in Points_obs:
            pnt_obs.append(points['points'])

        pnt_obs_flat = [item for sublist in pnt_obs for item in sublist]

        return pnt_obs_flat


    def add_observed_points(self):
        """ Add observed points (for sensitivity and back-analysis)
        """
        try:
            points_new = {}
            num_points = int(self.ui.lineEdit_46.text())
            point1_text = self.ui.lineEdit_44.text()
            point2_text = self.ui.lineEdit_45.text()
            point1 = (float(point1_text.split(',')[0]), float(point1_text.split(',')[1]))
            point2 = (float(point2_text.split(',')[0]), float(point2_text.split(',')[1]))

            points = list(zip(np.linspace(point1[0], point2[0], num_points), np.linspace(point1[1], point2[1], num_points)))

            points_new['points'] = points
            points_new['num_points'] = num_points
            points_new['point1'] = point1
            points_new['point2'] = point2
            points_new['id'] = randint(100000, 999999)
            points_new['obs_phase'] = self.ui.comboBox_31.currentIndex() + 1
            points_new['obs_type'] = self.ui.comboBox_30.currentText()
            points_new['data'] = None

            # adjust points for anchor force at anchor positions
            if points_new['obs_type'] == 'AnchorForce':
                points_new['points'].clear()
                for anchor in self.Anchors:
                    points_new['points'].append(anchor['position'])
                points_new['num_points'] = len(points_new['points'])
            
            points_new['pathpatches'] = self.plot_canvas.plot_points(points_new['points'], 'red')

            self.Points_obs.append(points_new)

            plaxis2d_input.add_observed_points(self.plaxis2d_input_file, 'g_i', points_new)

            self.update_observed_points_table()

            #self.ui.comboBox_23.addItem('Obs. set ' + str(len(self.Points_obs)))    # in Backman
            #self.ui.comboBox_27.addItem('Obs. set ' + str(len(self.Points_obs)))    # in Sensiman


        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values for points are correctly entered!')


    def load_observed_points(self):
        """ Loads observed points (for sensitivity and back-analysis).
        Text file to load is xy coordinates of the observed points
        """
        try:
            points_new = {}
            points_new['obs_phase'] = self.ui.comboBox_31.currentIndex() + 1
            points_new['obs_type'] = self.ui.comboBox_30.currentText()
            points_new['id'] = randint(100000, 999999)

            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
            data_file, _ = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(), 'Select data file', MONIMAN_OUTPUTS)

            if data_file:
                points = np.loadtxt(data_file.replace('/','\\'))
                points_new['points'] = list(map(tuple, points)) # numpy array to list of tuples
                points_new['num_points'] = len(points_new['points'])

                points_new['pathpatches'] = self.plot_canvas.plot_points(points_new['points'], 'red')

                self.Points_obs.append(points_new)

                plaxis2d_input.add_observed_points(self.plaxis2d_input_file, 'g_i', points_new)

                self.update_observed_points_table()
            
        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values for points are correctly entered!')

            
    def update_observed_points_table(self):
        """ Update table of observation points
        """
        self.ui.tableWidget_6.setRowCount(len(self.Points_obs))
        if len(self.Points_obs) == 0:
            self.ui.tableWidget_6.setColumnCount(0)
            self.ui.tableWidget_6.setRowCount(0)
        else:
            max_column = max([item['num_points'] for item in self.Points_obs])
            self.ui.tableWidget_6.setColumnCount(max_column)
            points_label = ['P' + str(pntnumber + 1) for pntnumber in range(max_column)]
            self.ui.tableWidget_6.setHorizontalHeaderLabels(points_label)

        labels = []
        for (i, points_set) in enumerate(self.Points_obs):
            label = 'Obs. set {0}: Type {1}, Phase {2}'.format(i+1, points_set['obs_type'], points_set['obs_phase'])
            labels.append(label)
            for (j, pnt) in enumerate(points_set['points']):
                self.ui.tableWidget_6.setItem(i, j, QtWidgets.QTableWidgetItem(str(pnt[0]) + ', ' + str(pnt[1])))

        if labels:
            self.ui.tableWidget_6.setVerticalHeaderLabels(labels)


    def remove_observed_points(self):
        """ Remove a set of observed points
        """
        if len(self.Points_obs) > 0:
            removed_points = self.Points_obs.pop()
            self.plot_canvas.undo_plot_pathpatches(removed_points['pathpatches'])

            plaxis2d_input.remove_structure(self.plaxis2d_input_file, removed_points['id'], '##POINTS_OBS', 4)

            self.update_observed_points_table()

            #self.ui.comboBox_23.removeItem(len(self.Points_obs))    # in Backman
            #self.ui.comboBox_27.removeItem(len(self.Points_obs))    # in Sensiman

    
    def view_wall_outputs(self):
        """ Views wall deflection and internal forces
        """
        output_database = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.p2dx')
        
        if not exists(output_database):
            self.dialog.show_message_box('Warning', 'PLAXIS2D database file does not exist. Make sure that PLAXIS2D simulation has been finished!')
            
        elif len(self.Walls) < 1:
            self.dialog.show_message_box('Warning', 'Please make sure that at least one wall is defined!')
        else:
            wall_id = int(self.ui.comboBox_14.currentText())
            point1 = None
            for wall in self.Walls:
                if wall['id'] == wall_id:
                    point1 = wall['point1']
                    #point2 = wall['point2']
            x_wall = point1[0]
            phasenumber = self.ui.spinBox.value()
            
            PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
            subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)

            
            s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
                        
            s_o.open(output_database)
            
            print('\nLaunched PLAXIS2D OUTPUT...')
            print('PLAXIS2D OUTPUT database is in {}'.format(output_database))

            # open wall output window (with Anchors and Struts also)
            self.form.open_wall_outputs(subprocess_plaxis_output, sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], s_o, g_o, 
                                        output_database, x_wall, self.Walls[0], self.Anchors, self.Struts, phasenumber, len(self.Phases))


    def plot_soilsection_settlement(self):
        """ Plot settlement (uy) a long a line section in soil
        """
        output_database = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.p2dx')
        
        if not exists(output_database):
            self.dialog.show_message_box('Warning', 'PLAXIS2D database file does not exist. Make sure that PLAXIS2D simulation has been finished!')
            
        else:           
            try:
                point1_text = self.ui.lineEdit_18.text()
                point2_text = self.ui.lineEdit_20.text()
                point1 = (float(point1_text.split(',')[0]), float(point1_text.split(',')[1]))
                point2 = (float(point2_text.split(',')[0]), float(point2_text.split(',')[1]))
                phasenumber = self.ui.spinBox_2.value()
                
                scaling_factor = float(self.ui.lineEdit_26.text())
                vicinity = float(self.ui.lineEdit_30.text())
                
                PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
                subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)
    
                
                s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
                            
                s_o.open(output_database)
                
                print('Launched PLAXIS2D OUTPUT..')
                print('PLAXIS2D OUTPUT database is in {}'.format(output_database))
    
                self.form.open_soilsection_settlement(subprocess_plaxis_output, sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], s_o, g_o, 
                                        output_database, point1, point2, scaling_factor, vicinity, phasenumber, len(self.Phases))   
            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check the two points are correctly entered!')
    

    def define_soil_improvement_structure(self):
        """ Defines geometrical and material properties for a soil improvement structure
        """
        method = self.ui.comboBox_44.currentText()       
        structure_name = self.ui.lineEdit_75.text()

        if structure_name is '': # wall_name must not be empty
            self.dialog.show_message_box('Warning', "Name of soil improvement structure cannot be empty!")
        
        else:
            if method == 'Stone columns':
                sc = StoneColumns()
                sc.open_edit_Stone_columns(method, structure_name)
                if sc.name != '':
                    print('Soil improvement structure {} is defined'.format(sc.name))
                    #append SCs
                    SC_new = {}
                    SC_new['sc_params'] = sc.params
                    SC_new['sc_name'] = sc.name
                    SC_new['polygonPoints'] = []
                    SC_new['sc_p0'] = None
                    SC_new['sub_soillayers'] = []  # sub soilayers is emtpy when the SC structure is created
                    self.SCs.append(SC_new)
                    self.display_soil_improvement_structure_names_in_comboboxes()

            elif method == 'Rigid inclusions':
                ri = FDC(self.Layer_polygons, self.Boreholes[0])
                ri.open_edit_rigid_inclusions(method, structure_name)
                if ri.name != '':
                    print('Rigid inclusions structure {} is defined'.format(ri.name))
                    # append FDCs
                    FDC_new = {}
                    FDC_new['FDC_params'] = ri.FDC_params
                    FDC_new['anchorage_params'] = ri.anchorage_params
                    FDC_new['LTP_params'] = ri.LTP_params
                    FDC_new['FDC_loading'] = ri.FDC_loading # parameters for load
                    FDC_new['FDC_matrice'] = ri.matrice # calculation results
                    FDC_new['FDC_name'] = ri.name
                    top = FDC_new['FDC_params']['top'] 
                    depth = FDC_new['FDC_params']['Lc'] 
                    FDC_new['polygonPoints'] = self.set_improved_soil_polygon_FDC(top, depth, left=0.0, right=10.0)
                    FDC_new['sub_soillayers'] = []  # sub soilayers is emtpy when the FDC structure is created
                    self.FDCs.append(FDC_new)
                    self.display_soil_improvement_structure_names_in_comboboxes()


    def display_soil_improvement_structure_names_in_comboboxes(self):
        """ Displays soil improvement structure in combobox
        """
        self.ui.comboBox_45.clear()
        self.ui.comboBox_47.clear() # in Optiman
        for sc in self.SCs:
            self.ui.comboBox_45.addItem(sc['sc_name'])
            self.ui.comboBox_47.addItem(sc['sc_name'])
        for fdc in self.FDCs:
            self.ui.comboBox_45.addItem(fdc['FDC_name'])
            self.ui.comboBox_47.addItem(fdc['FDC_name'])


    def change_soil_improvement_structure_properties(self):
        """ Defines geometrical and material properties for a soil improvement structure
        """
        method = self.ui.comboBox_44.currentText()       
        structure_name = self.ui.comboBox_45.currentText()
        if '_SC' in structure_name:
            for SC in self.SCs:
                if SC['sc_name'] == structure_name:
                    sc = StoneColumns(**SC['sc_params'])
                    sc.open_edit_Stone_columns(method, structure_name, isdefined=True)
                    SC['sc_params'] = sc.params
                    SC['sc_name'] = sc.name
                    break

        elif '_FDC' in structure_name:
            for fdc in self.FDCs:
                if fdc['FDC_name'] == structure_name:
                    params = fdc['FDC_params'].copy()
                    params.update(fdc['LTP_params'])
                    params.update(fdc['FDC_loading'])
                    params.update(fdc['anchorage_params'])
                    depth_previous = fdc['FDC_params']['Lc']
                    ri = FDC(self.Layer_polygons, self.Boreholes[0], **params)
                    ri.open_edit_rigid_inclusions(method, structure_name, isdefined=True)
                    # update FDC parameters
                    fdc['FDC_params'] = ri.FDC_params
                    fdc['anchorage_params'] = ri.anchorage_params
                    fdc['LTP_params'] = ri.LTP_params
                    fdc['FDC_loading'] = ri.FDC_loading # parameters for load
                    if ri.matrice is not None:
                        fdc['FDC_matrice'] = ri.matrice # calculation results
                    fdc['FDC_name'] = ri.name
                    top = fdc['FDC_params']['top'] 
                    depth = fdc['FDC_params']['Lc'] 
                    if depth != depth_previous: # update polygonPoints only when depth is changed
                        fdc['polygonPoints'] = self.set_improved_soil_polygon_FDC(top, depth, left=0.0, right=10.0, polygonPoints_current=fdc['polygonPoints'])
                    else: # show 4 points of polygonPoints on the user interface
                        self.show_polygon_points_rectangle_FDC(fdc['polygonPoints'])
                    break
    

    def remove_soil_improvement_structure(self):
        """ Removes a soil improvement structure
        """
        structure_name = self.ui.comboBox_45.currentText()
        if '_SC' in structure_name:
            self.remove_stone_columns_structure(structure_name)

        elif '_FDC' in structure_name:
            self.remove_rigid_inclusions_structure(structure_name)


    def remove_stone_columns_structure(self, sc_name):
        """ Removes (all components) rigid inclusion
        """
        sc_to_delete_idx = 0
        for sc in self.SCs:
            if sc['sc_name'] == sc_name:
                sc_to_delete = sc
                sc_to_delete_idx = self.SCs.index(sc_to_delete)
                break

        deleted_sc = self.SCs.pop(sc_to_delete_idx)
        for poly_point in deleted_sc['polygonPoints']:
            self.plot_canvas.undo_plot_pathpatches(poly_point['pathpatch'])
            
        self.display_soil_improvement_structure_names_in_comboboxes()

        # remove sub soillayers
        self.remove_soil_improvement_soil_clusters(deleted_sc['sub_soillayers'])

        # undo refine mesh
        if 'sc_points_fine_mesh' in deleted_sc:
            self.undo_refine_mesh_around_stone_columns(deleted_sc['sc_points_fine_mesh'], deleted_sc['sc_name'])
            del deleted_sc['sc_points_fine_mesh']

        # collect the remained polygons for mesh refinement and apply them
        Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(sc['sc_name']) for sc in self.SCs if 'sc_points_fine_mesh' in sc]
        if Polygons_fine_mesh:
            plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)
        else:
            plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')


    def remove_rigid_inclusions_structure(self, ri_name):
        """ Removes (all components) rigid inclusion
        """
        fdc_to_delete_idx = 0
        for fdc in self.FDCs:
            if fdc['FDC_name'] == ri_name:
                fdc_to_delete = fdc
                fdc_to_delete_idx = self.FDCs.index(fdc_to_delete)
                break

        deleted_fdc = self.FDCs.pop(fdc_to_delete_idx)
        for poly_point in deleted_fdc['polygonPoints']:
            self.plot_canvas.undo_plot_pathpatches(poly_point['pathpatch'])
            
        self.display_soil_improvement_structure_names_in_comboboxes()

        # remove sub soillayers
        self.remove_soil_improvement_soil_clusters(deleted_fdc['sub_soillayers'])

        # undo refine mesh
        if 'sc_points_fine_mesh' in deleted_fdc:
            self.undo_refine_mesh_around_stone_columns(deleted_fdc['sc_points_fine_mesh'], deleted_fdc['FDC_name'])
            del deleted_fdc['sc_points_fine_mesh']

        # collect the remained polygons for mesh refinement and apply them
        Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(fdc['FDC_name']) for fdc in self.FDCs if 'sc_points_fine_mesh' in fdc]
        if Polygons_fine_mesh:
            plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)
        else: # remove fine mesh
            plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')


    def set_improved_soil_polygon_FDC(self, top, depth, left, right, polygonPoints_current=[]):
        """ Sets and shows improved soil polygon
        """
        #left = self.geometry[0] # x_min
        #right = left + width
        bottom = top - depth
        # update with new suggested polygon points
        points_new = [[left, top], [right, top],
                     [right, bottom], [left, bottom]]
        polygonPoints = self.update_polygon_points_rectangle_FDC(points_new, polygonPoints_current)

        return polygonPoints


    def define_soil_improvement_soil_clusters(self):
        """ Defines depth-dependent improvement factors for the soil clusters
        """
        structure_name = self.ui.comboBox_45.currentText()
        if '_SC' in structure_name:
            self.define_stone_columns_soil_clusters()

        elif '_FDC' in structure_name:
            self.define_FDC_soil_clusters()


    def define_FDC_soil_clusters(self):
        """ Defines FDC (rigid inclusion) improvement factors for stiffnesses and adapts soil strength parameters of the improved soil region
        """
        try:
            # select the user selected FDC structure
            fdc_selected = None
            structure_name = self.ui.comboBox_45.currentText()
            for fdc in self.FDCs:
                if fdc['FDC_name'] == structure_name:
                    fdc_selected = fdc
                    #fdc_selected_idx = self.FDCs.index(fdc_selected)
                    break

            if fdc_selected['FDC_matrice'] is not None:
                # read and assign user input polygon points for the selected FDC structure
                fdc_selected['polygonPoints'] = self.add_polygon_points_rectangle(fdc_selected['polygonPoints'])

                # remove previously generated soil clusters related to the slected FDC structure 
                self.remove_soil_improvement_soil_clusters(fdc_selected['sub_soillayers'])

                # open FDC SoilClusters for editing
                top_FDC = fdc_selected['FDC_params']['top']
                top_LTP = fdc_selected['FDC_params']['top'] + fdc_selected['LTP_params']['hM']
                fdc_selected['sc_thickness_sublayer'] = 2.0 # default sub soillayer thickness
                fdc_soilcluster = FDC_SoilClusters(fdc_selected['FDC_matrice'], fdc_selected['polygonPoints'], self.Layer_polygons, self.Boreholes[0], top_LTP, top_FDC, fdc_selected['FDC_name'],
                                                    thickness_sublayer=fdc_selected['sc_thickness_sublayer'])
                fdc_soilcluster.open_FDC_soil_clusters()
                top = fdc_selected['FDC_params']['top'] 
                depth = fdc_selected['FDC_params']['Lc'] 
                left = fdc_soilcluster.columns_left
                right = fdc_soilcluster.columns_right

                # update improved soil polygon the new width (left and right values)
                fdc_selected['polygonPoints'] = self.set_improved_soil_polygon_FDC(top, depth, left, right, polygonPoints_current=fdc_selected['polygonPoints'])

                # store updated sublayer thickness
                fdc_selected['sc_thickness_sublayer'] = fdc_soilcluster.thickness_sublayer

                # add LTP polygon
                polygon_LTP = self.add_polygon_fdc_LTP(top + fdc_selected['LTP_params']['hM'] , top, fdc_soilcluster.columns_left, fdc_soilcluster.columns_right, fdc_selected)

                if fdc_soilcluster.sub_soillayers:
                    # add soil polygons
                    for sc_sub_soillayer in fdc_soilcluster.sub_soillayers:
                        self.add_polygon_fdc_soil_clusters_Jointed_Rock(sc_sub_soillayer, fdc_soilcluster.columns_left, fdc_soilcluster.columns_right, structure_name, fdc_selected)

                    # store sub_soillayers as a field in the selected FDC structure
                    fdc_selected['sub_soillayers'] = fdc_soilcluster.sub_soillayers
                    fdc_selected['sub_soillayers'].append(polygon_LTP) # append polygon for LTP for later removal

                    # refine mesh
                    if 'sc_points_fine_mesh' in fdc_selected:
                        self.undo_refine_mesh_around_stone_columns(fdc_selected['sc_points_fine_mesh'], fdc_selected['FDC_name'])
                    fdc_selected['sc_points_fine_mesh'] = self.refine_mesh_around_stone_columns(fdc_selected['polygonPoints'], fdc_selected['FDC_name'])
            
            # collect all polygons for mesh refinement and apply them
            Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(fdc['FDC_name']) for fdc in self.FDCs if 'sc_points_fine_mesh' in fdc_selected]
            if Polygons_fine_mesh:
                plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the point is correctly entered!') 



    def define_stone_columns_soil_clusters(self):
        """ Defines stone column improvement factors for stiffnesses and adapts soil strength parameters of the improved soil region
        """
        try:
            # select the user selected FDC structure
            SC_selected = None
            structure_name = self.ui.comboBox_45.currentText()
            for SC in self.SCs:
                if SC['sc_name'] == structure_name:
                    SC_selected = SC
                    break

            # read and assign user input polygon points for the selected FDC structure
            if 'polygonPoints' not in SC_selected:  # do not update column length from user input polygon when updating, use available SC_selected['polygonPoints'] instead
                SC_selected['polygonPoints'] = self.add_polygon_points_rectangle(SC_selected['polygonPoints'])
            elif SC_selected['polygonPoints'] == []: # update if the list is empty
                SC_selected['polygonPoints'] = self.add_polygon_points_rectangle(SC_selected['polygonPoints'])

            # remove previously generated soil clusters related to the slected FDC structure 
            self.remove_soil_improvement_soil_clusters(SC_selected['sub_soillayers'])

            if len(SC_selected['polygonPoints']) < 3:
                self.dialog.show_message_box('Warning', 'Please add points for the improved soil region!')
            elif not SC_selected['sc_params']:
                self.dialog.show_message_box('Warning', 'Please define the stone columns structure!')
            else:
                if SC_selected['sc_p0'] is None:   # soilcluster for stone columns has not been defined
                    sc_soilcluster = StoneColumnsSoilClusters(self.project_properties['project_title'], SC_selected['sc_params'], SC_selected['polygonPoints'], self.Layer_polygons, self.Boreholes[0], SC_selected['sc_name'])
                    sc_soilcluster.open_stone_columns_soil_clusters()
                else:
                    sc_soilcluster = StoneColumnsSoilClusters(self.project_properties['project_title'], SC_selected['sc_params'], SC_selected['polygonPoints'], self.Layer_polygons, self.Boreholes[0], SC_selected['sc_name'], 
                                                    p0=SC_selected['sc_p0'], unlimited_distribution=SC_selected['unlimited_distribution'], thickness_sublayer=SC_selected['sc_thickness_sublayer'], limit_depth=SC_selected['limit_depth'],
                                                    user_input_E_s=SC_selected['user_input_E_s'], should_consider_p0=SC_selected['should_consider_p0'])
                    sc_soilcluster.open_stone_columns_soil_clusters()

                # store current surcharge and layer thickness
                SC_selected['sc_p0'] = sc_soilcluster.p0
                SC_selected['sc_thickness_sublayer'] = sc_soilcluster.thickness_sublayer
                SC_selected['user_input_E_s'] = sc_soilcluster.user_input_E_s
                SC_selected['should_consider_p0'] = sc_soilcluster.should_consider_p0
                SC_selected['limit_depth'] = sc_soilcluster.limit_depth
                SC_selected['unlimited_distribution'] = sc_soilcluster.unlimited_distribution

                if sc_soilcluster.sub_soillayers:
                    #sc_soilcluster_ids = [sc_soilcluster['id'] for sc_soilcluster in self.sc_soilcluster.sub_soillayers]
                    #print(sc_soilcluster_ids)
                    # add soil polygons
                    for sc_sub_soillayer in sc_soilcluster.sub_soillayers:
                        #self.add_polygon_stone_columns_soil_clusters(sc_sub_soillayer, sc_soilcluster.columns_left, sc_soilcluster.columns_right)
                         self.add_polygon_stone_columns_soil_clusters_Jointed_Rock(sc_sub_soillayer, sc_soilcluster.columns_left, sc_soilcluster.columns_right, SC_selected['sc_name'], SC_selected)

                    # store sub_soillayers as a field in the selected SC structure
                    SC_selected['sub_soillayers'] = sc_soilcluster.sub_soillayers

                    # clear polygon points
                    while SC_selected['polygonPoints']:
                        self.remove_polygon_point(SC_selected['polygonPoints'])

                    # update with new polygon points
                    #points_new = [[sc_soilcluster.columns_left, sc_soilcluster.columns_top], [sc_soilcluster.columns_right, sc_soilcluster.columns_top],
                    #                        [sc_soilcluster.columns_right, sc_soilcluster.columns_bottom], [sc_soilcluster.columns_left, sc_soilcluster.columns_bottom]]
                    #self.update_polygon_points_rectangle(points_new)
                    top = sc_soilcluster.columns_top
                    bottom = sc_soilcluster.columns_bottom
                    depth = top - bottom
                    left = sc_soilcluster.columns_left
                    right = sc_soilcluster.columns_right
                    SC_selected['polygonPoints'] = self.set_improved_soil_polygon_FDC(top, depth, left, right, polygonPoints_current=SC_selected['polygonPoints'])

                    # refine mesh
                    if 'sc_points_fine_mesh' in SC_selected:
                        self.undo_refine_mesh_around_stone_columns(SC_selected['sc_points_fine_mesh'], SC_selected['sc_name'])
                    SC_selected['sc_points_fine_mesh'] = self.refine_mesh_around_stone_columns(SC_selected['polygonPoints'], SC_selected['sc_name'])

            # collect all polygons for mesh refinement and apply them
            Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(SC['sc_name']) for SC in self.SCs if 'sc_points_fine_mesh' in SC_selected]
            if Polygons_fine_mesh:
                plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the point is correctly entered!') 


    def refine_mesh_around_stone_columns(self, polygonPoints, id_fine_mesh):
        """ Refines mesh around stone columns/ rigid inclusions area 
        Improved soil area is defined by polygonPoints.
        """
        # use information in self.polygonPoints
        #print(self.polygonPoints)
        sc_width = polygonPoints[1]['point'][0] - polygonPoints[0]['point'][0]
        sc_depth = polygonPoints[3]['point'][1] - polygonPoints[0]['point'][1]
        sc_points_fine_mesh = []
        sc_points_fine_mesh.append(polygonPoints[0]['point'])
        sc_points_fine_mesh.append([polygonPoints[1]['point'][0] + 0.3*sc_width, polygonPoints[1]['point'][1]])
        sc_points_fine_mesh.append([polygonPoints[2]['point'][0] + 0.3*sc_width, polygonPoints[2]['point'][1] + 0.3*sc_depth])
        sc_points_fine_mesh.append([polygonPoints[3]['point'][0], polygonPoints[3]['point'][1] + 0.3*sc_depth])

        plaxis2d_input.add_polygon_fine_mesh_with_id(self.plaxis2d_input_file, 'g_i', sc_points_fine_mesh, id_fine_mesh)
        #plaxis2d_input.refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i') # 3 times mesh refinement by default

        return sc_points_fine_mesh


    def undo_refine_mesh_around_stone_columns(self, sc_points_fine_mesh, id_fine_mesh):
        """ Remove mesh refinement including the polygon for the fine mesh
        """
        plaxis2d_input.remove_structure_string_id(self.plaxis2d_input_file, id_fine_mesh, '##FINE_MESH_POLYGON', 2) # remove polygon of the fine mesh
        sc_points_fine_mesh.clear()
        #plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')
                

    def assign_design_variables_to_model_fdc(self, v, variables_fdc):
        """ Assigns current design variables v to plaxis model
        cnt: starting index for reading data in the variable v
        """
        cnt = 0
        fdc_selected = None
        # variables for stone columns
        for variables_ in variables_fdc:
            sc_id = list(variables_.keys())[0]
            for key, _ in variables_[sc_id].items():
                #print(key, value)
                variables_[sc_id][key] = v[cnt]
                cnt += 1

            # the considered fdc structure
            for fdc in self.FDCs:
                if fdc['FDC_name'] == list(variables_.keys())[0]:
                    fdc_selected = fdc
                    break

            self.update_fdc_by_id__(variables_, fdc_selected)

        if fdc_selected is not None:
            # visualize model
            top = fdc_selected['FDC_params']['top'] 
            depth = fdc_selected['FDC_params']['Lc'] 
            left = fdc_selected['polygonPoints'][0]['point'][0]
            right = fdc_selected['polygonPoints'][1]['point'][0]
            fdc_selected['polygonPoints'] = self.set_improved_soil_polygon_FDC(top, depth, left, right, polygonPoints_current=fdc_selected['polygonPoints'])


    def update_fdc_by_id__(self, variables_fdc, fdc):
        """ Updates FDC rigid inclusions parameters
        """
        #print(variables_sc)
        ri_id = list(variables_fdc.keys())[0]
        if ri_id == fdc['FDC_name']:
            for key, value in variables_fdc[ri_id].items():
                if key == 'Lc': 
                    fdc['FDC_params'][key] = value
                    #fdc['FDC_params']['H_lim'] = value # do not update limit depth
                else:
                    fdc['FDC_params'][key] = value
            

    def calculate_fdc__(self):
        """ Calculates fdc following ASIRI method
        """
        # consider only the first FDC structure for now
        fdc = self.FDCs[0]

        params = fdc['FDC_params'].copy()
        params.update(fdc['LTP_params'])
        params.update(fdc['FDC_loading'])
        params.update(fdc['anchorage_params'])
        ri = FDC(self.Layer_polygons, self.Boreholes[0], **params)

        # assemble data
        ri.assemble_data(show=False)

        # update column tip resistance at toe of column (stress-dependent)
        #ri.set_soil_params_at_anchorage_stress_dependent()

        # calculate and check if passed
        ri.calculate(show=False)

        # column settlement on top of LTP
        u_z_c = ri.matrice[0, 26]*1000 #mm


        return u_z_c, ri.isPassed


    def assign_design_variables_to_model_sc(self, v, variables_stone_columns):
        """ Assigns current design variables v to plaxis model
        cnt: starting index for reading data in the variable v
        To date, only variables for stone columns are considered
        """
        cnt = 0
        # variables for stone columns
        for variables_sc in variables_stone_columns:
            sc_id = list(variables_sc.keys())[0]
            for key, _ in variables_sc[sc_id].items():
                #print(key, value)
                variables_sc[sc_id][key] = v[cnt]
                cnt += 1
            
            # the considered sc structure
            for sc in self.SCs:
                if sc['sc_name'] == list(variables_sc.keys())[0]:
                    sc_selected = sc
                    break

            self.update_stone_columns_by_id__(variables_sc, sc_selected)


    def update_stone_columns_by_id__(self, variables_sc, sc):
        """ Updates stone columns parameters
        """
        #print(variables_sc)
        sc_id = list(variables_sc.keys())[0]

        if sc_id == sc['sc_name']:
            for key, value in variables_sc[sc_id].items():
                if key != 'depth': # for 'D' and 'a'
                    sc['sc_params'][key] = value
                    sc['sc_params']['Ac_over_A'] = StoneColumns(**sc['sc_params']).get_Ac_over_A() # also update Ac_over_A when a or D changes
                    #print(self.sc_params['Ac_over_A'])
                else: # 'depth'
                    # update self.polygonPoints and replot
                    columns_top = max([point['point'][1] for point in sc['polygonPoints']])
                    columns_bottom = columns_top - value
                    sc['polygonPoints'][2]['point'][1] = columns_bottom
                    sc['polygonPoints'][3]['point'][1] = columns_bottom
                    for point in sc['polygonPoints']:
                        self.plot_canvas.undo_plot_pathpatches(point['pathpatch'])
                        point['pathpatch'] = self.plot_canvas.plot_point(point['point'])
            

    def calculate_stone_columns_no_PLAXIS__(self):
        """ Calculates stone columns
        This function is used to evaluate the model during optimization
        """
        # consider only the first SC structure for now
        SC_selected = self.SCs[0]
        sc_soilcluster = StoneColumnsSoilClusters(self.project_properties['project_title'], SC_selected['sc_params'], SC_selected['polygonPoints'], self.Layer_polygons, self.Boreholes[0], SC_selected['sc_name'], 
                                        p0=SC_selected['sc_p0'], unlimited_distribution=SC_selected['unlimited_distribution'], thickness_sublayer=SC_selected['sc_thickness_sublayer'], limit_depth=SC_selected['limit_depth'],
                                        user_input_E_s=SC_selected['user_input_E_s'], should_consider_p0=SC_selected['should_consider_p0'])
        sc_soilcluster.calculate_soil_clusters__()

        # get soil settlement u [mm]
        u_improved = sc_soilcluster.sub_soillayers[-1]['u_improved_cummulative']

        return u_improved


    def remove_soil_improvement_soil_clusters_onclick(self):
        """
        """
        structure_name = self.ui.comboBox_45.currentText()

        if '_SC' in structure_name:
            self.remove_stone_columns_soil_clusters(structure_name)

        elif '_FDC' in structure_name:
            self.remove_fdc_soil_clusters(structure_name)


    def remove_stone_columns_soil_clusters(self, sc_name):
        """
        """
        sc_selected = None
        for sc in self.SCs:
            if sc['sc_name'] == sc_name:
                sc_selected = sc
                break

        if sc_selected is not None:
            self.remove_soil_improvement_soil_clusters(sc_selected['sub_soillayers'])

            # undo refine mesh
            if 'sc_points_fine_mesh' in sc_selected:
                self.undo_refine_mesh_around_stone_columns(sc_selected['sc_points_fine_mesh'], sc_selected['sc_name'])
                del sc_selected['sc_points_fine_mesh']

            # collect the remained polygons for mesh refinement and apply them
            Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(sc['sc_name']) for sc in self.SCs if 'sc_points_fine_mesh' in sc]
            if Polygons_fine_mesh:
                plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)
            else:
                plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')


    def remove_fdc_soil_clusters(self, fdc_name):
        """
        """
        fdc_selected = None
        for fdc in self.FDCs:
            if fdc['FDC_name'] == fdc_name:
                fdc_selected = fdc
                #fdc_selected_idx = self.FDCs.index(fdc_selected)
                break

        if fdc_selected is not None:
            self.remove_soil_improvement_soil_clusters(fdc_selected['sub_soillayers'])

            # undo refine mesh
            if 'sc_points_fine_mesh' in fdc_selected:
                self.undo_refine_mesh_around_stone_columns(fdc_selected['sc_points_fine_mesh'], fdc_selected['FDC_name'])
                del fdc_selected['sc_points_fine_mesh']

            # collect the remained polygons for mesh refinement and apply them
            Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(fdc['FDC_name']) for fdc in self.FDCs if 'sc_points_fine_mesh' in fdc]
            if Polygons_fine_mesh:
                plaxis2d_input.apply_refine_mesh_multi_polygons(self.plaxis2d_input_file, 'g_i', Polygons_fine_mesh)
            else:
                plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')


    def remove_soil_improvement_soil_clusters(self, sub_soillayers):
        """ Remove all soil clusters belonging to the stone columns region
        """

        if sub_soillayers:
            sc_soilcluster_ids = [sc_soilcluster['id'] for sc_soilcluster in sub_soillayers]
            #sc_soilcluster_ids = [item for item in sc_soilcluster_ids if isinstance(item, str)]     # filter out unexpected integer item
            if self.Polygons:
                for sc_sub_soillayer_id in sc_soilcluster_ids:
                    deleted_polygon = [item for item in self.Polygons if item['id'] == sc_sub_soillayer_id][0]
                    deleted_polygon_idx = self.Polygons.index(deleted_polygon)
                    deleted_polygon = self.Polygons.pop(deleted_polygon_idx)
                    if isinstance(sc_sub_soillayer_id, str):
                        plaxis2d_input.remove_structure_string_id(self.plaxis2d_input_file, deleted_polygon['id'], '##SOIL_POLYGON', 10)
                        plaxis2d_input.remove_structure_string_id(self.plaxis2d_input_file, deleted_polygon['id'], '##SOIL_POLYGON_IN_STAGE', 2)
                    else:
                        plaxis2d_input.remove_structure(self.plaxis2d_input_file, deleted_polygon['id'], '##SOIL_POLYGON', 10)
                        plaxis2d_input.remove_structure(self.plaxis2d_input_file, deleted_polygon['id'], '##SOIL_POLYGON_IN_STAGE', 2)
                    self.plot_canvas.undo_plot_pathpatches(deleted_polygon['pathpatches'])

            sub_soillayers.clear()


    def add_polygon_stone_columns_soil_clusters(self, sc_sub_soillayer, x_min, x_max):
        """ Adds a polygon for one sub soillayer of the soil improved by stone columns
        """
        interp_function = get_interp_function_Edyn_over_Esta_Esta()

        soilmaterial_origin = sc_sub_soillayer['soilmaterial_layer']
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        soilmaterial_origin_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial_origin + '.json')

        polygon = {}
        polygon['id'] = sc_sub_soillayer['id']
        polygon['soilmaterial'] = soilmaterial_origin + polygon['id']
        soilmaterial_dest_file_path = join(PATH_MATERIAL_LIBRARY, polygon['soilmaterial'] + '.json')

        # copy material file
        if os.path.exists(soilmaterial_origin_file_path):
            if os.path.exists(soilmaterial_dest_file_path):
                os.remove(soilmaterial_dest_file_path)
            shutil.copyfile(soilmaterial_origin_file_path, soilmaterial_dest_file_path)

        # update stiffnesses with soil improvement factor n2, update soil strength parameters 
        with open(soilmaterial_dest_file_path, 'r') as file:
            data = OrderedDict(json.load(file, object_pairs_hook = OrderedDict))
            data['EoedRef'] = data['EoedRef']*sc_sub_soillayer['n2']
            data['E50ref'] = data['E50ref']*sc_sub_soillayer['n2']
            data['EurRef'] = data['EurRef']*sc_sub_soillayer['n2']
            data['Cref'] = sc_sub_soillayer['c_bar']
            data['phi'] = sc_sub_soillayer['phi_bar']
            data['K0nc'] = get_HS_K0nc(sc_sub_soillayer['phi_bar'])
            data['MaterialName'] = data['MaterialName'] + ' ' + polygon['id']
            if 'HSsmall' in polygon['soilmaterial']: # HSsmall soil only
                Edyn_over_Esta = get_interp_Edyn_over_Esta(data['EurRef'], interp_function)
                #print('EurRef: {0}; Edyn_over_Esta: {1}'.format(data['EurRef'], Edyn_over_Esta))
                data['G0ref'] = get_HSsmall_G0ref(data['EurRef'], Edyn_over_Esta)
        with open(soilmaterial_dest_file_path, 'w') as file:
                json.dump(data, file)

        # 
        polygon['points'] = [(x_min, sc_sub_soillayer['top']), (x_max, sc_sub_soillayer['top']),(x_max, sc_sub_soillayer['bottom']), (x_min, sc_sub_soillayer['bottom'])]
        polygon['color'] = sc_sub_soillayer['color']
        polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], polygon['color'])
        self.Polygons.append(polygon)
        plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, soilmaterial_dest_file_path)
        plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)
    

    def add_polygon_stone_columns_soil_clusters_Jointed_Rock(self, sc_sub_soillayer, x_min, x_max, sc_name, sc):
        """ Adds a polygon for one sub soillayer of the soil improved by FDC rigid inclusion
        Soil model is changed to jointed rock for anisotropic stiffnesses assignment.
        """
        #interp_function = get_interp_function_Edyn_over_Esta_Esta()
        soilmaterial_origin = sc_sub_soillayer['soilmaterial_layer']
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        soilmaterial_origin_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial_origin + '.json')

        polygon = {}
        polygon['id'] = sc_sub_soillayer['id']
        soilmaterial_origin_str = soilmaterial_origin.split('_')
        soilmaterial_origin_str[-3] = 'JR'   # jointed rock
        soilmaterial_dest = '_'.join(soilmaterial_origin_str)
        polygon['soilmaterial'] = soilmaterial_dest + polygon['id']
        soilmaterial_dest_file_path = join(PATH_MATERIAL_LIBRARY, polygon['soilmaterial'] + '.json')

        # copy material file
        if os.path.exists(soilmaterial_origin_file_path):
            if os.path.exists(soilmaterial_dest_file_path):
                os.remove(soilmaterial_dest_file_path)
            shutil.copyfile(soilmaterial_origin_file_path, soilmaterial_dest_file_path)

        # update stiffnesses with soil improvement factor n2, update soil strength parameters 
        with open(soilmaterial_dest_file_path, 'r') as rfile:
            data = OrderedDict(json.load(rfile, object_pairs_hook = OrderedDict))
            data['SoilModel'] = int(7)  # 7 for jointed rock model
            #Eref1 = data['EoedRef']*sc_sub_soillayer['n_factor']    # 1: intact rock
            Eref1 = sc_sub_soillayer['E_s'] * sc_sub_soillayer['n2']    # 1: intact rock, stress dependent stiffness
            #alpha = (fdc['FDC_params']['Dc']**2 * np.pi * 0.25)/fdc['FDC_params']['a']**2
            #f_cm = fdc['FDC_params']['fck'] + 8 # MPa
            #Ecm = 1.0e6*22*(f_cm/10)**0.3    # kPa
            #Ecm_smeared = Ecm*alpha # smeared concrete E modulus
            #Eref1 = min(Eref1, Ecm_smeared) # maximal soil replaced stiffness is the smeared concrete stiffness

            nu1 = data['nu']
            Gref1 = Eref1/(2*(1+nu1))
            data['Gref1'] = Gref1
            data['nu1'] = nu1
            data['phi1'] = data['phi']
            data['psi1'] = data['psi']
            data['cref1'] = data['Cref']
            data['alpha11'] = 90.0

            #Eref2 = data['EoedRef'] #2: 
            Eref2 = sc_sub_soillayer['E_s'] # stress-dependent stiffness
            nu2 = min(nu1, np.sqrt(Eref2/Eref1)*(1-nu1)/2)
            data['nu2'] = nu2
            Gref2 = Eref2/(2*(1+nu2))
            data['Eref2'] = Eref2
            data['G2'] = Gref2
            data['MaterialName'] = data['MaterialName'] + ' ' + polygon['id']

            # remove non jointed rock soil parameters
            data.pop('EoedRef', None)
            data.pop('E50ref', None)
            data.pop('EurRef', None)
            data.pop('powerm', None)
            data.pop('K0nc', None)
            data.pop('phi', None)
            data.pop('psi', None)
            data.pop('Cref', None)
            data.pop('nu', None)
            data.pop('Rf', None)
            data.pop('G0ref', None)
            data.pop('gamma07', None)
            data.pop('Pref', None)

        with open(soilmaterial_dest_file_path, 'w') as wfile:
                json.dump(data, wfile)

        # add soil polygon and activate it in initial phase
        polygon['points'] = [(x_min, sc_sub_soillayer['top']), (x_max, sc_sub_soillayer['top']),(x_max, sc_sub_soillayer['bottom']), (x_min, sc_sub_soillayer['bottom'])]
        polygon['color'] = sc_sub_soillayer['color']
        polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], polygon['color'])
        self.Polygons.append(polygon)
        plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, soilmaterial_dest_file_path)
        plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)


    def add_polygon_fdc_LTP(self, top, bottom, left, right, fdc):
        """ Adds a soil cluster for LTP
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN'], r'solver\plaxis2d\materials')
        fname = join(PATH_MATERIAL_LIBRARY, 'LTP' + '.json')  # use Sand_dense_HS by default
        with open(fname, 'r') as rfile: # read material file
            data = OrderedDict(json.load(rfile, object_pairs_hook = OrderedDict))
            data['MaterialName'] = 'LTP'
            data['phi'] = fdc['LTP_params']['phi']
            data['Cref'] = fdc['LTP_params']['c']
            data['EoedRef'] = fdc['LTP_params']['Eoed']
            data['E50ref'] = fdc['LTP_params']['Eoed']
            data['EurRef'] = fdc['LTP_params']['Eoed']*3.0

        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        dest_fname = join(PATH_MATERIAL_LIBRARY, 'LTP' + '.json')
        with open(dest_fname, 'w') as wfile:
                json.dump(data, wfile)

        # add soil polygon and activate it in initial phase
        polygon = {}
        polygon['id'] = randint(100000, 999999)
        polygon['soilmaterial'] = 'LTP'
        polygon['points'] = [(left, top), (right, top), (right, bottom), (left, bottom)]
        polygon['color'] = '#ffff00'    # yellow
        set_material_color(dest_fname, polygon['color'])
        polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], polygon['color'])
        self.Polygons.append(polygon)
        plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, dest_fname)
        plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)

        return polygon


    def add_polygon_fdc_soil_clusters_Jointed_Rock(self, sc_sub_soillayer, x_min, x_max, structure_name, fdc):
        """ Adds a polygon for one sub soillayer of the soil improved by FDC rigid inclusion
        Soil model is changed to jointed rock for anisotropic stiffnesses assignment.
        """
        #interp_function = get_interp_function_Edyn_over_Esta_Esta()
        soilmaterial_origin = sc_sub_soillayer['soilmaterial_layer']
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        soilmaterial_origin_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial_origin + '.json')

        polygon = {}
        polygon['id'] = sc_sub_soillayer['id']
        soilmaterial_origin_str = soilmaterial_origin.split('_')
        soilmaterial_origin_str[-3] = 'JR'   # jointed rock
        soilmaterial_dest = '_'.join(soilmaterial_origin_str)
        polygon['soilmaterial'] = soilmaterial_dest + polygon['id']
        soilmaterial_dest_file_path = join(PATH_MATERIAL_LIBRARY, polygon['soilmaterial'] + '.json')

        # copy material file
        if os.path.exists(soilmaterial_origin_file_path):
            if os.path.exists(soilmaterial_dest_file_path):
                os.remove(soilmaterial_dest_file_path)
            shutil.copyfile(soilmaterial_origin_file_path, soilmaterial_dest_file_path)

        # update stiffnesses with soil improvement factor n2, update soil strength parameters 
        with open(soilmaterial_dest_file_path, 'r') as rfile:
            data = OrderedDict(json.load(rfile, object_pairs_hook = OrderedDict))
            data['SoilModel'] = int(7)  # 7 for jointed rock model
            #Eref1 = data['EoedRef']*sc_sub_soillayer['n_factor']    # 1: intact rock
            Eref1 = sc_sub_soillayer['E_s'] * sc_sub_soillayer['n_factor']    # 1: intact rock, stress dependent stiffness
            alpha = (fdc['FDC_params']['Dc']**2 * np.pi * 0.25)/fdc['FDC_params']['a']**2
            f_cm = fdc['FDC_params']['fck'] + 8 # MPa
            Ecm = 1.0e6*22*(f_cm/10)**0.3    # kPa
            Ecm_smeared = Ecm*alpha # smeared concrete E modulus
            Eref1 = min(Eref1, Ecm_smeared) # maximal soil replaced stiffness is the smeared concrete stiffness

            nu1 = data['nu']
            Gref1 = Eref1/(2*(1+nu1))
            data['Gref1'] = Gref1
            data['nu1'] = nu1
            data['phi1'] = data['phi']
            data['psi1'] = data['psi']
            data['cref1'] = data['Cref']
            data['alpha11'] = 90.0

            #Eref2 = data['EoedRef'] #2: 
            Eref2 = sc_sub_soillayer['E_s'] # stress-dependent stiffness
            nu2 = min(nu1, np.sqrt(Eref2/Eref1)*(1-nu1)/2)
            data['nu2'] = nu2
            Gref2 = Eref2/(2*(1+nu2))
            data['Eref2'] = Eref2
            data['G2'] = Gref2
            data['MaterialName'] = data['MaterialName'] + ' ' + polygon['id']

            # remove non jointed rock soil parameters
            data.pop('EoedRef', None)
            data.pop('E50ref', None)
            data.pop('EurRef', None)
            data.pop('powerm', None)
            data.pop('K0nc', None)
            data.pop('phi', None)
            data.pop('psi', None)
            data.pop('Cref', None)
            data.pop('nu', None)
            data.pop('Rf', None)
            data.pop('G0ref', None)
            data.pop('gamma07', None)
            data.pop('Pref', None)

        with open(soilmaterial_dest_file_path, 'w') as wfile:
                json.dump(data, wfile)

        # add soil polygon and activate it in initial phase
        polygon['points'] = [(x_min, sc_sub_soillayer['top']), (x_max, sc_sub_soillayer['top']),(x_max, sc_sub_soillayer['bottom']), (x_min, sc_sub_soillayer['bottom'])]
        polygon['color'] = sc_sub_soillayer['color']
        polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], polygon['color'])
        self.Polygons.append(polygon)
        plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, soilmaterial_dest_file_path)
        plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)


    def add_polygon_fdc_soil_clusters_HS_HSsmall(self, sc_sub_soillayer, x_min, x_max):
        """ Adds a polygon for one sub soillayer of the soil improved by FDC rigid inclusion
        HS or HSsmall is used, material model not changed. (This function is unused now).
        """
        interp_function = get_interp_function_Edyn_over_Esta_Esta()

        soilmaterial_origin = sc_sub_soillayer['soilmaterial_layer']
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        soilmaterial_origin_file_path = join(PATH_MATERIAL_LIBRARY, soilmaterial_origin + '.json')

        polygon = {}
        polygon['id'] = sc_sub_soillayer['id']
        polygon['soilmaterial'] = soilmaterial_origin + polygon['id']
        soilmaterial_dest_file_path = join(PATH_MATERIAL_LIBRARY, polygon['soilmaterial'] + '.json')

        # copy material file
        if os.path.exists(soilmaterial_origin_file_path):
            if os.path.exists(soilmaterial_dest_file_path):
                os.remove(soilmaterial_dest_file_path)
            shutil.copyfile(soilmaterial_origin_file_path, soilmaterial_dest_file_path)

        # update stiffnesses with soil improvement factor n2, update soil strength parameters 
        with open(soilmaterial_dest_file_path, 'r') as rfile:
            data = OrderedDict(json.load(rfile, object_pairs_hook = OrderedDict))
            data['EoedRef'] = data['EoedRef']*sc_sub_soillayer['n_factor']
            data['E50ref'] = data['E50ref']*sc_sub_soillayer['n_factor']
            data['EurRef'] = data['EurRef']*sc_sub_soillayer['n_factor']
            #data['Cref'] = sc_sub_soillayer['c_bar']
            #data['phi'] = sc_sub_soillayer['phi_bar']
            #data['K0nc'] = get_HS_K0nc(sc_sub_soillayer['phi_bar'])
            data['MaterialName'] = data['MaterialName'] + ' ' + polygon['id']
            if 'HSsmall' in polygon['soilmaterial']: # HSsmall soil only
                Edyn_over_Esta = get_interp_Edyn_over_Esta(data['EurRef'], interp_function)
                #print('EurRef: {0}; Edyn_over_Esta: {1}'.format(data['EurRef'], Edyn_over_Esta))
                data['G0ref'] = get_HSsmall_G0ref(data['EurRef'], Edyn_over_Esta)
        with open(soilmaterial_dest_file_path, 'w') as wfile:
                json.dump(data, wfile)

        # add soil polygon and activate it in initial phase
        polygon['points'] = [(x_min, sc_sub_soillayer['top']), (x_max, sc_sub_soillayer['top']),(x_max, sc_sub_soillayer['bottom']), (x_min, sc_sub_soillayer['bottom'])]
        polygon['color'] = sc_sub_soillayer['color']
        polygon['pathpatches'] = self.plot_canvas.plot_polygon(polygon['points'], polygon['color'])
        self.Polygons.append(polygon)
        plaxis2d_input.add_polygon(self.plaxis2d_input_file, 'g_i', polygon, soilmaterial_dest_file_path)
        plaxis2d_input.add_polygon_initial_phase(self.plaxis2d_input_file, 'g_i', polygon)


    #def check_constraints_sc(self, constraint_items):
    #    """ Check if the design variables satisfy constraints for stone columns
    #    """
    #    constraint_value = 0
    #    if 'stone_columns_spacing' in constraint_items:
    #        a = self.sc_params['a'] # spacing
    #        if a < constraint_items['stone_columns_spacing'][0]:
    #            constraint_value += 1
    #        if a > constraint_items['stone_columns_spacing'][1]:
    #            constraint_value += 1

    #    return int(constraint_value)


    def estimate_total_cost_sc(self):
        """ Estimates the total construction cost for stone columns
        """
        # unit costs
        UnitCosts = namedtuple('UnitCosts', 'concrete_volume, steel, anchor_length, stone_columns, rigid_inclusions, BG_per_day, anchor_installer_per_day, mobilization')
        
        # read user input from table
        user_costs = []
        for j in range(self.ui.tableWidget_23.columnCount()):
            user_costs.append(float(self.ui.tableWidget_23.item(0, j).text()))
        
        ## update unit_costs
        unit_costs = UnitCosts(*user_costs)

        # consider only the first SC structure for now
        sc = self.SCs[0]

        # calcuate cost
        cost = 0.0
        sc_cost_factory = StructureCostFactory()
        sc_cost = sc_cost_factory.get_cost_structure('StoneColumns', None, unit_costs, None, None, None, [], sc['sc_params'], sc['polygonPoints'])
        cost += sc_cost.calculate_cost()

        return cost


    def estimate_total_cost_fdc(self):
        """ Estimates the total construction cost for stone columns
        """
        # unit costs
        UnitCosts = namedtuple('UnitCosts', 'concrete_volume, steel, anchor_length, stone_columns, rigid_inclusions, BG_per_day, anchor_installer_per_day, mobilization')
        
        # read user input from table
        user_costs = []
        for j in range(self.ui.tableWidget_23.columnCount()):
            user_costs.append(float(self.ui.tableWidget_23.item(0, j).text()))
        
        ## update unit_costs
        unit_costs = UnitCosts(*user_costs)

        # consider only the first FDC structure for now
        fdc = self.FDCs[0]

        # calcuate cost
        cost = 0.0
        sc_cost_factory = StructureCostFactory()
        sc_cost = sc_cost_factory.get_cost_structure('RigidInclusions', None, unit_costs, None, None, None, self.Walls, fdc['FDC_params'], fdc['polygonPoints'])
        cost += sc_cost.calculate_cost()

        return cost


    def open_dim_wall_tool(self):
        """ Open the wall dimensioning window
        """
        try:
            if self.Walls:
                # which wall   
                wall_id =  int(self.ui.comboBox_14.currentText())
                selected_wallmaterial = None
                for wall in self.Walls:
                    if wall['id'] == wall_id:
                        selected_wall = wall
                        break

                for wallmaterial in self.Wallmaterials:
                    if selected_wall['json_item'] == wallmaterial['json_item']:
                        selected_wallmaterial = wallmaterial
                        break

                form = QtWidgets.QDialog()
                if 'Dwall' == self.Walls[0]['wall_type']:
                    D = read_data_in_json_item(self.Walls[0]['json_item'], 'd') # pile diameter
                    S = 1.0
                elif 'SPW' == self.Walls[0]['wall_type']:   # secant piles wall
                    D = read_data_in_json_item(self.Walls[0]['json_item'], 'D') # pile diameter
                    S = read_data_in_json_item(self.Walls[0]['json_item'], 'S') # spacing b/t two piles
                    if selected_wallmaterial['SPW131']: # SPW1:3:1
                        S = 2*S
                else: # contiguous piles wall
                    D = read_data_in_json_item(self.Walls[0]['json_item'], 'D') # pile diameter
                    S = read_data_in_json_item(self.Walls[0]['json_item'], 'S')/2 # spacing b/t two piles
                project_title = 'Design of Wall ' + self.project_properties['project_title']
                if 'cross_section_pile' not in self.dim_params:     # initialize cross section only if not defined
                    cross_section_pile = {'D': D, 'S': S, 'H': 100.0}                                  # initial concrete cover is 100.0 mm
                    self.dim_params['cross_section_pile'] = cross_section_pile
                if 'cross_section_barrette' not in self.dim_params: # initialize cross section only if not defined
                    cross_section_barrette = {'D': D, 'B': 2.6, 'BT': 2.8, 'H1': 100.0, 'H2': 100.0}   # initial concrete cover is 100.0 mm
                    self.dim_params['cross_section_barrette'] = cross_section_barrette

            else: # no Moniman project data is available
                self.set_paths_and_file()
                form = QtWidgets.QDialog()
                project_title = 'Design of Wall'
                if 'cross_section_pile' not in self.dim_params:     # initialize cross section only if not defined
                    cross_section_pile = {'D': 1.0, 'S': 1.0, 'H': 100.0}                                  # initial concrete cover is 100.0 mm
                    self.dim_params['cross_section_pile'] = cross_section_pile
                if 'cross_section_barrette' not in self.dim_params: # initialize cross section only if not defined
                    cross_section_barrette = {'D': 1.0, 'B': 2.6, 'BT': 2.8, 'H1': 100.0, 'H2': 100.0}   # initial concrete cover is 100.0 mm
                    self.dim_params['cross_section_barrette'] = cross_section_barrette

            # open Dim_wall form
            dim_obj = Dim_wall(form, project_title, **self.dim_params)

            self.dim_params['code'] = dim_obj.code
            self.dim_params['concrete_grade'] = dim_obj.concrete_grade
            self.dim_params['params_concrete'] = dim_obj.params_concrete
            self.dim_params['reinf_grade'] = dim_obj.reinf_grade
            self.dim_params['params_reinf'] = dim_obj.params_reinf
            self.dim_params['crack_width'] = dim_obj.crack_width
            self.dim_params['min_reinf'] = dim_obj.min_reinf
            self.dim_params['design_situation'] = dim_obj.design_situation
            self.dim_params['params_psf'] = dim_obj.params_psf
            self.dim_params['percentage_N'] = dim_obj.percentage_N
            self.dim_params['wall_outputs_phases'] = dim_obj.wall_outputs_phases
            self.dim_params['A_s'] = dim_obj.A_s
            self.dim_params['a_s'] = dim_obj.a_s
            self.dim_params['A_s1'] = dim_obj.A_s1
            self.dim_params['A_s2'] = dim_obj.A_s2
            self.dim_params['a_s12'] = dim_obj.a_s12
            self.dim_params['bar_diameters_vertical'] = dim_obj.bar_diameters_vertical
            self.dim_params['staggered_reinf_vertical_pile'] = dim_obj.staggered_reinf_vertical_pile
            self.dim_params['bar_diameters_shear'] = dim_obj.bar_diameters_shear
            self.dim_params['staggered_reinf_shear_pile'] = dim_obj.staggered_reinf_shear_pile
            self.dim_params['staggered_reinf_vertical_barrette_A_s_1'] = dim_obj.staggered_reinf_vertical_barrette_A_s_1
            self.dim_params['staggered_reinf_vertical_barrette_A_s_2'] = dim_obj.staggered_reinf_vertical_barrette_A_s_2
            self.dim_params['staggered_reinf_shear_barrette'] = dim_obj.staggered_reinf_shear_barrette

            self.dim_params['cross_section_pile'] = dim_obj.pile.cross_section
            self.dim_params['cross_section_barrette'] = dim_obj.barrette.cross_section

        except Exception as e:
            write_traceback_to_file(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])))


    def open_dim_anchor_tool(self):
        """ Open the anchor dimensioning window
        """
        try:
            if self.Anchors:
                form = QtWidgets.QDialog()
                project_title = self.project_properties['project_title']
                dim_obj = Dim_anchor(form, project_title, self.Anchors)
            
            else: # dimension a dummpy anchor
                anchor = {}
                anchor['position'] = [0.0, 0.0]
                anchor['angle'] = '-'
                anchor['Lspacing'] = '-'
                anchor['strand number'] = 5
                anchor['strand diameter'] = "0.6''"
                anchor['F_anchor'] = 200.0
                anchor['strand grade'] = '1570/1770'
                anchor['design situation'] = 'Situation E'
                form = QtWidgets.QDialog()
                project_title = ''
                dim_obj = Dim_anchor(form, project_title, [anchor])

        except Exception as e:
            write_traceback_to_file(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])))


    def open_dim_strut_tool(self):
        """ Open the strut dimensioning window
        """
        if self.Struts:
            try:
                form = QtWidgets.QDialog()
                project_title = self.project_properties['project_title']
                dim_obj = Dim_strut(form, project_title, self.Struts, **self.dim_params_strut)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. The model is properply created using an older version of Moniman!".format(e))
        
        else:   # add a dummy strut for dimensioning
            new_strut = {}
            new_strut['position'] = [0.0, 0.0]
            new_strut['direct_x'] = -12.0
            new_strut['direct_y'] = 0.0
            new_strut['Lspacing'] = 5.5
            new_strut['F_prestress'] = 0.0  # no prestress by default
            new_strut['usage'] = ''
            new_strut['json_item'] = ''
            new_strut['id'] = randint(100000, 999999)

            # parameters for dimensioning, will be overwritten in the strut dimensing tool
            new_strut['F_strut'] = 200.0 # by default, to be overwriten
            new_strut['slope_vert'] = math.atan(abs(new_strut['direct_y'])/abs(new_strut['direct_x']))*180/math.pi  # deg, newly introduced
            new_strut['slope_horiz'] = 0.0                                                                  # deg, newly intorduced: horizontal inclination (default 0.0, to be changed by user)
            new_strut['buckling length sy'] = 2*math.sqrt(new_strut['direct_x']**2 + new_strut['direct_y']**2)      # m, newly introduced
            new_strut['buckling length sz'] = 2*math.sqrt(new_strut['direct_x']**2 + new_strut['direct_y']**2)      # m, newly introduced: to be adjusted by user
            new_strut['eccentricity e/h'] = 0.1
            new_strut['eccentricity e/b'] = 0.0
            new_strut['strut_type'] = 'SteelTube'                          # 'SteelTube' or 'SteelProfile'
            new_strut['profile_id'] = ''                                   # newly introduced, to be assigned update_strut_layer()
            new_strut['nos'] = int(1)                   # number of beams  
            new_strut['distance_beam2beam'] = 100.0     # distance beam-to-beam [mm] 
            new_strut['assigned'] = False
            new_strut['design_loads'] = {'Nd': 100.0, 'Myd': 0.0, 'Mzd': 0.0}
            #
            form = QtWidgets.QDialog()
            project_title = 'Strut dimensioning'
            dim_obj = Dim_strut(form, project_title, [new_strut], **self.dim_params_strut)

        # save user settings
        self.dim_params_strut['design_situation'] = dim_obj.design_situation
        self.dim_params_strut['fyk'] = dim_obj.fyk


    def open_dim_waler_tool(self):
        """ Open the waler dimensioning window
        """
        if self.Struts or self.Anchors:
            try:
                form = QtWidgets.QDialog()
                project_title = self.project_properties['project_title']
                dim_obj = Dim_waler(form, project_title, self.Struts, self.Anchors, **self.dim_params_waler)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. The model is properply created using an older version of Moniman!".format(e))
        
        else:   # add a dummy strut for dimensioning
            new_strut = {}
            new_strut['position'] = [0.0, 0.0]
            new_strut['direct_x'] = -12.0
            new_strut['direct_y'] = 0.0
            new_strut['Lspacing'] = 5.5
            new_strut['F_prestress'] = 0.0  # no prestress by default
            new_strut['usage'] = ''
            new_strut['json_item'] = ''
            new_strut['id'] = randint(100000, 999999)
            new_strut['F_strut'] = 200.0 
            # parameters for waler beam
            new_strut['waler_width_support'] = 0.5 # width of support plate, m
            new_strut['waler_width_influence'] = 0.0 # width of influence for the calculation of normal force, Nm
            new_strut['waler_type'] = 'concrete'   # 'concrete' or 'steel_profile'
            new_strut['waler_concrete'] = {'b': 0.5, 'h': 0.5, 'edge_sep': 50, 'fck': 25.0, 'fyk': 500.0}      # units are m, m, mm, MPa, MPa
            new_strut['waler_concrete_reinf_As_E'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
            new_strut['waler_concrete_reinf_As_L'] = {'n': 4, 'dia': '16'}  # dia is string, '12' is single 16 mm bar, 'D12' is double 12 mm bars
            new_strut['waler_concrete_reinf_as'] = {'dia': '10', 'n_legs': 4, 'spacing': 25.0}  # spacing is in cm
            new_strut['waler_steel_profile'] = {'profile_id': 'HEA1000', 'nos': int(1), 'fyk': 235.0}    # units are -, -, MPa
            new_strut['F_support'] = 200.0 # by default
            form = QtWidgets.QDialog()
            project_title = 'Waler dimensioning'
            dim_obj = Dim_waler(form, project_title, [new_strut], [], **self.dim_params_waler)

        # save user settings
        self.dim_params_waler['design_situation'] = dim_obj.design_situation


    def open_dim_cross_section_tool(self):
        """ Open the cross-section dimensioning window
        """
        if self.Walls:
            form = QtWidgets.QDialog()
            #D = self.Walls[0] # pile diamter
            if 'Dwall' == self.Walls[0]['wall_type']:
                D = read_data_in_json_item(self.Walls[0]['json_item'], 'd') # pile diameter
                S = 1.0
            elif 'SPW' == self.Walls[0]['wall_type']:   # secant piles wall
                D = read_data_in_json_item(self.Walls[0]['json_item'], 'D') # pile diameter
                S = read_data_in_json_item(self.Walls[0]['json_item'], 'S') # spacing b/t two piles
            else: # contiguous piles wall
                D = read_data_in_json_item(self.Walls[0]['json_item'], 'D') # pile diameter
                S = read_data_in_json_item(self.Walls[0]['json_item'], 'S')/2 # spacing b/t two piles
            #project_title = 'Dim Cross Section ' + self.project_properties['project_title']
            project_title = 'Design of Capping Beam ' + self.project_properties['project_title']
        else: # no Moniman project data is available
            self.set_paths_and_file()
            form = QtWidgets.QDialog()
            D = 1.0
            S = 1.0
            project_title = 'Design of Cross Section'

        dim_obj = Dim_cross_section(form, project_title, **self.dim_params_cross_section)
        self.dim_params_cross_section['cross_section_pile'] = dim_obj.pile.cross_section
        self.dim_params_cross_section['cross_section_barrette'] = dim_obj.barrette.cross_section
        self.dim_params_cross_section['internal_forces_permanent'] = dim_obj.internal_forces_permanent
        self.dim_params_cross_section['internal_forces_transient'] = dim_obj.internal_forces_transient
        self.dim_params_cross_section['code'] = dim_obj.code
        self.dim_params_cross_section['concrete_grade'] = dim_obj.concrete_grade
        self.dim_params_cross_section['params_concrete'] = dim_obj.params_concrete
        self.dim_params_cross_section['reinf_grade'] = dim_obj.reinf_grade
        self.dim_params_cross_section['params_reinf'] = dim_obj.params_reinf
        self.dim_params_cross_section['crack_width'] = dim_obj.crack_width
        self.dim_params_cross_section['min_reinf'] = dim_obj.min_reinf
        self.dim_params_cross_section['design_situation'] = dim_obj.design_situation
        self.dim_params_cross_section['params_psf'] = dim_obj.params_psf
        self.dim_params_cross_section['bar_diameters_vertical'] = dim_obj.bar_diameters_vertical
        self.dim_params_cross_section['bar_diameters_shear'] = dim_obj.bar_diameters_shear
        self.dim_params_cross_section['staggered_reinf_vertical_barrette_A_s_1'] = dim_obj.staggered_reinf_vertical_barrette_A_s_1
        self.dim_params_cross_section['staggered_reinf_vertical_barrette_A_s_2'] = dim_obj.staggered_reinf_vertical_barrette_A_s_2
        self.dim_params_cross_section['staggered_reinf_shear_barrette'] = dim_obj.staggered_reinf_shear_barrette
        self.dim_params_cross_section['should_rotate_plot'] = dim_obj.should_rotate_plot



    def open_dim_wall_inserted_profile_beam_tool(self):
        """ Open the dimensioning tool for inserted steel profile
        """
        if len(self.Walls) > 1 and (self.Walls[1]['wall_type'] == 'Steel profile H/U'):
            try:
                form = QtWidgets.QDialog()
                project_title = self.project_properties['project_title']
                dim_obj = Dim_wall_inserted_steel_profile(form, project_title, self.Walls, self.Wallmaterials, self.Phases, **self.dim_params_inserted_steel_profile)

                # save params
                self.dim_params_inserted_steel_profile['design_situation'] = dim_obj.design_situation
                self.dim_params_inserted_steel_profile['internal_forces_max'] = dim_obj.internal_forces_max
                self.dim_params_inserted_steel_profile['internal_forces_top_RC_wall'] = dim_obj.internal_forces_top_RC_wall

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. The model is properply created using an older version of Moniman!".format(e))
        
        else:   # add a dummy strut for dimensioning
            self.dialog.show_message_box('Warning', "For using this tool your model must have 2 walls: the lower wall is RC wall and the upper wall is steel profile wall!")


    def open_dim_wall_MIP_profile_beam_tool(self):
        """ Open the dimensioning tool for MIP steel profile
        """
        if len(self.Walls) > 1 and (self.Walls[1]['wall_type'] == 'Steel profile H/U'):
            try:
                form = QtWidgets.QDialog()
                project_title = self.project_properties['project_title']
                dim_obj = Dim_MIP_steel_profile(form, project_title, self.Walls, self.Wallmaterials, self.Phases, **self.dim_params_MIP_steel_profile)

                # save params
                self.dim_params_MIP_steel_profile['design_situation'] = dim_obj.design_situation
                self.dim_params_MIP_steel_profile['minmax_values_at_min_M2D'] = dim_obj.minmax_values_at_min_M2D
                self.dim_params_MIP_steel_profile['minmax_values_at_max_M2D'] = dim_obj.minmax_values_at_max_M2D
                self.dim_params_MIP_steel_profile['minmax_values_at_min_Q2D'] = dim_obj.minmax_values_at_min_Q2D
                self.dim_params_MIP_steel_profile['minmax_values_at_max_Q2D'] = dim_obj.minmax_values_at_max_Q2D

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. The model is properply created using an older version of Moniman!".format(e))
        
        else:   # add a dummy strut for dimensioning
            self.dialog.show_message_box('Warning', "For using this tool your model must have 2 walls: the lower wall is RC wall and the upper wall is steel profile wall!")


    def open_borelogs_analyzer(self):
        """ Open the borelogs analysis tool
        """
        form = QtWidgets.QDialog()
        Borelogs_Analyzer(form, self.Boreholes[0], self.Layer_polygons)


    def save(self):
        """ Save PLAXMAN's state
        """
        try:
            # set paths
            self.set_paths_and_file()

            objs = (self.project_properties, self.geometry, self.mesh, 
                    self.Boreholes, self.Layer_polygons, self.material_json_item,
                    self.Soilmaterials, self.strand_json_item, self.grout_json_item, self.strut_json_item,
                    self.wall_json_item, self.Wallmaterials, self.Walls, self.Anchors, self.Struts, self.Lineloads, self.Pointloads,
                    self.polygonPoints, self.Polygons, self.Soilclusters, self.Soilclusters_notdried,
                    self.Waterlevels, self.Drains, self.Drain, self.Phases, self.new_phase, self.Points_obs,
                    self.sc_params, self.sc_name, self.sub_soillayers, self.sc_p0,
                    self.sc_thickness_sublayer, self.sc_points_fine_mesh, self.SCs, self.FDCs, self.dim_params, self.dim_params_cross_section, 
                    self.dim_params_strut, self.dim_params_waler, self.dim_params_inserted_steel_profile, None)

            filename = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_state.mon')
            #saveobjs(filename, *objs)
            saveobjs_pathpatches_ignored(filename, *objs)
            print("Plaxman's state is saved in {}".format(filename))

        except Exception as e:
            write_traceback_to_file(os.getcwd(), e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(os.getcwd())))

    def load(self):
        """ Load PLAXMAN's state
        """
        try:
            # set paths
            self.set_paths_and_file()

            filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_state.mon')
            if not isfile(filename):
                self.dialog.show_message_box('Error', 'File {} does not exist for loading'.format(filename))

            else:
                try:
                    #dummy = list(loadobjs(filename))
                    (self.project_properties, self.geometry, self.mesh,
                    self.Boreholes, self.Layer_polygons, self.material_json_item,
                    self.Soilmaterials, self.strand_json_item, self.grout_json_item, self.strut_json_item,
                    self.wall_json_item, self.Wallmaterials, self.Walls, self.Anchors, self.Struts, self.Lineloads, self.Pointloads,
                    self.polygonPoints, self.Polygons, self.Soilclusters, self.Soilclusters_notdried,
                    self.Waterlevels, self.Drains, self.Drain, self.Phases, self.new_phase, self.Points_obs, 
                    self.sc_params, self.sc_name, self.sub_soillayers, self.sc_p0,
                    self.sc_thickness_sublayer, self.sc_points_fine_mesh, self.SCs, self.FDCs, self.dim_params, self.dim_params_cross_section, 
                    self.dim_params_strut, self.dim_params_waler, self.dim_params_inserted_steel_profile, _,) = loadobjs(filename)
                except: # last Moniman version: without self.Drains, self.dim_params_strut, self.dim_params_waler
                    (self.project_properties, self.geometry, self.mesh,
                    self.Boreholes, self.Layer_polygons, self.material_json_item,
                    self.Soilmaterials, self.strand_json_item, self.grout_json_item, self.strut_json_item,
                    self.wall_json_item, self.Wallmaterials, self.Walls, self.Anchors, self.Struts, self.Lineloads, self.Pointloads,
                    self.polygonPoints, self.Polygons, self.Soilclusters, self.Soilclusters_notdried,
                    self.Waterlevels, self.Drain, self.Phases, self.new_phase, self.Points_obs, 
                    self.sc_params, self.sc_name, self.sub_soillayers, self.sc_p0,
                    self.sc_thickness_sublayer, self.sc_points_fine_mesh, self.SCs, self.FDCs, self.dim_params, self.dim_params_cross_section, _,) = loadobjs(filename)

                # workaround loading previous versions of Moniman project
                if self.dim_params_cross_section is None:
                    self.dim_params_cross_section = {}

                # clear UI items
                self.plaxman_x.clear_tables_reloading()
                self.plaxman_x.clear_comboboxes_reloading()
                # clear plot_canvas
                self.plot_canvas.axes.cla()
        
                loadPlaxman.update_geometry(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.project_properties, sys.modules['moniman_paths'], self.geometry)
                loadPlaxman.add_borehole(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Boreholes, self.geometry)
                loadPlaxman.add_layer(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Layer_polygons, self.Boreholes)
                self.plaxman_x.display_layers_on_table(self.Layer_polygons, self.Boreholes, self.geometry, self.ui.tableWidget)

                loadPlaxman.assign_material(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Layer_polygons, self.Boreholes, self.Soilmaterials)
                loadPlaxman.add_wall(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Walls, self.Wallmaterials)
                loadPlaxman.add_ground_anchor(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Anchors, self.geometry)
                loadPlaxman.add_strut(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Struts, self.geometry)
                loadPlaxman.add_lineload(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Lineloads, self.geometry)
                loadPlaxman.add_pointload(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Pointloads, self.geometry)
                loadPlaxman.add_polygon_point(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.polygonPoints)
                loadPlaxman.add_polygon(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Polygons)
                loadPlaxman.apply_mesh(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.mesh, self.Lineloads, self.Pointloads, self.Anchors, self.Struts, self.Walls)
                wall_thickness = 0.0    # wall thickness for plotting the excavated soil clusters
                if self.Walls:
                    wall_thickness = self.Walls[0]['wall_thickness']
                loadPlaxman.add_soilcluster(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Soilclusters, wall_thickness)
                loadPlaxman.add_waterlevel(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Waterlevels)
                loadPlaxman.add_drain(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Drain)
                loadPlaxman.add_drains(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Drains)
                loadPlaxman.add_phase(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Phases, self.Lineloads, self.Pointloads, self.Walls, 
                                      self.Soilclusters, self.Anchors, self.Struts, self.Drain)
                loadPlaxman.add_observed_points(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.Points_obs)
                
                # Connect plaxman signals to slots
                self.connect_signals_to_slots()

                # Stone columns & rigid inclusions
                loadPlaxman.define_soil_improvement_structure(self.ui, self.plot_canvas, self.plaxis2d_input_file, 'g_i', self.sc_name, self.SCs, self.FDCs, self.polygonPoints)

                # Extended Plaxman
                self.plaxman_x.display_walls_on_table(self.Walls)
                self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_25)
                self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_26)
                self.plaxman_x.display_lineloads_on_table(self.Lineloads, self.geometry[1], self.geometry[3])
                self.plaxman_x.display_pointloads_on_table(self.Pointloads, self.geometry[1], self.geometry[3])

                self.plaxman_x.display_waterlevels_on_table(self.Waterlevels)
                self.plaxman_x.display_soilclusters_on_table(self.Soilclusters)

                # Connect change of geometry's x_min and x_max to the handling slot
                self.ui.lineEdit.returnPressed.connect(lambda: self.update_geometry_xmin_xmax(float(self.ui.lineEdit.text()), float(self.ui.lineEdit_3.text())))
                self.ui.lineEdit_3.returnPressed.connect(lambda: self.update_geometry_xmin_xmax(float(self.ui.lineEdit.text()), float(self.ui.lineEdit_3.text())))

                print("Plaxman's state saved in file '{}' is loaded".format(filename))

        except Exception as e:
            write_traceback_to_file(os.getcwd(), e)
            self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(os.getcwd())))


    def print_report(self):
        """ Print design report
        """
        pages_model = []
        pages_structure = []
        pages_support_forces = []
        pages_fielddata = []

        if not self.project_properties:
            self.dialog.show_message_box('Warning', 'There is nothing to generate the report!')

        else:
            # table for soil stratigraphy
            page_stratigraphy = ReportPlaxman()
            page_stratigraphy.add_project_info(self.project_properties)
            page_stratigraphy.add_table_soil_stratigraphy(self.Layer_polygons, self.Boreholes)

            # table for soil materials
            page_soil_materials = ReportPlaxman()
            page_soil_materials.add_project_info(self.project_properties)
            page_soil_materials.add_table_soil_materials(self.Layer_polygons)
            # table for soil materials: permeabilities only
            page_soil_materials_perm = ReportPlaxman()
            page_soil_materials_perm.add_project_info(self.project_properties)
            page_soil_materials_perm.add_table_soil_materials_permeability(self.Layer_polygons)

            # table for wall material
            page_wall_material = ReportPlaxman()
            page_wall_material.add_project_info(self.project_properties)
            page_wall_material.add_table_wall_material(self.Walls[0])

            try:
                # model states
                for num_phase in range(len(self.Phases)):
                #for num_phase in range(2):
                    page = ReportPlaxman()
                    page.add_project_info(self.project_properties)
                    page.add_model_at_phase(self.geometry, self.Boreholes, self.Layer_polygons, self.Walls, self.Anchors, self.Struts, self.Lineloads, self.Pointloads, self.Polygons,
                                                    self.Soilclusters, self.Waterlevels, self.Phases, num_phase)
                    pages_model.append(page)

                # structure outputs
                path_output = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
                p, g_o = ReportPlaxman.open_output_database(join(path_output, 'retaining_wall.p2dx'))
                for num_phase in range(len(self.Phases)):
                #for num_phase in range(2):
                    # structure (wall)
                    page_s = ReportPlaxman()
                    page_s.add_project_info(self.project_properties)
                    page_s.add_structure_at_phase(p, g_o, path_output, self.Phases, num_phase, self.Walls, self.Anchors, self.Struts)
                    pages_structure.append(page_s)

                    # structure (anchors/ struts)
                    page_support_forces = ReportPlaxman()
                    page_support_forces.add_project_info(self.project_properties)
                    page_support_forces.add_table_anchor_strut_forces_at_phase(p, g_o, num_phase, path_output, self.Anchors, self.Struts, self.Phases)
                    pages_support_forces.append(page_support_forces)

                    # field data output/FoS curve
                    if self.Phases[num_phase]['phase_name'] == 'FoS':
                        # falure slip planes
                        page_FoS1 = ReportPlaxman()
                        page_FoS1.add_project_info(self.project_properties)
                        page_FoS1.add_field_data_at_phase_FoS(p, g_o, path_output, num_phase, self.Phases)
                        # FoS curve
                        page_FoS2 = ReportPlaxman()
                        page_FoS2.add_project_info(self.project_properties)
                        page_FoS2.add_msf_curve_at_FoS_phase(p, g_o, path_output, num_phase, self.Phases)

                    elif self.Phases[num_phase]['phase_name'][:10] == 'Dewatering':  # show active water pressure
                        page_fielddata = ReportPlaxman()
                        page_fielddata.add_project_info(self.project_properties)
                        page_fielddata.add_field_data_at_phase_dewatering(p, g_o, path_output, num_phase, self.Phases)
                        pages_fielddata.append(page_fielddata)

                    else:
                        page_fielddata = ReportPlaxman()
                        page_fielddata.add_project_info(self.project_properties)
                        page_fielddata.add_field_data_at_phase(p, g_o, path_output, num_phase, self.Phases)
                        pages_fielddata.append(page_fielddata)

                # close PLAXIS2D Output
                g_o.close()

            except Exception as e:
                #self.dialog.show_message_box('Error', 'Please view ERROR_LOG.txt in {} for further information!'.format(os.path.join(os.getcwd())))
                self.dialog.show_message_box('Warning', 'Exception {} has occured. Make sure that your Plaxis2D database is available and all calculation phases passed!'.format(e))

            # merg all pages
            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
            project_title = self.project_properties['project_title']
            filename = None
            try:    
                filename = os.path.join(MONIMAN_OUTPUTS, 'Report Retaining Wall ' + project_title + '.pdf')
                pp = PdfPages(filename)
                page_stratigraphy.fig.savefig(pp, format='pdf', bbox_inches='tight')
                page_soil_materials.fig.savefig(pp, format='pdf', bbox_inches='tight')
                page_soil_materials_perm.fig.savefig(pp, format='pdf', bbox_inches='tight')
                page_wall_material.fig.savefig(pp, format='pdf', bbox_inches='tight')

                for page_m, page_s, page_sf, page_f in zip(pages_model, pages_structure, pages_support_forces, pages_fielddata):
                    page_m.fig.savefig(pp, format='pdf', bbox_inches='tight')
                    page_s.fig.savefig(pp, format='pdf', bbox_inches='tight')
                    if page_sf.fig is not None:
                        page_sf.fig.savefig(pp, format='pdf', bbox_inches='tight')
                    page_f.fig.savefig(pp, format='pdf', bbox_inches='tight')

                try:
                    page_FoS1.fig.savefig(pp, format='pdf', bbox_inches='tight')
                    page_FoS2.fig.savefig(pp, format='pdf', bbox_inches='tight')
                except:
                    pass

                pp.close()
                # view report in Acrobat Reader
                cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
                cmd.append(filename)
                subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)

                # clean pathpatches_report


                return int(0)

            except PermissionError:
                return filename
