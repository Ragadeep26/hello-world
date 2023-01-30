# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 14:28:03 2018

@author: nya
"""

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt

class loadBackman():
    
    @staticmethod
    def load_data_site(ui, Data):
        """ Update table of observation points
        """
        #print(Data)
        if Data:
            max_column = max([data['data'].size for data in Data])
            ui.tableWidget_4.setColumnCount(max_column)
            ui.tableWidget_4.setRowCount(len(Data))
            points_label = ['P' + str(pntnumber + 1) for pntnumber in range(max_column)]
            ui.tableWidget_4.setHorizontalHeaderLabels(points_label)

        labels = []
        for (i, points_set) in enumerate(Data):
            label = 'Obs. set {0}: Type {1}, Phase {2}'.format(i+1, points_set['obs_type'], points_set['obs_phase'])
            labels.append(label)
            if points_set['data'].size > 1:
                for j in range(points_set['data'].size):
                    ui.tableWidget_4.setItem(i, j, QtWidgets.QTableWidgetItem(str(points_set['data'][j])))
            else:
                ui.tableWidget_4.setItem(i, 0, QtWidgets.QTableWidgetItem(str(points_set['data'])))

        if labels:
            ui.tableWidget_4.setVerticalHeaderLabels(labels)


    @staticmethod
    def add_soil_parameters(ui, Parameters):
        """ Reconstruct soil parameters to be determined by back-analysis
        """
        ui.treeWidget.blockSignals(True)
        ui.treeWidget.setColumnCount(5)
        num_parameter = 0

        for parameters_dict in Parameters:
            item = QtWidgets.QTreeWidgetItem([parameters_dict['soil'], 'Soil parameter', 'Initial value', 'Min value', 'Max value'])
            ui.treeWidget.addTopLevelItem(item)
            ui.treeWidget.expandItem(item) # expand children of this item
            for key, value in parameters_dict['parameter'].items():
                child = QtWidgets.QTreeWidgetItem(['m'+str(num_parameter+1), key, str(value), str(parameters_dict['value_min'][key]), str(parameters_dict['value_max'][key])])
                item.addChild(child)
                child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                num_parameter += 1

        ui.treeWidget.blockSignals(False)


    @staticmethod
    def add_wall_parameters(ui, Parameters_wall, Parameters):
        """ Reconstructs soil parameters to be determined by back-analysis
        """
        ui.treeWidget_9.blockSignals(True)
        ui.treeWidget_9.setColumnCount(5)
        num_parameter = sum(len(list(parameter['parameter'].items())) for parameter in Parameters) # numer of selected soil parameters
        for parameters_dict in Parameters_wall:
            item = QtWidgets.QTreeWidgetItem(['Wall_ID_'+str(parameters_dict['wall_id']), 'Wall parameter', 'Initial value', 'Min value', 'Max value'])
            ui.treeWidget_9.addTopLevelItem(item)
            ui.treeWidget_9.expandItem(item) # expand children of this item
            for key, value in parameters_dict['parameter'].items():
                child = QtWidgets.QTreeWidgetItem(['m'+str(num_parameter+1), key, str(value), str(parameters_dict['value_min'][key]), str(parameters_dict['value_max'][key])])
                item.addChild(child)
                child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                num_parameter += 1

        ui.treeWidget_9.blockSignals(False)


    @staticmethod
    def setup_optimization_ukf(ui, m0, m_min, m_max, P0, Q):
        """ Reconstruct configurations for UKF
        """
        if m0 is not None:
            ui.tableWidget_3.setColumnCount(m0.size)
            ui.tableWidget_3.setRowCount(5)
            param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(m0.size)]
            row_labels = ['m_min', 'm_max', 'm0', 'diag(P0)', 'diag(Q)']
            ui.tableWidget_3.setHorizontalHeaderLabels(param_labels)
            ui.tableWidget_3.setVerticalHeaderLabels(row_labels)

            for column_j in range(m0.size):
                ui.tableWidget_3.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(m_min[column_j])))
                ui.tableWidget_3.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(m_max[column_j])))
                ui.tableWidget_3.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(m0[column_j])))
                ui.tableWidget_3.setItem(3, column_j, QtWidgets.QTableWidgetItem(str(P0[column_j, column_j])))
                ui.tableWidget_3.setItem(4, column_j, QtWidgets.QTableWidgetItem(str(Q[column_j, column_j])))