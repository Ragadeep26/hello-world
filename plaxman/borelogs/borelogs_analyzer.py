# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 11:40:58 2020

@author: nya
"""
import os
import sys
import copy
import numpy as np
from scipy import interpolate
from itertools import combinations
from collections import OrderedDict
from tools.math import calc_dist_2p
from scipy.interpolate import griddata
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt
sys.path.insert(0, os.path.abspath(r'C:\Users\nya\Packages\Moniman'))   # for testing
from gui.gui_widget_Borelogs import Ui_Form as BorelogsForm
from mpl_toolkits import mplot3d
from gui.gui_main_matplotlib import MyStaticMplCanvas3D
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.gui_all_dialogs_ui import Ui_Dialog

class Borelogs_Analyzer(QtWidgets.QWidget):
    """ This class implements the borelog analyzer
    """
    def __init__(self, form, borehole, layers):
        """ Initializes borelog analyzer
        """
        super(Borelogs_Analyzer, self).__init__()
        self.ui = BorelogsForm()
        self.ui.setupUi(form)
        self.ui.splitter.setSizes([500, 500]) # resize widgets' size around splitter
        self.dialog = Ui_Dialog()

        # plot canvas
        self.plot_layout = QtWidgets.QVBoxLayout(self.ui.widget)
        self.plot_canvas = MyStaticMplCanvas3D(self.ui.widget, width=1, height=1, dpi=100)
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_toolbar = NavigationToolbar(self.plot_canvas, None)        
        self.plot_layout.addWidget(self.plot_toolbar)

        # reference borelog
        self.borelog_ref = borehole
        self.borelogs = []
        self.layers = layers    # defined layer polygons in Plaxman


        # connect signals
        self.connect_signals_to_slots()

        form.exec_()


    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.ui.pushButton.clicked.connect(self.add_borelog)
        self.ui.treeWidget.itemChanged.connect(lambda item, column: self.update_borelog(item, column))
        self.ui.pushButton_2.clicked.connect(self.remove_borelog)
        self.ui.pushButton_3.clicked.connect(self.interpolate_and_plot_layers)


    def add_borelog(self):
        """ Adds a borelog
        """
        try:
            x = float(self.ui.lineEdit.text().split(',')[0])
            y = float(self.ui.lineEdit.text().split(',')[1])
            Head = float(self.ui.lineEdit_2.text())
            borelog_new = Borelog(x, Head, copy.copy(self.borelog_ref['Top']), copy.copy(self.borelog_ref['Bottom']), y)

            self.borelogs.append(borelog_new)
            self.list_borelogs()
            self.plot_borelogs()

        except ValueError:
            self.dialog.show_message_box('Warning', 'Please check if the values are correctly entered')


    def remove_borelog(self):
        """ Removes a borelog
        """
        if len(self.borelogs) > 0:
            self.borelogs.pop()
            self.list_borelogs()
            if len(self.borelogs) == 0:
                self.plot_canvas.clear_canvas()
            else:
                self.plot_borelogs()

    
    def list_borelogs(self):
        """ Lists all borelogs on the treeeWidget
        """
        self.ui.treeWidget.blockSignals(True)
        self.ui.treeWidget.clear()
        for i, borelog in enumerate(self.borelogs):
            self.ui.treeWidget.setColumnCount(7)
            # add root
            #item = QtWidgets.QTreeWidgetItem(['Borelog {0}, GW {1}'.format(str(i+1), borelog.position['Head']) , 'Soil', 'Top', 'Bottom'])
            item = QtWidgets.QTreeWidgetItem(['Borelog ' + str(i+1), 'X', 'Y', 'GW level', 'Soil', 'Top', 'Bottom'])
            self.ui.treeWidget.addTopLevelItem(item)
            self.ui.treeWidget.expandItem(item) # expand children of this item
    
            # add children
            layer_i = 0
            for top, bottom in zip(borelog.tops, borelog.bottoms):
                if layer_i == 0:
                    child = QtWidgets.QTreeWidgetItem(['', str(borelog.position['x']), str(borelog.position['y']), str(borelog.position['Head']),  self.layers[layer_i]['soilmaterial_layer'], str(top), str(bottom)])
                    child.setBackground(1, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(2, QBrush(QColor(242, 255, 116))) # light yellow
                    child.setBackground(3, QBrush(QColor(242, 255, 116))) # light yellow
                else:
                    child = QtWidgets.QTreeWidgetItem(['', '', '', '', self.layers[layer_i]['soilmaterial_layer'], str(top), str(bottom)])
                item.addChild(child)
                child.setBackground(4, QBrush(QColor(self.layers[layer_i]['color']))) # soil color
                child.setBackground(5, QBrush(QColor(242, 255, 116))) # light yellow
                child.setBackground(6, QBrush(QColor(242, 255, 116))) # light yellow
                child.setFlags(child.flags() | Qt.ItemIsEditable) 
                layer_i += 1

        self.ui.treeWidget.blockSignals(False)


    def update_borelog(self, item, column):
        """ Updates GW level/ Top/ Bottom of a borelog
        """
        value = float(item.text(column))
        bl_text = item.parent().text(0)  # e.g. 'Borelog 1'
        bl_num = int(bl_text.split()[1]) - 1 # borelog number
        if column == 1: # position x
            self.borelogs[bl_num].position['x'] = value
        elif column == 2: # position x
            self.borelogs[bl_num].position['y'] = value
        elif column == 3: # GW level
            self.borelogs[bl_num].position['Head'] = value
        elif column == 5: # Top
            tops = [float(item.parent().child(i).text(column)) for i in range(len(self.borelogs[bl_num].tops))]
            self.borelogs[bl_num].tops = tops
            # change bottom of the upper layer accordingly
            self.ui.treeWidget.blockSignals(True)
            self.update_bottoms_according_to_tops(bl_num)
            self.ui.treeWidget.blockSignals(False)
        elif column == 6: # Bottom
            bottoms = [float(item.parent().child(i).text(column)) for i in range(len(self.borelogs[bl_num].bottoms))]
            self.borelogs[bl_num].bottoms = bottoms
            self.ui.treeWidget.blockSignals(True)
            self.update_tops_according_to_bottoms(bl_num)
            self.ui.treeWidget.blockSignals(False)

        # replot all borelogs
        self.plot_borelogs()


    def update_bottoms_according_to_tops(self, bl_num):
        """ Set bottoms of upper layers equal to tops of lower layers
        bl_num: borelog number
        """
        for layer_i in range(1, len(self.layers)):
            if self.borelogs[bl_num].bottoms[layer_i-1] != self.borelogs[bl_num].tops[layer_i]:
                self.borelogs[bl_num].bottoms[layer_i-1] = self.borelogs[bl_num].tops[layer_i]
        # list borelogs
        self.list_borelogs()


    def update_tops_according_to_bottoms(self, bl_num):
        """ Set bottoms of upper layers equal to tops of lower layers
        bl_num: borelog number
        """
        for layer_i in range(0, len(self.layers)-1):
            if self.borelogs[bl_num].tops[layer_i+1] != self.borelogs[bl_num].bottoms[layer_i]:
                self.borelogs[bl_num].tops[layer_i+1] = self.borelogs[bl_num].bottoms[layer_i]
        # list borelogs
        self.list_borelogs()


    def plot_borelogs(self):
        """ Plots borelogs
        """
        # clear canvas
        self.plot_canvas.clear_canvas()

        # replot all borelogs
        radius = max(0.1, 0.05 * self.get_max_distance_borelogs())
        for borelog in self.borelogs:
            self.plot_canvas.plot_borelog(borelog, radius, self.layers)


    def get_max_distance_borelogs(self):
        """ Gets maximum distance between available borelogs
        """
        borelog_pairs = combinations(self.borelogs, 2)
        dmax = 0.0
        for borelog_pair in list(borelog_pairs):
            x1 = borelog_pair[0].position['x']
            y1 = borelog_pair[0].position['y']
            x2 = borelog_pair[1].position['x']
            y2 = borelog_pair[1].position['y']
            d = calc_dist_2p((x1, y1), (x2, y2))
            dmax = max(dmax, d)

        return dmax


    def interpolate_and_plot_layers(self):
        """ Interpolates and plots all layers
        """
        for i, layer in enumerate(self.layers):
            gridx, gridy, gridz = self.interpolate_soil_layer(i)
            self.plot_canvas.plot_interpolated_layer(gridx, gridy, gridz)



    def interpolate_soil_layer(self, layer_i):
        """ Interpolates interfaced soil layer from borelogs
        layer_i: the ith layer
        """
        # get data
        points_layer_i = []
        elevations_layer_i = []
        for borelog in self.borelogs:
            x  = borelog.position['x']
            y  = borelog.position['y']
            z  = borelog.tops[layer_i]
            points_layer_i.append((x, y))
            elevations_layer_i.append(z)

        ## create interpolation grid
        x_min = min(point[0] for point in points_layer_i)
        x_max = max(point[0] for point in points_layer_i)
        y_min = min(point[1] for point in points_layer_i)
        y_max = max(point[1] for point in points_layer_i)
        margin = 20
        gridx, gridy = np.mgrid[x_min - margin : x_max + margin : 50j, y_min - margin: y_max + margin : 50j]
        # interpolate
        method = self.ui.comboBox.currentText()
        gridz = griddata(points_layer_i, elevations_layer_i, (gridx, gridy), method=method)
        #print(gridz)

        return gridx, gridy, gridz



class Borelog():
    """ This class implements the Borelog
    """
    def __init__(self, x, Head, top, bottom, y=0):
        self.position = {'x': x, 'Head': Head, 'y': y}
        self.tops = top
        self.bottoms = bottom



if __name__ == '__main__':
    """ Testing
    """
    app = QtWidgets.QApplication(sys.argv)        
    form = QtWidgets.QDialog()
    Borelogs_Analyzer(form)
    #form.show()
    sys.exit(app.exec_()) 