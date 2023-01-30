# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 16:58:00 2023

@author: nya
"""
import math
import os
import sys
import subprocess
import glob
import json
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from gui.gui_all_dialogs_ui import Ui_Dialog
from gui.gui_widget_Dim_MIP_steel_profile import Ui_Form as DimForm
from dimensioning.walers.waler_concrete import walerConcrete
from dimensioning.struts.steel_profile import SteelProfile
from dimensioning.walers.report import Report
from matplotlib.backends.backend_pdf import PdfPages
from common.boilerplate import start_plaxis
from plxscripting.easy import new_server
from solver.plaxis2d.output_commands import get_plate_outputs_with_y_limits

from system.system import load_paths

# load PATHS.py
load_paths(r'common\\PATHS.py')
ACROBAT = sys.modules['moniman_paths']['ACROBAT']

psf_p = {'permanent': 1.35, 'transient': 1.5, 'gamma_c': 1.5, 'gamma_s': 1.15, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_t = {'permanent': 1.2, 'transient': 1.3, 'gamma_c': 1.5, 'gamma_s': 1.15, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_a = {'permanent': 1.1, 'transient': 1.1, 'gamma_c': 1.3, 'gamma_s': 1.15, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_e = {'permanent': 1.0, 'transient': 1.0, 'gamma_c': 1.3, 'gamma_s': 1.15, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
PSFs = {'BS-P: Persistent': psf_p, 'BS-T: Transient': psf_t, 'BS-A: Accidential': psf_a, 'BS-E: Seismic': psf_e}
alpha_buckling_curves = {'a0': 0.13, 'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}

class Dim_MIP_steel_profile(QtWidgets.QWidget):
    """ This class implements dimensioning tool for the steel profile and its connection to RC continous wall
    """
    def __init__(self, form, project_title, Walls, Wallmaterials, Phases, design_situation='BS-P: Persistent', 
                minmax_values_at_min_M2D=OrderedDict(), minmax_values_at_max_M2D=OrderedDict(), minmax_values_at_min_Q2D=OrderedDict(), minmax_values_at_max_Q2D=OrderedDict()):
        super(Dim_MIP_steel_profile, self).__init__()
        self.ui = DimForm()
        self.ui.setupUi(form)
        self.dialog = Ui_Dialog()
        self.project_title = project_title

        # RC wall is first inserted wall, steel profile wall is the second one
        self.Walls = Walls
        self.wall_RC = None
        self.wall_profile = None
        if len(self.Walls) > 1:
            self.wall_RC = self.Walls[0]
            self.wall_profile = self.Walls[1]

        self.Wallmaterials = Wallmaterials
        self.Phases = Phases

        self.PSFs = PSFs
        self.design_situation = design_situation
        # display design situation
        design_situations = ['BS-P: Persistent', 'BS-T: Transient', 'BS-A: Accidential', 'BS-E: Seismic']
        self.ui.comboBox.setCurrentIndex(design_situations.index(self.design_situation))

        # initialize table for PSFs
        self.initialize_table_psf()

        # cross section
        self.cross_section = None

        # initilizes tables for wall internal forces
        self.initialize_tables_wall_internal_forces()
        #self.internal_forces_max = internal_forces_max                          # characteristic loads
        self.minmax_values_at_min_M2D = minmax_values_at_min_M2D
        self.minmax_values_at_max_M2D = minmax_values_at_max_M2D
        self.minmax_values_at_min_Q2D = minmax_values_at_min_Q2D
        self.minmax_values_at_max_Q2D = minmax_values_at_max_Q2D
        self.update_tables_internal_forces()

        ### fill table steel profiile cross section
        #self.fill_table_cross_section(self.wall_profile)
        ## get cross-section class
        #self.get_cross_section_class(self.wall_profile)

        # connect signals and update basic settings once
        self.connect_signals_to_slots()

        form.exec_()


    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.comboBox.currentTextChanged.connect(self.update_design_situation)
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_with_custom_value_psf(row, column))
        self.ui.pushButton_2.clicked.connect(self.retrieve_plaxis2d_database) 
        #self.ui.tableWidget_2.cellChanged.connect(lambda row, column: self.update_max_internal_forces_user_value(row, column))
        #self.ui.tableWidget_8.cellChanged.connect(lambda row, column: self.update_internal_forces_top_RC_wall_user_value(row, column))
        #self.ui.tableWidget_3.cellChanged.connect(lambda row, column: self.respond_to_steel_profile_nos_fyk(row, column))
        ##self.ui.pushButton.clicked.connect(self.print_report) # print report


    def initialize_table_psf(self):
        """ Initialize table for partial safety factors
        """
        self.ui.tableWidget.setRowCount(1)
        column_labels = ['permanent', 'transient', 'gamma_c', 'gamma_s', 'gamma_M0', 'gamma_M1']
        self.ui.tableWidget.blockSignals(True)
        self.ui.tableWidget.setColumnCount(len(column_labels))
        self.ui.tableWidget.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget.blockSignals(False)

        # fill table 
        self.fill_table_psf()


    def fill_table_psf(self):
        """ Fills psf parameters in table
        The coded values are overloaded by custom values if any
        """
        self.ui.tableWidget.blockSignals(True)
        self.ui.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['permanent'])))
        self.ui.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['transient'])))
        self.ui.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_c'])))
        self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_s'])))
        self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_M0'])))
        self.ui.tableWidget.setItem(0, 5, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_M1'])))
        for col_i in range(6):
            self.ui.tableWidget.item(0, col_i).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.blockSignals(False)


    def update_design_situation(self, design_situation):
        """ Updates design situation
        """
        # fill in table values
        self.design_situation = design_situation
        self.fill_table_psf()
        self.update_tables_internal_forces()


    def update_with_custom_value_psf(self, row, column):
        """ Updates a custom value for psf parameter
        """
        #if int(row) == 1:
        if int(row) == 0:
            text = self.ui.tableWidget.item(row, column).text()
            if text != '':
                try:
                    #value = float(text)
                    #self.ui.tableWidget.setItem(0, column, QtWidgets.QTableWidgetItem(str(value)))
                    self.read_parameters_psf()  # read and store parameter values

                    # refresh the rest
                    self.update_tables_internal_forces()

                except ValueError:
                    self.dialog.show_message_box('Error', 'Please check if the value you entered are correct!')

            else: # text is empty, set back stored values
                self.update_design_situation(self.design_situation)


    def read_parameters_psf(self):
        """ Reads and stores parameter values from psf table
        """
        try:
            psf_items = ['permanent', 'transient', 'gamma_c', 'gamma_s', 'gamma_M0', 'gamma_M1']
            for i, psf_i in enumerate(psf_items):
                if self.ui.tableWidget.item(0, i): # is not None
                    self.PSFs[self.design_situation][psf_i] = float(self.ui.tableWidget.item(0, i).text())
        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def initialize_tables_wall_internal_forces(self):
        """ Initilizes tables for wall internal forces
        """
        self.ui.comboBox_2.addItem(self.wall_profile['json_item'])
        
        # set limit for the number of calculation phases
        self.ui.spinBox.setMinimum(1)
        self.ui.spinBox.setMaximum(len(self.Phases))
        self.ui.spinBox.setValue(1)

        # initialize tables
        vertical_labels = ['@ min_M2D', '@ max_M2D', '@ min_Q2D', '@ max_Q2D']
        horizontal_labels = ['y [mNN]', 'Nx2D [kN/m]', 'M2D [kNm/m]', 'Q2D [kN/m]']
        self.ui.tableWidget_2.setColumnCount(len(horizontal_labels))
        self.ui.tableWidget_2.setRowCount(len(vertical_labels))
        self.ui.tableWidget_2.setVerticalHeaderLabels(vertical_labels)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(horizontal_labels)


    def retrieve_plaxis2d_database(self):
        """ Reads plaxis2d database using the current settings
        """
        x_wall = self.wall_profile['point1'][0]
        phasenumber = self.ui.spinBox.value()
        should_read_envelop = self.ui.checkBox.checkState() == 2
            
        PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
        subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)

            
        s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
                    
        path = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        output_database = os.path.join(path, 'retaining_wall.p2dx')
        s_o.open(output_database)

        self.update_wall_outputs(g_o, path, x_wall, self.wall_profile, phasenumber, should_read_envelop)


    def update_wall_outputs(self, g_o, path, x_wall, wall, phasenumber, should_read_envelop=False):        
        """ Reads wall outputs and returns maximal internal forces
        """
        (phasename, y_plate, Ux_plate, Nx2D_plate, Nx2Demax_plate, Nx2Demin_plate, M2D_plate, 
         M2Demax_plate, M2Demin_plate, Q2D_plate, 
         Q2Demax_plate, Q2Demin_plate) = get_plate_outputs_with_y_limits(path, g_o, x_wall, wall, phasenumber)

        # close Plaxis2D Output
        g_o.close()

        # display phase name
        self.ui.label_4.setText(phasename)

        # gets maximal internal forces
        if should_read_envelop:
            idx_min_M2D = M2D_plate.index(min(M2Demin_plate))
            idx_max_M2D = M2D_plate.index(max(M2Demax_plate))
            idx_min_Q2D = Q2D_plate.index(min(Q2Demin_plate))
            idx_max_Q2D = Q2D_plate.index(max(Q2Demax_plate))
        else:
            idx_min_M2D = M2D_plate.index(min(M2D_plate))
            idx_max_M2D = M2D_plate.index(max(M2D_plate))
            idx_min_Q2D = Q2D_plate.index(min(Q2D_plate))
            idx_max_Q2D = Q2D_plate.index(max(Q2D_plate))

        self.minmax_values_at_min_M2D['y'] = y_plate[idx_min_M2D]
        self.minmax_values_at_min_M2D['N2D'] = Nx2D_plate[idx_min_M2D]
        self.minmax_values_at_min_M2D['M2D'] = M2D_plate[idx_min_M2D]
        self.minmax_values_at_min_M2D['Q2D'] = Q2D_plate[idx_min_M2D]

        self.minmax_values_at_max_M2D['y'] = y_plate[idx_max_M2D]
        self.minmax_values_at_max_M2D['N2D'] = Nx2D_plate[idx_max_M2D]
        self.minmax_values_at_max_M2D['M2D'] = M2D_plate[idx_max_M2D]
        self.minmax_values_at_max_M2D['Q2D'] = Q2D_plate[idx_max_M2D]

        self.minmax_values_at_min_Q2D['y'] = y_plate[idx_min_Q2D]
        self.minmax_values_at_min_Q2D['N2D'] = Nx2D_plate[idx_min_Q2D]
        self.minmax_values_at_min_Q2D['M2D'] = M2D_plate[idx_min_Q2D]
        self.minmax_values_at_min_Q2D['Q2D'] = Q2D_plate[idx_min_Q2D]

        self.minmax_values_at_max_Q2D['y'] = y_plate[idx_max_Q2D]
        self.minmax_values_at_max_Q2D['N2D'] = Nx2D_plate[idx_max_Q2D]
        self.minmax_values_at_max_Q2D['M2D'] = M2D_plate[idx_max_Q2D]
        self.minmax_values_at_max_Q2D['Q2D'] = Q2D_plate[idx_max_Q2D]
        
        # fill tables for internal forces
        self.update_tables_internal_forces()

        ## fill table steel profiile cross section
        #self.fill_table_cross_section(wall)


    def update_tables_internal_forces(self):
        """ Fills table for wall internal forces
        """
        items_to_list = ['y', 'N2D', 'M2D', 'Q2D']
        if self.minmax_values_at_max_M2D:
            for i, item in enumerate(items_to_list):
                self.ui.tableWidget_2.setItem(0, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.minmax_values_at_min_M2D[item])))
                self.ui.tableWidget_2.setItem(1, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.minmax_values_at_max_M2D[item])))
                self.ui.tableWidget_2.setItem(2, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.minmax_values_at_max_Q2D[item])))
                self.ui.tableWidget_2.setItem(3, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.minmax_values_at_min_Q2D[item])))
                if i > 0:
                    self.ui.tableWidget_2.item(0, i).setBackground(QColor(242, 255, 116))
                    self.ui.tableWidget_2.item(1, i).setBackground(QColor(242, 255, 116))
                    self.ui.tableWidget_2.item(2, i).setBackground(QColor(242, 255, 116))
                    self.ui.tableWidget_2.item(3, i).setBackground(QColor(242, 255, 116))