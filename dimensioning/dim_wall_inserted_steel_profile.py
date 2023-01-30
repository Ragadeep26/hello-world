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
from PyQt5.QtGui import QColor, QBrush, QIcon, QPixmap
from gui.gui_all_dialogs_ui import Ui_Dialog
from gui.gui_widget_Dim_wall_inserted_steel_profile import Ui_Form as DimForm
from dimensioning.walers.waler_concrete import walerConcrete
from dimensioning.struts.steel_profile import SteelProfile
from dimensioning.walers.report import Report
from matplotlib.backends.backend_pdf import PdfPages
from common.boilerplate import start_plaxis
from plxscripting.easy import new_server
from solver.plaxis2d.output_commands import get_plate_outputs_with_y_limits
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
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

class Dim_wall_inserted_steel_profile(QtWidgets.QWidget):
    """ This class implements dimensioning tool for the steel profile and its connection to RC continous wall
    """
    def __init__(self, form, project_title, Walls, Wallmaterials, Phases, design_situation='BS-P: Persistent', 
                internal_forces_max={'M2D': 0.0, 'Q2D': 0.0, 'N2D': 100.0}, internal_forces_top_RC_wall={'M2D': 0.0, 'Q2D': 0.0, 'N2D': 100.0}):
        super(Dim_wall_inserted_steel_profile, self).__init__()
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
        self.pixmap = QPixmap('D:\Data\\3Packages\\Moniman-master\\solver\\plaxis2d\\beamfixity.jpg')

        # initilizes tables for wall internal forces
        self.initialize_tables_wall_internal_forces()
        self.internal_forces_max = internal_forces_max                          # characteristic loads
        self.internal_forces_top_RC_wall = internal_forces_top_RC_wall          # characteristic loads
        self.update_tables_internal_forces(self.wall_profile)

        ## fill table steel profiile cross section
        self.fill_table_cross_section(self.wall_profile)
        # get cross-section class
        self.get_cross_section_class(self.wall_profile)

        # connect signals and update basic settings once
        self.connect_signals_to_slots()

        form.exec_()


    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.comboBox.currentTextChanged.connect(self.update_design_situation)
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_with_custom_value_psf(row, column))
        self.ui.pushButton_2.clicked.connect(self.retrieve_plaxis2d_database) 
        self.ui.tableWidget_2.cellChanged.connect(lambda row, column: self.update_max_internal_forces_user_value(row, column))
        self.ui.tableWidget_8.cellChanged.connect(lambda row, column: self.update_internal_forces_top_RC_wall_user_value(row, column))
        self.ui.tableWidget_3.cellChanged.connect(lambda row, column: self.respond_to_steel_profile_nos_fyk(row, column))
        self.ui.tableWidget_6.cellChanged.connect(lambda row, column: self.respond_to_reinforcement_grade(row,column))
        #self.ui.pushButton.clicked.connect(self.print_report) # print report


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
        self.update_tables_internal_forces(self.wall_profile)


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
                    self.update_tables_internal_forces(self.wall_profile)

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
        # fill wall materials
        #for wallmat in self.Wallmaterials:
        #    self.ui.comboBox_2.addItem(wallmat['json_item'])
        self.ui.comboBox_2.addItem(self.wall_profile['json_item'])
        
        # set limit for the number of calculation phases
        self.ui.spinBox.setMinimum(1)
        self.ui.spinBox.setMaximum(len(self.Phases))
        self.ui.spinBox.setValue(1)

        # fill RC wall cut-off level, (top of the first inserted wall by default)
        top_RC_wall = max(self.Walls[0]['point1'][1], self.Walls[0]['point2'][1])
        self.ui.lineEdit.setText(str(top_RC_wall))

        # initialize tables
        vertical_labels = ['Max. M [kNm]', 'Max. Q [kN]', 'Max. N [kN]']
        self.ui.tableWidget_2.setColumnCount(2)
        self.ui.tableWidget_2.setRowCount(len(vertical_labels))
        self.ui.tableWidget_2.setVerticalHeaderLabels(vertical_labels)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(['Characteristic value', 'Design value'])
        vertical_labels = ['Me [kNm]', 'Qe [kN]', 'Ne [kN]']
        self.ui.tableWidget_8.setColumnCount(2)
        self.ui.tableWidget_8.setRowCount(len(vertical_labels))
        self.ui.tableWidget_8.setVerticalHeaderLabels(vertical_labels)
        self.ui.tableWidget_8.setHorizontalHeaderLabels(['Characteristic value', 'Design value'])
    

    def retrieve_plaxis2d_database(self):
        """ Reads plaxis2d database using the current settings
        """
        x_wall = self.wall_profile['point1'][0]
        phasenumber = self.ui.spinBox.value()
        top_RC_wall = float(self.ui.lineEdit.text())
        should_read_envelop = self.ui.checkBox.checkState() == 2
            
        PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
        subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)

            
        s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
                    
        path = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        output_database = os.path.join(path, 'retaining_wall.p2dx')
        s_o.open(output_database)

        self.update_wall_outputs(g_o, path, x_wall, top_RC_wall, self.wall_profile, phasenumber, should_read_envelop)


    def update_wall_outputs(self, g_o, path, x_wall, top_RC_wall, wall, phasenumber, should_read_envelop=False):        
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
            M2D_max = max(list(map(abs, M2Demax_plate + M2Demin_plate)))
            Q2D_max = max(list(map(abs, Q2Demax_plate + Q2Demin_plate)))
            N2D_max = -min(Nx2Demax_plate + Nx2Demin_plate)  # compression is positive
        else:
            M2D_max = max(list(map(abs, M2D_plate)))
            Q2D_max = max(list(map(abs, Q2D_plate)))
            N2D_max = -min(Nx2D_plate)                       # compression is positive
        
        self.internal_forces_max = {'M2D': M2D_max*wall['spacing'], 'Q2D': Q2D_max*wall['spacing'], 'N2D': N2D_max*wall['spacing']}
        
        print('\nMax. values: \nM2D_max = {0:.2f} [kNm/m], Q2D_max = {1:.2f} [kN/m], N2D_max = {2:.2f} [kN/m]'.format(M2D_max, Q2D_max, N2D_max))

        # get internal forces at top of reinforced concrete wall (lower wall)
        idx_y_RC_top = y_plate.index(top_RC_wall)
        if should_read_envelop:
            M2D_top_RC_wall = max(abs(M2Demax_plate[idx_y_RC_top]), abs(M2Demin_plate[idx_y_RC_top]))
            Q2D_top_RC_wall = max(abs(Q2Demax_plate[idx_y_RC_top]), abs(Q2Demax_plate[idx_y_RC_top]))
            N2D_top_RC_wall = -min(Nx2Demax_plate[idx_y_RC_top], Nx2Demax_plate[idx_y_RC_top])  # compression is positive
        else:
            M2D_top_RC_wall = abs(M2D_plate[idx_y_RC_top])
            Q2D_top_RC_wall = abs(Q2D_plate[idx_y_RC_top])
            N2D_top_RC_wall = -Nx2D_plate[idx_y_RC_top] # compression is positive

        self.internal_forces_top_RC_wall = {'M2D': M2D_top_RC_wall*wall['spacing'], 'Q2D': Q2D_top_RC_wall*wall['spacing'], 'N2D': N2D_top_RC_wall*wall['spacing']} # linear_force * profile_spacing

        print('\nValues at top of concrete wall: \nM2D_max = {0:.2f} [kNm/m], Q2D_max = {1:.2f} [kN/m], N2D_max = {2:.2f} [kN/m]'.format(M2D_top_RC_wall, Q2D_top_RC_wall, N2D_top_RC_wall))

        # fill tables for internal forces
        self.update_tables_internal_forces(wall)

        ## fill table steel profiile cross section
        #self.fill_table_cross_section(wall)


    def update_max_internal_forces_user_value(self, row, column):
        """ Updates max. internal forces with user value
        """
        items = ['M2D', 'Q2D', 'N2D']
        if column == 0:
            try:
                value = float(self.ui.tableWidget_2.item(row, column).text())
                self.internal_forces_max[items[row]] = value
                self.update_tables_internal_forces(self.wall_profile)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def update_internal_forces_top_RC_wall_user_value(self, row, column):
        """ Updates max. internal forces at top of RC wall with user value
        """
        items = ['M2D', 'Q2D', 'N2D']
        if column == 0:
            try:
                value = float(self.ui.tableWidget_8.item(row, column).text())
                self.internal_forces_top_RC_wall[items[row]] = value
                self.update_tables_internal_forces(self.wall_profile)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def update_tables_internal_forces(self, wall):
        """ Fills table for wall internal forces
        """
        self.ui.tableWidget_2.blockSignals(True)
        self.ui.tableWidget_8.blockSignals(True)
        items_to_list = ['M2D', 'Q2D', 'N2D']
        for i, item in enumerate(items_to_list):
            self.ui.tableWidget_2.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.internal_forces_max[item])))
            self.ui.tableWidget_2.item(i, 0).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget_2.setItem(i, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.internal_forces_max[item]*self.PSFs[self.design_situation]['permanent'])))
            self.ui.tableWidget_8.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.internal_forces_top_RC_wall[item])))
            self.ui.tableWidget_8.item(i, 0).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget_8.setItem(i, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(self.internal_forces_top_RC_wall[item]*self.PSFs[self.design_situation]['permanent'])))
        self.ui.tableWidget_2.blockSignals(False)
        self.ui.tableWidget_8.blockSignals(False)


    def fill_table_cross_section(self, wall):
        """ Fills table for cross section of H/U profile.
        """
        if wall['wall_type'] == 'Steel profile H/U':
            #items_to_list = ['profile_id', 'nos', 'fyk']
            items_to_list_with_unit = ['profile ID [-]', 'No. [-]', 'fy,k [MPa]']
            self.ui.tableWidget_3.clear()   # clear table to remove cellWidget(0, 0)
            self.ui.tableWidget_3.blockSignals(True)
            self.ui.tableWidget_3.setRowCount(len(items_to_list_with_unit))
            self.ui.tableWidget_3.setColumnCount(1)
            self.ui.tableWidget_3.setVerticalHeaderLabels(items_to_list_with_unit)

            profile_names = self.get_steel_profile_names()
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for name in profile_names:
                combobox.addItem(name)
            # show current profile id
            profile_id_index = profile_names.index(wall['json_item'][:-2])
            combobox.setCurrentIndex(profile_id_index)
            # set property and connect signal to slot
            combobox.setProperty('profile_id', 0)
            combobox.activated[str].connect(lambda profile_id: self.respond_to_profile_id_selection(profile_id))
            self.ui.tableWidget_3.setCellWidget(0, 0, combobox)

            self.ui.tableWidget_3.setItem(1, 0, QtWidgets.QTableWidgetItem('{}'.format(wall['profile_nos'])))
            self.ui.tableWidget_3.item(1, 0).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget_3.setItem(2, 0, QtWidgets.QTableWidgetItem('{}'.format(wall['fyk'])))
            self.ui.tableWidget_3.item(2, 0).setBackground(QColor(242, 255, 116))

            # display profile parameters
            self.display_parameters_steel_profile(wall)

            self.ui.tableWidget_3.blockSignals(False)


    def get_steel_profile_names(self):
        """ Gets available steel profile names
        """
        PATH_PROFILES = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels_H_U\\jsons')
        profile_names = []
        for item in glob.glob(PATH_PROFILES + '\\*'):
            profile_name = os.path.basename(item)
            profile_names.append(profile_name[:-5]) # no file ending '.json'
        
        return profile_names


    def respond_to_profile_id_selection(self, profile_id):
        """ Responds to profile id selection
        """
        self.wall_profile['json_item'] = profile_id + '__'

        # display profile parameters
        self.display_parameters_steel_profile(self.wall_profile)
        # get cross-section class
        self.get_cross_section_class(self.wall_profile)


    def respond_to_steel_profile_nos_fyk(self, row, column):
        """ Responds to change in steel profile number and fyk
        """
        items_to_list = ['profile_id', 'nos', 'fyk']
        if row == 0:    # change in profile id, already handled by cellWidget signal
            pass
        elif row == 1: # nos
            value = int(self.ui.tableWidget_3.item(row, column).text())
            self.wall_profile['profile_nos'] = value
        elif row == 2: # fck
            value = float(self.ui.tableWidget_3.item(row, column).text())
            self.wall_profile['fyk'] = value

        # display profile parameters
        self.display_parameters_steel_profile(self.wall_profile)
        # get cross-section class
        self.get_cross_section_class(self.wall_profile)


    def display_parameters_steel_profile(self, wall):
        """ Displays steel profile parameters
        """
        # list cross-section parameters
        profile_id = wall['json_item'][:-2]
        profile_nos = wall['profile_nos']
        profile_fyk = wall['fyk']
        json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels_H_U\\jsons', profile_id + '.json')
        with open(json_item, "r") as read_file:
            params = json.load(read_file, object_pairs_hook = OrderedDict)
        design_loads = {'Nd': self.internal_forces_max['N2D'] ,'Myd': self.internal_forces_max['M2D'], 'Mzd': 0.0}
        cross_section = SteelProfile(profile_fyk, self.PSFs[self.design_situation], design_loads, float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                            float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                            float(params['g']), buckling_curve=params['Knick'], nos=profile_nos)

        row_labels = ["Profile ID [-]", "No. [-]", "fy,k [Mpa]", "h [mm]", "b [mm]", "tw [mm]", "tf [mm]", "r [mm]", "A [cm^2]", "Iyy [cm^4]", "Izz [cm^4]", "Itor [cm^4]", "Iw [cm^6]", "W_el_y [cm^3]", "W_el_z [cm^3]", "W_pl_y [cm^3]", "W_pl_z [cm^3]", "N_pl,d [kN]", "V_pl,d [kN]", "M_pl,d,y [kNm]", "M_pl,d,z [kNm]", "g [kN/m]", "p [kN/m]"]
        self.ui.tableWidget_3.blockSignals(True)
        self.ui.tableWidget_3.setRowCount(len(row_labels))
        self.ui.tableWidget_3.setColumnCount(1)
        self.ui.tableWidget_3.setVerticalHeaderLabels(row_labels)
        items_to_list = ['h', 'b', 'tw', 'tf', 'r', 'A', 'Iyy', 'Izz', 'Itor', 'Iw','W_el_y', 'W_el_z', 'W_pl_y', 'W_pl_z', 'N_pl_d', 'V_pl_d', 'M_pl_d_y', 'M_pl_d_z', 'g', 'p']
        for i, item in enumerate(items_to_list):
            self.ui.tableWidget_3.setItem(0, i+3, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
        self.ui.tableWidget_3.blockSignals(False)


    def get_cross_section_class(self, wall):
        """ Gets cross section class
        """
        profile_id = wall['json_item'][:-2]
        profile_nos = wall['profile_nos']
        profile_fyk = wall['fyk']
        json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels_H_U\\jsons', profile_id + '.json')
        with open(json_item, "r") as read_file:
            params = json.load(read_file, object_pairs_hook = OrderedDict)

        gamma_F = self.PSFs[self.design_situation]['permanent']
        design_loads = {'Nd': gamma_F*self.internal_forces_max['N2D'] ,'Myd': gamma_F*self.internal_forces_max['M2D'], 'Mzd': 0.0}
        cross_section = SteelProfile(profile_fyk, self.PSFs[self.design_situation], design_loads, float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                            float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                            float(params['g']), buckling_curve=params['Knick'], nos=profile_nos)

        design_loads_cross_section_classification = {'Nd':  gamma_F*self.internal_forces_max['N2D']/profile_nos ,'Myd': gamma_F*self.internal_forces_max['N2D']/profile_nos, 'Mzd': 0.0}
        cross_section.QK, cross_section.QK_w, cross_section.QK_f = cross_section.get_cross_section_class(design_loads_cross_section_classification)
        self.ui.tableWidget_4.clear()
        row_labels = ['QK [-]', 'QK_web [-]', 'QK_flange [-]', 'epsilon [-]', 'alpha_web [-]', 'c/tw [-]', 'c/tw zul. [-]', 'sigma_1_web [kN/cm^2]', 'sigma_2_web [kN/cm^2]', 'psi_web [-]', 'c/tf [-]', 'c/tf zul. [-]']
        items_to_list = ['QK', 'QK_w', 'QK_f', 'epsilon', 'alpha_web', 'c_over_tw', 'c_over_tw_zul', 'sigma_1_web', 'sigma_2_web', 'psi_web', 'c_over_tf', 'c_over_tf_zul']
        self.ui.tableWidget_4.setRowCount(len(items_to_list))
        self.ui.tableWidget_4.setColumnCount(1)
        self.ui.tableWidget_4.setVerticalHeaderLabels(row_labels)
        for i, item in enumerate(items_to_list):
            if item in ['QK', 'QK_w', 'QK_f']:
                self.ui.tableWidget_4.setItem(i, 0, QtWidgets.QTableWidgetItem('{}'.format(getattr(cross_section, item))))
            else:
                self.ui.tableWidget_4.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
    
        # store cross-section for stress verifications and report generation
        self.cross_section = cross_section

        # perform stress and embedment verifications
        self.perform_stress_verifications(wall)
        self.perform_embedment_verifications(wall)
        #sketch plot
        self.ui.label_6.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(),self.pixmap.height())


    def perform_stress_verifications(self, wall):
        """ Performs stress verfications of the steel profile
        """
        gamma_F = self.PSFs[self.design_situation]['permanent']
        # max. internal forces
        util_N_max = gamma_F * self.internal_forces_max['N2D']/self.cross_section.N_pl_d
        util_V_max = gamma_F * self.internal_forces_max['Q2D']/self.cross_section.V_pl_d

        # at top of RC wall
        util_N_e = gamma_F * self.internal_forces_top_RC_wall['N2D']/self.cross_section.N_pl_d
        util_V_e = gamma_F * self.internal_forces_top_RC_wall['Q2D']/self.cross_section.V_pl_d

        # perform interation stress verification
        design_loads_Mmax = {'Nd': gamma_F*self.internal_forces_max['N2D'] ,'Myd': gamma_F*self.internal_forces_max['M2D'], 'Mzd': 0.0, 'Vd': gamma_F*self.internal_forces_max['Q2D']}
        design_loads_Me = {'Nd': gamma_F*self.internal_forces_top_RC_wall['N2D'] ,'Myd': gamma_F*self.internal_forces_top_RC_wall['M2D'], 'Mzd': 0.0, 'Vd': gamma_F*self.internal_forces_top_RC_wall['Q2D']}
        if self.cross_section.QK < 3:
            util_M_max = self.cross_section.perform_interaction_stress_verification_QK1_QK2(design_loads_Mmax)
            util_M_e = self.cross_section.perform_interaction_stress_verification_QK1_QK2(design_loads_Me)
        else: # QK3
            util_M_max = self.cross_section.perform_interaction_stress_verification_QK3(design_loads_Mmax)
            util_M_e = self.cross_section.perform_interaction_stress_verification_QK3(design_loads_Me)


        # display the stress verfication results on table
        self.ui.tableWidget_5.clear()
        self.ui.tableWidget_6.clear()
        self.ui.tableWidget_6.setRowCount(0)
        self.ui.tableWidget_6.setColumnCount(0)
        row_labels = ['N_Ed/N_pl_Rd [-]', 'V_Ed/V_pl_Rd [-]', 'My_Ed/My_pl_Rd [-]']
        column_labels = ['Max. value', 'At top of RC wall']
        self.ui.tableWidget_5.setRowCount(len(row_labels))
        self.ui.tableWidget_5.setColumnCount(len(column_labels))
        self.ui.tableWidget_5.setVerticalHeaderLabels(row_labels)
        self.ui.tableWidget_5.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_5.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_N_max)))
        self.ui.tableWidget_5.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_V_max)))
        self.ui.tableWidget_5.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_M_max)))    #!!
        self.ui.tableWidget_5.setItem(0, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_N_e)))
        self.ui.tableWidget_5.setItem(1, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_V_e)))
        self.ui.tableWidget_5.setItem(2, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_M_e)))      #!!

            
    def perform_embedment_verifications(self, wall):
        """ Performs embedment verfications of the steel profile
        """
        gamma_F = self.PSFs[self.design_situation]['permanent']

        # max. internal forces
        design_loads_Me = {'Nd': gamma_F*self.internal_forces_top_RC_wall['N2D'] ,'Myd': gamma_F*self.internal_forces_top_RC_wall['M2D'], 'Mzd': 0.0, 'Vd': gamma_F*self.internal_forces_top_RC_wall['Q2D']}

        bottom_steel_beam = min(self.Walls[1]['point1'][1], self.Walls[1]['point2'][1])
        top_RC_wall = max(self.Walls[0]['point1'][1], self.Walls[0]['point2'][1])
        embed_t =  top_RC_wall-bottom_steel_beam        #embedment from profile

        d = self.Walls[0]['wall_thickness']
        d1 = 0.11 if d>0.62 else 0.06 #edge distance or effective depth
        z = 0.85*(d-d1) #effective diameter

        #table_internal_forces_top_RC_Wall
        util_M_e_d = design_loads_Me['Myd']
        util_V_e_d = design_loads_Me['Vd']


        #design_loads
        Z_h_d = (6*((util_M_e_d/embed_t)+util_V_e_d))/5
        Z_v_d = (5/6)*(Z_h_d*embed_t)*(1/z)
        M_T_e = util_M_e_d+(embed_t*((util_V_e_d/6)-(Z_h_d/24)))
        V_T_e = Z_h_d-util_V_e_d

        #display the verification in a table
        #self.ui.tableWidget_6.clear()
        row_labels1 = ["Embedment t [m]","Z_h_d [kN]","Z_v_d [kN]","M_T_e [kNm] ","V_T_e [kN]","f_yk [MPa]","spiral cross section a_min over : {} m [cm2/m]".format(embed_t), "Longitudinal reinforcement A_min [cm2]"]
        self.ui.tableWidget_6.setRowCount(len(row_labels1))
        self.ui.tableWidget_6.setColumnCount(1)
        self.ui.tableWidget_6.setVerticalHeaderLabels(row_labels1)  
        self.ui.tableWidget_6.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(embed_t)))
        self.ui.tableWidget_6.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(Z_h_d)))
        self.ui.tableWidget_6.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(Z_v_d)))
        self.ui.tableWidget_6.setItem(3, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(M_T_e)))
        self.ui.tableWidget_6.setItem(4, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(V_T_e)))
        self.ui.tableWidget_6.setItem(5, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(500)))
        self.ui.tableWidget_6.item(5, 0).setBackground(QColor(242, 255, 116))
        gamma_s = self.PSFs[self.design_situation]['gamma_s']
        a_min = Z_h_d/(embed_t/3)/(500/10/gamma_s)
        A_min = Z_h_d/(500/10/gamma_s)
        self.ui.tableWidget_6.setItem(6, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(a_min)))
        self.ui.tableWidget_6.setItem(7, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(A_min)))

        
    def update_reinforcement_cage_over_embedment(self,fyk):
        #calculates_extrareinforcement_required_over_embedment_of_the_beam_into_the_wall
        embed_t = float(self.ui.tableWidget_6.item(0,0).text())
        Z_h_d = float(self.ui.tableWidget_6.item(1,0).text())
        self.ui.tableWidget_6.blockSignals(True)
        gamma_s = self.PSFs[self.design_situation]['gamma_s']
        a_min = Z_h_d/(embed_t/3)/(fyk/10/gamma_s)
        A_min = Z_h_d/(fyk/10/gamma_s)
        self.ui.tableWidget_6.setItem(6, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(a_min)))
        self.ui.tableWidget_6.setItem(7, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(A_min)))
        self.ui.tableWidget_6.blockSignals(False)
        

    def respond_to_reinforcement_grade(self,row,column):
        try:
            value = int(self.ui.tableWidget_6.item(row, column).text())
        except:
            value = 500
        self.update_reinforcement_cage_over_embedment(value)

        



