# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:07:31 2022

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


    def add_project_info(self, project_title, design_situation, fyk):
        """ Adds project information
        """
        self.axes.text(3*Report.cm, 27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        #struts_info1 = 'Number of strut layers: {}'.format(len(Struts))
        struts_info2 = 'Design situation {}'.format(design_situation)
        struts_info3 = 'Characteristic steel grade: {0:.0f} MPa'.format(fyk)
        self.axes.text(3*Report.cm, 26.4*Report.cm, struts_info2, fontsize=9, fontweight='bold', va='center')
        self.axes.text(3*Report.cm, 25.8*Report.cm, struts_info3, fontsize=9, fontweight='bold', va='center')
        #self.axes.text(3*Report.cm, 25.2*Report.cm, struts_info3, fontsize=9, fontweight='bold', va='center')


    def add_strut_layer_info(self, strut, design_situation, params_psf):
        """ Adds a strut layer
        """
        self.add_table_psf(design_situation, params_psf)
        self.add_table_strut_input_parameters(strut)
        self.add_table_selected_cross_section(strut)
        self.add_table_design_loads(strut['design_loads'])
        y = self.add_table_cross_section_classification(strut)
        y = self.add_table_flexural_buckling_check(strut, y)
        if strut['strut_type'] == 'SteelProfile':
            self.add_table_lateral_torsional_buckling_check(strut, y)


    def add_table_psf(self, design_situation, params_psf):
        """ Adds reinforcement values in table
        """
        x = 3*Report.cm
        y = 25*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Partial safety factors for design situation {0}'.format(design_situation), fontsize=8, fontweight='bold')
        headers = ['\N{GREEK SMALL LETTER GAMMA}_G [-]', '\N{GREEK SMALL LETTER GAMMA}_Q [-]', '\N{GREEK SMALL LETTER GAMMA}_c [-]', '\N{GREEK SMALL LETTER GAMMA}_M0 [-]', '\N{GREEK SMALL LETTER GAMMA}_M1 [-]']
        for key, value in zip(headers, params_psf.values()):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=7)
            x = x + 2.25*Report.cm


    def add_table_strut_input_parameters(self, strut):
        """ Adds table for characteristic input parameters for strut
        """
        x = 3*Report.cm
        y = 23*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Characteristic values for strut design: Strut level {:.2f} mNN'.format(strut['position'][1]), fontsize=8, fontweight='bold')
        items_to_list = ['position', 'direct_x', 'direct_y', 'Lspacing', 'F_strut', 'slope_vert', 'slope_horiz', 'buckling length sy', 'buckling length sz', 'eccentricity e/h', 'eccentricity e/b']
        items_to_list_with_unit = ['Strut level [mNN]', 'direct_x [m]', 'direct_y [m]', 'Lspacing [m]', 'F_strut [kN]', 'slope vert. [deg.]', 'slope horiz. [deg.]', 'buckl. length sy [m]', 'buckl. length sz [m]', 'eccentricity e/h [-]', 'eccentricity e/b [-]']
        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list):
            if i < 6:
                if item == 'position':
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, strut[item][1], fontsize=7)
                else:
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, strut[item], fontsize=7)
                x1 = x1 + 2.5*Report.cm
            else:   # the second row
                self.axes.text(x2, y - 4*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 5*0.6*Report.cm, strut[item], fontsize=7)
                x2 = x2 + 3.0*Report.cm
    

    def add_table_selected_cross_section(self, strut):
        """ Adds the selected cross-section for strut
        """
        x = 3*Report.cm
        y = 20*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Selected cross-section: {0}, profile ID: {1} x {2}'.format(strut['strut_type'], getattr(strut['cross_section'], 'nos'),strut['profile_id']), fontsize=8, fontweight='bold')

        if strut['strut_type'] == 'SteelTube':
            items_to_list = ['D', 't', 'nos', 'distance_beam2beam', 'A', 'Iyy', 'Izz', 'W_el_y', 'W_el_z', 'W_pl_y', 'W_pl_z', 'g', 'p']
            items_to_list_with_unit = ['D [mm]', 't [mm]', 'No. beams [-]', 'd_b2b [mm]', 'A [cm$^2$]', 'Iyy [cm$^4$]', 'Izz [cm$^4$]', 'W_el_y [cm$^3$]', 'W_el_z [cm$^3$]', 'W_pl_y [cm$^3$]', 'W_pl_z [cm$^3$]', 'g [kN/m]', 'p [kN/m]']
        elif strut['strut_type'] == 'SteelProfile':
            items_to_list = ['h', 'b', 'tw', 'tf', 'r', 'nos', 'distance_beam2beam', 'A', 'Iyy', 'Izz', 'W_el_y', 'W_el_z', 'W_pl_y', 'W_pl_z', 'g', 'p']
            items_to_list_with_unit = ['h [mm]', 'b [mm]', 'tw [mm]', 'tf [mm]', 'r [mm]','No. beams [-]', 'd_b2b [mm]', 'A [cm$^2$]', 'Iyy [cm$^4$]', 'Izz [cm$^4$]', 'W_el_y [cm$^3$]', 'W_el_z [cm$^3$]', 'W_pl_y [cm$^3$]', 'W_pl_z [cm$^3$]', 'g [kN/m]', 'p [kN/m]']

        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list):
            if i < 8:
                if item == 'nos':
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, '{}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                elif (item == 'distance_beam2beam') and (getattr(strut['cross_section'], 'nos') == 1):   # do not write distance beam-to-beam for a single beam
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, '-', fontsize=7)
                else:
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, '{:.1f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x1 += 2.0*Report.cm
            else:
                self.axes.text(x2, y - 4*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 5*0.6*Report.cm, '{:.1f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x2 += 2.0*Report.cm


    def add_table_design_loads(self, design_loads):
        """ Adds table for design loads
        """
        x = 3*Report.cm
        y = 16.8*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Design loads', fontsize=8, fontweight='bold')

        items_to_list = ['Nd', 'Myd', 'Mzd']
        items_to_list_with_unit = ["N_d [kN]", "My_d [kNm]", "Mz,d [kNm]"]
        for key, item in zip(items_to_list_with_unit, items_to_list):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, '{:.1f}'.format(design_loads[item]), fontsize=8)
            x = x + 2.25*Report.cm


    def add_table_cross_section_classification(self, strut):
        """ Adds table for cross-section class
        """
        x = 3*Report.cm
        y = 14.8*Report.cm
        self.axes.text(x, y - 0.6*Report.cm, 'Cross-section class: {}'.format(getattr(strut['cross_section'], 'QK')), fontsize=8, fontweight='bold')

        if strut['strut_type'] == 'SteelTube':
            items_to_list = ['QK', 'epsilon', 'd_over_t', 'd_over_t_zul']
            items_to_list_with_unit = ['QK [-]', 'epsilon [-]', 'd/t [-]', 'd/t allow. [-]']
        elif strut['strut_type'] == 'SteelProfile':
            items_to_list = ['QK', 'QK_w', 'QK_f', 'epsilon', 'alpha_web', 'c_over_tw', 'c_over_tw_zul', 'sigma_1_web', 'sigma_2_web', 'psi_web', 'c_over_tf', 'c_over_tf_zul']
            items_to_list_with_unit = ['QK [-]', 'QK_w [-]', 'QK_f [-]', 'epsilon [-]', 'alpha_w [-]', 'c/tw [-]', 'c/tw allow. [-]', 'sigma1_w [kN/cm$^2$]', 'sigma2_w [kN/cm$^2$]', 'psi_w [-]', 'c/tf [-]', 'c/tf allow. [-]']

        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list):
            if i < 7:
                if item in ['QK', 'QK_w', 'QK_f']:
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, '{}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                else:
                    self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                    self.axes.text(x1, y - 3*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x1 += 2.25*Report.cm
                y_final = y - 3*0.6*Report.cm
            else:
                self.axes.text(x2, y - 4*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 5*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x2 += 3.0*Report.cm
                y_final = y - 5*0.6*Report.cm
        
        return y_final  # y_final not fixed


    def add_table_flexural_buckling_check(self, strut, y_start):
        """ Adds table for flexural buckling check
        """
        x = 3*Report.cm
        y = y_start - 0.3*Report.cm

        util_yy = getattr(strut['cross_section'], 'util_total_y')
        util_zz = getattr(strut['cross_section'], 'util_total_z')
        util_max = max(util_yy, util_zz)
        self.axes.text(x, y - 0.6*Report.cm, 'Flexural buckling verification: Total utilization {:.2f}'.format(util_max), fontsize=8, fontweight='bold')

        items_to_list_axis_yy = ['alpha_pl_y', 'alpha_y', 'N_cr_yy', 'lambda_bar_yy', 'chi_yy', 'N_pl_Rd', 'k_yy', 'M_pl_Rd_y', 'util_N_d_y', 'util_M_d_y', 'util_total_y']
        items_to_list_axis_zz = ['alpha_pl_z', 'alpha_z', 'N_cr_zz', 'lambda_bar_zz', 'chi_zz', 'N_pl_Rd', 'k_zz', 'M_pl_Rd_z', 'util_N_d_z', 'util_M_d_z', 'util_total_z']
        items_to_list_with_unit = ["alpha_pl [-]", "imp. alpha [-]", "N_cr [kN]", "lambda [-]", 
                            "red. fact. chi [-]", "N_pl_Rd [kN]", "red. fact. k [-]", "M_pl_Rd [kNm]",
                            "N_d/(chi*N_pl_Rd)", "M_d*k/(M_pl_Rd)", "Total utilization"]

        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list_axis_yy):
            if i < 6:
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                self.axes.text(x1, y - 4*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], items_to_list_axis_zz[i])), fontsize=7)
                x1 += 2.8*Report.cm
                y_final = y - 4*0.6*Report.cm
            else:
                self.axes.text(x2, y - 5*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 6*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                self.axes.text(x2, y - 7*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], items_to_list_axis_zz[i])), fontsize=7)
                x2 += 2.8*Report.cm
                y_final = y - 7*0.6*Report.cm

        return y_final  # y_final not fixed


    def add_table_lateral_torsional_buckling_check(self, strut, y_start):
        """ Adds table for lateral torsional buckling check
        """
        x = 3*Report.cm
        y = y_start- 0.3*Report.cm

        util_total = getattr(strut['cross_section'], 'util_total')
        self.axes.text(x, y - 0.6*Report.cm, 'Lateral torsional buckling verification: Total utilization {:.2f}'.format(util_total), fontsize=8, fontweight='bold')

        items_to_list = ['c_LT', 'c2', 'M_cr', 'lambda_LT', 'chi_LT_z', 'kyz', 'kzy', 'util_N_d', 'util_M_d_y', 'util_M_d_z', 'util_total']
        items_to_list_with_unit = ["coeff. zeta [-]", "tors. radius c$^2$ [m$^2$]", "M_cr [kNm]", "lambda_LT [-]",
                                    "red. fact. chi_LT [-]", "red. fact. k_yz [-]", "red. fact. k_zy [-]", "N_d/(chi*N_pl_Rd)", "My_d*kyy/(My_pl_d)", "Mz_d*kyz/(Mz_pl_d)", "Total utilization"]

        x1 = x
        x2 = x
        for i, item in enumerate(items_to_list):
            if i < 6:
                self.axes.text(x1, y - 2*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x1, y - 3*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x1 += 2.8*Report.cm
            else:
                self.axes.text(x2, y - 4*0.6*Report.cm, items_to_list_with_unit[i], fontsize=7)
                self.axes.text(x2, y - 5*0.6*Report.cm, '{:.2f}'.format(getattr(strut['cross_section'], item)), fontsize=7)
                x2 += 2.8*Report.cm