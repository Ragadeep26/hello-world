# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 21:11:29 2020

@author: nya
"""
import os
import sys
import json
from collections import OrderedDict
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Circle, Arrow
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from gui.gui_main_matplotlib import MyStaticMplCanvas
from gui.gui_main_matplotlib import MyStaticMplCanvasSubplots
from common.boilerplate import start_plaxis
from plxscripting.easy import new_server
from solver.plaxis2d.output_commands import get_msf_points, get_plate_outputs, get_all_anchors_force, get_all_struts_force
from solver.plaxis2d.parameter_relations import get_Eref_Dwall, get_Eref_CPW, get_Eref_SPW

# for testing
from matplotlib.backends.backend_pdf import PdfPages
import subprocess
#MONIMAN = r'D:\Data\3Packages\Moniman' # for debugging

class Report(FigureCanvas):
    """ This class uses matplotlib for creating A4 pdf report
    """
    cm = 1/2.54

    def __init__(self, parent=None, width=42, height=29.7, dpi=300):
        self.fig = Figure(figsize=(width*Report.cm, height*Report.cm), facecolor='w', dpi=dpi)
        #self.fig = Figure(figsize=(42*Report.cm, 29.7*Report.cm), facecolor='w', dpi=dpi)
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
        MONIMAN = sys.modules['moniman_paths']['MONIMAN']
        COMMON = os.path.join(MONIMAN, 'common')

        # Frame layout - rect(lower left point coordinates, width, height, rotation angle)
        #rect = Rectangle((2.85*Report.cm, 2.7*Report.cm),16.45*Report.cm,24.7*Report.cm,linewidth=0.5,edgecolor='k',facecolor='none')
        rect = Rectangle((2.85*Report.cm, 2.7*Report.cm), 36.3*Report.cm, 24.3*Report.cm, linewidth=0.5, edgecolor='k', facecolor='none')
        self.axes.add_patch(rect)
        # BAUER logo
        bauer_logo = mpimg.imread(os.path.join(COMMON, 'logo.png'))
        imagebox = OffsetImage(bauer_logo, zoom=0.25)
        #anno_box = AnnotationBbox(imagebox, (18.2*Report.cm, 26.2*Report.cm), frameon=False)
        anno_box = AnnotationBbox(imagebox, (37.9*Report.cm, 25.8*Report.cm), frameon=False)
        self.axes.add_artist(anno_box)

        #height = [24.95,24.90,24.10,22.2,4.00]
        heights = [24.55, 24.50]
        # drawing the lines that make up the horizontal lines
        for height in heights:
            #self.axes.plot([2.85*Report.cm, 19.3*Report.cm],[height*Report.cm, height*Report.cm],linewidth=0.5,color='k')
            self.axes.plot([2.85*Report.cm, 39.15*Report.cm], [height*Report.cm, height*Report.cm], linewidth=0.5, color='k')
        # middle vertical line
        #self.axes.plot([12.2*Report.cm, 12.2*Report.cm],[24.10*Report.cm, 22.2*Report.cm],linewidth=0.5,color='k')
        #columns = [2.95, 6.60, 12.30, 15.45]

        self.axes.tick_params(axis='both', which='both', bottom=False, left=False, labelbottom=False, labelleft=False)


    def add_project_info(self, project_properties):
        """ Adds project information for pile wall
        """
        project_title = project_properties['project_title']
        self.axes.text(3*Report.cm, 26.5*Report.cm, 'Project: {} '.format(project_title), fontsize=9, fontweight='bold', va='center')


    def add_table_soil_stratigraphy(self, Layer_polygons, Boreholes):
        """ Adds table for soil stratigraphy
        """
        # frame information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Soil stratigraphy', fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # plot table soil stratigraphy
        self.plot_table_soil_stratigraphy(canvas, Layer_polygons, Boreholes)


    def add_table_soil_materials(self, Layer_polygons):
        """ Adds table for soil materials
        """
        # frame information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Soil materials', fontsize=9, fontweight='bold', va='center')

        # create canvas
        #ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.65])
        #canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        ax1 = self.axes.figure.add_axes([0.165, 0.1, 0.7, 0.8])
        canvas = MyStaticMplCanvas(width=0.7, height=0.8)
        canvas.axes = ax1

        # plot table soil stratigraphy
        self.plot_table_soil_materials(canvas, Layer_polygons)


    def add_table_soil_materials_permeability(self, Layer_polygons):
        """ Adds table for soil permeabilites
        """
        # frame information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Soil permeabilites', fontsize=9, fontweight='bold', va='center')

        # create canvas
        #ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.65])
        #canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        ax1 = self.axes.figure.add_axes([0.165, 0.1, 0.7, 0.8])
        canvas = MyStaticMplCanvas(width=0.7, height=0.8)
        canvas.axes = ax1

        # plot table soil stratigraphy
        self.plot_table_soil_materials_permeability(canvas, Layer_polygons)


    def add_table_wall_material(self, wall):
        """ Adds table for soil materials
        """
        # frame information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Material properties for wall', fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.165, 0.1, 0.7, 0.8])
        canvas = MyStaticMplCanvas(width=0.7, height=0.8)
        canvas.axes = ax1

        # plot table soil stratigraphy
        self.plot_table_wall_material(canvas, wall)


    def add_table_anchor_strut_forces_at_phase(self, p, g_o, num_phase, path_output, Anchors, Struts, Phases):
        """ Adds table for soil materials
        """
        # frame information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Anchor forces/ strut forces'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        #ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.65])
        #canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        ax1 = self.axes.figure.add_axes([0.165, 0.1, 0.7, 0.8])
        canvas = MyStaticMplCanvas(width=0.7, height=0.8)
        canvas.axes = ax1

        # plot table soil stratigraphy
        self.plot_table_anchor_strut_forces_at_phase(canvas, p, g_o, num_phase+1, path_output, Anchors, Struts)
        self.add_additional_phase_information(Phases[num_phase])


    def add_model_at_phase(self, geometry, Boreholes, Layer_polygons, Walls, Anchors, Struts, Lineloads, Pointloads, Polygons,
                           Soilclusters, Waterlevels, Phases, num_phase):
        """ Adds model states at a phase
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Model view'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # plot model
        self.plot_model(canvas, geometry, Boreholes, Layer_polygons, Walls, Anchors, Struts, Lineloads, Pointloads, Polygons,
                        Soilclusters, Waterlevels)

        # plot model at the phase
        self.initialize_pathpatches_for_phase(canvas, Lineloads, Pointloads, Anchors, Struts, Walls)
        for i_phase in range(num_phase+1):
            self.plot_model_at_phase(canvas, Phases[i_phase], Lineloads, Pointloads, Walls, Soilclusters, Anchors, Struts)
        self.add_additional_phase_information(Phases[num_phase])


    def add_structure_at_phase(self, p, g_o, path_output, Phases, num_phase, Walls, Anchors, Struts):
        """ Adds structure outputs at a phase
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Wall outputs'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        #ax1 = self.axes.figure.add_axes([0.15, 0.2, 0.65, 0.55])
        #self.fig.set_figwidth(36.3*Report.cm)
        #self.fig.set_figheight(24.3*Report.cm)
        #axes = self.fig.add_subplot(2, 4, 1)
        canvas = MyStaticMplCanvasSubplots(width=1, height=1, dpi=100, nrows=5, ncols=6)
        #canvas.axes = axes

        # plot wall outputs
        x_wall = Walls[0]['point1'][0]
        self.plot_wall_outputs_at_phase(canvas, p, g_o, num_phase+1, path_output, x_wall, Walls[0], Anchors, Struts)
        self.add_additional_phase_information(Phases[num_phase])


    def add_field_data_at_phase(self, p, g_o, path_output, num_phase, Phases):
        """ Adds field data at phase
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Total displacement'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # export data
        self.export_field_data_at_phase(canvas, p, g_o, path_output, num_phase+1)
        self.add_additional_phase_information(Phases[num_phase])


    def add_field_data_at_phase_dewatering(self, p, g_o, path_output, num_phase, Phases):
        """ Adds active water pressure field data at phase dewatering
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Active pore pressure'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # export data
        self.export_field_data_at_phase(canvas, p, g_o, path_output, num_phase+1, dewatering_phase=True)
        self.add_additional_phase_information(Phases[num_phase])


    def add_field_data_at_phase_FoS(self, p, g_o, path_output, num_phase, Phases):
        """ Adds principle incremental deviatoric strain field data at phase FoS
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Failure slip plane(s)'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # export data
        self.export_field_data_at_phase(canvas, p, g_o, path_output, num_phase+1, FoS_phase=True)
        self.add_additional_phase_information(Phases[num_phase])



    def add_msf_curve_at_FoS_phase(self, p, g_o, path_output, num_phase, Phases):
        """ Adds FoS curve for FoS phase
        """
        # phase information
        self.axes.text(3*Report.cm, 25.7*Report.cm, 'Phase {0}: {1} - Factor of safety'.format(num_phase+1, Phases[num_phase]['phase_name']), fontsize=9, fontweight='bold', va='center')

        # create canvas
        ax1 = self.axes.figure.add_axes([0.2, 0.2, 0.65, 0.55])
        canvas = MyStaticMplCanvas(width=0.65, height=0.65)
        canvas.axes = ax1

        # plot curve
        self.plot_msf_curve_at_FoS_phase(canvas, p, g_o, path_output, num_phase)


    def plot_model(self, canvas, geometry, Boreholes, Layer_polygons, Walls, Anchors, Struts, Lineloads, Pointloads, Polygons,
                   Soilclusters, Waterlevels):
        """ Plots model section at a phase
        """
        # geometry and borehole
        canvas.plot_geometry(geometry)
        for borehole in Boreholes:
            borehole['pathpatches'] = canvas.plot_borehole(len(Boreholes), borehole, geometry)
        # soil layers
        for i, layer in enumerate(Layer_polygons):
            layer['path_polygon'], layer['pathpatch_top'], layer['pathpatch_bottom'], layer['pathpatches'] = canvas.plot_layer(Boreholes, i, geometry[0], geometry[2])
            layer['pathpatch_layer'] = canvas.plot_assigned_layer(layer['path_polygon'], layer['color'])
        # wall
        for wall in Walls:
            wall['pathpatches_report'] = canvas.plot_wall(wall, wall['color'])
        # anchors
        for anchor in Anchors:
            anchor['pathpatches_report'] = canvas.plot_ground_anchor(anchor)
        # struts
        for strut in Struts:
            strut['pathpatches_report'] = canvas.plot_strut(strut, geometry[1], geometry[3])
        # lineloads
        for lload in Lineloads:
            lload['pathpatches_report'] = canvas.plot_lineload(lload, geometry[1], geometry[3])
        # pointloads
        for pload in Pointloads:
            pload['pathpatches_report'] = canvas.plot_pointload(pload, geometry[1], geometry[3])
        # polygons
        for polygon in Polygons:
            polygon['pathpatches_report'] = canvas.plot_polygon(polygon['points'], polygon['color'])
        # soilclusters
        for soilcluster in Soilclusters:
            if soilcluster['isRectangular']:
                soilcluster['pathpatches_report'] = canvas.plot_soilcluster(soilcluster, soilcluster['annotate'])
            else:
                soilcluster['pathpatches_report'] = canvas.plot_soilcluster_points(soilcluster)
        # waterlevels
        for waterlevel in Waterlevels:
            waterlevel['pathpatches_report'] = canvas.plot_waterlevel(waterlevel)


    def add_additional_phase_information(self, phase):
        """ Adds additional phase information
        """
        if phase['phase_name'] == 'Excavation':
            self.axes.text(3*Report.cm, 24.9*Report.cm, 'Excavation level: {0:.3f} [mNN]'.format(phase['soilcluster_bottom']), fontsize=9, fontweight='bold', va='center')
        elif phase['phase_name'] == 'Anchoring':
            #self.axes.text(3*Report.cm, 24.9*Report.cm, 'Anchor level: {0:.3f} [mNN]'.format(phase['anchor_level']), fontsize=9, fontweight='bold', va='center')
            self.axes.text(3*Report.cm, 24.9*Report.cm, 'Anchor level: {0:.3f} [mNN], Locking force: {1} [kN]'.format(phase['anchor_level'], *phase['F_prestress']), fontsize=9, fontweight='bold', va='center')
        elif (phase['phase_name'] == 'Strut/slab construction') | (phase['phase_name'] == 'Strut deconstruction'):
            self.axes.text(3*Report.cm, 24.9*Report.cm, 'Strut level: {0:.3f} [mNN]'.format(phase['strut_level']), fontsize=9, fontweight='bold', va='center')
        if phase['phase_name'] == 'Dewatering (lowering water level)':
            self.axes.text(3*Report.cm, 24.9*Report.cm, 'Dewatering level: {0:.3f} [mNN]'.format(phase['y_ref']), fontsize=9, fontweight='bold', va='center')


    def plot_model_at_phase(self, canvas, phase, Lineloads, Pointloads, Walls, Soilclusters, Anchors, Struts):
        """ Plots model view of the calculation phase
        """
        if phase['phase_name'] == 'Wall construction':
            for lineload in Lineloads:
                canvas.set_color(lineload['pathpatches_report'], 'blue')
            for pointload in Pointloads:
                canvas.set_color(pointload['pathpatches_report'], 'blue')
            for wall in Walls:
                canvas.set_color(wall['pathpatches_report'][0], wall['color'][0])
                canvas.set_color(wall['pathpatches_report'][1], wall['color'][1])
                canvas.set_color(wall['pathpatches_report'][2], wall['color'][2])
                canvas.set_color(wall['pathpatches_report'][3], wall['color'][3])

        elif phase['phase_name'] == 'Excavation':
            for soilcluster in Soilclusters:
                if soilcluster['id'] in phase['soilcluster_ids']:
                    canvas.set_color_excavated_soilcluster(soilcluster['pathpatches_report'])

        elif phase['phase_name'] == 'Anchoring':
            for anchor in Anchors:
                if anchor['id'] in phase['anchor_ids']:
                    canvas.set_color(anchor['pathpatches_report'][0], 'black')
                    canvas.set_color(anchor['pathpatches_report'][1], 'magenta')
                    canvas.set_color(anchor['pathpatches_report'][2], 'black')

        elif phase['phase_name'] == 'Strut/slab construction':
            for strut in Struts:
                if strut['id'] in phase['strut_ids']:
                    if strut['usage'] == 'Strut':
                        canvas.set_color(strut['pathpatches_report'][0], 'black')
                        canvas.set_color(strut['pathpatches_report'][1], 'black')
                        canvas.set_color(strut['pathpatches_report'][2], 'black')
                    else: # slabs
                        canvas.set_color(strut['pathpatches_report'][0], 'orange')
                        canvas.set_color(strut['pathpatches_report'][1], 'orange')
                        canvas.set_color(strut['pathpatches_report'][2], 'black')

        elif phase['phase_name'] == 'Strut deconstruction':
            for strut in Struts:
                if strut['id'] in phase['strut_ids']:
                    canvas.set_color(strut['pathpatches_report'], 'grey')


    def initialize_pathpatches_for_phase(self, canvas, Lineloads, Pointloads, Anchors, Struts, Walls):
        """ Sets structure colors to grey
        """
        for lineload in Lineloads:
            canvas.set_grey_pathpatches(lineload['pathpatches_report'])
        for pointload in Pointloads:
            canvas.set_grey_pathpatches(pointload['pathpatches_report'])
        for anchor in Anchors:
            canvas.set_grey_pathpatches(anchor['pathpatches_report'])
        for strut in Struts:
            canvas.set_grey_pathpatches(strut['pathpatches_report'])
        for wall in Walls:
            canvas.set_grey_pathpatches(wall['pathpatches_report'])


    def remove_pathpatches_report(self, canvas, geometry, Boreholes, Layer_polygons, Walls, Anchors, Struts, Lineloads, Pointloads, Polygons,
                    Soilclusters, Waterlevels):
        """ Remove all pathpatches used for the report
        """
        # geometry and borehole
        canvas.plot_geometry(geometry)
        for borehole in Boreholes:
            borehole['pathpatches'] = canvas.plot_borehole(len(Boreholes), borehole, geometry)
        # soil layers
        for i, layer in enumerate(Layer_polygons):
            layer['path_polygon'], layer['pathpatch_top'], layer['pathpatch_bottom'], layer['pathpatches'] = canvas.plot_layer(Boreholes, i, geometry[0], geometry[2])
            layer['pathpatch_layer'] = canvas.plot_assigned_layer(layer['path_polygon'], layer['color'])
        # wall
        for wall in Walls:
            wall['pathpatches_report'] = canvas.plot_wall(wall, wall['color'])
        # anchors
        for anchor in Anchors:
            anchor['pathpatches_report'] = canvas.plot_ground_anchor(anchor)
        # struts
        for strut in Struts:
            strut['pathpatches_report'] = canvas.plot_strut(strut, geometry[1], geometry[3])
        # lineloads
        for lload in Lineloads:
            lload['pathpatches_report'] = canvas.plot_lineload(lload, geometry[1], geometry[3])
        # pointloads
        for pload in Pointloads:
            pload['pathpatches_report'] = canvas.plot_pointload(pload, geometry[1], geometry[3])
        # polygons
        for polygon in Polygons:
            polygon['pathpatches_report'] = canvas.plot_polygon(polygon['points'], polygon['color'])
        # soilclusters
        for soilcluster in Soilclusters:
            if soilcluster['isRectangular']:
                soilcluster['pathpatches_report'] = canvas.plot_soilcluster(soilcluster, soilcluster['annotate'])
            else:
                soilcluster['pathpatches_report'] = canvas.plot_soilcluster_points(soilcluster)
        # waterlevels
        for waterlevel in Waterlevels:
            waterlevel['pathpatches_report'] = canvas.plot_waterlevel(waterlevel)


    @classmethod
    def open_output_database(cls, path):
        """ Opens PLAXIS2D output database
        path: path to output database
        """
        PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
        p = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001)

        s_o, g_o = new_server('localhost', 10001, password='mypassword')
        s_o.open(path)

        return p, g_o


    def plot_wall_outputs_at_phase(self, canvas, p, g_o, num_phase, path_output, x_wall, wall, Anchors, Struts):
        """ Plot wall outputs at a phase
        """
        if p.poll() is not None:
            # reopen PLAXIS2D output database if it is closed
            p, g_o = self.open_output_database(os.path.join(path_output, 'retaining_wall.p2dx'))

        (phasename, y_plate, Ux_plate, Nx2D_plate, Nx2Demax_plate, Nx2Demin_plate, M2D_plate,
        M2Demax_plate, M2Demin_plate, Q2D_plate,
        Q2Demax_plate, Q2Demin_plate) = get_plate_outputs(path_output, g_o, x_wall, num_phase)

        # plot
        axes = self.fig.add_subplot(2, 4, 1, position=[0.2, 0.5, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output(y_plate, np.array(Ux_plate)*1000, 2, 4, 1, 'Ux [mm]', 'Y [m]', 'blue', add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 2, position=[0.36, 0.5, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output(y_plate, Nx2D_plate, 2, 4, 2, 'Nx2D [kN/m]', None, 'red', add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 3, position=[0.52, 0.5, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output(y_plate, M2D_plate, 2, 4, 3, 'M2D [kNm/m]', None, 'red', add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 4, position=[0.68, 0.5, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output(y_plate, Q2D_plate, 2, 4, 4, 'Q2D [kN/m]', None, 'red', add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 5, position=[0.25, 0.2, 0.07, 0.25]); canvas.axes = axes
        self.plot_table_wall_info(canvas, wall)     # wall top/ bottom/ embedment depth
        axes = self.fig.add_subplot(2, 4, 6, position=[0.36, 0.2, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output_envelop(y_plate, Nx2Demax_plate, Nx2Demin_plate, 2, 4, 6, 'Nx2D_Envelope [kN/m]', 'Y [m]', add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 7, position=[0.52, 0.2, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output_envelop(y_plate, M2Demax_plate, M2Demin_plate, 2, 4, 7, 'M2D_Envelope [kNm/m]', None, add_subplot=False)
        axes = self.fig.add_subplot(2, 4, 8, position=[0.68, 0.2, 0.13, 0.25]); canvas.axes = axes
        canvas.plot_wall_output_envelop(y_plate, Q2Demax_plate, Q2Demin_plate, 2, 4, 8, 'Q2D_Envelope [kN/m]', None, add_subplot=False)


    def plot_table_wall_info(self, canvas, wall):
        """ Adds wall information such as top/ bottom/ embedment depth
        """
        level_top = '{0:.2f}'.format(wall['point1'][1])
        level_bottom = '{0:.2f}'.format(wall['point2'][1])
        depth_embedment = '{0:.2f}'.format(wall['depth_embedment'])
        label_rows = ['Wall top [mNN]', 'Wall bottom [mNN]', 'Embedment depth [m]']
        label_columns = None
        cell_text = [[level_top], [level_bottom], [depth_embedment]]

        # plot table
        canvas.plot_table(cell_text, None, label_columns, label_rows, colWidths=[0.7, 0.3])


    def plot_table_anchor_strut_forces_at_phase(self, canvas, p, g_o, num_phase, path_output, Anchors, Struts):
        """ Plot wall outputs at a phase
        """
        if p.poll() is not None:
            # reopen PLAXIS2D output database if it is closed
            p, g_o = self.open_output_database(os.path.join(path_output, 'retaining_wall.p2dx'))

        F_anchors = get_all_anchors_force(g_o, Anchors, num_phase)
        F_struts = get_all_struts_force(g_o, Struts, num_phase)
        # plot anchor forces/ strut forces
        self.plot_table_anchor_strut_forces(canvas, F_anchors, F_struts)


    def export_field_data_at_phase(self, canvas, p, g_o, path_output, num_phase, dewatering_phase=False, FoS_phase=False):
        """ Exports/ plots field data at a phase
        """
        if p.poll() is not None:
            # reopen PLAXIS2D output database if it is closed
            p, g_o = self.open_output_database(os.path.join(path_output, 'retaining_wall.p2dx'))

        g_o.Plots[-1].PhaseBehaviour = 'projectphase'

        phase_i = 'Phase_' + str(num_phase)
        phase_o = g_o.Phases[-1]
        for phase in g_o.Phases[:]:
            if phase.Name.value == phase_i:
                phase_o = phase
                #phase_o_name = phase.Identification.value

        # store png images under path_output\reports
        path_report = os.path.join(path_output, 'report')
        if not os.path.exists(path_report):
            os.makedirs(path_report)

        fname = os.path.join(path_report, 'utot_{0}.png').format(num_phase)
        g_o.Plots[-1].Phase = phase_o
        g_o.Plots[-1].ResultType = g_o.ResultTypes.Soil.Utot            # Total displacement
        if dewatering_phase:
            g_o.Plots[-1].ResultType = g_o.ResultTypes.Soil.PActive     # Active pore pressure
        if FoS_phase:
            g_o.Plots[-1].ResultType = g_o.ResultTypes.Soil.IncrementalDeviatoricStrain    # Incremental deviatoric strain (delta_eps1 - delta_eps3)/2
        g_o.Plots[-1].DrawFrame = False
        g_o.Plots[-1].export(fname, 1920, 1080)

        # put png image on canvas
        canvas.plot_image_from_file(fname)


    def plot_msf_curve_at_FoS_phase(self, canvas, p, g_o, path_output, num_phase):
        """ Plots safety factor curve for FoS phase
        """
        if p.poll() is not None:
            # reopen PLAXIS2D output database if it is closed
            p, g_o = self.open_output_database(os.path.join(path_output, 'retaining_wall.p2dx'))

        msf_points = get_msf_points(g_o, num_phase+1)
        #print(msf_points)
        canvas.plot_curve(msf_points)


    def plot_table_anchor_strut_forces(self, canvas, F_anchors, F_struts):
        """ Plots anchor and strut forces
        """
        try:
            label_columns = ['F phase [kN]', 'F max [kN]']
            F_all = F_anchors + F_struts
            F_all_sorted = sorted((f for f in F_all), key=lambda f: f['position'][1], reverse=True) # sorted from top to bottom
            cell_text = []
            label_rows = []
            for f in F_all_sorted:
                if 'AnchorForce2D' in f:
                    cell_text_i = [float('{:.2f}'.format(f['AnchorForce2D'])), float('{:.2f}'.format(f['AnchorForceMax2D']))]
                    label_row_i = f['position']
                    cell_text.append(cell_text_i)
                    label_rows.append(label_row_i)

            # plot table
            canvas.plot_table(cell_text, None, label_columns, label_rows, colWidths=[1.0/3]*2, loc='center')

        except:
            self.fig = None


    def plot_table_soil_stratigraphy(self, canvas, Layer_polygons, Boreholes):
        """ Adds table for soil stratigraphy
        """
        borehole = Boreholes[0]
        # prepare table
        label_columns = [borehole['name'] + ' - Top [mNN]', borehole['name'] + ' - Bottom [mNN]']
        cell_text = []
        colors = []
        label_rows = []
        for i, layer_polygon in enumerate(Layer_polygons):
            cell_text_i = [borehole['Top'][i], borehole['Bottom'][i]]
            label_row_i = layer_polygon['soilmaterial_layer']
            color_row_i = [layer_polygon['color']]*2
            label_rows.append(label_row_i)
            colors.append(color_row_i)
            cell_text.append(cell_text_i)

        # plot table
        canvas.plot_table(cell_text, colors, label_columns, label_rows, colWidths=[1.0/3]*2, loc='center')


    def plot_table_soil_materials(self, canvas, Layer_polygons):
        """ Plots table for soil stratigraphy
        """
        # read data from file
        data_soils = []
        for layer in Layer_polygons:
            if 'soilmaterial_layer' in layer:
                json_item = layer['soilmaterial_layer']
                PATH_MATERIAL_LIBRARY = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'materials')
                material_file = os.path.join(PATH_MATERIAL_LIBRARY, json_item + '.json')

                with open(material_file, "r") as read_file:
                    data = json.load(read_file, object_pairs_hook=OrderedDict)
                data_soil = {'name': data['MaterialName'], 'data': data, 'color': layer['color']}
                data_soils.append(data_soil)

        # filter data
        keys_to_remove = ['Colour', 'SoilModel', 'DrainageType', 'perm_primary_horizontal_axis', 'perm_vertical_axis', 'K0Determination',
                        'Rf', 'Pref', 'powerm']
        keys_to_replace = ['Gref']
        for data_soil in data_soils:
            for key in keys_to_remove:
                if key in data_soil['data']:
                    del data_soil['data'][key]
            for key in keys_to_replace:
                if key in data_soil['data']:
                    Gref = data_soil['data']['Gref']
                    nu = data_soil['data']['nu']
                    data_soil['data']["E'"] = Gref*2*(1+nu)
                    del data_soil['data'][key]

        # count max columns
        column_count = 0
        for data_soil in data_soils:
            column_count = max(column_count, len(data_soil['data']))

        # prepare data
        units = {'MaterialName': '', 'gammaUnsat': '\n[kN/m^3]', 'gammaSat': '\n[kN/m^3]', 'E50ref': '\n[kN/m^2]', 'EoedRef': '\n[kN/m^2]', 'EurRef': '\n[kN/m^2]', "E'": '\n[kN/m^2]', 'G0ref': '\n[kN/m^2]', 'gamma07': '\n[-]',
                'nu': '\n[-]', 'Cref': '\n[kN/m^2]', 'cref': '\n[kN/m^2]', 'phi': '\n[degree]', 'psi': '\n[degree]', 'K0Primary': '\n[-]', 'K0nc': '\n[-]', 'Rinter': '\n[-]'}
        cell_text = []
        colors = []
        for data_soil in data_soils:
            #column_count = len(data_soil['data'])
            colors.append([data_soil['color']]*column_count)
            colors.append([data_soil['color']]*column_count)
            cell_text_keys_row_i = ['']*column_count
            cell_text_values_row_i = ['']*column_count

            keys = [key for key in data_soil['data'].keys()]
            values = [float('{:.2f}'.format(value)) if isinstance(value, float) else value for value in data_soil['data'].values()]

            # adjust finer decimal precision for gamm07
            for i, key in enumerate(keys):
                if key == 'gamma07':
                    values[i] = data_soil['data'][key]

            for i in range(len(keys)):
                cell_text_keys_row_i[i] = keys[i] + units[keys[i]]
                cell_text_values_row_i[i] = values[i]

            cell_text.append(cell_text_keys_row_i)
            cell_text.append(cell_text_values_row_i)

        # plot table
        canvas.plot_table(cell_text, colors, None, None, fontsize=7.5)


    def plot_table_soil_materials_permeability(self, canvas, Layer_polygons):
        """ Plots table for soil permeabilites for all soils in stratigraphy
        """
        # read data from file
        data_soils = []
        for layer in Layer_polygons:
            if 'soilmaterial_layer' in layer:
                json_item = layer['soilmaterial_layer']
                PATH_MATERIAL_LIBRARY = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'materials')
                material_file = os.path.join(PATH_MATERIAL_LIBRARY, json_item + '.json')

                with open(material_file, "r") as read_file:
                    data = json.load(read_file, object_pairs_hook=OrderedDict)
                data_soil = {'name': data['MaterialName'], 'data': data, 'color': layer['color']}
                data_soils.append(data_soil)

        # filter data
        keys_to_remove = ['Colour', 'SoilModel', 'DrainageType', 'K0Determination',
                        'Rf', 'Pref', 'powerm']
        keys_to_replace = ['Gref']
        for data_soil in data_soils:
            for key in keys_to_remove:
                if key in data_soil['data']:
                    del data_soil['data'][key]
            for key in keys_to_replace:
                if key in data_soil['data']:
                    Gref = data_soil['data']['Gref']
                    nu = data_soil['data']['nu']
                    data_soil['data']["E'"] = Gref*2*(1+nu)
                    del data_soil['data'][key]

        # count max columns
        column_count = 3
        #for data_soil in data_soils:
        #    column_count = max(column_count, len(data_soil['data']))

        # prepare data
        units = {'MaterialName': '', 'perm_primary_horizontal_axis': '\n[m/s]', 'perm_vertical_axis': '\n[m/s]'}
        cell_text = []
        colors = []
        for data_soil in data_soils:
            #column_count = len(data_soil['data'])
            colors.append([data_soil['color']]*column_count)
            colors.append([data_soil['color']]*column_count)
            cell_text_keys_row_i = ['']*column_count
            cell_text_values_row_i = ['']*column_count

            #keys = [key for key in data_soil['data'].keys()]
            #values = [float('{:.2f}'.format(value)) if isinstance(value, float) else value for value in data_soil['data'].values()]
            keys = ['MaterialName', 'perm_primary_horizontal_axis', 'perm_vertical_axis']
            values = [data_soil['data'][key] for key in keys]

            for i in range(len(keys)):
                cell_text_keys_row_i[i] = keys[i] + units[keys[i]]
                cell_text_values_row_i[i] = values[i]

            cell_text.append(cell_text_keys_row_i)
            cell_text.append(cell_text_values_row_i)

        # plot table
        canvas.plot_table(cell_text, colors, None, None, fontsize=7.5)

    def plot_table_wall_material(self, canvas, wall):
        """ Plots table for wall
        """
        # read data from file
        PATH_MATERIAL_LIBRARY = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'materials')
        json_item = wall['json_item']
        material_file = os.path.join(PATH_MATERIAL_LIBRARY, json_item + 'moniman.json')
        with open(material_file, "r") as read_file:
            data = json.load(read_file, object_pairs_hook=OrderedDict)

        data_wall = {'name': data['MaterialName'], 'data': data, 'color': wall['color']}

        keys_to_replace = ['Gref']
        # replace data
        for key in keys_to_replace:
            if key in data_wall['data']:
                Gref = data_wall['data']['Gref']
                nu = data_wall['data']['nu']
                if wall['wall_type'] == 'Dwall':
                    data_wall['data']["E'"] = get_Eref_Dwall(Gref, nu)
                elif wall['wall_type'] == 'SPW':
                    D = data_wall['data']['D']
                    S = data_wall['data']['S']
                    EA = data_wall['data']['EA']
                    data_wall['data']["E'"] = get_Eref_SPW(D, S, EA)
                elif wall['wall_type'] == 'CPW':
                    D = data_wall['data']['D']
                    S = data_wall['data']['S']
                    EA = data_wall['data']['EA']
                    data_wall['data']["E'"] = get_Eref_CPW(D, S, EA)
                del data_wall['data'][key]

        # filter data
        keys_to_remove = ['Colour', 'D', 'S']
        keys_to_replace = ['Gref']
        for key in keys_to_remove:
            if key in data_wall['data']:
                del data_wall['data'][key]

        # prepare data
        column_count = len(data_wall['data'])
        cell_text = []
        keys = [key for key in data_wall['data'].keys()]
        units = ['', '', '\n[kN/m]', '\n[kN/m]', '\n[kNm^2/m]', '\n[-]', '\n[m]', '\n[kN/m/m]', '\n[kN/m^2]']
        values = [float('{:.2f}'.format(value)) if isinstance(value, float) else value for value in data_wall['data'].values()]

        cell_text_keys = ['']*column_count
        cell_text_values = ['']*column_count
        for i in range(len(keys)):
            cell_text_keys[i] = keys[i] + units[i]
            cell_text_values[i] = values[i]

        cell_text.append(cell_text_keys)
        cell_text.append(cell_text_values)

        # plot table
        canvas.plot_table(cell_text, None, None, None, fontsize=7.5)


if __name__ == '__main__':
    # test
    project_title = 'Sample project'
    project_properties = {'project_title': project_title}
    report_page1 = Report()
    report_page1.add_project_info(project_properties)

    filename = os.path.join(os.getcwd(), project_title + '.pdf')
    pp = PdfPages(filename)
    report_page1.fig.savefig(pp, format='pdf', bbox_inches='tight')

    pp.close()
    # view report in Acrobat Reader
    ACROBAT = r'C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat'
    cmd = [os.path.join(ACROBAT, r'Acrobat.exe')]
    cmd.append(filename)
    subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)