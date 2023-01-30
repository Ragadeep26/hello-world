# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 13:04:14 2023

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
from gui.gui_widget_Dim_waler import Ui_Form as DimForm
from dimensioning.walers.waler_concrete import walerConcrete
from dimensioning.struts.steel_profile import SteelProfile
from dimensioning.walers.report import Report
from matplotlib.backends.backend_pdf import PdfPages

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

class Dim_waler(QtWidgets.QWidget):
    """ This class implements dimensioning tool for struts
    """
    def __init__(self, form, project_title, Struts, Anchors, design_situation='BS-P: Persistent'):
        super(Dim_waler, self).__init__()
        self.ui = DimForm()
        self.ui.setupUi(form)
        self.dialog = Ui_Dialog()
        self.project_title = project_title

        self.Struts = Struts
        self.Anchors = Anchors

        self.PSFs = PSFs
        self.design_situation = design_situation
        # display design situation
        design_situations = ['BS-P: Persistent', 'BS-T: Transient', 'BS-A: Accidential', 'BS-E: Seismic']
        self.ui.comboBox.setCurrentIndex(design_situations.index(self.design_situation))

        # initialize table for PSFs
        self.initialize_table_psf()

        # fill table for struts and anchors
        self.fill_table_struts_anchors()

        # fill table cross-section
        self.fill_table_cross_section()

        # connect signals and update basic settings once
        self.connect_signals_to_slots()

        # show current settings for the first waler layer once
        position = self.ui.comboBox_2.currentText()
        self.update_waler_layer(position)

        form.exec_()


    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.comboBox.currentTextChanged.connect(self.update_design_situation)
        self.ui.tableWidget.cellChanged.connect(lambda row, column: self.update_with_custom_value_psf(row, column))
        self.ui.tableWidget_3.cellChanged.connect(lambda row, column: self.update_cross_section(row, column))
        self.ui.tableWidget_2.cellChanged.connect(lambda row, column: self.update_with_custom_value_strut_or_anchor(row, column))
        self.ui.comboBox_2.currentTextChanged.connect(self.update_waler_layer)  # waler layer selection
        self.ui.radioButton.clicked.connect(self.update_waler_type)         # receive the signal clicked() from two radio buttons instead of toggled() because signal from radio buttons cannot be disabled
        self.ui.radioButton_2.clicked.connect(self.update_waler_type)
        self.ui.tableWidget_5.cellChanged.connect(lambda row, column: self.update_user_reinforcement_vertical(row, column))
        self.ui.tableWidget_6.cellChanged.connect(lambda row, column: self.update_user_reinforcement_shear(row, column))
        self.ui.pushButton.clicked.connect(self.print_report) # print report


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

        ## refresh the rest
        self.fill_table_cross_section()     # also updates internal forces for design
        #position = self.ui.comboBox_2.currentText()
        #self.update_strut_layer(position)
        #tube_name = self.ui.tableWidget_3.cellWidget(0, 0).currentText()
        #self.respond_to_profile_id_selection(tube_name)


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
                    self.update_waler_layer(position)

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


    def fill_table_struts_anchors(self):
        """ Fills table for struts and anchors
        """
        Structures = self.Anchors + self.Struts
        Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
        self.Structures = Structures_sorted
        for structure in Structures_sorted:
            if 'F_strut' in structure:  # it's a strut
                #structure['F_support'] = structure['F_strut']
                structure['slope_vert'] = math.atan(abs(structure['direct_y'])/abs(structure['direct_x']))*180/math.pi  # deg, newly introduced
            else:   # it's an anchor
                #structure['F_support'] = structure['F_anchor']
                structure['slope_vert'] = structure['angle']

        items_to_list = ['position', 'Lspacing', 'F_support', 'slope_vert', 'waler_width_support', 'waler_width_influence']
        items_to_list_with_units = ['Waler y level [mNN]', 'Lspacing support [m]', 'F_support [kN]', 'slope vert. support [deg.]', 'width of support [m]', 'width of influence [m]']
        self.ui.tableWidget_2.setColumnCount(len(items_to_list_with_units))
        self.ui.tableWidget_2.setHorizontalHeaderLabels(items_to_list_with_units)
        self.ui.tableWidget_2.setRowCount(len(self.Structures))
        for i, structure in enumerate(self.Structures):
            for j, item in enumerate(items_to_list):
                if item == 'position': # display only y level
                    self.ui.tableWidget_2.setItem(i, j, QtWidgets.QTableWidgetItem(str(structure[item][1])))
                else:
                    self.ui.tableWidget_2.setItem(i, j, QtWidgets.QTableWidgetItem(str(structure[item])))
                # mark editable items with yellow
                items_editable = ['Lspacing', 'F_support', 'waler_width_support', 'waler_width_influence']
                if item in items_editable:
                    self.ui.tableWidget_2.item(i, j).setBackground(QColor(242, 255, 116))
        
        # list waler levels, which are levels of support structures
        positions_structure = [structure['position'] for structure in self.Structures]
        for position in positions_structure:
            position_id = '{}'.format(position[1])  # strut is indexed by level
            self.ui.comboBox_2.addItem(position_id)
    

    def update_with_custom_value_strut_or_anchor(self, row, column):
        """ Updates a custom value for waler parameters, which belong to strut or anchor support structure
        """
        text = self.ui.tableWidget_2.item(row, column).text()
        if text != '':
            try:
                # reference strut by level
                y_level = float(self.ui.tableWidget_2.item(row, 0).text())
                for structure in self.Structures:
                    if (structure['position'][1] == float(y_level)):
                        structure_selected = structure
                        break
                self.read_parameters_strut_or_anchor(structure_selected, row, column)  # read and store parameter values

                # refresh the rest
                # update internal forces for design
                position = self.ui.comboBox_2.currentText() # currently shown position
                if structure_selected['position'][1] == float(position): # update the rest only if the updated strut/ anchor is coincident with the currently activated waler layer
                    self.update_internal_forces_design(structure_selected)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))
    
        else: # text is empty, set back stored values
            self.fill_table_struts_anchors()


    def read_parameters_strut_or_anchor(self, strut, row, column):
        """ Reads strut parameter from table for the selected strut or anchor
        """
        items_to_list = ['position', 'Lspacing', 'F_support', 'slope_vert', 'waler_width_support', 'waler_width_influence']
        items_editable = ['Lspacing', 'F_support', 'waler_width_support', 'waler_width_influence']
        value = float(self.ui.tableWidget_2.item(row, column).text())
        if items_to_list[column] in items_editable:
            strut[items_to_list[column]] = value


    def update_waler_layer(self, position):
        """ Updates strut selection based on strut level
        """
        # which strut is selected?
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        # display waler type on radio button
        if waler_selected['waler_type'] == 'concrete':
            self.ui.radioButton.setChecked(True)
            self.ui.radioButton_2.setChecked(False)
        elif waler_selected['waler_type'] == 'steel_profile':
            self.ui.radioButton.setChecked(False)
            self.ui.radioButton_2.setChecked(True)
        
        # fill table cross-section and update design loads
        self.fill_table_cross_section()



    def fill_table_cross_section(self):
        """ Fills table for cross section of the waler beam.
        Waler beam can be concrete beam or steel profile beam
        """
        # which structure (level) is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        if waler_selected['waler_type'] == 'concrete':
            items_to_list = ['b', 'h', 'edge_sep', 'fck', 'fyk']
            items_to_list_with_unit = ['waler beam width [m]', 'waler beam height [m]', 'concrete cover [mm]', 'fc,k [MPa]', 'fy,k [MPa]']
            self.ui.tableWidget_3.clear()   # clear table to remove cellWidget(0, 0)
            self.ui.tableWidget_3.blockSignals(True)
            self.ui.tableWidget_3.setRowCount(len(items_to_list))
            self.ui.tableWidget_3.setColumnCount(1)
            self.ui.tableWidget_3.setVerticalHeaderLabels(items_to_list_with_unit)
            for j, item in enumerate(items_to_list):
                self.ui.tableWidget_3.setItem(j, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(waler_selected['waler_concrete'][item])))
                self.ui.tableWidget_3.item(j, 0).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget_3.blockSignals(False)

        elif waler_selected['waler_type'] == 'steel_profile':
            items_to_list = ['profile_id', 'nos', 'fyk']
            items_to_list_with_unit = ['profile ID [-]', 'No. [-]', 'fy,k [MPa]']
            self.ui.tableWidget_3.clear()   # clear table to remove cellWidget(0, 0)
            self.ui.tableWidget_3.blockSignals(True)
            self.ui.tableWidget_3.setRowCount(len(items_to_list))
            self.ui.tableWidget_3.setColumnCount(1)
            self.ui.tableWidget_3.setVerticalHeaderLabels(items_to_list_with_unit)
            for j, item in enumerate(items_to_list):
                if j == 0:
                    profile_names = self.get_steel_profile_names()
                    combobox = QtWidgets.QComboBox()
                    combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
                    for name in profile_names:
                        combobox.addItem(name)
                    # show current profile id
                    profile_id_index = profile_names.index(waler_selected['waler_steel_profile']['profile_id'])
                    combobox.setCurrentIndex(profile_id_index)
                    # set property and connect signal to slot
                    combobox.setProperty('profile_id', 0)
                    combobox.activated[str].connect(lambda profile_id: self.respond_to_profile_id_selection(profile_id))
                    self.ui.tableWidget_3.setCellWidget(0, 0, combobox)
                else:
                    self.ui.tableWidget_3.setItem(j, 0, QtWidgets.QTableWidgetItem('{}'.format(waler_selected['waler_steel_profile'][item])))
                    self.ui.tableWidget_3.item(j, 0).setBackground(QColor(242, 255, 116))

            # display profile parameters
            self.display_parameters_steel_profile(waler_selected)

            self.ui.tableWidget_3.blockSignals(False)

        # update internal forces for design
        self.update_internal_forces_design(waler_selected)
            

    def get_steel_profile_names(self):
        """ Gets available steel profile names
        strut_type: a string whose value is either 'SteelTube' or 'SteelProfile'
        """
        PATH_PROFILES = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons')
        profile_names = []
        for item in glob.glob(PATH_PROFILES + '\\*'):
            profile_name = os.path.basename(item)
            profile_names.append(profile_name[:-5]) # no file ending '.json'
        
        return profile_names


    def respond_to_profile_id_selection(self, profile_id):
        """ Responds to profile id selection
        """
        # which waler is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        waler_selected['waler_steel_profile']['profile_id'] = profile_id

        # display profile parameters
        self.display_parameters_steel_profile(waler_selected)

        # update internal forces for design
        self.update_internal_forces_design(waler_selected)


    def display_parameters_steel_profile(self, waler_selected):
        """ Displays steel profile parameters
        """
        # list cross-section parameters
        profile_id = waler_selected['waler_steel_profile']['profile_id']
        profile_nos = waler_selected['waler_steel_profile']['nos']
        profile_fyk = waler_selected['waler_steel_profile']['fyk']
        json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', profile_id + '.json')
        with open(json_item, "r") as read_file:
            params = json.load(read_file, object_pairs_hook = OrderedDict)
        design_loads = {'Nd':  waler_selected['design_loads']['Nd'] ,'Myd':waler_selected['design_loads']['Msd'], 'Mzd': 0.0}
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


    def update_waler_type(self):
        """ Updates waler type
        """
        # which waler is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break
        if self.ui.radioButton.isChecked() is True:
            waler_selected['waler_type'] = 'concrete'
        elif self.ui.radioButton_2.isChecked() is True:
            waler_selected['waler_type'] = 'steel_profile'
        
        # fill table for cross_section
        #strut_selected['assigned'] = False  # set assigned as False when switching strut type
        self.fill_table_cross_section()



    def update_cross_section(self, row, column):
        """ Updates cross section
        """
        # which waler is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        try:
            if self.ui.radioButton.isChecked() is True:     # update parameters for concrete beam cross-section
                self.read_parameters_cross_section_concrete(waler_selected, row, column)
            elif self.ui.radioButton_2.isChecked() is True: # update parameters for steel profile beam cross-section
                self.read_parameters_cross_section_steel_profile(waler_selected, row, column)
            
            # update internal forces for design
            self.update_internal_forces_design(waler_selected)

        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))
    

    def read_parameters_cross_section_concrete(self, waler, row, column):
        """ Reads/ stores parameter for concrete beam's cross section
        """
        items_to_list = ['b', 'h', 'edge_sep', 'fck', 'fyk']
        value = float(self.ui.tableWidget_3.item(row, column).text())
        waler['waler_concrete'][items_to_list[row]] = value
        

    def read_parameters_cross_section_steel_profile(self, waler, row, column):
        """ Reads/ stores parameter for steel profile beam's cross section
        """
        items_to_list = ['profile_id', 'nos', 'fyk']
        if row == 0:    # change in profile id, already handled by cellWidget signal
            pass
        elif row == 1: # nos
            value = int(self.ui.tableWidget_3.item(row, column).text())
        elif row == 2: # fck
            value = float(self.ui.tableWidget_3.item(row, column).text())
        waler['waler_steel_profile'][items_to_list[row]] = value

        # display profile parameters
        self.display_parameters_steel_profile(waler)


    def update_internal_forces_design(self, waler_selected):
        """ Updates design internal forces
        distributed multi-span load
        """
        if waler_selected['waler_type'] == 'concrete':
            self.update_internal_forces_design_concrete_beam(waler_selected)
        elif waler_selected['waler_type'] == 'steel_profile':
            self.update_internal_forces_design_steel_beam(waler_selected)

        # list design loads on table
        row_labels_loads = ["Ms_d [kNm]", "Mf_d [kNm]", "Vd [kN]", "Nd [kN]"]
        self.ui.tableWidget_4.setRowCount(len(row_labels_loads))
        self.ui.tableWidget_4.setColumnCount(1)
        self.ui.tableWidget_4.setVerticalHeaderLabels(row_labels_loads)
        self.ui.tableWidget_4.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(waler_selected['design_loads']['Msd'])))
        self.ui.tableWidget_4.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(waler_selected['design_loads']['Mfd'])))
        self.ui.tableWidget_4.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(waler_selected['design_loads']['Vd'])))
        self.ui.tableWidget_4.setItem(3, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(waler_selected['design_loads']['Nd'])))


    def update_internal_forces_design_steel_beam(self, waler_selected):
        """ Updates design internal forces for steel profile beam
        distributed multi-span load
        """
        A = waler_selected['F_support']     # support force, kN
        a = waler_selected['Lspacing']
        Msd = -(self.PSFs[self.design_situation]['permanent']*A*a*1.0/8 - A*(0.9**2)*1.0/16)
        Mfd = -Msd
        Vd = self.PSFs[self.design_situation]['permanent']*A*1/2 - A/a*waler_selected['waler_width_support']*1.0/2
        V1d = 0.0
        Nd = self.PSFs[self.design_situation]['permanent']*A/a*waler_selected['waler_width_influence']
        design_loads = {'Msd': Msd, 'Mfd': Mfd, 'Vd': Vd, 'V1d': V1d, 'Nd': Nd} # Nd: positive is compression
        waler_selected['design_loads'] = design_loads

        # classify cross-section
        self.get_cross_section_class(waler_selected)


    def update_internal_forces_design_concrete_beam(self, waler_selected):
        """ Updates design internal forces for concrete beam
        distributed multi-span load
        """
        A = waler_selected['F_support']     # support force, kN
        a = waler_selected['Lspacing']
        Msd = self.PSFs[self.design_situation]['permanent']*(A*a*0.9/12 - A*waler_selected['waler_width_support']*1.0/8)
        Mfd = self.PSFs[self.design_situation]['permanent']*(A*a*1.0/8 - A*a*0.9/12)
        Vd = self.PSFs[self.design_situation]['permanent']*(a/2 - waler_selected['waler_width_support']/2 - waler_selected['waler_concrete']['h'] + waler_selected['waler_concrete']['edge_sep']*0.001)/a * A
        Nd = -1.0*A/a*waler_selected['waler_width_influence']
        design_loads = {'Msd': Msd, 'Mfd': Mfd, 'Vd': Vd, 'Nd': Nd} # Nd: negative is compression
        waler_selected['design_loads'] = design_loads
    
        # calculate the required reinforcements
        self.calc_required_reinforcements_concrete_beam(waler_selected)



    def calc_required_reinforcements_concrete_beam(self, waler_selected):
        """ Calculates the required reinforcements for concrete waler beam
        """
        waler = walerConcrete(psf=self.PSFs[self.design_situation], **waler_selected['waler_concrete'])
        # required reinforcement caused by Msd
        design_loads_Msd = {'Nd': waler_selected['design_loads']['Nd'], 'Myd': waler_selected['design_loads']['Msd'], 'Vd': waler_selected['design_loads']['Vd']}
        design_loads_Mfd = {'Nd': waler_selected['design_loads']['Nd'], 'Myd': waler_selected['design_loads']['Mfd'], 'Vd': waler_selected['design_loads']['Vd']}
        AsE_Msd, AsL_Msd, as_Msd = waler.get_required_reinforcements(design_loads_Msd['Nd'], design_loads_Msd['Myd'], design_loads_Msd['Vd'])
        # required reinforcement caused by Mfd
        AsL_Mfd, AsE_Mfd, as_Mfd = waler.get_required_reinforcements(design_loads_Mfd['Nd'], design_loads_Mfd['Myd'], design_loads_Mfd['Vd'])
        AsE = max(abs(AsE_Msd), abs(AsE_Mfd))
        AsL = max(abs(AsL_Msd), abs(AsL_Mfd))
        a_s = max(as_Msd, as_Mfd)
        #print('AsE = {0} cm^2, AsL = {1} cm^2, a_s = {2} cm^2/m'.format(AsE, AsL, a_s))

        # store required reinforcement for report generation
        waler_selected['waler_concrete_reinf_required'] = {'AsE': AsE, 'AsL': AsL, 'a_s': a_s}

        # display the required reinforcements on table
        row_labels = ["As_E earth side [cm^2]", "As_L air side [cm^2]", "a_s [cm^2/m]"]
        self.ui.groupBox_8.setTitle('Required reinforcements')
        self.ui.tableWidget_7.clear()
        self.ui.tableWidget_7.setRowCount(len(row_labels))
        self.ui.tableWidget_7.setColumnCount(1)
        self.ui.tableWidget_7.setVerticalHeaderLabels(row_labels)
        self.ui.tableWidget_7.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(AsE)))
        self.ui.tableWidget_7.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(AsL)))
        self.ui.tableWidget_7.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(a_s)))

        # prepare tables for user reinforcement settings
        self.ui.groupBox_6.setTitle('Main reinforcements')
        self.ui.tableWidget_5.clear()
        self.initialize_table_reinf_vertical(self.ui.tableWidget_5, waler_selected)
        self.ui.groupBox_7.setTitle('Stirrups')
        self.ui.tableWidget_6.clear()
        self.initialize_table_reinf_shear(self.ui.tableWidget_6, waler_selected)

    
    def initialize_table_reinf_vertical(self, table_widget, waler_selected):
        """ Initializes table for vertial reinforcement
        """
        n_row = 2
        table_widget.blockSignals(True)
        table_widget.setRowCount(n_row)
        column_labels = ['n\n [-]', 'Dia.\n [mm]', 'A_s \n [cm^2]', 'Clearance\n [cm]', 'Weight [Kg/m]']
        table_widget.setColumnCount(len(column_labels))
        table_widget.setHorizontalHeaderLabels(column_labels)
        row_labels = ['Earth side', 'Air side']
        table_widget.setVerticalHeaderLabels(row_labels)

        table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(waler_selected['waler_concrete_reinf_As_E']['n'])))
        table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(waler_selected['waler_concrete_reinf_As_E']['dia']))
        table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem(str(waler_selected['waler_concrete_reinf_As_L']['n'])))
        table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(str(waler_selected['waler_concrete_reinf_As_L']['dia'])))

        n_column = len(column_labels)
        for row_i in range(n_row):
            for column_j in range(n_column-3):
                #table_widget.setItem(row_i, column_j, QtWidgets.QTableWidgetItem(''))
                cell = table_widget.item(row_i, column_j)
                cell.setBackground(QColor(242, 255, 116))
        
        # display the stored user input reinforcements once
        self.update_user_reinforcement_vertical(0, 0)

        table_widget.blockSignals(False)


    def initialize_table_reinf_shear(self, table_widget, waler_selected):
        """ Initializes table for shear reinforcement
        """
        n_row = 1
        table_widget.blockSignals(True)
        table_widget.setRowCount(n_row)
        column_labels = ['dia.\n d [mm]', 'n legs\n [-]', 'spacing\n [cm]', 'a_s \n [cm^2/m]', 'Weight [Kg/m]']
        table_widget.setColumnCount(len(column_labels))
        table_widget.setHorizontalHeaderLabels(column_labels)
        row_labels = ['Stirrups']
        table_widget.setVerticalHeaderLabels(row_labels)

        table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem(waler_selected['waler_concrete_reinf_as']['dia']))
        table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(str(waler_selected['waler_concrete_reinf_as']['n_legs'])))
        table_widget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(waler_selected['waler_concrete_reinf_as']['spacing'])))
        n_column = len(column_labels)
        for row_i in range(n_row):
            for column_j in range(n_column-2):
                #table_widget.setItem(row_i, column_j, QtWidgets.QTableWidgetItem(''))
                cell = table_widget.item(row_i, column_j)
                cell.setBackground(QColor(242, 255, 116))

        # display the stored user input reinforcements once
        self.update_user_reinforcement_shear(0, 0)

        table_widget.blockSignals(False)


    def update_user_reinforcement_vertical(self, row, column):
        """ Updates with user input for main reinforcement
        """
        # which waler is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        if waler_selected['waler_type'] == 'concrete':  # applies only for concrete waler beam
            try:
                if (column == 0) or (column == 1):
                    value = self.ui.tableWidget_5.item(row, column).text()
                    if row == 0: # earth side
                        if column == 0: #n
                            waler_selected['waler_concrete_reinf_As_E']['n'] = int(value)
                        else:   # dia
                            waler_selected['waler_concrete_reinf_As_E']['dia'] = value
                    elif row == 1: # air side
                        if column == 0: #n
                            waler_selected['waler_concrete_reinf_As_L']['n'] = int(value)
                        else:   # dia
                            waler_selected['waler_concrete_reinf_As_L']['dia'] = value

                # calculate As, clearance, weight
                waler = walerConcrete(psf=self.PSFs[self.design_situation], **waler_selected['waler_concrete'])
                As_E, clearance_E = waler.calc_A_s(waler_selected['waler_concrete_reinf_As_E']['n'], waler_selected['waler_concrete_reinf_As_E']['dia'])
                weight_E = waler.calc_weight_A_s(As_E, 1.0) # weight of reinforcement steel for 1 m
                As_L, clearance_L = waler.calc_A_s(waler_selected['waler_concrete_reinf_As_L']['n'], waler_selected['waler_concrete_reinf_As_L']['dia'])
                weight_L = waler.calc_weight_A_s(As_L, 1.0) # weight of reinforcement steel for 1 m

                # store proposed reinforcement data for report generation
                waler_selected['waler_concrete_reinf_As_E']['A_s'] = As_E
                waler_selected['waler_concrete_reinf_As_E']['clearance'] = clearance_E
                waler_selected['waler_concrete_reinf_As_E']['weight'] = weight_E
                waler_selected['waler_concrete_reinf_As_L']['A_s'] = As_L
                waler_selected['waler_concrete_reinf_As_L']['clearance'] = clearance_L
                waler_selected['waler_concrete_reinf_As_L']['weight'] = weight_L

                # display values on table
                self.ui.tableWidget_5.blockSignals(True)
                self.ui.tableWidget_5.setItem(0, 2, QtWidgets.QTableWidgetItem('{:.2f}'.format(As_E)))
                self.ui.tableWidget_5.setItem(0, 3, QtWidgets.QTableWidgetItem('{:.2f}'.format(clearance_E)))
                self.ui.tableWidget_5.setItem(0, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(weight_E)))
                self.ui.tableWidget_5.setItem(1, 2, QtWidgets.QTableWidgetItem('{:.2f}'.format(As_L)))
                self.ui.tableWidget_5.setItem(1, 3, QtWidgets.QTableWidgetItem('{:.2f}'.format(clearance_L)))
                self.ui.tableWidget_5.setItem(1, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(weight_L)))
                self.ui.tableWidget_5.blockSignals(False)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def update_user_reinforcement_shear(self, row, column):
        """ Updates with user input for shear reinforcement
        """
        # which waler is selected?
        position = self.ui.comboBox_2.currentText()
        for waler in self.Structures:
            if (waler['position'][1] == float(position)):
                waler_selected = waler
                break

        if waler_selected['waler_type'] == 'concrete':  # applies only for concrete waler beam
            try:
                value = self.ui.tableWidget_6.item(row, column).text()
                if column == 0:
                    waler_selected['waler_concrete_reinf_as']['dia'] = value
                elif column == 1:
                    waler_selected['waler_concrete_reinf_as']['n_legs'] = int(value)
                elif column == 2:
                    waler_selected['waler_concrete_reinf_as']['spacing'] = float(value)

                # calculate a_s, weight_a_s
                waler = walerConcrete(psf=self.PSFs[self.design_situation], **waler_selected['waler_concrete'])
                a_s = waler.calc_a_s(waler_selected['waler_concrete_reinf_as']['n_legs'], waler_selected['waler_concrete_reinf_as']['dia'], waler_selected['waler_concrete_reinf_as']['spacing'])
                weight_a_s = waler.calc_weight_a_s(a_s, 1.0, waler_selected['waler_concrete_reinf_as']['n_legs'])

                # store proposed reinforcement data for report generation
                waler_selected['waler_concrete_reinf_as']['a_s'] = a_s
                waler_selected['waler_concrete_reinf_as']['weight'] = weight_a_s

                # display values on table
                self.ui.tableWidget_6.blockSignals(True)
                self.ui.tableWidget_6.setItem(0, 3, QtWidgets.QTableWidgetItem('{:.2f}'.format(a_s)))
                self.ui.tableWidget_6.setItem(0, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(weight_a_s)))
                self.ui.tableWidget_6.blockSignals(False)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your input!".format(e))


    def get_cross_section_class(self, waler_selected):
        """ Gets cross section class
        """
        profile_id = waler_selected['waler_steel_profile']['profile_id']
        profile_nos = waler_selected['waler_steel_profile']['nos']
        profile_fyk = waler_selected['waler_steel_profile']['fyk']
        json_item = os.path.join(sys.modules['moniman_paths']['MONIMAN'],'solver\\plaxis2d\\profile_steels\\jsons', profile_id + '.json')
        with open(json_item, "r") as read_file:
            params = json.load(read_file, object_pairs_hook = OrderedDict)
        # instantiate cross section
        design_loads = {'Nd': waler_selected['design_loads']['Nd'] ,'Myd': waler_selected['design_loads']['Msd'], 'Mzd': 0.0, 'Vd': waler_selected['design_loads']['Vd']}
        cross_section = SteelProfile(profile_fyk, self.PSFs[self.design_situation], design_loads, float(params['h']), float(params['b']), float(params['t-s']), float(params['t-g']), float(params['r']), 
                            float(params['A']), float(params['S-y']), float(params['I-y']), float(params['I-z']), float(params['Itor']), float(params['Iw\\/1000']), float(params['W-y']), float(params['W-z']),
                            float(params['g']), buckling_curve=params['Knick'], nos=profile_nos)

        design_loads_cross_section_classification = {'Nd':  waler_selected['design_loads']['Nd']/profile_nos ,'Myd':waler_selected['design_loads']['Msd']/profile_nos, 'Mzd': 0.0}
        cross_section.QK, cross_section.QK_w, cross_section.QK_f = cross_section.get_cross_section_class(design_loads_cross_section_classification)
        self.ui.groupBox_8.setTitle('Cross-section classification')
        self.ui.tableWidget_7.clear()
        row_labels = ['QK [-]', 'QK_web [-]', 'QK_flange [-]', 'epsilon [-]', 'alpha_web [-]', 'c/tw [-]', 'c/tw zul. [-]', 'sigma_1_web [kN/cm^2]', 'sigma_2_web [kN/cm^2]', 'psi_web [-]', 'c/tf [-]', 'c/tf zul. [-]']
        items_to_list = ['QK', 'QK_w', 'QK_f', 'epsilon', 'alpha_web', 'c_over_tw', 'c_over_tw_zul', 'sigma_1_web', 'sigma_2_web', 'psi_web', 'c_over_tf', 'c_over_tf_zul']
        self.ui.tableWidget_7.setRowCount(len(items_to_list))
        self.ui.tableWidget_7.setColumnCount(1)
        self.ui.tableWidget_7.setVerticalHeaderLabels(row_labels)
        for i, item in enumerate(items_to_list):
            if item in ['QK', 'QK_w', 'QK_f']:
                self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{}'.format(getattr(cross_section, item))))
            else:
                self.ui.tableWidget_7.setItem(i, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(getattr(cross_section, item))))
        
        # store cross-section for report generation
        waler_selected['cross_section'] = cross_section

        # perform interation stress verification
        # Mfs: at span; Msd: at support
        design_loads_Msd = {'Nd': waler_selected['design_loads']['Nd'] ,'Myd': waler_selected['design_loads']['Msd'], 'Mzd': 0.0, 'Vd': waler_selected['design_loads']['Vd']}
        design_loads_Mfd = {'Nd': waler_selected['design_loads']['Nd'] ,'Myd': waler_selected['design_loads']['Mfd'], 'Mzd': 0.0, 'Vd': waler_selected['design_loads']['V1d']}
        if cross_section.QK < 3:
            util_Msd_interaction = cross_section.perform_interaction_stress_verification_QK1_QK2(design_loads_Msd)
            util_Mfd_interaction = cross_section.perform_interaction_stress_verification_QK1_QK2(design_loads_Mfd)
        else: # QK3
            util_Msd_interaction = cross_section.perform_interaction_stress_verification_QK3(design_loads_Msd)
            util_Mfd_interaction = cross_section.perform_interaction_stress_verification_QK3(design_loads_Mfd)

        util_N_f = design_loads_Mfd['Nd']/cross_section.N_pl_d
        util_N_s = design_loads_Msd['Nd']/cross_section.N_pl_d
        util_V_f = design_loads_Mfd['Vd']/cross_section.V_pl_d
        util_V_s = design_loads_Msd['Vd']/cross_section.V_pl_d
        util_M_f = abs(design_loads_Mfd['Myd'])/cross_section.M_pl_d_y
        util_M_s = abs(design_loads_Msd['Myd'])/cross_section.M_pl_d_y

        # store utilization factors for report generation
        waler_selected['steel_profile_utils'] = {'util_N_f': util_N_f, 'util_N_s': util_N_s, 'util_V_f': util_V_f, 'util_V_s': util_V_s,
                                        'util_M_f': util_M_f, 'util_M_s': util_M_s, 'util_Mfd_interaction': util_Mfd_interaction,  'util_Msd_interaction': util_Msd_interaction}

        # display the stress verfication results on table
        self.ui.groupBox_6.setTitle('Stress verifications for steel profile')
        self.ui.tableWidget_5.clear()
        self.ui.groupBox_7.setTitle('') # not used
        self.ui.tableWidget_6.clear()
        self.ui.tableWidget_6.setRowCount(0)
        self.ui.tableWidget_6.setColumnCount(0)
        row_labels = ['N_Ed/N_pl_Rd [-]', 'V_Ed/V_pl_Rd [-]', 'My_Ed/My_pl_Rd [-]', 'Interaction M/N/V [-]']
        column_labels = ['At span Mf,d', 'At support Ms,d']
        self.ui.tableWidget_5.setRowCount(len(row_labels))
        self.ui.tableWidget_5.setColumnCount(len(column_labels))
        self.ui.tableWidget_5.setVerticalHeaderLabels(row_labels)
        self.ui.tableWidget_5.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_5.setItem(0, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_N_f)))
        self.ui.tableWidget_5.setItem(1, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_V_f)))
        self.ui.tableWidget_5.setItem(2, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_M_f)))
        self.ui.tableWidget_5.setItem(3, 0, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_Mfd_interaction)))
        self.ui.tableWidget_5.setItem(0, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_N_s)))
        self.ui.tableWidget_5.setItem(1, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_V_s)))
        self.ui.tableWidget_5.setItem(2, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_M_s)))
        self.ui.tableWidget_5.setItem(3, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(util_Msd_interaction)))
        # set colors
        for row_i in range(4):
            for col_j in range(2):
                value = float(self.ui.tableWidget_5.item(row_i, col_j).text())
                if value > 1.0:
                    self.ui.tableWidget_5.item(row_i, col_j).setForeground(QBrush(QColor(255, 0, 0)))
                else:
                    self.ui.tableWidget_5.item(row_i, col_j).setForeground(QBrush(QColor(0, 0, 255)))


    def print_report(self):
        """ Prints PDF report
        """
        try:
            MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        except KeyError: # no project folder exists
            MONIMAN_OUTPUTS = '.'

        try:
            pages = []
            for waler in self.Structures:
                page_i = Report()
                page_i.add_project_info(self.project_title, self.design_situation)
                page_i.add_waler_layer_info(waler, self.design_situation,self.PSFs[self.design_situation])
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