# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 17:49:28 2020

@author: nya
"""

import os, sys
import subprocess
import csv, io
import json
import numpy as np
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtCore import pyqtSlot, QEvent
from numpy.lib.utils import _set_function_name
from tools.math import hex_to_rgb
from tools.json_functions import read_data_in_json_item
from gui.gui_main_matplotlib import MyStaticMplCanvas
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots_Dim
from gui.gui_dialog_edit_Stone_columns_ui import Ui_Dialog as editStoneColumns
from gui.gui_widget_StoneColumns_SoilClusters_ui import Ui_Dialog as StoneColumns_SoilClusters
from report.report_with_matplotlib import Report
from matplotlib.backends.backend_pdf import PdfPages
from system.system import load_paths


# load PATHS.py
load_paths(r'common\\PATHS.py')
ACROBAT = sys.modules['moniman_paths']['ACROBAT']

class StoneColumns():
    """ This class implements the structure of stone columns unit
    """
    def __init__(self, D=0.9, a=2.2, gamma_c=21.0, phi_c=45.0, ve=1000.0, we=0.5, nu_c=0.49, E_c=100e3, shape='triangle', Ac_over_A=0):
        """ Initializes geometrical and material properties of the stone column unit
        """
        self.params = OrderedDict()
        self.params['D'] = D                # diameter of stone columns [m]
        self.params['a'] = a                # spacing b/w stone columns [m]
        self.params['shape'] = shape        # Unit shape: 'trianle' or 'rectangle'
        self.params['gamma_c']  = gamma_c   # self weight of columns [kN/m^2]
        self.params['phi_c'] = phi_c        # effective stress friction angle of columns [°]
        #self.params['E_c'] = E_c           # Odoemeter stiffness modulus of columns [MPa]
        self.params['nu_c'] = nu_c          # Poisson's ratio of columns [-]
        self.params['ve'] = ve              # 
        self.params['we'] = we              # 
        self.params['E_c'] = E_c          # Constrained modulus for stone columns [kPa], can be edited by user
        self.params['Ac_over_A'] = self.get_Ac_over_A()      # 
        self.name = ''                      # Stone columns name


    
    def open_edit_Stone_columns(self, method, user_structure_name, isdefined=False):
        """ Opens dialog for defining D-wall
        """
        sc_box = QtWidgets.QDialog()
        self.sc_edit_box = editStoneColumns()
        self.sc_edit_box.setupUi(sc_box)
        self.sc_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        sc_box.setWindowTitle(method + ' properties')
        # plot canvas for cross-section of the stone columns unit
        self.plot_layout = QtWidgets.QVBoxLayout(self.sc_edit_box.widget)
        self.plot_canvas = MyStaticMplCanvas(self.sc_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_layout.addWidget(self.plot_canvas)

        # fill in table with default parameter values
        self.sc_edit_box.tableWidget.blockSignals(True)
        column_labels = ['Diameter\nD [m]', 'Spacing\na [m]', 'Shape','\N{GREEK SMALL LETTER GAMMA}_c [kN/m^3]', '\N{GREEK SMALL LETTER PHI}_c [°]',  'nu_c [-]', 've [-]', 'we [-]', 'E_c [kPa]', 'Ka [-]', 'Ko [-]', 'Ac/A [-]']
        self.sc_edit_box.tableWidget.setRowCount(1)
        self.sc_edit_box.tableWidget.setColumnCount(len(column_labels))
        self.sc_edit_box.tableWidget.setHorizontalHeaderLabels(column_labels)

        # stone columns structure name
        if isdefined:
            sc_name = user_structure_name
        else:
            sc_name = user_structure_name + '_SC'
        self.name = sc_name 
    
        for i, value in enumerate(self.params.values()):
            if i != int(2):
                self.sc_edit_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(value)))
                self.sc_edit_box.tableWidget.item(0, i).setBackground(QColor(242, 255, 116))
            else: # unit shape
                items = ['triangle', 'rectangle']
                combobox = QtWidgets.QComboBox()
                combobox.addItems(items)
                if self.params['shape']=='rectangle':
                    combobox.setCurrentIndex(1)
                else:
                    combobox.setCurrentIndex(0)
                combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
                combobox.currentIndexChanged.connect(lambda: self.update_parameters(0,2))
                self.sc_edit_box.tableWidget.setCellWidget(0, i, combobox)

        #E_c = 100*self.params['ve']
        Ka = self.get_Ka()
        Ko = self.get_Ko()
        Ac_over_A = self.get_Ac_over_A()
        #self.sc_edit_box.tableWidget.setItem(0, 8, QtWidgets.QTableWidgetItem(str(E_c)))
        self.sc_edit_box.tableWidget.setItem(0, 9, QtWidgets.QTableWidgetItem('{0:.3f}'.format(Ka)))
        self.sc_edit_box.tableWidget.setItem(0, 10, QtWidgets.QTableWidgetItem('{0:.3f}'.format(Ko)))
        self.sc_edit_box.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem('{0:.3f}'.format(Ac_over_A)))
        self.sc_edit_box.tableWidget.blockSignals(False)

        # plot cross-section of the unit
        self.plot_canvas.plot_stone_columns_cross_section(self.params['D'], self.params['a'], self.params['shape'])
        
        # connect table
        self.sc_edit_box.tableWidget.cellChanged.connect(lambda row, col: self.update_parameters(row, col))

        # store updated parameter when dialog box is closed
        self.sc_edit_box.buttonBox.accepted.connect(sc_box.close)
        sc_box.exec_()


    @pyqtSlot()
    def update_parameters(self, row, column):
        """ Updates parameters
        """
        if column != 2:
            value = float(self.sc_edit_box.tableWidget.item(0, column).text())
        if column == 0:
            self.params['D'] = value
            self.params['Ac_over_A'] = self.get_Ac_over_A()
            self.sc_edit_box.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem('{0:.3f}'.format(self.params['Ac_over_A'])))
            # plot cross-section of the unit
            self.plot_canvas.plot_stone_columns_cross_section(self.params['D'], self.params['a'], self.params['shape'])
        elif column == 1:
            self.params['a'] = value
            self.params['Ac_over_A'] = self.get_Ac_over_A()
            self.sc_edit_box.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem('{0:.3f}'.format(self.params['Ac_over_A'])))
            # plot cross-section of the unit
            self.plot_canvas.plot_stone_columns_cross_section(self.params['D'], self.params['a'], self.params['shape'])
        elif column == 3:
            self.params['gamma_c'] = value
        elif column == 4:
            self.params['phi_c'] = value
            # recalculate and display Ka, Ko
            Ka = self.get_Ka()
            Ko = self.get_Ko()
            self.sc_edit_box.tableWidget.blockSignals(True)
            self.sc_edit_box.tableWidget.setItem(0, 9, QtWidgets.QTableWidgetItem('{0:.3f}'.format(Ka)))
            self.sc_edit_box.tableWidget.setItem(0, 10, QtWidgets.QTableWidgetItem('{0:.3f}'.format(Ko)))
            self.sc_edit_box.tableWidget.blockSignals(False)
        elif column == 5:
            self.params['nu_c'] = value
        elif column == 6:
            self.params['ve'] = value
            E_c = 100*value
            self.sc_edit_box.tableWidget.setItem(0, 8, QtWidgets.QTableWidgetItem('{0:.1f}'.format(E_c)))
            self.sc_edit_box.tableWidget.item(0, 8).setBackground(QColor(242, 255, 116))
        elif column == 7:
            self.params['we'] = value
        elif column == 8:
            self.params['E_c'] = value
        elif column == 2: # shape
            self.params['shape'] = self.sc_edit_box.tableWidget.cellWidget(0, 2).currentText()
            self.params['Ac_over_A'] = self.get_Ac_over_A()
            self.sc_edit_box.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem('{0:.3f}'.format(self.params['Ac_over_A'])))
            # plot cross-section of the unit
            self.plot_canvas.plot_stone_columns_cross_section(self.params['D'], self.params['a'], self.params['shape'])


    def get_A(self):
        """ Gets area for a unit of stone columns
        """
        a = self.params['a']
        if self.params['shape'] == 'triangle':
            A = a * a * np.cos(30*np.pi/180)
        else:   # rectangle
            A = a * a
        return A


    def get_Ac_over_A(self):
        """ Gets Ac/A ratio based on the default stone columns diameter
        """
        A = self.get_A()
        Ac = 1/4* np.pi * self.params['D']**2
        Ac_over_A = Ac/A
        #self.params['Ac_over_A'] = Ac_over_A      # attribute for use in cost calculation
        return Ac_over_A


    def get_Ac_over_A_with_D(self, D):
        """ Gets Ac/A ratio using user input stone columns diameter
        """
        A = self.get_A()
        Ac = 1/4* np.pi * D**2
        Ac_over_A = Ac/A
        #self.params['Ac_over_A'] = Ac_over_A      # attribute for use in cost calculation
        return Ac_over_A


    def get_Ka(self):
        """ Gets coefficient of active earth pressure after Rankine
        """
        alpha = np.pi * (45 - self.params['phi_c']/2) / 180
        Ka = np.tan(alpha)**2
        return Ka
    

    def get_Ko(self):
        """ Gets coefficient of earth pressure at rest
        """
        alpha = np.pi * self.params['phi_c'] / 180
        Ko = 1.0 - np.sin(alpha)
        return Ko


class StoneColumnsSoilClusters():
    """ This class divides soil layers and calculates layer and depth dependent improvement factors.
    Stiffness parameter for each of the homogenized will be factored accordingly.
    """
    def __init__(self, project_title, sc_params, improved_soil_polygon, Layer_polygons, borehole, sc_name, p0=10, unlimited_distribution=False, thickness_sublayer=2.0, limit_depth=0.0,
                user_input_E_s=False, should_consider_p0=False):
        """ Initializes with soil improvement polygon and stone columns parameters
        Layer_polygons: all soil layers defined in Plaxman
        p0: surcharge [kN/m^2]
        """
        self.project_title = project_title
        self.stone_columns = StoneColumns(**sc_params)
        self.soil_polygon = improved_soil_polygon
        self.columns_top = max([point['point'][1] for point in self.soil_polygon])
        self.columns_bottom = min([point['point'][1] for point in self.soil_polygon])
        self.columns_left = min([point['point'][0] for point in self.soil_polygon])
        self.columns_right = max([point['point'][0] for point in self.soil_polygon])
        self.columns_depth = self.columns_top - self.columns_bottom
        self.limit_depth = limit_depth if (limit_depth > 0.0) else self.columns_top - self.columns_bottom   # limit depth is columns length by default
        self.p0 = p0
        self.unlimited_distribution = unlimited_distribution
        self.thickness_sublayer = thickness_sublayer
        self.Layer_polygons = Layer_polygons
        self.borehole = borehole

        self.sc_name = sc_name      # sc_name is part of sub-soil cluster names
        self.sub_soillayers = []    # holds data for each of the sub-soil layers

        self.user_input_E_s = user_input_E_s            # user input constrained modulus for soils instead of stress dependence
        self.should_consider_p0 = should_consider_p0     # should consider surcharge for calculation of the improvement factor n2

        #self.open_stone_columns_soil_clusters()


    def open_stone_columns_soil_clusters(self):
        """ Opens the form for defining the improved soil polygon
        """
        sc_soil_box = QtWidgets.QDialog()
        self.sc_soil_edit_box = StoneColumns_SoilClusters()
        self.sc_soil_edit_box.setupUi(sc_soil_box)
        self.sc_soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        sc_soil_box.setWindowTitle('Improved soil properties (layer- and depth-dependent)')
        # plot canvas for cross-section of the stone columns unit
        self.plot_layout = QtWidgets.QVBoxLayout(self.sc_soil_edit_box.widget)
        #self.plot_canvas = MyStaticMplCanvas(self.sc_soil_edit_box.widget, width=1, height=1, dpi=100)
        self.plot_canvas = MyStaticMplCanvasSubplots_Dim(self.sc_soil_edit_box.widget, width=1, height=1, dpi=100, nrows=1, ncols=3)
        self.plot_layout.addWidget(self.plot_canvas)
        # make push buttons not responsive to enter key press
        self.sc_soil_edit_box.pushButton.setAutoDefault(False)
        self.sc_soil_edit_box.pushButton.setDefault(False)

        # show basic parameters
        #columns_top = max([point['point'][1] for point in self.soil_polygon])
        #columns_bottom = min([point['point'][1] for point in self.soil_polygon])
        self.sc_soil_edit_box.lineEdit.setText('{:.2f}'.format(self.p0))
        self.sc_soil_edit_box.lineEdit_2.setText('{:.2f}'.format(self.columns_top))
        self.sc_soil_edit_box.lineEdit_3.setText('{:.2f}'.format(self.columns_top - self.columns_bottom))
        self.sc_soil_edit_box.lineEdit_4.setText('{:.2f}'.format(self.thickness_sublayer))
        self.sc_soil_edit_box.lineEdit_5.setText('{:.2f}'.format(self.limit_depth))
        if self.user_input_E_s:
            self.sc_soil_edit_box.checkBox.setCheckState(2)
        else:
            self.sc_soil_edit_box.checkBox.setCheckState(0)
        if self.should_consider_p0:
            self.sc_soil_edit_box.checkBox_2.setCheckState(2)
        else:
            self.sc_soil_edit_box.checkBox_2.setCheckState(0)
        if self.unlimited_distribution:
            self.sc_soil_edit_box.checkBox_3.setCheckState(2)
        else:
            self.sc_soil_edit_box.checkBox_3.setCheckState(0)

        # calculate and display soil layers
        self.calculate_soil_clusters()

        # connect signals
        self.connect_signals_to_slots()

        # event filter for copying table content
        #self.sc_soil_edit_box.tableWidget.installEventFilter(sc_soil_box)

        # store updated parameter when dialog box is closed
        self.sc_soil_edit_box.pushButton.clicked.connect(sc_soil_box.close)

        sc_soil_box.exec_()
    
    
    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.sc_soil_edit_box.lineEdit_5.setStyleSheet("background-color: rgb(242, 255, 116);\n") # depth below columns toe
        self.sc_soil_edit_box.lineEdit_5.editingFinished.connect(lambda : self.update_limit_depth(float(self.sc_soil_edit_box.lineEdit_5.text())))
        self.sc_soil_edit_box.lineEdit_4.setStyleSheet("background-color: rgb(242, 255, 116);\n") # thickness of sub soillayer
        self.sc_soil_edit_box.lineEdit_4.editingFinished.connect(lambda : self.update_thickness_sublayer(float(self.sc_soil_edit_box.lineEdit_4.text())))
        self.sc_soil_edit_box.lineEdit_3.setStyleSheet("background-color: rgb(242, 255, 116);\n") # bottom of stone columns
        self.sc_soil_edit_box.lineEdit_3.editingFinished.connect(lambda : self.update_columns_bottom(float(self.sc_soil_edit_box.lineEdit_3.text())))
        self.sc_soil_edit_box.lineEdit_2.setStyleSheet("background-color: rgb(242, 255, 116);\n") # top of stone columns
        self.sc_soil_edit_box.lineEdit_2.editingFinished.connect(lambda : self.update_columns_top(float(self.sc_soil_edit_box.lineEdit_2.text())))
        self.sc_soil_edit_box.lineEdit.setStyleSheet("background-color: rgb(242, 255, 116);\n") # surcharge
        self.sc_soil_edit_box.lineEdit.editingFinished.connect(lambda : self.update_surcharge(float(self.sc_soil_edit_box.lineEdit.text())))
        self.sc_soil_edit_box.comboBox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        self.sc_soil_edit_box.comboBox.currentTextChanged.connect(lambda text: self.plot_factor_values(text, index=0))
        self.sc_soil_edit_box.comboBox_2.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        self.sc_soil_edit_box.comboBox_2.currentTextChanged.connect(lambda text: self.plot_factor_values(text, index=1))
        self.sc_soil_edit_box.comboBox_3.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        self.sc_soil_edit_box.comboBox_3.currentTextChanged.connect(lambda text: self.plot_factor_values(text, index=2))
        self.sc_soil_edit_box.tableWidget.cellChanged.connect(lambda row, col: self.update_columns_diameter(row, col))
        self.sc_soil_edit_box.tableWidget.cellChanged.connect(lambda row, col: self.update_user_E_s(row, col))
        self.sc_soil_edit_box.checkBox.stateChanged.connect(lambda state_int: self.update_user_input_E_s(state_int==2))
        self.sc_soil_edit_box.checkBox_2.stateChanged.connect(lambda state_int: self.update_should_consider_p0(state_int==2))
        self.sc_soil_edit_box.checkBox_3.stateChanged.connect(lambda state_int: self.update_unlimited_distribution(state_int==2))
        self.sc_soil_edit_box.pushButton_2.clicked.connect(self.print_report)


    def update_user_input_E_s(self, user_input=False):
        """ Updates on using user constrained modulus or not
        """
        self.user_input_E_s = user_input
        self.calculate_soil_clusters()


    def update_should_consider_p0(self, should_consider_p0=False):
        """ Updates on using user constrained modulus or not
        """
        self.should_consider_p0 = should_consider_p0
        self.calculate_soil_clusters()


    def update_unlimited_distribution(self, unlimited_distribution=False):
        """ Updates on using user constrained modulus or not
        """
        self.unlimited_distribution = unlimited_distribution
        self.calculate_soil_clusters()


    def update_columns_bottom(self, columns_depth):
        """ Updates bottom of stone columns
        columns_depth: depth of columns
        """
        try:
            self.columns_bottom = self.columns_top - columns_depth
            self.columns_depth = columns_depth
            self.calculate_soil_clusters()

        except ValueError:
            pass


    def update_columns_top(self, columns_top):
        """ Updates bottom of stone columns
        columns_top: top of columns
        """
        try:
            self.columns_top = columns_top
            self.columns_bottom = self.columns_top - self.columns_depth
            self.calculate_soil_clusters()

        except ValueError:
            pass


    def update_columns_diameter(self, row, column):
        """ Updates diameter of stone columns (is meant for soil layer dependence)
        D: diameter of stone columns
        """
        #print(row, column)
        if column == 1:
            try:
                D = float(self.sc_soil_edit_box.tableWidget.item(row, column).text())
                soilmaterial = self.sc_soil_edit_box.tableWidget.item(row, column-1).text()
                for layerpolygon in self.Layer_polygons:
                    if soilmaterial==layerpolygon['soilmaterial_layer']:
                        layerpolygon['D_stone_columns'] = D
                        #print(soilmaterial, D)
                        break

                # recalculate soil improvement factors
                self.calculate_soil_clusters()

            except ValueError:
                pass


    def update_user_E_s(self, row, column):
        """ Updates user input value for soil's constrained modulus
        """
        if self.user_input_E_s:
            if column == 2:
                try:
                    E_s_user = float(self.sc_soil_edit_box.tableWidget.item(row, column).text())
                    soilmaterial = self.sc_soil_edit_box.tableWidget.item(row, column-2).text()
                    for layerpolygon in self.Layer_polygons:
                        if soilmaterial==layerpolygon['soilmaterial_layer']:
                            layerpolygon['E_s_user'] = E_s_user
                            break

                    # recalculate soil improvement factors
                    self.calculate_soil_clusters()

                except ValueError:
                    pass


    def update_surcharge(self, p0):
        """ Updates surcharge
        p0: surcharge
        """
        try:
            self.p0 = p0
            self.calculate_soil_clusters()

        except ValueError:
            pass


    def update_thickness_sublayer(self, thickness_sublayer):
        """ Updates sublayer thickness
        """
        try:
            # store thickness of the sublayer
            self.thickness_sublayer = thickness_sublayer
            self.calculate_soil_clusters()

        except ValueError:
            pass


    def update_limit_depth(self, limit_depth):
        """ Updates depth below column toe
        """
        try:
            self.limit_depth = limit_depth
            self.calculate_soil_clusters()

            # stress ratio (sigma_p' - sigma_v') / (sigma_p' + sigma_v') 

        except ValueError:
            pass



    def calculate_soil_clusters(self):
        """ Calculates and displays soil clusters on table
        """
        # clear old data
        self.sub_soillayers.clear()
        self.sc_soil_edit_box.tableWidget.blockSignals(True)
        self.sc_soil_edit_box.tableWidget.clearContents()
        self.sc_soil_edit_box.tableWidget.clear()
        # reset spans
        for row_i in range(self.sc_soil_edit_box.tableWidget.rowCount()):
            for col_i in range(self.sc_soil_edit_box.tableWidget.columnCount()):
                self.sc_soil_edit_box.tableWidget.setSpan(row_i, col_i, 1, 1)

        column_labels = ['Soil layer', 'D [m]', 'E_s_user [kN/m^2]', 'nu_s_user [-]', 'Sublayer ID', 'Top [mNN]', 'Bottom [mNN]', 'gammaSat\n[kN/m^3]', "sigma_v'\n[kN/m^2]", 
                        've [-]', 'we [-]', 'E_s\n[kN/m^2]', 'nu_s [-]', 'E_c\n[kN/m^2]', 'n0 [-]', 'Ec/Es [-]', '(Ac/A)_bar [-]', '(Ac/A)_1 [-]', 'n1 [-]', "sigma_p' [kN/m^2]",
                        'p_c/p_s [-]', 'fd [-]', 'n2 [-]', 'm [-]', 'phi_s [deg]', 'phi_bar [deg]', 'c_s [kN/m^2]', 'c_bar [kN/m^2]', 'u_unimproved [mm]', 'u_improved [mm]', 'u_unimproved cummulative [mm]', 'u_improved cummulative [mm]']
        self.sc_soil_edit_box.tableWidget.setColumnCount(len(column_labels))
        self.sc_soil_edit_box.tableWidget.setRowCount(100)
        self.sc_soil_edit_box.tableWidget.setHorizontalHeaderLabels(column_labels)

        #sigma_v = self.p0    # effective vertical stress
        sigma_v = 0 # vertical effective stress caused by soil overburden alone (surcharge not considered)
        layer_i_start_row = 0
        id_number = 1
        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            #print(layer_i, soilmaterial_layer)
            if layer_i==0:  # adjust top as top of columns
                layer_i_top = min(self.borehole['Top'][layer_i], self.columns_top)
            else:
                layer_i_top = self.borehole['Top'][layer_i]
            layer_i_bottom = self.borehole['Bottom'][layer_i]
            layer_i_nspan = int(max(1, int((layer_i_top - layer_i_bottom)//self.thickness_sublayer)))   # at least 1 sublayer exists in 1 soil layer

            #if (layer_i_top > self.columns_bottom) and (layer_i_bottom < self.columns_bottom):
            #    layer_i_nspan += 1

            if layer_i_nspan > 1:
                self.sc_soil_edit_box.tableWidget.setSpan(layer_i_start_row, 0, layer_i_nspan, 1)
            self.sc_soil_edit_box.tableWidget.setItem(layer_i_start_row, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # soilmaterial name
            self.sc_soil_edit_box.tableWidget.item(layer_i_start_row, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color

            if 'D_stone_columns' in layerpolygon:
                D = layerpolygon['D_stone_columns']
            else:   # set default stone columns diameter
                D = self.stone_columns.params['D']  # stone columns diameter, subject to user adaptation (depending on soil compressibility)
                layerpolygon['D_stone_columns'] = D # store stone columns diameter in Layer_polygons

            if layer_i_nspan > 1:
                self.sc_soil_edit_box.tableWidget.setSpan(layer_i_start_row, 1, layer_i_nspan, 1)   # layer dependent stone columns diameter
            self.sc_soil_edit_box.tableWidget.setItem(layer_i_start_row, 1, QtWidgets.QTableWidgetItem(str(D))) # show default diameter
            self.sc_soil_edit_box.tableWidget.item(layer_i_start_row, 1).setBackground(QColor(242, 255, 116)) # light yellow

            # constrained modulus
            if self.user_input_E_s:
                if 'E_s_user' not in layerpolygon:
                    layerpolygon['E_s_user'] = 2000.0
                if 'nu_s_user' not in layerpolygon:
                    layerpolygon['nu_s_user'] = 0.33
                if layer_i_nspan > 1:
                    self.sc_soil_edit_box.tableWidget.setSpan(layer_i_start_row, 2, layer_i_nspan, 1)   # layer dependent stone columns diameter
                    self.sc_soil_edit_box.tableWidget.setSpan(layer_i_start_row, 3, layer_i_nspan, 1)   # layer dependent stone columns diameter
                self.sc_soil_edit_box.tableWidget.setItem(layer_i_start_row, 2, QtWidgets.QTableWidgetItem('{0:.3f}'.format(layerpolygon['E_s_user'])))
                self.sc_soil_edit_box.tableWidget.item(layer_i_start_row, 2).setBackground(QColor(242, 255, 116)) # light yellow
                self.sc_soil_edit_box.tableWidget.setItem(layer_i_start_row, 3, QtWidgets.QTableWidgetItem('{0:.3f}'.format(layerpolygon['nu_s_user'])))
                self.sc_soil_edit_box.tableWidget.item(layer_i_start_row, 3).setBackground(QColor(242, 255, 116)) # light yellow

            # calculate and store sub-soil layer parameters 
            if self.user_input_E_s:
                if layer_i_top > self.columns_bottom:
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_bottom)
                    if layer_i_bottom < self.columns_bottom: # no improvement for rest of the layer_i
                        #sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, layer_i_bottom, without_improvement=True)
                        sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
                        layer_i_start_row -= 1
                else:   # below stone columns
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
            else:
                if layer_i_bottom > self.columns_bottom:
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_bottom)
                    if layer_i_bottom < self.columns_bottom: # no improvement for rest of the layer_i
                        #sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, layer_i_bottom, without_improvement=True)
                        sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
                        layer_i_start_row -= 1
                else: # below stone columns
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)

        # get cummulative settlements
        self.get_cummulative_settlements()

        # report stress ratio at limit depth
        stress_ratio = self.get_stress_ratio()
        print("Stress ratio at limit depth (sigma_p' - sigma_v') / (sigma_p' + sigma_v') = {0:.2f}".format(stress_ratio))

        # display data of the sub soil layers on table
        self.display_soil_clusters()
        self.sc_soil_edit_box.tableWidget.blockSignals(False)


    def calculate_soil_clusters__(self):
        """ Calculates soil clusters
        """
        # clear old data
        self.sub_soillayers.clear()

        #sigma_v = self.p0       # effective vertical stress
        sigma_v = 0 # vertical effective stress caused by soil overburden alone (surcharge not considered)
        layer_i_start_row = 0
        id_number = 1
        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            #print(layer_i, soilmaterial_layer)
            if layer_i==0:  # adjust top as top of columns
                layer_i_top = min(self.borehole['Top'][layer_i], self.columns_top)
            else:
                layer_i_top = self.borehole['Top'][layer_i]
            layer_i_bottom = self.borehole['Bottom'][layer_i]
            layer_i_nspan = int(max(1, int((layer_i_top - layer_i_bottom)//self.thickness_sublayer)))   # at least 1 sublayer exists in 1 soil layer

            #if (layer_i_top > self.columns_bottom) and (layer_i_bottom < self.columns_bottom):
            #    layer_i_nspan += 1

            # calculate and store sub-soil layer parameters 
            if self.user_input_E_s:
                if layer_i_top > self.columns_bottom:
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_bottom)
                    if layer_i_bottom < self.columns_bottom: # no improvement for rest of the layer_i
                        #sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, layer_i_bottom, without_improvement=True)
                        sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
                        layer_i_start_row -= 1
                else:   # below stone columns
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters_user_E_s(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
            else:
                if layer_i_bottom > self.columns_bottom:
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_bottom)
                    if layer_i_bottom < self.columns_bottom: # no improvement for rest of the layer_i
                        #sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, layer_i_bottom, without_improvement=True)
                        sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(self.sub_soillayers[-1]['bottom'], layer_i_bottom, 1, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)
                        layer_i_start_row -= 1
                else: # below stone columns
                    sigma_v, layer_i_start_row, id_number = self.calculate_sub_soillayer_parameters(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, self.columns_top-self.limit_depth, without_improvement=True)

        # get cummulative settlements
        self.get_cummulative_settlements()


    def calculate_sub_soillayer_parameters(self, layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, bottom, without_improvement=False):
        """ Calculates and store sub-soil layer parameters 
        bottom is toe level of columns. If additional depth below columns toe is considered, this additional depth is taken into account for bottom.
        Stiffnesses for soil and column depend on vertical effective stress (depth dependent stiffnesses)
        """
        sublayer_i_start = layer_i_top
        for i in range(layer_i_nspan):
            if sublayer_i_start <= bottom: # start of sub layer is below columns bottom
                break
            elif sublayer_i_start >= self.columns_top: # start of the sub soillayers must be from the columns top level
                sublayer_i_start = self.columns_top
            #else:
            # stone columns parameters
            Ka = self.stone_columns.get_Ka()
            Ko = self.stone_columns.get_Ko()
            D = layerpolygon['D_stone_columns']             # stone columns diameter D can be adapted by user input
            Ac_over_A = self.stone_columns.get_Ac_over_A_with_D(D) # Ac_over_A follows user adapted D
            ve_c = self.stone_columns.params['ve']
            we_c = self.stone_columns.params['we']
            phi_c = self.stone_columns.params['phi_c']

            sub_soillayer = OrderedDict()
            #sub_soillayer['id'] = str(id_number).zfill(6)
            sub_soillayer['id'] = self.sc_name + str(id_number).zfill(3)
            sub_soillayer['color'] = layerpolygon['color']
            sub_soillayer['soilmaterial_layer'] = soilmaterial_layer
            #sub_soillayer['D'] = D
            sub_soillayer['top'] = sublayer_i_start
            thickness_layer = self.borehole['Top'][layer_i] - self.borehole['Bottom'][layer_i]
            if self.thickness_sublayer > thickness_layer:
                thickness_sublayer_i = thickness_layer
                layer_i_nspan = 1
            elif i == (layer_i_nspan - 1): # last sub soil layer
                thickness_sublayer_i = sub_soillayer['top'] - max(layer_i_bottom, bottom)
            else:   # thickness of sublayer is larger than thickness of the soil layer
                thickness_sublayer_i = self.thickness_sublayer

            # adjust bottom of the last soil layer (columns end)
            if layer_i_nspan > 1:
                if (sub_soillayer['top'] - 2*self.thickness_sublayer) < bottom:
                    thickness_sublayer_i =  sub_soillayer['top'] - bottom
            else:
                if sub_soillayer['top'] - thickness_sublayer_i < bottom:
                    thickness_sublayer_i = sub_soillayer['top'] - bottom

            sub_soillayer['bottom'] = sublayer_i_start - thickness_sublayer_i
            sub_soillayer['gammaSat'] = read_data_in_json_item(soilmaterial_layer, 'gammaSat')
            #sub_soillayer['EoedRef'] = read_data_in_json_item(soilmaterial_layer, 'EoedRef')
            #sub_layer_i_depth = self.borehole['Top'][0] - sub_soillayer['top'] + 0.5*thickness_sublayer_i

            # depth-dependent soil stiffness
            sub_layer_i_level = sub_soillayer['top'] - 0.5*thickness_sublayer_i
            if sub_layer_i_level <= self.borehole['Head']: # under water (under bouyancy)
                sigma_v += (sub_soillayer['gammaSat'] - 10.0) * thickness_sublayer_i
            else:   # dried soil
                sigma_v += sub_soillayer['gammaSat'] * thickness_sublayer_i
            sub_soillayer["sigma_v'"] = sigma_v
            sub_soillayer['ve'] = read_data_in_json_item(soilmaterial_layer, 've')
            sub_soillayer['we'] = read_data_in_json_item(soilmaterial_layer, 'we')
            sub_soillayer['E_s'] = sub_soillayer['ve']*100*(sigma_v/100)**sub_soillayer['we']
            sub_soillayer['nu_s'] = read_data_in_json_item(soilmaterial_layer, 'nu')
            # depth-dependent stiffness for columns
            sub_soillayer['E_c'] = ve_c*100*(sigma_v/100)**we_c

            # basic improvement factor n0
            n0 = self.calc_n0_priebe(sub_soillayer['nu_s'], Ac_over_A, Ka)
            sub_soillayer['n0'] = n0
            # reduced improvement factor n1
            Ec_over_Es = sub_soillayer['E_c']/sub_soillayer['E_s']
            Ac_over_A_1 = self.calc_Ac_over_A_1_priebe(Ec_over_Es, Ka)
            delta_Ac_over_A = 1.0/Ac_over_A_1 - 1
            Ac_over_A_bar = 1.0/(1/Ac_over_A + delta_Ac_over_A)
            sub_soillayer["E_c/E_s"] = Ec_over_Es
            sub_soillayer["(Ac/A)_bar"] = Ac_over_A_bar
            sub_soillayer["(Ac/A)_1"] = Ac_over_A_1
            #sub_soillayer["(Ac/A)_bar"] = Ac_over_A_bar
            n1 = self.calc_n0_priebe(sub_soillayer['nu_s'], Ac_over_A_bar, Ka)
            sub_soillayer['n1'] = n1

            # stress distribution due to surcharge
            r = self.columns_right - self.columns_left    # radius of tank
            z = sub_soillayer['bottom'] - self.columns_top
            if self.unlimited_distribution:
                sigma_p = self.p0
            else:
                sigma_p = self.calc_stress_due_to_surcharge(self.p0, r, z)
            sub_soillayer["sigma_p'"] = sigma_p
            # improved factor n2 due to surcharge
            pc_over_ps = self.calc_pc_over_ps_priebe(sub_soillayer['nu_s'], Ac_over_A_bar, Ka)
            sub_soillayer['pc/ps'] = pc_over_ps
            #n2, fd = self.calc_n2_priebe(n1, self.p0, Ec_over_Es, sigma_v, pc_over_ps, Ac_over_A, Ac_over_A_bar, Ko)
            n2, fd = self.calc_n2_priebe(n1, Ec_over_Es, sigma_v, sigma_p, pc_over_ps, Ac_over_A, Ac_over_A_bar, Ko)
            sub_soillayer['fd'] = fd
            sub_soillayer['n2'] = n2
            sub_soillayer['m'] = (n2 - 1 + Ac_over_A_bar)/n2    # m for getting improved friction angle
            sub_soillayer['phi_s'] = read_data_in_json_item(soilmaterial_layer, 'phi')
            sub_soillayer['phi_bar'] = self.calc_phi_bar_priebe(sub_soillayer['m'], phi_c, sub_soillayer['phi_s'])
            sub_soillayer['c_s'] = read_data_in_json_item(soilmaterial_layer, 'Cref')
            sub_soillayer['c_bar'] = (1 - Ac_over_A_bar)*sub_soillayer['c_s']

            # no improvement for sub soillayers below columns toe
            if without_improvement:
                sub_soillayer['n0'] = sub_soillayer['n1'] = sub_soillayer['n2'] = 1.0
                sub_soillayer['phi_bar'] = sub_soillayer['phi_s']
                sub_soillayer['c_bar'] = sub_soillayer['c_s']

            # calculate settlement
            sub_soillayer['u_unimproved'] = self.calc_settlement(sub_soillayer["sigma_p'"], sub_soillayer['E_s'], thickness_sublayer_i)
            sub_soillayer['u_improved'] = self.calc_settlement(sub_soillayer["sigma_p'"], sub_soillayer['n2']*sub_soillayer['E_s'], thickness_sublayer_i)

            sublayer_i_start -= thickness_sublayer_i  # update top of the sublayer
            self.sub_soillayers.append(sub_soillayer)
            id_number += 1

        layer_i_start_row += layer_i_nspan

        return (sigma_v, layer_i_start_row, id_number)


    def calculate_sub_soillayer_parameters_user_E_s(self, layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layer_i, layerpolygon, soilmaterial_layer, sigma_v, bottom, without_improvement=False):
        """ Calculates and store sub-soil layer parameters using fixed user input constrained modulus for soils and columns
        bottom is toe level of columns. If additional depth below columns toe is considered, this additional depth is taken into account for bottom.
        """
        sublayer_i_start = layer_i_top
        for i in range(layer_i_nspan):
            if sublayer_i_start <= bottom: # start of sub layer is below columns bottom
                break
            elif sublayer_i_start >= self.columns_top: # start of the sub soillayers must be from the columns top level
                sublayer_i_start = self.columns_top
            #else:
            # stone columns parameters
            Ka = self.stone_columns.get_Ka()
            Ko = self.stone_columns.get_Ko()
            D = layerpolygon['D_stone_columns']             # stone columns diameter D can be adapted by user input
            Ac_over_A = self.stone_columns.get_Ac_over_A_with_D(D) # Ac_over_A follows user adapted D
            phi_c = self.stone_columns.params['phi_c']

            sub_soillayer = OrderedDict()
            #sub_soillayer['id'] = str(id_number).zfill(6)
            sub_soillayer['id'] = self.sc_name + str(id_number).zfill(3)
            sub_soillayer['color'] = layerpolygon['color']
            sub_soillayer['soilmaterial_layer'] = soilmaterial_layer
            sub_soillayer['top'] = sublayer_i_start
            thickness_layer = self.borehole['Top'][layer_i] - self.borehole['Bottom'][layer_i]
            if self.thickness_sublayer > thickness_layer:
                thickness_sublayer_i = thickness_layer
                layer_i_nspan = 1
            elif i == (layer_i_nspan - 1): # last sub soil layer
                thickness_sublayer_i = sub_soillayer['top'] - max(layer_i_bottom, bottom)
            else:   # thickness of sublayer is larger than thickness of the soil layer
                thickness_sublayer_i = self.thickness_sublayer

            # adjust bottom of the last soil layer (columns end)
            if layer_i_nspan > 1:
                if (sub_soillayer['top'] - 2*self.thickness_sublayer) < bottom:
                    thickness_sublayer_i =  sub_soillayer['top'] - bottom
            else:
                if sub_soillayer['top'] - thickness_sublayer_i < bottom:
                    thickness_sublayer_i = sub_soillayer['top'] - bottom

            sub_soillayer['bottom'] = sublayer_i_start - thickness_sublayer_i
            sub_soillayer['gammaSat'] = read_data_in_json_item(soilmaterial_layer, 'gammaSat')
            #sub_soillayer['gammaSat'] = np.nan
            sub_layer_i_level = sub_soillayer['top'] - 0.5*thickness_sublayer_i
            if sub_layer_i_level <= self.borehole['Head']: # under water (under bouyancy)
                sigma_v += (sub_soillayer['gammaSat'] - 10.0) * thickness_sublayer_i
            else:   # dried soil
                sigma_v += sub_soillayer['gammaSat'] * thickness_sublayer_i
            sub_soillayer["sigma_v'"] = sigma_v
            sub_soillayer['ve'] = np.nan
            sub_soillayer['we'] = np.nan
            #sub_soillayer['E_s'] = sub_soillayer['ve']*100*(sigma_v/100)**sub_soillayer['we']
            sub_soillayer['E_s'] = layerpolygon['E_s_user']
            #sub_soillayer['nu_s'] = read_data_in_json_item(soilmaterial_layer, 'nu')
            sub_soillayer['nu_s'] = layerpolygon['nu_s_user']
            sub_soillayer['E_c'] = self.stone_columns.params['E_c'] # fixed value

            # basic improvement factor n0
            n0 = self.calc_n0_priebe(sub_soillayer['nu_s'], Ac_over_A, Ka)
            sub_soillayer['n0'] = n0
            # reduced improvement factor n1
            Ec_over_Es = sub_soillayer['E_c']/sub_soillayer['E_s']
            Ac_over_A_1 = self.calc_Ac_over_A_1_priebe(Ec_over_Es, Ka)
            delta_Ac_over_A = 1.0/Ac_over_A_1 - 1
            Ac_over_A_bar = 1.0/(1/Ac_over_A + delta_Ac_over_A)
            sub_soillayer["E_c/E_s"] = Ec_over_Es
            sub_soillayer["(Ac/A)_bar"] = Ac_over_A_bar
            sub_soillayer["(Ac/A)_1"] = Ac_over_A_1
            #sub_soillayer["(Ac/A)_bar"] = Ac_over_A_bar
            n1 = self.calc_n0_priebe(sub_soillayer['nu_s'], Ac_over_A_bar, Ka)
            sub_soillayer['n1'] = n1

            # stress distribution due to surcharge
            r = self.columns_right - self.columns_left    # radius of tank
            z = sub_soillayer['bottom'] - self.columns_top
            if self.unlimited_distribution:
                sigma_p = self.p0
            else:
                sigma_p = self.calc_stress_due_to_surcharge(self.p0, r, z)
            sub_soillayer["sigma_p'"] = sigma_p
            # improved factor n2 due to surcharge
            pc_over_ps = self.calc_pc_over_ps_priebe(sub_soillayer['nu_s'], Ac_over_A_bar, Ka)
            sub_soillayer['pc/ps'] = pc_over_ps
            #n2, fd = self.calc_n2_priebe(n1, self.p0, Ec_over_Es, sigma_v, pc_over_ps, Ac_over_A, Ac_over_A_bar, Ko)
            n2, fd = self.calc_n2_priebe(n1, Ec_over_Es, sigma_v, sigma_p, pc_over_ps, Ac_over_A, Ac_over_A_bar, Ko)
            sub_soillayer['fd'] = fd
            sub_soillayer['n2'] = n2
            sub_soillayer['m'] = (n2 - 1 + Ac_over_A_bar)/n2    # m for getting improved friction angle
            sub_soillayer['phi_s'] = read_data_in_json_item(soilmaterial_layer, 'phi')
            sub_soillayer['phi_bar'] = self.calc_phi_bar_priebe(sub_soillayer['m'], phi_c, sub_soillayer['phi_s'])
            sub_soillayer['c_s'] = read_data_in_json_item(soilmaterial_layer, 'Cref')
            sub_soillayer['c_bar'] = (1 - Ac_over_A_bar)*sub_soillayer['c_s']

            # no improvement for sub soillayers below columns toe
            if without_improvement:
                sub_soillayer['n0'] = sub_soillayer['n1'] = sub_soillayer['n2'] = 1.0
                sub_soillayer['phi_bar'] = sub_soillayer['phi_s']
                sub_soillayer['c_bar'] = sub_soillayer['c_s']

            # calculate settlement
            sub_soillayer['u_unimproved'] = self.calc_settlement(sub_soillayer["sigma_p'"], sub_soillayer['E_s'], thickness_sublayer_i)
            sub_soillayer['u_improved'] = self.calc_settlement(sub_soillayer["sigma_p'"], sub_soillayer['n2']*sub_soillayer['E_s'], thickness_sublayer_i)

            sublayer_i_start -= thickness_sublayer_i  # update top of the sublayer
            self.sub_soillayers.append(sub_soillayer)
            id_number += 1

        layer_i_start_row += layer_i_nspan

        return (sigma_v, layer_i_start_row, id_number)


    def get_cummulative_settlements(self):
        """ Gets cummulative settlements
        """
        for i_sublayer, sub_soillayer in enumerate(self.sub_soillayers):
            if i_sublayer == 0:
                sub_soillayer['u_unimproved_cummulative'] = sub_soillayer['u_unimproved'] 
                sub_soillayer['u_improved_cummulative'] = sub_soillayer['u_improved'] 
            else:
                u_unimproved_sublayer = sub_soillayer['u_unimproved']
                u_improved_sublayer = sub_soillayer['u_improved']
                sub_soillayer['u_unimproved_cummulative'] = self.sub_soillayers[i_sublayer-1]['u_unimproved_cummulative'] + u_unimproved_sublayer
                sub_soillayer['u_improved_cummulative'] = self.sub_soillayers[i_sublayer-1]['u_improved_cummulative'] + u_improved_sublayer


    def get_stress_ratio(self):
        """ Get (sigma_p' - sigma_v') / (sigma_p' + sigma_v') at the last sub soilayer
        """
        sub_soillayer = self.sub_soillayers[-1] # the last subsoil layer, which is at limit depth
        sigma_p = sub_soillayer["sigma_p'"]
        sigma_v = sub_soillayer["sigma_v'"]
        print('sigma_p = {0:.2f} kPa'.format(sigma_p))
        print('sigma_v_prime = {0:.2f} kPa'.format(sigma_v))
        ratio = (sigma_p - sigma_v) / (sigma_p + sigma_v)
        
        return ratio


    def display_soil_clusters(self):
        """ Displays soil clusters on table
        """
        self.sc_soil_edit_box.tableWidget.blockSignals(True)
        self.sc_soil_edit_box.tableWidget.setRowCount(len(self.sub_soillayers)) # fit number of rows to data size
        #self.sc_soil_edit_box.tableWidget.setColumnCount(len(self.sub_soillayers[0].keys()))
        #self.sc_soil_edit_box.tableWidget.setHorizontalHeaderLabels(self.sub_soillayers[0].keys())
        for sublayer_i, sub_soillayer in enumerate(self.sub_soillayers):
            self.sc_soil_edit_box.tableWidget.setItem(sublayer_i, 4, QtWidgets.QTableWidgetItem(sub_soillayer['id']))
            keys = list(sub_soillayer.keys())
            for j, key in enumerate(keys[3:]): # from sublayer_id onward
                self.sc_soil_edit_box.tableWidget.setItem(sublayer_i, j+5, QtWidgets.QTableWidgetItem('{:.3f}'.format(sub_soillayer[key])))
            
                if sub_soillayer['bottom'] >= self.columns_bottom:
                    self.sc_soil_edit_box.tableWidget.item(sublayer_i, j+5).setBackground(QColor(147, 147, 147)) 

        # list keys in combo boxes for plotting option
        combo_boxes = [self.sc_soil_edit_box.comboBox, self.sc_soil_edit_box.comboBox_2, self.sc_soil_edit_box.comboBox_3]
        for i, combo_box in enumerate(combo_boxes):
            combo_box.blockSignals(True)
            combo_box.clear()
            combo_box.addItems(self.sub_soillayers[0].keys())
            if i==0:
                combo_box.setCurrentIndex(6)    # sigma_v'
            elif i==1:
                combo_box.setCurrentIndex(20)   # n2
            elif i==2:
                combo_box.setCurrentIndex(29)   # improved soil settlement
            combo_box.blockSignals(False)
            # plot factor
            self.plot_factor_values(combo_box.currentText(), index=i)

        self.sc_soil_edit_box.tableWidget.blockSignals(False)
    

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
            event.matches(QKeySequence.Copy)):
            self.copySelection(self.sc_soil_edit_box.tableWidget)
            return True
        return super(StoneColumnsSoilClusters, self).eventFilter(source, event)


    def copySelection(self, tableWidget):
        selection = tableWidget.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            QtWidgets.qApp.clipboard().setText(stream.getvalue())


    def plot_factor_values(self, key, index=0):
        """ Plot factor values indexed by key
        """
        try:
            level = [sub_soillayer['bottom'] for sub_soillayer in self.sub_soillayers]
            value = [sub_soillayer[key] for sub_soillayer in self.sub_soillayers]
            if key != 'soilmaterial_layer':
                self.plot_canvas.plot_improved_soil_factor(level, value, key, index=index)

        except:
            pass


    def calc_n0_priebe(self, nu_s, Ac_over_A, Ka):
        """ Calculates n0 after Priebe
        """
        f = self.calc_f_nu_s_Ac_over_A_priebe(nu_s, Ac_over_A)
        a = (0.5 +  f)/(Ka *  f)
        n0 = 1.0 + Ac_over_A*(a - 1.0)
        
        return n0


    def calc_f_nu_s_Ac_over_A_priebe(self, nu_s, Ac_over_A):
        """ Calculates f(nu_s, Ac/A) after Priebe
        """
        f_numerator = (1 - nu_s) * (1 - Ac_over_A)
        f_denominator = 1 - 2*nu_s + Ac_over_A

        return f_numerator/f_denominator

    
    def calc_Ac_over_A_1_priebe(self, n0, Ka):
        """ Calculates (Ac/A)_1 after Priebe
        """
        a = -(4*Ka*(n0-2) + 5)/(8*Ka - 2)
        b = 0.5*np.sqrt(((4*Ka*(n0-2) + 5)/(4*Ka - 1))**2 + 16*Ka*(n0-1)/(4*Ka - 1))
        if (a - b) < 0:
            return a + b
        else:
            return min(a + b, a - b)


    def calc_pc_over_ps_priebe(self, nu_s, Ac_over_A_bar, Ka):
        """ Calculates pc/ps after Priebe
        """
        f = self.calc_f_nu_s_Ac_over_A_priebe(nu_s, Ac_over_A_bar)
        return (0.5 + f)/(Ka*f)

    
    def calc_n2_priebe(self, n1, Ec_over_Es, sigma_v, sigma_p, pc_over_ps, Ac_over_A, Ac_over_A_bar, Ko):
        """ Calculates n2 after Priebe
        Input
            n1: reduced improvement factor due to column compressibility
            p0: surcharge [kN/m**2]
            Ec_over_Es: ratio b/w columns' constrained modulus and soil's constrained modulus
            sigma_v: vertical effective stress due to overburden
            sigma_p: vertical effective stress due to surcharge
            pc_over_ps: ratio b/w pressure on column and pressure on soil
            Ac_over_A: ratio b/w column area and total unit cell's area
            Ac_over_A_bar: modified area ratio due to column comprssibility
            Ko: coefficient of earth pressure at rest
        Output
            n2: improvement factor due to overburden
            fd: depth factor
        """
        n_max = 1.0 + Ac_over_A * (Ec_over_Es - 1.0)
        #n2_1 = n1 * max(1, Ec_over_Es/pc_over_ps)
        p0_eps = 1.0e-10 # avoid dividing by zero when p0 is zero
        pc = (sigma_p + p0_eps)/(Ac_over_A_bar + (1-Ac_over_A_bar)/pc_over_ps)
        fd = 1/(1 + (Ko - 1)/Ko * sigma_v / pc)    # p0 not considered
        if self.should_consider_p0:
            fd = 1/(1 + (Ko - 1)/Ko * (sigma_v + sigma_p*0.5) / pc)

        if fd > Ec_over_Es/pc_over_ps:
            fd = np.nan
            n2 = n1
        else:
            n2 = n1 * fd

        n2 = min(n_max, n2)

        return n2, fd


    def calc_phi_bar_priebe(self, m, phi_c, phi_s):
        """ Calculates friction angle of the improved soil
        """
        tan_phi_bar = m*np.tan(phi_c*np.pi/180) + (1-m)*np.tan(phi_s*np.pi/180)
        return np.arctan(tan_phi_bar)*180/np.pi


    def calc_stress_due_to_surcharge(self, p0, r, z):
        """ Calculates stress due to surchare
        This is stress distribution along depth
        p0: surcharge
        r: radius of the circular surface load
        z: depth
        """
        sigma = p0 * (1.0 - (1.0/(1 + (r/z)**2))**1.5)

        return sigma

    
    def calc_settlement(self, p0, E_s, delta_d):
        """ Calculates settlement of a unit cell soil column under surcharge
        p0: surcharge
        E_s: constrained modulus of soil
        delta_d: the considered thickness
        """
        u = delta_d*p0/E_s

        return u*1000   #mm


    def print_report(self):
        """ Prints report
        """
        try:
            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        except KeyError: # no project folder exists
            MONIMAN_OUTPUTS = '.'
        
        report_pages = []

        report_page1 = Report()
        report_page1.add_project_info_stone_columns(self.project_title)
        Ka = self.stone_columns.get_Ka()
        Ko = self.stone_columns.get_Ko()
        Ac_over_A = self.stone_columns.get_Ac_over_A()
        report_page1.add_table_stone_column_properties(self.stone_columns.params, [Ka, Ko, Ac_over_A])
        report_page1.plot_stone_columns_cross_section(self.stone_columns.params)
        report_page1.add_stone_columns_settings(self.columns_top, self.columns_bottom, self.limit_depth, self.borehole['Head'], self.p0)
        report_pages.append(report_page1)

        report_page2 = Report()
        report_page2.add_project_info_stone_columns(self.project_title)
        report_page2.add_table_results_stone_columns(self.sub_soillayers)
        report_pages.append(report_page2)
        
        report_page3 = Report()
        report_page3.add_project_info_stone_columns(self.project_title)
        report_page3.plot_stone_columns_improvement_results(self.sub_soillayers)
        report_pages.append(report_page3)


        try:    
            filename = os.path.join(MONIMAN_OUTPUTS, 'Design of Stone Columns ' + self.project_title + '.pdf')
            pp = PdfPages(filename)
            for report_page in report_pages:
                report_page.fig.savefig(pp, format='pdf')

            pp.close()
            # view report in Acrobat Reader
            cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
            cmd.append(filename)
            subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)
            
            return int(0)

        except PermissionError:
            return filename