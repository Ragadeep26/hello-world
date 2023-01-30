# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 10:12:56 2018

@author: nya
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, Arrow, Rectangle, Polygon
import matplotlib.pyplot as plt
from matplotlib import transforms
#import matplotlib as mpl
import matplotlib.image as mpimg
from matplotlib import gridspec
from matplotlib.ticker import MaxNLocator
from collections.abc import Iterable

#from gui.gui_main_ui.Ui_MainWindow import 
from tools.json_functions import read_data_in_json_item

from PyQt5 import QtWidgets 
from PyQt5.QtCore import pyqtSlot

import numpy as np
import copy
    

class MyStaticMplCanvas3D(FigureCanvas):
    """ 3D plots
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure = Figure()
        self.axis = self.figure.add_subplot(111, projection='3d')
        
        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        #self.figure.tight_layout()  # uses most available frame space
        self.axis.set_xlabel('x (m)')
        self.axis.set_ylabel('y (m)')
        self.axis.set_zlabel('z (m)')
        #self.axis.mouse_init(rotate_btn=1, zoom_btn=3)  # enables mouse interactions
        self.axis.mouse_init()


    def set_axis_equal_3d(self):
        """ Sets equal aspect ratio
        """
        extents = np.array([getattr(self.axis, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.axis, 'set_{}lim'.format(dim))(ctr - r, ctr + r)
        

    def clear_canvas(self):
        """ Clears 3d canvas
        """
        self.axis.cla()
        self.axis.set_xlabel('x (m)')
        self.axis.set_ylabel('y (m)')
        self.axis.set_zlabel('z (m)')


    def plot_borelog(self, borelog, radius, layers):
        """ Plot a borelog
        """
        x = borelog.position['x']
        y = borelog.position['y']
        #Head = borelog.position['Head']
        tops = borelog.tops
        bottoms = borelog.bottoms
        layer_i = 0
        for top, bottom in zip(tops, bottoms):
            Xc, Yc, Zc = self.data_for_cylinder_along_z(x , y, top, bottom, radius = 1)
            color = layers[layer_i]['color']
            self.axis.plot_surface(Xc, Yc, Zc, alpha=0.5, color=color)
            layer_i += 1

        self.axis.autoscale()
        self.set_axis_equal_3d() # use this code instead
        self.draw()


    def data_for_cylinder_along_z(self, center_x, center_y, top, bottom, radius):
        z = np.linspace(top, bottom, 10)
        theta = np.linspace(0, 2*np.pi, 6)
        theta_grid, z_grid=np.meshgrid(theta, z)
        x_grid = radius*np.cos(theta_grid) + center_x
        y_grid = radius*np.sin(theta_grid) + center_y

        return x_grid,y_grid,z_grid


    def plot_interpolated_layer(self, gridx, gridy, gridz):
        """ Plots the interpolated surfce of the soil layer
        """
        self.axis.plot_surface(gridx, gridy, gridz, alpha=0.5)
        #self.axis.autoscale()
        self.set_axis_equal_3d() # use this code instead
        self.draw()


class MyStaticMplCanvasSubplots_Dim(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, nrows=2, ncols=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.gs = gridspec.GridSpec(nrows, ncols, figure=self.fig)
        #self.axis_1 = self.fig.add_subplot(self.gs[0, 0], sharex=None, sharey=None)
        #self.axis_2 = self.fig.add_subplot(self.gs[1, 0], sharex=None, sharey=None)
        self.axes = self.fig.subplots(nrows, ncols, sharex=False, sharey=False)
        
        FigureCanvas.__init__(self, self.fig)
        
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def plot_stress_strain_material(self, strain, stress, index=0):
        """ Plots stress-strain curve for concrete material
        """
        self.axes[index].cla()
        self.axes[index].grid(which='both')
        self.axes[index].plot(strain, stress)

        if index==0:
            self.axes[index].set_xlabel('\N{GREEK SMALL LETTER EPSILON}_c [\N{PER MILLE SIGN}]')
            self.axes[index].set_ylabel(r'f_c [MN/$\mathregular{m^2}$]')
        elif index==1:
            self.axes[index].set_xlabel('\N{GREEK SMALL LETTER EPSILON}_s [\N{PER MILLE SIGN}]')
            self.axes[index].set_ylabel(r'f_s [MN/$\mathregular{m^2}$]')

        self.axes[index].autoscale_view()
        self.draw()


    def plot_cross_section_pile(self, D, sep):
        """ Plots cross-section of the pile
        D: diameter, sep: separation to edge
        """
        D = D*1000 # mm
        self.axes.cla()
        circle1_path = Circle((D/2,D/2), radius=D/2)
        self.axes.add_patch(circle1_path)
        D_inner = D - sep
        circle1_path = Circle((D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        self.axes.add_patch(circle1_path)

        #self.axes.axvline(D/2, color='black', linestyle='--')
        #self.axes.axvline(S+D/2 , color='black', linestyle='--')
        #self.axes.axvline(2*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
    

    def plot_cross_section_barrette(self, D, BT, B, H1, H2):
        """ Plots cross-section of the barrettes
        D: thickness, BT: width of trench
        H1/H2: separation to edge
        """
        D = D*1000 # mm
        BT = BT*1000 # mm
        B = B*1000 # mm
        self.axes.cla()
        rect1_path = Rectangle((0.0, 0.0), BT, D)
        self.axes.add_patch(rect1_path)
        rect2_path = Rectangle(((BT-B)/2, H1), B, D-H1-H2, facecolor=None, edgecolor='black', linestyle='--', linewidth=1)
        self.axes.add_patch(rect2_path)

        # highlight edges where longitudinal bars are
        points_bottom =[((BT-B)/2, H1), ((BT-B)/2+B, H1)]
        points_top =[((BT-B)/2, D-H2), ((BT-B)/2+B, D-H2)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices_top = np.array(points_top, float)
        vertices_bottom = np.array(points_bottom, float)
        path_top = Path(vertices_top, codes)
        path_bottom = Path(vertices_bottom, codes)
        pathpatch_top = PathPatch(path_top, facecolor='None', alpha=1.0, edgecolor='black', linestyle='--', linewidth=3.0)
        self.axes.add_patch(pathpatch_top)
        pathpatch_bottom = PathPatch(path_bottom, facecolor='None', alpha=1.0, edgecolor='black', linestyle='--', linewidth=3.0)
        self.axes.add_patch(pathpatch_bottom)

        #self.axes.axvline(D/2, color='black', linestyle='--')
        #self.axes.axvline(S+D/2 , color='black', linestyle='--')
        #self.axes.axvline(2*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()


    def plot_reinf_cross_section_barrette(self, cross_section, reinf_vertical_As1_all, reinf_vertical_As2_all, reinf_shear_all=None, rotate=False):
        """ Plots cross-section of the barrettes with given reinforcement
        D: thickness, BT: width of trench
        H1/H2: separation to edge
        """
        D = cross_section['D']*1000 # mm
        BT = cross_section['BT']*1000 # mm
        B = cross_section['B']*1000 # mm
        H1 = cross_section['H1']
        H2 = cross_section['H2']
        #self.axes.cla()
        if rotate:
            rect_path_outline = Rectangle((0.0-0.1*D, 0.0-0.1*BT), D+0.2*D, BT+0.2*BT, facecolor='none', edgecolor='none', linestyle='-', linewidth=1.5) # margins
        else:
            rect_path_outline = Rectangle((0.0-0.1*BT, 0.0-0.1*D), BT+0.2*BT, D+0.2*D, facecolor='none', edgecolor='none', linestyle='-', linewidth=1.5) # margins
        self.axes.add_patch(rect_path_outline)
        if rotate:
            rect1_path = Rectangle((0.0, 0.0), D, BT, facecolor='grey', edgecolor='black', linestyle='-', linewidth=1.5)
            rect2_path = Rectangle((H1, (BT-B)/2), D-H1-H2, B, facecolor='none', edgecolor='black', linestyle='--', linewidth=1)
        else:
            rect1_path = Rectangle((0.0, 0.0), BT, D, facecolor='grey', edgecolor='black', linestyle='-', linewidth=1.5)
            rect2_path = Rectangle(((BT-B)/2, H1), B, D-H1-H2, facecolor='none', edgecolor='black', linestyle='--', linewidth=1)
        self.axes.add_patch(rect1_path)
        self.axes.add_patch(rect2_path)
        # annotate dimensions D, B, BT, H1, H2
        if rotate:
            self.axes.annotate('', xy=(0, BT+0.02*BT), xycoords='data', xytext=(H1, BT+0.02*BT), arrowprops=dict(arrowstyle='-'))
            self.axes.annotate('H1', xy=(0, BT+0.05*D), xycoords='data', xytext=(0, BT+0.05*BT), rotation=0, fontsize=8, color='black', zorder=20)

            self.axes.annotate('', xy=(D-H2, BT+0.02*BT), xycoords='data', xytext=(D, BT+0.02*BT), arrowprops=dict(arrowstyle='-'))
            self.axes.annotate('H2', xy=(D-H2, BT+0.05*D), xycoords='data', xytext=(D-H2, BT+0.05*BT), rotation=0, fontsize=8, color='black', zorder=20)
            self.axes.annotate('', xy=(-0.02*D, (BT-B)/2), xycoords='data', xytext=(-0.02*D, (BT-B)/2+B), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('B', xy=(-0.06*D, B*1/3), xycoords='data', xytext=(-0.06*D, B**1/3), rotation=90, fontsize=8, color='black', zorder=20)
            self.axes.annotate('', xy=(D+0.06*D, 0.0), xycoords='data', xytext=(D+0.06*D, BT), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('BT', xy=(D+0.02*D, BT*1/3), xycoords='data', xytext=(D+0.02*D, BT**1/3), rotation=90, fontsize=8, color='black', zorder=20)
            self.axes.annotate('', xy=(D-H1, -0.06*D), xycoords='data', xytext=(H2, -0.06*D), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('D-H2-H2', xy=((D-H1)/3, -0.05*D), xycoords='data', xytext=((D-H1)/3, -0.05*D), rotation=0, fontsize=8, color='black', zorder=20)
        else:
            #text = 'B={0:.0f}mm'.format(B)
            self.axes.annotate('', xy=((BT-B)/2 + B, -0.06*D), xycoords='data', xytext=((BT-B)/2, -0.06*D), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('B', xy=((BT-B)/2 + B/3, -0.05*D), xycoords='data', xytext=((BT-B)/2 + B/3, -0.05*D), fontsize=8, color='black', zorder=20)
            #text = 'BT={0:.0f}mm'.format(BT)
            self.axes.annotate('', xy=(0, D + 0.04*D), xycoords='data', xytext=(BT, D + 0.04*D), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('BT', xy=(0 + B/3, D + 0.05*D), xycoords='data', xytext=(0 + B/3, D + 0.05*D), fontsize=8, color='black', zorder=20)
            #text = 'H1'
            self.axes.annotate('', xy=(-0.02*BT, 0), xycoords='data', xytext=(-0.02*BT, H1), arrowprops=dict(arrowstyle='-'))
            self.axes.annotate('H1', xy=(-0.05*BT, H1/2), xycoords='data', xytext=(-0.05*BT, H1/2), rotation=90, fontsize=8, color='black', zorder=20)
            #text = 'H2'
            self.axes.annotate('', xy=(-0.02*BT, D-H1), xycoords='data', xytext=(-0.02*BT, D), arrowprops=dict(arrowstyle='-'))
            self.axes.annotate('H2', xy=(-0.05*BT, D-H1/2), xycoords='data', xytext=(-0.05*BT, D-H1/2), rotation=90, fontsize=8, color='black', zorder=20)
            #text = 'D-H1-H2={0:.0f}mm'.format(D-H1-H2)
            self.axes.annotate('', xy=(BT+0.05*BT, H1), xycoords='data', xytext=(BT+0.05*BT, D-H2), arrowprops=dict(arrowstyle='<->'))
            self.axes.annotate('D-H2-H2', xy=(BT+0.02*BT, D*2/3), xycoords='data', xytext=(BT+0.02*BT, D*1/3), rotation=90, fontsize=8, color='black', zorder=20)

            ## annotate H1, H2
            #text = 'H1={0:.0f}mm, H2={1:.0f}mm'.format(H1, H2)
            #self.axes.annotate(text, xy=(-0.05*BT, D/2), xycoords='data', xytext=(-0.05*BT, D/2), rotation=90, fontsize=8, color='black', zorder=20)

        reinf_vertical_As1 = reinf_vertical_As1_all[0]
        reinf_vertical_As1_additional = None
        reinf_vertical_As2 = reinf_vertical_As2_all[0]
        reinf_vertical_As2_additional = None
        # plot given reinforcement reinf_vertical_As1 (lower edge)
        self.plot_bars_vertical(self.axes, reinf_vertical_As1, D, B, BT, H1, H2, position='bottom', text_position='above', rotate=rotate)

        # plot given reinforcement reinf_vertical_As2 (upper edge)
        self.plot_bars_vertical(self.axes, reinf_vertical_As2, D, B, BT, H1, H2, position='top', text_position='below', rotate=rotate)

        if len(reinf_vertical_As1_all) == 2:
            reinf_vertical_As1_additional = reinf_vertical_As1_all[1]
        if len(reinf_vertical_As2_all) == 2:
            reinf_vertical_As2_additional = reinf_vertical_As2_all[1]

        # plot additional given reinforcement 
        if reinf_vertical_As1_additional:
            self.plot_bars_vertical_additional(self.axes, reinf_vertical_As1_additional, D, B, BT, H1, H2, position='left', text_position='right', rotate=rotate)

        # plot additional given reinforcement 
        if reinf_vertical_As2_additional:
            self.plot_bars_vertical_additional(self.axes, reinf_vertical_As2_additional, D, B, BT, H1, H2, position='right', text_position='left', rotate=rotate)

        # plot shear reinforcement
        if reinf_shear_all:
            reinf_shear = reinf_shear_all[0]
            if reinf_shear['embrace']:
                for emb in reinf_shear['embrace'].split(';'):
                    if reinf_vertical_As1:
                        if len(emb.split()) > 1:
                            self.plot_bars_shear_double(self.axes, emb, reinf_shear, reinf_vertical_As1, D, B, BT, H1, H2, rotate=rotate)
                        else:
                            self.plot_bars_shear_single(self.axes, emb, reinf_shear, reinf_vertical_As1, D, B, BT, H1, H2, rotate=rotate)

            if len(reinf_shear_all) > 1:
                reinf_shear = reinf_shear_all[1]
                if reinf_shear['embrace']:
                    for emb in reinf_shear['embrace'].split(';'):
                        if reinf_vertical_As1_additional:
                            if len(emb.split()) > 1:
                                self.plot_bars_shear_double_additional(self.axes, emb, reinf_shear, reinf_vertical_As1_additional, D, B, BT, H1, H2, rotate=rotate)
                            else:
                                self.plot_bars_shear_single_additional(self.axes, emb, reinf_shear, reinf_vertical_As1_additional, D, B, BT, H1, H2, rotate=rotate)
        
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()


    def plot_bars_vertical(self, ax, reinf_vertical_As, D, B, BT, H1, H2, position='bottom', text_position='above', rotate=False):
        """ plots single/ double longitudinal bars
        """
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_x = (B - 2*dia)/(n-1) # spacing b/w bars in mm
            x_i = (BT-B)/2 + dia
            y_i = H1 + dia/2 if position == 'bottom' else D - H2 - dia/2
            for i in range(n):
                if rotate:
                    bar1 = Circle((y_i, x_i-dia/2), dia/2, color='orange')
                    bar2 = Circle((y_i, x_i+dia/2), dia/2, color='orange')
                else:
                    bar1 = Circle((x_i-dia/2, y_i), dia/2, color='orange')
                    bar2 = Circle((x_i+dia/2, y_i), dia/2, color='orange')
                x_i += delta_x
                ax.add_patch(bar1)
                ax.add_patch(bar2)
        else:
            dia = float(reinf_vertical_As['dia'])
            delta_x = (B - dia)/(n-1) # spacing b/w bars in mm
            x_i = (BT-B)/2 + dia/2
            y_i = H1 + dia/2 if position == 'bottom' else D - H2 - dia/2
            for i in range(n):
                if rotate:
                    bar = Circle((y_i, x_i), dia/2, color='orange')
                else:
                    bar = Circle((x_i, y_i), dia/2, color='orange')
                x_i += delta_x
                ax.add_patch(bar)

        text = '{0:.0f} bars {1} mm'.format(n, reinf_vertical_As['dia'])
        x_i = (BT-B)/2 + dia/2 + delta_x*(3/2*n//2)
        if rotate:
            (x_not, y_not) = (y_i, x_i)
        else:
            (x_not, y_not) = (x_i, y_i)
        if text_position == 'below':
            self.axes.annotate(text, xy=(x_not, y_not), xycoords='data', color='orange', weight='bold', zorder=10,
                                xytext= (x_not-0.3*D, y_not - 0.05*BT), arrowprops=dict(arrowstyle = "->", ec="orange"), fontsize=8)
        elif text_position == 'above':
            self.axes.annotate(text, xy=(x_not, y_not), xycoords='data', color='orange', weight='bold', zorder=10,
                                xytext= (x_not, y_not + 0.05*BT), arrowprops=dict(arrowstyle = "->", ec="orange"), fontsize=8)
        

    def plot_bars_vertical_additional(self, ax, reinf_vertical_As, D, B, BT, H1, H2, position='left', text_position='right', rotate=False):
        """ plots single/ double longitudinal bars
        """
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_y = (D - H1 - H2 - 2*dia)/(n + 2 -1) # spacing b/w bars in mm
            x_i = (BT-B)/2 + dia/2 if position=='left' else B + (BT-B)/2 - dia/2
            y_i = H1 + dia + delta_y
            for i in range(n):
                if rotate:
                    bar1 = Circle((y_i-dia/2, x_i), dia/2, color='blue')
                    bar2 = Circle((y_i+dia/2, x_i), dia/2, color='blue')
                else:
                    bar1 = Circle((x_i, y_i-dia/2), dia/2, color='blue')
                    bar2 = Circle((x_i, y_i+dia/2), dia/2, color='blue')
                y_i += delta_y
                ax.add_patch(bar1)
                ax.add_patch(bar2)

        else:
            dia = float(reinf_vertical_As['dia'])
            delta_y = (D - H1 - H2 - dia)/(n + 2 -1) # spacing b/w bars in mm
            x_i = (BT-B)/2 + dia/2 if position=='left' else B + (BT-B)/2 - dia/2
            y_i = H1 + dia/2 + delta_y
            for i in range(n):
                if rotate:
                    bar = Circle((y_i, x_i), dia/2, color='blue')
                else:
                    bar = Circle((x_i, y_i), dia/2, color='blue')
                y_i += delta_y
                ax.add_patch(bar)

        text = '{0:.0f} bars {1} mm'.format(n, reinf_vertical_As['dia'])
        y_i = H1 + dia/2 + delta_y*(n//2 + 1)
        if rotate:
            (x_not, y_not) = (y_i, x_i)
            rotation_text = 0
        else:
            (x_not, y_not) = (x_i, y_i)
            rotation_text = 90
        if text_position == 'right':
            self.axes.annotate(text, xy=(x_not, y_not), xycoords='data', color='blue', weight='bold', zorder=10,
                                xytext= ((x_not - 0.2*B), y_not-0.2*B), arrowprops=dict(arrowstyle = "->", ec="blue"), rotation=rotation_text, fontsize=8)
        elif text_position == 'left':
            self.axes.annotate(text, xy=(x_not, y_not), xycoords='data', color='blue', weight='bold', zorder=10,
                                xytext= ((x_not + 0.2*B), y_not+0.2*B), arrowprops=dict(arrowstyle = "->", ec="blue"), rotation=rotation_text, fontsize=8)


    def plot_bars_shear_double(self, ax, emb, reinf_shear, reinf_vertical_As, D, B, BT, H1, H2, rotate=False):
        """ plots doubly embraced stirrup
        """
        idx_x_start = int(emb.split()[0]) - 1
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_x = (B - 2*dia)/(n-1) # spacing b/w bars in mm
            x_start = (BT-B)/2 + idx_x_start*delta_x
            idx_x_end = int(emb.split()[1]) - 1
            x_end = (BT-B)/2 + 2*dia + idx_x_end*delta_x
            width = x_end - x_start

        else:
            dia = float(reinf_vertical_As['dia'])
            delta_x = (B - dia)/(n-1) # spacing b/w bars in mm
            x_start = (BT-B)/2 + idx_x_start*delta_x
            idx_x_end = int(emb.split()[1]) - 1
            x_end = (BT-B)/2 + dia + idx_x_end*delta_x
            width = x_end - x_start

        if idx_x_end < n - 1:
            if rotate:
                embrace_path = Rectangle((H1-0.5*dia, x_start), D-H1-H2+1*dia, width, facecolor='none', edgecolor='red', alpha=1.0, linestyle='-', linewidth=2)
            else:
                embrace_path = Rectangle((x_start, H1-0.5*dia), width, D-H1-H2+1*dia, facecolor='none', edgecolor='red', alpha=1.0, linestyle='-', linewidth=2)
            ax.add_patch(embrace_path)
        else:
            if rotate:
                embrace_path = Rectangle((H1, x_start), D-H1-H2+1, width, facecolor='none', edgecolor='red', alpha=1.0, linestyle='-', linewidth=2)
            else:
                embrace_path = Rectangle((x_start, H1), width, D-H1-H2+1, facecolor='none', edgecolor='red', alpha=1.0, linestyle='-', linewidth=2)
            ax.add_patch(embrace_path)
        text = '{0}mm@{1:.0f}cm, {2:.0f} legs'.format(reinf_shear['dia'], reinf_shear['spacing'], reinf_shear['n_legs'])
        if rotate:
            (x_not, y_not) = (D*1/5, x_start)
            rotation_text = 0
        else:
            (x_not, y_not) = (x_start, D*1/5)
            rotation_text = 90
        ax.annotate(text, xy=(x_not, y_not), xycoords='data', color='red', weight='bold', zorder=10,
                            xytext= ((x_not+0.1*D), y_not+0.1*D), arrowprops=dict(arrowstyle = "->", ec="red"), rotation=rotation_text, fontsize=8)

        # knots
        slope = 1/3
        if rotate:
            point1_x = x_start + 0.05*BT
            point1_y = H1 + 0.05*BT*slope
            points = [(H1, x_start), (point1_y, point1_x)]
        else:
            point1_x = x_start + 0.05*D 
            point1_y = H1 + 0.05*D*slope
            points = [(x_start, H1), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='red', linewidth=2, zorder=1)
        ax.add_patch(pathpatch)

        slope = 3/1
        if rotate:
            point1_x = x_start + 0.02*BT
            point1_y = H1 + 0.02*BT*slope
            points = [(H1, x_start), (point1_y, point1_x)]
        else:
            point1_x = x_start + 0.02*D 
            point1_y = H1 + 0.02*D*slope
            points = [(x_start, H1), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='red', linewidth=2, zorder=1)
        ax.add_patch(pathpatch)


    def plot_bars_shear_double_additional(self, ax, emb, reinf_shear, reinf_vertical_As, D, B, BT, H1, H2, rotate=False):
        """ plots doubly embraced stirrup
        """
        idx_y_start = int(emb.split()[0]) - 1
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_y = (D - H1 - H2 - 2*dia)/(n + 2 -1) # spacing b/w bars in mm
            x_start = (BT-B)/2 
            y_start = H1 + idx_y_start*delta_y
            idx_y_end = int(emb.split()[1]) - 1
            y_end = H1 + 2*dia + idx_y_end*delta_y
            height = y_end - y_start

        else:
            dia = float(reinf_vertical_As['dia'])
            delta_y = (D - H1 - H2 - dia)/(n + 2 -1) # spacing b/w bars in mm
            x_start = (BT-B)/2 
            y_start = H1 + idx_y_start*delta_y
            idx_y_end = int(emb.split()[1]) - 1
            y_end = H1 + dia + idx_y_end*delta_y
            height = y_end - y_start

        if idx_y_end < n + 2 - 1:
            if rotate:
                embrace_path = Rectangle((y_start, x_start-0.5*dia), height, B+1*dia, facecolor='none', edgecolor='pink', alpha=1.0, linestyle='-', linewidth=1.5)
            else:
                embrace_path = Rectangle((x_start-0.5*dia, y_start), B+1*dia, height, facecolor='none', edgecolor='pink', alpha=1.0, linestyle='-', linewidth=1.5)
            ax.add_patch(embrace_path)
        else:
            if rotate:
                embrace_path = Rectangle((y_start, x_start), height, B, facecolor='none', edgecolor='pink', alpha=1.0, linestyle='-', linewidth=1.5)
            else:
                embrace_path = Rectangle((x_start, y_start), B, height, facecolor='none', edgecolor='pink', alpha=1.0, linestyle='-', linewidth=1.5)
            ax.add_patch(embrace_path)
        text = '{0}mm@{1:.10}cm, {2:.0f} legs'.format(reinf_shear['dia'], reinf_shear['spacing'], reinf_shear['n_legs'])
        if rotate:
            (x_not, y_not) = (y_start, x_start + BT*1/2)
            rotation_text = 90.0
        else:
            (x_not, y_not) = (x_start + BT*1/2, y_start)
            rotation_text = 0.0
        ax.annotate(text, xy=(x_not, y_not), xycoords='data', color='pink', weight='bold', zorder=10,
                            xytext= (x_not + 0.1*D, y_not + 0.1*D), arrowprops=dict(arrowstyle = "->", ec="pink"), rotation=rotation_text, fontsize=8)

        # knots
        slope = 3/1
        if rotate:
            point1_y = x_start + 0.03*BT 
            point1_x = y_start + 0.03*BT*slope
            points = [(y_start, x_start), (point1_x, point1_y)]
        else:
            point1_x = x_start + 0.03*D 
            point1_y = y_start + 0.03*D*slope
            points = [(x_start, y_start), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='pink', linewidth=1.5, zorder=1)
        ax.add_patch(pathpatch)
        slope = 1/3
        if rotate:
            point1_y = x_start + 0.03*BT
            point1_x = y_start + 0.03*BT*slope
            points = [(y_start, x_start), (point1_x, point1_y)]
        else:
            point1_x = x_start + 0.03*D 
            point1_y = y_start + 0.03*D*slope
            points = [(x_start, y_start), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='pink', linewidth=1.5, zorder=1)
        ax.add_patch(pathpatch)


    def plot_bars_shear_single(self, ax, emb, reinf_shear, reinf_vertical_As, D, B, BT, H1, H2, rotate=False):
        """ plots single stirrup
        """
        idx_x_start = int(emb.split()[0]) - 1
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_x = (B - 2*dia)/(n-1) # spacing b/w bars in mm
            x_start = (BT-B)/2 + idx_x_start*delta_x
        else:
            dia = float(reinf_vertical_As['dia'])
            delta_x = (B - dia)/(n-1) # spacing b/w bars in mm
            x_start = (BT-B)/2 + idx_x_start*delta_x

        if rotate:
            point1 = (H1, x_start)
            point2 = (D-H2, x_start)
            vertices = np.array([point1, point2], float)
        else:
            point1 = (x_start, H1)
            point2 = (x_start, D-H2)
            vertices = np.array([point1, point2], float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='red', linewidth=2, zorder=1)
        ax.add_patch(pathpatch)
        text = '{0}mm@{1:.0f}cm, {2:.0f} legs'.format(reinf_shear['dia'], reinf_shear['spacing'], reinf_shear['n_legs'])
        if rotate:
            (x_not, y_not) = (D*1/5, x_start)
            rotation_text = 0
        else:
            (x_not, y_not) = (x_start, D*1/5)
            rotation_text = 90
        ax.annotate(text, xy=(x_not, y_not), xycoords='data', color='red', weight='bold', zorder=10,
                        xytext= ((x_not + 0.1*D), y_not - 0.1*D), arrowprops=dict(arrowstyle = "->", ec="red"), rotation=rotation_text, fontsize=8)

        # knots
        slope = 1/3
        if rotate:
            point1_y = x_start + 0.05*BT
            point1_x = H1 + 0.05*BT*slope
            points = [(H1, x_start), (point1_x, point1_y)]
        else:
            point1_x = x_start + 0.05*D 
            point1_y = H1 + 0.05*D*slope
            points = [(x_start, H1), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='red', linewidth=2, zorder=1)
        ax.add_patch(pathpatch)

        slope = 1/3
        if rotate:
            point1_y = x_start + 0.05*BT
            point1_x = D - H2 - 0.05*BT*slope
            points = [(D-H2, x_start), (point1_x, point1_y)]
        else:
            point1_x = x_start + 0.05*D 
            point1_y = D - H2 - 0.05*D*slope
            points = [(x_start, D-H2), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='red', linewidth=2, zorder=1)
        ax.add_patch(pathpatch)


    def plot_bars_shear_single_additional(self, ax, emb, reinf_shear, reinf_vertical_As, D, B, BT, H1, H2, rotate=False):
        """ plots single stirrup
        """
        idx_y_start = int(emb.split()[0]) - 1
        n = int(reinf_vertical_As['n'])
        if 'D' in reinf_vertical_As['dia']:
            dia = float(reinf_vertical_As['dia'][1:])
            delta_y = (D - H1 - H2 - 2*dia)/(n + 2 -1) # spacing b/w bars in mm
            x_start = (BT-B)/2 
            y_start = H1 + idx_y_start*delta_y
        else:
            dia = float(reinf_vertical_As['dia'])
            delta_y = (D - H1 - H2 - dia)/(n + 2 -1) # spacing b/w bars in mm
            x_start = (BT-B)/2 
            y_start = H1 + idx_y_start*delta_y

        if rotate:
            point1 = (y_start, x_start)
            point2 = (y_start, x_start+B)
            vertices = np.array([point1, point2], float)
        else:
            point1 = (x_start, y_start)
            point2 = (x_start+B, y_start)
            vertices = np.array([point1, point2], float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='pink', linewidth=1.5, zorder=100)
        ax.add_patch(pathpatch)
        text = '{0}mm@{1:.0f}cm, {2:.0f} legs'.format(reinf_shear['dia'], reinf_shear['spacing'], reinf_shear['n_legs'])
        if rotate:
            (x_not, y_not) = (y_start, x_start + BT*1/2)
            rotation_text = 90.0
        else:
            (x_not, y_not) = (x_start + BT*1/2, y_start)
            rotation_text = 0.0

        ax.annotate(text, xy=(x_not, y_not), xycoords='data', color='pink', weight='bold', zorder=10,
                            xytext= (x_not + 0.1*D, y_not + 0.1*D), arrowprops=dict(arrowstyle = "->", ec="pink"), rotation=rotation_text, fontsize=8)

        # knots
        slope = 3/1
        if rotate:
            point1_y = x_start + 0.03*D 
            point1_x = y_start + 0.03*D*slope
            points = [(y_start, x_start), (point1_x, point1_y)]
        else:
            point1_x = x_start + 0.03*D 
            point1_y = y_start + 0.03*D*slope
            points = [(x_start, y_start), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='pink', linewidth=1.5, zorder=1)
        ax.add_patch(pathpatch)
        
        slope = 3/1
        if rotate:
            point1_y = x_start + B - 0.03*D 
            point1_x = y_start + 0.03*D*slope
            points = [(y_start, x_start + B), (point1_x, point1_y)]
        else:
            point1_x = x_start + B - 0.03*D 
            point1_y = y_start + 0.03*D*slope
            points = [(x_start + B, y_start), (point1_x, point1_y)]
        vertices = np.array(points, float)
        codes = [Path.MOVETO] + [Path.LINETO]
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='none', alpha=1.0, edgecolor='pink', linewidth=1.5, zorder=1)
        ax.add_patch(pathpatch)


    def plot_wall_output(self, y, dat, A, index=0, clear=True, staggered_reinf=None):
        """ Plots wall internal forces
        """
        if clear:
            self.axes[index].cla()
        self.axes[index].grid(which='both')
        self.axes[index].plot(dat*A, y)
        if index==0:
            self.axes[index].set_xlabel('N [kN]')
        elif index==1:
            self.axes[index].set_xlabel('M [kNm]')
            if staggered_reinf:
                if 'M_max' in staggered_reinf[0]:
                    self.plot_wall_output_M_staggered(index, A, staggered_reinf, quantity='M_max')
        elif index==2:
            self.axes[index].set_xlabel('Q [kN]')
            if staggered_reinf:
                if 'Q_max' in staggered_reinf[0]:
                    self.plot_wall_output_M_staggered(index, A, staggered_reinf, quantity='Q_max')

        self.axes[index].autoscale_view()
        self.draw()


    def plot_wall_output_M_staggered(self, index, A, staggered_reinf, quantity='M_max'):
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

            self.plot_reinf_staggering(y_top, y_bottom, M_max*A, index, value_upper=M_max_upper*A, annotation=annotation, linewidth=1.5)
            self.plot_reinf_staggering(y_top, y_bottom, -M_max*A, index, value_upper=M_max_upper*A, annotation=annotation_sym, linewidth=1.5)   # symmetric line

            if i == 0: # first (top) segment
                self.plot_reinf_staggering(y_top, y_bottom, M_max*A, index, segment='first', linewidth=1.5)
                self.plot_reinf_staggering(y_top, y_bottom, -M_max*A, index, segment='first', linewidth=1.5)   # symmetric line

            if i==(len(staggered_reinf) - 1): # last (bottom) segment
                self.plot_reinf_staggering(y_top, y_bottom, M_max*A, index, segment='last', linewidth=1.5)
                self.plot_reinf_staggering(y_top, y_bottom, -M_max*A, index, segment='last', linewidth=1.5)   # symmetric line


    def plot_reinf(self, y, dat, should_plot_envelop=False, negative=False, index=0, clear=True):
        """ Plots reinforcement areas
        """
        if clear:
            self.axes[index].cla()
        self.axes[index].grid(which='both')
        if should_plot_envelop:
            if not negative:
                self.axes[index].plot(np.amax(dat, axis=1), y)
            else:
                self.axes[index].plot(np.amin(dat, axis=1), y) # max of negative float (for A_s2)
        else:
            self.axes[index].plot(dat, y)
        if index==0:
            self.axes[index].set_xlabel('A_s [$\mathregular{cm^2}$]')
        elif index==1:
            self.axes[index].set_xlabel('a_s [$\mathregular{cm^2/m}$]')

        #if np.max(dat) > 0.0:
        #    self.axes[index].set_xlim(0, np.max(dat)*1.2)
#
        self.axes[index].autoscale_view()
        self.draw()
    

    def plot_reinf_staggering(self, y_top, y_bottom, value, index, segment='inbetween', value_upper=0.0, annotation='', linewidth=2):
        """ Plots the staggered reinforcement defined by user
        segment = 'first', 'last', 'inbetween'
        """
        self.axes[index].plot((value, value), (y_top, y_bottom), color='black', linewidth=linewidth)
        bbox_props = dict(boxstyle="square,pad=0.2", fc="white", ec="b", lw=2, alpha=0.8)
        if value>0:
            self.axes[index].text(value + value*0.1, y_top - (y_top - y_bottom)/2, annotation, ha='left', va='center', size=9, bbox=bbox_props, rotation=90)
        else:
            self.axes[index].text(value + value*0.15, y_top - (y_top - y_bottom)/2, annotation, ha='left', va='center', size=9, bbox=bbox_props, rotation=90)
        #self.axes[index].annotate(annotation, (value, y_top - (y_top - y_bottom)/2), rotation=90)
        if segment=='first': # horizontal bar
            self.axes[index].plot((0, value), (y_top, y_top), color='black', linestyle='--', linewidth=linewidth)
        elif segment=='last': # horizontal bar
            self.axes[index].plot((0, value), (y_bottom, y_bottom), color='black', linestyle='--', linewidth=linewidth)
        elif segment=='inbetween':
            self.axes[index].plot((value_upper, value), (y_top, y_top), color='black', linestyle='--', linewidth=linewidth)
        self.axes[index].autoscale_view()
        self.draw()



    def plot_improved_soil_factor(self, level, factor, key, index=0, clear=True):
        """ Plots improved soil factors along levels
        """
        if clear:
            self.axes[index].cla()
        if index==0:
            self.axes[index].set_ylabel('Level [mNN]')
        self.axes[index].grid(which='both')
        self.axes[index].plot(factor, level)
        self.axes[index].set_xlabel(key)
        self.axes[index].autoscale_view()  
        self.draw()



class MyStaticMplCanvasSubplots(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, nrows=1, ncols=4):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = None
        self.gs = gridspec.GridSpec(nrows, ncols)
        
        FigureCanvas.__init__(self, self.fig)
        #super(MyStaticMplCanvasSubplots, self).__init__(self.fig)
        
        #FigureCanvas.setSizePolicy(self,
        #                           QtWidgets.QSizePolicy.Expanding,
        #                           QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
    

    def add_subplot(self, nrow, ncol, index, sharedaxis=None):
        #if sharedaxis is None:
        #    #self.axes = self.fig.add_subplot(nrow, ncol, index, sharex=None, sharey=None)
        #    #self.axes = self.fig.add_subplot(nrow, ncol, index, sharex='all', sharey='all')
        #elif sharedaxis == 2:
        #    self.axes = self.fig.add_subplot(nrow, ncol, index, sharex=True, sharey=True)

        self.axes = self.fig.add_subplot(nrow, ncol, index, sharex=None, sharey=None)


    def add_subplot_varied_widths(self, gridindex):
        self.axes = self.fig.add_subplot(self.gs[0,gridindex[0]:gridindex[1]])
        

    def plot_metamodel_validation_WallUx(self, nx, ny, wall_ux_metamodel, wall_ux_FEmodel, y_plate):
        """ Plots wall deflection comparisons betwen metamodel and FE model
        """
        for plotindex in range(nx * ny):
            #self.add_subplot(nx, ny, plotindex + 1, sharex='all', sharey='all')
            #self.add_subplot(nx, ny, plotindex + 1, True, True)
            if plotindex < len(wall_ux_FEmodel):
                self.add_subplot(nx, ny, plotindex + 1)
                self.axes.plot(wall_ux_metamodel[plotindex, :len(y_plate)], y_plate, 'b-', label='metamodel')
                self.axes.plot(wall_ux_FEmodel[plotindex, :len(y_plate)], y_plate, 'r--', label='FE model')
                self.axes.legend()
                self.axes.set_title(str(plotindex))


    def plot_metamodel_prediction_WallUx(self, plotindex, plottitle, wall_ux_metamodel, y_plate):
        """ Plots wall deflection comparisons betwen metamodel and FE model
        """
        self.add_subplot(2, 3, plotindex)
        self.axes.cla()
        ux = list(1000*wall_ux_metamodel.flatten())
        self.axes.plot(ux, y_plate, 'b-')
        self.axes.set_xlabel('deflection [mm]')
        self.axes.set_ylabel('wall level [m]')
        self.axes.set_title(plottitle)
        self.draw()


    def plot_wall_output_empty(self, nx, ny, plotindex, holdon = False, add_subplot=True):        
        """ Plots empty wall outputs
        """
        if add_subplot:
            self.add_subplot(nx, ny, plotindex)
        if not holdon:
            self.axes.cla()
        self.draw()


    def plot_wall_output(self, y_coord, value, nx, ny, plotindex, xlabel, ylabel = None, color = 'blue', annotate_min = True, annotate_max = True, holdon = False, add_subplot=True):        
        if add_subplot:
            self.add_subplot(nx, ny, plotindex)
        if not holdon:
            self.axes.cla()
        
        self.axes.fill_betweenx(y_coord, np.array(value), 0, hatch = '-', facecolor = color)
        
        self.axes.set_xlabel(xlabel)
        if ylabel is not None:
            self.axes.set_ylabel(ylabel)
        
        value_min = round(min(value), 1)
        value_max = round(max(value), 1)
        if annotate_min:            
            self.axes.axvline(value_min, color='black', linestyle='--')
        
        if annotate_max:
            self.axes.axvline(value_max, color='black', linestyle='--')
        
        self.axes.set_xticks(ticks=[value_min, value_max])
        plt.setp(self.axes.get_xticklabels(), rotation=0, horizontalalignment='center')
        
        self.axes.autoscale_view()
        self.draw()
        

    def plot_table(self, cell_text, colors, columns, rows, colWidths=None, loc='center', fontsize=9):
        """ Plots table only
        """
        self.axes.cla()
        self.axes.set_axis_off()
        the_table = self.axes.table(cellText=cell_text, cellColours=colors, colLabels=columns, rowLabels=rows, colWidths=colWidths, loc=loc, edges='open')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(fontsize)
        the_table.scale(0.4, 1.2)
        self.draw()

    def plot_wall_output_envelop(self, y_coord, value_emax, value_emin, nx, ny, plotindex, xlabel, ylabel=None, add_subplot=True):        
        if add_subplot:
            self.add_subplot(nx, ny, plotindex)
        
        self.axes.cla()
        
        self.axes.fill_betweenx(y_coord, np.array(value_emax), 0, hatch = '-', facecolor = 'yellow')
        self.axes.fill_betweenx(y_coord, np.array(value_emin), 0, hatch = '-', facecolor = 'orange')
        
        self.axes.set_xlabel(xlabel)
        if ylabel is not None:
            self.axes.set_ylabel(ylabel)
        
        value_min = round(min(value_emin), 1)
        value_max = round(max(value_emax), 1)
                   
        self.axes.axvline(value_min, color='black', linestyle='--')
        
        self.axes.axvline(value_max, color='black', linestyle='--')
        
        self.axes.set_xticks(ticks=[value_min, value_max])
        plt.setp(self.axes.get_xticklabels(), rotation=0, horizontalalignment='center')
        
        self.axes.autoscale_view()
        self.draw()


    def plot_wall_output_envelope_extreme_values_text(self, y_plate, minmax_values_at_min_M2D, minmax_values_at_max_M2D, minmax_values_at_min_Q2D, minmax_values_at_max_Q2D, nx, ny, plotindex, xlabel, ylabel = None):
        """ Displays internal forces at min/max bending moments and shear forces
        """
        self.add_subplot(nx, ny, plotindex)
        
        self.axes.cla()

        #y = minmax_values_at_min_M2D['y_at_min_M2D']
        y = min(y_plate) + 0*(max(y_plate) - min(y_plate))/3.5
        s = list(str(key) + '=' + '{:.2f}'.format(value) for key, value in minmax_values_at_min_M2D.items())
        self.axes.text(0, y, '{0}, {1}, {2}, {3}'.format(s[0], s[1], s[2], s[3]), fontsize='small')

        #y = minmax_values_at_max_M2D['y_at_max_M2D']
        y = min(y_plate) + 1*(max(y_plate) - min(y_plate))/3.5
        s = list(str(key) + '=' + '{:.2f}'.format(value) for key, value in minmax_values_at_max_M2D.items())
        self.axes.text(0, y, '{0}, {1}, {2}, {3}'.format(s[0], s[1], s[2], s[3]), fontsize='small')

        #y = minmax_values_at_min_Q2D['y_at_min_Q2D']
        y = min(y_plate) + 2*(max(y_plate) - min(y_plate))/3.5
        s = list(str(key) + '=' + '{:.2f}'.format(value) for key, value in minmax_values_at_min_Q2D.items())
        self.axes.text(0, y, '{0}, {1}, {2}, {3}'.format(s[0], s[1], s[2], s[3]), fontsize='small')

        #y = minmax_values_at_max_Q2D['y_at_max_Q2D']
        y = min(y_plate) + 3*(max(y_plate) - min(y_plate))/3.5
        s = list(str(key) + '=' + '{:.2f}'.format(value) for key, value in minmax_values_at_max_Q2D.items())
        self.axes.text(0, y, '{0}, {1}, {2}, {3}'.format(s[0], s[1], s[2], s[3]), fontsize='small')

        self.axes.set_ylim(min(y_plate), max(y_plate))
        self.axes.autoscale_view()
        self.draw()


    def plot_wall_output_points(self, y_coord, value, gridindex, xlabel, ylabel = None, color = 'blue', annotate_min = True, annotate_max = True, holdon = False):        
        """ Plots wall output at a few designated points
        """
        self.add_subplot_varied_widths(gridindex)

        if not holdon:
            self.axes.cla()
        
        self.axes.fill_betweenx(y_coord, np.array(value), 0, hatch = '-', facecolor = color, zorder=0)
        
        self.axes.set_xlabel(xlabel)
        if ylabel is not None:
            self.axes.set_ylabel(ylabel)
        
        value_min = min(value)
        value_max = max(value)
        if annotate_min:            
            self.axes.axvline(value_min, color='black', linestyle='--')
        
        if annotate_max:
            self.axes.axvline(value_max, color='black', linestyle='--')
        
        self.axes.set_xticks(ticks=[value_min, value_max])
        plt.setp(self.axes.get_xticklabels(), rotation=0, horizontalalignment='center')
        
        self.axes.autoscale_view()
        self.draw() 


    def plot_wall_output_scattered_points(self, y_coord, value, gridindex, color='black', holdon=False):
        """ Plots defection points
        """
        self.add_subplot_varied_widths(gridindex)

        if not holdon:
            self.axes.cla()

        self.axes.scatter(value, y_coord, c=color, s=6, zorder=1)
        self.axes.autoscale_view()
        self.draw() 


    def clear_plot_scalar(self, gridindex, x_max, y_max):
        """ Clears canvas
        """
        self.add_subplot_varied_widths(gridindex)
        self.axes.cla()
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.axes.set_xlim(0, x_max)
        self.axes.set_ylim(0, y_max)
        self.axes.autoscale_view()
        self.draw() 


    def plot_scalar_value(self, x, y, gridindex, xlabel = 'Iteration number', ylabel = 'Objective value'):
        """ Plot scalar value objective value during backanalysis
        """
        self.add_subplot_varied_widths(gridindex)
        self.axes.scatter(x, y, c='black', s=10)
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.autoscale_view()
        self.draw()


    def plot_soilsection_settlement(self, x_coord, y_coord, value, scaling_factor, vicinity, xlabel, ylabel = None):        
        self.add_subplot(1,1,1)
        
        self.axes.cla()
        
        
        #self.axes.fill_between(np.array(x_coord), np.array(y_coord) + scaling_factor*np.array(value), np.array(y_coord), hatch = '|', facecolor = 'blue')
        self.axes.fill_between(np.array(x_coord), np.array(value), 0, hatch = '|', facecolor = 'blue')
        
        self.axes.set_xlabel(xlabel)
        if ylabel is not None:
            self.axes.set_ylabel(ylabel)
        
        value_min = min(np.array(value))
        value_max = max(np.array(value))
        self.axes.axhline(value_min, color='black', linestyle='--')        
        self.axes.axhline(value_max, color='black', linestyle='--')        
        self.axes.set_yticks(ticks=[value_min, value_max])
                  
#        self.axes.axhline(value_min, color='black', linestyle='--')        
#        self.axes.axhline(value_max, color='black', linestyle='--')        
#        self.axes.set_yticks(ticks=[value_min, value_max], labels=[value_min/scaling_factor, value_max/scaling_factor])

#        plt.setp(self.axes.get_xticklabels(), rotation=0, horizontalalignment='center')
        
        self.axes.autoscale_view()
        self.draw()
        

#class MyStaticMplCanvas_Event(FigureCanvas):
#    def __init__(self, parent=None, width=5, height=4, dpi=100):
#        #self.fig = Figure(figsize=(width, height), dpi=dpi)
#        self.fig = plt.figure()
#        self.axes = self.fig.add_subplot(111)
#        FigureCanvas.__init__(self, self.fig)
#        #super().__init__(self.fig)
#        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
#        #self.axes.figure.canvas.mpl_connect('pick_event', self.on_pick)
#
#    def plot_objectives_2d(self, displs, costs, iter_number=None, color='red', clear_axis=True, marker='o', alpha=0.3):
#        """ Plots objective values
#        """
#        # clear canvas for every new plot
#        if clear_axis:
#            self.axes.cla()
#
#        self.axes.scatter(displs, costs, color=color, marker=marker, alpha=alpha)
#
#        self.axes.set_xlabel('f_1(x)')  # displacement
#        self.axes.set_ylabel('f_2(x)')  # cost
#        if iter_number:
#            self.axes.set_title('Generation xx' + str(iter_number))
#        if clear_axis:
#            #self.axes.set_xlim(np.min(displs) - 1.0e-4, np.max(displs) + 1.0e-4)
#            self.axes.set_xlim(np.min(displs) - 1, np.max(displs) + 1)
#            self.axes.set_ylim(np.min(costs) - 1.0 , np.max(costs) + 1.0)
#
#        #self.fig.canvas.mpl_connect('pick_event', self.on_pick)
#        #self.axes.figure.canvas.mpl_connect('pick_event', self.on_pick)
#        self.draw()
#
#
#    @pyqtSlot()
#    def on_pick(self,  event):
#        thisline = event.artist
#        xdata = thisline.get_xdata()
#        ydata = thisline.get_ydata()
#        ind = event.ind
#        print('Point %d is picked' % ind)
#        print('X = ', np.take(xdata, ind)[0]) # Print X point
#        print('Y = ', np.take(ydata, ind)[0]) # Print Y point


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)

        #FigureCanvas.__init__(self, self.fig)
        #self.setParent(parent)
        super(MyMplCanvas, self).__init__(self.fig)
        
        self.axes.autoscale(True, tight=True)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas for static plots.
    """
    def plot_objectives_2d(self, displs, costs, iter_number=None, color='red', clear_axis=True, marker='o', alpha=0.3, picker_size=0.0, plaxman_ap=None, solutions=None, 
                            variables_wall=None, variables_anchors=None, variables_struts=None, variables_stone_columns=None, variables_fdc=None):
        """ Plots objective values
        """
        displs = np.array(displs)*1000  # (mm)
        costs = np.array(costs)*0.001   # thousand euros
        # clear canvas for every new plot
        if clear_axis:
            self.axes.cla()

        if picker_size > 2.0:
            self.axes.plot(displs, costs, 'o', color=color, marker=marker, alpha=alpha, picker=picker_size, label='gen. ' + str(iter_number))
            self.cid = self.fig.canvas.mpl_connect('pick_event', lambda event : self.on_pick(event)) # OK
            #self.axes.figure.canvas.mpl_connect('pick_event', self.on_pick) # OK
            self.plaxman_ap = plaxman_ap
        else:
            self.axes.plot(displs, costs, 'o', color=color, marker=marker, alpha=alpha, label='gen. ' + str(iter_number)) # no picker (avoid repeated calls to slot())

        self.solutions = solutions
        self.variables_wall = variables_wall
        self.variables_anchors = variables_anchors
        self.variables_struts = variables_struts
        self.variables_stone_columns = variables_stone_columns
        self.variables_fdc = variables_fdc

        #self.axes.set_xlabel('Displacement (mm)')  # displacement
        self.axes.set_xlabel('Settlement (mm)')  # displacement
        self.axes.set_ylabel('Cost (1000 EURO)')  # cost
        self.axes.legend()
        if clear_axis:
            self.axes.set_title('Generation ' + str(iter_number))
            epsilon_x = 0.05*np.max(np.abs(displs))
            epsilon_y = 0.05*np.max(np.abs(costs))
            self.axes.set_xlim(np.min(displs) - epsilon_x, np.max(displs) + epsilon_x)
            self.axes.set_ylim(np.min(costs) - epsilon_y , np.max(costs) + epsilon_y)

        #self.axes.autoscale(True, tight=True)
        #self.axes.autoscale_view()  
        self.draw()


    @pyqtSlot()
    def on_pick(self,  event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        print('Solution {0} is picked: Cost = {1} (EUR); displacement = {2} (mm)'.format(ind[0], np.take(ydata, ind)[0], np.take(xdata, ind)[0]))
        #print('x = {0}, y = {1}'.format(np.take(xdata, ind)[0], np.take(ydata, ind)[0])) # Print point (x, y)

        # update model using Automated phases
        #if self.plaxman_ap is not None:
        if hasattr(self, 'plaxman_ap'):
            # update design variables to model
            v = self.solutions[ind[0], :].flatten()
            print('Design variables: ', v)
            if self.variables_stone_columns:    # stone columns
                self.plaxman_ap.assign_design_variables_to_model_sc(v, self.variables_stone_columns)

            elif self.variables_fdc:    # rigid inclusions
                self.plaxman_ap.assign_design_variables_to_model_fdc(v, self.variables_fdc)

            else: # retaining wall
                self.plaxman_ap.assign_design_variables_to_model(v, self.variables_wall, self.variables_anchors, self.variables_struts)
                # regenerate calculation phases
                self.plaxman_ap.setup_automated_phases_porepressure_interpolation__()


    @pyqtSlot()
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


    def plot_sensitivity_scores(self, scores, phase_number=None):
        """ Plots sensitivity scores
        """
        # clear canvas for every new plot
        self.axes.cla()

        #scores_normalized = 100.0 * scores / np.linalg.norm(scores)
        scores_normalized = 100.0 * scores / np.sum(scores)
        self.axes.set_xlabel('Parameter')
        self.axes.set_ylabel('Sensitivity scores [%]')

        # plot bars
        for i in range(scores_normalized.size):
            self.axes.bar(i, scores_normalized[i], width=0.2, color='b')
            self.axes.text(i - 0.1, scores_normalized[i] + 2, '%.1f' % scores_normalized[i])
        
        # xlabels
        self.axes.set_xticks(range(scores_normalized.size))
        xticklabels = ['m' + str(i) for i in range(1, scores_normalized.size + 1)]
        self.axes.set_xticklabels(xticklabels)

        # title
        if phase_number:
            self.axes.set_title('Phase ' + str(phase_number))
        else:
            self.axes.set_title('All phases')

        #self.axes.autoscale_view(enable=True, axis='both', tight=True)  
        self.axes.autoscale_view()  
        self.draw()

    def plot_sensitivity_scores_optiman(self, scores, objective_name=None):
        """ Plots sensitivity scores for Optiman
        """
        # clear canvas for every new plot
        self.axes.cla()

        #scores_normalized = 100.0 * scores / np.linalg.norm(scores)
        scores_normalized = 100.0 * scores / np.sum(scores)
        self.axes.set_xlabel('Design variables')
        self.axes.set_ylabel('Sensitivity scores [%]')

        # plot bars
        for i in range(scores_normalized.size):
            self.axes.bar(i, scores_normalized[i], width=0.2, color='b')
            self.axes.text(i - 0.1, scores_normalized[i] + 2, '%.1f' % scores_normalized[i])
        
        # xlabels
        self.axes.set_xticks(range(scores_normalized.size))
        xticklabels = ['v' + str(i) for i in range(1, scores_normalized.size + 1)]
        self.axes.set_xticklabels(xticklabels)

        # title
        if objective_name:
            self.axes.set_title(str(objective_name))
        else:
            self.axes.set_title('Max WallUx')

        self.axes.autoscale_view()  
        self.draw()

    def plot_geometry(self, geometry):
        """ Plot geometry
        """
        x_min = geometry[0]
        y_min = geometry[1]
        x_max = geometry[2]
        y_max = geometry[3]
        #points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (0,0)]
        #codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        codes = [Path.MOVETO] + [Path.LINETO]*2 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        #pathpatch = PathPatch(path, facecolor='grey', alpha=0.3, edgecolor='green')
        pathpatch = PathPatch(path, facecolor='None', alpha=0.3, edgecolor='None')
                
        self.axes.cla()
        #self.axes.arrow(0, 0, abs(y_max - y_min)*0.1, 0, color='red',  head_width=abs(y_max - y_min)*0.03, head_length=abs(y_max - y_min)*0.05, overhang = 0.2, length_includes_head=True)
        #self.axes.arrow(0, 0, 0, abs(y_max - y_min)*0.1, color='green', head_width=abs(y_max - y_min)*0.03, head_length=abs(y_max - y_min)*0.05, overhang = 0.2, length_includes_head=True)
        self.axes.add_patch(pathpatch)
        self.axes.autoscale_view()
                
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_aspect('equal')
        self.draw()
        

    def plot_borehole(self, num_boreholes, borehole, geometry, plot_waterlevel=True):
        """ Plot a borehole
        """
        x = borehole['x']
        Head = borehole['Head']
        x_min, y_min, x_max, y_max = geometry
        
        points = [(x, y_min), (x, y_max)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        pathpatch1 = PathPatch(path, facecolor='None', alpha=1.0, edgecolor='orange', linewidth=1.5)
        self.axes.add_patch(pathpatch1)
        

        points = [(x, Head), (x, y_min)]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        pathpatch2 = PathPatch(path, facecolor='None', alpha=1.0, edgecolor='blue', linestyle='-', linewidth=1.5)
        self.axes.add_patch(pathpatch2)
        
        points = [(x_min - 2 , Head), (x_max + 2, Head)]
        points += [(x_max -8, Head - 0.5), (x_max, Head - 0.5)]
        points += [(x_max -6, Head - 1), (x_max-2, Head - 1)]
        codes = codes*3
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        if plot_waterlevel is True:
            pathpatch3 = PathPatch(path, facecolor='None', alpha=1.0, edgecolor='deepskyblue', linestyle='-', linewidth=1.0)
            self.axes.add_patch(pathpatch3)
            annotation_water = self.axes.annotate('WL {0:.2f}'.format(Head), (x_max - 5, Head), xycoords='data', xytext=((x_max - 4, Head + 2)), 
                                arrowprops=dict(arrowstyle = "wedge", ec="dimgrey"), color='deepskyblue', fontsize=10)
        else:   # used for CMC rigid inclusions
            pathpatch3 = None
            annotation_water = None
        
        annotation = self.axes.annotate(borehole['name'], (x, y_min))

        # set top and bottom of view
        y_additional = (y_max - y_min)*0.1  # for showing line loads and point loads
        self.axes.set_ylim(bottom=y_min)  # use set_ylim() because ymin is at zero when autoscale_view() or autoscale() is used
        self.axes.set_ylim(top=y_max + y_additional)  # use set_ylim() because ymin is at zero when autoscale_view() or autoscale() is used
        #self.axes.relim(visible_only=True)
        #self.axes.autoscale_view()  
        self.draw()
        
        return (pathpatch1, pathpatch2, pathpatch3, annotation, annotation_water) # pathpatch return for removing a borehole plot object when undoing 'add borehole'
        
        
    def plot_layer(self, Boreholes, NUMBER_layer, x_min, x_max):
        Boreholes_sorted = sorted(Boreholes, key=lambda borehole: borehole['x'])    # sort boreholes in increasing x coordinates    
        #x_coords = [x_min, [borehole['x'] for borehole in Boreholes_sorted], x_max]
        #x_coords = [element for item in x_coords for element in item] # flattened list
        
        points_top = [(x_min, Boreholes_sorted[0]['Top'][NUMBER_layer])]
        points_bottom = [(x_min, Boreholes_sorted[0]['Bottom'][NUMBER_layer])]
        codes = [Path.MOVETO]
        
        for borehole in Boreholes_sorted:
            points_top.append((borehole['x'], borehole['Top'][NUMBER_layer]))
            points_bottom.append((borehole['x'], borehole['Bottom'][NUMBER_layer]))
            codes.append(Path.LINETO)
            
        points_top.append((x_max, Boreholes_sorted[-1]['Top'][NUMBER_layer]))
        points_bottom.append((x_max, Boreholes_sorted[-1]['Bottom'][NUMBER_layer]))
        codes.append(Path.LINETO)
        
        vertices_top = np.array(points_top, float)
        vertices_bottom = np.array(points_bottom, float)
        
        path_top = Path(vertices_top, codes)
        path_bottom = Path(vertices_bottom, codes)
        
        # save layer polygons
        vertices_polygon = np.concatenate((vertices_top, vertices_bottom[::-1], np.array([[0, 0]])), axis = 0)
        codes_polygon = codes + [codes[-1]]*len(codes) + [Path.CLOSEPOLY]
        path_polygon = Path(vertices_polygon, codes_polygon)
        
        pathpatch_top = PathPatch(path_top, facecolor='None', alpha=1.0, edgecolor='black', linestyle='-', linewidth=1.0)
        pathpatch_bottom = PathPatch(path_bottom, facecolor='None', alpha=1.0, edgecolor='black', linestyle='-', linewidth=1.0)

        # annotate top of layer
        layer_top = Boreholes_sorted[0]['Top'][NUMBER_layer]
        text = '{0:.2f}'.format(layer_top)

        annotation = self.axes.annotate(text, xy=(x_max-5, layer_top), xycoords='data', color="black", weight="bold",
                                 xytext=((x_max-4, layer_top+2)), arrowprops=dict(arrowstyle = "wedge", ec="dimgrey"), fontsize=10)

        self.axes.add_patch(pathpatch_top)
        self.axes.add_patch(pathpatch_bottom)

        # recompute data limits based on current artists
        self.axes.relim(visible_only=True)
        self.axes.autoscale_view()    
        self.draw()
        
        return (path_polygon, pathpatch_top, pathpatch_bottom, annotation)

        
    def plot_FDC(self, FDC_params, top_of_soil):
        """ Plots FDC rigid inclusions element
        """
        top = FDC_params['top']
        Dc = FDC_params['Dc']
        Lc = FDC_params['Lc']
        point_TL = (-Dc/2, top)
        point_TR = (Dc/2, top)
        point_BR = (Dc/2, top - Lc)
        point_BL = (-Dc/2, top - Lc)

        points = [point_TL, point_TR, point_BR, point_BL, (0, 0)]
        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black', facecolor='black', alpha=0.8)
        self.axes.add_patch(pathpatch)  

        self.axes.set_aspect('equal')
        self.axes.set_xlim(-3*Dc, 3*Dc)
        self.axes.set_ylim(top - Lc - Lc*0.2, top_of_soil)
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch)


    def plot_LTP(self, LTP, FDC_params):
        """ Plots FDC rigid inclusions element
        """
        hM = LTP['hM']
        top = FDC_params['top']
        Dc = FDC_params['Dc']
        Lc = FDC_params['Lc']
        point_TL = (-3*Dc, top + hM)
        point_TR = (3*Dc, top + hM)
        point_BR = (3*Dc, top)
        point_BL = (-3*Dc, top)

        points = [point_TL, point_TR, point_BR, point_BL, (0, 0)]
        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black', facecolor='yellow', alpha=0.8)
        self.axes.add_patch(pathpatch)  

        self.axes.set_aspect('equal')
        self.axes.set_xlim(-3*Dc, 3*Dc)
        self.axes.set_ylim(top - Lc - Lc*0.2, top + hM)
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch)


    def plot_q_p_Rd_vs_hM(self, h, q_p_Rd, hMi, q_p_Rdi):
        """ Plots allowable stress in LTP q_p_Rd vs LTP thickness
        """
        self.axes.cla()
        self.axes.scatter(h, q_p_Rd)
        self.axes.plot(h, q_p_Rd)
        self.axes.scatter(hMi, q_p_Rdi, color='red')
        self.axes.set_xlabel('LTP thickness hM [m]')
        self.axes.set_ylabel('Allowable stress in LTP q_p_Rd [kPa]')
        self.draw()


    def plot_q_p_Rd_vs_hM_Menard(self, points):
        """ Plots allowable stress in LTP q_p_Rd vs LTP thickness
        """
        points_x = [point[0] for point in points]
        points_y = [point[1] for point in points]
        self.axes.cla()
        self.axes.plot(points_x, points_y)
        self.axes.scatter(points_x[1], points_y[1], color='red') # hM, q_p_Rd
        self.axes.set_xlabel('LTP thickness hM [m]')
        self.axes.set_ylabel('Allowable stress in LTP q_p_Rd [kPa]')
        self.draw()


    def plot_FDC_and_soil_settlement(self, z, u_z_c, u_z_s, u_z_s_unreinf, z_below_FDC, u_z_s_below_FDC, show_u_s_unreinf):
        """
        """
        self.axes.cla()
        self.axes.plot(u_z_c, z, color='blue', label='column')
        self.axes.plot(u_z_s, z, color='red', label='soil')
        self.axes.plot(np.zeros(z.size), z, '-.', color='black')   # 0-line
        if show_u_s_unreinf:
            self.axes.plot(u_z_s_below_FDC, z_below_FDC, color='green')
            self.axes.plot(u_z_s_unreinf, z, color='green', label='unreinforced')
        self.axes.legend()
        self.axes.set_ylim(z_below_FDC[-1], z[0])    # revert y-axis
        self.axes.set_ylabel('Column depth [m]')
        self.axes.set_xlabel('Settlement [mm]')
        self.axes.grid(which='both')
        self.draw()


    def plot_FDC_and_soil_vertical_force(self, z, Q_fdc, Q_soil):
        """
        """
        self.axes.cla()
        self.axes.plot(Q_fdc, z, color='blue', label='vertical column force')
        self.axes.plot(Q_soil, z, color='red', label='vertical soil force')
        self.axes.plot(np.zeros(z.size), z, '-.', color='black')   # 0-line
        self.axes.legend()
        self.axes.set_ylim(z[-1], z[0])    # revert y-axis
        self.axes.set_ylabel('Column depth [m]')
        self.axes.set_xlabel('Force [kN]')
        self.axes.grid(which='both')
        self.draw()


    def plot_FDC_skin_resistance(self, z, f_s_mobilized, f_s_max):
        """
        """
        self.axes.cla()
        self.axes.plot(f_s_mobilized, z, color='blue', label='f_s mobilized')
        self.axes.plot(f_s_max, z, '--', color='red', label='f_s maximal')
        self.axes.plot(np.zeros(z.size), z, '-.', color='black')   # 0-line
        self.axes.legend()
        self.axes.set_ylim(z[-1], z[0])    # revert y-axis
        self.axes.set_ylabel('Column depth [m]')
        self.axes.set_xlabel('Skin resistance [kPa]')
        self.axes.grid(which='both')
        self.draw()


    def plot_assigned_layer(self, path_polygon, color):
        pathpatch_layer = PathPatch(path_polygon, facecolor=color, alpha=1.0, edgecolor='black', linewidth=1.0, zorder = 0)
        self.axes.add_patch(pathpatch_layer)

        #self.axes.relim(visible_only=True)
        #self.axes.autoscale_view()
        self.draw()
        
        return pathpatch_layer


    def undo_plot_pathpatches(self, pathpatches):        
        if isinstance(pathpatches, Iterable): 
            [pathpatch_i.set_visible(False) for pathpatch_i in pathpatches if pathpatch_i is not None]
            #[pathpatch_i.remove() for pathpatch_i in pathpatches]
        
        else: # for a single pathpatch object
            pathpatches.set_visible(False)
            #pathpatches.remove()

        del pathpatches
            
        # recompute data limits based on current artists
        self.axes.relim(visible_only=True)

        self.axes.autoscale_view()
        self.draw()
        
    def set_grey_pathpatches(self, pathpatches):
        if isinstance(pathpatches, Iterable): 
            [pathpatch_i.set_color('grey') for pathpatch_i in pathpatches if pathpatch_i is not None]
        
        else: # for a single pathpatch object
            pathpatches.set_color('grey')
            
        self.axes.autoscale_view()
        self.draw()

    def set_color(self, pathpatches, color):
        if isinstance(pathpatches, Iterable):
            [pathpatch_i.set_color(color) for pathpatch_i in pathpatches if pathpatch_i is not None]
        
        else: # for a single pathpatch object
            if pathpatches is not None:
                pathpatches.set_color(color)
                #pathpatches.set_facecolor(color)
            
        self.axes.autoscale_view()
        self.draw()


    def set_color_excavated_soilcluster(self, pathpatches, color='white'):
        if isinstance(pathpatches, Iterable):
            [pathpatch_i.set_color(color) for pathpatch_i in pathpatches[:-2] if pathpatch_i is not None]   # last 2 pathpatch items are annotation
            #[pathpatch_i.set_hatch('/') for pathpatch_i in pathpatches if pathpatch_i is not None]
            [pathpatch_i.set_alpha(None) for pathpatch_i in pathpatches[:-2] if pathpatch_i is not None]    # last 2 pathpatch items are annotation
        
        else: # for a single pathpatch object
            if pathpatches is not None:
                pathpatches.set_color(color)
                #pathpatches.set_hatch('/')
                pathpatches.set_alpha(None)
            
        self.axes.autoscale_view()
        self.draw()
    

    def set_colors(self, pathpatches, colors):
        #try: 
        #    [pathpatch_i.set_color(color) for pathpatch_i in pathpatches for color in colors if pathpatch_i is not None]
        
        #except TypeError: # for a single pathpatch object
        #    pathpatches.set_color(colors)
        #    #self.axes.add_patch(pathpatches)
        if isinstance(pathpatches, Iterable):
            [pathpatch_i.set_color(color) for pathpatch_i in pathpatches for color in colors if ((pathpatch_i is not None) and color is not None)]

        else:
            pathpatches.set_color(colors)
            
        self.axes.autoscale_view()
        self.draw()


    def set_colors2(self, pathpatches, colors):
        try: 
            #[pathpatch_i.set_color(color) for pathpatch_i in pathpatches for color in colors if pathpatch_i is not None]
            for i, pathpatch_i in enumerate(pathpatches):
                    if pathpatch_i is not None:
                        color = colors[i]
                        #pathpatch_i.set_facecolor(color)
                        pathpatch_i.set_facecolor('red')
        
        except TypeError: # for a single pathpatch object
            pathpatches.set_color(colors)
            #self.axes.add_patch(pathpatches)

        #from collections.abc import Iterable
        
        #if isinstance(pathpatches, Iterable):
        #    for i, pathpatch_i in enumerate(pathpatches):
        #        if pathpatch_i is not None:
        #            color = colors[i]
        #            #pathpatch_i.set_facecolor(color)
        #            pathpatch_i.set_facecolor('red')
        #            pathpatch_i.set_edgecolor('red')
        #else:
        #    #pathpatches.set_color(colors)
        #    pathpatches.set_facecolor('red')
        #    pathpatches.set_edgecolor('red')

            
        self.axes.autoscale_view()
        self.draw()


    def plot_stone_columns_cross_section(self, D, a, shape='triangle'):
        self.axes.cla()
        if shape == 'triangle':
            circle1_path = Circle((0.0, 0.0), radius=D/2)
            circle2_path = Circle((a, 0.0), radius=D/2)
            circle3_path = Circle((a/2, a*np.cos(30*np.pi/180)), radius=D/2)
            self.axes.add_patch(circle1_path)
            self.axes.add_patch(circle2_path)
            self.axes.add_patch(circle3_path)
        elif shape == 'rectangle':
            circle1_path = Circle((0.0, 0.0), radius=D/2)
            circle2_path = Circle((a, 0.0), radius=D/2)
            circle3_path = Circle((a, a), radius=D/2)
            circle4_path = Circle((0.0, a), radius=D/2)
            self.axes.add_patch(circle1_path)
            self.axes.add_patch(circle2_path)
            self.axes.add_patch(circle3_path)
            self.axes.add_patch(circle4_path)
        
        #self.axes.axvline(D/2, color='black', linestyle='--')
        #self.axes.axvline(S+D/2 , color='black', linestyle='--')
        #self.axes.axvline(2*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()


    def plot_dwall_cross_section(self, d):
        self.axes.cla()
        length = 3.0
        points = [(0, 0), (length, 0), (length, d), (0, d), (0,0)]
        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path)
        self.axes.add_patch(pathpatch)  
        self.axes.axvline(1, color='black', linestyle='--')
        self.axes.axvline(2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        

    def plot_SPW_cross_section(self, D, S, SPW131=False):
        """ Plots secant pile wall"""
        if not SPW131:
            self.plot_SPW111_cross_section(D, S)
        else:
            self.plot_SPW131_cross_section(D, S)


    def plot_SPW131_cross_section(self, D, S):
        self.axes.cla()
        circle1_path = Circle((D/2,D/2), radius=D/2)        # first secondary pile
        circle2_path = Circle((4*S+D/2,D/2), radius=D/2)    # second secondary pile

        circle3_path = Circle((1*S+D/2,D/2), radius=D/2)    # first primary pile
        circle4_path = Circle((2*S+D/2,D/2), radius=D/2)    # second primary pile
        circle5_path = Circle((3*S+D/2,D/2), radius=D/2)    # third primary pile

        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle2_path)
        self.axes.add_patch(circle3_path)
        self.axes.add_patch(circle4_path)
        self.axes.add_patch(circle5_path)
        D_inner = D - D/4   # to represent reinforcement cage
        circle1_path = Circle((D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        circle2_path = Circle((4*S+D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle2_path)
        
        self.axes.axvline(D/2, color='black', linestyle='--')
        self.axes.axvline(S+D/2 , color='black', linestyle='--')
        self.axes.axvline(2*S+D/2 , color='black', linestyle='--')
        self.axes.axvline(3*S+D/2, color='black', linestyle='--')
        self.axes.axvline(4*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()


    def plot_SPW111_cross_section(self, D, S):
        self.axes.cla()
        circle1_path = Circle((D/2,D/2), radius=D/2)
        circle2_path = Circle((S+D/2,D/2), radius=D/2)
        circle3_path = Circle((2*S+D/2,D/2), radius=D/2)
        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle2_path)
        self.axes.add_patch(circle3_path)
        D_inner = D - D/4
        circle1_path = Circle((D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        circle3_path = Circle((2*S+D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle3_path)
        
        self.axes.axvline(D/2, color='black', linestyle='--')
        self.axes.axvline(S+D/2 , color='black', linestyle='--')
        self.axes.axvline(2*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        
    def plot_CPW_cross_section(self, D, S):
        self.axes.cla()
        circle1_path = Circle((D/2,D/2), radius=D/2)
        circle2_path = Circle((S+D/2,D/2), radius=D/2)
        circle3_path = Circle((2*S+D/2,D/2), radius=D/2)
        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle2_path)
        self.axes.add_patch(circle3_path)
        D_inner = D - D/4
        circle1_path = Circle((D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        circle2_path = Circle((S + D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        circle3_path = Circle((2*S+D/2,D/2), radius=D_inner/2, facecolor=None, edgecolor='black', linestyle='--', linewidth=2)
        self.axes.add_patch(circle1_path)
        self.axes.add_patch(circle2_path)
        self.axes.add_patch(circle3_path)
        
        self.axes.axvline(D/2, color='black', linestyle='--')
        self.axes.axvline(S+D/2 , color='black', linestyle='--')
        self.axes.axvline(2*S+D/2, color='black', linestyle='--')
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
    
    def plot_Steeltube_cross_section(self, d_outer, d_inner):
        self.axes.cla()
        
        circle_outer_path = Circle((d_outer/2, d_outer/2), radius=d_outer/2, edgecolor='black')
        circle_inner_path = Circle((d_outer/2, d_outer/2), radius=d_inner/2, facecolor='white', edgecolor='black')
        self.axes.add_patch(circle_outer_path)
        self.axes.add_patch(circle_inner_path)
         
        self.axes.axvline(0, color='black', linestyle='--')
        self.axes.axvline((d_outer - d_inner)/2, color='black', linestyle='--')

        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        
    def plot_RCstrut_cross_section(self, width, height):
        self.axes.cla()
        
        points = [(0, 0), (width, 0), (width, height), (0, height), (0,0)]
        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black')
        self.axes.add_patch(pathpatch)  

        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        
    def plot_RCslab_cross_section(self, thickness):
        self.axes.cla()
        
        points = [(0, 0), (6, 0), (6, thickness), (0, thickness), (0,0)]
        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black')
        self.axes.add_patch(pathpatch)  

        self.axes.axvline(0, color='black', linestyle='--')
        self.axes.axvline(6 , color='black', linestyle='--')
        
        self.axes.set_aspect('equal')
        self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        
    
    def plot_point(self, point, color = 'black'):
        x = point[0]
        y = point[1]
        pointpatch = Circle((x, y), radius=0.3, color=color)
        self.axes.add_patch(pointpatch)
        
        self.axes.autoscale_view()  
        self.draw()
        
        return pointpatch
    
    def plot_points(self, points, color = 'black'):
        """ Plot multiple points
        """
        pointpatches = []
        for point in points:
            x = point[0]
            y = point[1]
            pointpatch = Circle((x, y), radius=0.1, color=color, zorder=20)
            self.axes.add_patch(pointpatch)
            pointpatches.append(pointpatch)
        
        self.axes.autoscale_view()  
        self.draw()
        
        return pointpatches
        
    def plot_wall(self, new_wall, colors):
        point1_x = new_wall['point1'][0]
        point1_y = new_wall['point1'][1]
        point2_x = new_wall['point2'][0]
        point2_y = new_wall['point2'][1]
        pos_interface = new_wall['interf_pos']
        neg_interface = new_wall['interf_neg']
        
        points = [(point1_x, point1_y), (point2_x, point2_y)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)

        # place steel profile wall on the foreground
        zorder = 10
        if new_wall['wall_type'] == 'Steel profile H/U':
            zorder = 20
        
        # wall as rectangular to display wall thickness
        wall_thickness = new_wall['wall_thickness']
        wall_height = abs(points[1][1] - points[0][1])
        wall_base_point = list(points[1])
        wall_base_point[0] -= wall_thickness/2
        wall_pathpatch = Rectangle(wall_base_point, wall_thickness, wall_height, facecolor=colors[0], edgecolor=colors[0], alpha=1.0, linewidth=4, zorder=zorder)
        self.axes.add_patch(wall_pathpatch)
        
        pos_interface_pathpatch = None
        neg_interface_pathpatch = None
        
        # interfaces
        delta = wall_thickness/4
        #delta = 0.5
        if pos_interface is True:
            if abs(point2_y - point1_y) < 1.e-4: # horizontal plate
                points = [(point1_x, point1_y + delta), (point2_x, point2_y + delta)]
            else:
                points = [(point1_x + wall_thickness/2 + delta, point1_y), (point2_x + wall_thickness/2 + delta, point2_y)]
            vertices = np.array(points, float)
            path = Path(vertices, codes)            
            pos_interface_pathpatch = PathPatch(path, facecolor=colors[1], alpha=1.0, edgecolor=colors[1], linewidth=1, zorder=zorder)
            self.axes.add_patch(pos_interface_pathpatch)
        if neg_interface is True:
            if abs(point2_y - point1_y) < 1.e-4: # horizontal plate
                points = [(point1_x, point1_y - delta), (point2_x, point2_y - delta)]
            else:
                points = [(point1_x - wall_thickness/2 - delta, point1_y), (point2_x - wall_thickness/2 - delta, point2_y)]
            vertices = np.array(points, float)
            path = Path(vertices, codes)            
            neg_interface_pathpatch = PathPatch(path, facecolor=colors[2], alpha=1.0, edgecolor=colors[2], linewidth=1, zorder=zorder)
            self.axes.add_patch(neg_interface_pathpatch)

        # annotation text for wall
        text = 'Base {0:.3f}\nLength {1:.2f}m'.format(point2_y, point1_y-point2_y)
        if new_wall['wall_type'] in ['Dwall', 'MIP']:
            text += '\n{0} thickness {1:.2f} m'.format(new_wall['wall_type'], new_wall['wall_thickness'])
        elif new_wall['wall_type'] in ['SPW', 'CPW']: # piled wall
            if new_wall['SPW131']:
                text += '\nPiled wall 1:3:1, D {0:.2f}m, S {1:.2f}m'.format(new_wall['wall_thickness'], new_wall['spacing'])
            else:
                text += '\nPiled wall, D {0:.2f}m, S {1:.2f}m'.format(new_wall['wall_thickness'], new_wall['spacing'])
        else: # profile
            profile = read_data_in_json_item(new_wall['json_item'], 'MaterialName')     # profile name
            profile_nos = new_wall['profile_nos']   # number of steel profiles
            text += '\n{0} x {1}, spacing {2} m'.format(profile_nos, profile, new_wall['spacing'])
        annotation = self.axes.annotate(text, xy=(point2_x, point2_y), xycoords='data', color="white", weight="bold",
                                 xytext=((point2_x + 4, point2_y - 5)), arrowprops=dict(arrowstyle = "->", ec="dimgrey"), fontsize=8)

        self.axes.autoscale_view()
        self.draw()
        
        return (wall_pathpatch, pos_interface_pathpatch, neg_interface_pathpatch, annotation)
    

    def plot_multilinear_skin_resistance(self, distance, resistance):
        self.axes.cla()      
        points = [(distance[i], resistance[i]) for i in range(len(distance))]               
        codes = [Path.MOVETO] + [Path.LINETO]*(len(distance) - 1)   
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor='black', linewidth=1)
        self.axes.add_patch(pathpatch)
        for i in range(len(distance)):
            self.axes.axvline(distance[i], color='black', linestyle='--', linewidth=0.5)
            self.axes.axhline(resistance[i], color='black', linestyle='--', linewidth=0.5)
        #self.axes.set_xlabel('Distance [m]')
        self.axes.set_ylabel('Resistance [kN/m]')
        #self.axes.set_axis_off()
        self.axes.autoscale_view()
        self.draw()
        

    def plot_multilinear_earth_pressure_wedge(self, points):
        codes = [Path.MOVETO] + [Path.LINETO]*(len(points) - 1)   
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor='grey', linewidth=1, linestyle='-.')
        self.axes.add_patch(pathpatch)
        self.axes.autoscale_view()
        self.draw()

        return pathpatch


    def plot_ground_anchor(self, anchor):
        
        point1_x = anchor['position'][0]
        point1_y = anchor['position'][1]
        
        angle = anchor['angle']
        length_free = anchor['length_free']
        length_fixed = anchor['length_fixed']
        
        x1 = np.cos(angle*np.pi/180) * length_free
        y1 = np.tan(angle*np.pi/180) * x1
        point2_x = point1_x + x1
        point2_y = point1_y + y1
                   
        x2 = np.cos(angle*np.pi/180) * (length_free + length_fixed)
        y2 = np.tan(angle*np.pi/180) * x2
        point3_x = point1_x + x2
        point3_y = point1_y + y2
        
        points = [(point1_x, point1_y), (point2_x, point2_y)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        freelength_pathpatch = PathPatch(path, facecolor='black', alpha=1.0, edgecolor='black', linewidth=1.5)
        self.axes.add_patch(freelength_pathpatch) 
        
        points = [(point2_x, point2_y), (point3_x, point3_y)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        
        fixedlength_pathpatch = PathPatch(path, facecolor='magenta', alpha=1.0, edgecolor='magenta', linewidth=2.5)
        self.axes.add_patch(fixedlength_pathpatch)                   
        
        text = 'H {0:.1f} A {1:.1f}\N{DEGREE SIGN} FL {2:.1f}m GL {3:.1f}m Lspacing {4:.2f}m F_prestress {5:.1f}kN'.format(point1_y, angle, length_free, length_fixed, anchor['Lspacing'], anchor['F_prestress'])
        annotation = self.axes.annotate(text, xy = (point1_x, point1_y), xycoords='data', color="white", weight="bold",
                           #xytext= ((point1_x + 1, point1_y)), arrowprops=dict(arrowstyle = "->", ec="dimgrey"), rotation=angle, fontsize=8)
                           #xytext= ((point1_x + 1, point1_y)), rotation=angle, fontsize=8)
                           #xytext= ((point1_x + 1, point1_y)), rotation=0, fontsize=8)
                           xytext= ((point1_x + 2, point1_y)), arrowprops=dict(arrowstyle = "->", ec="dimgrey"), rotation=0, fontsize=8)
                           
        self.axes.autoscale_view()  
        self.draw()
        
        return (freelength_pathpatch, fixedlength_pathpatch, annotation)

    
    def plot_strut(self, strut, y_min=-30, y_max=10):
        point1_x = strut['position'][0]
        point1_y = strut['position'][1]
        direct_x = strut['direct_x']
        direct_y = strut['direct_y']
        
        strut_color = 'black'
        if strut['usage'] == 'Slab':
            strut_color = 'orange'
        
        length = np.sqrt(direct_x**2 + direct_y**2)
        point2_x = point1_x + direct_x/length * abs(y_max - y_min)*0.1
        point2_y = point1_y + direct_y/length * abs(y_max - y_min)*0.1
        
            
        points = [(point1_x, point1_y), (point2_x, point2_y)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        longditudinal_pathpatch = PathPatch(path, facecolor=strut_color, alpha=1.0, edgecolor=strut_color, linewidth=2, zorder=100)
        
        # perpendicular line
        if abs(point2_y - point1_y) > 1.e-4:
            slope = -(point2_x - point1_x)/(point2_y - point1_y)
            b = point2_y - slope*point2_x      
            point3_x = point2_x + np.cos(np.arctan(slope)) * abs(y_max - y_min)*0.03
            point4_x = point2_x - np.cos(np.arctan(slope)) * abs(y_max - y_min)*0.03
            point3_y = slope*point3_x + b
            point4_y = slope*point4_x + b
        else:
            point3_x = point2_x
            point4_x = point2_x
            point3_y = point2_y +  abs(y_max - y_min)*0.03
            point4_y = point2_y - abs(y_max - y_min)*0.03
            
        points = [(point3_x, point3_y), (point4_x, point4_y)]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        transversal_pathpatch = PathPatch(path, facecolor=strut_color, alpha=1.0, edgecolor=strut_color, linewidth=2, zorder=100)
                
        self.axes.add_patch(longditudinal_pathpatch)
        self.axes.add_patch(transversal_pathpatch)
        
        text = 'H {0:.2f} Lspacing {1:.2f}m'.format(point1_y, strut['Lspacing'])
        annotation = self.axes.annotate(text, xy = (point1_x, point1_y), xycoords='data', color="white", weight="bold",
                           xytext= ((point1_x + abs(y_max - y_min)*0.08, point1_y)), arrowprops=dict(arrowstyle = "->", ec="dimgrey"), fontsize=8)
        
        self.axes.autoscale_view()  
        self.draw()
        
        return (longditudinal_pathpatch, transversal_pathpatch, annotation)

    
    def plot_lineload(self, lineload, y_min, y_max):
        points_bottom = [(lineload['point1'][0], lineload['point1'][1]), (lineload['point2'][0], lineload['point2'][1])]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points_bottom, float)
        path = Path(vertices, codes)
        bottom_pathpatch = PathPatch(path, color='blue', linewidth=1)
        
        length = np.sqrt(lineload['qx']**2 + lineload['qy']**2)
        dx = lineload['qx']/length * abs(y_max - y_min)*0.1
        dy = lineload['qy']/length * abs(y_max - y_min)*0.1
        point1_top_x = lineload['point1'][0] - dx
        point1_top_y = lineload['point1'][1] - dy
        point2_top_x = lineload['point2'][0] - dx
        point2_top_y = lineload['point2'][1] - dy
        
        points_top = [(point1_top_x, point1_top_y), (point2_top_x, point2_top_y)]
        vertices = np.array(points_top, float)
        path = Path(vertices, codes)
        top_pathpatch = PathPatch(path, facecolor='blue', alpha=1.0, edgecolor='blue', linewidth=1)
        
        arrow1_pathpatch = Arrow(point1_top_x, point1_top_y, dx, dy, color='blue', linewidth=1)
        arrow2_pathpatch = Arrow(point2_top_x, point2_top_y, dx, dy, color='blue', linewidth=1)

        # hatch pathpatch
        hatch_pathpatch = Polygon(points_bottom + points_top[::-1], closed=True, fill=False, hatch='|', edgecolor='blue', linewidth=0.5)
        
        self.axes.add_patch(bottom_pathpatch)
        self.axes.add_patch(top_pathpatch)
        self.axes.add_patch(arrow1_pathpatch)
        self.axes.add_patch(arrow2_pathpatch)
        self.axes.add_patch(hatch_pathpatch)
        
        # annotate with lineload magnitude
        annotation = self.axes.annotate('{0:.2f} [kN/m/m]'.format(lineload['qy']), 
                                        xy=(point1_top_x, point1_top_y), xycoords='data', color="black", 
                                        xytext=(point1_top_x, point1_top_y-0.1*dy))

        self.axes.autoscale_view()  
        self.draw()
        
        return (bottom_pathpatch, top_pathpatch, arrow1_pathpatch, arrow2_pathpatch, hatch_pathpatch, annotation)
    

    def plot_pointload(self, pointload, y_min, y_max):
        point_bottom = pointload['point']
        length = np.sqrt(pointload['Fx']**2 + pointload['Fy']**2)
        dx = pointload['Fx']/length * abs(y_max - y_min)*0.15
        dy = pointload['Fy']/length * abs(y_max - y_min)*0.15
        point_top_x = point_bottom[0] - dx
        point_top_y = point_bottom[1] - dy
        arrow_pathpatch = Arrow(point_top_x, point_top_y,  dx,  dy, facecolor='blue', alpha=1.0, edgecolor='blue', linewidth=1)

        # annotate with pointload magnitude
        annotation = self.axes.annotate('{0:.2f} [kN/m]'.format(pointload['Fy']), 
                                        xy=(point_top_x, point_top_y), xycoords='data', color="black", 
                                        xytext=(point_top_x, point_top_y-0.1*dy))
        
        self.axes.add_patch(arrow_pathpatch)
        self.axes.autoscale_view()  
        self.draw()
        
        return (arrow_pathpatch, annotation)
    

    def plot_soilcluster(self, soilcluster, wall_thickness=0.0, annotate=True, annotate_FEL=False):
        """ Plots a soil cluster, wall thickness when larger than 0 is considered to represent the actual thickness of the wall
        """
        if wall_thickness > 0.0:
            pointTR_x = soilcluster['pointTR'][0] - wall_thickness/2
            pointBR_x = soilcluster['pointBR'][0] - wall_thickness/2
        else:
            pointTR_x = soilcluster['pointTR'][0]
            pointBR_x = soilcluster['pointBR'][0]
        points = [(soilcluster['pointTL'][0], soilcluster['pointTL'][1]), (pointTR_x, soilcluster['pointTR'][1]), 
                  (pointBR_x, soilcluster['pointBR'][1]), (soilcluster['pointBL'][0], soilcluster['pointBL'][1]), (0,0)]

        codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black', facecolor='black', alpha=0.3)
        self.axes.add_patch(pathpatch)  

        # annotate with excavation level (bottom of soilcluster)
        points_EL = [(soilcluster['pointBR'][0], soilcluster['pointBR'][1]), (soilcluster['pointBL'][0], soilcluster['pointBL'][1])]
        codes_EL = [Path.MOVETO] + [Path.LINETO]
        vertices_EL = np.array(points_EL, float)
        path_EL = Path(vertices_EL, codes_EL)
        if annotate:
            if annotate_FEL:
                annotation = self.axes.annotate('FEL {0:.3f}'.format(soilcluster['pointBL'][1]), (soilcluster['pointBL'][0], soilcluster['pointBL'][1]))
            else:
                annotation = self.axes.annotate('EL {0:.3f}'.format(soilcluster['pointBL'][1]), (soilcluster['pointBL'][0], soilcluster['pointBL'][1]))
            annotation_EL = PathPatch(path_EL, edgecolor='black', alpha=1.0, linewidth=0.5, linestyle='--', zorder=100)
            self.axes.add_patch(annotation_EL)
        else:
            annotation = None
            annotation_EL = None

        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch, annotation_EL, annotation)

    
    def plot_soilcluster_points(self, soilcluster, wall_thickness=0.0, berm_base=False, berm_top=False, annotate=False):
        """ plots with dummy (None) annotations
         wall thickness when larger than 0 is considered to represent the actual thickness of the wall
        """
        points = copy.deepcopy(soilcluster['points'])

        if wall_thickness > 0:
            if berm_base:
                x_max = max([p[0] for p in points])
                for point in points:
                    if point[0] == x_max:
                        point[0] -= wall_thickness/2

            #elif berm_top:
            #    x_min = min([p[0] for p in points[2:]])
            #    for point in points:
            #        if point[0] == x_min:
            #            point[0] += wall_thickness/2

        points.append((0,0))
        codes = [Path.MOVETO] + [Path.LINETO]*(len(points)-2) + [Path.CLOSEPOLY]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='black', facecolor='black', alpha=0.3, zorder=10)    # zorder is needed for proper display
        self.axes.add_patch(pathpatch)  

        if annotate:
            x_min = min([p[0] for p in points[:-1]])
            y_min = min([p[1] for p in points[:-1]])
            index_y_min = [p[1] for p in points].index(y_min)
            annotation = self.axes.annotate('FEL {0:.3f}'.format(y_min), (x_min, y_min), zorder=100)
        else:
            annotation = None

        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch, None, annotation)

    
    def plot_polygon(self, points_in, color):
        points = []
        codes = [Path.MOVETO]        
        for (i, point) in enumerate(points_in):
            points.append(point)
            codes.append(Path.LINETO)       
        points.append((0,0))
        codes.pop()
        codes.append(Path.CLOSEPOLY)
        
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor = color, edgecolor = 'black', alpha=1.0, zorder = 0)
        self.axes.add_patch(pathpatch)  
        
        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return pathpatch

        
    def plot_waterlevel(self, waterlevel, color='blue'):
        """ Plot user water level
        """
        points = [(waterlevel['pointL'][0], waterlevel['pointL'][1]), (waterlevel['pointR'][0], waterlevel['pointR'][1])]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor=color, facecolor=color, alpha=1.0, linewidth=1.5, zorder=100)
        self.axes.add_patch(pathpatch)  

        annotation = self.axes.annotate('WL {0:.3f}'.format(waterlevel['pointR'][1]), (waterlevel['pointL'][0], waterlevel['pointR'][1]-2.0), 
                                        color='deepskyblue', zorder=100)

        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch, annotation)


    def plot_final_excavation_level(self, level, x_min, x_wall):
        """ Plots final excavation level
        """
        points = [(x_min, level), (x_wall, level)]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, edgecolor='red', facecolor='red', alpha=1.0, linewidth=2.0)
        self.axes.add_patch(pathpatch)  

        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return pathpatch

    
    def plot_drain(self, drain):
        """ Plot drain
        """
        wall_length = drain['wall_length']
        points = [(drain['pointL'][0], drain['pointL'][1]), (drain['pointR'][0], drain['pointR'][1])]
        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = np.array(points, float)
        path = Path(vertices, codes)
        pathpatch_drain = PathPatch(path, edgecolor='cyan', facecolor='cyan', alpha=1.0, linewidth=2.5)
        self.axes.add_patch(pathpatch_drain)  

        delta_x = wall_length/20
        
        if drain['islefthalfmodel'] is False:
            points = [(drain['wallfoot'][0], drain['wallfoot'][1]), (drain['pointR'][0], drain['pointR'][1])]
            points_pos = [(drain['wallfoot'][0] + delta_x, drain['wallfoot'][1]), (drain['pointR'][0] + delta_x, drain['pointR'][1])]
            points_neg = [(drain['wallfoot'][0] - delta_x, drain['wallfoot'][1]), (drain['pointR'][0] - delta_x, drain['pointR'][1])]
        else:
            points = [(drain['wallfoot'][0], drain['wallfoot'][1]), (drain['pointL'][0], drain['pointL'][1])]
            points_pos = [(drain['wallfoot'][0] + delta_x, drain['wallfoot'][1]), (drain['pointL'][0] + delta_x, drain['pointL'][1])]
            points_neg = [(drain['wallfoot'][0] - delta_x, drain['wallfoot'][1]), (drain['pointL'][0] - delta_x, drain['pointL'][1])]
        vertices = np.array(points, float)
        path = Path(vertices, codes)            
        interface_pathpatch = PathPatch(path)
        self.axes.add_patch(interface_pathpatch)
        
        vertices = np.array(points_pos, float)
        path = Path(vertices, codes)            
        pos_pathpatch = PathPatch(path, facecolor='green', alpha=1.0, edgecolor='green', linewidth=1)
        self.axes.add_patch(pos_pathpatch)
        
        vertices = np.array(points_neg, float)
        path = Path(vertices, codes)            
        neg_pathpatch = PathPatch(path, facecolor='green', alpha=1.0, edgecolor='green', linewidth=1)
        self.axes.add_patch(neg_pathpatch)
                             
                     
        self.axes.set_aspect('equal')
        self.axes.autoscale_view()
        self.draw()
        
        return (pathpatch_drain, interface_pathpatch, pos_pathpatch, neg_pathpatch)
    

    def plot_image_from_file(self, filename):
        """ Plots the image from file
        """
        img = mpimg.imread(filename)
        self.axes.imshow(img)
        self.draw()


    def plot_table(self, cell_text, colors, columns, rows, colWidths=None, loc='center', fontsize=9):
        """ Plots table only
        """
        self.axes.set_axis_off()
        the_table = self.axes.table(cellText=cell_text, cellColours=colors, colLabels=columns, rowLabels=rows, colWidths=colWidths, loc=loc)
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(fontsize)
        the_table.scale(1, 1.6)
        self.draw()


    def plot_curve(self, points, xlabel='Step number [-]', ylabel='FoS [-]'):
        """ Plots a curve
        """
        self.axes.plot(points)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
