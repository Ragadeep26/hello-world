# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 09:34:22 2018

@author: nya
"""

import sys, os, time
import glob
#sys.path.append(r'C:\Users\nya\Packages\Moniman')
import json
from os.path import join, exists, isfile
from collections import OrderedDict
import numpy as np
import copy
from PyQt5 import QtWidgets, QtGui, QtCore
from tools.file_tools import loadpy
from solver.plaxis2d.parameter_relations import (get_HS_moduli, set_plaxis_datatypes, set_nonplaxis_datatypes, get_HSsmall_G0ref, get_psi,
                                            get_HS_K0nc_empirical, get_SPW_parameters, get_CPW_parameters, get_steel_profile_parameters,
                                            get_Eref_CPW, get_Eref_SPW, get_Eref_SPW131, get_Eref_Dwall, get_soil_parameters_based_on_correlations_with_ve,
                                            calc_E_Modul_MIP)

from gui.gui_main_matplotlib import MyStaticMplCanvas
from gui.gui_text_edit_ui import Ui_Dialog as textEditBox
from gui.gui_dialog_edit_soil_HS_ui import Ui_Dialog as editSoilBox_HS
from gui.gui_dialog_edit_soil_HSsmall_ui import Ui_Dialog as editSoilBox_HSsmall
from gui.gui_dialog_edit_soil_MC_ui import Ui_Dialog as editSoilBox_MC
from gui.gui_dialog_edit_soil_LE_ui import Ui_Dialog as editSoilBox_LE

from gui.gui_dialog_edit_wall_Dwall_ui import Ui_Dialog as editWallBox_Dwall
from gui.gui_dialog_edit_wall_SPW_ui import Ui_Dialog as editWallBox_SPW
from gui.gui_dialog_edit_wall_CPW_ui import Ui_Dialog as editWallBox_CPW
from gui.gui_dialog_edit_wall_Steel_profile_ui import Ui_Dialog as editWallBox_Steel_profile
from gui.gui_dialog_edit_wall_MIPwall_ui import Ui_Dialog as editWallBox_MIPwall

from gui.gui_dialog_edit_strand_ui import Ui_Dialog as editStrandBox
from gui.gui_dialog_edit_grout_Linear_ui import Ui_Dialog as editGroutLinearBox
from gui.gui_dialog_edit_grout_Multilinear_ui import Ui_Dialog as editGroutMultilinearBox

from gui.gui_dialog_edit_strut_Steel_tube_ui import Ui_Dialog as editStrutSteeltube
from gui.gui_dialog_edit_strut_RC_bar_ui import Ui_Dialog as editStrutRCbar
from gui.gui_dialog_edit_strut_RC_slab_ui import Ui_Dialog as editStrutRCslab

from gui.gui_dialog_edit_points_free_polygon import Ui_Dialog as editPolygonPoints
from gui.gui_dialog_select_design_variables_groundanchor import Ui_Dialog as selectAnchorVariables 
from gui.gui_dialog_select_design_variables_strut import Ui_Dialog as selectStrutVariables 
from gui.gui_dialog_select_design_variables_stone_columns import Ui_Dialog as selectStoneColumnsVariables 
from gui.gui_dialog_select_design_variables_rigid_inclusions import Ui_Dialog as selectFDCVariables 
from gui.gui_dialog_select_phases import Ui_Dialog as selectObsPhases

class Ui_Dialog(QtWidgets.QWidget):
    """ This class implements all kinds of dialog for the main window
    """
    
    def __init__(self):
        
        super().__init__()
           

    def show_message_box(self, boxtitle, message):
        """ Display a message on dialog
        """
        self.msg_box = QtWidgets.QMessageBox()
        self.msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg_box.setWindowTitle(boxtitle)
        self.msg_box.setText(message)
        self.msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg_box.setStyleSheet("QWidget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QText{background-color: rgb(255, 255, 255);}\n"
"\n"
"QPushButton{background-color: rgb(205, 205, 205);}")
        self.msg_box.exec_()
        
        
    def show_save_box(self, filename):
        """ Display a confirmation box
        """
        self.msg_box = QtWidgets.QMessageBox()
        self.msg_box.setIcon(QtWidgets.QMessageBox.Question)
        boxtitle = "Save MONIMAN"
        self.msg_box.setWindowTitle(boxtitle)
        output_dir = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        #message = "File '{0}' exists in {1}. Do you want to overwrite it?".format(filename, output_dir)
        message = "MONIMAN's state exists in {0}. Do you want to overwrite it?".format(output_dir)
        self.msg_box.setText(message)
        self.msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        self.msg_box.setStyleSheet("QWidget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QText{background-color: rgb(255, 255, 255);}\n"
"\n"
"QPushButton{background-color: rgb(205, 205, 205);}")
        return self.msg_box.exec_()
        

    def show_new_project_box(self, filename):
        """ Display a confirmation box when project file already exists
        """
        self.msg_box = QtWidgets.QMessageBox()
        self.msg_box.setIcon(QtWidgets.QMessageBox.Question)
        boxtitle = "New MONIMAN Project"
        self.msg_box.setWindowTitle(boxtitle)
        message = "MONIMAN's state already exists here. Do you want to overwrite it?"
        self.msg_box.setText(message)
        self.msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        self.msg_box.setStyleSheet("QWidget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QText{background-color: rgb(255, 255, 255);}\n"
"\n"
"QPushButton{background-color: rgb(205, 205, 205);}")
        return self.msg_box.exec_()


    def open_color_selection(self):
        self.color_box = QtWidgets.QColorDialog()
        color = self.color_box.getColor()
        
        if color.isValid():
            return color
        else:
            return QtGui.QColor(85, 255, 0)

    def open_text_edit(self, filename):
        # Open text edit 
        cwd = os.getcwd()

        text_box = QtWidgets.QDialog()
        self.text_edit_box = textEditBox()
        self.text_edit_box.setupUi(text_box)
        text_box.setWindowTitle('Edit PATHS in working directory ' + cwd)
        
        data_dict = loadpy(filename)
        
        # set default paths for MONIMAN and MONIMAN_OUTPUTS
        data_dict['MONIMAN'] = cwd
        #data_dict['MONIMAN_OUTPUTS'] = cwd + '\MONIMAN_OUTPUTS'

        for key, value in data_dict.items():
            text = key + ' = ' + 'r' + "'" + value + "'" + '\n\n'
            self.text_edit_box.plainTextEdit.moveCursor(QtGui.QTextCursor.End)
            self.text_edit_box.plainTextEdit.insertPlainText(text)
        
        self.text_edit_box.buttonBox.accepted.connect(lambda: self.close_text_edit(filename))
                
        text_box.exec_()
    

    def close_text_edit(self, filename):
        with open(filename, 'w') as f:
            text = self.text_edit_box.plainTextEdit.toPlainText()
            f.write(text)


    def open_borehole_editor(self, selected_bh, x, Head):
        """ Opens borehole editor
        """
        text, ok = QtWidgets.QInputDialog.getText(self, 'Please enter new values for ' + selected_bh, 'BH_name, x, Head: {0}, {1}, {2}'.format(selected_bh, x, Head))
        
        if ok:
            return text
        else:
            return None


    def open_remove_structure_selection(self, Structures, dialog_title):
        remove_structure_box = QtWidgets.QDialog()
        remove_structure_box.setWindowTitle(dialog_title)
        remove_structure_box.resize(850,220)
        remove_structure_box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        remove_structure_box.setStyleSheet("QWidget{background-color: rgb(0, 74, 127);}\n"
"\n"
"QTableWidget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QCheckBox{background-color: rgb(255, 255, 255);}\n"
"\n"
"QWidget#widget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QGroupBox{background-color: rgb(251, 185, 0);}\n"
"\n"
"QPushButton{background-color: rgb(205, 205, 205);}\n"
"\n"
"QLineEdit{background-color:rgb(255, 255, 255);}\n"
"\n"
"QLabel{background-color:rgb(215, 215, 215);}")
        
        self.removed_ids = []
        row_number = len(Structures)
        column_items = sorted(list(Structures[-1].keys()))
        for structure in Structures:    # minimal fields
            tmp = sorted(list(Structures[-1].keys()))
            if len(tmp) < len(column_items):
                column_items = tmp

        column_items.append('')
        column_number = len(column_items)
        self.table = QtWidgets.QTableWidget(remove_structure_box)
        self.table.setRowCount(row_number)
        self.table.setColumnCount(column_number)
        self.table.setHorizontalHeaderLabels(column_items)
        
        for i in range(len(Structures)):
            for j in range(len(column_items) - 1):
                self.table.setItem(i, j,  QtWidgets.QTableWidgetItem(str(Structures[i][column_items[j]])))
            self.table.setCellWidget(i, len(column_items) - 1, QtWidgets.QCheckBox('Select item?'))
        
        
        self.buttonBox = QtWidgets.QDialogButtonBox(remove_structure_box)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addWidget(self.buttonBox)
        remove_structure_box.setLayout(vbox)
        
        self.buttonBox.accepted.connect(lambda: self.accept_remove_structure(Structures))
        self.buttonBox.accepted.connect(remove_structure_box.close)

        remove_structure_box.exec_()
        

    def accept_remove_structure(self, Structures):
        column = self.table.columnCount() - 1
        for i in range(self.table.rowCount()):
            removed = self.table.cellWidget(i, column).checkState()
            if removed == 2:
                self.removed_ids.append(Structures[i]['id'])
        

    def open_design_variables_selection_strut(self, strut):
        """ Opens dialog for selecting design variables of anchor
        """
        variables_box = QtWidgets.QDialog()
        self.soil_edit_box = selectStrutVariables()
        self.soil_edit_box.setupUi(variables_box)
        variables_box.setWindowTitle('Select design variables for Groundanchor_{}'.format(strut['id']))
        self.soil_edit_box.can_close_now = True

        self.soil_edit_box.isVariableSelected = [False] * self.soil_edit_box.tableWidget.columnCount()
        # write current anchor properties to table
        values = [strut['position'][1], strut['Lspacing']]
        for i in range(self.soil_edit_box.tableWidget.columnCount()):
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(values[i])))
            self.soil_edit_box.tableWidget.setCellWidget(1, i, QtWidgets.QCheckBox('Variable?'))

        self.soil_edit_box.buttonBox.accepted.connect(self.accept_variables_selection_strut)
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(variables_box))

        variables_box.exec_()


    def accept_variables_selection_strut(self):
        """ Records selected variables before closing
        """
        num_column = self.soil_edit_box.tableWidget.columnCount()

        for i in range(num_column):
            selected = self.soil_edit_box.tableWidget.cellWidget(1, i).checkState()
            if selected == 2:
                self.soil_edit_box.isVariableSelected[i] = True
            

    def open_observation_phases_selection(self, Points_obs):
        """
        """
        variables_box = QtWidgets.QDialog()
        self.soil_edit_box = selectObsPhases()
        self.soil_edit_box.setupUi(variables_box)
        variables_box.setWindowTitle('Select the considered observation phases')
        self.soil_edit_box.can_close_now = True

        # list observation phases (types?) on table
        obs_phases = [phase['obs_phase'] for phase in Points_obs]
        obs_types = [phase['obs_type'] for phase in Points_obs]
        self.soil_edit_box.tableWidget.setColumnCount(len(obs_phases))
        #self.soil_edit_box.isVariableSelected = [True] * self.soil_edit_box.tableWidget.columnCount()
        self.soil_edit_box.isVariableSelected = [pnts_obs['usedForMetamodel'] for pnts_obs in Points_obs]
        headers_h = [obs_type + '\n@Phase' for obs_type in obs_types]
        #headers_h = ['Phase']*self.soil_edit_box.tableWidget.columnCount()
        self.soil_edit_box.tableWidget.setHorizontalHeaderLabels(headers_h)

        #for i in range(self.soil_edit_box.tableWidget.columnCount()):
        for i, pnts_obs in enumerate(Points_obs):
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(obs_phases[i])))
            self.soil_edit_box.tableWidget.setCellWidget(1, i, QtWidgets.QCheckBox('Selected?'))
            if pnts_obs['usedForMetamodel'] == True:
                self.soil_edit_box.tableWidget.cellWidget(1, i).setCheckState(2)
            else:
                self.soil_edit_box.tableWidget.cellWidget(1, i).setCheckState(0)

        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.accept_observation_phases_selection(obs_phases))
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(variables_box))

        variables_box.exec_()


    def accept_observation_phases_selection(self, obs_phases):
        """ Records selected phases before closing
        """
        num_column = self.soil_edit_box.tableWidget.columnCount()

        for i in range(num_column):
            selected = self.soil_edit_box.tableWidget.cellWidget(1, i).checkState()
            if selected == 2:
                self.soil_edit_box.isVariableSelected[i] = True
            else:
                self.soil_edit_box.isVariableSelected[i] = False


    def open_design_variables_selection_anchor(self, anchor):
        """ Opens dialog for selecting design variables of anchor
        """
        variables_box = QtWidgets.QDialog()
        self.soil_edit_box = selectAnchorVariables()
        self.soil_edit_box.setupUi(variables_box)
        variables_box.setWindowTitle('Select design variables for Groundanchor_{}'.format(anchor['id']))
        self.soil_edit_box.can_close_now = True

        self.soil_edit_box.isVariableSelected = [False] * self.soil_edit_box.tableWidget.columnCount()
        # write current anchor properties to table
        values = [anchor['position'][1], anchor['angle'], anchor['length_free'], anchor['Lspacing'], anchor['F_prestress']]
        for i in range(self.soil_edit_box.tableWidget.columnCount()):
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(values[i])))
            self.soil_edit_box.tableWidget.setCellWidget(1, i, QtWidgets.QCheckBox('Variable?'))

        self.soil_edit_box.buttonBox.accepted.connect(self.accept_variables_selection_anchor)
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(variables_box))

        variables_box.exec_()


    def accept_variables_selection_anchor(self):
        """ Records selected variables before closing
        """
        num_column = self.soil_edit_box.tableWidget.columnCount()

        for i in range(num_column):
            selected = self.soil_edit_box.tableWidget.cellWidget(1, i).checkState()
            if selected == 2:
                self.soil_edit_box.isVariableSelected[i] = True


    def open_design_variables_selection_stone_columns(self, stone_columns_name, sc_params, columns_depth):
        """ Opens dialog for selecting design variables of stone columns
        """
        variables_box = QtWidgets.QDialog()
        self.soil_edit_box = selectStoneColumnsVariables()
        self.soil_edit_box.setupUi(variables_box)
        variables_box.setWindowTitle('Select design variables for stone columns {}'.format(stone_columns_name))
        self.soil_edit_box.can_close_now = True

        self.soil_edit_box.isVariableSelected = [False] * self.soil_edit_box.tableWidget.columnCount()
        # write current anchor properties to table
        values = [sc_params['D'], sc_params['a'], columns_depth]
        for i in range(self.soil_edit_box.tableWidget.columnCount()):
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(values[i])))
            self.soil_edit_box.tableWidget.setCellWidget(1, i, QtWidgets.QCheckBox('Variable?'))

        self.soil_edit_box.buttonBox.accepted.connect(self.accept_variables_selection_anchor)
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(variables_box))

        variables_box.exec_()


    def open_design_variables_selection_rigid_inclusions(self, FDC_name, FDC_params):
        """ Opens dialog for selecting design variables of stone columns
        """
        variables_box = QtWidgets.QDialog()
        self.soil_edit_box = selectFDCVariables()
        self.soil_edit_box.setupUi(variables_box)
        variables_box.setWindowTitle('Select design variables for FDC rigid inclusions {}'.format(FDC_name))
        self.soil_edit_box.can_close_now = True

        self.soil_edit_box.isVariableSelected = [False] * self.soil_edit_box.tableWidget.columnCount()
        # write current anchor properties to table
        values = [FDC_params['Dc'], FDC_params['a'], FDC_params['Lc']]
        for i in range(self.soil_edit_box.tableWidget.columnCount()):
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(values[i])))
            self.soil_edit_box.tableWidget.setCellWidget(1, i, QtWidgets.QCheckBox('Variable?'))

        self.soil_edit_box.buttonBox.accepted.connect(self.accept_variables_selection_anchor)
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(variables_box))

        variables_box.exec_()


    def open_edit_points_free_polygon(self, polygonPoints):
        points_box = QtWidgets.QDialog()
        self.soil_edit_box = editPolygonPoints()
        self.soil_edit_box.setupUi(points_box)
        points_box.setWindowTitle('Edit points for free polygon')
        self.soil_edit_box.can_close_now = False
        self.points_updated = [(pnt['point'][0], pnt['point'][1]) for pnt in polygonPoints]

        row_number = 2
        column_number = len(polygonPoints)
        self.soil_edit_box.tableWidget.setRowCount(row_number)
        self.soil_edit_box.tableWidget.setColumnCount(column_number) 

        points_label = ['Point ' + str(pntnumber + 1) for pntnumber in range(len(polygonPoints))]
        self.soil_edit_box.tableWidget.setHorizontalHeaderLabels(points_label)

        for (i, pnt) in enumerate(polygonPoints):
            pntx = pnt['point'][0]
            pnty = pnt['point'][1]
            self.soil_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(pntx)))
            self.soil_edit_box.tableWidget.setItem(1, i, QtWidgets.QTableWidgetItem(str(pnty)))

        self.soil_edit_box.buttonBox.accepted.connect(self.accept_edit_points_free_polygon)
        
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(points_box))

        points_box.exec_()
    

    def accept_edit_points_free_polygon(self):
        # read table
        try:
            for i in range(self.soil_edit_box.tableWidget.columnCount()):
                pntx = float(QtWidgets.QTableWidgetItem(self.soil_edit_box.tableWidget.item(0, i)).text())
                pnty = float(QtWidgets.QTableWidgetItem(self.soil_edit_box.tableWidget.item(1, i)).text())
                self.points_updated[i] = (pntx, pnty)
            
            self.soil_edit_box.can_close_now = True

        except ValueError:
            self.show_message_box('Warning', 'Please check if point coordinates are correctly entered!')


    def open_edit_soil_LE(self, soil_model, user_soil_name, color=QtGui.QColor(85, 255, 0).name(), isdefined=False, correlations_ve=False):
        """ Opens soil editor for a linear elastic material
        """
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_LE()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle(soil_model + ' properties')
        self.soil_edit_box.soil_model = soil_model
        self.soil_edit_box.json_item = None # json file for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.correlations_ve=correlations_ve
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = True
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            self.soil_edit_box.json_item = 'LINEAR_ELASTIC_material'
            json_item_user = [item.strip() for item in user_soil_name.split(',')]
            json_item_user.append(self.soil_edit_box.soil_model)
            json_item_user = '_'.join(json_item_user)
            json_item_user = json_item_user.replace(' ', '_')
            self.soil_edit_box.json_item_user = json_item_user

            self.load_and_update_json({'MaterialName': user_soil_name}, False)
            self.load_dependent_parameters_MC()
        else:
            self.soil_edit_box.json_item_user = user_soil_name # the selected soil for changing properties
            self.load_and_update_json(None, True)
            self.load_dependent_parameters_MC()

        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_MC)
        self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))     #<-- Write properties in table to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(material_box))    #<-- Conditional close
        
                                                                
        material_box.exec_()


    def open_edit_soil_MC(self, soil_model, user_soil_name, color=QtGui.QColor(85, 255, 0).name(), isdefined=False, correlations_ve=False):
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_MC()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle(soil_model + ' properties')
        self.soil_edit_box.soil_model = soil_model
        self.soil_edit_box.json_item = None # json file for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.correlations_ve = correlations_ve
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_soil_model(user_soil_name))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json({'MaterialName': user_soil_name}, False))
            self.soil_edit_box.pushButton.clicked.connect(self.load_dependent_parameters_MC)
        else:
            self.soil_edit_box.json_item_user = user_soil_name # the selected soil for changing properties
            self.load_and_update_json(None, True)
            self.load_dependent_parameters_MC()
            self.soil_edit_box.pushButton.setEnabled(False)

        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_MC)
        self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)

        
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))     #<-- Write properties in table to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(material_box))    #<-- Conditional close
        
                                                                
        material_box.exec_()
        
        
    def load_dependent_parameters_MC(self):
           
        Gref = self.soil_edit_box.data['Gref']
        nu = self.soil_edit_box.data['nu']
        Eref = Gref*2*(1 + nu)
        self.soil_edit_box.lineEdit.setText(str(Eref))
        self.soil_edit_box.lineEdit_4.setText(str(nu))

        
    def update_dependent_parameters_MC(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else: 
            try:
                Eref = float(self.soil_edit_box.lineEdit.text())
                nu = float(self.soil_edit_box.lineEdit_4.text())
                Gref = Eref/(2*(1 + nu))
                
                updated_parameters = {'Gref': Gref, 'nu': nu}
                
                self.update_table(updated_parameters)
                        
            except ValueError:
                self.show_message_box('Warning', "Please check if values correctly entered!")
                

    def select_soil_color(self):
        """ Select a color for soil
        """
        self.soil_edit_box.color = self.open_color_selection().name()
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)


    def open_edit_soil_HS(self, soil_model, user_soil_name, color=QtGui.QColor(85, 255, 0).name(), isdefined=False, correlations_ve=False):
        """ Opens soil edit box.
        soil_model is defined in combobox for material model (MC, HS, HSsmall).
        user_soil_name is given by the user. In the case of editing an already defined soil, user_soil_name is the selected soil.
        """
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_HS()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle(soil_model + ' properties')
        self.soil_edit_box.soil_model = soil_model
        self.soil_edit_box.json_item = None # json file for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.correlations_ve = correlations_ve
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)

        if self.soil_edit_box.correlations_ve:
            self.soil_edit_box.checkBox.setCheckState(2)
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_soil_model(user_soil_name))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json({'MaterialName': user_soil_name}))    # <-- Continue editting soil material
            self.soil_edit_box.pushButton.clicked.connect(self.load_dependent_parameters_HS)
        else:
            self.soil_edit_box.json_item_user = user_soil_name # the selected soil for changing properties
            self.load_and_update_json(None, True)
            self.load_dependent_parameters_HS(True)
            self.soil_edit_box.pushButton.setEnabled(False)


        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_HS)
        self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)

        # Save material properties to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(material_box))    #<-- Conditional close
        
        material_box.exec_()
    

    def match_json_name_soil_model(self, user_soil_name):
        """ Matches soil name for json_item.
        """
        json_item = self.soil_edit_box.comboBox.currentText()
        json_item = [item.strip() for item in json_item.split(',')]
        json_item.append(self.soil_edit_box.soil_model)
        json_item = '_'.join(json_item)
        json_item = json_item.replace(' ', '_')
        self.soil_edit_box.json_item = json_item
        
        json_item_user = user_soil_name
        json_item_user = [item.strip() for item in json_item_user.split(',')]
        json_item_user.append(self.soil_edit_box.soil_model)
        json_item_user = '_'.join(json_item_user)
        json_item_user = json_item_user.replace(' ', '_')
        self.soil_edit_box.json_item_user = json_item_user

    
    def remove_data_nonplaxis_parameters(self):
        """ Removes parameters that do not belong to PLAXIS2D soil parameters
            HS/HSsmall non-plaxis parameters: ve, we
            Wall SPW/CPW non-plaxis parameters: D, S
        """
        # copy data to data_moniman for later maintaining the relations among soil parameters
        self.soil_edit_box.data_moniman = copy.copy(self.soil_edit_box.data)

        # remove redundant properties
        self.soil_edit_box.data.pop('ve', None)
        self.soil_edit_box.data.pop('we', None)
        
        # Wall SPW/CPW non-plaxis parameters: D, S
        self.soil_edit_box.data.pop('D', None)
        self.soil_edit_box.data.pop('S', None)              

        # Steel tube strut
        if 'Strut' in self.soil_edit_box.data['MaterialName']:  # avoid deleting 'E' for grout body unexpectedly
            self.soil_edit_box.data.pop('E', None)  
        self.soil_edit_box.data.pop('d_outer', None)
        self.soil_edit_box.data.pop('d_inner', None)
        self.soil_edit_box.data.pop('fyk', None)        # strut tube
        self.soil_edit_box.data.pop('gamma_s', None)    # strut tube
        # RC bar strut
        self.soil_edit_box.data.pop('width', None)
        self.soil_edit_box.data.pop('height', None)
        self.soil_edit_box.data.pop('concrete_grade', None)
        # RC slab strut
        self.soil_edit_box.data.pop('thickness', None)
        self.soil_edit_box.data.pop('concrete_grade', None)

        # Steel profile wall
        if 'nos' in self.soil_edit_box.data:
            self.soil_edit_box.data.pop('nos', None)    # number of steel profiles
        
        # MIP wall
        self.soil_edit_box.data.pop('fmk', None)
        self.soil_edit_box.data.pop('fines_percentage', None)
        

    def load_dependent_parameters_HS(self, isdefined = False):
        Pref = self.soil_edit_box.data['Pref']
        #if isdefined is False:
        #    ve = self.soil_edit_box.data['ve']
        #    we = self.soil_edit_box.data['we']
        ve = self.soil_edit_box.data['ve']
        we = self.soil_edit_box.data['we']
        
        E50ref = self.soil_edit_box.data['E50ref']
        EoedRef = self.soil_edit_box.data['EoedRef']
        EurRef = self.soil_edit_box.data['EurRef']
        #ErefOed50: 1 
        #ErefUr50: 3 
        Eref50Oed = E50ref/EoedRef
        ErefUr50 = EurRef/E50ref
  
        #if isdefined is False:
        #    self.soil_edit_box.lineEdit.setText(str(ve))
        #    self.soil_edit_box.lineEdit_4.setText(str(we))
        #else:
        #    self.soil_edit_box.lineEdit.setEnabled(False)
        #    self.soil_edit_box.lineEdit_4.setEnabled(False)
        self.soil_edit_box.lineEdit.setText(str(ve))
        self.soil_edit_box.lineEdit_4.setText(str(we))

        self.soil_edit_box.lineEdit_2.setText(str(Pref))
        self.soil_edit_box.lineEdit_3.setText(str(EoedRef))
        self.soil_edit_box.lineEdit_5.setText(str(Eref50Oed))
        self.soil_edit_box.lineEdit_6.setText(str(ErefUr50))
        
        self.soil_edit_box.lineEdit_3.setReadOnly(True)  
        self.soil_edit_box.lineEdit_3.setStyleSheet("background-color: rgb(150, 150, 150)")
                    
        
    def update_dependent_parameters_HS(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else:
            try:
                ve = float(self.soil_edit_box.lineEdit.text())
                we = float(self.soil_edit_box.lineEdit_4.text())
                Pref = float(self.soil_edit_box.lineEdit_2.text())
                Eref50Oed = float(self.soil_edit_box.lineEdit_5.text())
                ErefUr50 = float(self.soil_edit_box.lineEdit_6.text())

                EoedRef, E50ref, EurRef = get_HS_moduli(ve, we, Pref, Eref50Oed, ErefUr50)

                self.soil_edit_box.lineEdit_3.setText(str(EoedRef))       

                updated_parameters = {'EoedRef': EoedRef, 'E50ref': E50ref, 'EurRef': EurRef, 've': ve, 'we': we, 'powerm': we}
                
                self.update_table(updated_parameters)

                # check if correlations with ve is used
                if self.soil_edit_box.checkBox.checkState() == 2:
                    self.update_soil_parameters_based_on_correlations_with_ve(ve)
                    self.soil_edit_box.correlations_ve = True
                else:
                    self.soil_edit_box.correlations_ve = False
                        
            except ValueError:
                self.show_message_box('Warning', "Please check if values correctly entered!")
    

    def update_soil_parameters_based_on_correlations_with_ve(self, ve):
        """ Updates phi, we, gammaSat, and gammaUnsat based on correlation with ve
        """
        phi, we, gammaSat, gammaUnsat = get_soil_parameters_based_on_correlations_with_ve(ve)
        # update K0nc as well
        K0nc = 1.0 - np.sin(phi*np.pi/180)
        # apply condition for dilation angle
        psi = get_psi(phi)
        updated_parameters = {'phi': phi, 'we': we, 'powerm': we, 'gammaSat': gammaSat, 'gammaUnsat': gammaUnsat, 'K0nc': K0nc, 'psi': psi}
        self.update_table(updated_parameters)

        
    def open_edit_soil_HSsmall(self, soil_model, user_soil_name, color=QtGui.QColor(85, 255, 0).name(), isdefined=False, correlations_ve=False):
        material_box = QtWidgets.QDialog()
        self.soil_edit_box = editSoilBox_HSsmall()
        self.soil_edit_box.setupUi(material_box)
        material_box.setWindowTitle(soil_model + ' properties')
        self.soil_edit_box.soil_model = soil_model
        self.soil_edit_box.json_item = None # json file for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.correlations_ve = correlations_ve
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        if self.soil_edit_box.correlations_ve:
            self.soil_edit_box.checkBox.setCheckState(2)

        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_soil_model(user_soil_name))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json({'MaterialName': user_soil_name}))    # <-- Continue editting soil material
            self.soil_edit_box.pushButton.clicked.connect(self.load_dependent_parameters_HSsmall)
        else:
            self.soil_edit_box.json_item_user = user_soil_name # the selected soil for changing properties
            self.load_and_update_json(None, True)
            self.load_dependent_parameters_HSsmall(True)
            self.soil_edit_box.pushButton.setEnabled(False)

        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_HSsmall)
        self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)

        # Save material properties to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(material_box))    #<-- Conditional close
        
        material_box.exec_()

    
    def load_dependent_parameters_HSsmall(self, isdefined = False):
        Pref = self.soil_edit_box.data['Pref']

        #if isdefined is False:
        #    ve = self.soil_edit_box.data['ve']
        #    w = self.soil_edit_box.data['we']
        ve = self.soil_edit_box.data['ve']
        we = self.soil_edit_box.data['we']
        
        E50ref = self.soil_edit_box.data['E50ref']
        EoedRef = self.soil_edit_box.data['EoedRef']
        EurRef = self.soil_edit_box.data['EurRef']
        G0ref = self.soil_edit_box.data['G0ref']
        gamma07 = self.soil_edit_box.data['gamma07']
        #ErefOed50: 1 
        #ErefUr50: 3 
        Eref50Oed = E50ref/EoedRef
        ErefUr50 = EurRef/E50ref
        E_dyn_over_sta = 2.4*G0ref/EurRef
  
        #if isdefined is False:
        #    self.soil_edit_box.lineEdit.setText(str(ve))
        #    self.soil_edit_box.lineEdit_4.setText(str(we))
        #else:
        #    self.soil_edit_box.lineEdit.setEnabled(False)
        #    self.soil_edit_box.lineEdit_4.setEnabled(False)
        self.soil_edit_box.lineEdit.setText(str(ve))
        self.soil_edit_box.lineEdit_4.setText(str(we))

        self.soil_edit_box.lineEdit_2.setText(str(Pref))
        self.soil_edit_box.lineEdit_3.setText(str(EoedRef))
        self.soil_edit_box.lineEdit_5.setText(str(Eref50Oed))
        self.soil_edit_box.lineEdit_6.setText(str(ErefUr50))
        self.soil_edit_box.lineEdit_7.setText(str(G0ref))
        self.soil_edit_box.lineEdit_8.setText(str(gamma07))
        self.soil_edit_box.lineEdit_9.setText(str(E_dyn_over_sta))
        
        self.soil_edit_box.lineEdit_3.setReadOnly(True)  
        self.soil_edit_box.lineEdit_3.setStyleSheet("background-color: rgb(150, 150, 150)")
        self.soil_edit_box.lineEdit_7.setReadOnly(True)  
        self.soil_edit_box.lineEdit_7.setStyleSheet("background-color: rgb(150, 150, 150)")


    def update_dependent_parameters_HSsmall(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else:
            try:
                ve = float(self.soil_edit_box.lineEdit.text())
                we = float(self.soil_edit_box.lineEdit_4.text())
                Pref = float(self.soil_edit_box.lineEdit_2.text())
                Pat = 100 # Atmospheric pressure 100 KN/m^2
                EoedRef = ve*Pat*(Pref/Pat)**we # EoefRef is a derived parameter
                self.soil_edit_box.lineEdit_3.setText(str(EoedRef))       
                
                  
                Eref50Oed = float(self.soil_edit_box.lineEdit_5.text())
                ErefUr50 = float(self.soil_edit_box.lineEdit_6.text())
                E_dyn_over_sta = float(self.soil_edit_box.lineEdit_9.text())
                E50ref = EoedRef*Eref50Oed
                EurRef = E50ref*ErefUr50

                G0ref = get_HSsmall_G0ref(EurRef, E_dyn_over_sta)
                self.soil_edit_box.lineEdit_7.setText(str(G0ref))       
                
                gamma07 = float(self.soil_edit_box.lineEdit_8.text())
                
                updated_parameters = {'EoedRef': EoedRef, 'E50ref': E50ref, 'EurRef': EurRef, 'G0ref': G0ref, 'gamma07': gamma07, 've': ve, 'we': we, 'powerm': we}

                # check if correlations with ve is used
                if self.soil_edit_box.checkBox.checkState() == 2:
                    self.update_soil_parameters_based_on_correlations_with_ve(ve)
                    self.soil_edit_box.correlations_ve = True
                else:
                    self.soil_edit_box.correlations_ve = False
                
                self.update_table(updated_parameters)
                        
            except ValueError:
                self.show_message_box('Warning', "Please check if values correctly entered!")
        

    def open_edit_wall_Dwall(self, wall_type, user_wall_name, color=QtGui.QColor(200, 255, 255).name(), isdefined=False):
        """ Opens dialog for defining D-wall
        """
        wall_box = QtWidgets.QDialog()
        self.soil_edit_box = editWallBox_Dwall()
        self.soil_edit_box.setupUi(wall_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        wall_box.setWindowTitle(wall_type + ' properties')
        self.soil_edit_box.json_item = None      # json file name for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file name for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        # Load default values from json file
        if isdefined is False: # defining new material
            self.soil_edit_box.json_item = 'WALL_' + wall_type # json file name for reading
            #self.soil_edit_box.json_item_user = user_wall_name + '_' + wall_type # json file name for writing
            self.soil_edit_box.json_item_user = user_wall_name # json file name for writing
            self.load_and_update_json(None)
        else: # editing already defined material
            self.soil_edit_box.json_item_user = user_wall_name # josn file name for reading/ writing
            self.load_and_update_json(None, True)
        
        # Continue only if data is successfully loaded
        if self.soil_edit_box.data:
            #MaterialName = self.soil_edit_box.data['MaterialName']
            MaterialName = self.soil_edit_box.json_item_user
            Gref = self.soil_edit_box.data['Gref']
            nu = self.soil_edit_box.data['nu']
            Eref = get_Eref_Dwall(Gref, nu)
            d = self.soil_edit_box.data['d']
            self.soil_edit_box.lineEdit.setText(MaterialName)
            self.soil_edit_box.lineEdit_2.setText(str(Eref))
            self.soil_edit_box.lineEdit_4.setText(str(nu))
            self.soil_edit_box.lineEdit_3.setText(str(d))
        
            self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
            self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
            self.plot_canvas.axes.set_axis_off()     
            self.plot_layout.addWidget(self.plot_canvas)

            # Update table once at first by default
            self.continue_edit_wall_Dwall(isdefined)

            # Update table if 'Update' is clicked
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.continue_edit_wall_Dwall(isdefined))
            self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)
        
            # Save wall properties to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(wall_box))    #<-- Conditional close
        
            wall_box.exec_()
        
    def continue_edit_wall_Dwall(self, isdefined):
        try:
            material_name = self.soil_edit_box.lineEdit.text()
            Eref = float(self.soil_edit_box.lineEdit_2.text())
            nu = float(self.soil_edit_box.lineEdit_4.text())
            Gref = Eref/(2*(1 + nu))
            d = float(self.soil_edit_box.lineEdit_3.text())
            
            EA = Eref*d*1.0
            EA2 = EA
            EI = Eref*(d**3*1.0/12)
            w = d*10.0
            
            new_values = {'MaterialName': material_name, 'd': d, 'Gref': Gref, 'nu': nu, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w}
            
            # Load json, update with new property values, and show on table
            self.load_and_update_json(new_values, isdefined)
            
            # Plot wall cross-section
            self.plot_canvas.plot_dwall_cross_section(d)
                    
        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")
        

    def open_edit_wall_MIP(self, wall_type, user_wall_name, color=QtGui.QColor(200, 255, 255).name(), isdefined=False):
        """ Opens dialog for defining MIP-wall
        """
        wall_box = QtWidgets.QDialog()
        self.soil_edit_box = editWallBox_MIPwall()
        self.soil_edit_box.setupUi(wall_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        wall_box.setWindowTitle(wall_type + ' properties')
        self.soil_edit_box.json_item = None      # json file name for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file name for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        # Load default values from json file
        if isdefined is False: # defining new material
            self.soil_edit_box.json_item = 'WALL_' + wall_type # json file name for reading
            #self.soil_edit_box.json_item_user = user_wall_name + '_' + wall_type # json file name for writing
            self.soil_edit_box.json_item_user = user_wall_name # json file name for writing
            self.load_and_update_json(None)
        else: # editing already defined material
            self.soil_edit_box.json_item_user = user_wall_name # josn file name for reading/ writing
            self.load_and_update_json(None, True)
        
        # Continue only if data is successfully loaded
        if self.soil_edit_box.data:
            #MaterialName = self.soil_edit_box.data['MaterialName']
            MaterialName = self.soil_edit_box.json_item_user
            Gref = self.soil_edit_box.data['Gref']
            nu = self.soil_edit_box.data['nu']
            Eref = get_Eref_Dwall(Gref, nu)
            d = self.soil_edit_box.data['d']
            self.soil_edit_box.lineEdit.setText(MaterialName)
            self.soil_edit_box.lineEdit_2.setText(str(Eref))
            self.soil_edit_box.lineEdit_4.setText(str(nu))
            self.soil_edit_box.lineEdit_3.setText(str(d))

            fmk = self.soil_edit_box.data['fmk']
            fines_percentage = self.soil_edit_box.data['fines_percentage']
            self.soil_edit_box.lineEdit_5.setText(str(fmk))
            self.soil_edit_box.lineEdit_6.setText(str(fines_percentage))
        
            self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
            self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
            self.plot_canvas.axes.set_axis_off()     
            self.plot_layout.addWidget(self.plot_canvas)

            # Update table once at first by default
            self.continue_edit_wall_MIP(isdefined)

            # Update table if 'Update' is clicked
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.continue_edit_wall_MIP(isdefined))
            self.soil_edit_box.pushButton_2.clicked.connect(self.estimate_E_Modul_MIP)
            self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)
        
            # Save wall properties to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(wall_box))    #<-- Conditional close
        
            wall_box.exec_()


    def estimate_E_Modul_MIP(self):
        """ Estimates E-Module for MIP
        """
        try:
            fmk = float(self.soil_edit_box.lineEdit_5.text())
            fines_percentage = float(self.soil_edit_box.lineEdit_6.text())
            E_MIP = calc_E_Modul_MIP(fmk, fines_percentage)
            # display the estimated E-modulus for MIP
            self.soil_edit_box.lineEdit_2.setText('{:.2f}'.format(E_MIP*1000))  # kPa

        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")


    def continue_edit_wall_MIP(self, isdefined):
        try:
            material_name = self.soil_edit_box.lineEdit.text()
            Eref = float(self.soil_edit_box.lineEdit_2.text())
            nu = float(self.soil_edit_box.lineEdit_4.text())
            Gref = Eref/(2*(1 + nu))
            d = float(self.soil_edit_box.lineEdit_3.text())
            
            EA = Eref*d*1.0
            EA2 = EA
            EI = Eref*(d**3*1.0/12)
            w = d*10.0

            fmk = float(self.soil_edit_box.lineEdit_5.text())
            fines_percentage = float(self.soil_edit_box.lineEdit_6.text())
            
            new_values = {'MaterialName': material_name, 'd': d, 'Gref': Gref, 'nu': nu, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'fmk': fmk, 'fines_percentage': fines_percentage}
            
            # Load json, update with new property values, and show on table
            self.load_and_update_json(new_values, isdefined)
            
            # Plot wall cross-section
            self.plot_canvas.plot_dwall_cross_section(d)
                    
        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")


    def open_edit_wall_SPW(self, wall_type, user_wall_name, SPW131=False, color=QtGui.QColor(200, 255, 255).name(), isdefined = False):
        wall_box = QtWidgets.QDialog()
        self.soil_edit_box = editWallBox_SPW()
        self.soil_edit_box.setupUi(wall_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        wall_box.setWindowTitle(wall_type + ' properties')
        self.soil_edit_box.json_item = None      # json file name for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file name for writing/ reading from user redefined database
        self.soil_edit_box.SPW131 = SPW131
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        # Load default values from json file
        if isdefined is False:
            self.soil_edit_box.json_item = 'WALL_' + wall_type # json file name for reading
            #self.soil_edit_box.json_item_user = user_wall_name + '_' + wall_type # json file name for writing
            self.soil_edit_box.json_item_user = user_wall_name  # json file name for writing
            self.load_and_update_json(None)
        else:
            self.soil_edit_box.json_item_user = user_wall_name # josn file name for reading/ writing
            self.load_and_update_json(None, True)
        
        # Continue only if data is successfully loaded
        if self.soil_edit_box.data:
            MaterialName = self.soil_edit_box.json_item_user
            nu = self.soil_edit_box.data['nu']

            D = self.soil_edit_box.data['D']
            S = self.soil_edit_box.data['S']
            EA = self.soil_edit_box.data['EA']
            if self.soil_edit_box.SPW131:
                Eref = get_Eref_SPW131(D, S, EA)
            else:
                Eref = get_Eref_SPW(D, S, EA)

            self.soil_edit_box.lineEdit.setText(MaterialName)
            self.soil_edit_box.lineEdit_2.setText(str(Eref))
            self.soil_edit_box.lineEdit_4.setText(str(nu))
            self.soil_edit_box.lineEdit_3.setText(str(D))
            self.soil_edit_box.lineEdit_5.setText(str(S))

            # set check state for SPW131
            if self.soil_edit_box.SPW131:
                self.soil_edit_box.checkBox.setCheckState(2)
        
            self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
            self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
            self.plot_canvas.axes.set_axis_off()       
            self.plot_layout.addWidget(self.plot_canvas)

            # Update table once at first by default
            self.continue_edit_wall_SPW(isdefined)

            # Update table if 'Update' is clicked
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.continue_edit_wall_SPW(isdefined))    # <-- Continue editting wall
            self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)

        
            # Save wall properties to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(wall_box))    #<-- Conditional close

            wall_box.exec_()


    def continue_edit_wall_SPW(self, isdefined = False):
        try:
            material_name = self.soil_edit_box.lineEdit.text()
            Eref = float(self.soil_edit_box.lineEdit_2.text())
            nu = float(self.soil_edit_box.lineEdit_4.text())
            D = float(self.soil_edit_box.lineEdit_3.text())
            S = float(self.soil_edit_box.lineEdit_5.text())
            self.soil_edit_box.SPW131 =  self.soil_edit_box.checkBox.checkState() == 2  # saving state
            
            (EA, EA2, EI, w, d, Gref) = get_SPW_parameters(D, S, Eref, nu, self.soil_edit_box.SPW131)
            new_values = {'MaterialName': material_name, 'd': d, 'Gref': Gref, 'nu': nu, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'D': D, 'S': S}
            
            # Load json, update with new property values, and show on table
            self.load_and_update_json(new_values, isdefined)
            
            # Plot wall cross-section
            self.plot_canvas.plot_SPW_cross_section(D, S, self.soil_edit_box.SPW131)
            
        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")
            

    def open_edit_wall_CPW(self, wall_type, user_wall_name, color=QtGui.QColor(200, 255, 255).name(), isdefined = False):
        wall_box = QtWidgets.QDialog()
        self.soil_edit_box = editWallBox_CPW()
        self.soil_edit_box.setupUi(wall_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        wall_box.setWindowTitle(wall_type + ' properties')
        self.soil_edit_box.json_item = None      # json file name for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file name for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        # Load default values from json file
        if isdefined is False:
            self.soil_edit_box.json_item = 'WALL_' + wall_type # json file name for reading
            #self.soil_edit_box.json_item_user = user_wall_name + '_' + wall_type # json file name for writing
            self.soil_edit_box.json_item_user = user_wall_name # json file name for writing
            self.load_and_update_json(None)
        else:
            self.soil_edit_box.json_item_user = user_wall_name # josn file name for reading/ writing
            self.load_and_update_json(None, True)
        
        # Continue only if data is successfully loaded
        if self.soil_edit_box.data:
            MaterialName = self.soil_edit_box.json_item_user
            nu = self.soil_edit_box.data['nu']

            D = self.soil_edit_box.data['D']
            S = self.soil_edit_box.data['S']
            EA = self.soil_edit_box.data['EA']
            Eref = get_Eref_CPW(D, S, EA)

            self.soil_edit_box.lineEdit.setText(MaterialName)
            self.soil_edit_box.lineEdit_2.setText(str(Eref))
            self.soil_edit_box.lineEdit_4.setText(str(nu))
            self.soil_edit_box.lineEdit_3.setText(str(D))
            self.soil_edit_box.lineEdit_5.setText(str(S))
        
            self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
            self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
            self.plot_canvas.axes.set_axis_off()      
            self.plot_layout.addWidget(self.plot_canvas)

            # Update table once at first by default
            self.continue_edit_wall_CPW(isdefined)
            #self.plot_canvas.plot_CPW_cross_section(D, S)

            # Update table if 'Update' is clicked
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.continue_edit_wall_CPW(isdefined))    # <-- Continue editting wall
            self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)
                                                         
            # Save wall properties to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(wall_box))    #<-- Conditional close
        
            wall_box.exec_()


    def continue_edit_wall_CPW(self, isdefined = False):
        try:
            material_name = self.soil_edit_box.lineEdit.text()
            Eref = float(self.soil_edit_box.lineEdit_2.text())
            nu = float(self.soil_edit_box.lineEdit_4.text())
            D = float(self.soil_edit_box.lineEdit_3.text())
            S = float(self.soil_edit_box.lineEdit_5.text())
            
            (EA, EA2, EI, w, d, Gref) = get_CPW_parameters(D, S, Eref, nu)
            new_values = {'MaterialName': material_name, 'd': d, 'Gref': Gref, 'nu': nu, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'D': D, 'S': S}
            
            # Load json, update with new property values, and show on table
            self.load_and_update_json(new_values, isdefined)
            
            # Plot wall cross-section
            self.plot_canvas.plot_CPW_cross_section(D, S)
            
        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")
        

    def open_edit_wall_Steel_profile(self, wall_type, user_wall_name, color=QtGui.QColor(200, 255, 255).name(), isdefined = False):
        wall_box = QtWidgets.QDialog()
        self.soil_edit_box = editWallBox_Steel_profile()
        self.soil_edit_box.setupUi(wall_box)
        wall_box.setWindowTitle(wall_type + ' properties')
        self.soil_edit_box.json_item = None      # json file name for reading from MONIMAN database
        self.soil_edit_box.json_item_user = None # json file name for writing/ reading from user redefined database
        self.soil_edit_box.done = False
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.color = color # default color
        self.soil_edit_box.pushButton_3.setStyleSheet("background-color: %s" % self.soil_edit_box.color)
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        profile_names = self.get_steel_profile_names()
        self.soil_edit_box.comboBox.addItems(profile_names)


        # Load default values from json file
        if isdefined is False:
            self.soil_edit_box.json_item = 'WALL_Profile' # json file name for reading
            self.soil_edit_box.json_item_user = user_wall_name # json file name for writing
            self.load_and_update_json(None)
        else:
            self.soil_edit_box.json_item_user = user_wall_name # json file name for reading/ writing
            self.load_and_update_json(None, True)
        
        # Continue only if data is successfully loaded
        if self.soil_edit_box.data:
            MaterialName = self.soil_edit_box.json_item_user
            nu = self.soil_edit_box.data['nu']
            S = self.soil_edit_box.data['S']
            profile_nos = int(self.soil_edit_box.data['nos'])    # number of steel profiles
            E = 210.0e6

            self.soil_edit_box.lineEdit.setText(str(profile_nos))
            self.soil_edit_box.lineEdit_2.setText(str(E))
            self.soil_edit_box.lineEdit_2.setReadOnly(True)
            self.soil_edit_box.lineEdit_2.setStyleSheet("background-color: rgb(215, 215, 215);")
            self.soil_edit_box.lineEdit_4.setText(str(nu))
            self.soil_edit_box.lineEdit_5.setText(str(S))
        
            # Update table once at first by default
            if isdefined is False:
                self.continue_edit_wall_Steel_profile(isdefined)
            else: # set index for profile in combobox
                profile_name = self.soil_edit_box.data['MaterialName']
                index_profile = profile_names.index(profile_name)
                self.soil_edit_box.comboBox.setCurrentIndex(index_profile)

            # Update table if 'Update' is clicked
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.continue_edit_wall_Steel_profile(isdefined))    # <-- Continue editting wall
            self.soil_edit_box.pushButton_3.clicked.connect(self.select_soil_color)
                                                         
            # Save wall properties to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))                  #<-- Write properties in table to json file
            self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(wall_box))                      #<-- Conditional close
        
            wall_box.exec_()


    def continue_edit_wall_Steel_profile(self, isdefined = False):
        try:
            if not isdefined:
                profile_name = self.soil_edit_box.comboBox.currentText()
                self.soil_edit_box.json_item_user = profile_name    # wall name is profile name
            else:
                profile_name = self.soil_edit_box.json_item_user[:-2]

            profile_nos = int(self.soil_edit_box.lineEdit.text())
            E = float(self.soil_edit_box.lineEdit_2.text())
            nu = float(self.soil_edit_box.lineEdit_4.text())
            S = float(self.soil_edit_box.lineEdit_5.text())

            # read profile data from library
            PATH_PROFILE_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN'],'solver\plaxis2d\profile_steels_H_U\jsons')
            with open(join(PATH_PROFILE_LIBRARY, profile_name + '.json'), "r") as read_file:
                data = json.load(read_file, object_pairs_hook = OrderedDict)
            A = profile_nos*float(data["A"])           # [cm^2]
            I = profile_nos*float(data["I-y"])         # [cm^4]
            
            (EA, EA2, EI, w, d, Gref) = get_steel_profile_parameters(A, I, S, E, nu)
            new_values = {'MaterialName': profile_name, 'd': d, 'Gref': Gref, 'nu': nu, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'S': S, 'nos': profile_nos}
            
            # Load json, update with new property values, and show on table
            self.load_and_update_json(new_values, isdefined)
            
        except ValueError:
            self.show_message_box('Warning', "Please check if values correctly entered!")


    def get_steel_profile_names(self):
        """ Gets available steel profiles to select
        """
        PATH_PROFILE_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons')
        profile_names = []
        for item in glob.glob(PATH_PROFILE_LIBRARY + '\\*'):
            profile_name = os.path.basename(item)
            profile_names.append(profile_name[:-5]) # no file ending '.json'
        
        return profile_names
    

    def open_edit_strand(self, strand_dia, no_strand, Lspacing, anchor_name, isdefined = False):
        """ Open dialog for editting ground anchor's trand properties
        """
        strand_box = QtWidgets.QDialog()
        self.soil_edit_box = editStrandBox()
        self.soil_edit_box.setupUi(strand_box)
        self.soil_edit_box.anchor_name = anchor_name
        self.soil_edit_box.json_item = None
        self.soil_edit_box.json_item_user = None # MOMINAN json file name for a user defined strand
        self.soil_edit_box.done = None
        strand_box.setWindowTitle('Strand properties for ' + anchor_name)
        self.soil_edit_box.parameters_selected = {}
        
        #if isdefined is False:
        #    self.soil_edit_box.json_item = 'ANCHOR_STRAND_' + 
        #    self.soil_edit_box.json_item_user = anchor_name + '_ANCHOR_GROUT_Linear' # MOMINAN json file name for a user defined grout body
        #else:
        #    self.soil_edit_box.json_item_user = anchor_name


        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            EA = self.calc_EA_strand(strand_dia, no_strand)
            self.match_json_name_strand()
            new_values = {'MaterialName': self.soil_edit_box.json_item_user, 'EA': EA, 'Lspacing': Lspacing}
        else:
            self.soil_edit_box.json_item_user = anchor_name
            new_values = None

        
        if isdefined is False:
            #self.soil_edit_box.pushButton.clicked.connect(self.match_json_name_strand)
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json(new_values, isdefined))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_dependent_parameters_strand(strand_dia, no_strand))
        else:
            self.soil_edit_box.json_item_user = anchor_name
            self.load_and_update_json(new_values, isdefined)
            self.load_dependent_parameters_strand(strand_dia, no_strand)
            self.soil_edit_box.pushButton.setEnabled(False)

        self.soil_edit_box.pushButton_2.clicked.connect(lambda: self.update_dependent_parameters_strand(strand_dia, no_strand))

        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file  
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(strand_box))    #<-- Conditional close
                                                     
        strand_box.exec_()
    
    
    def match_json_name_strand(self):
        material_type = self.soil_edit_box.comboBox.currentText()
        self.soil_edit_box.json_item = 'ANCHOR_STRAND_' + material_type 
        self.soil_edit_box.json_item_user = self.soil_edit_box.anchor_name + '_STRAND_' + material_type 

        
    def calc_EA_strand(self, strand_dia, no_strand, E=195.0E6):
        if strand_dia == "0.6''":
            return E * 140.0E-6 * no_strand # kN
        elif strand_dia == "0.62''":
            return E * 140.0E-6 * no_strand # kN
        else:
            return None
    

    def load_dependent_parameters_strand(self, strand_dia, no_strand):
           
        EA = self.soil_edit_box.data['EA']
        if strand_dia == "0.6''":
            E = EA / (140.0E-6 * no_strand)
        elif strand_dia == "0.62''":
            E = EA / (150.0E-6 * no_strand)
        else:
            E = 0.0
       
        self.soil_edit_box.lineEdit.setText(str(E))


    def update_dependent_parameters_strand(self, strand_dia, no_strand):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else: 
            try:
                E = float(self.soil_edit_box.lineEdit.text())          
                EA = self.calc_EA_strand(strand_dia, no_strand, E)
                updated_parameters = {'EA': EA}
                
                self.update_table(updated_parameters)
                
            except ValueError:
                self.show_message_box('Warning', "Please check if Young's modulus is correctly entered!")
                      
    
    def open_edit_grout_Linear(self, strand_dia, no_strand, Lspacing, anchor_name, isdefined = False):
        """ Opens dialog for editting ground anchor's grout properties
        """
        grout_box = QtWidgets.QDialog()
        self.soil_edit_box = editGroutLinearBox()
        self.soil_edit_box.setupUi(grout_box)
        grout_box.setWindowTitle('Linear skin resistance grout properties for ' + anchor_name)
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.done = None

        if isdefined is False:
            self.soil_edit_box.json_item = 'ANCHOR_GROUT_Linear' 
            self.soil_edit_box.json_item_user = anchor_name + '_GROUT_Linear' # MOMINAN json file name for a user defined grout body
        else:
            self.soil_edit_box.json_item_user = anchor_name
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            new_values = {'MaterialName': self.soil_edit_box.json_item_user, 'Lspacing': Lspacing}        
        else:
            new_values = None

        self.load_and_update_json(new_values, isdefined)
        
        Tstart = self.soil_edit_box.data['Tstart']
        Tend = self.soil_edit_box.data['Tend']
        E = self.soil_edit_box.data['E']
        Diameter = self.soil_edit_box.data['Diameter']
        
        self.soil_edit_box.lineEdit.setText(str(E))
        self.soil_edit_box.lineEdit_2.setText(str(Tstart))
        self.soil_edit_box.lineEdit_3.setText(str(Tend))
        self.soil_edit_box.lineEdit_4.setText(str(Diameter))
        
        self.soil_edit_box.pushButton.clicked.connect(self.update_grout_Linear)
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(grout_box))    #<-- Conditional close

        grout_box.exec_()
        

    def update_grout_Linear(self):
        try:
            E = float(self.soil_edit_box.lineEdit.text())
            Tstart = float(self.soil_edit_box.lineEdit_2.text())
            Tend = float(self.soil_edit_box.lineEdit_3.text())
            Diameter = float(self.soil_edit_box.lineEdit_4.text())
            
            updated_parameters = {'E': E, 'Tstart':Tstart, 'Tend':Tend, 'Diameter': Diameter, 'A': (Diameter/2)**2 * np.pi}
            self.update_table(updated_parameters)
            
        except ValueError:
            self.show_message_box('Warning', 'Please check if values are correctly entered!')
        

    def open_edit_grout_Multilinear(self, strand_dia, no_strand, Lspacing, anchor_name, isdefined = False):
        """ Open dialog for editting ground anchor's grout properties
        """
        grout_box = QtWidgets.QDialog()
        self.soil_edit_box = editGroutMultilinearBox()
        self.soil_edit_box.setupUi(grout_box)
        grout_box.setWindowTitle('Multi-linear skin resistance grout properties for ' + anchor_name)
        self.soil_edit_box.parameters_selected = {}
        self.soil_edit_box.done = None

        if isdefined is False:
            self.soil_edit_box.json_item = 'ANCHOR_GROUT_Multilinear' 
            self.soil_edit_box.json_item_user = anchor_name + '_GROUT_Multilinear' # MOMINAN json file name for grout properties is similar to the default database file
        else:
            self.soil_edit_box.json_item_user = anchor_name
        
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            new_values = {'MaterialName': self.soil_edit_box.json_item_user, 'Lspacing': Lspacing}        
        else:
            new_values = None

        self.load_and_update_json(new_values, isdefined)
        
        E = self.soil_edit_box.data['E']        
        Diameter = self.soil_edit_box.data['Diameter']

        self.soil_edit_box.lineEdit.setText(str(E))
        self.soil_edit_box.lineEdit_2.setText(str(Diameter))
        
        if isdefined is False:
            SkinResistanceTable = self.soil_edit_box.data['SkinResistanceTable']
        else:
            SkinResistanceTable = eval(self.soil_edit_box.data['SkinResistanceTable'])

        distance = SkinResistanceTable[::2] 
        skin_resistance = SkinResistanceTable[1::2] 
        self.soil_edit_box.tableWidget_2.setColumnCount(5)
        for col in range(len(distance)):
            self.soil_edit_box.tableWidget_2.setItem(0, col, QtWidgets.QTableWidgetItem(str(distance[col])))
            self.soil_edit_box.tableWidget_2.setItem(1, col, QtWidgets.QTableWidgetItem(str(skin_resistance[col])))
        
        self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
        self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_canvas.axes.set_axis_off()     
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_canvas.plot_multilinear_skin_resistance(distance, skin_resistance)

        self.soil_edit_box.pushButton.clicked.connect(self.update_grout_Multilinear)
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(grout_box))    #<-- Conditional close

        grout_box.exec_()
        

    def update_grout_Multilinear(self):
        try:
            E = float(self.soil_edit_box.lineEdit.text())          
            Diameter = float(self.soil_edit_box.lineEdit_2.text())          

            distance = []
            skin_resistance = []
            for col in range(self.soil_edit_box.tableWidget_2.columnCount()):
                distance_item = self.soil_edit_box.tableWidget_2.item(0, col)
                skin_resistance_item = self.soil_edit_box.tableWidget_2.item(1, col)
                if (distance_item is not None) and (skin_resistance_item is not None):
                    distance.append(float(distance_item.text()))
                    skin_resistance.append(float(skin_resistance_item.text()))
            
            self.plot_canvas.plot_multilinear_skin_resistance(distance, skin_resistance)
            
            table = [None]*2*len(distance)
            table[::2] = distance
            table[1::2] = skin_resistance
            updated_parameters = {'E': E, 'SkinResistanceTable': table, 'Diameter': Diameter, 'A': (Diameter/2)**2 * np.pi}
            self.update_table(updated_parameters)
            
        except ValueError:
            self.show_message_box('Warning', 'Please check if values are correctly entered!')
            
    def open_edit_strut_Steel_tube(self, Lspacing, strut_name, isdefined = False):
        """ Open dialog for editting ground anchor's trand properties
        """
        strut_box = QtWidgets.QDialog()
        self.soil_edit_box = editStrutSteeltube()
        self.soil_edit_box.setupUi(strut_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        self.soil_edit_box.strut_name = strut_name
        self.soil_edit_box.json_item = None
        self.soil_edit_box.json_item_user = None
        self.soil_edit_box.done = False
        strut_box.setWindowTitle('Strut properties for ' + strut_name)
        self.soil_edit_box.parameters_selected = {}
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            d_outer = 0.6
            d_inner = 0.54
            E = 210E6
            A = np.pi/4 * (d_outer**2 - d_inner**2)
            EA = E * A
            fyk, gamma_s = 355.0, 1.15
            new_values = {'Lspacing': Lspacing, 'EA': EA, 'E': E, 'd_outer': d_outer, 'd_inner': d_inner, 'fyk': fyk, 'gamma_s': gamma_s}   # E, d_outer, d_inner, fyk, gamma_s are moniman params
            self.soil_edit_box.lineEdit_2.setText(str(d_outer))
            self.soil_edit_box.lineEdit_3.setText(str(d_inner))
            self.soil_edit_box.lineEdit_4.setText(str(fyk))
            self.soil_edit_box.lineEdit_5.setText(str(gamma_s))
            self.soil_edit_box.lineEdit.setText(str(E))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_strut('Steel_tube'))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json(new_values, isdefined))

        else:
            new_values = None
            self.soil_edit_box.pushButton.setEnabled(False)
            self.soil_edit_box.json_item_user = strut_name
            self.load_and_update_json(new_values, isdefined)
            E = self.soil_edit_box.data['E']
            d_outer = self.soil_edit_box.data['d_outer']
            d_inner = self.soil_edit_box.data['d_inner']
            fyk = self.soil_edit_box.data['fyk']
            gamma_s = self.soil_edit_box.data['gamma_s']
            self.soil_edit_box.lineEdit.setText(str(E))
            self.soil_edit_box.lineEdit_2.setText(str(d_outer))
            self.soil_edit_box.lineEdit_3.setText(str(d_inner))
            self.soil_edit_box.lineEdit_4.setText(str(fyk))
            self.soil_edit_box.lineEdit_5.setText(str(gamma_s))
        
        # Add plot_canvas and plot strut
        self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
        self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_canvas.axes.set_axis_off()     
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_canvas.plot_Steeltube_cross_section(d_outer, d_inner)
        
        # Update with basic parameters of steel tube
        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_strut_Steel_tube)
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file  
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(strut_box))    #<-- Conditional close
                                                     
        strut_box.exec_()

    def match_json_name_strut(self, strut_type):
        material_type = self.soil_edit_box.comboBox.currentText()
        #self.soil_edit_box.json_item = 'STRUT_' + strut_type.replace(' ', '_') + '_' + material_type 
        self.soil_edit_box.json_item = 'STRUT_' + material_type 
        #self.soil_edit_box.json_item_user = self.soil_edit_box.strut_name + '_STRUT_' + material_type 
        self.soil_edit_box.json_item_user = self.soil_edit_box.strut_name + '_' + strut_type + '_' + material_type 

        
    def update_dependent_parameters_strut_Steel_tube(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else: 
            try:
                E = float(self.soil_edit_box.lineEdit.text())  
                d_outer = float(self.soil_edit_box.lineEdit_2.text())
                d_inner = float(self.soil_edit_box.lineEdit_3.text())
                fyk = float(self.soil_edit_box.lineEdit_4.text())   # MPa
                gamma_s = float(self.soil_edit_box.lineEdit_5.text())
                if d_outer < d_inner:
                    self.show_message_box('Warning', "Steel tube's outer diameter must be larger than its inner parameter!")
                else:
                    A = np.pi/4 * (d_outer**2 - d_inner**2) # m^2
                    EA = E * A
                    FMaxComp = A*fyk*1000/gamma_s           # kN
                    updated_parameters = {'EA': EA ,'E': E, 'd_outer': d_outer, 'd_inner': d_inner, 'FMaxComp': FMaxComp, 'FMaxTens': FMaxComp}
                    
                    self.update_table(updated_parameters)
                    
                    self.plot_canvas.plot_Steeltube_cross_section(d_outer, d_inner)
                
            except ValueError:
                self.show_message_box('Warning', "Please check if Steel tube's parameters are correctly entered!")
                
    def open_edit_strut_RC_bar(self, Lspacing, strut_name, isdefined = False):
        """ Open dialog for editting ground anchor's trand properties
        """
        strut_box = QtWidgets.QDialog()
        self.soil_edit_box = editStrutRCbar()
        self.soil_edit_box.setupUi(strut_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        self.soil_edit_box.strut_name = strut_name
        self.soil_edit_box.json_item = None
        self.soil_edit_box.json_item_user = None
        self.soil_edit_box.done = False
        strut_box.setWindowTitle('Strut properties for ' + strut_name)
        self.soil_edit_box.parameters_selected = {}
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            width = 0.6
            height = 0.54
            concrete_grade = self.soil_edit_box.comboBox_2.currentText()
            E = self.concrete_secant_elastic_modulus(concrete_grade)
            A = width * height
            EA = E * A
            new_values = {'Lspacing': Lspacing, 'EA': EA, 'width': width, 'height': height, 'concrete_grade': concrete_grade } # width, height, and concrete_grade are moniman params
            self.soil_edit_box.lineEdit_2.setText(str(width))
            self.soil_edit_box.lineEdit_3.setText(str(height))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_strut('RC_strut'))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json(new_values, isdefined))
        else:
            new_values = None
            self.soil_edit_box.pushButton.setEnabled(False)
            self.soil_edit_box.json_item_user = strut_name
            self.load_and_update_json(new_values, isdefined)
            width = self.soil_edit_box.data['width']
            height = self.soil_edit_box.data['height']
            concrete_grade = self.soil_edit_box.data['concrete_grade']
            self.set_combobox_concrete_grad(concrete_grade, self.soil_edit_box.comboBox_2)
            self.soil_edit_box.lineEdit_2.setText(str(width))
            self.soil_edit_box.lineEdit_3.setText(str(height))

        # Add plot_canvas and plot strut
        self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
        self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_canvas.axes.set_axis_off()     
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_canvas.plot_RCstrut_cross_section(width, height)

        # Update with basic RC bar parameters
        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_strut_RC_bar)
        
        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file  
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(strut_box))    #<-- Conditional close
                                                     
        strut_box.exec_()


    def update_dependent_parameters_strut_RC_bar(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else: 
            try:
                width = float(self.soil_edit_box.lineEdit_2.text())
                height = float(self.soil_edit_box.lineEdit_3.text())
                concrete_grade = self.soil_edit_box.comboBox_2.currentText()
                E = self.concrete_secant_elastic_modulus(concrete_grade)
                A = width * height
                EA = E * A
                updated_parameters = {'EA': EA, 'width': width, 'height': height, 'concrete_grade': concrete_grade}
                
                self.update_table(updated_parameters)
                
                self.plot_canvas.plot_RCstrut_cross_section(width, height)
                
            except ValueError:
                self.show_message_box('Warning', "Please check if RC bar's parameters are correctly entered!")
                
                
    def concrete_secant_elastic_modulus(self, concrete_grade):
        fck_dict = {'C12/15': 12, 'C16/20': 16, 'C20/25': 20, 'C25/30': 25, 'C30/37': 30 , 'C35/45': 35, 'C40/50': 40, 'C45/55': 45,
                     'C50/60': 50, 'C55/67': 55, 'C60/75': 60, 'C70/85': 70, 'C80/95': 80, 'C90/105': 90, 'C100/115': 100} #MPa
        fcm = fck_dict[concrete_grade] + 8# MPa
        Ecm = 22.0E6*(fcm/10)**0.3 # KPa    
        
        return Ecm

    def set_combobox_concrete_grad(self, concrete_grade, combobox):
        """ Sets concrete_grade item in combobox
        """
        for i in range(combobox.count()):
            itemtext = combobox.itemText(i)
            if itemtext == concrete_grade:
                combobox.setCurrentIndex(i)
                break


    def open_edit_strut_RC_slab(self, strut_name, isdefined = False):
        """ Open dialog for editting ground anchor's trand properties
        """
        strut_box = QtWidgets.QDialog()
        self.soil_edit_box = editStrutRCslab()
        self.soil_edit_box.setupUi(strut_box)
        self.soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        self.soil_edit_box.strut_name = strut_name
        self.soil_edit_box.json_item = None
        self.soil_edit_box.json_item = None
        self.soil_edit_box.done = False
        strut_box.setWindowTitle('Strut properties for ' + strut_name)
        self.soil_edit_box.parameters_selected = {}
        
        # 'OK' botton is enabled only if json file has not been loaded to table
        self.soil_edit_box.json_loaded = False
        self.soil_edit_box.buttonBox.setEnabled(self.soil_edit_box.json_loaded)
        # QDialog can be closed only after saving table to json
        self.soil_edit_box.can_close_now = False
        
        if isdefined is False:
            thickness = 0.4
            concrete_grade = self.soil_edit_box.comboBox_2.currentText()
            E = self.concrete_secant_elastic_modulus(concrete_grade)
            A = thickness * 1.0
            EA = E * A
            new_values = {'Lspacing': 1.0, 'EA': EA, 'thickness': thickness, 'concrete_grade': concrete_grade} # thickness and concrete_grade are moniman parameters
            self.soil_edit_box.lineEdit_2.setText(str(thickness))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.match_json_name_strut('RC_slab'))
            self.soil_edit_box.pushButton.clicked.connect(lambda: self.load_and_update_json(new_values, isdefined))
        else:
            new_values = None
            self.soil_edit_box.pushButton.setEnabled(False)
            self.soil_edit_box.json_item_user = strut_name
            self.load_and_update_json(new_values, isdefined)
            thickness = self.soil_edit_box.data['thickness']
            concrete_grade = self.soil_edit_box.data['concrete_grade']
            self.soil_edit_box.lineEdit_2.setText(str(thickness))
            self.set_combobox_concrete_grad(concrete_grade, self.soil_edit_box.comboBox_2)
        
        # Add plot_canvas and plot strut
        self.plot_layout = QtWidgets.QVBoxLayout(self.soil_edit_box.widget)
        self.plot_canvas = MyStaticMplCanvas(self.soil_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_canvas.axes.set_axis_off()     
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_canvas.plot_RCslab_cross_section(thickness)
        
        # Update with basic RC slab parameters
        self.soil_edit_box.pushButton_2.clicked.connect(self.update_dependent_parameters_strut_RC_slab)

        # Save material properties to json file   
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.save_table_to_json(isdefined))   # <-- Update materials in json file  
        self.soil_edit_box.buttonBox.accepted.connect(lambda: self.close_dialog_box(strut_box))    #<-- Conditional close
                                                     
        strut_box.exec_()


    def update_dependent_parameters_strut_RC_slab(self):
        if self.soil_edit_box.json_loaded is False:
            self.show_message_box('Warning', 'Please load material first!')
        else: 
            try:
                thickness = float(self.soil_edit_box.lineEdit_2.text())
                concrete_grade = self.soil_edit_box.comboBox_2.currentText()
                E = self.concrete_secant_elastic_modulus(concrete_grade)
                A = thickness * 1.0
                EA = E * A
                updated_parameters = {'EA': EA, 'thickness': thickness, 'concrete_grade': concrete_grade}
                
                self.update_table(updated_parameters)
                
                self.plot_canvas.plot_RCslab_cross_section(thickness)
                
            except ValueError:
                self.show_message_box('Warning', "Please check if RC slab's parameters are correctly entered!")
                

    def load_and_update_json(self, new_values = None, isdefined = False):

        PATHS = sys.modules['moniman_paths']
        if isdefined is False:
            PATH_MATERIAL_LIBRARY = join(PATHS['MONIMAN'], r'solver\plaxis2d\materials')
            fname = join(PATH_MATERIAL_LIBRARY, self.soil_edit_box.json_item + '.json')
            if isfile(fname):
                with open(fname, "r") as read_file:
                    self.soil_edit_box.data = json.load(read_file, object_pairs_hook = OrderedDict)         
            else: # json file does not exist
                self.show_message_box('Warning', "No material file for the selected item is found!")
                self.soil_edit_box.data = None

        else:
            PATH_MATERIAL_LIBRARY = join(PATHS['MONIMAN_OUTPUTS'],'materials')
            fname = join(PATH_MATERIAL_LIBRARY, self.soil_edit_box.json_item_user + 'moniman.json')
            if isfile(fname):
                with open(fname, "r") as read_file:
                    self.soil_edit_box.data = json.load(read_file, object_pairs_hook = OrderedDict)         
            else: # json file does not exist
                self.show_message_box('Warning', "No material file for the selected item is found!")
                self.soil_edit_box.data = None

        if self.soil_edit_box.data: # if data has been successfully loaded
            self.soil_edit_box.data = OrderedDict(self.soil_edit_box.data) # convert data to an ordered dictionary

            # Overload with the above defined values of basic properties (MaterialName, Gref, nu)
            if new_values is not None:
                for key, value in new_values.items():
                    self.soil_edit_box.data[key] = value
        
            # Read values to table for viewing and further editting
            self.soil_edit_box.tableWidget.setRowCount(3)
            self.soil_edit_box.tableWidget.setColumnCount(0)
            column = 0
            for key, value in self.soil_edit_box.data.items():
                self.soil_edit_box.tableWidget.insertColumn(column)
                self.soil_edit_box.tableWidget.setItem(0, column, QtWidgets.QTableWidgetItem(str(key)))
                self.soil_edit_box.tableWidget.setItem(1, column, QtWidgets.QTableWidgetItem(str(value)))

                self.soil_edit_box.tableWidget.setCellWidget(2, column, QtWidgets.QCheckBox('Sensitivity?'))

                column += 1
        
            self.soil_edit_box.json_loaded = True        
            self.soil_edit_box.buttonBox.setEnabled(True)
        
        else:
            self.soil_edit_box.can_close_now = True
        
    
    def update_table(self, new_values):
        # Display updated parameter values onto table
        num_column = self.soil_edit_box.tableWidget.columnCount()
        for column_i in range(num_column):
            item = QtWidgets.QTableWidgetItem(self.soil_edit_box.tableWidget.item(0, column_i)).text()
            if item in new_values:
                self.soil_edit_box.tableWidget.setItem(1, column_i, QtWidgets.QTableWidgetItem(str(new_values[item])))

    
    def close_dialog_box(self, dialogBox):
        if self.soil_edit_box.can_close_now is True:
            self.soil_edit_box.done = True
            dialogBox.close()
            

    def save_table_to_json(self, isdefined = False):
        close_event = QtGui.QCloseEvent()
        #close_event = self.soil_edit_box.
        try:
            # Update with the recent edited materials entered in the table
            for i, key in enumerate(self.soil_edit_box.data.keys()):
                self.soil_edit_box.data[key] = QtWidgets.QTableWidgetItem(self.soil_edit_box.tableWidget.item(1, i)).text()
                # Append the list of selected parameters (for sensitivity and back-analysis)
                if self.soil_edit_box.tableWidget.cellWidget(2, i).checkState() == 2:
                    #self.soil_edit_box.parameters_selected.append(key)
                    self.soil_edit_box.parameters_selected[key] = float(self.soil_edit_box.data[key])
                self.soil_edit_box.parameters_selected = OrderedDict(sorted(self.soil_edit_box.parameters_selected.items(), key=lambda t: t[0]))
            
            if 'HS' in self.soil_edit_box.json_item_user:
                # K0nc condition for HS/ HSsmall model
                K0nc, phi = get_HS_K0nc_empirical(float(self.soil_edit_box.data['phi']))
                self.soil_edit_box.data['K0nc'] = K0nc 
                self.soil_edit_box.data['phi'] = phi

            # remove non-plaxis parameters:
            # HS/HSsmall non-plaxis parameters: ve, we
            # Wall SPW/CPW non-plaxis parameters: D, S
            # Wall steel profiles: nos
            # MIP wall: fmk, fines_percentage
            self.remove_data_nonplaxis_parameters()

            # material data in MONIMAN contains redundant properties for later reconstructing dependent parameters
            # and selecting soil parameters for sensitivity/ back-analysis
            self.soil_edit_box.data = set_plaxis_datatypes(self.soil_edit_box.data)
            self.soil_edit_box.data_moniman = set_plaxis_datatypes(self.soil_edit_box.data_moniman)
            self.soil_edit_box.data_moniman = set_nonplaxis_datatypes(self.soil_edit_box.data_moniman)
            
            # Write back to json file
            PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
            if not exists(PATH_MATERIAL_LIBRARY):
                os.makedirs(PATH_MATERIAL_LIBRARY)
                
            if not isdefined:
                redefined_material_json_item = self.soil_edit_box.json_item_user + '__'
            else:
                redefined_material_json_item = self.soil_edit_box.json_item_user

            # write data for PLAXIS2D
            with open(join(PATH_MATERIAL_LIBRARY, redefined_material_json_item + '.json'), "w") as write_file:
                 json.dump(self.soil_edit_box.data, write_file) 
            
            # write data for MONIMAN
            with open(join(PATH_MATERIAL_LIBRARY, redefined_material_json_item + 'moniman.json'), "w") as write_file:
                 json.dump(self.soil_edit_box.data_moniman, write_file) 

            # Note: accept and reject signals in dialog ui are replaced by self handling 
            # using self.close_dialog_box() and QtGui.QCloseEvent().ignore()
            self.soil_edit_box.can_close_now = True
            
                 
        except ValueError:
            self.show_message_box('Warning', "Please check if values in the table are correctly entered!")
            close_event.ignore()
           
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Dialog = Ui_Dialog()
    #Dialog.show_message_box('Sample title', 'Sample message')
    Dialog.open_edit_soil_material('Sample title')
    sys.exit(app.exec_())