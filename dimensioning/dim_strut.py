# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 16:34:14 2022

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
from gui.gui_widget_Dim_strut import Ui_Form as DimForm
from dimensioning.struts.steel_tube import SteelTube
from dimensioning.struts.steel_profile import SteelProfile
from dimensioning.struts.report import Report
from matplotlib.backends.backend_pdf import PdfPages
from system.system import load_paths

# load PATHS.py
load_paths(r'common\\PATHS.py')
ACROBAT = sys.modules['moniman_paths']['ACROBAT']

psf_p = {'permanent': 1.35, 'transient': 1.5, 'gamma_c': 1.5, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_t = {'permanent': 1.2, 'transient': 1.3, 'gamma_c': 1.5, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_a = {'permanent': 1.1, 'transient': 1.1, 'gamma_c': 1.3, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
psf_e = {'permanent': 1.0, 'transient': 1.0, 'gamma_c': 1.3, 'gamma_M0': 1.0, 'gamma_M1': 1.1}
PSFs = {'BS-P: Persistent': psf_p, 'BS-T: Transient': psf_t, 'BS-A: Accidential': psf_a, 'BS-E: Seismic': psf_e}
alpha_buckling_curves = {'a0': 0.13, 'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}

class Dim_strut(QtWidgets.QWidget):
    """ This class implements dimensioning tool for struts
    """
    def __init__(self, form, project_title, Struts, design_situation='BS-P: Persistent', fyk = 235.0):
        super(Dim_strut, self).__init__()
        self.ui = DimForm()
        self.ui.setupUi(form)
        self.dialog = Ui_Dialog()
        self.project_title = project_title

        self.PSFs = PSFs
        self.design_situation = design_situation
        # display design situation
        design_situations = ['BS-P: Persistent', 'BS-T: Transient', 'BS-A: Accidential', 'BS-E: Seismic']
        self.ui.comboBox.setCurrentIndex(design_situations.index(self.design_situation))

        # design loads
        #self.design_loads = {'Nd': 100.0, 'Myd': 0.0, 'Mzd': 0.0}

        # steel yield stress
        self.fyk = fyk
        self.ui.lineEdit.setText(str(self.fyk)) # display fyk

        self.Struts = Struts

        # initialize table for PSFs
        self.initialize_table_psf()

        # fill table for struts
        self.fill_table_struts()

        # initialize table for cross section
        positions_strut = [strut['position'] for strut in self.Struts]
        for position in positions_strut:
            position_id = '{}'.format(position[1])  # strut is indexed by level
            self.ui.comboBox_2.addItem(position_id)
        self.ui.tableWidget_3.setRowCount(3)    # minimal number of rows: 3, will be extended later
        self.ui.tableWidget_3.setColumnCount(1)
        self.initialize_cross_section()

        # initialize tables for strut design
        self.initialize_tables_strut_design()


        # connect signals and update basic settings once
        self.connect_signals_to_slots()

        form.exec_()



    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.comboBox.currentTextChanged.connect(self.update_design_situation)
        self.ui.lineEdit.editingFinished.connect(lambda: self.update_fyk(self.ui.lineEdit.text()))
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_with_custom_value_psf(row, column))
        self.ui.tableWidget_2.cellChanged.connect(lambda row, column: self.update_with_custom_value_strut(row, column))
        self.ui.comboBox_2.currentTextChanged.connect(self.update_strut_layer)  # strut layer selection
        #self.ui.radioButton.toggled.connect(self.update_strut_type)
        self.ui.radioButton.clicked.connect(self.update_strut_type)         # receive the signal clicked() from two radio buttons instead of toggled() because signal from radio buttons cannot be disabled
        self.ui.radioButton_2.clicked.connect(self.update_strut_type)
        self.ui.pushButton.clicked.connect(self.print_report) # print report


    def update_design_situation(self, design_situation):
        """ Updates design situation
        """
        # fill in table values
        self.design_situation = design_situation
        self.fill_table_psf()

        # refresh the rest
        position = self.ui.comboBox_2.currentText()
        self.update_strut_layer(position)
        tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
        self.respond_to_profile_id_selection(tube_name)


    def update_fyk(self, fyk_text):
        """ Updates fyk
        """
        try:
            self.fyk = float(fyk_text)
            # refresh the rest
            profile_id = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
            self.respond_to_profile_id_selection(profile_id)

        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def initialize_table_psf(self):
        """ Initialize table for partial safety factors
        """
        self.ui.tableWidget.setRowCount(1)
        column_labels = ['permanent', 'transient', 'gamma_c', 'gamma_M0', 'gamma_M1']
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
        self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_M0'])))
        self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(str(self.PSFs[self.design_situation]['gamma_M1'])))
        for col_i in range(5):
            self.ui.tableWidget.item(0, col_i).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.blockSignals(False)


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
                    position = self.ui.comboBox_2.currentText()
                    self.update_strut_layer(position)
                    tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
                    self.respond_to_profile_id_selection(tube_name)

                except ValueError:
                    self.dialog.show_message_box('Error', 'Please check if the value you entered are correct!')

            else: # text is empty, set back stored values
                self.update_design_situation(self.design_situation)


    def read_parameters_psf(self):
        """ Reads and stores parameter values from psf table
        """
        try:
            psf_items = ['permanent', 'transient', 'gamma_c', 'gamma_M0', 'gamma_M1']
            for i, psf_i in enumerate(psf_items):
                if self.ui.tableWidget.item(0, i): # is not None
                    self.PSFs[self.design_situation][psf_i] = float(self.ui.tableWidget.item(0, i).text())
        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))

    
    def fill_table_struts(self):
        """ Fills table for struts
        """
        items_to_list = ['position', 'direct_x', 'direct_y', 'Lspacing', 'F_strut', 'slope_vert', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
        items_to_list_with_units = ['Strut y level [mNN]', 'direct_x [m]', 'direct_y [m]', 'Lspacing [m]', 'F_strut [kN]', 'slope vert. [deg.]', 'slope horiz. [deg.]', 'buckl. length sy [m]', 'buckl. length sz [m]', 'eccentricity e/h [-]', 'eccentricity e/b [-]']
        self.ui.tableWidget_2.setColumnCount(len(items_to_list_with_units))
        self.ui.tableWidget_2.setHorizontalHeaderLabels(items_to_list_with_units)
        self.ui.tableWidget_2.setRowCount(len(self.Struts))
        for i, strut in enumerate(self.Struts):
            for j, item in enumerate(items_to_list):
                if item == 'position': # display only y level
                    self.ui.tableWidget_2.setItem(i, j, QtWidgets.QTableWidgetItem(str(strut[item][1])))
                else:
                    self.ui.tableWidget_2.setItem(i, j, QtWidgets.QTableWidgetItem(str(strut[item])))
                # mark editable items with yellow
                items_editable = ['F_strut', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
                if item in items_editable:
                    self.ui.tableWidget_2.item(i, j).setBackground(QColor(242, 255, 116))


    def update_with_custom_value_strut(self, row, column):
        """ Updates a custom value for strut parameters
        """
        text = self.ui.tableWidget_2.item(row, column).text()
        if text != '':
            try:
                # reference strut by level
                y_level = float(self.ui.tableWidget_2.item(row, 0).text())
                for strut in self.Struts:
                    if (strut['position'][1] == float(y_level)):
                        strut_selected = strut
                        break
                self.read_parameters_strut(strut_selected, row, column)  # read and store parameter values

                # refresh the rest
                #self.update_strut_layer(position)
                tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
                self.respond_to_profile_id_selection(tube_name)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))
    
        else: # text is empty, set back stored values
            self.fill_table_struts()


    def read_parameters_strut(self, strut, row, column):
        """ Reads strut parameter from table for the selected strut
        """
        items_to_list = ['position', 'direct_x', 'direct_y', 'Lspacing', 'F_strut', 'slope_vert', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
        items_editable = ['F_strut', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
        value = float(self.ui.tableWidget_2.item(row, column).text())
        if items_to_list[column] in items_editable:
            strut[items_to_list[column]] = value


    def initialize_tables_strut_design(self):
        """ Initialize tab(s) for strut design
        The number of tabs is the number of strut layers"""
        # table for tube's cross section information
        self.ui.tableWidget_3.setRowCount(3)    # minimal number of rows: 3, will be extended later
        self.ui.tableWidget_3.setColumnCount(1)
        # table for design internal forces
        row_labels_loads = ["N_d [kN]", "My_d [kNm]", "Mz,d [kNm]"]
        self.ui.tableWidget_4.setRowCount(len(row_labels_loads))
        self.ui.tableWidget_4.setColumnCount(1)
        self.ui.tableWidget_4.setVerticalHeaderLabels(row_labels_loads)
        # table for cross-section class
        row_labels_loads = ["epsilon [-]", "c/t [-]", "cross-section class [-]"]
        self.ui.tableWidget_7.setRowCount(len(row_labels_loads))
        self.ui.tableWidget_7.setColumnCount(1)
        self.ui.tableWidget_7.setVerticalHeaderLabels(row_labels_loads)

        # table for flexural buckling
        column_labels_buckling = ["alpha_pl [-]", "imp. factor alpha [-]", "N_cr [kN]", "slendern. lambda [-]", 
                            "reduct. factor chi [-]", "N_pl_Rd [kN]", "reduct. factor k [-]", "M_pl_Rd [kNm]",
                            "N_d/(chi*N_pl_Rd)", "M_d*k/(M_pl_Rd)", "Total utilization"]
        self.ui.tableWidget_5.setColumnCount(len(column_labels_buckling))
        self.ui.tableWidget_5.setRowCount(2)
        self.ui.tableWidget_5.setHorizontalHeaderLabels(column_labels_buckling)
        self.ui.tableWidget_5.setVerticalHeaderLabels(['Axis y-y', 'Axis z-z'])

        # show strut info for the first layer once
        position = self.ui.comboBox_2.currentText()
        self.update_strut_layer(position)
        profile_id = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
        #self.respond_to_profile_id_selection(profile_id, self.Struts[0], to_be_assigned=False)
        self.respond_to_profile_id_selection(profile_id, to_be_assigned=False)


    def update_strut_type(self, is_checked):
        """ Updates trut type of the strut layer
        """
        # which strut is selected?
        position = self.ui.comboBox_2.currentText()
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break
        if self.ui.radioButton.isChecked() is True:
            strut_selected['strut_type'] = 'SteelTube'
        elif self.ui.radioButton_2.isChecked() is True:
            strut_selected['strut_type'] = 'SteelProfile'
        
        # initialize cross_section
        strut_selected['assigned'] = False  # set assigned as False when switching strut type
        self.initialize_cross_section()



    def initialize_cross_section(self):
        """ Initializes responsive widgets for cross-section 
        """
        # which strut is selected?
        position = self.ui.comboBox_2.currentText()
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break

        # profile names
        profile_names = self.get_strut_profile_names(strut_selected['strut_type'])
        combobox = QtWidgets.QComboBox()
        combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        for name in profile_names:
            combobox.addItem(name)
        combobox.setProperty('profile_id', 0)
        #combobox.activated[str].connect(lambda profile_id: self.respond_to_profile_id_selection(profile_id, strut_selected, to_be_assigned=True))
        combobox.activated[str].connect(lambda profile_id: self.respond_to_profile_id_selection(profile_id, to_be_assigned=True))
        self.ui.tableWidget_3.setCellWidget(0, 0, combobox)
        # for number of profiles
        combobox1 = QtWidgets.QComboBox()
        combobox1.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        tube_nos = [1, 2]
        for name in tube_nos:
            combobox1.addItem(str(name))
        combobox1.setProperty('tube_nos', 1)
        combobox1.activated[str].connect(lambda tube_nos: self.respond_to_profile_number_change(tube_nos))
        self.ui.tableWidget_3.setCellWidget(1, 0, combobox1)
        # for distance betwen multiple struts
        line_edit = QtWidgets.QLineEdit()
        line_edit.setStyleSheet("background-color: rgb(242, 255, 116);\n")
        line_edit.setProperty('d_b2b', 2)
        line_edit.editingFinished.connect(self.respond_to_distance_beam2beam)
        self.ui.tableWidget_3.setCellWidget(2, 0, line_edit)
        self.ui.tableWidget_3.cellWidget(2, 0).setText(str(100.0))  # default d_b2b when strut layer is first switched to
        if strut_selected['assigned'] is False:
        #if strut_selected['profile_id'] == '':
            # update results with the default (first item in the list of profiles)
            profile_id = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
            strut_selected['assigned'] = False
        else: # use the stored profile_id
            nos = strut_selected['nos']
            self.ui.tableWidget_3.cellWidget(1, 0).setCurrentIndex(nos - 1)     # number of profiles
            profile_id = strut_selected['profile_id']
        #self.respond_to_profile_id_selection(profile_id, strut_selected, strut_selected['assigned'])
        self.respond_to_profile_id_selection(profile_id)



    def update_strut_layer(self, position):
        """ Updates strut selection based on strut level
        """
        #print('\n\nupdate_strut_layer is called, position', position)
        # which strut is selected?
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break
        #print(strut_selected['assigned'], strut_selected['strut_type'], strut_selected['profile_id'])

        if strut_selected['assigned'] is False: # not assigned yet
            # steel tubes or profiles?
            if self.ui.radioButton.isChecked():
                strut_selected['strut_type'] = 'SteelTube'
            elif self.ui.radioButton_2.isChecked():
                strut_selected['strut_type'] = 'SteelProfile'

            # intialize cross-section, without assignment of profile to the selected strut
            self.initialize_cross_section()

        else: # profile has been assigned to strut, display assigned profile only

            # display strut type on radio button
            if strut_selected['strut_type'] == 'SteelTube':
                self.ui.radioButton.setChecked(True)
                self.ui.radioButton_2.setChecked(False)
            elif strut_selected['strut_type'] == 'SteelProfile':
                self.ui.radioButton.setChecked(False)
                self.ui.radioButton_2.setChecked(True)
            # profile id
            profile_id = strut_selected['profile_id']
            profile_names = self.get_strut_profile_names(strut_selected['strut_type'])
            # clear and refill combobox for profile ids
            self.ui.tableWidget_3.cellWidget(0, 0).setEnabled(False)
            self.ui.tableWidget_3.cellWidget(1, 0).setEnabled(False)
            self.ui.tableWidget_3.cellWidget(2, 0).setEnabled(False)
            self.ui.tableWidget_3.cellWidget(0, 0).clear()
            for name in profile_names:
                self.ui.tableWidget_3.cellWidget(0, 0).addItem(name)
            profile_id_index = profile_names.index(profile_id)
            self.ui.tableWidget_3.cellWidget(0, 0).setCurrentIndex(profile_id_index)
            # number of profiles
            self.ui.tableWidget_3.cellWidget(1, 0).setCurrentIndex(strut_selected['cross_section'].nos - 1)
            # distance beam to beam
            self.ui.tableWidget_3.cellWidget(2, 0).setText(str(strut_selected['cross_section'].distance_beam2beam))
            # update the rest
            self.update_the_rest(strut_selected, strut_selected['cross_section'])

            self.ui.tableWidget_3.cellWidget(0, 0).setEnabled(True)
            self.ui.tableWidget_3.cellWidget(1, 0).setEnabled(True)
            self.ui.tableWidget_3.cellWidget(2, 0).setEnabled(True)


    def get_strut_profile_names(self, strut_type):
        """ Gets available steel tubes to select
        strut_type: a string whose value is either 'SteelTube' or 'SteelProfile'
        """
        if strut_type == 'SteelTube':
            PATH_PROFILES = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\tubes\\jsons')
        elif strut_type == 'SteelProfile':
            PATH_PROFILES = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons')

        profile_names = []
        for item in glob.glob(PATH_PROFILES + '\\*'):
            profile_name = os.path.basename(item)
            profile_names.append(profile_name[:-5]) # no file ending '.json'
        
        return profile_names


    def respond_to_profile_id_selection(self, profile_id, to_be_assigned=True):
        """ Responds to profile id selection
        """
        # which strut is selected?
        position = self.ui.comboBox_2.currentText()
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break

        # read current profile numbers (the number of beams)
        profile_nos = int(self.ui.tableWidget_3.cellWidget(1, 0).currentText())

        # read cross-section information 
        if strut_selected['strut_type'] == 'SteelTube':
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\tubes\\jsons', profile_id + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            # instantiate cross section
            cross_section = SteelTube(self.fyk, self.PSFs[self.design_situation], float(params['D']), float(params['t']), float(params['A']), float(params['Sy']), float(params['I']), float(params['W']),
                                float(params['G']), buckling_curve=params['Knick'], nos=profile_nos)

        elif strut_selected['strut_type'] == 'SteelProfile':
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', profile_id + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            # instantiate cross section
            cross_section = SteelProfile(self.fyk, self.PSFs[self.design_situation], strut_selected['design_loads'], float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                                float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                                float(params['g']), buckling_curve=params['Knick'], nos=profile_nos)

        strut_selected['profile_id'] = profile_id
        strut_selected['cross_section'] = cross_section
        strut_selected['nos'] = profile_nos

        if to_be_assigned:
            strut_selected['assigned'] = True
        #else:
        #    strut_selected['assigned'] = False
        
        # update the rest
        self.update_the_rest(strut_selected, cross_section)


    def respond_to_profile_number_change(self, profile_nos):
        """ Responds to change in tube number
        """
        # which strut is selected?
        position = self.ui.comboBox_2.currentText()
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break

        strut_selected['nos'] = int(profile_nos)   # number of profiles
        cross_section = strut_selected['cross_section']

        # read current tube name
        tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()

        # change of profile number leads to change in design loads also, so update them
        self.update_internal_forces_design(strut_selected, cross_section)

        # instantiate cross section
        if isinstance(cross_section, SteelTube):
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\tubes\\jsons', tube_name + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            cross_section = SteelTube(self.fyk, self.PSFs[self.design_situation], float(params['D']), float(params['t']), float(params['A']), float(params['Sy']), float(params['I']), float(params['W']),
                                float(params['G']), buckling_curve=params['Knick'], nos=int(profile_nos))

        elif isinstance(cross_section, SteelProfile):
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', tube_name + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            cross_section = SteelProfile(self.fyk, self.PSFs[self.design_situation], strut_selected['design_loads'], float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                                float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                                float(params['g']), buckling_curve=params['Knick'], nos=int(profile_nos))

        # store cross-section
        strut_selected['cross_section'] = cross_section

        # update the rest
        self.update_the_rest(strut_selected, cross_section)


    def respond_to_distance_beam2beam(self):
        """ Responds to change in distance beam to beam
        """
        # read current beam to beam distance
        d_b2b = float(self.ui.tableWidget_3.cellWidget(2, 0).text())

        # read current tube name
        tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()

        # read current profile numbers
        profile_nos = int(self.ui.tableWidget_3.cellWidget(1, 0).currentText())

        # which strut is selected?
        position = self.ui.comboBox_2.currentText()
        for strut in self.Struts:
            if (strut['position'][1] == float(position)):
                strut_selected = strut
                break

        # instantiate cross section
        if isinstance(strut_selected['cross_section'], SteelTube):
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\tubes\\jsons', tube_name + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            cross_section = SteelTube(self.fyk, self.PSFs[self.design_situation], float(params['D']), float(params['t']), float(params['A']), float(params['Sy']), float(params['I']), float(params['W']),
                                float(params['G']), buckling_curve=params['Knick'], nos=int(profile_nos), distance_beam2beam=float(d_b2b))

        elif isinstance(strut_selected['cross_section'], SteelProfile):
            json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', tube_name + '.json')
            with open(json_item, "r") as read_file:
                params = json.load(read_file, object_pairs_hook = OrderedDict)
            cross_section = SteelProfile(self.fyk, self.PSFs[self.design_situation], strut_selected['design_loads'], float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                                float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                                float(params['g']), buckling_curve=params['Knick'], nos=int(profile_nos), distance_beam2beam=float(d_b2b))

        # store cross-section
        strut_selected['cross_section'] = cross_section
        strut_selected['distance_beam2beam'] = d_b2b

        # update the rest
        self.update_the_rest(strut_selected, cross_section)
    


    def update_the_rest(self, strut_selected, cross_section):
        """ Update dependent values upon change of tube's cross-section
        """
        self.ui.tableWidget_3.cellWidget(2, 0).setText(str(cross_section.distance_beam2beam))
        if strut_selected['strut_type'] == 'SteelTube':
            row_labels = ["Tube ID", "No.", "Dist. beam2beam [mm]", "D [mm]", "t [mm]", "A [cm^2]", "Iyy [cm^4]", "Izz [cm^4]", "W_el_y [cm^3]", "W_el_z [cm^3]", "W_pl_y [cm^3]", "W_pl_z [cm^3]", "N_pl,d [kN]", "M_pl,d,y [kNm]", "M_pl,d,z [kNm]", "g [kN/m]", "p [kN/m]"]
            self.ui.tableWidget_3.setRowCount(len(row_labels))
            self.ui.tableWidget_3.setColumnCount(1)
            self.ui.tableWidget_3.setVerticalHeaderLabels(row_labels)
            items_to_list = ['D', 't', 'A', 'Iyy', 'Izz', 'W_el_y', 'W_el_z', 'W_pl_y', 'W_pl_z', 'N_pl_d', 'M_pl_d_y', 'M_pl_d_z', 'g', 'p']
            for i, item in enumerate(items_to_list):
                self.ui.tableWidget_3.setItem(0, i+3, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))

            self.update_internal_forces_design(strut_selected, cross_section)
            self.update_cross_section_class(cross_section)
            #if strut_selected['assigned']:
            try:
                self.update_flexural_buckling(strut_selected, cross_section)
                self.update_lateral_torsional_buckling(strut_selected, cross_section) # only clear the table
            except:
                pass

        elif strut_selected['strut_type'] == 'SteelProfile':
            row_labels = ["Profile ID", "No.", "Dist. beam2beam [mm]", "h [mm]", "b [mm]", "tw [mm]", "tf [mm]", "r [mm]", "A [cm^2]", "Iyy [cm^4]", "Izz [cm^4]", "Itor [cm^4]", "Iw [cm^6]", "W_el_y [cm^3]", "W_el_z [cm^3]", "W_pl_y [cm^3]", "W_pl_z [cm^3]", "N_pl,d [kN]", "M_pl,d,y [kNm]", "M_pl,d,z [kNm]", "g [kN/m]", "p [kN/m]"]
            self.ui.tableWidget_3.setRowCount(len(row_labels))
            self.ui.tableWidget_3.setColumnCount(1)
            self.ui.tableWidget_3.setVerticalHeaderLabels(row_labels)
            items_to_list = ['h', 'b', 'tw', 'tf', 'r', 'A', 'Iyy', 'Izz', 'Itor', 'Iw','W_el_y', 'W_el_z', 'W_pl_y', 'W_pl_z', 'N_pl_d', 'M_pl_d_y', 'M_pl_d_z', 'g', 'p']
            for i, item in enumerate(items_to_list):
                self.ui.tableWidget_3.setItem(0, i+3, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
            self.update_internal_forces_design(strut_selected, cross_section)
            self.update_cross_section_class(cross_section, strut_selected['design_loads'])
            #if strut_selected['assigned']:
            try:
                self.update_flexural_buckling(strut_selected, cross_section)
                self.update_lateral_torsional_buckling(strut_selected, cross_section)
            except:
                pass



    def update_cross_section_class(self, cross_section, design_loads=None):
        """ Updates cross section class
        Design loads are needed for updating the class section of H-profile
        """
        if isinstance(cross_section, SteelTube):
            row_labels = ['QK [-]', 'epsilon [-]', 'd/t [-]', 'd/t zul. [-]']
            items_to_list = ['QK', 'epsilon', 'd_over_t', 'd_over_t_zul']
            self.ui.tableWidget_7.setRowCount(len(items_to_list))
            self.ui.tableWidget_7.setColumnCount(1)
            self.ui.tableWidget_7.setVerticalHeaderLabels(row_labels)
            for i, item in enumerate(items_to_list):
                if item == 'QK':
                    self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{}'.format(getattr(cross_section, item))))
                else:
                    self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
            #self.ui.tableWidget_7.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.epsilon)))
            #self.ui.tableWidget_7.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.D/cross_section.t)))
            #self.ui.tableWidget_7.setItem(2, 0, QtWidgets.QTableWidgetItem('{}'.format(cross_section.cross_section_class)))
        elif isinstance(cross_section, SteelProfile):
            # update cross-section class based on the current design loads devided by the number of beams
            design_loads_cross_section_classification = {}
            for key, value in design_loads.items():
                design_loads_cross_section_classification[key] = value/cross_section.nos
            cross_section.QK, cross_section.QK_w, cross_section.QK_f = cross_section.get_cross_section_class(design_loads_cross_section_classification)
            #row_labels = []
            row_labels = ['QK [-]', 'QK_web [-]', 'QK_flange [-]', 'epsilon [-]', 'alpha_web [-]', 'c/tw [-]', 'c/tw zul. [-]', 'sigma_1_web [kN/cm^2]', 'sigma_2_web [kN/cm^2]', 'psi_web [-]', 'c/tf [-]', 'c/tf zul. [-]']
            items_to_list = ['QK', 'QK_w', 'QK_f', 'epsilon', 'alpha_web', 'c_over_tw', 'c_over_tw_zul', 'sigma_1_web', 'sigma_2_web', 'psi_web', 'c_over_tf', 'c_over_tf_zul']

            # display additional parameters
            if abs(cross_section.design_loads['Mzd']) > 0.01 and cross_section.nos == 1:
                row_labels_additional = ['alpha_f [LO, RO, LU, RU]', 'psi_f [LO, RO, LU, RU]', 'simga_f [LO, RO, LU, RU]', 'k_sigma_f [LO, RO, LU, RU]']
                items_to_list_additinal = ['alpha_f_all', 'psi_f_all', 'sigma_f_all', 'k_sigma_f_all']
                row_labels += row_labels_additional
                items_to_list += items_to_list_additinal

            self.ui.tableWidget_7.setRowCount(len(items_to_list))
            self.ui.tableWidget_7.setColumnCount(1)
            self.ui.tableWidget_7.setVerticalHeaderLabels(row_labels)
            #self.ui.tableWidget_7.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.epsilon)))
            ##self.ui.tableWidget_7.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.D/cross_section.t)))
            #self.ui.tableWidget_7.setItem(2, 0, QtWidgets.QTableWidgetItem('{}'.format(cross_section.cross_section_class)))
            for i, item in enumerate(items_to_list):
                if item in ['QK', 'QK_w', 'QK_f']:
                    self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{}'.format(getattr(cross_section, item))))
                elif item in ['alpha_f_all', 'psi_f_all', 'sigma_f_all', 'k_sigma_f_all']:
                    self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{}'.format(getattr(cross_section, item))))
                else:
                    self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))


    def update_internal_forces_design(self, strut_selected, cross_section):
        """ Updates design internal forces
        """
        # axial force
        Nk = strut_selected['F_strut']/math.cos(strut_selected['slope_vert']*math.pi/180)/math.cos(strut_selected['slope_horiz']*math.pi/180)
        Nd = Nk*self.PSFs[self.design_situation]['permanent']
        # bending moments
        g = cross_section.G * 0.01  # tube self-weight, kN/m
        p = cross_section.p*self.PSFs[self.design_situation]['transient']/self.PSFs[self.design_situation]['permanent']
        if isinstance(cross_section, SteelTube):
            Myk = (g+p)*math.cos(strut_selected['slope_vert']*math.pi/180)*strut_selected['buckling length sy']**2 / 8 + Nk*strut_selected['eccentricity e/h']*cross_section.D/1000
            Mzd = Nd*strut_selected['eccentricity e/b']*cross_section.D/1000
        elif isinstance(cross_section, SteelProfile):
            Myk = (g+p)*math.cos(strut_selected['slope_vert']*math.pi/180)*strut_selected['buckling length sy']**2 / 8 + Nk*strut_selected['eccentricity e/h']*cross_section.h/1000
            Mzd = Nd*strut_selected['eccentricity e/b']*cross_section.h/1000
            if cross_section.nos > 1: # only for 2xH tube
                cross_section.get_N_cr(strut_selected['buckling length sy'], strut_selected['buckling length sz'])  # make N_cr_zz ready for the next code line
                Mzd += Nd*strut_selected['buckling length sz'] / 500 / (1.0 - Nd/(cross_section.N_cr_zz/self.PSFs[self.design_situation]['gamma_M1']))

        Myd = Myk*self.PSFs[self.design_situation]['permanent']
        #Mzd = Mzk*self.PSFs[self.design_situation]['permanent']

        # show updated internal forces in table
        self.ui.tableWidget_4.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(Nd)))
        self.ui.tableWidget_4.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(Myd)))
        self.ui.tableWidget_4.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(Mzd)))

        # store design loads
        strut_selected['design_loads']['Nd'] = Nd
        strut_selected['design_loads']['Myd'] = Myd
        strut_selected['design_loads']['Mzd'] = Mzd


    
    def update_flexural_buckling(self, strut_selected, cross_section):
        """ Updates calculation for flexural buckling
        """
        # get additional cross section data for design
        sy = strut_selected['buckling length sy']
        sz = strut_selected['buckling length sz']
        cross_section.get_additional_data_for_design(sy, sz, strut_selected['design_loads'])

        self.ui.tableWidget_5.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.alpha_pl_y)))
        self.ui.tableWidget_5.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.alpha_pl_z)))
        self.ui.tableWidget_5.setItem(0, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.alpha_y)))
        self.ui.tableWidget_5.setItem(1, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.alpha_z)))
        self.ui.tableWidget_5.setItem(0, 2, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.N_cr_yy)))
        self.ui.tableWidget_5.setItem(1, 2, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.N_cr_zz)))
        self.ui.tableWidget_5.setItem(0, 3, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.lambda_bar_yy)))
        self.ui.tableWidget_5.setItem(1, 3, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.lambda_bar_zz)))
        self.ui.tableWidget_5.setItem(0, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.chi_yy)))
        self.ui.tableWidget_5.setItem(1, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.chi_zz)))
        self.ui.tableWidget_5.setItem(0, 5, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.N_pl_Rd)))
        self.ui.tableWidget_5.setItem(1, 5, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.N_pl_Rd)))
        self.ui.tableWidget_5.setItem(0, 6, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.k_yy)))
        self.ui.tableWidget_5.setItem(1, 6, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.k_zz)))
        self.ui.tableWidget_5.setItem(0, 7, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.M_pl_Rd_y)))
        self.ui.tableWidget_5.setItem(1, 7, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.M_pl_Rd_z)))

        # display design checks
        self.ui.tableWidget_5.setItem(0, 8, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_N_d_y)))
        self.ui.tableWidget_5.setItem(1, 8, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_N_d_z)))
        self.ui.tableWidget_5.setItem(0, 9, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_M_d_y)))
        self.ui.tableWidget_5.setItem(1, 9, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_M_d_z)))
        self.ui.tableWidget_5.setItem(0, 10, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_total_y)))
        self.ui.tableWidget_5.setItem(1, 10, QtWidgets.QTableWidgetItem('{:.2f}'.format(cross_section.util_total_z)))
        # set colors
        if cross_section.util_total_y > 1.0:
            self.ui.tableWidget_5.item(0, 10).setForeground(QBrush(QColor(255, 0, 0)))
        else:
            self.ui.tableWidget_5.item(0, 10).setForeground(QBrush(QColor(0, 0, 255)))
        if cross_section.util_total_z > 1.0:
            self.ui.tableWidget_5.item(1, 10).setForeground(QBrush(QColor(255, 0, 0)))
        else:
            self.ui.tableWidget_5.item(1, 10).setForeground(QBrush(QColor(0, 0, 255)))


    def update_lateral_torsional_buckling(self, strut_selected, cross_section):
        """ Updates calculation for lateral torsional buckling
        """
        if isinstance(cross_section, SteelProfile):
            # perform design checks
            sy = strut_selected['buckling length sy']
            sz = strut_selected['buckling length sz']
            cross_section.perform_design_checks_lateral_torsional_buckling(strut_selected['design_loads'], sy, sz)

            column_labels_lat_tors_buckling = ["moment coeff. zeta [-]", "torsional radius c^2 [m^2]", "M_cr [kNm]", "slendern. lambda_LT [-]",
                                                "reduct. factor chi_LT [-]", "reduct. factor k_yz [-]", "reduct. factor k_zy [-]", "N_d/(chi*N_pl_Rd)", "My_d*kyy/(My_pl_d)", "Mz_d*kyz/(Mz_pl_d)", "Total utilization"]
            items_to_list = ['c_LT', 'c2', 'M_cr', 'lambda_LT', 'chi_LT_z', 'kyz', 'kzy', 'util_N_d', 'util_M_d_y', 'util_M_d_z', 'util_total']
            self.ui.tableWidget_6.setColumnCount(len(column_labels_lat_tors_buckling))
            self.ui.tableWidget_6.setRowCount(1)
            self.ui.tableWidget_6.setHorizontalHeaderLabels(column_labels_lat_tors_buckling)
            for i, item in enumerate(items_to_list):
                self.ui.tableWidget_6.setItem(0, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
                if item == 'util_total':
                    if cross_section.util_total > 1.0:
                        self.ui.tableWidget_6.item(0, i).setForeground(QBrush(QColor(255, 0, 0)))
                    else:
                        self.ui.tableWidget_6.item(0, i).setForeground(QBrush(QColor(0, 0, 255)))


        elif isinstance(cross_section, SteelTube):
            # lateral torsional buckling does not apply, clear table
            self.ui.tableWidget_6.clear()


    def print_report(self):
        """ Prints PDF report
        """
        try:
            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        except KeyError: # no project folder exists
            MONIMAN_OUTPUTS = '.'

        try:
            pages = []
            for strut in self.Struts:
                page_i = Report()
                page_i.add_project_info(self.project_title, self.design_situation, self.fyk)
                page_i.add_strut_layer_info(strut, self.design_situation,self.PSFs[self.design_situation])
                pages.append(page_i)

        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured! Please make sure that all strut layers are designed.".format(e))

        # dim all pages
        try:    
            filename = os.path.join(MONIMAN_OUTPUTS, 'Design of Struts' + '.pdf')
            pp = PdfPages(filename)
            for page_i in pages:
                page_i.fig.savefig(pp, format='pdf', bbox_inches='tight')

            pp.close()
            # view report in Acrobat Reader
            cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
            cmd.append(filename)
            subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)
            
            return int(0)

        except PermissionError:
            return filename