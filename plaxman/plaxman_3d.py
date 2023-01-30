
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 2022

@author: nya
"""
import os
import sys
#import numpy as np
import math
import pandas as pd
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from gui.gui_form_output_Wall_Plaxis3D_ui import Ui_Form as outputWall
from gui.gui_all_dialogs_ui import Ui_Dialog
from plxscripting.easy import new_server
from common.boilerplate import start_plaxis
from tools.math import move_point, calc_dist_2p, swap_2points
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots
from solver.plaxis3d.output_commands import get_plate_outputs_in_line, get_plate_outputs_in_box

class Plaxman3D():
    def __init__(self):
        self.dialog = Ui_Dialog()
        self.path_output_database = None    # path to Plaxis3D database file
        self.data = pd.DataFrame({})
        self.phasecount = 100                # number of phases, will be adjusted after reading Plaxis3D wall outputs
        self.point1 = None
        self.point2 = None
        self.d_edge = 0.0                   # distance from wall side edges to ignore
        # limits in z-direction to read out data
        self.z_top = None                   # top z, None means all z
        self.z_bottom = None                # bottom z, None means all z
        self.data_in_box = False            # read data in box or not?
        self.phasename = ''                 # phase name for data file name when saving


    def plot_wall_outputs(self):
        """ Plot wall deflection and internal forces
        """
        #output_database = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.p2dx')
        
        #if not os.path.exists(output_database):
        #    self.dialog.show_message_box('Warning', 'PLAXIS2D database file does not exist. Make sure that PLAXIS2D simulation has been finished!')
        #    
        #elif len(self.Walls) < 1:
        #    self.dialog.show_message_box('Warning', 'Please make sure that at least one wall is defined!')
        #else:
            #wall_id = int(self.ui.comboBox_14.currentText())
            #point1 = None
            #for wall in self.Walls:
            #    if wall['id'] == wall_id:
            #        point1 = wall['point1']
            #        #point2 = wall['point2']
            #x_wall = point1[0]
            #phasenumber = self.ui.spinBox.value()
            
            #PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
            #subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)

        #PLAXIS3D = r'C:\Program Files\Bentley\Geotechnical\PLAXIS 3D CONNECT Edition V21'
        PLAXIS3D = sys.modules['moniman_paths']['PLAXIS3D']
        subprocess_plaxis_output = start_plaxis(os.path.join(PLAXIS3D, 'Plaxis3DOutput.exe'), portnr=10001)

            
        s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
                    
        #s_o.open(output_database)
            
        print('\nLaunched PLAXIS3D OUTPUT...')
        #print('PLAXIS3D OUTPUT database is in {}'.format(output_database))

        # open wall output window (with Anchors and Struts also)
        self.open_wall_outputs(s_o, g_o)     # TODO: determine max number of phases



    def open_wall_outputs(self, s_o, g_o, phasenumber = 1):       
        form = QtWidgets.QDialog()
        #self.setWindowTitle('Wall outputs')
        self.wall_box = outputWall()
        self.wall_box.setupUi(form)
        self.s_o = s_o
        self.g_o = g_o
        
        self.plot_layout = QtWidgets.QVBoxLayout(self.wall_box.widget)
        self.plot_canvas = MyStaticMplCanvasSubplots(self.wall_box.widget, width=1, height=1, dpi=100, nrows=5, ncols=6)
        self.plot_layout.addWidget(self.plot_canvas)
        
        
        self.wall_box.spinBox.setMinimum(0)
        self.wall_box.spinBox.setMaximum(self.phasecount)
        self.wall_box.spinBox.setValue(phasenumber)

        self.path_output_database = self.wall_box.pushButton_2.clicked.connect(self.select_plaxis3d_database)
        
        self.wall_box.pushButton_3.clicked.connect(self.retrieve_plaxis3d_database)
        self.wall_box.pushButton.clicked.connect(self.save_wall_outputs)

        form.exec_()
    

    def select_plaxis3d_database(self):
        """ Select plaxis3d database
        file suffix *.p3d
        """
        data_file, _ = QFileDialog.getOpenFileName(QFileDialog(), caption='Select a Plaxis3D data file', filter='*.p3d')
        if data_file:
            self.s_o.open(data_file)
            self.path_output_database = data_file
            self.wall_box.lineEdit.setText(self.path_output_database)


    def retrieve_plaxis3d_database(self):
        """ Reads plaxis3d database using the current settings
        """
        #try:
        if self.path_output_database is None:
            self.dialog.show_message_box('Error', 'Please load Plaxis3D database!')
        else:
            try:
                point1_text = self.wall_box.lineEdit_2.text()
                point2_text = self.wall_box.lineEdit_3.text()
                self.point1 = (float(point1_text.split(',')[0]), float(point1_text.split(',')[1]))
                self.point2 = (float(point2_text.split(',')[0]), float(point2_text.split(',')[1]))
                self.d_edge = float(self.wall_box.lineEdit_4.text())
                # check for z range
                z_text = self.wall_box.lineEdit_7.text()
                if z_text != '':
                    self.z_top = float(z_text.split(',')[0])
                    self.z_bottom = float(z_text.split(',')[1])
                
                # check if data in box or data in line
                if self.wall_box.checkBox.checkState() == 2:
                    self.data_in_box = True

                if self.data_in_box is False:
                    # if the line composed by 2 points is parallel to y-axis
                    if self.point2[0] - self.point1[0] < 1.0E-5:
                        angle = 90.0    # degree
                    else:
                        slope = (self.point2[1] - self.point1[1]) / (self.point2[0] - self.point1[0])
                        angle = math.atan(slope)*180.0/math.pi  # degree
                    d_point1_point2 = calc_dist_2p(self.point1, self.point2)    # distance between point1 and point2 
                    point1_adjusted = move_point(self.point1, angle, self.d_edge)
                    point2_adjusted = move_point(self.point2, angle, -self.d_edge)
                    d_point1_point2_adjusted = calc_dist_2p(point1_adjusted, point2_adjusted)
                    if d_point1_point2_adjusted > d_point1_point2: # distance between point1 and point2 must be smaller after adjusting
                        point1_adjusted = move_point(self.point1, angle, -self.d_edge)  # reverse direction
                        point2_adjusted = move_point(self.point2, angle, self.d_edge)   # reverse direction

                    phasenumber = self.wall_box.spinBox.value()
                    print('Point 1 after adjustion', point1_adjusted)
                    print('Point2 after adjustion', point2_adjusted)
                    self.update_wall_outputs(point1_adjusted, point2_adjusted, phasenumber=phasenumber, z_top=self.z_top, z_bottom=self.z_bottom)

                else: # read data in a box composed of 2 points
                    # point1 and point2 should not have the same x- or y-coordinate
                    if (self.point1[0] == self.point2[0]) or (self.point1[1] == self.point2[1]):
                        self.dialog.show_message_box('Warning', "For reading values in a box, point1 and point2 should not have the same x- or y-coordinate!")
                    else:
                        phasenumber = self.wall_box.spinBox.value()
                        if self.point1[0] > self.point2[0]:
                            point1, point2 = swap_2points(self.point1, self.point2)     # point1 is on the left, point2 on the right
                        else:
                            point1 = self.point1
                            point2 = self.point2
                        self.update_wall_outputs(point1, point2, phasenumber=phasenumber, z_top=self.z_top, z_bottom=self.z_bottom, data_in_box=self.data_in_box)

            except Exception as e:
                self.dialog.show_message_box('Warning', "Exception '{}' has occured. Please check your settings!".format(e))


    def update_wall_outputs(self, point1, point2, phasenumber=1, z_top=None, z_bottom=None, data_in_box=False):        
        """ Gets Plaxis3D wall output between two points
        """
        if self.path_output_database is not None:
            path_out = os.path.dirname(self.path_output_database)
        
            # get wall outputs (plate) and node-to-node anchors forces
            if data_in_box is False:
                (self.phasecount, phasename, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate, 
                M11_plate, M11_EnvelopeMax_plate, M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate, 
                Q13_EnvelopeMin_plate, F_anchors_dict) = get_plate_outputs_in_line(path_out, self.g_o, point1, point2, phasenumber, z_top, z_bottom)
            else: # read data in box
                (self.phasecount, phasename, Z_plate, Utot_plate, N11_plate, N11_EnvelopeMax_plate, N11_EnvelopeMin_plate, 
                M11_plate, M11_EnvelopeMax_plate, M11_EnvelopeMin_plate, Q13_plate, Q13_EnvelopeMax_plate, 
                Q13_EnvelopeMin_plate, F_anchors_dict) = get_plate_outputs_in_box(path_out, self.g_o, point1, point2, phasenumber, z_top, z_bottom)

            self.wall_box.label_2.setText('Phase: ' + str(phasenumber))
            self.wall_box.spinBox.setMaximum(self.phasecount - 1)   # set upper limit for spinbox to be number of phases

            # sort anchor forces according to depth
            F_anchors = pd.DataFrame(F_anchors_dict)
            if F_anchors_dict:
                F_anchors = F_anchors.sort_values(by=['Z'], ascending=False) 

            # store data for later export
            #self.data['phasename'] = phasename
            self.phasename = phasename
            self.data.drop(self.data.index, inplace=True)   # clear dataframe
            self.data['Z_plate'] = Z_plate
            self.data['Utot_plate'] = Utot_plate
            self.data['N11_plate'] = N11_plate
            self.data['N11_EnvelopeMax_plate'] = N11_EnvelopeMax_plate
            self.data['N11_EnvelopeMin_plate'] = N11_EnvelopeMin_plate
            self.data['M11_plate'] = M11_plate
            self.data['M11_EnvelopeMax_plate'] = M11_EnvelopeMax_plate
            self.data['M11_EnvelopeMin_plate'] = M11_EnvelopeMin_plate
            self.data['Q13_plate'] = Q13_plate
            self.data['Q13_EnvelopeMax_plate'] = Q13_EnvelopeMax_plate
            self.data['Q13_EnvelopeMin_plate'] = Q13_EnvelopeMin_plate

            # sort according to depth
            self.data = self.data.sort_values(by=['Z_plate'], ascending=False) 

            if Z_plate: # not empty
                # get N, M, Q at min/ max phase bending moment and shear force
                print('Number of data points: {}\n'.format(len(Z_plate)))
                idx_min_M2D = M11_plate.index(min(M11_plate))
                idx_max_M2D = M11_plate.index(max(M11_plate))
                idx_min_Q2D = Q13_plate.index(min(Q13_plate))
                idx_max_Q2D = Q13_plate.index(max(Q13_plate))

                minmax_values_at_min_M2D = OrderedDict()
                minmax_values_at_min_M2D['z'] = Z_plate[idx_min_M2D]
                minmax_values_at_min_M2D['N11'] = N11_plate[idx_min_M2D]
                minmax_values_at_min_M2D['M11'] = M11_plate[idx_min_M2D]
                minmax_values_at_min_M2D['Q13'] = Q13_plate[idx_min_M2D]

                minmax_values_at_max_M2D = OrderedDict()
                minmax_values_at_max_M2D['z'] = Z_plate[idx_max_M2D]
                minmax_values_at_max_M2D['N11'] = N11_plate[idx_max_M2D]
                minmax_values_at_max_M2D['M11'] = M11_plate[idx_max_M2D]
                minmax_values_at_max_M2D['Q13'] = Q13_plate[idx_max_M2D]

                minmax_values_at_min_Q2D = OrderedDict()
                minmax_values_at_min_Q2D['z'] = Z_plate[idx_min_Q2D]
                minmax_values_at_min_Q2D['N11'] = N11_plate[idx_min_Q2D]
                minmax_values_at_min_Q2D['M11'] = M11_plate[idx_min_Q2D]
                minmax_values_at_min_Q2D['Q13'] = Q13_plate[idx_min_Q2D]

                minmax_values_at_max_Q2D = OrderedDict()
                minmax_values_at_max_Q2D['z'] = Z_plate[idx_max_Q2D]
                minmax_values_at_max_Q2D['N11'] = N11_plate[idx_max_Q2D]
                minmax_values_at_max_Q2D['M11'] = M11_plate[idx_max_Q2D]
                minmax_values_at_max_Q2D['Q13'] = Q13_plate[idx_max_Q2D]

                # plot
                #self.plot_canvas.plot_wall_output(self.data['Z_plate'], np.array(Utot_plate)*1000, 2, 4, 1, 'Utot [mm]', 'Z [m]', 'blue')
                self.plot_canvas.plot_wall_output(self.data['Z_plate'], self.data['Utot_plate']*1000, 2, 4, 1, 'Utot [mm]', 'Z [m]', 'blue')
                self.plot_canvas.plot_wall_output(self.data['Z_plate'], self.data['N11_plate'], 2, 4, 2, 'N11 [kN/m]', None, 'red')
                self.plot_canvas.plot_wall_output(self.data['Z_plate'], self.data['M11_plate'], 2, 4, 3, 'M11 [kNm/m]', None, 'red')
                self.plot_canvas.plot_wall_output(self.data['Z_plate'], self.data['Q13_plate'], 2, 4, 4, 'Q13 [kN/m]', None, 'red')        
                self.plot_canvas.plot_wall_output_envelop(self.data['Z_plate'], self.data['N11_EnvelopeMax_plate'], self.data['N11_EnvelopeMin_plate'], 2, 4, 6, 'N11_Envelope [kN/m]', 'Y [m]')
                self.plot_canvas.plot_wall_output_envelop(self.data['Z_plate'], self.data['M11_EnvelopeMax_plate'], self.data['M11_EnvelopeMin_plate'], 2, 4, 7, 'M11_Envelope [kNm/m]', None)
                self.plot_canvas.plot_wall_output_envelop(self.data['Z_plate'], self.data['Q13_EnvelopeMax_plate'], self.data['Q13_EnvelopeMin_plate'], 2, 4, 8, 'Q13_Envelope [kN/m]', None)
                self.display_maxmin_wall_forces(minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D)
                if F_anchors_dict:
                    self.display_anchor_forces(F_anchors)
                #axes = self.plot_canvas.fig.add_subplot(2, 4, 5, position=[0.12, 0.1, 0.2, 0.2]); self.plot_canvas.axes = axes
                #self.plot_table_wall_info(wall)

            else:
                print('Number of data points: {}\n'.format(len(Z_plate)))   # should be zero: no data points
                self.plot_canvas.plot_wall_output_empty(2, 4, 1)
                self.plot_canvas.plot_wall_output_empty(2, 4, 2)
                self.plot_canvas.plot_wall_output_empty(2, 4, 3)
                self.plot_canvas.plot_wall_output_empty(2, 4, 4)
                self.plot_canvas.plot_wall_output_empty(2, 4, 6)
                self.plot_canvas.plot_wall_output_empty(2, 4, 7)
                self.plot_canvas.plot_wall_output_empty(2, 4, 8)


    def display_maxmin_wall_forces(self, minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D):
        """ Displays max./min. wall forces
        """
        row_labels = ['@ min_M11', '@ max_M11', '@ min_Q13', '@ max_Q13']
        self.wall_box.tableWidget.setRowCount(len(row_labels))
        self.wall_box.tableWidget.setVerticalHeaderLabels(row_labels)
        col_labels = ['z [m]', 'N11 [kN/m]', 'M11 [kNm/m]', 'Q13 [kN/m]']
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


    def display_anchor_forces(self, F_anchors):
        """ Displays anchor forces
        """
        self.wall_box.tableWidget_2.setRowCount(len(F_anchors['Z']))
        col_labels = ['position (x,y,z)', 'AnchorForce3D [KN]']
        self.wall_box.tableWidget_2.setColumnCount(len(col_labels))
        self.wall_box.tableWidget_2.setHorizontalHeaderLabels(col_labels)
        i = 0
        for x, y, z, F_anchor in zip(F_anchors['X'], F_anchors['Y'], F_anchors['Z'], F_anchors['Force3D']):
            self.wall_box.tableWidget_2.setItem(i, 0, QtWidgets.QTableWidgetItem('{0:.3f}, {1:.3f}, {2:.3f}'.format(x, y, z)))
            self.wall_box.tableWidget_2.setItem(i, 1, QtWidgets.QTableWidgetItem('{:.2f}'.format(F_anchor)))
            i += 1



    def save_wall_outputs(self):
        """ Save wall internal forces for dimensioning
        """
        try:
            # prepare directory for wall outputs
            if self.path_output_database is not None:
                path_output_dir = os.path.dirname(self.path_output_database)
                WALL_OUTPUTS = os.path.join(path_output_dir, 'Wall_outputs_plaxis3d')
                if not os.path.exists(WALL_OUTPUTS):
                    os.makedirs(WALL_OUTPUTS)

                if not self.data.empty:
                    with open(os.path.join(WALL_OUTPUTS, self.phasename.replace('/',' ') + '.txt'), "w") as f:
                        f.write("{0}\t\t {1}\t\t {2}\t\t {3}\t\t {4}\n".format('z', 'Utot', 'N11', 'M11', 'Q13'))
                        for (z, Utot, N, M, Q) in zip(self.data['Z_plate'], self.data['Utot_plate'], self.data['N11_plate'], self.data['M11_plate'], self.data['Q13_plate']):
                            f.write("{0:.4E}\t {1:.4E}\t {2:.4E}\t {3:.4E}\t {4:.4E}\n".format(z, Utot, N, M, Q))

                    self.wall_box.label_3.setText('Data path: ' + os.path.join(WALL_OUTPUTS, self.phasename.replace('/',' ') + '.txt'))

                else:
                    self.dialog.show_message_box('Warning', "No data to export!")

            else:
                self.dialog.show_message_box('Warning', "No data to export!")

        except Exception as e:
            self.dialog.show_message_box('Warning', "Exception '{}' has occured!".format(e))