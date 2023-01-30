# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 11:12:17 2019

@author: nya
"""
import os, sys
from random import randint
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
#from gui.gui_all_dialogs_ui import Ui_Dialog
import solver.plaxis2d.input_scripting_commands as plaxis2d_input
from plaxman.plaxman import Plaxman

class Plaxman_CombinedPhases(Plaxman):

    def __init__(self, ui, plot_canvas):
        
        super().__init__(ui, plot_canvas)


    def display_all_model_components(self):
        """ Displays all model components on tables
        """
        self.update_soilclusters()
        self.update_waterlevels()
        self.update_drain()
        self.update_ground_anchors()
        self.update_struts()
        self.update_walls()
        self.update_lineloads()
        self.update_pointloads()
              
        
        
    def update_soilclusters(self):
        """ Inserts soil cluser in table in 'Combined phases'
        """
        column_labels = ['Soilcluser_ID', 'Cluster bottom', 'Current soilmaterial' , 'Action', 'Soilmaterial']
        self.ui.tableWidget_7.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_7.setRowCount(len(self.Soilclusters))

        for row_i, soilcluster in enumerate(self.Soilclusters):
            self.ui.tableWidget_7.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(soilcluster['id'])))
            self.ui.tableWidget_7.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(min(soilcluster['pointBL'][1], soilcluster['pointBR'][1]))))
            self.ui.tableWidget_7.setItem(row_i, 2, QtWidgets.QTableWidgetItem(soilcluster['soilmaterial']))

            actions = ['None', 'Activate', 'Deactivate', 'Set material', 'Set dry', 'Interpolate']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            #combobox.currentIndexChanged.connect(self.respond_to_soilcluster_action)
            combobox.activated[str].connect(self.respond_to_soilcluster_action)

            self.ui.tableWidget_7.setCellWidget(row_i, 3, combobox)

    
    def respond_to_soilcluster_action(self, text):
        """ Responds to changes in soilcluster action
        """
        combobox = self.ui.tableWidget_7.sender()
        #print('Soilcluster {0}, action {1}\n'.format(combobox.property('row'), text))
        soilmaterial_json_items = [soilmaterial['json_item'] for soilmaterial in self.Soilmaterials]
        if text == 'Set material':
            materialbox = QtWidgets.QComboBox() 
            materialbox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for material in soilmaterial_json_items:
                materialbox.addItem(material)

            self.ui.tableWidget_7.setCellWidget(combobox.property('row'), 4, materialbox)

        else:
            self.ui.tableWidget_7.removeCellWidget(combobox.property('row'), 4)
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_7.setItem(combobox.property('row'), 4, item)


    def update_waterlevels(self):
        """ Inserts soil cluser in table in 'Combined phases'
        """
        column_labels = ['WaterLevel_ID', 'Water level' , 'Action', '', 'Soilcluster(s)']
        self.ui.tableWidget_8.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_8.setRowCount(len(self.Waterlevels))

        for row_i, waterlevel in enumerate(self.Waterlevels):
            self.ui.tableWidget_8.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(waterlevel['id'])))
            self.ui.tableWidget_8.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(min(waterlevel['pointL'][1], waterlevel['pointR'][1]))))

            actions = ['None', 'Assign to soilcluster(s)']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            combobox.activated[str].connect(self.respond_to_waterlevel_action)

            self.ui.tableWidget_8.setCellWidget(row_i, 2, combobox)


    def respond_to_waterlevel_action(self, text):
        """ Responds to changes in waterlevel action
        """
        combobox = self.ui.tableWidget_8.sender()
        #print('Waterlevel {0}, action {1}\n'.format(combobox.property('row'), text))
        if text != 'None':
            select_clusters_button = QtWidgets.QPushButton('Select') 
            select_clusters_button.setProperty('row', combobox.property('row')) 
            select_clusters_button.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            #select_clusters_button.clicked.connect(self.waterlevel_select_soilclusters) -> doesn't work, 

            self.ui.tableWidget_8.setCellWidget(combobox.property('row'), 3, select_clusters_button)
            self.ui.tableWidget_8.cellWidget(combobox.property('row'), 3).clicked.connect(self.waterlevel_select_soilclusters)

        else:
            self.ui.tableWidget_8.removeCellWidget(combobox.property('row'), 3)
            self.ui.tableWidget_8.setItem(combobox.property('row'), 4, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_8.setItem(combobox.property('row'), 3, item)
            self.ui.tableWidget_8.setItem(combobox.property('row'), 4, item)


    def waterlevel_select_soilclusters(self):
        """ Selects soilclusters to which the (user) water level is assigned
        """
        select_clusters_button = self.ui.tableWidget_8.sender()
        row = select_clusters_button.property('row')
        #print(row)
        if self.Soilclusters:
            self.dialog.open_remove_structure_selection(self.Soilclusters, 'Soil cluster selection for assigning user water level')
            soilcluster_ids = self.dialog.removed_ids
            #print(soilcluster_ids)
            self.ui.tableWidget_8.setItem(row, 4, QtWidgets.QTableWidgetItem(str(soilcluster_ids)))


    def update_drain(self):
        """ Inserts the (single) drain in table in 'Combined phases'
        """
        column_labels = ['Drain_ID', 'Drain level [m]' , 'Action', 'Drain head [m]']
        self.ui.tableWidget_9.setHorizontalHeaderLabels(column_labels)

        if self.Drain:
            self.ui.tableWidget_9.setRowCount(1)
            row = 0
            self.ui.tableWidget_9.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.Drain['id'])))
            self.ui.tableWidget_9.setItem(row, 1, QtWidgets.QTableWidgetItem(str(min(self.Drain['pointL'][1], self.Drain['pointR'][1]))))

            actions = ['None', 'Change head']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row) 
            combobox.activated[str].connect(self.respond_to_drain_action)

            self.ui.tableWidget_9.setCellWidget(row, 2, combobox)
        
        else:
            self.ui.tableWidget_9.setRowCount(0)


    def respond_to_drain_action(self, text):
        """ Responds to changes in drain action
        """
        combobox = self.ui.tableWidget_9.sender()
        if text != 'None':
            self.ui.tableWidget_9.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem('0.0'))
            self.ui.tableWidget_9.item(combobox.property('row'), 3).setBackground(QColor(242, 255, 116))

        else:
            self.ui.tableWidget_9.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_9.setItem(combobox.property('row'), 3, item)
            

    def update_ground_anchors(self):
        """ Inserts groundanchors in table in 'Combined phases'
        """
        column_labels = ['GroundAnchor_ID', 'Position' , 'Action', 'F_pretress [kN]']
        self.ui.tableWidget_10.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_10.setRowCount(len(self.Anchors))

        for row_i, anchor in enumerate(self.Anchors):
            self.ui.tableWidget_10.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(anchor['id'])))
            self.ui.tableWidget_10.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(anchor['position'])))

            actions = ['None', 'Activate', 'Deactivate']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            combobox.setProperty('F_prestress', anchor['F_prestress']) 
            combobox.activated[str].connect(lambda text: self.respond_to_groundanchor_action(text))

            self.ui.tableWidget_10.setCellWidget(row_i, 2, combobox)


    def respond_to_groundanchor_action(self, text):
        """ Responds to changes in ground anchor action
        """
        combobox = self.ui.tableWidget_10.sender()
        if text == 'Activate':
            F_prestress = combobox.property('F_prestress')
            self.ui.tableWidget_10.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem(str(F_prestress)))

        else:
            self.ui.tableWidget_10.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_10.setItem(combobox.property('row'), 3, item)


    def update_struts(self):
        """ Inserts struts in table in 'Combined phases'
        """
        column_labels = ['Strut_ID', 'Position' , 'Action', 'F_pretress [kN]']
        self.ui.tableWidget_11.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_11.setRowCount(len(self.Struts))

        for row_i, strut in enumerate(self.Struts):
            self.ui.tableWidget_11.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(strut['id'])))
            self.ui.tableWidget_11.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(strut['position'])))

            actions = ['None', 'Activate', 'Deactivate']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            combobox.setProperty('F_prestress', strut['F_prestress'])
            combobox.activated[str].connect(lambda text: self.respond_to_strut_action(text))

            self.ui.tableWidget_11.setCellWidget(row_i, 2, combobox)


    def respond_to_strut_action(self, text):
        """ respond to changes in strut action
        """
        combobox = self.ui.tableWidget_11.sender()
        if text == 'Activate':
            F_prestress = combobox.property('F_prestress')
            self.ui.tableWidget_11.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem(str(F_prestress)))

        else:
            self.ui.tableWidget_11.setItem(combobox.property('row'), 3, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_11.setItem(combobox.property('row'), 3, item)


    def update_walls(self):
        """ Inserts walls to table in 'Combined phases'
        """
        column_labels = ['Wall_ID', 'Postion 1' , 'Position 2', 'Action']
        self.ui.tableWidget_12.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_12.setRowCount(len(self.Walls))

        for row_i, wall in enumerate(self.Walls):
            self.ui.tableWidget_12.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(wall['id'])))
            self.ui.tableWidget_12.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(wall['point1'])))
            self.ui.tableWidget_12.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(wall['point2'])))

            actions = ['None', 'Activate', 'Deactivate']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            self.ui.tableWidget_12.setCellWidget(row_i, 3, combobox)


    def update_lineloads(self):
        """ Inserts lineloads in table in 'Combined phases'
        """
        column_labels = ['Lineload_ID', 'Postion 1' , 'Position 2', 'qy [kN/m/m]', 'Action', 'new qy [kN/m/m]']
        self.ui.tableWidget_13.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_13.setRowCount(len(self.Lineloads))

        for row_i, lineload in enumerate(self.Lineloads):
            self.ui.tableWidget_13.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(lineload['id'])))
            self.ui.tableWidget_13.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(lineload['point1'])))
            self.ui.tableWidget_13.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(lineload['point2'])))
            self.ui.tableWidget_13.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(lineload['qy'])))

            actions = ['None', 'Activate', 'Deactivate', 'Change value']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            combobox.activated[str].connect(self.respond_to_lineload_action)

            self.ui.tableWidget_13.setCellWidget(row_i, 4, combobox)


    def respond_to_lineload_action(self, text):
        """ Responds to changes in line load action
        """
        combobox = self.ui.tableWidget_13.sender()
        if text == 'Change value':
            self.ui.tableWidget_13.setItem(combobox.property('row'), 5, QtWidgets.QTableWidgetItem('-20.0'))
            self.ui.tableWidget_13.item(combobox.property('row'), 5).setBackground(QColor(242, 255, 116))

        else:
            self.ui.tableWidget_13.setItem(combobox.property('row'), 5, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_13.setItem(combobox.property('row'), 5, item)


    def update_pointloads(self):
        """ Inserts pointloads in table in 'Combined phases'
        """

        column_labels = ['Pointload_ID', 'Postion' , 'Fx [kN/m]', 'Fy [kN/m]', 'Action', 'new Fy [kN/m]']
        self.ui.tableWidget_14.setHorizontalHeaderLabels(column_labels)
        self.ui.tableWidget_14.setRowCount(len(self.Pointloads))

        for row_i, pointload in enumerate(self.Pointloads):
            self.ui.tableWidget_14.setItem(row_i, 0, QtWidgets.QTableWidgetItem(str(pointload['id'])))
            self.ui.tableWidget_14.setItem(row_i, 1, QtWidgets.QTableWidgetItem(str(pointload['point'])))
            self.ui.tableWidget_14.setItem(row_i, 2, QtWidgets.QTableWidgetItem(str(pointload['Fx'])))
            self.ui.tableWidget_14.setItem(row_i, 3, QtWidgets.QTableWidgetItem(str(pointload['Fy'])))

            actions = ['None', 'Activate', 'Deactivate', 'Change value']
            combobox = QtWidgets.QComboBox()
            combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            for action in actions:
                combobox.addItem(action)

            combobox.setProperty('row', row_i) 
            combobox.activated[str].connect(self.respond_to_pointload_action)

            self.ui.tableWidget_14.setCellWidget(row_i, 4, combobox)


    def respond_to_pointload_action(self, text):
        """ Responds to changes in point load action
        """
        combobox = self.ui.tableWidget_14.sender()
        if text == 'Change value':
            self.ui.tableWidget_14.setItem(combobox.property('row'), 5, QtWidgets.QTableWidgetItem('-20.0'))
            self.ui.tableWidget_14.item(combobox.property('row'), 5).setBackground(QColor(242, 255, 116))

        else:
            self.ui.tableWidget_14.setItem(combobox.property('row'), 5, QtWidgets.QTableWidgetItem(''))
            # set cell read-only
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget_14.setItem(combobox.property('row'), 5, item)
    

    def add_combined_phase(self):
        """ Add one combined phase
        """
        #is_successful = True
        self.plaxis2d_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.py')
        new_phase = {}
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = self.ui.lineEdit_47.text()
        new_phase['deform_calc_type'] = self.ui.comboBox_24.currentText()
        new_phase['pore_pres_calc_type'] = self.ui.comboBox_25.currentText()
        new_phase['reset_displ_zero'] = (self.ui.checkBox_6.checkState() == 2)
        new_phase['loading_type'] = self.ui.comboBox_46.currentText()
        new_phase['time_interval'] = self.ui.lineEdit_85.text()

        new_phase['water_level_id'] = None       
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = True # flag for combined phase

        # add combined phase information
        if len(self.Phases) > 0:
            plaxis2d_input.add_combined_phase_info(self.plaxis2d_input_file, 'g_i', new_phase, self.Phases[-1])
        else:
            plaxis2d_input.add_combined_phase_info_initialphase(self.plaxis2d_input_file, 'g_i', new_phase)

        try:
            # check and add wall actions
            self.add_phase_walls(self.Walls, new_phase)
            # check and add lineload actions
            self.add_phase_lineloads(self.Lineloads, new_phase)
            # check and add pointload actions
            self.add_phase_pointloads(self.Pointloads, new_phase)
            # check and add soilcluster actions
            self.add_phase_soilclusters(self.Soilclusters, new_phase)
            # check and assign user water levels
            self.add_phase_waterlevels(self.Waterlevels, new_phase)
            # check and assign drain
            self.add_phase_drain(self.Drain, new_phase)
            # check and add ground anchors
            self.add_phase_anchors(self.Anchors, new_phase)
            # check and add struts
            self.add_phase_struts(self.Struts, new_phase)


            self.Phases.append(new_phase)
            self.update_phase_table(self.Phases)
            print(new_phase['phase_name'] + ' phase is created')

            # reset comboboxes for the next phase
            self.reset_comboboxes()
            self.ui.comboBox_31.addItem(str(len(self.Phases)))  # in Plaxman
            self.ui.comboBox_21.addItem(str(len(self.Phases)))  # in Backman

        except ValueError:
            plaxis2d_input.remove_structure_inbetween(self.plaxis2d_input_file, new_phase['phase_id'], '##PHASE', '##END_OF_PHASE')
            #is_successful = False
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')

        #return is_successful


    def reset_comboboxes(self):
        """ Reset comboboxes in combined phase
        """
        for row_i in range(self.ui.tableWidget_12.rowCount()): # walls
            self.ui.tableWidget_12.cellWidget(row_i, 3).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_13.rowCount()): # lineloads
            self.ui.tableWidget_13.cellWidget(row_i, 4).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_14.rowCount()): # pointloads
            self.ui.tableWidget_14.cellWidget(row_i, 4).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_7.rowCount()): # soilclusters
            self.ui.tableWidget_7.cellWidget(row_i, 3).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_8.rowCount()): # waterlevels
            self.ui.tableWidget_8.cellWidget(row_i, 2).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_9.rowCount()): # drain
            self.ui.tableWidget_9.cellWidget(row_i, 2).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_10.rowCount()): # anchors
            self.ui.tableWidget_10.cellWidget(row_i, 2).setCurrentIndex(0)
        for row_i in range(self.ui.tableWidget_11.rowCount()): # struts
            self.ui.tableWidget_11.cellWidget(row_i, 2).setCurrentIndex(0)


    def add_phase_walls(self, Walls, new_phase):
        """ Adds wall actions to phase
        """
        wall_ids_activate = []
        wall_ids_deactivate = []
        for row_i, wall in enumerate(Walls):
            action = self.ui.tableWidget_12.cellWidget(row_i, 3).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(wall['pathpatches'])
                #print(wall['pathpatches'][1].get_facecolor())
                #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in wall['pathpatches']))
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() if pathpatch_i is not None else None for pathpatch_i in wall['pathpatches'][:-1]))
                wall_ids_activate.append(wall['id'])
                self.plot_canvas.set_color(wall['pathpatches'][0], wall['color'][0])
                self.plot_canvas.set_color(wall['pathpatches'][1], wall['color'][1])
                self.plot_canvas.set_color(wall['pathpatches'][2], wall['color'][2])
                self.plot_canvas.set_color(wall['pathpatches'][3], wall['color'][3])    # annotation
                #print(wall['pathpatches'][1].get_facecolor())

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(wall['pathpatches'])
                new_phase['pathpatch_colors'].append(pathpatch_i.get_facecolor() for pathpatch_i in wall['pathpatches'])
                wall_ids_deactivate.append(wall['id'])
                self.plot_canvas.set_grey_pathpatches(wall['pathpatches'])

        new_phase['wall_ids_activate'] = wall_ids_activate
        new_phase['wall_ids_deactivate'] = wall_ids_deactivate

        plaxis2d_input.add_combined_phase_walls(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_lineloads(self, Lineloads, new_phase):
        """ Adds lineload actions to phase
        """
        lload_ids_activate = []
        lload_ids_deactivate = []
        lload_qys_new = {}   # id: value
        for row_i, lload in enumerate(Lineloads):
            action = self.ui.tableWidget_13.cellWidget(row_i, 4).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(lload['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in lload['pathpatches']))
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in lload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                lload_ids_activate.append(lload['id'])
                self.plot_canvas.set_color(lload['pathpatches'], 'blue')

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(lload['pathpatches'])
                #new_phase['pathpatch_colors'].append(pathpatch_i.get_facecolor() for pathpatch_i in lload['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in lload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                lload_ids_deactivate.append(lload['id'])
                self.plot_canvas.set_grey_pathpatches(lload['pathpatches'])
            
            elif action == 'Change value':
                lload_id = lload['id']
                qy = float(self.ui.tableWidget_13.item(row_i, 5).text())
                lload_qys_new[lload_id] = qy

        new_phase['lload_ids_activate'] = lload_ids_activate
        new_phase['lload_ids_deactivate'] = lload_ids_deactivate
        new_phase['lload_qys_new'] = lload_qys_new
        plaxis2d_input.add_combined_phase_lineloads(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_pointloads(self, Pointloads, new_phase):
        """ Adds pointload actions to phase
        """
        pload_ids_activate = []
        pload_ids_deactivate = []
        pload_Fys_new = {}   # id: value
        for row_i, pload in enumerate(Pointloads):
            action = self.ui.tableWidget_14.cellWidget(row_i, 4).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(pload['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(pload['pathpatches'].get_facecolor()))
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in pload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                pload_ids_activate.append(pload['id'])
                self.plot_canvas.set_color(pload['pathpatches'], 'blue')

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(pload['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(pload['pathpatches'].get_facecolor()))
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_edgecolor() for pathpatch_i in pload['pathpatches'][:-1]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                pload_ids_deactivate.append(pload['id'])
                self.plot_canvas.set_grey_pathpatches(pload['pathpatches'])

            elif action == 'Change value':
                pload_id = pload['id']
                Fy = float(self.ui.tableWidget_14.item(row_i, 5).text())
                pload_Fys_new[pload_id] = Fy

        new_phase['pload_ids_activate'] = pload_ids_activate
        new_phase['pload_ids_deactivate'] = pload_ids_deactivate
        new_phase['pload_Fys_new'] = pload_Fys_new
        plaxis2d_input.add_combined_phase_pointloads(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_soilclusters(self, Soilclusters, new_phase):
        """ Adds soilcluster actions to phase
        """
        scluster_ids_activate = []
        scluster_ids_deactivate = []
        scluster_ids_setmaterial = {} # {id: materialname}
        scluster_ids_setdry = []
        scluster_ids_interpolate = []   # soil clusters for interpolating pore pressure
        for row_i, scluster in enumerate(Soilclusters):
            action = self.ui.tableWidget_7.cellWidget(row_i, 3).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(scluster['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple(scluster['pathpatches'].get_facecolor()))
                scluster_ids_activate.append(scluster['id'])
                self.plot_canvas.set_color(scluster['pathpatches'], 'blue')

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(scluster['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(scluster['pathpatches'].get_facecolor()))
                #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in scluster['pathpatches'] if hasattr(pathpatch_i,'get_facecolor')))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in scluster['pathpatches'][:-2]))    # use get_edgecolor() instead of get_facecolor() and stop for loop before pathpatch for annotation
                scluster_ids_deactivate.append(scluster['id'])
                #self.plot_canvas.set_grey_pathpatches(scluster['pathpatches'])
                self.plot_canvas.set_color_excavated_soilcluster(scluster['pathpatches'])

            elif action == 'Set material':
                scluster_ids_setmaterial[str(scluster['id'])] = self.ui.tableWidget_7.cellWidget(row_i, 4).currentText()

            elif action == 'Set dry':
                scluster_ids_setdry.append(scluster['id'])

            elif action == 'Interpolate':
                scluster_ids_interpolate.append(scluster['id'])
                

        new_phase['scluster_ids_activate'] = scluster_ids_activate
        new_phase['scluster_ids_deactivate'] = scluster_ids_deactivate
        new_phase['scluster_ids_setmaterial'] = scluster_ids_setmaterial
        new_phase['scluster_ids_setdry'] = scluster_ids_setdry
        new_phase['scluster_ids_interpolate'] = scluster_ids_interpolate
        path_material = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        new_phase['path_material'] = path_material
        plaxis2d_input.add_combined_phase_soilclusters(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_waterlevels(self, Waterlevels, new_phase):
        """ Adds waterlevel actions to phase
        Note, for a combined phase, the user has to explicitly set soilclusters above drain head dry
        """
        wlevel_ids_use = []
        scluster_ids_assign = []
        for row_i, wlevel in enumerate(Waterlevels):
            action = self.ui.tableWidget_8.cellWidget(row_i, 2).currentText()
            if action == 'Assign to soilcluster(s)':
                wlevel_ids_use.append(wlevel['id'])
                scluster_ids_assign.append(eval(self.ui.tableWidget_8.item(row_i, 4).text()))

        new_phase['wlevel_ids_use'] = wlevel_ids_use
        new_phase['scluster_ids_assign'] = scluster_ids_assign
        plaxis2d_input.add_combined_phase_waterlevels(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_drain(self, Drain, new_phase):
        """ Adds drain actions to phase
        Note, for a combined phase, the user has to explicitly set soilclusters above drain head dry
        """
        new_phase['drain_id'] = None
        if Drain:
            drain_head = 0.0
            action = self.ui.tableWidget_9.cellWidget(0, 2).currentText()
            if action == 'Change head':
                drain_head = float(self.ui.tableWidget_9.item(0, 3).text())

            new_phase['drain_head'] = drain_head
            new_phase['drain_id'] = Drain['id']
            plaxis2d_input.add_combined_phase_drain(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_anchors(self, Anchors, new_phase):
        """ Adds ground anchor actions to phase
        """
        anchor_ids_activate = []
        anchor_forces_activate = []
        anchor_ids_deactivate = []
        for row_i, anchor in enumerate(Anchors):
            action = self.ui.tableWidget_10.cellWidget(row_i, 2).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(anchor['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in anchor['pathpatches']))
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in anchor['pathpatches'] if hasattr(pathpatch_i, 'get_facecolor')))
                anchor_ids_activate.append(anchor['id'])
                anchor_forces_activate.append(float(self.ui.tableWidget_10.item(row_i, 3).text()))
                self.plot_canvas.set_color(anchor['pathpatches'][0], 'black')
                self.plot_canvas.set_color(anchor['pathpatches'][1], 'magenta')
                self.plot_canvas.set_color(anchor['pathpatches'][2], 'black')   # annotation

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(anchor['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in anchor['pathpatches']))
                anchor_ids_deactivate.append(anchor['id'])
                self.plot_canvas.set_grey_pathpatches(anchor['pathpatches'])

        new_phase['anchor_ids_activate'] = anchor_ids_activate
        new_phase['F_prestress'] = anchor_forces_activate
        new_phase['anchor_ids_deactivate'] = anchor_ids_deactivate
        plaxis2d_input.add_combined_phase_anchors(self.plaxis2d_input_file, 'g_i', new_phase)


    def add_phase_struts(self, Struts, new_phase):
        """ Adds ground anchor actions to phase
        """
        strut_ids_activate = []
        strut_forces_activate = []
        strut_ids_deactivate = []
        for row_i, strut in enumerate(Struts):
            action = self.ui.tableWidget_11.cellWidget(row_i, 2).currentText()
            if action == 'Activate':
                new_phase['pathpatches'].append(strut['pathpatches'])
                #new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in strut['pathpatches']))
                strut_ids_activate.append(strut['id'])
                strut_forces_activate.append(float(self.ui.tableWidget_11.item(row_i, 3).text()))
                #self.plot_canvas.set_color(strut['pathpatches'], 'black')
                new_phase['pathpatch_colors'].append(tuple((strut['pathpatches'][0].get_facecolor(), strut['pathpatches'][1].get_facecolor())))
                self.plot_canvas.set_color(strut['pathpatches'][0], 'black')
                self.plot_canvas.set_color(strut['pathpatches'][1], 'black')
                self.plot_canvas.set_color(strut['pathpatches'][2], 'black')    # annotation

            elif action == 'Deactivate':
                new_phase['pathpatches'].append(strut['pathpatches'])
                new_phase['pathpatch_colors'].append(tuple(pathpatch_i.get_facecolor() for pathpatch_i in strut['pathpatches']))
                strut_ids_deactivate.append(strut['id'])
                self.plot_canvas.set_grey_pathpatches(strut['pathpatches'])

        new_phase['strut_ids_activate'] = strut_ids_activate
        new_phase['F_prestress'] = strut_forces_activate
        new_phase['strut_ids_deactivate'] = strut_ids_deactivate
        plaxis2d_input.add_combined_phase_struts(self.plaxis2d_input_file, 'g_i', new_phase)


    def remove_combined_phase(self):
        """ Removes a combined phase
        """
        self.plaxis2d_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.py')

        if len(self.Phases) > 0:
            deleted_phase = self.Phases.pop()   
            # undo assiging colors of the previously added phase
            if 'pathpatches' in deleted_phase:
                for group_i, pathpathgroup in enumerate(deleted_phase['pathpatches']):
                    #[print(color) for color in deleted_phase['pathpatch_colors'][group_i]]
                    self.plot_canvas.set_colors(pathpathgroup, deleted_phase['pathpatch_colors'][group_i])
                    #[print(pathpatch_i.get_facecolor()) for pathpatch_i in pathpathgroup]
                
            # remove the phase in plaxis2d_input_file
            plaxis2d_input.remove_structure_inbetween(self.plaxis2d_input_file, deleted_phase['phase_id'], '##PHASE', '##END_OF_PHASE')
            # update phase table
            self.update_phase_table(self.Phases)

            self.ui.comboBox_31.removeItem(len(self.Phases)) # in Plaxman
            self.ui.comboBox_21.removeItem(len(self.Phases)) # in Backman

            print(deleted_phase['phase_name'] + ' phase is removed')
                

    def update_phase_table(self, Phases):
        """ Update the table of phases
        """
        #column_items = sorted(list(self.Phases[0].keys()))
        #column_items = ['phase_id', 'phase_name', 'deform_calc_type', 'pore_pres_calc_type', 'water_level_id']
        column_items = ['phase_id', 'phase_name', 'deform_calc_type', 'pore_pres_calc_type', 'loading_type', 'time_interval', 'water_level_id']
        row_number = len(Phases)
        column_number = len(column_items)
        self.ui.tableWidget_2.setRowCount(row_number)
        self.ui.tableWidget_2.setColumnCount(column_number)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(column_items)
        for i in range(len(Phases)):
            for j in range(len(column_items)):
                self.ui.tableWidget_2.setItem(i, j,  QtWidgets.QTableWidgetItem(str(Phases[i][column_items[j]])))
            #self.ui.tableWidget_2.setCellWidget(i, len(column_items) - 1, QtWidgets.QCheckBox('Select item?'))
            
            
    def load(self):
        """ Simply shows model components 
        """
        self.display_all_model_components()
            
