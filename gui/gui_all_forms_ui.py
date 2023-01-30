# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 09:14:02 2018

@author: nya
"""

import sys, os
#sys.path.append(r'C:\Users\nya\Packages\Moniman')
import numpy as np
import pandas as pd
from collections import OrderedDict
import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from solver.plaxis2d.output_commands import get_plate_outputs, get_soilsection_uy, get_all_anchors_force, get_all_struts_force
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots
from gui.gui_form_output_Wall_ui import Ui_Form as outputWall
from gui.gui_form_output_Soilsection_settlement_ui import Ui_Form as outputSoilsectionSettlement
from gui.gui_form_metamodel_validation_view import Ui_Form as metamodelValidationView
from gui.gui_form_metamodel_prediction import Ui_Form as metamodelPredictionView
from gui.gui_form_About_ui import Ui_Form as formAbout
from gui.gui_form_Literature_ui import Ui_Form as formLiterature
from gui.gui_form_Pareto_front_explorer import Ui_Form as ParetofrontViewer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from common.boilerplate import start_plaxis
from plxscripting.easy import new_server

class Ui_Form(QtWidgets.QWidget):
    """ This class implements all widgets for moniman outputs
    """
    def __init__(self):
        super(Ui_Form, self).__init__()
        
    
    def open_form_About(self):
        """ Opens About text
        """
        form = QtWidgets.QDialog()
        self.about_box = formAbout()
        self.about_box.setupUi(form)
        form.exec_()


    def open_form_Literature(self):
        """ Opens About text
        """
        form = QtWidgets.QDialog()
        self.about_box = formLiterature()
        self.about_box.setupUi(form)
        form.exec_()


    def open_pareto_front_viewer(self, displs, costs):
        """ Opens Pareto front viewer
        Implements matplotlib pick_event here.
        """
        form = QtWidgets.QDialog()
        self.setWindowTitle('Pareto front viewer')
        self.pareto_box = ParetofrontViewer()
        self.pareto_box.setupUi(form)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)

        self.pareto_box.frame.setLayout(layout)
        layout.setContentsMargins(0, 1, 1, 0)#(left, top, right, bottom)

        ax = self.figure.add_subplot(111)
        ax.plot(np.array(displs)*1000, costs, 'o', picker=5)
        #ax.scatter(np.array(displs)*1000, costs, picker=5)

        self.canvas.draw()
        self.figure.canvas.mpl_connect('pick_event', self.on_pick1)

        form.exec_()

    def on_pick(self,  event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        print('Point %d is picked' % ind)
        print('X = ', np.take(xdata, ind)[0]) # Print X point
        print('Y = ', np.take(ydata, ind)[0]) # Print Y point
    
    def on_pick1(self, event):
        artist = event.artist
        xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
        x, y = artist.get_xdata(), artist.get_ydata()
        ind = event.ind
        print('Artist picked:', event.artist)
        print('{} vertices picked'.format(len(ind)))
        print('Pick between vertices {} and {}'.format(min(ind), max(ind)+1))
        print('x, y of mouse: {:.2f},{:.2f}'.format(xmouse, ymouse))
        print('Data point:', x[ind[0]], y[ind[0]])
        print('\n')

    def open_wall_outputs(self, subprocess_plaxis_output, path, s_o, g_o, output_database, x_wall, wall, Anchors, Struts, phasenumber = 1, phasecount = 1):       
        form = QtWidgets.QDialog()
        self.setWindowTitle('Wall outputs')
        self.wall_box = outputWall()
        self.wall_box.setupUi(form)
        self.subprocess_plaxis_output = subprocess_plaxis_output
        self.s_o = s_o
        self.g_o = g_o
        
        self.plot_layout = QtWidgets.QVBoxLayout(self.wall_box.widget)
        self.plot_canvas = MyStaticMplCanvasSubplots(self.wall_box.widget, width=1, height=1, dpi=100, nrows=5, ncols=6)
        self.plot_layout.addWidget(self.plot_canvas)
        
        
        self.wall_box.spinBox.setMinimum(1)
        self.wall_box.spinBox.setMaximum(phasecount)
        self.wall_box.spinBox.setValue(phasenumber)
        
        self.update_wall_outputs(path, output_database, x_wall, wall, Anchors, Struts)
        
        self.wall_box.spinBox.valueChanged.connect(lambda: self.update_wall_outputs(path, output_database, x_wall, wall, Anchors, Struts))

        # prepare directory for wall outputs
        WALL_OUTPUTS = os.path.join(path, 'Outputs_wall_forces')
        SUPPORT_OUTPUTS = os.path.join(path, 'Outputs_support_forces')
        if not os.path.exists(WALL_OUTPUTS):
            os.makedirs(WALL_OUTPUTS)
        if (Anchors or Struts) and not os.path.exists(SUPPORT_OUTPUTS):
            os.makedirs(SUPPORT_OUTPUTS)
        self.wall_box.pushButton.clicked.connect(lambda: self.save_wall_and_support_outputs(WALL_OUTPUTS, SUPPORT_OUTPUTS, Anchors, Struts))
        self.wall_box.pushButton_2.clicked.connect(lambda: self.update_and_save_wall_and_support_outputs_all_phases(path, output_database, x_wall, wall, Anchors, Struts, phasecount))

        form.exec_()

    
    def update_and_save_wall_and_support_outputs_all_phases(self, path, output_database, x_wall, wall, Anchors, Struts, phasecount):
        """ Updates and saves wall and support outputs for all calculation phases
        """
        try:
            # prepare directory for wall outputs
            WALL_OUTPUTS = os.path.join(path, 'Outputs_wall_forces')
            SUPPORT_OUTPUTS = os.path.join(path, 'Outputs_support_forces')
            if not os.path.exists(WALL_OUTPUTS):
                os.makedirs(WALL_OUTPUTS)
            if (Anchors or Struts) and not os.path.exists(SUPPORT_OUTPUTS):
                os.makedirs(SUPPORT_OUTPUTS)

            for phase_no_i in range(1, phasecount):
                self.wall_box.spinBox.setValue(phase_no_i)  # this creates a signal to call self.update_wall_outputs
                #self.update_wall_outputs(path, output_database, x_wall, wall, Anchors, Struts)
                self.save_wall_and_support_outputs(WALL_OUTPUTS, SUPPORT_OUTPUTS, Anchors, Struts)

        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured!".format(e))


    def update_wall_outputs(self, path, output_database, x_wall, wall, Anchors, Struts):        
        if self.subprocess_plaxis_output.poll() is not None:
            print('\nRelaunched PLAXIS2D OUTPUT...')
            PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
            self.subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)
            output_database = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.p2dx')
            self.s_o, self.g_o = new_server('localhost', 10001, password = 'mypassword')
            self.s_o.open(output_database)

        phasenumber = self.wall_box.spinBox.value()
        #self.wall_box.label_2.setText('Phase ' + str(phasenumber))
        
        (phasename, y_plate, Ux_plate, Nx2D_plate, Nx2Demax_plate, Nx2Demin_plate, M2D_plate, 
         M2Demax_plate, M2Demin_plate, Q2D_plate, 
         Q2Demax_plate, Q2Demin_plate) = get_plate_outputs(path, self.g_o, x_wall, phasenumber)
        
        # get max anchor forces and strut forces
        Fmax_anchors = get_all_anchors_force(self.g_o, Anchors, phasenumber)
        Fmax_struts = get_all_struts_force(self.g_o, Struts, phasenumber)

        # store data for later export
        self.data = {}
        self.data['phasename'] = phasename
        self.data['y_plate'] = y_plate
        self.data['Ux_plate'] = Ux_plate
        self.data['Nx2D_plate'] = Nx2D_plate
        self.data['M2D_plate'] = M2D_plate
        self.data['Q2D_plate'] = Q2D_plate
                
        # get N, M, Q at min/ max phase bending moment and shear force
        idx_min_M2D = M2D_plate.index(min(M2D_plate))
        idx_max_M2D = M2D_plate.index(max(M2D_plate))
        idx_min_Q2D = Q2D_plate.index(min(Q2D_plate))
        idx_max_Q2D = Q2D_plate.index(max(Q2D_plate))

        minmax_values_at_min_M2D = OrderedDict()
        minmax_values_at_min_M2D['y'] = y_plate[idx_min_M2D]
        minmax_values_at_min_M2D['NxD'] = Nx2D_plate[idx_min_M2D]
        minmax_values_at_min_M2D['M2D'] = M2D_plate[idx_min_M2D]
        minmax_values_at_min_M2D['Q2D'] = Q2D_plate[idx_min_M2D]

        minmax_values_at_max_M2D = OrderedDict()
        minmax_values_at_max_M2D['y'] = y_plate[idx_max_M2D]
        minmax_values_at_max_M2D['NxD'] = Nx2D_plate[idx_max_M2D]
        minmax_values_at_max_M2D['M2D'] = M2D_plate[idx_max_M2D]
        minmax_values_at_max_M2D['Q2D'] = Q2D_plate[idx_max_M2D]

        minmax_values_at_min_Q2D = OrderedDict()
        minmax_values_at_min_Q2D['y'] = y_plate[idx_min_Q2D]
        minmax_values_at_min_Q2D['NxD'] = Nx2D_plate[idx_min_Q2D]
        minmax_values_at_min_Q2D['M2D'] = M2D_plate[idx_min_Q2D]
        minmax_values_at_min_Q2D['Q2D'] = Q2D_plate[idx_min_Q2D]

        minmax_values_at_max_Q2D = OrderedDict()
        minmax_values_at_max_Q2D['y'] = y_plate[idx_max_Q2D]
        minmax_values_at_max_Q2D['NxD'] = Nx2D_plate[idx_max_Q2D]
        minmax_values_at_max_Q2D['M2D'] = M2D_plate[idx_max_Q2D]
        minmax_values_at_max_Q2D['Q2D'] = Q2D_plate[idx_max_Q2D]

        # show phase name
        self.wall_box.label_2.setText('Phase: ' + phasename)

        # plot
        self.plot_canvas.plot_wall_output(y_plate, np.array(Ux_plate)*1000, 2, 4, 1, 'Ux [mm]', 'Y [m]', 'blue')
        self.plot_canvas.plot_wall_output(y_plate, Nx2D_plate, 2, 4, 2, 'Nx2D [kN/m]', None, 'red')
        self.plot_canvas.plot_wall_output(y_plate, M2D_plate, 2, 4, 3, 'M2D [kNm/m]', None, 'red')
        self.plot_canvas.plot_wall_output(y_plate, Q2D_plate, 2, 4, 4, 'Q2D [kN/m]', None, 'red')        
        self.plot_canvas.plot_wall_output_envelop(y_plate, Nx2Demax_plate, Nx2Demin_plate, 2, 4, 6, 'Nx2D_Envelope [kN/m]', 'Y [m]')
        self.plot_canvas.plot_wall_output_envelop(y_plate, M2Demax_plate, M2Demin_plate, 2, 4, 7, 'M2D_Envelope [kNm/m]', None)
        self.plot_canvas.plot_wall_output_envelop(y_plate, Q2Demax_plate, Q2Demin_plate, 2, 4, 8, 'Q2D_Envelope [kN/m]', None)
        #self.plot_canvas.plot_wall_output_envelope_extreme_values_text(y_plate, minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D, 3, 4, 9, '')
        self.display_maxmin_wall_forces(minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D)
        self.display_max_anchor_forces(Fmax_anchors)
        self.display_min_strut_forces(Fmax_struts)
        axes = self.plot_canvas.fig.add_subplot(2, 4, 5, position=[0.12, 0.1, 0.2, 0.2]); self.plot_canvas.axes = axes
        #axes = self.plot_canvas.fig.add_subplot(2, 4, 5); self.plot_canvas.axes = axes
        self.plot_table_wall_info(wall)


    def plot_table_wall_info(self, wall):
        """ Adds wall information such as top/ bottom/ embedment depth
        """
        level_top = '{0:.2f}'.format(wall['point1'][1])
        level_bottom = '{0:.2f}'.format(wall['point2'][1])
        depth_embedment = '{0:.2f}'.format(wall['depth_embedment'])
        label_rows = ['Wall top [mNN]', 'Wall bottom [mNN]', 'Embedment depth [m]']
        label_columns = None
        cell_text = [[level_top], [level_bottom], [depth_embedment]]

        # plot table
        #self.plot_canvas.plot_table(cell_text, None, label_columns, label_rows, colWidths=[0.7 , 0.3])
        self.plot_canvas.plot_table(cell_text, None, label_columns, label_rows)


    def display_maxmin_wall_forces(self, minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D):
        """ Displays max./min. wall forces
        """
        row_labels = ['@ min_M2D', '@ max_M2D', '@ min_Q2D', '@ max_Q2D']
        self.wall_box.tableWidget.setRowCount(len(row_labels))
        self.wall_box.tableWidget.setVerticalHeaderLabels(row_labels)
        col_labels = ['y [m]', 'NxD [kN/m]', 'M2D [kNm/m]', 'Q2D [kN/m]']
        self.wall_box.tableWidget.setColumnCount(len(col_labels))
        self.wall_box.tableWidget.setHorizontalHeaderLabels(col_labels)

        for i, value in enumerate(minmax_values_at_min_M2D.values()):
            self.wall_box.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(value)))
        for i, value in enumerate(minmax_values_at_max_M2D.values()):
            self.wall_box.tableWidget.setItem(1, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(value)))
        for i, value in enumerate(minmax_values_at_min_Q2D.values()):
            self.wall_box.tableWidget.setItem(2, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(value)))
        for i, value in enumerate(minmax_values_at_max_Q2D.values()):
            self.wall_box.tableWidget.setItem(3, i, QtWidgets.QTableWidgetItem('{:.2f}'.format(value)))


    def display_max_anchor_forces(self, Fmax_anchors):
        """ Displays maximal anchor forces
        """
        self.wall_box.tableWidget_2.setRowCount(len(Fmax_anchors))
        col_labels = ['position (x,y)', 'AnchorForceMax2D [KN]']
        self.wall_box.tableWidget_2.setColumnCount(len(col_labels))
        self.wall_box.tableWidget_2.setHorizontalHeaderLabels(col_labels)
        for i, Fmax_anchor in enumerate(Fmax_anchors):
            self.wall_box.tableWidget_2.setItem(i, 0, QtWidgets.QTableWidgetItem('{0}, {1}'.format(Fmax_anchor['position'][0], Fmax_anchor['position'][1])))
            self.wall_box.tableWidget_2.setItem(i, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(Fmax_anchor['AnchorForceMax2D'])))


    def display_min_strut_forces(self, Fmax_struts):
        """ Displays minimal strut forces
        """
        self.wall_box.tableWidget_3.setRowCount(len(Fmax_struts))
        col_labels = ['position (x,y)', 'StrutForceMin2D [KN]']
        self.wall_box.tableWidget_3.setColumnCount(len(col_labels))
        self.wall_box.tableWidget_3.setHorizontalHeaderLabels(col_labels)
        for i, Fmax_strut in enumerate(Fmax_struts):
            self.wall_box.tableWidget_3.setItem(i, 0, QtWidgets.QTableWidgetItem('{0}, {1}'.format(Fmax_strut['position'][0], Fmax_strut['position'][1])))
            self.wall_box.tableWidget_3.setItem(i, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(Fmax_strut['AnchorForceMax2D'])))


    def save_wall_and_support_outputs(self, path_wall_output, path_support_output, Anchors, Struts):
        """ Save wall internal forces for dimensioning
        """
        # Wall forces
        if self.data:
            with open(os.path.join(path_wall_output, self.data['phasename'].replace('/',' ') + '.txt'), "w") as f:
                f.write("{0}\t\t {1}\t\t {2}\t\t {3}\t\t {4}\n".format('y', 'Ux', 'N', 'M', 'Q'))
                for (y, Ux, N, M, Q) in zip(self.data['y_plate'], self.data['Ux_plate'], self.data['Nx2D_plate'], self.data['M2D_plate'], self.data['Q2D_plate']):
                    f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\n".format(y, Ux, N, M, Q))

        self.wall_box.label_3.setText('Data path: ' + os.path.join(path_wall_output, self.data['phasename'].replace('/',' ') + '.txt'))

        # Anchor forces
        anchor_keys_to_write = ['position', 'angle', 'Lspacing', 'F_anchor']
        for anchor in Anchors:
            anchor_level = anchor['position'][1]
            anchor_dict_to_write = OrderedDict()
            for key in anchor_keys_to_write:
                anchor_dict_to_write[key] = anchor[key]

            with open(os.path.join(path_support_output, 'Anchor_at_level_' + str(anchor_level) + '_' + self.data['phasename'].replace('/',' ') + '.json'), "w") as write_file:
                json.dump(anchor_dict_to_write, write_file)

        # Strut forces
        strut_keys_to_write = ['position', 'direct_x', 'direct_y', 'Lspacing', 'F_strut', 'slope_vert', 'slope_horiz', 'buckling length sy', 'buckling length sz',
                        'eccentricity e/h', 'eccentricity e/b']
        for strut in Struts:
            strut_level = strut['position'][1]
            strut_dict_to_write = OrderedDict()
            for key in strut_keys_to_write:
                strut_dict_to_write[key] = strut[key]

            with open(os.path.join(path_support_output, 'Strut_at_level_' + str(strut_level) + '_' +self.data['phasename'].replace('/',' ') + '.json'), "w") as write_file:
                json.dump(strut_dict_to_write, write_file)


    def open_metamodel_validation_WallUx(self, wall_ux_metamodel=None, wall_ux_measured=None, y_plate=None):
        """ Opens meta model validation plots
        """
        form = QtWidgets.QDialog()
        self.setWindowTitle('Metamodel validation')
        self.view_box = metamodelValidationView()
        self.view_box.setupUi(form)

        self.plot_layout = QtWidgets.QVBoxLayout(self.view_box.widget)
        self.plot_canvas = MyStaticMplCanvasSubplots(self.view_box.widget, width=1, height=1, dpi=100, nrows=5, ncols=6)
        self.plot_layout.addWidget(self.plot_canvas)

        size_validation = len(wall_ux_measured)
        ny = 6
        if size_validation % 6 == 0:
            nx = size_validation//6
        else:
            nx = size_validation//6 + 1
        self.plot_canvas.plot_metamodel_validation_WallUx(nx, ny, wall_ux_metamodel, wall_ux_measured, y_plate)

        form.exec_()


    def open_metamodel_prediction(self, dialog, Metamodels, m0, m_min, m_max):
        """ Predicts using metamodel
        """
        form = QtWidgets.QDialog()
        self.setWindowTitle('Prediction using metamodel')
        self.view_box = metamodelPredictionView()
        self.view_box.setupUi(form)

        self.plot_layout = QtWidgets.QVBoxLayout(self.view_box.widget)
        self.plot_canvas = MyStaticMplCanvasSubplots(self.view_box.widget, width=1, height=1, dpi=100, nrows=2, ncols=3)
        self.plot_layout.addWidget(self.plot_canvas)

        # show metamodels in combobox
        for metamodel in Metamodels:
            self.view_box.comboBox.addItem(metamodel['name'])

        # show soil parameters on table
        self.view_box.tableWidget.setColumnCount(m0.size)
        self.view_box.tableWidget.setRowCount(3)
        param_labels = ['m' + str(param_cnt + 1) for param_cnt in range(m0.size)]
        row_labels = ['m_min', 'm_max', 'm_0']
        self.view_box.tableWidget.setHorizontalHeaderLabels(param_labels)
        self.view_box.tableWidget.setVerticalHeaderLabels(row_labels)

        for column_j in range(m0.size):
            self.view_box.tableWidget.setItem(0, column_j, QtWidgets.QTableWidgetItem(str(m_min[column_j])))
            self.view_box.tableWidget.setItem(1, column_j, QtWidgets.QTableWidgetItem(str(m_max[column_j])))
            self.view_box.tableWidget.setItem(2, column_j, QtWidgets.QTableWidgetItem(str(m0[column_j])))
            self.view_box.tableWidget.item(2, column_j).setBackground(QColor(242, 255, 116)) # light yellow
        
        self.change_metamodel(m0, Metamodels, dialog) # initial plot
        self.view_box.comboBox.currentIndexChanged.connect(lambda: self.change_metamodel(m0, Metamodels, dialog))
        self.view_box.tableWidget.cellChanged.connect(lambda row, column: self.change_metamodel_x(row, column, m0, Metamodels, dialog))


        form.exec_()
        

    @pyqtSlot()
    def change_metamodel(self, m0, Metamodels, dialog):
        """ Responds upon change in metamodel selection
        """
        #metamodel_name = self.view_box.comboBox.currentText()
        #print(metamodel_name)

        # which metamodel
        name_selected_metamodel = self.view_box.comboBox.currentText()
        metamodel_selected = None
        for metamodel in Metamodels:
            if metamodel['name'] == name_selected_metamodel:
                metamodel_selected = metamodel
        self.predict_and_plot_metamodel(dialog, metamodel_selected, m0)


    @pyqtSlot()
    def change_metamodel_x(self, row, column, m0, Metamodels, dialog):
        """ Responds upon change in input to metamodel
        """
        if row == 2:
            #for i in range(m0.size):
            #    m0[i] = float(self.view_box.tableWidget.item(2, i).text())
            m0[column] = float(self.view_box.tableWidget.item(2, column).text())

            # which metamodel
            name_selected_metamodel = self.view_box.comboBox.currentText()
            metamodel_selected = None
            for metamodel in Metamodels:
                if metamodel['name'] == name_selected_metamodel:
                    metamodel_selected = metamodel
                
            self.predict_and_plot_metamodel(dialog, metamodel_selected, m0)

        #print(m0)


    #@pyqtSlot()
    def predict_and_plot_metamodel(self, dialog, metamodel, m0):
        """ Predicts and plots output from metatmodel
        """
        #print('Prediction using metamodel {0}'.format(metamodel['name']))
        Points_obs = metamodel['Points_obs']
        gp_model = metamodel['model']
        y_predict = gp_model.predict(m0.reshape(1,-1))

        y_plate = np.array([item[1] for item in Points_obs[0]['points']])
        #data_to_file = np.array([])
        data_to_file = y_plate
        data_to_file_header = ['Y [m]']
        data_idx_start = 0
        plotindex = 0
        for obs_num, obs_set in enumerate(Points_obs):
            if obs_set['usedForMetamodel'] == True:
                plottitle = metamodel['name'] + '|Phase ' + str(obs_set['obs_phase'])
                plotindex += 1
                y_plate = [item[1] for item in Points_obs[obs_num]['points']]
                wall_ux_metamodel = y_predict[:, data_idx_start:data_idx_start + obs_set['num_points']]
                data_to_file = np.vstack([data_to_file, wall_ux_metamodel]) if data_to_file.size else wall_ux_metamodel
                data_to_file_header.append(plottitle + ' [mm]')
                self.plot_canvas.plot_metamodel_prediction_WallUx(plotindex, plottitle, wall_ux_metamodel, y_plate)

                data_idx_start += obs_set['num_points']

        # write data to file
        self.write_prediction_to_csv_file(dialog, metamodel['name'], np.transpose(data_to_file*1000), data_to_file_header)


    def write_prediction_to_csv_file(self, dialog, name_metamodel, data, header):
        """ Writes predicted values to CSV file
        """
        # save GP metamodel to file
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        SENSIMAN = os.path.join(MONIMAN_OUTPUTS, 'sensiman')
        fname = os.path.join(SENSIMAN, 'data_{0}.csv'.format(name_metamodel))
        #np.savetxt(fname, data, delimiter=';')
        try:
            pd.DataFrame(data).to_csv(fname, sep=';', decimal=',', header=header)
        except PermissionError:
            dialog.show_message_box('Info', 'Please close the file {0}!'.format(fname))

        
    def open_soilsection_settlement(self, subprocess_plaxis_output, path,  s_o, g_o, output_database, point1, point2, scaling_factor, vicinity, phasenumber = 1, phasecount = 1):       
        form = QtWidgets.QDialog()
        self.setWindowTitle('Settlement in soil section')
        self.soilsection_box = outputSoilsectionSettlement()
        self.soilsection_box.setupUi(form)
        self.subprocess_plaxis_output = subprocess_plaxis_output
        self.s_o = s_o
        self.g_o = g_o
        
        self.plot_layout = QtWidgets.QVBoxLayout(self.soilsection_box.widget)
        self.plot_canvas = MyStaticMplCanvasSubplots(self.soilsection_box.widget, width=1, height=1, dpi=100)
        self.plot_layout.addWidget(self.plot_canvas)
        
        
        self.soilsection_box.spinBox.setMinimum(1)
        self.soilsection_box.spinBox.setMaximum(phasecount)
        self.soilsection_box.spinBox.setValue(phasenumber)
        
        self.update_soilsection_settlement(path, output_database, point1, point2, scaling_factor, vicinity)
                
        self.soilsection_box.spinBox.valueChanged.connect(lambda: self.update_soilsection_settlement(path, output_database, point1, point2, scaling_factor, vicinity))
        
        form.exec_()        


    def update_soilsection_settlement(self, path, output_database, point1, point2, scaling_factor, vicinity):        
        if self.subprocess_plaxis_output.poll() is not None:
            print('\nRelaunched PLAXIS2D OUTPUT...\n')
            PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
            self.subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)
            output_database = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.p2dx')
            self.s_o, self.g_o = new_server('localhost', 10001, password = 'mypassword')
            self.s_o.open(output_database)

        phasenumber = self.soilsection_box.spinBox.value()
        self.soilsection_box.label_2.setText('Phase ' + str(phasenumber))
        
        (x_soilsection, y_soilsection, Uy_section) = get_soilsection_uy(path, self.g_o, point1, point2, vicinity, phasenumber)
       
        self.plot_canvas.plot_soilsection_settlement(x_soilsection, y_soilsection, np.array(Uy_section)*1000, scaling_factor, vicinity, 'X [m]', 'Uy [mm]')
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Ui_Form()
    form.open_wall_outputs(phasecount = 3)
    
    sys.exit(app.exec_())