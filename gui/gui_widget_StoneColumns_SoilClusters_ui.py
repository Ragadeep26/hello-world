# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_widget_StoneColumns_SoilClusters.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1457, 817)
        Dialog.setStyleSheet("QWidget{\n"
"background-color: rgb(0, 74, 127);\n"
"}\n"
"\n"
"QPushButton{\n"
"background-color: rgb(205, 205, 205);\n"
"}\n"
"\n"
"QLineEdit{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"\n"
"QLabel{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"QCheckBox{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"\n"
"QTableWidget{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"QComboBox{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"")
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        self.groupBox.setEnabled(True)
        self.groupBox.setToolTip("")
        self.groupBox.setStyleSheet("QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(5, 5, 0, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 7, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(80)
        self.gridLayout.addWidget(self.tableWidget, 6, 0, 1, 8)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 0, 4, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 2, 7, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout.addWidget(self.lineEdit_5, 3, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 3, 7, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(408, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout.addWidget(self.checkBox_3, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 2, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 4, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 2, 1, 4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter)
        self.groupBox_2.setStyleSheet("QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"")
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setContentsMargins(0, 5, 5, 5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_2.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.comboBox, 0, 0, 1, 1)
        self.comboBox_3 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_3.setObjectName("comboBox_3")
        self.gridLayout_2.addWidget(self.comboBox_3, 0, 2, 1, 1)
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setObjectName("widget")
        self.gridLayout_2.addWidget(self.widget, 1, 0, 1, 3)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 3)
        spacerItem3 = QtWidgets.QSpacerItem(1282, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem3, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setAutoDefault(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_3.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setAutoDefault(False)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_5.setToolTip(_translate("Dialog", "<html><head/><body><p>The calculations here follow Priebe [1]. Below are the summaries.</p><p>Depending on the sub soil layer thickness and depth of columns given, the number of sub soil layers will be adjusted accordingly. Soil parameters of the sub soil layers are copied from the original soil layers, only stiffness moduli are improved and soil strength parameters are adjusted after Priebe equations.</p><p>Soil stiffness E_s and columns stiffness E_c are calculated for each sub soil layers in the improved soil region following the relation E = v_e * 100 * (sigma_v\'/100)^w_e.</p><p>When friction angle of soil is modified by the columns, K0nc is updated by the relation K0nc = 1 - sin(phi_bar).</p><p>For HS-small soil, the ratio E_dyn/E_sta is recalculated from the current EurRef value by interpolationg from the (E_dyn/E_sta - E_sta) curve for soil. Then, G0ref is adapted following the relation G0ref = EurRef*(E_dyn/E_sta)*(1/2.4).</p><p>If user input constrained modulus is activated, soil stiffness E_s can be assigned by user for each layer. In this case, the columns stiffness E_c is not dependent on stress.</p><p>It is recommended to set the depth limit such that the stress increase by surcharge is less than 20% stress caused by overburden: (sigma_p\' -  sigma_v\') / (sigma_p\' + sigma_v\') &gt; 0.2, where sigma_p\' is the stress caused by surcharge and sigma_v\' is stress caused by soil overburden alone.</p><p>The stress caused by surchange sigma_p\' applied in a circular surface is distributed along depth following the relation </p><p>sigma_p\'(r, z) = p0 * [1 - (1/(1 + (r/z)^2)^(3/2)], where we take r to be radius of the circular surface load which results in stress distribution along depth z at the center of the circular surface.</p><p><br/></p><p>Reference:</p><p>[1] Priebe, H.J., 1995. The design of vibro replacement. <span style=\" font-style:italic;\">Ground engineering</span>, <span style=\" font-style:italic;\">28</span>(10), p.31.</p></body></html>"))
        self.label_5.setText(_translate("Dialog", "Information?"))
        self.label.setText(_translate("Dialog", "Surcharge [kN/m^2]"))
        self.label_2.setText(_translate("Dialog", "Top of columns [mNN]"))
        self.label_4.setText(_translate("Dialog", "Sublayer thickness [m]"))
        self.lineEdit.setText(_translate("Dialog", "10.0"))
        self.lineEdit_4.setText(_translate("Dialog", "2.0"))
        self.checkBox.setText(_translate("Dialog", "User input constrained modulus for soils?"))
        self.label_6.setText(_translate("Dialog", "Limit depth [m]"))
        self.checkBox_2.setText(_translate("Dialog", "Include surcharge in calculation of the improvement factor?"))
        self.checkBox_3.setText(_translate("Dialog", "Unlimited distribution?"))
        self.label_3.setText(_translate("Dialog", "Depth of columns [m]"))
        self.pushButton_2.setText(_translate("Dialog", "Print report"))
        self.pushButton.setText(_translate("Dialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

