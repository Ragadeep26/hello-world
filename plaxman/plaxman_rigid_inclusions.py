# -*- coding: utf-8 -*-
"""
Created on Fri May 22 13:16:55 2020

@author: nya
"""

import os, sys
import csv, io
import json
import numpy as np
import pandas as pd
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtCore import pyqtSlot, QEvent
from tools.math import hex_to_rgb
from tools.json_functions import read_data_in_json_item
from gui.gui_main_matplotlib import MyStaticMplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.gui_form_CMC import Ui_Form as FormFDC
from plaxman.rigid_inclusions.load_and_ltp import FDC_Loading
from plaxman.rigid_inclusions.load_and_ltp import LTP_calc
from plaxman.rigid_inclusions.rigid_inclusions_arg.Calculaxi_arg import Calcul_Click, get_unreinforced_soil_settlement
from gui.gui_widget_FDC_SoilClusters_ui import Ui_Dialog as FDCSoilClusters

class FDC():
    """ This class impements the full displacemetn column rigid inclusions
    """
    def __init__(self, Layer_polygons, borehole, top=0, Lc=4.0, H_lim=8.0, Dc=0.44, a=2.0, fck=20.0, pl=1700.0, Em=15000, alpha=0.33, nu=0.3, Ey=45000, user_input_E_s=False,
                alpha_cc=0.7, gammaC=1.5, kp = 1880.0, kq=4.8, Emp=3300.0, pl_anchorage_plus50cm=0.0, pl_anchorage_minus150cm=0.0,
                G=60.0, Q=40.0, gammaG=1.35, gammaQ=1.5,        # loading parameters
                hM=0.4, phi=38.0, c=0.0, s_q=1.0, s_c=1.3, nabla=105.0, gammaR=1.0, q_s=0.0, gammaSat=20.0, k_t=0.8, Ktand=1.0, Eoed=0.0, isMenard=False, **kwargs):     # LPT parameters
        self.FDC_params = OrderedDict()
        self.FDC_params['top'] = top
        self.FDC_params['Lc'] = Lc
        self.FDC_params['H_lim'] = H_lim
        self.FDC_params['Dc'] = Dc
        self.FDC_params['a'] = a
        self.FDC_params['fck'] = fck
        self.FDC_params['alpha_cc'] = alpha_cc
        self.FDC_params['gammaC'] = gammaC
        self.FDC_params['user_input_E_s'] = user_input_E_s   # user input constrained modulus (Oedometer modulus)
        #self.LTP_params = {'h': 0.4, 'pl': 1700.0, 'Em': 15000, 'alpha': 0.33, 'nu':0.3, 'Ey':45000}   # load transfer platform
        self.LTP_params = OrderedDict()
        self.LTP_params['hM'] = hM      # LTP thickness
        self.LTP_params['phi'] = phi    # angle of internal friction of LTP material
        self.LTP_params['c'] = c        # cohesion of LTP material
        self.LTP_params['s_q'] = s_q    # Prandlt shape parameter
        self.LTP_params['s_c'] = s_c    # Prandlt shape parameter
        self.LTP_params['nabla'] = nabla    # LTP parameter
        self.LTP_params['gammaR'] = gammaR    # LTP parameter
        self.LTP_params['pl'] = pl
        self.LTP_params['Em'] = Em
        self.LTP_params['alpha'] = alpha
        self.LTP_params['nu'] = nu
        self.LTP_params['Ey'] = Ey
        self.LTP_params['q_s'] = q_s        #!
        self.LTP_params['gammaSat'] = gammaSat   #!
        self.LTP_params['k_t'] = k_t   #!
        self.LTP_params['Ktand'] = Ktand   #!
        self.LTP_params['Eoed'] =  Ey*(1-nu)/((1+nu)*(1-2*nu)) #!
        self.LTP_params['isMenard'] = isMenard

        self.anchorage_params = {} # soil parameters at anchorage
        self.anchorage_params['kp'] = kp
        self.anchorage_params['kq'] = kq
        self.anchorage_params['Emp'] = Emp
        self.anchorage_params['pl_anchorage_plus50cm'] = pl_anchorage_plus50cm
        self.anchorage_params['pl_anchorage_minus150cm'] = pl_anchorage_minus150cm

        self.Layer_polygons = Layer_polygons
        self.borehole = borehole
        self.database_soiltype = None   # soil type dependent database
        self.database_soiltype_qp_kq = None   # soil type dependent qp, kq
        self.database_soiltype, self.database_soiltype_qp_kq = self.read_soiltype_database()    # read in soil type database once
        self.geometry = [borehole['x'], min(borehole['Bottom']), borehole['x'] + 2.0, max(borehole['Top'])] #[x_min, y_min, x_max, y_max]

        self.name = '' # structure name
    
        # Loading
        self.FDC_loading = {}
        self.FDC_loading['G'] = G
        self.FDC_loading['Q'] = Q
        self.FDC_loading['gammaG'] = gammaG
        self.FDC_loading['gammaQ'] = gammaQ
        self.FDC_loading_obj = FDC_Loading(**self.FDC_loading)

        # LPT & soil layer data, will be assembled later before calculation
        self.data = None
        self.Eoed_eff_unreinforced = None   # unreinforced soil Eoed within FDC
        self.matrice = None     # numpy matrix to store the calculation results
        self.Parameteres_below_FDC = None   # to store soil settlement below FDC toe
        self.isPassed = True    # LTP and column bearing capacities are passed or not


    
    def open_edit_rigid_inclusions(self, method, user_structure_name, isdefined=False):
        """ Opens form for defining rigid inclusions
        """
        cmc_box = QtWidgets.QDialog()
        self.ui = FormFDC()
        self.ui.setupUi(cmc_box)
        self.ui.splitter.setSizes([600, 400]) # resize widgets' size around splitter
        # plot canvas for FDC settings
        self.plot_layout = QtWidgets.QVBoxLayout(self.ui.widget)
        self.plot_canvas = MyStaticMplCanvas(self.ui.widget, width=1, height=1, dpi=100)
        self.plot_layout.addWidget(self.plot_canvas)
        # plot canvas for LTP thickness dependent bearing capacity
        self.plot_layout_1 = QtWidgets.QVBoxLayout(self.ui.widget_2)
        self.plot_canvas_1 = MyStaticMplCanvas(self.ui.widget_2, width=1, height=1, dpi=100)
        self.plot_toolbar_1 = NavigationToolbar(self.plot_canvas_1, None)        
        self.plot_layout_1.addWidget(self.plot_toolbar_1)
        self.plot_layout_1.addWidget(self.plot_canvas_1)
        # plot canvas for FDC and soil settlements
        self.plot_layout_2 = QtWidgets.QVBoxLayout(self.ui.widget_3)
        self.plot_canvas_2 = MyStaticMplCanvas(self.ui.widget_3, width=1, height=1, dpi=100)
        self.plot_layout_2.addWidget(self.plot_canvas_2)
        # plot canvas for skin resistance
        self.plot_layout_3 = QtWidgets.QVBoxLayout(self.ui.widget_4)
        self.plot_canvas_3 = MyStaticMplCanvas(self.ui.widget_4, width=1, height=1, dpi=100)
        self.plot_layout_3.addWidget(self.plot_canvas_3)
        # plot canvas for SLS vertical loads
        self.plot_layout_4 = QtWidgets.QVBoxLayout(self.ui.widget_5)
        self.plot_canvas_4 = MyStaticMplCanvas(self.ui.widget_5, width=1, height=1, dpi=100)
        self.plot_layout_4.addWidget(self.plot_canvas_4)

        ## soil type dependent parameters
        #if self.database_soiltype is None:  	# read in soil type database once
        #    self.database_soiltype, self.database_soiltype_qp_kq = self.read_soiltype_database()

        # rigid inclusions structure name
        if isdefined:
            ri_name = user_structure_name
        else:
            self.FDC_params['top'] = max(self.borehole['Top']) - self.LTP_params['hM'] # set default top of FDC piles
            self.initialize_soil_layers()
            ri_name = user_structure_name + '_FDC'
        self.name = ri_name 

        self.display_FDC_params()
        self.display_FDC_loading()

        self.display_soil_layers()

        self.plot_FDC()

        # set soil parameters at anchorage
        if not isdefined:
            self.set_soil_params_at_anchorage() # suggest anchorage parameters
        else:
            self.display_anchorage_params()

        self.connect_signals_to_slots()

        # show checkState isMenard
        if self.LTP_params['isMenard']:
            self.ui.checkBox_2.setCheckState(2)

        # show checkState user input Es
        if self.FDC_params['user_input_E_s']:
            self.ui.checkBox_3.setCheckState(2)
        
        cmc_box.exec_()
    

    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        # FDC
        self.ui.lineEdit.setStyleSheet("background-color: rgb(242, 255, 116);\n")       # FDC top
        self.ui.lineEdit.editingFinished.connect(self.update_FDC_top)
        self.ui.lineEdit_2.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC Lc
        self.ui.lineEdit_2.editingFinished.connect(self.update_FDC_length)
        self.ui.lineEdit_3.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC Dc
        self.ui.lineEdit_3.editingFinished.connect(self.update_FDC_diameter)
        self.ui.lineEdit_4.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC a
        self.ui.lineEdit_4.editingFinished.connect(self.update_FDC_spacing)
        self.ui.lineEdit_5.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC f_ck
        self.ui.lineEdit_5.editingFinished.connect(self.update_FDC_f_ck)
        self.ui.lineEdit_27.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC alpha_cc
        self.ui.lineEdit_27.editingFinished.connect(self.update_FDC_alpha_cc)
        self.ui.lineEdit_29.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC gammaC
        self.ui.lineEdit_29.editingFinished.connect(self.update_FDC_gammaC)
        self.ui.lineEdit_31.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # FDC H_lim
        self.ui.lineEdit_31.editingFinished.connect(self.update_FDC_H_lim)

        # user input Es
        self.ui.checkBox_3.stateChanged.connect(lambda state_int: self.update_user_input_E_s(state_int==2))

        # manual update soil resistance at anchorage
        self.ui.lineEdit_8.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # qp
        self.ui.lineEdit_8.editingFinished.connect(self.update_anchorage_qp)
        self.ui.lineEdit_9.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # kq
        self.ui.lineEdit_9.editingFinished.connect(self.update_anchorage_kq)
        self.ui.lineEdit_10.setStyleSheet("background-color: rgb(242, 255, 116);\n")     # Em
        self.ui.lineEdit_10.editingFinished.connect(self.update_anchorage_Em)

        self.ui.lineEdit_11.setStyleSheet("background-color: rgb(242, 255, 116);\n")   #  G
        self.ui.lineEdit_11.editingFinished.connect(self.update_FDC_loading_G)
        self.ui.lineEdit_12.setStyleSheet("background-color: rgb(242, 255, 116);\n")   #  Q
        self.ui.lineEdit_12.editingFinished.connect(self.update_FDC_loading_Q)
        self.ui.lineEdit_13.setStyleSheet("background-color: rgb(242, 255, 116);\n")   #  gammaG
        self.ui.lineEdit_13.editingFinished.connect(self.update_FDC_loading_gammaG)
        self.ui.lineEdit_14.setStyleSheet("background-color: rgb(242, 255, 116);\n")   #  gammaQ
        self.ui.lineEdit_14.editingFinished.connect(self.update_FDC_loading_gammaQ)
        # LTP
        self.ui.lineEdit_15.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # hM
        self.ui.lineEdit_15.editingFinished.connect(self.update_LTP_thickness)
        self.ui.lineEdit_16.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # phi
        self.ui.lineEdit_16.editingFinished.connect(self.update_LTP_phi)
        self.ui.lineEdit_17.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # c
        self.ui.lineEdit_17.editingFinished.connect(self.update_LTP_c)
        self.ui.lineEdit_18.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # s_q
        self.ui.lineEdit_18.editingFinished.connect(self.update_LTP_s_q)
        self.ui.lineEdit_19.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # s_c
        self.ui.lineEdit_19.editingFinished.connect(self.update_LTP_s_c)
        self.ui.lineEdit_25.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # nabla
        self.ui.lineEdit_25.editingFinished.connect(self.update_LTP_nabla)
        self.ui.lineEdit_26.setStyleSheet("background-color: rgb(242, 255, 116);\n")    # gammaR
        self.ui.lineEdit_26.editingFinished.connect(self.update_LTP_gammaR)
        self.ui.checkBox_2.stateChanged.connect(self.update_LTP_isMenard)    # isMenard?

        # update q_s, Ey
        self.ui.tableWidget.cellChanged.connect(lambda row, col: self.update_soillayer_qs(row, col)) # 
        self.ui.tableWidget.cellChanged.connect(lambda row, col: self.update_soillayer_Ey(row, col)) #  
        self.ui.tableWidget.cellChanged.connect(lambda row, col: self.update_soillayer_nu(row, col)) #  
        self.ui.tableWidget.cellChanged.connect(lambda row, col: self.update_soillayer_alpha(row, col)) #  
        self.ui.tableWidget.cellChanged.connect(lambda row, col: self.update_soillayer_Eoed_user(row, col)) #  update user input Eoed

        # assemble data
        self.ui.pushButton.clicked.connect(lambda: self.assemble_data(show=True))

        # calculate
        self.ui.pushButton_2.clicked.connect(lambda: self.calculate(show=True))

        # show unreinforced soil settlement on graph or not
        self.ui.checkBox.stateChanged.connect(self.update_settlements_graph)


    def display_FDC_params(self):
        """ Displays FDC parameters
        """
        self.ui.lineEdit.setText(str(self.FDC_params['top']))
        self.ui.lineEdit_2.setText(str(self.FDC_params['Lc']))
        self.ui.lineEdit_3.setText(str(self.FDC_params['Dc']))
        self.ui.lineEdit_4.setText(str(self.FDC_params['a']))
        self.ui.lineEdit_5.setText(str(self.FDC_params['fck']))
        self.ui.lineEdit_27.setText(str(self.FDC_params['alpha_cc']))
        self.ui.lineEdit_29.setText(str(self.FDC_params['gammaC']))
        self.ui.lineEdit_31.setText(str(self.FDC_params['H_lim']))

        # ultimate FDC compression
        f_ck = self.FDC_params['fck']
        alpha_cc = self.FDC_params['alpha_cc']
        gammaC = self.FDC_params['gammaC']
        f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
        self.FDC_params['fcd'] = f_cd
        Ec = self.get_FDC_Ecm(f_ck)
        self.ui.lineEdit_23.setText('{:.2f}'.format(f_cd))
        self.ui.lineEdit_30.setText('{:.2f}'.format(Ec))
    

    def display_anchorage_params(self):
        """ Displays anchorage params
        """
        qp = self.anchorage_params['kp']
        kq = self.anchorage_params['kq']
        Emp = self.anchorage_params['Emp']
        self.ui.lineEdit_8.setText('{:.2f}'.format(qp))
        self.ui.lineEdit_9.setText('{:.2f}'.format(kq))
        self.ui.lineEdit_10.setText('{:.2f}'.format(Emp))

        pl_anchorage_plus50cm = self.anchorage_params['pl_anchorage_plus50cm']
        pl_anchorage_minus150cm = self.anchorage_params['pl_anchorage_minus150cm']
        self.ui.lineEdit_6.setText('{:.2f}'.format(pl_anchorage_plus50cm))
        self.ui.lineEdit_7.setText('{:.2f}'.format(pl_anchorage_minus150cm))
    

    def display_LTP_params(self):
        """ Displays LTP parameters
        """
        self.ui.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem('LTP')) 
        self.ui.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem('LTP')) 
        self.ui.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.LTP_params['hM'])))
        self.ui.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(str(self.FDC_params['top'])))
        self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(str(self.LTP_params['pl']))) 
        self.ui.tableWidget.setItem(0, 5, QtWidgets.QTableWidgetItem(str(self.LTP_params['Em'])))
        self.ui.tableWidget.setItem(0, 6, QtWidgets.QTableWidgetItem(str(self.LTP_params['alpha'])))
        self.ui.tableWidget.item(0, 6).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.setItem(0, 7, QtWidgets.QTableWidgetItem(str(self.LTP_params['nu'])))
        self.ui.tableWidget.item(0, 7).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.setItem(0, 8, QtWidgets.QTableWidgetItem(str(self.LTP_params['Ey'])))
        self.ui.tableWidget.item(0, 8).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.setItem(0, 9, QtWidgets.QTableWidgetItem(str(self.LTP_params['Eoed'])))
        self.ui.tableWidget.setItem(0, 10, QtWidgets.QTableWidgetItem(str(self.LTP_params['q_s'])))
        self.ui.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem(str(self.LTP_params['k_t'])))
        self.ui.tableWidget.setItem(0, 12, QtWidgets.QTableWidgetItem(str(self.LTP_params['Ktand'])))
        self.ui.tableWidget.setItem(0, 13, QtWidgets.QTableWidgetItem(str(self.LTP_params['gammaSat'])))

        # LTP tab
        self.ui.lineEdit_15.setText(str(self.LTP_params['hM']))
        self.ui.lineEdit_16.setText(str(self.LTP_params['phi']))
        self.ui.lineEdit_17.setText(str(self.LTP_params['c']))
        self.ui.lineEdit_18.setText(str(self.LTP_params['s_q']))
        self.ui.lineEdit_19.setText(str(self.LTP_params['s_c']))
        self.get_q_p_and_q_s()
        self.ui.lineEdit_25.setText(str(self.LTP_params['nabla']))
        self.ui.lineEdit_26.setText(str(self.LTP_params['gammaR']))


    def display_FDC_loading(self):
        """ Displays loads and their safety factors
        """
        self.ui.lineEdit_11.setText(str(self.FDC_loading['G']))
        self.ui.lineEdit_12.setText(str(self.FDC_loading['Q']))
        self.ui.lineEdit_13.setText(str(self.FDC_loading['gammaG']))
        self.ui.lineEdit_14.setText(str(self.FDC_loading['gammaQ']))
        p0 = self.FDC_loading_obj.get_q0()
        self.ui.lineEdit_20.setText(str(p0))


    def save_FDC_loading(self):
        """ Saves loads and their safety factors
        """
        self.FDC_loading['G'] = self.FDC_loading_obj.G
        self.FDC_loading['gammaG'] = self.FDC_loading_obj.gammaG
        self.FDC_loading['Q'] = self.FDC_loading_obj.Q
        self.FDC_loading['gammaQ'] = self.FDC_loading_obj.gammaQ


    def plot_FDC(self):
        """ Plots FDC settings
        """
        self.plot_canvas.axes.cla() # clear axis

        self.borehole['pathpatches'] = self.plot_canvas.plot_borehole(1, self.borehole, self.geometry, plot_waterlevel=False)  # plot borehole
        for i, layer_polygon in enumerate(self.Layer_polygons): # plot layers
            layer_polygon['pathpatch_layer'] = self.plot_canvas.plot_assigned_layer(layer_polygon['path_polygon'], layer_polygon['color'])

        self.FDC_params['pathpatches'] = self.plot_canvas.plot_FDC(self.FDC_params, max(self.borehole['Top']))
        self.LTP_params['pathpatches'] = self.plot_canvas.plot_LTP(self.LTP_params, self.FDC_params)

        
    def read_soiltype_database(self):
        """ Reads soiltype database
        """
        cwd = os.path.join(sys.modules['moniman_paths']['MONIMAN'], r'common\databases')
        fname = os.path.join(cwd, 'CMC_database.xlsx')
        data_cmc = pd.read_excel(open(fname, 'rb'), sheetname='CMC_database')      # py34
        data_qp_kq = pd.read_excel(open(fname, 'rb'), sheetname='qp_kq_database')  # py34
        #data_cmc = pd.read_excel(open(fname, 'rb'), sheet_name='CMC_database')      # py37
        #data_qp_kq = pd.read_excel(open(fname, 'rb'), sheet_name='qp_kq_database')  # py37

        return data_cmc, data_qp_kq



    @pyqtSlot()
    def update_FDC_length(self):
        """ Updates FDC length
        """
        try:
            Lc = float(self.ui.lineEdit_2.text())
            self.FDC_params['Lc'] = Lc
            self.plot_FDC()

            # set soil parameters at anchorage
            self.set_soil_params_at_anchorage()

        except:
            pass


    @pyqtSlot()
    def update_FDC_H_lim(self):
        """ Updates limit depth H_lim
        """
        try:
            H_lim = float(self.ui.lineEdit_31.text())
            self.FDC_params['H_lim'] = H_lim

        except:
            pass


    @pyqtSlot()
    def update_FDC_diameter(self):
        """ Updates FDC diameter
        """
        try:
            Dc = float(self.ui.lineEdit_3.text())
            self.FDC_params['Dc'] = Dc
            self.plot_FDC()

        except:
            pass


    @pyqtSlot()
    def update_FDC_spacing(self):
        """ Updates FDC spacing
        """
        try:
            a = float(self.ui.lineEdit_4.text())
            self.FDC_params['a'] = a

        except:
            pass


    @pyqtSlot()
    def update_FDC_f_ck(self):
        """ Updates FDC f_ck
        """
        try:
            f_ck = float(self.ui.lineEdit_5.text())
            self.FDC_params['fck'] = f_ck
            alpha_cc = self.FDC_params['alpha_cc']
            gammaC = self.FDC_params['gammaC']
            f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
            self.FDC_params['fcd'] = f_cd
            Ec = self.get_FDC_Ecm(f_ck)
            self.ui.lineEdit_23.setText('{:.2f}'.format(f_cd))
            self.ui.lineEdit_30.setText('{:.2f}'.format(Ec))

        except:
            pass


    @pyqtSlot()
    def update_FDC_alpha_cc(self):
        """ Updates FDC alpha_cc
        """
        try:
            alpha_cc = float(self.ui.lineEdit_27.text())
            self.FDC_params['alpha_cc'] = alpha_cc
            f_ck = self.FDC_params['fck']
            gammaC = self.FDC_params['gammaC']
            f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
            self.FDC_params['fcd'] = f_cd
            Ec = self.get_FDC_Ecm(f_ck)
            self.ui.lineEdit_23.setText('{:.2f}'.format(f_cd))
            self.ui.lineEdit_30.setText('{:.2f}'.format(Ec))

        except:
            pass
        

    @pyqtSlot()
    def update_FDC_gammaC(self):
        """ Updates FDC gammaC
        """
        try:
            gammaC = float(self.ui.lineEdit_29.text())
            self.FDC_params['gammaC'] = gammaC
            f_ck = self.FDC_params['fck']
            alpha_cc = self.FDC_params['alpha_cc']
            f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
            self.FDC_params['fcd'] = f_cd
            Ec = self.get_FDC_Ecm(f_ck)
            self.ui.lineEdit_23.setText('{:.2f}'.format(f_cd))
            self.ui.lineEdit_30.setText('{:.2f}'.format(Ec))

        except:
            pass


    def get_FDC_f_cd(self, f_ck, alpha_cc, gammaC):
        """ Gets ULS average compressive stress allowable by FDC material, max 7 MPa
        f_ck: concrete unconfined compressive strength after 28 days
        """
        f_cd = alpha_cc*f_ck/gammaC
        return f_cd


    def get_FDC_Ecm(self, f_ck):
        """ Gets FDC Young's modulus
        """
        #Ec = 3700.0*f_ck**(1/3)/100 * 100000    # the French NA
        f_cm = f_ck + 8 # MPa
        Ecm = 1.0e6*22*(f_cm/10)**0.3    # kPa
        return Ecm


    @pyqtSlot()
    def update_FDC_top(self):
        """ Updates FDC top
        """
        try:
            top = float(self.ui.lineEdit.text())
            self.FDC_params['top'] = top
            self.plot_FDC()
            self.display_LTP_params()   # show the updated base of LTP on table

            # set soil parameters at anchorage
            self.set_soil_params_at_anchorage()

        except:
            pass


    @pyqtSlot()
    def update_soiltype(self, text):
        """ Updates soil type, soil type dependent parameters will be updated
        """
        soiltype = text
        self.ui.tableWidget.blockSignals(True)
        #layer = row
        soiltype_combobox = self.ui.tableWidget.sender()
        layer = soiltype_combobox.property('layer')
        #soiltype = self.ui.tableWidget.item(row, column).text()
        alpha = self.database_soiltype['alpha'][soiltype]
        q_s_max = self.database_soiltype['qs, max'][soiltype]
        k_t = self.database_soiltype['k_t'][soiltype]
        Eoed = float(self.ui.tableWidget.item(layer+1, 9).text())
        nu = self.Layer_polygons[layer]['nu']
        gammaSat = self.Layer_polygons[layer]['gammaSat']
        Ktand = self.Layer_polygons[layer]['Ktand']
        Ey = Eoed*(1+nu)*(1-2*nu)/(1-nu)
        Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
        pl = Em / 10    # limit pressure
        ve = self.Layer_polygons[layer]['ve']
        we = self.Layer_polygons[layer]['we']
        self.ui.tableWidget.setItem(layer+1, 6, QtWidgets.QTableWidgetItem(str(alpha)))
        self.ui.tableWidget.setItem(layer+1, 9, QtWidgets.QTableWidgetItem(str(Eoed)))
        self.ui.tableWidget.setItem(layer+1, 10, QtWidgets.QTableWidgetItem(str(q_s_max)))
        self.ui.tableWidget.item(layer+1, 10).setBackground(QColor(242, 255, 116))
        self.ui.tableWidget.setItem(layer+1, 11, QtWidgets.QTableWidgetItem(str(k_t)))
        self.ui.tableWidget.setItem(layer+1, 12, QtWidgets.QTableWidgetItem(str(Ktand)))
        self.ui.tableWidget.setItem(layer+1, 13, QtWidgets.QTableWidgetItem(str(gammaSat)))
        self.ui.tableWidget.setItem(layer+1, 5, QtWidgets.QTableWidgetItem(str(Em)))
        self.ui.tableWidget.setItem(layer+1, 4, QtWidgets.QTableWidgetItem(str(pl)))

        self.ui.tableWidget.blockSignals(False)

        # store layer values
        self.set_layerpolygon_params(self.Layer_polygons[layer], soiltype, alpha, q_s_max, k_t, Em, Ey, Eoed, nu, pl, Ktand, gammaSat, ve, we) #! TBD: q_s_max -> q_s

        # set soil parameters at anchorage
        self.set_soil_params_at_anchorage()


    @pyqtSlot()
    def update_soillayer_qs(self, row, column):
        """ Update skin resistance q_s for a soil layer
        """
        if int(column) == 10:
            q_s = float(self.ui.tableWidget.item(row, column).text())
            self.Layer_polygons[row-1]['q_s'] = q_s


    @pyqtSlot()
    def update_soillayer_Ey(self, row, column):
        """ Update Young's modulus Ey for a soil layer
        """
        if int(column) == 8:
            Ey = float(self.ui.tableWidget.item(row, column).text())
            if row==0: # LTP
                nu = self.LTP_params['nu']
                alpha = self.LTP_params['alpha']
                Eoed = Ey * (1-nu)/((1+nu)*(1-2*nu))
                Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
                pl = Em / 10    # limit pressure
                self.LTP_params['Ey'] = Ey
                self.LTP_params['Eoed'] = Eoed
                self.LTP_params['Em'] = Em
                self.LTP_params['pl'] = pl

            else:
                nu = self.Layer_polygons[row-1]['nu']
                alpha = self.Layer_polygons[row-1]['alpha']
                Eoed = Ey * (1-nu)/((1+nu)*(1-2*nu))
                Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
                pl = Em / 10    # limit pressure
                self.Layer_polygons[row-1]['Ey'] = Ey
                self.Layer_polygons[row-1]['Eoed'] = Eoed
                self.Layer_polygons[row-1]['Em'] = Em
                self.Layer_polygons[row-1]['pl'] = pl
            self.ui.tableWidget.setItem(row, 9, QtWidgets.QTableWidgetItem('{:.2f}'.format(Eoed)))
            self.ui.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem('{:.2f}'.format(Em)))
            self.ui.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(pl)))


    @pyqtSlot()
    def update_user_input_E_s(self, user_input=False):
        """ Updates on using user input Oedometer modulus
        """
        self.FDC_params['user_input_E_s'] = user_input


    @pyqtSlot()
    def update_soillayer_Eoed_user(self, row, column):
        """ Update user input Eoed for a soil layer
        """
        if int(column) == 14:
            Eoed_user = float(self.ui.tableWidget.item(row, column).text())
            self.Layer_polygons[row-1]['Eoed_user'] = Eoed_user


    @pyqtSlot()
    def update_soillayer_nu(self, row, column):
        """ Update Poisson's ratio nu for a soil layer
        """
        if int(column) == 7:
            nu = float(self.ui.tableWidget.item(row, column).text())
            if row==0: # LTP
                Ey = self.LTP_params['Ey']
                Eoed = Ey * (1-nu)/((1+nu)*(1-2*nu))
                self.LTP_params['nu'] = nu
                self.LTP_params['Eoed'] = Eoed

            else:
                Ey = self.Layer_polygons[row-1]['Ey']
                Eoed = Ey * (1-nu)/((1+nu)*(1-2*nu))
                self.Layer_polygons[row-1]['nu'] = nu
                self.Layer_polygons[row-1]['Eoed'] = Eoed
            self.ui.tableWidget.setItem(row, 9, QtWidgets.QTableWidgetItem('{:.2f}'.format(Eoed)))


    @pyqtSlot()
    def update_soillayer_alpha(self, row, column):
        """ Update alpha for a soil layer
        """
        if int(column) == 6:
            alpha = float(self.ui.tableWidget.item(row, column).text())
            if row==0: # LTP
                nu = self.LTP_params['nu']
                Ey = self.LTP_params['Ey']
                Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
                pl = Em / 10    # limit pressure
                self.LTP_params['alpha'] = alpha
                self.LTP_params['Em'] = Em
                self.LTP_params['pl'] = pl

            else:
                nu = self.Layer_polygons[row-1]['nu']
                Ey = self.Layer_polygons[row-1]['Ey']
                Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
                pl = Em / 10    # limit pressure
                self.Layer_polygons[row-1]['alpha'] = alpha
                self.Layer_polygons[row-1]['Em'] = Em
                self.Layer_polygons[row-1]['pl'] = pl
            self.ui.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem('{:.2f}'.format(Em)))
            self.ui.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem('{:.2f}'.format(pl)))


    def initialize_soil_layers(self):
        """ Initializes soil layers for the first time
        """
        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            # Young's modulus
            #Ey = read_data_in_json_item(soilmaterial_layer, 'EurRef')
            Eoed = read_data_in_json_item(soilmaterial_layer, 'EoedRef') 
            nu = read_data_in_json_item(soilmaterial_layer, 'nu')
            Ey = Eoed*(1+nu)*(1-2*nu)/(1-nu)
            gammaSat = read_data_in_json_item(soilmaterial_layer, 'gammaSat')

            soiltype = 'Clay'   # the defaut soil type
            alpha = self.database_soiltype['alpha'][soiltype]
            q_s_max = self.database_soiltype['qs, max'][soiltype]
            k_t = self.database_soiltype['k_t'][soiltype]
            Em = Ey * alpha # pressuremeter modulus Em = Ey * alpha
            pl = Em / 10    # limit pressure
            #Eoed = Ey * (1-nu)/((1+nu)*(1-2*nu))
            Ktand = 1.0

            # additional soil params for stress-dependent stiffness
            ve = read_data_in_json_item(soilmaterial_layer, 've')
            we = read_data_in_json_item(soilmaterial_layer, 'we')

            # suggest user input Eoed
            Eoed_user = Eoed

            # store layer values
            self.set_layerpolygon_params(layerpolygon, soiltype, alpha, q_s_max, k_t, Em, Ey, Eoed, nu, pl, Ktand, gammaSat, ve, we) #! TBD: q_s_max -> q_s


    def display_soil_layers(self):
        """ Displays soil layers
        """
        self.ui.tableWidget.blockSignals(True)
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.clear()

        column_labels = ['Layer', 'Soil type', 'thickness \nh [m]', 'base \nz_inf [m]', 'limit pressure \n pl*', 'pressuremeter modulus \n EmRef [KPa]', 'alpha \n[-]', 'nu \n [-]', 'EyRef \n [kPa]', 'EoedRef \n [kPa]', 'q_s \n [kPa]', 'k_t \n [-]', 'Ktand \n [-]', 'gammaSat\n[kN/m^3]', 'Eoed_user \n [kPa]']
        self.ui.tableWidget.setColumnCount(len(column_labels))
        self.ui.tableWidget.setRowCount(len(self.Layer_polygons) + 1)
        self.ui.tableWidget.setHorizontalHeaderLabels(column_labels)

        self.display_LTP_params()   # show LPT parameters

        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            self.ui.tableWidget.setItem(layer_i+1, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # show default diameter
            self.ui.tableWidget.item(layer_i+1, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color
            self.ui.tableWidget.setItem(layer_i+1, 8, QtWidgets.QTableWidgetItem(str(layerpolygon['Ey'])))
            self.ui.tableWidget.item(layer_i+1, 8).setBackground(QColor(242, 255, 116))
            # soil type
            soiltype_items = ['Clay', 'Silt', 'Sand', 'Gravel', 'Chalk', 'Marl', 'Rock']
            soiltype_combobox = QtWidgets.QComboBox()
            soiltype_combobox.addItems(soiltype_items)
            soiltype_combobox.setCurrentText(layerpolygon['soiltype'])
            soiltype_combobox.setProperty('layer', layer_i) # holds property of soil layer for use in updating soil type
            soiltype_combobox.setStyleSheet("background-color: rgb(242, 255, 116);\n")
            soiltype_combobox.activated[str].connect(self.update_soiltype)
            self.ui.tableWidget.setCellWidget(layer_i+1, 1, soiltype_combobox)

            self.ui.tableWidget.setItem(layer_i+1, 6, QtWidgets.QTableWidgetItem(str(layerpolygon['alpha'])))
            self.ui.tableWidget.item(layer_i+1, 6).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget.setItem(layer_i+1, 7, QtWidgets.QTableWidgetItem(str(layerpolygon['nu'])))
            self.ui.tableWidget.item(layer_i+1, 7).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget.setItem(layer_i+1, 9, QtWidgets.QTableWidgetItem(str(layerpolygon['Eoed'])))
            self.ui.tableWidget.setItem(layer_i+1, 10, QtWidgets.QTableWidgetItem(str(layerpolygon['q_s'])))
            self.ui.tableWidget.item(layer_i+1, 10).setBackground(QColor(242, 255, 116))
            self.ui.tableWidget.setItem(layer_i+1, 11, QtWidgets.QTableWidgetItem(str(layerpolygon['k_t'])))
            self.ui.tableWidget.setItem(layer_i+1, 12, QtWidgets.QTableWidgetItem(str(layerpolygon['Ktand'])))
            self.ui.tableWidget.setItem(layer_i+1, 13, QtWidgets.QTableWidgetItem(str(layerpolygon['gammaSat'])))
            self.ui.tableWidget.setItem(layer_i+1, 5, QtWidgets.QTableWidgetItem(str(layerpolygon['Em'])))
            self.ui.tableWidget.setItem(layer_i+1, 4, QtWidgets.QTableWidgetItem(str(layerpolygon['pl'])))
            self.ui.tableWidget.setItem(layer_i+1, 14, QtWidgets.QTableWidgetItem(str(layerpolygon['Eoed_user'])))  # User input Eoedometer
            self.ui.tableWidget.item(layer_i+1, 14).setBackground(QColor(242, 255, 116))

            # layer thickness and bottom
            layer_i_top = self.borehole['Top'][layer_i]
            layer_i_bottom = self.borehole['Bottom'][layer_i]
            layer_i_thickness = layer_i_top - layer_i_bottom
            self.ui.tableWidget.setItem(layer_i+1, 2, QtWidgets.QTableWidgetItem(str(layer_i_thickness)))
            self.ui.tableWidget.setItem(layer_i+1, 3, QtWidgets.QTableWidgetItem(str(layer_i_bottom)))


        self.ui.tableWidget.blockSignals(False)


    def set_layerpolygon_params(self, layerpolygon, soiltype, alpha, q_s, k_t, Em, Ey, Eoed, nu, pl, Ktand, gammaSat, ve, we):
        """ Sets/ stores layer polygon parameters
        """
        layerpolygon['soiltype'] = soiltype
        layerpolygon['alpha'] = alpha
        layerpolygon['q_s'] = q_s
        layerpolygon['k_t'] = k_t
        layerpolygon['Em'] = Em
        layerpolygon['Ey'] = Ey
        layerpolygon['Eoed'] = Eoed
        layerpolygon['Eoed_user'] = Eoed
        layerpolygon['nu'] = nu
        layerpolygon['pl'] = pl
        layerpolygon['Ktand'] = Ktand
        layerpolygon['gammaSat'] = gammaSat
        layerpolygon['ve'] = ve
        layerpolygon['we'] = we


    def set_soil_params_at_anchorage(self, show=True):
        """ Sets soil parameters at anchorage
        """
        level_toe = self.FDC_params['top'] - self.FDC_params['Lc']
        pl_anchorage_plus50cm = self.get_soil_param_at_level('pl', level_toe + 0.5)
        pl_anchorage_minus150cm = self.get_soil_param_at_level('pl', level_toe - 1.5)
        ple = (pl_anchorage_plus50cm**0.5 * pl_anchorage_minus150cm**1.5)**(1/(1.5 + 0.5))
        # kq
        soiltype_anchorage = self.get_soil_param_at_level('soiltype', level_toe)
        kq = self.database_soiltype_qp_kq['kq'][soiltype_anchorage]
        # Em
        Emp = self.get_soil_param_at_level('Em', level_toe)

        # store values
        self.anchorage_params['pl_anchorage_plus50cm'] = pl_anchorage_plus50cm
        self.anchorage_params['pl_anchorage_minus150cm'] = pl_anchorage_minus150cm
        self.anchorage_params['ple'] = ple
        self.anchorage_params['soiltype'] = soiltype_anchorage
        self.anchorage_params['kq'] = kq
        self.anchorage_params['Emp'] = Emp
        self.anchorage_params['kp'] = self.calc_qb()

        # show data
        if show:
            self.display_anchorage_params()


    def set_soil_params_at_anchorage_stress_dependent(self):
        """ Sets soil parameters at anchorage based on stress-dependent data
        This method is called after data assembly used for NSGA optimization.
        """
        level_toe = self.FDC_params['top'] - self.FDC_params['Lc']
        # kq
        soiltype_anchorage = self.get_soil_param_at_level('soiltype', level_toe)
        kq = self.database_soiltype_qp_kq['kq'][soiltype_anchorage]
        # Em
        Emp = self.data[-1, 2]  # Em at FDC toe
        ple = Emp/10
        self.anchorage_params['soiltype'] = soiltype_anchorage
        self.anchorage_params['kq'] = kq
        self.anchorage_params['ple'] = ple
        self.anchorage_params['Emp'] = Emp
        self.anchorage_params['kp'] = self.calc_qb()


    def calc_qb(self):
        """ Calculates soil resistance at column tip
        """
        hD = 10*self.FDC_params['Dc']
        #D = self.FDC_params['Lc'] + self.LTP_params['hM'] # D = Hc
        level_toe = self.FDC_params['top'] - self.FDC_params['Lc']
        pl_avrg = self.get_soil_param_at_level('pl', level_toe + hD) #! not averaged yet, TBD
        Def = hD*pl_avrg/self.anchorage_params['ple']
        Def_over_Dc = Def/self.FDC_params['Dc']
        soiltype = self.anchorage_params['soiltype']
        kpmax = self.database_soiltype_qp_kq['kpmax, Def/Dc > 5'][soiltype]
        if Def_over_Dc >= 5:
            kp_Def_over_Dc = kpmax
        else:
            kp_Def_over_Dc = 1 + (kpmax - 1)*Def_over_Dc/5

        kp = kp_Def_over_Dc*self.anchorage_params['ple']

        return kp


    def get_soil_param_at_level(self, param_name, level):
        """ Gets soil parameter value at a level
        """
        value = None
        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            if (self.borehole['Top'][layer_i] >= level) and (self.borehole['Bottom'][layer_i] <= level):
                value = layerpolygon[param_name]
                break

        return value



    @pyqtSlot()
    def update_anchorage_qp(self):
        """ Allows user to manually change qp
        """
        try:
            kp = float(self.ui.lineEdit_8.text())
            self.anchorage_params['kp'] = kp

        except:
            pass


    @pyqtSlot()
    def update_anchorage_kq(self):
        """ Allows user to manually change kq
        """
        try:
            kq = float(self.ui.lineEdit_9.text())
            self.anchorage_params['kq'] = kq

        except:
            pass


    @pyqtSlot()
    def update_anchorage_Em(self):
        """ Allows user to manually change Em
        """
        try:
            Emp = float(self.ui.lineEdit_10.text())
            self.anchorage_params['Emp'] = Emp

        except:
            pass


    @pyqtSlot()
    def update_FDC_loading_G(self):
        """ Updates G
        """
        try:
            G = float(self.ui.lineEdit_11.text())
            self.FDC_loading_obj.set_G(G)
            self.save_FDC_loading()
            self.display_FDC_loading()
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_FDC_loading_Q(self):
        """ Updates Q
        """
        try:
            Q = float(self.ui.lineEdit_12.text())
            self.FDC_loading_obj.set_Q(Q)
            self.save_FDC_loading()
            self.display_FDC_loading()
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_FDC_loading_gammaG(self):
        """ Updates Q
        """
        try:
            gammaG = float(self.ui.lineEdit_13.text())
            self.FDC_loading_obj.set_gammaG(gammaG)
            self.save_FDC_loading()
            self.display_FDC_loading()
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_FDC_loading_gammaQ(self):
        """ Updates Q
        """
        try:
            gammaQ = float(self.ui.lineEdit_14.text())
            self.FDC_loading_obj.set_gammaQ(gammaQ)
            self.save_FDC_loading()
            self.display_FDC_loading()
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_thickness(self):
        """ Updates LTP thickness hM
        """
        try:
            hM = float(self.ui.lineEdit_15.text())
            self.LTP_params['hM'] = hM
            #self.update_FDC_top()
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_phi(self):
        """ Updates the friction angle of LTP material
        """
        try:
            phi = float(self.ui.lineEdit_16.text())
            self.LTP_params['phi'] = phi
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_c(self):
        """ Updates cohension of LTP material
        """
        try:
            c = float(self.ui.lineEdit_17.text())
            self.LTP_params['c'] = c
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_s_q(self):
        """ Updates Prandtl s_q of LTP material
        """
        try:
            s_q = float(self.ui.lineEdit_18.text())
            self.LTP_params['s_q'] = s_q
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_s_c(self):
        """ Updates Prandtl s_c of LTP material
        """
        try:
            s_c = float(self.ui.lineEdit_19.text())
            self.LTP_params['s_c'] = s_c
            self.get_q_p_and_q_s()

        except:
            pass
    

    @pyqtSlot()
    def update_LTP_nabla(self):
        """ Updates Prandtl nabla of LTP material
        """
        try:
            nabla = float(self.ui.lineEdit_25.text())
            self.LTP_params['nabla'] = nabla
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_gammaR(self):
        """ Updates Prandtl nabla of LTP material
        """
        try:
            gammaR = float(self.ui.lineEdit_26.text())
            self.LTP_params['gammaR'] = gammaR
            self.get_q_p_and_q_s()

        except:
            pass


    @pyqtSlot()
    def update_LTP_isMenard(self, checkstate):
        """ Updates Prandtl nabla of LTP material
        """
        try:
            isMenard = (checkstate == 2)
            self.LTP_params['isMenard'] = isMenard
            self.get_q_p_and_q_s()

        except:
            pass



    def get_q_p_and_q_s(self):
        """ Gets (vertical) stress acting on soil (q_p_plus) and 
        (vertical) stress acting on colum (q_p_plus)
        """
        # LTP calculation object, initialized with up-to-dated parameters
        self.LTP_calc_obj = LTP_calc(self.LTP_params, self.FDC_params, self.FDC_loading)

        q0 = self.FDC_loading_obj.get_q0()
        q_p_plus = self.LTP_calc_obj.get_q_p_plus(q0)
        q_s_plus = self.LTP_calc_obj.get_q_s_plus(q0, q_p_plus)

        # height of Prandtl mechanism
        H_max, h1, h2 = self.LTP_calc_obj.get_H_max()

        # limit pressure of the LTP material
        f_ck = self.FDC_params['fck']
        alpha_cc = self.FDC_params['alpha_cc']
        gammaC = self.FDC_params['gammaC']
        f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
        self.FDC_params['fcd'] = f_cd
        hM = self.LTP_params['hM']
        if not self.LTP_params['isMenard']:
            q_p_Rd, q_p_min, q_p_max, k, n = self.LTP_calc_obj.get_q_p_Rd(q_s_plus, f_cd, H_max, h1, h2, hM)
            self.plot_q_p_Rd_vs_hM(q_p_min, q_p_max, k, n, hM, q_p_Rd)
        else: # Menard method
            q_p_Rd = self.LTP_calc_obj.get_q_p_Rd_Menard(q_p_plus, f_cd, H_max, hM)
            self.plot_q_p_Rd_vs_hM_Menard(q_p_plus, f_cd, H_max, hM, q_p_Rd)

        # show results
        self.ui.lineEdit_21.setText('{:.2f}'.format(q_p_plus))
        self.ui.lineEdit_22.setText('{:.2f}'.format(q_s_plus))
        self.ui.lineEdit_24.setText('{:.2f}'.format(H_max))
        self.ui.lineEdit_28.setText('{:.2f}'.format(q_p_Rd))
        N_q = self.LTP_calc_obj.get_Nq_Prandtl()
        N_c = self.LTP_calc_obj.get_Nc_Prandtl()
        self.ui.lineEdit_36.setText('{:.2f}'.format(N_q))
        self.ui.lineEdit_37.setText('{:.2f}'.format(N_c))
        

    def plot_q_p_Rd_vs_hM(self, q_p_min, q_p_max, k, n, hMi, q_p_Rdi):
        """ Plots allowable stress in LTP q_p_Rd vs LTP thickness
        hMi, q_p_Rdi: current design
        """
        h = np.arange(0, 2, 0.05)
        q_p_Rd = (q_p_max - q_p_min)*np.exp((-h**n) * k) + q_p_min

        self.plot_canvas_1.plot_q_p_Rd_vs_hM(h, q_p_Rd, hMi, q_p_Rdi)


    def plot_q_p_Rd_vs_hM_Menard(self, q_p_plus, f_cd, H_max, hM, q_p_Rd):
        """ Plots allowable stress in LTP q_p_Rd vs LTP thickness
        hMi, q_p_Rdi: current design
        """
        points = [(0, f_cd), (hM, q_p_Rd), (H_max, q_p_plus), (2.0, q_p_plus)]

        self.plot_canvas_1.plot_q_p_Rd_vs_hM_Menard(points)


    def assemble_data(self, show=True):
        """
        """
        self.data, self.Eoed_eff_unreinforced, sigma_v_unreinforced = self.assemble_data_FDC()
        self.data_below_FDC = self.assemble_data_below_FDC(sigma_v_unreinforced)

        # show data
        if show:
            self.display_assembed_data(self.data, self.ui.tableWidget_2)
            self.display_assembed_data(self.data_below_FDC, self.ui.tableWidget_4)


    def assemble_data_FDC(self):
        """ Assembles LTP and soil data within the FCX for the calculation
        """
        top = self.FDC_params['top'] + self.LTP_params['hM']
        bottom = top - self.LTP_params['hM'] - self.FDC_params['Lc'] 
        data = np.zeros((201, 11))
        top_level = np.linspace(top, bottom, 201,endpoint=True)# top
        delta_z = top_level[0] - top_level[1]
        data[:, 0] = top - top_level        # top (depth)
        data[:, 1] = data[:, 0] + delta_z   # bottom (depth)

        params = ['Em', 'alpha', 'nu', 'Ey', 'Eoed', 'q_s', 'k_t', 'gammaSat', 'Ktand']
        for i in range(data.shape[0]):
            for param_j, param in enumerate(params):
                if data[i, 0] < self.LTP_params['hM']: # within the LTP
                    data[i, param_j + 2] = self.LTP_params[param] 
                else:   # in the soil layers
                    data[i, param_j+2] = self.get_soil_param_at_level(param, top - data[i, 0])

        # stress-dependent stiffness for the reinforced soil
        if not self.FDC_params['user_input_E_s']:
            Eoed_eff, _ = self.get_depth_dependent_Eoed(0.0, data, top, top)
        else:
            Eoed_eff, _ = self.get_user_input_Eoed(0.0, data, top, top)

        # replace soil stiffness below LTP by stress-dependent stiffness
        idx_z = np.where(data[:, 0] > self.LTP_params['hM'])
        data[idx_z, 6] = Eoed_eff[idx_z]                            # Eoed
        nu = data[idx_z, 4]
        data[idx_z, 5] = Eoed_eff[idx_z]*(1+nu)*(1-2*nu)/(1-nu)     # Ey
        data[idx_z, 2] = data[idx_z, 5]*data[idx_z, 3]              # Em

        # stress-dependent stiffness for the unreinforced soil
        p0 = self.FDC_loading_obj.get_q0()/2  # surchange 
        if not self.FDC_params['user_input_E_s']:
            Eoed_eff_unreinforced, sigma_v_unreinforced = self.get_depth_dependent_Eoed(p0, data, top, top)
        else:
            Eoed_eff_unreinforced, sigma_v_unreinforced = self.get_user_input_Eoed(p0, data, top, top)

        return data, Eoed_eff_unreinforced, sigma_v_unreinforced


    def get_depth_dependent_Eoed(self, p0, data, top, sub_layer_start_level):
        """ Gets depth dependent Eoed
        p0: surcharge
        top: top ground surface level
        sub_layer_start_level: start level for stiffness calculation
        """
        sigma_v = p0 
        Eoed_eff = np.zeros(data.shape[0])
        sub_layer_i_level = sub_layer_start_level # ground surface
        for i in range(data.shape[0]):
            thickness_sublayer_i = data[i, 1] - data[i, 0]

            sub_layer_i_level -= thickness_sublayer_i
            gammaSat = data[i, 9]
            #Hw = self.FDC_params['top'] + self.LTP_params['hM'] - self.borehole['Head']   # depth of groundwater table from LTP top
            if sub_layer_i_level <= self.borehole['Head']: # under water (under bouyancy)
                sigma_v += (gammaSat - 10.0) * thickness_sublayer_i
            else:   # dried soil
                sigma_v += gammaSat * thickness_sublayer_i

            ve = self.get_soil_param_at_level('ve', top - data[i, 0])
            we = self.get_soil_param_at_level('we', top - data[i, 0])
            Eoed_eff[i] = ve*100*(sigma_v/100)**we

        return Eoed_eff, sigma_v


    def get_user_input_Eoed(self, p0, data, top, sub_layer_start_level):
        """ Gets user input Eoed
        p0: surcharge
        top: top ground surface level
        sub_layer_start_level: start level for stiffness calculation
        """
        sigma_v = p0 
        Eoed_eff = np.zeros(data.shape[0])
        sub_layer_i_level = sub_layer_start_level # ground surface
        for i in range(data.shape[0]):
            thickness_sublayer_i = data[i, 1] - data[i, 0]

            sub_layer_i_level -= thickness_sublayer_i
            gammaSat = data[i, 9]
            if sub_layer_i_level <= self.borehole['Head']: # under water (under bouyancy)
                sigma_v += (gammaSat - 10.0) * thickness_sublayer_i
            else:   # dried soil
                sigma_v += gammaSat * thickness_sublayer_i

            Eoed_user = self.get_soil_param_at_level('Eoed_user', top - data[i, 0])
            Eoed_eff[i] = Eoed_user

        return Eoed_eff, sigma_v


    def assemble_data_below_FDC(self, sigma_v_FDC_toe):
        """ Assembles LTP and soil data below column for the calculation
        """
        toe_level_FDC = self.FDC_params['top'] - self.FDC_params['Lc'] #
        H_lim_level = self.FDC_params['top'] - self.FDC_params['H_lim'] 
        data = np.zeros((101, 11))
        top_level = np.linspace(toe_level_FDC, H_lim_level, 101,endpoint=True)# top
        delta_z = top_level[0] - top_level[1]
        top_ground = self.FDC_params['top'] + self.LTP_params['hM']
        data[:, 0] = top_ground - top_level   # top (depth)
        data[:, 1] = data[:, 0] + delta_z   # bottom (depth)

        params = ['Em', 'alpha', 'nu', 'Ey', 'Eoed', 'q_s', 'k_t', 'gammaSat', 'Ktand']
        for i in range(data.shape[0]):
            for param_j, param in enumerate(params):
                data[i, param_j+2] = self.get_soil_param_at_level(param, top_ground - data[i, 0])
        
        if not self.FDC_params['user_input_E_s']: # stress-dependent stiffness
            Eoed_eff_unreinforced, _ = self.get_depth_dependent_Eoed(sigma_v_FDC_toe, data, top_ground, toe_level_FDC)
        else:
            Eoed_eff_unreinforced, _ = self.get_user_input_Eoed(sigma_v_FDC_toe, data, top_ground, toe_level_FDC)

        # replace soil stiffness below LTP by stress-dependent stiffness
        data[:, 6] = Eoed_eff_unreinforced[:]                   # Eoed
        nu = data[:, 4]
        data[:, 5] = Eoed_eff_unreinforced[:]*(1+nu)*(1-2*nu)/(1-nu)     # Ey
        data[:, 2] = data[:, 5]*data[:, 3]                      # Em

        return data


    def display_assembed_data(self, data, table_widget):
        """ Displays the assembled data 
        """
        num_row, num_column = data.shape
        headers = ['top [m]', 'bottom [m]', 'Em [kPa]', 'alpha [-]', 'nu [-]', 'Ey [kPa]', 'Eoed [kPa]', 'q_s [kPa]', 'k_t [-]', 'gammaSat [kN/m^3]', 'Ktan(delta)']
        table_widget.setRowCount(num_row)
        table_widget.setColumnCount(num_column)   
        table_widget.setHorizontalHeaderLabels(headers)

        params = ['Em', 'alpha', 'nu', 'Ey', 'Eoed', 'q_s', 'k_t', 'gammaSat', 'Ktand']
        for row_i in range(num_row):
            table_widget.setItem(row_i, 0,  QtWidgets.QTableWidgetItem(str(data[row_i, 0])))   # top 
            table_widget.setItem(row_i, 1,  QtWidgets.QTableWidgetItem(str(data[row_i, 1])))   # bottom
            #table_widget.setItem(row_i, num_column,  QtWidgets.QTableWidgetItem(str(Eoed_eff[row_i])))   # Eoed_eff
            for param_j, _ in enumerate(params):
                table_widget.setItem(row_i, param_j+2,  QtWidgets.QTableWidgetItem(str(data[row_i, param_j+2])))   
        


    def calculate(self, show=True):
        """ Calculates FDC settlement and reactions
        """
        if self.data is not None:
            Parameteres_matrix = np.delete(self.data, np.s_[1, 3, 4], axis=1)   # unused columns: bottom, alpha, and nu
            #Parameteres_matrix = [[0.00,0.02,0.04,0.06,0.08,0.11,0.13,0.15,0.17,0.19,0.21,0.23,0.25,0.27,0.29,0.32,0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48,0.50,0.53,0.55,0.57,0.59,0.61,0.63,0.65,0.67,0.69,0.71,0.74,0.76,0.78,0.80,0.82,0.84,0.86,0.88,0.90,0.92,0.95,0.97,0.99,1.01,1.03,1.05,1.07,1.09,1.11,1.13,1.16,1.18,1.20,1.22,1.24,1.26,1.28,1.30,1.32,1.34,1.37,1.39,1.41,1.43,1.45,1.47,1.49,1.51,1.53,1.55,1.58,1.60,1.62,1.64,1.66,1.68,1.70,1.72,1.74,1.76,1.79,1.81,1.83,1.85,1.87,1.89,1.91,1.93,1.95,1.97,2.00,2.02,2.04,2.06,2.08,2.10,2.12,2.14,2.16,2.18,2.21,2.23,2.25,2.27,2.29,2.31,2.33,2.35,2.37,2.39,2.42,2.44,2.46,2.48,2.50,2.52,2.54,2.56,2.58,2.60,2.63,2.65,2.67,2.69,2.71,2.73,2.75,2.77,2.79,2.81,2.84,2.86,2.88,2.90,2.92,2.94,2.96,2.98,3.00,3.02,3.05,3.07,3.09,3.11,3.13,3.15,3.17,3.19,3.21,3.23,3.26,3.28,3.30,3.32,3.34,3.36,3.38,3.40,3.42,3.44,3.47,3.49,3.51,3.53,3.55,3.57,3.59,3.61,3.63,3.65,3.68,3.70,3.72,3.74,3.76,3.78,3.80,3.82,3.84,3.86,3.89,3.91,3.93,3.95,3.97,3.99,4.01,4.03,4.05,4.07,4.10,4.12,4.14,4.16,4.18,4.20],[25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,2500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,25000,25000,25000,25000,25000,25000,25000,25000,25000,25000],[100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,100000,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,3731,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,2250,75758,75758,75758,75758,75758,75758,75758,75758,75758,75758],[134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,134615,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,5023,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,3029,101981,101981,101981,101981,101981,101981,101981,101981,101981,101981],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,120,120,120,120,120,120,120,120,120,120],[0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8],[20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,20,20,20,20,20,20,20,20,20,20],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]#[[0.0 for i in range (0,8)] for i in range(0,201)]

            Eoed_IF = self.LTP_params['Eoed']
            Dc = self.FDC_params['Dc']
            qp = self.anchorage_params['kp']
            kq = self.anchorage_params['kq']
            Emp = self.anchorage_params['Emp']
            Hc = self.LTP_params['hM'] + self.FDC_params['Lc']  # FDC depth from LTP top
            hM = self.LTP_params['hM']
            Hlim = self.FDC_params['H_lim']
            Hw = self.FDC_params['top'] + self.LTP_params['hM'] - self.borehole['Head']   # depth of groundwater table from LTP top
            dq = self.FDC_loading_obj.get_q0_unfactored()
            As = self.FDC_params['a'] * self.FDC_params['a']
            #Ec = 3700.0*self.FDC_params['fck']**(1/3)/100 * 100000
            Ec = self.get_FDC_Ecm(self.FDC_params['fck'])
            dQ_Hm = dq*As
            Etat = 10
            e1 = 0.001
            e2 = 0.001
            wqp1 = 0
            wqp2 = 0
            Eoeda = Eoed_IF

            # LTP calculation object, initialized with up-to-dated parameters
            self.LTP_calc_obj = LTP_calc(self.LTP_params, self.FDC_params, self.FDC_loading)
            q0 = self.FDC_loading_obj.get_q0()
            q_p_plus = self.LTP_calc_obj.get_q_p_plus(q0)
            q_s_plus = self.LTP_calc_obj.get_q_s_plus(q0, q_p_plus)

            # height of Prandtl mechanism
            H_max, h1, h2 = self.LTP_calc_obj.get_H_max()
            # limit pressure of the LTP material
            f_ck = self.FDC_params['fck']
            alpha_cc = self.FDC_params['alpha_cc']
            gammaC = self.FDC_params['gammaC']
            f_cd = self.get_FDC_f_cd(f_ck, alpha_cc, gammaC)*1000     # kPa
            self.FDC_params['fcd'] = f_cd
            hM = self.LTP_params['hM']

            # bearing capacity, Menard method or not
            if not self.LTP_params['isMenard']:
                q_p_Rd, _, _, _, _ = self.LTP_calc_obj.get_q_p_Rd(q_s_plus, f_cd, H_max, h1, h2, hM)
            else: 
                q_p_Rd = self.LTP_calc_obj.get_q_p_Rd_Menard(q_p_plus, f_cd, H_max, hM)

            gamma_eq_ULS = self.FDC_loading_obj.get_gamma_eq_ULS()
        
            if show:
                print('START FDC CALCULATION...')
            Q_p_Rd = q_p_Rd*Dc**2*np.pi*1/4
            #print('q_p_Rd', q_p_Rd)
            #print('Q_p_Rd', Q_p_Rd)
            #print(Q_p_Rd,gamma_eq_ULS,Eoed_IF,Dc,qp,kq,Emp,Hc,hM,Hlim,Hw,dq,As,Ec,dQ_Hm,Etat,e1,e2,wqp1,wqp2,Eoeda)
            matrice = Calcul_Click(Parameteres_matrix,Q_p_Rd,gamma_eq_ULS,Eoed_IF,Dc,qp,kq,Emp,Hc,hM,Hlim,Hw,dq,As,Ec,dQ_Hm,Etat,e1,e2,wqp1,wqp2,Eoeda)
            matrice_array = np.array(matrice)
            w_toe = matrice_array[-1, 26]

            gammaSat_LTP = self.LTP_params['gammaSat']
            Ey_LTP = self.LTP_params['Ey']
            nu_LTP = self.LTP_params['nu']
            #Parameteres_below_FDC = np.delete(self.data_below_FDC, np.s_[1, 3, 4], axis=1)   # unused columns: bottom, alpha, and nu
            Parameteres_below_FDC = self.data_below_FDC
            Parameteres_FDC = self.data
            Eoed_eff_unreinforced = self.Eoed_eff_unreinforced

            q = dq + self.LTP_params['gammaSat']*hM
            w_unreinforced, Parameteres_below_FDC, Parameteres_FDC = get_unreinforced_soil_settlement(Parameteres_FDC, Eoed_eff_unreinforced, Parameteres_below_FDC,q,gammaSat_LTP,Ey_LTP,nu_LTP,Hc,hM,Hlim,Hw,dq, Etat)
            w_toe = w_toe + Parameteres_below_FDC[0,-1]*1.0e-3 # add soil settlement below FDC to FDC settlement at the toe

            # add soil and column settlement just below FDC to soil settlement above it
            matrice_array[:, 28] = matrice_array[:, 28] + Parameteres_below_FDC[0, -1]*1.0e-3
            matrice_array[:, 26] = matrice_array[:, 26] + Parameteres_below_FDC[0, -1]*1.0e-3

            # Mobilized stress at the inclusion head
            idx_row = np.where(matrice_array[:,0] > self.LTP_params['hM'])[0][0] # index of the first found item
            sigma_fdc_hM_k = matrice_array[idx_row, 22]
            sigma_fdc_hM_d = sigma_fdc_hM_k * gamma_eq_ULS
            sigma_fdc_hM_d_max = np.max(matrice_array[:, 22] * gamma_eq_ULS)

            # store results for the calculation of improvement factors later
            self.matrice = np.c_[matrice_array, Parameteres_FDC[:,-1]]  # add a column to matrice which is the unreinforced settlement 

            # store soil settlement below FDC toe
            self.Parameteres_below_FDC = Parameteres_below_FDC

            # check with LTP and column bearing capacities
            self.check_passed(sigma_fdc_hM_d, sigma_fdc_hM_d_max, q_p_Rd)

            if show:
                print('Settlement at the FDC toe w_toe {:.2f} [mm]'.format(w_toe*1000))
                print('Unreinforced settlement {:.2f} [mm]'.format(w_unreinforced))
                print('ULS stress at inclusion head {:.2f} [kPa]'.format(sigma_fdc_hM_d))
                print('Max. ULS stress in column {:.2f} [kPa]'.format(sigma_fdc_hM_d_max))
                # display results
                self.display_results_table(matrice)
                w_elastic = sum([row[25] for row in matrice])   # FDC elastic shortening
                self.display_results_summary(w_toe*1000, w_elastic*1000, w_unreinforced, sigma_fdc_hM_d, sigma_fdc_hM_d_max)    # in mm and kPa
                # plot ..
                self.ui.toolBox.setCurrentIndex(1)
                self.plot_settlements_and_skin_resistance(self.matrice, self.Parameteres_below_FDC)




    def display_results_table(self, matrice):
        """ Displays calculation results
        """
        num_row = len(matrice)
        num_column = len(matrice[0])
        self.ui.tableWidget_3.setRowCount(num_row)
        self.ui.tableWidget_3.setColumnCount(num_column)
        headers = ['']*num_column
        headers[0] = 'z \n [m]'
        headers[3] = 'Em \n [kPa]'
        headers[4] = 'Ey \n [kPa]'
        headers[5] = 'Eoed \n [kPa]'
        headers[7] = 'q_s \n [kPa]'
        headers[8] = 'k_t \n [-]'
        headers[9] = 'gamma \n [kN/m^3]'
        headers[10] = 'Ktand \n [-]'
        headers[11] = 'gamma submerged \n [kN/m^3]'
        headers[12] = 'w_soil - w_column \n [m]'
        headers[13] = 'sigma_v0\' \n [kPa]'
        headers[14] = 'mobilized \n f_s \n [kPa]'
        headers[15] = 'maximal \n f_s \n [kPa]'
        headers[16] = 'lateral fric. \n Qsc \n [kN]'
        headers[17] = 'total fric. \n Qs \n [kN]'
        headers[18] = 'vertical force column \n Qfdp \n [kN]'
        headers[19] = 'lateral Qsmax \n [kN]'
        headers[20] = 'lateral neg. fric. \n [kN]'
        headers[21] = 'lateral pos. fric. \n [kN]'
        headers[22] = 'normal stress \n sigma_fdc \n [kPa]'
        headers[23] = 'force on soil \n Qsoil \n [kPa]'
        headers[24] = 'stress on soil \n sigma_soil \n [kPa]'
        headers[25] = 'elas. shortening col. \n delta_li_c \n [m]'
        headers[26] = 'w_column \n [m]'
        headers[27] = 'elas. shortening soil \n delta_li_s \n [m]'
        headers[28] = 'w_soil \n [m]'
        self.ui.tableWidget_3.setHorizontalHeaderLabels(headers)
        for irow, row  in  enumerate(matrice):
            for icolumn, column in enumerate(row):
                self.ui.tableWidget_3.setItem(irow, icolumn,  QtWidgets.QTableWidgetItem(str(column)))   



    def check_passed(self, sigma_fdc_hM_d, sigma_fdc_hM_d_max, q_p_Rd):
        """ Checks if LTP and piles bearing capacities are okay
        """
        self.isPassed = True
        if (sigma_fdc_hM_d >= q_p_Rd) or (sigma_fdc_hM_d_max >= self.FDC_params['fcd']):
            self.isPassed = False


    def display_results_summary(self, w_toe, w_elastic, w_unreinforced, sigma_fdc_hM_d, sigma_fdc_hM_d_max):
        """ Display summary of the calculation results
        """
        self.ui.lineEdit_32.setText('{:.2f}'.format(w_toe))
        self.ui.lineEdit_33.setText('{:.2f}'.format(w_elastic))
        w_total = w_toe + w_elastic
        self.ui.lineEdit_34.setText('{:.2f}'.format(w_total))
        self.ui.lineEdit_35.setText('{:.2f}'.format(w_unreinforced))

        # show the ULS stress at the inclusion head
        self.ui.lineEdit_38.setText('{:.2f}'.format(sigma_fdc_hM_d))
        q_p_Rd = float(self.ui.lineEdit_28.text())
        if sigma_fdc_hM_d <= q_p_Rd:
            self.ui.lineEdit_38.setStyleSheet("background-color: rgb(0, 255, 0);")  # green for satisfied
        else:
            self.ui.lineEdit_38.setStyleSheet("background-color: rgb(255, 0, 0);")  # red for unsatisfied
            self.isPassed = False

        # show the ULS stress at the inclusion head
        self.ui.lineEdit_39.setText('{:.2f}'.format(sigma_fdc_hM_d_max))
        f_cd = float(self.ui.lineEdit_23.text())
        if sigma_fdc_hM_d_max <= f_cd:
            self.ui.lineEdit_39.setStyleSheet("background-color: rgb(0, 255, 0);")  # green for satisfied
        else:
            self.ui.lineEdit_39.setStyleSheet("background-color: rgb(255, 0, 0);")  # red for unsatisfied
            self.isPassed = False


    def plot_settlements_and_skin_resistance(self, matrice, Parameteres_below_FDC, show_u_s_unreinf=True):
        """ Plots FDC and soil settlements
        """
        z = matrice[:, 0]
        u_z_c = matrice[:, 26]*1.0e3
        u_z_s = matrice[:, 28]*1.0e3
        f_s_mobilized = matrice[:, 14]
        f_s_max = matrice[:, 15]
        Q_fdc = matrice[:, 18]
        Q_soil = matrice[:, 23]
        self.plot_canvas_3.plot_FDC_skin_resistance(z, f_s_mobilized, f_s_max)
        self.plot_canvas_4.plot_FDC_and_soil_vertical_force(z, Q_fdc, Q_soil)

        # plot soil and column displacements, and soil displacement below FDC
        z_below_FDC = Parameteres_below_FDC[:, 0]
        u_z_s_below_FDC = Parameteres_below_FDC[:, -1]
        u_z_s_unreinf = matrice[:, -1]  # unreinforced soil settlement within FDC
        
        if self.ui.checkBox.checkState() == 0:
            show_u_s_unreinf = False
        self.plot_canvas_2.plot_FDC_and_soil_settlement(z, u_z_c, u_z_s, u_z_s_unreinf, z_below_FDC, u_z_s_below_FDC, show_u_s_unreinf)


    @pyqtSlot()
    def update_settlements_graph(self, state):
        """ Updates settlement graph to show unreinforced settlement or not
        """
        if isinstance(self.matrice, np.ndarray):
            if state==2: # checked
                self.plot_settlements_and_skin_resistance(self.matrice, self.Parameteres_below_FDC, show_u_s_unreinf=True)
            else: # state==0, unchecked
                self.plot_settlements_and_skin_resistance(self.matrice, self.Parameteres_below_FDC, show_u_s_unreinf=False)


class FDC_SoilClusters():
    """ This class divides soil layers and calculates layer and depth dependent improvement factors.
    Stiffness parameter for each of the homogenized will be factored accordingly.
    """
    def __init__(self, FDC_matrice, improved_soil_polygon, Layer_polygons, borehole, top_LTP, top_FDC, FDC_name, thickness_sublayer=2.0):
        """
        """
        self.soil_polygon = improved_soil_polygon
        self.columns_top = max([point['point'][1] for point in self.soil_polygon])
        self.columns_bottom = min([point['point'][1] for point in self.soil_polygon])
        self.columns_left = min([point['point'][0] for point in self.soil_polygon])
        self.columns_right = max([point['point'][0] for point in self.soil_polygon])
        self.columns_depth = self.columns_top - self.columns_bottom
        self.thickness_sublayer = thickness_sublayer
        self.Layer_polygons = Layer_polygons
        self.borehole = borehole

        self.top_LTP = top_LTP  # top level of the LTP
        self.top_FDC = top_FDC  # top level of FDC columns
        self.matrice = FDC_matrice  # numpy array holding FDC calculation results

        self.FDC_name = FDC_name
        self.sub_soillayers = []    # holds data for each of the sub-soil layers


    def open_FDC_soil_clusters(self):
        """ Opens the form for defining the improved soil polygon
        """
        sc_soil_box = QtWidgets.QDialog()
        self.sc_soil_edit_box = FDCSoilClusters()
        self.sc_soil_edit_box.setupUi(sc_soil_box)
        self.sc_soil_edit_box.splitter.setSizes([700, 300]) # resize widgets' size around splitter
        sc_soil_box.setWindowTitle('Improved soil properties (layer- and depth-dependent)')
        # make push buttons not responsive to enter key press
        self.sc_soil_edit_box.pushButton.setAutoDefault(False)
        self.sc_soil_edit_box.pushButton.setDefault(False)

        # show width of the imporoved soil polygon and thickness of the sublayer
        width = self.columns_right - self.columns_left
        self.sc_soil_edit_box.lineEdit.setText('{:.2f}'.format(width))
        self.sc_soil_edit_box.lineEdit_4.setText('{:.2f}'.format(self.thickness_sublayer))

        # calculate and display soil layers
        self.calculate_soil_clusters()

        # connect signals
        self.connect_signals_to_slots()

        # store updated parameter when dialog box is closed
        self.sc_soil_edit_box.pushButton.clicked.connect(sc_soil_box.close)

        sc_soil_box.exec_()


    def connect_signals_to_slots(self):
        """ Connects all signals to slots
        """
        self.sc_soil_edit_box.lineEdit_4.setStyleSheet("background-color: rgb(242, 255, 116);\n") # thickness of sub soillayer
        self.sc_soil_edit_box.lineEdit_4.editingFinished.connect(lambda : self.update_thickness_sublayer(float(self.sc_soil_edit_box.lineEdit_4.text())))
        self.sc_soil_edit_box.lineEdit.setStyleSheet("background-color: rgb(242, 255, 116);\n") # width
        self.sc_soil_edit_box.lineEdit.editingFinished.connect(lambda : self.update_width(float(self.sc_soil_edit_box.lineEdit.text())))


    def update_thickness_sublayer(self, thickness_sublayer):
        """ Updates sublayer thickness
        """
        try:
            # store thickness of the sublayer
            self.thickness_sublayer = thickness_sublayer
            self.calculate_soil_clusters()

        except ValueError:
            pass



    def update_width(self, width):
        """ Updates width of the 
        """
        try:
            # store thickness of the sublayer
            self.columns_right = self.columns_left + width

        except ValueError:
            pass


    def calculate_soil_clusters(self):
        """ Calculates and displays soil clusters on table
        """
        # clear old data
        self.sub_soillayers.clear()
        self.sc_soil_edit_box.tableWidget.blockSignals(True)
        self.sc_soil_edit_box.tableWidget.clearContents()
        self.sc_soil_edit_box.tableWidget.clear()

        column_labels = ['Soil layer', 'Sublayer ID', 'Top [m]', 'Bottom [m]', 'gammaSat [kN/m3]', "sigma_v' [kPa]", 've [-]', 'we [-]', 'E_s [kPa]', "uz_fdc [mm]", "uz_s [mm]", "uz_s unreinf. [mm]", "n_factor [-]"] 
        self.sc_soil_edit_box.tableWidget.setColumnCount(len(column_labels))
        self.sc_soil_edit_box.tableWidget.setRowCount(100)
        self.sc_soil_edit_box.tableWidget.setHorizontalHeaderLabels(column_labels)

        sigma_v = 0.0    # surcharge
        layer_i_start_row = 0
        id_number = 1
        for layer_i, layerpolygon in enumerate(self.Layer_polygons):
            soilmaterial_layer = layerpolygon['soilmaterial_layer']
            if layer_i==0:  # adjust top as top of columns
                layer_i_top = min(self.borehole['Top'][layer_i], self.top_FDC)
            else:
                layer_i_top = self.borehole['Top'][layer_i]
            layer_i_bottom = self.borehole['Bottom'][layer_i]
            layer_i_nspan = int(max(1, int((layer_i_top - layer_i_bottom)//self.thickness_sublayer)))   # at least 1 sublayer exists in 1 soil layer

            self.sc_soil_edit_box.tableWidget.setSpan(layer_i_start_row, 0, layer_i_nspan, 1)
            self.sc_soil_edit_box.tableWidget.setItem(layer_i_start_row, 0, QtWidgets.QTableWidgetItem(soilmaterial_layer)) # soilmaterial name
            self.sc_soil_edit_box.tableWidget.item(layer_i_start_row, 0).setBackground(QColor(*hex_to_rgb(layerpolygon['color']))) # set soil's color

            # get sub-soil layer parameters 
            sigma_v, layer_i_start_row, id_number = self.get_sub_soillayer_parameters(layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layerpolygon, soilmaterial_layer, sigma_v)

        # calculate improvement factors for each of the sub soillayers   
        self.get_n_factors() 

        # display data of the sub soil layers on table
        self.display_soil_clusters()


    def get_sub_soillayer_parameters(self, layer_i_top, layer_i_bottom, layer_i_nspan, layer_i_start_row, id_number, layerpolygon, soilmaterial_layer, sigma_v):
        """ Gets soil layer data and calculate improvement factors
        """
        sublayer_i_start = layer_i_top
        for i in range(layer_i_nspan):
            if sublayer_i_start <= self.columns_bottom: # start of sub layer is below columns bottom
                break
            elif sublayer_i_start >= self.columns_top: # start of the sub soillayers must be from the columns top level
                sublayer_i_start = self.columns_top
            #else:
            sub_soillayer = OrderedDict()
            sub_soillayer['id'] = self.FDC_name + str(id_number).zfill(3)
            sub_soillayer['color'] = layerpolygon['color']
            sub_soillayer['soilmaterial_layer'] = soilmaterial_layer
            sub_soillayer['top'] = sublayer_i_start
            if i == (layer_i_nspan - 1): # last sub soil layer
                thickness_sublayer_i = sub_soillayer['top'] - max(layer_i_bottom, self.columns_bottom)
            else:
                thickness_sublayer_i = self.thickness_sublayer
            # adjust bottom of the last soil layer (columns end)
            if (sub_soillayer['top'] - 2*self.thickness_sublayer) < self.columns_bottom:
                thickness_sublayer_i =  sub_soillayer['top'] - self.columns_bottom
            sub_soillayer['bottom'] = sublayer_i_start - thickness_sublayer_i

            # vertical effective stress for 'real' stress-dependent stiffness calculation
            sub_soillayer['gammaSat'] = read_data_in_json_item(soilmaterial_layer, 'gammaSat')
            sub_layer_i_level = sub_soillayer['top'] - 0.5*thickness_sublayer_i
            if sub_layer_i_level <= self.borehole['Head']: # under water (under bouyancy)
                sigma_v += (sub_soillayer['gammaSat'] - 10.0) * thickness_sublayer_i
            else:   # dried soil
                sigma_v += sub_soillayer['gammaSat'] * thickness_sublayer_i
            sub_soillayer["sigma_v'"] = sigma_v
            sub_soillayer['ve'] = read_data_in_json_item(soilmaterial_layer, 've')
            sub_soillayer['we'] = read_data_in_json_item(soilmaterial_layer, 'we')
            sub_soillayer['E_s'] = sub_soillayer['ve']*100*(sigma_v/100)**sub_soillayer['we']

            # settlements from reinforced and unreinforced soils
            z = self.matrice[:, 0]   # depth
            z_level = self.top_LTP - z
            idx_sub_soil_layer = np.where(z_level < sub_soillayer['top'])[0][0] # index of the first found item
            u_z_c = self.matrice[idx_sub_soil_layer, 26]*1.0e3      # column settlement
            u_z_s = self.matrice[idx_sub_soil_layer, 28]*1.0e3      # soil settlement
            u_z_s_unreinf = self.matrice[idx_sub_soil_layer, -1]    # unreinforced soil settlement
            sub_soillayer['uz_fdc'] = u_z_c
            sub_soillayer['uz_s'] = u_z_s
            sub_soillayer['uz_s unreinf'] = u_z_s_unreinf
            #sub_soillayer['n_factor'] = u_z_s_unreinf/u_z_s


            sublayer_i_start -= thickness_sublayer_i  # update top of the sublayer
            self.sub_soillayers.append(sub_soillayer)
            id_number += 1

        layer_i_start_row += layer_i_nspan

        return (sigma_v, layer_i_start_row, id_number)


    def get_n_factors(self):
        """ Gets improvement factor for each of the sub soillayers
        """
        for i, sub_soillayer in enumerate(self.sub_soillayers):
            if i+1 < len(self.sub_soillayers): # before the last sub soillayer
                u_z_diff_unreinf = sub_soillayer['uz_s unreinf'] - self.sub_soillayers[i+1]['uz_s unreinf']
                u_z_diff_reinf = sub_soillayer['uz_s'] - self.sub_soillayers[i+1]['uz_s']
            else:   # last sub soillayer
                u_z_diff_unreinf = sub_soillayer['uz_s unreinf'] 
                u_z_diff_reinf = sub_soillayer['uz_s']

            n_factor = u_z_diff_unreinf/u_z_diff_reinf
            sub_soillayer['n_factor'] = n_factor



    def display_soil_clusters(self):
        """ Displays soil clusters on table
        """
        self.sc_soil_edit_box.tableWidget.blockSignals(True)
        self.sc_soil_edit_box.tableWidget.setRowCount(len(self.sub_soillayers)) # fit number of rows to data size
        for sublayer_i, sub_soillayer in enumerate(self.sub_soillayers):
            self.sc_soil_edit_box.tableWidget.setItem(sublayer_i, 1, QtWidgets.QTableWidgetItem(sub_soillayer['id']))
            keys = list(sub_soillayer.keys())
            for j, key in enumerate(keys[3:]): # from sublayer_id onward
                self.sc_soil_edit_box.tableWidget.setItem(sublayer_i, j+2, QtWidgets.QTableWidgetItem('{:.2f}'.format(sub_soillayer[key])))

        self.sc_soil_edit_box.tableWidget.blockSignals(False)