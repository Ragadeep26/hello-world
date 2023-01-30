# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:13:38 2019

@author: nya
"""
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt

class loadSensiman():
    
    @staticmethod
    def add_soil_parameters(ui, Parameters):
        """ Reconstructs soil parameters to be determined by back-analysis
        """
        ui.treeWidget_2.blockSignals(True)
        ui.treeWidget_2.setColumnCount(5)
        num_parameter = 0
        for parameters_dict in Parameters:
            item = QtWidgets.QTreeWidgetItem([parameters_dict['soil'], 'Soil parameter', 'Initial value', 'Min value', 'Max value'])
            ui.treeWidget_2.addTopLevelItem(item)
            ui.treeWidget_2.expandItem(item) # expand children of this item
            for key, value in parameters_dict['parameter'].items():
                child = QtWidgets.QTreeWidgetItem(['m'+str(num_parameter+1), key, str(value), str(parameters_dict['value_min'][key]), str(parameters_dict['value_max'][key])])
                item.addChild(child)
                child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                num_parameter += 1

        ui.treeWidget_2.blockSignals(False)


    @staticmethod
    def add_wall_parameters(ui, Parameters_wall, Parameters):
        """ Reconstructs soil parameters to be determined by back-analysis
        """
        ui.treeWidget_6.blockSignals(True)
        ui.treeWidget_6.setColumnCount(5)
        num_parameter = sum(len(list(parameter['parameter'].items())) for parameter in Parameters) # numer of selected soil parameters
        for parameters_dict in Parameters_wall:
            item = QtWidgets.QTreeWidgetItem(['Wall_ID_'+str(parameters_dict['wall_id']), 'Wall parameter', 'Initial value', 'Min value', 'Max value'])
            ui.treeWidget_6.addTopLevelItem(item)
            ui.treeWidget_6.expandItem(item) # expand children of this item
            for key, value in parameters_dict['parameter'].items():
                child = QtWidgets.QTreeWidgetItem(['m'+str(num_parameter+1), key, str(value), str(parameters_dict['value_min'][key]), str(parameters_dict['value_max'][key])])
                item.addChild(child)
                child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                num_parameter += 1

        ui.treeWidget_6.blockSignals(False)


    @staticmethod
    def setup_metamodeling(ui, m_min, m_max):
        """  Reconstructs 
        """
        # list data types
        data_types = ['Training', 'Validation']
        for dt in data_types:
            ui.comboBox_23.addItem(dt) 

        if m_min is not None:
            ui.tableWidget_15.setColumnCount(m_min.size)
            ui.tableWidget_15.setRowCount(2)
            param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(m_min.size)]
            row_labels = ['m_min', 'm_max']
            ui.tableWidget_15.setHorizontalHeaderLabels(param_labels)
            ui.tableWidget_15.setVerticalHeaderLabels(row_labels)

            for column_j in range(m_min.size):
                ui.tableWidget_15.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(m_min[column_j])))
                ui.tableWidget_15.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(m_max[column_j])))


    @staticmethod
    def setup_local_sensitivity(ui, plot_canvas, m0, Points_obs, local_sensitivity, sensitivity_scores, ratio_perturbation_sensitivity):
        """  Reconstructs 
        """
        # set m0, m_min, and m_max in parameter table
        if local_sensitivity is not None:
            m_min = m0 - 0.1*m0
            m_max = m0 + 0.1*m0
            ui.tableWidget_16.setColumnCount(m_min.size)
            ui.tableWidget_16.setRowCount(3)
            param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(m_min.size)]
            row_labels = ['m_min', 'm0', 'm_max']
            ui.tableWidget_16.setHorizontalHeaderLabels(param_labels)
            ui.tableWidget_16.setVerticalHeaderLabels(row_labels)

            for column_j in range(m_min.size):
                ui.tableWidget_16.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(m_min[column_j])))
                ui.tableWidget_16.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(m0[column_j])))
                ui.tableWidget_16.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(m_max[column_j])))

            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
            SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
            LOCAL_SENSITIVITY = os.path.join(SENSIMAN, 'local_sensitivity')
            local_sensitivity.path_output = LOCAL_SENSITIVITY # reset path_output (necessary when loading project which has been saved as..)
            # show database file
            ui.label_89.setText('Database file: {0}, number of samples: {1}'.format(local_sensitivity.path_output, local_sensitivity.iter_max))

            # set observation phases in comboBox_15
            ui.comboBox_15.clear()
            ui.comboBox_15.blockSignals(True)
            for obs_set in Points_obs:
                ui.comboBox_15.addItem('Phase_' + str(obs_set['obs_phase']))
            ui.comboBox_15.addItem('All phases')
            ui.comboBox_15.setCurrentIndex(ui.comboBox_15.count() - 1)
            ui.comboBox_15.blockSignals(False)

            # plot sensitivity scores
            if sensitivity_scores:
                plot_canvas.plot_sensitivity_scores(sensitivity_scores['All phases'])
            
            # ratio for perturbation
            ui.lineEdit_82.setText(str(ratio_perturbation_sensitivity))


    @staticmethod
    def update_samples_list_metamodel(ui, samples):
        """ Updates the list for training/ validation samples
        """
        ui.listWidget.clear()

        for item in samples['paths_data_train']:
            ui.listWidget.addItem('Training set: ' + item)
        for item in samples['paths_data_validate']:
            ui.listWidget.addItem('Validation set: ' + item)


    @staticmethod
    def show_metamodels_on_combobox(ui, Metamodels):
        """ Simply lists the trained metamodels in combobox
        """
        ui.comboBox_22.clear()
        for metamodel in Metamodels:
            ui.comboBox_22.addItem(metamodel['name'])