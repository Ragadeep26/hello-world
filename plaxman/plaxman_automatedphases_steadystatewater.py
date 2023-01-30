# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 11:26:09 2022

@author: nya
"""

from random import randint
from plaxman.plaxman_automatedphases_phreatic import Plaxman_AutomatedPhases_Phreatic
import solver.plaxis2d.input_scripting_commands as plaxis2d_input


class Plaxman_AutomatedPhases_SteadyStateWater(Plaxman_AutomatedPhases_Phreatic):
    """ This class implements Automated phases with dewatering being modelled with steady state ground water flow.
    In Plaxis2D, the parameter 'PorePresCalcType' in calculation phases is to be set as 'Steady state groundwater flow'.
    This class inherits the class Plaxman_AutomatedPhases.
    """
    
    def __init__(self, ui, plot_canvas=None):
        """ Initilizes Plaxman's Automated Phases
        """
        super().__init__(ui, plot_canvas)


    def setup_automated_phases(self):
        """ Starts generating automated phases
        """
        if (self.ui.checkBox_20.checkState() == 2):   # steady state ground water flow
            self.setup_automated_phases_steadystatewater()

        else: # phreatic
            pass


    def setup_automated_phases_steadystatewater(self):
        """ Starts generating automated phases using steady state ground water
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

            # No need to consider porepressure interpolation
            self.setup_automated_phases_porepressure_steadystate_groundwater(wall_id, final_exc_level, depth_embedment)

            # refine mesh around wall
            self.refine_mesh_around_wall(self.wall, self.x_min, self.x_max, self.Boreholes)
            

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if values are correctly entered!')   



    def setup_automated_phases_porepressure_steadystate_groundwater(self, wall_id, final_exc_level, depth_embedment):
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
                    self.add_phase_dewatering(self.Phases, self.Drains, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i, pore_pres_calc_type='Steady state groundwater flow')
                # add excavation phase
                self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], self.deltas_support_to_ground[structure['id']], reset_displ_zero=reset_displ_zero_excavation_phase_i, pore_pres_calc_type='Steady state groundwater flow')

                if 'usage' not in structure: # 'usage' key indicates struts
                    F_prestress = structure['F_prestress']
                    self.add_phase_anchoring(self.Phases, self.Anchors, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i, pore_pres_calc_type='Steady state groundwater flow')
                else: # it is a strut
                    # add struting phase
                    F_prestress = structure['F_prestress']
                    self.add_phase_struting(self.Phases, self.Struts, [structure['id']], [F_prestress], reset_displ_zero=reset_displ_zero_supporting_phase_i, pore_pres_calc_type='Steady state groundwater flow')
        
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i+1)
            # add final dewatering and excavation phase
            soilcluster_ids_dewatering = self.Phases_data[phase_i+1]['soilcluster_ids'] + self.Phases_data[phase_i+2]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i+1]['waterlevel_id'] is not None) and (self.Phases_data[phase_i+1]['excavation_level'] < self.Boreholes[0]['Head']):
                self.add_phase_dewatering(self.Phases, self.Drains, self.Soilclusters_notdried, self.Phases_data[phase_i+1]['waterlevel_id'], soilcluster_ids_dewatering, None, reset_displ_zero=reset_displ_zero_dewatering_phase_i, pore_pres_calc_type='Steady state groundwater flow')
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i+1]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i, pore_pres_calc_type='Steady state groundwater flow')

        else: # Cantilever wall
            phase_i = 0
            reset_displ_zero_dewatering_phase_i, reset_displ_zero_excavation_phase_i, _ = self.set_up_reset_displacements_to_zero(phase_i)
            soilcluster_ids_dewatering = self.Phases_data[phase_i]['soilcluster_ids'] + self.Phases_data[phase_i+1]['soilcluster_ids'] # one additional soil cluster below is considered
            # add dewatering phase if the current excavation level is below the global water level
            if (self.Phases_data[phase_i]['waterlevel_id'] is not None) and (self.Phases_data[phase_i]['excavation_level'] < self.Boreholes[0]['Head']):
                self.add_phase_dewatering(self.Phases, self.Drains, self.Soilclusters_notdried, self.Phases_data[phase_i]['waterlevel_id'], soilcluster_ids_dewatering, reset_displ_zero=reset_displ_zero_dewatering_phase_i, pore_pres_calc_type='Steady state groundwater flow')
            self.add_phase_excavation(self.Phases, self.Soilclusters, self.Phases_data[phase_i]['soilcluster_ids'], reset_displ_zero=reset_displ_zero_excavation_phase_i, pore_pres_calc_type='Steady state groundwater flow')

        # Add reconstruction phases
        Slabs_only = [strut for strut in self.Struts if strut['usage']=='Slab']# Slabs for reconstructions
        Struts_only = [strut for strut in self.Struts if strut['usage']=='Strut']# no Slabs
        Slabs_only_sorted = sorted((structure for structure in Slabs_only), key = lambda structure: structure['position'][1], reverse=False)    # bottom to top
        #Struts_only_sorted = sorted((structure for structure in Struts_only), key = lambda structure: structure['position'][1], reverse=False)  # bottom to top
        for i_slab, slab in enumerate(Slabs_only_sorted):
            self.add_phase_struting(self.Phases, self.Struts, [slab['id']], [slab['F_prestress']], pore_pres_calc_type='Steady state groundwater flow')        # constructing a raft or floor slab
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
                self.add_phase_struting(self.Phases, self.Struts, strut_ids_to_deconstruct, [slab['F_prestress']], deconstruct=True, pore_pres_calc_type='Steady state groundwater flow')   # removing a temporary strut

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
                    waterlevel_id = self.add_waterlevel__(self.Drains, waterlevel_pointL, waterlevel_pointR)
                    self.deltas_ground_to_water[waterlevel_id] = self.delta_ground_to_water
                else:
                    waterlevel_id = None
            else:   # if automated phases are already generated
                if self.Drains:
                    waterlevel_id = self.Drains[i_existing_user_water_item]['id']
                    waterlevel_pointL = (pointBL[0]+1, pointBL[1] - self.deltas_ground_to_water[waterlevel_id])
                    waterlevel_pointR = (pointBR[0]-1, pointBR[1] - self.deltas_ground_to_water[waterlevel_id])
                    # add user water level conditionally
                    if waterlevel_pointL[1] < self.Boreholes[0]['Head']:
                        self.update_user_water_level(self.deltas_ground_to_water, pointBL, self.Drains, waterlevel_id) # update all user water levels !!!
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
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_with_bottom_berm(self.Drains, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
            self.Phases_data.append(phase_data)
        else:
            phase_data, pointTL, pointTR = self.define_phase_data_until_final_excavation_level_no_bottom_berm(self.Drains, soilcluster_bottom, pointTL, pointTR, soilcluster_ids, i_existing_user_water_item)
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



    def add_waterlevel__(self, Drains, pointL, pointR):
        """ Adds drains for water levels"""
        waterlevel = {}
        waterlevel['pointL'] = list(pointL)
        waterlevel['pointR'] = list(pointR)
        waterlevel['id'] = randint(100000, 999999)
            
        waterlevel_pathpatches = self.plot_canvas.plot_waterlevel(waterlevel, color='cyan')
        waterlevel['pathpatches'] = waterlevel_pathpatches

        Drains.append(waterlevel)
            
        plaxis2d_input.add_waterlevel_automatedphases_steadystate(self.plaxis2d_input_file, 'g_i', waterlevel)  # adds a drain instead
        #print('User water level is added, water level = {0}'.format(pointL[1]))
            
        #self.ui.comboBox_13.addItem(str(waterlevel['id']))     # do not show, this is a drain

        # Update content in table combined phases
        #self.plaxman_cp.update_waterlevels(Drains, Soilclusters)
        return waterlevel['id']


    def add_phase_dewatering(self, Phases, Drains, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation=None, reset_displ_zero=False, deform_calc_type='Plastic', loading_type='Staged construction', pore_pres_calc_type='Steady state groundwater flow', time_interval=0):
        """ Adds a dewatering phase
        """
        self.add_phase_dewatering__(Phases, Drains, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation, reset_displ_zero, deform_calc_type, loading_type, pore_pres_calc_type, time_interval)
        self.ui.comboBox_31.addItem(str(len(Phases)))  # in Plaxman
        self.ui.comboBox_21.addItem(str(len(Phases)))  # in Backman
        print('{0} phase until level {1} m is created'.format(Phases[-1]['phase_name'], Phases[-1]['y_ref']))


    def add_phase_dewatering__(self, Phases, Drains, Soilclusters_notdried, waterlevel_id, soilcluster_ids, soilcluster_ids_porepressure_interpolation, reset_displ_zero=False, DeformCalcType='Plastic', LoadingType='Staged construction', PorePresCalcType='Steady state groundwater flow', TimeInterval=0):
        """ Adds a dewatering phase
        """
        phasename = 'Dewatering (Steady state groundwater flow)'
        new_phase = {}
        new_phase['waterlevel_soilcluster_ids'] = soilcluster_ids
        new_phase['water_level_id'] = waterlevel_id
        new_phase['phase_id'] = randint(100000, 999999)
        new_phase['phase_name'] = phasename
        new_phase['deform_calc_type'] = DeformCalcType
        new_phase['loading_type'] = LoadingType
        new_phase['pore_pres_calc_type'] = PorePresCalcType
        new_phase['time_interval'] = TimeInterval
        new_phase['reset_displ_zero'] = reset_displ_zero
        new_phase['pathpatches'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['pathpatch_colors'] = []  # pathpatches before change, to reconstruct in 'remove phase'
        new_phase['combined_phase'] = False # flag for combined phase
        new_phase['y_ref'] = None
        #new_phase['delta_ground-water'] = delta_ground_to_water

        y_ref = None
        for waterlevel in Drains:
            if waterlevel['id'] == int(new_phase['water_level_id']):
                y_ref = waterlevel['pointL'][1]
        new_phase['y_ref'] = y_ref  # y_ref is needed for report generation
        new_phase['drain_head'] = y_ref
                
        setdry_soilcluster_ids = []
        for soilcluster in Soilclusters_notdried:
            if soilcluster['pointTR'] is not None:   # rectangular soil cluster
                if (soilcluster['pointBL'][1] > y_ref) and (soilcluster['pointBR'][1] > y_ref):
                    setdry_soilcluster_ids.append(soilcluster['id'])
            elif 'points' in soilcluster:   # muti-point soil cluster (for berms)
                y_min = min([point[1] for point in soilcluster['points']])
                if y_min > y_ref:
                    setdry_soilcluster_ids.append(soilcluster['id'])
        new_phase['setdry_soilcluster_ids'] = setdry_soilcluster_ids # add this back to self.Soilclusters_notdried in 'remove_phase'
        new_phase['soilcluster_ids_porepressure_interpolation'] = soilcluster_ids_porepressure_interpolation
                
        previous_phase = Phases[-1]
        plaxis2d_input.add_phase_dewatering2(self.plaxis2d_input_file, 'g_i', new_phase, previous_phase, waterlevel_id)
                
        # remove the soilclusters in self.Soilclusters_notdried that have not been dried
        for soilcluster_id in setdry_soilcluster_ids:
            deleted_item = [item for item in Soilclusters_notdried if item['id'] == soilcluster_id][0]
            deleted_item_idx = Soilclusters_notdried.index(deleted_item)
            #print(deleted_item_idx)            
            Soilclusters_notdried.pop(deleted_item_idx)                     
        #print(self.Soilclusters_notdried)

        Phases.append(dict(new_phase))