# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 11:26:10 2018

@author: nya
"""
import sys
import os
from os.path import join, isfile
import time
import numpy as np
import pickle
from collections import OrderedDict
from tools.file_tools import saveobjs, loadobjs
from system.run_thread import RunThreadIter
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QFileDialog
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots
from backman.backman_load import loadBackman
from tools.json_functions import read_data_in_json_item
from solver.plaxis2d.parameter_relations import get_Eref_CPW, get_Eref_SPW, get_Eref_Dwall

from workflow1.backanalysis_ukf import Backanalysis_Ukf
from workflow1.backanalysis_pso import Backanalysis_PSO
from optimize import misfit
#MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
#BACKMAN = os.path.join(MONIMAN_OUTPUTS, 'backman')
#MEASUREMENT = sys.modules['moniman_paths']['MEASUREMENT']

class Backman():
    def __init__(self, plaxman=None):
        """ Initializes Backman attributes
        """
        self.plaxman = plaxman
        self.ui = plaxman.ui
        self.dialog = plaxman.dialog
        
        self.Parameters = []            # soil parameters
        self.Parameters_wall = []       # wall parameters
        # array parameters (for UKF)
        self.m0 = None                  # initial values
        self.m_min = None               # min values
        self.m_max = None               # max values
        self.P0 = None                  # P0
        self.Q = None                   # Q
        self.Data = []                  # measured data
        self.d_obs = {}                 # flatened mesured data {'points':, 'data':, 'R'}

        self.path_metamodel = None      # path to metamodel
        self.metamodel = None	        # metamodel object
        
        # matplotlib canvas and toolbar for UKF
        self.plot_layout_ukf = QtWidgets.QVBoxLayout(self.ui.widget_2)
        self.plot_canvas_ukf = MyStaticMplCanvasSubplots(self.ui.widget_2, width=1, height=1, dpi=100)        
        self.plot_layout_ukf.addWidget(self.plot_canvas_ukf)   
        
        # matplotlib canvas and toolbar for PSO
        self.plot_layout_pso = QtWidgets.QVBoxLayout(self.ui.widget_4)
        self.plot_canvas_pso = MyStaticMplCanvasSubplots(self.ui.widget_4, width=1, height=1, dpi=100)        
        self.plot_layout_pso.addWidget(self.plot_canvas_pso)   

        # connect signals
        self.connect_signals_to_slots()
        
        

    def connect_signals_to_slots(self):
        """ Connect all signals to slots in Sensiman
        """
        self.ui.treeWidget.itemChanged.connect(lambda item, column: self.update_max_min_soil_parameters(item, column))
        
        
    def open_data_site(self):
        """ Opens select file to load site data
        """
        data_file, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Select data file', sys.modules['moniman_paths']['MONIMAN_OUTPUTS'])
        data = {}
        if data_file:
            #print(data_file)
            try:
                data['data'] = np.loadtxt(data_file)
                data['file'] = data_file
                data['obs_type'] = self.ui.comboBox_20.currentText()
                data['obs_phase'] = self.ui.comboBox_21.currentIndex() + 1
            
                data['stddev_percentage'] = float(self.ui.lineEdit_43.text())
                data_mean = np.mean(np.abs(data['data']))
                data['R'] = np.diag((data['stddev_percentage']*data_mean*np.ones(data['data'].size))**2)

                self.Data.append(data)
                self.update_data_table()

            except ValueError:
                data.clear()
                self.ui.tableWidget_4.clear()
                self.dialog.show_message_box('Error', 'Data file fails to load. Please check your data!')


    def remove_data_site(self):
        """ Removes the last data set
        """
        if len(self.Data) > 0:
            self.Data.pop()
            self.update_data_table()


    def update_data_table(self):
        """ Update table of observation points
        """
        self.ui.tableWidget_4.setRowCount(len(self.Data))
        if len(self.Data) == 0:
            self.ui.tableWidget_4.setColumnCount(0)
            self.ui.tableWidget_4.setRowCount(0)
        else:
            max_column = max([data['data'].size for data in self.Data])
            self.ui.tableWidget_4.setColumnCount(max_column)
            points_label = ['P' + str(pntnumber + 1) for pntnumber in range(max_column)]
            self.ui.tableWidget_4.setHorizontalHeaderLabels(points_label)

        labels = []
        for (i, points_set) in enumerate(self.Data):
            label = 'Obs. set {0}: Type {1}, Phase {2}'.format(i+1, points_set['obs_type'], points_set['obs_phase'])
            labels.append(label)
            if points_set['data'].size > 1:
                for j in range(points_set['data'].size):
                    self.ui.tableWidget_4.setItem(i, j, QtWidgets.QTableWidgetItem(str(points_set['data'][j])))
            else:
                self.ui.tableWidget_4.setItem(i, 0, QtWidgets.QTableWidgetItem(str(points_set['data'])))

        if labels:
            self.ui.tableWidget_4.setVerticalHeaderLabels(labels)

    
    def select_soil_parameters(self):
        """ Selects soil parameter to be determined by back-analysis
        """
        # which soil
        json_item_selected = self.ui.comboBox_19.currentText()
        selected_soil = None
        for soilmaterial in self.plaxman.Soilmaterials:
            if soilmaterial['json_item'] == json_item_selected:
                selected_soil = soilmaterial
                break

        if 'MC'==selected_soil['soil_model']:
            #self.dialog.open_edit_soil_MC('MC', selected_soil['json_item'], True, selected_soil['correlations_ve'])
            self.dialog.open_edit_soil_MC('MC', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user 

        elif 'HSsmall'==selected_soil['soil_model']:
            #self.dialog.open_edit_soil_HSsmall('HSsmall', selected_soil['json_item'], True, selected_soil['correlations_ve'])
            self.dialog.open_edit_soil_HSsmall('HSsmall', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user

        elif 'HS'==selected_soil['soil_model']:
            #self.dialog.open_edit_soil_HS('HS', selected_soil['json_item'], True, selected_soil['correlations_ve'])
            self.dialog.open_edit_soil_HS('HS', selected_soil['json_item'], color=selected_soil['color'], isdefined=True, correlations_ve=selected_soil['correlations_ve'])
            self.material_json_item = self.dialog.soil_edit_box.json_item_user
        
        self.add_soil_parameters()


    def add_soil_parameters(self):
        """ Adds soil parameter to be determined by back-analysis
        """
        #if self.material_json_item != '':
        try:
            if self.dialog.soil_edit_box.parameters_selected:
                parameter = {}
                parameter['parameter'] = self.dialog.soil_edit_box.parameters_selected
                parameter['soil'] = self.material_json_item
                parameter['value_min'] = {key: 0.6*value for key, value in parameter['parameter'].items()}
                parameter['value_max'] = {key: 1.4*value for key, value in parameter['parameter'].items()}
                parameter['value_min'] = OrderedDict(sorted(parameter['value_min'].items(), key=lambda t: t[0]))
                parameter['value_max'] = OrderedDict(sorted(parameter['value_max'].items(), key=lambda t: t[0]))
                self.Parameters.append(parameter)

                self.ui.treeWidget.setColumnCount(5)
                # add root
                item = QtWidgets.QTreeWidgetItem([self.material_json_item, 'Soil parameter', 'Initial value', 'Min value', 'Max value'])
                self.ui.treeWidget.addTopLevelItem(item)
                self.ui.treeWidget.expandItem(item) # expand children of this item

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
        """ Removes soil parameter to be determined by back-analysis
        """
        if len(self.Parameters) > 0:
            self.Parameters.pop()
            self.ui.treeWidget.takeTopLevelItem(len(self.Parameters))


    def select_wall_parameters(self):
        """ Selects wall variables for design optimization
        """
        if len(self.plaxman.Walls) > 0:
            wall_id_selected = int(self.ui.comboBox_53.currentText())

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
        if self.ui.checkBox_18.checkState() == 2:
            wall_id_selected = int(self.ui.comboBox_53.currentText())
            self.ui.treeWidget_9.blockSignals(True)
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
                self.ui.treeWidget_9.setColumnCount(5)
                # add root
                item = QtWidgets.QTreeWidgetItem(['Wall_ID_'+str(wall_id_selected), 'Wall parameter', 'Initial value', 'Min value', 'Max value'])
                self.ui.treeWidget_9.addTopLevelItem(item)
                self.ui.treeWidget_9.expandItem(item) # expand children of this item

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

            self.ui.treeWidget_9.blockSignals(False)

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
            self.ui.treeWidget_9.takeTopLevelItem(len(self.Parameters_wall))

    
    def go_to_inversion(self):
        """ Goes to optimization
        """
        if self.ui.radioButton_3.isChecked():       # UKF is selected
            self.ui.tabWidget_4.setCurrentIndex(1)

            self.setup_optimization_ukf()

            self.ui.pushButton_63.setEnabled(False)
            self.ui.pushButton_64.setEnabled(False)
            self.ui.pushButton_65.setEnabled(True)
        
        elif self.ui.radioButton_4.isChecked():     # PSO is selectec
            self.ui.tabWidget_4.setCurrentIndex(2)
            self.setup_optimization_pso()


    def setup_optimization_ukf(self):
        """ Sets up UKF for back-analysis
        """
        # merge parameters from different soils
        self.m0, self.m_min, self.m_max = self.merge_parameters()
        self.P0 = np.diag(((self.m_max - self.m_min)/25)**2)
        self.Q = (0.1**2)*self.P0

        if not self.Data: # Data is empty
            self.dialog.show_message_box('Warning', 'Please load measured data before you continue!')
            return

        # merge (flatten) measured data into self.data_obs
        self.merge_measured_data(self.Data, self.plaxman.Points_obs)

        # show on table
        self.ui.tableWidget_3.setColumnCount(self.m0.size)
        self.ui.tableWidget_3.setRowCount(5)
        param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(self.m0.size)]
        row_labels = ['m_min', 'm_max', 'm0', 'diag(P0)', 'diag(Q)']
        self.ui.tableWidget_3.setHorizontalHeaderLabels(param_labels)
        self.ui.tableWidget_3.setVerticalHeaderLabels(row_labels)

        for column_j in range(self.m0.size):
            self.ui.tableWidget_3.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.m_min[column_j])))
            self.ui.tableWidget_3.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.m_max[column_j])))
            self.ui.tableWidget_3.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(self.m0[column_j])))
            self.ui.tableWidget_3.setItem(3, column_j, QtWidgets.QTableWidgetItem(str(self.P0[column_j, column_j])))
            self.ui.tableWidget_3.setItem(4, column_j, QtWidgets.QTableWidgetItem(str(self.Q[column_j, column_j])))

        # set observation phase for plotting
        self.ui.comboBox_52.clear()
        for obs_set in self.plaxman.Points_obs:
            self.ui.comboBox_52.addItem('Phase_' + str(obs_set['obs_phase']))
        self.ui.comboBox_52.setCurrentIndex(self.ui.comboBox_52.count() - 1)



    def read_settings_from_table_ukf(self):
        """ Updates with new values in table
        """
        #for row_i in range(self.ui.tableWidget_3.rowCount()):
        for j in range(self.ui.tableWidget_3.columnCount()):
            self.m_min[j] = float(self.ui.tableWidget_3.item(0, j).text())
            self.m_max[j] = float(self.ui.tableWidget_3.item(1, j).text())
            self.m0[j] = float(self.ui.tableWidget_3.item(2, j).text())
            self.P0[j,j] = float(self.ui.tableWidget_3.item(3, j).text())
            self.Q[j,j] = float(self.ui.tableWidget_3.item(4, j).text())
        

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


    def merge_measured_data(self, Data, Points_obs):
        """ Merges sets measured data into a nparray vector
        """
        points_all = []
        for points in Points_obs:
            points_all.append(points['points'])
        points_all_flat = [item for sublist in points_all for item in sublist]
        self.d_obs['points'] = np.array(points_all_flat)

        data_all = []
        R_all = []
        for data in Data:
            data_all.append(data['data'].reshape(-1)) # reshaping 0d array (a single data point) to 1d row vector
            R_all.append(np.diag(data['R']))
        self.d_obs['data'] = np.concatenate(data_all)
        self.d_obs['R'] = np.diag(np.concatenate(R_all))


    def start_inversion_ukf(self):
        """ Runs UKF back-analysis
        """
        try:
            self.read_settings_from_table_ukf()
            lambda_ = 1.0e-3
            iter_max = int(self.ui.lineEdit_51.text())
            WallFootUx_Is_Zero = (self.ui.checkBox_7.checkState() == 2)

            self.ba = Backanalysis_Ukf(self.Data, self.Parameters, self.Parameters_wall, self.plaxman.Soilmaterials, self.plaxman.Points_obs, self.d_obs, self.m0, self.m_min, self.m_max, self.P0, self.Q, lambda_, iter_max, WallFootUx_Is_Zero)

            # checking if required data are ready
            if self.ba.check_data() is False:
                self.dialog.show_message_box('Error', 'Measurement data has not been loaded. Please load data!')
                return None

            # setting up
            obs_phase = int(self.ui.comboBox_52.currentText().split('_')[-1])
            self.display_wall_deflection_measured(self.plot_canvas_ukf, obs_phase)

            self.ui.pushButton_63.setEnabled(True)
            self.ui.pushButton_64.setEnabled(False)
            self.ui.pushButton_65.setEnabled(False)
            print('\nSETTING UP UKF BACK-ANALYSIS...')
            self.ba.setup()
            self.plot_canvas_ukf.clear_plot_scalar([2,4], iter_max, self.ba.J)

            print('Initial parameter values: {}'.format(self.ba.m))
            print('Initial objective value: {}'.format(self.ba.J))

            self.time_start = time.time()
            self.run_thread = RunThreadIter(workflow=self.ba)
            #self.ba.iterate() # for debugging
            self.run_thread.start()
            self.run_thread.run_percentage.connect(lambda value: self.display_inversion_progress_ukf(value, obs_phase))
            self.run_thread.iter_isDone.connect(self.print_inversion_results)

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the values are correctly entered!')


    def print_inversion_results(self, isDone=False):
        """ Prints current back-analysis results
        """
        if isDone:
            print('Current parameter values: {}'.format(self.ba.m))
            print('Current objective value: {}'.format(self.ba.J))


    def resume_inversion_ukf(self):
        """ Resumes running UKF back-analysis
        """
        self.ui.pushButton_63.setEnabled(True)
        self.ui.pushButton_64.setEnabled(False)
        self.ui.pushButton_65.setEnabled(False)
        print('\nRESUMING UKF BACK-ANALYSIS AT ITERATION {}...'.format(self.ba.iter + 1))
        self.run_thread.start()


    def stop_inversion_ukf(self):
        """ Stops UKF inversion process
        """
        self.ui.pushButton_63.setEnabled(False)
        self.ui.pushButton_64.setEnabled(True)
        self.ui.pushButton_65.setEnabled(True)
        print('\nSTOPPING UKF BACK-ANALYSIS AT ITERATION {}...'.format(self.ba.iter + 1))
        self.run_thread.stop()


    def display_inversion_progress_ukf(self, value, obs_phase):
        """ Sets progress bar to display percentage of finished iterations
        """
        self.ui.progressBar.setValue(value)
        current_time = time.time()
        self.ui.label_74.setText('Elapsed time is {0:.3f} minutes'.format((current_time - self.time_start)/60))
        print('\nITERATION {0} OF {1} IS RUNNING...'.format(self.ba.iter + 1, self.ba.iter_max))

        self.display_wall_deflection_simulated(self.plot_canvas_ukf, obs_phase)
        self.display_wall_deflection_measured(self.plot_canvas_ukf, obs_phase)
        self.plot_canvas_ukf.plot_scalar_value(self.ba.iter, self.ba.J, [2,4])


    def display_wall_deflection_simulated(self, plot_canvas, obs_phase):
        """ Displays simulated wall deflection representatively for visual inpsection
        """
        for i, obs_set in enumerate(self.ba.Points_obs):
            if obs_set['obs_phase'] == obs_phase:
                if obs_set['obs_type'] == 'WallUx':
                    data_source = os.path.join(self.ba.path_iter, 'data_Obs' + str(i+1) + '_WallUx_Phase' + str(obs_set['obs_phase']) + '_sigPnt_000')
                    Ux_plate = np.loadtxt(data_source)
                    y_plate = [item[1] for item in self.ba.Points_obs[i]['points']]
                    plot_canvas.plot_wall_output_points(np.array(y_plate), Ux_plate*1000, [1,2], 'Simulated Ux [mm]', 'Y [m]', 'blue')

                    # replot wall output from the initial parameter set
                    data_source_init = os.path.join(self.ba.path_iter0, 'data_Obs' + str(i+1) + '_WallUx_Phase' + str(obs_set['obs_phase']) + '_sigPnt_000')
                    Ux_plate_init = np.loadtxt(data_source_init)
                    plot_canvas.plot_wall_output_scattered_points(np.array(y_plate), Ux_plate_init*1000, [0,1], color='blue')

                    break


    def display_wall_deflection_measured(self, plot_canvas, obs_phase):
        """ Displays measured wall deflection representatively for visual inpsection
        """
        for i, data in enumerate(self.Data):
            if data['obs_phase'] == obs_phase:
                data_to_plot = data

                if data_to_plot['obs_type'] == 'WallUx':
                    Ux_plate = np.loadtxt(data_to_plot['file'])
                    y_plate = [item[1] for item in self.plaxman.Points_obs[i]['points']]
                    plot_canvas.plot_wall_output_points(np.array(y_plate), Ux_plate*1000, [0,1], 'Measured Ux [mm]', 'Y [m]', 'red', holdon=False)
                    plot_canvas.plot_wall_output_scattered_points(np.array(y_plate), Ux_plate*1000, [1,2], color='red', holdon=True)
                    break


    def load_available_results_ukf(self):
        """ Checks and loads back-analysis results if existed
        """
        QtWidgets.QApplication.processEvents()

        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        BACKMAN = os.path.join(MONIMAN_OUTPUTS, 'backman')
        
        iter_max = int(self.ui.lineEdit_51.text())

        iter_final = None
        
        obs_phase = int(self.ui.comboBox_52.currentText().split('_')[-1])

        for i, obs_set in enumerate(self.plaxman.Points_obs):
            if obs_set['obs_phase'] == obs_phase:
                if obs_set['obs_type'] == 'WallUx':
                    y_plate = [item[1] for item in self.plaxman.Points_obs[i]['points']]
                    for iter_ in range(iter_max):
                        file_WallUx = os.path.join(BACKMAN, 'iter_' + str(iter_).zfill(4),'data_Obs' + str(i+1) + '_WallUx_Phase' + str(obs_set['obs_phase']) + '_sigPnt_000')
                        file_J = os.path.join(BACKMAN, 'iter_' + str(iter_).zfill(4),'J')
                        if os.path.isfile(file_J):
                            J = np.loadtxt(file_J)
                            self.plot_canvas_ukf.plot_scalar_value(iter_, J, [2,4])
                            iter_final = iter_
                        else:
                            file_WallUx = os.path.join(BACKMAN, 'iter_' + str(iter_ - 1).zfill(4),'data_Obs' + str(i+1) + '_WallUx_Phase' + str(obs_set['obs_phase']) + '_sigPnt_000')
                            file_J = os.path.join(BACKMAN, 'iter_' + str(iter_ - 1).zfill(4),'J')
                            break

                        if iter_final is not None:
                            print('\nLoading back-analysis results until iteration #{}'.format(iter_final))
                            Ux_plate = np.loadtxt(file_WallUx)
                            self.plot_canvas_ukf.plot_wall_output_points(np.array(y_plate), Ux_plate*1000, [1,2], 'Simulated Ux [mm]', 'Y [m]', 'blue')
                            file_WallUx_init = os.path.join(BACKMAN, 'iter_' + str(0).zfill(4),'data_Obs' + str(i+1) + '_WallUx_Phase' + str(obs_set['obs_phase']) + '_sigPnt_000')
                            Ux_plate_init = np.loadtxt(file_WallUx_init)
                            self.plot_canvas_ukf.plot_wall_output_scattered_points(np.array(y_plate), Ux_plate_init*1000, [0,1], color='blue')

                            self.display_wall_deflection_measured(self.plot_canvas_ukf, obs_phase)

                        else:
                            print('\nNo available back-analysis results are found')

                    break

    def setup_optimization_pso(self):
        """ Sets up PSO for back-analysis
        """
        # merge parameters from different soils
        self.m0, self.m_min, self.m_max = self.merge_parameters()

        # merge (flatten) measured data into self.data_obs
        self.merge_measured_data(self.Data, self.plaxman.Points_obs)

        # show on table
        self.ui.tableWidget_5.setColumnCount(self.m0.size)
        param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(self.m0.size)]
        self.ui.tableWidget_5.setHorizontalHeaderLabels(param_labels)

        for column_j in range(self.m0.size):
            self.ui.tableWidget_5.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(self.m_min[column_j])))
            self.ui.tableWidget_5.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(self.m_max[column_j])))

        # add items to combo boxes
        self.ui.comboBox_26.clear()
        self.ui.comboBox_27.clear()
        self.ui.comboBox_26.addItems(param_labels)
        self.ui.comboBox_27.addItems(param_labels)

        # set observation phase for plotting
        self.ui.comboBox_51.clear()
        for obs_set in self.plaxman.Points_obs:
            self.ui.comboBox_51.addItem('Phase_' + str(obs_set['obs_phase']))
        self.ui.comboBox_51.setCurrentIndex(self.ui.comboBox_51.count() - 1)

        # disable push button for inspecting misfit
        self.ui.pushButton_89.setEnabled(False) 

    def load_metamodel_pso(self):
        """ Loads already trained metamodel 
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        model_file, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Select data file', SENSIMAN)
        if model_file:
            self.path_metamodel = model_file.replace('/','\\')
            self.ui.label_73.setText('Metamodel file: {}'.format(self.path_metamodel))


    def read_settings_from_table_pso(self):
        """ Updates with new values in table
        """
        for j in range(self.ui.tableWidget_5.columnCount()):
            self.m_min[j] = float(self.ui.tableWidget_5.item(0, j).text())
            self.m_max[j] = float(self.ui.tableWidget_5.item(1, j).text())


    def start_inversion_pso(self):
        """ Runs PSO back-analysis
        """

        try:
            self.read_settings_from_table_pso()
            #print(self.m_min)
            #print(self.m_max)

            iter_max = int(self.ui.lineEdit_50.text())
            population = int(self.ui.lineEdit_52.text())
            c1 = float(self.ui.lineEdit_53.text())
            c2 = float(self.ui.lineEdit_54.text())
            if self.ui.radioButton.isChecked():
                misfit = getattr(misfit, 'L1')
            else:
                misfit = getattr(misfit, 'L2')

            # load metamodel
            if self.path_metamodel:
                with open(self.path_metamodel, 'rb') as f:
                    self.metamodel = pickle.load(f)
            else:
                self.dialog.show_message_box('Warning', 'Please load the metamodel!')
                return None

            structure = 'Ring' if self.ui.radioButton_10.isChecked() else 'Star'    # structure of PSO
            self.ba = Backanalysis_PSO(self.d_obs, self.metamodel, misfit, self.m_min, self.m_max, iter_max, population, c1, c2, structure)

            # checking if required data are ready
            if self.ba.check_data() is False:
                self.dialog.show_message_box('Error', 'Measurement data has not been loaded. Please load data!')
                return None

            # setup
            obs_phase = int(self.ui.comboBox_51.currentText().split('_')[-1])
            self.display_wall_deflection_measured(self.plot_canvas_pso, obs_phase)

            # setting up
            print('\nSETTING UP PSO BACK-ANALYSIS...')
            self.ba.setup()
            data_predict = self.metamodel.predict(self.ba.swarm.globalbest.reshape(1, -1)).flatten()
            self.plot_canvas_pso.clear_plot_scalar([2,4], iter_max, self.ba.misfit(data_predict, self.d_obs['data']))
            self.display_wall_deflection_simulated_pso(self.plot_canvas_pso, obs_phase)

            # let run PSO back-analysis
            #self.ba.iterate() # for debugging
            #self.display_wall_deflection_simulated_pso(self.plot_canvas_pso)
            #self.ba.main() # for debugging

            self.time_start = time.time()
            self.run_thread = RunThreadIter(workflow=self.ba)
            print('STARTING BACK ANALYSIS (PSO {})...'.format(structure))
            self.run_thread.start()
            self.run_thread.run_percentage.connect(lambda percentage: self.display_inversion_progress_pso(percentage, self.ui.progressBar_4, self.ui.label_95, self.plot_canvas_pso, obs_phase))
            self.run_thread.iter_isDone.connect(self.print_inversion_results_pso)
            
            # allow push button for inspecting misfit (based on the global best particle)
            self.ui.pushButton_89.setEnabled(True) 

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the values are correctly entered!')


    def resume_inversion_pso(self):
        """ Resumes PSO back-analysis
        """
        print('\nRESUMING PSO BACK-ANALYSIS AT ITERATION {}...'.format(self.ba.iter + 1))
        self.run_thread.start()


    def stop_inversion_pso(self):
        """ Stops PSO back-analysis
        """
        print('\nSTOPPING PSO BACK-ANALYSIS AT ITERATION {}...'.format(self.ba.iter + 1))
        self.run_thread.stop()


    def display_inversion_progress_pso(self, percentage, progress_bar, elapsedtime_label, plot_canvas, obs_phase):
        """ Sets progress bar to display percentage of finished iterations
        """
        if (self.ba.iter + 1) % 10 == 0:
            progress_bar.setValue(percentage)
            current_time = time.time()
            elapsedtime_label.setText('Elapsed time is {0:.3f} minutes'.format((current_time - self.time_start)/60))
            #print('\nITERATION {0} OF {1} IS RUNNING...'.format(self.ba.iter + 1, self.ba.iter_max))

            self.display_wall_deflection_simulated_pso(plot_canvas, obs_phase)



    def display_wall_deflection_simulated_pso(self, plot_canvas, obs_phase):
        """ Displays simulated wall deflection representatively for visual inpsection
        """
        data_idx_start = 0
        for i, obs_set in enumerate(self.plaxman.Points_obs):
            if obs_set['obs_phase'] == obs_phase:

                if obs_set['obs_type'] == 'WallUx':
                    data_predict = self.metamodel.predict(self.ba.swarm.globalbest.reshape(1, -1)).flatten()
                    Ux_plate_predict = data_predict[data_idx_start:data_idx_start + obs_set['num_points']]
                    y_plate = [item[1] for item in self.plaxman.Points_obs[i]['points']]
                    plot_canvas.plot_wall_output_points(np.array(y_plate), Ux_plate_predict*1000, [1,2], 'Simulated Ux [mm]', 'Y [m]', 'blue')
            
                    Ux_plate_measure = np.loadtxt(self.Data[i]['file'])
                    plot_canvas.plot_wall_output_scattered_points(np.array(y_plate), Ux_plate_measure*1000, [1,2], color='red', holdon=True)
                    plot_canvas.plot_scalar_value(self.ba.iter, self.ba.misfit(data_predict, self.d_obs['data']), [2,4]) # misfit for all data

                    # plot wall deflection for the initial global best particle
                    if self.ba.iter == 1:
                        plot_canvas.plot_wall_output_scattered_points(np.array(y_plate), Ux_plate_predict*1000, [0,1], color='blue', holdon=True) 

                    break
            else:
                data_idx_start += obs_set['num_points']


    def print_inversion_results_pso(self, isDone=False):
        """ Prints current back-analysis results
        """
        if isDone and ((self.ba.iter + 1) % 10 == 0):
            print('Global best at iteration {}: {}'.format(self.ba.iter + 1, self.ba.swarm.globalbest))
            print('Misfit at global best: {}'.format(self.ba.misfit(self.metamodel.predict(self.ba.swarm.globalbest.reshape(1, -1)), self.d_obs['data'])))


    def inspect_misfit_pso(self):
        """ Views misfit function at the global best particle
        """
        import matplotlib.pyplot as plt # temporary simple plot
        from mpl_toolkits import mplot3d

        param1_idx = self.ui.comboBox_26.currentIndex()
        param2_idx = self.ui.comboBox_27.currentIndex()

        n_points = 50
        param1_range = np.linspace(self.m_min[param1_idx], self.m_max[param1_idx], n_points)
        param2_range = np.linspace(self.m_min[param2_idx], self.m_max[param2_idx], n_points)
        param = np.tile(self.ba.swarm.globalbest.reshape(1, -1), (n_points * n_points, 1))

        # assign in-range parameters to param for metamodel prediction
        for i, p1 in enumerate(param1_range):
            for j, p2 in enumerate(param2_range):
                param[i*n_points + j, param1_idx] = p1
                param[i*n_points + j, param2_idx] = p2

        data_predict = self.metamodel.predict(param)

        misfits = np.zeros(n_points * n_points)
        for i in range(n_points * n_points):
            misfits[i] = self.ba.misfit(data_predict[i, :], self.d_obs['data'])

        misfits = misfits.reshape(n_points, n_points)
        
        param1_grid, param2_grid = np.meshgrid(param1_range, param2_range)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        #ax.plot_surface(param1_grid, param2_grid, misfits,  rstride=20, cstride=20, alpha=0.4)
        ax.plot_surface(param1_grid, param2_grid, misfits,  cmap='copper', alpha=0.4)
        ax.contour(param1_grid, param2_grid, misfits, zdir='z', offset=-np.min(misfits), cmap='coolwarm')
        misfit_found = self.ba.misfit(self.metamodel.predict(self.ba.swarm.globalbest.reshape(1, -1)), self.d_obs['data'])
        ax.scatter(self.ba.swarm.globalbest[param1_idx], self.ba.swarm.globalbest[param2_idx], misfit_found, zdir='z')
        ax.text(self.ba.swarm.globalbest[param1_idx], self.ba.swarm.globalbest[param2_idx], misfit_found, 'PSO solution')

        ax.set_zlabel('Misfit value')
        ax.set_xlabel('m' + str(param1_idx + 1))
        ax.set_ylabel('m' + str(param2_idx + 1))
        plt.show()


    def save(self):
        """ Saves Backman
        """
        objs = (self.Parameters, self.m0, self.m_min, self.m_max, self.P0, self.Q, self.d_obs, self.Data,
                self.Parameters_wall, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None)
        filename = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'backman_state.mon')
        saveobjs(filename, *objs)
        print("Backman's state is saved in {}".format(filename))
    

    def load(self):
        """ Loads Backman
        """
        filename = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'backman_state.mon')
        if not isfile(filename):
            self.dialog.show_message_box('Error', 'File {} does not exist for loading'.format(filename))
        else:
            (self.Parameters, self.m0, self.m_min, self.m_max, self.P0, self.Q, self.d_obs, self.Data,
            self.Parameters_wall, _, _, _, _, _, _, _, _, _,
            _, _, _, _, _, _, _, _, _, _) = loadobjs(filename)

            loadBackman.load_data_site(self.ui, self.Data)
            loadBackman.add_soil_parameters(self.ui, self.Parameters)
            if self.P0 is not None:
                loadBackman.setup_optimization_ukf(self.ui, self.m0, self.m_min, self.m_max, self.P0, self.Q)

            try:    # newly added elements, pass when loading an old project folder
                loadBackman.add_wall_parameters(self.ui, self.Parameters_wall, self.Parameters)
            except:
                pass

            print("Backman's state saved in file '{}' is loaded".format(filename))
