# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:02:53 2019

@author: nya
"""

import sys, os
from os.path import isfile
import numpy as np
from collections import OrderedDict, namedtuple
from scipy.special import comb
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QFileDialog
from tools.file_tools import savetxt
from tools.file_tools import saveobjs, loadobjs
from tools.math import hex_to_rgb
from tools.list_functions import flatten_list
from system.run_thread import RunThreadIter
from optiman.optiman_load import loadOptiman
from gui.gui_main_matplotlib import MyStaticMplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#from gui.gui_all_forms_ui import Ui_Form

class Optiman():
    def __init__(self, plaxman_ap=None):
        """ Initializes Optiman attributes
        """
        self.plaxman_ap = plaxman_ap
        self.plot_canvas = self.plaxman_ap.plot_canvas
        self.ui = self.plaxman_ap.ui
        self.dialog = self.plaxman_ap.dialog
        self.form = self.plaxman_ap.form               # for Pareto front explorer

        self.objectives = OrderedDict({'Cost': 0.0})     # Objectives for design optimization
        self.sensitivity_scores = {}
        self.local_sensitivity = None
        self.objectives_WallNxMQ_Envelope = {}  # Additional objectives for sensitivity analysis of wall internal forces

        self.final_excavation_level = {}    # the final excavation level
        self.wall = None                    # the wall for optimization (only one object)
        self.selected_anchor_id = None      # for temporarily holding the selected anchor's ID
        #self.active_earth_pressure_wedge = {}   # active earth pressure wedge

        # design variables of wall
        self.variables_wall = {}            # design variables of wall (self.wall)
        self.variables_wall_min = {}        # min values for design variables of wall 
        self.variables_wall_max = {}        # max values for design variables of wall 
        self.variables_wall_subset = {}     # set of available values for variables of wall

        # design variables of ground anchors
        self.variables_anchors = []            # design variables of ground anchors (list of dictionaries)
        self.variables_anchors_min = []        # min values for design variables of ground anchors (list of dictionaries)
        self.variables_anchors_max = []        # max values for variables of ground anchors (list of dictionaries)
        self.variables_anchors_subset = []     # set of values for variables of ground anchors (list of dictionaries)

        # design variables of struts
        self.variables_struts = []            # design variables of struts (list of dictionaries)
        self.variables_struts_min = []        # min values for design variables of struts (list of dictionaries)
        self.variables_struts_max = []        # max values for variables of struts (list of dictionaries)
        self.variables_struts_subset = []     # set of values for variables of struts (list of dictionaries)

        # design variables of stone columns
        self.variables_stone_columns = []            # design variables of stone columns (list of dictionaries)
        self.variables_stone_columns_min = []        # min values for design variables of stone columns (list of dictionaries)
        self.variables_stone_columns_max = []        # max values for variables of stone columns (list of dictionaries)
        self.variables_stone_columns_subset = []     # set of values for variables of stone columns (list of dictionaries)

        # design variables of FDC rigid inclusions
        self.variables_fdc = []                     # design variables of rigid inclusions (list of dictionaries)
        self.variables_fdc_min = []                 # min values for design variables of rigid inclusions (list of dictionaries)
        self.variables_fdc_max = []                 # max values for variables of rigid inclusions (list of dictionaries)
        self.variables_fdc_subset = []              # set of values for variables of rigid inclusions (list of dictionaries)

        # merged design variables
        self.v0 = None                        # current design varables
        self.v_min = None                     # lower bounds for design variables
        self.v_max = None                     # upper bounds for design variables
        self.v_subset = None                  # sets for design variables

        # unit costs for objective calculation
        self.unit_costs= [150.0, 1000.0, 70.0, 30.0, 520.0, 6000.0, 500.0, 0.0]

        self.ratio_perturbation_sensitivity = 0.1  # ratio for perturbation of design variables in sensitivity analysis
        self.rnd_samples_input_file = None    # path to file that stores randomly sampled parameter sets for metamodel training
        self.optiman_nsga = None             # nsga2 workflow and result, do not save this object, memory leakage
        self.solutions_nsga = None            # nsga solutions, save this for nsga solutions instead
        self.objectives_nsga = None           # nsga objectives, save this for nsga objectives instead
        self.iter_nsga = None                 # nsga generation, save this for nsga objectives instead
        self.n_generation = 50                # number of nsga2 generations
        self.n_population = 12                # number of individuals in nsga2 population
        self.initial_population = None        # an initial population for NSGAII/III

        # matplotlib canvas for plotting sensitivity scores
        self.plot_layout1 = QtWidgets.QVBoxLayout(self.ui.widget_5)
        self.plot_canvas_sensitivity = MyStaticMplCanvas(self.ui.widget_3, width=1, height=1, dpi=100)        
        self.plot_layout1.addWidget(self.plot_canvas_sensitivity)   

        # matplotlib canvas for plotting objective values
        self.plot_layout2 = QtWidgets.QVBoxLayout(self.ui.widget_7)
        self.plot_canvas_objectives = MyStaticMplCanvas(self.ui.widget_7, width=1, height=1, dpi=100)        
        #self.plot_canvas_objectives = MyStaticMplCanvas_Event(self.ui.widget_7, width=1, height=1, dpi=100)        
        self.plot_layout2.addWidget(self.plot_canvas_objectives)   
        self.plot_toolbar_objectives = NavigationToolbar(self.plot_canvas_objectives, None)        
        self.plot_layout2.addWidget(self.plot_toolbar_objectives)

        # connect signals
        self.connect_signals_to_slots()



    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.treeWidget_3.itemChanged.connect(lambda item, column: self.update_max_min_wall_variables(item, column))
        self.ui.treeWidget_3.itemChanged.connect(lambda item, column: self.update_subset_wall_variables(item, column))
        self.ui.treeWidget_4.itemChanged.connect(lambda item, column: self.update_max_min_anchor_variables(item, column))
        self.ui.treeWidget_4.itemChanged.connect(lambda item, column: self.update_subset_anchor_variables(item, column))
        self.ui.treeWidget_5.itemChanged.connect(lambda item, column: self.update_max_min_strut_variables(item, column))
        self.ui.treeWidget_5.itemChanged.connect(lambda item, column: self.update_subset_strut_variables(item, column))
        self.ui.treeWidget_7.itemChanged.connect(lambda item, column: self.update_max_min_stone_columns_variables(item, column))
        self.ui.treeWidget_7.itemChanged.connect(lambda item, column: self.update_subset_stone_columns_variables(item, column))
        self.ui.treeWidget_7.itemChanged.connect(lambda item, column: self.update_max_min_fdc_variables(item, column))
        self.ui.treeWidget_7.itemChanged.connect(lambda item, column: self.update_subset_fdc_variables(item, column))
        #self.ui.checkBox_11.toggled.connect(lambda checked: self.plaxman_ap.add_active_earthpressure_wedge(checked))
        self.ui.checkBox_12.toggled.connect(lambda checked: self.update_objectives_WallUx(checked))
        self.ui.checkBox_15.toggled.connect(lambda checked: self.update_objectives_WallUy(checked))
        self.ui.checkBox_13.toggled.connect(lambda checked: self.update_objectives_SoilUy(checked))
        self.ui.checkBox_14.toggled.connect(lambda checked: self.update_objectives_FoS(checked))

        # unit costs
        self.ui.tableWidget_23.cellChanged.connect(lambda row, column: self.update_unit_costs(row, column))

        # plot sensitivity scores
        self.ui.comboBox_40.currentTextChanged.connect(lambda objective_text: self.report_local_sensitivity_scores(objective_text))

        
    def display_unit_costs(self):
        """ Displays unit costs
        """
        cost_labels = ['Concrete volume [EUR/m^3]', 'Steel [EUR/ton]', 'Anchor length [EUR/m]', 'Stone columns [EUR/m^3]', 'Rigid inclusions [EUR/m^3]', 'BG cost/day [EUR]', 'Anchor installer cost/day [EUR]', 'Mobilization [EUR]']
        #UnitCosts = namedtuple('UnitCosts', 'concrete_volume, steel, anchor_length, stone_columns, rigid_inclusions, BG_per_day, anchor_installer_per_day')
        self.ui.tableWidget_23.setHorizontalHeaderLabels(cost_labels)
        #self.unit_costs.append(0.0)    # mobilization cost
        for i, cost in enumerate(self.unit_costs):
            self.ui.tableWidget_23.setItem(0, i, QtWidgets.QTableWidgetItem(str(cost))) 
            self.ui.tableWidget_23.item(0, i).setBackground(QColor(242, 255, 116)) # light yellow

    @pyqtSlot()
    def update_unit_costs(self, row, column):
        """ Update unit costs
        """
        try:
            if row==0:
                cost = float(self.ui.tableWidget_23.item(0, column).text())
                self.unit_costs[column] = cost
        except:
            self.dialog.show_message_box('Warning', 'Please check if the value you entered is correct!')


    def display_all_model_components(self):
        """ Displays all model components on tables
        """
        self.display_Walls()
        self.display_Anchors()
        self.display_Struts()
        self.display_points_obs()
        self.display_unit_costs()
        

    def display_Walls(self):
        """ Sets Walls as Optiman's attribute
        """
        if self.plaxman_ap.Walls:
            self.wall = self.plaxman_ap.Walls[-1]

            # update wall ids in comboBox
            self.ui.comboBox_28.clear()
            ids = [str(wall['id']) for wall in self.plaxman_ap.Walls]
            self.ui.comboBox_28.addItems(ids)


    def display_Anchors(self):
        """ Sets Anchors as Optiman's attribute
        """
        # update anchor ids in comboBox
        self.ui.comboBox_34.clear()
        ids = [str(anchor['id']) for anchor in self.plaxman_ap.Anchors]
        self.ui.comboBox_34.addItems(ids)


    def display_Struts(self):
        """ Sets Struts as Optiman's attribute
        """
        # update anchor ids in comboBox
        self.ui.comboBox_35.clear()
        ids = [str(strut['id']) for strut in self.plaxman_ap.Struts]
        self.ui.comboBox_35.addItems(ids)


    def display_points_obs(self):
        """ Assigns observation points
        """
        for obs_set in self.plaxman_ap.Points_obs:
            if obs_set['obs_type'] == 'WallNxMQ_Envelope':
                self.objectives_WallNxMQ_Envelope['Wall Nx'] = 0.0
                self.objectives_WallNxMQ_Envelope['Wall M'] = 0.0
                self.objectives_WallNxMQ_Envelope['Wall Q'] = 0.0
                break


    def select_wall_variables(self):
        """ Selects wall variables for design optimization
        """
        if len(self.plaxman_ap.Walls) > 0:
            wall_id_selected = self.ui.comboBox_28.currentText()

            for wall in self.plaxman_ap.Walls:
                if wall['id'] == int(wall_id_selected):
                    self.wall = wall
                    if 'Dwall' == wall['wall_type']:
                        self.dialog.open_edit_wall_Dwall('Dwall', wall['wall_name'], True)

                    elif 'SPW' == wall['wall_type']:
                        self.dialog.open_edit_wall_SPW('SPW', wall['wall_name'], True)

                    elif 'CPW' == wall['wall_type']:
                        self.dialog.open_edit_wall_CPW('CPW', wall['wall_name'], True)

                    break # stop looping Walls once a wall having 'id' is found


    def add_wall_variables(self):
        """ Adds wall varialbes: wall cross section properties + embedment depth
        """

        self.ui.treeWidget_3.blockSignals(True)
        try: 
            variables = self.dialog.soil_edit_box.parameters_selected
            variables['id'] = int(self.ui.comboBox_28.currentText()) # keep wall id for later selection
        except AttributeError:
            variables = OrderedDict()
            variables['id'] = int(self.ui.comboBox_28.currentText()) # keep wall id for later selection

        # set wall (necessary when only embedment depth is selected)
        wall_id_selected = self.ui.comboBox_28.currentText()
        for wall in self.plaxman_ap.Walls:
            if wall['id'] == int(wall_id_selected):
                self.wall = wall

        if variables or (self.ui.checkBox_8.checkState() == 2): # variable has been selected 
            #print(variables)
            try:
                # is embedment depth selected as a design variable?
                final_excavation_level = self.plaxman_ap.final_excavation_level['level']
                wall_bottom = self.wall['point2'][1]
                depth_embedment = final_excavation_level - wall_bottom

                if depth_embedment > 0:
                    # add design variables
                    if self.ui.checkBox_8.checkState() == 2:
                        variables['depth_embedment'] = depth_embedment

                    # clear design variables and treewidget
                    self.variables_wall.clear()
                    #self.ui.treeWidget_3.clear()
                    if self.ui.treeWidget_3.topLevelItemCount() > 0:
                        self.ui.treeWidget_3.takeTopLevelItem(0)

                    # create design variables and their default bounds
                    self.variables_wall = variables.copy()  # shallow copy
                    self.variables_wall_min = variables.copy()  # shallow copy (OrderedDict)
                    self.variables_wall_max = variables.copy()  # shallow copy (OrderedDict)
                    self.variables_wall_subset = variables.copy()  # shallow copy (OrderedDict)
                    for key, value in self.variables_wall.items():
                        if key is not 'id':
                            self.variables_wall_min[key] = value - 0.5*value
                            self.variables_wall_max[key] = value + 0.5*value
                            # subset values, empty list by default
                            self.variables_wall_subset[key] = []

                    # list design variables on treeWidget_3
                    self.ui.treeWidget_3.setColumnCount(6)
                    # add root
                    item = QtWidgets.QTreeWidgetItem([self.wall['wall_name'] + str(self.wall['id']), 'Wall variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                    self.ui.treeWidget_3.addTopLevelItem(item)
                    self.ui.treeWidget_3.expandItem(item) # expand children of this item
    
                    # add children
                    cnt = 0
                    for key, value in variables.items():
                        if key is not 'id':
                            cnt += 1
                            child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(value - 0.5*value), str(value + 0.5*value)])
                            item.addChild(child)
                            child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                            child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                            child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                            child.setFlags(child.flags() | Qt.ItemIsEditable) 

                    self.ui.treeWidget_3.blockSignals(False)

                else:
                    self.dialog.show_message_box('Warning', 'Final excavation level must not be lower than top of the wall!')
        
            except(KeyError):
                self.dialog.show_message_box('Warning', 'Please set a final excavation level (by creating Automated phases) !')


    @pyqtSlot()
    def update_max_min_wall_variables(self, item, column):
        """ Updates min/max values for design variables of wall
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        #print(item.text(column))
        #print(item.parent().indexOfChild(item)) # row (child) number, starting from 0
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) != ''): # respond only text is not empty (avoid VallueError exception when value is changed by programming)
            if column == 3:
                value = float(item.text(column))
                self.variables_wall_min[key] = value
            elif column == 4:
                value = float(item.text(column))
                self.variables_wall_max[key] = value


    @pyqtSlot()
    def update_subset_wall_variables(self, item, column):
        """ Updates subset values for design variables of wall
        This slot is called upon change of values in treewidget.
        """
        key = item.text(1)  # key (located at column 1 of the changed child item)
        #if (column > 0) and (item.text(column) != ''): 
        if column > 0:
            values_text = item.text(column)
            if column == 5:
                try:
                    self.variables_wall_subset[key] = [float(value) for value in values_text.split(',')]
                except ValueError:
                    self.variables_wall_subset[key] = []


    def select_strut_variables(self):
        """ Selects design variables for strut
        """
        self.selected_strut_id = int(self.ui.comboBox_35.currentText())

        for strut in self.plaxman_ap.Struts:
            if strut['id'] == self.selected_strut_id:
                self.dialog.open_design_variables_selection_strut(strut)



    def add_strut_variables(self):
        """ Adds the selected deisign variables for struts
        """
        self.ui.treeWidget_5.blockSignals(True)
        try:
            if any(self.dialog.soil_edit_box.isVariableSelected): # if any variables are selected
                # which ground anchor is selected
                for strut in self.plaxman_ap.Struts:
                    if strut['id'] == self.selected_strut_id:
                        selected_strut = strut
                        break
                # list design variables on treeWidget_5
                self.ui.treeWidget_5.setColumnCount(6)
                # add root
                item = QtWidgets.QTreeWidgetItem(['Strut_' + str(self.selected_strut_id), 'Strut variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                self.ui.treeWidget_5.addTopLevelItem(item)
                self.ui.treeWidget_5.expandItem(item) # expand children of this item
    
                # add children
                keys = ['level', 'Lspacing']
                variables = OrderedDict()
                variables_min = OrderedDict()
                variables_max = OrderedDict()
                variables_subset = OrderedDict()
                cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in self.variables_anchors)
                cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in self.variables_struts)
                cnt = len(self.variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
                for i, key in enumerate(keys):
                    if self.dialog.soil_edit_box.isVariableSelected[i] is True:
                        if key is 'level':
                            variables[key] = selected_strut['position'][1]
                        else:
                            variables[key] = selected_strut[key]

                        child = QtWidgets.QTreeWidgetItem(['v' + str(cnt + i), key, str(variables[key]), str(variables[key] - 0.5*variables[key]), str(variables[key]+ 0.5*variables[key])])
                        item.addChild(child)
                        #item.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow (text)
                        #item.setForeground(3, QBrush(QColor(242, 255, 116))) # light yellow (background)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        variables_min[key] = variables[key] - 0.5*variables[key]
                        variables_max[key] = variables[key] + 0.5*variables[key]
                        variables_subset[key] = []

                strut_id = selected_strut['id']    
                variables_strut_id = {strut_id: variables}            # design variables indexed by ground anchor id
                variables_min_strut_id = {strut_id: variables_min}    # lower limits of design variables indexed by ground anchor id
                variables_max_strut_id = {strut_id: variables_max}    # upper limits of design variables indexed by ground anchor id
                variables_subset_strut_id = {strut_id: variables_subset}    # set of design variables indexed by ground anchor id
                self.variables_struts.append(variables_strut_id)
                self.variables_struts_min.append(variables_min_strut_id)
                self.variables_struts_max.append(variables_max_strut_id)
                self.variables_struts_subset.append(variables_subset_strut_id)

                self.ui.treeWidget_5.blockSignals(False)

        except (AttributeError):
            self.dialog.show_message_box('Warning', 'Please select design variables of groundanchor first!')


    def remove_strut_variables(self):
        """ Remove design variables of the last added strut
        """
        if self.variables_struts:
            self.variables_struts.pop()
            self.variables_struts_min.pop()
            self.variables_struts_max.pop()
            self.variables_struts_subset.pop()
            self.ui.treeWidget_5.takeTopLevelItem(len(self.variables_struts))


    def select_anchor_variables(self):
        """ Selects design variables for ground anchors
        """
        self.selected_anchor_id = int(self.ui.comboBox_34.currentText())

        for anchor in self.plaxman_ap.Anchors:
            if anchor['id'] == self.selected_anchor_id:
                self.dialog.open_design_variables_selection_anchor(anchor)


    def add_anchor_variables(self):
        """ Adds the selected design variables for ground anchors
        """
        self.ui.treeWidget_4.blockSignals(True)
        try:
            if any(self.dialog.soil_edit_box.isVariableSelected): # if any variables are selected
                # which ground anchor is selected
                for anchor in self.plaxman_ap.Anchors:
                    if anchor['id'] == self.selected_anchor_id:
                        selected_anchor = anchor
                        break
                # list design variables on treeWidget_3
                self.ui.treeWidget_4.setColumnCount(6)
                # add root
                item = QtWidgets.QTreeWidgetItem(['Groundanchor_' + str(self.selected_anchor_id), 'Anchor variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                self.ui.treeWidget_4.addTopLevelItem(item)
                self.ui.treeWidget_4.expandItem(item) # expand children of this item
    
                # add children
                keys = ['level', 'angle', 'length_free', 'Lspacing', 'F_prestress']
                variables = OrderedDict()
                variables_min = OrderedDict()
                variables_max = OrderedDict()
                variables_subset = OrderedDict()
                cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in self.variables_anchors)
                cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in self.variables_struts)
                cnt = len(self.variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
                for i, key in enumerate(keys):
                    if self.dialog.soil_edit_box.isVariableSelected[i] is True:
                        if key is 'level':
                            variables[key] = selected_anchor['position'][1]
                        else:
                            variables[key] = selected_anchor[key]

                        child = QtWidgets.QTreeWidgetItem(['v'+ str(cnt + i), key, str(variables[key]), str(variables[key] - 0.5*variables[key]), str(variables[key]+ 0.5*variables[key])])
                        item.addChild(child)
                        #item.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow (text)
                        #item.setForeground(3, QBrush(QColor(242, 255, 116))) # light yellow (background)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        variables_min[key] = variables[key] - 0.5*variables[key]
                        variables_max[key] = variables[key] + 0.5*variables[key]
                        variables_subset[key] = []

                anchor_id = selected_anchor['id']    
                variables_anchor_id = {anchor_id: variables}            # design variables indexed by ground anchor id
                variables_min_anchor_id = {anchor_id: variables_min}    # lower limits of design variables indexed by ground anchor id
                variables_max_anchor_id = {anchor_id: variables_max}    # upper limits of design variables indexed by ground anchor id
                variables_subset_anchor_id = {anchor_id: variables_subset}  # set of design variables indexed by ground anchor id
                self.variables_anchors.append(variables_anchor_id)
                self.variables_anchors_min.append(variables_min_anchor_id)
                self.variables_anchors_max.append(variables_max_anchor_id)
                self.variables_anchors_subset.append(variables_subset_anchor_id)

                self.ui.treeWidget_4.blockSignals(False)

                # display table for user seletion of soil layers that are ground anchor competent
                self.display_anchor_competent_soil_layers()

        except (AttributeError):
            self.dialog.show_message_box('Warning', 'Please select design variables of groundanchor first!')


    def remove_anchor_variables(self):
        """ Remove design variables of the last added anchor
        """
        if self.variables_anchors:
            self.variables_anchors.pop()
            self.variables_anchors_min.pop()
            self.variables_anchors_max.pop()
            self.variables_anchors_subset.pop()
            self.ui.treeWidget_4.takeTopLevelItem(len(self.variables_anchors))

    
    def select_soil_improvement_variables(self):
        """ Selects design variables for soil improvement structure
        """
        si_name = self.ui.comboBox_47.currentText()
        if '_SC' in si_name:
            for sc in self.plaxman_ap.SCs:
                if sc['sc_name'] == si_name:
                    sc_selected = sc
                    break
            self.select_stone_columns_variables(sc_selected)

        elif '_FDC' in si_name:
            for fdc in self.plaxman_ap.FDCs:
                if fdc['FDC_name'] == si_name:
                    fdc_selected = fdc
                    break
            self.select_FDC_variables(fdc_selected)


    def select_FDC_variables(self, fdc):
        """ Selects design variables for FDC rigid inclusion
        """
        FDC_params = fdc['FDC_params']
        polygonPoints = fdc['polygonPoints']
        if not (FDC_params and polygonPoints):
            self.dialog.show_message_box('Warning', 'Please define FDC rigid inclusions in Plaxman>Soil polygons!')
        else:
            self.dialog.open_design_variables_selection_rigid_inclusions(fdc['FDC_name'], fdc['FDC_params'])
            self.selected_soil_improvement_id = fdc['FDC_name']


    def select_stone_columns_variables(self, sc):
        """ Selects design variables for stone columns
        """
        sc_params = sc['sc_params']
        polygonPoints = sc['polygonPoints']
        if not (sc_params and polygonPoints):
            self.dialog.show_message_box('Warning', 'Please define stone columns in Plaxman>Soil polygons!')
        else:
            columns_top = max([point['point'][1] for point in polygonPoints])
            columns_bottom = min([point['point'][1] for point in polygonPoints])
            columns_depth = columns_top - columns_bottom
            self.dialog.open_design_variables_selection_stone_columns(sc['sc_name'], sc['sc_params'], columns_depth)
            self.selected_soil_improvement_id = sc['sc_name']


    def add_soil_improvement_variables(self):
        """ Adds the selected design variables for soil improvement structure
        """
        si_name = self.ui.comboBox_47.currentText()
        if '_SC' in si_name:
            for sc in self.plaxman_ap.SCs:
                if sc['sc_name'] == si_name:
                    sc_selected = sc
                    break
            self.add_stone_columns_variables(sc_selected)
        elif '_FDC' in si_name:
            for fdc in self.plaxman_ap.FDCs:
                if fdc['FDC_name'] == si_name:
                    fdc_selected = fdc
                    break
            self.add_FDC_variables(fdc_selected)


    def add_FDC_variables(self, fdc):
        """ Adds the selected design variables for stone columns
        """
        self.ui.treeWidget_7.blockSignals(True)
        try:
            if any(self.dialog.soil_edit_box.isVariableSelected): # if any variables are selected
                # list design variables on treeWidget_3
                self.ui.treeWidget_7.setColumnCount(6)
                # add root
                item = QtWidgets.QTreeWidgetItem(['RigidInclusions_' + str(self.selected_soil_improvement_id), 'Variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                self.ui.treeWidget_7.addTopLevelItem(item)
                self.ui.treeWidget_7.expandItem(item) # expand children of this item
    
                # add children
                keys = ['Dc', 'a', 'Lc']
                variables = OrderedDict()
                variables_min = OrderedDict()
                variables_max = OrderedDict()
                variables_subset = OrderedDict()
                cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in self.variables_anchors)
                cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in self.variables_struts)
                cnt_variables_stone_columns = sum(len(list(variables_sc.values())[0].items()) for variables_sc in self.variables_stone_columns)
                cnt_variables_fdc = sum(len(list(variables_.values())[0].items()) for variables_ in self.variables_fdc)
                cnt = len(self.variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts + cnt_variables_stone_columns + cnt_variables_fdc
                for i, key in enumerate(keys):
                    if self.dialog.soil_edit_box.isVariableSelected[i] is True:
                        variables[key] = fdc['FDC_params'][key]

                        child = QtWidgets.QTreeWidgetItem(['v'+ str(cnt + i), key, str(variables[key]), str(variables[key] - 0.5*variables[key]), str(variables[key]+ 0.5*variables[key])])
                        item.addChild(child)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        variables_min[key] = variables[key] - 0.5*variables[key]
                        variables_max[key] = variables[key] + 0.5*variables[key]
                        variables_subset[key] = []

                ri_id = self.selected_soil_improvement_id    
                variables_ri_id = {ri_id: variables}                    # design variables indexed by rigid inclusions id
                variables_min_ri_id = {ri_id: variables_min}            # lower limits of design variables indexed by rigid inclusions id
                variables_max_ri_id = {ri_id: variables_max}            # upper limits of design variables indexed by rigid inclusions id
                variables_subset_ri_id = {ri_id: variables_subset}      # set of design variables indexed by rigid inclusions id
                self.variables_fdc.append(variables_ri_id)
                self.variables_fdc_min.append(variables_min_ri_id)
                self.variables_fdc_max.append(variables_max_ri_id)
                self.variables_fdc_subset.append(variables_subset_ri_id)

                self.ui.treeWidget_7.blockSignals(False)

        except (AttributeError):
            self.dialog.show_message_box('Warning', 'Please select design variables of rigid inclusions first!')



    def add_stone_columns_variables(self, sc):
        """ Adds the selected design variables for stone columns
        """
        self.ui.treeWidget_7.blockSignals(True)
        try:
            if any(self.dialog.soil_edit_box.isVariableSelected): # if any variables are selected
                # list design variables on treeWidget_3
                self.ui.treeWidget_7.setColumnCount(6)
                # add root
                item = QtWidgets.QTreeWidgetItem(['StoneColumns_' + str(self.selected_soil_improvement_id), 'Variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                self.ui.treeWidget_7.addTopLevelItem(item)
                self.ui.treeWidget_7.expandItem(item) # expand children of this item
    
                # add children
                keys = ['D', 'a', 'depth']
                variables = OrderedDict()
                variables_min = OrderedDict()
                variables_max = OrderedDict()
                variables_subset = OrderedDict()
                cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in self.variables_anchors)
                cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in self.variables_struts)
                cnt_variables_stone_columns = sum(len(list(variables_sc.values())[0].items()) for variables_sc in self.variables_stone_columns)
                cnt = len(self.variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts + cnt_variables_stone_columns
                for i, key in enumerate(keys):
                    if self.dialog.soil_edit_box.isVariableSelected[i] is True:
                        if key is 'depth':
                            columns_top = max([point['point'][1] for point in sc['polygonPoints']])
                            columns_bottom = min([point['point'][1] for point in sc['polygonPoints']])
                            columns_depth = columns_top - columns_bottom
                            variables[key] = columns_depth
                        else:
                            variables[key] = sc['sc_params'][key]

                        child = QtWidgets.QTreeWidgetItem(['v'+ str(cnt + i), key, str(variables[key]), str(variables[key] - 0.5*variables[key]), str(variables[key]+ 0.5*variables[key])])
                        item.addChild(child)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        variables_min[key] = variables[key] - 0.5*variables[key]
                        variables_max[key] = variables[key] + 0.5*variables[key]
                        variables_subset[key] = []

                sc_id = self.selected_soil_improvement_id    
                variables_sc_id = {sc_id: variables}                    # design variables indexed by stone columns id
                variables_min_sc_id = {sc_id: variables_min}            # lower limits of design variables indexed by stone columns id
                variables_max_sc_id = {sc_id: variables_max}            # upper limits of design variables indexed by stone columns id
                variables_subset_sc_id = {sc_id: variables_subset}      # set of design variables indexed by stone columns id
                self.variables_stone_columns.append(variables_sc_id)
                self.variables_stone_columns_min.append(variables_min_sc_id)
                self.variables_stone_columns_max.append(variables_max_sc_id)
                self.variables_stone_columns_subset.append(variables_subset_sc_id)

                self.ui.treeWidget_7.blockSignals(False)

        except (AttributeError):
            self.dialog.show_message_box('Warning', 'Please select design variables of stone columns first!')


    def remove_soil_improvement_variables(self):
        """ Removes design variables of soil improvement structure
        """
        si_name = self.ui.comboBox_47.currentText()
        if '_SC' in si_name:
            self.remove_stone_columns_variables()
        elif '_FDC' in si_name:
            self.remove_fdc_variables()


    def remove_fdc_variables(self):
        """ Remove design variables of the last selected variables for fdc rigid inclusions
        """
        if self.variables_fdc:
            self.variables_fdc.pop()
            self.variables_fdc_min.pop()
            self.variables_fdc_max.pop()
            self.variables_fdc_subset.pop()
            self.ui.treeWidget_7.takeTopLevelItem(len(self.variables_fdc))


    def remove_stone_columns_variables(self):
        """ Remove design variables of the last selected variables for stone columns
        """
        if self.variables_stone_columns:
            self.variables_stone_columns.pop()
            self.variables_stone_columns_min.pop()
            self.variables_stone_columns_max.pop()
            self.variables_stone_columns_subset.pop()
            self.ui.treeWidget_7.takeTopLevelItem(len(self.variables_stone_columns))


    def display_anchor_competent_soil_layers(self):
        """ Displays soil layers for user selection of ground anchor competent soil layers
        """
        self.ui.tableWidget_17.setRowCount(2*len(self.plaxman_ap.Layer_polygons))
        self.ui.tableWidget_17.horizontalHeader().setVisible(True)
        column_labels = ['Soil layer', 'G. anchor competence', 'G. anchor through layers', 'Tskin [kN/m]']
        self.ui.tableWidget_17.setColumnCount(len(column_labels))
        self.ui.tableWidget_17.setHorizontalHeaderLabels(column_labels)

        for layer_i, layerpolygon in enumerate(self.plaxman_ap.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            #print(layer_i, soilmaterial_layer)
            self.ui.tableWidget_17.setItem(2*layer_i, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # soilmaterial name
            self.ui.tableWidget_17.item(2*layer_i, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color
            self.ui.tableWidget_17.setSpan(2*layer_i, 0, 2, 1)

            self.ui.tableWidget_17.setCellWidget(2*layer_i, 1, QtWidgets.QCheckBox('Selection?'))   # grouting competent?
            #self.ui.tableWidget_17.item(2*layer_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
            self.ui.tableWidget_17.setSpan(2*layer_i, 1, 2, 1)

            if layer_i < (len(self.plaxman_ap.Layer_polygons) - 1):
                self.ui.tableWidget_17.setCellWidget(2*layer_i+1, 2, QtWidgets.QCheckBox('Selection?'))   # grouting through layers?
                #self.ui.tableWidget_17.item(2*layer_i+1, 2).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_17.setSpan(2*layer_i+1, 2, 2, 1)

            #self.ui.tableWidget_17.setItem(2*layer_i, 3, QtWidgets.QTableWidgetItem('200.0')) # skin resistance
            self.ui.tableWidget_17.setItem(2*layer_i, 3, QtWidgets.QTableWidgetItem(str(layerpolygon['Tskin']))) # skin resistance
            #self.ui.tableWidget_17.item(2*layer_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
            self.ui.tableWidget_17.setSpan(2*layer_i, 3, 2, 1)



    @pyqtSlot()
    def update_max_min_anchor_variables(self, item, column):
        """ Updates min/max values for design variables of a ground anchor
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) is not ''):
            # get groundanchor id
            anchor_id = int(item.parent().text(0).split('_')[1])    # the considered ground anchor id
            for i, variables_anchor in enumerate(self.variables_anchors): # loop over variables for each of the ground anchors
                if anchor_id in variables_anchor.keys():
                    if column == 3:
                        value = float(item.text(column))
                        self.variables_anchors_min[i][anchor_id][key] = value
                    elif column == 4:
                        value = float(item.text(column))
                        self.variables_anchors_max[i][anchor_id][key] = value


    @pyqtSlot()
    def update_subset_anchor_variables(self, item, column):
        """ Updates subset values for design variables of a ground anchor
        This slot is called upon change of values in treewidget.
        """
        key = item.text(1)  # key (located at column 1 of the changed child item)
        #if (column > 0) and (item.text(column) != ''): 
        if column > 0:
            anchor_id = int(item.parent().text(0).split('_')[1])    # the considered ground anchor id
            for i, variables_anchor in enumerate(self.variables_anchors): # loop over variables for each of the ground anchors
                if anchor_id in variables_anchor.keys():
                    if column == 5:
                        try:
                            values_text = item.text(column)
                            self.variables_anchors_subset[i][anchor_id][key] = [float(value) for value in values_text.split(',')]
                        except ValueError:
                            self.variables_anchors_subset[i][anchor_id][key] = []


    @pyqtSlot()
    def update_max_min_strut_variables(self, item, column):
        """ Updates min/max values for design variables of a strut
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) is not ''):
            # get groundanchor id
            strut_id = int(item.parent().text(0).split('_')[1])    # the considered ground anchor id
            for i, variables_strut in enumerate(self.variables_struts): # loop over variables for each of the ground anchors
                if strut_id in variables_strut.keys():
                    if column == 3:
                        value = float(item.text(column))
                        self.variables_struts_min[i][strut_id][key] = value
                    elif column == 4:
                        value = float(item.text(column))
                        self.variables_struts_max[i][strut_id][key] = value


    @pyqtSlot()
    def update_subset_strut_variables(self, item, column):
        """ Updates subset values for design variables of a strut
        This slot is called upon change of values in treewidget.
        """
        key = item.text(1)  # key (located at column 1 of the changed child item)
        #if (column > 0) and (item.text(column) != ''): 
        if column > 0:
            strut_id = int(item.parent().text(0).split('_')[1])    # the considered ground anchor id
            for i, variables_strut in enumerate(self.variables_struts): # loop over variables for each of the ground anchors
                if strut_id in variables_strut.keys():
                    if column == 5:
                        try:
                            values_text = item.text(column)
                            self.variables_struts_subset[i][strut_id][key] = [float(value) for value in values_text.split(',')]
                        except ValueError:
                            self.variables_struts_subset[i][strut_id][key] = []


    @pyqtSlot()
    def update_max_min_stone_columns_variables(self, item, column):
        """ Updates min/max values for design variables of stone columns
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        if self.variables_stone_columns:
            key = item.text(1)  # key (located at column 1 of the changed child item)
            if (column > 0) and (item.text(column) is not ''):
                # get stone columns id
                sc_id = item.parent().text(0).split('_')[1]    # the considered stone columns id
                for i, variables_sc in enumerate(self.variables_stone_columns): # loop over variables for each of stone columns structure
                    if sc_id + '_SC' in variables_sc.keys():
                        if column == 3:
                            value = float(item.text(column))
                            self.variables_stone_columns_min[i][sc_id + '_SC'][key] = value
                        elif column == 4:
                            value = float(item.text(column))
                            self.variables_stone_columns_max[i][sc_id + '_SC'][key] = value

    @pyqtSlot()
    def update_subset_stone_columns_variables(self, item, column):
        """ Updates subset values for design variables of stone columns
        This slot is called upon change of values in treewidget.
        """
        key = item.text(1)  # key (located at column 1 of the changed child item)
        #if (column > 0) and (item.text(column) != ''): 
        if column > 0:
            sc_id = item.parent().text(0).split('_')[1]    # the considered stone columns id
            for i, variables_sc in enumerate(self.variables_stone_columns): # loop over variables for each of the ground anchors
                if sc_id + '_SC' in variables_sc.keys():
                    if column == 5:
                        try:
                            values_text = item.text(column)
                            self.variables_stone_columns_subset[i][sc_id + '_SC'][key] = [float(value) for value in values_text.split(',')]
                        except ValueError:
                            self.variables_stone_columns_subset[i][sc_id + '_SC'][key] = []


    @pyqtSlot()
    def update_max_min_fdc_variables(self, item, column):
        """ Updates min/max values for design variables of stone columns
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        if self.variables_fdc:
            key = item.text(1)  # key (located at column 1 of the changed child item)
            if (column > 0) and (item.text(column) is not ''):
                # get stone columns id
                sc_id = item.parent().text(0).split('_')[1]    # the considered stone columns id
                for i, variables_sc in enumerate(self.variables_fdc): # loop over variables for each of rigid inclusions
                    if sc_id + '_FDC' in variables_sc.keys():
                        if column == 3:
                            value = float(item.text(column))
                            self.variables_fdc_min[i][sc_id + '_FDC'][key] = value
                        elif column == 4:
                            value = float(item.text(column))
                            self.variables_fdc_max[i][sc_id + '_FDC'][key] = value


    @pyqtSlot()
    def update_subset_fdc_variables(self, item, column):
        """ Updates subset values for design variables of rigid inclusions
        This slot is called upon change of values in treewidget.
        """
        key = item.text(1)  # key (located at column 1 of the changed child item)
        #if (column > 0) and (item.text(column) != ''): 
        if column > 0:
            sc_id = item.parent().text(0).split('_')[1]    # the considered stone columns id
            for i, variables_sc in enumerate(self.variables_fdc): # loop over variables for each of rigid inclusions
                if sc_id + '_FDC' in variables_sc.keys():
                    if column == 5:
                        try:
                            values_text = item.text(column)
                            self.variables_fdc_subset[i][sc_id + '_FDC'][key] = [float(value) for value in values_text.split(',')]
                        except ValueError:
                            self.variables_fdc_subset[i][sc_id + '_FDC'][key] = []


    @pyqtSlot()
    def update_objectives_WallUx(self, checked):
        """ Updates objectives for design optimization
        """
        if checked:
            self.objectives['Max WallUx'] = 0.0
        else:
            del self.objectives['Max WallUx']
        # Add items to Sentivity
        self.ui.comboBox_40.blockSignals(True)
        self.ui.comboBox_40.clear()
        for key in self.objectives.keys():
            self.ui.comboBox_40.addItem(key)
        self.ui.comboBox_40.blockSignals(False)


    @pyqtSlot()
    def update_objectives_WallUy(self, checked):
        """ Updates objectives for design optimization
        """
        if checked:
            self.objectives['Max WallUy'] = 0.0
        else:
            del self.objectives['Max WallUy']
        # Add items to Sentivity
        self.ui.comboBox_40.blockSignals(True)
        self.ui.comboBox_40.clear()
        for key in self.objectives.keys():
            self.ui.comboBox_40.addItem(key)
        self.ui.comboBox_40.blockSignals(False)


    @pyqtSlot()
    def update_objectives_SoilUy(self, checked):
        """ Updates objectives for design optimization
        """
        if checked:
            self.objectives['Max SoilUy'] = 0.0
        else:
            del self.objectives['Max SoilUy']
        # Add items to Sentivity
        self.ui.comboBox_40.blockSignals(True)
        self.ui.comboBox_40.clear()
        for key in self.objectives.keys():
            self.ui.comboBox_40.addItem(key)
        self.ui.comboBox_40.blockSignals(False)


    @pyqtSlot()
    def update_objectives_FoS(self, checked):
        """ Updates objectives for design optimization
        """
        if checked:
            self.objectives['FoS'] = 0.0
        else:
            del self.objectives['FoS']
        # Add items to Sentivity
        self.ui.comboBox_40.blockSignals(True)
        self.ui.comboBox_40.clear()
        for key in self.objectives.keys():
            self.ui.comboBox_40.addItem(key)
        self.ui.comboBox_40.blockSignals(False)


    def go_to_sensitivity(self):
        """ Goes to sensitivity analysis for design optimization
        """
        self.setup_sensitivity()
        self.ui.tabWidget_7.setCurrentIndex(1)
        # fill self.objectives_WallNxMQ_Envelope in Objective combobox
        #checked = (self.ui.checkBox_12.checkState() == 2)
        #self.update_objectives_WallUx(checked)
        self.ui.comboBox_40.blockSignals(True)
        for key in self.objectives_WallNxMQ_Envelope.keys():
            self.ui.comboBox_40.addItem(key)
        self.ui.comboBox_40.blockSignals(False)


    def setup_sensitivity(self):
        """ Transfer settings to optiman_sensitivity
        """
        self.v0, self.v_min, self.v_max, self.v_subset = self.merg_design_variables()
        self.ratio_perturbation_sensitivity = float(self.ui.lineEdit_72.text())
        v_min = self.v0 - self.ratio_perturbation_sensitivity*self.v0
        v_max = self.v0 + self.ratio_perturbation_sensitivity*self.v0

        # show on table
        self.ui.tableWidget_21.setColumnCount(self.v0.size)
        self.ui.tableWidget_21.setRowCount(3)
        param_labels = ['v' + str(param_cnt + 1) for param_cnt in range(self.v0.size)]
        row_labels = ['v_min', 'v0', 'v_max']
        self.ui.tableWidget_21.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_21.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.v0.size):
            self.ui.tableWidget_21.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(v_min[column_j])))
            self.ui.tableWidget_21.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.v0[column_j])))
            self.ui.tableWidget_21.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(v_max[column_j])))


    def start_local_sensitivity(self):
        """ Starts generating database and calculates local sensitivity scores
        """
        from workflow1.optiman_sensitivity import OptimanSensitivity
        OptimanSensitivity.plaxman_ap = self.plaxman_ap     # class attribute

        self.local_sensitivity = OptimanSensitivity(self.variables_wall, self.variables_anchors, self.variables_struts, self.v0, self.v_min, self.v_max, self.plaxman_ap.Points_obs, objectives=self.objectives)
        #self.local_sensitivity.plaxman_ap = self.plaxman_ap     # instance attribute

        # checking if required data are ready
        if self.local_sensitivity.check() == int(1):
            self.dialog.show_message_box('Error', 'Please add at least one set of observation points in Plaxman\\Outputs!')
            return None
        elif self.local_sensitivity.check() == int(2):
            self.dialog.show_message_box('Error', 'Please add at least one set of observation points for WallNxMQ_Envelope in Plaxman\\Outputs!')
            return None

        # set up local sensitivity analysis
        self.local_sensitivity.setup()

        # generate finite-difference samples (input)
        self.local_sensitivity.generate_input_samples()
        self.ui.label_108.setText('Database file: {0}, number of samples: {1}'.format(self.local_sensitivity.path_output, self.local_sensitivity.iter_max))


        # start calculations
        #self.local_sensitivity.iterate()  # for debugging

        self.run_thread = RunThreadIter(workflow=self.local_sensitivity) # note, run_thread which does not belong to self fails
        print('\nSTARTING OUTPUT DATABASE GENERATION FOR SENSTIVITY ANALYSIS...')
        self.run_thread.start()
        self.run_thread.run_percentage.connect(lambda percentage: self.display_run_progress(percentage, self.ui.progressBar_5))
        self.run_thread.allDone.connect(lambda: self.report_local_sensitivity_scores('Max WallUx'))


    def stop_local_sensitivity(self):
        """ Stops generating FEM output database
        """
        print('\nSTOPPING OUTPUT DATABASE GENERATION FOR SENSTIVITY ANALYSIS...')
        self.run_thread.stop()


    def resume_local_sensitivity(self):
        """ resumes generating FEM output database
        """
        print('\nRESUMING OUTPUT DATABASE GENERATION FOR SENSTIVITY ANALYSIS...')
        self.run_thread.start()



    def display_run_progress(self, percentage, progress_bar):
        """ Displays run progress on progress bar
        """
        progress_bar.setValue(percentage)
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        print('Generating data for sample {0}/{1} with parameter set {2}'.format(self.run_thread.worklflow.iter + 1, self.run_thread.worklflow.iter_max, self.run_thread.worklflow.v))



    @pyqtSlot()
    def report_local_sensitivity_scores(self, objective_text):
        """ Reports local sensitivity scores
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
        SENSITIVITY = os.path.join(OPTIMAN, 'sensitivity')

        # update path to sensitivity 
        self.local_sensitivity.path_output = SENSITIVITY

        # which vector norm
        vector_norm = 'L2'

        try:
            # plot sensitivity scores
            if objective_text == 'Max WallUx':
                # calculate sensitivity scores for all data
                scores = self.local_sensitivity.calc_sensitivity_objective_WallUx(vector_norm=vector_norm)
            elif objective_text == 'FoS':
                scores = self.local_sensitivity.calc_sensitivity_objective_FoS(vector_norm=vector_norm)
            elif objective_text == 'Cost':
                scores = self.local_sensitivity.calc_sensitivity_objective_Cost(vector_norm=vector_norm)
            elif objective_text == 'Wall Nx':
                scores = self.local_sensitivity.calc_sensitivity_objective_WallNx(vector_norm=vector_norm)
            elif objective_text == 'Wall M':
                scores = self.local_sensitivity.calc_sensitivity_objective_WallM(vector_norm=vector_norm)
            elif objective_text == 'Wall Q':
                scores = self.local_sensitivity.calc_sensitivity_objective_WallQ(vector_norm=vector_norm)
            
            print('{0} sensitivity scores: {1}'.format(objective_text, 100*scores/np.sum(scores)))
            path_scores = os.path.join(OPTIMAN, 'sensitivity', 'sensitivity_scores')
            savetxt(path_scores, scores)
            self.plot_canvas_sensitivity.plot_sensitivity_scores_optiman(scores, objective_text)
            self.sensitivity_scores[objective_text] = scores

        except FileNotFoundError:
            print('No scores found!')


    def merg_design_variables(self):
        """ Merges design variables into one numpy array
        """
        v0 = []
        v_min = []
        v_max = []
        v_subset = []

        v0_wall = [value for key, value in self.variables_wall.items() if key != 'id']
        v_min_wall = [value for key, value in self.variables_wall_min.items() if key != 'id']
        v_max_wall = [value for key, value in self.variables_wall_max.items() if key != 'id']
        v_subset_wall = [value for key, value in self.variables_wall_subset.items() if key != 'id']

        v0.append(list(v0_wall))
        v_min.append(list(v_min_wall))
        v_max.append(list(v_max_wall))
        v_subset.append(list(v_subset_wall))

        # variables for anchors
        for variables_anchor in self.variables_anchors:
            v0_anchor = list(list(variables_anchor.values())[0].values())
            v0.append(v0_anchor)
        for variables_anchor_min in self.variables_anchors_min:
            v_min_anchor = list(list(variables_anchor_min.values())[0].values())
            v_min.append(v_min_anchor)
        for variables_anchor_max in self.variables_anchors_max:
            v_max_anchor = list(list(variables_anchor_max.values())[0].values())
            v_max.append(v_max_anchor)
        for variables_anchor_subset in self.variables_anchors_subset:
            v_subset_anchor = list(list(variables_anchor_subset.values())[0].values())
            v_subset.append(v_subset_anchor)

        # variables for struts
        for variables_strut in self.variables_struts:
            v0_strut = list(list(variables_strut.values())[0].values())
            v0.append(v0_strut)
        for variables_strut_min in self.variables_struts_min:
            v_min_strut = list(list(variables_strut_min.values())[0].values())
            v_min.append(v_min_strut)
        for variables_strut_max in self.variables_struts_max:
            v_max_strut = list(list(variables_strut_max.values())[0].values())
            v_max.append(v_max_strut)
        for variables_strut_subset in self.variables_struts_subset:
            v_subset_strut = list(list(variables_strut_subset.values())[0].values())
            v_subset.append(v_subset_strut)

        # variables for stone columns
        for variables_sc in self.variables_stone_columns:
            v0_sc = list(list(variables_sc.values())[0].values())
            v0.append(v0_sc)
        for variables_sc_min in self.variables_stone_columns_min:
            v_min_sc = list(list(variables_sc_min.values())[0].values())
            v_min.append(v_min_sc)
        for variables_sc_max in self.variables_stone_columns_max:
            v_max_sc = list(list(variables_sc_max.values())[0].values())
            v_max.append(v_max_sc)
        for variables_sc_subset in self.variables_stone_columns_subset:
            v_subset_sc = list(list(variables_sc_subset.values())[0].values())
            v_subset.append(v_subset_sc)

        # variables for rigid inclusions
        for variables_ in self.variables_fdc:
            v0_ = list(list(variables_.values())[0].values())
            v0.append(v0_)
        for variables_min in self.variables_fdc_min:
            v_min_ = list(list(variables_min.values())[0].values())
            v_min.append(v_min_)
        for variables_max in self.variables_fdc_max:
            v_max_ = list(list(variables_max.values())[0].values())
            v_max.append(v_max_)
        for variables_subset in self.variables_fdc_subset:
            v_subset_ = list(list(variables_subset.values())[0].values())
            v_subset.append(v_subset_)

        v0_flat = [item for sublist in v0 for item in sublist]
        v_min_flat = [item for sublist in v_min for item in sublist]
        v_max_flat = [item for sublist in v_max for item in sublist]
        v_subset_flat = [item for sublist in v_subset for item in sublist]

        return np.array(v0_flat), np.array(v_min_flat), np.array(v_max_flat), np.array(v_subset_flat)


    def go_to_metamodeling(self):
        """ Goes to NSGAII
        """
        self.setup_metamodeling()
        self.ui.tabWidget_7.setCurrentIndex(2)


    def setup_metamodeling(self):
        """ Transfer settings to optiman_sensitivity
        """
        self.v0, self.v_min, self.v_max, self.v_subset = self.merg_design_variables()

        # show on table
        self.ui.tableWidget_24.setColumnCount(self.v0.size)
        self.ui.tableWidget_24.setRowCount(3)
        param_labels = ['v' + str(param_cnt + 1) for param_cnt in range(self.v0.size)]
        row_labels = ['v_min', 'v0', 'v_max']
        self.ui.tableWidget_24.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_24.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.v0.size):
            self.ui.tableWidget_24.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.v_min[column_j])))
            self.ui.tableWidget_24.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.v0[column_j])))
            self.ui.tableWidget_24.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(self.v_max[column_j])))


    def generate_database_input(self):
        """ Genertates (random) database input
        """
        # Sample the parameter space (LHS method)
        try:
            num_points = int(self.ui.lineEdit_70.text())

            from workflow1.optiman_metamodeling import OptimanMetamodeling
            self.rnd_samples_input_file = OptimanMetamodeling.generate_input_samples(self.v_min, self.v_max, num_points)

            self.ui.label_119.setText('Database file: {0}, number of samples: {1}'.format(self.rnd_samples_input_file, num_points))

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if number of points is correctly entered!')


    def load_existing_database_input(self):
        """ Loads existing database (input) file
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
        METAMODEL = os.path.join(OPTIMAN, 'metamodel')
        data_file, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Select data file', METAMODEL)
        if data_file:
            try:
                self.rnd_samples_input_file = data_file.replace("/", "\\")
                samples_input = np.loadtxt(self.rnd_samples_input_file)
                self.ui.label_119.setText('Database file: {0}; number of samples: {1}'.format(self.rnd_samples_input_file, samples_input.shape[0]))

            except ValueError:
                self.dialog.show_message_box('Error', 'Data file fails to load. Please check your data!')


    def start_generate_database_output(self):
        """ Generates FEM database for metamodeling by running Plaxis2D calculations
        """
        from workflow1.optiman_metamodeling import OptimanMetamodeling

        if not self.rnd_samples_input_file:
            self.dialog.show_message_box('Warning', 'Please generate or load your randomly sampled points!')

        else:

            OptimanMetamodeling.plaxman_ap = self.plaxman_ap     # class attribute

            # set constraint items
            constraint_items = self.set_constraints()

            # initialize metamodeling workflow
            iter_ = int(self.ui.lineEdit_71.text())
            self.meta = OptimanMetamodeling(self.variables_wall, self.variables_anchors, self.variables_struts, self.v0, self.v_min, self.v_max, self.plaxman_ap.Points_obs, self.objectives, constraint_items, iter_)
            self.meta.setup()

            # load samples from input file and assign
            samples_input = np.loadtxt(self.rnd_samples_input_file)
            self.meta.set_input_samples(samples_input)

            # run 
            self.run_thread = RunThreadIter(workflow=self.meta) # note, run_thread which does not belong to self fails
            #for _ in range(3):      # for debugging
            #    self.meta.iterate()    # for debugging
            print('\nSTARTING OUTPUT DATABASE GENERATION AT SAMPLE {}...'.format(iter_ + 1))
            self.run_thread.start()
            self.run_thread.run_percentage.connect(lambda percentage: self.display_run_progress(percentage, self.ui.progressBar_6))


    def stop_generate_database_output(self):
        """ Stops generating output database
        """
        print('\nSTOPPING OUTPUT DATABASE GENERATION AT SAMPLE {}...'.format(self.run_thread.worklflow.iter + 1))
        self.run_thread.stop()
    

    def resume_generate_database_output(self):
        """ Resumes FEM database generations
        """
        print('\nRESUMING OUTPUT DATABASE GENERATION FROM SAMPLE {}...'.format(self.run_thread.worklflow.iter + 1))
        self.run_thread.start()



    def start_check_legal_samples(self):
        """ Check the rate of legal samples from the randomly generated samples
        This is good to do before generating output database by Plaxis2D calculations
        """
        from workflow1.optiman_metamodeling import OptimanMetamodeling

        if not self.rnd_samples_input_file:
            self.dialog.show_message_box('Warning', 'Please generate or load your randomly sampled points!')

        else: 
            OptimanMetamodeling.plaxman_ap = self.plaxman_ap     # class attribute

            # set constraint items
            constraint_items = self.set_constraints()

            # initialize metamodeling workflow
            self.meta = OptimanMetamodeling(self.variables_wall, self.variables_anchors, self.variables_struts, self.v0, self.v_min, self.v_max, self.Points_obs, self.objectives, constraint_items, iter_=0, check_legal_only=True)
            self.meta.setup()

            # load samples from input file and assign
            samples_input = np.loadtxt(self.rnd_samples_input_file)
            self.meta.set_input_samples(samples_input)

            # run 
            self.run_thread_meta = RunThreadIter(workflow=self.meta) # note, run_thread which does not belong to self fails
            #self.meta.iterate() # for debugging
            print('\nSTARTING CHECKING RANDOM SAMPLES AGAINST CONSTRAINTS')
            self.run_thread_meta.start()
            self.run_thread_meta.iter_isDone.connect(self.report_sample_legality)
            self.run_thread_meta.allDone.connect(self.report_sample_legality_final)


    def stop_check_legal_samples(self):
            """ Stops checking
            """
            print('\nSTOPPING CHECKING RANDOM SAMPLES AGIANST CONSTRAINTS')
            print('Current legal rate is {0:0.3f}'.format(self.run_thread_meta.worklflow.number_iter_success/(self.run_thread_meta.worklflow.iter)))
            self.run_thread_meta.stop()
            #time.sleep(1)
            #del self.run_thread_meta


    def report_sample_legality(self):
        """ Prints on the legality of the current samples
        """
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        print('Checking legality for sample {0}/{1} with parameter set {2}: legal is {3}. Current legal rate is {4:0.3f}'.format(
            self.run_thread_meta.worklflow.iter + 1, self.run_thread_meta.worklflow.iter_max, self.run_thread_meta.worklflow.v, 
            (self.run_thread_meta.worklflow.constraints_value==0), self.run_thread_meta.worklflow.number_iter_success/(self.run_thread_meta.worklflow.iter)))


    def report_sample_legality_final(self):
        """ Prints final legality rate for the generated random samples
        """
        print('RESULT: {0} out of {1} samples are legal'.format(self.run_thread_meta.worklflow.number_iter_success, self.run_thread_meta.worklflow.iter_max))


    def go_to_nsga2(self):
        """ Goes to NSGAII
        """
        self.setup_nsga2()
        self.ui.tabWidget_7.setCurrentIndex(3)
        #print(self.objectives)


    def setup_nsga2(self):
        """ Transfer settings to optiman_sensitivity
        """
        self.v0, self.v_min, self.v_max, self.v_subset = self.merg_design_variables()

        # show on table
        self.ui.tableWidget_27.setColumnCount(self.v_min.size)
        self.ui.tableWidget_27.setRowCount(3)
        param_labels = ['v' + str(param_cnt + 1) for param_cnt in range(self.v_min.size)]
        row_labels = ['v_min', 'v_max', 'v_subset']
        self.ui.tableWidget_27.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_27.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.v_min.size):
            self.ui.tableWidget_27.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.v_min[column_j])))
            self.ui.tableWidget_27.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.v_max[column_j])))
            self.ui.tableWidget_27.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(self.v_subset[column_j])))

        # clear grapth for pareto's front
        self.plot_canvas_objectives.axes.cla()
        self.plot_canvas_objectives.draw()


    def set_constraints(self):
        """ Prepares constraints for design optimization
        """
        constraint_items = {}
        # min/ max distance between ground anchors
        d_anchor_min = float(self.ui.lineEdit_56.text())
        d_anchor_max = float(self.ui.lineEdit_61.text())
        constraint_items['anchor_distance'] = (d_anchor_min, d_anchor_max)

        if self.plaxman_ap.active_earth_pressure_wedge:
            constraint_items['active_earthpressure_points'] = self.plaxman_ap.active_earth_pressure_wedge['points']

        # min/max spacing between stone columns
        a_sc_min = float(self.ui.lineEdit_79.text())
        a_sc_max = float(self.ui.lineEdit_80.text())
        constraint_items['stone_columns_spacing'] = (a_sc_min, a_sc_max)
        constraint_items['fdc_spacing'] = (a_sc_min, a_sc_max)

        return constraint_items


    def load_initial_population(self):
        """ Loads an initial population
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        #OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
        #METAMODEL = os.path.join(OPTIMAN, 'metamodel')
        data_file, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Select data file', MONIMAN_OUTPUTS)
        if data_file:
            try:
                self.rnd_samples_input_file = data_file.replace("/", "\\")
                self.initial_population = np.loadtxt(self.rnd_samples_input_file)

            except ValueError:
                self.dialog.show_message_box('Error', 'Data file fails to load. Please check your data!')


    def start_nsga2(self):
        """ Starts generating multi-objective optimization using NSGAII
        """
        from workflow1.optiman_nsga2 import Optiman_NSGAII
        from workflow1.optiman_nsga3 import Optiman_NSGAIII
        from optimize.platypus_wrapper.problem_nsga2 import Problem_Wrapper             # retaining wall problem
        from optimize.platypus_wrapper.problem_sc_nsga2 import Problem_SC_Wrapper       # stone columns problem
        from optimize.platypus_wrapper.problem_fdc_nsga2 import Problem_FDC_Wrapper     # rigid inclusions problem

        if self.plaxman_ap.Points_obs:
            # checking if required data are ready
            obs_types = [obs_set['obs_type'] for obs_set in self.plaxman_ap.Points_obs]
            if 'WallNxMQ_Envelope' not in obs_types:
                self.dialog.show_message_box('Error', 'Please add at least one set of observation points for WallNxMQ_Envelope in Plaxman\\Outputs!')
                return None

            # set constraint items
            constraint_items = self.set_constraints()
            if self.variables_stone_columns:    # Optimization for stone columns
                self.optiman_problem = Problem_SC_Wrapper(self.variables_stone_columns, self.v0, self.v_min, self.v_max, self.v_subset, self.objectives, constraint_items, self.plaxman_ap)
            elif self.variables_fdc:    # Optimization for rigid inclusions
                self.optiman_problem = Problem_FDC_Wrapper(self.variables_fdc, self.v0, self.v_min, self.v_max, self.v_subset, self.objectives, constraint_items, self.plaxman_ap)
            else:                               # Optimization for retaining wall
                self.optiman_problem = Problem_Wrapper(self.variables_wall, self.variables_anchors, self.variables_struts, self.v0, self.v_min, self.v_max, self.v_subset, self.objectives, constraint_items, self.plaxman_ap)

            self.n_generation = int(self.ui.lineEdit_68.text())
            self.n_population = int(self.ui.lineEdit_69.text())
            self.n_outer_divisions = int(self.ui.lineEdit_83.text().split(',')[0])
            self.n_inner_divisions = int(self.ui.lineEdit_83.text().split(',')[1])
            if self.ui.radioButton_8.isChecked():   #algorithm = 'NSGAII'
                self.optiman_nsga = Optiman_NSGAII(self.optiman_problem, self.n_population, self.n_generation, initial_population=self.initial_population)
            elif self.ui.radioButton_9.isChecked(): #algorithm = 'NSGAIII'
                self.optiman_nsga = Optiman_NSGAIII(self.optiman_problem, self.n_outer_divisions, self.n_inner_divisions, self.n_generation, initial_population=self.initial_population)

            # check initial population size
            if self.optiman_nsga.check_initial_population_size() is False:
                #self.dialog.show_message_box('Error', 'Please add at least one set of observation points in Plaxman\\Outputs!')
                self.dialog.show_message_box('Warning', 'The defined population size does not match with that of the initial population!')
                return None

            # set up optimization workflow
            self.optiman_nsga.setup()

            ## start calculations
            #for _ in range(3): # for debugging
            #    self.optiman_nsga.iterate()  # for debugging

            self.run_thread = RunThreadIter(workflow=self.optiman_nsga) # note, run_thread which does not belong to self fails
            print('\nSTARTING DESIGN OPTIMIZATION USING {0} WITH POPULATION SIZE {1}...'.format(self.optiman_nsga.algorithm_name, self.optiman_nsga.algorithm.population_size))
            self.run_thread.start()
            self.run_thread.run_percentage.connect(lambda percentage: self.display_run_progress_nsga2(percentage, self.ui.progressBar_7))
            self.run_thread.iter_isDone.connect(self.report_iterative_results)

        else:
            self.dialog.show_message_box('Warning', 'Please add observation points for wall deflection and internal forces!')


    def display_run_progress_nsga2(self, percentage, progress_bar):
        """ Displays run progress on progress bar
        """
        progress_bar.setValue(percentage)


    def report_iterative_results(self, picker_size=0.0, solutions=None):
        """ Reports current optimization result
        picker_size = 0, no picking of point is allowed.
        """
        print('Generation# ', self.optiman_nsga.iter)
        np.set_printoptions(precision=3)
        for solution in self.optiman_nsga.algorithm.result:
            print('Variables: {0}, Objectives: {1}'.format(np.array(list(flatten_list(solution.variables))), np.array(solution.objectives)))

        # plot current objectives
        costs = [solution.objectives[0] for solution in self.optiman_nsga.algorithm.result]
        disps = [solution.objectives[1] for solution in self.optiman_nsga.algorithm.result]
        solutions = [list(flatten_list(solution.variables)) for solution in self.optiman_nsga.algorithm.result]
        solutions = np.array(solutions)
        if self.optiman_nsga.iter == self.optiman_nsga.iter_max:
            picker_size = 5.0   # by default, allow to pick when final iteration is completed
        self.plot_canvas_objectives.plot_objectives_2d(disps, costs, self.optiman_nsga.iter, alpha=1.0, picker_size=picker_size, plaxman_ap=self.plaxman_ap, solutions=solutions,
                                                        variables_wall=self.variables_wall, variables_anchors=self.variables_anchors, variables_struts=self.variables_struts,
                                                        variables_stone_columns=self.variables_stone_columns, variables_fdc=self.variables_fdc)

        # plot last objectives
        if self.optiman_nsga.iter > 2:
        	MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        	OPTIMAN = os.path.join(MONIMAN_OUTPUTS, 'optiman')
        	NSGAII_PATH = os.path.join(OPTIMAN, 'nsga2')
        	objectives_last = np.loadtxt(os.path.join(NSGAII_PATH, 'gen_' + str(self.optiman_nsga.iter-1).zfill(4), 'objectives'))
        	objectives_last_1 = np.loadtxt(os.path.join(NSGAII_PATH, 'gen_' + str(self.optiman_nsga.iter-2).zfill(4), 'objectives'))
        	self.plot_canvas_objectives.plot_objectives_2d(objectives_last[:, 1], objectives_last[:,0], self.optiman_nsga.iter-1, 'green', False, marker='^')
        	self.plot_canvas_objectives.plot_objectives_2d(objectives_last_1[:, 1], objectives_last_1[:, 0], self.optiman_nsga.iter-2, 'blue', False, marker='^')

        # assign solutions to class attribute
        objectives = [solution.objectives for solution in self.optiman_nsga.algorithm.result]
        self.solutions_nsga = solutions
        self.objectives_nsga = objectives
        self.iter_nsga = self.optiman_nsga.iter


    def stop_nsga2(self):
        """ Stops nsga2
        Stop event will also allow to pick the solution on the graph for objectives (by setting pick_size)
        """
        print('\nSTOPPING {0} AT ITERATION {1}...'.format(self.optiman_nsga.algorithm_name, self.optiman_nsga.iter))
        self.run_thread.stop()
        if self.optiman_nsga.algorithm.result:
            try:
                solutions = [list(flatten_list(solution.variables)) for solution in self.optiman_nsga.algorithm.result]
                solutions = np.array(solutions)
                self.plot_canvas_objectives.fig.canvas.mpl_disconnect(self.plot_canvas_objectives.cid) # disconnect matplotlib's pick event
                self.report_iterative_results(picker_size=5, solutions=solutions)

                # assign solutions/objectives to class attribute
                objectives = [solution.objectives for solution in self.optiman_nsga.algorithm.result]
                self.solutions_nsga = solutions
                self.objectives_nsga = objectives
                self.iter_nsga = self.optiman_nsga.iter
            except:
                pass


    def resume_nsga2(self):
        """ Resumes nsga2
        """
        print('\nRESUMING {0} FROM ITERATION {1}...'.format(self.optiman_nsga.algorithm_name, self.optiman_nsga.iter))
        self.run_thread.start()


    def view_pareto_front(self):
        """ Opens Pareto front viewer
        """
        if self.objectives_nsga:
            costs = [objective[0] for objective in self.objectives_nsga]
            displs = [objective[1] for objective in self.objectives_nsga]
            self.form.open_pareto_front_viewer(displs, costs)


    def save(self):
        """ Saves Optiman
        """
        objs = (self.wall, self.final_excavation_level, 
        self.variables_wall, self.variables_wall_min, self.variables_wall_max, self.variables_wall_subset,
        self.variables_anchors, self.variables_anchors_min, self.variables_anchors_max, self.variables_anchors_subset,
        self.variables_struts, self.variables_struts_min, self.variables_struts_max, self.variables_struts_subset,
        self.local_sensitivity, self.objectives, self.v0, self.v_min, self.v_max, self.v_subset,
        self.sensitivity_scores, self.solutions_nsga, self.objectives_nsga, self.iter_nsga, self.ratio_perturbation_sensitivity, 
        self.n_generation, self.n_population, self.variables_stone_columns, self.variables_stone_columns_max, self.variables_stone_columns_min, self.variables_stone_columns_subset, 
        self.variables_fdc, self.variables_fdc_max, self.variables_fdc_min, self.variables_fdc_subset, self.unit_costs)

        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'optiman_state.mon')
        saveobjs(filename, *objs)
        print("Optiman's state is saved in {}".format(filename))


    def load(self):
        """ Loads Optiman
        """
        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'optiman_state.mon')
        if not isfile(filename):
            self.dialog.show_message_box('Error', 'File {} does not exist for loading'.format(filename))
        else:
            try:
                (self.wall, self.final_excavation_level,
                self.variables_wall, self.variables_wall_min, self.variables_wall_max, self.variables_wall_subset,
                self.variables_anchors, self.variables_anchors_min, self.variables_anchors_max, self.variables_anchors_subset,
                self.variables_struts, self.variables_struts_min, self.variables_struts_max, self.variables_struts_subset,
                self.local_sensitivity, self.objectives, self.v0, self.v_min, self.v_max, self.v_subset,
                self.sensitivity_scores, self.solutions_nsga, self.objectives_nsga, self.iter_nsga, self.ratio_perturbation_sensitivity, 
                self.n_generation, self.n_population, self.variables_stone_columns, self.variables_stone_columns_max, self.variables_stone_columns_min, self.variables_stone_columns_subset, 
                self.variables_fdc, self.variables_fdc_max, self.variables_fdc_min, self.variables_fdc_subset, self.unit_costs) = loadobjs(filename)
            except: # load an old project
                (self.wall, self.final_excavation_level,
                self.variables_wall, self.variables_wall_min, self.variables_wall_max, self.variables_wall_subset,
                self.variables_anchors, self.variables_anchors_min, self.variables_anchors_max, self.variables_anchors_subset,
                self.variables_struts, self.variables_struts_min, self.variables_struts_max, self.variables_struts_subset,
                self.local_sensitivity, self.objectives, self.v0, self.v_min, self.v_max, self.v_subset,
                self.sensitivity_scores, self.solutions_nsga, self.objectives_nsga, self.iter_nsga, self.ratio_perturbation_sensitivity, 
                self.n_generation, self.n_population, self.variables_stone_columns, self.variables_stone_columns_max, self.variables_stone_columns_min, self.variables_stone_columns_subset, 
                self.variables_fdc, self.variables_fdc_max, self.variables_fdc_min, self.variables_fdc_subset) = loadobjs(filename)
                #self.variables_fdc, self.variables_fdc_max, self.variables_fdc_min, self.variables_fdc_subset, self.unit_costs) = loadobjs(filename)
            
            self.display_all_model_components()
   
            loadOptiman.add_wall_variables(self.ui, self.wall, self.variables_wall, self.variables_wall_min, self.variables_wall_max, self.variables_wall_subset)
            loadOptiman.add_anchor_variables(self.ui, self.variables_anchors, self.variables_anchors_min, self.variables_anchors_max, self.variables_anchors_subset, self.variables_wall, self.variables_struts)
            loadOptiman.add_strut_variables(self.ui, self.variables_struts, self.variables_struts_min, self.variables_struts_max, self.variables_struts_subset, self.variables_wall, self.variables_anchors)
            loadOptiman.add_stone_columns_variables(self.ui, self.variables_stone_columns, self.variables_stone_columns_min, self.variables_stone_columns_max, self.variables_stone_columns_subset, self.variables_wall, self.variables_anchors, self.variables_struts)
            loadOptiman.add_fdc_variables(self.ui, self.variables_fdc, self.variables_fdc_min, self.variables_fdc_max, self.variables_fdc_subset, self.variables_wall, self.variables_anchors, self.variables_struts)
            #loadOptiman.add_active_earthpressure_wedge(self.ui, self.plot_canvas, self.active_earth_pressure_wedge)
            if self.variables_anchors:
                loadOptiman.display_anchor_competent_soil_layers(self.ui, self.plaxman_ap.Layer_polygons)
            loadOptiman.add_objectives(self.ui, self.objectives)
            #loadOptiman.add_table_design_variables(self.ui, self.v0, self.v_min, self.v_max)
            self.ui.lineEdit_72.setText(str(self.ratio_perturbation_sensitivity))
            if type(self.v0).__module__ == 'numpy':
                loadOptiman.add_table_design_variables(self.ui.tableWidget_21, self.v0, self.v0 - self.v0*self.ratio_perturbation_sensitivity, self.v0 + self.v0*self.ratio_perturbation_sensitivity) # table in Sensitivity
            loadOptiman.show_sensitivity_scores(self.ui, self.plot_canvas_sensitivity, self.sensitivity_scores, self.local_sensitivity)
            loadOptiman.add_table_design_variables(self.ui.tableWidget_24, self.v0, self.v_min, self.v_max) # table in Metamodeling
            self.ui.lineEdit_68.setText(str(self.n_generation))
            self.ui.lineEdit_69.setText(str(self.n_population))

            #self.ui.widget_7.InstallEventFilter(self)
            #QtWidgets.QApplication.processEvents()
            #loadOptiman.show_optimization_results(self.ui, self.plot_canvas_objectives) # for debugging
            if self.solutions_nsga is not None:
                loadOptiman.show_optimization_results(self.ui, self.plot_canvas_objectives, self.plaxman_ap, self.variables_wall, self.variables_anchors, self.variables_struts, self.variables_stone_columns, self.variables_fdc, self.solutions_nsga, self.objectives_nsga, self.iter_nsga)
            loadOptiman.add_table_design_variables_nsga2(self.ui.tableWidget_27, self.v_min, self.v_max, self.v_subset) # table in NSGA-II

            print("Optiman's state saved in file '{}' is loaded".format(filename))
