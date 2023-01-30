# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 2018

@author: nya
"""
import sys
from os.path import join
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QColor, QStandardItem
from tools.math import hex_to_rgb#, rgb_to_integer
import solver.plaxis2d.input_scripting_commands as plaxis2d_input


class loadPlaxman:
    """ This class defines static methods to reconstruct Plaxman's sate.
        Static methods are used so that no instance of the class is constructed.
        Also, static methods are suitable because no class attributes need to be changed during loading process.
    """

    @staticmethod
    def update_geometry(ui, plot_canvas, plaxis2d_input_file, prefix, project_properties, moniman_paths, geometry):
        """ Reconstruct geometry
        """
        # fill comboboxes for model type and element type
        model_types = ['Plane strain', 'Axisymmetry']
        element_types = ['15 nodes', '6 nodes']
        for mt in model_types:
            ui.comboBox.addItem(mt) 
        for et in element_types:
            ui.comboBox_2.addItem(et) 

        if geometry is not None:
            plaxis2d_input.set_project_properties(plaxis2d_input_file, prefix, project_properties, moniman_paths)
            plaxis2d_input.set_geometry(plaxis2d_input_file, prefix, geometry)
            plot_canvas.plot_geometry(geometry)

            ui.lineEdit.setText(str(geometry[0]))   # x_min
            ui.lineEdit_2.setText(str(geometry[1])) # y_min
            ui.lineEdit_3.setText(str(geometry[2])) # x_max
            ui.lineEdit_4.setText(str(geometry[3])) # y_max

            # model type, element type, and project title
            if project_properties['model_type'] == 'Axisymmetry':
                ui.comboBox.setCurrentIndex(1)
            else:
                ui.comboBox.setCurrentIndex(0)

            if project_properties['element_type'] == '6noded':
                ui.comboBox_2.setCurrentIndex(1)
            else:
                ui.comboBox_2.setCurrentIndex(0)

            ui.lineEdit_13.setText(project_properties['project_title'])

            # Set background color for x_min and x_max, indicating that they are responsive
            ui.lineEdit.setStyleSheet("background-color: rgb(242, 255, 116);")
            ui.lineEdit_3.setStyleSheet("background-color: rgb(242, 255, 116);")


    @staticmethod
    def add_borehole(ui, plot_canvas, plaxis2d_input_file, prefix, Boreholes, geometry):
        """ Reconstruct boreholes
        """

        for i, borehole in enumerate(Boreholes):
            #borehole['name'] = 'BH1'
            plaxis2d_input.add_borehole(plaxis2d_input_file, prefix, i+1, borehole)
            Boreholes[i]['pathpatches'] = plot_canvas.plot_borehole(i+1, borehole, geometry)

            ui.lineEdit_5.setText(str(borehole['x']))
            ui.lineEdit_6.setText(str(borehole['Head']))

            item = ui.tableWidget.verticalHeaderItem(0)
            item.setText(QCoreApplication.translate("MainWindow", "Layer 1"))
            item_number = 2*i
            item = ui.tableWidget.horizontalHeaderItem(item_number)
            item.setText(QCoreApplication.translate("MainWindow", borehole['name'] + " - Top"))
            item = ui.tableWidget.horizontalHeaderItem(item_number + 1)
            item.setText(QCoreApplication.translate("MainWindow", borehole['name'] + " - Bottom"))

            ui.comboBox_33.addItem(borehole['name'])


    @staticmethod
    def add_layer(ui, plot_canvas, plaxis2d_input_file, prefix, Layer_polygons, Boreholes):
        """ Reconstruct layer polygons
        """
        ui.tableWidget.clearContents()
        # add layer values
        for i, layer_polygon in enumerate(Layer_polygons):
            plaxis2d_input.add_layer(plaxis2d_input_file, prefix, i+1, layer_polygon['id'])

            item = ui.tableWidget.verticalHeaderItem(i)
            item.setText(QCoreApplication.translate("MainWindow", "Layer " + str(i+1)))

            for j, borehole in enumerate(Boreholes):
                plaxis2d_input.add_layer_values(plaxis2d_input_file, prefix, j+1, i, borehole['Top'][i], borehole['Bottom'][i])

            x_min = float(ui.lineEdit.text())
            x_max = float(ui.lineEdit_3.text())
            layer_polygon['path_polygon'], layer_polygon['pathpatch_top'], layer_polygon['pathpatch_bottom'], layer_polygon['pathpatches'] = plot_canvas.plot_layer(Boreholes, i, x_min, x_max)
            ui.comboBox_4.addItem("Layer " + str(i+1))
            

    @staticmethod
    def assign_material(ui, plot_canvas, plaxis2d_input_file, prefix, Layer_polygons, Boreholes, Soilmaterials):
        """ Reconstruct material assignments
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        for i, layer_polygon in enumerate(Layer_polygons):
            if 'soilmaterial_layer' in layer_polygon.keys():
                if layer_polygon['soilmaterial_layer'] is not None:
                    material_file_path = join(PATH_MATERIAL_LIBRARY, layer_polygon['soilmaterial_layer'] + '.json')
                    plaxis2d_input.assign_soil_to_layer(plaxis2d_input_file, prefix, str(i+1), layer_polygon['soilmaterial_layer'], material_file_path)
            
                    layer_polygon['pathpatch_layer'] = plot_canvas.plot_assigned_layer(layer_polygon['path_polygon'], layer_polygon['color'])
                    #print(layer_polygon['color'])

                    # reset colors in table
                    for col in range(1, 2*len(Boreholes), 2):
                        ui.tableWidget.item(i, col).setBackground(QColor(*hex_to_rgb(layer_polygon['color'])))

                    # show material name in soil layer
                    item = ui.tableWidget.verticalHeaderItem(i)
                    item.setText(QCoreApplication.translate("MainWindow", layer_polygon['soilmaterial_layer']))

        # list available soil models
        loadPlaxman.list_available_soil_models(ui)

        # add to available soil materials 
        if Soilmaterials:
            loadPlaxman.reconstruct_materials_list(ui, Soilmaterials)


    @staticmethod
    def reconstruct_materials_list(ui, Soilmaterials):
        """ Put soil materials back to combobox lists
        """
        loadPlaxman.fill_soilmaterials_in_combobox(ui.comboBox_17, Soilmaterials)    # in Soil polygons
        loadPlaxman.fill_soilmaterials_in_combobox(ui.comboBox_18, Soilmaterials)    # in Soil materials
        loadPlaxman.fill_soilmaterials_in_combobox(ui.comboBox_19, Soilmaterials)    # in Backman
        loadPlaxman.fill_soilmaterials_in_combobox(ui.comboBox_29, Soilmaterials)    # in Sensiman
            


    @staticmethod
    def fill_soilmaterials_in_combobox(combobox, Soilmaterials):
        """ Fills soil materials in combobox, with color
        """
        def combo_changed():
            for soilmat in Soilmaterials:
                if soilmat['json_item'] == combobox.currentText():
                    combobox.setStyleSheet("QComboBox:editable{ background-color: %s}" % QColor('white').name())
                    combobox.setStyleSheet("QComboBox:editable{ color: %s}" % soilmat['color'])
                    
        combobox.clear()
        model = combobox.model()
        for soilmat in Soilmaterials:
            entry = QStandardItem(soilmat['json_item'])
            color = soilmat['color']
            entry.setForeground(QColor(color))
            entry.setBackground(QColor('white'))
            model.appendRow(entry)

        combobox.currentIndexChanged.connect(combo_changed)



    @staticmethod
    def list_available_soil_models(ui):
        """ Put soil materials back to combobox lists
        """
        mat_models = ['MC', 'HS', 'HSsmall', 'LE']
        for mm in mat_models:
            ui.comboBox_3.addItem(mm) 
            ui.comboBox_16.addItem(mm)


    @staticmethod
    def add_wall(ui, plot_canvas, plaxis2d_input_file, prefix, Walls, Wallmaterials):
        """ Reconstruct walls
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        # list wall types
        loadPlaxman.list_available_wall_types(ui)
        
        for wall in Walls:
            wall_file_path = join(PATH_MATERIAL_LIBRARY, wall['json_item'] + '.json')
            plaxis2d_input.add_wall(plaxis2d_input_file, prefix, wall, wall['json_item'], wall_file_path)

            wall['pathpatches'] = plot_canvas.plot_wall(wall, wall['color'])
            #print(wall['color'])

            # set text back to GUI
            ui.lineEdit_7.setText(str(wall['point1'][0]) + ', ' + str(wall['point1'][1]))
            ui.lineEdit_9.setText(str(wall['point2'][0]) + ', ' + str(wall['point2'][1]))
            ui.lineEdit_44.setText(str(wall['point1'][0]) + ', ' + str(wall['point1'][1]))
            ui.lineEdit_45.setText(str(wall['point2'][0]) + ', ' + str(wall['point2'][1]))

            ui.comboBox_14.addItem(str(wall['id']))    # for wall outputs in Plaxman
            ui.comboBox_49.addItem(str(wall['id']))    # for selection of wall parameters in Sensiman
            ui.comboBox_53.addItem(str(wall['id']))    # for selection of wall parameters in Backman
            #ui.comboBox_32.addItem(str(wall['wall_name']))    # in Plaxman: Walls

        if Wallmaterials:
            loadPlaxman.reconstruct_wallmaterials_list(ui, Wallmaterials)


    @staticmethod
    def reconstruct_wallmaterials_list(ui, Wallmaterials):
        """ Put wall materials back to combobox
        """
        loadPlaxman.fill_soilmaterials_in_combobox(ui.comboBox_32, Wallmaterials)

    @staticmethod
    def list_available_wall_types(ui):
        """ Put wall types back to combobox lists
        """
        wall_types = ['Dwall', 'SPW', 'CPW', 'MIP', 'Steel profile H/U']
        for wt in wall_types:
            ui.comboBox_5.addItem(wt) 

    @staticmethod
    def define_soil_improvement_structure(ui, plot_canvas, plaxis2d_input_file, prefix, sc_name, SCs, FDCs, polygonPoints):
        """ Reconstructs stone columns and rigid inclusions
        """
        # Stone columns
        for sc in SCs:
            for poly_point in sc['polygonPoints']:
                poly_point['pathpatch'] = plot_canvas.plot_point(poly_point['point'])
            ui.comboBox_45.addItem(sc['sc_name'])
            ui.comboBox_47.addItem(sc['sc_name'])
            ui.lineEdit_76.setText(str(sc['polygonPoints'][0]['point'][0]) + ', ' + str(sc['polygonPoints'][0]['point'][1]))
            ui.lineEdit_77.setText(str(sc['polygonPoints'][1]['point'][0]) + ', ' + str(sc['polygonPoints'][1]['point'][1]))
            ui.lineEdit_81.setText(str(sc['polygonPoints'][2]['point'][0]) + ', ' + str(sc['polygonPoints'][2]['point'][1]))
            ui.lineEdit_78.setText(str(sc['polygonPoints'][3]['point'][0]) + ', ' + str(sc['polygonPoints'][3]['point'][1]))

            # refine mesh
            if 'sc_points_fine_mesh' in sc:
                plaxis2d_input.add_polygon_fine_mesh_with_id(plaxis2d_input_file, prefix, sc['sc_points_fine_mesh'], sc['sc_name'])

        # collect all polygons for mesh refinement and apply them
        Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(sc['sc_name']) for sc in SCs]
        if Polygons_fine_mesh:
            plaxis2d_input.apply_refine_mesh_multi_polygons(plaxis2d_input_file, prefix, Polygons_fine_mesh)

        # Rigid inclusions
        for fdc in FDCs:
            for poly_point in fdc['polygonPoints']:
                poly_point['pathpatch'] = plot_canvas.plot_point(poly_point['point'])
            ui.comboBox_45.addItem(fdc['FDC_name'])
            ui.comboBox_47.addItem(fdc['FDC_name'])

            # refine mesh
            if 'sc_points_fine_mesh' in fdc:
                plaxis2d_input.add_polygon_fine_mesh_with_id(plaxis2d_input_file, prefix, fdc['sc_points_fine_mesh'], fdc['FDC_name'])

        # collect all polygons for mesh refinement and apply them
        Polygons_fine_mesh = ['Polygon_fine_mesh_{0}'.format(fdc['FDC_name']) for fdc in FDCs]
        if Polygons_fine_mesh:
            plaxis2d_input.apply_refine_mesh_multi_polygons(plaxis2d_input_file, prefix, Polygons_fine_mesh)


    @staticmethod
    def add_ground_anchor(ui, plot_canvas, plaxis2d_input_file, prefix, Anchors, geometry):
        """ Reconstructs ground anchors
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        # list ground resistance types
        grout_resistance_types = ['Linear', 'Multi-linear']
        for gr in grout_resistance_types:
            ui.comboBox_7.addItem(gr) 
        strand_dias = ["0.6''", "0.62''"]
        for dia in strand_dias:
            ui.comboBox_6.addItem(dia)

        for anchor in Anchors:
            strand_file_path = join(PATH_MATERIAL_LIBRARY, anchor['strand_json_item'] + '.json')
            grout_file_path = join(PATH_MATERIAL_LIBRARY, anchor['grout_json_item'] + '.json')
            plaxis2d_input.add_ground_anchor(plaxis2d_input_file, prefix, anchor, strand_file_path, grout_file_path)

            anchor['pathpatches'] = plot_canvas.plot_ground_anchor(anchor)

            # set text back to GUI
            ui.lineEdit_11.setText(str(anchor['position'][0]) + ', ' + str(anchor['position'][1]))

            # set defined strands and grout bodies in comboBoxes
            ui.comboBox_37.addItem(anchor['strand_json_item'])
            ui.comboBox_37.setCurrentIndex(ui.comboBox_37.count()-1)
            ui.comboBox_38.addItem(anchor['grout_json_item'])
            ui.comboBox_38.setCurrentIndex(ui.comboBox_38.count()-1)


    @staticmethod
    def add_strut(ui, plot_canvas, plaxis2d_input_file, prefix, Struts, geometry):
        """ Reconstructs struts
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        # list strut types
        strut_types = ['Steel tube', 'RC strut', 'RC slab']
        for st in strut_types:
            ui.comboBox_8.addItem(st) 
        for strut in Struts:
            strut_file_path = join(PATH_MATERIAL_LIBRARY, strut['json_item'] + '.json')
            plaxis2d_input.add_strut(plaxis2d_input_file, prefix, strut, strut_file_path)

            y_min = geometry[1]
            y_max = geometry[3]
            strut['pathpatches'] = plot_canvas.plot_strut(strut, y_min, y_max)
            
            # set text back to GUI
            ui.lineEdit_29.setText(str(strut['position'][0]) + ', ' + str(strut['position'][1]))
            ui.lineEdit_32.setText(str(strut['direct_x']))
            ui.lineEdit_33.setText(str(strut['direct_y']))

            # set defined strands and grout bodies in comboBoxes
            ui.comboBox_39.addItem(strut['json_item'])
            ui.comboBox_39.setCurrentIndex(ui.comboBox_39.count()-1)
            ui.comboBox_50.addItem(str(strut['id']))    # for selection of strut parameters in Sensiman


    @staticmethod
    def add_lineload(ui, plot_canvas, plaxis2d_input_file, prefix, Lineloads, geometry):
        """ Reconstruct line loads
        """
        for lineload in Lineloads:
            plaxis2d_input.add_lineload(plaxis2d_input_file, prefix, lineload)

            y_min = geometry[1]
            y_max = geometry[3]
            lineload['pathpatches'] = plot_canvas.plot_lineload(lineload, y_min, y_max)
            
            # set text back to GUI
            ui.lineEdit_17.setText(str(lineload['point1'][0]) + ', ' + str(lineload['point1'][1]))
            ui.lineEdit_19.setText(str(lineload['point2'][0]) + ', ' + str(lineload['point2'][1]))
            ui.lineEdit_21.setText(str(lineload['qx']))
            ui.lineEdit_32.setText(str(lineload['qy']))


    @staticmethod
    def add_pointload(ui, plot_canvas, plaxis2d_input_file, prefix, Pointloads, geometry):
        """ Reconstruct point loads
        """
        for pointload in Pointloads:
            plaxis2d_input.add_pointload(plaxis2d_input_file, prefix, pointload)

            y_min = geometry[1]
            y_max = geometry[3]
            pointload['pathpatches'] = plot_canvas.plot_pointload(pointload, y_min, y_max)
            
            # set text back to GUI
            ui.lineEdit_25.setText(str(pointload['point'][0]) + ', ' + str(pointload['point'][1]))
            ui.lineEdit_24.setText(str(pointload['Fx']))
            ui.lineEdit_28.setText(str(pointload['Fy']))


    @staticmethod
    def add_polygon_point(ui, plot_canvas, plaxis2d_input_file, prefix, polygonPoints):
        """ Reconstruct free polygons
        """
        for point in polygonPoints:
            point['pathpatch'] = plot_canvas.plot_point(point['point'])
            

    @staticmethod
    def add_polygon(ui, plot_canvas, plaxis2d_input_file, prefix, Polygons):
        """ Reconstruct free polygons
        """
        PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        for polygon in Polygons:
            material_file_path = join(PATH_MATERIAL_LIBRARY, polygon['soilmaterial'] + '.json')
            plaxis2d_input.add_polygon(plaxis2d_input_file, prefix, polygon, material_file_path)
            plaxis2d_input.add_polygon_initial_phase(plaxis2d_input_file, prefix, polygon)

            polygon['pathpatches'] = plot_canvas.plot_polygon(polygon['points'], polygon['color'])


    @staticmethod
    def apply_mesh(ui, plot_canvas, plaxis2d_input_file, prefix, mesh, Lineloads, Pointloads, Anchors, Struts, Walls):
        """ Reapply mesh properties
        """
        # list mesh types
        mesh_types = ['Coarse', 'Medium', 'Fine']
        for mt in mesh_types:
            ui.comboBox_9.addItem(mt) 

        if 'element_dist' in mesh.keys():
            plaxis2d_input.apply_mesh(plaxis2d_input_file, prefix, mesh)

            for lineload in Lineloads:
                plot_canvas.set_grey_pathpatches(lineload['pathpatches'])
            for pointload in Pointloads:
                plot_canvas.set_grey_pathpatches(pointload['pathpatches'])
            for anchor in Anchors:
                plot_canvas.set_grey_pathpatches(anchor['pathpatches'])
            for strut in Struts:
                plot_canvas.set_grey_pathpatches(strut['pathpatches'])
            for wall in Walls:
                plot_canvas.set_grey_pathpatches(wall['pathpatches'])


    @staticmethod
    def add_soilcluster(ui, plot_canvas, plaxis2d_input_file, prefix, Soilclusters, wall_thickness):
        """ Reconstruct soil clusters (for excavation)
        """
        #PATH_MATERIAL_LIBRARY = join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'],'materials')
        for soilcluster in Soilclusters:
            if soilcluster['isRectangular']:
                #material_file_path = join(PATH_MATERIAL_LIBRARY, soilcluster['soilmaterial'] + '.json')
                plaxis2d_input.add_soilcluster(plaxis2d_input_file, prefix, soilcluster)
                #soilcluster['pathpatches'] = plot_canvas.plot_soilcluster(soilcluster)
                #soilcluster['annotate'] = None
                if 'annotate_FEL' in soilcluster:
                    soilcluster['pathpatches'] = plot_canvas.plot_soilcluster(soilcluster, wall_thickness, annotate=soilcluster['annotate'], annotate_FEL=soilcluster['annotate_FEL'])
                else:
                    soilcluster['pathpatches'] = plot_canvas.plot_soilcluster(soilcluster, wall_thickness, annotate=soilcluster['annotate'])
                # set text back to GUI
                ui.lineEdit_34.setText(str(soilcluster['pointTL'][0]) + ', ' + str(soilcluster['pointTL'][1]))
                ui.lineEdit_35.setText(str(soilcluster['pointTR'][0]) + ', ' + str(soilcluster['pointTR'][1]))
                ui.lineEdit_36.setText(str(soilcluster['pointBL'][0]) + ', ' + str(soilcluster['pointBL'][1]))
                ui.lineEdit_37.setText(str(soilcluster['pointBR'][0]) + ', ' + str(soilcluster['pointBR'][1]))

            else: # polygonal soilcluster
                #material_file_path = join(PATH_MATERIAL_LIBRARY, soilcluster['soilmaterial'] + '.json')
                plaxis2d_input.add_soilcluster_multi_points(plaxis2d_input_file, prefix, soilcluster)
                soilcluster['pathpatches'] = plot_canvas.plot_soilcluster_points(soilcluster, wall_thickness, soilcluster['berm_base'], soilcluster['berm_top'], soilcluster['annotate'])


    @staticmethod
    def add_waterlevel(ui, plot_canvas, plaxis2d_input_file, prefix, Waterlevels):
        """ Reconstruct user water level
        """
        for waterlevel in Waterlevels:
            plaxis2d_input.add_waterlevel(plaxis2d_input_file, prefix, waterlevel)
            waterlevel['pathpatches'] = plot_canvas.plot_waterlevel(waterlevel)

            # set text back to GUI
            ui.lineEdit_38.setText(str(waterlevel['pointL'][0]) + ', ' + str(waterlevel['pointL'][1]))
            ui.lineEdit_39.setText(str(waterlevel['pointR'][0]) + ', ' + str(waterlevel['pointR'][1]))

            ui.comboBox_13.addItem(str(waterlevel['id']))


    @staticmethod
    def add_drain(ui, plot_canvas, plaxis2d_input_file, prefix, drain):
        """ Reconstruct drain
        """
        if 'id' in drain.keys():
            plaxis2d_input.add_drain(plaxis2d_input_file, prefix, drain)
            drain['pathpatches'] = plot_canvas.plot_drain(drain)

            # set text back to GUI
            ui.lineEdit_10.setText(str(drain['wallfoot'][0]) + ', ' + str(drain['wallfoot'][1]))
            ui.lineEdit_40.setText(str(drain['pointL'][0]) + ', ' + str(drain['pointL'][1]))
            ui.lineEdit_41.setText(str(drain['pointR'][0]) + ', ' + str(drain['pointR'][1]))


    @staticmethod
    def add_drains(ui, plot_canvas, plaxis2d_input_file, prefix, drains):
        """ Reconstruct drains
        """
        for drain in drains:
            plaxis2d_input.add_waterlevel_automatedphases_steadystate(plaxis2d_input_file, prefix, drain)
            drain['pathpatches'] = plot_canvas.plot_waterlevel(drain, color='cyan')

            # set text back to GUI
            ui.lineEdit_38.setText(str(drain['pointL'][0]) + ', ' + str(drain['pointL'][1]))
            ui.lineEdit_39.setText(str(drain['pointR'][0]) + ', ' + str(drain['pointR'][1]))


    @staticmethod
    def add_phase(ui, plot_canvas, plaxis2d_input_file, prefix, Phases, Lineloads, Pointloads, Walls, 
                  Soilclusters, Anchors, Struts, Drain):
        """ Reconstruct calculation phases
        """
        # list phase options
        loadPlaxman.list_phase_options_in_comboboxes(ui)
        # load phase table
        if len(Phases) > 0:
            loadPlaxman.update_phase_table(ui, Phases)

        for (i, phase) in enumerate(Phases):
            if not phase['combined_phase'] and phase['phase_name'] == 'Wall construction':
                plaxis2d_input.add_phase_wall_construction(plaxis2d_input_file, prefix, phase)
                pathpatches = []
                for lineload in Lineloads:
                    plot_canvas.set_color(lineload['pathpatches'], 'blue')
                    pathpatches.append(lineload['pathpatches'])
                for pointload in Pointloads:
                    plot_canvas.set_color(pointload['pathpatches'], 'blue')
                    pathpatches.append(pointload['pathpatches'])
                for wall in Walls:
                    plot_canvas.set_color(wall['pathpatches'][0], wall['color'][0])
                    plot_canvas.set_color(wall['pathpatches'][1], wall['color'][1])
                    plot_canvas.set_color(wall['pathpatches'][2], wall['color'][2])
                    plot_canvas.set_color(wall['pathpatches'][3], wall['color'][3]) # annotation
                    pathpatches.append(wall['pathpatches'])
                phase['pathpatches'] = pathpatches

            elif not phase['combined_phase'] and phase['phase_name'] == 'Excavation':
                plaxis2d_input.add_phase_excavation(plaxis2d_input_file, prefix, phase, Phases[i-1])
                pathpatches = []
                for soilcluster in Soilclusters:
                    if soilcluster['id'] in phase['soilcluster_ids']:
                        #plot_canvas.set_color(soilcluster['pathpatches'], 'grey')
                        plot_canvas.set_color_excavated_soilcluster(soilcluster['pathpatches'])
                        pathpatches.append(soilcluster['pathpatches'])
                phase['pathpatches'] = pathpatches

            elif not phase['combined_phase'] and phase['phase_name'] == 'Anchoring':
                plaxis2d_input.add_phase_anchoring(plaxis2d_input_file, prefix, phase, Phases[i-1])
                pathpatches = []
                for anchor in Anchors:
                    if anchor['id'] in phase['anchor_ids']:
                        plot_canvas.set_color(anchor['pathpatches'][0], 'black')
                        plot_canvas.set_color(anchor['pathpatches'][1], 'magenta')
                        plot_canvas.set_color(anchor['pathpatches'][2], 'black') # annotation
                        pathpatches.append(anchor['pathpatches'])
                phase['pathpatches'] = pathpatches

            elif not phase['combined_phase'] and phase['phase_name'] == 'Strut/slab construction':
                plaxis2d_input.add_phase_strut_construction(plaxis2d_input_file, prefix, phase, Phases[i-1])
                pathpatches = []
                for strut in Struts:
                    if strut['id'] in phase['strut_ids']:
                        if strut['usage'] == 'Strut':
                            #plot_canvas.set_color(strut['pathpatches'], 'black')
                            plot_canvas.set_color(strut['pathpatches'][0], 'black')
                            plot_canvas.set_color(strut['pathpatches'][1], 'black')
                            plot_canvas.set_color(strut['pathpatches'][2], 'black') # annotation
                        else: # slabs
                            #plot_canvas.set_color(strut['pathpatches'], 'orange')
                            plot_canvas.set_color(strut['pathpatches'][0], 'orange')
                            plot_canvas.set_color(strut['pathpatches'][1], 'orange')
                            plot_canvas.set_color(strut['pathpatches'][2], 'black') # annotation
                        pathpatches.append(strut['pathpatches'])
                phase['pathpatches'] = pathpatches

            elif not phase['combined_phase'] and phase['phase_name'] == 'Strut deconstruction':
                plaxis2d_input.add_phase_strut_deconstruction(plaxis2d_input_file, prefix, phase, Phases[i-1])
                pathpatches = []
                for strut in Struts:
                    if strut['id'] in phase['strut_ids']:
                        plot_canvas.set_color(strut['pathpatches'], 'grey')
                        pathpatches.append(strut['pathpatches'])
                phase['pathpatches'] = pathpatches

            elif not phase['combined_phase'] and phase['phase_name'] == 'Dewatering (lowering water level)':
                if phase['soilcluster_ids_porepressure_interpolation'] is not None:
                    plaxis2d_input.add_phase_dewatering1_porepressure_interpolation(plaxis2d_input_file, 'g_i', phase, Phases[i-1])
                else:
                    plaxis2d_input.add_phase_dewatering1(plaxis2d_input_file, prefix, phase, Phases[i-1])

            elif not phase['combined_phase'] and phase['phase_name'] == 'Dewatering (lowering drain head)':
                plaxis2d_input.add_phase_dewatering2(plaxis2d_input_file, prefix, phase, Phases[i-1], Drain['id'])
                ui.lineEdit_8.setText(str(phase['drain_head']))

            elif not phase['combined_phase'] and phase['phase_name'] == 'Dewatering (Steady state groundwater flow)':
                plaxis2d_input.add_phase_dewatering2(plaxis2d_input_file, prefix, phase, Phases[i-1], phase['water_level_id'])
                    
            elif not phase['combined_phase'] and phase['phase_name'] == 'FoS':
                plaxis2d_input.add_phase_safety(plaxis2d_input_file, 'g_i', phase, Phases[i-1])
            
            elif phase['combined_phase'] is True:   # This is a combined phase
                loadPlaxman.load_combined_phase(plaxis2d_input_file, i, phase, Phases[i-1])

                ## replot
                #for group_i, pathpatchgroup in enumerate(phase['pathpatches']):
                #    #print('pathpatchgroup', pathpatchgroup)
                #    #print(pathpatchgroup[1].get_facecolor())
                #    plot_canvas.set_colors2(pathpatchgroup, phase['pathpatch_colors_current'][group_i])
                #    #plot_canvas.set_color(pathpatchgroup[0], 'blue')

                pathpatches = []
                for wall in Walls:
                    if wall['id'] in phase['wall_ids_activate']:
                        plot_canvas.set_color(wall['pathpatches'][0], wall['color'][0])
                        plot_canvas.set_color(wall['pathpatches'][1], wall['color'][1])
                        plot_canvas.set_color(wall['pathpatches'][2], wall['color'][2])
                        pathpatches.append(wall['pathpatches'])
                    if wall['id'] in phase['wall_ids_deactivate']:
                        plot_canvas.set_color(wall['pathpatches'], 'grey')
                        pathpatches.append(wall['pathpatches'])

                for lload in Lineloads:
                    if lload['id'] in phase['lload_ids_activate']:
                        plot_canvas.set_color(lload['pathpatches'], 'blue')
                        pathpatches.append(lload['pathpatches'])
                    if lload['id'] in phase['lload_ids_deactivate']:
                        plot_canvas.set_color(lload['pathpatches'], 'grey')
                        pathpatches.append(lload['pathpatches'])

                for pload in Pointloads:
                    if pload['id'] in phase['pload_ids_activate']:
                        plot_canvas.set_color(pload['pathpatches'], 'blue')
                        pathpatches.append(pload['pathpatches'])
                    if pload['id'] in phase['pload_ids_deactivate']:
                        plot_canvas.set_color(pload['pathpatches'], 'grey')
                        pathpatches.append(pload['pathpatches'])

                for scluster in Soilclusters:
                    if scluster['id'] in phase['scluster_ids_activate']:
                        plot_canvas.set_color(scluster['pathpatches'], 'black')
                        pathpatches.append(scluster['pathpatches'])
                    if scluster['id'] in phase['scluster_ids_deactivate']:
                        #plot_canvas.set_color(scluster['pathpatches'], 'grey')
                        plot_canvas.set_color_excavated_soilcluster(scluster['pathpatches'])
                        pathpatches.append(scluster['pathpatches'])

                for anchor in Anchors:
                    if anchor['id'] in phase['anchor_ids_activate']:
                        plot_canvas.set_color(anchor['pathpatches'][0], 'black')
                        plot_canvas.set_color(anchor['pathpatches'][1], 'magenta')
                        pathpatches.append(anchor['pathpatches'])
                    if anchor['id'] in phase['anchor_ids_deactivate']:
                        plot_canvas.set_color(anchor['pathpatches'], 'grey')
                        pathpatches.append(anchor['pathpatches'])

                for strut in Struts:
                    if strut['id'] in phase['strut_ids_activate']:
                        plot_canvas.set_color(strut['pathpatches'], 'black')
                        pathpatches.append(strut['pathpatches'])
                    if strut['id'] in phase['strut_ids_deactivate']:
                        plot_canvas.set_color(strut['pathpatches'], 'grey')
                        pathpatches.append(strut['pathpatches'])

                phase['pathpatches'] = pathpatches


            ui.comboBox_31.addItem(str(i+1))    # in Plaxman's FEM data selection
            ui.comboBox_21.addItem(str(i+1))    # in Backman's FEM data selection
            #ui.comboBox_26.addItem(str(i+1))    # in Sensiman's FEM data selection


    @staticmethod
    def list_phase_options_in_comboboxes(ui):
        """ Put phase options back to combobox lists
        """
        calc_types = ['Plastic', 'Consolidation']
        loading_types = ['Staged construction', 'Minimum excess pore pressure']
        pore_pressure_types = ['Phreatic', 'Steady state groundwater flow']
        predefined_phase_names = ['Wall construction', 'Excavation', 'Anchoring', 'Strut construction', 
                                'Dewatering (lowering water level)', 'Dewatering (lowering drain head)']
        for ct in calc_types:
            ui.comboBox_11.addItem(ct) 
            ui.comboBox_24.addItem(ct) 
        for lt in loading_types:
            ui.comboBox_43.addItem(lt) 
            ui.comboBox_46.addItem(lt) 
        for ppt in pore_pressure_types:
            ui.comboBox_12.addItem(ppt) 
            ui.comboBox_25.addItem(ppt) 
        for phasename in predefined_phase_names:
            ui.comboBox_10.addItem(phasename) 

    @staticmethod
    def load_combined_phase(plaxis2d_input_file, phasenumber, phase, previous_phase):
        """ Loads a combined phase
        """
        # add combined phase information
        if phasenumber > 0:
            plaxis2d_input.add_combined_phase_info(plaxis2d_input_file, 'g_i', phase, previous_phase)
        else:
            plaxis2d_input.add_combined_phase_info_initialphase(plaxis2d_input_file, 'g_i', phase)

        # walls and loads
        plaxis2d_input.add_combined_phase_walls(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_lineloads(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_pointloads(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_soilclusters(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_waterlevels(plaxis2d_input_file, 'g_i', phase)
        if phase['drain_id'] is not None:
            plaxis2d_input.add_combined_phase_drain(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_anchors(plaxis2d_input_file, 'g_i', phase)
        plaxis2d_input.add_combined_phase_struts(plaxis2d_input_file, 'g_i', phase)


    @staticmethod
    def update_phase_table(ui, Phases):
        """ Update the table of phases
        """
        column_items = ['phase_id', 'phase_name', 'deform_calc_type', 'pore_pres_calc_type', 'loading_type', 'time_interval', 'water_level_id']
        row_number = len(Phases)
        column_number = len(column_items)
        ui.tableWidget_2.setRowCount(row_number)
        ui.tableWidget_2.setColumnCount(column_number)
        ui.tableWidget_2.setHorizontalHeaderLabels(column_items)
        for i in range(len(Phases)):
            for j in range(len(column_items)):
                ui.tableWidget_2.setItem(i, j,  QtWidgets.QTableWidgetItem(str(Phases[i][column_items[j]])))
                pass


    @staticmethod
    def add_observed_points(ui, plot_canvas, plaxis2d_input_file, prefix, Points_obs):
        """ Reconstruct observed points (for sensitivity and back-analysis)
        """
        observed_types = ['WallUx', 'WallUy', 'WallHoopForce', 'WallNxMQ_Envelope', 'SoilUx', 'SoilUy', 'AnchorForce', 'StrutForce', 'FoS']
        for ot in observed_types:
            ui.comboBox_30.addItem(ot) 
            ui.comboBox_20.addItem(ot) 

        for num_set, points_set in enumerate(Points_obs):
            plaxis2d_input.add_observed_points(plaxis2d_input_file, prefix, points_set)
            points_set['pathpatches'] = plot_canvas.plot_points(points_set['points'], 'red')

            # reconstruct table of observed points
            ui.tableWidget_6.setRowCount(len(Points_obs))
            max_column = max([item['num_points'] for item in Points_obs])
            ui.tableWidget_6.setColumnCount(max_column)
            points_label = ['P' + str(pntnumber + 1) for pntnumber in range(max_column)]
            ui.tableWidget_6.setHorizontalHeaderLabels(points_label)
            #sets_label = ['Obs. set ' + str(setnumber + 1) for setnumber in range(len(Points_obs))]
            #ui.tableWidget_6.setVerticalHeaderLabels(sets_label)

            labels = []
            for (i, points_set) in enumerate(Points_obs):
                label = 'Obs. set {0}: Type {1}, Phase {2}'.format(i+1, points_set['obs_type'], points_set['obs_phase'])
                labels.append(label)
                for (j, pnt) in enumerate(points_set['points']):
                    ui.tableWidget_6.setItem(i, j, QtWidgets.QTableWidgetItem(str(pnt[0]) + ', ' + str(pnt[1])))

            if labels:
                ui.tableWidget_6.setVerticalHeaderLabels(labels)

            # set text back to GUI
            ui.lineEdit_46.setText(str(points_set['num_points']))
            #ui.lineEdit_44.setText(str(points_set['point1'][0]) + ', ' + str(points_set['point1'][1]))
            #ui.lineEdit_45.setText(str(points_set['point2'][0]) + ', ' + str(points_set['point2'][1]))

            #ui.comboBox_23.addItem('Obs. set ' + str(num_set+1))    # in Backman
    

    @staticmethod
    def add_active_earthpressure_wedge(ui, plot_canvas, active_earth_pressure_wedge):
        """ Adds the active earth pressure wedge
        """
        if active_earth_pressure_wedge:
            active_earth_pressure_wedge['pathpatches'] = plot_canvas.plot_multilinear_earth_pressure_wedge(active_earth_pressure_wedge['points'])
