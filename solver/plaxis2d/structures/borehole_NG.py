# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 14:06:48 2018

@author: nya
"""
import sys
sys.path.append(r'C:\Users\nya\Packages\Moniman')

from solver.plaxis2d.structures.base import Structure

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication

class Borehole(Structure):

    def __init__(self, x = 0, Head = 0):
        self.x = x
        self.Head = Head
        super().__init__()

    
    def get_gui_values(self, UI):
        x = float(UI.lineEdit_5.text())
        Head = float(UI.lineEdit_6.text())
        self.gui_values['x'] = x
        self.gui_values['Head'] = Head
                       
        return (x, Head)
    
    def add_borehole(self, UI, Dialog, Boreholes, Layer_polygons, plot_canvas, plaxis2d_input, plaxis2d_input_file):
        """ Adds a borehole with defined structural properties to model
        """
        # UI is the MainWindow, Boreholes is list of all created Borehole()
        # plaxis2d_input is to store the generated Plaxis2D Python model
        UI.pushButton_4.setEnabled(True)
        UI.pushButton_12.setEnabled(True)
        
        if len(Layer_polygons) > 0:
            Dialog.show_message_box('Warning', 'Please remove all soil layers first!')
        else:
            # Add a borehole
            if len(Boreholes) < 5:
                x = float(UI.lineEdit_5.text())
                Head = float(UI.lineEdit_6.text())
                
                # Check against co-located boreholes
                x_coords = [borehole.x for borehole in Boreholes]
                if x not in x_coords:
                    y_min = float(UI.lineEdit_2.text())
                    y_max = float(UI.lineEdit_4.text())
                                    
                    print('y_min: {}, y_max: {}'.format(y_min, y_max))

                    #UI.comboBox_3.addItem('Borehole ' + str(self.NUMBER_borehole))
                    item = UI.tableWidget.verticalHeaderItem(0)
                    
                    #[method_name for method_name in dir(item) if callable(getattr(item, method_name))]
                    
                    print('item: ', item)
                    
                    item.setText(QCoreApplication.translate("MainWindow", "Layer 1"))
                    item_number = 2*(len(Boreholes) - 1)
                    item = UI.tableWidget.horizontalHeaderItem(item_number)
                    item.setText(QCoreApplication.translate("MainWindow", "BH" + str(len(Boreholes)) + " - Top"))
                    item = UI.tableWidget.horizontalHeaderItem(item_number + 1)
                    item.setText(QCoreApplication.translate("MainWindow", "BH" + str(len(Boreholes)) + " - Bottom"))
                    
                    # Suggest initial top and botom levels at boreholes for the first soil layer
                    UI.tableWidget.setItem(0, 2*(len(Boreholes) - 1), QtWidgets.QTableWidgetItem(str(y_max)))
                    UI.tableWidget.setItem(0, 2*(len(Boreholes) - 1) +1 , QtWidgets.QTableWidgetItem(str(y_min)))
                    
                    pathpatches = plot_canvas.plot_borehole(len(Boreholes), x, Head, y_min, y_max)
                    
                     # Add the new borehole item for later soil layer creation
                    self.x = x
                    self.Head = Head
                    self.pathpatch = pathpatches
                    Boreholes.append(self)
                    
                    plaxis2d_input.add_borehole(plaxis2d_input_file, 'g_i', len(Boreholes), self.x, self.Head)
                    
                    print('New borehole is added at x = {}\n'.format(self.x))
    
                
                else:
                    Dialog.show_message_box('Warning', 'Borehole position is repeated, please modify!')
                
            else: 
                Dialog.show_message_box('Warning', 'Only up to 5 boreholes are allowed at the moment!')
                
        #return Borehole(x, Head)
    
    def create_borehole(self, GUI, Dialog, Boreholes, Layer_polygons, plaxis2d_input, plaxis2d_input_file):
        GUI.ui.pushButton_4.setEnabled(True)
        GUI.ui.pushButton_12.setEnabled(True)
        if len(Layer_polygons) > 0:
            Dialog.show_message_box('Warning', 'Please remove all soil layers first!')
        else:
            # Add a borehole
            if len(Boreholes) < 5:
                x = float(GUI.ui.lineEdit_5.text())
                Head = float(GUI.ui.lineEdit_6.text())
                
                # Check against co-located boreholes
                x_coords = [borehole['x'] for borehole in self.Boreholes]
                if x not in x_coords:
                    y_min = float(GUI.ui.lineEdit_2.text())
                    y_max = float(GUI.ui.lineEdit_4.text())
                    
                    # Add the new borehole item for later soil layer creation
                    new_borehole = {'x': x, 'Head': Head}
                    self.Boreholes.append(new_borehole)
                    #UI.comboBox_3.addItem('Borehole ' + str(self.NUMBER_borehole))
                    item = GUI.ui.tableWidget.verticalHeaderItem(0)
                    item.setText(QCoreApplication.translate("MainWindow", "Layer 1"))
                    item_number = 2*(len(Boreholes) - 1)
                    item = GUI.ui.tableWidget.horizontalHeaderItem(item_number)
                    item.setText(QCoreApplication.translate("MainWindow", "BH" + str(len(Boreholes)) + " - Top"))
                    item = GUI.ui.tableWidget.horizontalHeaderItem(item_number + 1)
                    item.setText(QCoreApplication.translate("MainWindow", "BH" + str(len(Boreholes)) + " - Bottom"))
                    
                    # Suggest initial top and botom levels at boreholes for the first soil layer
                    GUI.ui.tableWidget.setItem(0, 2*(len(Boreholes) - 1), QtWidgets.QTableWidgetItem(str(y_max)))
                    GUI.ui.tableWidget.setItem(0, 2*(len(Boreholes) - 1) +1 , QtWidgets.QTableWidgetItem(str(y_min)))
                    
                    new_borehole['pathpatches'] = GUI.plot_canvas.plot_borehole(len(Boreholes), x, Head, y_min, y_max)
                    
                    plaxis2d_input.add_borehole(plaxis2d_input_file, 'g_i', len(Boreholes), new_borehole['x'], new_borehole['Head'])
                    
                    print('New borehole is added at x = {}\n'.format(new_borehole['x']))
    
                
                else:
                    Dialog.show_message_box('Warning', 'Borehole position is repeated, please modify!')
                
            else: 
                Dialog.show_message_box('Warning', 'Only up to 5 boreholes are allowed at the moment!')
                
                
    def remove(self):
        """ Removes the last borehole
        """
        
#if __name__ == '__main__':
#    UI = Ui_MainWindow()
#    UI.setupUi(QtWidgets.QMainWindow())        
#        
#    bh = Borehole() 
#    bh.plot()
#    bh.get_gui_values(UI)
#    bh.print_gui_values()
#    