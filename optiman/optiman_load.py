# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 16:43:40 2019

@author: nya
"""
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt
from tools.math import hex_to_rgb, rgb_to_integer

class loadOptiman():
    
    
    @staticmethod
    def add_wall_variables(ui, wall, variables_wall, variables_wall_min, variables_wall_max, variables_wall_subset):
        """ Adds wall variables to treeWidget
        """
        if variables_wall:
            ui.treeWidget_3.blockSignals(True)
            ui.treeWidget_3.setColumnCount(6)
            # add root
            item = QtWidgets.QTreeWidgetItem([wall['wall_name'] + str(wall['id']), 'Wall variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
            ui.treeWidget_3.addTopLevelItem(item)
            ui.treeWidget_3.expandItem(item) # expand children of this item
            # add children
            cnt = 0
            for (key, value), value_min, value_max, values_subset in zip(variables_wall.items(), variables_wall_min.values(), variables_wall_max.values(), variables_wall_subset.values()):
                if key != 'id':
                    cnt += 1
                    values_subset_str = ', '.join([str(value) for value in values_subset])
                    child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(value_min), str(value_max), values_subset_str])
                    item.addChild(child)
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setFlags(child.flags() | Qt.ItemIsEditable) 

            ui.treeWidget_3.blockSignals(False)
                

    @staticmethod
    def add_anchor_variables(ui, variables_anchors, variables_anchors_min, variables_anchors_max, variables_anchors_subset, variables_wall, variables_struts):
        """ Adds anchor variables to treeWidget
        """
        if variables_anchors:
            # list design variables on treeWidget_3
            ui.treeWidget_4.blockSignals(True)
            ui.treeWidget_4.setColumnCount(6)
            #cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in variables_anchors)
            #cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt = len(variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
            cnt = len(variables_wall.keys()) - 1
            for i, variables_anchor in enumerate(variables_anchors): # loop over variables for each of the ground anchors
                # add root
                item = QtWidgets.QTreeWidgetItem(['Groundanchor_' + str(list(variables_anchor.keys())[0]), 'Anchor variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                ui.treeWidget_4.addTopLevelItem(item)
                ui.treeWidget_4.expandItem(item) # expand children of this item

                for key, value in list(variables_anchor.values())[0].items():
                    cnt += 1
                    values_subset = list(variables_anchors_subset[i].values())[0][key]
                    values_subset_str = ', '.join([str(value) for value in values_subset])
                    child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(list(variables_anchors_min[i].values())[0][key]), str(list(variables_anchors_max[i].values())[0][key]), values_subset_str])
                    item.addChild(child)
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setFlags(child.flags() | Qt.ItemIsEditable)

            ui.treeWidget_4.blockSignals(False)


    @staticmethod
    def add_strut_variables(ui, variables_struts, variables_struts_min, variables_struts_max, variables_struts_subset, variables_wall, variables_anchors):
        """ Adds strut variables to treeWidget
        """
        if variables_struts:
            ui.treeWidget_5.blockSignals(True)
            # list design variables on treeWidget_3
            ui.treeWidget_5.setColumnCount(6)
            cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in variables_anchors)
            #cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt = len(variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
            cnt = len(variables_wall.keys()) - 1 + cnt_variables_anchors
            for i, variables_strut in enumerate(variables_struts): # loop over variables for each of the ground anchors
                # add root
                item = QtWidgets.QTreeWidgetItem(['Strut_' + str(list(variables_strut.keys())[0]), 'Strut variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                ui.treeWidget_5.addTopLevelItem(item)
                ui.treeWidget_5.expandItem(item) # expand children of this item

                for key, value in list(variables_strut.values())[0].items():
                    cnt += 1
                    values_subset = list(variables_struts_subset[i].values())[0][key]
                    values_subset_str = ', '.join([str(value) for value in values_subset])
                    child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(list(variables_struts_min[i].values())[0][key]), str(list(variables_struts_max[i].values())[0][key]), values_subset_str])
                    item.addChild(child)
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setFlags(child.flags() | Qt.ItemIsEditable)

            ui.treeWidget_5.blockSignals(False)


    @staticmethod
    def add_stone_columns_variables(ui, variables_stone_columns, variables_stone_columns_min, variables_stone_columns_max, variables_stone_columns_subset, variables_wall, variables_anchors, variables_struts):
        """ Adds stone columns variables to treeWidget
        """
        if variables_stone_columns:
            ui.treeWidget_7.blockSignals(True)
            # list design variables on treeWidget_7
            ui.treeWidget_7.setColumnCount(6)
            cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in variables_anchors)
            cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt = len(variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
            cnt = len(variables_wall.keys()) - 1 + cnt_variables_anchors + cnt_variables_struts
            for i, variables_sc in enumerate(variables_stone_columns): # loop over variables for each of the ground anchors
                # add root
                item = QtWidgets.QTreeWidgetItem(['StoneColumns_' + str(list(variables_sc.keys())[0]), 'Variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                ui.treeWidget_7.addTopLevelItem(item)
                ui.treeWidget_7.expandItem(item) # expand children of this item

                for key, value in list(variables_sc.values())[0].items():
                    cnt += 1
                    values_subset = list(variables_stone_columns_subset[i].values())[0][key]
                    values_subset_str = ', '.join([str(value) for value in values_subset])
                    child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(list(variables_stone_columns_min[i].values())[0][key]), str(list(variables_stone_columns_max[i].values())[0][key]), values_subset_str])
                    item.addChild(child)
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setFlags(child.flags() | Qt.ItemIsEditable)

            ui.treeWidget_7.blockSignals(False)


    @staticmethod
    def add_fdc_variables(ui, variables_stone_columns, variables_stone_columns_min, variables_stone_columns_max, variables_stone_columns_subset, variables_wall, variables_anchors, variables_struts):
        """ Adds fdc variables to treeWidget
        """
        if variables_stone_columns:
            ui.treeWidget_7.blockSignals(True)
            # list design variables on treeWidget_7
            ui.treeWidget_7.setColumnCount(6)
            cnt_variables_anchors = sum(len(list(variables_anchor.values())[0].items()) for variables_anchor in variables_anchors)
            cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt_variables_struts = sum(len(list(variables_strut.values())[0].items()) for variables_strut in variables_struts)
            #cnt = len(variables_wall.keys()) + cnt_variables_anchors + cnt_variables_struts
            cnt = len(variables_wall.keys()) - 1 + cnt_variables_anchors + cnt_variables_struts
            for i, variables_sc in enumerate(variables_stone_columns): # loop over variables for each of the ground anchors
                # add root
                item = QtWidgets.QTreeWidgetItem(['RigidInclusions_' + str(list(variables_sc.keys())[0]), 'Variable', 'Current value', 'Min value', 'Max value', 'Subset values'])
                ui.treeWidget_7.addTopLevelItem(item)
                ui.treeWidget_7.expandItem(item) # expand children of this item

                for key, value in list(variables_sc.values())[0].items():
                    cnt += 1
                    values_subset = list(variables_stone_columns_subset[i].values())[0][key]
                    values_subset_str = ', '.join([str(value) for value in values_subset])
                    child = QtWidgets.QTreeWidgetItem(['v' + str(cnt), key, str(value), str(list(variables_stone_columns_min[i].values())[0][key]), str(list(variables_stone_columns_max[i].values())[0][key]), values_subset_str])
                    item.addChild(child)
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(4, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setFlags(child.flags() | Qt.ItemIsEditable)

            ui.treeWidget_7.blockSignals(False)


    @staticmethod
    def add_active_earthpressure_wedge(ui, plot_canvas, active_earth_pressure_wedge):
        """ Adds the active earth pressure wedge
        """
        if active_earth_pressure_wedge:
            ui.checkBox_11.blockSignals(True) # temporarily block this signal to avoid call slot add_active_earthpressure_wedge in Optiman
            active_earth_pressure_wedge['pathpatches'] = plot_canvas.plot_multilinear_earth_pressure_wedge(active_earth_pressure_wedge['points'])
            ui.checkBox_11.setCheckState(2)
            ui.checkBox_11.blockSignals(False)
            
    @staticmethod
    def display_anchor_competent_soil_layers(ui, Layer_polygons):
        """ Displays soil layers for user selection of ground anchor competent soil layers
        """
        ui.tableWidget_17.setRowCount(2*len(Layer_polygons))
        ui.tableWidget_17.horizontalHeader().setVisible(True)
        column_labels = ['Soil layer', 'G. anchor competence', 'G. anchor through layers', 'Tskin [kN/m]']
        ui.tableWidget_17.setColumnCount(len(column_labels))
        ui.tableWidget_17.setHorizontalHeaderLabels(column_labels)

        for layer_i, layerpolygon in enumerate(Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            #print(layer_i, soilmaterial_layer)
            ui.tableWidget_17.setItem(2*layer_i, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # soilmaterial name
            ui.tableWidget_17.item(2*layer_i, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color
            ui.tableWidget_17.setSpan(2*layer_i, 0, 2, 1)

            ui.tableWidget_17.setCellWidget(2*layer_i, 1, QtWidgets.QCheckBox('Selection?'))   # grouting competent?
            ui.tableWidget_17.setSpan(2*layer_i, 1, 2, 1)

            if layer_i < (len(Layer_polygons) - 1):
                ui.tableWidget_17.setCellWidget(2*layer_i+1, 2, QtWidgets.QCheckBox('Selection?'))   # grouting through layers?
                ui.tableWidget_17.setSpan(2*layer_i+1, 2, 2, 1)

            #ui.tableWidget_17.setItem(2*layer_i, 3, QtWidgets.QTableWidgetItem('200.0')) # skin resistance
            ui.tableWidget_17.setItem(2*layer_i, 3, QtWidgets.QTableWidgetItem(str(layerpolygon['Tskin']))) # skin resistance
            #ui.tableWidget_17.item(2*layer_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
            ui.tableWidget_17.setSpan(2*layer_i, 3, 2, 1)


    @staticmethod
    def add_objectives(ui, objectives):
        """ Reconstructs objetives on GUI
        """
        ui.comboBox_40.blockSignals(True)
        ui.checkBox_12.blockSignals(True)
        ui.checkBox_15.blockSignals(True)
        ui.checkBox_13.blockSignals(True)
        ui.checkBox_14.blockSignals(True)
        ui.comboBox_40.clear()
        for key in objectives.keys():
            if key == 'Max WallUx':
                ui.checkBox_12.setCheckState(2)
            elif key == 'Max WallUy':
                ui.checkBox_15.setCheckState(2)
            elif key == 'Max SoilUy':
                ui.checkBox_13.setCheckState(2)
            elif key == 'FoS':
                ui.checkBox_14.setCheckState(2)
            ui.comboBox_40.addItem(key)
        ui.comboBox_40.blockSignals(False)
        ui.checkBox_12.blockSignals(False)
        ui.checkBox_15.blockSignals(False)
        ui.checkBox_13.blockSignals(False)
        ui.checkBox_14.blockSignals(False)


    @staticmethod
    def add_table_design_variables(tableWidget, v0, v_min, v_max):
        """ Reconstructs table for design variables
        """
        if v_min is not None:
            tableWidget.setColumnCount(v_min.size)
            tableWidget.setRowCount(3)
            param_labels = ['v' + str(param_cnt + 1) for param_cnt in range(v_min.size)]
            row_labels = ['v_min', 'v0', 'v_max']
            tableWidget.setHorizontalHeaderLabels(param_labels)
            tableWidget.setVerticalHeaderLabels(row_labels)

            for column_j in range(v_min.size):
                tableWidget.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(v_min[column_j])))
                tableWidget.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(v0[column_j])))
                tableWidget.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(v_max[column_j])))


    @staticmethod
    def add_table_design_variables_nsga2(tableWidget, v_min, v_max, v_subset):
        """ Reconstructs table for design variables
        """
        if v_min is not None:
            tableWidget.setColumnCount(v_min.size)
            tableWidget.setRowCount(3)
            param_labels = ['v' + str(param_cnt + 1) for param_cnt in range(v_min.size)]
            row_labels = ['v_min', 'v_max', 'v_subset']
            tableWidget.setHorizontalHeaderLabels(param_labels)
            tableWidget.setVerticalHeaderLabels(row_labels)

            for column_j in range(v_min.size):
                tableWidget.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(v_min[column_j])))
                tableWidget.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(v_max[column_j])))
                tableWidget.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(v_subset[column_j])))


    @staticmethod
    def show_sensitivity_scores(ui,  plot_canvas_sensitivity, sensitivity_scores, local_sensitivity):
        """ Shows sensitivity scores for 'Max WallUx'
        """
        if 'Max WallUx' in sensitivity_scores:
            ui.label_108.setText('Database file: {0}, number of samples: {1}'.format(local_sensitivity.path_output, local_sensitivity.iter_max))
            plot_canvas_sensitivity.plot_sensitivity_scores_optiman(sensitivity_scores['Max WallUx'])

            ui.comboBox_40.blockSignals(True)
            for idx in range(ui.comboBox_40.count()):
                if ui.comboBox_40.itemText(idx) == 'Max WallUx':
                    ui.comboBox_40.setCurrentIndex(idx)
                    break
            ui.comboBox_40.blockSignals(False)


    @staticmethod
    def show_optimization_results(ui,  plot_canvas_objectives, plaxman_ap, variables_wall, variables_anchors, variables_struts, variables_stone_columns, variables_fdc, solutions_nsga, objectives_nsga, iter_nsga=0):
        """ Shows (NSGAII) optimized designs
        """
        if solutions_nsga is not None:
            costs = [objective[0] for objective in objectives_nsga]
            displs = [objective[1] for objective in objectives_nsga]
            #plot_canvas_objectives.plot_objectives_2d(displs, costs, optiman_nsga2.iter, clear_axis=True, alpha=1.0, picker_size=5)
            plot_canvas_objectives.plot_objectives_2d(displs, costs, iter_nsga, clear_axis=True, alpha=1.0, picker_size=5, plaxman_ap=plaxman_ap, solutions=solutions_nsga, variables_wall=variables_wall, 
                                                    variables_anchors=variables_anchors, variables_struts=variables_struts, variables_stone_columns=variables_stone_columns, variables_fdc=variables_fdc)
