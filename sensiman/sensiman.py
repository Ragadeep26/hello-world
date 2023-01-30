# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 14:51:03 2019

@author: nya
"""
import sys, os
import glob
from os.path import isfile
import numpy as np
import copy
from collections import OrderedDict
import pickle
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from tools.file_tools import savetxt
from tools.file_tools import saveobjs, loadobjs
from system.run_thread import RunThreadIter
from sensiman.sensiman_load import loadSensiman
from gui.gui_main_matplotlib import MyStaticMplCanvas 
#from optimize.gp import GaussianProcess
from tools.json_functions import read_data_in_json_item
from solver.plaxis2d.parameter_relations import (get_HS_moduli, set_plaxis_datatypes, get_HSsmall_G0ref, 
                                            get_HS_K0nc_empirical, get_SPW_parameters, get_CPW_parameters,
                                            get_Eref_CPW, get_Eref_SPW, get_Eref_Dwall)

from workflow1.metamodeling_data_generation import Metamodeling
from workflow1.sensitivity_local import LocalSensitivity

from system.run_thread import RunThreadSingle

class Sensiman():
    def __init__(self, plaxman=None):
        """ Initializes Sensiman attributes
        """
        self.plaxman = plaxman
        self.ui = plaxman.ui
        self.dialog = plaxman.dialog
        self.form = plaxman.form
        
        self.m0 = None                  # current parameter values
        self.m_min = None               # min parameter values
        self.m_max = None               # max parameter values
        
        self.Parameters = []            # soil parameters
        self.Parameters_wall = []       # wall parameters
        self.Parameters_strut = []      # strut parameters

        self.local_sensitivity = None
        self.sensitivity_scores = {}
        self.ratio_perturbation_sensitivity = 0.1  # ratio for perturbation of design variables in sensitivity analysis

        self.samples = {}                           # random samples for training/validation
        self.samples['paths_data_train'] = []       # paths to training data
        self.samples['paths_data_validate'] = []    # paths to validation data

        self.rnd_samples_input_file = None  # file that stores randomly sampled parameter sets for metamodel training
        self.metamodel = None
        self.Metamodels = []                # saved metamodels

        # matplotlib canvas for sensitivity scores
        self.plot_layout = QtWidgets.QVBoxLayout(self.ui.widget_3)
        self.plot_canvas = MyStaticMplCanvas(self.ui.widget_3, width=1, height=1, dpi=100)        
        self.plot_layout.addWidget(self.plot_canvas)   

        # connect signals
        self.connect_signals_to_slots()



    def connect_signals_to_slots(self):
        """ Connect all signals to slots in Sensiman
        """
        self.ui.comboBox_15.currentTextChanged.connect(lambda phase_text: self.report_local_sensitivity_scores(phase_text))
        self.ui.radioButton_7.toggled.connect(lambda checked: self.report_local_sensitivity_scores_L2L1Linf(checked))
        self.ui.radioButton_6.toggled.connect(lambda checked: self.report_local_sensitivity_scores_L2L1Linf(checked))
        self.ui.radioButton_5.toggled.connect(lambda checked: self.report_local_sensitivity_scores_L2L1Linf(checked))
        self.ui.treeWidget_2.itemChanged.connect(lambda item, column: self.update_max_min_soil_parameters(item, column))
        self.ui.treeWidget_6.itemChanged.connect(lambda item, column: self.update_max_min_wall_parameters(item, column))
        self.ui.treeWidget_8.itemChanged.connect(lambda item, column: self.update_max_min_strut_parameters(item, column))



    def select_soil_parameters(self):
        """ Selects soil parameters to be determined by back-analysis
        """
        # which soil
        json_item_selected = self.ui.comboBox_29.currentText()
        selected_soil = None
        for soilmaterial in self.plaxman.Soilmaterials:
            if soilmaterial['json_item'] == json_item_selected:
                selected_soil = soilmaterial
                break

        if 'MC'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_MC('MC', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user 

        elif 'HSsmall'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_HSsmall('HSsmall', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user

        elif 'HS'==selected_soil['soil_model']:
            self.dialog.open_edit_soil_HS('HS', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user
    
        self.add_soil_parameters()


    def add_soil_parameters(self):
        """ Adds soil parameter to be determined by back-analysis
        """
        try:
        #if self.material_json_item != '':
            self.ui.treeWidget_2.blockSignals(True)
            if self.dialog.soil_edit_box.parameters_selected:
                parameter = {}
                parameter['parameter'] = self.dialog.soil_edit_box.parameters_selected
                parameter['soil'] = self.material_json_item
                parameter['value_min'] = {key: 0.6*value for key, value in parameter['parameter'].items()}
                parameter['value_max'] = {key: 1.4*value for key, value in parameter['parameter'].items()}
                parameter['value_min'] = OrderedDict(sorted(parameter['value_min'].items(), key=lambda t: t[0]))
                parameter['value_max'] = OrderedDict(sorted(parameter['value_max'].items(), key=lambda t: t[0]))
                self.Parameters.append(parameter)

                self.ui.treeWidget_2.setColumnCount(5)
                # add root
                item = QtWidgets.QTreeWidgetItem([self.material_json_item, 'Soil parameter', 'Initial value', 'Min value', 'Max value'])
                self.ui.treeWidget_2.addTopLevelItem(item)
                self.ui.treeWidget_2.expandItem(item) # expand children of this item

                if self.Parameters:
                    # count number of parameters
                    cnt_parameter = 0
                    for parameter in self.Parameters[:-1]:
                        cnt_parameter += len(parameter['parameter'])

                    for key, value in self.Parameters[-1]['parameter'].items():
                        # add child
                        child = QtWidgets.QTreeWidgetItem(['m'+str(cnt_parameter+1), key, str(value), str(self.Parameters[-1]['value_min'][key]), str(self.Parameters[-1]['value_max'][key])])
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        item.addChild(child)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        cnt_parameter += 1

            self.ui.treeWidget_2.blockSignals(False)

        except(AttributeError):
            self.dialog.show_message_box('Warning', 'Please select soil parameters first!')


    @pyqtSlot()
    def update_max_min_soil_parameters(self, item, column):
        """ Updates min/max values for design variables of a soil parameter
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) is not ''):
            value = float(item.text(column))
            # get groundanchor id
            soil_json_name = item.parent().text(0)    # the considered soil

            for i, parameters_soil in enumerate(self.Parameters): # loop over soil parameters for each of the soils
                if soil_json_name == parameters_soil['soil']:
                    if column == 3:
                        parameters_soil['value_min'][key] = value
                    elif column == 4:
                        parameters_soil['value_max'][key] = value



    def remove_soil_parameters(self):
        """ Removes soil parameters
        """
        if len(self.Parameters) > 0:
            self.Parameters.pop()
            self.ui.treeWidget_2.takeTopLevelItem(len(self.Parameters))


    def select_wall_parameters(self):
        """ Selects wall variables for design optimization
        """
        if len(self.plaxman.Walls) > 0:
            wall_id_selected = int(self.ui.comboBox_49.currentText())

            for wall in self.plaxman.Walls:
                if wall['id'] == wall_id_selected:
                    self.wall = wall
                    if 'Dwall' == wall['wall_type']:
                        self.dialog.open_edit_wall_Dwall('Dwall', wall['wall_name'], True)

                    elif 'SPW' == wall['wall_type']:
                        self.dialog.open_edit_wall_SPW('SPW', wall['wall_name'], True)

                    elif 'CPW' == wall['wall_type']:
                        self.dialog.open_edit_wall_CPW('CPW', wall['wall_name'], True)

                    break # stop looping Walls once a wall having 'id' is found
    

    def get_Eref_wall(self, wall):
        """ Gets Eref for wall, depending on wall type
        """
        if 'Dwall' == wall['wall_type']:
            Gref = read_data_in_json_item(wall['json_item'], 'Gref')
            nu = read_data_in_json_item(wall['json_item'], 'nu')
            Eref = get_Eref_Dwall(Gref, nu)
            return Eref

        elif 'SPW' == wall['wall_type']:
            D = read_data_in_json_item(wall['json_item'], 'D')
            S = read_data_in_json_item(wall['json_item'], 'S')
            EA = read_data_in_json_item(wall['json_item'], 'EA')
            Eref = get_Eref_SPW(D, S, EA)
            return Eref

        elif 'CPW' == wall['wall_type']:
            D = read_data_in_json_item(wall['json_item'], 'D')
            S = read_data_in_json_item(wall['json_item'], 'S')
            EA = read_data_in_json_item(wall['json_item'], 'EA')
            Eref = get_Eref_CPW(D, S, EA)
            return Eref


    def add_wall_parameters(self):
        """ Adds  wall parameter to be determined by back-analysis
        For now, only Young's modulus is allowed.
        """
        if self.ui.checkBox_16.checkState() == 2:
            wall_id_selected = int(self.ui.comboBox_49.currentText())
            self.ui.treeWidget_6.blockSignals(True)
            # get Eref from json_item
            for wall in self.plaxman.Walls:
                if wall['id'] == wall_id_selected:
                    wall_selected = wall
                    break
            Eref = self.get_Eref_wall(wall_selected)
            parameter = {}
            parameter['parameter'] = {'E': Eref}
            parameter['wall_id'] = wall_id_selected
            parameter['json_item'] = wall_selected['json_item'] # for later parameter updates
            parameter['wall_type'] = wall_selected['wall_type'] # for later parameter updates
            parameter['value_min'] = {key: 0.6*value for key, value in parameter['parameter'].items()}
            parameter['value_max'] = {key: 1.4*value for key, value in parameter['parameter'].items()}
            parameter['value_min'] = OrderedDict(sorted(parameter['value_min'].items(), key=lambda t: t[0]))
            parameter['value_max'] = OrderedDict(sorted(parameter['value_max'].items(), key=lambda t: t[0]))
            self.Parameters_wall.append(parameter)

            if self.Parameters_wall:
                self.ui.treeWidget_6.setColumnCount(5)
                # add root
                item = QtWidgets.QTreeWidgetItem(['Wall_ID_'+str(wall_id_selected), 'Wall parameter', 'Initial value', 'Min value', 'Max value'])
                self.ui.treeWidget_6.addTopLevelItem(item)
                self.ui.treeWidget_6.expandItem(item) # expand children of this item

                cnt_parameter = sum(len(list(parameter['parameter'].items())) for parameter in self.Parameters) # numer of selected soil parameters
                if self.Parameters_wall:
                    # count number of parameters
                    for parameter in self.Parameters_wall[:-1]:
                        cnt_parameter += len(parameter['parameter'])

                    for key, value in self.Parameters_wall[-1]['parameter'].items():
                        # add child
                        child = QtWidgets.QTreeWidgetItem(['m'+str(cnt_parameter+1), key, str(value), str(self.Parameters_wall[-1]['value_min'][key]), str(self.Parameters_wall[-1]['value_max'][key])])
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        item.addChild(child)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        cnt_parameter += 1

            self.ui.treeWidget_6.blockSignals(False)

        else:
            self.dialog.show_message_box('Warning', 'Please select wall parameters first!')


    @pyqtSlot()
    def update_max_min_wall_parameters(self, item, column):
        """ Updates min/max values for design variables of a wall parameter
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) is not ''):
            value = float(item.text(column))
            # get groundanchor id
            wall_id_selected = int(item.parent().text(0)[8:])    # the considered wall

            for i, parameters_wall in enumerate(self.Parameters_wall): # loop over soil parameters for each of the soils
                if wall_id_selected == parameters_wall['wall_id']:
                    if column == 3:
                        parameters_wall['value_min'][key] = value
                    elif column == 4:
                        parameters_wall['value_max'][key] = value

        print(self.Parameters_wall)


    def remove_wall_parameters(self):
        """ Removes strut parameters
        """
        if len(self.Parameters_wall) > 0:
            self.Parameters_wall.pop()
            self.ui.treeWidget_6.takeTopLevelItem(len(self.Parameters_wall))


    def select_strut_parameters(self):
        """ Selects design variables for strut
        """
        #selected_strut_id = int(self.ui.comboBox_50.currentText())

        #for strut in self.plaxman.Struts:
        #    if strut['id'] == selected_strut_id:
        #        self.dialog.open_design_variables_selection_strut(strut)
        self.dialog.show_message_box('Warning', 'Not yet implemented!')


    def add_strut_parameters(self):
        """ Adds  strut parameter to be determined by back-analysis
        For now, only Young's modulus is allowed.
        """
        if self.ui.checkBox_17.checkState() == 2:
            strut_id_selected = int(self.ui.comboBox_50.currentText())
            self.ui.treeWidget_8.blockSignals(True)
            parameter = {}
            # get Eref from json_item
            for strut in self.plaxman.Struts:
                if strut['id'] == strut_id_selected:
                    strut_selected = strut
                    break
            EA = read_data_in_json_item(strut_selected['json_item'], 'EA')
            parameter['parameter'] = {'EA': EA}
            parameter['strut_id'] = strut_id_selected
            parameter['value_min'] = {key: 0.6*value for key, value in parameter['parameter'].items()}
            parameter['value_max'] = {key: 1.4*value for key, value in parameter['parameter'].items()}
            parameter['value_min'] = OrderedDict(sorted(parameter['value_min'].items(), key=lambda t: t[0]))
            parameter['value_max'] = OrderedDict(sorted(parameter['value_max'].items(), key=lambda t: t[0]))
            self.Parameters_strut.append(parameter)

            if self.Parameters_strut:
                self.ui.treeWidget_8.setColumnCount(5)
                # add root
                item = QtWidgets.QTreeWidgetItem(['Wall_ID_'+str(strut_id_selected), 'Strut parameter', 'Initial value', 'Min value', 'Max value'])
                self.ui.treeWidget_8.addTopLevelItem(item)
                self.ui.treeWidget_8.expandItem(item) # expand children of this item

                if self.Parameters_strut:
                    # count number of parameters
                    cnt_parameter = 0
                    for parameter in self.Parameters_strut[:-1]:
                        cnt_parameter += len(parameter['parameter'])

                    for key, value in self.Parameters_strut[-1]['parameter'].items():
                        # add child
                        child = QtWidgets.QTreeWidgetItem(['m'+str(cnt_parameter+1), key, str(value), str(self.Parameters_strut[-1]['value_min'][key]), str(self.Parameters_strut[-1]['value_max'][key])])
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        item.addChild(child)
                        child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                        child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                        cnt_parameter += 1

            self.ui.treeWidget_8.blockSignals(False)

        else:
            self.dialog.show_message_box('Warning', 'Please select strut parameters first!')


    @pyqtSlot()
    def update_max_min_strut_parameters(self, item, column):
        """ Updates min/max values for design variables of a strut parameter
        This slot is called upon change of values in treewidget.
        """
        #print(column)
        key = item.text(1)  # key (located at column 1 of the changed child item)
        if (column > 0) and (item.text(column) is not ''):
            value = float(item.text(column))
            # get groundanchor id
            strut_id_selected = int(item.parent().text(0)[8:])    # the considered wall

            for i, parameters_strut in enumerate(self.Parameters_strut): # loop over soil parameters for each of the soils
                if strut_id_selected == parameters_strut['strut_id']:
                    if column == 3:
                        parameters_strut['value_min'][key] = value
                    elif column == 4:
                        parameters_strut['value_max'][key] = value

        print(self.Parameters_strut)


    def remove_strut_parameters(self):
        """ Removes strut parameters
        """
        if len(self.Parameters_strut) > 0:
            self.Parameters_strut.pop()
            self.ui.treeWidget_8.takeTopLevelItem(len(self.Parameters_strut))


    def merge_observation_points(self, Points_obs):
        """ Merges sets of observation points
        """
        pnt_obs = []
        for points in Points_obs:
            pnt_obs.append(points['points'])

        pnt_obs_flat = [item for sublist in pnt_obs for item in sublist]

        return pnt_obs_flat


    def merge_parameters(self):
        """ Merges list of dictionaries (Parameters) into numpy arrays
        """
        m0 = []
        m_min = []
        m_max = []

        # parameters for soils
        m0_soil = [list(parameter['parameter'].values()) for parameter in self.Parameters]
        m_min_soil = [list(parameter['value_min'].values()) for parameter in self.Parameters]
        m_max_soil = [list(parameter['value_max'].values()) for parameter in self.Parameters]
        m0.append(m0_soil)
        m_min.append(m_min_soil)
        m_max.append(m_max_soil)

        # parameters for wall
        m0_wall = [list(parameter['parameter'].values()) for parameter in self.Parameters_wall]
        m_min_wall = [list(parameter['value_min'].values()) for parameter in self.Parameters_wall]
        m_max_wall = [list(parameter['value_max'].values()) for parameter in self.Parameters_wall]
        m0.append(m0_wall)
        m_min.append(m_min_wall)
        m_max.append(m_max_wall)


        m0_flat = [item for sublist in m0 for subsublist in sublist for item in subsublist]
        m_min_flat = [item for sublist in m_min for subsublist in sublist for item in subsublist]
        m_max_flat = [item for sublist in m_max for subsublist in sublist for item in subsublist]
            
        return np.array(m0_flat), np.array(m_min_flat), np.array(m_max_flat)


    def go_to_metamodeling(self):
        """ Goes to metamodeling
        """
        self.setup_metamodeling()
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tabWidget_3.setCurrentIndex(2)


    def setup_metamodeling(self):
        """ Transfer the parameters and their lower/ upper bounds to metamodeling
        """
        # merge parameters from different soils
        self.m0, self.m_min, self.m_max = self.merge_parameters()

        # show on table
        self.ui.tableWidget_15.setColumnCount(self.m0.size)
        self.ui.tableWidget_15.setRowCount(2)
        param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(self.m0.size)]
        row_labels = ['m_min', 'm_max']
        self.ui.tableWidget_15.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_15.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.m0.size):
            self.ui.tableWidget_15.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.m_min[column_j])))
            self.ui.tableWidget_15.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.m_max[column_j])))


    def read_settings_from_table_metamodeling(self):
        """ Updates with new min/max values in table
        """
        try:
            m_min = []
            m_max = []
            for j in range(self.ui.tableWidget_15.columnCount()):
                m_min.append(float(self.ui.tableWidget_15.item(0, j).text()))
                m_max.append(float(self.ui.tableWidget_15.item(1, j).text()))
        
            self.m_min = np.array(m_min)
            self.m_max = np.array(m_max)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values in table are correctly entered!')


    def generate_database_input(self):
        """ Genertates (random) database input
        """
        # read min/max values from table
        self.read_settings_from_table_metamodeling()

        # Sample the parameter space (LHS method)
        try:
            num_points = int(self.ui.lineEdit_48.text())

            self.rnd_samples_input_file = Metamodeling.generate_input_samples(self.m_min, self.m_max, num_points)

            self.ui.label_83.setText('Database file: {0}, number of samples: {1}'.format(self.rnd_samples_input_file, num_points))

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if number of points is correctly entered!')


    def load_existing_database_input(self):
        """ Loads existing database (input) file
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        data_file, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Select data file', SENSIMAN)
        if data_file:
            try:
                self.rnd_samples_input_file = data_file.replace("/", "\\")
                samples_input = np.loadtxt(self.rnd_samples_input_file)
                self.ui.label_83.setText('Database file: {0}; number of samples: {1}'.format(self.rnd_samples_input_file, samples_input.shape[0]))

            except ValueError:
                self.dialog.show_message_box('Error', 'Data file fails to load. Please check your data!')


    def start_generate_database_output(self):
        """ Generates FEM database for metamodeling by running Plaxis2D calculations
        """
        if not self.rnd_samples_input_file:
            self.dialog.show_message_box('Warning', 'Please generate or load your randomly sampled points!')

        else:

            # initialize metamodeling workflow
            iter_ = int(self.ui.lineEdit_49.text())
            self.meta = Metamodeling(self.Parameters, self.Parameters_wall, self.plaxman.Soilmaterials, self.plaxman.Points_obs, iter_)

            # checking if required data are ready
            if self.meta.check() is False:
                self.dialog.show_message_box('Error', 'Please add at least one set of observation points in Plaxman\\Outputs!')
                return None

            # setup
            self.meta.setup()

            # load samples from input file and assign
            samples_input = np.loadtxt(self.rnd_samples_input_file)
            self.meta.set_input_samples(samples_input)

            # run 
            self.run_thread = RunThreadIter(workflow=self.meta) # note, run_thread which does not belong to self fails
            #self.meta.iterate() # for debugging
            print('\nSTARTING OUTPUT DATABASE GENERATION AT SAMPLE {}...'.format(iter_ + 1))
            self.run_thread.start()
            self.run_thread.run_percentage.connect(lambda percentage: self.display_run_progress(percentage, self.ui.progressBar_2))
    

    def display_run_progress(self, percentage, progress_bar):
        """ Displays run progress on progress bar
        """
        progress_bar.setValue(percentage)
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        print('Generating data for sample {0}/{1} with parameter set {2}'.format(self.run_thread.worklflow.iter + 1, self.run_thread.worklflow.iter_max, self.run_thread.worklflow.m))

            
    def stop_generate_database_output(self):
        """ Stops FEM database generations
        """
        print('\nSTOPPING OUTPUT DATABASE GENERATION AT SAMPLE {}...'.format(self.run_thread.worklflow.iter + 1))
        self.run_thread.stop()


    def resume_generate_database_output(self):
        """ Resumes FEM database generations
        """
        print('\nRESUMING OUTPUT DATABASE GENERATION FROM SAMPLE {}...'.format(self.run_thread.worklflow.iter + 1))
        self.run_thread.start()



    def load_samples_metamodel(self):
        """ Loads random samples for training/ validation
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        selected_dir = QFileDialog.getExistingDirectory(QFileDialog(), 'Select database folder', SENSIMAN)

        if selected_dir:
            if self.ui.comboBox_23.currentText() == 'Training':
                self.samples['paths_data_train'].append(selected_dir)
                #print('Dat. train', self.samples['paths_data_train'])
            else:
                self.samples['paths_data_validate'].append(selected_dir)
                #print('Dat. validate', self.samples['paths_data_validate'])

            self.update_samples_list_metamodel()



    def update_samples_list_metamodel(self):
        """ Updates the list for training/ validation samples
        """
        self.ui.listWidget.clear()

        for item in self.samples['paths_data_train']:
            self.ui.listWidget.addItem('Training set: ' + item)
        for item in self.samples['paths_data_validate']:
            self.ui.listWidget.addItem('Validation set: ' + item)


    def select_observation_phases_metamodel(self):
        """ Selects certain observation phases for metamodeling
        """
        # by default, all observation sets are selected for building metamodels
        for pnts_obs in self.plaxman.Points_obs:
            if 'usedForMetamodel' not in pnts_obs:
                pnts_obs['usedForMetamodel'] = True     # 'usedForMetamodel' is a new key

        if self.plaxman.Points_obs:
            self.dialog.open_observation_phases_selection(self.plaxman.Points_obs)

            # store the selected observed phases
            for i, ptns_obs in enumerate(self.plaxman.Points_obs):
                ptns_obs['usedForMetamodel'] = self.dialog.soil_edit_box.isVariableSelected[i]

        else:
            self.dialog.show_message_box('Info', 'There are no observation phases to select!')


    def remove_samples_metamodel(self):
        """ Removes random samples for training/ validation
        """
        if self.ui.comboBox_23.currentText() == 'Training':
            if self.samples['paths_data_train']:
                self.samples['paths_data_train'].pop()
        else:
            if self.samples['paths_data_validate']:
                self.samples['paths_data_validate'].pop()

        self.update_samples_list_metamodel()

    
    def read_simulation_data(self, dir_data):
        """ Read data points while removing those from FAILED simulations
        dir_data is a string for the path of the samples.
        #y_size is the size of observed model outputs
        """
        x_all = np.loadtxt(os.path.join(dir_data, 'lhs_samples'))

        #x = np.zeros((0, x_all.shape[1])) # empty x
        #y = np.zeros((0, y_size)) # empty y
        x = np.array([])
        y = np.array([])

        for i in range(x_all.shape[0]):
            # check if simulation for this sample is passed
            isPassed = False
            sample_plaxisinfo = 'plaxisinfo__sample_' + str(i).zfill(4) + '_*'
            reg_expr = os.path.join(dir_data, sample_plaxisinfo)
            for fname in glob.glob(reg_expr):
                if 'PASSED' in fname:
                    isPassed = True

            # Selective adding a new sample
            if isPassed is True:
                x = np.vstack([x, x_all[i,:]]) if x.size else x_all[i, :]
                y_fname = os.path.join(dir_data, 'data_all_sample_' + str(i).zfill(4))
                y_i = np.loadtxt(y_fname)
                y = np.vstack([y, y_i]) if y.size else y_i


        return x, y


    def read_simulation_data_obs(self, dir_data):
        """ Read data points while removing those from FAILED simulations
        Only the selected observation data, marked with the key 'usedForMetamodel', are read
        dir_data is a string for the path of the samples.
        #y_size is the size of observed model outputs.
        """
        x_all = np.loadtxt(os.path.join(dir_data, 'lhs_samples'))

        x = np.array([])
        y = np.array([])

        for i in range(x_all.shape[0]):
            # check if simulation for this sample is passed
            isPassed = False
            sample_plaxisinfo = 'plaxisinfo__sample_' + str(i).zfill(4) + '_*'
            reg_expr = os.path.join(dir_data, sample_plaxisinfo)
            for fname in glob.glob(reg_expr):
                if 'PASSED' in fname:
                    isPassed = True

            # Selective adding a new sample
            if isPassed is True:
                x = np.vstack([x, x_all[i,:]]) if x.size else x_all[i, :]
                #y_fname = os.path.join(dir_data, 'data_all_sample_' + str(i).zfill(4))
                y_i = np.array([])
                for obs_set_i, pnts_obs in enumerate(self.plaxman.Points_obs):
                    if pnts_obs['usedForMetamodel'] == True:
                        data_fname = 'data_Obs{0}_{1}_Phase{2}_sample_{3}'.format(str(obs_set_i+1), pnts_obs['obs_type'], str(pnts_obs['obs_phase']), str(i).zfill(4))
                        y_fname = os.path.join(dir_data, data_fname)
                        y_i_partial = np.loadtxt(y_fname)
                        y_i = np.hstack([y_i, y_i_partial]) if y_i.size else y_i_partial
                y = np.vstack([y, y_i]) if y.size else y_i


        return x, y


    def read_samples_metamodel(self):
        """ Reads in samples for training/ validation
        Only PASSED simulation data are read
        """
        samples = {}
        if not self.samples['paths_data_train']:
            self.dialog.show_message_box('Warning', 'Please load at least one training data set')
            return samples

        elif not self.samples['paths_data_validate']:
            self.dialog.show_message_box('Warning', 'Please load at least one validation data set')
            return samples

        else:
            # read in training data
            samples['data_train_x'] = np.array([])
            samples['data_train_y'] = np.array([])
            for path in self.samples['paths_data_train']:
                # read in data x, y
                #data_x, data_y = self.read_simulation_data(path)
                data_x, data_y = self.read_simulation_data_obs(path)
                samples['data_train_x'] = np.vstack([samples['data_train_x'], data_x]) if samples['data_train_x'].size else data_x
                samples['data_train_y'] = np.vstack([samples['data_train_y'], data_y]) if samples['data_train_y'].size else data_y

            # read in validation data
            samples['data_validate_x'] = np.array([])
            samples['data_validate_y'] = np.array([])
            for path in self.samples['paths_data_validate']:
                # read in data x, y
                #data_x, data_y = self.read_simulation_data(path)
                data_x, data_y = self.read_simulation_data_obs(path)
                samples['data_validate_x'] = np.vstack([samples['data_validate_x'], data_x]) if samples['data_validate_x'].size else data_x
                samples['data_validate_y'] = np.vstack([samples['data_validate_y'], data_y]) if samples['data_validate_y'].size else data_y

        return samples


    def train_metamodel(self):
        """ Trains metamodal
        Now only available for gaussian process (GP)
        """
        from optimize.gp import GaussianProcess

        # if not specified, all observation sets are selected for building metamodels
        for pnts_obs in self.plaxman.Points_obs:
            if 'usedForMetamodel' not in pnts_obs:
                pnts_obs['usedForMetamodel'] = True     # 'usedForMetamodel' is a new key

        # read in samples
        samples = self.read_samples_metamodel()

        if samples: # start training only if data is not empty
            # read kernel coefficients
            kernel_coeffs = [float(self.ui.lineEdit_87.text()), float(self.ui.lineEdit_88.text()), float(self.ui.lineEdit_89.text())]

            # train GP metamodel
            print('\nGP METAMODEL IS BEING TRAINED...')
            self.metamodel = GaussianProcess(samples, kernel_coeffs)
        
            self.run_thread = RunThreadSingle(workflow=self.metamodel)
            self.run_thread.start()
            self.run_thread.isDone.connect(lambda: self.save_metamodel())

            ## for debugging
            #self.metamodel.run()  
            #self.save_metamodel(isDone=True)  


    def save_metamodel(self, isDone=False):
        """ Saves metamodel after being trained
        """
        #print('Save metamodel is called')
        #if isDone:
        suffix_metamodel = []
        for pnts_obs in self.plaxman.Points_obs:
            if pnts_obs['usedForMetamodel'] == True:
                suffix_metamodel.append(pnts_obs['obs_type'] + str(pnts_obs['obs_phase']))
        suffix_metamodel = ''.join(suffix_metamodel)
        
        # save GP metamodel to file
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        fname = os.path.join(SENSIMAN, 'metamodel_gp_{0}.pickle'.format(suffix_metamodel))
        with open(fname, 'wb') as f:
            pickle.dump(self.metamodel.gp, f)

        #self.ui.label_85.setText('Metamodel file: {}'.format(fname))
        self.view_validation_wall_ux(fname)

        # store and show metamodel
        new_metamodel = {}
        new_metamodel['model'] = self.metamodel.gp
        new_metamodel['name'] = suffix_metamodel
        new_metamodel['filename'] = fname
        # copy of observation points
        Points_obs = []
        for pnts_obs in self.plaxman.Points_obs:
            pnts_obs_copy = {}
            pnts_obs_copy['obs_phase'] = pnts_obs['obs_phase']
            pnts_obs_copy['obs_type'] = pnts_obs['obs_type']
            pnts_obs_copy['points'] = pnts_obs['points']
            pnts_obs_copy['num_points'] = pnts_obs['num_points']
            pnts_obs_copy['usedForMetamodel'] = pnts_obs['usedForMetamodel']
            Points_obs.append(pnts_obs_copy)

        #new_metamodel['Points_obs'] = copy.deepcopy(self.plaxman.Points_obs)
        new_metamodel['Points_obs'] = Points_obs

        self.Metamodels.append(new_metamodel)
        self.show_metamodels_on_combobox()


    def remove_metamodel(self):
        """ Removes a selected metamodel
        """
        if len(self.Metamodels) > 0:
            # which metamodel
            name_selected_metamodel = self.ui.comboBox_22.currentText()
            metamodel_selected = None
            for metamodel in self.Metamodels:
                if metamodel['name'] == name_selected_metamodel:
                    metamodel_selected = metamodel

            # pop the selected metamodel out of Metamodels
            deleted_item = [item for item in self.Metamodels if item['name'] == metamodel_selected['name']][0]
            deleted_item_idx = self.Metamodels.index(deleted_item)
            deleted_metamodel = self.Metamodels.pop(deleted_item_idx)

            # remove model file 
            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
            SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
            fname = os.path.join(SENSIMAN, 'metamodel_gp_{0}.pickle'.format(deleted_metamodel['name']))
            try:
                os.remove(fname)
                print('Metamodel {0} saved under {1} is removed'.format(deleted_metamodel['name'], fname))
            except OSError:
                pass

            # refresh combobox
            self.show_metamodels_on_combobox()


    def show_metamodels_on_combobox(self):
        """ Simply lists the trained metamodels in combobox
        """
        self.ui.comboBox_22.clear()
        for metamodel in self.Metamodels:
            self.ui.comboBox_22.addItem(metamodel['name'])


    def view_prediction_metamodel(self):
        """ Displays window for prediction using the trained metamodel
        """
        if len(self.Metamodels) > 0:
            self.form.open_metamodel_prediction(self.dialog, self.Metamodels, self.m0, self.m_min, self.m_max)
    

    def view_validation_wall_ux(self, fname):
        """ Displays validation results (only up to 30 samples)
        """
        # read in samples
        samples = self.read_samples_metamodel()

        # build suffix
        suffix_metamodel = []
        for pnts_obs in self.plaxman.Points_obs:
            if pnts_obs['usedForMetamodel'] == True:
                suffix_metamodel.append(pnts_obs['obs_type'] + str(pnts_obs['obs_phase']))
        suffix_metamodel = ''.join(suffix_metamodel)

        # load GP metamodel from file
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        fname = os.path.join(SENSIMAN, 'metamodel_gp_{0}.pickle'.format(suffix_metamodel))
        with open(fname, 'rb') as f:
            gp = pickle.load(f)

        score_train = gp.score(samples['data_train_x'], samples['data_train_y'])
        score_validate = gp.score(samples['data_validate_x'], samples['data_validate_y'])
        print('TRAINING GP METAMODEL IS FINISED')
        print('Achieved fitness on training data is {}'.format(score_train))
        print('Achieved fitness on validation data is {}'.format(score_validate))
        print('The trained GP model is saved under {0}'.format(fname))
        samples['data_validate_y_predict'] = gp.predict(samples['data_validate_x'])

        data_idx_start = 0
        for obs_num, obs_set in enumerate(self.plaxman.Points_obs):
            #if obs_set['obs_type'] == 'WallUx':
            if obs_set['usedForMetamodel'] == True:
                y_plate = [item[1] for item in self.plaxman.Points_obs[obs_num]['points']]
                wall_ux_metamodel = samples['data_validate_y_predict'][:, data_idx_start:data_idx_start + obs_set['num_points']]
                wall_ux_measured = samples['data_validate_y'][:, data_idx_start:data_idx_start + obs_set['num_points']]
                self.form.open_metamodel_validation_WallUx(wall_ux_metamodel, wall_ux_measured, y_plate)

                data_idx_start += obs_set['num_points']
            #else:
            #    data_idx_start += obs_set['num_points']


    def go_to_local_sensitivity(self):
        """ Goes to local sensivity
        """
        self.setup_local_sensitivity()
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tabWidget_3.setCurrentIndex(1)


    def setup_local_sensitivity(self):
        """ Transfer the parameters and their lower/ upper bounds to local sensitivity
        """
        # merge parameters from different soils
        self.m0, self.m_min, self.m_max = self.merge_parameters()
        self.ratio_perturbation_sensitivity = float(self.ui.lineEdit_82.text())
        self.m_min = self.m0 - self.ratio_perturbation_sensitivity*self.m0
        self.m_max = self.m0 + self.ratio_perturbation_sensitivity*self.m0

        # show on table
        self.ui.tableWidget_16.setColumnCount(self.m0.size)
        self.ui.tableWidget_16.setRowCount(3)
        param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(self.m0.size)]
        row_labels = ['m_min', 'm0', 'm_max']
        self.ui.tableWidget_16.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_16.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.m0.size):
            self.ui.tableWidget_16.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.m_min[column_j])))
            self.ui.tableWidget_16.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.m0[column_j])))
            self.ui.tableWidget_16.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(self.m_max[column_j])))


    def read_settings_from_table_local_sensitivity(self):
        """ Updates with new m0/min/max values in table
        """
        try:
            m_min = []
            m0 = []
            m_max = []
            for j in range(self.ui.tableWidget_16.columnCount()):
                m_min.append(float(self.ui.tableWidget_16.item(0, j).text()))
                m0.append(float(self.ui.tableWidget_16.item(1, j).text()))
                m_max.append(float(self.ui.tableWidget_16.item(2, j).text()))
        
            self.m_min = np.array(m_min)
            self.m0 = np.array(m0)
            self.m_max = np.array(m_max)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values in table are correctly entered!')


    def start_local_sensitivity(self):
        """ Starts generating FEM output database and calculates local sensitivity scores
        """
        # set observation phases in comboBox_15
        self.ui.comboBox_15.clear()
        self.ui.comboBox_15.blockSignals(True)
        for obs_set in self.plaxman.Points_obs:
            self.ui.comboBox_15.addItem('Phase_' + str(obs_set['obs_phase']))
        self.ui.comboBox_15.addItem('All phases')
        self.ui.comboBox_15.setCurrentIndex(self.ui.comboBox_15.count() - 1)

        # read (update) m0/min/max values from table
        self.read_settings_from_table_local_sensitivity()

        # initialize local sensitivity workflow
        self.local_sensitivity = LocalSensitivity(self.Parameters, self.Parameters_wall, self.plaxman.Soilmaterials, self.plaxman.Points_obs, self.m0, self.m_min, self.m_max)

        # checking if required data are ready
        check_result = self.local_sensitivity.check()
        if check_result == 1:
            self.dialog.show_message_box('Error', 'Please add at least one set of observation points in Plaxman\\Outputs!')
            return None
        elif  check_result > 1:
            self.dialog.show_message_box('Error', 'Please use one and only one type observation points in Plaxman\\Outputs!')
            return None

        # set up local sensitivity analysis
        self.local_sensitivity.setup()

        # generate finite-difference samples (input)
        self.local_sensitivity.generate_input_samples()
        self.ui.label_89.setText('Database file: {0}, number of samples: {1}'.format(self.local_sensitivity.path_output, self.local_sensitivity.iter_max))

        # start calculations
        #self.local_sensitivity.iterate() # for debugging
        #self.local_sensitivity.iterate() # for debugging
        self.run_thread = RunThreadIter(workflow=self.local_sensitivity) # note, run_thread which does not belong to self fails
        print('\nSTARTING OUTPUT DATABASE GENERATION FOR LOCAL SENSTIVITY ANALYSIS...')
        self.run_thread.start()
        self.run_thread.run_percentage.connect(lambda percentage: self.display_run_progress(percentage, self.ui.progressBar_3))
        self.run_thread.allDone.connect(lambda: self.report_local_sensitivity_scores('All phases'))

        # connect to slot if current text of comboBox_15 changes
        self.ui.comboBox_15.blockSignals(False)
        #self.ui.comboBox_15.currentTextChanged.connect(lambda phase_text: self.report_local_sensitivity_scores(phase_text))


    def stop_local_sensitivity(self):
        """ Stops generating FEM output database
        """
        print('\nSTOPPING OUTPUT DATABASE GENERATION FOR LOCAL SENSTIVITY ANALYSIS...')
        self.run_thread.stop()


    def resume_local_sensitivity(self):
        """ resumes generating FEM output database
        """
        print('\nRESUMING OUTPUT DATABASE GENERATION FOR LOCAL SENSTIVITY ANALYSIS...')
        self.run_thread.start()


    @pyqtSlot()
    def report_local_sensitivity_scores(self, phase_text):
        """ Reports local sensitivity scores
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')

        # which vector norm
        vector_norm = 'L2'
        if self.ui.radioButton_7.isChecked():
            vector_norm = 'L2'
        elif self.ui.radioButton_6.isChecked():
            vector_norm = 'L1'
        elif self.ui.radioButton_5.isChecked():
            vector_norm = 'Linf'

        try:
            # plot sensitivity scores
            if phase_text == 'All phases':
                # calculate sensitivity scores for all data
                scores, Lnorm = self.local_sensitivity.calc_sensitivity(vector_norm=vector_norm)
                print('{0} sensitivity scores for all phases: {1}'.format(Lnorm, 100*scores/np.sum(scores)))
                path_scores = os.path.join(SENSIMAN, 'local_sensitivity', 'sensitivity_scores')
                savetxt(path_scores, scores)
                self.plot_canvas.plot_sensitivity_scores(scores)
                self.sensitivity_scores['All phases'] = scores

            elif phase_text != '':
                # calculate sensitivity scores for data of each phase
                phase_number = int(phase_text.split('_')[-1])
                scores_phase, Lnorm = self.local_sensitivity.calc_sensitivity_phase(phase_number, vector_norm=vector_norm)
                print('{0} sensitivity scores for phase {1}: {2}'.format(Lnorm, phase_number, 100*scores_phase/np.sum(scores_phase)))
                path_scores = os.path.join(SENSIMAN, 'local_sensitivity', 'sensitivity_scores_phase_' + str(phase_number))
                savetxt(path_scores, scores_phase)
                self.plot_canvas.plot_sensitivity_scores(scores_phase, phase_number)
                self.sensitivity_scores[phase_text] = scores_phase

        except FileNotFoundError:
            print('No scores found!')
        

    @pyqtSlot()
    def report_local_sensitivity_scores_L2L1Linf(self, checked):
        """ Reports local sensitivity scores when radioButton_5 is checked
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')

        if checked:
            # which phase
            phase_text = self.ui.comboBox_15.currentText()

            # which vector norm
            vector_norm = 'L2'
            if self.ui.radioButton_7.isChecked():
                vector_norm = 'L2'
            elif self.ui.radioButton_6.isChecked():
                vector_norm = 'L1'
            elif self.ui.radioButton_5.isChecked():
                vector_norm = 'Linf'

            try:
                # plot sensitivity scores
                if phase_text == 'All phases':
                    # calculate sensitivity scores for all data
                    scores, Lnorm = self.local_sensitivity.calc_sensitivity(vector_norm=vector_norm)
                    print('{0} sensitivity scores for all phases: {1}'.format(Lnorm, 100*scores/np.sum(scores)))
                    path_scores = os.path.join(SENSIMAN, 'local_sensitivity', 'sensitivity_scores')
                    savetxt(path_scores, scores)
                    self.plot_canvas.plot_sensitivity_scores(scores)
                    self.sensitivity_scores['All phases'] = scores

                elif phase_text != '':
                    # calculate sensitivity scores for data of each phase
                    phase_number = int(phase_text.split('_')[-1])
                    scores_phase, Lnorm = self.local_sensitivity.calc_sensitivity_phase(phase_number, vector_norm=vector_norm)
                    print('{0} sensitivity scores for phase {1}: {2}'.format(Lnorm, phase_number, 100*scores_phase/np.sum(scores_phase)))
                    path_scores = os.path.join(SENSIMAN, 'local_sensitivity', 'sensitivity_scores_phase_' + str(phase_number))
                    savetxt(path_scores, scores_phase)
                    self.plot_canvas.plot_sensitivity_scores(scores_phase, phase_number)
                    self.sensitivity_scores[phase_text] = scores_phase

            except FileNotFoundError:
                print('No scores found!')

    def save(self):
        """ Saves Sensiman
        """
        objs = (self.Parameters, self.m0, self.m_min, self.m_max,
                self.local_sensitivity, self.sensitivity_scores, self.ratio_perturbation_sensitivity, self.samples, self.Metamodels, self.Parameters_wall, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None)
        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'sensiman_state.mon')
        saveobjs(filename, *objs)
        print("Sensiman's state is saved in {}".format(filename))


    def load(self):
        """ Loads Sensiman
        """
        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'sensiman_state.mon')
        if not isfile(filename):
            self.dialog.show_message_box('Error', 'File {} does not exist for loading'.format(filename))
        else:
            (self.Parameters, self.m0, self.m_min, self.m_max,
            self.local_sensitivity, self.sensitivity_scores, self.ratio_perturbation_sensitivity, self.samples, self.Metamodels, self.Parameters_wall, _, _, _, _,
            _, _, _, _, _, _, _, _, _, _) = loadobjs(filename)

            loadSensiman.add_soil_parameters(self.ui, self.Parameters)
            loadSensiman.setup_metamodeling(self.ui, self.m_min, self.m_max)
            loadSensiman.setup_local_sensitivity(self.ui, self.plot_canvas, self.m0, self.plaxman.Points_obs, self.local_sensitivity, self.sensitivity_scores, self.ratio_perturbation_sensitivity)
            try:
                loadSensiman.update_samples_list_metamodel(self.ui, self.samples)
                loadSensiman.show_metamodels_on_combobox(self.ui, self.Metamodels)
            except: # when loading projects created before 15.12.2020
                self.Metamodels = []                # saved metamodels
                self.samples = {}                   # random samples for training/validation
                self.samples['paths_data_train'] = []       # paths to training data
                self.samples['paths_data_validate'] = []    # paths to validation data

            try:    # newly added elements, pass when loading an old project folder
                loadSensiman.add_wall_parameters(self.ui, self.Parameters_wall, self.Parameters)
            except:
                pass

            print("Sensiman's state saved in file '{}' is loaded".format(filename))
