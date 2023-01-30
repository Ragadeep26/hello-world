# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 10:07:31 2023

@author: nya
"""
import os
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


class Report(FigureCanvas):
    """ This class uses matplotlib for creating A4 pdf report
    """
    cm = 1/2.54

    def __init__(self, parent=None, dpi=100):
        self.fig = Figure(figsize=(21*Report.cm, 29.7*Report.cm), facecolor='w', dpi=dpi)
        #self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)

        # add frame
        self.add_frame()

        self.draw()
        #self.show()


    def add_frame(self):
        """ Adds the outer frame
        """
        try:
            if os.path.exists(sys.modules['moniman_paths']['MONIMAN']):
                MONIMAN = sys.modules['moniman_paths']['MONIMAN']
            else:
                MONIMAN = '.'

        except KeyError:
            MONIMAN = '.'

        # BAUER logo
        COMMON = os.path.join(MONIMAN, 'common')
        bauer_logo = mpimg.imread(os.path.join(COMMON, 'logo.png'))
        imagebox = OffsetImage(bauer_logo, zoom=0.2)
        anno_box = AnnotationBbox(imagebox, (18.2*Report.cm, 26.2*Report.cm), frameon=False)
        self.axes.add_artist(anno_box)

        # Frame layout - rect(lower left point coordinates, width, height, rotation angle)
        rect = Rectangle((2.85*Report.cm, 2.7*Report.cm), 16.45*Report.cm, 24.7*Report.cm, linewidth=0.5, edgecolor='k', facecolor='none')
        self.axes.add_patch(rect)

        #height = [24.95,24.90,24.10,22.2,4.00]
        heights = [24.95, 24.90]
        # drawing the lines that make up the horizontal lines
        for height in heights:
            self.axes.plot([2.85*Report.cm, 19.3*Report.cm], [height*Report.cm, height*Report.cm], linewidth=0.5, color='k')
        # middle vertical line
        #self.axes.plot([12.2*Report.cm, 12.2*Report.cm],[24.10*Report.cm, 22.2*Report.cm],linewidth=0.5,color='k')
        #columns = [2.95, 6.60, 12.30, 15.45]

        self.axes.tick_params(axis='both', which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

        #footnote
        self.axes.text(3*Report.cm, 2.3*Report.cm, 'BAUER Spezialtiefbau GmbH - 86529 Schrobenhausen', fontsize=7)


    def add_project_info(self, project_title, design_situation):
        """ Adds project information
        """
        self.axes.text(3*Report.cm, 27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        #struts_info1 = 'Number of strut layers: {}'.format(len(Struts))
        struts_info2 = 'Design situation {}'.format(design_situation)
        self.axes.text(3*Report.cm, 26.4*Report.cm, struts_info2, fontsize=9, fontweight='bold', va='center')
        #self.axes.text(3*Report.cm, 25.2*Report.cm, struts_info3, fontsize=9, fontweight='bold', va='center')


    def add_waler_layer_info(self, waler, design_situation, params_psf):
        """ Adds a waler layer
        """
        self.add_table_psf(design_situation, params_psf)
        self.add_table_waler_input_parameters(waler)
        self.add_table_selected_cross_section(waler)
        self.add_table_design_loads(waler)
        if waler['waler_type'] == 'steel_profile':
            self.add_table_cross_section_classification(waler)
            self.add_table_stress_verifications(waler)
        else: # add table of required and given reinforcements for concrete
            self.add_table_required_reinforcements(waler)
            self.add_table_reinf_vertical_cross_section(waler)
            self.add_table_reinf_shear_cross_section(waler)


    def add_table_psf(self, design_situation, params_psf):
        """ Adds reinforcement values in table
        """
        x = 3*Report.cm
        y = 25*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Partial safety factors for design situation {0}'.format(design_situation), fontsize=8, fontweight='bold')
        headers = ['\N{GREEK SMALL LETTER GAMMA}_G [-]', '\N{GREEK SMALL LETTER GAMMA}_Q [-]', '\N{GREEK SMALL LETTER GAMMA}_c [-]', '\N{GREEK SMALL LETTER GAMMA}_s [-]', '\N{GREEK SMALL LETTER GAMMA}_M0 [-]', '\N{GREEK SMALL LETTER GAMMA}_M1 [-]']
        for key, value in zip(headers, params_psf.values()):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=7)
            x = x + 2.25*Report.cm


    def add_table_waler_input_parameters(self, waler):
        """ Adds table for characteristic input parameters for waler
        """
        x = 3*Report.cm
        y = 23*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Characteristic values for waler design: Waler level {:.2f} mNN'.format(waler['position'][1]), fontsize=8, fontweight='bold')
        #items_to_list = ['position', 'direct_x', 'direct_y', 'Lspacing', 'F_strut', 'slope_vert', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
        #items_to_list_with_unit = ['Strut level [mNN]', 'direct_x [m]', 'direct_y [m]', 'Lspacing [m]', 'F_strut [kN]', 'slope vert. [deg.]', 'slope horiz. [deg.]', 'buckl. length sy [m]', 'buckl. length sz [m]', 'eccentricity e/h [-]', 'eccentricity e/b [-]']
        items_to_list = ['position', 'Lspacing', 'F_support', 'slope_vert', 'waler_width_support', 'waler_width_influence']
        items_to_list_with_unit = ['Level [mNN]', 'Lspacing sup. [m]', 'F_support [kN]', 'angle sup. [deg.]', 'width of sup. [m]', 'influence width [m]']
        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list):
            if i < 6:
                if item == 'position':
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, waler[item][1], fontsize=7)
                else:
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, waler[item], fontsize=7)
                x1 = x1 + 2.5*Report.cm
            else:   # the second row
                self.axes.text(x2, y - 4*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 5*0.6*Report.cm, waler[item], fontsize=7)
                x2 = x2 + 3.0*Report.cm


    def add_table_selected_cross_section(self, waler):
        """ Adds the selected cross-section for waler
        """
        x = 3*Report.cm
        y = 21.0*Report.cm

        if waler['waler_type'] == 'steel_profile':
            self.axes.text(x, y - 0.6*Report.cm, 'Selected cross-section: {0}, profile ID: {1} x {2}'.format(waler['waler_type'], waler['waler_steel_profile']['nos'], waler['waler_steel_profile']['profile_id']), fontsize=8, fontweight='bold')
            items_to_list = ['profile_id', 'nos', 'fyk']
            items_to_list_with_unit = ['profile ID [-]', 'No. [-]', 'fy,k [MPa]']
            cross_section_type = 'waler_steel_profile'
        elif waler['waler_type'] == 'concrete':
            self.axes.text(x, y - 0.6*Report.cm, 'Selected cross-section: {0}'.format(waler['waler_type']), fontsize=8, fontweight='bold')
            items_to_list = ['b', 'h', 'edge_sep', 'fck', 'fyk']
            items_to_list_with_unit = ['beam width [m]', 'waler beam height [m]', 'concrete cover [mm]', 'fc,k [MPa]', 'fy,k [MPa]']
            cross_section_type = 'waler_concrete'

        x1 = x
        for i, item in enumerate(items_to_list):
            if (item == 'nos') or (item == 'profile_id'):
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{}'.format(waler[cross_section_type][item]), fontsize=7)
            else:
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{:.1f}'.format(waler[cross_section_type][item]), fontsize=7)
            x1 += 3.2*Report.cm


    def add_table_design_loads(self, waler):
        """ Adds table for design loads
        """
        x1 = 3*Report.cm
        x2 = 10*Report.cm
        y = 19.0*Report.cm
        self.axes.text(x1, y - 0.6*Report.cm, 'Design loads Ms,d', fontsize=8, fontweight='bold')
        self.axes.text(x2, y - 0.6*Report.cm, 'Design loads Mf,d', fontsize=8, fontweight='bold')

        if waler['waler_type'] == 'steel_profile':
            design_loads_Msd = {'Nd': waler['design_loads']['Nd'] ,'Myd': waler['design_loads']['Msd'], 'Mzd': 0.0, 'Vd': waler['design_loads']['Vd']}
            design_loads_Mfd = {'Nd': waler['design_loads']['Nd'] ,'Myd': waler['design_loads']['Mfd'], 'Mzd': 0.0, 'Vd': waler['design_loads']['V1d']}
        elif waler['waler_type'] == 'concrete':
            design_loads_Msd = {'Nd': waler['design_loads']['Nd'], 'Myd': waler['design_loads']['Msd'], 'Vd': waler['design_loads']['Vd']}
            design_loads_Mfd = {'Nd': waler['design_loads']['Nd'], 'Myd': waler['design_loads']['Mfd'], 'Vd': waler['design_loads']['Vd']}

        items_to_list = ['Nd', 'Myd', 'Vd']
        items_to_list_with_unit = ["Nd [kN]", "My,d [kNm]", "Vz,d [kN]"]
        for key, item in zip(items_to_list_with_unit, items_to_list):
            self.axes.text(x1, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x1, y - 3*0.6*Report.cm, '{:.1f}'.format(design_loads_Msd[item]), fontsize=8)
            self.axes.text(x2, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x2, y - 3*0.6*Report.cm, '{:.1f}'.format(design_loads_Mfd[item]), fontsize=8)
            x1 = x1 + 2.25*Report.cm
            x2 = x2 + 2.25*Report.cm


    def add_table_cross_section_classification(self, waler):
        """ Adds table for cross-section class
        """
        x = 3*Report.cm
        y = 17*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Cross-section class: {}'.format(getattr(waler['cross_section'], 'QK')), fontsize=8, fontweight='bold')

        items_to_list = ['QK', 'QK_w', 'QK_f', 'c_over_tw', 'c_over_tw_zul', 'c_over_tf', 'c_over_tf_zul']
        items_to_list_with_unit = ['QK [-]', 'QK_w [-]', 'QK_f [-]', 'c/tw [-]', 'c/tw allow. [-]', 'c/tf [-]', 'c/tf allow. [-]']

        x1 = x
        for i, item in enumerate(items_to_list):
            if item in ['QK', 'QK_w', 'QK_f']:
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{}'.format(getattr(waler['cross_section'], item)), fontsize=7)
            else:
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{:.2f}'.format(getattr(waler['cross_section'], item)), fontsize=7)
            x1 += 2.25*Report.cm
    

    def add_table_required_reinforcements(self, waler):
        """ Adds table the required reinforcement
        """
        x = 3*Report.cm
        y = 17*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Required reinforcements', fontsize=8, fontweight='bold')

        items_to_list = ['AsE', 'AsL', 'a_s']
        items_to_list_with_unit = ["As_E earth side [cm$^2$]", "As_L air side [cm$^2$]", "a_s [cm$^2$/m]"]
        for i, item in enumerate(items_to_list):
            self.axes.text(x, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, '{:.2f}'.format(waler['waler_concrete_reinf_required'][item]), fontsize=7)
            x += 3.5*Report.cm
        
    
    def add_table_stress_verifications(self, waler):
        """ Adds table for stress verifications of the steel profile
        """
        x = 3*Report.cm
        y = 15*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Stress verifcations for {0} x {1}'.format(waler['waler_steel_profile']['nos'], waler['waler_steel_profile']['profile_id']), fontsize=8, fontweight='bold')

        row_labels = ['N_Ed/N_pl_Rd [-]', 'V_Ed/V_pl_Rd [-]', 'My_Ed/My_pl_Rd [-]', 'Interaction M/N/V [-]']
        column_labels = ['At span Mf,d', 'At support Ms,d']
        items_to_list_f = ['util_N_f', 'util_V_f', 'util_M_f', 'util_Mfd_interaction']
        items_to_list_s = ['util_N_s', 'util_V_s', 'util_M_s', 'util_Msd_interaction']

        y = y - 0.6*Report.cm
        self.axes.text(x + 4*Report.cm, y - 0.6*Report.cm, column_labels[0], fontsize=7)
        self.axes.text(x + 7*Report.cm, y - 0.6*Report.cm, column_labels[1], fontsize=7)
        y = y - 0.6*Report.cm
        for i, item in enumerate(row_labels):
            y -= 1*0.6*Report.cm
            self.axes.text(x, y, item, fontsize=7)
            self.axes.text(x + 4*Report.cm, y, '{:.2f}'.format(waler['steel_profile_utils'][items_to_list_f[i]]), fontsize=7)
            self.axes.text(x + 7*Report.cm, y, '{:.2f}'.format(waler['steel_profile_utils'][items_to_list_s[i]]), fontsize=7)


    def add_table_reinf_vertical_cross_section(self, waler):
        """ Adds the proposed vertical reinforcement values in table
        """
        x = 3*Report.cm
        y = 14.5*Report.cm
        reinf_vertical_E = waler['waler_concrete_reinf_As_E']
        reinf_vertical_L = waler['waler_concrete_reinf_As_L']
        self.axes.text(x, y - 0.3*Report.cm, 'Proposed longitudinal reinforcements', fontsize=8, fontweight='bold')
        column_labels = ['', 'n\n [-]', 'Dia.\n [mm]', 'A_s \n [cm^2]', 'Clearance \n [cm]', 'Weight \n [Kg/m]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            x = x + 2.25*Report.cm

        y = y - 0.6*Report.cm
        reinf_sides = ['Earth side', 'Air side']
        for i, reinf_vertical in enumerate([reinf_vertical_E, reinf_vertical_L]):
            x = 3*Report.cm
            self.axes.text(x, y, reinf_sides[i], fontsize=7)
            self.axes.text(x + 1*2.25*Report.cm, y, '{}'.format(int(reinf_vertical['n']), fontsize=7))
            self.axes.text(x + 2*2.25*Report.cm, y, reinf_vertical['dia'], fontsize=7)
            self.axes.text(x + 3*2.25*Report.cm, y, '{0:.2f}'.format(abs(reinf_vertical['A_s'])), fontsize=7)
            self.axes.text(x + 4*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['clearance']), fontsize=7)
            self.axes.text(x + 5*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['weight']), fontsize=7)
            y = y - 0.6*Report.cm
        

    def add_table_reinf_shear_cross_section(self, waler):
        """ Adds the proposed shear reinforcement values in table
        """
        x = 3*Report.cm
        y = 11.0*Report.cm
        reinf_shear = waler['waler_concrete_reinf_as']
        self.axes.text(x, y - 0.3*Report.cm, 'Proposed shear reinforcement', fontsize=8, fontweight='bold')
        column_labels = ['',  'dia.\n d [mm]', 'n legs\n [-]', 'spacing\n [cm]', 'a_s \n [cm^2/m]', 'Weight \n [Kg/m]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            x = x + 2.25*Report.cm

        y = y - 0.6*Report.cm
        x = 3*Report.cm
        self.axes.text(x, y, 'Stirrups', fontsize=7)
        self.axes.text(x + 1*2.25*Report.cm, y, reinf_shear['dia'], fontsize=7)
        self.axes.text(x + 2*2.25*Report.cm, y, '{}'.format(int(reinf_shear['n_legs']), fontsize=7))
        self.axes.text(x + 3*2.25*Report.cm, y, reinf_shear['spacing'], fontsize=7)
        self.axes.text(x + 4*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['a_s']), fontsize=7)
        self.axes.text(x + 5*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['weight']), fontsize=7)