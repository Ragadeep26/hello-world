# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 08:55:29 2019

@author: nya
"""

#from memory_profiler import profile
import os, sys
import numpy as np
import json
from collections import OrderedDict, namedtuple
from random import randint
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot
from tools.math import hex_to_rgb, get_anchor_grout_endpoints, get_anchor_soillayer_intersection_point, calc_dist_2p
from tools.json_functions import read_data_in_json_item, update_data_in_json_item
from solver.plaxis2d.parameter_relations import get_SPW_parameters
from plaxman.plaxman import Plaxman
import solver.plaxis2d.input_scripting_commands as plaxis2d_input
from tools.file_tools import saveobjs, loadobjs
from gui.gui_groupbox_automated_phase import Ui_GroupBox as automatedPhasesGroupBox
from workflow1.evaluate_plaxis2d_model import Evaluate_Plaxis2DModel
from system.run_thread import RunThreadSingle
#from dimensioning.dimensioning import get_steel_areas_dw
from optiman.structure_costs import StructureCostFactory

class Plaxman_AutomatedPhases_Phreatic(Plaxman):

    def __init__(self, ui, plot_canvas=None):
        """ Initializes Plaxman's Automated Phases
        """
        super().__init__(ui, plot_canvas)
               
        self.final_excavation_level = {}    # the final excavation level
        self.wall = {}                      # the wall under consideration (only one object)

        self.Phases_data = []       # data for dewatering arranged in phases
        self.points_berm = {}       # coordinates of the berm
        self.points_berm_base = {}  # coordinates of the berm at base of the excavation

        self.pore_pressure_interp = False   # pore pressure interpolation is checked or not
        self.FoS_phase = False              # FoS phase is checked or not
        self.points_fine_mesh = []          # points for fine meshing

        self.active_earth_pressure_wedge = {}   # active earth pressure wedge

        self.delta_support_to_ground = 0.5  # distance from the support structure to the current excavation level
        self.delta_ground_to_water = 0.5    # distance from the current excavation level to the dewatering level
        self.deltas_support_to_ground = {}  # for updating phases data
        self.deltas_ground_to_water = {}    # for updating phases data
        self.phases_already_generated = False   # if the automated phases have been generated
        self.reset_displ_zero_dewatering = []
        self.reset_displ_zero_excavation = []
        self.reset_displ_zero_supporting = []

        self.ap_groupbox_ui = None  # groupbox for table of the generated automated phases
        
        # connect signals
        self.connect_signals_to_slots()
        
        
    
    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.lineEdit_59.setStyleSheet("background-color: rgb(242, 255, 116);")
        self.ui.lineEdit_59.returnPressed.connect(lambda: self.update_final_excavation_level(float(self.ui.lineEdit_59.text()), self.geometry[0]))
        self.ui.lineEdit_60.setStyleSheet("background-color: rgb(242, 255, 116);")
        #self.ui.lineEdit_60.returnPressed.connect(lambda: self.update_final_excavation_level(float(self.ui.lineEdit_59.text()), self.x_min))    # make sure that final excavation level is there
        self.ui.lineEdit_60.returnPressed.connect(lambda: self.update_embedment_depth(float(self.ui.lineEdit_60.text())))
        self.ui.tableWidget_19.cellChanged.connect(lambda row, column: self.update_skin_friction_for_soil_layer(row, column, self.Layer_polygons)) # update skin resistance for anchor's grout bodies


        
        
    def display_all_model_components(self):
        """ Displays all model components on tables
        """
        self.x_min = self.geometry[0]
        self.x_max = self.geometry[2]
        self.y_max = self.geometry[3]
        self.y_min = self.geometry[1]
        
        self.update_walls()
        
        if 'level' in self.final_excavation_level:
            self.ui.lineEdit_59.setText(str(self.final_excavation_level['level']))
            # plot final excavation line
            self.final_excavation_level['pathpatch'] = self.plot_canvas.plot_final_excavation_level(self.final_excavation_level['level'], self.x_min, self.wall['point1'][0])
        
        if 'depth_embedment' in self.wall:
            self.ui.lineEdit_60.setText(str(self.wall['depth_embedment']))
        
        self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_18, active=False)
        self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_20, active=False)

        # display anchors' soil layer dependent skin frictions
        self.display_anchor_soil_layer_dependent_skin_frictions(self.Layer_polygons)

        # write points for berms
        self.write_points_berm_top()
        self.write_points_berm_bottom()

        # Check pore pressure interpolation or not
        if self.pore_pressure_interp:
            self.ui.checkBox_9.setCheckState(2)      
        # Check FoS phase
        if self.FoS_phase:
            self.ui.checkBox_10.setCheckState(2)
            
        
    def update_walls(self):
        """ Inserts wall ID in combobox
        """
        if self.Walls:
            # Inserts wall ids in comboBox
            self.ui.comboBox_36.clear()
            ids = [str(wall['id']) for wall in self.Walls]
            self.ui.comboBox_36.addItems(ids)
            self.wall = self.Walls[0]

            if ids: # if at least a wall is inserted, suggest final excavation level as two thirds of wall length
                #self.suggest_final_excavation_level(self.Walls[-1])
                pass


    def remove_automated_phases(self):
        """ Remove all generated phases
        Therefore, all soilclusters, Waterlevels will be removed as well
        """

        self.remove_all_phases(self.Phases, self.Soilclusters, self.Soilclusters_notdried)
        self.update_phase_table(self.Phases)

        # remove soil clusters, water levels, and reset_displ_zero
        self.remove_all_soilclusters(self.Soilclusters, self.Soilclusters_notdried)
        self.remove_all_waterlevels(self.Waterlevels)
        self.remove_all_drains(self.Drains) # in case the previously generated phases are created by steady state ground water
        self.remove_all_reset_displ_zero()

        # remove data for phases
        self.Phases_data.clear()

        # clear final excavation level
        #self.final_excavation_level.clear()

        # undo refining the mesh
        if self.points_fine_mesh: # undo only if these polygon points are not empty
            self.undo_refine_mesh_around_wall()

        # remove active earth pressure wedge
        self.add_active_earthpressure_wedge(False)

        self.phases_already_generated = False


    def check_constraints(self, constraint_items):
        """ Check if the design variables satisfy constraints
        """
        constraint_value = 0

        # sort Anchors by level (highest to lowest)
        #Anchors_sorted = sorted((anchor for anchor in self.Anchors), key = lambda anchor: anchor['position'][1], reverse=True)
        Anchors_sorted = self.Anchors # no sort, to check constraint condition for anchor level

        # check for distance between two ground anchors 
        if (len(Anchors_sorted) > 1) and ('anchor_distance' in constraint_items):
            # distance between all 2-anchor combinations must be larger than the min allowable distance
            for i in range(0, len(Anchors_sorted)-1):
                for j in range(i+1, len(Anchors_sorted)):
                    d_i_plus_1 = calc_dist_2p(Anchors_sorted[i]['position'], Anchors_sorted[j]['position'])
                    if (d_i_plus_1 < constraint_items['anchor_distance'][0]):
                        constraint_value += 1

            # distance between two nearby anchors must be smaller than the max allowable distance
            for i in range(0, len(Anchors_sorted)-1):
                d_nearby_anchors = calc_dist_2p(Anchors_sorted[i]['position'], Anchors_sorted[i+1]['position'])
                if (d_nearby_anchors > constraint_items['anchor_distance'][1]):
                    constraint_value += 1

            for i in range(0, len(Anchors_sorted)-1):
                position_i_plus_1 = Anchors_sorted[i+1]['position'][1]
                if Anchors_sorted[i]['position'][1] <= position_i_plus_1: # Lower anchor is placed above upper anchor
                    constraint_value += 1

        # check for angle between two ground anchors 
        if len(Anchors_sorted) > 1:
            for i in range(0, len(Anchors_sorted)-1):
                #for j in range(i+1, len(Anchors_sorted)):
                angle_i_plus_1 = Anchors_sorted[i+1]['angle']
                angle_diff = abs(angle_i_plus_1) - abs(Anchors_sorted[i]['angle'])
                if angle_diff < -1.0:
                    constraint_value += 1
                    #print('Anchor angle violated!')

        # update points for active earth pressure wedge
        if self.active_earth_pressure_wedge:
            constraint_items['active_earthpressure_points'] = self.active_earth_pressure_wedge['points']
        # check for active earth pressure wedge, grout body should be below this wedge
        if 'active_earthpressure_points' in constraint_items:
            for anchor in Anchors_sorted:
                is_violated = self.is_grout_body_above_earthpressure_wedge(constraint_items['active_earthpressure_points'], anchor)
                if is_violated:
                    constraint_value += 1
                    #print('Active earthpressure wedge violated!')


        return int(constraint_value)


    def is_grout_body_above_earthpressure_wedge(self, active_earthpressure_points, anchor):
        """ Checks if any grout body of the ground anchor is above the active earth pressure wedge
        """
        result = False
        for point1, point2 in zip(active_earthpressure_points[:-1], active_earthpressure_points[1:]):
            X = np.array([[point1[0],1], [point2[0],1]])
            y = np.array([point1[1], point2[1]])
            c = np.linalg.solve(X, y) # a = c[0], b = c[1], y = ax + b
            # where the grout body is
            grout_point_start, _ = get_anchor_grout_endpoints(anchor['position'], anchor['angle'], anchor['length_free'], anchor['length_fixed'])
            if grout_point_start[1] > c[0] * grout_point_start[0] + c[1]: #y coordinate of grout's starting point is above the active earthpressure wedge line
                result = True
        
        return result


    @pyqtSlot()
    def add_active_earthpressure_wedge(self, checked):
        """ Adds an active earthpressure wedge (a multi-linear line) that prohibits grout parts of ground anchors to be embedded in
        """
        #print('add_active_earthpressure_wedge is called')
        if checked:
            wall_bottom_x = self.wall['point2'][0]
            wall_bottom_y = self.wall['point2'][1]

            points_active_wedge = [(wall_bottom_x, wall_bottom_y)]
            self.active_earth_pressure_wedge['points'] = points_active_wedge

            for layer_i, layer_polygon in reversed(list(enumerate(self.Layer_polygons))): # loop in reversed order
                if self.Boreholes[0]['Top'][layer_i] > wall_bottom_y: # top of the current soil layer is above wall bottom level
                    soilmaterial_layer = layer_polygon['soilmaterial_layer']
                    #print(layer_i, soilmaterial_layer)
                    phi_layer_i = self.read_soil_parameter(soilmaterial_layer, 'phi')    # friction angle of this layer
                    #print(phi_layer_i)
                    b = points_active_wedge[-1][1] - np.tan((90 - (45-phi_layer_i/2)) * np.pi/180) * points_active_wedge[-1][0] # y = tan(phi) * x + b
                    y_layer_i = self.Boreholes[0]['Top'][layer_i]
                    x_layer_i = (y_layer_i - b)/np.tan((90 - (45-phi_layer_i/2)) * np.pi/180)
                    points_active_wedge.append((x_layer_i, y_layer_i))
            
            #print(points_active_wedge)
            self.active_earth_pressure_wedge['pathpatches'] = self.plot_canvas.plot_multilinear_earth_pressure_wedge(points_active_wedge)
        
        else: # remove active wedge
            #self.plot_canvas.undo_plot_pathpatches(self.active_earth_pressure_wedge['pathpatches'])
            #self.active_earth_pressure_wedge.clear()
            if 'pathpatches' in self.active_earth_pressure_wedge:
                self.plot_canvas.undo_plot_pathpatches(self.active_earth_pressure_wedge['pathpatches'])
                self.active_earth_pressure_wedge.clear()


    def read_soil_parameter(self, json_item, soilparameter):
        """ Reads value of the soil parameter in json item
        """
        PATHS = sys.modules['moniman_paths']
        PATH_MATERIAL = os.path.join(PATHS['MONIMAN_OUTPUTS'], r'materials')
        fname = os.path.join(PATH_MATERIAL, json_item + '.json')
        if os.path.isfile(fname):
            with open(fname, "r") as read_file:
                materials_data = json.load(read_file, object_pairs_hook = OrderedDict)         
                return materials_data[soilparameter]

        else: # json file does not exist
            return None


    def assign_design_variables_to_model(self, v, variables_wall, variables_anchors, variables_struts):
        """ Assigns current design variables v to plaxis model
        """
        cnt = 0
        # wall variables
        if variables_wall:
            wall_id = variables_wall['id']
            if self.wall['id'] == int(wall_id):
                for key, _ in variables_wall.items():
                    if key != 'id':
                        if key == 'depth_embedment': # update wall embedment depth
                            #print(key, value)
                            self.wall[key] = v[cnt]
                            variables_wall[key] = v[cnt]
                            self.update_embedment_depth__(v[cnt])
                            if 'SPW' == self.wall['wall_type']:
                                self.update_SPW_parameters_with_embedment_depth()  # change in embedment depth leads to change in SPW spacings for SPW
                            cnt += 1

                        elif (key=='D') and ('SPW' == self.wall['wall_type']): # adjust spacings for SPW following D
                            self.update_SPW_parameters_with_D(v[cnt])
                            cnt += 1

                        else:
                            #print(key, value)
                            self.wall[key] = v[cnt]
                            update_data_in_json_item(self.wall['json_item'], {key: v[cnt]})
                            cnt += 1

        # variables for ground anchors
        for variables_anchor in variables_anchors:
            anchor_id = list(variables_anchor.keys())[0]
            for key, _ in variables_anchor[anchor_id].items():
                #print(key, value)
                variables_anchor[anchor_id][key] = v[cnt]
                self.plaxman_x.update_ground_anchor_by_id__(anchor_id, key, v[cnt], self.Anchors)
                cnt += 1

        # variables for struts
        for variables_strut in variables_struts:
            strut_id = list(variables_strut.keys())[0]
            for key, _ in variables_strut[strut_id].items():
                #print(key, value)
                variables_strut[strut_id][key] = v[cnt]
                self.update_strut_by_id__(strut_id, key, v[cnt], self.Struts)
                cnt += 1

        # adjust observation points for ground anchors
        self.adjust_observation_points_for_ground_anchors()

        #return cnt


    def update_SPW_parameters_with_D(self, D):
        """ Update SPW parameters following pile diameter D
        """
        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        L = calc_dist_2p(wall_point1, wall_point2)  # wall length
        S = D - L*0.01  # drilling deviation by 1% of the pile length
        (EA, EA2, EI, w, d, Gref) = get_SPW_parameters(D, S)
        update_data_in_json_item(self.wall['json_item'], {'D': D, 'S': S, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'd': d, 'Gref': Gref}) # spacing b/t piles
        # adjust Lspacing for anchors
        for anchor in self.Anchors:
            update_data_in_json_item(anchor['strand_json_item'], {'Lspacing': 2*S})
            update_data_in_json_item(anchor['grout_json_item'], {'Lspacing': 2*S})


    def update_SPW_parameters_with_embedment_depth(self):
        """ Update SPW parameters following change in embedment depth
        """
        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        L = calc_dist_2p(wall_point1, wall_point2)  # wall length
        D = read_data_in_json_item(self.wall['json_item'], 'D')
        S = D - L*0.01  # drilling deviation by 1% of the pile length
        (EA, EA2, EI, w, d, Gref) = get_SPW_parameters(D, S)
        update_data_in_json_item(self.wall['json_item'], {'D': D, 'S': S, 'EA': EA, 'EA2': EA2, 'EI': EI, 'w': w, 'd': d, 'Gref': Gref}) # spacing b/t piles
        # adjust Lspacing for anchors
        for anchor in self.Anchors:
            update_data_in_json_item(anchor['strand_json_item'], {'Lspacing': 2*S})
            update_data_in_json_item(anchor['grout_json_item'], {'Lspacing': 2*S})


    def adjust_observation_points_for_ground_anchors(self):
        """ As ground anchors change their positions, the observation points for them must change too
        """
        for points_obs in self.Points_obs:
            if points_obs['obs_type'] == 'AnchorForce':
                self.plot_canvas.undo_plot_pathpatches(points_obs['pathpatches'])
                plaxis2d_input.remove_structure(self.plaxis2d_input_file, points_obs['id'], '##POINTS_OBS', 4)
                points_obs['points'].clear()
                Anchors_sorted = sorted((anchor for anchor in self.Anchors), key = lambda anchor: anchor['position'][1], reverse=True)
                for anchor in Anchors_sorted:
                    points_obs['points'].append(anchor['position'])

                points_obs['pathpatches'] = self.plot_canvas.plot_points(points_obs['points'], 'red')
                plaxis2d_input.add_observed_points(self.plaxis2d_input_file, 'g_i', points_obs)


    def estimate_total_cost(self, Nx_max=0.0, M_max=0.0, Q_max=0.0):
        """ Estimates the total construction cost based on the current components of the design
        This cost is now relative for comparision of objective values
        """
        # installation speed for wall and anchor
        #install_speed_wall = float(self.ui.lineEdit_66.text())
        #install_speed_anchor = float(self.ui.lineEdit_67.text())

        # unit costs
        UnitCosts = namedtuple('UnitCosts', 'concrete_volume, steel, anchor_length, stone_columns, rigid_inclusions, BG_per_day, anchor_installer_per_day, mobilization')
        
        # read user input from table
        user_costs = []
        for j in range(self.ui.tableWidget_23.columnCount()):
            user_costs.append(float(self.ui.tableWidget_23.item(0, j).text()))
        
        ## update unit_costs
        unit_costs = UnitCosts(*user_costs)

        cost = 0.0
        # cost for wall per linear perimeter meter
        #cost += self.calc_concrete_cost(unit_costs)
        wall_cost_factory = StructureCostFactory()
        if 'Dwall' == self.wall['wall_type']:
            cost_wall = wall_cost_factory.get_cost_structure('DWall', self.wall, unit_costs, Nx_max, M_max, Q_max)
            cost += cost_wall.calculate_cost()
        else:
            cost_wall = wall_cost_factory.get_cost_structure('PWall', self.wall, unit_costs, Nx_max, M_max, Q_max)
            cost += cost_wall.calculate_cost()

        # cost for ground anchors
        cost += self.calc_ground_anchor_cost(unit_costs)

        return cost


    def calc_ground_anchor_cost(self, uint_costs):
        """ Calculates cost for ground anchor per cross-section linear meter
        """
        cost_ground_anchor = 0.0
        #for variables_anchor in variables_anchors:
        #    anchor_id = list(variables_anchor.keys())[0]
        #    for key, _ in variables_anchor[anchor_id].items():
        #        if key == 'length_free':
        #            cost += unit_costs.anchor_length * variables_anchor[anchor_id]['length_free']
        #            cost += unit_costs.anchor_installer_per_day * install_speed_anchor * variables_anchor[anchor_id]['length_free']

        for anchor in self.Anchors:
            length_anchor = anchor['length_free'] + anchor['length_fixed']
            Lspacing = anchor['Lspacing']
            cost_ground_anchor += (length_anchor * uint_costs.anchor_length)/Lspacing
        
        return cost_ground_anchor


    def setup_automated_phases(self):
        """ Starts generating automated phases
        """
        if (self.ui.checkBox_20.checkState() == 2):   # steady state ground water flow
            pass

        else: # phreatic
            self.setup_automated_phases_phreatic()


    def setup_automated_phases_phreatic(self):
        """ Starts generating automated phases using phreatic water levels
        """
        self.x_min = self.geometry[0]
        self.x_max = self.geometry[2]
        self.y_max = self.geometry[3]
        self.y_min = self.geometry[1]


        # check if 'FoS phase' is checked
        if (self.ui.checkBox_10.checkState() == 2):
            self.FoS_phase = True
        else:
            self.FoS_phase = False

        try:
            wall_id = int(self.ui.comboBox_36.currentText()) # wall id selected
            final_exc_level = float(self.ui.lineEdit_59.text())
            depth_embedment = float(self.ui.lineEdit_60.text())

            if (self.ui.checkBox_9.checkState() == 2):
                self.pore_pressure_interp = True
                self.setup_automated_phases_porepressure_interpolation(wall_id, final_exc_level, depth_embedment)
            else:
                self.pore_pressure_interp = False
                self.setup_automated_phases_no_porepressure_interpolation(wall_id, final_exc_level, depth_embedment)

            # refine mesh around wall
            self.refine_mesh_around_wall(self.wall, self.x_min, self.x_max, self.Boreholes)
            

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')   
    

    def read_points_berm(self):
        """ Read in points for the berm
        """
        str_x_coordinates = self.ui.lineEdit_63.text()
        str_y_coordinates = self.ui.lineEdit_64.text()
        x_coordinates = []
        y_coordinates = []
        if str_x_coordinates != '':
            x_coordinates = [float(x) for x in str_x_coordinates.split(',')]
        if str_y_coordinates != '':
            y_coordinates = [float(y) for y in str_y_coordinates.split(',')]
        
        if x_coordinates and y_coordinates and (len(x_coordinates) == len(y_coordinates)):
            ind_sorted = sorted(range(len(x_coordinates)), key=lambda k: x_coordinates[k]) # ascending order in x
            x_coordinates_sorted = [x_coordinates[idx] for idx in ind_sorted]
            y_coordinates_sorted = [y_coordinates[idx] for idx in ind_sorted]
            self.points_berm['x_coordinates'] = x_coordinates_sorted
            self.points_berm['y_coordinates'] = y_coordinates_sorted
            
        else:
            self.points_berm.clear()


    def read_points_berm_base(self):
        """ Read in points for the berm
        """
        str_x_coordinates = self.ui.lineEdit_12.text()
        str_y_coordinates = self.ui.lineEdit_90.text()
        x_coordinates = []
        y_coordinates = []
        if str_x_coordinates != '':
            x_coordinates = [float(x) for x in str_x_coordinates.split(',')]
        if str_y_coordinates != '':
            y_coordinates = [float(y) for y in str_y_coordinates.split(',')]
        
        if x_coordinates and y_coordinates and (len(x_coordinates) == len(y_coordinates)):
            ind_sorted = sorted(range(len(x_coordinates)), key=lambda k: x_coordinates[k]) # ascending order in x
            x_coordinates_sorted = [x_coordinates[idx] for idx in ind_sorted]
            y_coordinates_sorted = [y_coordinates[idx] for idx in ind_sorted]
            self.points_berm_base['x_coordinates'] = x_coordinates_sorted
            self.points_berm_base['y_coordinates'] = y_coordinates_sorted
            
        else:
            self.points_berm_base.clear()


    def write_points_berm_top(self):
        """ Write points for berm to UI
        """
        if self.points_berm:
            try:
                x_str = ', '.join(str(x) for x in self.points_berm['x_coordinates'])
                y_str = ', '.join(str(y) for y in self.points_berm['y_coordinates'])
                self.ui.lineEdit_63.setText(x_str)
                self.ui.lineEdit_64.setText(y_str)
            except:
                pass


    def write_points_berm_bottom(self):
        """ Write points for berm to UI
        """
        if self.points_berm_base:
            try:
                x_str = ', '.join(str(x) for x in self.points_berm_base['x_coordinates'])
                y_str = ', '.join(str(y) for y in self.points_berm_base['y_coordinates'])
                self.ui.lineEdit_12.setText(x_str)
                self.ui.lineEdit_90.setText(y_str)
            except:
                pass


    def initialize_automated_phases_table(self):
        """ Initializes table for showing the automatically generated phases
        """
        for i in reversed(range(self.ui.gridLayout_56.count())):
            #self.ui.gridLayout_56.itemAt(i).widget().setParent(None)
            item_old = self.ui.gridLayout_56.itemAt(i)
            self.ui.gridLayout_56.removeItem(item_old)

        # initialize groupbox
        GroupBox = QtWidgets.QGroupBox()
        automated_phase_groupbox_ui = automatedPhasesGroupBox()
        automated_phase_groupbox_ui.setupUi(GroupBox)

        # add widgets
        self.ui.gridLayout_56.addWidget(GroupBox)

        return automated_phase_groupbox_ui


    def setup_automated_phases_no_porepressure_interpolation(self, wall_id, final_exc_level, depth_embedment):
        """ Sets up wall, final excavation level, and support structures.
        Wall foot can be updated depending on embedment depth
        This function will genertate the phases and create connections to slots.
        The function is connected with the pushbutton 'Set', which must be clicked once to initate automated phases.
        """
        print('\nSTART SETTING UP AUTOMATED CALCULATION PHASES...')
        for wall in self.Walls:
            if wall['id'] == wall_id:
                self.wall = wall    # set wall for class attribute

        # set final excavation level
        self.update_final_excavation_level(final_exc_level, self.x_min)

        # set wall embedment depth (this means to change the wall foot)
        self.update_embedment_depth(depth_embedment)

        # insert ground anchors and struts
        self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_18, active=False)
        self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_20, active=False)

        # display anchors' soil layer dependent skin frictions
        self.display_anchor_soil_layer_dependent_skin_frictions(self.Layer_polygons)

        # clear data for phases
        print('CLEAR PREVIOUSLY PHASES, SOIL CLUSTER, AND USER WATER LEVELS...')
        self.clear_phases_data()
    
        # read berm coordinates
        self.read_points_berm()
        self.read_points_berm_base()

        # generate soilclusters and user water levels in relation with supporting structures (only ground anchors now)
        print('GENERATE SOIL CLUSTERS AND USER WATER LEVELS...')
        self.setup_soilclusters_and_waterlevels()
        self.apply_mesh()

        # add calculation phases
        print('GENERATE CALCULATION PHASES...')
        # construct wall(s)
        self.add_phase_wall_construction(self.Phases, self.Walls, self.Lineloads, self.Pointloads, self.Anchors, self.Struts)
        # dewater and excavate
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        if (self.Anchors + Struts_only):
            Structures = self.Anchors + Struts_only
            Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
            #Anchors_sorted = sorted((anchor for anchor in Anchors), key = lambda anchor: anchor['position'][1], reverse=True)
            #for phase_i, anchor in enumerate(Anchors_sorted):
            for phase_i, structure in enumerate(Structures_sorted):
                # reset displacement or not
                reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, reset_displ_zero_supporting_phase_i = self.set_up_reset_displacements_to_zero(phase_i)

                soilcluster_ids_dewatering = self.Phases_data[phase_i]['soilcluster_ids'] + self.Phases_data[phase_i+1]['soilcluster_ids'] # one additional soil cluster below is considered
                # add dewatering phase if the current excavation level is below the global water level
                if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                    self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                # add excavation phase
                self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], self.deltas_support_to_ground[structure['id']], reset_displ_zero=reset_displ_zero_excavation_phase_i)

                if 'usage' not in structure: # 'usage' key indicates struts
                    F_prestress = structure['F_prestress']
                    self.add_phase_anchoring(self.Phases, self.Anchors, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)
                else: # it is a strut
                    # add struting phase
                    F_prestress = structure['F_prestress']
                    self.add_phase_struting(self.Phases, self.Struts, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)
        
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i+1)
            # add final dewatering and excavation phase
            soilcluster_ids_dewatering = self.Phases_data[phase_i+1]['soilcluster_ids'] + self.Phases_data[phase_i+2]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i+1]['waterlevel_id'] is not None) and (self.Phases_data[phase_i+1]['excavation_level'] < self.Boreholes[0]['Head']):
                self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i+1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        else: # Cantilever wall
            phase_i = 0
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i)
            soilcluster_ids_dewatering = self.Phases_data[phase_i]['soilcluster_ids'] + self.Phases_data[phase_i+1]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        # Add reconstruction phases
        Slabs_only = [strut for strut in self.Struts if strut['usage']=='Slab']# Slabs for reconstructions
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Slabs_only_sorted = sorted((structure for structure in Slabs_only), key = lambda structure: structure['position'][1], reverse=False)    # bottom to top
        #Struts_only_sorted = sorted((structure for structure in Struts_only), key = lambda structure: structure['position'][1], reverse=False)  # bottom to top
        for i_slab, slab in enumerate(Slabs_only_sorted):
            self.add_phase_struting(self.Phases, self.Struts, [slab['id']], [slab['F_prestress']])        # constructing a raft or floor slab
            if i_slab < (len(Slabs_only_sorted) - 1):   # deconstruct struts above and between 2 slabs
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if (strut['position'][1] < Slabs_only_sorted[i_slab+1]['position'][1]) and (strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]):
                        strut_ids_to_deconstruct.append(strut['id'])
            else: # all struts above the top slab
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]:
                        strut_ids_to_deconstruct.append(strut['id'])
            if strut_ids_to_deconstruct:    # when not empty only
                self.add_phase_struting(self.Phases, self.Struts, strut_ids_to_deconstruct, [slab['F_prestress']], deconstruct=True)   # removing a temporary strut

        # Add safty phase
        if self.FoS_phase:
            if self.points_berm:
                self.add_phase_safety(self.Phases, self.points_berm['soilcluster_id_no_strength_reduction'])
            else:
                self.add_phase_safety(self.Phases)

        # Update Tskin for multilinear grout body for ground anchors
        self.assign_anchor_multilinear_skin_resistance(self.Anchors, self.Layer_polygons, self.Boreholes)

        # Update phase table in Predefined phases
        self.update_phase_table(self.Phases)

        # Update phase table in Automated phases
        self.ap_groupbox_ui = self.initialize_automated_phases_table()
        #self.update_phase_table_automated_phases(Phases, self.ap_groupbox_ui.tableWidget)
        self.update_phase_table_automated_phases(self.Phases, self.ap_groupbox_ui.tableWidget, self.Anchors)

        # Add active earth pressure wedge
        self.add_active_earthpressure_wedge(True)

        self.phases_already_generated = True



    def setup_soilclusters_and_waterlevels(self):
        """ Gernerate soilclusters and user water level automatically (no pore pressure interpolation)
        Necessary information for creating the calculation phases is stored in self.Phases_data
        """
        # add berm data if berm coordinates are available
        if self.points_berm:
            pointTL, pointTR = self.add_soil_cluser_berm_top()

        else:
            pointTL = [self.x_min, max(self.wall['point1'][1], self.Boreholes[0]['Top'][0])]
            pointTR = [self.wall['point1'][0], max(self.wall['point1'][1], self.Boreholes[0]['Top'][0])]

        # loop support structures for adding soil clusters and user water levels
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Structures = self.Anchors + Struts_only
        Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
        i_existing_user_water_item = 0
        for structure in Structures_sorted:
            if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
                soilcluster_bottom = structure['position'][1] - self.delta_support_to_ground
                self.deltas_support_to_ground[structure['id']] = self.delta_support_to_ground
            else:   # if automated phases are already generated
                soilcluster_bottom = structure['position'][1] - self.deltas_support_to_ground[structure['id']]

            soilcluster_ids = []
            # create a soil cluster having bottom at the soilcluster_bottom
            pointBL = [self.x_min, soilcluster_bottom]
            pointBR = [self.wall['point1'][0], soilcluster_bottom]
            soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'])
            soilcluster_ids.append(soilcluster_id)
            pointTL = pointBL
            pointTR = pointBR
            waterlevel_id = None
            if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
                waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.delta_ground_to_water)
                waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.delta_ground_to_water)
                # add user water level conditionally
                if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                    waterlevel_id = self.add_waterlevel__(self.Waterlevels, waterlevel_pointL, waterlevel_pointR)
                    self.deltas_ground_to_water[waterlevel_id] = self.delta_ground_to_water
                else:
                    waterlevel_id = None
            else:   # if automated phases are already generated
                if self.Waterlevels:
                    waterlevel_id = self.Waterlevels[i_existing_user_water_item]['id']
                    waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.deltas_ground_to_water[waterlevel_id])
                    waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.deltas_ground_to_water[waterlevel_id])
                    # add user water level conditionally
                    if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                        self.update_user_water_level(self.deltas_ground_to_water, pointBL, self.Waterlevels, waterlevel_id) # update all user water levels !!!
                        i_existing_user_water_item += 1
                    else:
                        waterlevel_id = None

            phase_data = {}
            phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
            if self.points_berm:
                phase_data['soilcluster_ids'] = soilcluster_ids + self.points_berm['soilcluster_id']  # soilcluster ids for excavation
                self.points_berm['soilcluster_id'].clear()
            else:
                phase_data['soilcluster_ids'] = soilcluster_ids # soilcluster ids for excavation
            phase_data['excavation_level'] = soilcluster_bottom  # intermediate excavation level
            self.Phases_data.append(phase_data)

        # the soilcluster(s) until the final excavation level
        soilcluster_bottom = self.final_excavation_level['level']
        soilcluster_ids = []
        if self.points_berm_base:
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_with_bottom_berm(self.Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
            self.Phases_data.append(phase_data)
        else:
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_no_bottom_berm(self.Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
            self.Phases_data.append(phase_data)

        # the soilcluster(s) until 3m below the final excavation level
        soilcluster_bottom = self.final_excavation_level['level'] - 3
        soilcluster_ids = []
        # create a soil cluster having bottom at the soilcluster_bottom
        pointBL = [self.x_min, soilcluster_bottom]
        pointBR = [self.wall['point1'][0], soilcluster_bottom]
        soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'], annotate=False)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        phase_data = {}
        #phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        phase_data['soilcluster_ids'] = soilcluster_ids   # soilcluster ids for excavation
        #phase_data['excavation_level'] = self.final_excavation_level['level']  # final excavation level
        self.Phases_data.append(phase_data)



    def setup_automated_phases_porepressure_interpolation(self, wall_id, final_exc_level, depth_embedment):
        """ Sets up wall, final excavation level, and support structures.
        Wall foot can be updated depending on embedment depth
        This function will genertate the phases and create connections to slots.
        The function is connected with the pushbutton 'Set', which must be clicked once to initate automated phases.
        """
        print('\nSTART SETTING UP AUTOMATED CALCULATION PHASES...')
        for wall in self.Walls:
            if wall['id'] == wall_id:
                self.wall = wall    # set wall for class attribute

        # set final excavation level
        self.update_final_excavation_level(final_exc_level, self.x_min)

        # set wall embedment depth (this means to change the wall foot)
        self.update_embedment_depth(depth_embedment)

        # insert ground anchors and struts
        self.plaxman_x.display_ground_anchors_on_table(self.Anchors, self.ui.tableWidget_18, active=False)
        self.plaxman_x.display_struts_on_table(self.Struts, self.ui.tableWidget_20, active=False)

        # display anchors' soil layer dependent skin frictions
        self.display_anchor_soil_layer_dependent_skin_frictions(self.Layer_polygons)

        # clear data for phases
        print('CLEAR PREVIOUSLY PHASES, SOIL CLUSTER, AND USER WATER LEVELS...')
        self.clear_phases_data()
    
        # read berm coordinates
        self.read_points_berm()
        self.read_points_berm_base()

        # generate soilclusters and user water levels in relation with supporting structures (only ground anchors now)
        print('GENERATE SOIL CLUSTERS AND USER WATER LEVELS...')
        self.setup_soilclusters_and_waterlevels_porepressure_interpolation()
        self.apply_mesh()

        # add calculation phases
        print('GENERATE CALCULATION PHASES (WITH PORE PRESSURE INTERPOLATION)...')
        # construct wall(s)
        self.add_phase_wall_construction(self.Phases, self.Walls, self.Lineloads, self.Pointloads, self.Anchors, self.Struts)
        # dewater and excavate
        alreadyInterpolated = False
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        if (self.Anchors + Struts_only):
            Structures = self.Anchors + Struts_only
            Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
            #Anchors_sorted = sorted((anchor for anchor in Anchors), key = lambda anchor: anchor['position'][1], reverse=True)
            for phase_i, structure in enumerate(Structures_sorted):
                # reset displacement or not
                reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, reset_displ_zero_supporting_phase_i = self.set_up_reset_displacements_to_zero(phase_i)

                # all soil clusters except the ones below the wall toe are considered
                soilcluster_ids_dewatering = [soilcluster_id for phase_data in self.Phases_data[phase_i:-1] for soilcluster_id in phase_data['soilcluster_ids']]  
                # add dewatering phase if the current excavation level is below the global water level
                if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                    if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                        self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                        alreadyInterpolated = True
                    else:
                        self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)

                # add excavation phase
                self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], self.deltas_support_to_ground[structure['id']], reset_displ_zero=reset_displ_zero_excavation_phase_i)

                if 'usage' not in structure: # 'usage' key indicates struts
                    F_prestress = structure['F_prestress']
                    self.add_phase_anchoring(self.Phases, self.Anchors, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)
                else:   # it is a strut
                    # add struting phase
                    F_prestress = structure['F_prestress']
                    self.add_phase_struting(self.Phases, self.Struts, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)

            # add final dewatering and excavation phase
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i+1)
            # all soil clusters except the ones below the wall toe are considered
            soilcluster_ids_dewatering = [soilcluster_id for phase_data in self.Phases_data[phase_i+1:-1] for soilcluster_id in phase_data['soilcluster_ids']]  # all soil clusters considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i+1]['waterlevel_id'] is not None) and (self.Phases_data[phase_i+1]['excavation_level'] < self.Boreholes[0]['Head']):
                if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                    self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                    alreadyInterpolated = True
                else:
                    self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i+1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        else: # Cantilever wall
            alreadyInterpolated = False
            phase_i = 0
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i)
            soilcluster_ids_dewatering = self.Phases_data[phase_i]['soilcluster_ids'] + self.Phases_data[phase_i+1]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                    self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                    alreadyInterpolated = True
                else:
                    self.add_phase_dewatering(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        # Add reconstruction phases
        Slabs_only = [strut for strut in self.Struts if strut['usage']=='Slab']# Slabs for reconstructions
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Slabs_only_sorted = sorted((structure for structure in Slabs_only), key = lambda structure: structure['position'][1], reverse=False)    # bottom to top
        #Struts_only_sorted = sorted((structure for structure in Struts_only), key = lambda structure: structure['position'][1], reverse=False)  # bottom to top
        for i_slab, slab in enumerate(Slabs_only_sorted):
            self.add_phase_struting(self.Phases, self.Struts, [slab['id']], [slab['F_prestress']])        # constructing a raft or floor slab
            if i_slab < (len(Slabs_only_sorted) - 1):   # deconstruct struts above and between 2 slabs
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if (strut['position'][1] < Slabs_only_sorted[i_slab+1]['position'][1]) and (strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]):
                        strut_ids_to_deconstruct.append(strut['id'])
            else: # all struts above the top slab
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]:
                        strut_ids_to_deconstruct.append(strut['id'])
            if strut_ids_to_deconstruct:    # when not empty only
                self.add_phase_struting(self.Phases, self.Struts, strut_ids_to_deconstruct, [slab['F_prestress']], deconstruct=True)   # removing a temporary strut

        # Add safety phase
        if self.FoS_phase:
            if self.points_berm:
                self.add_phase_safety(self.Phases, self.points_berm['soilcluster_id_no_strength_reduction'])
            else:
                self.add_phase_safety(self.Phases)
        
        # Update Tskin for multilinear grout body for ground anchors
        self.assign_anchor_multilinear_skin_resistance(self.Anchors, self.Layer_polygons, self.Boreholes)

        # Update phase tables once
        self.update_phase_table(self.Phases)
        
        # Update phase table in Automated phases
        self.ap_groupbox_ui = self.initialize_automated_phases_table()
        self.update_phase_table_automated_phases(self.Phases, self.ap_groupbox_ui.tableWidget, self.Anchors)

        # Add active earth pressure wedge
        self.add_active_earthpressure_wedge(True)

        self.phases_already_generated = True


    def set_up_reset_displacements_to_zero(self, phase_i):
        if len(self.reset_displ_zero_dewatering) < (phase_i+1):
            reset_displ_zero_dewatering_phase_i = False
            self.reset_displ_zero_dewatering.append(reset_displ_zero_dewatering_phase_i)
        else:
            reset_displ_zero_dewatering_phase_i = self.reset_displ_zero_dewatering[phase_i]

        if len(self.reset_displ_zero_supporting) < (phase_i+1):
            reset_displ_zero_supporting_phase_i = False
            self.reset_displ_zero_supporting.append(reset_displ_zero_supporting_phase_i)
        else:
            reset_displ_zero_supporting_phase_i = self.reset_displ_zero_supporting[phase_i]

        if len(self.reset_displ_zero_excavation) < (phase_i+1):
            reset_displ_zero_excavation_phase_i = False
            self.reset_displ_zero_excavation.append(reset_displ_zero_excavation_phase_i)
        else:
            reset_displ_zero_excavation_phase_i = self.reset_displ_zero_excavation[phase_i]
        
        return reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, reset_displ_zero_supporting_phase_i


    #@profile
    def setup_automated_phases_porepressure_interpolation__(self):
        """ Sets up wall, final excavation level, and support structures.
        Wall foot can be updated depending on embedment depth
        This function will genertate the phases and create connections to slots.
        The function is connected with the pushbutton 'Set', which must be clicked once to initate automated phases.
        """
        self.phases_already_generated = False   #!!!

        # clear data for phases
        self.clear_phases_data__(self.Phases, self.Walls, self.Lineloads, self.Pointloads, self.Soilclusters, self.Soilclusters_notdried, self.Anchors, self.Struts, 
                    self.Waterlevels, self.Drain)
        #self.clear_phases_data()
    
        # generate soilclusters and user water levels in relation with supporting structures (only ground anchors now)
        self.setup_soilclusters_and_waterlevels_porepressure_interpolation()

        # add calculation phases
        # construct wall(s)
        self.add_phase_wall_construction__(self.Phases, self.Walls, self.Lineloads, self.Pointloads, self.Anchors, self.Struts)
        # dewater and excavate
        alreadyInterpolated = False
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        if (self.Anchors + Struts_only):
            Structures = self.Anchors + Struts_only
            Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
            #Anchors_sorted = sorted((anchor for anchor in Anchors), key = lambda anchor: anchor['position'][1], reverse=True)
            for phase_i, structure in enumerate(Structures_sorted):
                # reset displacement or not
                reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, reset_displ_zero_supporting_phase_i = self.set_up_reset_displacements_to_zero(phase_i)

                # all soil clusters except the ones below the wall toe are considered
                soilcluster_ids_dewatering = [soilcluster_id for phase_data in self.Phases_data[phase_i:-1] for soilcluster_id in phase_data['soilcluster_ids']]  
                # add dewatering phase if the current excavation level is below the global water level
                if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                    if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                        self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                        alreadyInterpolated = True
                    else:
                        self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                # add excavation phase
                self.add_phase_excavation__(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], self.deltas_support_to_ground[structure['id']], reset_displ_zero=reset_displ_zero_excavation_phase_i)

                if 'usage' not in structure:  # 'usage' key indicates struts
                    F_prestress = structure['F_prestress']
                    self.add_phase_anchoring__(self.Phases, self.Anchors, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)
                else:   # it is a strut
                    # add struting phase
                    F_prestress = structure['F_prestress']
                    self.add_phase_struting__(self.Phases, self.Struts, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i)

            # add final dewatering and excavation phase
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i+1)
            # all soil clusters except the ones below the wall toe are considered
            soilcluster_ids_dewatering = [soilcluster_id for phase_data in self.Phases_data[phase_i+1:-1] for soilcluster_id in phase_data['soilcluster_ids']]  # all soil clusters considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i+1]['waterlevel_id'] is not None) and (self.Phases_data[phase_i+1]['excavation_level'] < self.Boreholes[0]['Head']):
                if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                    self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                    alreadyInterpolated = True
                else:
                    self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation__(self.Phases, self.Soilclusters, self.Phases_data[phase_i+1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        else: # Cantilever wall
            alreadyInterpolated = False
            phase_i = 0
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i)
            soilcluster_ids_dewatering = self.Phases_data[phase_i]['soilcluster_ids'] + self.Phases_data[phase_i+1]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                if not alreadyInterpolated: # porepressure interpolation is only applied once at the first dewatering phase
                    self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, self.Phases_data[-1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_dewatering_phase_i)
                    alreadyInterpolated = True
                else:
                    self.add_phase_dewatering__(self.Phases, self.Waterlevels, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i)
            self.add_phase_excavation__(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i)

        # Add reconstruction phases
        Slabs_only = [strut for strut in self.Struts if strut['usage']=='Slab']# Slabs for reconstructions
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Slabs_only_sorted = sorted((structure for structure in Slabs_only), key = lambda structure: structure['position'][1], reverse=False)    # bottom to top
        #Struts_only_sorted = sorted((structure for structure in Struts_only), key = lambda structure: structure['position'][1], reverse=False)  # bottom to top
        for i_slab, slab in enumerate(Slabs_only_sorted):
            self.add_phase_struting__(self.Phases, self.Struts, [slab['id']], [slab['F_prestress']])        # constructing a raft or floor slab
            if i_slab < (len(Slabs_only_sorted) - 1):   # deconstruct struts above and between 2 slabs
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if (strut['position'][1] < Slabs_only_sorted[i_slab+1]['position'][1]) and (strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]):
                        strut_ids_to_deconstruct.append(strut['id'])
            else: # all struts above the top slab
                strut_ids_to_deconstruct = []
                for strut in Struts_only:
                    if strut['position'][1] > Slabs_only_sorted[i_slab]['position'][1]:
                        strut_ids_to_deconstruct.append(strut['id'])
            if strut_ids_to_deconstruct:    # when not empty only
                self.add_phase_struting__(self.Phases, self.Struts, strut_ids_to_deconstruct, [slab['F_prestress']], deconstruct=True)   # removing a temporary strut

        # Add safety phase
        if self.FoS_phase:
            if self.points_berm:
                self.add_phase_safety__(self.Phases, self.points_berm['soilcluster_id_no_strength_reduction'])
            else:
                self.add_phase_safety__(self.Phases)
        
        # Update Tskin for multilinear grout body for ground anchors
        self.assign_anchor_multilinear_skin_resistance(self.Anchors, self.Layer_polygons, self.Boreholes)

        # Add active earth pressure wedge
        self.add_active_earthpressure_wedge(True)

        # refine mesh around wall (applied for Optiman: Sensitivity, Metamodeling, NSGA)
        self.refine_mesh_around_wall(self.wall, self.x_min, self.x_max, self.Boreholes)

        ## Update phase tables once
        #self.update_phase_table(self.Phases, self.ui.tableWidget_2)
        
        ## Update phase table in Automated phases
        #self.ap_groupbox_ui = self.initialize_automated_phases_table()
        #self.update_phase_table_automated_phases(self.Phases, self.ap_groupbox_ui.tableWidget, self.Anchors)

        #self.phases_already_generated = False   #!!!


    def add_soil_cluser_berm_top(self):
        """ Adds soil clusters for the berm on top
        """
        pointTL = [self.x_min, max(self.wall['point1'][1], self.Boreholes[0]['Top'][0])]
        pointBL = [self.x_min, self.wall['point1'][1]]
        pointBR = [self.wall['point1'][0], self.wall['point1'][1]]
        #points_berm = list(zip(self.points_berm['x_coordinates'], self.points_berm['y_coordinates']))
        points_berm = [list(p) for p in zip(self.points_berm['x_coordinates'], self.points_berm['y_coordinates'])]
        points_soilcluster = [pointTL] + [pointBL] + [pointBR] + points_berm
        pointTL = pointBL
        pointTR = pointBR
        #soilcluster_id = self.add_soilcluster_multi_points__(self.Soilclusters, self.Soilclusters_notdried, points_soilcluster, wall_thickness=self.wall['wall_thickness'], berm_top=True)
        soilcluster_id = self.add_soilcluster_multi_points__(self.Soilclusters, self.Soilclusters_notdried, points_soilcluster, wall_thickness=0.0, berm_top=True)
        self.points_berm['soilcluster_id'] = [soilcluster_id] # soilcluster ID belonging to the berm

        # soil cluster for which is strength reduction is applied in saftey phase
        if self.FoS_phase:
            points_no_strength_reduction = [(point[0] + 4, point[1]) for point in points_berm]
            points_berm.reverse() # reverse list
            points_no_strength_reduction_soilcluster = points_no_strength_reduction + points_berm
            soilcluster_id_no_strength_reduction = self.add_soilcluster_multi_points__(self.Soilclusters, self.Soilclusters_notdried, points_no_strength_reduction_soilcluster)
            self.points_berm['soilcluster_id_no_strength_reduction'] = soilcluster_id_no_strength_reduction
            
        return pointTL, pointTR


    def setup_soilclusters_and_waterlevels_porepressure_interpolation(self):
        """ Gernerate soilclusters and user water level automatically
        Necessary information for creating the calculation phases is stored in self.Phases_data
        """
        # add berm data if berm coordinates are available
        if self.points_berm:
            pointTL, pointTR = self.add_soil_cluser_berm_top()

        else:
            pointTL = [self.x_min, max(self.wall['point1'][1], self.Boreholes[0]['Top'][0])]
            pointTR = [self.wall['point1'][0], max(self.wall['point1'][1], self.Boreholes[0]['Top'][0])]
        
        # loop support structures for adding soil clusters and user water levels
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Structures = self.Anchors + Struts_only
        Structures_sorted = sorted((structure for structure in Structures), key = lambda structure: structure['position'][1], reverse=True)
        i_existing_user_water_item = 0
        for structure in Structures_sorted:
            if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
                soilcluster_bottom = structure['position'][1] - self.delta_support_to_ground
                self.deltas_support_to_ground[structure['id']] = self.delta_support_to_ground
            else:   # if automated phases are already generated
                soilcluster_bottom = structure['position'][1] - self.deltas_support_to_ground[structure['id']]

            soilcluster_ids = []
            # create a soil cluster having bottom at the soilcluster_bottom
            pointBL = [self.x_min, soilcluster_bottom]
            pointBR = [self.wall['point1'][0], soilcluster_bottom]
            soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'])
            soilcluster_ids.append(soilcluster_id)
            pointTL = pointBL
            pointTR = pointBR
            waterlevel_id = None
            if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
                waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.delta_ground_to_water)
                waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.delta_ground_to_water)
                # add user water level conditionally
                if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                    waterlevel_id = self.add_waterlevel__(self.Waterlevels, waterlevel_pointL, waterlevel_pointR)
                    self.deltas_ground_to_water[waterlevel_id] = self.delta_ground_to_water
                else:
                    waterlevel_id = None
            else:   # if automated phases are already generated
                if self.Waterlevels:
                    waterlevel_id = self.Waterlevels[i_existing_user_water_item]['id']
                    waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.deltas_ground_to_water[waterlevel_id])
                    waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.deltas_ground_to_water[waterlevel_id])
                    # add user water level conditionally
                    if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                        self.update_user_water_level(self.deltas_ground_to_water, pointBL, self.Waterlevels, waterlevel_id) # update all user water levels !!!
                        i_existing_user_water_item += 1
                    else:
                        waterlevel_id = None

            phase_data = {}
            phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
            if self.points_berm:
                phase_data['soilcluster_ids'] = soilcluster_ids + self.points_berm['soilcluster_id']  # soilcluster ids for excavation
                self.points_berm['soilcluster_id'].clear() # use berm data only once
            else:
                phase_data['soilcluster_ids'] = soilcluster_ids # soilcluster ids for excavation
            phase_data['excavation_level'] = soilcluster_bottom  # intermediate excavation level
            self.Phases_data.append(phase_data)

        # the soilcluster(s) until the final excavation level
        soilcluster_bottom = self.final_excavation_level['level']
        soilcluster_ids = []
        if self.points_berm_base:
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_with_bottom_berm(self.Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
            self.Phases_data.append(phase_data)
        else:
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_no_bottom_berm(self.Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
            self.Phases_data.append(phase_data)

        # the soilcluster(s) until foot of the wall
        soilcluster_bottom = self.final_excavation_level['level'] - self.wall['depth_embedment']
        soilcluster_ids = []
        if self.points_berm_base:
            phase_data, pointTL, pointTR = self.define_phase_data_until_foot_of_wall_with_bottom_berm(soilcluster_bottom, soilcluster_ids)
            self.Phases_data.append(phase_data)
        else:
            phase_data, pointTL, pointTR = self.define_phase_data_until_foot_of_wall_no_bottom_berm(soilcluster_bottom, pointTL, pointTR, soilcluster_ids)
            self.Phases_data.append(phase_data)


    def define_phase_data_until_final_excavation_level_no_bottom_berm(self, Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item):
        """ Sets and gets phase data until the final excavation level
        Return phase data information
        """
        # create a soil cluster having bottom at the soilcluster_bottom
        pointBL = [self.x_min, soilcluster_bottom]
        pointBR = [self.wall['point1'][0], soilcluster_bottom]
        soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'], annotate_FEL=True)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        waterlevel_id = None
        if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
            waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.delta_ground_to_water)
            waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.delta_ground_to_water)
            # add user water level conditionally
            if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                waterlevel_id = self.add_waterlevel__(Waterlevels, waterlevel_pointL, waterlevel_pointR)
                self.deltas_ground_to_water[waterlevel_id] = self.delta_ground_to_water
            else:
                waterlevel_id = None
        else:   # if automated phases are already generated
            if Waterlevels:
                waterlevel_id = Waterlevels[i_existing_user_water_item]['id']
                waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.deltas_ground_to_water[waterlevel_id])
                waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.deltas_ground_to_water[waterlevel_id])
                # add user water level conditionally
                if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                    self.update_user_water_level(self.deltas_ground_to_water, pointBL, Waterlevels, waterlevel_id) # update all user water levels !!!
                    i_existing_user_water_item += 1
                else:
                    waterlevel_id = None
        phase_data = {}
        phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        if self.points_berm:
            phase_data['soilcluster_ids'] = soilcluster_ids + self.points_berm['soilcluster_id']  # soilcluster ids for excavation
            self.points_berm['soilcluster_id'].clear() # use berm data only once
        else:
            phase_data['soilcluster_ids'] = soilcluster_ids # soilcluster ids for excavation
        phase_data['excavation_level'] = soilcluster_bottom  # final excavation level

        return phase_data, pointTL, pointTR


    def define_phase_data_until_final_excavation_level_with_bottom_berm(self, Waterlevels, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item):
        """ Sets and gets phase data until the final excavation level
        Return phase data information
        """
        #points_berm = list(zip(self.points_berm_base['x_coordinates'], self.points_berm_base['y_coordinates']))
        points_berm = [list(p) for p in zip(self.points_berm_base['x_coordinates'], self.points_berm_base['y_coordinates'])]
        points_soilcluster = [pointTR] + [pointTL] + points_berm
        soilcluster_id = self.add_soilcluster_multi_points__(self.Soilclusters, self.Soilclusters_notdried, points_soilcluster, self.wall['wall_thickness'], berm_base=True, annotate=True)
        soilcluster_ids.append(soilcluster_id)
        y_min = min(self.points_berm_base['y_coordinates']) # bottom of the berm
        pointBL = [pointTL[0], y_min]
        pointBR = [pointTR[0], y_min]
        waterlevel_id = None
        if not self.phases_already_generated: # default delta_support_to_ground (0.5 m)
            waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.delta_ground_to_water)
            waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.delta_ground_to_water)
            # add user water level conditionally
            if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                waterlevel_id = self.add_waterlevel__(Waterlevels, waterlevel_pointL, waterlevel_pointR)
                self.deltas_ground_to_water[waterlevel_id] = self.delta_ground_to_water
            else:
                waterlevel_id = None
        else:   # if automated phases are already generated
            if Waterlevels:
                waterlevel_id = Waterlevels[i_existing_user_water_item]['id']
                waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.deltas_ground_to_water[waterlevel_id])
                waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.deltas_ground_to_water[waterlevel_id])
                # add user water level conditionally
                if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                    self.update_user_water_level(self.deltas_ground_to_water, pointBL, Waterlevels, waterlevel_id) # update all user water levels !!!
                    i_existing_user_water_item += 1
                else:
                    waterlevel_id = None
        phase_data = {}
        phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        if self.points_berm:
            phase_data['soilcluster_ids'] = soilcluster_ids + self.points_berm['soilcluster_id']  # soilcluster ids for excavation
            self.points_berm['soilcluster_id'].clear() # use berm data only once
        else:
            phase_data['soilcluster_ids'] = soilcluster_ids # soilcluster ids for excavation
        phase_data['excavation_level'] = soilcluster_bottom  # final excavation level

        return phase_data, pointTL, pointTR



    def define_phase_data_until_foot_of_wall_no_bottom_berm(self, soilcluster_bottom, pointTL, pointTR, soilcluster_ids):
        """ Sets and gets phase data until the final excavation level
        Return phase data information
        """
        # create a soil cluster having bottom at the soilcluster_bottom
        pointBL = [self.x_min, soilcluster_bottom]
        pointBR = [self.wall['point1'][0], soilcluster_bottom]
        soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'], annotate=False)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        phase_data = {}
        #phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        phase_data['soilcluster_ids'] = soilcluster_ids   # soilcluster ids for excavation
        self.Phases_data.append(phase_data)

        # the soilcluster(s) until bottom of the model
        soilcluster_bottom = self.y_min
        soilcluster_ids = []
        # create a soil cluster having bottom at the soilcluster_bottom
        pointBL = [self.x_min, soilcluster_bottom]
        pointBR = [self.wall['point1'][0], soilcluster_bottom]
        soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, self.wall['wall_thickness'], annotate=False)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        phase_data = {}
        #phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        phase_data['soilcluster_ids'] = soilcluster_ids   # soilcluster ids for excavation

        return phase_data, pointTL, pointTR


    def define_phase_data_until_foot_of_wall_with_bottom_berm(self, soilcluster_bottom, soilcluster_ids):
        """ Sets and gets phase data until the final excavation level
        Return phase data information
        """
        # create a soil cluster having bottom at the soilcluster_bottom or bottom of berm, which ever is lower
        pointBL = [self.x_min, min(soilcluster_bottom, min(self.points_berm_base['y_coordinates']) - 1.0)]
        pointBR = [self.wall['point1'][0], min(soilcluster_bottom, min(self.points_berm_base['y_coordinates']) -1.0)]
        #points_berm = list(zip(self.points_berm_base['x_coordinates'], self.points_berm_base['y_coordinates']))
        points_berm = [list(p) for p in zip(self.points_berm_base['x_coordinates'], self.points_berm_base['y_coordinates'])]
        points_soilcluster = points_berm + [pointBR] + [pointBL]
        soilcluster_id = self.add_soilcluster_multi_points__(self.Soilclusters, self.Soilclusters_notdried, points_soilcluster, self.wall['wall_thickness'], berm_base=True)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        phase_data = {}
        #phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        phase_data['soilcluster_ids'] = soilcluster_ids   # soilcluster ids for excavation
        self.Phases_data.append(phase_data)

        # the soilcluster(s) until bottom of the model
        soilcluster_bottom = self.y_min
        soilcluster_ids = []
        # create a soil cluster having bottom at the soilcluster_bottom
        pointBL = [self.x_min, soilcluster_bottom]
        pointBR = [self.wall['point1'][0], soilcluster_bottom]
        soilcluster_id = self.add_soilcluster__(self.Soilclusters, self.Soilclusters_notdried, pointTL, pointTR, pointBL, pointBR, wall_thickness=self.wall['wall_thickness'], annotate=False)
        soilcluster_ids.append(soilcluster_id)
        pointTL = pointBL
        pointTR = pointBR
        phase_data = {}
        #phase_data['waterlevel_id'] = waterlevel_id       # water level at this dewatering phase
        phase_data['soilcluster_ids'] = soilcluster_ids   # soilcluster ids for excavation

        return phase_data, pointTL, pointTR


    def update_user_water_level(self, deltas, bottom_point, Waterlevels, waterlevel_id):
        """ Updates level for the water level having ID of waterlevel_id
        """
        for waterlevel in Waterlevels:
            if waterlevel['id'] == waterlevel_id: # the same water level ID
                delta = self.deltas_ground_to_water[waterlevel_id]
                waterlevel_pointL = (bottom_point[0]+2, bottom_point[1] - delta)
                waterlevel_pointR = (bottom_point[0]-2, bottom_point[1] - delta)
                if waterlevel['pointL'][1] != waterlevel_pointL[1]: # water level has been changed
                    waterlevel['pointL'][1] = waterlevel_pointL[1]
                    waterlevel['pointR'][1] = waterlevel_pointR[1]
                    plaxis2d_input.update_waterlevel(self.plaxis2d_input_file, 'g_i', waterlevel)
                    self.plot_canvas.undo_plot_pathpatches(waterlevel['pathpatches'])
                    waterlevel['pathpatches'] = self.plot_canvas.plot_waterlevel(waterlevel)


    def refine_mesh_around_wall(self, wall, x_min, x_max, Boreholes):
        """ Create polygon for refining mesh around the wall
        """
        wall_top = max(wall['point1'][1], Boreholes[0]['Top'][0])
        wall_toe = wall['point2'][1]
        x_wall = wall['point1'][0]
        #x_left_top = x_wall - (x_wall - x_min)*0.5
        x_left_top = x_min
        x_right_top = x_wall + (x_max - x_wall)*0.3
        #x_left_toe = x_wall - (x_wall - x_min)*0.5*0.4
        x_left_toe = x_min
        x_right_toe = x_wall + (x_max - x_wall)*0.3*0.3
        point_TL = (x_left_top, wall_top)
        point_TR = (x_right_top, wall_top)
        point_BL = (x_left_toe, wall_toe)
        point_BR = (x_right_toe, wall_toe)
        self.points_fine_mesh = list((point_TL, point_BL, point_BR, point_TR))
        plaxis2d_input.add_polygon_fine_mesh(self.plaxis2d_input_file, 'g_i', self.points_fine_mesh)
        plaxis2d_input.refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i') # 3 times mesh refinement by default

    
    def undo_refine_mesh_around_wall(self):
        """ Remove mesh refinement including the polygon for the fine mesh
        """
        plaxis2d_input.remove_structure(self.plaxis2d_input_file, 1, '##FINE_MESH_POLYGON', 2) # remove polygon of the fine mesh
        self.points_fine_mesh.clear()
        plaxis2d_input.undo_refine_mesh_around_wall(self.plaxis2d_input_file, 'g_i')


    def add_waterlevel__(self, Waterlevels, pointL, pointR):
        waterlevel = {}
        waterlevel['pointL'] = list(pointL)
        waterlevel['pointR'] = list(pointR)
        waterlevel['id'] = randint(100000, 999999)
            
        waterlevel_pathpatches = self.plot_canvas.plot_waterlevel(waterlevel)
        waterlevel['pathpatches'] = waterlevel_pathpatches

        Waterlevels.append(waterlevel)
            
        plaxis2d_input.add_waterlevel(self.plaxis2d_input_file, 'g_i', waterlevel)
        #print('User water level is added, water level = {0}'.format(pointL[1]))
            
        self.ui.comboBox_13.addItem(str(waterlevel['id']))

        # Update content in table combined phases
        #self.plaxman_cp.update_waterlevels(Waterlevels, Soilclusters)
        return waterlevel['id']


    def add_soilcluster_multi_points__(self, Soilclusters, Soilclusters_notdried, polygon_points, wall_thickness=0.0, berm_base=False, berm_top=False, annotate=False, soilmaterial=None):
        """ Adds a soil cluster (for excavation) defined by multiple polygon points
        This method is used to create soil clusters in the excavation pit belonging to the berm.
        wall_thickness and berm_base is used only for plotting the soil cluster considering thickness of the wall
        """
        soilcluster = {}
        soilcluster['points'] = polygon_points
        soilcluster['soilmaterial'] = soilmaterial
        soilcluster['pointTL'] = polygon_points[0]
        soilcluster['pointTR'] = None
        soilcluster['pointBL'] = polygon_points[1]
        soilcluster['pointBR'] = polygon_points[2]
        soilcluster['id'] = randint(100000, 999999)
        soilcluster['annotate'] = annotate
        soilcluster['isRectangular'] = False
        soilcluster['berm_base'] = berm_base # for loading
        soilcluster['berm_top'] = berm_top # for loading

        Soilclusters.append(soilcluster)
        Soilclusters_notdried.append(soilcluster)
            
        if berm_base:
            soilcluster_pathpatches = self.plot_canvas.plot_soilcluster_points(soilcluster, wall_thickness, berm_base=berm_base, annotate=annotate)
        elif berm_top:
            soilcluster_pathpatches = self.plot_canvas.plot_soilcluster_points(soilcluster, wall_thickness, berm_top=berm_top)
        else:
            soilcluster_pathpatches = self.plot_canvas.plot_soilcluster_points(soilcluster)

        soilcluster['pathpatches'] = soilcluster_pathpatches

        plaxis2d_input.add_soilcluster_multi_points(self.plaxis2d_input_file, 'g_i', soilcluster) # add_polygon() instead of add_soilcluster()
        #print('A multi-point soil cluster is added, top = {0}, bottom = {1}'.format(soilcluster['pointTL'][1], soilcluster['pointBL'][1]))

        return soilcluster['id']
    

    def clear_phases_data__(self, Phases, Walls, Lineloads, Pointloads, Soilclusters, Soilclusters_notdried, Anchors, Struts, 
                    Waterlevels, Drain):
        """ Removes all phases and construct wall
        """
        # remove Phases and Soilclusters if not emtpy
        self.remove_all_phases__(Phases, Soilclusters, Soilclusters_notdried)
        self.remove_all_soilclusters__(Soilclusters, Soilclusters_notdried)
        self.remove_all_waterlevels(Waterlevels)

        # remove data for phases
        self.Phases_data.clear()

        # undo refining the mesh
        if self.points_fine_mesh: # undo only if these polygon points are not empty
            self.undo_refine_mesh_around_wall()

        ## repaint wall
        #self.plot_canvas.undo_plot_pathpatches(self.wall['pathpatches'])
        #for wall in self.Walls:
        #    self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])

        # remove active earth pressure wedge
        self.add_active_earthpressure_wedge(False)


    def clear_phases_data(self):
        """ Removes all phases and construct wall
        """
        # remove Phases and Soilclusters if not emtpy
        self.remove_all_phases(self.Phases, self.Soilclusters, self.Soilclusters_notdried)
        self.remove_all_soilclusters(self.Soilclusters, self.Soilclusters_notdried)
        # do not remove user water levels for the regeneration of phases

        # remove data for phases
        self.Phases_data.clear()
        # remove selectively to keep 'reset_displ_zero*'
        #keys_to_remove = ['waterlevel_id', 'soilcluster_ids']
        #for phase_data in self.Phases_data:
        #    for key in keys_to_remove:
        #        if key in phase_data:
        #            del phase_data[key]

        # undo refining the mesh
        if self.points_fine_mesh: # undo only if these polygon points are not empty
            self.undo_refine_mesh_around_wall()

        # remove active earth pressure wedge
        self.add_active_earthpressure_wedge(False)


    def add_phase_safety(self, Phases, soil_cluster_id_no_strength_reduction=None):
        """ Adds a safety phase for determining FoS
        """
        self.add_phase_safety__(Phases, soil_cluster_id_no_strength_reduction)
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
        print('{0} phase is created'.format(Phases[-1]['phase_name']))


    def add_phase_safety__(self, Phases, soil_cluster_id_no_strength_reduction=None):
        """ Adds a safety phase for determining FoS
        """
        phasename = 'FoS'
        new_phase = {}
        new_phase['soilcluster_id_no_strength_reduction'] = soil_cluster_id_no_strength_reduction
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['loading_type'] = 'Incremental multipliers'
        new_phase['water_level_id'] = None #waterlevel_id        
        new_phase['deform_calc_type'] = 'Safety' #calculation_type
        new_phase['pore_pres_calc_type'] = 'Phreatic' #pore_pressure
        new_phase['time_interval'] = 0
        new_phase['reset_displ_zero'] = True #reset_displ_zero
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        previous_phase = Phases[-1]
                    
        plaxis2d_input.add_phase_safety(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase)
                    
        Phases.append(dict(new_phase))


    def update_phase_table_automated_phases(self, Phases, table, Anchors=None):
        """ Updates the table of phases (table=self.ui.tableWidget_22)
        """
        row_count = len(Phases)
        table.setRowCount(row_count)
        table.setColumnCount(10)

        table.blockSignals(True) # temporarily block signals from tableWidget to avoid call slot update_ground_anchor before the table is filled

        # clear only contents by setting empty string '' for all cells
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                cell_item = table.item(i, j)
                if cell_item is None:
                    table.setItem(i, j,  QtWidgets.QTableWidgetItem(''))
                else:
                    table.setItem(i, j,  QtWidgets.QTableWidgetItem(''))

        #column_items = sorted(list(self.Phases[0].keys()))
        column_items = ['phase_id', 'phase_name', 'deform_calc_type', 'pore_pres_calc_type', 'reset_displ_zero', 'water_level_id', 'delta_support-excavation [m]', 'delta_excavation-water [m]']
        #row_number = len(Phases)
        column_number = len(column_items)

        table.setHorizontalHeaderLabels(column_items)
        for i in range(len(Phases)):
            for j in range(len(column_items) - 3):
                #table.removeCellWidget(i, j) # remove cell item
                cell_item = table.item(i, j)
                if cell_item is None:
                    table.setItem(i, j,  QtWidgets.QTableWidgetItem(str(Phases[i][column_items[j]])))
                else:
                    cell_item.setText(str(Phases[i][column_items[j]]))

            if (Phases[i]['phase_name'] == 'Anchoring') | (Phases[i]['phase_name'] == 'Strut/slab construction'):
                    cell_item_reset_displ_zero = table.item(i, column_number - 4) 
                    cell_item_reset_displ_zero.setBackground(QColor(242, 255, 116))  # light yellow

            if Phases[i]['phase_name'] == 'Excavation':
                if 'delta_support-excavation' not in Phases[i]:
                    Phases[i]['delta_support-excavation'] = None

                if Phases[i]['delta_support-excavation'] is not None:
                    cell_item = table.item(i, column_number - 2)
                    if cell_item is None:
                        table.setItem(i, column_number - 2,  QtWidgets.QTableWidgetItem(str(Phases[i]['delta_support-excavation'])))  
                    else:
                        cell_item.setText(str(Phases[i]['delta_support-excavation']))
                    cell_item = table.item(i, column_number - 2)
                    cell_item.setBackground(QColor(242, 255, 116))  # light yellow
                    
                cell_item_reset_displ_zero = table.item(i, column_number - 4) 
                cell_item_reset_displ_zero.setBackground(QColor(242, 255, 116))  # light yellow

            if Phases[i]['phase_name'] == 'Dewatering (lowering water level)':
                if self.delta_ground_to_water:
                    cell_item = table.item(i, column_number - 1)
                    delta_ground_to_water = self.deltas_ground_to_water[Phases[i]['water_level_id']]
                    if cell_item is None:
                        table.setItem(i, column_number - 1,  QtWidgets.QTableWidgetItem(str(delta_ground_to_water)))     
                    else:
                        cell_item.setText(str(delta_ground_to_water))
                    cell_item = table.item(i, column_number - 1)
                    cell_item.setBackground(QColor(242, 255, 116))  # light yellow

                    # water_level_id
                    cell_item = table.item(i, column_number - 3)
                    if cell_item is None:
                        table.setItem(i, column_number - 3,  QtWidgets.QTableWidgetItem(str(Phases[i]['water_level_id'])))     # F_prestress
                    else:
                        cell_item.setText(str(Phases[i]['water_level_id']))

                cell_item_reset_displ_zero = table.item(i, column_number - 4) 
                cell_item_reset_displ_zero.setBackground(QColor(242, 255, 116))  # light yellow


        # connection for responding to values changed by user
        table.blockSignals(False) # unblock signals from tableWidge
        table.cellChanged.connect(lambda row, column: self.update_delta_support_to_excavation_level(row, column, Phases))
        table.cellChanged.connect(lambda row, column: self.update_delta_excavation_level_to_dewatering_level(row, column, Phases))
        table.cellChanged.connect(lambda row, column: self.update_displ_zero(row, column, Phases))
        #table.deleteLater()

        self.ap_groupbox_ui.pushButton.clicked.connect(lambda bool: self.calculate())


    @pyqtSlot()
    def update_displ_zero(self, row, column, Phases):
        """ Updates displacement to zero
        """
        if column == 4:
            # which phase_i is it? phase_i is numbered based on the support structures, which can be determined by 
            # counting the number of excavation phases performed until the considered phase
            phase_no_current = row
            phase_i = 0
            for i in range(0, phase_no_current):
                if Phases[i]['phase_name'] in ['Anchoring', 'Strut/slab construction']:
                    phase_i +=1

            phase_name_current = self.ap_groupbox_ui.tableWidget.item(phase_no_current, 1).text()
            reset_displ_zero_current_text = self.ap_groupbox_ui.tableWidget.item(phase_no_current, 4).text()
            if reset_displ_zero_current_text == 'True':
                reset_displ_zero = True
            elif reset_displ_zero_current_text == 'False':
                reset_displ_zero = False
            else:
                self.dialog.show_message_box('Warning', 'Please set only True or False!')
                return

            if phase_i >= len(self.reset_displ_zero_dewatering):
                self.dialog.show_message_box('Warning', 'Resetting displacements to zero at this phase is not allowed!')
                return

            else:
                if phase_name_current == 'Dewatering (lowering water level)':
                    self.reset_displ_zero_dewatering[phase_i] = reset_displ_zero
                elif phase_name_current == 'Excavation':
                    self.reset_displ_zero_excavation[phase_i] = reset_displ_zero
                elif phase_name_current in ['Anchoring', 'Strut/slab construction']:
                    self.reset_displ_zero_supporting[phase_i] = reset_displ_zero
                #print(phase_i)
                print('Reset displacements to zero is {0} at phase {1}'.format(reset_displ_zero, phase_name_current))


    @pyqtSlot()
    def update_delta_excavation_level_to_dewatering_level(self, row, column, Phases):
        """ Updates distance from the excavation level to the dewatering level
        """
        #print(row, column)
        if (column == 7) and (Phases[row]['phase_name'] == 'Dewatering (lowering water level)'):
            #print('Updates distance from support structure to the excavation level')
            try:
                delta = float(self.ap_groupbox_ui.tableWidget.item(row, column).text())
                phase_id = int(self.ap_groupbox_ui.tableWidget.item(row, 0).text()) # phase id of the dewatering phase
                #print(row, delta, phase_id)
                for phase in Phases:
                    if phase['phase_id'] == phase_id:
                        water_level_id = phase['water_level_id']
                        #phase_id = phase['phase_id']
                        self.deltas_ground_to_water[water_level_id] = delta    # update delta for user water level belonging to anchoring
                        print('water_level_id: {0}, delta: {1}'.format(water_level_id, delta))
                    #else:
                    #    self.deltas_ground_to_water[999999] = delta    # update delta for user water level belonging to the final excavation level
                    #    print('phase_id: {0}, delta: {1}'.format(999999, delta))
                
            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')


    @pyqtSlot()
    def update_delta_support_to_excavation_level(self, row, column, Phases):
        """ Updates distance from support structure to the excavation level
        """
        #print(row, column)
        if (column == 6) and (Phases[row]['phase_name'] == 'Excavation'):
            #print('Updates distance from support structure to the excavation level')
            try:
                delta = float(self.ap_groupbox_ui.tableWidget.item(row, column).text())
                phase_id = int(self.ap_groupbox_ui.tableWidget.item(row + 1, 0).text()) # phase id of the anchoring phase just below
                #print(row, delta, phase_id)
                for phase in Phases:
                    if phase['phase_id'] == phase_id:
                        try:
                            structure_id = phase['anchor_ids'][0]   # structure is a ground anchor
                        except KeyError:
                            structure_id = phase['strut_ids'][0]    # structure is a strut

                        self.deltas_support_to_ground[structure_id] = delta    # update delta
                
            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if value is correctly entered!')


    @pyqtSlot()
    def calculate(self):
        """ Executes PLAXIS2D for calculating the Python script of the model
        """
        print('\nLaunched PLAXIS2D INPUT for calculation...')
        self.model = Evaluate_Plaxis2DModel()
        self.run_thread = RunThreadSingle(workflow=self.model)
        self.run_thread.start()


    def remove_all_phases(self, Phases, Soilclusters, Soilclusters_notdried):
        """ Removes all calculation phases
        """
        while len(Phases) > 0:
            self.remove_phase(Phases, Soilclusters, Soilclusters_notdried)

        # Update (clear) phase table in Predefined phases
        self.remove_table_cell_items(self.ui.tableWidget_2)

        # Update (clear) phase table in Automated phases
        self.ap_groupbox_ui = self.initialize_automated_phases_table()
        self.update_phase_table_automated_phases(Phases, self.ap_groupbox_ui.tableWidget)


    def remove_all_phases__(self, Phases, Soilclusters, Soilclusters_notdried):
        """ Removes all calculation phases
        """
        while len(Phases) > 0:
            self.remove_phase__(Phases, Soilclusters, Soilclusters_notdried)

        # Update (clear) phase table in Predefined phases
        self.remove_table_cell_items(self.ui.tableWidget_2)

        ## Update (clear) phase table in Automated phases
        #self.ap_groupbox_ui = self.initialize_automated_phases_table()
        #self.update_phase_table_automated_phases(Phases, self.ap_groupbox_ui.tableWidget)


    def remove_table_cell_items(self, table):
        """ Remove cell items so that the signals from them are killed
        """
        for i in range(table.columnCount()):
            for j in range(table.rowCount()):
                table.removeCellWidget(i,j)


    def remove_phase(self, Phases, Soilclusters, Soilclusters_notdried):    
        """ Remove the last calculation phase
        """
        self.remove_phase__(Phases, Soilclusters, Soilclusters_notdried)

        print('The last phase is removed, {} phases remain'.format(len(Phases)))



    def remove_phase__(self, Phases, Soilclusters, Soilclusters_notdried):    
        """ Remove the last calculation phase
        """
        if len(Phases) > 0:
            deleted_phase = Phases.pop()   
            
            plaxis2d_input.remove_structure_inbetween(self.plaxis2d_input_file, deleted_phase['phase_id'], '##PHASE', '##END_OF_PHASE')

            ## undo assigning colors of the previously added phase
            if 'pathpatches' in deleted_phase:
                for group_i, pathpathgroup in enumerate(deleted_phase['pathpatches']):
                    self.plot_canvas.set_colors(pathpathgroup, deleted_phase['pathpatch_colors'][group_i])

            self.ui.comboBox_31.removeItem(len(Phases)) # in Plaxman
            self.ui.comboBox_21.removeItem(len(Phases)) # in Backman

            # reset the dry soilclusters, if phase is of dewatering type
            if deleted_phase['phase_name'][:10] == 'Dewatering':
                #print(deleted_phase['phase_name'][:10])
                #print(self.Soilclusters_notdried)
                #print('\n')
                for drysoilcluster_id in deleted_phase['setdry_soilcluster_ids']:
                    for soilcluster in Soilclusters:
                        if drysoilcluster_id == soilcluster['id']:
                            Soilclusters_notdried.append(soilcluster)
                #print(self.Soilclusters_notdried)



    def remove_all_soilclusters(self, Soilclusters, Soilclusters_notdried):
        """ Removes all soil clusters
        """
        self.remove_all_soilclusters__(Soilclusters, Soilclusters_notdried)
        print('Soilcluster removal done, {} items remain'.format(len(Soilclusters)))


    def remove_all_soilclusters__(self, Soilclusters, Soilclusters_notdried):
        """ Removes all soil clusters
        """
        while len(Soilclusters) > 0: 
            removed_soilcluster = Soilclusters.pop()
            self.plot_canvas.undo_plot_pathpatches(removed_soilcluster['pathpatches'])  
            plaxis2d_input.remove_structure(self.plaxis2d_input_file, removed_soilcluster['id'], '##SOIL_CLUSTER', 6)

        # clear Soilclusters_notdried
        Soilclusters_notdried.clear()

        # show soilclusters on table
        self.plaxman_x.display_soilclusters_on_table(self.Soilclusters, self.ui.tableWidget_29)


    def remove_all_waterlevels(self, Waterlevels):
        """ Removes all user water levels
        """
        while len(Waterlevels) > 0: 
            removed_waterlevel = Waterlevels.pop()
            self.plot_canvas.undo_plot_pathpatches(removed_waterlevel['pathpatches'])  
            plaxis2d_input.remove_structure(self.plaxis2d_input_file, removed_waterlevel['id'], '##WATER_LEVEL', 2)
            #print('User water level removal done, {} items remain'.format(len(Waterlevels)))


    def remove_all_drains(self, Drains):
        """ Removes all user water levels
        """
        while len(Drains) > 0: 
            removed_waterlevel = Drains.pop()
            self.plot_canvas.undo_plot_pathpatches(removed_waterlevel['pathpatches'])  
            plaxis2d_input.remove_structure(self.plaxis2d_input_file, removed_waterlevel['id'], '##DRAIN', 5)
            #print('User drain removal done, {} items remain'.format(len(Drains)))


    def remove_all_reset_displ_zero(self):
        """ Remove settings for resetting displacements to zero
        """
        self.reset_displ_zero_dewatering.clear()
        self.reset_displ_zero_excavation.clear()
        self.reset_displ_zero_supporting.clear()


#    def suggest_wall_embedment_depth(self, wall):
#        """ Suggests wall embedment depth
#        """
#        #wall_top_level = wall['point1'][1]
#        #wall_length = np.sqrt((wall['point2'][1] - wall['point1'][1])**2 + (wall['point2'][0] - wall['point1'][0])**2)
#        final_excavation_level = self.final_excavation_level['level']
#        wall_foot_level = wall['point2'][1] 
#        depth_embedment = final_excavation_level - wall_foot_level
#        #self.ui.lineEdit_59.setText("{:.2f}".format(final_excavation_level))
#        self.ui.lineEdit_60.setText("{:.2f}".format(depth_embedment))
    

    @pyqtSlot()
    def update_final_excavation_level(self, level, x_min):
        """ Updates depth of the wall embedment
        """
        #print(level, x_min)
        self.final_excavation_level['level'] = level

        # draw the line for final excavation level
        x_wall = self.wall['point1'][0]
        #x_min = self.plaxman.geometry[0]
        self.final_excavation_level['x_wall'] = x_wall
        self.final_excavation_level['x_min'] = x_min

        if 'pathpatch' in self.final_excavation_level:
            self.plot_canvas.undo_plot_pathpatches(self.final_excavation_level['pathpatch'])

        # plot final excavation line
        self.final_excavation_level['pathpatch'] = self.plot_canvas.plot_final_excavation_level(self.final_excavation_level['level'], x_min, x_wall)
        print('Final excavation level is at {}'.format(level))

        # set embedment depth based on the current wall length
        length_wall = self.wall['point1'][1] - self.wall['point2'][1]
        length_until_final_exc_level = self.wall['point1'][1] - self.final_excavation_level['level']
        depth_embedment =  length_wall - length_until_final_exc_level
        self.ui.lineEdit_60.setText('{:.3f}'.format(depth_embedment))


    @pyqtSlot()
    def update_embedment_depth(self, depth_embedment):
        """ Updates depth of the wall embedment
        """
        if self.wall: # only if the wall has been added
            self.update_embedment_depth__(depth_embedment)
            print('Wall bottom is at {}'.format(self.wall['point2'][1]))
    

    def update_embedment_depth__(self, depth_embedment):
        """ Updates depth of the wall embedment
        """
        # check if level is entered
        if 'level' not in self.final_excavation_level:
            self.update_final_excavation_level(float(self.ui.lineEdit_59.text()), self.x_min)    # make sure that final excavation level is there

        self.wall['depth_embedment'] = depth_embedment # additional key: value in self.wall
        self.wall['point2'][1] =  self.final_excavation_level['level'] - self.wall['depth_embedment']
        # update plaxis input file
        plaxis2d_input.update_wall(self.plaxis2d_input_file, 'g_i', self.wall)
        # repaint plot canvas
        self.plot_canvas.undo_plot_pathpatches(self.wall['pathpatches'])
        for wall in self.Walls: # also repaint the upper wall
            self.plot_canvas.undo_plot_pathpatches(wall['pathpatches'])
            wall['pathpatches'] = self.plot_canvas.plot_wall(wall, wall['color'])

    
    def update_strut_by_id__(self, strut_id, key, value, Struts):
        """ Updates strut (indexed by id)
        """
        for strut in Struts:
            if strut['id'] == strut_id:
                if key != 'level':
                    strut[key] = value
                    if key == 'Lspacing':
                        update_data_in_json_item(strut['json_item'], {'Lspacing': strut['Lspacing']})
                else: # level
                    strut['position'][1] = value

                # update plaxis2d input file
                plaxis2d_input.update_strut(self.plaxis2d_input_file, 'g_i', strut)

                # repaint the groundanchor
                self.plot_canvas.undo_plot_pathpatches(strut['pathpatches'])
                strut['pathpatches'] = self.plot_canvas.plot_strut(strut)
                #break
                

    def assign_anchor_multilinear_skin_resistance(self, Anchors, Layer_polygons, Boreholes):
        """ Assigns multilinear skin resistance for each of the ground anchors based on skin resistance defined for each soil layer
        """
        #for anchor_i, anchor in enumerate(Anchors):
        for anchor in Anchors:
            grout_point_start, grout_point_end = get_anchor_grout_endpoints(anchor['position'], anchor['angle'], anchor['length_free'], anchor['length_fixed'])
            points_intersection = []
            Tskins_intersection = []
            for layer_i, layerpolygon in enumerate(Layer_polygons):
                layer_bottom = Boreholes[0]['Bottom'][layer_i]
                #layer_top = Boreholes[0]['Top'][layer_i]

                point_intersection_minus, point_intersection_plus = get_anchor_soillayer_intersection_point(grout_point_start, grout_point_end, anchor['angle'], layer_bottom)
                if point_intersection_minus is not None:
                    points_intersection.append(point_intersection_minus)
                    points_intersection.append(point_intersection_plus)
                    Tskin_upper_layer = layerpolygon['Tskin']
                    Tskin_lower_layer = Layer_polygons[layer_i+1]['Tskin']
                    Tskins_intersection.append(Tskin_upper_layer)
                    Tskins_intersection.append(Tskin_lower_layer)
                #elif (grout_point_start[1] < layer_top) and (grout_point_end[1] > layer_bottom):
                else:
                    Tskin_layer = layerpolygon['Tskin']
            
            # Add end points and their skin resistance values
            if points_intersection:
                points_intersection.insert(0, grout_point_start)
                points_intersection.append(grout_point_end)
                Tskins_intersection.insert(0, Tskins_intersection[0])
                Tskins_intersection.append(Tskins_intersection[-1])
            else:
                points_intersection.insert(0, grout_point_start)
                points_intersection.append(grout_point_end)
                Tskins_intersection.insert(0, Tskin_layer)
                Tskins_intersection.append(Tskin_layer)

            # Prepare data for SkinResistanceTable
            distances = [0.0]
            for i in range(len(points_intersection)-1):
                d = calc_dist_2p(points_intersection[0], points_intersection[i+1])
                distances.append(d)
            #print(anchor_i, points_intersection)
            #print(anchor_i, Tskins_intersection)
            #print(anchor_i, distances)

            # Write Tskin values in SkinResistanceTable if points_intersection are not empty
            SkinResistanceTable = [None]*2*len(distances)
            SkinResistanceTable[::2] = distances
            SkinResistanceTable[1::2] = Tskins_intersection
            if 'Multilinear' in anchor['grout_json_item']: # Applies only to multilinear skin resistance grout
                update_data_in_json_item(anchor['grout_json_item'], {'SkinResistanceTable': str(SkinResistanceTable)})



    def display_anchor_soil_layer_dependent_skin_frictions(self, Layer_polygons):
        """ Displays soil layer dependent skin frictions for user adaption of multi-linear grout skin frictions
        """
        self.ui.tableWidget_19.blockSignals(True) # temporarily block signals from tableWidget_18 to avoid call slot update_ground_anchor before the table is filled
        #print(len(self.Layer_polygons))
        self.ui.tableWidget_19.setRowCount(len(Layer_polygons))
        self.ui.tableWidget_19.horizontalHeader().setVisible(True)
        column_labels = ['Soil layer', 'Tskin [kN/m]']
        self.ui.tableWidget_19.setColumnCount(len(column_labels))
        self.ui.tableWidget_19.setHorizontalHeaderLabels(column_labels)

        for layer_i, layerpolygon in enumerate(Layer_polygons):
            if 'color' in layerpolygon:
                if 'soilmaterial_layer' in layerpolygon:
                    soilmaterial_layer = layerpolygon['soilmaterial_layer']
                    #print(layer_i, soilmaterial_layer)
                    self.ui.tableWidget_19.setItem(layer_i, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # soilmaterial name
                    self.ui.tableWidget_19.item(layer_i, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color

                    #self.ui.tableWidget_19.setItem(layer_i, 1, QtWidgets.QTableWidgetItem('200.0')) # skin resistance
                    self.ui.tableWidget_19.setItem(layer_i, 1, QtWidgets.QTableWidgetItem(str(layerpolygon['Tskin']))) # skin resistance
                    self.ui.tableWidget_19.item(layer_i, 1).setBackground(QColor(242, 255, 116)) # light yellow

        ## connection for responding to values changed by user
        self.ui.tableWidget_19.blockSignals(False) # unblock signals from tableWidget_18
        #self.ui.tableWidget_19.cellChanged.connect(lambda row, column: self.update_skin_friction_for_soil_layer(row, column, Layer_polygons))


    @pyqtSlot()
    def update_skin_friction_for_soil_layer(self, row, column, Layer_polygons):
        """ Updates skin friction 
        """
        #print(row, column)
        if column == 1:
            try:
                if self.ui.tableWidget_19.item(row, column):
                    Tskin = float(self.ui.tableWidget_19.item(row, column).text())
                    Layer_polygons[row]['Tskin'] = Tskin
                    soilmaterial = Layer_polygons[row]['soilmaterial_layer']
                    print("Soil {0}'s skin resistance for ground anchor is set {1} kN/m".format(soilmaterial, Tskin))
        
            except ValueError:
                self.dialog.show_message_box('Warning', 'Please check if the skin resistance value is correctly entered!')


    def save(self):
        """ Save PLAXMAN's state
        """
        objs = (self.wall, self.final_excavation_level, self.Phases_data, 
                self.points_berm, self.points_berm_base, self.pore_pressure_interp,
                self.points_fine_mesh, self.deltas_ground_to_water, self.deltas_support_to_ground, 
                self.phases_already_generated, self.FoS_phase, self.active_earth_pressure_wedge,
                self.reset_displ_zero_dewatering, self.reset_displ_zero_excavation, self.reset_displ_zero_supporting)

        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_ap_state.mon')
        saveobjs(filename, *objs)
        #print("Plaxman's state is saved in {}".format(filename))


    def load(self):
        """ Load PLAXMAN's state
        """
        # set paths
        self.set_paths_and_file()


        filename = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'plaxman_ap_state.mon')
        if not os.path.isfile(filename):
            self.dialog.show_message_box('Error', 'File {} does not exist for loading'.format(filename))

        else:
            try:
                (self.wall, self.final_excavation_level, self.Phases_data, 
                self.points_berm, self.points_berm_base, self.pore_pressure_interp,
                self.points_fine_mesh, self.deltas_ground_to_water, self.deltas_support_to_ground, 
                self.phases_already_generated, self.FoS_phase, self.active_earth_pressure_wedge,
                self.reset_displ_zero_dewatering, self.reset_displ_zero_excavation, self.reset_displ_zero_supporting) = loadobjs(filename)
            except: # load an old project
                (self.wall, self.final_excavation_level, self.Phases_data, 
                self.points_berm, self.points_berm_base, self.pore_pressure_interp,
                self.points_fine_mesh, self.deltas_ground_to_water, self.deltas_support_to_ground, 
                self.phases_already_generated, self.FoS_phase, self.active_earth_pressure_wedge) = loadobjs(filename)
                #self.reset_displ_zero_dewatering, self.reset_displ_zero_excavation, self.reset_displ_zero_supporting) = loadobjs(filename)
        
            # display model components on gui
            self.display_all_model_components() # not completed, TBD

            # Update phase table in Automated phases
            self.ap_groupbox_ui = self.initialize_automated_phases_table()
            #self.update_phase_table_automated_phases(Phases, self.ap_groupbox_ui.tableWidget)
            self.update_phase_table_automated_phases(self.Phases, self.ap_groupbox_ui.tableWidget, self.Anchors)

            # Reconstruct points fine mesh (around the wall)
            if self.points_fine_mesh:
                self.refine_mesh_around_wall(self.wall, self.x_min, self.x_max, self.Boreholes)

            # Add active earth pressure wedge
            if self.active_earth_pressure_wedge:
                self.add_active_earthpressure_wedge(True)