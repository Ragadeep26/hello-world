# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 14:55:56 2020

@author: nya
"""
import os, sys
from os.path import join, exists, isfile
import json
from random import randint
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QColor, QStandardItem
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSlot
from tools.json_functions import update_data_in_json_item, set_material_color
from tools.math import hex_to_rgb, rgb_to_integer
import solver.plaxis2d.input_scripting_commands as plaxis2d_input
from gui.gui_all_dialogs_ui import Ui_Dialog
from gui.gui_dialog_edit_all_soils_ui import Ui_Dialog as editSoilBox_allSoils
from gui.gui_dialog_edit_all_layers_ui import Ui_Dialog as editSoilBox_allLayers

class Plaxman_Extended():
    """ Extended Plaxman provides additional methods to Plaxman
    """
    def __init__(self, ui, plaxis2d_input_file, plot_canvas=None):
        """ Initializes Plaxman's Automated Phases
        """
        self.ui = ui
        self.plaxis2d_input_file = plaxis2d_input_file
        self.plot_canvas = plot_canvas
        self.dialog = Ui_Dialog()
        
        # connect signals to slots
        #self.connect_signals_to_slots()
        
        
    #def connect_signals_to_slots(self):
    #    """ Connects all signals to slots
    #    """
    #    self.ui.tableWidget_25.cellChanged.connect(lambda row, column: self.update_ground_anchor(row, column, Anchors)) # update ground anchor
    
                                                   
    def display_walls_on_table(self, Walls, active=True):
        """ Displays all ground anchors on table.
        Geometrical parameters are free to change.
        """
        self.ui.tableWidget_30.clear()
        self.ui.tableWidget_30.blockSignals(True) # temporarily block signals 
        column_labels = ['Wall_ID', 'Point top (x,y)' , 'Point bottom (x,y)', 'Material [-]']
        self.ui.tableWidget_30.setColumnCount(len(column_labels))
        self.ui.tableWidget_30.setRowCount(len(Walls))
        self.ui.tableWidget_30.setHorizontalHeaderLabels(column_labels)

        for row_i, wall in enumerate(Walls):
            item_id = QtWidgets.QTableWidgetItem(str(wall['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_30.setItem(row_i, 0, item_id) # id is read-only
            self.ui.tableWidget_30.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(wall['point1'][0]) + ', ' + str(wall['point1'][1])))
            self.ui.tableWidget_30.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(wall['point2'][0]) + ', ' + str(wall['point2'][1])))
            item_json = QtWidgets.QTableWidgetItem(str(wall['json_item']))
            item_json.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_30.setItem(row_i, 3, item_json) # json item is read-only
            
        if active == True:
            for row_i, wall in enumerate(Walls):
                self.ui.tableWidget_30.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_30.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                
        # connection for responding to values changed by user
        self.ui.tableWidget_30.blockSignals(False) # unblock signals 
        if active == True:
            self.ui.tableWidget_30.cellChanged.connect(lambda row, column: self.update_wall(row, column, Walls))


    @pyqtSlot()
    def update_wall(self, row, column, Walls):
        """ Updates walls online
        """
        try:
            text = self.ui.tableWidget_30.item(row, column).text()
            x, y = float(text.split(',')[0]), float(text.split(',')[1])
            soilcluster_keys = ['id', 'point1', 'point2']
            key = soilcluster_keys[column]
            wall_id = int(self.ui.tableWidget_30.item(row, 0).text())
            
            for wall in Walls:
                if wall['id'] == wall_id:
                    wall[key][0] = x
                    wall[key][1] = y
                    
                    # update plaxis2d input file
                    plaxis2d_input.update_wall(self.plaxis2d_input_file, 'g_i', wall)
                    
                    # repaint the waterlevel
                    self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])
                    wall['pathpatches'] = self.plot_canvas.plot_wall(wall, wall['color'])
                        
        except (ValueError, IndexError):
            self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')
            
    
    def display_ground_anchors_on_table(self, Anchors, table_widget, active=True, signal_connection=True):
        """ Displays all ground anchors on table
        Geometrical parameters are free to change.
        signal_connection=False: do not connect signal the second time, update the table for ground anchors only
        """
        table_widget.clear()
        table_widget.blockSignals(True) # temporarily block signals from tableWidget_25 to avoid call slot update_ground_anchor before the table is filled
        column_labels = ['GroundAnchor_ID', 'Level [m]' , 'Angle [degr.]', 'Free length [m]', 'Fixed length [m]', 'Lspacing [m]', 'F_prestress [kN]', 'Strand material [-]', 'Grout material [-]']
        table_widget.setColumnCount(len(column_labels))
        table_widget.setRowCount(len(Anchors))
        table_widget.setHorizontalHeaderLabels(column_labels)

        for row_i, anchor in enumerate(Anchors):
            item_id = QtWidgets.QTableWidgetItem(str(anchor['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(row_i, 0, item_id) # id is read-only
            table_widget.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(anchor['position'][1])))
            table_widget.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(anchor['angle'])))
            table_widget.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(anchor['length_free'])))
            table_widget.setItem(row_i, 4, QtWidgets.QTableWidgetItem(str(anchor['length_fixed'])))
            Lspacing = self.get_Lspacing(anchor['grout_json_item'])
            table_widget.setItem(row_i, 5, QtWidgets.QTableWidgetItem(str(Lspacing)))
            table_widget.setItem(row_i, 6, QtWidgets.QTableWidgetItem(str(anchor['F_prestress'])))
            item_json_strand = QtWidgets.QTableWidgetItem(anchor['strand_json_item'])
            item_json_strand.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(row_i, 7, item_json_strand) # json item is read-only
            item_json_grout = QtWidgets.QTableWidgetItem(anchor['grout_json_item'])
            item_json_grout.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(row_i, 8, item_json_grout) # json item is read-only
        
        if active == True:
            for row_i, anchor in enumerate(Anchors):
                table_widget.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 4).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 5).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 6).setBackground(QColor(242, 255, 116)) # light yellow

        # connection for responding to values changed by user
        table_widget.blockSignals(False) # unblock signals from tableWidget_25
        if signal_connection == True:
            if active == True:
                table_widget.cellChanged.connect(lambda row, column: self.update_ground_anchor(row, column, Anchors, table_widget))
    

    def display_ground_anchors_comboboxes(self, Anchors, combobox_grout, combobox_strand):
        """ Displays lists for grout and strand materials
        """
        combobox_grout.clear()
        combobox_strand.clear()
        for anchor in Anchors:
            combobox_strand.addItem(anchor['strand_json_item'])     # combobox_37
            combobox_grout.addItem(anchor['grout_json_item'])      # combobox_38


    @pyqtSlot()
    def update_ground_anchor(self, row, column, Anchors, table_widget):
        """ Updates ground anchors online
        """
        #print(row, column)
        #print(Anchors)
        if column < 7:
            if table_widget.item(row, column):
                try:
                    value = float(table_widget.item(row, column).text())
                    anchor_keys = ('id', 'level', 'angle', 'length_free', 'length_fixed', 'Lspacing', 'F_prestress')
                    key = anchor_keys[column]
                    anchor_id = int(table_widget.item(row, 0).text())
    
                    self.update_ground_anchor_by_id__(anchor_id, key, value, Anchors)
                    print('Anchor {id}, {key} = {value}'.format(id=anchor_id, key=key, value=value))

                    # update Lspacing for all anchors 
                    if key == 'Lspacing':
                        self.display_ground_anchors_on_table(Anchors, table_widget, signal_connection=False)
    
                except ValueError:
                    self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')


    def update_ground_anchor_by_id__(self, anchor_id, key, value, Anchors):
        """ Updates ground anchor (indexed by id)
        """
        for anchor in Anchors:
            if anchor['id'] == anchor_id:
                if key != 'level':
                    anchor[key] = value
                    if key == 'Lspacing':
                        update_data_in_json_item(anchor['strand_json_item'], {'Lspacing': anchor['Lspacing']})
                        update_data_in_json_item(anchor['grout_json_item'], {'Lspacing': anchor['Lspacing']})
                else: # level
                    anchor['position'][1] = value

                # update plaxis2d input file
                plaxis2d_input.update_ground_anchor(self.plaxis2d_input_file, 'g_i', anchor)

                # repaint the groundanchor
                self.plot_canvas.undo_plot_pathpatches(anchor['pathpatches'])
                anchor['pathpatches'] = self.plot_canvas.plot_ground_anchor(anchor)
                #break
    
    
    def get_Lspacing(self, json_item):
        """ Gets Lspacing value for a groundanchor/ strut
        """
        PATHS = sys.modules['moniman_paths']
        PATH_MATERIAL = os.path.join(PATHS['MONIMAN_OUTPUTS'], r'materials')
        fname = os.path.join(PATH_MATERIAL, json_item + '.json')
        if os.path.isfile(fname):
            with open(fname, "r") as read_file:
                materials_data = json.load(read_file, object_pairs_hook = OrderedDict)         
                return(materials_data['Lspacing'])
        else: # json file does not exist
            materials_data = None
            return None



    def display_struts_on_table(self, Struts, table_widget, active=True):
        """ Displays all struts on table.
        Geometrical parameters are free to change.
        """
        table_widget.clear()
        table_widget.blockSignals(True) # temporarily block signals from tableWidget_26 to avoid call slot update_ground_anchor before the table is filled
        column_labels = ['Strut_ID', 'Level [m]' , 'Lspacing [m]', 'Span x [m]', 'Span y [m]', 'F_prestress [kN]', 'Strut material [-]']
        table_widget.setColumnCount(len(column_labels))
        table_widget.setRowCount(len(Struts))
        table_widget.setHorizontalHeaderLabels(column_labels)

        for row_i, strut in enumerate(Struts):
            item_id = QtWidgets.QTableWidgetItem(str(strut['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(row_i, 0, item_id) # id is read-only
            table_widget.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(strut['position'][1])))
            Lspacing = self.get_Lspacing(strut['json_item'])
            table_widget.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(Lspacing)))
            table_widget.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(strut['direct_x'])))
            table_widget.setItem(row_i, 4, QtWidgets.QTableWidgetItem(str(strut['direct_y'])))
            table_widget.setItem(row_i, 5, QtWidgets.QTableWidgetItem(str(strut['F_prestress'])))
            item_json = QtWidgets.QTableWidgetItem(strut['json_item'])
            item_json.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(row_i, 6, item_json) # json item is read-only

        if active == True:
            for row_i, strut in enumerate(Struts):
                table_widget.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 4).setBackground(QColor(242, 255, 116)) # light yellow
                table_widget.item(row_i, 5).setBackground(QColor(242, 255, 116)) # light yellow

        # connection for responding to values changed by user
        table_widget.blockSignals(False) # unblock signals from tableWidget_18
        if active == True:
            table_widget.cellChanged.connect(lambda row, column: self.update_strut(row, column, Struts, table_widget))
        
        
    @pyqtSlot()
    def update_strut(self, row, column, Struts, table_widget):
        """ Updates struts online
        """
        #print(row, column)
        #print(Struts)
        if column < 6:
            if table_widget.item(row, column):
                try:
                    value = float(table_widget.item(row, column).text())
                    anchor_keys = ('id', 'level', 'Lspacing', 'direct_x', 'direct_y', 'F_prestress')
                    key = anchor_keys[column]
                    strut_id = int(table_widget.item(row, 0).text())
    
                    for strut in Struts:
                        if strut['id'] == strut_id:
                            if key != 'level':
                                strut[key] = value
                                print('Strut {id}, {key} = {value}'.format(id=strut_id, key=key, value=value))
                                if key == 'Lspacing':
                                    update_data_in_json_item(strut['json_item'], {'Lspacing': strut['Lspacing']})
                            else: # level
                                strut['position'][1] = value
                                print('Strut {id} is at level {level}'.format(id=strut_id, level=value))
    
                            # update plaxis2d input file
                            plaxis2d_input.update_strut(self.plaxis2d_input_file, 'g_i', strut)
    
                            # repaint the groundanchor
                            self.plot_canvas.undo_plot_pathpatches(strut['pathpatches'])
                            strut['pathpatches'] = self.plot_canvas.plot_strut(strut)
                            #break
    
                except ValueError:
                    self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')



    def display_waterlevels_on_table(self, Waterlevels, active=True):
        """ Displays all user water levels on table.
        Geometrical parameters are free to change.
        """
        self.ui.tableWidget_28.clear()
        self.ui.tableWidget_28.blockSignals(True) # temporarily block signals
        column_labels = ['WaterLevel_ID', 'Level [m]']
        self.ui.tableWidget_28.setColumnCount(len(column_labels))
        self.ui.tableWidget_28.setRowCount(len(Waterlevels))
        self.ui.tableWidget_28.setHorizontalHeaderLabels(column_labels)
        
        for row_i, waterlevel in enumerate(Waterlevels):
            item_id = QtWidgets.QTableWidgetItem(str(waterlevel['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_28.setItem(row_i, 0, item_id) # id is read-only
            self.ui.tableWidget_28.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(min(waterlevel['pointL'][1], waterlevel['pointR'][1]))))
            
        if active == True:
            for row_i, waterlevel in enumerate(Waterlevels):
                self.ui.tableWidget_28.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                
        # connection for responding to values changed by user
        self.ui.tableWidget_28.blockSignals(False) # unblock signals
        if active == True:
            self.ui.tableWidget_28.cellChanged.connect(lambda row, column: self.update_waterlevel(row, column, Waterlevels))
            
    
    @pyqtSlot()
    def update_waterlevel(self, row, column, Waterlevels):
        """ Updates struts online
        """
        if column == 1:
            if self.ui.tableWidget_28.item(row, column):
                try:
                    value = float(self.ui.tableWidget_28.item(row, column).text())
                    waterlevel_id = int(self.ui.tableWidget_28.item(row, 0).text())
                    
                    for waterlevel in Waterlevels:
                        if waterlevel['id'] == waterlevel_id:
                            waterlevel['pointL'][1] = value
                            waterlevel['pointR'][1] = value
                            
                            # update plaxis2d input file
                            plaxis2d_input.update_waterlevel(self.plaxis2d_input_file, 'g_i', waterlevel)
                            
                            # repaint the waterlevel
                            self.plot_canvas.undo_plot_pathpatches(waterlevel['pathpatches'])
                            waterlevel['pathpatches'] = self.plot_canvas.plot_waterlevel(waterlevel)
                                
                except ValueError:
                    self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')
                    
                    
    def display_soilclusters_on_table(self, Soilclusters__, active=True):
        """ Displays all soil clusters on table. Only retangular soil clusters are displayed.
        Geometrical parameters are free to change.
        """
        Soilclusters = [soilcluster for soilcluster in Soilclusters__ if soilcluster['isRectangular'] is True]      # only rectangular soil clusters
        
        self.ui.tableWidget_29.clear()
        self.ui.tableWidget_29.blockSignals(True) # temporarily block signals
        column_labels = ['WaterLevel_ID', 'PointTL (x,y)', 'PointTR (x,y)', 'PointBL (x,y)', 'PointBR (x,y)']
        self.ui.tableWidget_29.setColumnCount(len(column_labels))
        self.ui.tableWidget_29.setRowCount(len(Soilclusters))
        self.ui.tableWidget_29.setHorizontalHeaderLabels(column_labels)
        
        for row_i, soilcluster in enumerate(Soilclusters):
            item_id = QtWidgets.QTableWidgetItem(str(soilcluster['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_29.setItem(row_i, 0, item_id) # id is read-only
            self.ui.tableWidget_29.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(soilcluster['pointTL'][0]) + ', ' + str(soilcluster['pointTL'][1])))
            self.ui.tableWidget_29.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(soilcluster['pointTR'][0]) + ', ' + str(soilcluster['pointTR'][1])))
            self.ui.tableWidget_29.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(soilcluster['pointBL'][0]) + ', ' + str(soilcluster['pointBL'][1])))
            self.ui.tableWidget_29.setItem(row_i, 4, QtWidgets.QTableWidgetItem(str(soilcluster['pointBR'][0]) + ', ' + str(soilcluster['pointBR'][1])))
            
        if active == True:
            for row_i, soilcluster in enumerate(Soilclusters):
                self.ui.tableWidget_29.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_29.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_29.item(row_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_29.item(row_i, 4).setBackground(QColor(242, 255, 116)) # light yellow
                
        # connection for responding to values changed by user
        self.ui.tableWidget_29.blockSignals(False) # unblock signals 
        if active == True:
            self.ui.tableWidget_29.cellChanged.connect(lambda row, column: self.update_soilcluster(row, column, Soilclusters))
            
            
    @pyqtSlot()
    def update_soilcluster(self, row, column, Soilclusters):
        """ Updates struts online
        """
        try:
            text = self.ui.tableWidget_29.item(row, column).text()
            x, y = float(text.split(',')[0]), float(text.split(',')[1])
            soilcluster_keys = ['id', 'pointTL', 'pointTR', 'pointBL', 'pointBR']
            key = soilcluster_keys[column]
            soilcluster_id = int(self.ui.tableWidget_29.item(row, 0).text())
            
            for soilcluster in Soilclusters:
                if soilcluster['id'] == soilcluster_id:
                    soilcluster[key][0] = x
                    soilcluster[key][1] = y
                    
                    # update plaxis2d input file
                    plaxis2d_input.update_soilcluster(self.plaxis2d_input_file, 'g_i', soilcluster)
                    
                    # repaint the waterlevel
                    self.plot_canvas.undo_plot_pathpatches(soilcluster['pathpatches'])
                    soilcluster['pathpatches'] = self.plot_canvas.plot_soilcluster(soilcluster)
                        
        except (ValueError, IndexError):
            self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')
            
            
    def display_lineloads_on_table(self, Lineloads, y_min, y_max, active=True):
        """ Displays all line loads on table.
        Geometrical parameters are free to change.
        y_min, y_max: for plotting only
        """
        self.ui.tableWidget_31.clear()
        self.ui.tableWidget_31.blockSignals(True) # temporarily block signals 
        column_labels = ['Lineload_ID', 'Point 1 (x,y)' , 'Point 2 (x,y)', 'qx [kN/m/m]', 'qy [kN/m/m]']
        self.ui.tableWidget_31.setColumnCount(len(column_labels))
        self.ui.tableWidget_31.setRowCount(len(Lineloads))
        self.ui.tableWidget_31.setHorizontalHeaderLabels(column_labels)

        for row_i, lload in enumerate(Lineloads):
            item_id = QtWidgets.QTableWidgetItem(str(lload['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_31.setItem(row_i, 0, item_id) # id is read-only
            self.ui.tableWidget_31.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(lload['point1'][0]) + ', ' + str(lload['point1'][1])))
            self.ui.tableWidget_31.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(lload['point2'][0]) + ', ' + str(lload['point2'][1])))
            self.ui.tableWidget_31.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(lload['qx'])))
            self.ui.tableWidget_31.setItem(row_i, 4, QtWidgets.QTableWidgetItem(str(lload['qy'])))            
           
        if active == True:
            for row_i, wall in enumerate(Lineloads):
                self.ui.tableWidget_31.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_31.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_31.item(row_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_31.item(row_i, 4).setBackground(QColor(242, 255, 116)) # light yellow
                
        # connection for responding to values changed by user
        self.ui.tableWidget_31.blockSignals(False) # unblock signals 
        if active == True:
            self.ui.tableWidget_31.cellChanged.connect(lambda row, column: self.update_lineload(row, column, Lineloads, y_min, y_max))

        
    @pyqtSlot()
    def update_lineload(self, row, column, Lineloads, y_min, y_max):
        """ Updates line loads online
        """
        try:
            text = self.ui.tableWidget_31.item(row, column).text()
            lload_keys = ['id', 'point1', 'point2', 'qx', 'qy']
            key = lload_keys[column]
            lload_id = int(self.ui.tableWidget_31.item(row, 0).text())
            
            for lload in Lineloads:
                if lload['id'] == lload_id:
                    if (key == 'point1') or (key == 'point2'):
                        x, y = float(text.split(',')[0]), float(text.split(',')[1])
                        lload[key][0] = x
                        lload[key][1] = y
                    else: # key == qx or qy
                        value = float(text)
                        lload[key] = value
                    
                    # update plaxis2d input file
                    plaxis2d_input.update_lineload(self.plaxis2d_input_file, 'g_i', lload)
                    
                    # repaint the waterlevel
                    self.plot_canvas.undo_plot_pathpatches(lload['pathpatches'])
                    lload['pathpatches'] = self.plot_canvas.plot_lineload(lload, y_min, y_max,)
                        
        except (ValueError, IndexError):
            self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')

            
    def display_pointloads_on_table(self, Pointloads, y_min, y_max, active=True):
        """ Displays all point loads on table.
        Geometrical parameters are free to change.
        y_min, y_max: for plotting only
        """
        self.ui.tableWidget_32.clear()
        self.ui.tableWidget_32.blockSignals(True) # temporarily block signals 
        column_labels = ['Wall_ID', 'Point (x,y)' , 'Fx [kN/m]', 'Fy [kN/m]']
        self.ui.tableWidget_32.setColumnCount(len(column_labels))
        self.ui.tableWidget_32.setRowCount(len(Pointloads))
        self.ui.tableWidget_32.setHorizontalHeaderLabels(column_labels)

        for row_i, pload in enumerate(Pointloads):
            item_id = QtWidgets.QTableWidgetItem(str(pload['id']))
            item_id.setFlags(Qt.ItemIsEnabled)
            self.ui.tableWidget_32.setItem(row_i, 0, item_id) # id is read-only
            self.ui.tableWidget_32.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(pload['point'][0]) + ', ' + str(pload['point'][1])))
            self.ui.tableWidget_32.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(pload['Fx'])))
            self.ui.tableWidget_32.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(pload['Fy'])))            
           
        if active == True:
            for row_i, wall in enumerate(Pointloads):
                self.ui.tableWidget_32.item(row_i, 1).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_32.item(row_i, 2).setBackground(QColor(242, 255, 116)) # light yellow
                self.ui.tableWidget_32.item(row_i, 3).setBackground(QColor(242, 255, 116)) # light yellow
                
        # connection for responding to values changed by user
        self.ui.tableWidget_32.blockSignals(False) # unblock signals 
        if active == True:
            self.ui.tableWidget_32.cellChanged.connect(lambda row, column: self.update_pointload(row, column, Pointloads, y_min, y_max))

            
    @pyqtSlot()
    def update_pointload(self, row, column, Pointloads, y_min, y_max):
        """ Updates line loads online
        """
        try:
            text = self.ui.tableWidget_32.item(row, column).text()
            pload_keys = ['id', 'point', 'Fx', 'Fy']
            key = pload_keys[column]
            pload_id = int(self.ui.tableWidget_32.item(row, 0).text())
            
            for pload in Pointloads:
                if pload['id'] == pload_id:
                    if (key == 'point'):
                        x, y = float(text.split(',')[0]), float(text.split(',')[1])
                        pload[key][0] = x
                        pload[key][1] = y
                    else: # key == qx or qy
                        value = float(text)
                        pload[key] = value
                    
                    # update plaxis2d input file
                    plaxis2d_input.update_pointload(self.plaxis2d_input_file, 'g_i', pload)
                    
                    # repaint the waterlevel
                    self.plot_canvas.undo_plot_pathpatches(pload['pathpatches'])
                    pload['pathpatches'] = self.plot_canvas.plot_pointload(pload, y_min, y_max,)
                        
        except (ValueError, IndexError):
            self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')
            

    def process_adding_layer(self, Layer_polygons, Boreholes, tops, bottoms, geometry, active=True):
        """ Process adding a layer, shows layering information on table and connect signals
        Geometrical parameters are free to change.
        """
        x_min = geometry[0]
        x_max = geometry[2]

        NUMBER_layer = len(Layer_polygons)
        layer_polygon = {}
        layer_polygon['id'] = randint(100000, 999999) # identification for deleting a layer
        plaxis2d_input.add_layer(self.plaxis2d_input_file, 'g_i', NUMBER_layer + 1, layer_polygon['id'])
        self.ui.tableWidget.blockSignals(True) # temporarily block signals 
        
        for borehole_i, borehole in enumerate(Boreholes):
            # Register top and bottom
            borehole['Top'].append(tops[borehole_i])
            borehole['Bottom'].append(bottoms[borehole_i])
            
            # Assign the next layer's top equal to the current layer's bottom and an initial zeor thickness
            self.ui.tableWidget.setItem(NUMBER_layer + 1, 2*borehole_i, QtWidgets.QTableWidgetItem(str(borehole['Bottom'][-1])))
            self.ui.tableWidget.setItem(NUMBER_layer + 1, 2*borehole_i + 1, QtWidgets.QTableWidgetItem(str(borehole['Bottom'][-1])))

            # Set bottom cell as read-only and paint background color for top cells
            cell_top = self.ui.tableWidget.item(NUMBER_layer, 2*borehole_i)
            cell_bottom = self.ui.tableWidget.item(NUMBER_layer, 2*borehole_i + 1)
            cell_bottom.setFlags(cell_bottom.flags() ^ Qt.ItemIsEditable)
            cell_top.setBackground(QColor(242, 255, 116)) # light yellow
            self.ui.tableWidget.item(NUMBER_layer+1, 2*borehole_i).setBackground(QColor(242, 255, 116)) # light yellow, predictive layer

            # Adjust y_min and borehole when bottom of the layer is less than the current y_min
            if float(borehole['Bottom'][-1]) < geometry[1]: 
                geometry[1] = float(borehole['Bottom'][-1])
                self.ui.lineEdit_2.setText(str(geometry[1]))
                #redraw borehole
                self.plot_canvas.undo_plot_pathpatches(borehole['pathpatches'])
                borehole['pathpatches'] = self.plot_canvas.plot_borehole(len(Boreholes), borehole, geometry)

        for borehole_i, borehole in enumerate(Boreholes):
            plaxis2d_input.add_layer_values(self.plaxis2d_input_file, 'g_i', borehole_i+1, NUMBER_layer, borehole['Top'][-1], borehole['Bottom'][-1])
        NUMBER_layer += 1
        print('Soil layer {} is added'.format(NUMBER_layer))
        path_polygon, pathpatch_top, pathpatch_bottom, annotation = self.plot_canvas.plot_layer(Boreholes, NUMBER_layer - 1, x_min, x_max)
                    
        layer_polygon['path_polygon'] = path_polygon
        layer_polygon['pathpatch_top'] = pathpatch_top
        layer_polygon['pathpatch_bottom'] = pathpatch_bottom
        layer_polygon['pathpatches'] = annotation   # holds only the pathpatch for annotation for now
        layer_polygon['shaded'] = False
        layer_polygon['pathpatch_layer'] = None
        layer_polygon['soilmaterial_layer'] = None

        #NUMBER_layer += 1
        # Update layer table and add a new layer for later material assignment
        item_defined = self.ui.tableWidget.verticalHeaderItem(NUMBER_layer-1)
        item_defined.setText(QCoreApplication.translate("MainWindow", "Layer " + str(NUMBER_layer)))
        item_next = self.ui.tableWidget.verticalHeaderItem(NUMBER_layer)
        item_next.setText(QCoreApplication.translate("MainWindow", "(Layer " + str(NUMBER_layer + 1) + ")"))

        # Show layers in combobox
        self.ui.comboBox_4.addItem("Layer " + str(NUMBER_layer))
        
        # connect signal to slot
        self.ui.tableWidget.blockSignals(False) # unblock signals 
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_layer(row, column, Layer_polygons, Boreholes, geometry))

        return layer_polygon
        
        
    def display_layers_on_table(self, Layer_polygons, Boreholes, geometry, active=True):
        """ Displays all layer polygons on table and connect signals
        Geometrical parameters are free to change.
        """
        self.ui.tableWidget.blockSignals(True) # temporarily block signals 
        #self.ui.tableWidget.clear()
        # add layer values
        i = 0
        for i, layer_polygon in enumerate(Layer_polygons):
            item = self.ui.tableWidget.verticalHeaderItem(i)
            item.setText(QCoreApplication.translate("MainWindow", "Layer " + str(i+1)))

            for j, borehole in enumerate(Boreholes):
                self.ui.tableWidget.setItem(i, 2*j, QtWidgets.QTableWidgetItem(str(borehole['Top'][i])))
                self.ui.tableWidget.setItem(i, 2*j + 1, QtWidgets.QTableWidgetItem(str(borehole['Bottom'][i])))
               
                self.ui.tableWidget.item(i, 2*j + 1).setFlags(self.ui.tableWidget.item(i, 2*j + 1).flags() ^ Qt.ItemIsEditable)     # read-only for bottom
                self.ui.tableWidget.item(i, 2*j).setBackground(QColor(242, 255, 116))  # light yellow
            
            item_next = self.ui.tableWidget.verticalHeaderItem(i + 1)
            item_next.setText(QCoreApplication.translate("MainWindow", "(Layer " + str(i+2) + ")"))

        # suggest next layer
        for j, borehole in enumerate(Boreholes):
            if borehole['Bottom']:
                self.ui.tableWidget.setItem(i + 1, 2*j, QtWidgets.QTableWidgetItem(str(borehole['Bottom'][-1])))
                # paint background color of top as light yellow for the last row
                self.ui.tableWidget.item(i+1, 2*j).setBackground(QColor(242, 255, 116))

        if len(Layer_polygons) == 0: # layers are emtpy
            for j, borehole in enumerate(Boreholes):
                self.ui.tableWidget.setItem(0, 2*j, QtWidgets.QTableWidgetItem(str(geometry[3])))
                self.ui.tableWidget.setItem(0, 2*j + 1, QtWidgets.QTableWidgetItem(str(geometry[1])))
                item = self.ui.tableWidget.verticalHeaderItem(0)
                item.setText(QCoreApplication.translate("MainWindow", "(Layer " + str(1) + ")"))
                item_next = self.ui.tableWidget.verticalHeaderItem(1)
                item_next.setText(QCoreApplication.translate("MainWindow", ""))
                self.ui.tableWidget.setItem(1, 2*j, QtWidgets.QTableWidgetItem(''))
                self.ui.tableWidget.setItem(1, 2*j + 1, QtWidgets.QTableWidgetItem(''))
        
         # connect signal to slot
        self.ui.tableWidget.blockSignals(False) # unblock signals 
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_layer(row, column, Layer_polygons, Boreholes, geometry))
        
        
    @pyqtSlot()
    def update_layer(self, row, column, Layer_polygons, Boreholes, geometry):
        """ Processes layer change
        """
        #print(row)
        #print(column)
        self.ui.tableWidget.blockSignals(True) # temporarily block signals 
        index_layer = row
        index_borehole_item = column
        index_borehole = int(index_borehole_item/2)
        x_min = geometry[0]
        x_max = geometry[2]
        if (index_layer < len(Layer_polygons) + 1) and (index_borehole < len(Boreholes)) and (index_borehole_item % 2 == 0): # except also change in borehole bottom
            #if (index_layer == len(Layer_polygons)) and (self.ui.tableWidget.item(index_layer, index_borehole_item + 1) is None) and (index_layer > 0): # bottom of the last layer
            if index_layer == 0: # top of the last layer, update top of model and replot borehole
                geometry[3] = float(self.ui.tableWidget.item(row, column).text())# y_max
                self.ui.lineEdit_4.setText(str(geometry[3]))
                #redraw borehole
                self.plot_canvas.undo_plot_pathpatches(Boreholes[index_borehole]['pathpatches'])
                Boreholes[index_borehole]['pathpatches'] = self.plot_canvas.plot_borehole(len(Boreholes), Boreholes[index_borehole], geometry)

            if (index_layer == len(Layer_polygons)) and (index_layer > 0): # bottom of the last layer
                # update bottom of the current layer
                Boreholes[index_borehole]['Bottom'][index_layer - 1] = float(self.ui.tableWidget.item(row, column).text())
                self.ui.tableWidget.setItem(index_layer - 1, index_borehole_item + 1, QtWidgets.QTableWidgetItem(str(Boreholes[index_borehole]['Bottom'][index_layer - 1])))
                self.plot_canvas.undo_plot_pathpatches((Layer_polygons[-1]['pathpatch_top'], Layer_polygons[-1]['pathpatch_bottom'], Layer_polygons[-1]['pathpatches']))
                # update y_min as well when bottom of the last soil layer is updated
                geometry[1] = float(self.ui.tableWidget.item(row, column).text())
                self.ui.lineEdit_2.setText(str(geometry[1]))
                ##redraw borehole
                ##self.plot_canvas.undo_plot_pathpatches(Boreholes[index_borehole]['pathpatches'])
                ##Boreholes[index_borehole]['pathpatches'] = self.plot_canvas.plot_borehole(len(Boreholes), Boreholes[index_borehole], geometry)
                #self.plot_canvas.undo_plot_pathpatches(Layer_polygons[-1]['pathpatch_layer'])
                Layer_polygons[-1]['path_polygon'], Layer_polygons[-1]['pathpatch_top'], Layer_polygons[-1]['pathpatch_bottom'], Layer_polygons[-1]['pathpatches'] = self.plot_canvas.plot_layer(Boreholes, len(Layer_polygons) - 1, x_min, x_max)
                if Layer_polygons[-1]['shaded'] == True:
                    self.plot_canvas.undo_plot_pathpatches(Layer_polygons[-1]['pathpatch_layer'])
                    Layer_polygons[-1]['pathpatch_layer'] = self.plot_canvas.plot_assigned_layer(Layer_polygons[-1]['path_polygon'], Layer_polygons[-1]['color'])

                # update plaxis input file
                plaxis2d_input.remove_structure(self.plaxis2d_input_file, Layer_polygons[-1]['id'], '##SOIL_LAYER', 2 + int(3*len(Boreholes)))
                # add the same soil layer again with updated values
                plaxis2d_input.add_layer(self.plaxis2d_input_file, 'g_i', len(Layer_polygons) - 1, Layer_polygons[-1]['id'])
                for j, borehole in enumerate(Boreholes):
                    plaxis2d_input.add_layer_values(self.plaxis2d_input_file, 'g_i', j + 1, len(Layer_polygons) - 1, borehole['Top'][-1], borehole['Bottom'][-1])
                # adjust y_min of the model
                geometry[1] = Boreholes[index_borehole]['Bottom'][index_layer - 1] #x_min, y_min, x_max, y_max
                self.plot_canvas.undo_plot_pathpatches(Boreholes[index_borehole]['pathpatches'])
                Boreholes[index_borehole]['pathpatches'] = self.plot_canvas.plot_borehole(len(Boreholes), Boreholes[index_borehole], geometry)
                print(geometry[1])

            elif (index_layer < len(Layer_polygons)): # upper layers (without bottom layer)
                # update top of the current layer
                Boreholes[index_borehole]['Top'][index_layer] = float(self.ui.tableWidget.item(row, column).text())

                # bottom of the previous layer is set to top of the current layer
                if (index_layer > 0): # except change in the first layer 
                    Boreholes[index_borehole]['Bottom'][index_layer - 1] = Boreholes[index_borehole]['Top'][index_layer]
                    self.ui.tableWidget.setItem(index_layer - 1, index_borehole_item + 1, QtWidgets.QTableWidgetItem(str(Boreholes[index_borehole]['Bottom'][index_layer - 1])))
                    self.ui.tableWidget.item(index_layer - 1, index_borehole_item + 1).setFlags(self.ui.tableWidget.item(index_layer - 1, index_borehole_item + 1).flags() ^ Qt.ItemIsEditable)
            
                # remove and replot layers
                for i, layer_polygon in enumerate(Layer_polygons):
                    self.plot_canvas.undo_plot_pathpatches((layer_polygon['pathpatch_top'], layer_polygon['pathpatch_bottom'], layer_polygon['pathpatches']))
                    layer_polygon['path_polygon'], layer_polygon['pathpatch_top'], layer_polygon['pathpatch_bottom'], layer_polygon['pathpatches'] = self.plot_canvas.plot_layer(Boreholes, i, x_min, x_max)

                    if layer_polygon['shaded'] == True: # if soil material has been assigned to layer
                        self.plot_canvas.undo_plot_pathpatches(layer_polygon['pathpatch_layer'])
                        layer_polygon['pathpatch_layer'] = self.plot_canvas.plot_assigned_layer(layer_polygon['path_polygon'], layer_polygon['color'])
                        self.ui.tableWidget.item(i, index_borehole_item + 1).setBackground(QColor(layer_polygon['color']))
            
                # update plaxis input file
                for i, layer_polygon in enumerate(Layer_polygons):
                    # remove soil layer
                    plaxis2d_input.remove_structure(self.plaxis2d_input_file, layer_polygon['id'], '##SOIL_LAYER', 2 + int(3*len(Boreholes)))

                    # add the same soil layer again with updated values
                    plaxis2d_input.add_layer(self.plaxis2d_input_file, 'g_i', i + 1, layer_polygon['id'])
                    for j, borehole in enumerate(Boreholes):
                        plaxis2d_input.add_layer_values(self.plaxis2d_input_file, 'g_i', j + 1, i, borehole['Top'][i], borehole['Bottom'][i])

        self.ui.tableWidget.blockSignals(False) # unblock signals 


    def remove_last_layer(self, Layer_polygons, Boreholes, geometry):
        """ Remove the last soil layer
        """
        shaded_states = [item['shaded'] for item in Layer_polygons]
        if any(shaded_states):
            self.dialog.show_message_box('Warning', 'Please undo material assignments first!')

        else:    
            NUMBER_layer = len(Layer_polygons)
            self.ui.tableWidget.blockSignals(True)  # temporary block signals
            # Remove the last soil layer
            if len(Layer_polygons) > 0:
                deleted_polygon = Layer_polygons.pop()
                NUMBER_layer = NUMBER_layer - 1
                self.plot_canvas.undo_plot_pathpatches((deleted_polygon['pathpatch_top'], deleted_polygon['pathpatch_bottom'], deleted_polygon['pathpatches']))
            
                for column_i in range(self.ui.tableWidget.columnCount()):
                    self.ui.tableWidget.setItem(NUMBER_layer + 1, column_i, QtWidgets.QTableWidgetItem(''))
                    self.ui.tableWidget.setItem(NUMBER_layer , 2*column_i + 1, QtWidgets.QTableWidgetItem(''))
                    
                item_removed = self.ui.tableWidget.verticalHeaderItem(NUMBER_layer+1)
                item_removed.setText(QCoreApplication.translate("MainWindow", ""))
                item_next = self.ui.tableWidget.verticalHeaderItem(NUMBER_layer)
                item_next.setText(QCoreApplication.translate("MainWindow", "(Layer " + str(NUMBER_layer+1) + ")"))
                
                self.ui.comboBox_4.removeItem(self.ui.comboBox_4.count() - 1)
                
                print('The last soil layer is removed, {} layers remain'.format(len(Layer_polygons)))
            
                plaxis2d_input.remove_structure(self.plaxis2d_input_file, deleted_polygon['id'], '##SOIL_LAYER', 2 + int(3*len(Boreholes)))

                # Remove Top and Bottom of the most recent layer in Boreholes
                for borehole in Boreholes:
                    borehole['Top'].pop()
                    borehole['Bottom'].pop()

                self.ui.tableWidget.blockSignals(False)  # unblock signals

                # Displays and connects signals
                self.display_layers_on_table(Layer_polygons, Boreholes, geometry, self.ui.tableWidget)


    def process_assigning_material(self, json_item, i_layer, Soilmaterials, Layer_polygons, Boreholes):
        """ Processes assigning material to soil layer
        """
        # get color from the selected soil material
        for soilmat in Soilmaterials:
            if soilmat['json_item'] == json_item:
                color = soilmat['color']

        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        material_file_path = join(PATH_MATERIAL_LIBRARY, json_item + '.json')
        material_moniman_file_path = join(PATH_MATERIAL_LIBRARY, json_item + 'moniman.json')
                
        #current_layer = self.ui.comboBox_4.currentText().split()
        
        if Layer_polygons[i_layer]['shaded'] == True:
            self.dialog.show_message_box('Warning', 'Please unassign material before reassignment!')
            
        elif not isfile(material_file_path):
            self.dialog.show_message_box('Warning', 'Please edit soil properties!')
        
        else:                            
            layer_polygon = Layer_polygons[i_layer]['path_polygon']
            Layer_polygons[i_layer]['shaded'] = True
            #color = self.current_material_color.name()
            layer_pathpatch = self.plot_canvas.plot_assigned_layer(layer_polygon, color)
            Layer_polygons[i_layer]['pathpatch_layer'] = layer_pathpatch
            Layer_polygons[i_layer]['color'] = color

            # write to python file
            plaxis2d_input.assign_soil_to_layer(self.plaxis2d_input_file, 'g_i', i_layer+1, json_item, material_file_path)
            
            # update the list of soil materials            
            soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in Soilmaterials]
            if json_item not in soilmaterial_json_items:
                Soilmaterials.append({'json_item': json_item, 'soil_model': None, 'correlations_ve': False})
                #self.ui.comboBox_17.addItem(self.material_json_item)
            Layer_polygons[i_layer]['soilmaterial_layer'] = json_item
            Layer_polygons[i_layer]['Tskin'] = 200.0 # friction bearing capacity in [kN/m]
                               
            # set material colour
            set_material_color(material_file_path, color)
            set_material_color(material_moniman_file_path, color)
            for col in range(1, 2*len(Boreholes), 2):
                self.ui.tableWidget.item(i_layer, col).setBackground(QColor(*hex_to_rgb(color)))
            # show material name in soil layer
            item = self.ui.tableWidget.verticalHeaderItem(i_layer)
            item.setText(QCoreApplication.translate("MainWindow", json_item))
            
            print('Material properties file: {}'.format(material_file_path))
            print('Material {0} has been assigned to Layer {1}'.format(json_item, i_layer+1))


    def undo_all_assign_materials(self, Layer_polygons, Boreholes):
        """ Undo all material assigment
        """
        self.ui.tableWidget.blockSignals(True)  # temporary block signals
        for i_layer, layer in enumerate(Layer_polygons):
            if 'soilmaterial_layer' in layer:
                layer_pathpathch_to_undo = layer['pathpatch_layer']
            
                if layer_pathpathch_to_undo:
                    self.plot_canvas.undo_plot_pathpatches(layer_pathpathch_to_undo)

                layer['pathpatch_layer'] = None
                layer['soilmaterial_layer'] = None
                del layer['soilmaterial_layer']
                layer['shaded'] = False
            
                plaxis2d_input.unassign_soil_layer(self.plaxis2d_input_file, i_layer)

                for col in range(2*len(Boreholes)):
                    self.ui.tableWidget.item(i_layer, col).setBackground(QColor(255, 255, 255))

                print('Soil assigment to Layer {} is undone'.format(i_layer+1))

                # refill color in cells for borehole's top
                for i_layer in range(len(Layer_polygons)+1):
                    for borehole_i, _ in enumerate(Boreholes):
                        self.ui.tableWidget.item(i_layer, 2*borehole_i).setBackground(QColor(242, 255, 116)) # light yellow, predictive layer

        self.ui.tableWidget.blockSignals(False)  # unblock signals
    

    def clear_tables_reloading(self):
        """ Clears all tables when reloading
        """
        n_tables = 29
        table_0 = ['self.ui.tableWidget']
        tables_rest = ['self.ui.tableWidget_' + str(i+1) for i in range(n_tables)]
        
        for table in table_0:
            try:
                eval(table + '.clearContents()')    # clear contents
                # clear headers
                for i in range(eval(table + '.rowCount()')):
                    item = eval(table + '.horizontalHeaderItem({0})'.format(str(i)))
                    item.setText(QCoreApplication.translate("MainWindow", ''))
                for i in range(eval(table + '.columnCount()')):
                    item = eval(table + '.verticalHeaderItem({0})'.format(str(i)))
                    item.setText(QCoreApplication.translate("MainWindow", ''))
            except:
                pass
        for table in tables_rest:
            try:
                eval(table + '.clearContents()')    # clear contents 
                # clear headers
                for i in range(eval(table + '.rowCount()')):
                    item = eval(table + '.horizontalHeaderItem({0})'.format(str(i)))
                    item.setText(QCoreApplication.translate("MainWindow", ''))
                for i in range(eval(table + '.columnCount()')):
                    item = eval(table + '.verticalHeaderItem({0})'.format(str(i)))
                    item.setText(QCoreApplication.translate("MainWindow", ''))
            except:
                pass


    def clear_comboboxes_reloading(self):
        """ Clears all comboboxes when reloading
        """
        combobox_0 = self.ui.comboBox
        combobox_0.clear()

        n_comboboxes = 35
        comboboxes_rest = ['self.ui.comboBox_' + str(i+1) for i in range(n_comboboxes)]
        for combobox in comboboxes_rest:
            try:
                eval(combobox + '.clear()')    # clear 
            except:
                pass
    

    def open_all_soils(self, Layer_polygons):
        """ Opens all soils for viewing and editting
        """
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_allSoils()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle('Properties of all soils')

        self.soil_edit_box.data_soils = []
        for layer in Layer_polygons:
            if 'soilmaterial_layer' in layer:
                json_item = layer['soilmaterial_layer']
                if json_item: # view only if json_item is not None
                    PATH_MATERIAL_LIBRARY = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
                    material_file = os.path.join(PATH_MATERIAL_LIBRARY, json_item + '.json')

                    with open(material_file, "r") as read_file:
                        data = json.load(read_file, object_pairs_hook = OrderedDict)         
                    data_soil ={'json_item': json_item, 'data': data}
                    self.soil_edit_box.data_soils.append(data_soil)
        
        # show soil properties on table
        self.display_data_soils_on_table()

        material_box.exec_()
    

    def display_data_soils_on_table(self, active=True):
        """ Displays all soil properties on table
        """
        self.soil_edit_box.tableWidget.setRowCount(2*len(self.soil_edit_box.data_soils))
        column_count = 0
        for data_soil in self.soil_edit_box.data_soils:
            keys = [key for key in data_soil['data'].keys()]
            column_count = max(column_count, len(keys))
        self.soil_edit_box.tableWidget.setColumnCount(column_count)

        for i_row, data_soil in enumerate(self.soil_edit_box.data_soils):
            i_column = 0
            for key, value in data_soil['data'].items():
                self.soil_edit_box.tableWidget.setItem(2*i_row, i_column, QtWidgets.QTableWidgetItem(str(key)))
                self.soil_edit_box.tableWidget.setItem(2*i_row + 1, i_column, QtWidgets.QTableWidgetItem(str(value)))
                if i_column > 1:
                    self.soil_edit_box.tableWidget.item(2*i_row + 1, i_column).setBackground(QColor(242, 255, 116)) # light yellow
                i_column += 1
        
        if active == True:
            self.soil_edit_box.tableWidget.cellChanged.connect(lambda row, column: self.update_data_soils(row, column))


    @pyqtSlot()
    def update_data_soils(self, row, column):
        """ Responds to changing in soil parameter value
        """
        self.soil_edit_box.tableWidget.blockSignals(True)
        try:
            # which soil
            index_soil = (row - 1) // 2
            key = self.soil_edit_box.tableWidget.item(row-1, column).text()
            value_str = self.soil_edit_box.tableWidget.item(row, column).text()
            keys_int = ['SoilModel', 'DrainageType', 'K0Determination']
            if key in keys_int:
                value = int(value_str)
            else:
                value = float(value_str)

        except:
            self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')
            return
        
        if (row - 1) % 2 == 0:
            # assign
            self.soil_edit_box.data_soils[index_soil]['data'][key] = value

            # write updated data to disc
            json_item = self.soil_edit_box.data_soils[index_soil]['json_item']
            PATH_MATERIAL_LIBRARY = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
            material_file = os.path.join(PATH_MATERIAL_LIBRARY, json_item + '.json')
            with open(os.path.join(PATH_MATERIAL_LIBRARY, material_file), "w") as write_file:
                json.dump(self.soil_edit_box.data_soils[index_soil]['data'], write_file) 

            # update also moniman material file
            material_file_moniman = os.path.join(PATH_MATERIAL_LIBRARY, json_item + 'moniman.json')
            with open(material_file_moniman, "r") as read_file:
                data_moniman = json.load(read_file, object_pairs_hook = OrderedDict)         
            data_moniman[key] = value
            with open(material_file_moniman, "w") as write_file:
                json.dump(data_moniman, write_file) 

            print('{0} of soil {1} has now value {2}'.format(key, json_item, value))
        
        else:   # you just changed a key (soil parameter name)
            index_soil = row // 2
            keys = [key for key in self.soil_edit_box.data_soils[index_soil]['data'].keys()]
            key = keys[column]
            self.soil_edit_box.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(key)) # it is a key

        self.soil_edit_box.tableWidget.blockSignals(False)


    def open_all_layers(self, Layer_polygons, Boreholes, Soilmaterials, geometry):
        """ Opens all soil layers for viewing and editting
        """
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_allLayers()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle('Properties of all soil layers')

        self.soil_edit_box.data_soils = []
        
        # show soil properties on table
        self.display_layers_on_table_2(Layer_polygons, Boreholes, Soilmaterials)

        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.process_updating_soil_layers(Layer_polygons, Boreholes, Soilmaterials, geometry))
        self.soil_edit_box.buttonBox.accepted.connect(lambda: material_box.close())
        self.soil_edit_box.buttonBox.rejected.connect(lambda: material_box.close())

        material_box.exec_()


    def display_layers_on_table_2(self, Layer_polygons, Boreholes, Soilmaterials):
        """ Displays all soil layers on table
        """
        n_rows = 17
        n_cols = 2*len(Boreholes) + 1
        self.soil_edit_box.tableWidget.setRowCount(n_rows)
        self.soil_edit_box.tableWidget.setColumnCount(n_cols)
        labels_row = ['Layer ' + str(i+1) for i in range(n_rows)]
        labels_column_tops = [borehole['name'] + ' - Top' for borehole in Boreholes]
        labels_column_bottoms = [borehole['name'] + ' - Bottom' for borehole in Boreholes]
        labels_column = [None]*n_cols
        labels_column[:-1:2] = labels_column_tops
        labels_column[1:-1:2] = labels_column_bottoms
        labels_column[-1] = 'Soil material'
        self.soil_edit_box.tableWidget.setVerticalHeaderLabels(labels_row)
        self.soil_edit_box.tableWidget.setHorizontalHeaderLabels(labels_column)

        # fill in current tops and bottoms
        for i_layer, layer_polygon in enumerate(Layer_polygons):
            for i_borehole, borehole in enumerate(Boreholes):
                self.soil_edit_box.tableWidget.setItem(i_layer, 2*i_borehole, QtWidgets.QTableWidgetItem(str(borehole['Top'][i_layer])))
                self.soil_edit_box.tableWidget.setItem(i_layer, 2*i_borehole + 1, QtWidgets.QTableWidgetItem(str(borehole['Bottom'][i_layer])))

            combobox_material = self.display_materials_on_combobox(Soilmaterials, i_layer, layer_polygon)
            combobox_material.setProperty('layer', i_layer)  # set property for later access
            self.soil_edit_box.tableWidget.setCellWidget(i_layer, n_cols-1, combobox_material)

        # layers without soil assigment
        for ii_layer in range(len(Layer_polygons), n_rows):
            combobox_material = self.display_materials_on_combobox(Soilmaterials, ii_layer, None)
            combobox_material.setProperty('layer', ii_layer)  # set property for later access
            self.soil_edit_box.tableWidget.setCellWidget(ii_layer, n_cols-1, combobox_material)


    def display_materials_on_combobox(self, Soilmaterials, i_layer, layer_polygon=None):
        """ Displays soil materials on combobox
        """
        # fill comboboxe
        combobox = QtWidgets.QComboBox()
        self.fill_soilmaterials_in_combobox(combobox, Soilmaterials)

        # show current item
        if layer_polygon:
            if 'soilmaterial_layer' in layer_polygon:
                for idx in range(combobox.count()):
                    if combobox.itemText(idx) == layer_polygon['soilmaterial_layer']:
                        combobox.setCurrentIndex(idx)

            else:   # empty layer
                combobox.setCurrentIndex(0)
        else:   # reserved layer
            combobox.setCurrentIndex(0)

        return combobox


    def fill_soilmaterials_in_combobox(self, combobox, Soilmaterials):
        """ Fills soil materials in combobox, with color
        """
        def combo_changed():
            for soilmat in Soilmaterials:
                if soilmat['json_item'] == combobox.currentText():
                    combobox.setStyleSheet("QComboBox:editable{ background-color: %s}" % QColor('white').name())
                    combobox.setStyleSheet("QComboBox:editable{ color: %s}" % soilmat['color'])
                    
        combobox.clear()
        combobox.addItem('None')    # no material
        model = combobox.model()
        for soilmat in Soilmaterials:
            entry = QStandardItem(soilmat['json_item'])
            color = soilmat['color']
            entry.setForeground(QColor(color))
            entry.setBackground(QColor('white'))
            model.appendRow(entry)

        combobox.currentIndexChanged.connect(combo_changed)


    def process_updating_soil_layers(self, Layer_polygons, Boreholes, Soilmaterials, geometry):
        """ Read new soil strata and update soil layers
        All current layers and the assigned material if any will be removed.
        """
        self.undo_all_assign_materials(Layer_polygons, Boreholes)

        # remove all layers
        n_layers_to_repeat = len(Layer_polygons)
        for _ in range(n_layers_to_repeat):
            self.remove_last_layer(Layer_polygons, Boreholes, geometry)
        
        # clear boreholes' tops and bottoms
        for borehole in Boreholes:
            borehole['Top'].clear()
            borehole['Bottom'].clear()

        # read new values from table
        n_rows = 17
        n_cols = 2*len(Boreholes) + 1
        for i_layer in range(n_rows):
            try:
                tops = []
                bottoms = []
                for i_borehole, borehole in enumerate(Boreholes):
                    cell_top = self.soil_edit_box.tableWidget.item(i_layer, 2*i_borehole)
                    cell_bottom = self.soil_edit_box.tableWidget.item(i_layer, 2*i_borehole + 1)
                    tops.append(float(cell_top.text()))
                    bottoms.append(float(cell_bottom.text()))

                    # clear current borehole tops and bottoms

                # update soil layers and the assigned materials
                layer_polygon = self.process_adding_layer(Layer_polygons, Boreholes, tops, bottoms, geometry, active=True)
                Layer_polygons.append(layer_polygon)

            except:
                break

        # read and assign soil materials
        for i_layer, layer in enumerate(Layer_polygons):
            json_item = self.soil_edit_box.tableWidget.cellWidget(i_layer, n_cols-1).currentText()
            if json_item != 'None':
                self.process_assigning_material(json_item, i_layer, Soilmaterials, Layer_polygons, Boreholes)


                
