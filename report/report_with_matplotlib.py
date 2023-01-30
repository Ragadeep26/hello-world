# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 10:07:31 2020

@author: nya
"""
import os
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Circle, Arrow
from matplotlib.table import Table
from matplotlib.transforms import Bbox
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots_Dim
from gui.gui_main_matplotlib import MyStaticMplCanvas


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


    def add_project_info_pile(self, project_title, cross_section, weight_ratio=0.0):
        """ Adds project information for pile wall
        """
        self.axes.text(3*Report.cm, 27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        cross_section_info = 'D{0}mm, spacing b/w second. piles {1}m'.format(cross_section['D']*1000, cross_section['S']*2)
        self.axes.text(3*Report.cm, 26.4*Report.cm, cross_section_info, fontsize=9, fontweight='bold', va='center')
        self.axes.text(3*Report.cm, 25.8*Report.cm, 'Steel rate: {:.2f} Kg/m'.format(weight_ratio), fontsize=9, fontweight='bold', va='center')


    def add_project_info_barrette(self, project_title, cross_section, weight_ratio=0.0):
        """ Adds project information for D-wall
        """
        self.axes.text(3*Report.cm, 27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        cross_section_info = 'D{0}mm, beam width {1}mm'.format(cross_section['D']*1000, cross_section['BT']*1000)
        self.axes.text(3*Report.cm, 26.4*Report.cm, cross_section_info, fontsize=9, fontweight='bold', va='center')
        self.axes.text(3*Report.cm, 25.8*Report.cm, 'Steel rate: {:.2f} Kg/m'.format(weight_ratio), fontsize=9, fontweight='bold', va='center')


    def add_table_conrete(self, concrete_grade, headers, params_concrete, crack_width):
        """ Adds concrete values in table
        """
        x = 3*Report.cm
        y = 21*Report.cm
        concrete_grade_altered = params_concrete['param_0']
        self.axes.text(x, y - 0.3*Report.cm, 'Concrete grade: {0} MPa (cylinder)'.format(concrete_grade_altered), fontsize=8, fontweight='bold')
        for key, value in zip(headers, params_concrete.values()):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=8)
            x = x + 2.05*Report.cm

        self.axes.text(3*Report.cm, y - 4*0.6*Report.cm, 'Crack width: {}'.format(crack_width), fontsize=8)


    def add_table_reinf(self, reinf_grade, headers, params_reinf, min_reinf):
        """ Adds reinforcement values in table
        """
        x = 3*Report.cm
        y = 18*Report.cm
        #self.axes.text(x, y - 0.3*Report.cm, 'Steel grade: {0}'.format(reinf_grade), fontsize=8, fontweight='bold')
        self.axes.text(x, y - 0.3*Report.cm, 'Reinforcement steel', fontsize=8, fontweight='bold')
        for key, value in zip(headers, params_reinf.values()):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=8)
            x = x + 2.25*Report.cm

        self.axes.text(3*Report.cm, y - 4*0.6*Report.cm, 'Mininum reinforcement: {}'.format(min_reinf), fontsize=8)


    def add_table_psf(self, design_situation, headers, params_psf):
        """ Adds reinforcement values in table
        """
        x = 3*Report.cm
        y = 15*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Partial safety factors for design situation {0}'.format(design_situation), fontsize=8, fontweight='bold')
        for key, value in zip(headers, params_psf.values()):
            self.axes.text(x, y - 2*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=8)
            x = x + 2.25*Report.cm


    def add_table_cross_section_pile(self, cross_section):
        """ Adds cross-section data and plots the cross-section
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Cross-section', fontsize=8, fontweight='bold')
        column_labels = ['Diameter \n D [mm]', 'Sep. to edge \n H [mm]', 'Spacing b/w \n second. piles A [m]']
        col = 0
        for key, value in cross_section.items():
            if key=='S':
                value = 2*value # spacing b/w secondary piles

            self.axes.text(x, y - 2*0.6*Report.cm, column_labels[col], fontsize=7)
            #self.axes.text(x, y - 3*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=8)
            x = x + 2.25*Report.cm
            col += 1

        self.plot_cross_section_pile(cross_section['D'], cross_section['H'])


    def add_table_cross_section_barrette(self, cross_section):
        """ Adds cross-section data and plots the cross-section
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Cross-section', fontsize=8, fontweight='bold')
        column_labels = ['Thickness \n D [mm]', 'Width of\npanel BT [mm]', 'Width of\ncage  B [mm]', 'Sep. to edge \n H1 [mm]', 'Sep. to edge \n H2 [mm]', 'Symmetric reinforcement']
        col = 0
        for value in cross_section.values():
            self.axes.text(x, y - 2*0.6*Report.cm, column_labels[col], fontsize=7)
            #self.axes.text(x, y - 3*0.6*Report.cm, key, fontsize=7)
            self.axes.text(x, y - 3*0.6*Report.cm, value, fontsize=8)
            x = x + 2.1*Report.cm
            col += 1
        
        D = cross_section['D']
        BT = cross_section['BT']
        B = cross_section['B']
        H1 = cross_section['H1']
        H2 = cross_section['H2']
        self.plot_cross_section_barrette(D, BT, B, H1, H2)


    def add_table_staggered_reinf_vertical(self, staggered_reinf_vertical_wall, y=None, type=''):
        """ Adds the staggered vertical reinforcement values in table
        """
        x = 3*Report.cm
        if y is None:
            y = 24*Report.cm
        else:
            y = y -0.6*Report.cm

        self.axes.text(x, y - 0.3*Report.cm, 'Vertical reinforcement {0}'.format(type), fontsize=8, fontweight='bold')
        column_labels = ['Level\n [m]', 'n\n [-]', 'Dia.\n [mm]', 'A_s \n [cm^2]', 'Clearance \n [cm]', 'Weight \n [Kg]']
        y = y - 2*0.6*Report.cm
        for label in column_labels:
            self.axes.text(x, y, label, fontsize=7)
            x = x + 2.25*Report.cm
        y = y - 0.6*Report.cm
        for i, reinf_vertical in enumerate(staggered_reinf_vertical_wall):
            x = 3*Report.cm
            self.axes.text(x, y, reinf_vertical['top'], fontsize=8)
            self.axes.text(x + 2.25*Report.cm, y, '{0:.0f}'.format(reinf_vertical['n'], fontsize=8))
            self.axes.text(x + 2*2.25*Report.cm, y, reinf_vertical['dia'], fontsize=8)
            self.axes.text(x + 3*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['A_s']), fontsize=8)
            self.axes.text(x + 4*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['clearance']), fontsize=8)
            self.axes.text(x + 5*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['weight']), fontsize=8)
            y = y - 0.6*Report.cm
            if i == (len(staggered_reinf_vertical_wall)-1):
                x = 3*Report.cm
                self.axes.text(x, y, reinf_vertical['bottom'], fontsize=8)
        
        return y
    

    def add_table_staggered_reinf_shear(self, staggered_reinf_shear_wall, y):
        """ Adds the staggered vertical reinforcement values in table
        """
        x = 3*Report.cm
        y = y - 0.6*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Shear reinforcement', fontsize=8, fontweight='bold')
        column_labels = ['Level\n [m]', 'dia.\n d [mm]', 'n legs\n [-]', 'spacing\n [cm]', 'a_s \n [cm^2/m]', 'Weight \n [Kg]']
        y = y - 2*0.6*Report.cm
        for label in column_labels:
            self.axes.text(x, y, label, fontsize=7)
            x = x + 2.25*Report.cm
        y = y - 0.6*Report.cm
        for i, reinf_shear in enumerate(staggered_reinf_shear_wall):
            x = 3*Report.cm
            self.axes.text(x, y, reinf_shear['top'], fontsize=8)
            self.axes.text(x + 2.25*Report.cm, y, reinf_shear['dia'], fontsize=8)
            self.axes.text(x + 2*2.25*Report.cm, y, '{:.0f}'.format(reinf_shear['n_legs']), fontsize=8)
            self.axes.text(x + 3*2.25*Report.cm, y, reinf_shear['spacing'], fontsize=8)
            self.axes.text(x + 4*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['a_s']), fontsize=8)
            self.axes.text(x + 5*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['weight']), fontsize=8)
            y = y - 0.6*Report.cm
            if i == (len(staggered_reinf_shear_wall)-1):
                x = 3*Report.cm
                self.axes.text(x, y, reinf_shear['bottom'], fontsize=8)
        
        return y


    def add_table_staggered_reinf_vertical_cross_section(self, staggered_reinf_vertical, y=None, type=''):
        """ Adds the staggered vertical reinforcement values in table
        """
        x = 3*Report.cm
        if y is None:
            y = 24*Report.cm
        else:
            y = y - 0.6*Report.cm

        self.axes.text(x, y - 0.3*Report.cm, 'Given longitudinal reinforcement {0}'.format(type), fontsize=8, fontweight='bold')
        column_labels = ['', 'n\n [-]', 'Dia.\n [mm]', 'A_s \n [cm^2]', 'Clearance \n [cm]', 'Weight \n [Kg/m]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            if i == 0:
                x = x + 2*2.25*Report.cm
            else:
                x = x + 2.25*Report.cm
        y = y - 0.6*Report.cm
        for i, reinf_vertical in enumerate(staggered_reinf_vertical):
            x = 3*Report.cm
            if i == 0:  # main bars
                self.axes.text(x, y, 'Main direction', fontsize=8)
            elif i == 1: # additional bars
                self.axes.text(x, y, 'Perpendicular direction', fontsize=8)
            self.axes.text(x + 2*2.25*Report.cm, y, '{0:.0f}'.format(reinf_vertical['n'], fontsize=8))
            self.axes.text(x + 3*2.25*Report.cm, y, reinf_vertical['dia'], fontsize=8)
            self.axes.text(x + 4*2.25*Report.cm, y, '{0:.2f}'.format(abs(reinf_vertical['A_s'])), fontsize=8)
            self.axes.text(x + 5*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['clearance']), fontsize=8)
            self.axes.text(x + 6*2.25*Report.cm, y, '{0:.2f}'.format(reinf_vertical['weight']), fontsize=8)
            y = y - 0.6*Report.cm
        
        return y


    def add_table_staggered_reinf_shear_cross_section(self, staggered_reinf_shear, y):
        """ Adds the staggered vertical reinforcement values in table
        """
        x = 3*Report.cm
        y = y - 0.6*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Given shear reinforcement', fontsize=8, fontweight='bold')
        column_labels = ['',  'dia.\n d [mm]', 'n legs\n [-]', 'spacing\n [cm]', 'a_s \n [cm^2/m]', 'Weight \n [Kg/m]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            if i == 0:
                x = x + 2*2.25*Report.cm
            else:
                x = x + 2.25*Report.cm
        y = y - 0.6*Report.cm
        for i, reinf_shear in enumerate(staggered_reinf_shear):
            x = 3*Report.cm
            if i == 0:  # main bars
                self.axes.text(x, y, 'Main direction', fontsize=8)
            elif i == 1: # additional bars
                self.axes.text(x, y, 'Perpendicular direction', fontsize=8)
            self.axes.text(x + 2*2.25*Report.cm, y, reinf_shear['dia'], fontsize=8)
            self.axes.text(x + 3*2.25*Report.cm, y, '{:.0f}'.format(reinf_shear['n_legs'], fontsize=8))
            self.axes.text(x + 4*2.25*Report.cm, y, reinf_shear['spacing'], fontsize=8)
            self.axes.text(x + 5*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['a_s']), fontsize=8)
            self.axes.text(x + 6*2.25*Report.cm, y, '{:.2f}'.format(reinf_shear['weight']), fontsize=8)
            y = y - 0.6*Report.cm
        
        return y


    def add_table_internal_forces_cross_section(self, internal_forces_permanent, internal_forces_transient, internal_forces_design):
        """ Adds the internal forces in table
        """
        x = 3*Report.cm
        y = 24*Report.cm

        self.axes.text(x, y - 0.3*Report.cm, 'Internal forces', fontsize=8, fontweight='bold')
        column_labels = ['', 'Permanent', 'Transient', 'Design']
        row_labels = ['Normal force N [kN]','Bending moment M [kNm]', 'Shear force Q [kN]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            if i == 0:
                x = x + 2*2.25*Report.cm
            else:
                x = x + 2.25*Report.cm

        y = y - 0.6*Report.cm
        keys = ['N', 'M', 'Q']
        for i, key in enumerate(keys):
            x = 3*Report.cm
            self.axes.text(x , y, row_labels[i], fontsize=8)
            self.axes.text(x + 2*2.25*Report.cm, y, '{:.1f}'.format(internal_forces_permanent[key]), fontsize=8)
            self.axes.text(x + 3*2.25*Report.cm, y, '{:.1f}'.format(internal_forces_transient[key]), fontsize=8)
            self.axes.text(x + 4*2.25*Report.cm, y, '{:.1f}'.format(internal_forces_design[key]), fontsize=8)
            y = y - 0.6*Report.cm
        
        return y


    def add_table_required_reinforcement_cross_section(self, A_s1, A_s2, a_s12):
        """ Adds the required reinforcement in table
        """
        x = 3*Report.cm
        y = 20*Report.cm

        self.axes.text(x, y - 0.3*Report.cm, 'Required reinforcement', fontsize=8, fontweight='bold')
        column_labels = ['', 'Value']
        row_labels = ['Longitudinal A_s1 [cm^2]','Longitudinal A_s1 [cm^2]', 'Shear a_s [cm^2/m]']
        y = y - 2*0.6*Report.cm
        for i, label in enumerate(column_labels):
            self.axes.text(x, y, label, fontsize=7)
            if i == 0:
                x = x + 2*2.25*Report.cm
            else:
                x = x + 2.25*Report.cm

        y = y - 0.6*Report.cm
        values = [A_s1, A_s2, a_s12]
        x = 3*Report.cm
        for i, value in enumerate(values):
            x = 3*Report.cm
            self.axes.text(x, y, row_labels[i], fontsize=8)
            self.axes.text(x + 2*2.25*Report.cm, y, '{0:.2f}'.format(value), fontsize=8)
            y = y - 0.6*Report.cm
        
        return y


    def plot_reinf_cross_section(self, cross_section, reinf_vertical_As1, reinf_vertical_As2, reinf_shear, rotate=False):
        """ Plots reinforcement of cross section
        """
        self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Drawing of reinforcement', fontsize=8, fontweight='bold')
        ax1 = self.axes.figure.add_axes([0.25, 0.25, 0.5, 0.5])
        canvas = MyStaticMplCanvasSubplots_Dim(width=0.5, height=0.5, dpi=100, nrows=1, ncols=1)
        canvas.axes = ax1
        canvas.plot_reinf_cross_section_barrette(cross_section, reinf_vertical_As1, reinf_vertical_As2, reinf_shear, rotate=rotate)


    def add_info_reinf_cross_section_dimensions(self, cross_section):
        """ Adds information about dimensions for the drawing of reinforcement
        """
        x = 3*Report.cm
        y = 7*Report.cm

        text_D = 'Beam height D = {:.2f} m'.format(cross_section['D'])
        text_BT = 'Beam width BT = {:.2f} m'.format(cross_section['BT'])
        text_B = 'Width of reinforcement B = {:.2f} m'.format(cross_section['B'])
        text_H1 = 'Concrete cover H1 = {:.2f} mm'.format(cross_section['H1'])
        text_H2 = 'Concrete cover H2 = {:.2f} mm'.format(cross_section['H2'])
        text_all = [text_D, text_BT, text_B, text_H1, text_H2]
        for text in text_all:
            self.axes.text(x, y, text, fontsize=8, va='center')
            y = y - 0.6*Report.cm
        


    def plot_staggered_reinf_vertical(self, staggered_reinf_vertical_wall, y, A_s, separate=False):
        """ Plots staggered vertical reinforcement
        """

        if not separate:
            self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Staggering of reinforcement', fontsize=8, fontweight='bold')
            ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.3, 0.5])
        else:
            self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Staggering of vertical reinforcement', fontsize=8, fontweight='bold')
            ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])

        ax1.tick_params(axis='both', which='both', labelsize=8)
        if A_s is not None:
            self.plot_reinf(ax1, y, A_s)
            ax1.set_xlabel('A_s [$\mathregular{cm^2}$]', fontsize=8)
        for i, reinf_vertical in enumerate(staggered_reinf_vertical_wall):
            y_top = reinf_vertical['top']
            y_bottom = reinf_vertical['bottom']
            A_s = reinf_vertical['A_s']
            if i > 0:
                A_s_upper = staggered_reinf_vertical_wall[i-1]['A_s']
            else:
                A_s_upper = 0

            annotation = str(int(reinf_vertical['n'])) + 'X' + reinf_vertical['dia'] + 'mm'
            self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, value_upper=A_s_upper, annotation=annotation)

            if i == 0: # first (top) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='first')

            if i == (len(staggered_reinf_vertical_wall) - 1): # last (bottom) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='last')


    def plot_staggered_reinf_vertical_barrette(self, staggered_reinf_vertical_wall_A_s_1, staggered_reinf_vertical_wall_A_s_2, y, A_s1, A_s2, separate=False):
        """ Plots staggered vertical reinforcement
        """

        if not separate:
            self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Staggering of reinforcement', fontsize=8, fontweight='bold')
            ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.3, 0.5])
        else:
            self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Staggering of vertical reinforcement', fontsize=8, fontweight='bold')
            ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])

        ax1.tick_params(axis='both', which='both', labelsize=8)
        if A_s1 is not None:
            self.plot_reinf(ax1, y, A_s1)
            ax1.set_xlabel('A_s1 [$\mathregular{cm^2}$]', fontsize=8)

        if A_s2 is not None:
            self.plot_reinf(ax1, y, A_s2)
            ax1.set_xlabel('A_s2 [$\mathregular{cm^2}$]', fontsize=8)

        for i, reinf_vertical in enumerate(staggered_reinf_vertical_wall_A_s_1):
            y_top = reinf_vertical['top']
            y_bottom = reinf_vertical['bottom']
            A_s = reinf_vertical['A_s']
            if i>0:
                A_s_upper = staggered_reinf_vertical_wall_A_s_1[i-1]['A_s']
            else:
                A_s_upper = 0

            annotation = str(int(reinf_vertical['n'])) + 'X' + reinf_vertical['dia'] + 'mm'
            self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, value_upper=A_s_upper, annotation=annotation)

            if i == 0: # first (top) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='first')

            if i==(len(staggered_reinf_vertical_wall_A_s_1) - 1): # last (bottom) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='last')

        for i, reinf_vertical in enumerate(staggered_reinf_vertical_wall_A_s_2):
            y_top = reinf_vertical['top']
            y_bottom = reinf_vertical['bottom']
            A_s = reinf_vertical['A_s']
            if i>0:
                A_s_upper = staggered_reinf_vertical_wall_A_s_2[i-1]['A_s']
            else:
                A_s_upper = 0

            annotation = str(int(reinf_vertical['n'])) + 'X' + reinf_vertical['dia'] + 'mm'
            self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, value_upper=A_s_upper, annotation=annotation)

            if i == 0: # first (top) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='first')

            if i==(len(staggered_reinf_vertical_wall_A_s_2) - 1): # last (bottom) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, A_s, segment='last')


    def plot_staggered_reinf_shear(self, staggered_reinf_shear_wall, y, a_s, separate=False):
        """ Plots staggered shear reinforcement
        """
        if not separate:
            ax1 = self.axes.figure.add_axes([0.55, 0.2, 0.3, 0.5])
        else:
            self.axes.text(3*Report.cm, 24*Report.cm - 0.3*Report.cm, 'Staggering of shear reinforcement', fontsize=8, fontweight='bold')
            ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])
        ax1.tick_params(axis='both', which='both', labelsize=8)
        if a_s is not None:
            self.plot_reinf(ax1, y, a_s)
            ax1.set_xlabel('a_s [$\mathregular{cm^2/m}$]', fontsize=8)
        for i, reinf_shear in enumerate(staggered_reinf_shear_wall):
            y_top = reinf_shear['top']
            y_bottom = reinf_shear['bottom']
            a_s = reinf_shear['a_s']
            if i>0:
                a_s_upper = staggered_reinf_shear_wall[i-1]['a_s']
            else:
                a_s_upper = 0

            annotation = reinf_shear['dia'] + 'mm@' + str(int(reinf_shear['spacing'])) + 'cm, ' + str(reinf_shear['n_legs']) + ' legs'
            self.plot_reinf_staggering(ax1, y_top, y_bottom, a_s, value_upper=a_s_upper, annotation=annotation)

            if i == 0: # first (top) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, a_s, segment='first')

            if i == (len(staggered_reinf_shear_wall) - 1): # last (bottom) segment
                self.plot_reinf_staggering(ax1, y_top, y_bottom, a_s, segment='last')

    def plot_reinf(self, ax, y, dat):
        """ Plots the required reinforcement areas
        """
        ax.grid(which='both')
        ax.plot(dat, y)
            

    def plot_reinf_staggering(self, ax, y_top, y_bottom, value, segment='inbetween', value_upper=0.0, annotation='', linewidth=2):
        """ Plots it
        """
        ax.plot((value, value), (y_top, y_bottom), color='black', linewidth=linewidth)
        bbox_props = dict(boxstyle="square,pad=0.2", fc="white", ec="b", lw=2, alpha=0.3)
        if value > 0:
            ax.text(value+value*0.1, y_top - (y_top - y_bottom)/2, annotation, ha='left', va='center', size=9, bbox=bbox_props, rotation=90)
        else:
            ax.text(value+value*0.15, y_top - (y_top - y_bottom)/2, annotation, ha='left', va='center', size=9, bbox=bbox_props, rotation=90)
        #self.axes[index].annotate(annotation, (value, y_top - (y_top - y_bottom)/2), rotation=90)
        if segment=='first': # horizontal bar
            ax.plot((0, value), (y_top, y_top), color='black', linestyle='--', linewidth=linewidth)
        elif segment=='last': # horizontal bar
            ax.plot((0, value), (y_bottom, y_bottom), color='black', linestyle='--', linewidth=linewidth)
        elif segment=='inbetween':
            ax.plot((value_upper, value), (y_top, y_top), color='black', linestyle='--', linewidth=linewidth)


    def plot_stress_strain_curves(self, stress_strain):
        """ Plots stress-strain curve of concrete
        """
        ax1 = self.axes.figure.add_axes([0.23, 0.20, 0.25, 0.20])
        ax2 = self.axes.figure.add_axes([0.55, 0.20, 0.25, 0.20])
        ax1.grid(which='both')
        ax1.plot(stress_strain['Ecm_range'], stress_strain['f_ck_range'])
        ax1.set_xlabel('\N{GREEK SMALL LETTER EPSILON}_c [\N{PER MILLE SIGN}]', fontsize=8)
        ax1.set_ylabel(r'f_c [MN/$\mathregular{m^2}$]', fontsize=8)
        ax2.grid(which='both')
        ax2.plot(stress_strain['epsilon_range'], stress_strain['f_yk_range'])
        ax2.set_xlabel('\N{GREEK SMALL LETTER EPSILON}_s [\N{PER MILLE SIGN}]', fontsize=8)
        ax2.set_ylabel(r'f_s [MN/$\mathregular{m^2}$]', fontsize=8)
        ax1.tick_params(axis='both', which='both', labelsize=8)
        ax2.tick_params(axis='both', which='both', labelsize=8)


    def plot_cross_section_pile(self, D, sep):
        """ Plots pile cross-section
        """
        D = D*1000  # mm
        ax1 = self.axes.figure.add_axes([0.65, 0.65, 0.13, 0.13])
        circle1_path = Circle((D/2,D/2), radius=D/2)
        D_inner = D - sep
        circle2_path = Circle((D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        ax1.add_patch(circle1_path)
        ax1.add_patch(circle2_path)
        ax1.set_aspect('equal')
        ax1.set_axis_off()
        ax1.plot()
        self.draw()


    def plot_cross_section_barrette(self, D, BT, B, H1, H2):
        """ Plots barrette cross-section
        """
        D = D*1000 # mm
        BT = BT*1000 # mm
        B = B*1000 # mm
        #ax1 = self.axes.figure.add_axes([0.63, 0.60, 0.22, 0.22])
        ax1 = self.axes.figure.add_axes([0.65, 0.65, 0.12, 0.12])
        rect1_path = Rectangle((0.0, 0.0), BT, D)
        ax1.add_patch(rect1_path)
        rect2_path = Rectangle(((BT-B)/2, H1), B, D-H1-H2, facecolor=None, edgecolor='black', linestyle='--', linewidth=1)
        ax1.add_patch(rect2_path)
        # highlight edges where longitudinal bars are
        points_bottom =[((BT-B)/2, H1), ((BT-B)/2+B, H1)]
        points_top =[((BT-B)/2, D-H2), ((BT-B)/2+B, D-H2)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices_top = np.array(points_top, float)
        vertices_bottom = np.array(points_bottom, float)
        path_top = Path(vertices_top, codes)
        path_bottom = Path(vertices_bottom, codes)
        pathpatch_top = PathPatch(path_top, facecolor='None', alpha=1.0, edgecolor='black', linestyle='--', linewidth=3.0)
        ax1.add_patch(pathpatch_top)
        pathpatch_bottom = PathPatch(path_bottom, facecolor='None', alpha=1.0, edgecolor='black', linestyle='--', linewidth=3.0)
        ax1.add_patch(pathpatch_bottom)

        ax1.set_aspect('equal')
        ax1.set_axis_off()
        ax1.plot()
        self.draw()


    def plot_wall_outputs(self, wall_outputs_phases, A, percentage_N=100.0):
        """ Plots internal forces of wall
        A: width of barrette
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Characteristic wall internal forces per reinforced element and deflection', fontsize=8, fontweight='bold')
        if percentage_N < 100.0:
            self.axes.text(x, y - 2.5*0.3*Report.cm, '{0:.1f}% of the compressive axial force is used in the design'.format(percentage_N), fontsize=8, fontweight='bold')

        ax1 = self.axes.figure.add_axes([0.25, 0.15, 0.57, 0.12])
        ax2 = self.axes.figure.add_axes([0.25, 0.30, 0.57, 0.12])
        ax3 = self.axes.figure.add_axes([0.25, 0.45, 0.57, 0.12])
        ax4 = self.axes.figure.add_axes([0.25, 0.60, 0.57, 0.12])
        ax1.grid(which='both')
        ax2.grid(which='both')
        ax3.grid(which='both')
        ax4.grid(which='both')
        ax1.tick_params(axis='both', which='both', labelsize=8)
        ax2.tick_params(axis='both', which='both', labelsize=8)
        ax3.tick_params(axis='both', which='both', labelsize=8)
        ax4.tick_params(axis='both', which='both', labelsize=8)
        #ax2.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
        #ax3.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
        #ax4.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
        ax1.set_xlabel('Level [m]', fontsize=8)
        ax1.set_xlim(max(wall_outputs_phases[0]['y']), min(wall_outputs_phases[0]['y']))
        ax2.set_xlim(max(wall_outputs_phases[0]['y']), min(wall_outputs_phases[0]['y']))
        ax3.set_xlim(max(wall_outputs_phases[0]['y']), min(wall_outputs_phases[0]['y']))
        ax4.set_xlim(max(wall_outputs_phases[0]['y']), min(wall_outputs_phases[0]['y']))
        ax1.set_ylabel('Ux [cm]', fontsize=8)
        ax2.set_ylabel('N_k [kN]', fontsize=8)
        ax3.set_ylabel('M_k [kNm]', fontsize=8)
        ax4.set_ylabel('Q_k [kN]', fontsize=8)
        for wall_outputs in wall_outputs_phases:
            ax1.plot(wall_outputs['y'], wall_outputs['Ux']*100)
            ax2.plot(wall_outputs['y'], wall_outputs['N']*A)
            ax3.plot(wall_outputs['y'], wall_outputs['M']*A)
            ax4.plot(wall_outputs['y'], wall_outputs['Q']*A)


    def plot_wall_outputs_separate_N(self, wall_outputs_phases, A, percentage_N=100.0):
        """ Plots internal forces of wall
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Characteristic wall axial force per reinforced element (compression is negative)', fontsize=8, fontweight='bold')
        if percentage_N < 100.0:
            self.axes.text(x, y - 2.5*0.3*Report.cm, '{0:.1f}% of the compressive axial force is used in the design'.format(percentage_N), fontsize=8, fontweight='bold')

        ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])
        ax1.grid(which='both')
        ax1.tick_params(axis='both', which='both', labelsize=8)
        ax1.set_xlabel('N_k [kN]', fontsize=8)
        ax1.set_ylabel('Level [m]', fontsize=8)
        for wall_outputs in wall_outputs_phases:
            ax1.plot(wall_outputs['N']*A, wall_outputs['y'])


    def plot_wall_outputs_separate_M(self, wall_outputs_phases, A, staggered_reinf=None):
        """ Plots internal forces of wall
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Characteristic wall bending moment per reinforced element', fontsize=8, fontweight='bold')

        ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])
        ax1.grid(which='both')
        ax1.tick_params(axis='both', which='both', labelsize=8)
        ax1.set_xlabel('M_k [kNm]', fontsize=8)
        ax1.set_ylabel('Level [m]', fontsize=8)
        for wall_outputs in wall_outputs_phases:
            ax1.plot(wall_outputs['M']*A, wall_outputs['y'])
        #if staggered_reinf:
        #    self.plot_wall_output_M_or_Q_staggered(ax1, A, staggered_reinf)


    def plot_wall_outputs_separate_Q(self, wall_outputs_phases, A, staggered_reinf=None):
        """ Plots internal forces of wall
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Charateristic wall shear force per reinforced element', fontsize=8, fontweight='bold')

        ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.5, 0.5])
        ax1.grid(which='both')
        ax1.tick_params(axis='both', which='both', labelsize=8)
        ax1.set_xlabel('Q_k [kN]', fontsize=8)
        ax1.set_ylabel('Level [m]', fontsize=8)
        for wall_outputs in wall_outputs_phases:
            ax1.plot(wall_outputs['Q']*A, wall_outputs['y'])
        #if staggered_reinf:
        #    self.plot_wall_output_M_or_Q_staggered(ax1, A, staggered_reinf, quantity='Q_max')


    def plot_wall_output_M_or_Q_staggered(self, ax, A, staggered_reinf, quantity='M_max'):
        """ Adds segment annotations to bending moment plot
        """

        for i, reinf_vertical in enumerate(staggered_reinf):
            y_top = reinf_vertical['top']
            y_bottom = reinf_vertical['bottom']
            M_max = reinf_vertical[quantity]
            if i>0:
                M_max_upper = staggered_reinf[i-1][quantity]
            else:
                M_max_upper = 0

            annotation = '{0:.1f} kNm'.format(M_max*A)
            annotation_sym = '{0:.1f} kNm'.format(-M_max*A)
            if quantity == 'Q_max':
                annotation = '{0:.1f} kN'.format(M_max*A)
                annotation_sym = '{0:.1f} kN'.format(-M_max*A)

            self.plot_reinf_staggering(ax, y_top, y_bottom, M_max*A, value_upper=M_max_upper*A, annotation=annotation, linewidth=1.5, segment=None)
            self.plot_reinf_staggering(ax, y_top, y_bottom, -M_max*A, value_upper=M_max_upper*A, annotation=annotation_sym, linewidth=1.5, segment=None) # symmetric line

            #if i == 0: # first (top) segment
            #    self.plot_reinf_staggering(ax, y_top, y_bottom, M_max*A, segment='first', linewidth=1.5)  
            #    self.plot_reinf_staggering(ax, y_top, y_bottom, -M_max*A, segment='first', linewidth=1.5)  # symmetric line

            #if i==(len(staggered_reinf) - 1): # last (bottom) segment
            #    self.plot_reinf_staggering(ax, y_top, y_bottom, M_max*A, segment='last', linewidth=1.5)
            #    self.plot_reinf_staggering(ax, y_top, y_bottom, -M_max*A, segment='last', linewidth=1.5)   # symmetric line


    def save_pdf(self, filename):
        """ Saves report as PDF
        """
        self.fig.savefig(filename, pdi=100, format='pdf')


    ## FOR DIMENSIONING OF ANCHORS
    def add_project_info_anchor(self, project_title):
        """ Adds project information for pile wall
        """
        self.axes.text(3*Report.cm,27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        info = 'Anchor dimensions'
        self.axes.text(3*Report.cm,26.4*Report.cm, info, fontsize=9, fontweight='bold', va='center')


    def add_table_psf_anchor(self, params_psfs):
        """ Adds reinforcement values in table
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Partial safety factors'.format(fontsize=8, fontweight='bold'))
        headers_horizontal = ['Situation E', 'Situation V']
        headers_vertical = ['Safety on load gamma_G [-]', 'Safety on strand gamma_M [-]', 'Safety on grout body gamma_a [-]']

        for hv in headers_vertical:
            self.axes.text(x, y - 3*0.6*Report.cm, hv, fontsize=7) # vertical header
            y = y - 0.6*Report.cm

        y = 24*Report.cm
        for i_col, hh in enumerate(headers_horizontal):
            self.axes.text(x + 6.*Report.cm,  y - 2*0.6*Report.cm, hh, fontsize=7) # horizontal header
            self.axes.text(x + 6.*Report.cm,  y - 3*0.6*Report.cm, params_psfs[hh]['gamma_G'], fontsize=7) # gamma_G
            self.axes.text(x + 6.*Report.cm , y - 4*0.6*Report.cm, params_psfs[hh]['gamma_M'], fontsize=7) # gamma_M
            self.axes.text(x + 6.*Report.cm , y - 5*0.6*Report.cm, params_psfs[hh]['gamma_a'], fontsize=7) # gamma_a
            x = x + 2.25*Report.cm
        
    
    def add_table_anchors(self, Anchors, index_start):
        """ Adds table showing dimensions for all anchors
        """
        x = 3*Report.cm
        y = 19*Report.cm
        self.axes.text(x, y - 0.3*Report.cm, 'Anchor dimensions'.format(fontsize=8, fontweight='bold'))

        row_keys = ['strand grade', 'position', 'angle', 'Lspacing', 'strand number', 'strand diameter', 'F_anchor', 'design situation', 'F_d', 'R_t_d', 'F_p', 'F_p permissible', 'F_d/R_t_d', 'F_p/F_p permissible']
        row_units = ['[-]', '[mNN]', '[deg]', '[m]', '[-]', "['']", '[kN]', '[-]', '[kN]', '[kN]', '[kN]', '[kN]', '[-]', '[-]']
        row_labels = [key for key in row_keys]
        # capitalize row headers
        for i in range(10):
            row_labels[i] = row_labels[i].capitalize()
        # add prefix to row headers
        prefixes = ['']*len(row_labels)
        prefixes[8] = 'Design load '
        prefixes[9] = 'Design resist. '
        prefixes[10] = 'Test force '
        prefixes[12] = 'Util. '
        prefixes[13] = 'Util. '
        for i in range(len(row_labels)):
            row_labels[i] = prefixes[i] + row_labels[i]
        # add units
        row_labels = [key + ' ' + unit for key, unit in zip(row_labels, row_units)]

        # vertical headers
        for i_row, key in enumerate(row_labels):
            self.axes.text(x,  y - (i_row+3)*0.6*Report.cm, key, fontsize=7) # horizontal header
        # horizontal headers
        x = 3*Report.cm
        y = 19*Report.cm
        for i_anchor, anchor in enumerate(Anchors):
            self.axes.text(x + 4.*Report.cm,  y - 2*0.6*Report.cm, 'Anchor ' + str(index_start+i_anchor+1), fontsize=7) # horizontal header
            for i_row, key in enumerate(row_keys):
                # format float number to display
                if isinstance(anchor[key], float):
                    text = '{0:.2f}'.format(anchor[key])
                else:
                    text = str(anchor[key])

                if key == 'position':
                    self.axes.text(x + 4.*Report.cm,  y - (i_row+3)*0.6*Report.cm, '{0:.2f}'.format(anchor[key][1]), fontsize=7) 
                else:
                    self.axes.text(x + 4.*Report.cm,  y - (i_row+3)*0.6*Report.cm, text, fontsize=7) 

            x = x + 2.25*Report.cm


    ## FOR STONE COLUMNS
    def add_project_info_stone_columns(self, project_title):
        """ Adds project information 
        """
        self.axes.text(3*Report.cm,27*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')
        info = 'Design of Stone Columns'
        self.axes.text(3*Report.cm,26.4*Report.cm, info, fontsize=9, fontweight='bold', va='center')


    def add_table_stone_column_properties(self, sc_params, additional_params):
        """ Adds table for stone columns properties
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y, 'Properties of stone columns'.format(fontsize=8, fontweight='bold'))

        column_labels = ['Diameter\nD [m]', 'Spacing\na [m]', 'Shape\n[-]','Unit weight\n\N{GREEK SMALL LETTER GAMMA}_c [kN/m^3]', 'Friction angle\n\N{GREEK SMALL LETTER PHI}_c [°]', 
                        "Poisson's\nratio\nnu_c [-]", 'Constrained\nmodulus\nE_c [kPa]'] 

        if 've' in sc_params:
            del sc_params['ve']
        if 'we' in sc_params:
            del sc_params['we']
        if 'Ac_over_A' in sc_params:
            del sc_params['Ac_over_A']

        x = 3*Report.cm
        for label in column_labels:
            self.axes.text(x, y - 3*0.6*Report.cm, label, fontsize=7) # vertical header
            x = x + 2.3*Report.cm
        x = 3*Report.cm
        for value in sc_params.values():
            value = '{:.2f}'.format(value) if isinstance(value, float) else value
            self.axes.text(x, y - 4*0.6*Report.cm, value, fontsize=7) # vertical header
            x = x + 2.3*Report.cm

        column_labels = ['Coeff. active\nearth pressure\nKa [-]', 'Coeff. at rest\nearth pressure\nKo [-]', 'Replacement\nratio\nAc/A [-]']
        x = 3*Report.cm
        for label in column_labels:
            self.axes.text(x, y - 7*0.6*Report.cm, label, fontsize=7) # vertical header
            x = x + 2.3*Report.cm

        x = 3*Report.cm
        for value in additional_params:
            value = '{:.2f}'.format(value) if isinstance(value, float) else value
            self.axes.text(x, y - 8*0.6*Report.cm, value, fontsize=7) # vertical header
            x = x + 2.3*Report.cm


    def plot_stone_columns_cross_section(self, sc_params):
        """ Plots stone columns' cross section
        """
        self.axes.text(3*Report.cm, 18*Report.cm - 0.3*Report.cm, 'Grid of stone columns'.format(fontsize=8, fontweight='bold'))
        ax1 = self.axes.figure.add_axes([0.5, 0.4, 0.2, 0.2])
        canvas = MyStaticMplCanvas(width=1, height=1, dpi=100)
        canvas.axes = ax1
        canvas.plot_stone_columns_cross_section(sc_params['D'], sc_params['a'], sc_params['shape'])


    def add_stone_columns_settings(self, columns_top, columns_bottom, depth_below_columns_toe, water_level, p0):
        """ Adds additional information about 
        """
        x = 3*Report.cm
        y = 11*Report.cm
        self.axes.text(x, y, 'Settings of stone columns'.format(fontsize=8, fontweight='bold'))
        self.axes.text(x, y-2*0.6*Report.cm, 'Top of stone columns: {0:.2f} [mNN]'.format(columns_top), fontsize=7)
        self.axes.text(x, y-3*0.6*Report.cm, 'Base of stone columns: {0:.2f} [mNN]'.format(columns_bottom), fontsize=7)
        self.axes.text(x, y-4*0.6*Report.cm, 'Depth below base of stone columns: {0:.2f} [m]'.format(depth_below_columns_toe), fontsize=7)
        self.axes.text(x, y-5*0.6*Report.cm, 'Ground water level: {0:.2f} [mNN]'.format(water_level), fontsize=7)
        self.axes.text(x, y-6*0.6*Report.cm, 'Surcharge: {0:.2f} [kN/m^2]'.format(p0), fontsize=7)


    def add_table_results_stone_columns(self, sub_soillayers):
        """ Adds table for the results of stone columns
        """
        x = 3*Report.cm
        y = 24*Report.cm
        self.axes.text(x, y, 'Results of soil improvement'.format(fontsize=8, fontweight='bold'))

        column_labels = ['Soil layer\n[-]', 'Top\n[mNN]', 'Bottom\n[mNN]', 'Constr.\nmodul.\nE_s [MPa]', 
                        'Improv.\nfactor\nn0 [-]', 'Improv.\nfactor\nn1 [-]','Depth\nfactor\nfd [-]','Improv.\nfactor\nn2 [-]', 'Unimprov.\nsettl.\n[mm]', 'Improv.\nsettl.\n[mm]']
        for i, label in enumerate(column_labels):
            self.axes.text(x, y - 3*0.6*Report.cm, label, fontsize=7) # vertical header
            if i == 0:
                x = x + 2.6*Report.cm
            else:
                x = x + 1.5*Report.cm
        
        keys = ['soilmaterial_layer', 'top', 'bottom', 'E_s', 'n0', 'n1', 'fd', 'n2', 'u_unimproved_cummulative', 'u_improved_cummulative']
        y = 21*Report.cm
        for sub_soillayer in sub_soillayers:
            x = 3*Report.cm
            for i, key in enumerate(keys):
                if key == 'E_s':
                    value = 0.001*sub_soillayer[key]
                elif key == 'soilmaterial_layer':
                    value = sub_soillayer[key][:-10]
                else:
                    value = sub_soillayer[key]

                value = '{:.2f}'.format(value) if isinstance(value, float) else value
                self.axes.text(x, y, value, fontsize=7) # vertical header
                if i == 0:
                    x = x + 2.6*Report.cm
                else:
                    x = x + 1.5*Report.cm

            y = y - 0.6*Report.cm


    def plot_stone_columns_improvement_results(self, sub_soillayers):
        """ Plots stone columns' improvement results
        """
        self.axes.text(3*Report.cm, 24*Report.cm, 'Results of soil improvement'.format(fontsize=8, fontweight='bold'))
        #axes = self.axes.figure.subplots(1, 3, sharex=False, sharey=False)
        ax1 = self.axes.figure.add_axes([0.25, 0.2, 0.2, 0.5])
        ax2 = self.axes.figure.add_axes([0.45, 0.2, 0.2, 0.5])
        ax3 = self.axes.figure.add_axes([0.65, 0.2, 0.2, 0.5])
        canvas = MyStaticMplCanvasSubplots_Dim(width=1, height=1, dpi=100, nrows=1, ncols=3)
        #canvas.axes = axes
        canvas.axes = [ax1, ax2, ax3]
        level = [sub_soillayer['bottom'] for sub_soillayer in sub_soillayers]
        n2 = [sub_soillayer['n2'] for sub_soillayer in sub_soillayers]
        u_without_sc = [sub_soillayer['u_unimproved_cummulative'] for sub_soillayer in sub_soillayers]
        u_with_sc = [sub_soillayer['u_improved_cummulative'] for sub_soillayer in sub_soillayers]
        canvas.plot_improved_soil_factor(level, n2, 'n_2 [-]', index=0)
        canvas.plot_improved_soil_factor(level, u_without_sc, 'u unimprov. [mm]', index=1)
        canvas.plot_improved_soil_factor(level, u_with_sc, 'u improv. [mm]', index=2)